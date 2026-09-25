#!/usr/bin/env python3
"""estimate_fire_fetch_cost.py — price the CEMS fire-danger fetch BEFORE queueing it.

Per the working rule learned the expensive way on 3 September 2026: the CDS
prices a request server-side with nothing queued and nothing downloaded, and the
cost limit had been discovered three times by 24-hour rejection when it could
have been read in one second. Price first.

CREDENTIALS ARE NEVER PASSED TO THIS SCRIPT, and it does not invent a new place
to keep them. It reads the estate's existing `.env` with the same `load_env`
shape that `fetch_era5_I1_I2.py`, `fetch_cerra_daily_max.py` and `cds_jobs.py`
already use — one credential store for the estate, named in Pin 9, read by
scripts and never printed. An `export` at the prompt would put the key in shell
history; a `~/.ecmwfdatastoresrc` would create a SECOND store, which is worse
for audit than either one alone.

EWDS is a separate endpoint from the C3S CDS, so it needs its own two lines
added to that same file:

    EWDS_API_URL=https://ewds.climate.copernicus.eu/api
    EWDS_API_KEY=...

    python3 scripts/estimate_fire_fetch_cost.py

WHAT IT PRICES, and why these two variables:

  fire_daily_severity_rating  the operative climatology. DSR is a non-linear
                              transformation of FWI and is, per Vitolo et al.
                              (Scientific Data 6:190032), "considered suitable
                              as fire weather measure to be averaged over space
                              (i.e. region) and time (i.e. season)". FWI is not.
                              Averaging FWI over 86 years would be the same
                              class of error as the marginals defect that broke
                              I2.

  fire_weather_index          the cross-check. Counting days above the EFFIS
                              class thresholds is a legitimate use of FWI —
                              exceedance counting is not averaging.

MEASURED 21 September 2026 with --sweep: cost equals the exact day count (366
for leap-year 2024, 731 for 2023+2024) and the limit on this dataset is 3720,
not the 400 CERRA hit. Ten years fit in one request; eleven (4018) do not. So
the fetch is 9 ten-year windows x 2 variables = 18 requests, not 172.
"""
from __future__ import annotations
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cds_cost import find_env, load_env, field, open_client  # noqa: E402

DATASET = "cems-fire-historical-v1"
VARIABLES = ["fire_daily_severity_rating", "fire_weather_index"]
PROBE_YEAR = "2024"          # a complete year, priced as representative
MONTHS = ["%02d" % m for m in range(1, 13)]
DAYS = ["%02d" % d for d in range(1, 32)]

def request_for(variable, year):
    return request_for_years(variable, [year])


def request_for_years(variable, years):
    """Same request, N years wide. The CDS prices cost = variables x days, so
    this is the instrument that tests whether the measured cost actually scales
    with the year count or whether something else is being charged for."""
    return {
        "product_type": ["reanalysis"],
        "variable": [variable],
        "dataset_type": ["consolidated_dataset"],
        "system_version": ["4_1"],
        "year": list(years),
        "month": MONTHS,
        "day": DAYS,
        "grid": ["0.25/0.25"],
        "data_format": "grib",          # NetCDF4 is flagged Experimental
    }

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None, help="path to the estate .env")
    ap.add_argument("--sweep", action="store_true",
                    help="price 1/2/5/10/20-year requests to measure how cost scales")
    a = ap.parse_args()
    env_path = find_env(a.env)
    if not env_path:
        print("Could not locate the estate .env. Pass --env <path>.")
        return 2
    print("credential store: %s" % env_path)
    env = load_env(env_path)
    try:
        client = open_client(env, "EWDS")
    except SystemExit as exc:
        print(exc); return 2
    except Exception as exc:
        print("Client could not authenticate: %s" % exc); return 2

    print("dataset: %s" % DATASET)
    print("probe year: %s (one complete year, one variable per request)\n" % PROBE_YEAR)
    total = 0.0
    for v in VARIABLES:
        try:
            costs = client.get_process(DATASET).estimate_costs(request_for(v, PROBE_YEAR))
        except Exception as exc:
            print("  %-30s estimate FAILED: %s" % (v, exc)); continue
        print("  %-30s %s" % (v, costs))
        total += field(costs, "cost")
    if a.sweep:
        print("\nYEAR-COUNT SWEEP on %s — is cost linear in days?" % VARIABLES[0])
        base = None
        for n in (1, 2, 5, 10, 11, 20):
            years = [str(y) for y in range(2024 - n + 1, 2025)]
            try:
                c = client.get_process(DATASET).estimate_costs(
                    request_for_years(VARIABLES[0], years))
            except Exception as exc:
                print("  %2d year(s)  estimate FAILED: %s" % (n, exc)); continue
            cost = field(c, "cost")
            limit = field(c, "limit")
            if base is None:
                base = cost
            ratio = (cost / base) if base else float("nan")
            print("  %2d year(s)  cost %9.1f  limit %9.1f  %s  x%.2f vs 1y"
                  % (n, cost, limit, "OK" if cost <= limit else "OVER", ratio))
        return 0

    print("\n1940-2025 in ten-year windows (measured limit 3720 units = 10 years;")
    print("11 years prices at 4018 and is refused) x %d variables = %d requests."
          % (len(VARIABLES), 9 * len(VARIABLES)))
    print("Run --sweep to re-measure the limit before relying on that number.")
    print("Queue latency is per request and independent of payload — request")
    print("COUNT is the only lever, so queue them together rather than serially.")
    print("\nDownload volume, measured separately: 0.25 deg global daily is")
    print("~4.2 MB/day raw, ~1.5 GB/year, ~130 GB raw over 86 years per variable.")
    print("Do NOT store it. Stream: fetch a year, sample at the 622,104 points,")
    print("accumulate statistics, discard the raster. Kept per asset that is")
    print("~5 million values instead of 19.5 billion.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
