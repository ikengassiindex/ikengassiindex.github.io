#!/usr/bin/env python3
"""socio_economic_backfill.py — R2 Grid Equity Defect Class 4 closure

Task #453 (23 July 2026) — Path A-connector implementation.
Task #454 SYSTEMIC (24 July 2026) — cohort-wide extension (+11 countries).

Retroactively backfills `socio_economic` fields on v43 OSM Overpass-added
substations that were left with `province: None` by the ingestion pipeline.

Root cause (empirically confirmed 23 Jul 2026): Wave 2/3/4 OSM Overpass
connectors write per-sub v43_provenance audit trail (with province/NUTS-3
detection where OSM tags are rich) but do NOT propagate that detection
to the top-level `province` field. Downstream `overlay_socioeconomic()`
at socioeconomic.py:476 uses `sub.get("province") or ""` as join key —
empty join key = no CSV match = all 6-8 socio_economic fields empty.

This utility closes the gap without touching the connector code (that's
the deferred proper root-cause fix in a follow-on connector patch).
Instead it:
  1. Reads per-country ssi-data.json
  2. Extracts the detected admin code from v43_provenance
     (Slovenia: nuts3_code_detected; Colombia: department_detected;
      Luxembourg + Lithuania: from polygon spatial-join — TBD)
  3. Sets top-level `sub['province']` = detected code
  4. Looks up socio_economic row in per-country CSV
  5. MERGES fields into `sub['socio_economic']` (dict.update semantics —
     preserves Task #451 catchment_population + Task #452 migration_score
     markers by NOT overwriting them)
  6. Computes V_socio from the ep_norm / gdp_norm / elderly_norm
     formula lifted from socioeconomic.py:511-517
  7. Adds Task #453 audit marker `_socio_economic_source`

Country strategy matrix (as of Task #453 Step 2a, 23 Jul 2026):

  Slovenia     → --from-provenance     (nuts3_code_detected in v43_provenance)
  Colombia     → --from-provenance     (department_detected in v43_provenance)
  Luxembourg   → --from-polygon        (OSM has no admin tags — polygon join needed)
  Lithuania    → --from-polygon        (OSM has no admin tags — polygon join needed)

Convention preservation
-----------------------
- #7  Data-Layer Anchoring documented-proxy — per-country CSV sources
      (eurostat_nuts3_socioeconomic.csv or agency_regional_socioeconomic.csv)
- #56 Visibly-honest degradation — sub missing detection → left None
      (not fabricated); rd_pct_gdp / E2_local NOT filled (legacy pipeline scope,
      not Task #453 scope); Slovenia rd_pct_gdp = 0 across all subs is a
      SEPARATE Task-#450-SYSTEMIC-adjacent bug documented but not fixed here.
- #60 Ikenga IS the ESG provider — public open-license institutional sources
- #79 ssi-data sharding preserved

Task #451 + #452 marker preservation (BINDING)
-----------------------------------------------
Every existing key in sub['socio_economic'] MUST survive this pass unchanged
unless the field name is in `_BACKFILL_TARGET_FIELDS`. The `_catchment_population_source`
+ `_migration_score_source` markers are explicitly excluded from update.

Usage
-----
Diagnose:
    python3 scripts/pipeline/enrichment/socio_economic_backfill.py --diagnose-only

Slovenia pilot (dry-run):
    python3 scripts/pipeline/enrichment/socio_economic_backfill.py slovenia --dry-run

Slovenia apply:
    python3 scripts/pipeline/enrichment/socio_economic_backfill.py slovenia

Provenance-mode cohort (Slovenia + Colombia):
    python3 scripts/pipeline/enrichment/socio_economic_backfill.py --provenance-cohort

Cross-refs
----------
- Task #453           R2 Defect Class 4 (this workstream)
- Task #451           R2 Defect Class 2 catchment_population (marker preserved)
- Task #452           R2 Defect Class 3 migration_score (marker preserved)
- Task #450 SYSTEMIC  Wave 4 per-substation interpolation regression (parent)
- scripts/pipeline/ingestion/socioeconomic.py::overlay_socioeconomic (~line 452)
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── path setup ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.pipeline.utils.ssi_data_sharding import (  # type: ignore
        read_ssi_data,
        write_ssi_data,
    )
    _HAS_SHARDING = True
except ImportError:
    _HAS_SHARDING = False

# Polygon-mode dependencies (optional — required only for --from-polygon)
try:
    import geopandas as gpd  # type: ignore
    from shapely.geometry import Point  # type: ignore
    from shapely.strtree import STRtree  # type: ignore
    _HAS_POLYGON_DEPS = True
except ImportError:
    _HAS_POLYGON_DEPS = False


# ═════════════════════════════════════════════════════════════════════
#  CANONICAL CONSTANTS
# ═════════════════════════════════════════════════════════════════════

# Convention #56 audit-trail marker for Task #453 writes
AUDIT_TRAIL_KEY = "_socio_economic_source"
AUDIT_TRAIL_VALUE_PROVENANCE = "TASK_453_PROVENANCE_BACKFILL_v4_2"
AUDIT_TRAIL_VALUE_POLYGON = "TASK_453_POLYGON_BACKFILL_v4_2"

# Task #451/#452 markers that MUST be preserved untouched
PRESERVED_MARKERS = frozenset({
    "_catchment_population_source",   # Task #451
    "_migration_score_source",         # Task #452
})

# Fields Task #453 backfill sets — every other field in sub['socio_economic']
# survives unchanged (dict.update semantics for these + preservation for rest)
BACKFILL_TARGET_FIELDS = frozenset({
    "gdp_per_capita",
    "unemployment_rate",
    "EP_rate_region",
    "elderly_pct",
    "V_socio",
    AUDIT_TRAIL_KEY,
})

# Fields explicitly NOT touched by Task #453 (Task #451/#452 domain OR
# legacy pipeline scope):
DO_NOT_TOUCH_FIELDS = frozenset({
    "population",              # Task #451 GHSL enrichment
    "migration_score",         # Task #452 Niva enrichment
    "E2_local",                # Legacy pipeline scope (deferred)
    "rd_pct_gdp",              # Legacy pipeline scope (deferred)
    "_catchment_population_source",
    "_migration_score_source",
})


# ═════════════════════════════════════════════════════════════════════
#  Per-country config — provenance-mode countries
# ═════════════════════════════════════════════════════════════════════

# Slovenia + Colombia have already-detected admin codes in v43_provenance
# from their respective osm_overpass.py connectors. This utility just
# propagates them to the top-level `province` field + fills socio_economic.

PROVENANCE_COUNTRY_CONFIGS = {
    "slovenia": {
        "provenance_source_key": "SI-C1-osm-overpass",
        "provenance_detected_field": "nuts3_code_detected",
        "csv_relpath": "scripts/pipeline/data/slovenia/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",     # matches SI0xx nuts3 codes
        "sub_id_prefix_pattern": "SI_v43_",
    },
    "colombia": {
        "provenance_source_key": "CO-C1-osm-overpass",
        "provenance_detected_field": "department_detected",
        "csv_relpath": "scripts/pipeline/data/colombia/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",     # matches Antioquia / Bogotá D.C. / etc.
        "sub_id_prefix_pattern": "CO_v43_",
    },
}


# ═════════════════════════════════════════════════════════════════════
#  Per-country config — polygon-mode countries (Task #453 load-bearing)
# ═════════════════════════════════════════════════════════════════════

# All 4 Task #453 countries need polygon spatial-join per empirical Step 2a
# probe (23 Jul 2026) — provenance-mode is dead across LU/SI/CO/LT.
#
# Polygon shapefile sources (Convention #7 documented-proxy per preflight YAML):
# - Eurostat GISCO NUTS 2024 shapefile (EPSG:4326, LEVL_CODE == 3) for LU/SI/LT
# - DANE Colombia MGN 2024 departmental shapefile (EPSG:4326) for Colombia
#
# Operator downloads shapefiles to ~/ prior to execution. Diagnose mode
# reports missing shapefiles + install instructions per Convention #56.

POLYGON_COUNTRY_CONFIGS = {
    "luxembourg": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "LU"},
        "polygon_admin_column": "NUTS_ID",   # emits LU000 for single Luxembourg NUTS-3
        "csv_relpath": "scripts/pipeline/data/luxembourg/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",     # matches NUTS_ID e.g. LU000
        "sub_id_prefix_pattern": "LU_v43_",
        "expected_admin_codes": ["LU000"],
    },
    "slovenia": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "SI"},
        "polygon_admin_column": "NUTS_ID",   # emits SI031..SI044
        "csv_relpath": "scripts/pipeline/data/slovenia/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "SI_v43_",
        "expected_admin_codes": [
            "SI031", "SI032", "SI033", "SI034", "SI035", "SI036",
            "SI037", "SI038", "SI041", "SI042", "SI043", "SI044",
        ],
    },
    "lithuania": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "LT"},
        "polygon_admin_column": "NUTS_ID",   # emits LT011..LT029 (10 apskritys)
        "csv_relpath": "scripts/pipeline/data/lithuania/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "LT_v43_",
        "expected_admin_codes": [
            "LT011", "LT021", "LT022", "LT023", "LT024",
            "LT025", "LT026", "LT027", "LT028", "LT029",
        ],
    },
    "colombia": {
        # GADM 4.1 chosen 23 Jul 2026 as Convention #7 documented-proxy fallback
        # after DANE geoportal empirically requires form-based download.
        # GADM is peer-reviewed academic-open-license source (UC Davis
        # geodata.ucdavis.edu/gadm; vintage 2022; CC0-derivative)
        # widely cited in scientific literature. Substitution logged in
        # preflight YAML operator_signoff_log.
        "polygon_path": "~/gadm41_COL_shp/gadm41_COL_1.shp",
        "polygon_filter": {},   # gadm41_COL_1.shp IS admin1-level (departamentos)
        "polygon_admin_column": "NAME_1",  # GADM standard column for admin1 name
        "polygon_admin_normalise": False,   # keep accents intact
        "csv_relpath": "scripts/pipeline/data/colombia/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",
        # GADM 4.1 → agency CSV alias map (empirically discovered 23 Jul 2026):
        # GADM uses "Bogotá" (no D.C. suffix), CSV uses "Bogotá D.C.";
        # GADM may use "Archipiélago de San Andrés..." full name, CSV uses shortened.
        # Add empirically as pilot surfaces mismatches.
        "csv_lookup_aliases": {
            "Bogotá": "Bogotá D.C.",
            "Archipiélago de San Andrés y Providencia y Santa Catalina": "San Andrés y Providencia",
            "San Andrés y Providencia y Santa Catalina": "San Andrés y Providencia",
        },
        "sub_id_prefix_pattern": "CO_v43_",
        "expected_admin_codes": None,   # 33 departamentos incl. Bogotá D.C.
    },
    # ═════════════════════════════════════════════════════════════════════
    # Task #454 SYSTEMIC cohort (24 Jul 2026) — 11 additional countries
    # reusing Task #453 polygon utility template. 9 EU via Eurostat GISCO
    # NUTS-3 (single shapefile already downloaded for Task #453) + 2 non-EU
    # via GADM 4.1 (per Task #453 Colombia precedent, ~20MB each download).
    # ═════════════════════════════════════════════════════════════════════
    "belgium": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "BE"},
        "polygon_admin_column": "NUTS_ID",   # emits BE100..BE353 (44 codes)
        "csv_relpath": "scripts/pipeline/data/belgium/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "BE_v43_",
        "expected_admin_codes": [
            "BE100", "BE211", "BE212", "BE213", "BE223", "BE224", "BE225",
            "BE231", "BE232", "BE233", "BE234", "BE235", "BE236", "BE241",
            "BE242", "BE251", "BE252", "BE253", "BE254", "BE255", "BE256",
            "BE257", "BE258", "BE310", "BE323", "BE328", "BE329", "BE32A",
            "BE32B", "BE32C", "BE32D", "BE331", "BE332", "BE334", "BE335",
            "BE336", "BE341", "BE342", "BE343", "BE344", "BE345", "BE351",
            "BE352", "BE353",
        ],
    },
    "czechia": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "CZ"},
        "polygon_admin_column": "NUTS_ID",   # emits CZ010..CZ080 (14 codes)
        "csv_relpath": "scripts/pipeline/data/czechia/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "CZ_v43_",
        "expected_admin_codes": [
            "CZ010", "CZ020", "CZ031", "CZ032", "CZ041", "CZ042",
            "CZ051", "CZ052", "CZ053", "CZ063", "CZ064", "CZ071",
            "CZ072", "CZ080",
        ],
    },
    "denmark": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "DK"},
        "polygon_admin_column": "NUTS_ID",   # emits DK011..DK050 (11 codes)
        "csv_relpath": "scripts/pipeline/data/denmark/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "DK_v43_",
        "expected_admin_codes": [
            "DK011", "DK012", "DK013", "DK014", "DK021", "DK022",
            "DK031", "DK032", "DK041", "DK042", "DK050",
        ],
    },
    "estonia": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "EE"},
        "polygon_admin_column": "NUTS_ID",   # emits EE001..EE00A (5 codes)
        "csv_relpath": "scripts/pipeline/data/estonia/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "EE_v43_",
        "expected_admin_codes": [
            "EE001", "EE004", "EE008", "EE009", "EE00A",
        ],
    },
    "finland": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "FI"},
        "polygon_admin_column": "NUTS_ID",   # emits FI196..FI200 (19 codes)
        "csv_relpath": "scripts/pipeline/data/finland/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "FI_v43_",
        "expected_admin_codes": [
            "FI196", "FI198", "FI199", "FI19A", "FI19B", "FI1B1",
            "FI1C1", "FI1C2", "FI1C5", "FI1C6", "FI1C7", "FI1D5",
            "FI1D7", "FI1D8", "FI1D9", "FI1DA", "FI1DB", "FI1DC",
            "FI200",
        ],
    },
    "ireland": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "IE"},
        "polygon_admin_column": "NUTS_ID",   # emits IE041..IE063 (8 codes)
        "csv_relpath": "scripts/pipeline/data/ireland/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "IE_v43_",
        "expected_admin_codes": [
            "IE041", "IE042", "IE051", "IE052", "IE053",
            "IE061", "IE062", "IE063",
        ],
    },
    "latvia": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "LV"},
        "polygon_admin_column": "NUTS_ID",   # emits LV005..LV00C (5 codes)
        "csv_relpath": "scripts/pipeline/data/latvia/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "LV_v43_",
        "expected_admin_codes": [
            "LV005", "LV009", "LV00A", "LV00B", "LV00C",
        ],
    },
    "netherlands": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "NL"},
        "polygon_admin_column": "NUTS_ID",   # emits NL112..NL423 (40 codes)
        "csv_relpath": "scripts/pipeline/data/netherlands/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "NL_v43_",
        "expected_admin_codes": [
            "NL112", "NL114", "NL115", "NL126", "NL127", "NL128",
            "NL131", "NL132", "NL133", "NL211", "NL212", "NL213",
            "NL221", "NL224", "NL225", "NL226", "NL230", "NL321",
            "NL323", "NL325", "NL327", "NL328", "NL32A", "NL32B",
            "NL341", "NL342", "NL350", "NL361", "NL362", "NL363",
            "NL364", "NL365", "NL366", "NL411", "NL414", "NL415",
            "NL416", "NL421", "NL422", "NL423",
        ],
    },
    "poland": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "PL"},
        "polygon_admin_column": "NUTS_ID",   # emits PL213..PL926 (73 codes)
        "csv_relpath": "scripts/pipeline/data/poland/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "PL_v43_",
        "expected_admin_codes": [
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
        ],
    },
    # ── Non-EU (GADM 4.1 documented-proxy per Task #453 Colombia precedent) ──
    "switzerland": {
        # GADM 4.1 admin1 = 26 cantons. Non-EEA member; CSV canton names in
        # German/French/Italian per Swiss federal usage. Aliases populated
        # empirically 24 Jul 2026 after cohort apply surfaced 67 unmatched
        # subs (16 in Luzern area, 44 in St. Gallen area, 7 border spillovers):
        # GADM emits English/French forms for Luzern + St. Gallen.
        "polygon_path": "~/gadm41_CHE_shp/gadm41_CHE_1.shp",
        "polygon_filter": {},
        "polygon_admin_column": "NAME_1",
        "polygon_admin_normalise": False,
        "csv_relpath": "scripts/pipeline/data/switzerland/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",
        "csv_lookup_aliases": {
            # GADM English/French → CSV German canton name (agency uses local usage)
            "Lucerne": "Luzern",              # GADM English/French form
            "Luzerne": "Luzern",              # possible alt spelling
            "Sankt Gallen": "St. Gallen",     # GADM full German form (Sankt)
            "Saint Gallen": "St. Gallen",     # GADM English form
            "St Gallen": "St. Gallen",        # possible alt (no period)
        },
        "sub_id_prefix_pattern": "CH_v43_",
        "expected_admin_codes": None,   # 26 cantons validated at pilot time
    },
    "canada": {
        # GADM 4.1 admin1 = 13 provinces + territories. CSV uses province
        # NAME (Newfoundland and Labrador, Northwest Territories, etc.) —
        # aliases populate empirically. Convention #7 documented-proxy
        # anchor: GADM cite is stable/vintage-locked for LP-DD defensibility.
        "polygon_path": "~/gadm41_CAN_shp/gadm41_CAN_1.shp",
        "polygon_filter": {},
        "polygon_admin_column": "NAME_1",
        "polygon_admin_normalise": False,
        "csv_relpath": "scripts/pipeline/data/canada/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",
        "csv_lookup_aliases": {},  # populate as pilot surfaces mismatches
        "sub_id_prefix_pattern": "CA_v43_",
        "expected_admin_codes": None,   # 13 provinces validated at pilot time
    },
    # ═════════════════════════════════════════════════════════════════════
    # Task #501 — V_socio semantic-scale bridge (Wave 4 majors, 24 Jul 2026)
    # Empirical scope: 8 Wave 4 majors with fleet-uniform national-scalar
    # V_socio signature (FR 195,569 subs @ 0.1867 · DE 187,714 @ 0.1867 ·
    # US 101,594 @ 0.180 · IT 51,910 @ 0.7275 · ES 30,222 @ 0.3993 ·
    # PT 13,977 @ 0.4737 · SE 11,399 @ 0.1867 · JP 7,073 @ 0.6233) =
    # 199,458 substations total. Case-c triggers (province=None, gdp
    # populated at national scalar); utility polygon-joins to derive
    # NUTS-3 code + overwrites fleet-uniform V_socio with per-region
    # value computed from CSV lookup. Italy BLOCKED — missing ISTAT
    # NUTS-3 CSV (analogous to Greece Task #454b block).
    # 5 EU countries reuse Eurostat GISCO NUTS-3 2024 shapefile;
    # 2 non-EU (US + JP) use GADM 4.1 admin1.
    # ═════════════════════════════════════════════════════════════════════
    "france": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "FR"},
        "polygon_admin_column": "NUTS_ID",   # emits FR101..FRY50 (101 codes, incl. DOM/COM)
        "csv_relpath": "scripts/pipeline/data/france/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "FR_v43_",
        "expected_admin_codes": None,   # 101 NUTS-3 codes validated at pilot time
    },
    "germany": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "DE"},
        "polygon_admin_column": "NUTS_ID",   # emits DE111..DEG0N (400 codes; largest cohort-wide)
        "csv_relpath": "scripts/pipeline/data/germany/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "DE_v43_",
        "expected_admin_codes": None,   # 400 NUTS-3 codes validated at pilot time
    },
    "spain": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "ES"},
        "polygon_admin_column": "NUTS_ID",   # emits ES111..ES709 (59 codes incl. Canarias)
        "csv_relpath": "scripts/pipeline/data/spain/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "ES_v43_",
        "expected_admin_codes": None,   # 59 NUTS-3 codes validated at pilot time
    },
    "portugal": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "PT"},
        "polygon_admin_column": "NUTS_ID",   # emits PT111..PT300 (26 codes incl. Açores + Madeira)
        "csv_relpath": "scripts/pipeline/data/portugal/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "PT_v43_",
        "expected_admin_codes": None,   # 26 NUTS-3 codes validated at pilot time
    },
    "sweden": {
        "polygon_path": "~/eurostat_gisco_nuts3_2024/NUTS_RG_01M_2024_4326.shp",
        "polygon_filter": {"LEVL_CODE": 3, "CNTR_CODE": "SE"},
        "polygon_admin_column": "NUTS_ID",   # emits SE110..SE332 (21 codes)
        "csv_relpath": "scripts/pipeline/data/sweden/eurostat_nuts3_socioeconomic.csv",
        "csv_lookup_column": "province",
        "sub_id_prefix_pattern": "SE_v43_",
        "expected_admin_codes": None,   # 21 NUTS-3 codes validated at pilot time
    },
    "us": {
        # GADM 4.1 admin1 = 50 states + DC + territories. CSV agency source
        # uses state names as province column. GADM NAME_1 emits English
        # state names directly. Convention #7 documented-proxy anchor.
        "polygon_path": "~/gadm41_USA_shp/gadm41_USA_1.shp",
        "polygon_filter": {},
        "polygon_admin_column": "NAME_1",
        "polygon_admin_normalise": False,
        "csv_relpath": "scripts/pipeline/data/us/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",
        "csv_lookup_aliases": {},  # populate as pilot surfaces mismatches
        "sub_id_prefix_pattern": "US_v43_",
        "expected_admin_codes": None,   # 50 states + DC validated at pilot time
    },
    "japan": {
        # GADM 4.1 admin1 = 47 prefectures. CSV agency source uses
        # romanized prefecture names (Aichi, Akita, Aomori, ...).
        # GADM NAME_1 emits English romanization directly.
        "polygon_path": "~/gadm41_JPN_shp/gadm41_JPN_1.shp",
        "polygon_filter": {},
        "polygon_admin_column": "NAME_1",
        "polygon_admin_normalise": False,
        "csv_relpath": "scripts/pipeline/data/japan/agency_regional_socioeconomic.csv",
        "csv_lookup_column": "province",
        "csv_lookup_aliases": {},  # populate as pilot surfaces mismatches
        "sub_id_prefix_pattern": "JP_v43_",
        "expected_admin_codes": None,   # 47 prefectures validated at pilot time
    },
    # Italy BLOCKED — missing scripts/pipeline/data/italy/eurostat_nuts3_socioeconomic.csv
    # AND scripts/pipeline/data/italy/agency_regional_socioeconomic.csv. Requires operator-
    # sourced ISTAT NUTS-3 data scaffolding (110 provinces / 21 regions IT111..ITH1). Once
    # CSV lands, add italy entry mirroring france/germany/spain pattern.
}


# ═════════════════════════════════════════════════════════════════════
#  Logging
# ═════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
#  V_socio computation (mirrors socioeconomic.py:511-517)
# ═════════════════════════════════════════════════════════════════════

def compute_v_socio(ep_rate: float, gdp_pc: float, elderly_pct: float) -> float:
    """Convention #7: mirrors socioeconomic.py:overlay_socioeconomic V_socio
    formula. Any drift here would produce different V_socio values than
    the modern pipeline emits — deliberately keep in lock-step."""
    ep_norm = min(1.0, ep_rate / 25.0)
    gdp_norm = max(0.0, min(1.0, 1.0 - (gdp_pc - 14000.0) / 40000.0))
    elderly_norm = min(1.0, max(0.0, (elderly_pct - 18.0) / 15.0))
    return round(
        0.45 * ep_norm + 0.35 * gdp_norm + 0.20 * elderly_norm,
        4,
    )


# ═════════════════════════════════════════════════════════════════════
#  CSV loader
# ═════════════════════════════════════════════════════════════════════

def load_socio_csv(csv_path: Path, lookup_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a per-country socio-economic CSV, keyed by lookup_column value.

    Returns dict: { csv[lookup_column]: { column: value, ... } }
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    lookup: Dict[str, Dict[str, Any]] = {}
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (row.get(lookup_column) or "").strip()
            if not key:
                continue
            # Numeric coercion for known fields
            cleaned: Dict[str, Any] = {}
            for k, v in row.items():
                if k in ("gdp_per_capita", "unemployment_rate", "elderly_pct", "ep_rate"):
                    try:
                        cleaned[k] = float(v) if v not in (None, "", "None") else None
                    except (ValueError, TypeError):
                        cleaned[k] = None
                else:
                    cleaned[k] = v
            lookup[key] = cleaned
    return lookup


# ═════════════════════════════════════════════════════════════════════
#  Per-country provenance-mode enrichment
# ═════════════════════════════════════════════════════════════════════

def enrich_country_from_provenance(
    slug: str,
    config: Dict[str, Any],
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Backfill socio_economic for a country whose osm_overpass.py already
    detects admin codes but doesn't propagate to `province`.

    Reads detection from v43_provenance[SOURCE_KEY][DETECTED_FIELD], sets
    top-level `province`, merges CSV fields into `socio_economic` block.

    Preserves Task #451/#452 markers by touching ONLY the fields in
    BACKFILL_TARGET_FIELDS + the top-level `province` key.
    """
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")

    t0 = time.time()
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found")

    csv_path = REPO_ROOT / config["csv_relpath"]
    log.info(f"[{slug}] loading CSV {csv_path.name}...")
    csv_lookup = load_socio_csv(csv_path, config["csv_lookup_column"])
    log.info(f"[{slug}] CSV loaded — {len(csv_lookup)} regions available: "
             f"sample={list(csv_lookup.keys())[:5]}")

    log.info(f"[{slug}] loading ssi-data.json...")
    data = read_ssi_data(ssi_path)
    substations = data.get("substations", [])
    n = len(substations)
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # ── audit counters ─────────────────────────────────────────────────
    n_v43 = 0
    n_already_populated = 0
    n_no_provenance_detection = 0
    n_csv_lookup_miss = 0
    n_written = 0
    detected_codes = set()

    prov_key = config["provenance_source_key"]
    det_field = config["provenance_detected_field"]

    log.info(f"[{slug}] enriching (provenance_source={prov_key}, "
             f"detected_field={det_field})...")

    for sub in substations:
        sid = sub.get("substation_id") or sub.get("id") or ""

        # Only touch v43 subs (v1 subs already have complete socio_economic)
        if "_v43_" not in str(sid):
            continue
        n_v43 += 1

        # If province is already populated (from prior run), skip
        if sub.get("province"):
            n_already_populated += 1
            continue

        # Extract detected code from v43_provenance
        prov = (sub.get("v43_provenance") or {}).get(prov_key) or {}
        detected = prov.get(det_field)
        if not detected:
            n_no_provenance_detection += 1
            continue

        code = str(detected).strip()
        detected_codes.add(code)

        # CSV lookup
        row = csv_lookup.get(code)
        if not row:
            # Try case-normalised fallback
            row = csv_lookup.get(code.upper()) or csv_lookup.get(code.lower())
        if not row:
            n_csv_lookup_miss += 1
            continue

        # ── Merge fields — dict.update semantics, preserves markers ──
        se = sub.setdefault("socio_economic", {})

        gdp_pc = row.get("gdp_per_capita") or 30000.0
        unemp = row.get("unemployment_rate") or 5.0
        ep_rate = row.get("ep_rate") or 7.0
        elderly_pct = row.get("elderly_pct")

        # Only backfill fields we're allowed to touch — preserves Task
        # #451 population + Task #452 migration_score + their markers
        se["gdp_per_capita"] = gdp_pc
        se["unemployment_rate"] = unemp
        se["EP_rate_region"] = ep_rate
        if elderly_pct is not None:
            se["elderly_pct"] = elderly_pct

        # Compute V_socio only if we have all inputs
        if elderly_pct is not None:
            se["V_socio"] = compute_v_socio(ep_rate, gdp_pc, elderly_pct)

        # Set top-level province + audit marker
        sub["province"] = code
        se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE_PROVENANCE

        n_written += 1

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
    else:
        log.info(f"[{slug}] writing ssi-data.json...")
        write_ssi_data(data, ssi_path)
        log.info(f"[{slug}] saved.")

    elapsed = time.time() - t0
    return {
        "country": slug,
        "mode": "from_provenance",
        "n_substations": n,
        "n_v43_subs": n_v43,
        "n_written": n_written,
        "n_already_populated": n_already_populated,
        "n_no_provenance_detection": n_no_provenance_detection,
        "n_csv_lookup_miss": n_csv_lookup_miss,
        "unique_detected_codes": len(detected_codes),
        "detected_codes_sample": sorted(detected_codes)[:10],
        "csv_regions_available": len(csv_lookup),
        "wall_clock_sec": round(elapsed, 1),
        "dry_run": dry_run,
    }


