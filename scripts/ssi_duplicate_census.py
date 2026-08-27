#!/usr/bin/env python3
"""
SSI substation duplicate census — READ ONLY. Modifies nothing.

Run from the repo root of ikengassiindex.github.io:

    python3 ssi_duplicate_census.py                    # cohort census
    python3 ssi_duplicate_census.py germany us         # named countries
    python3 ssi_duplicate_census.py --json out.json    # machine-readable groups

WHY A CENSUS BEFORE A DEDUPE
-----------------------------
99,790 substations (13.9% of the cohort) share an exact coordinate with at
least one other. That is not the same as 99,790 duplicates: a site with two
voltage levels can legitimately be modelled as two records at one point. The
count is only actionable once split by how certain we are, so this classifies
rather than totals, and deletes nothing.

THE DISCRIMINATING RULE
-----------------------
Records are grouped by rounded coordinate (6 dp ~ 0.1 m) and each group is
placed in exactly one class, most certain first:

  A  DUPLICATE ID      the same substation_id appears more than once.
                       Unambiguous: one record, stored twice.

  B  SAME OSM FEATURE  distinct substation_ids sharing one osm_feature_id.
                       Unambiguous: one upstream feature ingested twice.

  C  IDENTICAL FACILITY  distinct ids, same coordinate, and identical on
                       voltage_kv, operator, region and province — every
                       attribute that describes the physical asset. Nothing
                       distinguishes these records except identity fields the
                       pipeline generated. Treated as duplicates.

  D  COLOCATED, DIVERGENT  same coordinate but differing on at least one of
                       voltage_kv / operator. Split on measurement:

     D1  only one REAL voltage in the group, the rest 0.0 or None. The
         records do not actually disagree — one simply has no voltage. A
         duplicate wearing an unknown. 13 groups cohort-wide.

     D2  two or more genuinely different voltages at one point. France
         pairing 20 kV with 400 kV is a transmission/distribution
         co-location and is real infrastructure, not a duplicate.
         207 groups, 175 of them in the US. NEVER auto-resolved.

WHICH RECORD SURVIVES
---------------------
For A, B and C the census nominates a keeper by, in order:
  1. has a real name (not the generated "Substation <id>" form)
  2. most populated fields
  3. has osm_feature_id
  4. lowest substation_id, for determinism

It only NOMINATES. Nothing is written.

TRANSMISSION LINES  (--lines)
----------------------------
grid-geo.json does NOT reference substations from its line records: `l` holds
polyline geometry only. Connectivity lives in `a`, a map of substation_id ->
[line indices]. So removing a substation orphans nothing directly — but it
drops that substation's edges unless they are MERGED onto the keeper first.
That is the additive counterpart to Discipline #36's rule that lines to
filtered-out substations are kept.

Measured cohort-wide: of 77,785 duplicate groups, 35,529 carry adjacency, but
only ~7 have real adjacency on more than one member — 29 line-links in total
sit on a record the keeper rule would discard. Deduplication is safe provided
those are merged.

--lines also counts byte-identical line geometries: 298,660 of 2,668,490
(11.2%) cohort-wide, concentrated in germany (28.1%), italy (20.8%) and
us (20.0%). Same repeated-ingestion origin as the substation duplicates.

INDEPENDENT CORROBORATION
-------------------------
grid-geo.json already holds the DEDUPLICATED fleet. Its substation count
matches this census's post-dedupe figure to the record on japan (6,168),
australia (12,059) and spain (12,438), and to within 11 on germany
(108,027 vs 108,016) and 2 on france. Two artefacts built by different code
paths agree on the true fleet size — which also means the map has been
drawing the real number while the page has been reporting the inflated one.

WHY THE SCORES DIVERGE INSIDE A GROUP
-------------------------------------
Duplicates receive distinct generated names ("Substation 11000028404"), and
R_median traces back to an MD5 of the name. So one physical site is scored
several times and lands in several bands. The census reports the R_median
spread per group because it quantifies what deduplication would correct.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path.cwd()
FACILITY_KEYS = ("voltage_kv", "operator", "region", "province")


def cohort_slugs() -> list[str]:
    cj = json.loads((REPO / "intelligence" / "countries.json").read_text())
    return sorted(c["slug"] for c in cj["countries"] if "slug" in c)


def load(slug: str) -> list[dict]:
    p = REPO / slug / "ssi-data.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text())
    if isinstance(d, list):
        return d
    if d.get("substations_shards"):
        subs = []
        for e in d["substations_shards"]:
            rel = e["path"] if isinstance(e, dict) else e
            sp = p.parent / Path(rel).name
            if not sp.exists():
                continue
            part = json.loads(sp.read_text())
            subs += part if isinstance(part, list) else (part.get("substations") or [])
        return subs
    return d.get("substations") or []


def generated_name(s: dict) -> bool:
    n = s.get("name")
    if not n or not isinstance(n, str) or not n.strip():
        return True
    return n.strip() == f"Substation {s.get('substation_id')}"


def keeper(group: list[dict]) -> dict:
    return sorted(
        group,
        key=lambda s: (
            generated_name(s),                     # real name first
            -sum(1 for v in s.values() if v not in (None, "", {}, [])),
            s.get("osm_feature_id") is None,
            str(s.get("substation_id")),
        ),
    )[0]


def classify(slug: str):
    subs = load(slug)
    by_coord = defaultdict(list)
    for s in subs:
        lat, lon = s.get("lat"), s.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            by_coord[(round(float(lat), 6), round(float(lon), 6))].append(s)

    out = {"slug": slug, "substations": len(subs),
           "A": [], "B": [], "C": [], "D1": [], "D2": []}

    for coord, group in by_coord.items():
        if len(group) < 2:
            continue

        ids = Counter(str(s.get("substation_id")) for s in group)
        osm = Counter(str(s.get("osm_feature_id")) for s in group
                      if s.get("osm_feature_id"))

        rs = [s.get("R_median") for s in group if isinstance(s.get("R_median"), (int, float))]
        bands = sorted({s.get("classification") for s in group})
        rec = {
            "coord": list(coord),
            "n": len(group),
            "ids": [str(s.get("substation_id")) for s in group][:8],
            "voltages": sorted({s.get("voltage_kv") for s in group}, key=str),
            "R_median_spread": round(max(rs) - min(rs), 4) if len(rs) > 1 else 0.0,
            "bands": [b for b in bands if b is not None],
            "keeper": str(keeper(group).get("substation_id")),
            "redundant": len(group) - 1,
        }

        if any(v > 1 for v in ids.values()):
            out["A"].append(rec)
        elif any(v > 1 for v in osm.values()):
            out["B"].append(rec)
        elif all(
            all(s.get(k) == group[0].get(k) for k in FACILITY_KEYS)
            for s in group
        ):
            out["C"].append(rec)
        else:
            # D1 vs D2 — does the group actually disagree on voltage, or does
            # one record simply not have one? A 0.0 / None voltage is an
            # unknown, not a distinguishing attribute.
            real_v = [v for v in rec["voltages"] if isinstance(v, (int, float)) and v > 0]
            out["D1" if len(real_v) <= 1 else "D2"].append(rec)

    return out


def load_grid_geo(slug: str):
    """Return (adjacency map, line records). Convention #80 shards resolved."""
    p = REPO / slug / "grid-geo.json"
    if not p.exists():
        return {}, []
    g = json.loads(p.read_text())
    lines = list(g.get("l") or [])
    for e in (g.get("l_shards") or []):
        rel = e["path"] if isinstance(e, dict) else e
        sp = p.parent / Path(rel).name
        if sp.exists():
            q = json.loads(sp.read_text())
            lines += q if isinstance(q, list) else (q.get("l") or q.get("lines") or [])
    return (g.get("a") or {}), lines


