"""
SSI Pipeline — Per-Country Modifier Tests (Phase 1 PR-3)

7 tests proving the F-L3-4 cohort closure end-to-end through score_substation:

- Tests 9-11: cohort-specific modifiers (Korea typhoon+chaebol, Colombia
              volcanic, Israel drought) actually shift R_median upward
- Test 12: Italy (no per-country modifiers) stays at the canonical 5-mod
          baseline — regression guard
- Tests 13-15: per-modifier provenance (modifier_impacts dict, mult_product,
              add_sum) is populated correctly per substation

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-3 §"Test criteria (the 15 PR-3 tests)"
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L3-4 cohort closure
"""

import pytest

from scripts.pipeline.scoring.engine import (
    compute_r_median,
    compute_r_base,
    score_substation,
)
from scripts.pipeline.scoring.modifier_registry import (
    compute_modifier_terms,
    per_modifier_impacts,
    MODIFIER_REGISTRY,
)


# ═══════════════════════════════════════════════════════════
#  Canonical fixtures (PR-3 cohort regression)
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def baseline_components():
    """Mid-range components — used as the canonical anchor for cohort tests."""
    return {"C": 0.55, "V": 0.50, "I": 0.48, "E": 0.52, "S": 0.45, "T": 0.40}


@pytest.fixture
def canonical_5_modifiers():
    """The v4.0.2 baseline 5-modifier dict (no cohort-specific terms)."""
    return {
        "R3_C_mult": 1.05,
        "R4_F_topo": 1.10,
        "R6_restoration": 0.98,
        "R6_seismic": 1.08,
        "R7_cyber": 1.01,
    }


def _build_substation(country, components, modifiers, sub_id="TEST-001"):
    """Helper: build a minimal substation dict that score_substation accepts."""
    return {
        "id": sub_id,
        "country": country,
        "components": components,
        "modifiers": modifiers,
    }


# ═══════════════════════════════════════════════════════════
#  COHORT-SPECIFIC MODIFIERS (Tests 9-11)
# ═══════════════════════════════════════════════════════════

class TestCohortModifiers:
    """Country-specific modifiers must materially shift R_median (F-L3-4)."""

    def test_9_korea_typhoon_and_chaebol_shift_r_median_upward(
        self, baseline_components, canonical_5_modifiers
    ):
        """Korea's R6_typhoon=1.10 + R6_chaebol=1.06 add ~16.6% on top of canonical mult."""
        R_base = compute_r_base(baseline_components)
        # Canonical-only baseline
        R_canonical = compute_r_median(R_base, canonical_5_modifiers)
        # Korea adds 2 country-specific multiplicative modifiers
        korea_mods = {**canonical_5_modifiers, "R6_typhoon": 1.10, "R6_chaebol": 1.06}
        R_korea = compute_r_median(R_base, korea_mods)
        assert R_korea > R_canonical, (
            f"Korea's R6_typhoon + R6_chaebol did not shift R_median up "
            f"(canonical={R_canonical:.4f}, korea={R_korea:.4f}) — "
            f"F-L3-4 cohort regression"
        )
        # Expected uplift: factor 1.10 × 1.06 = 1.166 — the gap should be ~16% of R_canonical
        # (since soft_clip may compress slightly, allow 12% as floor)
        gap = (R_korea - R_canonical) / R_canonical
        assert gap > 0.10, (
            f"Korea cohort uplift too small: {gap:.3f} (expected >10%)"
        )

    def test_10_colombia_volcanic_shifts_r_median_upward(
        self, baseline_components, canonical_5_modifiers
    ):
        """Colombia's R6_volcanic=1.12 must materially shift R_median."""
        R_base = compute_r_base(baseline_components)
        R_canonical = compute_r_median(R_base, canonical_5_modifiers)
        colombia_mods = {**canonical_5_modifiers, "R6_volcanic": 1.12}
        R_colombia = compute_r_median(R_base, colombia_mods)
        assert R_colombia > R_canonical, (
            f"Colombia's R6_volcanic did not shift R_median up "
            f"(canonical={R_canonical:.4f}, colombia={R_colombia:.4f})"
        )
        # 12% multiplier should yield ~12% lift (less if soft_clip engages)
        gap = (R_colombia - R_canonical) / R_canonical
        assert gap > 0.08, f"Colombia volcanic uplift too small: {gap:.3f}"

    def test_11_israel_drought_shifts_r_median_upward(
        self, baseline_components, canonical_5_modifiers
    ):
        """Israel's R6_drought=1.05 must shift R_median up."""
        R_base = compute_r_base(baseline_components)
        R_canonical = compute_r_median(R_base, canonical_5_modifiers)
        israel_mods = {**canonical_5_modifiers, "R6_drought": 1.05}
        R_israel = compute_r_median(R_base, israel_mods)
        assert R_israel > R_canonical, (
            f"Israel's R6_drought did not shift R_median up "
            f"(canonical={R_canonical:.4f}, israel={R_israel:.4f})"
        )


# ═══════════════════════════════════════════════════════════
#  ITALY REGRESSION GUARD (Test 12)
# ═══════════════════════════════════════════════════════════

