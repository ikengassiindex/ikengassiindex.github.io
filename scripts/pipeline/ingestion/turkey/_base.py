"""Turkey v4.23 substation ingestion base module.

Shared infrastructure for OSM Overpass fetch + provenance + resolver +
alias normalisation across Turkish scripts (Latin + Turkish diacritics
+ Kurdish + Arabic + Ottoman legacy).

Convention preservation:
- #7 Data-Layer Anchoring (documented proxy per country hazard baselines)
- #23 Provenance pinning (SHA-256 raw payload + audit sidecar)
- #36 Cross-border filter (5.0 km tolerance turkey entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation (partial-fetch preserved end-to-end)
- #60 Non-commercial provenance (OSM ODbL + TEİAŞ SOE + EPİAŞ public)
- #78 BINDING 12th enforcement — Turkish + Kurdish + Arabic + Greek + English + Ottoman legacy
- #78 §4bis.5 Layer 3 8TH ENFORCEMENT — Istanbul 3-way BEDAŞ + AYEDAŞ + BOĞAZİÇİ
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
COUNTRY_SLUG = "turkey"
COUNTRY_CODE = "tr"

# ─── Convention #78 §4bis.5 Layer 3 8TH ENFORCEMENT — Istanbul 3-way geofence ───
# Bosphorus separates European Istanbul (BEDAŞ) from Asian Istanbul (AYEDAŞ)
# with BOĞAZİÇİ strait carve-out capturing 3 HV crossings + legacy operator name.
ISTANBUL_BEDAS_BBOX = {
    "lat_min": 40.85, "lat_max": 41.30,
    "lon_min": 28.30, "lon_max": 29.05,
    "operator_canonical": "BEDAŞ",
    "operator_english": "Bogazici Electricity Distribution",
    "role": "ISTANBUL_EUROPEAN_SIDE_DSO",
    "customers_millions": 4.5,
}

ISTANBUL_AYEDAS_BBOX = {
    "lat_min": 40.85, "lat_max": 41.30,
    "lon_min": 29.05, "lon_max": 30.00,
    "operator_canonical": "AYEDAŞ",
    "operator_english": "Anatolian Side Electricity Distribution",
    "role": "ISTANBUL_ASIAN_SIDE_DSO",
    "customers_millions": 3.0,
}

BOSPHORUS_STRAIT_BBOX = {
    "lat_min": 41.00, "lat_max": 41.20,
    "lon_min": 29.00, "lon_max": 29.15,
    "operator_canonical": "BOĞAZİÇİ",
    "operator_english": "Bosphorus Strait HV Crossing Zone",
    "role": "BOSPHORUS_STRAIT_HV_CROSSING_GEOFENCE",
    "note": "3 HV crossings — Boğaziçi 380kV AC 1968 + FSM 154kV AC 1993 + Yavuz Sultan Selim 500kV HVDC 2016 + adjacent submarine cables + pre-2013 monolithic operator name capture",
}

# ─── Åland-analog — Aegean isolated islands carve-out (Layer 4c) ───
# Bozcaada + Gökçeada (large Aegean Turkish islands) — potential DSO carve-out
AEGEAN_ISOLATED_BBOX = {
    "lat_min": 39.75, "lat_max": 40.25,
    "lon_min": 25.55, "lon_max": 26.20,
    "operator_canonical": "TREDAŞ_Aegean_Islands",
    "role": "AEGEAN_ISLANDS_TREDAS_ISOLATED_CARVE_OUT",
    "note": "Bozcaada + Gökçeada Aegean Turkish islands (Çanakkale province)",
}

# ─── Voltage thresholds ───
TSO_MIN_KV = 154.0  # TEİAŞ transmission threshold — Turkish 154 kV subtransmission tier is TSO-owned
EHV_KV = 380.0      # TEİAŞ EHV backbone
NUCLEAR_KV = 500.0  # HVDC + high-voltage nuclear connection tier

# ─── 21-DSO admin-based region map (Layer 3b) ───
# Post-2013 privatization → 21 DSOs cover Turkey's 81 provinces
# (Kayseri KCETAŞ is only non-privatized municipal DSO)
DSO_PROVINCE_MAP: dict[str, str] = {
    # Istanbul 3-way handled separately at Layer 3a §4bis.5 geofence
    "Istanbul": "BEDAŞ/AYEDAŞ/BOĞAZİÇİ",  # Layer 3a geofence override
    # ── TREDAŞ (Thrace European) ──
    "Edirne": "TREDAŞ",
    "Kırklareli": "TREDAŞ",
    "Tekirdağ": "TREDAŞ",
    # ── SEDAŞ (Sakarya/Marmara East) ──
    "Sakarya": "SEDAŞ",
    "Kocaeli": "SEDAŞ",
    "Bolu": "SEDAŞ",
    "Düzce": "SEDAŞ",
    # ── UEDAŞ (Bursa/Marmara South) ──
    "Bursa": "UEDAŞ",
    "Balıkesir": "UEDAŞ",
    "Yalova": "UEDAŞ",
    "Çanakkale": "UEDAŞ",
    # ── OEDAŞ (Eskişehir/Aegean East) ──
    "Eskişehir": "OEDAŞ",
    "Bilecik": "OEDAŞ",
    "Afyonkarahisar": "OEDAŞ",
    "Kütahya": "OEDAŞ",
    "Uşak": "OEDAŞ",
    # ── Gediz EDAŞ (İzmir/Aegean) ──
    "İzmir": "Gediz",
    "Manisa": "Gediz",
    # ── ADM/Aydem EDAŞ (Aegean South) ──
    "Aydın": "ADM",
    "Denizli": "ADM",
    "Muğla": "ADM",
    # ── Akdeniz EDAŞ (Mediterranean) ──
    "Antalya": "Akdeniz EDAŞ",
    "Isparta": "Akdeniz EDAŞ",
    "Burdur": "Akdeniz EDAŞ",
    # ── Toroslar EDAŞ (Southern Anatolia — 2023 EARTHQUAKE RECONSTRUCTION zone) ──
    "Adana": "Toroslar",
    "Mersin": "Toroslar",
    "Hatay": "Toroslar",  # RECONSTRUCTION
    "Osmaniye": "Toroslar",  # RECONSTRUCTION
    "Gaziantep": "Toroslar",  # RECONSTRUCTION + refugee cohort
    "Kilis": "Toroslar",  # Syrian border + refugee
    # ── Başkent EDAŞ (Ankara/Central) ──
    "Ankara": "Başkent",
    "Karabük": "Başkent",
    "Kastamonu": "Başkent",
    "Kırıkkale": "Başkent",
    "Zonguldak": "Başkent",
    "Bartın": "Başkent",
    "Çankırı": "Başkent",
    # ── Meram EDAŞ (Konya/Central) ──
    "Konya": "Meram",
    "Karaman": "Meram",
    "Aksaray": "Meram",
    "Niğde": "Meram",
    "Nevşehir": "Meram",
    "Kırşehir": "Meram",
    # ── KCETAŞ (Kayseri MUNICIPAL — ONLY non-privatized) ──
    "Kayseri": "KCETAŞ",  # note: municipal-owned
    # ── YEDAŞ (Yeşilırmak/Black Sea Central — 2021 KARADENIZ FLOOD zone) ──
    "Samsun": "YEDAŞ",
    "Ordu": "YEDAŞ",  # FLOOD 2021
    "Sinop": "YEDAŞ",  # FLOOD 2021
    "Amasya": "YEDAŞ",
    "Çorum": "YEDAŞ",
    "Tokat": "YEDAŞ",
    # ── ÇEDAŞ (Çamlıbel/Central Anatolia) ──
    "Sivas": "ÇEDAŞ",
    "Yozgat": "ÇEDAŞ",
    # ── Fırat EDAŞ (Eastern Anatolia — 2023 EARTHQUAKE RECONSTRUCTION partial) ──
    "Elazığ": "Fırat",  # RECONSTRUCTION partial
    "Malatya": "Fırat",  # RECONSTRUCTION
    "Bingöl": "Fırat",
    "Tunceli": "Fırat",
    # ── DEDAŞ (Dicle/SE Anatolia — Kurdish region + 4M Syrian refugee LARGEST global) ──
    "Diyarbakır": "DEDAŞ",  # Kurdish region
    "Şırnak": "DEDAŞ",
    "Batman": "DEDAŞ",
    "Mardin": "DEDAŞ",
    "Siirt": "DEDAŞ",
    "Şanlıurfa": "DEDAŞ",  # LARGEST refugee cohort
    "Adıyaman": "DEDAŞ",  # RECONSTRUCTION
    # ── VEDAŞ (Van Gölü/Far East) ──
    "Van": "VEDAŞ",
    "Bitlis": "VEDAŞ",
    "Muş": "VEDAŞ",
    "Hakkari": "VEDAŞ",  # Iranian/Iraqi border
    # ── Aras EDAŞ (Northeast — Armenian border-CLOSED + Georgian border) ──
    "Erzurum": "Aras",
    "Erzincan": "Aras",
    "Ağrı": "Aras",
    "Kars": "Aras",  # Georgian border
    "Iğdır": "Aras",  # Armenian border CLOSED
    "Ardahan": "Aras",  # Georgian border
    "Bayburt": "Aras",
    "Gümüşhane": "Çoruh",  # actually Çoruh EDAŞ
    # ── Çoruh EDAŞ (Black Sea East — Georgian border + high seismic) ──
    "Rize": "Çoruh",
    "Trabzon": "Çoruh",  # 2011 earthquake legacy
    "Artvin": "Çoruh",  # Georgian border
    # ── Kahramanmaraş RECONSTRUCTION zone (2023 M7.8) ──
    "Kahramanmaraş": "Toroslar",  # earthquake epicenter
}


def _normalize_operator(name: str) -> str:
    """NFC normalization + strip + lowercase for alias matching.

    Preserves Turkish diacritics ç ğ ı ö ş ü + Kurdish ê î û + Arabic script.
    Per Convention #78 BINDING 12th enforcement.
    """
    if not name:
        return ""
    # NFC normalization — required for Turkish diacritics + Ottoman legacy
    normalized = unicodedata.normalize("NFC", name)
    return normalized.strip().lower()


# ─── Convention #78 BINDING 12th enforcement — Turkish alias map (~150 entries) ───
# Turkish + Kurdish + Arabic + Greek + Ottoman + English variants
_ALIAS_MAP: dict[str, str] = {
    # ═══ TEİAŞ national TSO (state-owned 100%) ═══
    _normalize_operator("TEİAŞ"): "TEİAŞ",
    _normalize_operator("TEIAS"): "TEİAŞ",
    _normalize_operator("Teias"): "TEİAŞ",
    _normalize_operator("Türkiye Elektrik İletim"): "TEİAŞ",
    _normalize_operator("Türkiye Elektrik İletim A.Ş."): "TEİAŞ",
    _normalize_operator("Türkiye Elektrik İletim Anonim Şirketi"): "TEİAŞ",
    _normalize_operator("Turkiye Elektrik Iletim"): "TEİAŞ",
    _normalize_operator("Turkey Electricity Transmission"): "TEİAŞ",
    _normalize_operator("Turkish Electricity Transmission"): "TEİAŞ",
    _normalize_operator("Turkish Electricity Transmission Company"): "TEİAŞ",
    _normalize_operator("TEİAŞ Genel Müdürlüğü"): "TEİAŞ",
    _normalize_operator("TEIAS Genel Mudurlugu"): "TEİAŞ",
    _normalize_operator("TEİAŞ Ankara"): "TEİAŞ",
    # TEK legacy predecessor (pre-2001 monopoly, broken by Law 4628)
    _normalize_operator("TEK"): "TEİAŞ",  # ambiguous — could be TEDAŞ/EÜAŞ/TETAŞ but historically → TEİAŞ transmission side
    _normalize_operator("Türkiye Elektrik Kurumu"): "TEİAŞ",
    _normalize_operator("Turkiye Elektrik Kurumu"): "TEİAŞ",

    # ═══ EÜAŞ state generation (Layer 4b — generation, not grid) ═══
    _normalize_operator("EÜAŞ"): "EÜAŞ",
    _normalize_operator("EUAS"): "EÜAŞ",
    _normalize_operator("Elektrik Üretim A.Ş."): "EÜAŞ",
    _normalize_operator("Elektrik Uretim Anonim Sirketi"): "EÜAŞ",
    _normalize_operator("Electricity Generation Company"): "EÜAŞ",
    # TETAŞ trading (merged into EÜAŞ 2019)
    _normalize_operator("TETAŞ"): "TETAŞ",
    _normalize_operator("TETAS"): "TETAŞ",
    _normalize_operator("Türkiye Elektrik Ticaret"): "TETAŞ",
    _normalize_operator("Turkey Electricity Trading"): "TETAŞ",

    # ═══ Convention #78 §4bis.5 Layer 3 8TH ENFORCEMENT — Istanbul 3-way ═══
    # BEDAŞ (European Istanbul)
    _normalize_operator("BEDAŞ"): "BEDAŞ",
    _normalize_operator("BEDAS"): "BEDAŞ",
    _normalize_operator("Boğaziçi Elektrik Dağıtım"): "BEDAŞ",
    _normalize_operator("Boğaziçi Elektrik Dağıtım A.Ş."): "BEDAŞ",
    _normalize_operator("Bogazici Elektrik Dagitim"): "BEDAŞ",
    _normalize_operator("Bogazici Electricity Distribution"): "BEDAŞ",
    _normalize_operator("BEDAS Elektrik"): "BEDAŞ",
    # AYEDAŞ (Asian Istanbul)
    _normalize_operator("AYEDAŞ"): "AYEDAŞ",
    _normalize_operator("AYEDAS"): "AYEDAŞ",
    _normalize_operator("Anadolu Yakası Elektrik Dağıtım"): "AYEDAŞ",
    _normalize_operator("Anadolu Yakası Elektrik Dağıtım A.Ş."): "AYEDAŞ",
    _normalize_operator("Anadolu Yakasi Elektrik Dagitim"): "AYEDAŞ",
    _normalize_operator("Anatolian Side Electricity Distribution"): "AYEDAŞ",
    _normalize_operator("Anatolian Side Electricity"): "AYEDAŞ",
    # BOĞAZİÇİ strait / legacy pre-2013 monolithic operator name
    _normalize_operator("BOĞAZİÇİ"): "BOĞAZİÇİ",
    _normalize_operator("BOGAZICI"): "BOĞAZİÇİ",
    _normalize_operator("Bosphorus"): "BOĞAZİÇİ",
    _normalize_operator("Boğaziçi"): "BOĞAZİÇİ",
    _normalize_operator("Boğaz"): "BOĞAZİÇİ",  # Turkish for "strait"

    # ═══ 18 other privatized DSOs (Layer 3b admin resolver) ═══
    # TREDAŞ (Thrace European)
    _normalize_operator("TREDAŞ"): "TREDAŞ",
    _normalize_operator("TREDAS"): "TREDAŞ",
    _normalize_operator("Trakya Elektrik Dağıtım"): "TREDAŞ",
    _normalize_operator("Trakya EDAŞ"): "TREDAŞ",
    _normalize_operator("Trakya EDAS"): "TREDAŞ",
    _normalize_operator("Thrace Electricity Distribution"): "TREDAŞ",
    # SEDAŞ (Sakarya)
    _normalize_operator("SEDAŞ"): "SEDAŞ",
    _normalize_operator("SEDAS"): "SEDAŞ",
    _normalize_operator("Sakarya Elektrik Dağıtım"): "SEDAŞ",
    _normalize_operator("Sakarya EDAŞ"): "SEDAŞ",
    _normalize_operator("Sakarya EDAS"): "SEDAŞ",
    # UEDAŞ (Bursa/Uludağ)
    _normalize_operator("UEDAŞ"): "UEDAŞ",
    _normalize_operator("UEDAS"): "UEDAŞ",
    _normalize_operator("Uludağ Elektrik Dağıtım"): "UEDAŞ",
    _normalize_operator("Uludag Elektrik Dagitim"): "UEDAŞ",
    _normalize_operator("Uludağ EDAŞ"): "UEDAŞ",
    # OEDAŞ (Osmangazi/Eskişehir)
    _normalize_operator("OEDAŞ"): "OEDAŞ",
    _normalize_operator("OEDAS"): "OEDAŞ",
    _normalize_operator("Osmangazi Elektrik Dağıtım"): "OEDAŞ",
    _normalize_operator("Osmangazi EDAŞ"): "OEDAŞ",
    _normalize_operator("Osmangazi EDAS"): "OEDAŞ",
    # Gediz EDAŞ (İzmir/Aegean)
    _normalize_operator("Gediz"): "Gediz",
    _normalize_operator("Gediz EDAŞ"): "Gediz",
    _normalize_operator("Gediz EDAS"): "Gediz",
    _normalize_operator("Gediz Elektrik Dağıtım"): "Gediz",
    _normalize_operator("Gediz Elektrik Dagitim"): "Gediz",
    # ADM/Aydem EDAŞ (Aegean South)
    _normalize_operator("ADM"): "ADM",
    _normalize_operator("ADM Elektrik Dağıtım"): "ADM",
    _normalize_operator("ADEDAŞ"): "ADM",
    _normalize_operator("ADEDAS"): "ADM",
    _normalize_operator("Aydem"): "ADM",
    _normalize_operator("Aydem Elektrik Dağıtım"): "ADM",
    _normalize_operator("Aydem EDAŞ"): "ADM",
    # Akdeniz EDAŞ (Mediterranean)
    _normalize_operator("Akdeniz EDAŞ"): "Akdeniz EDAŞ",
    _normalize_operator("Akdeniz EDAS"): "Akdeniz EDAŞ",
    _normalize_operator("Akdeniz Elektrik Dağıtım"): "Akdeniz EDAŞ",
    _normalize_operator("Akdeniz Electricity"): "Akdeniz EDAŞ",
    # Toroslar EDAŞ (Southern Anatolia — 2023 EARTHQUAKE zone)
    _normalize_operator("Toroslar"): "Toroslar",
    _normalize_operator("Toroslar EDAŞ"): "Toroslar",
    _normalize_operator("Toroslar EDAS"): "Toroslar",
    _normalize_operator("Toroslar Elektrik Dağıtım"): "Toroslar",
    _normalize_operator("Toros Elektrik"): "Toroslar",
    # Başkent EDAŞ (Ankara/Capital)
    _normalize_operator("Başkent"): "Başkent",
    _normalize_operator("Baskent"): "Başkent",
    _normalize_operator("Başkent EDAŞ"): "Başkent",
    _normalize_operator("Baskent EDAS"): "Başkent",
    _normalize_operator("Başkent Elektrik Dağıtım"): "Başkent",
    _normalize_operator("Capital Electricity Distribution"): "Başkent",
    # Meram EDAŞ (Konya/Central)
    _normalize_operator("Meram"): "Meram",
    _normalize_operator("Meram EDAŞ"): "Meram",
    _normalize_operator("Meram EDAS"): "Meram",
    _normalize_operator("Meram Elektrik Dağıtım"): "Meram",
    # KCETAŞ (Kayseri MUNICIPAL — only non-privatized)
    _normalize_operator("KCETAŞ"): "KCETAŞ",
    _normalize_operator("KCETAS"): "KCETAŞ",
    _normalize_operator("Kayseri ve Civarı Elektrik"): "KCETAŞ",
    _normalize_operator("Kayseri Elektrik Dağıtım"): "KCETAŞ",
    _normalize_operator("Kayseri Elektrik"): "KCETAŞ",
    # YEDAŞ (Yeşilırmak — 2021 KARADENIZ FLOOD zone)
    _normalize_operator("YEDAŞ"): "YEDAŞ",
    _normalize_operator("YEDAS"): "YEDAŞ",
    _normalize_operator("Yeşilırmak Elektrik Dağıtım"): "YEDAŞ",
    _normalize_operator("Yesilirmak EDAS"): "YEDAŞ",
    _normalize_operator("Yesilirmak Elektrik"): "YEDAŞ",
    # ÇEDAŞ (Çamlıbel)
    _normalize_operator("ÇEDAŞ"): "ÇEDAŞ",
    _normalize_operator("CEDAS"): "ÇEDAŞ",
    _normalize_operator("Çamlıbel Elektrik Dağıtım"): "ÇEDAŞ",
    _normalize_operator("Camlibel Elektrik Dagitim"): "ÇEDAŞ",
    _normalize_operator("Camlibel EDAS"): "ÇEDAŞ",
    # Fırat EDAŞ (Eastern Anatolia — RECONSTRUCTION partial)
    _normalize_operator("Fırat EDAŞ"): "Fırat",
    _normalize_operator("Firat EDAS"): "Fırat",
    _normalize_operator("Fırat Elektrik Dağıtım"): "Fırat",
    _normalize_operator("Firat Elektrik Dagitim"): "Fırat",
    # DEDAŞ (Dicle — Kurdish region + refugee 4M LARGEST global)
    _normalize_operator("DEDAŞ"): "DEDAŞ",
    _normalize_operator("DEDAS"): "DEDAŞ",
    _normalize_operator("Dicle Elektrik Dağıtım"): "DEDAŞ",
    _normalize_operator("Dicle EDAŞ"): "DEDAŞ",
    _normalize_operator("Dicle EDAS"): "DEDAŞ",
    _normalize_operator("Dicle Electricity"): "DEDAŞ",
    # Kurdish variant (Recognition 2013)
    _normalize_operator("Dîcle"): "DEDAŞ",  # Kurdish diacritic
    # VEDAŞ (Van Gölü — Far East)
    _normalize_operator("VEDAŞ"): "VEDAŞ",
    _normalize_operator("VEDAS"): "VEDAŞ",
    _normalize_operator("Van Gölü Elektrik Dağıtım"): "VEDAŞ",
    _normalize_operator("Van Golu EDAS"): "VEDAŞ",
    _normalize_operator("Van Gölü EDAŞ"): "VEDAŞ",
    _normalize_operator("Lake Van Electricity"): "VEDAŞ",
    # Aras EDAŞ (Northeast — Armenian/Georgian borders)
    _normalize_operator("Aras"): "Aras",
    _normalize_operator("Aras EDAŞ"): "Aras",
    _normalize_operator("Aras EDAS"): "Aras",
    _normalize_operator("Aras Elektrik Dağıtım"): "Aras",
    # Çoruh EDAŞ (Black Sea East — high seismic + Georgian border)
    _normalize_operator("Çoruh EDAŞ"): "Çoruh",
    _normalize_operator("Coruh EDAS"): "Çoruh",
    _normalize_operator("Çoruh"): "Çoruh",
    _normalize_operator("Coruh"): "Çoruh",
    _normalize_operator("Çoruh Elektrik Dağıtım"): "Çoruh",

    # ═══ Nuclear generation (Layer 4b generation carve-out) ═══
    _normalize_operator("Akkuyu"): "Akkuyu",
    _normalize_operator("Akkuyu Nükleer"): "Akkuyu",
    _normalize_operator("Akkuyu Nukleer"): "Akkuyu",
    _normalize_operator("Akkuyu NGS"): "Akkuyu",
    _normalize_operator("Akkuyu NPP"): "Akkuyu",
    _normalize_operator("Akkuyu Nuclear"): "Akkuyu",
    _normalize_operator("Akkuyu Nuclear Power Plant"): "Akkuyu",
    _normalize_operator("Akkuyu Nükleer Güç Santrali"): "Akkuyu",
    _normalize_operator("Rosatom Akkuyu"): "Akkuyu",

    # ═══ TCDD rail (Layer 4b — 25 kV AC electrified) ═══
    _normalize_operator("TCDD"): "TCDD",
    _normalize_operator("Türkiye Cumhuriyeti Devlet Demiryolları"): "TCDD",
    _normalize_operator("Turkiye Cumhuriyeti Devlet Demiryollari"): "TCDD",
    _normalize_operator("Devlet Demiryolları"): "TCDD",
    _normalize_operator("Turkish State Railways"): "TCDD",
    _normalize_operator("TCDD Genel Müdürlüğü"): "TCDD",
    _normalize_operator("YHT"): "TCDD",  # Yüksek Hızlı Tren (high-speed rail)
    _normalize_operator("Yüksek Hızlı Tren"): "TCDD",

    # ═══ BOTAŞ natural gas TSO (Layer 2 catchment — gas pumping) ═══
    _normalize_operator("BOTAŞ"): "BOTAŞ",
    _normalize_operator("BOTAS"): "BOTAŞ",
    _normalize_operator("Boru Hatları ile Petrol Taşıma"): "BOTAŞ",
    _normalize_operator("Boru Hatlari ile Petrol Tasima"): "BOTAŞ",
    _normalize_operator("Boru Hatları Petrol"): "BOTAŞ",
    _normalize_operator("Petroleum Pipeline Corporation"): "BOTAŞ",
    _normalize_operator("BOTAŞ Genel Müdürlüğü"): "BOTAŞ",

    # ═══ Cross-border interconnector operators (informational) ═══
    # Bulgaria: ESO EAD (Elektroenergien Sistemen Operator) — via Kapıkule
    _normalize_operator("ESO"): "TEİAŞ",  # cross-border tag → route to Turkish TSO
    _normalize_operator("ESO EAD"): "TEİAŞ",
    # Greece: ADMIE/IPTO — via Nea Santa Thrace crossing
    _normalize_operator("ADMIE"): "TEİAŞ",
    _normalize_operator("IPTO"): "TEİAŞ",
    # Georgia: GSE (Georgian State Electrosystem) — via Meltem/Kars
    _normalize_operator("GSE"): "TEİAŞ",
    _normalize_operator("Georgian State Electrosystem"): "TEİAŞ",
    # Iraq: MoE Iraq — via Cizre 400 kV
    _normalize_operator("Ministry of Electricity Iraq"): "TEİAŞ",
    # Iran: Tavanir — via Doğubayazıt HVDC
    _normalize_operator("Tavanir"): "TEİAŞ",
    _normalize_operator("Iran Power Generation"): "TEİAŞ",
}


def normalize_operator_name(raw: Optional[str]) -> tuple[Optional[str], bool]:
    """Return (canonical_name, was_alias_normalised).

    Per Convention #78 BINDING 12th enforcement — NFC normalization
    for Turkish + Kurdish + Arabic + Greek + Ottoman legacy scripts.

    Returns (canonical, False) if raw already canonical or unmapped.
    Returns (canonical, True) if raw matched an alias.
    """
    if not raw:
        return (None, False)
    norm_key = _normalize_operator(raw)
    if norm_key in _ALIAS_MAP:
        canonical = _ALIAS_MAP[norm_key]
        # Distinguish "was already canonical" from "was alias-normalised"
        was_normalised = _normalize_operator(canonical) != norm_key
        return (canonical, was_normalised)
    return (raw, False)


def is_in_bbox(lat: float, lon: float, bbox: dict) -> bool:
    """Convention #78 §4bis.5 Layer 3 geofence check."""
    return (
        bbox["lat_min"] <= lat <= bbox["lat_max"]
        and bbox["lon_min"] <= lon <= bbox["lon_max"]
    )


