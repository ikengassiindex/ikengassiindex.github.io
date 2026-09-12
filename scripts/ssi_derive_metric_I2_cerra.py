#!/usr/bin/env python3
"""
Derive I2 — wind — from the CERRA daily-maximum gust archive.

    python3 scripts/ssi_derive_metric_I2_cerra.py --raw-only
    python3 scripts/ssi_derive_metric_I2_cerra.py            (needs THRESHOLD+ANCHOR)

DEFINITION, pending the operator's pin
    gust(d) = daily maximum 10 m wind gust at the unit's CERRA cell,  m/s
    I2_raw  = mean annual sum over days of max(0, gust(d) - GUST_THRESHOLD)
              in m/s-days

WHY CERRA AND NOT ERA5
    ERA5 single levels is 0.25 deg (~31 km). CERRA is 5.5 km. The metric is a
    gust maximum at a point, and a 31 km cell averages away the terrain that
    makes one substation windier than another 20 km along the valley.

    The cost is coverage. CERRA is a European reanalysis: 513,554 of the
    estate's 622,104 substations lie inside its domain. For the other 108,550,
    I2 is DECLARED ABSENT. It is not estimated, not interpolated from ERA5,
    and not filled by a mosaic - that route was tested twice and failed twice
    (RESULT_I2_mosaic_test_1_FAILED.md, _test_2_FAILED.md). One instrument,
    one meaning per published value.

WHY THE DAILY MAXIMUM IS SUFFICIENT AND EXACT
    Both quantities this computes - the annual maximum, and the sum over days
    of the excess above a threshold - are exact functions of a daily maximum.
    A daily maximum is a maximum of maxima over ONE variable, which is the
    case the nonlinearity rule exempts. It is not sqrt(max u^2, max v^2),
    which broke the original I2 and whose error has no sign because the
    components are signed; and it is not relative humidity from daily-mean T
    and Td, which still blocks I8.

    The archive was fetched with leadtime_hour ["1","2","3"] - all 24 hours,
    not the 8 that the first probes saw. See
    FINDING_cerra_leadtime_and_temporal_sampling.md for what the missing 16
    would have cost: 19.6 per cent of cells more than 5 per cent low on their
    own maximum, while the fleet mean moved 3 per cent.

CELLS ARE RESOLVED ONCE, ELSEWHERE
    CERRA carries 2-D lat/lon, no grid_mapping and no x/y axes, so there is
    nothing to do abs(lat - la).argmin() against. scripts/resolve_cerra_cells.py
    builds and audits the mapping; this reads it. If the resolution is wrong it
    is wrong in one place with one set of numbers attached to it.

    61,377 distinct cells carry all 513,554 substations - 8.4 per occupied
    cell. So the heavy work is done PER CELL and expanded to substations
    afterwards: the same answer, 8.4x less arithmetic. The degeneracy is also
    a limitation and belongs in the metric's declaration, not hidden behind
    the phrase "5.5 km".

INCOMPLETE YEARS ARE REFUSED
    An annual maximum computed from nine months is not an annual maximum, and
    nothing about the number announces that it isn't. A year missing any month
    is refused whole and counted. This also makes the script safe to run
    against a partially fetched archive: it will refuse rather than quietly
    produce a low answer.

CONVENTION #56
    Outside the CERRA domain -> ABSENT, counted, never estimated. No
    coordinates -> skipped and counted (resolve_cerra_cells.py reports these).
    Fewer than MIN_YEARS complete years -> refused. Nothing is defaulted.

PIN 13
    Writing metrics.I2 touches published records, so it must not run inside a
    bot window: 1st Thursday 06:00 UTC, 2nd Thursday 10:00 and 11:00 UTC. The
    write path checks. --raw-only writes nothing and is always safe.
"""
from __future__ import annotations
import argparse, calendar, datetime as dt, json, pathlib, sys

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
ARCHIVE = CACHE / "cerra_dmax"
CELLMAP = CACHE / "cerra_cell_map.npz"
FIELD = "fg10"

MIN_YEARS = 4
IRI_TOP = 0.30

GUST_THRESHOLD = None     # m/s. Pin by amendment from the --raw-only curve.
ANCHOR = None             # m/s-days mapping to the top of [0, 0.30].

CANDIDATES = [15.0, 17.2, 20.0, 22.5, 25.0, 27.5, 30.0, 32.5, 35.0, 40.0]


