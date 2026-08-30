#!/usr/bin/env python3
"""
I4 (RTN density) and I6 (Sub density) — the first real metrics in the register.

    python3 scripts/ssi_derive_metrics_I4_I6.py france --dry-run
    python3 scripts/ssi_derive_metrics_I4_I6.py --all
    python3 scripts/ssi_derive_metrics_I4_I6.py italy --verbose

WHAT THIS BUILDS, AND WHAT IT DOES NOT
--------------------------------------
It writes a `metrics` block that has never existed in this register — the layer
between sources and components. It does NOT change components.I, and it does not
reduce the HASHED count.

I is nine metrics:

    I = 0.12·I1 + 0.09·I2 + 0.15·I3 + 0.12·I4 + 0.12·I5 + 0.12·I6
      + 0.10·I7 + 0.08·I8 + 0.10·I9

Two of nine does not compose a component, so the enrich_esg_gaps fill for
components.I stays until all nine are real. This is a foundation, not a visible
change to any published score. Saying so plainly because the opposite
impression would be the easiest thing in the world to give.

DEFINITION — pinned by the flag officer, 30 August 2026
-------------------------------------------------------
Definition A with a per-country voltage filter, per
AMENDMENT_DRAFT_I4_definition.md and
AMENDMENT_DRAFT_I4_transmission_thresholds.md.

  I4_raw  transmission line-km within a 3x3 block of 0.1 degree cells
          (~33 km across) centred on the substation's cell. A line counts
          when kv >= the country's pinned transmission floor.
  I6_raw  substations within the same 3x3 block.

  Both normalised Method B over FLEET P5/P95 (construct section 03), then
  INVERTED per the same section, because higher density means better
  resilience:

      N'(x) = N(P5 + P95 - x)

  The inversion is the part most likely to be got backwards, and getting it
  backwards would rank the fleet exactly wrong while producing entirely
  plausible numbers. test_metrics_I4_I6.py asserts the direction explicitly:
  a denser substation must end with a LOWER metric.

Nothing is fetched. Every line record in all 39 countries already carries kv
in grid-geo.json — 2.9 million records — so the Overpass re-ingestion this
definition seemed to require is unnecessary.

UNIT GUARD
----------
Turkey's kv field is in VOLTS on 27% of its records (154000, 380000, 34500) —
the same unit-confusion class as the Italy voltage=15000;400 case. A kv above
1000 is never kilovolts on a power line. The derivation refuses to run for any
country where more than 1% of line records breach that, rather than silently
counting a 20 kV distribution line as 20,000 kV transmission.

CONVENTION #56
--------------
A country with no pinned threshold is REFUSED, not defaulted. A substation
with no coordinates is skipped and counted. I6 needs no threshold and could
run alone, but is held to the same country gate so the two metrics always
describe the same population.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
PINS = ROOT / "scripts" / "i4_transmission_thresholds.json"
CELL = 0.1                      # degrees; ~11 km lat, 3x3 block ~33 km across
UNIT_BREACH_MAX = 0.01          # >1% of records with kv>1000 = units are wrong
AMENDMENT = ("AMENDMENT_DRAFT_I4_definition.md + "
             "AMENDMENT_DRAFT_I4_transmission_thresholds.md, pinned 30 Aug 2026")

sys.path.insert(0, str(ROOT / "scripts"))
from pipeline.scoring.engine import soft_clip_upper                  # noqa: E402


def load_pins():
    d = json.loads(PINS.read_text())
    return ({k: v for k, v in d.items() if not k.startswith("_")},
            d.get("_needs_pin", {}))


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
        return m, subs, None
    subs, paths = [], []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        block = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(block)
        paths.append((p, len(block), isinstance(raw, list)))
    if not subs:
        raise ValueError(f"{len(shards)} shards declared but no records read")
    return m, subs, paths


def load_lines(slug):
    g = json.loads((ROOT / slug / "grid-geo.json").read_text())
    out = list(g.get("l") or [])
    for sh in (g.get("l_shards") or []):
        p = ROOT / slug / pathlib.Path(sh["path"] if isinstance(sh, dict) else sh).name
        if p.exists():
            r = json.loads(p.read_text())
            out.extend(r if isinstance(r, list) else (r.get("l") or []))
    return out


def cell(lat, lon):
    return (int(math.floor(lat / CELL)), int(math.floor(lon / CELL)))


def seg_km(a, b):
    dy = (b[1] - a[1]) * 111.32
    dx = (b[0] - a[0]) * 111.32 * math.cos(math.radians((a[1] + b[1]) / 2))
    return math.hypot(dx, dy)


def percentile(sv, q):
    if not sv:
        return None
    i = q * (len(sv) - 1)
    lo, hi = int(i), min(int(i) + 1, len(sv) - 1)
    return sv[lo] + (sv[hi] - sv[lo]) * (i - lo)


def method_b(x, p5, p95):
    if p5 is None or p95 is None or p95 <= p5:
        return None
    return max(0.0, soft_clip_upper((x - p5) / (p95 - p5)))


def method_b_inverted(x, p5, p95):
    """N'(x) = N(P5 + P95 - x) — construct section 03."""
    if p5 is None or p95 is None or p95 <= p5:
        return None
    return method_b(p5 + p95 - x, p5, p95)


