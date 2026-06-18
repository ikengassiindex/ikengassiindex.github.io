#!/usr/bin/env python3
"""
SSI Pipeline — Phase 1.5 Data Orchestrator (P15-D, 8 June 2026)

One CLI tool that fetches all three v4.0.2 ingestion data classes — seismic
PGA, ERA5 climate baseline, OECD socio-economic — for a country (or all 39
SoT countries) and writes them to the canonical pipeline data paths.

This is the operator-facing entry point for closing the F-L4-2-extended cohort
data gap (22 countries that currently fail validate_schema strict mode).

Usage:
    # Single country
    python3 scripts/pipeline/fetch_data.py --country korea
    python3 scripts/pipeline/fetch_data.py --country korea --skip-climate

    # All 36 countries missing data
    python3 scripts/pipeline/fetch_data.py --all-missing
    python3 scripts/pipeline/fetch_data.py --all-missing --dry-run

    # Just the 22 F-L4-2-extended cohort
    python3 scripts/pipeline/fetch_data.py --f-l4-2-cohort

    # Verify what's present without fetching
    python3 scripts/pipeline/fetch_data.py --verify --all-missing

Prerequisites (one-time operator setup):
    1. Climate (CDS):    pip install --user cdsapi
                         Register at https://cds.climate.copernicus.eu (free)
                         Either: export CDS_API_KEY=<key>
                         Or:     put url+key in ~/.cdsapirc

    2. Seismic (GEM):    Download GSHM 2018 PGA 475-yr CSV (~50 MB) from
                         https://www.globalquakemodel.org/products/data
                         Place at: scripts/pipeline/data/cross-cutting/gem_global_pga475.csv

    3. Socio (OECD):     No setup — uses public OECD.Stat REST API
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Make the pipeline package importable
sys.path.insert(0, str(REPO_ROOT))

# Country slug source-of-truth
SOT_PATH = REPO_ROOT / "intelligence" / "countries.json"

logger = logging.getLogger("ssi.fetch_data")


# ═══════════════════════════════════════════════════════════
#  Country cohorts
# ═══════════════════════════════════════════════════════════

# 22 countries that fail validate_schema strict mode after Phase 1 PR-7.
# Mitigating these closes the F-L4-2-extended cohort acceptance gate.
F_L4_2_EXTENDED_COHORT = [
    'australia', 'belgium', 'canada', 'chile', 'colombia', 'costa-rica',
    'czechia', 'estonia', 'hungary', 'iceland', 'ireland', 'israel',
    'latvia', 'lithuania', 'luxembourg', 'netherlands', 'new-zealand',
    'norway', 'portugal', 'slovakia', 'slovenia', 'us',
]


def _load_sot_slugs():
    sot = json.loads(SOT_PATH.read_text())
    return sorted(sot["slugs"])


# ═══════════════════════════════════════════════════════════
#  Per-class fetchers (thin wrappers around ingestion modules)
# ═══════════════════════════════════════════════════════════

def _fetch_climate(country, dry_run=False):
    """Fetch ERA5 baseline. Uses the existing climate.py path (CDS API)."""
    from scripts.pipeline.ingestion.climate import fetch_era5_baseline
    if dry_run:
        return ("dry-run", 0)
    grid = fetch_era5_baseline(country)
    if grid:
        return ("ok", len(grid))
    return ("failed", 0)


def _fetch_seismic(country, dry_run=False):
    """Fetch seismic PGA. Falls back to GEM global bbox-clip if needed."""
    from scripts.pipeline.ingestion.seismic import fetch_seismic_grid
    if dry_run:
        return ("dry-run", 0)
    grid = fetch_seismic_grid(country)
    if grid:
        return ("ok", len(grid))
    return ("failed", 0)


def _fetch_socio(country, dry_run=False):
    """Fetch socio-economic data. Falls back to OECD.Stat if no agency CSV."""
    from scripts.pipeline.ingestion.socioeconomic import fetch_socioeconomic_data
    if dry_run:
        return ("dry-run", 0)
    data = fetch_socioeconomic_data(country)
    if data:
        return ("ok", len(data))
    return ("failed", 0)


# ═══════════════════════════════════════════════════════════
#  Verify mode — report what's present without fetching
# ═══════════════════════════════════════════════════════════

def _verify_country(country):
    """Check which data classes are present per country.

    P15-A-6 fix (8 Jun 2026 evening): climate path was checking
    data/cross-cutting/era5_baseline_<c>.csv, but fetch_era5_baseline
    writes JSON to .cache/era5_baseline_<c>.json. The CSV is never
    written by the pipeline (only the JSON cache + raw NetCDFs). Verify
    now considers EITHER the committed CSV (if operator manually exports)
    OR the JSON cache as evidence that ERA5 baseline is on disk.
    """
    DATA = REPO_ROOT / "scripts" / "pipeline" / "data"
    CACHE = REPO_ROOT / "scripts" / "pipeline" / ".cache"

    # Climate — accept EITHER the committed CSV OR the JSON cache
    era5_csv = DATA / "cross-cutting" / f"era5_baseline_{country}.csv"
    era5_json = CACHE / f"era5_baseline_{country}.json"
    has_era5_csv = era5_csv.exists() and era5_csv.stat().st_size > 1024
    has_era5_json = era5_json.exists() and era5_json.stat().st_size > 1024
    has_era5 = has_era5_csv or has_era5_json

    # Seismic
    has_seismic = False
    if (DATA / country).exists():
        for f in (DATA / country).iterdir():
            if 'pga' in f.name.lower() and f.suffix == '.csv':
                has_seismic = True
                break
    # Socio
    has_socio = False
    if (DATA / country).exists():
        for f in (DATA / country).iterdir():
            if 'socio' in f.name.lower() and f.suffix == '.csv':
                has_socio = True
                break
    return {
        'country': country,
        'climate': has_era5,
        'climate_via': 'csv' if has_era5_csv else ('cache' if has_era5_json else 'none'),
        'seismic': has_seismic,
        'socioeconomic': has_socio,
        'complete': has_era5 and has_seismic and has_socio,
    }


def cmd_verify(countries):
    print(f"\n═══ Data inventory verify ({len(countries)} countries) ═══\n")
    print(f"  {'country':<14} climate  seismic  socio   complete")
    print(f"  {'-'*14} {'-'*7} {'-'*7} {'-'*7} {'-'*8}")
    complete = 0
    for c in countries:
        r = _verify_country(c)
        tick = lambda b: "  ✓  " if b else "  ✗  "
        print(f"  {c:<14}{tick(r['climate'])}{tick(r['seismic'])}{tick(r['socioeconomic'])}{tick(r['complete'])}")
        if r['complete']:
            complete += 1
    print(f"\n  Complete: {complete}/{len(countries)}")
    return 0 if complete == len(countries) else 1


# ═══════════════════════════════════════════════════════════
#  Fetch mode — actually pull the data
# ═══════════════════════════════════════════════════════════

def cmd_fetch(countries, skip=None, dry_run=False):
    """Iterate countries and run all three fetchers per country."""
    skip = skip or set()
    print(f"\n═══ Phase 1.5 data fetch ({len(countries)} countries, dry-run={dry_run}) ═══\n")
    results = []
    for c in countries:
        print(f"  {c}:")
        row = {'country': c}
        for cls, fn, label in [
            ('climate', _fetch_climate, 'ERA5 baseline'),
            ('seismic', _fetch_seismic, 'Seismic PGA'),
            ('socioeconomic', _fetch_socio, 'OECD socio'),
        ]:
            if cls in skip:
                print(f"    {label:<18} SKIPPED")
                row[cls] = 'skipped'
                continue
            try:
                status, count = fn(c, dry_run=dry_run)
                row[cls] = status
                if status == 'ok':
                    print(f"    {label:<18} ✓ ({count} records)")
                elif status == 'dry-run':
                    print(f"    {label:<18} (dry-run)")
                else:
                    print(f"    {label:<18} ✗ FAILED")
            except Exception as e:
                row[cls] = f'error: {e}'
                print(f"    {label:<18} ✗ ERROR: {e}")
        results.append(row)
        print()

    # Summary
    ok_per_class = {
        cls: sum(1 for r in results if r.get(cls) == 'ok')
        for cls in ('climate', 'seismic', 'socioeconomic')
    }
    print(f"═══ Summary ═══")
    for cls, n in ok_per_class.items():
        print(f"  {cls}: {n}/{len(results)} succeeded")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n')[2],  # 1-line summary
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See module docstring for prerequisites + setup."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--country", help="Single country slug")
    target.add_argument("--all-missing", action="store_true",
                        help="All countries with at least one missing data class")
    target.add_argument("--f-l4-2-cohort", action="store_true",
                        help="22 countries in the F-L4-2-extended cohort")
    target.add_argument("--all", action="store_true",
                        help="All 39 SoT countries (incl. those already complete)")

    parser.add_argument("--verify", action="store_true",
                        help="Just report data presence; don't fetch")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be fetched without calling APIs")

    parser.add_argument("--skip-climate", action="store_true")
    parser.add_argument("--skip-seismic", action="store_true")
    parser.add_argument("--skip-socio", action="store_true")
    parser.add_argument("--only-class", choices=["climate", "seismic", "socioeconomic"],
                        help="Run only the named data class; skip the other two. "
                             "When combined with --all-missing, also filters the "
                             "country list to those specifically missing that class.")

    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Resolve country list
    if args.country:
        countries = [args.country]
    elif args.f_l4_2_cohort:
        countries = F_L4_2_EXTENDED_COHORT
    elif args.all:
        countries = _load_sot_slugs()
    else:  # --all-missing
        all_slugs = _load_sot_slugs()
        if args.only_class:
            # Narrow filter: countries missing the specified class only.
            # This makes --all-missing --only-class climate scan just the
            # 28 countries without ERA5, not all 37 with any missing class.
            countries = [
                c for c in all_slugs
                if not _verify_country(c)[args.only_class]
            ]
            print(
                f"\n  Of {len(all_slugs)} SoT countries, "
                f"{len(countries)} are missing {args.only_class}."
            )
        else:
            countries = [c for c in all_slugs if not _verify_country(c)['complete']]
            print(f"\n  Of {len(all_slugs)} SoT countries, {len(countries)} have missing data.")

    skip = set()
    if args.skip_climate: skip.add('climate')
    if args.skip_seismic: skip.add('seismic')
    if args.skip_socio: skip.add('socioeconomic')
    # --only-class collapses to skip the other two
    if args.only_class:
        for cls in ('climate', 'seismic', 'socioeconomic'):
            if cls != args.only_class:
                skip.add(cls)

    if args.verify:
        return cmd_verify(countries)
    return cmd_fetch(countries, skip=skip, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
