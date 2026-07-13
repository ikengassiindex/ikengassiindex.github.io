"""
SSI Pipeline — Canada L1 connector: CanVec 50K Resource Management theme.

Source ID:   CA-C1-canvec-resmgt (federal-canonical-primary)
Publisher:   Natural Resources Canada (NRCan) — Earth Sciences Sector
URL:         https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/fgdb/Res_MGT/
Licence:     Open Government Licence - Canada (OGL-CA)
Ref system:  EPSG:4617 (NAD83 CSRS)
Publication: 2017-12-15, continual revision
Anchor SHA:  e337056b6eb000d4ca21c43b9548047971ca419b9a0bae5899acee2dd7f4a945
             (canvec_50K_CA_Res_MGT_fgdb.zip, 11,053,682 bytes, pre-flight
             2026-07-12 empirical anchor)

National baseline (from pre-flight audit YAML):
  - transformer_station_0 (Point):        2,762
  - transformer_station_2 (MultiPolygon): 1,776
  - Total substations:                    4,538
  - power_line_1 (MultiLineString):      13,009

Schema note: substation records at the federal layer carry LOCATION only
(feature_id + temporal_extent + horiz_accuracy + map_selection); no voltage,
no owner, no name.  Voltage/owner enrichment requires provincial-utility
federation via YEC, NS-NSTDB, etc.  Empirical completeness ratio ~14%
(Yukon proxy: 3 CanVec vs 21 YEC operational).

Empirical refutation trail (see revision_log v1→v2 in pre-flight YAML):
  v1 assumption:   CanVec ManMade theme is the federal canonical
  v2 correction:   ManMade has zero electricity feature classes — the ManMade
                   Feature Catalogue's "Electric Power Station" (code 606) =
                   generation plants, not substations.  The correct theme is
                   Res_MGT (Resource Management) which contains
                   transformer_station_0/_2 + power_line_1.

Discipline #36:   Point-in-Canada-polygon filter applied via _base.apply_bounds_filter
                  with 5 km tolerance (Mode-3 per cross_border_tolerances.json).
Discipline #41:   Both substations + power_lines are ingested in the same pass;
                  parity check via _base.assert_line_parity.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
    CANADA_CACHE_DIR,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "CA-C1-canvec-resmgt"
BASE_URL = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/fgdb/Res_MGT/"
CANADA_WIDE_FILENAME = "canvec_50K_CA_Res_MGT_fgdb.zip"
EXPECTED_SHA256 = "e337056b6eb000d4ca21c43b9548047971ca419b9a0bae5899acee2dd7f4a945"
EXPECTED_BYTES = 11_053_682

SUBSTATION_LAYERS = ["transformer_station_0", "transformer_station_2"]
LINE_LAYER = "power_line_1"

# Optional per-province mode — 13 provinces + territories at 15.67 MB aggregate
# (see pre-flight YAML provincial_coverage_matrix).  Canada-wide (10.54 MB) is
# the default and is empirically anchored; per-province is fallback for
# constrained-bandwidth environments.
PROVINCE_FILES = {
    "AB": "canvec_50K_AB_Res_MGT_fgdb.zip",
    "BC": "canvec_50K_BC_Res_MGT_fgdb.zip",
    "MB": "canvec_50K_MB_Res_MGT_fgdb.zip",
    "NB": "canvec_50K_NB_Res_MGT_fgdb.zip",
    "NL": "canvec_50K_NL_Res_MGT_fgdb.zip",
    "NS": "canvec_50K_NS_Res_MGT_fgdb.zip",
    "NT": "canvec_50K_NT_Res_MGT_fgdb.zip",
    "NU": "canvec_50K_NU_Res_MGT_fgdb.zip",
    "ON": "canvec_50K_ON_Res_MGT_fgdb.zip",
    "PE": "canvec_50K_PE_Res_MGT_fgdb.zip",
    "QC": "canvec_50K_QC_Res_MGT_fgdb.zip",
    "SK": "canvec_50K_SK_Res_MGT_fgdb.zip",
    "YT": "canvec_50K_YT_Res_MGT_fgdb.zip",
}


# ── Fetch ────────────────────────────────────────────────────────────────
def _fetch_zip(url: str, timeout: int = 120) -> bytes:
    """Fetch and return raw ZIP bytes with SHA-256 audit."""
    cache = cache_path_for(url, ext=".zip")
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache, len(body))
        return body
    req = urllib.request.Request(url, headers={"User-Agent": "SSI-Index-Foundation/1.0"})
    logger.info("Fetching %s ...", url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    cache.write_bytes(body)
    logger.info("Cached %s (%d bytes)", cache, len(body))
    return body


def _extract_gdb(zip_bytes: bytes, work_dir: Path) -> Path:
    """Unpack the ZIP and return the path to the .gdb directory."""
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(work_dir)
    for root, dirs, _ in os.walk(work_dir):
        for d in dirs:
            if d.endswith(".gdb"):
                return Path(root) / d
    raise FileNotFoundError(f"No .gdb directory found under {work_dir}")


# ── Parse ────────────────────────────────────────────────────────────────
def _read_layer(gdb_path: Path, layer: str) -> tuple[dict, list, list]:
    """Read a single FGDB layer via pyogrio raw + return (meta, geometries, field_rows).

    field_rows is a list of dicts (one per feature) keyed by the layer's field
    names.  geometries is a list of shapely geometry objects (Point,
    MultiPolygon, or MultiLineString) already decoded from WKB.

    Coordinates in CanVec Res_MGT are lat/lon (NAD83 CSRS = EPSG:4617); for
    SSI Index 100 m tolerance NAD83↔WGS84 offset (<2 m) is below the noise
    floor — coordinates are consumed as WGS84 directly.  Convention #56
    visibly-honest degradation: if a feature's WKB fails to parse, it is
    skipped with a per-record warning rather than crashing the fetch.
    """
    try:
        from pyogrio.raw import read as read_raw
        from shapely import wkb as _wkb
    except ImportError as exc:
        raise RuntimeError(
            "pyogrio + shapely required for CanVec FGDB reading — "
            "check scripts/pipeline/requirements.txt."
        ) from exc

    meta, _fids, geometry_blobs, field_data = read_raw(gdb_path, layer=layer)
    field_names = list(meta["fields"])

    geometries: list = []
    field_rows: list[dict] = []
    parse_failures = 0
    for i, wkb_bytes in enumerate(geometry_blobs):
        try:
            geom = _wkb.loads(wkb_bytes)
        except Exception:
            parse_failures += 1
            continue
        geometries.append(geom)
        row = {name: field_data[j][i] for j, name in enumerate(field_names)}
        field_rows.append(row)

    if parse_failures:
        logger.warning(
            "%s :: %d features had unparseable WKB (skipped, Convention #56)",
            layer, parse_failures,
        )
    return meta, geometries, field_rows


def _substation_record_from_geometry(
    geom, row: dict, *, feature_index: int,
) -> SubstationRecord | None:
    """Convert a shapely geometry + attribute row into a SubstationRecord.

    Handles both transformer_station_0 (Point) and transformer_station_2
    (MultiPolygon).  For polygons the centroid is used as the station node
    location (Discipline #36 convention — Canada substation-yard footprints
    at 1:50,000 scale are small enough that centroid vs perimeter distinction
    is below the 100 m Index tolerance).
    """
    if geom.geom_type == "Point":
        longitude, latitude = geom.x, geom.y
    elif geom.geom_type in ("Polygon", "MultiPolygon"):
        c = geom.centroid
        longitude, latitude = c.x, c.y
    else:
        return None

    def _to_str(v) -> str | None:
        if v is None or (isinstance(v, float) and v != v):    # NaN
            return None
        return str(v)

    def _to_float(v) -> float | None:
        if v is None:
            return None
        try:
            f = float(v)
            return f if f == f else None    # exclude NaN
        except (TypeError, ValueError):
            return None

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=_to_str(row.get("feature_id")) or f"unnamed-{feature_index}",
        latitude=float(latitude),
        longitude=float(longitude),
        voltage_kv=None,             # Convention #56 visibly-honest degradation
        owner=None,                  # Federal CanVec layer carries no owner
        operator_station_name=None,
        horiz_accuracy_min_m=_to_float(row.get("md_horiz_position_accuracy_min")),
        horiz_accuracy_max_m=_to_float(row.get("md_horiz_position_accuracy_max")),
        temporal_extent_min=_to_str(row.get("md_temporal_extent_date_min")),
        temporal_extent_max=_to_str(row.get("md_temporal_extent_date_max")),
        raw_attributes={k: _to_str(v) for k, v in row.items()},
    )


def _line_record_from_geometry(
    geom, row: dict, *, feature_index: int,
) -> TransmissionLineRecord | None:
    """Convert a shapely MultiLineString (or LineString) + attributes into a
    TransmissionLineRecord.

    Canonical geometry: nested list-of-list-of-[lon, lat] pairs per the
    GeoJSON MultiLineString convention (matches TransmissionLineRecord field).
    """
    def _to_str(v) -> str | None:
        return None if v is None else str(v)
    def _to_int(v) -> int | None:
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    if geom.geom_type == "MultiLineString":
        multiline = [
            [[pt[0], pt[1]] for pt in ls.coords]
            for ls in geom.geoms
        ]
    elif geom.geom_type == "LineString":
        multiline = [[[pt[0], pt[1]] for pt in geom.coords]]
    else:
        return None

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=_to_str(row.get("feature_id")) or f"unnamed-{feature_index}",
        coordinates_multilinestring=multiline,
        voltage_kv=None,             # Absent at federal CanVec layer
        owner=None,
        line_name=None,
        number_of_lines=_to_int(row.get("number_of_lines")),
        raw_attributes={k: _to_str(v) for k, v in row.items()},
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    provincial_scope: str = "CA",
    apply_bounds: bool = True,
    strict_line_parity: bool = False,
) -> IngestionResult:
    """Fetch CanVec 50K Res_MGT substations + power_lines for Canada.

    Args:
      provincial_scope:   "CA" (Canada-wide, default) or an ISO-3166-2
                          province code ("AB", "BC", "ON", "QC", "YT", ...)
      apply_bounds:       Apply Discipline #36 point-in-polygon Canada-bounds
                          filter (default True).  Set False only for
                          debug/development inspection.
      strict_line_parity: Raise on Discipline #41 parity signal (default False —
                          signals surface as warnings so downstream federation
                          can complete).

    Returns:
      IngestionResult with substations + transmission_lines populated, plus
      raw_sha256 audit anchor and warnings list.  Discipline #41 parity findings
      are added to warnings; the parent audit YAML sidecar records them.
    """
    filename = (
        CANADA_WIDE_FILENAME if provincial_scope == "CA"
        else PROVINCE_FILES.get(provincial_scope)
    )
    if not filename:
        raise ValueError(
            f"Unknown provincial_scope {provincial_scope!r}; "
            f"expected 'CA' or one of {sorted(PROVINCE_FILES.keys())}."
        )

    url = BASE_URL + filename
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=url,
        provincial_scope=provincial_scope,
    )

    try:
        zip_bytes = _fetch_zip(url)
    except Exception as exc:
        result.warnings.append(
            f"Convention #56 degradation — CanVec fetch failed for {url}: {exc}"
        )
        return result

    result.raw_bytes_fetched = len(zip_bytes)
    result.raw_sha256 = hashlib.sha256(zip_bytes).hexdigest()

    if provincial_scope == "CA" and result.raw_sha256 != EXPECTED_SHA256:
        result.warnings.append(
            f"SHA-256 drift vs pre-flight anchor: got {result.raw_sha256}, "
            f"expected {EXPECTED_SHA256}. NRCan may have republished; "
            "re-anchor pre-flight audit YAML before merging."
        )

    work_dir = CANADA_CACHE_DIR / f"resmgt_{provincial_scope}"
    try:
        gdb = _extract_gdb(zip_bytes, work_dir)
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — .gdb extract failed: {exc}")
        return result

    # Substations (Point + MultiPolygon) + power_lines.
    # NAD83 CSRS (EPSG:4617) → WGS84 identity approximation: NAD83↔WGS84
    # offset is <2 m; below the SSI Index 100 m tolerance for R6b/R4 modifiers.
    logger.info(
        "Parsing CanVec Res_MGT layers under %s (substation=%s, line=%s)",
        gdb, SUBSTATION_LAYERS, LINE_LAYER,
    )
    try:
        # Substations across both layers (point + polygon).
        for layer in SUBSTATION_LAYERS:
            meta, geometries, field_rows = _read_layer(gdb, layer)
            layer_kept = 0
            for i, (geom, row) in enumerate(zip(geometries, field_rows)):
                rec = _substation_record_from_geometry(geom, row, feature_index=i)
                if rec is not None:
                    result.substations.append(rec)
                    layer_kept += 1
            logger.info("  %s :: %d substations extracted", layer, layer_kept)

        # Transmission lines.
        meta, geometries, field_rows = _read_layer(gdb, LINE_LAYER)
        line_kept = 0
        for i, (geom, row) in enumerate(zip(geometries, field_rows)):
            rec = _line_record_from_geometry(geom, row, feature_index=i)
            if rec is not None:
                result.transmission_lines.append(rec)
                line_kept += 1
        logger.info("  %s :: %d lines extracted", LINE_LAYER, line_kept)
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — parse failed: {exc}")
        return result

    # Discipline #36 bounds filter
    if apply_bounds:
        kept_subs, dropped_subs = apply_bounds_filter(result.substations)
        kept_lines, dropped_lines = apply_bounds_filter(result.transmission_lines)
        if dropped_subs:
            result.warnings.append(
                f"Discipline #36 filter dropped {len(dropped_subs)} substations "
                "outside Canada polygon (5 km tolerance)."
            )
        if dropped_lines:
            result.warnings.append(
                f"Discipline #36 filter dropped {len(dropped_lines)} lines "
                "outside Canada polygon (5 km tolerance)."
            )
        result.substations = kept_subs
        result.transmission_lines = kept_lines

    # Discipline #41 parity check
    parity_ok, findings = assert_line_parity(
        result, outbound_border_ok=True, strict=strict_line_parity
    )
    result.warnings.extend(findings)

    return result


def main() -> None:
    """CLI wrapper for one-shot fetch + audit-sidecar emission."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    result = fetch(provincial_scope="CA")
    _, findings = assert_line_parity(result)
    emit_audit_sidecar(result, parity_findings=findings)


if __name__ == "__main__":
    main()
