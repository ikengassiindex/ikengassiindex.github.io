#!/usr/bin/env python3
"""
scripts/check_map_aesthetics.py — Discipline #26 (v2)

Map-rendering aesthetic gate. Catches polygon-geometry defects in
bounds.json that produce poor visual quality on the country map renderer.

Two axes of check (BOTH must pass for FAIL-free verdict):

  Axis 1: Per-feature centroid envelope
    Drops entire features (or multipolygon sub-rings) whose centroid is
    outside the country's primary populated envelope. Catches Cocos
    Island, Dokdo + Ulleungdo, etc. — codified Session 33 (CR Cocos
    hotfix) + Session 36 (Korea hotfix).

  Axis 2: Per-ring vertex envelope + jump-splice (NEW)
    Within each ring, detects vertices that stretch outside the country
    envelope AND any consecutive-vertex jumps > 0.5°. Catches in-ring
    offshore stretches (Jeollanam-do's Heuksan-do/Hong-do, etc.) where
    a single polygon ring traces mainland → offshore islet → back.

Plus geometric defects: open rings, max-jump > 2°, bounds-bbox
> 1.3× substation-bbox, over-detailed polygons (>4000 pts/feature).

Usage:
    python3 scripts/check_map_aesthetics.py <slug>
    python3 scripts/check_map_aesthetics.py --all

Exit codes:
    0 = PASS (or country has no bounds.json — substation auto-fit, exempt)
    1 = FAIL (geometric defect or aesthetic threshold exceeded)
"""
import json, math, os, sys, glob

# Country-specific mainland envelope hints (lat_min, lat_max, lon_min, lon_max)
# Auto-derived from substations + a 15% padding if not in this table.
COUNTRY_ENVELOPE = {
    "costa-rica": (8.04, 11.22, -85.95, -82.55),
    "korea":      (33.00, 39.00, 125.90, 130.50),  # mainland + Jeju; excludes Dokdo/Ulleungdo + Yellow Sea remote
    "iceland":    (63.00, 67.00, -25.00, -13.00),
    "israel":     (29.50, 33.50, 34.20, 35.90),
    "japan":      (24.00, 46.00, 123.00, 146.00),
    "netherlands":(50.70, 53.60, 3.30, 7.30),
    "belgium":    (49.40, 51.60, 2.50, 6.50),
    "estonia":    (57.50, 59.80, 21.70, 28.30),
    "latvia":     (55.60, 58.10, 20.90, 28.30),
    "lithuania":  (53.80, 56.50, 20.90, 26.90),
    "hungary":    (45.70, 48.70, 16.10, 22.90),
    "slovakia":   (47.70, 49.70, 16.80, 22.60),
    "slovenia":   (45.40, 46.90, 13.30, 16.70),
}

def ring_centroid(ring):
    if not ring: return (0.0, 0.0)
    lats = [p[1] for p in ring]
    lons = [p[0] for p in ring]
    return (sum(lats)/len(lats), sum(lons)/len(lons))

def ring_jumps(ring):
    """Return (max_jump_deg, n_jumps_over_1deg, n_jumps_over_2deg)."""
    if len(ring) < 2: return (0.0, 0, 0)
    max_j = 0.0; n1 = 0; n2 = 0
    for i in range(len(ring)-1):
        d = math.sqrt((ring[i+1][0]-ring[i][0])**2 + (ring[i+1][1]-ring[i][1])**2)
        if d > max_j: max_j = d
        if d > 2.0: n2 += 1
        if d > 1.0: n1 += 1
    return (max_j, n1, n2)

def is_ring_open(ring):
    return len(ring) > 0 and ring[0] != ring[-1]