def derive(slug, subs, lines, floor):
    breach = sum(1 for ln in lines
                 if isinstance(ln.get("kv"), (int, float)) and ln["kv"] > 1000)
    if lines and breach / len(lines) > UNIT_BREACH_MAX:
        raise ValueError(
            f"{breach:,} of {len(lines):,} line records carry kv > 1000 "
            f"({100*breach/len(lines):.1f}%) — the kv field is in volts, not "
            f"kilovolts. Fix the units before deriving I4.")

    line_km = collections.Counter()
    kept = 0
    for ln in lines:
        kv = ln.get("kv")
        if not isinstance(kv, (int, float)) or kv < floor:
            continue
        kept += 1
        p = ln.get("p") or []
        for a, b in zip(p, p[1:]):
            line_km[cell((a[1] + b[1]) / 2, (a[0] + b[0]) / 2)] += seg_km(a, b)

    sub_n = collections.Counter()
    for s in subs:
        if isinstance(s.get("lat"), (int, float)) and isinstance(s.get("lon"), (int, float)):
            sub_n[cell(s["lat"], s["lon"])] += 1

    raw4, raw6, idx = [], [], []
    for i, s in enumerate(subs):
        if not (isinstance(s.get("lat"), (int, float))
                and isinstance(s.get("lon"), (int, float))):
            continue
        k = cell(s["lat"], s["lon"])
        blk = [(k[0] + a, k[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
        raw4.append(sum(line_km.get(x, 0.0) for x in blk))
        raw6.append(sum(sub_n.get(x, 0) for x in blk))
        idx.append(i)

    a4 = (percentile(sorted(raw4), 0.05), percentile(sorted(raw4), 0.95))
    a6 = (percentile(sorted(raw6), 0.05), percentile(sorted(raw6), 0.95))
    src = (f"derived per {AMENDMENT}: I4 = transmission line-km (kv >= {floor}) "
           f"within a 3x3 block of {CELL} deg cells, Method B over fleet P5/P95, "
           f"inverted per construct section 03; I6 = substations in the same "
           f"block, same normalisation. {kept:,} of {len(lines):,} lines above "
           f"the floor.")
    n = 0
    for j, i in enumerate(idx):
        v4 = method_b_inverted(raw4[j], *a4)
        v6 = method_b_inverted(raw6[j], *a6)
        if v4 is None or v6 is None:
            continue
        m = subs[i].setdefault("metrics", {})
        m["I4"] = round(v4, 4)
        m["I6"] = round(v6, 4)
        m["_I4_raw_km"] = round(raw4[j], 3)
        m["_I6_raw_count"] = raw6[j]
        subs[i]["_metrics_source"] = src
        n += 1
    return n, len(subs) - n, kept, len(lines), a4, a6, raw4, raw6


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    pins, held = load_pins()
    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  I4 / I6 — {AMENDMENT}\n")
    print(f"  {'country':<14}{'floor':>6}{'lines kept':>12}{'derived':>9}"
          f"{'skipped':>9}{'med I4':>8}{'med I6':>8}")
    for slug in sorted(slugs):
        if slug not in pins:
            why = held.get(slug, "no pinned threshold")
            print(f"  {slug:<14}REFUSED — {why}")
            continue
        try:
            man, subs, paths = load_substations(slug)
            lines = load_lines(slug)
            n, sk, kept, tot, a4, a6, r4, r6 = derive(slug, subs, lines, pins[slug])
        except Exception as ex:
            print(f"  {slug:<14}ERROR — {ex}")
            continue
        got4 = sorted(s["metrics"]["I4"] for s in subs if "metrics" in s)
        got6 = sorted(s["metrics"]["I6"] for s in subs if "metrics" in s)
        m4 = got4[len(got4) // 2] if got4 else float("nan")
        m6 = got6[len(got6) // 2] if got6 else float("nan")
        print(f"  {slug:<14}{pins[slug]:>6}{kept:>12,}{n:>9,}{sk:>9,}"
              f"{m4:>8.3f}{m6:>8.3f}")
        if args.verbose:
            print(f"      I4 raw km  P5 {a4[0]:.1f}  P95 {a4[1]:.1f}")
            print(f"      I6 raw cnt P5 {a6[0]:.1f}  P95 {a6[1]:.1f}")
        if not args.dry_run and n:
            man.setdefault("meta", {}).setdefault("metric_derivations", []).append({
                "metrics": ["I4", "I6"], "at_utc": datetime.now(timezone.utc).isoformat(),
                "amendment": AMENDMENT, "kv_floor": pins[slug],
                "lines_above_floor": kept, "lines_total": tot,
                "n_derived": n, "n_skipped": sk,
                "anchors": {"I4": list(a4), "I6": list(a6)}})
            if paths is None:
                man["substations"] = subs
                (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
            else:
                i = 0
                for p, cnt, was_list in paths:
                    blk = subs[i:i + cnt]; i += cnt
                    p.write_text(json.dumps(blk if was_list else {"substations": blk}))
                (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
    print(f"\n  {'DRY RUN — nothing written' if args.dry_run else 'APPLIED'}")
    print("  components.I is unchanged: I is nine metrics and this supplies two.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
