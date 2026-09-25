#!/usr/bin/env python3
"""
extract_country_configs.py — Phase 1.5 (KB §65.4.5).

For each of the 31 country folders, parse {country}/intelligence.html
and {country}/index.html to extract:
  - R3 bucket thresholds (4 numeric literals)
  - High-Consequence threshold
  - Edition anchor offset
  - Admin-l1 + admin-l2 labels + counts

Write the extracted values as intelligence/country-configs/{country}.json
conforming to schemas/country-config.schema.json.

This is the inert single-source-of-truth that Phase 2's central renderer
will consume to replace hardcoded JS literals in per-country HTML
(anti-pattern A7 from KB §64.3).

USAGE:
  python3 scripts/extract_country_configs.py                 # all countries
  python3 scripts/extract_country_configs.py slovenia        # one country
  python3 scripts/extract_country_configs.py --validate-only # don't write, just check
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIGS_DIR = REPO / 'intelligence' / 'country-configs'
COUNTRIES_JSON = REPO / 'intelligence' / 'countries.json'


# ── Regex patterns for HTML extraction ──
# R3 bucket: filter: function(s){ return s.modifiers.R3_C_mult >= 1.05; }
RE_R3_BUCKET_GE = re.compile(r'R3_C_mult\s*>=\s*([\d.]+)')
RE_R3_BUCKET_LT = re.compile(r'R3_C_mult\s*<\s*([\d.]+)')
RE_R3_BUCKET_BAND = re.compile(r'R3_C_mult\s*>=\s*([\d.]+)\s*&&\s*s\.modifiers\.R3_C_mult\s*<\s*([\d.]+)')
RE_TIER_LABEL = re.compile(r"label:\s*'([^']+)'")
# Edition anchor: var nextEditionNum = (nextYear - 2026) * 12 + (nextMonth + 1) - 6;
RE_EDITION_OFFSET = re.compile(r'nextEditionNum\s*=.*?-\s*(\d+)\s*;')


def parse_country_html(slug: str) -> dict:
    """Extract config-worthy values from a country's intelligence.html + ssi-data.json."""
    out = {
        'slug': slug,
        'extracted_from': [],
    }

    intel = REPO / slug / 'intelligence.html'
    if intel.exists():
        text = intel.read_text(errors='ignore')
        out['extracted_from'].append('intelligence.html')

        # R3 bucket boundaries — find all >= comparisons (top boundary of each tier)
        ge_thresholds = sorted(set(float(m) for m in RE_R3_BUCKET_GE.findall(text)), reverse=True)
        if ge_thresholds:
            out['r3_thresholds_extracted'] = ge_thresholds

        # Edition anchor offset
        m = RE_EDITION_OFFSET.search(text)
        if m:
            out['edition_anchor_offset'] = int(m.group(1))

    # Pull region count from ssi-data.json (authoritative)
    ssi_data = REPO / slug / 'ssi-data.json'
    if ssi_data.exists():
        try:
            d = json.loads(ssi_data.read_text())
            out['extracted_from'].append('ssi-data.json')
            # Region count: prefer meta.regions, fallback to len(regions array)
            meta = d.get('meta', {})
            if 'regions' in meta and isinstance(meta['regions'], int):
                out['regions_count'] = meta['regions']
            elif isinstance(d.get('regions'), list):
                out['regions_count'] = len(d['regions'])
            elif isinstance(d.get('regions'), dict):
                out['regions_count'] = len(d['regions'])
            # Substation count from fleet_summary
            if isinstance(d.get('fleet_summary'), dict):
                out['substations_count'] = d['fleet_summary'].get('total', 0)
            elif isinstance(d.get('substations'), list):
                out['substations_count'] = len(d['substations'])
        except (json.JSONDecodeError, MemoryError) as e:
            out['ssi_data_error'] = str(e)[:80]

    return out


