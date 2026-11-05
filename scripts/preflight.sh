#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# preflight.sh — Discipline Enforcement Orchestrator (Session 32 / Phase 4)
#
# Runs all enforceable disciplines as a single pre-flight gate before deploy.
# Returns 0 if all gates pass, non-zero (1-N) if any fail.
#
# Usage:
#   bash scripts/preflight.sh                 # all countries, all gates
#   bash scripts/preflight.sh <slug>          # single country
#   bash scripts/preflight.sh <slug> --strict # exit on first fail
#   bash scripts/preflight.sh --report-only   # report findings, don't exit non-zero
#
# Gate inventory (post-KR Session 32):
#   D#3   — Inline JS parse-check (check_inline_js_parse.py)        [BPG Part XXXIV]
#   D#14  — Canonical {s,l,a} grid-geo + regions list schema         [BPG Part XXXVII]
#   D#15  — country-configs/<slug>.json mandatory                    [BPG Part XXXVII]
#   D#16  — Page ID-count parity vs canonical (check_page_ids.py)    [BPG Part XXXVIII NEW]
#   D#17  — Substation 44-field schema + rd_pct_gdp variance          [BPG Part XXXVIII NEW]
#   D#18  — nav.js slug parity (check_nav_slug.py)                    [BPG Part XXXVIII NEW]
#   D#19  — Currency-symbol country-native primary                    [BPG Part XXXVIII NEW]
#   D#20  — Edition anchor month offset range [1,12]                  [BPG Part XXXIX NEW]
#   D#21  — Content leakage (proper-noun vocab)                       [BPG Part XL]
#   D#26  — Map aesthetic (two-axis offshore clip + jumps)            [BPG Part XLII NEW v2]
#   D#27  — Substation sub-dict completeness (stub-class)             [BPG Part XLII NEW]
#   D#28  — Power-line geometry richness (chord-only defect)          [BPG Part XLIII]
#   D#29  — R3_C_mult per-substation variance (non-strict health)     [BPG Part XLV NEW]
#   D#30  — Required-files presence (intelligence/ssi-metadata/data/geo) [BPG Part LX NEW]
#   D#56  — Fleet-size floor (KB §56 stub-deploy regression)          [validate-schema.py]
#   D#57  — Doctrine reproduce block (check_doctrine_has_reproduce.py) [DISCIPLINE_the_claim_gate I2]
#
#   THE DECLARED ADVISORY SET — wired 28 September 2026 under FO-017 (b).
#   Called "THE NINE" in three places until 2 October; the case statement held
#   EIGHT on the day it was written, and holds six now that D#58 and D#59 are
#   promoted. A label carrying a count goes stale the first time the count
#   moves, so it no longer carries one. These are the
#   gates that asked whether a published NUMBER WAS MEASURED and were run by
#   nothing at all. The eighteen above ask about form; not one of them asks
#   whether a coefficient came from a source.
#
#   D#58  — pin14 name-hash sweep      (cannot fail — E21, threshold behind FO-016)
#   D#59  — pin14 field-first          (cannot fail — E21, threshold behind FO-016)
#   D#60  — components are measured    (strict; FO-013 · §1's 0.180/0.820)
#   D#61  — R_base derives from comps  (strict; FO-013(a) · FO-014)
#   D#62  — master-equation closure    (strict; E31)
#   D#63  — confidence-interval coherence (strict; E22 — the gate is fixed, the
#                                          6 remaining pairs are the defect)
#   D#64  — R7 cutover complete        (E9)
#   D#65  — band rule per country      (PASSES TODAY → BLOCKING, not advisory)
#   D#66  — published counts match     (PASSES TODAY → BLOCKING, not advisory)
#
#   They read the whole estate — 622,104 records — so they run only on a
#   full-estate invocation, never on `preflight.sh <slug>`. That is a declared
#   design choice, not an omission: a per-country run cannot answer an
#   estate-wide question, and making a deploy wait minutes for one it cannot
#   answer is how a gate gets switched off.
# ════════════════════════════════════════════════════════════════════════════

set -uo pipefail
cd "$(dirname "$0")/.."

