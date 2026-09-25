#!/usr/bin/env python3
"""The single place that answers "what is this country's polygon, and who says so".

    python3 scripts/ssi_boundary_source.py            # report what resolves today

WHY THIS EXISTS
    Discipline #36 tested each fleet against {country}/bounds.json, a file of
    unrecorded provenance that varies in quality by an order of magnitude.
    Measured against Eurostat GISCO NUTS 2024:

        slovenia/bounds.json    +33.9% too large   (27,136 km² vs 20,269)
        netherlands/bounds.json +11.2% too large
        ireland/bounds.json      +4.2% too large   — reaches into the North
        norway/bounds.json       under-inclusive   — 652 false positives
        denmark/bounds.json      under-inclusive   — 216 false positives
        portugal/bounds.json     under-inclusive   — 166 false positives
        france/bounds.json       under-inclusive   — 3,149 false positives

    An over-large polygon hides contamination; an under-large one invents it.
    Both were happening at once, in different countries, unnoticed, because
    nothing ever compared bounds.json to an authority.

THE RULE
    One source family, declared per country:
      1. GISCO NUTS 2024 1:1M EPSG:4326, union of a country's NUTS-3 units.
         Covers 26 of the 39. Gives sub-national granularity for free.
      2. GISCO CNTR 2024 1:1M EPSG:4326, country polygons, for the rest and
         for every non-cohort neighbour the exclusivity test needs.
      3. {country}/bounds.json — FALLBACK ONLY, and every caller is told.

    It never silently degrades. A country with no authoritative polygon is
    reported as such, by name, and the caller decides. §7.5.
"""
from __future__ import annotations
import collections, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from _ssi_gis_dir import gis_dir, nuts_path, cntr_path, candidates   # noqa: E402

# The directory is RESOLVED, not assumed. This line previously read
#   GIS = ~/mnt/eurostat_gisco_nuts3_2024
# which is a Cowork device-VM mount path. On the operator's own Mac the folder
# is at ~/eurostat_gisco_nuts3_2024, so CNTR was not found, all thirteen
# non-NUTS countries fell back to bounds.json, and the cross-border gate
# correctly failed closed on a clean country. Verified in one environment,
# shipped to another.
try:
    GIS = gis_dir()
    NUTS_SHP = nuts_path()
    _c = cntr_path()
except RuntimeError as _e:                     # named, never silent. §7.5
    sys.stderr.write(str(_e) + "\n")
    GIS = candidates()[0]
    NUTS_SHP = GIS / "NUTS_RG_01M_2024_4326.shp"
    _c = None
_C = "CNTR_RG_01M_2024_4326"
CNTR_SHP = _c if _c is not None else (GIS / f"{_C}.shp")

NUTS_CC = {
    "austria":"AT","belgium":"BE","czechia":"CZ","denmark":"DK","estonia":"EE",
    "finland":"FI","france":"FR","germany":"DE","greece":"EL","hungary":"HU",
    "iceland":"IS","ireland":"IE","italy":"IT","latvia":"LV","lithuania":"LT",
    "luxembourg":"LU","netherlands":"NL","norway":"NO","poland":"PL",
    "portugal":"PT","slovakia":"SK","slovenia":"SI","spain":"ES","sweden":"SE",
    "switzerland":"CH","turkey":"TR",
}
CNTR_CC = {
    "australia":"AU","canada":"CA","chile":"CL","colombia":"CO",
    "costa-rica":"CR","greenland":"GL","israel":"IL","japan":"JP",
    "korea":"KR","mexico":"MX","new-zealand":"NZ","uk":"UK","us":"US",
}

