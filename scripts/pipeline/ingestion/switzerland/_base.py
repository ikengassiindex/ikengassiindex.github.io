"""
SSI Pipeline — Switzerland v4.23 ingestion, shared base layer.

Wave 3 Priority 24 (third Wave 3 country post-Iceland; architecturally
richest Wave 3 cohort country at 947 baseline subs). Region-jurisdiction
× voltage-class monopoly via Swissgrid AG federal TSO + 5 major
cantonal DSOs (Axpo Grid + BKW + CKW + Groupe E + Romande Energie) +
3 metropolitan carve-outs (EWZ Zürich + SIG Geneva + SIL Lausanne) +
~600 municipal DSOs via Layer 3 lat/lon geofence. 10th cohort-wide
application of region-jurisdiction fallback pattern (after Belgium +
Netherlands + Chile + Hungary + Slovenia + Colombia + Norway +
Slovakia + Czechia + Iceland).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 6th EMPIRICAL TEST ⚡

Sixth country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive multi-language multi-script alias mapping
REQUIRED at Step 3 connector authoring time:
  - German diacritics (ä ö ü ß + Swiss usage ß→ss)
  - French diacritics (à é è ê ï ô ù û)
  - Italian diacritics (à è ì ò ù)
  - Romansh (rare — <5% Graubünden — SA legal form + Rait/Electricitad)
  - Trilingual legal-form variants (AG German / SA French/Romansh /
    SpA Italian)
  - Comma-separated legal-form variants ("AG" with/without space
    + "s.a." lowercase variant)
  - Historical predecessor legacies:
    * NOK → Axpo Grid (2001 rebrand — 25-year legacy LARGEST)
    * Bernische Kraftwerke → BKW (2013 rebrand — 13-year)
    * EEF (Entreprises Électriques Fribourgeoises) → Groupe E (2006)
    * EOS (Énergie Ouest Suisse) → Romande Energie (2007)
    * Rätia Energie → Repower (2007)

Switzerland specifics:
  - Swissgrid AG — federal TSO (established 2006 via BFE unbundling
    per EU 3rd Package bilateral agreement; full asset transfer 2009).
    Operates 380/220 kV EHV backbone including 41 cross-border
    interconnections with DE + FR + IT + AT + LI. ~6,700 km
    transmission network. HIGHEST cross-border interconnector count
    cohort-wide.
  - Axpo Grid AG — LARGEST cantonal DSO in Deutschschweiz. Voltage:
    150/110 kV + 16/50 kV MV + 0.4 kV LV. Territory: Aargau + Zürich
    canton (excluding EWZ metropolitan area) + Schaffhausen +
    Thurgau + parts of Zug + Bern. ~15% national market.
    Predecessor: NOK (Nordostschweizerische Kraftwerke) — 2001
    rebrand (25-year legacy LARGEST expected — many OSM tags may
    retain legacy NOK). Parent: Axpo Holding AG (57% cantonal
    ownership).
  - BKW Energie AG — DSO. Voltage: 132 kV + MV + LV. Territory:
    Bern (canton) + Jura + parts of Neuchâtel + Solothurn + Freiburg.
    ~12% national market. Rebrand: Bernische Kraftwerke AG →
    BKW AG (2013 rebrand — 13-year legacy).
  - CKW (Centralschweizerische Kraftwerke) — DSO. Voltage: 110 kV +
    MV + LV. Territory: Zentralschweiz (Luzern + Nidwalden +
    Obwalden + Uri + Schwyz + parts of Aargau). ~8% national market.
    Established 1894 — NO rebrand (oldest continuously-operating
    Swiss DSO).
  - Groupe E SA — DSO (French-speaking region). Voltage: 132/60 kV
    + MV + LV. Territory: Fribourg + Neuchâtel + parts of Vaud +
    French-speaking Bern. ~10% national market. Rebrand: EEF
    (Entreprises Électriques Fribourgeoises) → Groupe E SA (2006).
  - Romande Energie SA — DSO (French-speaking region). Voltage:
    132/60 kV + MV + LV. Territory: Vaud + parts of Fribourg +
    Valais + Geneva outskirts (canton excluding SIG metropolitan
    area). ~10% national market. Rebrand: EOS (Énergie Ouest
    Suisse) → Romande Energie SA (2007).
  - EWZ (Elektrizitätswerk der Stadt Zürich) — MUNICIPAL DSO
    (Zürich Stadt city proper). Voltage: 110/50 kV + MV + LV.
    Territory: Zürich city administrative boundary (bbox 47.32-47.44
    lat, 8.45-8.62 lon). ~4% national market. Convention #78
    §4bis.5 Layer 3 geofence 3rd enforcement candidate (narrow
    metro carve-out analogous to Warsaw Innogy Stoen).
  - SIG (Services Industriels de Genève) — MUNICIPAL DSO
    (Genève canton). Voltage: 130/60 kV + MV + LV. Territory:
    Geneva metropolitan area (bbox 46.15-46.28 lat, 6.05-6.20 lon).
    ~4% national market. Convention #78 §4bis.5 Layer 3 geofence
    4th enforcement candidate.
  - SIL (Services Industriels de Lausanne) — MUNICIPAL DSO
    (Lausanne city proper). Voltage: 60 kV + MV + LV. Territory:
    Lausanne administrative boundary (bbox 46.51-46.55 lat,
    6.58-6.68 lon). ~2% national market. Convention #78 §4bis.5
    Layer 3 geofence 5th enforcement candidate (smaller carve-out).
  - AET (Azienda Elettrica Ticinese) — Italian-language DSO.
    Voltage: 150/50 kV + MV + LV. Territory: Ticino (Italian-
    speaking canton). ~3% national market. Established 1958.
  - Repower AG — DSO (Graubünden multi-language canton). Voltage:
    132/60 kV + MV + LV. Territory: Graubünden. ~2% national
    market. Rebrand: Rätia Energie AG → Repower AG (2007).
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
SWITZERLAND_BOUNDS_JSON = REPO_ROOT / "switzerland" / "bounds.json"
SWITZERLAND_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
SWITZERLAND_DATA_DIR = PIPELINE_DIR / "data" / "switzerland"
SWITZERLAND_CACHE_DIR = SWITZERLAND_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 6th enforcement) ───
# Preemptive 4-language multi-script mapping: German (ä ö ü ß) + French
# (à é è ê ï ô ù û) + Italian (à è ì ò ù) + Romansh + trilingual
# legal-form variants (AG/SA/SpA) + predecessor rebrands
_DNSP_ALIAS_MAP = {
    # ── Swissgrid (TSO) — trilingual variants ─────────────────────────
    "swissgrid": "Swissgrid",
    "swissgrid ag": "Swissgrid",                # German legal form
    "swissgrid ag.": "Swissgrid",
    "swissgrid sa": "Swissgrid",                # French legal form
    "swissgrid s.a.": "Swissgrid",
    "swissgrid spa": "Swissgrid",               # Italian legal form
    "swissgrid s.p.a.": "Swissgrid",
    "swissgrid grid": "Swissgrid",
    "swissgrid transmission": "Swissgrid",

    # ── Axpo Grid variants (LARGEST Deutschschweiz DSO) ───────────────
    "axpo": "Axpo Grid",                        # Ambiguous — Axpo Holding vs Axpo Grid
    "axpo ag": "Axpo Grid",
    "axpo grid": "Axpo Grid",
    "axpo grid ag": "Axpo Grid",
    "axpo grid ag.": "Axpo Grid",
    "axpo holding": "Axpo Grid (Holding — parent)",
    "axpo holding ag": "Axpo Grid (Holding — parent)",
    "axpo solutions": "Axpo Solutions (Generation subsidiary)",
    "axpo solutions ag": "Axpo Solutions (Generation subsidiary)",
    # NOK predecessor — 25-year legacy LARGEST
    "nok": "Axpo Grid-legacy (NOK Nordostschweizerische Kraftwerke pre-2001 rebrand)",
    "nordostschweizerische kraftwerke": "Axpo Grid-legacy (NOK pre-2001 rebrand)",
    "nordostschweizerische kraftwerke ag": "Axpo Grid-legacy (NOK pre-2001 rebrand)",
    "n.o.k.": "Axpo Grid-legacy (NOK pre-2001 rebrand)",

    # ── BKW variants (Bern DSO) ────────────────────────────────────────
    "bkw": "BKW",
    "bkw ag": "BKW",
    "bkw energie": "BKW",
    "bkw energie ag": "BKW",
    "bkw netzservice": "BKW",
    "bkw netzservice ag": "BKW",
    # Predecessor: Bernische Kraftwerke → BKW (2013 rebrand)
    "bernische kraftwerke": "BKW-legacy (Bernische Kraftwerke pre-2013 rebrand)",
    "bernische kraftwerke ag": "BKW-legacy (Bernische Kraftwerke pre-2013 rebrand)",
    "bernische kraftwerke fmb": "BKW-legacy (Bernische Kraftwerke FMB pre-2013 rebrand)",
    "bkw fmb": "BKW-legacy (BKW FMB pre-2013 rebrand)",
    "bkw fmb energie": "BKW-legacy (BKW FMB pre-2013 rebrand)",
    "bkw fmb energie ag": "BKW-legacy (BKW FMB pre-2013 rebrand)",

    # ── CKW variants (Zentralschweiz DSO) ──────────────────────────────
    "ckw": "CKW",
    "ckw ag": "CKW",
    "ckw ag.": "CKW",
    "centralschweizerische kraftwerke": "CKW",
    "centralschweizerische kraftwerke ag": "CKW",
    "c.k.w.": "CKW",

    # ── Groupe E variants (French-speaking region DSO) ─────────────────
    "groupe e": "Groupe E",
    "groupe e sa": "Groupe E",
    "groupe e s.a.": "Groupe E",                # Lowercase
    "groupe-e": "Groupe E",                     # Hyphenated
    "groupe-e sa": "Groupe E",
    "group e": "Groupe E",                      # Common typo
    "groupe é": "Groupe E",                     # With É accent
    # Predecessor: EEF → Groupe E (2006 rebrand)
    "eef": "Groupe E-legacy (EEF Entreprises Électriques Fribourgeoises pre-2006 rebrand)",
    "entreprises électriques fribourgeoises": "Groupe E-legacy (EEF pre-2006 rebrand)",
    "entreprises electriques fribourgeoises": "Groupe E-legacy (EEF pre-2006 rebrand)",
    "entreprises électriques fribourgeoises sa": "Groupe E-legacy (EEF pre-2006 rebrand)",
    "entreprises electriques fribourgeoises sa": "Groupe E-legacy (EEF pre-2006 rebrand)",
    "e.e.f.": "Groupe E-legacy (EEF pre-2006 rebrand)",

    # ── Romande Energie variants (Vaud/Valais DSO) ─────────────────────
    "romande energie": "Romande Energie",
    "romande energie sa": "Romande Energie",
    "romande energie s.a.": "Romande Energie",
    "romande énergie": "Romande Energie",       # With accent
    "romande énergie sa": "Romande Energie",
    "romande-energie": "Romande Energie",       # Hyphenated
    # Predecessor: EOS → Romande Energie (2007 rebrand)
    "eos": "Romande Energie-legacy (EOS Énergie Ouest Suisse pre-2007 rebrand)",
    "energie ouest suisse": "Romande Energie-legacy (EOS pre-2007 rebrand)",
    "énergie ouest suisse": "Romande Energie-legacy (EOS pre-2007 rebrand)",
    "energie ouest suisse sa": "Romande Energie-legacy (EOS pre-2007 rebrand)",
    "énergie ouest suisse sa": "Romande Energie-legacy (EOS pre-2007 rebrand)",
    "e.o.s.": "Romande Energie-legacy (EOS pre-2007 rebrand)",

    # ── EWZ variants (Zürich MUNICIPAL DSO — metro carve-out) ──────────
    "ewz": "EWZ",
    "ewz zürich": "EWZ",
    "ewz zurich": "EWZ",                        # ASCII variant
    "elektrizitätswerk der stadt zürich": "EWZ",
    "elektrizitatswerk der stadt zurich": "EWZ",
    "elektrizitätswerk zürich": "EWZ",
    "elektrizitätswerke der stadt zürich": "EWZ",
    "elektrizitätswerke zürich": "EWZ",
    "stadt zürich elektrizitätswerk": "EWZ",

    # ── SIG variants (Geneva MUNICIPAL DSO — metro carve-out) ──────────
    "sig": "SIG",
    "sig genève": "SIG",
    "sig geneve": "SIG",                        # ASCII variant
    "services industriels de genève": "SIG",
    "services industriels de geneve": "SIG",
    "services industriels genève": "SIG",
    "services industriels geneve": "SIG",
    "s.i.g.": "SIG",

    # ── SIL variants (Lausanne MUNICIPAL DSO — metro carve-out) ────────
    "sil": "SIL",
    "sil lausanne": "SIL",
    "services industriels de lausanne": "SIL",
    "services industriels lausanne": "SIL",
    "s.i.l.": "SIL",
    "lausanne si": "SIL",

    # ── AET variants (Ticino Italian-language DSO) ─────────────────────
    "aet": "AET",
    "aet sa": "AET",
    "aet spa": "AET",                           # Italian legal form
    "aet s.p.a.": "AET",
    "azienda elettrica ticinese": "AET",
    "azienda elettrica ticinese sa": "AET",
    "azienda elettrica ticinese spa": "AET",

    # ── Repower variants (Graubünden multi-language DSO) ───────────────
    "repower": "Repower",
    "repower ag": "Repower",
    "repower sa": "Repower",                    # Italian territory
    # Predecessor: Rätia Energie → Repower (2007 rebrand)
    "rätia energie": "Repower-legacy (Rätia Energie pre-2007 rebrand)",
    "ratia energie": "Repower-legacy (Rätia Energie pre-2007 rebrand)",
    "rätia energie ag": "Repower-legacy (Rätia Energie pre-2007 rebrand)",
    "ratia energie ag": "Repower-legacy (Rätia Energie pre-2007 rebrand)",

    # ── Alpiq (Generation subsidiary — should NOT tag substations) ─────
    "alpiq": "Alpiq (Generation — Related Entity)",
    "alpiq ag": "Alpiq (Generation — Related Entity)",
    "alpiq holding": "Alpiq (Generation — Related Entity)",
    "alpiq holding ag": "Alpiq (Generation — Related Entity)",

    # ── SBB / CFF / FFS — Swiss Federal Railways trilingual ────────────
    "sbb": "Swiss Federal Railways (SBB/CFF/FFS — Electric Traction)",
    "sbb ag": "Swiss Federal Railways (SBB/CFF/FFS — Electric Traction)",
    "sbb cff ffs": "Swiss Federal Railways (SBB/CFF/FFS — Electric Traction)",
    "schweizerische bundesbahnen": "Swiss Federal Railways (SBB — Electric Traction)",
    "cff": "Swiss Federal Railways (CFF — Electric Traction)",
    "cff sa": "Swiss Federal Railways (CFF — Electric Traction)",
    "chemins de fer fédéraux": "Swiss Federal Railways (CFF — Electric Traction)",
    "chemins de fer federaux": "Swiss Federal Railways (CFF — Electric Traction)",
    "chemins de fer fédéraux suisses": "Swiss Federal Railways (CFF — Electric Traction)",
    "ffs": "Swiss Federal Railways (FFS — Electric Traction)",
    "ffs spa": "Swiss Federal Railways (FFS — Electric Traction)",
    "ferrovie federali svizzere": "Swiss Federal Railways (FFS — Electric Traction)",

    # ── Nuclear plants (dedicated tags) ─────────────────────────────────
    "kkg": "Kernkraftwerk Gösgen (Nuclear Plant)",
    "kernkraftwerk gösgen": "Kernkraftwerk Gösgen (Nuclear Plant)",
    "kernkraftwerk gosgen": "Kernkraftwerk Gösgen (Nuclear Plant)",
    "kkl": "Kernkraftwerk Leibstadt (Nuclear Plant)",
    "kernkraftwerk leibstadt": "Kernkraftwerk Leibstadt (Nuclear Plant)",
    "kkb": "Kernkraftwerk Beznau (Nuclear Plant)",
    "kernkraftwerk beznau": "Kernkraftwerk Beznau (Nuclear Plant)",
    "kernkraftwerk mühleberg": "Kernkraftwerk Mühleberg (Decommissioned Nuclear)",
    "kernkraftwerk muhleberg": "Kernkraftwerk Mühleberg (Decommissioned Nuclear)",

    # ── Industrial captives + research campuses ────────────────────────
    "cern": "CERN (Research Campus — Geneva)",
    "cern lhc": "CERN (Research Campus — Geneva)",
    "cern hl-lhc": "CERN (Research Campus — Geneva)",
    "epfl": "EPFL (Campus — Lausanne)",
    "ecole polytechnique fédérale": "EPFL (Campus — Lausanne)",
    "ecole polytechnique federale": "EPFL (Campus — Lausanne)",
    "eth": "ETH Zürich (Campus — Zürich)",
    "eth zürich": "ETH Zürich (Campus — Zürich)",
    "eth zurich": "ETH Zürich (Campus — Zürich)",
    "eth zürich campus": "ETH Zürich (Campus — Zürich)",
    "roche": "Roche (Industrial Captive — Basel-Stadt)",
    "roche ag": "Roche (Industrial Captive — Basel-Stadt)",
    "hoffmann-la roche": "Roche (Industrial Captive — Basel-Stadt)",
    "novartis": "Novartis (Industrial Captive — Basel-Stadt)",
    "novartis ag": "Novartis (Industrial Captive — Basel-Stadt)",

    # ── Municipal DSO placeholders (top-10 non-metro) ──────────────────
    "iwb": "IWB (Industrielle Werke Basel — Municipal DSO)",
    "industrielle werke basel": "IWB (Industrielle Werke Basel — Municipal DSO)",
    "iwb basel": "IWB (Industrielle Werke Basel — Municipal DSO)",
    "ebl": "EBL (Elektra Baselland — Municipal DSO)",
    "elektra baselland": "EBL (Elektra Baselland — Municipal DSO)",
    "sig winterthur": "Stadtwerk Winterthur (Municipal DSO)",
    "stadtwerk winterthur": "Stadtwerk Winterthur (Municipal DSO)",
    "ewb": "EWB (Energie Wasser Bern — Municipal DSO)",
    "energie wasser bern": "EWB (Energie Wasser Bern — Municipal DSO)",
    "wwz": "WWZ (Wasserwerke Zug — Municipal DSO)",
    "wasserwerke zug": "WWZ (Wasserwerke Zug — Municipal DSO)",

    # ── Swiss typographic-quote variants (Latvia/Czechia precedent) ────
    # Swiss uses « ... » (French guillemets) + „ ... " (German)
    'as "swissgrid"': "Swissgrid",
    'as «swissgrid»': "Swissgrid",
    'as „swissgrid"': "Swissgrid",
    'as "axpo grid"': "Axpo Grid",
    'as «axpo grid»': "Axpo Grid",
    'as "bkw"': "BKW",
    'as «bkw»': "BKW",
    'as "ckw"': "CKW",
    'as "groupe e"': "Groupe E",
    'as «groupe e»': "Groupe E",
    'as "romande energie"': "Romande Energie",
    'as «romande energie»': "Romande Energie",
    'as "ewz"': "EWZ",
    'as "sig"': "SIG",
    'as «sig»': "SIG",
    'as "sil"': "SIL",
    'as "aet"': "AET",
    'as "repower"': "Repower",
    'as "nok"': "Axpo Grid-legacy (NOK pre-2001 rebrand)",
    'as "eos"': "Romande Energie-legacy (EOS pre-2007 rebrand)",
    'as "eef"': "Groupe E-legacy (EEF pre-2006 rebrand)",
    'as "bernische kraftwerke"': "BKW-legacy (Bernische Kraftwerke pre-2013 rebrand)",
    'as "rätia energie"': "Repower-legacy (Rätia Energie pre-2007 rebrand)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 6th enforcement — preserves 4-language NFC
    diacritics (German ä ö ü ß + French à é è ê ï ô ù û + Italian
    à è ì ò ù + Romansh) + typographic quotes (« ... » French +
    „ ... " German) + trilingual legal-form variants (AG/SA/SpA)
    for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with 4-language
    Swiss diacritics preserved in input, normalised via NFC + lower-case
    lookup. Handles typographic-quote variants + trilingual legal-form
    (AG/SA/SpA) + predecessor rebrand cascades per Convention #78
    BINDING 6th enforcement (6th empirical test post-promotion).

    Swiss 4-language script cohabitation is 🆕 NEW cohort-wide alias
    class — first Wave 3 4-language country. Predecessor rebrand
    classes: NOK → Axpo Grid (2001 — 25-year LARGEST legacy) +
    Bernische Kraftwerke → BKW (2013) + EEF → Groupe E (2006) +
    EOS → Romande Energie (2007) + Rätia Energie → Repower (2007)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 to DSO map (26 Swiss cantons) ─────────────────────────────────
# Switzerland OSM likely does NOT populate ref:nuts:3 tags on substations
# (Wave 2/3 empirical precedent). Forward-compat surface below; actual
# attribution flows via Layer 3 geofence with 3 metro carve-outs.
# Swiss NUTS-3 = 26 cantons.
_NUTS3_TO_DSO = {
    # Deutschschweiz — Axpo Grid dominant
    "CH040": "Axpo Grid",              # Zürich (canton, excluding EWZ metro)
    "CH033": "Axpo Grid",              # Aargau
    "CH052": "Axpo Grid",              # Schaffhausen
    "CH057": "Axpo Grid",              # Thurgau
    "CH066": "Axpo Grid",              # Zug (partial)
    # Bern + Jura → BKW
    "CH021": "BKW",                    # Bern
    "CH025": "BKW",                    # Jura
    "CH024": "BKW",                    # Solothurn
    # Zentralschweiz — CKW
    "CH061": "CKW",                    # Luzern
    "CH062": "CKW",                    # Uri
    "CH063": "CKW",                    # Schwyz
    "CH064": "CKW",                    # Obwalden
    "CH065": "CKW",                    # Nidwalden
    # Nordwestschweiz — mixed IWB + Axpo
    "CH031": "IWB (Industrielle Werke Basel — Municipal DSO)",  # Basel-Stadt
    "CH032": "EBL (Elektra Baselland — Municipal DSO)",         # Basel-Landschaft
    # Ostschweiz — mixed
    "CH055": "Axpo Grid",              # St. Gallen
    "CH051": "Axpo Grid",              # Glarus
    "CH053": "Axpo Grid",              # Appenzell IR
    "CH054": "Axpo Grid",              # Appenzell AR
    "CH056": "Repower",                # Graubünden
    # French-speaking region — Groupe E + Romande Energie split
    "CH022": "Groupe E",               # Fribourg
    "CH023": "Groupe E",               # Neuchâtel (partial)
    "CH011": "Romande Energie",        # Vaud (excluding Lausanne SIL metro + Geneva SIG metro)
    "CH013": "Romande Energie",        # Valais
    "CH012": "SIG",                    # Genève (canton — SIG metro dominant)
    # Ticino — AET
    "CH070": "AET",                    # Ticino
}


def resolve_owner_from_nuts3(nuts3_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NUTS-3 code (Swiss canton)."""
    if not nuts3_code:
        return None
    return _NUTS3_TO_DSO.get(nuts3_code.strip().upper())


