#!/usr/bin/env python3
"""
I3 — Heat-wave IRI, as an EXTREME DEVIATION from the local seasonal norm.

    python3 scripts/ssi_derive_metric_I3.py greece --dry-run
    python3 scripts/ssi_derive_metric_I3.py --all

WHY A DEVIATION AND NOT A TEMPERATURE
-------------------------------------
Pinned by the flag officer, 30 August 2026: the metric captures extreme
deviations. Infrastructure is designed to local norms, so a departure FROM
those norms is what exceeds design assumptions — a Norwegian substation built
for Norwegian conditions is stressed by a Norwegian extreme much as a Greek
one is by a Greek extreme. This is also the standard climatological definition
of a heat wave (Perkins & Alexander 2013; WMO): local percentile exceedance,
not an absolute threshold.

An absolute threshold was measured and rejected on evidence: at 30/33/35 °C
every Norwegian and Finnish substation scores 0, so P5 == P95 and Method B
correctly declines to normalise. I3 would have been undefined for those fleets.

TWO TRAPS, BOTH MEASURED BEFORE THIS WAS WRITTEN
------------------------------------------------
1. FREQUENCY IS DEGENERATE BY CONSTRUCTION. If the threshold is the p90 of the
   same data, ~10% of days exceed it everywhere by definition. Measured: the
   exceedance count is capped at 0-37 days/yr in EVERY country, carrying almost
   no spatial signal. So the metric must be MAGNITUDE, not count.

2. A WHOLE-YEAR BASELINE MEASURES CLIMATE VARIABILITY, NOT EXTREMENESS.
   With p90 taken over the full year, the seasonal cycle dominates and the
   median excess ranked finland (106 degC-days) and norway (95) ABOVE greece
   (65) and turkey (51) — i.e. it ranked Finland as the most heat-exposed
   country in the register. Standardising by the annual sigma did not fix it
   (norway 11.6 sigma-days against greece 8.1).

   The fix is a CALENDAR-DAY baseline: p90 computed per pentad over a moving
   window, so the threshold tracks the seasonal cycle and the exceedance is
   weather, not season. That inverts the ordering to greece 29.0, finland 23.5,
   turkey 22.9, norway 22.8, japan 14.1 degC-days/yr — which is the ordering a
   heat metric should produce.

DEFINITION
----------
  baseline    per grid cell, the 90th percentile of daily-max 2 m temperature
              for each pentad of the calendar year, pooled across all available
              years over a +/- 1 pentad window (~75 samples per bin)
  heat day    daily max above that day's baseline
  heat wave   a run of >= 3 consecutive heat days (Perkins & Alexander)
  I3_raw      mean annual cumulative excess in degC-days, summed over days
              inside heat waves only

  I3 = Method B over FLEET P5/P95, NOT inverted — more heat-wave excess is more
  risk, and the metric carries risk in the same direction as R.

SOURCE
------
ERA5-Land daily maximum 2 m temperature, already cached in the repo at
scripts/pipeline/.cache/era5land_daily_max_<slug>_<year>.nc — 193 files,
2.58 GB, all 39 countries. Nothing is fetched.

CONVENTION #7 DECLARATION — THE BASELINE IS SHORT
-------------------------------------------------
Standard practice builds a heat-wave climatology from 30 years. This has FIVE
(2018-2022; luxembourg and slovenia have four). Two consequences, declared
rather than hidden:

  - the p90 per pentad rests on ~75 samples, so it carries sampling error
  - the same period defines the baseline AND measures the exceedance, so this
    is a WITHIN-PERIOD extremeness measure, not an anomaly against an
    independent climatology

It is sound for ranking substations against each other, which is what Method B
needs. It is not a climate-trend statement and must not be read as one.

CONVENTION #56
--------------
A country with fewer than 4 years is REFUSED. A substation outside the grid or
without coordinates is skipped and counted, never defaulted.
"""
from __future__ import annotations
import argparse, json, math, os, pathlib, sys
from datetime import datetime, timezone

import numpy as np
try:
    import netCDF4
except ImportError:
    sys.exit("netCDF4 required:  pip3 install netCDF4")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
YEARS = (2018, 2019, 2020, 2021, 2022)
MIN_YEARS = 4
PENTADS = 73
WINDOW = 1           # +/- 1 pentad => ~15 calendar days pooled
PCT = 90
MIN_RUN = 3          # consecutive days to count as a heat wave
MAX_SNAP = 3         # cells; ~33 km. Beyond this a substation is not on this grid
AMENDMENT = "AMENDMENT_I3_heatwave_extreme_deviation.md"


def soft_clip_upper(x):
    return x if x <= 1.0 else 1.0 + math.log(x) if x > 0 else x


def method_b(x, p5, p95):
    if p5 is None or p95 is None or p95 <= p5:
        return None
    return max(0.0, min(1.0, (x - p5) / (p95 - p5)))


def percentile(sv, q):
    if not sv:
        return None
    i = q * (len(sv) - 1)
    lo, hi = int(i), min(int(i) + 1, len(sv) - 1)
    return sv[lo] + (sv[hi] - sv[lo]) * (i - lo)