def build_config(slug: str, country_meta: dict, extracted: dict) -> dict:
    """Compose a country-config.json conforming to the schema.
    Uses extracted values where available; falls back to sensible defaults."""
    cfg = {
        'slug': slug,
        'country_name': country_meta.get('name', slug.capitalize()),
        'iso2': country_meta.get('iso2', ''),
        'iso3': country_meta.get('iso3', ''),
        'flag': country_meta.get('flag', ''),
        'capital': country_meta.get('capital', ''),
        'first_refresh': country_meta.get('first_refresh', '2026-03-12'),
        'tso': country_meta.get('tso', ''),
        'regulator': country_meta.get('regulator', ''),
        'admin': {
            'l1': {
                'label_en': country_meta.get('admin_l1_label', 'region'),
                'label_short': country_meta.get('admin_l1_label_short', 'region'),
                'count': extracted.get('regions_count') or country_meta.get('regions_count') or 1,
            }
        },
    }
    # Optional local name
    if country_meta.get('name_local'):
        cfg['country_name_local'] = country_meta['name_local']
    if country_meta.get('admin_l2_label'):
        cfg['admin']['l2'] = {
            'label_en': country_meta['admin_l2_label'],
            'count': country_meta.get('admin_l2_count', 0),
        }

    # R3 thresholds: pilot-quality defaults if we couldn't extract
    r3_thresholds = extracted.get('r3_thresholds_extracted', [])
    if len(r3_thresholds) >= 3:
        # Map to canonical 4-bucket structure: take top 3 as bucket lower-bounds
        b1, b2, b3 = sorted(r3_thresholds, reverse=True)[:3]
        cfg['thresholds'] = {
            'r3_buckets': [
                {'label': 'Capital-Intensive / High-Consequence', 'icon': '\U0001F3ED',
                 'lower': b1, 'upper': None, 'voll_range': '€15-30/kWh', 'color': '#941914'},
                {'label': 'Industrial / Medium-Large Enterprise', 'icon': '\U0001F527',
                 'lower': b2, 'upper': b1, 'voll_range': '€8-15/kWh', 'color': '#aa4234'},
                {'label': 'Commercial / Mixed', 'icon': '\U0001F3EA',
                 'lower': b3, 'upper': b2, 'voll_range': '€3-8/kWh', 'color': '#b8863a'},
                {'label': 'Light-Rural / Agricultural', 'icon': '\U0001F33E',
                 'lower': 0.0, 'upper': b3, 'voll_range': '€1-3/kWh', 'color': '#5d8563'},
            ],
            'high_consequence_threshold': round((b1 + b2) / 2, 3),
        }
    # else: partial or zero extraction — omit thresholds entirely.
    # Phase 1.5 = best-effort first-pass; renderer applies sane defaults
    # when thresholds absent. Full bucket structure for these countries
    # will be completed in a follow-up pass with data-driven percentiles.

    if 'edition_anchor_offset' in extracted:
        cfg['edition_anchor_month_offset'] = extracted['edition_anchor_offset']

    return cfg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    validate_only = '--validate-only' in sys.argv

    cj = json.loads(COUNTRIES_JSON.read_text())
    country_lookup = {c['slug']: c for c in cj['countries'] if 'slug' in c}

    if args:
        slugs = args
    else:
        slugs = sorted(country_lookup.keys())

    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

    written = skipped = error = 0
    print(f"{'country':<14}  R3-buckets  edition  written")
    print('-' * 50)
    for slug in slugs:
        if slug not in country_lookup:
            print(f"  {slug}: not in countries.json — skip")
            skipped += 1
            continue
        try:
            extracted = parse_country_html(slug)
            cfg = build_config(slug, country_lookup[slug], extracted)
            r3_n = len(extracted.get('r3_thresholds_extracted', []))
            ed_offset = extracted.get('edition_anchor_offset', '-')
            out_path = CONFIGS_DIR / f'{slug}.json'
            if not validate_only:
                out_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
                written += 1
            print(f"  {slug:<12}  {r3_n:>4} thresh  off={str(ed_offset):>3}  {'✓' if not validate_only else '(dry)'}")
        except Exception as e:
            print(f"  {slug:<12}  ERROR: {e}")
            error += 1

    print('-' * 50)
    print(f"Wrote: {written} | Skipped: {skipped} | Errors: {error}")

    # Validate written configs against schema
    if not validate_only and written:
        print("\nValidating written configs against schemas/country-config.schema.json...")
        try:
            from jsonschema import Draft202012Validator
            schema = json.loads((REPO / 'schemas' / 'country-config.schema.json').read_text())
            v = Draft202012Validator(schema)
            v_pass = v_fail = 0
            for cfg_file in sorted(CONFIGS_DIR.glob('*.json')):
                data = json.loads(cfg_file.read_text())
                errs = list(v.iter_errors(data))
                if errs:
                    v_fail += 1
                    print(f"  ✗ {cfg_file.name}: {errs[0].message[:100]}")
                else:
                    v_pass += 1
            print(f"\n  Schema validation: {v_pass} pass / {v_fail} fail")
        except ImportError:
            print("  (skip — jsonschema not installed)")

    return 0 if error == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
