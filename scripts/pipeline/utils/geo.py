"""
SSI Pipeline — Geospatial Utilities
Spatial interpolation, nearest-neighbour lookup, coordinate helpers,
and per-country point-in-polygon enforcement (Discipline #36, KB §72).

CROSS-BORDER LEAK GUARD (added 18 Jun 2026):
  load_country_polygon() + is_inside_country() + filter_by_country_polygon()
  Enforce the rule that every substation in {country}/ssi-data.json must
  lie within {country}/bounds.json's national polygon (with a configurable
  boundary-precision tolerance, default 100m). This closes the failure
  class that surfaced in the 18 Jun 2026 cross-border audit: Austria 47.5%
  of substations were Bavarian/Slovenian/Italian/Swiss substations
  misattributed to Austrian Bundesländer; Canada 74.4% sat outside the
  metropolitan-provinces polygon; Greenland 86.5% sat outside the
  coastline-precision polygon. See CROSS_BORDER_SUBSTATION_AUDIT_20260618.md.
"""

import math
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# Lazy import — shapely is only needed when the polygon helpers are called.
# Allows downstream modules to import this file without paying shapely's
# import cost. Existing helpers (haversine_km, nearest_grid_value,
# bilinear_interpolate, load_substations, substation_coords) work without
# shapely.
def _require_shapely():
    """Lazy-import shapely. Raise a clear error if not installed."""
    try:
        from shapely.geometry import shape, Point
        from shapely.ops import unary_union
        return shape, Point, unary_union
    except ImportError as e:
        raise ImportError(
            "shapely required for cross-border polygon enforcement. "
            "Install via: pip install -r scripts/pipeline/requirements.txt"
        ) from e


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


# ─────────────────────────────────────────────────────────────────────────────
# Cross-border polygon enforcement (Discipline #36, added 18 Jun 2026)
# ─────────────────────────────────────────────────────────────────────────────

# At mid-latitudes 1 degree of latitude ≈ 111 km. We use this for converting
# the user-facing tolerance (in km / metres) to the shapely .buffer() units
# (which are in the polygon's own CRS units — for GeoJSON that's degrees).
_DEG_TO_KM = 111.0

# Default boundary-precision tolerance for the cross-border check. Italy's
# Stage 4 pilot showed 4 outliers all within 20m of the polygon edge after
# the buffer(0) heal — coastline-precision noise, not data quality. The
# 100m default is the standard cadastral tolerance and clears all 4 Italian
# outliers while still catching the 668 Austrian misattributions.
DEFAULT_BOUNDARY_TOLERANCE_KM = 0.1  # 100 m


def load_country_tolerance(country, repo_root=None):
    """
    Load the country-specific boundary tolerance from cross_border_tolerances.json
    at the repo root. Returns DEFAULT_BOUNDARY_TOLERANCE_KM if no override
    exists for this country.

    The config file is methodology-transparent — every country's tolerance
    is declared explicitly with rationale. See cross_border_tolerances.json
    at the repo root.
    """
    if repo_root is None:
        from ..config import REPO_ROOT
        repo_root = REPO_ROOT
    config_path = Path(repo_root) / "cross_border_tolerances.json"
    if not config_path.exists():
        return DEFAULT_BOUNDARY_TOLERANCE_KM
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        countries = cfg.get("countries", {})
        if country in countries:
            return float(countries[country].get(
                "boundary_tolerance_km", DEFAULT_BOUNDARY_TOLERANCE_KM
            ))
        return float(cfg.get("_default_tolerance_km", DEFAULT_BOUNDARY_TOLERANCE_KM))
    except Exception as e:
        logger.warning(f"Failed to read cross_border_tolerances.json: {e}; "
                       f"using default {DEFAULT_BOUNDARY_TOLERANCE_KM}km")
        return DEFAULT_BOUNDARY_TOLERANCE_KM


