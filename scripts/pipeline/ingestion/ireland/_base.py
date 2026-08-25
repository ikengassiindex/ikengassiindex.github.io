"""
SSI Pipeline — Ireland v4.23 ingestion, shared base layer.

Wave 3 Priority 25 (fourth Wave 3 country post-Switzerland; SIMPLER
architecture than Swiss 8-way via single-DSO simplification). Voltage-
class × single-DSO monopoly via EirGrid federal TSO + ESB Networks
single national DSO. 3rd cohort-wide single-DSO application (after
Greece P22 DEDDIE + Costa Rica P13 ICE + now Ireland P25).

⚡ CONVENTION #78 BINDING ENFORCEMENT — 7th EMPIRICAL TEST ⚡

Seventh country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive English + Gaeilge (Irish) alias mapping REQUIRED
at Step 3 connector authoring time:
  - English legal-form variants (Ltd / Limited / plc / DAC / PLC)
  - Gaeilge (Irish) legal-form variants (Teoranta / Teo / Cuideachta)
  - Minimal Gaeilge diacritics (á é í ó ú)
  - Predecessor rebrand: ESB Distribution → ESB Networks 2010
    (15-year legacy)
  - EirGrid Gaeilge alias (Éirid)

Ireland specifics:
  - EirGrid plc — state-owned Irish TSO (established 2006 via EU 3rd
    Package unbundling from ESB Group; full asset transfer 2008).
    Operates 400/275/220/110 kV backbone including Moyle + East-West
    HVDC interconnectors. ~6,900 km transmission network.
  - ESB Networks DAC — SINGLE national DSO covering ALL 26 Republic
    of Ireland counties (analogous to Greek DEDDIE). Voltage: 110 kV
    (mixed TSO/DSO tier) + MV (38/20/10 kV) + LV (0.4 kV). Parent:
    Electricity Supply Board (ESB Group — state-owned 95%).
    ~2.3M electricity customers. Predecessor: ESB Distribution
    (pre-2010 rebrand to ESB Networks) + Designated Activity Company
    legal form (post-2014 Companies Act).
  - SONI (System Operator for Northern Ireland) — sister TSO in NI
    (excluded from Republic bounds via bounds.json). Coordinates via
    SEM/I-SEM (Integrated Single Electricity Market) with EirGrid.
  - Northern Ireland Electricity Networks (NIE Networks) — NI DSO
    (excluded from Republic scope).

Historical predecessors preserved for audit trail:
  - ESB Distribution (pre-2010) → ESB Networks 2010 rebrand + DAC
    conversion 2014 per Companies Act 2014 (LARGEST predecessor
    alias class expected — 15-year legacy)
  - ESB Group (pre-2006) integrated TSO + Generation + DSO until
    EirGrid unbundling; ESB Group retained Generation + DSO
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
IRELAND_BOUNDS_JSON = REPO_ROOT / "ireland" / "bounds.json"
IRELAND_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
IRELAND_DATA_DIR = PIPELINE_DIR / "data" / "ireland"
IRELAND_CACHE_DIR = IRELAND_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING 7th enforcement) ───
# Preemptive English + Gaeilge (Irish) alias mapping: English-language
# DOMINANT (~90%) + minimal Gaeilge diacritics + trilingual legal-form
# (Ltd/Limited/plc/DAC + Teoranta/Teo/Cuideachta)
_DNSP_ALIAS_MAP = {
    # ── EirGrid variants (TSO) ─────────────────────────────────────────
    "eirgrid": "EirGrid",
    "eirgrid plc": "EirGrid",
    "eirgrid Plc": "EirGrid",
    "eirgrid PLC": "EirGrid",
    "eirgrid ltd": "EirGrid",
    "eirgrid limited": "EirGrid",
    "eirgrid group": "EirGrid",
    "eirgrid group plc": "EirGrid",
    "EIRGRID": "EirGrid",
    "Eirgrid": "EirGrid",
    # Gaeilge (Irish) variants
    "éirid": "EirGrid",                       # Gaeilge name
    "eirid": "EirGrid",                       # ASCII transliteration
    "éirid plc": "EirGrid",
    "eirid plc": "EirGrid",
    # Predecessor: ESB Group pre-2006 unbundling
    "esb transmission": "EirGrid-legacy (ESB Group pre-2006 unbundling)",
    "esb transmission network": "EirGrid-legacy (ESB Group pre-2006 unbundling)",

    # ── ESB Networks variants (SINGLE national DSO — LARGEST alias class) ──
    "esb networks": "ESB Networks",
    "esb networks dac": "ESB Networks",
    "esb networks DAC": "ESB Networks",
    "esb networks ltd": "ESB Networks",
    "esb networks Ltd": "ESB Networks",
    "esb networks limited": "ESB Networks",
    "esb networks Limited": "ESB Networks",
    "esb networks plc": "ESB Networks",
    "ESB Networks": "ESB Networks",
    "ESB NETWORKS": "ESB Networks",
    # Parent ESB Group
    "esb": "ESB (Holding — parent, Electricity Supply Board)",
    "esb group": "ESB (Holding — parent, Electricity Supply Board)",
    "esb group plc": "ESB (Holding — parent, Electricity Supply Board)",
    "ESB": "ESB (Holding — parent, Electricity Supply Board)",
    "electricity supply board": "ESB (Holding — parent, Electricity Supply Board)",
    "electricity supply board plc": "ESB (Holding — parent, Electricity Supply Board)",
    # Gaeilge (Irish) full name
    "bord solátbhair leictreachais": "ESB (Holding — Bord Solátbhair Leictreachais)",
    "bord solathair leictreachais": "ESB (Holding — Bord Solátbhair Leictreachais)",
    "bord solathair leictreachais teo": "ESB (Holding — Bord Solátbhair Leictreachais)",
    "bord soláthair leictreachais": "ESB (Holding — Bord Solátbhair Leictreachais)",
    # ESB Distribution predecessor (2010 rebrand — LARGEST legacy 15-year)
    "esb distribution": "ESB Networks-legacy (ESB Distribution pre-2010 rebrand)",
    "esb distribution ltd": "ESB Networks-legacy (ESB Distribution pre-2010 rebrand)",
    "esb distribution limited": "ESB Networks-legacy (ESB Distribution pre-2010 rebrand)",
    # ESB Generation (related but distinct)
    "esb generation": "ESB Generation (Generation — Related Entity)",
    "esb generation and trading": "ESB Generation (Generation — Related Entity)",
    "esb power generation": "ESB Generation (Generation — Related Entity)",

    # ── SONI + NIE Networks (Northern Ireland — cross-border) ──────────
    "soni": "SONI (Northern Ireland TSO — Cross-border SEM/I-SEM)",
    "soni ltd": "SONI (Northern Ireland TSO — Cross-border SEM/I-SEM)",
    "system operator for northern ireland": "SONI (Northern Ireland TSO — Cross-border SEM/I-SEM)",
    "nie": "NIE Networks (Northern Ireland DSO — Cross-border)",
    "nie networks": "NIE Networks (Northern Ireland DSO — Cross-border)",
    "nie networks ltd": "NIE Networks (Northern Ireland DSO — Cross-border)",
    "northern ireland electricity": "NIE Networks (Northern Ireland DSO — Cross-border)",

    # ── Moyle Interconnector + East-West Interconnector ────────────────
    "moyle interconnector": "Moyle Interconnector (HVDC 500 MW to Scotland)",
    "moyle interconnector ltd": "Moyle Interconnector (HVDC 500 MW to Scotland)",
    "east-west interconnector": "East-West Interconnector (HVDC 500 MW to Wales)",
    "ewic": "East-West Interconnector (HVDC 500 MW to Wales)",
    "east west interconnector": "East-West Interconnector (HVDC 500 MW to Wales)",

    # ── Iarnród Éireann (Irish Rail — electric traction) ───────────────
    "iarnród éireann": "Iarnród Éireann (Irish Rail — Electric Traction)",
    "iarnrod eireann": "Iarnród Éireann (Irish Rail — Electric Traction)",
    "irish rail": "Iarnród Éireann (Irish Rail — Electric Traction)",
    "cie": "Iarnród Éireann (CIE parent — Electric Traction)",
    "córas iompair éireann": "Iarnród Éireann (CIE parent — Electric Traction)",
    "coras iompair eireann": "Iarnród Éireann (CIE parent — Electric Traction)",
    "dart": "Iarnród Éireann (DART Electric Traction — Dublin)",
    "dublin area rapid transit": "Iarnród Éireann (DART Electric Traction — Dublin)",
    "luas": "Transport Infrastructure Ireland (Luas Tram — Dublin)",
    "transdev": "Transport Infrastructure Ireland (Luas Tram — Dublin)",

    # ── Bord na Móna (state peat — Midlands, decommissioning) ───────────
    "bord na móna": "Bord na Móna (State Peat — Midlands)",
    "bord na mona": "Bord na Móna (State Peat — Midlands)",
    "bord na móna plc": "Bord na Móna (State Peat — Midlands)",
    "bord na mona plc": "Bord na Móna (State Peat — Midlands)",

    # ── Coillte (Irish Forestry Board) ─────────────────────────────────
    "coillte": "Coillte (Irish Forestry Board)",
    "coillte teoranta": "Coillte (Irish Forestry Board)",
    "coillte teo": "Coillte (Irish Forestry Board)",

    # ── Industrial captives (data centres + aluminium + semiconductor) ─
    "intel": "Intel Ireland (Industrial Captive — Leixlip Fab)",
    "intel ireland": "Intel Ireland (Industrial Captive — Leixlip Fab)",
    "intel ireland ltd": "Intel Ireland (Industrial Captive — Leixlip Fab)",
    "google": "Google Ireland Data Centres (Industrial Captive — Dublin)",
    "google ireland": "Google Ireland Data Centres (Industrial Captive — Dublin)",
    "google data centre": "Google Ireland Data Centres (Industrial Captive — Dublin)",
    "microsoft": "Microsoft Ireland Data Centres (Industrial Captive — Dublin)",
    "microsoft ireland": "Microsoft Ireland Data Centres (Industrial Captive — Dublin)",
    "microsoft datacenter": "Microsoft Ireland Data Centres (Industrial Captive — Dublin)",
    "aws": "AWS Ireland Data Centres (Industrial Captive — Dublin)",
    "amazon web services": "AWS Ireland Data Centres (Industrial Captive — Dublin)",
    "meta": "Meta Ireland Data Centres (Industrial Captive — Dublin)",
    "facebook": "Meta Ireland Data Centres (Industrial Captive — Dublin)",
    "facebook ireland": "Meta Ireland Data Centres (Industrial Captive — Dublin)",
    "aughinish": "Aughinish Alumina (Industrial Captive — Limerick Alumina Refinery)",
    "aughinish alumina": "Aughinish Alumina (Industrial Captive — Limerick Alumina Refinery)",
    "rusal aughinish": "Aughinish Alumina (Industrial Captive — Limerick Alumina Refinery)",
    "moneypoint": "Moneypoint Coal Plant (Decommissioning 2025 — Clare County)",
    "moneypoint power station": "Moneypoint Coal Plant (Decommissioning 2025 — Clare County)",

    # ── Airports (industrial captives) ──────────────────────────────────
    "dublin airport": "Dublin Airport Authority DAA (Industrial Captive)",
    "daa": "Dublin Airport Authority DAA (Industrial Captive)",
    "dublin airport authority": "Dublin Airport Authority DAA (Industrial Captive)",
    "cork airport": "Cork Airport (Industrial Captive)",
    "shannon airport": "Shannon Airport (Industrial Captive)",

    # ── Small municipal DSO placeholders (non-existent in Ireland) ─────
    # Ireland is FULLY UNIFIED under ESB Networks — no municipal DSO
    # cohort. Preserve empty class for future documentation.
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING 7th enforcement — preserves minimal Gaeilge
    (Irish) diacritics (á é í ó ú) + English legal-form variants
    (Ltd/Limited/plc/DAC) + trilingual legal-form (Teoranta/Teo/
    Cuideachta) for OSM tag variants."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with minimal
    Gaeilge (Irish) diacritics preserved in input, normalised via NFC +
    lower-case lookup. Handles English + Gaeilge legal-form variants
    (Ltd/Limited/plc/DAC/Teoranta/Teo/Cuideachta) + ESB Distribution
    predecessor cascade per Convention #78 BINDING 7th enforcement
    (7th empirical test post-promotion).

    Ireland is FIRST English-language Wave 3 country — expected LOWEST
    cohort-wide alias hit count due to English-language dominance
    (~90%) + minimal Gaeilge cohabitation. Establishes precedent for
    future monolingual-English cohort countries (GB/US/AU/CA)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 to DSO map (empirically ~0 hits — single DSO) ─────────────────
# Ireland OSM likely does NOT populate ref:nuts:3 tags on substations
# (Wave 2/3 empirical precedent). Forward-compat surface below; actual
# attribution flows via voltage-class × single-DSO resolver.
# Irish NUTS-3 codes: 8 regions per post-2015 restructure.
_NUTS3_TO_DSO = {
    # All 8 NUTS-3 → ESB Networks (single national DSO)
    "IE041": "ESB Networks",              # Border
    "IE042": "ESB Networks",              # West
    "IE051": "ESB Networks",              # Mid-West
    "IE052": "ESB Networks",              # South-East
    "IE053": "ESB Networks",              # South-West
    "IE061": "ESB Networks",              # Dublin
    "IE062": "ESB Networks",              # Mid-East
    "IE063": "ESB Networks",              # Midland
}


def resolve_owner_from_nuts3(nuts3_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NUTS-3 code (Irish region).

    Single-DSO simplification — every Irish NUTS-3 region routes to
    ESB Networks. Kept for forward-compat with future multi-DSO
    countries; empirically ~0 hits expected."""
    if not nuts3_code:
        return None
    return _NUTS3_TO_DSO.get(nuts3_code.strip().upper())


