"""
SSI Pipeline — Chile v4.23 ingestion, shared base layer.

Country-parallel of Belgium/Netherlands _base.py. Fifth v4.23 fallback class —
latitude-band region geofence exploiting Chile's narrow 4,400 km N-S strip
topology.

Chile specifics:
  - Fragmented transmission ownership (≥110 kV):
      TRANSELEC (~60% market share — largest EHV owner)
      ISA InterChile (~40% — 500 kV backbone)
      Various IPPs + subsidiaries (small share)
  - 6 primary DSOs by lat-band region:
      Metropolitana → Enel Distribución (formerly Chilectra pre-2018)
      Valparaíso → Chilquinta
      Araucanía → Frontel (Grupo SAESA)
      Los Ríos + Los Lagos → SAESA
      Aysén → Edelaysén (SAESA subsidiary)
      Magallanes → Edelmag
  - CGE Distribución nationwide default (largest by area, ~33%):
      Arica y Parinacota + Tarapacá + Antofagasta + Atacama + Coquimbo +
      O'Higgins + Maule + Ñuble + Biobío
  - DSO alias normalisation:
      Chilectra → Enel Distribución (pre-2018 Enel acquisition)
      ELECDA/EMELAT/CONAFE → CGE Distribución (subsidiary consolidation)
  - Metropolitana/Valparaíso lat overlap resolved via longitude
    (Metro inland lon > -70.5; Valparaíso coastal lon < -71.5)
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
CHILE_BOUNDS_JSON = REPO_ROOT / "chile" / "bounds.json"
CHILE_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
CHILE_DATA_DIR = PIPELINE_DIR / "data" / "chile"
CHILE_CACHE_DIR = CHILE_DATA_DIR / "_osm_cache"


# ── DSO alias normalisation (case-insensitive) ───────────────────────────
_DNSP_ALIAS_MAP = {
    # Enel Distribución consolidation
    "chilectra": "Enel Distribución",
    "enel chile": "Enel Distribución",
    "enel distribucion": "Enel Distribución",  # unaccented variant
    "enel distribución": "Enel Distribución",
    # CGE Distribución subsidiary consolidation
    "elecda": "CGE Distribución",  # Antofagasta subsidiary
    "emelat": "CGE Distribución",  # Atacama subsidiary
    "conafe": "CGE Distribución",  # Coquimbo — Compañía Nacional de Fuerza Eléctrica
    "cge": "CGE Distribución",
    "cge distribucion": "CGE Distribución",
    "cge distribución": "CGE Distribución",
    # SAESA grupo consolidation
    "saesa grupo": "SAESA",
    "grupo saesa": "SAESA",
    "saesa": "SAESA",
    # Canonical self-mapping (catch case variants — Netherlands lesson learned)
    "edelaysen": "Edelaysén",
    "edelaysén": "Edelaysén",
    "edelmag": "Edelmag",
    "frontel": "Frontel",
    "chilquinta": "Chilquinta",
    "transelec": "TRANSELEC",
    "isa interchile": "ISA InterChile",
    "interchile": "ISA InterChile",
    # TSO (grid operator, not owner)
    "coordinador electrico nacional": "CEN",
    "coordinador eléctrico nacional": "CEN",
    "cen": "CEN",
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive alias normalisation."""
    if not owner:
        return owner
    key = owner.strip().lower()
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── Latitude-band region → DSO ───────────────────────────────────────────
#
# Chile is a narrow 4,400 km N-S strip. Latitude alone resolves most
# regions cleanly; longitude disambiguation only needed for
# Metropolitana/Valparaíso overlap band.
#
# Voltage threshold: 110 kV. Above → TRANSELEC (dominant EHV owner,
# ~60% market share — majority-default per Convention #56 visibly-honest;
# ISA InterChile owns remaining ~40% 500 kV backbone).

_TSO_THRESHOLD_KV = 110.0

