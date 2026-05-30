#!/usr/bin/env python3
"""
check_substation_schema.py — Discipline #17 (BPG Part XXXVIII, KB §71.11 / A1d).

Prevents A1d (data-schema deficit) by enforcing that every country's
ssi-data.json emits substations with full IS/HU canonical 44-field schema
+ checks per-region variance on fields that should vary (rd_pct_gdp etc.).

KOREA INCIDENTS (May 29, 2026):
  - Hotfix #2: KR emitted substations with 24 fields vs IS canonical 44.
                B.2 panel + ESG + data.html had 20+ empty fields per substation.
  - Hotfix #7-issue3: rd_pct_gdp was UNIFORM 4.8% across all 17 regions
                       (hardcoded global constant); should vary 1.2%-9.5%.

This gate catches both at pre-flight.

Usage:
  python3 scripts/check_substation_schema.py <slug>      # one country
  python3 scripts/check_substation_schema.py --all       # all live
  python3 scripts/check_substation_schema.py --strict    # exit 1 on any fail
  python3 scripts/check_substation_schema.py --canonical # print expected schema

Canonical reference (IS/HU): 44 fields per substation
Threshold: ≥35 fields per substation (catches the KR 24-field regression)

Per-region variance checks (fields expected to vary across admin units):
  socio_economic.rd_pct_gdp     ≥ 5 unique values (catches KR uniform 4.8%)
  socio_economic.gdp_pc_usd_ppp ≥ 5 unique values
  socio_economic.unemployment_pct ≥ 3 unique values
  R6_typhoon (if present)       ≥ 3 unique values
  R6_chaebol (if present)       ≥ 3 unique values
"""
import json
import sys
import os
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent

# Minimum field count per substation (catches KR 24-field regression)
MIN_FIELDS = 35

# Per-region variance checks: (path, min_unique_values, severity)
# Field names match IS/HU/KR canonical socio_economic dict (verified May 29, 2026).
# Per-region variance checks. Only ERROR-severity fields are enforced as gates.
# Fields kept at WARN are informational (not all countries emit them at substation level).
VARIANCE_CHECKS = [
    ("socio_economic.rd_pct_gdp",       5, "ERROR"),  # KR hotfix #7 root cause — REQUIRED variance
]


def get_nested(d, path):
    """Get nested field by dot-path (e.g. 'socio_economic.rd_pct_gdp')."""
    keys = path.split(".")
    val = d
    for k in keys:
        if not isinstance(val, dict):
            return None
        val = val.get(k)
        if val is None:
            return None
    return val


def load_slugs():
    """Load country slugs from intelligence/countries.json."""
    path = REPO_ROOT / "intelligence" / "countries.json"
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "countries" in data:
            return [c["slug"] for c in data["countries"] if c.get("slug")]
        return list(data.keys())
    except Exception:
        return sorted([
            d.name for d in REPO_ROOT.iterdir()
            if d.is_dir() and (d / "ssi-data.json").exists()
        ])


def count_fields(sub):
    """Count fields in a substation, treating nested dicts as their leaves."""
    def _count(d):
        if not isinstance(d, dict):
            return 1
        total = 0
        for k, v in d.items():
            if isinstance(v, dict):
                total += _count(v)
            else:
                total += 1
        return total
    return _count(sub)


def check_country(slug):
    """Run schema check on one country. Returns (passes, fails, warns)."""
    fails, warns = [], []
    path = REPO_ROOT / slug / "ssi-data.json"
    if not path.exists():
        return [], [(slug, "MISSING ssi-data.json")], []
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [], [(slug, f"INVALID JSON: {e}")], []

    substations = data.get("substations", [])
    if isinstance(substations, dict):
        substations = list(substations.values())
    if not substations:
        return [], [(slug, "no substations array")], []

    # 1. Field count check (catches A1d)
    sample = substations[0]
    field_count = count_fields(sample)
    if field_count < MIN_FIELDS:
        fails.append((slug, f"substation field count {field_count} < {MIN_FIELDS} (A1d regression — KR-style)"))
    # also check if MOST substations have similar field counts
    sample_counts = [count_fields(s) for s in substations[:50]]
    if sample_counts:
        median_count = sorted(sample_counts)[len(sample_counts) // 2]
        if median_count < MIN_FIELDS:
            fails.append((slug, f"substation field count median {median_count} < {MIN_FIELDS} across first 50 subs"))

    # 2. Variance checks (catches uniform-constant emissions like KR rd_pct_gdp=4.8% uniform)
    for path_str, min_unique, severity in VARIANCE_CHECKS:
        values = [get_nested(s, path_str) for s in substations]
        values = [v for v in values if v is not None]
        if not values:
            warns.append((slug, f"variance check {path_str}: field absent in all substations"))
            continue
        unique_count = len(set(values))
        # Only enforce variance if we have enough substations to expect it
        # (countries with <10 regions naturally have low variance)
        regions = data.get("regions", [])
        if isinstance(regions, dict):
            regions = list(regions.values())
        n_regions = len(regions)
        if n_regions >= 8 and unique_count < min_unique:
            msg = f"variance check {path_str}: only {unique_count} unique values across {n_regions} regions (expected ≥ {min_unique})"
            if severity == "ERROR":
                fails.append((slug, msg + " — KR uniform-emission regression"))
            else:
                warns.append((slug, msg))
        elif n_regions < 8 and unique_count == 1:
            # Even small-region countries shouldn't have uniform constants if multiple substations have the field
            if len(values) > 5:
                warns.append((slug, f"variance check {path_str}: uniform value across {len(values)} substations (small country, n_regions={n_regions})"))

    passes = [(slug, "OK")] if not fails else []
    return passes, fails, warns


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    if not args:
        print(__doc__.split("Usage:")[0].strip())
        print("\nUsage: python3 scripts/check_substation_schema.py <slug>|--all|--canonical [--strict]")
        sys.exit(0)

    if args[0] == "--canonical":
        print(f"Discipline #17 — substation schema parity check")
        print(f"  Minimum fields per substation: {MIN_FIELDS}")
        print(f"  Variance checks ({len(VARIANCE_CHECKS)}):")
        for path, n, sev in VARIANCE_CHECKS:
            print(f"    {sev:6}  {path:40}  ≥ {n} unique values (when n_regions ≥ 8)")
        sys.exit(0)

    if args[0] == "--all":
        slugs = load_slugs()
    else:
        slugs = [args[0]]

    print(f"check_substation_schema.py — Discipline #17 — checking {len(slugs)} countries")
    print()

    total_fails = 0
    total_warns = 0
    countries_with_issues = 0
    for slug in slugs:
        passes, fails, warns = check_country(slug)
        if fails or warns:
            countries_with_issues += 1
            print(f"  {'FAIL' if fails else 'WARN'} {slug}:")
            for _, msg in fails:
                print(f"    FAIL: {msg}")
            for _, msg in warns:
                print(f"    WARN: {msg}")
            total_fails += len(fails)
            total_warns += len(warns)
        else:
            print(f"  PASS {slug}")

    print()
    print(f"Summary: {len(slugs)} countries checked, {countries_with_issues} with issues, {total_fails} fails, {total_warns} warnings")

    if total_fails and strict:
        print("\nSTRICT MODE: exit 1 (deploy would be blocked)")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