def reconcile(results):
    """Explain, id by id, every disagreement with grid-geo.

    grid-geo.json was built by a code path that did not carry the duplicates
    through, so its substation set is an independent check on this rule. A
    delta is only acceptable once each id in it is accounted for. Three
    categories, and only the third would mean the rule is wrong:

      keeper-choice   dropped here, kept there — the group's OTHER member
                      survives, so the site is still represented. Benign.
      preserved D2    kept here, absent there — grid-geo collapsed a genuine
                      multi-voltage co-location. Keeping it is correct.
      grid-geo gap    kept here, absent there, and not a duplicate of anything
                      — a real substation missing from the map layer.
    """
    print("\n" + "=" * 78)
    print("RECONCILIATION AGAINST grid-geo.json")
    print("=" * 78)
    print(f"{'country':<13}{'survivors':>10}{'grid-geo':>10}"
          f"{'keeper-chc':>12}{'D2 kept':>9}{'gg gap':>8}{'unexplained':>13}")
    for r in results:
        slug = r["slug"]
        gp = REPO / slug / "grid-geo.json"
        if not gp.exists():
            continue
        drop = set()
        for cls in ("A", "B", "C", "D1"):
            for g in r[cls]:
                drop |= {i for i in set(g["ids"]) if i != g["keeper"]}
        if not drop:
            continue
        subs = load(slug)
        all_ids = {str(s.get("substation_id")) for s in subs}
        seen, sids = set(), set()
        for s in subs:
            sid = str(s.get("substation_id"))
            if sid in drop or sid in seen:
                continue
            seen.add(sid); sids.add(sid)
        gg = set(json.loads(gp.read_text()).get("s") or {})
        d2ids = {i for g in r["D2"] for i in g["ids"]}
        only_gg, only_me = gg - sids, sids - gg
        keeper_choice = len(only_gg & drop)
        missing_upstream = len(only_gg - all_ids)
        d2_kept = len(only_me & d2ids)
        gg_gap = len(only_me - d2ids)
        unexplained = missing_upstream
        print(f"{slug:<13}{len(sids):>10,}{len(gg):>10,}"
              f"{keeper_choice:>12,}{d2_kept:>9,}{gg_gap:>8,}{unexplained:>13,}")
    print("\n  keeper-chc  both artefacts kept a different member of the same group — benign")
    print("  D2 kept     genuine multi-voltage co-location this rule preserves — correct")
    print("  gg gap      real substation present in ssi-data but absent from the map layer")
    print("  unexplained would mean the rule is wrong. Must be zero before --apply.")


