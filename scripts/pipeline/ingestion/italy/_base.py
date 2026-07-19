"""Italy P34 Wave 4 — Convention #78 BINDING 16th enforcement.

8-language alias map (HIGHEST cohort-wide):
  Italian + English + German South Tyrol + French Aosta Valley +
  Slovenian Trieste + Ladin Dolomites + Friulian + Sardinian

Convention #78 §4bis.5 DUAL 11th + 12th enforcement:
  - Milan 2-way A2A/Unareti + E-Distribuzione geofence
  - Rome 2-way ACEA + E-Distribuzione geofence

10-layer resolver:
  1. Direct alias hit (Convention #78 BINDING 16th)
  2. Milan A2A/Unareti §4bis.5 (11th)
  3. Milan E-Distribuzione §4bis.5 (11th)
  4. Rome ACEA §4bis.5 (12th)
  5. Rome E-Distribuzione §4bis.5 (12th)
  6. Voltage-class heuristic (EHV/HV/subT/MV)
  7. Rail traction 3 kV DC + 25 kV AC
  8. Alpine regional DSO (Edyna/Deval)
  9. Rural low-voltage default → E-Distribuzione
 10. Fallback DSO → E-Distribuzione (85% mainland market)

Sub-conventions preserved: #7 + #23 + #56 + #60 + #78 BINDING.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Bounding boxes — Discipline #36 + §4bis.5 geofences
# ─────────────────────────────────────────────────────────────

# Italy national bbox — mainland + Sicilia + Sardegna + minor islands
# 35.49°N Lampedusa → 47.09°N Vetta d'Italia
# 6.63°E Monte Bianco → 18.52°E Otranto
ITALY_BBOX = {
    "lat_min": 35.49,
    "lat_max": 47.09,
    "lon_min": 6.63,
    "lon_max": 18.52,
}

# Convention #78 §4bis.5 11th enforcement — Milan
# 2-way DSO split for Milan metropolitan area (~3.2M pop):
# A2A/Unareti (inner core, ~1.1M customers) + E-Distribuzione
# (outer metropolitan, ~1.0M customers)
MILAN_A2A_UNARETI_BBOX = {
    "lat_min": 45.35,
    "lat_max": 45.60,
    "lon_min": 9.05,
    "lon_max": 9.30,
    "operator_canonical": "A2A/Unareti Milan",
    "role": "DSO",
}

MILAN_E_DISTRIBUZIONE_BBOX = {
    "lat_min": 45.30,
    "lat_max": 45.65,
    "lon_min": 8.90,
    "lon_max": 9.40,
    "operator_canonical": "E-Distribuzione Milan",
    "role": "DSO",
}

# Convention #78 §4bis.5 12th enforcement — Rome
# 2-way DSO split for Rome metropolitan area (~2.8M pop):
# ACEA (inner Rome ~1.6M) + E-Distribuzione (outer Lazio ~1.4M)
ROME_ACEA_BBOX = {
    "lat_min": 41.75,
    "lat_max": 42.00,
    "lon_min": 12.35,
    "lon_max": 12.65,
    "operator_canonical": "ACEA Rome",
    "role": "DSO",
}

ROME_E_DISTRIBUZIONE_BBOX = {
    "lat_min": 41.60,
    "lat_max": 42.10,
    "lon_min": 12.20,
    "lon_max": 12.90,
    "operator_canonical": "E-Distribuzione Rome/Lazio",
    "role": "DSO",
}


# ─────────────────────────────────────────────────────────────
# Convention #78 BINDING 16TH ENFORCEMENT — 8-language ALIAS_MAP
# ─────────────────────────────────────────────────────────────
# ~150 alias entries across 17 canonical operators.
# Italian diacritics preserved: à è é ì ò ù + German ä ö ü ß +
# French à â ç é è ê î ô + Slovenian č š ž + Ladin ë + Friulian.

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ═══ TERNA — National TSO (state-controlled) ═══
    "terna": ("Terna", "TSO"),
    "terna s.p.a.": ("Terna", "TSO"),
    "terna spa": ("Terna", "TSO"),
    "terna rete elettrica nazionale": ("Terna", "TSO"),
    "terna rete elettrica": ("Terna", "TSO"),
    "italian national grid": ("Terna", "TSO"),
    "italian transmission system operator": ("Terna", "TSO"),
    "italian tso": ("Terna", "TSO"),
    "italienisches nationales stromnetz": ("Terna", "TSO"),  # German
    "réseau électrique national italien": ("Terna", "TSO"),  # French
    "reseau electrique national italien": ("Terna", "TSO"),
    "italijansko nacionalno omrežje": ("Terna", "TSO"),  # Slovenian
    "italijansko nacionalno omrezje": ("Terna", "TSO"),

    # ═══ E-DISTRIBUZIONE — Dominant mainland DSO (~85%) ═══
    "e-distribuzione": ("E-Distribuzione", "DSO"),
    "e-distribuzione s.p.a.": ("E-Distribuzione", "DSO"),
    "e-distribuzione spa": ("E-Distribuzione", "DSO"),
    "edistribuzione": ("E-Distribuzione", "DSO"),
    "e distribuzione": ("E-Distribuzione", "DSO"),
    "enel distribuzione": ("E-Distribuzione", "DSO"),  # predecessor pre-2016
    "enel distribuzione s.p.a.": ("E-Distribuzione", "DSO"),
    "enel distribution": ("E-Distribuzione", "DSO"),
    "enel": ("E-Distribuzione", "DSO"),  # generic — dominant utility
    "enel spa": ("E-Distribuzione", "DSO"),
    "enel s.p.a.": ("E-Distribuzione", "DSO"),

    # ═══ ACEA — Rome metropolitan DSO (§4bis.5 12th candidate) ═══
    "acea": ("ACEA", "DSO"),
    "acea s.p.a.": ("ACEA", "DSO"),
    "acea spa": ("ACEA", "DSO"),
    "acea distribuzione": ("ACEA", "DSO"),
    "areti": ("ACEA", "DSO"),  # ACEA Areti subsidiary
    "acea areti": ("ACEA", "DSO"),
    "rome electricity distribution": ("ACEA", "DSO"),

    # ═══ A2A — Milan/Brescia metropolitan (§4bis.5 11th candidate) ═══
    "a2a": ("A2A", "DSO"),
    "a2a s.p.a.": ("A2A", "DSO"),
    "a2a spa": ("A2A", "DSO"),
    "a2a reti elettriche": ("A2A", "DSO"),  # predecessor pre-2017
    "a2a distribuzione": ("A2A", "DSO"),
    "milan brescia utility": ("A2A", "DSO"),

    # ═══ UNARETI — Milan subsidiary (§4bis.5 11th candidate) ═══
    "unareti": ("Unareti", "DSO"),
    "unareti s.p.a.": ("Unareti", "DSO"),
    "unareti spa": ("Unareti", "DSO"),
    "unareti distribuzione": ("Unareti", "DSO"),
    "milan distribution": ("Unareti", "DSO"),

    # ═══ IREN — Turin/Genoa/Trieste/Reggio multi-city ═══
    "iren": ("Iren", "DSO"),
    "iren s.p.a.": ("Iren", "DSO"),
    "iren spa": ("Iren", "DSO"),
    "ireti": ("Iren", "DSO"),  # IREN grid subsidiary
    "iren rete elettrica": ("Iren", "DSO"),
    "iren vallée d'aoste": ("Iren", "DSO"),  # French Aosta cross-border
    "iren vallee d'aoste": ("Iren", "DSO"),
    "turin genoa utility": ("Iren", "DSO"),

    # ═══ HERA — Bologna/Emilia-Romagna metropolitan ═══
    "hera": ("Hera", "DSO"),
    "hera s.p.a.": ("Hera", "DSO"),
    "hera spa": ("Hera", "DSO"),
    "hera distribuzione": ("Hera", "DSO"),
    "inrete": ("Hera", "DSO"),  # Hera Inrete subsidiary
    "inrete distribuzione energia": ("Hera", "DSO"),
    "emilia-romagna utility": ("Hera", "DSO"),

    # ═══ AGSM AIM — Verona/Vicenza municipal ═══
    "agsm": ("AGSM AIM", "DSO"),
    "agsm aim": ("AGSM AIM", "DSO"),
    "agsm-aim": ("AGSM AIM", "DSO"),
    "aim vicenza": ("AGSM AIM", "DSO"),
    "agsm verona": ("AGSM AIM", "DSO"),
    "verona utility": ("AGSM AIM", "DSO"),

    # ═══ DEVAL — Aosta Valley regional (bilingual IT/FR) ═══
    "deval": ("Deval", "DSO"),
    "deval s.p.a.": ("Deval", "DSO"),
    "deval spa": ("Deval", "DSO"),
    "deval distribuzione": ("Deval", "DSO"),
    "deval vallée d'aoste": ("Deval", "DSO"),  # French Aosta statutory
    "deval vallee d'aoste": ("Deval", "DSO"),
    "aosta valley electricity": ("Deval", "DSO"),

    # ═══ EDYNA / ALPERIA — South Tyrol/Alto Adige (bilingual IT/DE) ═══
    "edyna": ("Edyna", "DSO"),
    "edyna s.r.l.": ("Edyna", "DSO"),
    "edyna srl": ("Edyna", "DSO"),
    "edyna gmbh": ("Edyna", "DSO"),  # German
    "alperia": ("Edyna", "DSO"),  # Alperia parent
    "alperia fiber": ("Edyna", "DSO"),
    "südtirol netz": ("Edyna", "DSO"),  # German
    "sudtirol netz": ("Edyna", "DSO"),
    "south tyrol electricity": ("Edyna", "DSO"),

    # ═══ RFI — Rail traction 3 kV DC + 25 kV AC ═══
    "rfi": ("RFI", "RAIL_TRACTION"),
    "rete ferroviaria italiana": ("RFI", "RAIL_TRACTION"),
    "rfi s.p.a.": ("RFI", "RAIL_TRACTION"),
    "rfi spa": ("RFI", "RAIL_TRACTION"),
    "ferrovie dello stato": ("RFI", "RAIL_TRACTION"),
    "fs italiane": ("RFI", "RAIL_TRACTION"),
    "fs": ("RFI", "RAIL_TRACTION"),
    "italian rail infrastructure": ("RFI", "RAIL_TRACTION"),
    "italian state railways": ("RFI", "RAIL_TRACTION"),
    "italienische eisenbahn": ("RFI", "RAIL_TRACTION"),  # German

    # ═══ ATM — Milan Metro 1500 V DC ═══
    "atm": ("ATM Milano", "RAIL_METRO_MILANO"),
    "atm milano": ("ATM Milano", "RAIL_METRO_MILANO"),
    "azienda trasporti milanesi": ("ATM Milano", "RAIL_METRO_MILANO"),
    "milan metro": ("ATM Milano", "RAIL_METRO_MILANO"),

    # ═══ ATAC — Rome Metro 1500 V DC ═══
    "atac": ("ATAC Roma", "RAIL_METRO_ROMA"),
    "atac roma": ("ATAC Roma", "RAIL_METRO_ROMA"),
    "atac s.p.a.": ("ATAC Roma", "RAIL_METRO_ROMA"),
    "rome metro": ("ATAC Roma", "RAIL_METRO_ROMA"),

    # ═══ Renewable generation (Layer 4b) ═══
    "enel green power": ("Enel Green Power", "GEN_RENEWABLE"),
    "egp": ("Enel Green Power", "GEN_RENEWABLE"),
    "erg renew": ("ERG Renew", "GEN_RENEWABLE"),
    "erg": ("ERG Renew", "GEN_RENEWABLE"),
    "edison": ("Edison", "GEN_ENERGY_MULTIPLE"),
    "edison s.p.a.": ("Edison", "GEN_ENERGY_MULTIPLE"),
    "edison renewables": ("Edison", "GEN_ENERGY_MULTIPLE"),
    "a2a renewables": ("A2A Renewables", "GEN_RENEWABLE_MULTIPLE"),

    # ═══ HVDC + AC interconnector consortiums ═══
    "sapei": ("SAPEI", "HVDC_INTERCONNECTOR"),
    "sapei hvdc": ("SAPEI", "HVDC_INTERCONNECTOR"),
    "sorgente-rizziconi": ("Sorgente-Rizziconi", "HVDC_INTERCONNECTOR"),
    "sorgente rizziconi": ("Sorgente-Rizziconi", "HVDC_INTERCONNECTOR"),
    "sicilia-calabria": ("Sorgente-Rizziconi", "HVDC_INTERCONNECTOR"),
    "sacoi": ("SACOI", "HVDC_INTERCONNECTOR"),
    "sacoi hvdc": ("SACOI", "HVDC_INTERCONNECTOR"),
    "malta interconnector": ("Malta-Italy HVDC", "HVDC_INTERCONNECTOR"),
    "malta-italy hvdc": ("Malta-Italy HVDC", "HVDC_INTERCONNECTOR"),

    # ═══ Cross-border partner TSOs (route to Terna) ═══
    "rte": ("Terna", "TSO_CROSS_BORDER_FR"),
    "réseau de transport d'électricité": ("Terna", "TSO_CROSS_BORDER_FR"),
    "reseau de transport d'electricite": ("Terna", "TSO_CROSS_BORDER_FR"),
    "french tso": ("Terna", "TSO_CROSS_BORDER_FR"),
    "swissgrid": ("Terna", "TSO_CROSS_BORDER_CH"),
    "swissgrid ag": ("Terna", "TSO_CROSS_BORDER_CH"),
    "swissgrid italia": ("Terna", "TSO_CROSS_BORDER_CH"),
    "swiss tso": ("Terna", "TSO_CROSS_BORDER_CH"),
    "apg": ("Terna", "TSO_CROSS_BORDER_AT"),
    "austrian power grid": ("Terna", "TSO_CROSS_BORDER_AT"),
    "apg ag": ("Terna", "TSO_CROSS_BORDER_AT"),
    "austrian tso": ("Terna", "TSO_CROSS_BORDER_AT"),
    "eles": ("Terna", "TSO_CROSS_BORDER_SI"),
    "eles d.o.o.": ("Terna", "TSO_CROSS_BORDER_SI"),
    "elektro-slovenija": ("Terna", "TSO_CROSS_BORDER_SI"),
    "slovenian tso": ("Terna", "TSO_CROSS_BORDER_SI"),
    "admie": ("Terna", "TSO_CROSS_BORDER_GR"),
    "ipto": ("Terna", "TSO_CROSS_BORDER_GR"),
    "greek tso": ("Terna", "TSO_CROSS_BORDER_GR"),
}


# Convention #78 BINDING enforcement counter
_ALIAS_HIT_COUNTER = {"total": 0}


def _normalize(name: str) -> str:
    """NFC-normalise + lowercase for alias matching.

    Preserves Italian diacritics (à è é ì ò ù) + German (ä ö ü ß) +
    French (à â ç é è ê î ô) + Slovenian (č š ž) special chars.
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
    """10-layer operator resolver — Italy P34 Wave 4.

    Returns (canonical_operator, role, resolution_layer). None if
    unresolved (Convention #56 visibly-honest degradation).
    """
    # ─── Layer 1: Direct alias hit (Convention #78 BINDING 16th) ───
    if raw_operator:
        normalized = _normalize(raw_operator)
        if normalized in ALIAS_MAP:
            canonical, role = ALIAS_MAP[normalized]
            _ALIAS_HIT_COUNTER["total"] += 1
            return canonical, role, "alias_hit"

    # Coord-based layers require lat+lon
    if lat is None or lon is None:
        return _resolve_by_voltage_only(voltage_kv)

    # ─── Layer 2: Milan §4bis.5 A2A/Unareti (11th enforcement) ───
    if _in_bbox(lat, lon, MILAN_A2A_UNARETI_BBOX):
        return "A2A/Unareti Milan", "DSO", "milan_a2a_unareti_geofence"

    # ─── Layer 3: Milan §4bis.5 E-Distribuzione (11th enforcement) ───
    if _in_bbox(lat, lon, MILAN_E_DISTRIBUZIONE_BBOX):
        return (
            "E-Distribuzione Milan",
            "DSO",
            "milan_e_distribuzione_geofence",
        )

    # ─── Layer 4: Rome §4bis.5 ACEA (12th enforcement) ───
    if _in_bbox(lat, lon, ROME_ACEA_BBOX):
        return "ACEA Rome", "DSO", "rome_acea_geofence"

    # ─── Layer 5: Rome §4bis.5 E-Distribuzione (12th enforcement) ───
    if _in_bbox(lat, lon, ROME_E_DISTRIBUZIONE_BBOX):
        return (
            "E-Distribuzione Rome/Lazio",
            "DSO",
            "rome_e_distribuzione_geofence",
        )

    # ─── Layer 6: Voltage-class heuristic ───
    if voltage_kv is not None:
        if voltage_kv >= 400.0:
            return "Terna", "TSO", "voltage_ehv"
        if voltage_kv >= 220.0:
            return "Terna", "TSO", "voltage_hv_transmission"
        if voltage_kv >= 132.0:
            # Italian dominant subT voltage class (Terna)
            return "Terna", "TSO", "voltage_subtransmission_132"
        if voltage_kv >= 60.0:
            return "Terna", "TSO", "voltage_regional_60"

    # ─── Layer 7: Rail traction 3 kV DC or 25 kV AC ───
    if voltage_kv is not None:
        if 2.5 <= voltage_kv <= 3.5:
            return "RFI", "RAIL_TRACTION", "rail_traction_3kv_dc"
        if 24.0 <= voltage_kv <= 26.0:
            return "RFI", "RAIL_TRACTION", "rail_traction_25kv_ac"

    # ─── Layer 8: Alpine regional DSO (Alto Adige/Trentino/Aosta) ───
    # Approximate bboxes for autonomous regions
    if voltage_kv is not None and voltage_kv < 60.0:
        # South Tyrol/Alto Adige (~46.3-47.1°N × 10.4-12.5°E)
        if 46.3 <= lat <= 47.1 and 10.4 <= lon <= 12.5:
            return "Edyna", "DSO", "south_tyrol_edyna_regional"
        # Aosta Valley (~45.5-45.9°N × 6.9-7.9°E)
        if 45.5 <= lat <= 45.9 and 6.9 <= lon <= 7.9:
            return "Deval", "DSO", "aosta_valley_deval_regional"

    # ─── Layer 9: Rural low-voltage default → E-Distribuzione ───
    if voltage_kv is not None and voltage_kv < 30.0:
        return "E-Distribuzione", "DSO", "voltage_lv_default"

    # ─── Layer 10: Fallback DSO → E-Distribuzione (85% market) ───
    if voltage_kv is None:
        return None, None, None  # Convention #56 — insufficient signal

    return "E-Distribuzione", "DSO", "fallback_default_dso"