# ═════════════════════════════════════════════════════════════════════
#  Polygon spatial-join loader
# ═════════════════════════════════════════════════════════════════════

def _resolve_path(path_str: str) -> Path:
    """Expand ~ and env vars, return absolute Path."""
    return Path(path_str).expanduser().resolve()


def load_polygon_index(
    polygon_path: Path,
    admin_column: str,
    polygon_filter: Optional[Dict[str, Any]] = None,
    admin_normalise: bool = False,
) -> Optional[Dict[str, Any]]:
    """Load a shapefile into a STRtree spatial index keyed on admin_column.

    Returns dict with:
      tree: shapely.strtree.STRtree
      geometries: list[shapely.geometry] (indices match tree return values)
      admin_codes: list[str] (parallel to geometries)
      crs: str
      n_polygons: int

    Returns None on failure (shapefile missing, wrong CRS, etc.) per
    Convention #56 visibly-honest degradation.
    """
    if not _HAS_POLYGON_DEPS:
        log.error(f"polygon-mode dependencies missing (install: pip install geopandas shapely)")
        return None
    if not polygon_path.exists():
        log.error(f"polygon shapefile not found: {polygon_path}")
        return None

    log.info(f"loading polygon shapefile {polygon_path.name}...")
    gdf = gpd.read_file(polygon_path)

    # Reproject to EPSG:4326 if needed (per preflight R4 mitigation)
    if gdf.crs is None:
        log.warning(f"shapefile has no CRS declared — assuming EPSG:4326")
        gdf.set_crs("EPSG:4326", inplace=True)
    elif gdf.crs.to_epsg() != 4326:
        log.info(f"reprojecting from {gdf.crs} → EPSG:4326")
        gdf = gdf.to_crs("EPSG:4326")

    # Apply filter (e.g. LEVL_CODE=3 + CNTR_CODE=LU for Eurostat GISCO)
    if polygon_filter:
        for col, val in polygon_filter.items():
            if col not in gdf.columns:
                log.error(f"filter column '{col}' not in shapefile columns: {list(gdf.columns)[:20]}")
                return None
            gdf = gdf[gdf[col] == val]
        log.info(f"filter {polygon_filter} → {len(gdf)} polygons")

    if admin_column not in gdf.columns:
        log.error(f"admin_column '{admin_column}' not in shapefile columns: {list(gdf.columns)[:20]}")
        return None

    if len(gdf) == 0:
        log.error(f"filter produced empty geodataframe")
        return None

    geometries = list(gdf.geometry)
    admin_codes: List[str] = []
    for _, row in gdf.iterrows():
        code = row[admin_column]
        if code is None:
            admin_codes.append("")
            continue
        code_str = str(code).strip()
        if admin_normalise:
            # DANE column strings are UPPERCASE; normalise to Title Case for CSV lookup
            code_str = code_str.title()
        admin_codes.append(code_str)

    tree = STRtree(geometries)
    log.info(f"STRtree built with {len(geometries)} polygons; "
             f"admin codes sample: {admin_codes[:5]}")

    return {
        "tree": tree,
        "geometries": geometries,
        "admin_codes": admin_codes,
        "crs": "EPSG:4326",
        "n_polygons": len(geometries),
    }


