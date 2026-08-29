#!/usr/bin/env python3
"""
The master equation must close, and the page must not claim it does when it doesn't.

    python3 scripts/check_master_equation_closure.py --all
    python3 scripts/check_master_equation_closure.py --all --strict
    python3 scripts/check_master_equation_closure.py france --verbose
    python3 scripts/check_master_equation_closure.py --all --update-baseline

THE RELATION
------------
Every country page publishes this row in its ssi-metadata.js, and renders it on
the methodology page as a passed self-check:

    { check: 'v4.2 master equation closure',
      criterion: 'R_final = soft_clip_upper(R_base x PI mult_i) + SUM (add_j - 1.0)
                  -- only R6c is additive, applied OUTSIDE soft_clip',
      status: 'verified', tier: 'v4.2' }

All four terms are published per substation as R_base_median, mult_product,
add_sum and R_median. Measured on 29 August 2026 the relation held on 28.1% of
622,039 records. italy 0.0%, japan 0.2%, germany 1.1%, france 1.3%, us 1.3% --
398,599 substations in the five largest fleets, essentially none of them. The
pages reported it verified throughout.

FOUR CHECKS
-----------
  CLOSURE     |soft_clip(R_base x mult_product) + add_sum - R_median| > 5e-4
  RE_CORE     mult_product equals the ESG composite's multiplicative core,
              R6d x R6e x R8 x R9 x R10. On france and germany this is 100.0%
              of records: the field that should hold PI mult_i of the master
              equation holds the Re_raw core instead --
                  Re_raw = (R6d x R6e x R8 x R9 x R10) + (R6c - 1.00)
              named for the mechanism, so a future reader does not have to
              rediscover it.
  INCOMPLETE  one or more of the four terms absent, so closure cannot be
              evaluated. Convention #56: reported, never silently skipped.
  DECLARED    the country's ssi-metadata.js asserts status 'verified' for the
              closure check while fewer than 99% of its records close. This is
              the only check here that looks at a published claim rather than
              at arithmetic, and it is the one that matters to a reader.

The 5e-4 tolerance is the rounding floor: every operand is stored to 4 decimals.

BASELINE
--------
447,000-odd records fail today, so an unbaselined --strict would be red forever
and would bury the next regression in debt it can never clear. The known
population is recorded per country in scripts/master_equation_baseline.json and
--strict fails only on an INCREASE. Every run prints live, baseline and delta,
so nothing is hidden; lowering the baseline is how progress is measured.

DECLARED is deliberately NOT baselined. A page asserting a verification that
does not hold is not technical debt to be amortised -- it is a statement to the
reader, and it should fail from the first run until it is either true or
withdrawn.

Task #520: the loader refuses to read data['substations'] off a sharded
manifest, which would otherwise report a clean cohort it never looked at.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "master_equation_baseline.json"
CHECKS = ("CLOSURE", "RE_CORE", "INCOMPLETE")
TOL = 5e-4
RE_CORE_KEYS = ("R6d_wildfire", "R6e_winter", "R8_adapt", "R9_compound", "R10_just")

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from pipeline.scoring.engine import soft_clip_upper
except Exception as ex:                                    # pragma: no cover
    sys.exit(f"ABORT: cannot import soft_clip_upper — {ex}. The check cannot "
             f"be evaluated with a local re-implementation; it must use the "
             f"engine's own function or it is testing something else.")

_DECLARED = re.compile(
    r"check:\s*'v4\.2 master equation closure'.*?status:\s*'([a-z_]+)'", re.S)


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_substations(slug):
    m = json.loads((ROOT / slug / "ssi-data.json").read_text())
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


def declared_status(slug):
    """What the country's own metadata says about closure, or None."""
    p = ROOT / slug / "ssi-metadata.js"
    if not p.exists():
        return None
    m = _DECLARED.search(p.read_text(errors="replace"))
    return m.group(1) if m else None


def audit(subs):
    c = {k: 0 for k in CHECKS}
    closes = 0
    evaluable = 0
    worst = (0.0, None)
    for s in subs:
        rb, mp = s.get("R_base_median"), s.get("mult_product")
        ad, med = s.get("add_sum"), s.get("R_median")
        if None in (rb, mp, ad, med):
            c["INCOMPLETE"] += 1
        else:
            evaluable += 1
            d = abs(soft_clip_upper(rb * mp) + ad - med)
            if d > TOL:
                c["CLOSURE"] += 1
                if d > worst[0]:
                    worst = (d, s.get("substation_id"))
            else:
                closes += 1
        mods = s.get("modifiers") or {}
        if mp is not None and all(k in mods for k in RE_CORE_KEYS):
            core = 1.0
            for k in RE_CORE_KEYS:
                core *= mods[k]
            if abs(core - mp) <= TOL:
                c["RE_CORE"] += 1
    share = closes / evaluable if evaluable else None
    return c, share, worst


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
    live, shares, declared, unreadable, total = {}, {}, {}, [], 0

    for slug in sorted(slugs):
        try:
            subs = load_substations(slug)
        except Exception as ex:
            unreadable.append((slug, str(ex)))
            continue
        total += len(subs)
        c, share, worst = audit(subs)
        live[slug], shares[slug] = c, share
        declared[slug] = declared_status(slug)
        if args.verbose:
            pct = "n/a" if share is None else f"{100 * share:.1f}%"
            print(f"\n  {slug} ({len(subs):,}) closes {pct}  "
                  f"declared '{declared[slug]}'")
            for k in CHECKS:
                if c[k]:
                    print(f"    {k:<11}{c[k]:>9,}")
            if worst[1]:
                print(f"    worst |delta| {worst[0]:.5f} at {worst[1]}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(live, indent=1, sort_keys=True) + "\n")
        print(f"\n  baseline written: {BASELINE.relative_to(ROOT)} "
              f"({len(live)} countries)")
        print("  NOTE: DECLARED is not baselined and never will be.")
        return 0

    print(f"\n  Master-equation closure — {len(live)} countries, "
          f"{total:,} substations\n")
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

    ev = sum(1 for s in live if shares[s] is not None)
    if ev:
        w = [shares[s] for s in live if shares[s] is not None]
        print(f"\n    cohort closure: "
              f"{100 * sum(w) / len(w):.1f}% mean across {ev} countries")

    # DECLARED — the published claim, never baselined
    false_claims = [(s, shares[s]) for s in live
                    if declared[s] == "verified"
                    and shares[s] is not None and shares[s] < 0.99]
    print(f"\n    DECLARED    {len(false_claims):>12,}"
          f"{'':>12}{'':>10}  countries claiming 'verified' below 99% closure")
    if false_claims:
        for s, sh in sorted(false_claims, key=lambda t: t[1])[:20]:
            print(f"      {s:<16}page says verified · {100 * sh:5.1f}% of records close")

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
        if false_claims:
            print(f"\nSTRICT: {len(false_claims)} countries publish "
                  f"'verified' for a closure check that does not hold.")
            return 1
        if regressions:
            print(f"\nSTRICT: closure regressed against baseline "
                  f"({', '.join(regressions)}).")
            return 1
        print("\nSTRICT: no regression, and no country claims a verification "
              "it does not have.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
