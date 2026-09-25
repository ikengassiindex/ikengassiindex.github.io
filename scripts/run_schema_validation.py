#!/usr/bin/env python3
"""
run_schema_validation.py — Phase 1.1 validator runner.

Validates every country's grid-geo.json + ssi-data.json + bounds.json
against the canonical schemas in schemas/. Greenland excluded from
grid-geo (deliberate islanded-grid exception).

USAGE:  python3 scripts/run_schema_validation.py [--strict]
        --strict: exit 1 on any failure (for CI/pre-commit use)
"""
import json
import os
import sys
from pathlib import Path

# jsonschema package
try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema --break-system-packages")
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / 'schemas'

# Documented exceptions — these countries deliberately diverge from canonical
EXCEPTIONS = {
    'grid-geo.json': {'greenland'},  # islanded micro-grids, alternate schema
    'ssi-data.json': set(),
    'bounds.json':   set(),
}

def load_slugs():
    cj = json.load(open(REPO / 'intelligence' / 'countries.json'))
    return sorted([c['slug'] for c in cj['countries'] if 'slug' in c])

def load_validator(name):
    schema = json.load(open(SCHEMA_DIR / name))
    return Draft202012Validator(schema)

def _substation_validator():
    """Validator for a single substation record, resolved out of the ssi-data schema.

    Convention #79 moved the five largest countries (france, germany, us, uk,
    italy) from an inline `substations` array to a `substations_shards`
    manifest naming sibling files. The root schema alone cannot follow that
    indirection, so before this existed the validator reported one error —
    "'substations' is a required property" — and stopped. The consequence was
    not one error, it was zero coverage: ~470,000 substations in the cohort's
    biggest countries were never schema-checked at all. This resolves the
    shards so they are.
    """
    schema = json.load(open(SCHEMA_DIR / 'ssi-data.schema.json'))
    sub_schema = dict(schema['$defs']['substation'])
    sub_schema['$defs'] = schema['$defs']          # keep #/$defs/... refs resolvable
    return Draft202012Validator(sub_schema)


def _shard_paths(data, filepath):
    """Sibling shard files named by a Convention #79 manifest, in order."""
    out = []
    for entry in data.get('substations_shards') or []:
        rel = entry['path'] if isinstance(entry, dict) else entry
        out.append(filepath.parent / Path(rel).name)
    return out


def check(validator, filepath, max_errors=2):
    """Return None if file missing, list of error messages otherwise (empty = pass)."""
    if not filepath.exists():
        return None
    try:
        data = json.loads(filepath.read_text())
    except Exception as e:
        return [f'JSON-PARSE: {e}']
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    msgs = [
        '/' + '/'.join(str(p) for p in e.absolute_path) + ': ' + e.message[:120]
        for e in errors[:max_errors]
    ]

    # Convention #79 — descend into the shards the manifest names.
    if isinstance(data, dict) and data.get('substations_shards'):
        sub_v = _substation_validator()
        for shard in _shard_paths(data, filepath):
            if len(msgs) >= max_errors:
                break
            if not shard.exists():
                msgs.append(f'/substations_shards: missing shard file {shard.name}')
                continue
            try:
                part = json.loads(shard.read_text())
            except Exception as e:
                msgs.append(f'/{shard.name}: JSON-PARSE: {e}')
                continue
            records = part if isinstance(part, list) else (part.get('substations') or [])
            for i, rec in enumerate(records):
                if len(msgs) >= max_errors:
                    break
                for e in sub_v.iter_errors(rec):
                    msgs.append(
                        f'/{shard.name}/{i}/' + '/'.join(str(p) for p in e.absolute_path)
                        + ': ' + e.message[:120]
                    )
                    break        # one error per record is enough to fail it
    return msgs

def main():
    strict = '--strict' in sys.argv
    slugs = load_slugs()

    validators = {
        'grid-geo.json': load_validator('grid-geo.schema.json'),
        'ssi-data.json': load_validator('ssi-data.schema.json'),
        'bounds.json':   load_validator('bounds.schema.json'),
    }

    print(f"Validating {len(slugs)} countries against {len(validators)} schemas")
    print(f"Exceptions: " + ', '.join(f"{f}={list(e)}" for f, e in EXCEPTIONS.items() if e))
    print()

    # Header
    print(f"{'country':<14} {'grid-geo':<8}  {'ssi-data':<8}  {'bounds':<8}")
    print('-' * 50)

    totals = {f: {'pass': 0, 'fail': 0, 'skip': 0, 'missing': 0} for f in validators}
    all_failures = []

    for slug in slugs:
        row = [slug]
        for fname, v in validators.items():
            if slug in EXCEPTIONS[fname]:
                totals[fname]['skip'] += 1
                row.append('skip')
                continue
            errs = check(v, REPO / slug / fname)
            if errs is None:
                totals[fname]['missing'] += 1
                row.append('--')
            elif not errs:
                totals[fname]['pass'] += 1
                row.append('ok')
            else:
                totals[fname]['fail'] += 1
                row.append(f'FAIL({len(errs)})')
                for e in errs:
                    all_failures.append((slug, fname, e))
        flag = ' '
        if any(r.startswith('FAIL') for r in row[1:]):
            flag = '!'
        print(f"{flag}{row[0]:<13} {row[1]:<8}  {row[2]:<8}  {row[3]:<8}")

    print('-' * 50)
    for fname in validators:
        t = totals[fname]
        print(f"  {fname:<15}  pass={t['pass']:>2}  fail={t['fail']:>2}  skip={t['skip']:>2}  missing={t['missing']:>2}")

    if all_failures:
        print(f"\n=== FAILURE DETAILS ({len(all_failures)}) ===")
        for slug, fname, err in all_failures[:30]:
            print(f"  [{slug}/{fname}] {err}")
        if len(all_failures) > 30:
            print(f"  ...and {len(all_failures) - 30} more")

    total_fail = sum(t['fail'] for t in totals.values())
    if strict and total_fail:
        print(f"\nSTRICT MODE: {total_fail} validation failures → exit 1")
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
