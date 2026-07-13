"""
SSI Pipeline — Austria v4.23 federation merger.

Merges OSM Overpass L1 ingestion output into austria/ssi-data.json + austria/grid-geo.json.

Merger operations (Option A per austria/v4_23-ingestion-audit-austria-delta.yaml):

  1. Owner-enrichment on matched pairs (500 m Discipline #41 threshold):
     existing substation gains: owner (DIRECT OSM operator= tag propagation),
     operator_station_name, osm_feature_id, v43_sources, v43_provenance dict.
     Austria has BEST-IN-COHORT OSM operator tagging (77.2% directly tagged
     vs Mexico 16.6%, Norway ~30% pre-NVE).  NO monopoly fallback rule —
     Austrian market is FRAGMENTED across 9+ distinct utilities (APG TSO +
     Wiener Netze + 7 Bundesland DSOs + ÖBB railway).

  2. Voltage cross-validation on matched pairs:
     Compare existing OSM-derived voltage_kv vs fresh OSM voltage_kv.  Flag
     >1.5× ratio discrepancies as data-quality findings written to
     austria/v4_23-voltage-cross-validation.json.

  3. Voltage fill on matched pairs where existing has NO voltage:
     OSM voltage_kv fills into existing sub.

  4. Net-new substation ingestion:
     OSM substations with no existing match within 500 m are added to
     austria/ssi-data.json with L2/L3 fields set to null placeholders per
     Convention #56 visibly-honest degradation.

  5. Line densification (Austria goes ONE-SHOT — Mexico deferred to Step 5b):
     All OSM lines are appended to austria/grid-geo.json's `l` array in the
     compact SSI Index schema ({i, p, kv, ss, se}).  A dedupe pass removes
     lines whose midpoint sits within 100m of an existing line with the same
     voltage tier.

  6. Audit trail:
     Every enriched substation carries v43_sources = ["AT-C1-osm-overpass"] +
     v43_provenance dict with feature_id + owner_provenance class + tag_normalisation
     details.  Every net-new line carries {source_id, osm_way_id, voltage_kv,
     osm_line_class}.

Convention #46 asset-class vs portfolio identity: N/A (single-country canonical).
Convention #56 visibly-honest degradation: null placeholders on new subs; owner=None
  preserved for ~23% untagged tail (do NOT fabricate default — market is fragmented).
Convention #60 non-commercial provenance: OSM (ODbL) only in Phase 1.  ENTSO-E
  Transparency Platform queued as Phase 2 supplement.
Convention #64 strict per-country resolution: never writes outside austria/*.json.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .osm_overpass import fetch as fetch_osm
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
SSI_DATA_JSON = REPO_ROOT / "austria" / "ssi-data.json"
GRID_GEO_JSON = REPO_ROOT / "austria" / "grid-geo.json"
VOLTAGE_XCHECK_JSON = REPO_ROOT / "austria" / "v4_23-voltage-cross-validation.json"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_METERS = 500.0          # Discipline #41 substation-line proximity
LINE_DEDUPE_MIDPOINT_METERS = 100.0     # midpoint-based line dedupe threshold
SOURCE_ID = "AT-C1-osm-overpass"


# ── Utilities ────────────────────────────────────────────────────────────
def _stable_id(payload: str, prefix: str = "AT_v43_") -> str:
    """SHA-1 over payload → 12-char hex, prefixed."""
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{h}"


def _line_midpoint(coords_multi: list[list[list[float]]]) -> tuple[float, float] | None:
    """Compute midpoint of first sub-line (start + end / 2).  [lon,lat] convention."""
    if not coords_multi or not coords_multi[0]:
        return None
    first = coords_multi[0]
    if len(first) < 2:
        return None
    lon0, lat0 = first[0][0], first[0][1]
    lon1, lat1 = first[-1][0], first[-1][1]
    return ((lat0 + lat1) / 2.0, (lon0 + lon1) / 2.0)


def _v42_placeholder_fields() -> dict[str, Any]:
    """Convention #56 null placeholders for L2/L3 fields awaiting rescore.

    Uses empty dicts for dict-typed fields (Canada Priority 1 Stage 3.5b
    lesson learned + Norway Priority 2 lesson learned + Mexico Priority 3
    lesson learned — None crashed the fleet-floor stage; {} degrades cleanly).
    """
    return {
        # L2 climate
        "climate_trajectory": {},
        # L2 seismic (dict — canvas fleet-floor expects .get())
        "seismic": {},
        # L2 socio
        "socio_economic": {},
        # L3 topology
        "graph_topology": {},
        "markov": {},
        "transition": {},
        # L3 modifiers
        "components": {},
        "modifiers": {},
        "modifier_impacts": {},
        "modifier_impact": {},
        "modifier_pct": {},
        # L3 scoring (v4.2 multiplicative neutral + zeroed additive)
        "R_base_median": None,
        "R_unclipped": None,
        "R_median": None,
        "R_P5": None,
        "R_P95": None,
        "Re_raw": 1.0,          # v4.2 master equation multiplicative neutral
        "Re_norm": 0.0,          # 0 additive contribution
        # L3 alerts
        "add_sum": 0.0,
        "mult_product": 1.0,
        "P_critical": None,
        "CI_width": None,
        "component_alert": 0.0,
        # L3 classification
        "alert_components": [],
        "alert_flag": False,
        "classification": None,
        "confidence_tier": None,
        "fleet_percentile": None,
        "skewness": None,
        # L2 environmental
        "environmental": {},
    }


# ── Substation proximity match ───────────────────────────────────────────
def _build_proximity_grid(existing_subs: list[dict], cell_deg: float = 0.01):
    """Grid-index existing substations for O(1) proximity query."""
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
    """Return (index_in_existing_or_None, distance_m)."""
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
    """Apply enrichment + append net-new.

    Returns (enriched, voltage_filled, net_new, xcheck_findings).
    """
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
            # ── Owner enrichment (direct OSM operator= tag propagation) ──
            owner = ov.owner
            owner_provenance = ov.raw_attributes.get("owner_provenance")
            osm_name = ov.operator_station_name
            osm_id = ov.raw_attributes.get("osm_id")
            osm_type = ov.raw_attributes.get("osm_type")

            if owner and not existing_sub.get("owner"):
                existing_sub["owner"] = owner
            if osm_name and not existing_sub.get("operator_station_name"):
                existing_sub["operator_station_name"] = osm_name

            # Preserve OSM feature id linkage
            existing_sub["osm_feature_id"] = f"osm_{osm_type}_{osm_id}"

            # ── v43 provenance ──
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
            }

            # ── Voltage fill on empty existing ──
            existing_v = existing_sub.get("voltage_kv")
            osm_v = ov.voltage_kv
            if (not existing_v or existing_v == 0) and osm_v and osm_v > 0:
                existing_sub["voltage_kv"] = osm_v
                v43_prov[SOURCE_ID]["voltage_kv_filled_from_osm"] = osm_v
                voltage_filled += 1

            # ── Voltage cross-validation ──
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
            # ── Net-new substation ──
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
                "region": None,           # bundesland — L2 spatial join fills at rescore
                "bundesland": None,
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


# ── Voltage cross-check emission ─────────────────────────────────────────
def emit_voltage_cross_validation(findings: list[dict], total_matched: int) -> None:
    payload = {
        "schema_version": "v4_23-voltage-cross-validation-1",
        "generated_at_utc": now_utc_iso(),
        "source_pair": {
            "existing_source": "OSM voltage= tags (austria/ssi-data.json, prior ingestion vintage)",
            "new_source": f"{SOURCE_ID} fresh OSM voltage= tags",
        },
        "methodology": (
            "For each matched substation pair (500 m proximity threshold), compare "
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
        "Wrote voltage cross-validation report: %s (%d findings across %d matched pairs)",
        VOLTAGE_XCHECK_JSON, len(findings), total_matched,
    )


# ── Line densification ──────────────────────────────────────────────────
def _existing_line_midpoints(grid_geo: dict) -> list[tuple[float, float, float]]:
    """Extract (mid_lat, mid_lon, voltage_kv) tuples from existing grid-geo lines."""
    out: list[tuple[float, float, float]] = []
    for line in grid_geo.get("l", []):
        # SSI-native compact schema: line has 'p' = polyline [[lon,lat],...]
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
    """Return True if this OSM line duplicates an existing line (within 100m + same tier)."""
    for (elat, elon, ekv) in existing_mids:
        d = _haversine_m(osm_mid_lat, osm_mid_lon, elat, elon)
        if d <= threshold_m:
            # Same voltage tier? (Both zero, or within ±20% relative)
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
    """Append net-new lines to grid-geo.json.  Returns (appended, deduped)."""
    existing_mids = _existing_line_midpoints(grid_geo)
    l_array = grid_geo.setdefault("l", [])
    appended = 0
    deduped = 0
    now = now_utc_iso()

    for ln in osm_lines:
        # OSM line coordinates as [[lon,lat],...]
        coords = ln.polyline
        if not coords or len(coords) < 2:
            continue
        lon0, lat0 = coords[0][0], coords[0][1]
        lon1, lat1 = coords[-1][0], coords[-1][1]
        mid_lat = (lat0 + lat1) / 2.0
        mid_lon = (lon0 + lon1) / 2.0
        kv = ln.voltage_kv or 0.0

        if _line_would_dedupe(mid_lat, mid_lon, kv, existing_mids):
            deduped += 1
            continue

        new_id = _stable_id(str(ln.raw_attributes.get("osm_id") or ln.feature_id), prefix="AT_v43_l_")
        new_line = {
            "i": new_id,
            "p": coords,
            "kv": kv,
            "ss": None,   # start-substation stable-id — L3 topology fills at rescore
            "se": None,   # end-substation stable-id
            "src": SOURCE_ID,
            "osm_id": ln.raw_attributes.get("osm_id"),
            "osm_line_class": ln.raw_attributes.get("osm_power_class"),
            "created_at_utc": now,
        }
        l_array.append(new_line)
        # Extend the midpoint cache so subsequent OSM lines dedupe against fresh appends
        existing_mids.append((mid_lat, mid_lon, kv))
        appended += 1

    return appended, deduped


# ── Main entry ───────────────────────────────────────────────────────────
def main(*, dry_run: bool = False, skip_lines: bool = False, max_line_quadrants: int | None = None) -> dict:
    """Execute Option A merge: subs + lines one-shot from fresh OSM fetch."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Fetching OSM Austria (subs + lines one-shot)...")
    result = fetch_osm(
        apply_bounds=True,
        ingest_lines=not skip_lines,
        max_line_quadrants=max_line_quadrants,
    )
    logger.info(
        "OSM ingestion: %d substations + %d lines + SHA-256 %s",
        len(result.substations), len(result.transmission_lines), result.raw_sha256,
    )

    # ── Load existing state ──
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

    # ── Merge substations ──
    enriched, voltage_filled, net_new, xcheck = merge_substations(
        existing_subs, result.substations
    )
    logger.info(
        "Substation merge: %d enriched + %d voltage-filled + %d net-new + %d xcheck findings",
        enriched, voltage_filled, net_new, len(xcheck),
    )

    # ── Merge lines ──
    if skip_lines:
        appended_lines, deduped_lines = 0, 0
        logger.info("Line merge SKIPPED per --skip-lines flag")
    else:
        appended_lines, deduped_lines = merge_lines(grid_geo, result.transmission_lines)
        logger.info(
            "Line merge: %d appended + %d deduped (existing tier match)",
            appended_lines, deduped_lines,
        )

    # ── Write outputs ──
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
    parser = argparse.ArgumentParser(description="Austria v4.23 federation merger (subs + lines one-shot)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write output files")
    parser.add_argument("--skip-lines", action="store_true", help="Skip line densification (subs only)")
    parser.add_argument("--max-line-quadrants", type=int, default=None,
                        help="Limit number of bbox quadrants for lines (debug/probe use)")
    args = parser.parse_args()

    stats = main(
        dry_run=args.dry_run,
        skip_lines=args.skip_lines,
        max_line_quadrants=args.max_line_quadrants,
    )
    print()
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
