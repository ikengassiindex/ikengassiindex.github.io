#!/usr/bin/env python3
"""estimate_winter_fetch_cost.py — price the FMICLIM freezing-rain fetch.

The winter leg is anchored on Kämäräinen et al. (2017), NHESS 17:243-258 — open
access, read rather than cited from a title. Its FMICLIM diagnostic is a
CONDITIONAL test across four co-temporal fields:

    T2m below a cold-layer threshold                       (calibrated 0.09 C)
    a moist warm melting layer above it                    (min -0.64 C, RH >= 89%)
    minimum cold-layer depth                               (69 hPa)
    minimum precipitation rate                             (0.39 mm / 6 h)

Because it is conditional across co-temporal fields, it CANNOT be evaluated
from independently pre-aggregated marginals — the defect that broke I2 and
blocks I8. Every timestep must arrive with all its fields together. That is
what makes this leg expensive, and it is not negotiable by fetching less.

Two datasets, both C3S CDS, both open:

    reanalysis-era5-pressure-levels   RH + T at 925 / 850 / 700 hPa
    reanalysis-era5-single-levels     2m T, surface pressure, total precip

6-hourly (00/06/12/18 UTC), which is the paper's own timestep.

    python3 scripts/estimate_winter_fetch_cost.py            # one year, both
    python3 scripts/estimate_winter_fetch_cost.py --sweep    # find the boundary

Nothing is queued and nothing is downloaded. No credential is passed in, read
aloud, or printed.
"""
from __future__ import annotations
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cds_cost import find_env, load_env, open_client, price, sweep, find_boundary  # noqa: E402

PL_DATASET = "reanalysis-era5-pressure-levels"
SL_DATASET = "reanalysis-era5-single-levels"

PL_VARIABLES = ["relative_humidity", "temperature"]
PL_LEVELS = ["925", "850", "700"]
SL_VARIABLES = ["2m_temperature", "surface_pressure", "total_precipitation"]

TIMES = ["00:00", "06:00", "12:00", "18:00"]     # the paper's 6-hourly timestep
MONTHS = ["%02d" % m for m in range(1, 13)]
DAYS = ["%02d" % d for d in range(1, 32)]
END_YEAR = 2024


def years_ending(n, end=END_YEAR):
    return [str(y) for y in range(end - n + 1, end + 1)]


def pl_request(n_years):
    return {
        "product_type": ["reanalysis"],
        "variable": PL_VARIABLES,
        "pressure_level": PL_LEVELS,
        "year": years_ending(n_years),
        "month": MONTHS,
        "day": DAYS,
        "time": TIMES,
        "grid": ["0.25/0.25"],
        "data_format": "grib",
    }


def sl_request(n_years):
    return {
        "product_type": ["reanalysis"],
        "variable": SL_VARIABLES,
        "year": years_ending(n_years),
        "month": MONTHS,
        "day": DAYS,
        "time": TIMES,
        "grid": ["0.25/0.25"],
        "data_format": "grib",
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None, help="path to the estate .env")
    ap.add_argument("--sweep", action="store_true",
                    help="price several window sizes to locate the limit")
    a = ap.parse_args()

    env_path = find_env(a.env)
    if not env_path:
        print("Could not locate the estate .env. Pass --env <path>.")
        return 2
    print("credential store: %s" % env_path)
    env = load_env(env_path)
    try:
        client = open_client(env, "CDS")
    except SystemExit as exc:
        print(exc); return 2
    except Exception as exc:
        print("Client could not authenticate: %s" % exc); return 2

    legs = [
        (PL_DATASET, pl_request,
         "%d vars x %d levels x %d times" % (len(PL_VARIABLES), len(PL_LEVELS), len(TIMES))),
        (SL_DATASET, sl_request,
         "%d vars x %d times" % (len(SL_VARIABLES), len(TIMES))),
    ]

    counts = (1, 2, 5, 10) if a.sweep else (1,)
    for dataset, build, shape in legs:
        print("\n%s  (%s, %d-%d probe)" % (dataset, shape, END_YEAR, END_YEAR))
        if a.sweep:
            sweep(client, dataset, build, counts)
            best, _, _, _, _ = find_boundary(client, dataset, build, 1, 90)
            if best:
                windows = -(-86 // best)
                print("  -> %d-year windows; 1940-2025 is %d request(s)" % (best, windows))
            else:
                print("  -> even ONE year exceeds the limit; must sub-divide below a year")
        else:
            try:
                cost, limit = price(client, dataset, build(1))
            except Exception as exc:
                print("  estimate FAILED: %s" % exc); continue
            print("  1 year   cost %10.1f  limit %10.1f  %s"
                  % (cost, limit, "OK" if cost <= limit else "OVER"))

    print("\nThe fetch cannot be made cheaper by dropping fields: FMICLIM is a")
    print("conditional test across all of them at the same timestep. It can only")
    print("be made cheaper by fetching a SHORTER RECORD, which is a decision for")
    print("the operator, not an optimisation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
