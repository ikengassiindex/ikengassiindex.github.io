"""
SSI Pipeline — Validator Tests (Phase 1 PR-5)

12 tests covering the new validate_schema.py module:

- Tests 1-3: schema-shape pins ($id, accepts new fields, rejects missing R_median)
- Tests 4-5: new modifier range gate (above + below range)
- Test 6: new classification ↔ R_median band invariant
- Test 7: new regional-consistency gate
- Tests 8-9: _SLUG_TO_ISO2 SoT coverage (39 entries; korea→KR)
- Test 10: validate_schema is importable as a Python module
- Test 11: MIN_FLEET single-source-of-truth
- Test 12: pipeline Phase 2b passes Italy via direct import

Cross-reference: PHASE_1_IMPLEMENTATION_PLAN.md PR-5 §"Test criteria (the 12 PR-5 tests)"
                 AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md F-L4-2 closure
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts/ to sys.path so we can import validate_schema as a module
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ═══════════════════════════════════════════════════════════
#  SCHEMA SHAPE (Tests 1-3)
# ═══════════════════════════════════════════════════════════

class TestSchemaShape:
    """Validate the JSON Schema file itself."""

    @pytest.fixture
    def schema(self):
        return json.loads((REPO_ROOT / "schemas/ssi-data.schema.json").read_text())

    def test_1_schema_id_is_v4_0_2_pinned(self, schema):
        """Schema $id must include the v4.0.2 path segment (PR-5 versioning)."""
        expected = "https://ikengassiindex.github.io/schemas/ssi-data/v4.0.2.json"
        assert schema["$id"] == expected, (
            f"Schema $id is {schema['$id']!r}, expected {expected!r}. "
            f"PR-5 pinned the v4.0.2 path segment so the schema URL itself "
            f"declares which methodology version it validates."
        )

    def test_2_schema_declares_new_pr3_provenance_fields(self, schema):
        """Schema must declare mult_product, add_sum, modifier_impacts in substation properties."""
        sub_props = schema["$defs"]["substation"]["properties"]
        for field in ("mult_product", "add_sum", "modifier_impacts"):
            assert field in sub_props, (
                f"Substation schema missing PR-3 field {field!r}. "
                f"Renderers + the v4.2 W-axis gate consume this for the "
                f"modifier-breakdown widget."
            )
        # mult_product is bounded number
        assert sub_props["mult_product"]["type"] == "number"
        # modifier_impacts is a dict with number values
        assert sub_props["modifier_impacts"]["type"] == "object"
        assert sub_props["modifier_impacts"]["additionalProperties"]["type"] == "number"

    def test_3_schema_keeps_r_median_as_required(self, schema):
        """R_median MUST remain in substation.required."""
        required = schema["$defs"]["substation"]["required"]
        assert "R_median" in required, (
            "R_median dropped from substation.required — would silently "
            "allow ssi-data.json files with empty score fields."
        )
        # The other 3 core fields stay required too
        for f in ("classification", "components", "modifiers"):
            assert f in required, f"{f} dropped from substation.required"


# ═══════════════════════════════════════════════════════════
#  NEW SEMANTIC GATES (Tests 4-7)
# ═══════════════════════════════════════════════════════════

class TestModifierRangeGate:
    """check_modifier_ranges catches modifier values outside registry bounds."""

    def test_4_modifier_above_range_is_caught(self):
        """R6_seismic=1.30 (registry max 1.25, tolerance 2% → 1.275) must fail."""
        from validate_schema import check_modifier_ranges
        # Synthesize a fleet where every substation has R6_seismic=1.30
        # (well above 1.25 × 1.02 = 1.275 tolerance ceiling)
        substations = [
            {"substation_id": f"TEST_{i:03d}", "modifiers": {"R6_seismic": 1.30}}
            for i in range(100)
        ]
        errors, warnings = check_modifier_ranges(substations)
        # 100% violation should produce an error (>1% threshold)
        assert any("R6_seismic" in e for e in errors), (
            f"R6_seismic=1.30 not caught by range check. errors={errors}, warnings={warnings}"
        )

    def test_5_modifier_below_range_is_caught(self):
        """R7_cyber=0.90 (registry min 0.99, tolerance 2% → 0.9702) must fail."""
        from validate_schema import check_modifier_ranges
        substations = [
            {"substation_id": f"TEST_{i:03d}", "modifiers": {"R7_cyber": 0.90}}
            for i in range(100)
        ]
        errors, warnings = check_modifier_ranges(substations)
        assert any("R7_cyber" in e for e in errors), (
            f"R7_cyber=0.90 not caught by range check. errors={errors}, warnings={warnings}"
        )


class TestClassificationBandGate:
    """Classification MUST match R_median band; mismatch ≥2% is an error."""

    def test_6_classification_mismatch_above_threshold_is_error(self, tmp_path):
        """40 substations with R_median=0.6 classified 'Low' (expected 'High') → error."""
        import json as _json
        # Synthesize a fleet of 40 mismatched substations (every one mislabelled)
        substations = []
        for i in range(40):
            substations.append({
                "substation_id": f"TEST_{i:03d}", "lat": 41.9, "lon": 12.5,
                "R_median": 0.6,                # → expected band: High
                "classification": "Low",         # mismatched
                "components": {"C": 0.6, "V": 0.6, "I": 0.6, "E": 0.6, "S": 0.6, "T": 0.6},
                "modifiers": {
                    "R3_C_mult": 1.05, "R4_F_topo": 1.10, "R6_restoration": 0.98,
                    "R6_seismic": 1.08, "R7_cyber": 1.01,
                },
            })
        data = {
            "meta": {"version": "4.0.2", "country": "test"},
            "fleet_summary": {"total": 40, "bands": {"Low": 0, "Medium": 0, "High": 40, "Critical": 0}},
            "regions": [{"code": "R1"}, {"code": "R2"}],
            "substations": substations,
        }
        fp = tmp_path / "ssi-data.json"
        fp.write_text(_json.dumps(data))

        from validate_schema import validate_file
        errors, warnings = validate_file(str(fp))
        # 100% mismatch → above 2% threshold → must be ERROR
        assert any("CLASSIFICATION-BAND" in e for e in errors), (
            f"Classification-band gate did not fire. errors={errors}"
        )


class TestRegionalConsistencyGate:
    """check_regional_consistency catches mismatched substation→region mapping."""

    def test_7_orphan_regions_are_caught(self):
        """When >5% substations carry a region code absent from regions rollup → error."""
        from validate_schema import check_regional_consistency
        # 100 substations: 90 point at region 'R1', 10 point at orphan 'R_ORPHAN'
        subs = [{"region": "R1"} for _ in range(90)] + \
               [{"region": "R_ORPHAN"} for _ in range(10)]
        data = {
            "regions": [{"code": "R1", "name": "Region 1"}],   # R_ORPHAN missing
            "substations": subs,
        }
        errors = check_regional_consistency(data)
        assert any("REGIONAL-CONSISTENCY" in e for e in errors), (
            f"Orphan region not caught. errors={errors}"
        )
        # The error message must name the orphan
        assert any("R_ORPHAN" in e for e in errors), (
            f"Orphan region code R_ORPHAN not named in error. errors={errors}"
        )


# ═══════════════════════════════════════════════════════════
#  COUNTRY COVERAGE (Tests 8-9)
# ═══════════════════════════════════════════════════════════

class TestCountryCoverage:
    """_SLUG_TO_ISO2 must cover all 39 SoT countries (F-L4-2 closure)."""

    def test_8_slug_to_iso2_has_39_entries(self):
        """All 39 SoT countries must be in _SLUG_TO_ISO2."""
        from validate_schema import _SLUG_TO_ISO2
        # Cross-check against the canonical SoT
        sot = json.loads((REPO_ROOT / "intelligence/countries.json").read_text())
        sot_slugs = set(sot["slugs"])
        slug_map_keys = set(_SLUG_TO_ISO2)
        missing = sot_slugs - slug_map_keys
        assert not missing, (
            f"_SLUG_TO_ISO2 missing {len(missing)} SoT countries: {sorted(missing)}. "
            f"These would silently bypass fleet-floor protection (F-L4-2)."
        )
        # The map can have at most the SoT count (no rogue extras)
        extras = slug_map_keys - sot_slugs
        assert not extras, (
            f"_SLUG_TO_ISO2 has {len(extras)} entries not in SoT: {sorted(extras)}"
        )

    def test_9_korea_maps_to_kr(self):
        """Korea: slug='korea' → ISO2='KR' (PR-5 closure for F-L4-2 cohort)."""
        from validate_schema import _SLUG_TO_ISO2
        assert _SLUG_TO_ISO2.get("korea") == "KR", (
            f"_SLUG_TO_ISO2['korea'] is {_SLUG_TO_ISO2.get('korea')!r}, expected 'KR'. "
            f"Pre-PR-5 Korea was silently bypassed; this pin documents the F-L4-2 closure."
        )


# ═══════════════════════════════════════════════════════════
#  IMPORTABILITY + SINGLE-SOURCE (Tests 10-11)
# ═══════════════════════════════════════════════════════════

class TestImportableModule:
    """validate_schema must be a proper Python module (post-rename from hyphen name)."""

    def test_10_validate_schema_is_importable(self):
        """import validate_schema works WITHOUT subprocess."""
        import validate_schema
        # All canonical names exported
        for name in ("validate_file", "check_fleet_floor", "check_modifier_ranges",
                     "check_regional_consistency", "MIN_FLEET", "_SLUG_TO_ISO2",
                     "COUNTRY_BOUNDS", "_MODIFIER_RANGES"):
            assert hasattr(validate_schema, name), (
                f"validate_schema missing public symbol {name!r}"
            )
        # validate_file is callable
        assert callable(validate_schema.validate_file)

    def test_11_min_fleet_single_source(self):
        """from validate_schema import MIN_FLEET works AND score-country.py uses it."""
        from validate_schema import MIN_FLEET as MF_canonical
        # Read score-country.py source and check it imports MIN_FLEET (not inlines it)
        sc = (SCRIPTS_DIR / "score-country.py").read_text()
        assert "from validate_schema import MIN_FLEET" in sc, (
            "score-country.py does not import MIN_FLEET from validate_schema — "
            "would carry an inlined copy that drifts (F-L4-2 + Session 32 pattern)."
        )
        # The inlined dict at the old location MUST be gone
        # (sanity: the old comment about "Inlined here because validate-schema.py
        # has a hyphen" should not appear in modern source)
        assert "Inlined here because" not in sc, (
            "score-country.py still has the inlined MIN_FLEET comment — incomplete migration"
        )


# ═══════════════════════════════════════════════════════════
#  PIPELINE PHASE 2b SMOKE (Test 12)
# ═══════════════════════════════════════════════════════════

class TestPipelinePhase2b:
    """Phase 2b validates Italy via direct Python import (PR-5 retired subprocess)."""

    def test_12_pipeline_phase_2b_passes_italy(self):
        """validate_file('italy/ssi-data.json') returns 0 errors (fleet-floor + new gates)."""
        italy_json = REPO_ROOT / "italy" / "ssi-data.json"
        if not italy_json.exists():
            pytest.skip("italy/ssi-data.json not available in this checkout")
        from validate_schema import validate_file
        errors, warnings = validate_file(str(italy_json))
        # Italy passes all gates (it's the canonical reference cohort)
        assert errors == [], (
            f"Italy ssi-data.json failed PR-5 validator gates: {errors}. "
            f"Italy is the canonical reference — failure here means PR-5 broke the gate logic."
        )
        # The PR-3 provenance warning is expected (legacy data, refresh queued
        # for PR-7). So are the pre-L3 notices: since M-046/M-053, Italy's fleet
        # is entirely Unclassified pending the cohort rescore, and CHECK 7 /
        # CHECK 8 report that state deliberately — validate_schema.py emits them
        # as the Convention #56 disclosure, not as faults ("R_median=None
        # (pre-L3 state per Convention #56)"). Treating the validator's own
        # honest degradation notice as an unexpected warning would make the
        # visibly-honest path the failing one, which is backwards.
        #
        # Note this test's real assertion is `errors == []`, and that passes.
        # Only the warning allowlist was stale.
        EXPECTED = ("PR-3 PROVENANCE", "pre-L3 state", "all pre-L3 state")
        non_provenance = [w for w in warnings
                          if not any(tag in w for tag in EXPECTED)]
        assert non_provenance == [], (
            f"Italy emits unexpected warnings beyond the documented PR-3 provenance gap: "
            f"{non_provenance}"
        )

    def test_pipeline_run_py_uses_direct_import(self):
        """scripts/pipeline/run.py uses `from validate_schema import validate_file`."""
        run_py = (SCRIPTS_DIR / "pipeline" / "run.py").read_text()
        assert "from validate_schema import validate_file" in run_py, (
            "scripts/pipeline/run.py is still subprocess-calling validate-schema.py. "
            "PR-5 retired this path for the ~3.1 s startup-cost saved across the "
            "39-country batch."
        )
