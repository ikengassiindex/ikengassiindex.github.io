"""
SSI Pipeline — Hungary v4.23 ingestion, shared base layer.

Country-parallel of Belgium/Netherlands/Chile _base.py. Reuses country-agnostic
dataclasses from Canada _base and overlays Hungary-specific paths + tolerance
+ 2-DSO consolidation fallback logic.

Hungary specifics:
  - 1 TSO: MAVIR (state-owned, operates 220/400 kV network)
  - Post-2020 E.ON Hungária consolidation of all Hungarian DSOs:
      ELMŰ-ÉMÁSZ:      Budapest metro + Pest + Northeast counties
                       (traditional brand preserved by E.ON)
      E.ON Hungária:   Transdanubia + Southern Great Plain
                       (all former E.ON regional + DÉMÁSZ + Innogy)
  - NUTS-3 code region mapping (HU110 Budapest through HU333 Csongrád)
  - Historical alias normalisation:
      DÉMÁSZ → E.ON Hungária (post-2018 acquisition)
      Innogy → E.ON Hungária (post-2019 rebrand)
      ELMŰ ↔ ELMÜ, ÉMÁSZ (accent variants)
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
HUNGARY_BOUNDS_JSON = REPO_ROOT / "hungary" / "bounds.json"
HUNGARY_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
HUNGARY_DATA_DIR = PIPELINE_DIR / "data" / "hungary"
HUNGARY_CACHE_DIR = HUNGARY_DATA_DIR / "_osm_cache"


# ── DSO alias normalisation (case-insensitive) ───────────────────────────
_DNSP_ALIAS_MAP = {
    # ELMŰ-ÉMÁSZ consolidation
    "elmű": "ELMŰ-ÉMÁSZ",
    "elmü": "ELMŰ-ÉMÁSZ",  # accent variant
    "elmu": "ELMŰ-ÉMÁSZ",  # unaccented
    "budapesti elektromos művek": "ELMŰ-ÉMÁSZ",
    "budapesti elektromos muvek": "ELMŰ-ÉMÁSZ",
    "émász": "ELMŰ-ÉMÁSZ",
    "emasz": "ELMŰ-ÉMÁSZ",
    "északmagyarországi áramszolgáltató": "ELMŰ-ÉMÁSZ",
    "elmű-émász": "ELMŰ-ÉMÁSZ",
    "elmu-emasz": "ELMŰ-ÉMÁSZ",
    # E.ON Hungária consolidation
    "démász": "E.ON Hungária",
    "demasz": "E.ON Hungária",
    "e.on észak-dunántúli": "E.ON Hungária",
    "e.on dél-dunántúli": "E.ON Hungária",
    "e.on tiszántúli": "E.ON Hungária",
    "e.on áramhálózati": "E.ON Hungária",
    "e.on aramhalozati": "E.ON Hungária",
    "e.on hungária": "E.ON Hungária",
    "e.on hungaria": "E.ON Hungária",
    "innogy": "E.ON Hungária",
    "e.on": "E.ON Hungária",
    "eon": "E.ON Hungária",
    # MAVIR canonical
    "mavir": "MAVIR",
    "mavir zrt": "MAVIR",
    "mavir zrt.": "MAVIR",
}


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive alias normalisation with accented character support."""
    if not owner:
        return owner
    key = owner.strip().lower()
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 code → DSO mapping ────────────────────────────────────────────
# ELMŰ-ÉMÁSZ scope: Budapest + Pest + Northern Hungary + Northern Great Plain
_ELMU_EMASZ_NUTS3 = {
    "HU110",  # Budapest
    "HU120",  # Pest
    "HU311",  # Borsod-Abaúj-Zemplén
    "HU312",  # Heves
    "HU313",  # Nógrád
    "HU321",  # Hajdú-Bihar
    "HU322",  # Jász-Nagykun-Szolnok
    "HU323",  # Szabolcs-Szatmár-Bereg
}

# E.ON Hungária scope: Transdanubia + Southern Great Plain
_EON_HUNGARIA_NUTS3 = {
    "HU211",  # Fejér
    "HU212",  # Komárom-Esztergom
    "HU213",  # Veszprém
    "HU221",  # Győr-Moson-Sopron
    "HU222",  # Vas
    "HU223",  # Zala
    "HU231",  # Baranya
    "HU232",  # Somogy
    "HU233",  # Tolna
    "HU331",  # Bács-Kiskun
    "HU332",  # Békés
    "HU333",  # Csongrád
}


# ── Voltage threshold ────────────────────────────────────────────────────
# MAVIR operates 220/400 kV EHV backbone. 132 kV is Hungarian HV distribution
# tier — DSO-owned (307 subs in baseline vs 46 at 400 kV + 12 at 220 kV).
# Threshold at 200 kV catches only true EHV transmission (220/400).
_TSO_THRESHOLD_KV = 200.0


