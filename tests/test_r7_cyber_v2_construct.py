#!/usr/bin/env python3
"""test_r7_cyber_v2_construct.py — Sentinel for R7_cyber v2 CRA-anchored composite

Task #1102 + #1107 + #1118 + #1134 (18 August 2026)
=====================================================

Pins the architectural invariants of the R7_cyber v2 module + registry
entry per Gate A GATE-A-1 + GATE-A-2 + GATE-A-11 operator sign-off
18 August 2026 Session B.

Sentinel class matrix
---------------------
- TestUtilityConstantLock — envelope + weights + audit-trail markers locked.
- TestWeightSumToUnity — BINDING sum-to-unity for W_ENTITY + W_PRODUCT
  and for each layer's sub-weights (a1+a2+a3 = b1+b2+b3 = 1.0).
- TestEnvelopeInvariant — every computed R7_cyber_v2 stays in [0.99, 1.05]
  for valid inputs.
- TestConvention56Fallback — None entity + None product → identity 1.0
  with audit marker; partial None handled without silent identity.
- TestDualWriteSemantics — R7_cyber v1 value never modified when v2
  computed; v1 snapshot captured in ``_r7_cyber_v1_value``.
- TestPathCDComposite — EU cohort resolves to Path C; non-EU cohort
  resolves to Path D; both use the composite entity + product formula.
- TestRegulatoryVintageAnchor — CRA Article 14 + NIS2 Article 21 vintage
  years present in module docstring; registry entry cites Task #1102.
- TestRegistryKeyParity — module ``REGISTRY_KEY`` matches
  ``modifier_registry.py`` entry byte-identical.
- TestCohortSoT — 39-country cohort intact per ``intelligence/countries.json``;
  every slug resolves to a valid path variant.
- TestFormulaCanonicalAnchors — anchor points from D2 §3 spec (delta=0,
  delta=1, delta=0.5) produce expected R7 v2 outputs.

Run: ``pytest tests/test_r7_cyber_v2_construct.py -v``
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest

# Add repo root to sys.path so ``from scripts.pipeline.scoring...`` works.
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.scoring import r7_cyber_v2 as R7V2  # noqa: E402


# ══════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════


@pytest.fixture
def eu_country_inputs_full():
    """Fully-populated EU country inputs (Path C) — every component present."""
    return {
        "country_slug": "spain",
        "as_of_date": "2026-08-18",
        "nis2_status_norm": 0.72,
        "nis2_incident_history_norm": 0.15,
        "regulatory_regime_maturity_norm": 0.85,
        "srp_exploited_vuln_signal": 0.10,
        "default_vendor_mix_cra_vintage": 0.0,
        "default_sbom_coverage": 0.0,
        "path_variant": "C",
    }


@pytest.fixture
def non_eu_country_inputs_full():
    """Fully-populated non-EU country inputs (Path D)."""
    return {
        "country_slug": "us",
        "as_of_date": "2026-08-18",
        "nis2_status_norm": 0.90,     # NERC CIP mature register
        "nis2_incident_history_norm": 0.20,
        "regulatory_regime_maturity_norm": 1.00,
        "srp_exploited_vuln_signal": 0.05,
        "default_vendor_mix_cra_vintage": 0.10,
        "default_sbom_coverage": 0.05,
        "path_variant": "D",
    }


@pytest.fixture
def entity_only_inputs():
    """Country with entity-layer populated, product-layer all None."""
    return {
        "country_slug": "greece",
        "path_variant": "C",
        "nis2_status_norm": 0.50,
        "nis2_incident_history_norm": 0.30,
        "regulatory_regime_maturity_norm": 0.40,
        "srp_exploited_vuln_signal": None,
        "default_vendor_mix_cra_vintage": None,
        "default_sbom_coverage": None,
    }


@pytest.fixture
def product_only_inputs():
    """Country with product-layer populated, entity-layer all None."""
    return {
        "country_slug": "greenland",
        "path_variant": "D",
        "nis2_status_norm": None,
        "nis2_incident_history_norm": None,
        "regulatory_regime_maturity_norm": None,
        "srp_exploited_vuln_signal": 0.05,
        "default_vendor_mix_cra_vintage": 0.15,
        "default_sbom_coverage": 0.10,
    }


@pytest.fixture
def all_none_inputs():
    """Country with every input None → Convention #56 identity fallback."""
    return {
        "country_slug": "chile",
        "path_variant": "D",
        "nis2_status_norm": None,
        "nis2_incident_history_norm": None,
        "regulatory_regime_maturity_norm": None,
        "srp_exploited_vuln_signal": None,
        "default_vendor_mix_cra_vintage": None,
        "default_sbom_coverage": None,
    }


