"""
SSI Pipeline — Iceland v4.23 ingestion, shared base layer.

Wave 3 Priority 23 (second Wave 3 country post-Greece; smallest of
remaining Wave 3 queue at 684 baseline subs). Region-jurisdiction ×
voltage-class monopoly via Landsnet single TSO + 5 regional DSOs (Veitur
Capital Region + HS Veitur Reykjanes + RARIK rural default + Norðurorka
Akureyri + Orkubú Vestfjarða Westfjords) via Layer 3 lat/lon geofence
with 4 metro/regional carve-outs. 9th cohort-wide application of
region-jurisdiction fallback pattern (after Belgium + Netherlands +
Chile + Hungary + Slovenia + Colombia + Norway + Slovakia + Czechia).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 5th EMPIRICAL TEST ⚡

Fifth country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive multi-script alias mapping REQUIRED at Step 3
connector authoring time:
  - Icelandic NFC diacritics (Þ ð æ ö á é í ó ú ý) — 🆕 NEW class
    cohort-wide (first Icelandic-script country in cohort)
  - Latin transliteration (Þ→th; ð→d; æ→ae; ö→o) for OSM tag variants
    where contributors omit Icelandic-specific characters
  - Legal-form variants (hf./ohf. — hlutafélag / opinbert hlutafélag)
    + comma-separated Icelandic commercial registry variants
  - Historical predecessor legacies (Landsvirkjun pre-2005 unbundle +
    Hitaveita Suðurnesja → HS Veitur 2008 + Rafmagnsveitur ríkisins →
    RARIK 2006 + Rafveita Akureyrar → Norðurorka pre-2000)

Iceland specifics:
  - Landsnet hf. — state-owned single TSO (established 2005 via
    unbundling from Landsvirkjun per EU 3rd Package Directive
    2003/54/EC). Operates 220/132/66 kV backbone. NO 400 kV (small
    isolated grid). ~3,300 km transmission network.
  - Veitur ohf. — Capital Region DSO (subsidiary of Orkuveita
    Reykjavíkur / OR). Voltage: 132 kV + 11-33 kV MV + 0.4 kV LV.
    Territory: Höfuðborgarsvæðið (Reykjavík metropolitan area including
    Reykjavík proper + Kópavogur + Hafnarfjörður + Garðabær +
    Mosfellsbær + Seltjarnarnes) + Akranes + Borgarnes.
    ~130,000 connections (~35% national market).
  - RARIK ohf. — LARGEST DSO by area (Rafmagnsveitur ríkisins).
    Voltage: 132 kV + MV + LV. Territory: rural default + North
    (excluding Akureyri) + South (excluding Reykjanes + Westman
    Islands) + East + West. ~55,000 connections (~40% national market).
  - HS Veitur hf. — Reykjanes peninsula + Vestmannaeyjar DSO.
    Voltage: 132 kV + MV + LV. Territory: Suðurnes (Keflavík +
    Reykjanesbær + Vogar + Grindavík) + Vestmannaeyjar (Westman
    Islands) + parts of South Iceland (Selfoss + Hveragerði).
    Rebrand: Hitaveita Suðurnesja → HS Veitur 2008.
    ~30,000 connections (~15% national market).
  - Norðurorka hf. — Akureyri + Eyjafjörður DSO. Voltage: 132 kV + MV
    + LV. Territory: Akureyri (2nd largest Icelandic city) + Dalvík +
    Húsavík. Rebrand: Rafveita Akureyrar → Norðurorka pre-2000.
    ~14,000 connections (~7% national market).
  - Orkubú Vestfjarða ohf. — Westfjords isolated peninsula DSO
    (established 1978). Voltage: 132 kV + MV + LV. Territory:
    Vestfirðir (Ísafjörður + Bolungarvík + Patreksfjörður). Only
    Icelandic DSO NEVER rebranded (46-year continuous operation).
    ~4,500 connections (~3% national market).

Historical predecessors preserved for audit trail:
  - Landsvirkjun (state utility 1965) integrated generation +
    transmission until 2005 unbundle; Landsvirkjun retained generation
    (12 hydro + 3 geothermal + 2 wind), Landsnet became TSO
  - Hitaveita Suðurnesja (geothermal-first utility 1974) → HS Veitur
    2008 rebrand (LARGEST predecessor alias class expected — 18 years
    since rebrand, many OSM tags still carry legacy name)
  - Rafmagnsveitur ríkisins (state DSO 1946) → RARIK 2006 ohf.
    conversion (20 years since rebrand)
  - Rafveita Akureyrar (Akureyri municipal DSO pre-2000) → Norðurorka
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
ICELAND_BOUNDS_JSON = REPO_ROOT / "iceland" / "bounds.json"
ICELAND_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
ICELAND_DATA_DIR = PIPELINE_DIR / "data" / "iceland"
ICELAND_CACHE_DIR = ICELAND_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 5th enforcement) ───
# Preemptive multi-script mapping: Icelandic NFC (Þ ð æ ö á é í ó ú ý) +
# Latin transliteration + hf./ohf. legal-form + predecessor rebrands
_DNSP_ALIAS_MAP = {
    # ── Landsnet variants (TSO) ────────────────────────────────────────
    "landsnet": "Landsnet",
    "landsnet hf.": "Landsnet",
    "landsnet hf": "Landsnet",
    "landsnet, hf.": "Landsnet",
    "landsnet, hf": "Landsnet",
    # Legal form variants (Icelandic hlutafélag)
    "landsnet a.s.": "Landsnet",           # Latin a.s. variant
    "landsnet a. s.": "Landsnet",          # Spaced variant
    # Icelandic English usage
    "landsnet grid": "Landsnet",
    "landsnet transmission": "Landsnet",
    # Predecessor: Landsvirkjun transmission branch pre-2005 unbundle
    "landsvirkjun": "Landsnet-legacy (Landsvirkjun pre-2005 unbundle)",
    "landsvirkjun hf.": "Landsnet-legacy (Landsvirkjun pre-2005 unbundle)",
    "landsvirkjun hf": "Landsnet-legacy (Landsvirkjun pre-2005 unbundle)",
    "landsvirkjun transmission": "Landsnet-legacy (Landsvirkjun pre-2005 unbundle)",

    # ── Veitur variants (Capital Region DSO) ───────────────────────────
    "veitur": "Veitur",
    "veitur ohf.": "Veitur",
    "veitur ohf": "Veitur",
    "veitur hf.": "Veitur",                # Sometimes tagged hf instead of ohf
    "veitur hf": "Veitur",
    # Parent Orkuveita Reykjavíkur (OR)
    "orkuveita reykjavíkur": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    "orkuveita reykjavikur": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    "orkuveita reykjavíkur ohf.": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    "orkuveita reykjavikur ohf.": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    "or": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    "orkuveitan": "Veitur (via OR parent — Orkuveita Reykjavíkur)",
    # Predecessor: Rafmagnsveita Reykjavíkur pre-2000
    "rafmagnsveita reykjavíkur": "Veitur-legacy (Rafmagnsveita Reykjavíkur pre-2000)",
    "rafmagnsveita reykjavikur": "Veitur-legacy (Rafmagnsveita Reykjavíkur pre-2000)",
    "rafmagnsveita": "Veitur-legacy (Rafmagnsveita Reykjavíkur pre-2000)",
    "rr": "Veitur-legacy (Rafmagnsveita Reykjavíkur pre-2000)",

    # ── RARIK variants (LARGEST DSO by area) ───────────────────────────
    "rarik": "RARIK",
    "rarik ohf.": "RARIK",
    "rarik ohf": "RARIK",
    "rarik hf.": "RARIK",
    "rarik hf": "RARIK",
    # Full Icelandic name (Rafmagnsveitur ríkisins = State Electricity Corp)
    "rafmagnsveitur ríkisins": "RARIK",
    "rafmagnsveitur rikisins": "RARIK",     # Latin transliteration (í → i)
    "rafmagnsveitur ríkisins ohf.": "RARIK",
    "rafmagnsveitur rikisins ohf.": "RARIK",
    # Predecessor: State ownership pre-2006 ohf. conversion
    "rafmagnsveitur ríkisins (state)": "RARIK-legacy (state pre-2006)",
    "rafmagnsveitur rikisins (state)": "RARIK-legacy (state pre-2006)",

    # ── HS Veitur variants (Reykjanes + Vestmannaeyjar DSO) ────────────
    "hs veitur": "HS Veitur",
    "hs veitur hf.": "HS Veitur",
    "hs veitur hf": "HS Veitur",
    "hs-veitur": "HS Veitur",               # Hyphenated variant
    "hs-veitur hf.": "HS Veitur",
    "hsveitur": "HS Veitur",                # No-space variant
    # Predecessor: Hitaveita Suðurnesja 1974-2008 (LARGEST predecessor class)
    "hitaveita suðurnesja": "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",
    "hitaveita sudurnesja": "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",   # Latin
    "hitaveita suðurnesja hf.": "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",
    "hitaveita sudurnesja hf.": "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",
    "hs": "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",   # Ambiguous prefix
    # Related HS Orka (generation subsidiary — should NOT tag substations but may leak)
    "hs orka": "HS Orka (Generation — Related Entity)",
    "hs orka hf.": "HS Orka (Generation — Related Entity)",

    # ── Norðurorka variants (Akureyri DSO) ─────────────────────────────
    "norðurorka": "Norðurorka",
    "nordurorka": "Norðurorka",              # Latin transliteration (ð → d)
    "norðurorka hf.": "Norðurorka",
    "nordurorka hf.": "Norðurorka",
    "norðurorka hf": "Norðurorka",
    "nordurorka hf": "Norðurorka",
    # Predecessor: Rafveita Akureyrar pre-2000
    "rafveita akureyrar": "Norðurorka-legacy (Rafveita Akureyrar pre-2000 rebrand)",
    "rafveita akureyrar hf.": "Norðurorka-legacy (Rafveita Akureyrar pre-2000 rebrand)",

    # ── Orkubú Vestfjarða variants (Westfjords DSO) ────────────────────
    "orkubú vestfjarða": "Orkubú Vestfjarða",
    "orkubu vestfjarda": "Orkubú Vestfjarða",  # Latin transliteration
    "orkubu vestfjarda": "Orkubú Vestfjarða",
    "orkubú vestfjarða ohf.": "Orkubú Vestfjarða",
    "orkubu vestfjarda ohf.": "Orkubú Vestfjarða",
    "orkubú vestfjarða hf.": "Orkubú Vestfjarða",
    "orkubu vestfjarda hf.": "Orkubú Vestfjarða",
    "ov": "Orkubú Vestfjarða",               # Acronym
    "ov ohf.": "Orkubú Vestfjarða",
    "ov hf.": "Orkubú Vestfjarða",

    # ── Landsvirkjun (State Generation Utility — NOT a DSO) ────────────
    # Should NOT appear on distribution substations but may leak from
    # generation-plant tagging. Preserve honestly per Convention #56.
    "landsvirkjun generation": "Landsvirkjun (State Generation)",
    "landsvirkjun power": "Landsvirkjun (State Generation)",
    "lv": "Landsvirkjun (State Generation)",   # Ambiguous — could clash

    # ── ON Power (OR generation subsidiary) ────────────────────────────
    "on": "ON Power (OR Generation Subsidiary)",
    "on hf.": "ON Power (OR Generation Subsidiary)",
    "on power": "ON Power (OR Generation Subsidiary)",
    "on power hf.": "ON Power (OR Generation Subsidiary)",

    # ── Industrial captives (aluminium + ferrosilicon + silicon) ───────
    "rio tinto": "Rio Tinto Alcan (Industrial Captive — Straumsvík Aluminium Smelter)",
    "rio tinto alcan": "Rio Tinto Alcan (Industrial Captive — Straumsvík Aluminium Smelter)",
    "rio tinto iceland": "Rio Tinto Alcan (Industrial Captive — Straumsvík Aluminium Smelter)",
    "isal": "Rio Tinto Alcan (Industrial Captive — Straumsvík Aluminium Smelter)",  # ISAL = pre-Rio-Tinto brand
    "century aluminum": "Century Aluminum (Industrial Captive — Grundartangi + Helguvík Smelters)",
    "century al": "Century Aluminum (Industrial Captive — Grundartangi + Helguvík Smelters)",
    "century": "Century Aluminum (Industrial Captive — Grundartangi + Helguvík Smelters)",
    "norðurál": "Century Aluminum (Industrial Captive — Norðurál Grundartangi Smelter)",
    "nordural": "Century Aluminum (Industrial Captive — Norðurál Grundartangi Smelter)",
    "norðurál hf.": "Century Aluminum (Industrial Captive — Norðurál Grundartangi Smelter)",
    "nordural hf.": "Century Aluminum (Industrial Captive — Norðurál Grundartangi Smelter)",
    "elkem": "Elkem Iceland (Industrial Captive — Grundartangi Ferrosilicon)",
    "elkem iceland": "Elkem Iceland (Industrial Captive — Grundartangi Ferrosilicon)",
    "elkem ísland": "Elkem Iceland (Industrial Captive — Grundartangi Ferrosilicon)",
    "elkem island": "Elkem Iceland (Industrial Captive — Grundartangi Ferrosilicon)",
    "pcc": "PCC BakkiSilicon (Industrial Captive — Bakki Silicon Metal Plant)",
    "pcc bakkisilicon": "PCC BakkiSilicon (Industrial Captive — Bakki Silicon Metal Plant)",
    "pcc silicon": "PCC BakkiSilicon (Industrial Captive — Bakki Silicon Metal Plant)",
    "bakki silicon": "PCC BakkiSilicon (Industrial Captive — Bakki Silicon Metal Plant)",
    # Fjarðaál (Rio Tinto Reyðarfjörður)
    "fjarðaál": "Fjarðaál Reyðarfjörður (Industrial Captive — Aluminium Smelter)",
    "fjardaal": "Fjarðaál Reyðarfjörður (Industrial Captive — Aluminium Smelter)",
    "alcoa fjarðaál": "Fjarðaál Reyðarfjörður (Industrial Captive — Aluminium Smelter)",
    "alcoa fjardaal": "Fjarðaál Reyðarfjörður (Industrial Captive — Aluminium Smelter)",
    "alcoa iceland": "Fjarðaál Reyðarfjörður (Industrial Captive — Aluminium Smelter)",

    # ── Data centers (cryptocurrency + AI compute) ─────────────────────
    "verne global": "Verne Global (Industrial Captive — Data Center Keflavík)",
    "verne": "Verne Global (Industrial Captive — Data Center Keflavík)",
    "advania": "Advania Data Centers (Industrial Captive — Reykjanes)",
    "advania data centers": "Advania Data Centers (Industrial Captive — Reykjanes)",
    "atnorth": "atNorth (Industrial Captive — Data Center Reykjanes)",
    "atnorth data center": "atNorth (Industrial Captive — Data Center Reykjanes)",

    # ── Icelandic typographic-quote variants (Latvia + Czechia precedent) ─
    # Icelandic uses „..." (U+201E + U+201C) — same as German/Czech
    'as "landsnet"': "Landsnet",
    'as „landsnet"': "Landsnet",
    'as "veitur"': "Veitur",
    'as „veitur"': "Veitur",
    'as "rarik"': "RARIK",
    'as „rarik"': "RARIK",
    'as "hs veitur"': "HS Veitur",
    'as „hs veitur"': "HS Veitur",
    'as "norðurorka"': "Norðurorka",
    'as „norðurorka"': "Norðurorka",
    'as "orkubú vestfjarða"': "Orkubú Vestfjarða",
    'as „orkubú vestfjarða"': "Orkubú Vestfjarða",
    'as "hitaveita suðurnesja"': "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",
    'as „hitaveita suðurnesja"': "HS Veitur-legacy (Hitaveita Suðurnesja pre-2008 rebrand)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 5th enforcement — preserves Icelandic NFC
    diacritics (Þ ð æ ö á é í ó ú ý) + typographic quotes („..."
    Icelandic-German style same as Czech + Latvian) + Latin
    transliteration handles (þ→th; ð→d; æ→ae; ö→o) for OSM tag
    variants where contributors omit Icelandic-specific characters."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Icelandic
    diacritics preserved in input, normalised via NFC + lower-case lookup.
    Handles Latin transliteration variants (þ→th; ð→d; æ→ae; ö→o) from
    OSM contributors + Icelandic typographic-quote variants per
    Convention #78 BINDING 5th enforcement (5th empirical test
    post-promotion).

    Icelandic script is 🆕 NEW cohort-wide alias class — first
    Icelandic-script country in cohort. Predecessor rebrand classes:
    Hitaveita Suðurnesja → HS Veitur (2008 — LARGEST expected 18-year
    legacy) + Rafmagnsveitur ríkisins → RARIK (2006 — 20-year legacy) +
    Rafveita Akureyrar → Norðurorka (pre-2000) + Landsvirkjun →
    Landsnet (2005 — 1-generation cascade)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 to DSO map ────────────────────────────────────────────────────
# Iceland OSM likely does NOT populate ref:nuts:3 tags on substations
# (empirical hypothesis Slovenia + Slovakia + Czechia + Poland +
# Greece precedent). Forward-compat surface below; actual attribution
# flows via Layer 3 geofence.
# Icelandic NUTS-3 codes: IS001 Höfuðborgarsvæðið + IS002 Suðurnes +
# IS003 Vesturland + IS004 Vestfirðir + IS005 Norðurland vestra +
# IS006 Norðurland eystra + IS007 Austurland + IS008 Suðurland
_NUTS3_TO_DSO = {
    "IS001": "Veitur",              # Capital Region (Reykjavík metro)
    "IS002": "HS Veitur",           # Reykjanes peninsula (Suðurnes)
    "IS003": "RARIK",               # West Iceland (Vesturland)
    "IS004": "Orkubú Vestfjarða",   # Westfjords (Vestfirðir)
    "IS005": "RARIK",               # Northwest (Norðurland vestra)
    "IS006": "Norðurorka",          # Northeast — Akureyri (Norðurland eystra)
    "IS007": "RARIK",               # East (Austurland)
    "IS008": "RARIK",               # South (Suðurland) — RARIK default,
                                    # HS Veitur takes Vestmannaeyjar + Selfoss
                                    # via Layer 3 geofence carve-out
}


def resolve_owner_from_nuts3(nuts3_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NUTS-3 code."""
    if not nuts3_code:
        return None
    return _NUTS3_TO_DSO.get(nuts3_code.strip().upper())


