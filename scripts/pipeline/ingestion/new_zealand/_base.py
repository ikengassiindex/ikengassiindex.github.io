"""
SSI Pipeline — New Zealand v4.23 ingestion, shared base layer.

Wave 3 Priority 27 (sixth Wave 3 country post-Korea; RICHEST cohort-wide
architecture via 29-EDB multi-DSO cohabitation with Convention #78
§4bis.5 Layer 3 5th enforcement at Auckland metropolitan carve-out —
Vector vs Counties Energy split). FIRST English multi-DSO Wave 3 event.

⚡ CONVENTION #78 BINDING ENFORCEMENT — 9th EMPIRICAL TEST ⚡

Ninth country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive English dominant + Māori Te Reo diacritic
alias mapping REQUIRED at Step 3 connector authoring time:
  - English legal-form variants (Ltd / Limited / PLC — rare in NZ)
  - Māori diacritics via NFC normalization (macrons ā ē ī ō ū)
  - Māori Te Reo native names (Aotearoa cohabit + Ara Whanui
    KiwiRail)
  - Generation-retail separation (Meridian/Mercury/Genesis own
    generation but Transpower owns transmission — must NOT alias
    generation-retail entity to grid substation)
  - Predecessor rebrands: TransPower NZ → Transpower NZ 2011
    (rebrand); Electricity Corporation of New Zealand (ECNZ)
    pre-1996 unbundling → separated into Transpower + Meridian +
    Genesis + Mighty River (now Mercury) + Contact Energy

FIRST Southern Hemisphere Wave 3 event — establishes Māori diacritic
cohort precedent + English multi-DSO precedent for future Australia
Wave 3 continuation.

New Zealand specifics:
  - Transpower New Zealand Ltd — state-owned single national TSO.
    Operates 220 kV EHV backbone + 110/66 kV transmission across
    both islands. Owns 1200 MW Cook Strait HVDC Inter-Island link
    (Kikiwa South + Haywards North; 2 x 350 kV DC bipole 1988 +
    1 x 500 kV DC pole 3 2013). ~11,000 km transmission network.
    Established via 1996 ECNZ unbundling.
  - 29 EDBs (Electricity Distribution Businesses) operating MV/LV
    distribution across 16 NZ regions. Each EDB is a separate
    corporate entity (mix of council-owned Local Purpose Trusts,
    community trusts, and listed companies). Aggregate ~200,000 km
    distribution network.
  - Auckland region (253 subs) split between:
    * Vector — Auckland CBD + North Shore + eastern suburbs
      (~65% of Auckland region)
    * Counties Energy — southern Auckland (Papakura + Franklin +
      Waiuku, ~35%)
    Requires Convention #78 §4bis.5 Layer 3 5th enforcement via
    lat/lon geofence (bbox approx -36.85 to -36.75 lat / 174.65
    to 174.90 lon for Vector; south of -37.00 lat for Counties).
  - Canterbury region (284 subs) split between:
    * Orion NZ — Christchurch + Selwyn + Waimakariri (~65%)
    * MainPower NZ — North Canterbury (Rangiora + Amberley +
      Kaikoura, ~15%)
    * Alpine Energy — South Canterbury (Timaru + Twizel +
      Waimate, ~15%)
    * Network Waitaki — Waitaki district (Oamaru, ~5%)
    Soft-boundary Layer 3 admin-based attribution (no §4bis.5
    geofence — Orion NZ dominant sufficient for parsimony).
  - Cook Strait HVDC Inter-Island link — DOMESTIC (Jeju-analog:
    intra-NZ, NOT cross-border). Transpower owns; 1200 MW capacity
    supports North Island load balancing from South Island hydro.
  - KiwiRail (Ara Whanui in Te Reo Māori) — 25 kV AC electrified
    main trunk line Palmerston North to Hamilton + Auckland metro
    rail 25 kV AC (Puhinui + Papatoetoe + Onehunga branch).
  - NZAS Tiwai Point aluminium smelter (Southland) — largest
    single industrial captive (~13% NZ electricity demand;
    Meridian Energy hydro contract from Manapouri).
  - Methanex NZ — Motunui + Waitara methanol production (Taranaki
    natural gas feedstock).
  - Generation-retail entities OWN generation, NOT distribution:
    * Meridian Energy — Waitaki (Benmore + Aviemore) + Clyde +
      Manapouri + wind + solar (majority hydro; state-owned 51%)
    * Mercury NZ — Waikato hydro (Karapiro + Aratiatia +
      Wairakei) + Taupo geothermal (state-owned 51%)
    * Genesis Energy — Huntly thermal (gas + coal) + Tokaanu +
      Tekapo B (state-owned 51%)
    * Contact Energy — Clyde partial + Wairakei geothermal +
      Rangipo + Stratford gas (private listed)
    * Trustpower — Bay of Plenty hydro (private listed)
  - 16 NZ regions (post-1989 local government reform):
    * NORTH ISLAND: Northland + Auckland + Waikato + Bay of Plenty
      + Gisborne + Hawke's Bay + Taranaki + Manawatu-Whanganui +
      Wellington
    * SOUTH ISLAND: Marlborough + Tasman + Nelson + West Coast +
      Canterbury + Otago + Southland
  - Territorial extensions preserved via bounds.json:
    * Chatham Islands (Rekohu — Moriori Te Reo)
    * Kermadec Islands (Rangitāhua — Māori Te Reo)
    * Tokelau (autonomous territory)
    * NOT Ross Dependency Antarctica (outside grid scope)

Historical predecessors preserved for audit trail:
  - Electricity Corporation of New Zealand (ECNZ, 1987-1996) —
    monolithic pre-unbundling entity; split into Transpower (grid)
    + Meridian + Genesis + Mighty River (now Mercury) + Contact
    Energy (generation-retail) per 1996 Electricity Industry
    Reform Act
  - New Zealand Electricity Department (NZED, 1946-1987) —
    government department pre-corporatisation
  - Municipal/borough council electricity departments pre-1993
    Energy Companies Act reform — many EDBs are corporate
    descendants of council electricity departments (e.g.
    Wellington Electricity was Wellington City Council; Vector
    partly Auckland Electric Power Board)
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
NZ_BOUNDS_JSON = REPO_ROOT / "new-zealand" / "bounds.json"
NZ_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
NZ_DATA_DIR = PIPELINE_DIR / "data" / "new-zealand"
NZ_CACHE_DIR = NZ_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 9th enforcement) ───
# Preemptive English dominant + Māori Te Reo diacritic cohabitation +
# generation-retail separation (Meridian/Mercury/Genesis own generation,
# NOT distribution — must route to Transpower for TSO substations)
_DNSP_ALIAS_MAP = {
    # ── Transpower NZ Ltd (TSO — single national) ────────────────────────
    "transpower": "Transpower",
    "Transpower": "Transpower",
    "transpower ltd": "Transpower",
    "transpower limited": "Transpower",
    "transpower new zealand": "Transpower",
    "transpower nz": "Transpower",
    "transpower new zealand limited": "Transpower",
    "transpower new zealand ltd": "Transpower",
    "transpower nz ltd": "Transpower",
    "TRANSPOWER": "Transpower",
    # Predecessor: ECNZ (1987-1996 pre-unbundling)
    "ecnz": "Transpower-legacy (ECNZ 1987-1996 pre-unbundling)",
    "electricity corporation of new zealand": "Transpower-legacy (ECNZ 1987-1996 pre-unbundling)",
    "electricity corporation of nz": "Transpower-legacy (ECNZ 1987-1996 pre-unbundling)",
    # Predecessor: NZED (1946-1987 pre-corporatisation)
    "nzed": "Transpower-legacy (NZED 1946-1987 pre-corporatisation)",
    "new zealand electricity department": "Transpower-legacy (NZED 1946-1987 pre-corporatisation)",

    # ── AUCKLAND — Vector + Counties Energy (§4bis.5 5th enforcement) ────
    "vector": "Vector",
    "Vector": "Vector",
    "vector ltd": "Vector",
    "vector limited": "Vector",
    "vector aotearoa": "Vector",  # Māori Te Reo cohabitation
    # Predecessor: Auckland Electric Power Board (AEPB pre-1993)
    "aepb": "Vector-legacy (Auckland Electric Power Board pre-1993 reform)",
    "auckland electric power board": "Vector-legacy (Auckland Electric Power Board pre-1993 reform)",
    # Counties Energy (Auckland southern)
    "counties energy": "Counties Energy",
    "counties power": "Counties Energy",
    "counties power ltd": "Counties Energy",
    "counties power limited": "Counties Energy",
    "counties manukau power": "Counties Energy",
    "counties energy ltd": "Counties Energy",

    # ── NORTHLAND — Top Energy + Northpower ──────────────────────────────
    "top energy": "Top Energy",
    "top energy ltd": "Top Energy",
    "top energy limited": "Top Energy",
    "northpower": "Northpower",
    "northpower ltd": "Northpower",
    "northpower limited": "Northpower",

    # ── WAIKATO — WEL Networks + Waipa + The Lines Company + Powerco ─────
    "wel networks": "WEL Networks",
    "wel networks ltd": "WEL Networks",
    "wel networks limited": "WEL Networks",
    "waikato electricity lines": "WEL Networks",
    "wel": "WEL Networks",
    "waipa networks": "Waipa Networks",
    "waipa networks ltd": "Waipa Networks",
    "the lines company": "The Lines Company",
    "the lines company ltd": "The Lines Company",
    "tlc": "The Lines Company",

    # ── BAY OF PLENTY — Horizon Networks + Unison Networks ───────────────
    "horizon networks": "Horizon Networks",
    "horizon networks ltd": "Horizon Networks",
    "horizon energy": "Horizon Networks",
    "horizon energy ltd": "Horizon Networks",
    "unison networks": "Unison Networks",
    "unison networks ltd": "Unison Networks",
    "unison": "Unison Networks",

    # ── GISBORNE — Eastland Network ──────────────────────────────────────
    "eastland network": "Eastland Network",
    "eastland network ltd": "Eastland Network",
    "eastland group": "Eastland Network",

    # ── TARANAKI + MANAWATU-WHANGANUI + WAIRARAPA — Powerco (LARGEST spread) ──
    "powerco": "Powerco",
    "Powerco": "Powerco",
    "powerco ltd": "Powerco",
    "powerco limited": "Powerco",

    # ── MANAWATU — Electra (Kapiti + Horowhenua) ─────────────────────────
    "electra": "Electra",
    "electra ltd": "Electra",
    "electra limited": "Electra",

    # ── WELLINGTON — Wellington Electricity Lines ────────────────────────
    "wellington electricity": "Wellington Electricity",
    "wellington electricity lines": "Wellington Electricity",
    "wellington electricity lines ltd": "Wellington Electricity",
    "wellington electricity lines limited": "Wellington Electricity",
    "well": "Wellington Electricity",  # short-form
    # Predecessor: Wellington City Council
    "wellington city council": "Wellington Electricity-legacy (Wellington City Council pre-1993 reform)",

    # ── MARLBOROUGH ──────────────────────────────────────────────────────
    "marlborough lines": "Marlborough Lines",
    "marlborough lines ltd": "Marlborough Lines",

    # ── NELSON + TASMAN — Network Tasman + Nelson Electricity ────────────
    "network tasman": "Network Tasman",
    "network tasman ltd": "Network Tasman",
    "nelson electricity": "Nelson Electricity",
    "nelson electricity ltd": "Nelson Electricity",

    # ── WEST COAST — Westpower + Buller Electricity ──────────────────────
    "westpower": "Westpower",
    "westpower ltd": "Westpower",
    "buller electricity": "Buller Electricity",
    "buller electricity ltd": "Buller Electricity",

    # ── CANTERBURY — Orion + MainPower + Alpine + Waitaki (4-way) ────────
    "orion": "Orion New Zealand",
    "Orion": "Orion New Zealand",
    "orion nz": "Orion New Zealand",
    "orion new zealand": "Orion New Zealand",
    "orion new zealand ltd": "Orion New Zealand",
    "orion nz ltd": "Orion New Zealand",
    "orion aotearoa": "Orion New Zealand",  # Māori Te Reo cohabitation
    "mainpower nz": "MainPower NZ",
    "mainpower": "MainPower NZ",
    "mainpower new zealand": "MainPower NZ",
    "mainpower nz ltd": "MainPower NZ",
    "alpine energy": "Alpine Energy",
    "alpine energy ltd": "Alpine Energy",
    "network waitaki": "Network Waitaki",
    "network waitaki ltd": "Network Waitaki",

    # ── OTAGO — Aurora Energy + OtagoNet ─────────────────────────────────
    "aurora energy": "Aurora Energy",
    "aurora energy ltd": "Aurora Energy",
    "aurora": "Aurora Energy",
    "otago net": "OtagoNet",
    "otagonet": "OtagoNet",
    "otagonet ltd": "OtagoNet",

    # ── SOUTHLAND — PowerNet + The Power Company ─────────────────────────
    "powernet": "PowerNet",
    "PowerNet": "PowerNet",
    "power net": "PowerNet",
    "powernet ltd": "PowerNet",
    "electricity invercargill": "PowerNet",
    "eil": "PowerNet",
    "the power company": "The Power Company",
    "the power company ltd": "The Power Company",
    "tpc": "The Power Company",

    # ── KiwiRail (Ara Whanui — Māori Te Reo) — Rail Traction ─────────────
    "kiwirail": "KiwiRail",
    "KiwiRail": "KiwiRail",
    "kiwirail ltd": "KiwiRail",
    "kiwirail group": "KiwiRail",
    "ara whanui": "KiwiRail",  # Māori Te Reo name
    "auckland transport": "KiwiRail (Auckland Metro Rail Traction)",
    "at metro": "KiwiRail (Auckland Metro Rail Traction)",
    "kiwirail metro auckland": "KiwiRail (Auckland Metro Rail Traction)",

    # ── NZAS Tiwai Point (Industrial Captive — largest single) ───────────
    "nzas": "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",
    "new zealand aluminium smelters": "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",
    "tiwai point": "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",
    "bluff aluminium": "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",
    "rio tinto aluminium": "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",

    # ── Methanex NZ (Industrial Captive — Taranaki) ──────────────────────
    "methanex": "Methanex NZ (Industrial Captive — Methanol Production)",
    "methanex nz": "Methanex NZ (Industrial Captive — Methanol Production)",
    "methanex motunui": "Methanex NZ (Industrial Captive — Methanol Production)",
    "methanex waitara": "Methanex NZ (Industrial Captive — Methanol Production)",

    # ── Fonterra (Industrial Captive — Dairy CHP multi-region) ───────────
    "fonterra": "Fonterra (Industrial Captive — Dairy CHP)",
    "fonterra cooperative": "Fonterra (Industrial Captive — Dairy CHP)",
    "fonterra cooperative group": "Fonterra (Industrial Captive — Dairy CHP)",

    # ── Generation-Retail (OWNS GENERATION, NOT DISTRIBUTION) ────────────
    # These entities OWN power stations but grid ownership is Transpower.
    # OSM operator= tag on a substation should route to Transpower.
    # If a generation-retail entity's tag appears on a *substation* (not
    # a *power station*), it's a mis-tag — route to Transpower.
    "meridian energy": "Meridian Energy (Generation-Retail — hydro; grid=Transpower)",
    "meridian energy ltd": "Meridian Energy (Generation-Retail — hydro; grid=Transpower)",
    "meridian": "Meridian Energy (Generation-Retail — hydro; grid=Transpower)",
    "meridian aotearoa": "Meridian Energy (Generation-Retail — hydro; grid=Transpower)",
    "mercury nz": "Mercury NZ (Generation-Retail — hydro+geothermal; grid=Transpower)",
    "mercury energy": "Mercury NZ (Generation-Retail — hydro+geothermal; grid=Transpower)",
    "mercury nz ltd": "Mercury NZ (Generation-Retail — hydro+geothermal; grid=Transpower)",
    "mercury": "Mercury NZ (Generation-Retail — hydro+geothermal; grid=Transpower)",
    "genesis energy": "Genesis Energy (Generation-Retail — gas+coal; grid=Transpower)",
    "genesis energy ltd": "Genesis Energy (Generation-Retail — gas+coal; grid=Transpower)",
    "contact energy": "Contact Energy (Generation-Retail — geothermal+gas; grid=Transpower)",
    "contact energy ltd": "Contact Energy (Generation-Retail — geothermal+gas; grid=Transpower)",
    "trustpower": "Trustpower (Generation-Retail — hydro; grid=Transpower)",
    "trustpower ltd": "Trustpower (Generation-Retail — hydro; grid=Transpower)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 9th enforcement — preserves Māori diacritic
    macron composition (ā ē ī ō ū) via NFC normalization + English
    legal-form variants (Ltd/Limited/PLC) + generation-retail
    separation flags for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Māori
    diacritic macron composition preserved via NFC + lower-case lookup.
    Handles English dominant + Māori Te Reo cohabitation + generation-
    retail separation (Meridian/Mercury/Genesis/Contact/Trustpower own
    generation but grid ownership is Transpower — a substation carrying
    a generation-retail tag is a mis-tag and gets flagged for review)
    per Convention #78 BINDING 9th enforcement (9th empirical test
    post-promotion).

    New Zealand is FIRST English multi-DSO Wave 3 country — expected
    30-80 alias-normalisation hits (LOWER than Korean 198 given English
    dominance). Establishes precedent for future English multi-DSO
    Wave 3 continuation (Australia + UK + US + Canada)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── KiwiRail rail traction identity (Layer 2 — 25 kV AC) ─────────────────
_KIWIRAIL_NAME_PATTERNS = [
    "kiwirail", "ara whanui", "rail", "traction",
    "auckland transport", "at metro",
]


def _is_kiwirail_traction(name: str | None, voltage_kv: float | None) -> bool:
    """Return True if the substation matches KiwiRail traction pattern.

    25 kV AC electrified main trunk line traction + Auckland metro."""
    if not name:
        return False
    n = _normalise_key(name)
    # KiwiRail 25 kV AC signature
    if voltage_kv is not None and 24.0 <= voltage_kv <= 26.0:
        if any(pat in n for pat in _KIWIRAIL_NAME_PATTERNS):
            return True
    # Name-only match
    if "kiwirail" in n or "ara whanui" in n:
        return True
    return False


# ── NZAS Tiwai Point identity (Layer 3 — Largest single industrial captive) ──
def _is_nzas_tiwai(name: str | None) -> bool:
    """Return True if the substation matches NZAS Tiwai Point pattern.

    Southland aluminium smelter, largest single NZ electricity consumer."""
    if not name:
        return False
    n = _normalise_key(name)
    return any(pat in n for pat in [
        "nzas", "tiwai point", "tiwai", "bluff aluminium", "rio tinto aluminium",
    ])


# ── Industrial captive detection (Layer 4 — Methanex + Fonterra + others) ──
_INDUSTRIAL_CAPTIVE_PATTERNS = {
    "methanex": "Methanex NZ (Industrial Captive — Methanol Production)",
    "motunui": "Methanex NZ (Industrial Captive — Motunui Methanol)",
    "waitara valley": "Methanex NZ (Industrial Captive — Waitara Methanol)",
    "fonterra": "Fonterra (Industrial Captive — Dairy CHP)",
    "kapuni": "Todd Energy (Industrial Captive — Kapuni Gas)",
    "kupe": "Beach Energy (Industrial Captive — Kupe Gas)",
    "waikato dairy": "Fonterra (Industrial Captive — Dairy CHP)",
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


# ── Auckland §4bis.5 Layer 3 5th enforcement geofence ────────────────────
# Auckland region splits between:
#   * Vector — CBD + North Shore + eastern suburbs (~65%)
#   * Counties Energy — southern Auckland Papakura + Franklin (~35%)
#
# 5th cohort-wide §4bis.5 enforcement after:
#   1. Prague CZ (Czechia P20)
#   2. Warsaw PL (Poland P21)
#   3. EWZ Zurich CH (Switzerland P24)
#   4. SIG Geneva CH (Switzerland P24)
#   5. NEW: Auckland NZ (Vector vs Counties Energy)

# Vector metropolitan geofence bbox — Auckland CBD + North Shore + eastern
# suburbs. Roughly the Auckland Council urban area north of the Manukau
# Harbour, excluding the southern Franklin ward.
_VECTOR_AUCKLAND_LAT_MIN = -37.05
_VECTOR_AUCKLAND_LAT_MAX = -36.65
_VECTOR_AUCKLAND_LON_MIN = 174.55
_VECTOR_AUCKLAND_LON_MAX = 175.05

# Counties Energy detection — south of -37.05 lat OR name contains southern
# Auckland town (Papakura + Franklin + Waiuku + Pukekohe)
_COUNTIES_ENERGY_NAME_PATTERNS = [
    "papakura", "franklin", "waiuku", "pukekohe", "manukau south",
    "clarks beach", "patumahoe", "tuakau",
]


def _detect_auckland_dso(
    lat: float, lon: float, name: str | None
) -> tuple[str, str] | None:
    """Convention #78 §4bis.5 Layer 3 5th enforcement — Auckland Vector vs
    Counties Energy split by lat/lon geofence + name pattern fallback.

    Returns (owner, provenance) if lat/lon matches Auckland region;
    otherwise None (defers to Layer 3 admin-based fallback)."""
    # Check if lat/lon is within Auckland region
    if not (
        _VECTOR_AUCKLAND_LAT_MIN <= lat <= _VECTOR_AUCKLAND_LAT_MAX
        and _VECTOR_AUCKLAND_LON_MIN <= lon <= _VECTOR_AUCKLAND_LON_MAX
    ):
        return None

    # Counties Energy detection by name (southern towns)
    if name:
        n = _normalise_key(name)
        if any(pat in n for pat in _COUNTIES_ENERGY_NAME_PATTERNS):
            return (
                "Counties Energy",
                "region_jurisdiction_layer_3_4bis5_5th_enforcement_Counties_Energy_via_name",
            )

    # Counties Energy detection by lat (south of Manukau Harbour ~-37.00)
    if lat < -37.00:
        return (
            "Counties Energy",
            "region_jurisdiction_layer_3_4bis5_5th_enforcement_Counties_Energy_via_lat",
        )

    # Vector catch-all for remaining Auckland
    return (
        "Vector",
        "region_jurisdiction_layer_3_4bis5_5th_enforcement_Vector_via_geofence",
    )


# ── Canterbury soft-boundary Layer 3 (no §4bis.5 geofence) ───────────────
# Canterbury region splits between:
#   * Orion NZ — Christchurch + Selwyn + Waimakariri (~65%)
#   * MainPower NZ — North Canterbury (~15%)
#   * Alpine Energy — South Canterbury (~15%)
#   * Network Waitaki — Waitaki district (~5%)
#
# Soft-boundary: use lat threshold + name pattern; Orion NZ catch-all.

_MAINPOWER_LAT_MAX = -43.20  # north of Christchurch
_ALPINE_ENERGY_LAT_MIN = -44.30
_ALPINE_ENERGY_LAT_MAX = -43.90  # south of Christchurch
_NETWORK_WAITAKI_LAT_MIN = -45.20
_NETWORK_WAITAKI_LAT_MAX = -44.30  # Waitaki district

_MAINPOWER_NAME_PATTERNS = ["rangiora", "amberley", "kaikoura", "cheviot"]
_ALPINE_ENERGY_NAME_PATTERNS = [
    "timaru", "twizel", "waimate", "geraldine", "temuka", "fairlie",
]
_NETWORK_WAITAKI_NAME_PATTERNS = ["oamaru", "waitaki", "kurow", "duntroon"]


def _detect_canterbury_dso(
    lat: float, name: str | None
) -> tuple[str, str] | None:
    """Canterbury soft-boundary Layer 3 (no §4bis.5 enforcement).

    Returns (owner, provenance) or None (defers to Orion NZ catch-all)."""
    if name:
        n = _normalise_key(name)
        if any(pat in n for pat in _MAINPOWER_NAME_PATTERNS):
            return ("MainPower NZ", "region_jurisdiction_layer_3_Canterbury_MainPower_via_name")
        if any(pat in n for pat in _ALPINE_ENERGY_NAME_PATTERNS):
            return ("Alpine Energy", "region_jurisdiction_layer_3_Canterbury_Alpine_via_name")
        if any(pat in n for pat in _NETWORK_WAITAKI_NAME_PATTERNS):
            return ("Network Waitaki", "region_jurisdiction_layer_3_Canterbury_Waitaki_via_name")

    # Lat-based fallback (rough soft-boundary)
    if lat > _MAINPOWER_LAT_MAX:
        return ("MainPower NZ", "region_jurisdiction_layer_3_Canterbury_MainPower_via_lat")
    if _ALPINE_ENERGY_LAT_MIN <= lat <= _ALPINE_ENERGY_LAT_MAX:
        return ("Alpine Energy", "region_jurisdiction_layer_3_Canterbury_Alpine_via_lat")
    if _NETWORK_WAITAKI_LAT_MIN <= lat <= _NETWORK_WAITAKI_LAT_MAX:
        return ("Network Waitaki", "region_jurisdiction_layer_3_Canterbury_Waitaki_via_lat")

    return None  # Orion catch-all


# ── Region → dominant EDB map (16 regions × 29 EDBs) ─────────────────────
# For regions with multiple EDBs, the DOMINANT EDB (largest customer
# count / geographic coverage) is chosen as the Layer 3 attribution.
# Refined attribution requires §4bis.5 geofence (Auckland) or soft-
# boundary detection (Canterbury) at Layer 3 sub-cascade.
_REGION_TO_DOMINANT_DSO = {
    # ── NORTH ISLAND ──
    "northland": "Top Energy",         # Top Energy northern; Northpower southern (both routed here)
    "auckland": "Vector",              # Vector metropolitan (Counties Energy via §4bis.5)
    "waikato": "WEL Networks",         # Multi-EDB but WEL dominant (Hamilton urban)
    "bay of plenty": "Horizon Networks",  # Horizon + Unison (Rotorua)
    "gisborne": "Eastland Network",
    "hawke's bay": "Unison Networks",
    "hawkes bay": "Unison Networks",   # ASCII variant
    "taranaki": "Powerco",
    "manawatu-whanganui": "Powerco",
    "manawatu-wanganui": "Powerco",    # variant
    "wellington": "Wellington Electricity",  # WELL metropolitan (Powerco Wairarapa cross-boundary)
    # ── SOUTH ISLAND ──
    "marlborough": "Marlborough Lines",
    "nelson": "Nelson Electricity",
    "tasman": "Network Tasman",
    "west coast": "Westpower",
    "canterbury": "Orion New Zealand",  # Orion metropolitan (soft-boundary Layer 3 sub-cascade)
    "otago": "Aurora Energy",
    "southland": "PowerNet",
    # ── OFFSHORE TERRITORIAL EXTENSIONS ──
    "chatham islands": "Transpower",   # offshore territorial extension (Chatham Islands own generator + no EDB structure)
    "chathams": "Transpower",
    "kermadec": "Transpower",
    "tokelau": "Transpower",
}


def resolve_owner_from_admin(admin_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NZ region name.

    16-region admin partition; each region resolves to dominant EDB.
    Auckland + Canterbury require Layer 3 §4bis.5 sub-cascade for
    refined attribution."""
    if not admin_code:
        return None
    key = _normalise_key(admin_code).replace(" region", "").strip()
    return _REGION_TO_DOMINANT_DSO.get(key)