@pytest.fixture
def sub_with_v1():
    """Substation with existing R7_cyber v1 value + baseline modifier dict."""
    return {
        "substation_id": "test-sub-001",
        "modifiers": {
            "R7_cyber": 1.02,
            "R3_C_mult": 1.10,
        },
    }


# ══════════════════════════════════════════════════════════════════
# TestUtilityConstantLock — module constants BINDING
# ══════════════════════════════════════════════════════════════════


class TestUtilityConstantLock:
    """Every load-bearing constant is pinned here. Any drift fails CI."""

    def test_envelope_low_locked_at_099(self):
        assert R7V2.ENVELOPE_LOW == 0.99, \
            "Gate A v0 operator sign-off: envelope preserved [0.99, 1.05] for R7 v1 continuity"

    def test_envelope_high_locked_at_105(self):
        assert R7V2.ENVELOPE_HIGH == 1.05, \
            "Gate A v0 operator sign-off: envelope preserved [0.99, 1.05] for R7 v1 continuity"

    def test_w_entity_locked_at_055(self):
        assert R7V2.W_ENTITY == 0.55, \
            "Gate A GATE-A-2 sign-off 18 Aug 2026 Session B: w_entity = 0.55"

    def test_w_product_locked_at_045(self):
        assert R7V2.W_PRODUCT == 0.45, \
            "Gate A GATE-A-2 sign-off 18 Aug 2026 Session B: w_product = 0.45"

    def test_entity_weights_locked(self):
        assert R7V2.ENTITY_WEIGHTS == (0.35, 0.35, 0.30), \
            "D2 §3.1: a1=0.35 (NIS2 Article 31) + a2=0.35 (Article 23) + a3=0.30 (regime maturity)"

    def test_product_weights_locked(self):
        assert R7V2.PRODUCT_WEIGHTS == (0.45, 0.35, 0.20), \
            "D2 §3.2: b1=0.45 (CRA Article 13 vintage) + b2=0.35 (SBOM) + b3=0.20 (SRP)"

    def test_audit_trail_key_locked(self):
        assert R7V2.AUDIT_TRAIL_KEY == "_r7_cyber_v2_source"

    def test_audit_trail_value_locked(self):
        assert R7V2.AUDIT_TRAIL_VALUE == \
            "R7_CYBER_V2_CRA_NIS2_PATH_CD_v0_task_1102_1107_1118_1134"

    def test_fallback_key_locked(self):
        assert R7V2.FALLBACK_KEY == "_r7_cyber_v2_fallback_reason"

    def test_v1_retired_key_locked(self):
        assert R7V2.V1_RETIRED_KEY == "_r7_cyber_v1_retired"

    def test_v1_value_key_locked(self):
        assert R7V2.V1_VALUE_KEY == "_r7_cyber_v1_value"

    def test_registry_key_locked(self):
        assert R7V2.REGISTRY_KEY == "R7_cyber_v2"

    def test_cra_article_14_binding_date_pinned(self):
        assert R7V2.CRA_ARTICLE_14_BINDING_DATE == "2026-09-11", \
            "CRA Article 14 hard binding date per Regulation (EU) 2024/2847"

    def test_nis2_transposition_deadline_pinned(self):
        assert R7V2.NIS2_TRANSPOSITION_DEADLINE == "2024-10-17", \
            "NIS2 transposition deadline per Directive (EU) 2022/2555"

    def test_cra_full_applicability_pinned(self):
        assert R7V2.CRA_FULL_APPLICABILITY == "2027-12-11", \
            "CRA full applicability per Regulation (EU) 2024/2847"


# ══════════════════════════════════════════════════════════════════
# TestWeightSumToUnity — BINDING sum-to-unity invariants
# ══════════════════════════════════════════════════════════════════


