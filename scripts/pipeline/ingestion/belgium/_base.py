"""
SSI Pipeline — Belgium v4.23 ingestion, shared base layer.

Country-parallel of Austria + Greenland + Mexico + Australia _base.py. Reuses
country-agnostic dataclasses from Canada _base and overlays Belgium-specific
paths + tolerance + 3-region owner fallback logic.

Belgium specifics:
  - 3 regions × distinct DNSPs (Flanders → Fluvius; Wallonia → ORES/Resa;
    Brussels-Capital → Sibelga)
  - 1 TSO Elia (≥150 kV federal network)
  - Fluvius is single Flanders DNSP post-2018 Eandis+Infrax merger
  - Wallonia has ORES (4 provinces) + Resa (Liège metro only) — geofence
    disambiguation
  - Historical OSM tags may show pre-merger names — normalise via alias map
"""

from __future__ import annotations

import hashlib
import json
import logging
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
BELGIUM_BOUNDS_JSON = REPO_ROOT / "belgium" / "bounds.json"
BELGIUM_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
BELGIUM_DATA_DIR = PIPELINE_DIR / "data" / "belgium"
BELGIUM_CACHE_DIR = BELGIUM_DATA_DIR / "_osm_cache"


# ── Region-jurisdiction owner fallback ───────────────────────────────────
#
# Voltage threshold: 150 kV. Above → Elia TSO; below → region DNSP.
# Elia operates 380/220/150 kV federal network. Belgian DNSPs operate
# 70/36/15/11/10 kV MV + LV distribution.

_TSO_THRESHOLD_KV = 150.0

# Historical DNSP alias normalisation (Fluvius Eandis+Infrax pre-2018)
_DNSP_ALIAS_MAP = {
    "Eandis": "Fluvius",
    "Infrax": "Fluvius",
    "Fluvius System Operator": "Fluvius",
    "Tecteo": "Resa",
    "RESA": "Resa",
    "ORES Assets": "ORES",
    "Sibelga (BE)": "Sibelga",
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Map historical/variant owner names to canonical DNSP identifier."""
    if not owner:
        return owner
    return _DNSP_ALIAS_MAP.get(owner.strip(), owner.strip())


def _region_from_lat_lon(lat: float, lon: float) -> str | None:
    """Coarse Belgium region assignment from lat/lon.

    NOT a polygon check — quadrant heuristics. Cross-border filter still
    applies (Discipline #36).

    Flanders: north half (lat >= 50.7 mostly, but also south-west West-Flanders
              coast). Approximation: south boundary is the linguistic border
              (roughly lat 50.7-50.8, sloping down toward Brussels bubble).
    Wallonia: south half (lat < 50.7 outside Brussels bubble).
    Brussels-Capital: small bubble at lat 50.76-50.91, lon 4.31-4.49.
    """
    # Brussels-Capital tight bubble first
    if 50.76 <= lat <= 50.91 and 4.31 <= lon <= 4.49:
        return "BRU"
    # Approximation of linguistic border for the rest
    # Flanders/Wallonia boundary runs roughly W-E along lat 50.7-50.8
    # with dips (Brussels enclave excluded above; Halle-Vilvoorde Flemish)
    if lat >= 50.7:
        return "FLA"
    # South of that = Wallonia
    return "WAL"


def resolve_owner_from_region_jurisdiction(
    lat: float, lon: float, voltage_kv: float | None, osm_region: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance) tuple.

    Uses OSM addr:region= or region= tag if provided, otherwise falls back
    to lat/lon geofence. Returns (None, provenance) if region can't be
    resolved.
    """
    # Try OSM region tag first (typically "Flanders" / "Wallonia" / "Brussels")
    region = None
    if osm_region:
        low = osm_region.strip().lower()
        if "flan" in low or "vlaanderen" in low:
            region = "FLA"
        elif "wallo" in low or "wall" in low:
            region = "WAL"
        elif "brussel" in low or "brux" in low:
            region = "BRU"

    if region is None:
        region = _region_from_lat_lon(lat, lon)
    if region is None:
        return None, "region_unresolved_no_geofence_match"

    is_tso = voltage_kv is not None and voltage_kv >= _TSO_THRESHOLD_KV
    if is_tso:
        return "Elia", f"region_fallback_TSO_gte{_TSO_THRESHOLD_KV}kV"

    if region == "FLA":
        return "Fluvius", "region_fallback_Flanders_Fluvius_post2018_merger"

    if region == "WAL":
        # Liege metro geofence for Resa vs ORES default
        # Resa scope: Liège city + immediate suburbs — narrow band around lat/lon
        if 50.55 <= lat <= 50.72 and 5.45 <= lon <= 5.75:
            return "Resa", "region_fallback_Wallonia_Liege_metro_Resa_geofence"
        return "ORES", "region_fallback_Wallonia_ORES_default"

    if region == "BRU":
        return "Sibelga", "region_fallback_Brussels_Capital_Sibelga"

    return None, f"region_fallback_region_{region}_no_mapping"


# ── Discipline #36 with Belgium 100m default tolerance ───────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Belgium bounds filter with 100m default tolerance.

    Belgium bounds already CLEAN pre-workstream (task #58 Mode 2 not required —
    no offshore/territorial complications). 100m adequate.
    """
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "belgium", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="belgium", tolerance_km=tolerance_km
    )


# ── Audit sidecar (§5ter contract) ───────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "belgium/v4_23-ingestion-audit-belgium-preflight.yaml",
) -> Path:
    """Emit Belgium audit sidecar mirroring the 6 prior countries."""
    if output_dir is None:
        output_dir = BELGIUM_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("be-"):
        slug = slug[len("be-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-belgium-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Belgium ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/belgium/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: belgium",
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
        "  step_2_fetch: belgium/v4_23-ingestion-audit-belgium-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: belgium/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    BELGIUM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return BELGIUM_CACHE_DIR / f"{key}{ext}"


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
    "normalise_owner_alias",
    "BELGIUM_BOUNDS_JSON",
    "BELGIUM_TOLERANCE_JSON",
    "BELGIUM_DATA_DIR",
    "BELGIUM_CACHE_DIR",
]
