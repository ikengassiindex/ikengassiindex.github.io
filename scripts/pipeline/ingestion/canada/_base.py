"""
SSI Pipeline — Canada v4.23 ingestion, shared base layer.

Responsibilities:
  - Normalised dataclasses (SubstationRecord + TransmissionLineRecord + IngestionResult)
    consistent across the four Canada source connectors.
  - Discipline #36 point-in-polygon Canada-bounds filter (delegates to
    scripts.pipeline.utils.geo).
  - Discipline #41 substation-line parity assertion (every substation must
    connect to ≥1 line; every line must have both endpoints inside the
    substation registry OR be tagged as an outbound-to-cross-border boundary).
  - Per-source audit-YAML sidecar emission per METHODOLOGY_DISCIPLINES.md §5ter.

Consumer contract: each connector's fetch_*() function returns an IngestionResult.
The downstream federation layer (Step 3 follow-on) merges IngestionResults across
CanVec (federal), NACEI (strategic), YEC (Yukon), NS-NSTDB (Nova Scotia), and
emits the enriched substation payload into canada/ssi-data.json.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = PIPELINE_DIR.parent.parent
CANADA_BOUNDS_JSON = REPO_ROOT / "canada" / "bounds.json"
CANADA_DATA_DIR = PIPELINE_DIR / "data" / "canada"
CANADA_CACHE_DIR = CANADA_DATA_DIR / "_canvec_cache"    # raw fetch cache (SHA-256-keyed)


# ── Dataclasses ──────────────────────────────────────────────────────────
@dataclass
class SubstationRecord:
    """Normalised substation record across all Canada source connectors.

    Federal CanVec Res_MGT only populates (source_id, latitude, longitude,
    horiz_accuracy_min/max, temporal_extent_min/max, feature_id).  Provincial
    supplementary sources populate voltage_kv + owner + operator_station_name
    where available.
    """
    source_id: str                          # e.g. "CA-C1-canvec-resmgt"
    feature_id: str                         # publisher-assigned canonical ID
    latitude: float                         # WGS84
    longitude: float                        # WGS84
    voltage_kv: float | None = None         # incoming voltage (kV); None at CanVec federal layer
    voltage_out_kv: float | None = None     # outgoing voltage (kV); YEC populates
    owner: str | None = None                # utility owner name (YEC/BC-Hydro/etc.)
    operator_station_name: str | None = None  # publisher-assigned name
    community: str | None = None            # nearest community (YEC populates)
    is_transmission_station: bool | None = None  # YEC TRANSMISSION_IND
    is_switching_station: bool | None = None
    is_converter_station: bool | None = None
    lines_in_count: int | None = None       # YEC LINES_IN_NUM
    lines_out_count: int | None = None      # YEC LINES_OUT_NUM
    horiz_accuracy_min_m: float | None = None
    horiz_accuracy_max_m: float | None = None
    temporal_extent_min: str | None = None  # ISO-8601 or "YYYY-MM-DD"
    temporal_extent_max: str | None = None
    raw_attributes: dict[str, Any] = field(default_factory=dict)  # source-native record

    def audit_key(self) -> str:
        """Stable key for cross-source deduplication + Discipline #41 parity checks."""
        return f"{self.source_id}::{self.feature_id}"


@dataclass
class TransmissionLineRecord:
    """Normalised transmission-line record (Discipline #41 companion to
    SubstationRecord).

    Canonical geometry representation: GeoJSON MultiLineString coordinates
    ([[[lon, lat], ...], ...]).  Voltage is populated where available (NACEI
    has Voltage_kV field; CanVec power_line_1 does not have voltage at federal
    layer; BC Transmission Lines has voltage suppressed per BC Hydro publication
    agreement).
    """
    source_id: str
    feature_id: str
    coordinates_multilinestring: list[list[list[float]]]  # WGS84 [ [ [lon,lat], ... ], ... ]
    voltage_kv: float | None = None
    owner: str | None = None
    line_name: str | None = None
    from_station_id: str | None = None   # optional endpoint reference (SubstationRecord.feature_id)
    to_station_id: str | None = None
    number_of_lines: int | None = None
    raw_attributes: dict[str, Any] = field(default_factory=dict)

    def audit_key(self) -> str:
        return f"{self.source_id}::line::{self.feature_id}"


