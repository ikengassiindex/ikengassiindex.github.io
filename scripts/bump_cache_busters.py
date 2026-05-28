#!/usr/bin/env python3
"""
bump_cache_busters.py — Phase 1.8 (KB §65)

Rewrites `?v=NNN` query strings in country HTML pages to use the git-blob
hash of the target file. Result: every time a data file changes, its
cache-buster URL changes automatically — no manual ?v=N+1 bumping.

Why this matters (anti-pattern A10 — browser-cache stale-read after URL-stable
data patch): tonight we patched ssi-data.json multiple times but the URL key
stayed at ?v=600, so browsers served stale cached copies. We had to manually
bump to ?v=700 across 8 files. With git-hash busters, the URL changes
automatically on every commit that modifies the target file.

USAGE:
  python3 scripts/bump_cache_busters.py                       # all countries
  python3 scripts/bump_cache_busters.py slovenia              # one country
  python3 scripts/bump_cache_busters.py --check               # exit 1 if any URL is stale
  python3 scripts/bump_cache_busters.py --dry-run             # show changes without writing

Targets in HTML:
    href="../style.css?v=NNN"           → use git-hash of style.css
    src="../nav.js?v=NNN"               → use git-hash of nav.js
    src="ssi-metadata.js?v=NNN"         → use git-hash of {country}/ssi-metadata.js
    fetch('ssi-data.json?v=NNN')        → use git-hash of {country}/ssi-data.json
    fetch('grid-geo.json?v=NNN')        → use git-hash of {country}/grid-geo.json
    fetch('bounds.json?v=NNN')          → use git-hash of {country}/bounds.json

CI / pre-commit: --check exits 1 if any cache-buster is out of sync with its
target file's current hash. Wired into validate-schemas.yml.
"""
from __future__ import annotations  # str | None unions work on Python 3.7+

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COUNTRIES_JSON = REPO / 'intelligence' / 'countries.json'

# Map URL pattern → file path resolver (relative to repo root)
# Each tuple: (url_basename, get_path_fn(country)) where the URL appears in country/page.html
TARGETS = [
    # Shared site assets (root level)
    ('style.css',         lambda c: REPO / 'style.css'),
    ('nav.js',            lambda c: REPO / 'nav.js'),
    ('map.js',            lambda c: REPO / 'map.js'),
    ('ssi-engine.js',     lambda c: REPO / 'ssi-engine.js'),
    ('ssi-versions.js',   lambda c: REPO / 'ssi-versions.js'),
    # Phase 2b/2c/2d thin-shell modules (KB §65) — central renderer + section registries
    ('country-renderer.js',          lambda c: REPO / 'country-renderer.js'),
    ('esg-sections.js',              lambda c: REPO / 'esg-sections.js'),
    ('intelligence-sections.js',     lambda c: REPO / 'intelligence-sections.js'),
    ('index-sections.js',            lambda c: REPO / 'index-sections.js'),
    ('regional-sections.js',         lambda c: REPO / 'regional-sections.js'),
    ('map-sections.js',              lambda c: REPO / 'map-sections.js'),
    ('methodology-sections.js',      lambda c: REPO / 'methodology-sections.js'),
    ('data-sections.js',             lambda c: REPO / 'data-sections.js'),
    ('dno-dashboard-sections.js',    lambda c: REPO / 'dno-dashboard-sections.js'),
    # Per-country assets
    ('ssi-metadata.js',   lambda c: REPO / c / 'ssi-metadata.js'),
    ('ssi-data.json',     lambda c: REPO / c / 'ssi-data.json'),
    ('grid-geo.json',     lambda c: REPO / c / 'grid-geo.json'),
    ('bounds.json',       lambda c: REPO / c / 'bounds.json'),
    ('versions.json',     lambda c: REPO / c / 'versions.json'),
]


