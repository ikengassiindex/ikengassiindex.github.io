"""Each component-provenance check must fire on what it names, and nothing else.

456,200 substations carry six component scores reproduced bit-for-bit by
round(vary(0.35, name + '_' + K, 0.30), 4) — a hash of the substation's own
name. These pin the detector so a later edit cannot quietly report a measured
cohort.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_components_are_measured import audit, hashed_keys, CHECKS, KEYS
from enrich_esg_gaps import vary

NAME = "Substation 1000000000"
HASHED = {k: round(vary(0.35, f"{NAME}_{k}", 0.30), 4) for k in KEYS}
REAL = {"C": 0.71, "V": 0.62, "I": 0.55, "E": 0.48, "S": 0.66, "T": 0.39}


def rec(**over):
    s = {"substation_id": "X1", "name": NAME, "components": dict(REAL)}
    s.update(over)
    return s


def only(counts, *expected):
    fired = {k for k in CHECKS if counts[k]}
    assert fired == set(expected), f"fired {sorted(fired)}, expected {sorted(expected)}"


def test_measured_components_trip_nothing():
    c, _ = audit([rec()])
    only(c)


def test_hashed_fires_when_all_six_reproduce():
    c, ex = audit([rec(components=dict(HASHED))])
    only(c, "HASHED")
    assert ex["substation_id"] == "X1"


def test_partial_fires_on_a_mixture():
    """A record half measured and half manufactured is its own category."""
    mixed = dict(REAL)
    mixed["C"] = HASHED["C"]
    mixed["V"] = HASHED["V"]
    c, _ = audit([rec(components=mixed)])
    only(c, "PARTIAL")


def test_the_hash_is_keyed_per_component_not_per_record():
    """vary is called with name + '_' + K, so a value valid for C is not for V."""
    wrong = dict(REAL)
    wrong["V"] = HASHED["C"]
    assert hashed_keys(NAME, wrong) == []


def test_the_hash_is_keyed_on_the_name():
    """The same components under a different name are not the same hash."""
    c, _ = audit([rec(name="Something Else", components=dict(HASHED))])
    only(c)


def test_no_comps_fires_and_hashed_does_not_guess():
    c, _ = audit([rec(components={})])
    only(c, "NO_COMPS")


def test_unchecked_when_there_is_no_name_to_hash():
    """Convention #56: the derivation cannot run, so it is reported, not passed."""
    c, _ = audit([rec(name=None)])
    only(c, "UNCHECKED")


def test_the_live_register_reproduces_the_finding():
    """france's first record: all six components are the hash of its name."""
    import json
    m = json.loads((ROOT / "france" / "ssi-data.json").read_text())
    shard = ROOT / "france" / pathlib.Path(m["substations_shards"][0]["path"]).name
    raw = json.loads(shard.read_text())
    subs = raw if isinstance(raw, list) else raw["substations"]
    s = subs[0]
    assert len(hashed_keys(s["name"], s["components"])) == 6, (
        "france's first record should reproduce all six — that is the finding")
