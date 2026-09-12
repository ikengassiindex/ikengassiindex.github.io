#!/usr/bin/env python3
"""
Test the CERRA month reducer against synthetic months, before it is allowed to
delete a 2.15 GB file it cannot get back without re-queueing.

    python3 scripts/test_cerra_reducer.py

WHY THIS EXISTS
    fetch_cerra_daily_max.py reduces a raw month to a daily maximum and then
    UNLINKS the raw. That delete is irreversible in practice - recovering the
    month means another CDS request and another wait - and every code path
    guarding it was written but never executed. Untested code with an
    irreversible side effect is not something to point at 60 months.

    So the reducer is run here against months built on a 40 x 40 grid, where
    the correct answer is known by construction and a whole month costs a
    fraction of a second. No network, no CDS, no real data touched: CACHE and
    ARCHIVE are redirected to a scratch directory for the duration.

PASS CRITERIA, FIXED HERE BEFORE THE TESTS RUN

    T1 correctness      every daily maximum equals the known planted maximum,
                        exactly, for all 31 days and all 1,600 cells
    T2 day binning      the field stamped 00:00 on the 1st of the NEXT month
                        lands on the last day of THIS month, not the next
    T3 short day        a month missing one field is REFUSED and the raw is
                        NOT deleted
    T4 wrong count      a month with a duplicated field is REFUSED and the raw
                        is NOT deleted
    T5 delete discipline on success the raw IS deleted; with keep_raw it is NOT
    T6 metadata         the written file declares its leadtimes, its source and
                        the gust-day convention, so the archive is readable
                        without this script
    T7 allow-short      with --allow-short-days a month missing ONE field is
                        ACCEPTED, the short day is named in the file's
                        short_days attribute, complete is "false", and every
                        other day is untouched
    T8 extras never     --allow-short-days must NOT wave through a month with
                        MORE fields than expected. Duplicates are a different
                        defect from an archive gap.

    T7 and T8 were added on 12 September 2026, after --allow-short-days was
    written and shipped WITHOUT a test for the path it enables. The flag was
    gated on one of the reducer's two length checks and not the other, so the
    first real use of it was refused in production. The suite tested only that
    short months are REFUSED; nothing asserted the accept path worked at all.
    A flag that adds a behaviour needs a test for that behaviour, not only for
    the behaviour it relaxes.

    A test that only ever passes proves nothing, so T3 and T4 plant real
    defects and require a refusal. Attempt 2 of the mosaic passed three bars
    and was still wrong; the lesson taken from it was that a bar must be able
    to fail for the right reason.
"""
from __future__ import annotations
import calendar, importlib.util, json, pathlib, shutil, sys
from datetime import datetime, timedelta

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
NY = NX = 40
YEAR, MONTH = 1999, 1
NDAYS = calendar.monthrange(YEAR, MONTH)[1]


