"""
SSI Pipeline — Poland v4.23 ingestion, shared base layer.

Region-jurisdiction × voltage-class monopoly via PSE TSO + 4 regional DSOs
(PGE Dystrybucja LARGEST territorially + Tauron Dystrybucja south + Enea
Operator west/north + Energa Operator north) + Innogy Stoen Warsaw metro
Layer 3 geofence. 9th cohort-wide application of region-jurisdiction
fallback pattern (after Belgium + Netherlands + Chile + Hungary + Slovenia
+ Colombia + Norway + Slovakia + Czechia).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 3rd EMPIRICAL TEST ⚡
⚡ LAYER 3 GEOFENCE SUB-CONVENTION 3rd ENFORCEMENT POST-BINDING ⚡
🏛 VISEGRÁD TRIO COMPLETION MILESTONE (3 of 3) 🏛

Third country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia P17 closure, 16 July 2026),
following Slovakia P19 1st enforcement + Czechia P20 2nd enforcement.
Poland completes Visegrád Trio at v4.23 (SK + CZ + PL; HU shipped Wave 2
P7 under different sub-convention path — NUTS-3 populated in Hungarian
OSM tags).

Preemptive multi-script alias mapping REQUIRED at Step 3 connector
authoring time per Convention #78 BINDING. Poland is LARGEST expected
alias-normalisation cohort with **5-7 rebrand-predecessor alias classes**:

  - Polish NFC diacritics (ą ć ę ł ń ó ś ź ż)
  - Polish typographic quotes („..." like German/Czech/Latvian)
  - Belarusian Cyrillic (Podlaskie minority OSM contributors)
  - Ukrainian Cyrillic (eastern Silesia + Rzeszów-Kaliningrad Direct HVAC
    cross-border area OSM contributors)
  - PGE Dystrybucja 4-regional-predecessor cascade (2019 consolidation)
  - Tauron Dystrybucja 2-variant predecessor (EnergiaPro + Enion, 2008)
  - Enea Operator predecessor (ZGE Zachodniopomorska Grupa Energetyczna,
    pre-2007)
  - Energa Operator 2-variant predecessor (GEZ Grupa Energetyczna Zachód +
    Koncern Energetyczny Energa, pre-2006)
  - Innogy Stoen Operator 3-GENERATION rebrand cascade (RWE Stoen 2020 →
    Stoen 2016 → ZE Warszawa 2003) — UNIQUE cohort-wide multi-generation
    tracking; NEW sub-convention candidate for multi-generation rebrand-
    predecessor tracking codified via this codifying instance

Poland specifics:
  - PSE (Polskie Sieci Elektroenergetyczne S.A.) — state TSO (100%
    state-owned via Ministerstwo Aktywów Państwowych), operates 750 kV
    (Rzeszów-Kaliningrad Direct HVAC unique cohort-wide + Białystok-Ross
    interconnector Belarus) + 400 kV Continental European EHV (LitPol
    Link 2015 to Baltics) + 220 kV Soviet-era HV + 110 kV transmission.
    ~14,000 km transmission network + 8 interconnectors to 7 bordering
    countries.
  - PGE Dystrybucja S.A. — LARGEST territorial DSO (~35% market share).
    Territory: 8 województwa across NE/E/S Poland — Mazowieckie (non-
    Warsaw) + Łódzkie + Świętokrzyskie + Lubelskie + Podkarpackie +
    Warmińsko-Mazurskie. ~5.8M connections. Parent: PGE Polska Grupa
    Energetyczna (57.4% state-owned via MSP).
  - Tauron Dystrybucja S.A. — Second-largest DSO (~24% market share).
    Territory: 5 województwa south Poland — Małopolskie + Śląskie +
    Opolskie + Dolnośląskie + Podkarpackie (Bieszczady portion).
    ~5.6M connections. Parent: Tauron Polska Energia (30.06% state via
    MSP + 55.94% free float).
  - Enea Operator sp. z o.o. — Third DSO (~19% market share). Territory:
    4 województwa W/NW Poland — Wielkopolskie + Zachodniopomorskie +
    Lubuskie + Kujawsko-Pomorskie (Bydgoszcz portion + parts of Gorzów
    Wielkopolski). ~2.6M connections. Parent: Enea SA (52.35% state via
    MSP).
  - Energa Operator SA — Fourth DSO (~14% market share). Territory:
    4 województwa N Poland — Pomorskie + Warmińsko-Mazurskie (Elbląg
    portion) + Kujawsko-Pomorskie (Toruń portion) + Wielkopolskie (Kalisz
    portion). ~3.1M connections. Parent: PKN Orlen SA (100% via 2020
    acquisition; Energa was independent SA pre-2020).
  - Innogy Stoen Operator sp. z o.o. — Warsaw metro DSO (~8% market
    share). LAYER 3 GEOFENCE ENFORCEMENT: Warsaw metropolitan area
    only. ~1.1M connections. Parent: Innogy SE (RWE subsidiary since
    2020). 3-GENERATION REBRAND CASCADE preserved for audit trail.
  - Historical predecessors (pre-1990 socialist utility system):
    Preserved honestly per Convention #56 (Zjednoczone Zakłady
    Energetyczne + regional ZE prefixes).

Poland context: Visegrád Group member (V4 with Slovakia + Czechia +
Hungary). EU-synchronised Continental European zone since 1993 + LitPol
Link HVAC 2015 to Baltic Trio (Baltics desynchronised from BRELL Feb
2025 — LitPol now key sync path). Bordering 7 countries: Germany W +
Czech Republic S + Slovakia S + Ukraine E + Belarus E + Lithuania NE +
Russia (Kaliningrad enclave) NE + maritime border with Sweden + Denmark.
Discipline #36 100m tolerance preserved cleanly across all borders.
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
POLAND_BOUNDS_JSON = REPO_ROOT / "poland" / "bounds.json"
POLAND_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
POLAND_DATA_DIR = PIPELINE_DIR / "data" / "poland"
POLAND_CACHE_DIR = POLAND_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 3rd enforcement) ───
# Preemptive multi-script mapping: Polish NFC + Cyrillic (Belarusian +
# Ukrainian minority OSM) + typographic quotes + comma-separated legal-
# form variants + 5 rebrand-predecessor cascades including Innogy Stoen
# UNIQUE 3-generation multi-generational tracking
_DNSP_ALIAS_MAP = {
    # ── PSE variants (state TSO) ───────────────────────────────────────
    "pse": "PSE",
    "pse s.a.": "PSE",
    "pse sa": "PSE",
    "pse, s.a.": "PSE",
    "polskie sieci elektroenergetyczne": "PSE",
    "polskie sieci elektroenergetyczne s.a.": "PSE",
    "polskie sieci elektroenergetyczne sa": "PSE",
    "polskie sieci elektroenergetyczne s. a.": "PSE",   # space variant
    "polskie sieci elektroenergetyczne, s.a.": "PSE",
    # PSE Cyrillic (Belarusian OSM Podlaskie + Ukrainian OSM SE)
    "псэ": "PSE",
    "польские сети электроэнергетичне": "PSE",
    "польскі сеці электраэнергетычные": "PSE",   # Belarusian
    # PSE predecessors (pre-2004 restructuring from PSE-Operator)
    "pse-operator": "PSE-legacy (PSE-Operator pre-2004)",
    "pse-operator s.a.": "PSE-legacy (PSE-Operator pre-2004)",
    "polskie sieci elektroenergetyczne - operator": "PSE-legacy (PSE-Operator pre-2004)",
    "pse operator": "PSE-legacy (PSE-Operator pre-2004)",

    # ── PGE Dystrybucja variants (LARGEST DSO ~35%) ───────────────────
    "pge dystrybucja": "PGE Dystrybucja",
    "pge dystrybucja s.a.": "PGE Dystrybucja",
    "pge dystrybucja sa": "PGE Dystrybucja",
    "pge dystrybucja, s.a.": "PGE Dystrybucja",
    "pge dystrybucja s. a.": "PGE Dystrybucja",   # space variant
    "pge-dystrybucja": "PGE Dystrybucja",
    "pged": "PGE Dystrybucja",
    # PGE Cyrillic
    "пге дистрибуция": "PGE Dystrybucja",
    "пге дистрибуцыя": "PGE Dystrybucja",   # Belarusian
    # PGE Group parent (may leak on tags)
    "pge": "PGE Group (Holding — Parent)",
    "pge s.a.": "PGE Group (Holding — Parent)",
    "pge polska grupa energetyczna": "PGE Group (Holding — Parent)",
    "pge polska grupa energetyczna s.a.": "PGE Group (Holding — Parent)",
    # PGE Dystrybucja 4-regional-predecessor cascade (2019 consolidation)
    # → CONVENTION #78 BINDING 4-VARIANT PREDECESSOR CASCADE
    "pge rzeszów": "PGE Dystrybucja-legacy (PGE Rzeszów pre-2019)",
    "pge rzeszow": "PGE Dystrybucja-legacy (PGE Rzeszów pre-2019)",
    "pge dystrybucja rzeszów": "PGE Dystrybucja-legacy (PGE Rzeszów pre-2019)",
    "pge dystrybucja rzeszow": "PGE Dystrybucja-legacy (PGE Rzeszów pre-2019)",
    "pge zamość": "PGE Dystrybucja-legacy (PGE Zamość pre-2019)",
    "pge zamosc": "PGE Dystrybucja-legacy (PGE Zamość pre-2019)",
    "pge dystrybucja zamość": "PGE Dystrybucja-legacy (PGE Zamość pre-2019)",
    "pge dystrybucja zamosc": "PGE Dystrybucja-legacy (PGE Zamość pre-2019)",
    "pge lublin": "PGE Dystrybucja-legacy (PGE Lublin pre-2019)",
    "pge dystrybucja lublin": "PGE Dystrybucja-legacy (PGE Lublin pre-2019)",
    "pge skarżysko": "PGE Dystrybucja-legacy (PGE Skarżysko pre-2019)",
    "pge skarzysko": "PGE Dystrybucja-legacy (PGE Skarżysko pre-2019)",
    "pge dystrybucja skarżysko": "PGE Dystrybucja-legacy (PGE Skarżysko pre-2019)",
    "pge dystrybucja skarzysko": "PGE Dystrybucja-legacy (PGE Skarżysko pre-2019)",
    # PGE Distribucja pre-2010 predecessor
    "łódzki zakład energetyczny": "PGE Dystrybucja-legacy (Łódzki Zakład Energetyczny pre-2010)",
    "lodzki zaklad energetyczny": "PGE Dystrybucja-legacy (Łódzki Zakład Energetyczny pre-2010)",

    # ── Tauron Dystrybucja variants (2nd DSO ~24%) ─────────────────────
    "tauron dystrybucja": "Tauron Dystrybucja",
    "tauron dystrybucja s.a.": "Tauron Dystrybucja",
    "tauron dystrybucja sa": "Tauron Dystrybucja",
    "tauron dystrybucja, s.a.": "Tauron Dystrybucja",
    "tauron dystrybucja s. a.": "Tauron Dystrybucja",
    "tauron-dystrybucja": "Tauron Dystrybucja",
    "taurond": "Tauron Dystrybucja",
    # Tauron Cyrillic
    "таурон дистрибуция": "Tauron Dystrybucja",
    "таурон дистрыбуцыя": "Tauron Dystrybucja",   # Belarusian
    # Tauron Group parent
    "tauron": "Tauron Group (Holding — Parent)",
    "tauron polska energia": "Tauron Group (Holding — Parent)",
    "tauron polska energia s.a.": "Tauron Group (Holding — Parent)",
    # Tauron 2-VARIANT predecessor cascade (2008 EnergiaPro + Enion)
    # → CONVENTION #78 BINDING 2-VARIANT PREDECESSOR CASCADE
    "energiapro": "Tauron Dystrybucja-legacy (EnergiaPro pre-2008)",
    "energiapro s.a.": "Tauron Dystrybucja-legacy (EnergiaPro pre-2008)",
    "energiapro grupa": "Tauron Dystrybucja-legacy (EnergiaPro pre-2008)",
    "energia pro": "Tauron Dystrybucja-legacy (EnergiaPro pre-2008)",
    "enion": "Tauron Dystrybucja-legacy (Enion pre-2008)",
    "enion energia": "Tauron Dystrybucja-legacy (Enion pre-2008)",
    "enion s.a.": "Tauron Dystrybucja-legacy (Enion pre-2008)",
    "enion grupa": "Tauron Dystrybucja-legacy (Enion pre-2008)",

    # ── Enea Operator variants (3rd DSO ~19%) ──────────────────────────
    "enea operator": "Enea Operator",
    "enea operator sp. z o.o.": "Enea Operator",
    "enea operator sp. z o. o.": "Enea Operator",   # space variant
    "enea operator sp.z o.o.": "Enea Operator",
    "enea operator, sp. z o.o.": "Enea Operator",
    "enea-operator": "Enea Operator",
    "eneaop": "Enea Operator",
    # Enea Cyrillic
    "энеа оператор": "Enea Operator",
    "энеа аператар": "Enea Operator",   # Belarusian
    # Enea Group parent
    "enea": "Enea Group (Holding — Parent)",
    "enea s.a.": "Enea Group (Holding — Parent)",
    "enea sa": "Enea Group (Holding — Parent)",
    # Enea predecessor (pre-2007 ZGE consolidation)
    # → CONVENTION #78 BINDING 1-VARIANT PREDECESSOR CASCADE
    "zge": "Enea Operator-legacy (ZGE Zachodniopomorska pre-2007)",
    "zachodniopomorska grupa energetyczna": "Enea Operator-legacy (ZGE Zachodniopomorska pre-2007)",
    "zachodniopomorska grupa energetyczna s.a.": "Enea Operator-legacy (ZGE Zachodniopomorska pre-2007)",

    # ── Energa Operator variants (4th DSO ~14%) ────────────────────────
    "energa operator": "Energa Operator",
    "energa operator s.a.": "Energa Operator",
    "energa operator sa": "Energa Operator",
    "energa operator, s.a.": "Energa Operator",
    "energa operator s. a.": "Energa Operator",
    "energa-operator": "Energa Operator",
    "energaop": "Energa Operator",
    # Energa Cyrillic
    "энерга оператор": "Energa Operator",
    "энэрга аператар": "Energa Operator",   # Belarusian
    # Energa Group parent (post-2020 PKN Orlen acquisition)
    "energa": "Energa Group (Holding — Parent, now PKN Orlen subsidiary)",
    "energa s.a.": "Energa Group (Holding — Parent, now PKN Orlen subsidiary)",
    "energa sa": "Energa Group (Holding — Parent, now PKN Orlen subsidiary)",
    # Energa 2-VARIANT predecessor cascade (2006 GEZ + Koncern Energa)
    # → CONVENTION #78 BINDING 2-VARIANT PREDECESSOR CASCADE
    "gez": "Energa Operator-legacy (GEZ Grupa Energetyczna Zachód pre-2006)",
    "grupa energetyczna zachód": "Energa Operator-legacy (GEZ Grupa Energetyczna Zachód pre-2006)",
    "grupa energetyczna zachod": "Energa Operator-legacy (GEZ Grupa Energetyczna Zachód pre-2006)",
    "koncern energetyczny energa": "Energa Operator-legacy (KEE Koncern pre-2006)",
    "koncern energetyczny energa s.a.": "Energa Operator-legacy (KEE Koncern pre-2006)",

    # ── Innogy Stoen Operator variants (Warsaw metro DSO ~8%) ──────────
    # 3-GENERATION REBRAND CASCADE — UNIQUE COHORT-WIDE (new sub-
    # convention candidate for multi-generation rebrand-predecessor tracking)
    "innogy stoen operator": "Innogy Stoen Operator",
    "innogy stoen operator sp. z o.o.": "Innogy Stoen Operator",
    "innogy stoen operator sp.z o.o.": "Innogy Stoen Operator",
    "innogy stoen operator sp. z o. o.": "Innogy Stoen Operator",
    "innogy stoen": "Innogy Stoen Operator",
    "innogy": "Innogy Stoen Operator",   # ambiguous parent may leak
    "innogy poland": "Innogy Stoen Operator",
    "innogy polska": "Innogy Stoen Operator",
    "innogy polska s.a.": "Innogy Stoen Operator",
    # Innogy Cyrillic
    "инногы стоен": "Innogy Stoen Operator",
    "инноджи стоен": "Innogy Stoen Operator",
    # Generation 2: RWE Stoen Operator (2003-2020 rebrand)
    "rwe stoen operator": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    "rwe stoen": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    "rwe stoen operator sp. z o.o.": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    "rwe polska": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    "rwe polska s.a.": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    "rwe": "Innogy Stoen Operator-legacy (RWE Stoen 2003-2020)",
    # Generation 3: Stoen Operator sp. z o.o. (2016 rebrand from Stoen SA)
    "stoen operator": "Innogy Stoen Operator-legacy (Stoen Operator 2016-2020)",
    "stoen operator sp. z o.o.": "Innogy Stoen Operator-legacy (Stoen Operator 2016-2020)",
    "stoen sa": "Innogy Stoen Operator-legacy (Stoen SA 2003-2016)",
    "stoen s.a.": "Innogy Stoen Operator-legacy (Stoen SA 2003-2016)",
    "stoen": "Innogy Stoen Operator-legacy (Stoen SA 2003-2016)",
    # Generation 4 (pre-2003): ZE Warszawa state utility
    "ze warszawa": "Innogy Stoen Operator-legacy (ZE Warszawa pre-2003 state utility)",
    "zakład energetyczny warszawa": "Innogy Stoen Operator-legacy (ZE Warszawa pre-2003 state utility)",
    "zaklad energetyczny warszawa": "Innogy Stoen Operator-legacy (ZE Warszawa pre-2003 state utility)",
    "zakład energetyczny warszawa s.a.": "Innogy Stoen Operator-legacy (ZE Warszawa pre-2003 state utility)",
    "zaklad energetyczny warszawa s.a.": "Innogy Stoen Operator-legacy (ZE Warszawa pre-2003 state utility)",

    # ── Polish State Railways (electric traction 3 kV DC) ──────────────
    "pkp energetyka": "PKP Energetyka (Polish Railways Electric Traction)",
    "pkp energetyka s.a.": "PKP Energetyka (Polish Railways Electric Traction)",
    "pkp energetyka sa": "PKP Energetyka (Polish Railways Electric Traction)",
    "pkp": "PKP Energetyka (Polish Railways Electric Traction)",
    "polskie koleje państwowe": "PKP Energetyka (Polish Railways Electric Traction)",
    "polskie koleje panstwowe": "PKP Energetyka (Polish Railways Electric Traction)",

    # ── Warsaw + Kraków + Wrocław + Gdańsk public transport ────────────
    "metro warszawskie": "Metro Warszawskie (Warsaw Metro Traction)",
    "metro warszawskie sp. z o.o.": "Metro Warszawskie (Warsaw Metro Traction)",
    "warszawski metro": "Metro Warszawskie (Warsaw Metro Traction)",
    "tramwaje warszawskie": "Tramwaje Warszawskie (Warsaw Tram)",
    "tramwaje warszawskie sp. z o.o.": "Tramwaje Warszawskie (Warsaw Tram)",
    "mpk kraków": "MPK Kraków (Kraków Public Transport)",
    "mpk krakow": "MPK Kraków (Kraków Public Transport)",
    "mpk wrocław": "MPK Wrocław (Wrocław Public Transport)",
    "mpk wroclaw": "MPK Wrocław (Wrocław Public Transport)",
    "mzkzg gdańsk": "MZKZG Gdańsk (Gdańsk Public Transport)",
    "mzkzg gdansk": "MZKZG Gdańsk (Gdańsk Public Transport)",
    "zkm gdynia": "ZKM Gdynia (Gdynia Public Transport)",
    "mpk poznań": "MPK Poznań (Poznań Public Transport)",
    "mpk poznan": "MPK Poznań (Poznań Public Transport)",

    # ── Industrial captives ────────────────────────────────────────────
    "kghm polska miedź": "KGHM Polska Miedź (Industrial Captive — Copper Mining)",
    "kghm polska miedz": "KGHM Polska Miedź (Industrial Captive — Copper Mining)",
    "kghm": "KGHM Polska Miedź (Industrial Captive — Copper Mining)",
    "jsw": "JSW Jastrzębska (Industrial Captive — Coal Mining)",
    "jastrzębska spółka węglowa": "JSW Jastrzębska (Industrial Captive — Coal Mining)",
    "jastrzebska spolka weglowa": "JSW Jastrzębska (Industrial Captive — Coal Mining)",
    "pkn orlen": "PKN Orlen (Industrial Captive — Petrochemical)",
    "pkn orlen s.a.": "PKN Orlen (Industrial Captive — Petrochemical)",
    "orlen": "PKN Orlen (Industrial Captive — Petrochemical)",
    "orlen s.a.": "PKN Orlen (Industrial Captive — Petrochemical)",
    "grupa azoty": "Grupa Azoty (Industrial Captive — Chemical)",
    "grupa azoty s.a.": "Grupa Azoty (Industrial Captive — Chemical)",
    "arcelormittal poland": "ArcelorMittal Poland (Industrial Captive — Steel)",
    "arcelormittal polska": "ArcelorMittal Poland (Industrial Captive — Steel)",
    "arcelormittal": "ArcelorMittal Poland (Industrial Captive — Steel)",

    # ── Polish typographic-quote variants (Latvia + Czech precedent) ───
    # Polish uses „..." (U+201E + U+201D) bottom-open + top-close, same as
    # Czech/German/Latvian tradition
    'as "pge dystrybucja"': "PGE Dystrybucja",
    'as „pge dystrybucja"': "PGE Dystrybucja",
    'a.s. „pge dystrybucja"': "PGE Dystrybucja",
    'sp. z o.o. „tauron dystrybucja"': "Tauron Dystrybucja",
    'as "tauron dystrybucja"': "Tauron Dystrybucja",
    'as „tauron dystrybucja"': "Tauron Dystrybucja",
    'as "enea operator"': "Enea Operator",
    'as „enea operator"': "Enea Operator",
    'sp. z o.o. „enea operator"': "Enea Operator",
    'as "energa operator"': "Energa Operator",
    'as „energa operator"': "Energa Operator",
    'sp. z o.o. „innogy stoen operator"': "Innogy Stoen Operator",
    'sp. z o.o. „innogy stoen"': "Innogy Stoen Operator",
    'as "innogy stoen"': "Innogy Stoen Operator",
    'as „innogy stoen"': "Innogy Stoen Operator",
    'as "pse"': "PSE",
    'as „pse"': "PSE",
    'as "polskie sieci elektroenergetyczne"': "PSE",
    'as „polskie sieci elektroenergetyczne"': "PSE",
}


def normalise_owner_alias(raw: str | None) -> tuple[str | None, bool]:
    """Normalise a raw OSM operator= tag to canonical form.

    Returns (canonical_name_or_None, was_normalised_bool).
    - Applies Unicode NFC normalisation (Polish diacritics)
    - Case-insensitive lookup against _DNSP_ALIAS_MAP
    - Preserves original tag intent in raw_attributes.osm_original_operator
      (called by osm_overpass.py sub parser) per Convention #56 visibly-honest.
    """
    if not raw or not isinstance(raw, str):
        return None, False
    # NFC normalisation for Polish diacritics
    nfc = unicodedata.normalize("NFC", raw.strip())
    key = nfc.casefold()
    if key in _DNSP_ALIAS_MAP:
        return _DNSP_ALIAS_MAP[key], key != nfc.strip()
    return nfc.strip(), False


# ── Layer 3 lat/lon geofence (Convention #78 §4bis.5 3rd enforcement) ────
# Warsaw metro Innogy Stoen bbox — refined per Task #262 methodology
# (Prague precedent post-Wave-2 retrospective audit). Warsaw admin bounds
# (~517 km²) vs historic Innogy Stoen concession area (~350-400 km²) —
# refinement queued for post-fetch retrospective audit if empirical
# attribution > 10%.
INNOGY_STOEN_WARSAW_BBOX = {
    "lat_min": 52.10,
    "lat_max": 52.35,
    "lon_min": 20.85,
    "lon_max": 21.25,
    "km2_estimated": 517.0,   # admin bounds; ~1.4× historic concession
    "provenance": "Warsaw admin bounds initial; refinement candidate per Task #262 methodology",
}


# 4 DSO territorial partitions (bounding-box heuristic — supplemented by
# województwo NUTS-3 lookup when OSM populates ref:nuts:3 tags)
PGE_DYSTRYBUCJA_TERRITORIES_NUTS3 = frozenset({
    # Mazowieckie (excluding Warsaw metro)
    "PL911", "PL912", "PL921", "PL922", "PL923", "PL924", "PL925", "PL926",
    # Łódzkie
    "PL711", "PL712", "PL713", "PL714", "PL715",
    # Świętokrzyskie
    "PL721", "PL722",
    # Lubelskie
    "PL811", "PL812", "PL814", "PL815",
    # Podkarpackie
    "PL821", "PL822", "PL823", "PL824",
    # Warmińsko-Mazurskie
    "PL621", "PL622", "PL623",
})

TAURON_DYSTRYBUCJA_TERRITORIES_NUTS3 = frozenset({
    # Małopolskie
    "PL213", "PL214", "PL217", "PL218", "PL219", "PL21A",
    # Śląskie
    "PL22A", "PL22B", "PL22C", "PL227", "PL228", "PL229",
    # Opolskie
    "PL521", "PL522",
    # Dolnośląskie
    "PL514", "PL515", "PL516", "PL517", "PL518", "PL519", "PL51A",
})

ENEA_OPERATOR_TERRITORIES_NUTS3 = frozenset({
    # Wielkopolskie
    "PL411", "PL414", "PL415", "PL416", "PL417", "PL418",
    # Zachodniopomorskie
    "PL426", "PL427", "PL428",
    # Lubuskie
    "PL431", "PL432",
    # Kujawsko-Pomorskie (Bydgoszcz portion)
    "PL613", "PL616",
})

ENERGA_OPERATOR_TERRITORIES_NUTS3 = frozenset({
    # Pomorskie
    "PL633", "PL634", "PL636", "PL637", "PL638",
    # Kujawsko-Pomorskie (Toruń portion — partial)
    "PL611", "PL612", "PL614", "PL615", "PL617", "PL618", "PL619", "PL61A",
    # Warmińsko-Mazurskie (Elbląg portion)
    "PL624",
})


def _point_in_bbox(lat: float, lon: float, bbox: dict) -> bool:
    """Test if (lat, lon) falls within a bounding-box dict."""
    return (
        bbox["lat_min"] <= lat <= bbox["lat_max"]
        and bbox["lon_min"] <= lon <= bbox["lon_max"]
    )


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    nuts_3: str | None,
    lat: float | None,
    lon: float | None,
) -> tuple[str, str]:
    """Region-jurisdiction × voltage-class owner resolver — 9th cohort
    application with Convention #78 §4bis.5 Layer 3 geofence enforcement.

    Returns (owner_name, provenance_tag).

    Resolution order:
    1. Voltage-class TSO: ≥220 kV → PSE_TSO (Convention #56 preserved)
    2. NUTS-3 województwo → DSO map (4-DSO territorial partition)
       When OSM DOES populate ref:nuts:3 tags (Polish OSM does per
       empirical baseline metadata — richer than Slovakia/Czechia)
    3. Layer 3 geofence: Warsaw metro (Innogy Stoen bbox refined per
       Task #262 methodology)
    4. Unresolved fallback → PGE_Dystrybucja_default_LARGEST_DSO
       (documented in Convention #56 visibly-honest sense)
    """
    # Layer 1 — TSO voltage-class threshold
    if voltage_kv is not None and voltage_kv >= 220:
        return "PSE", "region_jurisdiction_fallback_PSE_via_voltage_class"

    # Layer 2 — NUTS-3 DSO map (rich for Poland baseline)
    if nuts_3:
        if nuts_3 in PGE_DYSTRYBUCJA_TERRITORIES_NUTS3:
            return "PGE Dystrybucja", "region_jurisdiction_fallback_PGE_via_nuts3"
        if nuts_3 in TAURON_DYSTRYBUCJA_TERRITORIES_NUTS3:
            return "Tauron Dystrybucja", "region_jurisdiction_fallback_Tauron_via_nuts3"
        if nuts_3 in ENEA_OPERATOR_TERRITORIES_NUTS3:
            return "Enea Operator", "region_jurisdiction_fallback_Enea_via_nuts3"
        if nuts_3 in ENERGA_OPERATOR_TERRITORIES_NUTS3:
            return "Energa Operator", "region_jurisdiction_fallback_Energa_via_nuts3"

    # Layer 3 — lat/lon geofence: Warsaw metro Innogy Stoen carve-out
    if lat is not None and lon is not None:
        if _point_in_bbox(lat, lon, INNOGY_STOEN_WARSAW_BBOX):
            return "Innogy Stoen Operator", "region_jurisdiction_fallback_Innogy_Stoen_via_lat_lon_geofence"

    # Layer 4 — unresolved default: PGE (LARGEST DSO territorial catch-all)
    return "PGE Dystrybucja", "region_jurisdiction_fallback_PGE_via_LARGEST_DSO_default"


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    POLAND_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return POLAND_CACHE_DIR / f"{key}{ext}"


# ── Discipline #36 bounds filter (Poland polygon, 100m default) ──────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Apply Discipline #36 point-in-polygon filter using poland/bounds.json.
    Returns (kept, dropped) tuple. 100m tolerance per cross_border_tolerances.json.

    Follows Czechia P20 canonical signature — canada._base.apply_bounds_filter
    is keyword-only (`country_slug` + `tolerance_km`), NOT positional path args.
    """
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(POLAND_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("poland", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="poland", tolerance_km=tolerance_km
    )


# ── Audit sidecar emission (v43_provenance sidecar per Convention #56) ───
def emit_audit_sidecar(result: IngestionResult, out_path: Path) -> Path:
    """Emit YAML audit sidecar to <path>. Convention #56 visibly-honest
    degradation preserved via warnings + fetched_at_utc metadata."""
    lines = [
        f"# Poland v4.23 OSM Overpass audit sidecar",
        f"# Source: {result.source_id}",
        f"# Fetched: {result.fetched_at_utc}",
        f"# SHA-256: {result.raw_sha256}",
        f"# Substations: {len(result.substations)}",
        f"# Transmission lines: {len(result.transmission_lines)}",
        f"# Raw bytes: {result.raw_bytes_fetched}",
        f"# Warnings ({len(result.warnings)}):",
    ]
    for w in result.warnings:
        lines.append(f"#   - {w}")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


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
    "normalise_owner_alias",
    "POLAND_BOUNDS_JSON",
    "POLAND_TOLERANCE_JSON",
    "POLAND_DATA_DIR",
    "POLAND_CACHE_DIR",
]
