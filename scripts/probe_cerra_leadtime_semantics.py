#!/usr/bin/env python3
"""
Establish what a CERRA gust leadtime actually covers, before five years are fetched.

    python3 scripts/probe_cerra_leadtime_semantics.py --env <.env>

WHY THIS EXISTS
    The January probes were fetched with leadtime_hour = ["1"] and came back
    with 248 timesteps for a 31-day month: 8 per day, one per 3-hourly analysis
    at 00, 03, ... 21 UTC. If each of those fields is the gust maximum over the
    single hour following its analysis, then that fetch saw 8 hours out of every
    24 and never looked at the other 16.

    I2 is an ANNUAL MAXIMUM. A metric built on a maximum cannot be computed from
    a third of the hours: the estimate is biased low, and biased low unevenly,
    because gusts have a diurnal cycle and the sampled hours are not a random
    third of the day.

    It also puts the one comparison already made in doubt. CERRA measured 0.891
    of ERA5 at the same substations — 11 per cent lower. The ERA5 side is a
    DAILY MAXIMUM over all 24 hours (derived-era5-land-daily-statistics, 365
    timesteps per year, confirmed on disk). If the CERRA side saw a third of the
    hours, then some or all of that 11 per cent is the sampling, not the model,
    and the two numbers were never like for like.

    The fix, if the reading is right, is leadtime_hour = ["1","2","3"]: three
    one-hour windows per 3-hourly run, tiling the day with no gap and no overlap.
    That prices at 52,560 per variable-year against a limit of 90,000, so a year
    still fits in one request, and it triples the bytes.

    Tripling a 33 GB fetch on an inference is not acceptable. So: one day, all
    three leadtimes, cost 144, and the time axis answers it.

WHAT DECIDES IT
    Fetch 2018-01-01 with leadtime_hour 1, 2 and 3 and read the valid_time axis.

      24 distinct hourly timestamps       -> each leadtime is a distinct 1-hour
                                             window; they tile the day; the
                                             lt=["1"] fetch saw 8 hours of 24.
                                             Refetch with 1,2,3.

      8 timestamps, or duplicates, or a
      separate step/leadtime dimension    -> the windows are nested or the file
                                             is shaped differently than assumed.
                                             Read it before deciding anything.

    A second, independent check runs on the same file: for the analysis at 00
    UTC, compare the three leadtime fields cell by cell. Nested windows (max over
    [0,1], [0,2], [0,3]) are monotonically non-decreasing everywhere by
    construction. Disjoint hourly windows are not. That distinguishes the two
    readings even if the time axis is ambiguous.

WHAT IT DOES NOT DO
    It does not derive anything and it does not touch a published record.
"""
from __future__ import annotations
import argparse, pathlib, re, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
DS = "reanalysis-cerra-single-levels"


def load_env(p):
    env = {}
    for ln in open(p, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
        if m:
            env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if not env.get("CDS_API_KEY"):
        sys.exit("CDS_API_KEY not found in the .env")
    return env


def inspect(path) -> int:
    import netCDF4, numpy as np, cftime
    d = netCDF4.Dataset(str(path))
    dims = {k: len(v) for k, v in d.dimensions.items()}
    print(f"\n  dimensions : {dims}")
    print(f"  variables  : {list(d.variables)}")

    tname = "valid_time" if "valid_time" in d.variables else "time"
    tv = d.variables[tname]
    t = cftime.num2date(tv[:], tv.units, getattr(tv, "calendar", "standard"))
    stamps = [str(x) for x in t]
    print(f"\n  {tname}: {len(stamps)} values")
    for s in stamps:
        print(f"    {s}")
    uniq = sorted(set(stamps))
    print(f"\n  distinct timestamps: {len(uniq)} of {len(stamps)}")

    extra = [k for k in d.dimensions
             if k not in ("valid_time", "time", "x", "y", "latitude", "longitude")]
    if extra:
        print(f"  EXTRA DIMENSION(S) PRESENT: {extra} — the file is not flat in time")

    # monotonicity test on the first analysis
    var = "fg10" if "fg10" in d.variables else None
    if var and len(stamps) >= 3:
        a = d.variables[var][0][:]
        b = d.variables[var][1][:]
        c = d.variables[var][2][:]
        import numpy as np
        fin = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
        n = int(fin.sum())
        if n:
            nd_ab = int((b[fin] >= a[fin]).sum())
            nd_bc = int((c[fin] >= b[fin]).sum())
            print(f"\n  MONOTONICITY across the first three fields ({n:,} finite cells)")
            print(f"    field1 >= field0 : {nd_ab:,} ({100*nd_ab/n:.2f}%)")
            print(f"    field2 >= field1 : {nd_bc:,} ({100*nd_bc/n:.2f}%)")
            print(f"    100% on both     -> NESTED windows (max over 0-1, 0-2, 0-3)")
            print(f"    well under 100%  -> DISJOINT hourly windows; they tile the day")
    d.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--year", default="2018")
    ap.add_argument("--month", default="01")
    ap.add_argument("--day", default="01")
    a = ap.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"cerra_gust_ltprobe_{a.year}{a.month}{a.day}.nc"
    if out.exists():
        print(f"  already on disk: {out.name}  {out.stat().st_size/1e6:.1f} MB")
        return inspect(out)

    import cdsapi
    env = load_env(a.env)
    client = cdsapi.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                           quiet=True, progress=False)
    req = {
        "variable": ["10m_wind_gust_since_previous_post_processing"],
        "level_type": "surface_or_atmosphere",
        "data_type": "reanalysis",
        "product_type": "forecast",
        "year": [a.year], "month": [a.month], "day": [a.day],
        "time": ["00:00", "03:00", "06:00", "09:00",
                 "12:00", "15:00", "18:00", "21:00"],
        "leadtime_hour": ["1", "2", "3"],
        "data_format": "netcdf",
    }
    print(f"\n  CERRA leadtime-semantics probe — {a.year}-{a.month}-{a.day}, "
          f"8 analyses x leadtimes 1,2,3")
    print(f"  cost 144 against a limit of 90,000 (priced, not guessed). "
          f"Expect ~55 MB.\n")
    t0 = time.time()
    tmp = out.with_suffix(".part")
    try:
        client.retrieve(DS, req, str(tmp))
        tmp.rename(out)
    except Exception as ex:
        print(f"  FAILED after {(time.time()-t0)/60:.0f} min — "
              f"{type(ex).__name__}: {ex}")
        return 1
    print(f"  OK  {out.name}  {out.stat().st_size/1e6:,.1f} MB  "
          f"in {(time.time()-t0)/60:.0f} min")
    return inspect(out)


if __name__ == "__main__":
    sys.exit(main())
