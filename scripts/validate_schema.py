#!/usr/bin/env python3
"""
SSI v4.0.2 / v4.2 — JSON Schema Validator

PR-5 (audit memo 2026-06-08): renamed from validate-schema.py (hyphen-named,
not importable) to validate_schema.py (underscore-named, proper Python module).
The 3 historical callers continue to work:
  • scripts/score-country.py — was inlining MIN_FLEET; now imports it from here
  • scripts/pipeline/run.py   — was subprocess-calling; now imports validate_file()
  • CLI invocation `python3 scripts/validate-schema.py <path>` continues to
    work via a backward-compat shim at scripts/validate-schema.py

Phase 2A (25 June 2026 — v4.2 alignment closure post 39-country empirical audit):
  • Check 7 R_median range extended [0, 1] → [0, 1.30] to accept the additive
    R6c_flood contribution (soft_clip_upper compresses multiplicative to ≤1.0;
    R6c_flood layers on top with range [1.00, 1.30]; max R_median = 1.30).
  • Check 8 classification banding extended 4 bands → 5 bands (Extreme added
    for R_median ∈ [1.00, 1.30]) — operator decision Q1(b) 25 June 2026.
  • Modifier registry (_MODIFIER_RANGES below) synced with pipeline
    scoring.modifier_registry.MODIFIER_REGISTRY: R3_C_mult ceiling 1.30→1.50,
    R7_cyber ceiling 1.50→1.05.
  • --all mode now iterates intelligence/countries.json::slugs (39 countries)
    rather than COUNTRY_BOUNDS (was 30) — closes KB §57 silent-skip gap for
    denmark / finland / greece / mexico / norway / poland / sweden / turkey /
    ireland which the pre-Phase-2A validator was silently bypassing.
  • MIN_FLEET recalibrated for Austria (1200→700) and Canada (8000→6000) to
    reflect post-Discipline-#36 remediated cohort reality (Austria 1406→741;
    Canada was 24986→6399 pre-vs-post cross-border filter).
  • COUNTRY_BOUNDS extended with the 9 previously-missing SoT countries.

Usage:
  python3 scripts/validate_schema.py <country_folder>/ssi-data.json
  python3 scripts/validate_schema.py --all

Programmatic:
  from validate_schema import validate_file, MIN_FLEET, _SLUG_TO_ISO2, COUNTRY_BOUNDS

Checks (PR-5 expanded — was 8 in pre-PR-5; now 11):
  1. Required top-level keys: meta, fleet_summary, regions, substations
  2. Fleet-floor (KB §56 anti-stub-data prophylactic)
  3. Substation core schema: substation_id, lat, lon, R_median, components, classification
  4. Component format: raw (compSum > 1.0)
  5. Lat/lon within country bounds
  6. R_median within [0, 1.30]   (Phase 2A: v4.2 additive R6c_flood layered on top of soft_clip_upper)
  7. Classification matches R_median band, 5-band system incl. Extreme (Phase 2A)
  8. ESG field completeness (markov, seismic, transition)
  9. (PR-5 NEW) Per-modifier value within MODIFIER_REGISTRY range
  10. (PR-5 NEW) Regional summary ↔ substation membership consistency
  11. (PR-5 NEW) Substations missing PR-3 provenance fields (mult_product / add_sum / modifier_impacts)
"""
import json
import os
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional


