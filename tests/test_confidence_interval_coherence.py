"""Each coherence check must fire on the defect it names, and on nothing else.

A gate is only worth its baseline if every check has been shown to catch the
thing it claims to catch. These build the six defects deliberately and assert
one hit each -- so a future edit that quietly neuters a check fails here rather
than reporting a clean cohort.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from check_confidence_interval_coherence import audit, classify_confidence, CHECKS
from enrich_esg_gaps import vary


def clean(**over):
    """A record that should trip nothing: ordered, real width, honest tier."""
    s = {"name": "Clean Substation", "R_median": 0.60,
         "R_P5": 0.55, "R_P95": 0.68, "CI_width": 0.13,
         "add_sum": 0.10, "confidence_tier": "medium"}
    s.update(over)
    return s


def only(counts, *expected):
    fired = {k for k in CHECKS if counts[k]}
    assert fired == set(expected), f"fired {sorted(fired)}, expected {sorted(expected)}"


def test_clean_record_trips_nothing():
    c, _ = audit([clean()])
    only(c)


def test_order_fires_when_p95_is_below_the_median():
    # The live shape: both endpoints below the median they should bracket.
    c, _ = audit([clean(R_P5=0.14, R_P95=0.20, CI_width=0.06,
                        confidence_tier="high")])
    only(c, "ORDER")


def test_degenerate_and_impostor_fire_on_the_add_sum_overwrite():
    # R_P5 == R_P95 == add_sum: the 534,443-record corruption exactly.
    c, _ = audit([clean(R_P5=0.10, R_P95=0.10, add_sum=0.10,
                        CI_width=0.0, confidence_tier=None)])
    only(c, "ORDER", "DEGENERATE", "IMPOSTOR")


def test_width_fires_when_ci_width_contradicts_the_endpoints():
    c, _ = audit([clean(CI_width=0.99)])
    only(c, "WIDTH")


def test_synthetic_fires_on_a_name_hashed_width():
    name = "Substation 1000000000"
    w = vary(0.22, name, 0.15)
    # Endpoints kept consistent with w so only SYNTHETIC fires.
    c, _ = audit([clean(name=name, R_median=0.60,
                        R_P5=round(0.60 - w / 2, 4), R_P95=round(0.60 + w / 2, 4),
                        CI_width=w, confidence_tier=classify_confidence(
                            round(0.60 - w / 2, 4), round(0.60 + w / 2, 4)))])
    only(c, "SYNTHETIC")


def test_tier_fires_on_the_hardcoded_literal():
    # CI of 0.03 is 'high'; the register says 'medium' because it is a literal.
    c, _ = audit([clean(R_P5=0.58, R_P95=0.61, CI_width=0.03,
                        confidence_tier="medium")])
    only(c, "TIER")


def test_tier_expects_none_where_there_is_no_basis():
    # engine.classify_confidence returns None for a zero-width interval;
    # a record honestly carrying None must not be reported as a tier mismatch.
    c, _ = audit([clean(R_P5=0.10, R_P95=0.10, R_median=0.10,
                        add_sum=0.99, CI_width=0.0, confidence_tier=None)])
    only(c, "DEGENERATE")


def test_missing_fields_do_not_fire_anything():
    # Convention #56: absent is not wrong. A pre-L3 record trips no check.
    c, _ = audit([{"name": "Pre-L3", "R_median": None, "R_P5": None,
                   "R_P95": None, "CI_width": None, "add_sum": None,
                   "confidence_tier": None}])
    only(c)
