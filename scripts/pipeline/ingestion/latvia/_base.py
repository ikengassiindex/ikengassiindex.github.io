"""
SSI Pipeline — Latvia v4.23 ingestion, shared base layer.

2-operator vertically-integrated state monopoly via Latvenergo Group holding.
Baltic Trio 3rd instance — empirical completion after Lithuania Priority 16
+ Estonia Priority 17. Queued for Convention #78 sub-convention BINDING
promotion methodology-version event at 3-country cumulative validation.

Latvia specifics:
  - AS Augstsprieguma tīkls (AST) TSO (100% state, spun out from Latvenergo
    Transmission 2011) ≥110 kV — operates 330 kV (Soviet-era EHV backbone)
    + 110 kV transmission
  - AS Sadales tīkls monopoly default (100% state via Latvenergo Group,
    2007 rename from Sadales tīkli) — operates 20 + 10 + 6 + 3 kV
    distribution (Soviet-era voltage mix with dominant 20 kV MV tier)
  - Historical AST/Sadales tīkls legacy names preserved for audit trail
    (DEEPER historical alias depth than Estonia/Lithuania — 3 predecessors):
    * Latvijas Elektrostacijas (pre-2005 TSO predecessor) → AST-legacy
    * Latvenergo Transmission (2005-2011 predecessor) → AST-legacy
    * Sadales tīkli (pre-2007 DSO predecessor) → Sadales tīkls-legacy
  - Latvian Unicode NFC alias normalisation (ā ē ī ō ū č ģ ķ ļ ņ š ž diacritics)
  - Cyrillic alias handling (Latgale Russian-speaking OSM contributors —
    DEEPER than Estonia's Ida-Virumaa: 17.5% baseline share, 25%+ Russian-
    speaking population per 2011 census). Preemptive аст / садалес тиклс /
    латвэнерго Cyrillic renderings per Convention #78 sub-convention.
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
LATVIA_BOUNDS_JSON = REPO_ROOT / "latvia" / "bounds.json"
LATVIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
LATVIA_DATA_DIR = PIPELINE_DIR / "data" / "latvia"
LATVIA_CACHE_DIR = LATVIA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (case-insensitive + Unicode NFC) ───────────
_DNSP_ALIAS_MAP = {
    # AST variants (English + Latvian + legal-form)
    "ast": "AST",
    "as ast": "AST",
    "ast as": "AST",
    "ast a.s.": "AST",
    "augstsprieguma tīkls": "AST",
    "as augstsprieguma tīkls": "AST",
    "augstsprieguma tīkls as": "AST",
    "augstsprieguma tikls": "AST",  # accent-stripped variant
    "as augstsprieguma tikls": "AST",
    # Latvijas Elektrostacijas — pre-2005 TSO predecessor
    "latvijas elektrostacijas": "AST-legacy",
    "as latvijas elektrostacijas": "AST-legacy",
    # Latvenergo Transmission — 2005-2011 predecessor
    "latvenergo transmission": "AST-legacy",
    "latvenergo transmissija": "AST-legacy",
    # Sadales tīkls variants (English + Latvian + legal-form)
    "sadales tīkls": "Sadales tīkls",
    "as sadales tīkls": "Sadales tīkls",
    "sadales tīkls as": "Sadales tīkls",
    "sadales tikls": "Sadales tīkls",  # accent-stripped
    "as sadales tikls": "Sadales tīkls",
    "sadales tikls as": "Sadales tīkls",
    # Sadales tīkli — pre-2007 DSO predecessor (rename to Sadales tīkls in 2007)
    "sadales tīkli": "Sadales tīkls-legacy",
    "as sadales tīkli": "Sadales tīkls-legacy",
    "sadales tikli": "Sadales tīkls-legacy",  # accent-stripped
    "latvenergo sadale": "Sadales tīkls-legacy",  # earlier predecessor
    # Latvenergo holding (parent — non-owner but may tag some infra)
    "latvenergo": "Latvenergo Group (Holding Company)",
    "latvenergo as": "Latvenergo Group (Holding Company)",
    "as latvenergo": "Latvenergo Group (Holding Company)",
    "latvenergo group": "Latvenergo Group (Holding Company)",
    # Cyrillic-script variants (Latgale Russian-speaking population — DEEPER than Estonia)
    # Preemptively included per Convention #78 sub-convention on multi-script OSM
    "аст": "AST",  # Cyrillic AST
    "садалес тиклс": "Sadales tīkls",  # Cyrillic Sadales tīkls
    "садалес тикли": "Sadales tīkls-legacy",  # Cyrillic Sadales tīkli (pre-2007)
    "латвэнерго": "Latvenergo Group (Holding Company)",  # Cyrillic Latvenergo
    "латвияс электростацияс": "AST-legacy",  # Cyrillic Latvijas Elektrostacijas
    # Latvian Railways (Latvijas dzelzceļš — electric traction only)
    "latvijas dzelzceļš": "Latvian Railways (Electric)",
    "latvijas dzelzcels": "Latvian Railways (Electric)",  # accent-stripped
    "ldz": "Latvian Railways (Electric)",
    "as ldz": "Latvian Railways (Electric)",
    "vas latvijas dzelzceļš": "Latvian Railways (Electric)",  # VAS = state joint-stock
    # Conexus Baltic Grid (gas TSO, 2017 unbundling — may occasionally tag electric infra)
    "conexus baltic grid": "Conexus Baltic Grid (Gas Infrastructure)",
    "conexus": "Conexus Baltic Grid (Gas Infrastructure)",
    # Ventspils Nafta (oil terminal industrial captive — Kurzeme port)
    "ventspils nafta": "Ventspils Nafta (Industrial Captive)",
    "ventspils nafta terminals": "Ventspils Nafta (Industrial Captive)",
    # Liepājas Metalurgs (Kurzeme steel industrial captive)
    "liepājas metalurgs": "Liepājas Metalurgs (Industrial Captive)",
    "liepajas metalurgs": "Liepājas Metalurgs (Industrial Captive)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Latvian
    diacritics preserved in input, normalised via NFC + lower-case lookup.
    Handles Cyrillic aliases from Latgale Russian-speaking OSM
    contributors per Convention #78 sub-convention (empirically deeper
    than Estonia's Ida-Virumaa cohort)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── AST TSO voltage threshold ────────────────────────────────────────────
# AST operates 330 kV (Soviet-era EHV) + 110 kV transmission. Below 110 kV →
# Sadales tīkls monopoly default (20 + 10 + 6 + 3 kV distribution). 110 kV
# is MIXED — AST backbone + Sadales tīkls subtransmission overlap;
# empirically Latvia's baseline is transmission-heavy so majority at 110 kV
# is AST. Note Latvia has NO 450 kV HVDC (no Estlink-analogue) — Baltic
# Nordic connection routes via Lithuania (NordBalt/LitPol).
_AST_TSO_MIN_KV = 110.0


def resolve_owner_from_2_operator_monopoly(
    voltage_kv: float | None, lat: float, lon: float
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Simplest 2-operator resolver mirror of Estonia + Lithuania Baltic Trio
    pattern. No geofence overlay needed — AST + Sadales tīkls are the only
    2 grid-infrastructure owners nationwide. Private infrastructure
    (Latvian Railways traction + industrial captives Ventspils Nafta,
    Liepājas Metalurgs) surfaces via direct OSM operator= tag.

    Layer 1: AST TSO threshold ≥110 kV → AST.
    Layer 2: Sadales tīkls monopoly default (all remaining territory ≤110 kV).
    """
    # Layer 1: TSO threshold ≥110 kV → AST (330 + 110 kV backbone)
    if voltage_kv is not None and voltage_kv >= _AST_TSO_MIN_KV:
        return "AST", "monopoly_fallback_AST_TSO_threshold_ge_110kv"

    # Layer 2: Sadales tīkls monopoly default (20 + 10 + 6 + 3 kV distribution + unknown)
    return "Sadales tīkls", "monopoly_fallback_Sadales_tikls_default_state_dso_via_latvenergo_holding"


# ── Discipline #36 with Latvia 100m default tolerance ────────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Latvia bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "latvia", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="latvia", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "latvia/v4_23-ingestion-audit-latvia-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = LATVIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("lv-"):
        slug = slug[len("lv-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-latvia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Latvia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/latvia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: latvia",
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
        "  step_2_fetch: latvia/v4_23-ingestion-audit-latvia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: latvia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    LATVIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return LATVIA_CACHE_DIR / f"{key}{ext}"


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
    "LATVIA_BOUNDS_JSON",
    "LATVIA_TOLERANCE_JSON",
    "LATVIA_DATA_DIR",
    "LATVIA_CACHE_DIR",
]
