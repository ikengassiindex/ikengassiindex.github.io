"""
SSI Pipeline — Colombia v4.23 ingestion, shared base layer.

Sixth region-jurisdiction × voltage-class instance with LARGEST DSO cardinality
yet (~30 DSOs). Colombia specifics:
  - ISA state-linked TSO ≥220 kV + XM SA ESP system operator (non-owner)
  - ~30 regional distributors mapped by department name (baseline 100% populated)
  - Historical alias handling: Electricaribe (legacy) → Air-e or Afinia
    disambiguated by department, not by alias alone
  - Spanish + accented-char normalisation for department names (Nariño, Bogotá)
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
COLOMBIA_BOUNDS_JSON = REPO_ROOT / "colombia" / "bounds.json"
COLOMBIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
COLOMBIA_DATA_DIR = PIPELINE_DIR / "data" / "colombia"
COLOMBIA_CACHE_DIR = COLOMBIA_DATA_DIR / "_osm_cache"


# ── DSO alias normalisation (case-insensitive + NFC + accent-strip) ──────
_DNSP_ALIAS_MAP = {
    # ISA + XM variants (state TSO + system operator)
    "isa": "ISA",
    "isa - interconexion electrica": "ISA",
    "interconexion electrica": "ISA",
    "interconexion electrica s.a.": "ISA",
    "interconexion electrica s.a. esp": "ISA",
    "isa esp": "ISA",
    "xm": "XM SA ESP (System Operator)",
    "xm sa esp": "XM SA ESP (System Operator)",
    "xm compania de expertos en mercados": "XM SA ESP (System Operator)",
    # EPM (Antioquia)
    "epm": "EPM",
    "empresas publicas de medellin": "EPM",
    "empresas publicas medellin": "EPM",
    "epm esp": "EPM",
    "epm e.s.p.": "EPM",
    # Enel-Codensa (Bogotá + Cundinamarca)
    "codensa": "Enel-Codensa",
    "codensa s.a.": "Enel-Codensa",
    "codensa esp": "Enel-Codensa",
    "enel": "Enel-Codensa",  # OSM standalone variant surfaced 2026-07-13
    "enel s.a.": "Enel-Codensa",
    "enel codensa": "Enel-Codensa",
    "enel-codensa": "Enel-Codensa",
    "enel colombia": "Enel-Codensa",
    "enel colombia s.a.": "Enel-Codensa",
    "enel emgesa": "Enel-Codensa",  # generation arm; grid is Codensa
    "emgesa": "Enel-Codensa",
    # Emcali (Cali metro)
    "emcali": "Emcali",
    "empresas municipales de cali": "Emcali",
    # EPSA (rest of Valle del Cauca)
    "epsa": "EPSA",
    "empresa de energia del pacifico": "EPSA",
    "celsia": "EPSA",  # parent brand
    "celsia colombia": "EPSA",
    # CENS (Norte de Santander)
    "cens": "CENS",
    "centrales electricas del norte de santander": "CENS",
    "centrales electricas de norte de santander": "CENS",
    # EBSA (Boyacá)
    "ebsa": "EBSA",
    "empresa de energia de boyaca": "EBSA",
    # Air-e (Atlántico + Magdalena + La Guajira)
    "air-e": "Air-e",
    "aire": "Air-e",
    "air-e sas esp": "Air-e",
    "air e sas esp": "Air-e",
    # Afinia (Bolívar + Cesar + Córdoba + Sucre)
    "afinia": "Afinia",
    "afinia esp": "Afinia",
    "afinia sas esp": "Afinia",
    # Cedenar (Nariño)
    "cedenar": "Cedenar",
    "centrales electricas de narino": "Cedenar",
    # Essa (Santander)
    "essa": "Essa",
    "electrificadora de santander": "Essa",
    "electrificadora santander": "Essa",
    # Chec (Eje Cafetero — Caldas + Quindío + Risaralda)
    "chec": "Chec",
    "central hidroelectrica de caldas": "Chec",
    "chec grupo epm": "Chec",
    # Electrohuila (Huila)
    "electrohuila": "Electrohuila",
    "electrificadora del huila": "Electrohuila",
    # Enertolima (Tolima)
    "enertolima": "Enertolima",
    "electrificadora del tolima": "Enertolima",
    # Enerca (Casanare)
    "enerca": "Enerca",
    "energia de casanare": "Enerca",
    # Enelar (Arauca)
    "enelar": "Enerca-Enelar",
    "energia de arauca": "Enerca-Enelar",
    # Emsa (Meta + Guaviare + Vichada + Vaupés + Guainía)
    "emsa": "Emsa",
    "electrificadora del meta": "Emsa",
    "empresa electrificadora del meta": "Emsa",
    # Electrocaqueta (Caquetá)
    "electrocaqueta": "Electrocaqueta",
    "electrificadora del caqueta": "Electrocaqueta",
    # DisPac (Chocó)
    "dispac": "DisPac",
    "distribuidora del pacifico": "DisPac",
    # CEO (Cauca)
    "ceo": "CEO",
    "compania energetica de occidente": "CEO",
    "cedelca": "CEO",  # legacy predecessor
    # Amazonas (isolated grid, ICEL / Ingas)
    "amazonas": "Amazonas",
    "empresa de energia amazonas": "Amazonas",
    # Sopesa (Islas de San Andrés y Providencia)
    "sopesa": "Sopesa",
    "sociedad productora de energia de san andres": "Sopesa",
    # GEB (Bogotá TSO — transmission + minor DSO overlap with ENEL)
    "geb": "GEB",
    "grupo energia bogota": "GEB",
    "empresa de energia de bogota": "GEB",
    "eeb": "GEB",
    # Ecopetrol (industrial captive — oil/gas)
    "ecopetrol": "Ecopetrol",
    # Legacy Electricaribe (route via department)
    "electricaribe": "Electricaribe-legacy",
    "electricosta": "Air-e-legacy",
}


def _strip_accents(s: str) -> str:
    """Strip diacritics for lookup keys (Nariño → narino, Bogotá → bogota)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _normalise_key(s: str) -> str:
    """NFC + strip + lower-case + accent-strip for case-insensitive lookup."""
    return _strip_accents(unicodedata.normalize("NFC", s).strip().lower())


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC + accent-strip alias normalisation."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── ISA TSO voltage threshold ────────────────────────────────────────────
# ISA operates ALL 220+ kV transmission (500 + 230 + 220 kV backbone).
# Below 220 kV → DSO via department map.
_ISA_TSO_MIN_KV = 220.0


