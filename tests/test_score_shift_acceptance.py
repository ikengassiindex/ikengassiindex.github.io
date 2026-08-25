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
from datetime import datetime
from pathlib import Path

import pytest

from ._ssi_test_support import load_ssi_data

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

#: Minimum share of the smaller fleet that must match on substation_id for the
#: comparison to mean anything.
#:
#: Until 19 August 2026 this test skipped when NO ids matched. That inverted
#: the gate: japan, portugal, spain and sweden all passed precisely because
#: their identity keys had been fully re-issued and there was nothing left to
#: compare. Sweden went 3,872 -> 1,192 substations, a 69% fleet loss, and the
#: acceptance gate reported green. A gate that succeeds on the absence of
#: evidence is worse than no gate, because it is read as assurance.
#:
#: A genuinely absent baseline still skips (the file isn't there). A baseline
#: that exists but cannot be matched now FAILS, because that is a real and
#: actionable condition: either the ids were re-issued, or the fleet was
#: replaced. Both need a human.
#: Cross-reference: modification-log M-028.
_MIN_ID_OVERLAP_FRACTION = 0.50

#: How far the baseline snapshot may lag the live file before the comparison
#: stops being an acceptance test.
#:
#: This gate is meant to compare the state immediately BEFORE a refresh with
#: the state immediately AFTER it. The snapshots on disk are dated 4 June 2026
#: and the live files 18 August — eleven weeks and several methodology releases
#: apart. Comparing across that gap does not measure a refresh; it measures
#: cumulative drift, and it fails at 63-100% on 29 countries no matter how
#: sound the latest refresh was.
#:
#: A stale baseline SKIPS: the gate genuinely cannot assess anything, and a
#: skip says so without claiming success. A baseline that exists and is fresh
#: but cannot be matched by id still FAILS — see _MIN_ID_OVERLAP_FRACTION —
#: because that is an event, not an absence.
#: Cross-reference: modification-log M-028.
_MAX_BASELINE_LAG_DAYS = 21


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
    # The POST side must be shard-resolved: for the six Convention #79
    # countries a plain json.load yields no substations, which this gate would
    # otherwise read as "the entire fleet vanished" and report as an identity
    # break. The PRE side is a pre-sharding snapshot and is always inline.
    return (
        json.loads(pre_fp.read_text(encoding="utf-8")),
        load_ssi_data(country, REPO_ROOT),
    )


def _substations_by_id(data):
    """Return {substation_id: substation_dict} for stable matching."""
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    return {s.get("substation_id") or s.get("internal_id") or s.get("id"): s
            for s in subs if s}


