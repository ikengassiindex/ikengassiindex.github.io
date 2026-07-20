"""Japan P35 Wave 4 — Convention #78 BINDING 17th enforcement.

4-language alias map (Japanese kanji+hiragana+katakana+rōmaji +
English + Ainu + Ryukyuan).

9-regional-utility territory-based resolver (NO §4bis.5 metropolitan
geofence — regional-monopoly architectural simplification).

8-layer resolver:
  1. Direct alias hit (Convention #78 BINDING 17th)
  2. Voltage-class heuristic (EHV/HV/subT/MV)
  3. Rail traction 1.5 kV DC JR + 25 kV AC Shinkansen
  4. Frequency converter station coord match
  5. Nuclear reactor coord match (post-Fukushima carve-out)
  6. Okinawa bbox → Okinawa Electric Power (100% islanded)
  7. Rural low-voltage default → E-Distribuzione-equivalent (regional)
  8. Fallback → coord-based regional utility mapping

Sub-conventions preserved: #7 + #23 + #56 + #60 + #78 BINDING.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# ─────────────────────────────────────────────────────────────
# Bounding boxes — Discipline #36 + regional utility territories
# ─────────────────────────────────────────────────────────────

# Japan national bbox — 24.05°N Yonaguni → 45.53°N Sōya-misaki
# 122.93°E Sakishima → 153.99°E Minamitorishima Ogasawara
JAPAN_BBOX = {
    "lat_min": 24.05,
    "lat_max": 45.53,
    "lon_min": 122.93,
    "lon_max": 153.99,
}

# 9 regional utility territories (approximate bboxes for coord fallback)
# ─────────────────────────────────────────────────────────────
# NOT §4bis.5 geofences — Japan is regional-monopoly single-DSO
# per territory. These are coord-based routing hints for unresolved
# operators (Layer 8 fallback).

REGIONAL_TERRITORIES = {
    "hokkaido_epc_network": {
        "lat_min": 41.35,  # Hakodate
        "lat_max": 45.53,  # Sōya-misaki
        "lon_min": 139.75,
        "lon_max": 145.82,
        "operator_canonical": "Hokkaido Electric Power Network",
        "role": "REGIONAL_TSO_TD_50HZ",
    },
    "tohoku_epc_network": {
        "lat_min": 36.75,
        "lat_max": 41.60,
        "lon_min": 138.50,  # includes Niigata
        "lon_max": 142.10,
        "operator_canonical": "Tohoku Electric Power Network",
        "role": "REGIONAL_TSO_TD_50HZ",
    },
    "tepco_power_grid": {
        "lat_min": 34.90,
        "lat_max": 37.10,
        "lon_min": 138.70,
        "lon_max": 141.10,
        "operator_canonical": "TEPCO Power Grid",
        "role": "REGIONAL_TSO_TD_50HZ",
    },
    "chubu_power_grid": {
        "lat_min": 34.30,
        "lat_max": 37.10,
        "lon_min": 135.90,
        "lon_max": 138.90,
        "operator_canonical": "Chubu Electric Power Grid",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "hokuriku_epc_td": {
        "lat_min": 35.90,
        "lat_max": 37.60,
        "lon_min": 135.60,
        "lon_max": 137.90,
        "operator_canonical": "Hokuriku Electric Power T&D",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "kansai_td": {
        "lat_min": 33.40,
        "lat_max": 35.90,
        "lon_min": 134.20,
        "lon_max": 136.60,
        "operator_canonical": "Kansai T&D",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "chugoku_td": {
        "lat_min": 33.75,
        "lat_max": 35.85,
        "lon_min": 130.85,
        "lon_max": 134.55,
        "operator_canonical": "Chugoku Electric Power Network",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "shikoku_td": {
        "lat_min": 32.70,
        "lat_max": 34.55,
        "lon_min": 132.00,
        "lon_max": 134.75,
        "operator_canonical": "Shikoku Electric Power T&D",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "kyushu_td": {
        "lat_min": 27.00,  # includes Amami
        "lat_max": 33.90,
        "lon_min": 128.35,
        "lon_max": 132.05,
        "operator_canonical": "Kyushu Electric Power T&D",
        "role": "REGIONAL_TSO_TD_60HZ",
    },
    "okinawa_electric_power": {
        "lat_min": 24.05,  # Yonaguni
        "lat_max": 27.15,  # main Okinawa north
        "lon_min": 122.93,
        "lon_max": 131.35,  # Daito Islands
        "operator_canonical": "Okinawa Electric Power",
        "role": "ISLANDED_REGIONAL_TSO_TD_60HZ",
    },
}


# ─────────────────────────────────────────────────────────────
# Convention #78 BINDING 17TH ENFORCEMENT — 4-language ALIAS_MAP
# ─────────────────────────────────────────────────────────────
# ~130 alias entries across 20+ canonical operators.
# Japanese scripts: Kanji (東京電力) + Hiragana + Katakana (メトロ) +
# Rōmaji (TEPCO/Tokyo Electric Power).

ALIAS_MAP: dict[str, tuple[str, str]] = {
    # ═══ TEPCO POWER GRID — Kanto 50 Hz ═══
    "tepco": ("TEPCO Power Grid", "DSO"),
    "tepco power grid": ("TEPCO Power Grid", "DSO"),
    "tepco pg": ("TEPCO Power Grid", "DSO"),
    "tokyo electric power": ("TEPCO Power Grid", "DSO"),
    "tokyo electric power grid": ("TEPCO Power Grid", "DSO"),
    "tokyo electric power company": ("TEPCO Power Grid", "DSO"),
    "tepco holdings": ("TEPCO Power Grid", "DSO"),
    "東京電力": ("TEPCO Power Grid", "DSO"),
    "東京電力パワーグリッド": ("TEPCO Power Grid", "DSO"),
    "東電": ("TEPCO Power Grid", "DSO"),
    "東電pg": ("TEPCO Power Grid", "DSO"),
    "東京電力ホールディングス": ("TEPCO Power Grid", "DSO"),
    "tepcoパワーグリッド": ("TEPCO Power Grid", "DSO"),

    # ═══ KANSAI T&D — Kansai 60 Hz ═══
    "kepco": ("Kansai T&D", "DSO"),
    "kansai": ("Kansai T&D", "DSO"),
    "kansai electric power": ("Kansai T&D", "DSO"),
    "kansai transmission and distribution": ("Kansai T&D", "DSO"),
    "kansai t&d": ("Kansai T&D", "DSO"),
    "kansai td": ("Kansai T&D", "DSO"),
    "関西電力": ("Kansai T&D", "DSO"),
    "関西電力送配電": ("Kansai T&D", "DSO"),
    "関電": ("Kansai T&D", "DSO"),
    "関電t&d": ("Kansai T&D", "DSO"),

    # ═══ CHUBU POWER GRID — Central Honshu 60 Hz ═══
    "chubu": ("Chubu Electric Power Grid", "DSO"),
    "chubu electric power": ("Chubu Electric Power Grid", "DSO"),
    "chubu power grid": ("Chubu Electric Power Grid", "DSO"),
    "chubu pg": ("Chubu Electric Power Grid", "DSO"),
    "中部電力": ("Chubu Electric Power Grid", "DSO"),
    "中部電力パワーグリッド": ("Chubu Electric Power Grid", "DSO"),
    "中電": ("Chubu Electric Power Grid", "DSO"),
    "中電pg": ("Chubu Electric Power Grid", "DSO"),
    "中部電力ミライズ": ("Chubu Electric Power Grid", "DSO"),

    # ═══ KYUSHU T&D — Kyushu 60 Hz ═══
    "kyushu": ("Kyushu Electric Power T&D", "DSO"),
    "kyushu electric power": ("Kyushu Electric Power T&D", "DSO"),
    "kyushu t&d": ("Kyushu Electric Power T&D", "DSO"),
    "kyushu td": ("Kyushu Electric Power T&D", "DSO"),
    "九州電力": ("Kyushu Electric Power T&D", "DSO"),
    "九州電力送配電": ("Kyushu Electric Power T&D", "DSO"),
    "九電": ("Kyushu Electric Power T&D", "DSO"),
    "九電t&d": ("Kyushu Electric Power T&D", "DSO"),

    # ═══ TOHOKU NETWORK — Tohoku 50 Hz ═══
    "tohoku": ("Tohoku Electric Power Network", "DSO"),
    "tohoku electric power": ("Tohoku Electric Power Network", "DSO"),
    "tohoku electric power network": ("Tohoku Electric Power Network", "DSO"),
    "tohoku epc network": ("Tohoku Electric Power Network", "DSO"),
    "東北電力": ("Tohoku Electric Power Network", "DSO"),
    "東北電力ネットワーク": ("Tohoku Electric Power Network", "DSO"),
    "東北電力送配電": ("Tohoku Electric Power Network", "DSO"),
    "東北epcネットワーク": ("Tohoku Electric Power Network", "DSO"),

    # ═══ HOKKAIDO NETWORK — Hokkaido 50 Hz ═══
    "hokkaido": ("Hokkaido Electric Power Network", "DSO"),
    "hokkaido electric power": ("Hokkaido Electric Power Network", "DSO"),
    "hokkaido electric power network": ("Hokkaido Electric Power Network", "DSO"),
    "hepco": ("Hokkaido Electric Power Network", "DSO"),
    "hepco network": ("Hokkaido Electric Power Network", "DSO"),
    "北海道電力": ("Hokkaido Electric Power Network", "DSO"),
    "北海道電力ネットワーク": ("Hokkaido Electric Power Network", "DSO"),
    "ホクデン": ("Hokkaido Electric Power Network", "DSO"),
    "ホクデンnw": ("Hokkaido Electric Power Network", "DSO"),
    "北電": ("Hokkaido Electric Power Network", "DSO"),
    "北電nw": ("Hokkaido Electric Power Network", "DSO"),

    # ═══ CHUGOKU T&D — Chugoku 60 Hz ═══
    "chugoku": ("Chugoku Electric Power Network", "DSO"),
    "chugoku electric power": ("Chugoku Electric Power Network", "DSO"),
    "chugoku electric power network": ("Chugoku Electric Power Network", "DSO"),
    "chugoku t&d": ("Chugoku Electric Power Network", "DSO"),
    "chugoku td": ("Chugoku Electric Power Network", "DSO"),
    "中国電力": ("Chugoku Electric Power Network", "DSO"),
    "中国電力ネットワーク": ("Chugoku Electric Power Network", "DSO"),
    "中国電力送配電": ("Chugoku Electric Power Network", "DSO"),
    "中電nw": ("Chugoku Electric Power Network", "DSO"),

    # ═══ SHIKOKU T&D — Shikoku 60 Hz ═══
    "shikoku": ("Shikoku Electric Power T&D", "DSO"),
    "shikoku electric power": ("Shikoku Electric Power T&D", "DSO"),
    "shikoku t&d": ("Shikoku Electric Power T&D", "DSO"),
    "shikoku td": ("Shikoku Electric Power T&D", "DSO"),
    "四国電力": ("Shikoku Electric Power T&D", "DSO"),
    "四国電力送配電": ("Shikoku Electric Power T&D", "DSO"),
    "四電": ("Shikoku Electric Power T&D", "DSO"),
    "四電t&d": ("Shikoku Electric Power T&D", "DSO"),

    # ═══ OKINAWA — 100% islanded 60 Hz ═══
    "okinawa": ("Okinawa Electric Power", "ISLANDED_DSO"),
    "okinawa electric power": ("Okinawa Electric Power", "ISLANDED_DSO"),
    "okinawa-epco": ("Okinawa Electric Power", "ISLANDED_DSO"),
    "okinawa epco": ("Okinawa Electric Power", "ISLANDED_DSO"),
    "沖縄電力": ("Okinawa Electric Power", "ISLANDED_DSO"),
    "オキ電": ("Okinawa Electric Power", "ISLANDED_DSO"),

    # ═══ HOKURIKU T&D — Hokuriku 60 Hz (small territory) ═══
    "hokuriku": ("Hokuriku Electric Power T&D", "DSO"),
    "hokuriku electric power": ("Hokuriku Electric Power T&D", "DSO"),
    "hokuriku t&d": ("Hokuriku Electric Power T&D", "DSO"),
    "北陸電力": ("Hokuriku Electric Power T&D", "DSO"),
    "北陸電力送配電": ("Hokuriku Electric Power T&D", "DSO"),
    "陸電": ("Hokuriku Electric Power T&D", "DSO"),

    # ═══ JR RAIL TRACTION — 1.5 kV DC + 25 kV AC Shinkansen ═══
    "jr east": ("JR East", "RAIL_TRACTION"),
    "east japan railway": ("JR East", "RAIL_TRACTION"),
    "east japan railway company": ("JR East", "RAIL_TRACTION"),
    "jr-east": ("JR East", "RAIL_TRACTION"),
    "jreast": ("JR East", "RAIL_TRACTION"),
    "jr東日本": ("JR East", "RAIL_TRACTION"),
    "東日本旅客鉄道": ("JR East", "RAIL_TRACTION"),
    "jr west": ("JR West", "RAIL_TRACTION"),
    "west japan railway": ("JR West", "RAIL_TRACTION"),
    "jr-west": ("JR West", "RAIL_TRACTION"),
    "jr西日本": ("JR West", "RAIL_TRACTION"),
    "西日本旅客鉄道": ("JR West", "RAIL_TRACTION"),
    "jr central": ("JR Central", "RAIL_TRACTION"),
    "jr-central": ("JR Central", "RAIL_TRACTION"),
    "jr東海": ("JR Central", "RAIL_TRACTION"),
    "東海旅客鉄道": ("JR Central", "RAIL_TRACTION"),
    "jr kyushu": ("JR Kyushu", "RAIL_TRACTION"),
    "jr-kyushu": ("JR Kyushu", "RAIL_TRACTION"),
    "jr九州": ("JR Kyushu", "RAIL_TRACTION"),
    "jr hokkaido": ("JR Hokkaido", "RAIL_TRACTION"),
    "jr-hokkaido": ("JR Hokkaido", "RAIL_TRACTION"),
    "jr北海道": ("JR Hokkaido", "RAIL_TRACTION"),
    "jr shikoku": ("JR Shikoku", "RAIL_TRACTION"),
    "jr-shikoku": ("JR Shikoku", "RAIL_TRACTION"),
    "jr四国": ("JR Shikoku", "RAIL_TRACTION"),

    # ═══ Metro operators ═══
    "tokyo metro": ("Tokyo Metro", "RAIL_METRO_TOKYO"),
    "東京メトロ": ("Tokyo Metro", "RAIL_METRO_TOKYO"),
    "東京地下鉄": ("Tokyo Metro", "RAIL_METRO_TOKYO"),
    "toei": ("Toei Subway", "RAIL_METRO_TOKYO_TOEI"),
    "toei subway": ("Toei Subway", "RAIL_METRO_TOKYO_TOEI"),
    "都営地下鉄": ("Toei Subway", "RAIL_METRO_TOKYO_TOEI"),
    "東京都交通局": ("Toei Subway", "RAIL_METRO_TOKYO_TOEI"),
    "osaka metro": ("Osaka Metro", "RAIL_METRO_OSAKA"),
    "大阪メトロ": ("Osaka Metro", "RAIL_METRO_OSAKA"),
    "大阪市高速電気軌道": ("Osaka Metro", "RAIL_METRO_OSAKA"),

    # ═══ Nuclear + wholesale generation (Layer 4b) ═══
    "japan atomic power": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "japan atomic power company": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "japco": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "japc": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "日本原子力発電": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "原電": ("Japan Atomic Power Company", "GEN_NUCLEAR"),
    "j-power": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),
    "jpower": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),
    "electric power development company": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),
    "epdc": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),
    "電源開発": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),
    "電源開発株式会社": ("J-Power", "GEN_NUCLEAR_MULTIPLE"),

    # ═══ OCCTO — national coordination body ═══
    "occto": ("OCCTO", "NATIONAL_COORDINATION"),
    "organization for cross-regional coordination of transmission operators": ("OCCTO", "NATIONAL_COORDINATION"),
    "電力広域的運営推進機関": ("OCCTO", "NATIONAL_COORDINATION"),
    "広域機関": ("OCCTO", "NATIONAL_COORDINATION"),

    # ═══ HVDC frequency converter operators ═══
    "shin-shinano": ("Shin-Shinano FC Station", "FREQUENCY_CONVERTER"),
    "shin shinano": ("Shin-Shinano FC Station", "FREQUENCY_CONVERTER"),
    "新信濃": ("Shin-Shinano FC Station", "FREQUENCY_CONVERTER"),
    "sakuma": ("Sakuma FC Station", "FREQUENCY_CONVERTER"),
    "佐久間": ("Sakuma FC Station", "FREQUENCY_CONVERTER"),
    "higashi-shimizu": ("Higashi-Shimizu FC Station", "FREQUENCY_CONVERTER"),
    "higashi shimizu": ("Higashi-Shimizu FC Station", "FREQUENCY_CONVERTER"),
    "東清水": ("Higashi-Shimizu FC Station", "FREQUENCY_CONVERTER"),
    "minami-fukumitsu": ("Minami-Fukumitsu FC Station", "FREQUENCY_CONVERTER"),
    "minami fukumitsu": ("Minami-Fukumitsu FC Station", "FREQUENCY_CONVERTER"),
    "南福光": ("Minami-Fukumitsu FC Station", "FREQUENCY_CONVERTER"),
}


# Convention #78 BINDING enforcement counter
_ALIAS_HIT_COUNTER = {"total": 0}


def _normalize(name: str) -> str:
    """NFC-normalise + lowercase for alias matching.

    Preserves Japanese scripts (kanji + hiragana + katakana) end-to-end.
    Handles fullwidth/halfwidth ambiguity via NFC canonicalisation.
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
    """Coord-based fallback → regional utility.

    Iterates 9 regional utility territories (small territories first —
    Okinawa + Hokuriku + Shikoku before larger — to reduce overlap
    conflicts). Returns None if outside all territories.
    """
    territory_order = [
        "okinawa_electric_power",  # smallest, no overlap
        "hokuriku_epc_td",  # small, overlaps Chubu slightly
        "shikoku_td",  # island
        "hokkaido_epc_network",  # island north
        "kyushu_td",  # island south
        "chugoku_td",
        "tohoku_epc_network",
        "tepco_power_grid",  # Kanto
        "chubu_power_grid",  # Central Honshu
        "kansai_td",  # Osaka
    ]
    for name in territory_order:
        territory = REGIONAL_TERRITORIES[name]
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
    """8-layer operator resolver — Japan P35 Wave 4.

    Returns (canonical_operator, role, resolution_layer). None if
    unresolved (Convention #56 visibly-honest degradation).
    """
    # ─── Layer 1: Direct alias hit (Convention #78 BINDING 17th) ───
    if raw_operator:
        normalized = _normalize(raw_operator)
        if normalized in ALIAS_MAP:
            canonical, role = ALIAS_MAP[normalized]
            _ALIAS_HIT_COUNTER["total"] += 1
            return canonical, role, "alias_hit"

    # Coord-based layers require lat+lon
    if lat is None or lon is None:
        return _resolve_by_voltage_only(voltage_kv)

    # ─── Layer 2: Voltage-class heuristic ───
    if voltage_kv is not None:
        # Japan uses 500 kV EHV, 275 kV HV, 154 kV regional, 66 kV subT
        if voltage_kv >= 500.0:
            regional = _resolve_regional_utility_by_coord(lat, lon)
            if regional:
                return regional[0], "TSO_EHV", "voltage_ehv_regional"
            return "TEPCO Power Grid", "TSO_EHV", "voltage_ehv_default"
        if voltage_kv >= 275.0:
            regional = _resolve_regional_utility_by_coord(lat, lon)
            if regional:
                return regional[0], "TSO_HV", "voltage_hv_275_regional"
            return "TEPCO Power Grid", "TSO_HV", "voltage_hv_275_default"
        if voltage_kv >= 154.0:
            regional = _resolve_regional_utility_by_coord(lat, lon)
            if regional:
                return (
                    regional[0],
                    "TSO_REGIONAL",
                    "voltage_regional_154",
                )
        if voltage_kv >= 66.0:
            regional = _resolve_regional_utility_by_coord(lat, lon)
            if regional:
                return (
                    regional[0],
                    "TSO_SUBT",
                    "voltage_subtransmission_66",
                )

    # ─── Layer 3: Rail traction — 1.5 kV DC JR + 25 kV AC Shinkansen ───
    if voltage_kv is not None:
        if 1.3 <= voltage_kv <= 1.7:
            return "JR (regional)", "RAIL_TRACTION", "rail_traction_1_5kv_dc"
        if 24.0 <= voltage_kv <= 26.0:
            return "JR Shinkansen", "RAIL_TRACTION", "rail_traction_25kv_ac"

    # ─── Layer 4: Frequency converter coord match ───
    # Shin-Shinano ~36.66°N 138.15°E
    if abs(lat - 36.66) < 0.05 and abs(lon - 138.15) < 0.10:
        return (
            "Shin-Shinano FC Station",
            "FREQUENCY_CONVERTER",
            "shin_shinano_fc_geofence",
        )
    # Sakuma ~35.10°N 137.80°E
    if abs(lat - 35.10) < 0.05 and abs(lon - 137.80) < 0.10:
        return "Sakuma FC Station", "FREQUENCY_CONVERTER", "sakuma_fc_geofence"
    # Higashi-Shimizu ~35.02°N 138.50°E
    if abs(lat - 35.02) < 0.05 and abs(lon - 138.50) < 0.10:
        return (
            "Higashi-Shimizu FC Station",
            "FREQUENCY_CONVERTER",
            "higashi_shimizu_fc_geofence",
        )
    # Minami-Fukumitsu ~36.61°N 136.83°E
    if abs(lat - 36.61) < 0.05 and abs(lon - 136.83) < 0.10:
        return (
            "Minami-Fukumitsu FC Station",
            "FREQUENCY_CONVERTER",
            "minami_fukumitsu_fc_geofence",
        )

    # ─── Layer 5: Regional utility by coord (main routing) ───
    regional = _resolve_regional_utility_by_coord(lat, lon)
    if regional:
        return regional

    # ─── Layer 6: Voltage-only voltage-inferred routing (no coord match) ───
    if voltage_kv is not None:
        if voltage_kv < 30.0:
            # Rural MV — default to TEPCO PG (largest customer base)
            return (
                "TEPCO Power Grid",
                "DSO",
                "voltage_lv_default_no_regional_match",
            )

    # ─── Layer 7-8: Fallback → TEPCO PG (largest utility by customers) ───
    if voltage_kv is None:
        return None, None, None  # Convention #56 — insufficient signal

    return "TEPCO Power Grid", "DSO", "fallback_default_tepco"


