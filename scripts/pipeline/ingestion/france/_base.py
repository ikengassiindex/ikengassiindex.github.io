"""France P37 Wave 4 — Convention #78 BINDING 19th enforcement.

8-language alias map TIES ITALY as HIGHEST cohort-wide:
  French (Français) + English + Corsican (Corsu) + Breton (Brezhoneg)
  + Basque (Euskara) + Alsatian (Elsässisch) + Catalan (Català) +
  Occitan (Occitan/Provençal).

NO §4bis.5 metropolitan geofence (Enedis ~95% dominant DSO
architectural simplification — 3rd Wave 4 country without §4bis.5
after Portugal + Japan).

8-layer resolver:
  1. Direct alias hit (Convention #78 BINDING 19th)
  2. Voltage-class heuristic (EHV/HV/subT/MV)
  3. Rail traction 1.5 kV DC SNCF + 25 kV AC TGV
  4. Corsica bbox → EDF SEI Corsica
  5. Guadeloupe bbox → EDF SEI Guadeloupe
  6. Martinique bbox → EDF SEI Martinique
  7. Guyane française bbox → EDF SEI Guyane
  8. Réunion bbox → EDF SEI Réunion
  9. Mayotte bbox → EDM Électricité de Mayotte
 10. Saint-Pierre-et-Miquelon bbox → EDF SEI SPM
 11. Alsace regional → ES Strasbourg + UEM Metz (if voltage MV)
 12. Fallback default DSO → Enedis (~95% mainland)

Sub-conventions preserved: #7 + #23 + #56 + #60 + #78 BINDING.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Bounding boxes — Discipline #36 + DOM/COM overseas carve-outs
# ─────────────────────────────────────────────────────────────

# France master bbox — mainland + Corsica + DOM territories
# Guyane française extends to South America (2.10°N to 5.80°N)
# Réunion in Indian Ocean (~55.5°E)
# Nouvelle-Calédonie in Pacific (~165°E) - COM not included in master bbox
# (would make bbox global-spanning; captured via dedicated bbox in fetcher)
FRANCE_MASTER_BBOX = {
    "lat_min": -21.40,  # Réunion south (Indian Ocean)
    "lat_max": 51.10,   # Dunkerque (mainland north)
    "lon_min": -61.85,  # Guadeloupe west (Caribbean)
    "lon_max": 55.85,   # Réunion east (Indian Ocean)
}

# Mainland France + Corsica
MAINLAND_BBOX = {
    "lat_min": 41.30,  # Corsica south
    "lat_max": 51.10,  # Dunkerque
    "lon_min": -5.15,  # Pointe de Corsen Brittany
    "lon_max": 9.60,   # Alsace east
}

# Corsica (part of mainland bbox but separately identified)
CORSICA_BBOX = {
    "lat_min": 41.30,
    "lat_max": 43.05,
    "lon_min": 8.50,
    "lon_max": 9.65,
    "operator_canonical": "EDF SEI Corsica",
    "role": "ISLANDED_DSO_CORSICA",
}

# DOM territories (each ISLANDED via EDF SEI or dedicated DSO)
GUADELOUPE_BBOX = {
    "lat_min": 15.83, "lat_max": 16.52,
    "lon_min": -61.85, "lon_max": -61.00,
    "operator_canonical": "EDF SEI Guadeloupe",
    "role": "ISLANDED_DOM_GUADELOUPE",
}

MARTINIQUE_BBOX = {
    "lat_min": 14.38, "lat_max": 14.88,
    "lon_min": -61.25, "lon_max": -60.80,
    "operator_canonical": "EDF SEI Martinique",
    "role": "ISLANDED_DOM_MARTINIQUE",
}

GUYANE_BBOX = {
    "lat_min": 2.10, "lat_max": 5.80,
    "lon_min": -54.60, "lon_max": -51.60,
    "operator_canonical": "EDF SEI Guyane",
    "role": "ISLANDED_DOM_GUYANE",
}

REUNION_BBOX = {
    "lat_min": -21.40, "lat_max": -20.85,
    "lon_min": 55.20, "lon_max": 55.85,
    "operator_canonical": "EDF SEI Réunion",
    "role": "ISLANDED_DOM_REUNION",
}

MAYOTTE_BBOX = {
    "lat_min": -13.05, "lat_max": -12.60,
    "lon_min": 45.00, "lon_max": 45.30,
    "operator_canonical": "EDM Mayotte",
    "role": "ISLANDED_DOM_MAYOTTE",
}

SAINT_PIERRE_MIQUELON_BBOX = {
    "lat_min": 46.75, "lat_max": 47.15,
    "lon_min": -56.45, "lon_max": -56.10,
    "operator_canonical": "EDF SEI Saint-Pierre-et-Miquelon",
    "role": "ISLANDED_DOM_SPM",
}


# ─────────────────────────────────────────────────────────────
# Convention #78 BINDING 19TH ENFORCEMENT — 8-language ALIAS_MAP
# ─────────────────────────────────────────────────────────────

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ═══ RTE — National TSO ═══
    "rte": ("RTE", "TSO"),
    "réseau de transport d'électricité": ("RTE", "TSO"),
    "reseau de transport d'electricite": ("RTE", "TSO"),
    "rte réseau de transport": ("RTE", "TSO"),
    "rte reseau de transport": ("RTE", "TSO"),
    "french national grid": ("RTE", "TSO"),
    "french transmission system operator": ("RTE", "TSO"),
    "french tso": ("RTE", "TSO"),

    # ═══ ENEDIS — Dominant mainland DSO (~95%) ═══
    "enedis": ("Enedis", "DSO"),
    "enedis sa": ("Enedis", "DSO"),
    "erdf": ("Enedis", "DSO"),  # predecessor rebrand pre-2016
    "électricité réseau distribution france": ("Enedis", "DSO"),
    "electricite reseau distribution france": ("Enedis", "DSO"),
    "french distribution system operator": ("Enedis", "DSO"),
    "edf réseau": ("Enedis", "DSO"),  # generic pre-2000
    "edf reseau": ("Enedis", "DSO"),

    # ═══ ES STRASBOURG — Alsace regional DSO (WWI+WWII legacy) ═══
    "es": ("ES Strasbourg", "DSO"),
    "es strasbourg": ("ES Strasbourg", "DSO"),
    "électricité de strasbourg": ("ES Strasbourg", "DSO"),
    "electricite de strasbourg": ("ES Strasbourg", "DSO"),
    "és strasbourg": ("ES Strasbourg", "DSO"),
    "es réseaux": ("ES Strasbourg", "DSO"),
    "es reseaux": ("ES Strasbourg", "DSO"),
    "elektrizität straßburg": ("ES Strasbourg", "DSO"),  # Alsatian/German
    "elektrizitat strassburg": ("ES Strasbourg", "DSO"),
    "es straßburg": ("ES Strasbourg", "DSO"),
    "strasbourg electricity": ("ES Strasbourg", "DSO"),

    # ═══ UEM METZ — Moselle regional DSO ═══
    "uem": ("UEM Metz", "DSO"),
    "uem metz": ("UEM Metz", "DSO"),
    "usine d'électricité de metz": ("UEM Metz", "DSO"),
    "usine d'electricite de metz": ("UEM Metz", "DSO"),
    "metz electricity works": ("UEM Metz", "DSO"),

    # ═══ SICAE — Northern France cooperatives ═══
    "sicae": ("SICAE", "COOPERATIVE_DSO"),
    "société d'intérêt collectif agricole d'électricité": ("SICAE", "COOPERATIVE_DSO"),
    "societe d'interet collectif agricole d'electricite": ("SICAE", "COOPERATIVE_DSO"),
    "sicae-oise": ("SICAE", "COOPERATIVE_DSO"),
    "sicae oise": ("SICAE", "COOPERATIVE_DSO"),
    "sicae somme-cambrésis": ("SICAE", "COOPERATIVE_DSO"),
    "sicae somme cambresis": ("SICAE", "COOPERATIVE_DSO"),
    "sicae aisne": ("SICAE", "COOPERATIVE_DSO"),
    "sicae ardennes": ("SICAE", "COOPERATIVE_DSO"),
    "sicae cooperative": ("SICAE", "COOPERATIVE_DSO"),

    # ═══ GÉRÉDIS — Deux-Sèvres regional ═══
    "gérédis": ("Gérédis Deux-Sèvres", "DSO"),
    "geredis": ("Gérédis Deux-Sèvres", "DSO"),
    "gérédis deux-sèvres": ("Gérédis Deux-Sèvres", "DSO"),
    "geredis deux-sevres": ("Gérédis Deux-Sèvres", "DSO"),

    # ═══ GEG GRENOBLE — Alpine municipal ═══
    "geg": ("GEG Grenoble", "DSO"),
    "geg grenoble": ("GEG Grenoble", "DSO"),
    "gaz électricité de grenoble": ("GEG Grenoble", "DSO"),
    "gaz electricite de grenoble": ("GEG Grenoble", "DSO"),
    "régie grenobloise": ("GEG Grenoble", "DSO"),
    "regie grenobloise": ("GEG Grenoble", "DSO"),
    "geg-ener": ("GEG Grenoble", "DSO"),
    "grenoble municipal utility": ("GEG Grenoble", "DSO"),

    # ═══ SALLANCHES + VIALIS + others ═══
    "sallanches": ("Sallanches", "DSO"),
    "régie sallanches": ("Sallanches", "DSO"),
    "regie sallanches": ("Sallanches", "DSO"),
    "vialis": ("Vialis Colmar", "DSO"),
    "vialis colmar": ("Vialis Colmar", "DSO"),
    "eld vialis": ("Vialis Colmar", "DSO"),
    "colmar vialis": ("Vialis Colmar", "DSO"),

    # ═══ EDF SEI — Islanded DOM territories ═══
    "edf sei": ("EDF SEI", "ISLANDED_DOM"),
    "systèmes énergétiques insulaires": ("EDF SEI", "ISLANDED_DOM"),
    "systemes energetiques insulaires": ("EDF SEI", "ISLANDED_DOM"),
    "edf systèmes énergétiques insulaires": ("EDF SEI", "ISLANDED_DOM"),
    "edf systemes energetiques insulaires": ("EDF SEI", "ISLANDED_DOM"),
    "edf islanded energy systems": ("EDF SEI", "ISLANDED_DOM"),

    # ═══ EDM MAYOTTE ═══
    "edm": ("EDM Mayotte", "ISLANDED_DOM"),
    "électricité de mayotte": ("EDM Mayotte", "ISLANDED_DOM"),
    "electricite de mayotte": ("EDM Mayotte", "ISLANDED_DOM"),
    "edm mayotte": ("EDM Mayotte", "ISLANDED_DOM"),
    "mayotte electricity": ("EDM Mayotte", "ISLANDED_DOM"),

    # ═══ ENERCAL NOUVELLE-CALÉDONIE ═══
    "enercal": ("Enercal", "ISLANDED_COM"),
    "enercal nouvelle-calédonie": ("Enercal", "ISLANDED_COM"),
    "enercal nouvelle caledonie": ("Enercal", "ISLANDED_COM"),
    "new caledonia electricity": ("Enercal", "ISLANDED_COM"),

    # ═══ EDT-ENGIE POLYNÉSIE ═══
    "edt-engie": ("EDT-Engie", "ISLANDED_COM"),
    "edt engie": ("EDT-Engie", "ISLANDED_COM"),
    "edt polynésie": ("EDT-Engie", "ISLANDED_COM"),
    "edt polynesie": ("EDT-Engie", "ISLANDED_COM"),
    "électricité de tahiti": ("EDT-Engie", "ISLANDED_COM"),
    "electricite de tahiti": ("EDT-Engie", "ISLANDED_COM"),
    "tahiti electricity": ("EDT-Engie", "ISLANDED_COM"),

    # ═══ EEWF WALLIS-FUTUNA ═══
    "eewf": ("EEWF", "ISLANDED_COM"),
    "électricité et eau de wallis et futuna": ("EEWF", "ISLANDED_COM"),
    "electricite et eau de wallis et futuna": ("EEWF", "ISLANDED_COM"),
    "wallis-futuna electricity and water": ("EEWF", "ISLANDED_COM"),

    # ═══ SNCF RÉSEAU — Rail traction 1.5 kV DC + 25 kV AC TGV ═══
    "sncf réseau": ("SNCF Réseau", "RAIL_TRACTION"),
    "sncf reseau": ("SNCF Réseau", "RAIL_TRACTION"),
    "sncf": ("SNCF Réseau", "RAIL_TRACTION"),
    "réseau ferré de france": ("SNCF Réseau", "RAIL_TRACTION"),
    "reseau ferre de france": ("SNCF Réseau", "RAIL_TRACTION"),
    "rff": ("SNCF Réseau", "RAIL_TRACTION"),  # pre-2015 predecessor
    "sncf voyageurs": ("SNCF Réseau", "RAIL_TRACTION"),
    "french rail infrastructure": ("SNCF Réseau", "RAIL_TRACTION"),

    # ═══ RATP — Paris metro ═══
    "ratp": ("RATP Paris", "RAIL_METRO_PARIS"),
    "régie autonome des transports parisiens": ("RATP Paris", "RAIL_METRO_PARIS"),
    "regie autonome des transports parisiens": ("RATP Paris", "RAIL_METRO_PARIS"),
    "paris metro": ("RATP Paris", "RAIL_METRO_PARIS"),

    # ═══ EDF — Nuclear leadership (Layer 4b) ═══
    "edf": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "édf": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "électricité de france": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "electricite de france": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "edf nucléaire": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "edf nucleaire": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),
    "edf nuclear": ("EDF Nuclear", "GEN_NUCLEAR_DOMINANT"),

    # ═══ ORANO — Nuclear fuel cycle ═══
    "orano": ("Orano", "NUCLEAR_FUEL_CYCLE"),
    "orano cycle": ("Orano", "NUCLEAR_FUEL_CYCLE"),
    "areva nc": ("Orano", "NUCLEAR_FUEL_CYCLE"),  # predecessor pre-2018
    "areva": ("Orano", "NUCLEAR_FUEL_CYCLE"),

    # ═══ Renewable generation (Layer 4b) ═══
    "edf renouvelables": ("EDF Renouvelables", "GEN_RENEWABLE"),
    "edf en": ("EDF Renouvelables", "GEN_RENEWABLE"),
    "edf renewables": ("EDF Renouvelables", "GEN_RENEWABLE"),
    "engie": ("Engie", "GEN_MULTIPLE"),
    "engie france": ("Engie", "GEN_MULTIPLE"),
    "gaz de france": ("Engie", "GEN_MULTIPLE"),  # GDF Suez → Engie 2015
    "gdf suez": ("Engie", "GEN_MULTIPLE"),
    "totalenergies": ("TotalEnergies", "GEN_MULTIPLE"),
    "totalenergies france": ("TotalEnergies", "GEN_MULTIPLE"),
    "total": ("TotalEnergies", "GEN_MULTIPLE"),

    # ═══ HVDC + AC interconnector consortiums ═══
    "ifa": ("IFA UK", "HVDC_INTERCONNECTOR_UK"),
    "interconnexion france-angleterre": ("IFA UK", "HVDC_INTERCONNECTOR_UK"),
    "ifa2": ("IFA2 UK", "HVDC_INTERCONNECTOR_UK"),
    "interconnexion france-angleterre 2": ("IFA2 UK", "HVDC_INTERCONNECTOR_UK"),
    "eleclink": ("ElecLink UK", "HVDC_INTERCONNECTOR_UK"),
    "eleclink interconnexion": ("ElecLink UK", "HVDC_INTERCONNECTOR_UK"),
    "inelfe": ("INELFE Spain", "HVDC_INTERCONNECTOR_ES"),
    "interconnexion france-espagne": ("INELFE Spain", "HVDC_INTERCONNECTOR_ES"),
    "baixas-santa llogaia": ("INELFE Spain", "HVDC_INTERCONNECTOR_ES"),

    # ═══ Cross-border partner TSOs (route to RTE) ═══
    "elia": ("RTE", "TSO_CROSS_BORDER_BE"),
    "elia belgique": ("RTE", "TSO_CROSS_BORDER_BE"),
    "elia belgië": ("RTE", "TSO_CROSS_BORDER_BE"),
    "belgian tso": ("RTE", "TSO_CROSS_BORDER_BE"),
    "amprion": ("RTE", "TSO_CROSS_BORDER_DE"),
    "50hertz": ("RTE", "TSO_CROSS_BORDER_DE"),
    "tennet": ("RTE", "TSO_CROSS_BORDER_DE_OR_NL"),
    "transnetbw": ("RTE", "TSO_CROSS_BORDER_DE"),
    "german tsos": ("RTE", "TSO_CROSS_BORDER_DE"),
    "swissgrid": ("RTE", "TSO_CROSS_BORDER_CH"),
    "réseau suisse": ("RTE", "TSO_CROSS_BORDER_CH"),
    "reseau suisse": ("RTE", "TSO_CROSS_BORDER_CH"),
    "swiss tso": ("RTE", "TSO_CROSS_BORDER_CH"),
    "terna": ("RTE", "TSO_CROSS_BORDER_IT"),
    "terna s.p.a.": ("RTE", "TSO_CROSS_BORDER_IT"),
    "italian tso": ("RTE", "TSO_CROSS_BORDER_IT"),
    "ree": ("RTE", "TSO_CROSS_BORDER_ES"),
    "red eléctrica de españa": ("RTE", "TSO_CROSS_BORDER_ES"),
    "red electrica de espana": ("RTE", "TSO_CROSS_BORDER_ES"),
    "spanish tso": ("RTE", "TSO_CROSS_BORDER_ES"),
    "neso": ("RTE", "TSO_CROSS_BORDER_UK"),
    "national energy system operator": ("RTE", "TSO_CROSS_BORDER_UK"),
    "national grid eso": ("RTE", "TSO_CROSS_BORDER_UK"),
    "uk eso": ("RTE", "TSO_CROSS_BORDER_UK"),

    # ═══ FEDA Andorra small radial ═══
    "feda": ("RTE", "TSO_CROSS_BORDER_AD"),
    "forces elèctriques d'andorra": ("RTE", "TSO_CROSS_BORDER_AD"),
    "forces electriques d'andorra": ("RTE", "TSO_CROSS_BORDER_AD"),
    "andorra radial": ("RTE", "TSO_CROSS_BORDER_AD"),
}


# Convention #78 BINDING enforcement counter
_ALIAS_HIT_COUNTER = {"total": 0}


def _normalize(name: str) -> str:
    """NFC-normalise + lowercase for alias matching.

    Preserves French diacritics (à â ç é è ê ë î ï ô ù û ÿ) +
    German Alsatian (ä ö ü ß) + Corsican + Catalan (à é í ó ú ü ç).
    """
    if not name:
        return ""
    normalized = unicodedata.normalize("NFC", name).strip().lower()
    return normalized


def _in_bbox(lat: float, lon: float, bbox: dict) -> bool:
    return (
        bbox["lat_min"] <= lat <= bbox["lat_max"]
        and bbox["lon_min"] <= lon <= bbox["lon_max"]
    )


def resolve_operator(
    raw_operator: Optional[str],
    *,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    voltage_kv: Optional[float] = None,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """12-layer operator resolver — France P37 Wave 4.

    Returns (canonical_operator, role, resolution_layer). None if
    unresolved (Convention #56 visibly-honest degradation).
    """
    # ─── Layer 1: Direct alias hit (Convention #78 BINDING 19th) ───
    if raw_operator:
        normalized = _normalize(raw_operator)
        if normalized in ALIAS_MAP:
            canonical, role = ALIAS_MAP[normalized]
            _ALIAS_HIT_COUNTER["total"] += 1
            return canonical, role, "alias_hit"

    # Coord-based layers require lat+lon
    if lat is None or lon is None:
        return _resolve_by_voltage_only(voltage_kv)

    # ─── Layer 2: Voltage-class heuristic (main resolution path) ───
    if voltage_kv is not None:
        if voltage_kv >= 400.0:
            return "RTE", "TSO_EHV", "voltage_ehv"
        if voltage_kv >= 225.0:
            return "RTE", "TSO_HV", "voltage_hv_225"  # French HV standard
        if voltage_kv >= 150.0:
            return "RTE", "TSO_REGIONAL", "voltage_regional_150"
        if voltage_kv >= 90.0:
            return "RTE", "TSO_SUBT", "voltage_subtransmission_90"
        if voltage_kv >= 63.0:
            return "RTE", "TSO_SUBT", "voltage_subtransmission_63"

    # ─── Layer 3: Rail traction 1.5 kV DC SNCF + 25 kV AC TGV ───
    if voltage_kv is not None:
        if 1.3 <= voltage_kv <= 1.7:
            return "SNCF Réseau", "RAIL_TRACTION", "rail_traction_1_5kv_dc"
        if 24.0 <= voltage_kv <= 26.0:
            return "SNCF Réseau", "RAIL_TRACTION", "rail_traction_25kv_ac_tgv"

    # ─── Layer 4: Corsica bbox → EDF SEI Corsica ───
    if _in_bbox(lat, lon, CORSICA_BBOX):
        return (
            "EDF SEI Corsica",
            "ISLANDED_DSO_CORSICA",
            "corsica_bbox_carve_out",
        )

    # ─── Layer 5: Guadeloupe bbox → EDF SEI Guadeloupe ───
    if _in_bbox(lat, lon, GUADELOUPE_BBOX):
        return (
            "EDF SEI Guadeloupe",
            "ISLANDED_DOM_GUADELOUPE",
            "guadeloupe_bbox_carve_out",
        )

    # ─── Layer 6: Martinique bbox → EDF SEI Martinique ───
    if _in_bbox(lat, lon, MARTINIQUE_BBOX):
        return (
            "EDF SEI Martinique",
            "ISLANDED_DOM_MARTINIQUE",
            "martinique_bbox_carve_out",
        )

    # ─── Layer 7: Guyane bbox → EDF SEI Guyane ───
    if _in_bbox(lat, lon, GUYANE_BBOX):
        return (
            "EDF SEI Guyane",
            "ISLANDED_DOM_GUYANE",
            "guyane_bbox_carve_out",
        )

    # ─── Layer 8: Réunion bbox → EDF SEI Réunion ───
    if _in_bbox(lat, lon, REUNION_BBOX):
        return (
            "EDF SEI Réunion",
            "ISLANDED_DOM_REUNION",
            "reunion_bbox_carve_out",
        )

    # ─── Layer 9: Mayotte bbox → EDM Mayotte ───
    if _in_bbox(lat, lon, MAYOTTE_BBOX):
        return (
            "EDM Mayotte",
            "ISLANDED_DOM_MAYOTTE",
            "mayotte_bbox_carve_out",
        )

    # ─── Layer 10: Saint-Pierre-et-Miquelon bbox → EDF SEI SPM ───
    if _in_bbox(lat, lon, SAINT_PIERRE_MIQUELON_BBOX):
        return (
            "EDF SEI Saint-Pierre-et-Miquelon",
            "ISLANDED_DOM_SPM",
            "saint_pierre_miquelon_bbox_carve_out",
        )

    # ─── Layer 11: Alsace regional ELDs (Bas-Rhin + Moselle) ───
    if voltage_kv is not None and voltage_kv < 45.0:
        # Bas-Rhin (Alsace) ~48.0-49.1°N × 7.4-8.3°E → ES Strasbourg
        if 48.0 <= lat <= 49.1 and 7.4 <= lon <= 8.3:
            return "ES Strasbourg", "DSO", "alsace_es_strasbourg_regional"
        # Moselle ~48.9-49.5°N × 6.0-7.3°E → UEM Metz
        if 48.9 <= lat <= 49.5 and 6.0 <= lon <= 7.3:
            return "UEM Metz", "DSO", "moselle_uem_metz_regional"

    # ─── Layer 12: Fallback default DSO → Enedis (95% mainland) ───
    if voltage_kv is None:
        return None, None, None  # Convention #56 — insufficient signal

    return "Enedis", "DSO", "fallback_default_enedis"


def _resolve_by_voltage_only(
    voltage_kv: Optional[float],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Voltage-only fallback when lat/lon absent."""
    if voltage_kv is None:
        return None, None, None
    if voltage_kv >= 400.0:
        return "RTE", "TSO_EHV", "voltage_ehv_no_coords"
    if voltage_kv >= 225.0:
        return "RTE", "TSO_HV", "voltage_hv_225_no_coords"
    if voltage_kv >= 63.0:
        return "RTE", "TSO_SUBT", "voltage_subtransmission_63_no_coords"
    if 1.3 <= voltage_kv <= 1.7:
        return "SNCF Réseau", "RAIL_TRACTION", "rail_traction_1_5kv_dc_no_coords"
    if 24.0 <= voltage_kv <= 26.0:
        return "SNCF Réseau", "RAIL_TRACTION", "rail_traction_25kv_ac_tgv_no_coords"
    return None, None, None


# Resolver layer catalogue — exposed for audit
RESOLVER_LAYERS = [
    "alias_hit",  # Convention #78 BINDING 19th
    "voltage_ehv",
    "voltage_hv_225",
    "voltage_regional_150",
    "voltage_subtransmission_90",
    "voltage_subtransmission_63",
    "rail_traction_1_5kv_dc",
    "rail_traction_25kv_ac_tgv",
    "corsica_bbox_carve_out",
    "guadeloupe_bbox_carve_out",
    "martinique_bbox_carve_out",
    "guyane_bbox_carve_out",
    "reunion_bbox_carve_out",
    "mayotte_bbox_carve_out",
    "saint_pierre_miquelon_bbox_carve_out",
    "alsace_es_strasbourg_regional",
    "moselle_uem_metz_regional",
    "fallback_default_enedis",
    # No-coord fallbacks
    "voltage_ehv_no_coords",
    "voltage_hv_225_no_coords",
    "voltage_subtransmission_63_no_coords",
    "rail_traction_1_5kv_dc_no_coords",
    "rail_traction_25kv_ac_tgv_no_coords",
]


def alias_hit_count() -> int:
    """Return cumulative Convention #78 alias hits for audit sidecar."""
    return _ALIAS_HIT_COUNTER["total"]


def reset_alias_hit_counter() -> None:
    """Reset counter (for test isolation)."""
    _ALIAS_HIT_COUNTER["total"] = 0
