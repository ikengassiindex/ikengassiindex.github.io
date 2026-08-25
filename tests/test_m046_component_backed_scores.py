"""
Sentinel — every published score must be backed by real components (M-046).

WHAT WENT WRONG
───────────────
`score_substation()` reads components off the record; it does not build them:

    components = updated.get("components", {})        # engine.py
    R_base     = compute_r_base(components)           # → 0.0 for {}

Every `merge_into_ssi_data.py` writes `"components": {}` at ingest, and
`compute_r_base({})` returns **0.0** — no exception, no None. So a substation
that was ingested but never enriched still scores, as:

    R_final = soft_clip_upper(0.0 × Π mult) + Σ(add − 1.0)
            = Σ(add − 1.0)

The published number is the flood additive term and nothing else. Zero
contribution from criticality, vulnerability, infrastructure, exposure,
socio-economics or trajectory — the six things the index exists to measure.

Measured on 19 August 2026: **78,505 substations, 10.9 % of the cohort**, across
poland (91.9 % of its fleet), austria (95.0 %), czechia (87.9 %), belgium,
lithuania, slovenia, netherlands, latvia, denmark, australia and others.
Published as Low 48,588 · Medium 23,145 · High 3,453 · Critical 3,310 ·
Extreme 9. Every one of them looks like an ordinary score on the public site.

WHY A RESCORE DOES NOT FIX IT
─────────────────────────────
Phase ζ re-runs `score_substation`, which cannot build components. It
reproduces these values unchanged and stamps fresh provenance on them. The 79
`legacy-drift` XFAILs carry the mitigation *"operator --all refresh re-emits via
post-PR-3 canonical engine"* — that refresh does not build components either.

WHAT THIS SENTINEL PINS
───────────────────────
A record may be unscored (no `R_median`) — that is honest, and G5 reports it.
A record may be scored from real components — that is correct.
A record may NOT carry a score derived from nothing. That is the one state the
index must never publish, because it is indistinguishable from a real result.

Two independent detections, agreeing to 99.8 % on the measured cohort:
  1. empty `components` + non-null `R_median`
  2. `CI_width == 0.0` — a 10,000-draw Monte Carlo never yields exactly zero
     spread; it means there was nothing to perturb

THIS TEST IS EXPECTED TO FAIL UNTIL THE ENRICHMENT BACKLOG IS CLEARED.
Do not xfail it. An xfail with a mitigation note is exactly how the Sweden
fleet-floor refusal (M-044) was silenced for a month. If the count needs to be
burnt down incrementally, lower `MAX_ALLOWED` deliberately and leave the
history visible in this file.

Cross-reference: modification-log M-046, M-007, M-044.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ._ssi_test_support import load_ssi_data, substation_list  # noqa: E402

COUNTRIES = sorted(
    json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())["slugs"]
)

#: Substations permitted to carry a score with no components behind it.
#: Zero. Raise this only with a recorded decision, never to make a run green.
MAX_ALLOWED = 0

#: Measured 19 August 2026, for drift detection. If a country's count moves
#: without a corresponding entry in the modification log, something changed the
#: data outside the tracked pipeline.
BASELINE_20260819 = {
    "poland": 25509, "austria": 13979, "czechia": 7825, "belgium": 5428,
    "australia": 4487, "lithuania": 4396, "netherlands": 3809, "latvia": 3425,
    "denmark": 2389, "slovenia": 1571, "estonia": 1178, "canada": 1107,
}


def _fabricated(subs):
    """Records carrying a score that no component data supports."""
    out = []
    for s in subs:
        r = s.get("R_median")
        if r is None:
            continue  # unscored is honest — G5 owns that case
        if not s.get("components"):
            out.append(s)
    return out


def _zero_spread(subs):
    """Records whose Monte Carlo produced exactly zero spread."""
    return [
        s for s in subs
        if s.get("R_median") is not None
        and isinstance(s.get("CI_width"), (int, float))
        and abs(s["CI_width"]) < 1e-12
    ]


@pytest.fixture(scope="module", params=COUNTRIES)
def country(request):
    return request.param


@pytest.fixture(scope="module")
def subs(country):
    fp = REPO_ROOT / country / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{country}/ssi-data.json absent in this checkout")
    return substation_list(load_ssi_data(country, REPO_ROOT))


class TestScoresAreComponentBacked:

    def test_no_score_without_components(self, country, subs):
        bad = _fabricated(subs)
        if len(bad) <= MAX_ALLOWED:
            return
        bands: dict[str, int] = {}
        for s in bad:
            bands[s.get("classification")] = bands.get(s.get("classification"), 0) + 1
        ex = bad[0]
        pytest.fail(
            f"{country}: {len(bad)} of {len(subs)} substations "
            f"({100 * len(bad) / len(subs):.1f}%) publish an R_median with an "
            f"EMPTY components dict. R_base is 0.0, so the score is the "
            f"additive modifier term alone — no criticality, vulnerability, "
            f"infrastructure, exposure, socio-economic or trajectory input.\n"
            f"  published bands: {bands}\n"
            f"  example: {ex.get('substation_id')} "
            f"R_median={ex.get('R_median')} R_base_median={ex.get('R_base_median')} "
            f"CI_width={ex.get('CI_width')} classification={ex.get('classification')!r}\n"
            f"  A rescore will NOT fix this — score_substation reads components, "
            f"it does not build them. These records need an enrichment pass."
        )

    def test_r_base_zero_implies_unscored(self, country, subs):
        """R_base_median == 0.0 with a published score is the same defect,
        detected without looking at the components dict."""
        bad = [
            s for s in subs
            if s.get("R_median") is not None
            and isinstance(s.get("R_base_median"), (int, float))
            and abs(s["R_base_median"]) < 1e-12
        ]
        assert len(bad) <= MAX_ALLOWED, (
            f"{country}: {len(bad)} substations publish a score on "
            f"R_base_median == 0.0. Example: {bad[0].get('substation_id')} "
            f"→ R_median={bad[0].get('R_median')}"
        )

    def test_monte_carlo_produced_real_spread(self, country, subs):
        """CI_width == 0.0 over 10,000 draws means nothing was perturbed."""
        bad = _zero_spread(subs)
        assert len(bad) <= MAX_ALLOWED, (
            f"{country}: {len(bad)} substations have CI_width == 0.0. A "
            f"10,000-iteration Monte Carlo cannot produce zero spread from "
            f"real inputs. Example: {bad[0].get('substation_id')} "
            f"→ R_P5={bad[0].get('R_P5')} R_median={bad[0].get('R_median')} "
            f"R_P95={bad[0].get('R_P95')}"
        )


class TestCohortRollup:

    def test_cohort_total(self):
        """One number the operator can track to zero."""
        total = affected = 0
        per_country = {}
        for c in COUNTRIES:
            if not (REPO_ROOT / c / "ssi-data.json").exists():
                continue
            s = substation_list(load_ssi_data(c, REPO_ROOT))
            total += len(s)
            n = len(_fabricated(s))
            if n:
                per_country[c] = n
                affected += n
        worst = dict(sorted(per_country.items(), key=lambda kv: -kv[1])[:8])
        assert affected <= MAX_ALLOWED, (
            f"COHORT: {affected:,} of {total:,} substations "
            f"({100 * affected / total:.1f}%) publish a score with no component "
            f"data behind it. Worst: {worst}. "
            f"Baseline at discovery (19 Aug 2026) was 78,505 — see M-046."
        )

    def test_no_country_regressed_against_the_discovery_baseline(self):
        """The population must shrink, never grow.

        A country whose count rises has had records ingested-but-not-enriched
        since the baseline, or has had components stripped by a later writer.
        Either way it is a new event, not the known backlog.
        """
        grown = {}
        for c, base in BASELINE_20260819.items():
            if not (REPO_ROOT / c / "ssi-data.json").exists():
                continue
            n = len(_fabricated(substation_list(load_ssi_data(c, REPO_ROOT))))
            if n > base:
                grown[c] = (base, n)
        assert not grown, (
            f"These countries have MORE component-less scores than at "
            f"discovery: {grown}. The backlog is meant to burn down. A rise "
            f"means new records were scored without enrichment, or a writer "
            f"stripped components from records that had them."
        )


class TestZeroVectorIsRefusedAtSource:
    """M-057 — the guard above tests the *data*; these test the *function*.

    145 records survived the original M-046 remediation by carrying a components
    dict that was present, complete, and entirely 0.0 (canada 137, turkey 6, plus
    two with one component at 3e-4). `compute_r_base` accepted them, returned
    0.0, and the pipeline published R_median with CI_width exactly 0.0 and a
    "Low" classification — the identical fabricated output the M-046 guard
    exists to prevent, reached through a populated dict instead of an empty one.

    An all-zero vector is not an observation. The components are P5/P95
    normalised, so six simultaneous exact zeros would put one substation at the
    fleet floor of every axis at once, and the zero-width confidence interval
    proves the Monte Carlo had nothing to perturb.

    These assertions are on the function rather than on the cohort so that a
    refactor which deletes the guard fails immediately, without waiting for a
    rescore to reintroduce the bad rows.
    """

    def test_all_zero_vector_returns_none(self):
        from scripts.pipeline.scoring.engine import compute_r_base
        assert compute_r_base({"C": 0.0, "V": 0.0, "I": 0.0, "E": 0.0, "S": 0.0, "T": 0.0}) is None, (
            "compute_r_base accepted an all-zero component vector. It yields "
            "R_base = 0.0 — the most resilient end of a risk scale — from no "
            "evidence at all, which is M-046 exactly. Return None so the record "
            "classifies Unclassified (Convention #56)."
        )

    def test_empty_and_keyless_still_return_none(self):
        from scripts.pipeline.scoring.engine import compute_r_base
        assert compute_r_base({}) is None
        assert compute_r_base({"not_a_component": 1.0}) is None

    def test_a_single_nonzero_component_in_a_FULL_vector_is_still_scored(self):
        """The refusal must stay narrow — within a complete vector.

        SUPERSEDED IN PART, 20 August 2026 (M-061). This test previously
        asserted that `compute_r_base({"C": 0.58})` scores, on the reasoning
        that "partial data is data". That was written when nothing in the
        estate could produce components incrementally, so the only reachable
        case was all-or-nothing.

        `ingestion/components.py` changed that: it builds letters as sources
        arrive, so a vector with I and E but not C/V/S/T is now reachable.
        Scoring it would count 0.65 of the weight as zero risk — M-046's exact
        failure, in the same reassuring direction. Incomplete vectors are now
        refused, and this test pins the *remaining* narrowness: a complete
        vector with small or zero individual entries still scores.
        """
        from scripts.pipeline.scoring.engine import compute_r_base
        full = {"C": 0.58, "V": 0.2, "I": 0.3, "E": 0.4, "S": 0.5, "T": 0.6}
        assert compute_r_base(full) is not None
        assert compute_r_base({"C": 0.0, "V": 0.0, "I": 0.0, "E": 0.0,
                               "S": 0.0, "T": 0.0003}) is not None, (
            "a complete vector that is merely near-zero must still score — it "
            "is caught downstream on the Monte Carlo's own evidence, not here."
        )

    def test_incomplete_vectors_are_refused(self):
        """M-061 — the unmeasured weight must not be counted as zero risk."""
        from scripts.pipeline.scoring.engine import compute_r_base
        full = {"C": 0.5, "V": 0.5, "I": 0.5, "E": 0.5, "S": 0.5, "T": 0.5}
        assert compute_r_base({"I": 0.5, "E": 0.5}) is None, (
            "a vector holding only I and E scored. The other four letters "
            "carry 0.65 of R_base and would be counted as zero — i.e. as "
            "maximum resilience — on no evidence at all."
        )
        for drop in full:
            partial = {k: v for k, v in full.items() if k != drop}
            assert compute_r_base(partial) is None, (
                f"vector missing only {drop} still scored; every letter is "
                f"load-bearing and none may default"
            )

    def test_the_guard_uses_no_numeric_threshold(self):
        """`R_base < some_epsilon` would be an invented cut-off (Discipline #50).

        The refusal is structural — 'every present component is exactly zero' —
        not a judgement about how small is too small. Records that are merely
        near-zero are caught downstream by the zero-spread detection above,
        on the evidence of the Monte Carlo rather than on a chosen constant.
        """
        import ast
        import inspect
        from scripts.pipeline.scoring import engine

        # Parse the executable body only. The docstring legitimately *names*
        # the threshold it refuses to use; the code must not contain one.
        fn = ast.parse(inspect.getsource(engine.compute_r_base).lstrip()).body[0]
        body = fn.body[1:] if (fn.body and isinstance(fn.body[0], ast.Expr)
                               and isinstance(fn.body[0].value, ast.Constant)
                               and isinstance(fn.body[0].value.value, str)) else fn.body

        tiny = [
            node.value for stmt in body for node in ast.walk(stmt)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, float)
            and 0 < abs(node.value) < 0.001
        ]
        assert not tiny, (
            f"compute_r_base has grown a numeric epsilon ({tiny}). Refuse on the "
            "structure of the vector — 'every present component is exactly zero' "
            "— not on a threshold somebody picked. A chosen constant is the "
            "branch Discipline #50 warns against."
        )


class TestStoredScoreMatchesStoredComponents:
    """M-058 — detection 4: the stored score must be derivable from the stored inputs.

    Detections 1–3 above each test a *symptom* of scoring without evidence:
    empty components, R_base_median == 0.0, zero Monte Carlo spread. All three
    reported clean on the UK while 25,624 substations — 91% of its scored fleet
    — published the identical score R_median = 0.0855, classified "Low", on top
    of real and varied component vectors.

    They were scored when `components` was empty (R_base = 0, so R_final
    collapsed to the per-country constant Σ(add_i − 1.0)), and a later
    enrichment pass populated `components` without the rescore that
    METHODOLOGY_DISCIPLINES §5bis Criterion 2 requires. Detection 1 could not
    see them because the components were present; detection 3 could not, because
    CI_width was non-zero — left over from an unrelated run and contradicting
    the record's own R_P5 == R_P95. Only detection 2 caught them, and only for
    the 25,624 whose stale R_base_median was *exactly* 0.0; a further 445 held
    0.0004–0.0009 and slipped past even that.

    This detection is the generalisation the other three are special cases of:

        round(compute_r_base(components), 4) == stored R_base_median

    Both sides are 4-decimal quantities, so this is an exact comparison at the
    stored precision, not a tolerance. It catches any divergence between what a
    record claims to have been scored from and what it actually holds — stale
    scores, half-applied enrichment, a writer that updated inputs without
    triggering a rescore — including shapes nobody has seen yet.

    Rescored under the operator decision of 20 August 2026: recompute locally
    rather than retire, because unlike M-046/M-053/M-057 the inputs here are
    real and complete. Every one of the 25,624 moved off "Low" — 23,794 to
    Medium and 1,830 to High. The fabricated constant had been understating
    risk across the entire fleet.

    Do not xfail this test. If a legitimate reason ever exists for a stored
    R_base_median to differ from its components, that reason belongs in the
    record as a marker, not in a skip.
    """

    MAX_ALLOWED = 0

    def test_stored_r_base_matches_components(self, country, subs):
        from scripts.pipeline.scoring.engine import compute_r_base

        bad = []
        for s in subs:
            if s.get("R_median") is None:
                continue                      # Unclassified — nothing to check
            stored = s.get("R_base_median")
            if stored is None:
                continue
            recomputed = compute_r_base(s.get("components") or {})
            if recomputed is None:
                continue                      # caught by detections 1 and 2
            if round(recomputed, 4) != stored:
                bad.append((s.get("substation_id"), stored, round(recomputed, 4)))

        worst = sorted(bad, key=lambda b: -abs(b[2] - b[1]))[:5]
        assert len(bad) <= self.MAX_ALLOWED, (
            f"{country}: {len(bad):,} substations publish a score whose stored "
            f"R_base_median does not match their own components.\n"
            f"  worst (id, stored, from components): {worst}\n\n"
            "The score was computed from different inputs than the record now "
            "carries — inputs changed without a rescore (§5bis Criterion 2). "
            "Either rescore them (if the components are real and complete) or "
            "retire the score to Unclassified (if they are not). Do not adjust "
            "the stored R_base_median to agree: that makes the record "
            "self-consistent and still wrong."
        )
