#!/usr/bin/env python3
"""
Check a written daily-max month against the raw it came from, independently of
the code that wrote it.

    python3 scripts/verify_cerra_dmax.py --month 2018-01

WHY, WHEN THE REDUCER ALREADY VERIFIES
    The reducer reopens what it wrote and checks the shape and that the data is
    finite. That catches a truncated write. It cannot catch a wrong ANSWER,
    because it is the same code path that produced the answer: if the day
    binning is off by one, the reducer will happily confirm a well-formed file
    full of the wrong maxima.

    scripts/test_cerra_reducer.py tests the logic on synthetic months where the
    answer is known by construction, and 12 of 12 pass. This is the other half:
    the real CERRA month, real gusts, real time stamps, recomputed by brute
    force from the raw with none of the reducer's machinery.

    It is the reason month one is fetched with --keep-raw. Once it passes, the
    remaining months delete their raw as they go.

WHAT IT CHECKS

    C1 exact equality        for a sample of days, recompute the maximum over
                             that day's 24 hourly fields directly from the raw,
                             by brute force, and require EXACT equality with
                             the stored daily max at every cell
    C2 boundary day          the last day of the month specifically, because it
                             is the one whose 24th field is stamped 00:00 on the
                             1st of the NEXT month. If that field were binned
                             forward, the last day would be quietly low
    C3 first day             the first day specifically, because it is the one
                             that could be short: the hour 00:00-01:00 belongs
                             to the previous month's last analysis and is
                             absent by design
    C4 no ceiling            the stored month maximum equals the raw month
                             maximum, so nothing was clipped or saturated
    C5 physical range        values lie in a range a 10 m gust can occupy.
                             A wide bound - this catches unit errors and fill
                             values, not meteorology

    C1 on every day is the strongest form and costs one full pass of the raw.
    --days controls the sample; the default is every day, because month one is
    the month that licences the other 59.
"""
from __future__ import annotations
import argparse, calendar, pathlib, sys
from datetime import timedelta

import numpy as np
import netCDF4, cftime

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
ARCHIVE = CACHE / "cerra_dmax"
GUST_MIN, GUST_MAX = 0.0, 130.0     # m/s. The world record gust is ~113 m/s.


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True, help="YYYY-MM")
    ap.add_argument("--days", type=int, default=0,
                    help="sample this many days (0 = all)")
    a = ap.parse_args()
    y, m = (int(x) for x in a.month.split("-"))
    ndays = calendar.monthrange(y, m)[1]

    raw = CACHE / f"cerra_raw_{y}{m:02d}.nc"
    dmx = ARCHIVE / f"cerra_dmax_{y}{m:02d}.nc"
    for p in (raw, dmx):
        if not p.exists():
            sys.exit(f"missing {p.name} — this check needs the raw, so run the "
                     f"fetch with --keep-raw")

    R = netCDF4.Dataset(str(raw))
    D = netCDF4.Dataset(str(dmx))
    rv, dv = R.variables["fg10"], D.variables["fg10"]
    tv = R.variables["valid_time"]
    stamps = cftime.num2date(tv[:], tv.units, getattr(tv, "calendar", "standard"))
    day_of = np.array([(t - timedelta(hours=1)).day for t in stamps])

    print(f"\n  VERIFY {dmx.name} against {raw.name}")
    print(f"  raw {rv.shape}  ->  daily max {dv.shape}   {ndays} days expected")

    results = []

    def check(name, ok, detail="", skipped=False):
        # A check that cannot fail is not a check. C4 is only meaningful over
        # the whole month, so on a partial sample it is reported SKIP and
        # counted as not run - never PASS. This is the exact defect that let
        # mosaic attempt 2 clear three bars while measuring the wrong thing.
        results.append((name, None if skipped else ok))
        tag = "SKIP" if skipped else ("PASS" if ok else "FAIL")
        print(f"  {tag}  {name}" + (f"   {detail}" if detail else ""))

    check("shape — one slice per calendar day",
          dv.shape[0] == ndays, f"{dv.shape[0]} of {ndays}")

    order = list(range(1, ndays + 1))
    if a.days:
        rng = np.random.default_rng(20260910)
        must = {1, ndays}
        rest = [d for d in order if d not in must]
        order = sorted(must | set(rng.permutation(rest)[:max(0, a.days - 2)].tolist()))

    worst = 0.0
    bad_days = []
    mmax_raw = -np.inf
    for d in order:
        idx = np.flatnonzero(day_of == d)
        if len(idx) != 24:
            bad_days.append((d, f"{len(idx)} fields"))
            continue
        acc = None
        for k in idx:                       # brute force, no reducer machinery
            f = np.asarray(rv[int(k)], dtype="float32")
            acc = f if acc is None else np.maximum(acc, f)
        got = np.asarray(dv[d - 1], dtype="float32")
        mmax_raw = max(mmax_raw, float(np.nanmax(acc)))
        fin = np.isfinite(acc) | np.isfinite(got)
        if not np.array_equal(np.nan_to_num(acc, nan=-9e9),
                              np.nan_to_num(got, nan=-9e9)):
            diff = float(np.nanmax(np.abs(acc - got)))
            worst = max(worst, diff)
            bad_days.append((d, f"max abs diff {diff:g}"))

    check(f"C1 exact equality — {len(order)} day(s) recomputed by brute force",
          not bad_days, "all cells identical" if not bad_days else f"{bad_days[:5]}")
    check("C2 boundary day — the last day, whose 24th field is stamped "
          "00:00 of the next month",
          ndays in order and not any(d == ndays for d, _ in bad_days))
    check("C3 first day — short by design in hour 00:00-01:00, still 24 fields",
          int((day_of == 1).sum()) == 24, f"{int((day_of == 1).sum())} fields")

    dmax_all = float(np.nanmax(np.asarray(dv[:], dtype="float32")))
    full = len(order) == ndays
    check("C4 no ceiling — stored month max equals raw month max",
          full and abs(dmax_all - mmax_raw) < 1e-6,
          f"stored {dmax_all:.4f}  raw {mmax_raw:.4f}"
          + ("" if full else f"   only {len(order)} of {ndays} days read, so "
                             f"the raw figure is not the month max — "
                             f"re-run without --days"),
          skipped=not full)

    dmin = float(np.nanmin(np.asarray(dv[:], dtype="float32")))
    check("C5 physical range — a 10 m gust, not a unit error or a fill value",
          GUST_MIN <= dmin and dmax_all <= GUST_MAX,
          f"{dmin:.3f} .. {dmax_all:.3f} m/s")

    R.close(); D.close()
    bad = [n for n, ok in results if ok is False]
    skip = [n for n, ok in results if ok is None]
    print()
    print(f"  {sum(1 for _, ok in results if ok)} passed · {len(bad)} failed "
          f"· {len(skip)} not run")
    if bad:
        print(f"  FAILED: {bad}")
        print(f"  Do NOT release the remaining months. The raw is still on disk.")
        return 1
    if skip:
        print(f"  NOT RUN: {skip}")
        print(f"  A partial verification does not licence 59 more months.")
        print(f"  Re-run without --days before releasing them.")
        return 2
    print(f"  {dmx.name} reproduces the raw exactly, on every day of the month.")
    print(f"  The reducer may run the remaining months and delete as it goes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
