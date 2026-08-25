"""
SSI Pipeline — Luxembourg v4.23 ingestion, shared base layer.

Second application of Greenland monopoly-class pattern. Luxembourg specifics:
  - Creos Luxembourg S.A.: unified TSO+DSO covering ~90% of country
  - Small municipal DSOs (optional geofence):
      Sudstroum:            Esch-sur-Alzette + Bettembourg + Rumelange + Kayl
                            (southern industrial belt)
      Ville de Diekirch:    Diekirch canton small city center
      Ville d'Ettelbruck:   Ettelbruck small city center
      Ville de Vianden:     Vianden pumped-storage town (north)
  - Historical alias normalisation:
      CEGEDEL (pre-2009) → Creos
      Enovos (supply sibling company) → Creos (for grid infrastructure)
"""

from __future__ import annotations

import hashlib
import json
import logging
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
LUXEMBOURG_BOUNDS_JSON = REPO_ROOT / "luxembourg" / "bounds.json"
LUXEMBOURG_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
LUXEMBOURG_DATA_DIR = PIPELINE_DIR / "data" / "luxembourg"
LUXEMBOURG_CACHE_DIR = LUXEMBOURG_DATA_DIR / "_osm_cache"


# ── DSO alias normalisation (case-insensitive) ───────────────────────────
_DNSP_ALIAS_MAP = {
    "creos luxembourg s.a.": "Creos",
    "creos luxembourg sa": "Creos",
    "creos luxembourg": "Creos",
    "creos": "Creos",
    "cegedel": "Creos",  # pre-2009 predecessor
    "cegedel net": "Creos",
    "enovos": "Creos",  # supply sibling; grid is Creos
    "enovos luxembourg": "Creos",
    "sudstroum": "Sudstroum",
    "ville de diekirch": "Ville de Diekirch",
    "ville d'ettelbruck": "Ville d'Ettelbruck",
    "ville de vianden": "Ville de Vianden",
    "diekirch": "Ville de Diekirch",
    "ettelbruck": "Ville d'Ettelbruck",
    "vianden": "Ville de Vianden",
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive alias normalisation."""
    if not owner:
        return owner
    key = owner.strip().lower()
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Municipal DSO geofence ───────────────────────────────────────────────
# Small bounding boxes for known municipal DSO territories
def _municipal_dso_from_geofence(lat: float, lon: float) -> str | None:
    """Return municipal DSO name if lat/lon falls in a known territory."""
    # Sudstroum — southern industrial belt (Esch-sur-Alzette + neighbours)
    # Esch: 49.50, 5.98; Bettembourg: 49.52, 6.10; Rumelange: 49.45, 6.03; Kayl: 49.48, 6.03
    if 49.44 <= lat <= 49.54 and 5.95 <= lon <= 6.12:
        return "Sudstroum"
    # Ville de Diekirch — canton small city
    if 49.86 <= lat <= 49.88 and 6.15 <= lon <= 6.17:
        return "Ville de Diekirch"
    # Ville d'Ettelbruck — canton small city
    if 49.83 <= lat <= 49.85 and 6.09 <= lon <= 6.12:
        return "Ville d'Ettelbruck"
    # Ville de Vianden — small town in Vianden canton (near pumped-storage)
    if 49.93 <= lat <= 49.94 and 6.20 <= lon <= 6.22:
        return "Ville de Vianden"
    return None


def resolve_owner_from_monopoly_default(
    lat: float, lon: float, voltage_kv: float | None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Creos is unified TSO+DSO for ~90% of Luxembourg. Municipal DSOs
    resolved via optional geofence.
    """
    # Check municipal geofence first (small nested territories)
    municipal = _municipal_dso_from_geofence(lat, lon)
    if municipal is not None:
        return municipal, f"monopoly_fallback_municipal_{municipal.replace(' ', '_')}_geofence"

    # Default: Creos (dominant TSO+DSO, ~90% country)
    return "Creos", "monopoly_fallback_Creos_default_90pct_country_coverage"


# ── Discipline #36 with Luxembourg 100m default tolerance ────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Luxembourg bounds filter with 100m default tolerance.

    Luxembourg bounds already CLEAN. 100m adequate for cross-border filtering
    (BE + DE + FR neighbours all handled by polygon).
    """
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(LUXEMBOURG_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("luxembourg", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="luxembourg", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "luxembourg/v4_23-ingestion-audit-luxembourg-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = LUXEMBOURG_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("lu-"):
        slug = slug[len("lu-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-luxembourg-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Luxembourg ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/luxembourg/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: luxembourg",
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
        "  step_2_fetch: luxembourg/v4_23-ingestion-audit-luxembourg-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: luxembourg/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    LUXEMBOURG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return LUXEMBOURG_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_monopoly_default",
    "normalise_owner_alias",
    "LUXEMBOURG_BOUNDS_JSON",
    "LUXEMBOURG_TOLERANCE_JSON",
    "LUXEMBOURG_DATA_DIR",
    "LUXEMBOURG_CACHE_DIR",
]
