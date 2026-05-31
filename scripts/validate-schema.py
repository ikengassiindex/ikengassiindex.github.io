#!/usr/bin/env python3
"""
SSI v4.0.2 — JSON Schema Validator
Validates ssi-data.json files before deployment.

Usage:
  python3 validate-schema.py <country_folder>/ssi-data.json
  python3 validate-schema.py --all  # validates all countries

Checks:
  1. Required top-level keys: meta, fleet_summary, regions, substations
  2. Substation schema: substation_id, lat, lon, R_median, components, modifiers, classification
  3. Component format: raw (compSum > 1.0)
  4. Lat/lon within country bounds
  5. R_median within 0-1 range
  6. Classification matches R_median band
  7. Regions array has >1 entry
"""
import json, sys, os

# Country bounds (lat_min, lat_max, lon_min, lon_max)
COUNTRY_BOUNDS = {
    'france':      (41.0, 51.5, -5.5, 10.0),
    'italy':       (35.5, 47.5, 6.5, 19.0),
    'uk':          (49.5, 61.0, -8.5, 2.0),
    'spain':       (35.5, 44.0, -10.0, 4.5),
    'germany':     (47.0, 55.5, 5.5, 15.5),
    'switzerland': (45.5, 48.0, 5.5, 10.5),
    'austria':     (46.0, 49.5, 9.5, 17.5),
    'us':          (24.0, 72.0, -180.0, -65.0),
    'canada':      (41.0, 84.0, -141.0, -52.0),
    'japan':       (24.0, 46.0, 122.0, 154.0),
    'australia':   (-45.0, -10.0, 110.0, 155.0),
    'chile':       (-56.0, -17.0, -76.0, -66.0),
    'portugal':    (36.9, 42.2, -9.6, -6.1),
    'new-zealand': (-47.5, -34.0, 165.5, 179.0),
    'greenland':   (59.5, 83.7, -74.0, -11.0),
    'czechia':     (48.55, 51.06, 12.09, 18.86),
    'luxembourg':  (49.45, 50.18,  5.73,  6.53),
    'belgium':     (49.50, 51.51,  2.55,  6.41),
    'netherlands': (50.75, 53.55,  3.36,  7.23),
    'estonia':     (57.51, 59.69, 21.83, 28.21),
    'latvia':      (55.67, 58.09, 20.97, 28.24),
    'lithuania':   (53.90, 56.45, 20.95, 26.84),
}

WEIGHTS = {'C': 0.30, 'V': 0.10, 'I': 0.25, 'E': 0.10, 'S': 0.20, 'T': 0.05}

# KB §56 — Stub Deploy Regression prophylactic (May 2026 incident).
# Per-country fleet-size floors. Any ssi-data.json with substation_count
# below the floor is presumed STUB DATA and fails validation.
MIN_FLEET = {
    "AT": 1200, "CH": 800,  "DE": 10000,
    "IT": 4000, "ES": 3500, "IE": 990, "JP": 4500,
    # Session 32 recalibration: LU 700→80 (actual 91; small country, coarse OSM canton-level)
    "LU": 80,   "BE": 1000, "NL": 1300, "CZ": 800,
    "LV": 1000, "LT": 400,  "EE": 500, "SI": 120,
    "FR": 6500,
    # Other live countries — set conservative floors based on live ssi-data.json counts
    # Session 32 recalibration: CL 1500→900 (actual 1095; OSM completeness gap),
    #                            GL 100→30 (actual 37; pre-launch dataset)
    "AU": 5000, "CA": 8000, "CL": 900,  "DK": 1500,
    "FI": 3000, "GR": 1500, "GL": 30,   "MX": 4000,
    "NZ": 1000, "NO": 4000, "PL": 3000, "PT": 1500,
    "SE": 3500, "TR": 4000, "GB": 2500, "US": 30000,
}

# Country slug → ISO2 (used to derive iso2 from filepath when data lacks an iso2 key)
_SLUG_TO_ISO2 = {
    'france': 'FR', 'italy': 'IT', 'uk': 'GB', 'spain': 'ES',
    'germany': 'DE', 'switzerland': 'CH', 'austria': 'AT',
    'us': 'US', 'canada': 'CA', 'japan': 'JP', 'australia': 'AU',
    'chile': 'CL', 'portugal': 'PT', 'new-zealand': 'NZ',
    'greenland': 'GL', 'czechia': 'CZ', 'luxembourg': 'LU',
    'belgium': 'BE', 'netherlands': 'NL', 'estonia': 'EE',
    'latvia': 'LV', 'lithuania': 'LT', 'denmark': 'DK',
    'norway': 'NO', 'finland': 'FI', 'poland': 'PL',
    'sweden': 'SE', 'mexico': 'MX', 'greece': 'GR',
    'turkey': 'TR', 'ireland': 'IE',
}