def in_bot_window(now=None) -> str | None:
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.weekday() != 3:                       # Thursday
        return None
    nth = (now.day - 1) // 7 + 1
    if nth == 1 and 5 <= now.hour <= 7:
        return "pipeline-enrichment (1st Thursday 06:00 UTC)"
    if nth == 2 and 9 <= now.hour <= 12:
        return "monthly-refresh / esg-refresh (2nd Thursday 10:00 and 11:00 UTC)"
    return None


def load_cellmap():
    if not CELLMAP.exists():
        sys.exit(f"no {CELLMAP.name} — run scripts/resolve_cerra_cells.py first")
    z = np.load(CELLMAP, allow_pickle=False)
    return (z["slug_id"], z["sub_index"], z["i"].astype("int32"),
            z["j"].astype("int32"), [str(s) for s in z["slugs"]])


def complete_years():
    """Years for which all twelve monthly files are present. A year missing a
    month is named and refused, not silently shortened."""
    have = {}
    for p in sorted(ARCHIVE.glob("cerra_dmax_*.nc")):
        stem = p.stem.replace("cerra_dmax_", "")
        have.setdefault(stem[:4], set()).add(int(stem[4:]))
    full, partial = [], {}
    for y, ms in sorted(have.items()):
        missing = sorted(set(range(1, 13)) - ms)
        if missing:
            partial[y] = missing
        else:
            full.append(y)
    return full, partial


def month_gaps(year):
    """Days in a year whose daily maximum was built from fewer than 24 hourly
    windows. fetch_cerra_daily_max.py records these in each file's short_days
    attribute; a value there is a LOWER BOUND on the true maximum, so the
    derivation must carry the caveat rather than let it end at the file."""
    out = []
    for m in range(1, 13):
        q = ARCHIVE / f"cerra_dmax_{year}{m:02d}.nc"
        if not q.exists():
            continue
        d = netCDF4.Dataset(str(q))
        raw = getattr(d, "short_days", "[]")
        d.close()
        try:
            for e in json.loads(raw):
                out.append((f"{year}-{m:02d}-{e['day']:02d}",
                            e["fields"], e["expected"]))
        except Exception:
            pass
    return out


def year_stats(year, ii, jj):
    """One pass over a year's twelve monthly files. Returns, per cell, the
    annual maximum and the exceedance sum at every candidate threshold. Both
    are maxima/sums over time, so accumulating month by month is exact."""
    ncell = len(ii)
    amax = np.full(ncell, -np.inf, dtype="float64")
    exc = np.zeros((len(CANDIDATES), ncell), dtype="float64")
    ndays = 0
    for m in range(1, 13):
        p = ARCHIVE / f"cerra_dmax_{year}{m:02d}.nc"
        d = netCDF4.Dataset(str(p))
        v = d.variables[FIELD]
        blk = np.asarray(v[:], dtype="float32")[:, ii, jj]   # (days, ncell)
        d.close()
        exp = calendar.monthrange(int(year), m)[1]
        if blk.shape[0] != exp:
            sys.exit(f"{p.name}: {blk.shape[0]} days, expected {exp}. Refusing.")
        ndays += blk.shape[0]
        fin = np.isfinite(blk)
        amax = np.maximum(amax, np.nanmax(np.where(fin, blk, -np.inf), axis=0))
        for n, thr in enumerate(CANDIDATES):
            exc[n] += np.where(fin, np.maximum(0.0, blk - thr), 0.0).sum(axis=0)
    exp_days = 366 if calendar.isleap(int(year)) else 365
    if ndays != exp_days:
        sys.exit(f"{year}: {ndays} days assembled, expected {exp_days}. Refusing.")
    amax[~np.isfinite(amax)] = np.nan
    return amax, exc


