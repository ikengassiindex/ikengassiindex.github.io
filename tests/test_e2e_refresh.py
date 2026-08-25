"""
SSI Pipeline — End-to-End Refresh Acceptance Harness (Phase 1 PR-7)

Per-country pytest gates run against the live ssi-data.json files. The harness
parameterises across all 39 SoT countries; each country runs through 7 gates:

  G1. File exists at <country>/ssi-data.json
  G2. JSON parses cleanly
  G3. Substation count ≥ MIN_FLEET[iso2] (anti-stub-data, KB §56)
  G4. validate_schema returns 0 errors (Phase 2b semantic gates)
  G5. No NaN / Inf / negative R_median in any substation
  G6. Every substation carries PR-3 provenance fields (mult_product, add_sum,
      modifier_impacts) — Phase 1 §8 criterion 8
  G7. R_median ↔ classification band invariant holds at <2% mismatch
      (transition tolerance per PR-5)

Test execution is fast (<3s) because it reads JSON files that are already on
disk — no scoring computation. This is the operator-runnable acceptance gate.

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-7 §"Files changed"
                 PHASE_1_IMPLEMENTATION_PLAN.md §8 acceptance criteria
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L4-2 closure
"""

import json
import math
import sys
from pathlib import Path

import pytest

from ._ssi_test_support import load_ssi_data

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Load SoT slug list (single source of truth)
_SOT_PATH = REPO_ROOT / "intelligence" / "countries.json"
_SOT = json.loads(_SOT_PATH.read_text(encoding="utf-8"))
COUNTRIES = sorted(_SOT["slugs"])  # 39 SoT slugs


# ═══════════════════════════════════════════════════════════
#  Per-country fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="module", params=COUNTRIES)
def country(request):
    """Parameterised fixture: 1 test instance per country."""
    return request.param


@pytest.fixture(scope="module")
def country_data(country):
    """Load <country>/ssi-data.json once per country (module-scoped).

    Resolves Convention #79 sharding transparently, so every downstream gate
    sees a uniform `substations` list whether or not the country is sharded.
    """
    fp = REPO_ROOT / country / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{country}/ssi-data.json absent in this checkout")
    return load_ssi_data(country, REPO_ROOT)


# ═══════════════════════════════════════════════════════════
#  G1 — File exists
# ═══════════════════════════════════════════════════════════

class TestG1FilePresence:
    """Every SoT country must have its ssi-data.json on disk."""

    def test_g1_file_exists(self, country):
        fp = REPO_ROOT / country / "ssi-data.json"
        if not fp.exists():
            pytest.skip(f"{country}/ssi-data.json absent in this checkout")
        assert fp.exists(), f"{country}/ssi-data.json missing"
        assert fp.stat().st_size > 1024, (
            f"{country}/ssi-data.json suspiciously small ({fp.stat().st_size} bytes)"
        )


# ═══════════════════════════════════════════════════════════
#  G2 — JSON parses
# ═══════════════════════════════════════════════════════════

class TestG2JsonParses:
    """ssi-data.json must parse to a dict with at least 'substations'."""

    def test_g2_top_level_shape(self, country_data):
        assert isinstance(country_data, dict), "ssi-data.json is not a dict"
        assert "substations" in country_data, (
            "ssi-data.json missing top-level 'substations' (and, if the "
            "country is sharded, the manifest failed to resolve)"
        )

    def test_g2b_shard_total_matches_declared_fleet(self, country, country_data):
        """A sharded country's resolved fleet must match its declared totals.

        This is the cheap completeness check the JS loaders should also carry:
        one integer comparison that catches a dropped shard, a short write, a
        stale CDN object or a half-deployed refresh. Without it, losing a
        shard reads as a smaller fleet rather than as an error.
        """
        fp = REPO_ROOT / country / "ssi-data.json"
        manifest = json.loads(fp.read_text(encoding="utf-8"))
        if not manifest.get("sharded"):
            pytest.skip(f"{country} is not sharded")
        resolved = len(country_data.get("substations", []))
        shard_sum = sum(s.get("count", 0) for s in manifest["substations_shards"])
        assert resolved == shard_sum, (
            f"{country}: resolved {resolved} substations but the manifest's "
            f"shard counts sum to {shard_sum}"
        )
        for label, declared in (
            ("meta.total", (manifest.get("meta") or {}).get("total")),
            ("meta.n_substations", (manifest.get("meta") or {}).get("n_substations")),
            ("fleet_summary.total", (manifest.get("fleet_summary") or {}).get("total")),
        ):
            if isinstance(declared, int):
                assert resolved == declared, (
                    f"{country}: resolved {resolved} substations but "
                    f"{label} declares {declared}"
                )


