#!/usr/bin/env python3
"""
Fetch CERRA gust at full temporal coverage, reduce each month to a daily
maximum, and delete the raw. 129 GB moves; about 4 GB stays.

    python3 scripts/fetch_cerra_daily_max.py --env <.env> --months 2018-01
    python3 scripts/fetch_cerra_daily_max.py --env <.env> --years 2018-2022
    python3 scripts/fetch_cerra_daily_max.py --status

WHY THE REDUCTION IS EXACT
    I2 needs the DAILY MAXIMUM gust and nothing finer: I2_raw is a mean annual
    sum over days of max(0, gust(d) - THRESHOLD), and the threshold curve needs
    the annual maximum. Both are exact functions of a daily maximum, and a daily
    maximum is a maximum of maxima over ONE variable.

    That is the case the nonlinearity rule exempts. It is not the case that
    broke the original I2 - sqrt(max u^2, max v^2) is not max sqrt(u^2+v^2),
    and because ERA5 components are signed the error there has no sign. It is
    not the I8 case either, where relative humidity from daily-mean T and Td is
    a nonlinear function of two pre-aggregated marginals. Here there is one
    variable and one monotone reduction, so nothing is lost.

WHY leadtime_hour = ["1","2","3"]
    Measured, not assumed. See doctrine/FINDING_cerra_leadtime_and_temporal_
    sampling.md. The leadtimes are DISJOINT one-hour windows - 24 distinct
    hourly stamps in a one-day probe, and monotonicity across the three fields
    at 43.5% and 48.3%, which is coin-flip and not the 100% that nested windows
    would give. Fetching only leadtime 1 samples 8 hours of 24 and leaves one
    cell in five more than 5% low on its own maximum.

THE GUST DAY RUNS 01:00 TO 00:00
    A month requested with days 1..N and leadtimes 1,2,3 returns exactly 24N
    fields, 01:00 on the 1st through 00:00 on the 1st of the next month. Each
    field is the maximum over the hour ENDING at its stamp, so it is assigned
    here to the date of (valid_time - 1 hour). That gives 24 fields per calendar
    day with no gap, no overlap and no leakage across the month boundary.

    A gust day therefore runs 01:00 UTC to 00:00 UTC the following day. The
    annual maximum is unaffected - a maximum over all hours of a year does not
    depend on how hours are binned into days. Declared, not buried.

    The script REFUSES a month that does not yield exactly 24 fields for every
    day it claims. A short day is a silent low bias in a maximum, which is the
    defect this whole exercise exists to avoid.

RESUMABILITY AND DELETION
    A month whose daily-max file already exists is skipped without a request.
    The raw file is deleted only after the daily-max file has been written,
    reopened and verified. --keep-raw suppresses the delete.

WHAT IT DOES NOT DO
    It does not derive anything and it does not touch a published record. It
    writes only under scripts/pipeline/.cache/, which is gitignored.
"""
from __future__ import annotations
import argparse, calendar, json, pathlib, re, sys, time
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
ARCHIVE = CACHE / "cerra_dmax"
DS = "reanalysis-cerra-single-levels"
VARIABLE = "10m_wind_gust_since_previous_post_processing"
FIELD = "fg10"
LEADTIMES = ["1", "2", "3"]
ANALYSES = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
PER_DAY = 24
READ_CHUNK = 48          # timesteps per read; 48 x 1069^2 float32 = 219 MB


