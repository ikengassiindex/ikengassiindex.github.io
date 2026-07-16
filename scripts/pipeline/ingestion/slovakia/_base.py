"""
SSI Pipeline — Slovakia v4.23 ingestion, shared base layer.

Region-jurisdiction × voltage-class monopoly via SEPS TSO + 3 regional
DSOs (ZSD west + SSD centre + VSD east) via clean NUTS-3 territorial
partition. 7th cohort-wide application of region-jurisdiction fallback
pattern (after Belgium + Netherlands + Chile + Hungary + Slovenia +
Colombia + Norway).

⚡ CONVENTION #78 BINDING ENFORCEMENT — FIRST EMPIRICAL TEST ⚡

First country onboarded post Convention #78 sub-convention BINDING
promotion methodology-version event (Latvia Priority 18 closure, 16
July 2026). Preemptive multi-script alias mapping REQUIRED at Step 3
connector authoring time:
  - Slovak NFC diacritics (č š ž ď ľ ň ť ĺ ŕ á í ó ú ý)
  - Slovak typographic quotes („..." like Czech/German/Latvian)
  - Cyrillic aliases (Rusyn + Ukrainian minority OSM contributors in
    eastern Slovakia — Prešov + Košice bordering Ukraine)
  - Historical Czechoslovak-era + post-1993 predecessor legacies

Slovakia specifics:
  - SEPS (Slovenská elektrizačná prenosová sústava a.s.) — state TSO
    (100% state-owned), operates 750 kV (Mir/Slavia Ukraine cross-border)
    + 400/420 kV (Continental European EHV backbone) + 110 kV transmission
  - ZSD (Západoslovenská distribučná a.s.) — West Slovakia DSO,
    NUTS-3: SK010 Bratislava + SK021 Trnava + SK022 Trenčín + SK023 Nitra
    (parent: ZSE Energia 51% Slovak state / 49% E.ON)
  - SSD (Stredoslovenská distribučná a.s.) — Centre Slovakia DSO,
    NUTS-3: SK031 Žilina + SK032 Banská Bystrica
    (parent: SSE 51% Slovak state / 49% EPH)
  - VSD (Východoslovenská distribučná a.s.) — East Slovakia DSO,
    NUTS-3: SK041 Prešov + SK042 Košice
    (parent: VSE 51% Slovak state / 49% RWE Innogy)
  - Historical predecessors preserved for audit trail:
    * Slovenský energetický podnik š.p. (pre-2002) → SEPS-legacy
    * Západoslovenské / Stredoslovenské / Východoslovenské energetické
      závody (pre-2005) → *SD-legacy
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
SLOVAKIA_BOUNDS_JSON = REPO_ROOT / "slovakia" / "bounds.json"
SLOVAKIA_TOLERANCE_JSON = REPO_ROOT / "cross_border_tolerances.json"
SLOVAKIA_DATA_DIR = PIPELINE_DIR / "data" / "slovakia"
SLOVAKIA_CACHE_DIR = SLOVAKIA_DATA_DIR / "_osm_cache"


# ── Owner alias normalisation (Convention #78 BINDING enforcement) ───────
# Preemptive multi-script mapping: Slovak NFC + Cyrillic + typographic quotes
_DNSP_ALIAS_MAP = {
    # SEPS variants (English + Slovak + legal-form)
    "seps": "SEPS",
    "seps a.s.": "SEPS",
    "seps, a.s.": "SEPS",
    "a.s. seps": "SEPS",
    "slovenská elektrizačná prenosová sústava": "SEPS",
    "slovenská elektrizačná prenosová sústava a.s.": "SEPS",
    "slovenska elektrizacna prenosova sustava": "SEPS",  # accent-stripped
    "slovenska elektrizacna prenosova sustava a.s.": "SEPS",
    # SEPS Cyrillic (Rusyn/Ukrainian OSM in eastern Slovakia)
    "сепс": "SEPS",
    "словенска електризачна преносова сустава": "SEPS",
    # SEPS predecessor — Slovenský energetický podnik (pre-2002 unbundling)
    "slovenský energetický podnik": "SEPS-legacy",
    "slovenský energetický podnik š.p.": "SEPS-legacy",
    "slovensky energeticky podnik": "SEPS-legacy",  # accent-stripped
    "slovensky energeticky podnik s.p.": "SEPS-legacy",

    # ZSD variants (West Slovakia DSO)
    "zsd": "ZSD",
    "zsd a.s.": "ZSD",
    "zsd, a.s.": "ZSD",
    "západoslovenská distribučná": "ZSD",
    "západoslovenská distribučná a.s.": "ZSD",
    "zapadoslovenska distribucna": "ZSD",  # accent-stripped
    "zapadoslovenska distribucna a.s.": "ZSD",
    # ZSD Cyrillic
    "зсд": "ZSD",
    "западнословенска дистрибучна": "ZSD",
    # ZSE Energia (ZSD parent)
    "zse": "ZSE Energia (Holding — West Slovakia)",
    "zse energia": "ZSE Energia (Holding — West Slovakia)",
    "zse energia a.s.": "ZSE Energia (Holding — West Slovakia)",
    "západoslovenská energetika": "ZSE Energia (Holding — West Slovakia)",
    "zapadoslovenska energetika": "ZSE Energia (Holding — West Slovakia)",
    # ZSD predecessor
    "západoslovenské energetické závody": "ZSD-legacy",
    "zapadoslovenske energeticke zavody": "ZSD-legacy",  # accent-stripped

    # SSD variants (Centre Slovakia DSO)
    "ssd": "SSD",
    "ssd a.s.": "SSD",
    "ssd, a.s.": "SSD",
    "stredoslovenská distribučná": "SSD",
    "stredoslovenská distribučná a.s.": "SSD",
    "stredoslovenska distribucna": "SSD",  # accent-stripped
    "stredoslovenska distribucna a.s.": "SSD",
    # SSD Cyrillic
    "ссд": "SSD",
    "стредословенска дистрибучна": "SSD",
    # SSE (SSD parent)
    "sse": "SSE (Holding — Centre Slovakia)",
    "sse energia": "SSE (Holding — Centre Slovakia)",
    "sse a.s.": "SSE (Holding — Centre Slovakia)",
    "stredoslovenská energetika": "SSE (Holding — Centre Slovakia)",
    "stredoslovenska energetika": "SSE (Holding — Centre Slovakia)",
    # SSD predecessor
    "stredoslovenské energetické závody": "SSD-legacy",
    "stredoslovenske energeticke zavody": "SSD-legacy",  # accent-stripped

    # VSD variants (East Slovakia DSO)
    "vsd": "VSD",
    "vsd a.s.": "VSD",
    "vsd, a.s.": "VSD",
    "východoslovenská distribučná": "VSD",
    "východoslovenská distribučná a.s.": "VSD",
    "vychodoslovenska distribucna": "VSD",  # accent-stripped
    "vychodoslovenska distribucna a.s.": "VSD",
    # VSD Cyrillic (deeper cohort — Rusyn/Ukrainian minority)
    "всд": "VSD",
    "восточнословенска дистрибучна": "VSD",
    # VSE (VSD parent)
    "vse": "VSE (Holding — East Slovakia)",
    "vse energia": "VSE (Holding — East Slovakia)",
    "vse a.s.": "VSE (Holding — East Slovakia)",
    "východoslovenská energetika": "VSE (Holding — East Slovakia)",
    "vychodoslovenska energetika": "VSE (Holding — East Slovakia)",
    # VSD predecessor
    "východoslovenské energetické závody": "VSD-legacy",
    "vychodoslovenske energeticke zavody": "VSD-legacy",  # accent-stripped

    # Slovenské elektrárne (generation-only, non-grid — may occasionally tag)
    "slovenské elektrárne": "Slovenské elektrárne (Generation)",
    "slovenske elektrarne": "Slovenské elektrárne (Generation)",
    "slovenské elektrárne a.s.": "Slovenské elektrárne (Generation)",
    "se": "Slovenské elektrárne (Generation)",
    "se a.s.": "Slovenské elektrárne (Generation)",
    "enel": "Slovenské elektrárne (Generation)",  # Enel Group parent

    # Slovak Railways (Železnice Slovenskej republiky — electric traction)
    "žsr": "Slovak Railways (Electric)",
    "zsr": "Slovak Railways (Electric)",
    "železnice slovenskej republiky": "Slovak Railways (Electric)",
    "zeleznice slovenskej republiky": "Slovak Railways (Electric)",  # accent-stripped

    # US Steel Košice (major industrial captive — eastern Slovakia)
    "u.s. steel košice": "U.S. Steel Košice (Industrial Captive)",
    "us steel košice": "U.S. Steel Košice (Industrial Captive)",
    "us steel kosice": "U.S. Steel Košice (Industrial Captive)",
    "u.s. steel kosice": "U.S. Steel Košice (Industrial Captive)",

    # Slovnaft (Bratislava oil refinery industrial captive)
    "slovnaft": "Slovnaft (Industrial Captive)",
    "slovnaft a.s.": "Slovnaft (Industrial Captive)",

    # ── Slovak typographic-quote variants (Convention #78 BINDING preemptive) ──
    # Per Latvia precedent: „..." (U+201E + U+201C) + ASCII "..." + curly "..."
    # Preemptively mapping quoted SEPS + quoted DSO variants at connector authoring
    'as "seps"': 'SEPS',
    'as „seps“': 'SEPS',
    'a.s. „seps“': 'SEPS',
    'as "zsd"': 'ZSD',
    'as „zsd“': 'ZSD',
    'as "ssd"': 'SSD',
    'as „ssd“': 'SSD',
    'as "vsd"': 'VSD',
    'as „vsd“': 'VSD',
    'as "západoslovenská distribučná"': 'ZSD',
    'as „západoslovenská distribučná“': 'ZSD',
    'as "stredoslovenská distribučná"': 'SSD',
    'as „stredoslovenská distribučná“': 'SSD',
    'as "východoslovenská distribučná"': 'VSD',
    'as „východoslovenská distribučná“': 'VSD',

    # ── Comma-separated legal-form variants (Slovakia Step 2 fetch surfaced) ──
    # NEW sub-class discovered empirically — Slovak commercial registry style
    # uses comma-separated legal form suffix (a.s. or a. s. with space variant).
    # Convention #78 BINDING enforcement retroactively extended to catch these
    # at connector authoring time going forward (post-Slovakia empirical finding).
    'západoslovenská distribučná, a.s.': 'ZSD',
    'západoslovenská distribučná, a. s.': 'ZSD',
    'zapadoslovenska distribucna, a.s.': 'ZSD',  # accent-stripped
    'zapadoslovenska distribucna, a. s.': 'ZSD',  # accent-stripped
    'stredoslovenská distribučná, a.s.': 'SSD',
    'stredoslovenská distribučná, a. s.': 'SSD',
    'stredoslovenska distribucna, a.s.': 'SSD',  # accent-stripped
    'stredoslovenska distribucna, a. s.': 'SSD',  # accent-stripped
    'východoslovenská distribučná, a.s.': 'VSD',
    'východoslovenská distribučná, a. s.': 'VSD',
    'vychodoslovenska distribucna, a.s.': 'VSD',  # accent-stripped
    'vychodoslovenska distribucna, a. s.': 'VSD',  # accent-stripped
    'slovenská elektrizačná prenosová sústava, a.s.': 'SEPS',
    'slovenská elektrizačná prenosová sústava, a. s.': 'SEPS',
    'slovenska elektrizacna prenosova sustava, a.s.': 'SEPS',  # accent-stripped
    'slovenska elektrizacna prenosova sustava, a. s.': 'SEPS',  # accent-stripped
}


def _normalise_key(s: str) -> str:
    """Unicode NFC + strip + lower-case for case-insensitive lookup.

    Convention #78 BINDING enforcement — preserves multi-script diacritics
    (Slovak NFC č š ž ď ľ ň ť) + Cyrillic (Rusyn/Ukrainian eastern Slovakia)
    + typographic quotes („..." Slovak style)."""
    return unicodedata.normalize("NFC", s).strip().lower()


def normalise_owner_alias(owner: str | None) -> str | None:
    """Case-insensitive + Unicode NFC alias normalisation with Slovak
    diacritics preserved in input, normalised via NFC + lower-case lookup.
    Handles Cyrillic aliases from eastern Slovakia Rusyn/Ukrainian OSM
    contributors + Slovak typographic-quote variants per Convention #78
    BINDING enforcement (first empirical test post-promotion)."""
    if not owner:
        return owner
    key = _normalise_key(owner)
    return _DNSP_ALIAS_MAP.get(key, owner.strip())


# ── NUTS-3 to DSO map ────────────────────────────────────────────────────
# Slovakia's clean 3-way east/centre/west partition maps 1:1 to NUTS-3.
_NUTS3_TO_DSO = {
    # ZSD (West Slovakia)
    "SK010": "ZSD",  # Bratislavský kraj
    "SK021": "ZSD",  # Trnavský kraj
    "SK022": "ZSD",  # Trenčiansky kraj
    "SK023": "ZSD",  # Nitriansky kraj
    # SSD (Centre Slovakia)
    "SK031": "SSD",  # Žilinský kraj
    "SK032": "SSD",  # Banskobystrický kraj
    # VSD (East Slovakia)
    "SK041": "VSD",  # Prešovský kraj
    "SK042": "VSD",  # Košický kraj
}


def resolve_owner_from_nuts3(nuts3_code: str | None) -> str | None:
    """Region-jurisdiction resolver via NUTS-3 code."""
    if not nuts3_code:
        return None
    return _NUTS3_TO_DSO.get(nuts3_code.strip().upper())


# ── Layer 3 lat/lon geofence (Slovenia precedent applied when NUTS-3 absent) ─
# Slovakia OSM does not populate ref:nuts:3 tags on substations (empirical
# finding Step 2 fetch — Slovenia Priority 12 precedent). Add lat/lon
# geofence for DSO attribution. Slovak territorial partition maps cleanly
# to longitude: ZSD west + SSD centre + VSD east, all spanning full latitude.
#
# Approximate boundaries based on NUTS-3 regional centroids:
#   ZSD (SK010 Bratislava 17.11°E + SK021 Trnava 17.59 + SK022 Trenčín 18.04
#        + SK023 Nitra 18.09): west boundary Slovakia bounds 16.83°E,
#        east boundary ~18.50°E (mid-point between Nitra 18.09 and Žilina 18.74)
#   SSD (SK031 Žilina 18.74°E + SK032 Banská Bystrica 19.15): west 18.50°E,
#        east ~20.50°E (mid-point between Banská Bystrica 19.15 and Prešov 21.24)
#   VSD (SK041 Prešov 21.24°E + SK042 Košice 21.26): west 20.50°E, east 22.57°E
_ZSD_EAST_BOUNDARY = 18.50
_SSD_EAST_BOUNDARY = 20.50


def resolve_owner_from_lat_lon_geofence(lat: float, lon: float) -> str | None:
    """Slovak 3-way DSO territorial partition by longitude.

    Slovenia precedent (Priority 12) — apply when OSM does not populate
    NUTS-3 tags. Convention #78 BINDING enforcement extends: when NUTS-3
    tag absent, geofence MUST be preemptively coded at Step 3 connector
    authoring time.

    Returns DSO code or None if lat/lon outside Slovak bounds.
    """
    # Sanity check — within Slovakia bounds
    if not (47.73 <= lat <= 49.61 and 16.83 <= lon <= 22.57):
        return None
    if lon < _ZSD_EAST_BOUNDARY:
        return "ZSD"  # West Slovakia
    elif lon < _SSD_EAST_BOUNDARY:
        return "SSD"  # Centre Slovakia
    else:
        return "VSD"  # East Slovakia


# ── SEPS TSO voltage threshold ───────────────────────────────────────────
# SEPS operates 750/420/400/220 kV EHV backbone. Below 220 kV → DSO
# jurisdiction via NUTS-3 map or lat/lon geofence. 110 kV MIXED tier —
# default to SEPS if voltage present but no territorial resolution.
_SEPS_TSO_MIN_KV = 220.0


def resolve_owner_from_region_jurisdiction(
    voltage_kv: float | None, lat: float, lon: float, nuts3: str | None = None
) -> tuple[str | None, str]:
    """Return (owner, provenance).

    Region-jurisdiction × voltage-class resolver — 7th cohort-wide
    application (after Belgium + Netherlands + Chile + Hungary + Slovenia
    + Colombia + Norway). Slovenia precedent (Layer 3 lat/lon geofence
    when NUTS-3 tag absent) applied per Convention #78 BINDING enforcement.

    Layer 1: SEPS TSO threshold ≥220 kV → SEPS (750/420/400/220 kV backbone).
    Layer 2: NUTS-3 → DSO map (if OSM populates NUTS-3 tags — empirically
             0 hits in Slovakia Step 2 fetch; kept for forward-compat).
    Layer 3: Lat/lon geofence → DSO (Slovenia precedent — 3-way longitude
             partition when NUTS-3 tag absent).
    Layer 4: 110 kV mixed tier — defaults to SEPS if geofence fails.
    Layer 5: Empirical default — SEPS as unified state TSO catch-all.
    """
    # Layer 1: EHV → SEPS
    if voltage_kv is not None and voltage_kv >= _SEPS_TSO_MIN_KV:
        return "SEPS", "region_jurisdiction_fallback_SEPS_TSO_threshold_ge_220kv"

    # Layer 2: NUTS-3 → DSO (empirically 0 hits — kept for forward-compat)
    if nuts3:
        dso = resolve_owner_from_nuts3(nuts3)
        if dso:
            return dso, f"region_jurisdiction_fallback_{dso}_via_nuts3_{nuts3}"

    # Layer 3: Lat/lon geofence → DSO (Slovenia precedent applied)
    dso_via_geofence = resolve_owner_from_lat_lon_geofence(lat, lon)
    if dso_via_geofence:
        return dso_via_geofence, f"region_jurisdiction_fallback_{dso_via_geofence}_via_lat_lon_geofence"

    # Layer 4: 110 kV mixed tier — default to SEPS if geofence returned None
    if voltage_kv is not None and voltage_kv >= 100.0:
        return "SEPS", "region_jurisdiction_fallback_SEPS_TSO_110kv_mixed_tier"

    # Layer 5: catch-all — SEPS as unified state TSO
    return "SEPS", "region_jurisdiction_fallback_SEPS_state_utility_default"


# ── Discipline #36 with Slovakia 100m default tolerance ──────────────────
def apply_bounds_filter(records, *, tolerance_km: float | None = None):
    """Slovakia bounds filter with 100m default tolerance."""
    if tolerance_km is None:
        try:
            tol_cfg = json.loads(SLOVAKIA_TOLERANCE_JSON.read_text(encoding="utf-8"))
            tolerance_km = float(
                tol_cfg.get("per_country", {}).get("slovakia", {}).get("tolerance_km", 0.1)
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            tolerance_km = 0.1
    return _apply_bounds_generic(
        records, country_slug="slovakia", tolerance_km=tolerance_km
    )


# ── Audit sidecar ────────────────────────────────────────────────────────
def emit_audit_sidecar(
    result: IngestionResult,
    *,
    output_dir: Path | None = None,
    parity_findings: list[str] | None = None,
    parent_preflight_yaml: str = "slovakia/v4_23-ingestion-audit-slovakia-preflight.yaml",
) -> Path:
    if output_dir is None:
        output_dir = SLOVAKIA_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.source_id.lower().replace("_", "-")
    if slug.startswith("sk-"):
        slug = slug[len("sk-c") + 1 :]
    out_path = output_dir / f"v4_23-ingestion-audit-slovakia-{slug}.yaml"

    lines = [
        "# SSI Index v4.23 workstream — Slovakia ingestion fetch audit",
        "# Auto-generated by scripts/pipeline/ingestion/slovakia/_base.py::emit_audit_sidecar",
        f"# Parent pre-flight: {parent_preflight_yaml}",
        "",
        "schema_version: v4_23-ingestion-audit-fetch-1",
        "country_slug: slovakia",
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
        "  step_2_fetch: slovakia/v4_23-ingestion-audit-slovakia-fetch.yaml",
        "  commit_hash_placeholder: TBD_at_L1_connector_merge",
        "  ci_job_url_placeholder: TBD_at_L1_connector_merge",
        "  downstream_deliverable: slovakia/ssi-data.json (via federation layer)",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote audit sidecar %s (%d bytes)", out_path, out_path.stat().st_size)
    return out_path


# ── Cache helpers ────────────────────────────────────────────────────────
def cache_path_for(url: str, *, ext: str = ".json") -> Path:
    SLOVAKIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return SLOVAKIA_CACHE_DIR / f"{key}{ext}"


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
    "resolve_owner_from_nuts3",
    "normalise_owner_alias",
    "SLOVAKIA_BOUNDS_JSON",
    "SLOVAKIA_TOLERANCE_JSON",
    "SLOVAKIA_DATA_DIR",
    "SLOVAKIA_CACHE_DIR",
]