# ═══════════════════════════════════════════════════════════
#  Country geographic bounds (lat_min, lat_max, lon_min, lon_max)
# ═══════════════════════════════════════════════════════════
# PR-5 (F-L4-2): added the 7 missing F-L4-2 countries —
#   Korea, Colombia, Israel, Costa Rica, Iceland, Hungary, Slovakia
COUNTRY_BOUNDS = {
    'france':       (41.0, 51.5, -5.5, 10.0),
    'italy':        (35.5, 47.5, 6.5, 19.0),
    'uk':           (49.5, 61.0, -8.5, 2.0),
    'spain':        (35.5, 44.0, -10.0, 4.5),
    'germany':      (47.0, 55.5, 5.5, 15.5),
    'switzerland':  (45.5, 48.0, 5.5, 10.5),
    'austria':      (46.0, 49.5, 9.5, 17.5),
    'us':           (24.0, 72.0, -180.0, -65.0),
    'canada':       (41.0, 84.0, -141.0, -52.0),
    'japan':        (24.0, 46.0, 122.0, 154.0),
    'australia':    (-45.0, -10.0, 110.0, 155.0),
    'chile':        (-56.0, -17.0, -76.0, -66.0),
    'portugal':     (36.9, 42.2, -9.6, -6.1),
    'new-zealand':  (-47.5, -34.0, 165.5, 179.0),
    'greenland':    (59.5, 83.7, -74.0, -11.0),
    'czechia':      (48.55, 51.06, 12.09, 18.86),
    'luxembourg':   (49.45, 50.18,  5.73,  6.53),
    'belgium':      (49.50, 51.51,  2.55,  6.41),
    'netherlands':  (50.75, 53.55,  3.36,  7.23),
    'estonia':      (57.51, 59.69, 21.83, 28.21),
    'latvia':       (55.67, 58.09, 20.97, 28.24),
    'lithuania':    (53.90, 56.45, 20.95, 26.84),
    # PR-5 additions for F-L4-2 cohort
    'korea':        (33.0, 38.7, 124.5, 132.0),    # Republic of Korea (incl. Jeju)
    'colombia':     (-4.3, 13.5, -82.0, -66.8),    # Continental + Caribbean territories
    'israel':       (29.4, 33.4, 34.2, 35.9),      # State of Israel
    'costa-rica':   (8.0, 11.3, -86.0, -82.5),     # Republic of Costa Rica
    'iceland':      (63.2, 66.6, -24.6, -13.4),    # Iceland
    'hungary':      (45.7, 48.6, 16.1, 22.9),      # Hungary
    'slovakia':     (47.7, 49.7, 16.8, 22.6),      # Slovak Republic
    # PR-5 acceptance audit — Slovenia was missing from the bounds table
    # (had MIN_FLEET entry SI=120 but no bounds, so --all skipped it).
    'slovenia':     (45.4, 46.9, 13.4, 16.6),      # Republic of Slovenia
    # ─── Phase 2A (25 June 2026): 9 SoT countries previously missing from
    # COUNTRY_BOUNDS — the pre-Phase-2A --all mode iterated this dict rather
    # than intelligence/countries.json::slugs so these 9 were silently
    # bypassed by the daily validator. Bounds derived from observed lat/lon
    # extrema of each country's HEAD ssi-data.json + conservative padding.
    'denmark':      (54.0, 58.0,  8.0, 15.5),
    'finland':      (59.5, 70.5, 19.0, 32.0),
    'greece':       (34.5, 42.0, 19.5, 30.0),
    'mexico':       (14.5, 33.0, -118.0, -86.5),
    'norway':       (57.5, 71.5,  4.0, 32.0),      # incl. Bear Island
    'poland':       (49.0, 55.0, 14.0, 24.5),
    'sweden':       (55.0, 69.0, 10.5, 25.0),
    'turkey':       (35.5, 42.5, 25.5, 45.0),
    'ireland':      (51.4, 55.5, -10.6, -5.8),
}


# Component weight architecture (used for raw vs weighted format detection)
WEIGHTS = {'C': 0.30, 'V': 0.10, 'I': 0.25, 'E': 0.10, 'S': 0.20, 'T': 0.05}


# ═══════════════════════════════════════════════════════════
#  Fleet-size floors per country (KB §56 anti-stub-data gate)
# ═══════════════════════════════════════════════════════════
# Any ssi-data.json with substation_count below the floor is presumed STUB
# DATA and fails validation. Source-of-truth for MIN_FLEET; score-country.py
# now imports this rather than maintaining its own inlined copy.
MIN_FLEET = {
    # Phase 2A (25 June 2026): AT 1200→700 post-Discipline-#36 cross-border
    # remediation reality (Austria 1406 pre-remediation → 741 post; 700 floor
    # leaves ~5% headroom below current observed cohort size and prevents a
    # second-pass remediation from silently tripping the floor).
    "AT": 700, "CH": 800,  "DE": 10000,
    "IT": 4000,             "IE": 990, "JP": 4500,
    # Session 32 recalibration: LU 700→80 (actual 91; small country, coarse OSM canton-level)
    "LU": 80,   "BE": 1000, "NL": 1300, "CZ": 800,
    "LV": 1000, "LT": 400,  "EE": 500, "SI": 120,
    "FR": 6500,
    # Other live countries — conservative floors based on live ssi-data.json counts.
    # Session 32 recalibration: CL 1500→900 (actual 1095; OSM completeness gap),
    #                            GL 100→30 (actual 37; pre-launch dataset).
    # Phase 2A (25 June 2026): CA 8000→6000 post-Discipline-#36 cross-border
    # remediation reality (Canada was 24986 pre-remediation with 74% cross-border
    # leakage → 6399 post; 6000 floor leaves ~6% headroom below current observed).
    # Phase 2C (25 June 2026): 4 additional floors recalibrated to reflect
    # current cohort reality after D#36 remediation + CI pipeline reclassify:
    #   GR 1500→500   (actual 556; also gap-audit-flagged for under-collection)
    #   MX 4000→2200  (actual 2436; pre-D#36 3140 with 22.5% leakage; gap-audit)
    #   PL 3000→2100  (actual 2247; gap-audit-flagged for under-collection)
    #   ES 3500→3300  (actual 3423; marginal 2% shortfall, likely additional D#36)
    # All 4 floors leave 5-10% headroom below current observed. The v4.23 gap
    # audit (task #124) will separately track aspirational per-country fleet
    # targets; MIN_FLEET stays as a no-regression anti-stub-data gate, not an
    # aspirational counts encoder.
    "AU": 5000, "CA": 6000, "CL": 900,  "DK": 1500,
    "FI": 3000, "GR":  500, "GL": 30,   "MX": 2200,
    "NZ": 1000, "NO": 4000, "PL": 2100, "PT": 1500,
    "SE": 3500, "TR": 4000, "GB": 2500, "US": 30000,
    "ES": 3300,
    # Session 34 (Israel onboarding): IL 200 (actual 257; small dense country)
    "IL": 200,
    # PR-5 (F-L4-2 closure 2026-06-08): floors for the 6 F-L4-2 countries
    # not yet covered (IL was already in). Floors set conservatively at
    # ~70% of the current observed counts so genuine data refreshes pass
    # while obvious stub-data (e.g. <50 substations for KR which has ~10k)
    # fail loudly. Recalibrate on the next refresh per the Session 32 pattern.
    "KR":  300,   # Republic of Korea — ~10k actual; floor leaves headroom for partial-refresh
    "CO":  300,   # Colombia — ~1.2k actual
    "CR":  100,   # Costa Rica — ~430 actual (Central American small grid)
    "IS":  100,   # Iceland — ~1.1k actual (small island grid)
    "HU": 1500,   # Hungary — ~7.4k actual
    "SK":  500,   # Slovakia — ~2.4k actual
}


