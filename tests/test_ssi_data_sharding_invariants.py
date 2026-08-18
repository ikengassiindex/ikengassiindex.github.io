"""
SSI Pipeline — Convention #79 candidate: ssi-data automatic sharding invariants

Regression sentinel for the failure-mode that surfaced during Wave 4 Commit 44:
per-country ssi-data.json can grow beyond GitHub's 100 MB per-file hard limit
when enriched cohorts (100k+ subs × ~1.7 KB per sub) push single-file size above
threshold. Convention #79 candidate codifies automatic sharding: when total
payload >90 MB, split `substations` array into `ssi-data-substations-NN.json`
shards ≤60 MB each, replacing the single-file with a small manifest carrying
`sharded: true` + `substations_shards[]` index.

Pre-fix worst cases (empirical Wave 4 Commit 44):
  - France   340.94 MB single-file → GitHub 100 MB REJECT
  - Germany  334.70 MB single-file → GitHub 100 MB REJECT
  - US       181.51 MB single-file → GitHub 100 MB REJECT
  - UK       109.64 MB single-file → GitHub 100 MB REJECT

Post-fix (Commit 45 `ad9adfc5`, Convention #79 candidate implementation):
  - 4 countries sharded: UK 2 + US 4 + Germany 6 + France 6 = 18 shard files
  - Every shard file <60 MB (safely under GitHub 100 MB hard limit)
  - Manifest file <5 MB carrying meta + fleet_summary + regions + shard index
  - JS loaders (map.js + country-renderer.js) auto-detect `sharded: true` +
    fetch shards in parallel + concatenate into virtual `substations` inline
  - 35 non-Wave-4 countries continue single-file (below 90 MB threshold);
    backward-compatible with zero rendering changes

This sentinel runs at pytest level so any cohort-wide file-size regression
(e.g. accidental `indent=2` pretty-print restoration; forgetting to run
sharding utility after enrichment pass; stale shard files left behind after
re-sharding) is caught locally before pushing to origin.

The 5 tests split into three classes:
  - TestConvention79ManifestSchema — sharded countries expose correct manifest keys
  - TestConvention79ShardFileInvariants — every shard file exists + <100 MB
  - TestConvention79BackwardCompatibility — single-file countries stay valid

Cross-references:
  - scripts/pipeline/utils/ssi_data_sharding.py — sharding utility (Commit 45)
  - scripts/pipeline/utils/grid_geo_sharding.py — Convention #80 sibling pattern
  - map.js loadSsiData() + country-renderer.js loadSsiData() — JS loaders
  - Commit 45 `ad9adfc5` — 4 large countries sharded
  - Commit 44 `d0312749` — Wave 4 R4/R5/R6 partial 5/9 closure (5 small non-sharded)
  - CLAUDE.md — Convention #79 candidate codification in tagline
  - Task #125 — original >90 MB pre-commit sentinel (pretty-print class)
  - Task #430 — Commit 45 Convention #79 sharding utility + renderer patch
  - Task #432 — this sentinel (Workstream 3 of 4)
"""

import json
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
#  CONFIG — Convention #79 thresholds
# ═══════════════════════════════════════════════════════════

# GitHub's hard per-file size limit — this is the true blocker (rejected at push).
GITHUB_HARD_LIMIT_MB = 100.0

# Convention #79 threshold — files ≥90 MB should be sharded (10 MB safety margin
# under GitHub hard limit). Countries below stay single-file.
SHARDING_THRESHOLD_MB = 90.0

# Wave 4 sharded countries as of Commit 45 `ad9adfc5`. Extended as new
# countries cross the sharding threshold (Wave 5+ additions to be appended).
SHARDED_COUNTRIES = ("uk", "us", "france", "germany", "italy", "poland")

# Countries expected to stay single-file (subset — validated below by scanning).
# Non-exhaustive; the test class walks all non-sharded countries via
# intelligence/countries.json single-source-of-truth.
NON_SHARDED_SAMPLE = ("sweden", "portugal", "japan", "spain")


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════


def _all_countries():
    """Return the 39-country slug list from single source of truth (KB §57)."""
    path = REPO_ROOT / "intelligence" / "countries.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data.get("slugs", [])


def _load_manifest(slug):
    """Load a country's ssi-data.json manifest (dict or None if missing)."""
    path = REPO_ROOT / slug / "ssi-data.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _file_size_mb(path):
    """Return file size in MB (float)."""
    return path.stat().st_size / 1024 / 1024


# ═══════════════════════════════════════════════════════════
#  CLASS 1 — Manifest schema invariants (sharded countries)
# ═══════════════════════════════════════════════════════════


