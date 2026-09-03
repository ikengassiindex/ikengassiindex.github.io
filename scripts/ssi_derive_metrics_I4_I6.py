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

  Both normalised Method B over THAT COUNTRY'S fleet P5/P95 (construct
  section 03; the master construct states the anchoring is within a country
  and not across the cohort), then
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
AMENDMENT = ("AMENDMENT_DRAFT_I4_I6_definition.md + "
             "AMENDMENT_DRAFT_I4_transmission_thresholds.md, pinned 30 Aug 2026")

sys.path.insert(0, str(ROOT / "scripts"))
from pipeline.scoring.engine import soft_clip                       # noqa: E402


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
    # soft_clip, NOT soft_clip_upper. Construct section 03 defines both
    # Method A and Method B as N(x) = soft_clip((x - P5)/(P95 - P5)) and
    # names this function. soft_clip_upper is the R_final overflow
    # compressor: discontinuous at 1.0, so a ratio of 1.0001 returned
    # 0.2693 and the worst substations in the fleet published as
    # mid-fleet. M-006, re-scoped 31 August 2026.
    return soft_clip((x - p5) / (p95 - p5))


def method_b_inverted(x, p5, p95):
    """N'(x) = N(P5 + P95 - x) — construct section 03."""
    if p5 is None or p95 is None or p95 <= p5:
        return None
    return method_b(p5 + p95 - x, p5, p95)


# ═══════════════════════════════════════════════════════════════════════════
#  SUB-NATIONAL FLOORS (30 August 2026)
# ───────────────────────────────────────────────────────────────────────────
#  Most countries have one transmission definition. The UK has three, because
#  it has three transmission operators under three regulatory definitions:
#
#      England & Wales   275 kV   National Grid Electricity Transmission
#      Scotland          132 kV   SSEN Transmission / SP Transmission
#      Northern Ireland  110 kV   SONI / NIE Networks
#
#  A single national floor is wrong in both directions, not merely imprecise:
#  132 counts 17,783 km of English and Welsh DISTRIBUTION as transmission,
#  while 275 drops 4,880 km of genuine Scottish and Northern Irish TRANSMISSION.
#
#  So a threshold entry may be an object carrying `jurisdictions` and a named
#  `classifier`, and the floor becomes a function of the line rather than a
#  constant. Scalar entries are untouched and behave exactly as before.
# ═══════════════════════════════════════════════════════════════════════════

_SCOT = ('aberdeen', 'angus', 'argyll', 'clackmannan', 'dumfries', 'dundee',
         'dunbarton', 'edinburgh', 'eilean', 'falkirk', 'fife', 'glasgow',
         'highland', 'inverclyde', 'lanarkshire', 'lothian', 'moray', 'orkney',
         'perth', 'renfrew', 'scottish borders', 'shetland', 'stirling',
         'kinross', 'ayrshire', 'na h-')
_NI = ('antrim', 'ards', 'armagh', 'belfast', 'causeway', 'coleraine',
       'craigavon', 'derry', 'londonderry', 'down', 'fermanagh', 'lisburn',
       'magherafelt', 'mid ulster', 'moyle', 'newry', 'newtownabbey', 'omagh',
       'strabane', 'tyrone', 'ballymena', 'ballymoney', 'banbridge',
       'carrickfergus', 'castlereagh', 'cookstown', 'dungannon', 'larne',
       'limavady', 'northern ireland')


def _uk_by_name(region):
    if not region:
        return None
    r = region.lower()
    if any(h in r for h in _NI):
        return "NI"
    if any(h in r for h in _SCOT):
        return "SCO"
    return None


def _uk_border_lat(lon):
    """The Anglo-Scottish border, as a straight line from the Solway Firth
    (-3.05, 54.99) to Berwick-upon-Tweed (-2.03, 55.79). The real border
    wanders either side of this by up to ~15 km; region names take precedence
    wherever they exist, so the line only decides cases names cannot."""
    lo = max(-3.05, min(-2.03, lon))
    return 54.99 + (lo + 3.05) * (55.79 - 54.99) / 1.02


def _uk_by_geo(lat, lon):
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None
    if lon < -5.35 and lat < 55.30:          # north-east of the island of Ireland
        return "NI"
    return "SCO" if lat >= _uk_border_lat(lon) else "EW"


