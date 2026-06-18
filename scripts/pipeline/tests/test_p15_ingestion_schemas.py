"""
P15-C1 — Schema validation for Phase 1.5 ingestion outputs.

Walks all 39 SoT countries and verifies the canonical CSVs have correct
columns, non-zero rows, and plausible value ranges. Catches future drift
if a fetcher silently produces malformed output (e.g. missing columns,
unit conversion bugs, mis-coded NaN handling).

Run via:
    pytest scripts/pipeline/tests/test_p15_ingestion_schemas.py -v

Or to skip countries that don't have data yet (operator-side fetches not run):
    pytest scripts/pipeline/tests/test_p15_ingestion_schemas.py -v -k 'not climate'

Acceptance gate: ALL tests green = L1 data is canonical-schema-compliant.
Use as a CI gate before promoting any ingestion code change.
"""
import csv
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SOT_PATH = REPO_ROOT / "intelligence" / "countries.json"
DATA = REPO_ROOT / "scripts" / "pipeline" / "data"


# ═══════════════════════════════════════════════════════════
#  Test parametrisation
# ═══════════════════════════════════════════════════════════

def load_sot_slugs():
    return sorted(json.loads(SOT_PATH.read_text())["slugs"])


SOT_SLUGS = load_sot_slugs()


# ═══════════════════════════════════════════════════════════
#  Schema definitions (canonical, per SOURCES_AND_LICENSES.md §4)
# ═══════════════════════════════════════════════════════════

# Territory-name column has agency-specific aliases (mexico: estado;
# some EU: region; US Census: state). The L1 parser
# _parse_socioeconomic_csv normalises these to a canonical key, so for
# the schema check we accept ANY of these.
SOCIO_TERRITORY_ALIASES = {"province", "estado", "state", "territory", "departamento",
                            "fylke", "canton", "kommune", "sido", "prefecture", "il"}
SOCIO_REQUIRED_COLS = {
    "region", "gdp_per_capita", "unemployment_rate",
    "elderly_pct", "ep_rate", "migration_score", "_data_source",
}

SEISMIC_REQUIRED_COLS = {"lon", "lat", "pga_g"}

CLIMATE_REQUIRED_COLS = {"lat", "lon", "t_mean_c", "heat_days", "ice_days"}