SLUG=""
# Strict is the DEFAULT as of 25 September 2026.
#
# It was not, and that was the defect. Every child gate here exits 0 on failure
# unless handed --strict; preflight passed an empty flag by default; and every
# landing script invoked preflight without the flag. The result was a gate that
# printed "1 fails" and "✓ PASS" on consecutive lines. Run against a slug that
# does not exist, eleven of twelve gates passed it.
#
# Opting out is now explicit, named and loud. A gate that should not block gets
# an entry in ADVISORY below with a written reason — a declared exemption, not
# an accidental one.
STRICT_FLAG="--strict"
LENIENT=0
REPORT_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_FLAG="--strict" ;;
    --lenient) STRICT_FLAG=""; LENIENT=1 ;;
    --report-only) REPORT_ONLY=1 ;;
    --*) ;;  # ignore unknown flags (don't treat as slug)
    *) SLUG="$arg" ;;
  esac
done




echo "════════════════════════════════════════════════════════════════════════"
echo "preflight.sh — Discipline Enforcement Orchestrator"
echo "Target: ${SLUG:-ALL COUNTRIES}"
echo "Mode: $([ -n "$STRICT_FLAG" ] && echo strict || echo lenient)"
echo "════════════════════════════════════════════════════════════════════════"

TOTAL_FAILS=0
FAILED_GATES=()
ADVISORY_WARNS=0
ADVISORY_GATES=()

