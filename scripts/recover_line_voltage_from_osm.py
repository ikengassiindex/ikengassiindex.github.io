#!/usr/bin/env python3
"""
Fill missing line voltages from OSM, by OSM way id, gated on geometry.

    python3 scripts/recover_line_voltage_from_osm.py mexico --osm-glob '<dir>/osm_lines_mexico_*.json' --dry-run

WHY MEXICO AND NOT THE OTHER TWO
--------------------------------
luxembourg, iceland and mexico were held from I4/I6 because more than half
their line-km carries no voltage. All three were tested against OSM; only one
is recoverable, and that is a measured result, not an assumption:

  mexico       9,794 lines missing kv; 8,696 (88.8%) are genuine OSM ways
               present in the current extract.  RECOVERABLE.
  luxembourg     797 missing; only 116 exist in OSM even including minor_line
               and cable, and NONE of those carries a voltage tag.
  iceland      1,230 missing; line ids are 1..1,427 — sequential synthetic
               integers, not OSM ids — so no id join exists at all, and OSM
               holds just 153 voltage-bearing lines for the whole country.

MEXICO'S grid-geo IS A MERGE OF TWO SOURCES
-------------------------------------------
This matters for how the join is validated. The two populations are disjoint:

  lines WITH kv     7,414 — 63% carry ids above 1.6e9, which is beyond any
                    real OSM way id, and 0% are found in OSM. Not OSM-sourced.
  lines WITHOUT kv  9,794 — 88.8% are genuine OSM ways.

So there is NO ground truth of the usual kind: no record where both the
register and OSM hold a voltage for the same way. The turkey recovery could be
validated that way; this cannot.

VALIDATED ON GEOMETRY INSTEAD
-----------------------------
An id join is an exact key, not an inference — but only if `i` really is the
OSM way id. That is testable, and was tested, by comparing the register's own
stored geometry against the OSM way's:

    8,696 id-matched lines with geometry on both sides
    start vertex  median 0.4 m   p95 0.6 m
    end vertex    median 0.4 m   p95 0.6 m
    within 50 m at BOTH ends: 8,688 of 8,696

Eight lines disagree by up to 11 km. Those are refused, not filled.

GUARDS
------
- both endpoints must agree within MATCH_M, or the record is refused
- OSM voltage is parsed as the MAXIMUM of a multi-valued tag, the same
  convention as repair_voltage_units.py, and must land on a plausible level
- a line that already carries a voltage is never overwritten
"""
from __future__ import annotations
import argparse, glob, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATCH_M = 50.0
PLAUSIBLE_MAX_KV = 1200.0


def km(a, b, c, d):
    dy = (c - a) * 111.32
    dx = (d - b) * 111.32 * math.cos(math.radians((a + c) / 2))
    return math.hypot(dx, dy)


def parse_kv(raw):
    vals = [int(v) for v in str(raw).replace(",", ";").split(";") if v.strip().isdigit()]
    if not vals:
        return None
    v = max(vals) / 1000.0
    return round(v, 3) if 0 < v <= PLAUSIBLE_MAX_KV else None


def load_osm(pattern):
    volts, geoms = {}, {}
    for p in sorted(glob.glob(pattern)):
        try:
            els = json.loads(pathlib.Path(p).read_text())["elements"]
        except Exception:
            continue
        for x in els:
            i = int(x["id"])
            t = x.get("tags") or {}
            if t.get("voltage"):
                volts[i] = t["voltage"]
            if x.get("geometry"):
                geoms[i] = x["geometry"]
    return volts, geoms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--osm-glob", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    volts, geoms = load_osm(a.osm_glob)
    gp = ROOT / a.slug / "grid-geo.json"
    g = json.loads(gp.read_text())
    lines = g.get("l") or []

    filled = refused_geom = refused_kv = already = no_match = 0
    for ln in lines:
        v = ln.get("kv")
        if isinstance(v, (int, float)) and v > 0:
            already += 1
            continue
        try:
            i = int(str(ln.get("i")))
        except Exception:
            no_match += 1
            continue
        if i not in volts:
            no_match += 1
            continue
        pts = ln.get("p") or []
        gg = geoms.get(i)
        if not pts or not gg:
            refused_geom += 1
            continue
        d0 = km(pts[0][1], pts[0][0], gg[0]["lat"], gg[0]["lon"]) * 1000
        d1 = km(pts[-1][1], pts[-1][0], gg[-1]["lat"], gg[-1]["lon"]) * 1000
        if d0 > MATCH_M or d1 > MATCH_M:
            refused_geom += 1
            continue
        kvv = parse_kv(volts[i])
        if kvv is None:
            refused_kv += 1
            continue
        if not a.dry_run:
            ln["kv"] = kvv
        filled += 1

    print(f"\n  {a.slug} — {len(lines):,} line records")
    for k, n in (("already had a voltage", already), ("FILLED from OSM", filled),
                 ("refused, geometry disagrees", refused_geom),
                 ("refused, implausible voltage", refused_kv),
                 ("no OSM way with a voltage", no_match)):
        print(f"      {k:32}{n:>8,}")
    assert already + filled + refused_geom + refused_kv + no_match == len(lines)

    if not a.dry_run and filled:
        gp.write_text(json.dumps(g))
        print(f"      written\n")
    else:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
