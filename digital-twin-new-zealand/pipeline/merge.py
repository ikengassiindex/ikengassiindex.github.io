#!/usr/bin/env python3
"""
Pipeline Merge — Combines all 7 Digital Twin module outputs into a single
combined_ingestion.json for downstream scoring and enrichment.

SSI v4.0.2 · New Zealand Digital Twin
"""
import json, os, sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

MODULES = [
    'd01_tso',
    'd02_regulator',
    'd03_hazard',
    'd04_statistics',
    'd05_osm',
    'd06_weather',
    'd07_copernicus',
]

def load_module_output(module_name):
    """Load a module's output.json."""
    path = os.path.join(ROOT_DIR, module_name, 'output.json')
    if not os.path.exists(path):
        print(f"  ⚠ {module_name}: output.json not found — skipping")
        return None
    with open(path) as f:
        data = json.load(f)
    # Validate minimum schema
    if 'meta' not in data:
        print(f"  ⚠ {module_name}: missing 'meta' key — skipping")
        return None
    return data

def merge_modules():
    """Merge all module outputs into combined ingestion file."""
    print("[merge] Combining Digital Twin module outputs...")
    modules = {}
    total_records = 0

    for mod_name in MODULES:
        data = load_module_output(mod_name)
        if data is not None:
            modules[mod_name] = data
            records = data['meta'].get('records', 0)
            total_records += records
            print(f"  ✓ {mod_name}: {records} records")
        else:
            print(f"  ✗ {mod_name}: not available")

    combined = {
        'meta': {
            'pipeline': 'SSI v4.0.2 Digital Twin — New Zealand',
            'country': 'New Zealand',
            'country_code': 'NZ',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'modules_loaded': len(modules),
            'modules_expected': len(MODULES),
            'total_records': total_records,
            'version': '4.0.2',
        },
        'modules': modules,
        'quality': {
            'completeness': round(len(modules) / len(MODULES) * 100, 1),
            'modules_missing': [m for m in MODULES if m not in modules],
        }
    }

    return combined

def main():
    combined = merge_modules()
    output_path = os.path.join(SCRIPT_DIR, 'combined_ingestion.json')
    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=2)

    loaded = combined['meta']['modules_loaded']
    expected = combined['meta']['modules_expected']
    print(f"\n[merge] Output written: {output_path}")
    print(f"[merge] Modules: {loaded}/{expected} loaded, {combined['meta']['total_records']} total records")

    if loaded < expected:
        missing = combined['quality']['modules_missing']
        print(f"[merge] WARNING: Missing modules: {', '.join(missing)}")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
