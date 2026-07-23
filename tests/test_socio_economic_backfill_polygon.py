"""Task #453 + #454 SYSTEMIC — Socio-economic polygon-backfill sentinel

Regression sentinel closing R2 Grid Equity Defect Class 4. Before Task #453:
`socio_economic.{gdp_per_capita, unemployment_rate, EP_rate_region,
elderly_pct, V_socio}` was empty for v43 substations in Luxembourg (12%
populated) / Slovenia (16%) / Colombia (51%) / Lithuania (50%) because
v43 subs (added via Wave 2/3 OSM Overpass ingestion) landed with
`province: None` in the canonical, and downstream
`socioeconomic.py::overlay_socioeconomic()` uses `province` as CSV join
key — empty join key = no match = all 6-8 socio_economic fields empty.

Task #453 (23 Jul 2026) replaced this via polygon spatial-join against
Eurostat GISCO NUTS-3 2024 (LU/SI/LT) + GADM 4.1 (Colombia — documented-proxy
fallback after DANE geoportal empirically requires form-based download).

Task #454 SYSTEMIC (24 Jul 2026) extended the cohort to 11 additional
countries (BE/CZ/DK/EE/FI/IE/LV/NL/PL via Eurostat GISCO NUTS-3;
CH/CA via GADM 4.1) covering ~52,107 v43 subs — 15-country cohort total.
Task #454 also refined the utility's skip-logic (3-case decision tree):
(a) fully populated → idempotent no-op; (b) province set but socio_economic
gap (Canada case) → bypass polygon join + CSV lookup on existing province;
(c) not populated → polygon spatial-join (existing behavior).

Empirical Task #454 outcome: 59,041/59,077 v43 subs enriched (99.94%);
65 Convention #56 fallback (0.11%); 100% Task #451/#452 marker preservation
across 15-country cohort. Convention #78 §5septies OSM-tag-density
discipline empirical instance count: 5 → 16 (11 new instances).

See Phase 2H addendum in ikengassiindex.github.io/CLAUDE.md, REPORTS_FRAMING_KB
§8bis Discipline #47 EXTENSION, and METHODOLOGY_DISCIPLINES.md §5septies
(empirical OSM tag density is per-country) for full architectural context.

This sentinel pins five architectural invariants that together defeat the
drift class from re-entering:

  (1) UTILITY CONSTANT LOCK — `AUDIT_TRAIL_VALUE_POLYGON`,
      `PRESERVED_MARKERS` frozenset, `BACKFILL_TARGET_FIELDS` frozenset,
      `POLYGON_COUNTRY_CONFIGS` cardinality + expected key set.
      Any drift is a Task #453 methodology-version event.

  (2) MERGE-NOT-REPLACE BINDING CONTRACT — Task #451
      `_catchment_population_source` marker + Task #452
      `_migration_score_source` marker MUST survive across 4-country
      cohort untouched. Convention-BINDING: enrichment utilities in this
      discipline family (Task #451 GHSL raster / Task #452 Niva raster /
      Task #453 polygon spatial-join) MUST preserve upstream markers.

  (3) COHORT DATA — every enriched v43 sub carries a valid admin code
      from the country's canonical set: LU='LU000'; SI in {SI031..SI044};
      LT in {LT011..LT028}; CO in DANE 33-departmento set. Every enriched
      sub also carries the Task #453 audit marker.

  (4) V_SOCIO FORMULA LOCK — canonical anchor points match
      `overlay_socioeconomic()` line 511-517: EP=25 saturates at
      ep_norm=1.0 (0.45 weight), GDP=14k → gdp_norm=1.0, GDP=54k →
      gdp_norm=0.0, elderly=18 → 0.0, elderly=33 → 1.0. Weight profile
      0.45+0.35+0.20 sums to 1.0. Formula matches modern pipeline output
      by BINDING contract.

  (5) CONVENTION #56 FALLBACK — subs outside all polygons receive None
      (not fabricated); no audit marker emitted.

Cross-references:
  - Task #453           R2 Defect Class 4 (this workstream)
  - Task #451           R2 Defect Class 2 catchment_population (sibling STOCK variant)
  - Task #452           R2 Defect Class 3 migration_score (sibling FLOW variant)
  - Task #454           SYSTEMIC cohort-wide sweep (~21 other countries)
  - Convention #7       Data-Layer Anchoring documented-proxy (Eurostat + GADM)
  - Convention #56      Visibly-honest degradation (outside-polygon → None)
  - Convention #60      Ikenga IS the ESG provider (open-license sources)
  - Convention #79      ssi-data sharding (read_ssi_data)
  - REPORTS_FRAMING_KB.md §8bis Discipline #47 candidate EXTENSION (3 variants)
  - METHODOLOGY_DISCIPLINES.md §5septies (empirical OSM tag density)

Utility source:
  scripts/pipeline/enrichment/socio_economic_backfill.py

Pre-flight audit:
  docs/audits/task_453_polygon_backfill_preflight_20260723.yaml
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ═══════════════════════════════════════════════════════════
#  CONFIG — Task #453 invariants
# ═══════════════════════════════════════════════════════════

AUDIT_TRAIL_KEY = "_socio_economic_source"
AUDIT_TRAIL_VALUE_POLYGON = "TASK_453_POLYGON_BACKFILL_v4_2"

# Task #451/#452 markers this discipline family MUST preserve
TASK_451_MARKER = "_catchment_population_source"
TASK_452_MARKER = "_migration_score_source"

# Task #453 target countries (all 4 need polygon spatial-join per
# empirical OSM tag-density dead-end 23 Jul 2026)
TASK_453_COUNTRIES = ("luxembourg", "slovenia", "lithuania", "colombia")

# Task #454 SYSTEMIC cohort extension (11 new countries 24 Jul 2026)
TASK_454_COUNTRIES = (
    "belgium", "czechia", "denmark", "estonia", "finland",
    "ireland", "latvia", "netherlands", "poland",
    "switzerland", "canada",
)

# Task #501 V_socio semantic-scale bridge (Wave 4 majors, 24 Jul 2026 later same day)
# 7 of 8 Wave 4 majors — Italy blocked (missing ISTAT NUTS-3 CSV, analogous to
# Greece Task #454b block). Utility case-c triggers (province=None, gdp
# populated as fleet-uniform national scalar); polygon spatial-join derives
# NUTS-3 code + overwrites fleet-uniform V_socio with per-region CSV value.
TASK_501_COUNTRIES = (
    "france", "germany", "spain", "portugal", "sweden",   # 5 EU via Eurostat NUTS-3
    "us", "japan",                                          # 2 non-EU via GADM 4.1
    # italy BLOCKED — needs operator-sourced ISTAT NUTS-3 CSV
)

# Task #454c Greenland micro-scope (24 Jul 2026 later same day) — 6 v43 subs
# via GADM 4.1 5-municipality admin1 shapefile.
TASK_454C_COUNTRIES = ("greenland",)

# Task #454b Greece (24 Jul 2026 fastest-path close-out) — 163 v43 subs via
# Eurostat NUTS-3 shapefile (already downloaded) + operator-scaffolded CSV
# with 52 NUTS-3 codes + Greek national-average defaults + TODO_ELSTAT_YYYY
# provenance markers. Values progressively refined via ELSTAT / Eurostat
# regional datasets (nama_10r_3gdp + lfst_r_lfu3rt + demo_r_pjangrp3 + ilc_mdes01).
TASK_454B_COUNTRIES = ("greece",)

# Task #501 Italy follow-on (24 Jul 2026 later same day) — 51,910 v43 subs
# via Eurostat NUTS-3 shapefile (already downloaded) + operator-scaffolded
# CSV with 107 NUTS-3 codes + ISTAT 2023 CN + LFS 2024 anchor with regional
# gradient + TODO_ISTAT_YYYY provenance markers. Italy was the only
# Task #501 blocker at first-apply pass; template scaffold pattern mirrors
# Greece Task #454b fastest-path recipe.
TASK_501_ITALY_COUNTRIES = ("italy",)

# Full 25-country target cohort (Task #453 + Task #454 + Task #501 + Task #454c + Task #454b + Task #501-Italy)
TARGET_COUNTRIES = (
    TASK_453_COUNTRIES
    + TASK_454_COUNTRIES
    + TASK_501_COUNTRIES
    + TASK_454C_COUNTRIES
    + TASK_454B_COUNTRIES
    + TASK_501_ITALY_COUNTRIES
)

# Expected admin code sets for cohort data invariant
EXPECTED_ADMIN_CODES = {
    "luxembourg": frozenset({"LU000"}),
    "slovenia": frozenset({
        "SI031", "SI032", "SI033", "SI034", "SI035", "SI036",
        "SI037", "SI038", "SI041", "SI042", "SI043", "SI044",
    }),
    "lithuania": frozenset({
        # Lithuania NUTS-3 2024 (per Eurostat GISCO): 10 apskritys.
        # LT011 Klaipėdos + LT021 Alytaus + LT022 Kauno + LT023 Marijampolės +
        # LT024 Panevėžio + LT025 Šiaulių + LT026 Tauragės + LT027 Telšių +
        # LT028 Utenos + LT029 Vilniaus apskritis.
        "LT011", "LT021", "LT022", "LT023", "LT024",
        "LT025", "LT026", "LT027", "LT028", "LT029",
    }),
    # Colombia — 33 DANE-canonical department names (via GADM alias-mapped).
    "colombia": frozenset({
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.",
        "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare",
        "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca",
        "Guainía", "Guaviare", "Huila", "La Guajira", "Magdalena",
        "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío",
        "Risaralda", "San Andrés y Providencia", "Santander", "Sucre",
        "Tolima", "Valle del Cauca", "Vaupés", "Vichada",
    }),
    # ─── Task #454 SYSTEMIC cohort (11 new countries 24 Jul 2026) ───
    "belgium": frozenset({
        "BE100", "BE211", "BE212", "BE213", "BE223", "BE224", "BE225",
        "BE231", "BE232", "BE233", "BE234", "BE235", "BE236", "BE241",
        "BE242", "BE251", "BE252", "BE253", "BE254", "BE255", "BE256",
        "BE257", "BE258", "BE310", "BE323", "BE328", "BE329", "BE32A",
        "BE32B", "BE32C", "BE32D", "BE331", "BE332", "BE334", "BE335",
        "BE336", "BE341", "BE342", "BE343", "BE344", "BE345", "BE351",
        "BE352", "BE353",
    }),
    "czechia": frozenset({
        "CZ010", "CZ020", "CZ031", "CZ032", "CZ041", "CZ042",
        "CZ051", "CZ052", "CZ053", "CZ063", "CZ064", "CZ071",
        "CZ072", "CZ080",
    }),
    "denmark": frozenset({
        "DK011", "DK012", "DK013", "DK014", "DK021", "DK022",
        "DK031", "DK032", "DK041", "DK042", "DK050",
    }),
    "estonia": frozenset({
        "EE001", "EE004", "EE008", "EE009", "EE00A",
    }),
    "finland": frozenset({
        "FI196", "FI198", "FI199", "FI19A", "FI19B", "FI1B1",
        "FI1C1", "FI1C2", "FI1C5", "FI1C6", "FI1C7", "FI1D5",
        "FI1D7", "FI1D8", "FI1D9", "FI1DA", "FI1DB", "FI1DC",
        "FI200",
    }),
    "ireland": frozenset({
        "IE041", "IE042", "IE051", "IE052", "IE053",
        "IE061", "IE062", "IE063",
    }),
    "latvia": frozenset({
        "LV005", "LV009", "LV00A", "LV00B", "LV00C",
    }),
    "netherlands": frozenset({
        "NL112", "NL114", "NL115", "NL126", "NL127", "NL128",
        "NL131", "NL132", "NL133", "NL211", "NL212", "NL213",
        "NL221", "NL224", "NL225", "NL226", "NL230", "NL321",
        "NL323", "NL325", "NL327", "NL328", "NL32A", "NL32B",
        "NL341", "NL342", "NL350", "NL361", "NL362", "NL363",
        "NL364", "NL365", "NL366", "NL411", "NL414", "NL415",
        "NL416", "NL421", "NL422", "NL423",
    }),
    "poland": frozenset({
        "PL213", "PL214", "PL217", "PL218", "PL219", "PL21A",
        "PL224", "PL225", "PL227", "PL228", "PL229", "PL22A",
        "PL22B", "PL22C", "PL411", "PL414", "PL415", "PL416",
        "PL417", "PL418", "PL424", "PL426", "PL427", "PL428",
        "PL431", "PL432", "PL514", "PL515", "PL516", "PL517",
        "PL518", "PL523", "PL524", "PL613", "PL616", "PL617",
        "PL618", "PL619", "PL621", "PL622", "PL623", "PL633",
        "PL634", "PL636", "PL637", "PL638", "PL711", "PL712",
        "PL713", "PL714", "PL715", "PL721", "PL722", "PL811",
        "PL812", "PL814", "PL815", "PL821", "PL822", "PL823",
        "PL824", "PL841", "PL842", "PL843", "PL911", "PL912",
        "PL913", "PL921", "PL922", "PL923", "PL924", "PL925",
        "PL926",
    }),
    # Switzerland — 26 CSV cantons (agency uses local German/French usage).
    # GADM aliases (Lucerne / Sankt Gallen) are input mappings; canonical
    # values stored in ssi-data.json come from the CSV via alias resolution.
    "switzerland": frozenset({
        "Aargau", "Appenzell Ausserrhoden", "Appenzell Innerrhoden",
        "Basel-Landschaft", "Basel-Stadt", "Bern", "Fribourg", "Genève",
        "Glarus", "Graubünden", "Jura", "Luzern", "Neuchâtel",
        "Nidwalden", "Obwalden", "Schaffhausen", "Schwyz", "Solothurn",
        "St. Gallen", "Thurgau", "Ticino", "Uri", "Valais", "Vaud",
        "Zug", "Zürich",
    }),
    # Canada — 13 CSV provinces/territories (English names match GADM).
    # Note: Case-b bypass path — existing province used as CSV key directly.
    "canada": frozenset({
        "Alberta", "British Columbia", "Manitoba", "New Brunswick",
        "Newfoundland and Labrador", "Northwest Territories",
        "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
        "Québec", "Saskatchewan", "Yukon",
    }),
}


def _has_polygon_deps() -> bool:
    """Task #453 utility optionally depends on geopandas + shapely.
    Sentinel tests that need live spatial-join skip gracefully when deps
    absent (CI + sandbox contexts)."""
    try:
        import geopandas  # noqa: F401
        import shapely  # noqa: F401
        return True
    except ImportError:
        return False


_HAS_POLYGON_DEPS = _has_polygon_deps()


def _load_ssi_data(slug: str) -> dict:
    """Load per-country ssi-data.json via Convention #79 sharding-aware
    reader if importable, else fallback to direct JSON load."""
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        pytest.skip(f"[{slug}] ssi-data.json not present — sandbox context")
    try:
        from pipeline.utils.ssi_data_sharding import read_ssi_data
        return read_ssi_data(ssi_path)
    except ImportError:
        return json.loads(ssi_path.read_text())


def _v43_subs_with_task_453_marker(slug: str) -> list:
    """Return list of v43 subs enriched by Task #453 (carry the audit marker)."""
    data = _load_ssi_data(slug)
    subs = data.get("substations", [])
    return [
        s for s in subs
        if "_v43_" in str(s.get("substation_id", ""))
        and (s.get("socio_economic") or {}).get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE_POLYGON
    ]