@dataclass
class IngestionResult:
    """Result envelope for one connector's fetch pass.

    Convention #56 visibly-honest degradation: if a source is fully unreachable
    or empty, this returns an empty result with a non-empty warnings list, NOT
    an exception, so downstream federation can proceed with the remaining
    sources.  Every warning must reference a Convention or Discipline number.
    """
    source_id: str
    fetched_at_utc: str                          # ISO-8601 UTC
    substations: list[SubstationRecord] = field(default_factory=list)
    transmission_lines: list[TransmissionLineRecord] = field(default_factory=list)
    raw_bytes_fetched: int = 0
    raw_sha256: str | None = None                # SHA-256 over the primary raw payload
    source_url: str | None = None
    warnings: list[str] = field(default_factory=list)
    provincial_scope: str | None = None          # e.g. "YT" | "NS" | "CA" for national


# ── Discipline #36 point-in-polygon filter ───────────────────────────────
def apply_bounds_filter(
    records: list[SubstationRecord] | list[TransmissionLineRecord],
    *,
    country_slug: str = "canada",
    tolerance_km: float = 5.0,   # Canada Mode-3 per cross_border_tolerances.json
) -> tuple[list, list[dict]]:
    """Delegate to scripts.pipeline.utils.geo.filter_by_country_polygon
    using the canonical signatures (country slug + tolerance_km + dict-shaped
    substations with lat/lon keys).

    Returns:
        (kept_records, dropped_records_with_reason)

    The Canada bounds polygon lives at canada/bounds.json and is topology-healed
    per Discipline #36 remediation (2026-06-24 commit 86d7c9df).  Tolerance
    default = 5 km per Canada Mode-3 cross_border_tolerances.json entry
    (Arctic + fjord + Great Lakes shoreline complexity).

    Records tagged as valid outbound-to-cross-border boundary features (e.g. a
    transmission line ending at Detroit-Windsor tie) MUST be handled by the
    downstream federation layer — this filter is per-substation only.
    """
    try:
        from ...utils.geo import filter_by_country_polygon, load_country_polygon
    except ImportError as exc:
        logger.warning(
            "utils.geo not importable (%s); Discipline #36 bounds filter is a NO-OP. "
            "This is Convention #56 visibly-honest degradation.",
            exc,
        )
        return list(records), []

    polygon = load_country_polygon(country_slug)
    if polygon is None:
        logger.warning(
            "%s bounds polygon missing; Discipline #36 filter is NO-OP. "
            "This is Convention #56 visibly-honest degradation.",
            country_slug,
        )
        return list(records), []

    # filter_by_country_polygon takes dict-shaped substations with lat/lon keys.
    # Wrap each record in a probe-dict indexed by list position so we can map
    # back to the original SubstationRecord/TransmissionLineRecord.
    probes: list[dict] = []
    for i, r in enumerate(records):
        if isinstance(r, SubstationRecord):
            probes.append({"_idx": i, "lat": r.latitude, "lon": r.longitude})
        elif isinstance(r, TransmissionLineRecord):
            if not r.coordinates_multilinestring or not r.coordinates_multilinestring[0]:
                probes.append({"_idx": i, "lat": None, "lon": None, "_empty": True})
                continue
            # Midpoint of first line's start+end (per Discipline #36 line-clipping convention)
            first_line = r.coordinates_multilinestring[0]
            mid_lon = (first_line[0][0] + first_line[-1][0]) / 2.0
            mid_lat = (first_line[0][1] + first_line[-1][1]) / 2.0
            probes.append({"_idx": i, "lat": mid_lat, "lon": mid_lon})
        else:
            probes.append({"_idx": i, "lat": None, "lon": None, "_unknown_type": True})

    kept_probes, dropped_probes = filter_by_country_polygon(
        probes, polygon, tolerance_km=tolerance_km, lat_key="lat", lon_key="lon"
    )
    kept_indices = {p["_idx"] for p in kept_probes}
    kept: list = []
    dropped: list[dict] = []
    for i, r in enumerate(records):
        if i in kept_indices:
            kept.append(r)
        else:
            reject_reason = f"outside {country_slug} polygon (tolerance {tolerance_km} km)"
            dropped.append({"record": r, "reason": reject_reason})
    return kept, dropped


