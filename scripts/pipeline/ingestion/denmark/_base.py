"""
SSI Pipeline — Denmark v4.23 ingestion, shared base layer.

Wave 3 Priority 28 (seventh Wave 3 country post-New Zealand;
Nordic offshore-wind-cohort multi-DSO architecture with Convention
#78 §4bis.5 Layer 3 6TH ENFORCEMENT at Copenhagen (København)
metropolitan Radius Elnet geofence). FIRST Nordic offshore wind
Wave 3 event.

⚡ CONVENTION #78 BINDING ENFORCEMENT — 🎉 DECADE MILESTONE 🎉 ⚡

Tenth country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive Danish + English + minimal German Schleswig
alias mapping REQUIRED at Step 3 connector authoring time:
  - Danish diacritics via NFC normalization (æ ø å)
  - Danish legal-form variants (A/S / ApS / AmbA / FmbA)
  - Predecessor rebrand cascades:
    * DONG Energy → Ørsted 2017 (5-year legacy)
    * SEAS-NVE → Andel/Cerius 2020 (4-year legacy)
    * Eltra + Elkraft System → Energinet 2005 (19-year legacy)
    * TRE-FOR → Trefor 2011 rebrand + EWII 2016 ownership change
    * Norlys Holding 2019 merger (NRGi + Nordvest + Verdo → N1)
  - Offshore wind generation-vs-distribution separation
    (Ørsted/Vattenfall own offshore wind BUT grid=Energinet TSO)

Denmark specifics:
  - Energinet Danmark A/S — state-owned single national TSO
    (Ministry of Climate, Energy and Utilities). Operates:
    * 400 kV EHV backbone (Cross-Sønderjylland Nord-Syd link +
      interconnectors)
    * 150 kV regional transmission (Zealand + Bornholm)
    * 132 kV regional transmission (Jutland historical tier)
    * 4 HVDC interconnectors — Skagerrak 4× (Norway) + Kontek
      (Germany) + Kriegers Flak (Germany + Sweden) + Öresund
      HVDC/AC (Sweden)
    * DK1 (Continental Europe synchronous) + DK2 (Nordic
      synchronous) bidding zones split at Great Belt
  - Radius Elnet A/S (Ørsted subsidiary since 2015) — Copenhagen +
    Frederiksberg + North Zealand + Bornholm metropolitan DSO.
    1.1M customers = 25% DK share. Convention #78 §4bis.5 6TH
    ENFORCEMENT via Copenhagen metropolitan lat/lon geofence.
  - Cerius A/S (Andel Group since 2020 SEAS-NVE rebrand) — Zealand
    central + south DSO. 400k customers = 9% DK share.
  - N1 A/S (Norlys Holding since 2019 merger) — North + Central
    Jutland DSO. 700k customers = 15% DK share. Formed via merger
    of NRGi + Nordvest Elforsyning + Verdo Randers + ELRO + Galten
    Elværk.
  - Trefor Elnet A/S (EWII since 2016 rebrand) — East Jutland +
    Fyn/Funen DSO. 350k customers = 8% DK share.
  - Banedanmark — rail traction infrastructure (25 kV AC —
    Copenhagen + Fredericia + Padborg to Germany electrified main
    lines).
  - Offshore wind operators (owns generation NOT grid):
    * Ørsted A/S — Horns Rev I+II+III + Anholt Havmøllepark 400 MW
      + Kriegers Flak 605 MW DK-side
    * Vattenfall Wind Denmark — Horns Rev III partial + Kriegers
      Flak partial
    * European Energy A/S — Danish renewable developer

Historical predecessors preserved for audit trail:
  - Eltra (1998-2005) — DK1 Jutland+Funen TSO pre-2005 merger
  - Elkraft System (1998-2005) — DK2 Zealand TSO pre-2005 merger
  - DONG Energy (2006-2017) → Ørsted 2017 rebrand (post-oil-gas
    divestment)
  - DONG Elnet + Københavns Energi (KE) → Radius Elnet 2015
  - SEAS-NVE (1999-2020) → Cerius A/S + Andel Energi 2020 rebrand
  - NRGi + Nordvest + Verdo + ELRO + Galten → N1 A/S 2019 merger
  - TRE-FOR (1913-2011) → Trefor 2011 rebrand + EWII 2016
    ownership
  - Municipal energy departments pre-1993 corporatization (Odense
    Energi + Aalborg Kommune Elektricitetsforsyning + København
    Energi + etc.)
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
DK_BOUNDS_JSON = REPO_ROOT / "denmark" / "bounds.json"
DK_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
DK_DATA_DIR = PIPELINE_DIR / "data" / "denmark"
DK_CACHE_DIR = DK_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 10th DECADE) ───────
_DNSP_ALIAS_MAP = {
    # ── Energinet A/S (TSO — single national) ────────────────────────────
    "energinet": "Energinet",
    "Energinet": "Energinet",
    "energinet a/s": "Energinet",
    "energinet.dk": "Energinet",
    "energinet danmark": "Energinet",
    "energinet denmark": "Energinet",
    "ENERGINET": "Energinet",
    # Predecessor: Eltra (1998-2005 DK1 Jutland+Funen TSO)
    "eltra": "Energinet-legacy (Eltra 1998-2005 DK1 pre-merger)",
    "eltra system": "Energinet-legacy (Eltra 1998-2005 DK1 pre-merger)",
    "eltra amba": "Energinet-legacy (Eltra 1998-2005 DK1 pre-merger)",
    # Predecessor: Elkraft System (1998-2005 DK2 Zealand TSO)
    "elkraft": "Energinet-legacy (Elkraft System 1998-2005 DK2 pre-merger)",
    "elkraft system": "Energinet-legacy (Elkraft System 1998-2005 DK2 pre-merger)",
    "elkraft system amba": "Energinet-legacy (Elkraft System 1998-2005 DK2 pre-merger)",

    # ── Radius Elnet A/S (Copenhagen + North Zealand + Bornholm) ─────────
    "radius": "Radius Elnet",
    "Radius": "Radius Elnet",
    "radius elnet": "Radius Elnet",
    "radius elnet a/s": "Radius Elnet",
    "radius elnet as": "Radius Elnet",
    "RADIUS": "Radius Elnet",
    # Predecessor: DONG Energy Distribution → Radius 2015
    "dong energy distribution": "Radius Elnet-legacy (DONG Energy pre-2015 rebrand)",
    "dong elnet": "Radius Elnet-legacy (DONG Energy pre-2015 rebrand)",
    "dong": "Radius Elnet-legacy (DONG Energy pre-2015 rebrand)",
    "dong energy": "Radius Elnet-legacy (DONG Energy pre-2015 rebrand)",
    "dong energy a/s": "Radius Elnet-legacy (DONG Energy pre-2015 rebrand)",
    # Predecessor: KE (Københavns Energi) merged to Radius 2015
    "ke": "Radius Elnet-legacy (Københavns Energi pre-2015 merger)",
    "københavns energi": "Radius Elnet-legacy (Københavns Energi pre-2015 merger)",
    "kobenhavns energi": "Radius Elnet-legacy (Københavns Energi pre-2015 merger)",
    "ke transmission": "Radius Elnet-legacy (KE Transmission pre-2015)",
    "copenhagen energy": "Radius Elnet-legacy (KE English variant pre-2015)",

    # ── Cerius A/S (Zealand central+south) ───────────────────────────────
    "cerius": "Cerius",
    "Cerius": "Cerius",
    "cerius a/s": "Cerius",
    "cerius as": "Cerius",
    # Predecessor: SEAS-NVE → Cerius 2020 rebrand
    "seas-nve": "Cerius-legacy (SEAS-NVE 1999-2020 pre-rebrand)",
    "seas nve": "Cerius-legacy (SEAS-NVE 1999-2020 pre-rebrand)",
    "seas": "Cerius-legacy (SEAS pre-1999 predecessor)",
    "nve": "Cerius-legacy (NVE Elnet pre-1999 predecessor)",
    "seas nve elnet": "Cerius-legacy (SEAS-NVE Elnet pre-2020 rebrand)",
    "seas-nve elnet": "Cerius-legacy (SEAS-NVE Elnet pre-2020 rebrand)",
    "seas nve as": "Cerius-legacy (SEAS-NVE A/S pre-2020 rebrand)",
    # Parent: Andel (post-2020 rebrand of SEAS-NVE + others)
    "andel": "Andel (Cerius parent — Zealand cooperative)",
    "andel energi": "Andel (Cerius parent — Zealand cooperative)",
    "andel a.m.b.a.": "Andel (Cerius parent — Zealand cooperative)",
    "andel amba": "Andel (Cerius parent — Zealand cooperative)",

    # ── N1 A/S (North + Central Jutland) ─────────────────────────────────
    "n1": "N1",
    "N1": "N1",
    "n1 a/s": "N1",
    "n1 as": "N1",
    "n1 elnet": "N1",
    "n1 netværk": "N1",
    "n1 network": "N1",
    # Parent: Norlys Holding (2019 merger)
    "norlys": "N1 (Norlys parent — 2019 merger)",
    "norlys holding": "N1 (Norlys parent — 2019 merger)",
    "norlys holding a/s": "N1 (Norlys parent — 2019 merger)",
    # Predecessors merged into N1 via Norlys 2019
    "nrgi": "N1-legacy (NRGi Elnet pre-2019 Norlys merger)",
    "nrgi elnet": "N1-legacy (NRGi Elnet pre-2019 Norlys merger)",
    "nrgi a.m.b.a.": "N1-legacy (NRGi amba pre-2019 Norlys merger)",
    "nrgi amba": "N1-legacy (NRGi amba pre-2019 Norlys merger)",
    "nordvest": "N1-legacy (Nordvest Elforsyning pre-2019 Norlys merger)",
    "nordvest elforsyning": "N1-legacy (Nordvest Elforsyning pre-2019 Norlys merger)",
    "verdo": "N1-legacy (Verdo Randers pre-2019 Norlys merger)",
    "verdo randers": "N1-legacy (Verdo Randers pre-2019 Norlys merger)",
    "verdo elnet": "N1-legacy (Verdo Randers pre-2019 Norlys merger)",
    "elro": "N1-legacy (ELRO pre-2019 Norlys merger)",
    "elro elnet": "N1-legacy (ELRO pre-2019 Norlys merger)",
    "galten elværk": "N1-legacy (Galten Elværk pre-2019 Norlys merger)",
    "galten elvaerk": "N1-legacy (Galten Elværk pre-2019 Norlys merger)",

    # ── Trefor Elnet A/S (East Jutland + Fyn/Funen) ──────────────────────
    "trefor": "Trefor",
    "Trefor": "Trefor",
    "trefor elnet": "Trefor",
    "trefor el-net": "Trefor",
    "TREFOR": "Trefor",
    "TREFOR El-net": "Trefor",
    "trefor elnet a/s": "Trefor",
    "trefor el-net a/s": "Trefor",
    "tre-for": "Trefor-legacy (TRE-FOR 1913-2011 pre-rebrand)",
    "tre-for elnet": "Trefor-legacy (TRE-FOR 1913-2011 pre-rebrand)",
    # Parent: EWII (European Water & Infrastructure Investments) since 2016
    "ewii": "Trefor (EWII parent since 2016 ownership)",
    "ewii a/s": "Trefor (EWII parent since 2016 ownership)",
    # Predecessor municipal utilities merged to TRE-FOR
    "fredericia kommune energi": "Trefor-legacy (Fredericia Kommune Energi pre-1993)",
    "kolding elforsyning": "Trefor-legacy (Kolding Elforsyning pre-1993)",

    # ── AURA El-net (Aarhus surroundings) ────────────────────────────────
    "aura": "AURA El-net",
    "AURA": "AURA El-net",
    "aura el-net": "AURA El-net",
    "aura el net": "AURA El-net",
    "aura elnet": "AURA El-net",
    "nrgi aarhus": "AURA El-net-legacy (NRGi Aarhus pre-rebrand)",
    "aura el": "AURA El-net",

    # ── Konstant Net (Silkeborg + Skanderborg minor DSO) ─────────────────
    "konstant": "Konstant Net",
    "konstant net": "Konstant Net",
    "konstant a/s": "Konstant Net",

    # ── Dinel A/S (Aarhus metropolitan) ──────────────────────────────────
    "dinel": "Dinel",
    "Dinel": "Dinel",
    "dinel a/s": "Dinel",
    "dinel as": "Dinel",

    # ── Banedanmark (rail traction 25 kV AC) ─────────────────────────────
    "banedanmark": "Banedanmark",
    "Banedanmark": "Banedanmark",
    "banedanmark a/s": "Banedanmark",
    "rail net denmark": "Banedanmark",
    # Predecessor: DSB Banedivision (pre-1997 unbundling)
    "dsb banedivision": "Banedanmark-legacy (DSB Banedivision pre-1997)",
    "dsb bane": "Banedanmark-legacy (DSB Banedivision pre-1997)",
    "dsb": "DSB (Danish State Railways — rail operator, not infrastructure)",
    "danske statsbaner": "DSB (Danish State Railways — rail operator, not infrastructure)",

    # ── Ørsted A/S (Offshore wind + former DSO owner — GENERATION NOT DSO) ──
    "ørsted": "Ørsted (Offshore Wind Generation — grid=Energinet)",
    "orsted": "Ørsted (Offshore Wind Generation — grid=Energinet)",
    "Ørsted": "Ørsted (Offshore Wind Generation — grid=Energinet)",
    "ørsted a/s": "Ørsted (Offshore Wind Generation — grid=Energinet)",
    "orsted a/s": "Ørsted (Offshore Wind Generation — grid=Energinet)",
    # Note: 'DONG Energy' aliases route to Radius Elnet-legacy above
    # (Radius was DONG Energy Distribution pre-2015). But NON-Radius
    # DONG offshore wind + generation goes to Ørsted (renamed 2017).

    # ── Vattenfall Wind Denmark (Offshore wind — GENERATION NOT DSO) ─────
    "vattenfall": "Vattenfall Wind Denmark (Offshore Wind Generation — grid=Energinet)",
    "vattenfall wind": "Vattenfall Wind Denmark (Offshore Wind Generation — grid=Energinet)",
    "vattenfall wind denmark": "Vattenfall Wind Denmark (Offshore Wind Generation — grid=Energinet)",
    "vattenfall vind": "Vattenfall Wind Denmark (Offshore Wind Generation — grid=Energinet)",
    "vattenfall a/s": "Vattenfall Wind Denmark (Offshore Wind Generation — grid=Energinet)",

    # ── European Energy A/S (Renewable developer — GENERATION NOT DSO) ───
    "european energy": "European Energy (Renewable Generation — grid=Energinet)",
    "european energy a/s": "European Energy (Renewable Generation — grid=Energinet)",

    # ── Nexel A/S (Zealand — Radius Elnet subsidiary structure) ──────────
    # Empirical: LARGEST unmapped cohort-wide event during Denmark P28 —
    # 4,909 subs = 61.6% of OSM fetch tagged "Nexel". Nexel is a Radius
    # Elnet subsidiary structure covering specific Zealand municipalities.
    # Per Denmark P28 closure YAML alias_map_extension_CRITICAL finding.
    "nexel": "Nexel (Radius Elnet subsidiary — Zealand)",
    "Nexel": "Nexel (Radius Elnet subsidiary — Zealand)",
    "nexel a/s": "Nexel (Radius Elnet subsidiary — Zealand)",
    "nexel as": "Nexel (Radius Elnet subsidiary — Zealand)",
    "NEXEL": "Nexel (Radius Elnet subsidiary — Zealand)",

    # ── Vores Elnet A/S (Fyn/Funen cooperative DSO) ──────────────────────
    # 105 subs empirical Denmark P28. Cooperative DSO on Fyn (Funen island)
    # distinct from Trefor Elnet coverage.
    "vores elnet": "Vores Elnet (Fyn cooperative DSO)",
    "Vores Elnet": "Vores Elnet (Fyn cooperative DSO)",
    "vores elnet a/s": "Vores Elnet (Fyn cooperative DSO)",
    "vores elnet as": "Vores Elnet (Fyn cooperative DSO)",
    "vores": "Vores Elnet (Fyn cooperative DSO)",

    # ── Flow Elnet A/S (Central Jutland — EnergiMidt 2020 rebrand) ───────
    # 45 subs Flow + 17 subs EnergiMidt legacy = 62 subs total (Silkeborg
    # + Herning + Skanderborg). EnergiMidt rebranded to Flow Elnet 2020.
    "flow elnet": "Flow Elnet (Central Jutland — Silkeborg/Herning)",
    "Flow Elnet": "Flow Elnet (Central Jutland — Silkeborg/Herning)",
    "flow elnet a/s": "Flow Elnet (Central Jutland — Silkeborg/Herning)",
    "flow elnet as": "Flow Elnet (Central Jutland — Silkeborg/Herning)",
    "flow": "Flow Elnet (Central Jutland — Silkeborg/Herning)",
    # Predecessor: EnergiMidt → Flow Elnet 2020 rebrand
    "energimidt": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",
    "EnergiMidt": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",
    "energimidt a/s": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",
    "energimidt as": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",
    "energi midt": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",
    "energi-midt": "Flow Elnet-legacy (EnergiMidt pre-2020 rebrand)",

    # ── Better Energy A/S + Stevning P/S (Renewable developer) ───────────
    # 144 subs empirical Denmark P28. Solar/wind renewable developer —
    # generation NOT DSO. Grid ownership routes back to relevant DSO
    # (Radius/Cerius/N1/Trefor depending on location).
    "better energy": "Better Energy (Renewable Generation — grid=DSO by location)",
    "better energy a/s": "Better Energy (Renewable Generation — grid=DSO by location)",
    "better energy as": "Better Energy (Renewable Generation — grid=DSO by location)",
    "stevning": "Better Energy (Stevning P/S subsidiary)",
    "stevning p/s": "Better Energy (Stevning P/S subsidiary)",
    "stevning ps": "Better Energy (Stevning P/S subsidiary)",

    # ── CPH (Copenhagen Airport — Industrial Captive) ────────────────────
    # 24 subs empirical Denmark P28. Copenhagen Airport (Københavns
    # Lufthavne A/S) industrial captive — airport infrastructure MV grid.
    "cph": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "CPH": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "københavns lufthavne": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "kobenhavns lufthavne": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "copenhagen airport": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "cph a/s": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",
    "kastrup lufthavn": "Copenhagen Airport (Industrial Captive — Aviation MV Grid)",

    # ── Industrial captives ──────────────────────────────────────────────
    "novo nordisk": "Novo Nordisk (Industrial Captive — Pharma CHP)",
    "novo nordisk a/s": "Novo Nordisk (Industrial Captive — Pharma CHP)",
    "arla": "Arla Foods (Industrial Captive — Dairy CHP)",
    "arla foods": "Arla Foods (Industrial Captive — Dairy CHP)",
    "arla foods amba": "Arla Foods (Industrial Captive — Dairy CHP)",
    "mærsk": "Mærsk (Industrial Captive — Nordsøolie historical)",
    "maersk": "Mærsk (Industrial Captive — Nordsøolie historical)",
    "a.p. moller maersk": "Mærsk (Industrial Captive — Nordsøolie historical)",
    "a.p. møller maersk": "Mærsk (Industrial Captive — Nordsøolie historical)",
    "grundfos": "Grundfos (Industrial Captive — Pump Manufacturing)",
    "lego": "LEGO Group (Industrial Captive — Billund Toy Manufacturing)",
    "lego group": "LEGO Group (Industrial Captive — Billund Toy Manufacturing)",
    "danish crown": "Danish Crown (Industrial Captive — Meat Processing)",
    "aalborg portland": "Aalborg Portland (Industrial Captive — Cement)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 10th DECADE MILESTONE — preserves Danish
    diacritic composition (æ ø å) via NFC normalization + Danish
    legal-form variants (A/S / ApS / AmbA / FmbA) + offshore-wind
    generation-vs-distribution separation flags for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Danish
    diacritic composition preserved via NFC + lower-case lookup.
    Handles Danish + English + minimal German Schleswig + offshore
    wind generation-retail separation (Ørsted/Vattenfall own offshore
    wind but grid ownership is Energinet TSO — a substation carrying
    an offshore-wind operator tag on the DK mainland/nearshore is
    likely legitimate generation, but transmission-tier subs remain
    Energinet) per Convention #78 BINDING 10th DECADE MILESTONE.

    Denmark is 10TH cohort-wide event — establishes Nordic offshore-
    wind cohort precedent for future Sweden/Finland Wave 3
    continuations."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Banedanmark rail traction identity (Layer 2 — 25 kV AC) ──────────────
_BANEDANMARK_NAME_PATTERNS = [
    "banedanmark", "dsb", "s-tog", "s-train", "kastrup", "øresund",
    "oresund", "rail", "traction", "jernbane",
]


def _is_banedanmark_traction(name: str | None, voltage_kv: float | None) -> bool:
    """Return True if the substation matches Banedanmark rail traction.

    25 kV AC electrified main lines (Copenhagen + Fredericia + Padborg
    to Germany)."""
    if not name:
        return False
    n = _normalise_key(name)
    if voltage_kv is not None and 24.0 <= voltage_kv <= 26.0:
        if any(pat in n for pat in _BANEDANMARK_NAME_PATTERNS):
            return True
    if "banedanmark" in n or "jernbane" in n:
        return True
    return False


# ── Offshore wind farm identity (Layer 3 — name-match) ───────────────────
_OFFSHORE_WIND_NAME_PATTERNS = {
    "horns rev": "Ørsted Horns Rev I/II/III (Offshore Wind — grid=Energinet)",
    "hornsrev": "Ørsted Horns Rev I/II/III (Offshore Wind — grid=Energinet)",
    "anholt": "Ørsted Anholt Havmøllepark (Offshore Wind 400 MW — grid=Energinet)",
    "anholt havmøllepark": "Ørsted Anholt Havmøllepark (Offshore Wind 400 MW — grid=Energinet)",
    "kriegers flak": "Kriegers Flak (Offshore Wind + Combined Grid Solution — grid=Energinet)",
    "vesterhav nord": "Vattenfall Vesterhav Nord (Offshore Wind — grid=Energinet)",
    "vesterhav syd": "Vattenfall Vesterhav Syd (Offshore Wind — grid=Energinet)",
    "rødsand": "Ørsted Rødsand (Offshore Wind — grid=Energinet)",
    "rodsand": "Ørsted Rødsand (Offshore Wind — grid=Energinet)",
    "nysted": "Ørsted Nysted (Offshore Wind — grid=Energinet)",
    "middelgrunden": "Middelgrunden (Offshore Wind Cooperative — grid=Energinet)",
    "avedøre": "Ørsted Avedøre (Onshore + Offshore Cluster — grid=Energinet)",
    "avedore": "Ørsted Avedøre (Onshore + Offshore Cluster — grid=Energinet)",
}


def _detect_offshore_wind(name: str | None) -> str | None:
    """Return offshore wind operator if name matches a Layer 3 pattern."""
    if not name:
        return None
    n = _normalise_key(name)
    for pattern, owner in _OFFSHORE_WIND_NAME_PATTERNS.items():
        if pattern in n:
            return owner
    return None


# ── Industrial captive detection (Layer 4 — Novo Nordisk + Arla + etc.) ──
_INDUSTRIAL_CAPTIVE_PATTERNS = {
    "novo nordisk": "Novo Nordisk (Industrial Captive — Pharma CHP)",
    "novo": "Novo Nordisk (Industrial Captive — Pharma CHP)",
    "arla": "Arla Foods (Industrial Captive — Dairy CHP)",
    "grundfos": "Grundfos (Industrial Captive — Pump Manufacturing)",
    "lego": "LEGO Group (Industrial Captive — Billund Toy Manufacturing)",
    "aalborg portland": "Aalborg Portland (Industrial Captive — Cement)",
    "danish crown": "Danish Crown (Industrial Captive — Meat Processing)",
    "mærsk": "Mærsk (Industrial Captive — Nordsøolie historical)",
    "maersk": "Mærsk (Industrial Captive — Nordsøolie historical)",
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


# ── Copenhagen §4bis.5 Layer 3 6TH ENFORCEMENT geofence ──────────────────
# Copenhagen (København) metropolitan Radius Elnet geofence — 6th cohort-
# wide §4bis.5 enforcement after:
#   1. Prague CZ (Czechia P20)
#   2. Warsaw PL (Poland P21)
#   3. EWZ Zurich CH (Switzerland P24)
#   4. SIG Geneva CH (Switzerland P24)
#   5. Auckland NZ (New Zealand P27)
#   6. NEW: Copenhagen DK (Denmark P28)

_RADIUS_COPENHAGEN_LAT_MIN = 55.55
_RADIUS_COPENHAGEN_LAT_MAX = 55.80
_RADIUS_COPENHAGEN_LON_MIN = 12.30
_RADIUS_COPENHAGEN_LON_MAX = 12.70


def _detect_copenhagen_dso(
    lat: float, lon: float, name: str | None
) -> tuple[str, str] | None:
    """Convention #78 §4bis.5 Layer 3 6TH ENFORCEMENT — Copenhagen
    metropolitan Radius Elnet geofence.

    Radius Elnet covers entire Hovedstaden region + Bornholm, so the
    geofence primarily confirms Copenhagen city core attribution vs
    generic Hovedstaden fallback. Returns (owner, provenance) if
    lat/lon matches Copenhagen metropolitan bbox; otherwise None
    (defers to Layer 5 Hovedstaden region → Radius fallback)."""
    if not (
        _RADIUS_COPENHAGEN_LAT_MIN <= lat <= _RADIUS_COPENHAGEN_LAT_MAX
        and _RADIUS_COPENHAGEN_LON_MIN <= lon <= _RADIUS_COPENHAGEN_LON_MAX
    ):
        return None

    return (
        "Radius Elnet",
        "region_jurisdiction_layer_3_4bis5_6th_enforcement_Radius_via_Copenhagen_geofence",
    )


# ── Region → dominant DSO map (5 admin regions × 4 major DSOs) ───────────
_REGION_TO_DOMINANT_DSO = {
    "hovedstaden": "Radius Elnet",       # Copenhagen + Frederiksberg + North Zealand + Bornholm
    "sjælland": "Cerius",                # Zealand central+south
    "sjaelland": "Cerius",               # ASCII variant
    "nordjylland": "N1",                 # North Jutland (Aalborg)
    "midtjylland": "N1",                 # Central Jutland (Aarhus)
    "syddanmark": "Trefor",              # South Jutland + Fyn/Funen
}


def resolve_owner_from_admin(admin_code: str | None) -> str | None:
    """Region-jurisdiction resolver via Danish 5-region admin code.

    5-region admin partition (post-2007 reform); each region resolves
    to dominant DSO. Hovedstaden requires Layer 3 §4bis.5 sub-cascade
    for Copenhagen metropolitan carve-out."""
    if not admin_code:
        return None
    key = _normalise_key(admin_code).strip()
    # Strip common region suffixes
    key = key.replace(" region", "").replace("region ", "").strip()
    return _REGION_TO_DOMINANT_DSO.get(key)


# ── Energinet TSO voltage threshold ──────────────────────────────────────
# Denmark unique voltage tier signature:
#   400 kV EHV backbone (Cross-Sønderjylland Nord-Syd + interconnectors)
#   150 kV regional transmission (Zealand + Bornholm historical)
#   132 kV regional transmission (Jutland historical)
#   60/50/30 kV Danish sub-transmission tiers
#   20/15/10 kV MV distribution
#
# Rule: ≥132 kV → Energinet TSO
_ENERGINET_TSO_MIN_KV = 132.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    lat: float,
    lon: float,
    admin_code: str | None = None,
    name: str | None = None,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Denmark 6-layer multi-DSO resolver (Nordic offshore-wind cohort):

      Layer 1: Energinet TSO threshold (≥132 kV → Energinet)
      Layer 2: Banedanmark rail traction (25 kV AC + name match)
      Layer 3a: Offshore wind farm (Horns Rev + Anholt + Kriegers Flak +
                Vesterhav + Rødsand + Nysted + Middelgrunden name match)
      Layer 3b: §4bis.5 Copenhagen metropolitan Radius geofence
                (6TH COHORT-WIDE ENFORCEMENT)
      Layer 4: Industrial captive (Novo Nordisk + Arla + Grundfos + LEGO +
               Aalborg Portland + Danish Crown + Mærsk)
      Layer 5: Region → dominant DSO map (5 regions × 4 major DSOs)
      Layer 6: Energinet catch-all (safety net)

    14th cohort-wide application of the region-jurisdiction resolver
    (after Belgium + Netherlands + Chile + Hungary + Slovenia + Colombia
    + Norway + Slovakia + Czechia + Iceland + Switzerland + Ireland +
    Korea + New Zealand — Denmark P28).

    Convention #78 §4bis.5 Layer 3 6TH ENFORCEMENT — Copenhagen
    metropolitan Radius Elnet geofence.
    """
    # Layer 1: Energinet TSO threshold
    if voltage_kv is not None and voltage_kv >= _ENERGINET_TSO_MIN_KV:
        return "Energinet", "region_jurisdiction_layer_1_Energinet_TSO_threshold_ge_132kv"

    # Layer 2: Banedanmark rail traction
    if _is_banedanmark_traction(name, voltage_kv):
        return "Banedanmark", "region_jurisdiction_layer_2_Banedanmark_25kv_AC_traction"

    # Layer 3a: Offshore wind farm (name-match)
    offshore = _detect_offshore_wind(name)
    if offshore:
        return offshore, "region_jurisdiction_layer_3a_offshore_wind_name_match"

    # Layer 3b: Copenhagen §4bis.5 geofence (6th cohort-wide enforcement)
    copenhagen_result = _detect_copenhagen_dso(lat, lon, name)
    if copenhagen_result:
        return copenhagen_result

    # Layer 4: Industrial captive
    captive = _detect_industrial_captive(name)
    if captive:
        return captive, "region_jurisdiction_layer_4_industrial_captive_name_match"

    # Layer 5: Region → dominant DSO map
    if admin_code:
        dso = resolve_owner_from_admin(admin_code)
        if dso:
            return dso, f"region_jurisdiction_layer_5_{dso.replace(' ', '_')}_via_admin_{_normalise_key(admin_code)}"

    # Layer 6: Energinet catch-all (safety net)
    return "Energinet", "region_jurisdiction_layer_6_Energinet_catch_all_default"


# ── Discipline #36 with Denmark 5.0 km default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Denmark bounds filter with 5.0 km default tolerance.

    Per existing DK entry from Mode 2 remediation — coastal storm
    surge exposure + offshore wind territorial waters allowance
    (Horns Rev + Anholt + Kriegers Flak platforms in Danish EEZ) +
    4 cross-border HVDC interconnectors (Skagerrak Norway + Kontek
    Germany + Kriegers Flak Germany + Öresund Sweden). Faroe Islands
    + Greenland pre-excluded via bounds.json (separate country entries
    in ssi-index)."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(DK_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("countries", {}).get("denmark", {}).get("boundary_tolerance_km", 5.0)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 5.0
    return _apply_bounds_generic(
        records, country_slug="denmark", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "denmark/v4_23-ingestion-audit-denmark-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = DK_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("dk-"):
        slug = slug[len("dk-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-denmark-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Denmark ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/denmark/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: denmark",
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
        "  step_2_fetch: denmark/v4_23-ingestion-audit-denmark-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: denmark/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    DK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return DK_CACHE_DIR / f"{key}{ext}"


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
    "DK_BOUNDS_JSON",
    "DK_TOLERANCE_JSON",
    "DK_DATA_DIR",
    "DK_CACHE_DIR",
]
