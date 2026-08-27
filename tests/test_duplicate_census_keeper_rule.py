"""Pin the rule that decides which duplicate substation survives.

scripts/ssi_duplicate_census.py classifies co-located substations into five
classes and names one member of each group as the keeper. scripts/
ssi_dedupe_substations.py removes the rest. japan is already reshaped by that
rule — 7,073 to 6,168 — spain is next, and 99,447 duplicates remain across the
cohort with germany and us the largest.

Until this file existed, nothing pinned the rule. An edit to keeper() or to the
D1/D2 boundary would quietly change which substation survives, and the change
would be invisible: the counts would look the same, a different asset would be
gone, and japan's already-applied removals would no longer be reproducible from
the code that made them.

What is pinned:

  keeper()          the four tiebreakers, in order, and that the result does
                    not depend on the order the group arrives in
  generated_name()  what counts as a placeholder name
  classify()        class precedence A > B > C > D, and the D1/D2 boundary
  FACILITY_KEYS     the fields that decide "identical facility"

The D1/D2 boundary is the one that matters most. D2 groups are genuine
multi-voltage co-locations — distinct assets sharing a site — and are
preserved. D1 groups differ only because one record has no voltage, which is
an unknown rather than a distinguishing attribute, and are collapsed. Move
that boundary and real fleet is either destroyed or duplicates survive.
"""
from __future__ import annotations

import itertools

import pytest

from scripts.ssi_duplicate_census import (
    FACILITY_KEYS,
    classify,
    generated_name,
    keeper,
)


def sub(sid, **kw):
    """A substation record. lat/lon default to one shared coordinate so that
    every record built here lands in the same co-location group."""
    s = {"substation_id": sid, "lat": 45.0, "lon": 9.0}
    s.update(kw)
    return s


# ───────────────────────── generated_name ─────────────────────────

class TestGeneratedName:
    """A placeholder name must not beat a real one, so what counts as a
    placeholder is load-bearing."""

    @pytest.mark.parametrize("name", [None, "", "   ", 42, [], {}])
    def test_absent_or_non_string_is_generated(self, name):
        assert generated_name(sub("X1", name=name)) is True

    def test_substation_id_placeholder_is_generated(self):
        assert generated_name(sub("X1", name="Substation X1")) is True

    def test_placeholder_for_a_different_id_is_a_real_name(self):
        # "Substation X2" on record X1 is not this record's placeholder.
        assert generated_name(sub("X1", name="Substation X2")) is False

    def test_real_name_is_not_generated(self):
        assert generated_name(sub("X1", name="Cordoba 400kV")) is False

    def test_surrounding_whitespace_does_not_hide_a_placeholder(self):
        assert generated_name(sub("X1", name="  Substation X1  ")) is True


# ───────────────────────────── keeper ─────────────────────────────

