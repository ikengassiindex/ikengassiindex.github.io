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
COUNTRIES = [
    "italy", "germany", "france", "spain", "uk",
    "us", "switzerland", "austria", "canada", "japan",
    "denmark", "norway", "finland", "poland", "sweden", "mexico",
    "greece", "turkey", "ireland", "portugal",
]

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
}

# ── SSI v4.0.2 Scoring Parameters ─────────────────────────
COMPONENT_WEIGHTS = {"C": 0.30, "V": 0.10, "I": 0.25, "E": 0.10, "S": 0.20, "T": 0.05}

MODIFIER_RANGES = {
    "R3_C_mult":      (0.70, 1.50),
    "R4_F_topo":      (0.80, 1.35),
    "R6_restoration": (0.90, 1.10),
    "R6_seismic":     (1.00, 1.25),
    "R7_cyber":       (0.99, 1.05),
}

CLASSIFICATION_BANDS = [
    {"name": "Low",      "min": 0.00, "max": 0.25},
    {"name": "Medium",   "min": 0.25, "max": 0.50},
    {"name": "High",     "min": 0.50, "max": 0.75},
    {"name": "Critical", "min": 0.75, "max": 1.00},
]

MC_ITERATIONS = 10_000

# ── ESG Report Definitions ────────────────────────────────
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
        "name": "EU Taxonomy Alignment",
        "framework": "Climate Delegated Act · Article 11 Adaptation",
        "primary_sdg": 9,
        "variables": ["R_median", "components", "modifiers", "CI"],
        "required_fields": ["R_median", "components", "modifiers"],
    },
    "R4": {
        "name": "Energy Transition & DER Stress",
        "framework": "ESRS E1 Transition · TCFD Transition Risk",
        "primary_sdg": 7,
        "variables": ["T1_score", "DER_ratio", "DER_variability", "EV_load_ratio"],
        "required_fields": ["transition.T1_score", "transition.DER_ratio"],
    },
    "R5": {
        "name": "Pollution & Corrosion",
        "framework": "ESRS E2 Pollution · ISO 9223",
        "primary_sdg": 11,
        "variables": ["corrosion_class", "E2_local", "E_component"],
        "required_fields": ["markov.corrosion_class", "socio_economic.E2_local"],
    },
    "R6": {
        "name": "Cybersecurity Exposure",
        "framework": "NIS2 Directive · ENISA · ESRS G1",
        "primary_sdg": 9,
        "variables": ["R7_cyber", "BC_percentile", "degree", "is_bridge"],
        "required_fields": ["graph_topology.degree", "graph_topology.BC_percentile"],
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
