"""Turkey P30 merge into ssi-data.json + grid-geo.json.

⚠⚠⚠ SCHEMA BUG — DO NOT RE-RUN WITHOUT FIX ⚠⚠⚠
======================================================================
This merge script (Wave 3 P30 Turkey initial version) contains a schema
emission bug for grid-geo.json:

- CORRECT canonical schema (used by all 38 other countries):
    {"s": {osm_id: {x, y, n, v}},
     "l": [{i, p: [[lon,lat],...], kv, ss, se}, ...],
     "a": {sub_id: [connected_sub_ids]}}

- WRONG schema this merger EMITTED (Wave 3 P30 first-run bug):
    Standard GeoJSON FeatureCollection with type + features array,
    features had EMPTY coordinates (no geometry data at all)

Hotfix applied 2026-07-18 (Commit 33): stripped the corrupted GeoJSON
layer from turkey/grid-geo.json, restored canonical compact schema.
Baseline lines (8,061) + subs (4,092) + adjacency (4,083) intact.

Wave 4+ merge scripts (starting with UK P31) must emit compact
{s, l, o} schema from the start, with proper OSM way node coord
resolution (out geom or 2-pass) + substation ID assignment + adjacency
graph construction. Do NOT reuse this Turkey merger as a template
without the schema fix.

To properly re-enhance Turkey in a future workstream, either:
(a) Move Turkey to Wave 4 with a corrected merger emitting compact
    schema, OR
(b) Rewrite this merger in place to emit compact schema, then re-run
    against cached OSM data (turkey/_osm_cache/*.json still valid).
======================================================================

🎉 COHORT COMPLETION MILESTONE 🎉  (SUBSTATION side complete;
line-side enhancement DEFERRED pending merger fix)
Wave 3 Priority 30 = LAST v4.23 refresh candidate.
Post-Turkey closure: 30/39 v4.23 enhancement pass complete.
Wave 4 (9 countries: UK + Sweden + Spain + Italy + Japan + Portugal
+ France + Germany + US) still needed for true 39/39 cohort-wide
consistency.

Merges OSM Overpass fetch (substations + lines) into Turkey's baseline
ssi-data.json + grid-geo.json canonicals with:
- 500m spatial matching for enrichment
- Voltage cross-validation reporting
- Step 4b retroactive attribution via 8-layer resolver
- Convention #78 §4bis.5 Istanbul 3-way 8TH enforcement application
- Discipline #36 cross-border filter (5.0 km tolerance)
- Convention #56 compact-JSON write (visibly-honest efficient encoding)

Convention preservation:
- #7 Data-Layer Anchoring (documented proxy Layer 4 baselines)
- #23 Provenance pinning (SHA-256 + audit sidecar)
- #29 Per-substation R3 variance (preserved)
- #36 Cross-border filter (5.0 km tolerance turkey entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation
- #60 Non-commercial provenance
- #67 Consumer-adapter discipline (renderer uses ssi-data.json directly)
- #78 BINDING 12th enforcement (Turkish + Kurdish + Arabic + Greek + Ottoman)
- #78 §4bis.5 8TH ENFORCEMENT (Istanbul 3-way BEDAŞ + AYEDAŞ + BOĞAZİÇİ)
"""
from __future__ import annotations

import json
import logging
import math
import sys
from pathlib import Path
from typing import Any

from scripts.pipeline.ingestion.turkey._base import (
    COUNTRY_SLUG,
    check_discipline_41,
    resolve_owner,
)
from scripts.pipeline.ingestion.turkey.osm_overpass import fetch_turkey_osm

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SSI_DATA_PATH = REPO_ROOT / COUNTRY_SLUG / "ssi-data.json"
GRID_GEO_PATH = REPO_ROOT / COUNTRY_SLUG / "grid-geo.json"
VOLTAGE_XCHECK_PATH = REPO_ROOT / COUNTRY_SLUG / "v4_23-voltage-cross-validation.json"

