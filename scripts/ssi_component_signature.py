#!/usr/bin/env python3
"""One row per jurisdiction per component, from the published register alone.

VARY-BAND.  scripts/enrich_esg_gaps.py fills an absent component with
    vary(0.35, name+'_'+K, 0.30) = 0.35 * (1 +/- 0.30)
whose image is exactly the closed interval [0.245, 0.455] and nothing else.
A component whose every published value lies in that interval, filling it, is
that generator's output -- a test that survives the substation renames the
dedupe remediations performed, which destroyed the seed but not the output.

MODAL SHARE.  The largest share of records carrying one single value. 100%
means the component is a constant: it enters R_base at full weight and moves
no substation relative to any other.

NORM-PILE.  Records at exactly 0.0 and exactly 1.0. A pile of ~5% at each end
is the signature of a hard-clipped min-max renormalisation on the country's
own P5/P95 -- the value published is then a within-country percentile of
whatever went in, not a quantity.

Reads only. Writes nothing.
"""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYS=['C','V','I','E','S','T']
LO,HI=0.245,0.455

def load(slug, repo='.'):
    d=json.load(open(os.path.join(repo,slug,'ssi-data.json')))
    if d.get('substations'): return d['substations']
    from scripts._ssi_data_shard_reader import load_ssi_data
    _,s,_=load_ssi_data(slug); return s

def measure(slug):
    subs=load(slug)
    n=len(subs); empty=sum(1 for s in subs if not (s.get('components') or {}))
    rows=[]
    for K in KEYS:
        vals=[(s.get('components') or {}).get(K) for s in subs]
        nn=[v for v in vals if v is not None]
        if not nn:
            rows.append({'K':K,'present':0}); continue
        c=collections.Counter(nn)
        inband=sum(1 for v in nn if LO-1e-9 <= v <= HI+1e-9)
        rows.append({'K':K,'present':len(nn),'null':len(vals)-len(nn),
            'distinct':len(c),'min':min(nn),'max':max(nn),
            'vary_band_pct':round(100.0*inband/len(nn),1),
            'modal_pct':round(100.0*c.most_common(1)[0][1]/len(nn),1),
            'modal_val':c.most_common(1)[0][0],
            'at_0':c.get(0.0,0),'at_1':c.get(1.0,0)})
    return {'slug':slug,'n':n,'empty_components':empty,'rows':rows}

if __name__=='__main__':
    out=[]
    for slug in sys.argv[1:]:
        try: out.append(measure(slug))
        except Exception as e: out.append({'slug':slug,'error':f'{type(e).__name__}: {e}'})
    print(json.dumps(out))