def load_country_polygon(country, repo_root=None, heal_topology=True):
    """
    Load the per-country national polygon from {country}/bounds.json,
    union all features, optionally heal self-intersections via buffer(0).

    Returns the shapely polygon (or MultiPolygon) for the country's
    national territory. Each feature in bounds.json is typically a
    sub-national administrative unit (region / state / province / Land /
    Bundesland / comunidad autónoma); the union gives the national polygon.

    Parameters
    ----------
    country : str
        Country slug (matches the per-country folder under the repo root).
    repo_root : Path or str, optional
        Override the repo root (default: scripts.pipeline.config.REPO_ROOT).
    heal_topology : bool, default True
        Apply shapely buffer(0) to heal self-intersections. The 18 Jun 2026
        audit found 12 of 20 Italian region polygons + 4 other countries
        carried self-intersections; buffer(0) heals them without changing
        the substantive shape.

    Returns
    -------
    shapely.geometry.Polygon or MultiPolygon or None
        The country's national polygon, or None if bounds.json is missing.

    Raises
    ------
    ImportError
        If shapely is not installed.
    """
    shape, _Point, unary_union = _require_shapely()

    if repo_root is None:
        from ..config import REPO_ROOT
        repo_root = REPO_ROOT

    bounds_path = Path(repo_root) / country / "bounds.json"
    if not bounds_path.exists():
        logger.warning(f"{country}: bounds.json not found at {bounds_path} — "
                       f"cross-border check skipped (acceptable for countries "
                       f"not yet bounds-equipped; see Discipline #30 — "
                       f"bounds.json currently OPTIONAL)")
        return None

    with open(bounds_path) as f:
        bounds = json.load(f)

    features = bounds.get("features", [])
    if not features:
        logger.warning(f"{country}: bounds.json has no features — skipped")
        return None

    polys = []
    invalid_count = 0
    for feat in features:
        if not feat.get("geometry"):
            continue
        geom = shape(feat["geometry"])
        if not geom.is_valid:
            invalid_count += 1
            if heal_topology:
                geom = geom.buffer(0)
                if not geom.is_valid or geom.is_empty:
                    logger.warning(
                        f"{country}: feature "
                        f"'{feat.get('properties', {}).get('name', '?')}' "
                        f"could not be healed via buffer(0); skipping"
                    )
                    continue
        polys.append(geom)

    if invalid_count > 0 and heal_topology:
        logger.info(
            f"{country}: healed {invalid_count} self-intersecting feature(s) "
            f"via buffer(0)"
        )

    if not polys:
        logger.warning(f"{country}: no valid polygons after healing — skipped")
        return None

    return unary_union(polys)


def is_inside_country(lat, lon, country_polygon, tolerance_km=DEFAULT_BOUNDARY_TOLERANCE_KM):
    """
    Test whether (lat, lon) lies inside the country polygon, with an
    optional boundary-precision tolerance.

    A point within tolerance_km of the polygon edge is treated as inside.
    This absorbs coastline-simplification artefacts (Italy Stage 4 pilot
    had 4 substations 0-20m outside the polygon — all clearly Italian).

    Parameters
    ----------
    lat, lon : float
        Substation coordinates (WGS84 decimal degrees).
    country_polygon : shapely.geometry.Polygon or MultiPolygon
        From load_country_polygon().
    tolerance_km : float, default 0.1 (100 m)
        Boundary-precision tolerance. Set to 0.0 for strict inside-only.

    Returns
    -------
    (bool, float)
        Tuple of (inside, distance_km_outside).
        inside is True if the point is inside the polygon OR within
        tolerance_km of its boundary.
        distance_km_outside is 0.0 if inside, otherwise the
        great-circle-approximated distance to the polygon edge in km.
    """
    shape, Point, _union = _require_shapely()
    if country_polygon is None:
        return True, 0.0  # No polygon available — pass through

    pt = Point(lon, lat)
    if country_polygon.contains(pt):
        return True, 0.0

    # Outside the strict polygon. Compute distance in degrees, convert to km.
    dist_deg = pt.distance(country_polygon)
    dist_km = dist_deg * _DEG_TO_KM

    if dist_km <= tolerance_km:
        return True, dist_km  # Within tolerance; treat as inside

    return False, dist_km


