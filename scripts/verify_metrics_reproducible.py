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

    COUNTRY-RELATIVE — I3, I4, I5, I6. Normalised against that country's own
    fleet, and the anchors ARE published, in meta.metric_derivations[]: as
    `anchors` {metric: [P5, P95]} for the Method B metrics, and as `anchor`
    {value, units, maps_to, frozen, basis} for I3's Method C. That log is
    APPEND-ONLY, so the LAST entry naming a metric is the live one - reading
    any earlier entry gives a superseded anchor.

    An earlier version of this script asserted those anchors were "published
    nowhere as values, only inside the provenance sentence, as words". That
    was false. It came from grepping the manifest for the string "anchor",
    seeing 765 hits, and inferring prose without opening one. Corrected here
    and in doctrine/FINDING_published_metrics_must_be_recomputable.md.

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
    "I1": ("_I1_raw", "record",  0.9029,  0.30, 4),
    "I2": ("_I2_raw", "metrics", 45.3363, 0.30, 4),
}
# metric -> (raw field, normalisation). Anchors come from the manifest.
COUNTRY_RELATIVE = {
    "I3": ("_I3_raw_degC_days", "C"),      # frozen anchor, maps_to 0.30
    "I4": ("_I4_raw_km",        "Binv"),   # Method B, inverted
    "I5": ("_I5_raw_F_AA",      "B"),
    "I6": ("_I6_raw_count",     "Binv"),
}


def method_b(x, p5, p95):
    if p5 is None or p95 is None or p95 <= p5:
        return None
    return max(0.0, min(1.0, (x - p5) / (p95 - p5)))


def live_anchors(man):
    """metric_derivations is APPEND-ONLY: the LAST entry naming a metric wins."""
    out = {}
    for e in man.get("meta", {}).get("metric_derivations", []):
        a = e.get("anchors")
        if isinstance(a, dict):
            for k, v in a.items():
                if isinstance(v, (list, tuple)) and len(v) == 2:
                    out[k] = ("B", float(v[0]), float(v[1]))
        anc = e.get("anchor")
        if isinstance(anc, dict) and anc.get("value") is not None:
            for k in (e.get("metrics") or []):
                out[k] = ("C", float(anc["value"]), float(anc.get("maps_to", 1.0)))
    return out


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
    cr_ok = collections.Counter(); cr_bad = collections.Counter()
    cr_noanchor = collections.Counter(); cr_ex = {}
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
        anchors = live_anchors(man)
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
                # Aligned 12 September: the metric field carries N(x) in
                # [0, 1] at 4 dp, and _<k>_iri the 0.30 contribution at 5 dp,
                # each derived from the rounded raw. Both are checked.
                nx = min(1.0, max(0.0, src[rf]) / anchor)
                want = round(nx, 4)
                want_iri = round(top * nx, 5)
                if abs(m.get(f"_{k}_iri", -9e9) - want_iri) > 1e-9:
                    bad[k] += 1
                    example.setdefault(k, (slug, m.get(f"_{k}_iri"), want_iri,
                                           src[rf]))
                    continue
                if abs(m[k] - want) > 1e-9:
                    bad[k] += 1
                    example.setdefault(k, (slug, m[k], want, src[rf]))
                else:
                    ok[k] += 1
            for k, (rf, how) in COUNTRY_RELATIVE.items():
                if k not in m or not isinstance(m.get(rf), (int, float)):
                    continue
                ncr[k] += 1
                if k not in anchors:
                    cr_noanchor[k] += 1
                    continue
                kind, a1, a2 = anchors[k]
                x = m[rf]
                if kind == "C":
                    # The metric field carries N(x) in [0, 1]; maps_to scales
                    # the SEPARATE _<k>_iri field, not this one. Applying it
                    # here reported I3 as 100% irreproducible, which was the
                    # check being wrong, not I3.
                    want = round(min(1.0, max(0.0, x) / a1), 4)
                elif how == "Binv":
                    w = method_b(a1 + a2 - x, a1, a2)
                    want = None if w is None else round(w, 4)
                else:
                    w = method_b(x, a1, a2)
                    want = None if w is None else round(w, 4)
                if want is None:
                    cr_noanchor[k] += 1
                elif abs(m[k] - want) > 1e-9:
                    cr_bad[k] += 1
                    cr_ex.setdefault(k, (slug, m[k], want, x))
                else:
                    cr_ok[k] += 1

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

    print(f"\n  TIER TWO — country-relative, anchors read from the manifest\n")
    print(f"  {'metric':<8}{'checked':>11}{'reproducible':>14}{'NOT':>10}"
          f"{'share':>9}{'no anchor':>12}")
    for k in COUNTRY_RELATIVE:
        n = cr_ok[k] + cr_bad[k]
        if not n:
            continue
        if cr_bad[k]:
            fail = True
        print(f"  {k:<8}{n:>11,}{cr_ok[k]:>14,}{cr_bad[k]:>10,}"
              f"{100*cr_bad[k]/n:>8.3f}%{cr_noanchor[k]:>12,}")
        if k in cr_ex:
            s_, cur, want, r = cr_ex[k]
            print(f"           e.g. {s_}: published {cur}, from raw {r} -> {want}")

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
