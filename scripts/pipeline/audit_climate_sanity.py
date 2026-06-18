#!/usr/bin/env python3
"""
P15-C2 — Climate sanity-check audit.

After the P15-A-3 ERA5-Land + daily-statistics batch lands, this CLI
audits each per-country era5_baseline_<country>.csv against known
reference cities to verify the L1 output makes physical sense.

For each reference city: find the nearest grid point in the country's
CSV, check if its (t_mean_c, heat_days, ice_days) fall within the
expected envelope. Flag any country that fails.

Expected envelopes are calibrated from published climatologies (ECCAD,
NOAA NCEI, IPCC AR6) for the 1991-2020 standard climatological window.

Usage:
    python3 scripts/pipeline/audit_climate_sanity.py          # audit all 39
    python3 scripts/pipeline/audit_climate_sanity.py --country italy
    python3 scripts/pipeline/audit_climate_sanity.py --json   # machine-readable

Acceptance gate: every country green = climate ingestion is physical-bounds
compliant. Any red flags suggest CDS API quirks, bad bbox, mis-rounded
coords, or unit-conversion bugs.
"""
import argparse
import csv
import json
import sys
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA = REPO_ROOT / "scripts" / "pipeline" / "data" / "cross-cutting"


# ═══════════════════════════════════════════════════════════
#  Reference cities + expected ranges (calibrated from public climatology)
# ═══════════════════════════════════════════════════════════
# Each entry: (city, country, lat, lon, t_mean_c_range, heat_days_range, ice_days_range)
# Ranges intentionally generous to absorb the 5-year-vs-30-year window difference
# and the 0.1° grid-cell averaging vs published station data.