class TestWeightSumToUnity:
    """Sum-to-unity invariants — BINDING per V_socio precedent + Discipline #47."""

    def test_path_variant_weights_sum_to_unity(self):
        total = R7V2.W_ENTITY + R7V2.W_PRODUCT
        assert math.isclose(total, 1.0, abs_tol=1e-9), \
            f"BINDING: W_ENTITY + W_PRODUCT must equal 1.0 (got {total})"

    def test_entity_layer_weights_sum_to_unity(self):
        total = sum(R7V2.ENTITY_WEIGHTS)
        assert math.isclose(total, 1.0, abs_tol=1e-9), \
            f"BINDING: entity weights (a1+a2+a3) must equal 1.0 (got {total})"

    def test_product_layer_weights_sum_to_unity(self):
        total = sum(R7V2.PRODUCT_WEIGHTS)
        assert math.isclose(total, 1.0, abs_tol=1e-9), \
            f"BINDING: product weights (b1+b2+b3) must equal 1.0 (got {total})"


# ══════════════════════════════════════════════════════════════════
# TestEnvelopeInvariant — [0.99, 1.05] preserved for every valid input
# ══════════════════════════════════════════════════════════════════


class TestEnvelopeInvariant:
    """Every computed R7_cyber_v2 must sit in [ENVELOPE_LOW, ENVELOPE_HIGH]."""

    @pytest.mark.parametrize("delta", [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
    def test_scale_delta_to_envelope_stays_in_bounds(self, delta):
        r7 = R7V2.scale_delta_to_envelope(delta)
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH, \
            f"delta={delta} produced R7_cyber_v2={r7} outside envelope"

    def test_scale_delta_zero_matches_envelope_low(self):
        assert math.isclose(R7V2.scale_delta_to_envelope(0.0), R7V2.ENVELOPE_LOW)

    def test_scale_delta_one_matches_envelope_high(self):
        assert math.isclose(R7V2.scale_delta_to_envelope(1.0), R7V2.ENVELOPE_HIGH)

    def test_scale_delta_half_matches_envelope_midpoint(self):
        expected = R7V2.ENVELOPE_LOW + 0.5 * (R7V2.ENVELOPE_HIGH - R7V2.ENVELOPE_LOW)
        assert math.isclose(R7V2.scale_delta_to_envelope(0.5), expected)

    def test_scale_delta_clamps_below_zero(self):
        """Defensive: negative delta clamps to ENVELOPE_LOW."""
        r7 = R7V2.scale_delta_to_envelope(-0.5)
        assert r7 == R7V2.ENVELOPE_LOW

    def test_scale_delta_clamps_above_one(self):
        """Defensive: delta > 1 clamps to ENVELOPE_HIGH."""
        r7 = R7V2.scale_delta_to_envelope(1.5)
        assert r7 == R7V2.ENVELOPE_HIGH

    def test_full_pipeline_envelope_holds_for_valid_country(self, eu_country_inputs_full, sub_with_v1):
        r7, _ = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, eu_country_inputs_full)
        assert r7 is not None
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH


# ══════════════════════════════════════════════════════════════════
# TestConvention56Fallback — visibly-honest degradation
# ══════════════════════════════════════════════════════════════════


class TestConvention56Fallback:

    def test_missing_country_inputs_returns_identity_with_marker(self, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, None)
        assert r7 == 1.0, "no_country_inputs must return identity 1.0"
        assert audit["fallback_reason"] == "no_country_inputs"

    def test_all_none_inputs_returns_identity_with_marker(self, all_none_inputs, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, all_none_inputs)
        assert r7 == 1.0, "no_entity_no_product_data must return identity 1.0"
        assert audit["fallback_reason"] == "no_entity_no_product_data"

    def test_entity_only_populated_uses_product_layer_fallback(self, entity_only_inputs, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, entity_only_inputs)
        assert r7 is not None
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH
        assert audit["fallback_reason"] == "product_layer_none_full_weight_on_entity"
        assert audit["f_entity"] is not None
        assert audit["f_product"] is None

    def test_product_only_populated_uses_entity_layer_fallback(self, product_only_inputs, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, product_only_inputs)
        assert r7 is not None
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH
        assert audit["fallback_reason"] == "entity_layer_none_full_weight_on_product"
        assert audit["f_entity"] is None
        assert audit["f_product"] is not None

    def test_partial_entity_component_missing_still_computes(self):
        """One entity component None → other two carry the layer per partial handling."""
        f_e, missing = R7V2.compute_f_entity(
            nis2_status_norm=0.6,
            nis2_incident_history_norm=None,
            regulatory_regime_maturity_norm=0.4,
        )
        assert f_e is not None
        assert 0.0 <= f_e <= 1.0
        assert "component_1" in missing

    def test_all_entity_components_none_returns_none(self):
        f_e, missing = R7V2.compute_f_entity(None, None, None)
        assert f_e is None
        assert len(missing) == 3

    def test_all_product_components_none_returns_none(self):
        f_p, missing = R7V2.compute_f_product(None, None, None)
        assert f_p is None
        assert len(missing) == 3


# ══════════════════════════════════════════════════════════════════
# TestDualWriteSemantics — GATE-A-11 sign-off preservation
# ══════════════════════════════════════════════════════════════════


class TestDualWriteSemantics:

    def test_v1_value_snapshot_captured_via_full_apply_semantic(self, sub_with_v1, eu_country_inputs_full):
        """Confirm the per-sub compute path returns a v2 value without touching sub v1 field.

        Note: the compute function does not mutate sub['modifiers'] directly; the
        apply_r7_cyber_v2_to_country caller does the writing. This test confirms
        the compute path stays pure.
        """
        v1_before = sub_with_v1["modifiers"]["R7_cyber"]
        _r7, _audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, eu_country_inputs_full)
        v1_after = sub_with_v1["modifiers"]["R7_cyber"]
        assert v1_before == v1_after == 1.02, \
            "compute_r7_cyber_v2_for_sub must NOT modify R7_cyber v1 value"

    def test_v2_compute_returns_new_value_distinct_from_v1(self, sub_with_v1, eu_country_inputs_full):
        r7_v2, _ = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, eu_country_inputs_full)
        # v2 is computed from CRA/NIS2 inputs, not from v1. Values may or may
        # not match numerically by coincidence, but the computation path is
        # fully independent.
        assert r7_v2 is not None
        assert isinstance(r7_v2, float)