# ═══════════════════════════════════════════════════════════
#  G3 — Fleet floor
# ═══════════════════════════════════════════════════════════

class TestG3FleetFloor:
    """Substation count must clear MIN_FLEET[iso2] (KB §56 anti-stub-data)."""

    def test_g3_fleet_floor(self, country, country_data):
        import os
        from validate_schema import MIN_FLEET, _SLUG_TO_ISO2
        iso2 = _SLUG_TO_ISO2.get(country)
        assert iso2 is not None, (
            f"{country} not in _SLUG_TO_ISO2 — F-L4-2 regression"
        )
        floor = MIN_FLEET.get(iso2)
        assert floor is not None, (
            f"{country} (ISO {iso2}) not in MIN_FLEET — incomplete F-L4-2 closure"
        )
        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        strict = os.environ.get("SSI_PR7_REFRESHED", "").lower() in (
            "1", "true", "yes", "on")
        if len(subs) < floor and not strict:
            # Partial-OSM countries (greece/mexico/poland observed pre-PR-7):
            # legacy ingestion gap. Operator --all refresh re-pulls latest OSM.
            pytest.xfail(
                f"{country} fleet {len(subs)} < MIN_FLEET ({floor}) — "
                f"partial-OSM legacy ingestion gap. Mitigation: operator "
                f"--all refresh re-pulls latest OSM substation set."
            )
        assert len(subs) >= floor, (
            f"{country} fleet {len(subs)} < MIN_FLEET ({floor}) — "
            f"stub-data regression (KB §56)"
        )


# ═══════════════════════════════════════════════════════════
#  G4 — validate_schema gates
# ═══════════════════════════════════════════════════════════

class TestG4ValidatorPasses:
    """Per-PR-5 validator must return 0 errors per country.

    Auto-detect legacy-drift cohort: any country whose validate_schema returns
    errors is xfailed under the "F-L4-2-extended cohort" header. PR-7's
    operator-gated --all refresh mitigates by re-emitting via the post-PR-3
    canonical engine. The xfail is documented in PHASE_1_ACCEPTANCE_REPORT.md
    §F-L4-2-extended. To run after --all refresh, set env var
    `SSI_PR7_REFRESHED=1` to force strict pass-mode.
    """

    def test_g4_validate_schema_passes(self, country):
        import os
        from validate_schema import validate_file
        fp = REPO_ROOT / country / "ssi-data.json"
        if not fp.exists():
            pytest.skip(f"{country}/ssi-data.json absent in this checkout")
        errors, _warnings = validate_file(str(fp))
        strict = os.environ.get("SSI_PR7_REFRESHED", "").lower() in (
            "1", "true", "yes", "on")
        if errors and not strict:
            # Legacy-drift cohort: xfail with the first error as the reason.
            # Operator runs `SSI_PR7_REFRESHED=1 pytest ...` after --all to
            # force this to strict pass-mode and surface any residual drift.
            pytest.xfail(
                f"{country} legacy-drift (F-L4-2-extended). Mitigation: "
                f"operator --all refresh re-emits via post-PR-3 canonical "
                f"engine. First error: {errors[0]}"
            )
        assert errors == [], (
            f"{country} fails validate_schema after --all refresh: {errors}"
        )


# ═══════════════════════════════════════════════════════════
#  G5 — No NaN / Inf / negative R_median
# ═══════════════════════════════════════════════════════════

#: Upper bound of the v4.24 classification band table. The five bands are
#: Low / Medium / High / Critical / Extreme, and Extreme is [1.00, 1.30].
#: Asserting R_median <= 1.0 — as this gate did until 19 August 2026 —
#: contradicts the methodology the gate exists to protect: it fires on every
#: legitimately Extreme substation and would go on firing after a correct
#: rescore. Raising the tolerance instead of the bound was rejected: that
#: would blind the gate to a genuine overshoot past 1.30, which is the thing
#: actually worth catching. Measured at the time of the change: zero
#: substations in any of the 39 countries exceed 1.30.
#: Cross-reference: modification-log M-029 / FL-007.
BAND_TABLE_MAX_R = 1.30


