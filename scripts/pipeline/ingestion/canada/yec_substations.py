"""
SSI Pipeline — Canada L1 connector: Yukon Energy Corporation.

Source ID:   CA-C3-yec-substations (provincial-territorial-supplementary)
Publisher:   Yukon Energy Corporation (utility) via Government of Yukon GeoYukon
URL:         https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/
             GY_UtilitiesCommunications/MapServer/8
Licence:     Open Government Licence - Yukon
Vintage:     2026-07-08 metadata_last_modified (4 days before pre-flight)

Role: Territorial operational-utility supplementary — 21 substations at pre-flight
with FULL voltage schema (INCOMING_CAPACITY_V + OUTGOING_CAPACITY_V) plus
transmission/switching/converter indicators + lines-in/out counts.  Populates
the voltage_kv + owner + operator_station_name fields that CanVec Res_MGT lacks.

Companion source YEC Power Lines (Layer TBD) is queued for Discipline #41
line-coupling at the territorial layer.  Both YEC substation + line datasets
are published on the same GeoYukon MapServer.

Sample audit anchor: SHA-256 a152d3478d7bbcfd12ee3b14e1d2b6cc0c256984bbebbbaeb0d4c73a29e472f3
over the 2-feature GeoJSON response (893 bytes) at pre-flight.

Field schema (Layer 8 substations):
  OBJECTID, NAME, COMMUNITY,
  INCOMING_CAPACITY_V (int), OUTGOING_CAPACITY_V (int),
  STEP_DOWN_IND, STEP_UP_IND, TRANSMISSION_IND, SWITCHING_IND, CONVERTER_IND (Y/N),
  LINES_IN_NUM (int16), LINES_OUT_NUM (int16)
"""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.request
from pathlib import Path

from ._base import (
    SubstationRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "CA-C3-yec-substations"
MAPSERVER_LAYER_8 = (
    "https://mapservices.gov.yk.ca/arcgis/rest/services/GeoYukon/"
    "GY_UtilitiesCommunications/MapServer/8"
)


# ── Fetch ────────────────────────────────────────────────────────────────
def _query_arcgis_geojson(timeout: int = 30) -> bytes:
    url = f"{MAPSERVER_LAYER_8}/query?where=1%3D1&outFields=*&f=geojson"
    cache = cache_path_for(url, ext=".geojson")
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache, len(body))
        return body
    req = urllib.request.Request(url, headers={"User-Agent": "SSI-Index-Foundation/1.0"})
    logger.info("Fetching YEC substations ...")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    cache.write_bytes(body)
    return body


# ── Parse ────────────────────────────────────────────────────────────────
def _yn_to_bool(v) -> bool | None:
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("y", "yes", "true", "1"):
        return True
    if s in ("n", "no", "false", "0"):
        return False
    return None


def _substation_record_from_geojson_feature(feature: dict) -> SubstationRecord:
    """Normalise a YEC GeoJSON feature into SubstationRecord.

    The v_incoming/v_outgoing fields are integers in Volts; convert to kV for
    the normalised schema.
    """
    props = feature.get("properties", {}) or {}
    geom = feature.get("geometry") or {}
    if geom.get("type") != "Point":
        raise ValueError(f"YEC substation with unexpected geometry: {geom.get('type')!r}")
    lon, lat = geom.get("coordinates", [None, None])

    v_in = props.get("INCOMING_CAPACITY_V")
    v_out = props.get("OUTGOING_CAPACITY_V")
    voltage_in_kv = float(v_in) / 1000.0 if v_in not in (None, 0) else None
    voltage_out_kv = float(v_out) / 1000.0 if v_out not in (None, 0) else None

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=str(props.get("OBJECTID", "")),
        latitude=lat,
        longitude=lon,
        voltage_kv=voltage_in_kv,
        voltage_out_kv=voltage_out_kv,
        owner="Yukon Energy Corporation",
        operator_station_name=props.get("NAME"),
        community=props.get("COMMUNITY"),
        is_transmission_station=_yn_to_bool(props.get("TRANSMISSION_IND")),
        is_switching_station=_yn_to_bool(props.get("SWITCHING_IND")),
        is_converter_station=_yn_to_bool(props.get("CONVERTER_IND")),
        lines_in_count=props.get("LINES_IN_NUM"),
        lines_out_count=props.get("LINES_OUT_NUM"),
        raw_attributes=dict(props),
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(*, apply_bounds: bool = True) -> IngestionResult:
    """Fetch YEC substations (Yukon Territory)."""
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=f"{MAPSERVER_LAYER_8}/query?where=1%3D1&outFields=*&f=geojson",
        provincial_scope="YT",
    )

    try:
        body = _query_arcgis_geojson()
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — YEC fetch failed: {exc}")
        return result

    result.raw_bytes_fetched = len(body)
    result.raw_sha256 = hashlib.sha256(body).hexdigest()

    try:
        geo = json.loads(body)
    except json.JSONDecodeError as exc:
        result.warnings.append(f"Convention #56 degradation — GeoJSON parse failed: {exc}")
        return result

    for feat in geo.get("features", []):
        try:
            result.substations.append(_substation_record_from_geojson_feature(feat))
        except Exception as exc:
            result.warnings.append(f"Convention #56 — skipped feature: {exc}")

    if apply_bounds:
        kept, dropped = apply_bounds_filter(result.substations)
        if dropped:
            result.warnings.append(
                f"Discipline #36 filter dropped {len(dropped)} YEC substations — "
                "unexpected for a territorial-utility source; verify Canada bounds "
                "polygon covers Yukon Territory (should — Arctic extension per "
                "commit 86d7c9df)."
            )
        result.substations = kept

    _, findings = assert_line_parity(
        result, outbound_border_ok=True   # YEC substations without in-source lines are OK
    )
    result.warnings.extend(findings)
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    result = fetch()
    _, findings = assert_line_parity(result)
    emit_audit_sidecar(result, parity_findings=findings)


if __name__ == "__main__":
    main()
