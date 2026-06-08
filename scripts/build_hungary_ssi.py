#!/usr/bin/env python3
"""
Build hungary/ssi-data.json from grid-geo.json + data/hungary_config.json
using scripts/score-country.py as the engine, then post-process to:
 - convert socio-economic config values from fractions (0.04) to percentages (4.0)
   so the renderer shows sensible numbers
 - fix province from region code -> human name (with HU diacritics)
 - add kreis (capital), megye_name_hu
 - add confidence_pct / confidence_tiers / band_pct to fleet_summary
 - add R_mean/R_median aliases, P5/P95 aliases
 - add R_base alias, modifier_pct, alert_flag, P_critical, skewness, confidence_tier
 - keep voltage_kv null when missing (per schema)
 - enrich meta with version, country slug, code, generation timestamp,
   variables count, total_departments

⚠️  DEPRECATED (PR-4, audit memo 2026-06-08)
    This wrapper hardcodes Hungary-specific post-processing (NUTS-3 diacritic
    rename + capital lookup + R_base aliasing) in Python. PR-4 extracts the
    declarative data into `intelligence/country-configs/hungary.json` under a
    new `pipeline_enrichment` block.

    PR-7 will retire this wrapper entirely; the canonical pipeline
    (scripts/pipeline/scoring/engine.py + a country dispatcher) will consume
    the declarative enrichment block to reproduce the same ssi-data.json
    shape. The migration is decoupled from PR-4 because the pipeline
    dispatcher doesn't exist yet — but the declarative configs are ready,
    so this script becomes redundant the moment PR-7 lands.

    Until PR-7:
      → This wrapper continues to work unchanged.
      → A deprecation banner prints to stderr at startup.
      → All numerical outputs match the canonical Python pipeline exactly
        (PR-2/PR-3 numpy/registry chain is the underlying engine).
"""
import json
import hashlib
import sys
import datetime
import warnings
from pathlib import Path

# PR-4 deprecation banner — printed to stderr at startup so the operator sees it
# in any invocation context (cron, manual, CI).
print(
    "\n⚠️  DEPRECATED: scripts/build_hungary_ssi.py is slated for retirement in PR-7.\n"
    "    Replacement: python -m scripts.pipeline.run hungary\n"
    "    See intelligence/country-configs/hungary.json::pipeline_enrichment for\n"
    "    the declarative configuration that will drive the canonical pipeline.\n",
    file=sys.stderr,
)
warnings.warn(
    "build_hungary_ssi.py: deprecated in PR-4, retiring in PR-7. "
    "Migrate to: python -m scripts.pipeline.run hungary.",
    DeprecationWarning, stacklevel=2
)

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'scripts'))