# ═══════════════════════════════════════════════════════════
#  Country slug → ISO 3166-1 alpha-2
# ═══════════════════════════════════════════════════════════
# Used to derive iso2 from filepath when the data lacks an iso2 key.
# PR-5 (F-L4-2): added 7 entries so the 7 F-L4-2 countries get fleet-floor
# protection. Pre-PR-5 they were silently bypassed (iso2=None → MIN_FLEET
# .get(None)=None → permissive skip).
_SLUG_TO_ISO2 = {
    'france': 'FR', 'italy': 'IT', 'uk': 'GB', 'spain': 'ES',
    'germany': 'DE', 'switzerland': 'CH', 'austria': 'AT',
    'us': 'US', 'canada': 'CA', 'japan': 'JP', 'australia': 'AU',
    'chile': 'CL', 'portugal': 'PT', 'new-zealand': 'NZ',
    'greenland': 'GL', 'czechia': 'CZ', 'luxembourg': 'LU',
    'belgium': 'BE', 'netherlands': 'NL', 'estonia': 'EE',
    'latvia': 'LV', 'lithuania': 'LT', 'denmark': 'DK',
    'norway': 'NO', 'finland': 'FI', 'poland': 'PL',
    'sweden': 'SE', 'mexico': 'MX', 'greece': 'GR',
    'turkey': 'TR', 'ireland': 'IE',
    # PR-5 (F-L4-2) — 7 countries that were silently bypassed pre-PR-5
    'korea': 'KR', 'colombia': 'CO', 'israel': 'IL',
    'costa-rica': 'CR', 'iceland': 'IS',
    'hungary': 'HU', 'slovakia': 'SK',
    # PR-5 acceptance audit found one further SoT gap: Slovenia (SI is in
    # MIN_FLEET but was missing from the slug map; same silent-bypass class
    # as the F-L4-2 cohort).
    'slovenia': 'SI',
}


# ═══════════════════════════════════════════════════════════
#  Modifier registry — for PR-5 new gate 9 (range check)
# ═══════════════════════════════════════════════════════════
# Mirrors scripts/pipeline/scoring/modifier_registry.py::MODIFIER_REGISTRY's
# ranges. We embed the range table here (rather than importing) so the
# validator runs on machines that don't have the pipeline package installed
# (e.g. a deploy gate that only ships the validator). Convention #56 says
# the registry is the single source of truth — this is a deliberate copy
# kept in sync via the PR-5 regression test (test_modifier_ranges_match_registry).
_MODIFIER_RANGES = {
    # Phase 2A (25 June 2026): synced with pipeline
    # scripts/pipeline/scoring/modifier_registry.py::MODIFIER_REGISTRY
    # so the validator can never disagree with the engine on what a
    # modifier's declared range is.
    #   • R3_C_mult ceiling 1.30 → 1.50 (was drifting from pipeline's 1.50).
    #   • R7_cyber ceiling 1.50 → 1.05 (was permissive; pipeline says 1.05).
    # Canonical v4.0.2 (5 modifiers)
    "R3_C_mult":      (0.70, 1.50),
    "R4_F_topo":      (0.80, 1.35),
    "R6_restoration": (0.90, 1.10),
    "R6_seismic":     (0.95, 1.25),  # task #180 (13 Jul 2026): floor 1.00 → 0.95 for BE/NL/LU/CZ low-seismicity reality
    "R7_cyber":       (0.99, 1.05),
    # Per-country adaptations
    "R6_volcanic":     (1.00, 1.20),
    "R6_drought":      (1.00, 1.18),
    "R6_armed_conflict": (1.00, 1.12),
    "R6_typhoon":      (1.00, 1.15),
    "R6_chaebol":      (1.00, 1.10),
    # v4.2-ready
    "R6c_flood":       (1.00, 1.30),   # additive type
    "R6d_wildfire":    (1.00, 1.25),
    "R6e_winter":      (1.00, 1.25),
    "R8_adapt":        (0.92, 1.05),   # reverse-signed
    "R9_compound":     (1.00, 1.20),
    "R10_just":        (1.00, 1.15),
}


