#!/usr/bin/env python3
"""
Phase 0 — every numeric field, every country, tested against every known
fabrication mechanism. Writes nothing to the register.

    python3 scripts/ssi_provenance_sweep.py --all --out SWEEP.json
    python3 scripts/ssi_provenance_sweep.py france norway --verbose
    python3 scripts/ssi_provenance_sweep.py --all --out SWEEP.json --resume

WHY THIS EXISTS
---------------
On 29 August 2026 six derived blocks were reported as carrying "real" data on
87% of records — graph_topology, markov, seismic, socio_economic,
climate_trajectory, transition. One of the six was then tested. `transition`
turned out to be vary(base, name, spread) for the nine largest countries:
france's DER_ratio is vary(0.48, name, 0.25), italy's is vary(0.61, name, 0.25).
A component was derived from those inputs and committed before the test was
run, and had to be reverted (124b1624).

The other five blocks have never been tested. Neither have the modifiers. The
claim that they are real rests on the same reasoning that failed: the fields
look plausible, they carry provenance-shaped keys, and nobody checked.

This sweep checks. Every numeric leaf on the record, against every mechanism
whose code is in the tree and can therefore be reproduced exactly.

THE MECHANISMS
--------------
  NAME_HASH   enrich_esg_gaps.vary(base, name, spread)
              = base * (1 + (stable_hash(name) - 0.5) * 2 * spread)
              An exact affine function of stable_hash(name), so a fabricated
              field correlates with that hash at |r| = 1.000. This is the one
              that produced the components (456,200 records) and the transition
              block in nine countries.

  SEED_HASH   score-country.det_var(seed, base, pct)
              = base * (1 + (md5(seed)[:8]/0xFFFFFFFF * 2 - 1) * pct),
              seed = substation_id + name. The greenfield onboarding path.
              Tested against several seed spellings because the v4.23
              re-ingestion reassigned substation ids, so the original seed may
              no longer exist on the record.

  CONSTANT    one distinct value across the country — no per-substation
              information at all, whatever its provenance.

  REGION_CONST  constant within each region: a regional reference value joined
              to substations. NOT fabrication — this is the documented-proxy
              pattern of Convention #7 — but it is not a per-substation
              measurement either, and the distinction matters for any formula
              that assumes substation-level variation.

  UNIQUE      as many distinct values as records. Consistent with a real
              per-substation measurement AND with an untested synthesis. It is
              reported as a shape, never as a verdict.

VERDICTS
--------
  FABRICATED    matches NAME_HASH or SEED_HASH at |r| > 0.99
  CONSTANT / REGION_CONST / DEGENERATE   as above
  UNESTABLISHED matches no known mechanism. This is NOT "real" — it means the
                mechanisms we can reproduce do not explain it. Convention #56
                applied to our own knowledge: say what we do not know.

Sampling: up to SAMPLE records per country, drawn with a fixed seed. An exact
affine relationship shows |r| = 1.000 on any sample; sampling cannot hide it.
The sample size used is recorded per country in the output.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = 6000
R_HASH = 0.99

sys.path.insert(0, str(ROOT / "scripts"))
from enrich_esg_gaps import stable_hash                              # noqa: E402


def md5h(seed):
    return int(hashlib.md5(str(seed).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_substations(slug):
    m = json.loads((ROOT / slug / "ssi-data.json").read_text())
    shards = m.get("substations_shards")
    if not shards:
        subs = m.get("substations")
        if subs is None:
            raise ValueError("manifest has neither substations nor shards")
        return subs
    out = []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        out.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
    if not out:
        raise ValueError(f"{len(shards)} shards declared but no records read")
    return out


def numeric_paths(subs, probe=400):
    """Every numeric leaf path, to two levels."""
    seen = collections.Counter()
    for s in subs[:probe]:
        for k, v in s.items():
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                seen[k] += 1
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, bool):
                        continue
                    if isinstance(v2, (int, float)):
                        seen[f"{k}.{k2}"] += 1
    return [p for p, n in seen.items() if n >= probe * 0.5]


def get(s, path):
    if "." in path:
        a, b = path.split(".", 1)
        d = s.get(a)
        return d.get(b) if isinstance(d, dict) else None
    return s.get(path)


def pearson(x, y):
    n = len(x)
    if n < 50:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x)
    sy = sum((b - my) ** 2 for b in y)
    if sx <= 0 or sy <= 0:
        return None
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / math.sqrt(sx * sy)


def classify(slug, subs, path):
    rows = [(s, get(s, path)) for s in subs]
    rows = [(s, v) for s, v in rows if isinstance(v, (int, float))
            and not isinstance(v, bool)]
    n = len(rows)
    if n < 50:
        return {"verdict": "TOO_FEW", "n": n}
    vals = [v for _, v in rows]
    distinct = len(set(vals))
    if distinct == 1:
        return {"verdict": "CONSTANT", "n": n, "distinct": 1, "value": vals[0]}

    seeds = {}
    named = [(s, v) for s, v in rows if s.get("name") is not None]
    leaf = path.split(".")[-1]
    if len(named) >= 50:
        seeds["name"] = ([stable_hash(s["name"]) for s, _ in named],
                         [v for _, v in named])
        # The components' own mechanism: vary(0.35, name + '_' + KEY, 0.30).
        # Seeded on the field name, not the record name. The first version of
        # this sweep omitted it and reported components as UNESTABLISHED — a
        # false negative on the exact defect that prompted the sweep.
        seeds[f"name_{leaf}"] = (
            [stable_hash(f"{s['name']}_{leaf}") for s, _ in named],
            [v for _, v in named])
        seeds[f"name_{leaf}_md5"] = (
            [md5h(f"{s['name']}_{leaf}") for s, _ in named],
            [v for _, v in named])
        seeds["name_md5"] = ([md5h(s["name"]) for s, _ in named],
                             [v for _, v in named])
        ided = [(s, v) for s, v in named if s.get("substation_id") is not None]
        if len(ided) >= 50:
            seeds["id+name_md5"] = (
                [md5h(f"{s['substation_id']}{s['name']}") for s, _ in ided],
                [v for _, v in ided])
            # det_var's seed is sid + name, then the component letter appended.
            seeds[f"id+name+{leaf}_md5"] = (
                [md5h(f"{s['substation_id']}{s['name']}{leaf}") for s, _ in ided],
                [v for _, v in ided])
    ided = [(s, v) for s, v in rows if s.get("substation_id") is not None]
    if len(ided) >= 50:
        seeds["id"] = ([stable_hash(str(s["substation_id"])) for s, _ in ided],
                       [v for _, v in ided])

    best = (0.0, None)
    for label, (h, v) in seeds.items():
        r = pearson(h, v)
        if r is not None and abs(r) > best[0]:
            best = (abs(r), label)
    if best[0] > R_HASH:
        return {"verdict": "FABRICATED", "n": n, "distinct": distinct,
                "mechanism": best[1], "r": round(best[0], 5)}

    by_region = collections.defaultdict(set)
    for s, v in rows:
        by_region[s.get("region") or s.get("province")].add(v)
    per = sorted(len(x) for x in by_region.values())
    med_per = per[len(per) // 2] if per else 0
    if med_per == 1 and len(by_region) > 1:
        return {"verdict": "REGION_CONST", "n": n, "distinct": distinct,
                "regions": len(by_region)}
    return {"verdict": "UNESTABLISHED", "n": n, "distinct": distinct,
            "unique_ratio": round(distinct / n, 4),
            "best_r": round(best[0], 4), "best_seed": best[1]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    out = {}
    if args.out and args.resume and pathlib.Path(args.out).exists():
        out = json.loads(pathlib.Path(args.out).read_text())
        print(f"  resuming: {len(out)} countries already swept")

    rng = random.Random(20260830)
    for slug in sorted(slugs):
        if slug in out:
            continue
        try:
            subs = load_substations(slug)
        except Exception as ex:
            out[slug] = {"_error": str(ex)}
            print(f"  {slug:<14}UNREADABLE: {ex}")
            continue
        n_all = len(subs)
        if n_all > SAMPLE:
            subs = rng.sample(subs, SAMPLE)
        res = {"_n_total": n_all, "_n_sampled": len(subs), "fields": {}}
        for p in sorted(numeric_paths(subs)):
            res["fields"][p] = classify(slug, subs, p)
        out[slug] = res
        c = collections.Counter(v["verdict"] for v in res["fields"].values())
        print(f"  {slug:<14}{n_all:>8,} recs · {len(res['fields']):>3} fields · "
              + " · ".join(f"{k} {v}" for k, v in c.most_common()))
        if args.out:
            pathlib.Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
        if args.verbose:
            for p, v in sorted(res["fields"].items()):
                if v["verdict"] == "FABRICATED":
                    print(f"      FABRICATED  {p:<34}{v['mechanism']} r={v['r']}")
    if args.out:
        print(f"\n  written {args.out}  ({len(out)} countries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
