"""
SSI Pipeline — Costa Rica v4.23 federation merger.

Merges OSM Overpass L1 ingestion into costa-rica/ssi-data.json + grid-geo.json.

Merger operations (Option A per pre-flight):

  1. Owner-enrichment on matched pairs (500 m Discipline #41 threshold):
     Direct OSM operator= tag (with DSO alias normalisation: Spanish legal
     forms R.L./RL/S.A. + regulatory abbreviations I.C.E./C.N.F.L./J.A.S.E.C.)
     OR monopoly-with-overlay fallback per _base.py::resolve_owner_from_monopoly_with_overlay
     (ICE TSO threshold ≥138 kV + 7-DSO territorial geofence + ICE monopoly default).
     Costa Rica baseline: 0% owner tagged. Expected post-merge: ~100%.

  2. Voltage cross-validation on matched pairs (>1.5× ratio flagged).

  3. Voltage fill on matched pairs (baseline 100% at 230+138 kV transmission
     tier only — LARGE MULTI-TIER FILL OPPORTUNITY from OSM MV distribution).

  4. Net-new substations with L2/L3 null placeholders (Convention #56).

  5. Line densification: append + dedupe by midpoint 100m + voltage ±20%.

  6. Audit trail with owner_provenance + DSO-alias normalisation flag.

Convention #56 visibly-honest: alias normalisation preserves original
OSM tag in raw_attributes.osm_original_operator for audit trail.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from .osm_overpass import fetch as fetch_osm
from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    now_utc_iso,
    normalise_owner_alias,
)
from ..norway.nve_nettanlegg import _haversine_m

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parent.parent.parent.parent.parent
# Data path uses hyphen (costa-rica/) per intelligence/countries.json slug
SSI_DATA_JSON = REPO_ROOT / "costa-rica" / "ssi-data.json"
GRID_GEO_JSON = REPO_ROOT / "costa-rica" / "grid-geo.json"
VOLTAGE_XCHECK_JSON = REPO_ROOT / "costa-rica" / "v4_23-voltage-cross-validation.json"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_METERS = 500.0
LINE_DEDUPE_MIDPOINT_METERS = 100.0
SOURCE_ID = "CR-C1-osm-overpass"


# ── Utilities ────────────────────────────────────────────────────────────
def _stable_id(payload: str, prefix: str = "CR_v43_") -> str:
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{h}"


def _v42_placeholder_fields() -> dict[str, Any]:
    """Convention #56 null placeholders for L2/L3 fields awaiting rescore."""
    return {
        "climate_trajectory": {},
        "seismic": {},
        "socio_economic": {},
        "graph_topology": {},
        "markov": {},
        "transition": {},
        "components": {},
        "modifiers": {},
        "modifier_impacts": {},
        "modifier_impact": {},
        "modifier_pct": {},
        "R_base_median": None,
        "R_unclipped": None,
        "R_median": None,
        "R_P5": None,
        "R_P95": None,
        "Re_raw": 1.0,
        "Re_norm": 0.0,
        "add_sum": 0.0,
        "mult_product": 1.0,
        "P_critical": None,
        "CI_width": None,
        "component_alert": 0.0,
        "alert_components": [],
        "alert_flag": False,
        "classification": None,
        "confidence_tier": None,
        "fleet_percentile": None,
        "skewness": None,
        "environmental": {},
    }


# ── Substation proximity match ───────────────────────────────────────────
def _build_proximity_grid(existing_subs: list[dict], cell_deg: float = 0.01):
    grid: dict[tuple[int, int], list[tuple[float, float, int]]] = {}
    for idx, s in enumerate(existing_subs):
        lat = s.get("latitude") or s.get("lat")
        lon = s.get("longitude") or s.get("lon")
        if lat is None or lon is None:
            continue
        key = (int(float(lon) / cell_deg), int(float(lat) / cell_deg))
        grid.setdefault(key, []).append((float(lat), float(lon), idx))
    return grid


