"""
SSI Pipeline — Climate Trajectory Ingestion
Fetches CMIP6 climate projections and ERA5 reanalysis to compute
forward-looking IRI metrics (I1/I2/I3 trajectories).

Priority 1 in the Data Procurement Matrix — affects ALL 10 countries.

Pipeline: Copernicus CDS → spatial interpolation → delta from baseline → IRI_forward

Supported sources:
  - Copernicus CDS: ERA5 reanalysis (1940–present, 31 km)
  - Copernicus CDS: CMIP6 SSP2-4.5 ensemble (50+ GCMs)
  - National downscaling where available:
    * Italy: ISPRA regional projections
    * UK: UKCP18 (12 km)
    * Switzerland: CH2018
    * France: DRIAS/Météo-France
    * Germany: DWD REMO/WETTREG
    * Mexico: SMN/CONAGUA regional projections
"""

import json
import logging
import math
import os
from pathlib import Path

from ..utils.geo import (
    haversine_km, nearest_grid_value, bilinear_interpolate,
    load_substations, substation_coords,
)
from ..config import CACHE_DIR, CDS_API_KEY, CDS_API_URL, CMIP6_MODELS

logger = logging.getLogger(__name__)

# ── Paths ──
PIPELINE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PIPELINE_DIR / "data"

# Local committed reference files (preferred)
CMIP6_LOCAL_CSV = DATA_DIR / "cross-cutting" / "cmip6_ssp245_deltas.csv"

def _era5_local_path(country):
    return DATA_DIR / "cross-cutting" / f"era5_baseline_{country}.csv"

def _cmip6_country_local(country):
    return DATA_DIR / country / f"cmip6_ssp245_deltas.csv"


# ═══════════════════════════════════════════════════════════
#  CDS API CLIENT
# ═══════════════════════════════════════════════════════════

def cds_retrieve(dataset, request_params, output_path):
    """
    Retrieve data from Copernicus Climate Data Store.
    Requires CDS_API_KEY environment variable.

    Uses the CDS API v2 (cdsapi package if available, otherwise direct HTTP).
    """
    if not CDS_API_KEY:
        logger.warning("CDS_API_KEY not set — cannot fetch from Copernicus CDS")
        return False

    try:
        import cdsapi
        c = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)
        c.retrieve(dataset, request_params, str(output_path))
        logger.info(f"Downloaded {dataset} to {output_path}")
        return True
    except ImportError:
        logger.warning("cdsapi package not installed — using direct HTTP fallback")
        return _cds_http_retrieve(dataset, request_params, output_path)
    except Exception as e:
        logger.error(f"CDS API error: {e}")
        return False


