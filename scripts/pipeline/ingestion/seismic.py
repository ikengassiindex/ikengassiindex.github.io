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
    "greece":      DATA_DIR / "greece" / "eak_pga475.csv",
}

# Live API URLs per country (upgrade path)
_SEISMIC_API_URLS = {
    "us":     ["https://earthquake.usgs.gov/nshmp/api/hazard"],
    "japan":  ["https://www.j-shis.bosai.go.jp/map/api/psha"],
    "spain":  ["https://www.ign.es/web/resources/sismologia/peligrosidad/"],
    "mexico": ["https://www2.ssn.unam.mx:8080/catalogo/"],
}

# ═══════════════════════════════════════════════════════════
#  P15-B-4 NATIONAL SEISMIC AGENCY TIER (registry, v4.5 expansion)
# ═══════════════════════════════════════════════════════════
# Mirrors the climate.py P15-A-4 architecture:
#
#   Tier 1a (direct national agency, registered + populated):
#     italy   — INGV MPS04 (ingv_mps04_pga475.csv) ✓ in _SEISMIC_LOCAL_PATHS
#     greece  — EAK 2003 (eak_pga475.csv) ✓
#     mexico  — CENAPRED (cenapred_pga475.csv) ✓
#
#   Tier 1b (direct national agency, registry built but file empty —
#            v4.5 expansion targets):
#     us      — USGS NSHM 2023 (fault-resolved, MUCH finer than GEM 0.05°)
#     japan   — NIED J-SHIS (1km municipality grid)
#     germany — BGR D-A-CH model
#     france  — BRGM Plan Séisme
#     spain   — IGN Peligrosidad Sísmica
#     uk      — BGS national hazard map
#     switzerland — SED hazard map
#     austria — GeoSphere Austria (formerly ZAMG)
#     canada — NRCan 5th Gen
#     norway  — NORSAR hazard model
#     ... (+ ~30 more national agencies that contribute to GEM 2023.1)
#
#   Tier 2 (international fallback): GEM 2023.1 GeoTIFF (existing P15-B-2 path)
#
# Per-country source-agency attribution for the 37 countries that currently
# use Tier 2 GEM: each is documented below for audit traceability. GEM 2023.1
# was created by collating maps from national + regional probabilistic
# seismic hazard models per Pagani et al. (2018); each GEM pixel can in
# principle be traced to the contributing national model.
_NATIONAL_SEISMIC_AGENCY = {
    "us":          "USGS NSHM 2023",
    "japan":       "NIED J-SHIS (National Research Institute for Earth Science and Disaster Resilience)",
    "italy":       "INGV MPS04 (Istituto Nazionale di Geofisica e Vulcanologia)",
    "germany":     "BGR (Bundesanstalt für Geowissenschaften und Rohstoffe)",
    "france":      "BRGM Plan Séisme (Bureau de Recherches Géologiques et Minières)",
    "spain":       "IGN (Instituto Geográfico Nacional)",
    "uk":          "BGS (British Geological Survey)",
    "switzerland": "SED (Swiss Seismological Service)",
    "austria":     "GeoSphere Austria (formerly ZAMG)",
    "canada":      "NRCan 5th Gen Seismic Hazard Model",
    "denmark":     "GEUS (Geological Survey of Denmark and Greenland)",
    "norway":      "NORSAR + NGU (Norwegian Seismic Array)",
    "finland":     "ISUH (Institute of Seismology, University of Helsinki)",
    "poland":      "IGF-PAN (Institute of Geophysics, Polish Academy of Sciences)",
    "sweden":      "SNSN (Swedish National Seismic Network)",
    "mexico":      "CENAPRED + SSN (Centro Nacional de Prevención de Desastres)",
    "greece":      "EAK 2003 (Greek Earthquake Planning and Protection Organization)",
    "netherlands": "KNMI Seismology and Acoustics",
    "belgium":     "ROB-KSB (Royal Observatory of Belgium)",
    "ireland":     "INSN (Irish National Seismic Network) + DIAS",
    "portugal":    "IPMA Seismology Division",
    "iceland":     "IMO (Icelandic Met Office, Earthquake Monitoring)",
    "luxembourg":  "ECGS (European Center for Geodynamics and Seismology)",
    "hungary":     "MTA CSFK GGI (Hungarian Academy seismic group)",
    "czechia":     "IRSM CAS + IGT (Institute of Rock Structure and Mechanics)",
    "slovakia":    "GFÚ SAV (Geophysical Institute, Slovak Academy)",
    "slovenia":    "ARSO Seismology Office",
    "estonia":     "Tartu Observatory (Estonian seismic network)",
    "latvia":      "LVĢMC Seismology",
    "lithuania":   "VU GMC (Vilnius University Geophysical Center)",
    "turkey":      "AFAD (Disaster and Emergency Management Authority)",
    "israel":      "GII (Geophysical Institute of Israel)",
    "korea":       "KMA Earthquake and Volcano Center",
    "new-zealand": "GeoNet (GNS Science + EQC)",
    "australia":   "Geoscience Australia NSHA18",
    "chile":       "CSN (Centro Sismológico Nacional, Universidad de Chile)",
    "colombia":    "SGC (Servicio Geológico Colombiano)",
    "costa-rica":  "OVSICORI-UNA + RSN (Observatorio Vulcanológico y Sismológico)",
    "greenland":   "DMI Seismology (Danish Met operates Greenland stations)",
}


