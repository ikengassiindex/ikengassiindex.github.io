#!/usr/bin/env python3
"""
Fetch ONE month of CERRA gust over the full domain, and measure it.

    python3 scripts/probe_cerra_one_month.py --env <.env>

WHY A PROBE AND NOT THE PLAN
    Everything about CERRA that can be established without spending queue has
    been: cost 17,520 for a full variable-year against a limit of 90,000, so a
    year fits in one request; area is free, as on ERA5; the domain covers
    513,554 of 622,104 substations (82.6 per cent).

    Two things cannot be established that way.

    BYTES. 1069 x 1069 cells x 8 analyses/day is ~13 GB per variable-year
    uncompressed. What netCDF compression does to a gust field is a guess, and
    a guess is what produced the 8 GB estimate for a fetch that came in at 3.1.

    LATENCY. Every CERRA request is far larger than anything measured so far —
    the largest ERA5 file this estate has fetched is 237 MB. Queue latency was
    measured as independent of payload from 0.1 MB to 154 MB. Whether that
    holds at 1 GB is an extrapolation beyond the measured range.

    So: one month, full domain, measured. Then the plan is built on numbers.

WHAT IT DOES NOT DO
    It does not derive anything and it does not touch a published record. It
    writes one file to the cache and prints its size, its grid, and the wall
    time it took.
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--year", default="2018")
    ap.add_argument("--month", default="01")
    a = ap.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"cerra_gust_probe_{a.year}{a.month}.nc"
    if out.exists():
        print(f"  already on disk: {out.name}  {out.stat().st_size/1e6:.1f} MB")
        return 0

    import cdsapi
    env = load_env(a.env)
    client = cdsapi.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                           quiet=True, progress=False)
    req = {
        "variable": ["10m_wind_gust_since_previous_post_processing"],
        "level_type": "surface_or_atmosphere",
        "data_type": "reanalysis",
        "product_type": "forecast",
        "year": [a.year],
        "month": [a.month],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": ["00:00", "03:00", "06:00", "09:00",
                 "12:00", "15:00", "18:00", "21:00"],
        "leadtime_hour": ["1"],
        "data_format": "netcdf",
    }
    print(f"\n  CERRA probe — {a.year}-{a.month}, full domain, 8 analyses/day")
    print(f"  cost 1,488 against a limit of 90,000. Submitting one request.\n")
    t0 = time.time()
    tmp = out.with_suffix(".part")
    try:
        client.retrieve(DS, req, str(tmp))
        tmp.rename(out)
    except Exception as ex:
        print(f"  FAILED after {(time.time()-t0)/3600:.1f} h — "
              f"{type(ex).__name__}: {ex}")
        return 1
    mb = out.stat().st_size / 1e6
    hrs = (time.time() - t0) / 3600
    print(f"  OK  {out.name}  {mb:,.1f} MB  in {hrs:.1f} h")
    print(f"\n  EXTRAPOLATION FROM THIS ONE MEASUREMENT")
    print(f"    per variable-year : {mb*12/1000:,.1f} GB")
    print(f"    5 years           : {mb*60/1000:,.1f} GB")
    print(f"    (state it as extrapolated until a second month confirms it)")
    try:
        import netCDF4, numpy as np
        d = netCDF4.Dataset(str(out))
        print(f"\n  dimensions: { {k: len(v) for k, v in d.dimensions.items()} }")
        print(f"  variables : {[k for k in d.variables]}")
        for k in ("latitude", "longitude", "x", "y"):
            if k in d.variables:
                v = d.variables[k]
                print(f"    {k}: shape {v.shape}")
        d.close()
    except Exception as ex:
        print(f"  could not inspect: {type(ex).__name__}: {ex}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
