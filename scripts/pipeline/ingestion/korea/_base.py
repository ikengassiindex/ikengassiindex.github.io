"""
SSI Pipeline — Korea v4.23 ingestion, shared base layer.

Wave 3 Priority 26 (fifth Wave 3 country post-Ireland; SIMPLEST
cohort-wide architecture via KEPCO monopoly — vertically-integrated
state-owned utility owning ALL substations across ALL voltage tiers).
4th cohort-wide single-DSO application (after Greece P22 DEDDIE +
Costa Rica P13 ICE + Ireland P25 ESB Networks + now Korea P26 KEPCO).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 8th EMPIRICAL TEST ⚡

Eighth country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive Hangul + Latin transliteration + English
acronym alias mapping REQUIRED at Step 3 connector authoring time:
  - Hangul native forms (한국전력공사 / 한전 / 한국수력원자력)
  - Revised Romanization (RRK, 2000 standard) transliterations
  - McCune-Reischauer (M-R, pre-2000, still common) transliterations
  - English acronyms (KEPCO / KHNP / KPX / KDN)
  - Legal-form suffixes (주식회사 / 株式會社 / ㈜ / Co., Ltd.)
  - Predecessor: KECO (pre-1982 Korea Electric Company) →
    3 utilities merger → KEPCO 1982

FIRST Asian Wave 3 event — establishes Hangul multi-script cohort
precedent for future Japan (Kanji + Hiragana + Katakana) and
Taiwan (Traditional Chinese) onboardings.

Korea specifics:
  - KEPCO (한국전력공사, 한전) — Korea Electric Power Corporation.
    State-owned (Ministry of Trade, Industry and Energy 51.1% +
    Korea Development Bank 32.9%). Vertically-integrated
    monopoly: owns transmission (765/345/154 kV) + subtransmission
    (55 kV) + distribution (22.9/6.6 kV). ~2.5M km distribution
    network + ~30,000 km transmission. Established 1982 via merger
    of Korea Electric Company (KECO) + Korea Power Generation Co +
    Korea Hydro Electric Power Co.
  - KPX (전력거래소) — Korea Power Exchange. Market operator
    (dispatch only, NO ownership). Splits KEPCO's system operator
    function per 2001 partial unbundling.
  - KHNP (한국수력원자력, 한수원) — Korea Hydro & Nuclear Power.
    KEPCO subsidiary since 2001. Operates 6 nuclear plant sites:
    Kori (고리) / Hanbit (한빛, formerly Yonggwang) / Hanul (한울,
    formerly Ulchin) / Wolseong (월성) / Saeul (새울) + Shin-*
    prefix variants for new units. Nuclear-plant substations
    carved out at Layer 1 by name pattern.
  - 5 KEPCO generation subsidiaries (post-2001 unbundling):
    East-West Power (동서발전, KEWP) + Korea Southern Power
    (남부발전, KOSPO) + Korea Western Power (서부발전, KOWEPO) +
    Korea Midland Power (중부발전, KOMIPO) + Korea South-East Power
    (남동발전, KOEN). Own thermal + gas + renewable generation.
    Attribution at Layer 2 (name-based).
  - KDHC (한국지역난방공사) — Korea District Heating Corporation.
    CHP substations in Seoul/Bundang/Suwon/etc. Layer 2 identity.
  - KORAIL (한국철도공사, 코레일) — rail traction substations for
    KTX high-speed + conventional lines. Layer 2 identity.
  - Industrial captives: POSCO Energy (Gwangyang steel), GS EPS
    (Bugok LNG), SK Gas Power (Hadong CHP), Hyundai Green Power
    (Dangjin steel), Samsung Electronics self-generation
    (Hwaseong/Pyeongtaek/Giheung semiconductor fabs).
  - Jeju HVDC interconnector — 3 submarine cables between Jeju
    Island and Haenam (mainland Jeollanam): #1 (1998) 300 MW +
    #2 (2014) 400 MW + #3 (2022) 200 MW. DOMESTIC (Jeju is
    Korean territory). KEPCO-owned.

Historical predecessors preserved for audit trail:
  - Korea Electric Company (KECO, 한국전력) — 1961-1982 (merged
    Chosun Electric + Kyongsong Electric)
  - Korea Power Generation Company (1961-1982)
  - Korea Hydro Electric Power Company (1961-1982)
  - Pre-1961: Chosun Electric (조선전력, Japanese colonial-era +
    Republic post-1948) + Kyongsong Electric (경성전기)
"""

