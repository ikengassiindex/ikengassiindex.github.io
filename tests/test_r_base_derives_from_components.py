"""Each R_base check must fire on the defect it names, and on nothing else.

135,844 substations carry R_base_median == 0.0. That population is two
different defects and the gate must not blur them: 57,351 have components
present and were zeroed anyway (the Wave-4 L3 regression, re-derivable), and
78,558 have no components at all (nothing to re-derive from). 78,493 of the
second group are published with a real band rather than "Unclassified".
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_r_base_derives_from_components import audit, fix_has_run, CHECKS, TOL
from pipeline.scoring.engine import compute_r_base

COMPS = {"C": 0.45, "V": 0.33, "I": 0.41, "E": 0.25, "S": 0.29, "T": 0.43}
RB = round(compute_r_base(COMPS), 4)


def rec(**over):
    """A record whose R_base really is derived from its components."""
    s = {"substation_id": "X1", "components": dict(COMPS), "R_base_median": RB,
         "mult_product": 1.25, "add_sum": 0.14, "R_median": 0.60,
         "classification": "Medium"}
    s.update(over)
    return s


def only(counts, *expected):
    fired = {k for k in CHECKS if counts[k]}
    assert fired == set(expected), f"fired {sorted(fired)}, expected {sorted(expected)}"


def test_a_derived_record_trips_nothing():
    c, _ = audit([rec()])
    only(c)


def test_zero_and_drift_fire_together_when_components_are_present():
    # uk's shape: components populated, R_base zeroed anyway.
    c, ex = audit([rec(R_base_median=0.0)])
    only(c, "ZERO", "DRIFT")
    assert ex["substation_id"] == "X1"


def test_drift_alone_when_r_base_is_wrong_but_not_zero():
    c, _ = audit([rec(R_base_median=round(RB + 0.05, 4))])
    only(c, "DRIFT")


def test_no_comps_fires_and_zero_does_not_claim_a_derivation():
    # austria/poland's shape. With no components there is nothing to derive
    # from, so ZERO and DRIFT must stay silent — blurring the two populations
    # is exactly what this test exists to prevent.
    c, _ = audit([rec(components={}, R_base_median=0.0,
                      classification="Unclassified")])
    only(c, "NO_COMPS")


def test_banded_blind_fires_when_a_blind_record_carries_a_band():
    c, _ = audit([rec(components={}, R_base_median=0.0, classification="Low")])
    only(c, "NO_COMPS", "BANDED_BLIND")


def test_only_flood_fires_when_the_score_is_the_additive_term():
    # R_median == add_sum: the composite score is the flood modifier alone.
    c, _ = audit([rec(R_median=0.14)])
    only(c, "ONLY_FLOOD")


def test_tolerance_is_the_rounding_floor():
    inside, _ = audit([rec(R_base_median=round(RB + TOL * 0.8, 6))])
    only(inside)
    outside, _ = audit([rec(R_base_median=round(RB + TOL * 1.2, 6))])
    only(outside, "DRIFT")


def test_fix_has_run_reads_the_provenance():
    assert fix_has_run({"_provenance": {"history": [
        {"action": "L3_R_base_regression_fix"}]}}) is True
    assert fix_has_run({"_provenance": {"history": [{"action": "something"}]}}) is False
    assert fix_has_run({}) is False


def test_the_real_registers_agree_with_the_finding():
    """france was fixed and records it; uk was not and does not."""
    import json
    fr = json.loads((ROOT / "france" / "ssi-data.json").read_text())
    uk = json.loads((ROOT / "uk" / "ssi-data.json").read_text())
    assert fix_has_run(fr) is True, "france should record the Wave-4 fix"
    assert fix_has_run(uk) is False, "uk should not — that is the finding"
