"""Task #451 R2 Defect Class 2 — Catchment population GHSL enrichment sentinel

Regression sentinel closing R2 Grid Equity Defect Class 2. Before Task #451:
`scripts/score-country.py` line 195 fabricated `socio_economic.population`
via `int(det_var(seed+'pop', ref.get('pop_density',50)*25, 0.40))` —
deterministic-variance synthetic in violation of Convention #56 (visibly-
honest degradation). Task #451 replaced this with a real spatial-join
pipeline against the GHSL Population Grid (EC JRC / Copernicus Emergency
Management Service, R2023A epoch E2025), computing 5 km catchment sums
per substation via Mollweide equal-area projection.

This sentinel pins four architectural invariants that together defeat the
drift class from re-entering:

  (1) STATIC — no live call to `det_var(seed+'pop', ...)` in
      `scripts/score-country.py`. The line MAY exist as a commented-out
      tombstone (per Convention #56 retire-with-tombstone pattern);
      it MUST NOT exist as a live call.

  (2) UTILITY CONSTANT LOCK — the catchment enrichment utility's
      constants (`DEFAULT_RADIUS_KM=5.0`, `AUDIT_TRAIL_VALUE`,
      `AUDIT_TRAIL_KEY`) are unchanged. Any drift is a Task #451
      methodology-version event that requires operator sign-off.

  (3) AUDIT TRAIL — for every substation with non-None
      `socio_economic.population`, the sibling field
      `_catchment_population_source` MUST equal the Task #451 canonical
      marker `GHSL_POP_R2023A_E2025_v4_2_task_451`. Catches any downstream
      code path that writes `population` without going through the GHSL
      enrichment utility.

  (4) VALUE INVARIANT — population values are non-negative integers
      ≤ 1e10 (upper bound generously above any realistic country
      population). Catches negative / float / synthetic-artifact
      corruption.

Cross-references:
  - Task #451           R2 Defect Class 2 (this workstream)
  - Task #450           SYSTEMIC Wave 4 per-substation interpolation
                        regression (parent class)
  - Task #117, #159     D2 modifier drift class (grandparent)
  - Convention #7       Data-Layer Anchoring documented-proxy pattern
                        (GHSL as canonical open-license source)
  - Convention #56      Visibly-honest degradation (retire-with-tombstone;
                        None fallback for raster-gap subs)
  - Convention #60      Ikenga IS the ESG provider (GHSL is public
                        institutional publisher, not commercial)
  - Convention #79      ssi-data sharding (this sentinel reads via
                        read_ssi_data to work through the shard manifest)

Utility source:
  scripts/pipeline/enrichment/catchment_population.py

Pre-flight audit:
  docs/audits/task_451_catchment_population_preflight_20260723.yaml

GHSL provenance:
  Publisher       : EC JRC / Copernicus Emergency Management Service
  Product         : GHS-POP R2023A, epoch E2025
  Coordinate sys  : Mollweide equal-area (ESRI:54009 native, EPSG:54009
                    documentation label)
  Resolution      : 30 arc-sec (~1 km at equator) via 1 km Mollweide grid
  License         : attribution-required open license
                    (Convention #7 + #60 compatible)
"""
from __future__ import annotations

import json
import re
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
#  CONFIG — Task #451 invariants
# ═══════════════════════════════════════════════════════════

# Canonical audit-trail values per Task #451 utility module. Any change
# here without a matching change in scripts/pipeline/enrichment/
# catchment_population.py is a drift-class violation.
AUDIT_TRAIL_KEY = "_catchment_population_source"
AUDIT_TRAIL_VALUE = "GHSL_POP_R2023A_E2025_v4_2_task_451"

# Sanity bound — no country's per-substation catchment_population should
# exceed 1 billion (higher than the largest metro on Earth by orders of
# magnitude). Catches accidental multiplication / bad decoding.
POPULATION_UPPER_BOUND = 1_000_000_000

# Static scan target
SCORE_COUNTRY_PATH = SCRIPTS_DIR / "score-country.py"

