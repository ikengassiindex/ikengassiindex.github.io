#!/usr/bin/env python3
"""
Discipline #30 — Required-files presence pre-flight gate.

For every country listed in intelligence/countries.json['slugs'], asserts that
each REQUIRED file is present in the country folder. Catches the regression
class that surfaced 2026-06-04 (commit 5d3efa6a session): the March DACH
rollback (76c9f4ac, KB §56) deleted germany/ssi-metadata.js and
switzerland/ssi-metadata.js, and the loss went undetected for ~3 months
because no pre-flight gate ever asserted file presence.

The check is structural — file exists or not. Content validity is the job
of D#3 (inline-JS parse), D#14 (canonical schema), D#16 (page IDs), etc.

Files classified as REQUIRED (page-breaking-if-missing) vs OPTIONAL
(map-only or footer-only):

REQUIRED (breaks intelligence/index/regional/map render):
  - intelligence.html
  - ssi-metadata.js         ← the file that surfaced this discipline
  - ssi-data.json
  - grid-geo.json

OPTIONAL (map.html overlay only, or version-history footer):
  - bounds.json             ← map-only; FR/IT/ES/UK render without it
  - versions.json           ← footer-history only

Usage:
  python3 scripts/check_required_files.py                  # all countries
  python3 scripts/check_required_files.py <slug>           # single country
  python3 scripts/check_required_files.py --strict         # exit 1 if any OPTIONAL missing too

Exits 0 if all REQUIRED files present for every checked country.
Exits 1 if any REQUIRED file is missing (or any OPTIONAL with --strict).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)

REQUIRED_FILES = [
    "intelligence.html",
    "ssi-metadata.js",
    "ssi-data.json",
    "grid-geo.json",
]
OPTIONAL_FILES = [
    "bounds.json",
    "versions.json",
    "esg-report.html",
    "index.html",
    "regional.html",
    "map.html",
    "data.html",
    "methodology.html",
]


def check_country(slug, strict=False):
    missing_required = [f for f in REQUIRED_FILES if not os.path.exists(f"{slug}/{f}")]
    missing_optional = [f for f in OPTIONAL_FILES if not os.path.exists(f"{slug}/{f}")]
    return missing_required, missing_optional


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if not a.startswith("--")]

    with open("intelligence/countries.json") as f:
        countries = json.load(f)
    all_slugs = countries["slugs"]

    if args:
        slugs = [a for a in args if a in all_slugs]
        unknown = [a for a in args if a not in all_slugs]
        if unknown:
            print(f"WARN: unknown slug(s): {unknown}", file=sys.stderr)
        if not slugs:
            print("ERROR: no valid slug provided", file=sys.stderr)
            return 2
    else:
        slugs = all_slugs

    total_req_missing = 0
    total_opt_missing = 0
    fail_countries = []

    print(f"D#30 file-presence check — {len(slugs)} countries × {len(REQUIRED_FILES)} required files\n")
    for slug in slugs:
        req, opt = check_country(slug)
        if req:
            fail_countries.append(slug)
            print(f"  FAIL {slug:18s} missing REQUIRED: {', '.join(req)}")
            total_req_missing += len(req)
        elif opt and strict:
            fail_countries.append(slug)
            print(f"  WARN {slug:18s} missing optional: {', '.join(opt)}")
            total_opt_missing += len(opt)

    print()
    if total_req_missing == 0 and (total_opt_missing == 0 or not strict):
        print(f"  PASS — all {len(slugs)} countries have all {len(REQUIRED_FILES)} required files")
        if not strict:
            opt_short = sum(1 for s in slugs if check_country(s)[1])
            if opt_short:
                print(f"  (note: {opt_short} countries missing optional files; run with --strict to flag)")
        return 0

    print(f"  FAIL — {len(fail_countries)} countries with missing files")
    print(f"         {total_req_missing} REQUIRED + {total_opt_missing} optional missing")
    print()
    print("  Required-file regression discipline (KB §93): this class of bug")
    print("  caused germany + switzerland intelligence pages to be broken in")
    print("  production from March 2026 to June 2026 (3 months undetected).")
    print("  Add this gate to preflight.sh and as a pre-deploy assertion.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