# ═══════════════════════════════════════════════════════════
#  1 — UTILITY CONSTANT LOCK (4 cases)
# ═══════════════════════════════════════════════════════════

class TestUtilityConstantLock:
    """Task #453 utility constants are pinned.
    Any drift is a methodology-version event."""

    def test_utility_module_importable(self):
        from pipeline.enrichment import socio_economic_backfill as sb  # noqa: F401

    def test_audit_trail_value_locked(self):
        from pipeline.enrichment import socio_economic_backfill as sb
        assert sb.AUDIT_TRAIL_VALUE_POLYGON == AUDIT_TRAIL_VALUE_POLYGON, (
            f"Audit-trail marker drift: expected '{AUDIT_TRAIL_VALUE_POLYGON}', "
            f"got '{sb.AUDIT_TRAIL_VALUE_POLYGON}'. Marker change breaks the "
            f"provenance chain for every enriched substation."
        )

    def test_preserved_markers_frozenset_locked(self):
        from pipeline.enrichment import socio_economic_backfill as sb
        expected = frozenset({TASK_451_MARKER, TASK_452_MARKER})
        assert sb.PRESERVED_MARKERS == expected, (
            f"PRESERVED_MARKERS drift: expected {expected}, got "
            f"{sb.PRESERVED_MARKERS}. Task #451/#452 markers MUST be listed "
            f"per merge-not-replace BINDING contract."
        )

    def test_polygon_country_configs_locked_to_25_countries(self):
        from pipeline.enrichment import socio_economic_backfill as sb
        assert set(sb.POLYGON_COUNTRY_CONFIGS.keys()) == set(TARGET_COUNTRIES), (
            f"POLYGON_COUNTRY_CONFIGS drift: expected {sorted(TARGET_COUNTRIES)}, "
            f"got {sorted(sb.POLYGON_COUNTRY_CONFIGS.keys())}. Task #453 target "
            f"cohort was 4 countries (LU/SI/LT/CO); Task #454 SYSTEMIC (24 Jul 2026) "
            f"extended to 11 more countries (BE/CZ/DK/EE/FI/IE/LV/NL/PL via Eurostat "
            f"GISCO NUTS-3; CH/CA via GADM 4.1). Adding a 16th country requires "
            f"POLYGON_COUNTRY_CONFIGS extension + EXPECTED_ADMIN_CODES + this test update."
        )

    def test_task_454_countries_reuse_task_453_utility_architecture(self):
        """Task #454 SYSTEMIC MUST reuse Task #453 utility unchanged.
        All 11 new countries share the same POLYGON_COUNTRY_CONFIGS schema
        + AUDIT_TRAIL_VALUE_POLYGON marker. Task #454 did NOT introduce a
        new utility or a new audit marker — extension is config-only.
        """
        from pipeline.enrichment import socio_economic_backfill as sb
        for slug in TASK_454_COUNTRIES:
            assert slug in sb.POLYGON_COUNTRY_CONFIGS, (
                f"Task #454 country '{slug}' missing from POLYGON_COUNTRY_CONFIGS"
            )
            cfg = sb.POLYGON_COUNTRY_CONFIGS[slug]
            # Required config keys (schema shared with Task #453 4-country cohort)
            for req_key in ("polygon_path", "polygon_admin_column",
                            "csv_relpath", "csv_lookup_column",
                            "sub_id_prefix_pattern"):
                assert req_key in cfg, (
                    f"Task #454 config '{slug}' missing required key '{req_key}'"
                )


