#!/usr/bin/env python3
"""
scripts/check_line_geometry.py — Discipline #28

Power-line geometry richness gate. Catches the LT/JP/TR/US/IE-class
defect where grid-geo.json stores power lines as simple A→B straight
chords (exactly 2 vertices per line) instead of OSM-way-routed
multi-vertex paths.

The defect class:
  - LT had 693 lines, all with exactly 2 vertices, 0 multi-vertex
  - JP had 11,628 lines, all with exactly 2 vertices, 0 multi-vertex
  - TR had 8,061 lines, all with exactly 2 vertices, 0 multi-vertex
  - US had 68,400 lines, all with exactly 2 vertices, 0 multi-vertex
  - IE had 2,306 lines, only 48 multi-vertex (2% — barely better than chord)

Benchmarks (countries with proper OSM-way ingestion):
  - France:   13.5 avg pts/line, 68% multi-vertex
  - Italy:    3.4 avg pts/line, 78% multi-vertex
  - Estonia: 17.0 avg pts/line, 73% multi-vertex
  - Iceland: 38.9 avg pts/line, 96% multi-vertex

Thresholds:
  - FAIL: avg < 2.5 vertices/line (essentially chord-only rendering)
  - WARN: 2.5 <= avg < 4    (some routing but mostly chords)
  - PASS: avg >= 4

This is intentionally permissive on the boundary case (IT at 3.4 is
WARN, not FAIL) because IT does have 78% multi-vertex lines — the
low avg is a function of the OSM data structure (line broken into
many short ways), not a chord-only defect.

Usage:
    python3 scripts/check_line_geometry.py <slug>
    python3 scripts/check_line_geometry.py --all
    python3 scripts/check_line_geometry.py --all --strict   # exit 1 on FAIL

Exit codes:
    0 = PASS or only WARN
    1 = FAIL (chord-only rendering)
"""
import json, os, sys, glob


def check_country(slug, repo_root="."):
    path = os.path.join(repo_root, slug, "grid-geo.json")
    if not os.path.exists(path):
        return {"slug": slug, "status": "EXEMPT", "reason": "no grid-geo.json"}
    try:
        g = json.load(open(path))
    except Exception as e:
        return {"slug": slug, "status": "ERROR", "reason": str(e)[:80]}

    lines = g.get("l") or g.get("lines") or []
    if not lines:
        return {"slug": slug, "status": "EXEMPT", "reason": "no lines"}

    total_pts = 0
    n_geom = 0
    multi = 0
    max_pts = 0
    for ln in lines:
        if not isinstance(ln, dict): continue
        pts = ln.get("p") or ln.get("g") or ln.get("geometry") or ln.get("coords")
        if not pts: continue
        # Handle nested (multilinestring) by flattening once
        if pts and isinstance(pts[0], list) and pts[0] and isinstance(pts[0][0], list):
            pts = [p for seg in pts for p in seg]
        n_geom += 1
        total_pts += len(pts)
        if len(pts) > 2: multi += 1
        if len(pts) > max_pts: max_pts = len(pts)

    if n_geom == 0:
        return {"slug": slug, "status": "ERROR", "reason": "no parseable line geometry"}

    avg = total_pts / n_geom
    pct_multi = 100 * multi / n_geom

    if avg < 2.5:
        status = "FAIL"
    elif avg < 4:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "slug": slug, "status": status,
        "n_lines": n_geom,
        "avg_pts": round(avg, 2),
        "multi_vertex": multi,
        "pct_multi": round(pct_multi, 0),
        "max_pts": max_pts,
        "total_vertices": total_pts,
    }


def main():
    args = sys.argv[1:]
    strict = "--strict" in args
    args = [a for a in args if not a.startswith("--")]

    if args and args[0] == "--all" or (not args):
        if args and args[0] == "--all": args = []
        slugs = sorted([os.path.dirname(p) for p in glob.glob("*/grid-geo.json")])
    else:
        slugs = args

    print(f"check_line_geometry.py — Discipline #28 — checking {len(slugs)} countries")
    print(f"  Thresholds: PASS avg>=4, WARN 2.5<=avg<4, FAIL avg<2.5")
    print()

    n_fail = 0; n_warn = 0; n_pass = 0; n_exempt = 0
    for slug in slugs:
        r = check_country(slug)
        if r["status"] == "FAIL":
            n_fail += 1
            print(f"  FAIL  {slug:<20} {r['n_lines']:>6} lines, avg {r['avg_pts']:>5.2f} pts, {r['pct_multi']:>3.0f}% multi-vertex (chord-only rendering)")
        elif r["status"] == "WARN":
            n_warn += 1
            print(f"  WARN  {slug:<20} {r['n_lines']:>6} lines, avg {r['avg_pts']:>5.2f} pts, {r['pct_multi']:>3.0f}% multi-vertex")
        elif r["status"] == "EXEMPT":
            n_exempt += 1
        elif r["status"] == "ERROR":
            n_fail += 1
            print(f"  ERROR {slug}: {r['reason']}")
        else:
            n_pass += 1

    print()
    print(f"Summary: {n_pass} PASS · {n_warn} WARN · {n_fail} FAIL · {n_exempt} exempt")
    if n_fail and strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
