"""
SSI Pipeline — Greece v4.23 ingestion, shared base layer.

Region-jurisdiction × voltage-class monopoly via ADMIE/IPTO TSO
(≥66 kV) + DEDDIE/HEDNO SINGLE national DSO (<66 kV). 9th cohort-wide
application of region-jurisdiction fallback pattern (after Belgium +
Netherlands + Chile + Hungary + Slovenia + Colombia + Norway + Slovakia
+ Czechia). Wave 3 first-country resets smallest-first cadence post
Poland (Wave 2 P21 LARGEST).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 4th EMPIRICAL TEST ⚡

Fourth country onboarded post Convention #78 BINDING promotion event
(Latvia Priority 18 closure, 16 July 2026). Preemptive multi-script
alias mapping REQUIRED at Step 3 connector authoring time:
  - Greek script (ΑΔΜΗΕ / ΔΕΔΔΗΕ / ΔΕΗ / ΑΕ suffix — dominant class)
  - Latin transliteration (ADMIE / DEDDIE / DEI — parallel entries)
  - English acronyms (IPTO / HEDNO / PPC — international documentation)
  - Legal-form variants (ΑΕ / Α.Ε. / SA / S.A. / Anonymos Etaireia)
  - Greek diacritics (τόνος + διαλυτικά — accented letters)
  - Predecessor rebrand: DEI/PPC (pre-2011 integrated utility) → both
    ADMIE (2011) + DEDDIE (2012). SHALLOWER than Poland's 3-generation
    RWE Stoen cascade — single-generation rebrand simplifies attribution.

Greece specifics — SIMPLEST cohort-wide post-BINDING:
  - ADMIE (ΑΔΜΗΕ / IPTO) — Independent Power Transmission Operator SA.
    100% state ownership consolidated 2018-2019 (post partial Chinese
    State Grid stake divestment). Operates 400 kV backbone (Continental
    European sync since 1974) + 150 kV HV mainland + 66 kV subtransmission.
    Established 2011 by unbundling from PPC (DEI) per EU 3rd Energy
    Package Directive 2009/72/EC. ~12,000 km transmission network.
  - DEDDIE (ΔΕΔΔΗΕ / HEDNO) — Hellenic Electricity Distribution Network
    Operator SA. 51% state-owned via PPC subsidiary + 49% Macquarie
    Asset Management (2022 privatisation partial). SINGLE national DSO
    covering ALL mainland + interconnected islands. Voltage: 20 kV MV +
    400/230 V LV. Established 2012 by unbundling from PPC per same
    Directive. ~7.6M connections. NO sub-national DSO partition — Layer
    3 lat/lon geofence NOT required.
  - Historical predecessor preserved for audit trail:
    * DEI/PPC (ΔΕΗ / Δημόσια Επιχείρηση Ηλεκτρισμού) was the pre-2011
      integrated utility. Both ADMIE + DEDDIE were unbundled from it
      2011-2012. Many pre-2011 OSM tags still carry "DEI" or "PPC" or
      "ΔΕΗ" — moderate predecessor alias class.
    * DEI itself is still an active generation company (~45% generation
      market share post-2020 privatisation) — some substations at
      lignite complexes (Kozani + Ptolemaida + Meliti) still tagged with
      DEI as generation-side operator.

Convention #78 §4bis.5 Layer 3 lat/lon geofence:
  - NOT REQUIRED for Greece. Single national DSO removes territorial
    partition complexity. Cumulative post-Greece §4bis.5 enforcement
    count stays at 3 (Prague Czechia + Warsaw narrow-carve-out Poland +
    reserved for multi-DSO countries).
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
    emit_audit_sidecar as _emit_audit_generic,
    now_utc_iso,
)

# ── Paths ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
GREECE_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
GREECE_CACHE_DIR = Path(__file__).resolve().parent / "cache"
GREECE_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ══ Convention #78 BINDING alias normalisation ══════════════════════════
# 4th enforcement — Greek script + Latin transliteration + English
# acronyms + Greek diacritics + ΑΕ/SA legal-form + DEI predecessor.

_OWNER_ALIAS_MAP: dict[str, str] = {
    # ── ADMIE / IPTO variants (TSO — Independent Power Transmission Operator) ──
    "admie": "ADMIE (IPTO)",
    "αδμηε": "ADMIE (IPTO)",                                   # Greek script
    "ipto": "ADMIE (IPTO)",                                    # English acronym
    "admie sa": "ADMIE (IPTO)",
    "admie s.a.": "ADMIE (IPTO)",
    "admie ae": "ADMIE (IPTO)",
    "admie α.ε.": "ADMIE (IPTO)",
    "admie α.ε": "ADMIE (IPTO)",
    "admie αε": "ADMIE (IPTO)",
    "admie a.e.": "ADMIE (IPTO)",                              # Latin a.e. variant
    "admie a.e": "ADMIE (IPTO)",
    "admie a. e.": "ADMIE (IPTO)",                             # spaced variant
    "admie holding": "ADMIE (IPTO Holding)",
    "admie holding sa": "ADMIE (IPTO Holding)",
    "ipto sa": "ADMIE (IPTO)",
    "ipto holding": "ADMIE (IPTO Holding)",
    "independent power transmission operator": "ADMIE (IPTO)",
    "independent power transmission operator sa": "ADMIE (IPTO)",
    "ανεξαρτητοσ διαχειριστησ μεταφορασ ηλεκτρικησ ενεργειασ": "ADMIE (IPTO)",
    "ανεξάρτητος διαχειριστής μεταφοράς ηλεκτρικής ενέργειας": "ADMIE (IPTO)",
    "αδμηε αε": "ADMIE (IPTO)",
    "αδμηε α.ε.": "ADMIE (IPTO)",
    "αδμηε ανώνυμη εταιρεία": "ADMIE (IPTO)",

    # ── DEDDIE / HEDNO variants (SINGLE national DSO) ───────────────────
    "deddie": "DEDDIE (HEDNO)",
    "δεδδηε": "DEDDIE (HEDNO)",                                # Greek script
    "hedno": "DEDDIE (HEDNO)",                                 # English acronym
    "deddie sa": "DEDDIE (HEDNO)",
    "deddie s.a.": "DEDDIE (HEDNO)",
    "deddie ae": "DEDDIE (HEDNO)",
    "deddie α.ε.": "DEDDIE (HEDNO)",
    "deddie α.ε": "DEDDIE (HEDNO)",
    "deddie αε": "DEDDIE (HEDNO)",
    "deddie a.e.": "DEDDIE (HEDNO)",                           # Latin a.e. variant
    "deddie a.e": "DEDDIE (HEDNO)",
    "deddie a. e.": "DEDDIE (HEDNO)",                          # spaced variant
    "hedno sa": "DEDDIE (HEDNO)",
    "hedno s.a.": "DEDDIE (HEDNO)",
    "hellenic electricity distribution network operator": "DEDDIE (HEDNO)",
    "hellenic electricity distribution network operator sa": "DEDDIE (HEDNO)",
    "διαχειριστησ ελληνικου δικτυου διανομησ ηλεκτρικησ ενεργειασ": "DEDDIE (HEDNO)",
    "διαχειριστής ελληνικού δικτύου διανομής ηλεκτρικής ενέργειας": "DEDDIE (HEDNO)",
    "δεδδηε αε": "DEDDIE (HEDNO)",
    "δεδδηε α.ε.": "DEDDIE (HEDNO)",
    "δεδδηε ανώνυμη εταιρεία": "DEDDIE (HEDNO)",

    # ── DEI / PPC predecessor variants (pre-2011 integrated utility) ────
    "dei": "DEI (PPC) — legacy pre-2011",
    "δεη": "DEI (PPC) — legacy pre-2011",                      # Greek script
    "ppc": "DEI (PPC) — legacy pre-2011",                      # English acronym
    "dei sa": "DEI (PPC) — legacy pre-2011",
    "dei s.a.": "DEI (PPC) — legacy pre-2011",
    "dei ae": "DEI (PPC) — legacy pre-2011",
    "δεη αε": "DEI (PPC) — legacy pre-2011",
    "δεη α.ε.": "DEI (PPC) — legacy pre-2011",
    "ppc sa": "DEI (PPC) — legacy pre-2011",
    "ppc s.a.": "DEI (PPC) — legacy pre-2011",
    "public power corporation": "DEI (PPC) — legacy pre-2011",
    "public power corporation sa": "DEI (PPC) — legacy pre-2011",
    "δημοσια επιχειρηση ηλεκτρισμου": "DEI (PPC) — legacy pre-2011",
    "δημόσια επιχείρηση ηλεκτρισμού": "DEI (PPC) — legacy pre-2011",
    "δεη ανώνυμη εταιρεία": "DEI (PPC) — legacy pre-2011",
    # DEI is STILL an active generator post-2020 privatisation (~45% market share)
    # — some substations at Kozani/Ptolemaida/Meliti lignite complexes remain
    # tagged with DEI as generation-side operator. Legacy tag preserved.

    # ── Greek Railways (electric traction 25 kV AC 50 Hz) ────────────────
    "ergose": "OSE / ERGOSE (Greek Railways)",
    "εργοσε": "OSE / ERGOSE (Greek Railways)",
    "ose": "OSE / ERGOSE (Greek Railways)",
    "οσε": "OSE / ERGOSE (Greek Railways)",
    "hellenic railways": "OSE / ERGOSE (Greek Railways)",
    "ergose sa": "OSE / ERGOSE (Greek Railways)",
    "ose sa": "OSE / ERGOSE (Greek Railways)",
    "trainose": "TrainOSE (Greek Railways Operator)",
    "hellenic train": "Hellenic Train (Greek Railways Operator)",

    # ── Athens Metro traction (750 V DC) ─────────────────────────────────
    "attiko metro": "Attiko Metro (Athens Metro Traction)",
    "αττικό μετρό": "Attiko Metro (Athens Metro Traction)",
    "attiko metro sa": "Attiko Metro (Athens Metro Traction)",
    "stasy": "STASY (Athens Tram + Electric Trolleybus)",
    "σταθερεσ συγκοινωνιεσ": "STASY (Athens Tram + Electric Trolleybus)",
    "σταθερές συγκοινωνίες": "STASY (Athens Tram + Electric Trolleybus)",

    # ── Industrial captives (large private consumers) ────────────────────
    "aluminium of greece": "Aluminium of Greece (Distomo)",
    "αλουμίνιον της ελλάδος": "Aluminium of Greece (Distomo)",
    "aluminium of greece sa": "Aluminium of Greece (Distomo)",
    "aluminum of greece": "Aluminium of Greece (Distomo)",   # US-English variant
    "mytilineos": "Mytilineos (Aluminium of Greece parent)",
    "μυτιληναίος": "Mytilineos (Aluminium of Greece parent)",
    "hellenic petroleum": "Hellenic Petroleum (ELPE)",
    "ελληνικά πετρέλαια": "Hellenic Petroleum (ELPE)",
    "elpe": "Hellenic Petroleum (ELPE)",
    "helpe": "Hellenic Petroleum (ELPE)",
    "motor oil hellas": "Motor Oil Hellas (Corinth refinery)",
    "motor oil": "Motor Oil Hellas (Corinth refinery)",
    "larco": "Larco (Ferronickel Larymna) — legacy",
    "λάρκο": "Larco (Ferronickel Larymna) — legacy",
    "corinth pipeworks": "Corinth Pipeworks (Thisvi steel)",
    "hellenic sugar industry": "Hellenic Sugar Industry (Serres + Xanthi)",
    "ελληνική βιομηχανία ζάχαρης": "Hellenic Sugar Industry (Serres + Xanthi)",
    "cenergy": "Cenergy Holdings (Corinth Pipeworks parent)",

    # ── Renewable independent power producers (mostly wind + solar) ──────
    "terna energy": "Terna Energy (RES IPP)",
    "τέρνα ενεργειακή": "Terna Energy (RES IPP)",
    "iberdrola rokas": "Iberdrola Rokas (Wind IPP)",
    "iberdrola": "Iberdrola (RES IPP)",
    "edf renewables": "EDF Renewables Hellas (RES IPP)",
    "enel green power hellas": "Enel Green Power Hellas (RES IPP)",
    "hellenic wind power": "Hellenic Wind Power (RES IPP)",
    "reeder renewables": "Reeder Renewables (RES IPP)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING enforcement — preserves Greek diacritics
    (τόνος + διαλυτικά — accented letters) + Latin transliteration +
    English acronyms + ΑΕ/SA legal-form variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Greek
    diacritics preserved in input, normalised via NFC + lower-case
    lookup. Handles multi-script (Greek + Latin) parallel entries and
    DEI/PPC pre-2011 predecessor tags per Convention #78 BINDING 4th
    enforcement."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _OWNER_ALIAS_MAP.get(key, owner.strip())


# ══ Region-jurisdiction × voltage-class resolver — SIMPLEST cohort-wide ══
# Greece has SINGLE national DSO. NO NUTS-3 map needed. NO Layer 3
# geofence needed. Attribution reduces to voltage-class threshold:
#   ≥66 kV → ADMIE (IPTO) — TSO
#   <66 kV → DEDDIE (HEDNO) — SINGLE national DSO

_ADMIE_VOLTAGE_THRESHOLD_KV = 66.0     # 66 kV subtransmission still ADMIE
                                        # (150 kV mainland HV backbone above)


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None,
    lat: float,
    lon: float,
    *,
    nuts3: str | None = None,
) -> tuple[str, str]:
    """Greek single-DSO region-jurisdiction resolver.

    Rules (in priority order):
      1. Voltage ≥ 66 kV → ADMIE (IPTO) TSO
      2. Voltage < 66 kV → DEDDIE (HEDNO) SINGLE national DSO
      3. Voltage None → DEDDIE (HEDNO) default (Convention #56 preserved
         — voltage-degraded subs default to distribution-tier attribution
         which is empirically dominant class in Greek grid)

    nuts3 parameter accepted for API-compat with czechia/poland/canada
    connector interface but NOT used (single-DSO makes it moot).

    Returns:
        (owner_name, provenance_tag) tuple where provenance_tag is
        one of: 'region_jurisdiction_fallback_ADMIE_TSO',
                'region_jurisdiction_fallback_DEDDIE_DSO',
                'region_jurisdiction_fallback_DEDDIE_DSO_voltage_default'
    """
    if voltage_kv is None:
        return ("DEDDIE (HEDNO)", "region_jurisdiction_fallback_DEDDIE_DSO_voltage_default")
    if voltage_kv >= _ADMIE_VOLTAGE_THRESHOLD_KV:
        return ("ADMIE (IPTO)", "region_jurisdiction_fallback_ADMIE_TSO")
    return ("DEDDIE (HEDNO)", "region_jurisdiction_fallback_DEDDIE_DSO")


# ══ Discipline #36 cross-border filter ═══════════════════════════════════

def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Apply Greece polygon filter with configurable tolerance.

    Uses canada _base generic filter with country_slug='greece' + tolerance
    loaded from cross_border_tolerances.json (default 100m cadastral per
    Discipline #36 baseline). Follows Canada canonical keyword-only-args
    pattern per Poland P21 hotfix precedent (Task #288)."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(GREECE_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(tol_cfg.get("per_country", {}).get("greece", {}).get("tolerance_km", 0.1))
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(records, country_slug="greece", tolerance_km=tolerance_km)


# ══ Cache helper ═════════════════════════════════════════════════════════

def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    """Return path to per-URL cache file inside greece cache dir."""
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return GREECE_CACHE_DIR / f"cz-{key}{ext}"


# ══ Audit sidecar emitter ════════════════════════════════════════════════

def emit_audit_sidecar(result, *, parity_findings=None):
    """Emit v4.23 audit sidecar per convention (delegates to canada generic)."""
    return _emit_audit_generic(result, parity_findings=parity_findings)