# Per-country direct-agency override registry — v4.5 expansion target.
# When populated, this fetcher takes precedence over the existing local-CSV
# path. Empty for now; aspirational targets:
#   us      — USGS NSHM 2023 raster download + parse
#   japan   — NIED J-SHIS API: https://www.j-shis.bosai.go.jp/map/api/psha
#   france  — BRGM Plan Séisme zone shapefile + GMPE
#   germany — BGR D-A-CH grid
#   spain   — IGN Norma de Construcción Sismorresistente NCSE-02 map
_NATIONAL_SEISMIC_FETCHERS = {
    # "us":      _fetch_usgs_nshm_2023,           # P15-B-4-future (HIGH PRIORITY — fault-resolved >> GEM)
    # "japan":   _fetch_nied_jshis_japan,         # P15-B-4-future (1km grid >> GEM 0.05°)
    # "germany": _fetch_bgr_dach_germany,         # P15-B-4-future
    # "france":  _fetch_brgm_plan_seisme_france,  # P15-B-4-future
    # "spain":   _fetch_ign_ncse02_spain,         # P15-B-4-future
}


def get_national_seismic_agency(country):
    """P15-B-4: return the name of the national seismic agency for a country.
    Used by output writers to tag each PGA point with source_agency for audit.
    Falls back to 'GEM 2023.1 (international aggregation)' for unmapped countries.
    """
    return _NATIONAL_SEISMIC_AGENCY.get(
        country,
        "GEM 2023.1 Global Seismic Hazard Map (international aggregation of national models)"
    )

# ═══════════════════════════════════════════════════════════
#  P15-B GLOBAL FALLBACK — GEM Global Seismic Hazard Map 2023.1
# ═══════════════════════════════════════════════════════════
# P15-B-2 (8 June 2026): switched primary input from imagined CSV to the
# GEM 2023.1 GeoTIFF raster (the actual format GEM publishes). The CSV
# path is kept as a secondary fallback for operators who pre-extract
# their own region.
#
# Operator downloads ONE global GeoTIFF raster (~50-200 MB, free) and places it at:
#   scripts/pipeline/data/cross-cutting/gshm-2023-1.tif
# OR (legacy) places a pre-extracted CSV at:
#   scripts/pipeline/data/cross-cutting/gem_global_pga475.csv  (lon, lat, pga_g cols)
#
# Source: GEM Foundation — https://www.globalquakemodel.org/product/global-seismic-hazard-map
# Direct download (2023.1, raster): https://cloud.openquake.org/s/6SnFk2f92JEr76H
# License: CC BY-NC-SA 4.0 (Non-Commercial; commercial use requires License Request from GEM)
#
# Coverage: all 39 SoT countries via single file. 2023.1 has 2.5× higher
# spatial resolution than 2018 (~0.05° native vs 0.1° in 2018).
#
# Dependency: requires `rasterio` for GeoTIFF reading (heavy because of GDAL
# backend). The legacy CSV path requires only stdlib. If rasterio is not
# installed AND only the .tif is present, the fetcher logs a clear error.
_GEM_GLOBAL_TIF = DATA_DIR / "cross-cutting" / "gshm-2023-1.tif"
_GEM_GLOBAL_CSV = DATA_DIR / "cross-cutting" / "gem_global_pga475.csv"

