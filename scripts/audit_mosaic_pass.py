#!/usr/bin/env python3
"""
Scrutinise the PASS as hard as the failure. Two doubts about attempt 2.

    python3 scripts/audit_mosaic_pass.py

Attempt 2 (texture from the period MEAN) passed all three bars: persistence
min r 0.842 / median 0.873, gap closed 265 per cent, scale invariance 0.937.

Two of those numbers deserve less trust than they look.

DOUBT 1 — T3 did not test what the construction needs
    T3 compares texture(chosen statistic) against texture(MEDIAN). With the
    mean chosen, it compared the MEAN against the MEDIAN — two central
    statistics, which agree almost by definition. r = 0.937 is close to
    meaningless as a check.

    The construction estimates texture from the MEAN and applies it to a daily
    series whose EXTREMES drive a threshold-excess metric. The question is
    therefore whether mean-derived texture transfers to maxima. That was never
    tested. Attempt 1 gives a hint in the wrong direction: max-derived texture
    was itself unstable.

DOUBT 2 — T2 compared against the wrong baseline
    T2 measured the mosaic CV against the CV of CERRA's MAX field. But the
    texture came from CERRA's MEAN field, and the mosaic multiplies it by
    ERA5's MAX. Three different statistics in one comparison.

    A mean field and a max field do not have the same spatial spread: maxima
    are set by broad storms that flatten spatial contrast, while means retain
    terrain contrast. So the mosaic overshooting CERRA's MAX CV by 265-665 per
    cent may be a baseline mismatch rather than the injected noise that the
    same signature indicated in attempt 1.

    Either way the number does not support a conclusion, and reporting "265
    per cent of the gap closed" as a success would be the kind of thing this
    estate exists to catch.

Neither doubt touches TEST 1. Persistence at r 0.84-0.96 across six countries
and two years stands, and it is the finding that matters: mean-derived texture
is a stable property of the site.
"""
from __future__ import annotations
import importlib.util, pathlib, sys
import numpy as np, netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location(
    "tp", str(ROOT / "scripts" / "test_texture_persistence.py"))
tp = importlib.util.module_from_spec(_s); _s.loader.exec_module(tp)
mf = tp.mf

C = ROOT / "scripts" / "pipeline" / ".cache"
A = C / "cerra_gust_probe_201801.nc"
E5 = C / "era5land_i2gust_r0_1wgspp_2018.nc"
COUNTRIES = ["france", "germany", "uk", "italy"]


def main() -> int:
    dsc = netCDF4.Dataset(str(E5)); cg = mf.Grid(dsc); dsc.close()

    print("\n  DOUBT 1 — does MEAN-derived texture transfer to MAXIMA?")
    print("  T3 compared mean-texture with MEDIAN-texture: two central")
    print("  statistics. The metric is driven by extremes. This is the test.\n")
    gA, tex_mean, stat_mean = tp.texture_field(str(A), cg, how="mean")
    idx = {}
    for slug in COUNTRIES:
        la, lo = tp.subs_of(slug)
        i, j = gA.index(la, lo)
        ok = (i >= 0) & (j >= 0)
        idx[slug] = (i[ok], j[ok])
    tm = {s: tex_mean[i, j] for s, (i, j) in idx.items()}
    sm = {s: stat_mean[i, j] for s, (i, j) in idx.items()}
    del tex_mean, stat_mean, gA

    gA, tex_max, stat_max = tp.texture_field(str(A), cg, how="max")
    print(f"  {'country':<10}{'n':>9}{'r(mean,max)':>14}   verdict")
    rs = []
    for slug in COUNTRIES:
        i, j = idx[slug]
        r = tp.pearson(tm[slug], tex_max[i, j])
        rs.append(r)
        print(f"  {slug:<10}{len(i):>9,}{r:>14.3f}   "
              f"{'transfers' if r >= 0.80 else 'DOES NOT TRANSFER'}")
    print(f"\n  median r {np.median(rs):.3f}   "
          f"{'PASS' if np.median(rs) >= 0.80 else 'FAIL'}  (bar 0.80, the same "
          f"bar T3 used)")

    print("\n  DOUBT 2 — was T2 measured against the right baseline?")
    print(f"  {'country':<10}{'CV cerra MAX':>14}{'CV cerra MEAN':>15}"
          f"{'ratio':>8}")
    for slug in COUNTRIES:
        i, j = idx[slug]
        vmax = stat_max[i, j]; vmean = sm[slug]
        vmax = vmax[np.isfinite(vmax)]; vmean = vmean[np.isfinite(vmean)]
        cmax = vmax.std() / vmax.mean(); cmean = vmean.std() / vmean.mean()
        print(f"  {slug:<10}{cmax:>14.3f}{cmean:>15.3f}{cmean/cmax:>8.2f}x")
    print("\n  If the MEAN field's CV is much larger than the MAX field's, the")
    print("  mosaic's apparent overshoot is a baseline mismatch, not noise —")
    print("  and T2 must be re-stated against the mean-field baseline before")
    print("  it means anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
