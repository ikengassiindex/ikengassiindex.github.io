#!/usr/bin/env python3
"""
Derive I2 — wind — from the merged-region daily maximum gust fetch.

    python3 scripts/ssi_derive_metric_I2.py --plan <gust.json> --raw-only --all
    python3 scripts/ssi_derive_metric_I2.py --plan <gust.json> --all   (needs THRESHOLD+ANCHOR)

DEFINITION, pending the operator's pin
    gust(d) = daily maximum 10 m wind gust at the unit's grid cell,  m/s
    I2_raw  = mean annual sum over days of max(0, gust(d) - GUST_THRESHOLD)
              in m/s-days

WHY GUST AND NOT WIND SPEED
    The pinned definition was built on the daily maximum of sqrt(u^2+v^2). No
    daily product can supply that: sqrt(max u^2, max v^2) is a different
    quantity, and because ERA5 components are SIGNED the error has no sign — a
    real 20 m/s gale can score zero excess and a calm day can score 4.01.

    A gust is a scalar, so there is nothing to recombine and the defect cannot
    arise. It is also closer to the mechanism: IEC 60826 designs overhead lines
    to a reference wind with gust response factors, not to a mean.

    Declared, and carried in the metric's limitation:
      - ERA5 single levels is 0.25 deg (~31 km); I1, I3 and I5 are ERA5-Land at
        0.1 deg (~9 km). The estate mixes grids. ERA5-Land carries no gust
        variable — checked, not assumed.
      - ERA5's gust is a PARAMETRISATION of sub-grid variability, not an
        observation, and gust schemes are weakest in complex terrain.
      - I2 remains the wind half of a two-term hazard. Vegetation is absent.

WHY THIS WRITES A CURVE AND NOT A NUMBER
    GUST_THRESHOLD is not pinned and must not be invented here. 17.2 m/s is
    Beaufort 8 SUSTAINED; gusts clear it routinely without damage, so carrying
    it across would manufacture excess on most of the fleet. Converting it
    means choosing a gust factor, which is terrain-dependent — a judgement
    dressed as arithmetic.

    So --raw-only computes, in ONE pass over the data, the fleet's exceedance
    response at every candidate threshold in CANDIDATES, plus the annual-maximum
    gust distribution. The operator pins the threshold against that curve, as
    I3's anchor was pinned against its fleet, and the metric is then derived.

CONVENTION #56
    No coordinates -> skipped and counted. Sea cell -> snapped to nearest valid
    cell within MAX_SNAP and counted; unresolvable -> skipped, never defaulted.
    Fewer than MIN_YEARS -> refused. Note that unlike ERA5-Land, this product is
    NOT land-masked, so a coastal cell carries a real value and the snap is a
    much smaller correction here; it is kept so the two metrics resolve cells
    the same way.
"""
from __future__ import annotations
import argparse, json, pathlib, sys
from datetime import datetime, timezone

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"

MIN_YEARS = 4
MAX_SNAP = 6
IRI_TOP = 0.30
TIME_CHUNK = 40

GUST_THRESHOLD = None     # m/s. Pin by amendment from the --raw-only curve.
ANCHOR = None             # m/s-days mapping to the top of [0, 0.30].

CANDIDATES = [15.0, 17.2, 20.0, 22.5, 25.0, 27.5, 30.0, 32.5, 35.0, 40.0]


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man, man.get("substations") or [], None
    subs, paths = [], []
    for e in sh:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        blk = raw if isinstance(raw, list) else (raw.get("substations") or [])
        subs.extend(blk)
        paths.append((p, len(blk), isinstance(raw, list)))
    return man, subs, paths


def save(slug, man, subs, paths):
    if paths is None:
        man["substations"] = subs
        (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))
        return
    off = 0
    for p, cnt, was_list in paths:
        blk = subs[off:off + cnt]
        off += cnt
        p.write_text(json.dumps(blk if was_list else {"substations": blk}))
    (ROOT / slug / "ssi-data.json").write_text(json.dumps(man))