def _resolve_by_voltage_only(
    voltage_kv: Optional[float],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Voltage-only fallback when lat/lon absent."""
    if voltage_kv is None:
        return None, None, None
    if voltage_kv >= 400.0:
        return "Terna", "TSO", "voltage_ehv_no_coords"
    if voltage_kv >= 220.0:
        return "Terna", "TSO", "voltage_hv_transmission_no_coords"
    if voltage_kv >= 132.0:
        return "Terna", "TSO", "voltage_subtransmission_132_no_coords"
    if 2.5 <= voltage_kv <= 3.5:
        return "RFI", "RAIL_TRACTION", "rail_traction_3kv_dc_no_coords"
    if 24.0 <= voltage_kv <= 26.0:
        return "RFI", "RAIL_TRACTION", "rail_traction_25kv_ac_no_coords"
    return None, None, None


# Resolver layer catalogue — exposed for audit
RESOLVER_LAYERS = [
    "alias_hit",  # Convention #78 BINDING 16th
    "milan_a2a_unareti_geofence",  # §4bis.5 11th part-a
    "milan_e_distribuzione_geofence",  # §4bis.5 11th part-b
    "rome_acea_geofence",  # §4bis.5 12th part-a
    "rome_e_distribuzione_geofence",  # §4bis.5 12th part-b
    "voltage_ehv",
    "voltage_hv_transmission",
    "voltage_subtransmission_132",
    "voltage_regional_60",
    "rail_traction_3kv_dc",
    "rail_traction_25kv_ac",
    "south_tyrol_edyna_regional",
    "aosta_valley_deval_regional",
    "voltage_lv_default",
    "fallback_default_dso",
    # No-coord fallbacks
    "voltage_ehv_no_coords",
    "voltage_hv_transmission_no_coords",
    "voltage_subtransmission_132_no_coords",
    "rail_traction_3kv_dc_no_coords",
    "rail_traction_25kv_ac_no_coords",
]


def alias_hit_count() -> int:
    """Return cumulative Convention #78 alias hits for audit sidecar."""
    return _ALIAS_HIT_COUNTER["total"]


def reset_alias_hit_counter() -> None:
    """Reset counter (for test isolation)."""
    _ALIAS_HIT_COUNTER["total"] = 0
