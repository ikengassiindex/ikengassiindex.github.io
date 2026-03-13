#!/usr/bin/env python3
"""
SSI Intelligence Edition Auto-Updater
Runs monthly via GitHub Actions to:
1. Increment edition number in edition-config.json
2. Set active_edition_key to current month
3. Add next month's rotation entry if missing
4. Update ssi-data.json timestamps
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path('intelligence/edition-config.json')
COUNTRIES = ['france','italy','uk','us','germany','spain','switzerland','austria','canada']

def main():
    if not CONFIG_PATH.exists():
        print('ERROR: edition-config.json not found')
        sys.exit(1)

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    now = datetime.utcnow()
    current_key = f"{now.year}-{now.month:02d}"
    next_month = now.replace(day=1) + timedelta(days=32)
    next_key = f"{next_month.year}-{next_month.month:02d}"

    # Store previous active key for archival reference
    prev_active_key = config.get('active_edition_key')
    if prev_active_key:
        print(f"Previous active edition: {prev_active_key}")
        # Write prev key to file so workflow can read it
        Path('prev_edition_key.txt').write_text(prev_active_key)

    # Increment edition
    old_ed = config.get('current_edition', 0)
    new_ed = old_ed + 1
    config['current_edition'] = new_ed
    new_label = f"{new_ed:03d}"
    print(f"Edition incremented: {old_ed:03d} -> {new_label}")

    # Set active_edition_key to current month
    config['active_edition_key'] = current_key
    print(f"Active edition key set to: {current_key}")

    # Create rotation entry for current month if missing
    if current_key not in config.get('rotation', {}):
        prev_keys = sorted(config.get('rotation', {}).keys())
        if prev_keys:
            prev = config['rotation'][prev_keys[-1]]
            config['rotation'][current_key] = {
                'edition_label': new_label,
                'theme_index': (prev.get('theme_index', 0) % 12) + 1,
                'countries': prev['countries']
            }
        print(f"Created rotation entry for {current_key}")
    else:
        config['rotation'][current_key]['edition_label'] = new_label

    # Write back
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Config saved. Edition {new_label} active for {current_key}")

    # Update ssi-data.json timestamps
    today = now.strftime('%Y-%m-%d')
    for country in COUNTRIES:
        data_path = Path(country) / 'ssi-data.json'
        if not data_path.exists():
            print(f"  SKIP {country}: no ssi-data.json")
            continue
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'metadata' in data:
                data['metadata']['generated'] = today
            elif 'meta' in data:
                data['meta']['generated'] = today
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"  Updated {country}/ssi-data.json generated={today}")
        except Exception as e:
            print(f"  ERROR {country}: {e}")

if __name__ == '__main__':
    main()