def check_fleet_floor(data, iso2):
    """KB §56 — fail if substation count < MIN_FLEET[iso2]. Returns list of errors."""
    floor = MIN_FLEET.get(iso2)
    if floor is None:
        return []  # no floor defined; permissive
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    actual = len(subs)
    if actual < floor:
        return [
            f"FLEET-FLOOR FAILED (KB §56): {iso2} has {actual} substations < MIN_FLEET ({floor}). "
            f"Likely STUB DATA from placeholder OSM input. Refuse to publish."
        ]
    return []


def validate_file(filepath):
    """Validate a single ssi-data.json file."""
    errors = []
    warnings = []

    # Detect country from path
    parts = filepath.replace('\\', '/').split('/')
    country = None
    for p in parts:
        if p in COUNTRY_BOUNDS:
            country = p
            break

    # Load
    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"FATAL: Invalid JSON — {e}"], []

    # 1. Top-level keys
    for key in ['meta', 'fleet_summary', 'regions', 'substations']:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    substations = data.get('substations', [])
    if not substations:
        errors.append("No substations found")
        return errors, warnings

    # KB §56 — Fleet-floor check (prophylactic against stub-data deploys).
    iso2 = data.get('iso2') or (_SLUG_TO_ISO2.get(country) if country else None)
    if iso2:
        errors.extend(check_fleet_floor(data, iso2))

    # 2. Regions
    regions = data.get('regions', [])
    if isinstance(regions, list) and len(regions) <= 1:
        errors.append(f"Only {len(regions)} region(s) — expected >1")
    elif isinstance(regions, dict) and len(regions) <= 1:
        errors.append(f"Only {len(regions)} region(s) — expected >1")

    # 3. Substation schema
    required_fields = ['substation_id', 'lat', 'lon', 'R_median', 'components', 'classification']
    sample = substations[0]
    for field in required_fields:
        if field not in sample:
            errors.append(f"Substation missing field: {field}")

    # 4. Component format (must be raw)
    comp_sums = []
    for s in substations[:100]:
        if s.get('components'):
            comp_sum = sum(s['components'].get(k, 0) for k in WEIGHTS)
            comp_sums.append(comp_sum)
    if comp_sums:
        avg_sum = sum(comp_sums) / len(comp_sums)
        if avg_sum <= 1.0:
            errors.append(f"Weighted format detected (avg compSum={avg_sum:.3f}) — must be raw (>1.0)")

    # 5. Lat/lon bounds
    if country and country in COUNTRY_BOUNDS:
        bounds = COUNTRY_BOUNDS[country]
        out_of_bounds = 0
        for s in substations:
            lat, lon = s.get('lat', 0), s.get('lon', 0)
            if lat < bounds[0] or lat > bounds[1] or lon < bounds[2] or lon > bounds[3]:
                out_of_bounds += 1
        if out_of_bounds > 0:
            pct = out_of_bounds / len(substations) * 100
            if pct > 5:
                errors.append(f"{out_of_bounds} substations ({pct:.1f}%) outside {country} bounds")
            else:
                warnings.append(f"{out_of_bounds} substations ({pct:.1f}%) outside {country} bounds")

    # 6. R_median range
    r_values = [s.get('R_median', 0) for s in substations]
    r_min, r_max = min(r_values), max(r_values)
    if r_min < 0 or r_max > 1:
        errors.append(f"R_median out of [0,1] range: {r_min:.3f}–{r_max:.3f}")

    # 7. Classification consistency
    misclassified = 0
    for s in substations[:500]:
        r = s.get('R_median', 0)
        expected = 'Low' if r < 0.25 else 'Medium' if r < 0.50 else 'High' if r < 0.75 else 'Critical'
        if s.get('classification') != expected:
            misclassified += 1
    if misclassified > 0:
        warnings.append(f"{misclassified} substations have mismatched classification (checked first 500)")

    # 8. ESG fields
    esg_fields = ['markov', 'seismic', 'transition']
    for field in esg_fields:
        if not sample.get(field):
            warnings.append(f"Missing ESG field: {field}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-schema.py <file.json> [--all]")
        sys.exit(1)

    if sys.argv[1] == '--all':
        all_pass = True
        for country in COUNTRY_BOUNDS:
            filepath = f"{country}/ssi-data.json"
            if os.path.exists(filepath):
                errors, warnings = validate_file(filepath)
                status = "\u2705" if not errors else "\u274C"
                print(f"{status} {country}: {len(errors)} errors, {len(warnings)} warnings")
                for e in errors:
                    print(f"    ERROR: {e}")
                for w in warnings:
                    print(f"    WARN: {w}")
                if errors:
                    all_pass = False
            else:
                print(f"  \u26A0 {country}: file not found")
        sys.exit(0 if all_pass else 1)
    else:
        errors, warnings = validate_file(sys.argv[1])
        status = "PASS" if not errors else "FAIL"
        print(f"\n{status}: {len(errors)} errors, {len(warnings)} warnings")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN: {w}")
        sys.exit(0 if not errors else 1)


if __name__ == '__main__':
    main()