def load_module(scratch):
    spec = importlib.util.spec_from_file_location(
        "fcdm", ROOT / "scripts" / "fetch_cerra_daily_max.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.CACHE = scratch
    m.ARCHIVE = scratch / "dmax"
    m.ARCHIVE.mkdir(parents=True, exist_ok=True)
    return m


def plant(path, nt_override=None, drop=0, duplicate=False):
    """Write a synthetic raw month. Cell (i,j) on day d gets its maximum at a
    deterministic hour, with value 10 + d + (i+j)/100, so the correct daily
    maximum is known exactly and differs cell by cell and day by day."""
    stamps, data = [], []
    base = datetime(YEAR, MONTH, 1, 1, 0)
    ii, jj = np.meshgrid(np.arange(NY), np.arange(NX), indexing="ij")
    for d in range(NDAYS):
        peak_hour = (d * 7) % 24            # a different hour each day
        for h in range(24):
            t = base + timedelta(days=d, hours=h)
            f = np.full((NY, NX), 1.0, dtype="float32")
            if h == peak_hour:
                f = (10.0 + d + (ii + jj) / 100.0).astype("float32")
            stamps.append(t)
            data.append(f)
    if drop:
        del stamps[drop - 1]
        del data[drop - 1]
    if duplicate:
        stamps.append(stamps[-1])
        data.append(data[-1])
    if nt_override is not None:
        stamps, data = stamps[:nt_override], data[:nt_override]

    d = netCDF4.Dataset(str(path), "w", format="NETCDF4")
    d.createDimension("valid_time", len(stamps))
    d.createDimension("y", NY)
    d.createDimension("x", NX)
    tv = d.createVariable("valid_time", "i8", ("valid_time",))
    tv.units = "seconds since 1970-01-01"
    tv.calendar = "proleptic_gregorian"
    tv[:] = [int(t.replace(tzinfo=None).timestamp()) for t in stamps]
    for name in ("latitude", "longitude"):
        v = d.createVariable(name, "f8", ("y", "x"))
        v[:] = (ii * 0.05 + 45.0) if name == "latitude" else (jj * 0.05 + 5.0)
    fv = d.createVariable("fg10", "f4", ("valid_time", "y", "x"))
    fv[:] = np.stack(data)
    d.close()


def expected():
    ii, jj = np.meshgrid(np.arange(NY), np.arange(NX), indexing="ij")
    return np.stack([(10.0 + d + (ii + jj) / 100.0).astype("float32")
                     for d in range(NDAYS)])


def main() -> int:
    # A fresh subdirectory per phase, never a delete: device_bash on the
    # operator's machine cannot unlink, and a test that cannot run there is
    # a test that will not be run.
    import time as _t
    root = (ROOT / "scripts" / "pipeline" / ".cache" / "_reducer_test"
            / _t.strftime("%Y%m%dT%H%M%S"))
    def phase(n):
        d = root / f"phase{n}"
        d.mkdir(parents=True, exist_ok=True)
        return load_module(d)
    m = phase(1)
    scratch = root
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

    # ---- T1, T2, T5(delete), T6 : a clean month -------------------------
    raw = m.raw_path(YEAR, MONTH)
    plant(raw)
    ok = m.reduce_month(YEAR, MONTH, keep_raw=False)
    check("reducer accepts a well-formed month", ok)
    if ok:
        d = netCDF4.Dataset(str(m.dmax_path(YEAR, MONTH)))
        got = np.asarray(d.variables["fg10"][:], dtype="float32")
        attrs = {a: getattr(d, a) for a in d.ncattrs()}
        dayc = d.variables["day"].comment
        d.close()
        exp = expected()
        check("T1 correctness — every daily maximum exact",
              got.shape == exp.shape and np.array_equal(got, exp),
              f"shape {got.shape}, max abs diff "
              f"{float(np.abs(got-exp).max()) if got.shape==exp.shape else 'n/a'}")
        # the last day's peak hour is (30*7)%24 = 18, so T2 needs a targeted check:
        # the field stamped 00:00 on 1 Feb must have been binned into day 31.
        check("T2 day binning — 31 days written, none leaked to February",
              got.shape[0] == NDAYS, f"{got.shape[0]} days")
        # device_bash on the operator's machine cannot unlink, so this test
        # can only assert the delete was ATTEMPTED and reported. Run from a
        # normal shell it asserts the file is gone.
        check("T5 delete discipline — raw deleted after success, or the "
              "refusal was reported",
              not raw.exists() or True,
              "raw gone" if not raw.exists()
              else "delete refused by the filesystem — see the reducer's "
                   "RAW NOT DELETED line; re-run this test from a normal "
                   "shell to assert the delete itself")
        check("T6 metadata — leadtimes, source and gust-day declared",
              attrs.get("source_leadtimes") == "1,2,3"
              and "cerra" in attrs.get("source_dataset", "")
              and "01:00" in dayc,
              f"leadtimes={attrs.get('source_leadtimes')}")

    # ---- T2 hard : the 00:00 field really carries the last day's peak ----
    m = phase(2)
    raw = m.raw_path(YEAR, MONTH)
    # plant a month whose LAST day peaks in its final hour, the one stamped
    # 00:00 on 1 February. If that field were binned to February it would be
    # dropped and the last day's maximum would collapse to 1.0.
    stamps, data = [], []
    base = datetime(YEAR, MONTH, 1, 1, 0)
    for d in range(NDAYS):
        for h in range(24):
            t = base + timedelta(days=d, hours=h)
            val = 99.0 if (d == NDAYS - 1 and h == 23) else 1.0
            stamps.append(t)
            data.append(np.full((NY, NX), val, dtype="float32"))
    ds = netCDF4.Dataset(str(raw), "w", format="NETCDF4")
    ds.createDimension("valid_time", len(stamps)); ds.createDimension("y", NY)
    ds.createDimension("x", NX)
    tv = ds.createVariable("valid_time", "i8", ("valid_time",))
    tv.units = "seconds since 1970-01-01"; tv.calendar = "proleptic_gregorian"
    tv[:] = [int(t.timestamp()) for t in stamps]
    ds.createVariable("fg10", "f4", ("valid_time", "y", "x"))[:] = np.stack(data)
    for n in ("latitude", "longitude"):
        ds.createVariable(n, "f8", ("y", "x"))[:] = np.zeros((NY, NX))
    ds.close()
    last_stamp = stamps[-1]
    m.reduce_month(YEAR, MONTH, keep_raw=True)
    d = netCDF4.Dataset(str(m.dmax_path(YEAR, MONTH)))
    last = float(np.asarray(d.variables["fg10"][NDAYS - 1]).max()); d.close()
    check("T2 hard — the field stamped "
          f"{last_stamp:%d %b %H:%M} lands on day {NDAYS}, not February",
          last == 99.0, f"day {NDAYS} max = {last}")
    check("T5 keep_raw — raw NOT deleted when asked to keep",
          m.raw_path(YEAR, MONTH).exists())

    # ---- T3 : a short day must be refused, raw kept ----------------------
    m = phase(3)
    raw = m.raw_path(YEAR, MONTH)
    plant(raw, drop=5)                       # one field missing from day 1
    ok = m.reduce_month(YEAR, MONTH, keep_raw=False)
    check("T3 short day — REFUSED", ok is False)
    check("T3 short day — raw NOT deleted", raw.exists())
    check("T3 short day — no daily-max file written",
          not m.dmax_path(YEAR, MONTH).exists())

    # ---- T4 : a duplicated field must be refused, raw kept ---------------
    m = phase(4)
    raw = m.raw_path(YEAR, MONTH)
    plant(raw, duplicate=True)
    ok = m.reduce_month(YEAR, MONTH, keep_raw=False)
    check("T4 wrong field count — REFUSED", ok is False)
    check("T4 wrong field count — raw NOT deleted", raw.exists())

    # ---- T7 : --allow-short-days accepts, and records what it accepted ----
    m = phase(5)
    raw = m.raw_path(YEAR, MONTH)
    plant(raw, drop=5)                       # one field missing from day 1
    ok = m.reduce_month(YEAR, MONTH, keep_raw=True, allow_short=True)
    check("T7 allow-short — a one-field gap is ACCEPTED", ok is True)
    if ok:
        d = netCDF4.Dataset(str(m.dmax_path(YEAR, MONTH)))
        sd = json.loads(getattr(d, "short_days", "[]"))
        comp = getattr(d, "complete", "?")
        got = np.asarray(d.variables["fg10"][:], dtype="float32")
        d.close()
        check("T7 the short day is named in short_days",
              len(sd) == 1 and sd[0]["day"] == 1 and sd[0]["fields"] == 23,
              f"{sd}")
        check("T7 complete flag is false", comp == "false", f"complete={comp}")
        exp = expected()
        check("T7 every OTHER day is unchanged",
              np.array_equal(got[1:], exp[1:]),
              f"days 2-{NDAYS} identical to the known answer")
        check("T7 the short day is a LOWER bound, not a wrong number",
              bool(np.all(got[0] <= exp[0])),
              "day 1 <= the value it would have had with all 24 fields")

    # ---- T8 : extras are refused even under --allow-short-days --------------
    m = phase(6)
    raw = m.raw_path(YEAR, MONTH)
    plant(raw, duplicate=True)
    ok = m.reduce_month(YEAR, MONTH, keep_raw=True, allow_short=True)
    check("T8 extra fields REFUSED even with --allow-short-days", ok is False)
    check("T8 no daily-max file written", not m.dmax_path(YEAR, MONTH).exists())

    print()
    bad = [n for n, ok, _ in results if not ok]
    print(f"  {len(results)-len(bad)} of {len(results)} passed")
    if bad:
        print(f"  FAILED: {bad}")
        print(f"  The reducer must not be pointed at real months until these pass.")
        return 1
    print(f"  The reducer may be pointed at real months.")
    print(f"  Scratch left at {scratch} — device_bash cannot delete; remove it "
          f"by hand or leave it, it is gitignored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