REFERENCE_CITIES = [
    # (label,             country,        lat,    lon,    t_range,    heat_range, ice_range)
    ("Rome",              "italy",         41.9,   12.5,   (13, 19),   (25, 75),    (0, 10)),
    ("Manchester",        "uk",            53.5,   -2.2,   (7, 13),    (0, 12),     (15, 50)),
    ("Reykjavik",         "iceland",       64.1,  -21.9,   (2, 8),     (0, 2),      (60, 140)),
    ("Madrid",            "spain",         40.4,   -3.7,   (12, 18),   (40, 100),   (0, 25)),
    ("Phoenix-equiv",     "us",            33.4, -112.1,   (20, 26),   (130, 200),  (0, 5)),
    ("Tromsø",            "norway",        69.6,   18.9,   (-3, 6),    (0, 3),      (90, 200)),
    ("Cairns",            "australia",    -16.9,  145.8,   (22, 28),   (180, 365),  (0, 0)),
    ("Tokyo",             "japan",         35.7,  139.7,   (13, 19),   (20, 70),    (0, 20)),
    ("Mexico City",       "mexico",        19.4,  -99.1,   (13, 20),   (5, 60),     (0, 15)),
    ("Oslo",              "norway",        59.9,   10.7,   (3, 9),     (0, 12),     (50, 130)),
    ("Helsinki",          "finland",       60.2,   24.9,   (3, 8),     (0, 12),     (60, 140)),
    ("Berlin",            "germany",       52.5,   13.4,   (8, 12),    (3, 25),     (15, 50)),
    ("Athens",            "greece",        37.9,   23.7,   (15, 21),   (60, 130),   (0, 8)),
    ("Lisbon",            "portugal",      38.7,   -9.1,   (14, 19),   (15, 75),    (0, 5)),
    ("Wellington",        "new-zealand",  -41.3,  174.8,   (10, 16),   (0, 20),     (0, 10)),
    ("Reykjavik 2",       "iceland",       64.0,  -22.0,   (2, 8),     (0, 2),      (60, 140)),
    ("Seoul",             "korea",         37.6,  127.0,   (10, 16),   (15, 60),    (15, 60)),
    ("Antalya",           "turkey",        36.9,   30.7,   (16, 22),   (60, 140),   (0, 5)),
    ("Brussels",          "belgium",       50.8,    4.4,   (8, 13),    (3, 25),     (10, 40)),
    ("Vienna",            "austria",       48.2,   16.4,   (8, 13),    (10, 35),    (15, 50)),
    ("Stockholm",         "sweden",        59.3,   18.1,   (5, 10),    (0, 15),     (40, 110)),
    ("Reykjavik (Iceland)","iceland",      64.1,  -21.9,   (2, 8),     (0, 2),      (60, 140)),
    ("Copenhagen",        "denmark",       55.7,   12.6,   (7, 11),    (0, 12),     (10, 50)),
    ("Dublin",            "ireland",       53.3,   -6.3,   (8, 12),    (0, 8),      (5, 25)),
    ("Bern",              "switzerland",   46.9,    7.4,   (7, 13),    (3, 25),     (25, 80)),
    ("Riga",              "latvia",        56.9,   24.1,   (5, 9),     (0, 12),     (50, 110)),
    ("Tallinn",           "estonia",       59.4,   24.8,   (3, 8),     (0, 8),      (60, 130)),
    ("Vilnius",           "lithuania",     54.7,   25.3,   (4, 9),     (0, 12),     (50, 120)),
    ("Bratislava",        "slovakia",      48.1,   17.1,   (8, 13),    (10, 40),    (15, 60)),
    ("Ljubljana",         "slovenia",      46.1,   14.5,   (8, 13),    (5, 35),     (25, 70)),
    ("Budapest",          "hungary",       47.5,   19.1,   (9, 14),    (15, 60),    (15, 55)),
    ("Prague",            "czechia",       50.1,   14.4,   (7, 11),    (3, 25),     (20, 60)),
    ("Warsaw",            "poland",        52.2,   21.0,   (7, 11),    (3, 25),     (30, 80)),
    ("Luxembourg",        "luxembourg",    49.6,    6.1,   (8, 12),    (3, 20),     (15, 50)),
    ("Amsterdam",         "netherlands",   52.4,    4.9,   (8, 12),    (0, 12),     (5, 30)),
    ("Paris",             "france",        48.9,    2.4,   (9, 14),    (5, 25),     (5, 30)),
    ("Tel Aviv",          "israel",        32.1,   34.8,   (18, 23),   (90, 180),   (0, 0)),
    ("San José (CR)",     "costa-rica",     9.9,  -84.1,   (18, 24),   (0, 30),     (0, 0)),
    ("Bogotá",            "colombia",       4.7,  -74.1,   (12, 17),   (0, 20),     (0, 0)),
    ("Santiago",          "chile",        -33.4,  -70.7,   (12, 18),   (40, 110),   (0, 10)),
    ("Nuuk",              "greenland",     64.2,  -51.7,   (-3, 4),    (0, 0),      (140, 250)),
    ("Toronto",           "canada",        43.7,  -79.4,   (6, 11),    (15, 55),    (40, 110)),
]


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km."""
    R = 6371.0
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def find_nearest_grid_point(rows, target_lat, target_lon):
    """Find the row in rows whose (lat, lon) is nearest target."""
    best = None
    best_dist = float("inf")
    for r in rows:
        try:
            lat = float(r["lat"])
            lon = float(r["lon"])
        except (KeyError, ValueError):
            continue
        d = haversine_km(lat, lon, target_lat, target_lon)
        if d < best_dist:
            best_dist = d
            best = r
    return best, best_dist


def audit_city(label, country, ref_lat, ref_lon, t_range, heat_range, ice_range):
    """Returns a result dict."""
    csv_path = DATA / f"era5_baseline_{country}.csv"
    if not csv_path.exists():
        return {
            "label": label, "country": country,
            "status": "MISSING",
            "message": f"era5_baseline_{country}.csv not yet present (P15-A-3 batch not run)",
        }
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {
            "label": label, "country": country,
            "status": "EMPTY",
            "message": f"era5_baseline_{country}.csv has zero rows",
        }
    nearest, dist_km = find_nearest_grid_point(rows, ref_lat, ref_lon)
    if nearest is None:
        return {
            "label": label, "country": country,
            "status": "NO_NEAREST",
            "message": "Could not parse any lat/lon in CSV",
        }
    try:
        t_mean = float(nearest["t_mean_c"])
        heat = float(nearest["heat_days"])
        ice  = float(nearest["ice_days"])
    except (KeyError, ValueError) as e:
        return {
            "label": label, "country": country,
            "status": "MALFORMED",
            "message": f"Nearest grid point malformed: {e}",
        }
    flags = []
    if not (t_range[0] <= t_mean <= t_range[1]):
        flags.append(f"t_mean_c={t_mean:.1f} outside {t_range}")
    if not (heat_range[0] <= heat <= heat_range[1]):
        flags.append(f"heat_days={heat:.1f} outside {heat_range}")
    if not (ice_range[0] <= ice <= ice_range[1]):
        flags.append(f"ice_days={ice:.1f} outside {ice_range}")
    return {
        "label": label, "country": country,
        "ref_lat": ref_lat, "ref_lon": ref_lon,
        "nearest_lat": float(nearest["lat"]), "nearest_lon": float(nearest["lon"]),
        "distance_km": round(dist_km, 1),
        "t_mean_c": round(t_mean, 1),
        "heat_days": round(heat, 1),
        "ice_days": round(ice, 1),
        "status": "OK" if not flags else "FLAG",
        "flags": flags,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--country", help="Audit only one country")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = p.parse_args()

    targets = REFERENCE_CITIES
    if args.country:
        targets = [t for t in targets if t[1] == args.country]
        if not targets:
            print(f"No reference city configured for country={args.country}", file=sys.stderr)
            return 1

    results = [audit_city(*t) for t in targets]

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    # Human-readable output
    print(f"\n═══ P15-C2 climate sanity audit ({len(results)} reference cities) ═══\n")
    print(f"  {'city':22s} {'country':14s} {'status':6s}  t_mean_c  heat_days  ice_days  flags")
    print(f"  {'-'*22} {'-'*14} {'-'*6}  {'-'*8}  {'-'*9}  {'-'*8}  {'-'*40}")

    status_counts = {"OK": 0, "FLAG": 0, "MISSING": 0, "EMPTY": 0, "MALFORMED": 0, "NO_NEAREST": 0}
    for r in results:
        s = r["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
        if s == "MISSING" or s == "EMPTY" or s == "MALFORMED" or s == "NO_NEAREST":
            print(f"  {r['label'][:22]:22s} {r['country']:14s} {s:6s}  {r['message']}")
        else:
            flag_str = "; ".join(r["flags"]) if r["flags"] else ""
            print(f"  {r['label'][:22]:22s} {r['country']:14s} {s:6s}  "
                  f"{r['t_mean_c']:>8.1f}  {r['heat_days']:>9.1f}  {r['ice_days']:>8.1f}  {flag_str}")

    print()
    print(f"  Summary: OK {status_counts['OK']} · FLAG {status_counts['FLAG']} · MISSING {status_counts['MISSING']}")
    if status_counts["FLAG"] > 0:
        print(f"\n  ⚠ {status_counts['FLAG']} reference city checks fell outside expected envelope.")
        print(f"  Investigate via the per-city flag messages above.")
    if status_counts["MISSING"] > 0:
        print(f"\n  ⏳ {status_counts['MISSING']} countries still missing climate data (P15-A-3 batch pending).")

    # Exit non-zero if any actual FLAGs (real out-of-range), even with MISSING noise
    return 1 if status_counts["FLAG"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