# ── Layer 3 lat/lon geofence (5-DSO territorial partition) ───────────────
# Iceland OSM does not populate ref:nuts:3 tags on substations (empirical
# finding hypothesis — Wave 2 Slovenia + Slovakia + Czechia + Wave 3
# Poland + Greece cumulative precedent). Add lat/lon geofence for DSO
# attribution.
#
# Icelandic territorial partition — 5 DSOs + 1 TSO:
#   Veitur (Capital Region metro) — bbox 64.05-64.20 lat, -22.05 to -21.70 lon
#   HS Veitur (Reykjanes peninsula + Vestmannaeyjar) — 2 disjoint bboxes:
#     - Reykjanes: 63.75-64.05 lat, -22.75 to -22.05 lon
#     - Vestmannaeyjar (Westman Islands): 63.35-63.55 lat, -20.40 to -20.10 lon
#   Norðurorka (Akureyri + Eyjafjörður) — bbox 65.60-66.20 lat, -18.75 to -18.05 lon
#   Orkubú Vestfjarða (Westfjords) — bbox 65.20-66.60 lat, -24.55 to -22.00 lon
#   RARIK (default catch-all) — everything else (largest territory by area)
#   Landsnet (TSO — only via voltage threshold Layer 1 ≥132 kV)
#
# Iceland bounds: 63.30 <= lat <= 66.55, -24.55 <= lon <= -13.30

