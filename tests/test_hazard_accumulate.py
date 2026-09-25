#!/usr/bin/env python3
"""test_hazard_accumulate.py — Sentinel for the streaming hazard accumulator

21 September 2026
=================

The accumulator is where 1-2 TB becomes tens of MB. Everything it discards is
discarded forever, so what it keeps has to be right the first time.

Sentinel class matrix
---------------------
- TestRegimeTagging — the four observing-system regimes, their boundaries, and
  the standing guarantee that the 1991-2020 normal lies inside exactly one.
- TestWelfordIsExact — mean and variance against a known series, and the
  cancellation case where sum-of-squares loses digits and Welford does not.
- TestOneObservationHasNoVariance — section 7.5: no certainty from one reading.
- TestMissingValuesAreSkippedNotZeroed — a sea-mask None must not drag a mean.
- TestPartialTimestepsAreRefused — a short row would bias silently.
- TestTheNormalReportsItsOwnCoverage — you cannot get a 1991-2020 normal from
  four years without being told it was four.
- TestFanOutIsNearestCellAndAuditable — the asset gets the cell's value and the
  cell's identity, with the same tie-break as the index.
- TestTheApiCannotAggregateBeforeEvaluating — the nonlinearity rule, enforced
  by shape: observe() takes one scalar per cell, never a stack of fields.
"""
from __future__ import annotations
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from hazard_accumulate import (  # noqa: E402
    Accumulator, CellYear, NORMAL_FROM, NORMAL_TO, fan_out, load_cell_index,
    regime_for)


class TestRegimeTagging(unittest.TestCase):
    def test_the_four_regimes_and_their_boundaries(self):
        for year, want in ((1940, "no_upper_air"), (1945, "no_upper_air"),
                           (1946, "pre_satellite"), (1969, "pre_satellite"),
                           (1970, "early_satellite"), (1978, "early_satellite"),
                           (1979, "modern"), (2025, "modern")):
            self.assertEqual(regime_for(year), want, "year %d" % year)

    def test_the_boundary_is_1970_for_satellite_not_1979(self):
        # ECMWF: "no satellite data were used before 1970". The conventional
        # shorthand pre-1979 = pre-satellite is what this pins against.
        self.assertNotEqual(regime_for(1970), regime_for(1969))
        self.assertEqual(regime_for(1975), "early_satellite")

    def test_before_the_record_is_an_error_not_a_default(self):
        with self.assertRaises(ValueError):
            regime_for(1939)

    def test_the_standard_normal_lies_inside_one_regime(self):
        self.assertEqual(
            {regime_for(y) for y in range(NORMAL_FROM, NORMAL_TO + 1)}, {"modern"})


class TestWelfordIsExact(unittest.TestCase):
    def test_mean_and_variance_of_a_known_series(self):
        cy = CellYear()
        for x in (2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0):
            cy.push(x, ())
        self.assertAlmostEqual(cy.mean, 5.0, places=12)
        self.assertAlmostEqual(cy.variance, 32.0 / 7.0, places=12)   # sample
        self.assertEqual((cy.min, cy.max), (2.0, 9.0))

    def test_it_survives_the_cancellation_that_breaks_sum_of_squares(self):
        # A near-constant series at large offset: the naive sum-of-squares form
        # subtracts two almost equal huge numbers and can even go negative.
        base = 1e9
        xs = [base + d for d in (1.0, 2.0, 3.0, 4.0, 5.0)]
        cy = CellYear()
        for x in xs:
            cy.push(x, ())
        self.assertAlmostEqual(cy.variance, 2.5, places=6)
        n = len(xs)
        naive = (sum(x * x for x in xs) - sum(xs) ** 2 / n) / (n - 1)
        self.assertGreater(abs(naive - 2.5), 1e-3,
                           "if the naive form is accurate here the test has "
                           "stopped demonstrating anything")


class TestOneObservationHasNoVariance(unittest.TestCase):
    def test_variance_of_a_single_reading_is_none_not_zero(self):
        cy = CellYear()
        cy.push(3.0, ())
        self.assertIsNone(cy.variance)
        self.assertIsNone(cy.as_dict()["sd"])

    def test_an_empty_cell_year_reports_no_extremes(self):
        d = CellYear().as_dict()
        self.assertEqual(d["n"], 0)
        self.assertIsNone(d["min"])
        self.assertIsNone(d["max"])


class TestMissingValuesAreSkippedNotZeroed(unittest.TestCase):
    def test_none_does_not_enter_the_mean(self):
        a = Accumulator("dsr", n_cells=2, resolution_deg=0.25)
        a.observe(2000, [10.0, None])
        a.observe(2000, [20.0, None])
        a.observe(2000, [30.0, 5.0])
        self.assertEqual(a.cell_year(0, 2000).n, 3)
        self.assertAlmostEqual(a.cell_year(0, 2000).mean, 20.0)
        self.assertEqual(a.cell_year(1, 2000).n, 1)
        self.assertAlmostEqual(a.cell_year(1, 2000).mean, 5.0)

    def test_a_cell_that_never_reported_stays_absent(self):
        a = Accumulator("dsr", n_cells=2, resolution_deg=0.25)
        a.observe(2000, [1.0, None])
        self.assertIsNone(a.cell_year(1, 2000))


class TestPartialTimestepsAreRefused(unittest.TestCase):
    def test_a_short_row_raises(self):
        a = Accumulator("dsr", n_cells=3, resolution_deg=0.25)
        with self.assertRaises(ValueError):
            a.observe(2000, [1.0, 2.0])

    def test_a_long_row_raises(self):
        a = Accumulator("dsr", n_cells=2, resolution_deg=0.25)
        with self.assertRaises(ValueError):
            a.observe(2000, [1.0, 2.0, 3.0])


