#!/usr/bin/env python3
"""Discipline #36 v2 — cross-border enforcement that asks the right question.

    python3 scripts/check_cross_border_v2.py --all --strict

WHAT THE FIRST VERSION GOT WRONG, ALL OF IT MEASURED ON 25 SEPTEMBER 2026

  1. NO RUNNER.        check_cross_border.py is absent from scripts/preflight.sh.
                       The gate existed and nothing ever called it.

  2. FAILS OPEN.       shapely missing -> ImportError -> every country SKIPPED
                       -> skipped counted as not-violating -> "violating: 0"
                       -> exit 0. A green light manufactured by a missing
                       dependency, across all 39 countries.

  3. MEMBERSHIP, NOT   It asked "is this point inside my own polygon?" and never
     EXCLUSIVITY.      "is it inside somebody else's?". A substation inside both
                       Italy's generous bounds and Slovenia's actual territory
                       passed.

  4. TOLERANCE WIDE    italy's configured tolerance is 5.0 km. 345 of its 346
     ENOUGH TO HOLD    outliers sat within 5 km. The tolerance was sized for
     A FOREIGN         coastline imprecision and is wide enough to contain
     PROVINCE.         Goriška, Savoie, Klagenfurt-Villach and Ticino.

  5. EVIDENCE          is_inside_country returns (True, dist) for tolerated
     DISCARDED.        points and the caller only records max_dist for points it
                       calls outside. Every country printed "Max km 0.0" while
                       346 Italian records sat 0-5.002 km beyond the border.

  6. UNVERIFIED        {country}/bounds.json has no recorded provenance and is
     GEOMETRY.         wrong in both directions: slovenia +33.9% too large,
                       netherlands +11.2%, ireland +4.2%; norway, denmark,
                       portugal and france under-inclusive, between them
                       inventing 4,183 false positives.

WHAT THIS VERSION DOES

  Authoritative geometry only, via scripts/ssi_boundary_source.py — GISCO NUTS
  2024 for the 26 NUTS countries, GISCO CNTR 2024 for the rest and for every
  neighbour on earth. bounds.json is never used.

  Two independent assertions per country:
      A. CONTAINMENT  how many records fall outside their own polygon, and how
                      far — reported for every outlier, tolerated or not.
      B. EXCLUSIVITY  how many fall inside ANOTHER STATE. This is the assertion
                      that matters and the one the old gate could not make.

  Exclusivity has no tolerance. A substation is either inside another country
  or it is not; no distance makes that acceptable.

  Declared policy, never silent:
      TERRITORY   a state's own dependent territories count as that state.
      INTEGRATED  microstates and enclaves whose distribution grid is
                  integrated with the surrounding country stay with it.
                  Operator decision, 25 September 2026.
      CONTESTED   boundaries that are themselves disputed are flagged and
                  never adjudicated here.

  FAILS CLOSED. Any country that cannot be evaluated is a failure, not a skip.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))

TERRITORY = {'PR':'us','GU':'us','VI':'us','AS':'us','MP':'us','UM':'us','FO':'denmark',
 'AX':'finland','SJ':'norway','GI':'uk','IM':'uk','JE':'uk','GG':'uk','NC':'france','PF':'france',
 'RE':'france','GP':'france','MQ':'france','GF':'france','YT':'france','PM':'france','WF':'france',
 'BL':'france','MF':'france','AW':'netherlands','CW':'netherlands','SX':'netherlands',
 'BQ':'netherlands','CK':'new-zealand','NU':'new-zealand','TK':'new-zealand','NF':'australia',
 'CX':'australia','CC':'australia','HM':'australia'}
INTEGRATED = {('italy','SM'),('italy','VA'),('france','AD'),('france','MC'),('spain','AD'),
              ('spain','MA'),('switzerland','LI'),('austria','LI')}
CONTESTED  = {('israel','SY'),('israel','PS'),('israel','XJL'),('israel','XAD')}

def run(slugs, threshold_foreign, json_out=None):
    import numpy as np, shapely
    from ssi_boundary_source import load, NUTS_CC, CNTR_CC
    from scripts._ssi_data_shard_reader import load_ssi_data
    polys, prov, unresolved = load()
    COH = {**{v: k for k, v in NUTS_CC.items()}, **{v: k for k, v in CNTR_CC.items()}}

    failures, rows = [], []
    for slug, why in unresolved:
        failures.append(f"{slug}: no authoritative polygon ({why})")

    print(f"\n{'Country':<15}{'Fleet':>9}{'Outside':>9}{'MaxKm':>9}{'FOREIGN':>9}  {'Verdict':<10} where")
    print("-" * 104)
    for slug in slugs:
        if slug not in polys:
            failures.append(f"{slug}: no polygon"); continue
        try:
            _, subs, _ = load_ssi_data(slug)
        except Exception as e:
            failures.append(f"{slug}: fleet unreadable ({type(e).__name__}: {e})"); continue
        S = [s for s in subs if s.get("lat") is not None and s.get("lon") is not None]
        if len(S) != len(subs):
            failures.append(f"{slug}: {len(subs)-len(S)} records without coordinates")
        P = np.array([[s["lon"], s["lat"]] for s in S])
        pts = shapely.points(P[:, 0], P[:, 1])
        out_mask = ~shapely.contains(polys[slug], pts)
        idx = np.where(out_mask)[0]
        maxkm = 0.0; foreign = 0; tally = collections.Counter()
        if len(idx):
            op = pts[idx]
            # distance measured to own polygon UNION its own dependent territories,
            # or a Puerto Rican substation reads as 1,800 km from the United States.
            own = polys[slug]
            terr = [polys['_'+c] for c, o in TERRITORY.items() if o == slug and '_'+c in polys]
            if terr:
                from shapely.ops import unary_union
                own = unary_union([own] + terr)
            maxkm = float(max(p.distance(own) for p in op) * 111.32)
            fmask = np.zeros(len(idx), bool)
            # One mask per DESTINATION state, not per polygon. A country appears
            # twice in `polys` — once as a cohort member and once as a neighbour —
            # and summing both counts every record twice. It did.
            per_dest = collections.defaultdict(lambda: np.zeros(len(idx), bool))
            for oc, g in polys.items():
                if oc == slug: continue
                raw = oc.lstrip('_')
                if (slug, raw) in INTEGRATED or (slug, raw) in CONTESTED: continue
                if TERRITORY.get(raw) == slug or COH.get(raw) == slug: continue
                h = shapely.contains(g, op)
                if h.any():
                    fmask |= h
                    per_dest[COH.get(raw, raw)] |= h
            for dest, m in per_dest.items():
                tally[dest] = int(m.sum())
            foreign = int(fmask.sum())
            for j in np.where(fmask)[0]:
                s = S[idx[j]]
                rows.append({"country": slug, "substation_id": s.get("substation_id"),
                             "lat": s["lat"], "lon": s["lon"]})
        verdict = "FAIL" if foreign > threshold_foreign else "ok"
        if foreign > threshold_foreign:
            failures.append(f"{slug}: {foreign} substations inside another state")
        print(f"{slug:<15}{len(subs):>9,}{len(idx):>9,}{maxkm:>9.2f}{foreign:>9,}  {verdict:<10}"
              f"{', '.join(f'{k} {v}' for k, v in tally.most_common(3))}")

    print(f"\n=== SUMMARY ===")
    print(f"  countries evaluated : {len(slugs)}")
    print(f"  substations inside another state : {len(rows):,}")
    print(f"  failures : {len(failures)}")
    for f in failures[:20]:
        print(f"     ✗ {f}")
    if len(failures) > 20:
        print(f"     … and {len(failures)-20} more")
    if json_out:
        json.dump({"failures": failures, "foreign": rows}, open(json_out, "w"), indent=1)
    return failures

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country", nargs="?"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--threshold-foreign", type=int, default=0,
                    help="substations inside another state tolerated per country. Default 0. "
                         "There is no distance at which being in another country is acceptable.")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any failure")
    ap.add_argument("--json")
    a = ap.parse_args()
    from ssi_boundary_source import NUTS_CC, CNTR_CC
    cohort = sorted(list(NUTS_CC) + list(CNTR_CC))
    slugs = cohort if a.all else ([a.country] if a.country else cohort)
    failures = run(slugs, a.threshold_foreign, a.json)
    if failures and a.strict:
        print("\n✗ GATE FAILED — see failures above"); return 1
    if failures:
        print("\n⚠ failures present; run with --strict to make them block")
    else:
        print("\n✓ no substation in this cohort lies inside another state")
    return 0

if __name__ == "__main__":
    sys.exit(main())
