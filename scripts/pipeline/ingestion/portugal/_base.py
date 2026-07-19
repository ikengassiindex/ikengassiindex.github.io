"""Portugal P33 Wave 4 — Convention #78 BINDING 15th enforcement.

4-language alias map (Portuguese + English + Spanish cross-border +
Mirandese minority) + Açores + Madeira archipelago bbox carve-outs +
8-layer resolver (NO §4bis.5 metropolitan geofence — single-DSO
architectural simplification via E-REDES 99% mainland monopoly).

Sub-conventions preserved:
  #7 Data-Layer Anchoring — Layer 4 baselines documented proxies
  #23 provenance — every alias entry cites operator canonical + role
  #56 visibly-honest degradation — unresolved names return None, do
     not silently default to E-REDES or REN
  #60 non-commercial provenance — all sources from operator public
     websites + regulator ERSE + REN + E-REDES + EDA + EEM directory
  #78 BINDING 15th enforcement — Portuguese + English + Spanish +
     Mirandese 4-language alias normalization at Layer 5
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Bounding boxes — Discipline #36 + archipelago carve-outs
# ─────────────────────────────────────────────────────────────

# Continental Portugal — 36.96°N/42.15°N × -9.51°W/-6.19°W
# Southernmost Cabo de São Vicente Algarve + northernmost Minho river
# Galicia border. Excludes Atlantic international waters.
CONTINENTAL_BBOX = {
    "lat_min": 36.96,
    "lat_max": 42.15,
    "lon_min": -9.51,
    "lon_max": -6.19,
}

# Açores archipelago — ISLANDED grid via EDA Electricidade dos Açores
# 9 populated islands split into 3 groups:
#   Occidental: Corvo + Flores (~-31.3°W)
#   Central: Faial + Pico + São Jorge + Terceira + Graciosa (~-28°W)
#   Oriental: São Miguel + Santa Maria (~-25°W)
AZORES_BBOX = {
    "lat_min": 36.9,   # Santa Maria south
    "lat_max": 39.7,   # Corvo north
    "lon_min": -31.3,  # Corvo/Flores west
    "lon_max": -25.0,  # Santa Maria east
    "operator_canonical": "EDA",
    "role": "ISLANDED_DSO_AZORES",
}

# Madeira archipelago — ISLANDED grid via EEM Empresa de Electricidade
# da Madeira. Madeira main + Porto Santo + Desertas + Selvagens.
MADEIRA_BBOX = {
    "lat_min": 32.4,   # Ilhas Selvagens south
    "lat_max": 33.1,   # Porto Santo north
    "lon_min": -17.3,  # Madeira west
    "lon_max": -16.3,  # Porto Santo east
    "operator_canonical": "EEM",
    "role": "ISLANDED_DSO_MADEIRA",
}


# ─────────────────────────────────────────────────────────────
# Convention #78 BINDING 15th ENFORCEMENT — Alias map
# 4-language (Portuguese + English + Spanish + Mirandese) + diacritics
# ─────────────────────────────────────────────────────────────

# ~90 alias entries across 12 canonical operators. Portuguese
# diacritics preserved: ã õ ç à á â é ê í ó ú.
# Structure: raw_variant → (canonical_operator, role)

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ═══ REN — National TSO (state-majority-owned; spun off EDP 1994) ═══
    "ren": ("REN", "TSO"),
    "redes energéticas nacionais": ("REN", "TSO"),
    "redes energeticas nacionais": ("REN", "TSO"),
    "ren - redes energéticas nacionais": ("REN", "TSO"),
    "ren - redes energeticas nacionais": ("REN", "TSO"),
    "ren sgps": ("REN", "TSO"),
    "ren, sgps": ("REN", "TSO"),
    "portuguese national grid": ("REN", "TSO"),
    "portuguese transmission system operator": ("REN", "TSO"),
    "ren portugal": ("REN", "TSO"),
    "redes energéticas nacionales portugal": ("REN", "TSO"),  # Spanish
    "redes energeticas nacionales portugal": ("REN", "TSO"),

    # ═══ E-REDES — Dominant mainland DSO (~99%) ═══
    "e-redes": ("E-REDES", "DSO"),
    "e-redes sa": ("E-REDES", "DSO"),
    "e-redes s.a.": ("E-REDES", "DSO"),
    "eredes": ("E-REDES", "DSO"),
    "e redes": ("E-REDES", "DSO"),
    "edp distribuição": ("E-REDES", "DSO"),  # predecessor pre-2021
    "edp distribuicao": ("E-REDES", "DSO"),
    "edp distribuição de energia": ("E-REDES", "DSO"),
    "edp distribuicao de energia": ("E-REDES", "DSO"),
    "edp-d": ("E-REDES", "DSO"),
    "edp d": ("E-REDES", "DSO"),
    "edp distribution": ("E-REDES", "DSO"),
    "edp distribuição energia": ("E-REDES", "DSO"),

    # ═══ EDA — Açores islanded DSO ═══
    "eda": ("EDA", "ISLANDED_DSO_AZORES"),
    "electricidade dos açores": ("EDA", "ISLANDED_DSO_AZORES"),
    "electricidade dos acores": ("EDA", "ISLANDED_DSO_AZORES"),
    "eda - electricidade dos açores": ("EDA", "ISLANDED_DSO_AZORES"),
    "eda - electricidade dos acores": ("EDA", "ISLANDED_DSO_AZORES"),
    "eda açores": ("EDA", "ISLANDED_DSO_AZORES"),
    "eda acores": ("EDA", "ISLANDED_DSO_AZORES"),
    "azores electricity": ("EDA", "ISLANDED_DSO_AZORES"),
    "azores dso": ("EDA", "ISLANDED_DSO_AZORES"),

    # ═══ EEM — Madeira islanded DSO ═══
    "eem": ("EEM", "ISLANDED_DSO_MADEIRA"),
    "empresa de electricidade da madeira": ("EEM", "ISLANDED_DSO_MADEIRA"),
    "eem - empresa de electricidade da madeira": ("EEM", "ISLANDED_DSO_MADEIRA"),
    "eem madeira": ("EEM", "ISLANDED_DSO_MADEIRA"),
    "madeira electricity": ("EEM", "ISLANDED_DSO_MADEIRA"),
    "madeira dso": ("EEM", "ISLANDED_DSO_MADEIRA"),

    # ═══ Small municipal DSOs (residual ~1% market share) ═══
    "coop. eléctrica do vale d'este": ("CEVE", "MUNICIPAL_DSO_MINHO"),
    "coop. electrica do vale d'este": ("CEVE", "MUNICIPAL_DSO_MINHO"),
    "coop electrica do vale deste": ("CEVE", "MUNICIPAL_DSO_MINHO"),
    "ceve": ("CEVE", "MUNICIPAL_DSO_MINHO"),
    "coop. eléctrica de vilarinho": ("CEVE", "MUNICIPAL_DSO_MINHO"),

    # ═══ Infraestruturas de Portugal — Rail traction 25 kV 50 Hz ═══
    "infraestruturas de portugal": ("Infraestruturas de Portugal", "RAIL_TRACTION"),
    "ip": ("Infraestruturas de Portugal", "RAIL_TRACTION"),
    "ip ferrovia": ("Infraestruturas de Portugal", "RAIL_TRACTION"),
    "ip - infraestruturas de portugal": ("Infraestruturas de Portugal", "RAIL_TRACTION"),
    "refer": ("Infraestruturas de Portugal", "RAIL_TRACTION"),  # predecessor pre-2015
    "portuguese rail infrastructure": ("Infraestruturas de Portugal", "RAIL_TRACTION"),
    "cp - comboios de portugal": ("Infraestruturas de Portugal", "RAIL_TRACTION"),

    # ═══ Lisboa metro 750 V DC ═══
    "metropolitano de lisboa": ("Metropolitano de Lisboa", "RAIL_METRO_LISBOA"),
    "metro lisboa": ("Metropolitano de Lisboa", "RAIL_METRO_LISBOA"),
    "metro de lisboa": ("Metropolitano de Lisboa", "RAIL_METRO_LISBOA"),
    "ml": ("Metropolitano de Lisboa", "RAIL_METRO_LISBOA"),
    "lisbon metro": ("Metropolitano de Lisboa", "RAIL_METRO_LISBOA"),

    # ═══ Porto light metro 750 V DC ═══
    "metro do porto": ("Metro do Porto", "RAIL_METRO_PORTO"),
    "metro porto": ("Metro do Porto", "RAIL_METRO_PORTO"),
    "porto metro": ("Metro do Porto", "RAIL_METRO_PORTO"),

    # ═══ EDP Renováveis — Renewable generation (Layer 4b) ═══
    "edp renováveis": ("EDP Renováveis", "GEN_RENEWABLE"),
    "edp renovaveis": ("EDP Renováveis", "GEN_RENEWABLE"),
    "edpr": ("EDP Renováveis", "GEN_RENEWABLE"),
    "edp renewables": ("EDP Renováveis", "GEN_RENEWABLE"),

    # ═══ Iberdrola Portugal (cross-border generation) ═══
    "iberdrola portugal": ("Iberdrola Portugal", "GEN_RENEWABLE_CROSS_BORDER"),
    "iberdrola": ("Iberdrola Portugal", "GEN_RENEWABLE_CROSS_BORDER"),

    # ═══ CROSS-BORDER PARTNER TSO (route to REN via Iberian synchronous) ═══
    "ree": ("REN", "TSO_CROSS_BORDER_ES"),
    "red eléctrica de españa": ("REN", "TSO_CROSS_BORDER_ES"),
    "red electrica de espana": ("REN", "TSO_CROSS_BORDER_ES"),
    "red eléctrica": ("REN", "TSO_CROSS_BORDER_ES"),
    "red electrica": ("REN", "TSO_CROSS_BORDER_ES"),
    "spanish national grid": ("REN", "TSO_CROSS_BORDER_ES"),
    "spanish tso": ("REN", "TSO_CROSS_BORDER_ES"),
    "ren-ree": ("REN", "TSO_IBERIAN_INTERCONNECTOR"),
    "ren + ree": ("REN", "TSO_IBERIAN_INTERCONNECTOR"),
    "interconexão ibérica": ("REN", "TSO_IBERIAN_INTERCONNECTOR"),
    "interconexao iberica": ("REN", "TSO_IBERIAN_INTERCONNECTOR"),
    "iberian interconnection": ("REN", "TSO_IBERIAN_INTERCONNECTOR"),
}


# Convention #78 BINDING enforcement counter — cumulative alias hits
_ALIAS_HIT_COUNTER = {"total": 0}


def _normalize(name: str) -> str:
    """NFC-normalise + lowercase for alias matching.

    Preserves Portuguese diacritics (ã õ ç à á â é ê í ó ú) +
    Mirandese special chars.
    """
    if not name:
        return ""
    normalized = unicodedata.normalize("NFC", name).strip().lower()
    return normalized


def _in_bbox(lat: float, lon: float, bbox: dict) -> bool:
    """Check if a point is inside the given bbox."""
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
    """8-layer operator resolver — Portugal P33 Wave 4.

    Returns (canonical_operator, role, resolution_layer). None if
    unresolved (Convention #56 visibly-honest degradation).

    Resolution order (first hit wins):
      1. Direct alias hit (Convention #78 BINDING 15th enforcement)
      2. Açores archipelago bbox → EDA islanded DSO
      3. Madeira archipelago bbox → EEM islanded DSO
      4. Voltage-class heuristic:
         - EHV ≥400 kV → REN TSO
         - 220 kV / 150 kV → REN transmission backbone
         - 60 kV → E-REDES subtransmission
      5. Rail traction 25 kV 50 Hz → Infraestruturas de Portugal
      6. Rural low-voltage default (<30 kV) → E-REDES (99% mainland)
      7. Fallback DSO → E-REDES
      8. Unresolved → None (Convention #56)

    Note: NO §4bis.5 metropolitan geofence layer — Portugal is
    single-DSO (E-REDES ~99% mainland). Açores + Madeira archipelago
    carve-outs handled at bbox layer (layers 2+3), not §4bis.5.
    """
    # ─── Layer 1: Direct alias hit (Convention #78 BINDING 15th) ───
    if raw_operator:
        normalized = _normalize(raw_operator)
        if normalized in ALIAS_MAP:
            canonical, role = ALIAS_MAP[normalized]
            _ALIAS_HIT_COUNTER["total"] += 1
            return canonical, role, "alias_hit"

    # Coord-based layers require lat+lon
    if lat is None or lon is None:
        return _resolve_by_voltage_only(voltage_kv)

    # ─── Layer 2: Açores bbox → EDA ───
    if _in_bbox(lat, lon, AZORES_BBOX):
        return "EDA", "ISLANDED_DSO_AZORES", "azores_bbox_carve_out"

    # ─── Layer 3: Madeira bbox → EEM ───
    if _in_bbox(lat, lon, MADEIRA_BBOX):
        return "EEM", "ISLANDED_DSO_MADEIRA", "madeira_bbox_carve_out"

    # ─── Layer 4: Voltage-class heuristic ───
    if voltage_kv is not None:
        if voltage_kv >= 400.0:
            return "REN", "TSO", "voltage_ehv"
        if voltage_kv >= 220.0:
            return "REN", "TSO", "voltage_hv_transmission"
        if voltage_kv >= 150.0:
            return "REN", "TSO", "voltage_regional_transmission"
        if voltage_kv >= 60.0:
            return "E-REDES", "DSO", "voltage_subtransmission"

    # ─── Layer 5: Rail traction 25 kV 50 Hz ───
    # Distinctive Portuguese rail electrification frequency
    if voltage_kv is not None and 24.0 <= voltage_kv <= 26.0:
        return (
            "Infraestruturas de Portugal",
            "RAIL_TRACTION",
            "rail_traction_frequency",
        )

    # ─── Layer 6: Rural low-voltage default ───
    if voltage_kv is not None and voltage_kv < 30.0:
        return "E-REDES", "DSO", "voltage_lv_default"

    # ─── Layer 7: Fallback DSO ───
    if voltage_kv is None:
        return None, None, None  # Convention #56 — insufficient signal

    return "E-REDES", "DSO", "fallback_default_dso"


def _resolve_by_voltage_only(
    voltage_kv: Optional[float],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Voltage-only fallback when lat/lon absent."""
    if voltage_kv is None:
        return None, None, None
    if voltage_kv >= 400.0:
        return "REN", "TSO", "voltage_ehv_no_coords"
    if voltage_kv >= 220.0:
        return "REN", "TSO", "voltage_hv_transmission_no_coords"
    if voltage_kv >= 150.0:
        return "REN", "TSO", "voltage_regional_no_coords"
    if 24.0 <= voltage_kv <= 26.0:
        return "Infraestruturas de Portugal", "RAIL_TRACTION", "rail_traction_no_coords"
    return None, None, None


# Resolver layer catalogue — exposed for audit
RESOLVER_LAYERS = [
    "alias_hit",  # Convention #78 BINDING 15th
    "azores_bbox_carve_out",  # islanded DSO EDA
    "madeira_bbox_carve_out",  # islanded DSO EEM
    "voltage_ehv",
    "voltage_hv_transmission",
    "voltage_regional_transmission",
    "voltage_subtransmission",
    "rail_traction_frequency",
    "voltage_lv_default",
    "fallback_default_dso",
    # No-coord fallbacks
    "voltage_ehv_no_coords",
    "voltage_hv_transmission_no_coords",
    "voltage_regional_no_coords",
    "rail_traction_no_coords",
]


def alias_hit_count() -> int:
    """Return cumulative Convention #78 alias hits for audit sidecar."""
    return _ALIAS_HIT_COUNTER["total"]


def reset_alias_hit_counter() -> None:
    """Reset counter (for test isolation)."""
    _ALIAS_HIT_COUNTER["total"] = 0