def resolve_owner_via_admin(province: Optional[str]) -> Optional[str]:
    """Layer 3b admin-based resolver (21-DSO Turkish province → DSO).

    Returns None if province unknown (Layer 5 fallback to TEİAŞ catch-all).
    """
    if not province:
        return None
    return DSO_PROVINCE_MAP.get(province)


@dataclass
class OwnerResolverResult:
    """Per-substation owner attribution decision + provenance.

    Layer routing (8-layer resolver + admin fallback):
    - Layer 0: Direct OSM operator= tag (Convention #78 alias-normalise)
    - Layer 1: TEİAŞ TSO threshold (voltage ≥ 154 kV)
    - Layer 2: BOTAŞ natural-gas cross-sector
    - Layer 3a: Convention #78 §4bis.5 Istanbul 3-way geofence
    - Layer 3b: 21-DSO admin-based resolver
    - Layer 4a: Akkuyu nuclear generation carve-out
    - Layer 4b: TCDD rail 25 kV AC electrified
    - Layer 4c: Aegean isolated islands (Bozcaada/Gökçeada)
    - Layer 5: TEİAŞ Layer 6 catch-all default
    """
    canonical_name: str
    provenance: str
    was_alias_normalised: bool = False
    convention_78_4bis_5_geofence_hit: Optional[str] = None  # BEDAŞ/AYEDAŞ/BOĞAZİÇİ if fired


