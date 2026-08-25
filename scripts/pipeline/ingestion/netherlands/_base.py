"""
SSI Pipeline — Netherlands v4.23 ingestion, shared base layer.

Country-parallel of Belgium/Austria/Australia _base.py. Reuses country-agnostic
dataclasses from Canada _base and overlays Netherlands-specific paths + tolerance
+ 12-province × 6-DSO fallback logic.

Netherlands specifics:
  - 1 TSO: TenneT (operates 110/150/220/380 kV federal network)
  - 3 primary DSOs (98% of subs):
      Liander:  Noord-Holland + Gelderland + Friesland + Flevoland (4 provinces)
      Stedin:   Zuid-Holland + Utrecht + Zeeland (Enduris subsidiary) (3 provinces)
      Enexis:   Overijssel + Drenthe + Groningen + Noord-Brabant + Limburg (5 provinces)
  - 3 small regional DSOs (geofence-resolved):
      Coteq Netbeheer:   Almelo area (Overijssel)
      Rendo Netwerken:   Zwolle+Steenwijk (Overijssel/Drenthe border)
      Westland Infra:    Westland horticultural region (Zuid-Holland)
  - Historical DSO alias normalisation (Enduris → Stedin; Alliander → Liander;
    pre-2011 splitsingswet Nuon/Essent/Eneco preserved via osm_original_operator)
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
NETHERLANDS_BOUNDS_JSON = REPO_ROOT / "netherlands" / "bounds.json"
NETHERLANDS_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
NETHERLANDS_DATA_DIR = PIPELINE_DIR / "data" / "netherlands"
NETHERLANDS_CACHE_DIR = NETHERLANDS_DATA_DIR / "_osm_cache"


# ── Region-jurisdiction owner fallback ───────────────────────────────────
#
# Voltage threshold: 110 kV. Above → TenneT TSO; below → region DSO.
# TenneT operates 110/150/220/380 kV. NL DSOs operate ≤50 kV MV + LV.

_TSO_THRESHOLD_KV = 110.0

# DSO alias normalisation (case-insensitive keys)
_DNSP_ALIAS_MAP = {
    "enduris": "Stedin",  # Enduris = Stedin's Zeeland trading subsidiary
    "alliander": "Liander",  # Alliander is the holding, Liander is the DSO
    "stedin netbeheer": "Stedin",
    "enexis netbeheer": "Enexis",
    "liander n.v.": "Liander",
    "liander nv": "Liander",
    "coteq netbeheer": "Coteq",
    "rendo netwerken": "Rendo",
    "westland infra": "Westland Infra",
    "tennet tso": "TenneT",
    "tennet tso b.v.": "TenneT",
    "tennet nl": "TenneT",
    # Pre-2011 splitsingswet historical names — preserved as osm_original_operator
    # but normalised to modern DSO by geographic scope for owner attribution
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive alias normalisation."""
    if not owner:
        return owner
    key = owner.strip().lower()
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Province → primary DSO map (12 provinces, 3 primary DSOs) ────────────
_PROVINCE_TO_DSO = {
    # Liander (4 provinces)
    "Noord-Holland": "Liander",
    "Gelderland": "Liander",
    "Friesland": "Liander",
    "Flevoland": "Liander",
    # Stedin (3 provinces)
    "Zuid-Holland": "Stedin",
    "Utrecht": "Stedin",
    "Zeeland": "Stedin",  # Enduris subsidiary
    # Enexis (5 provinces)
    "Overijssel": "Enexis",
    "Drenthe": "Enexis",
    "Groningen": "Enexis",
    "Noord-Brabant": "Enexis",
    "Limburg": "Enexis",
    "Limburg (NL)": "Enexis",
}