def load_env(p):
    env = {}
    for ln in open(p, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
        if m:
            env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if not env.get("CDS_API_KEY"):
        sys.exit("CDS_API_KEY not found in the .env")
    return env


def months_from(args) -> list[tuple[int, int]]:
    out = []
    if args.months:
        for tok in args.months.split(","):
            y, m = tok.strip().split("-")
            out.append((int(y), int(m)))
    if args.years:
        a, _, b = args.years.partition("-")
        for y in range(int(a), int(b or a) + 1):
            out.extend((y, m) for m in range(1, 13))
    return sorted(set(out))


def dmax_path(y, m):
    return ARCHIVE / f"cerra_dmax_{y}{m:02d}.nc"


def raw_path(y, m):
    return CACHE / f"cerra_raw_{y}{m:02d}.nc"


def grid_path():
    return ARCHIVE / "cerra_grid.nc"


def write_grid(src):
    """Latitude and longitude are 2-D and identical in every month. Written
    once, 18 MB, instead of 18 MB x 60 inside the monthly files."""
    import netCDF4, numpy as np
    if grid_path().exists():
        return
    s = netCDF4.Dataset(str(src))
    lat = np.asarray(s.variables["latitude"][:])
    lon = np.asarray(s.variables["longitude"][:])
    s.close()
    d = netCDF4.Dataset(str(grid_path()), "w", format="NETCDF4")
    d.createDimension("y", lat.shape[0])
    d.createDimension("x", lat.shape[1])
    for name, arr, units in (("latitude", lat, "degrees_north"),
                             ("longitude", lon, "degrees_east")):
        v = d.createVariable(name, "f8", ("y", "x"), zlib=True, complevel=4)
        v.units = units
        v[:] = arr
    d.comment = ("CERRA Lambert Conformal Conic grid, 1069 x 1069 at 5.5 km. "
                 "The source netCDF carries no grid_mapping and no x/y axes; "
                 "these 2-D coordinates are the authority. Resolve cells with "
                 "scripts/resolve_cerra_cells.py, never by argmin on an axis.")
    d.close()
    print(f"    grid written  {grid_path().name}  "
          f"{grid_path().stat().st_size/1e6:.1f} MB")


def reduce_month(y, m, keep_raw, allow_short=False) -> bool:
    import netCDF4, numpy as np, cftime
    src, dst = raw_path(y, m), dmax_path(y, m)
    ndays = calendar.monthrange(y, m)[1]

    s = netCDF4.Dataset(str(src))
    tv = s.variables["valid_time"]
    stamps = cftime.num2date(tv[:], tv.units, getattr(tv, "calendar", "standard"))
    nt = len(stamps)
    expected_fields = ndays * PER_DAY
    if nt != expected_fields:
        # EXTRA fields are never acceptable — duplicates or a wrong request
        # shape are a different defect from an archive gap, and --allow-short-
        # days must not wave them through.
        if nt > expected_fields or not allow_short:
            s.close()
            print(f"    REFUSED — {nt} fields, expected {expected_fields} "
                  f"({ndays} days x {PER_DAY}). Raw kept for inspection.")
            if nt < expected_fields and not allow_short:
                print(f"    If the {expected_fields - nt} missing field(s) are "
                      f"genuinely absent from the archive rather than from this")
                print(f"    retrieval, re-run with --allow-short-days: the gap is "
                      f"then recorded in the file's own metadata instead of being")
                print(f"    lost. Verify it is a real gap first — fetch the day "
                      f"alone with probe_cerra_leadtime_semantics.py and see")
                print(f"    whether it comes back short a second time.")
            return False
        print(f"    {nt} fields, expected {expected_fields} — "
              f"{expected_fields - nt} missing. Enumerating by day.")

    # a field stamped at HH:00 is the maximum over the hour ENDING there,
    # so it belongs to the day that hour STARTED in
    day_of = np.array([(t - timedelta(hours=1)).day for t in stamps])
    mon_of = np.array([(t - timedelta(hours=1)).month for t in stamps])
    if not (mon_of == m).all():
        s.close()
        print(f"    REFUSED — {int((mon_of != m).sum())} fields fall outside "
              f"month {m:02d} after the hour-ending shift. Raw kept.")
        return False
    counts = np.bincount(day_of, minlength=ndays + 1)[1:]
    short = [(int(i + 1), int(c)) for i, c in enumerate(counts) if c != PER_DAY]
    if short and not allow_short:
        s.close()
        print(f"    REFUSED — days without exactly {PER_DAY} fields: {short}. "
              f"A short day is a silent low bias in a maximum. Raw kept.")
        return False
    if short:
        print(f"    SHORT DAYS ACCEPTED under --allow-short-days: {short}")
        print(f"    Every value on those days is a LOWER BOUND on the true")
        print(f"    maximum. Recorded in the file's short_days attribute.")

    var = s.variables[FIELD]
    ny, nx = var.shape[1], var.shape[2]
    out = np.full((ndays, ny, nx), -np.inf, dtype="float32")
    for t0 in range(0, nt, READ_CHUNK):
        blk = np.asarray(var[t0:t0 + READ_CHUNK], dtype="float32")
        for k in range(blk.shape[0]):
            d0 = day_of[t0 + k] - 1
            np.maximum(out[d0], blk[k], out=out[d0])
    s.close()

    nfin = int(np.isfinite(out).sum())
    out[~np.isfinite(out)] = np.nan

    tmp = dst.with_suffix(".part")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    d = netCDF4.Dataset(str(tmp), "w", format="NETCDF4")
    d.createDimension("day", ndays)
    d.createDimension("y", ny)
    d.createDimension("x", nx)
    dv = d.createVariable("day", "i4", ("day",))
    dv.units = f"days since {y}-{m:02d}-01"
    dv.comment = ("a gust day runs 01:00 UTC to 00:00 UTC the following day; "
                  "each hourly field is the maximum over the hour ENDING at "
                  "its stamp and is binned by the hour it started in")
    dv[:] = np.arange(ndays)
    fv = d.createVariable(FIELD, "f4", ("day", "y", "x"),
                          zlib=True, complevel=4, shuffle=True,
                          chunksizes=(1, min(214, ny), min(214, nx)))
    fv.units = "m s**-1"
    fv.long_name = ("Daily maximum of the maximum 10 metre wind gust, "
                    "over all 24 hourly windows")
    fv.cell_methods = "day: maximum"
    fv[:] = out
    d.source_dataset = DS
    d.source_variable = VARIABLE
    d.source_leadtimes = ",".join(LEADTIMES)
    d.source_analyses = ",".join(ANALYSES)
    d.reduction = ("exact: a daily maximum is a maximum of maxima over one "
                   "variable, so no information required by I2 is lost")
    d.produced_by = "scripts/fetch_cerra_daily_max.py"
    # Convention #56 — absence is recorded, never inferred from silence. A day
    # with fewer than 24 hourly windows carries a maximum that is a LOWER BOUND
    # on the truth, and the file says which days and how many fields each had,
    # so a reader who never sees this script still knows.
    d.short_days = json.dumps([{"day": dd, "fields": c, "expected": PER_DAY}
                               for dd, c in short]) if short else "[]"
    d.complete = "false" if short else "true"
    d.close()
    tmp.rename(dst)

    # reopen and verify before anything is deleted
    v = netCDF4.Dataset(str(dst))
    back = v.variables[FIELD]
    ok = (back.shape == (ndays, ny, nx))
    smp = np.asarray(back[0], dtype="float32")
    v.close()
    if not ok or not np.isfinite(smp).any():
        print(f"    WROTE BUT FAILED VERIFICATION — raw kept.")
        return False

    mb_in, mb_out = src.stat().st_size / 1e6, dst.stat().st_size / 1e6
    print(f"    reduced  {ndays} days  {nfin:,} finite cell-days  "
          f"{mb_in:,.0f} MB -> {mb_out:,.0f} MB  ({mb_in/mb_out:.1f}x)")
    write_grid(src)
    if keep_raw:
        print(f"    raw kept by --keep-raw")
    else:
        try:
            src.unlink()
            print(f"    raw deleted")
        except OSError as ex:
            # The reduction succeeded and was verified; only the cleanup
            # failed. That is a disk problem, not a data problem, so the run
            # continues rather than abandoning 59 more months - but it is
            # said loudly, because 2.15 GB per month accumulates fast.
            print(f"    RAW NOT DELETED — {type(ex).__name__}: {ex}")
            print(f"    The daily max is written and verified. Delete "
                  f"{src.name} by hand; disk will fill at ~2.15 GB/month.")
    return True


def fetch_month(client, y, m) -> bool:
    ndays = calendar.monthrange(y, m)[1]
    req = {
        "variable": [VARIABLE],
        "level_type": "surface_or_atmosphere",
        "data_type": "reanalysis",
        "product_type": "forecast",
        "year": [str(y)], "month": [f"{m:02d}"],
        "day": [f"{d:02d}" for d in range(1, ndays + 1)],
        "time": ANALYSES,
        "leadtime_hour": LEADTIMES,
        "data_format": "netcdf",
    }
    tmp = raw_path(y, m).with_suffix(".part")
    t0 = time.time()
    try:
        client.retrieve(DS, req, str(tmp))
        tmp.rename(raw_path(y, m))
    except Exception as ex:
        print(f"    FETCH FAILED after {(time.time()-t0)/3600:.1f} h — "
              f"{type(ex).__name__}: {str(ex)[:200]}")
        return False
    print(f"    fetched  {raw_path(y,m).stat().st_size/1e6:,.0f} MB  "
          f"in {(time.time()-t0)/3600:.2f} h")
    return True


def status() -> int:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    got = sorted(ARCHIVE.glob("cerra_dmax_*.nc"))
    tot = sum(p.stat().st_size for p in got) / 1e9
    print(f"\n  CERRA daily-max archive — {len(got)} of 60 months, {tot:.2f} GB")
    by_year = {}
    for p in got:
        by_year.setdefault(p.stem[-6:-2], []).append(p.stem[-2:])
    for y in sorted(by_year):
        ms = sorted(by_year[y])
        print(f"    {y}  {len(ms):>2}/12  {' '.join(ms)}")
    left = [p for p in sorted(CACHE.glob("cerra_raw_*.nc"))]
    if left:
        print(f"\n  raw files still on disk ({len(left)}):")
        for p in left:
            print(f"    {p.name}  {p.stat().st_size/1e9:.2f} GB")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env")
    ap.add_argument("--months", help="comma list, e.g. 2018-01,2018-02")
    ap.add_argument("--years", help="range, e.g. 2018-2022")
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--allow-short-days", action="store_true",
                    help="accept a month whose archive genuinely lacks an hour, "
                         "recording which days are short in the output file. "
                         "Never a default: verify the gap is in the archive and "
                         "not in the retrieval first.")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--reduce-only", action="store_true",
                    help="reduce raw files already on disk; fetch nothing")
    a = ap.parse_args()
    if a.status:
        return status()

    todo = months_from(a)
    if not todo:
        ap.error("give --months or --years (or --status)")
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    client = None
    if not a.reduce_only:
        if not a.env:
            ap.error("--env is required unless --reduce-only")
        import cdsapi
        env = load_env(a.env)
        client = cdsapi.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                               quiet=True, progress=False)

    print(f"\n  CERRA gust, leadtimes {','.join(LEADTIMES)} — "
          f"{len(todo)} month(s) requested")
    print(f"  cost 6 x 24 x days per month, well under the 90,000 limit")
    print(f"  each month is reduced to a daily maximum and the raw deleted\n")

    done = failed = skipped = 0
    for (y, m) in todo:
        tag = f"{y}-{m:02d}"
        if dmax_path(y, m).exists():
            print(f"  {tag}  already reduced — skipped")
            skipped += 1
            continue
        print(f"  {tag}")
        if not raw_path(y, m).exists():
            if a.reduce_only:
                print(f"    no raw on disk — skipped")
                skipped += 1
                continue
            if not fetch_month(client, y, m):
                failed += 1
                continue
        if reduce_month(y, m, a.keep_raw, a.allow_short_days):
            done += 1
        else:
            failed += 1

    print(f"\n  {done} reduced · {skipped} skipped · {failed} failed")
    status()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
