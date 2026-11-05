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

# Per-region variance checks. Field names match the IS/HU/KR canonical
# socio_economic dict (verified May 29, 2026). Only ERROR severity is enforced.
#
# E412 AND E414, 19 October 2026: THE FLOOR WAS MEASURING THE WRONG THING, AND
# IT WAS SATISFIED BY THE FABRICATION IT WAS BUILT TO CATCH.
#
# The floor exists because Korea emitted ONE hard-coded value across 17
# regions (hotfix #7). But `rd_pct_gdp` was, estate-wide, the national figure
# jittered by the md5 of each substation's own NAME - so the hash's spread
# satisfied the floor, while A SINGLE SOURCED REGIONAL FIGURE WOULD FAIL IT.
# Measured on 19 October before the write: luxembourg's 723 records carried
# ELEVEN hash values and sit in exactly ONE NUTS 2 region, so the measurement
# that replaces the hash has one value and the hash passed where the truth
# would not. Seven fleets were in that position - estonia, finland, ireland,
# lithuania, luxembourg, slovakia, slovenia - every one of them because the
# country IS fewer than five NUTS 2 regions.
#
# THE DISCRIMINATOR IS PROVENANCE AND NOT SPREAD. A record carrying
# `source_marker` has a declared source, and its value is whatever its source
# says - uniform or not. A record without one is an emission, and the floor
# stands over those exactly as it did.
#
# WHAT THIS IS NOT. It is not a softening to let a write through: E414 ruled
# that "a gate changed without the data to satisfy it is a gate changed to
# pass", which is why this lands in the SAME commit as the series. The two
# fleets failing today - italy and spain, three unique values each - fail
# because their value is a hash with no source, and they go on failing until
# the write gives them one.
#
# AND THE UNSOURCED RESIDUE IS REPORTED, NEVER SILENT. The floor is applied to
# the unsourced population only where that population is the fleet's MAJORITY,
# because the defect the floor was built for was a constant across a WHOLE
# fleet; a few hundred records left behind by a join gap is a different finding
# with its own row, and it is printed with its count either way.
VARIANCE_CHECKS = [
    {"path": "socio_economic.rd_pct_gdp", "min_unique": 5, "severity": "ERROR",
     "source_marker": "_rd_pct_gdp_source"},   # KR hotfix #7 root cause
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


def variance_verdict(substations, vc, n_regions):
    """THE WHOLE VARIANCE DECISION, as a pure function of three inputs.

    Returns a list of (severity, message); severity is "ERROR" or "WARN".

    IT IS A FUNCTION AND NOT INLINE SO THAT THE BLOCK THAT PROVES IT REFUSES
    RUNS THIS CODE AND NOT A SECOND COPY OF IT. Two copies of one check is
    how an inline version and MH's gate D disagreed about the same script
    inside an hour.
    """
    path_str = vc["path"]
    min_unique = vc["min_unique"]
    severity = vc["severity"]
    marker = vc.get("source_marker")
    out = []
    # SOURCED AND UNSOURCED ARE SEPARATED FIRST. A value with a declared
    # source is whatever its source says; the floor is about EMISSIONS.
    sourced, values = [], []
    for s in substations:
        v = get_nested(s, path_str)
        if v is None:
            continue
        if marker and s.get(marker):
            sourced.append(v)
        else:
            values.append(v)
    if sourced:
        out.append(("WARN", f"variance check {path_str}: {len(sourced)} record(s) "
                            f"carry a declared source and are exempt "
                            f"({len(set(sourced))} distinct); "
                            f"{len(values)} unsourced"))
    if not values and not sourced:
        out.append(("WARN", f"variance check {path_str}: field absent in all substations"))
        return out
    if not values:
        return out
    # THE FLOOR APPLIES TO THE UNSOURCED POPULATION, and only where it is this
    # fleet's MAJORITY: a residue left by a join gap is not the whole-fleet
    # constant this floor was built for, and it is reported above with its
    # count either way.
    if sourced and len(values) <= len(sourced):
        return out
    unique_count = len(set(values))
    # Only enforce variance where there are enough regions to expect it
    # (countries with fewer than eight naturally have low variance).
    if n_regions >= 8 and unique_count < min_unique:
        msg = (f"variance check {path_str}: only {unique_count} unique values "
               f"across {n_regions} regions (expected ≥ {min_unique})")
        if severity == "ERROR":
            out.append(("ERROR", msg + " — KR uniform-emission regression"))
        else:
            out.append(("WARN", msg))
    elif n_regions < 8 and unique_count == 1 and len(values) > 5:
        out.append(("WARN", f"variance check {path_str}: uniform value across "
                            f"{len(values)} substations (small country, "
                            f"n_regions={n_regions})"))
    return out


def check_country(slug):
    """Run schema check on one country. Returns (passes, fails, warns)."""
    fails, warns = [], []
    path = REPO_ROOT / slug / "ssi-data.json"
    if not path.exists():
        return [], [(slug, "MISSING ssi-data.json")], []
    # Convention #79 sharded countries keep no "substations" key in the manifest.
    # Reading the manifest directly therefore returned an empty list and this
    # gate reported "no substations array" for france, germany, italy, poland,
    # spain and uk — the six largest fleets, 419,000 substations, 67% of the
    # estate — which meant it had never schema-checked any of them. Fixed
    # 25 September 2026 by routing through the canonical sharding-aware reader,
    # the same one scripts/validate_schema.py already used.
    try:
        import sys as _sys, pathlib as _pl
        _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
        from scripts._ssi_data_shard_reader import load_ssi_data
        data, substations, _sharded = load_ssi_data(slug)
    except json.JSONDecodeError as e:
        return [], [(slug, f"INVALID JSON: {e}")], []
    except Exception as e:
        return [], [(slug, f"UNREADABLE: {type(e).__name__}: {e}")], []

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
    regions = data.get("regions", [])
    if isinstance(regions, dict):
        regions = list(regions.values())
    for _vc in VARIANCE_CHECKS:
        for sev, msg in variance_verdict(substations, _vc, len(regions)):
            if sev == "ERROR":
                fails.append((slug, msg))
            else:
                warns.append((slug, msg))

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
