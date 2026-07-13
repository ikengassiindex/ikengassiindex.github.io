"""
SSI Pipeline — Canada L1 connector: NACEI Electric Transmission Line.

Source ID:   CA-C2-nacei-arcgis (federal-strategic-cross-check)
Publisher:   NRCan + US DOE + Mexico SENER (NACEI trilateral, treaty-level)
URL:         https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/
             energy_infrastructure_of_north_america_en/MapServer/1
Licence:     Open Government Licence - Canada (as NRCan-published)
Vintage:     2017 (last publisher notice August 2017)

Role: Strategic-scale continent-view backbone (500 kV+ interconnections)
cross-check against CanVec Res_MGT extraction.  Canada-filtered feature count
is small (28 line features at pre-flight 2026-07-12) — not comprehensive, but
provides voltage_kV + owner + line name attributes which CanVec Res_MGT lacks.

**Critical schema gotcha (empirically anchored 2026-07-12):**
The `Country` field values are full names, NOT ISO codes.  Filter must be
`Country = 'Canada'`.  Filter `Country = 'CA'` returns count = 0 silently.
This is the exact class of failure the pre-flight audit is designed to catch.

Sample audit anchor: SHA-256 340ac343ea2cacb43d4b0eb85083f5516c1f9ad1a0c72a1932af97f09b1e3682
over the 2-feature Canada-filtered GeoJSON response (1191 bytes) at pre-flight.

Field schema (Layer 1):
  OBJECTID, Country, LineName, Owner, Latitude, Longitude,
  City, County, StateProv, ZipCode, Address,
  FrmState, FrmCountry, ToState, ToCountry,
  NumLines, Voltage_kV, Source, Period
"""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.parse
import urllib.request
from pathlib import Path

from ._base import (
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "CA-C2-nacei-arcgis"
MAPSERVER_LAYER_1 = (
    "https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/"
    "energy_infrastructure_of_north_america_en/MapServer/1"
)

# CRITICAL — this is the empirically-verified filter (see pre-flight audit YAML
# §critical_schema_gotcha).  Any deviation returns 0 features silently.
CANADA_FILTER = "Country = 'Canada'"
CANADA_FILTER_URL_ENCODED = urllib.parse.quote(CANADA_FILTER)


# ── Fetch ────────────────────────────────────────────────────────────────
def _query_arcgis_geojson(where: str, out_fields: str = "*", timeout: int = 30) -> bytes:
    """Query the ArcGIS REST service and return the raw GeoJSON bytes."""
    url = (
        f"{MAPSERVER_LAYER_1}/query"
        f"?where={urllib.parse.quote(where)}"
        f"&outFields={out_fields}"
        f"&f=geojson"
    )
    cache = cache_path_for(url, ext=".geojson")
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache, len(body))
        return body
    req = urllib.request.Request(url, headers={"User-Agent": "SSI-Index-Foundation/1.0"})
    logger.info("Fetching NACEI Layer 1 with WHERE=%r ...", where)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    cache.write_bytes(body)
    return body