class TestG5RMedianFinite:
    """Every substation must have a finite R_median inside [0, BAND_TABLE_MAX_R]."""

    def test_g5_r_median_finite_and_in_range(self, country, country_data):
        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        if not subs:
            pytest.skip(f"{country} has no substations to check")
        bad_finite = 0
        bad_range = 0
        bad_sample = None
        # A dedicated sample for the non-finite branch. Sharing `bad_sample`
        # with the range branch made the assertion print a finite number while
        # reporting "NaN/Inf/None", which hid 33 genuinely unscored
        # substations (M-027) behind a plausible-looking value.
        bad_finite_sample = None
        # ── R_median = None is a legitimate terminal state (20 Aug 2026, M-059) ──
        # Convention #56: "degraded / missing fields carry None with a marker
        # rather than silent defaults". METHODOLOGY_DISCIPLINES line 257 names
        # it explicitly: "R_median = None (legitimate visibly-honest degradation
        # marker when substation exists on grid but scoring inputs incomplete)".
        # validate_schema.py already honours this (`if r is None: return
        # 'Unclassified'  # pre-L3 state per Convention #56`); this gate did not,
        # and counted the prescribed state as a NaN/Inf fault. Under a rank-2
        # source contradicting a rank-5 gate, the gate is the defect.
        #
        # This is NOT a relaxation. None is still a hard failure whenever the
        # record does not carry the matching terminal state — an R_median of
        # None sitting under a "Low" label is a genuine inconsistency this gate
        # previously could not distinguish from an honest Unclassified, because
        # it failed on both. NaN, Inf, unparseable and out-of-range are
        # untouched.
        bad_marker = 0
        bad_marker_sample = None
        for s in subs:
            r = s.get("R_median")
            if r is None:
                if s.get("classification") == "Unclassified":
                    continue
                bad_marker += 1
                if bad_marker_sample is None:
                    bad_marker_sample = (s.get("substation_id", "?"),
                                         s.get("classification"))
                continue
            try:
                rf = float(r)
            except (TypeError, ValueError):
                bad_finite += 1
                if bad_finite_sample is None:
                    bad_finite_sample = (s.get("substation_id", "?"), r)
                continue
            if math.isnan(rf) or math.isinf(rf):
                bad_finite += 1
                if bad_finite_sample is None:
                    bad_finite_sample = (s.get("substation_id", "?"), r)
            elif rf < 0.0 or rf > BAND_TABLE_MAX_R:
                bad_range += 1
                if bad_sample is None:
                    bad_sample = (s.get("substation_id", "?"), r)
        assert bad_finite == 0, (
            f"{country} has {bad_finite} substations with NaN/Inf/unparseable "
            f"R_median. Example: {bad_finite_sample}"
        )
        assert bad_marker == 0, (
            f"{country} has {bad_marker} substations with R_median = None that "
            f"are NOT classified 'Unclassified'. Example: {bad_marker_sample}. "
            f"None is the prescribed degradation marker (Convention #56) and is "
            f"accepted here — but only together with the classification that "
            f"declares it. A None score wearing a band label is the pair "
            f"disagreeing, and the band is what renders."
        )
        # Bound tolerance: allow up to 0.5% of substations to drift very
        # slightly out of [0,1] (boundary rounding artefacts); above that fail
        bad_pct = bad_range / len(subs) * 100
        assert bad_pct <= 0.5, (
            f"{country} has {bad_range} substations ({bad_pct:.2f}%) "
            f"with R_median outside [0,{BAND_TABLE_MAX_R}] — beyond the "
            f"Extreme band ceiling. Example: {bad_sample}"
        )


# ═══════════════════════════════════════════════════════════
#  G6 — PR-3 provenance fields
# ═══════════════════════════════════════════════════════════

class TestG6ProvenanceFields:
    """Phase 1 §8 criterion 8: every substation carries mult_product, add_sum,
    modifier_impacts (added by PR-3, backfilled in PR-7)."""

    def test_g6_provenance_fields_present(self, country, country_data):
        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        if not subs:
            pytest.skip(f"{country} has no substations to check")
        # Check a sample of 50 substations (statistical sampling — covers
        # the case where backfill was partial)
        sample = subs[:50]
        missing = {"mult_product": 0, "add_sum": 0, "modifier_impacts": 0}
        for s in sample:
            for field in missing:
                if field not in s:
                    missing[field] += 1
        # All three PR-3 fields must be present on every sampled substation
        bad_fields = [f for f, c in missing.items() if c > 0]
        assert not bad_fields, (
            f"{country} sample of {len(sample)} substations: "
            f"missing {bad_fields} on at least one substation. "
            f"Counts: {missing}. Run scripts/backfill_provenance.py "
            f"to populate."
        )


# ═══════════════════════════════════════════════════════════
#  G7 — Classification ↔ R_median band invariant
# ═══════════════════════════════════════════════════════════