# Country bounding boxes (lat_min, lat_max, lon_min, lon_max) — mirrors
# scripts/validate_schema.py::COUNTRY_BOUNDS for consistency. Used to
# bbox-clip the global GEM grid into per-country CSVs.
_COUNTRY_BBOX_FOR_CLIP = {
    'france':       (41.0, 51.5, -5.5, 10.0),
    'italy':        (35.5, 47.5, 6.5, 19.0),
    'uk':           (49.5, 61.0, -8.5, 2.0),
    'spain':        (35.5, 44.0, -10.0, 4.5),
    'germany':      (47.0, 55.5, 5.5, 15.5),
    'switzerland':  (45.5, 48.0, 5.5, 10.5),
    'austria':      (46.0, 49.5, 9.5, 17.5),
    'us':           (24.0, 72.0, -180.0, -65.0),
    'canada':       (41.0, 84.0, -141.0, -52.0),
    'japan':        (24.0, 46.0, 122.0, 154.0),
    'australia':    (-45.0, -10.0, 110.0, 155.0),
    'chile':        (-56.0, -17.0, -76.0, -66.0),
    'portugal':     (36.9, 42.2, -9.6, -6.1),
    'new-zealand':  (-47.5, -34.0, 165.5, 179.0),
    'greenland':    (59.5, 83.7, -74.0, -11.0),
    'czechia':      (48.55, 51.06, 12.09, 18.86),
    'luxembourg':   (49.45, 50.18,  5.73,  6.53),
    'belgium':      (49.50, 51.51,  2.55,  6.41),
    'netherlands':  (50.75, 53.55,  3.36,  7.23),
    'estonia':      (57.51, 59.69, 21.83, 28.21),
    'latvia':       (55.67, 58.09, 20.97, 28.24),
    'lithuania':    (53.90, 56.45, 20.95, 26.84),
    'korea':        (33.0, 38.7, 124.5, 132.0),
    'colombia':     (-4.3, 13.5, -82.0, -66.8),
    'israel':       (29.4, 33.4, 34.2, 35.9),
    'costa-rica':   (8.0, 11.3, -86.0, -82.5),
    'iceland':      (63.2, 66.6, -24.6, -13.4),
    'hungary':      (45.7, 48.6, 16.1, 22.9),
    'slovakia':     (47.7, 49.7, 16.8, 22.6),
    'slovenia':     (45.4, 46.9, 13.4, 16.6),
    # Add boxes for the remaining countries that exist in MIN_FLEET but
    # haven't been added to COUNTRY_BOUNDS yet (denmark, norway, finland,
    # sweden, mexico, greece, ireland, poland, turkey)
    'denmark':      (54.5, 57.8,  8.0, 15.2),
    'norway':       (57.9, 71.3,  4.6, 31.1),
    'finland':      (59.7, 70.1, 20.5, 31.6),
    'sweden':       (55.3, 69.1, 10.9, 24.2),
    'mexico':       (14.5, 32.8, -118.5, -86.5),
    'greece':       (34.8, 41.8, 19.3, 28.3),
    'ireland':      (51.4, 55.4, -10.5, -5.4),
    'poland':       (49.0, 55.0, 14.1, 24.2),
    'turkey':       (35.8, 42.1, 26.0, 44.8),
}


def _read_geotiff_bbox(tif_path, bbox, country):
    """P15-B-2: bbox-clip a GeoTIFF raster and return list of grid-point dicts.

    Uses rasterio to handle the affine geo-transform correctly. Returns
    None on import failure or read error (caller should fall through to
    CSV path).
    """
    try:
        import rasterio
        from rasterio.windows import from_bounds
    except ImportError:
        logger.warning(
            f"P15-B-2: rasterio not installed; cannot read {tif_path.name}. "
            f"Install with: pip install rasterio    "
            f"(or pre-extract the GeoTIFF to {_GEM_GLOBAL_CSV.name} and use the CSV path)"
        )
        return None

    lat_min, lat_max, lon_min, lon_max = bbox
    try:
        with rasterio.open(tif_path) as src:
            # Window the raster to the bbox (rasterio handles the affine
            # transform). bounds order is (left, bottom, right, top) = (lon_min, lat_min, lon_max, lat_max).
            window = from_bounds(
                lon_min, lat_min, lon_max, lat_max,
                transform=src.transform,
            )
            # Read the windowed band (PGA values, dtype usually float32)
            data = src.read(1, window=window, masked=True)
            # Compute the per-pixel lat/lon for this window
            window_transform = src.window_transform(window)

            # Iterate over pixels in the window
            points = []
            nodata = src.nodata
            rows, cols = data.shape
            for i in range(rows):
                for j in range(cols):
                    val = data[i, j]
                    # Skip masked/nodata
                    if data.mask is not False and bool(data.mask[i, j]):
                        continue
                    if nodata is not None and val == nodata:
                        continue
                    if val is None or not (val == val):  # NaN check
                        continue
                    # Center of the pixel (j + 0.5, i + 0.5)
                    lon, lat = window_transform * (j + 0.5, i + 0.5)
                    points.append({
                        "lon": round(float(lon), 4),
                        "lat": round(float(lat), 4),
                        "pga_g": round(float(val), 4),
                    })
            logger.info(
                f"P15-B-2: extracted {len(points)} GEM raster points for {country} "
                f"(2023.1, bbox lat [{lat_min}, {lat_max}], lon [{lon_min}, {lon_max}])"
            )
            return points
    except Exception as exc:
        logger.error(f"P15-B-2: failed to read {tif_path.name}: {exc}")
        return None