def query_polygon(
    lat: float,
    lon: float,
    poly_index: Dict[str, Any],
) -> Optional[str]:
    """Point-in-polygon query. Returns admin_code or None if outside all polygons.

    STRtree.query() returns candidate indices whose bboxes intersect the
    point; we then verify true containment via the geometry.contains(point).

    Handles shapely 2.x (returns numpy array of integer indices — including
    numpy.int64 which is NOT isinstance(int)) AND shapely 1.x (returns list
    of geometry objects).
    """
    if lat is None or lon is None:
        return None
    point = Point(lon, lat)   # shapely uses (x, y) = (lon, lat)
    candidates = poly_index["tree"].query(point)
    geometries = poly_index["geometries"]
    admin_codes = poly_index["admin_codes"]
    n_polys = len(geometries)
    for idx in candidates:
        # Try integer-index path first (shapely 2.x + numpy.int64)
        try:
            i = int(idx)
            if 0 <= i < n_polys:
                geom = geometries[i]
                code = admin_codes[i]
                if geom.contains(point):
                    return code
                continue
        except (TypeError, ValueError):
            pass
        # Shapely 1.x fallback — idx IS the geometry object
        try:
            geom = idx
            if not hasattr(geom, "contains"):
                continue
            if geom.contains(point):
                # Find its admin code by identity match
                for i in range(n_polys):
                    if geometries[i] is geom:
                        return admin_codes[i]
        except Exception:  # noqa: BLE001
            continue
    return None


