"""
SSI Pipeline — Czechia v4.23 ingestion, shared base layer.

Region-jurisdiction × voltage-class monopoly via ČEPS TSO + 3 regional
DSOs (ČEZ Distribuce dominant + EG.D south + PRE distribuce Prague metro)
via Layer 3 lat/lon geofence with PRE metro carve-out. 8th cohort-wide
application of region-jurisdiction fallback pattern (after Belgium +
Netherlands + Chile + Hungary + Slovenia + Colombia + Norway + Slovakia).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 2nd EMPIRICAL TEST ⚡

Second country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026) and Layer 3 geofence sub-convention codification (Slovakia
Priority 19, 16 July 2026). Preemptive multi-script alias mapping +
Layer 3 geofence REQUIRED at Step 3 connector authoring time:
  - Czech NFC diacritics (ě š č ř ž ý á í é ú ů ň ť ď ó)
  - Czech typographic quotes („..." like Latvian/German + Slovak sibling)
  - Cyrillic aliases (Ukrainian minority OSM contributors in eastern
    Bohemia + Silesia bordering Slovakia + Poland)
  - Historical predecessor legacies (pre-2003 5-region DSO merger +
    2021 E.ON → EG.D rebrand — LARGEST predecessor alias class expected
    cohort-wide, 2-4 years since rebrand)
  - Comma-separated legal-form variants (Czech commercial registry
    "a. s." with space + "a.s." without) — Slovak precedent extended

Czechia specifics:
  - ČEPS a.s. (Česká energetická přenosová soustava) — state TSO
    (100% state-owned via MPO Ministry of Industry and Trade), operates
    400/220/110 kV EHV backbone including cross-border interconnections
    with DE + AT + SK + PL. ~5,600 km transmission network.
  - ČEZ Distribuce a.s. — LARGEST DSO, parent ČEZ Group (69.8% state-
    owned via MPO). Voltage: 110 kV + 22/35 kV MV + 0.4 kV LV. Territory:
    Bohemia excluding Prague + Silesia + Moravia excluding EG.D south.
    ~3.7M connections (~65% national market).
  - EG.D a.s. — DSO, rebranded 2021 from E.ON Distribuce (E.ON Germany
    sold Czech operations to Sazka Group). Voltage: 110 kV + MV + LV.
    Territory: South Bohemia + South Moravia + parts of Vysočina + Zlín.
    ~1.2M connections (~15% national market).
  - PRE distribuce a.s. — Prague metro monopoly DSO. Voltage: 110 kV +
    MV + LV. Territory: Prague metropolitan area ONLY (bbox 49.94-50.18
    lat, 14.22-14.75 lon). ~750,000 connections (~4% national market).
    Parent: Pražská energetika a.s. (58% EnBW Germany + 42% City of Prague).
  - Historical predecessors preserved for audit trail:
    * ČEZ absorbed 5 pre-2003 regional DSOs: Východočeská + Severomoravská
      + Středočeská + Západočeská + Severočeská energetika
    * EG.D was E.ON Distribuce until 2021 rebrand (2-4 year old OSM tags
      still carry E.ON — LARGEST predecessor class cohort-wide)
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
CZECHIA_BOUNDS_JSON = REPO_ROOT / "czechia" / "bounds.json"
CZECHIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
CZECHIA_DATA_DIR = PIPELINE_DIR / "data" / "czechia"
CZECHIA_CACHE_DIR = CZECHIA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 2nd enforcement) ───
# Preemptive multi-script mapping: Czech NFC + Cyrillic + typographic
# quotes + comma-separated legal-form variants + E.ON→EG.D rebrand
_DNSP_ALIAS_MAP = {
    # ── ČEPS variants (TSO) ────────────────────────────────────────────
    "ceps": "CEPS",
    "čeps": "CEPS",
    "ceps a.s.": "CEPS",
    "čeps a.s.": "CEPS",
    "ceps, a.s.": "CEPS",
    "čeps, a.s.": "CEPS",
    "ceps a. s.": "CEPS",   # space variant (Slovak precedent)
    "čeps a. s.": "CEPS",
    "ceps, a. s.": "CEPS",
    "čeps, a. s.": "CEPS",
    "česká energetická přenosová soustava": "CEPS",
    "ceska energeticka prenosova soustava": "CEPS",   # accent-stripped
    "česká energetická přenosová soustava a.s.": "CEPS",
    "ceska energeticka prenosova soustava a.s.": "CEPS",
    # ČEPS Cyrillic (rare — Ukrainian OSM contributions eastern Silesia)
    "чепс": "CEPS",
    "ческа енергетичка преносова соустава": "CEPS",

    # ── ČEZ Distribuce variants (LARGEST DSO) ──────────────────────────
    "cez distribuce": "CEZ Distribuce",
    "čez distribuce": "CEZ Distribuce",
    "cez distribuce a.s.": "CEZ Distribuce",
    "čez distribuce a.s.": "CEZ Distribuce",
    "cez distribuce, a.s.": "CEZ Distribuce",
    "čez distribuce, a.s.": "CEZ Distribuce",
    "cez distribuce a. s.": "CEZ Distribuce",
    "čez distribuce a. s.": "CEZ Distribuce",
    "cez distribuce, a. s.": "CEZ Distribuce",
    "čez distribuce, a. s.": "CEZ Distribuce",
    "cezd": "CEZ Distribuce",
    "čezd": "CEZ Distribuce",
    # ČEZ Distribuce Cyrillic
    "чез дистрибуце": "CEZ Distribuce",
    "чез дистрибуце а.с.": "CEZ Distribuce",
    # ČEZ Group parent (may appear on some tags — preserve honestly)
    "cez": "CEZ Group (Holding — Parent)",
    "čez": "CEZ Group (Holding — Parent)",
    "cez a.s.": "CEZ Group (Holding — Parent)",
    "čez a.s.": "CEZ Group (Holding — Parent)",
    "cez group": "CEZ Group (Holding — Parent)",
    "čez group": "CEZ Group (Holding — Parent)",
    "cez, a.s.": "CEZ Group (Holding — Parent)",
    "čez, a.s.": "CEZ Group (Holding — Parent)",
    # ČEZ Prodej (retail arm — should NOT appear on substations but may leak)
    "cez prodej": "CEZ Prodej (Retail)",
    "čez prodej": "CEZ Prodej (Retail)",
    "cez prodej a.s.": "CEZ Prodej (Retail)",
    "čez prodej a.s.": "CEZ Prodej (Retail)",
    # ČEZ Distribuce pre-2003 predecessors (5-region DSO merger)
    "východočeská energetika": "CEZ Distribuce-legacy (VCE Východočeská)",
    "vychodoceska energetika": "CEZ Distribuce-legacy (VCE Východočeská)",
    "severomoravská energetika": "CEZ Distribuce-legacy (SME Severomoravská)",
    "severomoravska energetika": "CEZ Distribuce-legacy (SME Severomoravská)",
    "středočeská energetická": "CEZ Distribuce-legacy (STE Středočeská)",
    "stredoceska energeticka": "CEZ Distribuce-legacy (STE Středočeská)",
    "západočeská energetika": "CEZ Distribuce-legacy (ZCE Západočeská)",
    "zapadoceska energetika": "CEZ Distribuce-legacy (ZCE Západočeská)",
    "severočeská energetika": "CEZ Distribuce-legacy (SCE Severočeská)",
    "severoceska energetika": "CEZ Distribuce-legacy (SCE Severočeská)",

    # ── EG.D variants (South DSO — LARGEST predecessor class E.ON→EG.D) ─
    "eg.d": "EG.D",
    "eg. d": "EG.D",
    "egd": "EG.D",
    "eg.d a.s.": "EG.D",
    "egd a.s.": "EG.D",
    "eg.d, a.s.": "EG.D",
    "egd, a.s.": "EG.D",
    "eg.d a. s.": "EG.D",
    "egd a. s.": "EG.D",
    "eg.d, a. s.": "EG.D",
    "egd, a. s.": "EG.D",
    # EG.D Cyrillic
    "ег.д": "EG.D",
    "егд": "EG.D",
    # E.ON Distribuce pre-2021 rebrand — LARGEST predecessor class expected
    # (2-4 years since rebrand — many OSM tags still carry legacy E.ON)
    "e.on distribuce": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on distribuce a.s.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on distribuce, a.s.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on distribuce, a. s.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on distribuce a. s.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on česká republika": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on ceska republika": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on česká republika s.r.o.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on ceska republika s.r.o.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "e.on": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "eon distribuce": "EG.D-legacy (E.ON pre-2021 rebrand)",   # no dot variant
    "eon distribuce a.s.": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "eon": "EG.D-legacy (E.ON pre-2021 rebrand)",
    "eon.energie": "EG.D-legacy (E.ON pre-2021 rebrand)",
    # EG.D pre-2001 South Bohemia + South Moravia predecessors
    "jihočeská energetika": "EG.D-legacy (JCE Jihočeská pre-2001)",
    "jihoceska energetika": "EG.D-legacy (JCE Jihočeská pre-2001)",
    "jce": "EG.D-legacy (JCE Jihočeská pre-2001)",
    "jihomoravská energetika": "EG.D-legacy (JME Jihomoravská pre-2001)",
    "jihomoravska energetika": "EG.D-legacy (JME Jihomoravská pre-2001)",
    "jme": "EG.D-legacy (JME Jihomoravská pre-2001)",

    # ── PRE distribuce variants (Prague metro DSO) ─────────────────────
    "pre distribuce": "PRE distribuce",
    "pre distribuce a.s.": "PRE distribuce",
    "pre distribuce, a.s.": "PRE distribuce",
    "pre distribuce a. s.": "PRE distribuce",
    "pre distribuce, a. s.": "PRE distribuce",
    "pred": "PRE distribuce",
    # PRE distribuce Cyrillic
    "пре дистрибуце": "PRE distribuce",
    # Pražská energetika (PRE parent holding — may appear on some tags)
    "pražská energetika": "PRE (Holding — Pražská energetika)",
    "prazska energetika": "PRE (Holding — Pražská energetika)",
    "pražská energetika a.s.": "PRE (Holding — Pražská energetika)",
    "prazska energetika a.s.": "PRE (Holding — Pražská energetika)",
    "pre": "PRE (Holding — Pražská energetika)",   # ambiguous — parent

    # ── Czech Railways (electric traction 25 kV AC 50 Hz + 3 kV DC) ────
    "české dráhy": "Czech Railways (Electric Traction)",
    "ceske drahy": "Czech Railways (Electric Traction)",
    "české dráhy a.s.": "Czech Railways (Electric Traction)",
    "cd energetika": "Czech Railways (Electric Traction)",
    "čd energetika": "Czech Railways (Electric Traction)",
    "čd": "Czech Railways (Electric Traction)",
    "cd": "Czech Railways (Electric Traction)",
    "správa železnic": "Czech Railways Infrastructure Manager",
    "sprava zeleznic": "Czech Railways Infrastructure Manager",

    # ── Prague public transport (tram + metro traction) ────────────────
    "dopravní podnik hl. m. prahy": "Dopravní podnik Prahy (Public Transport)",
    "dopravni podnik hl. m. prahy": "Dopravní podnik Prahy (Public Transport)",
    "dpp": "Dopravní podnik Prahy (Public Transport)",
    "dopravní podnik hl. m. prahy a.s.": "Dopravní podnik Prahy (Public Transport)",

    # ── Brno + Ostrava public transport ────────────────────────────────
    "dopravní podnik měst brna": "Dopravní podnik Brna (Public Transport)",
    "dopravni podnik mest brna": "Dopravní podnik Brna (Public Transport)",
    "dpmb": "Dopravní podnik Brna (Public Transport)",
    "dopravní podnik ostrava": "Dopravní podnik Ostrava (Public Transport)",
    "dopravni podnik ostrava": "Dopravní podnik Ostrava (Public Transport)",
    "dpo": "Dopravní podnik Ostrava (Public Transport)",

    # ── Industrial captives ────────────────────────────────────────────
    "škoda auto": "Škoda Auto (Industrial Captive — Mladá Boleslav)",
    "skoda auto": "Škoda Auto (Industrial Captive — Mladá Boleslav)",
    "škoda auto a.s.": "Škoda Auto (Industrial Captive — Mladá Boleslav)",
    "unipetrol": "Unipetrol (Industrial Captive — Refinery)",
    "unipetrol a.s.": "Unipetrol (Industrial Captive — Refinery)",
    "orlen unipetrol": "Unipetrol (Industrial Captive — Refinery)",
    "sokolovská uhelná": "Sokolovská uhelná (Industrial Captive — Lignite)",
    "sokolovska uhelna": "Sokolovská uhelná (Industrial Captive — Lignite)",
    "arcelormittal ostrava": "ArcelorMittal Ostrava (Industrial Captive — Steel)",
    "arcelormittal": "ArcelorMittal Ostrava (Industrial Captive — Steel)",
    "liberty ostrava": "ArcelorMittal Ostrava (Industrial Captive — Steel)",   # 2019 rebrand
    "třinecké železárny": "Třinecké železárny (Industrial Captive — Steel)",
    "trinecke zelezarny": "Třinecké železárny (Industrial Captive — Steel)",
    "vítkovice": "Vítkovice (Industrial Captive — Steel)",
    "vitkovice": "Vítkovice (Industrial Captive — Steel)",

    # ── Czech typographic-quote variants (Latvia + Slovak precedent) ───
    # Czech uses „..." (U+201E + U+201C) bottom-open + top-close
    'as "čez distribuce"': "CEZ Distribuce",
    'as „čez distribuce"': "CEZ Distribuce",
    'a.s. „čez distribuce"': "CEZ Distribuce",
    'as "cez distribuce"': "CEZ Distribuce",
    'as „cez distribuce"': "CEZ Distribuce",
    'as "eg.d"': "EG.D",
    'as „eg.d"': "EG.D",
    'as "e.on distribuce"': "EG.D-legacy (E.ON pre-2021 rebrand)",
    'as „e.on distribuce"': "EG.D-legacy (E.ON pre-2021 rebrand)",
    'as "pre distribuce"': "PRE distribuce",
    'as „pre distribuce"': "PRE distribuce",
    'as "čeps"': "CEPS",
    'as „čeps"': "CEPS",
    'as "ceps"': "CEPS",
    'as „ceps"': "CEPS",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING enforcement — preserves multi-script diacritics
    (Czech NFC ě š č ř ž ý á í é ú ů ň ť ď ó) + Cyrillic (Ukrainian
    minority eastern Silesia) + typographic quotes („..." Czech style)."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Czech
    diacritics preserved in input, normalised via NFC + lower-case lookup.
    Handles Cyrillic aliases from eastern Silesia Ukrainian OSM
    contributors + Czech typographic-quote variants per Convention #78
    BINDING enforcement (2nd empirical test post-promotion).

    E.ON → EG.D 2021 rebrand handled as LARGEST predecessor alias class
    cohort-wide."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 to DSO map ────────────────────────────────────────────────────
# Czechia OSM does NOT populate ref:nuts:3 tags on substations (empirical
# hypothesis Slovenia + Slovakia precedent). Forward-compat surface below;
# actual attribution flows via Layer 3 geofence.
# Czech NUTS-3 codes: CZ010 Praha + CZ020 Středočeský + CZ031 Jihočeský +
# CZ032 Plzeňský + CZ041 Karlovarský + CZ042 Ústecký + CZ051 Liberecký +
# CZ052 Královéhradecký + CZ053 Pardubický + CZ063 Vysočina +
# CZ064 Jihomoravský + CZ071 Olomoucký + CZ072 Zlínský + CZ080 Moravskoslezský
_NUTS3_TO_DSO = {
    # PRE distribuce (Prague metro ONLY)
    "CZ010": "PRE distribuce",  # Hlavní město Praha
    # EG.D (South Bohemia + South Moravia + parts of Vysočina + Zlín)
    "CZ031": "EG.D",             # Jihočeský (South Bohemia — full)
    "CZ064": "EG.D",             # Jihomoravský (South Moravia — full)
    "CZ063": "EG.D",             # Vysočina (partial — many subs go to EG.D)
    "CZ072": "EG.D",             # Zlínský (partial — many subs go to EG.D)
    # ČEZ Distribuce (all other regions — largest territory)
    "CZ020": "CEZ Distribuce",   # Středočeský
    "CZ032": "CEZ Distribuce",   # Plzeňský
    "CZ041": "CEZ Distribuce",   # Karlovarský
    "CZ042": "CEZ Distribuce",   # Ústecký
    "CZ051": "CEZ Distribuce",   # Liberecký
    "CZ052": "CEZ Distribuce",   # Královéhradecký
    "CZ053": "CEZ Distribuce",   # Pardubický
    "CZ071": "CEZ Distribuce",   # Olomoucký
    "CZ080": "CEZ Distribuce",   # Moravskoslezský
}


def resolve_owner_from_nuts3(nuts3_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NUTS-3 code."""
    if not nuts3_code:
        return None
    return _NUTS3_TO_DSO.get(nuts3_code.strip().upper())


