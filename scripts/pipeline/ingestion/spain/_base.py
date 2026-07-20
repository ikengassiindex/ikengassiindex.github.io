"""Spain P36 Wave 4 — Convention #78 BINDING 18th enforcement.

6-language alias map (Spanish Castellano + English + Catalan Català +
Galician Galego + Basque Euskara + Aranese Occitan). 3rd HIGHEST
cohort-wide language count after Italy 8 (Italian+English+German+
French+Slovenian+Ladin+Friulian+Sardinian).

Madrid §4bis.5 13th enforcement 2-way (Naturgy inner + Iberdrola i-DE
outer). Balearic + Canary + Ceuta + Melilla bbox carve-outs.

9-layer resolver:
  1. Direct alias hit (Convention #78 BINDING 18th)
  2. Madrid Naturgy §4bis.5 13th part-a
  3. Madrid Iberdrola i-DE §4bis.5 13th part-b
  4. Voltage-class heuristic (EHV/HV/subT/MV)
  5. Rail traction 3 kV DC RENFE + 25 kV AC AVE
  6. Balearic bbox → Endesa Baleares
  7. Canary bbox → Endesa Canarias
  8. Ceuta/Melilla bbox → Endesa exclaves
  9. Regional utility coord routing (Iberdrola / Endesa / Naturgy / EDP HC / Viesgo)

Sub-conventions preserved: #7 + #23 + #56 + #60 + #78 BINDING.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Bounding boxes — Discipline #36 + §4bis.5 + archipelago carve-outs
# ─────────────────────────────────────────────────────────────

# Spain master bbox (mainland + Balearic + Canary + Ceuta + Melilla)
# Peninsula: 35.99°N Tarifa → 43.79°N Estaca de Bares
# Canaries: 27.63°N El Hierro → 29.42°N Lanzarote (~1,700 km SW mainland)
# Includes: -18.16°W Canarias west → 4.33°E Cap de Creus east
SPAIN_MASTER_BBOX = {
    "lat_min": 27.63,
    "lat_max": 43.79,
    "lon_min": -18.16,
    "lon_max": 4.33,
}

# Mainland Spain (Peninsula + Balearic)
MAINLAND_BBOX = {
    "lat_min": 35.99,
    "lat_max": 43.79,
    "lon_min": -9.30,
    "lon_max": 4.33,
}

# Balearic Islands (Mallorca + Menorca + Ibiza + Formentera)
BALEARIC_BBOX = {
    "lat_min": 38.65,   # Formentera
    "lat_max": 40.10,   # Menorca north
    "lon_min": 1.15,    # Ibiza west
    "lon_max": 4.35,    # Menorca east
    "operator_canonical": "Endesa Baleares",
    "role": "DSO_ISLAND_ENDESA",
}

# Canary Islands (7 main + minor)
CANARY_BBOX = {
    "lat_min": 27.63,   # El Hierro south
    "lat_max": 29.42,   # Lanzarote north
    "lon_min": -18.16,  # El Hierro west
    "lon_max": -13.42,  # Lanzarote east
    "operator_canonical": "Endesa Canarias",
    "role": "DSO_ISLAND_ENDESA",
}

# Ceuta (North Africa Spanish exclave)
CEUTA_BBOX = {
    "lat_min": 35.87,
    "lat_max": 35.92,
    "lon_min": -5.38,
    "lon_max": -5.28,
    "operator_canonical": "Endesa Ceuta",
    "role": "DSO_EXCLAVE_ENDESA",
}

# Melilla (North Africa Spanish exclave)
MELILLA_BBOX = {
    "lat_min": 35.27,
    "lat_max": 35.31,
    "lon_min": -2.97,
    "lon_max": -2.92,
    "operator_canonical": "Endesa Melilla",
    "role": "DSO_EXCLAVE_ENDESA",
}

# Convention #78 §4bis.5 13th enforcement — Madrid
# 2-way DSO split for Madrid metropolitan area (~6.7M population):
# Naturgy dominant inner metropolitan (via Unión Fenosa historical
# concession) + Iberdrola i-DE outer metropolitan + some inner overlap
MADRID_NATURGY_BBOX = {
    "lat_min": 40.35,
    "lat_max": 40.55,
    "lon_min": -3.85,
    "lon_max": -3.60,
    "operator_canonical": "Naturgy Madrid",
    "role": "DSO",
}

MADRID_IBERDROLA_BBOX = {
    "lat_min": 40.30,
    "lat_max": 40.65,
    "lon_min": -3.95,
    "lon_max": -3.50,
    "operator_canonical": "Iberdrola i-DE Madrid",
    "role": "DSO",
}

# Regional utility approximate coord routing bboxes (Layer 9 fallback)
# Non-overlapping majority coverage per DSO market territory
REGIONAL_UTILITY_TERRITORIES = {
    "iberdrola_i_de_north": {
        "lat_min": 42.50,  # País Vasco + Navarra
        "lat_max": 43.60,
        "lon_min": -3.30,
        "lon_max": -1.30,
        "operator_canonical": "Iberdrola i-DE",
        "role": "DSO",
    },
    "iberdrola_i_de_east": {
        "lat_min": 38.00,  # Valencia + Castellón + Alicante
        "lat_max": 40.80,
        "lon_min": -1.90,
        "lon_max": 0.60,
        "operator_canonical": "Iberdrola i-DE",
        "role": "DSO",
    },
    "iberdrola_i_de_center_south": {
        "lat_min": 36.80,  # Murcia + Castilla-La Mancha + Extremadura
        "lat_max": 40.20,
        "lon_min": -7.60,
        "lon_max": -1.40,
        "operator_canonical": "Iberdrola i-DE",
        "role": "DSO",
    },
    "endesa_cataluna": {
        "lat_min": 40.50,
        "lat_max": 42.90,
        "lon_min": 0.15,
        "lon_max": 3.40,
        "operator_canonical": "Endesa",
        "role": "DSO",
    },
    "endesa_andalucia_aragon": {
        "lat_min": 35.90,  # Andalucía
        "lat_max": 42.90,  # Aragón north
        "lon_min": -7.60,
        "lon_max": 0.90,
        "operator_canonical": "Endesa",
        "role": "DSO",
    },
    "naturgy_castilla_leon": {
        "lat_min": 40.30,
        "lat_max": 43.50,
        "lon_min": -7.10,
        "lon_max": -1.75,
        "operator_canonical": "Naturgy",
        "role": "DSO",
    },
    "naturgy_galicia": {
        "lat_min": 41.80,
        "lat_max": 43.80,
        "lon_min": -9.30,
        "lon_max": -6.75,
        "operator_canonical": "Naturgy",
        "role": "DSO",
    },
    "edp_hc_asturias": {
        "lat_min": 43.00,
        "lat_max": 43.80,
        "lon_min": -7.20,
        "lon_max": -4.50,
        "operator_canonical": "EDP HC Energía",
        "role": "DSO",
    },
    "viesgo_cantabria": {
        "lat_min": 42.90,
        "lat_max": 43.55,
        "lon_min": -4.85,
        "lon_max": -3.10,
        "operator_canonical": "Viesgo",
        "role": "DSO",
    },
}


# ─────────────────────────────────────────────────────────────
# Convention #78 BINDING 18TH ENFORCEMENT — 6-language ALIAS_MAP
# ─────────────────────────────────────────────────────────────
# ~140 alias entries. Spanish + Catalan + Galician + Basque + Aranese
# diacritics preserved: á é í ó ú ñ ç à è ï ò ü l·l ú ñ.

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ═══ REE / REDEIA — National TSO ═══
    "ree": ("REE", "TSO"),
    "red eléctrica de españa": ("REE", "TSO"),
    "red electrica de espana": ("REE", "TSO"),
    "red eléctrica": ("REE", "TSO"),
    "red electrica": ("REE", "TSO"),
    "redeia": ("REE", "TSO"),
    "redeia corporación": ("REE", "TSO"),
    "redeia corporacion": ("REE", "TSO"),
    "spanish national grid": ("REE", "TSO"),
    "spanish transmission system operator": ("REE", "TSO"),
    "spanish tso": ("REE", "TSO"),
    # Catalan
    "xarxa elèctrica d'espanya": ("REE", "TSO"),
    "xarxa electrica d'espanya": ("REE", "TSO"),
    # Galician
    "rede eléctrica de españa": ("REE", "TSO"),
    "rede electrica de espana": ("REE", "TSO"),
    # Basque
    "espainiako sare elektrikoa": ("REE", "TSO"),

    # ═══ IBERDROLA i-DE — Largest DSO 40% ═══
    "i-de": ("Iberdrola i-DE", "DSO"),
    "ide": ("Iberdrola i-DE", "DSO"),
    "iberdrola i-de": ("Iberdrola i-DE", "DSO"),
    "iberdrola i-de redes": ("Iberdrola i-DE", "DSO"),
    "iberdrola distribución": ("Iberdrola i-DE", "DSO"),  # predecessor
    "iberdrola distribucion": ("Iberdrola i-DE", "DSO"),
    "iberdrola distribución españa": ("Iberdrola i-DE", "DSO"),
    "iberdrola distribucion espana": ("Iberdrola i-DE", "DSO"),
    "iberdrola españa": ("Iberdrola i-DE", "DSO"),
    "iberdrola espana": ("Iberdrola i-DE", "DSO"),
    "iberdrola": ("Iberdrola i-DE", "DSO"),  # generic
    "iberdrola sa": ("Iberdrola i-DE", "DSO"),
    "iberdrola distribution": ("Iberdrola i-DE", "DSO"),
    # Catalan
    "iberdrola distribució": ("Iberdrola i-DE", "DSO"),
    "iberdrola distribucio": ("Iberdrola i-DE", "DSO"),
    # Basque
    "iberdrola banaketa": ("Iberdrola i-DE", "DSO"),

    # ═══ ENDESA — Second largest DSO 30% (Enel Italian parent) ═══
    "endesa": ("Endesa", "DSO"),
    "e-distribución": ("Endesa", "DSO"),
    "e-distribucion": ("Endesa", "DSO"),
    "edistribucion": ("Endesa", "DSO"),
    "e distribucion": ("Endesa", "DSO"),
    "endesa distribución": ("Endesa", "DSO"),
    "endesa distribucion": ("Endesa", "DSO"),
    "endesa redes digitales": ("Endesa", "DSO"),
    "endesa distribution": ("Endesa", "DSO"),
    # Catalan
    "e-distribució": ("Endesa", "DSO"),
    "e-distribucio": ("Endesa", "DSO"),

    # ═══ NATURGY / UFD — Third largest DSO Madrid+Castilla+Galicia ═══
    "naturgy": ("Naturgy", "DSO"),
    "ufd": ("Naturgy", "DSO"),
    "naturgy ufd": ("Naturgy", "DSO"),
    "naturgy electricidad españa": ("Naturgy", "DSO"),
    "naturgy electricidad espana": ("Naturgy", "DSO"),
    "unión fenosa distribución": ("Naturgy", "DSO"),  # predecessor
    "union fenosa distribucion": ("Naturgy", "DSO"),
    "unión fenosa": ("Naturgy", "DSO"),
    "union fenosa": ("Naturgy", "DSO"),
    "gas natural fenosa distribución": ("Naturgy", "DSO"),
    "gas natural fenosa distribucion": ("Naturgy", "DSO"),
    "gas natural fenosa": ("Naturgy", "DSO"),
    "naturgy electricity spain": ("Naturgy", "DSO"),

    # ═══ EDP HC ENERGÍA — Asturias regional ═══
    "edp hc energía": ("EDP HC Energía", "DSO"),
    "edp hc energia": ("EDP HC Energía", "DSO"),
    "edp hidrocantábrico": ("EDP HC Energía", "DSO"),
    "edp hidrocantabrico": ("EDP HC Energía", "DSO"),
    "hc energía": ("EDP HC Energía", "DSO"),
    "hc energia": ("EDP HC Energía", "DSO"),
    "hidrocantábrico": ("EDP HC Energía", "DSO"),
    "hidrocantabrico": ("EDP HC Energía", "DSO"),
    "edp españa": ("EDP HC Energía", "DSO"),
    "edp espana": ("EDP HC Energía", "DSO"),
    "edp spain": ("EDP HC Energía", "DSO"),

    # ═══ VIESGO — Cantabria + Northern Castilla (TotalEnergies parent) ═══
    "viesgo": ("Viesgo", "DSO"),
    "grupo viesgo": ("Viesgo", "DSO"),
    "viesgo distribución": ("Viesgo", "DSO"),
    "viesgo distribucion": ("Viesgo", "DSO"),

    # ═══ Small regional/municipal DSOs ═══
    "grupo energético del sur": ("Grupo Energético del Sur", "DSO"),
    "grupo energetico del sur": ("Grupo Energético del Sur", "DSO"),
    "ges": ("Grupo Energético del Sur", "DSO"),
    "distribuidora eléctrica bermeo": ("Distribuidora Eléctrica Bermeo", "DSO"),
    "distribuidora electrica bermeo": ("Distribuidora Eléctrica Bermeo", "DSO"),
    # Basque
    "bermeoko elektrizitate banatzailea": ("Distribuidora Eléctrica Bermeo", "DSO"),

    # ═══ ADIF — Rail traction 3 kV DC + 25 kV AC AVE ═══
    "adif": ("ADIF", "RAIL_TRACTION"),
    "administrador de infraestructuras ferroviarias": ("ADIF", "RAIL_TRACTION"),
    "adif alta velocidad": ("ADIF", "RAIL_TRACTION"),
    "spanish rail infrastructure administrator": ("ADIF", "RAIL_TRACTION"),
    # Catalan
    "administrador d'infraestructures ferroviàries": ("ADIF", "RAIL_TRACTION"),

    # ═══ Metro operators ═══
    "metro de madrid": ("Metro de Madrid", "RAIL_METRO_MADRID"),
    "metro madrid": ("Metro de Madrid", "RAIL_METRO_MADRID"),
    "mdm": ("Metro de Madrid", "RAIL_METRO_MADRID"),
    "madrid metro": ("Metro de Madrid", "RAIL_METRO_MADRID"),
    "tmb": ("TMB Barcelona Metro", "RAIL_METRO_BARCELONA"),
    "transports metropolitans de barcelona": ("TMB Barcelona Metro", "RAIL_METRO_BARCELONA"),
    "metro de barcelona": ("TMB Barcelona Metro", "RAIL_METRO_BARCELONA"),
    "metro barcelona": ("TMB Barcelona Metro", "RAIL_METRO_BARCELONA"),
    "barcelona metro": ("TMB Barcelona Metro", "RAIL_METRO_BARCELONA"),

    # ═══ Renewable generation (Layer 4b) ═══
    "iberdrola renovables": ("Iberdrola Renovables", "GEN_RENEWABLE"),
    "iberdrola renewables": ("Iberdrola Renovables", "GEN_RENEWABLE"),
    "acciona energía": ("Acciona Energía", "GEN_RENEWABLE"),
    "acciona energia": ("Acciona Energía", "GEN_RENEWABLE"),
    "acciona": ("Acciona Energía", "GEN_RENEWABLE"),
    "acciona energy": ("Acciona Energía", "GEN_RENEWABLE"),
    "naturgy renovables": ("Naturgy Renovables", "GEN_RENEWABLE"),

    # ═══ HVDC + AC interconnector consortiums ═══
    "inelfe": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "interconnexion france-espagne": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "interconexión france-espagne": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "interconexion francia-espana": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "baixas-santa llogaia": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "france-spain interconnection": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    # Catalan
    "interconnexió frança-espanya": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "interconnexio franca-espanya": ("INELFE", "HVDC_INTERCONNECTOR_FR"),
    "tarifa-fardioua hvdc": ("Spain-Morocco HVDC", "HVDC_INTERCONNECTOR_MA"),
    "españa-marruecos hvdc": ("Spain-Morocco HVDC", "HVDC_INTERCONNECTOR_MA"),
    "espana-marruecos hvdc": ("Spain-Morocco HVDC", "HVDC_INTERCONNECTOR_MA"),
    "spain-morocco interconnection": ("Spain-Morocco HVDC", "HVDC_INTERCONNECTOR_MA"),
    "cometa": ("Cometa HVDC", "HVDC_INTERCONNECTOR_BALEARIC"),
    "cometa hvdc": ("Cometa HVDC", "HVDC_INTERCONNECTOR_BALEARIC"),
    "peninsula-mallorca": ("Cometa HVDC", "HVDC_INTERCONNECTOR_BALEARIC"),

    # ═══ Cross-border partner TSOs (route to REE) ═══
    "ren": ("REE", "TSO_CROSS_BORDER_PT"),
    "redes energéticas nacionais": ("REE", "TSO_CROSS_BORDER_PT"),
    "redes energeticas nacionais": ("REE", "TSO_CROSS_BORDER_PT"),
    "portuguese tso": ("REE", "TSO_CROSS_BORDER_PT"),
    "rte": ("REE", "TSO_CROSS_BORDER_FR"),
    "réseau de transport d'électricité": ("REE", "TSO_CROSS_BORDER_FR"),
    "reseau de transport d'electricite": ("REE", "TSO_CROSS_BORDER_FR"),
    "french tso": ("REE", "TSO_CROSS_BORDER_FR"),
    "onee": ("REE", "TSO_CROSS_BORDER_MA"),
    "office national de l'électricité et de l'eau potable": ("REE", "TSO_CROSS_BORDER_MA"),
    "office national de l'electricite et de l'eau potable": ("REE", "TSO_CROSS_BORDER_MA"),
    "one marruecos": ("REE", "TSO_CROSS_BORDER_MA"),
    "moroccan tso": ("REE", "TSO_CROSS_BORDER_MA"),
    "moroccan national electricity and water office": ("REE", "TSO_CROSS_BORDER_MA"),
    # Andorra small radial
    "feda": ("REE", "TSO_CROSS_BORDER_AD"),
    "forces elèctriques d'andorra": ("REE", "TSO_CROSS_BORDER_AD"),
    "forces electriques d'andorra": ("REE", "TSO_CROSS_BORDER_AD"),
}


# Convention #78 BINDING enforcement counter
_ALIAS_HIT_COUNTER = {"total": 0}


def _normalize(name: str) -> str:
    """NFC-normalise + lowercase for alias matching.

    Preserves Spanish diacritics (á é í ó ú ñ) + Catalan (à è í ï ò
    ú ü ç l·l) + Basque (special chars) + Galician (á é í ó ú ñ ç).
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


