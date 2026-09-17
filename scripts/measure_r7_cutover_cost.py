#!/usr/bin/env python3
"""measure_r7_cutover_cost.py — what the R7 v1->v2 substitution costs, in the
bands the site actually publishes.

Supersedes the band arithmetic in doctrine/RESULT_what_completing_the_R7_cutover_costs.md,
which measured with `classify_band` (ABSOLUTE cutoffs) while the site publishes
per-country normalised bands (Phase 2D). Verified 17 September 2026: recomputing
every record's absolute band from its published R_median reproduces that
document's "published" column bit-for-bit — 67,823 / 99,871 / 384,996 / 67,854 /
1,495 — against a published distribution of 189,211 / 159,928 / 164,836 / 83,340
/ 24,724. Right arithmetic, wrong bands.

METHOD, and why it is built this way.

The substitution's effect on one record is a RATIO of two cyber multipliers, and
nothing else touches the chain:

    ratio = clip(v2) / clip(v1)          both present
          = clip(v2)                     v1 absent  (78,558 records)
          = computed v2 / clip(v1)       v2 absent  (sweden's 2,582)

applied to the published score through the published chain:

    raw0  = R_median - add_sum           == R_base x mult_product
    R_new = soft_clip_upper(raw0 x ratio) + add_sum

This anchors on the PUBLISHED R_median rather than recomputing it, which buys
three things:

  * ratio == 1 gives R_new == R_median EXACTLY. No spurious movement, and no
    Monte Carlo noise — the rescore is never run. See
    FINDING_the_monte_carlo_is_unseeded.md.
  * It works on the five countries whose published mult_product does not
    reproduce from their own modifiers. Their absolute values stay wrong, but
    the R7 EFFECT on them is still exactly measurable, because a ratio applied
    to a stale baseline still isolates the ratio.
  * Exact wherever raw0 <= 1.0, which is where soft_clip_upper is the identity.
    Records above it are counted separately and reported, not silently
    first-ordered.

Bands are compared on a CONSISTENT basis: classify_band_normalised with the
record's own stored country anchors, before and after. The published
`classification` field is reported alongside but not used as the baseline — it
agrees with its own recomputation on only 86.9 per cent of records, which is a
separate open question and must not leak into this measurement.

Read-only. Measures; writes nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from scripts.pipeline.scoring.engine import classify_band_normalised, soft_clip_upper  # noqa: E402
from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY  # noqa: E402
from scripts.pipeline.scoring import r7_cyber_v2 as R7  # noqa: E402

LO, HI = MODIFIER_REGISTRY["R7_cyber_v2"]["range"]
STALE = {"france", "germany", "us", "italy", "japan"}
BANDS = ["Low", "Medium", "High", "Critical", "Extreme", "Unclassified"]


def clip(v):
    return max(LO, min(HI, v))


def chain(modifiers, exclude):
    """Multiplicative half of compute_modifier_terms, with a chosen set removed.

    Not compute_modifier_terms itself: that skips the retired v1, which is the
    behaviour under test. Reproducing the arithmetic here lets v1 be put back in
    so the record's actual chain can be identified.
    """
    p = 1.0
    for name, value in modifiers.items():
        if name in exclude or value is None:
            continue
        spec = MODIFIER_REGISTRY.get(name)
        if spec is None or spec.get("type") != "mult":
            continue
        lo, hi = spec["range"]
        p *= max(lo, min(hi, value))
    return p


def records(country):
    d = json.load(open(os.path.join(REPO, country, "ssi-data.json")))
    sh = d.get("substations_shards") or []
    if sh:
        for s in sh:
            p = os.path.join(REPO, country, os.path.basename(s.get("path", "")))
            if os.path.exists(p):
                sd = json.load(open(p))
                for r in (sd.get("substations") if isinstance(sd, dict) else sd) or []:
                    yield r
    else:
        for r in (d.get("substations") or []):
            yield r


def measure(country):
    ci = None
    st = Counter()
    before = Counter()
    after = Counter()
    moves = Counter()
    for r in records(country):
        st["n"] += 1
        mo = r.get("modifiers") or {}
        R0, add = r.get("R_median"), r.get("add_sum")
        p5, p95 = r.get("_band_norm_R_P5"), r.get("_band_norm_R_P95")
        if R0 is None or add is None:
            st["skipped_no_score"] += 1
            continue

        v1 = mo.get("R7_cyber")
        v2 = mo.get("R7_cyber_v2")
        if v2 is None:
            if ci is None:
                ci = R7.load_country_inputs(country) or {}
            if not ci:
                st["skipped_no_country_inputs"] += 1
                continue
            v2, _audit = R7.compute_r7_cyber_v2_for_sub(r, ci)
            st["v2_computed"] += 1
            mo = dict(mo); mo["R7_cyber_v2"] = v2
        if v1 is None:
            st["no_v1_beneath"] += 1

        # WHICH CHAIN IS THE RECORD ALREADY ON? Assuming it is on v1 is wrong:
        # six countries (canada, finland, norway, sweden, turkey, uk) are already
        # cut over, and applying a v2/v1 ratio to them would add v2 a second time
        # and remove a v1 that was never in their product. Read it, do not assume.
        pub_m = r.get("mult_product")
        m_v1 = chain(mo, {"R7_cyber_v2"})
        m_v2 = chain(mo, {"R7_cyber"})
        m_both = chain(mo, set())
        if pub_m is None:
            st["skipped_no_mult"] += 1
            continue
        fits_v2 = abs(round(m_v2, 4) - pub_m) <= 5e-5
        fits_v1 = abs(round(m_v1, 4) - pub_m) <= 5e-5
        fits_both = abs(round(m_both, 4) - pub_m) <= 5e-5
        if fits_v2:
            ratio = 1.0                       # already cut over: costs nothing
            st["already_cut_over"] += 1
        elif fits_v1:
            ratio = m_v2 / m_v1 if m_v1 else 1.0
            st["on_v1"] += 1
        elif fits_both:
            ratio = m_v2 / m_both if m_both else 1.0
            st["double_counted"] += 1
        else:
            st["baseline_does_not_reproduce"] += 1
            continue                          # cannot attribute; excluded

        raw0 = R0 - add
        if raw0 > 1.0:
            st["compressed_first_order"] += 1
        else:
            st["exact"] += 1
        R1 = soft_clip_upper(raw0 * ratio) + add

        b0 = classify_band_normalised(R0, p5, p95)
        b1 = classify_band_normalised(R1, p5, p95)
        before[b0] += 1
        after[b1] += 1
        if b0 != b1:
            st["band_changed"] += 1
            moves["%s->%s" % (b0, b1)] += 1
            if BANDS.index(b1) > BANDS.index(b0):
                st["worse"] += 1
            else:
                st["better"] += 1
        if abs(R1 - R0) > 1e-12:
            st["R_moved"] += 1
        # does the published label reproduce from its own inputs?
        st["published_label_reproduces"] += (b0 == r.get("classification"))
    return {"country": country, "stale_baseline": country in STALE,
            "st": st, "before": before, "after": after, "moves": moves}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country")
    a = ap.parse_args()
    cts = ([a.country] if a.country else
           sorted(x for x in os.listdir(REPO)
                  if os.path.isdir(os.path.join(REPO, x))
                  and os.path.exists(os.path.join(REPO, x, "ssi-data.json"))))
    rows = [measure(c) for c in cts]

    print("%-14s %8s %9s %8s %8s %7s  %s" % (
        "country", "n", "R moved", "band chg", "%", "worse", "stale"))
    for r in rows:
        s = r["st"]
        n = s["n"] or 1
        print("%-14s %8d %9d %8d %7.1f%% %7d  %s" % (
            r["country"], s["n"], s["R_moved"], s["band_changed"],
            100 * s["band_changed"] / n, s["worse"],
            "YES" if r["stale_baseline"] else ""))

    T = Counter()
    B, A, M = Counter(), Counter(), Counter()
    for r in rows:
        T.update(r["st"]); B.update(r["before"]); A.update(r["after"]); M.update(r["moves"])
    n = T["n"]
    attributable = T["exact"] + T["compressed_first_order"]
    changing = T["on_v1"] + T["double_counted"]
    print("\n" + "=" * 74)
    print("SCOPE — every percentage below states its own denominator.\n")
    print("  estate                                               %8d" % n)
    print("  baseline does NOT reproduce, EXCLUDED, unattributable %8d  %5.1f%% of estate"
          % (T["baseline_does_not_reproduce"], 100 * T["baseline_does_not_reproduce"] / n))
    print("  ATTRIBUTABLE (baseline reproduces)                   %8d  %5.1f%% of estate"
          % (attributable, 100 * attributable / n))
    print("     of which already cut over, cost nil               %8d" % T["already_cut_over"])
    print("     of which on v1, the population that moves         %8d" % T["on_v1"])
    print("     of which double-counted (both in the product)     %8d" % T["double_counted"])
    print("     exact (raw0 <= 1.0, soft_clip_upper is identity)  %8d  %5.1f%% of attributable"
          % (T["exact"], 100 * T["exact"] / attributable if attributable else 0))
    print("     compressed, first-order                           %8d" % T["compressed_first_order"])
    print("\n  v2 computed where absent                             %8d" % T["v2_computed"])
    print("  no v1 beneath (substitution writes, not replaces)    %8d" % T["no_v1_beneath"])
    if changing:
        print("\nWHAT IT COSTS, on the %d attributable records that are not already cut over:" % changing)
        print("  R_median moves                                       %8d  %5.1f%% of those"
              % (T["R_moved"], 100 * T["R_moved"] / changing))
        print("  BAND CHANGES                                         %8d  %5.1f%% of those"
              % (T["band_changed"], 100 * T["band_changed"] / changing))
        print("                                                                 %5.2f%% of the estate"
              % (100 * T["band_changed"] / n))
        print("     to a worse band %d   to a better band %d" % (T["worse"], T["better"]))
    print("\n  band distribution over the %d attributable records, before -> after:" % attributable)
    for b in BANDS:
        if B[b] or A[b]:
            print("     %-13s %8d -> %8d   %+d" % (b, B[b], A[b], A[b] - B[b]))
    print("\n  largest movements:")
    for k, v in M.most_common(6):
        print("     %-26s %7d" % (k, v))
    print("\n  published `classification` reproduces from its own R_median and anchors")
    print("  on %d of the %d attributable = %.1f%% — SEPARATE open question."
          % (T["published_label_reproduces"], attributable,
             100 * T["published_label_reproduces"] / attributable if attributable else 0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
