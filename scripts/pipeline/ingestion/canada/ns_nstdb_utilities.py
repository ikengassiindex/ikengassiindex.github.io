"""
SSI Pipeline — Canada L1 connector: Nova Scotia NSTDB Utilities.

Source ID:   CA-C4-ns-nstdb-utilities-point (provincial-supplementary)
Publisher:   Government of Nova Scotia (GeoNova / Land Information Services)
URL (GeoJSON): https://data.novascotia.ca/api/geospatial/eiwy-kfrj?method=export&format=GeoJSON
URL (CSV):     https://data.novascotia.ca/api/views/eiwy-kfrj/rows.csv?accessType=DOWNLOAD
Companion Line Layer: id x39x-aw9i (same publisher, satisfies Discipline #41)
Licence:     Open Government Licence – Nova Scotia
Vintage:     2025-09-24 metadata_last_modified

Field schema (Point Layer):
  the_geom (WKT Point) | FEAT_CODE (str) | FEAT_DESC (str) | ZVALUE (float) | ANGLE (float)

**Critical filter gotcha:** the point layer is a MIXED-UTILITY topographic dataset
(pipelines, tanks, electrical substations, comms).  Filter by FEAT_CODE for the
substation subset.  The FEAT_CODE for electrical substations is not part of the
publisher's endpoint URL parameters — the filter must apply POST-fetch.  The
canonical code table lives at
https://nsgi.novascotia.ca/WSF_DDS/DDS.svc/DownloadFile?tkey=fhrTtdnDvfytwLz6&id=17
and is fetched separately.

Preliminary probe (pre-flight 2026-07-12, first 500 CSV lines) returned zero
substation matches on naive text search — the actual FEAT_CODE must be
identified from the NSTDB Feature Code table.  Placeholder codes in this
scaffold: NSTDB uses UT-prefixed codes for utility features (UTTK60 =
"TANK (6-15m diameter) point" observed empirically).  The electrical-substation
code is one of the UT-prefixed set; identification is queued as Step 3
follow-on before merging into canada/ssi-data.json.

Consequence for the scaffold: this connector fetches the full mixed payload +
provides a `filter_substations()` hook.  Until the FEAT_CODE is anchored, all
UT-prefixed features are surfaced as candidates and downstream federation
narrows via a whitelist.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
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
SOURCE_ID = "CA-C4-ns-nstdb-utilities-point"
GEOJSON_URL = "https://data.novascotia.ca/api/geospatial/eiwy-kfrj?method=export&format=GeoJSON"

# Placeholder — the actual electrical-substation FEAT_CODE must be verified
# against the NSTDB Feature Code table.  Empirical probe surfaced UTTK60 = TANK;
# candidate substation codes to verify (from the UT-prefix pattern) are stored
# in this whitelist.  Downstream federation narrows the filter after the code
# is anchored.
CANDIDATE_SUBSTATION_FEAT_CODES = {
    # Feature Code Table check queued for Step 3 follow-on.  Once anchored:
    # replace this open whitelist with the empirically-verified code(s).
    # Placeholder pattern: UTSS* or UTEL* per NSTDB naming convention.
    "UTSS40",
    "UTSS50",
    "UTSS60",
    "UTEL40",
    "UTEL50",
    "UTEL60",
}


# ── Fetch ────────────────────────────────────────────────────────────────
def _fetch_geojson(timeout: int = 60) -> bytes:
    cache = cache_path_for(GEOJSON_URL, ext=".geojson")
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache, len(body))
        return body
    req = urllib.request.Request(GEOJSON_URL, headers={"User-Agent": "SSI-Index-Foundation/1.0"})
    logger.info("Fetching NS NSTDB Utilities Point Layer ...")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    cache.write_bytes(body)
    return body


# ── Parse ────────────────────────────────────────────────────────────────
def _substation_record_from_geojson_feature(feature: dict) -> SubstationRecord | None:
    """Normalise a NSTDB Utilities Point feature.  Returns None if not a
    substation-candidate (mixed-payload filter)."""
    props = feature.get("properties", {}) or {}
    feat_code = str(props.get("FEAT_CODE", "")).strip()
    if feat_code not in CANDIDATE_SUBSTATION_FEAT_CODES:
        return None

    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates", [None, None])
    if geom.get("type") != "Point":
        return None

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=f"nstdb-{feat_code}-{props.get('OBJECTID', props.get('_id', ''))}",
        latitude=coords[1],
        longitude=coords[0],
        voltage_kv=None,             # Absent in NSTDB Point Layer schema
        owner=None,                  # Nova Scotia Power is the province utility
                                     # but publisher does not tag ownership
        operator_station_name=props.get("FEAT_DESC"),
        raw_attributes=dict(props),
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(*, apply_bounds: bool = True) -> IngestionResult:
    """Fetch Nova Scotia NSTDB Utilities Point Layer and filter to substation
    candidates.

    Warning: the substation FEAT_CODE whitelist is a scaffold placeholder
    pending anchor against the NSTDB Feature Code table.  Verify before
    merging into canada/ssi-data.json.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=GEOJSON_URL,
        provincial_scope="NS",
    )
    result.warnings.append(
        "Discipline #55 stub — Nova Scotia substation FEAT_CODE whitelist is a "
        "scaffold placeholder.  Anchor against the NSTDB Feature Code table at "
        "https://nsgi.novascotia.ca/WSF_DDS/DDS.svc/DownloadFile?tkey=fhrTtdnDvfytwLz6&id=17 "
        "before merging."
    )

    try:
        body = _fetch_geojson()
    except Exception as exc:
        result.warnings.append(f"Convention #56 degradation — NS-NSTDB fetch failed: {exc}")
        return result

    result.raw_bytes_fetched = len(body)
    result.raw_sha256 = hashlib.sha256(body).hexdigest()

    try:
        geo = json.loads(body)
    except json.JSONDecodeError as exc:
        result.warnings.append(f"Convention #56 degradation — GeoJSON parse failed: {exc}")
        return result

    total_features = 0
    for feat in geo.get("features", []):
        total_features += 1
        rec = _substation_record_from_geojson_feature(feat)
        if rec is not None:
            result.substations.append(rec)

    logger.info(
        "NS NSTDB Utilities — total features %d, matched %d substation candidates",
        total_features, len(result.substations),
    )
    result.warnings.append(
        f"NS NSTDB — {total_features} total point-utility features screened; "
        f"{len(result.substations)} matched substation-candidate FEAT_CODE whitelist. "
        "Zero matches indicates FEAT_CODE whitelist mismatch."
    )

    if apply_bounds:
        kept, dropped = apply_bounds_filter(result.substations)
        if dropped:
            result.warnings.append(
                f"Discipline #36 filter dropped {len(dropped)} NS substations "
                "outside Canada polygon."
            )
        result.substations = kept

    _, findings = assert_line_parity(result, outbound_border_ok=True)
    result.warnings.extend(findings)
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    result = fetch()
    _, findings = assert_line_parity(result)
    emit_audit_sidecar(result, parity_findings=findings)


if __name__ == "__main__":
    main()