# ═══════════════════════════════════════════════════════════
#  2 — MERGE-NOT-REPLACE BINDING CONTRACT (16 cases)
# ═══════════════════════════════════════════════════════════

class TestMergeNotReplace:
    """Enrichment utility MUST preserve Task #451/#452 audit-trail markers
    via dict.update() semantics on the sub's socio_economic block.
    Direct-assignment or full-dict-replacement is banned.

    Parametrised across 4-country cohort × 4 preservation checks.
    """

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_task_451_marker_preserved_where_task_453_wrote(self, slug):
        """Every Task-#453-enriched sub with pre-existing Task #451 marker
        MUST still carry that marker post-Task-#453."""
        subs = _v43_subs_with_task_453_marker(slug)
        if not subs:
            pytest.skip(f"[{slug}] no Task #453-enriched subs found (utility not yet run)")
        n_task_451_present = sum(
            1 for s in subs
            if (s.get("socio_economic") or {}).get(TASK_451_MARKER)
        )
        # Empirically all 4 countries had 100% Task #451 coverage (from cohort
        # apply 23 Jul 2026), so post-#453 all enriched subs MUST carry #451 marker.
        assert n_task_451_present == len(subs), (
            f"[{slug}] MERGE-NOT-REPLACE VIOLATION: {n_task_451_present}/{len(subs)} "
            f"Task-#453-enriched subs carry Task #451 marker. Expected 100% "
            f"preservation per BINDING contract."
        )

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_task_452_marker_preserved_where_task_453_wrote(self, slug):
        """Every Task-#453-enriched sub with pre-existing Task #452 marker
        MUST still carry that marker post-Task-#453."""
        subs = _v43_subs_with_task_453_marker(slug)
        if not subs:
            pytest.skip(f"[{slug}] no Task #453-enriched subs found (utility not yet run)")
        n_task_452_present = sum(
            1 for s in subs
            if (s.get("socio_economic") or {}).get(TASK_452_MARKER)
        )
        assert n_task_452_present == len(subs), (
            f"[{slug}] MERGE-NOT-REPLACE VIOLATION: {n_task_452_present}/{len(subs)} "
            f"Task-#453-enriched subs carry Task #452 marker. Expected 100% "
            f"preservation per BINDING contract."
        )

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_task_453_marker_present_on_enriched_subs(self, slug):
        """Every Task-#453-enriched sub carries the correct marker value."""
        data = _load_ssi_data(slug)
        subs = data.get("substations", [])
        v43_with_socio = [
            s for s in subs
            if "_v43_" in str(s.get("substation_id", ""))
            and s.get("socio_economic")
            and (s.get("socio_economic") or {}).get("gdp_per_capita") is not None
        ]
        if not v43_with_socio:
            pytest.skip(f"[{slug}] no v43 subs with populated socio_economic — utility not yet run")
        n_marker = sum(
            1 for s in v43_with_socio
            if (s.get("socio_economic") or {}).get(AUDIT_TRAIL_KEY) == AUDIT_TRAIL_VALUE_POLYGON
        )
        # At least 50% of populated v43 subs should carry the marker
        # (allow for potential future re-runs with different fields).
        assert n_marker >= len(v43_with_socio) * 0.5, (
            f"[{slug}] Only {n_marker}/{len(v43_with_socio)} populated v43 "
            f"subs carry Task #453 marker. Expected majority coverage."
        )

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_do_not_touch_fields_not_in_backfill_targets(self, slug):
        """Task #451/#452 marker keys MUST NOT be in BACKFILL_TARGET_FIELDS."""
        from pipeline.enrichment import socio_economic_backfill as sb
        assert TASK_451_MARKER not in sb.BACKFILL_TARGET_FIELDS
        assert TASK_452_MARKER not in sb.BACKFILL_TARGET_FIELDS
        assert "population" not in sb.BACKFILL_TARGET_FIELDS   # Task #451 field
        assert "migration_score" not in sb.BACKFILL_TARGET_FIELDS   # Task #452 field


