#!/usr/bin/env python3
"""
SUPERSEDED — DO NOT RUN. Kept for the record, not for use.

    Replaced by scripts/fetch_era5_merged.py on 2026-09-03.

WHY IT IS HERE AT ALL
    It produced the measurement that killed it: 50.1 h, 12 files of 2,065,
    5.74 files/day, 360 days to finish. FINDING_era5_fetch_not_viable.md cites
    this script by name, so a reader must be able to see what was run.

TWO REASONS NOT TO RUN IT
    1. Its plan decomposes the estate into 59 country boxes. The CDS prices
       FIELDS, not bytes — a global box costs the same as Denmark — so the
       decomposition multiplies the request count by 59 and buys nothing.
       Measured by scripts/probe_era5_area_sensitivity.py.
    2. Its dmax set fetches 10 m u and v as separate daily maxima. Combining
       them gives sqrt(max u^2, max v^2), which is NOT max sqrt(u^2+v^2). The
       components are signed, so the error has no sign: a real 20 m/s gale can
       score zero excess and a day that never gales can score 4.01 m/s-days.
       I2 cannot be built from this. See FINDING_era5_fetch_not_viable.md s4.

    Its dmean set (temperature + dewpoint, for I8) is degraded by the same rule
    — relative humidity is nonlinear in T and Td — and should not be spent
    until I8's definition is pinned.

    Only its snow and temperature requests were ever sound, and those are what
    fetch_era5_merged.py now fetches in 20 requests instead of 2,065.
"""

from __future__ import annotations
import argparse, json, os, pathlib, re, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
YEARS = None  # taken from the plan