# ─── Spatial match tolerance ───
MATCH_RADIUS_M = 500  # canonical Nordic precedent


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters."""
    R = 6_371_000.0  # Earth mean radius m
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def load_baseline_subs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load Turkey baseline ssi-data.json.

    Returns (substations_list, full_document).
    Handles both flat-list root and {"substations": [...]} wrapped schemas.
    """
    if not SSI_DATA_PATH.exists():
        logger.warning(f"Baseline not found at {SSI_DATA_PATH}; creating fresh")
        return ([], {"substations": []})
    data = json.loads(SSI_DATA_PATH.read_text())
    if isinstance(data, list):
        # Flat-list schema (Convention #78 §4bis.4 Latvia precedent) — guard defensively
        return (data, {"substations": data})
    subs = data.get("substations", [])
    return (subs, data)


def load_baseline_lines() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load Turkey baseline grid-geo.json lines."""
    if not GRID_GEO_PATH.exists():
        logger.warning(f"grid-geo.json not found at {GRID_GEO_PATH}; creating fresh")
        return ([], {"features": []})
    data = json.loads(GRID_GEO_PATH.read_text())
    features = data.get("features", [])
    lines = [f for f in features if f.get("geometry", {}).get("type") in ("LineString", "MultiLineString")]
    return (lines, data)


def merge_substations(
    baseline_subs: list[dict[str, Any]],
    osm_subs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Merge OSM substations into baseline with 500m spatial matching.

    Returns (final_subs_list, stats_dict).
    Stats: enriched, voltage_filled, net_new_substations, voltage_xcheck_findings,
           step_4b_retroactive_attribution
    """
    stats = {
        "enriched": 0,
        "voltage_filled": 0,
        "net_new_substations": 0,
        "voltage_xcheck_findings": 0,
        "step_4b_retroactive_attribution": 0,
    }
    voltage_xcheck_findings: list[dict[str, Any]] = []

    # Build spatial index of baseline subs
    baseline_indexed = []
    for i, sub in enumerate(baseline_subs):
        lat = sub.get("lat") or sub.get("latitude")
        lon = sub.get("lon") or sub.get("lng") or sub.get("longitude")
        if lat is not None and lon is not None:
            baseline_indexed.append((i, float(lat), float(lon)))

    # ── Match OSM subs to baseline within 500m ──
    matched_baseline_indices = set()
    unmatched_osm_subs = []

    for osm_sub in osm_subs:
        osm_lat, osm_lon = osm_sub.get("lat"), osm_sub.get("lon")
        if osm_lat is None or osm_lon is None:
            unmatched_osm_subs.append(osm_sub)
            continue

        best_match_idx = None
        best_dist = float("inf")
        for i, blat, blon in baseline_indexed:
            if i in matched_baseline_indices:
                continue
            d = haversine_m(osm_lat, osm_lon, blat, blon)
            if d < MATCH_RADIUS_M and d < best_dist:
                best_dist = d
                best_match_idx = i

        if best_match_idx is not None:
            # Enrich baseline sub with OSM data
            baseline_sub = baseline_subs[best_match_idx]
            matched_baseline_indices.add(best_match_idx)
            stats["enriched"] += 1

            # Voltage cross-validation
            osm_kv = osm_sub.get("voltage_kv")
            baseline_kv = baseline_sub.get("voltage_kv") or baseline_sub.get("voltage")
            if osm_kv is not None and baseline_kv is not None:
                try:
                    baseline_kv_f = float(baseline_kv)
                    if abs(osm_kv - baseline_kv_f) > 5.0:
                        stats["voltage_xcheck_findings"] += 1
                        voltage_xcheck_findings.append({
                            "baseline_idx": best_match_idx,
                            "baseline_kv": baseline_kv_f,
                            "osm_kv": osm_kv,
                            "delta_kv": osm_kv - baseline_kv_f,
                            "lat": osm_lat,
                            "lon": osm_lon,
                        })
                except (ValueError, TypeError):
                    pass
            elif osm_kv is not None and baseline_kv is None:
                # Voltage-filled from OSM
                baseline_sub["voltage_kv"] = osm_kv
                stats["voltage_filled"] += 1

            # Step 4b retroactive attribution via 8-layer resolver
            if not baseline_sub.get("operator"):
                result = resolve_owner(
                    osm_operator=osm_sub.get("operator"),
                    voltage_kv=osm_sub.get("voltage_kv") or baseline_sub.get("voltage_kv"),
                    lat=osm_lat,
                    lon=osm_lon,
                    province=osm_sub.get("province") or baseline_sub.get("province"),
                    name=osm_sub.get("name") or baseline_sub.get("name"),
                )
                baseline_sub["operator"] = result.canonical_name
                baseline_sub["_owner_provenance"] = result.provenance
                stats["step_4b_retroactive_attribution"] += 1
        else:
            unmatched_osm_subs.append(osm_sub)

    # ── Convert unmatched OSM subs to net-new baseline entries ──
    for osm_sub in unmatched_osm_subs:
        # Skip if no coordinates (can't materialise on map)
        if osm_sub.get("lat") is None or osm_sub.get("lon") is None:
            continue

        # Apply Convention #56 Re_raw=1.0, Re_norm=0.0 defaults
        new_sub = {
            "lat": osm_sub["lat"],
            "lon": osm_sub["lon"],
            "voltage_kv": osm_sub.get("voltage_kv"),
            "operator": osm_sub.get("_resolved_operator") or osm_sub.get("operator"),
            "name": osm_sub.get("name"),
            "province": osm_sub.get("province"),
            "osm_id": osm_sub.get("osm_id"),
            "osm_type": osm_sub.get("osm_type"),
            "_owner_provenance": osm_sub.get("_owner_provenance"),
            "_source": "osm_overpass_v4_23_p30",
            # Convention #56 visibly-honest degradation defaults
            "Re_raw": 1.0,
            "Re_norm": 0.0,
        }
        baseline_subs.append(new_sub)
        stats["net_new_substations"] += 1

    # Write voltage cross-validation report
    VOLTAGE_XCHECK_PATH.parent.mkdir(parents=True, exist_ok=True)
    xcheck_report = {
        "schema_version": "v4_23-voltage-xcheck-1",
        "country": COUNTRY_SLUG,
        "findings_count": len(voltage_xcheck_findings),
        "match_pairs_count": stats["enriched"],
        "rate_pct": (len(voltage_xcheck_findings) / stats["enriched"] * 100.0)
        if stats["enriched"] > 0
        else 0.0,
        "findings": voltage_xcheck_findings[:100],  # cap at 100 for size
    }
    VOLTAGE_XCHECK_PATH.write_text(json.dumps(xcheck_report, separators=(",", ":"), ensure_ascii=False))
    logger.info(
        f"Wrote voltage cross-validation report: {VOLTAGE_XCHECK_PATH} "
        f"({len(voltage_xcheck_findings)} findings across {stats['enriched']} matched pairs)"
    )

    return (baseline_subs, stats)


