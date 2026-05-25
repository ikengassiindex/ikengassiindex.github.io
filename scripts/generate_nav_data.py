#!/usr/bin/env python3
"""
generate_nav_data.py — Phase 1.4 codegen (KB §65.4.4, option α).

Reads intelligence/countries.json (single source of truth for country
metadata) and regenerates the auto-generated section of nav.js between
sentinel comments:

  // >>> BEGIN AUTO-GENERATED FROM countries.json (do not edit by hand)
  ...auto-generated SSI_COUNTRY_SLUGS / SSI_COUNTRY_LABELS / countryStats...
  // <<< END AUTO-GENERATED

Eliminates anti-pattern A4 (KB §64.3) — parallel hardcoded country
list in nav.js drifting from countries.json.

USAGE:  python3 scripts/generate_nav_data.py [--check]
        --check: exit 1 if nav.js auto-section is out of sync (for CI)
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NAV_JS = REPO / 'nav.js'
COUNTRIES_JSON = REPO / 'intelligence' / 'countries.json'

BEGIN_MARK = '// >>> BEGIN AUTO-GENERATED FROM countries.json (do not edit by hand)'
END_MARK = '// <<< END AUTO-GENERATED'


def load_countries():
    """Return list of country dicts with at least slug + name + flag."""
    cj = json.loads(COUNTRIES_JSON.read_text())
    return [c for c in cj.get('countries', []) if isinstance(c, dict) and 'slug' in c]


def _js_unicode_escape(s: str) -> str:
    """Escape non-ASCII as JS \\uXXXX (with surrogate pairs for code points > U+FFFF
    so flag emojis like 🇫🇷 emit \\uD83C\\uDDEB\\uD83C\\uDDF7)."""
    out = []
    for ch in s:
        cp = ord(ch)
        if cp < 128:
            out.append(ch)
        elif cp <= 0xFFFF:
            out.append(f'\\u{cp:04X}')
        else:
            # Encode as UTF-16 surrogate pair
            cp_adj = cp - 0x10000
            hi = 0xD800 | (cp_adj >> 10)
            lo = 0xDC00 | (cp_adj & 0x3FF)
            out.append(f'\\u{hi:04X}\\u{lo:04X}')
    return ''.join(out)


def render_auto_section(countries: list) -> str:
    """Emit the JS block: slug array + labels dict + countryStats footer line."""
    # Sort alphabetically for stable diffs
    countries = sorted(countries, key=lambda c: c['slug'])

    slugs_js = ',\n  '.join(f"'{c['slug']}'" for c in countries)

    # Labels: "slug: '🇫🇷 France'" — use the flag + name from countries.json
    label_lines = []
    for c in countries:
        slug = c['slug']
        flag = c.get('flag', '')
        name = c.get('name', slug.capitalize())
        flag_esc = _js_unicode_escape(flag)
        label_lines.append(f"  '{slug}': '{flag_esc} {name}'")
    labels_js = ',\n'.join(label_lines)

    # countryStats lines — these were previously hand-written. For now we emit a
    # placeholder map; Phase 1.5 will move full stats into the per-country config.
    stats_lines = []
    for c in countries:
        slug = c['slug']
        # Best-effort default; per-country config (Phase 1.5) will override
        n_subs = c.get('substations_count', '?')
        n_regions = c.get('regions_count', '?')
        region_label = c.get('admin_l1_label', 'regions')
        line = f"  '{slug}': '95 variables \\u00b7 substations: {n_subs} \\u00b7 {n_regions} {region_label}'"
        stats_lines.append(line)
    stats_js = ',\n'.join(stats_lines)

    block = f"""{BEGIN_MARK}
// Single source of truth: intelligence/countries.json (regenerate via
// scripts/generate_nav_data.py — pre-commit hook does this automatically).
// {len(countries)} countries as of last regeneration.

var SSI_COUNTRY_SLUGS = [
  {slugs_js}
];
var SSI_COUNTRY_PATH_RE = new RegExp('/(' + SSI_COUNTRY_SLUGS.join('|') + ')/');

var SSI_COUNTRY_LABELS = {{
{labels_js}
}};

var SSI_COUNTRY_STATS_DEFAULT = {{
{stats_js}
}};
{END_MARK}"""
    return block


def patch_nav_js(new_block: str) -> tuple[str, bool]:
    """Replace the auto-section in nav.js, return (new_content, changed)."""
    src = NAV_JS.read_text()
    pattern = re.compile(
        re.escape(BEGIN_MARK) + r'.*?' + re.escape(END_MARK),
        re.DOTALL,
    )
    if pattern.search(src):
        # Use a lambda to avoid re.sub treating backslash escapes in new_block as backrefs
        new_src = pattern.sub(lambda m: new_block, src)
    else:
        # First run: inject after the initial header comment block
        # (find the first blank line after the file-header comment)
        insert_at = src.find('\n\n')
        if insert_at == -1:
            insert_at = 0
        else:
            insert_at += 2
        new_src = src[:insert_at] + new_block + '\n\n' + src[insert_at:]
    return new_src, new_src != src


def main():
    check_mode = '--check' in sys.argv
    countries = load_countries()
    block = render_auto_section(countries)
    new_src, changed = patch_nav_js(block)

    if check_mode:
        if changed:
            print(f"OUT OF SYNC: nav.js auto-section differs from countries.json")
            print(f"  Run: python3 scripts/generate_nav_data.py")
            return 1
        print(f"OK: nav.js auto-section is in sync ({len(countries)} countries)")
        return 0

    if changed:
        NAV_JS.write_text(new_src)
        print(f"Regenerated nav.js auto-section ({len(countries)} countries)")
    else:
        print(f"nav.js auto-section unchanged ({len(countries)} countries)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
