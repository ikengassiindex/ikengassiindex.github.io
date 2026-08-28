"""Pin the rule that a zero-width interval is not high confidence.

classify_confidence answered "high" for a confidence interval of width zero,
because `ci <= 0.10` is true when ci is 0 and a zero-width interval is exactly
what you get when no Monte Carlo runs. 78,638 substations were published as
high-confidence on that basis, including 13,979 of austria's 14,720 and all
25,517 of poland's unscored population.

The failure is not a wrong number. It is a claim of precision standing in for
the absence of a measurement, which no downstream reader can distinguish from
the real thing.

These cases exist so that reverting the guard fails the suite rather than
quietly restoring 78,638 unearned "high" labels.
"""
from __future__ import annotations

import pytest

from scripts.pipeline.scoring.engine import classify_confidence

# The narrowest interval a real 10,000-iteration simulation produced anywhere in
# the cohort, measured 27 August 2026 across eight countries. Every degenerate
# record sits at exactly 0.0, so the two populations do not overlap and the
# guard cannot swallow a genuine estimate.
NARROWEST_REAL = 0.042


class TestNoSimulationIsNotConfidence:
    def test_zero_width_interval_has_no_tier(self):
        assert classify_confidence(0.5, 0.5) is None

    @pytest.mark.parametrize("v", [0.0, 0.25, 0.9999, 1.30])
    def test_zero_width_at_any_level_has_no_tier(self, v):
        # It is the width that carries the information, not where it sits.
        assert classify_confidence(v, v) is None

    @pytest.mark.parametrize("p5,p95", [(None, 0.5), (0.5, None), (None, None)])
    def test_absent_percentiles_have_no_tier(self, p5, p95):
        # Previously "medium" — the same silent default wearing a different
        # number. A substation whose percentiles were never computed does not
        # have a middling confidence; it has none.
        assert classify_confidence(p5, p95) is None


class TestRealIntervalsAreUnaffected:
    def test_the_narrowest_real_interval_still_reads_high(self):
        assert classify_confidence(0.40, 0.40 + NARROWEST_REAL) == "high"

    @pytest.mark.parametrize("width,tier", [
        (0.050, "high"),
        (0.100, "high"),      # boundary, inclusive
        (0.101, "medium"),
        (0.250, "medium"),    # boundary, inclusive
        (0.251, "low"),
        (0.350, "low"),
    ])
    def test_bands_are_unchanged(self, width, tier):
        assert classify_confidence(0.40, 0.40 + width) == tier

    def test_the_guard_cannot_reach_a_real_interval(self):
        """The guard triggers at 1e-9; the narrowest real interval is 0.042,
        seven orders of magnitude away. Asserted from the low side — a width of
        1e-6 is already far below anything a simulation produces and must still
        come back as a tier rather than None.

        Not asserted at 1e-9 itself: 0.4 + 1e-9 minus 0.4 evaluates to
        1.0000000116e-09 in binary floating point, so such a test would be
        pinning float representation rather than the rule.
        """
        assert classify_confidence(0.4, 0.4 + 1e-6) == "high"
        assert classify_confidence(0.4, 0.4) is None


def test_the_old_behaviour_is_genuinely_gone():
    """The specific regression: a zero-width interval must never again return
    the string that 78,638 records were published with."""
    assert classify_confidence(0.6, 0.6) != "high"


class TestTheConsumersSurviveIt:
    """The guard changed a return type, and the damage from that lands in the
    callers, not the function. The isolation tests above all passed while
    compute_fleet_summary raised KeyError on 632,270 records, because it uses
    the tier as a dict key. These call a consumer."""

    def _fleet(self):
        from scripts.pipeline.scoring.engine import compute_fleet_summary
        return compute_fleet_summary([
            # real simulation
            {"R_median": 0.50, "R_P5": 0.45, "R_P95": 0.58, "components": {"C": 0.4}},
            # zero-width: no simulation ran
            {"R_median": 0.30, "R_P5": 0.30, "R_P95": 0.30, "components": {}},
            # percentiles never computed
            {"R_median": None, "components": {}},
        ])

    def test_a_zero_width_record_does_not_raise(self):
        assert self._fleet()  # KeyError: None before the fix

    def test_absent_tiers_are_counted_not_dropped(self):
        c = self._fleet()["confidence_tiers"]
        assert sum(c.values()) == 3, f"a substation went missing from the tally: {c}"
        assert c["Unclassified"] == 2
        assert c["medium"] == 1

    def test_the_three_real_tiers_still_exist(self):
        # map.js and remediate_cross_border.py both read these by name.
        for k in ("high", "medium", "low"):
            assert k in self._fleet()["confidence_tiers"]
