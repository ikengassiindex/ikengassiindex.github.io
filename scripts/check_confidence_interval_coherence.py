#!/usr/bin/env python3
"""
The published confidence interval must be a confidence interval.

    python3 scripts/check_confidence_interval_coherence.py --all
    python3 scripts/check_confidence_interval_coherence.py --all --strict
    python3 scripts/check_confidence_interval_coherence.py france --verbose
    python3 scripts/check_confidence_interval_coherence.py --all --update-baseline

WHAT THIS GATES
---------------
Every country page publishes four uncertainty fields per substation: R_P5,
R_P95, CI_width and confidence_tier. On 29 August 2026 none of them carried a
Monte Carlo result on the majority of the cohort:

  * R_P5 and R_P95 had both been overwritten with `add_sum`, the additive
    R6c flood modifier -- 534,443 records, 85.9% of the cohort, 100% of
    france, germany, us, italy and japan.
  * CI_width is written by enrich_esg_gaps.py:405 as vary(0.22, name, 0.15),
    a deterministic hash of the substation's NAME. It reproduces the published
    width bit-for-bit for 100.00% of records in five countries.
  * confidence_tier is written as the literal 'medium' at
    enrich_esg_gaps.py:414 -- 81.2% of the cohort reads it.

The ESG page consequently renders, for France 1000000000:

    Confidence Interval
    0.143 - 0.143
    P5-P95 . CI width 0.233 . medium confidence

against an R_median of 0.612: a zero-width interval, a contradicting width,
and both endpoints below the median they should bracket.

SIX CHECKS
----------
  ORDER      not (R_P5 <= R_median <= R_P95)
  DEGENERATE R_P5 == R_P95 -- an interval with no width
  IMPOSTOR   R_P5 == add_sum -- the specific corruption, named so a future
             reader does not have to rediscover the mechanism
  WIDTH      CI_width disagrees with R_P95 - R_P5
  SYNTHETIC  CI_width reproduces vary(0.22, name, 0.15) exactly
  TIER       confidence_tier disagrees with classify_confidence(R_P5, R_P95)

WHY THERE IS A BASELINE
-----------------------
534,443 records fail today. A gate that fails everywhere on the day it is
written is a gate everyone learns to scroll past, and it would mask the next
regression inside noise it can never clear. So the known population is recorded
per country in the baseline file, and --strict fails only when a count EXCEEDS
its baseline.

This hides nothing: every run prints the live count, the baseline and the
delta, so the debt stays in view. --update-baseline re-records after a
deliberate repair, and lowering a baseline is the measure of progress.

Convention #56: a country whose data cannot be read is reported as unreadable
and fails --strict. It is never silently skipped.

Task #520: manifests may be sharded. Reading data['substations'] on a sharded
manifest silently yields nothing, which would make this gate report a clean
cohort it never looked at. load_substations() refuses that.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "confidence_interval_baseline.json"
CHECKS = ("ORDER", "DEGENERATE", "IMPOSTOR", "WIDTH", "SYNTHETIC", "TIER")
EPS = 1e-9
WIDTH_TOL = 5e-4          # both operands are stored rounded to 4dp

try:
    sys.path.insert(0, str(ROOT / "scripts"))
    from enrich_esg_gaps import vary as _vary
except Exception:                                   # pragma: no cover
    _vary = None                                    # Convention #56: say so


def load_slugs():
    p = ROOT / "intelligence" / "countries.json"
    d = json.loads(p.read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_substations(slug):
    """Shard-aware. Raises rather than returning an empty list (Task #520)."""
    man = ROOT / slug / "ssi-data.json"
    m = json.loads(man.read_text())
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


def classify_confidence(p5, p95):
    """Mirrors engine.classify_confidence, including its None returns."""
    if p5 is None or p95 is None:
        return None
    ci = p95 - p5
    if ci <= EPS:
        return None
    if ci <= 0.10:
        return "high"
    if ci <= 0.25:
        return "medium"
    return "low"


def audit(subs):
    c = {k: 0 for k in CHECKS}
    examples = {}
    for s in subs:
        p5, p95 = s.get("R_P5"), s.get("R_P95")
        med, w = s.get("R_median"), s.get("CI_width")
        add, name = s.get("add_sum"), s.get("name")

        def hit(k):
            c[k] += 1
            examples.setdefault(k, s)

        if None not in (p5, p95, med) and not (p5 <= med <= p95):
            hit("ORDER")
        if None not in (p5, p95) and abs(p95 - p5) <= EPS:
            hit("DEGENERATE")
        if None not in (p5, add) and abs(p5 - add) <= EPS:
            hit("IMPOSTOR")
        if None not in (p5, p95, w) and abs(w - (p95 - p5)) > WIDTH_TOL:
            hit("WIDTH")
        if _vary is not None and w is not None and name is not None:
            # A hash-match alone is not proof of fabrication. After the uk /
            # canada / turkey rescore, two turkey records had a genuine Monte
            # Carlo width that happened to land on vary(0.22, name, 0.15) to
            # four decimals -- 2 collisions in 4,031 records, which is what a
            # 4dp value in a narrow band will do. Their endpoints agreed with
            # the width exactly, so the interval was real.
            #
            # What identified the fabricated population was that its width was
            # ORPHANED: CI_width said 0.233 while R_P5 and R_P95 were equal.
            # Requiring both conditions keeps every one of the original
            # 430,191 and drops the coincidences.
            orphaned = (p5 is None or p95 is None
                        or abs(w - (p95 - p5)) > WIDTH_TOL)
            if abs(_vary(0.22, name, 0.15) - w) <= EPS and orphaned:
                hit("SYNTHETIC")
        if s.get("confidence_tier") != classify_confidence(p5, p95):
            hit("TIER")
    return c, examples


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
    live, unreadable, total = {}, [], 0

    if _vary is None:
        print("  NOTE: enrich_esg_gaps.vary is not importable -- the SYNTHETIC\n"
              "        check is not running. It is reported as 0, which is not\n"
              "        the same as a clean result.\n")

    for slug in sorted(slugs):
        try:
            subs = load_substations(slug)
        except Exception as ex:
            unreadable.append((slug, str(ex)))
            continue
        total += len(subs)
        c, ex = audit(subs)
        live[slug] = c
        if args.verbose and any(c.values()):
            print(f"\n  {slug} ({len(subs):,} substations)")
            for k in CHECKS:
                if c[k]:
                    print(f"    {k:<11}{c[k]:>9,}")
            s = ex.get("IMPOSTOR") or ex.get("DEGENERATE") or ex.get("ORDER")
            if s:
                print(f"    e.g. {s.get('substation_id')}: "
                      f"R_P5={s.get('R_P5')} R_P95={s.get('R_P95')} "
                      f"R_median={s.get('R_median')} add_sum={s.get('add_sum')} "
                      f"CI_width={s.get('CI_width')}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(live, indent=1, sort_keys=True) + "\n")
        print(f"\n  baseline written: {BASELINE.relative_to(ROOT)}"
              f"  ({len(live)} countries)")
        return 0

    print(f"\n  Confidence-interval coherence -- {len(live)} countries, "
          f"{total:,} substations\n")
    print(f"    {'check':<12}{'live':>12}{'baseline':>12}{'delta':>10}")
    regressions = []
    for k in CHECKS:
        lv = sum(c[k] for c in live.values())
        bl = sum(base.get(s, {}).get(k, 0) for s in live)
        d = lv - bl
        flag = "  <-- REGRESSION" if d > 0 else ""
        if d > 0:
            regressions.append((k, d))
        print(f"    {k:<12}{lv:>12,}{bl:>12,}{d:>+10,}{flag}")

    worse = [(s, k, live[s][k] - base.get(s, {}).get(k, 0))
             for s in live for k in CHECKS
             if live[s][k] > base.get(s, {}).get(k, 0)]
    if worse:
        print("\n    countries above baseline:")
        for s, k, d in sorted(worse, key=lambda t: -t[2])[:20]:
            print(f"      {s:<16}{k:<12}{d:+,}")

    if unreadable:
        print("\n    UNREADABLE (Convention #56 -- not counted as clean):")
        for s, why in unreadable:
            print(f"      {s:<16}{why}")

    if not base:
        print("\n  No baseline recorded yet. Run --update-baseline to record the\n"
              "  known population, after which --strict fails on any increase.")

    if args.strict:
        if unreadable:
            print("\nSTRICT: countries unreadable.")
            return 1
        if regressions:
            print("\nSTRICT: coherence regressed against baseline.")
            return 1
        print("\nSTRICT: no coherence regression against baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