# Gates that report but do not block, each with the reason it does not.
# Anything not named here blocks.
is_advisory() {
  case "$1" in
    # ── THE DECLARED ADVISORY SET, FO-017 (b), 28 September 2026 ─────────
    # Accidental silences become DECLARED ones. (Written as "nine"; it was
    # eight, and is six since 2 October.) Each entry carries
    # the figure measured on the live estate that day and the PLAN_OF_WORK.md
    # row that will clear it. Promotion to blocking is deleting one line.
    #
    # THE FLAG OFFICER'S CAVEAT, RECORDED WITH A DATE: if these entries are
    # still here unchanged at the END OF OCTOBER 2026, (a) was the right
    # ruling and they should be promoted rather than re-argued.

    # ── D#58 and D#59 PROMOTED TO BLOCKING, 2 October 2026 ───────────────
    # They were advisory because "a threshold is a doctrine value and sits
    # behind FO-016", which is true of a THRESHOLD and not of a RATCHET. Both
    # gates now carry a failure path against doctrine/PIN14_BASELINE.txt, which
    # asserts no limit doctrine has not set — only that the Pin 14 surface is no
    # worse than it was on 2 October. FO-016 is off their critical path and
    # stays open; it is still the right place to set an actual threshold.
    #
    # BOTH PASS TODAY, and that is the whole safety argument for promoting them.
    # Had either failed, the ratchet would have landed and these two lines would
    # have stayed. They are listed here, deleted, rather than removed silently:
    #     "D#58") return 0 ;;   -- 91.2% of gt.cluster_coeff from a name hash
    #     "D#59") return 0 ;;   -- 28 hash-written field targets in 6 files
    # Restoring those two lines reverts the promotion, and nothing else does.
    # See doctrine/FINDING_a_ratchet_is_not_a_threshold_so_two_advisory_gates_can_be_promoted.md

    # D#60 — component provenance PARTIAL/UNCHECKED; portugal 157, uk 37,
    # germany 29, italy 11. Owned by FO-013 and by §1's 0.180-measured /
    # 0.820-name-hash split, which is the estate's largest open defect.
    "D#60") return 0 ;;

    # D#61 — R_base derivation regressed: DRIFT, ONLY_FLOOD, BANDED_BLIND,
    # canada 138 zeroed. Owned by FO-013(a) — rescore the twenty-seven — and
    # by FO-014's correction that the precondition is on the composite.
    "D#61") return 0 ;;

    # ── D#62 PROMOTED TO BLOCKING, 2 October 2026 ────────────────────────
    # Its stated complaint was "39 countries publish 'verified' for a closure
    # check that does not hold: sweden 54.2%, canada 57.4%, denmark 58.2%,
    # australia 60.8%" (E31). DISCHARGED. Measured today under --strict:
    #     DECLARED  0   countries claiming 'verified' below 99% closure
    #     STRICT: no regression, and no country claims a verification it
    #     does not have.
    # The gate exits 0. Cohort closure is 31.5% mean and 198,708 records still
    # fail CLOSURE — that defect is real and is NOT what this entry claimed;
    # the gate ratchets it against a baseline and the baseline is falling.
    # Promoted because it PASSES, which is the whole safety argument, same as
    # D#58 and D#59 in JL. The deleted line, for the revert:
    #     "D#62") return 0 ;;

    # D#63 — 6 country-check pairs above baseline by 64 in total, in finland,
    # iceland and new-zealand. The GATE is fixed (E22, landed FU) and now sees
    # the country rather than the cohort; what remains is the defect it found.
    "D#63") return 0 ;;

    # D#64 — cutover incomplete: A 619,522 records not marked retired,
    # B 543,546 still carry modifiers.R7_cyber, C 23 whose mult_product does
    # not reproduce from v2. E9.
    "D#64") return 0 ;;

    # D#65 and D#66 are NOT here, deliberately. Both PASS on the live estate
    # today — 39 countries and 622,104 assets 100% normalised, and every
    # published count matching the register. A gate that passes has no silence
    # to declare, and making it advisory would CREATE one. They are wired
    # blocking. This narrows FO-017 (b) and the narrowing is recorded rather
    # than taken quietly.

    # D#67 — wired 2 October 2026 and advisory from its first run, which is
    # the honest order. It was one of E18's four checkers that NO RUNNER
    # INVOKED. Run for the first time under --strict today it reports a real
    # and large defect: 39 COUNTRIES PUBLISH REGIONAL BAND COUNTS THEIR OWN
    # SUBSTATIONS CONTRADICT — israel 6 of 6 regions (97 records), costa-rica
    # 7 of 7 (74), greece 20 of 55 (53), luxembourg 11 of 12 (43), colombia
    # 17 of 29 (40), greenland 1 of 6 (1).
    #
    # It is declared here rather than invoked without --strict, because a
    # silence in the argv is on no register at all (check_gate_silences.py).
    # ── D#67 PROMOTED TO BLOCKING the same day it was wired, 2 October ────
    # The repair ran. ssi_repair_fleet_bands.py --apply across all 39 fleets,
    # authorised by the flag officer on the measured size: 46.3% of the estate's
    # published band counts moved, and NOT ONE SUBSTATION RECORD CHANGED — all
    # 39 manifests differ from HEAD in exactly two keys, fleet_summary and
    # regions, both recounted from each substation's own `classification`.
    # The gate now reports: "OK: published bands match the classification field
    # (39 countries)". Promoted because it PASSES, which is the whole safety
    # argument, as for D#58, D#59 and D#62. The deleted line, for the revert:
    #     "D#67") return 0 ;;

    # D#78 - wired 8 October 2026 and advisory from its first run, which is
    # the honest order, as D#67 was on 2 October. It was one of E18's guards
    # that NO RUNNER INVOKED. Under --strict it reports a real, pre-existing
    # defect: of 23 NUTS-coded fleets, 11 carry a region NAME that names a
    # different administrative unit from the one its CODE denotes. That is
    # E115's class and an open question, not this landing's to rule on.
    #
    # Declared here rather than invoked without --strict, because a silence in
    # the argv is on no register at all (check_gate_silences.py, and the
    # landing preamble's land_check_gate_silences, which refused the first
    # version of this wiring).
    #
    # Promotion to blocking is deleting this one line, and is a ruling on the
    # eleven - not a wiring change.
    "D#78") return 0 ;;

    # D#29: per-substation R3 variance. CORRECTED 12 October 2026 (E311).
    #
    # THIS NOTE SAID, UNTIL TODAY: "Pipelines onboarded through
    # score-country.py's det_var pattern have a systemic discrete-R3 weakness".
    # It is kept as a quotation because two documents cite it and one register
    # row (E41) was written to correct it -- and E41 got it wrong too.
    #
    # MEASURED: det_var(sid+name+'R3', 1.0, 0.08), stored at round(,6), is what
    # score-country.py writes and it reproduces NONE of the published values --
    # 0 of australia's 8,078, belgium's 1,219, greece's 556, korea's 1,290,
    # denmark's 2,433, italy's 41,662 and the us's 73,859; 2 of france's 168,894
    # and 2 of the uk's 34,120, which is the rate chance predicts. The ranges
    # settle it independently: the call can only emit [0.92, 1.08] and australia
    # spans 0.7336..1.1764, greece reaches 1.2130, denmark 1.2290.
    #
    # WHAT DOES REPRODUCE is the mechanism the block further down already names:
    # regional socio-economic data applied uniformly, enrich_esg_gaps.py's
    # round(1.0 - v_socio * 0.15, 4). It reproduces 57,197 of the uk's 59,744
    # and 60,020 of the us's 73,859. The uk carries 13 distinct V_socio against
    # 1,534 distinct R3 values, so it is a mixture -- and 13 inputs applied
    # uniformly IS the clustering this gate was built to catch.
    #
    # The seven one-value fleets each store ONE value at FOUR decimals, where
    # score-country.py writes six: france and germany 0.9720, italy 0.8909,
    # japan 0.9065, portugal 0.9289, spain 0.9401, us 0.9730. germany, japan and
    # the us equal the formula at their own modal V_socio; france and spain at a
    # value they carry but not the mode; ITALY'S 0.727333 AND PORTUGAL'S 0.474
    # ARE NOT AMONG THEIR OWN V_socio VALUES AT ALL, so a third writer applied
    # them and E311 does not claim to know which.
    #
    # B.2 still renders correctly via country-config quartile bucketing. Health
    # metric until the pipeline-layer cleanup lands. Promotion to blocking is a
    # ruling, not a wiring change, and nothing about the line below has moved.
    "D#29") return 0 ;;
    *) return 1 ;;
  esac
}