# ── Layer 3 lat/lon geofence (Slovenia + Slovakia precedent) ─────────────
# Czechia OSM does not populate ref:nuts:3 tags on substations (empirical
# finding hypothesis — Slovenia Priority 12 + Slovakia Priority 19
# precedent). Add lat/lon geofence for DSO attribution.
#
# Czech territorial partition — 3 DSOs + TSO:
#   PRE distribuce (Prague metro) — bbox 49.94-50.18 lat, 14.22-14.75 lon
#   EG.D (South) — 2 disjoint bboxes:
#     - South Bohemia: lon < 15.50 AND lat < 49.60
#     - South Moravia: 15.50 <= lon < 17.20 AND lat < 49.30
#   ČEZ Distribuce (default catch-all) — everything else
#   ČEPS (TSO — only via voltage threshold Layer 1)
#
# Czechia bounds: 48.55 <= lat <= 51.06, 12.09 <= lon <= 18.87

# PRE distribuce historic Prague concession area (empirically refined
# post synthetic-cache dry-run, 16 July 2026). NOT Prague administrative
# bounds — Praha-východ + Praha-západ + adjacent Central Bohemia territory
# is ČEZ Distribuce, not PRE. PRE serves only the historic Prague core.
# Slovakia + Czechia empirical precedent: Layer 3 geofence bbox refinement
# when DSO distribution diverges >±10% from baseline region_split.
_PRE_PRAGUE_LAT_MIN = 50.00
_PRE_PRAGUE_LAT_MAX = 50.15
_PRE_PRAGUE_LON_MIN = 14.30
_PRE_PRAGUE_LON_MAX = 14.62