def _find_nearest_existing(
    ov: SubstationRecord, grid: dict, existing: list[dict],
    cell_deg: float = 0.01, threshold_m: float = PROXIMITY_MATCH_METERS,
) -> tuple[int | None, float]:
    cx = int(ov.longitude / cell_deg)
    cy = int(ov.latitude / cell_deg)
    best_idx: int | None = None
    best_d = float("inf")
    for dcx in (-1, 0, 1):
        for dcy in (-1, 0, 1):
            for (lat, lon, idx) in grid.get((cx + dcx, cy + dcy), []):
                d = _haversine_m(ov.latitude, ov.longitude, lat, lon)
                if d < best_d:
                    best_d = d
                    best_idx = idx
    if best_idx is not None and best_d <= threshold_m:
        return best_idx, best_d
    return None, best_d


# ── Merge substations ────────────────────────────────────────────────────
def merge_substations(
    existing: list[dict],
    osm_subs: list[SubstationRecord],
) -> tuple[int, int, int, list[dict]]:
    """Returns (enriched, voltage_filled, net_new, xcheck_findings)."""
    grid = _build_proximity_grid(existing)
    enriched = 0
    voltage_filled = 0
    net_new = 0
    xcheck_findings: list[dict] = []
    now = now_utc_iso()

    for ov in osm_subs:
        best_idx, dist_m = _find_nearest_existing(ov, grid, existing)
        if best_idx is not None:
            existing_sub = existing[best_idx]
            owner = ov.owner
            owner_provenance = ov.raw_attributes.get("owner_provenance")
            osm_name = ov.operator_station_name
            osm_id = ov.raw_attributes.get("osm_id")
            osm_type = ov.raw_attributes.get("osm_type")

            if owner and not existing_sub.get("owner"):
                existing_sub["owner"] = owner
            if osm_name and not existing_sub.get("operator_station_name"):
                existing_sub["operator_station_name"] = osm_name

            existing_sub["osm_feature_id"] = f"osm_{osm_type}_{osm_id}"

            v43_sources = existing_sub.setdefault("v43_sources", [])
            if SOURCE_ID not in v43_sources:
                v43_sources.append(SOURCE_ID)
            v43_prov = existing_sub.setdefault("v43_provenance", {})
            v43_prov[SOURCE_ID] = {
                "feature_id": ov.feature_id,
                "match_distance_m": round(dist_m, 1),
                "enriched_at_utc": now,
                "owner": owner,
                "owner_provenance": owner_provenance,
                "osm_name": osm_name,
                "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
                "osm_original_operator": ov.raw_attributes.get("osm_original_operator"),
            }

            existing_v = existing_sub.get("voltage_kv")
            osm_v = ov.voltage_kv
            if (not existing_v or existing_v == 0) and osm_v and osm_v > 0:
                existing_sub["voltage_kv"] = osm_v
                v43_prov[SOURCE_ID]["voltage_kv_filled_from_osm"] = osm_v
                voltage_filled += 1

            if (existing_v and existing_v > 0 and osm_v and osm_v > 0):
                ratio = max(existing_v, osm_v) / min(existing_v, osm_v)
                if ratio > 1.5:
                    xcheck_findings.append({
                        "substation_id": existing_sub.get("substation_id") or existing_sub.get("id"),
                        "match_distance_m": round(dist_m, 1),
                        "existing_voltage_kv": existing_v,
                        "osm_voltage_kv": osm_v,
                        "ratio": round(ratio, 2),
                        "osm_feature_id": ov.feature_id,
                        "flag": "voltage_tier_mismatch",
                    })

            enriched += 1

        else:
            new_id = _stable_id(str(ov.raw_attributes.get("osm_id") or ov.feature_id))
            new_sub = {
                "substation_id": new_id,
                "id": new_id,
                "name": ov.operator_station_name or "",
                "operator_station_name": ov.operator_station_name,
                "latitude": ov.latitude,
                "longitude": ov.longitude,
                "lat": ov.latitude,
                "lon": ov.longitude,
                "voltage_kv": ov.voltage_kv or 0.0,
                "owner": ov.owner,
                "osm_feature_id": ov.feature_id,
                "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
                "region": None,  # L2 province spatial join fills at rescore
                "province": None,
                "version": "4.2",
                "v43_sources": [SOURCE_ID],
                "v43_provenance": {SOURCE_ID: {
                    "feature_id": ov.feature_id,
                    "created_at_utc": now,
                    "owner": ov.owner,
                    "owner_provenance": ov.raw_attributes.get("owner_provenance"),
                    "osm_name": ov.operator_station_name,
                    "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
                    "osm_original_operator": ov.raw_attributes.get("osm_original_operator"),
                }},
                **_v42_placeholder_fields(),
            }
            existing.append(new_sub)
            net_new += 1

    return enriched, voltage_filled, net_new, xcheck_findings


