#!/usr/bin/env python3
"""
SSI Index — Data file size sentinel.

Purpose: catch the indent=2 pretty-printing bloat class BEFORE push.  GitHub
enforces a hard 100 MB per-file limit; a Python one-liner that accidentally
re-serialises a per-country ssi-data.json with indent=2 can easily inflate
a 20 MB compact file into 120+ MB.  US ssi-data.json at 73.6 MB (compact)
was the trigger case — one accidental indent=2 rewrite would blow the GitHub
limit and require a force-push cleanup.

Usage:
    # Manual check
    python3 scripts/check_data_file_sizes.py
    python3 scripts/check_data_file_sizes.py --strict          # fail on WARN too
    python3 scripts/check_data_file_sizes.py --threshold 50    # custom MB threshold

    # As pre-commit hook (install once with):
    #   ln -sf ../../scripts/check_data_file_sizes.py .git/hooks/pre-commit
    #   chmod +x .git/hooks/pre-commit
    # Hook uses default 90 MB threshold + only checks files that git has staged.

    # CI:
    # Wired into .github/workflows/validate.yml as a matrix step.

Exit codes:
    0 = all files within threshold
    1 = one or more files over hard threshold (FAIL / block push)
    2 = one or more files in warning band + --strict flag (WARN → FAIL)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# GitHub's hard limit is 100 MB per file.  Our sentinel threshold is 90 MB to
# leave headroom for git-lfs / diff / packfile overhead + human reaction time.
DEFAULT_THRESHOLD_MB = 90.0

# Warning band starts at 60% of threshold — surfaces bloat trends early
WARN_FRACTION = 0.60


def format_size(bytes_val: int) -> str:
    return f'{bytes_val / (1024 * 1024):.1f} MB'


def scan_data_files(repo_root: Path, only_staged: bool = False) -> list[tuple[Path, int]]:
    """Return [(relative_path, size_bytes), ...] for all ssi-data.json + grid-geo.json.

    If only_staged is True, restrict to files that git has staged for commit
    (used by the pre-commit hook path).
    """
    if only_staged:
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
                capture_output=True, text=True, check=True, cwd=repo_root,
            )
            staged = set(result.stdout.strip().split('\n'))
        except (subprocess.CalledProcessError, FileNotFoundError):
            staged = set()
    else:
        staged = None

    matches: list[tuple[Path, int]] = []
    for country_dir in sorted(repo_root.iterdir()):
        if not country_dir.is_dir() or country_dir.name.startswith('.'):
            continue
        for filename in ('ssi-data.json', 'grid-geo.json'):
            fp = country_dir / filename
            if not fp.exists():
                continue
            rel = fp.relative_to(repo_root)
            if staged is not None and str(rel) not in staged:
                continue
            matches.append((rel, fp.stat().st_size))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD_MB,
                        help=f'Hard threshold in MB (default {DEFAULT_THRESHOLD_MB})')
    parser.add_argument('--strict', action='store_true',
                        help='Fail on WARN band (60%% of threshold) too')
    parser.add_argument('--only-staged', action='store_true',
                        help='Only check files staged for commit (git diff --cached)')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                        help='Repository root (default: cwd)')
    args = parser.parse_args()

    threshold_bytes = int(args.threshold * 1024 * 1024)
    warn_bytes = int(threshold_bytes * WARN_FRACTION)

    files = scan_data_files(args.repo_root.resolve(), only_staged=args.only_staged)
    if not files:
        print('No ssi-data.json / grid-geo.json files found (or none staged).')
        return 0

    fail: list[tuple[Path, int]] = []
    warn: list[tuple[Path, int]] = []

    max_len = max(len(str(rel)) for rel, _ in files)
    fmt_col = f'  {{:<{max_len}}}'

    print(f'SSI Index data file size sentinel')
    print(f'  Threshold: {args.threshold:.0f} MB (fail)  ·  Warn band: {args.threshold * WARN_FRACTION:.1f} MB')
    print(f'  Files checked: {len(files)}  ·  Scope: {"staged only" if args.only_staged else "full cohort"}')
    print()

    for rel, sz in sorted(files, key=lambda x: -x[1]):
        if sz > threshold_bytes:
            status = '❌ FAIL'
            fail.append((rel, sz))
        elif sz > warn_bytes:
            status = '⚠️  WARN'
            warn.append((rel, sz))
        else:
            status = '✅ OK'
        print(f'  {status}  {fmt_col.format(str(rel))}  {format_size(sz):>10}')

    print()

    if fail:
        print(f'❌ {len(fail)} file(s) exceed {args.threshold:.0f} MB — blocking push')
        print()
        print('Remediation:')
        print('  1. Verify the file is NOT accidentally indent=2 pretty-printed.')
        print('     Compact form: `json.dumps(data)` (no indent kwarg).')
        print('     Bloated form: `json.dumps(data, indent=2)`.')
        print('  2. If legitimately large, consider compression: coordinate precision')
        print('     rounding, polyline simplification, or null-field stripping.')
        print('     See scripts/optimise_grid_geo.py for polyline simplification.')
        print('  3. If truly needed at this size, use git-lfs.')
        return 1

    if warn and args.strict:
        print(f'⚠️  {len(warn)} file(s) in warn band + --strict — treating as FAIL')
        return 2

    if warn:
        print(f'⚠️  {len(warn)} file(s) in warn band (>{args.threshold * WARN_FRACTION:.1f} MB)')
        print('   Not blocking, but investigate before they reach the hard threshold.')

    print('✅ All data files within threshold.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