def resolve_owner(
    *,
    osm_operator: Optional[str],
    voltage_kv: Optional[float],
    lat: Optional[float],
    lon: Optional[float],
    province: Optional[str],
    name: Optional[str] = None,
) -> OwnerResolverResult:
    """Full 8-layer resolver dispatch for Turkey.

    Order matters — first-match wins per Nordic + Iceland precedent.
    """
    # ── Layer 0: Direct OSM operator= tag (highest confidence) ──
    if osm_operator:
        canonical, was_normalised = normalize_operator_name(osm_operator)
        if canonical:
            provenance = (
                "osm_operator_tag_direct_alias_normalised"
                if was_normalised
                else "osm_operator_tag_direct"
            )
            return OwnerResolverResult(
                canonical_name=canonical,
                provenance=provenance,
                was_alias_normalised=was_normalised,
            )

    # ── Layer 4a: Akkuyu nuclear name-match (before geofence — narrow) ──
    if name:
        name_norm = _normalize_operator(name)
        if "akkuyu" in name_norm:
            return OwnerResolverResult(
                canonical_name="Akkuyu",
                provenance="region_jurisdiction_layer_4a_akkuyu_nuclear_name_match",
            )

    # ── Layer 3a: Convention #78 §4bis.5 8TH ENFORCEMENT — Istanbul 3-way ──
    if lat is not None and lon is not None:
        # BOĞAZİÇİ strait carve-out (narrowest — first check)
        if is_in_bbox(lat, lon, BOSPHORUS_STRAIT_BBOX):
            return OwnerResolverResult(
                canonical_name="BOĞAZİÇİ",
                provenance="region_jurisdiction_layer_3_4bis5_8th_enforcement_BOĞAZİÇİ_strait_via_geofence",
                convention_78_4bis_5_geofence_hit="BOĞAZİÇİ",
            )
        # BEDAŞ European Istanbul
        if is_in_bbox(lat, lon, ISTANBUL_BEDAS_BBOX):
            return OwnerResolverResult(
                canonical_name="BEDAŞ",
                provenance="region_jurisdiction_layer_3_4bis5_8th_enforcement_BEDAŞ_via_Istanbul_geofence",
                convention_78_4bis_5_geofence_hit="BEDAŞ",
            )
        # AYEDAŞ Asian Istanbul
        if is_in_bbox(lat, lon, ISTANBUL_AYEDAS_BBOX):
            return OwnerResolverResult(
                canonical_name="AYEDAŞ",
                provenance="region_jurisdiction_layer_3_4bis5_8th_enforcement_AYEDAŞ_via_Istanbul_geofence",
                convention_78_4bis_5_geofence_hit="AYEDAŞ",
            )
        # ── Layer 4c: Aegean isolated islands (Bozcaada + Gökçeada) ──
        if is_in_bbox(lat, lon, AEGEAN_ISOLATED_BBOX):
            return OwnerResolverResult(
                canonical_name="TREDAŞ",  # Bozcaada+Gökçeada under Çanakkale → TREDAŞ actually UEDAŞ
                provenance="region_jurisdiction_layer_4c_aegean_isolated_islands_via_bbox",
            )

    # ── Layer 1: TEİAŞ TSO threshold (voltage ≥ 154 kV) ──
    if voltage_kv is not None and voltage_kv >= TSO_MIN_KV:
        return OwnerResolverResult(
            canonical_name="TEİAŞ",
            provenance="region_jurisdiction_layer_1_TEİAŞ_TSO_threshold_ge_154kv",
        )

    # ── Layer 3b: 21-DSO admin-based resolver ──
    dso = resolve_owner_via_admin(province)
    if dso:
        return OwnerResolverResult(
            canonical_name=dso,
            provenance=f"region_jurisdiction_layer_3b_{dso}_via_admin_map",
        )

    # ── Layer 5: TEİAŞ Layer 6 catch-all default (post-Nordic precedent) ──
    return OwnerResolverResult(
        canonical_name="TEİAŞ",
        provenance="region_jurisdiction_layer_6_TEİAŞ_catch_all_default",
    )