def load_years(slug, lat_slice=None):
    """lat_slice keeps the whole time series but only a band of latitudes.

    Canada, greenland, the us and australia span so much of the globe that the
    full (days x lat x lon) float32 array runs to several GB and the process is
    OOM-killed. The climatology is computed independently per cell, so slicing
    the latitude axis is exact, not an approximation."""
    arrs, doys, lat, lon, used = [], [], None, None, []
    for y in YEARS:
        p = CACHE / f"era5land_daily_max_{slug}_{y}.nc"
        if not p.exists():
            continue
        d = netCDF4.Dataset(str(p))
        v = d.variables["t2m"]
        a = (np.asarray(v[:, lat_slice, :], dtype="float32") if lat_slice is not None
             else np.asarray(v[:], dtype="float32"))
        arrs.append(a)
        doys.append(np.arange(a.shape[0]) % 366)
        la = np.asarray(d.variables["latitude"][:])
        lat = la[lat_slice] if lat_slice is not None else la
        lon = np.asarray(d.variables["longitude"][:])
        d.close()
        used.append(y)
    if len(used) < MIN_YEARS:
        raise ValueError(f"only {len(used)} year(s) of ERA5 cached, need {MIN_YEARS}")
    return np.concatenate(arrs, 0), np.concatenate(doys), lat, lon, used


def grid_shape(slug):
    for y in YEARS:
        p = CACHE / f"era5land_daily_max_{slug}_{y}.nc"
        if p.exists():
            d = netCDF4.Dataset(str(p))
            n = (len(d.dimensions["valid_time"]), len(d.dimensions["latitude"]),
                 len(d.dimensions["longitude"]))
            d.close()
            return n
    raise ValueError("no cached ERA5 for this country")