def uk_jurisdiction(subs):
    """substation_id -> jurisdiction, name first and geometry as fallback.

    Cross-validated on the 6,166 substations both methods can classify:
    6,131 agree, 35 disagree (34 Scottish-named just south of the straight-line
    border, 1 name collision). Name wins, so the disagreements resolve the way
    the region says. 0 substations end unclassified."""
    out = {}
    for s in subs:
        sid = s.get("substation_id")
        if sid is None:
            continue
        j = _uk_by_name(s.get("region")) or _uk_by_geo(s.get("lat"), s.get("lon"))
        if j:
            out[str(sid)] = j
    return out


CLASSIFIERS = {"uk_jurisdiction": uk_jurisdiction}


def make_floor(spec, subs):
    """Return (floor_fn, describe). floor_fn(line) -> kV floor, or None to skip.

    A scalar spec returns a constant function, so every already-derived country
    keeps byte-identical behaviour."""
    if isinstance(spec, (int, float)):
        return (lambda ln: spec), str(spec)
    juris = {j["id"]: j["floor"] for j in spec["jurisdictions"]}
    cls = CLASSIFIERS[spec["classifier"]](subs)
    geo = _uk_by_geo if spec["classifier"] == "uk_jurisdiction" else None

    def floor_fn(ln):
        # A line belongs to the jurisdiction of an endpoint substation we know.
        for k in ("ss", "se"):
            j = cls.get(str(ln.get(k)))
            if j:
                return juris.get(j)
        # Otherwise place it by its own midpoint. 74% of UK line records reach
        # this path, which is why the geometric test was validated against
        # region names before it was trusted.
        p = ln.get("p") or []
        if not p or geo is None:
            return None
        j = geo(sum(q[1] for q in p) / len(p), sum(q[0] for q in p) / len(p))
        return juris.get(j) if j else None

    return floor_fn, " / ".join(f"{j['id']} {j['floor']}" for j in spec["jurisdictions"])


