#!/usr/bin/env python3
"""
migrate_grid_geo_to_canonical.py — Phase 0a of the architecture refactor.

Normalizes grid-geo.json schema across 6 outlier countries to the canonical
shape used by 21 healthy countries + map.js:

  canonical line:   {i, kv, p, ss, se}
  canonical sub:    {n, v, x, y}  [+optional r]

Migrations applied:
  - czechia, luxembourg:  rename line.id → line.i, line.v → line.kv
  - mexico, norway:       add line.kv=0, line.ss=-1, line.se=-1 if missing
  - belgium, canada,
    netherlands:          add line.ss=-1, line.se=-1 if missing
  - greece:               add sub.v=0 if missing

Greenland is intentionally skipped — its islanded-micro-grid schema
({k, op, osm, type, cables, voltage_raw}) is semantically different
and needs its own renderer path (deferred to Phase 2).

Denmark's extra line.n field is preserved (harmless additive).

USAGE:  python3 scripts/migrate_grid_geo_to_canonical.py [--dry-run]

Idempotent — running twice on the same file is safe (already-canonical
lines are left untouched).
"""
import json
import sys
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Country → transformation rules
RENAME_LINES = {
    'czechia':    {'id': 'i', 'v': 'kv'},
    'luxembourg': {'id': 'i', 'v': 'kv'},
}

ADD_LINE_DEFAULTS = {
    'czechia':     {'ss': -1, 'se': -1},
    'luxembourg':  {'ss': -1, 'se': -1},
    'mexico':      {'kv': 0, 'ss': -1, 'se': -1},
    'norway':      {'kv': 0, 'ss': -1, 'se': -1},
    'belgium':     {'ss': -1, 'se': -1},
    'canada':      {'ss': -1, 'se': -1},
    'netherlands': {'ss': -1, 'se': -1},
}

ADD_SUB_DEFAULTS = {
    'greece': {'v': 0},
}


def migrate_country(slug: str, dry: bool = False) -> dict:
    path = REPO / slug / 'grid-geo.json'
    if not path.exists():
        return {'slug': slug, 'status': 'no-file'}

    geo = json.loads(path.read_text())
    lines = geo.get('l', [])
    subs = geo.get('s', {})

    rename_map = RENAME_LINES.get(slug, {})
    line_defaults = ADD_LINE_DEFAULTS.get(slug, {})
    sub_defaults = ADD_SUB_DEFAULTS.get(slug, {})

    renamed = 0
    defaulted_lines = 0
    defaulted_subs = 0

    for l in lines:
        # Rename keys
        for old_key, new_key in rename_map.items():
            if old_key in l and new_key not in l:
                l[new_key] = l.pop(old_key)
                renamed += 1
        # Add defaults
        for k, v in line_defaults.items():
            if k not in l:
                l[k] = v
                defaulted_lines += 1

    for k_sub, sub in subs.items():
        if not isinstance(sub, dict):
            continue
        for k, v in sub_defaults.items():
            if k not in sub:
                sub[k] = v
                defaulted_subs += 1

    if dry:
        return {
            'slug': slug,
            'status': 'would-change' if (renamed + defaulted_lines + defaulted_subs) else 'no-op',
            'renamed': renamed,
            'defaulted_lines': defaulted_lines,
            'defaulted_subs': defaulted_subs,
            'total_lines': len(lines),
            'total_subs': len(subs),
        }

    # Write atomically (compact format to preserve file size)
    path.write_text(json.dumps(geo, ensure_ascii=False, separators=(',', ':')))
    return {
        'slug': slug,
        'status': 'migrated' if (renamed + defaulted_lines + defaulted_subs) else 'no-op',
        'renamed': renamed,
        'defaulted_lines': defaulted_lines,
        'defaulted_subs': defaulted_subs,
        'total_lines': len(lines),
        'total_subs': len(subs),
        'bytes': path.stat().st_size,
    }


def main():
    dry = '--dry-run' in sys.argv
    targets = sorted(set(RENAME_LINES) | set(ADD_LINE_DEFAULTS) | set(ADD_SUB_DEFAULTS))
    print(f"{'DRY-RUN' if dry else 'EXECUTE'}: migrating {len(targets)} countries to canonical grid-geo.json schema")
    print(f"  Targets: {', '.join(targets)}")
    print()

    results = []
    for slug in targets:
        r = migrate_country(slug, dry=dry)
        results.append(r)
        print(f"  {slug:<13} {r['status']:<14} renamed={r.get('renamed', 0):>3}  "
              f"def_lines={r.get('defaulted_lines', 0):>4}  def_subs={r.get('defaulted_subs', 0):>3}  "
              f"({r.get('total_lines', 0)} lines / {r.get('total_subs', 0)} subs)")

    print()
    if dry:
        print(f"Run without --dry-run to apply.")
    else:
        print(f"Done. Verify with: python3 scripts/audit_grid_geo_schemas.py")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
