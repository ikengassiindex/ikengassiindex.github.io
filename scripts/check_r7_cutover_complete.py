#!/usr/bin/env python3
"""check_r7_cutover_complete.py — does the PUBLISHED DATA show the R7 cutover?

Per doctrine/DOCTRINE_a_check_must_read_the_artefact.md. The existing sentinel
`tests/test_r7_cyber_v2_construct.py::TestPostCutoverInvariants` asserts
versions.json, edition-config.json, the registry flags and the shard thresholds.
Every one of those reads code or config; none reads a substation record. It is
GREEN today while the cutover has not happened. This script is the missing half.

It answers three questions against every published record in all 39 countries:

  A. Is `_r7_cyber_v1_retired` True?
  B. Is `modifiers.R7_cyber` (v1) gone from the emitted modifier set?
  C. Which modifier set does the published `mult_product` actually reproduce?
     Four hypotheses are tested per record, not one:
       v1_only   — chain with R7_cyber,    without R7_cyber_v2
       v2_only   — chain with R7_cyber_v2, without R7_cyber
       both      — chain with BOTH (the double count)
       neither   — chain with neither

(C) is the one that matters. `modifier_registry.compute_modifier_terms` carries a
comment stating that before the retired-skip guard existed the function
multiplied every modifier present, so a record carrying both had the cyber
modifier applied twice, and that "Sweden's published scores carry that
double-count today". That is a claim about the ARTEFACT, and this script is how
it gets confirmed or refuted rather than repeated.

Read-only. Exits 0 only when the cutover is complete cohort-wide.

Usage:
    python3 scripts/check_r7_cutover_complete.py [--country SLUG] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY  # noqa: E402

V1 = "R7_cyber"
V2 = "R7_cyber_v2"
RETIRED_KEY = "_r7_cyber_v1_retired"
TOL = 5e-5          # published mult_product is round(x, 4)


def mult_product_over(modifiers, exclude):
    """Reproduce compute_modifier_terms' multiplicative half for a chosen set.

    Deliberately does NOT call compute_modifier_terms: that function now skips
    retired modifiers, which is exactly the behaviour under test. Reproducing
    the arithmetic here lets the retired modifier be put back IN, so the
    double-count hypothesis can be tested rather than assumed away.
    """
    p = 1.0
    for name, value in modifiers.items():
        if name in exclude:
            continue
        spec = MODIFIER_REGISTRY.get(name)
        if spec is None or spec.get("type") != "mult":
            continue
        if value is None:
            continue
        lo, hi = spec["range"]
        p *= max(lo, min(hi, value))
    return p


def records(root, country):
    main = os.path.join(root, country, "ssi-data.json")
    d = json.load(open(main))
    shards = d.get("substations_shards") or []
    if shards:
        for sh in shards:
            p = os.path.join(root, country, os.path.basename(sh.get("path", "")))
            if not os.path.exists(p):
                sys.stderr.write("MISSING SHARD %s %s\n" % (country, p))
                continue
            sd = json.load(open(p))
            for r in (sd.get("substations") if isinstance(sd, dict) else sd) or []:
                yield r
    else:
        for r in (d.get("substations") or []):
            yield r


def check_country(root, country):
    st = {
        "n": 0, "retired_true": 0, "retired_false": 0, "retired_absent": 0,
        "v1_present": 0, "v2_present": 0, "v2_no_v1": 0,
        "fit": Counter(), "no_published_mult": 0,
    }
    for r in records(root, country):
        st["n"] += 1
        mo = r.get("modifiers") or {}
        has1, has2 = V1 in mo and mo[V1] is not None, V2 in mo and mo[V2] is not None
        st["v1_present"] += has1
        st["v2_present"] += has2
        st["v2_no_v1"] += (has2 and not has1)

        rk = r.get(RETIRED_KEY)
        if rk is True:
            st["retired_true"] += 1
        elif rk is False:
            st["retired_false"] += 1
        else:
            st["retired_absent"] += 1

        pub = r.get("mult_product")
        if pub is None:
            st["no_published_mult"] += 1
            continue
        cand = {
            "v1_only": mult_product_over(mo, {V2}),
            "v2_only": mult_product_over(mo, {V1}),
            "both":    mult_product_over(mo, set()),
            "neither": mult_product_over(mo, {V1, V2}),
        }
        hits = [k for k, v in cand.items() if abs(round(v, 4) - pub) <= TOL]
        # v1_only and v2_only coincide when only one of the two is present, and
        # all four coincide when neither is. Report the DEGENERATE case honestly
        # rather than crediting the first match.
        if not hits:
            st["fit"]["none"] += 1
        elif len(hits) == 1:
            st["fit"][hits[0]] += 1
        else:
            st["fit"]["ambiguous(" + "|".join(sorted(hits)) + ")"] += 1
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    root = REPO
    countries = ([a.country] if a.country else
                 sorted(x for x in os.listdir(root)
                        if os.path.isdir(os.path.join(root, x))
                        and os.path.exists(os.path.join(root, x, "ssi-data.json"))))

    tot = defaultdict(int)
    fit_tot = Counter()
    rows = []
    for c in countries:
        st = check_country(root, c)
        rows.append((c, st))
        for k, v in st.items():
            if k == "fit":
                fit_tot.update(v)
            else:
                tot[k] += v

    if not a.quiet:
        print("%-14s %8s %8s %8s %8s  %s" % (
            "country", "n", "v1", "v2", "retired", "mult_product fits"))
        for c, st in rows:
            top = ", ".join("%s %d" % (k, v) for k, v in st["fit"].most_common(3))
            print("%-14s %8d %8d %8d %8d  %s" % (
                c, st["n"], st["v1_present"], st["v2_present"],
                st["retired_true"], top))

    n = tot["n"]
    print("\n%s" % ("=" * 72))
    print("ESTATE  n = %d" % n)
    print("  A  _r7_cyber_v1_retired True     %8d   False %8d   absent %8d"
          % (tot["retired_true"], tot["retired_false"], tot["retired_absent"]))
    print("  B  modifiers.R7_cyber present    %8d   (must be 0 post-cutover)"
          % tot["v1_present"])
    print("     modifiers.R7_cyber_v2 present %8d" % tot["v2_present"])
    print("     v2 with no v1 beneath it      %8d" % tot["v2_no_v1"])
    print("  C  published mult_product fits:")
    for k, v in fit_tot.most_common():
        print("       %-34s %8d  %5.1f%%" % (k, v, 100.0 * v / n if n else 0))

    fail = []
    if tot["retired_true"] != tot["retired_true"] + tot["retired_false"]:
        fail.append("A: %d records are not marked retired" % tot["retired_false"])
    if tot["v1_present"]:
        fail.append("B: %d records still carry modifiers.R7_cyber" % tot["v1_present"])
    bad_fit = sum(v for k, v in fit_tot.items()
                  if k != "v2_only" and not k.startswith("ambiguous"))
    if bad_fit:
        fail.append("C: %d records' mult_product does not reproduce from v2" % bad_fit)

    print("\n%s" % ("=" * 72))
    if fail:
        print("CUTOVER INCOMPLETE")
        for f in fail:
            print("  - %s" % f)
        return 1
    print("CUTOVER COMPLETE — all three conditions hold cohort-wide")
    return 0


if __name__ == "__main__":
    sys.exit(main())
