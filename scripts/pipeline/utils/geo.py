"""
SSI Pipeline — Geospatial Utilities
Spatial interpolation, nearest-neighbour lookup, and coordinate helpers.
"""

import math
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_grid_value(lat, lon, grid_points, value_key="value", max_distance_km=50.0):
    """
    Find the nearest grid point to (lat, lon) and return its value.
    grid_points: list of dicts with 'lat', 'lon', and value_key.
    Returns (value, distance_km) or (None, None) if no point within max_distance_km.
    """
    best_val = None
    best_dist = float("inf")

    for pt in grid_points:
        d = haversine_km(lat, lon, pt["lat"], pt["lon"])
        if d < best_dist:
            best_dist = d
            best_val = pt.get(value_key)

    if best_dist > max_distance_km:
        return None, None
    return best_val, best_dist


def bilinear_interpolate(lat, lon, grid_points, value_key="value", grid_spacing=0.05, _cache={}):
    """
    Bilinear interpolation on a regular grid.
    grid_points: list of dicts with 'lat', 'lon', and value_key.
    Falls back to nearest-neighbour if interpolation fails.
    Uses an internal cache for the grid lookup dict (built once per grid).
    """
    # Build lookup dict (cached by id of grid_points list)
    cache_key = (id(grid_points), value_key)
    if cache_key not in _cache:
        grid = {}
        for pt in grid_points:
            # Round to grid spacing to build clean lookup keys
            k_lat = round(round(pt["lat"] / grid_spacing) * grid_spacing, 4)
            k_lon = round(round(pt["lon"] / grid_spacing) * grid_spacing, 4)
            grid[(k_lat, k_lon)] = pt.get(value_key, 0)
        _cache[cache_key] = grid
    grid = _cache[cache_key]

    # Find bounding cell
    lat0 = round(math.floor(lat / grid_spacing) * grid_spacing, 4)
    lon0 = round(math.floor(lon / grid_spacing) * grid_spacing, 4)
    lat1 = round(lat0 + grid_spacing, 4)
    lon1 = round(lon0 + grid_spacing, 4)

    corners = [
        grid.get((lat0, lon0)),
        grid.get((lat0, lon1)),
        grid.get((lat1, lon0)),
        grid.get((lat1, lon1)),
    ]

    if None in corners:
        # Try nearby cells (handle edge cases near coastline)
        for dlat in [-grid_spacing, 0, grid_spacing]:
            for dlon in [-grid_spacing, 0, grid_spacing]:
                key = (round(lat0 + dlat, 4), round(lon0 + dlon, 4))
                if key in grid:
                    return grid[key]
        return None

    # Bilinear weights
    t = (lon - lat0) / grid_spacing if grid_spacing else 0  # guard div-by-zero
    u = (lat - lat0) / grid_spacing if grid_spacing else 0
    t = (lon - lon0) / grid_spacing
    u = (lat - lat0) / grid_spacing

    val = (corners[0] * (1 - t) * (1 - u) +
           corners[1] * t * (1 - u) +
           corners[2] * (1 - t) * u +
           corners[3] * t * u)
    return val


def load_substations(country, repo_root=None):
    """
    Load substations from ssi-data.json for a country.

    Handles two data formats:
    1. Dict format: substations = [{name, lat, lon, ...}, ...]
    2. Compact array format: substations = [[val1, val2, ...], ...]
       with sub_fields = ["name", "lon", "lat", ...] mapping
    """
    if repo_root is None:
        from ..config import REPO_ROOT
        repo_root = REPO_ROOT

    data_path = Path(repo_root) / country / "ssi-data.json"
    if not data_path.exists():
        raise FileNotFoundError(f"No ssi-data.json found at {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    raw_subs = data.get("substations", [])

    # Detect compact array format and convert to dicts
    if raw_subs and isinstance(raw_subs[0], list):
        fields = data.get("sub_fields", [])
        if not fields:
            raise ValueError(f"Compact array format but no sub_fields in {data_path}")
        subs = []
        for arr in raw_subs:
            d = {}
            for i, field in enumerate(fields):
                if i < len(arr):
                    val = arr[i]
                    # Expand nested dicts/lists stored as JSON
                    if field in ("components", "ci", "modifiers") and isinstance(val, str):
                        try:
                            val = json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    d[field] = val
            # Ensure substation_id exists
            if "substation_id" not in d:
                d["substation_id"] = d.get("name", f"sub_{len(subs)}")
            subs.append(d)
        # Store converted format back for downstream use
        data["_compact_format"] = True
        data["_sub_fields"] = fields
    else:
        subs = raw_subs

    logger.info(f"Loaded {len(subs)} substations for {country}")
    return data, subs


def substation_coords(substations):
    """Extract (lat, lon, index) tuples for spatial queries."""
    coords = []
    for i, sub in enumerate(substations):
        lat = sub.get("lat")
        lon = sub.get("lon")
        if lat is not None and lon is not None:
            coords.append((lat, lon, i))
    return coords


def classify_seismic_zone(pga_g):
    """
    Classify seismic zone from PGA (g) using Italian seismic classification.
    Zone 1: PGA >= 0.25g (highest hazard)
    Zone 2: 0.15 <= PGA < 0.25g
    Zone 3: 0.05 <= PGA < 0.15g
    Zone 4: PGA < 0.05g (lowest hazard)
    """
    if pga_g >= 0.25:
        return 1
    elif pga_g >= 0.15:
        return 2
    elif pga_g >= 0.05:
        return 3
    else:
        return 4