def line_census(results):
    """Duplicate line geometries, and adjacency a dedupe would drop."""
    import hashlib

    print("\n" + "=" * 78)
    print("TRANSMISSION LINES")
    print("=" * 78)
    print(f"{'country':<13}{'lines':>10}{'dup geom':>10}{'%':>7}"
          f"{'grp w/ adj':>12}{'edges at risk':>14}")
    tl = td = te = tm = 0
    rows = []
    for r in results:
        adj, lines = load_grid_geo(r["slug"])
        if not adj and not lines:
            continue
        seen, dup = set(), 0
        for ln in lines:
            pts = ln.get("p") if isinstance(ln, dict) else None
            if not pts:
                continue
            h = hashlib.md5(json.dumps(pts, separators=(",", ":")).encode()).hexdigest()
            if h in seen:
                dup += 1
            else:
                seen.add(h)

        n_adj = edges = 0
        for cls in ("A", "B", "C", "D1"):
            for g in r[cls]:
                present = [i for i in g["ids"] if i in adj]
                if present:
                    n_adj += 1
                # class A repeats one id, so `a` holds a single entry and
                # nothing is at risk; only DISTINCT ids can strand edges.
                distinct = [i for i in set(present) if i != g["keeper"]]
                edges += sum(len(adj[i]) for i in distinct)

        tl += len(lines); td += dup; te += edges; tm += n_adj
        rows.append((r["slug"], len(lines), dup, n_adj, edges))

    for slug, n, dup, n_adj, edges in sorted(rows, key=lambda x: -x[2])[:14]:
        pct = f"{dup / n * 100:.1f}%" if n else "-"
        print(f"{slug:<13}{n:>10,}{dup:>10,}{pct:>7}{n_adj:>12,}{edges:>14,}")
    print("-" * 78)
    print(f"{'COHORT':<13}{tl:>10,}{td:>10,}"
          f"{(td / tl * 100 if tl else 0):>6.1f}%{tm:>12,}{te:>14,}")
    print(f"\n  {td:,} line records duplicate another's geometry exactly.")
    print(f"  {te:,} line-links sit on a record the keeper rule would discard —")
    print(f"  these must be merged onto the keeper, not dropped.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*", help="slugs (default: whole cohort)")
    ap.add_argument("--json", metavar="PATH", help="write the classified groups")
    ap.add_argument("--reconcile", action="store_true",
                    help="reconcile the survivor set against grid-geo, id by id")
    ap.add_argument("--lines", action="store_true",
                    help="also census grid-geo.json: duplicate geometries + adjacency at risk")
    args = ap.parse_args()

    if not (REPO / "intelligence" / "countries.json").exists():
        sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

    slugs = args.countries or cohort_slugs()
    results, tot = [], Counter()

    print(f"{'country':<14}{'subs':>9}{'A id':>7}{'B osm':>7}{'C ident':>9}"
          f"{'D1 unk':>8}{'D2 real':>9}{'redundant':>11}{'% fleet':>9}")
    print("-" * 84)

    for slug in slugs:
        r = classify(slug)
        if not r["substations"]:
            continue
        results.append(r)
        red = sum(g["redundant"] for cls in ("A", "B", "C", "D1") for g in r[cls])
        counts = {c: len(r[c]) for c in ("A", "B", "C", "D1", "D2")}
        for k, v in counts.items():
            tot[k] += v
        tot["subs"] += r["substations"]
        tot["redundant"] += red
        if any(counts.values()):
            print(f"{slug:<14}{r['substations']:>9,}{counts['A']:>7,}{counts['B']:>7,}"
                  f"{counts['C']:>9,}{counts['D1']:>8,}{counts['D2']:>9,}{red:>11,}"
                  f"{red / r['substations'] * 100:>8.1f}%")

    print("-" * 84)
    print(f"{'COHORT':<14}{tot['subs']:>9,}{tot['A']:>7,}{tot['B']:>7,}"
          f"{tot['C']:>9,}{tot['D1']:>8,}{tot['D2']:>9,}{tot['redundant']:>11,}"
          f"{tot['redundant'] / tot['subs'] * 100:>8.1f}%")

    print(f"\n  A + B + C + D1 are duplicates: {tot['redundant']:,} redundant records "
          f"({tot['redundant'] / tot['subs'] * 100:.1f}% of the cohort)")
    print(f"  post-dedupe cohort would be {tot['subs'] - tot['redundant']:,} substations")
    print(f"  D2 stays: {tot['D2']:,} coordinates carry genuinely different voltages "
          f"(transmission/distribution co-location)")

    spreads = [g["R_median_spread"] for r in results for c in ("A", "B", "C", "D1")
               for g in r[c] if g["R_median_spread"] > 0]
    if spreads:
        spreads.sort()
        multi = sum(1 for r in results for c in ("A", "B", "C", "D1")
                    for g in r[c] if len(g["bands"]) > 1)
        print(f"\n  score divergence inside duplicate groups:")
        print(f"    median R_median spread {spreads[len(spreads) // 2]:.4f}, "
              f"max {spreads[-1]:.4f}")
        print(f"    {multi:,} groups span more than one classification band")

    if args.reconcile:
        reconcile(results)

    if args.lines:
        line_census(results)

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1))
        print(f"\n  groups written to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
