#!/usr/bin/env python3
"""
check_nav_slug.py — Discipline #18 (BPG Part XXXVIII, KB §71.13 / A1e).

Prevents A1e (SoT regeneration gap) by verifying that every slug in
intelligence/countries.json is ALSO present in nav.js (which is
auto-generated from countries.json by scripts/generate_nav_data.py).

KOREA INCIDENT (May 29, 2026): Step 6 added 'korea' to countries.json
but scripts/generate_nav_data.py was NOT run. nav.js was missing 'korea'
in 3 sections (SSI_COUNTRY_SLUGS + SSI_COUNTRY_LABELS + SSI_COUNTRY_STATS_DEFAULT).
Result: Korean pages showed "KOREA" word instead of 🇰🇷 flag emoji, and
Ikenga logo failed to load (404 from /korea/ikenga-logo.png).

Hotfix #4 (ebee75db) patched nav.js manually. This gate would have caught
the regression at Step 6 pre-flight.

Usage:
  python3 scripts/check_nav_slug.py             # check all slugs
  python3 scripts/check_nav_slug.py --strict    # exit 1 on any missing
  python3 scripts/check_nav_slug.py <slug>      # check specific slug

Three nav.js sections checked per slug:
  1. SSI_COUNTRY_SLUGS array        — controls SSI_BASE/path detection (logo path)
  2. SSI_COUNTRY_LABELS dict        — controls flag emoji + country name display
  3. SSI_COUNTRY_STATS_DEFAULT dict — controls footer stats default

Missing any of the 3 → A1e regression.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NAV_PATH = REPO_ROOT / "nav.js"
COUNTRIES_PATH = REPO_ROOT / "intelligence" / "countries.json"

# Patterns to extract the 3 sections from nav.js
SLUGS_RE = re.compile(r"SSI_COUNTRY_SLUGS\s*=\s*\[([^\]]+)\]", re.DOTALL)
LABELS_RE = re.compile(r"SSI_COUNTRY_LABELS\s*=\s*\{([^}]+)\}", re.DOTALL)
STATS_RE = re.compile(r"SSI_COUNTRY_STATS_DEFAULT\s*=\s*\{([^}]+)\}", re.DOTALL)


def load_countries_slugs():
    """Load slugs from intelligence/countries.json (SoT)."""
    with open(COUNTRIES_PATH) as f:
        data = json.load(f)
    if isinstance(data, dict) and "countries" in data:
        return [c["slug"] for c in data["countries"] if c.get("slug")]
    return list(data.keys())


def parse_nav_sections():
    """Extract the 3 dict/array contents from nav.js."""
    if not NAV_PATH.exists():
        print(f"FATAL: nav.js not found at {NAV_PATH}", file=sys.stderr)
        sys.exit(2)
    with open(NAV_PATH) as f:
        nav = f.read()

    # Extract array content
    slugs_match = SLUGS_RE.search(nav)
    slugs_in_nav = set()
    if slugs_match:
        # Extract quoted strings from array content
        for m in re.finditer(r"['\"]([a-z0-9-]+)['\"]", slugs_match.group(1)):
            slugs_in_nav.add(m.group(1))

    # Extract LABELS dict keys
    labels_match = LABELS_RE.search(nav)
    labels_in_nav = set()
    if labels_match:
        for m in re.finditer(r"['\"]([a-z0-9-]+)['\"]\s*:", labels_match.group(1)):
            labels_in_nav.add(m.group(1))

    # Extract STATS_DEFAULT dict keys
    stats_match = STATS_RE.search(nav)
    stats_in_nav = set()
    if stats_match:
        for m in re.finditer(r"['\"]([a-z0-9-]+)['\"]\s*:", stats_match.group(1)):
            stats_in_nav.add(m.group(1))

    return slugs_in_nav, labels_in_nav, stats_in_nav


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    target_slug = args[0] if args else None

    expected_slugs = set(load_countries_slugs())
    slugs_in_nav, labels_in_nav, stats_in_nav = parse_nav_sections()

    if target_slug:
        if target_slug not in expected_slugs:
            print(f"WARN: {target_slug} not in countries.json — skipping check")
            sys.exit(0)
        expected_slugs = {target_slug}

    print(f"check_nav_slug.py — Discipline #18 — checking {len(expected_slugs)} slugs against nav.js sections")
    print()

    missing_slugs = expected_slugs - slugs_in_nav
    missing_labels = expected_slugs - labels_in_nav
    missing_stats = expected_slugs - stats_in_nav

    all_missing = missing_slugs | missing_labels | missing_stats

    if not all_missing:
        print(f"PASS: all {len(expected_slugs)} slugs present in all 3 nav.js sections")
        sys.exit(0)

    print(f"FAIL: {len(all_missing)} slugs have at least one missing entry in nav.js")
    for slug in sorted(all_missing):
        in_slugs = "✓" if slug in slugs_in_nav else "✗"
        in_labels = "✓" if slug in labels_in_nav else "✗"
        in_stats = "✓" if slug in stats_in_nav else "✗"
        print(f"  {slug:18}  SLUGS:{in_slugs}  LABELS:{in_labels}  STATS:{in_stats}  [A1e regression]")

    print()
    print(f"Counts: SLUGS array {len(slugs_in_nav)} / LABELS dict {len(labels_in_nav)} / STATS_DEFAULT dict {len(stats_in_nav)} / countries.json {len(expected_slugs)}")
    print()
    print("Remediation: run `python3 scripts/generate_nav_data.py` then commit nav.js.")

    if strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