# ── Layer 3 lat/lon geofence (3-metro carve-out + 8-way cantonal) ───────
# Switzerland OSM does not populate ref:nuts:3 tags on substations
# (empirical hypothesis — Wave 2/3 cumulative precedent). Add lat/lon
# geofence for DSO attribution.
#
# Swiss territorial partition — 8-way (5 major DSOs + 3 metro carve-outs):
#   Layer 3a: EWZ Zürich metro (city administrative bbox)
#   Layer 3b: SIG Geneva metro (canton bbox)
#   Layer 3c: SIL Lausanne metro (city administrative bbox)
#   Layer 3d: Axpo Grid Deutschschweiz territories
#   Layer 3e: BKW Bern + Jura territories
#   Layer 3f: CKW Zentralschweiz territories
#   Layer 3g: Groupe E Fribourg + Neuchâtel territories
#   Layer 3h: Romande Energie Vaud + Valais territories
#   Layer 3i: AET Ticino
#   Layer 3j: Repower Graubünden
#   Layer 3k: IWB Basel-Stadt + EBL Basel-Landschaft
#   Layer 3z: Axpo Grid default catch-all Deutschschweiz
#   Swissgrid (TSO — only via voltage threshold Layer 1 ≥220 kV)
#
# Switzerland bounds: 45.82 <= lat <= 47.81, 5.96 <= lon <= 10.49

