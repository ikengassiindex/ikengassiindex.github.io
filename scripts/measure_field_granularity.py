#!/usr/bin/env python3
"""
Does a wind field actually vary between substations? Measure it, per country.

    python3 scripts/measure_field_granularity.py --file <a .nc field> [--countries a,b]

WHY THIS EXISTS
    I2's whole value is discrimination between substations. On ERA5 gust at
    0.25 deg it barely discriminates: 168,780 French substations share 1,138
    distinct cell values, and the UK fleet spans 6.2 m/s from P5 to P95.

    The proposed remedy is CERRA at 5.5 km. The expectation is that a genuine
    5.5 km reanalysis resolves local exposure that a 31 km field cannot. THE
    SAME EXPECTATION ABOUT ERA5-LAND WAS WRONG — its 10 m wind is ERA5's 0.25
    deg field interpolated, so sampling it at 0.1 deg would have produced MORE
    distinct values carrying the SAME information, and would have looked like
    a success. See FINDING_era5land_wind_is_interpolated.md.

    So the decision to spend on CERRA is not taken on the expectation. It is
    taken on this measurement, run identically on both fields.

    The numbers to beat, measured on ERA5 gust 0.25 deg, annual max 2018:

        country      substations   cells    CV     P5-P95 (m/s)
        france           168,780   1,138   0.096   23.2-30.5
        germany          108,016     850   0.113   22.4-33.0
        norway             6,113     683   0.149   21.9-35.9
        uk                59,744     664   0.066   26.5-32.7
        italy             41,662     661   0.169   19.8-34.3
        spain             12,438     916   0.105   20.6-30.0

    A finer field that does not raise CV materially is buying resolution
    without buying information, and that must be reported, not absorbed.

GRID HANDLING
    Regular lat/lon (ERA5): 1-D latitude and longitude coordinate variables.
    TESTED — it reproduces the table above.

    Projected curvilinear (CERRA): a Lambert Conformal Conic grid, carrying
    either 2-D latitude/longitude arrays or x/y axes with a grid_mapping.
    Substation coordinates are projected and indexed directly, because the
    grid is regular in PROJECTED space.
    *** UNTESTED. No CERRA file exists yet. The projection is read from the
    file, never reconstructed from documentation — a reconstruction that
    agrees to 5 km over 5,875 km is good enough to plan with and not good
    enough to derive published values from. ***
"""
from __future__ import annotations
import argparse, json, pathlib, sys

import numpy as np
import netCDF4

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIME_CHUNK = 40


def slugs():
    d = json.loads((ROOT / "intelligence" / "countries.json").read_text())
    return [c["slug"] for c in (d["countries"] if isinstance(d, dict) else d)]


def load(slug):
    man = json.loads((ROOT / slug / "ssi-data.json").read_text())
    sh = man.get("substations_shards")
    if not sh:
        return man.get("substations") or []
    out = []
    for e in sh:
        raw = json.loads((ROOT / slug / pathlib.Path(e["path"]).name).read_text())
        out.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
    return out


def field_name(ds):
    skip = {"latitude", "longitude", "valid_time", "time", "number", "expver",
            "lat", "lon", "x", "y", "crs", "Lambert_Conformal", "projection"}
    cand = [k for k, v in ds.variables.items()
            if k not in skip and len(v.dimensions) >= 3]
    if len(cand) != 1:
        raise ValueError(f"expected exactly one 3-D field, found {cand}")
    return cand[0]


