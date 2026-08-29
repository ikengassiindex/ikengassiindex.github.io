#!/usr/bin/env python3
"""
scripts/fix_wave4_r_base_regression.py — L3 R_base composition rescore
======================================================================

Fixes the Wave 4 L3 scoring regression that emitted `R_base_median = 0.0`
uniformly across 8 large countries, nullifying the C·V·I·E·S·T composite
(the entire multiplicative R-modifier chain then multiplied against zero,
so R_median collapsed to purely additive R6c_flood overflow bounded to
[0, 0.30] → 86% false-classified as "Low" cohort-wide).

Root cause discovered 21 July 2026 via Spain audit (Task #454):

    scripts/refresh_v42_modifiers_re_composite.py (R7 Phase 4c) populates
    per-substation modifier values (R6c_flood, R6d_wildfire, R6e_winter,
    R8_adapt, R9_compound, R10_just) + Re_raw + Re_norm — but does NOT
    re-invoke compute_r_base(components) or run Monte Carlo to update
    R_median. Wave 4 batch rerun (Task #423) computed R_base from
    then-empty component stubs → wrote 0.0 to disk. Later enrichment
    populated components per-substation but no downstream step recomputed
    R_base against those enriched values.

    Empirical proof for Spain (30,222 subs):
      - Current on-disk R_base_median: 0.0 uniform (1 unique)
      - Proper R_base from populated components: 0.26–0.43 (per-sub variance)
      - Simulated correct R_median: mean 0.61, std 0.09
      - Simulated correct band distribution: 0% Low, 27% Medium, 66% High,
        7% Critical (vs current 86% Low, 14% Medium, 0% High/Critical)

Affected countries (8 of Wave 4 P32-P39; UK P31 correctly processed):
  spain, italy, france, portugal, germany, sweden, japan, us

This script:
  1. Loads ssi-data.json (Convention #79 sharded or inline)
  2. For each substation, calls engine.score_substation() with no updates
     — this recomputes R_base = compute_r_base(components) + runs the
     full 10K-iteration Monte Carlo copula against real modifiers +
     applies classify_band() to the resulting R_median
  3. Writes back all engine-computed fields (R_base_median, R_median,
     R_P5, R_P95, CI_width, skewness, P_critical, R_unclipped,
     modifier_impact, modifier_pct, classification, confidence_tier,
     mult_product, add_sum, modifier_impacts)
  4. Refreshes fleet_summary via compute_fleet_summary + regions[].bands
     via compute_regional_summary
  5. Re-shards Convention #79 large countries (Germany/France/US + Spain
     if it grows past 90 MB)
  6. Emits per-country audit YAML capturing before/after band transitions
     + mean R_median shift + provenance pins

Convention preservation:
  - #7   Data-Layer Anchoring — deterministic derivation from on-disk
         components + modifiers via same engine.py functions the
         production pipeline uses
  - #23  Provenance pinning — audit YAML per country emitted
  - #56  Visibly-honest degradation — subs with R_median=None retained;
         classify_band handles them via "Unclassified" band
  - #67  Consumer-adapter discipline — reads via read_ssi_data(),
         writes via write_ssi_data() (Convention #79 sharding transparent)
  - #79  SSI-data automatic sharding (preserved by write_ssi_data)

Usage:
    python3 scripts/fix_wave4_r_base_regression.py <slug>            # single country
    python3 scripts/fix_wave4_r_base_regression.py <slug> --dry-run  # preview
    python3 scripts/fix_wave4_r_base_regression.py --all-broken      # all 8
    python3 scripts/fix_wave4_r_base_regression.py --all-broken --dry-run

Exit codes:
    0 = SUCCESS or DRY_RUN
    1 = ERROR (file missing, parse failure, engine crash)
    2 = SKIPPED (country not in broken list + no --force)

Runtime estimate:
    Monte Carlo 10K iter × ~590K subs (8 countries) ≈ 45-60 minutes
    Deterministic-only path (--fast) ≈ 3-5 minutes cohort-wide
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Repo root import shim ───
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.scoring.engine import (  # noqa: E402
    score_substation,
    compute_r_base,
    compute_r_median,
    classify_band,
    apply_country_normalised_bands,
    classify_confidence,
    compute_fleet_summary,
    compute_regional_summary,
    COMPONENT_WEIGHTS,
)
from scripts.pipeline.utils.ssi_data_sharding import (  # noqa: E402
    read_ssi_data,
    write_ssi_data,
    SSI_DATA_SHARD_THRESHOLD_MB,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")
logger = logging.getLogger(__name__)

# ─── Broken country list (empirically confirmed 21 July 2026) ───
BROKEN_COUNTRIES = [
    "spain",     # 30,222 subs
    "italy",     # 51,910 subs
    "france",    # 195,569 subs (sharded)
    "portugal",  # 13,977 subs
    "germany",   # 187,714 subs (sharded)
    "sweden",    # 11,399 subs
    "japan",     #  7,073 subs
    "us",        # 101,594 subs (sharded)
]

BANDS_ORDER = ["Low", "Medium", "High", "Critical", "Extreme", "Unclassified"]


def band_counts(subs: list) -> dict:
    """Count classifications across a substation list."""
    counts = {b: 0 for b in BANDS_ORDER}
    for s in subs:
        c = s.get("classification", "Unclassified")
        if c not in counts:
            c = "Unclassified"
        counts[c] += 1
    return counts


def r_median_stats(subs: list) -> dict:
    """Compute R_median summary statistics."""
    vals = [s.get("R_median") for s in subs if isinstance(s.get("R_median"), (int, float))]
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None, "std": None}
    import statistics
    return {
        "n": len(vals),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
        "mean": round(statistics.mean(vals), 4),
        "std": round(statistics.stdev(vals) if len(vals) > 1 else 0, 4),
    }


def r_base_stats(subs: list) -> dict:
    """Compute R_base_median summary statistics."""
    vals = [s.get("R_base_median") for s in subs if isinstance(s.get("R_base_median"), (int, float))]
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None}
    import statistics
    return {
        "n": len(vals),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
        "mean": round(statistics.mean(vals), 4),
        "unique": len(set(round(v, 4) for v in vals)),
    }


def diagnose_country(slug: str) -> dict:
    """Load a country's ssi-data + report whether it exhibits the R_base=0 defect."""
    path = REPO_ROOT.parent / slug / "ssi-data.json"
    if not path.exists():
        # Fall back to repo-root-relative path (running from ikengassiindex.github.io)
        path = REPO_ROOT / slug / "ssi-data.json"
    if not path.exists():
        return {"slug": slug, "error": "ssi-data.json not found"}

    data = read_ssi_data(path)
    subs = data.get("substations", [])
    if not subs:
        return {"slug": slug, "error": "no substations loaded"}

    rb = r_base_stats(subs[:5000])
    rm = r_median_stats(subs[:5000])
    is_broken = rb.get("max", 0) is not None and rb["max"] < 0.001
    return {
        "slug": slug,
        "n_subs_total": len(subs),
        "R_base_stats": rb,
        "R_median_stats": rm,
        "band_counts": band_counts(subs),
        "is_broken": is_broken,
    }


