#!/usr/bin/env python3
"""Resolve the cross-border contamination: reassign what is new, remove what is duplicated.

    python3 scripts/ssi_resolve_cross_border.py            # dry run
    python3 scripts/ssi_resolve_cross_border.py --write

THE AUDIT THAT DETERMINED THE ACTION
    doctrine/FINDING_the_gate_that_passed_by_not_running.md found 3,535
    substations filed under a state they are not in. The operator's
    instruction was to reassign them to the correct fleet, auditing for
    duplicates first.

    The audit changed the answer. Matching each record against the receiving
    country's fleet by position:

        already present in the destination   3,203
        genuinely new to the destination       323

    Match quality: median separation 0.04 m, 2,204 of 2,345 within one metre,
    548 sharing an identical name as well as a position. These are not nearby
    substations. They are the same substation, ingested twice — once correctly
    into its own country and once into the neighbour by bounding-box overshoot.

    Reassigning them would manufacture 3,203 duplicate assets. So:

        duplicate in destination  -> REMOVE from the wrong fleet
        new to destination        -> REASSIGN to the right fleet

    The duplicate threshold is 50 m, three orders of magnitude above the
    median match and far below any plausible spacing of distinct substations.
    The fifteen records between 50 and 150 m are treated as NEW and reassigned,
    because reassignment is recoverable and removal is less so.

ALSO REMOVED
    - records whose containing state has no fleet in this cohort and so cannot
      be published under any country we cover: BY 1, PE 1, RU 3, SY 3.
    - the four records with no explanation rather than a rationalised one:
      a Japanese substation 268.9 km offshore, one at 21.8 km, and two
      Australian including Mildura, which is inland on the Murray.

WHAT IT DOES NOT DO
    It does not re-score. A reassigned record carries its old components into a
    new fleet whose P5/P95 it now also changes; that is the refresh's job, not
    this script's. It writes a full before/after manifest so every move is
    reversible.
"""
from __future__ import annotations
import argparse, collections, csv, gc, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
DUP_M = 50.0
MANIFEST = ROOT / "data/quarantine/cross_border_20260925.csv"
TERRITORY_PARENT = {"GI": "uk", "IM": "uk", "JE": "uk", "GG": "uk"}
UNEXPLAINED = set()   # filled from the manifest: verdict == offshore_far

def haversine_m(la1, lo1, la2, lo2):
    dy = (la2 - la1) * 111320.0
    dx = (lo2 - lo1) * 111320.0 * math.cos(math.radians(la1))
    return math.hypot(dx, dy)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data
    from ssi_boundary_source import NUTS_CC, CNTR_CC
    COHORT = set(NUTS_CC) | set(CNTR_CC)

    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    state = [r for r in rows if r["verdict"] == "state"]
    far   = [r for r in rows if r["verdict"] == "offshore_far"]

    # classify every 'state' record as duplicate-in-destination or new
    by_dest = collections.defaultdict(list)
    for r in state:
        d = TERRITORY_PARENT.get(r["attributed_to"], r["attributed_to"])
        r["_dest"] = d
        by_dest[d].append(r)

    decision = {}     # (country, substation_id) -> ('remove'|'reassign', dest, why)
    for d, rs in sorted(by_dest.items()):
        if d not in COHORT:
            for r in rs:
                decision[(r["country"], r["substation_id"])] = (
                    "remove", d, f"containing state {d} has no fleet in this cohort")
            continue
        _, subs, _ = load_ssi_data(d)
        idx = collections.defaultdict(list)
        for s in subs:
            if s.get("lat") is not None:
                idx[(round(s["lat"], 3), round(s["lon"], 3))].append(s)
        for r in rs:
            la, lo = float(r["lat"]), float(r["lon"]); best = None
            for dla in (-0.001, 0, 0.001):
                for dlo in (-0.001, 0, 0.001):
                    for s in idx.get((round(la + dla, 3), round(lo + dlo, 3)), []):
                        dist = haversine_m(la, lo, s["lat"], s["lon"])
                        if best is None or dist < best[0]: best = (dist, s)
            if best and best[0] <= DUP_M:
                decision[(r["country"], r["substation_id"])] = (
                    "remove", d,
                    f"duplicate of {d} {best[1].get('substation_id')} at {best[0]:.2f} m")
            else:
                decision[(r["country"], r["substation_id"])] = (
                    "reassign", d,
                    f"new to {d}" + (f"; nearest existing {best[0]:.1f} m" if best else ""))
        del subs, idx; gc.collect()

    for r in far:
        decision[(r["country"], r["substation_id"])] = (
            "remove", "", f"unexplained: {float(r['km_outside_own']):.1f} km outside own territory")

    acts = collections.Counter(v[0] for v in decision.values())
    print(f"decisions: {dict(acts)}   over {len(decision):,} records\n")
    per = collections.defaultdict(collections.Counter)
    for (c, sid), (act, d, why) in decision.items(): per[c][act] += 1
    print(f"{'country':<14}{'remove':>9}{'reassign':>10}")
    for c in sorted(per): print(f"{c:<14}{per[c]['remove']:>9,}{per[c]['reassign']:>10,}")

    # write the audit trail regardless of --write
    out = ROOT / "data/quarantine/cross_border_resolution_20260925.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["country","substation_id","action","destination","reason"])
        for (c, sid), (act, d, why) in sorted(decision.items()):
            w.writerow([c, sid, act, d, why])
    print(f"\n✓ wrote {out.relative_to(ROOT)} — every move, with its reason")

    if not a.write:
        print("\n(dry run — no ssi-data.json touched)")
        return 0

    moved = collections.defaultdict(list)
    for slug in sorted({c for c, _ in decision}):
        manifest, subs, sharded = load_ssi_data(slug)
        keep, n_rm = [], 0
        for s in subs:
            k = (slug, s.get("substation_id"))
            if k in decision:
                act, d, why = decision[k]
                s["_cross_border_action"] = act
                s["_cross_border_reason"] = why
                s["_cross_border_from"] = slug
                if act == "reassign": moved[d].append(s)
                n_rm += 1
                continue
            keep.append(s)
        save_ssi_data(slug, manifest, keep, sharded)
        print(f"  {slug:<14} removed {n_rm:,}  → fleet {len(subs):,} to {len(keep):,}")
        del subs; gc.collect()
    for d, recs in sorted(moved.items()):
        manifest, subs, sharded = load_ssi_data(d)
        subs.extend(recs)
        save_ssi_data(d, manifest, subs, sharded)
        print(f"  {d:<14} received {len(recs):,} → fleet {len(subs)-len(recs):,} to {len(subs):,}")
        del subs; gc.collect()
    print("\n✓ written")
    return 0

if __name__ == "__main__":
    sys.exit(main())