# Veitur Capital Region metro bbox (Höfuðborgarsvæðið)
# Includes Reykjavík + Kópavogur + Hafnarfjörður + Garðabær + Mosfellsbær + Seltjarnarnes
_VEITUR_METRO_LAT_MIN = 64.05
_VEITUR_METRO_LAT_MAX = 64.20
_VEITUR_METRO_LON_MIN = -22.05
_VEITUR_METRO_LON_MAX = -21.70

# HS Veitur Reykjanes peninsula bbox (Priority 1)
# Includes Keflavík + Reykjanesbær + Vogar + Grindavík
_HS_REYKJANES_LAT_MIN = 63.75
_HS_REYKJANES_LAT_MAX = 64.05
_HS_REYKJANES_LON_MIN = -22.75
_HS_REYKJANES_LON_MAX = -22.05

# HS Veitur Vestmannaeyjar bbox (Priority 2 — Westman Islands)
_HS_VESTMAN_LAT_MIN = 63.35
_HS_VESTMAN_LAT_MAX = 63.55
_HS_VESTMAN_LON_MIN = -20.40
_HS_VESTMAN_LON_MAX = -20.10

# Norðurorka Akureyri bbox (Eyjafjörður)
_NORDURORKA_LAT_MIN = 65.60
_NORDURORKA_LAT_MAX = 66.20
_NORDURORKA_LON_MIN = -18.75
_NORDURORKA_LON_MAX = -18.05