def _province_from_lat_lon(lat: float, lon: float) -> str | None:
    """Very-coarse province assignment from lat/lon (bounding-box approximation)."""
    # Islands + special regions
    # South (below 51.6): Zeeland or North-Brabant or Limburg
    if lat < 51.6:
        # Zeeland (SW islands + Walcheren + Zeeuws-Vlaanderen)
        if lon < 4.4:
            return "Zeeland"
        # Limburg (NL) — narrow south panhandle
        if lat < 51.3 or (lat < 51.5 and lon > 5.9):
            return "Limburg"
        # North-Brabant (rest of south)
        return "Noord-Brabant"

    # Central (51.6-52.6)
    if lat < 52.6:
        # Zuid-Holland: west coast (Randstad Rotterdam+Den Haag)
        if lon < 4.7 and lat < 52.2:
            return "Zuid-Holland"
        # Utrecht: central-west
        if 4.7 <= lon < 5.5 and lat < 52.2:
            return "Utrecht"
        # Flevoland: reclaimed polder (lat 52.2-52.6, lon 5.2-6.0)
        if lat >= 52.2 and 5.2 <= lon < 6.0:
            return "Flevoland"
        # Gelderland: east-central
        if lon >= 5.5:
            return "Gelderland"
        # Noord-Holland: north-west (Amsterdam metro extends to ~52.4)
        if lon < 5.2 and lat >= 52.2:
            return "Noord-Holland"
        # Default for central band
        return "Utrecht"

    # North (52.6-53.0)
    if lat < 53.0:
        if lon < 5.4:
            return "Noord-Holland"
        if lon < 6.0:
            return "Flevoland"
        if lon < 6.7:
            return "Overijssel"
        return "Drenthe"

    # Far north (53.0+) — Friesland (west) + Groningen (east)
    # Friesland extends further east than 5.7 (Leeuwarden 5.78, Dokkum 5.99)
    if lon < 6.0:
        return "Friesland"
    return "Groningen"


def _small_dso_from_geofence(lat: float, lon: float) -> str | None:
    """Return small regional DSO if lat/lon falls in a geofence, else None."""
    # Coteq Netbeheer — Almelo area (Overijssel)
    if 52.31 <= lat <= 52.42 and 6.60 <= lon <= 6.75:
        return "Coteq"
    # Rendo Netwerken — Zwolle+Steenwijk (Overijssel/Drenthe border)
    if 52.65 <= lat <= 52.85 and 5.95 <= lon <= 6.20:
        return "Rendo"
    # Westland Infra — Westland horticultural region (Zuid-Holland)
    if 51.98 <= lat <= 52.05 and 4.15 <= lon <= 4.28:
        return "Westland Infra"
    return None


def resolve_owner_from_region_jurisdiction(
    lat: float, lon: float, voltage_kv: float | None, osm_province: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance) tuple.

    Uses OSM addr:state= (province) if provided, otherwise lat/lon geofence.
    """
    is_tso = voltage_kv is not None and voltage_kv >= _TSO_THRESHOLD_KV
    if is_tso:
        return "TenneT", f"region_fallback_TSO_gte{_TSO_THRESHOLD_KV}kV"

    # Check small-DSO geofence first (they nest inside primary-DSO provinces)
    small = _small_dso_from_geofence(lat, lon)
    if small is not None:
        return small, f"region_fallback_small_DSO_{small}_geofence"

    # OSM province tag, else lat/lon
    province = None
    if osm_province:
        p = osm_province.strip()
        # Match to canonical name (case-insensitive)
        for canon in _PROVINCE_TO_DSO.keys():
            if p.lower() == canon.lower() or p.lower() == canon.split(" (")[0].lower():
                province = canon
                break

    if province is None:
        province = _province_from_lat_lon(lat, lon)

    if province is None:
        return None, "region_unresolved_no_geofence_match"

    dso = _PROVINCE_TO_DSO.get(province)
    if dso is None:
        return None, f"region_fallback_province_{province}_no_dso_mapping"

    return dso, f"region_fallback_{province.replace(' ', '_')}_{dso}"


# ── Discipline #36 with Netherlands 100m default tolerance ───────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Netherlands bounds filter with 100m default tolerance.

    Netherlands bounds already CLEAN pre-workstream. 100m adequate.
    """
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "netherlands", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="netherlands", tolerance_km=tolerance_km
    )


# ── Audit sidecar (§5ter contract) ───────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "netherlands/v4_23-ingestion-audit-netherlands-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = NETHERLANDS_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("nl-"):
        slug = slug[len("nl-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-netherlands-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Netherlands ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/netherlands/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: netherlands",
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
        "  step_2_fetch: netherlands/v4_23-ingestion-audit-netherlands-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: netherlands/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    NETHERLANDS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return NETHERLANDS_CACHE_DIR / f"{key}{ext}"


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
    "NETHERLANDS_BOUNDS_JSON",
    "NETHERLANDS_TOLERANCE_JSON",
    "NETHERLANDS_DATA_DIR",
    "NETHERLANDS_CACHE_DIR",
]