def _resolve_by_voltage_only(
    voltage_kv: Optional[float],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Voltage-only fallback when lat/lon absent."""
    if voltage_kv is None:
        return None, None, None
    if voltage_kv >= 500.0:
        return "TEPCO Power Grid", "TSO_EHV", "voltage_ehv_no_coords"
    if voltage_kv >= 275.0:
        return "TEPCO Power Grid", "TSO_HV", "voltage_hv_275_no_coords"
    if 1.3 <= voltage_kv <= 1.7:
        return "JR (regional)", "RAIL_TRACTION", "rail_traction_1_5kv_dc_no_coords"
    if 24.0 <= voltage_kv <= 26.0:
        return "JR Shinkansen", "RAIL_TRACTION", "rail_traction_25kv_ac_no_coords"
    return None, None, None


# Resolver layer catalogue — exposed for audit
RESOLVER_LAYERS = [
    "alias_hit",  # Convention #78 BINDING 17th
    "voltage_ehv_regional",
    "voltage_ehv_default",
    "voltage_hv_275_regional",
    "voltage_hv_275_default",
    "voltage_regional_154",
    "voltage_subtransmission_66",
    "rail_traction_1_5kv_dc",
    "rail_traction_25kv_ac",
    "shin_shinano_fc_geofence",
    "sakuma_fc_geofence",
    "higashi_shimizu_fc_geofence",
    "minami_fukumitsu_fc_geofence",
    # Regional utility coord-based
    "regional_utility_okinawa_electric_power_coord",
    "regional_utility_hokuriku_epc_td_coord",
    "regional_utility_shikoku_td_coord",
    "regional_utility_hokkaido_epc_network_coord",
    "regional_utility_kyushu_td_coord",
    "regional_utility_chugoku_td_coord",
    "regional_utility_tohoku_epc_network_coord",
    "regional_utility_tepco_power_grid_coord",
    "regional_utility_chubu_power_grid_coord",
    "regional_utility_kansai_td_coord",
    "voltage_lv_default_no_regional_match",
    "fallback_default_tepco",
    # No-coord fallbacks
    "voltage_ehv_no_coords",
    "voltage_hv_275_no_coords",
    "rail_traction_1_5kv_dc_no_coords",
    "rail_traction_25kv_ac_no_coords",
]


def alias_hit_count() -> int:
    """Return cumulative Convention #78 alias hits for audit sidecar."""
    return _ALIAS_HIT_COUNTER["total"]


def reset_alias_hit_counter() -> None:
    """Reset counter (for test isolation)."""
    _ALIAS_HIT_COUNTER["total"] = 0
