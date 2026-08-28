"""The published band distribution must count the labels, not re-derive them.

28 August 2026. A us dedupe published Low 0.0% over a fleet whose substations
were 22.6% Low, and four CI checks passed while it did, because every one of
them compared the page to the manifest or the manifest to itself. germany,
japan and sweden were in the same state; japan had been for months.

The cause was one import. ssi_dedupe_substations.py::write_country called
engine.compute_fleet_summary, which recounts bands from R_median with the
absolute cutoffs Task #461 replaced, discarding each substation's normalised
`classification`.
"""
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.pipeline.scoring.engine import compute_fleet_summary  # noqa: E402
from scripts.refresh_fleet_summary import (  # noqa: E402
    _recompute_fleet_summary_task_461_aware as recompute)


def _fleet():
    """Two substations whose normalised labels disagree with their absolute
    bands. Both sit at R_median ~0.7, which classify_band calls High."""
    return [
        {"R_median": 0.70, "R_P5": 0.60, "R_P95": 0.80, "classification": "Low"},
        {"R_median": 0.72, "R_P5": 0.72, "R_P95": 0.72, "classification": "Extreme"},
    ]


class TestTheTwoRoutinesDiffer:
    """If these ever agree the rest of this file proves nothing."""

    def test_the_engine_still_re_derives_from_R_median(self):
        # Not a defect in itself — engine.compute_fleet_summary is correct for
        # a country that was never normalised. It is wrong only as the thing a
        # rewrite of a normalised country calls.
        assert compute_fleet_summary(_fleet())["bands"]["High"] == 2

    def test_the_task_461_routine_counts_the_labels(self):
        b = recompute(_fleet())["bands"]
        assert b["Low"] == 1 and b["Extreme"] == 1 and b["High"] == 0


class TestTheWritePathUsesTheRightOne:
    """A source-level assertion, deliberately. The alternative is a fixture
    country with shards on disk, and the defect is precisely that the function
    LOOKS right at every call site — it is the import that was wrong."""

    SRC = REPO / "scripts" / "ssi_dedupe_substations.py"

    def test_it_imports_the_task_461_aware_routine(self):
        s = self.SRC.read_text()
        assert "_recompute_fleet_summary_task_461_aware" in s

    def test_it_does_not_import_the_engine_fleet_summary(self):
        s = self.SRC.read_text()
        assert "from pipeline.scoring.engine import compute_fleet_summary" not in s
        assert "engine import compute_fleet_summary," not in s

    def test_preserved_provenance_cannot_overwrite_a_rebuild(self):
        # germany's manifest stamped "task_461_per_country_normalised" over
        # bands that were not normalised, because `fs.update(preserved)` ran
        # after the rebuild. A false provenance claim is worse than none.
        s = self.SRC.read_text()
        assert "fs.update(preserved)" not in s
        assert "{**preserved, **fs}" in s


class TestTheCheckerCatchesIt:
    CHECK = REPO / "scripts" / "check_bands_match_classification.py"

    def test_the_checker_exists(self):
        assert self.CHECK.exists(), "the gate that would have caught this"

    def test_a_planted_mismatch_is_reported(self, tmp_path):
        """Build a two-country repo skeleton, break one, and require a
        non-zero exit under --strict."""
        (tmp_path / "intelligence").mkdir()
        (tmp_path / "intelligence" / "countries.json").write_text(
            json.dumps({"slugs": ["good", "bad"]}))
        subs = [{"substation_id": str(i), "R_median": 0.7,
                 "classification": "Low" if i < 8 else "High"} for i in range(10)]
        honest = {"Low": 8, "Medium": 0, "High": 2,
                  "Critical": 0, "Extreme": 0, "Unclassified": 0}
        liar = {"Low": 0, "Medium": 0, "High": 10,
                "Critical": 0, "Extreme": 0, "Unclassified": 0}
        for slug, bands in (("good", honest), ("bad", liar)):
            d = tmp_path / slug
            d.mkdir()
            (d / "ssi-data.json").write_text(json.dumps(
                {"fleet_summary": {"bands": bands}, "substations": subs}))

        r = subprocess.run([sys.executable, str(self.CHECK), "--all", "--strict"],
                           cwd=tmp_path, capture_output=True, text=True)
        assert r.returncode == 1, f"the mismatch went unreported:\n{r.stdout}"
        assert "bad" in r.stdout
        assert "good:" not in r.stdout, "a country that agrees must not be flagged"

    def test_an_unnormalised_country_is_not_a_failure(self, tmp_path):
        """A country whose labels are the absolute bands still matches its own
        summary. The check asks for agreement, not for normalisation."""
        (tmp_path / "intelligence").mkdir()
        (tmp_path / "intelligence" / "countries.json").write_text(
            json.dumps({"slugs": ["plain"]}))
        subs = [{"substation_id": str(i), "R_median": 0.7,
                 "classification": "High"} for i in range(10)]
        d = tmp_path / "plain"
        d.mkdir()
        (d / "ssi-data.json").write_text(json.dumps(
            {"fleet_summary": {"bands": {"Low": 0, "Medium": 0, "High": 10,
                                         "Critical": 0, "Extreme": 0,
                                         "Unclassified": 0}},
             "substations": subs}))
        r = subprocess.run([sys.executable, str(self.CHECK), "--all", "--strict"],
                           cwd=tmp_path, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout

    def test_it_reads_shards_rather_than_the_flat_key(self, tmp_path):
        """Task #520: a sharded manifest has no `substations` key. A reader
        that ignores the shard list sees an empty fleet and reports agreement
        with anything."""
        (tmp_path / "intelligence").mkdir()
        (tmp_path / "intelligence" / "countries.json").write_text(
            json.dumps({"slugs": ["shardy"]}))
        d = tmp_path / "shardy"
        d.mkdir()
        subs = [{"substation_id": str(i), "R_median": 0.7,
                 "classification": "Low"} for i in range(10)]
        (d / "ssi-data-substations-01.json").write_text(json.dumps(subs))
        (d / "ssi-data.json").write_text(json.dumps({
            "sharded": True,
            "substations_shards": [{"path": "ssi-data-substations-01.json",
                                    "count": 10}],
            "fleet_summary": {"bands": {"Low": 0, "Medium": 0, "High": 10,
                                        "Critical": 0, "Extreme": 0,
                                        "Unclassified": 0}}}))
        r = subprocess.run([sys.executable, str(self.CHECK), "--all", "--strict"],
                           cwd=tmp_path, capture_output=True, text=True)
        assert r.returncode == 1, ("the shard was not read — this is the "
                                   f"Task #520 defect class:\n{r.stdout}")