# Regex: 'population' key mapped to a `det_var(seed+'pop', ...)` synthetic
# generator. Matches the exact line 195 pattern that Task #451 retired.
# Applied to source with comment lines stripped (see stripped_source()).
BANNED_SYNTHETIC_PATTERN = re.compile(
    r"['\"]population['\"]\s*:\s*int\(\s*det_var\(\s*seed\s*\+\s*['\"]pop['\"]"
)

# Cohort SoT (KB §57)
COUNTRIES_JSON = REPO_ROOT / "intelligence" / "countries.json"


def _try_load_slugs() -> list[str]:
    """Load the 39-country cohort slug list. Return [] on any failure so
    parametrize collects zero cases rather than crashing the test module.
    A separate test asserts the SoT is intact."""
    try:
        return json.loads(COUNTRIES_JSON.read_text())["slugs"]
    except Exception:
        return []


_COHORT_SLUGS = _try_load_slugs()


def _stripped_source(path: Path) -> str:
    """Return the file source with pure-comment lines removed.

    A pure-comment line is one whose first non-whitespace character is '#'.
    Inline-trailing comments (`code  # comment`) are retained because the
    code portion is still live. The retire-with-tombstone pattern per
    Convention #56 places the retired line inside a comment block, so
    stripping pure-comment lines correctly ignores the tombstone.
    """
    live_lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        live_lines.append(line)
    return "\n".join(live_lines)


# ═══════════════════════════════════════════════════════════
#  1 — STATIC ANALYSIS: score-country.py retirement
# ═══════════════════════════════════════════════════════════

class TestScoreCountryTombstone:
    """The synthetic-population generator on line ~195 of
    scripts/score-country.py MUST be retired per Task #451 Step 5b.

    Tombstone form (comment-only) is legal; live call is not.
    """

    def test_score_country_py_exists(self):
        assert SCORE_COUNTRY_PATH.exists(), (
            f"score-country.py absent at {SCORE_COUNTRY_PATH} — "
            f"cannot verify Task #451 retirement without the file."
        )

    def test_no_live_synthetic_population_generator(self):
        """The banned pattern MUST NOT appear in any live (non-commented) line.

        If this test fires, someone re-introduced a
        `det_var(seed+'pop', ...)` synthetic call — either by uncommenting
        the Task #451 tombstone or by adding a new one elsewhere.
        Convention #56 requires real GHSL enrichment via the utility at
        scripts/pipeline/enrichment/catchment_population.py.
        """
        live_src = _stripped_source(SCORE_COUNTRY_PATH)
        matches = BANNED_SYNTHETIC_PATTERN.findall(live_src)
        assert not matches, (
            "Live synthetic population generator detected in "
            "scripts/score-country.py — Convention #56 violation. "
            "Task #451 retired this on 23 Jul 2026; any live call "
            "regenerates fabricated demographic values. Route through "
            "scripts/pipeline/enrichment/catchment_population.py instead."
        )


# ═══════════════════════════════════════════════════════════
#  2 — UTILITY CONSTANT LOCK
# ═══════════════════════════════════════════════════════════

class TestUtilityConstantLock:
    """The catchment enrichment utility's key constants are pinned.
    Any drift is a Task #451 methodology-version event."""

    def test_utility_module_importable(self):
        from pipeline.enrichment import catchment_population as cp  # noqa: F401

    def test_default_radius_5km(self):
        from pipeline.enrichment import catchment_population as cp
        assert cp.DEFAULT_RADIUS_KM == 5.0, (
            f"Radius drift: got {cp.DEFAULT_RADIUS_KM}, expected 5.0. "
            f"5 km is the v4.2 catchment methodology anchor; changes "
            f"require operator sign-off + methodology version bump."
        )

    def test_audit_trail_value_locked(self):
        from pipeline.enrichment import catchment_population as cp
        assert cp.AUDIT_TRAIL_VALUE == AUDIT_TRAIL_VALUE, (
            f"Audit-trail marker drift: expected '{AUDIT_TRAIL_VALUE}', "
            f"got '{cp.AUDIT_TRAIL_VALUE}'. Marker change breaks the "
            f"provenance chain for every enriched substation cohort-wide."
        )

    def test_audit_trail_key_locked(self):
        from pipeline.enrichment import catchment_population as cp
        assert cp.AUDIT_TRAIL_KEY == AUDIT_TRAIL_KEY, (
            f"Audit-trail key drift: expected '{AUDIT_TRAIL_KEY}', "
            f"got '{cp.AUDIT_TRAIL_KEY}'."
        )