class TestKeeperTiebreakers:
    """Four tiebreakers, applied in this order:
         1. a real name beats a generated one
         2. more populated fields beats fewer
         3. having an osm_feature_id beats not having one
         4. lowest substation_id as a string — the deterministic backstop
    """

    def test_1_real_name_beats_generated_even_with_fewer_fields(self):
        named = sub("B", name="Cordoba 400kV")
        rich = sub("A", name="Substation A", operator="REE", region="Andalucia",
                   province="Cordoba", voltage_kv=400, osm_feature_id="w1")
        assert keeper([rich, named])["substation_id"] == "B"

    def test_2_more_fields_wins_when_both_names_are_real(self):
        thin = sub("A", name="Cordoba 400kV")
        rich = sub("B", name="Cordoba 400kV", operator="REE", voltage_kv=400)
        assert keeper([thin, rich])["substation_id"] == "B"

    def test_2_zero_and_false_count_as_populated_not_absent(self):
        # A 0 kV reading is a value someone recorded. Only None, "", {} and []
        # are absent. Getting this wrong would silently reorder keepers.
        #
        # The ids are deliberately the wrong way round: "Z" sorts last, so it
        # can only win on field count. With "A" it would win on the id
        # backstop instead and the test would pass whatever this rule did.
        zeros = sub("Z", name="Site", voltage_kv=0, operator=False)
        empties = sub("A", name="Site", voltage_kv=None, operator="")
        assert keeper([empties, zeros])["substation_id"] == "Z"

    def test_3_osm_feature_id_breaks_a_tie_on_name_and_field_count(self):
        with_osm = sub("B", name="Site", osm_feature_id="w1")
        without = sub("A", name="Site", operator="REE")
        # both: real name, two populated fields beyond the base three
        assert keeper([without, with_osm])["substation_id"] == "B"

    def test_4_lowest_string_id_is_the_final_backstop(self):
        a = sub("A", name="Site", osm_feature_id="w1")
        b = sub("B", name="Site", osm_feature_id="w2")
        assert keeper([b, a])["substation_id"] == "A"

    def test_4_ordering_is_string_ordering_not_numeric(self):
        # "10" sorts before "9" as a string. Pinned because changing it to a
        # numeric sort would silently pick a different keeper on every
        # numerically-keyed country.
        s9 = sub("9", name="Site", osm_feature_id="w")
        s10 = sub("10", name="Site", osm_feature_id="w")
        assert keeper([s9, s10])["substation_id"] == "10"


class TestKeeperDeterminism:
    """The keeper must not depend on the order records happen to sit in the
    file. Without this, a re-ingestion that reordered records would silently
    change which substation survives."""

    def test_every_permutation_yields_the_same_keeper(self):
        group = [
            sub("C", name="Cordoba 400kV", operator="REE", voltage_kv=400),
            sub("A", name="Substation A", osm_feature_id="w1"),
            sub("B", name="Cordoba 400kV"),
            sub("D", name=None, operator="REE"),
        ]
        keepers = {keeper(list(p))["substation_id"]
                   for p in itertools.permutations(group)}
        assert keepers == {"C"}

    def test_a_single_member_group_keeps_itself(self):
        assert keeper([sub("A", name="Site")])["substation_id"] == "A"


# ──────────────────────────── classify ────────────────────────────

@pytest.fixture
def census(monkeypatch):
    """classify() reads a country off disk. Feed it records instead."""
    def _run(records):
        monkeypatch.setattr("scripts.ssi_duplicate_census.load",
                            lambda slug: records)
        return classify("synthetic")
    return _run


class TestClassPrecedence:
    """A duplicate id is class A whatever else is true of the group; a
    duplicate OSM feature is B; an identical facility is C; the rest split
    D1/D2. The order matters — a group can satisfy several conditions, and
    only the first one it satisfies should count."""

    def test_A_duplicate_substation_id(self, census):
        r = census([sub("dup", name="One", voltage_kv=400),
                    sub("dup", name="Two", voltage_kv=132)])
        assert len(r["A"]) == 1 and not (r["B"] or r["C"] or r["D1"] or r["D2"])

    def test_A_wins_over_a_group_that_would_otherwise_be_D2(self, census):
        # Distinct real voltages would make this D2 if the ids were distinct.
        r = census([sub("dup", voltage_kv=400, name="a"),
                    sub("dup", voltage_kv=132, name="b")])
        assert len(r["A"]) == 1 and not r["D2"]

    def test_B_duplicate_osm_feature_id_with_distinct_ids(self, census):
        r = census([sub("A", osm_feature_id="w1", voltage_kv=400),
                    sub("B", osm_feature_id="w1", voltage_kv=132)])
        assert len(r["B"]) == 1 and not (r["A"] or r["C"] or r["D1"] or r["D2"])

    def test_C_identical_facility_keys(self, census):
        common = dict(voltage_kv=220, operator="REE",
                      region="Andalucia", province="Cordoba")
        r = census([sub("A", **common), sub("B", **common)])
        assert len(r["C"]) == 1 and not (r["A"] or r["B"] or r["D1"] or r["D2"])

    def test_C_requires_every_facility_key_to_match(self, census):
        r = census([sub("A", voltage_kv=220, operator="REE",
                        region="Andalucia", province="Cordoba"),
                    sub("B", voltage_kv=220, operator="Endesa",
                        region="Andalucia", province="Cordoba")])
        assert not r["C"]
        assert len(r["D1"]) == 1  # one real voltage across the group


