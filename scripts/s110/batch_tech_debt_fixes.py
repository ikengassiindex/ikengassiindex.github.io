#!/usr/bin/env python3
"""
Batch tech-debt fixes (closes #743, #745, #750, #751, #738, #755).

Run from repo root: python3 scripts/s110/batch_tech_debt_fixes.py [--dry-run]

Categories applied:
  1. #743 country_adjective leakage (10 countries)
  2. #745 methodology admin-label substation placeholder (10 countries)
  3. #745 Italy département → regione
  4. #745 Costa Rica "Provincia provincia" → "Provincia" + Iceland-prose scrub
  5. #745 Switzerland NUTS-3 landshluti + Iceland-agency prose scrub
  6. #750 esg-report cache-buster — handled in template, not here
  7. #751 esg-report edition_badge normalize to greenfield form (33 countries)
  8. #738 Iceland Hungarian residue scrub (27 occurrences)
  9. #738 Korea Hungarian residue scrub (13 occurrences)
  10. #755 LV/LT NUTS-3 region → NUTS-3 Region casing (54 string edits)
"""
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "templates" / "configs"

DRY_RUN = '--dry-run' in sys.argv

# ─── #743 country_adjective fixes ──────────────────────────────────────────────
COUNTRY_ADJ = {
    'belgium':     'Belgian',
    'chile':       'Chilean',
    'colombia':    'Colombian',
    'costa-rica':  'Costa Rican',
    'estonia':     'Estonian',
    'israel':      'Israeli',
    'latvia':      'Latvian',
    'lithuania':   'Lithuanian',
    'netherlands': 'Dutch',
    'new-zealand': 'New Zealand',
}

# ─── #745 substation placeholder fixes (10 countries) ──────────────────────────
# Format: slug → (admin_label_singular_lower, admin_label_plural_lower)
ADMIN_LABEL_FIXES = {
    'australia':  ('state',       'states'),
    'chile':      ('region',      'regions'),
    'denmark':    ('region',      'regions'),
    'finland':    ('maakunta',    'maakunnat'),
    'greece':     ('region',      'regions'),
    'greenland':  ('kommune',     'kommuner'),
    'mexico':     ('estado',      'estados'),
    'norway':     ('fylke',       'fylker'),
    'poland':     ('województwo', 'województwa'),
    'sweden':     ('län',         'län'),
}

# ─── #738 Iceland Hungarian residue cleanup ────────────────────────────────────
ICELAND_REPLACEMENTS = [
    # NUTS-3 Megye → Landshluti (admin + regional + index + data labels)
    ('NUTS-3 Megyék', 'Landshluti'),
    ('NUTS-3 Megye',  'Landshluti'),
    ('NUTS-3 landshluti', 'Landshluti'),
    ('landshluti Megyék', 'landshluti'),
    # Reykjavík + Pest is Hungarian residue (Pest is a Budapest district)
    ('Reykjavík + Pest + 18 landshluti', 'Höfuðborgarsvæðið + 7 other landshluti'),
    # "3,155 települések" is Hungarian "settlements" — Iceland has ~80 sveitarfélög
    ('3,155 települések', '~80 sveitarfélög'),
    # "—+II geothermal corridor" — drop placeholder
    ('—+II geothermal corridor included. ', ''),
    ('—+II geothermal corridor, ', ''),
    ('—+II geothermal corridor', 'Hellisheiði + Nesjavellir geothermal corridor'),
    ('Orkustofnun + Landsnet + — oversight', 'Orkustofnun + Landsnet oversight'),
    # the placeholder for —+II in intelligence_teaser
    (', the\n  —+II geothermal corridor', ''),
    (', the —+II geothermal corridor', ', the Hellisheiði + Nesjavellir geothermal corridor'),
    # "+ Landsvirkjun/E.ON" — E.ON isn't an Icelandic DSO; should be RARIK + Veitur + HS Veitur
    ('Landsvirkjun/E.ON heritage', 'Landsvirkjun heritage with RARIK + Veitur + HS Veitur DSO network'),
    ('Landsvirkjun + E.ON distribution', 'RARIK + Veitur + HS Veitur distribution'),
    ('Landsvirkjun/E.ON distribution', 'RARIK + Veitur + HS Veitur distribution'),
    # remove the "(traditional regions, 2 NUTS-3)" parenthetical clutter — IS uses landshluti
    (' (traditional regions, 2 NUTS-3)', ''),
]

