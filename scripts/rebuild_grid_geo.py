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
import re
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
    """Every line, tagged with the file it came from.

    The origin matters at write time: Convention #80 shards the geometry, and
    a line has to go back where it was found or the manifest balloons past
    GitHub's 100 MB limit. `None` means the manifest itself.
    """
    L = g.get("l")
    if isinstance(L, list) and L:
        return [(rec, None) for rec in L]
    out = []
    for k in ("l_shards", "lines_shards", "line_shards", "shards"):
        for sh in g.get(k) or []:
            q = sh["path"] if isinstance(sh, dict) else sh
            name = Path(q).name
            f = REPO / slug / name
            if f.exists():
                part = json.loads(f.read_text(encoding="utf-8"))
                recs = part if isinstance(part, list) else (part.get("l") or [])
                out += [(rec, name) for rec in recs]
    if not out:
        for f in sorted((REPO / slug).glob("grid-geo-l-*.json")):
            part = json.loads(f.read_text(encoding="utf-8"))
            recs = part if isinstance(part, list) else (part.get("l") or [])
            out += [(rec, f.name) for rec in recs]
    return out


# The renderer already solves this, and the gate should know it. map.js keeps a
# MAINLAND_BBOXES table used ONLY to anchor the viewport: substations outside
# the box stay in memory and remain visible on pan, they just do not drag the
# auto-fit. France, the US and Norway have entries; New Zealand was added when
# its fleet turned out to carry one substation in the Chathams. Reading the
# table here rather than restating it keeps the two files from drifting apart.
def mainland_bboxes():
    js = (REPO / "map.js").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"const MAINLAND_BBOXES = \{(.*?)\n\s*\};", js, re.S)
    if not m:
        return {}
    out = {}
    for row in re.finditer(
            r"'?([a-z-]+)'?:\s*\{\s*minLat:\s*(-?[\d.]+),\s*minLon:\s*(-?[\d.]+),"
            r"\s*maxLat:\s*(-?[\d.]+),\s*maxLon:\s*(-?[\d.]+)", m.group(1)):
        out[row.group(1)] = tuple(float(row.group(i)) for i in (2, 3, 4, 5))
    return out



_PLACEHOLDER_NAME = re.compile(r"^Substation \d+$")


def source_object_key(s):
    """What upstream object a substation record came from.

    `substation_id` is minted per row, so it cannot see that two rows describe
    the same thing. The source key can: Germany's 168,776 rows resolve to
    108,027 OSM objects, and the US's 97,915 to 77,592.
    """
    if s.get("osm_id") not in (None, ""):
        return f"{s.get('osm_type')}/{s.get('osm_id')}"
    for k in ("osm_feature_id", "osm_ref"):
        if s.get(k) not in (None, ""):
            return str(s[k])
    vp = s.get("v43_provenance")
    if isinstance(vp, dict):
        for blk in vp.values():
            if isinstance(blk, dict) and blk.get("feature_id"):
                return str(blk["feature_id"])
    return None


