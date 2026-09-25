#!/usr/bin/env python3
"""
SSI Archive Retention — opt-in cleanup of old archive/YYYY-MM/ folders.

By default lists what would be deleted and exits (dry-run). Pass --apply to
actually remove folders. Retention defaults to 12 months; override with
--keep-months N.

The _logs/ folder is preserved regardless — it is small and useful for
post-hoc diagnostics.

Usage:
  python3 scripts/archive-retention.py                 # dry run, 12 months
  python3 scripts/archive-retention.py --keep-months 6
  python3 scripts/archive-retention.py --apply

Not wired into the monthly workflow on purpose — retention policy should be
a deliberate human decision, run manually when git repo weight warrants it.
"""
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ARCHIVE_DIR = Path("archive")
PROTECTED = {"_logs"}  # folders never removed
MONTH_RE_LEN = 7  # 'YYYY-MM'


def months_between(a: str, b: str) -> int:
    """Return (b - a) in whole months, both as 'YYYY-MM' strings."""
    ay, am = int(a[:4]), int(a[5:7])
    by, bm = int(b[:4]), int(b[5:7])
    return (by - ay) * 12 + (bm - am)


def iter_month_folders():
    if not ARCHIVE_DIR.exists():
        return
    for child in sorted(ARCHIVE_DIR.iterdir()):
        if not child.is_dir():
            continue
        if child.name in PROTECTED:
            continue
        if len(child.name) != MONTH_RE_LEN or child.name[4] != '-':
            continue
        try:
            int(child.name[:4]); int(child.name[5:7])
        except ValueError:
            continue
        yield child


def main():
    p = argparse.ArgumentParser(description="Prune old archive/YYYY-MM/ folders.")
    p.add_argument("--keep-months", type=int, default=12,
                   help="Retain this many most-recent months (default: 12).")
    p.add_argument("--apply", action="store_true",
                   help="Actually delete. Default is a dry-run listing.")
    args = p.parse_args()

    current_ym = datetime.utcnow().strftime("%Y-%m")
    folders = list(iter_month_folders())
    if not folders:
        print(f"No month folders found under {ARCHIVE_DIR}/ — nothing to do.")
        return 0

    to_keep, to_remove = [], []
    for folder in folders:
        age = months_between(folder.name, current_ym)
        (to_remove if age >= args.keep_months else to_keep).append((folder, age))

    print(f"Archive retention — keep last {args.keep_months} months (current: {current_ym})")
    print(f"  Total folders: {len(folders)}")
    print(f"  Keeping:  {len(to_keep)}")
    print(f"  Pruning:  {len(to_remove)}")
    print()

    if not to_remove:
        print("Nothing to prune.")
        return 0

    for folder, age in to_remove:
        size_mb = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"  {'REMOVE' if args.apply else 'WOULD REMOVE'} {folder} ({age} months old, {size_mb:.1f} MB)")

    if not args.apply:
        print()
        print("Dry run. Pass --apply to actually delete.")
        return 0

    removed_bytes = 0
    for folder, _age in to_remove:
        size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        shutil.rmtree(folder)
        removed_bytes += size
        print(f"  Removed {folder}")

    print()
    print(f"Pruned {len(to_remove)} folders — freed {removed_bytes / (1024 * 1024):.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
