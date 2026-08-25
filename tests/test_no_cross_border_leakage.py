"""
SSI Pipeline — Cross-Border Substation Enforcement Tests (Discipline #36)

Regression sentinel for the failure-mode the 18 June 2026 audit surfaced:
per-country ssi-data.json was inheriting substations from neighbouring
countries via ingestion bounding-box overshoot.

Pre-fix worst cases:
  - Austria  47.5% outside (665 Bavarian / Slovenian / South-Tyrolean substations
              misattributed to Austrian Bundesländer)
  - Canada   74.4% outside (US / Greenland-coords substations)
  - Greenland 86.5% outside (mostly Iceland + Canadian Arctic)
  - Norway   23.4% outside (fjord-coastline simplification artefacts)
  - UK       19.2% outside (Northern Ireland polygon gap)
  - France   ??.?% outside (DOM-TOM polygon gap)
  - Mexico   22.5% outside (US border overshoot)

Post-fix (commit 86d7c9df, PR #1, 24 June 2026):
  - All 39 countries ≤5% outside their bounds.json polygon (with per-country
    tolerance from cross_border_tolerances.json — default 100m, Greenland/
    New-Zealand/Denmark/Norway 5km for fjord/coastline simplification).

This sentinel runs the same check that .github/workflows/validate.yml runs
as a CI gate — but at pytest level so anyone running `pytest tests/` locally
catches a regression before pushing. Marked @pytest.mark.integration +
@pytest.mark.slow because it loads 39 country polygons + 174,046 substations
through shapely.

The 8 tests below split into three classes:
  - TestBoundsTopology       — every bounds.json parses + is non-empty
  - TestCrossBorderGate      — the 5%-outside-polygon enforcement gate
  - TestKnownLeakers         — explicit regression guards for the 7 originally-
                                leaking countries (must stay ≤5% forever)

Cross-references:
  - CROSS_BORDER_SUBSTATION_AUDIT_20260618.md — original audit memo
  - MODE_2_3_FOLLOWON_PLAN.md                — second-wave remediation plan
  - PR_CROSS_BORDER_GUARD.md                 — PR-ready description
  - .github/workflows/validate.yml           — CI gate (same check, runs on PR)
  - .github/workflows/pipeline-enrichment.yml — pipeline auto-remediation step
  - scripts/check_cross_border.py            — the deploy-gate CLI tool
  - scripts/remediate_cross_border.py        — the one-shot fixer CLI tool
  - cross_border_tolerances.json             — per-country tolerance config
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ═══════════════════════════════════════════════════════════
#  CONFIG — single source of truth for the threshold
# ═══════════════════════════════════════════════════════════

# 5% outside-polygon threshold matches scripts/check_cross_border.py default.
# Change here only when changing the CI gate threshold (.github/workflows/
# validate.yml + pipeline-enrichment.yml) too. The post-fix audit found every
# remediated country sits comfortably below this — Austria at 0.0% (741/741
# inside), the others similar. The 5% headroom tolerates upstream OSM
# refresh drift without false-firing.
THRESHOLD_PCT = 5.0

# The 7 countries that were materially leaking pre-fix. They MUST stay ≤5%
# forever — any regression here is a structural failure (filter not applied,
# bounds.json reverted, tolerance config corrupted). Greenland + New-Zealand
# join from the Mode 2 (coastline tolerance) remediation queue.
KNOWN_PREVIOUSLY_LEAKING = [
    "austria",
    "canada",
    "chile",
    "france",
    "mexico",
    "norway",
    "uk",
    "greenland",
    "new-zealand",
    "denmark",
]


def _all_country_slugs():
    """Read intelligence/countries.json::slugs — the canonical 39-country list."""
    return json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())["slugs"]


def _country_has_bounds(slug):
    return (REPO_ROOT / slug / "bounds.json").exists()


def _country_has_ssi_data(slug):
    return (REPO_ROOT / slug / "ssi-data.json").exists()


# ═══════════════════════════════════════════════════════════
#  TestBoundsTopology — every bounds.json must be loadable
# ═══════════════════════════════════════════════════════════

class TestBoundsTopology:
    """Per-country bounds.json must parse + yield a non-empty polygon."""

    @pytest.mark.integration
    @pytest.mark.parametrize("slug", _all_country_slugs())
    def test_bounds_json_loads_and_is_non_empty(self, slug):
        """
        Every slug in intelligence/countries.json must either have a bounds.json
        that parses to a non-empty polygon (after topology-healing via shapely
        buffer(0)) OR be explicitly skipped because no bounds.json is shipped
        for that slug yet (Mode 4 closure: the file just isn't there yet).

        The audit memo (18 June 2026) found 4 countries with topology-invalid
        bounds.json — Belgium, Costa Rica, Iceland, Japan. The auto-heal via
        buffer(0) inside load_country_polygon() resolves those cases.
        """
        if not _country_has_bounds(slug):
            pytest.skip(f"{slug}: no bounds.json shipped yet (Mode 4 — bounds backlog)")

        try:
            from scripts.pipeline.utils.geo import load_country_polygon
        except ImportError:
            pytest.skip("shapely not installed; run `pip install shapely>=2.0`")

        poly = load_country_polygon(slug)
        assert poly is not None, (
            f"{slug}: load_country_polygon returned None. bounds.json may be "
            f"empty, malformed, or carry no valid sub-national polygons."
        )
        assert not poly.is_empty, (
            f"{slug}: polygon is empty after topology-healing. bounds.json "
            f"may contain only zero-area features."
        )
        assert poly.is_valid, (
            f"{slug}: polygon failed shapely validity check even after "
            f"buffer(0) healing. Manual topology repair needed."
        )


# ═══════════════════════════════════════════════════════════
#  TestCrossBorderGate — the 5%-outside enforcement gate
# ═══════════════════════════════════════════════════════════

class TestCrossBorderGate:
    """
    Cohort-wide enforcement: every country with bounds.json + ssi-data.json
    must have ≤5% of its substations outside the national polygon (after
    per-country tolerance from cross_border_tolerances.json is applied).

    This is the SAME check that .github/workflows/validate.yml runs as a CI
    gate. The pytest version exists so anyone running `pytest tests/` locally
    catches a regression before pushing — the CI gate runs only on push/PR
    events.
    """

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.parametrize("slug", _all_country_slugs())
    def test_country_inside_polygon_within_threshold(self, slug):
        """
        For each country, run the same point-in-polygon audit the CI gate runs.
        Skip if no bounds.json (Mode 4 backlog) or no ssi-data.json (empty
        canonical). Fail if outside-% exceeds 5% threshold.
        """
        if not _country_has_bounds(slug):
            pytest.skip(f"{slug}: no bounds.json (Mode 4 backlog)")
        if not _country_has_ssi_data(slug):
            pytest.skip(f"{slug}: no ssi-data.json")

        try:
            from scripts.pipeline.utils.geo import cross_border_audit
        except ImportError:
            pytest.skip("shapely not installed; run `pip install shapely>=2.0`")

        result = cross_border_audit(slug)
        if result is None:
            pytest.skip(f"{slug}: cross_border_audit returned None")

        outside_pct = result.get("outside_pct", 0.0)
        inside = result.get("inside_count", 0)
        outside = result.get("outside_count", 0)
        total = inside + outside

        assert outside_pct <= THRESHOLD_PCT, (
            f"{slug}: {outside_pct:.1f}% outside polygon "
            f"({outside}/{total} substations) exceeds {THRESHOLD_PCT}% threshold. "
            f"This is the Discipline #36 cross-border gate firing. Run "
            f"`python3 scripts/remediate_cross_border.py {slug}` to fix, then "
            f"re-run this test. See CROSS_BORDER_SUBSTATION_AUDIT_20260618.md."
        )


# ═══════════════════════════════════════════════════════════
#  TestKnownLeakers — explicit regression guards
# ═══════════════════════════════════════════════════════════

class TestKnownLeakers:
    """
    The 10 countries that were materially leaking before the 18 June 2026
    remediation. They were each fixed in PR #1 (commit 86d7c9df). Any
    regression here means the fix has been silently undone — either the
    bounds.json was reverted, the tolerance config corrupted, or the
    upstream ingestion ran without the post-ingestion remediation step.

    These are belt-and-braces guards on top of the cohort-wide gate above —
    they make sure the SPECIFIC countries that were caught leaking stay
    caught if the gate ever stops working.
    """

    @pytest.mark.integration
    @pytest.mark.parametrize("slug", KNOWN_PREVIOUSLY_LEAKING)
    def test_known_leaker_has_bounds_json(self, slug):
        """The bounds.json for each remediated country must exist."""
        assert _country_has_bounds(slug), (
            f"{slug}: bounds.json missing. This country was remediated in PR #1 "
            f"(commit 86d7c9df, Discipline #36) and the bounds.json was committed "
            f"alongside the cleaned ssi-data.json. If bounds.json is gone, the "
            f"filter has no polygon to test against and the next ingestion will "
            f"silently re-leak."
        )

    @pytest.mark.integration
    @pytest.mark.parametrize("slug", KNOWN_PREVIOUSLY_LEAKING)
    def test_known_leaker_has_ssi_data_json(self, slug):
        """The ssi-data.json for each remediated country must exist."""
        assert _country_has_ssi_data(slug), (
            f"{slug}: ssi-data.json missing. The remediated cohort canonical was "
            f"committed in PR #1; if it's gone the country page won't render."
        )

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.parametrize("slug", KNOWN_PREVIOUSLY_LEAKING)
    def test_known_leaker_within_threshold(self, slug):
        """Each previously-leaking country must stay ≤5% outside polygon forever."""
        try:
            from scripts.pipeline.utils.geo import cross_border_audit
        except ImportError:
            pytest.skip("shapely not installed; run `pip install shapely>=2.0`")

        result = cross_border_audit(slug)
        assert result is not None, (
            f"{slug}: cross_border_audit returned None — bounds.json or "
            f"ssi-data.json may be malformed."
        )

        outside_pct = result.get("outside_pct", 0.0)
        assert outside_pct <= THRESHOLD_PCT, (
            f"{slug}: REGRESSION — {outside_pct:.1f}% outside polygon "
            f"exceeds the {THRESHOLD_PCT}% threshold. This country was "
            f"explicitly remediated in PR #1 (commit 86d7c9df). The fix has "
            f"been silently undone — investigate whether (a) bounds.json was "
            f"reverted, (b) tolerance config corrupted, (c) an ingestion ran "
            f"without the post-ingestion remediation step. See "
            f"CROSS_BORDER_SUBSTATION_AUDIT_20260618.md for full forensics."
        )


# ═══════════════════════════════════════════════════════════
#  TestToleranceConfig — cross_border_tolerances.json invariants
# ═══════════════════════════════════════════════════════════

class TestToleranceConfig:
    """The per-country tolerance config feeds the gate; it must stay well-formed."""

    @pytest.mark.unit
    def test_tolerance_config_parses(self):
        """cross_border_tolerances.json must be valid JSON with the expected shape."""
        config_path = REPO_ROOT / "cross_border_tolerances.json"
        assert config_path.exists(), (
            "cross_border_tolerances.json missing from repo root. The gate "
            "falls back to a 100m default if absent, but Mode 2 countries "
            "(Greenland, New Zealand, Norway, Denmark) need 5km coastline "
            "tolerance to pass — without the config they'll false-fire."
        )

        cfg = json.loads(config_path.read_text())
        assert "default_tolerance_km" in cfg, (
            "cross_border_tolerances.json missing 'default_tolerance_km' key."
        )
        assert "per_country" in cfg, (
            "cross_border_tolerances.json missing 'per_country' key."
        )

    @pytest.mark.unit
    def test_mode_2_countries_have_coastline_tolerance(self):
        """
        Greenland, New Zealand, Norway, Denmark were diagnosed as Mode 2
        (coastline-precision artefact, not actual cross-border leakage). They
        need a 5km tolerance to pass the gate. If this regresses, those four
        countries will fail the gate even though their data is correct.
        """
        cfg = json.loads((REPO_ROOT / "cross_border_tolerances.json").read_text())
        per_country = cfg.get("per_country", {})

        mode_2_countries = ["greenland", "new-zealand", "norway", "denmark"]
        for slug in mode_2_countries:
            tol = per_country.get(slug)
            assert tol is not None, (
                f"{slug}: tolerance missing from cross_border_tolerances.json. "
                f"This Mode 2 country needs an explicit per-country tolerance "
                f"(typically 5km) to pass the gate."
            )
            assert tol >= 1.0, (
                f"{slug}: tolerance {tol}km too tight for a Mode 2 country "
                f"(coastline-precision). The 18 June 2026 audit calibrated "
                f"5km for these four; tightening below ~1km will false-fire."
            )
