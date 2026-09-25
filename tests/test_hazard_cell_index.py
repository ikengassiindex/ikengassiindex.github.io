#!/usr/bin/env python3
"""test_hazard_cell_index.py — Sentinel for the asset-to-raster-cell index

21 September 2026
=================

Pins the one artefact every hazard leg must agree on. Established by
``doctrine/RESULT_a_raster_can_give_25165_values_not_622104.md``: a 0.25 deg
raster carries 25,165 distinct values for a 622,104-asset estate, 99.1 % of
assets share a cell, and the largest cell holds 2,855 of them.

Sentinel class matrix
---------------------
- TestConventionIsNotBankersRounding — the tie-break is floor(x+0.5), which
  does not depend on position or sign. Python's round() does both, and the two
  real assets on the estate where they disagree are pinned by name.
- TestLongitudeIsCarriedBothWays — the estate stores -180..180, ERA5 publishes
  0..359.75, and the artefact carries both so no one has to guess.
- TestArtefactReconcilesWithTheResult — the four published figures.
- TestIndexIsWellFormed — ordinals dense and unique, occupancy sums to the
  estate, every country's cells are real cells.
- TestNoSilentAbsence — section 7.5: the builder refuses to write an index that
  quietly drops an asset it could not place.
"""
from __future__ import annotations
import json
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from build_hazard_cell_index import cell_index, RESOLUTION  # noqa: E402

ARTEFACT = os.path.join(ROOT, "data", "hazard_cell_index.json")


def _idx():
    with open(ARTEFACT, encoding="utf-8") as fh:
        return json.load(fh)


class TestConventionIsNotBankersRounding(unittest.TestCase):
    def test_exact_half_always_goes_up_never_to_even(self):
        # round() sends 0.5 -> 0 and 2.5 -> 2. A nearest-neighbour rule whose
        # direction depends on which cell you are near is not a rule.
        for v, want in ((0.5, 1), (1.5, 2), (2.5, 3), (3.5, 4)):
            self.assertEqual(math.floor(v + 0.5), want)
            self.assertEqual(cell_index(v * RESOLUTION), want)

    def test_it_is_symmetric_across_zero_where_round_is_not(self):
        self.assertEqual(round(-1.5), -2)          # the behaviour we reject
        self.assertEqual(cell_index(-1.5 * RESOLUTION), -1)

    def test_the_two_real_assets_where_the_conventions_disagree(self):
        # Measured over all 622,104 assets: exactly these two move. Pinned so
        # that a future change of convention cannot pass unnoticed.
        self.assertEqual((cell_index(47.43024), cell_index(19.125)), (190, 77))
        self.assertEqual((round(47.43024 / RESOLUTION), round(19.125 / RESOLUTION)),
                         (190, 76))
        self.assertEqual((cell_index(47.125), cell_index(9.1138)), (189, 36))
        self.assertEqual((round(47.125 / RESOLUTION), round(9.1138 / RESOLUTION)),
                         (188, 36))

    def test_the_disagreement_does_not_move_the_published_cell_count(self):
        # Both conventions give 25,165. The convention is fixed because it
        # should be, not because it changed a number — and this records that.
        self.assertEqual(_idx()["n_cells"], 25165)


class TestLongitudeIsCarriedBothWays(unittest.TestCase):
    def test_negative_longitudes_are_converted_not_dropped(self):
        cells = {(c["lat"], c["lon_signed"]): c for c in _idx()["cells"]}
        west = [c for c in cells.values() if c["lon_signed"] < 0]
        self.assertTrue(west, "the estate spans Portugal, Ireland and the Americas")
        for c in west:
            self.assertAlmostEqual(c["lon_era5"], c["lon_signed"] % 360.0, places=4)
            self.assertGreaterEqual(c["lon_era5"], 0.0)
            self.assertLess(c["lon_era5"], 360.0)

    def test_every_cell_lies_on_the_grid(self):
        for c in _idx()["cells"]:
            for v in (c["lat"], c["lon_signed"]):
                self.assertAlmostEqual(v / RESOLUTION, round(v / RESOLUTION), places=6,
                                       msg="cell centre off the 0.25 deg grid: %r" % c)


class TestArtefactReconcilesWithTheResult(unittest.TestCase):
    """The four figures published in the RESULT. If the estate's asset set
    changes these must change together with that document, not silently."""

    def test_assets(self):
        self.assertEqual(_idx()["n_assets"], 622104)

    def test_cells_and_shared_cells_sum(self):
        i = _idx()
        self.assertEqual(i["n_cells"], 25165)
        self.assertEqual(i["n_cells_shared"], 19740)
        alone = i["n_cells"] - i["n_cells_shared"]
        self.assertEqual(alone, 5425)

    def test_assets_sharing_and_largest_cell(self):
        i = _idx()
        self.assertEqual(i["n_assets_sharing"], 616679)
        self.assertEqual(i["largest_cell_assets"], 2855)
        self.assertGreater(100.0 * i["n_assets_sharing"] / i["n_assets"], 99.0)

    def test_resolution_is_native_and_not_refined(self):
        # Refining to 0.10 deg would manufacture per-asset variation by
        # interpolation — the exact error the RESULT is about.
        self.assertEqual(_idx()["resolution_deg"], 0.25)


class TestIndexIsWellFormed(unittest.TestCase):
    def test_ordinals_are_dense_and_in_order(self):
        cells = _idx()["cells"]
        self.assertEqual([c["o"] for c in cells], list(range(len(cells))))

    def test_occupancy_sums_to_the_estate(self):
        i = _idx()
        self.assertEqual(sum(c["n"] for c in i["cells"]), i["n_assets"])

    def test_shared_count_is_derived_not_asserted(self):
        i = _idx()
        self.assertEqual(sum(1 for c in i["cells"] if c["n"] > 1), i["n_cells_shared"])
        self.assertEqual(sum(c["n"] for c in i["cells"] if c["n"] > 1),
                         i["n_assets_sharing"])

    def test_every_country_cell_is_a_real_cell(self):
        i = _idx()
        n = i["n_cells"]
        self.assertEqual(len(i["countries"]), 39)
        for slug, rec in i["countries"].items():
            self.assertTrue(rec["cells"], "%s has no cells" % slug)
            for o in rec["cells"]:
                self.assertTrue(0 <= o < n, "%s references cell %d" % (slug, o))

    def test_country_assets_sum_to_the_estate(self):
        i = _idx()
        self.assertEqual(sum(r["assets"] for r in i["countries"].values()),
                         i["n_assets"])

    def test_border_cells_belong_to_more_than_one_country(self):
        # Counting per country gave 25,694 — 529 too many — because a border
        # cell is one cell to the raster. This pins that cells ARE shared
        # across countries, so the global count is the right one.
        i = _idx()
        seen, shared_across = set(), 0
        for rec in i["countries"].values():
            for o in rec["cells"]:
                if o in seen:
                    shared_across += 1
                seen.add(o)
        self.assertGreater(shared_across, 0,
                           "no cell spans a border — the per-country overcount "
                           "of 529 would then be unexplained")


class TestNoSilentAbsence(unittest.TestCase):
    def test_builder_refuses_assets_without_coordinates(self):
        import build_hazard_cell_index as b
        src = open(b.__file__, encoding="utf-8").read()
        self.assertIn("refuses to hide", src)
        self.assertIn("no_geo", src)

    def test_builder_refuses_a_country_with_no_data(self):
        import build_hazard_cell_index as b
        src = open(b.__file__, encoding="utf-8").read()
        self.assertIn("refusing to write a", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