# EWZ Zürich Stadt metro bbox (Convention #78 §4bis.5 candidate)
_EWZ_ZURICH_LAT_MIN = 47.32
_EWZ_ZURICH_LAT_MAX = 47.44
_EWZ_ZURICH_LON_MIN = 8.45
_EWZ_ZURICH_LON_MAX = 8.62

# SIG Geneva metro bbox (Convention #78 §4bis.5 candidate)
_SIG_GENEVA_LAT_MIN = 46.15
_SIG_GENEVA_LAT_MAX = 46.28
_SIG_GENEVA_LON_MIN = 6.05
_SIG_GENEVA_LON_MAX = 6.20

# SIL Lausanne metro bbox (Convention #78 §4bis.5 candidate)
_SIL_LAUSANNE_LAT_MIN = 46.51
_SIL_LAUSANNE_LAT_MAX = 46.55
_SIL_LAUSANNE_LON_MIN = 6.58
_SIL_LAUSANNE_LON_MAX = 6.68

# IWB Basel-Stadt metro bbox
_IWB_BASEL_LAT_MIN = 47.52
_IWB_BASEL_LAT_MAX = 47.60
_IWB_BASEL_LON_MIN = 7.55
_IWB_BASEL_LON_MAX = 7.65

# Ticino (AET) — full canton bbox
_AET_TICINO_LAT_MIN = 45.82
_AET_TICINO_LAT_MAX = 46.55
_AET_TICINO_LON_MIN = 8.42
_AET_TICINO_LON_MAX = 9.28

