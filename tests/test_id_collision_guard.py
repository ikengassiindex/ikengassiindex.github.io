"""A repeated substation_id is not always a duplicate.

australia, 28 August 2026. 438 ids appeared more than once. 436 of those
groups held byte-identical records — one substation stored twice or three
times. Two did not, and one of those two, AU_v43_a8df26153d28, held Buronga
substation at 330 kV and Buronga Switching Station at 220 kV, 218 m apart.

write_country keeps whichever record comes first in file order and discards
the rest, so the dedupe would have deleted a real 220 kV switching station and
counted it among 506 duplicates removed. The grid-geo delta would have moved
by one, inside tolerance. Nothing else would have shown it.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from scripts.ssi_dedupe_substations import (  # noqa: E402
    _same_facility, _assert_ids_are_not_collisions)


def sub(sid, name, kv, lat, lon, **kw):
    d = {"substation_id": sid, "name": name, "voltage_kv": kv,
         "lat": lat, "lon": lon}
    d.update(kw)
    return d


# The two australia cases, at their real coordinates.
BURONGA_330 = sub("AU_v43_a8df26153d28", "Buronga substation", 330.0,
                  -34.1026346, 142.2571684, R_median=0.2404)
BURONGA_220 = sub("AU_v43_a8df26153d28", "Buronga Switching Station", 220.0,
                  -34.1030741, 142.2594744, R_median=0.1885)
WODONGA_A = sub("AU_v43_4c6b0408d5f7", "Wodonga Terminal Station", 330.0,
                -36.155093, 146.949985, R_median=0.2415)
WODONGA_B = sub("AU_v43_4c6b0408d5f7", "Wodonga Terminal Station", 330.0,
                -36.155018, 146.949985, R_median=0.2415)


class TestSameFacility:
    def test_wodonga_is_one_site_recorded_twice(self):
        # 8 m apart, identical name, voltage and score. Must still collapse —
        # a guard that refused this would block a legitimate dedupe.
        assert _same_facility(WODONGA_A, WODONGA_B)

    def test_buronga_is_two_sites_sharing_an_id(self):
        assert not _same_facility(BURONGA_330, BURONGA_220)

    def test_a_different_name_alone_is_enough(self):
        a = sub("X", "Alpha", 110.0, 50.0, 5.0)
        b = sub("X", "Beta", 110.0, 50.0, 5.0)
        assert not _same_facility(a, b)

    def test_a_different_voltage_alone_is_enough(self):
        a = sub("X", "Alpha", 110.0, 50.0, 5.0)
        b = sub("X", "Alpha", 220.0, 50.0, 5.0)
        assert not _same_facility(a, b)

    def test_distance_alone_is_enough(self):
        # Same name and voltage but 1 km apart: two sites, not jitter.
        a = sub("X", "Alpha", 110.0, 50.0, 5.0)
        b = sub("X", "Alpha", 110.0, 50.009, 5.0)
        assert not _same_facility(a, b)

    def test_missing_coordinates_are_not_assumed_equal(self):
        # Convention #56: absent data degrades visibly, it does not default
        # to the convenient answer.
        a = sub("X", "Alpha", 110.0, 50.0, 5.0)
        b = {"substation_id": "X", "name": "Alpha", "voltage_kv": 110.0}
        assert not _same_facility(a, b)

    def test_identical_records_pass(self):
        assert _same_facility(BURONGA_330, dict(BURONGA_330))


class TestTheGuard:
    def test_a_clean_country_passes_silently(self):
        _assert_ids_are_not_collisions("nowhere", [
            sub("A", "One", 110.0, 50.0, 5.0),
            sub("B", "Two", 110.0, 51.0, 5.0),
        ])

    def test_a_genuine_duplicate_passes(self):
        _assert_ids_are_not_collisions("nowhere", [WODONGA_A, WODONGA_B])

    def test_a_collision_aborts(self, capsys):
        with pytest.raises(SystemExit) as e:
            _assert_ids_are_not_collisions("australia",
                                           [BURONGA_330, BURONGA_220])
        assert e.value.code == 3
        out = capsys.readouterr().out
        assert "Buronga Switching Station" in out, \
            "the record that would be deleted must be named"
        assert "AU_v43_a8df26153d28" in out

    def test_it_aborts_rather_than_skipping_the_group(self):
        """A country with a colliding id must not be partially deduplicated.
        Every join downstream keys on substation_id."""
        with pytest.raises(SystemExit):
            _assert_ids_are_not_collisions("australia", [
                BURONGA_330, BURONGA_220,
                WODONGA_A, WODONGA_B,
                sub("C", "Clean", 110.0, 40.0, 5.0),
            ])

    def test_three_way_groups_are_checked_against_the_first(self):
        third = sub("AU_v43_4c6b0408d5f7", "Somewhere Else", 66.0, -10.0, 20.0)
        with pytest.raises(SystemExit):
            _assert_ids_are_not_collisions("nowhere",
                                           [WODONGA_A, WODONGA_B, third])