def fix_country(slug: str, dry_run: bool = False, fast: bool = False) -> dict:
    """Recompute R_base_median + R_median + classification for every sub.

    Args:
      slug: country slug (e.g. "spain")
      dry_run: if True, do NOT write ssi-data.json; only report the
               would-be band transitions + stats deltas
      fast: if True, use deterministic compute_r_median (no Monte Carlo);
            R_P5/R_P95/CI_width/skewness fields preserved as-is from prior
            state. If False (default), invoke score_substation() which
            runs the full 10K-iteration MC copula.

    Returns:
      dict with before/after R_base_stats, R_median_stats, band_counts,
      transition matrix (from_band, to_band), duration_seconds, and
      whether the fix was applied.
    """
    path = REPO_ROOT.parent / slug / "ssi-data.json"
    if not path.exists():
        path = REPO_ROOT / slug / "ssi-data.json"
    if not path.exists():
        return {"slug": slug, "error": "ssi-data.json not found", "applied": False}

    logger.info(f"[{slug}] loading ssi-data...")
    t0 = time.time()
    data = read_ssi_data(path)
    subs = data.get("substations", [])
    n = len(subs)
    if n == 0:
        return {"slug": slug, "error": "no substations loaded", "applied": False}

    logger.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # Before-state
    before_rb = r_base_stats(subs)
    before_rm = r_median_stats(subs)
    before_bands = band_counts(subs)

    # Rescore each sub
    logger.info(f"[{slug}] rescoring ({'FAST deterministic' if fast else 'FULL MC 10K'})...")
    t_score_start = time.time()
    from_to_transitions = {}
    # Task #461: the band a record ends up with is decided AFTER the whole
    # country is rescored, because the cutoffs are per-country percentiles of
    # the new R_median distribution. So the old classes are captured here and
    # the transitions computed once normalisation has run — not per record
    # against an intermediate absolute band.
    old_classes = [s.get("classification", "Unclassified") for s in subs]
    _blind_skipped = 0
    for i, sub in enumerate(subs):
        # Convention #56. A record with no components has nothing to derive a
        # score from. Rescoring it anyway yields R_base = 0 and therefore
        # R_median = add_sum — the flood modifier alone — which is a real
        # number, so the record acquires a band it has no basis for. That is
        # the BANDED_BLIND defect (5fefb9ac), and turkey's dry run showed the
        # repair creating 30 fresh instances of it. Leave them exactly as
        # found; what to do with a blind substation is a decision, not a
        # rescore.
        _comps = sub.get("components") or {}
        if not any(isinstance(v, (int, float)) for v in _comps.values()):
            _blind_skipped += 1
            continue
        if fast:
            # Deterministic path: recompute R_base + R_median analytically
            components = sub.get("components", {})
            modifiers = sub.get("modifiers", {})
            R_base = compute_r_base(components)
            R_med = compute_r_median(R_base, modifiers)
            sub["R_base_median"] = round(R_base, 4)
            sub["R_median"] = round(R_med, 4)
            sub["R_unclipped"] = round(R_med, 4)
            sub["classification"] = classify_band(R_med)
            # modifier_impact + pct
            sub["modifier_impact"] = round(R_med - R_base, 4)
            sub["modifier_pct"] = f"{abs(R_med - R_base) / max(R_base, 0.001) * 100:.1f}%"
        else:
            # Full MC via score_substation (empty updates — just recompute)
            updated = score_substation(sub)
            # score_substation returns a NEW deepcopy — replace in-place
            subs[i] = updated
            sub = updated

        # Progress
        if (i + 1) % 10000 == 0:
            elapsed = time.time() - t_score_start
            rate = (i + 1) / elapsed
            eta = (n - i - 1) / rate
            logger.info(f"[{slug}]   {i+1:>7,}/{n:,} ({100*(i+1)/n:.1f}%) - {rate:.0f} subs/s - ETA {eta:.0f}s")

    scoring_seconds = time.time() - t_score_start
    logger.info(f"[{slug}] rescored {n:,} subs in {scoring_seconds:.1f}s ({n/scoring_seconds:.0f} subs/s)")

    # Task #461 per-country normalisation. score_substation and the FAST path
    # both write classify_band's ABSOLUTE band; the register is banded by
    # within-country rank. Without this the repair would revert Task #461 for
    # every country it touched — and silently, because fleet_summary would be
    # rebuilt from the same absolute classes and the band gate would still
    # agree with itself.
    apply_country_normalised_bands(subs)

    # Convention #56, tested on the property the register cares about: a band
    # implies data behind it. The earlier form of this guard counted records
    # with R_median None AFTER the rescore, by which point the rescore had
    # supplied one — it measured the right property at the wrong moment and
    # passed while 30 blind records were being banded.
    _banded_blind = [s for s in subs
                     if not any(isinstance(v, (int, float))
                                for v in (s.get("components") or {}).values())
                     and s.get("classification") not in (None, "Unclassified")]
    if _banded_blind:
        raise AssertionError(
            f"{slug}: {len(_banded_blind)} substations have no components but "
            f"carry a band — e.g. {_banded_blind[0].get('substation_id')!r} as "
            f"{_banded_blind[0].get('classification')!r}. The repair must not "
            f"manufacture a classification it has no data for.")
    if _blind_skipped:
        logger.warning(
            "[%s] %d substations have no components and were left untouched — "
            "not rescored, not rebanded. There is nothing to derive a score "
            "from; see FINDING_r_base_zero_135844.md section 5.2.",
            slug, _blind_skipped)

    for old_c, sub in zip(old_classes, subs):
        key = (old_c, sub.get("classification", "Unclassified"))
        from_to_transitions[key] = from_to_transitions.get(key, 0) + 1

    # After-state
    after_rb = r_base_stats(subs)
    after_rm = r_median_stats(subs)
    after_bands = band_counts(subs)

    # Refresh fleet_summary + regions[].bands
    logger.info(f"[{slug}] refreshing fleet_summary + regional bands...")
    data["substations"] = subs
    # engine.compute_fleet_summary (engine.py:737) and
    # compute_regional_summary (:799) both tally with classify_band, the
    # absolute classifier. On a Task #461 country that publishes a band
    # distribution contradicting its own map. The aware routines count the
    # `classification` field instead — the same two this repo already switched
    # ssi_dedupe_substations.py onto.
    from refresh_fleet_summary import (
        _recompute_fleet_summary_task_461_aware,
        _recompute_regional_summary_task_461_aware)
    data["fleet_summary"] = _recompute_fleet_summary_task_461_aware(subs)
    if "regions" in data and isinstance(data["regions"], list):
        data["regions"] = _recompute_regional_summary_task_461_aware(subs)

    # Provenance pin
    data.setdefault("_provenance", {}).setdefault("history", []).append({
        "action": "L3_R_base_regression_fix",
        "script": "scripts/fix_wave4_r_base_regression.py",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_ref": "Task #454 → Task #455 → Task #450 systemic closure",
        "mode": "FAST" if fast else "FULL_MC_10K",
        "n_subs": n,
        "n_blind_skipped": _blind_skipped,
        "before": {"R_base_stats": before_rb, "R_median_stats": before_rm, "band_counts": before_bands},
        "after": {"R_base_stats": after_rb, "R_median_stats": after_rm, "band_counts": after_bands},
        "convention_refs": ["#7", "#23", "#56", "#67", "#79"],
        "note": "Fixes L3 R_base=0 regression that classified 86% subs as Low. See root-cause narrative in script docstring.",
    })

    result = {
        "slug": slug,
        "n_subs": n,
        "duration_seconds": round(time.time() - t0, 1),
        "scoring_seconds": round(scoring_seconds, 1),
        "before": {"R_base": before_rb, "R_median": before_rm, "bands": before_bands},
        "after": {"R_base": after_rb, "R_median": after_rm, "bands": after_bands},
        "transitions": {f"{k[0]}→{k[1]}": v for k, v in sorted(from_to_transitions.items(), key=lambda x: -x[1])[:15]},
        "applied": not dry_run,
    }

    if dry_run:
        logger.info(f"[{slug}] --dry-run: NOT writing ssi-data.json")
    else:
        logger.info(f"[{slug}] writing ssi-data.json (may re-shard if > {SSI_DATA_SHARD_THRESHOLD_MB} MB)...")
        write_ssi_data(data, path)
        logger.info(f"[{slug}] saved.")

    return result