class TestD1D2Boundary:
    """The boundary that decides whether real fleet survives.

    D2 — two or more genuine voltages at one coordinate — is a real
    multi-voltage site and is preserved by the deduplicator. D1 — where the
    group differs only because a record carries no voltage, or a 0.0 — is an
    unknown rather than a distinguishing attribute, and collapses.
    """

    def test_two_real_voltages_is_D2_and_is_preserved(self, census):
        r = census([sub("A", voltage_kv=400, operator="REE"),
                    sub("B", voltage_kv=132, operator="Endesa")])
        assert len(r["D2"]) == 1 and not r["D1"]

    @pytest.mark.parametrize("unknown", [None, 0, 0.0])
    def test_one_real_voltage_against_an_unknown_is_D1(self, census, unknown):
        r = census([sub("A", voltage_kv=132, operator="REE"),
                    sub("B", voltage_kv=unknown, operator="Endesa")])
        assert len(r["D1"]) == 1 and not r["D2"]

    def test_two_unknowns_is_D1(self, census):
        r = census([sub("A", voltage_kv=0, operator="REE"),
                    sub("B", voltage_kv=None, operator="Endesa")])
        assert len(r["D1"]) == 1 and not r["D2"]

    def test_negative_voltage_is_not_a_real_voltage(self, census):
        r = census([sub("A", voltage_kv=132, operator="REE"),
                    sub("B", voltage_kv=-1, operator="Endesa")])
        assert len(r["D1"]) == 1 and not r["D2"]

    def test_three_real_voltages_is_D2(self, census):
        r = census([sub("A", voltage_kv=400, operator="a"),
                    sub("B", voltage_kv=220, operator="b"),
                    sub("C", voltage_kv=132, operator="c")])
        assert len(r["D2"]) == 1


class TestGrouping:
    """Only exact co-location groups. A lone substation is never a duplicate,
    and a coordinate that differs past the sixth decimal is a different site."""

    def test_a_lone_substation_is_never_reported(self, census):
        r = census([sub("A", name="Solo", voltage_kv=400)])
        assert not any(r[k] for k in ("A", "B", "C", "D1", "D2"))
        assert r["substations"] == 1

    def test_records_without_usable_coordinates_are_skipped(self, census):
        r = census([{"substation_id": "A", "lat": None, "lon": 9.0},
                    {"substation_id": "B", "lat": None, "lon": 9.0}])
        assert not any(r[k] for k in ("A", "B", "C", "D1", "D2"))

    def test_coordinates_are_matched_to_six_decimals(self, census):
        a = sub("A", voltage_kv=400, operator="x")
        b = sub("B", voltage_kv=400, operator="x")
        b["lat"] = 45.0000004          # rounds to 45.0
        assert sum(len(census([a, b])[k]) for k in ("C", "D1", "D2")) == 1

        c = sub("C", voltage_kv=400, operator="x")
        c["lat"] = 45.00001            # does not round to 45.0
        assert not any(census([a, c])[k] for k in ("A", "B", "C", "D1", "D2"))

    def test_the_named_keeper_is_a_member_of_its_own_group(self, census):
        r = census([sub("A", voltage_kv=400, operator="x", name="Real"),
                    sub("B", voltage_kv=400, operator="x")])
        rec = (r["C"] + r["D1"] + r["D2"])[0]
        assert rec["keeper"] in rec["ids"]
        assert rec["redundant"] == rec["n"] - 1


# ─────────────────────────── constant lock ───────────────────────────

def test_facility_keys_are_locked():
    """"Identical facility" is defined by exactly these four fields. Adding one
    moves groups from C to D; removing one moves them from D to C. Either
    changes what gets deleted across 99,447 duplicate records."""
    assert FACILITY_KEYS == ("voltage_kv", "operator", "region", "province")
