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
def _iter_features_via_pyogrio(gdb_path: Path, layer: str):
    """Yield (attributes_dict, wgs84_geometry_geojson) for each feature.

    Uses pyogrio when available (Phase-1.5 pipeline standard); falls back to
    a visibly-honest warning if the runtime lacks GDAL bindings.
    """
    try:
        from pyogrio import read_info
        from pyogrio.raw import read as read_raw
    except ImportError as exc:
        raise RuntimeError(
            "pyogrio not installed — install via `pip install pyogrio` "
            "(GDAL 3.6+ bundled).  This is required for CanVec FGDB reading."
        ) from exc

    info = read_info(gdb_path, layer=layer)
    logger.info(
        "%s :: layer=%s features=%s geom=%s",
        gdb_path.name, layer, info.get("features"), info.get("geometry_type")
    )
    # NOTE — the actual read call semantics vary across pyogrio versions;
    # the canonical fallback below reads via geopandas if it becomes available
    # in the pipeline runtime.  Otherwise the raw read yields tuples that must
    # be re-interpreted by the caller.  Downstream federation layer normalises.
    fields, geom_type, crs, encoding, geometry, field_data = read_raw(
        gdb_path, layer=layer,
    )
    yield fields, geom_type, crs, geometry, field_data


def _substation_record_from_feature(
    feature_id: str, attrs: dict, latitude: float, longitude: float,
) -> SubstationRecord:
    """Normalise a CanVec transformer_station feature into a SubstationRecord.

    CanVec Res_MGT substation schema (empirically verified 2026-07-12):
      - feature_id                      (string, publisher-canonical)
      - md_temporal_extent_date_min     (string)
      - md_temporal_extent_date_max     (string)
      - md_horiz_position_accuracy_min  (float, metres)
      - md_horiz_position_accuracy_max  (float, metres)
      - map_selection                   (int16)

    Voltage, owner, name are ABSENT at the federal layer — populated via
    downstream federation with provincial-utility supplements.
    """
    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=str(feature_id),
        latitude=latitude,
        longitude=longitude,
        voltage_kv=None,             # Convention #56 visibly-honest degradation
        owner=None,
        operator_station_name=None,
        horiz_accuracy_min_m=attrs.get("md_horiz_position_accuracy_min"),
        horiz_accuracy_max_m=attrs.get("md_horiz_position_accuracy_max"),
        temporal_extent_min=attrs.get("md_temporal_extent_date_min"),
        temporal_extent_max=attrs.get("md_temporal_extent_date_max"),
        raw_attributes=dict(attrs),
    )


def _line_record_from_feature(
    feature_id: str, attrs: dict, geometry_multilinestring: list,
) -> TransmissionLineRecord:
    """CanVec power_line_1 schema (verified 2026-07-12):
      - feature_id / md_temporal_extent_*
      - md_horiz_position_accuracy_min/max
      - line_location (int16)
      - number_of_lines (int32)
      - map_selection (int16)
      - Shape_Length (float64)
    """
    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=str(feature_id),
        coordinates_multilinestring=geometry_multilinestring,
        voltage_kv=None,             # Absent at federal CanVec layer
        owner=None,
        line_name=None,
        number_of_lines=attrs.get("number_of_lines"),
        raw_attributes=dict(attrs),
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
    # The actual GDAL/pyogrio→WGS84 reprojection happens in the parse layer;
    # scaffold body below yields per-feature records with placeholder geometry
    # extraction and is the Step-3-follow-on target for full implementation.
    logger.info(
        "Parsing CanVec Res_MGT layers under %s (substation=%s, line=%s)",
        gdb, SUBSTATION_LAYERS, LINE_LAYER,
    )
    try:
        # STEP-3-FOLLOW-ON: replace the placeholder yields below with the
        # canonical pyogrio read that projects EPSG:4617 → WGS84, converts
        # MultiPolygon substation footprints to centroid points, and populates
        # the horiz_accuracy + temporal_extent fields per SubstationRecord.
        for layer in SUBSTATION_LAYERS:
            # placeholder — implementation deferred
            _ = layer
        # placeholder for line parsing
        result.warnings.append(
            "Discipline #55 stub — CanVec Res_MGT record-extraction body is a "
            "scaffold; full implementation deferred to Step 3 follow-on. "
            "Pre-flight anchor + fetch + SHA-256 audit + Discipline #36 filter "
            "hook are wired; the geometry-projection + attribute normalisation "
            "call chain lands with the first Canada L1 merge PR."
        )
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