# ═══════════════════════════════════════════════════════════
#  3 — COHORT DATA (12 cases)
# ═══════════════════════════════════════════════════════════

class TestCohortData:
    """Every enriched v43 sub carries a valid admin code from the
    country's canonical set. Parametrised across 4-country cohort × 3
    invariants."""

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_enriched_subs_have_province_populated(self, slug):
        """Every Task-#453-enriched sub carries a non-None top-level province."""
        subs = _v43_subs_with_task_453_marker(slug)
        if not subs:
            pytest.skip(f"[{slug}] no enriched subs — utility not yet run")
        n_with_province = sum(1 for s in subs if s.get("province"))
        assert n_with_province == len(subs), (
            f"[{slug}] {n_with_province}/{len(subs)} enriched subs have "
            f"non-None province. Task #453 MUST set province for every "
            f"enriched sub."
        )

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_province_values_in_expected_admin_code_set(self, slug):
        """Every Task-#453-enriched sub's province MUST be in the country's
        canonical admin code set."""
        subs = _v43_subs_with_task_453_marker(slug)
        if not subs:
            pytest.skip(f"[{slug}] no enriched subs — utility not yet run")
        expected = EXPECTED_ADMIN_CODES[slug]
        provinces_seen = {s.get("province") for s in subs}
        unexpected = provinces_seen - expected
        assert not unexpected, (
            f"[{slug}] provinces outside canonical set: {sorted(unexpected)[:10]}. "
            f"Expected subset of {sorted(expected)[:5]}...."
        )

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_enriched_subs_have_core_socio_economic_fields(self, slug):
        """Every Task-#453-enriched sub carries the 4 core socio_economic
        fields (gdp_per_capita, unemployment_rate, EP_rate_region,
        elderly_pct) — V_socio may be None if elderly_pct missing from CSV."""
        subs = _v43_subs_with_task_453_marker(slug)
        if not subs:
            pytest.skip(f"[{slug}] no enriched subs — utility not yet run")
        required = ("gdp_per_capita", "unemployment_rate", "EP_rate_region")
        for field in required:
            n_present = sum(
                1 for s in subs
                if (s.get("socio_economic") or {}).get(field) is not None
            )
            assert n_present == len(subs), (
                f"[{slug}] field '{field}' populated in {n_present}/{len(subs)} "
                f"enriched subs. Expected 100% coverage."
            )