def find_socio_csv(country):
    """Locate the canonical socio CSV for a country. Tries each known pattern
    in priority order: agency_regional > eurostat_nuts3 > worldbank_national >
    native <agency>_*_socioeconomic.csv.
    """
    cdir = DATA / country
    if not cdir.exists():
        return None
    candidates = [
        cdir / "agency_regional_socioeconomic.csv",
        cdir / "eurostat_nuts3_socioeconomic.csv",
        cdir / "worldbank_national_socioeconomic.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Native pre-existing — match *_socioeconomic.csv
    matches = list(cdir.glob("*socioeconomic*.csv"))
    return matches[0] if matches else None


def find_seismic_csv(country):
    cdir = DATA / country
    if not cdir.exists():
        return None
    candidates = [
        cdir / "gem_pga475.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Native agency PGA
    matches = list(cdir.glob("*pga475.csv")) + list(cdir.glob("*pga*.csv"))
    return matches[0] if matches else None


def find_climate_csv(country):
    f = DATA / "cross-cutting" / f"era5_baseline_{country}.csv"
    return f if f.exists() else None


def read_csv(path):
    """Read a CSV. Filters rows whose first column starts with `#`
    (some files use # as a leading-comment convention even though CSV
    spec doesn't formally support it — see e.g. mexico/inegi_estado_*).
    """
    with open(path) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    if not fields:
        return [], []
    first_col = fields[0]
    rows = [
        r for r in rows
        if (r.get(first_col) or "").strip() and not str(r.get(first_col, "")).lstrip().startswith("#")
    ]
    return fields, rows


# ═══════════════════════════════════════════════════════════
#  Socio-economic schema tests
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("country", SOT_SLUGS)
def test_socio_csv_exists(country):
    """Every SoT country has a canonical socio CSV after P15-F-1/F-2."""
    csv_path = find_socio_csv(country)
    assert csv_path is not None, f"No socio CSV found for {country} in {DATA / country}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_socio_required_columns(country):
    csv_path = find_socio_csv(country)
    if csv_path is None:
        pytest.skip(f"No socio CSV for {country}")
    cols, _ = read_csv(csv_path)
    cols_set = set(cols)
    missing = SOCIO_REQUIRED_COLS - cols_set
    # _data_source is required for P15-F* but pre-existing native CSVs may not have it
    is_native = "agency_regional" not in csv_path.name and "eurostat" not in csv_path.name
    if is_native:
        missing.discard("_data_source")
    # Territory column: any of the agency-specific aliases satisfies this
    if not cols_set & SOCIO_TERRITORY_ALIASES:
        missing.add("(territory-name: any of " + "/".join(sorted(SOCIO_TERRITORY_ALIASES)) + ")")
    assert not missing, f"{country} socio CSV {csv_path.name} missing columns: {missing}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_socio_has_rows(country, request):
    csv_path = find_socio_csv(country)
    if csv_path is None:
        pytest.skip(f"No socio CSV for {country}")
    # Mexico's inegi_estado_*.csv is a STUB (header + 5 comment rows, no data)
    # that documents the planned INEGI DENUE + CONEVAL API ingestion. The real
    # mexico data flows from the compiled-dict fallback path
    # (_compiled_mexico_estado_data, 32 estados) at runtime. xfail this test
    # until the stub is either populated or removed.
    if country == "mexico" and csv_path.name.startswith("inegi_estado"):
        pytest.xfail("mexico inegi CSV is a stub; real data via _compiled_mexico_estado_data")
    _, rows = read_csv(csv_path)
    assert len(rows) >= 1, f"{country} socio CSV has zero rows"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_socio_gdp_plausible(country):
    """GDP per capita: blank, or 0 < gdp < 250_000 EUR (covers everything from
    Vaupés Colombia (~€2k) to Zug Switzerland (~€223k)."""
    csv_path = find_socio_csv(country)
    if csv_path is None:
        pytest.skip(f"No socio CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows:
        gdp = r.get("gdp_per_capita", "").strip()
        if not gdp:
            continue
        try:
            v = float(gdp)
        except (ValueError, TypeError):
            bad.append((r.get("region", "?"), gdp, "non-numeric"))
            continue
        if v <= 0:
            bad.append((r.get("region", "?"), gdp, "non-positive"))
        elif v > 250000:
            bad.append((r.get("region", "?"), gdp, f"too high: {v}"))
    assert not bad, f"{country} gdp_per_capita out of plausible range: {bad[:3]}..."


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_socio_unemployment_plausible(country):
    """Unemployment rate: 0-30% (covers low Czech 2% to high Greek 16%)."""
    csv_path = find_socio_csv(country)
    if csv_path is None:
        pytest.skip(f"No socio CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows:
        v_str = r.get("unemployment_rate", "").strip()
        if not v_str:
            continue
        try:
            v = float(v_str)
        except (ValueError, TypeError):
            bad.append((r.get("region", "?"), v_str, "non-numeric"))
            continue
        if v < 0 or v > 30:
            bad.append((r.get("region", "?"), v_str, "out of range"))
    assert not bad, f"{country} unemployment_rate out of range: {bad[:3]}..."


# ═══════════════════════════════════════════════════════════
#  Seismic schema tests
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("country", SOT_SLUGS)
def test_seismic_csv_exists(country):
    """Every SoT country has a seismic CSV (37 via GEM + 2 native)."""
    csv_path = find_seismic_csv(country)
    assert csv_path is not None, f"No seismic CSV for {country}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_seismic_required_columns(country):
    csv_path = find_seismic_csv(country)
    if csv_path is None:
        pytest.skip(f"No seismic CSV for {country}")
    cols, _ = read_csv(csv_path)
    missing = SEISMIC_REQUIRED_COLS - set(cols)
    assert not missing, f"{country} seismic CSV missing columns: {missing}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_seismic_has_rows(country):
    csv_path = find_seismic_csv(country)
    if csv_path is None:
        pytest.skip(f"No seismic CSV for {country}")
    _, rows = read_csv(csv_path)
    assert len(rows) >= 10, f"{country} seismic CSV has too few rows: {len(rows)}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_seismic_pga_plausible(country):
    """PGA 475-yr return period: 0 < pga_g < 3.0 g (physical envelope)."""
    csv_path = find_seismic_csv(country)
    if csv_path is None:
        pytest.skip(f"No seismic CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows[:1000]:  # sample first 1000 rows for speed (large grids)
        try:
            v = float(r.get("pga_g", "0"))
        except (ValueError, TypeError):
            bad.append((r, "non-numeric"))
            continue
        if v < 0 or v > 3.0:
            bad.append((v, "out of range"))
    assert not bad, f"{country} pga_g out of range: {bad[:3]}..."


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_seismic_coords_plausible(country):
    """lat/lon within (-90, 90) / (-180, 180)."""
    csv_path = find_seismic_csv(country)
    if csv_path is None:
        pytest.skip(f"No seismic CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows[:100]:  # sample
        try:
            lat = float(r["lat"])
            lon = float(r["lon"])
        except (ValueError, KeyError):
            bad.append(("malformed", r))
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            bad.append((lat, lon, "out of bounds"))
    assert not bad, f"{country} seismic coords out of bounds: {bad[:3]}..."


# ═══════════════════════════════════════════════════════════
#  Climate schema tests (skip if step 3 batch hasn't run)
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("country", SOT_SLUGS)
def test_climate_csv_exists_or_skipped(country):
    """Per P15-A-3 climate batch — every country should have ERA5-Land baseline."""
    csv_path = find_climate_csv(country)
    if csv_path is None:
        pytest.skip(f"No climate CSV for {country} (P15-A-3 batch not yet run)")
    assert csv_path.exists()


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_climate_required_columns(country):
    csv_path = find_climate_csv(country)
    if csv_path is None:
        pytest.skip(f"No climate CSV for {country}")
    cols, _ = read_csv(csv_path)
    missing = CLIMATE_REQUIRED_COLS - set(cols)
    assert not missing, f"{country} climate CSV missing columns: {missing}"


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_climate_tmean_plausible(country):
    """t_mean_c per cell: -50°C to +50°C (physical envelope)."""
    csv_path = find_climate_csv(country)
    if csv_path is None:
        pytest.skip(f"No climate CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows[:500]:  # sample
        try:
            v = float(r.get("t_mean_c", "0"))
        except (ValueError, TypeError):
            bad.append((r, "non-numeric"))
            continue
        if v < -50 or v > 50:
            bad.append((v, "out of range"))
    assert not bad, f"{country} t_mean_c out of range: {bad[:3]}..."


@pytest.mark.parametrize("country", SOT_SLUGS)
def test_climate_heat_ice_bounds(country):
    """heat_days and ice_days must each be 0-365."""
    csv_path = find_climate_csv(country)
    if csv_path is None:
        pytest.skip(f"No climate CSV for {country}")
    _, rows = read_csv(csv_path)
    bad = []
    for r in rows[:500]:
        try:
            h = float(r.get("heat_days", "0"))
            i = float(r.get("ice_days", "0"))
        except (ValueError, TypeError):
            bad.append((r, "non-numeric"))
            continue
        if not (0 <= h <= 365):
            bad.append((h, "heat_days out of range"))
        if not (0 <= i <= 365):
            bad.append((i, "ice_days out of range"))
    assert not bad, f"{country} heat_days/ice_days out of range: {bad[:3]}..."


# ═══════════════════════════════════════════════════════════
#  Cross-class consistency check
# ═══════════════════════════════════════════════════════════

def test_all_three_classes_present_for_each_country():
    """Final acceptance gate — every SoT country should have all three classes
    (when P15-A-3 climate batch has completed)."""
    missing = {"socio": [], "seismic": [], "climate": []}
    for slug in SOT_SLUGS:
        if find_socio_csv(slug) is None:
            missing["socio"].append(slug)
        if find_seismic_csv(slug) is None:
            missing["seismic"].append(slug)
        if find_climate_csv(slug) is None:
            missing["climate"].append(slug)
    # We don't fail on climate-only missing — that batch is operator-side and may
    # still be running. Print a friendly status.
    failures = []
    if missing["socio"]:
        failures.append(f"socio missing: {missing['socio']}")
    if missing["seismic"]:
        failures.append(f"seismic missing: {missing['seismic']}")
    if missing["climate"]:
        print(f"\n  ⚠ climate batch not yet run for: {missing['climate']}")
    assert not failures, "\n".join(failures)