def print_summary(res: dict):
    """Human-readable per-country summary."""
    if "error" in res:
        print(f"\n❌ {res['slug']}: {res['error']}")
        return
    print(f"\n─── {res['slug']} ({res['n_subs']:,} subs, {res['duration_seconds']}s) ───")
    b = res["before"]
    a = res["after"]
    print(f"  R_base_median:  before={b['R_base'].get('mean'):.4f} (unique={b['R_base'].get('unique', 1)}) → after={a['R_base'].get('mean'):.4f} (unique={a['R_base'].get('unique', 1)})")
    print(f"  R_median:       before mean={b['R_median']['mean']:.4f} max={b['R_median']['max']:.4f} → after mean={a['R_median']['mean']:.4f} max={a['R_median']['max']:.4f}")
    print(f"  Band shift:")
    for band in BANDS_ORDER:
        old = b["bands"].get(band, 0)
        new = a["bands"].get(band, 0)
        delta = new - old
        pct_old = 100 * old / res["n_subs"]
        pct_new = 100 * new / res["n_subs"]
        arrow = "→" if delta == 0 else ("↑" if delta > 0 else "↓")
        print(f"    {band:<12} {old:>7,} ({pct_old:>5.1f}%)  {arrow}  {new:>7,} ({pct_new:>5.1f}%)   delta={delta:+,}")
    print(f"  Top transitions (from→to):")
    for tr, count in list(res["transitions"].items())[:8]:
        print(f"    {tr:<25} {count:>7,}")
    print(f"  {'✓ APPLIED' if res['applied'] else '⏸ DRY RUN (no write)'}")