# ── Voltage cross-check emission ─────────────────────────────────────────
def emit_voltage_cross_validation(findings: list[dict], total_matched: int) -> None:
    payload = {
        "schema_version": "v4_23-voltage-cross-validation-1",
        "generated_at_utc": now_utc_iso(),
        "source_pair": {
            "existing_source": "OSM voltage= tags (costa-rica/ssi-data.json, prior vintage)",
            "new_source": f"{SOURCE_ID} fresh OSM voltage= tags",
        },
        "methodology": (
            "For each matched substation pair (500 m proximity threshold), compare "
            "existing OSM-derived voltage_kv vs fresh OSM voltage_kv. Flag as "
            "'voltage_tier_mismatch' when ratio exceeds 1.5x."
        ),
        "counts": {
            "matched_pairs_evaluated": total_matched,
            "voltage_tier_mismatches": len(findings),
            "voltage_tier_mismatch_rate_pct": (
                round(100 * len(findings) / max(total_matched, 1), 2)
            ),
        },
        "findings": findings,
    }
    VOLTAGE_XCHECK_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    logger.info(
        "Wrote voltage cross-validation report: %s (%d findings across %d matched pairs)",
        VOLTAGE_XCHECK_JSON, len(findings), total_matched,
    )


# ── Line densification ──────────────────────────────────────────────────
def _existing_line_midpoints(grid_geo: dict) -> list[tuple[float, float, float]]:
    out: list[tuple[float, float, float]] = []
    for line in grid_geo.get("l", []):
        pts = line.get("p") or []
        if len(pts) < 2:
            continue
        lon0, lat0 = pts[0][0], pts[0][1]
        lon1, lat1 = pts[-1][0], pts[-1][1]
        mid_lat = (lat0 + lat1) / 2.0
        mid_lon = (lon0 + lon1) / 2.0
        kv = float(line.get("kv") or 0.0)
        out.append((mid_lat, mid_lon, kv))
    return out


def _line_would_dedupe(
    osm_mid_lat: float, osm_mid_lon: float, osm_kv: float,
    existing_mids: list[tuple[float, float, float]],
    threshold_m: float = LINE_DEDUPE_MIDPOINT_METERS,
    voltage_tier_tolerance: float = 0.20,
) -> bool:
    for (elat, elon, ekv) in existing_mids:
        d = _haversine_m(osm_mid_lat, osm_mid_lon, elat, elon)
        if d <= threshold_m:
            if ekv == 0 and osm_kv == 0:
                return True
            if ekv > 0 and osm_kv > 0:
                ratio = max(ekv, osm_kv) / min(ekv, osm_kv)
                if ratio <= (1.0 + voltage_tier_tolerance):
                    return True
    return False


def merge_lines(
    grid_geo: dict,
    osm_lines: list[TransmissionLineRecord],
) -> tuple[int, int]:
    existing_mids = _existing_line_midpoints(grid_geo)
    l_array = grid_geo.setdefault("l", [])
    appended = 0
    deduped = 0
    now = now_utc_iso()

    for ln in osm_lines:
        coords_multi = ln.coordinates_multilinestring
        if not coords_multi or not coords_multi[0]:
            continue
        coords = coords_multi[0]
        if len(coords) < 2:
            continue
        lon0, lat0 = coords[0][0], coords[0][1]
        lon1, lat1 = coords[-1][0], coords[-1][1]
        mid_lat = (lat0 + lat1) / 2.0
        mid_lon = (lon0 + lon1) / 2.0
        kv = ln.voltage_kv or 0.0

        if _line_would_dedupe(mid_lat, mid_lon, kv, existing_mids):
            deduped += 1
            continue

        new_id = _stable_id(str(ln.raw_attributes.get("osm_id") or ln.feature_id), prefix="CR_v43_l_")
        new_line = {
            "i": new_id,
            "p": coords,
            "kv": kv,
            "ss": None,
            "se": None,
            "src": SOURCE_ID,
            "osm_id": ln.raw_attributes.get("osm_id"),
            "osm_line_class": ln.raw_attributes.get("osm_power_class"),
            "created_at_utc": now,
        }
        l_array.append(new_line)
        existing_mids.append((mid_lat, mid_lon, kv))
        appended += 1

    return appended, deduped


