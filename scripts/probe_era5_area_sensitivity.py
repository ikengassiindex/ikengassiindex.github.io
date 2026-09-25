#!/usr/bin/env python3
"""
Is the CDS cost independent of AREA? Measured, not assumed. Nothing submitted.

    python3 scripts/probe_era5_area_sensitivity.py --plan <plan.json> --env <.env>

WHY
    probe_era5_cost_frontier.py priced six boxes spanning three orders of
    magnitude in area — New Zealand to Canada — and every one returned
    cost 365.0 against a limit of 400.0. That is exactly one field per day per
    variable, which says the CDS prices FIELDS and not BYTES.

    If that holds at the extreme, then a box covering a whole continent costs
    the same as a box covering Denmark, and the 59-box plan is 59 times larger
    than it needs to be. Request COUNT is the only lever on a 5.74/day queue,
    so this is the whole question.

    It is also the axis never tested. Three fetch redesigns moved variables and
    years, which the pricing rule says are the two axes that cannot move.

WHAT IT DOES
    Prices one variable, one year, at escalating areas from a single country up
    to the whole globe, and prints cost against limit. Then prices the merged
    boxes an area-free rule would allow, and states the resulting plan size.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

LADDER = [
    ("denmark alone",        [58.0,   8.0,  54.5,  15.5]),
    ("nordics",              [71.5,   4.0,  54.0,  32.0]),
    ("europe",               [72.0, -25.0,  34.0,  45.0]),
    ("europe + north africa",[72.0, -25.0,  20.0,  45.0]),
    ("north america",        [84.0,-170.0,  14.0, -52.0]),
    ("western hemisphere",   [84.0,-170.0, -56.0, -34.0]),
    ("eastern hemisphere",   [78.0, -25.0, -47.0, 180.0]),
    ("global",               [90.0,-180.0, -90.0, 180.0]),
]


def load_env(p):
    env = {}
    with open(p, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if not env.get("CDS_API_KEY"):
        sys.exit("CDS_API_KEY not found in the .env")
    return env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--variable", default="snow_depth_water_equivalent")
    ap.add_argument("--year", default="2018")
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    dataset = plan["dataset"]

    import ecmwf.datastores as ds
    env = load_env(a.env)
    client = ds.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                       progress=False)

    print(f"\n  AREA SENSITIVITY — {dataset}")
    print(f"  1 variable ({a.variable}) x 1 year ({a.year}) x escalating area")
    print(f"  NOTHING IS SUBMITTED\n")
    print(f"  {'area':<24}{'deg^2':>10}{'x denmark':>11}{'cost':>9}{'limit':>8}   verdict")

    base = None
    ok_at_global = False
    for name, ar in LADDER:
        deg2 = (ar[0] - ar[2]) * (ar[3] - ar[1])
        base = base or deg2
        req = {
            "variable": [a.variable],
            "year": [a.year],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "daily_statistic": "daily_maximum",
            "time_zone": "utc+00:00",
            "frequency": "1_hourly",
            "area": ar,
            "data_format": "netcdf",
        }
        try:
            r = client.estimate_costs(dataset, req)
        except Exception as ex:
            print(f"  {name:<24}{deg2:>10.0f}{deg2/base:>10.0f}x"
                  f"   ESTIMATE FAILED {type(ex).__name__}: {str(ex)[:120]}")
            continue
        cost = r.get("cost") if isinstance(r, dict) else None
        limit = r.get("limit") if isinstance(r, dict) else None
        ok = cost is not None and limit and cost <= limit
        if ok and name == "global":
            ok_at_global = True
        print(f"  {name:<24}{deg2:>10.0f}{deg2/base:>10.0f}x{cost:>9}{limit:>8}"
              f"   {'ACCEPTED' if ok else 'OVER LIMIT'}")

    nb = sum(len(v) for v in plan["boxes"].values())
    ny = len(plan["years"])
    nv = sum(len(rs["variables"]) for rs in plan["request_sets"])
    print(f"\n  PLAN SIZE UNDER EACH RULE")
    print(f"    today            {nb} boxes x {ny} years x {nv} variables"
          f" = {nb*ny*nv:>6} requests")
    for k, label in ((5, "5 regional boxes"), (2, "2 hemisphere boxes"),
                     (1, "1 global box")):
        print(f"    {label:<17}{k} box{'es' if k>1 else '  '} x {ny} years x "
              f"{nv} variables = {k*ny*nv:>6} requests"
              f"   ~{k*ny*nv/5.74:>5.0f} days at the measured 5.74/day")
    if ok_at_global:
        print("\n  A global box prices the same as Denmark. Area is free; the")
        print("  59-box decomposition is buying nothing and costing 59x.")
    print("\n  Cost is fields, not bytes. Bytes are still real and land on disk —")
    print("  size must be measured separately before any of this is acted on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