def _resolve_regional_utility_by_coord(
    lat: float, lon: float
) -> Optional[tuple[str, str, str]]:
    """Coord-based fallback → regional utility DSO.

    Priority order: smallest-territory first (avoid overlap conflicts).
    """
    territory_order = [
        "viesgo_cantabria",
        "edp_hc_asturias",
        "naturgy_galicia",
        "endesa_cataluna",
        "iberdrola_i_de_north",
        "iberdrola_i_de_east",
        "iberdrola_i_de_center_south",
        "naturgy_castilla_leon",
        "endesa_andalucia_aragon",
    ]
    for name in territory_order:
        territory = REGIONAL_UTILITY_TERRITORIES[name]
        if _in_bbox(lat, lon, territory):
            return (
                territory["operator_canonical"],
                territory["role"],
                f"regional_utility_{name}_coord",
            )
    return None


def resolve_operator(
    raw_operator: Optional[str],
    *,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    voltage_kv: Optional[float] = None,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """9-layer operator resolver — Spain P36 Wave 4.

    Returns (canonical_operator, role, resolution_layer). None if
    unresolved (Convention #56 visibly-honest degradation).
    """
    # ─── Layer 1: Direct alias hit (Convention #78 BINDING 18th) ───
    if raw_operator:
        normalized = _normalize(raw_operator)
        if normalized in ALIAS_MAP:
            canonical, role = ALIAS_MAP[normalized]
            _ALIAS_HIT_COUNTER["total"] += 1
            return canonical, role, "alias_hit"

    # Coord-based layers require lat+lon
    if lat is None or lon is None:
        return _resolve_by_voltage_only(voltage_kv)

    # ─── Layer 2: Madrid Naturgy §4bis.5 13th ───
    if _in_bbox(lat, lon, MADRID_NATURGY_BBOX):
        return "Naturgy Madrid", "DSO", "madrid_naturgy_geofence"

    # ─── Layer 3: Madrid Iberdrola i-DE §4bis.5 13th ───
    if _in_bbox(lat, lon, MADRID_IBERDROLA_BBOX):
        return "Iberdrola i-DE Madrid", "DSO", "madrid_iberdrola_geofence"

    # ─── Layer 4: Voltage-class heuristic ───
    if voltage_kv is not None:
        if voltage_kv >= 400.0:
            return "REE", "TSO_EHV", "voltage_ehv"
        if voltage_kv >= 220.0:
            return "REE", "TSO_HV", "voltage_hv_transmission"
        if voltage_kv >= 132.0:
            return "REE", "TSO_SUBT", "voltage_subtransmission_132"

    # ─── Layer 5: Rail traction 3 kV DC RENFE + 25 kV AC AVE ───
    if voltage_kv is not None:
        if 2.5 <= voltage_kv <= 3.5:
            return "ADIF", "RAIL_TRACTION", "rail_traction_3kv_dc"
        if 24.0 <= voltage_kv <= 26.0:
            return "ADIF", "RAIL_TRACTION", "rail_traction_25kv_ac_ave"

    # ─── Layer 6: Balearic bbox → Endesa Baleares ───
    if _in_bbox(lat, lon, BALEARIC_BBOX):
        return (
            "Endesa Baleares",
            "DSO_ISLAND_ENDESA",
            "balearic_bbox_carve_out",
        )

    # ─── Layer 7: Canary bbox → Endesa Canarias ───
    if _in_bbox(lat, lon, CANARY_BBOX):
        return (
            "Endesa Canarias",
            "DSO_ISLAND_ENDESA",
            "canary_bbox_carve_out",
        )

    # ─── Layer 8: Ceuta/Melilla → Endesa exclave ───
    if _in_bbox(lat, lon, CEUTA_BBOX):
        return "Endesa Ceuta", "DSO_EXCLAVE_ENDESA", "ceuta_bbox_carve_out"
    if _in_bbox(lat, lon, MELILLA_BBOX):
        return "Endesa Melilla", "DSO_EXCLAVE_ENDESA", "melilla_bbox_carve_out"

    # ─── Layer 9: Regional utility coord routing ───
    regional = _resolve_regional_utility_by_coord(lat, lon)
    if regional:
        return regional

    # ─── Fallback: E-Distribuzione-equivalent unspecified default ───
    if voltage_kv is None:
        return None, None, None  # Convention #56 — insufficient signal

    # Default to Iberdrola i-DE (largest by market share)
    return "Iberdrola i-DE", "DSO", "fallback_default_dso"


def _resolve_by_voltage_only(
    voltage_kv: Optional[float],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Voltage-only fallback when lat/lon absent."""
    if voltage_kv is None:
        return None, None, None
    if voltage_kv >= 400.0:
        return "REE", "TSO_EHV", "voltage_ehv_no_coords"
    if voltage_kv >= 220.0:
        return "REE", "TSO_HV", "voltage_hv_transmission_no_coords"
    if voltage_kv >= 132.0:
        return "REE", "TSO_SUBT", "voltage_subtransmission_132_no_coords"
    if 2.5 <= voltage_kv <= 3.5:
        return "ADIF", "RAIL_TRACTION", "rail_traction_3kv_dc_no_coords"
    if 24.0 <= voltage_kv <= 26.0:
        return "ADIF", "RAIL_TRACTION", "rail_traction_25kv_ac_ave_no_coords"
    return None, None, None


# Resolver layer catalogue — exposed for audit
RESOLVER_LAYERS = [
    "alias_hit",  # Convention #78 BINDING 18th
    "madrid_naturgy_geofence",  # §4bis.5 13th part-a
    "madrid_iberdrola_geofence",  # §4bis.5 13th part-b
    "voltage_ehv",
    "voltage_hv_transmission",
    "voltage_subtransmission_132",
    "rail_traction_3kv_dc",
    "rail_traction_25kv_ac_ave",
    "balearic_bbox_carve_out",
    "canary_bbox_carve_out",
    "ceuta_bbox_carve_out",
    "melilla_bbox_carve_out",
    # Regional utility coord-based
    "regional_utility_viesgo_cantabria_coord",
    "regional_utility_edp_hc_asturias_coord",
    "regional_utility_naturgy_galicia_coord",
    "regional_utility_endesa_cataluna_coord",
    "regional_utility_iberdrola_i_de_north_coord",
    "regional_utility_iberdrola_i_de_east_coord",
    "regional_utility_iberdrola_i_de_center_south_coord",
    "regional_utility_naturgy_castilla_leon_coord",
    "regional_utility_endesa_andalucia_aragon_coord",
    "fallback_default_dso",
    # No-coord fallbacks
    "voltage_ehv_no_coords",
    "voltage_hv_transmission_no_coords",
    "voltage_subtransmission_132_no_coords",
    "rail_traction_3kv_dc_no_coords",
    "rail_traction_25kv_ac_ave_no_coords",
]


def alias_hit_count() -> int:
    """Return cumulative Convention #78 alias hits for audit sidecar."""
    return _ALIAS_HIT_COUNTER["total"]


def reset_alias_hit_counter() -> None:
    """Reset counter (for test isolation)."""
    _ALIAS_HIT_COUNTER["total"] = 0