from __future__ import annotations

import hashlib
import json
import logging
import unicodedata
from pathlib import Path

from ...utils.tolerance import resolve_boundary_tolerance_km

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
KOREA_BOUNDS_JSON = REPO_ROOT / "korea" / "bounds.json"
KOREA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
KOREA_DATA_DIR = PIPELINE_DIR / "data" / "korea"
KOREA_CACHE_DIR = KOREA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 8th enforcement) ───
# Preemptive Hangul + Latin RRK/M-R + English acronyms + Chaebol captives
# + KEPCO GENCOs + legal-form suffixes (주식회사 / ㈜ / Co., Ltd.)
_DNSP_ALIAS_MAP = {
    # ── KEPCO variants (Korea Electric Power Corporation) ───────────────
    # LARGEST alias class — 99.5%+ of Korean substations
    "kepco": "KEPCO",
    "KEPCO": "KEPCO",
    "kepco co., ltd.": "KEPCO",
    "kepco co ltd": "KEPCO",
    "kepco corp": "KEPCO",
    "kepco corporation": "KEPCO",
    "korea electric power corporation": "KEPCO",
    "korea electric power corp": "KEPCO",
    "korea electric power": "KEPCO",
    "korean electric power corporation": "KEPCO",
    "korean electric power corp": "KEPCO",
    # Hangul native forms
    "한국전력공사": "KEPCO",
    "한전": "KEPCO",
    "한국전력": "KEPCO",
    "한국전력주식회사": "KEPCO",
    "한국전력(주)": "KEPCO",
    # Revised Romanization (RRK, 2000)
    "hanguk jeollyeok gongsa": "KEPCO",
    "hangug jeonlyeog gongsa": "KEPCO",
    "hanjeon": "KEPCO",
    "han jeon": "KEPCO",
    # McCune-Reischauer (M-R, pre-2000)
    "han'guk chŏllyŏk kongsa": "KEPCO",
    "hanguk chollyok kongsa": "KEPCO",
    "hanjŏn": "KEPCO",
    # Legal-form suffixes
    "kepco 주식회사": "KEPCO",
    "kepco ㈜": "KEPCO",
    "한전 ㈜": "KEPCO",
    # Predecessor: KECO (pre-1982 Korea Electric Company)
    "keco": "KEPCO-legacy (Korea Electric Company pre-1982 merger)",
    "korea electric company": "KEPCO-legacy (Korea Electric Company pre-1982 merger)",
    "korea electric co": "KEPCO-legacy (Korea Electric Company pre-1982 merger)",
    # Pre-1961 predecessors (Japanese colonial era + early Republic)
    "chosun electric": "KEPCO-legacy (Chosun Electric pre-1961 predecessor)",
    "조선전력": "KEPCO-legacy (Chosun Electric pre-1961 predecessor)",
    "kyongsong electric": "KEPCO-legacy (Kyongsong Electric pre-1961 predecessor)",
    "경성전기": "KEPCO-legacy (Kyongsong Electric pre-1961 predecessor)",

    # ── KHNP variants (Korea Hydro & Nuclear Power — nuclear operator) ──
    "khnp": "KHNP",
    "KHNP": "KHNP",
    "khnp co., ltd.": "KHNP",
    "khnp co ltd": "KHNP",
    "korea hydro & nuclear power": "KHNP",
    "korea hydro and nuclear power": "KHNP",
    "korea hydro nuclear power": "KHNP",
    "korea hydro & nuclear power co ltd": "KHNP",
    # Hangul
    "한국수력원자력": "KHNP",
    "한수원": "KHNP",
    "한국수력원자력주식회사": "KHNP",
    "한수원 ㈜": "KHNP",
    # RRK / M-R
    "hanguk suryeok wonjaryeok": "KHNP",
    "hansuwon": "KHNP",
    "han'guk suryŏk wŏnjaryŏk": "KHNP",

    # ── KPX variants (Korea Power Exchange — market operator only) ──────
    "kpx": "KPX (market operator — dispatch only, no ownership)",
    "KPX": "KPX (market operator — dispatch only, no ownership)",
    "korea power exchange": "KPX (market operator — dispatch only, no ownership)",
    "electric power exchange": "KPX (market operator — dispatch only, no ownership)",
    "전력거래소": "KPX (market operator — dispatch only, no ownership)",
    "jeonryeok georaeso": "KPX (market operator — dispatch only, no ownership)",

    # ── KEPCO KDN (SCADA / IT subsidiary) ────────────────────────────────
    "kdn": "KEPCO KDN (SCADA subsidiary)",
    "kepco kdn": "KEPCO KDN (SCADA subsidiary)",
    "케이디엔": "KEPCO KDN (SCADA subsidiary)",
    "한전kdn": "KEPCO KDN (SCADA subsidiary)",

    # ── 5 KEPCO GENCOs (post-2001 unbundling — generation only) ─────────
    # East-West Power (동서발전, KEWP)
    "ewp": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "kewp": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "east-west power": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "east west power": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "korea east-west power": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "동서발전": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    "한국동서발전": "East-West Power (GENCO — generation only, KEPCO subsidiary)",
    # Korea Southern Power (KOSPO, 남부발전)
    "kospo": "KOSPO Korea Southern Power (GENCO — generation only)",
    "korea southern power": "KOSPO Korea Southern Power (GENCO — generation only)",
    "남부발전": "KOSPO Korea Southern Power (GENCO — generation only)",
    "한국남부발전": "KOSPO Korea Southern Power (GENCO — generation only)",
    # Korea Western Power (KOWEPO, 서부발전)
    "kowepo": "KOWEPO Korea Western Power (GENCO — generation only)",
    "korea western power": "KOWEPO Korea Western Power (GENCO — generation only)",
    "서부발전": "KOWEPO Korea Western Power (GENCO — generation only)",
    "한국서부발전": "KOWEPO Korea Western Power (GENCO — generation only)",
    # Korea Midland Power (KOMIPO, 중부발전)
    "komipo": "KOMIPO Korea Midland Power (GENCO — generation only)",
    "korea midland power": "KOMIPO Korea Midland Power (GENCO — generation only)",
    "중부발전": "KOMIPO Korea Midland Power (GENCO — generation only)",
    "한국중부발전": "KOMIPO Korea Midland Power (GENCO — generation only)",
    # Korea South-East Power (KOEN, 남동발전)
    "koen": "KOEN Korea South-East Power (GENCO — generation only)",
    "korea south-east power": "KOEN Korea South-East Power (GENCO — generation only)",
    "korea southeast power": "KOEN Korea South-East Power (GENCO — generation only)",
    "남동발전": "KOEN Korea South-East Power (GENCO — generation only)",
    "한국남동발전": "KOEN Korea South-East Power (GENCO — generation only)",

    # ── KDHC (Korea District Heating Corporation — CHP subs) ────────────
    "kdhc": "KDHC Korea District Heating Corporation (CHP)",
    "korea district heating": "KDHC Korea District Heating Corporation (CHP)",
    "korea district heating corporation": "KDHC Korea District Heating Corporation (CHP)",
    "한국지역난방공사": "KDHC Korea District Heating Corporation (CHP)",
    "지역난방공사": "KDHC Korea District Heating Corporation (CHP)",

    # ── KORAIL (rail traction substations) ──────────────────────────────
    "korail": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "KORAIL": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "korea railroad corporation": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "korea railroad": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "한국철도공사": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "코레일": "KORAIL Korea Railroad Corporation (Rail Traction)",
    # KTX operator (KORAIL subsidiary)
    "ktx": "KORAIL Korea Railroad Corporation (KTX High-Speed Traction)",
    # KR (Korea Rail Network Authority — infrastructure)
    "kr": "KR Korea Rail Network Authority (Rail Infrastructure)",
    "한국철도시설공단": "KR Korea Rail Network Authority (Rail Infrastructure)",

    # ── Metro operators (urban rail traction) ───────────────────────────
    "seoul metro": "Seoul Metro (Urban Rail Traction — Seoul)",
    "서울교통공사": "Seoul Metro (Urban Rail Traction — Seoul)",
    "busan metro": "Busan Metro (Urban Rail Traction — Busan)",
    "부산교통공사": "Busan Metro (Urban Rail Traction — Busan)",
    "incheon metro": "Incheon Metro (Urban Rail Traction — Incheon)",
    "인천교통공사": "Incheon Metro (Urban Rail Traction — Incheon)",
    "daegu metro": "Daegu Metro (Urban Rail Traction — Daegu)",
    "대구도시철도공사": "Daegu Metro (Urban Rail Traction — Daegu)",

    # ── Industrial captives (Chaebol self-generation + heavy industry) ──
    # POSCO Energy (Gwangyang steel + LNG CHP)
    "posco": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "posco energy": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "포스코에너지": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "포스코": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "posco green solution": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    # GS EPS (Bugok LNG CHP)
    "gs eps": "GS EPS (Industrial Captive — LNG CHP)",
    "gs energy": "GS EPS (Industrial Captive — LNG CHP)",
    "지에스이피에스": "GS EPS (Industrial Captive — LNG CHP)",
    # SK Gas / SK E&S (Hadong LNG CHP + gas)
    "sk gas": "SK Gas Power (Industrial Captive — LNG CHP)",
    "sk e&s": "SK Gas Power (Industrial Captive — LNG CHP)",
    "sk energy": "SK Gas Power (Industrial Captive — LNG CHP)",
    "에스케이가스": "SK Gas Power (Industrial Captive — LNG CHP)",
    # Hyundai Green Power (Dangjin steel)
    "hyundai green power": "Hyundai Green Power (Industrial Captive — Steel CHP)",
    "hyundai energy": "Hyundai Green Power (Industrial Captive — Steel CHP)",
    "현대그린파워": "Hyundai Green Power (Industrial Captive — Steel CHP)",
    # Samsung Electronics self-generation (Hwaseong/Pyeongtaek/Giheung fabs)
    "samsung electronics": "Samsung Electronics self-gen (Industrial Captive — Semiconductor)",
    "삼성전자": "Samsung Electronics self-gen (Industrial Captive — Semiconductor)",
    # SK Hynix self-generation (Icheon/Cheongju fabs)
    "sk hynix": "SK Hynix self-gen (Industrial Captive — Semiconductor)",
    "sk 하이닉스": "SK Hynix self-gen (Industrial Captive — Semiconductor)",
    "에스케이하이닉스": "SK Hynix self-gen (Industrial Captive — Semiconductor)",
    # LG Chem (batteries + petrochemical CHP)
    "lg chem": "LG Chem self-gen (Industrial Captive — Petrochemical CHP)",
    "엘지화학": "LG Chem self-gen (Industrial Captive — Petrochemical CHP)",
    # Data centres (Naver / Kakao / Coupang)
    "naver": "Naver Cloud Data Centres (Industrial Captive)",
    "네이버": "Naver Cloud Data Centres (Industrial Captive)",
    "kakao": "Kakao Data Centres (Industrial Captive)",
    "카카오": "Kakao Data Centres (Industrial Captive)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 8th enforcement — preserves Hangul jamo
    composition (초성+중성+종성) via NFC normalization + English
    legal-form variants (Ltd/Limited/Co.) + Hangul legal-form
    (주식회사 / ㈜) + trilingual script tolerance (Hangul / Latin
    RRK / Latin M-R / English acronyms) for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Hangul
    jamo composition preserved via NFC + lower-case lookup. Handles
    Hangul + Latin RRK + Latin M-R + English acronyms + Chaebol
    captives + KEPCO GENCOs per Convention #78 BINDING 8th
    enforcement (8th empirical test post-promotion).

    Korea is FIRST Asian Wave 3 country — expected HIGH alias hit
    count due to Hangul + Latin dual-script cohabitation on OSM
    (~100-200 hits projected). Establishes precedent for future
    Asian cohort onboardings (Japan Kanji + Hiragana + Katakana +
    Taiwan Traditional Chinese)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── KHNP nuclear-plant identity (Layer 1 name-based) ─────────────────────
# 6 KHNP nuclear plants — Kori/Hanbit/Hanul/Wolseong/Saeul + Shin-*
# prefix variants for newer units. Handled at Layer 1 in the
# region-jurisdiction resolver via name-substring match (case-
# insensitive, NFC-normalized, both Hangul and Romanized forms).
_KHNP_NUCLEAR_NAME_PATTERNS = [
    # Hangul forms
    "고리", "한빛", "한울", "월성", "새울",
    "신고리", "신한울", "신월성",
    # Legacy Hangul names (pre-2013 rename)
    "영광",   # Yonggwang → Hanbit (2013 rename)
    "울진",   # Ulchin → Hanul (2013 rename)
    # Latin (RRK + common) forms
    "kori", "hanbit", "hanul", "wolseong", "saeul",
    "shin-kori", "shin kori", "shinkori",
    "shin-hanul", "shin hanul", "shinhanul",
    "shin-wolseong", "shin wolseong", "shinwolseong",
    "yonggwang", "ulchin",
    # M-R variants
    "wŏlsŏng", "shin-kŏri",
]


def _is_khnp_nuclear(name: str | None) -> bool:
    """Return True if the substation name matches a KHNP nuclear-plant
    identity pattern (Layer 1 name-based attribution)."""
    if not name:
        return False
    n = _normalise_key(name)
    return any(pat in n for pat in _KHNP_NUCLEAR_NAME_PATTERNS)


# ── Industrial captive identity (Layer 2 name-based) ─────────────────────
_INDUSTRIAL_CAPTIVE_PATTERNS = {
    # Chaebol steel + semiconductor + petrochemical
    "포스코": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "posco": "POSCO Energy (Industrial Captive — Steel + LNG CHP)",
    "삼성전자": "Samsung Electronics self-gen (Industrial Captive — Semiconductor)",
    "samsung": "Samsung Electronics self-gen (Industrial Captive — Semiconductor)",
    "sk 하이닉스": "SK Hynix self-gen (Industrial Captive — Semiconductor)",
    "sk hynix": "SK Hynix self-gen (Industrial Captive — Semiconductor)",
    "현대": "Hyundai Green Power (Industrial Captive — Steel CHP)",
    "hyundai": "Hyundai Green Power (Industrial Captive — Steel CHP)",
    "lg 화학": "LG Chem self-gen (Industrial Captive — Petrochemical CHP)",
    "lg chem": "LG Chem self-gen (Industrial Captive — Petrochemical CHP)",
    # District heating
    "지역난방": "KDHC Korea District Heating Corporation (CHP)",
    "district heating": "KDHC Korea District Heating Corporation (CHP)",
    # Rail traction
    "코레일": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "korail": "KORAIL Korea Railroad Corporation (Rail Traction)",
    "ktx": "KORAIL Korea Railroad Corporation (KTX High-Speed Traction)",
}


def _detect_industrial_captive(name: str | None) -> str | None:
    """Return industrial captive owner if name matches a Layer 2 pattern.

    Handles POSCO/Samsung/SK Hynix/Hyundai/LG Chem self-generation +
    KDHC district-heating + KORAIL rail traction."""
    if not name:
        return None
    n = _normalise_key(name)
    for pattern, owner in _INDUSTRIAL_CAPTIVE_PATTERNS.items():
        if pattern in n:
            return owner
    return None


# ── First-tier admin → DSO map (all route to KEPCO) ──────────────────────
# Korea has 17 first-tier admin regions (do 도 provinces + si 시
# metropolitan cities). All route to KEPCO monopoly. Kept for
# forward-compat with future multi-DSO countries; empirically ~0
# hits expected (single-DSO simplification).
_ADMIN_TO_DSO = {
    # 8 do (province) — 도
    "gyeonggi": "KEPCO",       # 경기도
    "gyeongbuk": "KEPCO",      # 경상북도
    "gyeongnam": "KEPCO",      # 경상남도
    "chungbuk": "KEPCO",       # 충청북도
    "chungnam": "KEPCO",       # 충청남도
    "jeonbuk": "KEPCO",        # 전라북도
    "jeonnam": "KEPCO",        # 전라남도
    "gangwon": "KEPCO",        # 강원도
    "jeju": "KEPCO",           # 제주특별자치도
    # 8 si (metropolitan city) — 시
    "seoul": "KEPCO",          # 서울특별시
    "busan": "KEPCO",          # 부산광역시
    "daegu": "KEPCO",          # 대구광역시
    "incheon": "KEPCO",        # 인천광역시
    "gwangju": "KEPCO",        # 광주광역시
    "daejeon": "KEPCO",        # 대전광역시
    "ulsan": "KEPCO",          # 울산광역시
    "sejong": "KEPCO",         # 세종특별자치시
}


def resolve_owner_from_admin(admin_code: str | None) -> str | None:
    """Region-jurisdiction resolver via Korean first-tier admin code
    (do/si). Single-DSO simplification — every Korean admin region
    routes to KEPCO. Kept for forward-compat; empirically ~0 hits
    expected (KEPCO catch-all handles the same case)."""
    if not admin_code:
        return None
    return _ADMIN_TO_DSO.get(admin_code.strip().lower())


# ── KEPCO monopoly resolver (Layer 1-2-3-4 cascade) ──────────────────────
def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    lat: float,
    lon: float,
    admin_code: str | None = None,
    name: str | None = None,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Korea SIMPLIFIES the region-jurisdiction × voltage-class resolver
    to a 4-layer name-based cascade (KEPCO monopoly — no voltage-based
    unbundling like Ireland EirGrid ≥110 kV):

      Layer 1: KHNP nuclear-plant identity (name pattern match).
      Layer 2: Industrial captive identity (POSCO/Samsung/SK Hynix/
               Hyundai/LG Chem/KDHC/KORAIL name pattern match).
      Layer 3: Admin region → DSO map (empirically ~0 hits — all
               17 do/si route to KEPCO anyway).
      Layer 4: KEPCO catch-all default (monopoly).

    12th cohort-wide application of the region-jurisdiction resolver
    (after Belgium + Netherlands + Chile + Hungary + Slovenia +
    Colombia + Norway + Slovakia + Czechia + Iceland + Switzerland +
    Ireland — Korea).

    Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED — KEPCO
    monopoly covers all 17 do/si first-tier admin regions
    (Ireland/Greek/Costa Rica single-DSO precedent).
    """
    # Layer 1: KHNP nuclear-plant identity
    if _is_khnp_nuclear(name):
        return "KHNP", "region_jurisdiction_layer_1_KHNP_nuclear_name_match"

    # Layer 2: Industrial captive identity
    captive = _detect_industrial_captive(name)
    if captive:
        return captive, "region_jurisdiction_layer_2_industrial_captive_name_match"

    # Layer 3: Admin region → DSO (empirically ~0 hits — all route to KEPCO)
    if admin_code:
        dso = resolve_owner_from_admin(admin_code)
        if dso:
            return dso, f"region_jurisdiction_layer_3_{dso}_via_admin_{admin_code}"

    # Layer 4: KEPCO catch-all (monopoly default)
    return "KEPCO", "region_jurisdiction_layer_4_KEPCO_monopoly_default"


# ── Discipline #36 with Korea 5.0 km default tolerance ───────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Korea bounds filter with 5.0 km default tolerance.

    Per Iceland-analog precedent — Korea has ~4,400 islands +
    Ulleungdo + Dokdo + Marado + Jeju + Baengnyeongdo offshore
    offsets warranting 5.0 km tolerance (50× cadastral default).
    KR-ISOLATED grid means NO legitimate cross-border substations
    exist; tolerance purely absorbs coastline simplification +
    offshore island offsets. DMZ northern boundary (~38.3° N)
    pre-excluded via bounds.json 17-region South-Korea-only polygon."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "korea", module_fallback=5.0
        )
    return _apply_bounds_generic(
        records, country_slug="korea", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "korea/v4_23-ingestion-audit-korea-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = KOREA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("kr-"):
        slug = slug[len("kr-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-korea-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Korea ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/korea/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: korea",
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
        "  step_2_fetch: korea/v4_23-ingestion-audit-korea-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: korea/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    KOREA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return KOREA_CACHE_DIR / f"{key}{ext}"


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
    "KOREA_BOUNDS_JSON",
    "KOREA_TOLERANCE_JSON",
    "KOREA_DATA_DIR",
    "KOREA_CACHE_DIR",
]
