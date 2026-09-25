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
    # D#29: per-substation R3 variance. Pipelines onboarded through
    # score-country.py's det_var pattern have a systemic discrete-R3 weakness;
    # B.2 still renders correctly via country-config quartile bucketing. Health
    # metric until the pipeline-layer cleanup lands.
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
# Runs NON-STRICT — currently 19 of 39 countries fail (legacy digital-twin
# pipelines have systemic discrete-R3 weakness; B.2 still renders correctly
# thanks to country-config quartile-bucket calibration from hotfix #1).
# Future country onboardings via score-country.py det_var pattern will PASS
# by construction. Discipline #29 serves as a health metric pre-flight, not
# a deploy blocker, until pipeline-layer cleanup completes.
if [ -f scripts/check_r3_variance.py ]; then
  if [ -n "$SLUG" ]; then
    run_gate "D#29" "R3_C_mult variance (non-strict)" \
      python3 scripts/check_r3_variance.py "$SLUG"
  else
    run_gate "D#29" "R3_C_mult variance (all, non-strict)" \
      python3 scripts/check_r3_variance.py --all
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