# Graubünden (Repower) — full canton bbox
_REPOWER_GR_LAT_MIN = 46.15
_REPOWER_GR_LAT_MAX = 47.07
_REPOWER_GR_LON_MIN = 8.65
_REPOWER_GR_LON_MAX = 10.49

# Genève canton (SIG catchment beyond metro)
_SIG_GENEVA_CANTON_LAT_MIN = 46.13
_SIG_GENEVA_CANTON_LAT_MAX = 46.38
_SIG_GENEVA_CANTON_LON_MIN = 5.96
_SIG_GENEVA_CANTON_LON_MAX = 6.32

# Vaud + Valais (Romande Energie) — approximate combined bbox
_ROMANDE_VD_VS_LAT_MIN = 46.13
_ROMANDE_VD_VS_LAT_MAX = 46.90
_ROMANDE_VD_VS_LON_MIN = 6.05
_ROMANDE_VD_VS_LON_MAX = 8.15

# Fribourg + Neuchâtel (Groupe E) — approximate combined bbox
_GROUPE_E_FR_NE_LAT_MIN = 46.55
_GROUPE_E_FR_NE_LAT_MAX = 47.17
_GROUPE_E_FR_NE_LON_MIN = 6.70
_GROUPE_E_FR_NE_LON_MAX = 7.30