# ── Transpower TSO voltage threshold ─────────────────────────────────────
# Transpower operates 220/110/66 kV backbone. Below 66 kV → distribution
# (29 EDBs). ≥110 kV → Transpower TSO unambiguously.
# 66 kV is ambiguous: some subs are Transpower-owned, some EDB-owned.
# Rule: ≥110 kV → Transpower; <110 kV → EDB via Layer 3.
_TRANSPOWER_TSO_MIN_KV = 110.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    lat: float,
    lon: float,
    admin_code: str | None = None,
    name: str | None = None,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    NZ RICHEST cohort-wide multi-DSO resolver — 5-layer cascade:

      Layer 1: Transpower TSO threshold (≥110 kV → Transpower)
      Layer 2: KiwiRail rail traction (25 kV AC + name match)
      Layer 3: NZAS Tiwai Point aluminium smelter (name match)
      Layer 4: Industrial captive (Methanex + Fonterra + others)
      Layer 5a: §4bis.5 Auckland Vector vs Counties Energy geofence
                (5TH COHORT-WIDE ENFORCEMENT)
      Layer 5b: Canterbury soft-boundary (Orion + MainPower + Alpine + Waitaki)
      Layer 6: Region → dominant EDB map (14 other regions)
      Layer 7: Transpower catch-all (safety net)

    13th cohort-wide application of the region-jurisdiction resolver
    (after Belgium + Netherlands + Chile + Hungary + Slovenia + Colombia
    + Norway + Slovakia + Czechia + Iceland + Switzerland + Ireland +
    Korea — New Zealand P27).

    Convention #78 §4bis.5 Layer 3 5th enforcement — Auckland metro
    split (Vector vs Counties Energy) required due to 253-sub Auckland
    region ambiguity.
    """
    # Layer 1: Transpower TSO threshold
    if voltage_kv is not None and voltage_kv >= _TRANSPOWER_TSO_MIN_KV:
        return "Transpower", "region_jurisdiction_layer_1_Transpower_TSO_threshold_ge_110kv"

    # Layer 2: KiwiRail rail traction
    if _is_kiwirail_traction(name, voltage_kv):
        return "KiwiRail", "region_jurisdiction_layer_2_KiwiRail_25kv_AC_traction"

    # Layer 3: NZAS Tiwai Point
    if _is_nzas_tiwai(name):
        return (
            "NZAS Tiwai Point (Industrial Captive — Aluminium Smelter)",
            "region_jurisdiction_layer_3_NZAS_Tiwai_Point_name_match",
        )

    # Layer 4: Industrial captive
    captive = _detect_industrial_captive(name)
    if captive:
        return captive, "region_jurisdiction_layer_4_industrial_captive_name_match"

    # Layer 5a: Auckland §4bis.5 geofence (5th cohort-wide enforcement)
    auckland_result = _detect_auckland_dso(lat, lon, name)
    if auckland_result:
        return auckland_result

    # Layer 5b: Canterbury soft-boundary
    if admin_code:
        norm_admin = _normalise_key(admin_code).replace(" region", "").strip()
        if norm_admin == "canterbury":
            canterbury_result = _detect_canterbury_dso(lat, name)
            if canterbury_result:
                return canterbury_result
            return (
                "Orion New Zealand",
                "region_jurisdiction_layer_5b_Canterbury_Orion_catch_all",
            )

    # Layer 6: Region → dominant EDB map
    if admin_code:
        dso = resolve_owner_from_admin(admin_code)
        if dso:
            return dso, f"region_jurisdiction_layer_6_{dso.replace(' ', '_')}_via_admin_{_normalise_key(admin_code)}"

    # Layer 7: Transpower catch-all (safety net)
    return "Transpower", "region_jurisdiction_layer_7_Transpower_catch_all_default"


# ── Discipline #36 with NZ 5.0 km default tolerance ──────────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """New Zealand bounds filter with 5.0 km default tolerance.

    Per existing NZ entry from Mode 2 remediation — Pacific coastline
    complexity (North Cape + East Cape + Coromandel + Fiordland + Stewart
    Island) + territorial extensions (Chatham + Kermadec + Tokelau)
    warrant 5.0 km tolerance (50× cadastral default). Cook Strait HVDC
    interconnector is DOMESTIC (Jeju-analog: intra-NZ, NOT cross-border);
    bounds.json 24-feature polygon includes territorial extensions per
    Mode 3 pattern from Discipline #36 remediation."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(NZ_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("countries", {}).get("new-zealand", {}).get("boundary_tolerance_km", 5.0)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 5.0
    return _apply_bounds_generic(
        records, country_slug="new-zealand", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "new-zealand/v4_23-ingestion-audit-new-zealand-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = NZ_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("nz-"):
        slug = slug[len("nz-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-new-zealand-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — New Zealand ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/new_zealand/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: new-zealand",
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
        "  step_2_fetch: new-zealand/v4_23-ingestion-audit-new-zealand-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: new-zealand/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    NZ_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return NZ_CACHE_DIR / f"{key}{ext}"


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
    "NZ_BOUNDS_JSON",
    "NZ_TOLERANCE_JSON",
    "NZ_DATA_DIR",
    "NZ_CACHE_DIR",
]