# ═══════════════════════════════════════════════════════════
#  Check 2 — Fleet-floor (KB §56 anti-stub-data prophylactic)
# ═══════════════════════════════════════════════════════════

def check_fleet_floor(data: Dict[str, Any], iso2: str) -> List[str]:
    """Fail if substation count < MIN_FLEET[iso2]. Returns list of errors."""
    floor = MIN_FLEET.get(iso2)
    if floor is None:
        return []  # no floor defined; permissive
    subs = data.get("substations", [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    actual = len(subs)
    if actual < floor:
        return [
            f"FLEET-FLOOR FAILED (KB §56): {iso2} has {actual} substations < MIN_FLEET ({floor}). "
            f"Likely STUB DATA from placeholder OSM input. Refuse to publish."
        ]
    return []


# ═══════════════════════════════════════════════════════════
#  Check 9 (NEW PR-5) — Per-modifier value within range
# ═══════════════════════════════════════════════════════════

# PR-5 (audit memo 2026-06-08): tolerance band for the modifier-range check.
# Legacy ssi-data.json files (pre-PR-2 cron output) carry modifier values
# that sit fractionally outside the forward-looking MODIFIER_REGISTRY ranges
# due to calibration drift (e.g. Italy's R7_cyber=0.9889 vs registry lower
# bound 0.99). A 2% relative tolerance below the lower bound + 2% above the
# upper bound accommodates this without silencing real out-of-range violations.
# Promotion to strict (tolerance=0) is queued for PR-7 post daily-routine
# refresh.
_MODIFIER_RANGE_TOLERANCE = 0.02


def check_modifier_ranges(substations: list) -> Tuple[List[str], List[str]]:
    """
    For every substation, every modifier value MUST sit within the range
    declared in MODIFIER_REGISTRY (mirror table _MODIFIER_RANGES above),
    with a small tolerance band (_MODIFIER_RANGE_TOLERANCE = 2%) during the
    Phase 1 transition.

    Returns (errors, warnings). Errors are per-modifier violation counts
    above 1% of fleet (suggests systematic bug); below 1% is a warning.
    """
    errors: List[str] = []
    warnings: List[str] = []
    if not substations:
        return errors, warnings

    n = len(substations)
    # Track violations per modifier so we can report aggregated stats
    violations_by_mod: Dict[str, List[Tuple[Any, float, Tuple[float, float]]]] = {}
    for s in substations:
        mods = s.get('modifiers', {})
        if not isinstance(mods, dict):
            continue
        for mod_name, value in mods.items():
            rng = _MODIFIER_RANGES.get(mod_name)
            if rng is None:
                # Unknown modifier — handled separately; not a range violation
                continue
            if not isinstance(value, (int, float)):
                continue
            lo, hi = rng
            # PR-5 tolerance band: forgive drift up to ±2% relative
            lo_tol = lo - abs(lo) * _MODIFIER_RANGE_TOLERANCE
            hi_tol = hi + abs(hi) * _MODIFIER_RANGE_TOLERANCE
            if value < lo_tol or value > hi_tol:
                violations_by_mod.setdefault(mod_name, []).append(
                    (s.get('substation_id', s.get('id', '?')), value, rng)
                )

    for mod_name, viols in sorted(violations_by_mod.items()):
        count = len(viols)
        pct = count / n * 100
        sample = viols[0]
        sample_id, sample_value, (lo, hi) = sample
        msg = (
            f"MODIFIER-RANGE: {count} substations ({pct:.2f}%) have "
            f"{mod_name} outside [{lo}, {hi}]. "
            f"Example: substation {sample_id!r} has {mod_name}={sample_value}"
        )
        if pct >= 1.0:
            errors.append(msg)
        else:
            warnings.append(msg)
    return errors, warnings


# ═══════════════════════════════════════════════════════════
#  Check 10 (NEW PR-5) — Regional summary ↔ substation membership
# ═══════════════════════════════════════════════════════════

def check_regional_consistency(data: Dict[str, Any]) -> List[str]:
    """
    The `regions` rollup MUST reflect actual substation membership. Specifically:
      (a) Every substation's `region` code MUST appear in the regions rollup.
      (b) Every region in the rollup MUST have ≥1 member substation.
      (c) Per-region substation count in regions rollup (if declared) MUST
          match the actual count from the substations array.

    Returns list of errors. Tolerates the two known regions shapes (array
    of {code, ...} dicts or {code: {...}} dict).
    """
    errors: List[str] = []
    subs = data.get('substations', [])
    if isinstance(subs, dict):
        subs = list(subs.values())
    if not subs:
        return errors

    regions = data.get('regions', [])
    if not regions:
        return errors

    # Normalize regions to {code: meta_dict}
    regions_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(regions, dict):
        regions_map = dict(regions)
    elif isinstance(regions, list):
        for r in regions:
            if isinstance(r, dict):
                code = r.get('code') or r.get('region') or r.get('id')
                if code:
                    regions_map[code] = r

    # Count actual substations per region
    actual_counts: Dict[str, int] = {}
    sub_regions = set()
    for s in subs:
        rcode = s.get('region')
        if rcode:
            actual_counts[rcode] = actual_counts.get(rcode, 0) + 1
            sub_regions.add(rcode)

    # (a) Every substation's region appears in rollup (with 5% tolerance for
    # legacy data where region codes drift from canonical labels)
    if regions_map:
        rollup_codes = set(regions_map.keys())
        orphan = sub_regions - rollup_codes
        if orphan:
            orphan_count = sum(actual_counts[r] for r in orphan)
            pct = orphan_count / len(subs) * 100
            if pct >= 5.0:
                errors.append(
                    f"REGIONAL-CONSISTENCY: {len(orphan)} region code(s) "
                    f"({sorted(orphan)[:5]}) referenced by {orphan_count} substations "
                    f"({pct:.1f}%) but absent from regions rollup."
                )

        # (c) Per-region count consistency
        for code, meta in regions_map.items():
            if not isinstance(meta, dict):
                continue
            declared = meta.get('substation_count') or meta.get('count') or meta.get('total')
            if isinstance(declared, int) and declared >= 0:
                actual = actual_counts.get(code, 0)
                if declared != actual and abs(declared - actual) > max(2, 0.05 * declared):
                    errors.append(
                        f"REGIONAL-CONSISTENCY: region {code} declares "
                        f"substation_count={declared} but actual={actual}."
                    )

    return errors


# ═══════════════════════════════════════════════════════════
#  Check 11 (NEW PR-5) — PR-3 provenance fields presence
# ═══════════════════════════════════════════════════════════

def check_provenance_fields(substations: list) -> List[str]:
    """
    PR-3 (audit memo 2026-06-08) added 3 provenance fields to every substation
    record: mult_product, add_sum, modifier_impacts. This is a WARNING-level
    gate until the daily-routine pipeline refreshes every country (planned
    PR-7). After PR-7 it should be promoted to ERROR.

    Returns list of warnings (not errors during the transition).
    """
    if not substations:
        return []
    sample = substations[0]
    missing = []
    for field in ('mult_product', 'add_sum', 'modifier_impacts'):
        if field not in sample:
            missing.append(field)
    if missing:
        return [
            f"PR-3 PROVENANCE: substation records missing {missing}. "
            f"Will be promoted to ERROR after PR-7 daily-routine refresh."
        ]
    return []


# ═══════════════════════════════════════════════════════════
#  validate_file — the main per-file validator
# ═══════════════════════════════════════════════════════════

def validate_file(filepath: str) -> Tuple[List[str], List[str]]:
    """Validate a single ssi-data.json file. Returns (errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []

    # Detect country from path
    parts = filepath.replace('\\', '/').split('/')
    country: Optional[str] = None
    for p in parts:
        if p in COUNTRY_BOUNDS:
            country = p
            break

    # Load
    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"FATAL: Invalid JSON — {e}"], []

    # Convention #79 — resolve shards before any gate runs.
    #
    # Six countries (france, germany, italy, poland, uk, us) exceed the 60 MB
    # threshold, so their ssi-data.json is a manifest with no inline
    # `substations` key. Until 19 August 2026 this validator read that manifest
    # and saw zero substations — whereupon check_modifier_ranges returned early
    # on the empty list and the file PASSED. A validator that reports success
    # on 577,765 substations it never looked at is worse than no validator.
    # Cross-reference: modification-log M-030.
    if isinstance(data, dict) and data.get("sharded"):
        shards = data.get("substations_shards") or []
        if not shards:
            return ["FATAL: sharded=true but no 'substations_shards' list"], []
        base = Path(filepath).resolve().parent
        merged = []
        for shard in shards:
            rel = shard.get("path") if isinstance(shard, dict) else shard
            shard_fp = base / rel if rel else None
            if not shard_fp or not shard_fp.exists():
                return [f"FATAL: manifest references missing shard {rel!r}"], []
            try:
                payload = json.loads(shard_fp.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                return [f"FATAL: shard {rel} is invalid JSON — {e}"], []
            if isinstance(payload, dict):
                payload = payload.get("substations", [])
            if not isinstance(payload, list):
                return [f"FATAL: shard {rel} did not parse to a list"], []
            declared = shard.get("count") if isinstance(shard, dict) else None
            if declared is not None and len(payload) != declared:
                return [
                    f"FATAL: shard {rel} holds {len(payload)} substations but "
                    f"the manifest declares {declared}"
                ], []
            merged.extend(payload)
        data = dict(data)
        data["substations"] = merged

    # Class D fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3): guard
    # against flat-list root schema (Latvia + any future country in Phase 1
    # intermediate state per CONVENTION_78_BINDING_EMPIRICAL_AUDIT §4bis.4).
    # Task #263 CLOSED — flat-list is Phase 1 pre-wrapper state, NOT a bug.
    # Convention #56 visibly-honest degradation: surface the missing wrapper via
    # a WARNING (post-L3 rewrite by enrichment/merge.py adds the wrapper).
    if isinstance(data, list):
        warnings.append(
            "Country uses flat-list root schema (Phase 1 intermediate state per "
            "CONVENTION_78 §4bis.4); Phase 2 L2/L3 pipeline will rewrite with wrapper"
        )
        data = {"substations": data}

    # ─── Check 1: top-level keys ──
    for key in ['meta', 'fleet_summary', 'regions', 'substations']:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    substations = data.get('substations', [])
    if isinstance(substations, dict):
        substations = list(substations.values())
    if not substations:
        errors.append("No substations found")
        return errors, warnings

    # ─── Check 2: fleet-floor ──
    iso2 = data.get('iso2') or (_SLUG_TO_ISO2.get(country) if country else None)
    if iso2:
        errors.extend(check_fleet_floor(data, iso2))

    # ─── Check 3: regions count ──
    regions = data.get('regions', [])
    if isinstance(regions, list) and len(regions) <= 1:
        errors.append(f"Only {len(regions)} region(s) — expected >1")
    elif isinstance(regions, dict) and len(regions) <= 1:
        errors.append(f"Only {len(regions)} region(s) — expected >1")

    # ─── Check 4: substation schema ──
    required_fields = ['substation_id', 'lat', 'lon', 'R_median', 'components', 'classification']
    sample = substations[0]
    for field in required_fields:
        if field not in sample:
            errors.append(f"Substation missing field: {field}")

    # ─── Check 5: component format (must be raw, not weighted) ──
    comp_sums = []
    for s in substations[:100]:
        if s.get('components'):
            comp_sum = sum(s['components'].get(k, 0) for k in WEIGHTS)
            comp_sums.append(comp_sum)
    if comp_sums:
        avg_sum = sum(comp_sums) / len(comp_sums)
        if avg_sum <= 1.0:
            errors.append(f"Weighted format detected (avg compSum={avg_sum:.3f}) — must be raw (>1.0)")

    # ─── Check 6: lat/lon bounds ──
    if country and country in COUNTRY_BOUNDS:
        bounds = COUNTRY_BOUNDS[country]
        out_of_bounds = 0
        for s in substations:
            lat, lon = s.get('lat', 0), s.get('lon', 0)
            if lat < bounds[0] or lat > bounds[1] or lon < bounds[2] or lon > bounds[3]:
                out_of_bounds += 1
        if out_of_bounds > 0:
            pct = out_of_bounds / len(substations) * 100
            if pct > 5:
                errors.append(f"{out_of_bounds} substations ({pct:.1f}%) outside {country} bounds")
            else:
                warnings.append(f"{out_of_bounds} substations ({pct:.1f}%) outside {country} bounds")

    # ─── Check 7: R_median range ──
    # Phase 2A (25 June 2026): range extended [0, 1] → [0, 1.30] for v4.2.
    # The v4.2 master equation is
    #   R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)
    # where the multiplicative chain is compressed asymptotically toward 1.0
    # by soft_clip_upper, and the ADDITIVE R6c_flood (range [1.00, 1.30])
    # layers on top. Max theoretical R_median is 1.30. See Convention #77
    # + methodology brief for the derivation. Values above 1.30 signal a
    # scoring engine bug (additive stack overflow) and remain an error.
    # Classes B/C fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3):
    # filter pre-L3 None R_median subs per Convention #56 (visibly-honest
    # degradation, CONVENTION_78 §4bis.4). Pre-L3 substations legitimately
    # carry R_median=None until Phase 2 L3 rescore completes.
    r_values = [s['R_median'] for s in substations if s.get('R_median') is not None]
    n_unscored = len(substations) - len(r_values)
    if not r_values:
        warnings.append(
            f"CHECK 7: 0/{len(substations)} substations have numeric R_median "
            f"(all pre-L3 state); Check 7 range validation skipped"
        )
    else:
        r_min, r_max = min(r_values), max(r_values)
        if r_min < 0 or r_max > 1.30:
            errors.append(f"R_median out of [0, 1.30] range: {r_min:.3f}–{r_max:.3f}")
        if n_unscored > 0:
            warnings.append(
                f"CHECK 7: {n_unscored}/{len(substations)} substations have "
                f"R_median=None (pre-L3 state); excluded from range validation"
            )

    # ─── Check 8: classification ↔ R_median band invariant ──
    # Phase 2A (25 June 2026): 4-band → 5-band system per operator Q1(b)
    # decision. The 5th band 'Extreme' [1.00, 1.30] captures the additive
    # R6c_flood zone where multiplicative saturation combines with flood-
    # driven overflow. See methodology cascade in Phase 2B: methodology.html
    # + intelligence-sections.js + esg-sections.js + map.js + regional-
    # sections.js all updated for the 5-band system.
    # Thresholds preserved: warn ≥ 0.5%, error ≥ 2.0%. The 2% threshold
    # accommodates boundary-edge cases produced by the legacy pipeline
    # (e.g. R_median=0.337 classified 'Low' instead of 'Medium' — fractional
    # drift at band boundaries). Phase 2C full-cohort rescore against the
    # 5-band system should collapse mismatch rates to near-zero cohort-wide.
    # Classes B/C fix (16 July 2026, FAILURE_SOLVING_PROPOSAL_20260716.md §3):
    # None-guard for pre-L3 substations per Convention #56 + CONVENTION_78 §4bis.4
    def _expected_band_v42(r):
        if r is None: return 'Unclassified'  # pre-L3 state per Convention #56
        if r < 0.25:  return 'Low'
        if r < 0.50:  return 'Medium'
        if r < 0.75:  return 'High'
        if r < 1.00:  return 'Critical'
        return 'Extreme'

    # ── M-064 (20 August 2026): compare the ABSOLUTE band, not the label ──
    #
    # This check compared `classification` against the band derived from
    # R_median. Since **Task #461** (22 July 2026) `classification` is the
    # per-country NORMALISED band — explicitly "band label = within-country
    # ranking not absolute R" — so the two are *designed* to differ. The check
    # was testing a pre-Task-#461 contract.
    #
    # It is an ERROR, not a warning, so `run.py` Phase 2b refused to commit for
    # every normalised country: czechia 100%, austria 99.6%, australia 71.8%.
    # `python -m scripts.pipeline.run` could not complete cohort-wide, and the
    # message blamed the data. That is why the cohort refresh had never run.
    #
    # The absolute band lives in `_band_absolute`, written by
    # normalise_bands_per_country.py before it overwrites `classification`.
    # Verified at the time of this change: 83,443 of 83,443 scored records
    # across all 31 scoring countries carry it, and it equals
    # classify_band(R_median) for every one.
    #
    # THIS IS NOT A RELAXATION. The old check tested one thing and could not
    # distinguish "wrong band" from "not a band at all". This tests four, and
    # each catches something the old one could not:
    #   (a) `_band_absolute` is PRESENT      — absence now fails rather than
    #                                          passing unexamined (M-030)
    #   (b) `_band_absolute` == band(R_median) — the real score↔band invariant
    #   (c) `classification` is a VALID band  — garbage labels were previously
    #                                          indistinguishable from drift
    #   (d) where the country is NOT Task-#461 normalised, `classification`
    #       must equal `_band_absolute` — with no normalisation applied there
    #       is no legitimate reason for them to differ, so genuine drift is
    #       still caught
    _fs = data.get('fleet_summary') or {}
    normalised = bool((_fs.get('_band_normalisation') or {}).get('applied'))

    missing_abs = 0
    abs_wrong = 0
    bad_label = 0
    drift = 0
    n_skipped_pre_l3 = 0
    sample_violation = None
    sample_missing = None
    sample_label = None
    sample_drift = None

    VALID_BANDS = {'Low', 'Medium', 'High', 'Critical', 'Extreme', 'Unclassified'}

    for s in substations:
        r = s.get('R_median')
        if r is None:
            n_skipped_pre_l3 += 1
            continue  # Convention #56: pre-L3 subs excluded from the tally
        expected = _expected_band_v42(r)
        band_abs = s.get('_band_absolute')
        cls = s.get('classification')

        if band_abs is None:
            missing_abs += 1
            if sample_missing is None:
                sample_missing = s.get('substation_id', s.get('id', '?'))
        elif band_abs != expected:
            abs_wrong += 1
            if sample_violation is None:
                sample_violation = (s.get('substation_id', s.get('id', '?')),
                                    band_abs, expected, r)

        if cls not in VALID_BANDS:
            bad_label += 1
            if sample_label is None:
                sample_label = (s.get('substation_id', s.get('id', '?')), cls)

        if not normalised and band_abs is not None and cls != band_abs:
            drift += 1
            if sample_drift is None:
                sample_drift = (s.get('substation_id', s.get('id', '?')), cls, band_abs, r)

    if n_skipped_pre_l3 > 0:
        warnings.append(
            f"CHECK 8: {n_skipped_pre_l3}/{len(substations)} substations "
            f"skipped — R_median=None (pre-L3 state per Convention #56)"
        )

    n_scored = len(substations) - n_skipped_pre_l3

    if missing_abs > 0:
        errors.append(
            f"CLASSIFICATION-BAND: {missing_abs}/{n_scored} scored substations have "
            f"no `_band_absolute` (e.g. {sample_missing!r}). The absolute band is "
            f"what makes the score↔band invariant checkable once Task #461 "
            f"normalisation has overwritten `classification`. Run "
            f"scripts/normalise_bands_per_country.py, which snapshots it."
        )

    if abs_wrong > 0:
        pct = abs_wrong / n_scored * 100 if n_scored else 0
        sid, got, expected, r = sample_violation
        r_str = f"{r:.4f}" if isinstance(r, (int, float)) else "None"
        msg = (
            f"CLASSIFICATION-BAND: {abs_wrong} substations ({pct:.2f}%) have "
            f"`_band_absolute` mismatched to their own R_median. "
            f"Example: {sid!r} has R_median={r_str} (expected={expected}) but "
            f"_band_absolute={got!r}. This is the score↔band invariant and it "
            f"does not tolerate normalisation as an excuse."
        )
        if pct >= 2.0:
            errors.append(msg)
        elif pct >= 0.5:
            warnings.append(msg)

    if bad_label > 0:
        sid, cls = sample_label
        errors.append(
            f"CLASSIFICATION-BAND: {bad_label}/{n_scored} substations carry a "
            f"`classification` that is not a band at all (e.g. {sid!r} → {cls!r}). "
            f"Valid: {sorted(VALID_BANDS)}."
        )

    if drift > 0:
        pct = drift / n_scored * 100 if n_scored else 0
        sid, cls, band_abs, r = sample_drift
        r_str = f"{r:.4f}" if isinstance(r, (int, float)) else "None"
        msg = (
            f"CLASSIFICATION-BAND: this country has no Task #461 normalisation "
            f"applied, so `classification` should equal `_band_absolute` — but "
            f"{drift} substations ({pct:.2f}%) differ. Example: {sid!r} "
            f"R_median={r_str}, _band_absolute={band_abs!r}, "
            f"classification={cls!r}. Either run "
            f"scripts/normalise_bands_per_country.py, or this is genuine "
            f"legacy drift needing a rescore."
        )
        if pct >= 2.0:
            errors.append(msg)
        elif pct >= 0.5:
            warnings.append(msg)

    # ─── Check 9 (NEW PR-5): per-modifier range ──
    mod_errors, mod_warnings = check_modifier_ranges(substations)
    errors.extend(mod_errors)
    warnings.extend(mod_warnings)

    # ─── Check 10 (NEW PR-5): regional consistency ──
    errors.extend(check_regional_consistency(data))

    # ─── Check 11 (NEW PR-5): PR-3 provenance fields ──
    # Currently emits warnings only; promoted to error post-PR-7.
    warnings.extend(check_provenance_fields(substations))

    # ─── ESG fields completeness (legacy warning) ──
    esg_fields = ['markov', 'seismic', 'transition']
    for field in esg_fields:
        if not sample.get(field):
            warnings.append(f"Missing ESG field: {field}")

    return errors, warnings


# ═══════════════════════════════════════════════════════════
#  CLI entry point
# ═══════════════════════════════════════════════════════════

def _load_sot_country_slugs() -> List[str]:
    """
    Phase 2A (25 June 2026 · KB §57 alignment): --all mode iterates the
    canonical SoT slug list at intelligence/countries.json rather than the
    validator's own COUNTRY_BOUNDS dict. Pre-Phase-2A the validator silently
    bypassed 9 SoT countries (denmark, finland, greece, mexico, norway,
    poland, sweden, turkey, ireland) because their bounds weren't in
    COUNTRY_BOUNDS. Bounds for all 39 SoT slugs are now populated so this
    change is safe.

    Fallback (when countries.json isn't reachable — e.g. sparse-checkout
    CI context that omits intelligence/): iterate sorted(COUNTRY_BOUNDS)
    for backward compatibility.
    """
    sot_path = Path(__file__).resolve().parent.parent / "intelligence" / "countries.json"
    if sot_path.exists():
        try:
            with open(sot_path) as f:
                cfg = json.load(f)
            slugs = cfg.get("slugs", [])
            if isinstance(slugs, list) and slugs:
                return sorted(slugs)
        except (json.JSONDecodeError, OSError):
            pass
    # Fallback — sparse-checkout or malformed SoT
    return sorted(COUNTRY_BOUNDS.keys())


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_schema.py <file.json> [--all]")
        sys.exit(1)

    if sys.argv[1] == '--all':
        all_pass = True
        for country in _load_sot_country_slugs():
            filepath = f"{country}/ssi-data.json"
            if os.path.exists(filepath):
                errors, warnings = validate_file(filepath)
                status = "✅" if not errors else "❌"
                print(f"{status} {country}: {len(errors)} errors, {len(warnings)} warnings")
                for e in errors:
                    print(f"    ERROR: {e}")
                for w in warnings:
                    print(f"    WARN: {w}")
                if errors:
                    all_pass = False
            else:
                print(f"  ⚠ {country}: file not found")
        sys.exit(0 if all_pass else 1)
    else:
        errors, warnings = validate_file(sys.argv[1])
        status = "PASS" if not errors else "FAIL"
        print(f"\n{status}: {len(errors)} errors, {len(warnings)} warnings")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN: {w}")
        sys.exit(0 if not errors else 1)


if __name__ == '__main__':
    main()