# ── Department name → DSO map (~30 departments) ──────────────────────────
# Keys are accent-stripped lower-case for lookup consistency.
_DEPARTMENT_TO_DSO = {
    "antioquia": "EPM",
    "bogota": "Enel-Codensa",
    "bogota d.c.": "Enel-Codensa",
    "bogota d c": "Enel-Codensa",
    "atlantico": "Air-e",
    "magdalena": "Air-e",
    "la-guajira": "Air-e",
    "guajira": "Air-e",  # OSM variant
    "la guajira": "Air-e",
    "bolivar": "Afinia",
    "cesar": "Afinia",
    "cordoba": "Afinia",
    "sucre": "Afinia",
    "santander": "Essa",
    "norte-de-santander": "CENS",
    "norte de santander": "CENS",
    "boyaca": "EBSA",
    "caldas": "Chec",
    "quindio": "Chec",
    "risaralda": "Chec",
    "huila": "Electrohuila",
    "tolima": "Enertolima",
    "narino": "Cedenar",  # accent-stripped Nariño
    "cauca": "CEO",
    "casanare": "Enerca",
    "meta": "Emsa",
    "arauca": "Enerca-Enelar",
    "guaviare": "Emsa",
    "putumayo": "Emsa",  # falls back to CEDENAR territory too
    "caqueta": "Electrocaqueta",
    "choco": "DisPac",
    "amazonas": "Amazonas",
    "vichada": "Emsa",
    "vaupes": "Emsa",
    "guainia": "Emsa",
    "san-andres": "Sopesa",
    "san andres": "Sopesa",
    "san andres y providencia": "Sopesa",
    "archipielago-de-san-andres": "Sopesa",
    # Cundinamarca: overlaps with Enel-Codensa (Bogotá suburbs) — see Cali metro geofence
    "cundinamarca": "Enel-Codensa",
    # Valle del Cauca: overlaps with Emcali (Cali metro geofence)
    "valle-del-cauca": "EPSA",
    "valle del cauca": "EPSA",
}