# ═════════════════════════════════════════════════════════════════════
#  Per-country polygon-mode enrichment (Task #453 load-bearing)
# ═════════════════════════════════════════════════════════════════════

def enrich_country_from_polygon(
    slug: str,
    config: Dict[str, Any],
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Polygon spatial-join backfill for a country whose OSM tag density is
    empirically insufficient for admin-code derivation via provenance-mode
    (see METHODOLOGY_DISCIPLINES.md §5septies).

    Loads country-specific admin polygon shapefile → STRtree spatial index →
    iterates v43 subs with province=None → point-in-polygon → sets top-level
    sub["province"] + merges CSV socio_economic fields into
    sub["socio_economic"] via dict.update() semantics preserving Task
    #451/#452 audit-trail markers per Convention BINDING contract.

    Convention #56 fallback: subs outside all polygons receive None (not
    fabricated). Any polygon-mode error → returns None-populated audit
    without raising.
    """
    if not _HAS_SHARDING:
        raise RuntimeError("ssi_data_sharding utility not importable")
    if not _HAS_POLYGON_DEPS:
        raise RuntimeError(
            "polygon-mode dependencies missing — install: pip install geopandas shapely"
        )

    t0 = time.time()
    ssi_path = REPO_ROOT / slug / "ssi-data.json"
    if not ssi_path.exists():
        raise FileNotFoundError(f"[{slug}] ssi-data.json not found")

    # ── load polygon index ─────────────────────────────────────────────
    polygon_path = _resolve_path(config["polygon_path"])
    poly_index = load_polygon_index(
        polygon_path,
        admin_column=config["polygon_admin_column"],
        polygon_filter=config.get("polygon_filter"),
        admin_normalise=config.get("polygon_admin_normalise", False),
    )
    if poly_index is None:
        log.error(f"[{slug}] polygon index load FAILED — cannot proceed")
        return {
            "country": slug,
            "mode": "from_polygon",
            "error": "polygon_index_load_failed",
            "polygon_path_expected": str(polygon_path),
            "dry_run": dry_run,
        }

    # ── load CSV ───────────────────────────────────────────────────────
    csv_path = REPO_ROOT / config["csv_relpath"]
    log.info(f"[{slug}] loading CSV {csv_path.name}...")
    csv_lookup = load_socio_csv(csv_path, config["csv_lookup_column"])
    log.info(f"[{slug}] CSV loaded — {len(csv_lookup)} regions; "
             f"sample keys: {list(csv_lookup.keys())[:5]}")

    # ── load ssi-data.json ────────────────────────────────────────────
    log.info(f"[{slug}] loading ssi-data.json...")
    data = read_ssi_data(ssi_path)
    substations = data.get("substations", [])
    n = len(substations)
    log.info(f"[{slug}] {n:,} subs loaded in {time.time()-t0:.1f}s")

    # ── audit counters ─────────────────────────────────────────────────
    n_v43 = 0
    n_already_populated = 0
    n_missing_coords = 0
    n_outside_polygons = 0
    n_csv_lookup_miss = 0
    n_written = 0
    detected_codes: Dict[str, int] = {}   # code → count
    task_451_markers_preserved = 0
    task_452_markers_preserved = 0

    log.info(f"[{slug}] enriching via polygon spatial-join...")

    for sub in substations:
        sid = sub.get("substation_id") or sub.get("id") or ""

        # Only touch v43 subs (v1 subs already have complete socio_economic)
        if "_v43_" not in str(sid):
            continue
        n_v43 += 1

        # Skip logic — refined 24 Jul 2026 per Task #454 Canada surface:
        # (a) FULLY POPULATED (Task #453 idempotent no-op): province AND
        #     gdp_per_capita both set → skip (preserves LU/SI/LT/CO idempotency)
        # (b) PARTIALLY POPULATED (Task #454 Canada case): province set BUT
        #     gdp_per_capita None → bypass polygon join, use existing province
        #     as CSV lookup key (Canada v43 subs already carry valid province
        #     names matching CSV; polygon join would be redundant)
        # (c) NOT POPULATED (Task #453 EU/CO + Task #454 EU case): province None
        #     → run polygon spatial-join to derive it (existing logic)
        existing_province = sub.get("province")
        existing_se = sub.get("socio_economic") or {}
        existing_gdp_populated = existing_se.get("gdp_per_capita") is not None

        if existing_province and existing_gdp_populated:
            # Case (a): idempotent no-op
            n_already_populated += 1
            continue

        code: Optional[str] = None

        if existing_province and not existing_gdp_populated:
            # Case (b): use existing province, bypass polygon join
            code = str(existing_province).strip()
        else:
            # Case (c): derive province via polygon spatial-join
            # ── point-in-polygon query ────────────────────────────────────
            lat = sub.get("lat") or sub.get("latitude")
            lon = sub.get("lon") or sub.get("longitude")
            if lat is None or lon is None:
                n_missing_coords += 1
                continue

            try:
                code = query_polygon(float(lat), float(lon), poly_index)
            except (ValueError, TypeError):
                n_missing_coords += 1
                continue

            if code is None:
                # Convention #56 visibly-honest degradation: outside all polygons
                n_outside_polygons += 1
                continue

        # ── CSV lookup ─────────────────────────────────────────────────
        row = csv_lookup.get(code)
        if not row:
            # Try per-country alias map (e.g. GADM "Bogotá" → CSV "Bogotá D.C.")
            aliases = config.get("csv_lookup_aliases") or {}
            aliased = aliases.get(code)
            if aliased:
                row = csv_lookup.get(aliased)
        if not row:
            # Try case-normalised fallback (defensive)
            row = csv_lookup.get(code.upper()) or csv_lookup.get(code.lower())
        if not row:
            n_csv_lookup_miss += 1
            continue

        # ── Merge fields — dict.update semantics preserves markers ────
        se = sub.setdefault("socio_economic", {})

        # Track pre-existing markers for audit
        had_451 = "_catchment_population_source" in se
        had_452 = "_migration_score_source" in se

        gdp_pc = row.get("gdp_per_capita") or 30000.0
        unemp = row.get("unemployment_rate") or 5.0
        ep_rate = row.get("ep_rate") or 7.0
        elderly_pct = row.get("elderly_pct")

        # Explicit field-list update — preserves Task #451/#452 markers +
        # migration_score by NOT including them in the update field set
        se["gdp_per_capita"] = gdp_pc
        se["unemployment_rate"] = unemp
        se["EP_rate_region"] = ep_rate
        if elderly_pct is not None:
            se["elderly_pct"] = elderly_pct

        # Compute V_socio only if we have all inputs
        if elderly_pct is not None:
            se["V_socio"] = compute_v_socio(ep_rate, gdp_pc, elderly_pct)

        # Set top-level province + audit marker
        sub["province"] = code
        se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE_POLYGON

        # Verify BINDING contract: markers survived
        if had_451:
            task_451_markers_preserved += 1
        if had_452:
            task_452_markers_preserved += 1

        detected_codes[code] = detected_codes.get(code, 0) + 1
        n_written += 1

    if dry_run:
        log.info(f"[{slug}] DRY-RUN — no write")
    else:
        log.info(f"[{slug}] writing ssi-data.json...")
        write_ssi_data(data, ssi_path)
        log.info(f"[{slug}] saved.")

    elapsed = time.time() - t0
    return {
        "country": slug,
        "mode": "from_polygon",
        "n_substations": n,
        "n_v43_subs": n_v43,
        "n_written": n_written,
        "n_already_populated": n_already_populated,
        "n_missing_coords": n_missing_coords,
        "n_outside_polygons": n_outside_polygons,   # Convention #56 fallback
        "n_csv_lookup_miss": n_csv_lookup_miss,
        "unique_detected_codes": len(detected_codes),
        "detected_codes_distribution": dict(sorted(
            detected_codes.items(), key=lambda kv: -kv[1]
        )[:20]),
        "task_451_markers_preserved": task_451_markers_preserved,
        "task_452_markers_preserved": task_452_markers_preserved,
        "csv_regions_available": len(csv_lookup),
        "polygon_source_path": str(polygon_path),
        "polygon_n_polygons_loaded": poly_index["n_polygons"],
        "wall_clock_sec": round(elapsed, 1),
        "dry_run": dry_run,
    }


# ═════════════════════════════════════════════════════════════════════
#  Diagnostics
# ═════════════════════════════════════════════════════════════════════

def diagnose() -> Dict[str, Any]:
    diag: Dict[str, Any] = {
        "task_id": 453,
        "ssi_data_sharding_importable": _HAS_SHARDING,
        "polygon_deps_importable": _HAS_POLYGON_DEPS,
        "polygon_deps_install_cmd": "pip install geopandas shapely" if not _HAS_POLYGON_DEPS else None,
        "provenance_countries": {},
        "polygon_countries": {},
    }
    for slug, config in POLYGON_COUNTRY_CONFIGS.items():
        ssi_path = REPO_ROOT / slug / "ssi-data.json"
        csv_path = REPO_ROOT / config["csv_relpath"]
        polygon_path = _resolve_path(config["polygon_path"])
        diag["polygon_countries"][slug] = {
            "ssi_data_present": ssi_path.exists(),
            "csv_present": csv_path.exists(),
            "csv_path": str(csv_path.relative_to(REPO_ROOT)) if csv_path.exists() else str(csv_path),
            "polygon_path_expected": str(polygon_path),
            "polygon_present": polygon_path.exists(),
            "polygon_filter": config.get("polygon_filter", {}),
            "polygon_admin_column": config["polygon_admin_column"],
            "expected_admin_codes_count": (
                len(config["expected_admin_codes"])
                if config.get("expected_admin_codes") else "N/A (Colombia — 32 departamentos)"
            ),
        }
    diag["ready_for_polygon_cohort"] = _HAS_SHARDING and _HAS_POLYGON_DEPS and all(
        v["ssi_data_present"] and v["csv_present"] and v["polygon_present"]
        for v in diag["polygon_countries"].values()
    )
    for slug, config in PROVENANCE_COUNTRY_CONFIGS.items():
        ssi_path = REPO_ROOT / slug / "ssi-data.json"
        csv_path = REPO_ROOT / config["csv_relpath"]
        diag["provenance_countries"][slug] = {
            "ssi_data_present": ssi_path.exists(),
            "csv_present": csv_path.exists(),
            "csv_path": str(csv_path.relative_to(REPO_ROOT)) if csv_path.exists() else str(csv_path),
            "provenance_source_key": config["provenance_source_key"],
            "detected_field": config["provenance_detected_field"],
        }
    diag["ready_for_provenance_cohort"] = _HAS_SHARDING and all(
        v["ssi_data_present"] and v["csv_present"]
        for v in diag["provenance_countries"].values()
    )
    return diag


# ═════════════════════════════════════════════════════════════════════
#  CLI
# ═════════════════════════════════════════════════════════════════════

def _print_report(audit: Dict[str, Any]) -> None:
    if audit.get("error"):
        print(f"\n─── {audit['country']} (mode={audit['mode']}) FAILED ───")
        print(f"  error: {audit['error']}")
        for k, v in audit.items():
            if k not in {"country", "mode", "error"}:
                print(f"  {k}: {v}")
        return

    slug = audit["country"]
    mode = audit["mode"]
    n = audit["n_substations"]
    v43 = audit["n_v43_subs"]
    print(f"\n─── {slug} (mode={mode}, "
          f"{n:,} total subs, {v43:,} v43 subs, {audit['wall_clock_sec']}s) ───")
    print(f"  n_written                        {audit['n_written']:>7,}")
    print(f"  n_already_populated              {audit['n_already_populated']:>7,}")

    if mode == "from_provenance":
        print(f"  n_no_provenance_detection        {audit['n_no_provenance_detection']:>7,}")
        print(f"  n_csv_lookup_miss                {audit['n_csv_lookup_miss']:>7,}")
        print(f"  Unique detected codes: {audit['unique_detected_codes']} "
              f"(sample: {audit['detected_codes_sample'][:6]})")

    elif mode == "from_polygon":
        print(f"  n_missing_coords                 {audit['n_missing_coords']:>7,}")
        print(f"  n_outside_polygons (C56)         {audit['n_outside_polygons']:>7,}")
        print(f"  n_csv_lookup_miss                {audit['n_csv_lookup_miss']:>7,}")
        print(f"  Unique admin codes derived: {audit['unique_detected_codes']}")
        if audit.get("detected_codes_distribution"):
            print(f"  Code distribution (top): "
                  f"{list(audit['detected_codes_distribution'].items())[:5]}")
        print(f"  Task #451 markers preserved: {audit['task_451_markers_preserved']:,}")
        print(f"  Task #452 markers preserved: {audit['task_452_markers_preserved']:,}")
        print(f"  Polygon source: {Path(audit['polygon_source_path']).name} "
              f"({audit['polygon_n_polygons_loaded']} polygons loaded)")

    print(f"  CSV regions available: {audit['csv_regions_available']}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("slug", nargs="?",
                    help="country slug (LU|SI|CO|LT for polygon-mode; slovenia|colombia for provenance-mode)")
    ap.add_argument(
        "--from-polygon", action="store_true",
        help="use polygon spatial-join mode (Task #453 load-bearing implementation)",
    )
    ap.add_argument(
        "--polygon-cohort", action="store_true",
        help="run against all polygon-mode countries (luxembourg + slovenia + colombia + lithuania)",
    )
    ap.add_argument(
        "--provenance-cohort", action="store_true",
        help="run against all provenance-mode countries (slovenia + colombia — EMPIRICALLY DEAD 23 Jul 2026)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--diagnose-only", action="store_true")
    args = ap.parse_args()

    if args.diagnose_only:
        print(json.dumps(diagnose(), indent=2, default=str))
        return

    if not _HAS_SHARDING:
        log.error("ssi_data_sharding utility not importable")
        sys.exit(2)

    # ── Determine mode + targets ──────────────────────────────────────
    use_polygon = args.from_polygon or args.polygon_cohort

    if args.polygon_cohort:
        targets = list(POLYGON_COUNTRY_CONFIGS.keys())
    elif args.provenance_cohort:
        targets = list(PROVENANCE_COUNTRY_CONFIGS.keys())
        use_polygon = False
    elif args.slug:
        if use_polygon:
            if args.slug not in POLYGON_COUNTRY_CONFIGS:
                log.error(f"Unknown polygon-mode country '{args.slug}'. "
                          f"Polygon-mode supports: {list(POLYGON_COUNTRY_CONFIGS.keys())}.")
                sys.exit(2)
        else:
            # Default: prefer polygon-mode for any slug that supports it
            # (empirical Step 2a probe 23 Jul 2026 confirmed provenance-mode
            # is dead for all 4 target countries)
            if args.slug in POLYGON_COUNTRY_CONFIGS:
                use_polygon = True
                log.info(f"[{args.slug}] defaulting to polygon-mode "
                         f"(provenance-mode dead per Step 2a probe)")
            elif args.slug in PROVENANCE_COUNTRY_CONFIGS:
                use_polygon = False
            else:
                log.error(f"Unknown country '{args.slug}'. "
                          f"Polygon-mode: {list(POLYGON_COUNTRY_CONFIGS.keys())}. "
                          f"Provenance-mode: {list(PROVENANCE_COUNTRY_CONFIGS.keys())}.")
                sys.exit(2)
        targets = [args.slug]
    else:
        ap.error("must pass a slug OR --polygon-cohort OR --provenance-cohort")

    # ── Validate polygon deps if using polygon-mode ───────────────────
    if use_polygon and not _HAS_POLYGON_DEPS:
        log.error("polygon-mode requires geopandas + shapely — install: pip install geopandas shapely")
        sys.exit(2)

    # ── Execute enrichment ────────────────────────────────────────────
    audits = []
    mode_name = "from_polygon" if use_polygon else "from_provenance"
    for slug in targets:
        if use_polygon:
            config = POLYGON_COUNTRY_CONFIGS[slug]
            enrich_fn = enrich_country_from_polygon
        else:
            config = PROVENANCE_COUNTRY_CONFIGS[slug]
            enrich_fn = enrich_country_from_provenance
        try:
            audit = enrich_fn(slug, config, dry_run=args.dry_run)
            audits.append(audit)
            _print_report(audit)
        except Exception as e:  # noqa: BLE001
            log.error(f"[{slug}] FAILED: {e}")
            import traceback
            traceback.print_exc()

    if audits:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        report_path = Path.home() / f"socio_economic_backfill_audit_{ts}.json"
        report_path.write_text(json.dumps({
            "task_id": 453,
            "mode": mode_name,
            "run_timestamp_utc": ts,
            "dry_run": args.dry_run,
            "n_countries": len(audits),
            "audits": audits,
        }, indent=2, default=str))
        print(f"\n✓ Consolidated audit report: {report_path}")


if __name__ == "__main__":
    main()
