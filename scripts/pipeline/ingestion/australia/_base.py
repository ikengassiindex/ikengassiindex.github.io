"""
SSI Pipeline — Australia v4.23 ingestion, shared base layer.

Country-parallel of Austria + Greenland + Mexico _base.py. Re-exports the
country-agnostic dataclasses from Canada _base and overlays Australia-specific
paths + tolerance config + state-jurisdiction owner fallback logic.

Australia specifics:
  - 8 states/territories with per-jurisdiction TSO + DNSPs (see mapping below)
  - Federal-fragmented — no monopoly-fallback rule (Austrian pattern)
  - State-jurisdiction fallback logic: for substations with no OSM operator=
    tag, assign owner based on (a) which state polygon they fall in and (b)
    voltage class (>132 kV → state TSO; ≤132 kV → state DNSP with metro/rural
    disambiguation)
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from ...utils.tolerance import resolve_boundary_tolerance_km

# Re-export the country-agnostic dataclasses from Canada _base
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
AUSTRALIA_BOUNDS_JSON = REPO_ROOT / "australia" / "bounds.json"
AUSTRALIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
AUSTRALIA_DATA_DIR = PIPELINE_DIR / "data" / "australia"
AUSTRALIA_CACHE_DIR = AUSTRALIA_DATA_DIR / "_osm_cache"


# ── State-jurisdiction owner fallback ────────────────────────────────────
#
# Per pre-flight audit (australia/v4_23-ingestion-audit-australia-preflight.yaml),
# assign owner from state + voltage class for substations with no OSM
# operator= tag. Multi-DNSP states (NSW/QLD/VIC) use metro/rural geofence
# refinement.
#
# HV/EHV threshold: 132 kV. Above this → state TSO. At or below → state DNSP.
# Precedent: NEM/WEM operational thresholds at 132 kV network boundary.

_HV_TSO_THRESHOLD_KV = 132.0


def _state_from_lat_lon(lat: float, lon: float) -> str | None:
    """Very-coarse state assignment from lat/lon.

    NOT a polygon check — just quadrant heuristics for cases where OSM
    doesn't already tag `addr:state=`. Refined against pre-flight
    substation distribution. Cross-border filter still applies (Discipline #36).
    """
    # Tasmania (island)
    if lat < -40.0:
        return "TAS"
    # NT (top-end)
    if lat > -26.0 and 129.0 <= lon <= 138.0:
        return "NT"
    # WA (west of 129E)
    if lon < 129.0:
        return "WA"
    # SA (129-141E, south of -26)
    if 129.0 <= lon < 141.0:
        return "SA"
    # QLD (north-east above -29)
    if lat > -29.0 and lon >= 138.0:
        return "QLD"
    # NSW/ACT (141-154E, -29 to -37)
    if lon >= 141.0:
        # ACT bubble (Canberra ~ -35.3, 149.1)
        if -35.9 < lat < -35.1 and 148.7 < lon < 149.5:
            return "ACT"
        # VIC (below -34)
        if lat < -34.0 and lon < 150.0:
            return "VIC"
        # NSW default (also covers south-east coast)
        return "NSW"
    return None


def resolve_owner_from_state_jurisdiction(
    lat: float, lon: float, voltage_kv: float | None, osm_state: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance) tuple.

    Uses OSM addr:state= tag if provided, otherwise falls back to lat/lon.
    Returns (None, provenance) if state can't be resolved.
    """
    state = osm_state or _state_from_lat_lon(lat, lon)
    if state is None:
        return None, "state_unresolved_no_geofence_match"

    state = state.upper()
    is_tso = voltage_kv is not None and voltage_kv > _HV_TSO_THRESHOLD_KV

    if state == "NSW":
        if is_tso:
            return "TransGrid", f"state_fallback_NSW_TSO_gt{_HV_TSO_THRESHOLD_KV}kV"
        # Metro Sydney: lat -34.2 to -32.5, lon 150.5 to 151.5
        if -34.2 < lat < -32.5 and 150.5 < lon < 151.5:
            return "Ausgrid", "state_fallback_NSW_metro_Sydney_geofence"
        # Greater Western Sydney: -34.2 to -33.4, 150.0 to 150.9
        if -34.2 < lat < -33.4 and 150.0 < lon < 150.9:
            return "Endeavour Energy", "state_fallback_NSW_greater_west_geofence"
        return "Essential Energy", "state_fallback_NSW_rural_default"

    if state == "QLD":
        if is_tso:
            return "Powerlink", f"state_fallback_QLD_TSO_gt{_HV_TSO_THRESHOLD_KV}kV"
        # SEQ south-east corner: lat -28.5+, lon <153.5 (Brisbane/GC/Sunshine Coast)
        if lat > -28.5 and lon < 153.5:
            return "Energex", "state_fallback_QLD_SEQ_geofence"
        return "Ergon Energy", "state_fallback_QLD_rural_default"

    if state == "VIC":
        if is_tso:
            return "AEMO Victoria", f"state_fallback_VIC_TSO_gt{_HV_TSO_THRESHOLD_KV}kV"
        # VIC has 5 DNSPs — geofence approximation only for CitiPower (Melbourne CBD)
        # and Powercor (west VIC). Others default to visibly-honest unresolved.
        if -37.85 < lat < -37.75 and 144.90 < lon < 145.00:
            return "CitiPower", "state_fallback_VIC_Melbourne_CBD_geofence"
        if lon < 143.5:
            return "Powercor", "state_fallback_VIC_west_geofence"
        # Multi-DNSP unresolved — visibly-honest per Convention #56
        return "Victoria DNSP (unresolved multi-provider)", "state_fallback_VIC_multi_dnsp_unresolved_convention_56"

    if state == "WA":
        if is_tso:
            return "Western Power", f"state_fallback_WA_TSO_gt{_HV_TSO_THRESHOLD_KV}kV"
        # Horizon Power = regional/off-grid (roughly north of -25 latitude)
        if lat > -25.0:
            return "Horizon Power", "state_fallback_WA_regional_geofence"
        return "Western Power", "state_fallback_WA_SWIS_default"

    if state == "SA":
        if is_tso:
            return "ElectraNet", f"state_fallback_SA_TSO_gt{_HV_TSO_THRESHOLD_KV}kV"
        return "SA Power Networks", "state_fallback_SA_DNSP"

    if state == "TAS":
        return "TasNetworks", "state_fallback_TAS_combined_tso_dnsp"

    if state == "ACT":
        return "Evoenergy", "state_fallback_ACT_combined"

    if state == "NT":
        return "Power and Water Corporation", "state_fallback_NT_combined"

    return None, f"state_fallback_state_{state}_no_mapping"


# ── Discipline #36 with Australia 100m default tolerance ─────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Australia bounds filter with 100m default tolerance.

    Australia bounds already remediated per task #59 (Mode 2 tolerance config)
    and task #58 (Mode 3 documentation). 100m default adequate for mainland +
    Tasmania. Coastal islands + territorial waters handled by tolerance config.
    """
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "australia", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="australia", tolerance_km=tolerance_km
    )


# ── Audit sidecar (§5ter contract) ───────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "australia/v4_23-ingestion-audit-australia-preflight.yaml",
) -> Path:
    """Emit Australia audit sidecar mirroring Canada + Austria + Greenland."""
    if output_dir is None:
        output_dir = AUSTRALIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("au-"):
        slug = slug[len("au-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-australia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Australia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/australia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: australia",
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
        "  step_2_fetch: australia/v4_23-ingestion-audit-australia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: australia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    AUSTRALIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return AUSTRALIA_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_state_jurisdiction",
    "AUSTRALIA_BOUNDS_JSON",
    "AUSTRALIA_TOLERANCE_JSON",
    "AUSTRALIA_DATA_DIR",
    "AUSTRALIA_CACHE_DIR",
]
