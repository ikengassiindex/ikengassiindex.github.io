#!/usr/bin/env python3
"""
Is texture a property of the site, or of the weather? Pre-registered test.

    python3 scripts/test_texture_persistence.py \
        --fine-a <cerra month A> --fine-b <cerra month B> --coarse <era5 file>

WHAT TEXTURE IS
    THINKING_I2_mosaic.md proposes taking the LEVEL of I2's wind field from
    ERA5, which covers the globe on one ruler, and the TEXTURE from the finest
    source available locally:

        texture(cell) = FINE_stat(cell) / mean of FINE_stat over the ERA5
                        cell that contains it

    By construction texture averages to 1 inside every ERA5 cell, so a fine
    source can redistribute within a region but never move its level. That is
    what makes sources with an 11 per cent level offset and a 0.26 rank
    correlation combinable at all.

WHY THIS TEST DECIDES IT
    The construction is only legitimate if texture is TERRAIN — exposure,
    roughness, orography — which does not change between years. If texture is
    instead the footprint of one January's storms, applying it would inject
    spurious structure into roughly 500,000 published values and would be
    worse than the coarse field it replaces.

    Terrain persists. Weather does not. So: compute texture from two separate
    periods and see whether they agree at the same substation.

PASS CRITERIA, FIXED BEFORE THE DATA WAS SEEN
    Written 2026-09-10 while the second CERRA month was still queued, so the
    bar cannot be moved to fit the answer.

    TEST 1  persistence
            per-country Pearson r between texture(A) and texture(B)
            PASS  every country r >= 0.60 AND median country r >= 0.80
            FAIL  otherwise -> texture is weather; abandon the mosaic

    TEST 2  does it buy anything
            within-country CV of (ERA5 level x texture), against the two
            baselines measured on 2018-01:
                        ERA5    CERRA
              france    0.120   0.133
              germany   0.135   0.146
              norway    0.160   0.190
              uk        0.064   0.092
              italy     0.206   0.234
              spain     0.154   0.182
            PASS  the mosaic CV closes at least half the ERA5->CERRA gap in
                  the median country
            FAIL  otherwise -> texture is real but too weak to be worth it

    TEST 3  scale invariance
            texture is derived from a maximum and applied to a daily series.
            Compare texture computed on the period MAXIMUM against texture
            computed on the period MEDIAN.
            PASS  r >= 0.80 -> one multiplier is defensible
            FAIL  otherwise -> texture must be applied as a distribution
                  mapping, not a multiplier. Not fatal; a different form.

    A single January pair is a WEAK test of persistence: two cold-season
    months in the same synoptic regime can agree for reasons that do not hold
    in summer. If these pass, a July month is the honest confirmation before
    anything is committed. Recorded here so a pass is not over-read.
"""
from __future__ import annotations
import argparse, json, pathlib, sys
import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util
_s = importlib.util.spec_from_file_location(
    "mf", str(ROOT / "scripts" / "measure_field_granularity.py"))
mf = importlib.util.module_from_spec(_s); _s.loader.exec_module(mf)

COUNTRIES = ["france", "germany", "norway", "uk", "italy", "spain"]
BASE = {"france": (0.120, 0.133), "germany": (0.135, 0.146),
        "norway": (0.160, 0.190), "uk": (0.064, 0.092),
        "italy": (0.206, 0.234), "spain": (0.154, 0.182)}
CHUNK = 40


def cell_stat(path, fld, how="max", nmax=0):
    """Per-cell statistic over the whole grid, streamed."""
    ds = netCDF4.Dataset(str(path))
    v = ds.variables[fld]
    nt = v.shape[0] if not nmax else min(nmax, v.shape[0])
    if how == "max":
        acc = np.full(v.shape[1:], -np.inf, dtype="float32")
        for t in range(0, nt, CHUNK):
            b = np.asarray(v[t:t + CHUNK], dtype="float32")
            acc = np.maximum(acc, np.nanmax(np.where(np.isfinite(b), b, -np.inf), 0))
        acc[~np.isfinite(acc)] = np.nan
    else:                                   # median, sampled to bound memory
        idx = np.linspace(0, nt - 1, min(nt, 60)).astype(int)
        acc = np.nanmedian(np.asarray(v[idx], dtype="float32"), 0)
    ds.close()
    return acc


