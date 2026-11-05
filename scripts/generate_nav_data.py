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


def _voltage_kv(s):
    """The caller's own predicate, lifted out of the loop it used to sit in so
    that the tally below and any future reader share ONE definition of what a
    voltage band is."""
    v = s.get('voltage_kv')
    return v if isinstance(v, (int, float)) else 0


def _tally_substations(slug):
    """(n, ehv, hv) with ONE SHARD RESIDENT AT A TIME. Convention #79
    shard-aware.

    THIS REPLACED A MATERIALISING READER, AND THE REASON IS MEASURED. It was:

        def _read_substations(slug):   # returned a list of EVERY record
            ...
            out = []
            for e in d['substations_shards']:
                ...
                out += q if isinstance(q, list) else (q.get('substations') or [])
            return out

    and its only caller took three numbers off that list. Measured 5 November
    2026 on the device bridge, `generate_nav_data.py --check` peaked at
    3.62 GB of RSS on a machine with 3,906 MB and NO SWAP, so the instrument
    ran within about 290 MB of the ceiling and its cost was decided by what
    else was resident. A sibling instrument at 3.47 GB was killed outright -
    rc=-9, empty stdout, empty stderr. The largest single shard is 47.0 MB.

    The reader that returned the list is GONE rather than kept beside this
    one: nothing in scripts/, tests/ or doctrine/ imported it, and leaving a
    3.6 GB materialiser in the module for a later shift to call again would be
    the defect waiting to be re-entered.

    NO NUMBER MOVES: all 39 fleets were computed both ways and the four
    figures the caller uses agree on every one.
    """
    p = REPO / slug / 'ssi-data.json'
    if not p.exists():
        return 0, 0, 0
    d = json.loads(p.read_text())
    n = ehv = hv = 0

    def tally(rows):
        nonlocal n, ehv, hv
        for s in rows:
            n += 1
            v = _voltage_kv(s)
            if v >= 220:
                ehv += 1
            elif 110 <= v < 220:
                hv += 1

    if isinstance(d, list):
        tally(d)
        return n, ehv, hv
    if d.get('substations_shards'):
        shards = list(d['substations_shards'])
        del d
        for e in shards:
            rel = e['path'] if isinstance(e, dict) else e
            sp = p.parent / Path(rel).name
            if sp.exists():
                q = json.loads(sp.read_text())
                tally(q if isinstance(q, list) else (q.get('substations') or []))
                del q
        return n, ehv, hv
    tally(d.get('substations') or [])
    return n, ehv, hv


def _read_line_count(slug):
    """Convention #80 shard-aware, and STREAMING for the same measured reason
    as _tally_substations above: the largest single line shard is 80.8 MB and
    the whole family is 571 MB, which used to be resident at once."""
    p = REPO / slug / 'grid-geo.json'
    if not p.exists():
        return 0
    g = json.loads(p.read_text())
    n = len(g.get('l') or [])
    shards = list(g.get('l_shards') or [])
    del g
    for e in shards:
        rel = e['path'] if isinstance(e, dict) else e
        sp = p.parent / Path(rel).name
        if sp.exists():
            q = json.loads(sp.read_text())
            n += len(q if isinstance(q, list) else (q.get('l') or q.get('lines') or []))
            del q
    return n


def _read_admin_l1(slug):
    """(count, plural label). The config declares the administrative tier the
    index reports at; len(regions) in the data is a by-product of the spatial
    join and carries a finer tier on several countries.

    label_plural is used verbatim when someone has deliberately set it. It is
    absent on all 39 today. label_en is NOT pluralised and NOT used: it holds
    a singular on 31 countries and a glossed phrase on eight — 'Departamento
    (32 departamentos + Bogota D.C. = 33)', 'do/si (17 provinces and
    metropolitan cities)', 'Mehoz (6 mehozot districts)'. Appending an s to
    those produces 'Mehozs' and 'krajs'. Correct local plurals reach the
    footer through countries.json::admin_l1_label, lifted from the strings a
    human wrote; everything else says 'regions' and is right."""
    p = REPO / 'intelligence' / 'country-configs' / f'{slug}.json'
    if not p.exists():
        return None, 'regions'
    l1 = (json.loads(p.read_text()).get('admin') or {}).get('l1') or {}
    return l1.get('count'), (l1.get('label_plural') or 'regions')


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
    # Figures come from the data files, never from countries.json. countries.json
    # carries only the editorial fragments the data cannot reproduce:
    # footer_sources, admin_l1_label, footer_note.
    stats_lines = []
    for c in countries:
        slug = c['slug']
        n_subs, ehv, hv = _tally_substations(slug)
        n_lines = _read_line_count(slug)
        n_regions, cfg_label = _read_admin_l1(slug)
        dist = n_subs - ehv - hv
        seg = ['95 variables']
        if c.get('footer_sources'):
            seg.append(f"{c['footer_sources']} sources")
        seg.append(f"{n_subs:,} substations ({ehv:,} EHV \u2265220 kV \u00b7 "
                   f"{hv:,} HV 110\u2013220 kV \u00b7 {dist:,} distribution-tier)")
        tail = f"{n_lines:,} power lines"
        if n_regions is not None:
            tail += f" across {n_regions:,} {c.get('admin_l1_label') or cfg_label}"
            if c.get('footer_note'):
                tail += f" \u00b7 {c['footer_note']}"
        seg.append(tail)
        text = _js_unicode_escape(' \u00b7 '.join(seg))
        stats_lines.append(f"  '{slug}': '{text}'")
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
