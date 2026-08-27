#!/usr/bin/env python3
"""
Re-derive confidence_tier from the percentiles already stored on each record.

    python3 scripts/ssi_refresh_confidence_tier.py --all
    python3 scripts/ssi_refresh_confidence_tier.py --all --apply
    python3 scripts/ssi_refresh_confidence_tier.py austria poland --apply

Run from the repo root. Dry run by default.

WHY
---
engine.py::classify_confidence used to answer "high" for a zero-width
confidence interval, because `ci <= 0.10` is true when ci is 0 and a zero-width
interval is what you get when no Monte Carlo ran. Roughly 78,500 substations
are published on that basis — 13,979 of austria's 14,720, all 25,517 of
poland's unscored population.

The guard is fixed in the engine, but that only governs future scoring. Every
record already written keeps the tier it was given. This re-derives the field
in place from the R_P5 and R_P95 already stored on each substation, so the
published data agrees with the corrected rule.

WHICH FIELD IT TRUSTS, AND WHY IT IS NOT THE PERCENTILES
---------------------------------------------------------
The obvious derivation — R_P95 minus R_P5 — is wrong, and measuring the cohort
before applying anything is what caught it. Three populations exist:

    A   CI_width 0, P5 == P95            78,638   nothing ran
    B   CI_width > 0, P5 == P95         553,632   ran, percentiles degenerate
    C   CI_width > 0, P5 < P95           87,595   coherent

Population B is france, germany, us, uk, italy and japan: 553,632 substations
whose stored R_P5 and R_P95 are identical while CI_width records a real
interval — italy 0.1938, us 0.2028. Deriving from the percentiles would have
answered None for all of them, when their own simulation says "medium".

CI_width is the field that survived correctly everywhere. On population C it
equals P95 minus P5 to within 1e-4, so trusting it costs nothing where both are
sound, and it is right on B where the percentiles are not.

So: CI_width when it is a number, percentiles only as a fallback when it is
absent.

That B exists at all is a separate defect and is not fixed here. Anything
reading per-substation R_P5/R_P95 on those six countries — a published
confidence interval, a chart error bar — is reading a zero-width range that the
data itself contradicts.

WHAT IT IS NOT
--------------
Not a rescore. No Monte Carlo runs, no R_median moves, no band changes. One
field is recomputed from a value already on the record, through the engine's
own function, so this file cannot drift from the rule it applies.

A substation whose interval is genuinely narrow keeps "high". The narrowest
interval a real 10,000-iteration simulation produced is 0.042 and every
degenerate record is exactly 0.0, so the two populations do not overlap.

Convention #79 sharding is preserved: reads and writes go through
scripts/_ssi_data_shard_reader, so the large countries stay sharded.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path.cwd()
if not (REPO / "intelligence" / "countries.json").exists():
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")
sys.path.insert(0, str(REPO))

try:
    from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data
except ImportError:
    sys.exit("ABORT: scripts/_ssi_data_shard_reader.py not importable — it is "
             "what keeps the sharded countries sharded.")
try:
    from scripts.pipeline.scoring.engine import classify_confidence
except ImportError:
    sys.exit("ABORT: cannot import classify_confidence from the engine. This "
             "tool deliberately applies the engine's own rule rather than a "
             "copy of it.")

if classify_confidence(0.5, 0.5) is not None:
    sys.exit("ABORT: the engine still answers "
             f"{classify_confidence(0.5, 0.5)!r} for a zero-width interval. "
             "Apply fix_step13_confidence_and_version.py first — otherwise "
             "this would write the same wrong values back.")


def slugs():
    cj = json.loads((REPO / "intelligence" / "countries.json").read_text())
    return sorted(c["slug"] for c in cj["countries"] if "slug" in c)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    targets = slugs() if (args.all or not args.countries) else args.countries

    print(f"confidence_tier re-derived from stored percentiles — "
          f"{'APPLY' if args.apply else 'DRY RUN'}\n")
    print(f"{'country':<14}{'subs':>9}{'changed':>10}{'high->none':>12}"
          f"{'other':>8}   most common change")
    print("-" * 76)

    grand = Counter()
    total_changed = 0
    for slug in targets:
        try:
            manifest, subs, was_sharded = load_ssi_data(slug)
        except Exception as exc:
            print(f"{slug:<14}{'—':>9}   unreadable: {type(exc).__name__}")
            continue

        moves = Counter()
        for s in subs:
            if not isinstance(s, dict):
                continue
            old = s.get("confidence_tier")
            ci = s.get("CI_width")
            if isinstance(ci, (int, float)):
                # The engine's own rule, fed the width it actually recorded.
                new = classify_confidence(0.0, ci)
            else:
                new = classify_confidence(s.get("R_P5"), s.get("R_P95"))
            if new != old:
                moves[(old, new)] += 1
                s["confidence_tier"] = new

        changed = sum(moves.values())
        total_changed += changed
        grand.update(moves)
        h2n = moves.get(("high", None), 0)
        top = max(moves.items(), key=lambda kv: kv[1])[0] if moves else None
        top_s = f"{top[0]!r} -> {top[1]!r}" if top else ""
        print(f"{slug:<14}{len(subs):>9,}{changed:>10,}{h2n:>12,}"
              f"{changed - h2n:>8,}   {top_s}")

        if args.apply and changed:
            save_ssi_data(slug, manifest, subs, force_sharded=was_sharded)

    print("-" * 76)
    print(f"{'total':<14}{'':>9}{total_changed:>10,}"
          f"{grand.get(('high', None), 0):>12,}"
          f"{total_changed - grand.get(('high', None), 0):>8,}")

    if grand:
        print("\n  every transition, cohort-wide:")
        for (old, new), n in grand.most_common():
            print(f"      {str(old):<8} -> {str(new):<8} {n:>8,}")

    if not args.apply:
        print("\n  dry run — nothing written. Add --apply once the numbers are agreed.")
        print("  This is a field re-derivation, not a rescore: no R_median moves,")
        print("  no band changes, no Monte Carlo.")
    else:
        print("\n  written. Then refresh the published figures per country the")
        print("  usual way, and note that confidence_tier is not among the six")
        print("  data-canonical fleet figures, so no page copy changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
