#!/usr/bin/env python3
"""
LP-8: Promote v4.2 country pages from SSI Index/pages-v4.2/ to live <slug>/.

For each of 39 countries:
  1. Resolve OneDrive source folder (handling slug mapping)
  2. Backup current live <slug>/ pages to <slug>/_v4.0.2.backup/
  3. Copy canonical files from pages-v4.2/ to <slug>/
  4. Skip .bak / .pre_* backup files
  5. Skip files we want to preserve (none currently; ssi-metadata.js DSR was
     already applied to pages-v4.2 too per task #419)

Files promoted per country (canonical surface):
  - 7 HTML pages (index, intelligence, esg-report, methodology, data, map, regional)
  - ssi-metadata.js, ssi-data.json (canonical scoring data)
  - bounds.json, grid-geo.json (map geo)
  - <slug>-section-overrides.js (country JS overlay)
  - ikenga-logo.svg (shared brand asset)

Run from:  ~/ikengassiindex.github.io
Run as:    python3 PROMOTE_V4_2_COUNTRIES.py --dry-run     (preview)
           python3 PROMOTE_V4_2_COUNTRIES.py               (execute)
"""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

# Repo + OneDrive roots
REPO_ROOT = Path(__file__).resolve().parent

# OneDrive root candidates — first existing wins. Supports both operator's Mac
# (where the OneDrive folder is at the standard CloudStorage path) and the
# sandbox (where it's mounted under /sessions/.../mnt/SSI Index).
_ONEDRIVE_CANDIDATES = [
    Path('/Users/cedricberard/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/'
         'Shared DR/Internal/0. General/0.22. IP agenda/SSI Index'),
    Path('/sessions/wonderful-exciting-fermi/mnt/SSI Index'),
]
ONEDRIVE_ROOT = next((p for p in _ONEDRIVE_CANDIDATES if p.is_dir()), _ONEDRIVE_CANDIDATES[0])

# Slug mapping: OneDrive folder name → live repo slug
SLUG_MAP = {
    'costa_rica': 'costa-rica',
    'new_zealand': 'new-zealand',
    'united_kingdom': 'uk',
    'united_states': 'us',
    'SSI_v4_2 Italy Pilot': 'italy',
}

# Files to promote per country (everything else in pages-v4.2/ stays in OneDrive)
CANONICAL_FILES = [
    'index.html',
    'intelligence.html',
    'esg-report.html',
    'methodology.html',
    'data.html',
    'map.html',
    'regional.html',
    'ssi-metadata.js',
    'ssi-data.json',
    'bounds.json',
    'grid-geo.json',
    'ikenga-logo.svg',
]

# File patterns to skip (backups, test artefacts)
SKIP_PATTERNS = ['.bak', '.pre_', '.pre-', '_backup', '.v4.0.2.backup']


def discover_v42_sources() -> dict[str, Path]:
    """Walk OneDrive SSI Index and return live_slug → pages-v4.2 path mapping."""
    sources: dict[str, Path] = {}
    for d in ONEDRIVE_ROOT.iterdir():
        if not d.is_dir():
            continue
        pages_v42 = d / 'pages-v4.2'
        if not pages_v42.is_dir():
            continue
        live_slug = SLUG_MAP.get(d.name, d.name)
        sources[live_slug] = pages_v42
    return sources


def should_skip(name: str) -> bool:
    return any(p in name for p in SKIP_PATTERNS)


def promote_country(live_slug: str, source_dir: Path, dry_run: bool) -> dict:
    """Promote one country's v4.2 surface to live <slug>/."""
    live_dir = REPO_ROOT / live_slug
    if not live_dir.is_dir():
        return {'status': 'skip', 'reason': f'no live <slug>/ folder for {live_slug}'}

    backup_dir = live_dir / '_v4.0.2.backup'
    actions = {'backup': [], 'copy': [], 'skip_missing': [], 'skip_section_overrides': None}

    # Step 1: Backup current live canonical files
    if not dry_run:
        backup_dir.mkdir(exist_ok=True)
    for fname in CANONICAL_FILES:
        live_file = live_dir / fname
        if live_file.is_file():
            target = backup_dir / fname
            if not dry_run:
                shutil.copy2(live_file, target)
            actions['backup'].append(fname)

    # Also backup the country's section-overrides.js if present
    overrides_name = f'{live_slug}-section-overrides.js'
    live_overrides = live_dir / overrides_name
    if live_overrides.is_file():
        if not dry_run:
            shutil.copy2(live_overrides, backup_dir / overrides_name)
        actions['backup'].append(overrides_name)

    # Step 2: Copy v4.2 canonical files
    for fname in CANONICAL_FILES:
        src = source_dir / fname
        if not src.is_file():
            actions['skip_missing'].append(fname)
            continue
        dst = live_dir / fname
        if not dry_run:
            shutil.copy2(src, dst)
        actions['copy'].append(fname)

    # Step 3: Copy country-specific section-overrides.js (if exists in v4.2)
    src_overrides = source_dir / overrides_name
    if src_overrides.is_file():
        if not dry_run:
            shutil.copy2(src_overrides, live_dir / overrides_name)
        actions['copy'].append(overrides_name)
    else:
        # Maybe under a different name (e.g., italy/italy-section-overrides.js)
        for candidate in source_dir.glob('*-section-overrides.js'):
            if should_skip(candidate.name):
                continue
            if not dry_run:
                shutil.copy2(candidate, live_dir / candidate.name)
            actions['copy'].append(candidate.name)
            break

    return {'status': 'ok', 'actions': actions}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Preview without writing')
    ap.add_argument('--only', help='Comma-separated slugs to promote (default: all)')
    args = ap.parse_args()

    print('=' * 70)
    print('  LP-8: Promote v4.2 country pages → live <slug>/')
    print(f'  Mode: {"DRY-RUN" if args.dry_run else "EXECUTE"}')
    print('=' * 70)

    sources = discover_v42_sources()
    if args.only:
        wanted = set(s.strip() for s in args.only.split(','))
        sources = {k: v for k, v in sources.items() if k in wanted}

    print(f'\n  Discovered {len(sources)} v4.2 source folders.\n')

    total_ok = total_skip = 0
    total_files_copied = 0
    for live_slug in sorted(sources.keys()):
        source_dir = sources[live_slug]
        result = promote_country(live_slug, source_dir, args.dry_run)
        if result['status'] == 'ok':
            actions = result['actions']
            print(f"  ✓ {live_slug:14}  backup={len(actions['backup'])}  "
                  f"copy={len(actions['copy'])}  "
                  f"missing={len(actions['skip_missing'])}")
            total_ok += 1
            total_files_copied += len(actions['copy'])
            if actions['skip_missing']:
                print(f"     (missing in v4.2: {', '.join(actions['skip_missing'])})")
        else:
            print(f"  ✗ {live_slug:14}  {result.get('reason', 'unknown')}")
            total_skip += 1

    print()
    print(f'  Summary: {total_ok} ok, {total_skip} skipped, '
          f'{total_files_copied} files {"would be " if args.dry_run else ""}copied.')

    if args.dry_run:
        print('\n  (dry-run — no changes written. Re-run without --dry-run to execute.)')
    else:
        print('\n  ✓ Promotion complete. Next steps:')
        print('    1. Spot-check 2-3 countries: open <slug>/intelligence.html in browser')
        print('    2. git status (should show ~280 modified + new files)')
        print('    3. git add . && git commit + push')
    return 0


if __name__ == '__main__':
    sys.exit(main())
