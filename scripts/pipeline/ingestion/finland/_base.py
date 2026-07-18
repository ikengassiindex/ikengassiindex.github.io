"""
SSI Pipeline — Finland v4.23 ingestion, shared base layer.

Wave 3 Priority 29 (eighth Wave 3 country post-Denmark; Nordic
cluster extension via Fingrid TSO + multi-DSO architecture with
Convention #78 §4bis.5 Layer 3 7TH ENFORCEMENT at Helsinki
metropolitan Helen Sähköverkko vs Vantaan Energia vs Caruna
3-way split). FIRST Finnish + Swedish + Sami trilingual Wave 3
event.

⚡ CONVENTION #78 BINDING ENFORCEMENT — 11th EMPIRICAL TEST ⚡
(post 10-country DECADE MILESTONE closed at Denmark P28)

Eleventh country onboarded post Convention #78 sub-convention
BINDING promotion methodology-version event (Latvia Priority 18
closure, 16 July 2026). Preemptive Finnish + Swedish + Sami +
English trilingual alias mapping REQUIRED at Step 3 connector
authoring time:
  - Finnish diacritics via NFC normalization (ä ö å)
  - Swedish diacritics (ä ö å — same set, Åland 100% Swedish)
  - Sami minority diacritics (ŋ ǯ â — Northern/Skolt/Inari)
  - Finnish legal-form variants (Oyj / Oy / Ky / ry)
  - Swedish/Åland legal-form variants (Ab / Abp / AB)
  - Predecessor rebrand cascades:
    * Fortum → Caruna 2014 (Fortum Distribution sale to
      First Sentier Investors + Elo + KEVA consortium)
    * Vattenfall Finland → Elenia 2012 (Vattenfall Nordic sale
      to Ardian + IIF)
    * IVO (Imatran Voima) → Fortum 1998 (Neste merger)
    * Helsingin Energia → Helen 2015 (unbundling +
      Helen Sähköverkko subsidiary)

Finland specifics:
  - Fingrid Oyj — state-owned single national TSO. Operates:
    * 400 kV EHV backbone (Cross-Finland transmission)
    * 220 kV legacy transmission (16 subs — largely superseded)
    * 110 kV MAIN transmission tier (3760 subs in baseline —
      Fingrid TSO + some regional DSOs share this tier)
    * 4 HVDC interconnectors — EstLink 1+2 (Estonia) +
      FennoSkan 1+2 (Sweden)
    * Fenno-Scandia ENTSO-E synchronous grid via Sweden/Norway
    * NO Russian border (post-2022 disconnect via RAO Nordic
      dissolution)
    Established 1996 unbundling.
  - Caruna Oy — LARGEST Finnish DSO. First Sentier Investors +
    Elo + KEVA consortium since 2014 Fortum sale. Coverage:
    Uusimaa (excl Helsinki+Vantaa) + Varsinais-Suomi +
    Satakunta + Etelä-Pohjanmaa + Pohjanmaa + Keski-Pohjanmaa
    (~1M customers = 30% of FI).
  - Elenia Oy — 2nd-LARGEST Finnish DSO. Ardian + IIF ownership
    since 2012 Vattenfall Finland sale + rebrand. Coverage:
    Pirkanmaa (Tampere) + Kanta-Häme + Päijät-Häme + Keski-Suomi
    + Pohjois-Pohjanmaa (~430k customers = 13% of FI).
  - Helen Sähköverkko Oy — Helsinki municipal DSO (Helen Oy
    subsidiary since 2015 unbundling from Helsingin Energia).
    Coverage: Helsinki city (~400k customers = 12% of FI).
    Convention #78 §4bis.5 7TH ENFORCEMENT geofence subject.
  - Vantaan Energia Sähköverkot Oy — Vantaa + Kerava municipal
    DSO. Owned by Vantaa (55%) + Helsinki (35%) + Espoo (10%).
    Coverage: Vantaa northern suburb (~110k customers).
  - Turku Energia Sähköverkot / Åbo Energi — Turku municipal
    DSO (~135k customers).
  - Tampereen Sähkölaitos — Tampere municipal DSO core (~150k
    customers; Elenia covers surrounding Pirkanmaa).
  - Nuclear operators (generation NOT grid):
    * Teollisuuden Voima Oyj (TVO) — Olkiluoto 1+2 BWR +
      Olkiluoto 3 EPR (world's largest, 2023 grid-connected)
    * Fortum — Loviisa 1+2 VVER-440
  - Åland autonomous jurisdiction (Swedish 100%):
    * Kraftnät Åland Ab — TSO (separate HVDC connection to
      Sweden Björkö)
    * Mariehamns Elnät Ab — DSO
  - VR Group — rail traction 25 kV AC electrified main lines:
    * Helsinki-Turku + Helsinki-Tampere-Oulu + Karelia (Helsinki-
      Joensuu) + Coastal line (Helsinki-Kouvola)

Historical predecessors preserved for audit trail:
  - IVO (Imatran Voima, 1932-1998) → Fortum 1998 merger with Neste
  - Fortum Distribution/Sähkönsiirto → Caruna 2014 (Fortum sale)
  - Vattenfall Finland Distribution → Elenia 2012 (Vattenfall Nordic sale)
  - Helsingin Energia → Helen 2015 (unbundling + subsidiary
    Helen Sähköverkko Oy)
  - Pohjolan Voima → industrial captive predecessor
"""

