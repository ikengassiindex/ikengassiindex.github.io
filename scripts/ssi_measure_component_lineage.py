#!/usr/bin/env python3
"""Component lineage: walk every ssi-data.json backup a jurisdiction holds,
oldest first, and report at each hop whether the next value is the previous one
unchanged (=), the previous one min-max normalised on the country's own P5/P95
with a hard clip (N), or neither (x).

At the oldest state, test whether the value is a generator output:
  det  = det_var(sid+name+K, base, pct) from scripts/score-country.py, base
         per region and unknown, so inverted: base = v/(1+(h*2-1)*pct).  All
         records in a region implying one base means the generator is det_var.
  vary = vary(0.35, name+'_'+K, 0.30) from scripts/enrich_esg_gaps.py.

Reads only. Writes nothing.
"""
import json, sys, hashlib, collections, os, glob

KEYS = ['C','V','I','E','S','T']
PCT  = {'C':0.35,'V':0.40,'I':0.30,'E':0.25,'S':0.20,'T':0.30}
FLOOR= {'C':0.05,'V':0.05,'I':0.05,'E':0.05,'S':0.10,'T':0.05}

def h_of(s): return int(hashlib.md5(s.encode()).hexdigest()[:8],16)/0xFFFFFFFF
def pctl(sv,q):
    n=len(sv)
    if not n: return None
    k=(n-1)*q/100.0; f=int(k); c=min(f+1,n-1)
    return sv[f]+(sv[c]-sv[f])*(k-f)
def vary(b,s,sp): return round(b*(1.0+(h_of(s)-0.5)*2*sp),4)

def subs_of(path):
    with open(path) as f: d=json.load(f)
    return d.get('substations') or []

def current(slug, repo):
    d=json.load(open(os.path.join(repo,slug,'ssi-data.json')))
    if d.get('substations'): return d['substations']
    sys.path.insert(0,repo)
    from scripts._ssi_data_shard_reader import load_ssi_data
    _,s,_=load_ssi_data(slug); return s

def hop(prev, nxt, K):
    """prev, nxt: {sid: value}. Returns (relation, pct, n)."""
    vals=sorted(prev.values())
    p5,p95=pctl(vals,5),pctl(vals,95)
    ih=nh=tot=0
    for sid,v in prev.items():
        y=nxt.get(sid)
        if y is None: continue
        tot+=1
        if abs(y-v)<1.5e-4: ih+=1
        if p95 is not None and p95>p5:
            n=max(0.0,min(1.0,(v-p5)/(p95-p5)))
            if abs(y-round(n,4))<1.5e-4: nh+=1
    if not tot: return ('-',None,0)
    pi,pn=100.0*ih/tot,100.0*nh/tot
    if pi>=pn: return ('=',round(pi,1),tot)
    return ('N',round(pn,1),tot)

def gen_tests(recs, K):
    xs=[(sid,v,s) for sid,v,s in recs]
    best=(-1,None,None)
    for gk in ('region','province','_all'):
        by=collections.defaultdict(collections.Counter); clip=0
        for sid,v,s in xs:
            if abs(v-FLOOR[K])<1e-9 or abs(v-0.95)<1e-9: clip+=1; continue
            f=1.0+(h_of((sid or '')+(s.get('name') or '')+K)*2-1)*PCT[K]
            g='_' if gk=='_all' else (s.get(gk) or s.get('region_code') or 'Default')
            by[g][round(v/f,4)]+=1
        hit=tot=0
        for g,c in by.items(): tot+=sum(c.values()); hit+=c.most_common(1)[0][1]
        if tot and 100.0*hit/tot>best[0]: best=(100.0*hit/tot,gk,clip)
    vh=sum(1 for sid,v,s in xs if abs(v-vary(0.35,(s.get('name') or '')+'_'+K,0.30))<5e-5)
    return (round(best[0],1) if best[0]>=0 else None, best[1], best[2],
            round(100.0*vh/len(xs),1) if xs else None)

def measure(slug, repo='.'):
    paths=glob.glob(os.path.join(repo,slug,'ssi-data.json.*'))
    paths=[p for p in paths if os.path.isfile(p)]
    paths.sort(key=lambda p: os.path.getmtime(p))
    states=[]
    for p in paths:
        try: states.append((os.path.basename(p).replace('ssi-data.json.',''), subs_of(p)))
        except Exception: pass
    states.append(('NOW', current(slug, repo)))
    out={'slug':slug,'order':[t for t,_ in states],'n':[len(s) for _,s in states],'components':{}}
    for K in KEYS:
        maps=[]
        for tag,subs in states:
            m={}; recs=[]
            for s in subs:
                v=(s.get('components') or {}).get(K)
                if v is None: continue
                sid=s.get('substation_id')
                m[sid]=v
                oid=s.get('osm_id') or s.get('osm_feature_id')
                if oid: m['osm:'+str(oid)]=v
                if s.get('lat') is not None and s.get('lon') is not None:
                    m[f"xy:{round(float(s['lat']),5)},{round(float(s['lon']),5)}"]=v
                recs.append((sid,v,s))
            maps.append((tag,m,recs))
        chain=[]
        for i in range(len(maps)-1):
            r,p,n=hop(maps[i][1],maps[i+1][1],K)
            chain.append(f"{r}{'' if p is None else int(round(p))}@{n}")
        gens=[]
        for tag,m,recs in maps:
            if not recs: gens.append({'state':tag,'n':0,'det':None,'vary':None,'distinct':0}); continue
            g=gen_tests(recs,K)
            gens.append({'state':tag,'n':len(recs),'det':g[0],'grp':g[1],'clip':g[2],
                         'vary':g[3],'distinct':len(set(v for _,v,_ in recs))})
        out['components'][K]={'states':gens,'chain':chain}
    return out

if __name__=='__main__':
    res=[]
    for slug in sys.argv[1:]:
        try: res.append(measure(slug))
        except Exception as e: res.append({'slug':slug,'error':f'{type(e).__name__}: {e}'})
    print(json.dumps(res,indent=1))