# Zentralschweiz (CKW) — Luzern/Uri/Schwyz/Obwalden/Nidwalden approximate
_CKW_LAT_MIN = 46.55
_CKW_LAT_MAX = 47.30
_CKW_LON_MIN = 7.85
_CKW_LON_MAX = 8.85

# Bern + Jura (BKW) — approximate combined bbox
# NOTE: BKW eastern boundary set at 7.95 to exclude Aargau canton
# (Axpo Grid territory starts ~8.00 at Erlinsbach; Aarau at 8.31).
# Solothurn eastern edge (Aarburg/Olten) at ~7.90 preserved.
_BKW_LAT_MIN = 46.40
_BKW_LAT_MAX = 47.51
_BKW_LON_MIN = 6.85
_BKW_LON_MAX = 7.95

# Switzerland national bounds sanity check
_CH_LAT_MIN = 45.82
_CH_LAT_MAX = 47.81
_CH_LON_MIN = 5.96
_CH_LON_MAX = 10.49


def resolve_owner_from_lat_lon_geofence(lat: float, lon: float) -> str | None:
    """Swiss 8-way DSO territorial partition via 3-metro carve-out +
    5-cantonal-major + 2-language-region composition.

    Wave 2/3 cumulative precedent (Slovenia P12 + Slovakia P19 + Czechia
    P20 + Poland P21 + Greece P22 + Iceland P23) — apply when OSM does
    not populate NUTS-3 tags. Convention #78 BINDING 6th enforcement
    Layer 3 geofence sub-convention with FIRST cohort-wide MULTI-METRO
    carve-out pattern (3 metros vs Warsaw's single-metro precedent).

    Switzerland empirically EXTENDS the sub-convention from Iceland's
    5-way multi-DSO territorial partition to 8-way multi-metro +
    multi-cantonal composition:
      Layer 3a: EWZ Zürich Stadt metro bbox (city admin)
      Layer 3b: SIG Geneva metro bbox (city core)
      Layer 3c: SIL Lausanne metro bbox (city admin)
      Layer 3d: IWB Basel-Stadt metro bbox
      Layer 3e: AET Ticino canton bbox
      Layer 3f: Repower Graubünden canton bbox
      Layer 3g: SIG Genève canton bbox (broader than metro)
      Layer 3h: Groupe E Fribourg + Neuchâtel bbox
      Layer 3i: Romande Energie Vaud + Valais bbox
      Layer 3j: CKW Zentralschweiz bbox
      Layer 3k: BKW Bern + Jura bbox
      Layer 3z: Axpo Grid Deutschschweiz default catch-all

    Returns DSO code or None if lat/lon outside Swiss bounds.
    """
    # Sanity check — within Switzerland bounds
    if not (_CH_LAT_MIN <= lat <= _CH_LAT_MAX and _CH_LON_MIN <= lon <= _CH_LON_MAX):
        return None

    # Layer 3a: EWZ Zürich Stadt metro (checked first — smallest metro carve-out)
    if (_EWZ_ZURICH_LAT_MIN <= lat <= _EWZ_ZURICH_LAT_MAX
            and _EWZ_ZURICH_LON_MIN <= lon <= _EWZ_ZURICH_LON_MAX):
        return "EWZ"

    # Layer 3b: SIG Geneva metro (city core)
    if (_SIG_GENEVA_LAT_MIN <= lat <= _SIG_GENEVA_LAT_MAX
            and _SIG_GENEVA_LON_MIN <= lon <= _SIG_GENEVA_LON_MAX):
        return "SIG"

    # Layer 3c: SIL Lausanne metro
    if (_SIL_LAUSANNE_LAT_MIN <= lat <= _SIL_LAUSANNE_LAT_MAX
            and _SIL_LAUSANNE_LON_MIN <= lon <= _SIL_LAUSANNE_LON_MAX):
        return "SIL"

    # Layer 3d: IWB Basel-Stadt metro
    if (_IWB_BASEL_LAT_MIN <= lat <= _IWB_BASEL_LAT_MAX
            and _IWB_BASEL_LON_MIN <= lon <= _IWB_BASEL_LON_MAX):
        return "IWB (Industrielle Werke Basel — Municipal DSO)"

    # Layer 3e: AET Ticino canton
    if (_AET_TICINO_LAT_MIN <= lat <= _AET_TICINO_LAT_MAX
            and _AET_TICINO_LON_MIN <= lon <= _AET_TICINO_LON_MAX):
        return "AET"

    # Layer 3f: Repower Graubünden canton
    if (_REPOWER_GR_LAT_MIN <= lat <= _REPOWER_GR_LAT_MAX
            and _REPOWER_GR_LON_MIN <= lon <= _REPOWER_GR_LON_MAX):
        return "Repower"

    # Layer 3g: SIG Genève canton (broader catchment)
    if (_SIG_GENEVA_CANTON_LAT_MIN <= lat <= _SIG_GENEVA_CANTON_LAT_MAX
            and _SIG_GENEVA_CANTON_LON_MIN <= lon <= _SIG_GENEVA_CANTON_LON_MAX):
        return "SIG"

    # Layer 3h: Groupe E Fribourg + Neuchâtel
    if (_GROUPE_E_FR_NE_LAT_MIN <= lat <= _GROUPE_E_FR_NE_LAT_MAX
            and _GROUPE_E_FR_NE_LON_MIN <= lon <= _GROUPE_E_FR_NE_LON_MAX):
        return "Groupe E"

    # Layer 3i: Romande Energie Vaud + Valais
    if (_ROMANDE_VD_VS_LAT_MIN <= lat <= _ROMANDE_VD_VS_LAT_MAX
            and _ROMANDE_VD_VS_LON_MIN <= lon <= _ROMANDE_VD_VS_LON_MAX):
        return "Romande Energie"

    # Layer 3j: CKW Zentralschweiz
    if (_CKW_LAT_MIN <= lat <= _CKW_LAT_MAX
            and _CKW_LON_MIN <= lon <= _CKW_LON_MAX):
        return "CKW"

    # Layer 3k: BKW Bern + Jura
    if (_BKW_LAT_MIN <= lat <= _BKW_LAT_MAX
            and _BKW_LON_MIN <= lon <= _BKW_LON_MAX):
        return "BKW"

    # Layer 3z: Axpo Grid Deutschschweiz default catch-all
    return "Axpo Grid"


