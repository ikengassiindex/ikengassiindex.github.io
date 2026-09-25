#!/usr/bin/env python3
"""fetch_jrc_flood.py — select and fetch only the JRC flood tiles this estate needs.

The Global River Flood Hazard Maps are 271 tiles of 10 x 10 degrees. This estate
occupies 115 of them. Fetching the other 156 would be downloading Siberia and
the Sahara to score substations in Portugal.

RUN IT ON THE MAC, in the operator's own Terminal, as with the Overpass fetch on
30 August. The data host is not on the Cowork egress allowlist.

    python3 scripts/fetch_jrc_flood.py --size-only      # price it, download nothing
    python3 scripts/fetch_jrc_flood.py --download DIR   # then fetch

PRICE BEFORE YOU FETCH. --size-only issues HEAD requests and sums Content-Length.
Same discipline as estimate_costs() on the CDS, applied to bytes: the estate has
discovered a limit by rejection three times and should not do it a fourth.

NOTHING IS GUESSED. The script reads each directory index and matches filenames
against the tile labels, so the file-naming convention, the mask naming and
which tiles exist are all read rather than assumed. A needed tile that is absent
is REPORTED, not silently skipped: absence there means the dataset does not
cover that ground (Greenland, Antarctica, basins under 500 km2, open ocean) and
those assets carry R6c_flood as declared-absent under section 7.5.

THE TILE CONVENTION, PROVEN RATHER THAN ASSUMED. The labels encode a 10 degree
corner but do not say which corner. Both were settled by contradiction from the
published file list, without needing tile_extents.geojson:

  - Latitude label is the NORTHERN edge. N90 tiles exist; read as a southern
    edge that would be a tile spanning 90-100N, which does not exist.
  - Longitude label is the WESTERN edge. W180 tiles exist; read as an eastern
    edge that would be -190 to -180, which does not exist. W0 is therefore
    0 to +10, which is why the listing has no "E0" column.

Cross-checked against three jurisdictions whose extent is known independently:
Iceland needs N70_W30 and N70_W20, New Zealand needs S30_E170 and S40_E170,
Italy needs N50_E10 and N50_W0 — all present in the listing.

WE TAKE _depth AND NOT _reclass. The reclassified layer bins depth into
<1 / 1-3 / 3-10 / >10 m. The estate needs metres and can bin them itself;
taking the bins discards precision that cannot be recovered.

THE TWO MASK SETS ARE NOT OPTIONAL. Permanent_WaterBodies is what the hazard
maps are patched with, and Spurious_Depths marks where depths above 10 m are
predicted in channels under 3,000 km2 at RP10, plus a 2 km buffer. Without them
a substation beside a lake reads as inundated and a modelling artefact reads as
hazard.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import re
import sys
import urllib.request

BASE = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard"
RPS = ["RP10", "RP20", "RP50", "RP75", "RP100", "RP200", "RP500"]
MASKS = ["Permanent_WaterBodies", "Spurious_Depths"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELL_INDEX = os.path.join(ROOT, "data", "hazard_cell_index.json")


def tile_label(lat, lon):
    n = int(math.ceil(lat / 10.0) * 10)
    w = int(math.floor(lon / 10.0) * 10)
    ns = "N%d" % n if n >= 0 else "S%d" % (-n)
    ew = ("W%d" % -w) if w < 0 else ("W0" if w == 0 else "E%d" % w)
    return "%s_%s" % (ns, ew)


def needed_tiles():
    idx = json.load(open(CELL_INDEX, encoding="utf-8"))
    counts = {}
    for c in idx["cells"]:
        counts[tile_label(c["lat"], c["lon_signed"])] = \
            counts.get(tile_label(c["lat"], c["lon_signed"]), 0) + c["n"]
    return counts, idx["n_assets"]


def listing(folder):
    """Filenames in one directory index, read rather than guessed."""
    url = "%s/%s/" % (BASE, folder)
    with urllib.request.urlopen(url, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    return sorted(set(re.findall(r'href="([^"?/][^"]*\.tif)"', html)))


def head_bytes(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Length") or 0)


def select(files, tiles, want_reclass=False):
    out = []
    for f in files:
        if not want_reclass and f.endswith("_reclass.tif"):
            continue
        for t in tiles:
            if "_%s_" % t in f:
                out.append((t, f))
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size-only", action="store_true",
                    help="HEAD every file and report the exact byte total")
    ap.add_argument("--download", metavar="DIR", default=None)
    ap.add_argument("--reclass", action="store_true",
                    help="also take the binned layer (not recommended)")
    a = ap.parse_args()
    if not a.size_only and not a.download:
        ap.error("choose --size-only or --download DIR")

    tiles, n_assets = needed_tiles()
    print("estate: %d assets in %d tiles of 271\n" % (n_assets, len(tiles)))

    grand = 0
    missing = {}
    for folder in RPS + MASKS:
        try:
            files = listing(folder)
        except Exception as exc:
            print("  %-22s INDEX UNREADABLE: %s" % (folder, exc)); continue
        picked = select(files, tiles, a.reclass)
        found = {t for t, _ in picked}
        absent = sorted(set(tiles) - found)
        if absent:
            missing[folder] = absent
        total = 0
        for t, f in picked:
            url = "%s/%s/%s" % (BASE, folder, f)
            if a.size_only:
                try:
                    total += head_bytes(url)
                except Exception as exc:
                    print("    HEAD failed %s: %s" % (f, exc))
            else:
                dest = os.path.join(a.download, folder, f)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if os.path.exists(dest):
                    total += os.path.getsize(dest); continue
                urllib.request.urlretrieve(url, dest)
                total += os.path.getsize(dest)
                print("    %s" % f)
        grand += total
        print("  %-22s %4d files  %8.2f GB  (%d tiles absent)"
              % (folder, len(picked), total / 1e9, len(absent)))

    print("\nTOTAL %.2f GB" % (grand / 1e9))
    if missing:
        print("\nTILES THE DATASET DOES NOT COVER — assets there carry R6c_flood")
        print("as DECLARED ABSENT (section 7.5), never defaulted:")
        for folder, absent in missing.items():
            print("  %-22s %s" % (folder, " ".join(absent)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