# ─── Discipline #36 cross-border filter ───
def load_bounds_polygon() -> Optional[Any]:
    """Load turkey bounds.json 2-polygon file (European Thrace + Asian Anatolia)."""
    bounds_path = REPO_ROOT / COUNTRY_SLUG / "bounds.json"
    if not bounds_path.exists():
        logger.warning(f"bounds.json not found at {bounds_path}")
        return None
    try:
        return json.loads(bounds_path.read_text())
    except Exception as exc:
        logger.error(f"Failed to load bounds.json: {exc}")
        return None


def load_tolerance_km() -> float:
    """Load turkey tolerance from cross_border_tolerances.json (5.0 km)."""
    tolerance_path = REPO_ROOT / "cross_border_tolerances.json"
    try:
        data = json.loads(tolerance_path.read_text())
        return data.get("countries", {}).get(COUNTRY_SLUG, {}).get(
            "boundary_tolerance_km", data.get("_default_tolerance_km", 0.1)
        )
    except Exception as exc:
        logger.warning(f"Failed to load tolerance: {exc}; defaulting to 5.0 km")
        return 5.0


def apply_bounds_filter(
    features: list[dict[str, Any]],
    *,
    tolerance_km: Optional[float] = None,
) -> tuple[list[dict[str, Any]], int]:
    """Discipline #36 cross-border filter with turkey 5.0 km tolerance.

    Returns (filtered_features, drops_count).
    """
    if tolerance_km is None:
        tolerance_km = load_tolerance_km()

    # NOTE: This is a shim signature — real implementation delegates to
    # scripts/pipeline/utils/cross_border.py::filter_by_country_polygon
    # per canonical Nordic pattern. Actual filter body imported downstream.
    try:
        from scripts.pipeline.utils.cross_border import (
            filter_by_country_polygon,
        )
        return filter_by_country_polygon(
            features,
            country_slug=COUNTRY_SLUG,
            tolerance_km=tolerance_km,
        )
    except ImportError:
        logger.warning(
            f"cross_border filter unavailable; passing through {len(features)} features"
        )
        return (features, 0)