# Import score-country.py module (hyphen in name -> need importlib)
import importlib.util
spec = importlib.util.spec_from_file_location("score_country", REPO / "scripts" / "score-country.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

# Load inputs
CONFIG = json.load(open(REPO / 'data' / 'hungary_config.json'))
GRID = json.load(open(REPO / 'hungary' / 'grid-geo.json'))

# ── HU NUTS-3 names with diacritics (config uses ASCII; renderer wants real names)
HU_NAMES_DIACRITIC = {
    'HU110': 'Budapest',
    'HU120': 'Pest',
    'HU211': 'Fejér',
    'HU212': 'Komárom-Esztergom',
    'HU213': 'Veszprém',
    'HU221': 'Győr-Moson-Sopron',
    'HU222': 'Vas',
    'HU223': 'Zala',
    'HU231': 'Baranya',
    'HU232': 'Somogy',
    'HU233': 'Tolna',
    'HU311': 'Borsod-Abaúj-Zemplén',
    'HU312': 'Heves',
    'HU313': 'Nógrád',
    'HU321': 'Hajdú-Bihar',
    'HU322': 'Jász-Nagykun-Szolnok',
    'HU323': 'Szabolcs-Szatmár-Bereg',
    'HU331': 'Bács-Kiskun',
    'HU332': 'Békés',
    'HU333': 'Csongrád-Csanád',
}

# Capitals with diacritics (config has ASCII versions; we want native spelling)
HU_CAPITALS_DIACRITIC = {
    'HU110': 'Budapest',
    'HU120': 'Budapest',
    'HU211': 'Székesfehérvár',
    'HU212': 'Tatabánya',
    'HU213': 'Veszprém',
    'HU221': 'Győr',
    'HU222': 'Szombathely',
    'HU223': 'Zalaegerszeg',
    'HU231': 'Pécs',
    'HU232': 'Kaposvár',
    'HU233': 'Szekszárd',
    'HU311': 'Miskolc',
    'HU312': 'Eger',
    'HU313': 'Salgótarján',
    'HU321': 'Debrecen',
    'HU322': 'Szolnok',
    'HU323': 'Nyíregyháza',
    'HU331': 'Kecskemét',
    'HU332': 'Békéscsaba',
    'HU333': 'Szeged',
}

# Build OSM-style input from canonical compact grid-geo
osm_subs = []
for sid, s in GRID['s'].items():
    v_kv = s.get('v', 0) or 0
    osm_subs.append({
        'osm_id': sid,
        'lat': s.get('y'),
        'lon': s.get('x'),
        'name': s.get('n', '') or '',
        'voltage': str(int(v_kv * 1000)) if v_kv > 0 else '',
        'region': s.get('r', 'HU110'),
    })

print(f"Loaded {len(osm_subs)} substations from grid-geo.json")

# Run the scoring engine
substations = [sc.build_substation(s, i, CONFIG) for i, s in enumerate(osm_subs)]
substations.sort(key=lambda x: x['R_median'])
for i, s in enumerate(substations):
    s['fleet_percentile'] = round(i / len(substations), 4)

REGIONS_CFG = CONFIG.get('regions', {})

def province_name(region_code):
    # Prefer the diacritic table; fall back to config name; fall back to code
    if region_code in HU_NAMES_DIACRITIC:
        return HU_NAMES_DIACRITIC[region_code]
    rc = REGIONS_CFG.get(region_code, {})
    name = rc.get('name', region_code)
    if '(' in name:
        name = name.split('(')[0].strip()
    return name

def kreis_name(region_code):
    if region_code in HU_CAPITALS_DIACRITIC:
        return HU_CAPITALS_DIACRITIC[region_code]
    return REGIONS_CFG.get(region_code, {}).get('capital', '')

# Fleet-wide stats
import statistics
r_values = sorted(s['R_median'] for s in substations)
fleet_median = statistics.median(r_values) if r_values else 0
fleet_mean = statistics.mean(r_values) if r_values else 0

def percentile(arr, p):
    if not arr: return 0
    k = (len(arr) - 1) * (p / 100.0)
    f = int(k); c = min(f + 1, len(arr) - 1)
    return arr[f] + (arr[c] - arr[f]) * (k - f)

fleet_p5 = percentile(r_values, 5)
fleet_p95 = percentile(r_values, 95)

# Post-process each substation
for s in substations:
    region = s['region']
    rcfg = REGIONS_CFG.get(region, CONFIG.get('default_region', {}))

    s['province'] = province_name(region)
    s['kreis'] = kreis_name(region)
    s['megye_name_hu'] = province_name(region)
    s['region_code'] = region
    s['departement'] = s['province']
    s['dept_code'] = region

    osm = osm_subs[s['internal_id'] - 1]
    if not osm.get('voltage'):
        s['voltage_kv'] = None

    s['R_base'] = s['R_base_median']
    s['R_deterministic'] = s['R_base_median']
    s['R_mean'] = s['R_median']

    if s.get('R_base_median'):
        s['modifier_pct'] = round((s['modifier_impact'] / s['R_base_median']) * 100, 1)
    else:
        s['modifier_pct'] = 0.0

    s['band_pct'] = round(s['fleet_percentile'] * 100, 1)
    s['P_critical'] = s['markov'].get('p_critical_20yr', 0)
    s['skewness'] = 0.0

    if s['classification'] == 'Critical':
        s['alert_flag'] = '\U0001F534'
    elif s['component_alert']:
        s['alert_flag'] = '\U0001F7E1'
    else:
        s['alert_flag'] = ''

    s['confidence_tier'] = 'high'
    s['confidence_pct'] = 100.0

    se = s['socio_economic']
    seed = s['substation_id'] + s['name']
    unemp_raw = rcfg.get('unemp', 0.045)
    target_pct = unemp_raw * 100 if unemp_raw < 1.0 else unemp_raw
    h = int(hashlib.md5((seed + 'ur').encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    se['unemployment_rate'] = round(target_pct * (1 + (h * 2 - 1) * 0.15), 1)

    eld_raw = rcfg.get('elderly', 0.20)
    eld_pct = eld_raw * 100 if eld_raw < 1.0 else eld_raw
    h = int(hashlib.md5((seed + 'el').encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    se['elderly_pct'] = round(eld_pct * (1 + (h * 2 - 1) * 0.10), 1)

    # HU R&D % of GDP by NUTS-3 (Eurostat 2023 vintage, approximated)
    # Budapest leads; Central Hungary corridor and Veszprém uni cluster mid;
    # eastern megyék and Békés lag.
    rd_base = {
        'HU110': 2.20, 'HU120': 1.40, 'HU211': 1.30, 'HU212': 1.10,
        'HU213': 1.50, 'HU221': 1.10, 'HU222': 0.80, 'HU223': 0.70,
        'HU231': 0.90, 'HU232': 0.60, 'HU233': 0.70, 'HU311': 1.00,
        'HU312': 0.80, 'HU313': 0.40, 'HU321': 1.30, 'HU322': 0.70,
        'HU323': 0.60, 'HU331': 0.80, 'HU332': 0.40, 'HU333': 1.20,
    }.get(region, 0.95)
    h = int(hashlib.md5((seed + 'rd').encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    se['rd_pct_gdp'] = round(rd_base * (1 + (h * 2 - 1) * 0.20), 2)

    s['seismic']['R6_seismic'] = s['modifiers']['R6_seismic']

# Build regions array
def build_regions(substations):
    rmap = {}
    for s in substations:
        r = s['region']
        if r not in rmap:
            rmap[r] = {
                'region': r,
                'name': province_name(r),
                'kreis': kreis_name(r),
                'count': 0,
                'R_sum': 0,
                'R_min': 999,
                'R_max': 0,
                'R_values': [],
                'bands': {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0},
            }
        rm = rmap[r]
        rm['count'] += 1
        rm['R_sum'] += s['R_median']
        rm['R_min'] = min(rm['R_min'], s['R_median'])
        rm['R_max'] = max(rm['R_max'], s['R_median'])
        rm['R_values'].append(s['R_median'])
        rm['bands'][s['classification']] += 1

    regions = []
    for r, rm in sorted(rmap.items(),
                       key=lambda x: -x[1]['R_sum'] / max(1, x[1]['count'])):
        avg = rm['R_sum'] / max(1, rm['count'])
        rvals = sorted(rm['R_values'])
        med = rvals[len(rvals)//2] if rvals else 0
        regions.append({
            'region': rm['region'],
            'name': rm['name'],
            'kreis': rm['kreis'],
            'count': rm['count'],
            'R_min': round(rm['R_min'], 3),
            'R_max': round(rm['R_max'], 3),
            'bands': rm['bands'],
            'median_R': round(med, 3),
            'mean_R': round(avg, 3),
            'R_median': round(med, 3),
            'pct_critical': round(rm['bands']['Critical'] / max(1, rm['count']) * 100, 1),
            'pct_high': round((rm['bands']['High'] + rm['bands']['Critical']) / max(1, rm['count']) * 100, 1),
        })
    return regions

regions = build_regions(substations)

band_counts = {b: sum(1 for s in substations if s['classification'] == b)
               for b in ['Low', 'Medium', 'High', 'Critical']}
total = len(substations)
band_pct = {b: round(c / total * 100, 1) for b, c in band_counts.items()}

conf_counts = {'high': total, 'medium': 0, 'low': 0}
conf_pct = {'high': 100.0, 'medium': 0.0, 'low': 0.0}

fleet_summary = {
    'total': total,
    'median_R': round(fleet_median, 3),
    'R_median': round(fleet_median, 3),
    'mean_R': round(fleet_mean, 3),
    'R_mean': round(fleet_mean, 3),
    'R_min': round(min(r_values), 3),
    'R_max': round(max(r_values), 3),
    'P5': round(fleet_p5, 3),
    'P95': round(fleet_p95, 3),
    'R_P5': round(fleet_p5, 3),
    'R_P95': round(fleet_p95, 3),
    'bands': band_counts,
    'band_pct': band_pct,
    'confidence_tiers': conf_counts,
    'confidence_pct': conf_pct,
}

meta = {
    'country': 'hungary',
    'code': 'HU',
    'iso2': 'HU',
    'version': '4.0.2',
    'substations': total,
    'regions': len(regions),
    'total_departments': len(regions),
    'variables': 95,
    'mc_iterations': 0,
    'generated': datetime.date.today().isoformat(),
    'generator': 'SSI v4.0.2 Pipeline (Hungary, score-country.py + post-process)',
    'note': f'Substations from OpenStreetMap ({total} nodes), scored at megye level (20 NUTS-3) with deterministic per-substation jitter. R3 5-tier (Budapest 1.02 → Nógrád/Békés 1.07); R6 seismic alpha 0.35 (Pannonian low); MIN_FLEET 2800.',
}

data = {
    'country': 'Hungary',
    'iso2': 'HU',
    'version': '4.0.2',
    'meta': meta,
    'fleet_summary': fleet_summary,
    'regions': regions,
    'substations': substations,
}

out_path = REPO / 'hungary' / 'ssi-data.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

size_mb = out_path.stat().st_size / 1024 / 1024
print(f"\nWrote {out_path} ({size_mb:.2f} MB)")
print(f"Fleet median R: {fleet_summary['median_R']}")
print(f"Fleet mean R:   {fleet_summary['mean_R']}")
print(f"P5-P95: {fleet_summary['P5']} - {fleet_summary['P95']}")
print(f"Bands: {band_counts}")
print(f"Band %: {band_pct}")
print(f"Regions: {len(regions)}")
from collections import Counter
print(f"Per-region: {dict(sorted(Counter(s['region'] for s in substations).items()))}")
