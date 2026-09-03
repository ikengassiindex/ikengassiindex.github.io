#!/usr/bin/env python3
"""
Derive components.T from the transition block, per the v4.2 construct.

    python3 scripts/ssi_derive_component_T.py --all --dry-run
    python3 scripts/ssi_derive_component_T.py --all
    python3 scripts/ssi_derive_component_T.py france --verbose

THE FORMULA, AS PUBLISHED
-------------------------
SSI_v4_2_Complete_Formula_Construct_Italy_v3.html, canonical anchor 22 July
2026, sections 02 / 03 / 04:

    T  = T1                                    intra-weight 1.00
    T1 = 0.50·N(DER_ratio) + 0.30·N(DER_variability) + 0.20·N(EV_load_ratio)
    N  = Method B: soft_clip( (x - P5) / (P95 - P5) ) over THAT COUNTRY'S
         fleet percentiles, not the cohort's
    global weight of T in R_base = 0.05

All three sub-metrics are already on the record, in `transition`, on 87.4% of
the cohort. Nothing is fetched; nothing is invented.

WHY THIS COMPONENT AND NOT ANOTHER
----------------------------------
components.C/V/I/E/S/T are a hash of the substation's NAME on 456,200 records
(gated in fe74eeb5) -- round(vary(0.35, name + '_' + K, 0.30), 4). T is the one
component whose inputs are present AND whose formula is a single published
metric, so it is the smallest step that is genuinely real.

V looked easier and is not: the construct's V is
N(V1_total x (1 + 0.50 x V2_severe_ratio)) from DSO power-quality records, which
are on no substation. socio_economic.V_socio is an input to the R3 consequence
MODIFIER (section 01: C_mult = consequence_sigmoid(pop, load, V_socio)), not to
the V component. C -- Continuity, the largest at 0.30 -- needs DSO outage
records that exist for no country in the live pipeline.

ON THE STORED T1_score
----------------------
The record already carries transition.T1_score. In france, germany and italy it
correlates 0.9996 with the formula above -- it is real, not fabricated -- but
1.0000 with DER_ratio alone, so it is derived from one sub-metric where the
construct specifies three. In norway it correlates 0.0762 with its own inputs.

This script does NOT touch T1_score. It writes components.T from the published
formula and records both values, so the divergence is visible and can be
decided on rather than silently resolved.

CONVENTION #56
--------------
A record missing any sub-metric gets nothing: components.T is left exactly as
found and the record is counted as SKIPPED. There is no partial derivation and
no fallback constant. Fleet percentiles are computed per country over the
records that DO have the input, and the count is reported -- Method B's anchors
"update with each fleet run" per section 03, so the population they are drawn
from is part of the provenance.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUB = ("DER_ratio", "DER_variability", "EV_load_ratio")
ALPHA = {"DER_ratio": 0.50, "DER_variability": 0.30, "EV_load_ratio": 0.20}
FC = ("SSI_v4_2_Complete_Formula_Construct_Italy_v3.html §02/§03/§04 "
      "(canonical anchor 22 July 2026, Phase G.4)")

sys.path.insert(0, str(ROOT / "scripts"))
from pipeline.scoring.engine import soft_clip                       # noqa: E402
from enrich_esg_gaps import stable_hash                              # noqa: E402

# Refuse to derive from inputs that are themselves a hash of the name.
HASH_R = 0.99


def inputs_are_fabricated(subs):
    """Do the sub-metrics reproduce vary(base, name, spread)?

    Learned the hard way. On 29 August 2026 this script derived italy's
    components.T from its transition block and the result was committed — a
    correct T1 computation over three name hashes, carrying a provenance
    marker asserting it came from the canonical construct. Worse than the hash
    it replaced, because it looked sourced.

    vary(base, name, spread) = base * (1 + (stable_hash(name) - 0.5) * 2 *
    spread), so a fabricated sub-metric is an exact affine function of
    stable_hash(name) and correlates with it at |r| = 1.000. Measured across
    the cohort:

        r = 1.000 : canada, france, germany, italy, japan, portugal, spain,
                    uk, us   -- transition block is a name hash
        r < 0.30  : the other 25, including norway, finland, sweden, turkey

    france's DER_ratio is vary(0.48, name, 0.25); italy's is
    vary(0.61, name, 0.25). Clean per-country base constants with name-hash
    jitter — the same mechanism as the components themselves.

    Returns {sub_metric: |r|} for any that breach HASH_R, else {}.
    """
    named = [s for s in subs
             if isinstance(s.get("transition"), dict) and s.get("name") is not None
             and all(isinstance(s["transition"].get(k), (int, float)) for k in SUB)]
    if len(named) < 50:
        return {}
    h = [stable_hash(s["name"]) for s in named]
    hm = sum(h) / len(h)
    hv = sum((x - hm) ** 2 for x in h)
    out = {}
    for k in SUB:
        v = [s["transition"][k] for s in named]
        vm = sum(v) / len(v)
        vv = sum((x - vm) ** 2 for x in v)
        if hv <= 0 or vv <= 0:
            continue
        cov = sum((a - hm) * (b - vm) for a, b in zip(h, v))
        r = abs(cov / (hv ** 0.5 * vv ** 0.5))
        if r > HASH_R:
            out[k] = r
    return out


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    i = q * (len(sorted_vals) - 1)
    lo, hi = int(i), min(int(i) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


def method_b(x, p5, p95):
    """soft_clip((x - P5) / (P95 - P5)) — section 03.

    soft_clip_upper is the engine's own function, so the top of the range is
    compressed exactly as the master equation compresses it rather than hard
    truncated. The floor is 0: the construct specifies a soft clip at P95 only.
    """
    if p95 is None or p5 is None or p95 <= p5:
        return None
    # soft_clip, NOT soft_clip_upper. Construct section 03 defines both
    # Method A and Method B as N(x) = soft_clip((x - P5)/(P95 - P5)) and
    # names this function. soft_clip_upper is the R_final overflow
    # compressor: discontinuous at 1.0, so a ratio of 1.0001 returned
    # 0.2693 and the worst substations in the fleet published as
    # mid-fleet. M-006, re-scoped 31 August 2026.
    return soft_clip((x - p5) / (p95 - p5))


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if not shards:
        subs = man.get("substations")
        if subs is None:
            raise ValueError("manifest has neither substations nor shards")
        return man, subs, None
    subs, paths = [], []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        block = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(block)
        paths.append((p, len(block), isinstance(raw, list)))
    if not subs:
        raise ValueError(f"{len(shards)} shards declared but no records read")
    return man, subs, paths


def derive(subs):
    """Returns (n_derived, n_skipped, anchors, deltas)."""
    usable = [s for s in subs
              if isinstance(s.get("transition"), dict)
              and all(isinstance(s["transition"].get(k), (int, float)) for k in SUB)]
    anchors = {}
    degenerate = []
    for k in SUB:
        vals = sorted(s["transition"][k] for s in usable)
        p5, p95 = percentile(vals, 0.05), percentile(vals, 0.95)
        anchors[k] = (p5, p95)
        if p5 is not None and p95 is not None and p95 <= p5:
            degenerate.append(f"{k} ({len(set(vals))} distinct value(s) "
                              f"across {len(vals):,} records)")
    # Convention #56: refuse the country and say why. A sub-metric with one
    # distinct value across a whole fleet carries no information about any
    # substation in it, and Method B correctly declines to normalise it. The
    # composite must not be quietly rebuilt from the two that remain — that
    # would reweight T without disclosing it.
    if degenerate:
        raise ValueError("degenerate sub-metric, Method B declines: "
                         + "; ".join(degenerate))
    derived = skipped = 0
    deltas = []
    for s in subs:
        t = s.get("transition")
        if not isinstance(t, dict) or not all(
                isinstance(t.get(k), (int, float)) for k in SUB):
            skipped += 1
            continue
        # Normalise first, THEN weight. The previous form multiplied inside
        # the comprehension, so a None from method_b raised TypeError before
        # the guard on the next line could ever see it: the guard was written
        # correctly and placed one line too late, and was unreachable.
        norm = [method_b(t[k], *anchors[k]) for k in SUB]
        if any(v is None for v in norm):
            skipped += 1
            continue
        parts = [ALPHA[k] * v for k, v in zip(SUB, norm)]
        t1 = round(sum(parts), 4)
        comps = s.setdefault("components", {})
        old = comps.get("T")
        comps["T"] = t1
        s["_component_T_source"] = (
            f"derived per {FC}: T1 = 0.50*N(DER_ratio) + 0.30*N(DER_variability)"
            f" + 0.20*N(EV_load_ratio), Method B over this country's fleet"
            f" P5/P95 of "
            f"{len(usable):,} records")
        if isinstance(old, (int, float)):
            deltas.append(t1 - old)
        derived += 1
    return derived, skipped, anchors, deltas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  components.T from the transition block — {FC}\n")
    print(f"  {'country':<14}{'derived':>9}{'skipped':>9}{'med Δ':>9}"
          f"{'p95 |Δ|':>9}{'ΔR_base':>10}")
    tot_d = tot_s = 0
    refused = []
    for slug in sorted(slugs):
        try:
            man, subs, paths = load(slug)
        except Exception as ex:
            print(f"  {slug:<14}UNREADABLE: {ex}")
            continue
        fab = inputs_are_fabricated(subs)
        if fab:
            detail = ", ".join(f"{k} r={v:.3f}" for k, v in sorted(fab.items()))
            print(f"  {slug:<14}REFUSED — transition block is a hash of the "
                  f"substation name ({detail})")
            refused.append(slug)
            continue
        try:
            d, sk, anchors, deltas = derive(subs)
        except Exception as ex:
            # A refusal is a result, not a crash. Before this, a degenerate
            # sub-metric aborted the whole run on the first country that had
            # one, so the 34 countries after it in the alphabet were never
            # reached.
            print(f"  {slug:<14}REFUSED — {ex}")
            refused.append(slug)
            continue
        tot_d += d
        tot_s += sk
        if deltas:
            ds = sorted(deltas)
            med = ds[len(ds) // 2]
            p95 = sorted(abs(x) for x in ds)[int(len(ds) * 0.95)]
            # T enters R_base at global weight 0.05
            print(f"  {slug:<14}{d:>9,}{sk:>9,}{med:>+9.4f}{p95:>9.4f}"
                  f"{0.05 * med:>+10.4f}")
        else:
            print(f"  {slug:<14}{d:>9,}{sk:>9,}{'—':>9}{'—':>9}{'—':>10}")
        if args.verbose:
            for k in SUB:
                print(f"      {k:<18}P5 {anchors[k][0]!s:>10}  P95 {anchors[k][1]!s:>10}")
        if not args.dry_run and d:
            man.setdefault("meta", {}).setdefault("component_derivations", []).append({
                "component": "T", "at_utc": datetime.now(timezone.utc).isoformat(),
                "formula_construct": FC, "n_derived": d, "n_skipped": sk,
                "anchors": {k: list(anchors[k]) for k in SUB}})
            if paths is None:
                man["substations"] = subs
                (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
            else:
                i = 0
                for p, n, was_list in paths:
                    block = subs[i:i + n]
                    i += n
                    p.write_text(json.dumps(block if was_list
                                            else {"substations": block}))
                (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))

    print(f"  {'-'*60}")
    print(f"  {'TOTAL':<14}{tot_d:>9,}{tot_s:>9,}")
    print(f"\n  {'DRY RUN — nothing written' if args.dry_run else 'APPLIED'}")
    if refused:
        print(f"  REFUSED {len(refused)}: {', '.join(refused)} — their transition\n"
              f"  block is vary(base, name, spread), so deriving T from it would\n"
              f"  produce a real formula over a name hash and label it sourced.")
    if tot_s:
        print(f"  {tot_s:,} records lack a sub-metric and were left untouched "
              f"(Convention #56).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
