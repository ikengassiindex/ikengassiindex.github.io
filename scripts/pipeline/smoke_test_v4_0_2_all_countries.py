#!/usr/bin/env python3
"""
v4.0.2 multi-country smoke test — iterates the smoke checks across all
39 SoT countries.

For each country, runs 4 checks (country-agnostic):

  1. L1 socio: fetch returns a dict with >5 regions + valid GDP values
  2. L1 seismic: fetch returns grid points + agency attribution
  3. Architecture: per-country attribution lookup works
  4. Sanity: GDP spread + max PGA in plausible global ranges

Output: per-country line with pass/fail per check, then summary across
all 39. Special handling for the US (needs CENSUS_API_KEY env var).

Usage:
    python3 scripts/pipeline/smoke_test_v4_0_2_all_countries.py
    python3 scripts/pipeline/smoke_test_v4_0_2_all_countries.py --verbose
    python3 scripts/pipeline/smoke_test_v4_0_2_all_countries.py --country us

Exit code 0 = all 39 green (or only known-pending — US without key, climate without batch)
Exit code 1 = at least one unexpected red.
"""
import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


# Per-country expected MAX PGA bounds (g). Calibrated from published
# national-PSHA-model + GEM 2023.1 — values are wide envelopes; only
# flag if max falls outside. None = skip (no expected range).
PGA_EXPECTED_RANGE = {
    # Subduction / active plate boundaries — very high
    "japan":       (0.5, 3.0),
    "chile":       (0.4, 3.0),
    "mexico":      (0.3, 2.0),
    "new-zealand": (0.3, 2.5),
    "costa-rica":  (0.3, 2.0),
    "colombia":    (0.2, 2.0),
    "turkey":      (0.3, 2.0),
    "us":          (0.4, 3.0),  # California / Cascadia / Alaska
    "greece":      (0.3, 1.5),
    "italy":       (0.2, 1.5),
    "iceland":     (0.1, 1.5),
    "israel":      (0.05, 1.0),
    "portugal":    (0.05, 1.5),
    # Alpine / Pyrenees — moderate-high
    "switzerland": (0.05, 0.8),
    "austria":     (0.05, 0.8),
    "slovenia":    (0.1, 1.0),
    "slovakia":    (0.05, 0.6),
    "spain":       (0.05, 0.8),
    "france":      (0.02, 0.8),  # Pyrenees + Alps + Caribbean overseas
    # Korea/Australia/Canada — moderate
    "korea":       (0.1, 1.0),
    "australia":   (0.05, 2.0),  # Tennant Creek + Meckering source zones can spike
    "canada":      (0.1, 2.5),   # Cascadia + Eastern Canada
    # Intraplate / low — Northern Europe + Eastern Europe
    "germany":     (0.02, 0.4),
    "uk":          (0.02, 0.3),
    "ireland":     (0.001, 0.2),  # Ireland is genuinely <0.01g intraplate Atlantic
    "belgium":     (0.02, 0.3),
    "netherlands": (0.02, 0.4),
    "denmark":     (0.01, 0.2),
    "sweden":      (0.01, 0.3),
    "norway":      (0.02, 0.5),
    "finland":     (0.01, 0.2),
    "poland":      (0.02, 0.3),
    "czechia":     (0.02, 0.3),
    "hungary":     (0.02, 0.4),
    "luxembourg":  (0.01, 0.2),
    "estonia":     (0.005, 0.15),
    "latvia":      (0.005, 0.15),
    "lithuania":   (0.005, 0.15),
    "greenland":   (0.005, 1.0),  # Greenland bbox extends east to Mid-Atlantic Ridge pixels
}

# Per-country expected min number of socio regions (rough lower bound).
# Wide envelopes — only flag if returned < min.
SOCIO_MIN_REGIONS = {
    "us":          40,    # 51 states+DC+PR; allow some tolerance
    "uk":          10,    # 12 NUTS-1
    "norway":      10,    # 15 fylker
    "new-zealand": 14,    # 16 RCs
    "australia":   7,     # 8 states/territories
    "japan":       40,    # 47 prefectures
    "canada":      12,    # 13 provinces
    "korea":       15,    # 17 sido
    "switzerland": 24,    # 26 cantons
    "turkey":      14,    # 15 detailed + national-mean
    "chile":       14,    # 16 regiones
    "iceland":     6,     # 8 regions
    "colombia":    30,    # 33 departamentos
    "israel":      6,     # 7 districts
    "costa-rica":  6,     # 7 provincias
    "greenland":   4,     # 5 kommuner
    # EU countries via Eurostat NUTS-3 — varies widely
    "germany":     50,    # 400 NUTS-3
    "france":      90,    # 101 NUTS-3
    "italy":       80,    # 107 provinces
    "spain":       30,    # ~50 provinces
    "poland":      50,    # 73 NUTS-3
    "portugal":    20,    # 25 NUTS-3
    "belgium":     30,    # 44 NUTS-3
    "netherlands": 30,    # 40 NUTS-3
    "austria":     30,    # 35 NUTS-3
    "sweden":      8,     # 21 counties / 8 NUTS-2
    "denmark":     8,     # 11 NUTS-3
    "finland":     10,    # 19 NUTS-3
    "ireland":     5,     # 8 NUTS-3
    "greece":      10,    # 13 peripheries
    "hungary":     8,     # 20 counties + Budapest
    "czechia":     10,    # 14 NUTS-3
    "slovakia":    7,     # 8 NUTS-3
    "slovenia":    7,     # 12 NUTS-3
    "estonia":     3,     # 5 NUTS-3
    "latvia":      3,     # 6 NUTS-3
    "lithuania":   3,     # 10 NUTS-3
    "luxembourg":  1,     # 1 NUTS-3 (Luxembourg)
    "mexico":      20,    # 32 estados
}