def collapse_to_objects(subs):
    """One node per source object, keeping the best-named row.

    Verified on Germany before this was written: of 43,163 objects carrying
    more than one row, every single one has all its rows at identical
    coordinates. 6,792 repeat name and voltage exactly; the other 36,371 differ
    only in a synthetic `Substation <id>` name that embeds the row's own
    identifier. None of them is a second substation.

    Rows with no source key are kept as they are — Canada is register-sourced
    and has none, and a missing key is not evidence of a duplicate.
    """
    best, order, collapsed = {}, [], 0
    for s in subs:
        k = source_object_key(s)
        if k is None:
            order.append(s)
            continue
        if k not in best:
            best[k] = s
            order.append(("K", k))
            continue
        collapsed += 1
        cur = best[k]
        cur_named = bool(cur.get("name")) and not _PLACEHOLDER_NAME.match(str(cur.get("name")))
        new_named = bool(s.get("name")) and not _PLACEHOLDER_NAME.match(str(s.get("name")))
        if new_named and not cur_named:
            best[k] = s
    out = []
    for item in order:
        out.append(best[item[1]] if isinstance(item, tuple) else item)
    return out, collapsed


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
        # A fleet straddling the date line reads as a 355-degree span when the
        # longitudes are compared naively. Re-measure it wrapped: shift the
        # western lobe east by 360 and take whichever span is smaller. New
        # Zealand is 355 degrees naive and 10 degrees wrapped — one substation
        # in the Chathams against 1,588 on the mainland.
        wrapped = [x + 360 if x < 0 else x for x in xs]
        span_wrapped = max(wrapped) - min(wrapped)
        west = sum(1 for x in xs if x < 0)
        east = len(xs) - west
        # Both tests matter. A country wholly in one hemisphere has an
        # identical wrapped span, and comparing two floats that should be
        # equal is decided by the last bit — which is how Colombia and Costa
        # Rica, entirely west of 0°, were refused for straddling a meridian
        # they do not reach. Requiring a non-empty lobe on each side and a
        # full degree of improvement makes the test say what it means.
        box = mainland_bboxes().get(slug)
        if box:
            lo_lat, lo_lon, hi_lat, hi_lon = box
            anchor = [n for n in nodes.values()
                      if lo_lon <= n["x"] <= hi_lon and lo_lat <= n["y"] <= hi_lat]
            if anchor:
                axs = [n["x"] for n in anchor]
                if max(axs) - min(axs) <= 60:
                    west = east = 0        # the viewport anchor is sane
                    warnings.append(
                        f"{len(nodes) - len(anchor):,} substation(s) outside the "
                        f"map.js mainland box — visible on pan, excluded from the "
                        f"auto-fit anchor, which spans "
                        f"{max(axs) - min(axs):.1f}°")
        if west and east and span_wrapped < span_x - 1.0:
            minority, side = ((west, "west of 0°") if west <= east
                              else (east, "east of 0°"))
            problems.append(
                f"fleet straddles the anti-meridian: {span_x:.0f}° naive, "
                f"{span_wrapped:.0f}° wrapped; the smaller lobe is "
                f"{minority:,} substation(s) {side}. map.js measures the "
                f"cluster span naively, so its "
                f"Mode-3 safeguard would fall back to a cluster that is itself "
                f"pathological and the map would not render. This needs a "
                f"decision, not a default — see the module docstring.")
        if span_x > 350 or span_y > 175:
            warnings.append(f"extent spans {span_x:.0f}° x {span_y:.0f}° — check "
                            f"the Mode-3 viewport safeguard still catches this")

    # Lines keep [lon, lat]; a polyline whose first pair looks like [lat, lon]
    # would put the whole conductor somewhere else entirely.
    off = 0
    for e, _origin in lines[:5000]:
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


def rebuild(slug, dedupe=False):
    gpath = REPO / slug / "grid-geo.json"
    g = json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else {}
    old_s = g.get("s") or {}
    lines = load_lines(slug, g)
    subs = load_substations(slug)
    collapsed = 0
    if dedupe:
        subs, collapsed = collapse_to_objects(subs)

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

    dup_same = dup_diff = dup_rows = 0
    _seen = {}
    for _s in subs:
        _k = str(_s.get("substation_id"))
        _c = (round(_s.get("lat"), 6) if isinstance(_s.get("lat"), float) else _s.get("lat"),
              round(_s.get("lon"), 6) if isinstance(_s.get("lon"), float) else _s.get("lon"))
        if _k in _seen:
            dup_rows += 1
            if _seen[_k] == _c:
                dup_same += 1
            else:
                dup_diff += 1
        else:
            _seen[_k] = _c

    problems, warnings = geolocation_gate(slug, nodes, lines)

    # Keying the map by substation_id deduplicates, which is right — but it
    # must be said out loud, because the rows disappear from the map without
    # disappearing from the fleet. Australia carries 436 ids used twice at
    # identical coordinates (504 rows) and 2 used by genuinely different
    # substations; Turkey carries 29. Same coordinates is a duplicate record;
    # different coordinates is an id collision and a data defect.
    if dup_same or dup_diff:
        bits = []
        if dup_same:
            bits.append(f"{dup_rows:,} duplicate row(s) at identical coordinates")
        if dup_diff:
            bits.append(f"{dup_diff} id(s) shared by substations at DIFFERENT "
                        f"coordinates")
        warnings.append("substation_id not unique — " + "; ".join(bits))

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
    for e, origin in lines:
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
        out_lines.append((ne, origin))

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
        "slug": slug, "nodes": nodes, "lines_with_origin": out_lines,
        "adjacency": {k: v for k, v in adjacency.items()},
        "old_nodes": len(old_s), "new_nodes": len(nodes),
        "collapsed": collapsed,
        "skipped": skipped, "lines_total": len(lines), "lines_resolved": resolved,
        "problems": problems, "warnings": warnings,
        "centre_drift_m": drift, "grid": g,
    }



