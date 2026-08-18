#!/usr/bin/env python3
"""r7_cyber_v2.py — CRA + NIS2 regulatory-vintage composite modifier (v0 first apply)

Task #1102 + #1107 + #1118 + #1134 (18 August 2026)
=====================================================

Implements the R7_cyber v2 composite modifier per D2 formula construct
(`R7_CYBER_V2_FORMULA_CONSTRUCT_DRAFT.md` at
`SSI Index/Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/`).

Sibling to R7_cyber v1 (legacy DESI + ACN scalar proxy, `[0.99, 1.05]`
envelope) with which it co-exists during the ~6-month dual-write
transition per Gate A GATE-A-11 operator sign-off 18 August 2026
Session B. R7 v1 remains live + emitted; R7 v2 is written as a sibling
field so downstream consumers may select either.

Load-bearing methodology anchor
-------------------------------
- **Registry key.** ``R7_cyber_v2`` (byte-identical between
  ``modifier_registry.py::MODIFIER_REGISTRY`` and emitted
  ``sub["modifiers"]["R7_cyber_v2"]``). Sentinel
  ``tests/test_r7_cyber_v2_construct.py`` pins parity.
- **Envelope at v0.** ``[0.99, 1.05]`` (matches R7 v1 default for
  continuity). Envelope re-calibration deferred to v1 (post ENISA SRP
  feed availability if opens) → v2 (post 11 December 2027 CRA full
  applicability + SBOM per-vendor granularity). D2 spec draft describes
  a wider ``[0.85, 1.10]`` envelope; the operator explicitly resolved
  v0 to preserve v1 envelope for cross-consumer continuity.
- **Path variant.** Path C+D composite (Gate A GATE-A-1 sign-off
  18 August 2026 Session B). EU cohort (26 countries) via CRA
  Article 14 reporting cascade + NIS2 Article 21 essential-entity
  register read; non-EU cohort (13 countries) via country-statute
  parallel constructs per D1 memo §4 table (UK NIS Regs 2018 + CAF ·
  US NERC CIP + CIRCIA · Japan METI CPSF · Korea K-ISMS-P · Australia
  ACSC ISM + SoCI Act · New Zealand NZISM · Chile Ley 21.663 ·
  Colombia CONPES 3854 · Costa Rica MICITT + CSIRT-CR · Israel INCD ·
  Mexico CERT-MX · Turkey BTK + Law 7545 · Canada CCCS).
- **Weights.** ``w_entity = 0.55, w_product = 0.45`` (Gate A
  GATE-A-2 sign-off 18 August 2026 Session B). Anchored Ciso-Nasser
  2024 + NERC E-ISAC 2022 empirical grounding — operator-response
  discipline dominates over vendor-vulnerability tail for grid-critical
  infrastructure. Sum-to-unity BINDING invariant (``w_entity +
  w_product == 1.0``) pinned at sentinel.

Regulatory anchors (Convention #7 documented-proxy)
---------------------------------------------------
- **CRA.** ``Regulation (EU) 2024/2847 · Article 14`` reporting
  cascade (24 h / 72 h / 14 d). In force 10 December 2024. Article 14
  hard binding date 11 September 2026. Full applicability
  11 December 2027.
- **NIS2.** ``Directive (EU) 2022/2555 · Article 3`` (telecom
  definition) + ``Article 21`` (ten measures) + ``Article 23``
  (incident reporting) + ``Article 31`` (essential-entity register).
  OJ L 14 December 2022. Transposition deadline 17 October 2024
  (missed by 22/27 Member States as of 2026 Q3).

Formula (Path C+D composite)
----------------------------
::

    R7_cyber_v2 = 1.0 + delta_cyber_scaled
    delta_cyber = w_entity(country) * f_entity(country, t)
                + w_product(country) * f_product(sub, country, t)

    f_entity(country, t) = a1 * nis2_status_norm
                         + a2 * nis2_incident_history_norm
                         + a3 * regulatory_regime_maturity_norm
    where a1 = 0.35, a2 = 0.35, a3 = 0.30  [sum = 1.0]

    f_product(sub, country, t) = b1 * vendor_mix_cra_vintage
                               + b2 * sbom_coverage
                               + b3 * srp_exploited_vuln_signal
    where b1 = 0.45, b2 = 0.35, b3 = 0.20  [sum = 1.0]

    delta_cyber in [0, 1] (each f_layer in [0, 1] by construction).
    delta_cyber_scaled maps [0, 1] -> envelope [0.99, 1.05]:
        R7_cyber_v2 = 0.99 + delta_cyber * 0.06

    Envelope preserved [0.99, 1.05] per Gate A v0 operator sign-off.

Convention #56 fallback
-----------------------
- ``f_entity == None`` and ``f_product == None`` (no register data) →
  R7_cyber_v2 = 1.0 (v1 identity fallback) + audit marker.
- One layer None, other populated → redistribute the missing layer's
  weight to the populated layer. Preserves per-sub differentiation
  where partial data exists.
- Individual component None within a layer → treat as 0.0 (neutral)
  and log the specific missing component in the audit marker.

Dual-write semantics (GATE-A-11)
--------------------------------
- ``R7_cyber`` v1 is NEVER modified by this module. v1 remains live
  + emitted by the pre-existing R7 pipeline path.
- ``R7_cyber_v2`` is written as a sibling field on
  ``sub["modifiers"]``.
- ``_r7_cyber_v1_retired`` initialized False at v0 first apply;
  transitions True at v1 tombstone timing (~Q1 2027 per operator).
- ``_r7_cyber_v1_value`` captures the last-computed v1 multiplier
  at time of v2 first apply (Convention #56 audit trail).

Convention preservation matrix
------------------------------
- **#7** Data-Layer Anchoring — CRA + NIS2 publisher-cited (OJ L),
  article-pinned, vintage-year-declared.
- **#54** Housekeeping cascade — module authoring is Phase 2J P3
  landing per METHODOLOGY_CASCADE_PLAYBOOK.md v0.3 §3.3 T1 row.
- **#55** Verify-don't-trust — sentinel
  ``tests/test_r7_cyber_v2_construct.py`` pins every invariant.
- **#56** Visibly-honest degradation — every fallback path emits
  ``_r7_cyber_v2_fallback_reason`` marker; no silent identity default.
- **#60** Ikenga IS the ESG provider — all sources are institutional
  publishers (EU institutions + national CSIRTs + national regulators).
- **#63** Parallel-worlds — R7 v2 modifies R_final (scoring-world);
  W6 (commercial-tier) evaluates compliance-world register only.
- **#78** §5septies BINDING — L1 ingestion not touched.
- **#79** ssi-data sharding preserved — reads via
  ``_ssi_data_shard_reader``; writes via ``save_ssi_data``.

Usage
-----
Diagnose-only (check inputs available per country, no reads):

    python3 scripts/pipeline/scoring/r7_cyber_v2.py --diagnose-only

Single country dry-run (compute + report, don't write):

    python3 scripts/pipeline/scoring/r7_cyber_v2.py spain --dry-run

Single country apply:

    python3 scripts/pipeline/scoring/r7_cyber_v2.py spain

Cohort-wide apply (39 countries per intelligence/countries.json):

    python3 scripts/pipeline/scoring/r7_cyber_v2.py --all-countries

Regulatory-vintage inputs (per-country registers)
-------------------------------------------------
This v0 first-apply module reads per-country regulatory-vintage
inputs from ``scripts/pipeline/data/{slug}/r7_cyber_v2_inputs.json``
if present; otherwise falls back to Convention #56 identity per-sub.
Per-country inputs are authored/refreshed by the operator via national
CSIRT + regulator + register reads (see D1 memo §4 table for source
URLs per country).

Input schema per country (all fields in [0, 1] or None per Convention #56)::

    {
      "country_slug": "spain",
      "as_of_date": "2026-08-18",
      "nis2_status_norm": 0.72,             # NIS2 Article 31 register density
      "nis2_incident_history_norm": 0.15,   # 24m CSIRT-reported incidents
      "regulatory_regime_maturity_norm": 0.85,
      "srp_exploited_vuln_signal": 0.10,    # ENISA SRP (Path A pending)
      "default_vendor_mix_cra_vintage": 0.0,  # pre-11-Dec-2027 baseline
      "default_sbom_coverage": 0.0,          # pre-Article-13 baseline
      "path_variant": "C",                  # or "D" for non-EU
      "sources": {
        "nis2_status": "Regulation (EU) 2022/2555 Article 31 register + Spain INCIBE 2026-Q2 snapshot",
        "nis2_incident_history": "Spain INCIBE-CERT annual reports 2024-2026",
        ...
      }
    }

For v0 first apply many countries will have partial inputs. Convention
#56 fallback rules above handle every partial case visibly.

Module contract (BINDING per sentinel)
--------------------------------------
- ``ENVELOPE_LOW = 0.99``
- ``ENVELOPE_HIGH = 1.05``
- ``W_ENTITY = 0.55``
- ``W_PRODUCT = 0.45``
- ``ENTITY_WEIGHTS = (0.35, 0.35, 0.30)`` for (a1, a2, a3)
- ``PRODUCT_WEIGHTS = (0.45, 0.35, 0.20)`` for (b1, b2, b3)
- ``AUDIT_TRAIL_KEY = "_r7_cyber_v2_source"``
- ``AUDIT_TRAIL_VALUE = "R7_CYBER_V2_CRA_NIS2_PATH_CD_v0_task_1102_1107_1118_1134"``
- ``FALLBACK_KEY = "_r7_cyber_v2_fallback_reason"``
- ``V1_RETIRED_KEY = "_r7_cyber_v1_retired"``
- ``V1_VALUE_KEY = "_r7_cyber_v1_value"``
- ``REGISTRY_KEY = "R7_cyber_v2"``

BINDING invariants pinned at
``tests/test_r7_cyber_v2_construct.py::TestUtilityConstantLock``.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("r7_cyber_v2")

# ══════════════════════════════════════════════════════════════════
# MODULE CONSTANTS (BINDING per sentinel TestUtilityConstantLock)
# ══════════════════════════════════════════════════════════════════

# Envelope at v0 first apply — matches R7 v1 default for continuity.
# Envelope re-calibration deferred to v1 (post ENISA SRP) → v2
# (post 11 Dec 2027 CRA full applicability).
ENVELOPE_LOW: float = 0.99
ENVELOPE_HIGH: float = 1.05

# Path variant weights (Gate A GATE-A-2 sign-off 18 Aug 2026 Session B).
# Anchored Ciso-Nasser 2024 + NERC E-ISAC 2022 empirical grounding.
# BINDING sum-to-unity invariant: W_ENTITY + W_PRODUCT == 1.0.
W_ENTITY: float = 0.55
W_PRODUCT: float = 0.45

# Entity-layer component weights (f_entity):
#   a1 · nis2_status_norm (Article 31 register discipline)
#   a2 · nis2_incident_history_norm (Article 23 incident-report register)
#   a3 · regulatory_regime_maturity_norm (regulator density per Convention #78 §5septies)
# BINDING sum-to-unity: a1 + a2 + a3 == 1.0.
ENTITY_WEIGHTS: Tuple[float, float, float] = (0.35, 0.35, 0.30)

# Product-layer component weights (f_product):
#   b1 · vendor_mix_cra_vintage (CRA Article 13 conformity)
#   b2 · sbom_coverage (CRA Article 13 disclosure)
#   b3 · srp_exploited_vuln_signal (ENISA SRP, Path A pending)
# BINDING sum-to-unity: b1 + b2 + b3 == 1.0.
PRODUCT_WEIGHTS: Tuple[float, float, float] = (0.45, 0.35, 0.20)

# Convention #56 audit trail — every populated R7 v2 value carries this marker.
AUDIT_TRAIL_KEY: str = "_r7_cyber_v2_source"
AUDIT_TRAIL_VALUE: str = "R7_CYBER_V2_CRA_NIS2_PATH_CD_v0_task_1102_1107_1118_1134"

# Convention #56 fallback marker — populated when v2 falls back to identity or partial.
FALLBACK_KEY: str = "_r7_cyber_v2_fallback_reason"

# Dual-write transition markers per Gate A GATE-A-11 sign-off.
V1_RETIRED_KEY: str = "_r7_cyber_v1_retired"
V1_VALUE_KEY: str = "_r7_cyber_v1_value"

# Registry key (byte-identical to modifier_registry.py entry name).
REGISTRY_KEY: str = "R7_cyber_v2"

# EU cohort (26 countries) — Path C via CRA + NIS2 register-read.
# Non-EU cohort (13 countries) — Path D via country-statute parallel constructs
# per D1 memo §4 table.
EU_COHORT: Tuple[str, ...] = (
    "austria", "belgium", "czechia", "denmark", "estonia", "finland",
    "france", "germany", "greece", "hungary", "ireland", "italy",
    "latvia", "lithuania", "luxembourg", "netherlands", "poland",
    "portugal", "slovakia", "slovenia", "spain", "sweden",
    # Norway is EFTA/EEA — NIS2 applicable via EEA Agreement adoption
    "norway",
    # Iceland is EFTA/EEA
    "iceland",
    # Switzerland is not EU/EEA — path variant D (national)
    # (Note: Cyprus, Malta, Bulgaria, Romania, Croatia not in v4.2 39-country cohort)
)

NON_EU_COHORT: Tuple[str, ...] = (
    "uk", "us", "canada", "japan", "korea", "australia", "new-zealand",
    "chile", "colombia", "costa-rica", "israel", "mexico", "turkey",
    "switzerland", "greenland",
)

# Regulatory anchor pins per D2 formula construct §4 (documented-proxy).
CRA_ARTICLE_14_BINDING_DATE: str = "2026-09-11"
NIS2_TRANSPOSITION_DEADLINE: str = "2024-10-17"
CRA_FULL_APPLICABILITY: str = "2027-12-11"


# ══════════════════════════════════════════════════════════════════
# PATH RESOLUTION
# ══════════════════════════════════════════════════════════════════

REPO_ROOT: Path = Path(__file__).resolve().parents[3]
COUNTRIES_SOT: Path = REPO_ROOT / "intelligence" / "countries.json"
PIPELINE_DATA_ROOT: Path = REPO_ROOT / "scripts" / "pipeline" / "data"


def _load_countries_slugs() -> List[str]:
    """Return the 39-country slug list from ``intelligence/countries.json`` (KB §57)."""
    with COUNTRIES_SOT.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload["slugs"]


def resolve_path_variant(country_slug: str) -> str:
    """Return 'C' (EU cohort via CRA + NIS2) or 'D' (non-EU parallel constructs).

    Per D1 memo §4 table: EU + EEA countries use Path C (CRA Article 14 +
    NIS2 Article 21 direct register read); non-EU countries use Path D
    (country-statute parallel constructs — UK CAF · US NERC CIP + CIRCIA ·
    Japan METI CPSF · etc).
    """
    slug = country_slug.strip().lower()
    if slug in EU_COHORT:
        return "C"
    if slug in NON_EU_COHORT:
        return "D"
    logger.warning(
        "resolve_path_variant: %s not in EU_COHORT or NON_EU_COHORT — "
        "falling back to Path D (non-EU parallel-construct) per Convention #56",
        slug,
    )
    return "D"


# ══════════════════════════════════════════════════════════════════
# CORE FORMULA (Path C+D composite per Gate A GATE-A-1 + GATE-A-2)
# ══════════════════════════════════════════════════════════════════


def _weighted_sum_or_none(
    components: List[Tuple[Optional[float], float]],
) -> Tuple[Optional[float], List[str]]:
    """Compute weighted sum treating None components per Convention #56.

    Per D2 spec: individual missing components within a layer are treated
    as 0.0 (neutral) with the specific missing component logged. If ALL
    components are None, the layer returns None (fallback signal).

    Parameters
    ----------
    components : list of (value, weight) tuples.

    Returns
    -------
    (result, missing_labels)
        result : weighted sum in [0, 1], or None if every component is None.
        missing_labels : list of "component_{index}" for None components.
    """
    missing = []
    numerator = 0.0
    denom = 0.0
    any_populated = False
    for idx, (val, weight) in enumerate(components):
        if val is None:
            missing.append(f"component_{idx}")
            continue
        any_populated = True
        # Clamp to [0, 1] envelope (defensive; inputs SHOULD be pre-normed).
        val_clamped = max(0.0, min(1.0, float(val)))
        numerator += weight * val_clamped
        denom += weight
    if not any_populated:
        return None, missing
    # Convention #56 partial: if some components missing, re-scale by populated denom
    # so the layer output stays comparable across countries with partial data.
    if denom == 0.0:
        return None, missing
    result = numerator / denom
    # Clamp defensively.
    result = max(0.0, min(1.0, result))
    return result, missing


def compute_f_entity(
    nis2_status_norm: Optional[float],
    nis2_incident_history_norm: Optional[float],
    regulatory_regime_maturity_norm: Optional[float],
) -> Tuple[Optional[float], List[str]]:
    """Entity-layer per D2 §3.1 (Path C+D composite).

    ``f_entity = a1 · nis2_status_norm + a2 · nis2_incident_history_norm
                + a3 · regulatory_regime_maturity_norm``

    Each per-country normaliser in [0, 1]. Convention #56: if all three
    inputs are None, returns (None, [...]) signalling entity-layer
    fallback needed.
    """
    a1, a2, a3 = ENTITY_WEIGHTS
    return _weighted_sum_or_none([
        (nis2_status_norm, a1),
        (nis2_incident_history_norm, a2),
        (regulatory_regime_maturity_norm, a3),
    ])


def compute_f_product(
    vendor_mix_cra_vintage: Optional[float],
    sbom_coverage: Optional[float],
    srp_exploited_vuln_signal: Optional[float],
) -> Tuple[Optional[float], List[str]]:
    """Product-layer per D2 §3.2 (Path C+D composite).

    ``f_product = b1 · vendor_mix_cra_vintage + b2 · sbom_coverage
                + b3 · srp_exploited_vuln_signal``

    Each per-sub or per-country normaliser in [0, 1]. Convention #56:
    if all three inputs are None, returns (None, [...]) signalling
    product-layer fallback needed.
    """
    b1, b2, b3 = PRODUCT_WEIGHTS
    return _weighted_sum_or_none([
        (vendor_mix_cra_vintage, b1),
        (sbom_coverage, b2),
        (srp_exploited_vuln_signal, b3),
    ])


def compose_delta_cyber(
    f_entity: Optional[float],
    f_product: Optional[float],
) -> Tuple[Optional[float], str]:
    """Compose delta_cyber from entity + product layers per D2 §3.

    ``delta_cyber = w_entity · f_entity + w_product · f_product``

    Convention #56 partial handling:
    - Both None → return (None, "no_entity_no_product_data") for identity fallback.
    - Entity None, product populated → redistribute w_entity weight to product:
      delta_cyber = 1.0 · f_product (with fallback_reason marker).
    - Product None, entity populated → redistribute w_product to entity.
    - Both populated → nominal weighted sum.
    """
    if f_entity is None and f_product is None:
        return None, "no_entity_no_product_data"
    if f_entity is None:
        # Product-only path — full weight on populated layer.
        return f_product, "entity_layer_none_full_weight_on_product"
    if f_product is None:
        # Entity-only path — full weight on populated layer.
        return f_entity, "product_layer_none_full_weight_on_entity"
    # Both populated — nominal composition per Gate A GATE-A-2.
    delta = W_ENTITY * f_entity + W_PRODUCT * f_product
    # Clamp to [0, 1] defensively.
    delta = max(0.0, min(1.0, delta))
    return delta, ""


def scale_delta_to_envelope(delta_cyber: float) -> float:
    """Map delta_cyber ∈ [0, 1] to R7_cyber_v2 ∈ [ENVELOPE_LOW, ENVELOPE_HIGH].

    Per Gate A v0 operator sign-off: envelope preserved [0.99, 1.05] for
    continuity with R7 v1. Linear mapping:

        R7_cyber_v2 = ENVELOPE_LOW + delta_cyber · (ENVELOPE_HIGH - ENVELOPE_LOW)

    delta_cyber = 0.0 → R7 v2 = 0.99 (best-case, matches v1 lower bound)
    delta_cyber = 1.0 → R7 v2 = 1.05 (worst-case, matches v1 upper bound)
    delta_cyber = 0.5 → R7 v2 = 1.02 (neutral midpoint)
    """
    if delta_cyber is None:
        raise ValueError("scale_delta_to_envelope called with None delta_cyber")
    delta_clamped = max(0.0, min(1.0, float(delta_cyber)))
    span = ENVELOPE_HIGH - ENVELOPE_LOW
    result = ENVELOPE_LOW + delta_clamped * span
    # Clamp defensively (guard against floating-point envelope creep).
    return max(ENVELOPE_LOW, min(ENVELOPE_HIGH, result))


# ══════════════════════════════════════════════════════════════════
# PER-SUBSTATION COMPUTATION (v0 first-apply entry point)
# ══════════════════════════════════════════════════════════════════


def compute_r7_cyber_v2_for_sub(
    sub: Dict[str, Any],
    country_inputs: Optional[Dict[str, Any]],
) -> Tuple[Optional[float], Dict[str, Any]]:
    """Compute R7_cyber v2 for a single substation.

    Convention #56 contract:
    - If ``country_inputs`` is None (no per-country register data loaded):
      return (None, {"fallback_reason": "no_country_inputs", ...}). Caller
      writes identity 1.0 into ``sub["modifiers"]["R7_cyber_v2"]`` with
      fallback marker per D2 §3 spec.
    - If both f_entity and f_product resolve to None (all six components
      missing): return (1.0, {"fallback_reason": "no_entity_no_product_data",
      ...}) so R7 v2 == v1 identity default.
    - Otherwise: return (r7_v2_value, {"delta_cyber": ..., ...}).

    Dual-write semantics (GATE-A-11):
    - This function does NOT touch ``sub["modifiers"]["R7_cyber"]`` (v1
      value stays exactly as-is).
    - Records ``_r7_cyber_v1_value`` snapshot for audit trail.

    Parameters
    ----------
    sub : substation dict (from ssi-data.json).
    country_inputs : per-country regulatory-vintage inputs dict, or None.

    Returns
    -------
    (r7_cyber_v2_value, audit_meta)
    """
    audit_meta: Dict[str, Any] = {
        "path_variant": None,
        "fallback_reason": "",
        "missing_components": [],
        "delta_cyber": None,
        "f_entity": None,
        "f_product": None,
    }

    if country_inputs is None:
        audit_meta["fallback_reason"] = "no_country_inputs"
        # Convention #56: identity fallback preserves R7 v1 semantic.
        return 1.0, audit_meta

    audit_meta["path_variant"] = country_inputs.get("path_variant", "C")

    # Entity-layer (per-country from register read).
    f_entity, entity_missing = compute_f_entity(
        nis2_status_norm=country_inputs.get("nis2_status_norm"),
        nis2_incident_history_norm=country_inputs.get("nis2_incident_history_norm"),
        regulatory_regime_maturity_norm=country_inputs.get("regulatory_regime_maturity_norm"),
    )
    audit_meta["f_entity"] = f_entity
    audit_meta["missing_components"].extend(f"entity.{m}" for m in entity_missing)

    # Product-layer (per-sub if available, else per-country default).
    # For v0 first apply, per-sub vendor mix + SBOM coverage are typically not
    # yet populated at substation granularity (pre-CRA-full-applicability).
    # Falls back to country-level defaults.
    vendor_mix = sub.get("vendor_mix_cra_vintage",
                         country_inputs.get("default_vendor_mix_cra_vintage"))
    sbom = sub.get("sbom_coverage",
                   country_inputs.get("default_sbom_coverage"))
    srp = country_inputs.get("srp_exploited_vuln_signal")

    f_product, product_missing = compute_f_product(
        vendor_mix_cra_vintage=vendor_mix,
        sbom_coverage=sbom,
        srp_exploited_vuln_signal=srp,
    )
    audit_meta["f_product"] = f_product
    audit_meta["missing_components"].extend(f"product.{m}" for m in product_missing)

    # Compose delta_cyber per D2 §3.
    delta_cyber, compose_fallback = compose_delta_cyber(f_entity, f_product)
    audit_meta["delta_cyber"] = delta_cyber
    if compose_fallback:
        audit_meta["fallback_reason"] = compose_fallback

    if delta_cyber is None:
        # Both layers None → identity fallback per D2 §3 Convention #56.
        return 1.0, audit_meta

    # Map delta to envelope.
    r7_v2 = scale_delta_to_envelope(delta_cyber)
    return r7_v2, audit_meta


# ══════════════════════════════════════════════════════════════════
# PER-COUNTRY INPUT LOADING (regulatory-vintage register)
# ══════════════════════════════════════════════════════════════════


def load_country_inputs(country_slug: str) -> Optional[Dict[str, Any]]:
    """Load per-country regulatory-vintage inputs from
    ``scripts/pipeline/data/{slug}/r7_cyber_v2_inputs.json``.

    Returns None (Convention #56 visibly-honest) if the input file does
    not exist — the caller handles fallback per D2 §3.
    """
    inputs_path = PIPELINE_DATA_ROOT / country_slug / "r7_cyber_v2_inputs.json"
    if not inputs_path.exists():
        logger.info(
            "load_country_inputs: %s not found for %s — Convention #56 "
            "fallback to identity 1.0 at apply time",
            inputs_path, country_slug,
        )
        return None
    try:
        with inputs_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        # Basic shape check.
        if not isinstance(payload, dict):
            logger.warning(
                "load_country_inputs: %s malformed (not a dict) — Convention "
                "#56 fallback", inputs_path,
            )
            return None
        # Ensure path_variant field present per resolve_path_variant contract.
        if "path_variant" not in payload:
            payload["path_variant"] = resolve_path_variant(country_slug)
        return payload
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "load_country_inputs: %s failed to parse (%s) — Convention #56 fallback",
            inputs_path, exc,
        )
        return None


# ══════════════════════════════════════════════════════════════════
# COUNTRY APPLY (uses _ssi_data_shard_reader per Convention #79)
# ══════════════════════════════════════════════════════════════════


def apply_r7_cyber_v2_to_country(
    country_slug: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Apply R7_cyber v2 v0 first-apply pass to a single country.

    Reads country ssi-data via ``_ssi_data_shard_reader`` (Convention #79
    sharding preserved). Writes ``R7_cyber_v2`` sibling field alongside
    R7 v1 (dual-write per GATE-A-11). NEVER modifies existing
    ``R7_cyber`` v1 value.

    Returns a summary dict (n_processed, n_populated_v2, fallback distribution).
    """
    # Import here to keep the module importable without the sharding utility.
    from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data  # noqa: E402

    logger.info("apply_r7_cyber_v2_to_country: begin %s (dry_run=%s)",
                country_slug, dry_run)

    country_inputs = load_country_inputs(country_slug)
    data = load_ssi_data(country_slug)
    substations = data.get("substations") or []
    if isinstance(substations, dict):
        # Convention #78 §4bis.4 flat-list handling — should not occur here
        # given the shard reader normalises, but guard defensively.
        substations = substations.get("items", []) or []

    summary: Dict[str, Any] = {
        "country_slug": country_slug,
        "path_variant": (country_inputs or {}).get("path_variant") or resolve_path_variant(country_slug),
        "n_substations": len(substations),
        "n_populated_v2": 0,
        "n_fallback_identity": 0,
        "fallback_reasons": {},
        "envelope_min_observed": None,
        "envelope_max_observed": None,
    }

    for sub in substations:
        modifiers = sub.setdefault("modifiers", {})
        # Capture R7 v1 value snapshot for audit trail (dual-write GATE-A-11).
        v1_val = modifiers.get("R7_cyber")
        # Compute R7 v2.
        r7_v2, audit = compute_r7_cyber_v2_for_sub(sub, country_inputs)
        # Write dual-write markers.
        modifiers[REGISTRY_KEY] = r7_v2
        sub[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
        if audit["fallback_reason"]:
            sub[FALLBACK_KEY] = audit["fallback_reason"]
        elif FALLBACK_KEY in sub:
            # Clean up stale fallback marker if this pass populates cleanly.
            del sub[FALLBACK_KEY]
        # Dual-write transition markers (v1 remains live per GATE-A-11).
        sub[V1_RETIRED_KEY] = False
        if v1_val is not None:
            sub[V1_VALUE_KEY] = v1_val

        # Update summary.
        if audit["fallback_reason"] == "no_country_inputs" or \
           audit["fallback_reason"] == "no_entity_no_product_data":
            summary["n_fallback_identity"] += 1
            reason = audit["fallback_reason"]
            summary["fallback_reasons"][reason] = summary["fallback_reasons"].get(reason, 0) + 1
        else:
            summary["n_populated_v2"] += 1
            if summary["envelope_min_observed"] is None or r7_v2 < summary["envelope_min_observed"]:
                summary["envelope_min_observed"] = r7_v2
            if summary["envelope_max_observed"] is None or r7_v2 > summary["envelope_max_observed"]:
                summary["envelope_max_observed"] = r7_v2

    if not dry_run:
        save_ssi_data(country_slug, data)
        logger.info("apply_r7_cyber_v2_to_country: wrote %s (n=%d subs)",
                    country_slug, len(substations))
    else:
        logger.info("apply_r7_cyber_v2_to_country: DRY-RUN — %s not written",
                    country_slug)

    return summary


def apply_r7_cyber_v2_to_all(dry_run: bool = False) -> List[Dict[str, Any]]:
    """Cohort-wide apply per KB §57 SoT."""
    slugs = _load_countries_slugs()
    summaries = []
    for slug in slugs:
        try:
            s = apply_r7_cyber_v2_to_country(slug, dry_run=dry_run)
            summaries.append(s)
        except Exception as exc:  # noqa: BLE001 — surface per Convention #56
            logger.exception("apply_r7_cyber_v2_to_country: %s FAILED (%s)",
                             slug, exc)
            summaries.append({
                "country_slug": slug,
                "error": str(exc),
            })
    return summaries


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════


def _diagnose() -> None:
    """Diagnose mode — check module constants + cohort SoT + per-country inputs presence."""
    slugs = _load_countries_slugs()
    print(f"R7_cyber v2 diagnose — 39-country cohort per intelligence/countries.json")
    print(f"  ENVELOPE_LOW={ENVELOPE_LOW} · ENVELOPE_HIGH={ENVELOPE_HIGH}")
    print(f"  W_ENTITY={W_ENTITY} · W_PRODUCT={W_PRODUCT} · sum={W_ENTITY + W_PRODUCT}")
    print(f"  ENTITY_WEIGHTS={ENTITY_WEIGHTS} · sum={sum(ENTITY_WEIGHTS)}")
    print(f"  PRODUCT_WEIGHTS={PRODUCT_WEIGHTS} · sum={sum(PRODUCT_WEIGHTS)}")
    print(f"  REGISTRY_KEY={REGISTRY_KEY}")
    print(f"  AUDIT_TRAIL_VALUE={AUDIT_TRAIL_VALUE}")
    print()
    n_present = 0
    for slug in slugs:
        variant = resolve_path_variant(slug)
        inputs = load_country_inputs(slug)
        status = "PRESENT" if inputs is not None else "MISSING (Convention #56 identity fallback at apply)"
        if inputs is not None:
            n_present += 1
        print(f"  {slug:20s}  Path {variant}  {status}")
    print()
    print(f"  Per-country inputs present: {n_present}/{len(slugs)}")


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="R7_cyber v2 CRA + NIS2 regulatory-vintage composite modifier (v0 first apply)"
    )
    parser.add_argument("country", nargs="?", help="Country slug (or omit with --all-countries).")
    parser.add_argument("--all-countries", action="store_true",
                        help="Apply to every country in intelligence/countries.json::slugs.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute + summarise; do NOT write ssi-data.")
    parser.add_argument("--diagnose-only", action="store_true",
                        help="Diagnose module constants + input presence; no compute or write.")
    args = parser.parse_args(argv)

    if args.diagnose_only:
        _diagnose()
        return 0

    if args.all_countries:
        summaries = apply_r7_cyber_v2_to_all(dry_run=args.dry_run)
        total_populated = sum(s.get("n_populated_v2", 0) for s in summaries)
        total_fallback = sum(s.get("n_fallback_identity", 0) for s in summaries)
        print(json.dumps({
            "cohort_size": len(summaries),
            "total_populated_v2": total_populated,
            "total_fallback_identity": total_fallback,
            "per_country": summaries,
        }, indent=2, default=str))
        return 0

    if not args.country:
        parser.error("country slug required (or use --all-countries / --diagnose-only)")

    summary = apply_r7_cyber_v2_to_country(args.country, dry_run=args.dry_run)
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
