"""UK P31 merge into ssi-data.json + grid-geo.json — WAVE 4 CORRECTED architecture.

🎉 WAVE 4 P31 = FIRST v4.23 ENHANCEMENT EXTENSION COUNTRY 🎉
Post-Turkey schema-bug LESSON APPLIED:
- Emits canonical compact `{s, l, a}` schema from the start
- Uses OSM `out center` + `out geom` query hints for proper coord resolution
- Substation ID assignment (integer 10-digit 5000000000+ per UK convention)
- Line ID assignment (integer 30000000+ per UK convention)
- Line endpoint (ss/se) STRING matching per UK convention
- Adjacency graph construction (optional; UK baseline empty a dict)

Convention preservation:
- #7 Data-Layer Anchoring
- #23 Provenance pinning (SHA-256 + audit sidecar)
- #29 Per-substation R3 variance (preserved)
- #36 Cross-border filter (3.0 km tolerance uk entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation
- #60 Non-commercial provenance
- #67 Consumer-adapter discipline
- #78 BINDING 13th enforcement (5-language)
- #78 §4bis.5 9TH ENFORCEMENT (London UKPN LPN)
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from scripts.pipeline.ingestion.uk._base import (
    COUNTRY_SLUG,
    add_to_grid_index,
    build_grid_index,
    build_sub_spatial_index,
    check_discipline_41,
    compact_line_entry,
    compact_substation_entry,
    find_nearest_sub,
    find_nearest_sub_gridded,
    haversine_m,
    next_available_line_id,
    next_available_sub_id,
    resolve_owner,
)
from scripts.pipeline.ingestion.uk.osm_overpass import fetch_uk_osm

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SSI_DATA_PATH = REPO_ROOT / COUNTRY_SLUG / "ssi-data.json"
GRID_GEO_PATH = REPO_ROOT / COUNTRY_SLUG / "grid-geo.json"
VOLTAGE_XCHECK_PATH = REPO_ROOT / COUNTRY_SLUG / "v4_23-voltage-cross-validation.json"

MATCH_RADIUS_M = 500  # substation spatial match
LINE_ENDPOINT_MATCH_RADIUS_M = 1000  # line endpoint → substation matching


def load_baseline_ssi_data() -> tuple[list[dict], dict]:
    """Load UK ssi-data.json (wrapped schema)."""
    if not SSI_DATA_PATH.exists():
        return ([], {"substations": []})
    data = json.loads(SSI_DATA_PATH.read_text())
    subs = data.get("substations", []) if isinstance(data, dict) else data
    return (subs, data)


def load_baseline_grid_geo() -> dict:
    """Load UK grid-geo.json (compact `{s, l, a}` schema)."""
    if not GRID_GEO_PATH.exists():
        return {"s": {}, "l": [], "a": {}}
    data = json.loads(GRID_GEO_PATH.read_text())
    # Ensure all 3 keys exist
    data.setdefault("s", {})
    data.setdefault("l", [])
    data.setdefault("a", {})
    return data


def merge_substations_ssi_data(
    baseline_subs: list[dict],
    osm_subs: list[dict],
) -> tuple[list[dict], dict]:
    """Merge OSM subs into ssi-data.json wrapped schema.

    Returns (final_subs, stats).
    """
    stats = {
        "enriched": 0,
        "voltage_filled": 0,
        "net_new": 0,
        "voltage_xcheck_findings": 0,
        "step_4b_retroactive_attribution": 0,
    }
    voltage_findings: list[dict] = []

    # Build baseline spatial index
    baseline_indexed = []
    for i, sub in enumerate(baseline_subs):
        lat = sub.get("lat") or sub.get("latitude")
        lon = sub.get("lon") or sub.get("longitude")
        if lat is not None and lon is not None:
            baseline_indexed.append((i, float(lat), float(lon)))

    matched_baseline = set()
    unmatched_osm = []

    for osm_sub in osm_subs:
        olat, olon = osm_sub.get("lat"), osm_sub.get("lon")
        if olat is None or olon is None:
            unmatched_osm.append(osm_sub)
            continue

        best_idx = None
        best_d = float("inf")
        for i, blat, blon in baseline_indexed:
            if i in matched_baseline:
                continue
            d = haversine_m(olat, olon, blat, blon)
            if d < MATCH_RADIUS_M and d < best_d:
                best_d = d
                best_idx = i

        if best_idx is not None:
            baseline_sub = baseline_subs[best_idx]
            matched_baseline.add(best_idx)
            stats["enriched"] += 1

            # Voltage cross-validation
            okv = osm_sub.get("voltage_kv")
            bkv = baseline_sub.get("voltage_kv") or baseline_sub.get("voltage")
            if okv is not None and bkv is not None:
                try:
                    bkv_f = float(bkv)
                    if abs(okv - bkv_f) > 5.0:
                        stats["voltage_xcheck_findings"] += 1
                        voltage_findings.append({
                            "baseline_idx": best_idx,
                            "baseline_kv": bkv_f,
                            "osm_kv": okv,
                            "delta_kv": okv - bkv_f,
                            "lat": olat,
                            "lon": olon,
                        })
                except (ValueError, TypeError):
                    pass
            elif okv is not None and bkv is None:
                baseline_sub["voltage_kv"] = okv
                stats["voltage_filled"] += 1

            # Step 4b retroactive attribution
            if not baseline_sub.get("operator"):
                result = resolve_owner(
                    osm_operator=osm_sub.get("operator"),
                    voltage_kv=osm_sub.get("voltage_kv") or baseline_sub.get("voltage_kv"),
                    lat=olat,
                    lon=olon,
                    region=osm_sub.get("region") or baseline_sub.get("region"),
                    name=osm_sub.get("name") or baseline_sub.get("name"),
                )
                baseline_sub["operator"] = result.canonical_name
                baseline_sub["_owner_provenance"] = result.provenance
                stats["step_4b_retroactive_attribution"] += 1
        else:
            unmatched_osm.append(osm_sub)

    # Add net-new subs
    for osm_sub in unmatched_osm:
        if osm_sub.get("lat") is None or osm_sub.get("lon") is None:
            continue
        new_sub = {
            "lat": osm_sub["lat"],
            "lon": osm_sub["lon"],
            "voltage_kv": osm_sub.get("voltage_kv"),
            "operator": osm_sub.get("_resolved_operator") or osm_sub.get("operator"),
            "name": osm_sub.get("name"),
            "region": osm_sub.get("region"),
            "osm_id": osm_sub.get("osm_id"),
            "osm_type": osm_sub.get("osm_type"),
            "_owner_provenance": osm_sub.get("_owner_provenance"),
            "_source": "osm_overpass_v4_23_p31_wave_4",
            "Re_raw": 1.0,
            "Re_norm": 0.0,
        }
        baseline_subs.append(new_sub)
        stats["net_new"] += 1

    # Write voltage xcheck report
    xcheck_report = {
        "schema_version": "v4_23-voltage-xcheck-1",
        "country": COUNTRY_SLUG,
        "findings_count": len(voltage_findings),
        "match_pairs_count": stats["enriched"],
        "rate_pct": (len(voltage_findings) / stats["enriched"] * 100.0) if stats["enriched"] > 0 else 0.0,
        "findings": voltage_findings[:100],
    }
    VOLTAGE_XCHECK_PATH.write_text(json.dumps(xcheck_report, separators=(",", ":"), ensure_ascii=False))
    logger.info(
        f"Wrote voltage xcheck report: {VOLTAGE_XCHECK_PATH} "
        f"({len(voltage_findings)} findings across {stats['enriched']} matched pairs)"
    )
    return (baseline_subs, stats)


def merge_grid_geo_compact_schema(
    grid_doc: dict,
    osm_subs: list[dict],
    osm_lines: list[dict],
) -> tuple[dict, dict]:
    """🎉 WAVE 4 CORRECTED MERGE 🎉 — emit canonical compact `{s, l, a}` schema.

    Post-Turkey schema-bug lesson: build s + l + a from OSM data with
    proper coord resolution.

    Returns (merged_grid_doc, stats).
    """
    stats = {
        "s_subs_added_to_compact": 0,
        "l_lines_added_to_compact": 0,
        "l_lines_skipped_no_geometry": 0,
        "l_lines_matched_endpoints": 0,
        "a_adjacency_edges_added": 0,
    }

    # Copy existing s + l + a dicts (defensive)
    s_dict = dict(grid_doc.get("s", {}))
    l_list = list(grid_doc.get("l", []))
    a_dict = {k: list(v) for k, v in grid_doc.get("a", {}).items()}

    # Build grid-based spatial index for O(1) nearest-neighbor queries
    # (Wave 4 performance fix for UK's 60,128 subs × 201,976 lines merge)
    spatial_index = build_sub_spatial_index(s_dict)
    grid_index = build_grid_index(spatial_index)
    logger.info(
        f"Built grid-based spatial index: {len(grid_index)} cells for "
        f"{len(spatial_index)} baseline subs"
    )

    # ─── Step 1: Add net-new OSM substations to compact `s` dict ───
    next_sub_id = next_available_sub_id(s_dict)
    osm_to_compact_id: dict[str, str] = {}  # OSM id → compact sub_id_str for line matching

    for i, osm_sub in enumerate(osm_subs):
        olat, olon = osm_sub.get("lat"), osm_sub.get("lon")
        if olat is None or olon is None:
            continue

        # Check if matches existing sub in compact `s` (GRIDDED lookup — O(1))
        matched_id = find_nearest_sub_gridded(olon, olat, grid_index, radius_m=MATCH_RADIUS_M)
        if matched_id:
            osm_to_compact_id[str(osm_sub.get("osm_id"))] = matched_id
        else:
            # Add net-new to compact `s` dict
            new_id = str(next_sub_id)
            next_sub_id += 1
            s_dict[new_id] = compact_substation_entry(
                lon=olon,
                lat=olat,
                name=osm_sub.get("name") or f"Substation UK-{new_id}",
                voltage_kv=osm_sub.get("voltage_kv"),
            )
            osm_to_compact_id[str(osm_sub.get("osm_id"))] = new_id
            add_to_grid_index(grid_index, new_id, olon, olat)
            stats["s_subs_added_to_compact"] += 1

        if (i + 1) % 10000 == 0:
            logger.info(f"  Substation merge progress: {i+1:,}/{len(osm_subs):,} processed")

    # ─── Step 2: Add OSM lines to compact `l` list with endpoint matching ───
    next_line_id = next_available_line_id(l_list)
    existing_osm_line_ids = {
        (entry.get("_osm_id") if isinstance(entry, dict) else None)
        for entry in l_list
    }

    for line_i, osm_line in enumerate(osm_lines):
        polyline = osm_line.get("polyline")
        if not polyline or len(polyline) < 2:
            stats["l_lines_skipped_no_geometry"] += 1
            continue

        # Match endpoints to substations (GRIDDED lookup — O(1) per query)
        first_pt = polyline[0]   # [lon, lat]
        last_pt = polyline[-1]

        ss_id = find_nearest_sub_gridded(first_pt[0], first_pt[1], grid_index, radius_m=LINE_ENDPOINT_MATCH_RADIUS_M)
        se_id = find_nearest_sub_gridded(last_pt[0], last_pt[1], grid_index, radius_m=LINE_ENDPOINT_MATCH_RADIUS_M)

        if (line_i + 1) % 20000 == 0:
            logger.info(f"  Line merge progress: {line_i+1:,}/{len(osm_lines):,} processed")

        line_entry = compact_line_entry(
            line_id=next_line_id,
            polyline=polyline,
            voltage_kv=osm_line.get("voltage_kv"),
            ss=ss_id,
            se=se_id,
        )
        # Preserve OSM id for future dedup (as _osm_id sidecar field)
        line_entry["_osm_id"] = str(osm_line.get("osm_id"))
        line_entry["_source"] = "osm_overpass_v4_23_p31_wave_4"

        l_list.append(line_entry)
        next_line_id += 1
        stats["l_lines_added_to_compact"] += 1
        if ss_id and se_id:
            stats["l_lines_matched_endpoints"] += 1

            # Build adjacency (bidirectional)
            if ss_id != se_id:
                a_dict.setdefault(ss_id, [])
                if se_id not in a_dict[ss_id]:
                    a_dict[ss_id].append(se_id)
                    stats["a_adjacency_edges_added"] += 1
                a_dict.setdefault(se_id, [])
                if ss_id not in a_dict[se_id]:
                    a_dict[se_id].append(ss_id)

    # Write back
    grid_doc["s"] = s_dict
    grid_doc["l"] = l_list
    grid_doc["a"] = a_dict
    return (grid_doc, stats)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    # ─── Step 1: Fetch OSM ───
    logger.info("Fetching UK OSM Overpass (WAVE 4 CORRECTED — out center + out geom)...")
    osm_result = fetch_uk_osm()
    logger.info(
        f"OSM ingestion: {len(osm_result.substations)} subs + {len(osm_result.lines)} lines + "
        f"SHA-256 {osm_result.raw_sha256}"
    )

    # ─── Step 2: Load baselines ───
    logger.info(f"Loading {SSI_DATA_PATH} ...")
    baseline_subs, ssi_doc = load_baseline_ssi_data()
    logger.info(f"  existing ssi-data: {len(baseline_subs)} substations")

    logger.info(f"Loading {GRID_GEO_PATH} ...")
    grid_doc = load_baseline_grid_geo()
    logger.info(f"  existing grid-geo: s={len(grid_doc['s'])} subs, l={len(grid_doc['l'])} lines, a={len(grid_doc['a'])} adj")

    # ─── Step 3: Merge ssi-data.json ───
    final_subs, sub_stats = merge_substations_ssi_data(baseline_subs, osm_result.substations)
    logger.info(
        f"Substation ssi-data merge: {sub_stats['enriched']} enriched + "
        f"{sub_stats['voltage_filled']} voltage-filled + "
        f"{sub_stats['net_new']} net-new + "
        f"{sub_stats['voltage_xcheck_findings']} xcheck findings"
    )
    logger.info(
        f"Step 4b retroactive attribution: {sub_stats['step_4b_retroactive_attribution']} "
        f"subs closed via 9-layer resolver"
    )

    # ─── Step 4: Merge grid-geo.json COMPACT SCHEMA ───
    logger.info("Merging grid-geo.json COMPACT schema (Wave 4 corrected)...")
    grid_doc, grid_stats = merge_grid_geo_compact_schema(grid_doc, osm_result.substations, osm_result.lines)
    logger.info(
        f"Compact grid-geo merge: "
        f"s +{grid_stats['s_subs_added_to_compact']} net-new subs, "
        f"l +{grid_stats['l_lines_added_to_compact']} lines "
        f"({grid_stats['l_lines_matched_endpoints']} with matched endpoints, "
        f"{grid_stats['l_lines_skipped_no_geometry']} skipped no-geometry), "
        f"a +{grid_stats['a_adjacency_edges_added']} adjacency edges"
    )

    # ─── Step 5: Write canonicals (Convention #56 compact JSON) ───
    ssi_doc["substations"] = final_subs
    SSI_DATA_PATH.write_text(json.dumps(ssi_doc, separators=(",", ":"), ensure_ascii=False))
    logger.info(f"Wrote {SSI_DATA_PATH} ({SSI_DATA_PATH.stat().st_size / 1024 / 1024:.1f} MB, {len(final_subs)} substations)")

    GRID_GEO_PATH.write_text(json.dumps(grid_doc, separators=(",", ":"), ensure_ascii=False))
    logger.info(
        f"Wrote {GRID_GEO_PATH} ({GRID_GEO_PATH.stat().st_size / 1024 / 1024:.1f} MB, "
        f"compact {{s: {len(grid_doc['s'])}, l: {len(grid_doc['l'])}, a: {len(grid_doc['a'])}}})"
    )

    # ─── Print summary ───
    print()
    print("Merge stats (WAVE 4 CORRECTED architecture):")
    print(f"  --- ssi-data.json (substations) ---")
    print(f"  enriched: {sub_stats['enriched']}")
    print(f"  voltage_filled: {sub_stats['voltage_filled']}")
    print(f"  net_new_substations: {sub_stats['net_new']}")
    print(f"  voltage_xcheck_findings: {sub_stats['voltage_xcheck_findings']}")
    print(f"  step_4b_retroactive_attribution: {sub_stats['step_4b_retroactive_attribution']}")
    print(f"  final_substation_count: {len(final_subs)}")
    print(f"  --- grid-geo.json (COMPACT SCHEMA) ---")
    print(f"  s_dict_final: {len(grid_doc['s'])} substations")
    print(f"  l_list_final: {len(grid_doc['l'])} lines")
    print(f"  a_dict_final: {len(grid_doc['a'])} adjacency entries")
    print(f"  s_subs_net_new_added: {grid_stats['s_subs_added_to_compact']}")
    print(f"  l_lines_added_to_compact: {grid_stats['l_lines_added_to_compact']}")
    print(f"  l_lines_matched_endpoints: {grid_stats['l_lines_matched_endpoints']}")
    print(f"  l_lines_skipped_no_geometry: {grid_stats['l_lines_skipped_no_geometry']}")
    print(f"  a_adjacency_edges_added: {grid_stats['a_adjacency_edges_added']}")
    print(f"  raw_sha256: {osm_result.raw_sha256}")
    print(f"  raw_bytes_fetched: {osm_result.raw_bytes_fetched}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
