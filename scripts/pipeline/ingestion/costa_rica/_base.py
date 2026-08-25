"""
SSI Pipeline — Costa Rica v4.23 ingestion, shared base layer.

Third application of the monopoly-class fallback pattern (after Greenland pure
+ Luxembourg + municipal overlay), extended with 7-DSO nested territorial
overlay. Costa Rica specifics:
  - ICE d.o.o. state-owned TSO+DSO ~40% direct + all transmission ≥138 kV
  - 7 non-ICE DSOs handle specific cantons/provinces
  - Historical/legal-form alias normalisation (I.C.E. / R.L. / d.d. strip)

Note: Python package uses underscore (costa_rica); data path uses hyphen
(costa-rica/).
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
# Data path uses hyphen per intelligence/countries.json slug convention
COSTA_RICA_BOUNDS_JSON = REPO_ROOT / "costa-rica" / "bounds.json"
COSTA_RICA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
COSTA_RICA_DATA_DIR = PIPELINE_DIR / "data" / "costa-rica"
COSTA_RICA_CACHE_DIR = COSTA_RICA_DATA_DIR / "_osm_cache"


# ── DSO alias normalisation (case-insensitive) ───────────────────────────
_DNSP_ALIAS_MAP = {
    # ICE variants (state TSO+DSO)
    "ice": "ICE",
    "i.c.e.": "ICE",
    "i.c.e": "ICE",
    "instituto costarricense de electricidad": "ICE",
    "ice — servicio eléctrico": "ICE",
    "ice - servicio eléctrico": "ICE",
    "ice servicio electrico": "ICE",
    # CNFL variants (ICE subsidiary SJ metro)
    "cnfl": "CNFL",
    "c.n.f.l.": "CNFL",
    "c.n.f.l": "CNFL",
    "compañía nacional de fuerza y luz": "CNFL",
    "compania nacional de fuerza y luz": "CNFL",
    "cia nacional fuerza y luz": "CNFL",
    "cnfl s.a.": "CNFL",
    # ESPH variants (municipal Heredia)
    "esph": "ESPH",
    "e.s.p.h.": "ESPH",
    "esph s.a.": "ESPH",
    "empresa de servicios públicos de heredia": "ESPH",
    "empresa de servicios publicos de heredia": "ESPH",
    # JASEC variants (municipal Cartago)
    "jasec": "JASEC",
    "j.a.s.e.c.": "JASEC",
    "junta administrativa del servicio eléctrico de cartago": "JASEC",
    "junta administrativa del servicio electrico de cartago": "JASEC",
    # Coopeguanacaste variants
    "coopeguanacaste": "Coopeguanacaste",
    "coopeguanacaste r.l.": "Coopeguanacaste",
    "coopeguanacaste rl": "Coopeguanacaste",
    "coopeguanacaste r l": "Coopeguanacaste",
    # Coopelesca variants
    "coopelesca": "Coopelesca",
    "coopelesca r.l.": "Coopelesca",
    "coopelesca rl": "Coopelesca",
    "coopelesca r l": "Coopelesca",
    # Coopesantos variants
    "coopesantos": "Coopesantos",
    "coopesantos r.l.": "Coopesantos",
    "coopesantos rl": "Coopesantos",
    "coopesantos r l": "Coopesantos",
    # Coopealfaroruiz variants
    "coopealfaroruiz": "Coopealfaroruiz",
    "coopealfaroruiz r.l.": "Coopealfaroruiz",
    "coopealfaroruiz rl": "Coopealfaroruiz",
    "coopealfaro ruiz": "Coopealfaroruiz",
    "coope alfaro ruiz": "Coopealfaroruiz",
    # Regulators (unlikely on subs but preserved)
    "minae": "MINAE",
    "aresep": "ARESEP",
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive alias normalisation with Spanish legal-form strip."""
    if not owner:
        return owner
    key = owner.strip().lower()
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── ICE TSO voltage threshold ────────────────────────────────────────────
# All Costa Rica transmission ≥138 kV is ICE (230 kV backbone + 138 kV subtrunk).
# Below 138 kV falls to DSO layer (ICE distribution or non-ICE DSO overlay).
_ICE_TSO_MIN_KV = 138.0


