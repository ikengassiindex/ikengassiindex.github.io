#!/usr/bin/env python3
"""Where does each published component C,V,I,E,S,T come from?

For each jurisdiction, every ssi-data.json.<tag> backup on disk is a candidate
preimage. Two tests, both config-free.

TEST A — the transform.  For each candidate backup, is today's value that
backup's value min-max normalised on the country's own P5/P95 with a hard clip?
        published == clip01( (backup - P5) / (P95 - P5) )
matched by substation_id.  Reported: the best-matching backup and its share.
Also reported: IDENTITY, the share where published == backup unchanged.

TEST B — the preimage.  Is the best-matching backup's value the score-country.py
MD5 generator det_var(sid+name+K, base, pct) = base*(1+(h*2-1)*pct)?
base is per-region and unknown; pct is fixed in the source (C .35 V .40 I .30
E .25 S .20 T .30).  Invert: each record implies base = v/(1+(h*2-1)*pct).  If
every record in a region implies the same base, the generator is det_var.
Grouping is tried on `region`, on `province`, and on the whole country; the
best is reported.  Clipped records (at the floor or at 0.95) are excluded and
counted, since the clip destroys the inversion.

TEST B2 — the enrich_esg_gaps.py generator vary(0.35, name+'_'+K, 0.30).

Reads only. Writes nothing.
"""
import json, sys, hashlib, collections, os, glob

KEYS = ['C','V','I','E','S','T']
PCT  = {'C':0.35,'V':0.40,'I':0.30,'E':0.25,'S':0.20,'T':0.30}
FLOOR= {'C':0.05,'V':0.05,'I':0.05,'E':0.05,'S':0.10,'T':0.05}

def h_of(seed):
    return int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

def pctl(sv, q):
    n = len(sv)
    if n == 0: return None
    k = (n-1)*q/100.0; f = int(k); c = min(f+1, n-1)
    return sv[f] + (sv[c]-sv[f])*(k-f)

def vary(base, s, spread):
    return round(base*(1.0+(h_of(s)-0.5)*2*spread), 4)

def load(path):
    with open(path) as f: d = json.load(f)
    return d.get('substations') or []

def load_current(slug, repo):
    p = os.path.join(repo, slug, 'ssi-data.json')
    d = json.load(open(p))
    if d.get('substations'): return d['substations']
    sys.path.insert(0, repo)
    from scripts._ssi_data_shard_reader import load_ssi_data
    _, subs, _ = load_ssi_data(slug)
    return subs

def testB(xs, K):
    best = (0, 0, None)
    for gk in ('region','province','_all'):
        by = collections.defaultdict(collections.Counter)
        clipped = 0
        for i, v, s in xs:
            if abs(v-FLOOR[K]) < 1e-9 or abs(v-0.95) < 1e-9:
                clipped += 1; continue
            f = 1.0 + (h_of((i or '')+(s.get('name') or '')+K)*2-1)*PCT[K]
            if f == 0: continue
            g = '_' if gk == '_all' else (s.get(gk) or s.get('region_code') or 'Default')
            by[g][round(v/f, 4)] += 1
        hit = tot = 0
        for g, c in by.items():
            tot += sum(c.values()); hit += c.most_common(1)[0][1]
        if tot and hit/tot > best[0]/max(best[1],1):
            best = (hit, tot, gk, clipped)
    if best[1] == 0: return None, None, best[2] if len(best)>2 else None
    return 100.0*best[0]/best[1], best[3], best[2]

def measure(slug, repo='.'):
    cur = load_current(slug, repo)
    cur_by = {s.get('substation_id'): s for s in cur}
    baks = sorted(glob.glob(os.path.join(repo, slug, 'ssi-data.json.*')))
    out = {'slug': slug, 'n_current': len(cur), 'backups': [os.path.basename(b).replace('ssi-data.json.','') for b in baks], 'components': {}}
    loaded = []
    for b in baks:
        try: loaded.append((os.path.basename(b).replace('ssi-data.json.',''), load(b)))
        except Exception: pass
    for K in KEYS:
        bestA = {'pct': -1}
        for tag, bak in loaded:
            xs = [(s.get('substation_id'), (s.get('components') or {}).get(K), s) for s in bak]
            xs = [(i,v,s) for i,v,s in xs if v is not None]
            if not xs: continue
            vals = sorted(v for _,v,_ in xs)
            p5, p95 = pctl(vals,5), pctl(vals,95)
            nhit = ihit = tot = 0
            for i,v,_ in xs:
                c = cur_by.get(i)
                if not c: continue
                y = (c.get('components') or {}).get(K)
                if y is None: continue
                tot += 1
                if abs(y-v) < 1.5e-4: ihit += 1
                if p95 is not None and p95 > p5:
                    n = max(0.0, min(1.0, (v-p5)/(p95-p5)))
                    if abs(y-round(n,4)) < 1.5e-4: nhit += 1
            if tot == 0: continue
            pct_n = 100.0*nhit/tot; pct_i = 100.0*ihit/tot
            score = max(pct_n, pct_i)
            if score > bestA['pct']:
                bestA = {'pct': score, 'tag': tag, 'kind': 'NORMALISED' if pct_n >= pct_i else 'IDENTITY',
                         'norm_pct': round(pct_n,1), 'ident_pct': round(pct_i,1), 'n': tot, 'xs': xs}
        if bestA['pct'] < 0:
            out['components'][K] = {'note': 'no comparable backup'}; continue
        xs = bestA.pop('xs')
        bpct, clipped, grouping = testB(xs, K)
        vhit = sum(1 for i,v,s in xs if abs(v - vary(0.35, (s.get('name') or '')+'_'+K, 0.30)) < 5e-5)
        cvals = [(s.get('components') or {}).get(K) for s in cur]
        cnn = [v for v in cvals if v is not None]
        out['components'][K] = {
            'best_backup': bestA['tag'], 'relation': bestA['kind'],
            'norm_pct': bestA['norm_pct'], 'ident_pct': bestA['ident_pct'], 'matched': bestA['n'],
            'preimage_det_var_pct': round(bpct,1) if bpct is not None else None,
            'preimage_grouping': grouping, 'preimage_clipped': clipped,
            'preimage_vary_pct': round(100.0*vhit/len(xs),1) if xs else None,
            'current_distinct': len(set(cnn)), 'current_null': len(cvals)-len(cnn),
            'current_at_0': sum(1 for v in cnn if v == 0.0), 'current_at_1': sum(1 for v in cnn if v == 1.0),
            'current_at_0.5': sum(1 for v in cnn if v == 0.5),
        }
    return out

if __name__ == '__main__':
    res = []
    for slug in sys.argv[1:]:
        try: res.append(measure(slug))
        except Exception as e:
            res.append({'slug': slug, 'error': f'{type(e).__name__}: {e}'})
    print(json.dumps(res, indent=1))
