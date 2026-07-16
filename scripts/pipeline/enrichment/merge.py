"""
SSI Pipeline — Enrichment & Merge Layer
Merges ingested data into ssi-data.json and rescores affected substations.

Pipeline flow:
  1. Load current ssi-data.json for country
  2. Load ingestion results (seismic, climate, socio-economic)
  3. Merge updates into substation records
  4. Rescore affected substations via scoring engine
  5. Recompute fleet and regional summaries
  6. Write updated ssi-data.json
  7. Report ESG readiness changes
"""

import json
import logging
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from ..scoring.engine import (
    score_substation, compute_fleet_summary, compute_regional_summary,
    classify_band, classify_confidence,
)
from ..utils.geo import load_substations
from ..config import REPO_ROOT, ESG_REPORTS

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  MERGE ENGINE
# ═══════════════════════════════════════════════════════════

def merge_and_rescore(country, seismic_results=None, climate_results=None,
                      socio_results=None, rescore=True, dry_run=False):
    """
    Merge ingestion results into ssi-data.json and rescore.

    Args:
        country: Country identifier
        seismic_results: Output from seismic.overlay_seismic_pga()
        climate_results: Output from climate.compute_iri_forward()
        socio_results: Output from socioeconomic.overlay_socioeconomic()
        rescore: If True, run Monte Carlo rescoring (slower but accurate)
        dry_run: If True, compute but don't write to disk

    Returns:
        dict with merge statistics and ESG readiness assessment
    """
    data_path = Path(REPO_ROOT) / country / "ssi-data.json"
    if not data_path.exists():
        raise FileNotFoundError(f"No ssi-data.json at {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    # Class D fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3): guard
    # against flat-list root schema (Latvia + any future country in Phase 1
    # intermediate state per CONVENTION_78_BINDING_EMPIRICAL_AUDIT §4bis.4).
    # Phase 2 pipeline is expected to rewrite with proper wrapper — see line 196.
    if isinstance(data, list):
        logger.info(
            f"Country {country} uses flat-list root schema (Phase 1 intermediate "
            f"state per CONVENTION_78 §4bis.4); wrapping as {{'substations': [...]}}"
        )
        data = {"substations": data}

    raw_subs = data["substations"]

    # Handle compact array format (sub_fields mapping)
    if raw_subs and isinstance(raw_subs[0], list):
        fields = data.get("sub_fields", [])
        if not fields:
            raise ValueError(f"Compact array format but no sub_fields in {data_path}")
        subs = []
        for arr in raw_subs:
            d = {}
            for i, field in enumerate(fields):
                if i < len(arr):
                    d[field] = arr[i]
            if "substation_id" not in d:
                d["substation_id"] = d.get("name", f"sub_{len(subs)}")
            subs.append(d)
        data["_compact_format"] = True
        data["_sub_fields"] = fields
    else:
        subs = raw_subs

    n = len(subs)

    # Build index maps from ingestion results
    seismic_map = _build_index_map(seismic_results) if seismic_results else {}
    climate_map = _build_index_map(climate_results) if climate_results else {}
    socio_map = _build_index_map(socio_results) if socio_results else {}

    stats = {
        "country": country,
        "total_substations": n,
        "seismic_updates": 0,
        "climate_updates": 0,
        "socio_updates": 0,
        "rescored": 0,
        "classification_changes": [],
    }

    updated_subs = []

    for idx, sub in enumerate(subs):
        sid = sub["substation_id"]
        seismic_update = seismic_map.get(idx) or seismic_map.get(sid)
        climate_update = climate_map.get(idx) or climate_map.get(sid)
        socio_update = socio_map.get(idx) or socio_map.get(sid)

        has_seismic = (seismic_update and
                       abs(seismic_update.get("pga_g", 0.03) -
                           sub.get("seismic", {}).get("pga_g", 0.03)) > 0.001)
        has_climate = (climate_update and
                       abs(climate_update.get("I3_trajectory", 1.0) -
                           sub.get("climate_trajectory", {}).get("I3_trajectory", 1.0)) > 0.001)
        has_socio = (socio_update and "V_socio" in socio_update.get("socio_economic", {}))

        if has_seismic:
            stats["seismic_updates"] += 1
        if has_climate:
            stats["climate_updates"] += 1
        if has_socio:
            stats["socio_updates"] += 1

        needs_rescore = has_seismic or has_climate or has_socio

        if needs_rescore and rescore:
            old_class = sub.get("classification", "Medium")

            updated = score_substation(
                sub,
                seismic_update=seismic_update if has_seismic else None,
                climate_update=climate_update if has_climate else None,
                socio_update=socio_update.get("socio_economic") if has_socio else None,
            )
            updated_subs.append(updated)
            stats["rescored"] += 1

            new_class = updated.get("classification", "Medium")
            if old_class != new_class:
                stats["classification_changes"].append({
                    "substation_id": sid,
                    "name": sub.get("name", ""),
                    "old": old_class,
                    "new": new_class,
                    "R_old": sub.get("R_median", 0),
                    "R_new": updated.get("R_median", 0),
                })
        elif needs_rescore:
            # Apply data updates without full rescoring
            updated = _apply_updates_no_rescore(sub, seismic_update, climate_update, socio_update)
            updated_subs.append(updated)
        else:
            updated_subs.append(sub)

    # Recompute fleet and regional summaries
    data["substations"] = updated_subs
    data["fleet_summary"] = compute_fleet_summary(updated_subs)
    data["regions"] = compute_regional_summary(updated_subs)

    # Update metadata
    # Class D fix: Latvia flat-list schema lacks 'meta' wrapper — bootstrap it
    # per Convention #78 §4bis.6 (Phase 2 rewrites file with proper wrapper).
    if "meta" not in data:
        data["meta"] = {}
    data["meta"]["generated"] = datetime.now().strftime("%Y-%m-%d")
    data["meta"]["generator"] = "SSI v4.0.2 Pipeline (automated enrichment)"
    data["meta"]["enrichment_run"] = {
        "timestamp": datetime.now().isoformat(),
        "seismic_updates": stats["seismic_updates"],
        "climate_updates": stats["climate_updates"],
        "socio_updates": stats["socio_updates"],
        "rescored": stats["rescored"],
    }

    # Compute fleet percentiles
    # Classes B/C fix: filter pre-L3 None R_median subs per Convention #56.
    # Substations without R_median get fleet_percentile=None (visibly-honest).
    R_vals = sorted(
        s["R_median"] for s in updated_subs if s.get("R_median") is not None
    )
    for sub in updated_subs:
        if sub.get("R_median") is None:
            sub["fleet_percentile"] = None
            continue
        # Binary search for fleet percentile
        import bisect
        rank = bisect.bisect_left(R_vals, sub["R_median"])
        sub["fleet_percentile"] = round(rank / len(R_vals), 3) if R_vals else None

    # Convert back to compact array format if source used it
    if data.get("_compact_format"):
        fields = data.get("_sub_fields", [])
        compact_subs = []
        for sub in updated_subs:
            arr = []
            for field in fields:
                val = sub.get(field)
                arr.append(val)
            compact_subs.append(arr)
        data["substations"] = compact_subs
        # Clean up internal markers
        data.pop("_compact_format", None)
        data.pop("_sub_fields", None)
    else:
        data["substations"] = updated_subs

    # Write
    if not dry_run:
        with open(data_path, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        logger.info(f"Wrote updated ssi-data.json for {country} ({len(updated_subs)} substations)")
    else:
        logger.info(f"[DRY RUN] Would write {country}/ssi-data.json")

    # ESG readiness assessment
    stats["esg_readiness"] = assess_esg_readiness(updated_subs, country)

    return stats


def _build_index_map(results):
    """Build lookup map from ingestion results (by index and substation_id)."""
    if not results:
        return {}
    m = {}
    for r in results:
        if "index" in r:
            m[r["index"]] = r
        if "substation_id" in r:
            m[r["substation_id"]] = r
    return m


def _apply_updates_no_rescore(sub, seismic_update, climate_update, socio_update):
    """Apply data updates without running Monte Carlo rescoring."""
    updated = deepcopy(sub)

    if seismic_update:
        updated.setdefault("seismic", {})
        if "pga_g" in seismic_update:
            updated["seismic"]["pga_g"] = seismic_update["pga_g"]
        if "zone" in seismic_update:
            updated["seismic"]["zone"] = seismic_update["zone"]

    if climate_update:
        updated["climate_trajectory"] = {
            "I1_trajectory": climate_update.get("I1_trajectory", 1.0),
            "I2_trajectory": climate_update.get("I2_trajectory", 1.0),
            "I3_trajectory": climate_update.get("I3_trajectory", 1.0),
        }

    if socio_update and "socio_economic" in socio_update:
        se = updated.get("socio_economic", {})
        se.update(socio_update["socio_economic"])
        updated["socio_economic"] = se

    return updated


# ═══════════════════════════════════════════════════════════
#  ESG READINESS ASSESSMENT
# ═══════════════════════════════════════════════════════════

def assess_esg_readiness(substations, country):
    """
    Evaluate ESG report readiness based on data completeness.

    For each of the 7 reports (R1-R7 per FC v3 §14 canonical, upgraded
    16 July 2026 R7 workstream), checks whether required fields have
    non-default values across the fleet. Returns READY/PARTIAL/GAP.

    R7 SFDR PAI Infrastructure Disclosure uses Re_normalised as
    documented-proxy per Convention #7 Data-Layer Anchoring. Fresh
    net-new substations post-L1 refresh carry Re_normalised=0.0
    neutral-default per Convention #56 visibly-honest degradation; this
    counts as NOT READY per Convention #78 §4bis.4 two-phase workflow
    discipline (Phase 2 modifier-chain rescore populates Re_normalised
    with actual composite values).
    """
    n = len(substations)
    if n == 0:
        return {}

    readiness = {}

    for report_id, report_def in ESG_REPORTS.items():
        checks = {}
        for field_path in report_def.get("required_fields", []):
            # Navigate nested path (e.g., "seismic.pga_g")
            parts = field_path.split(".")
            non_default = 0
            for sub in substations:
                val = sub
                missing = False
                for p in parts:
                    if isinstance(val, dict):
                        if p not in val:
                            # Convention #56 gate — treat missing field as
                            # NOT populated (fix landed 16 July 2026 R7 workstream
                            # Phase 4a hotfix; previously sub.get(p, {}) returned
                            # empty-dict fallback that passed 'not None' check and
                            # falsely counted as populated).
                            missing = True
                            break
                        val = val[p]
                    else:
                        missing = True
                        break

                if missing or val is None:
                    continue

                if not _is_default_value(field_path, val):
                    non_default += 1

            checks[field_path] = {
                "non_default_count": non_default,
                "non_default_pct": round(non_default / n * 100, 1),
            }

        # Classify readiness
        pcts = [c["non_default_pct"] for c in checks.values()]
        min_pct = min(pcts) if pcts else 0
        avg_pct = sum(pcts) / len(pcts) if pcts else 0

        if min_pct >= 80:
            status = "READY"
        elif avg_pct >= 30:
            status = "PARTIAL"
        else:
            status = "GAP"

        readiness[report_id] = {
            "name": report_def["name"],
            "status": status,
            "field_checks": checks,
            "min_coverage_pct": round(min_pct, 1),
            "avg_coverage_pct": round(avg_pct, 1),
        }

    return readiness


def _is_default_value(field_path, value):
    """Check if a value is a known default (indicating missing data)."""
    defaults = {
        "seismic.pga_g": [0.03, 0],
        "seismic.zone": [4],
        "climate_trajectory.I1_trajectory": [1.0],
        "climate_trajectory.I2_trajectory": [1.0],
        "climate_trajectory.I3_trajectory": [1.0],
        "socio_economic.V_socio": [0.5],  # uniform default
        "graph_topology.degree": [10],  # Germany default
        # R7 SFDR PAI: Re_norm=0.0 is the Convention #56 neutral-default
        # emitted by merge_into_ssi_data.py for net-new substations post-L1
        # refresh (before Phase 2 modifier-chain rescore populates the actual
        # Re composite). Counts as NOT READY until rescore per Convention
        # #78 §4bis.4 two-phase workflow discipline. Note field name in
        # ikengassiindex.github.io public dashboard ssi-data.json is `Re_norm`
        # (not `Re_normalised` as used in the ssi-enn-compliance clone's
        # Convention #66 EXPECTED_KEYS — cross-repo naming inconsistency
        # documented 16 July 2026 R7 workstream Phase 4a smoke test).
        "Re_norm": [0.0],
    }

    known = defaults.get(field_path, [])
    return value in known


# ═══════════════════════════════════════════════════════════
#  DIFF REPORT
# ═══════════════════════════════════════════════════════════

def generate_diff_report(stats):
    """Generate human-readable enrichment diff report."""
    lines = [
        f"═══ SSI Pipeline Enrichment Report ═══",
        f"Country: {stats['country']}",
        f"Total substations: {stats['total_substations']}",
        f"",
        f"── Data Updates ──",
        f"  Seismic PGA:      {stats['seismic_updates']:,} substations updated",
        f"  Climate trajectory: {stats['climate_updates']:,} substations updated",
        f"  Socio-economic:    {stats['socio_updates']:,} substations updated",
        f"  Rescored (MC):     {stats['rescored']:,} substations",
        f"",
    ]

    # Classification changes
    changes = stats.get("classification_changes", [])
    if changes:
        lines.append(f"── Classification Changes ({len(changes)}) ──")
        upgrades = [c for c in changes if _band_rank(c["new"]) < _band_rank(c["old"])]
        downgrades = [c for c in changes if _band_rank(c["new"]) > _band_rank(c["old"])]
        lines.append(f"  Upgrades:   {len(upgrades)}")
        lines.append(f"  Downgrades: {len(downgrades)}")
        for c in changes[:20]:
            arrow = "↑" if _band_rank(c["new"]) < _band_rank(c["old"]) else "↓"
            lines.append(f"  {arrow} {c['name']}: {c['old']} → {c['new']} "
                        f"(R: {c['R_old']:.4f} → {c['R_new']:.4f})")
    else:
        lines.append("── No classification changes ──")

    # ESG Readiness
    esg = stats.get("esg_readiness", {})
    if esg:
        lines.append(f"")
        lines.append(f"── ESG Report Readiness ──")
        for rid in sorted(esg.keys()):
            r = esg[rid]
            emoji = {"READY": "●", "PARTIAL": "◐", "GAP": "○"}
            lines.append(f"  {emoji.get(r['status'], '?')} {rid} {r['name']}: "
                        f"{r['status']} (min {r['min_coverage_pct']}% / avg {r['avg_coverage_pct']}%)")

    return "\n".join(lines)


def _band_rank(name):
    ranks = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    return ranks.get(name, 1)


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    """Run full enrichment pipeline for a country."""
    import argparse

    parser = argparse.ArgumentParser(description="SSI Pipeline — Enrichment & Merge")
    parser.add_argument("country", help="Country to process")
    parser.add_argument("--seismic", type=str, help="Path to seismic results JSON")
    parser.add_argument("--climate", type=str, help="Path to climate results JSON")
    parser.add_argument("--socio", type=str, help="Path to socio-economic results JSON")
    parser.add_argument("--no-rescore", action="store_true", help="Skip Monte Carlo rescoring")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to disk")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    seismic = json.load(open(args.seismic)) if args.seismic else None
    climate = json.load(open(args.climate)) if args.climate else None
    socio = json.load(open(args.socio)) if args.socio else None

    stats = merge_and_rescore(
        args.country,
        seismic_results=seismic,
        climate_results=climate,
        socio_results=socio,
        rescore=not args.no_rescore,
        dry_run=args.dry_run,
    )

    report = generate_diff_report(stats)
    print(report)


if __name__ == "__main__":
    main()
