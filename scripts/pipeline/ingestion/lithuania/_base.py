"""
SSI Pipeline — Lithuania v4.23 ingestion, shared base layer.

Simplest 2-operator vertically-integrated state monopoly via EPSO-G holding.
Lithuania specifics:
  - Litgrid AB TSO (100% state) ≥110 kV — 400 + 330 + 110 kV transmission
  - ESO monopoly default (100% state) — 35 + 30 + 10 + 0.4 kV distribution
  - Historical Litgrid/ESO legacy names (Lietuvos energija / LESTO) preserved
    for audit trail
  - Lithuanian Unicode NFC alias normalisation
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
LITHUANIA_BOUNDS_JSON = REPO_ROOT / "lithuania" / "bounds.json"
LITHUANIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
LITHUANIA_DATA_DIR = PIPELINE_DIR / "data" / "lithuania"
LITHUANIA_CACHE_DIR = LITHUANIA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (case-insensitive + Unicode NFC) ───────────
_DNSP_ALIAS_MAP = {
    # Litgrid variants (English + Lithuanian + legal-form)
    "litgrid": "Litgrid",
    "litgrid ab": "Litgrid",
    "litgrid a.b.": "Litgrid",
    "ab litgrid": "Litgrid",
    # Lietuvos energija — pre-2011 predecessor
    "lietuvos energija": "Litgrid-legacy",
    "ab lietuvos energija": "Litgrid-legacy",
    # ESO variants (English + Lithuanian + legal-form)
    "eso": "ESO",
    "eso ab": "ESO",
    "ab eso": "ESO",
    "elektros skirstymo operatorius": "ESO",
    "ab elektros skirstymo operatorius": "ESO",
    "elektros skirstymo operatorius ab": "ESO",
    # LESTO — pre-2016 DSO predecessor
    "lesto": "ESO-legacy",
    "lesto ab": "ESO-legacy",
    "ab lesto": "ESO-legacy",
    # EPSO-G holding (parent — non-owner but may tag some infra)
    "epso-g": "EPSO-G (Holding Company)",
    "epso g": "EPSO-G (Holding Company)",
    "ab epso-g": "EPSO-G (Holding Company)",
    # Ignitis Group (state generator/retailer — non-grid)
    "ignitis": "Ignitis Group (Generation/Retail)",
    "ignitis group": "Ignitis Group (Generation/Retail)",
    "ab ignitis grupė": "Ignitis Group (Generation/Retail)",
    "ab ignitis grupe": "Ignitis Group (Generation/Retail)",
    # Lithuanian Railways (LTG / Lietuvos geležinkeliai) — traction only
    "lietuvos geležinkeliai": "Lithuanian Railways (LTG)",
    "lietuvos gelezinkeliai": "Lithuanian Railways (LTG)",
    "ltg": "Lithuanian Railways (LTG)",
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Lithuanian
    diacritics preserved in input, normalised via NFC + lower-case lookup."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Litgrid TSO voltage threshold ────────────────────────────────────────
# Litgrid operates 400 + 330 + 110 kV transmission (per public EPSO-G data).
# Below 110 kV → ESO monopoly default (35 + 30 + 10 + 0.4 kV distribution).
# 110 kV is MIXED — Litgrid backbone + ESO subtransmission overlap;
# empirically Lithuania's baseline is transmission-heavy so majority at
# 110 kV is Litgrid.
_LITGRID_TSO_MIN_KV = 110.0


def resolve_owner_from_2_operator_monopoly(
    voltage_kv: float | None, lat: float, lon: float
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Simplest 2-operator resolver. No geofence overlay needed — Litgrid + ESO
    are the only 2 grid-infrastructure owners nationwide. Private
    infrastructure (Ignitis generation + railway traction) surfaces via
    direct OSM operator= tag.

    Layer 1: Litgrid TSO threshold ≥110 kV → Litgrid.
    Layer 2: ESO monopoly default (all remaining territory ≤110 kV).
    """
    # Layer 1: TSO threshold ≥110 kV → Litgrid (400 + 330 + 110 kV backbone)
    if voltage_kv is not None and voltage_kv >= _LITGRID_TSO_MIN_KV:
        return "Litgrid", "monopoly_fallback_Litgrid_TSO_threshold_ge_110kv"

    # Layer 2: ESO monopoly default (35 + 30 + 10 kV distribution + unknown)
    return "ESO", "monopoly_fallback_ESO_default_state_dso_via_epso_g_holding"


# ── Discipline #36 with Lithuania 100m default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Lithuania bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(LITHUANIA_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("lithuania", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="lithuania", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "lithuania/v4_23-ingestion-audit-lithuania-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = LITHUANIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("lt-"):
        slug = slug[len("lt-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-lithuania-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Lithuania ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/lithuania/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: lithuania",
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
        "  step_2_fetch: lithuania/v4_23-ingestion-audit-lithuania-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: lithuania/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    LITHUANIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return LITHUANIA_CACHE_DIR / f"{key}{ext}"


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
    "LITHUANIA_BOUNDS_JSON",
    "LITHUANIA_TOLERANCE_JSON",
    "LITHUANIA_DATA_DIR",
    "LITHUANIA_CACHE_DIR",
]
