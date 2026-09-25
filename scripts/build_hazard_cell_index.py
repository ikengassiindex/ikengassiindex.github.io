#!/usr/bin/env python3
"""build_hazard_cell_index.py — the one authoritative map from 622,104 assets
to the raster cells that can actually carry a hazard value.

Why this is an artefact and not a helper function: every hazard leg — fire,
winter, flood, and anything after them — must use the SAME asset-to-cell
assignment, or two legs will disagree about which substations share a value
and no one will be able to say which is right. Built once, read by all.

Established by RESULT_a_raster_can_give_25165_values_not_622104.md: a 0.25 deg
raster carries 25,165 distinct values for this estate, 99.1 % of assets share
a cell, and requesting a finer grid manufactures resolution the data does not
have.

THE CONVENTION, fixed here and stated in the artefact.

    cell_index = floor(coord / resolution + 0.5)
    cell_centre = cell_index * resolution

NOT Python's round(). round() is banker's rounding: an exact half-cell tie goes
to the EVEN multiple, so the tie-break depends on where you are on the grid,
and it is asymmetric across zero — round(-1.5) is -2 while round(1.5) is 2. A
nearest-neighbour rule whose direction depends on position is not a rule.

Measured on the estate: the two conventions disagree for exactly **2 assets of
622,104** (one in Hungary at lon 19.125, one in Switzerland at lat 47.125) and
both give 25,165 cells, so no published figure changes. The convention is fixed
because it should be, not because it moved a number.

LONGITUDE. The estate stores signed longitudes, -180..180. ERA5 publishes on
0..359.75. Both are recorded per cell so neither the sampler nor an auditor has
to guess which one a file is on.

    python3 scripts/build_hazard_cell_index.py            # writes the artefact
    python3 scripts/build_hazard_cell_index.py --check    # verify, write nothing
"""
from __future__ import annotations
import argparse
import collections
import datetime as _dt
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "hazard_cell_index.json")
RESOLUTION = 0.25          # ERA5 and CEMS native. See the RESULT: do not refine.


def cell_index(coord, res=RESOLUTION):
    """Nearest grid point, with a tie-break that does not depend on position."""
    return math.floor(coord / res + 0.5)


def load_country(slug):
    """Two record shapes exist in the estate; read whichever this country uses."""
    recs = []
    for f in sorted(glob.glob(os.path.join(ROOT, slug, "ssi-data-substations-*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        recs += d if isinstance(d, list) else next(
            (v for v in d.values() if isinstance(v, list)), [])
    if not recs:
        p = os.path.join(ROOT, slug, "ssi-data.json")
        if os.path.exists(p):
            recs = json.load(open(p, encoding="utf-8")).get("substations", [])
    return recs


def build():
    slugs = json.load(open(os.path.join(ROOT, "intelligence", "countries.json"),
                           encoding="utf-8"))["slugs"]
    ordinal = {}                                   # (i, j) -> ordinal
    cells = []                                     # ordinal -> (i, j)
    per_country = {}
    occupancy = collections.Counter()
    n_assets = 0
    no_geo = []

    for slug in sorted(slugs):
        recs = load_country(slug)
        if not recs:
            raise SystemExit("no per-asset data found for %s — refusing to write a "
                             "partial index" % slug)
        seen = set()
        for rec in recs:
            n_assets += 1
            la, lo = rec.get("lat"), rec.get("lon")
            if la is None or lo is None:
                no_geo.append((slug, rec.get("substation_id")))
                continue
            key = (cell_index(la), cell_index(lo))
            o = ordinal.get(key)
            if o is None:
                o = ordinal[key] = len(cells)
                cells.append(key)
            seen.add(o)
            occupancy[o] += 1
        per_country[slug] = {"assets": len(recs), "cells": sorted(seen)}
        del recs

    if no_geo:
        # Section 7.5: no silent absence. An asset with no coordinates cannot be
        # sampled, and the index says so by name rather than dropping it.
        raise SystemExit("%d assets have no coordinates; the index refuses to hide "
                         "them: %s" % (len(no_geo), no_geo[:5]))

    shared = sum(1 for o in range(len(cells)) if occupancy[o] > 1)
    return {
        "_generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_authority": "RESULT_a_raster_can_give_25165_values_not_622104.md",
        "resolution_deg": RESOLUTION,
        "convention": "cell_index = floor(coord/resolution + 0.5); "
                      "centre = cell_index * resolution. NOT python round(), "
                      "which is banker's rounding and position-dependent.",
        "longitude_note": "lon_signed is -180..180 as the estate stores it; "
                          "lon_era5 is 0..359.75 as ERA5 publishes it.",
        "n_assets": n_assets,
        "n_cells": len(cells),
        "n_cells_shared": shared,
        "n_assets_sharing": sum(occupancy[o] for o in range(len(cells))
                                if occupancy[o] > 1),
        "largest_cell_assets": max(occupancy.values()),
        "cells": [
            {
                "o": o,
                "lat": round(i * RESOLUTION, 4),
                "lon_signed": round(j * RESOLUTION, 4),
                "lon_era5": round((j * RESOLUTION) % 360.0, 4),
                "n": occupancy[o],
            }
            for o, (i, j) in enumerate(cells)
        ],
        "countries": per_country,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild and compare against the artefact on disk; write nothing")
    a = ap.parse_args()
    idx = build()

    print("assets            %7d" % idx["n_assets"])
    print("cells at %.2f deg  %7d   (%.2f%% of assets)"
          % (idx["resolution_deg"], idx["n_cells"],
             100.0 * idx["n_cells"] / idx["n_assets"]))
    print("cells shared      %7d" % idx["n_cells_shared"])
    print("assets sharing    %7d   (%.1f%% of the estate)"
          % (idx["n_assets_sharing"],
             100.0 * idx["n_assets_sharing"] / idx["n_assets"]))
    print("largest cell      %7d assets" % idx["largest_cell_assets"])

    if a.check:
        if not os.path.exists(OUT):
            print("\nNO ARTEFACT on disk at %s" % OUT); return 1
        old = json.load(open(OUT, encoding="utf-8"))
        same = all(old.get(k) == idx.get(k) for k in
                   ("resolution_deg", "n_assets", "n_cells", "n_cells_shared",
                    "n_assets_sharing", "largest_cell_assets"))
        print("\nartefact on disk %s" % ("MATCHES" if same else "DIFFERS — rebuild"))
        return 0 if same else 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, separators=(",", ":"))
    print("\nwrote %s (%.1f MB)" % (OUT, os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
