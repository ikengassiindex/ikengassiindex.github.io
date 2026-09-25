#!/usr/bin/env python3
"""
check_page_ids.py — Discipline #16 (BPG Part XXXVIII, KB §71.10 / A1c).

Prevents A1c (HTML static fabrication) by enforcing that every country's
8 pages have a minimum count of `id="..."` attributes matching reference
canonical (HU or IS).

KOREA INCIDENT (May 29, 2026): initial inaugural deploy had intelligence.html
with 1 ID vs IS 77. Pages rendered EMPTY because renderer DOM hooks were
missing. Hotfix #1 (256 files, full rebuild from IS template) closed it.

This gate would have caught the regression at pre-flight, BEFORE deploy.

Usage:
  python3 scripts/check_page_ids.py <slug>            # check one country
  python3 scripts/check_page_ids.py --all             # all live countries
  python3 scripts/check_page_ids.py --strict          # exit 1 on any fail
  python3 scripts/check_page_ids.py --thresholds      # print expected mins

Reference baselines (measured across 13 live countries, IS/HU/KR canonical):
  Page                  Canonical  Threshold (catches KR 1-ID fab failure mode)
  intelligence.html     77         ≥40  (KR fab had 1; catches <50%)
  esg-report.html       16-17      ≥10
  index.html            20-26      ≥15
  regional.html         15         ≥10
  map.html              12         ≥8
  data.html             10         ≥6
  methodology.html      7          ≥5
  dno-dashboard.html    varies 0-40 (warn-only; structurally divergent)
"""
import re
import sys
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Minimum ID counts per page (calibrated against IS/HU/KR canonical, May 2026)
# Threshold = ~50% of canonical, catches the KR fab failure mode (1 ID vs 77)
MIN_IDS = {
    "intelligence.html":  40,  # canonical 77 — primary diagnostic page
    "esg-report.html":    10,  # canonical 16-17
    "index.html":         15,  # canonical 20-26 (DE outlier 20)
    "regional.html":      10,  # canonical 15
    "map.html":            8,  # canonical 12
    "data.html":           6,  # canonical 10
    "methodology.html":    5,  # canonical 7
    # dno-dashboard.html: skipped — natural variance 0-40 (italy 40, LU/BE 0)
}

PAGES = list(MIN_IDS.keys())

# Regex: id="..." or id='...'
ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def load_slugs():
    """Load country slugs from intelligence/countries.json (SoT)."""
    path = REPO_ROOT / "intelligence" / "countries.json"
    try:
        with open(path) as f:
            data = json.load(f)
        # countries.json format: {"countries": [{"slug": "...", ...}, ...]}
        if isinstance(data, dict) and "countries" in data:
            return [c["slug"] for c in data["countries"] if c.get("slug")]
        # Or {"slug1": {...}, "slug2": {...}}
        return list(data.keys())
    except Exception as e:
        print(f"WARN: could not load countries.json ({e}); falling back to directory scan", file=sys.stderr)
        # Fallback: scan for directories containing intelligence.html
        return sorted([
            d.name for d in REPO_ROOT.iterdir()
            if d.is_dir() and (d / "intelligence.html").exists()
        ])


def count_ids(filepath):
    """Count unique id attributes in an HTML file. Returns -1 for deliberately
    pre-launch locked pages (excluded from threshold check)."""
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            html = f.read()
    except FileNotFoundError:
        return None
    # Skip pre-launch locked-card templates (Greenland, future pre-launch countries)
    if "locked-card" in html and ("Coming" in html or "Launching" in html or "pending" in html):
        return -1
    ids = ID_RE.findall(html)
    return len(set(ids))  # count UNIQUE IDs


def is_skipped(count):
    """Pre-launch locked pages return -1; treat as PASS."""
    return count == -1


def check_country(slug):
    """Run ID-count check on all 8 pages for one country. Returns (passes, fails, missing)."""
    passes, fails, missing = [], [], []
    for page in PAGES:
        path = REPO_ROOT / slug / page
        count = count_ids(path)
        threshold = MIN_IDS[page]
        if count is None:
            missing.append((slug, page))
        elif count == -1:
            # Pre-launch locked-card template — treat as PASS (deliberately not full thin-shell yet)
            passes.append((slug, page, "locked", threshold))
        elif count < threshold:
            fails.append((slug, page, count, threshold))
        else:
            passes.append((slug, page, count, threshold))
    return passes, fails, missing


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]

    if not args:
        print(__doc__.split("Usage:")[0].strip())
        print("\nUsage: python3 scripts/check_page_ids.py <slug>|--all|--thresholds [--strict]")
        sys.exit(0)

    if args[0] == "--thresholds":
        print("Minimum ID counts per page (D#16 — A1c prevention):")
        for page, n in MIN_IDS.items():
            print(f"  {page:25}  ≥ {n} IDs")
        sys.exit(0)

    if args[0] == "--all":
        slugs = load_slugs()
    else:
        slugs = [args[0]]

    print(f"check_page_ids.py — Discipline #16 — checking {len(slugs)} countries × {len(PAGES)} pages")
    print()

    all_fails = []
    all_missing = []
    total_pass = 0
    total_fail = 0
    for slug in slugs:
        passes, fails, missing = check_country(slug)
        total_pass += len(passes)
        total_fail += len(fails)
        if fails or missing:
            status = "FAIL"
            print(f"  {status} {slug}: {len(fails)} fails, {len(missing)} missing, {len(passes)} pass")
            for _, page, count, thresh in fails:
                print(f"    FAIL: {page} → {count} IDs (< {thresh})  [A1c regression]")
            for _, page in missing:
                print(f"    MISSING: {page}")
            all_fails.extend(fails)
            all_missing.extend(missing)
        else:
            print(f"  PASS {slug}: {len(passes)} pages all ≥ threshold")

    print()
    print(f"Total: {total_pass} pass / {total_fail} fail / {len(all_missing)} missing")

    if all_fails or all_missing:
        if strict:
            print("\nSTRICT MODE: exit 1 (deploy would be blocked)")
            sys.exit(1)
        else:
            print("\n(non-strict — would warn but not block)")
            sys.exit(0)
    else:
        print("\nAll checks PASSED — D#16 gate green")
        sys.exit(0)


if __name__ == "__main__":
    main()