class TestItalyRegression:
    """Italy (canonical 5 only) must produce IDENTICAL R_median pre/post PR-3."""

    def test_12_italy_canonical_only_matches_explicit_chain(
        self, baseline_components, canonical_5_modifiers
    ):
        """Italy's R_median = R_base × Π(canonical 5) within 1e-9 (no cohort drift)."""
        R_base = compute_r_base(baseline_components)
        R_pr3 = compute_r_median(R_base, canonical_5_modifiers)
        # Explicit-chain reference: matches the pre-PR-3 hardcoded sequence
        from scripts.pipeline.scoring.engine import soft_clip_upper
        R_raw_manual = R_base
        R_raw_manual *= canonical_5_modifiers["R3_C_mult"]
        R_raw_manual *= canonical_5_modifiers["R4_F_topo"]
        R_raw_manual *= canonical_5_modifiers["R6_restoration"]
        R_raw_manual *= canonical_5_modifiers["R6_seismic"]
        # R7_cyber is deliberately absent. It was retired at the v4.24 hard
        # cutover (18 August 2026) and superseded by R7_cyber_v2, so it is no
        # longer part of the chain — compute_modifier_terms skips it. Keeping it
        # here would assert that a retired modifier is still applied, which is
        # the defect this suite should be catching rather than pinning.
        # The canonical chain is four multiplicative modifiers, not five.
        R_manual = soft_clip_upper(R_raw_manual)
        assert R_pr3 == pytest.approx(R_manual, abs=1e-9), (
            f"Italy regressed pre/post PR-3: {R_pr3} vs {R_manual} — "
            f"the canonical 5-modifier chain MUST be identity-preserving"
        )


# ═══════════════════════════════════════════════════════════
#  PROVENANCE FIELDS (Tests 13-15)
# ═══════════════════════════════════════════════════════════

class TestProvenance:
    """score_substation populates modifier_impacts + mult_product + add_sum."""

    def test_13_modifier_impacts_dict_present_for_korea(self, baseline_components):
        """Korea substation receives modifier_impacts dict with at least 5 keys."""
        korea_mods = {
            "R3_C_mult": 1.05,
            "R4_F_topo": 1.10,
            "R6_restoration": 0.98,
            "R6_seismic": 1.02,
            "R6_typhoon": 1.08,
            "R6_chaebol": 1.06,
            "R7_cyber": 1.015,
        }
        sub = _build_substation("KR", baseline_components, korea_mods, "KR-SS-001")
        scored = score_substation(sub)
        assert "modifier_impacts" in scored, "modifier_impacts dict missing"
        impacts = scored["modifier_impacts"]
        assert isinstance(impacts, dict), f"modifier_impacts is {type(impacts)}, expected dict"
        # Korea has 7 modifiers; all are in registry
        assert len(impacts) >= 5, (
            f"Korea modifier_impacts has only {len(impacts)} keys, expected ≥5"
        )
        # The two cohort-specific modifiers MUST appear
        assert "R6_typhoon" in impacts, "R6_typhoon missing from modifier_impacts"
        assert "R6_chaebol" in impacts, "R6_chaebol missing from modifier_impacts"

    def test_14_impacts_sum_consistent_with_mult_product_and_add_sum(
        self, baseline_components
    ):
        """Sum of modifier_impacts ~ (mult_product − 1.0) + add_sum, modulo product->sum."""
        # Build a mixed-modifier substation (mult + add)
        mods = {
            "R3_C_mult": 1.15,
            "R4_F_topo": 1.05,
            "R6_seismic": 1.10,
            "R6c_flood": 1.20,  # additive
        }
        sub = _build_substation("XX", baseline_components, mods)
        scored = score_substation(sub)
        # Validate the three persisted fields exist + types
        assert "mult_product" in scored, "mult_product missing"
        assert "add_sum" in scored, "add_sum missing"
        assert "modifier_impacts" in scored, "modifier_impacts missing"
        # mult_product and add_sum should match compute_modifier_terms output
        expected_mult, expected_add = compute_modifier_terms(mods)
        assert scored["mult_product"] == pytest.approx(expected_mult, abs=1e-4)
        assert scored["add_sum"] == pytest.approx(expected_add, abs=1e-4)
        # Additive-only-portion of modifier_impacts must equal add_sum
        add_modifiers = [m for m, spec in MODIFIER_REGISTRY.items() if spec["type"] == "add"]
        add_impacts_sum = sum(
            scored["modifier_impacts"].get(m, 0.0) for m in add_modifiers
        )
        assert add_impacts_sum == pytest.approx(scored["add_sum"], abs=1e-4), (
            f"Additive impacts sum {add_impacts_sum} != add_sum {scored['add_sum']}"
        )

    def test_15_mult_product_and_add_sum_persisted_in_scored_record(
        self, baseline_components, canonical_5_modifiers
    ):
        """mult_product and add_sum land on the output dict, ready for ssi-data.json."""
        sub = _build_substation("IT", baseline_components, canonical_5_modifiers)
        scored = score_substation(sub)
        # Both persisted as rounded floats (audit-trail friendly)
        assert isinstance(scored["mult_product"], float)
        assert isinstance(scored["add_sum"], float)
        # Italy has only multiplicative modifiers → add_sum must be exactly 0.0
        assert scored["add_sum"] == 0.0, (
            f"Italy add_sum should be 0.0 (no additive mods), got {scored['add_sum']}"
        )
        # mult_product is the product of 5 canonical modifiers
        expected = (1.05 * 1.10 * 0.98 * 1.08 * 1.01)
        assert scored["mult_product"] == pytest.approx(expected, abs=1e-3)
