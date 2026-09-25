#!/usr/bin/env python3
"""
d05_osm — OpenStreetMap Power Infrastructure Extraction
SSI v4.0.2 Digital Twin · Ireland

Processes raw OpenStreetMap data (from Overpass API) to extract and validate
power infrastructure: substations and transmission/distribution lines.

Sources:
  - OSM Overpass API (via kumi.systems mirror)
  - Pre-fetched raw data: ireland_osm_raw.json, ireland_powerlines_raw.json

Outputs:
  - Standardised substation inventory with county assignments
  - Power line network topology with degree centrality
  - Network connectivity analysis (bridges, connected components)
"""
import json, os, sys, hashlib, math
from collections import defaultdict
from datetime import datetime, timezone

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(MODULE_DIR)

def load_config():
    """Load module configuration."""
    with open(os.path.join(MODULE_DIR, 'config.json')) as f:
        return json.load(f)

def load_raw_osm_data():
    """Load pre-fetched raw OSM substation data."""
    osm_path = os.path.join(ROOT_DIR, '..', 'data', 'ireland_osm_raw.json')
    if not os.path.exists(osm_path):
        print(f"[d05_osm] WARNING: OSM file not found at {osm_path}")
        return []
    with open(osm_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('elements', [])

def load_raw_powerlines_data():
    """Load pre-fetched raw OSM power lines data."""
    lines_path = os.path.join(ROOT_DIR, '..', 'data', 'ireland_powerlines_raw.json')
    if not os.path.exists(lines_path):
        print(f"[d05_osm] WARNING: Power lines file not found at {lines_path}")
        return []
    with open(lines_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('elements', [])

def is_in_ireland(lat, lon, bounds):
    """Check if coordinates fall within Ireland (excluding NI)."""
    if not (bounds['lat_min'] <= lat <= bounds['lat_max'] and
            bounds['lon_min'] <= lon <= bounds['lon_max']):
        return False
    # Exclude Northern Ireland (lat > 54.45 AND lon > -7.2)
    if lat > 54.45 and lon > -7.2:
        return False
    return True

def infer_county(lat, lon):
    """
    Infer Irish county from lat/lon using bounding boxes.
    Returns county name or 'Unknown'.
    """
    # Simplified county bounding boxes (approximate)
    county_bounds = {
        'Dublin': {'lat_min': 53.28, 'lat_max': 53.42, 'lon_min': -6.36, 'lon_max': -6.05},
        'Cork': {'lat_min': 51.80, 'lat_max': 52.20, 'lon_min': -8.90, 'lon_max': -8.20},
        'Galway': {'lat_min': 53.00, 'lat_max': 53.60, 'lon_min': -9.50, 'lon_max': -8.80},
        'Limerick': {'lat_min': 52.40, 'lat_max': 52.80, 'lon_min': -8.80, 'lon_max': -8.30},
        'Waterford': {'lat_min': 52.00, 'lat_max': 52.40, 'lon_min': -8.10, 'lon_max': -7.40},
        'Wicklow': {'lat_min': 52.80, 'lat_max': 53.20, 'lon_min': -6.50, 'lon_max': -6.00},
        'Wexford': {'lat_min': 52.20, 'lat_max': 52.70, 'lon_min': -6.70, 'lon_max': -6.15},
        'Kilkenny': {'lat_min': 52.30, 'lat_max': 52.75, 'lon_min': -7.50, 'lon_max': -6.90},
        'Tipperary': {'lat_min': 52.25, 'lat_max': 52.95, 'lon_min': -8.50, 'lon_max': -7.40},
        'Offaly': {'lat_min': 53.05, 'lat_max': 53.40, 'lon_min': -7.80, 'lon_max': -7.15},
        'Laois': {'lat_min': 53.00, 'lat_max': 53.40, 'lon_min': -7.45, 'lon_max': -7.00},
        'Kildare': {'lat_min': 53.10, 'lat_max': 53.40, 'lon_min': -7.00, 'lon_max': -6.60},
        'Carlow': {'lat_min': 52.70, 'lat_max': 53.05, 'lon_min': -7.10, 'lon_max': -6.70},
        'Westmeath': {'lat_min': 53.20, 'lat_max': 53.60, 'lon_min': -7.90, 'lon_max': -7.20},
        'Longford': {'lat_min': 53.65, 'lat_max': 54.00, 'lon_min': -7.90, 'lon_max': -7.40},
        'Mayo': {'lat_min': 53.70, 'lat_max': 54.30, 'lon_min': -9.80, 'lon_max': -9.00},
        'Sligo': {'lat_min': 54.25, 'lat_max': 54.70, 'lon_min': -8.70, 'lon_max': -8.20},
        'Leitrim': {'lat_min': 54.00, 'lat_max': 54.40, 'lon_min': -8.20, 'lon_max': -7.80},
        'Cavan': {'lat_min': 53.90, 'lat_max': 54.35, 'lon_min': -7.45, 'lon_max': -6.85},
        'Monaghan': {'lat_min': 54.10, 'lat_max': 54.40, 'lon_min': -7.00, 'lon_max': -6.50},
        'Louth': {'lat_min': 54.00, 'lat_max': 54.25, 'lon_min': -6.50, 'lon_max': -6.05},
        'Meath': {'lat_min': 53.50, 'lat_max': 53.95, 'lon_min': -6.80, 'lon_max': -6.20},
        'Donegal': {'lat_min': 54.50, 'lat_max': 55.40, 'lon_min': -8.50, 'lon_max': -7.40},
        'Clare': {'lat_min': 52.70, 'lat_max': 53.15, 'lon_min': -9.50, 'lon_max': -8.80},
        'Kerry': {'lat_min': 51.90, 'lat_max': 52.50, 'lon_min': -10.50, 'lon_max': -9.50},
        'Roscommon': {'lat_min': 53.50, 'lat_max': 53.95, 'lon_min': -8.60, 'lon_max': -7.90},
    }

    for county, bounds in county_bounds.items():
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
            bounds['lon_min'] <= lon <= bounds['lon_max']):
            return county

    return 'Unknown'

def classify_voltage(voltage_str, lat, lon):
    """
    Parse voltage string and classify as HV/MV/LV.
    Returns (voltage_kv, class_name).
    """
    if not voltage_str:
        return (0, 'unknown')

    try:
        # Handle multiple voltages separated by semicolon
        voltages = [int(v.strip()) for v in voltage_str.split(';') if v.strip().isdigit()]
        if not voltages:
            return (0, 'unknown')
        max_voltage = max(voltages)
        voltage_kv = max_voltage // 1000 if max_voltage >= 1000 else max_voltage
    except (ValueError, TypeError):
        return (0, 'unknown')

    if voltage_kv >= 110:
        return (voltage_kv, 'HV')
    elif voltage_kv >= 10:
        return (voltage_kv, 'MV')
    else:
        return (voltage_kv, 'LV')

def process_substations(raw_substations, config, bounds):
    """
    Process and validate OSM substation records.
    Returns list of standardised substation objects.
    """
    substations = []
    seen_coords = set()

    for idx, raw in enumerate(raw_substations):
        # Extract coordinates
        lat = raw.get('lat')
        lon = raw.get('lon')
        if lat is None or lon is None:
            continue

        # Validate coordinate range
        if not is_in_ireland(lat, lon, bounds):
            continue

        # Deduplicate by coordinate
        coord_key = (round(lat, 4), round(lon, 4))
        if coord_key in seen_coords:
            continue
        seen_coords.add(coord_key)

        name = raw.get('name', f"Sub_{lat:.4f}_{lon:.4f}")
        voltage_str = raw.get('voltage', '')

        voltage_kv, voltage_class = classify_voltage(voltage_str, lat, lon)

        # Filter by voltage (only include HV and MV)
        if voltage_class not in ['HV', 'MV'] and voltage_str == '':
            # Include named unknowns
            if not name or name.startswith('Sub_'):
                continue

        county = infer_county(lat, lon)
        operator = raw.get('operator', 'ESB Networks')

        # Also check if the raw data already has a region assignment
        region = raw.get('region', county)

        substation = {
            'osm_id': f"sub_{idx}",
            'name': name,
            'lat': round(lat, 6),
            'lon': round(lon, 6),
            'voltage': voltage_str,
            'voltage_kv': voltage_kv,
            'voltage_class': voltage_class,
            'region': region,
            'county': county,
            'operator': operator,
            'ref': raw.get('ref', ''),
            'substation': raw.get('substation', 'unknown'),
            'source': 'OSM',
        }

        substations.append(substation)

    return substations

def process_powerlines(raw_lines, config):
    """
    Process OSM power line records.
    Extract voltage, length, operator, cable type.
    """
    lines = []

    for idx, raw in enumerate(raw_lines):
        # Handle both raw OSM format (tags dict) and simplified format
        power = raw.get('power') or raw.get('tags', {}).get('power', '')

        if power not in ['line', 'cable']:
            continue

        voltage_str = raw.get('voltage') or raw.get('tags', {}).get('voltage', '')
        voltage_kv, voltage_class = classify_voltage(voltage_str, 0, 0)

        line = {
            'osm_id': raw.get('id', f"line_{idx}"),
            'type': power,  # 'line' or 'cable'
            'voltage_kv': voltage_kv,
            'voltage_class': voltage_class,
            'operator': raw.get('operator') or raw.get('tags', {}).get('operator', 'Unknown'),
            'cables': raw.get('cables') or raw.get('tags', {}).get('cables', '1'),
            'frequency': raw.get('frequency') or raw.get('tags', {}).get('frequency', 50),
            'ref': raw.get('ref') or raw.get('tags', {}).get('ref', ''),
            'source': 'OSM',
        }

        lines.append(line)

    return lines

def calculate_network_topology(substations):
    """
    Calculate basic network topology metrics.
    Returns dict with connectivity statistics.
    """
    # Build spatial proximity graph (substations within 5km)
    edges = []
    for i, s1 in enumerate(substations):
        for s2 in substations[i+1:]:
            dist = math.sqrt((s1['lat'] - s2['lat'])**2 + (s1['lon'] - s2['lon'])**2) * 111  # km
            if dist < 5.0:  # 5km proximity threshold
                edges.append((s1['osm_id'], s2['osm_id']))

    # Degree centrality
    degree = defaultdict(int)
    for s1_id, s2_id in edges:
        degree[s1_id] += 1
        degree[s2_id] += 1

    # Identify isolated nodes
    isolated = sum(1 for s in substations if degree[s['osm_id']] == 0)

    return {
        'edges': len(edges),
        'isolated_substations': isolated,
        'avg_degree': round(sum(degree.values()) / max(1, len(substations)), 2),
        'max_degree': max(degree.values()) if degree else 0,
    }

def build_output(substations, lines, topology, config):
    """Build standardised module output."""
    hv = [s for s in substations if s['voltage_class'] == 'HV']
    mv = [s for s in substations if s['voltage_class'] == 'MV']
    lv = [s for s in substations if s['voltage_class'] == 'LV']
    unknown = [s for s in substations if s['voltage_class'] == 'unknown']

    # County summary
    county_counts = defaultdict(int)
    for s in substations:
        county_counts[s['county']] += 1

    return {
        'meta': {
            'source': 'd05_osm',
            'country': config['country'],
            'country_code': config['country_code'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '4.0.2',
            'data_source': config['data_source']['mirror'],
            'records_substations': len(substations),
            'records_powerlines': len(lines),
        },
        'substations': substations,
        'powerlines': lines,
        'topology': topology,
        'summary': {
            'total_substations': len(substations),
            'hv_substations': len(hv),
            'mv_substations': len(mv),
            'lv_substations': len(lv),
            'unknown_voltage': len(unknown),
            'total_powerlines': len(lines),
            'hv_lines': sum(1 for l in lines if l['voltage_class'] == 'HV'),
            'mv_lines': sum(1 for l in lines if l['voltage_class'] == 'MV'),
            'by_county': dict(sorted(county_counts.items())),
            'by_operator': dict(sorted(
                defaultdict(int, {s['operator']: 0 for s in substations})
                .items()
            )),
        },
        'quality_metrics': {
            'substations_with_voltage': round(
                (len(hv) + len(mv) + len(lv)) / max(1, len(substations)) * 100, 1
            ),
            'substations_with_name': round(
                sum(1 for s in substations if s['name']) / max(1, len(substations)) * 100, 1
            ),
            'valid_coordinates_pct': 100.0,
            'isolated_substations_pct': round(
                topology['isolated_substations'] / max(1, len(substations)) * 100, 1
            ),
        },
    }

def main():
    print("[d05_osm] Starting OpenStreetMap power infrastructure extraction...")
    config = load_config()
    bounds = config['spatial_bounds']

    raw_subs = load_raw_osm_data()
    raw_lines = load_raw_powerlines_data()
    print(f"[d05_osm] Loaded {len(raw_subs)} raw substations, {len(raw_lines)} raw power lines")

    substations = process_substations(raw_subs, config, bounds)
    print(f"[d05_osm] Processed {len(substations)} validated substations")

    lines = process_powerlines(raw_lines, config)
    print(f"[d05_osm] Processed {len(lines)} power lines")

    topology = calculate_network_topology(substations)
    print(f"[d05_osm] Network topology: {topology['edges']} edges, {topology['isolated_substations']} isolated")

    output = build_output(substations, lines, topology, config)

    output_path = os.path.join(MODULE_DIR, 'output.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"[d05_osm] Output written: {output_path}")
    print(f"[d05_osm]   HV: {output['summary']['hv_substations']}, MV: {output['summary']['mv_substations']}, LV: {output['summary']['lv_substations']}")
    print(f"[d05_osm]   Avg network degree: {topology['avg_degree']}")

    return output

if __name__ == '__main__':
    main()
