"""
SSI Pipeline — Estonia v4.23 ingestion, shared base layer.

2-operator vertically-integrated state monopoly via Eesti Energia holding.
Baltic Trio 2nd instance (after Lithuania Priority 16).

Estonia specifics:
  - Elering AS TSO (100% state, spun out from Eesti Energia 2010) ≥110 kV
    — operates 450 kV DC (Estlink 1+2 HVDC subsea to Finland) + 330 kV
    (Soviet-era EHV backbone) + 110 kV transmission
  - Elektrilevi OÜ monopoly default (100% state via Eesti Energia, spun
    out 2013) — operates 35 + 10 + 0.4 kV distribution
  - Historical Elering/Elektrilevi legacy names preserved for audit trail:
    * Põhivõrk (pre-2010 TSO predecessor) → Elering-legacy
    * Eesti Energia Jaotusvõrk (pre-2013 DSO predecessor) → Elektrilevi-legacy
  - Estonian Unicode NFC alias normalisation (Ä Ö Õ Ü Š Ž diacritics)
  - Cyrillic alias handling (Ida-Virumaa / Narva Russian-speaking OSM
    contributors) — Elering Russian: Элеринг · Elektrilevi Russian: Электрилеви
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
ESTONIA_BOUNDS_JSON = REPO_ROOT / "estonia" / "bounds.json"
ESTONIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
ESTONIA_DATA_DIR = PIPELINE_DIR / "data" / "estonia"
ESTONIA_CACHE_DIR = ESTONIA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (case-insensitive + Unicode NFC) ───────────
_DNSP_ALIAS_MAP = {
    # Elering variants (English + Estonian + legal-form)
    "elering": "Elering",
    "elering as": "Elering",
    "as elering": "Elering",
    "elering a.s.": "Elering",
    # Põhivõrk — pre-2010 TSO predecessor (Eesti Energia subsidiary)
    "põhivõrk": "Elering-legacy",
    "põhivõrk oü": "Elering-legacy",
    "oü põhivõrk": "Elering-legacy",
    "pohivork": "Elering-legacy",  # accent-stripped variant
    "pohivork oü": "Elering-legacy",
    # Elektrilevi variants (English + Estonian + legal-form)
    "elektrilevi": "Elektrilevi",
    "elektrilevi oü": "Elektrilevi",
    "oü elektrilevi": "Elektrilevi",
    # Eesti Energia Jaotusvõrk — pre-2013 DSO predecessor
    "eesti energia jaotusvõrk": "Elektrilevi-legacy",
    "jaotusvõrk": "Elektrilevi-legacy",
    "jaotusvõrk oü": "Elektrilevi-legacy",
    "oü jaotusvõrk": "Elektrilevi-legacy",
    "jaotusvork": "Elektrilevi-legacy",  # accent-stripped
    # Eesti Energia holding (parent — non-owner but may tag some infra)
    "eesti energia": "Eesti Energia Grupp (Holding Company)",
    "eesti energia as": "Eesti Energia Grupp (Holding Company)",
    "as eesti energia": "Eesti Energia Grupp (Holding Company)",
    "enefit": "Eesti Energia Grupp (Holding Company)",
    "enefit group": "Eesti Energia Grupp (Holding Company)",
    # Cyrillic-script variants (Ida-Virumaa Narva Russian-speaking population)
    # Preemptively included per Convention #78 sub-convention on multi-script OSM
    "элеринг": "Elering",       # Cyrillic rendering of Elering
    "электрилеви": "Elektrilevi",  # Cyrillic rendering of Elektrilevi
    "эсти энерджиа": "Eesti Energia Grupp (Holding Company)",
    # Estonian Railways (Elektriraudtee / Eesti Raudtee — electric traction only)
    "elektriraudtee": "Estonian Railways (Electric)",
    "elektriraudtee as": "Estonian Railways (Electric)",
    "eesti raudtee": "Estonian Railways (Electric)",
    # Alexela (Estonian private energy retailer, occasional grid-adjacent tags)
    "alexela": "Alexela (Retail/Generation)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Estonian
    diacritics preserved in input, normalised via NFC + lower-case lookup.
    Handles Cyrillic aliases from Ida-Virumaa Russian-speaking OSM
    contributors per Convention #78 sub-convention."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Elering TSO voltage threshold ────────────────────────────────────────
# Elering operates 450 kV DC (Estlink HVDC) + 330 kV (Soviet-era EHV) +
# 110 kV transmission. Below 110 kV → Elektrilevi monopoly default
# (35 + 10 + 0.4 kV distribution). 110 kV is MIXED — Elering backbone +
# Elektrilevi subtransmission overlap; empirically Estonia's baseline is
# transmission-heavy so majority at 110 kV is Elering.
_ELERING_TSO_MIN_KV = 110.0


def resolve_owner_from_2_operator_monopoly(
    voltage_kv: float | None, lat: float, lon: float
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Simplest 2-operator resolver mirror of Lithuania pattern. No geofence
    overlay needed — Elering + Elektrilevi are the only 2 grid-infrastructure
    owners nationwide. Private infrastructure (Estonian Railways traction +
    Alexela generation) surfaces via direct OSM operator= tag.

    Layer 1: Elering TSO threshold ≥110 kV → Elering.
    Layer 2: Elektrilevi monopoly default (all remaining territory ≤110 kV).
    """
    # Layer 1: TSO threshold ≥110 kV → Elering (450 + 330 + 110 kV backbone)
    if voltage_kv is not None and voltage_kv >= _ELERING_TSO_MIN_KV:
        return "Elering", "monopoly_fallback_Elering_TSO_threshold_ge_110kv"

    # Layer 2: Elektrilevi monopoly default (35 + 10 + 0.4 kV distribution + unknown)
    return "Elektrilevi", "monopoly_fallback_Elektrilevi_default_state_dso_via_eesti_energia_holding"


# ── Discipline #36 with Estonia 100m default tolerance ───────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Estonia bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "estonia", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="estonia", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "estonia/v4_23-ingestion-audit-estonia-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = ESTONIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("ee-"):
        slug = slug[len("ee-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-estonia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Estonia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/estonia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: estonia",
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
        "  step_2_fetch: estonia/v4_23-ingestion-audit-estonia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: estonia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    ESTONIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return ESTONIA_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_2_operator_monopoly",
    "normalise_owner_alias",
    "ESTONIA_BOUNDS_JSON",
    "ESTONIA_TOLERANCE_JSON",
    "ESTONIA_DATA_DIR",
    "ESTONIA_CACHE_DIR",
]