# (lat_north, lat_south, region, dso)  — lats are negative; north > south
_LATITUDE_BANDS = [
    (-17.5, -18.6,  "Arica y Parinacota", "CGE Distribución"),
    (-18.6, -21.5,  "Tarapacá",           "CGE Distribución"),
    (-21.5, -26.0,  "Antofagasta",        "CGE Distribución"),
    (-26.0, -29.5,  "Atacama",            "CGE Distribución"),
    (-29.5, -32.3,  "Coquimbo",           "CGE Distribución"),
    # Valparaíso/Metropolitana overlap band handled specially via lon disambiguation
    (-33.5, -35.0,  "O'Higgins",          "CGE Distribución"),
    (-35.0, -36.5,  "Maule",              "CGE Distribución"),
    (-36.5, -37.3,  "Ñuble",              "CGE Distribución"),
    (-37.3, -38.5,  "Biobío",             "CGE Distribución"),
    (-38.5, -39.7,  "Araucanía",          "Frontel"),
    (-39.7, -40.7,  "Los Ríos",           "SAESA"),
    (-40.7, -44.0,  "Los Lagos",          "SAESA"),
    (-44.0, -49.5,  "Aysén",              "Edelaysén"),
    (-49.5, -56.0,  "Magallanes",         "Edelmag"),
]


def _region_from_lat_lon(lat: float, lon: float) -> tuple[str | None, str | None]:
    """Return (region_name, dso) for a lat/lon.

    Metropolitana/Valparaíso overlap band (-32.3 to -33.5) resolved by lon:
      lon >= -71.0 → Metropolitana (Santiago inland)
      lon <  -71.0 → Valparaíso (coastal)
    """
    # Special-case the Metro/Valparaíso overlap first
    if -33.5 <= lat < -32.3:
        if lon >= -71.0:
            return ("Metropolitana", "Enel Distribución")
        return ("Valparaíso", "Chilquinta")

    # Standard lat-band lookup
    for lat_north, lat_south, region, dso in _LATITUDE_BANDS:
        # Note: lats are negative; lat_north > lat_south (both negative)
        if lat_south <= lat < lat_north:
            return (region, dso)

    return (None, None)


def resolve_owner_from_region_jurisdiction(
    lat: float, lon: float, voltage_kv: float | None, osm_region: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance) tuple.

    ≥110 kV → TRANSELEC (majority-default; ~60% market share).
    <110 kV → region DSO via lat-band geofence + Metro/Valpo lon disambiguation.
    """
    is_tso = voltage_kv is not None and voltage_kv >= _TSO_THRESHOLD_KV
    if is_tso:
        return (
            "TRANSELEC",
            f"region_fallback_TSO_gte{_TSO_THRESHOLD_KV}kV_majority_default_transelec_60pct",
        )

    # Try OSM region tag, else lat/lon
    region = None
    dso = None
    if osm_region:
        r_low = osm_region.strip().lower()
        # Match to canonical region name (case-insensitive, unaccented tolerance)
        for _, _, canon, canon_dso in _LATITUDE_BANDS:
            if canon.lower() == r_low or canon.lower().replace("ó", "o").replace("í", "i") == r_low.replace("ó", "o").replace("í", "i"):
                region = canon
                dso = canon_dso
                break
        # Metropolitana/Valparaíso special-case
        if region is None:
            if "metropolit" in r_low or "santiago" in r_low:
                region = "Metropolitana"
                dso = "Enel Distribución"
            elif "valpara" in r_low:
                region = "Valparaíso"
                dso = "Chilquinta"

    if region is None:
        region, dso = _region_from_lat_lon(lat, lon)

    if region is None or dso is None:
        return None, "region_unresolved_no_geofence_match"

    # Normalise region name to safe provenance token
    region_token = region.replace(" ", "_").replace("'", "").replace("ñ", "n")
    return dso, f"region_fallback_{region_token}_{dso.replace(' ', '_')}"


# ── Discipline #36 with Chile 100m default tolerance ─────────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Chile bounds filter with 100m default tolerance.

    Chile bounds already remediated (task #64 Mode 3 partial — 130
    Argentinian Patagonia substations removed). 100m adequate.
    """
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(CHILE_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("chile", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="chile", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "chile/v4_23-ingestion-audit-chile-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = CHILE_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("cl-"):
        slug = slug[len("cl-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-chile-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Chile ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/chile/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: chile",
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
        "  step_2_fetch: chile/v4_23-ingestion-audit-chile-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: chile/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    CHILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return CHILE_CACHE_DIR / f"{key}{ext}"


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
    "CHILE_BOUNDS_JSON",
    "CHILE_TOLERANCE_JSON",
    "CHILE_DATA_DIR",
    "CHILE_CACHE_DIR",
]