def main():
    ap = argparse.ArgumentParser(description="Fix Wave 4 L3 R_base_median=0 regression")
    ap.add_argument("slug", nargs="?", help="Single country slug (or use --all-broken)")
    ap.add_argument("--all-broken", action="store_true", help=f"Run on all 8 broken countries: {BROKEN_COUNTRIES}")
    ap.add_argument("--dry-run", action="store_true", help="Preview only; do not write ssi-data.json")
    ap.add_argument("--fast", action="store_true", help="Deterministic recompute (no Monte Carlo — 15× faster)")
    ap.add_argument("--diagnose-only", action="store_true", help="Just report R_base=0 detection; no rescore")
    ap.add_argument("--force", action="store_true", help="Rescore a country even if not in BROKEN_COUNTRIES")
    args = ap.parse_args()

    if not args.slug and not args.all_broken:
        ap.error("must provide <slug> or --all-broken")

    targets = BROKEN_COUNTRIES if args.all_broken else [args.slug]

    # Diagnose-only path
    if args.diagnose_only:
        for slug in targets:
            diag = diagnose_country(slug)
            if "error" in diag:
                print(f"❌ {slug}: {diag['error']}")
                continue
            status = "❌ BROKEN" if diag["is_broken"] else "✅ ok"
            rb = diag["R_base_stats"]
            print(f"{slug:<12} n={diag['n_subs_total']:>7,}  R_base=[{rb['min']:.4f}, {rb['max']:.4f}] unique={rb['unique']}  {status}")
        return 0

    # Guard against running on non-broken countries without --force
    if not args.all_broken and args.slug not in BROKEN_COUNTRIES and not args.force:
        print(f"⚠ {args.slug} not in BROKEN_COUNTRIES {BROKEN_COUNTRIES}")
        print(f"  Use --force to rescore anyway, or --diagnose-only to check status")
        return 2

    # Fix path
    results = []
    t_start = time.time()
    for slug in targets:
        try:
            res = fix_country(slug, dry_run=args.dry_run, fast=args.fast)
            results.append(res)
            print_summary(res)
        except Exception as e:
            logger.exception(f"[{slug}] FAILED: {e}")
            results.append({"slug": slug, "error": str(e), "applied": False})

    # Emit combined audit YAML (dry-run and applied both write to different filename)
    audit_path = REPO_ROOT.parent / f"fix_wave4_r_base_audit_{'DRYRUN_' if args.dry_run else ''}{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    if not audit_path.parent.exists():
        audit_path = REPO_ROOT / audit_path.name  # fallback to repo dir
    audit_path.write_text(json.dumps({
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "FAST" if args.fast else "FULL_MC_10K",
        "dry_run": args.dry_run,
        "targets": targets,
        "results": results,
        "total_duration_seconds": round(time.time() - t_start, 1),
    }, indent=2, default=str))
    print(f"\n✓ Audit report: {audit_path}")

    # Exit code
    return 0 if all("error" not in r for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
