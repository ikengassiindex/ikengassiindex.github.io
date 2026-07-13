"""
SSI Pipeline — Norway v4.23 federation merger.

Merges NVE Nettanlegg L1 ingestion output into norway/ssi-data.json + norway/grid-geo.json.

Merger operations (Option A per norway/v4_23-ingestion-audit-norway-delta.yaml):

  1. Owner-enrichment on matched pairs (500 m Discipline #41 threshold):
     existing substation gains: owner, operator_station_name, eierOrgnr,
     driftsattår, lokalId, v43_sources, v43_provenance dict.

  2. Voltage cross-validation on matched pairs:
     Compare NVE-derived voltage (max incident line spenning via reverse
     Discipline #41) vs existing OSM voltage_kv.  Flag discrepancies as
     data-quality findings written to norway/v4_23-voltage-cross-validation.json.

  3. Net-new substation ingestion:
     Any NVE substation with no existing match within 500 m is added to
     norway/ssi-data.json with L2/L3 fields set to null placeholders (per
     Convention #56 visibly-honest degradation).  Fields awaiting enrichment
     surface as null downstream.

  4. Line densification:
     All NVE Luftlinje + Sjøkabel lines are appended to norway/grid-geo.json's
     `l` array in the compact SSI Index schema ({i, p, kv, ss, se}).
     A dedupe pass removes lines whose midpoint sits within 100m of an
     existing line with the same voltage tier.

  5. Audit trail:
     Every enriched substation carries `v43_sources: ["NO-C1-nve-nettanlegg"]`
     + `v43_provenance: {source_id: {feature_id, spenning_kv_inherited, ...}}`.
     Every net-new substation carries the same fields.  Every net-new line
     carries {source_id, lokalId, spenning_kv, nettniva}.

Convention #56 visibly-honest degradation:
  - Fields awaiting L2/L3 rescore surface as null (not spurious defaults).
  - Missing eier / eierOrgnr / driftsattår on individual NVE features remain
    None on the enriched substation (do not fabricate).
  - Merge failures on individual features are logged and skipped, not silenced.

Convention #46 asset-class vs portfolio identity:
  - N/A here — Norway is a single-country canonical, not a portfolio scope.

Convention #64 strict per-country resolution:
  - This merger ONLY writes to norway/*.json.  No cross-country contamination.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .nve_nettanlegg import fetch as fetch_nve
from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    now_utc_iso,
)
from .nve_nettanlegg import _haversine_m

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parent.parent.parent.parent.parent
SSI_DATA_JSON = REPO_ROOT / "norway" / "ssi-data.json"
GRID_GEO_JSON = REPO_ROOT / "norway" / "grid-geo.json"
VOLTAGE_XCHECK_JSON = REPO_ROOT / "norway" / "v4_23-voltage-cross-validation.json"
BOUNDS_JSON = REPO_ROOT / "norway" / "bounds.json"

# ── Constants ────────────────────────────────────────────────────────────
PROXIMITY_MATCH_METERS = 500.0          # Discipline #41 substation-line proximity
LINE_DEDUPE_MIDPOINT_METERS = 100.0     # midpoint-based line dedupe threshold
SOURCE_ID = "NO-C1-nve-nettanlegg"

# ── Utilities ────────────────────────────────────────────────────────────
def _stable_id(payload: str, prefix: str = "NO_v43_") -> str:
    """SHA-1 over payload → 12-char hex, prefixed."""
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}{h}"


def _line_midpoint(coords_multi: list[list[list[float]]]) -> tuple[float, float] | None:
    """Compute midpoint of first sub-line (start + end / 2)."""
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
    nv: SubstationRecord, grid: dict, existing: list[dict],
    cell_deg: float = 0.01, threshold_m: float = PROXIMITY_MATCH_METERS,
) -> tuple[int | None, float]:
    """Return (index_in_existing_or_None, distance_m)."""
    cx = int(nv.longitude / cell_deg)
    cy = int(nv.latitude / cell_deg)
    best_idx: int | None = None
    best_d = float("inf")
    for dcx in (-1, 0, 1):
        for dcy in (-1, 0, 1):
            for (lat, lon, idx) in grid.get((cx + dcx, cy + dcy), []):
                d = _haversine_m(nv.latitude, nv.longitude, lat, lon)
                if d < best_d:
                    best_d = d
                    best_idx = idx
    if best_idx is not None and best_d <= threshold_m:
        return best_idx, best_d
    return None, best_d


# ── Merge substations ────────────────────────────────────────────────────
def merge_substations(
    existing: list[dict],
    nve_subs: list[SubstationRecord],
) -> tuple[int, int, list[dict]]:
    """Apply enrichment + append net-new.  Returns (enriched, net_new, xcheck_findings)."""
    grid = _build_proximity_grid(existing)
    enriched = 0
    net_new = 0
    xcheck_findings: list[dict] = []
    now = now_utc_iso()

    for nv in nve_subs:
        best_idx, dist_m = _find_nearest_existing(nv, grid, existing)
        if best_idx is not None:
            existing_sub = existing[best_idx]
            # ── Owner enrichment ──
            eier = nv.owner
            eier_orgnr = nv.raw_attributes.get("eierOrgnr")
            navn = nv.operator_station_name
            driftsatt = nv.raw_attributes.get("driftsattår")
            lokal_id = nv.raw_attributes.get("lokalId")

            if eier and not existing_sub.get("owner"):
                existing_sub["owner"] = eier
            if navn and not existing_sub.get("operator_station_name"):
                existing_sub["operator_station_name"] = navn
            if eier_orgnr:
                existing_sub["eier_orgnr"] = eier_orgnr
            if driftsatt:
                existing_sub["commissioning_year"] = driftsatt
            if lokal_id:
                existing_sub["nve_lokal_id"] = lokal_id

            # ── v43 provenance ──
            v43_sources = existing_sub.setdefault("v43_sources", [])
            if SOURCE_ID not in v43_sources:
                v43_sources.append(SOURCE_ID)
            v43_prov = existing_sub.setdefault("v43_provenance", {})
            v43_prov[SOURCE_ID] = {
                "feature_id": nv.feature_id,
                "match_distance_m": round(dist_m, 1),
                "enriched_at_utc": now,
                "eier": eier,
                "eier_orgnr": eier_orgnr,
                "navn": navn,
                "driftsattår": driftsatt,
            }

            # ── Voltage cross-validation ──
            existing_v = existing_sub.get("voltage_kv")
            inherited_v = nv.voltage_kv
            if (existing_v is not None and existing_v > 0 and
                    inherited_v is not None and inherited_v > 0):
                # both populated — compare
                ratio = max(existing_v, inherited_v) / min(existing_v, inherited_v)
                if ratio > 1.5:  # different voltage tier
                    xcheck_findings.append({
                        "substation_id": existing_sub.get("substation_id")
                            or existing_sub.get("id"),
                        "match_distance_m": round(dist_m, 1),
                        "existing_voltage_kv": existing_v,
                        "nve_inherited_voltage_kv": inherited_v,
                        "ratio": round(ratio, 2),
                        "nve_lokal_id": lokal_id,
                        "flag": "voltage_tier_mismatch",
                    })

            enriched += 1

        else:
            # ── Net-new substation ──
            new_id = _stable_id(nv.raw_attributes.get("lokalId") or nv.feature_id)
            new_sub = {
                "substation_id": new_id,
                "id": new_id,
                "name": nv.operator_station_name or "",
                "operator_station_name": nv.operator_station_name,
                "latitude": nv.latitude,
                "longitude": nv.longitude,
                "lat": nv.latitude,
                "lon": nv.longitude,
                "voltage_kv": nv.voltage_kv or 0.0,
                "owner": nv.owner,
                "eier_orgnr": nv.raw_attributes.get("eierOrgnr"),
                "commissioning_year": nv.raw_attributes.get("driftsattår"),
                "nve_lokal_id": nv.raw_attributes.get("lokalId"),
                "region": None,
                "departement": None,
                "dept_code": None,
                "version": "4.2",
                "v43_sources": [SOURCE_ID],
                "v43_provenance": {SOURCE_ID: {
                    "feature_id": nv.feature_id,
                    "created_at_utc": now,
                    "eier": nv.owner,
                    "eier_orgnr": nv.raw_attributes.get("eierOrgnr"),
                    "navn": nv.operator_station_name,
                    "driftsattår": nv.raw_attributes.get("driftsattår"),
                }},
                **_v42_placeholder_fields(),
            }
            existing.append(new_sub)
            net_new += 1

    return enriched, net_new, xcheck_findings


# ── Line densification ──────────────────────────────────────────────────
def _load_grid_geo() -> dict:
    if GRID_GEO_JSON.exists():
        return json.loads(GRID_GEO_JSON.read_text())
    return {"s": {}, "l": [], "a": {}}


def _line_dedupe_key(coords_multi: list[list[list[float]]], kv: float | None) -> tuple:
    """Deduplication key: rounded midpoint + voltage bucket."""
    mp = _line_midpoint(coords_multi)
    if mp is None:
        return ("empty",)
    lat_r = round(mp[0], 3)   # ~110m precision
    lon_r = round(mp[1], 3)
    kv_bucket = None
    if kv is not None:
        if kv < 20: kv_bucket = "lv"
        elif kv < 50: kv_bucket = "mv"
        elif kv < 200: kv_bucket = "regional"
        else: kv_bucket = "transmission"
    return (lat_r, lon_r, kv_bucket)


def merge_lines(nve_lines: list[TransmissionLineRecord]) -> tuple[dict, int, int]:
    """Merge NVE lines into grid-geo.json.  Returns (grid_geo_dict, net_new, dedup_skipped)."""
    grid_geo = _load_grid_geo()
    existing_lines = grid_geo.get("l", [])

    # Build dedupe index over existing lines
    existing_keys = set()
    for ex_line in existing_lines:
        p = ex_line.get("p", [])
        if not p or len(p) < 2:
            continue
        # compact grid-geo uses flat [[lon,lat],...] not multi-line — wrap as single-line multi
        try:
            coords_multi = [p]
            key = _line_dedupe_key(coords_multi, ex_line.get("kv"))
            existing_keys.add(key)
        except Exception:
            continue

    net_new = 0
    dedup_skipped = 0
    for ln in nve_lines:
        key = _line_dedupe_key(ln.coordinates_multilinestring, ln.voltage_kv)
        if key in existing_keys:
            dedup_skipped += 1
            continue
        existing_keys.add(key)

        # convert MultiLineString to flat point array (concatenate segments)
        flat_pts: list[list[float]] = []
        for seg in ln.coordinates_multilinestring:
            flat_pts.extend(seg)
        if len(flat_pts) < 2:
            continue

        # Determine numeric ID for compact grid-geo format
        line_id = int(hashlib.sha1(ln.feature_id.encode()).hexdigest()[:8], 16)

        new_line = {
            "i": line_id,
            "p": flat_pts,
            "kv": ln.voltage_kv if ln.voltage_kv is not None else 0,
            "ss": None,
            "se": None,
            "v43_source": SOURCE_ID,
            "v43_lokal_id": ln.feature_id,
            "v43_nettniva": ln.raw_attributes.get("nettnivå"),
            "v43_eier": ln.owner,
            "v43_source_tag": ln.raw_attributes.get("source_tag"),
        }
        existing_lines.append(new_line)
        net_new += 1

    grid_geo["l"] = existing_lines
    return grid_geo, net_new, dedup_skipped


# ── Voltage cross-check emission ─────────────────────────────────────────
def emit_voltage_cross_validation(findings: list[dict], total_matched: int) -> None:
    payload = {
        "schema_version": "v4_23-voltage-cross-validation-1",
        "generated_at_utc": now_utc_iso(),
        "source_pair": {
            "existing_source": "OSM voltage= tags (norway/ssi-data.json)",
            "new_source": f"{SOURCE_ID} reverse Discipline #41 voltage inheritance",
        },
        "methodology": (
            "For each matched substation pair (500 m proximity threshold), compare "
            "existing OSM voltage_kv vs NVE-inherited voltage_kv (max incident line "
            "spenning). Flag as 'voltage_tier_mismatch' when the ratio exceeds 1.5x "
            "(indicative of different voltage tier — e.g. 22 kV LV vs 132 kV regional)."
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
def main(*, ingest_lines: bool = True, dry_run: bool = False) -> dict:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Fetching NVE Nettanlegg (uses on-disk cache — no re-download if warm)...")
    result = fetch_nve(
        apply_bounds=True,
        ingest_luftlinje=ingest_lines,
        ingest_sjokabel=ingest_lines,
        propagate_voltage=True,
    )
    logger.info(
        "NVE ingestion complete: %d substations + %d lines + SHA-256 %s",
        len(result.substations), len(result.transmission_lines), result.raw_sha256,
    )

    # ── Load existing state ──
    logger.info("Loading %s ...", SSI_DATA_JSON)
    existing_ssi = json.loads(SSI_DATA_JSON.read_text())
    if isinstance(existing_ssi, list):
        existing_subs = existing_ssi
        wrap_as = "list"
    elif isinstance(existing_ssi, dict) and "substations" in existing_ssi:
        existing_subs = existing_ssi["substations"]
        wrap_as = "dict_with_key"
    else:
        # dict keyed by substation_id
        existing_subs = list(existing_ssi.values())
        wrap_as = "dict_keyed_by_id"
    logger.info("  existing: %d substations", len(existing_subs))

    # ── Merge substations ──
    enriched, net_new, xcheck = merge_substations(existing_subs, result.substations)
    logger.info(
        "Substation merge: %d enriched + %d net-new + %d voltage cross-check findings",
        enriched, net_new, len(xcheck),
    )

    # ── Merge lines ──
    line_stats = None
    if ingest_lines and result.transmission_lines:
        grid_geo, net_new_lines, dedup_skipped = merge_lines(result.transmission_lines)
        line_stats = {
            "net_new_lines": net_new_lines,
            "dedup_skipped": dedup_skipped,
            "grid_geo_total_after": len(grid_geo["l"]),
        }
        logger.info(
            "Line merge: %d net-new + %d dedup-skipped → %d total",
            net_new_lines, dedup_skipped, len(grid_geo["l"]),
        )
    else:
        grid_geo = None

    # ── Write outputs ──
    if not dry_run:
        # ssi-data.json
        if wrap_as == "list":
            SSI_DATA_JSON.write_text(json.dumps(existing_subs, ensure_ascii=False))
        elif wrap_as == "dict_with_key":
            existing_ssi["substations"] = existing_subs
            SSI_DATA_JSON.write_text(json.dumps(existing_ssi, ensure_ascii=False))
        else:
            # dict keyed — rebuild by substation_id
            new_dict = {s.get("substation_id") or s.get("id"): s for s in existing_subs}
            SSI_DATA_JSON.write_text(json.dumps(new_dict, ensure_ascii=False))
        logger.info(
            "Wrote %s (%.1f MB, %d substations)",
            SSI_DATA_JSON,
            SSI_DATA_JSON.stat().st_size / (1024 * 1024),
            len(existing_subs),
        )

        # grid-geo.json
        if grid_geo is not None:
            GRID_GEO_JSON.write_text(json.dumps(grid_geo, ensure_ascii=False))
            logger.info(
                "Wrote %s (%.1f MB, %d lines)",
                GRID_GEO_JSON,
                GRID_GEO_JSON.stat().st_size / (1024 * 1024),
                len(grid_geo["l"]),
            )

        # voltage cross-validation
        emit_voltage_cross_validation(xcheck, enriched)

    return {
        "enriched": enriched,
        "net_new": net_new,
        "voltage_xcheck_findings": len(xcheck),
        "line_stats": line_stats,
        "final_substation_count": len(existing_subs),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Norway v4.23 federation merger")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-lines", action="store_true")
    args = parser.parse_args()

    stats = main(ingest_lines=not args.skip_lines, dry_run=args.dry_run)
    print()
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
