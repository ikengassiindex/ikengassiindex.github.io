"""
Arithmetic sentinels for M-001 (retired-modifier exclusion) and
M-006 (soft_clip_upper continuity).

Rationale — why these are ARITHMETIC and not METADATA assertions.
Both defects survived a GREEN suite because the existing sentinels
asserted the presence of documentation rather than the behaviour of
the arithmetic:

  * `test_v1_r7_cyber_tombstoned_post_cutover` asserts that a "retired"
    STRING exists in the registry dict. It passed while R7_cyber v1 was
    still being multiplied into the product on 31,247 substations.
  * `soft_clip_upper` was reviewed and carried forward as "well-defined,
    no edge cases" while discontinuous by 0.731 at exactly the band
    boundary the index exists to identify.

Each assertion below fails against the pre-fix code.

Convention #55 (verify-don't-trust) · Convention #56 (visibly-honest).
"""
import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.scoring.engine import (  # noqa: E402
    BANDS,
    _soft_clip_upper_vectorized,
    soft_clip_upper,
)
from scripts.pipeline.scoring.modifier_registry import (  # noqa: E402
    MODIFIER_REGISTRY,
    compute_modifier_terms,
    per_modifier_impacts,
)


class TestM001RetiredModifierExclusion:
    """A retired modifier must not contribute to the multiplicative product."""

    def test_retired_v1_excluded_from_product(self):
        assert compute_modifier_terms(
            {"R7_cyber": 1.05, "R7_cyber_v2": 1.02}
        ) == (1.02, 0.0)

    def test_retired_v1_excluded_from_audit_impacts(self):
        impacts = per_modifier_impacts({"R7_cyber": 1.05, "R7_cyber_v2": 1.02})
        assert "R7_cyber" not in impacts
        assert impacts == {"R7_cyber_v2": 0.02}

    def test_live_modifiers_unaffected(self):
        assert compute_modifier_terms({"R3_C_mult": 1.10}) == (1.1, 0.0)

    def test_additive_modifiers_unaffected(self):
        mult, add = compute_modifier_terms({"R6c_flood": 1.15})
        assert mult == 1.0
        assert add == pytest.approx(0.15)

    def test_every_retired_entry_is_excluded(self):
        """Generalises past R7 — any future v1/v2 sibling pair is covered."""
        for name, spec in MODIFIER_REGISTRY.items():
            if not spec.get("retired"):
                continue
            probe = max(spec["range"])
            mult, add = compute_modifier_terms({name: probe})
            assert (mult, add) == (1.0, 0.0), (
                f"retired modifier {name!r} still contributes: {(mult, add)}"
            )


class TestM006SoftClipContinuity:
    """soft_clip_upper must be continuous, monotone, and respect the band ceiling."""

    def test_continuous_at_threshold(self):
        assert abs(soft_clip_upper(1.0 + 1e-9) - soft_clip_upper(1.0)) < 1e-6

    def test_identity_below_threshold(self):
        for x in (0.0, 0.25, 0.5, 0.75, 0.99, 1.0):
            assert soft_clip_upper(x) == pytest.approx(x)

    def test_monotone_non_decreasing(self):
        grid = [0.5 + 0.01 * i for i in range(201)]
        for a, b in zip(grid, grid[1:]):
            assert soft_clip_upper(a) <= soft_clip_upper(b), (
                f"non-monotone between {a} and {b}"
            )

    def test_band_ceiling_holds(self):
        """max R_final = saturated multiplicative + max additive == band ceiling."""
        max_add = MODIFIER_REGISTRY["R6c_flood"]["range"][1] - 1.0
        band_max = BANDS[-1]["max"]
        assert soft_clip_upper(1e6) + max_add == pytest.approx(band_max)

    def test_extreme_band_reachable_multiplicatively(self):
        """A substation at high multiplicative stress must reach Extreme."""
        extreme_min = BANDS[-1]["min"]
        assert soft_clip_upper(1.30) >= extreme_min

    def test_scalar_and_vectorized_agree(self):
        """The Monte Carlo path uses the vectorized twin — they must not diverge."""
        grid = np.array([0.5 + 0.01 * i for i in range(201)])
        assert np.allclose(
            _soft_clip_upper_vectorized(grid),
            np.array([soft_clip_upper(float(x)) for x in grid]),
        )
