#!/usr/bin/env python3
"""
LP-11: Fix slug-form leakage on 4 countries + Türkiye rename.

Problem:
  4 countries (uk, us, costa-rica, new-zealand) have CountryRenderer.init() +
  data-country attrs + section-overrides.js refs using OneDrive folder name
  (united_kingdom, united_states, costa_rica, new_zealand) instead of the live
  URL slug. CountryRenderer fails to find a matching config and leaks the raw
  underscore-form string into the rendered header.

  Plus: Turkey was officially renamed Türkiye at the UN in June 2022.

Fixes per country (uk/us/costa-rica/new-zealand):
  1. Rename <slug>/<underscore>-section-overrides.js → <slug>/<slug>-section-overrides.js
  2. In each of 7 HTML pages per country:
     - data-country="<underscore>" → data-country="<slug>"
     - <underscore>-section-overrides.js → <slug>-section-overrides.js (2 refs:
       comment + script src)
     - CountryRenderer.init('<underscore>', ...) → CountryRenderer.init('<slug>', ...)
  3. Also handle _v4.0.2.backup/ pages (preserve audit trail consistency).

Plus nav.js:
  - 'turkey': '🇹🇷 Turkey' → '🇹🇷 Türkiye'

Run from: ~/ikengassiindex.github.io
Run as:   python3 FIX_SLUG_LEAKAGE.py --dry-run    (preview)
          python3 FIX_SLUG_LEAKAGE.py              (execute)
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Slug remap: live URL slug → OneDrive folder name to retire
SLUG_REMAP = {
    'uk': 'united_kingdom',
    'us': 'united_states',
    'costa-rica': 'costa_rica',
    'new-zealand': 'new_zealand',
}

# HTML files per country to scan
HTML_FILES = [
    'index.html',
    'intelligence.html',
    'esg-report.html',
    'methodology.html',
    'data.html',
    'map.html',
    'regional.html',
]


def fix_html_file(html_path: Path, live_slug: str, underscore_slug: str,
                  dry_run: bool) -> int:
    """Return number of substitutions made (or would be made)."""
    if not html_path.is_file():
        return 0
    text = html_path.read_text(encoding='utf-8')
    original = text
    # 1. data-country attribute
    text = text.replace(
        f'data-country="{underscore_slug}"',
        f'data-country="{live_slug}"',
    )
    # 2. section-overrides.js references (file name in 2 places: comment + script src)
    text = text.replace(
        f'{underscore_slug}-section-overrides.js',
        f'{live_slug}-section-overrides.js',
    )
    # 3. CountryRenderer.init('<underscore>', ...) → CountryRenderer.init('<slug>', ...)
    text = text.replace(
        f"CountryRenderer.init('{underscore_slug}'",
        f"CountryRenderer.init('{live_slug}'",
    )
    if text == original:
        return 0
    # Count substitutions roughly
    n = (original.count(f'data-country="{underscore_slug}"')
         + original.count(f'{underscore_slug}-section-overrides.js')
         + original.count(f"CountryRenderer.init('{underscore_slug}'"))
    if not dry_run:
        html_path.write_text(text, encoding='utf-8')
    return n


def rename_section_overrides(country_dir: Path, live_slug: str,
                              underscore_slug: str, dry_run: bool) -> bool:
    """Rename <slug>/<underscore>-section-overrides.js → <slug>/<slug>-section-overrides.js."""
    src = country_dir / f'{underscore_slug}-section-overrides.js'
    dst = country_dir / f'{live_slug}-section-overrides.js'
    if not src.is_file():
        return False
    if dry_run:
        return True
    src.rename(dst)
    return True


def fix_nav_js_turkey(dry_run: bool) -> bool:
    """Rename Turkey → Türkiye in nav.js SSI_COUNTRY_LABELS."""
    nav = REPO_ROOT / 'nav.js'
    text = nav.read_text(encoding='utf-8')
    old = "'turkey': '\\uD83C\\uDDF9\\uD83C\\uDDF7 Turkey',"
    new = "'turkey': '\\uD83C\\uDDF9\\uD83C\\uDDF7 Türkiye',"
    if old not in text:
        # Already fixed, or pattern unexpected
        return False
    text = text.replace(old, new)
    if not dry_run:
        nav.write_text(text, encoding='utf-8')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print('=' * 70)
    print('  LP-11: Fix slug-form leakage + Türkiye rename')
    print(f'  Mode: {"DRY-RUN" if args.dry_run else "EXECUTE"}')
    print('=' * 70)

    # Step 1: per-country HTML + JS file rename
    total_subs = 0
    for live_slug, underscore in SLUG_REMAP.items():
        print(f'\n  --- {live_slug} (retiring "{underscore}") ---')
        country_dir = REPO_ROOT / live_slug
        if not country_dir.is_dir():
            print(f'    ✗ no {live_slug}/ folder — skipping')
            continue

        # Rename live section-overrides.js
        if rename_section_overrides(country_dir, live_slug, underscore, args.dry_run):
            print(f'    ✓ renamed {underscore}-section-overrides.js → {live_slug}-section-overrides.js')
        else:
            print(f'    · no {underscore}-section-overrides.js in {live_slug}/ (already fixed?)')

        # Also rename the backup if present
        backup_dir = country_dir / '_v4.0.2.backup'
        if backup_dir.is_dir():
            if rename_section_overrides(backup_dir, live_slug, underscore, args.dry_run):
                print(f'    ✓ also renamed in _v4.0.2.backup/')

        # Patch every HTML page in the country dir + backup dir
        n_country = 0
        for html_name in HTML_FILES:
            n = fix_html_file(country_dir / html_name, live_slug, underscore, args.dry_run)
            if n:
                n_country += n
        for html_name in HTML_FILES:
            n = fix_html_file(backup_dir / html_name, live_slug, underscore, args.dry_run)
            if n:
                n_country += n
        print(f'    ✓ {n_country} HTML substitutions in {live_slug}/ + _v4.0.2.backup/')
        total_subs += n_country

    # Step 2: nav.js Turkey → Türkiye
    print(f'\n  --- nav.js Turkey → Türkiye ---')
    if fix_nav_js_turkey(args.dry_run):
        print(f'    ✓ nav.js Turkey label → Türkiye')
    else:
        print(f'    · nav.js Turkey label already fixed (or pattern mismatch)')

    print(f'\n  Summary: {total_subs} HTML substitutions {"would be " if args.dry_run else ""}made.')

    if args.dry_run:
        print('\n  (dry-run — no changes written. Re-run without --dry-run to execute.)')
    else:
        print('\n  ✓ Done. Next steps:')
        print('    git status')
        print('    git add .')
        print('    git commit -m "fix(cohort): slug-form leakage + Türkiye rename (LP-11)"')
        print('    git push origin main')
    return 0


if __name__ == '__main__':
    sys.exit(main())