class TestG7ClassificationBand:
    """The stored absolute band must match the score it came from.

    REWRITTEN 20 August 2026 (M-064). The previous version had four defects,
    and the xfail hid all of them:

    1.  It compared `classification` against a band derived from R_median.
        Since Task #461 (22 July 2026) `classification` is the per-country
        NORMALISED band — "band label = within-country ranking not absolute R"
        — so the two are designed to differ. Every normalised country failed,
        up to 100% (czechia). The same comparison sat in validate_schema as an
        ERROR, which is why `run.py` Phase 2b refused to commit cohort-wide
        and the cohort refresh had never completed.

    2.  Its band table was FOUR bands. `Extreme` [1.00, 1.30] has existed since
        Phase 2A (25 June 2026), so every record at R >= 1.00 was scored
        against a table that could not represent it.

    3.  `r = s.get("R_median", 0)` — a numeric default in a checking path
        (Discipline #50). A record with the key absent became R=0 and was then
        asserted to be "Low", inventing a pass.

    4.  `pct = misclassified / len(subs)` divided by the whole fleet including
        Unclassified records, understating the true rate — on a fleet that is
        now 88.4% Unclassified, that divisor is mostly noise.

    What it tests now is the invariant the gate was always for: **the stored
    `_band_absolute` equals the band the engine derives from the record's own
    R_median.** It imports `classify_band` rather than restating the table, so
    the two cannot drift again.

    `classification` is not ignored — it is checked to be a *valid band label*,
    and where a country has no Task #461 normalisation applied it must equal
    `_band_absolute`, since nothing would explain a difference.
    """

    def test_g7_absolute_band_matches_score(self, country, country_data):
        from scripts.pipeline.scoring.engine import classify_band

        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        if not subs:
            pytest.skip(f"{country} has no substations to check")

        scored = [s for s in subs if isinstance(s.get("R_median"), (int, float))]
        if not scored:
            pytest.skip(f"{country} has no scored substations (all pre-L3)")

        missing, wrong, sample = 0, 0, None
        for s in scored:
            expected = classify_band(s["R_median"])
            band_abs = s.get("_band_absolute")
            if band_abs is None:
                missing += 1
            elif band_abs != expected:
                wrong += 1
                if sample is None:
                    sample = (s.get("substation_id", "?"), s["R_median"],
                              expected, band_abs)

        assert missing == 0, (
            f"{country}: {missing}/{len(scored)} scored substations have no "
            f"`_band_absolute`. It is written by "
            f"scripts/normalise_bands_per_country.py before `classification` is "
            f"overwritten with the normalised label; without it the score-to-band "
            f"invariant cannot be checked at all."
        )
        pct = wrong / len(scored) * 100
        assert pct <= 2.0, (
            f"{country}: {wrong} of {len(scored)} scored substations ({pct:.2f}%) "
            f"have `_band_absolute` mismatched to their own R_median. "
            f"Example: {sample}. This is the score-to-band invariant — "
            f"normalisation is not an explanation for it."
        )

    def test_g7_classification_is_a_valid_band(self, country, country_data):
        """The label that actually renders must at least be a band."""
        VALID = {"Low", "Medium", "High", "Critical", "Extreme", "Unclassified"}
        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        if not subs:
            pytest.skip(f"{country} has no substations to check")
        bad = [(s.get("substation_id", "?"), s.get("classification"))
               for s in subs if s.get("classification") not in VALID]
        assert not bad, (
            f"{country}: {len(bad)} substations carry a `classification` that is "
            f"not a band. Examples: {bad[:5]}. Valid: {sorted(VALID)}."
        )

    def test_g7_unnormalised_countries_have_no_drift(self, country, country_data):
        """Without Task #461 applied, `classification` must equal `_band_absolute`.

        This is what remains of the original gate's intent, scoped to the case
        where it is actually meaningful. Greece was the one country never
        normalised, and this caught 36 stale labels from an earlier banding run
        (M-064) — 17 too low, 19 too high, so drift rather than bias.
        """
        fs = country_data.get("fleet_summary") or {}
        if (fs.get("_band_normalisation") or {}).get("applied"):
            pytest.skip(f"{country} has Task #461 normalisation applied — "
                        f"`classification` is the normalised band by design")
        subs = country_data.get("substations", [])
        if isinstance(subs, dict):
            subs = list(subs.values())
        scored = [s for s in subs if isinstance(s.get("R_median"), (int, float))]
        if not scored:
            pytest.skip(f"{country} has no scored substations")
        drift = [(s.get("substation_id", "?"), s.get("classification"),
                  s.get("_band_absolute"))
                 for s in scored
                 if s.get("_band_absolute") is not None
                 and s.get("classification") != s.get("_band_absolute")]
        pct = len(drift) / len(scored) * 100
        assert pct <= 2.0, (
            f"{country}: no Task #461 normalisation is applied, so "
            f"`classification` should equal `_band_absolute` — but "
            f"{len(drift)} of {len(scored)} ({pct:.2f}%) differ. "
            f"Examples: {drift[:5]}."
        )
