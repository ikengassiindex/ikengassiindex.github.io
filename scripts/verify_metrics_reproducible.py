#!/usr/bin/env python3
"""
Can every published metric be recomputed from what its record publishes?

    python3 scripts/verify_metrics_reproducible.py
    python3 scripts/verify_metrics_reproducible.py --gate

THE PRINCIPLE

    A metric is published alongside a raw counterpart so that a reader can
    verify it WITHOUT trusting the producer. If the published metric cannot be
    recomputed from the published inputs, that promise is broken, and it breaks
    in the worst way: the reader's correct arithmetic disagrees with us, and
    looks like their mistake.

TWO TIERS, AND THE ESTATE SAYS SO NOWHERE

    GLOBAL ANCHOR — I1, I2. metric = TOP x min(1, raw / ANCHOR), with ANCHOR
    frozen and recorded in doctrine. One record plus the decision document is
    enough to verify. This script checks those exactly.

    COUNTRY-RELATIVE — I4, I5, I6. Method B against that country's own fleet
    P5/P95, and those two numbers are published NOWHERE as values: they appear
    only inside the provenance sentence, as words. A reader can recover them by
    re-deriving percentiles from all of that country's published raws, but not
    from the record in hand, and percentiles recomputed from ROUNDED raws will
    not exactly equal the originals.

    So this script checks tier one exactly and reports tier two as UNVERIFIABLE
    FROM THE RECORD rather than passing it. A check that cannot see the thing
    it is meant to examine must not report green - that lesson cost this estate
    four separate incidents in one week.

WHAT --gate DOES
    Exits 1 if any tier-one metric fails, or if any file declared in a
    manifest is absent from the checkout. It does NOT yet fail on tier two:
    that becomes a failure once the manifest anchors are published, which is
    the point of doing them.
"""
from __future__ import annotations
import argparse, collections, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# metric -> (raw field, where it lives, anchor, top, dp)
GLOBAL = {
    "I1": ("_I1_raw", "record",  0.9029,  0.30, 5),
    "I2": ("_I2_raw", "metrics", 45.3363, 0.30, 5),
}
# metric -> raw field. Normaliser is per country and unpublished.
COUNTRY_RELATIVE = {
    "I3": "_I3_raw_degC_days",
    "I4": "_I4_raw_km",
    "I5": "_I5_raw_F_AA",
    "I6": "_I6_raw_count",
}


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    a = ap.parse_args()

    ok = collections.Counter(); bad = collections.Counter()
    orphan = collections.Counter(); example = {}
    # Counted per (country, raw) pair, NOT per raw value. Keying globally
    # merged a raw that is ambiguous in two countries into one count and
    # reported 1,157 where the per-country measurement said 1,181. Two
    # instruments disagreeing about one quantity is the defect, not the gap.
    amb = collections.Counter()
    ncr = collections.Counter()
    unchecked = []

    for slug in slugs():
        man_p = ROOT / slug / "ssi-data.json"
        if not man_p.exists():
            continue
        man = json.loads(man_p.read_text())
        subs = man.get("substations") or []
        if not subs:
            for e in (man.get("substations_shards") or []):
                q = ROOT / slug / pathlib.Path(e["path"]).name
                if not q.exists():
                    unchecked.append(f"{slug}/{q.name}")
                    continue
                raw = json.loads(q.read_text())
                subs.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
        local = {k: collections.defaultdict(set) for k in COUNTRY_RELATIVE}
        for s in subs:
            m = s.get("metrics") or {}
            for k, (rf, where, anchor, top, dp) in GLOBAL.items():
                src = s if where == "record" else m
                has_m, has_r = k in m, isinstance(src.get(rf), (int, float))
                if has_m != has_r:
                    orphan[k] += 1
                    continue
                if not has_m:
                    continue
                want = round(top * min(1.0, max(0.0, src[rf]) / anchor), dp)
                if abs(m[k] - want) > 1e-9:
                    bad[k] += 1
                    example.setdefault(k, (slug, m[k], want, src[rf]))
                else:
                    ok[k] += 1
            for k, rf in COUNTRY_RELATIVE.items():
                if k in m and isinstance(m.get(rf), (int, float)):
                    ncr[k] += 1
                    local[k][m[rf]].add(m[k])
        for k in COUNTRY_RELATIVE:
            amb[k] += sum(1 for mv in local[k].values() if len(mv) > 1)
        del subs

    print(f"\n  TIER ONE — global anchor, verifiable from one record\n")
    print(f"  {'metric':<8}{'checked':>11}{'reproducible':>14}{'NOT':>8}"
          f"{'orphaned':>10}")
    fail = False
    for k in GLOBAL:
        n = ok[k] + bad[k]
        if not n:
            print(f"  {k:<8}{'—':>11}   not present")
            continue
        if bad[k] or orphan[k]:
            fail = True
        print(f"  {k:<8}{n:>11,}{ok[k]:>14,}{bad[k]:>8,}{orphan[k]:>10,}")
        if k in example:
            s_, cur, want, r = example[k]
            print(f"           e.g. {s_}: published {cur}, from raw {r} -> {want}")

    print(f"\n  TIER TWO — country-relative normaliser, NOT published as values\n")
    for k, rf in COUNTRY_RELATIVE.items():
        if not ncr[k]:
            continue
        print(f"  {k:<8}{ncr[k]:>11,}   UNVERIFIABLE FROM THE RECORD "
              f"({amb[k]:,} country/raw pair(s) map to more than one metric)")
    print(f"\n  Tier two is not a pass and not a failure: the P5/P95 these use")
    print(f"  are published nowhere as numbers, so this script cannot check")
    print(f"  them. Publishing them in each manifest is what turns this into a")
    print(f"  real check.")

    if unchecked:
        fail = True
        print(f"\n  NOT CHECKED — {len(unchecked)} declared shard(s) absent from "
              f"this checkout:")
        for u in unchecked[:6]:
            print(f"    {u}")

    print()
    if a.gate and fail:
        print(f"  GATE FAILED")
        return 1
    print(f"  tier one reproduces from the published record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
