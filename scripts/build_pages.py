#!/usr/bin/env python3
"""
S110 — Phase 3 Level C Build Orchestrator
=========================================

Generates per-country HTML files from Jinja2 templates + per-country YAML configs.

Templates:    templates/{page}.html.j2
Configs:      templates/configs/{slug}.yaml
Output:       {slug}/{page}.html

CLI:
  python3 scripts/build_pages.py --all              # build all countries × all pages
  python3 scripts/build_pages.py --page map         # all countries × one page
  python3 scripts/build_pages.py --country slovenia # one country × all pages
  python3 scripts/build_pages.py --country slovenia --page map  # one × one
  python3 scripts/build_pages.py --check            # validate configs, no writes
  python3 scripts/build_pages.py --diff             # show diff vs current; no writes

Cache-busters: auto-computed via git hash-object (Q7 decision).
DOM IDs:       enforced via D#16 post-build check (Q8 decision).

Schema versioning: each config carries schema_version: "1.0" (Q2 decision).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip3 install pyyaml --break-system-packages")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ImportError:
    print("ERROR: Jinja2 is required. Install with: pip3 install jinja2 --break-system-packages")
    sys.exit(1)


REPO_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
CONFIGS_DIR = TEMPLATES_DIR / "configs"

# 8 page types supported by the build (Phase 3 scope)
PAGE_TYPES = ['intelligence', 'esg-report', 'data', 'methodology',
              'index', 'regional', 'map', 'dno-dashboard']

# Schema version this build expects
EXPECTED_SCHEMA_VERSION = "1.0"


# ────────────────────────────────────────────────────────────────────────
# Cache-buster filter (Q7 — auto-computed from git SHA of file content)
# ────────────────────────────────────────────────────────────────────────

_cb_cache = {}

def cache_buster(rel_path):
    """First 10 chars of git hash-object of the file's current content.
    rel_path is relative to repo root (e.g. '../style.css' or 'slovenia/ssi-metadata.js')."""
    if rel_path in _cb_cache:
        return _cb_cache[rel_path]
    # Resolve to absolute path within repo
    if rel_path.startswith('../'):
        # Output context: rel_path is relative to <slug>/{page}.html
        # so '../style.css' means REPO_ROOT/style.css
        abs_path = REPO_ROOT / rel_path[3:]
    else:
        abs_path = REPO_ROOT / rel_path
    if not abs_path.exists():
        # Fallback for files that don't exist yet
        result = "00000000"
    else:
        try:
            out = subprocess.check_output(
                ['git', 'hash-object', str(abs_path)],
                cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
            result = out[:10]
        except subprocess.CalledProcessError:
            result = "00000000"
    _cb_cache[rel_path] = result
    return result


# ────────────────────────────────────────────────────────────────────────
# Config loader + validator
# ────────────────────────────────────────────────────────────────────────

def load_config(slug):
    """Load templates/configs/<slug>.yaml + validate schema_version."""
    path = CONFIGS_DIR / f"{slug}.yaml"
    if not path.exists():
        return None, f"Config not found: {path}"
    with open(path) as f:
        cfg = yaml.safe_load(f)
    if cfg.get('schema_version') != EXPECTED_SCHEMA_VERSION:
        return None, (
            f"Schema version mismatch in {path}: "
            f"got {cfg.get('schema_version')}, expected {EXPECTED_SCHEMA_VERSION}"
        )
    return cfg, None


def list_country_configs():
    """Enumerate slug values that have a config file present."""
    return sorted(p.stem for p in CONFIGS_DIR.glob("*.yaml"))


# ────────────────────────────────────────────────────────────────────────
# Renderer
# ────────────────────────────────────────────────────────────────────────

def make_env():
    """Initialise Jinja2 environment with cache-buster filter + strict undefined."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters['cb'] = cache_buster
    return env


def render_page(env, slug, page, config):
    """Render templates/{page}.html.j2 with slug + page + config context."""
    template_path = f"{page}.html.j2"
    template = env.get_template(template_path)
    ctx = {
        'slug': slug,
        'page': page,
        **config,  # spread config so country_name, fleet_count, admin etc. are top-level
    }
    return template.render(**ctx)


# ────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="S110 Phase 3 build orchestrator")
    parser.add_argument('--country', help='Slug of country (or "all")')
    parser.add_argument('--page', help=f'Page type ({", ".join(PAGE_TYPES)}) or "all"')
    parser.add_argument('--all', action='store_true', help='Build all countries × all pages')
    parser.add_argument('--check', action='store_true', help='Validate configs only, no writes')
    parser.add_argument('--diff', action='store_true', help='Show diff vs current; no writes')
    parser.add_argument('--write', action='store_true', help='Write outputs (default: dry-run)')
    args = parser.parse_args()

    # Determine country scope
    if args.all or args.country == 'all':
        countries = list_country_configs()
    elif args.country:
        countries = [args.country]
    else:
        print("ERROR: Specify --country <slug> or --all")
        return 1

    # Determine page scope
    if args.all or args.page == 'all':
        pages = PAGE_TYPES
    elif args.page:
        if args.page not in PAGE_TYPES:
            print(f"ERROR: unknown page type '{args.page}'. Choose from: {PAGE_TYPES}")
            return 1
        pages = [args.page]
    else:
        print("ERROR: Specify --page <name> or --all")
        return 1

    env = make_env()
    written = 0
    errors = 0

    for slug in countries:
        cfg, err = load_config(slug)
        if err:
            print(f"  ✗ {slug:<14} CONFIG: {err}")
            errors += 1
            continue
        if args.check:
            print(f"  ✓ {slug:<14} schema {cfg.get('schema_version')} OK")
            continue

        for page in pages:
            template_file = TEMPLATES_DIR / f"{page}.html.j2"
            if not template_file.exists():
                print(f"  - {slug}/{page:<16} (template not built yet)")
                continue
            try:
                html = render_page(env, slug, page, cfg)
            except Exception as e:
                print(f"  ✗ {slug}/{page} RENDER FAIL: {e}")
                errors += 1
                continue

            out_path = REPO_ROOT / slug / f"{page}.html"
            if args.diff:
                if out_path.exists():
                    current = out_path.read_text()
                    if current == html:
                        print(f"  = {slug}/{page} (identical)")
                    else:
                        print(f"  Δ {slug}/{page} (would change: {abs(len(html)-len(current))} bytes)")
                else:
                    print(f"  + {slug}/{page} (new)")
                continue

            if not args.write:
                print(f"  ⟶ {slug}/{page} DRY-RUN ({len(html)} bytes; pass --write to commit)")
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(html)
            written += 1
            print(f"  ✓ {slug}/{page} written ({len(html)} bytes)")

    print()
    if args.check:
        print(f"Validated {len(countries)} configs, {errors} errors")
    elif args.diff:
        print(f"Diff mode: {len(countries)} countries × {len(pages)} pages compared")
    else:
        print(f"Wrote {written} files, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
