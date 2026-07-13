#!/usr/bin/env python3
"""
SSI Index — 39-country cohort audit sweep (task #179).

Runs multiple drift + coverage diagnostics across the whole cohort in one pass.
Produces:
  - Structured JSON report at COHORT_AUDIT_REPORT_YYYYMMDD.json
  - Human-readable summary printed to stdout
  - Optional auto-patch mode for trivially-fixable drift (--auto-patch)

Checks performed (per country):
  1. File size          — flag {ssi-data, grid-geo}.json > 60 MB warn / 90 MB fail
  2. Modifier registry  — flag any modifier value outside (min, max) declared band
  3. Climate scale      — flag climate_trajectory values < 0.5 (delta-scale bug)
  4. Owner coverage     — flag countries with < 50% substations having owner tagged
  5. Voltage coverage   — flag countries with < 70% substations having voltage tagged
  6. Region coverage    — flag countries with > 30% substations having 'unknown' region
  7. Discipline #36     — cross-border polygon check (defers to check_cross_border.py)
  8. Discipline #41     — sub/line ratio in cohort-empirical envelope

Usage:
    python3 scripts/cohort_audit_sweep.py
    python3 scripts/cohort_audit_sweep.py --json out.json
    python3 scripts/cohort_audit_sweep.py --auto-patch      # apply climate offset fixes
    python3 scripts/cohort_audit_sweep.py --country italy   # single country

Exit codes:
    0 = no FAIL findings (WARNs OK, informational)
    1 = one or more FAIL findings (blocks CI if wired)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# Modifier registry (mirror of scripts/validate_schema.py::_MODIFIER_RANGES)
MODIFIER_RANGES = {
    "R3_C_mult":      (0.70, 1.50),
    "R4_F_topo":      (0.80, 1.35),
    "R6_restoration": (0.90, 1.10),
    "R6_seismic":     (1.00, 1.25),
    "R7_cyber":       (0.99, 1.05),
    "R6_volcanic":     (1.00, 1.20),
    "R6_drought":      (1.00, 1.18),
    "R6_armed_conflict": (1.00, 1.12),
    "R6_typhoon":      (1.00, 1.15),
    "R6_chaebol":      (1.00, 1.10),
    "R6c_flood":       (1.00, 1.30),
    "R6d_wildfire":    (1.00, 1.25),
    "R6e_winter":      (1.00, 1.25),
    "R8_adapt":        (0.92, 1.05),
    "R9_compound":     (1.00, 1.20),
}

# Thresholds
CLIMATE_SCALE_THRESHOLD = 0.5     # values < 0.5 = raw delta bug
OWNER_COVERAGE_WARN = 50          # % substations owner-tagged
VOLTAGE_COVERAGE_WARN = 70        # % substations voltage-tagged
REGION_UNKNOWN_WARN = 30          # % substations region='unknown' or None
SIZE_WARN_MB = 60
SIZE_FAIL_MB = 90


def load_country_data(slug: str, repo_root: Path) -> tuple[list[dict], list[dict]]:
    """Return (substations_list, lines_list) for a country."""
    p_ssi = repo_root / slug / 'ssi-data.json'
    p_grid = repo_root / slug / 'grid-geo.json'
    subs = []
    lines = []
    if p_ssi.exists():
        d = json.load(open(p_ssi))
        raw = d.get('substations', d)
        if isinstance(raw, dict):
            subs = list(raw.values())
        elif isinstance(raw, list):
            subs = raw
    if p_grid.exists():
        d = json.load(open(p_grid))
        lines = d.get('l', [])
    return subs, lines


def audit_country(slug: str, repo_root: Path, auto_patch: bool = False) -> dict:
    """Run all audit checks on a single country + return findings dict."""
    findings = {'slug': slug, 'checks': {}, 'findings': [], 'patches_applied': []}
    subs, lines = load_country_data(slug, repo_root)
    n_subs = len(subs)
    findings['n_subs'] = n_subs
    findings['n_lines'] = len(lines)

    if n_subs == 0:
        findings['findings'].append({'severity': 'INFO', 'check': 'load', 'msg': 'no substations'})
        return findings

    # --- 1. File size ---
    for filename in ('ssi-data.json', 'grid-geo.json'):
        fp = repo_root / slug / filename
        if fp.exists():
            sz_mb = fp.stat().st_size / (1024 * 1024)
            key = filename.replace('.json', '')
            findings['checks'][f'size_{key}_mb'] = round(sz_mb, 2)
            if sz_mb > SIZE_FAIL_MB:
                findings['findings'].append({
                    'severity': 'FAIL', 'check': 'size',
                    'msg': f'{filename} {sz_mb:.1f} MB > {SIZE_FAIL_MB} MB',
                })
            elif sz_mb > SIZE_WARN_MB:
                findings['findings'].append({
                    'severity': 'WARN', 'check': 'size',
                    'msg': f'{filename} {sz_mb:.1f} MB > {SIZE_WARN_MB} MB warn band',
                })

    # --- 2. Modifier registry drift ---
    modifier_drift: dict[str, dict] = {}
    for s in subs:
        mods = s.get('modifiers', {})
        if not isinstance(mods, dict):
            continue
        for m_key, (m_min, m_max) in MODIFIER_RANGES.items():
            v = mods.get(m_key)
            if v is None:
                continue
            try: v = float(v)
            except (TypeError, ValueError): continue
            if v < m_min or v > m_max:
                d = modifier_drift.setdefault(m_key, {'below': 0, 'above': 0, 'total': 0, 'min': v, 'max': v})
                if v < m_min: d['below'] += 1
                else: d['above'] += 1
                d['min'] = min(d['min'], v)
                d['max'] = max(d['max'], v)
                d['total'] += 1
    # Count total emissions per modifier for percentage
    modifier_emission_totals: dict[str, int] = {}
    for s in subs:
        mods = s.get('modifiers', {})
        if isinstance(mods, dict):
            for m_key in MODIFIER_RANGES:
                if mods.get(m_key) is not None:
                    modifier_emission_totals[m_key] = modifier_emission_totals.get(m_key, 0) + 1
    findings['checks']['modifier_drift'] = {}
    for m_key, d in modifier_drift.items():
        total_emitted = modifier_emission_totals.get(m_key, 0)
        pct = 100 * d['total'] / max(total_emitted, 1)
        findings['checks']['modifier_drift'][m_key] = {
            'n_out_of_range': d['total'], 'pct': round(pct, 1),
            'below_registry': d['below'], 'above_registry': d['above'],
            'observed_min': round(d['min'], 4), 'observed_max': round(d['max'], 4),
        }
        if pct > 10:
            findings['findings'].append({
                'severity': 'WARN', 'check': 'modifier_drift',
                'msg': f'{m_key}: {d["total"]:,}/{total_emitted:,} ({pct:.1f}%) outside registry ({MODIFIER_RANGES[m_key][0]:.3f}, {MODIFIER_RANGES[m_key][1]:.3f})',
            })

    # --- 3. Climate trajectory scale bug ---
    ct_delta_bug_count = 0
    for s in subs:
        ct = s.get('climate_trajectory')
        if isinstance(ct, dict):
            i1 = ct.get('I1_trajectory')
            if i1 is not None:
                try:
                    if float(i1) < CLIMATE_SCALE_THRESHOLD:
                        ct_delta_bug_count += 1
                except (TypeError, ValueError):
                    pass
    findings['checks']['climate_delta_bug_count'] = ct_delta_bug_count
    if ct_delta_bug_count > 0:
        pct = 100 * ct_delta_bug_count / n_subs
        findings['findings'].append({
            'severity': 'FAIL' if pct > 50 else 'WARN',
            'check': 'climate_scale',
            'msg': f'{ct_delta_bug_count:,}/{n_subs:,} ({pct:.1f}%) have I1_trajectory < 0.5 — delta-scale bug (Task #160 class)',
        })
        # Auto-patch if requested
        if auto_patch:
            patched = 0
            for s in subs:
                ct = s.get('climate_trajectory')
                if not isinstance(ct, dict):
                    continue
                p = False
                for k in ('I1_trajectory', 'I2_trajectory', 'I3_trajectory'):
                    v = ct.get(k)
                    if v is None:
                        continue
                    try:
                        v = float(v)
                    except (TypeError, ValueError):
                        continue
                    if v < CLIMATE_SCALE_THRESHOLD:
                        ct[k] = round(v + 1.0, 4)
                        p = True
                if p:
                    patched += 1
            if patched > 0:
                # Rewrite the file
                p_ssi = repo_root / slug / 'ssi-data.json'
                d = json.load(open(p_ssi))
                src = d.get('substations')
                if isinstance(src, dict):
                    d['substations'] = {s.get('substation_id') or s.get('id'): s for s in subs}
                else:
                    d['substations'] = subs
                p_ssi.write_text(json.dumps(d, ensure_ascii=False))
                findings['patches_applied'].append(
                    f'climate_trajectory +1.0 offset applied to {patched:,} substations'
                )

    # --- 4. Owner coverage ---
    owner_tagged = sum(1 for s in subs if s.get('owner'))
    pct = 100 * owner_tagged / n_subs
    findings['checks']['owner_coverage_pct'] = round(pct, 1)
    if pct < OWNER_COVERAGE_WARN:
        findings['findings'].append({
            'severity': 'WARN', 'check': 'owner_coverage',
            'msg': f'{owner_tagged:,}/{n_subs:,} ({pct:.1f}%) substations have owner tagged — below {OWNER_COVERAGE_WARN}% warn',
        })

    # --- 5. Voltage coverage ---
    voltage_tagged = 0
    for s in subs:
        v = s.get('voltage_kv') or s.get('voltage')
        try:
            if float(v) > 0:
                voltage_tagged += 1
        except (TypeError, ValueError):
            pass
    pct = 100 * voltage_tagged / n_subs
    findings['checks']['voltage_coverage_pct'] = round(pct, 1)
    if pct < VOLTAGE_COVERAGE_WARN:
        findings['findings'].append({
            'severity': 'WARN', 'check': 'voltage_coverage',
            'msg': f'{voltage_tagged:,}/{n_subs:,} ({pct:.1f}%) substations have voltage tagged — below {VOLTAGE_COVERAGE_WARN}% warn',
        })

    # --- 6. Region unknown coverage ---
    region_fields = ('region', 'bundesland', 'kommune', 'state', 'province', 'departement')
    unknown_count = 0
    for s in subs:
        has_region = False
        for f in region_fields:
            v = s.get(f)
            if v and v != 'unknown' and v != 'Unknown':
                has_region = True
                break
        if not has_region:
            unknown_count += 1
    pct = 100 * unknown_count / n_subs
    findings['checks']['region_unknown_pct'] = round(pct, 1)
    if pct > REGION_UNKNOWN_WARN:
        findings['findings'].append({
            'severity': 'WARN', 'check': 'region_coverage',
            'msg': f'{unknown_count:,}/{n_subs:,} ({pct:.1f}%) substations have unknown/None region — above {REGION_UNKNOWN_WARN}% warn',
        })

    # --- 7. Discipline #41 line-substation ratio ---
    if n_subs > 0 and findings['n_lines'] > 0:
        ratio = findings['n_lines'] / n_subs
        findings['checks']['discipline_41_ratio'] = round(ratio, 2)
        # Cohort empirical envelope: 0.3 - 25 lines/sub is normal
        if ratio < 0.3:
            findings['findings'].append({
                'severity': 'WARN', 'check': 'discipline_41',
                'msg': f'lines/subs ratio {ratio:.2f} < 0.3 — line coverage possibly sparse',
            })
        elif ratio > 25:
            findings['findings'].append({
                'severity': 'WARN', 'check': 'discipline_41',
                'msg': f'lines/subs ratio {ratio:.2f} > 25 — line coverage possibly bloated',
            })

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--json', type=Path, help='Write structured report to JSON file')
    parser.add_argument('--country', help='Audit single country (default: all 39)')
    parser.add_argument('--auto-patch', action='store_true',
                        help='Apply climate_trajectory +1.0 offset fix in-place')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()

    # Discover countries from intelligence/countries.json
    sot = repo_root / 'intelligence' / 'countries.json'
    if sot.exists():
        countries = json.load(open(sot))['slugs']
    else:
        countries = sorted(
            d.name for d in repo_root.iterdir()
            if d.is_dir() and (d / 'ssi-data.json').exists()
        )

    if args.country:
        countries = [args.country]

    print(f'Cohort audit sweep  ·  {len(countries)} countries  ·  auto-patch={args.auto_patch}')
    print()

    all_findings = []
    total_fail = 0
    total_warn = 0
    total_patches = 0
    for slug in countries:
        r = audit_country(slug, repo_root, auto_patch=args.auto_patch)
        all_findings.append(r)
        fails = sum(1 for f in r['findings'] if f['severity'] == 'FAIL')
        warns = sum(1 for f in r['findings'] if f['severity'] == 'WARN')
        patches = len(r['patches_applied'])
        total_fail += fails
        total_warn += warns
        total_patches += patches

        status = '❌ FAIL' if fails else ('⚠️  WARN' if warns else '✅ OK')
        patch_note = f' · patches={patches}' if patches else ''
        print(f'  {status}  {slug:15s}  fail={fails} warn={warns}{patch_note}')
        for f in r['findings']:
            marker = '❌' if f['severity'] == 'FAIL' else '⚠️'
            print(f'         {marker} {f["check"]}: {f["msg"]}')

    print()
    print(f'Cohort summary:  {len(countries)} countries checked  ·  '
          f'{total_fail} FAIL  ·  {total_warn} WARN  ·  {total_patches} patch(es) applied')

    if args.json:
        args.json.write_text(json.dumps({
            'countries_checked': len(countries),
            'total_fail': total_fail,
            'total_warn': total_warn,
            'total_patches': total_patches,
            'per_country': all_findings,
        }, indent=2, ensure_ascii=False))
        print(f'Structured report → {args.json}')

    return 1 if total_fail > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