def _dso_from_department(dept: str | None) -> str | None:
    """Return DSO name if department name is known."""
    if not dept:
        return None
    key = _strip_accents(str(dept).strip().lower())
    return _DEPARTMENT_TO_DSO.get(key)


# ── Cali metro geofence (Emcali carve-out from Valle del Cauca EPSA) ─────
def _cali_metro_bbox_check(lat: float, lon: float) -> bool:
    """Check if lat/lon falls in Cali metro (Emcali territory)."""
    return 3.30 <= lat <= 3.60 and -76.65 <= lon <= -76.40


def resolve_owner_from_department_map(
    voltage_kv: float | None,
    department: str | None,
    lat: float,
    lon: float,
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Layer 1: ISA TSO threshold ≥220 kV → ISA.
    Layer 2: DSO via department-name lookup (baseline 100% populated).
    Layer 3: Cali metro Emcali carve-out (within Valle del Cauca).
    Layer 4: ISA state-utility default (Convention #56 for unresolved).
    """
    # Layer 1: TSO threshold ≥220 kV → ISA (backbone 500/230/220 kV)
    if voltage_kv is not None and voltage_kv >= _ISA_TSO_MIN_KV:
        return "ISA", "region_jurisdiction_fallback_ISA_TSO_threshold_ge_220kv"

    # Layer 3: Cali metro Emcali carve-out (must fire before Layer 2 for Valle del Cauca)
    if _cali_metro_bbox_check(lat, lon):
        return "Emcali", "region_jurisdiction_fallback_Emcali_cali_metro_geofence"

    # Layer 2: DSO via department name
    dso = _dso_from_department(department)
    if dso is not None:
        return dso, f"region_jurisdiction_fallback_{dso.replace(' ', '_').replace('-', '_')}_via_department_{_strip_accents(str(department).lower())}"

    # Layer 4: ISA state-utility default (Convention #56 visibly-honest for unmapped)
    return "ISA", "region_jurisdiction_fallback_ISA_default_state_utility"


# ── Discipline #36 with Colombia 100m default tolerance ──────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Colombia bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(COLOMBIA_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("colombia", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="colombia", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "colombia/v4_23-ingestion-audit-colombia-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = COLOMBIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("co-"):
        slug = slug[len("co-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-colombia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Colombia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/colombia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: colombia",
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
        "  step_2_fetch: colombia/v4_23-ingestion-audit-colombia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: colombia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    COLOMBIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return COLOMBIA_CACHE_DIR / f"{key}{ext}"


__all__ = [
    "SubstationRecord",
    "TransmissionLineRecord",
    "IngestionResult",
    "apply_bounds_filter",
    "assert_line_parity",
    "emit_audit_sidecar",
    "cache_path_for",
    "now_utc_iso",
    "resolve_owner_from_department_map",
    "normalise_owner_alias",
    "_dso_from_department",
    "COLOMBIA_BOUNDS_JSON",
    "COLOMBIA_TOLERANCE_JSON",
    "COLOMBIA_DATA_DIR",
    "COLOMBIA_CACHE_DIR",
]