# ── Swissgrid TSO voltage threshold ──────────────────────────────────────
# Swissgrid operates 380/220 kV EHV backbone. Below 220 kV → DSO
# jurisdiction via NUTS-3 map or lat/lon geofence. 150 kV boundary case
# — default to Swissgrid if voltage present but no territorial resolution.
_SWISSGRID_TSO_MIN_KV = 220.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None, lat: float, lon: float, nuts3: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Region-jurisdiction × voltage-class resolver — 10th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary + Slovenia
    + Colombia + Norway + Slovakia + Czechia + Iceland). Wave 2/3
    cumulative precedent (Layer 3 lat/lon geofence when NUTS-3 tag
    absent) applied per Convention #78 BINDING 6th enforcement Layer 3
    geofence sub-convention.

    Switzerland empirically EXTENDS Layer 3 geofence from Iceland's
    5-way multi-DSO to 8-way multi-metro + multi-cantonal composition:
      Layer 1: Swissgrid TSO threshold ≥220 kV → Swissgrid (380/220 kV backbone).
      Layer 2: NUTS-3 → DSO map (if OSM populates NUTS-3 tags — empirically
               ~0 hits expected in Switzerland; kept for forward-compat).
      Layer 3: Lat/lon geofence → DSO (8-way multi-metro/multi-cantonal):
        3a: EWZ Zürich metro
        3b: SIG Geneva metro
        3c: SIL Lausanne metro
        3d: IWB Basel-Stadt metro
        3e: AET Ticino canton
        3f: Repower Graubünden canton
        3g: SIG Genève canton (broader)
        3h: Groupe E Fribourg + Neuchâtel
        3i: Romande Energie Vaud + Valais
        3j: CKW Zentralschweiz
        3k: BKW Bern + Jura
        3z: Axpo Grid Deutschschweiz default catch-all
      Layer 4: 150 kV mixed tier — defaults to Swissgrid if geofence fails.
      Layer 5: Empirical default — Axpo Grid as LARGEST DSO catch-all.
    """
    # Layer 1: EHV → Swissgrid TSO
    if voltage_kv is not None and voltage_kv >= _SWISSGRID_TSO_MIN_KV:
        return "Swissgrid", "region_jurisdiction_fallback_Swissgrid_TSO_threshold_ge_220kv"

    # Layer 2: NUTS-3 → DSO (empirically ~0 hits — kept for forward-compat)
    if nuts3:
        dso = resolve_owner_from_nuts3(nuts3)
        if dso:
            return dso, f"region_jurisdiction_fallback_{dso}_via_nuts3_{nuts3}"

    # Layer 3: Lat/lon geofence → DSO (8-way multi-metro/multi-cantonal)
    dso_via_geofence = resolve_owner_from_lat_lon_geofence(lat, lon)
    if dso_via_geofence:
        return dso_via_geofence, f"region_jurisdiction_fallback_{dso_via_geofence}_via_lat_lon_geofence"

    # Layer 4: 150 kV mixed tier — default to Swissgrid if geofence None
    if voltage_kv is not None and voltage_kv >= 150.0:
        return "Swissgrid", "region_jurisdiction_fallback_Swissgrid_TSO_150kv_boundary_tier"

    # Layer 5: catch-all — Axpo Grid as LARGEST DSO by area
    return "Axpo Grid", "region_jurisdiction_fallback_Axpo_Grid_default"


# ── Discipline #36 with Switzerland 0.5 km default tolerance ─────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Switzerland bounds filter with 0.5 km default tolerance.

    Per Alpine ridge-line + 41-cross-border-interconnector precedent —
    Switzerland's 1739 km international border (Alpine ridge-lines with
    FR/DE/IT/AT/LI + 2 enclaves Büsingen + Campione d'Italia) warrant
    0.5 km tolerance (5× cadastral default). Switzerland has HIGHEST
    cross-border interconnector count cohort-wide (41 legitimate
    near-border cases); tolerance absorbs Alpine terrain simplification
    without dropping legitimate cross-border TSO substations."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "switzerland", module_fallback=0.5
        )
    return _apply_bounds_generic(
        records, country_slug="switzerland", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "switzerland/v4_23-ingestion-audit-switzerland-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = SWITZERLAND_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("ch-"):
        slug = slug[len("ch-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-switzerland-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Switzerland ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/switzerland/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: switzerland",
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
        "  step_2_fetch: switzerland/v4_23-ingestion-audit-switzerland-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: switzerland/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    SWITZERLAND_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return SWITZERLAND_CACHE_DIR / f"{key}{ext}"


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
    "SWITZERLAND_BOUNDS_JSON",
    "SWITZERLAND_TOLERANCE_JSON",
    "SWITZERLAND_DATA_DIR",
    "SWITZERLAND_CACHE_DIR",
]