run_gate() {
  local name="$1"
  local label="$2"
  shift 2
  echo ""
  echo "─── $name: $label ───"
  if "$@"; then
    echo "  ✓ PASS"
  else
    rc=$?
    if is_advisory "$name"; then
      echo "  ⚠ WARN (exit=$rc) — $name is advisory by declaration, not blocking"
      ADVISORY_WARNS=$((ADVISORY_WARNS + 1))
      ADVISORY_GATES+=("$name")
    else
      echo "  ✗ FAIL (exit=$rc)"
      TOTAL_FAILS=$((TOTAL_FAILS + 1))
      FAILED_GATES+=("$name")
    fi
  fi
}

# ── THE DECLARED ADVISORY SET (FO-017 (b)) — estate-wide only ─────────
if [ -z "$SLUG" ]; then
  [ -f scripts/check_pin14_name_hash_sweep.py ] && run_gate "D#58" \
    "pin 14 — name-hash sweep (cannot fail; E21)" \
    python3 scripts/check_pin14_name_hash_sweep.py
  # D#74 — the control-flow half of D#59. A hash in an `if` TEST steers a
  # published value and the field-first scan, which follows DATA flow, cannot
  # see it. Wired BLOCKING: it passes today against its own ratchet, and a
  # guard that passes has no silence to declare.
  [ -f scripts/check_pin14_control_flow.py ] && run_gate "D#74" \
    "Pin 14 — a hash in the condition" \
    python3 scripts/check_pin14_control_flow.py
  [ -f scripts/check_pin14_field_first.py ] && run_gate "D#59" \
    "pin 14 — field-first (cannot fail; E21)" \
    python3 scripts/check_pin14_field_first.py
  [ -f scripts/check_components_are_measured.py ] && run_gate "D#60" \
    "components are measured" \
    python3 scripts/check_components_are_measured.py --all $STRICT_FLAG
  [ -f scripts/check_r_base_derives_from_components.py ] && run_gate "D#61" \
    "R_base derives from components" \
    python3 scripts/check_r_base_derives_from_components.py --all $STRICT_FLAG
  [ -f scripts/check_master_equation_closure.py ] && run_gate "D#62" \
    "master-equation closure" \
    python3 scripts/check_master_equation_closure.py --all $STRICT_FLAG
  [ -f scripts/check_confidence_interval_coherence.py ] && run_gate "D#63" \
    "confidence-interval coherence" \
    python3 scripts/check_confidence_interval_coherence.py --all $STRICT_FLAG
  [ -f scripts/check_r7_cutover_complete.py ] && run_gate "D#64" \
    "R7 cutover complete" \
    python3 scripts/check_r7_cutover_complete.py
  [ -f scripts/check_band_rule_per_country.py ] && run_gate "D#65" \
    "band rule per country (BLOCKING — passes today)" \
    python3 scripts/check_band_rule_per_country.py
  # ── D#67..D#69, wired 2 October 2026 ─────────────────────────────────
  # E18: four checkers and tests no runner invoked. These three pass today
  # (17s, 1s, 7s) and are wired BLOCKING — a guard that passes has no silence
  # to declare, and making it advisory would create one, which is the
  # narrowing D#65 and D#66 already record. The fourth,
  # test_texture_persistence.py, is NOT here: it requires --fine-a, --fine-b
  # and --coarse, so it is a CLI instrument misnamed test_*, which is E9's
  # defect in the test_ namespace. It is named in §3 rather than wired.
  [ -f scripts/check_bands_match_classification.py ] && run_gate "D#67" \
    "bands match classification (strict; advisory by declaration)" \
    python3 scripts/check_bands_match_classification.py --strict
  [ -f scripts/test_cerra_reducer.py ] && run_gate "D#68" \
    "CERRA reducer" \
    python3 scripts/test_cerra_reducer.py
  [ -f scripts/test_numeric_hygiene_is_value_preserving.py ] && run_gate "D#69" \
    "numeric hygiene is value-preserving" \
    python3 scripts/test_numeric_hygiene_is_value_preserving.py
  # ── D#70..D#73, wired 2 October 2026 ─────────────────────────────────
  # These four surfaced only once E18's detector stopped counting LANDING
  # SCRIPTS as runners. Each had been invoked once, by hand, by the land_*.sh
  # that introduced it, and never again -- which is why E18 read 4 and not 6.
  # All four pass under --strict today (1s, 1s, 1s, 36s), so all four are
  # wired BLOCKING; a guard that passes has no silence to declare.
  [ -f scripts/check_component_names.py ] && run_gate "D#70" \
    "component names" \
    python3 scripts/check_component_names.py --strict
  [ -f scripts/check_normaliser_contract.py ] && run_gate "D#71" \
    "normaliser contract" \
    python3 scripts/check_normaliser_contract.py --strict
  [ -f scripts/check_r_base_field_reads.py ] && run_gate "D#72" \
    "R_base field reads" \
    python3 scripts/check_r_base_field_reads.py --strict
  [ -f scripts/check_register_serialisation.py ] && run_gate "D#73" \
    "register serialisation" \
    python3 scripts/check_register_serialisation.py --strict
  [ -f scripts/check_published_counts_match_data.py ] && run_gate "D#66" \
    "published counts match the register (BLOCKING — passes today)" \
    python3 scripts/check_published_counts_match_data.py --all
