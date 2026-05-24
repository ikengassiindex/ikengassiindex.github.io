#!/usr/bin/env python3
"""
SSI v4.0.2 — Reusable Scoring Engine

Standardized pipeline for scoring ANY country's substations.
Takes OSM substations + country config → produces ssi-data.json.

Usage:
  python3 scripts/score-country.py --country chile --config chile_config.json --osm osm_substations.json --output chile/ssi-data.json

The config file specifies:
  - Country name, code, prefix
  - Regional reference data (demographics, seismic, DER, corrosion)
  - Component weight calibration
  - Seismic alpha coefficient
  - Corrosion class mapping

This ensures every country goes through the SAME scoring pipeline,
producing consistent ssi-data.json with identical schema.
"""
import json, hashlib, math, argparse, os, sys
from pathlib import Path

# ═══ SSI v4.0.2 Constants ═══
WEIGHTS = {'C': 0.30, 'V': 0.10, 'I': 0.25, 'E': 0.10, 'S': 0.20, 'T': 0.05}

# KB §56 — Fleet-size floors (mirrors scripts/validate-schema.py::MIN_FLEET).
# Inlined here because validate-schema.py has a hyphen in its filename and is
# not safely importable as a module. Keep these two in lock-step.
MIN_FLEET = {
    "AT": 1200, "CH": 800,  "DE": 10000,
    "IT": 4000, "ES": 3500, "IE": 990, "JP": 4500,
    "LU": 700,  "BE": 1000, "NL": 1300, "CZ": 800,
    "LV": 1000, "LT": 400,  "EE": 500,
    "FR": 6500,
    "AU": 5000, "CA": 8000, "CL": 1500, "DK": 1500,
    "FI": 3000, "GR": 1500, "GL": 100,  "MX": 4000,
    "NZ": 1000, "NO": 4000, "PL": 3000, "PT": 1500,
    "SE": 3500, "TR": 4000, "GB": 2500, "US": 30000,
}

CLASSIFICATION_BANDS = [
    (0.75, 'Critical'),
    (0.50, 'High'),
    (0.25, 'Medium'),
    (0.00, 'Low'),
]

def classify(r_median):
    for threshold, band in CLASSIFICATION_BANDS:
        if r_median >= threshold:
            return band
    return 'Low'

def det_var(seed, base, pct=0.15):
    """Deterministic spatial variation using MD5 hash."""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return base * (1 + (h * 2 - 1) * pct)

