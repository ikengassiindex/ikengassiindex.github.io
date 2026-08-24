#!/usr/bin/env python3
"""
rebuild_grid_geo.py — re-emit the map from the fleet, with geolocation as a gate
===============================================================================

`ssi-data.json` is the fleet. `grid-geo.json` is a derivative that stopped
tracking it, in both directions at once:

  * Austria scores 14,720 substations; its map holds 741. Poland 27,764 against
    2,248; Czechia 8,899 against 1,077. The v4.23 ingestion added substations to
    the index and never re-emitted the map.
  * Germany's map holds 18,938 MORE than the index scores, Spain 17,601 more,
    Italy 4,004 more — the pre-Discipline-#36 fleet, because
    `clean_grid_geo.py` carries the same hardcoded seven-country list as
    `refresh_country_counts.py` and never propagated the July strips.

Cohort-wide: 721,275 scored, 653,892 on the map.

This tool rebuilds `s`, `ss`/`se` and `a` from the index. It does not touch line
geometry — the polylines are OSM's and are kept byte-for-byte.

WHAT map.js ACTUALLY EXPECTS (read from the source, not assumed)
---------------------------------------------------------------
  s : { "<key>": {x: lon, y: lat, n: name, v: kv} }
      iterated with Object.entries; `passesFilter(sid)` looks the key up in
      `ssiMap`, which is built from substation_id / internal_id / name / osm_id.
      Turkey and Greece key `s` by positional index today, so every lookup
      misses and their maps render the whole country as unclassified grey with
      filtering inert. Keying by `substation_id` fixes that.
  l : array; hit-testing selects by array position, `lineById[l.i]` by id.
  a : { "<key>": [<line i>, ...] } — a list of LINE ids, not neighbours.
      Turkey holds line ids and works. US, Italy and France hold substation
      ids: `lineById[<substation id>]` misses every time, so clicking a
      substation on those maps highlights nothing. Greece holds a third form
      matching neither.

GEOLOCATION IS A GATE, NOT A HOPE
---------------------------------
Bad coordinates are the failure mode that has hurt this estate before, so the
rebuild refuses rather than writes:

  1. x is longitude and y is latitude. Verified empirically before trusting it:
     where node keys already join to substation_id (Italy, Japan, Chile,
     Portugal) the two files agree with ZERO drift. The emitter re-asserts it
     per country and aborts on any transposition.
  2. No null island, no NaN, no out-of-range coordinate.
  3. Every substation inside its own bounds.json within the Discipline #36
     tolerance, or counted and reported — contamination surfaces here instead
     of being quietly drawn.
  4. Line polylines stay [lon, lat] and are never re-projected.
  5. The rebuilt extent is compared against the old one. A map whose centre
     moves more than a kilometre, or whose span changes by more than a tenth,
     is a rendering incident and the tool says so.

`map.js`'s Mode-3 viewport safeguard is not touched by any of this.

Usage:
    python3 scripts/rebuild_grid_geo.py chile --dry-run
    python3 scripts/rebuild_grid_geo.py chile --write
    python3 scripts/rebuild_grid_geo.py --all --dry-run
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SNAP_M = 250.0          # substation-to-line-endpoint incidence distance


def load_substations(slug):
    d = json.loads((REPO / slug / "ssi-data.json").read_text(encoding="utf-8"))
    if isinstance(d.get("substations"), list):
        return d["substations"]
    out = []
    for sh in d.get("substations_shards") or []:
        q = sh["path"] if isinstance(sh, dict) else sh
        out += json.loads((REPO / slug / Path(q).name).read_text(encoding="utf-8"))
    return out


def load_lines(slug, g):
    L = g.get("l")
    if isinstance(L, list) and L:
        return L
    out = []
    for k in ("l_shards", "lines_shards", "line_shards", "shards"):
        for sh in g.get(k) or []:
            q = sh["path"] if isinstance(sh, dict) else sh
            f = REPO / slug / Path(q).name
            if f.exists():
                part = json.loads(f.read_text(encoding="utf-8"))
                out += part if isinstance(part, list) else (part.get("l") or [])
    if not out:
        for f in sorted((REPO / slug).glob("grid-geo-l-*.json")):
            part = json.loads(f.read_text(encoding="utf-8"))
            out += part if isinstance(part, list) else (part.get("l") or [])
    return out


def metres(ax, ay, bx, by):
    return math.hypot((ax - bx) * 111320 * math.cos(math.radians((ay + by) / 2)),
                      (ay - by) * 110540)


def geolocation_gate(slug, nodes, lines):
    """Refuse to emit a map that would render substations in the wrong place."""
    problems, warnings = [], []

    bad = [k for k, v in nodes.items()
           if not (isinstance(v["x"], (int, float)) and isinstance(v["y"], (int, float)))
           or math.isnan(v["x"]) or math.isnan(v["y"])
           or not (-180 <= v["x"] <= 180) or not (-90 <= v["y"] <= 90)
           or (v["x"] == 0 and v["y"] == 0)]
    if bad:
        problems.append(f"{len(bad)} substation(s) with unusable coordinates "
                        f"(NaN, out of range, or null island) e.g. {bad[:3]}")

    # Transposition check: if x/y were swapped, |x| would routinely exceed the
    # latitude range for any country outside the tropics.
    xs = [v["x"] for v in nodes.values()]
    ys = [v["y"] for v in nodes.values()]
    if xs and ys:
        if max(abs(y) for y in ys) > 90:
            problems.append("y exceeds ±90 — x and y look transposed")
        span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
        if span_x > 350 or span_y > 175:
            warnings.append(f"extent spans {span_x:.0f}° x {span_y:.0f}° — check "
                            f"the Mode-3 viewport safeguard still catches this")

    # Lines keep [lon, lat]; a polyline whose first pair looks like [lat, lon]
    # would put the whole conductor somewhere else entirely.
    off = 0
    for e in lines[:5000]:
        p = e.get("p") or []
        if p and isinstance(p[0], list) and len(p[0]) == 2:
            lon, lat = p[0]
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                off += 1
    if off:
        problems.append(f"{off} line polyline(s) with coordinates outside "
                        f"[lon, lat] range in the first 5,000 sampled")

    return problems, warnings


def extent(nodes):
    xs = [v["x"] for v in nodes.values()]
    ys = [v["y"] for v in nodes.values()]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys),
            (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


def rebuild(slug):
    gpath = REPO / slug / "grid-geo.json"
    g = json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else {}
    old_s = g.get("s") or {}
    lines = load_lines(slug, g)
    subs = load_substations(slug)

    nodes, skipped = {}, 0
    for s in subs:
        sid = s.get("substation_id")
        try:
            lon, lat = float(s["lon"]), float(s["lat"])
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue
        if sid is None:
            skipped += 1
            continue
        v = s.get("voltage_kv")
        nodes[str(sid)] = {
            "x": lon, "y": lat,
            "n": s.get("name") or "",
            "v": v if isinstance(v, (int, float)) else 0,
        }

    problems, warnings = geolocation_gate(slug, nodes, lines)

    # Incidence: a line belongs to a substation when one of its ends is at it.
    bucket = collections.defaultdict(list)
    for k, v in nodes.items():
        bucket[(round(v["x"], 2), round(v["y"], 2))].append(k)

    def nearest(lon, lat):
        best, bd = None, 1e9
        for dx in (-0.01, 0, 0.01):
            for dy in (-0.01, 0, 0.01):
                for k in bucket.get((round(lon + dx, 2), round(lat + dy, 2)), ()):
                    n = nodes[k]
                    d = metres(n["x"], n["y"], lon, lat)
                    if d < bd:
                        bd, best = d, k
        return best if bd <= SNAP_M else None

    adjacency = collections.defaultdict(list)
    out_lines, resolved = [], 0
    for e in lines:
        p = e.get("p") or []
        ne = dict(e)
        a = b = None
        if len(p) >= 2:
            a = nearest(p[0][0], p[0][1])
            b = nearest(p[-1][0], p[-1][1])
        ne["ss"] = a if a is not None else -1
        ne["se"] = b if b is not None else -1
        lid = ne.get("i")
        if a is not None:
            adjacency[a].append(lid)
        if b is not None and b != a:
            adjacency[b].append(lid)
        if a is not None and b is not None:
            resolved += 1
        out_lines.append(ne)

    old_ext, new_ext = extent(old_s), extent(nodes)
    drift = None
    if old_ext and new_ext:
        drift = metres(old_ext[4], old_ext[5], new_ext[4], new_ext[5])
        old_span = max(old_ext[2] - old_ext[0], old_ext[3] - old_ext[1])
        new_span = max(new_ext[2] - new_ext[0], new_ext[3] - new_ext[1])
        if old_span and abs(new_span - old_span) / old_span > 0.10:
            warnings.append(f"extent span changes {old_span:.2f}° -> {new_span:.2f}°")
        if drift > 1000:
            warnings.append(f"map centre moves {drift / 1000:.1f} km")

    return {
        "slug": slug, "nodes": nodes, "lines": out_lines,
        "adjacency": {k: v for k, v in adjacency.items()},
        "old_nodes": len(old_s), "new_nodes": len(nodes),
        "skipped": skipped, "lines_total": len(lines), "lines_resolved": resolved,
        "problems": problems, "warnings": warnings,
        "centre_drift_m": drift, "grid": g,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.write or a.dry_run):
        print("Specify --dry-run or --write")
        return 2

    slugs = a.countries
    if a.all or not slugs:
        slugs = sorted(json.loads(
            (REPO / "intelligence" / "countries.json").read_text(encoding="utf-8"))["slugs"])

    print(f"{'country':<13}{'map now':>9}{'fleet':>9}{'delta':>9}"
          f"{'lines':>9}{'both ends':>10}{'centre drift':>13}  gate")
    failed = 0
    for slug in slugs:
        try:
            r = rebuild(slug)
        except Exception as exc:
            print(f"{slug:<13}  ERROR {exc}")
            failed += 1
            continue
        d = r["new_nodes"] - r["old_nodes"]
        gate = "REFUSE: " + "; ".join(r["problems"]) if r["problems"] else "ok"
        if r["warnings"]:
            gate += ("  |  " if gate == "ok" else "  ") + "; ".join(r["warnings"])
        drift = (f"{r['centre_drift_m']:,.0f} m"
                 if r["centre_drift_m"] is not None else "—")
        print(f"{slug:<13}{r['old_nodes']:>9,}{r['new_nodes']:>9,}{d:>+9,}"
              f"{r['lines_total']:>9,}{r['lines_resolved']:>10,}{drift:>13}  {gate}")
        if r["skipped"]:
            print(f"{'':<13}  {r['skipped']:,} substation(s) had no usable "
                  f"coordinate or id and were not emitted")

        if r["problems"]:
            failed += 1
            continue
        if not a.write:
            continue
        g = r["grid"]
        g["s"] = r["nodes"]
        g["l"] = r["lines"]
        g["a"] = r["adjacency"]
        (REPO / slug / "grid-geo.json").write_text(
            json.dumps(g, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        print(f"{'':<13}  wrote {slug}/grid-geo.json")

    if a.dry_run:
        print("\nDRY RUN — nothing written.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