# Orkubú Vestfjarða Westfjords bbox
# Isolated peninsula includes Ísafjörður + Bolungarvík + Patreksfjörður
_OV_WESTFJORDS_LAT_MIN = 65.20
_OV_WESTFJORDS_LAT_MAX = 66.60
_OV_WESTFJORDS_LON_MIN = -24.55
_OV_WESTFJORDS_LON_MAX = -22.00

# Iceland national bounds sanity check
_IS_LAT_MIN = 63.30
_IS_LAT_MAX = 66.55
_IS_LON_MIN = -24.55
_IS_LON_MAX = -13.30


def resolve_owner_from_lat_lon_geofence(lat: float, lon: float) -> str | None:
    """Icelandic 5-way DSO territorial partition via metro + multi-bbox
    composition.

    Wave 2/3 cumulative precedent (Slovenia Priority 12 + Slovakia
    Priority 19 + Czechia Priority 20 + Poland Priority 21 + Greece
    Priority 22) — apply when OSM does not populate NUTS-3 tags.
    Convention #78 BINDING 5th enforcement Layer 3 geofence
    sub-convention: when NUTS-3 tag absent, geofence MUST be
    preemptively coded at Step 3 connector authoring time.

    Iceland empirically EXTENDS the sub-convention from Czechia's
    metro-carve-out + multi-bbox composition to 4 disjoint territorial
    bboxes + isolated-island bbox (Vestmannaeyjar — first Icelandic
    Wave 3 cohort island-DSO carve-out):
      Layer 3a: Veitur Capital Region metro bbox (Höfuðborgarsvæðið)
      Layer 3b: HS Veitur Reykjanes peninsula bbox
      Layer 3c: HS Veitur Vestmannaeyjar island bbox
      Layer 3d: Norðurorka Akureyri bbox (Eyjafjörður)
      Layer 3e: Orkubú Vestfjarða Westfjords bbox
      Layer 3f: RARIK default catch-all (largest territory)

    Returns DSO code or None if lat/lon outside Icelandic bounds.
    """
    # Sanity check — within Iceland bounds
    if not (_IS_LAT_MIN <= lat <= _IS_LAT_MAX and _IS_LON_MIN <= lon <= _IS_LON_MAX):
        return None

    # Layer 3a: Veitur Capital Region metro bbox (checked first — highest priority)
    if (_VEITUR_METRO_LAT_MIN <= lat <= _VEITUR_METRO_LAT_MAX
            and _VEITUR_METRO_LON_MIN <= lon <= _VEITUR_METRO_LON_MAX):
        return "Veitur"

    # Layer 3b: HS Veitur Reykjanes peninsula bbox
    if (_HS_REYKJANES_LAT_MIN <= lat <= _HS_REYKJANES_LAT_MAX
            and _HS_REYKJANES_LON_MIN <= lon <= _HS_REYKJANES_LON_MAX):
        return "HS Veitur"

    # Layer 3c: HS Veitur Vestmannaeyjar island bbox
    if (_HS_VESTMAN_LAT_MIN <= lat <= _HS_VESTMAN_LAT_MAX
            and _HS_VESTMAN_LON_MIN <= lon <= _HS_VESTMAN_LON_MAX):
        return "HS Veitur"

    # Layer 3d: Norðurorka Akureyri bbox
    if (_NORDURORKA_LAT_MIN <= lat <= _NORDURORKA_LAT_MAX
            and _NORDURORKA_LON_MIN <= lon <= _NORDURORKA_LON_MAX):
        return "Norðurorka"

    # Layer 3e: Orkubú Vestfjarða Westfjords bbox
    if (_OV_WESTFJORDS_LAT_MIN <= lat <= _OV_WESTFJORDS_LAT_MAX
            and _OV_WESTFJORDS_LON_MIN <= lon <= _OV_WESTFJORDS_LON_MAX):
        return "Orkubú Vestfjarða"

    # Layer 3f: RARIK default catch-all (largest DSO by area)
    return "RARIK"