def git_hash(path: Path) -> str | None:
    """Return the git-blob hash of a file's CURRENT contents (working-tree, not committed).
    Uses `git hash-object` which computes the SHA-1 of the blob without staging."""
    if not path.exists():
        return None
    try:
        out = subprocess.run(
            ['git', 'hash-object', str(path)],
            capture_output=True, text=True, timeout=5, cwd=str(REPO),
        )
        if out.returncode != 0:
            return None
        return out.stdout.strip()[:10]  # first 10 chars is plenty for cache invalidation
    except Exception:
        return None


def load_slugs():
    cj = json.loads(COUNTRIES_JSON.read_text())
    return sorted([c['slug'] for c in cj['countries'] if 'slug' in c])


def rewrite_html(html_path: Path, country: str, dry: bool, check: bool) -> tuple[int, list]:
    """Rewrite all ?v= cache-busters in html_path to match git-hash of target files.
    Returns (n_changes, list_of_stale_targets_if_check_mode)."""
    src = html_path.read_text()
    new_src = src
    changes = []
    stale_list = []

    for basename, path_fn in TARGETS:
        target_path = path_fn(country)
        new_hash = git_hash(target_path)
        if new_hash is None:
            continue  # file doesn't exist (e.g. bounds.json absent for some countries)

        # Match patterns like:  basename?v=<token>
        # The version token MUST be a positive character class — alphanumerics,
        # dots, hyphens, underscores only. Anything else (backtick, semicolon,
        # comma, brace, angle bracket, etc.) must terminate the match so we
        # don't accidentally swallow surrounding JS/HTML syntax.
        #
        # Previous negative class `[^"\'\s)&]+` ate closing backticks and
        # semicolons of template literals like `path?v=700`;` (KB §65.4.8 bug,
        # patched 2026-05-25 after slovenia/esg-report.html was broken locally
        # by the eat-too-much regex).
        pattern = re.compile(
            r'(' + re.escape(basename) + r'\?v=)([A-Za-z0-9._-]+)'
        )
        for m in pattern.finditer(new_src):
            old_val = m.group(2)
            if old_val != new_hash:
                changes.append((basename, old_val, new_hash))
                if check:
                    stale_list.append((basename, old_val, new_hash))

        new_src = pattern.sub(r'\g<1>' + new_hash, new_src)

    if not check and not dry and new_src != src:
        html_path.write_text(new_src)
    return len(changes), stale_list


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    check = '--check' in sys.argv

    slugs = args if args else load_slugs()

    page_names = ['index.html', 'intelligence.html', 'esg-report.html',
                  'data.html', 'regional.html', 'methodology.html',
                  'map.html', 'dno-dashboard.html']

    total_changes = 0
    total_stale = 0
    print(f"{'MODE: ' + ('CHECK' if check else 'DRY-RUN' if dry else 'EXECUTE'):<20}  {len(slugs)} countries")
    print('-' * 60)

    for slug in slugs:
        n_changed_country = 0
        for page in page_names:
            html_path = REPO / slug / page
            if not html_path.exists():
                continue
            n_changes, stale = rewrite_html(html_path, slug, dry, check)
            if n_changes:
                n_changed_country += n_changes
                if check:
                    total_stale += len(stale)
                    for basename, old_val, new_hash in stale[:3]:
                        print(f"  ✗ {slug}/{page}  {basename}?v={old_val} → should be ?v={new_hash}")
        if n_changed_country:
            total_changes += n_changed_country
            if not check:
                print(f"  {slug}: rewrote {n_changed_country} cache-busters")

    print('-' * 60)
    if check:
        if total_stale:
            print(f"STALE: {total_stale} cache-busters out of date. Run:")
            print(f"  python3 scripts/bump_cache_busters.py")
            return 1
        print(f"✓ All cache-busters in sync with git-blob hashes")
        return 0
    print(f"{'Would rewrite' if dry else 'Rewrote'} {total_changes} cache-busters across {len(slugs)} countries")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
