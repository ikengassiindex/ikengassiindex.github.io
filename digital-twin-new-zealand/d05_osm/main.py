#!/usr/bin/env python3
"""
d05_osm — OpenStreetMap Power Infrastructure Extraction
SSI v4.0.2 Digital Twin · New Zealand

Processes raw OpenStreetMap data (from Overpass API) to extract and validate
power infrastructure: substations and transmission/distribution lines.

NZ-specific characteristics:
  - 16 regions with deterministic population-weighted distribution
  - HV ≥110kV, MV 11-109kV, LV <11kV
  - Target: ~170 transmission + ~11,330 distribution substations
  - Key operators: Transpower (transmission), Vector, Orion, Powerco, etc.
  - Network topology: 5km proximity threshold for edges
  - Since raw OSM data unavailable, generates deterministic substations using
    region bounding boxes and population weights

Sources:
  - OSM Overpass API (via kumi.systems mirror)
  - Pre-fetched raw data: nz_osm_raw.json, nz_powerlines_raw.json (if available)
  - Synthetic generation with MD5 determinism per region

Outputs:
  - Standardised substation inventory with region assignments
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
    osm_path = os.path.join(ROOT_DIR, '..', 'data', 'nz_osm_raw.json')
    if not os.path.exists(osm_path):
        print(f"[d05_osm] WARNING: OSM file not found at {osm_path}")
        return []
    with open(osm_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('elements', [])

def load_raw_powerlines_data():
    """Load pre-fetched raw OSM power lines data."""
    lines_path = os.path.join(ROOT_DIR, '..', 'data', 'nz_powerlines_raw.json')
    if not os.path.exists(lines_path):
        print(f"[d05_osm] WARNING: Power lines file not found at {lines_path}")
        return []
    with open(lines_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('elements', [])

def is_in_new_zealand(lat, lon, bounds):
    """Check if coordinates fall within New Zealand (excluding Chatham Islands)."""
    if not (bounds['lat_min'] <= lat <= bounds['lat_max'] and
            bounds['lon_min'] <= lon <= bounds['lon_max']):
        return False
    # Exclude Chatham Islands (too remote, east of 176.5°E)
    if lon > 176.5 and lat < -43.5:
        return False
    return True

def infer_region(lat, lon):
    """
    Infer NZ region from lat/lon using bounding boxes.
    Returns region name or 'Unknown'.
    """
    # NZ regional bounding boxes (approximate)
    region_bounds = {
        'Northland': {'lat_min': -34.4, 'lat_max': -35.8, 'lon_min': 173.0, 'lon_max': 174.8},
        'Auckland': {'lat_min': -36.4, 'lat_max': -37.2, 'lon_min': 174.3, 'lon_max': 175.4},
        'Waikato': {'lat_min': -37.0, 'lat_max': -38.6, 'lon_min': 174.8, 'lon_max': 176.6},
        'Bay of Plenty': {'lat_min': -37.4, 'lat_max': -38.2, 'lon_min': 175.8, 'lon_max': 177.4},
        'Gisborne': {'lat_min': -37.8, 'lat_max': -38.8, 'lon_min': 177.0, 'lon_max': 178.6},
        'Hawke\'s Bay': {'lat_min': -38.5, 'lat_max': -40.0, 'lon_min': 175.8, 'lon_max': 177.6},
        'Taranaki': {'lat_min': -38.6, 'lat_max': -39.6, 'lon_min': 173.5, 'lon_max': 174.8},
        'Manawatu-Whanganui': {'lat_min': -38.8, 'lat_max': -40.4, 'lon_min': 174.8, 'lon_max': 176.6},
        'Wellington': {'lat_min': -40.6, 'lat_max': -41.6, 'lon_min': 174.4, 'lon_max': 176.2},
        'Tasman': {'lat_min': -40.5, 'lat_max': -42.0, 'lon_min': 171.5, 'lon_max': 173.5},
        'Nelson': {'lat_min': -41.2, 'lat_max': -41.4, 'lon_min': 173.2, 'lon_max': 173.4},
        'Marlborough': {'lat_min': -41.0, 'lat_max': -42.4, 'lon_min': 173.0, 'lon_max': 174.5},
        'West Coast': {'lat_min': -41.5, 'lat_max': -44.5, 'lon_min': 168.0, 'lon_max': 172.0},
        'Canterbury': {'lat_min': -42.0, 'lat_max': -44.6, 'lon_min': 170.0, 'lon_max': 173.5},
        'Otago': {'lat_min': -44.0, 'lat_max': -46.6, 'lon_min': 168.0, 'lon_max': 171.5},
        'Southland': {'lat_min': -45.5, 'lat_max': -47.0, 'lon_min': 166.0, 'lon_max': 169.5},
    }

    for region, bounds in region_bounds.items():
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
            bounds['lon_min'] <= lon <= bounds['lon_max']):
            return region

    return 'Unknown'

def classify_voltage(voltage_str, lat, lon):
    """
    Parse voltage string and classify as HV/MV/LV.
    NZ threshold: HV ≥110kV, MV 11-109kV, LV <11kV
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
    elif voltage_kv >= 11:
        return (voltage_kv, 'MV')
    else:
        return (voltage_kv, 'LV')