# ── Coarse county-name lat/lon geofence (for OSM addr:state without NUTS-3) ─
# Very rough county centroids for lat/lon → NUTS-3 fallback
def _nuts3_from_lat_lon(lat: float, lon: float) -> str | None:
    """Return NUTS-3 code from lat/lon (coarse county bbox heuristic).

    Approximate but adequate for DSO fallback. Cross-border filter handles
    edges (Discipline #36).
    """
    # Budapest metro (small tight bubble)
    if 47.35 <= lat <= 47.60 and 18.95 <= lon <= 19.35:
        return "HU110"

    # Pest county (surrounds Budapest, larger bubble)
    if 47.10 <= lat <= 47.85 and 18.50 <= lon <= 19.85:
        return "HU120"

    # Northeast (Borsod-Abaúj-Zemplén / Heves / Nógrád / Northern Great Plain)
    if lat >= 47.5 and lon >= 19.5:
        # North (border with Slovakia)
        if lat >= 48.0:
            if lon < 20.5:
                return "HU313"  # Nógrád
            if lon < 21.0:
                return "HU312"  # Heves
            return "HU311"  # Borsod-Abaúj-Zemplén
        # Northern Great Plain
        if lon >= 21.5:
            return "HU323"  # Szabolcs-Szatmár-Bereg
        if lon >= 20.5:
            return "HU321"  # Hajdú-Bihar
        return "HU322"  # Jász-Nagykun-Szolnok

    # Transdanubia (west of Danube — lon < 19.0)
    if lon < 19.0:
        # Western Transdanubia (west of Balaton)
        if lon < 17.5:
            if lat >= 47.3:
                return "HU221"  # Győr-Moson-Sopron
            if lat >= 46.7:
                return "HU222"  # Vas
            return "HU223"  # Zala
        # Central Transdanubia
        if lat >= 47.3:
            return "HU212"  # Komárom-Esztergom
        if lat >= 46.9:
            return "HU211"  # Fejér
        if lat >= 46.7:
            return "HU213"  # Veszprém
        # Southern Transdanubia
        if lon < 18.0:
            return "HU232"  # Somogy
        if lon < 18.5:
            return "HU231"  # Baranya
        return "HU233"  # Tolna

    # Southern Great Plain (east + south)
    if lat < 47.0:
        if lon < 20.0:
            return "HU331"  # Bács-Kiskun
        if lon < 20.7:
            return "HU333"  # Csongrád
        return "HU332"  # Békés

    # Central/east fallback
    return "HU322"  # Jász-Nagykun-Szolnok


def resolve_owner_from_region_jurisdiction(
    lat: float, lon: float, voltage_kv: float | None, osm_region: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance) tuple.

    ≥120 kV → MAVIR (TSO). <120 kV → DSO via NUTS-3 → 2-DSO mapping.
    """
    is_tso = voltage_kv is not None and voltage_kv >= _TSO_THRESHOLD_KV
    if is_tso:
        return "MAVIR", f"region_fallback_TSO_gte{_TSO_THRESHOLD_KV}kV"

    # Try OSM NUTS-3 region tag first (rare in OSM but ideal when present)
    nuts3 = None
    if osm_region:
        r = osm_region.strip().upper()
        if r.startswith("HU") and len(r) in (5, 6):
            nuts3 = r[:5]  # HU### form

    if nuts3 is None:
        nuts3 = _nuts3_from_lat_lon(lat, lon)

    if nuts3 is None:
        return None, "region_unresolved_no_geofence_match"

    if nuts3 in _ELMU_EMASZ_NUTS3:
        return "ELMŰ-ÉMÁSZ", f"region_fallback_{nuts3}_ELMU_EMASZ"
    if nuts3 in _EON_HUNGARIA_NUTS3:
        return "E.ON Hungária", f"region_fallback_{nuts3}_EON_Hungaria"

    # Should not reach here — all 20 NUTS-3 codes covered
    return None, f"region_fallback_{nuts3}_no_dso_mapping"


# ── Discipline #36 with Hungary 100m default tolerance ───────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Hungary bounds filter with 100m default tolerance.

    Hungary bounds already CLEAN pre-workstream. 100m adequate.
    """
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "hungary", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="hungary", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "hungary/v4_23-ingestion-audit-hungary-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = HUNGARY_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("hu-"):
        slug = slug[len("hu-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-hungary-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Hungary ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/hungary/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: hungary",
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
        "  step_2_fetch: hungary/v4_23-ingestion-audit-hungary-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: hungary/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    HUNGARY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return HUNGARY_CACHE_DIR / f"{key}{ext}"


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
    "HUNGARY_BOUNDS_JSON",
    "HUNGARY_TOLERANCE_JSON",
    "HUNGARY_DATA_DIR",
    "HUNGARY_CACHE_DIR",
]