class TestThresholdsCountExceedance(unittest.TestCase):
    def test_counts_are_per_threshold_and_inclusive(self):
        # EFFIS-style class counting: exceedance counting is a legitimate use
        # of FWI, unlike averaging it.
        a = Accumulator("fwi", n_cells=1, resolution_deg=0.25,
                        thresholds=(11.2, 21.3, 38.0))
        for x in (5.0, 11.2, 25.0, 50.0):
            a.observe(2000, [x])
        self.assertEqual(a.cell_year(0, 2000).exceed, [3, 2, 1])


class TestTheNormalReportsItsOwnCoverage(unittest.TestCase):
    def test_a_four_year_normal_says_it_is_four_years(self):
        a = Accumulator("dsr", n_cells=1, resolution_deg=0.25)
        for y in (1991, 1992, 1993, 1994):
            a.observe(y, [10.0])
        value, present, expected = a.normal(0)
        self.assertAlmostEqual(value, 10.0)
        self.assertEqual(present, 4)
        self.assertEqual(expected, 30)

    def test_the_normal_is_weighted_by_observation_count(self):
        a = Accumulator("dsr", n_cells=1, resolution_deg=0.25)
        for _ in range(9):
            a.observe(1991, [0.0])
        a.observe(1992, [10.0])
        value, present, _ = a.normal(0)
        self.assertAlmostEqual(value, 1.0)      # not 5.0, which averaging years gives
        self.assertEqual(present, 2)

    def test_no_data_in_the_window_returns_none_not_zero(self):
        a = Accumulator("dsr", n_cells=1, resolution_deg=0.25)
        a.observe(1950, [7.0])
        value, present, _ = a.normal(0)
        self.assertIsNone(value)
        self.assertEqual(present, 0)


class TestSeriesCarriesTheRegime(unittest.TestCase):
    def test_every_year_in_the_series_is_tagged(self):
        a = Accumulator("dsr", n_cells=1, resolution_deg=0.25)
        for y in (1943, 1960, 1974, 2001):
            a.observe(y, [1.0])
        got = {r["year"]: r["regime"] for r in a.series(0)}
        self.assertEqual(got, {1943: "no_upper_air", 1960: "pre_satellite",
                               1974: "early_satellite", 2001: "modern"})

    def test_summary_names_every_regime_present(self):
        a = Accumulator("dsr", n_cells=1, resolution_deg=0.25)
        a.observe(1943, [1.0])
        a.observe(2001, [1.0])
        self.assertEqual(a.summary()["regimes_present"],
                         ["modern", "no_upper_air"])


class TestFanOutIsNearestCellAndAuditable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = load_cell_index()

    def test_an_asset_gets_its_cell_ordinal_back(self):
        c = self.idx["cells"][0]
        per_cell = [float(i) for i in range(self.idx["n_cells"])]
        value, o = fan_out(per_cell, self.idx, c["lat"], c["lon_signed"])
        self.assertEqual(o, c["o"])
        self.assertEqual(value, float(c["o"]))

    def test_two_points_in_one_cell_get_the_identical_value(self):
        c = next(c for c in self.idx["cells"] if c["n"] > 1)
        per_cell = [float(i) for i in range(self.idx["n_cells"])]
        res = self.idx["resolution_deg"]
        a = fan_out(per_cell, self.idx, c["lat"] + res * 0.2, c["lon_signed"])
        b = fan_out(per_cell, self.idx, c["lat"] - res * 0.2, c["lon_signed"])
        self.assertEqual(a, b)
        self.assertEqual(a[1], c["o"])

    def test_a_point_outside_the_index_is_an_error_not_a_nearest_guess(self):
        per_cell = [0.0] * self.idx["n_cells"]
        with self.assertRaises(KeyError):
            fan_out(per_cell, self.idx, 0.0, 0.0)   # Gulf of Guinea


class TestTheApiCannotAggregateBeforeEvaluating(unittest.TestCase):
    """The nonlinearity rule, enforced by shape rather than by comment."""

    def test_observe_takes_one_scalar_per_cell_not_a_field_stack(self):
        a = Accumulator("fmiclim", n_cells=2, resolution_deg=0.25)
        with self.assertRaises((ValueError, TypeError)):
            # a caller holding RH/T/precip per cell has not yet run the
            # diagnostic, and there is no way to hand them over
            a.observe(2000, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    def test_the_accumulator_never_sees_an_input_variable_name(self):
        """No IDENTIFIER in the code names an input field or an interpolation.

        The first version of this test grepped the whole source and failed on
        the module's own docstring, which says it does not interpolate. Prose
        about a prohibition is not a violation of it. This walks the AST and
        looks only at names the code actually binds or calls.
        """
        import ast
        import hazard_accumulate as h
        tree = ast.parse(open(h.__file__, encoding="utf-8").read())
        identifiers = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                identifiers.add(node.id)
            elif isinstance(node, ast.Attribute):
                identifiers.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                identifiers.add(node.name)
                if isinstance(node, ast.FunctionDef):
                    identifiers.update(a.arg for a in node.args.args)
        lowered = " ".join(sorted(identifiers)).lower()
        for forbidden in ("relative_humidity", "humidity", "pressure_level",
                          "temperature", "precip", "interp", "bilinear"):
            self.assertNotIn(forbidden, lowered,
                             "the accumulator has acquired knowledge of inputs "
                             "or of interpolation: %r" % forbidden)


if __name__ == "__main__":
    unittest.main(verbosity=2)
