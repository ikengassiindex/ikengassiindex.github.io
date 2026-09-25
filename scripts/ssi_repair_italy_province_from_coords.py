#!/usr/bin/env python3
"""Assign a province to the Italian records that carry none, from their coordinates.

    python3 scripts/ssi_repair_italy_province_from_coords.py            # dry run
    python3 scripts/ssi_repair_italy_province_from_coords.py --write

WHY
    346 of Italy's 41,662 records cannot be joined to any territorial C metric:
    300 carry the province "Unknown" and 46 carry a region name where a
    province belongs. Every one of them has a latitude and a longitude.

    They are not a missing measurement. They are a missing key, and a key can
    be recovered from geometry.

HOW
    Even-odd ray casting against the Eurostat GISCO NUTS 2024 boundaries at
    1:1 million, EPSG:4326, restricted to Italy's 107 NUTS-3 polygons. All
    rings of a multipart shape are tested together, so enclaves and holes
    resolve correctly by the even-odd rule.

    A point that falls in no polygon is left alone. It gets no province and
    therefore no C. Absent, not guessed.

WHAT IT WRITES
    `province` (the NUTS-3 code) and `region` (the province name), plus
    `_province_source` recording that the key was derived from coordinates
    rather than supplied. No score, no component and no measurement is touched.
"""
from __future__ import annotations
import argparse, os, pathlib, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Resolved, not assumed — see scripts/_ssi_gis_dir.py. This line used to
# hardcode ~/mnt/..., a Cowork device-VM mount path that does not exist on the
# operator's own machine.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _ssi_gis_dir import nuts_path          # noqa: E402
SHP = str(nuts_path())
VALID2 = {"ITC1","ITC2","ITC3","ITC4","ITF1","ITF2","ITF3","ITF4","ITF5","ITF6",
          "ITG1","ITG2","ITH1","ITH2","ITH3","ITH4","ITH5","ITI1","ITI2","ITI3","ITI4"}

def rings(shape):
    pts = shape.points
    idx = list(shape.parts) + [len(pts)]
    return [pts[idx[i]:idx[i+1]] for i in range(len(idx)-1)]

def inside(x, y, ring_list):
    """Even-odd ray casting across every ring. Holes resolve by parity."""
    c = False
    for ring in ring_list:
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i]; xj, yj = ring[j]
            if (yi > y) != (yj > y):
                xint = (xj - xi) * (y - yi) / (yj - yi) + xi
                if x < xint:
                    c = not c
            j = i
    return c

def load_polys():
    import shapefile
    sf = shapefile.Reader(SHP)
    flds = [f[0] for f in sf.fields[1:]]
    out = []
    for sr in sf.iterShapeRecords():
        r = dict(zip(flds, sr.record))
        if r.get("CNTR_CODE") == "IT" and int(r.get("LEVL_CODE", 9)) == 3:
            rl = rings(sr.shape)
            out.append((r["NUTS_ID"], r.get("NAME_LATN") or r.get("NUTS_NAME"),
                        tuple(sr.shape.bbox), rl))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data
    polys = load_polys()
    if len(polys) != 107:
        print(f"✗ expected 107 Italian NUTS-3 polygons, found {len(polys)}", file=sys.stderr); return 1
    print(f"✓ {len(polys)} Italian NUTS-3 polygons, GISCO NUTS 2024 1:1M EPSG:4326")

    manifest, subs, sharded = load_ssi_data("italy")
    need = [(i, s) for i, s in enumerate(subs)
            if (s.get("province") or "")[:4] not in VALID2]
    print(f"records lacking a usable province: {len(need)}")

    fixed, unresolved = collections.Counter(), 0
    for i, s in need:
        lat, lon = s.get("lat"), s.get("lon")
        if lat is None or lon is None:
            unresolved += 1; continue
        hit = None
        for nid, name, bb, rl in polys:
            if bb[0] <= lon <= bb[2] and bb[1] <= lat <= bb[3] and inside(lon, lat, rl):
                hit = (nid, name); break
        if hit is None:
            unresolved += 1; continue
        fixed[hit[1]] += 1
        if a.write:
            s["_province_before"] = s.get("province")
            s["_region_before"] = s.get("region")
            s["province"] = hit[0]
            s["region"] = hit[1]
            s["_province_source"] = ("derived from lat/lon by point-in-polygon against "
                                     "Eurostat GISCO NUTS 2024 1:1M EPSG:4326; the key was "
                                     "recovered, no measurement was assigned")
    n = sum(fixed.values())
    print(f"\nresolved {n} of {len(need)}   unresolved {unresolved} (left absent, not guessed)")
    for name, c in fixed.most_common(15):
        print(f"    {name:<26}{c:>5}")
    if len(fixed) > 15: print(f"    ... and {len(fixed)-15} more provinces")
    if a.write:
        save_ssi_data("italy", manifest, subs, sharded); print("\n✓ written")
    else:
        print("\n(dry run — nothing written)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