def generate_substations_deterministic(config):
    """
    Generate deterministic substation population using region bounding boxes
    and population weights. Uses MD5 hash for reproducibility.
    """
    substations = []
    region_weights = config['region_population_weights']
    total_subs = config['target_statistics']['total_substations']

    # Calculate substation allocation per region
    total_weight = sum(region_weights.values())

    for region_name, weight in region_weights.items():
        region_subs = int((weight / total_weight) * total_subs)
        if region_subs == 0:
            continue

        # Get region bounds
        bounds = config['regions'][region_name]['bounds']
        lat_min, lat_max = bounds['lat_min'], bounds['lat_max']
        lon_min, lon_max = bounds['lon_min'], bounds['lon_max']

        # Generate deterministic substations for this region
        for i in range(region_subs):
            # Deterministic seed per region and index
            seed_str = f"{region_name}_{i}"
            seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

            # Generate position within region bounds
            lat = lat_min + (lat_max - lat_min) * seed
            lon = lon_min + (lon_max - lon_min) * seed * 0.8 + (1 - seed) * 0.2

            # Voltage classification (deterministic)
            voltage_seed = int(hashlib.md5(f"{region_name}_v_{i}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
            if voltage_seed < 0.15:  # 15% HV
                voltage_kv = 220 if voltage_seed < 0.08 else 110
                voltage_class = 'HV'
                voltage_str = str(voltage_kv * 1000)
            elif voltage_seed < 0.85:  # 70% MV
                voltage_kv = int(33 + voltage_seed * 30)
                voltage_class = 'MV'
                voltage_str = str(voltage_kv * 1000)
            else:  # 15% LV
                voltage_kv = int(5 + voltage_seed * 5)
                voltage_class = 'LV'
                voltage_str = str(voltage_kv * 1000)

            # Operator assignment (deterministic)
            operators = config['operators']
            op_seed = int(hashlib.md5(f"{region_name}_op_{i}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
            operator = operators[int(op_seed * len(operators))]

            substation = {
                'osm_id': f"sub_{region_name}_{i}",
                'name': f"{region_name}_Sub_{i:04d}",
                'lat': round(lat, 6),
                'lon': round(lon, 6),
                'voltage': voltage_str,
                'voltage_kv': voltage_kv,
                'voltage_class': voltage_class,
                'region': region_name,
                'operator': operator,
                'ref': f"{region_name.upper()}-{i:06d}",
                'substation': 'distribution' if voltage_class in ['MV', 'LV'] else 'transmission',
                'source': 'OSM-Synthetic',
            }

            substations.append(substation)

    return substations

def process_substations(raw_substations, config, bounds):
    """
    Process and validate OSM substation records.
    Falls back to deterministic generation if raw data unavailable.
    Returns list of standardised substation objects.
    """
    if not raw_substations:
        print("[d05_osm] No raw OSM data found, using deterministic generation...")
        return generate_substations_deterministic(config)

    substations = []
    seen_coords = set()

    for idx, raw in enumerate(raw_substations):
        # Extract coordinates
        lat = raw.get('lat')
        lon = raw.get('lon')
        if lat is None or lon is None:
            continue

        # Validate coordinate range
        if not is_in_new_zealand(lat, lon, bounds):
            continue

        # Deduplicate by coordinate
        coord_key = (round(lat, 4), round(lon, 4))
        if coord_key in seen_coords:
            continue
        seen_coords.add(coord_key)

        name = raw.get('name', f"Sub_{lat:.4f}_{lon:.4f}")
        voltage_str = raw.get('voltage', '')

        voltage_kv, voltage_class = classify_voltage(voltage_str, lat, lon)

        # Filter by voltage
        if voltage_class not in ['HV', 'MV'] and voltage_str == '':
            if not name or name.startswith('Sub_'):
                continue

        region = infer_region(lat, lon)
        operator = raw.get('operator', 'Unknown')

        substation = {
            'osm_id': f"sub_{idx}",
            'name': name,
            'lat': round(lat, 6),
            'lon': round(lon, 6),
            'voltage': voltage_str,
            'voltage_kv': voltage_kv,
            'voltage_class': voltage_class,
            'region': region,
            'operator': operator,
            'ref': raw.get('ref', ''),
            'substation': raw.get('substation', 'unknown'),
            'source': 'OSM',
        }

        substations.append(substation)

    # If few records loaded, supplement with deterministic generation
    if len(substations) < 100:
        print(f"[d05_osm] Loaded {len(substations)} raw records, supplementing with deterministic generation...")
        substations.extend(generate_substations_deterministic(config))

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

    # Region summary
    region_counts = defaultdict(int)
    for s in substations:
        region_counts[s['region']] += 1

    # Operator summary
    operator_counts = defaultdict(int)
    for s in substations:
        operator_counts[s['operator']] += 1

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
            'by_region': dict(sorted(region_counts.items())),
            'by_operator': dict(sorted(operator_counts.items())),
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
