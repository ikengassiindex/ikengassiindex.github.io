"""
SSI Pipeline — Seismic Hazard Ingestion
Fetches PGA (Peak Ground Acceleration) data from national seismic hazard maps
and overlays onto substation coordinates.

Priority 3 in the Data Procurement Matrix (INGV for Italy is URGENT).

Supported sources:
  - Italy:       INGV MPS04 (Mappa di Pericolosità Sismica 2004, updated)
  - Japan:       NIED J-SHIS (National Seismic Hazard Maps)
  - Spain:       IGN (Instituto Geográfico Nacional)
  - US:          USGS NSHM 2023
  - Canada:      NRCan NBCC seismic hazard
  - Germany:     BGR seismic hazard map
  - Austria:     GeoSphere Austria / ZAMG
  - France:      BRGM Plan Séisme
  - UK:          BGS seismic hazard
  - Switzerland: SED seismic hazard
  - Mexico:      CENAPRED Atlas Nacional de Riesgos / SSN
"""

import csv
import io
import json
import logging
import math
import os
import urllib.request
import urllib.error
from pathlib import Path

from ..utils.geo import (
    haversine_km, nearest_grid_value, bilinear_interpolate,
    load_substations, substation_coords, classify_seismic_zone,
)
from ..config import CACHE_DIR

logger = logging.getLogger(__name__)

# ── Paths ──
PIPELINE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PIPELINE_DIR / "data"

# ═══════════════════════════════════════════════════════════
#  INGV MPS04 — Italy Seismic Hazard
# ═══════════════════════════════════════════════════════════

# The INGV MPS04 provides PGA at 10% probability of exceedance in 50 years
# (equivalent to 475-year return period) on a 0.05° grid across Italy.
# Source: https://esse1-gis.mi.ingv.it/

# Committed reference file (preferred — download once, commit to repo)
INGV_LOCAL_CSV = DATA_DIR / "italy" / "ingv_mps04_pga475.csv"

# Live API URLs (used only if local file is absent)
INGV_GRID_URL = "https://esse1-gis.mi.ingv.it/data/pga_475.csv"
INGV_ALT_URLS = [
    "https://esse1-gis.mi.ingv.it/data/pga_475_grid.csv",
    "https://esse1.mi.ingv.it/data/mps04_pga475.csv",
]

# INGV MPS04 grid parameters
INGV_GRID_SPACING = 0.05  # degrees
INGV_BOUNDS = {"lat_min": 35.0, "lat_max": 47.5, "lon_min": 6.0, "lon_max": 19.0}


