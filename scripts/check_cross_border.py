#!/usr/bin/env python3
"""
check_cross_border.py — Discipline #36 (KB §72.1, 18 June 2026).

Cross-border substation enforcement gate. Each country's substations in
{country}/ssi-data.json must lie within {country}/bounds.json's national
polygon (with a configurable boundary-precision tolerance, default 100m).

REGRESSION HISTORY:
  18 Jun 2026 cross-border audit (operator-triggered "is Austria leaking?"):
    - 🚨 SEVERE  ≥30% outside: Greenland 86.5%, Canada 74.4%, Austria 47.5%
    - ⚠ MODERATE 10-30%:        Norway 23.4%, Mexico 22.5%, UK 19.2%, Chile 12.1%
    - ⚪ MINOR     1-10%:         13 countries
    - ✅ CLEAN     <1%:           14 countries (incl. Italy 0.09% post-heal)
    - ⚙ TOPOLOGY  invalid:       Belgium, Costa Rica, Iceland, Japan
  Aggregate: ≈17% of all 174,046 published substations were outside their
  country canonical's polygon — equivalent to ~24,650 misattributed
  substations cohort-wide.

  Austria detail (worst case the operator surfaced):
    668 of 1,406 substations were Bavarian / Slovenian / South-Tyrolean /
    Engadin substations misattributed to Austrian Bundesländer. Name
    evidence (Föhring, Augsburg, Freising, Hudi kot Trpotek, RTP Pekre,
    Fleres FS, Ova Spin, Filisur) is unambiguous — these are foreign
    substations ingested by a bounding-box overshoot at the upstream
    source step.

CHECK LOGIC:
  For each country with a valid bounds.json:
    1. Load the union of all sub-national polygons.
    2. Heal self-intersections via shapely buffer(0).
    3. For each substation, test (lat, lon) is inside the polygon (with
       optional tolerance buffer for coastline precision).
    4. Report inside / outside / missing-coords counts.
    5. Fail the gate if outside% exceeds threshold (default 5%).

THRESHOLDS:
  - Default fail threshold: 5% outside (catches Austrian-class drift while
    tolerating coastline-precision noise like Italy's 0.09%).
  - Default tolerance: 100m boundary buffer (standard cadastral tolerance).
  - Both configurable per-invocation. CI should use the defaults.

USAGE:
  python3 scripts/check_cross_border.py                       # all countries (warn only)
  python3 scripts/check_cross_border.py austria               # one country
  python3 scripts/check_cross_border.py --all --strict        # fail-on-any-violation
  python3 scripts/check_cross_border.py --all --threshold 1.0 # tight threshold (1%)
  python3 scripts/check_cross_border.py --tolerance-km 0.5    # 500m tolerance buffer
  python3 scripts/check_cross_border.py --json out.json       # machine-readable report

EXIT CODES:
  0   OK — all countries below threshold (or no --strict / no findings)
  1   In --strict mode: at least one country exceeded the threshold, OR at
      least one country could not be evaluated at all (a gate that cannot
      evaluate a country does not pass)
  2   Argument or environment error

CI INTEGRATION:
  Wire after every monthly-refresh.yml cron run. Recommended block:

      - name: Cross-border polygon check
        run: |
          pip install shapely
          python3 scripts/check_cross_border.py --all --strict --json \\
            audit/cross-border-$(date -u +%Y-%m-%d).json

  The JSON report is suitable for diffing against the previous report —
  any country that regressed past threshold gets flagged for manual review
  before the refresh ships.

COMPANION FIX:
  The point-in-polygon helpers live in scripts/pipeline/utils/geo.py
  alongside the existing geo utilities. To filter substations at ingestion
  time (eliminating Austrian-class drift at source), call:

      from scripts.pipeline.utils.geo import (
          load_country_polygon, filter_by_country_polygon,
      )
      poly = load_country_polygon(country)
      kept, rejected = filter_by_country_polygon(subs, poly)

  See CROSS_BORDER_SUBSTATION_AUDIT_20260618.md for the original audit
  evidence + four-mode failure classification.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ─── Country slug list, single source of truth ──────────────────────────────
def load_country_slugs() -> list[str]:
    """Read intelligence/countries.json — the project-wide source of truth."""
    countries_json = REPO_ROOT / "intelligence" / "countries.json"
    if not countries_json.exists():
        # Fallback to filesystem scan if intelligence/countries.json is missing
        return sorted([
            d.name for d in REPO_ROOT.iterdir()
            if d.is_dir() and (d / "ssi-data.json").exists()
        ])
    with open(countries_json) as f:
        meta = json.load(f)
    return meta.get("slugs", [])


# ─── Severity classification (mirrors the audit memo) ────────────────────────
def severity(pct_out: float) -> str:
    """Map outside% to severity badge for human-readable reports."""
    if pct_out >= 30:
        return "🚨 SEVERE"
    if pct_out >= 10:
        return "⚠ MODERATE"
    if pct_out >= 1:
        return "⚪ MINOR"
    return "✅ CLEAN"


# ─── Main check loop ────────────────────────────────────────────────────────
def run_check(slugs: list[str], tolerance_km: float, threshold_pct: float,
              json_out: Path | None = None) -> tuple[int, dict]:
    """Returns (n_violations, full_report_dict)."""

    # Lazy import — only pay shapely's import cost when actually checking
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.pipeline.utils.geo import cross_border_audit
    except ImportError as e:
        print(f"FATAL: cannot import cross_border_audit helper: {e}",
              file=sys.stderr)
        print("Install shapely: pip install -r scripts/pipeline/requirements.txt",
              file=sys.stderr)
        sys.exit(2)

    print(f"\n{'Country':<18} {'Total':>7} {'Inside':>7} {'Outside':>8} "
          f"{'% Out':>7} {'Max km':>8} {'Severity':<14}")
    print("-" * 80)

    per_country = []
    violations = 0
    for slug in slugs:
        try:
            res = cross_border_audit(slug, repo_root=REPO_ROOT,
                                     tolerance_km=tolerance_km)
        except FileNotFoundError as e:
            res = {
                "country": slug, "skipped": True,
                "skip_reason": f"ssi-data.json missing ({e})",
                "total": 0, "inside": 0, "outside": 0, "missing_coords": 0,
                "pct_outside": 0.0, "tolerance_km": tolerance_km,
                "max_dist_km": 0.0, "outliers_sample": [],
            }
        except Exception as e:
            res = {
                "country": slug, "skipped": True,
                "skip_reason": f"audit failure: {type(e).__name__}: {e}",
                "total": 0, "inside": 0, "outside": 0, "missing_coords": 0,
                "pct_outside": 0.0, "tolerance_km": tolerance_km,
                "max_dist_km": 0.0, "outliers_sample": [],
            }

        if res["skipped"]:
            print(f"{slug:<18} {'—':>7} {'—':>7} {'—':>8} {'—':>7} "
                  f"{'—':>8} {'⏭ SKIPPED':<14}  ({res['skip_reason']})")
        else:
            sev = severity(res["pct_outside"])
            res["severity"] = sev
            print(f"{slug:<18} {res['total']:>7} {res['inside']:>7} "
                  f"{res['outside']:>8} {res['pct_outside']:>6.2f}% "
                  f"{res['max_dist_km']:>7.1f} {sev:<14}")
            if res["pct_outside"] > threshold_pct:
                violations += 1

        per_country.append(res)

    report = {
        "tool": "check_cross_border.py",
        "discipline": "#36",
        "kb_section": "§72.1",
        "tolerance_km": tolerance_km,
        "threshold_pct": threshold_pct,
        "per_country": per_country,
        "violation_count": violations,
        "skipped_count": sum(1 for r in per_country if r.get("skipped")),
    }

    print()
    print(f"=== SUMMARY ===")
    print(f"  Countries checked:         {len(slugs)}")
    print(f"  Countries skipped:         {sum(1 for r in per_country if r.get('skipped'))}")
    print(f"  Countries violating ({threshold_pct}% outside): {violations}")
    print()

    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  JSON report written to: {json_out}")
        print()

    return violations, report


def main():
    parser = argparse.ArgumentParser(
        description="Cross-border substation enforcement gate (Discipline #36).",
        epilog="See module docstring for full regression history + thresholds.",
    )
    parser.add_argument(
        "country", nargs="?",
        help="Country slug. Omit + use --all for the whole cohort.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Check every country in intelligence/countries.json::slugs.",
    )
    parser.add_argument(
        "--tolerance-km", type=float, default=None,
        help="Boundary-precision tolerance in km. If omitted, per-country "
             "override from cross_border_tolerances.json is used (or 0.1 "
             "/ 100m default). Set explicitly to 0.0 for strict inside-only.",
    )
    parser.add_argument(
        "--threshold", type=float, default=5.0,
        help="Pass threshold for %% outside. Default 5.0%%. With --strict, "
             "any country exceeding this fails the gate.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 1 if any country exceeds --threshold. Without --strict, "
             "the check is informational (exit 0 regardless).",
    )
    parser.add_argument(
        "--json", type=Path, default=None,
        help="Optional path for machine-readable JSON report (CI consumption).",
    )
    args = parser.parse_args()

    if args.country and args.all:
        print("ERROR: pass either a country slug OR --all, not both.",
              file=sys.stderr)
        sys.exit(2)

    if args.country:
        slugs = [args.country]
    elif args.all:
        slugs = load_country_slugs()
    else:
        slugs = load_country_slugs()  # Same as --all but no failure mode
        # Without --strict the script is informational

    if not slugs:
        print("ERROR: no countries to check.", file=sys.stderr)
        sys.exit(2)

    violations, report = run_check(
        slugs,
        tolerance_km=args.tolerance_km,
        threshold_pct=args.threshold,
        json_out=args.json,
    )

    # A gate that cannot evaluate a country must not report a pass. Without
    # this branch the summary reads "0 countries violating" out of 0 actually
    # checked, and a pass by absence of evidence is indistinguishable from a
    # pass. Skips are informational without --strict, and fatal with it.
    skipped = report.get("skipped_count", 0)
    if args.strict and skipped > 0:
        print(f"FAIL: {skipped} country/countries could not be evaluated; "
              f"--strict does not pass on unevaluated countries.",
              file=sys.stderr)
        for r in report["per_country"]:
            if r.get("skipped"):
                print(f"  - {r['country']}: {r.get('skip_reason')}",
                      file=sys.stderr)
        sys.exit(1)

    if args.strict and violations > 0:
        print(f"FAIL: {violations} countries exceed {args.threshold}% threshold "
              f"under --strict mode.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
