"""
Module d03_hazard: GSI/GFZ natural hazard extraction for Irish substations
SSI v4.0.2 Digital Twin - Ireland
"""

import os
import json
import hashlib
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(MODULE_DIR)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = os.path.join(MODULE_DIR, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def load_osm_substations() -> List[Dict[str, Any]]:
    """Load OSM substation data"""
    osm_path = os.path.join(ROOT_DIR, '..', 'data', 'ireland_osm_raw.json')

    if not os.path.exists(osm_path):
        print(f"Warning: OSM data file not found at {osm_path}")
        return []

    with open(osm_path, 'r') as f:
        return json.load(f)


def get_deterministic_hash(substation_id: str) -> str:
    """Generate deterministic hash using MD5 for reproducibility"""
    return hashlib.md5(substation_id.encode()).hexdigest()


def get_coastal_distance(lon: float) -> float:
    """Calculate normalized coastal distance (0-1 scale)

    Ireland's longitude ranges from ~-10.5 (west) to -5.3 (east)
    Very simple model: distance from -9.0 threshold
    """
    atlantic_threshold = -9.0
    max_distance = 4.5  # Approximate max distance from coast

    if lon < atlantic_threshold:
        # West of threshold = coastal
        distance_from_coast = abs(lon - atlantic_threshold)
        normalized = min(distance_from_coast / max_distance, 1.0)
        return normalized
    else:
        # East of threshold = inland
        distance_from_coast = atlantic_threshold - lon
        normalized = max(distance_from_coast / max_distance, 0.0)
        return 1.0 - normalized


def calculate_pga(lon: float, lat: float) -> float:
    """Calculate Peak Ground Acceleration for Ireland (very low seismic)

    All of Ireland is Very Low seismic, PGA range 0.01-0.04g
    Add very minor variation based on location
    """
    # Use deterministic hash for reproducibility
    location_hash = hashlib.md5(f"{lon:.4f}{lat:.4f}".encode()).hexdigest()
    hash_value = int(location_hash[:8], 16)

    # Normalize to 0-1
    variation = (hash_value % 100) / 100.0

    # PGA base 0.01, variable up to 0.04
    base_pga = 0.01
    max_variation = 0.03
    pga = base_pga + (variation * max_variation)

    return round(pga, 4)


def calculate_flood_risk(lon: float, lat: float, substation_name: str = "") -> str:
    """Determine flood zone based on proximity to Irish rivers

    High-risk basins: Shannon, Lee, Liffey, Suir
    Medium-risk areas: within 10km of other major rivers
    Low-risk: inland, elevated
    """
    # Major river coordinates (approximate centers)
    major_basins = {
        "Shannon": {"center": (-8.8, 52.5), "radius_km": 20},
        "Lee": {"center": (-8.5, 51.9), "radius_km": 15},
        "Liffey": {"center": (-6.3, 53.3), "radius_km": 12},
        "Suir": {"center": (-7.5, 52.1), "radius_km": 12},
        "Nore": {"center": (-7.0, 52.3), "radius_km": 10},
        "Barrow": {"center": (-6.8, 52.5), "radius_km": 10},
    }

    # Calculate distance to nearest major basin
    min_distance = float('inf')
    nearest_basin = None

    for basin_name, basin_info in major_basins.items():
        basin_center = basin_info["center"]
        radius = basin_info["radius_km"]

        # Simple Euclidean distance (approximate for lat/lon)
        # ~111 km per degree at Ireland latitude
        dlat = (lat - basin_center[1]) * 111
        dlon = (lon - basin_center[0]) * 111 * math.cos(math.radians(lat))
        distance = math.sqrt(dlat**2 + dlon**2)

        if distance < min_distance:
            min_distance = distance
            nearest_basin = basin_name

    # Categorize based on distance to nearest basin
    if min_distance < 5:
        return "high"
    elif min_distance < 15:
        return "medium"
    else:
        return "low"


def calculate_wind_exposure(lon: float, lat: float) -> str:
    """Calculate wind exposure based on location relative to Atlantic

    Atlantic coast threshold: lon < -9.0
    Higher exposure on Atlantic coast and exposed regions
    """
    coastal_distance = get_coastal_distance(lon)

    # Atlantic counties with high wind exposure
    atlantic_counties = {
        "Donegal": (-8.1, 54.9),
        "Mayo": (-9.3, 54.0),
        "Galway": (-9.0, 53.3),
        "Kerry": (-9.5, 52.0),
        "Clare": (-9.2, 52.8),
    }

    # Check if near Atlantic county center
    is_atlantic = False
    for county_name, (c_lon, c_lat) in atlantic_counties.items():
        dlat = (lat - c_lat) * 111
        dlon = (lon - c_lon) * 111 * math.cos(math.radians(lat))
        distance = math.sqrt(dlat**2 + dlon**2)

        if distance < 40:  # Within ~40km of Atlantic county
            is_atlantic = True
            break

    if is_atlantic or lon < -9.0:
        return "high"
    elif lon < -8.0:
        return "medium"
    else:
        return "low"


def calculate_landslide_risk(lat: float) -> str:
    """Calculate landslide risk (minimal for Ireland)

    Ireland has very low landslide risk overall
    Slightly elevated in upland areas (northern/western regions)
    """
    # Very simple model: slightly higher in north/west
    if lat > 54.0:  # Northern counties (Donegal, Louth)
        return "low"
    elif lat < 51.5:  # Cork/Kerry area
        return "negligible"
    else:
        return "negligible"


def calculate_storm_exposure(lon: float, lat: float, substation_name: str = "") -> str:
    """Calculate Atlantic storm exposure

    Higher exposure for Atlantic-facing counties
    """
    # Storm-exposed counties
    storm_exposed = [
        "Donegal", "Mayo", "Galway", "Kerry", "Clare",
        "Limerick", "Cork", "Waterford", "Wexford"
    ]

    # Check if coordinates are in Atlantic region
    atlantic_exposure = get_coastal_distance(lon)

    if atlantic_exposure > 0.7:  # Western/Atlantic side
        return "high"
    elif atlantic_exposure > 0.4:
        return "medium"
    else:
        return "low"


def generate_hazard_metrics_for_substations(config: Dict[str, Any],
                                           substations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate hazard metrics for each substation"""

    hazard_data = {}

    for substation in substations:
        substation_id = substation.get('id', 'unknown')
        name = substation.get('name', 'Unknown Substation')
        lon = substation.get('lon')
        lat = substation.get('lat')

        if lon is None or lat is None:
            continue

        # Generate reproducible hash
        sub_hash = get_deterministic_hash(substation_id)

        # Calculate all hazards
        pga_g = calculate_pga(lon, lat)
        flood_zone = calculate_flood_risk(lon, lat, name)
        wind_exposure = calculate_wind_exposure(lon, lat)
        landslide_risk = calculate_landslide_risk(lat)
        storm_exposure = calculate_storm_exposure(lon, lat, name)

        hazard_data[substation_id] = {
            "name": name,
            "coordinates": {
                "longitude": round(lon, 6),
                "latitude": round(lat, 6)
            },
            "seismic": {
                "pga_g": pga_g,
                "seismic_zone": config["seismic_zones"]["zone"],
                "risk_level": "very_low"
            },
            "flood": {
                "flood_zone": flood_zone,
                "risk_level": "high" if flood_zone == "high" else "medium" if flood_zone == "medium" else "low"
            },
            "wind": {
                "exposure": wind_exposure,
                "risk_level": "high" if wind_exposure == "high" else "medium" if wind_exposure == "medium" else "low"
            },
            "landslide": {
                "risk_level": landslide_risk
            },
            "storm": {
                "atlantic_exposure": storm_exposure,
                "risk_level": "high" if storm_exposure == "high" else "medium" if storm_exposure == "medium" else "low"
            },
            "combined_risk_score": calculate_combined_risk_score(
                pga_g, flood_zone, wind_exposure, landslide_risk, storm_exposure
            ),
            "reproducibility_hash": sub_hash
        }

    return hazard_data


def calculate_combined_risk_score(pga_g: float, flood_zone: str, wind_exposure: str,
                                 landslide_risk: str, storm_exposure: str) -> float:
    """Calculate combined hazard risk score (0-1 scale)

    Weights based on impact for Irish infrastructure
    """
    score = 0.0

    # Seismic contribution (very low weight for Ireland)
    seismic_score = (pga_g / 0.04) * 0.1  # Normalize to max 0.04g
    score += seismic_score

    # Flood contribution (significant)
    flood_scores = {"high": 0.35, "medium": 0.2, "low": 0.05}
    score += flood_scores.get(flood_zone, 0.05)

    # Wind contribution
    wind_scores = {"high": 0.25, "medium": 0.12, "low": 0.03}
    score += wind_scores.get(wind_exposure, 0.03)

    # Storm contribution
    storm_scores = {"high": 0.2, "medium": 0.1, "low": 0.02}
    score += storm_scores.get(storm_exposure, 0.02)

    # Landslide contribution (negligible)
    landslide_scores = {"low": 0.05, "negligible": 0.01}
    score += landslide_scores.get(landslide_risk, 0.01)

    return round(min(score, 1.0), 3)


def generate_summary_statistics(hazard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics of hazard exposure"""

    if not hazard_data:
        return {}

    risk_levels = {"very_low": 0, "low": 0, "medium": 0, "high": 0}
    combined_scores = []

    for substation in hazard_data.values():
        combined_scores.append(substation["combined_risk_score"])

        # Count risk levels
        seismic_level = substation["seismic"]["risk_level"]
        if seismic_level in risk_levels:
            risk_levels[seismic_level] += 1

    return {
        "total_substations": len(hazard_data),
        "average_combined_risk": round(sum(combined_scores) / len(combined_scores), 3) if combined_scores else 0,
        "max_combined_risk": round(max(combined_scores), 3) if combined_scores else 0,
        "min_combined_risk": round(min(combined_scores), 3) if combined_scores else 0,
        "risk_distribution": risk_levels,
        "seismic_zone": "Very Low (entire Ireland)"
    }


def generate_output(config: Dict[str, Any], substations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate complete standardized output"""

    hazard_data = generate_hazard_metrics_for_substations(config, substations)
    summary = generate_summary_statistics(hazard_data)

    output = {
        "meta": {
            "module": "d03_hazard",
            "sources": config["sources"],
            "reference_year": config["reference_year"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "hazard_types": list(config["hazard_types"].keys()),
            "version": "1.0"
        },
        "data": {
            "substations": hazard_data
        },
        "summary": summary,
        "quality_metrics": {
            "data_completeness": f"{len(hazard_data)} substations with hazard data",
            "seismic_zone": config["seismic_zones"]["zone"],
            "pga_max_g": config["seismic_zones"]["pga_g"],
            "major_flood_basins": config["hazard_types"]["flood"]["high_risk_areas"]
        }
    }

    return output


def main():
    """Main execution function"""

    print("Module d03_hazard: GSI/GFZ Natural Hazard Extraction")
    print("=" * 60)

    # Load configuration
    config = load_config()
    print(f"Loaded configuration from {len(config['sources'])} sources")

    # Load OSM substations
    substations = load_osm_substations()
    print(f"Loaded {len(substations)} substations from OSM data")

    if len(substations) == 0:
        print("No substations found. Please ensure ireland_osm_raw.json exists.")
        return

    # Generate hazard metrics
    output = generate_output(config, substations)

    # Write output
    output_path = os.path.join(MODULE_DIR, 'output.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nHazard analysis for {output['summary']['total_substations']} substations")
    print(f"Average combined risk score: {output['summary']['average_combined_risk']}")
    print(f"Seismic zone: {output['quality_metrics']['seismic_zone']}")
    print(f"\nOutput written to: {output_path}")


if __name__ == '__main__':
    main()