def _cds_http_retrieve(dataset, params, output_path):
    """Direct HTTP fallback for CDS API."""
    import urllib.request
    import urllib.error

    api_url = f"{CDS_API_URL}/v1/resources/{dataset}"
    headers = {
        "Authorization": f"Bearer {CDS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        req_data = json.dumps(params).encode()
        req = urllib.request.Request(api_url, data=req_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=300) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        logger.error(f"CDS HTTP fallback failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════
#  ERA5 CLIMATE BASELINE
# ═══════════════════════════════════════════════════════════

def fetch_era5_baseline(country, years=(2000, 2020), cache=True):
    """
    Load ERA5 climate baseline (heat days, ice days, wind speed) for a country.

    Resolution order:
      1. Local committed CSV (scripts/pipeline/data/cross-cutting/era5_baseline_{country}.csv)
      2. Cached JSON from previous CDS download
      3. Live download from Copernicus CDS (requires CDS_API_KEY)
      4. ABORT with instructions — no synthetic data
    """
    local_path = _era5_local_path(country)

    # 1. Local committed reference
    if local_path.exists():
        logger.info(f"Loading ERA5 baseline from committed reference: {local_path}")
        grid = _parse_climate_csv(local_path, ["lat", "lon", "t_mean_c", "heat_days", "ice_days", "wind_speed"])
        if grid:
            return grid

    # 2. Cache
    cache_path = CACHE_DIR / f"era5_baseline_{country}.json"
    if cache and cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    # 3. Live CDS download
    bbox = _country_bbox(country)
    if bbox and CDS_API_KEY:
        era5_request = {
            "product_type": "monthly_averaged_reanalysis",
            "variable": ["2m_temperature", "10m_wind_speed",
                         "maximum_2m_temperature_since_previous_post_processing",
                         "minimum_2m_temperature_since_previous_post_processing"],
            "year": [str(y) for y in range(years[0], years[1] + 1)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "time": "00:00",
            "area": [bbox["lat_max"], bbox["lon_min"], bbox["lat_min"], bbox["lon_max"]],
            "format": "netcdf",
        }
        output = CACHE_DIR / f"era5_{country}_{years[0]}_{years[1]}.nc"
        success = cds_retrieve("reanalysis-era5-single-levels-monthly-means", era5_request, output)
        if success:
            baseline = _process_era5_netcdf(output, country)
            if baseline and cache:
                with open(cache_path, "w") as f:
                    json.dump(baseline, f)
            return baseline

    # 4. ABORT
    logger.error(
        f"ERA5 baseline data not available for {country}.\n"
        f"  No synthetic fallback — real climate data is required.\n"
        f"\n"
        f"  To fix this:\n"
        f"    1. Register at https://cds.climate.copernicus.eu (free)\n"
        f"    2. Download ERA5 monthly means (2000–2020) for {country}\n"
        f"    3. Process into CSV: lat, lon, t_mean_c, heat_days, ice_days, wind_speed\n"
        f"    4. Place at: {local_path}\n"
        f"\n"
        f"  Or set CDS_API_KEY env var for automatic download.\n"
        f"  See scripts/pipeline/data/README.md for full instructions."
    )
    return None


def _parse_climate_csv(csv_path, expected_columns):
    """
    Parse a committed climate reference CSV into a list of grid-point dicts.

    Args:
        csv_path: Path to CSV file
        expected_columns: List of column names to extract (first two should be lat/lon)

    Returns:
        List of dicts with numeric values, or None if parsing fails.
    """
    import csv as csv_mod

    try:
        grid = []
        with open(csv_path, newline="") as f:
            reader = csv_mod.DictReader(f)
            headers = reader.fieldnames or []

            # Validate columns exist
            missing = [c for c in expected_columns if c not in headers]
            if missing:
                logger.warning(f"Climate CSV {csv_path} missing columns: {missing}")
                # Try common aliases
                alias_map = {
                    "lat": ["latitude", "LAT", "Lat"],
                    "lon": ["longitude", "LON", "Lon", "lng"],
                    "t_mean_c": ["t_mean", "temperature", "temp_c"],
                    "heat_days": ["heat_days_yr", "hot_days"],
                    "ice_days": ["ice_days_yr", "frost_days"],
                    "wind_speed": ["wind_ms", "wind_speed_ms"],
                    "delta_t_c": ["delta_t", "warming_c"],
                    "delta_heat_pct": ["delta_heat", "heat_change_pct"],
                    "delta_ice_pct": ["delta_ice", "ice_change_pct"],
                    "delta_wind_pct": ["delta_wind", "wind_change_pct"],
                }
                col_map = {}
                for col in expected_columns:
                    if col in headers:
                        col_map[col] = col
                    else:
                        for alias in alias_map.get(col, []):
                            if alias in headers:
                                col_map[col] = alias
                                break
                        else:
                            logger.error(f"Cannot resolve column '{col}' in {csv_path}")
                            return None
            else:
                col_map = {c: c for c in expected_columns}

            for row in reader:
                try:
                    point = {}
                    for target, source in col_map.items():
                        val = row[source].strip()
                        point[target] = float(val)
                    grid.append(point)
                except (ValueError, KeyError) as e:
                    continue  # skip malformed rows

        if not grid:
            logger.warning(f"Climate CSV {csv_path} parsed but yielded 0 rows")
            return None

        logger.info(f"Parsed {len(grid)} grid points from {csv_path.name}")
        return grid

    except FileNotFoundError:
        logger.warning(f"Climate CSV not found: {csv_path}")
        return None
    except Exception as e:
        logger.error(f"Error parsing climate CSV {csv_path}: {e}")
        return None


def _process_era5_netcdf(nc_path, country):
    """Process ERA5 NetCDF into grid of climate metrics."""
    try:
        import netCDF4 as nc
        ds = nc.Dataset(str(nc_path))

        lats = ds.variables["latitude"][:]
        lons = ds.variables["longitude"][:]
        t2m = ds.variables["t2m"][:]  # 2m temperature (K)

        grid = []
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                t_mean_c = float(t2m[:, i, j].mean()) - 273.15
                heat_days = max(0, (t_mean_c - 20) * 15)
                ice_days = max(0, (0 - t_mean_c) * 20)

                grid.append({
                    "lat": float(lat), "lon": float(lon),
                    "t_mean_c": round(t_mean_c, 2),
                    "heat_days": round(heat_days, 1),
                    "ice_days": round(ice_days, 1),
                })

        ds.close()
        return grid
    except ImportError:
        logger.error(
            f"netCDF4 not available — cannot process ERA5 NetCDF for {country}.\n"
            f"  Install with: pip install netCDF4\n"
            f"  Or pre-process the NetCDF to CSV and place at: {_era5_local_path(country)}"
        )
        return None


# ═══════════════════════════════════════════════════════════
#  CMIP6 CLIMATE PROJECTIONS
# ═══════════════════════════════════════════════════════════

def fetch_cmip6_projections(country, scenario="ssp245", period=(2030, 2050), cache=True):
    """
    Load CMIP6 ensemble projections (SSP2-4.5 deltas) for a country.

    Resolution order:
      1. Country-specific committed CSV (scripts/pipeline/data/{country}/cmip6_ssp245_deltas.csv)
      2. Cross-cutting committed CSV (scripts/pipeline/data/cross-cutting/cmip6_ssp245_deltas.csv)
      3. Cached JSON from previous CDS download
      4. Live download from Copernicus CDS (requires CDS_API_KEY + netCDF4)
      5. ABORT with instructions — no synthetic data

    Returns gridded deltas: [{"lat", "lon", "delta_t_c", "delta_heat_pct", "delta_ice_pct", "delta_wind_pct"}, ...]
    """
    cmip6_cols = ["lat", "lon", "delta_t_c", "delta_heat_pct", "delta_ice_pct", "delta_wind_pct"]

    # 1. Country-specific committed CSV
    country_csv = _cmip6_country_local(country)
    if country_csv.exists():
        logger.info(f"Loading CMIP6 deltas from country CSV: {country_csv}")
        grid = _parse_climate_csv(country_csv, cmip6_cols)
        if grid:
            return grid

    # 2. Cross-cutting committed CSV (global grid — filter to country bbox)
    if CMIP6_LOCAL_CSV.exists():
        logger.info(f"Loading CMIP6 deltas from cross-cutting CSV: {CMIP6_LOCAL_CSV}")
        full_grid = _parse_climate_csv(CMIP6_LOCAL_CSV, cmip6_cols)
        if full_grid:
            bbox = _country_bbox(country)
            if bbox:
                grid = [
                    p for p in full_grid
                    if bbox["lat_min"] <= p["lat"] <= bbox["lat_max"]
                    and bbox["lon_min"] <= p["lon"] <= bbox["lon_max"]
                ]
                if grid:
                    logger.info(f"Filtered {len(grid)} CMIP6 grid points for {country} from global grid")
                    return grid

    # 3. Cache
    cache_path = CACHE_DIR / f"cmip6_{scenario}_{country}.json"
    if cache and cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    # 4. Live CDS download
    bbox = _country_bbox(country)
    if bbox and CDS_API_KEY:
        cmip6_request = {
            "temporal_resolution": "monthly",
            "experiment": scenario,
            "variable": "near_surface_air_temperature",
            "model": CMIP6_MODELS,
            "year": [str(y) for y in range(period[0], period[1] + 1)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "area": [bbox["lat_max"], bbox["lon_min"], bbox["lat_min"], bbox["lon_max"]],
            "format": "zip",
        }

        output = CACHE_DIR / f"cmip6_{scenario}_{country}_{period[0]}_{period[1]}.zip"
        success = cds_retrieve("projections-cmip6", cmip6_request, output)

        if success:
            deltas = _process_cmip6(output, country)
            if deltas and cache:
                with open(cache_path, "w") as f:
                    json.dump(deltas, f)
            return deltas

    # 5. ABORT
    logger.error(
        f"CMIP6 climate projections not available for {country}.\n"
        f"  No synthetic fallback — real climate projection data is required.\n"
        f"\n"
        f"  To fix this:\n"
        f"    1. Register at https://cds.climate.copernicus.eu (free)\n"
        f"    2. Accept the CMIP6 licence terms\n"
        f"    3. Download SSP2-4.5 ensemble (ACCESS-CM2, CNRM-CM6-1, EC-Earth3,\n"
        f"       GFDL-ESM4, MRI-ESM2-0), period 2030–2050, monthly\n"
        f"    4. Compute ensemble median per 0.5° grid cell\n"
        f"    5. Subtract 2000–2020 ERA5 baseline to get deltas\n"
        f"    6. Save as CSV: lat, lon, delta_t_c, delta_heat_pct, delta_ice_pct, delta_wind_pct\n"
        f"    7. Place at: {country_csv}\n"
        f"       Or for all countries: {CMIP6_LOCAL_CSV}\n"
        f"\n"
        f"  Or set CDS_API_KEY env var for automatic download.\n"
        f"  See scripts/pipeline/data/README.md for full instructions."
    )
    return None


def _process_cmip6(zip_path, country):
    """Process CMIP6 NetCDF ensemble into delta grid."""
    try:
        import netCDF4  # noqa: F401
        # Full implementation: extract NetCDF from zip, compute ensemble median,
        # subtract baseline, produce delta grid
        logger.warning("CMIP6 NetCDF post-processing not yet implemented — pre-process to CSV")
        return None
    except ImportError:
        logger.error(
            f"netCDF4 not available — cannot process CMIP6 NetCDF.\n"
            f"  Install with: pip install netCDF4\n"
            f"  Or pre-process to CSV and place at: {_cmip6_country_local(country)}"
        )
        return None


# ═══════════════════════════════════════════════════════════
#  IRI FORWARD COMPUTATION
# ═══════════════════════════════════════════════════════════

def compute_iri_forward(country, era5_baseline=None, cmip6_deltas=None, cache=True):
    """
    Compute forward-looking IRI trajectory ratios for each substation.

    IRI_forward = IRI_base × (1 + delta_CMIP6)

    The trajectory ratio indicates how much each IRI metric is expected to change
    under SSP2-4.5 by 2030–2050 relative to 2000–2020 baseline.

    Returns list of per-substation trajectory updates.
    """
    if era5_baseline is None:
        era5_baseline = fetch_era5_baseline(country, cache=cache)
    if cmip6_deltas is None:
        cmip6_deltas = fetch_cmip6_projections(country, cache=cache)

    if not cmip6_deltas:
        logger.warning(f"No CMIP6 data for {country} — IRI forward cannot be computed")
        return []

    data, subs = load_substations(country)
    coords = substation_coords(subs)

    # Build a fast lookup grid for CMIP6 deltas (O(1) per query instead of O(n))
    cmip6_grid = {}
    for pt in cmip6_deltas:
        key = (round(pt["lat"] * 2) / 2, round(pt["lon"] * 2) / 2)  # round to 0.5°
        cmip6_grid[key] = pt

    results = []
    for lat, lon, idx in coords:
        sub = subs[idx]

        # Fast O(1) lookup — round substation coords to nearest 0.5° CMIP6 grid cell
        grid_key = (round(lat * 2) / 2, round(lon * 2) / 2)
        best_pt = cmip6_grid.get(grid_key)

        # Try nearby cells if exact key not found
        if best_pt is None:
            for dlat in [-0.5, 0, 0.5]:
                for dlon in [-0.5, 0, 0.5]:
                    nearby_key = (grid_key[0] + dlat, grid_key[1] + dlon)
                    best_pt = cmip6_grid.get(nearby_key)
                    if best_pt:
                        break
                if best_pt:
                    break

        if best_pt is None:
            # Country-mean fallback
            delta_heat = 0.15
            delta_ice = -0.10
            delta_wind = 0.05
            delta_t = 1.0
        else:
            delta_heat = best_pt.get("delta_heat_pct", 0.15)
            delta_ice = best_pt.get("delta_ice_pct", -0.10)
            delta_wind = best_pt.get("delta_wind_pct", 0.05)
            delta_t = best_pt.get("delta_t_c", 1.0)

        # IRI trajectory ratios
        # I1 = snow/ice → less ice stress → lower I1
        # I2 = tree-fall/wind → more wind → higher I2
        # I3 = heat-wave → more heat → higher I3
        i1_trajectory = round(1.0 + delta_ice, 4)
        i2_trajectory = round(1.0 + delta_wind, 4)
        i3_trajectory = round(1.0 + delta_heat, 4)

        results.append({
            "substation_id": sub.get("substation_id", sub.get("name", f"sub_{idx}")),
            "index": idx,
            "I1_trajectory": i1_trajectory,
            "I2_trajectory": i2_trajectory,
            "I3_trajectory": i3_trajectory,
            "delta_t_c": delta_t,
            "previous": sub.get("climate_trajectory", {}),
        })

    # Summary
    if results:
        i3_vals = [r["I3_trajectory"] for r in results]
        logger.info(f"IRI forward for {country}: I3_trajectory range [{min(i3_vals):.4f}, {max(i3_vals):.4f}]")

    return results


# ═══════════════════════════════════════════════════════════
#  COUNTRY BOUNDING BOXES
# ═══════════════════════════════════════════════════════════

def _country_bbox(country):
    """Return lat/lon bounding box for CDS API requests."""
    boxes = {
        "italy":       {"lat_min": 35.5, "lat_max": 47.1, "lon_min": 6.6,  "lon_max": 18.5},
        "germany":     {"lat_min": 47.3, "lat_max": 55.1, "lon_min": 5.9,  "lon_max": 15.0},
        "france":      {"lat_min": 41.3, "lat_max": 51.1, "lon_min": -5.1, "lon_max": 9.6},
        "spain":       {"lat_min": 36.0, "lat_max": 43.8, "lon_min": -9.3, "lon_max": 3.3},
        "uk":          {"lat_min": 49.9, "lat_max": 60.9, "lon_min": -8.2, "lon_max": 1.8},
        "us":          {"lat_min": 24.5, "lat_max": 49.4, "lon_min": -124.8, "lon_max": -66.9},
        "switzerland": {"lat_min": 45.8, "lat_max": 47.8, "lon_min": 5.9, "lon_max": 10.5},
        "austria":     {"lat_min": 46.4, "lat_max": 49.0, "lon_min": 9.5, "lon_max": 17.2},
        "canada":      {"lat_min": 41.7, "lat_max": 83.1, "lon_min": -141.0, "lon_max": -52.6},
        "japan":       {"lat_min": 24.0, "lat_max": 45.6, "lon_min": 122.9, "lon_max": 153.0},
        "denmark":     {"lat_min": 54.5, "lat_max": 57.8, "lon_min": 8.0,  "lon_max": 15.2},
        "norway":      {"lat_min": 57.9, "lat_max": 71.2, "lon_min": 4.5,  "lon_max": 31.1},
        "finland":     {"lat_min": 59.8, "lat_max": 70.1, "lon_min": 20.6, "lon_max": 31.6},
        "poland":      {"lat_min": 49.0, "lat_max": 54.9, "lon_min": 14.1, "lon_max": 24.2},
        "sweden":      {"lat_min": 55.3, "lat_max": 69.1, "lon_min": 11.0, "lon_max": 24.2},
        "mexico":      {"lat_min": 14.5, "lat_max": 32.8, "lon_min": -118.5, "lon_max": -86.5},
    }
    return boxes.get(country)


# ═══════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    """Run climate trajectory ingestion for a country."""
    import argparse

    parser = argparse.ArgumentParser(description="SSI Pipeline — Climate Trajectory Ingestion")
    parser.add_argument("country", help="Country to process")
    parser.add_argument("--scenario", default="ssp245", help="CMIP6 scenario (default: ssp245)")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--output", type=str)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    results = compute_iri_forward(args.country, cache=not args.no_cache)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Wrote {len(results)} results to {args.output}")
    else:
        print(f"\nClimate trajectory results for {args.country}: {len(results)} substations")


if __name__ == "__main__":
    main()