def texture_field(fine_path, coarse_grid, fld="fg10", how="max"):
    """texture per FINE cell = fine stat / mean of fine stat over its ERA5 cell."""
    ds = netCDF4.Dataset(str(fine_path)); g = mf.Grid(ds); ds.close()
    stat = cell_stat(fine_path, fld, how)
    la = g.lat2d.ravel(); lo = g.lon2d.ravel()
    ci, cj = coarse_grid.index(la, lo)
    ok = (ci >= 0) & (cj >= 0) & np.isfinite(stat.ravel())
    key = ci.astype(np.int64) * 100000 + cj
    s = stat.ravel()
    sums = np.bincount(key[ok], weights=s[ok])
    cnts = np.bincount(key[ok])
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(cnts > 0, sums / np.maximum(cnts, 1), np.nan)
    tex = np.full(s.shape, np.nan)
    tex[ok] = s[ok] / means[key[ok]]
    return g, tex.reshape(stat.shape), stat


def subs_of(slug):
    subs = mf.load(slug)
    la = np.array([s["lat"] for s in subs if isinstance(s.get("lat"), (int, float))])
    lo = np.array([s["lon"] for s in subs if isinstance(s.get("lon"), (int, float))])
    del subs
    return la, lo


def pearson(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 30: return None
    a, b = a[m], b[m]
    if a.std() == 0 or b.std() == 0: return None
    return float(np.corrcoef(a, b)[0, 1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fine-a", required=True)
    ap.add_argument("--fine-b", required=True)
    ap.add_argument("--coarse", required=True)
    ap.add_argument("--coarse-timesteps", type=int, default=31)
    a = ap.parse_args()

    dsc = netCDF4.Dataset(a.coarse); cg = mf.Grid(dsc); dsc.close()
    print(f"\n  coarse (level) : {pathlib.Path(a.coarse).name}  {cg.shape} ~{cg.res_km:.1f} km")
    print(f"  fine A         : {pathlib.Path(a.fine_a).name}")
    print(f"  fine B         : {pathlib.Path(a.fine_b).name}\n")

    gA, texA, statA = texture_field(a.fine_a, cg)
    gB, texB, _     = texture_field(a.fine_b, cg)
    _,  texMed, _   = texture_field(a.fine_a, cg, how="median")
    coarse_stat = cell_stat(a.coarse, "fg10", "max", a.coarse_timesteps)

    print(f"  {'country':<10}{'n':>9} | {'T1 r':>7} | {'CV era5':>8}{'CV mos':>8}"
          f"{'CV cerra':>9}{'gap closed':>12} | {'T3 r':>7}")
    t1, t2, t3 = [], [], []
    for slug in COUNTRIES:
        la, lo = subs_of(slug)
        fi, fj = gA.index(la, lo)
        ci, cj = cg.index(la, lo)
        ok = (fi >= 0) & (fj >= 0) & (ci >= 0) & (cj >= 0)
        if ok.sum() < 30: continue
        ta = texA[fi[ok], fj[ok]]; tb = texB[fi[ok], fj[ok]]
        tm = texMed[fi[ok], fj[ok]]
        lvl = coarse_stat[ci[ok], cj[ok]]
        r1 = pearson(ta, tb); r3 = pearson(ta, tm)
        mos = lvl * ta
        m = np.isfinite(mos)
        cv = float(mos[m].std() / mos[m].mean())
        e5, ce = BASE[slug]
        closed = (cv - e5) / (ce - e5) if ce != e5 else float("nan")
        t1.append(r1); t2.append(closed); t3.append(r3)
        print(f"  {slug:<10}{int(ok.sum()):>9,} | {r1:>7.3f} | {e5:>8.3f}{cv:>8.3f}"
              f"{ce:>9.3f}{100*closed:>11.0f}% | {r3:>7.3f}")

    ok1 = all(r is not None and r >= 0.60 for r in t1) and np.median(t1) >= 0.80
    ok2 = np.median(t2) >= 0.50
    ok3 = np.median([r for r in t3 if r is not None]) >= 0.80
    print(f"\n  TEST 1 persistence     min r {min(t1):.3f}  median {np.median(t1):.3f}"
          f"   {'PASS' if ok1 else 'FAIL'}   (need all >= 0.60, median >= 0.80)")
    print(f"  TEST 2 worth it        median gap closed {100*np.median(t2):.0f}%"
          f"          {'PASS' if ok2 else 'FAIL'}   (need >= 50%)")
    print(f"  TEST 3 scale invariant median r {np.median([r for r in t3 if r is not None]):.3f}"
          f"           {'PASS' if ok3 else 'FAIL'}   (need >= 0.80)")
    print(f"\n  VERDICT: {'mosaic is supported' if (ok1 and ok2) else 'mosaic NOT supported'}"
          + ("" if ok3 else " — and texture must be a distribution mapping, not a multiplier"))
    print("  One January pair is a weak persistence test. Confirm with July")
    print("  before committing, whatever this says.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