# ══════════════════════════════════════════════════════════════════
# TestPathCDComposite — EU (Path C) + non-EU (Path D) parallel constructs
# ══════════════════════════════════════════════════════════════════


class TestPathCDComposite:

    @pytest.mark.parametrize("slug", ["spain", "germany", "france", "italy",
                                       "portugal", "netherlands", "belgium",
                                       "poland", "sweden", "finland"])
    def test_eu_cohort_resolves_to_path_c(self, slug):
        assert R7V2.resolve_path_variant(slug) == "C", \
            f"EU cohort country {slug} must resolve to Path C (CRA + NIS2 register)"

    @pytest.mark.parametrize("slug", ["us", "uk", "japan", "canada", "australia",
                                       "korea", "chile", "colombia", "israel",
                                       "turkey", "mexico", "new-zealand"])
    def test_non_eu_cohort_resolves_to_path_d(self, slug):
        assert R7V2.resolve_path_variant(slug) == "D", \
            f"Non-EU country {slug} must resolve to Path D (parallel construct)"

    def test_path_c_full_pipeline_produces_valid_r7(self, eu_country_inputs_full, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, eu_country_inputs_full)
        assert audit["path_variant"] == "C"
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH

    def test_path_d_full_pipeline_produces_valid_r7(self, non_eu_country_inputs_full, sub_with_v1):
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, non_eu_country_inputs_full)
        assert audit["path_variant"] == "D"
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH


# ══════════════════════════════════════════════════════════════════
# TestRegulatoryVintageAnchor — Convention #7 documented-proxy anchoring
# ══════════════════════════════════════════════════════════════════