# ── EirGrid TSO voltage threshold ────────────────────────────────────────
# EirGrid operates 400/275/220/110 kV backbone. 110 kV is Ireland's MAIN
# transmission tier (unlike Central European countries where 110 kV is
# DSO subtransmission). Below 110 kV → ESB Networks distribution.
#
# Empirical rule (documented in preflight):
#   ≥110 kV → EirGrid TSO
#   <110 kV → ESB Networks DSO
#   Voltage None → ESB Networks default (distribution-tier dominant)
_EIRGRID_TSO_MIN_KV = 110.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None, lat: float, lon: float, nuts3: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Region-jurisdiction × voltage-class resolver — 11th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary +
    Slovenia + Colombia + Norway + Slovakia + Czechia + Iceland +
    Switzerland). Greek P22 single-DSO simplification precedent
    applied via Convention #78 BINDING 7th enforcement.

    Ireland empirically SIMPLIFIES Layer 3 geofence to voltage-class
    threshold + single-DSO fallback (no metropolitan carve-outs):
      Layer 1: EirGrid TSO threshold ≥110 kV → EirGrid (400/275/220/110 kV backbone).
      Layer 2: NUTS-3 → DSO map (if OSM populates NUTS-3 tags — empirically
               ~0 hits expected; all NUTS-3 route to ESB Networks anyway).
      Layer 3: Voltage <110 kV OR None → ESB Networks SINGLE national DSO.

    Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED — single national
    DSO covers all 26 Republic of Ireland counties (Greek DEDDIE
    precedent).
    """
    # Layer 1: HV → EirGrid TSO
    if voltage_kv is not None and voltage_kv >= _EIRGRID_TSO_MIN_KV:
        return "EirGrid", "region_jurisdiction_fallback_EirGrid_TSO_threshold_ge_110kv"

    # Layer 2: NUTS-3 → DSO (empirically ~0 hits — all route to ESB Networks)
    if nuts3:
        dso = resolve_owner_from_nuts3(nuts3)
        if dso:
            return dso, f"region_jurisdiction_fallback_{dso}_via_nuts3_{nuts3}"

    # Layer 3: catch-all — ESB Networks SINGLE national DSO
    return "ESB Networks", "region_jurisdiction_fallback_ESB_Networks_default"


# ── Discipline #36 with Ireland 1.0 km default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Ireland bounds filter with 1.0 km default tolerance.

    Per Atlantic coastline + HVDC cross-border precedent — Ireland's
    Atlantic coastline complexity (Ring of Kerry + Wild Atlantic Way
    peninsulas + Aran Islands) + 3 cross-border interconnectors
    (Moyle HVDC + East-West HVDC + Northern Ireland AC land) warrant
    1.0 km tolerance (10× cadastral default). Northern Ireland land
    border (~500 km) is pre-excluded via bounds.json 26-county
    Republic-only polygon."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(IRELAND_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("countries", {}).get("ireland", {}).get("boundary_tolerance_km", 1.0)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 1.0
    return _apply_bounds_generic(
        records, country_slug="ireland", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "ireland/v4_23-ingestion-audit-ireland-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = IRELAND_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("ie-"):
        slug = slug[len("ie-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-ireland-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Ireland ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/ireland/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: ireland",
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
        "  step_2_fetch: ireland/v4_23-ingestion-audit-ireland-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: ireland/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    IRELAND_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return IRELAND_CACHE_DIR / f"{key}{ext}"


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
    "normalise_owner_alias",
    "IRELAND_BOUNDS_JSON",
    "IRELAND_TOLERANCE_JSON",
    "IRELAND_DATA_DIR",
    "IRELAND_CACHE_DIR",
]
