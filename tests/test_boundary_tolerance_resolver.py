"""
Sentinel — boundary-tolerance resolution (M-026).

WHAT WENT WRONG
───────────────
Each of the 30 ingestion modules carried its own inline read of
``cross_border_tolerances.json``. The reads drifted into two dialects:

    tol_cfg["per_country"][slug]["tolerance_km"]           # 22 modules
    tol_cfg["countries"][slug]["boundary_tolerance_km"]    #  8 modules

The file only ever had the second shape, so 22 modules resolved to ``{}`` and
silently used a hardcoded literal. For 21 of them the literal coincided with
the configured value (or nothing was configured) and the fault was invisible.
Greece was configured at 5.0 km — chosen for the Aegean archipelago — and ran
at 0.1 km, 50x too tight, dropping 17 real island and gulf substations. The
audit tool read the config correctly and reported Greece CLEAN, so audit and
ingestion disagreed about the same file while both looked healthy.

WHAT THIS SENTINEL PINS
───────────────────────
1.  There is exactly ONE reader. No module may parse the config itself.
2.  The legacy ``per_country`` dialect never comes back.
3.  Resolution order is config → module literal → cohort default → floor,
    and in particular the module literal outranks the cohort default. Getting
    that backwards silently demoted Finland (literal 5.0 km, no config entry)
    to 0.1 km during the very refactor that fixed Greece.
4.  Greece specifically resolves to its configured 5.0 km.

Assertions here are about ARITHMETIC OUTCOMES, not about metadata being
present. Every finding in this workstream that a green suite failed to catch
was a metadata-presence assertion.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.pipeline.utils.tolerance import (  # noqa: E402
    TOLERANCE_CONFIG_PATH,
    audit_all,
    normalise_slug,
    resolve,
)

INGESTION_DIR = REPO_ROOT / "scripts" / "pipeline" / "ingestion"

#: The module literals each ingestion module passes as `module_fallback`.
#: Kept here so a change to any of them is a visible diff in a test, not a
#: silent change of behaviour buried in one of 30 country modules.
MODULE_FALLBACKS = {
    "australia": 0.1, "austria": 0.1, "belgium": 0.1, "chile": 0.1,
    "colombia": 0.1, "costa-rica": 0.1, "czechia": 0.1, "denmark": 5.0,
    "estonia": 0.1, "finland": 5.0, "greece": 0.1, "greenland": 5.0,
    "hungary": 0.1, "iceland": 5.0, "ireland": 1.0, "israel": 0.1,
    "korea": 5.0, "latvia": 0.1, "lithuania": 0.1, "luxembourg": 0.1,
    "mexico": 0.1, "netherlands": 0.1, "new-zealand": 5.0, "norway": 5.0,
    "poland": 0.1, "slovakia": 0.1, "slovenia": 0.1, "switzerland": 0.5,
    "turkey": 5.0, "uk": 3.0,
}

#: The effective tolerance every country must resolve to. Measured against the
#: pre-refactor behaviour: identical everywhere except Greece, which is the
#: whole point of the change.
EXPECTED_EFFECTIVE_KM = dict(MODULE_FALLBACKS, greece=5.0)


class TestSingleReader:
    """Nothing but the resolver may read the tolerance config."""

    def test_no_module_parses_the_config_itself(self):
        offenders = []
        for py in INGESTION_DIR.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            src = py.read_text(encoding="utf-8", errors="replace")
            if "cross_border_tolerances.json" not in src:
                continue
            # A bare Path constant or a comment is fine; parsing is not.
            for line in src.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if "cross_border_tolerances.json" in line and (
                    "json.load" in line or "read_text" in line
                ):
                    offenders.append(f"{py.relative_to(REPO_ROOT)}: {stripped}")
        assert not offenders, (
            "These files parse cross_border_tolerances.json directly instead "
            "of calling scripts.pipeline.utils.tolerance. Duplicated readers "
            "are what caused M-026:\n  " + "\n  ".join(offenders)
        )

    def test_legacy_per_country_dialect_is_gone(self):
        offenders = []
        for py in (REPO_ROOT / "scripts").rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            src = py.read_text(encoding="utf-8", errors="replace")
            if 'get("per_country"' in src or "get('per_country'" in src:
                offenders.append(str(py.relative_to(REPO_ROOT)))
        assert not offenders, (
            "The legacy 'per_country' dialect has reappeared in: "
            f"{offenders}. The config key is 'countries' with "
            "'boundary_tolerance_km'."
        )

    def test_config_has_no_per_country_key(self):
        cfg = json.loads(TOLERANCE_CONFIG_PATH.read_text(encoding="utf-8"))
        assert "per_country" not in cfg, (
            "cross_border_tolerances.json grew a 'per_country' key. Nothing "
            "reads it; a tolerance placed there would be silently ignored."
        )
        assert "countries" in cfg, "config lost its 'countries' key"
        assert isinstance(cfg.get("_default_tolerance_km"), (int, float))


class TestResolutionOrder:
    """Order matters, and the Finland case proves which order is right."""

    def test_config_entry_wins_over_module_literal(self, tmp_path):
        cfg = tmp_path / "t.json"
        cfg.write_text(json.dumps(
            {"_default_tolerance_km": 0.1,
             "countries": {"greece": {"boundary_tolerance_km": 5.0}}}
        ))
        r = resolve("greece", module_fallback=0.1, config_path=cfg)
        assert r.value_km == 5.0
        assert r.source == "config:countries"

    def test_module_literal_outranks_cohort_default(self, tmp_path):
        """The Finland case.

        Finland has no entry in the config and a 5.0 km module literal. If the
        cohort default (0.1) outranked the literal, Finland would silently drop
        50x. It must not.
        """
        cfg = tmp_path / "t.json"
        cfg.write_text(json.dumps({"_default_tolerance_km": 0.1, "countries": {}}))
        r = resolve("finland", module_fallback=5.0, config_path=cfg)
        assert r.value_km == 5.0, (
            "an undeclared per-country literal was demoted to the cohort "
            "default — this is the Finland regression"
        )
        assert r.source == "module_fallback"

    def test_cohort_default_applies_when_no_literal_given(self, tmp_path):
        cfg = tmp_path / "t.json"
        cfg.write_text(json.dumps({"_default_tolerance_km": 0.1, "countries": {}}))
        r = resolve("nowhere", config_path=cfg)
        assert r.value_km == 0.1
        assert r.source == "config:default"

    def test_missing_config_degrades_visibly_to_the_literal(self, tmp_path):
        r = resolve("greece", module_fallback=0.1, config_path=tmp_path / "absent.json")
        assert r.value_km == 0.1
        assert r.source == "module_fallback"

    def test_package_names_map_to_public_slugs(self):
        assert normalise_slug("new_zealand") == "new-zealand"
        assert normalise_slug("costa_rica") == "costa-rica"
        assert normalise_slug("greece") == "greece"


class TestEffectiveTolerances:
    """The arithmetic outcome for every country, pinned."""

    @pytest.mark.parametrize("slug", sorted(EXPECTED_EFFECTIVE_KM))
    def test_effective_tolerance(self, slug):
        expected = EXPECTED_EFFECTIVE_KM[slug]
        actual = resolve(slug, module_fallback=MODULE_FALLBACKS[slug]).value_km
        assert actual == pytest.approx(expected), (
            f"{slug} resolves to {actual} km, expected {expected} km"
        )

    def test_greece_is_five_km(self):
        """The one country whose effective tolerance the M-026 fix changes."""
        r = resolve("greece", module_fallback=0.1)
        assert r.value_km == 5.0, (
            "Greece is back on 0.1 km. Its 5.0 km tolerance exists for the "
            "Aegean archipelago; at 0.1 km the ingestion drops real island "
            "substations."
        )
        assert r.source == "config:countries"

    def test_only_greece_changed(self):
        """No other country's effective tolerance moved during the refactor."""
        pre_refactor = dict(MODULE_FALLBACKS)  # what each module used before
        moved = {
            slug: (pre_refactor[slug], resolve(slug, module_fallback=fb).value_km)
            for slug, fb in MODULE_FALLBACKS.items()
            if resolve(slug, module_fallback=fb).value_km != pre_refactor[slug]
        }
        assert set(moved) == {"greece"}, (
            f"expected only Greece to move, got {moved}"
        )


class TestAuditability:
    """The resolver can report itself, without importing 30 modules."""

    def test_audit_all_covers_every_configured_country(self):
        cfg = json.loads(TOLERANCE_CONFIG_PATH.read_text(encoding="utf-8"))
        report = audit_all()
        assert set(report) == set(cfg["countries"])
        for slug, res in report.items():
            assert res.source == "config:countries"
            assert res.value_km > 0

    def test_every_configured_country_carries_a_rationale(self):
        """Convention: a tolerance override is a methodology claim, so it is
        declared with its reasoning. An unexplained override is unauditable."""
        cfg = json.loads(TOLERANCE_CONFIG_PATH.read_text(encoding="utf-8"))
        missing = [
            slug for slug, entry in cfg["countries"].items()
            if not str(entry.get("rationale", "")).strip()
        ]
        assert not missing, f"tolerance overrides with no rationale: {missing}"
