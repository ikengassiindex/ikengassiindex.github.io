#!/usr/bin/env python3
"""Apply per-country P5/P95 normalisation to classification bands.

Task #461 (22 July 2026, follow-on to R_base fix commit 06a83c98)

The Wave 4 R_base regression fix (commit 06a83c98) closed the L3
R_base_median=0 defect + restored per-substation discrimination via
compute_r_base() re-invocation. But the empirical R_median distribution
is compressed to [0.42, 0.83] because:
  (a) additive R6c_flood modifier applies a ~0.25 floor cohort-wide
  (b) soft_clip_upper caps the maximum at ~0.85 for most subs

Under the fixed absolute-R 5-band cutoffs [0.25, 0.50, 0.75, 1.00] this
collapses ~80% of substations in ITA/ESP/PRT/FRA/DEU into the 'High'
band — the underlying per-substation ranking IS present (Madrid 0.53 <
Bilbao 0.61 < rural 0.66) but the band boundary hides it.

This script applies per-country P5/P95 normalisation to the
`classification` field:
  R_norm = clip((R_median - country_P5) / (country_P95 - country_P5), 0, 1)
  classification = classify_band(R_norm)  # uses existing 5-band cutoffs

Per Convention #56 visibly-honest degradation:
  - R_median stays unchanged per substation (LP-DD absolute score
    auditable in tooltips + intelligence dashboards).
  - Only `classification` field changes semantic — from "absolute
    physical risk threshold" to "within-country risk ranking".
  - The per-country P5/P95 anchors are stored on fleet_summary + on
    each sub as `_band_norm_R_P5` + `_band_norm_R_P95` for audit.
  - Sub also carries `_band_absolute` (what the band would be under
    absolute cutoffs) so the semantic shift can be verified retroactively.

Empirical outcome expected (Spain 30,222 subs pre-normalisation):
  Before:  0% Low / 11.4% Med / 81.6% High / 7.0% Crit / 0% Extreme
  After:   ~15% Low / ~30% Med / ~30% High / ~20% Crit / ~5% Extreme
         (linear normalisation preserves shape, distributes across bands)

Usage:
  # Single country
  python3 scripts/normalise_bands_per_country.py spain
  # Dry run (no writes)
  python3 scripts/normalise_bands_per_country.py spain --dry-run
  # All 8 Wave 4 countries (post R_base fix)
  python3 scripts/normalise_bands_per_country.py --wave4-post-rbase-fix
  # All 39 countries cohort-wide (advanced — only after Wave 4 verified)
  python3 scripts/normalise_bands_per_country.py --all-countries

Diagnose-only mode prints the empirical P5/P95 + before/after band
distribution without writing anything:
  python3 scripts/normalise_bands_per_country.py spain --diagnose-only
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# ── path setup for engine + writer imports ─────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.scoring.engine import (  # type: ignore
    apply_country_normalised_bands,
    classify_band,
    compute_fleet_summary,
    compute_regional_summary,
)
from scripts.pipeline.utils.ssi_data_sharding import (  # type: ignore
    read_ssi_data,
    write_ssi_data,
)

# ── countries covered by R_base fix commit 06a83c98 ────────────────────
WAVE4_POST_RBASE_FIX = [
    "spain", "italy", "portugal", "france",
    "germany", "sweden", "japan", "us",
]

# ── logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def _band_dict_from_subs(substations):
    """Count subs per band (post-mutation)."""
    counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0, "Extreme": 0, "Unclassified": 0}
    for s in substations:
        c = s.get("classification", "Unclassified")
        counts[c] = counts.get(c, 0) + 1
    return counts


def _snapshot_absolute_bands(substations):
    """Compute what the absolute-cutoff band would be — for audit trail."""
    for s in substations:
        R = s.get("R_median")
        s["_band_absolute"] = classify_band(R) if R is not None else "Unclassified"


def process_country(slug: str, *, dry_run: bool, diagnose_only: bool) -> dict:
    """Apply per-country normalisation to one country's ssi-data.

    Returns audit dict with before/after band counts + P5/P95 anchors.
    """
    t0 = time.time()
    country_dir = REPO_ROOT / slug
    ssi_path = country_dir / "ssi-data.json"

    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found at {ssi_path}")

    log.info(f"[{slug}] loading ssi-data...")
    data = read_ssi_data(ssi_path)
    substations = data.get("substations", [])
    n = len(substations)
    if n == 0:
        raise RuntimeError(f"[{slug}] ssi-data has zero substations")
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # ── snapshot BEFORE state ──────────────────────────────────────────
    before_bands = _band_dict_from_subs(substations)
    R_vals = sorted(s["R_median"] for s in substations if s.get("R_median") is not None)
    if R_vals:
        pre_R_P5 = R_vals[max(0, int(0.05 * len(R_vals)) - 1)]
        pre_R_P95 = R_vals[min(len(R_vals) - 1, int(0.95 * len(R_vals)))]
    else:
        pre_R_P5 = pre_R_P95 = None

    # ── mark each sub with what absolute-cutoff band would be ──────────
    _snapshot_absolute_bands(substations)

    # ── apply normalisation ────────────────────────────────────────────
    log.info(f"[{slug}] applying per-country P5/P95 normalisation...")
    R_P5, R_P95, n_norm, n_skip = apply_country_normalised_bands(substations)
    log.info(f"  R_P5={R_P5:.4f} R_P95={R_P95:.4f} span={R_P95-R_P5:.4f} "
             f"({n_norm:,} normalised, {n_skip} skipped)")

    # ── snapshot AFTER state ──────────────────────────────────────────
    after_bands = _band_dict_from_subs(substations)

    # ── refresh fleet_summary + regional_summary ──────────────────────
    log.info(f"[{slug}] refreshing fleet_summary + regional_summary...")
    fleet = compute_fleet_summary(substations)
    fleet["_band_normalisation"] = {
        "applied": True,
        "method": "per_country_P5_P95_linear",
        "R_P5": round(R_P5, 4),
        "R_P95": round(R_P95, 4),
        "task_id": 461,
        "task_reference": "Task #461 (22 Jul 2026) — semantic shift: band label = within-country ranking not absolute R",
    }
    data["fleet_summary"] = fleet
    data["regions"] = compute_regional_summary(substations)

    # ── diagnose-only exits here without writing ──────────────────────
    if diagnose_only:
        log.info(f"[{slug}] DIAGNOSE-ONLY — no write")
        return _build_audit_dict(slug, n, before_bands, after_bands, pre_R_P5, pre_R_P95, R_P5, R_P95)

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
        return _build_audit_dict(slug, n, before_bands, after_bands, pre_R_P5, pre_R_P95, R_P5, R_P95)

    # ── write back ────────────────────────────────────────────────────
    log.info(f"[{slug}] writing ssi-data.json (may re-shard if > 90.0 MB)...")
    write_ssi_data(data, ssi_path)
    log.info(f"[{slug}] saved. total {time.time()-t0:.1f}s")

    return _build_audit_dict(slug, n, before_bands, after_bands, pre_R_P5, pre_R_P95, R_P5, R_P95)


def _build_audit_dict(slug, n, before, after, pre_p5, pre_p95, p5, p95):
    return {
        "country": slug,
        "n_substations": n,
        "R_P5": round(p5, 4) if p5 is not None else None,
        "R_P95": round(p95, 4) if p95 is not None else None,
        "R_span": round(p95 - p5, 4) if (p5 is not None and p95 is not None) else None,
        "bands_before_absolute": before,
        "bands_after_normalised": after,
        "band_delta_pct": {
            b: round((after.get(b, 0) - before.get(b, 0)) / n * 100, 2)
            for b in ["Low", "Medium", "High", "Critical", "Extreme", "Unclassified"]
        },
    }


def _print_report(audit: dict):
    """Print a human-readable band-shift table."""
    n = audit["n_substations"]
    print(f"\n─── {audit['country']} ({n:,} subs) ───")
    print(f"  R_P5={audit['R_P5']} R_P95={audit['R_P95']} span={audit['R_span']}")
    print(f"  Band distribution:")
    print(f"    Band          BEFORE (abs)          AFTER (norm)          Delta")
    for b in ["Low", "Medium", "High", "Critical", "Extreme", "Unclassified"]:
        before = audit["bands_before_absolute"].get(b, 0)
        after = audit["bands_after_normalised"].get(b, 0)
        delta = audit["band_delta_pct"].get(b, 0)
        arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
        print(f"    {b:12s}  {before:>7,} ({before/n*100:5.1f}%)  {arrow}  "
              f"{after:>7,} ({after/n*100:5.1f}%)  delta={delta:+.2f}%")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", nargs="?", help="country slug (e.g. spain)")
    ap.add_argument("--wave4-post-rbase-fix", action="store_true",
                    help="run against all 8 Wave 4 R_base-fix countries")
    ap.add_argument("--all-countries", action="store_true",
                    help="run against all 39 cohort countries (advanced)")
    ap.add_argument("--dry-run", action="store_true",
                    help="compute + report but don't write ssi-data.json")
    ap.add_argument("--diagnose-only", action="store_true",
                    help="print P5/P95 + band shift table without writing")
    args = ap.parse_args()

    # Resolve target list
    if args.wave4_post_rbase_fix:
        targets = WAVE4_POST_RBASE_FIX
    elif args.all_countries:
        # Read from intelligence/countries.json per KB §57 (single source of truth)
        countries_path = REPO_ROOT / "intelligence" / "countries.json"
        if not countries_path.exists():
            log.error("intelligence/countries.json not found — required for --all-countries")
            sys.exit(2)
        cohort = json.loads(countries_path.read_text())
        targets = cohort.get("slugs", [])
        if not targets:
            log.error("intelligence/countries.json has no 'slugs' key")
            sys.exit(2)
    elif args.slug:
        targets = [args.slug]
    else:
        ap.error("must pass a slug OR --wave4-post-rbase-fix OR --all-countries")

    all_audits = []
    for slug in targets:
        try:
            audit = process_country(slug, dry_run=args.dry_run, diagnose_only=args.diagnose_only)
            _print_report(audit)
            all_audits.append(audit)
        except Exception as e:  # noqa: BLE001
            log.error(f"[{slug}] FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Write consolidated audit report
    if all_audits:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        report_path = Path.home() / f"normalise_bands_audit_{ts}.json"
        report_path.write_text(json.dumps({
            "task_id": 461,
            "run_timestamp_utc": ts,
            "mode": "diagnose-only" if args.diagnose_only else ("dry-run" if args.dry_run else "applied"),
            "n_countries": len(all_audits),
            "audits": all_audits,
        }, indent=2))
        print(f"\n✓ Consolidated audit report: {report_path}")


if __name__ == "__main__":
    main()