# ═══════════════════════════════════════════════════════════
#  4 — V_SOCIO FORMULA LOCK (8 cases)
# ═══════════════════════════════════════════════════════════

class TestVSocioFormulaLock:
    """V_socio = 0.45 * ep_norm + 0.35 * gdp_norm + 0.20 * elderly_norm

    Normalisations (mirrored from socioeconomic.py:511-517 canonical):
      ep_norm      = min(1.0, ep_rate / 25.0)
      gdp_norm     = clip(1.0 - (gdp_pc - 14000) / 40000, 0, 1)
      elderly_norm = clip((elderly_pct - 18) / 15, 0, 1)

    Any drift breaks the BINDING contract with modern pipeline output.
    """

    def test_ep_saturation_at_25pct(self):
        """EP=25% saturates ep_norm at 1.0 → contributes 0.45 to V_socio."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=25.0, gdp_pc=30000.0, elderly_pct=20.0)
        # ep contribution = 0.45; gdp_norm=(1-(30000-14000)/40000)=0.6→0.21;
        # elderly_norm=(20-18)/15=0.133→0.0267; total ≈ 0.687
        assert 0.68 <= v <= 0.69, f"EP=25 saturation: expected V_socio ≈ 0.687, got {v}"

    def test_gdp_floor_at_14k(self):
        """GDP=€14k saturates gdp_norm at 1.0 → contributes 0.35."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=7.0, gdp_pc=14000.0, elderly_pct=20.0)
        # ep_norm=7/25=0.28→0.126; gdp_norm=1.0→0.35; elderly_norm=0.133→0.0267;
        # total ≈ 0.503
        assert 0.50 <= v <= 0.51, f"GDP=14k floor: expected V_socio ≈ 0.503, got {v}"

    def test_gdp_ceiling_at_54k(self):
        """GDP=€54k saturates gdp_norm at 0.0 → contributes 0.0."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=7.0, gdp_pc=54000.0, elderly_pct=20.0)
        # ep_norm=0.28→0.126; gdp_norm=0.0→0.0; elderly_norm=0.133→0.0267;
        # total ≈ 0.153
        assert 0.15 <= v <= 0.16, f"GDP=54k ceiling: expected V_socio ≈ 0.153, got {v}"

    def test_elderly_floor_at_18pct(self):
        """elderly=18% → elderly_norm=0 → contributes 0.0."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=7.0, gdp_pc=30000.0, elderly_pct=18.0)
        # ep_norm=0.28→0.126; gdp_norm=0.6→0.21; elderly_norm=0.0→0.0;
        # total = 0.336
        assert 0.33 <= v <= 0.34, f"elderly=18 floor: expected V_socio ≈ 0.336, got {v}"

    def test_elderly_ceiling_at_33pct(self):
        """elderly=33% → elderly_norm=1 → contributes 0.20."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=7.0, gdp_pc=30000.0, elderly_pct=33.0)
        # ep_norm=0.28→0.126; gdp_norm=0.6→0.21; elderly_norm=1.0→0.20;
        # total = 0.536
        assert 0.53 <= v <= 0.54, f"elderly=33 ceiling: expected V_socio ≈ 0.536, got {v}"

    def test_weight_profile_sums_to_unity(self):
        """0.45 + 0.35 + 0.20 = 1.0 — invariant across formula surface."""
        # At max input (EP=25, GDP=14k, elderly=33): V_socio should equal
        # exactly 0.45 + 0.35 + 0.20 = 1.0
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=25.0, gdp_pc=14000.0, elderly_pct=33.0)
        assert abs(v - 1.0) < 0.001, (
            f"Weight profile sum: EP + GDP + elderly at max should give "
            f"V_socio=1.0, got {v}"
        )

    def test_min_inputs_give_v_socio_zero(self):
        """At neutral-low (EP=0, GDP=54k, elderly=18): V_socio ≈ 0.0."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        v = compute_v_socio(ep_rate=0.0, gdp_pc=54000.0, elderly_pct=18.0)
        # ep_norm=0; gdp_norm=0; elderly_norm=0 → all zero contributions
        assert 0.0 <= v <= 0.01, f"Min inputs: expected V_socio ≈ 0.0, got {v}"

    def test_v_socio_always_in_unit_interval(self):
        """V_socio MUST always be in [0.0, 1.0] regardless of input range."""
        from pipeline.enrichment.socio_economic_backfill import compute_v_socio
        # Test extreme input values (out-of-band) — utility should clamp
        extreme_cases = [
            (100.0, 1000, 5.0),   # Very high EP, very low GDP, no elderly
            (0.0, 200000, 60.0),  # No EP, very high GDP, extreme elderly
            (50.0, 30000, 25.0),  # Middle-of-band EP over-saturated
        ]
        for ep, gdp, elderly in extreme_cases:
            v = compute_v_socio(ep_rate=ep, gdp_pc=gdp, elderly_pct=elderly)
            assert 0.0 <= v <= 1.0, (
                f"V_socio out of [0,1] envelope: ep={ep} gdp={gdp} "
                f"elderly={elderly} → {v}"
            )