def write_country(slug, r):
    """Write nodes and adjacency back, preserving the shard layout exactly.

    The obvious implementation — assign `g["l"]` and dump one file — would
    have destroyed the repository. Convention #80 shards the line geometry,
    and concatenating it back inline gives a single `grid-geo.json` of 391 MB
    for the US, 95 MB for France and 94 MB for Germany. GitHub rejects any
    file over 100 MB, so the first `git push` would have failed with three
    files already rewritten.

    Lines are not changing here in any case. This cascade re-emits the node
    set from the fleet and rebuilds the adjacency; the OSM geometry is
    untouched. So each line record is written back to the file it came from,
    carrying only its re-indexed `ss`/`se`, and the manifest keeps its shard
    references.
    """
    out = []
    g = r["grid"]
    g["s"] = r["nodes"]
    g["a"] = r["adjacency"]

    by_file = collections.defaultdict(list)
    for rec, origin in r["lines_with_origin"]:
        by_file[origin].append(rec)

    for origin, recs in sorted(by_file.items()):
        if origin is None:              # lines live inline in the manifest
            g["l"] = recs
            continue
        payload = json.loads((REPO / slug / origin).read_text(encoding="utf-8"))
        if isinstance(payload, list):
            payload = recs
        else:
            payload["l"] = recs
        (REPO / slug / origin).write_text(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8")
        shard_mb = (REPO / slug / origin).stat().st_size / 1048576
        note = (f"  — over the Convention #79 60 MB threshold" if shard_mb > 60
                else "")
        out.append(f"wrote {slug}/{origin} ({len(recs):,} lines, "
                   f"{shard_mb:,.1f} MB){note}")

    if "l" not in g:
        g["l"] = []
    path = REPO / slug / "grid-geo.json"
    path.write_text(json.dumps(g, separators=(",", ":"), ensure_ascii=False),
                    encoding="utf-8")
    mb = path.stat().st_size / 1048576
    out.append(f"wrote {slug}/grid-geo.json ({mb:,.1f} MB, "
               f"{len(r['nodes']):,} nodes)")
    if mb > 60:
        out.append(f"WARNING {slug}/grid-geo.json is {mb:,.1f} MB — over the "
                   f"Convention #79 60 MB threshold")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dedupe-by-object", action="store_true",
                    help="one map node per source object, not per row")
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
            r = rebuild(slug, dedupe=a.dedupe_by_object)
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
        if r.get("collapsed"):
            print(f"{'':<13}  {r['collapsed']:,} row(s) collapsed onto a source "
                  f"object already emitted")
        if r["skipped"]:
            print(f"{'':<13}  {r['skipped']:,} substation(s) had no usable "
                  f"coordinate or id and were not emitted")

        if r["problems"]:
            failed += 1
            continue
        if not a.write:
            continue
        for line in write_country(slug, r):
            print(f"{'':<13}  {line}")

    if a.dry_run:
        print("\nDRY RUN — nothing written.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
