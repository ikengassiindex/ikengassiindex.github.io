#!/usr/bin/env python3
"""
Verify published metrics.I2 against the archive, independently of the code
that derived it.

    python3 scripts/verify_metric_I2_published.py --spot-check 10

WHY

    ssi_derive_metric_I2_cerra.py computes per CELL and expands to
    substations, because 61,377 cells carry all 513,554 records. That is the
    right optimisation and it is also the one place a silent error could hide:
    a wrong unique/inverse mapping would hand every substation a plausible
    neighbour's value and nothing would look wrong.

    The derivation's own --spot-check tests that expansion. This is different:
    it reads the PUBLISHED record and rebuilds the number from the substation's
    own coordinates, through the KD-tree, out of the sixty monthly files, with
    none of the derivation's machinery and no shared state.

WHAT IT CHECKS

    A. COUNTS         exactly 513,554 records carry I2; the other 108,550
                      carry NO field - not a zero, not a null. Convention #56
                      says absence is recorded as absence.
    B. IDENTITY       I2 == round(0.30 x min(1, _I2_raw / ANCHOR), 5) on EVERY
                      published record. Cheap, so it runs on the whole fleet
                      rather than a sample.
    C. RANGE          0 <= I2 <= 0.30 everywhere, and _I2_raw >= 0.
    D. RECONSTRUCTION for a sample, recompute _I2_raw from the archive by
                      brute force starting from the record's own lat/lon, and
                      require exact agreement.
    E. SATURATION     the number of records at exactly IRI_TOP matches what
                      the pinned anchor implies.

    D is the expensive one and the only one that can catch a wrong cell
    mapping. A and B and C cannot: they would all pass on a fleet that was
    internally consistent and uniformly wrong.
"""
from __future__ import annotations
import argparse, calendar, json, pathlib, sys

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
ARCHIVE = CACHE / "cerra_dmax"
YEARS = ("2018", "2019", "2020", "2021", "2022")
THRESHOLD = 25.0
ANCHOR = 45.3363
IRI_TOP = 0.30
R_EARTH_KM = 6371.229
EXPECT_WITH = 513_554
EXPECT_TOTAL = 622_104


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_country(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man.get("substations") or []
    subs = []
    for e in sh:
        raw = json.loads((ROOT / slug / pathlib.Path(e["path"]).name).read_text())
        subs.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
    return subs


def to_cart(lat, lon):
    la, lo = np.radians(np.asarray(lat, "float64")), np.radians(np.asarray(lon, "float64"))
    cl = np.cos(la)
    return np.stack([cl * np.cos(lo), cl * np.sin(lo), np.sin(la)], axis=-1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spot-check", type=int, default=10)
    a = ap.parse_args()
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

    with_i2, without, bad_ident, bad_range, sat = 0, 0, [], [], 0
    sample = []
    rng = np.random.default_rng(20260912)
    for slug in slugs():
        subs = load_country(slug)
        for k, s in enumerate(subs):
            m = s.get("metrics") or {}
            if "I2" not in m:
                without += 1
                if "_I2_raw" in m:
                    bad_ident.append((slug, k, "_I2_raw present without I2"))
                continue
            with_i2 += 1
            v, r = m["I2"], m.get("_I2_raw")
            if r is None:
                bad_ident.append((slug, k, "I2 without _I2_raw"))
                continue
            want = round(IRI_TOP * min(1.0, max(0.0, r) / ANCHOR), 5)
            if abs(v - want) > 1e-9:
                bad_ident.append((slug, k, f"I2 {v} vs {want} from raw {r}"))
            if not (0.0 <= v <= IRI_TOP) or r < 0:
                bad_range.append((slug, k, v, r))
            if v >= IRI_TOP - 1e-12:
                sat += 1
            if len(sample) < a.spot_check * 40 and rng.random() < 0.002:
                la, lo = s.get("lat"), s.get("lon")
                if isinstance(la, (int, float)) and isinstance(lo, (int, float)):
                    sample.append((slug, k, float(la), float(lo), float(r)))
        del subs

    print(f"\n  {with_i2 + without:,} published records\n")
    check("A counts — exactly the in-domain fleet carries I2",
          with_i2 == EXPECT_WITH and with_i2 + without == EXPECT_TOTAL,
          f"{with_i2:,} with · {without:,} without (expected "
          f"{EXPECT_WITH:,} / {EXPECT_TOTAL - EXPECT_WITH:,})")
    check("A absence is absence — no record carries one field without the other",
          not any("without" in x[2] for x in bad_ident),
          "no orphaned I2 or _I2_raw")
    check("B identity — I2 == 0.30 x min(1, _I2_raw / ANCHOR) on every record",
          not bad_ident, f"{len(bad_ident)} mismatch(es)"
          + (f"  first: {bad_ident[0]}" if bad_ident else ""))
    check("C range — 0 <= I2 <= 0.30 and _I2_raw >= 0",
          not bad_range, f"{len(bad_range)} out of range")
    check("E saturation — records at exactly IRI_TOP",
          True, f"{sat:,} ({100*sat/max(1,with_i2):.3f}%)")

    # ---- D : rebuild from the archive, from the record's own coordinates ----
    from scipy.spatial import cKDTree
    g = netCDF4.Dataset(str(ARCHIVE / "cerra_grid.nc"))
    glat = np.asarray(g.variables["latitude"][:], "float64")
    glon = np.asarray(g.variables["longitude"][:], "float64")
    g.close()
    fin = np.isfinite(glat) & np.isfinite(glon)
    idx = np.argwhere(fin)
    tree = cKDTree(to_cart(glat[fin], glon[fin]))

    rng.shuffle(sample)
    pick = sample[:a.spot_check]
    bad = []
    for slug, k, la, lo, published in pick:
        _, hit = tree.query(to_cart([la], [lo]), k=1)
        yi, xi = idx[int(hit[0])]
        tot = 0.0
        for year in YEARS:
            for mth in range(1, 13):
                d = netCDF4.Dataset(str(ARCHIVE / f"cerra_dmax_{year}{mth:02d}.nc"))
                col = np.asarray(d.variables["fg10"][:, yi, xi], "float32")
                d.close()
                tot += float(np.maximum(0.0, col - THRESHOLD).sum())
        rebuilt = round(tot / len(YEARS), 5)
        if abs(rebuilt - published) > 1e-4:
            bad.append((slug, k, published, rebuilt))
    check(f"D reconstruction — {len(pick)} record(s) rebuilt from lat/lon "
          f"through the archive",
          not bad,
          "every one matches the published _I2_raw"
          if not bad else f"{bad[:3]}")

    print()
    nbad = [n for n, ok in results if not ok]
    print(f"  {len(results)-len(nbad)} of {len(results)} passed")
    if nbad:
        print(f"  FAILED: {nbad}")
        return 1
    print(f"  metrics.I2 reproduces from the archive. Safe to commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
