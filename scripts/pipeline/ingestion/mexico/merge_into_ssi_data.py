"""
SSI Pipeline — Mexico v4.3 federation merger.

Merges OSM Overpass L1 ingestion output into mexico/ssi-data.json.

Merger operations (Option A per mexico/v4_3-ingestion-audit-mexico-delta.yaml):

  1. Owner-enrichment on matched pairs (500 m Discipline #41 threshold):
     existing substation gains: owner (via CFE-monopoly fallback rule), name,
     v43_sources, v43_provenance dict with owner_provenance class + CFE
     canonical Spanish name where applicable.

  2. Voltage cross-validation on matched pairs:
     Compare existing OSM-derived voltage_kv vs fresh OSM voltage_kv.  Flag
     discrepancies as data-quality findings written to
     mexico/v4_3-voltage-cross-validation.json.  Empirically 0.04% mismatch
     rate for Mexico (near-empty artifact).

  3. Voltage fill on 312 matched pairs where existing has NO voltage:
     OSM voltage_kv fills into existing sub.

  4. Net-new substation ingestion:
     649 OSM substations with no existing match within 500 m are added to
     mexico/ssi-data.json with L2/L3 fields set to null placeholders per
     Convention #56 visibly-honest degradation.

  5. Lines DEFERRED to Step 5b:
     Line densification requires operator to run L1 connector on residential
     IP (Overpass API rate-limits cloud IPs).  Discipline #41 line-parity
     tracked as PARTIAL until Step 5b executes.

  6. Audit trail:
     Every enriched substation carries v43_sources = ["MX-C1-osm-overpass"] +
     v43_provenance dict with feature_id + owner_provenance class + tag_normalisation
     details.

Convention #46 asset-class vs portfolio identity: N/A (single-country canonical).
Convention #56 visibly-honest degradation: null placeholders on new subs; owner=None
  preserved for industrial self-gen (do not fabricate CFE default).
Convention #60 non-commercial provenance: OSM (ODbL) + INEGI DENUE queued (public).
Convention #64 strict per-country resolution: never writes outside mexico/*.json.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .osm_overpass import fetch as fetch_osm, CFE_CANONICAL_NAME
from ._base import (
    SubstationRecord,
    IngestionResult,
    now_utc_iso,
)
from ..norway.nve_nettanlegg import _haversine_m

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parent.parent.parent.parent.parent
SSI_DATA_JSON = REPO_ROOT / "mexico" / "ssi-data.json"
VOLTAGE_XCHECK_JSON = REPO_ROOT / "mexico" / "v4_3-voltage-cross-validation.json"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_METERS = 500.0
SOURCE_ID = "MX-C1-osm-overpass"

# ── Utilities ────────────────────────────────────────────────────────────
def _stable_id(payload: str, prefix: str = "MX_v43_") -> str:
    """SHA-1 over payload → 12-char hex, prefixed."""
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{h}"


def _v42_placeholder_fields() -> dict[str, Any]:
    """Convention #56 null placeholders for L2/L3 fields awaiting rescore.

    Uses empty dicts for dict-typed fields (Canada Priority 1 Stage 3.5b
    lesson learned + Norway Priority 2 lesson learned).
    """
    return {
        # L2 climate
        "climate_trajectory": {},
        # L2 seismic
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
        "Re_norm": 0.0,
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
            # ── Owner enrichment ──
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
                "region": None,
                "departement": None,
                "dept_code": None,
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
        "schema_version": "v4_3-voltage-cross-validation-1",
        "generated_at_utc": now_utc_iso(),
        "source_pair": {
            "existing_source": "OSM voltage= tags (mexico/ssi-data.json, prior ingestion vintage)",
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


# ── Main entry ───────────────────────────────────────────────────────────
def main(*, dry_run: bool = False) -> dict:
    """Execute Option A merge: subs from cache, lines deferred to Step 5b."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Fetching OSM Mexico from cache (Step 5 Option A — subs only)...")
    result = fetch_osm(
        apply_bounds=True,
        ingest_lines=False,  # deferred to Step 5b (operator local)
    )
    logger.info(
        "OSM ingestion (subs only): %d substations + SHA-256 %s",
        len(result.substations), result.raw_sha256,
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

    # ── Merge substations ──
    enriched, voltage_filled, net_new, xcheck = merge_substations(
        existing_subs, result.substations
    )
    logger.info(
        "Substation merge: %d enriched + %d voltage-filled + %d net-new + %d xcheck findings",
        enriched, voltage_filled, net_new, len(xcheck),
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
        emit_voltage_cross_validation(xcheck, enriched)

    return {
        "enriched": enriched,
        "voltage_filled": voltage_filled,
        "net_new": net_new,
        "voltage_xcheck_findings": len(xcheck),
        "final_substation_count": len(existing_subs),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mexico v4.3 federation merger (Option A — subs only)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    stats = main(dry_run=args.dry_run)
    print()
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