fi

# D#57 — Doctrine reproduce block (NEW, 28 September 2026)
# Repo-wide, not per-country, so it runs once whatever the slug. A FINDING or
# RESULT asserts something about the estate or about a source; without a way to
# re-derive it, it is a claim. Three false claims were made to the flag officer
# in one session, two of which he caught — doctrine/DISCIPLINE_the_claim_gate.md.
# It carries a declared baseline of the records that predate the rule, fails on
# any NEW record without a block and on any growth in the backlog, and the
# baseline may only fall. It is NOT advisory: a gate on diligence that does not
# block is the shape §7.8 names.
if [ -f scripts/check_doctrine_has_reproduce.py ]; then
  run_gate "D#57" "doctrine records carry a reproduce block" \
    python3 scripts/check_doctrine_has_reproduce.py
fi

# D#30 — Required-files presence (NEW, KB §93 / BPG Part LX)
# Runs first because if any country is missing required files, all subsequent
# gates that try to load those files will produce noise (file-not-found errors
# masquerading as content/schema failures).
if [ -f scripts/check_required_files.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#30" "required-files presence" \
      python3 scripts/check_required_files.py "$SLUG" $STRICT_FLAG
  else
    run_gate "D#30" "required-files presence (all 39)" \
      python3 scripts/check_required_files.py $STRICT_FLAG
  fi
fi

# D#3 — Inline JS parse-check
if [ -f scripts/check_inline_js_parse.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#3" "inline JS parse-check" \
      python3 scripts/check_inline_js_parse.py "$SLUG" $STRICT_FLAG
  else
    run_gate "D#3" "inline JS parse-check (all)" \
      python3 scripts/check_inline_js_parse.py $STRICT_FLAG
  fi
fi

# D#14 + D#15 + D#56 — validate-schema.py
if [ -n "$SLUG" ] && [ -f "$SLUG/ssi-data.json" ]; then
  run_gate "D#14/15/56" "schema + fleet-floor + country-config" \
    python3 scripts/validate-schema.py "$SLUG/ssi-data.json"
elif [ -z "$SLUG" ]; then
  run_gate "D#14/15/56" "schema + fleet-floor + country-config (all)" \
    python3 scripts/validate-schema.py --all
fi

# D#16 — page-ID parity (NEW Session 32)
if [ -n "$SLUG" ]; then
  run_gate "D#16" "page-ID parity vs canonical" \
    python3 scripts/check_page_ids.py "$SLUG" $STRICT_FLAG
else
  run_gate "D#16" "page-ID parity (all countries)" \
    python3 scripts/check_page_ids.py --all $STRICT_FLAG
fi

# D#17 — substation schema + variance (NEW Session 32)
if [ -n "$SLUG" ]; then
  run_gate "D#17" "substation schema + variance" \
    python3 scripts/check_substation_schema.py "$SLUG" $STRICT_FLAG
else
  run_gate "D#17" "substation schema + variance (all)" \
    python3 scripts/check_substation_schema.py --all $STRICT_FLAG
fi

# D#18 — nav.js slug parity (NEW Session 32)
if [ -n "$SLUG" ]; then
  run_gate "D#18" "nav.js slug parity" \
    python3 scripts/check_nav_slug.py "$SLUG" $STRICT_FLAG
else
  run_gate "D#18" "nav.js slug parity (all)" \
    python3 scripts/check_nav_slug.py $STRICT_FLAG
fi

# D#19 — currency leakage (NEW Session 32)
if [ -n "$SLUG" ]; then
  run_gate "D#19" "currency leakage (non-eurozone)" \
    python3 scripts/check_currency_leakage.py "$SLUG" $STRICT_FLAG
else
  run_gate "D#19" "currency leakage (all non-eurozone)" \
    python3 scripts/check_currency_leakage.py $STRICT_FLAG
fi

# D#20 — country-config edition_anchor_month_offset range [1, 12] (NEW post-§72.10)
# Catches the IS+KR misalignment that produced "Edition 07" instead of "02".
if [ -n "$SLUG" ]; then
  run_gate "D#20" "edition_anchor_month_offset range" \
    python3 scripts/check_edition_offset.py "$SLUG" $STRICT_FLAG
else
  run_gate "D#20" "edition_anchor_month_offset range (all)" \
    python3 scripts/check_edition_offset.py $STRICT_FLAG
fi

# D#21 — Content leakage (cross-country proper-noun contamination, post-CR S33B)
if [ -f scripts/check_content_leakage.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#21" "content leakage (cross-country)" \
      python3 scripts/check_content_leakage.py "$SLUG" $STRICT_FLAG
  else
    run_gate "D#21" "content leakage (all)" \
      python3 scripts/check_content_leakage.py $STRICT_FLAG
  fi
fi

# D#26 — Map aesthetic (two-axis offshore clip, post-Korea/Israel S36/S37)
# v2: per-feature centroid (Axis 1) + per-ring vertex envelope (Axis 2, NEW)
if [ -f scripts/check_map_aesthetics.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#26" "map aesthetic (two-axis offshore clip)" \
      python3 scripts/check_map_aesthetics.py "$SLUG"
  else
    run_gate "D#26" "map aesthetic (all with bounds.json)" \
      python3 scripts/check_map_aesthetics.py --all
  fi
fi

# D#27 — Substation sub-dict completeness (stub-class defect, post-IL S35)
# Catches socio_economic/graph_topology/seismic/markov stubs that render blank.
if [ -f scripts/check_socio_economic_completeness.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#27" "substation sub-dict completeness" \
      python3 scripts/check_socio_economic_completeness.py "$SLUG"
  else
    run_gate "D#27" "substation sub-dict completeness (all)" \
      python3 scripts/check_socio_economic_completeness.py --all
  fi
fi

# D#28 — Power-line geometry richness (post-Session 38)
# Catches the LT/JP/TR/US/IE chord-only rendering class. New onboardings via
# the proper d05_osm Overpass `out geom` path will always PASS. Legacy JP/TR/US
# fail until their offline OSM PBF re-ingestion lands — runs non-strict so the
# legacy fails don't block other countries' deploys.
if [ -f scripts/check_line_geometry.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#28" "power-line geometry richness" \
      python3 scripts/check_line_geometry.py "$SLUG" $STRICT_FLAG
  else
    run_gate "D#28" "power-line geometry richness (all)" \
      python3 scripts/check_line_geometry.py --all
  fi
fi

# D#29 — R3_C_mult per-substation variance (post-Session 100 / KB §78)
# Catches the DK/EE/GL/LV/LT discrete-clustering defect where regional socio-
# economic data is applied uniformly to all substations in a region, producing
# 4-5 discrete R3 values that break Section B.2 tier display.
# Runs NON-STRICT. THE FIGURE HERE WAS STALE AND IS CORRECTED (E311,
# 12 October 2026): it read "currently 19 of 39 countries fail"; measured today
# the gate reports 28 PASS, 3 WARN, 8 FAIL — france, germany, italy, japan,
# portugal, spain, uk, us. Seven of the eight store a single value; the uk
# fails at 2.6 per cent, 1,534 distinct values over 59,744 records, not 0.0.
# B.2 still renders correctly thanks to country-config quartile-bucket
# calibration from hotfix #1.
#
# THE CAUSAL CLAIM IN THIS BLOCK IS THE RIGHT ONE and the one in the D#29 case
# of advisory_ok() above was backwards: "regional socio-economic data applied
# uniformly to all substations in a region" is exactly what E311 reproduces —
# enrich_esg_gaps.py's round(1.0 - v_socio * 0.15, 4), on 95.7 per cent of the
# uk and 81.3 per cent of the us. The sentence "future country onboardings via
# score-country.py det_var pattern will PASS by construction" is kept, because
# it is consistent with the measurement: det_var is per-substation and produces
# variance — it just produced none of the values the estate now publishes.
# Discipline #29 serves as a health metric pre-flight, not a deploy blocker,
# until pipeline-layer cleanup completes.
if [ -f scripts/check_r3_variance.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#29" "R3_C_mult variance (strict; advisory by declaration)" \
      python3 scripts/check_r3_variance.py "$SLUG" --strict
  else
    run_gate "D#29" "R3_C_mult variance (all, strict; advisory by declaration)" \
      python3 scripts/check_r3_variance.py --all --strict
  fi
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════"

# ─── D#36: cross-border enforcement ────────────────────────────────────────
# Wired 25 September 2026. It was never wired before. The gate existed, carried
# a documented regression history, and had removed 22,358 substations in June —
# and nothing ever called it. It also failed open: shapely missing meant every
# country SKIPPED, skipped counted as not-violating, and exit 0.
#
# v2 asks the question v1 could not: not "is this inside my own polygon?" but
# "is it inside ANOTHER STATE?". Exclusivity carries no tolerance — no distance
# makes being in another country acceptable. It fails closed: a country that
# cannot be evaluated is a failure, not a skip.
# D#76 — the metric registry agrees with the MASTER formula construct.
#
# D#75 checks the registry against the ENGINE: that its intra-weights match
# INTRA_WEIGHTS. That passed all day on 3 October while FOURTEEN OF TWENTY METRIC
# NAMES disagreed with the authority of record -- the arithmetic spine was gated
# and the metric identities were not.
#
# The authority is SSI_FORMULA_CONSTRUCT_MASTER.md, 28 September 2026, which lives
# in a connected document folder and not in this repository, so this gate reads a
# frozen extract and re-hashes the live master only when it is reachable. Where the
# two disagree about WHAT A METRIC IS, the master wins. E72.
if [ -f scripts/check_registry_against_master.py ]; then
  run_gate "D#76" "metric registry agrees with the MASTER construct" \
    python3 scripts/check_registry_against_master.py
fi

# D#75 — the metric registry agrees with the engine it is a registry OF.
#
# This is `_registry_selfcheck()`, recovered. It lived in
# scripts/pipeline/ingestion/components.py from 20 August 2026 and was deleted as
# collateral of bf3ec3e3, a REVERT of a soft_clip correction. Nobody decided to
# delete it. Its own stated reason for existing: "A registry that drifts from
# INTRA_WEIGHTS would let a component roll up from the wrong metric set --
# silently, and in the direction nobody checks."
#
# It needs no data and no network, so it runs for every slug and for --all. It
# also enforces the rule the predecessor lacked: a construct with no cited source
# is a blocker, and every declared proxy and every withdrawn quantity must carry
# its reason and its date.
if [ -f scripts/check_metric_registry.py ]; then
  run_gate "D#75" "metric registry agrees with engine INTRA_WEIGHTS" \
    python3 scripts/check_metric_registry.py
fi

if [ -f scripts/check_cross_border_v2.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#36" "cross-border (inside another state?)" \
      python3 scripts/check_cross_border_v2.py "$SLUG" --strict
  else
    run_gate "D#36" "cross-border (all, inside another state?)" \
      python3 scripts/check_cross_border_v2.py --all --strict
  fi
fi

if [ "$LENIENT" -eq 1 ]; then
  echo ""
  echo "⚠  RAN WITH --lenient. Child gates did not enforce. This authorises nothing."
fi
# ── E18, 8 October 2026: two guards that nothing ran ────────────────────────
# Queue B2 asks, for each checker no runner invokes: wire it, or retire it with
# a reason. These two are wired. The other four declare their reason in their
# own docstring, which scripts/ssi_tracker_state.py now reads - see E18 there.
#
# D#77 and D#78, not 75 and 76: those two are already taken by the metric
# registry gates above. Measured while wiring these: the run_gate numbers in
# this file ALREADY repeat - 3, 16-21, 26-28 and others each appear twice - so
# the inventory is not a unique key today. That is not this landing's to fix,
# but it is why these two were checked against the file rather than assumed.
#
# D#78 is wired WITH --strict and DECLARED ADVISORY in is_advisory() above.
#
# The first version of this block wired it non-strict instead, and argued for
# that: 11 of 23 NUTS-coded fleets disagree, strict would turn CI red on eleven
# pre-existing findings, so pass no flag and let the guard report. The landing
# preamble's own land_check_gate_silences REFUSED it, and it was right. Those
# are two different things:
#
#   non-strict in the argv  - the gate cannot fail, and NOTHING RECORDS THAT.
#                             The silence is on no register and no reason is
#                             attached to it anywhere.
#   --strict + is_advisory  - the gate runs at full strength, reports its
#                             eleven findings every run, does not block, and
#                             the silence sits on the register with its reason
#                             and its promotion condition.
#
# The second is what D#67 did on 2 October, in its own words: "declared here
# rather than invoked without --strict, because a silence in the argv is on no
# register at all." The conclusion - do not turn CI red on eleven findings this
# landing does not rule on - was correct; the mechanism was wrong.
[ -f scripts/test_the_prose_anchor_matcher.py ] && run_gate "D#77" \
  "prose-anchor matcher regression (the four historical anchor failures)" \
  python3 scripts/test_the_prose_anchor_matcher.py
[ -f scripts/check_region_name_matches_its_code.py ] && run_gate "D#78" \
  "region NAME names the unit its CODE says (advisory by declaration)" \
  python3 scripts/check_region_name_matches_its_code.py --strict

if [ "$ADVISORY_WARNS" -gt 0 ]; then
  echo "⚠  ${ADVISORY_WARNS} advisory gate(s) reported issues: ${ADVISORY_GATES[*]}"
fi
if [ "$TOTAL_FAILS" -eq 0 ]; then
  if [ "$LENIENT" -eq 1 ]; then
    echo "✗ no blocking failures, but --lenient means nothing was enforced — NOT authorised"
    exit 1
  fi
  echo "✓ ALL GATES PASSED — deploy authorized"
  exit 0
else
  echo "✗ ${TOTAL_FAILS} GATE(S) FAILED: ${FAILED_GATES[*]}"
  echo ""
  if [ "$REPORT_ONLY" -eq 1 ]; then
    echo "(--report-only: not blocking)"
    exit 0
  fi
  echo "REMEDIATION:"
  echo "  Review each FAIL above. Re-run individual gate scripts with --strict to see details."
  echo "  Do NOT proceed with deploy until all gates green."
  exit 1
fi
