#!/usr/bin/env python3
"""
refresh_fleet_summary.py — Recompute fleet_summary + regions from sharded ssi-data.

CONTEXT
-------
After Discipline #36 remediation (scripts/remediate_cross_border.py) or Convention
#79 sharded pipeline runs, a country's `ssi-data.json` manifest can carry stale
`fleet_summary` aggregates:

  - `median_R`, `mean_R`, `P5`, `P95` = None
  - `n_scored` mismatched with `total`
  - `bands` missing the 5th "Extreme" band (Phase 2B, 25 Jun 2026)
  - `band_pct` percentages sum to <100%
  - regions[] carry per-region `R_median: None`

The map.html header renders "median R = —" when median_R is None, and the L2/L3
recompute-fleet_summary step didn't run after remediation. This script closes
the gap by loading actual substations (across shards per Convention #79),
calling `engine.compute_fleet_summary()` + `engine.compute_regional_summary()`,
and writing the corrected manifest back atomically.

USAGE
-----
    # Single country
    python3 scripts/refresh_fleet_summary.py france

    # Multiple countries
    python3 scripts/refresh_fleet_summary.py france germany italy spain sweden

    # Auto-detect drift + fix cohort-wide
    python3 scripts/refresh_fleet_summary.py --all-drift

    # Dry run (report changes without writing)
    python3 scripts/refresh_fleet_summary.py --all-drift --dry-run

CONVENTION PRESERVATION
-----------------------
- Convention #56 (visibly-honest degradation): sub with R_median=None stays
  "Unclassified" in bands + None median propagates if no scored subs exist.
- Convention #79 (ssi-data sharding): loads + writes via canonical shard
  reader/writer; sharded state preserved on save.
- Convention #55 (verify-don't-trust): emits before/after diff per country.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Support both invocation styles: `python3 scripts/refresh_fleet_summary.py` and
# `python3 -m scripts.refresh_fleet_summary`. When called as a script, __package__
# is not set, so we prepend the repo root to sys.path.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data  # noqa: E402
from scripts.pipeline.scoring.engine import (  # noqa: E402
    _percentile,
    classify_confidence,
    compute_fleet_summary,
    compute_regional_summary,
)


_CANONICAL_BANDS = ("Low", "Medium", "High", "Critical", "Extreme", "Unclassified")


def _bands_from_classification_field(substations):
    """Count bands by each sub's `classification` field (Task #461 per-country
    normalised) rather than absolute-cutoff `classify_band(R_median)`.

    Task #461 (22 July 2026, Phase 2D) introduced per-country P5/P95 percentile
    normalisation so classification bands reflect within-country ranking not
    absolute R_median. The engine's `compute_fleet_summary` counts by absolute
    cutoffs which regresses from the Phase 2D state. Preserve the per-country
    normalised counts by aggregating `sub['classification']` directly.
    """
    counts = {k: 0 for k in _CANONICAL_BANDS}
    for s in substations:
        band = s.get("classification")
        if band not in counts:
            # Unexpected label — file under Unclassified per Convention #56.
            band = "Unclassified"
        counts[band] += 1
    return counts


def _recompute_fleet_summary_task_461_aware(substations):
    """Recompute fleet_summary preserving Task #461 per-country normalised bands.

    Delegates aggregate stats (median_R, mean_R, P5, P95, n_scored,
    confidence_tiers) to the engine's `compute_fleet_summary` for canonical
    behaviour, then overrides the `bands` + `band_pct` blocks with counts from
    each sub's `.classification` field.
    """
    fs = compute_fleet_summary(substations, previous=data.get('fleet_summary'))  # M-065
    n = len(substations)
    if n == 0:
        return fs

    bands_norm = _bands_from_classification_field(substations)
    fs["bands"] = bands_norm
    fs["band_pct"] = {k: round(v / n * 100, 1) for k, v in bands_norm.items()}

    # Record which basis was used so a future consumer can distinguish
    # absolute-cutoff bands from Task #461 per-country normalised bands.
    fs["_bands_source"] = "task_461_per_country_normalised_classification_field"
    return fs


def _has_drift(manifest: dict) -> tuple[bool, list[str]]:
    """Return (is_drifted, list_of_issues)."""
    fs = manifest.get("fleet_summary") or {}
    total = fs.get("total") or 0
    if total < 100:
        return False, []

    issues = []

    # M-004 fix (19 August 2026) — band-basis drift. Without this predicate
    # --all-drift silently skips every country whose ONLY defect is that
    # fleet_summary.bands was built on absolute cutoffs rather than the Task
    # #461 per-country normalised `classification` field. That was 39 of 39.
    if fs.get("_bands_source") != "task_461_per_country_normalised_classification_field":
        issues.append("bands_not_task_461_normalised")

    median_R = fs.get("median_R")
    n_scored = fs.get("n_scored") or 0
    bands = fs.get("bands") or {}
    bands_sum = sum(bands.values()) if bands else 0

    if median_R is None:
        issues.append("median_R=None")
    if n_scored != total:
        issues.append(f"n_scored_stale({n_scored}vs{total})")
    if "Extreme" not in bands:
        issues.append("no_Extreme_band")
    if bands_sum > 0 and abs(bands_sum - total) > total * 0.02:
        issues.append(f"bands_drift({bands_sum}vs{total})")

    return len(issues) > 0, issues


def _summarize(manifest: dict) -> str:
    fs = manifest.get("fleet_summary") or {}
    med = fs.get("median_R")
    med_s = f"{med:.4f}" if med is not None else "None"
    return (
        f"total={fs.get('total')} n_scored={fs.get('n_scored')} "
        f"median_R={med_s} bands={fs.get('bands')}"
    )


def refresh_country(slug: str, dry_run: bool = False) -> dict:
    """Recompute fleet_summary + regions for a country. Returns diff report."""
    manifest, subs, is_sharded = load_ssi_data(slug)

    before_fs = dict(manifest.get("fleet_summary") or {})
    before_str = _summarize(manifest)

    # Recompute from actual substations (Task #461-aware bands)
    new_fleet_summary = _recompute_fleet_summary_task_461_aware(subs)
    new_regions = compute_regional_summary(subs)

    # Preserve any additional fields the previous fleet_summary may have carried
    # (e.g. band_normalisation, phase2c_reclassify_runs metadata) — but ALWAYS
    # let the recomputed keys win.
    preserved_keys = {
        k: v for k, v in before_fs.items()
        if k not in new_fleet_summary and not k.startswith("_")
    }
    merged_fleet_summary = {**preserved_keys, **new_fleet_summary}

    manifest["fleet_summary"] = merged_fleet_summary
    manifest["regions"] = new_regions

    after_str = _summarize(manifest)

    report = {
        "country": slug,
        "n_subs": len(subs),
        "sharded": is_sharded,
        "before": before_str,
        "after": after_str,
        "n_regions_before": len(before_fs.get("regions") or [])
        if isinstance(before_fs.get("regions"), list)
        else "n/a",
        "n_regions_after": len(new_regions),
    }

    if not dry_run:
        save_ssi_data(slug, manifest, subs)
        report["written"] = True
    else:
        report["written"] = False

    return report


def _all_drifted_countries() -> list[str]:
    """Scan intelligence/countries.json for drift signatures."""
    with open(REPO_ROOT / "intelligence" / "countries.json") as f:
        countries = json.load(f)["slugs"]

    drifted = []
    for slug in countries:
        try:
            manifest, _subs, _sharded = load_ssi_data(slug)
        except FileNotFoundError:
            continue
        except Exception as e:  # noqa: BLE001
            print(f"  WARNING: could not load {slug}: {e}", file=sys.stderr)
            continue
        is_drift, _ = _has_drift(manifest)
        if is_drift:
            drifted.append(slug)
    return drifted


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="Country slug(s) to refresh")
    ap.add_argument("--all-drift", action="store_true", help="Auto-detect + fix all drifted countries")
    ap.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = ap.parse_args()

    if args.all_drift:
        targets = _all_drifted_countries()
        print(f"Detected {len(targets)} countries with fleet_summary drift:")
        for t in targets:
            print(f"  - {t}")
        print()
    else:
        targets = args.slugs

    if not targets:
        ap.print_help()
        return 1

    for slug in targets:
        print(f"[{slug}] {'DRY-RUN' if args.dry_run else 'REFRESHING'}...")
        try:
            report = refresh_country(slug, dry_run=args.dry_run)
        except FileNotFoundError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        print(f"  before: {report['before']}")
        print(f"  after:  {report['after']}")
        print(f"  n_subs={report['n_subs']:,}  sharded={report['sharded']}  regions={report['n_regions_after']}  written={report['written']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