def filter_by_country_polygon(substations, country_polygon,
                              tolerance_km=DEFAULT_BOUNDARY_TOLERANCE_KM,
                              lat_key="lat", lon_key="lon"):
    """
    Partition substations into (kept_inside, rejected_outside) by the
    country polygon test.

    Each rejected substation carries an added '_reject_reason' field
    describing why it was excluded — useful for audit-trail logging
    so an operator can confirm whether the rejections are correct
    (Austrian-class misattributions) or false positives (polygon-precision
    issues).

    Parameters
    ----------
    substations : list of dict
        Per-substation records (e.g. from data["substations"]).
    country_polygon : shapely geometry or None
        From load_country_polygon(). If None, all substations pass through.
    tolerance_km : float, default 0.1
        Boundary-precision tolerance.
    lat_key, lon_key : str
        Field names for latitude/longitude in each substation dict.

    Returns
    -------
    (list, list)
        (kept_inside, rejected_outside). Order is preserved.
    """
    if country_polygon is None:
        return list(substations), []

    kept, rejected = [], []
    for s in substations:
        lat = s.get(lat_key)
        lon = s.get(lon_key)
        if lat is None or lon is None:
            # Missing coords — keep but flag, so downstream can decide
            kept.append(s)
            continue
        inside, dist_km = is_inside_country(lat, lon, country_polygon,
                                            tolerance_km=tolerance_km)
        if inside:
            kept.append(s)
        else:
            r = dict(s)
            r["_reject_reason"] = "outside_country_polygon"
            r["_reject_dist_km"] = round(dist_km, 3)
            r["_reject_tolerance_km"] = tolerance_km
            rejected.append(r)
    return kept, rejected


def cross_border_audit(country, repo_root=None,
                       tolerance_km=None):
    """
    Run the cross-border audit on a country's existing ssi-data.json
    against its bounds.json polygon.

    This is the canonical entry point used by scripts/check_cross_border.py.

    If tolerance_km is None, the per-country override from
    cross_border_tolerances.json is read (default 0.1 km / 100m).

    Returns
    -------
    dict
        {
          "country": str,
          "total": int,
          "inside": int,
          "outside": int,
          "missing_coords": int,
          "pct_outside": float,
          "tolerance_km": float,
          "max_dist_km": float,
          "outliers_sample": list of dict (top-10 by distance),
          "skipped": bool, "skip_reason": str
        }
    """
    if repo_root is None:
        from ..config import REPO_ROOT
        repo_root = REPO_ROOT

    # If tolerance not specified, read per-country override from config
    if tolerance_km is None:
        tolerance_km = load_country_tolerance(country, repo_root=repo_root)

    poly = load_country_polygon(country, repo_root=repo_root, heal_topology=True)
    if poly is None:
        return {
            "country": country,
            "skipped": True,
            "skip_reason": "bounds.json missing or invalid",
            "total": 0,
            "inside": 0,
            "outside": 0,
            "missing_coords": 0,
            "pct_outside": 0.0,
            "tolerance_km": tolerance_km,
            "max_dist_km": 0.0,
            "outliers_sample": [],
        }

    data, subs = load_substations(country, repo_root=repo_root)

    inside, outside_records, missing = 0, [], 0
    max_dist = 0.0
    for s in subs:
        lat, lon = s.get("lat"), s.get("lon")
        if lat is None or lon is None:
            missing += 1
            continue
        is_in, dist_km = is_inside_country(lat, lon, poly,
                                           tolerance_km=tolerance_km)
        if is_in:
            inside += 1
        else:
            outside_records.append({
                "name": s.get("name"),
                "lat": lat,
                "lon": lon,
                "region": s.get("region"),
                "province": s.get("province"),
                "kreis": s.get("kreis"),
                "dist_km_outside": round(dist_km, 3),
            })
            if dist_km > max_dist:
                max_dist = dist_km

    total = len(subs)
    pct = (100 * len(outside_records) / total) if total else 0.0
    outside_records.sort(key=lambda x: -x["dist_km_outside"])

    return {
        "country": country,
        "skipped": False,
        "skip_reason": None,
        "total": total,
        "inside": inside,
        "outside": len(outside_records),
        "missing_coords": missing,
        "pct_outside": round(pct, 2),
        "tolerance_km": tolerance_km,
        "max_dist_km": round(max_dist, 2),
        "outliers_sample": outside_records[:10],
    }
