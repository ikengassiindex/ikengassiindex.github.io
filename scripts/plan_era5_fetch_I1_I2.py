#!/usr/bin/env python3
"""
Plan (and optionally run) the ERA5-Land fetch that I1 and I2 need.

    python3 scripts/plan_era5_fetch_I1_I2.py --plan
    python3 scripts/plan_era5_fetch_I1_I2.py --write-requests requests.json
    python3 scripts/plan_era5_fetch_I1_I2.py --fetch          # needs cdsapi + ~/.cdsapirc

WHAT IS MISSING AND WHY
-----------------------
I1 (Snow/Ice, 0.12) and I2 (Tree-fall, 0.09) are 0.21 of component I and have
no inputs in the repo. The cache holds daily-max 2 m temperature only — enough
for I3 and I5, not for these.

The existing climate module cannot supply them either: its ERA5 baseline is
computed and then never read (climate.py::compute_iri_forward), and what it
computes is an affine transform of a mean temperature wearing the name of a day
count. See FINDING_iri_current_was_never_real.md.

WHAT TO REQUEST
---------------
Dataset `derived-era5-land-daily-statistics`, matching the window and extent of
the daily-max temperature already cached, so the two are directly comparable and
the land mask and cell-resolution code already written are reused unchanged.

  I2  10m_u_component_of_wind, 10m_v_component_of_wind   daily_maximum
  I1  snow_depth                                          daily_maximum
      2m_temperature                                      daily_minimum

2m_temperature daily_maximum rides along in the same request at no extra cost,
because these boxes COVER TERRITORY THE EXISTING CACHE DOES NOT. I3 and I5 are
at 99.68%, and the 1,975 missing substations are missing for exactly one
reason: the cached temperature was fetched against the under-covering project
bbox table. spain 818 (Canaries + Balearics), us 870, france 153, portugal 91
(Azores, Madeira), uk 32, canada 5, estonia 2, new-zealand 1.

Those records cannot be recovered from what is cached — they sit outside the
grid entirely. Fetching daily-max temperature on the clustered boxes closes
I3 and I5 to 100% as a side effect of a request that was being made anyway.
Leaving it out would have meant a second fetch later for one variable.

Years 2018-2022. Full Bourgouin freezing rain needs HOURLY precipitation and
dewpoint and is a far larger acquisition; snow depth plus freezing-day counts is
the tractable I1 and is what the construct actually names — the Alpine snowfall
signal d11_era5 explicitly defers to.

WHY CLUSTERS AND NOT ONE BOX PER COUNTRY
----------------------------------------
The project's own bbox table (climate.py::_country_bbox) UNDER-COVERS: 31 of 39
countries have substations outside their box. That is exactly why I3 and I5
skipped records — spain's 818 are the Canaries (Gran Canaria 327, Tenerife 322)
and the Balearics, excluded by a box starting at 36.0 N and stopping at 3.3 E.

But a box drawn around ALL of a country's substations over-covers just as badly,
because several countries hold distant territory:

    france        lat -21.7..51.4  lon -62.0..56.1   Reunion, Antilles, Guiana
    us            lat  13.0..70.6  lon -165.7..145.2 Alaska, Hawaii, Guam
    portugal      lon -31.6..-5.9                    Azores, Madeira
    new-zealand   lon -176.8..178.7                  crosses the antimeridian

A single box for france would request most of the Atlantic and Indian Oceans.

So the substations are clustered geographically and one box is emitted per
cluster. Coverage is complete by construction — every substation is inside some
box — and the requested area stays close to where the assets actually are.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location(
    "geo", ROOT / "scripts" / "ssi_derive_metrics_I4_I6.py")
geo = importlib.util.module_from_spec(_s); _s.loader.exec_module(geo)

YEARS = [2018, 2019, 2020, 2021, 2022]
MARGIN_DEG = 0.3          # one ERA5-Land cell is 0.1 deg; 3 cells of slack
LINK_DEG = 3.0            # clusters closer than this are merged
DATASET = "derived-era5-land-daily-statistics"

# Grouped BY STATISTIC, because one request carries one daily_statistic but any
# number of variables — and the API takes a list of years. Ungrouped this was
# 885 requests (3 sets x 5 years x 59 boxes); grouped it is 118, which is a
# reasonable thing to ask someone to run.
REQUESTS = [
    {"tag": "dmax", "for": "I2 + I1 + I3/I5 gap",
     "variables": ["10m_u_component_of_wind", "10m_v_component_of_wind",
                   "snow_depth", "2m_temperature"],
     "statistic": "daily_maximum"},
    {"tag": "dmin", "for": "I1",
     "variables": ["2m_temperature"],
     "statistic": "daily_minimum"},
]


def cluster(points, link=LINK_DEG):
    """Single-link clustering on a lat/lon grid. Cheap and sufficient — the
    question is only 'is this territory near that one', not taxonomy."""
    cells = {}
    for la, lo in points:
        cells.setdefault((int(la // link), int(lo // link)), []).append((la, lo))
    keys = list(cells)
    parent = {k: k for k in keys}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    kset = set(keys)
    for k in keys:
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                n = (k[0] + di, k[1] + dj)
                if n in kset:
                    union(k, n)
    groups = {}
    for k in keys:
        groups.setdefault(find(k), []).extend(cells[k])
    return list(groups.values())


def boxes_for(slug):
    man, subs, _ = geo.load_substations(slug)
    pts = [(s["lat"], s["lon"]) for s in subs
           if isinstance(s.get("lat"), (int, float))
           and isinstance(s.get("lon"), (int, float))]
    n_total = len(subs)
    del subs, man
    out = []
    for grp in cluster(pts):
        la = [p[0] for p in grp]; lo = [p[1] for p in grp]
        out.append({
            "n": len(grp),
            "north": round(max(la) + MARGIN_DEG, 2),
            "south": round(min(la) - MARGIN_DEG, 2),
            "west":  round(min(lo) - MARGIN_DEG, 2),
            "east":  round(max(lo) + MARGIN_DEG, 2),
        })
    out.sort(key=lambda b: -b["n"])
    return out, n_total, len(pts)


def area(b):
    lat_km = (b["north"] - b["south"]) * 111.0
    mid = math.radians((b["north"] + b["south"]) / 2)
    lon_km = (b["east"] - b["west"]) * 111.0 * max(math.cos(mid), 0.01)
    return lat_km * lon_km


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--write-requests", default="")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--out-dir", default="scripts/pipeline/.cache")
    a = ap.parse_args()

    plan, total_boxes, total_area = {}, 0, 0.0
    print(f"\n  ERA5-Land fetch plan for I1 + I2 — {DATASET}\n")
    print(f"  {'country':13}{'subs':>8}{'boxes':>7}{'largest box (S..N / W..E)':>34}")
    for slug in geo.load_slugs():
        try:
            bs, n_total, n_pts = boxes_for(slug)
        except Exception as ex:
            print(f"  {slug:13} ERROR {ex}")
            continue
        plan[slug] = bs
        total_boxes += len(bs)
        total_area += sum(area(b) for b in bs)
        b = bs[0]
        txt = "%.1f..%.1f / %.1f..%.1f" % (b["south"], b["north"], b["west"], b["east"])
        extra = "" if len(bs) == 1 else f"  (+{len(bs)-1} more)"
        print(f"  {slug:13}{n_total:>8,}{len(bs):>7}{txt:>34}{extra}")

    print(f"\n  {total_boxes} boxes across 39 countries · "
          f"{total_area/1e6:.1f} million km2 requested · "
          f"{len(REQUESTS)} request sets, all {len(YEARS)} years per request "
          f"= {total_boxes * len(REQUESTS):,} CDS requests")
    print("\n  Requests per box-year:")
    for r in REQUESTS:
        print(f"    {r['tag']:6} {r['for']:3} {r['statistic']:14} {', '.join(r['variables'])}")

    if a.write_requests:
        payload = {"dataset": DATASET, "years": YEARS,
                   "request_sets": REQUESTS, "boxes": plan}
        pathlib.Path(a.write_requests).write_text(json.dumps(payload, indent=1))
        print(f"\n  written {a.write_requests}")

    if a.fetch:
        try:
            import cdsapi
        except ImportError:
            sys.exit("\n  cdsapi not installed:  pip3 install cdsapi\n"
                     "  and put your key in ~/.cdsapirc — see "
                     "https://cds.climate.copernicus.eu/how-to-api\n")
        c = cdsapi.Client()
        out = pathlib.Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
        for slug, bs in plan.items():
            for bi, b in enumerate(bs):
                for r in REQUESTS:
                    if True:
                        tgt = out / f"era5land_{r['tag']}_{slug}_{bi}.nc"
                        if tgt.exists():
                            print(f"  have {tgt.name}"); continue
                        req = {
                            "variable": r["variables"],
                            "year": [str(y) for y in YEARS],
                            "month": [f"{m:02d}" for m in range(1, 13)],
                            "day": [f"{d:02d}" for d in range(1, 32)],
                            "daily_statistic": r["statistic"],
                            "time_zone": "utc+00:00",
                            "frequency": "1_hourly",
                            "area": [b["north"], b["west"], b["south"], b["east"]],
                        }
                        print(f"  -> {tgt.name}")
                        c.retrieve(DATASET, req, str(tgt))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