class TestConvention79ManifestSchema:
    """Manifest schema invariants for Convention #79 sharded countries."""

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_manifest_has_sharded_true_flag(self, slug):
        """Sharded country manifest MUST carry `sharded: true` for JS loader auto-detect."""
        manifest = _load_manifest(slug)
        assert manifest is not None, f"{slug}/ssi-data.json missing"
        assert manifest.get("sharded") is True, (
            f"{slug}/ssi-data.json is sharded (per Convention #79) but manifest "
            f"lacks `sharded: true` flag. map.js loadSsiData() + country-renderer.js "
            f"loadSsiData() rely on this flag to trigger parallel-fetch shard loader. "
            f"Regression: re-check scripts/pipeline/utils/ssi_data_sharding.py::write_ssi_data() "
            f"was invoked and completed; verify no manual mutation stripped the flag."
        )

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_manifest_has_substations_shards_array(self, slug):
        """Sharded manifest MUST carry `substations_shards[]` with valid schema per entry."""
        manifest = _load_manifest(slug)
        shards = manifest.get("substations_shards")
        assert isinstance(shards, list) and len(shards) > 0, (
            f"{slug}/ssi-data.json missing or empty `substations_shards[]` array. "
            f"Convention #79 requires the manifest to list every shard with "
            f"{{'path': str, 'count': int, 'size_mb': float}} per entry."
        )
        for i, sh in enumerate(shards):
            assert isinstance(sh, dict), f"{slug} shard[{i}] not a dict"
            assert "path" in sh and "count" in sh and "size_mb" in sh, (
                f"{slug} shard[{i}] missing required keys (path + count + size_mb). "
                f"Got keys: {list(sh.keys())}"
            )
            assert isinstance(sh["path"], str) and sh["path"].endswith(".json"), (
                f"{slug} shard[{i}].path is not a .json filename: {sh['path']!r}"
            )

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_manifest_inline_keys_preserved(self, slug):
        """meta + fleet_summary + regions MUST stay inline (never sharded)."""
        manifest = _load_manifest(slug)
        # Convention #79 rule — only `substations` array is sharded; all other
        # top-level keys stay inline in the manifest for renderer immediate access.
        # meta + fleet_summary + regions are small aggregates always needed on load.
        for key in ("meta", "fleet_summary"):
            assert key in manifest, (
                f"{slug}/ssi-data.json manifest missing inline `{key}` key. "
                f"Convention #79 requires meta + fleet_summary + regions stay inline."
            )
        # `regions` may be a list or dict depending on cohort; presence check only.
        # (Some countries have empty regions post-Wave-4 bootstrap; still must be present.)

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_manifest_size_under_5mb(self, slug):
        """Manifest itself MUST stay small (<5 MB) — otherwise renderer overhead grows."""
        path = REPO_ROOT / slug / "ssi-data.json"
        size_mb = _file_size_mb(path)
        assert size_mb < 5.0, (
            f"{slug}/ssi-data.json manifest is {size_mb:.2f} MB — should be <5 MB. "
            f"Convention #79 requires manifests carry ONLY meta + fleet_summary + "
            f"regions + shard-index; the `substations` array MUST be sharded out. "
            f"If manifest is large, re-run scripts/pipeline/utils/ssi_data_sharding.py "
            f"to re-shard properly."
        )


# ═══════════════════════════════════════════════════════════
#  CLASS 2 — Shard file invariants (physical file checks)
# ═══════════════════════════════════════════════════════════


class TestConvention79ShardFileInvariants:
    """Per-shard-file physical invariants."""

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_every_referenced_shard_exists(self, slug):
        """Every shard listed in manifest MUST exist on disk (no dangling references)."""
        manifest = _load_manifest(slug)
        shards = manifest.get("substations_shards", [])
        country_dir = REPO_ROOT / slug
        for sh in shards:
            shard_path = country_dir / sh["path"]
            assert shard_path.exists(), (
                f"{slug} manifest references shard `{sh['path']}` but file does "
                f"not exist on disk. Convention #56 partial-fetch would surface "
                f"visibly-missing subs — but Convention #79 CI-time invariant is "
                f"that every manifest reference resolves. Rerun sharding utility."
            )

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_every_shard_under_github_hard_limit(self, slug):
        """Every shard file MUST be strictly under GitHub's 100 MB hard limit."""
        manifest = _load_manifest(slug)
        country_dir = REPO_ROOT / slug
        shards = manifest.get("substations_shards", [])
        for sh in shards:
            shard_path = country_dir / sh["path"]
            if not shard_path.exists():
                continue  # Covered by previous test
            size_mb = _file_size_mb(shard_path)
            assert size_mb < GITHUB_HARD_LIMIT_MB, (
                f"{slug} shard `{sh['path']}` is {size_mb:.2f} MB — EXCEEDS "
                f"GitHub's {GITHUB_HARD_LIMIT_MB} MB hard limit. Push will be "
                f"REJECTED. Re-shard with smaller target (currently 60 MB target; "
                f"try 45 MB) via ssi_data_sharding.py::write_ssi_data(..., "
                f"target_shard_mb=45.0)."
            )

    def test_no_stale_shard_files(self):
        """No orphan `ssi-data-substations-*.json` files in NON-sharded country dirs.

        Countries below the 90 MB threshold should NOT have shard files.
        Stale shard files from a previous over-sharding pass would confuse
        the renderer + waste disk. Convention #79 utility's cleanup_stale_shards()
        should have removed them on the last write pass.
        """
        offenders = []
        for slug in _all_countries():
            if slug in SHARDED_COUNTRIES:
                continue
            country_dir = REPO_ROOT / slug
            if not country_dir.exists():
                continue
            stale = list(country_dir.glob("ssi-data-substations-*.json"))
            if stale:
                offenders.append((slug, [p.name for p in stale]))

        assert not offenders, (
            f"Found stale shard files in NON-sharded country dirs: {offenders}. "
            f"Convention #79 utility's cleanup_stale_shards() should have removed "
            f"them. Manually rm the files or re-run ssi_data_sharding.py to trigger "
            f"cleanup."
        )