def fetch_gem_global_for_country(country):
    """
    P15-B / P15-B-2: Bbox-clip the GEM Global PGA grid for a specific country.

    Tries the 2023.1 GeoTIFF raster first (preferred), then falls back to
    a legacy pre-extracted CSV. Returns list of {"lon", "lat", "pga_g"} dicts.

    Returns empty list if:
      - Neither raster nor CSV present (operator needs to download)
      - Country bbox is not known
      - No grid points fall within the bbox
    """
    bbox = _COUNTRY_BBOX_FOR_CLIP.get(country)
    if bbox is None:
        logger.warning(
            f"P15-B: no bounding box defined for {country}. "
            f"Add an entry to _COUNTRY_BBOX_FOR_CLIP in seismic.py."
        )
        return []

    # PRIMARY: GeoTIFF raster (GEM 2023.1)
    if _GEM_GLOBAL_TIF.exists():
        points = _read_geotiff_bbox(_GEM_GLOBAL_TIF, bbox, country)
        if points is not None:
            return points
        # rasterio missing or read failed → fall through to CSV

    # SECONDARY: pre-extracted CSV (legacy GEM 2018 or operator-prepared)
    if not _GEM_GLOBAL_CSV.exists():
        logger.warning(
            f"GEM global PGA grid not present.\n"
            f"  Expected EITHER:\n"
            f"    {_GEM_GLOBAL_TIF}  (preferred, GEM 2023.1 raster)\n"
            f"    {_GEM_GLOBAL_CSV}  (legacy CSV)\n"
            f"  Download raster from https://cloud.openquake.org/s/6SnFk2f92JEr76H\n"
            f"  Product page: https://www.globalquakemodel.org/product/global-seismic-hazard-map\n"
            f"  License: CC BY-NC-SA 4.0 (research/non-commercial; commercial use needs GEM license)"
        )
        return []

    lat_min, lat_max, lon_min, lon_max = bbox
    points = []
    try:
        with open(_GEM_GLOBAL_CSV) as f:
            header = f.readline().strip().split(',')
            # Tolerant column lookup: GEM exports may name columns slightly
            # differently (e.g. PGA vs pga_g). Try common variants.
            try:
                lon_i = next(i for i, h in enumerate(header) if h.lower() in ('lon', 'longitude'))
                lat_i = next(i for i, h in enumerate(header) if h.lower() in ('lat', 'latitude'))
                pga_i = next(i for i, h in enumerate(header) if 'pga' in h.lower())
            except StopIteration:
                logger.error(
                    f"GEM global CSV header doesn't match expected schema. "
                    f"Got: {header}. Expected columns containing lon/lat/pga."
                )
                return []
            for line in f:
                if not line.strip() or line.startswith('#'):
                    continue
                parts = line.strip().split(',')
                try:
                    lon = float(parts[lon_i])
                    lat = float(parts[lat_i])
                    pga = float(parts[pga_i])
                except (ValueError, IndexError):
                    continue
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    points.append({"lon": lon, "lat": lat, "pga_g": pga})
    except Exception as e:
        logger.error(f"Failed to read GEM global CSV: {e}")
        return []

    logger.info(
        f"P15-B: extracted {len(points)} GEM grid points for {country} "
        f"(bbox lat [{lat_min}, {lat_max}], lon [{lon_min}, {lon_max}])"
    )
    return points


