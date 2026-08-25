"""Sentinel — one v4.0.2 measurement may support exactly one substation.

WHY THIS TEST EXISTS
────────────────────
M-054 recovered genuine component sets for substations whose IDs were re-issued
during Wave 4, by matching position against `<country>/_v4.0.2.backup` donors
within 100 m. The matcher held its consumed-donor set in a local variable, so it
was correct within one invocation and blind across invocations. A second pass
re-matched donors already spent by the first, and copied one donor's components
into a second substation.

4,499 records across france, us, sweden and uk ended up carrying components
measured somewhere else, for a different asset. Nothing about them looked wrong:
plausible values, a provenance marker, a match distance under 100 m. Two records
simply cited the same evidence.

This is M-046 wearing different clothes. There the missing input was replaced by
a number; here it was replaced by *someone else's* number. In both cases a
record published a value with no observation behind it, and every downstream
check passed because there was something to look at.

Retracted under M-056: nearest recipient keeps the donor, the rest return to
component-less Unclassified.

WHAT THIS PINS
──────────────
Across every country, each donor `substation_id` cited in a
`_components_recovered` marker appears at most once. `MAX_ALLOWED = 0`.

Do not xfail this test. If a future recovery pass needs to run, give it a
cross-invocation donor guard — read the markers already on disk and exclude
those donors before matching — rather than lowering this bar.

Cross-reference: Convention #56, CLAUDE.md Discipline #50, METHODOLOGY_DISCIPLINES
§5bis Criterion 2, modification-log M-054 / M-056.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

from ._ssi_test_support import load_ssi_data

REPO_ROOT = Path(__file__).resolve().parent.parent

MAX_ALLOWED = 0

DONOR_PATTERN = re.compile(r"\(donor ([^)]*)\)")

COUNTRIES = sorted(p.parent.name for p in REPO_ROOT.glob("*/ssi-data.json"))


@pytest.mark.parametrize("country", COUNTRIES or [pytest.param(None, marks=pytest.mark.skip(reason="no country data in this checkout"))])
def test_no_donor_is_attributed_to_two_substations(country):
    doc = load_ssi_data(country, REPO_ROOT)
    recipients = collections.defaultdict(list)
    for sub in doc.get("substations") or []:
        marker = sub.get("_components_recovered")
        if not marker:
            continue
        match = DONOR_PATTERN.search(marker)
        if match:
            recipients[match.group(1)].append(sub.get("substation_id"))

    reused = {donor: ids for donor, ids in recipients.items() if len(ids) > 1}
    excess = sum(len(ids) - 1 for ids in reused.values())

    sample = list(reused.items())[:5]
    assert excess <= MAX_ALLOWED, (
        f"{country}: {len(reused):,} v4.0.2 donors are each cited by more than "
        f"one substation, giving {excess:,} records whose components describe a "
        f"different asset.\n"
        f"  examples: {sample}\n\n"
        "A component set is an observation of one substation. Copying it to a "
        "second is fabrication, not recovery — the same defect as M-046 with a "
        "more convincing surface. Retract the further recipients (keep the "
        "nearest match) and give the recovery pass a cross-invocation donor "
        "guard before re-running it."
    )


def test_retracted_records_carry_no_components():
    """A retraction that leaves the components behind has retracted nothing."""
    leaked = []
    for country in COUNTRIES:
        doc = load_ssi_data(country, REPO_ROOT)
        for sub in doc.get("substations") or []:
            if sub.get("_components_recovery_retracted") and sub.get("components"):
                leaked.append((country, sub.get("substation_id")))
    assert not leaked, (
        f"{len(leaked):,} records are marked as having had their recovered "
        f"components retracted but still carry a populated `components` dict: "
        f"{leaked[:5]}. The marker and the data disagree, and the data is what "
        "gets scored."
    )