# EG.D South Bohemia bbox (Jihočeský kraj — Priority 1 bbox)
_EGD_SOUTH_BOHEMIA_LON_MAX = 15.50    # west of ~15.50
_EGD_SOUTH_BOHEMIA_LAT_MAX = 49.60    # south of ~49.60

# EG.D South Moravia bbox (Jihomoravský kraj — Priority 2 bbox)
_EGD_SOUTH_MORAVIA_LON_MIN = 15.50
_EGD_SOUTH_MORAVIA_LON_MAX = 17.20
_EGD_SOUTH_MORAVIA_LAT_MAX = 49.30    # south of ~49.30

# Czechia national bounds sanity check
_CZ_LAT_MIN = 48.55
_CZ_LAT_MAX = 51.06
_CZ_LON_MIN = 12.09
_CZ_LON_MAX = 18.87


def resolve_owner_from_lat_lon_geofence(lat: float, lon: float) -> str | None:
    """Czech 3-way DSO territorial partition via metro + 2-bbox composition.

    Slovenia + Slovakia precedent (Priority 12 + Priority 19) — apply when
    OSM does not populate NUTS-3 tags. Convention #78 BINDING enforcement
    Layer 3 geofence sub-convention: when NUTS-3 tag absent, geofence MUST
    be preemptively coded at Step 3 connector authoring time.

    Czechia empirically GENERALIZES the sub-convention from Slovakia's
    linear longitude partition to metro-carve-out + multi-bbox composition:
      Layer 3a: PRE Prague metro bbox (Hlavní město Praha administrative)
      Layer 3b: EG.D South Bohemia bbox (west-south)
      Layer 3c: EG.D South Moravia bbox (east-south)
      Layer 3d: ČEZ Distribuce default catch-all (largest territory)

    Returns DSO code or None if lat/lon outside Czech bounds.
    """
    # Sanity check — within Czechia bounds
    if not (_CZ_LAT_MIN <= lat <= _CZ_LAT_MAX and _CZ_LON_MIN <= lon <= _CZ_LON_MAX):
        return None

    # Layer 3a: PRE Prague metro bbox (checked first — smallest territory)
    if (_PRE_PRAGUE_LAT_MIN <= lat <= _PRE_PRAGUE_LAT_MAX
            and _PRE_PRAGUE_LON_MIN <= lon <= _PRE_PRAGUE_LON_MAX):
        return "PRE distribuce"

    # Layer 3b: EG.D South Bohemia bbox
    if lon < _EGD_SOUTH_BOHEMIA_LON_MAX and lat < _EGD_SOUTH_BOHEMIA_LAT_MAX:
        return "EG.D"

    # Layer 3c: EG.D South Moravia bbox
    if (_EGD_SOUTH_MORAVIA_LON_MIN <= lon < _EGD_SOUTH_MORAVIA_LON_MAX
            and lat < _EGD_SOUTH_MORAVIA_LAT_MAX):
        return "EG.D"

    # Layer 3d: ČEZ Distribuce default catch-all (largest DSO territory)
    return "CEZ Distribuce"