# ── Discipline #41 substation-line parity ────────────────────────────────
def assert_line_parity(
    result: IngestionResult,
    *,
    outbound_border_ok: bool = True,
    min_line_ratio: float = 0.5,
    strict: bool = False,
) -> tuple[bool, list[str]]:
    """Discipline #41 substation ↔ line parity invariant.

    Every substation MUST connect to ≥1 line; every line MUST have both
    endpoints inside the substation registry OR the near-boundary tolerance
    band (outbound-to-cross-border, tolerated when outbound_border_ok=True).

    For federal-canonical sources (CanVec Res_MGT) where lines-to-substations
    linkage is inferred by geometric proximity rather than explicit endpoint
    IDs, this reports a warning rather than raising — the downstream
    federation layer performs the KDTree join.

    Returns:
        (parity_ok, list_of_parity_findings)
    """
    findings: list[str] = []
    sub_count = len(result.substations)
    line_count = len(result.transmission_lines)

    # Bare-minimum checks (do not KDTree-join here — that is Step 3 follow-on)
    if sub_count == 0 and line_count == 0:
        findings.append("Discipline #41 N/A — empty ingestion result.")
        return True, findings

    if sub_count > 0 and line_count == 0:
        findings.append(
            f"Discipline #41 breach — {sub_count} substations but 0 transmission lines. "
            "Companion line source must be ingested before merging into canada/ssi-data.json."
        )
        return False, findings

    if line_count > 0 and sub_count == 0:
        if outbound_border_ok:
            findings.append(
                f"Discipline #41 partial — {line_count} lines with 0 substations; "
                "acceptable if this source is lines-only (e.g. BC Transmission Lines, "
                "CA-C5) and the substation-node registry is federated from another source."
            )
            return True, findings
        findings.append(
            f"Discipline #41 breach — {line_count} lines but 0 substations "
            "(outbound_border_ok=False)."
        )
        return False, findings

    # Both substations + lines present at this source — informational ratio check
    ratio = line_count / max(sub_count, 1)
    if ratio < min_line_ratio:
        findings.append(
            f"Discipline #41 signal — line-to-substation ratio {ratio:.2f} "
            f"(threshold {min_line_ratio}). May indicate under-collection of "
            "companion line features; verify source completeness."
        )
    else:
        findings.append(
            f"Discipline #41 OK — {sub_count} substations + {line_count} lines "
            f"(ratio {ratio:.2f})."
        )

    parity_ok = True
    if strict and any("breach" in f or "signal" in f for f in findings):
        parity_ok = False
    return parity_ok, findings


# ── Audit sidecar (METHODOLOGY_DISCIPLINES.md §5ter) ────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path = CANADA_DATA_DIR,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "canada/v4_23-ingestion-audit-canada-preflight.yaml",
) -> Path:
    """Write per-source audit YAML sidecar per §5ter state-transition contract.

    Filename convention: v4_23-ingestion-audit-canada-<source_slug>.yaml
    (e.g. v4_23-ingestion-audit-canada-canvec-resmgt.yaml).

    Chain: parent pre-flight YAML → this fetch YAML → downstream federation
    YAML.  Each step names the preceding step + the git commit-hash placeholder
    for the merge that landed the transition.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("ca-"):
        slug = slug[len("ca-c") + 1 :]     # strip "CA-C1-" prefix, keep tail
    out_path = output_dir / f"v4_23-ingestion-audit-canada-{slug}.yaml"

    payload_lines = [
        "# SSI Index v4.23 workstream — Canada ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/canada/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        f"schema_version: v4_23-ingestion-audit-fetch-1",
        f"country_slug: canada",
        f"source_id: {result.source_id}",
        f"fetched_at_utc: \"{result.fetched_at_utc}\"",
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
    for f in (parity_findings or []):
        payload_lines.append(f"  - {json.dumps(f)}")
    payload_lines.extend([
        "",
        "warnings:",
    ])
    for w in result.warnings:
        payload_lines.append(f"  - {json.dumps(w)}")
    payload_lines.extend([
        "",
        "auditability_chain:",
        f"  parent_preflight: {parent_preflight_yaml}",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: canada/ssi-data.json (via federation layer, Step 3 follow-on)",
        "",
    ])
    out_path.write_text("\n".join(payload_lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".bin") -> Path:
    """SHA-256-keyed cache path so repeated fetches of the same URL hit cache."""
    CANADA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return CANADA_CACHE_DIR / f"{key}{ext}"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
