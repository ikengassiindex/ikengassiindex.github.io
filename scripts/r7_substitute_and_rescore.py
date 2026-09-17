#!/usr/bin/env python3
"""r7_substitute_and_rescore.py — step 4 of doctrine/PLAN_r7_cutover.md.

Applies the R7_cyber v1 -> v2 SUBSTITUTION to the published records and
rescores, WITHOUT re-running ingestion.

Why not `python -m scripts.pipeline.run --all` (Phase zeta). Measured
17 September 2026: `merge_and_rescore` gates its rescore on
`needs_rescore = has_seismic or has_climate or has_socio`, so with no ingestion
results it rescores zero substations. There is no rescore-only path through the
orchestrator. Phase zeta therefore means a full ingestion pass over 39 countries,
which changes far more than R7 in one movement and makes any bad outcome hard to
attribute. `score_substation` itself measures 4.8 ms per record — under an hour
for the whole estate. This script is that hour, and nothing else.

Per record:
  1. If R7_cyber_v2 is absent, compute it from the country inputs. Sweden's 2,582
     v2-less records are the only such population; their computed value is
     bit-identical to the 1,192 that already carry one, v2 being a national
     constant.
  2. substitute_v1_with_v2 — snapshot v1, remove it from the emitted modifier
     set, mark _r7_cyber_v1_retired True.
  3. score_substation — recompute the chain and the Monte Carlo.

DRY RUN BY DEFAULT. Nothing is written without --write.

TWO THINGS THIS DOES NOT DO, both deliberate:

  * It does not settle `classification`. score_substation assigns the ABSOLUTE
    band via classify_band, while the published band is the per-country
    percentile of Phase 2D. Phase eta —
    `scripts/normalise_bands_per_country.py --all-countries` — MUST follow, or
    every country's bands silently revert to absolute thresholds. Band movement
    is reported here both ways and both are provisional.

  * It does not separate the R7 effect from the stale-baseline effect in the
    five countries whose published mult_product does not reproduce from their
    own modifiers (france, germany, us, italy, japan — 397,852 records). For
    those, the movement reported is BOTH effects summed, and this script says so
    per country rather than quoting one cohort-wide figure. See
    doctrine/RESULT_the_r7_data_sentinel.md.

Usage:
    python3 scripts/r7_substitute_and_rescore.py --country sweden
    python3 scripts/r7_substitute_and_rescore.py --country sweden --write
    python3 scripts/r7_substitute_and_rescore.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data  # noqa: E402
from scripts.pipeline.scoring import r7_cyber_v2 as R7  # noqa: E402
from scripts.pipeline.scoring.engine import (  # noqa: E402
    score_substation, classify_band, classify_band_normalised,
)
from scripts.pipeline.scoring.modifier_registry import compute_modifier_terms  # noqa: E402

# The five whose published mult_product does not reproduce from their own
# modifiers. Movement measured on these is the substitution PLUS the accumulated
# drift, and must never be quoted as the substitution alone.
STALE_BASELINE = {"france", "germany", "us", "italy", "japan"}


def process_country(slug, write=False, limit=None):
    t0 = time.time()
    country_inputs = R7.load_country_inputs(slug)
    data, subs, is_sharded = load_ssi_data(slug)
    if not subs:
        return {"country": slug, "error": "no substations"}

    st = Counter()
    st["n"] = len(subs)
    band_abs = Counter()
    band_norm = Counter()
    dR = []
    out = []

    for sub in (subs[:limit] if limit else subs):
        mo = sub.get("modifiers") or {}
        before_R = sub.get("R_median")
        before_band = sub.get("classification")
        before_mult = sub.get("mult_product")

        # (1) complete v2 where it is absent
        v2 = mo.get("R7_cyber_v2")
        if v2 is None:
            if not country_inputs:
                st["skipped_no_country_inputs"] += 1
                out.append(sub)
                continue
            v2, audit = R7.compute_r7_cyber_v2_for_sub(sub, country_inputs)
            sub[R7.AUDIT_TRAIL_KEY] = R7.AUDIT_TRAIL_VALUE
            if audit.get("fallback_reason"):
                sub[R7.FALLBACK_KEY] = audit["fallback_reason"]
            st["v2_computed"] += 1

        # (2) the substitution, from its single home
        v1_val = R7.substitute_v1_with_v2(sub, v2)
        st["v1_removed"] += (v1_val is not None)
        st["no_v1_beneath"] += (v1_val is None)

        # (3) rescore. Convention #56: a record with no components is not
        # scoreable and is left exactly as it stands, counted not crashed on.
        if not sub.get("components"):
            st["skipped_no_components"] += 1
            out.append(sub)
            continue
        try:
            updated = score_substation(sub)
        except Exception as exc:                      # noqa: BLE001
            st["rescore_failed"] += 1
            sys.stderr.write("RESCORE FAILED %s %s: %s\n"
                             % (slug, sub.get("substation_id"), exc))
            out.append(sub)
            continue
        st["rescored"] += 1
        out.append(updated)

        after_R = updated.get("R_median")
        if before_R is not None and after_R is not None:
            dR.append(after_R - before_R)
        if before_mult is not None and updated.get("mult_product") != before_mult:
            st["mult_product_changed"] += 1

        # bands, both ways, both provisional until Phase eta
        after_abs = updated.get("classification")
        if before_band and after_abs and before_band != after_abs:
            band_abs["changed"] += 1
        if before_R is not None and after_R is not None:
            b4 = classify_band_normalised(before_R, sub.get("R_P5"), sub.get("R_P95"))
            af = classify_band_normalised(after_R, updated.get("R_P5"), updated.get("R_P95"))
            if b4 != af:
                band_norm["changed"] += 1
                band_norm["%s->%s" % (b4, af)] += 1

    res = {
        "country": slug,
        "stale_baseline": slug in STALE_BASELINE,
        "n": st["n"],
        "rescored": st["rescored"],
        "v2_computed": st["v2_computed"],
        "v1_removed": st["v1_removed"],
        "no_v1_beneath": st["no_v1_beneath"],
        "skipped_no_components": st["skipped_no_components"],
        "rescore_failed": st["rescore_failed"],
        "mult_product_changed": st["mult_product_changed"],
        "band_changed_absolute": band_abs["changed"],
        "band_changed_normalised": band_norm["changed"],
        "dR_mean": round(sum(dR) / len(dR), 6) if dR else None,
        "dR_worse": sum(1 for d in dR if d > 0),
        "dR_better": sum(1 for d in dR if d < 0),
        "seconds": round(time.time() - t0, 1),
        "written": False,
    }
    if write and not limit:
        if is_sharded:
            data["substations"] = out
        else:
            data["substations"] = out
        save_ssi_data(slug, data)
        res["written"] = True
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true",
                    help="persist. WITHOUT THIS NOTHING IS WRITTEN.")
    ap.add_argument("--limit", type=int,
                    help="process only the first N records (never writes)")
    a = ap.parse_args()

    if a.all:
        slugs = sorted(x for x in os.listdir(REPO)
                       if os.path.isdir(os.path.join(REPO, x))
                       and os.path.exists(os.path.join(REPO, x, "ssi-data.json")))
    elif a.country:
        slugs = [a.country]
    else:
        ap.error("--country SLUG or --all")

    if not a.write:
        print(">>> DRY RUN — nothing will be written. Pass --write to persist.\n")

    results = []
    for s in slugs:
        r = process_country(s, write=a.write, limit=a.limit)
        results.append(r)
        print(json.dumps(r))

    print("\n" + "=" * 72)
    tot = Counter()
    for r in results:
        for k in ("n", "rescored", "v2_computed", "v1_removed", "no_v1_beneath",
                  "mult_product_changed", "band_changed_normalised",
                  "skipped_no_components", "rescore_failed"):
            tot[k] += r.get(k) or 0
    print("TOTAL over %d countries" % len(results))
    for k, v in tot.items():
        print("  %-26s %8d" % (k, v))
    stale = [r for r in results if r["stale_baseline"]]
    if stale:
        print("\nOF WHICH, the five whose baseline does not reproduce — their movement")
        print("is the substitution PLUS accumulated drift, and is not comparable:")
        for r in stale:
            print("  %-10s n=%7d  band changes (normalised) %6d  dR mean %s"
                  % (r["country"], r["n"], r["band_changed_normalised"] or 0, r["dR_mean"]))
    print("\nPhase eta MUST follow any --write run:")
    print("  python3 scripts/normalise_bands_per_country.py --all-countries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