def region_file(plan, rid, year):
    v = plan["variables"][0]
    ab = "".join(w[0] for w in v.split("_"))[:6]
    return CACHE / f"era5land_{plan['tag']}_{rid}_{ab}_{year}.nc"


def field_name(ds):
    skip = {"latitude", "longitude", "valid_time", "time", "number",
            "expver", "lat", "lon"}
    cand = [k for k, v in ds.variables.items()
            if k not in skip and len(v.dimensions) >= 3]
    if len(cand) != 1:
        raise ValueError(f"expected exactly one 3-D field, found {cand}")
    return cand[0]


def axes_and_validity(path):
    ds = netCDF4.Dataset(str(path))
    lat = np.asarray(ds.variables["latitude"][:])
    lon = np.asarray(ds.variables["longitude"][:])
    f = field_name(ds)
    nt = ds.variables[f].shape[0]
    probe = np.asarray(ds.variables[f][::max(1, nt // 8)], dtype="float32")
    ds.close()
    return lat, lon, np.isfinite(probe).any(axis=0), f


def resolve(points, lat, lon, valid):
    out, snapped, skipped = {}, 0, 0
    for k, (la, lo) in points:
        i = int(np.abs(lat - la).argmin())
        j = int(np.abs(lon - lo).argmin())
        if not valid[i, j]:
            found = None
            for r in range(1, MAX_SNAP + 1):
                a0, a1 = max(0, i - r), min(valid.shape[0], i + r + 1)
                b0, b1 = max(0, j - r), min(valid.shape[1], j + r + 1)
                blk = valid[a0:a1, b0:b1]
                if blk.any():
                    c = np.argwhere(blk)
                    d2 = (c[:, 0] + a0 - i) ** 2 + (c[:, 1] + b0 - j) ** 2
                    ii, jj = c[int(np.argmin(d2))]
                    found = (int(ii + a0), int(jj + b0))
                    break
            if found is None:
                skipped += 1
                continue
            i, j = found
            snapped += 1
        out[k] = (i, j)
    return out, snapped, skipped


def year_stats(path, cells, field):
    """One streamed pass. Per cell: annual max gust, and the exceedance sum at
    every candidate threshold. Both are sums/maxima over time, so chunking is
    exact rather than approximate."""
    cl = sorted(set(cells.values()))
    rmin, rmax = min(i for i, _ in cl), max(i for i, _ in cl)
    ii = np.array([i - rmin for i, _ in cl])
    jj = np.array([j for _, j in cl])
    pos = {c: k for k, c in enumerate(cl)}

    ds = netCDF4.Dataset(str(path))
    var = ds.variables[field]
    nt = var.shape[0]
    amax = np.full(len(cl), -np.inf, dtype="float64")
    exc = np.zeros((len(CANDIDATES), len(cl)), dtype="float64")
    for t0 in range(0, nt, TIME_CHUNK):
        blk = np.asarray(var[t0:t0 + TIME_CHUNK, rmin:rmax + 1, :],
                         dtype="float32")[:, ii, jj]
        fin = np.isfinite(blk)
        amax = np.maximum(amax, np.nanmax(np.where(fin, blk, -np.inf), axis=0))
        for n, thr in enumerate(CANDIDATES):
            exc[n] += np.where(fin, np.maximum(0.0, blk - thr), 0.0).sum(axis=0)
    ds.close()
    amax[~np.isfinite(amax)] = np.nan
    return ({k: float(amax[pos[c]]) for k, c in cells.items()},
            {k: exc[:, pos[c]].copy() for k, c in cells.items()})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--raw-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    plan = json.loads(pathlib.Path(a.plan).read_text())
    years = [str(y) for y in plan["years"]]
    regions = plan["regions"]
    if not a.raw_only and (GUST_THRESHOLD is None or ANCHOR is None):
        sys.exit("GUST_THRESHOLD and ANCHOR are not pinned. Run --raw-only, "
                 "take the fleet curve to amendment, set both, then re-run.")

    want = slugs() if a.all else a.slugs
    if not want:
        sys.exit("give country slugs or --all")

    placed = {r["id"]: [] for r in regions}
    counts, nocoord, outside = {}, 0, 0
    for slug in sorted(want):
        try:
            _, subs, _ = load(slug)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        counts[slug] = len(subs)
        for k, s in enumerate(subs):
            la, lo = s.get("lat"), s.get("lon")
            if not isinstance(la, (int, float)) or not isinstance(lo, (int, float)):
                nocoord += 1
                continue
            hit = [r for r in regions
                   if r["south"] <= la <= r["north"] and r["west"] <= lo <= r["east"]]
            if not hit:
                outside += 1
                continue
            placed[hit[0]["id"]].append((slug, k, float(la), float(lo)))
        del subs

    print(f"\n  I2 — wind, daily maximum 10 m gust exceedance")
    print(f"  {len(counts)} countries · {sum(len(v) for v in placed.values()):,} "
          f"placed · {nocoord:,} without coordinates · {outside:,} outside\n")

    amax_by, exc_by = {}, {}
    for r in regions:
        pts = placed[r["id"]]
        if not pts:
            print(f"  {r['id']}  no substations")
            continue
        have = [y for y in years if region_file(plan, r["id"], y).exists()]
        print(f"  {r['id']}  {len(pts):,} substations · {len(have)}/{len(years)} "
              f"years on disk" + ("" if len(have) == len(years) else "  PARTIAL"))
        if not have:
            continue
        lat, lon, valid, field = axes_and_validity(region_file(plan, r["id"], have[0]))
        cells, snapped, skipped = resolve([((s, k), (la, lo))
                                           for s, k, la, lo in pts], lat, lon, valid)
        print(f"        field '{field}' · grid {valid.shape} · "
              f"{snapped:,} snapped · {skipped:,} unresolvable")
        if a.dry_run:
            continue
        for y in have:
            am, ex = year_stats(region_file(plan, r["id"], y), cells, field)
            for key, v in am.items():
                amax_by.setdefault(key, []).append(v)
                exc_by.setdefault(key, []).append(ex[key])
            print(f"        {y}  {len(am):,} cells")

    if a.dry_run:
        print("\n  DRY RUN — nothing written")
        return 0
    if not amax_by:
        print("\n  nothing derived. Nothing written.")
        return 1

    keys = [k for k, v in amax_by.items()
            if sum(1 for x in v if np.isfinite(x)) >= MIN_YEARS]
    am_mean = np.array([np.mean([x for x in amax_by[k] if np.isfinite(x)])
                        for k in keys])
    exc_mean = np.vstack([np.mean(np.vstack(exc_by[k]), axis=0) for k in keys])

    print(f"\n  FLEET — {len(keys):,} substations with >= {MIN_YEARS} years")
    print(f"\n  annual maximum gust, mean over years (m/s)")
    for q in (5, 50, 90, 99, 99.9, 100):
        print(f"    P{q:<6} {np.percentile(am_mean, q):7.2f}")

    print(f"\n  THRESHOLD RESPONSE — the curve the pin is chosen against")
    print(f"  {'threshold':>10}{'% of fleet > 0':>16}{'median of those':>18}"
          f"{'P99':>10}{'max':>10}")
    for n, thr in enumerate(CANDIDATES):
        col = exc_mean[:, n]
        nz = col[col > 0]
        print(f"  {thr:>10.1f}{100*len(nz)/len(col):>15.1f}%"
              f"{(np.median(nz) if len(nz) else 0):>18.2f}"
              f"{(np.percentile(nz, 99) if len(nz) else 0):>10.2f}"
              f"{col.max():>10.2f}")
    print("\n  A threshold that leaves ~100% of the fleet above zero is not")
    print("  discriminating; one that leaves almost none is not measuring.")
    print("  The pin is a judgement about where wind stops being weather and")
    print("  starts being a load, and it is the operator's.")
    print("\n  Nothing written — --raw-only. metrics.I2 needs the pin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