def write_gem_country_csv(country, points, output_path=None):
    """
    P15-B: Write a country's bbox-clipped GEM points to the canonical
    per-country CSV path so the rest of the pipeline can consume it.

    The expected path follows the convention:
      scripts/pipeline/data/<country>/gem_pga475.csv
    """
    if not points:
        return False
    if output_path is None:
        output_path = DATA_DIR / country / "gem_pga475.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("lon,lat,pga_g\n")
        for p in points:
            f.write(f"{p['lon']:.4f},{p['lat']:.4f},{p['pga_g']:.4f}\n")
    logger.info(f"P15-B: wrote {len(points)} GEM points to {output_path}")
    return True


def fetch_seismic_grid(country, cache=True):
    """
    Load seismic PGA grid for any country.

    P15-B-4 resolution chain (8 June 2026):
      Tier 1a — Direct national agency fetcher (_NATIONAL_SEISMIC_FETCHERS registry,
                currently empty stubs; v4.5 expansion targets: USGS NSHM 2023,
                NIED J-SHIS Japan, BGR Germany, BRGM France, IGN Spain)
      Tier 1b — Local committed CSV per agency (_SEISMIC_LOCAL_PATHS — currently
                populated for italy/greece/mexico; 14 other paths registered
                but empty awaiting operator action)
      Tier 1c — Cache JSON
      Tier 1d — Live agency API (_SEISMIC_API_URLS)
      Tier 2  — GEM 2023.1 global raster (P15-B-2 path)
      Tier 3  — ABORT

    Each PGA point's audit traceability via get_national_seismic_agency(country).
    """
    local_path = _SEISMIC_LOCAL_PATHS.get(country)
    cache_path = CACHE_DIR / f"seismic_{country}.json"

    # ── Tier 1a: per-country direct national fetcher (override) ──
    direct_fetcher = _NATIONAL_SEISMIC_FETCHERS.get(country)
    if direct_fetcher is not None:
        try:
            grid_points = direct_fetcher(country)
            if grid_points:
                logger.info(
                    f"P15-B-4: Tier 1a (direct national agency) succeeded for {country}; "
                    f"emitted {len(grid_points)} records from "
                    f"{get_national_seismic_agency(country)}"
                )
                return grid_points
        except Exception as exc:
            logger.warning(
                f"P15-B-4: Tier 1a direct fetcher for {country} raised "
                f"{type(exc).__name__}: {exc}; falling through."
            )

    # ── Tier 1b: Local reference file (per-country native agency CSV) ──
    if local_path and local_path.exists():
        logger.info(f"Loading seismic data from committed reference: {local_path}")
        with open(local_path) as f:
            grid_points = _parse_ingv_csv(f.read())  # same CSV format for all countries
        if grid_points:
            logger.info(
                f"  Loaded {len(grid_points)} grid points from {get_national_seismic_agency(country)}"
            )
            return grid_points

    # 1b. P15-B: GEM-extracted per-country CSV (created by the GEM global
    # fallback path on previous runs). This way subsequent pipeline calls
    # don't re-extract from the global file every time.
    gem_country_path = DATA_DIR / country / "gem_pga475.csv"
    if gem_country_path.exists():
        logger.info(f"Loading GEM-extracted seismic data: {gem_country_path}")
        with open(gem_country_path) as f:
            grid_points = _parse_ingv_csv(f.read())
        if grid_points:
            logger.info(f"  Loaded {len(grid_points)} grid points (GEM 2018 global)")
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

    # 3.5 P15-B: GEM Global Seismic Hazard Map fallback
    # When per-country agency dispatch fails (no API key, agency offline,
    # endpoint changed), try the global GEM 2018 grid. The operator
    # downloads the global CSV once; this code bbox-clips per country.
    grid_points = fetch_gem_global_for_country(country)
    if grid_points:
        logger.info(
            f"  Using GEM global fallback for {country} ({len(grid_points)} points). "
            f"Per-country agency dispatch failed; GEM grid covers this country at "
            f"~0.1° resolution. To upgrade to native agency data, see step 4 instructions."
        )
        # Also persist a per-country CSV so subsequent pipeline runs hit
        # the local-reference path (step 1) and don't re-clip every time.
        write_gem_country_csv(country, grid_points)
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
        "greece":      ("ITSAK/EAK 2003",   "https://www.itsak.gr/"),
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
                                            "denmark", "norway", "finland", "poland", "sweden", "mexico",
                                            "greece"],
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