def _query_arcgis_count(where: str, timeout: int = 15) -> int:
    """Query the ArcGIS REST service for the feature count only."""
    url = (
        f"{MAPSERVER_LAYER_1}/query"
        f"?where={urllib.parse.quote(where)}"
        f"&returnCountOnly=true&f=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "SSI-Index-Foundation/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        j = json.loads(r.read())
    return int(j.get("count", 0))


# ── Parse ────────────────────────────────────────────────────────────────
def _line_record_from_geojson_feature(feature: dict) -> TransmissionLineRecord:
    """Normalise a NACEI Layer 1 GeoJSON feature into TransmissionLineRecord.

    NACEI Layer 1 geometry is Point (line-representative point at the mid- or
    end-station coordinate rather than a full line geometry, per the NACEI
    Layer-1 publication convention).  We wrap the single point as a
    one-vertex MultiLineString to fit the SubstationRecord/TransmissionLineRecord
    duality; downstream federation reconciles with CanVec Res_MGT power_line_1
    which carries true MultiLineString geometry.
    """
    props = feature.get("properties", {}) or {}
    geom = feature.get("geometry") or {}
    geom_type = geom.get("type")
    if geom_type == "Point":
        coords = geom.get("coordinates", [None, None])
        multi_line = [[coords, coords]]        # degenerate 1-vertex "line"
    elif geom_type == "MultiLineString":
        multi_line = geom.get("coordinates", [])
    elif geom_type == "LineString":
        multi_line = [geom.get("coordinates", [])]
    else:
        multi_line = []

    voltage_kv = props.get("Voltage_kV")
    if isinstance(voltage_kv, str):
        try:
            voltage_kv = float(voltage_kv)
        except ValueError:
            voltage_kv = None

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=str(props.get("OBJECTID", "")),
        coordinates_multilinestring=multi_line,
        voltage_kv=voltage_kv,
        owner=props.get("Owner"),
        line_name=props.get("LineName"),
        from_station_id=props.get("FrmState"),
        to_station_id=props.get("ToState"),
        number_of_lines=props.get("NumLines"),
        raw_attributes=dict(props),
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    where: str = CANADA_FILTER,
    apply_bounds: bool = True,
) -> IngestionResult:
    """Fetch NACEI Layer 1 electric transmission lines for Canada.

    Args:
      where:        SQL-where filter.  Default is the empirically-verified
                    Canada-full-name filter — DO NOT change to `Country = 'CA'`
                    (silently returns 0 features per the pre-flight anchor).
      apply_bounds: Apply Discipline #36 point-in-polygon filter to the derived
                    midpoint of each line feature (default True).

    Returns:
      IngestionResult (transmission_lines populated; substations empty by design
      — NACEI has no substation layer).  Warnings include Discipline #41 lines-only
      parity signal — expected for this source.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=f"{MAPSERVER_LAYER_1}/query?where={urllib.parse.quote(where)}&f=geojson",
        provincial_scope="CA",
    )

    # Pre-flight sanity — the schema gotcha catcher
    try:
        n = _query_arcgis_count(where)
        if n == 0:
            result.warnings.append(
                f"NACEI Layer 1 returned 0 features for WHERE={where!r}. "
                "This is the pre-flight schema-gotcha signature — verify the "
                "filter uses Country full-name (e.g. 'Canada'), NOT the ISO code "
                "'CA'.  See pre-flight audit YAML §critical_schema_gotcha."
            )
            return result
        logger.info("NACEI Layer 1 :: WHERE=%r yields %d features", where, n)
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — NACEI count probe failed: {exc}")
        return result

    try:
        body = _query_arcgis_geojson(where)
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — NACEI GeoJSON fetch failed: {exc}")
        return result

    result.raw_bytes_fetched = len(body)
    result.raw_sha256 = hashlib.sha256(body).hexdigest()

    try:
        geo = json.loads(body)
    except json.JSONDecodeError as exc:
        result.warnings.append(f"Convention #56 degradation — GeoJSON parse failed: {exc}")
        return result

    for feat in geo.get("features", []):
        result.transmission_lines.append(_line_record_from_geojson_feature(feat))

    if apply_bounds:
        kept, dropped = apply_bounds_filter(result.transmission_lines)
        if dropped:
            result.warnings.append(
                f"Discipline #36 filter dropped {len(dropped)} NACEI lines "
                "outside Canada polygon (5 km tolerance).  Some NACEI lines "
                "are trans-border ties — verify these before merging."
            )
        result.transmission_lines = kept

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=True)
    result.warnings.extend(findings)
    return result


def main() -> None:
    """CLI wrapper."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    result = fetch()
    _, findings = assert_line_parity(result)
    emit_audit_sidecar(result, parity_findings=findings)


if __name__ == "__main__":
    main()