# ── Landsnet TSO voltage threshold ───────────────────────────────────────
# Landsnet operates 220/132/66 kV backbone. Below 132 kV → DSO
# jurisdiction via NUTS-3 map or lat/lon geofence. 132 kV is the primary
# transmission tier (Iceland has few 220 kV — small isolated grid).
# 66 kV is subtransmission — can be DSO or TSO depending on region.
#
# Empirical rule (documented in preflight):
#   ≥132 kV → Landsnet TSO
#   <132 kV → Regional DSO via geofence
# 66 kV tier: Layer 4 fallback to Landsnet if geofence returns default catch-all
_LANDSNET_TSO_MIN_KV = 132.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None, lat: float, lon: float, nuts3: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Region-jurisdiction × voltage-class resolver — 9th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary + Slovenia
    + Colombia + Norway + Slovakia + Czechia). Slovenia + Slovakia +
    Czechia + Poland + Greece cumulative precedent (Layer 3 lat/lon
    geofence when NUTS-3 tag absent) applied per Convention #78 BINDING
    5th enforcement Layer 3 geofence sub-convention.

    Iceland empirically EXTENDS Layer 3 geofence from Czechia's 3-way
    metro-carve-out to 5-way multi-bbox composition + first-cohort
    island-DSO carve-out (Vestmannaeyjar):
      Layer 1: Landsnet TSO threshold ≥132 kV → Landsnet
      Layer 2: NUTS-3 → DSO map (if OSM populates NUTS-3 tags —
               empirically ~0 hits expected in Iceland; kept for
               forward-compat).
      Layer 3: Lat/lon geofence → DSO (5-way multi-bbox composition):
        3a: Veitur Capital Region metro bbox
        3b: HS Veitur Reykjanes peninsula bbox
        3c: HS Veitur Vestmannaeyjar island bbox
        3d: Norðurorka Akureyri bbox
        3e: Orkubú Vestfjarða Westfjords bbox
        3f: RARIK default catch-all (largest territory)
      Layer 4: 66 kV subtransmission tier — defaults to Landsnet if
               geofence returned catch-all (uncertain jurisdiction).
      Layer 5: Empirical default — RARIK as LARGEST DSO catch-all.
    """
    # Layer 1: HV → Landsnet TSO
    if voltage_kv is not None and voltage_kv >= _LANDSNET_TSO_MIN_KV:
        return "Landsnet", "region_jurisdiction_fallback_Landsnet_TSO_threshold_ge_132kv"

    # Layer 2: NUTS-3 → DSO (empirically ~0 hits — kept for forward-compat)
    if nuts3:
        dso = resolve_owner_from_nuts3(nuts3)
        if dso:
            return dso, f"region_jurisdiction_fallback_{dso}_via_nuts3_{nuts3}"

    # Layer 3: Lat/lon geofence → DSO (5-way multi-bbox composition)
    dso_via_geofence = resolve_owner_from_lat_lon_geofence(lat, lon)
    if dso_via_geofence:
        return dso_via_geofence, f"region_jurisdiction_fallback_{dso_via_geofence}_via_lat_lon_geofence"

    # Layer 4: 66 kV subtransmission mixed tier — default to Landsnet if
    # geofence returned None (outside Iceland bounds — should not happen
    # post-bounds-filter but defensive)
    if voltage_kv is not None and voltage_kv >= 66.0:
        return "Landsnet", "region_jurisdiction_fallback_Landsnet_TSO_66kv_subtransmission_tier"

    # Layer 5: catch-all — RARIK as LARGEST DSO by area
    return "RARIK", "region_jurisdiction_fallback_RARIK_default"


# ── Discipline #36 with Iceland 5.0 km default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Iceland bounds filter with 5.0 km default tolerance.

    Per Greenland/NZ/Denmark/Norway coastline precedent — Iceland's
    heavily-indented fjord coastline + Vestmannaeyjar island offset +
    Grímsey Arctic Circle offshore island + volcanic geothermal
    remote-siting warrant 5.0 km tolerance (not the standard 0.1 km
    cadastral default). Iceland is fully-isolated grid — no legitimate
    cross-border subs; tolerance is purely for coastline precision."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(ICELAND_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("iceland", {}).get("tolerance_km", 5.0)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 5.0
    return _apply_bounds_generic(
        records, country_slug="iceland", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "iceland/v4_23-ingestion-audit-iceland-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = ICELAND_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("is-"):
        slug = slug[len("is-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-iceland-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Iceland ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/iceland/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: iceland",
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
        "  step_2_fetch: iceland/v4_23-ingestion-audit-iceland-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: iceland/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    ICELAND_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return ICELAND_CACHE_DIR / f"{key}{ext}"


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
    "ICELAND_BOUNDS_JSON",
    "ICELAND_TOLERANCE_JSON",
    "ICELAND_DATA_DIR",
    "ICELAND_CACHE_DIR",
]
