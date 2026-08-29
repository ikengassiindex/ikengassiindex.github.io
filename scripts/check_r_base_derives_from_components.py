#!/usr/bin/env python3
"""
R_base must come from the components. For 135,844 substations it is zero.

    python3 scripts/check_r_base_derives_from_components.py --all
    python3 scripts/check_r_base_derives_from_components.py --all --strict
    python3 scripts/check_r_base_derives_from_components.py uk --verbose
    python3 scripts/check_r_base_derives_from_components.py --all --update-baseline

WHAT THIS GATES
---------------
R_base_median is compute_r_base(components) -- a weighted sum over the six
component scores. On 29 August 2026 it was exactly 0.0 on 135,844 substations
across 27 countries, 21.8% of the cohort. That population is TWO defects, and
the checks below separate them:

  57,351  components present and populated, R_base zeroed anyway
          (uk 57,207, canada 138, turkey 6) -- the Wave-4 L3 regression,
          re-derivable from the components that are sitting in the record
  78,558  components == {} entirely -- nothing to re-derive from, a deeper
          problem, and 78,493 of them are published with a real band anyway

With R_base = 0 the v4.2 master equation degenerates:

    R_median = soft_clip_upper(0 x PI mult_i) + SUM (add_j - 1.0) = add_sum

and only R6c_flood is additive. Verified on uk: of 57,207 zeroed records,
R_median == add_sum on 57,207 -- 100.0%. For those substations the composite
resilience score is the flood modifier and nothing else. The components are
right there in the record, contributing zero.

    uk        57,207 / 59,744   95.8%      poland    25,517 / 27,764   91.9%
    austria   13,979 / 14,720   95.0%      czechia    7,825 /  8,899   87.9%

This is a known defect with a known remedy. france's _provenance records it
being corrected on 22 July 2026 by scripts/fix_wave4_r_base_regression.py:
R_base before min 0.0, max 0.0, unique 1; after min 0.2517, max 0.4450,
unique 1726. The pass reached france and stopped. uk's _provenance history is
empty.

FIVE CHECKS
-----------
  ZERO        R_base_median == 0.0 with components populated
  DRIFT       R_base_median disagrees with compute_r_base(components)
  ONLY_FLOOD  R_median == add_sum -- the score is the additive modifier alone
  NO_COMPS    components absent or empty, so nothing can be derived or checked
              (Convention #56: reported, never counted as clean)
  BANDED_BLIND a record with NO components published with a real band rather
              than "Unclassified". These score add_sum alone, which is small,
              so they land at the safe end -- 65,439 Low and 13,054 Medium --
              and pull the country's P5 down, shifting everyone else up
  UNFIXED     country-level: has ZERO records and no L3_R_base_regression_fix
              in its _provenance history -- i.e. the existing remedy has never
              been run against it

WHY THIS GATE HAS A REACHABLE GREEN
-----------------------------------
The master-equation gate cannot go green until a doctrine question is settled.
This one can: the inputs are intact, compute_r_base reproduces the stored value
on 100.0% of records in 38 of 39 countries, and the fix exists and has run
successfully once. The baseline here is a debt to be paid down to zero, not a
permanent fixture.

Task #520: the loader refuses to read data['substations'] off a sharded
manifest, which would otherwise report a clean cohort it never looked at.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "r_base_baseline.json"
CHECKS = ("ZERO", "DRIFT", "ONLY_FLOOD", "NO_COMPS", "BANDED_BLIND")
TOL = 5e-4
FIX_ACTION = "L3_R_base_regression_fix"

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from pipeline.scoring.engine import compute_r_base
except Exception as ex:                                    # pragma: no cover
    sys.exit(f"ABORT: cannot import compute_r_base — {ex}. This check must use "
             f"the engine's own derivation or it is testing something else.")


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_manifest(slug):
    return json.loads((ROOT / slug / "ssi-data.json").read_text())


def load_substations(slug, man=None):
    m = man or load_manifest(slug)
    shards = m.get("substations_shards")
    if not shards:
        subs = m.get("substations")
        if subs is None:
            raise ValueError("manifest has neither substations nor shards")
        return subs
    out = []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        r = json.loads(p.read_text())
        out.extend(r if isinstance(r, list) else (r.get("substations") or []))
    if not out:
        raise ValueError(f"{len(shards)} shards declared but no records read")
    return out


def fix_has_run(man):
    """Has fix_wave4_r_base_regression.py been recorded against this country?"""
    hist = (man.get("_provenance") or {}).get("history") or []
    return any(e.get("action") == FIX_ACTION for e in hist)


def audit(subs):
    c = {k: 0 for k in CHECKS}
    example = None
    for s in subs:
        comps = s.get("components") or {}
        rb = s.get("R_base_median")
        med, ad = s.get("R_median"), s.get("add_sum")

        if not comps or not any(isinstance(v, (int, float)) for v in comps.values()):
            c["NO_COMPS"] += 1
            # Convention #56: a substation with no component data has no basis
            # for a resilience band. classify_band's peer for that state is
            # "Unclassified". 78,493 of these are published with a real band
            # instead -- 65,439 Low and 13,054 Medium -- because with no
            # components R_median collapses to add_sum, the flood modifier
            # alone, which is small. So a record with no data is published at
            # the SAFE end of the scale, and drags the country's P5 down with
            # it, shifting every other substation's normalised band upward.
            if s.get("classification") not in (None, "Unclassified"):
                c["BANDED_BLIND"] += 1
        else:
            if rb == 0.0:
                c["ZERO"] += 1
                if example is None:
                    example = s
            if rb is not None and abs(compute_r_base(comps) - rb) > TOL:
                c["DRIFT"] += 1
        if med is not None and ad is not None and abs(med - ad) <= TOL:
            c["ONLY_FLOOD"] += 1
    return c, example


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    live, unfixed, unreadable, total = {}, [], [], 0

    for slug in sorted(slugs):
        try:
            man = load_manifest(slug)
            subs = load_substations(slug, man)
        except Exception as ex:
            unreadable.append((slug, str(ex)))
            continue
        total += len(subs)
        c, ex = audit(subs)
        live[slug] = c
        if c["ZERO"] and not fix_has_run(man):
            unfixed.append((slug, c["ZERO"], len(subs)))
        if args.verbose and any(c.values()):
            print(f"\n  {slug} ({len(subs):,})")
            for k in CHECKS:
                if c[k]:
                    print(f"    {k:<11}{c[k]:>9,}")
            if ex is not None:
                print(f"    e.g. {ex.get('substation_id')}: R_base "
                      f"{ex.get('R_base_median')} · mult {ex.get('mult_product')} · "
                      f"add {ex.get('add_sum')} · R_median {ex.get('R_median')}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(live, indent=1, sort_keys=True) + "\n")
        print(f"\n  baseline written: {BASELINE.relative_to(ROOT)} "
              f"({len(live)} countries)")
        print("  This baseline is a debt to be paid down, not a fixture.")
        return 0

    print(f"\n  R_base derivation — {len(live)} countries, {total:,} substations\n")
    print(f"    {'check':<12}{'live':>12}{'baseline':>12}{'delta':>10}")
    regressions = []
    for k in CHECKS:
        lv = sum(c[k] for c in live.values())
        bl = sum(base.get(s, {}).get(k, 0) for s in live)
        d = lv - bl
        if d > 0:
            regressions.append(k)
        print(f"    {k:<12}{lv:>12,}{bl:>12,}{d:>+10,}"
              f"{'  <-- REGRESSION' if d > 0 else ''}")

    worst = sorted(((c["ZERO"], s) for s, c in live.items() if c["ZERO"]),
                   reverse=True)
    if worst:
        print("\n    worst affected:")
        for z, s in worst[:12]:
            print(f"      {s:<16}{z:>9,} zeroed")

    print(f"\n    UNFIXED     {len(unfixed):>12,}"
          f"{'':>12}{'':>10}  countries with zeroed R_base and no record of "
          f"{FIX_ACTION}")
    for s, z, n in sorted(unfixed, key=lambda t: -t[1])[:15]:
        print(f"      {s:<16}{z:>9,} / {n:<9,} and the fix has never run here")

    if unreadable:
        print("\n    UNREADABLE (Convention #56 — not counted as clean):")
        for s, why in unreadable:
            print(f"      {s:<16}{why}")

    if not base:
        print("\n  No baseline recorded yet. Run --update-baseline to record the\n"
              "  known population; --strict then fails on any increase.")

    if args.strict:
        if unreadable:
            print("\nSTRICT: countries unreadable.")
            return 1
        if regressions:
            print(f"\nSTRICT: R_base derivation regressed against baseline "
                  f"({', '.join(regressions)}).")
            return 1
        print("\nSTRICT: no regression against baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