def _read(shp):
    try:
        import shapefile                       # pyshp
        from shapely.geometry import shape     # shapely
    except ImportError as e:
        raise SystemExit(
            "MISSING DEPENDENCY: %s\n"
            "This script reads GISCO shapefiles and cannot proceed without it.\n"
            "Install it into the interpreter that runs this script:\n"
            "    python3 -m pip install --user pyshp shapely\n"
            "If pip refuses with 'externally-managed-environment', add\n"
            "    --break-system-packages\n"
            "Interpreter in use: %s" % (e, sys.executable))
    sf = shapefile.Reader(str(shp))
    flds = [f[0] for f in sf.fields[1:]]
    for sr in sf.iterShapeRecords():
        yield dict(zip(flds, sr.record)), shape(sr.shape.__geo_interface__)

def load(include_neighbours=True):
    """Returns (polygons, provenance, unresolved)."""
    from shapely.ops import unary_union
    polys, prov, unresolved = {}, {}, []

    nuts3 = collections.defaultdict(list)
    if NUTS_SHP.exists():
        for r, g in _read(NUTS_SHP):
            if int(r.get("LEVL_CODE", 9)) == 3:
                nuts3[r["CNTR_CODE"]].append(g)
    cntr = {}
    if CNTR_SHP.exists():
        for r, g in _read(CNTR_SHP):
            cid = r.get("CNTR_ID") or r.get("CNTR_CODE") or r.get("ISO3_CODE")
            cntr.setdefault(cid, []).append(g)

    for slug, cc in NUTS_CC.items():
        if cc in nuts3:
            polys[slug] = unary_union([g.buffer(0) for g in nuts3[cc]])
            prov[slug] = f"GISCO NUTS 2024 1:1M EPSG:4326, union of {len(nuts3[cc])} NUTS-3 units ({cc})"
        else:
            unresolved.append((slug, "NUTS shapefile missing or country absent"))
    for slug, cc in CNTR_CC.items():
        if cc in cntr:
            polys[slug] = unary_union([g.buffer(0) for g in cntr[cc]])
            prov[slug] = f"GISCO CNTR 2024 1:1M EPSG:4326 ({cc})"
        else:
            unresolved.append((slug, f"GISCO CNTR not available for {cc}"))

    if include_neighbours:
        for cc, gs in nuts3.items():
            if cc in NUTS_CC.values(): continue
            polys["_" + cc] = unary_union([g.buffer(0) for g in gs])
            prov["_" + cc] = f"GISCO NUTS 2024 union ({cc}) — neighbour only"
        for cid, gs in cntr.items():
            key = "_" + str(cid)
            if key in polys or cid in CNTR_CC.values(): continue
            polys[key] = unary_union([g.buffer(0) for g in gs])
            prov[key] = f"GISCO CNTR 2024 ({cid}) — neighbour only"
    return polys, prov, unresolved

def fallback_bounds(slug):
    """The declared fallback. Callers must surface that they used it."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    p = ROOT / slug / "bounds.json"
    if not p.exists(): return None
    b = json.load(open(p))
    fs = [shape(f["geometry"]).buffer(0) for f in b.get("features", []) if f.get("geometry")]
    return unary_union(fs) if fs else None

if __name__ == "__main__":
    print(f"NUTS shapefile : {'present' if NUTS_SHP.exists() else 'MISSING'}  {NUTS_SHP}")
    print(f"CNTR shapefile : {'present' if CNTR_SHP.exists() else 'MISSING'}  {CNTR_SHP}")
    polys, prov, unresolved = load()
    cohort = [k for k in polys if not k.startswith("_")]
    print(f"\nauthoritative polygons for {len(cohort)} of {len(NUTS_CC)+len(CNTR_CC)} cohort countries")
    print(f"neighbour polygons: {len(polys)-len(cohort)}")
    if unresolved:
        print(f"\nUNRESOLVED — these have NO authoritative polygon and fall back to bounds.json:")
        for slug, why in unresolved:
            fb = fallback_bounds(slug)
            print(f"   {slug:<14} {why}   fallback: {'bounds.json' if fb else 'NONE'}")
    else:
        print("\n✓ every cohort country has an authoritative polygon; no fallback in use")