def probe(year, ii, jj, cell_of_sub, slug_id, sub_index, slugs,
          ii_all, jj_all, nspot) -> int:
    """One year, printed. Deliberately not a derivation: a single year cannot
    produce I2, whose definition is a MEAN over years, and a number that looks
    like the answer is the most dangerous thing a probe can emit."""
    print(f"\n  {'='*66}")
    print(f"  PROBE — {year} ALONE. This is NOT I2 and must not be pinned")
    print(f"  against. I2 is a mean over >= {MIN_YEARS} complete years.")
    print(f"  {'='*66}")
    amax, exc = year_stats(year, ii, jj)
    am = amax[cell_of_sub]
    print(f"\n  annual maximum gust {year}, per substation (m/s)")
    for q in (5, 50, 90, 99, 99.9, 100):
        print(f"    P{q:<6} {np.nanpercentile(am, q):7.2f}")
    print(f"\n  exceedance response, {year} alone (m/s-days)")
    print(f"  {'threshold':>10}{'% > 0':>10}{'median of those':>18}{'max':>10}")
    for n, thr in enumerate(CANDIDATES):
        col = exc[n][cell_of_sub]
        nz = col[col > 0]
        print(f"  {thr:>10.1f}{100*len(nz)/len(col):>9.1f}%"
              f"{(np.median(nz) if len(nz) else 0):>18.2f}{col.max():>10.2f}")

    if nspot:
        # Recompute chosen substations from the monthly files with none of the
        # per-cell machinery: straight from the substation's own (i, j) in the
        # map. This tests the whole indexing chain - unique/inverse, the
        # cell->substation expansion, and the month-by-month accumulation -
        # against the only thing that can falsify it, the data itself.
        rng = np.random.default_rng(20260911)
        pick = rng.permutation(len(ii_all))[:nspot]
        bad = []
        for s_i in pick:
            yi, xi = int(ii_all[s_i]), int(jj_all[s_i])
            best = -np.inf
            for m in range(1, 13):
                d = netCDF4.Dataset(str(ARCHIVE / f"cerra_dmax_{year}{m:02d}.nc"))
                col = np.asarray(d.variables[FIELD][:, yi, xi], dtype="float32")
                d.close()
                best = max(best, float(np.nanmax(col)))
            got = float(am[s_i])
            if not (abs(best - got) <= 1e-6):
                bad.append((int(s_i), slugs[int(slug_id[s_i])],
                            f"brute {best:.6f} vs derived {got:.6f}"))
        tag = "PASS" if not bad else "FAIL"
        print(f"\n  {tag}  spot check — {nspot} substation(s) recomputed by "
              f"brute force from their own (i, j)")
        if bad:
            for b in bad[:5]:
                print(f"        {b}")
            print(f"  The cell->substation expansion does not reproduce the "
                  f"data. Do not derive.")
            return 1
        print(f"        every one identical to the per-cell result")
    print(f"\n  Nothing written. This is a probe.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-only", action="store_true")
    ap.add_argument("--years", help="comma list; default every complete year")
    ap.add_argument("--probe-year", metavar="YYYY",
                    help="compute ONE year and print its distribution. This is "
                         "NOT I2 and must never be pinned against — it exists "
                         "to exercise the arithmetic against real data before "
                         "the archive is complete.")
    ap.add_argument("--spot-check", type=int, default=0, metavar="N",
                    help="with --probe-year: recompute N substations' annual "
                         "maxima directly from the monthly files, by brute "
                         "force, and require exact agreement")
    a = ap.parse_args()

    writing = not (a.raw_only or a.probe_year)
    if writing:
        if GUST_THRESHOLD is None or ANCHOR is None:
            sys.exit("GUST_THRESHOLD and ANCHOR are not pinned. Run --raw-only, "
                     "take the fleet curve to amendment, set both, then re-run.")
        w = in_bot_window()
        if w:
            sys.exit(f"REFUSING — inside the {w} window. Pin 13. "
                     f"Wait for the bot's run to land.")

    slug_id, sub_index, ii_all, jj_all, slugs = load_cellmap()
    nsub = len(slug_id)

    # 61,377 distinct cells carry 513,554 substations. Work per cell.
    comp = ii_all.astype("int64") * 100000 + jj_all.astype("int64")
    uniq, cell_of_sub = np.unique(comp, return_inverse=True)
    ii = (uniq // 100000).astype("int32")
    jj = (uniq % 100000).astype("int32")
    ncell = len(uniq)

    full, partial = complete_years()
    if a.probe_year:
        if a.probe_year not in full:
            sys.exit(f"{a.probe_year} is not complete on disk. "
                     f"Complete years: {full or 'none'}")
        return probe(a.probe_year, ii, jj, cell_of_sub, slug_id, sub_index,
                     slugs, ii_all, jj_all, a.spot_check)
    if a.years:
        want = [y.strip() for y in a.years.split(",")]
        missing = [y for y in want if y not in full]
        if missing:
            sys.exit(f"not complete on disk: {missing}. "
                     f"Complete years are {full or 'none'}.")
        full = want

    print(f"\n  I2 — wind, CERRA daily maximum 10 m gust at 5.5 km")
    print(f"  {nsub:,} substations inside the domain · {ncell:,} distinct cells "
          f"({nsub/ncell:.1f} per occupied cell)")
    print(f"  622,104 in the estate, so {622104-nsub:,} are OUTSIDE the domain "
          f"and I2 is ABSENT for them")
    if partial:
        for y, miss in partial.items():
            print(f"  {y}  REFUSED — missing month(s) "
                  f"{', '.join(f'{m:02d}' for m in miss)}. An annual maximum "
                  f"from a part-year is not an annual maximum.")
    print(f"  complete years on disk: {', '.join(full) if full else 'NONE'}")

    gaps = [g for y in full for g in month_gaps(y)]
    if gaps:
        print(f"\n  ARCHIVE GAPS — {len(gaps)} day(s) built from fewer than 24")
        print(f"  hourly windows. Every maximum on these days is a LOWER BOUND.")
        for tag, got, exp in gaps:
            print(f"    {tag}   {got} of {exp} fields")
        print(f"  This is CERRA's gap, not the retrieval's, and it belongs in")
        print(f"  the metric's limitation. It does not stop the derivation.")

    if len(full) < MIN_YEARS:
        print(f"\n  Fewer than MIN_YEARS={MIN_YEARS} complete years. "
              f"Nothing derived, nothing written.")
        print(f"  This is the refusal working, not a failure — let the fetch "
              f"finish.")
        return 1

    A, E = [], []
    for y in full:
        amax, exc = year_stats(y, ii, jj)
        A.append(amax); E.append(exc)
        print(f"    {y}  {np.isfinite(amax).sum():,} cells · "
              f"annual max median {np.nanmedian(amax):.2f} m/s")

    A = np.vstack(A)                       # (nyear, ncell)
    E = np.stack(E)                        # (nyear, ncand, ncell)
    nfin = np.isfinite(A).sum(axis=0)
    ok = nfin >= MIN_YEARS
    am_cell = np.where(ok, np.nanmean(A, axis=0), np.nan)
    ex_cell = np.where(ok, E.mean(axis=0), np.nan)      # (ncand, ncell)

    # expand cells -> substations; every substation in a cell shares its value
    keep = ok[cell_of_sub]
    am = am_cell[cell_of_sub][keep]
    ex = ex_cell[:, cell_of_sub][:, keep]

    print(f"\n  FLEET — {keep.sum():,} substations with >= {MIN_YEARS} "
          f"complete years ({(~keep).sum():,} refused)")
    print(f"\n  annual maximum gust, mean over years (m/s)")
    for q in (5, 50, 90, 99, 99.9, 100):
        print(f"    P{q:<6} {np.percentile(am, q):7.2f}")

    print(f"\n  THRESHOLD RESPONSE — the curve the pin is chosen against")
    print(f"  {'threshold':>10}{'% of fleet > 0':>16}{'median of those':>18}"
          f"{'P99':>10}{'max':>10}")
    for n, thr in enumerate(CANDIDATES):
        col = ex[n]
        nz = col[col > 0]
        print(f"  {thr:>10.1f}{100*len(nz)/len(col):>15.1f}%"
              f"{(np.median(nz) if len(nz) else 0):>18.2f}"
              f"{(np.percentile(nz, 99) if len(nz) else 0):>10.2f}"
              f"{col.max():>10.2f}")
    print("\n  A threshold that leaves ~100% of the fleet above zero is not")
    print("  discriminating; one that leaves almost none is not measuring.")
    print("  The pin is a judgement about where wind stops being weather and")
    print("  starts being a load, and it is the operator's.")

    by = {}
    for s, k in zip(slug_id[keep], sub_index[keep]):
        by[slugs[s]] = by.get(slugs[s], 0) + 1
    print(f"\n  per country, substations with a derivable I2")
    for s in sorted(by):
        print(f"    {s:<16}{by[s]:>9,}")

    print(f"\n  Nothing written — --raw-only. metrics.I2 needs the pin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
