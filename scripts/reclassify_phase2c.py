#!/usr/bin/env python3
"""
Phase 2C — Full-cohort reclassification against the 5-band Extreme system.

Purpose
-------
Phase 2B-1 extended scripts/pipeline/scoring/engine.py::BANDS from 4 bands to 5
(added 'Extreme' for R_median ∈ [1.00, 1.30] — the additive-R6c_flood overflow
zone per the v4.2 master equation). The stored `classification` field on
existing substations was written by legacy scoring paths that predate the new
band table; this script regenerates it cohort-wide.

Why a targeted re-classification, not a full pipeline `--rescore`
---------------------------------------------------------------
The Phase 2B-1 change was purely at the classify-band boundary. R_median values
themselves are unchanged: no modifier chain change, no R_base change, no MC
change. So the R_median values on disk are already correct — they just need
re-binning against the new 5-band table. A full pipeline rescore would re-run
Monte Carlo unnecessarily (~1 h for 174 k substations × 10 k iterations); this
script does the same corrective work in ~2 min by re-applying classify_band()
and recomputing fleet + regional band aggregates.

Empirically expected outcome
----------------------------
Post-run, `python3 scripts/validate_schema.py --all` should collapse:
  - Cause A (Italy R_median > 1.0 range gate) — already cleared in Phase 2A
    validator patch; this script emits Extreme classifications for those subs
    so the classification-band gate passes too.
  - Cause B (classification stale after merge-without-rescore) — cleared
    cohort-wide as every substation's classification is rewritten from its
    current R_median.
  - Cause C (Luxembourg all-Low + Belgium/Netherlands legacy scoring vintage)
    — cleared; classification field now reflects current R_median against
    the 5-band table.

Cause D2 (structurally-orphaned modifier drift — R7_cyber, R4_F_topo, etc.)
is unaffected because that lives in the modifier values, not the classification
field. Cause D2 stays as the queued follow-on workstream per operator's Q3(a)
decision.

Idempotency
-----------
Safe to re-run; if a substation's classification already matches
classify_band(R_median), no delta. fleet_summary.bands + regions[].bands
dicts are regenerated deterministically each pass.

Usage
-----
    python3 scripts/reclassify_phase2c.py                    # all 39 SoT
    python3 scripts/reclassify_phase2c.py italy austria      # subset
    python3 scripts/reclassify_phase2c.py --dry-run          # report only

Cross-references
----------------
- Convention #56 (visibly-honest degradation): no substation is silently
  reclassified; the audit log lists every classification transition.
- Convention #63 (parallel worlds): reclassification stays inside the
  compliance-methodology world; no financial-side output affected.
- Phase 2A validator patch (`scripts/validate_schema.py`).
- Phase 2B-1 engine BANDS extension (`scripts/pipeline/scoring/engine.py`).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Import the canonical BANDS + classify_band from the engine — single source
# of truth per Convention #67 (consumer-adapter discipline). engine.py uses a
# relative import for modifier_registry, so we need to load it as a package
# member (scripts.pipeline.scoring.engine) not a bare module.
_repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root))
from scripts.pipeline.scoring import engine  # noqa: E402

BAND_NAMES: List[str] = [b["name"] for b in engine.BANDS]  # Low/Medium/High/Critical/Extreme


def _empty_band_counts() -> Dict[str, int]:
    return {name: 0 for name in BAND_NAMES}


def _load_country_slugs() -> List[str]:
    """Read the canonical SoT slug list per KB §57."""
    p = _repo_root / "intelligence" / "countries.json"
    with open(p) as f:
        cfg = json.load(f)
    return list(cfg.get("slugs", []))


def _reclassify_substations(subs: List[Dict[str, Any]]) -> Tuple[int, Counter]:
    """
    Rewrite each substation's `classification` field from
    engine.classify_band(R_median). Returns (changed_count, transitions_counter).
    """
    changed = 0
    transitions: Counter = Counter()
    for s in subs:
        r = s.get("R_median")
        if r is None:
            continue
        try:
            r = float(r)
        except (TypeError, ValueError):
            continue
        new_band = engine.classify_band(r)
        old_band = s.get("classification")
        if old_band != new_band:
            transitions[(old_band, new_band)] += 1
            s["classification"] = new_band
            changed += 1
    return changed, transitions


def _recompute_fleet_summary(fs: Dict[str, Any], subs: List[Dict[str, Any]]) -> None:
    """
    Regenerate fleet_summary.bands + fleet_summary.band_pct with the 5-band
    system. Preserves other fields (median_R, mean_R, P5, P95, confidence*).
    """
    n = len(subs)
    if n == 0:
        return
    bands = _empty_band_counts()
    for s in subs:
        band = s.get("classification")
        if band in bands:
            bands[band] += 1
    fs["bands"] = bands
    fs["band_pct"] = {k: round(v / n * 100, 1) for k, v in bands.items()}


def _recompute_regions(regions: List[Dict[str, Any]], subs: List[Dict[str, Any]]) -> None:
    """
    Regenerate per-region bands + pct_critical + pct_extreme + pct_high with
    the 5-band system. Preserves other per-region fields (region, count,
    median_R, mean_R). Accepts either a list of dicts or a dict-of-dicts.

    pct_critical stays SINGLE-BAND (Critical only) per Phase 2B-1 engine
    convention (see engine.compute_regional_summary docstring).
    pct_extreme is a NEW peer single-band metric.
    pct_high is CUMULATIVE (High + Critical + Extreme) — extended from the
    pre-Phase-2B-1 (High + Critical) definition preserving 'top-of-fleet
    share' semantic.
    """
    # Group subs by region so we can re-tally without relying on stale counts
    per_region_subs: Dict[str, List[Dict[str, Any]]] = {}
    for s in subs:
        code = s.get("region")
        if code is None:
            continue
        per_region_subs.setdefault(code, []).append(s)

    def _update_region_entry(entry: Dict[str, Any], code: str) -> None:
        rsubs = per_region_subs.get(code, [])
        n = len(rsubs)
        if n == 0:
            return
        bands = _empty_band_counts()
        for s in rsubs:
            b = s.get("classification")
            if b in bands:
                bands[b] += 1
        entry["count"] = n
        entry["bands"] = bands
        entry["pct_critical"] = round(bands["Critical"] / n * 100, 1)
        entry["pct_extreme"] = round(bands["Extreme"] / n * 100, 1)
        entry["pct_high"] = round(
            (bands["High"] + bands["Critical"] + bands["Extreme"]) / n * 100, 1
        )

    if isinstance(regions, list):
        for entry in regions:
            code = entry.get("region") or entry.get("code") or entry.get("id")
            if code:
                _update_region_entry(entry, code)
    elif isinstance(regions, dict):
        for code, entry in regions.items():
            if isinstance(entry, dict):
                _update_region_entry(entry, code)


def process_country(slug: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Reclassify one country's ssi-data.json. Returns a per-country audit dict:
      { slug, changed, subs_total, transitions, band_dist_before, band_dist_after }
    """
    path = _repo_root / slug / "ssi-data.json"
    if not path.exists():
        return {"slug": slug, "skipped": True, "reason": "ssi-data.json not found"}

    with open(path) as f:
        data = json.load(f)

    subs_raw = data.get("substations", [])
    if isinstance(subs_raw, dict):
        subs = list(subs_raw.values())
    else:
        subs = subs_raw

    # Snapshot band distribution BEFORE re-classification
    band_before = Counter(s.get("classification") for s in subs)

    changed, transitions = _reclassify_substations(subs)

    # Snapshot band distribution AFTER re-classification
    band_after = Counter(s.get("classification") for s in subs)

    # Recompute fleet_summary + regions with 5-band system
    fs = data.setdefault("fleet_summary", {})
    _recompute_fleet_summary(fs, subs)

    regions = data.get("regions")
    if regions:
        _recompute_regions(regions, subs)

    # Meta stamp — Convention #56 visibly-honest audit trail
    meta = data.setdefault("meta", {})
    prior = meta.get("phase2c_reclassify_runs", [])
    if not isinstance(prior, list):
        prior = []
    from datetime import datetime, timezone
    prior.append({
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "changed": changed,
        "subs_total": len(subs),
        "engine_bands": BAND_NAMES,
        "dry_run": bool(dry_run),
    })
    meta["phase2c_reclassify_runs"] = prior[-3:]  # keep last 3 runs for audit

    if not dry_run:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "slug": slug,
        "changed": changed,
        "subs_total": len(subs),
        "transitions": dict(transitions),
        "band_dist_before": dict(band_before),
        "band_dist_after": dict(band_after),
    }