class Grid:
    """Maps (lat, lon) -> (row, col). Two kinds, detected from the file."""

    def __init__(self, ds):
        self.kind = None
        lat = ds.variables.get("latitude", ds.variables.get("lat"))
        lon = ds.variables.get("longitude", ds.variables.get("lon"))
        if lat is not None and lat.ndim == 1 and lon is not None and lon.ndim == 1:
            self.kind = "latlon"
            self.lat = np.asarray(lat[:])
            self.lon = np.asarray(lon[:])
            self.shape = (len(self.lat), len(self.lon))
            self.res_km = abs(float(self.lat[1] - self.lat[0])) * 111.0
            return
        if lat is not None and lat.ndim == 2:
            self.kind = "curvilinear"
            self._init_curvilinear(np.asarray(lat[:]), np.asarray(lon[:]))
            return
        raise ValueError("cannot identify the grid from this file")

    def _init_curvilinear(self, lat2d, lon2d):
        """Nearest cell from the file's OWN 2-D coordinates. No projection.

        CERRA's netCDF carries latitude and longitude for all 1,069 x 1,069
        cells and NO grid_mapping variable and NO x/y axes. Reconstructing the
        Lambert Conformal Conic from documentation would place 620,000
        substations on a projection the file never states — and the earlier
        reconstruction, though it agreed to 5 km over 5,875 km, is exactly the
        kind of near-enough that should not carry published values.

        The coordinates are in the file. Use them: a KD-tree over the cells as
        unit-sphere Cartesian points gives the true nearest cell, and chord
        distance orders identically to great-circle distance, so the nearest
        neighbour is the same either way.
        """
        from scipy.spatial import cKDTree
        self.lat2d, self.lon2d = lat2d, lon2d
        self.shape = lat2d.shape
        la = np.radians(lat2d.ravel()); lo = np.radians(lon2d.ravel())
        pts = np.column_stack([np.cos(la)*np.cos(lo),
                               np.cos(la)*np.sin(lo), np.sin(la)])
        self.tree = cKDTree(pts)
        # resolution, measured from the grid rather than quoted
        mid = lat2d.shape[0]//2
        d = np.radians(lat2d[mid,1]-lat2d[mid,0])**2 + \
            (np.radians(lon2d[mid,1]-lon2d[mid,0])*np.cos(np.radians(lat2d[mid,0])))**2
        self.res_km = float(np.sqrt(d))*6371.0
        self.crs_name = "from file 2-D lat/lon, no projection assumed"

    def _init_projected(self, ds, lat2d, lon2d):
        """Read the projection FROM THE FILE. Never reconstruct it."""
        from pyproj import CRS, Transformer
        gm = None
        for k, v in ds.variables.items():
            if hasattr(v, "grid_mapping_name"):
                gm = v
                break
        if gm is None:
            raise ValueError("2-D coordinates but no grid_mapping variable — "
                             "refusing to guess the projection")
        attrs = {a: gm.getncattr(a) for a in gm.ncattrs()}
        crs = CRS.from_cf(attrs)
        self.tf = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        xv = ds.variables.get("x", ds.variables.get("xc"))
        yv = ds.variables.get("y", ds.variables.get("yc"))
        if xv is None or yv is None:
            raise ValueError("projected grid without x/y axes — not handled")
        self.x = np.asarray(xv[:], dtype="float64")
        self.y = np.asarray(yv[:], dtype="float64")
        self.shape = (len(self.y), len(self.x))
        self.res_km = abs(float(self.x[1] - self.x[0])) / 1000.0
        self.crs_name = crs.to_string()[:70]

    def index(self, lats, lons):
        if self.kind == "latlon":
            i = np.abs(self.lat[None, :] - np.asarray(lats)[:, None]).argmin(1)
            j = np.abs(self.lon[None, :] - np.asarray(lons)[:, None]).argmin(1)
            return i, j
        la = np.radians(np.asarray(lats)); lo = np.radians(np.asarray(lons))
        q = np.column_stack([np.cos(la)*np.cos(lo),
                             np.cos(la)*np.sin(lo), np.sin(la)])
        dist, flat = self.tree.query(q, k=1)
        i, j = np.unravel_index(flat, self.shape)
        # a substation outside the domain still returns its nearest EDGE cell,
        # so distance is the test, not index bounds. 2 cells is the cut.
        far = dist * 6371.0 > 2.0 * self.res_km
        return np.where(far, -1, i), np.where(far, -1, j)