from __future__ import annotations

import hashlib
import json
import logging
import unicodedata
from pathlib import Path

# Re-export country-agnostic dataclasses from Canada _base
from ..canada._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter as _apply_bounds_generic,
    assert_line_parity,
    now_utc_iso,
)

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = PIPELINE_DIR.parent.parent
FI_BOUNDS_JSON = REPO_ROOT / "finland" / "bounds.json"
FI_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
FI_DATA_DIR = PIPELINE_DIR / "data" / "finland"
FI_CACHE_DIR = FI_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 11th enforcement) ──
_DNSP_ALIAS_MAP = {
    # ── Fingrid Oyj (TSO — single national) ──────────────────────────────
    "fingrid": "Fingrid",
    "Fingrid": "Fingrid",
    "fingrid oyj": "Fingrid",
    "fingrid oy": "Fingrid",
    "fingrid abp": "Fingrid",  # Swedish variant
    "finnish grid": "Fingrid",
    "FINGRID": "Fingrid",
    # Predecessor: IVO (Imatran Voima, 1932-1998)
    "ivo": "Fingrid-legacy (IVO Imatran Voima 1932-1998 pre-unbundling)",
    "imatran voima": "Fingrid-legacy (IVO Imatran Voima 1932-1998 pre-unbundling)",
    "imatran voima oy": "Fingrid-legacy (IVO Imatran Voima 1932-1998 pre-unbundling)",
    "IVO": "Fingrid-legacy (IVO Imatran Voima 1932-1998 pre-unbundling)",

    # ── Caruna Oy (LARGEST DSO) ──────────────────────────────────────────
    "caruna": "Caruna",
    "Caruna": "Caruna",
    "caruna oy": "Caruna",
    "caruna oyj": "Caruna",
    "caruna networks": "Caruna",
    "caruna networks oy": "Caruna",
    "CARUNA": "Caruna",
    # Predecessor: Fortum Distribution/Sähkönsiirto → Caruna 2014
    "fortum sähkönsiirto": "Caruna-legacy (Fortum Distribution pre-2014 rebrand)",
    "fortum sahkonsiirto": "Caruna-legacy (Fortum Distribution pre-2014 rebrand)",
    "fortum distribution": "Caruna-legacy (Fortum Distribution pre-2014 rebrand)",
    "fortum verkko": "Caruna-legacy (Fortum Distribution pre-2014 rebrand)",

    # ── Elenia Oy (2nd-LARGEST DSO) ──────────────────────────────────────
    "elenia": "Elenia",
    "Elenia": "Elenia",
    "elenia oy": "Elenia",
    "elenia verkko": "Elenia",
    "elenia verkko oy": "Elenia",
    "ELENIA": "Elenia",
    # Predecessor: Vattenfall Verkko → Elenia 2012
    "vattenfall verkko": "Elenia-legacy (Vattenfall Verkko pre-2012 rebrand)",
    "vattenfall distribution finland": "Elenia-legacy (Vattenfall Distribution pre-2012 rebrand)",
    "vattenfall verkko oy": "Elenia-legacy (Vattenfall Verkko pre-2012 rebrand)",
    "vattenfall": "Elenia-legacy (Vattenfall Finland pre-2012 rebrand)",  # Finland-scope
    # Note: For non-Finland Vattenfall (Sweden), the SE-scoped alias
    # would need to be checked, but this map is Finland-only.

    # ── Helen Sähköverkko Oy (Helsinki metro DSO) ────────────────────────
    "helen sähköverkko": "Helen Sähköverkko",
    "helen sahkoverkko": "Helen Sähköverkko",
    "helen sähköverkko oy": "Helen Sähköverkko",
    "helen sahkoverkko oy": "Helen Sähköverkko",
    "helen elverk": "Helen Sähköverkko",  # Swedish variant
    "helsingfors energi elnät": "Helen Sähköverkko",  # Swedish variant
    "helsingfors energi elnat": "Helen Sähköverkko",
    "helen": "Helen (parent Helen Oy — Helsinki municipal)",
    "helen oy": "Helen (parent Helen Oy — Helsinki municipal)",
    "helsingin energia": "Helen Sähköverkko-legacy (Helsingin Energia pre-2015 unbundling)",
    "HELEN": "Helen (parent Helen Oy — Helsinki municipal)",

    # ── Vantaan Energia Sähköverkot (Helsinki northern suburb DSO) ───────
    "vantaan energia": "Vantaan Energia Sähköverkot",
    "vantaan energia sähköverkot": "Vantaan Energia Sähköverkot",
    "vantaan energia sahkoverkot": "Vantaan Energia Sähköverkot",
    "vantaan energia sähköverkot oy": "Vantaan Energia Sähköverkot",
    "vesv": "Vantaan Energia Sähköverkot",
    "vanda energi": "Vantaan Energia Sähköverkot",  # Swedish variant
    "vanda energi ab": "Vantaan Energia Sähköverkot",

    # ── Turku Energia Sähköverkot (Turku metro DSO) ──────────────────────
    "turku energia": "Turku Energia Sähköverkot",
    "turku energia sähköverkot": "Turku Energia Sähköverkot",
    "turku energia sahkoverkot": "Turku Energia Sähköverkot",
    "turku energia sähköverkot oy": "Turku Energia Sähköverkot",
    "åbo energi": "Turku Energia Sähköverkot",  # Swedish variant (Åbo = Turku)
    "abo energi": "Turku Energia Sähköverkot",
    "abo energi ab": "Turku Energia Sähköverkot",

    # ── Tampereen Sähkölaitos (Tampere metro DSO) ────────────────────────
    "tampereen sähkölaitos": "Tampereen Sähkölaitos",
    "tampereen sahkolaitos": "Tampereen Sähkölaitos",
    "tampereen energia": "Tampereen Sähkölaitos",
    "tampereen energia oy": "Tampereen Sähkölaitos",
    "tampere energia": "Tampereen Sähkölaitos",

    # ── Savon Voima Verkko (Savonia + Kymenlaakso regional) ──────────────
    "savon voima": "Savon Voima Verkko",
    "savon voima verkko": "Savon Voima Verkko",
    "savon voima verkko oy": "Savon Voima Verkko",

    # ── KSS-verkko / Kymenlaakson Sähköverkko ────────────────────────────
    "kss-verkko": "KSS Verkko (Kymenlaakson)",
    "kss verkko": "KSS Verkko (Kymenlaakson)",
    "kymenlaakson sähköverkko": "KSS Verkko (Kymenlaakson)",
    "kymenlaakson sahkoverkko": "KSS Verkko (Kymenlaakson)",

    # ── Lappeenrannan Energia (South Karelia) ────────────────────────────
    "lappeenrannan energia": "Lappeenrannan Energia",
    "lpr energia": "Lappeenrannan Energia",

    # ── Rovaniemen Energia (Lappi capital) ───────────────────────────────
    "rovaniemen energia": "Rovaniemen Energia",
    "rovaniemen verkko": "Rovaniemen Energia",
    "rovaniemen verkko oy": "Rovaniemen Energia",

    # ── Tornion Energia (Tornio border) ──────────────────────────────────
    "tornion energia": "Tornion Energia",
    "torninlaakson sähkö": "Tornion Energia",
    "torninlaakson sahko": "Tornion Energia",

    # ── KSOY-verkko (Keski-Suomi) ────────────────────────────────────────
    "ksoy-verkko": "KSOY Verkko (Keski-Suomen)",
    "ksoy verkko": "KSOY Verkko (Keski-Suomen)",
    "keski-suomen sähkövoima": "KSOY Verkko (Keski-Suomen)",
    "keski-suomen sahkovoima": "KSOY Verkko (Keski-Suomen)",

    # ── Åland Autonomous (Swedish 100%) ──────────────────────────────────
    "kraftnät åland": "Kraftnät Åland (Åland Autonomous TSO)",
    "kraftnat aland": "Kraftnät Åland (Åland Autonomous TSO)",
    "kraftnät åland ab": "Kraftnät Åland (Åland Autonomous TSO)",
    "kraftnat aland ab": "Kraftnät Åland (Åland Autonomous TSO)",
    "mariehamns elnät": "Mariehamns Elnät (Åland Autonomous DSO)",
    "mariehamns elnat": "Mariehamns Elnät (Åland Autonomous DSO)",
    "mariehamns elnät ab": "Mariehamns Elnät (Åland Autonomous DSO)",
    "maarianhaminan sähköverkko": "Mariehamns Elnät (Åland Autonomous DSO)",  # Finnish variant

    # ── VR Group (Rail traction 25 kV AC) ────────────────────────────────
    "vr": "VR Group",
    "VR": "VR Group",
    "vr-yhtymä": "VR Group",
    "vr yhtyma": "VR Group",
    "vr group": "VR Group",
    "vr track": "VR Group",
    "finnish railways": "VR Group",

    # ── TVO Nuclear (Teollisuuden Voima) — GENERATION NOT DSO ────────────
    "tvo": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",
    "TVO": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",
    "teollisuuden voima": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",
    "teollisuuden voima oyj": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",
    "industrial power company": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",

    # ── Fortum (Post-1998 IVO merger; Loviisa nuclear) ────────────────────
    "fortum": "Fortum (Loviisa Nuclear + Generation-Retail — grid=Fingrid)",
    "fortum oyj": "Fortum (Loviisa Nuclear + Generation-Retail — grid=Fingrid)",
    "fortum power and heat": "Fortum (Generation-Retail — grid=Fingrid)",
    "fortum sähkönmyynti": "Fortum (Retail — grid=Fingrid)",
    "fortum sahkonmyynti": "Fortum (Retail — grid=Fingrid)",
    "fortum kraft": "Fortum (Swedish variant — grid=Fingrid)",

    # ── Industrial captives (forestry + steel + telecom) ─────────────────
    "stora enso": "Stora Enso (Industrial Captive — Forest Pulp+Paper)",
    "stora enso oyj": "Stora Enso (Industrial Captive — Forest Pulp+Paper)",
    "upm": "UPM-Kymmene (Industrial Captive — Forest Pulp+Paper)",
    "upm-kymmene": "UPM-Kymmene (Industrial Captive — Forest Pulp+Paper)",
    "upm-kymmene oyj": "UPM-Kymmene (Industrial Captive — Forest Pulp+Paper)",
    "metsä group": "Metsä Group (Industrial Captive — Forest Pulp+Paper)",
    "metsa group": "Metsä Group (Industrial Captive — Forest Pulp+Paper)",
    "metsä-botnia": "Metsä Group (Industrial Captive — Metsä-Botnia Pulp)",
    "metsa-botnia": "Metsä Group (Industrial Captive — Metsä-Botnia Pulp)",
    "metsä fibre": "Metsä Group (Industrial Captive — Metsä Fibre)",
    "metsa fibre": "Metsä Group (Industrial Captive — Metsä Fibre)",
    "outokumpu": "Outokumpu (Industrial Captive — Stainless Steel Tornio)",
    "outokumpu oyj": "Outokumpu (Industrial Captive — Stainless Steel Tornio)",
    "ssab raahe": "SSAB Raahe (Industrial Captive — Steel Raahe)",
    "rautaruukki": "SSAB Raahe (Industrial Captive — Rautaruukki legacy)",
    "nokia": "Nokia (Industrial Captive — Telecom)",
    "nokia oyj": "Nokia (Industrial Captive — Telecom)",
    "neste": "Neste (Industrial Captive — Petrochemical Porvoo/Naantali)",
    "neste oyj": "Neste (Industrial Captive — Petrochemical)",
    "pohjolan voima": "Pohjolan Voima (Industrial Generation Cooperative)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 11th enforcement — preserves Finnish +
    Swedish + Sami diacritic composition (ä ö å + Sami ŋ ǯ â) via NFC
    normalization + Finnish legal-form variants (Oyj/Oy/Ky/ry) +
    Swedish/Åland variants (Ab/Abp/AB) for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Finnish
    + Swedish + Sami diacritic composition preserved via NFC + lower-
    case lookup. Handles trilingual Nordic cohabitation + nuclear
    generation-vs-distribution separation (TVO/Fortum own nuclear
    generation but grid ownership is Fingrid TSO) per Convention #78
    BINDING 11th empirical test (post 10-country DECADE MILESTONE).

    Finland is 11TH cohort-wide event + FIRST post-DECADE-MILESTONE
    country — establishes Nordic cluster precedent (DK + FI) for
    future Sweden/Norway Wave 3 continuations."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── VR Group rail traction identity (Layer 2 — 25 kV AC) ─────────────────
_VR_NAME_PATTERNS = ["vr", "rail", "rautatie", "juna", "traction"]


def _is_vr_traction(name: str | None, voltage_kv: float | None) -> bool:
    """Return True if the substation matches VR Group rail traction.

    25 kV AC electrified main lines (Helsinki-Turku + Helsinki-
    Tampere-Oulu + Karelia + Coastal)."""
    if not name:
        return False
    n = _normalise_key(name)
    if voltage_kv is not None and 24.0 <= voltage_kv <= 26.0:
        if any(pat in n for pat in _VR_NAME_PATTERNS):
            return True
    if "vr group" in n or "rautatie" in n:
        return True
    return False


# ── Nuclear plant identity (Layer 3 — name-match) ────────────────────────
_NUCLEAR_NAME_PATTERNS = {
    "olkiluoto": "TVO Olkiluoto (Nuclear Generation — grid=Fingrid)",
    "ol1": "TVO Olkiluoto OL1 (Nuclear Generation — grid=Fingrid)",
    "ol2": "TVO Olkiluoto OL2 (Nuclear Generation — grid=Fingrid)",
    "ol3": "TVO Olkiluoto OL3 EPR (Nuclear Generation — grid=Fingrid)",
    "loviisa": "Fortum Loviisa (Nuclear Generation — grid=Fingrid)",
    "lo1": "Fortum Loviisa 1 (Nuclear Generation — grid=Fingrid)",
    "lo2": "Fortum Loviisa 2 (Nuclear Generation — grid=Fingrid)",
}


def _detect_nuclear(name: str | None) -> str | None:
    """Return nuclear operator if name matches a Layer 3 pattern."""
    if not name:
        return None
    n = _normalise_key(name)
    for pattern, owner in _NUCLEAR_NAME_PATTERNS.items():
        if pattern in n:
            return owner
    return None


# ── Industrial captive detection (Layer 4 — forest + steel + telecom) ────
_INDUSTRIAL_CAPTIVE_PATTERNS = {
    "stora enso": "Stora Enso (Industrial Captive — Forest Pulp+Paper)",
    "upm": "UPM-Kymmene (Industrial Captive — Forest Pulp+Paper)",
    "metsä": "Metsä Group (Industrial Captive — Forest Pulp+Paper)",
    "metsa": "Metsä Group (Industrial Captive — Forest Pulp+Paper)",
    "outokumpu": "Outokumpu (Industrial Captive — Stainless Steel Tornio)",
    "ssab": "SSAB (Industrial Captive — Steel)",
    "rautaruukki": "SSAB Raahe (Industrial Captive — Rautaruukki legacy)",
    "nokia": "Nokia (Industrial Captive — Telecom)",
    "neste": "Neste (Industrial Captive — Petrochemical)",
    "pohjolan voima": "Pohjolan Voima (Industrial Generation Cooperative)",
}


def _detect_industrial_captive(name: str | None) -> str | None:
    """Return industrial captive owner if name matches Layer 4 pattern."""
    if not name:
        return None
    n = _normalise_key(name)
    for pattern, owner in _INDUSTRIAL_CAPTIVE_PATTERNS.items():
        if pattern in n:
            return owner
    return None


# ── Helsinki §4bis.5 Layer 3 7TH ENFORCEMENT geofence ────────────────────
# Helsinki metropolitan 3-way DSO split:
#   * Helen Sähköverkko — Helsinki city core (~40 km²)
#   * Vantaan Energia — Vantaa northern suburb (~240 km²)
#   * Caruna — Uusimaa outside Helsinki+Vantaa
#
# 7th cohort-wide §4bis.5 enforcement after:
#   1. Prague CZ + 2. Warsaw PL + 3. EWZ Zurich CH + 4. SIG Geneva CH
#   5. Auckland NZ + 6. Copenhagen DK (HIGHEST hits 615)
#   7. NEW: Helsinki FI

_HELEN_HELSINKI_LAT_MIN = 60.15
_HELEN_HELSINKI_LAT_MAX = 60.27  # Helsinki city boundary
_HELEN_HELSINKI_LON_MIN = 24.85
_HELEN_HELSINKI_LON_MAX = 25.20

_VANTAA_LAT_MIN = 60.27  # Vantaa starts north of Helsinki
_VANTAA_LAT_MAX = 60.40
_VANTAA_LON_MIN = 24.85
_VANTAA_LON_MAX = 25.20

_VANTAA_NAME_PATTERNS = [
    "vantaa", "vanda", "tikkurila", "myyrmäki", "myyrmaki",
    "kerava", "korso",
]


def _detect_helsinki_metro_dso(
    lat: float, lon: float, name: str | None
) -> tuple[str, str] | None:
    """Convention #78 §4bis.5 Layer 3 7TH ENFORCEMENT — Helsinki
    metropolitan 3-way DSO split (Helen vs Vantaan Energia vs Caruna).

    Returns (owner, provenance) if lat/lon matches Helsinki metro bbox;
    otherwise None (defers to Layer 6 Uusimaa → Caruna fallback)."""

    # Vantaa detection by name (northern suburb towns)
    if name:
        n = _normalise_key(name)
        if any(pat in n for pat in _VANTAA_NAME_PATTERNS):
            return (
                "Vantaan Energia Sähköverkot",
                "region_jurisdiction_layer_3_4bis5_7th_enforcement_Vantaan_Energia_via_name",
            )

    # Helen (Helsinki city core geofence)
    if (
        _HELEN_HELSINKI_LAT_MIN <= lat <= _HELEN_HELSINKI_LAT_MAX
        and _HELEN_HELSINKI_LON_MIN <= lon <= _HELEN_HELSINKI_LON_MAX
    ):
        return (
            "Helen Sähköverkko",
            "region_jurisdiction_layer_3_4bis5_7th_enforcement_Helen_via_Helsinki_geofence",
        )

    # Vantaan Energia (northern suburb geofence)
    if (
        _VANTAA_LAT_MIN < lat <= _VANTAA_LAT_MAX
        and _VANTAA_LON_MIN <= lon <= _VANTAA_LON_MAX
    ):
        return (
            "Vantaan Energia Sähköverkot",
            "region_jurisdiction_layer_3_4bis5_7th_enforcement_Vantaan_via_geofence",
        )

    return None  # defer to Layer 6 Uusimaa → Caruna


# ── Åland Autonomous Swedish-only carve-out (Layer 4) ────────────────────
# Åland archipelago (Ahvenanmaa) is autonomous Swedish-100% jurisdiction
# with separate energy law (Elmarknadslag) + separate HVDC to Sweden.
# Detection via bbox (west of 21.5 E) OR admin name match.
_ALAND_LON_MAX = 21.5

def _detect_aland(
    lat: float, lon: float, admin_code: str | None
) -> tuple[str, str] | None:
    """Return (owner, provenance) if within Åland autonomous jurisdiction.

    Åland covers Ahvenanmaa admin region + western archipelago bbox.
    Kraftnät Åland is the autonomous TSO."""
    if admin_code:
        norm = _normalise_key(admin_code)
        if norm in ("ahvenanmaa", "åland", "aland"):
            return (
                "Kraftnät Åland (Åland Autonomous TSO)",
                "region_jurisdiction_layer_4_Aland_via_admin",
            )
    if lon <= _ALAND_LON_MAX:
        return (
            "Kraftnät Åland (Åland Autonomous TSO)",
            "region_jurisdiction_layer_4_Aland_via_bbox_west_of_21.5E",
        )
    return None


# ── Region → dominant DSO map (18 maakunta) ──────────────────────────────
_REGION_TO_DOMINANT_DSO = {
    # Metropolitan concentration
    "uusimaa": "Caruna",  # Helsinki via §4bis.5 geofence; Caruna covers surrounding
    # Southern Finland
    "varsinais-suomi": "Caruna",
    "satakunta": "Caruna",
    "kymenlaakso": "KSS Verkko (Kymenlaakson)",
    "etelä-karjala": "Lappeenrannan Energia",
    "etela-karjala": "Lappeenrannan Energia",
    # Central Finland
    "pirkanmaa": "Elenia",
    "kanta-häme": "Elenia",
    "kanta-hame": "Elenia",
    "päijät-häme": "Elenia",
    "paijat-hame": "Elenia",
    "keski-suomi": "Elenia",
    # Western Finland
    "etelä-pohjanmaa": "Caruna",
    "etela-pohjanmaa": "Caruna",
    "pohjanmaa": "Caruna",
    "keski-pohjanmaa": "Caruna",
    # Eastern Finland
    "pohjois-savo": "Savon Voima Verkko",
    "etelä-savo": "Savon Voima Verkko",
    "etela-savo": "Savon Voima Verkko",
    "pohjois-karjala": "Savon Voima Verkko",
    # Northern Finland
    "pohjois-pohjanmaa": "Elenia",
    "kainuu": "Fingrid",  # limited DSO — mostly TSO in Arctic
    "lappi": "Fingrid",   # limited DSO — mostly TSO in Arctic (Rovaniemen Energia in city core)
    # Autonomous
    "ahvenanmaa": "Kraftnät Åland (Åland Autonomous TSO)",
    "åland": "Kraftnät Åland (Åland Autonomous TSO)",
    "aland": "Kraftnät Åland (Åland Autonomous TSO)",
}


def resolve_owner_from_admin(admin_code: str | None) -> str | None:
    """Region-jurisdiction resolver via Finnish 18-maakunta admin code.

    18-region admin partition; each maakunta resolves to dominant DSO.
    Uusimaa requires Layer 3 §4bis.5 sub-cascade for Helsinki
    metropolitan carve-out. Ahvenanmaa handled at Layer 4 via
    _detect_aland."""
    if not admin_code:
        return None
    key = _normalise_key(admin_code).strip()
    key = key.replace(" region", "").replace(" maakunta", "").strip()
    return _REGION_TO_DOMINANT_DSO.get(key)


# ── Fingrid TSO voltage threshold ────────────────────────────────────────
# Finland unique voltage tier signature:
#   400 kV EHV backbone (Cross-Finland Fingrid)
#   220 kV legacy transmission (16 subs — largely superseded)
#   110 kV MAIN transmission tier (3760 baseline subs — Fingrid + some DSO)
#   45 kV Finnish-specific sub-transmission (23 subs)
#   20 kV MV distribution (11 subs)
#
# Rule: ≥110 kV → Fingrid TSO (with Layer 5 direct-OSM catching some DSO)
_FINGRID_TSO_MIN_KV = 110.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    lat: float,
    lon: float,
    admin_code: str | None = None,
    name: str | None = None,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Finland 8-layer multi-DSO resolver (Nordic cluster extension):

      Layer 1: Fingrid TSO threshold (≥110 kV → Fingrid)
      Layer 2: VR Group rail traction (25 kV AC + name match)
      Layer 3a: Nuclear plant name-match (Olkiluoto + Loviisa)
      Layer 3b: §4bis.5 Helsinki metropolitan 3-way geofence
                (Helen city + Vantaan suburb + Caruna region)
                (7TH COHORT-WIDE ENFORCEMENT)
      Layer 4a: Åland autonomous jurisdiction (Swedish-only)
      Layer 4b: Industrial captive (Stora Enso + UPM + Metsä +
                Outokumpu + SSAB + Nokia + Neste + Pohjolan Voima)
      Layer 5: Region → dominant DSO map (18 maakunta × 6 major +
               minor DSOs)
      Layer 6: Fingrid catch-all (safety net)

    15th cohort-wide application of the region-jurisdiction resolver
    (after Belgium + Netherlands + Chile + Hungary + Slovenia + Colombia
    + Norway + Slovakia + Czechia + Iceland + Switzerland + Ireland +
    Korea + New Zealand + Denmark — Finland P29).

    Convention #78 §4bis.5 Layer 3 7TH ENFORCEMENT — Helsinki
    metropolitan 3-way DSO split.
    """
    # Layer 1: Fingrid TSO threshold
    if voltage_kv is not None and voltage_kv >= _FINGRID_TSO_MIN_KV:
        return "Fingrid", "region_jurisdiction_layer_1_Fingrid_TSO_threshold_ge_110kv"

    # Layer 2: VR Group rail traction
    if _is_vr_traction(name, voltage_kv):
        return "VR Group", "region_jurisdiction_layer_2_VR_25kv_AC_traction"

    # Layer 3a: Nuclear plant identity
    nuclear = _detect_nuclear(name)
    if nuclear:
        return nuclear, "region_jurisdiction_layer_3a_nuclear_name_match"

    # Layer 3b: Helsinki §4bis.5 metropolitan geofence (7th enforcement)
    helsinki_result = _detect_helsinki_metro_dso(lat, lon, name)
    if helsinki_result:
        return helsinki_result

    # Layer 4a: Åland autonomous jurisdiction
    aland_result = _detect_aland(lat, lon, admin_code)
    if aland_result:
        return aland_result

    # Layer 4b: Industrial captive
    captive = _detect_industrial_captive(name)
    if captive:
        return captive, "region_jurisdiction_layer_4b_industrial_captive_name_match"

    # Layer 5: Region → dominant DSO map
    if admin_code:
        dso = resolve_owner_from_admin(admin_code)
        if dso:
            return dso, f"region_jurisdiction_layer_5_{dso.replace(' ', '_')}_via_admin_{_normalise_key(admin_code)}"

    # Layer 6: Fingrid catch-all (safety net)
    return "Fingrid", "region_jurisdiction_layer_6_Fingrid_catch_all_default"


# ── Discipline #36 with Finland 5.0 km default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Finland bounds filter with 5.0 km default tolerance.

    Per existing FI entry from Mode 2 remediation — Baltic archipelago
    (Turku archipelago + Åland) + Bothnian coastline + Karelia border
    precedent + 4 HVDC interconnector terminals (EstLink 1+2 Anttila +
    FennoSkan 1+2 Rauma). No Russian cross-border (post-2022
    disconnect)."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(FI_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("countries", {}).get("finland", {}).get("boundary_tolerance_km", 5.0)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 5.0
    return _apply_bounds_generic(
        records, country_slug="finland", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "finland/v4_23-ingestion-audit-finland-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = FI_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("fi-"):
        slug = slug[len("fi-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-finland-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Finland ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/finland/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: finland",
        f"source_id: {result.source_id}",
        f'fetched_at_utc: "{result.fetched_at_utc}"',
        f"source_url: {result.source_url or 'null'}",
        f"raw_bytes_fetched: {result.raw_bytes_fetched}",
        f"raw_sha256: {result.raw_sha256 or 'null'}",
        f"provincial_scope: {result.provincial_scope or 'null'}",
        "",
        "empirical_counts:",
        f"  substations: {len(result.substations)}",
        f"  transmission_lines: {len(result.transmission_lines)}",
        "",
        "discipline_41_line_parity:",
    ]
    for f in parity_findings or []:
        lines.append(f"  - {json.dumps(f)}")
    lines += ["", "warnings:"]
    for w in result.warnings:
        lines.append(f"  - {json.dumps(w)}")
    lines += [
        "",
        "auditability_chain:",
        f"  parent_preflight: {parent_preflight_yaml}",
        "  step_2_fetch: finland/v4_23-ingestion-audit-finland-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: finland/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    FI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return FI_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_region_jurisdiction",
    "resolve_owner_from_admin",
    "normalise_owner_alias",
    "FI_BOUNDS_JSON",
    "FI_TOLERANCE_JSON",
    "FI_DATA_DIR",
    "FI_CACHE_DIR",
]
