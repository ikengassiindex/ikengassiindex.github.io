"""
SSI Pipeline — Israel v4.23 ingestion, shared base layer.

Third pure-monopoly-class instance. Israel specifics:
  - IEC state-owned monopoly ~99% + TSO ≥161 kV (unique low HV threshold)
  - Noga TSO SO (non-owner of grid infrastructure, spun out 2020-2021)
  - Minor private IPPs: OPC / Dorad / Delek / Enlight
  - Industrial captives: Ashdod Refineries / Israel Chemicals (Dead Sea Works)
  - Hebrew Unicode alias normalisation with NFC + case-insensitive lookup
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
ISRAEL_BOUNDS_JSON = REPO_ROOT / "israel" / "bounds.json"
ISRAEL_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
ISRAEL_DATA_DIR = PIPELINE_DIR / "data" / "israel"
ISRAEL_CACHE_DIR = ISRAEL_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (case-insensitive + Unicode NFC) ───────────
# Keys are Unicode-normalised (NFC) lower-case strings; values are canonical.
_DNSP_ALIAS_MAP = {
    # IEC variants (English + Hebrew + Ltd forms)
    "iec": "IEC",
    "iec ltd": "IEC",
    "iec ltd.": "IEC",
    "israel electric": "IEC",
    "israel electric corporation": "IEC",
    "israel electric company": "IEC",  # OSM Israeli-English variant surfaced 2026-07
    "israel electric corp": "IEC",
    "israel electric corp.": "IEC",
    "the israel electric corporation": "IEC",
    "חברת חשמל לישראל": "IEC",  # Hebrew formal name
    "חברת חשמל לישראל בעמ": "IEC",  # with Ltd suffix (bet-ayin-mem)
    "חברת החשמל לישראל": "IEC",  # with definite article
    "חברת החשמל": "IEC",  # Hebrew "The Electric Company" (definite article, no לישראל) — OSM surfaced 2026-07
    "חברת חשמל": "IEC",             # Hebrew short
    "חשמל": "IEC",                   # Hebrew shortest (context: energy provider)
    # Noga (system operator, non-owner)
    "noga": "Noga (System Operator)",
    "נגה": "Noga (System Operator)",
    "נגה מנהל המערכת": "Noga (System Operator)",
    # OPC Energy
    "opc": "OPC Energy",
    "opc energy": "OPC Energy",
    "opc energy ltd": "OPC Energy",
    "opc energy ltd.": "OPC Energy",
    "opc אנרגיה": "OPC Energy",
    # Dorad Energy
    "dorad": "Dorad Energy",
    "dorad energy": "Dorad Energy",
    "dorad energy ltd": "Dorad Energy",
    "dorad energy ltd.": "Dorad Energy",
    "דורד": "Dorad Energy",
    "דורד אנרגיה": "Dorad Energy",
    # Delek variants
    "delek israel electricity": "Delek Israel Electricity",
    "delek electricity": "Delek Israel Electricity",
    "דלק אנרגיה": "Delek Israel Electricity",
    # Enlight Renewable Energy
    "enlight": "Enlight Renewable Energy",
    "enlight renewable": "Enlight Renewable Energy",
    "enlight renewable energy": "Enlight Renewable Energy",
    "אנלייט": "Enlight Renewable Energy",
    # Industrial captives — Ashdod Refineries (Oil Refineries Ltd)
    "ashdod refineries": "Ashdod Refineries",
    "orl": "Ashdod Refineries",
    "oil refineries": "Ashdod Refineries",
    "בזן": "Ashdod Refineries",  # Hebrew short for Bazan / ORL
    # Industrial captives — Israel Chemicals / Dead Sea Works
    "icl": "Israel Chemicals",
    "israel chemicals": "Israel Chemicals",
    "israel chemicals ltd": "Israel Chemicals",
    "dead sea works": "Israel Chemicals",
    "מפעלי ים המלח": "Israel Chemicals",
    "כים": "Israel Chemicals",  # ICL Hebrew
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── IEC TSO voltage threshold ────────────────────────────────────────────
# Israel's UNIQUELY LOW TSO threshold at 161 kV (US-standard heritage).
# All transmission at 161 + 400 kV = IEC by construction.
_IEC_TSO_MIN_KV = 161.0


def resolve_owner_from_monopoly_default(
    voltage_kv: float | None, lat: float, lon: float
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Israel is a pure monopoly (IEC ~99%). No geofence overlay needed —
    private IPPs surface via direct OSM operator= tag rather than
    territorial mapping.

    Layer 1: IEC TSO threshold ≥161 kV → IEC.
    Layer 2: IEC monopoly default (all remaining territory).
    """
    # Layer 1: TSO threshold ≥161 kV → IEC
    if voltage_kv is not None and voltage_kv >= _IEC_TSO_MIN_KV:
        return "IEC", "monopoly_fallback_IEC_TSO_threshold_ge_161kv"

    # Layer 2: IEC monopoly default (all remaining territory ≥99% coverage)
    return "IEC", "monopoly_fallback_IEC_default_state_monopoly_99pct_coverage"


# ── Discipline #36 with Israel 100m default tolerance ────────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Israel bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        tolerance_km = resolve_boundary_tolerance_km(
            "israel", module_fallback=0.1
        )
    return _apply_bounds_generic(
        records, country_slug="israel", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "israel/v4_23-ingestion-audit-israel-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = ISRAEL_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("il-"):
        slug = slug[len("il-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-israel-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Israel ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/israel/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: israel",
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
        "  step_2_fetch: israel/v4_23-ingestion-audit-israel-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: israel/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    ISRAEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return ISRAEL_CACHE_DIR / f"{key}{ext}"


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
    "ISRAEL_BOUNDS_JSON",
    "ISRAEL_TOLERANCE_JSON",
    "ISRAEL_DATA_DIR",
    "ISRAEL_CACHE_DIR",
]