# ── DSO territory geofence (priority-ordered, most-specific-first) ───────
def _dso_from_lat_lon_geofence(lat: float, lon: float) -> str | None:
    """Return non-ICE DSO name via lat/lon geofence with priority ordering.

    Costa Rica has 7 non-ICE DSOs mapped to cantonal territories. Priority
    ordering resolves overlap zones (e.g. Coopealfaroruiz canton sits inside
    Alajuela province where ICE default would otherwise fire).

    Territory bounding boxes derived from cantonal boundaries + empirical
    OSM DSO distribution. ICE fires as monopoly default for all territory
    outside these 7 nested boxes.
    """
    # Priority 1: Coopealfaroruiz RL — Zarcero canton (Alfaro Ruiz), tiny NW Alajuela
    if 10.15 <= lat <= 10.30 and -84.50 <= lon <= -84.30:
        return "Coopealfaroruiz"

    # Priority 2: ESPH — Heredia city + Barva + Santo Domingo + San Rafael + San Isidro + San Pablo
    if 9.98 <= lat <= 10.10 and -84.15 <= lon <= -84.02:
        return "ESPH"

    # Priority 3: JASEC — Cartago central + Alvarado + Oreamuno + El Guarco + Paraíso
    if 9.83 <= lat <= 9.92 and -83.95 <= lon <= -83.80:
        return "JASEC"

    # Priority 4: Coopesantos RL — Los Santos (Tarrazú + Dota + León Cortés + Acosta)
    if 9.55 <= lat <= 9.85 and -84.30 <= lon <= -83.85:
        return "Coopesantos"

    # Priority 5: Coopelesca RL — San Carlos + Los Chiles + Guatuso + Upala + partial Sarapiquí
    if 10.30 <= lat <= 11.10 and -84.90 <= lon <= -84.20:
        return "Coopelesca"

    # Priority 6: Coopeguanacaste RL — Santa Cruz + Nicoya + Nandayure + Carrillo + Hojancha
    if 9.85 <= lat <= 10.65 and -85.80 <= lon <= -85.20:
        return "Coopeguanacaste"

    # Priority 7: CNFL — San José metro + neighbouring cantons (ICE subsidiary)
    if 9.85 <= lat <= 10.05 and -84.30 <= lon <= -84.00:
        return "CNFL"

    return None


def resolve_owner_from_monopoly_with_overlay(
    voltage_kv: float | None,
    lat: float,
    lon: float,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Layer 1: ICE TSO threshold ≥138 kV → ICE.
    Layer 2: Non-ICE DSO via lat/lon geofence (7-territory priority order).
    Layer 3: ICE monopoly default (all remaining territory).
    """
    # Layer 1: TSO threshold ≥138 kV → ICE
    if voltage_kv is not None and voltage_kv >= _ICE_TSO_MIN_KV:
        return "ICE", "monopoly_fallback_ICE_TSO_threshold_ge_138kv"

    # Layer 2: Non-ICE DSO via lat/lon geofence
    dso = _dso_from_lat_lon_geofence(lat, lon)
    if dso is not None:
        return dso, f"monopoly_fallback_dso_overlay_{dso.replace(' ', '_')}_geofence"

    # Layer 3: ICE default (monopoly fallback for all remaining territory)
    return "ICE", "monopoly_fallback_ICE_default_state_majority_utility"


# ── Discipline #36 with Costa Rica 100m default tolerance ────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Costa Rica bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "costa-rica", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="costa-rica", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "costa-rica/v4_23-ingestion-audit-costa-rica-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = COSTA_RICA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("cr-"):
        slug = slug[len("cr-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-costa-rica-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Costa Rica ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/costa_rica/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: costa-rica",
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
        "  step_2_fetch: costa-rica/v4_23-ingestion-audit-costa-rica-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: costa-rica/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    COSTA_RICA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return COSTA_RICA_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_monopoly_with_overlay",
    "normalise_owner_alias",
    "COSTA_RICA_BOUNDS_JSON",
    "COSTA_RICA_TOLERANCE_JSON",
    "COSTA_RICA_DATA_DIR",
    "COSTA_RICA_CACHE_DIR",
]