# ═══════════════════════════════════════════════════════════
#  3 — COHORT SoT integrity
# ═══════════════════════════════════════════════════════════

class TestCohortSoT:
    """intelligence/countries.json is the 39-country SoT per KB §57.
    A missing / malformed SoT silently zeroes the cohort scan below."""

    def test_countries_json_exists(self):
        assert COUNTRIES_JSON.exists(), (
            f"{COUNTRIES_JSON} absent — KB §57 SoT violation."
        )

    def test_cohort_size(self):
        assert len(_COHORT_SLUGS) == 39, (
            f"Expected 39 cohort slugs, got {len(_COHORT_SLUGS)}. "
            f"Update this assertion in the same commit as any cohort "
            f"expansion (Wave 5+ additions)."
        )


# ═══════════════════════════════════════════════════════════
#  4 — COHORT-WIDE DATA INVARIANTS
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("slug", _COHORT_SLUGS)
def test_catchment_population_provenance_and_values(slug: str):
    """For every sub with non-None socio_economic.population:

      (a) VALUE INVARIANT — int, non-negative, ≤ 1e10
      (b) AUDIT TRAIL — `_catchment_population_source` present + equals
          the Task #451 canonical marker

    Convention #79 ssi-data sharding is handled transparently by
    `read_ssi_data` (loads shard manifest + concatenates virtual
    substations).
    """
    from pipeline.utils.ssi_data_sharding import read_ssi_data

    fp = REPO_ROOT / slug / "ssi-data.json"
    if not fp.exists():
        pytest.skip(f"{slug}/ssi-data.json absent in this checkout")

    data = read_ssi_data(fp)
    subs = data.get("substations", [])
    if not subs:
        pytest.skip(f"{slug}: zero substations (empty cohort or shard load failure)")

    # Handle Wave 4 compact array format (substations as [values] list
    # + `sub_fields` header) transparently — decompact to dicts.
    if subs and isinstance(subs[0], list):
        fields = data.get("sub_fields", [])
        subs = [dict(zip(fields, s)) for s in subs]

    invalid_value = []      # (idx, value)
    missing_marker = []     # idx
    wrong_marker = []       # (idx, marker)

    for i, sub in enumerate(subs):
        se = sub.get("socio_economic") or {}
        pop = se.get("population")
        if pop is None:
            # Convention #56 legitimate None (raster-gap substation).
            continue
        # (a) Value invariant
        if not isinstance(pop, int) or pop < 0 or pop > POPULATION_UPPER_BOUND:
            invalid_value.append((i, pop))
            continue
        # (b) Audit-trail marker
        marker = se.get(AUDIT_TRAIL_KEY)
        if marker is None:
            missing_marker.append(i)
        elif marker != AUDIT_TRAIL_VALUE:
            wrong_marker.append((i, marker))

    assert not invalid_value, (
        f"{slug}: {len(invalid_value)} substations carry INVALID "
        f"socio_economic.population values (non-int / negative / "
        f">1e10). First 5: {invalid_value[:5]}. "
        f"Any value writing must go through the GHSL enrichment "
        f"utility per Convention #56."
    )
    assert not missing_marker, (
        f"{slug}: {len(missing_marker)} substations have non-None "
        f"population but no '{AUDIT_TRAIL_KEY}' marker. First 5 "
        f"indices: {missing_marker[:5]}. Any code path that writes "
        f"socio_economic.population MUST also write the audit-trail "
        f"marker per Task #451."
    )
    assert not wrong_marker, (
        f"{slug}: {len(wrong_marker)} substations carry a WRONG "
        f"audit-trail marker (expected '{AUDIT_TRAIL_VALUE}'). "
        f"First 5: {wrong_marker[:5]}."
    )