# ── Main entry ───────────────────────────────────────────────────────────
def main(*, dry_run: bool = False, skip_lines: bool = False) -> dict:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Fetching OSM Costa Rica (subs + lines one-shot; single-query pattern)...")
    result = fetch_osm(apply_bounds=True, ingest_lines=not skip_lines)
    logger.info(
        "OSM ingestion: %d substations + %d lines + SHA-256 %s",
        len(result.substations), len(result.transmission_lines), result.raw_sha256,
    )

    logger.info("Loading %s ...", SSI_DATA_JSON)
    existing_ssi = json.loads(SSI_DATA_JSON.read_text())
    if isinstance(existing_ssi, dict) and "substations" in existing_ssi:
        existing_subs = existing_ssi["substations"]
        wrap_as = "dict_with_key"
    elif isinstance(existing_ssi, list):
        existing_subs = existing_ssi
        wrap_as = "list"
    else:
        existing_subs = list(existing_ssi.values())
        wrap_as = "dict_keyed_by_id"
    logger.info("  existing: %d substations", len(existing_subs))

    logger.info("Loading %s ...", GRID_GEO_JSON)
    grid_geo = json.loads(GRID_GEO_JSON.read_text())
    logger.info("  existing: %d lines", len(grid_geo.get("l", [])))

    enriched, voltage_filled, net_new, xcheck = merge_substations(
        existing_subs, result.substations
    )
    logger.info(
        "Substation merge: %d enriched + %d voltage-filled + %d net-new + %d xcheck findings",
        enriched, voltage_filled, net_new, len(xcheck),
    )

    if skip_lines:
        appended_lines, deduped_lines = 0, 0
    else:
        appended_lines, deduped_lines = merge_lines(grid_geo, result.transmission_lines)
        logger.info(
            "Line merge: %d appended + %d deduped (existing tier match)",
            appended_lines, deduped_lines,
        )

    if not dry_run:
        if wrap_as == "dict_with_key":
            existing_ssi["substations"] = existing_subs
            SSI_DATA_JSON.write_text(json.dumps(existing_ssi, ensure_ascii=False))
        elif wrap_as == "list":
            SSI_DATA_JSON.write_text(json.dumps(existing_subs, ensure_ascii=False))
        else:
            new_dict = {s.get("substation_id") or s.get("id"): s for s in existing_subs}
            SSI_DATA_JSON.write_text(json.dumps(new_dict, ensure_ascii=False))
        logger.info(
            "Wrote %s (%.1f MB, %d substations)",
            SSI_DATA_JSON,
            SSI_DATA_JSON.stat().st_size / (1024 * 1024),
            len(existing_subs),
        )

        if not skip_lines and appended_lines > 0:
            GRID_GEO_JSON.write_text(json.dumps(grid_geo, ensure_ascii=False))
            logger.info(
                "Wrote %s (%.1f MB, %d lines)",
                GRID_GEO_JSON,
                GRID_GEO_JSON.stat().st_size / (1024 * 1024),
                len(grid_geo.get("l", [])),
            )

        emit_voltage_cross_validation(xcheck, enriched)

    return {
        "enriched": enriched,
        "voltage_filled": voltage_filled,
        "net_new_substations": net_new,
        "voltage_xcheck_findings": len(xcheck),
        "final_substation_count": len(existing_subs),
        "lines_appended": appended_lines,
        "lines_deduped": deduped_lines,
        "final_line_count": len(grid_geo.get("l", [])),
        "raw_sha256": result.raw_sha256,
        "raw_bytes_fetched": result.raw_bytes_fetched,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Costa Rica v4.23 federation merger")
    parser.add_argument("--dry-run", action="store_true", help="Do not write output files")
    parser.add_argument("--skip-lines", action="store_true", help="Skip line densification")
    args = parser.parse_args()

    stats = main(dry_run=args.dry_run, skip_lines=args.skip_lines)
    print()
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