def _generated_date(doc, fp):
    """Best-effort vintage of a snapshot: meta.generated, else file mtime."""
    raw = (doc.get("meta") or {}).get("generated") or (doc.get("meta") or {}).get("timestamp")
    if isinstance(raw, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(raw[:len(fmt) + 2].rstrip("Z"), fmt).date()
            except ValueError:
                continue
    return datetime.fromtimestamp(fp.stat().st_mtime).date()


def _skip_if_baseline_stale(country, pre, post):
    """Skip when the snapshot is too old to constitute a refresh baseline."""
    pre_fp = REPO_ROOT / country / "ssi-data.json.pre-pr7-backup"
    post_fp = REPO_ROOT / country / "ssi-data.json"
    pre_date = _generated_date(pre, pre_fp)
    post_date = _generated_date(post, post_fp)
    lag = (post_date - pre_date).days
    if lag > _MAX_BASELINE_LAG_DAYS:
        pytest.skip(
            f"{country}: baseline is {lag} days stale "
            f"({pre_date} vs {post_date}), beyond the "
            f"{_MAX_BASELINE_LAG_DAYS}-day limit. This gate compares a refresh "
            f"against the state that preceded it; across {lag} days it is "
            f"measuring cumulative methodology drift instead. Re-baseline "
            f"after the cohort rescore."
        )


def _assert_baseline_comparable(country, pre_by_id, post_by_id, common):
    """Fail — do not skip — when the two snapshots cannot be compared.

    See _MIN_ID_OVERLAP_FRACTION for why this is an assertion rather than a
    skip. The message reports the fleet sizes as well as the overlap, because
    a large fleet-size delta alongside zero overlap is the signature of a
    wholesale replacement rather than an incremental refresh.
    """
    n_pre, n_post = len(pre_by_id), len(post_by_id)
    smaller = min(n_pre, n_post)
    if smaller == 0:
        pytest.skip(f"{country}: one of the snapshots has no substations")
    overlap = len(common) / smaller
    assert overlap >= _MIN_ID_OVERLAP_FRACTION, (
        f"{country}: BASELINE NOT COMPARABLE — only {len(common)} "
        f"substation_ids are common to the pre ({n_pre}) and post ({n_post}) "
        f"snapshots, i.e. {overlap * 100:.1f}% of the smaller fleet, below "
        f"the {_MIN_ID_OVERLAP_FRACTION * 100:.0f}% floor. The score-shift "
        f"gate cannot say anything about this country. Either the identity "
        f"key was re-issued (Convention #56 break) or the fleet was replaced "
        f"— both need investigating before this gate means anything. "
        f"Fleet delta: {n_post - n_pre:+d} ({(n_post - n_pre) / n_pre * 100:+.1f}%)."
    )


# ═══════════════════════════════════════════════════════════
#  Test 1 — Score-shift bound (universal across 39 countries)
# ═══════════════════════════════════════════════════════════

class TestScoreShiftBound:
    """|ΔR_median| > 10% on ≤5% of substations across the fleet."""

    def test_large_shifts_below_5_percent_fraction(self, country, pre_post_data):
        pre, post = pre_post_data
        _skip_if_baseline_stale(country, pre, post)
        pre_by_id = _substations_by_id(pre)
        post_by_id = _substations_by_id(post)
        # Match on common ids only
        common = set(pre_by_id) & set(post_by_id)
        _assert_baseline_comparable(country, pre_by_id, post_by_id, common)
        large_shifts = 0
        for sid in common:
            pre_r = pre_by_id[sid].get("R_median")
            post_r = post_by_id[sid].get("R_median")
            if not (isinstance(pre_r, (int, float)) and isinstance(post_r, (int, float))):
                continue
            if pre_r == 0:
                # treat division-by-zero edge as a large shift if post is nonzero
                if post_r != 0:
                    large_shifts += 1
                continue
            rel_shift = abs(post_r - pre_r) / abs(pre_r)
            if rel_shift > _LARGE_SHIFT_PCT:
                large_shifts += 1
        large_pct = large_shifts / len(common)
        assert large_pct <= _LARGE_SHIFT_MAX_FRACTION, (
            f"{country}: {large_shifts} substations "
            f"({large_pct * 100:.2f}%) have |Δ R_median| > "
            f"{_LARGE_SHIFT_PCT * 100:.0f}% — above the {_LARGE_SHIFT_MAX_FRACTION * 100:.0f}% "
            f"acceptance bound"
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
        post = load_ssi_data(cohort_country, REPO_ROOT)

        pre_by_id = _substations_by_id(pre)
        post_by_id = _substations_by_id(post)
        common = set(pre_by_id) & set(post_by_id)
        _assert_baseline_comparable(cohort_country, pre_by_id, post_by_id, common)
        _skip_if_baseline_stale(cohort_country, pre, post)

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
    """All 39 countries' substations carry the PR-3 provenance fields after backfill."""

    def test_provenance_present_after_backfill(self, country):
        fp = REPO_ROOT / country / "ssi-data.json"
        if not fp.exists():
            pytest.skip(f"{country}/ssi-data.json absent")
        # Shard-resolved: a plain json.load returns no substations for the six
        # Convention #79 countries, and this test would then skip on
        # "has no substations" — checking provenance on nothing.
        data = load_ssi_data(country, REPO_ROOT)
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