def series_max(path, rows, cols, fld, nmax=0):
    """Max over time at each (row,col). Streamed; the maximum is associative."""
    ds = netCDF4.Dataset(str(path))
    var = ds.variables[fld]
    nt = var.shape[0] if not nmax else min(nmax, var.shape[0])
    rmin, rmax = int(rows.min()), int(rows.max())
    acc = np.full(len(rows), -np.inf, dtype="float64")
    for t0 in range(0, nt, TIME_CHUNK):
        blk = np.asarray(var[t0:t0 + TIME_CHUNK, rmin:rmax + 1, :],
                         dtype="float32")[:, rows - rmin, cols]
        acc = np.maximum(acc, np.nanmax(np.where(np.isfinite(blk), blk, -np.inf),
                                        axis=0))
    ds.close()
    acc[~np.isfinite(acc)] = np.nan
    return acc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--max-timesteps", type=int, default=0,
                    help="use only the first N timesteps. REQUIRED for a "
                         "like-for-like comparison between fields of "
                         "different temporal resolution: an annual maximum is "
                         "dominated by one broad storm and shows LESS spatial "
                         "spread than a monthly maximum, so comparing a year "
                         "of one field against a month of another inflates "
                         "the finer field's apparent advantage.")
    ap.add_argument("--countries", default=None,
                    help="comma-separated slugs; default is the six baselined")
    a = ap.parse_args()

    p = pathlib.Path(a.file)
    ds = netCDF4.Dataset(str(p))
    fld = field_name(ds)
    g = Grid(ds)
    nt = ds.variables[fld].shape[0]
    ds.close()

    print(f"\n  {p.name}   {p.stat().st_size/1e6:,.1f} MB")
    print(f"  field '{fld}' · grid {g.shape} · {g.kind} · ~{g.res_km:.1f} km"
          + (f" · {g.crs_name}" if g.kind == "projected" else ""))
    used = min(a.max_timesteps, nt) if a.max_timesteps else nt
    print(f"  {nt} timesteps in file · USING {used}\n")

    want = (a.countries.split(",") if a.countries
            else ["france", "germany", "norway", "uk", "italy", "spain"])
    print(f"  {'country':<14}{'subs':>9}{'in grid':>9}{'cells':>8}"
          f"{'mean':>8}{'sd':>7}{'CV':>7}{'P5-P95':>15}")
    for slug in want:
        try:
            subs = load(slug)
        except Exception as ex:
            print(f"  {slug:<14}REFUSED — {ex}")
            continue
        la = np.array([s["lat"] for s in subs
                       if isinstance(s.get("lat"), (int, float))])
        lo = np.array([s["lon"] for s in subs
                       if isinstance(s.get("lon"), (int, float))])
        del subs
        if not len(la):
            continue
        i, j = g.index(la, lo)
        ok = (i >= 0) & (j >= 0)
        if not ok.any():
            print(f"  {slug:<14}{len(la):>9,}{0:>9}   entirely outside this grid")
            continue
        v = series_max(p, i[ok], j[ok], fld, a.max_timesteps)
        v = v[np.isfinite(v)]
        if len(v) < 2:
            continue
        ncell = len(set(zip(i[ok].tolist(), j[ok].tolist())))
        print(f"  {slug:<14}{len(la):>9,}{int(ok.sum()):>9,}{ncell:>8,}"
              f"{v.mean():>8.2f}{v.std():>7.2f}{v.std()/v.mean():>7.3f}"
              f"{np.percentile(v,5):>8.1f}-{np.percentile(v,95):<6.1f}")

    print("\n  CV is the between-substation spread WITHIN a country. It is the")
    print("  number that decides whether a finer field is worth its cost:")
    print("  more distinct cells with the same CV is resolution without")
    print("  information, which is what ERA5-Land would have delivered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