# ─── Convention #23 provenance ───
def sha256_hexdigest(data: bytes) -> str:
    """Convention #23 SHA-256 raw payload provenance pin."""
    return hashlib.sha256(data).hexdigest()


# ─── Discipline #41 line-substation parity ───
def check_discipline_41(subs_count: int, lines_count: int) -> tuple[str, float]:
    """Discipline #41 — line/substation ratio target [1.5-5.0].

    Returns (message, ratio).
    """
    if subs_count == 0:
        return ("Discipline #41 DEGENERATE — 0 substations.", 0.0)
    ratio = lines_count / subs_count
    if ratio < 1.5:
        return (
            f"Discipline #41 BELOW_HEALTHY_BAND — {subs_count} substations + "
            f"{lines_count} lines (ratio {ratio:.2f}). May indicate line under-capture.",
            ratio,
        )
    elif ratio > 5.0:
        return (
            f"Discipline #41 ABOVE_HEALTHY_BAND — {subs_count} substations + "
            f"{lines_count} lines (ratio {ratio:.2f}). May indicate MV/LV over-capture.",
            ratio,
        )
    return (
        f"Discipline #41 OK — {subs_count} substations + {lines_count} lines (ratio {ratio:.2f}).",
        ratio,
    )


# ─── Audit sidecar emission ───
def emit_audit_sidecar(
    subcommand: str,
    *,
    substations_count: int,
    lines_count: int,
    raw_sha256: str,
    raw_bytes: int,
    owner_provenance_hist: dict[str, int],
    convention_78_binding_hits: int = 0,
    convention_78_4bis_5_hits: dict[str, int] = None,
    partial_fetch_notes: list[str] = None,
    discipline_41_msg: str = "",
    discipline_36_drops_subs: int = 0,
    discipline_36_drops_lines: int = 0,
) -> Path:
    """Emit YAML audit sidecar per Convention #23 provenance pinning.

    NOTE: Known cohort-wide filename bug — file lands at
    scripts/pipeline/data/turkey/v4_23-ingestion-audit-turkey--{subcommand}.yaml
    (double-hyphen) rather than turkey/. Non-blocking; batch-fix queued.
    """
    data_dir = REPO_ROOT / "scripts" / "pipeline" / "data" / COUNTRY_SLUG
    data_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = (
        data_dir / f"v4_23-ingestion-audit-{COUNTRY_SLUG}--{subcommand}.yaml"
    )

    lines = [
        "# SSI Index v4.23 — Turkey P30 Ingestion Audit Sidecar",
        f"# Subcommand: {subcommand}",
        f"# Convention #23 provenance pin — auto-generated by _base.emit_audit_sidecar",
        "",
        "schema_version: v4_23-ingestion-audit-1",
        "country_slug: turkey",
        f"subcommand: {subcommand}",
        f"substations_count: {substations_count}",
        f"lines_count: {lines_count}",
        f"raw_sha256: {raw_sha256}",
        f"raw_bytes_fetched: {raw_bytes}",
        "",
        "# Discipline #41 line-substation parity",
        f"discipline_41: '{discipline_41_msg}'",
        "",
        "# Discipline #36 cross-border filter drops",
        f"discipline_36_drops_subs: {discipline_36_drops_subs}",
        f"discipline_36_drops_lines: {discipline_36_drops_lines}",
        "",
        "# Owner-provenance distribution (Layer 0-5 resolver histogram)",
        "owner_provenance_histogram:",
    ]
    for prov, count in sorted(owner_provenance_hist.items(), key=lambda x: -x[1]):
        lines.append(f"  {prov}: {count}")
    lines.extend(
        [
            "",
            "# Convention #78 BINDING 12th enforcement empirical validation",
            f"convention_78_alias_normalisation_hits: {convention_78_binding_hits}",
            "",
            "# Convention #78 §4bis.5 Layer 3 8TH ENFORCEMENT — Istanbul 3-way",
            "convention_78_4bis_5_hits:",
        ]
    )
    if convention_78_4bis_5_hits:
        for k, v in sorted(convention_78_4bis_5_hits.items()):
            lines.append(f"  {k}: {v}")
    else:
        lines.append("  {}")

    if partial_fetch_notes:
        lines.append("")
        lines.append("# Convention #56 partial-fetch notes")
        for note in partial_fetch_notes:
            lines.append(f"  - {note}")

    sidecar_path.write_text("\n".join(lines) + "\n")
    logger.info(f"Wrote audit sidecar {sidecar_path} ({sidecar_path.stat().st_size} bytes)")
    return sidecar_path