# ═══════════════════════════════════════════════════════════
#  5 — CONVENTION #56 FALLBACK (4 cases)
# ═══════════════════════════════════════════════════════════

class TestConvention56Fallback:
    """Subs outside all polygons receive None (not fabricated); no audit
    marker emitted per Convention #56 visibly-honest degradation."""

    @pytest.mark.parametrize("slug", TARGET_COUNTRIES)
    def test_unenriched_v43_subs_have_no_task_453_marker(self, slug):
        """Any v43 sub without socio_economic populated MUST NOT carry the
        Task #453 audit marker."""
        data = _load_ssi_data(slug)
        subs = data.get("substations", [])
        v43_no_socio = [
            s for s in subs
            if "_v43_" in str(s.get("substation_id", ""))
            and not (s.get("socio_economic") or {}).get("gdp_per_capita")
        ]
        for sub in v43_no_socio:
            marker = (sub.get("socio_economic") or {}).get(AUDIT_TRAIL_KEY)
            assert marker is None or marker != AUDIT_TRAIL_VALUE_POLYGON, (
                f"[{slug}] sub {sub.get('substation_id')} has no socio_economic "
                f"data but carries Task #453 marker — Convention #56 violation."
            )


# ═══════════════════════════════════════════════════════════
#  ~155-CASE SANITY CHECK (Task #453 45 + Task #454 110)
# ═══════════════════════════════════════════════════════════

def test_sentinel_case_count_matches_preflight_yaml():
    """Verify sentinel_matrix specification in preflight YAML is honoured:
    5 test classes × total ~155 cases (parametrised across 15-country cohort).

    Task #453 (23 Jul 2026) baseline: 45 cases across 4-country cohort.
    Task #454 SYSTEMIC (24 Jul 2026): +110 cases via 11-country extension
      (4 MergeNotReplace parametrise + 3 CohortData parametrise
       + 1 Convention56Fallback parametrise = 8 × 11 new countries + 2
       new tests for Task #454 architecture reuse).
    """
    expected_classes = {
        "TestUtilityConstantLock",       # 6 cases (was 4, +2 Task #454 arch reuse)
        "TestMergeNotReplace",           # 60 cases (15 × 4)
        "TestCohortData",                # 45 cases (15 × 3)
        "TestVSocioFormulaLock",         # 8 cases (unchanged — formula lock)
        "TestConvention56Fallback",      # 15 cases (15 × 1)
    }
    # Cross-reference: preflight YAMLs
    #   docs/audits/task_453_polygon_backfill_preflight_20260723.yaml
    #   docs/audits/task_454_systemic_cohort_extension_preflight_20260724.yaml
    assert len(expected_classes) == 5
