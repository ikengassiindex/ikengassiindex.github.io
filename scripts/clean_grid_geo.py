#!/usr/bin/env python3
"""
clean_grid_geo.py — Discipline #36 grid-geo follow-up (18 June 2026 deep night).

After ssi-data.json remediation removes foreign substations from a country,
grid-geo.json still contains them — causing the map.html to render the
foreign substations as gray background dots even though they're not in
ssi-data.json. This script propagates the point-in-polygon filter to
grid-geo.json's 's' (substations), 'l' (lines), and 'a' (annotations)
sections.

Filtering rules:
  - 's' (substations dict keyed by ID): strict point-in-polygon test using
    per-country tolerance from cross_border_tolerances.json. Same logic as
    ssi-data.json filtering.
  - 'l' (lines list): keep lines where AT LEAST ONE endpoint is inside the
    polygon. This preserves cross-border transmission lines (which are real
    infrastructure connecting the country to neighbours) but drops lines
    that are fully outside.
  - 'a' (annotations dict keyed by substation ID): keep only keys that
    survive in the cleaned 's' dict.

Backups: original grid-geo.json is saved as
{country}/grid-geo.json.pre-remediate-{ISO}.backup.

USAGE:
  python3 scripts/clean_grid_geo.py austria --dry-run
  python3 scripts/clean_grid_geo.py austria
  python3 scripts/clean_grid_geo.py --all-remediated  # all 7 remediated countries

EXIT CODES:
  0   Cleanup completed (or --dry-run preview)
  1   No-op (country already clean)
  2   Argument/environment error
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Countries where ssi-data.json was remediated and grid-geo.json needs the
# same treatment (see CROSS_BORDER_SUBSTATION_AUDIT_20260618.md).
REMEDIATED_COUNTRIES = [
    "austria", "mexico", "norway", "uk", "france", "chile", "canada",
]


def clean_grid_geo(country, dry_run=False):
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.pipeline.utils.geo import (
        load_country_polygon, is_inside_country, load_country_tolerance,
    )

    print(f"\n=== Cleaning grid-geo.json for {country} ===")

    grid_path = REPO_ROOT / country / "grid-geo.json"
    if not grid_path.exists():
        print(f"  ⚠ {country}/grid-geo.json not found — skipped")
        return 1

    poly = load_country_polygon(country, repo_root=REPO_ROOT, heal_topology=True)
    if poly is None:
        print(f"  ⚠ {country}/bounds.json missing — skipped")
        return 1

    tolerance_km = load_country_tolerance(country, repo_root=REPO_ROOT)
    print(f"  tolerance: {tolerance_km} km")

    with open(grid_path) as f:
        g = json.load(f)

    n_subs_before = len(g.get("s", {}))
    n_lines_before = len(g.get("l", []))
    n_a_before = len(g.get("a", {}))

    print(f"  before: {n_subs_before} substations, {n_lines_before} lines, "
          f"{n_a_before} annotations")

    # 1) Filter substations
    kept_subs = {}
    removed_subs_keys = set()
    for k, v in g.get("s", {}).items():
        x = v.get("x")  # longitude
        y = v.get("y")  # latitude
        if x is None or y is None:
            kept_subs[k] = v
            continue
        inside, _ = is_inside_country(y, x, poly, tolerance_km=tolerance_km)
        if inside:
            kept_subs[k] = v
        else:
            removed_subs_keys.add(k)
    print(f"  's' (substations) kept: {len(kept_subs)} / {n_subs_before} "
          f"({len(removed_subs_keys)} removed)")

    # 2) Filter lines — keep if at least one endpoint inside
    kept_lines = []
    n_kept_inside_both = 0
    n_kept_one_endpoint = 0
    for line in g.get("l", []):
        path = line.get("p", [])
        if not path or len(path) < 2:
            kept_lines.append(line)
            continue
        # Check first + last endpoints (sufficient for cross-border detection)
        x0, y0 = path[0]
        x_end, y_end = path[-1]
        in0, _ = is_inside_country(y0, x0, poly, tolerance_km=tolerance_km)
        in1, _ = is_inside_country(y_end, x_end, poly, tolerance_km=tolerance_km)
        if in0 and in1:
            kept_lines.append(line)
            n_kept_inside_both += 1
        elif in0 or in1:
            # Cross-border line — keep (real international transmission)
            kept_lines.append(line)
            n_kept_one_endpoint += 1
        # else: both endpoints outside → drop
    print(f"  'l' (lines) kept: {len(kept_lines)} / {n_lines_before} "
          f"(both-inside: {n_kept_inside_both}, cross-border: {n_kept_one_endpoint})")

    # 3) Filter annotations — keep only keys that survive in s
    kept_a = {k: v for k, v in g.get("a", {}).items() if k in kept_subs}
    print(f"  'a' (annotations) kept: {len(kept_a)} / {n_a_before}")

    if dry_run:
        print("\n  DRY RUN — no files written.")
        return 0

    # Backup + write
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = REPO_ROOT / country / f"grid-geo.json.pre-clean-{ts}.backup"
    shutil.copy2(grid_path, backup_path)
    print(f"\n  ✓ Backed up original to: {backup_path.name}")

    g["s"] = kept_subs
    g["l"] = kept_lines
    g["a"] = kept_a

    with open(grid_path, "w") as f:
        json.dump(g, f, separators=(",", ":"))
    print(f"  ✓ Wrote cleaned grid-geo.json ({len(kept_subs)} substations, "
          f"{len(kept_lines)} lines)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Clean grid-geo.json to match remediated ssi-data.json.",
    )
    parser.add_argument("country", nargs="?", help="Country slug.")
    parser.add_argument("--all-remediated", action="store_true",
                        help="Process all 7 remediated countries.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing files.")
    args = parser.parse_args()

    if args.all_remediated and args.country:
        print("ERROR: pass either a country slug OR --all-remediated.", file=sys.stderr)
        sys.exit(2)

    if args.all_remediated:
        for c in REMEDIATED_COUNTRIES:
            clean_grid_geo(c, dry_run=args.dry_run)
        return

    if not args.country:
        print("ERROR: must pass a country slug or --all-remediated.", file=sys.stderr)
        sys.exit(2)

    sys.exit(clean_grid_geo(args.country, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