# ─── #738 Korea Hungarian residue cleanup ──────────────────────────────────────
KOREA_REPLACEMENTS = [
    # NUTS-3 Megye → Do/Si
    ('NUTS-3 Megyék', 'Do/Si'),
    ('NUTS-3 Megye',  'Do/Si'),
    ('Megyék', ''),  # bare "Megyék" plural remnant
    # "Samsung-SK Hynix geothermal" — Korea is peninsular, no geothermal context
    ('Samsung-SK Hynix geothermal oversight', 'Samsung-SK Hynix fab corridor demand'),
    # "KEPCO/KEPCO heritage" — duplicate KEPCO
    ('KPX/KEPCO + KEPCO/KEPCO heritage', 'KPX/KEPCO transmission + KEPCO single-DSO heritage'),
    # "17 do/si Megyék" → "17 do/si"
    ('17 do/si Megyék', '17 do/si'),
]

# ─── #755 LV/LT casing (NUTS-3 region → NUTS-3 Region) ─────────────────────────
LVLT_REPLACEMENTS = [
    ('NUTS-3 regions', 'NUTS-3 Regions'),
    ('NUTS-3 region', 'NUTS-3 Region'),
]


def apply_replacements(text, repls):
    """Apply (find, replace) tuples sequentially."""
    for find, repl in repls:
        text = text.replace(find, repl)
    return text


def load_cfg(slug):
    return yaml.safe_load((CONFIG_DIR / f"{slug}.yaml").read_text())


def save_cfg(slug, cfg):
    """Save preserving canonical key ordering."""
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data','methodology','index','esg_report','intelligence'):
        if k in cfg:
            new_order[k] = cfg[k]
    for k, v in cfg.items():
        if k not in new_order:
            new_order[k] = v
    if not DRY_RUN:
        (CONFIG_DIR / f"{slug}.yaml").write_text(
            yaml.safe_dump(new_order, sort_keys=False, allow_unicode=True)
        )


def cfg_text_replace(slug, repls):
    """Apply text-level replacements to the entire yaml file (works through YAML structure)."""
    path = CONFIG_DIR / f"{slug}.yaml"
    text = path.read_text()
    original = text
    text = apply_replacements(text, repls)
    if text != original and not DRY_RUN:
        path.write_text(text)
    return text != original


