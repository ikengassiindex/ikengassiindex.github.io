#!/usr/bin/env python3
"""
scripts/check_r3_variance.py — Discipline #29

R3_C_mult per-substation variance gate. Catches the DK/EE/GL/LV/LT-class defect
where each country's digital-twin scoring pipeline applies regional socio-economic
data uniformly to all substations in a region, producing R3_C_mult clustered at a
handful of discrete values (single value per admin region).

The defect class (Session 100 / KB §78 / Wave A hotfix #2):
  - Denmark:    4 unique R3_C_mult values across 2,451 substations (0.16% ratio)
  - Estonia:    4 unique R3 values across 614 substations (15 regions, single per region)
  - Greenland:  5 unique R3 values across 37 substations
  - Latvia:     4 unique R3 values across 1,219 substations
  - Lithuania:  4 unique R3 values across 505 substations

Effect: Section B.2 "Economic Impact by Business Fabric" on intelligence.html
dumps 100% of substations into a single tier because quartile-bucketing collapses
on tied values.

Reference: Session 100 fix applied hash-deterministic per-substation jitter at
±2.5% multiplicative — DK 4→823 / EE 4→447 / GL 5→37 / LV 4→694 / LT 4→394
unique values restored. KB §72 Phase 3b precedent (rd_pct_gdp jitter across
11 countries).

Thresholds (unique R3_C_mult values / total substations):
  - PASS: ratio >= 0.25     (≥25% unique — healthy spread)
  - WARN: 0.05 <= ratio < 0.25  (some clustering, may have legitimate ties from voltage-class groupings)
  - FAIL: ratio < 0.05      (severe discrete-clustering, B.2 tier display will break)

Special-case: countries with very small fleets (< 50 substations) get a
floor-based check instead of ratio-based: PASS if unique >= 25% × N OR
unique >= 8 (whichever is higher).

Usage:
    python3 scripts/check_r3_variance.py <slug>
    python3 scripts/check_r3_variance.py --all
    python3 scripts/check_r3_variance.py --all --strict   # exit 1 on FAIL

Exit codes:
    0 = PASS or only WARN
    1 = FAIL
"""
import json
import os
import sys
import glob
import argparse


def check_country(slug, repo_root="."):
    """Return dict with verdict + diagnostic stats for one country."""
    path = os.path.join(repo_root, slug, "ssi-data.json")
    if not os.path.exists(path):
        return {"slug": slug, "status": "EXEMPT", "reason": "no ssi-data.json"}

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return {"slug": slug, "status": "ERROR", "reason": str(e)[:80]}

    raw_subs = data.get("substations", [])
    if not raw_subs:
        return {"slug": slug, "status": "EXEMPT", "reason": "no substations"}

    # Handle compact array format
    if isinstance(raw_subs[0], list):
        fields = data.get("sub_fields", [])
        if not fields:
            return {"slug": slug, "status": "ERROR", "reason": "compact format without sub_fields"}
        try:
            mod_idx = fields.index("modifiers")
        except ValueError:
            return {"slug": slug, "status": "ERROR", "reason": "no modifiers field"}
        vals = []
        for arr in raw_subs:
            if mod_idx < len(arr) and isinstance(arr[mod_idx], dict):
                v = arr[mod_idx].get("R3_C_mult")
                if isinstance(v, (int, float)):
                    vals.append(round(v, 6))
    else:
        vals = []
        for s in raw_subs:
            v = s.get("modifiers", {}).get("R3_C_mult")
            if isinstance(v, (int, float)):
                vals.append(round(v, 6))

    n = len(vals)
    if n == 0:
        return {"slug": slug, "status": "EXEMPT", "reason": "no R3_C_mult values"}

    unique = len(set(vals))
    ratio = unique / n

    # Small-fleet floor: < 50 substations, require unique >= max(0.25*N, 8)
    # (the floor of 8 covers Greenland-sized cohorts where 25%-of-N is too few)
    if n < 50:
        floor = max(int(0.25 * n), 8)
        if unique >= floor:
            status = "PASS"
            reason = f"small fleet n={n}, unique={unique} >= floor({floor})"
        elif unique >= max(int(0.10 * n), 4):
            status = "WARN"
            reason = f"small fleet n={n}, unique={unique} < floor({floor}) but >= 10% or 4"
        else:
            status = "FAIL"
            reason = f"small fleet n={n}, unique={unique} too low"
    else:
        if ratio >= 0.25:
            status = "PASS"
            reason = f"unique={unique}/{n} = {ratio:.1%}"
        elif ratio >= 0.05:
            status = "WARN"
            reason = f"unique={unique}/{n} = {ratio:.1%} (some clustering)"
        else:
            status = "FAIL"
            reason = f"unique={unique}/{n} = {ratio:.1%} — severe discrete-clustering, B.2 tier display will break"

    return {
        "slug": slug,
        "status": status,
        "reason": reason,
        "n": n,
        "unique": unique,
        "ratio": ratio,
    }


def get_all_slugs(repo_root="."):
    """Return list of slugs from intelligence/countries.json."""
    p = os.path.join(repo_root, "intelligence", "countries.json")
    if not os.path.exists(p):
        # Fallback: scan top-level directories with ssi-data.json
        return sorted([
            os.path.basename(d) for d in glob.glob(os.path.join(repo_root, "*"))
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "ssi-data.json"))
        ])
    with open(p) as f:
        data = json.load(f)
    cs = data.get("countries", data) if isinstance(data, dict) else data
    return [c["slug"] if isinstance(c, dict) else c for c in cs]


def main():
    parser = argparse.ArgumentParser(description="Discipline #29 — R3_C_mult per-substation variance gate")
    parser.add_argument("slugs", nargs="*", help="Country slug(s) to check")
    parser.add_argument("--all", action="store_true", help="Check all countries from countries.json")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on FAIL (default: exit 0 on FAIL too)")
    parser.add_argument("--repo-root", default=".", help="Path to repo root (default: cwd)")
    args = parser.parse_args()

    if args.all:
        slugs = get_all_slugs(args.repo_root)
    elif args.slugs:
        slugs = args.slugs
    else:
        parser.print_help()
        return 1

    print(f"check_r3_variance.py — Discipline #29 — checking {len(slugs)} countries")
    print(f"  PASS: unique/n >= 0.25   WARN: 0.05 <= ratio < 0.25   FAIL: ratio < 0.05")
    print(f"  Small-fleet (n<50) floor: unique >= max(0.25*N, 8)")
    print()

    n_pass = n_warn = n_fail = n_exempt = n_error = 0
    fails = []
    for slug in slugs:
        r = check_country(slug, args.repo_root)
        if r["status"] == "PASS":
            n_pass += 1
            print(f"  ✓ PASS  {slug:<14} {r['reason']}")
        elif r["status"] == "WARN":
            n_warn += 1
            print(f"  ⚠ WARN  {slug:<14} {r['reason']}")
        elif r["status"] == "FAIL":
            n_fail += 1
            fails.append(slug)
            print(f"  ✗ FAIL  {slug:<14} {r['reason']}")
        elif r["status"] == "EXEMPT":
            n_exempt += 1
            print(f"  - EXEMPT {slug:<14} {r['reason']}")
        else:
            n_error += 1
            print(f"  ! ERROR {slug:<14} {r.get('reason', '?')}")

    print()
    print(f"Summary: {n_pass} PASS · {n_warn} WARN · {n_fail} FAIL · {n_exempt} exempt · {n_error} error")
    if fails:
        print(f"Failed: {' '.join(fails)}")

    if args.strict and n_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
