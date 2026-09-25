"""
SSI Pipeline — Per-Country Score-Shift Acceptance (Phase 1 PR-7)

Compares pre-refresh and post-refresh ssi-data.json files for each country,
verifying the score-shift profile meets the PR-7 acceptance bound:

  • |Δ R_median| > 10% on ≤ 5% of substations in every country
    (the rest stay within natural MC noise)

For the 5 per-country adaptation cohorts (Korea, Colombia, Israel, Costa Rica,
Iceland) the test additionally verifies that the now-applied modifiers
produced the expected DIRECTIONAL shift (positive uplift where R6_typhoon /
R6_volcanic / R6_drought / R6_armed_conflict are > 1.0).

Test design — distribution-comparison harness:
  • Pre-refresh snapshot lives at <country>/ssi-data.json.pre-pr7-backup
    (created by scripts/backfill_provenance.py before write-back)
  • Post-refresh state at <country>/ssi-data.json
  • If the backup file is absent, the test is skipped (operator hasn't run
    backfill yet OR an --all refresh already happened)
  • Substations matched by 'substation_id' (Convention #56 stable key)

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-7 §"Acceptance gates"
                 PHASE_1_IMPLEMENTATION_PLAN.md §"Test criteria"
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L3-4 cohort closure
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_SOT = json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())
COUNTRIES = sorted(_SOT["slugs"])

# Per-country adaptation cohort — countries that carry cohort-specific
# modifiers (Korea R6_typhoon + R6_chaebol; Colombia R6_volcanic + R6_drought
# + R6_armed_conflict; Israel R6_drought; Costa Rica R6_volcanic + R6_seismic;
# Iceland R6_volcanic). Pre-PR-3 these were stored but never multiplied;
# PR-3 wired them through compute_r_median. PR-7 expects positive directional
# shift on these countries (R_median moves upward after refresh).
_ADAPTATION_COHORT = {
    "korea":      ["R6_typhoon", "R6_chaebol"],
    "colombia":   ["R6_volcanic", "R6_drought", "R6_armed_conflict"],
    "israel":     ["R6_drought"],
    "costa-rica": ["R6_volcanic", "R6_seismic"],
    "iceland":    ["R6_volcanic"],
}

# Acceptance thresholds (PR-7 plan)
_LARGE_SHIFT_PCT = 0.10              # |Δ R_median| > 10% counts as "large"
_LARGE_SHIFT_MAX_FRACTION = 0.05      # ≤ 5% of substations may have large shifts


# ═══════════════════════════════════════════════════════════
#  Per-country fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="module", params=COUNTRIES)
def country(request):
    return request.param


@pytest.fixture(scope="module")
def pre_post_data(country):
    """Load pre + post refresh data for the country. Skip if backup absent."""
    post_fp = REPO_ROOT / country / "ssi-data.json"
    pre_fp = REPO_ROOT / country / "ssi-data.json.pre-pr7-backup"
    if not post_fp.exists():
        pytest.skip(f"{country}/ssi-data.json absent in this checkout")
    if not pre_fp.exists():
        pytest.skip(
            f"{country}/ssi-data.json.pre-pr7-backup absent — run "
            f"scripts/backfill_provenance.py first to create the snapshot"
        )
    return (
        json.loads(pre_fp.read_text(encoding="utf-8")),
        json.loads(post_fp.read_text(encoding="utf-8")),
    )


def _substations_by_id(data):
    """Return {substation_id: substation_dict} for stable matching."""
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    return {s.get("substation_id") or s.get("internal_id") or s.get("id"): s
            for s in subs if s}


# ═══════════════════════════════════════════════════════════
#  Test 1 — Score-shift bound (universal across 39 countries)
# ═══════════════════════════════════════════════════════════

class TestScoreShiftBound:
    """RETIRED 21 September 2026 — deliberately, with the reasoning here.

    This gate compared every substation's R_median against
    `ssi-data.json.pre-pr7-backup` and failed if more than 5 % had moved by
    more than 10 %. It was written to accept ONE change, PR-7, and then left
    comparing against that same frozen snapshot.

    Measured before retiring it:

      * the snapshots are dated **2026-06-04**; the current data is
        **2026-09-10**. Three months and every intentional change in between —
        the R_base regression fix, I1 to I6 derivation, Task #462 band
        normalisation, the five-band reclassify, the R7 v2 apply and its
        revert, v4.24.
      * austria: median shift **89.7 %**, and **99.3 %** of substations moved
        more than 10 %. R_median went from [0.1865, 0.5429] to
        [0.0485, 1.1033] — a different distribution, because it is a
        different index.
      * the comparison population is not the fleet. Common substation ids
        between snapshot and current: **iceland 99.9 %, denmark 50.5 %,
        austria 5.0 %, poland 0 %.** The dedupe of 29 August changed ids, so
        this gate was measuring between none and all of each country.

    It was not detecting a regression. It was reporting that the index had
    been improved, in 29 countries, once per run.

    NOT RE-BASELINED. Pointing it at today's data would make it green and
    guard nothing until the next change, and re-baselining a failing
    expectation to whatever the code now emits is the precise habit this
    estate has spent the day removing. It is retired instead, and what it
    should be replaced by is stated rather than implied.

    WHAT A LIVE VERSION WOULD NEED: a per-edition data snapshot to compare
    against. The `archive/` tree keeps monthly ESG reports, not `ssi-data`,
    so there is no rolling baseline to point at today. Creating one costs
    ~255 MB per edition in git and is a decision for the operator, not a
    fix to be smuggled into a test file.

    `TestScoreEnvelope` below replaces it with an invariant that needs no
    baseline at all.
    """


class TestScoreEnvelope:
    """R_median must lie inside the band table's declared range.

    Baseline-free, so it cannot go stale the way the shift gate did. The
    five-band table runs Low/Medium/High/Critical/Extreme with Extreme
    declared as [1.00, 1.30], so 1.30 is the ceiling the published
    classification can express. A score above it would be unclassifiable by
    the estate's own table.

    Measured 21 September 2026 across all 39 jurisdictions: 622,039 scored
    records in [0.0000, 1.2703], with 65 carrying None under Convention #56.
    The highest maxima are colombia 1.2703, ireland 1.2678 and turkey 1.2578,
    so the headroom is real but thin — about 2 % — and that is worth knowing
    before the additive tail moves.
    """

    R_MEDIAN_FLOOR = 0.0
    R_MEDIAN_CEILING = 1.30          # top of the Extreme band

    def test_r_median_inside_the_band_table(self, country):
        post_fp = REPO_ROOT / country / "ssi-data.json"
        if not post_fp.exists():
            pytest.skip(f"{country}/ssi-data.json absent in this checkout")
        try:
            from pipeline.utils.ssi_data_sharding import read_ssi_data
            data = read_ssi_data(post_fp)
        except ImportError:
            data = json.loads(post_fp.read_text(encoding="utf-8"))
        out = []
        n_scored = 0
        for sub in data.get("substations", []):
            v = sub.get("R_median")
            if v is None:
                continue                      # Convention #56 pre-L3 state
            if not isinstance(v, (int, float)):
                continue
            n_scored += 1
            if not (self.R_MEDIAN_FLOOR <= v <= self.R_MEDIAN_CEILING):
                out.append((sub.get("substation_id"), v))
        assert not out, (
            f"{country}: {len(out)} of {n_scored} scored substations carry an "
            f"R_median outside [{self.R_MEDIAN_FLOOR}, {self.R_MEDIAN_CEILING}], "
            f"which the five-band table cannot classify. First five: {out[:5]}"
        )


# ═══════════════════════════════════════════════════════════
#  Test 2 — Adaptation cohort directional shift (5 countries)
# ═══════════════════════════════════════════════════════════

class TestAdaptationCohortShift:
    """For the 5 adaptation-cohort countries, R_median must shift in the
    direction implied by their cohort-specific modifiers post-PR-3."""

    @pytest.mark.parametrize("cohort_country", list(_ADAPTATION_COHORT.keys()))
    def test_cohort_country_r_median_shifts(self, cohort_country):
        """Korea/Colombia/Israel/Costa-Rica/Iceland: R_median mean should
        shift positively (upward) after PR-3 wires their cohort modifiers."""
        pre_fp = REPO_ROOT / cohort_country / "ssi-data.json.pre-pr7-backup"
        post_fp = REPO_ROOT / cohort_country / "ssi-data.json"
        if not pre_fp.exists():
            pytest.skip(
                f"{cohort_country}: pre-PR-7 backup not present — run "
                f"scripts/backfill_provenance.py first"
            )
        if not post_fp.exists():
            pytest.skip(f"{cohort_country}: ssi-data.json absent")
        pre = json.loads(pre_fp.read_text(encoding="utf-8"))
        post = json.loads(post_fp.read_text(encoding="utf-8"))

        pre_by_id = _substations_by_id(pre)
        post_by_id = _substations_by_id(post)
        common = set(pre_by_id) & set(post_by_id)
        if not common:
            pytest.skip(f"{cohort_country}: no common ids")

        # Compute mean R_median pre + post; under backfill-only mode the
        # provenance fields populate but R_median is preserved, so the mean
        # delta should be ~0. Under --all refresh mode the cohort modifiers
        # apply and shift mean upward.
        pre_rs = [pre_by_id[sid].get("R_median") for sid in common]
        post_rs = [post_by_id[sid].get("R_median") for sid in common]
        pre_rs = [r for r in pre_rs if isinstance(r, (int, float))]
        post_rs = [r for r in post_rs if isinstance(r, (int, float))]
        if not (pre_rs and post_rs):
            pytest.skip(f"{cohort_country}: no R_median values to compare")
        pre_mean = sum(pre_rs) / len(pre_rs)
        post_mean = sum(post_rs) / len(post_rs)

        # Backfill-only mode (provenance fields added, R_median preserved)
        # → mean delta ≈ 0 (passes naturally). Full --all mode → positive
        # shift expected. Either way, we just need to verify the direction
        # isn't negative beyond noise (<-2%).
        relative_delta = (post_mean - pre_mean) / max(pre_mean, 0.001)
        assert relative_delta >= -0.02, (
            f"{cohort_country}: R_median mean shifted negatively by "
            f"{relative_delta * 100:+.2f}% post-PR-7. The cohort modifiers "
            f"({_ADAPTATION_COHORT[cohort_country]}) should shift R_median "
            f"upward, not downward, after PR-3 wires them through "
            f"compute_modifier_terms()."
        )


# ═══════════════════════════════════════════════════════════
#  Test 3 — Provenance fields populated (backfill outcome)
# ═══════════════════════════════════════════════════════════

class TestProvenancePopulated:
    """All 39 countries' substations carry the PR-3 provenance fields after backfill.

    It did not cover all 39. Until 21 September 2026 this read
    `data["substations"]` directly, which on a Convention #79 sharded country
    is absent — the records live in `substations_shards`. So it reported
    "<country> has no substations" and SKIPPED, and the six it skipped were
    poland, uk, us, france, germany and italy: the largest fleets in the
    estate, some 470,000 records.

    That is Task #520's registered defect class, and it is the same shape as
    everything else found today — a check that does not reach the data it
    claims to check, reporting a skip that reads as "nothing to see".
    It now uses the sharding-aware reader.
    """

    def test_provenance_present_after_backfill(self, country):
        fp = REPO_ROOT / country / "ssi-data.json"
        if not fp.exists():
            pytest.skip(f"{country}/ssi-data.json absent")
        try:
            from pipeline.utils.ssi_data_sharding import read_ssi_data
            data = read_ssi_data(fp)
        except ImportError:
            data = json.loads(fp.read_text(encoding="utf-8"))
        subs = data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        if not subs:
            pytest.skip(f"{country} has no substations")
        # Sample first 10 — backfill is bulk, so failures show up in sample
        sample = subs[:10]
        for field in ("mult_product", "add_sum", "modifier_impacts"):
            missing = sum(1 for s in sample if field not in s)
            assert missing == 0, (
                f"{country}: field {field!r} missing from {missing}/10 sampled "
                f"substations. Run scripts/backfill_provenance.py to populate."
            )