def axes_and_validity(slug):
    """lat, lon, and a land mask, without reading a whole year of data.

    Validity is taken from a handful of timesteps spread across one year: a
    cell that is finite at any of them is land. ERA5-Land's sea mask does not
    move, so this is exact and costs a few MB instead of gigabytes."""
    for y in YEARS:
        p = CACHE / f"era5land_daily_max_{slug}_{y}.nc"
        if not p.exists():
            continue
        d = netCDF4.Dataset(str(p))
        lat = np.asarray(d.variables["latitude"][:])
        lon = np.asarray(d.variables["longitude"][:])
        nt = len(d.dimensions["valid_time"])
        probe = np.asarray(d.variables["t2m"][::max(1, nt // 8)], dtype="float32")
        d.close()
        return lat, lon, np.isfinite(probe).any(axis=0)
    raise ValueError("no cached ERA5 for this country")


def resolve_cells(subs, lat, lon, valid):
    """substation index -> (i, j) on a LAND cell, or None. Also the snap count.

    ERA5-Land is empty over sea, so a coastal substation lands on an all-NaN
    cell whose sum is 0.0 — finite, plausible and false. Measured before this
    existed: it would have handed a zero to 900 of norway's 6,113 substations."""
    out, snapped, skipped = {}, 0, 0
    for k, s in enumerate(subs):
        la, lo = s.get("lat"), s.get("lon")
        if not isinstance(la, (int, float)) or not isinstance(lo, (int, float)):
            skipped += 1
            continue
        i = int(np.abs(lat - la).argmin())
        j = int(np.abs(lon - lo).argmin())
        if not valid[i, j]:
            found = None
            for r in range(1, MAX_SNAP + 1):
                a0, a1 = max(0, i - r), min(valid.shape[0], i + r + 1)
                b0, b1 = max(0, j - r), min(valid.shape[1], j + r + 1)
                blk = valid[a0:a1, b0:b1]
                if blk.any():
                    cand = np.argwhere(blk)
                    d2 = (cand[:, 0] + a0 - i) ** 2 + (cand[:, 1] + b0 - j) ** 2
                    ii, jj = cand[int(np.argmin(d2))]
                    found = (int(ii + a0), int(jj + b0))
                    break
            if found is None:
                skipped += 1
                continue
            i, j = found
            snapped += 1
        out[k] = (i, j)
    return out, snapped, skipped


def series_for_cells(slug, cells):
    """(time, n_cells) float32 for just the cells we need, plus doy and years.

    ONE CONTIGUOUS SLICE PER YEAR, immediately reduced to the needed cells.
    Reading [:, one_row, :] instead fights the HDF5 chunk layout — every chunk
    in the file has to be touched for each row — and canada did not finish in
    175 s that way. Slicing the latitude BAND the substations occupy and then
    fancy-indexing is one sequential read per file.

    Peak memory is one year of the band, not the whole cube: canada's full grid
    is 415 x 885 x 1825 = 2.7 GB and was OOM-killed."""
    cell_list = sorted(cells)
    rmin = min(i for i, _ in cell_list)
    rmax = max(i for i, _ in cell_list)
    ii = np.array([i - rmin for i, _ in cell_list])
    jj = np.array([j for _, j in cell_list])
    offset = {c: k for k, c in enumerate(cell_list)}

    blocks, doys, used = [], [], []
    for y in YEARS:
        p = CACHE / f"era5land_daily_max_{slug}_{y}.nc"
        if not p.exists():
            continue
        d = netCDF4.Dataset(str(p))
        band = np.asarray(d.variables["t2m"][:, rmin:rmax + 1, :], dtype="float32")
        d.close()
        blocks.append(band[:, ii, jj])
        doys.append(np.arange(band.shape[0]) % 366)
        del band
        used.append(y)
    if len(used) < MIN_YEARS:
        raise ValueError(f"only {len(used)} year(s) of ERA5 cached, need {MIN_YEARS}")
    return np.concatenate(blocks, 0), np.concatenate(doys), offset, used


def heatwave_1d(t, doy):
    """Same definition as heatwave_field, over a (time, n_cells) array."""
    years = t.shape[0] / 365.25
    b = (doy * PENTADS // 366).astype(int)
    clim = np.empty((PENTADS, t.shape[1]), dtype="float32")
    for k in range(PENTADS):
        off = (b - k + PENTADS // 2) % PENTADS - PENTADS // 2
        clim[k] = np.nanpercentile(t[np.abs(off) <= WINDOW], PCT, axis=0)
    exc = t - clim[b]
    above = np.nan_to_num(exc, nan=-1.0) > 0
    n = above.shape[0]
    runlen = np.zeros(above.shape, dtype=np.int16)
    cur = np.zeros(above.shape[1], dtype=np.int16)
    for i in range(n):
        cur = np.where(above[i], cur + 1, 0)
        runlen[i] = cur
    keep = np.zeros(above.shape, dtype=bool)
    mx = np.zeros(above.shape[1], dtype=np.int16)
    for i in range(n - 1, -1, -1):
        mx = np.where(above[i], np.maximum(mx, runlen[i]), 0)
        keep[i] = above[i] & (mx >= MIN_RUN)
    return np.where(keep, np.nan_to_num(exc), 0).sum(0) / years


def derive(slug, subs, dry):
    lat, lon, valid = axes_and_validity(slug)
    cellmap, snapped, skipped = resolve_cells(subs, lat, lon, valid)
    if not cellmap:
        raise ValueError("no substation fell on a land cell")
    t, doy, offset, used = series_for_cells(slug, set(cellmap.values()))
    degd = heatwave_1d(t, doy)
    del t

    raw, idx = [], []
    for k, (i, j) in cellmap.items():
        v = degd[offset[(i, j)]]
        if not np.isfinite(v):
            skipped += 1
            continue
        raw.append(float(v))
        idx.append(k)

    if not raw:
        raise ValueError("no substation fell on a finite grid cell")
    sv = sorted(raw)
    p5, p95 = percentile(sv, 0.05), percentile(sv, 0.95)
    n = 0
    for k, i in enumerate(idx):
        v = method_b(raw[k], p5, p95)
        if v is None:
            continue
        if not dry:
            m = subs[i].setdefault("metrics", {})
            m["I3"] = round(v, 4)
            m["_I3_raw_degC_days"] = round(raw[k], 3)
        n += 1
    return n, skipped, snapped, (p5, p95), used, float(np.median(raw))


def load_slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_subs(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if not shards:
        return man, man.get("substations") or [], None
    subs, paths = [], []
    for e in shards:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        block = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(block)
        paths.append((p, len(block), isinstance(raw, list)))
    return man, subs, paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slugs = load_slugs() if a.all else a.slugs
    if not slugs:
        sys.exit("give country slugs or --all")

    print(f"\n  I3 heat-wave IRI — {AMENDMENT}\n")
    print(f"  {'country':<14}{'yrs':>5}{'derived':>9}{'skipped':>9}{'snapped':>9}"
          f"{'med degC-d':>12}{'P5':>8}{'P95':>8}")
    for slug in slugs:
        try:
            man, subs, paths = load_subs(slug)
            n, sk, snp, anch, used, med = derive(slug, subs, a.dry_run)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        print(f"  {slug:<14}{len(used):>5}{n:>9,}{sk:>9,}{snp:>9,}{med:>12.1f}"
              f"{anch[0]:>8.1f}{anch[1]:>8.1f}")
        if a.dry_run or not n:
            continue
        man.setdefault("meta", {}).setdefault("metric_derivations", []).append({
            "metrics": ["I3"], "at_utc": datetime.now(timezone.utc).isoformat(),
            "amendment": AMENDMENT, "source": "ERA5-Land daily max 2m temperature",
            "years": used, "baseline": f"pentad p{PCT}, +/-{WINDOW} pentad window",
            "min_run_days": MIN_RUN, "n_derived": n, "n_skipped": sk, "n_snapped_to_land": snp,
            "anchors": {"I3": list(anch)},
            "caveat": "five-year baseline; within-period extremeness, not a "
                      "climate-trend statement"})
        if paths is None:
            man["substations"] = subs
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        else:
            off = 0
            for p, cnt, was_list in paths:
                blk = subs[off:off + cnt]; off += cnt
                p.write_text(json.dumps(blk if was_list else {"substations": blk}))
            (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
