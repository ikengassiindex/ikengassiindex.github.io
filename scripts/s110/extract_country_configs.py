#!/usr/bin/env python3
"""
S110 Session 3 — Auto-extract per-country map.html metadata into YAML configs.

For each country WITHOUT a templates/configs/<slug>.yaml, parse the current
<country>/map.html and emit a config file with:
  - slug, country_name, country_possessive, fleet_count
  - admin (count + level labels)
  - descriptions.map
  - map.voltage_filter_options

Skips countries that already have a config file.
"""
import json, re, sys, yaml
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
CONFIGS = REPO / 'templates' / 'configs'

# country_name overrides for slugs that don't title-case cleanly
NAME_OVERRIDES = {
    'uk': 'United Kingdom',
    'us': 'United States',
    'new-zealand': 'New Zealand',
    'costa-rica': 'Costa Rica',
    'czechia': 'Czechia',
}

def country_name_from_slug(slug):
    if slug in NAME_OVERRIDES:
        return NAME_OVERRIDES[slug]
    return slug.replace('-', ' ').title()

def parse_map_html(slug):
    """Extract per-country metadata from <slug>/map.html."""
    path = REPO / slug / 'map.html'
    if not path.exists():
        return None, f"No {path}"
    html = path.read_text()
    
    out = {'schema_version': '1.0', 'slug': slug}
    
    # 1. Meta description
    m = re.search(r'name="description"\s+content="([^"]+)"', html)
    description = m.group(1) if m else ""
    out['_description'] = description  # temporary; will move to descriptions.map
    
    # 2. country_possessive — from "across X's transmission" or "in X's transmission"
    m = re.search(r'(?:across|in)\s+([^<]+?)\s+transmission and distribution grid', html)
    if m:
        possessive = m.group(1).strip()
        out['country_possessive'] = possessive
    else:
        # Fallback: from description "of X's electrical grid"
        m = re.search(r'Interactive map of ([^<]+?)\s+electrical grid', description)
        if m:
            out['country_possessive'] = m.group(1).strip()
        else:
            out['country_possessive'] = country_name_from_slug(slug) + "'s"
    
    # 3. country_name — usually = possessive minus 's, or override
    out['country_name'] = country_name_from_slug(slug)
    
    # 4. fleet_count — from substation count in ssi-data.json (source of truth)
    ssi_path = REPO / slug / 'ssi-data.json'
    if ssi_path.exists():
        with open(ssi_path) as f:
            ssi = json.load(f)
        out['fleet_count'] = len(ssi.get('substations', []))
    else:
        # Fallback: from page-header text
        m = re.search(r'<p>Explore ([\d,]+) substations', html)
        out['fleet_count'] = int(m.group(1).replace(',', '')) if m else 0
    
    # 5. admin.count — from regions count in ssi-data.json
    if ssi_path.exists():
        admin_count = len(ssi.get('regions', []))
    else:
        admin_count = 0
    
    # 6. admin.level_label_singular — from filter-region <label>
    m = re.search(r'<label>([^<]+)</label>\s*<select id="filter-region">', html)
    label_singular = m.group(1).strip() if m else "Region"
    
    # 7. admin.level_label_plural — from "All X" option
    m = re.search(r'<select id="filter-region">\s*<option value="all">All ([^<]+)</option>', html)
    label_plural = m.group(1).strip() if m else label_singular + "s"
    
    out['admin'] = {
        'count': admin_count,
        'level_label_singular': label_singular,
        'level_label_plural': label_plural,
        'short': label_singular,
    }
    
    # 8. descriptions.map — verbatim from meta description (or normalised below)
    out['descriptions'] = {'map': description}
    del out['_description']
    
    # 9. voltage_filter_options
    m = re.search(r'<select id="filter-voltage">(.*?)</select>', html, re.DOTALL)
    if m:
        opts = re.findall(r'<option value="([^"]+)">([^<]+)</option>', m.group(1))
        voltage_options = [
            {'value': v, 'label': lbl.replace('&lt;', '<')}
            for v, lbl in opts if v != 'all'
        ]
    else:
        voltage_options = []
    
    out['map'] = {'voltage_filter_options': voltage_options}
    return out, None

# Identify the 33 countries needing configs
all_country_dirs = sorted(
    p.name for p in REPO.iterdir()
    if p.is_dir() and (p / 'map.html').exists() and not p.name.startswith('.')
    and (p / 'ssi-data.json').exists()
)
existing_configs = {p.stem for p in CONFIGS.glob('*.yaml')}
missing = [c for c in all_country_dirs if c not in existing_configs]

print(f"=== Total countries with map.html + ssi-data.json: {len(all_country_dirs)} ===")
print(f"=== Existing configs (skip): {sorted(existing_configs)} ===")
print(f"=== Missing configs to author: {len(missing)} ===")
print()

errors = 0
for slug in missing:
    cfg, err = parse_map_html(slug)
    if err:
        print(f"  ✗ {slug:<14} {err}")
        errors += 1
        continue
    
    out_path = CONFIGS / f'{slug}.yaml'
    with open(out_path, 'w') as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    print(f"  ✓ {slug:<14}  fleet={cfg['fleet_count']:>5}  admin={cfg['admin']['count']}×{cfg['admin']['level_label_singular']}  voltages={len(cfg['map']['voltage_filter_options'])}")

print(f"\nAuthored {len(missing) - errors} configs, {errors} errors")