def main():
    changes = []

    # 1. #743 country_adjective fixes
    print("\n--- #743 country_adjective fixes ---")
    for slug, adj in COUNTRY_ADJ.items():
        cfg = load_cfg(slug)
        old = cfg.get('data', {}).get('country_adjective', '?')
        if old != adj:
            cfg['data']['country_adjective'] = adj
            save_cfg(slug, cfg)
            print(f"  {slug:<14} {old!r:>16} → {adj!r}")
            changes.append((slug, '#743 country_adjective'))

    # 2. #745 substation placeholder fixes
    print("\n--- #745 substation placeholder fixes ---")
    for slug, (sing, plur) in ADMIN_LABEL_FIXES.items():
        cfg = load_cfg(slug)
        method = cfg.get('methodology', {})
        old_s = method.get('admin_label_singular_lower', '?')
        old_p = method.get('admin_label_plural_lower', '?')
        if old_s != sing or old_p != plur:
            method['admin_label_singular_lower'] = sing
            method['admin_label_plural_lower'] = plur
            save_cfg(slug, cfg)
            print(f"  {slug:<14} {old_s!r:>14}/{old_p!r:<14} → {sing!r}/{plur!r}")
            changes.append((slug, '#745 admin_label'))

    # 3. #745 Italy département → regione
    print("\n--- #745 Italy département → regione ---")
    cfg = load_cfg('italy')
    method = cfg.get('methodology', {})
    if method.get('admin_label_singular_lower') == 'département':
        method['admin_label_singular_lower'] = 'regione'
        method['admin_label_plural_lower'] = 'regioni'
        save_cfg('italy', cfg)
        print(f"  italy          département/départements → regione/regioni")
        changes.append(('italy', '#745 Italy France-leakage'))

    # 4. #745 Costa Rica "Provincia provincia" → "Provincia"
    print("\n--- #745 Costa Rica garbled ---")
    if cfg_text_replace('costa-rica', [
        ('Select Provincia provincia above', 'Select Provincia above'),
        ('admin_label_singular_lower: Provincia provincia', 'admin_label_singular_lower: provincia'),
        # Iceland prose leakage in custom_ingest_html
        ('ARESEP raforkutölfræði', 'ARESEP'),
        ('CNFL + ICE direct + HS CNFL DSO', 'CNFL + ICE distribution + Coopelesca/Coopeguanacaste cooperatives'),
        ('INEC provincia regional accounts', 'INEC regional accounts'),
        ('IMN (IMO/OVF) consolidated meteorology + hydrology + seismic + volcanic',
         'IMN consolidated meteorology + hydrology + OVSICORI seismic + volcanic'),
        ('Þjórsá/Sog Q100', 'Reventazón + Tárcoles + Térraba Q100'),
        ('Iceland is NOT an ENTSO-E member (insular grid)',
         'Costa Rica is part of SIEPAC regional interconnect (Central American grid)'),
        # also any stray Hungarian/Icelandic terms
        ('CERT-IS + Fjarskiptastofa', 'CSIRT-CR + SUTEL'),
    ]):
        print(f"  costa-rica     scrubbed Iceland/Hungarian prose")
        changes.append(('costa-rica', '#745 Iceland prose scrub'))

    # 5. #745 Switzerland NUTS-3 landshluti + Iceland prose scrub
    print("\n--- #745 Switzerland Iceland prose scrub ---")
    cfg = load_cfg('switzerland')
    method = cfg.get('methodology', {})
    method['admin_label_singular_lower'] = 'canton'
    method['admin_label_plural_lower'] = 'cantons'
    method['regulator_acronym'] = 'ElCom'
    method['ingest_sources_prose'] = (
        'Swissgrid network statement, ElCom quality reports, BFE/OFEN energy office statistics, '
        'BFS/OFS regional accounts, SNB national accounts, MeteoSwiss meteorology, '
        'BAFU/OFEV hydrology + flood mapping, SED seismology, NCSC + MELANI cyber, '
        'Copernicus, ENTSO-E, Eurostat, OSM Overpass'
    )
    method['data_sources_country'] = 'Switzerland'
    save_cfg('switzerland', cfg)
    print(f"  switzerland    admin/regulator/prose all scrubbed (Iceland → Swiss agencies)")
    changes.append(('switzerland', '#745 Iceland prose scrub'))

    # 7. #751 esg-report edition_badge normalize to greenfield form
    print("\n--- #751 esg-report edition_badge normalize ---")
    for path in sorted(CONFIG_DIR.glob('*.yaml')):
        slug = path.stem
        cfg = load_cfg(slug)
        esg = cfg.get('esg_report', {})
        badge = esg.get('edition_badge', '')
        country_name = cfg.get('country_name', slug.upper())
        country_upper = country_name.upper()
        # If badge already has COUNTRY EDITION, skip (greenfield form)
        if ' EDITION ' in badge.upper() and slug.replace('-','').lower() in badge.lower().replace('-',''):
            continue
        # Greenland is bespoke (sage color, SESSION 1) — leave alone
        if slug == 'greenland':
            continue
        # Build normalized badge
        new_badge = f'ANNUAL ESG DISCLOSURE — REPORTING PERIOD 2025 · {country_upper} EDITION 01'
        if badge and badge != new_badge:
            esg['edition_badge'] = new_badge
            save_cfg(slug, cfg)
            print(f"  {slug:<14} → ...· {country_upper} EDITION 01")
            changes.append((slug, '#751 edition_badge normalize'))

    # 8. #738 Iceland Hungarian residue cleanup
    print("\n--- #738 Iceland Hungarian residue scrub ---")
    if cfg_text_replace('iceland', ICELAND_REPLACEMENTS):
        print(f"  iceland        applied {len(ICELAND_REPLACEMENTS)} replacements")
        changes.append(('iceland', '#738 Hungarian residue scrub'))

    # Also fix admin block in iceland.yaml (the substring "NUTS-3 Megye" got replaced
    # but admin.short stays as the value used to be — let me explicitly set it)
    cfg = load_cfg('iceland')
    cfg['admin']['level_label_singular'] = 'Landshluti'
    cfg['admin']['level_label_plural'] = 'Landshluti'
    cfg['admin']['short'] = 'Landshluti'
    save_cfg('iceland', cfg)
    print(f"  iceland        admin block set to Landshluti")

    # 9. #738 Korea Hungarian residue cleanup
    print("\n--- #738 Korea Hungarian residue scrub ---")
    if cfg_text_replace('korea', KOREA_REPLACEMENTS):
        print(f"  korea          applied {len(KOREA_REPLACEMENTS)} replacements")
        changes.append(('korea', '#738 Hungarian residue scrub'))

    # Also fix admin block in korea.yaml
    cfg = load_cfg('korea')
    cfg['admin']['level_label_singular'] = 'Do/Si'
    cfg['admin']['level_label_plural'] = 'Do/Si'
    cfg['admin']['short'] = 'Do/Si'
    save_cfg('korea', cfg)
    print(f"  korea          admin block set to Do/Si")

    # 10. #755 LV/LT casing
    print("\n--- #755 LV/LT NUTS-3 region capitalize ---")
    for slug in ['latvia', 'lithuania']:
        if cfg_text_replace(slug, LVLT_REPLACEMENTS):
            print(f"  {slug:<14} NUTS-3 region → NUTS-3 Region (and plural)")
            changes.append((slug, '#755 LV/LT casing'))

    # Summary
    print(f"\n=== SUMMARY ({len(changes)} edits across {len(set(c[0] for c in changes))} countries) ===")
    print(f"Dry-run: {DRY_RUN}")


if __name__ == '__main__':
    main()