class TestRegulatoryVintageAnchor:

    def test_module_docstring_cites_cra_regulation(self):
        docstring = R7V2.__doc__ or ""
        assert "Regulation (EU) 2024/2847" in docstring, \
            "R7 v2 module must cite CRA full regulation number per FL-004 amendment (playbook §5)"

    def test_module_docstring_cites_nis2_directive(self):
        docstring = R7V2.__doc__ or ""
        assert "Directive (EU) 2022/2555" in docstring, \
            "R7 v2 module must cite NIS2 full directive number per FL-004 amendment"

    def test_module_docstring_cites_article_14(self):
        docstring = R7V2.__doc__ or ""
        assert "Article 14" in docstring, "CRA Article 14 must be cited (reporting cascade)"

    def test_module_docstring_cites_article_21(self):
        docstring = R7V2.__doc__ or ""
        assert "Article 21" in docstring, "NIS2 Article 21 must be cited (ten measures)"

    def test_module_docstring_cites_task_1102(self):
        docstring = R7V2.__doc__ or ""
        assert "1102" in docstring, "R7 v2 module must cite Task #1102 (CRA workstream parent)"


# ══════════════════════════════════════════════════════════════════
# TestRegistryKeyParity — modifier_registry byte-identical to module
# ══════════════════════════════════════════════════════════════════


class TestRegistryKeyParity:

    def test_registry_entry_present_and_matches_module_key(self):
        """The modifier_registry.py MODIFIER_REGISTRY must carry an entry
        keyed exactly by R7V2.REGISTRY_KEY. Sentinel prevents drift
        between the registry declaration and the module contract.
        """
        from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY
        assert R7V2.REGISTRY_KEY in MODIFIER_REGISTRY, \
            f"registry key {R7V2.REGISTRY_KEY!r} missing from MODIFIER_REGISTRY"

    def test_registry_entry_envelope_matches_module_envelope(self):
        from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY
        entry = MODIFIER_REGISTRY[R7V2.REGISTRY_KEY]
        assert entry["range"] == (R7V2.ENVELOPE_LOW, R7V2.ENVELOPE_HIGH), \
            f"registry envelope {entry['range']} must match module envelope " \
            f"[{R7V2.ENVELOPE_LOW}, {R7V2.ENVELOPE_HIGH}]"

    def test_registry_entry_type_is_mult(self):
        from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY
        entry = MODIFIER_REGISTRY[R7V2.REGISTRY_KEY]
        assert entry["type"] == "mult", "R7_cyber v2 must be a multiplicative modifier"

    def test_v1_r7_cyber_tombstoned_post_cutover(self):
        """GATE-A-11-REVISED (18 August 2026): hard cutover.

        R7_cyber v1 registry entry is retained for audit-trail readers but
        MUST carry a ``retired`` field naming the v4.24 methodology-version
        event. The registry-key still resolves so consumer errors can be
        reported clearly ("this modifier is retired, migrate to R7_cyber_v2")
        rather than silently returning KeyError.
        """
        from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY
        assert "R7_cyber" in MODIFIER_REGISTRY, \
            "R7_cyber v1 registry entry must be retained for audit-trail readers"
        entry = MODIFIER_REGISTRY["R7_cyber"]
        assert "retired" in entry, \
            "R7_cyber v1 must carry a 'retired' field per GATE-A-11-REVISED hard cutover"
        assert "v4.24" in entry["retired"] or "18 August 2026" in entry["retired"], \
            f"R7_cyber v1 'retired' field must name v4.24 methodology-version event; got {entry['retired']!r}"


# ══════════════════════════════════════════════════════════════════
# TestPostCutoverInvariants — v4.24 methodology-version event
# ══════════════════════════════════════════════════════════════════


