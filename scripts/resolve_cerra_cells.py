#!/usr/bin/env python3
"""
Resolve every substation in the estate to a CERRA grid cell, once, and audit it.

    python3 scripts/resolve_cerra_cells.py --grid-file <a CERRA .nc>
    python3 scripts/resolve_cerra_cells.py --report

WHY THIS IS ITS OWN STEP
    CERRA is not a lat/lon grid. It is Lambert Conformal Conic, 1069 x 1069 at
    5.5 km, and the netCDF the CDS returns carries TWO-DIMENSIONAL latitude and
    longitude arrays with NO grid_mapping variable and NO x/y coordinate axes -
    checked on the January probe, not assumed. There is nothing to do
    `abs(lat - la).argmin()` against. The ERA5 resolver in
    ssi_derive_metric_I1/I2 cannot be reused and must not be adapted by hand
    inside a derivation script.

    So the mapping is computed once here, audited here, written to disk here,
    and the derivation reads it. If the resolution is wrong, it is wrong in one
    place with one set of numbers attached to it, rather than silently inside
    whichever metric happened to run.

HOW
    A KD-tree over the grid's own latitude/longitude arrays, projected to unit
    -sphere Cartesian. Cartesian, not degrees: a degree of longitude is 111 km
    at the equator and 43 km at Trondheim, and this domain reaches 72 N, so a
    nearest neighbour found in degree space is not the nearest neighbour. No
    projection is reconstructed and no PROJ string is trusted - the file's own
    coordinates are the authority.

IN OR OUT OF THE DOMAIN
    CERRA covers Europe and no more. A substation in Chile has a nearest CERRA
    cell like any other point on the sphere; it is simply thousands of km away.
    A point is INSIDE when its nearest cell centre is within MAX_KM. The cell
    is 5.5 km square, so the furthest an interior point can sit from its own
    cell centre is half the diagonal, 3.889 km. MAX_KM is set to 4.0: tight
    enough that no exterior point can pass, loose enough that no interior point
    can fail.

    The distance histogram is printed so the cut can be seen rather than
    trusted. A well-formed answer has a dense mass below 3.9 km, then nothing
    at all until the exterior points appear far away. A smear across the cut
    would mean the reading is wrong, and it would be visible.

CONVENTION #56
    A substation without coordinates is skipped and counted, never defaulted. A
    substation outside the domain is recorded as outside and counted; I2 is
    declared ABSENT for it. Nothing is snapped across the boundary and nothing
    is extrapolated inward.

OUTPUT
    scripts/pipeline/.cache/cerra_cell_map.npz
        slug_id   int16    index into the 'slugs' array
        sub_index int32    position in that country's substation list
        i, j      int16    CERRA grid indices (y, x)
        dist_km   float32  substation to cell-centre distance
        slugs     <U32     the country slugs, in order
        grid_file <U128    the file the grid was read from
    Only substations INSIDE the domain appear. Absence is the record.
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scripts" / "pipeline" / ".cache"
OUT = CACHE / "cerra_cell_map.npz"
MAX_KM = 4.0
R_EARTH_KM = 6371.229          # the radius CERRA's own GRIB header declares


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load_subs(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man.get("substations") or []
    subs = []
    for e in sh:
        p = ROOT / slug / pathlib.Path(e["path"]).name
        raw = json.loads(p.read_text())
        subs.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
    return subs


def to_cartesian(lat_deg, lon_deg):
    import numpy as np
    la = np.radians(np.asarray(lat_deg, dtype="float64"))
    lo = np.radians(np.asarray(lon_deg, dtype="float64"))
    cl = np.cos(la)
    return np.stack([cl * np.cos(lo), cl * np.sin(lo), np.sin(la)], axis=-1)


def build(grid_file: pathlib.Path) -> int:
    import numpy as np, netCDF4
    from scipy.spatial import cKDTree

    ds = netCDF4.Dataset(str(grid_file))
    if "latitude" not in ds.variables or "longitude" not in ds.variables:
        sys.exit(f"{grid_file.name}: no latitude/longitude variables")
    glat = np.asarray(ds.variables["latitude"][:], dtype="float64")
    glon = np.asarray(ds.variables["longitude"][:], dtype="float64")
    if glat.ndim != 2:
        sys.exit(f"{grid_file.name}: latitude is {glat.ndim}-D, expected 2-D. "
                 f"This resolver is for the curvilinear CERRA grid only.")
    ny, nx = glat.shape
    has_map = [k for k in ds.variables
               if "grid_mapping" in getattr(ds.variables[k], "ncattrs", lambda: [])()]
    ds.close()
    print(f"\n  grid   {grid_file.name}   {ny} x {nx} = {ny*nx:,} cells")
    print(f"         2-D lat/lon, grid_mapping present on: "
          f"{has_map or 'nothing — as expected'}")
    print(f"         lat {np.nanmin(glat):.3f} .. {np.nanmax(glat):.3f}   "
          f"lon {np.nanmin(glon):.3f} .. {np.nanmax(glon):.3f}")

    fin = np.isfinite(glat) & np.isfinite(glon)
    idx = np.argwhere(fin)
    tree = cKDTree(to_cartesian(glat[fin], glon[fin]))
    print(f"         {len(idx):,} cells with finite coordinates -> KD-tree built")

    all_slugs = slugs()
    S, K, I, J, D = [], [], [], [], []
    nocoord = 0
    rows = []
    for sid, slug in enumerate(all_slugs):
        try:
            subs = load_subs(slug)
        except Exception as ex:
            print(f"  {slug:<16} REFUSED — {type(ex).__name__}: {ex}")
            continue
        la, lo, ks = [], [], []
        for k, s in enumerate(subs):
            a, b = s.get("lat"), s.get("lon")
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                nocoord += 1
                continue
            la.append(float(a)); lo.append(float(b)); ks.append(k)
        n_total = len(subs)
        del subs
        if not ks:
            rows.append((slug, n_total, 0, 0.0, None, None))
            continue
        d_chord, hit = tree.query(to_cartesian(la, lo), k=1, workers=-1)
        # chord length on the unit sphere -> great-circle km
        d_km = 2.0 * R_EARTH_KM * np.arcsin(np.clip(np.asarray(d_chord) / 2.0, 0, 1))
        inside = d_km <= MAX_KM
        n_in = int(inside.sum())
        rows.append((slug, n_total, n_in,
                     100.0 * n_in / n_total if n_total else 0.0,
                     float(d_km[inside].max()) if n_in else None,
                     float(np.median(d_km[inside])) if n_in else None))
        if n_in:
            cells = idx[np.asarray(hit)[inside]]
            S.append(np.full(n_in, sid, dtype="int16"))
            K.append(np.asarray(ks, dtype="int32")[inside])
            I.append(cells[:, 0].astype("int16"))
            J.append(cells[:, 1].astype("int16"))
            D.append(d_km[inside].astype("float32"))

    print(f"\n  {'country':<16}{'total':>9}{'inside':>9}{'%':>7}"
          f"{'median km':>11}{'max km':>9}")
    tot = ins = 0
    for slug, n, ni, pc, mx, md in rows:
        tot += n; ins += ni
        print(f"  {slug:<16}{n:>9,}{ni:>9,}{pc:>6.1f}%"
              f"{(f'{md:.3f}' if md is not None else '-'):>11}"
              f"{(f'{mx:.3f}' if mx is not None else '-'):>9}")
    print(f"  {'TOTAL':<16}{tot:>9,}{ins:>9,}"
          f"{100.0*ins/tot if tot else 0:>6.1f}%")
    print(f"  {nocoord:,} substations without coordinates, skipped and counted")

    if not S:
        sys.exit("no substation resolved — nothing written")

    import numpy as np
    np.savez_compressed(
        OUT,
        slug_id=np.concatenate(S), sub_index=np.concatenate(K),
        i=np.concatenate(I), j=np.concatenate(J), dist_km=np.concatenate(D),
        slugs=np.array(all_slugs, dtype="<U32"),
        grid_file=np.array(grid_file.name, dtype="<U128"),
        max_km=np.array(MAX_KM), grid_shape=np.array([ny, nx]))
    print(f"\n  written {OUT.name}  {OUT.stat().st_size/1e6:.1f} MB")
    return report()


def report() -> int:
    import numpy as np
    if not OUT.exists():
        sys.exit("no cerra_cell_map.npz — run with --grid-file first")
    z = np.load(OUT, allow_pickle=False)
    d = z["dist_km"]
    print(f"\n  DISTANCE HISTOGRAM — {len(d):,} resolved substations")
    edges = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 3.889, 4.0]
    for lo, hi in zip(edges[:-1], edges[1:]):
        n = int(((d >= lo) & (d < hi)).sum())
        bar = "#" * int(60 * n / max(1, len(d)))
        print(f"    {lo:>5.3f} - {hi:<5.3f} km  {n:>8,}  {bar}")
    over = int((d > 3.889).sum())
    print(f"\n    beyond half a cell diagonal (3.889 km): {over:,} "
          f"({100*over/len(d):.4f}%)")
    print(f"    A cell is 5.5 km square, so an interior point cannot exceed")
    print(f"    3.889 km from its own centre. A non-zero count here is not a")
    print(f"    rounding artefact — it is grid edge, and it must be explained.")
    print(f"\n    max {d.max():.4f} km   median {np.median(d):.4f} km")
    cells = np.unique(z["i"].astype("int32") * 10000 + z["j"].astype("int32"))
    print(f"    {len(cells):,} distinct CERRA cells carry "
          f"{len(d):,} substations "
          f"({len(d)/len(cells):.2f} per occupied cell)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-file")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report and not a.grid_file:
        return report()
    if not a.grid_file:
        cand = sorted(CACHE.glob("cerra_gust_*.nc"))
        if not cand:
            ap.error("give --grid-file (no cerra_gust_*.nc in the cache)")
        a.grid_file = str(cand[0])
        print(f"  no --grid-file given; using {pathlib.Path(a.grid_file).name}")
    return build(pathlib.Path(a.grid_file))


if __name__ == "__main__":
    sys.exit(main())
