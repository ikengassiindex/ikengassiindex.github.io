"""Task #452 R2 Defect Class 3 — Migration_score Niva 2023 enrichment sentinel

Regression sentinel closing R2 Grid Equity Defect Class 3. Before Task #452:
`socio_economic.migration_score` was populated by
`scripts/pipeline/ingestion/socioeconomic.py` with genuine NUTS-3 / regional
values for ~10 countries (Norway 742 unique / Denmark 590 / Lithuania 332 /
Ireland 25 / Mexico 18 / New Zealand 67 / etc), a fleet-uniform 0.5
national scalar fallback for 8 Wave 4 majors + a fleet-uniform Italy
`-5.0` miscoding, and None for 19 countries entirely — the Task #450
SYSTEMIC signature at R2 Grid Equity axis. Task #452 replaced this via
real spatial-join pipeline against the Niva et al. 2023 20-yr sum gridded
net-migration raster (Nature Human Behaviour 7:2023-2037, DOI
10.1038/s41562-023-01689-4; dataset DOI 10.5281/zenodo.7997134; CC BY 4.0).

This sentinel pins six architectural invariants that together defeat the
drift class from re-entering:

  (1) UTILITY CONSTANT LOCK — `MAPPING_CONSTANT_K=200.0`, `AUDIT_TRAIL_VALUE`,
      `AUDIT_TRAIL_KEY`, `CRS_WGS84`. Any drift is a Task #452 methodology-
      version event.

  (2) MAPPING FORMULA — `0.5 + 0.5 * tanh(x/K)` round-trip verified for
      canonical anchor points. `x=0` MUST map to 0.5 exactly (neutral),
      symmetric behaviour around zero, saturates in [0, 1].

  (3) FLEET-UNIFORM DETECTION — `is_fleet_uniform_fallback()` correctly
      classifies six synthetic test cases: (a) 30k × 0.5 → True; (b) real
      distribution 742 unique → False; (c) all-None → False; (d) < 100 subs
      → False; (e) 18 unique values (Mexico-like) → False; (f) mixed
      Nones + 9k fleet-uniform → True.

  (4) AUDIT TRAIL — for every substation with `_migration_score_source`
      marker, the value equals the Task #452 canonical marker
      `NIVA_2023_20YR_SUM_v4_2_task_452`.

  (5) VALUE INVARIANT — every non-None `socio_economic.migration_score`
      value lies in [0.0, 1.0] (utility clamps by construction; sentinel
      guards downstream corruption).

  (6) REAL-DISTRIBUTION PRESERVATION — the 5 countries with pre-Task-#452
      genuine per-substation distributions (norway / lithuania / ireland /
      denmark / mexico / new-zealand) MUST NOT carry the Task #452 audit
      marker (skip proof). Their populated values were preserved untouched.

Cross-references:
  - Task #452           R2 Defect Class 3 (this workstream)
  - Task #451           R2 Defect Class 2 catchment_population (TEMPLATE)
  - Task #450           SYSTEMIC per-substation interpolation regression (parent)
  - Task #117 / #159    D2 modifier drift class (grandparent)
  - Convention #7       Data-Layer Anchoring documented-proxy (Niva as canonical)
  - Convention #56      Visibly-honest degradation (raster-gap subs → None)
  - Convention #60      Ikenga IS the ESG provider (Niva is CC BY 4.0 open)
  - Convention #79      ssi-data sharding (read_ssi_data)

Utility source:
  scripts/pipeline/enrichment/migration_score.py

Pre-flight audit:
  docs/audits/task_452_migration_score_preflight_20260723.yaml
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ═══════════════════════════════════════════════════════════
#  CONFIG — Task #452 invariants
# ═══════════════════════════════════════════════════════════

AUDIT_TRAIL_KEY = "_migration_score_source"
AUDIT_TRAIL_VALUE = "NIVA_2023_20YR_SUM_v4_2_task_452"
EXPECTED_K = 200.0

# Cohort SoT
COUNTRIES_JSON = REPO_ROOT / "intelligence" / "countries.json"

# Countries with genuine pre-Task-#452 per-substation distributions.
# For each: expected MINIMUM count of populated substations that MUST
# survive Task #452 without the audit marker (proof of NARROW-scope
# preservation).
#
# Values are derived from the Task #452 apply audit report — the
# `n_skipped_existing` field per country. Small safety margin below
# empirical value to allow future re-runs to modify these countries'
# Convention #56 rate without breaking the sentinel.
#
# Semantics:
#   count(subs with populated migration_score AND no marker) >= minimum
#
# If empirically 100% populated + 0% marker (Mexico, Norway), minimum is
# the total sub count. If partial coverage (Denmark, Ireland, Lithuania),
# minimum is the pre-existing populated count.
PRESERVED_MIN_UNMARKED_POPULATED = {
    "norway":       6_000,    # ~6,113 preserved (100% real distribution)
    "mexico":       3_000,    # ~3,085 preserved (100% real distribution)
    "turkey":       4_000,    # ~4,001 preserved (7 unique, real)
    "denmark":      2_400,    # ~2,433 preserved (590 unique)
    "new-zealand":  1_500,    # ~1,558 preserved (67 unique)
    "ireland":        990,    # ~  994 preserved (25 unique)
    "greece":         550,    # ~  556 preserved (13 unique)
    "lithuania":      500,    # ~  505 preserved (332 unique)
    "poland":       2_200,    # ~2,247 preserved (16 unique)
}
PRESERVED_REAL_DISTRIBUTION_COUNTRIES = frozenset(PRESERVED_MIN_UNMARKED_POPULATED.keys())


def _try_load_slugs() -> list[str]:
    try:
        return json.loads(COUNTRIES_JSON.read_text())["slugs"]
    except Exception:
        return []


_COHORT_SLUGS = _try_load_slugs()


# ═══════════════════════════════════════════════════════════
#  1 — UTILITY CONSTANT LOCK
# ═══════════════════════════════════════════════════════════

class TestUtilityConstantLock:
    """Task #452 utility constants are pinned.
    Any drift is a methodology-version event."""

    def test_utility_module_importable(self):
        from pipeline.enrichment import migration_score as ms  # noqa: F401

    def test_mapping_constant_k_locked(self):
        from pipeline.enrichment import migration_score as ms
        assert ms.MAPPING_CONSTANT_K == EXPECTED_K, (
            f"Range-mapping constant K drift: expected {EXPECTED_K}, "
            f"got {ms.MAPPING_CONSTANT_K}. K=200 is the Niva 2023 empirical "
            f"moderate-magnitude anchor per Gate A sign-off; changes require "
            f"operator sign-off + methodology version bump."
        )

    def test_audit_trail_value_locked(self):
        from pipeline.enrichment import migration_score as ms
        assert ms.AUDIT_TRAIL_VALUE == AUDIT_TRAIL_VALUE, (
            f"Audit-trail marker drift: expected '{AUDIT_TRAIL_VALUE}', "
            f"got '{ms.AUDIT_TRAIL_VALUE}'. Marker change breaks the "
            f"provenance chain for every enriched substation."
        )

    def test_audit_trail_key_locked(self):
        from pipeline.enrichment import migration_score as ms
        assert ms.AUDIT_TRAIL_KEY == AUDIT_TRAIL_KEY

    def test_crs_wgs84_declared(self):
        from pipeline.enrichment import migration_score as ms
        assert ms.CRS_WGS84 == "EPSG:4326"


# ═══════════════════════════════════════════════════════════
#  2 — MAPPING FORMULA — canonical round-trip
# ═══════════════════════════════════════════════════════════

class TestMappingFormula:
    """`score = 0.5 + 0.5 * tanh(raw / K)` — canonical anchor points."""

    def test_zero_maps_to_neutral(self):
        from pipeline.enrichment.migration_score import map_raw_to_score
        assert map_raw_to_score(0.0) == 0.5, (
            "raw=0 MUST map to 0.5 exactly (neutral by construction)."
        )

    def test_symmetric_around_zero(self):
        from pipeline.enrichment.migration_score import map_raw_to_score
        for raw in [10, 50, 100, 200, 500, 1000]:
            plus = map_raw_to_score(float(raw))
            minus = map_raw_to_score(float(-raw))
            # tanh is odd → f(x) + f(-x) = 1
            total = plus + minus
            assert abs(total - 1.0) < 1e-12, (
                f"Mapping asymmetry at raw=±{raw}: f(+)={plus}, f(-)={minus}, "
                f"sum={total} (expected 1.0)."
            )

    @pytest.mark.parametrize("raw,expected_min,expected_max", [
        (0.0, 0.5, 0.5),
        (100.0, 0.73, 0.74),
        (200.0, 0.88, 0.89),
        (500.0, 0.99, 1.0),
        (1000.0, 0.99, 1.0),
        (-100.0, 0.26, 0.27),
        (-200.0, 0.11, 0.12),
        (-500.0, 0.0, 0.01),
    ])
    def test_canonical_anchor_points(self, raw, expected_min, expected_max):
        from pipeline.enrichment.migration_score import map_raw_to_score
        score = map_raw_to_score(raw)
        assert expected_min <= score <= expected_max, (
            f"raw={raw} produced score={score:.4f}, expected in "
            f"[{expected_min}, {expected_max}]."
        )

    def test_saturates_in_unit_interval(self):
        from pipeline.enrichment.migration_score import map_raw_to_score
        # Extreme values MUST saturate cleanly — no over/undershoot
        assert 0.0 <= map_raw_to_score(1_000_000.0) <= 1.0
        assert 0.0 <= map_raw_to_score(-1_000_000.0) <= 1.0

    def test_none_input_returns_none(self):
        from pipeline.enrichment.migration_score import map_raw_to_score
        assert map_raw_to_score(None) is None

    def test_nan_input_returns_none(self):
        from pipeline.enrichment.migration_score import map_raw_to_score
        assert map_raw_to_score(float("nan")) is None


# ═══════════════════════════════════════════════════════════
#  3 — FLEET-UNIFORM DETECTION (Task #450 SYSTEMIC signature)
# ═══════════════════════════════════════════════════════════

def _synthetic_subs_uniform(n: int, val: float) -> list:
    return [{"socio_economic": {"migration_score": val}} for _ in range(n)]


def _synthetic_subs_multi(n: int, unique: int, base: float = 0.0) -> list:
    return [
        {"socio_economic": {"migration_score": base + (i % unique) * 0.01}}
        for i in range(n)
    ]


def _synthetic_subs_none(n: int) -> list:
    return [{"socio_economic": {"migration_score": None}} for _ in range(n)]


class TestFleetUniformDetection:
    """`is_fleet_uniform_fallback` correctly identifies Task #450 SYSTEMIC
    signature (n_unique==1 AND n_populated > threshold)."""

    def test_spain_like_fleet_uniform_detected(self):
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_uniform(30_000, 0.5)
        assert is_fleet_uniform_fallback(subs) is True

    def test_italy_like_fleet_uniform_negative_value_detected(self):
        """Italy has fleet-uniform -5.0 (miscoding). Detection MUST fire
        regardless of the specific uniform value."""
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_uniform(50_000, -5.0)
        assert is_fleet_uniform_fallback(subs) is True

    def test_norway_like_real_distribution_preserved(self):
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_multi(6_113, unique=742, base=0.01)
        assert is_fleet_uniform_fallback(subs) is False

    def test_belgium_like_all_none_preserved(self):
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_none(6_651)
        assert is_fleet_uniform_fallback(subs) is False

    def test_small_country_below_threshold_preserved(self):
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_uniform(50, 0.5)
        assert is_fleet_uniform_fallback(subs) is False

    def test_mexico_like_18_unique_preserved(self):
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = _synthetic_subs_multi(3_085, unique=18, base=-5.0)
        assert is_fleet_uniform_fallback(subs) is False

    def test_australia_like_mixed_none_and_uniform_detected(self):
        """Australia has 3,509 None + 9,056 fleet-uniform 0.5. Detection
        must fire on the populated subset."""
        from pipeline.enrichment.migration_score import is_fleet_uniform_fallback
        subs = (
            _synthetic_subs_none(3_509)
            + _synthetic_subs_uniform(9_056, 0.5)
        )
        assert is_fleet_uniform_fallback(subs) is True


# ═══════════════════════════════════════════════════════════
#  4 — COHORT SoT INTEGRITY
# ═══════════════════════════════════════════════════════════

class TestCohortSoT:
    def test_countries_json_exists(self):
        assert COUNTRIES_JSON.exists()

    def test_cohort_size(self):
        assert len(_COHORT_SLUGS) == 39

    def test_preserved_countries_all_in_cohort(self):
        for slug in PRESERVED_REAL_DISTRIBUTION_COUNTRIES:
            assert slug in _COHORT_SLUGS, (
                f"Preserved-distribution country '{slug}' missing from SoT. "
                f"Task #452 sentinel preservation set stale?"
            )


# ═══════════════════════════════════════════════════════════
#  5 — COHORT-WIDE VALUE + AUDIT-TRAIL INVARIANTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("slug", _COHORT_SLUGS)
def test_migration_score_value_invariant_for_task_452_writes(slug: str):
    """Every substation WRITTEN by Task #452 (marker present) MUST have
    migration_score in [0.0, 1.0]. Task #452's tanh mapping guarantees
    this by construction; sentinel guards against downstream corruption.

    IMPORTANT — Preserved pre-Task-#452 values are exempt. Some countries
    (new-zealand, ireland, greece) had populated distributions in ranges
    like [-0.39, +0.33] pre-Task-#452 — real per-substation values from
    the modern pipeline's socioeconomic.py output but NOT normalized to
    [0, 1]. Those semantic-drift issues are Task #450 SYSTEMIC scope,
    NOT Task #452 scope (NARROW-plus-fleet-uniform-override preserves
    them unchanged per Gate A sign-off).

    This invariant restricts the check to subs that carry Task #452's
    audit marker — the ones we actually wrote.
    """
    from pipeline.utils.ssi_data_sharding import read_ssi_data

    fp = REPO_ROOT / slug / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{slug}/ssi-data.json absent")

    data = read_ssi_data(fp)
    subs = data.get("substations", [])
    if not subs:
        pytest.skip(f"{slug}: zero substations")

    if subs and isinstance(subs[0], list):
        fields = data.get("sub_fields", [])
        subs = [dict(zip(fields, s)) for s in subs]

    out_of_range = []
    n_marked = 0
    for i, sub in enumerate(subs):
        se = sub.get("socio_economic") or {}
        marker = se.get(AUDIT_TRAIL_KEY)
        if marker != AUDIT_TRAIL_VALUE:
            continue  # Preserved pre-Task-#452 value — exempt
        n_marked += 1
        val = se.get("migration_score")
        if val is None:
            continue  # Convention #56 legitimate None
        if not isinstance(val, (int, float)):
            out_of_range.append((i, val))
            continue
        if not (0.0 <= val <= 1.0):
            out_of_range.append((i, val))

    if n_marked == 0:
        pytest.skip(f"{slug}: no Task #452 writes (all preserved)")

    assert not out_of_range, (
        f"{slug}: {len(out_of_range)} Task #452-written substations carry "
        f"migration_score outside [0, 1] range. First 5: {out_of_range[:5]}. "
        f"Utility clamps to [0, 1] by construction — this is a downstream "
        f"corruption signal."
    )


@pytest.mark.parametrize("slug", _COHORT_SLUGS)
def test_migration_score_audit_trail_marker(slug: str):
    """For every substation carrying `_migration_score_source` marker,
    the value MUST equal the Task #452 canonical marker. Catches any
    downstream code path that writes population without going through
    the utility (would corrupt provenance chain)."""
    from pipeline.utils.ssi_data_sharding import read_ssi_data

    fp = REPO_ROOT / slug / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{slug}/ssi-data.json absent")

    data = read_ssi_data(fp)
    subs = data.get("substations", [])
    if not subs:
        pytest.skip(f"{slug}: zero substations")

    if subs and isinstance(subs[0], list):
        fields = data.get("sub_fields", [])
        subs = [dict(zip(fields, s)) for s in subs]

    wrong_marker = []
    for i, sub in enumerate(subs):
        se = sub.get("socio_economic") or {}
        marker = se.get(AUDIT_TRAIL_KEY)
        if marker is None:
            continue
        if marker != AUDIT_TRAIL_VALUE:
            wrong_marker.append((i, marker))

    assert not wrong_marker, (
        f"{slug}: {len(wrong_marker)} substations carry a WRONG "
        f"'_migration_score_source' marker (expected "
        f"'{AUDIT_TRAIL_VALUE}'). First 5: {wrong_marker[:5]}."
    )


# ═══════════════════════════════════════════════════════════
#  6 — REAL-DISTRIBUTION PRESERVATION (NARROW scope proof)
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("slug", sorted(PRESERVED_REAL_DISTRIBUTION_COUNTRIES))
def test_real_distribution_country_preservation(slug: str):
    """NARROW-scope preservation invariant.

    For each PRESERVED country, at least `PRESERVED_MIN_UNMARKED_POPULATED[slug]`
    substations MUST post-Task-#452 carry:
      - `migration_score` populated (non-None)
      - AND NO Task #452 audit marker

    This is the proof that Task #452 skipped the country's genuine per-
    substation distribution cleanly. If the count drops below the minimum,
    fleet-uniform detection had a false positive OR the utility's skip
    logic broke.

    NOTE — this ADDS to any Nones-filled-with-marker subs (those are
    correctly written by Task #452). We're specifically checking that
    the pre-existing real-distribution subs survived untouched.
    """
    from pipeline.utils.ssi_data_sharding import read_ssi_data

    fp = REPO_ROOT / slug / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{slug}/ssi-data.json absent")

    data = read_ssi_data(fp)
    subs = data.get("substations", [])
    if not subs:
        pytest.skip(f"{slug}: zero substations")

    if subs and isinstance(subs[0], list):
        fields = data.get("sub_fields", [])
        subs = [dict(zip(fields, s)) for s in subs]

    n_populated_unmarked = 0
    for sub in subs:
        se = sub.get("socio_economic") or {}
        val = se.get("migration_score")
        marker = se.get(AUDIT_TRAIL_KEY)
        if val is not None and marker != AUDIT_TRAIL_VALUE:
            n_populated_unmarked += 1

    expected_min = PRESERVED_MIN_UNMARKED_POPULATED[slug]
    assert n_populated_unmarked >= expected_min, (
        f"{slug}: only {n_populated_unmarked} populated substations lack "
        f"the Task #452 marker (expected >= {expected_min}). Task #452's "
        f"NARROW-scope preservation failed — real distribution was "
        f"overwritten. Investigate fleet-uniform detection false-positive "
        f"or update PRESERVED_MIN_UNMARKED_POPULATED[{slug!r}] if this "
        f"country's distribution genuinely shifted."
    )
