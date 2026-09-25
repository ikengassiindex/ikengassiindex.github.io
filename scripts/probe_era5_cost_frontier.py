#!/usr/bin/env python3
"""
Ask the CDS what each candidate request COSTS, without submitting any of them.

    python3 scripts/probe_era5_cost_frontier.py --plan <plan.json>
    python3 scripts/probe_era5_cost_frontier.py --plan <plan.json> --boxes 6

WHY THIS EXISTS
    The fetch failed at 5.74 files/day because queue latency is per-request and
    independent of payload. Request COUNT is the only lever. Packing more into
    each request is the only way to pull the count down, and the binding limit
    is the CDS cost limit, which we have only ever discovered by being refused.

    ecmwf-datastores-client exposes estimate_costs(). It prices a request
    server-side and returns the limit alongside it. Nothing is queued, nothing
    is downloaded, no job is created. So the entire packing frontier can be
    mapped in minutes instead of being discovered one 24-hour rejection at a
    time.

WHAT IT DOES
    For each sampled box, walks a ladder of (variables x years) packings and
    records cost, limit and whether it would be accepted. Prints the largest
    accepted packing per box, and what the whole plan would cost at that
    packing.

    It probes the SOUND sets only. Per FINDING_era5_fetch_not_viable.md s4 the
    10 m u/v sets buy a quantity whose error has no sign, so they are excluded
    here rather than being priced as though they were usable. Pass
    --include-wind to price them anyway.

THE CREDENTIAL
    Read from the pipeline .env as CDS_API_KEY / CDS_API_URL and handed
    straight to the client. Never printed, never logged, never written to any
    output of this script.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIND = ("10m_u_component_of_wind", "10m_v_component_of_wind")


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


def build(rs, box, years, nvar, nyear):
    return {
        "variable": rs["variables"][:nvar],
        "year": [str(y) for y in years[:nyear]],
        "month": [f"{m:02d}" for m in range(1, 13)],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "daily_statistic": rs["statistic"],
        "time_zone": "utc+00:00",
        "frequency": "1_hourly",
        "area": [box["north"], box["west"], box["south"], box["east"]],
        "data_format": "netcdf",
    }


def span(box):
    return (box["north"] - box["south"]) * (box["east"] - box["west"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--env", default=None)
    ap.add_argument("--boxes", type=int, default=6,
                    help="how many boxes to sample, spread by area")
    ap.add_argument("--include-wind", action="store_true")
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    years = plan["years"]
    dataset = plan["dataset"]

    sets = []
    for rs in plan["request_sets"]:
        v = list(rs["variables"])
        if not a.include_wind:
            v = [x for x in v if x not in WIND]
        if v:
            sets.append({**rs, "variables": v})

    flat = [(slug, i, b) for slug, bs in plan["boxes"].items()
            for i, b in enumerate(bs)]
    flat.sort(key=lambda t: span(t[2]))
    if a.boxes and a.boxes < len(flat):
        step = (len(flat) - 1) / (a.boxes - 1)
        flat = [flat[round(i * step)] for i in range(a.boxes)]

    import ecmwf.datastores as ds
    env = load_env(a.env or (ROOT.parent / "SSI Index" / "SSI_v4_2 Italy Pilot"
                             / "pipeline-v4.2" / ".env"))
    client = ds.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                       progress=False)

    print(f"\n  CDS cost frontier — {dataset}")
    print(f"  {len(flat)} boxes sampled by area · sets "
          f"{[s['tag'] for s in sets]} · NOTHING IS SUBMITTED\n")

    best = {}
    for slug, bi, box in flat:
        for rs in sets:
            nv = len(rs["variables"])
            top = None
            for nvar in range(1, nv + 1):
                for nyear in range(1, len(years) + 1):
                    req = build(rs, box, years, nvar, nyear)
                    try:
                        r = client.estimate_costs(dataset, req)
                    except Exception as ex:
                        print(f"    {slug:<14} {rs['tag']:<6} {nvar}v x {nyear}y  "
                              f"ESTIMATE FAILED {type(ex).__name__}: {str(ex)[:200]}")
                        continue
                    cost = r.get("cost") if isinstance(r, dict) else None
                    limit = r.get("limit") if isinstance(r, dict) else None
                    ok = (cost is not None and limit and cost <= limit)
                    mark = "ok " if ok else "OVER"
                    print(f"    {slug:<14} {rs['tag']:<6} {nvar}v x {nyear}y  "
                          f"cost {cost}  limit {limit}  {mark}"
                          + ("" if isinstance(r, dict) and "cost" in r
                             else f"  raw={r}"))
                    if ok:
                        top = (nvar, nyear)
            best[(slug, bi, rs["tag"])] = top

    print("\n  LARGEST ACCEPTED PACKING PER SAMPLED BOX")
    print(f"  {'country':<14}{'box':>4}{'set':>8}{'vars':>6}{'years':>7}"
          f"{'reqs for that set':>20}")
    for (slug, bi, tag), top in sorted(best.items()):
        nv = len(next(s for s in sets if s["tag"] == tag)["variables"])
        if top is None:
            print(f"  {slug:<14}{bi:>4}{tag:>8}{'-':>6}{'-':>7}"
                  f"{'NOTHING ACCEPTED':>20}")
            continue
        import math
        n = math.ceil(nv / top[0]) * math.ceil(len(years) / top[1])
        print(f"  {slug:<14}{bi:>4}{tag:>8}{top[0]:>6}{top[1]:>7}{n:>20}")

    print("\n  Read this as the frontier, not the plan. Boxes were sampled by")
    print("  area; the plan is rebuilt only after every box is priced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