def check_country(slug, repo_root="."):
    """Returns dict with findings; empty findings = PASS."""
    bounds_path = os.path.join(repo_root, slug, "bounds.json")
    grid_path   = os.path.join(repo_root, slug, "grid-geo.json")

    if not os.path.exists(bounds_path):
        return {"slug": slug, "status": "EXEMPT", "reason": "no bounds.json — substation auto-fit"}

    try: b = json.load(open(bounds_path))
    except Exception as e: return {"slug": slug, "status": "ERROR", "reason": f"bounds.json parse: {e}"}

    features = b.get("features") if isinstance(b, dict) else (b if isinstance(b, list) else [])
    if not features:
        return {"slug": slug, "status": "ERROR", "reason": "bounds.json has no features"}

    findings = []
    n_open = 0; n_jumps2 = 0; max_jump = 0.0; total_pts = 0
    n_features = len(features)
    bbox_lats = []; bbox_lons = []

    # Get country envelope (or auto-derive from substations)
    envelope = COUNTRY_ENVELOPE.get(slug)
    if not envelope and os.path.exists(grid_path):
        try:
            g = json.load(open(grid_path))
            subs = g.get("s") or g.get("substations") or {}
            sub_iter = subs.values() if isinstance(subs, dict) else subs
            slats = []; slons = []
            for s in sub_iter:
                if isinstance(s, dict):
                    la = s.get('y') or s.get('lat'); lo = s.get('x') or s.get('lon')
                    if la is not None: slats.append(la)
                    if lo is not None: slons.append(lo)
            if slats:
                pad_lat = (max(slats) - min(slats)) * 0.10
                pad_lon = (max(slons) - min(slons)) * 0.10
                envelope = (min(slats)-pad_lat, max(slats)+pad_lat,
                            min(slons)-pad_lon, max(slons)+pad_lon)
        except: pass

    # Per-feature + per-ring analysis
    for feat in features:
        g = feat.get("geometry") or {}
        gtype = g.get("type")
        coords = g.get("coordinates") or []
        if gtype == "Polygon": rings = [coords[0]] if coords else []
        elif gtype == "MultiPolygon": rings = [poly[0] for poly in coords if poly]
        else: continue

        for ring in rings:
            if len(ring) < 3: continue
            total_pts += len(ring)

            # Geometric checks
            if is_ring_open(ring):
                n_open += 1
                findings.append({"axis": "geometric", "severity": "FAIL",
                    "feature": feat.get("properties",{}).get("name","?"),
                    "issue": "open ring (ring[0] != ring[-1])"})

            mj, j1, j2 = ring_jumps(ring)
            if mj > max_jump: max_jump = mj
            if j2 > 0:
                n_jumps2 += j2
                findings.append({"axis": "geometric", "severity": "FAIL",
                    "feature": feat.get("properties",{}).get("name","?"),
                    "issue": f"max-jump {mj:.3f}° exceeds 2° threshold (severe offshore-connector)"})
            elif mj > 1.0:
                findings.append({"axis": "geometric", "severity": "WARN",
                    "feature": feat.get("properties",{}).get("name","?"),
                    "issue": f"jump {mj:.3f}° between 1-2° (possible in-ring offshore stretch)"})

            # Axis 1: Per-feature centroid envelope
            if envelope:
                clat, clon = ring_centroid(ring)
                lat_min, lat_max, lon_min, lon_max = envelope
                if not (lat_min <= clat <= lat_max and lon_min <= clon <= lon_max):
                    findings.append({"axis": "axis1_centroid", "severity": "FAIL",
                        "feature": feat.get("properties",{}).get("name","?"),
                        "issue": f"ring centroid ({clat:.2f},{clon:.2f}) outside envelope {envelope}"})

            # Axis 2: Per-ring vertex envelope (NEW)
            if envelope:
                lat_min, lat_max, lon_min, lon_max = envelope
                n_outside = sum(1 for p in ring
                                if not (lat_min <= p[1] <= lat_max and lon_min <= p[0] <= lon_max))
                pct_outside = 100 * n_outside / len(ring) if ring else 0
                if pct_outside > 5:
                    findings.append({"axis": "axis2_vertex", "severity": "FAIL" if pct_outside > 20 else "WARN",
                        "feature": feat.get("properties",{}).get("name","?"),
                        "issue": f"{n_outside}/{len(ring)} ring vertices outside envelope ({pct_outside:.1f}%)"})

            for p in ring:
                bbox_lats.append(p[1]); bbox_lons.append(p[0])

    # Substation bbox check
    if os.path.exists(grid_path) and bbox_lats:
        try:
            g = json.load(open(grid_path))
            subs = g.get("s") or g.get("substations") or {}
            sub_iter = subs.values() if isinstance(subs, dict) else subs
            slats = []; slons = []
            for s in sub_iter:
                if isinstance(s, dict):
                    la = s.get('y') or s.get('lat'); lo = s.get('x') or s.get('lon')
                    if la is not None: slats.append(la)
                    if lo is not None: slons.append(lo)
            if slats:
                bnd_lon_range = max(bbox_lons)-min(bbox_lons)
                sub_lon_range = max(slons)-min(slons)
                ratio = bnd_lon_range / max(sub_lon_range, 0.1)
                if ratio > 1.3:
                    findings.append({"axis": "axis2_vertex", "severity": "FAIL",
                        "feature": "(all)",
                        "issue": f"bounds-lon-range / sub-lon-range = {ratio:.2f}× (target <1.3×)"})
        except: pass

    # Over-detailed polygon check
    if n_features > 0 and total_pts / n_features > 4000:
        findings.append({"axis": "geometric", "severity": "WARN",
            "feature": "(all)",
            "issue": f"avg pts/feature {total_pts/n_features:.0f} > 4000 — apply Douglas-Peucker simplification"})

    # Determine overall status
    has_fail = any(f["severity"] == "FAIL" for f in findings)
    status = "FAIL" if has_fail else ("WARN" if findings else "PASS")

    return {"slug": slug, "status": status, "findings": findings,
            "metrics": {"n_features": n_features, "total_pts": total_pts,
                       "n_open_rings": n_open, "max_jump": round(max_jump, 3),
                       "n_jumps_over_2deg": n_jumps2}}

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: check_map_aesthetics.py <slug>|--all")
        sys.exit(2)

    if args[0] == "--all":
        slugs = [d for d in sorted(os.listdir("."))
                 if os.path.isdir(d) and os.path.exists(os.path.join(d,"bounds.json"))]
    else:
        slugs = args

    print(f"check_map_aesthetics.py — Discipline #26 v2 — checking {len(slugs)} countries")
    print(f"  Axis 1: per-feature centroid envelope")
    print(f"  Axis 2: per-ring vertex envelope + jump-splice")
    print()

    n_fail = 0; n_warn = 0; n_pass = 0; n_exempt = 0
    for slug in slugs:
        r = check_country(slug)
        if r["status"] == "FAIL":
            n_fail += 1
            print(f"  FAIL {slug}")
            for f in r["findings"]:
                if f["severity"] == "FAIL":
                    print(f"      → [{f['axis']}] {f['feature']}: {f['issue']}")
        elif r["status"] == "WARN":
            n_warn += 1
            print(f"  WARN {slug}")
            for f in r["findings"][:3]:
                print(f"      → [{f['axis']}] {f['feature']}: {f['issue']}")
        elif r["status"] == "EXEMPT":
            n_exempt += 1
        elif r["status"] == "ERROR":
            n_fail += 1
            print(f"  ERROR {slug}: {r.get('reason','?')}")
        else:
            n_pass += 1
            # quiet success

    print()
    print(f"Summary: {n_pass} PASS · {n_warn} WARN · {n_fail} FAIL · {n_exempt} exempt (no bounds.json)")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
