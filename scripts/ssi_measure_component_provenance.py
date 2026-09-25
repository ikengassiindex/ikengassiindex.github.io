#!/usr/bin/env python3
"""Measure the signature of C,V,I,E,S,T across jurisdictions.

For each component: n present, distinct values, count exactly 0.0 / 1.0 / 0.5,
min, max, and whether the value reproduces from det_var(sid+name, <region>_base)
(the score-country.py MD5 generator) or from vary(0.35, name+'_'+K, 0.30)
(the enrich_esg_gaps.py MD5 generator).

Reads only. Writes nothing.
"""
import json, sys, hashlib, collections, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts._ssi_data_shard_reader import load_ssi_data

KEYS = ['C','V','I','E','S','T']

def det_var(seed, base, pct=0.15):
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return base * (1 + (h*2-1)*pct)

def stable_hash(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

def vary(base, sub_name, spread=0.15):
    h = stable_hash(sub_name)
    return round(base * (1.0 + (h-0.5)*2*spread), 4)

def load_cfg(slug):
    p = os.path.join('data', f'{slug}_config.json')
    if os.path.exists(p):
        try: return json.load(open(p))
        except Exception: return None
    return None

def measure(slug):
    _, subs, _ = load_ssi_data(slug)
    n = len(subs)
    cfg = load_cfg(slug)
    regs = (cfg or {}).get('regions', {})
    dflt = (cfg or {}).get('default_region', {})
    alpha = (cfg or {}).get('seismic_alpha', 0.55)
    out = {'slug': slug, 'n': n, 'has_config': cfg is not None, 'components': {}}
    counters = {k: collections.Counter() for k in KEYS}
    missing = 0
    det_hit = {k: 0 for k in KEYS}
    vary_hit = {k: 0 for k in KEYS}
    det_elig = 0
    for s in subs:
        comp = s.get('components')
        if not comp:
            missing += 1
            continue
        for k in KEYS:
            counters[k][comp.get(k)] += 1
        name = s.get('name') or ''
        for k in KEYS:
            v = comp.get(k)
            if v is None: continue
            if abs(float(v) - vary(0.35, f'{name}_{k}', 0.30)) < 5e-5:
                vary_hit[k] += 1
        if cfg is not None:
            sid = s.get('substation_id') or ''
            region = s.get('region') or s.get('region_code') or ''
            ref = regs.get(region, dflt)
            seed = sid + name
            exp = {
                'C': max(0.05, min(0.95, det_var(seed+'C', ref.get('C_base',0.45), 0.35))),
                'V': max(0.05, min(0.95, det_var(seed+'V', ref.get('V_base',0.35), 0.40))),
                'I': max(0.05, min(0.95, det_var(seed+'I', ref.get('I_base',0.35), 0.30))),
                'E': max(0.05, min(0.95, det_var(seed+'E', ref.get('E_base',0.35), 0.25))),
                'S': max(0.10, min(0.95, det_var(seed+'S', min(0.85, ref.get('pga_base',0.1)*alpha*2), 0.20))),
                'T': max(0.05, min(0.95, det_var(seed+'T', ref.get('T_base',0.3), 0.30))),
            }
            det_elig += 1
            for k in KEYS:
                v = comp.get(k)
                if v is not None and abs(float(v)-exp[k]) < 5e-5:
                    det_hit[k] += 1
    out['empty_components'] = missing
    present = n - missing
    for k in KEYS:
        c = counters[k]
        vals = [v for v in c if v is not None]
        out['components'][k] = {
            'present': present - c.get(None, 0),
            'null': c.get(None, 0),
            'distinct': len(vals),
            'at_0': c.get(0.0, 0),
            'at_1': c.get(1.0, 0),
            'at_0.5': c.get(0.5, 0),
            'min': min(vals) if vals else None,
            'max': max(vals) if vals else None,
            'det_var_pct': round(100.0*det_hit[k]/det_elig, 1) if det_elig else None,
            'vary_pct': round(100.0*vary_hit[k]/present, 1) if present else None,
        }
    return out

if __name__ == '__main__':
    res = []
    for slug in sys.argv[1:]:
        try:
            res.append(measure(slug))
        except Exception as e:
            res.append({'slug': slug, 'error': f'{type(e).__name__}: {e}'})
    print(json.dumps(res, indent=1))