# ── ČEPS TSO voltage threshold ───────────────────────────────────────────
# ČEPS operates 400/220/110 kV EHV backbone. Below 220 kV → DSO
# jurisdiction via NUTS-3 map or lat/lon geofence. 110 kV MIXED tier —
# default to ČEPS if voltage present but no territorial resolution.
_CEPS_TSO_MIN_KV = 220.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None, lat: float, lon: float, nuts3: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Region-jurisdiction × voltage-class resolver — 8th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary + Slovenia
    + Colombia + Norway + Slovakia). Slovenia + Slovakia precedent (Layer
    3 lat/lon geofence when NUTS-3 tag absent) applied per Convention #78
    BINDING enforcement Layer 3 geofence sub-convention.

    Czechia empirically GENERALIZES Layer 3 geofence from Slovakia's linear
    longitude partition to metro-carve-out + multi-bbox composition:
      Layer 1: ČEPS TSO threshold ≥220 kV → ČEPS (400/220 kV backbone).
      Layer 2: NUTS-3 → DSO map (if OSM populates NUTS-3 tags — empirically
               ~0 hits expected in Czechia; kept for forward-compat).
      Layer 3: Lat/lon geofence → DSO (Slovenia + Slovakia precedent):
        3a: PRE Prague metro bbox
        3b: EG.D South Bohemia bbox
        3c: EG.D South Moravia bbox
        3d: ČEZ Distribuce default catch-all
      Layer 4: 110 kV mixed tier — defaults to ČEPS if geofence fails.
      Layer 5: Empirical default — ČEZ Distribuce as LARGEST DSO catch-all.
    """
    # Layer 1: EHV → ČEPS
    if voltage_kv is not None and voltage_kv >= _CEPS_TSO_MIN_KV:
        return "CEPS", "region_jurisdiction_fallback_CEPS_TSO_threshold_ge_220kv"

    # Layer 2: NUTS-3 → DSO (empirically ~0 hits — kept for forward-compat)
    if nuts3:
        dso = resolve_owner_from_nuts3(nuts3)
        if dso:
            return dso, f"region_jurisdiction_fallback_{dso}_via_nuts3_{nuts3}"

    # Layer 3: Lat/lon geofence → DSO (Slovenia + Slovakia precedent)
    dso_via_geofence = resolve_owner_from_lat_lon_geofence(lat, lon)
    if dso_via_geofence:
        return dso_via_geofence, f"region_jurisdiction_fallback_{dso_via_geofence}_via_lat_lon_geofence"

    # Layer 4: 110 kV mixed tier — default to ČEPS if geofence returned None
    if voltage_kv is not None and voltage_kv >= 100.0:
        return "CEPS", "region_jurisdiction_fallback_CEPS_TSO_110kv_mixed_tier"

    # Layer 5: catch-all — ČEZ Distribuce as LARGEST DSO
    # (differs from Slovakia's SEPS default: Czechia's LARGEST is a DSO,
    #  not the TSO. This reflects ČEZ Distribuce's ~65% national coverage.)
    return "CEZ Distribuce", "region_jurisdiction_fallback_CEZ_Distribuce_default"


# ── Discipline #36 with Czechia 100m default tolerance ──────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Czechia bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(CZECHIA_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("czechia", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="czechia", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "czechia/v4_23-ingestion-audit-czechia-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = CZECHIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("cz-"):
        slug = slug[len("cz-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-czechia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Czechia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/czechia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: czechia",
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
        "  step_2_fetch: czechia/v4_23-ingestion-audit-czechia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: czechia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    CZECHIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return CZECHIA_CACHE_DIR / f"{key}{ext}"


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
    "resolve_owner_from_nuts3",
    "resolve_owner_from_lat_lon_geofence",
    "normalise_owner_alias",
    "CZECHIA_BOUNDS_JSON",
    "CZECHIA_TOLERANCE_JSON",
    "CZECHIA_DATA_DIR",
    "CZECHIA_CACHE_DIR",
]
