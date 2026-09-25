#!/usr/bin/env python3
"""measure_grid_cell_collapse.py — how many DISTINCT hazard values can a
gridded raster give 622,104 substations?

Asked before the fetch-and-sample layer is written, because the answer decides
both its shape and something the index will have to declare.

A reanalysis raster has a cell size. Every asset inside one cell receives the
SAME value — not approximately, identically. So the number of distinct hazard
values available to the estate is not 622,104; it is the number of occupied
cells. This script measures that, per resolution and per country.

It also reads the CURRENT published hazard modifiers and counts their distinct
values inside each cell, because those modifiers are name-hash derived and
therefore vary per asset. Replacing them with real raster data will make them
LESS varied within a cell. That is a correction, and it will look like a
regression to anyone who has not been told in advance.

    python3 scripts/measure_grid_cell_collapse.py
"""
from __future__ import annotations
import collections
import glob
import json
import os
import sys

RESOLUTIONS = [0.5, 0.25, 0.1]          # ERA5 / CEMS offer 0.25 and 0.5
HAZARD_KEYS = ["R6d_wildfire", "R6e_winter", "R6c_flood"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_country(slug):
    """Two shapes exist in the estate. Read whichever this country uses."""
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


def cell(lat, lon, res):
    return (round(lat / res), round(lon / res))


def main():
    slugs = json.load(open(os.path.join(ROOT, "intelligence", "countries.json"),
                           encoding="utf-8"))["slugs"]
    total = 0
    global_cells = {r: set() for r in RESOLUTIONS}
    per_country = {}
    occupancy = collections.Counter()          # assets per 0.25 deg cell
    # GLOBAL, so a border cell is one cell and not one per country. Holding
    # the RECORDS here exhausted memory at 622,104 across 39 files; keep only
    # the count and the distinct hazard values, which is all that is read.
    cell_count = collections.Counter()
    cell_values = collections.defaultdict(lambda: collections.defaultdict(set))
    distinct_now = collections.Counter()       # distinct published values per cell
    missing_geo = 0

    for slug in sorted(slugs):
        recs = load_country(slug)
        if not recs:
            print("  NO DATA: %s" % slug, file=sys.stderr)
            continue
        cc = {r: set() for r in RESOLUTIONS}
        for rec in recs:
            la, lo = rec.get("lat"), rec.get("lon")
            total += 1
            if la is None or lo is None:
                missing_geo += 1
                continue
            for r in RESOLUTIONS:
                k = cell(la, lo, r)
                cc[r].add(k)
                global_cells[r].add(k)
            k = cell(la, lo, 0.25)
            cell_count[k] += 1
            mods = rec.get("modifiers") or {}
            for hk in HAZARD_KEYS:
                v = mods.get(hk)
                if v is not None:
                    cell_values[k][hk].add(v)
        per_country[slug] = (len(recs), {r: len(cc[r]) for r in RESOLUTIONS})
        del recs

    # Occupancy is computed GLOBALLY, not per country. A 0.25 deg cell on a
    # border holds assets from two countries and is one cell to the raster;
    # counting it once per country inflated the total by 529 cells when this
    # was first written.
    for k, n_in_cell in cell_count.items():
        occupancy[n_in_cell] += 1
        for hk in HAZARD_KEYS:
            distinct_now[(hk, n_in_cell > 1)] += len(cell_values[k][hk])

    print("assets: %d   without coordinates: %d" % (total, missing_geo))
    print("\nDISTINCT HAZARD VALUES AVAILABLE, by raster resolution")
    for r in RESOLUTIONS:
        n = len(global_cells[r])
        print("  %.2f deg  %7d occupied cells   %5.1fx collapse   %.2f%% of assets"
              % (r, n, total / n, 100.0 * n / total))

    print("\nOCCUPANCY at 0.25 deg — how many assets share one hazard value")
    shared = sum(c for k, c in occupancy.items() if k > 1)
    alone = occupancy.get(1, 0)
    assets_shared = sum(k * c for k, c in occupancy.items() if k > 1)
    print("  cells holding exactly one asset : %6d" % alone)
    print("  cells holding more than one     : %6d" % shared)
    print("  assets sharing a cell           : %6d  (%.1f%% of the estate)"
          % (assets_shared, 100.0 * assets_shared / total))
    print("  largest single cell             : %6d assets" % max(occupancy))

    print("\nWHAT THE PUBLISHED MODIFIERS DO TODAY, inside multi-asset cells")
    for hk in HAZARD_KEYS:
        d = distinct_now[(hk, True)]
        print("  %-14s %7d distinct values across %d shared cells"
              % (hk, d, shared))
    print("  A raster can supply exactly ONE value per cell. Every distinct")
    print("  value above beyond one per cell is variation the data cannot")
    print("  justify — it is the name hash, not the hazard.")

    print("\nDENSEST AND SPARSEST at 0.25 deg")
    ranked = sorted(per_country.items(), key=lambda kv: -kv[1][0] / max(1, kv[1][1][0.25]))
    for label, rows in (("densest", ranked[:5]), ("sparsest", ranked[-5:])):
        print("  %s:" % label)
        for slug, (a, cs) in rows:
            print("    %-14s %7d assets %6d cells  %6.1f per cell"
                  % (slug, a, cs[0.25], a / max(1, cs[0.25])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