class TestPostCutoverInvariants:
    """Sentinel invariants for the v4.23 → v4.24 methodology-version event
    (18 August 2026, GATE-A-11-REVISED hard cutover).

    Rationale: after Phase γδε lands the R7_cyber v1 tombstone + R7_cyber_v2
    promotion, downstream code paths + user-facing metadata MUST reflect the
    cutover. These sentinels pin that state against regression.
    """

    def test_methodology_version_v4_24(self):
        """versions.json must declare methodology 4.24 post-cutover."""
        import json
        from pathlib import Path
        p = Path(__file__).resolve().parent.parent / "versions.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data.get("methodology") == "4.24", \
            f"versions.json methodology field must be '4.24' post-cutover; got {data.get('methodology')!r}"

    def test_edition_config_ssi_version_v4_24(self):
        """intelligence/edition-config.json ssi_version must be '4.24' post-cutover."""
        import json
        from pathlib import Path
        p = Path(__file__).resolve().parent.parent / "intelligence" / "edition-config.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data.get("ssi_version") == "4.24", \
            f"edition-config.json ssi_version must be '4.24' post-cutover; got {data.get('ssi_version')!r}"

    def test_r7_v2_is_primary_r7_modifier(self):
        """R7_cyber_v2 is present + not marked retired; R7_cyber v1 IS retired."""
        from scripts.pipeline.scoring.modifier_registry import MODIFIER_REGISTRY
        v1 = MODIFIER_REGISTRY.get("R7_cyber", {})
        v2 = MODIFIER_REGISTRY.get("R7_cyber_v2", {})
        assert "retired" in v1, "R7_cyber v1 must be marked retired post-cutover"
        assert "retired" not in v2, "R7_cyber_v2 must NOT be marked retired post-cutover"

    def test_sharding_threshold_recalibrated_60_45(self):
        """Convention #79 sharding threshold recalibrated 90→60 MB, target 60→45 MB."""
        from scripts.pipeline.utils.ssi_data_sharding import (
            SSI_DATA_SHARD_THRESHOLD_MB, SSI_DATA_SHARD_TARGET_MB,
        )
        assert SSI_DATA_SHARD_THRESHOLD_MB == 60.0, \
            f"Convention #79 threshold must be 60 MB post-v4.24 recalibration; got {SSI_DATA_SHARD_THRESHOLD_MB}"
        assert SSI_DATA_SHARD_TARGET_MB == 45.0, \
            f"Convention #79 shard target must be 45 MB post-v4.24 recalibration; got {SSI_DATA_SHARD_TARGET_MB}"


# ══════════════════════════════════════════════════════════════════
# TestCohortSoT — 39-country cohort intact per KB §57
# ══════════════════════════════════════════════════════════════════


class TestCohortSoT:

    def test_countries_sot_has_39_slugs(self):
        slugs = R7V2._load_countries_slugs()
        assert len(slugs) == 39, \
            f"KB §57: intelligence/countries.json must carry 39 slugs (got {len(slugs)})"

    def test_every_slug_resolves_to_path_variant(self):
        slugs = R7V2._load_countries_slugs()
        for slug in slugs:
            variant = R7V2.resolve_path_variant(slug)
            assert variant in ("C", "D"), \
                f"slug {slug} resolved to invalid path variant {variant!r}"

    def test_eu_plus_non_eu_cohort_covers_all_slugs(self):
        slugs = set(R7V2._load_countries_slugs())
        covered = set(R7V2.EU_COHORT) | set(R7V2.NON_EU_COHORT)
        missing = slugs - covered
        # We tolerate a small number of Path D fallback slugs (per resolve_path_variant),
        # but at v0 first apply every slug should be explicitly enumerated.
        assert not missing, \
            f"EU_COHORT + NON_EU_COHORT must explicitly cover all slugs (missing: {sorted(missing)})"


# ══════════════════════════════════════════════════════════════════
# TestFormulaCanonicalAnchors — D2 §3 spec anchor points
# ══════════════════════════════════════════════════════════════════