def _fmt_transition_summary(transitions: Dict[Any, int], limit: int = 6) -> str:
    if not transitions:
        return "(no transitions — classifications already match 5-band table)"
    items = sorted(transitions.items(), key=lambda kv: -kv[1])
    parts = [f"{a}->{b}={n}" for (a, b), n in items[:limit]]
    if len(items) > limit:
        parts.append(f"+{len(items) - limit} more")
    return " · ".join(parts)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 2C — Full-cohort reclassification against the 5-band Extreme system",
    )
    parser.add_argument(
        "slugs",
        nargs="*",
        help="Country slug(s) to reclassify. Default: all 39 SoT slugs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report transitions without writing files.",
    )
    args = parser.parse_args(argv)

    targets = args.slugs or _load_country_slugs()
    dry_run = args.dry_run

    print(f"Phase 2C reclassification — {len(BAND_NAMES)} bands: {BAND_NAMES}")
    print(f"Target countries: {len(targets)}{' (dry-run)' if dry_run else ''}")
    print()

    cohort_changed = 0
    cohort_total = 0
    for slug in sorted(targets):
        result = process_country(slug, dry_run=dry_run)
        if result.get("skipped"):
            print(f"  ⚠  {slug:14s} SKIPPED: {result.get('reason')}")
            continue
        cohort_changed += result["changed"]
        cohort_total += result["subs_total"]
        pct = (result["changed"] / result["subs_total"] * 100) if result["subs_total"] else 0
        icon = "✓" if not dry_run else "·"
        print(
            f"  {icon}  {slug:14s} "
            f"n={result['subs_total']:>6d}  "
            f"changed={result['changed']:>5d} ({pct:5.1f}%)  "
            f"transitions: {_fmt_transition_summary(result['transitions'])}"
        )

    print()
    cohort_pct = (cohort_changed / cohort_total * 100) if cohort_total else 0
    print(
        f"COHORT: {cohort_changed:,} / {cohort_total:,} substations reclassified "
        f"({cohort_pct:.1f}%){' — DRY RUN, no writes' if dry_run else ''}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
