#!/usr/bin/env python3
"""
Fetch a merged-region ERA5 plan. Resumable, concurrent, refuses loudly.

    python3 scripts/fetch_era5_merged.py --plan <merged.json> --env <.env> --dry-run
    python3 scripts/fetch_era5_merged.py --plan <merged.json> --env <.env> --workers 5

WHY THE PLAN LOOKS LIKE THIS
    The CDS prices FIELDS, not bytes: cost = variables x days, and AREA DOES
    NOT ENTER. A global box prices 365.0 against a limit of 400.0 — the same as
    Denmark. Measured, not inferred; see probe_era5_area_sensitivity.py.

    Queue latency is per-request and was measured at a 23.8 h median over 12
    files, independent of payload from 0.1 MB to 154 MB. Throughput is
    therefore workers / latency, and request COUNT is the only lever. Merging
    59 boxes into a handful takes the count from 2,065 to tens.

    Note the extrapolation this run tests: latency was measured up to 154 MB
    and these requests are ~1 GB. If latency turns out to scale with size after
    all, the first completion will say so and this plan needs re-cutting, not
    re-running.

NAMING
    era5land_<tag>_<region>_<variable-abbr>_<year>.nc

    A different scheme from the 193 cached era5land_daily_max_<slug>_<year>.nc
    files that I3 and I5 are derived from. Nothing here overwrites those.

DERIVATION CHANGES DOWNSTREAM
    A merged file spans many countries, so the derivation reads one regional
    field and samples at each substation's grid cell, rather than opening a
    per-country box. That is a real change to the I1 code path and is NOT done
    by this script.

THE CREDENTIAL
    Read from the .env as CDS_API_KEY / CDS_API_URL and handed straight to the
    client. Never printed, never logged, never written to any output.

CONVENTION #56
    A failed request is recorded and the run continues. Nothing is defaulted,
    nothing synthesised, a partial fetch is reported as partial. Re-running
    skips what is on disk.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
PRINT = threading.Lock()


def abbr(v):
    return "".join(w[0] for w in v.split("_"))[:6]


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


def say(*a):
    with PRINT:
        print(*a, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--env", required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    years = [str(y) for y in plan["years"]]
    CACHE.mkdir(parents=True, exist_ok=True)

    jobs = []
    for r in plan["regions"]:
        for y in years:
            for v in plan["variables"]:
                out = CACHE / f"era5land_{plan['tag']}_{r['id']}_{abbr(v)}_{y}.nc"
                jobs.append((r, y, v, out))
    todo = [j for j in jobs if not j[3].exists()]

    print(f"\n  {plan['dataset']} — {plan['tag']}")
    print(f"  {len(plan['regions'])} regions x {len(years)} years x "
          f"{len(plan['variables'])} variables = {len(jobs)} requests")
    print(f"  {len(jobs)-len(todo)} on disk · {len(todo)} to submit · "
          f"est {plan.get('est_total_gb','?')} GB total\n")
    if a.dry_run:
        for r, y, v, out in todo:
            print(f"    {r['id']}  {y}  {v:<32} "
                  f"[{r['north']},{r['west']},{r['south']},{r['east']}]  "
                  f"~{r['est_mb_per_variable_year']:.0f} MB -> {out.name}")
        print("\n  DRY RUN — nothing submitted")
        return 0

    import cdsapi
    env = load_env(a.env)
    local = threading.local()

    def client():
        if not hasattr(local, "c"):
            local.c = cdsapi.Client(url=env.get("CDS_API_URL"),
                                    key=env["CDS_API_KEY"],
                                    quiet=True, progress=False)
        return local.c

    def run(job):
        r, y, v, out = job
        req = {"variable": [v], "year": [y],
               "month": [f"{m:02d}" for m in range(1, 13)],
               "day": [f"{d:02d}" for d in range(1, 32)],
               "daily_statistic": plan["statistic"],
               "time_zone": "utc+00:00", "frequency": "1_hourly",
               "area": [r["north"], r["west"], r["south"], r["east"]],
               "data_format": "netcdf"}
        t0 = time.time()
        tmp = out.with_suffix(".part")
        try:
            client().retrieve(plan["dataset"], req, str(tmp))
            tmp.rename(out)
            mb = out.stat().st_size / 1e6
            say(f"    OK   {r['id']} {y} {abbr(v):<6} {mb:9.1f} MB "
                f"(est {r['est_mb_per_variable_year']:.0f})  "
                f"{(time.time()-t0)/3600:5.1f} h")
            return ("ok", mb, time.time() - t0)
        except Exception as ex:
            # Convention #56: say what failed, in full, and carry on.
            say(f"    FAIL {r['id']} {y} {abbr(v):<6} "
                f"{(time.time()-t0)/3600:5.1f} h  {type(ex).__name__}: {ex}")
            return ("fail", 0.0, time.time() - t0)

    say(f"  submitting with {a.workers} workers — first completion is the one "
        f"that matters, it tests whether latency scales with size\n")
    res = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run, j) for j in todo]
        for f in as_completed(futs):
            res.append(f.result())
    ok = [r for r in res if r[0] == "ok"]
    say(f"\n  fetched {len(ok)} · failed {len(res)-len(ok)} · "
        f"{len(todo)-len(res)} not attempted")
    if ok:
        hrs = sorted(r[2] / 3600 for r in ok)
        say(f"  wall time  min {hrs[0]:.1f} h  median {hrs[len(hrs)//2]:.1f} h  "
            f"max {hrs[-1]:.1f} h   total {sum(r[1] for r in ok)/1000:.1f} GB")
    say("  re-run to retry failures; files on disk are skipped")
    return 1 if len(ok) != len(res) else 0


if __name__ == "__main__":
    sys.exit(main())
