"""
SSI Pipeline — Greenland v4.23 federation merger.

Merges OSM Overpass L1 ingestion output into greenland/ssi-data.json + greenland/grid-geo.json.

Merger operations (Option A — subs + lines one-shot):

  1. Owner-enrichment on matched pairs (500 m Discipline #41 threshold):
     Existing substation gains owner (via PURE MONOPOLY fallback rule for
     100% of untagged tail — Nukissiorfiit is the SOLE utility), name,
     v43_sources, v43_provenance dict with owner_provenance class label.

  2. Voltage cross-validation on matched pairs.

  3. Voltage fill on matched pairs where existing has NO voltage.

  4. Net-new substation ingestion (small — Step 2 anchor predicts ~5-10 net-new).

  5. Line densification (MAY BE NEGATIVE — baseline has 125 lines vs OSM 103-112).
     Any OSM line whose midpoint doesn't match an existing line within 100m +
     voltage tier is appended.  Realistic delta ~0-20 net-new lines.

  6. Audit trail: every enriched substation carries v43_sources = ["GL-C1-osm-overpass"]
     + v43_provenance dict with feature_id + owner_provenance class + Nukissiorfiit
     fallback flag where applicable.

Convention #46: N/A (single-country canonical).
Convention #56 visibly-honest degradation: null placeholders on net-new subs;
  owner=Nukissiorfiit on untagged (100% confidence via PURE MONOPOLY rule);
  voltage stays None on untagged (do NOT fabricate).
Convention #60 non-commercial provenance: OSM (ODbL) only in Phase 1.
Convention #64 strict per-country resolution: writes only to greenland/*.json.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from .osm_overpass import fetch as fetch_osm, NUKISSIORFIIT_CANONICAL_NAME
from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    now_utc_iso,
)
from ..norway.nve_nettanlegg import _haversine_m

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parent.parent.parent.parent.parent
SSI_DATA_JSON = REPO_ROOT / "greenland" / "ssi-data.json"
GRID_GEO_JSON = REPO_ROOT / "greenland" / "grid-geo.json"
VOLTAGE_XCHECK_JSON = REPO_ROOT / "greenland" / "v4_23-voltage-cross-validation.json"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_METERS = 500.0
LINE_DEDUPE_MIDPOINT_METERS = 100.0
SOURCE_ID = "GL-C1-osm-overpass"


# ── Utilities ────────────────────────────────────────────────────────────
def _stable_id(payload: str, prefix: str = "GL_v43_") -> str:
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{h}"


def _v42_placeholder_fields() -> dict[str, Any]:
    """Convention #56 null placeholders for L2/L3 fields awaiting rescore.

    Dict-typed fields default to {} not None (Canada Priority 1 Stage 3.5b
    + Norway Priority 2 + Mexico Priority 3 + Austria Priority 4 lesson
    learned — None crashes the fleet-floor stage).
    """
    return {
        "climate_trajectory": {}, "seismic": {}, "socio_economic": {},
        "graph_topology": {}, "markov": {}, "transition": {},
        "components": {}, "modifiers": {}, "modifier_impacts": {},
        "modifier_impact": {}, "modifier_pct": {},
        "R_base_median": None, "R_unclipped": None, "R_median": None,
        "R_P5": None, "R_P95": None,
        "Re_raw": 1.0, "Re_norm": 0.0,           # v4.2 master equation neutral defaults
        "add_sum": 0.0, "mult_product": 1.0,
        "P_critical": None, "CI_width": None, "component_alert": 0.0,
        "alert_components": [], "alert_flag": False,
        "classification": None, "confidence_tier": None,
        "fleet_percentile": None, "skewness": None,
        "environmental": {},
    }


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


def merge_substations(
    existing: list[dict],
    osm_subs: list[SubstationRecord],
) -> tuple[int, int, int, list[dict]]:
    """Apply enrichment + append net-new.  Returns (enriched, voltage_filled, net_new, xcheck)."""
    grid = _build_proximity_grid(existing)
    enriched = 0
    voltage_filled = 0
    net_new = 0
    xcheck_findings: list[dict] = []
    now = now_utc_iso()

    for ov in osm_subs:
        best_idx, dist_m = _find_nearest_existing(ov, grid, existing)
        if best_idx is not None:
            ex = existing[best_idx]
            owner = ov.owner
            owner_prov = ov.raw_attributes.get("owner_provenance")
            osm_name = ov.operator_station_name
            osm_id = ov.raw_attributes.get("osm_id")
            osm_type = ov.raw_attributes.get("osm_type")

            if owner and not ex.get("owner"):
                ex["owner"] = owner
            if osm_name and not ex.get("operator_station_name"):
                ex["operator_station_name"] = osm_name
            ex["osm_feature_id"] = f"osm_{osm_type}_{osm_id}"

            v43_sources = ex.setdefault("v43_sources", [])
            if SOURCE_ID not in v43_sources:
                v43_sources.append(SOURCE_ID)
            v43_prov = ex.setdefault("v43_provenance", {})
            v43_prov[SOURCE_ID] = {
                "feature_id": ov.feature_id,
                "match_distance_m": round(dist_m, 1),
                "enriched_at_utc": now,
                "owner": owner,
                "owner_provenance": owner_prov,
                "osm_name": osm_name,
                "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
            }

            ex_v = ex.get("voltage_kv")
            osm_v = ov.voltage_kv
            if (not ex_v or ex_v == 0) and osm_v and osm_v > 0:
                ex["voltage_kv"] = osm_v
                v43_prov[SOURCE_ID]["voltage_kv_filled_from_osm"] = osm_v
                voltage_filled += 1

            if ex_v and ex_v > 0 and osm_v and osm_v > 0:
                ratio = max(ex_v, osm_v) / min(ex_v, osm_v)
                if ratio > 1.5:
                    xcheck_findings.append({
                        "substation_id": ex.get("substation_id") or ex.get("id"),
                        "match_distance_m": round(dist_m, 1),
                        "existing_voltage_kv": ex_v,
                        "osm_voltage_kv": osm_v,
                        "ratio": round(ratio, 2),
                        "osm_feature_id": ov.feature_id,
                        "flag": "voltage_tier_mismatch",
                    })

            enriched += 1
        else:
            new_id = _stable_id(str(ov.raw_attributes.get("osm_id") or ov.feature_id))
            new_sub = {
                "substation_id": new_id, "id": new_id,
                "name": ov.operator_station_name or "",
                "operator_station_name": ov.operator_station_name,
                "latitude": ov.latitude, "longitude": ov.longitude,
                "lat": ov.latitude, "lon": ov.longitude,
                "voltage_kv": ov.voltage_kv or 0.0,
                "owner": ov.owner,
                "osm_feature_id": ov.feature_id,
                "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
                "region": None, "kommune": None,
                "version": "4.2",
                "v43_sources": [SOURCE_ID],
                "v43_provenance": {SOURCE_ID: {
                    "feature_id": ov.feature_id,
                    "created_at_utc": now,
                    "owner": ov.owner,
                    "owner_provenance": ov.raw_attributes.get("owner_provenance"),
                    "osm_name": ov.operator_station_name,
                    "osm_substation_subtype": ov.raw_attributes.get("osm_substation_subtype"),
                }},
                **_v42_placeholder_fields(),
            }
            existing.append(new_sub)
            net_new += 1

    return enriched, voltage_filled, net_new, xcheck_findings


def emit_voltage_cross_validation(findings: list[dict], total_matched: int) -> None:
    payload = {
        "schema_version": "v4_23-voltage-cross-validation-1",
        "generated_at_utc": now_utc_iso(),
        "source_pair": {
            "existing_source": "OSM voltage= tags (greenland/ssi-data.json, prior vintage)",
            "new_source": f"{SOURCE_ID} fresh OSM voltage= tags",
        },
        "methodology": (
            "For each matched substation pair (500m proximity threshold), compare "
            "existing OSM-derived voltage_kv vs fresh OSM voltage_kv from L1 connector. "
            "Flag as 'voltage_tier_mismatch' when the ratio exceeds 1.5x."
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
        "Wrote voltage xcheck: %s (%d findings across %d matched pairs)",
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
        out.append(((lat0 + lat1) / 2.0, (lon0 + lon1) / 2.0, float(line.get("kv") or 0.0)))
    return out


def _line_would_dedupe(
    m_lat: float, m_lon: float, m_kv: float,
    existing_mids: list[tuple[float, float, float]],
    threshold_m: float = LINE_DEDUPE_MIDPOINT_METERS,
    tier_tolerance: float = 0.20,
) -> bool:
    for (elat, elon, ekv) in existing_mids:
        d = _haversine_m(m_lat, m_lon, elat, elon)
        if d <= threshold_m:
            if ekv == 0 and m_kv == 0:
                return True
            if ekv > 0 and m_kv > 0:
                if max(ekv, m_kv) / min(ekv, m_kv) <= (1.0 + tier_tolerance):
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
        m_lat = (lat0 + lat1) / 2.0
        m_lon = (lon0 + lon1) / 2.0
        kv = ln.voltage_kv or 0.0

        if _line_would_dedupe(m_lat, m_lon, kv, existing_mids):
            deduped += 1
            continue

        new_id = _stable_id(str(ln.raw_attributes.get("osm_id") or ln.feature_id), prefix="GL_v43_l_")
        l_array.append({
            "i": new_id,
            "p": coords,
            "kv": kv,
            "ss": None, "se": None,
            "src": SOURCE_ID,
            "osm_id": ln.raw_attributes.get("osm_id"),
            "osm_line_class": ln.raw_attributes.get("osm_power_class"),
            "op": ln.owner,
            "created_at_utc": now,
        })
        existing_mids.append((m_lat, m_lon, kv))
        appended += 1

    return appended, deduped


# ── Main entry ───────────────────────────────────────────────────────────
def main(*, dry_run: bool = False, skip_lines: bool = False) -> dict:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Fetching OSM Greenland (subs + lines one-shot)...")
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
        "Substation merge: %d enriched + %d voltage-filled + %d net-new + %d xcheck",
        enriched, voltage_filled, net_new, len(xcheck),
    )

    if skip_lines:
        appended_lines, deduped_lines = 0, 0
        logger.info("Line merge SKIPPED per --skip-lines")
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
            "Wrote %s (%.2f MB, %d substations)",
            SSI_DATA_JSON,
            SSI_DATA_JSON.stat().st_size / (1024 * 1024),
            len(existing_subs),
        )
        if not skip_lines and appended_lines > 0:
            GRID_GEO_JSON.write_text(json.dumps(grid_geo, ensure_ascii=False))
            logger.info(
                "Wrote %s (%.2f MB, %d lines)",
                GRID_GEO_JSON,
                GRID_GEO_JSON.stat().st_size / (1024 * 1024),
                len(grid_geo.get("l", [])),
            )
        emit_voltage_cross_validation(xcheck, enriched)

    # ── Provenance stats ──
    monopoly_fallback_subs = sum(
        1 for s in result.substations
        if s.raw_attributes.get("owner_provenance") == "nukissiorfiit_monopoly_fallback"
    )
    monopoly_fallback_lines = sum(
        1 for l in result.transmission_lines
        if l.raw_attributes.get("owner_provenance") == "nukissiorfiit_monopoly_fallback"
    )

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
        "monopoly_fallback_subs": monopoly_fallback_subs,
        "monopoly_fallback_lines": monopoly_fallback_lines,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Greenland v4.23 federation merger")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-lines", action="store_true")
    args = parser.parse_args()

    stats = main(dry_run=args.dry_run, skip_lines=args.skip_lines)
    print()
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