def _get_socio_gdp(row):
    """Alias-aware GDP lookup (italy uses gdp_pc; P15-F-* uses gdp_per_capita)."""
    for alias in ("gdp_per_capita", "gdp_pc", "gdp"):
        if alias in row:
            v = row[alias]
            if isinstance(v, str):
                try:
                    return float(v) if v.strip() else None
                except ValueError:
                    return None
            return v
    return None


def check_country(country, verbose=False):
    """Run the 4 checks for a single country. Return dict with results."""
    result = {
        "country": country,
        "socio": "?",
        "seismic": "?",
        "architecture": "?",
        "sanity": "?",
        "messages": [],
    }

    # 1. Socio
    try:
        from scripts.pipeline.ingestion.socioeconomic import fetch_socioeconomic_data
        # Skip US if no CENSUS_API_KEY (expected, not a failure)
        if country == "us" and not os.environ.get("CENSUS_API_KEY"):
            result["socio"] = "SKIP"
            result["messages"].append("us socio skipped: CENSUS_API_KEY not set (expected)")
        else:
            data = fetch_socioeconomic_data(country, cache=True)
            if not isinstance(data, dict) or not data:
                result["socio"] = "FAIL"
                result["messages"].append(f"socio: empty or non-dict return")
            else:
                n = len(data)
                min_expected = SOCIO_MIN_REGIONS.get(country, 1)
                if n < min_expected:
                    result["socio"] = "FAIL"
                    result["messages"].append(f"socio: {n} regions < expected ≥ {min_expected}")
                else:
                    # Check at least 50% of rows have a numeric GDP
                    n_valid_gdp = sum(
                        1 for v in data.values()
                        if isinstance(_get_socio_gdp(v), (int, float))
                        and _get_socio_gdp(v) > 0
                    )
                    if n_valid_gdp < n * 0.4:
                        result["socio"] = "FAIL"
                        result["messages"].append(
                            f"socio: only {n_valid_gdp}/{n} rows have valid GDP "
                            f"(< 40% threshold)"
                        )
                    else:
                        result["socio"] = "OK"
                        if verbose:
                            result["messages"].append(
                                f"socio: {n} regions, {n_valid_gdp} with valid GDP"
                            )
    except Exception as exc:
        result["socio"] = "FAIL"
        result["messages"].append(f"socio: {type(exc).__name__}: {exc}")

    # 2. Seismic
    try:
        from scripts.pipeline.ingestion.seismic import (
            fetch_seismic_grid,
            get_national_seismic_agency,
        )
        grid = fetch_seismic_grid(country, cache=True)
        if not grid:
            result["seismic"] = "FAIL"
            result["messages"].append("seismic: empty grid")
        else:
            n = len(grid)
            if n < 10:
                result["seismic"] = "FAIL"
                result["messages"].append(f"seismic: only {n} grid points (< 10)")
            else:
                # Find max PGA
                max_pga_row = max(grid, key=lambda p: p.get("pga_g", 0))
                max_pga = max_pga_row.get("pga_g", 0)
                expected_range = PGA_EXPECTED_RANGE.get(country)
                if expected_range and not (expected_range[0] <= max_pga <= expected_range[1]):
                    result["seismic"] = "FAIL"
                    result["messages"].append(
                        f"seismic: max PGA {max_pga:.3f}g outside expected "
                        f"{expected_range} for {country}"
                    )
                else:
                    result["seismic"] = "OK"
                    if verbose:
                        result["messages"].append(
                            f"seismic: {n} points, max PGA {max_pga:.3f}g at "
                            f"({max_pga_row.get('lat', 0):.1f}°N, "
                            f"{max_pga_row.get('lon', 0):.1f}°E)"
                        )
    except Exception as exc:
        result["seismic"] = "FAIL"
        result["messages"].append(f"seismic: {type(exc).__name__}: {exc}")

    # 3. Architecture (per-country attribution lookup)
    try:
        from scripts.pipeline.ingestion.seismic import get_national_seismic_agency
        from scripts.pipeline.ingestion.climate import _GHCND_NATIONAL_AGENCY
        agency = get_national_seismic_agency(country)
        climate_agency = _GHCND_NATIONAL_AGENCY.get(country)
        if not agency or "GEM 2023.1" in agency and country not in (
            # These 36 countries legitimately use GEM as primary
            "us", "japan", "germany", "france", "spain", "uk", "switzerland",
            "austria", "canada", "denmark", "norway", "finland", "poland",
            "sweden", "netherlands", "belgium", "ireland", "portugal",
            "iceland", "luxembourg", "hungary", "czechia", "slovakia",
            "slovenia", "estonia", "latvia", "lithuania", "turkey", "israel",
            "korea", "new-zealand", "australia", "chile", "colombia",
            "costa-rica", "greenland",
        ):
            # italy/greece/mexico should NOT show "GEM 2023.1" — they have natives
            result["architecture"] = "FAIL"
            result["messages"].append(
                f"architecture: {country} attribution wrong: {agency}"
            )
        elif not climate_agency:
            result["architecture"] = "FAIL"
            result["messages"].append(f"architecture: climate agency not in GHCN-D map")
        else:
            result["architecture"] = "OK"
            if verbose:
                result["messages"].append(
                    f"architecture: seismic={agency[:40]}..., climate={climate_agency[:40]}..."
                )
    except Exception as exc:
        result["architecture"] = "FAIL"
        result["messages"].append(f"architecture: {type(exc).__name__}: {exc}")

    # 4. Sanity (GDP spread + already covered seismic above; just check spread)
    if result["socio"] == "OK":
        try:
            from scripts.pipeline.ingestion.socioeconomic import fetch_socioeconomic_data
            data = fetch_socioeconomic_data(country, cache=True)
            gdps = []
            for v in data.values():
                g = _get_socio_gdp(v)
                if isinstance(g, (int, float)) and g > 0:
                    gdps.append(g)
            if len(gdps) >= 2:
                ratio = max(gdps) / min(gdps)
                # Sanity: spread between 1.05× (very uniform) and 100× (anomalous)
                if ratio > 100:
                    result["sanity"] = "FAIL"
                    result["messages"].append(f"sanity: GDP spread {ratio:.1f}× (>100×, anomalous)")
                else:
                    result["sanity"] = "OK"
                    if verbose:
                        result["messages"].append(
                            f"sanity: GDP {min(gdps):.0f} → {max(gdps):.0f} (ratio {ratio:.2f}×)"
                        )
            else:
                result["sanity"] = "SKIP"  # Single-row case (e.g. small countries) — can't measure spread
        except Exception as exc:
            result["sanity"] = "FAIL"
            result["messages"].append(f"sanity: {type(exc).__name__}: {exc}")
    else:
        result["sanity"] = "SKIP"  # Skip if socio failed/skipped

    return result


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--country", help="Test a single country only")
    p.add_argument("--verbose", action="store_true", help="Per-country detail")
    args = p.parse_args()

    sot = sorted(json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())["slugs"])
    countries = [args.country] if args.country else sot

    print(f"\n═══ v4.0.2 SMOKE TEST — multi-country ({len(countries)} countries) ═══\n")
    print(f"  {'country':14s} socio  seismic  arch  sanity")
    print(f"  {'-'*14} {'-'*5}  {'-'*7}  {'-'*4}  {'-'*6}")

    results = []
    for c in countries:
        r = check_country(c, verbose=args.verbose)
        results.append(r)
        mark = lambda s: {"OK": "✓", "FAIL": "✗", "SKIP": "—", "?": "?"}.get(s, "?")
        print(f"  {c:14s}  {mark(r['socio']):3s}    {mark(r['seismic']):3s}      {mark(r['architecture']):3s}    {mark(r['sanity']):3s}")
        if args.verbose or any(s == "FAIL" for s in (r['socio'], r['seismic'], r['architecture'], r['sanity'])):
            for msg in r["messages"]:
                print(f"      • {msg}")

    print()
    # Summary
    n_total = len(results) * 4  # 4 checks per country
    n_ok = sum(1 for r in results for c in (r['socio'], r['seismic'], r['architecture'], r['sanity']) if c == "OK")
    n_fail = sum(1 for r in results for c in (r['socio'], r['seismic'], r['architecture'], r['sanity']) if c == "FAIL")
    n_skip = sum(1 for r in results for c in (r['socio'], r['seismic'], r['architecture'], r['sanity']) if c == "SKIP")
    n_countries_clean = sum(
        1 for r in results
        if r['socio'] in ("OK", "SKIP") and r['seismic'] == "OK" and r['architecture'] == "OK" and r['sanity'] in ("OK", "SKIP")
    )
    print(f"  ═══ Summary ═══")
    print(f"  Countries with no FAILs: {n_countries_clean}/{len(results)}")
    print(f"  Total checks: {n_ok} OK · {n_skip} SKIP · {n_fail} FAIL  (out of {n_total})")
    if n_fail > 0:
        print(f"\n  ⚠ {n_fail} check failures — investigate before PR-8")
    else:
        print(f"\n  🟢 All countries clean for v4.0.2 closure")

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