def derive(slug, subs, lines, floor, floor_label=None):
    breach = sum(1 for ln in lines
                 if isinstance(ln.get("kv"), (int, float)) and ln["kv"] > 1000)
    if lines and breach / len(lines) > UNIT_BREACH_MAX:
        raise ValueError(
            f"{breach:,} of {len(lines):,} line records carry kv > 1000 "
            f"({100*breach/len(lines):.1f}%) — the kv field is in volts, not "
            f"kilovolts. Fix the units before deriving I4.")

    line_km = collections.Counter()
    kept = 0
    unit_skipped = 0
    for ln in lines:
        kv = ln.get("kv")
        # A kv above 1000 is volts, or junk. The country-level guard above
        # catches a SYSTEMATIC failure; it cannot catch one bad record, and one
        # bad record passes any floor. Turkey exposed this: a single line tagged
        # 15400 would have contributed 1,005 phantom transmission km.
        if isinstance(kv, (int, float)) and kv > 1000:
            unit_skipped += 1
            continue
        f = floor(ln) if callable(floor) else floor
        if f is None or not isinstance(kv, (int, float)) or kv < f:
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
    # floor_label, not floor. `floor` is a closure for any country with a
    # sub-national threshold, so interpolating it wrote
    # "<function make_floor.<locals>.floor_fn at 0x7f...>" into the published
    # provenance of 136,731 records across us, uk, mexico and greenland — an
    # unreadable string carrying a heap address that differed on every run.
    # make_floor has returned a describe string since it was written; it was
    # simply never threaded to here.
    shown = floor_label if floor_label is not None else floor
    src = (f"derived per {AMENDMENT}: I4 = transmission line-km (kv >= {shown}) "
           f"within a 3x3 block of {CELL} deg cells, Method B over this "
           f"country's fleet P5/P95, "
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


def derive_from_raw(slug, subs):
    """Re-normalise the stored block sums. Reads no OSM, recomputes no geometry.

    Added 31 August 2026 with the M-006 re-scope. The block sums are already
    carried per record as _I4_raw_km and _I6_raw_count, and the defect being
    repaired is in the NORMALISER, not in the sums. Re-running the full path
    would re-read OSM and re-walk every 3x3 block to arrive at numbers the
    records already hold, and would silently absorb any drift in the OSM
    extract into a change advertised as a clip repair.

    Anchors are recomputed from the stored raws, which is exactly what
    derive() does with the sums it has just computed, so the two paths agree
    by construction.
    """
    raw4, raw6, idx, missing = [], [], [], 0
    for i, s in enumerate(subs):
        m = s.get("metrics") or {}
        v4, v6 = m.get("_I4_raw_km"), m.get("_I6_raw_count")
        if not isinstance(v4, (int, float)) or not isinstance(v6, (int, float)):
            missing += 1
            continue
        raw4.append(float(v4))
        raw6.append(float(v6))
        idx.append(i)
    if not raw4:
        raise ValueError("no record carries _I4_raw_km; run the full "
                         "derivation for this country instead")
    a4 = (percentile(sorted(raw4), 0.05), percentile(sorted(raw4), 0.95))
    a6 = (percentile(sorted(raw6), 0.05), percentile(sorted(raw6), 0.95))
    n = changed = 0
    for j, i in enumerate(idx):
        v4 = method_b_inverted(raw4[j], *a4)
        v6 = method_b_inverted(raw6[j], *a6)
        if v4 is None or v6 is None:
            continue
        m = subs[i].setdefault("metrics", {})
        if (m.get("I4") != round(v4, 4)) or (m.get("I6") != round(v6, 4)):
            changed += 1
        m["I4"] = round(v4, 4)
        m["I6"] = round(v6, 4)
        n += 1
    return n, missing, a4, a6, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--from-raw", action="store_true",
                    help="re-normalise the stored block sums; reads no OSM")
    args = ap.parse_args()

    pins, held = load_pins()
    slugs = load_slugs() if args.all else args.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  I4 / I6 — {AMENDMENT}\n")
    print(f"  {'country':<14}{'floor':>18}{'lines kept':>12}{'derived':>9}"
          f"{'skipped':>9}{'med I4':>8}{'med I6':>8}")
    for slug in sorted(slugs):
        if slug not in pins:
            why = held.get(slug, "no pinned threshold")
            print(f"  {slug:<14}REFUSED — {why}")
            continue
        try:
            man, subs, paths = load_substations(slug)
            if args.from_raw:
                floor_label = "(from stored raws)"
                n, sk, a4, a6, changed = derive_from_raw(slug, subs)
                kept = tot = 0
            else:
                lines = load_lines(slug)
                floor_fn, floor_label = make_floor(pins[slug], subs)
                n, sk, kept, tot, a4, a6, r4, r6 = derive(
                    slug, subs, lines, floor_fn, floor_label)
                changed = None
        except Exception as ex:
            print(f"  {slug:<14}ERROR — {ex}")
            continue
        got4 = sorted(s["metrics"]["I4"] for s in subs if "metrics" in s)
        got6 = sorted(s["metrics"]["I6"] for s in subs if "metrics" in s)
        m4 = got4[len(got4) // 2] if got4 else float("nan")
        m6 = got6[len(got6) // 2] if got6 else float("nan")
        print(f"  {slug:<14}{floor_label:>18}{kept:>12,}{n:>9,}{sk:>9,}"
              f"{m4:>8.3f}{m6:>8.3f}"
              + (f"{changed:>10,}" if changed is not None else ""))
        if args.verbose:
            print(f"      I4 raw km  P5 {a4[0]:.1f}  P95 {a4[1]:.1f}")
            print(f"      I6 raw cnt P5 {a6[0]:.1f}  P95 {a6[1]:.1f}")
        if not args.dry_run and n:
            man.setdefault("meta", {}).setdefault("metric_derivations", []).append({
                "metrics": ["I4", "I6"], "at_utc": datetime.now(timezone.utc).isoformat(),
                "amendment": AMENDMENT, "kv_floor": pins[slug],
                "kv_floor_label": (None if args.from_raw else floor_label),
                "lines_above_floor": kept, "lines_total": tot,
                "n_derived": n, "n_skipped": sk,
                "re_normalised_from_stored_raw": bool(args.from_raw),
                "clip": ("soft_clip — construct section 03; replaces the "
                         "soft_clip_upper overflow compressor, M-006"),
                "n_values_changed": changed,
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