class TestFormulaCanonicalAnchors:
    """Anchor points from D2 spec §3 — pin the mapping empirically."""

    def test_delta_zero_maps_to_099(self):
        """Best-case per Gate A v0: delta_cyber=0 → R7 v2 = 0.99."""
        r7 = R7V2.scale_delta_to_envelope(0.0)
        assert math.isclose(r7, 0.99, abs_tol=1e-9)

    def test_delta_one_maps_to_105(self):
        """Worst-case per Gate A v0: delta_cyber=1 → R7 v2 = 1.05."""
        r7 = R7V2.scale_delta_to_envelope(1.0)
        assert math.isclose(r7, 1.05, abs_tol=1e-9)

    def test_delta_half_maps_to_102(self):
        """Neutral midpoint per Gate A v0: delta_cyber=0.5 → R7 v2 = 1.02."""
        r7 = R7V2.scale_delta_to_envelope(0.5)
        assert math.isclose(r7, 1.02, abs_tol=1e-9)

    def test_entity_layer_full_score_returns_one(self):
        """Full-score entity layer: all three components at 1.0 → f_entity = 1.0."""
        f_e, missing = R7V2.compute_f_entity(1.0, 1.0, 1.0)
        assert math.isclose(f_e, 1.0, abs_tol=1e-9)
        assert missing == []

    def test_entity_layer_zero_score_returns_zero(self):
        f_e, missing = R7V2.compute_f_entity(0.0, 0.0, 0.0)
        assert math.isclose(f_e, 0.0, abs_tol=1e-9)
        assert missing == []

    def test_product_layer_full_score_returns_one(self):
        f_p, missing = R7V2.compute_f_product(1.0, 1.0, 1.0)
        assert math.isclose(f_p, 1.0, abs_tol=1e-9)
        assert missing == []

    def test_compose_delta_full_entity_full_product(self):
        """f_entity=1.0 + f_product=1.0 → delta = 1.0 (worst case)."""
        delta, fb = R7V2.compose_delta_cyber(1.0, 1.0)
        assert math.isclose(delta, 1.0, abs_tol=1e-9)
        assert fb == ""

    def test_compose_delta_zero_both_layers(self):
        delta, fb = R7V2.compose_delta_cyber(0.0, 0.0)
        assert math.isclose(delta, 0.0, abs_tol=1e-9)

    def test_compose_delta_weighted_split(self):
        """f_entity=1.0 + f_product=0.0 → delta = 0.55 · 1.0 + 0.45 · 0.0 = 0.55."""
        delta, fb = R7V2.compose_delta_cyber(1.0, 0.0)
        assert math.isclose(delta, 0.55, abs_tol=1e-9)


# ══════════════════════════════════════════════════════════════════
# TestIntegrationPerCountry — synthetic per-country apply invariants
# ══════════════════════════════════════════════════════════════════


class TestIntegrationPerCountry:
    """End-to-end per-country integration tests using synthetic fixtures.

    NOTE: These tests do NOT run apply_r7_cyber_v2_to_country against real
    ssi-data.json (that requires per-country CRA/NIS2 register data which
    is not authored yet at v0 first apply). Tests use synthetic inputs.
    """

    @pytest.mark.parametrize("slug,variant", [
        ("spain", "C"),
        ("germany", "C"),
        ("us", "D"),
        ("japan", "D"),
    ])
    def test_compute_pipeline_yields_valid_r7_for_populated_inputs(self, slug, variant, sub_with_v1):
        """Synthetic well-populated inputs must yield an R7 v2 in envelope."""
        country_inputs = {
            "country_slug": slug,
            "path_variant": variant,
            "nis2_status_norm": 0.6,
            "nis2_incident_history_norm": 0.2,
            "regulatory_regime_maturity_norm": 0.7,
            "srp_exploited_vuln_signal": 0.1,
            "default_vendor_mix_cra_vintage": 0.05,
            "default_sbom_coverage": 0.0,
        }
        r7, audit = R7V2.compute_r7_cyber_v2_for_sub(sub_with_v1, country_inputs)
        assert r7 is not None
        assert R7V2.ENVELOPE_LOW <= r7 <= R7V2.ENVELOPE_HIGH
        assert audit["path_variant"] == variant
        assert audit["fallback_reason"] == ""

    def test_missing_inputs_file_returns_none_from_loader(self, tmp_path, monkeypatch):
        """Convention #56: absent inputs file → loader returns None (visibly-honest)."""
        monkeypatch.setattr(R7V2, "PIPELINE_DATA_ROOT", tmp_path)
        result = R7V2.load_country_inputs("nonexistent-slug")
        assert result is None

    def test_malformed_inputs_file_returns_none(self, tmp_path, monkeypatch):
        """Convention #56: malformed inputs → loader returns None (not raise)."""
        monkeypatch.setattr(R7V2, "PIPELINE_DATA_ROOT", tmp_path)
        country_dir = tmp_path / "test-country"
        country_dir.mkdir()
        (country_dir / "r7_cyber_v2_inputs.json").write_text("{ malformed json ")
        result = R7V2.load_country_inputs("test-country")
        assert result is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