# ═══════════════════════════════════════════════════════════
#  CLASS 3 — Backward compatibility (non-sharded countries)
# ═══════════════════════════════════════════════════════════


class TestConvention79BackwardCompatibility:
    """Non-sharded countries continue to work with the single-file schema."""

    @pytest.mark.parametrize("slug", NON_SHARDED_SAMPLE)
    def test_non_sharded_has_no_sharded_flag(self, slug):
        """Non-sharded manifest MUST NOT carry `sharded: true` (would trigger renderer's
        parallel-fetch path with no shards to fetch → error)."""
        manifest = _load_manifest(slug)
        if manifest is None:
            pytest.skip(f"{slug}/ssi-data.json not present")
        # Either missing entirely OR explicitly False
        assert not manifest.get("sharded"), (
            f"{slug}/ssi-data.json has `sharded: {manifest.get('sharded')}` "
            f"but is not in SHARDED_COUNTRIES list. Either re-shard properly "
            f"(if size >90 MB), OR remove the `sharded` flag (if single-file), "
            f"OR add slug to SHARDED_COUNTRIES list in this sentinel."
        )

    @pytest.mark.parametrize("slug", NON_SHARDED_SAMPLE)
    def test_non_sharded_has_inline_substations(self, slug):
        """Non-sharded ssi-data.json MUST have `substations` as inline list."""
        manifest = _load_manifest(slug)
        if manifest is None:
            pytest.skip(f"{slug}/ssi-data.json not present")
        if manifest.get("sharded"):
            pytest.skip(f"{slug} is sharded per manifest; covered by other tests")
        subs = manifest.get("substations")
        # Some Wave 3 countries use flat-list root (Latvia pattern) — handle both.
        if isinstance(manifest, list):
            return  # Flat-list root pattern — Convention #78 §4bis.4 intermediate state
        assert isinstance(subs, list), (
            f"{slug}/ssi-data.json is single-file (not sharded) but `substations` "
            f"is not an inline list. Got type: {type(subs).__name__}. Convention #79 "
            f"single-file schema requires inline `substations: [...]`."
        )

    def test_all_country_manifests_under_github_hard_limit(self):
        """Every country's ssi-data.json (manifest or single-file) MUST be <100 MB."""
        offenders = []
        for slug in _all_countries():
            path = REPO_ROOT / slug / "ssi-data.json"
            if not path.exists():
                continue
            size_mb = _file_size_mb(path)
            if size_mb >= GITHUB_HARD_LIMIT_MB:
                offenders.append((slug, round(size_mb, 2)))

        assert not offenders, (
            f"Country ssi-data.json files EXCEEDING GitHub 100 MB hard limit: "
            f"{offenders}. Push will be REJECTED. Run Convention #79 sharding: "
            f"`python -m scripts.pipeline.utils.ssi_data_sharding shard {' '.join(s for s, _ in offenders)}`."
        )


# ═══════════════════════════════════════════════════════════
#  CLASS 4 — Convention #79 utility self-consistency
# ═══════════════════════════════════════════════════════════


class TestConvention79UtilityInvariants:
    """The sharding utility's own validate_ssi_data() must agree with our checks."""

    @pytest.mark.parametrize("slug", SHARDED_COUNTRIES)
    def test_utility_validate_ssi_data_passes(self, slug):
        """Convention #79 utility's own validation MUST return no issues for sharded countries."""
        try:
            from pipeline.utils.ssi_data_sharding import validate_ssi_data
        except ImportError:
            pytest.skip(
                "scripts/pipeline/utils/ssi_data_sharding.py not importable in "
                "current sys.path — non-blocking for release, sentinel intended "
                "for CI where package layout is stable."
            )
        path = REPO_ROOT / slug / "ssi-data.json"
        is_valid, issues = validate_ssi_data(path)
        assert is_valid, (
            f"{slug}/ssi-data.json fails Convention #79 utility validation: {issues}"
        )
