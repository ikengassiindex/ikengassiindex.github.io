"""
SSI Index v4.0.2 — Pipeline Configuration
Central configuration for ingestion, scoring, and enrichment.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT  # country folders are at repo root
CACHE_DIR = PIPELINE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

# ── Countries ─────────────────────────────────────────────
# KB §49.8 / §57 (Normalization) — single source of truth.
# Slugs live in intelligence/countries.json. The pipeline must NEVER carry
# a private hardcoded list — that path drifts and excludes new countries
# from monthly automation (e.g. the BE/NL/LU/CZ/LV/LT/EE pipeline-enrichment
# fleet-floor hole, May 2026).
def _load_countries_from_sot():
    import json
    sot = REPO_ROOT / "intelligence" / "countries.json"
    if not sot.exists():
        # Fallback for tests / standalone runs where the repo SoT is unavailable.
        return ["france", "italy", "germany", "spain", "uk", "us"]
    with open(sot) as f:
        return list(json.load(f)["slugs"])

COUNTRIES = _load_countries_from_sot()

# Country metadata for ingestion routing
COUNTRY_META = {
    "italy":       {"iso2": "IT", "iso3": "ITA", "nuts0": "IT",  "stats_agency": "ISTAT",  "seismic_source": "INGV",       "fields": 59},
    "germany":     {"iso2": "DE", "iso3": "DEU", "nuts0": "DE",  "stats_agency": "Destatis","seismic_source": "BGR",        "fields": 61},
    "france":      {"iso2": "FR", "iso3": "FRA", "nuts0": "FR",  "stats_agency": "INSEE",  "seismic_source": "BRGM",       "fields": 61},
    "spain":       {"iso2": "ES", "iso3": "ESP", "nuts0": "ES",  "stats_agency": "INE",    "seismic_source": "IGN",        "fields": 61},
    "uk":          {"iso2": "GB", "iso3": "GBR", "nuts0": "UK",  "stats_agency": "ONS",    "seismic_source": "BGS",        "fields": 58},
    "us":          {"iso2": "US", "iso3": "USA", "nuts0": None,   "stats_agency": "Census", "seismic_source": "USGS",       "fields": 10},
    "switzerland": {"iso2": "CH", "iso3": "CHE", "nuts0": "CH",  "stats_agency": "BFS",    "seismic_source": "SED",        "fields": 61},
    "austria":     {"iso2": "AT", "iso3": "AUT", "nuts0": "AT",  "stats_agency": "StatAT", "seismic_source": "GeoSphere",  "fields": 79},
    "canada":      {"iso2": "CA", "iso3": "CAN", "nuts0": None,   "stats_agency": "StatCan","seismic_source": "NRCan",      "fields": 39},
    "japan":       {"iso2": "JP", "iso3": "JPN", "nuts0": None,   "stats_agency": "eStat",  "seismic_source": "NIED",       "fields": 62},
    "denmark":     {"iso2": "DK", "iso3": "DNK", "nuts0": "DK",  "stats_agency": "DST",    "seismic_source": "GEUS",       "fields": 61},
    "norway":      {"iso2": "NO", "iso3": "NOR", "nuts0": "NO",  "stats_agency": "SSB",    "seismic_source": "NORSAR",     "fields": 61},
    "finland":     {"iso2": "FI", "iso3": "FIN", "nuts0": "FI",  "stats_agency": "StatFin","seismic_source": "ISUH",       "fields": 61},
    "poland":      {"iso2": "PL", "iso3": "POL", "nuts0": "PL",  "stats_agency": "GUS",    "seismic_source": "IGF-PAN",    "fields": 61},
    "sweden":      {"iso2": "SE", "iso3": "SWE", "nuts0": "SE",  "stats_agency": "SCB",    "seismic_source": "SNSN",       "fields": 61},
    "mexico":      {"iso2": "MX", "iso3": "MEX", "nuts0": None,   "stats_agency": "INEGI",  "seismic_source": "CENAPRED",   "fields": 95},
    "greece":      {"iso2": "GR", "iso3": "GRC", "nuts0": "EL",  "stats_agency": "ELSTAT", "seismic_source": "ITSAK/EAK",  "fields": 95},
    "turkey":      {"iso2": "TR", "iso3": "TUR", "nuts0": None,   "stats_agency": "TÜİK",   "seismic_source": "AFAD",       "fields": 95},
    "ireland":     {"iso2": "IE", "iso3": "IRL", "nuts0": "IE",  "stats_agency": "CSO",    "seismic_source": "DIAS/GSI",   "fields": 95},
    "portugal":    {"iso2": "PT", "iso3": "PRT", "nuts0": "PT",  "stats_agency": "INE",    "seismic_source": "IPMA/LNEG",  "fields": 95},
    "new-zealand": {"iso2": "NZ", "iso3": "NZL", "nuts0": None,  "stats_agency": "StatsNZ","seismic_source": "GNS/GeoNet", "fields": 95},
    "greenland":   {"iso2": "GL", "iso3": "GRL", "nuts0": None,  "stats_agency": "Stat.gl","seismic_source": "GEUS/DMI",   "fields": 95},
}

# ── SSI v4.0.2 Scoring Parameters ─────────────────────────
COMPONENT_WEIGHTS = {"C": 0.30, "V": 0.10, "I": 0.25, "E": 0.10, "S": 0.20, "T": 0.05}

MODIFIER_RANGES = {
    "R3_C_mult":      (0.70, 1.50),
    "R4_F_topo":      (0.80, 1.35),
    "R6_restoration": (0.90, 1.10),
    "R6_seismic":     (0.95, 1.25),
    "R7_cyber":       (0.99, 1.05),
}
# Convention #56 note: R6_seismic floor widened 1.00 → 0.95 in task #180 to align
# spec with empirical Central European low-seismicity reality (Belgium/Netherlands/
# Luxembourg/Czechia tectonically-passive plates emit values 0.95-1.00). Ceiling
# preserved. Task #179 cohort audit sweep root-cause anchor.

CLASSIFICATION_BANDS = [
    {"name": "Low",      "min": 0.00, "max": 0.25},
    {"name": "Medium",   "min": 0.25, "max": 0.50},
    {"name": "High",     "min": 0.50, "max": 0.75},
    {"name": "Critical", "min": 0.75, "max": 1.00},
]

MC_ITERATIONS = 10_000

# ── ESG Report Definitions ────────────────────────────────
# 🔥 7-report catalog per FC v3 §14 canonical (upgraded 16 July 2026 R7 workstream)
# — R7 SFDR PAI Infrastructure Disclosure added as documented-proxy under
# Convention #7 (Data-Layer Anchoring) using Re_normalised composite.
# — R3 relabelled "EU Taxonomy Alignment" → "Infrastructure Resilience [Re composite home]"
#   per FC v3 §14 subsection 13.3 (methodology home for Re composite).
# — R4 ↔ R5 order swap per FC v3 §14 canonical: R4=Pollution (was R5), R5=Transition (was R4).
# — R7a formula-modifier (R7_cyber) remains at R6 Cybersecurity Exposure inputs list.
# — R7b ESG-axis (this new R7 entry) uses Re_normalised as documented-proxy per
#   V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5 R7 duality codification.
# See R7_SFDR_PAI_diligence_note.md + R7_SFDR_PAI_current_state_audit.md +
# R7_SFDR_PAI_phase3_design_signoff.md for full workstream rationale.
ESG_REPORTS = {
    "R1": {
        "name": "Climate Physical Risk Assessment",
        "framework": "ESRS E1 · TCFD Physical Risk · EU Taxonomy Annex A",
        "primary_sdg": 13,
        "variables": ["I1", "I2", "I3", "I5", "R2_climate", "R6b_seismic", "markov"],
        "required_fields": ["seismic.pga_g", "climate_trajectory.I1_trajectory"],
    },
    "R2": {
        "name": "Grid Equity & Social Vulnerability",
        "framework": "ESRS S1/S2 · SFDR PAI Social · UN PRI",
        "primary_sdg": 7,
        "variables": ["V_socio", "EP_rate", "elderly_vuln", "migration_score", "fiscal_composite"],
        "required_fields": ["socio_economic.V_socio", "socio_economic.EP_rate_region"],
    },
    "R3": {
        # FC v3 §14 subsection 13.3 canonical — Re composite home
        # Renamed from "EU Taxonomy Alignment" 16 July 2026 per R7 workstream.
        # Underlying methodology unchanged (Article 11 Adaptation screening via
        # R_median + 6 components + full modifier suite + Markov degradation).
        "name": "Infrastructure Resilience [Re composite home]",
        "framework": "Climate Delegated Act · Article 11 Adaptation · Re composite anchor (FC v3 §14 subsection 13.3)",
        "primary_sdg": 9,
        "variables": ["R_median", "components", "modifiers", "CI", "Re_norm"],
        "required_fields": ["R_median", "components", "modifiers"],
    },
    "R4": {
        # FC v3 §14 canonical order — R4 was previously "Energy Transition & DER Stress" but
        # FC v3 §14 canonical places Pollution at position 4. Swapped 16 July 2026 per R7 workstream.
        "name": "Pollution & Corrosion",
        "framework": "ESRS E2 Pollution · ISO 9223",
        "primary_sdg": 11,
        "variables": ["corrosion_class", "E2_local", "E_component"],
        "required_fields": ["markov.corrosion_class", "socio_economic.E2_local"],
    },
    "R5": {
        # FC v3 §14 canonical order — R5 was previously "Pollution & Corrosion" but FC v3 §14
        # canonical places Energy Transition at position 5. Swapped 16 July 2026 per R7 workstream.
        "name": "Energy Transition & DER Stress",
        "framework": "ESRS E1 Transition · TCFD Transition Risk",
        "primary_sdg": 7,
        "variables": ["T1_score", "DER_ratio", "DER_variability", "EV_load_ratio"],
        "required_fields": ["transition.T1_score", "transition.DER_ratio"],
    },
    "R6": {
        "name": "Cybersecurity Exposure",
        "framework": "NIS2 Directive · ENISA · ESRS G1",
        "primary_sdg": 9,
        "variables": ["R7_cyber", "BC_percentile", "degree", "is_bridge"],
        "required_fields": ["graph_topology.degree", "graph_topology.BC_percentile"],
    },
    "R7": {
        # NEW 16 July 2026 — R7 SFDR PAI Infrastructure Disclosure per FC v3 §14
        # subsection 13.7 "R7 — SFDR Principal Adverse Impact Statement (Infrastructure Module)".
        # This is R7b (ESG-axis), distinct-by-design from R7a formula-modifier (R7_cyber)
        # per V4_2_IMPLEMENTATION_ARCHITECTURE.md §4.5 R7 duality codification.
        # Data source: Re_normalised composite (Convention #7 Data-Layer Anchoring documented-proxy).
        # Bounds: [0, 1] via Re_norm = clip((Re_raw − 0.920) / (1.787 − 0.920), 0, 1).
        # Re_raw underlying: Re_raw = (R6d × R6e × R8 × R9 × R10) + (R6c − 1.00) bounded [0.920, 1.787].
        # Convention #56 preservation: fresh net-new substations post-L1 refresh carry neutral
        # defaults (Re_raw=1.0, Re_norm=0.0) per merge_into_ssi_data.py init; only Re_norm > 0
        # counts as READY per two-phase workflow discipline (Convention #78 §4bis.4).
        "name": "SFDR PAI Infrastructure Disclosure",
        "framework": "SFDR Article 4 · PAI Table 1 · Delegated Reg (EU) 2022/1288 · FC v3 §14 subsection 13.7 · Infrastructure Module",
        "primary_sdg": 12,  # Responsible Consumption & Production
        "variables": ["Re_norm", "Re_raw", "R6c_flood", "R6d_wildfire", "R6e_winter", "R8_adapt", "R9_compound", "R10_just"],
        "required_fields": ["Re_norm"],
    },
}

# ── Data Source API Configuration ─────────────────────────
# API keys loaded from environment variables
CDS_API_KEY = os.environ.get("CDS_API_KEY")        # Copernicus Climate Data Store
CDS_API_URL = "https://cds.climate.copernicus.eu/api"

# INGV MPS04 — Italy seismic hazard (direct download, no API key needed)
INGV_MPS04_URL = "https://esse1-gis.mi.ingv.it/s1_en.php"
INGV_HAZARD_GRID_URL = "https://esse1-gis.mi.ingv.it/data/pga_475_grid.csv"

# CENAPRED — Mexico seismic & volcanic hazard (open access)
CENAPRED_SEISMIC_URL = "https://www.cenapred.unam.mx/es/Publicaciones/archivos/atlas-nacional-de-riesgos"
# SSN — Servicio Sismológico Nacional seismicity data
SSN_SEISMIC_URL = "https://www2.ssn.unam.mx:8080/catalogo/"
# INEGI — Mexican statistics open data
INEGI_API_BASE = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"

# Copernicus ERA5 reanalysis
ERA5_VARIABLES = ["2m_temperature", "10m_u_component_of_wind", "10m_v_component_of_wind"]

# CMIP6 — SSP2-4.5 ensemble
CMIP6_EXPERIMENT = "ssp245"
CMIP6_MODELS = ["ACCESS-CM2", "CNRM-CM6-1", "EC-Earth3", "GFDL-ESM4", "MRI-ESM2-0"]
CMIP6_PERIOD_BASELINE = (2000, 2020)
CMIP6_PERIOD_FUTURE = (2030, 2050)

# ISTAT Open Data API
ISTAT_API_BASE = "https://esploradati.istat.it/SDMXWS/rest"

# ELSTAT — Greece statistics open data
ELSTAT_API_BASE = "https://www.statistics.gr/en/sdmx-rest"

# ITSAK / EAK 2003 — Greece seismic hazard
ITSAK_HAZARD_URL = "https://www.itsak.gr/db/data/pga"

# ── Logging ───────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