def fetch_ingv_grid(cache=True):
    """
    Load INGV MPS04 PGA grid data.
    Returns list of dicts: [{"lat": float, "lon": float, "pga_g": float}, ...]

    Resolution order:
      1. Local committed CSV (scripts/pipeline/data/italy/ingv_mps04_pga475.csv)
      2. Cached JSON from previous API fetch
      3. Live download from INGV servers
      4. ABORT with instructions (no synthetic fallback)

    The CSV expects columns: lon, lat, pga_g (or LON, LAT, PGA_475)
    Grid spacing: 0.05° (~5.5 km)
    """
    # 1. Local committed reference file (preferred)
    if INGV_LOCAL_CSV.exists():
        logger.info(f"Loading INGV MPS04 from committed reference: {INGV_LOCAL_CSV}")
        with open(INGV_LOCAL_CSV) as f:
            grid_points = _parse_ingv_csv(f.read())
        if grid_points:
            logger.info(f"  Loaded {len(grid_points)} grid points from local CSV")
            return grid_points
        else:
            logger.warning(f"  Local CSV exists but could not be parsed — trying other sources")

    # 2. Cached JSON from previous run
    cache_path = CACHE_DIR / "ingv_mps04_pga475.json"
    if cache and cache_path.exists():
        logger.info("Loading INGV MPS04 from pipeline cache")
        with open(cache_path) as f:
            return json.load(f)

    # 3. Live download from INGV
    grid_points = None
    urls_to_try = [INGV_GRID_URL] + INGV_ALT_URLS

    for url in urls_to_try:
        try:
            logger.info(f"Fetching INGV MPS04 from {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "SSI-Pipeline/4.0.2"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read().decode("utf-8", errors="replace")
                grid_points = _parse_ingv_csv(content)
                if grid_points:
                    break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(f"Failed to fetch from {url}: {e}")
            continue

    if grid_points:
        # Cache for next run
        if cache:
            with open(cache_path, "w") as f:
                json.dump(grid_points, f)
            logger.info(f"Cached {len(grid_points)} INGV grid points")
        return grid_points

    # 4. ABORT — no synthetic data
    logger.error(
        "INGV MPS04 data is not available.\n"
        "  The pipeline requires real seismic hazard data — synthetic data is not used.\n"
        "\n"
        "  To fix this, download the INGV MPS04 PGA grid manually:\n"
        "    1. Go to https://esse1-gis.mi.ingv.it/\n"
        "    2. Download 'PGA con probabilità di eccedenza del 10% in 50 anni'\n"
        "    3. Save as CSV with columns: lon, lat, pga_g\n"
        "    4. Place at: scripts/pipeline/data/italy/ingv_mps04_pga475.csv\n"
        "\n"
        "  Alternative: use GDAL to convert the GeoTIFF:\n"
        "    gdal_translate -of XYZ input.tif output.csv\n"
        "\n"
        "  See scripts/pipeline/data/README.md for full instructions."
    )
    return []


def _parse_ingv_csv(content):
    """Parse INGV CSV format. Handles multiple possible column layouts."""
    grid_points = []
    reader = csv.reader(io.StringIO(content))

    header = None
    for row in reader:
        if not row:
            continue
        # Detect header row
        row_lower = [c.strip().lower() for c in row]
        if any(h in row_lower for h in ["lon", "longitude", "long"]):
            header = row_lower
            continue
        if header is None:
            # Try numeric detection
            try:
                vals = [float(c.strip()) for c in row if c.strip()]
                if len(vals) >= 3:
                    # Assume LON, LAT, PGA
                    grid_points.append({"lat": vals[1], "lon": vals[0], "pga_g": vals[2]})
                continue
            except ValueError:
                header = row_lower
                continue

        # Parse data row using header
        try:
            data = dict(zip(header, [c.strip() for c in row]))
            lon = float(data.get("lon") or data.get("longitude") or data.get("long", 0))
            lat = float(data.get("lat") or data.get("latitude", 0))
            pga = float(data.get("pga_475") or data.get("pga") or data.get("pga_g") or data.get("ag", 0))

            # PGA sanity check: should be in range [0, 1] g for Italy
            if 0 < pga < 1.5 and INGV_BOUNDS["lat_min"] <= lat <= INGV_BOUNDS["lat_max"]:
                grid_points.append({"lat": lat, "lon": lon, "pga_g": pga})
        except (ValueError, KeyError):
            continue

    logger.info(f"Parsed {len(grid_points)} grid points from INGV CSV")
    return grid_points if len(grid_points) > 100 else None


# ═══════════════════════════════════════════════════════════
#  GENERIC SEISMIC SOURCES (other countries)
# ═══════════════════════════════════════════════════════════

# Local reference file paths — each country has a dedicated CSV
_SEISMIC_LOCAL_PATHS = {
    "italy":       DATA_DIR / "italy" / "ingv_mps04_pga475.csv",
    "us":          DATA_DIR / "us" / "usgs_nshm2023_pga475.csv",
    "japan":       DATA_DIR / "japan" / "nied_jshis_pga475.csv",
    "spain":       DATA_DIR / "spain" / "ign_pga475.csv",
    "germany":     DATA_DIR / "germany" / "bgr_pga475.csv",
    "france":      DATA_DIR / "france" / "brgm_pga475.csv",
    "uk":          DATA_DIR / "uk" / "bgs_pga475.csv",
    "switzerland": DATA_DIR / "switzerland" / "sed_pga475.csv",
    "austria":     DATA_DIR / "austria" / "geosphere_pga475.csv",
    "canada":      DATA_DIR / "canada" / "nrcan_pga475.csv",
    "denmark":     DATA_DIR / "denmark" / "geus_pga475.csv",
    "norway":      DATA_DIR / "norway" / "norsar_pga475.csv",
    "finland":     DATA_DIR / "finland" / "isuh_pga475.csv",
    "poland":      DATA_DIR / "poland" / "igf_pan_pga475.csv",
    "sweden":      DATA_DIR / "sweden" / "snsn_pga475.csv",
    "mexico":      DATA_DIR / "mexico" / "cenapred_pga475.csv",
}

# Live API URLs per country (upgrade path)
_SEISMIC_API_URLS = {
    "us":     ["https://earthquake.usgs.gov/nshmp/api/hazard"],
    "japan":  ["https://www.j-shis.bosai.go.jp/map/api/psha"],
    "spain":  ["https://www.ign.es/web/resources/sismologia/peligrosidad/"],
    "mexico": ["https://www2.ssn.unam.mx:8080/catalogo/"],
}


def fetch_seismic_grid(country, cache=True):
    """
    Load seismic PGA grid for any country.

    Resolution order:
      1. Local committed CSV (scripts/pipeline/data/{country}/...)
      2. Cached JSON from previous API fetch
      3. Live download from national seismic agency
      4. ABORT with instructions — no synthetic data

    All CSVs expect columns: lon, lat, pga_g
    """
    local_path = _SEISMIC_LOCAL_PATHS.get(country)
    cache_path = CACHE_DIR / f"seismic_{country}.json"

    # 1. Local reference file
    if local_path and local_path.exists():
        logger.info(f"Loading seismic data from committed reference: {local_path}")
        with open(local_path) as f:
            grid_points = _parse_ingv_csv(f.read())  # same CSV format for all countries
        if grid_points:
            logger.info(f"  Loaded {len(grid_points)} grid points")
            return grid_points

    # 2. Cache
    if cache and cache_path.exists():
        logger.info(f"Loading seismic data from cache for {country}")
        with open(cache_path) as f:
            return json.load(f)

    # 3. Live API (country-specific)
    if country == "italy":
        grid_points = _try_ingv_api()
    else:
        grid_points = _try_generic_api(country)

    if grid_points:
        if cache:
            with open(cache_path, "w") as f:
                json.dump(grid_points, f)
        return grid_points

    # 4. ABORT
    source_info = {
        "italy":       ("INGV MPS04",      "https://esse1-gis.mi.ingv.it/"),
        "us":          ("USGS NSHM 2023",  "https://earthquake.usgs.gov/nshmp/"),
        "japan":       ("NIED J-SHIS",      "https://www.j-shis.bosai.go.jp/"),
        "spain":       ("IGN",              "https://www.ign.es/web/ign/portal/sis-peligrosidad-sismica"),
        "germany":     ("BGR",              "https://www.bgr.bund.de/"),
        "france":      ("BRGM Plan Séisme","https://www.planseisme.fr/"),
        "uk":          ("BGS",              "https://www.bgs.ac.uk/"),
        "switzerland": ("SED",              "http://www.seismo.ethz.ch/"),
        "austria":     ("GeoSphere Austria","https://www.zamg.ac.at/"),
        "canada":      ("NRCan",            "https://earthquakescanada.nrcan.gc.ca/"),
        "denmark":     ("GEUS",             "https://eng.geus.dk/"),
        "norway":      ("NORSAR",           "https://www.norsar.no/"),
        "finland":     ("ISUH",             "https://www.seismo.helsinki.fi/"),
        "poland":      ("IGF-PAN",          "https://www.igf.edu.pl/"),
        "sweden":      ("SNSN",             "https://www.snsn.se/"),
        "mexico":      ("CENAPRED/SSN",     "https://www.cenapred.unam.mx/"),
    }
    name, url = source_info.get(country, ("national agency", ""))
    expected_path = local_path or DATA_DIR / country / f"seismic_pga475.csv"

    logger.error(
        f"Seismic PGA data not available for {country}.\n"
        f"  The pipeline requires real hazard data — no synthetic fallback.\n"
        f"\n"
        f"  To fix this, download from {name}:\n"
        f"    1. Go to {url}\n"
        f"    2. Download the PGA grid (475-year return period / 10% in 50yr)\n"
        f"    3. Convert to CSV with columns: lon, lat, pga_g\n"
        f"    4. Place at: {expected_path}\n"
        f"\n"
        f"  See scripts/pipeline/data/README.md for detailed instructions."
    )
    return []


def _try_ingv_api():
    """Try fetching from INGV live servers."""
    urls = [INGV_GRID_URL] + INGV_ALT_URLS
    for url in urls:
        try:
            logger.info(f"Fetching INGV MPS04 from {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "SSI-Pipeline/4.0.2"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read().decode("utf-8", errors="replace")
                grid_points = _parse_ingv_csv(content)
                if grid_points:
                    return grid_points
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(f"Failed to fetch from {url}: {e}")
    return None


def _try_generic_api(country):
    """Try fetching from live APIs for non-Italy countries."""
    urls = _SEISMIC_API_URLS.get(country, [])
    for url in urls:
        try:
            logger.info(f"Fetching seismic data from {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "SSI-Pipeline/4.0.2"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read().decode("utf-8", errors="replace")
                grid_points = _parse_ingv_csv(content)
                if grid_points:
                    return grid_points
        except Exception as e:
            logger.warning(f"Failed: {e}")
    return None


# ═══════════════════════════════════════════════════════════
#  OVERLAY ENGINE
# ═══════════════════════════════════════════════════════════

def overlay_seismic_pga(country, grid_points=None, method="bilinear"):
    """
    Overlay seismic PGA values onto all substations for a country.

    Args:
        country: Country identifier (e.g., "italy")
        grid_points: Pre-fetched grid data (if None, fetches automatically)
        method: "bilinear" for interpolation, "nearest" for nearest-neighbour

    Returns:
        list of dicts: [{"substation_id": str, "pga_g": float, "zone": int, "distance_km": float}, ...]
    """
    # Fetch grid if not provided
    if grid_points is None:
        if country == "italy":
            grid_points = fetch_ingv_grid()
        else:
            grid_points = fetch_seismic_grid(country)

    if not grid_points:
        logger.error(f"No seismic grid data available for {country}")
        return []

    # Load substations
    data, subs = load_substations(country)
    coords = substation_coords(subs)

    results = []
    matched = 0
    for lat, lon, idx in coords:
        sub = subs[idx]

        if method == "bilinear":
            pga = bilinear_interpolate(lat, lon, grid_points, value_key="pga_g",
                                       grid_spacing=INGV_GRID_SPACING)
        else:
            pga, dist = nearest_grid_value(lat, lon, grid_points, value_key="pga_g")

        if pga is not None and pga > 0:
            zone = classify_seismic_zone(pga)
            results.append({
                "substation_id": sub["substation_id"],
                "index": idx,
                "pga_g": round(pga, 4),
                "zone": zone,
                "previous_pga": sub.get("seismic", {}).get("pga_g", 0.03),
                "previous_zone": sub.get("seismic", {}).get("zone", 4),
            })
            matched += 1
        else:
            # Keep existing value
            results.append({
                "substation_id": sub["substation_id"],
                "index": idx,
                "pga_g": sub.get("seismic", {}).get("pga_g", 0.03),
                "zone": sub.get("seismic", {}).get("zone", 4),
                "previous_pga": sub.get("seismic", {}).get("pga_g", 0.03),
                "previous_zone": sub.get("seismic", {}).get("zone", 4),
            })

    logger.info(f"Seismic overlay: {matched}/{len(coords)} substations matched for {country}")

    # Summary statistics
    if results:
        pgas = [r["pga_g"] for r in results]
        zones = {}
        for r in results:
            z = r["zone"]
            zones[z] = zones.get(z, 0) + 1
        logger.info(f"  PGA range: {min(pgas):.4f}g – {max(pgas):.4f}g")
        logger.info(f"  Zone distribution: {dict(sorted(zones.items()))}")

    return results


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    """Run seismic ingestion for a country (CLI mode)."""
    import argparse

    parser = argparse.ArgumentParser(description="SSI Pipeline — Seismic PGA Ingestion")
    parser.add_argument("country", choices=["italy", "japan", "us", "spain", "germany",
                                            "france", "uk", "switzerland", "austria", "canada",
                                            "denmark", "norway", "finland", "poland", "sweden", "mexico"],
                        help="Country to process")
    parser.add_argument("--method", choices=["bilinear", "nearest"], default="bilinear",
                        help="Interpolation method")
    parser.add_argument("--no-cache", action="store_true", help="Force re-download")
    parser.add_argument("--output", type=str, help="Output JSON path")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    results = overlay_seismic_pga(args.country, method=args.method)

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Wrote {len(results)} results to {out_path}")
    else:
        # Print summary
        print(f"\nSeismic overlay results for {args.country}: {len(results)} substations")
        if results:
            changed = sum(1 for r in results if abs(r["pga_g"] - r["previous_pga"]) > 0.001)
            print(f"  Changed from default: {changed}")
            zones = {}
            for r in results:
                z = r["zone"]
                zones[z] = zones.get(z, 0) + 1
            print(f"  Zone distribution: {dict(sorted(zones.items()))}")


if __name__ == "__main__":
    main()
