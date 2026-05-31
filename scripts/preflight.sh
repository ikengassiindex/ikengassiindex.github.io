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
#   D#56  — Fleet-size floor (KB §56 stub-deploy regression)          [validate-schema.py]
# ════════════════════════════════════════════════════════════════════════════

set -uo pipefail
cd "$(dirname "$0")/.."

SLUG=""
STRICT_FLAG=""
REPORT_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT_FLAG="--strict" ;;
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
    echo "  ✗ FAIL (exit=$rc)"
    TOTAL_FAILS=$((TOTAL_FAILS + 1))
    FAILED_GATES+=("$name")
  fi
}

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

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════"
if [ "$TOTAL_FAILS" -eq 0 ]; then
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
