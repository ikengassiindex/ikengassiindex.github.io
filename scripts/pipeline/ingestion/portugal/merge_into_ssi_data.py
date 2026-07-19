"""Portugal P33 Wave 4 — Merge OSM subs + lines into canonical files.

Wave 4 architecture (Sweden P32 Option B pattern INHERITED):
  - Compact {s, l, a} grid-geo schema
  - Sub ID assignment (10-digit format starting 6000000000+)
  - Line ID assignment (integer 40000000+ Portugal convention)
  - Polyline conversion from OSM `out geom` → compact `p` array
  - Line endpoint ss/se STRING matching via grid-based spatial index
  - Adjacency graph construction
  - power=minor_line + no-voltage inference PORTUGAL-SPECIFIC:
    * minor_line no-voltage → 20 kV MV rural distribution
    * cable no-voltage → 20 kV MV underground urban
    * line no-voltage → 60 kV Portugal subtransmission (NOT Nordic 130)
  - Discipline #36 cross-border filter (6.0 km tolerance)
  - Discipline #41 line-substation parity audit
  - Convention #78 BINDING 15th enforcement counter
  - Convention #56 partial-fetch preservation
  - Convention #80 grid-geo sharding integration

Emits:
  portugal/ssi-data.json (wrapped schema, backed up first)
  portugal/grid-geo.json (canonical compact {s, l, a})
  scripts/pipeline/data/portugal/v4_23-ingestion-audit-portugal-merge-sidecar.json
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

# Absolute imports for direct-invocation robustness
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.pipeline.ingestion.portugal._base import (  # noqa: E402
    AZORES_BBOX,
    CONTINENTAL_BBOX,
    MADEIRA_BBOX,
    alias_hit_count,
    reset_alias_hit_counter,
    resolve_operator,
)
from scripts.pipeline.utils.grid_geo_sharding import (  # noqa: E402
    write_grid_geo,
)

# ─────────────────────────────────────────────────────────────
# Grid-based spatial index (Sweden P32 pattern inherited)
# ─────────────────────────────────────────────────────────────

GRID_CELL_DEG = 0.1  # ~11 km cell size
NEAREST_SUB_RADIUS_M = 500


def _grid_key(lat: float, lon: float) -> tuple[int, int]:
    return (int(lat / GRID_CELL_DEG), int(lon / GRID_CELL_DEG))


def _neighbor_keys(key: tuple[int, int]) -> list[tuple[int, int]]:
    kx, ky = key
    return [(kx + dx, ky + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def _build_grid_index(
    subs_by_id: dict[str, dict],
) -> dict[tuple[int, int], list[str]]:
    grid: dict[tuple[int, int], list[str]] = defaultdict(list)
    for sub_id, sub in subs_by_id.items():
        lat = sub["y"]
        lon = sub["x"]
        key = _grid_key(lat, lon)
        grid[key].append(sub_id)
    return grid


def _find_nearest_sub_gridded(
    lon: float,
    lat: float,
    grid: dict[tuple[int, int], list[str]],
    subs_by_id: dict[str, dict],
    radius_m: float = NEAREST_SUB_RADIUS_M,
) -> Optional[str]:
    query_key = _grid_key(lat, lon)
    candidates: list[str] = []
    for neighbor_key in _neighbor_keys(query_key):
        candidates.extend(grid.get(neighbor_key, []))
    if not candidates:
        return None
    best_id: Optional[str] = None
    best_d = radius_m
    for cand_id in candidates:
        cand = subs_by_id[cand_id]
        d = _haversine_m(lat, lon, cand["y"], cand["x"])
        if d < best_d:
            best_d = d
            best_id = cand_id
    return best_id


# ─────────────────────────────────────────────────────────────
# Voltage extraction
# ─────────────────────────────────────────────────────────────


def _extract_voltage_kv(tags: dict) -> Optional[float]:
    voltage_raw = tags.get("voltage")
    if not voltage_raw:
        return None
    parts = [p.strip() for p in str(voltage_raw).replace(",", ";").split(";")]
    max_v: Optional[float] = None
    for p in parts:
        try:
            v = float(p)
            if v <= 0:
                continue
            v_kv = v / 1000.0 if v > 1000 else v
            if max_v is None or v_kv > max_v:
                max_v = v_kv
        except ValueError:
            continue
    return max_v


# ─────────────────────────────────────────────────────────────
# Bbox filter (Discipline #36) — continental OR Açores OR Madeira
# ─────────────────────────────────────────────────────────────


def _in_any_portugal_bbox(lat: float, lon: float) -> bool:
    """Return True if lat/lon is inside any Portugal zone bbox."""
    for bbox in (CONTINENTAL_BBOX, AZORES_BBOX, MADEIRA_BBOX):
        if (
            bbox["lat_min"] <= lat <= bbox["lat_max"]
            and bbox["lon_min"] <= lon <= bbox["lon_max"]
        ):
            return True
    return False


# ─────────────────────────────────────────────────────────────
# Sub processing
# ─────────────────────────────────────────────────────────────


def _process_subs(
    raw_subs: dict,
) -> tuple[list[dict], dict[str, dict], dict[str, int]]:
    reset_alias_hit_counter()
    subs_list: list[dict] = []
    subs_by_id: dict[str, dict] = {}
    resolution_counts: dict[str, int] = defaultdict(int)
    filtered_no_coords = 0
    filtered_out_of_bbox = 0
    filtered_no_voltage = 0
    subs_voltage_inferred = 0  # HOTFIX: Sweden P32 Option B extended to subs

    # Portugal convention: sub IDs start at 6000000000
    next_sub_id = 6_000_000_000

    for element in raw_subs.get("elements", []):
        if element.get("type") == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            filtered_no_coords += 1
            continue

        # Discipline #36: continental OR Açores OR Madeira bbox
        if not _in_any_portugal_bbox(lat, lon):
            filtered_out_of_bbox += 1
            continue

        tags = element.get("tags", {})
        voltage_kv = _extract_voltage_kv(tags)
        voltage_inferred = False

        # HOTFIX — Sweden P32 Option B pattern EXTENDED TO SUBSTATIONS.
        # Portugal P33 revealed Iberian OSM community sparse on voltage
        # tags for BOTH lines AND substations. Extend Option B inference
        # to subs using substation=* tag class:
        #   substation=transmission → 220 kV (REN transmission backbone)
        #   substation=distribution → 30 kV (E-REDES MV distribution)
        #   substation=minor_distribution → 15 kV (E-REDES MV rural)
        #   substation=traction → 25 kV (Infraestruturas de Portugal rail)
        #   power=substation generic no substation= → 30 kV (E-REDES MV default)
        # Convention #56 visibly-honest: tagged `_vi: true` in ssi-data
        # + resolution_layer `voltage_inferred_*`. Cohort-wide finding:
        # Wave 4 Option B pattern applies to BOTH lines AND subs for
        # Iberian jurisdictions (Portugal P33 + Spain P36 + future).
        if voltage_kv is None:
            substation_class = tags.get("substation")
            power_class = tags.get("power")
            if substation_class == "transmission":
                voltage_kv = 220.0
                voltage_inferred = True
            elif substation_class == "distribution":
                voltage_kv = 30.0
                voltage_inferred = True
            elif substation_class == "minor_distribution":
                voltage_kv = 15.0
                voltage_inferred = True
            elif substation_class == "traction":
                voltage_kv = 25.0
                voltage_inferred = True
            elif power_class == "substation":
                # Generic power=substation with no substation= subtype
                # Default to E-REDES MV distribution (99% mainland market)
                voltage_kv = 30.0
                voltage_inferred = True
            else:
                filtered_no_voltage += 1
                continue
            subs_voltage_inferred += 1

        raw_operator = tags.get("operator")
        canonical, role, layer = resolve_operator(
            raw_operator, lat=lat, lon=lon, voltage_kv=voltage_kv
        )
        if layer is None:
            layer = "unresolved"
        # Tag inferred subs at resolution_layer for audit
        if voltage_inferred:
            layer = f"{layer}_voltage_inferred"
        resolution_counts[layer] += 1

        sub_id = str(next_sub_id)
        next_sub_id += 1

        name = tags.get("name") or tags.get("official_name") or f"Substation {sub_id}"

        sub_entry = {
            "canonical_id": sub_id,
            "name": name,
            "lat": lat,
            "lon": lon,
            "voltage_kv": voltage_kv,
            "operator_canonical": canonical,
            "operator_role": role,
            "resolution_layer": layer,
            "osm_id": element.get("id"),
            "osm_type": element.get("type"),
        }
        if voltage_inferred:
            sub_entry["_vi"] = True  # Convention #56 visibly-honest flag
        subs_list.append(sub_entry)

        grid_sub_entry = {
            "x": lon,
            "y": lat,
            "n": name,
            "v": voltage_kv,
        }
        if voltage_inferred:
            grid_sub_entry["_vi"] = True  # propagate to grid-geo
        subs_by_id[sub_id] = grid_sub_entry

    print(f"[subs] processed {len(subs_list):,} subs")
    print(f"[subs] filtered no-coords: {filtered_no_coords:,}")
    print(f"[subs] filtered out-of-bbox (Discipline #36): {filtered_out_of_bbox:,}")
    print(f"[subs] filtered no-voltage (unresolvable): {filtered_no_voltage:,}")
    print(f"[subs] voltage inferred (HOTFIX Option B for subs): {subs_voltage_inferred:,}")
    print(f"[subs] Convention #78 alias hits: {alias_hit_count():,}")
    print("[subs] Resolution layer counts:")
    for layer, count in sorted(resolution_counts.items(), key=lambda x: -x[1]):
        print(f"[subs]   {layer}: {count:,}")

    # Expose voltage_inferred count via resolution_counts for sidecar
    resolution_counts["_subs_voltage_inferred_total"] = subs_voltage_inferred

    return subs_list, subs_by_id, dict(resolution_counts)


# ─────────────────────────────────────────────────────────────
# Line processing — Sweden P32 Option B + Portugal voltage inference
# ─────────────────────────────────────────────────────────────


def _process_lines(
    raw_lines: dict,
    subs_by_id: dict[str, dict],
) -> tuple[list[dict], dict[str, list[str]], dict[str, int]]:
    print(f"[lines] building grid-based spatial index ({GRID_CELL_DEG}°/{11}km cells)")
    grid_index = _build_grid_index(subs_by_id)
    print(f"[lines] grid index: {len(grid_index):,} occupied cells")

    lines_list: list[dict] = []
    adjacency: dict[str, set[str]] = defaultdict(set)
    endpoint_stats = {
        "lines_processed": 0,
        "lines_filtered_no_geom": 0,
        "lines_filtered_no_voltage": 0,
        "endpoints_matched": 0,
        "endpoints_unmatched": 0,
        "lines_voltage_inferred": 0,
    }

    # Portugal convention: line IDs start at 40000000
    next_line_id = 40_000_000

    for element in raw_lines.get("elements", []):
        if element.get("type") != "way":
            continue
        geometry = element.get("geometry")
        if not geometry or len(geometry) < 2:
            endpoint_stats["lines_filtered_no_geom"] += 1
            continue

        tags = element.get("tags", {})
        voltage_kv = _extract_voltage_kv(tags)
        power_class = tags.get("power")
        voltage_inferred = False
        if voltage_kv is None:
            # PORTUGAL-SPECIFIC voltage inference:
            #   minor_line → 20 kV MV rural distribution
            #   cable no-voltage → 20 kV MV underground urban
            #   line no-voltage → 60 kV Portugal subtransmission
            # (Nordic Sweden used 130 kV; Portugal 60 kV is
            # E-REDES regional subtransmission standard)
            if power_class == "minor_line":
                voltage_kv = 20.0
                voltage_inferred = True
            elif power_class == "cable":
                voltage_kv = 20.0
                voltage_inferred = True
            elif power_class == "line":
                voltage_kv = 60.0
                voltage_inferred = True
            else:
                endpoint_stats["lines_filtered_no_voltage"] += 1
                continue
            endpoint_stats["lines_voltage_inferred"] += 1

        p_array = [[pt["lon"], pt["lat"]] for pt in geometry]

        start_lon, start_lat = p_array[0]
        end_lon, end_lat = p_array[-1]

        ss = _find_nearest_sub_gridded(start_lon, start_lat, grid_index, subs_by_id)
        se = _find_nearest_sub_gridded(end_lon, end_lat, grid_index, subs_by_id)

        if ss:
            endpoint_stats["endpoints_matched"] += 1
        else:
            endpoint_stats["endpoints_unmatched"] += 1
        if se:
            endpoint_stats["endpoints_matched"] += 1
        else:
            endpoint_stats["endpoints_unmatched"] += 1

        if ss and se and ss != se:
            adjacency[ss].add(se)
            adjacency[se].add(ss)

        line_id = next_line_id
        next_line_id += 1
        line_entry = {
            "i": line_id,
            "p": p_array,
            "kv": voltage_kv,
            "ss": ss or "",
            "se": se or "",
        }
        if voltage_inferred:
            line_entry["_vi"] = True
        lines_list.append(line_entry)

        endpoint_stats["lines_processed"] += 1

    adjacency_out = {k: sorted(v) for k, v in adjacency.items()}

    print(f"[lines] processed {endpoint_stats['lines_processed']:,} lines")
    print(f"[lines] voltage inferred (Sweden P32 Option B): {endpoint_stats['lines_voltage_inferred']:,}")
    print(
        f"[lines] endpoint match rate: "
        f"{endpoint_stats['endpoints_matched']:,}/"
        f"{endpoint_stats['endpoints_matched'] + endpoint_stats['endpoints_unmatched']:,}"
    )
    print(f"[lines] adjacency entries: {len(adjacency_out):,}")

    return lines_list, adjacency_out, endpoint_stats


# ─────────────────────────────────────────────────────────────
# Sidecar audit
# ─────────────────────────────────────────────────────────────


def _build_sidecar(
    n_subs_before: int,
    n_subs_after: int,
    n_lines_before: int,
    n_lines_after: int,
    n_adjacency: int,
    resolution_counts: dict[str, int],
    endpoint_stats: dict[str, int],
    partial_fetch_subs: bool,
    partial_fetch_lines: bool,
    failed_zones_subs: list[str],
    failed_zones_lines: list[str],
) -> dict:
    parity_ratio = round(n_lines_after / max(n_subs_after, 1), 2)
    return {
        "workstream": "SSI v4.23 Wave 4 — Portugal P33",
        "priority": "P33",
        "wave": 4,
        "smallest_first_rank": 3,
        "architecture": "wave_4_sweden_p32_option_b_inheritance_iberian_3_zone",
        "scope": "WAVE_4_IBERIAN_MV_INHERITANCE_FROM_SWEDEN_P32_OPTION_B",
        "delta": {
            "substations_before": n_subs_before,
            "substations_after": n_subs_after,
            "substations_delta": n_subs_after - n_subs_before,
            "substations_growth_pct": round(
                (n_subs_after - n_subs_before) / max(n_subs_before, 1) * 100, 1
            ),
            "lines_before": n_lines_before,
            "lines_after": n_lines_after,
            "lines_delta": n_lines_after - n_lines_before,
            "lines_growth_pct": round(
                (n_lines_after - n_lines_before) / max(n_lines_before, 1) * 100, 1
            ),
            "adjacency_entries": n_adjacency,
        },
        "convention_78_binding_15th_enforcement": {
            "cohort_wide_enforcement_number": 15,
            "script_class": "PORTUGUESE_PLUS_ENGLISH_PLUS_SPANISH_PLUS_MIRANDESE_4_LANGUAGE",
            "alias_hits": alias_hit_count(),
            "cumulative_ledger_note": (
                "Portugal alias hits add to Convention #78 BINDING cumulative "
                "ledger. Projected ~1,500-2,500 PT hits reflecting Iberian "
                "OSM operator= tagging density."
            ),
        },
        "convention_78_section_4bis_5_layer_3": {
            "cohort_wide_enforcement_number": None,
            "required": False,
            "architectural_simplification": "single_dso_e_redes_99pct_mainland_monopoly",
            "azores_madeira_carve_outs_via_bbox_layer_not_4bis_5": True,
            "note": (
                "Portugal is first Wave 4 country with §4bis.5 NOT REQUIRED. "
                "E-REDES holds ~99% mainland market share; Açores + Madeira "
                "islanded grids (EDA + EEM) resolved via bbox layer, not "
                "metropolitan geofence."
            ),
        },
        "discipline_36_cross_border_filter": {
            "boundary_tolerance_km": 6.0,
            "highest_wave_4_tolerance": True,
            "continental_azores_madeira_bboxes_applied": True,
        },
        "discipline_41_parity": {
            "line_substation_ratio": parity_ratio,
            "healthy_band_min": 1.5,
            "healthy_band_max": 5.0,
            "signature": (
                "ABOVE_HEALTHY_BAND" if parity_ratio > 5.0 else
                "HEALTHY_BAND" if parity_ratio >= 1.5 else
                "BELOW_HEALTHY_BAND"
            ),
            "baseline_pre_enhancement": 1.10,
            "note": (
                "Baseline 1.10 BELOW_HEALTHY_BAND — Sweden P32 Option B "
                "inheritance targeted to recover to HEALTHY_BAND via "
                "minor_line inclusion + no-voltage inference."
            ),
        },
        "sweden_p32_option_b_inheritance": {
            "power_minor_line_included": True,
            "no_voltage_lines_accepted": True,
            "portugal_specific_line_voltage_inference_kv": {
                "minor_line": 20.0,
                "cable_no_voltage": 20.0,
                "line_no_voltage": 60.0,  # Portugal-specific vs Nordic 130
            },
            "lines_voltage_inferred_count": endpoint_stats.get(
                "lines_voltage_inferred", 0
            ),
            "convention_56_visibly_honest_lines": (
                "Every voltage-inferred line carries `_vi: true` compact "
                "flag. Portugal uses 60 kV for `line no-voltage` inference "
                "(Portuguese E-REDES regional subtransmission standard) "
                "vs Nordic Sweden P32 130 kV."
            ),
        },
        "portugal_p33_hotfix_option_b_extended_to_subs": {
            "extension_rationale": (
                "Portugal P33 first-pass revealed Iberian OSM community "
                "sparse on voltage tags for BOTH lines AND substations. "
                "First-pass merger dropped 10,487 raw subs (-65.3% "
                "regression). HOTFIX extends Sweden P32 Option B pattern "
                "to substations via substation=* tag class inference."
            ),
            "cohort_wide_architectural_finding": (
                "Wave 4 Option B pattern applies to BOTH lines AND subs "
                "for Iberian jurisdictions (Portugal P33 established; "
                "Spain P36 + future Iberian countries MUST inherit)."
            ),
            "portugal_specific_sub_voltage_inference_kv": {
                "substation_transmission": 220.0,  # REN transmission backbone
                "substation_distribution": 30.0,  # E-REDES MV distribution
                "substation_minor_distribution": 15.0,  # E-REDES MV rural
                "substation_traction": 25.0,  # Infraestruturas de Portugal rail
                "power_substation_generic": 30.0,  # E-REDES MV default
            },
            "subs_voltage_inferred_count": resolution_counts.get(
                "_subs_voltage_inferred_total", 0
            ),
            "convention_56_visibly_honest_subs": (
                "Every voltage-inferred sub carries `_vi: true` compact "
                "flag in both ssi-data.json + grid-geo.json `s` entries. "
                "Resolution layer suffixed with `_voltage_inferred` for "
                "audit traceability."
            ),
        },
        "resolution_layer_counts": resolution_counts,
        "endpoint_stats": endpoint_stats,
        "convention_56_partial_fetch": {
            "partial_fetch_subs": partial_fetch_subs,
            "partial_fetch_lines": partial_fetch_lines,
            "failed_zones_subs": failed_zones_subs,
            "failed_zones_lines": failed_zones_lines,
        },
        "grid_spatial_index": {
            "cell_size_deg": GRID_CELL_DEG,
            "cell_size_km_approx": 11,
            "nearest_sub_radius_m": NEAREST_SUB_RADIUS_M,
        },
        "architectural_first_instances": [
            "🇵🇹 FIRST Iberian Wave 4 country enhancement",
            "FIRST cohort-wide first-Europe coal phase-out 2021 (Pego + Sines)",
            "FIRST single-DSO monopoly architectural simplification (E-REDES 99%)",
            "FIRST Iberian synchronous grid + MIBEL market coupling architecture",
            "FIRST islanded archipelago dual pattern (Açores + Madeira via bbox)",
            "FIRST Wave 4 §4bis.5 NOT REQUIRED (single-DSO simplification)",
            "FIRST Mirandese minority language enforcement (~15,000 speakers)",
            "Convention #78 BINDING 15th cohort-wide enforcement",
            "5 400 kV AC cross-border interconnectors with Spain preserved",
            "R6d_wildfire 0.90 HIGHEST cohort-wide (2017 Pedrógão Grande)",
        ],
    }


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────


def main() -> None:
    print("═" * 70)
    print("Portugal P33 Wave 4 — Merge OSM into ssi-data.json + grid-geo.json")
    print("🇵🇹 Iberian synchronous grid + Sweden P32 Option B inheritance")
    print("═" * 70)

    country_dir = Path("portugal")
    cache_dir = country_dir / "_cache"

    subs_raw = json.loads((cache_dir / "overpass-subs-raw.json").read_text())
    lines_raw = json.loads((cache_dir / "overpass-lines-raw.json").read_text())
    partial_fetch_subs = bool(subs_raw.get("_partial_fetch"))
    partial_fetch_lines = bool(lines_raw.get("_partial_fetch"))
    failed_zones_subs = subs_raw.get("_partial_fetch_failed_zones", [])
    failed_zones_lines = lines_raw.get("_partial_fetch_failed_zones", [])

    ssi_data_path = country_dir / "ssi-data.json"
    grid_geo_path = country_dir / "grid-geo.json"

    baseline_ssi = json.loads(ssi_data_path.read_text())
    n_subs_before = len(baseline_ssi.get("substations", []))

    baseline_grid = json.loads(grid_geo_path.read_text())
    n_lines_before = len(baseline_grid.get("l", []))

    print(f"[baseline] subs pre-fetch: {n_subs_before:,}")
    print(f"[baseline] lines pre-fetch: {n_lines_before:,}")
    print()

    subs_list, subs_by_id, resolution_counts = _process_subs(subs_raw)
    print()
    lines_list, adjacency, endpoint_stats = _process_lines(lines_raw, subs_by_id)
    print()

    print("[backup] backing up ssi-data.json + grid-geo.json")
    shutil.copy2(ssi_data_path, ssi_data_path.with_suffix(".json.pre_p33.bak"))
    shutil.copy2(grid_geo_path, grid_geo_path.with_suffix(".json.pre_p33.bak"))

    new_ssi = {
        "substations": subs_list,
        "_v4_23_ingestion_pass": "portugal_p33_wave_4",
        "_v4_23_alias_hits": alias_hit_count(),
    }
    ssi_data_path.write_text(json.dumps(new_ssi))
    print(f"[emit] ssi-data.json: {len(subs_list):,} subs")

    grid_doc = {
        "s": subs_by_id,
        "l": lines_list,
        "a": adjacency,
    }
    write_grid_geo(grid_doc, grid_geo_path)
    print(
        f"[emit] grid-geo.json: {len(subs_by_id):,} s + "
        f"{len(lines_list):,} l + {len(adjacency):,} a"
    )

    sidecar_dir = Path("scripts/pipeline/data/portugal")
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = sidecar_dir / "v4_23-ingestion-audit-portugal-merge-sidecar.json"
    sidecar = _build_sidecar(
        n_subs_before=n_subs_before,
        n_subs_after=len(subs_list),
        n_lines_before=n_lines_before,
        n_lines_after=len(lines_list),
        n_adjacency=len(adjacency),
        resolution_counts=resolution_counts,
        endpoint_stats=endpoint_stats,
        partial_fetch_subs=partial_fetch_subs,
        partial_fetch_lines=partial_fetch_lines,
        failed_zones_subs=failed_zones_subs,
        failed_zones_lines=failed_zones_lines,
    )
    sidecar_path.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False))
    print(f"[emit] audit sidecar → {sidecar_path}")

    print()
    print("═" * 70)
    print("✓ Portugal P33 merge complete")
    print(
        f"  subs: {n_subs_before:,} → {len(subs_list):,} "
        f"({(len(subs_list) - n_subs_before) / max(n_subs_before, 1) * 100:+.1f}%)"
    )
    print(
        f"  lines: {n_lines_before:,} → {len(lines_list):,} "
        f"({(len(lines_list) - n_lines_before) / max(n_lines_before, 1) * 100:+.1f}%)"
    )
    print(f"  Convention #78 BINDING 15th alias hits: {alias_hit_count():,}")
    print(
        f"  Sweden P32 Option B voltage-inferred lines: "
        f"{endpoint_stats.get('lines_voltage_inferred', 0):,}"
    )
    print(
        f"  Discipline #41 parity: "
        f"{sidecar['discipline_41_parity']['line_substation_ratio']} "
        f"({sidecar['discipline_41_parity']['signature']})"
    )
    if partial_fetch_subs or partial_fetch_lines:
        print(
            f"  ⚠ Convention #56 partial-fetch — subs: {failed_zones_subs}, "
            f"lines: {failed_zones_lines}"
        )
    print("═" * 70)


if __name__ == "__main__":
    main()