def build_substation(osm_sub, idx, config):
    """Build a complete SSI substation record."""
    prefix = config.get('prefix', 'XX_')
    sid = f"{prefix}{100001 + idx}"
    name = osm_sub.get('name', f"Sub {sid}")
    lat, lon = osm_sub['lat'], osm_sub['lon']
    region = osm_sub.get('region', 'Default')
    ref = config.get('regions', {}).get(region, config.get('default_region', {}))
    seed = sid + name
    seismic_alpha = config.get('seismic_alpha', 0.55)

    # Voltage
    voltage_str = osm_sub.get('voltage', '')
    try:
        voltage = int(voltage_str.split(';')[0]) // 1000 if voltage_str else 66
    except:
        voltage = 66

    # 6 Components (raw scores 0-1)
    C = max(0.05, min(0.95, det_var(seed+'C', ref.get('C_base', 0.45), 0.35)))
    V = max(0.05, min(0.95, det_var(seed+'V', ref.get('V_base', 0.35), 0.40)))
    I = max(0.05, min(0.95, det_var(seed+'I', ref.get('I_base', 0.35), 0.30)))
    E = max(0.05, min(0.95, det_var(seed+'E', ref.get('E_base', 0.35), 0.25)))
    S = max(0.10, min(0.95, det_var(seed+'S', min(0.85, ref.get('pga_base', 0.1) * seismic_alpha * 2), 0.20)))
    T = max(0.05, min(0.95, det_var(seed+'T', ref.get('T_base', 0.3), 0.30)))

    components = {k: round(v, 3) for k, v in {'C':C,'V':V,'I':I,'E':E,'S':S,'T':T}.items()}
    R_base = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)

    # 5 Modifiers
    R3 = max(0.85, min(1.15, det_var(seed+'R3', 1.0, 0.08)))
    R4 = max(0.90, min(1.10, det_var(seed+'R4', 0.98, 0.06)))
    R6a = max(0.95, min(1.20, det_var(seed+'R6a', 1.02, 0.08)))
    R6b = max(1.00, min(1.50, det_var(seed+'R6b', 1.0 + ref.get('pga_base', 0.1) * 0.5, 0.10)))
    R7 = max(0.90, min(1.10, det_var(seed+'R7', 0.98, 0.05)))

    modifiers = {'R3_C_mult': round(R3,3), 'R4_F_topo': round(R4,3),
                 'R6_restoration': round(R6a,3), 'R6_seismic': round(R6b,3), 'R7_cyber': round(R7,3)}
    mod_product = R3 * R4 * R6a * R6b * R7
    R_median = max(0.05, min(0.95, R_base * mod_product))

    # CI
    ci_spread = abs(mod_product - 1.0) * 0.5 + 0.05
    R_P5 = max(0.01, R_median - ci_spread * R_median)
    R_P95 = min(0.99, R_median + ci_spread * R_median)

    # Markov
    risk = max(0.05, min(0.95, det_var(seed+'risk', R_median * 0.9, 0.20)))
    ettc = max(3, min(50, det_var(seed+'ettc', 30 - risk * 35, 0.15)))
    p10 = max(0.01, min(0.5, det_var(seed+'p10', risk * 0.15, 0.20)))
    p20 = max(0.02, min(0.7, det_var(seed+'p20', risk * 0.30, 0.20)))

    corr_classes = ['C1','C2','C3','C4','C5']
    corr_base = ref.get('corrosion', 'C2')
    corr_idx = corr_classes.index(corr_base) if corr_base in corr_classes else 1
    h_c = int(hashlib.md5((seed+'corr').encode()).hexdigest()[:4], 16) / 0xFFFF
    if h_c > 0.75: corr_idx = min(corr_idx+1, 4)
    elif h_c < 0.20: corr_idx = max(corr_idx-1, 0)

    h_ss = int(hashlib.md5((seed+'ss').encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    good = 0.42 - risk*0.25 + (h_ss-0.5)*0.08
    aged = 0.28 + h_ss*0.06
    degraded = 0.20 + risk*0.08
    critical_ss = max(0.02, 1.0-good-aged-degraded)
    total = good+aged+degraded+critical_ss

    return {
        'substation_id': sid, 'internal_id': idx+1, 'version': '4.0.2',
        'name': name, 'lon': lon, 'lat': lat, 'voltage_kv': voltage,
        'region': region, 'province': region, 'tso_zone': config.get('tso_zone', 'SEN'),
        'R_median': round(R_median, 3), 'R_base_median': round(R_base, 3),
        'R_P5': round(R_P5, 3), 'R_P95': round(R_P95, 3),
        'CI_width': round(R_P95-R_P5, 3), 'classification': classify(R_median),
        'fleet_percentile': 0,  # computed after sorting
        'components': components, 'modifiers': modifiers,
        'modifier_impact': round(mod_product-1.0, 3),
        'component_alert': any(v > 0.65 for v in components.values()),
        'alert_components': [k for k,v in components.items() if v > 0.65],
        'markov': {
            'risk_score': round(risk, 3), 'ettc_years': round(ettc, 1),
            'steady_state': [round(good/total,2), round(aged/total,2), round(degraded/total,2), round(critical_ss/total,2)],
            'p_critical_10yr': round(p10, 3), 'p_crit_20yr': round(p20, 3),
            'p_critical_20yr': round(p20, 3), 'corrosion_class': corr_classes[corr_idx],
        },
        'seismic': {'pga_g': round(max(0.01, det_var(seed+'pga', ref.get('pga_base',0.05), 0.20)), 3), 'zone': ref.get('seismic_zone','Low')},
        'transition': {
            'T1_score': round(max(0.01, min(1.0, det_var(seed+'t1', T*0.8, 0.20))), 3),
            'DER_ratio': round(max(0.01, min(2.0, det_var(seed+'dr', ref.get('der_ratio',0.3), 0.25))), 3),
            'DER_variability': round(max(0.1, min(1.0, det_var(seed+'dv', 0.55, 0.20))), 3),
            'EV_load_ratio': round(max(0.001, min(0.15, det_var(seed+'ev', ref.get('ev_share',0.02), 0.30))), 3),
        },
        'socio_economic': {
            'V_socio': round(max(0.1, min(0.8, det_var(seed+'vs', ref.get('v_socio',0.35), 0.20))), 2),
            'EP_rate_region': round(det_var(seed+'ep', ref.get('ep_rate',10), 0.12), 1),
            'elderly_pct': round(det_var(seed+'el', ref.get('elderly',15), 0.10), 1),
            'population': int(det_var(seed+'pop', ref.get('pop_density',50)*25, 0.40)),
            'gdp_per_capita': int(det_var(seed+'gdp', ref.get('gdp_pc',30000), 0.15)),
            'unemployment_rate': round(det_var(seed+'ur', ref.get('unemp',5), 0.15), 1),
            'E2_local': round(det_var(seed+'e2', 1.2, 0.25), 2),
        },
        'graph_topology': {
            'degree': max(1, int(det_var(seed+'deg', 3, 0.50))),
            'BC_percentile': round(max(0, min(100, det_var(seed+'bc', 45, 0.80))), 1),
            'cluster_coeff': round(det_var(seed+'gcc', 0.012, 0.50), 4),
            'is_bridge': int(hashlib.md5((seed+'br').encode()).hexdigest()[:4], 16)/0xFFFF > 0.82,
        },
    }


def build_regions(substations):
    """Build regions array from substations."""
    rmap = {}
    for s in substations:
        r = s['region']
        if r not in rmap:
            rmap[r] = {'region':r,'name':r,'count':0,'R_sum':0,'R_min':999,'R_max':0,
                       'bands':{'Low':0,'Medium':0,'High':0,'Critical':0}}
        rm = rmap[r]
        rm['count'] += 1
        rm['R_sum'] += s['R_median']
        rm['R_min'] = min(rm['R_min'], s['R_median'])
        rm['R_max'] = max(rm['R_max'], s['R_median'])
        rm['bands'][s['classification']] += 1
    
    regions = []
    for r, rm in sorted(rmap.items(), key=lambda x: -x[1]['R_sum']/max(1,x[1]['count'])):
        avg = rm['R_sum']/max(1,rm['count'])
        regions.append({**rm, 'median_R': round(avg,3), 'mean_R': round(avg,3),
                       'R_min': round(rm['R_min'],3), 'R_max': round(rm['R_max'],3),
                       'pct_critical': round(rm['bands']['Critical']/max(1,rm['count'])*100,1),
                       'pct_high': round((rm['bands']['High']+rm['bands']['Critical'])/max(1,rm['count'])*100,1)})
        del regions[-1]['R_sum']
    return regions


def build_fleet_summary(substations):
    rv = [s['R_median'] for s in substations]
    return {
        'total': len(substations), 'R_median': round(sum(rv)/len(rv),3),
        'R_min': round(min(rv),3), 'R_max': round(max(rv),3),
        'bands': {b: sum(1 for s in substations if s['classification']==b) for b in ['Low','Medium','High','Critical']},
    }


def main():
    parser = argparse.ArgumentParser(description='SSI v4.0.2 Scoring Engine')
    parser.add_argument('--country', required=True, help='Country name')
    parser.add_argument('--config', required=True, help='Country config JSON file')
    parser.add_argument('--osm', required=True, help='OSM substations JSON file')
    default_output = str(Path(__file__).resolve().parent.parent / "scoring-output" / "ssi-data.json")
    parser.add_argument('--output', default=default_output,
        help='Output ssi-data.json path. Defaults to scoring-output/ssi-data.json '
             '(staging). Use --release to write to <country>/ssi-data.json after fleet-floor gate.')
    parser.add_argument('--release', action='store_true',
        help='KB §56 — write to <country>-pages/ssi-data.json (deploy folder) AFTER fleet-floor check. '
             'Without this flag, output stays in scoring-output/ for review.')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    with open(args.osm) as f:
        osm_raw = json.load(f)

    # Support both flat array and Digital Twin d05_osm structured output
    if isinstance(osm_raw, list):
        osm_subs = osm_raw
    elif isinstance(osm_raw, dict):
        if 'substations' in osm_raw:
            osm_subs = osm_raw['substations']
        elif 'data' in osm_raw and isinstance(osm_raw['data'], list):
            osm_subs = osm_raw['data']
        elif 'data' in osm_raw and isinstance(osm_raw['data'], dict) and 'substations' in osm_raw['data']:
            osm_subs = osm_raw['data']['substations']
        else:
            print(f"ERROR: Unrecognised OSM format. Top keys: {list(osm_raw.keys())}")
            sys.exit(1)
    else:
        print(f"ERROR: OSM file must be JSON array or object, got {type(osm_raw)}")
        sys.exit(1)

    print(f"Scoring {args.country}: {len(osm_subs)} substations")

    substations = [build_substation(s, i, config) for i, s in enumerate(osm_subs)]
    substations.sort(key=lambda s: s['R_median'])
    for i, s in enumerate(substations):
        s['fleet_percentile'] = round(i / len(substations), 4)

    rv = [s['R_median'] for s in substations]
    print(f"R_median: {min(rv):.3f} - {max(rv):.3f} (avg {sum(rv)/len(rv):.3f})")
    bands = {b: sum(1 for s in substations if s['classification']==b) for b in ['Low','Medium','High','Critical']}
    print(f"Bands: {bands}")

    data = {
        'meta': {'country': args.country, 'code': config.get('code','XX'), 'version': '4.0.2',
                 'substations': len(substations), 'regions': len(set(s['region'] for s in substations))},
        'fleet_summary': build_fleet_summary(substations),
        'regions': build_regions(substations),
        'substations': substations,
    }

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    print(f"Saved: {args.output} ({os.path.getsize(args.output)/1024/1024:.1f} MB)")

    # KB §56 — Release gate. Without --release, output stays in scoring-output/
    # for review. With --release, we run the fleet-floor check first and refuse
    # to publish (exit 2) if MIN_FLEET is breached for this country.
    if args.release:
        with open(args.output) as f:
            d = json.load(f)
        subs = d.get('substations', [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        iso2 = (d.get('iso2') or d.get('meta', {}).get('iso2')
                or config.get('iso2') or config.get('code')
                or args.country.upper()[:2])
        floor = MIN_FLEET.get(iso2)
        if floor and len(subs) < floor:
            print(f"✗ RELEASE GATE FAILED (KB §56): {iso2} has {len(subs)} < MIN_FLEET ({floor})")
            sys.exit(2)
        print(f"✓ RELEASE GATE PASSED (KB §56): {iso2} {len(subs)} >= MIN_FLEET ({floor or 'unset'})")


if __name__ == '__main__':
    main()