def load_env(env_path):
    """Read the credential. Values are returned, never printed."""
    env = {}
    with open(env_path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if not env.get("CDS_API_KEY"):
        sys.exit("CDS_API_KEY not found in the .env — nothing to authenticate with")
    return env


def area(box):
    """CDS wants [north, west, south, east], and is strict about the order."""
    return [box["north"], box["west"], box["south"], box["east"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--env", default=None,
                    help="path to the pipeline .env holding CDS_API_KEY")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="submit at most N requests this run (0 = no limit)")
    ap.add_argument("--only-tag", default=None)
    ap.add_argument("--workers", type=int, default=6,
                    help="concurrent requests. Measured: one small request "
                         "takes ~864 s, almost all of it queue latency and "
                         "not transfer (the file was 0.1 MB), so this scales "
                         "close to linearly until the CDS per-user limit.")
    ap.add_argument("--only-slug", default=None)
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    years = [str(y) for y in plan["years"]]
    dataset = plan["dataset"]
    CACHE.mkdir(parents=True, exist_ok=True)

    jobs = []
    for slug, boxes in sorted(plan["boxes"].items()):
        if a.only_slug and slug != a.only_slug:
            continue
        for bi, box in enumerate(boxes):
            for rs in plan["request_sets"]:
                if a.only_tag and rs["tag"] != a.only_tag:
                    continue
                for var in rs["variables"]:
                    for yr in years:
                        short = "".join(w[0] for w in var.split("_"))[:6]
                        out = (CACHE /
                               f"era5land_{rs['tag']}_{slug}_b{bi}_{short}_{yr}.nc")
                        jobs.append((slug, bi, box, rs, var, yr, out))

    todo = [j for j in jobs if not j[6].exists()]
    by_country = {}
    for j in todo:
        by_country.setdefault(j[0], []).append(j)
    todo, queues = [], list(by_country.values())
    while any(queues):
        for q in queues:
            if q:
                todo.append(q.pop(0))
    del queues, by_country
    print(f"\n  ERA5-Land fetch — {dataset}")
    print(f"  {len(jobs)} requests in the plan · {len(jobs) - len(todo)} already on "
          f"disk · {len(todo)} to submit\n")
    if a.dry_run:
        for slug, bi, box, rs, var, yr, out in todo[:12]:
            print(f"    {rs['tag']:<6} {slug:<12} b{bi} {yr} {var[:26]:<26}"
                  f" -> {out.name}")
        if len(todo) > 12:
            print(f"    ... and {len(todo) - 12} more")
        print("\n  DRY RUN — nothing submitted")
        return 0

    import cdsapi, threading, random
    from concurrent.futures import ThreadPoolExecutor, as_completed
    env = load_env(a.env or (ROOT.parent / "SSI Index" / "SSI_v4_2 Italy Pilot"
                             / "pipeline-v4.2" / ".env"))

    # One client per worker thread. cdsapi's Client is not documented as
    # thread-safe and it carries per-request state, so sharing one across
    # threads would be trusting an undocumented property with a nine-day job.
    _local = threading.local()

    def client_for_thread():
        c = getattr(_local, "client", None)
        if c is None:
            c = cdsapi.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                              quiet=True, progress=False)
            _local.client = c
        return c

    _print_lock = threading.Lock()

    def say(msg):
        with _print_lock:
            print(msg, flush=True)

    done = failed = 0

    MONTHS = [f"{m:02d}" for m in range(1, 13)]
    DAYS = [f"{d:02d}" for d in range(1, 32)]

    def submit(client, rs, var, box, yr, months, out, attempt=0):
        """Retrieve one slice. On a cost-limit refusal, halve the months.

        CDS answers an oversized request with 403 'cost limits exceeded'. That
        is a shape problem, not an auth problem, and the only honest response
        is to make the request smaller and say how many pieces it took — not
        to give up and not to pretend the year was fetched.
        """
        req = {"variable": [var], "year": [yr], "month": months,
               "day": DAYS, "daily_statistic": rs["statistic"],
               "time_zone": "utc+00:00", "frequency": "1_hourly",
               "area": area(box), "data_format": "netcdf"}
        try:
            tmp = out.with_suffix(f".part{months[0]}")
            client.retrieve(dataset, req, str(tmp))
            return [tmp]
        except Exception as ex:
            msg = str(ex)
            if "cost limits exceeded" in msg or "too large" in msg:
                if len(months) == 1:
                    raise RuntimeError(
                        f"a single month still exceeds the cost limit for "
                        f"area {area(box)} for a SINGLE variable — the BOX "
                        f"must be split geographically") from ex
                mid = len(months) // 2
                return (submit(client, rs, var, box, yr, months[:mid], out)
                        + submit(client, rs, var, box, yr, months[mid:], out))
            # Per-user concurrency and rate limits are a queue condition, not a
            # failure: back off and retry rather than burning the job.
            transient = ("429" in msg or "too many" in msg.lower()
                         or "rate limit" in msg.lower()
                         or "503" in msg or "502" in msg)
            if transient and attempt < 5:
                time.sleep(min(300, 20 * (2 ** attempt)) * (0.7 + random.random()))
                return submit(client, rs, var, box, yr, months, out, attempt + 1)
            raise

    if a.limit:
        todo = todo[:a.limit]

    def run_one(job):
        slug, bi, box, rs, var, yr, out = job
        if out.exists():
            return ("skip", None)
        t0 = time.time()
        client = client_for_thread()
        try:
            parts = submit(client, rs, var, box, yr, MONTHS, out)
            if len(parts) == 1:
                parts[0].rename(out)
            else:
                import xarray as xr
                ds = xr.open_mfdataset([str(x) for x in parts],
                                       combine="by_coords")
                ds.to_netcdf(out)
                ds.close()
                for x in parts:
                    x.unlink()
            say(f"    OK   {rs['tag']:<6} {slug:<12} b{bi} {yr} {var[:22]:<22}"
                f"{out.stat().st_size / 1e6:8.1f} MB  "
                f"{len(parts)} call(s)  {time.time() - t0:6.0f}s")
            return ("ok", None)
        except Exception as ex:
            for stray in out.parent.glob(out.stem + ".part*"):
                try:
                    stray.unlink()
                except OSError:
                    pass
            say(f"    FAIL {rs['tag']:<6} {slug:<12} b{bi} {yr} {var[:22]:<22}"
                f"{type(ex).__name__}: {str(ex)[:300]}")
            return ("fail", None)

    say(f"  running {a.workers} concurrent requests\n")
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as pool:
        for res, _ in pool.map(run_one, todo):
            if res == "ok":
                done += 1
            elif res == "fail":
                failed += 1

    print(f"\n  fetched {done} · failed {failed} · "
          f"{len(todo) - done - failed} not reached")
    print("  re-run to retry failures; files already on disk are skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