def merge_lines(
    baseline_lines: list[dict[str, Any]],
    osm_lines: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Merge OSM transmission lines into baseline with dedup by osm_id."""
    stats = {"lines_appended": 0, "lines_deduped": 0}

    baseline_osm_ids = set()
    for line in baseline_lines:
        props = line.get("properties", {}) or {}
        oid = props.get("osm_id") or props.get("id")
        if oid:
            baseline_osm_ids.add(str(oid))

    for osm_line in osm_lines:
        oid = str(osm_line.get("osm_id", ""))
        if oid in baseline_osm_ids:
            stats["lines_deduped"] += 1
            continue
        # Append as GeoJSON-ish
        new_line = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": []},
            "properties": {
                "osm_id": oid,
                "voltage_kv": osm_line.get("voltage_kv"),
                "operator": osm_line.get("operator"),
                "_source": "osm_overpass_v4_23_p30",
            },
        }
        baseline_lines.append(new_line)
        stats["lines_appended"] += 1

    return (baseline_lines, stats)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ─── Step 1: Fetch OSM Overpass ───
    logger.info("Fetching OSM Turkey (subs + lines one-shot; single-query pattern)...")
    osm_result = fetch_turkey_osm()
    logger.info(
        f"OSM ingestion: {len(osm_result.substations)} substations + "
        f"{len(osm_result.lines)} lines + SHA-256 {osm_result.raw_sha256}"
    )

    # ─── Step 2: Load baselines ───
    logger.info(f"Loading {SSI_DATA_PATH} ...")
    baseline_subs, ssi_doc = load_baseline_subs()
    logger.info(f"  existing: {len(baseline_subs)} substations")

    logger.info(f"Loading {GRID_GEO_PATH} ...")
    baseline_lines, grid_doc = load_baseline_lines()
    logger.info(f"  existing: {len(baseline_lines)} lines")

    # ─── Step 3: Merge substations ───
    final_subs, sub_stats = merge_substations(baseline_subs, osm_result.substations)
    logger.info(
        f"Substation merge: {sub_stats['enriched']} enriched + "
        f"{sub_stats['voltage_filled']} voltage-filled + "
        f"{sub_stats['net_new_substations']} net-new + "
        f"{sub_stats['voltage_xcheck_findings']} xcheck findings"
    )
    logger.info(
        f"Step 4b retroactive attribution: {sub_stats['step_4b_retroactive_attribution']} "
        f"subs closed via 8-layer multi-DSO resolver"
    )

    # ─── Step 4: Merge lines ───
    final_lines, line_stats = merge_lines(baseline_lines, osm_result.lines)
    logger.info(
        f"Line merge: {line_stats['lines_appended']} appended + "
        f"{line_stats['lines_deduped']} deduped (existing tier match)"
    )

    # ─── Step 5: Write canonicals (Convention #56 compact JSON) ───
    ssi_doc["substations"] = final_subs
    SSI_DATA_PATH.write_text(
        json.dumps(ssi_doc, separators=(",", ":"), ensure_ascii=False)
    )
    logger.info(
        f"Wrote {SSI_DATA_PATH} "
        f"({SSI_DATA_PATH.stat().st_size / 1024 / 1024:.1f} MB, {len(final_subs)} substations)"
    )

    # For grid-geo, keep the FeatureCollection schema
    if "features" not in grid_doc:
        grid_doc["type"] = "FeatureCollection"
        grid_doc["features"] = []
    # Preserve non-line features + append merged lines
    non_line_features = [
        f for f in grid_doc.get("features", [])
        if f.get("geometry", {}).get("type") not in ("LineString", "MultiLineString")
    ]
    grid_doc["features"] = non_line_features + final_lines
    GRID_GEO_PATH.write_text(
        json.dumps(grid_doc, separators=(",", ":"), ensure_ascii=False)
    )

    # ─── Print merge stats summary ───
    print()
    print("Merge stats:")
    print(f"  enriched: {sub_stats['enriched']}")
    print(f"  voltage_filled: {sub_stats['voltage_filled']}")
    print(f"  net_new_substations: {sub_stats['net_new_substations']}")
    print(f"  voltage_xcheck_findings: {sub_stats['voltage_xcheck_findings']}")
    print(f"  step_4b_retroactive_attribution: {sub_stats['step_4b_retroactive_attribution']}")
    print(f"  final_substation_count: {len(final_subs)}")
    print(f"  lines_appended: {line_stats['lines_appended']}")
    print(f"  lines_deduped: {line_stats['lines_deduped']}")
    print(f"  final_line_count: {len(final_lines)}")
    print(f"  raw_sha256: {osm_result.raw_sha256}")
    print(f"  raw_bytes_fetched: {osm_result.raw_bytes_fetched}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
