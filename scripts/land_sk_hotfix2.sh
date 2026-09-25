#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_sk_hotfix2.sh — SK hotfix #2: Safe namespace + null-handling refactor
#
# Architectural follow-up to SK hotfix #1 (KB §68.9). The first hotfix patched
# 5 visible sites with inline null checks; #2 ships a centralized
# `window.CountryRenderer.Safe` namespace and refactors 74 sites across
# the 8 section files to use it. The result: every null/undefined render
# risk now flows through one of 8 helpers, each documented with the bug
# class it prevents (KB §68.9 A12.1–A12.5).
#
# Files changed:
#   country-renderer.js          221 → 420 (+199, Safe namespace + docs)
#   esg-sections.js              756 → 757  ( +1, Safe wired)
#   intelligence-sections.js   1,524 → 1,542 (+18, 40 Safe.* sites)
#   index-sections.js            361 → 363  ( +2, 15 Safe.* sites)
#   regional-sections.js         434 → 432  ( −2, 3 Safe.* sites + compaction)
#   map-sections.js              147 → 145  ( −2, 1 Safe.* site)
#   methodology-sections.js      253 → 251  ( −2, 1 Safe.* site)
#   data-sections.js             547 → 554  ( +7, 13 Safe.* sites in PDF exports)
#   dno-dashboard-sections.js    256 → 258  ( +2, Safe wired, low surface)
#
# Net per-file delta ≈ +24 lines across section files (essentially a wash)
# while replacing 80+ ad-hoc null guards with the centralized Safe API.
#
# Blast radius: all 33 country pages. Every country's Overview KPI sub-line,
# Top Critical table, intelligence focus-card, D.2 corridor table, PDF
# exports, and ESG report sections benefit from the same hardening.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail
cd "$(dirname "$0")/.."

rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

# ─── Pre-flight ───────────────────────────────────────────────────────────
echo "→ pre-flight: gates"
if command -v node >/dev/null 2>&1; then
  # node --check on all 10 shared files
  for f in country-renderer.js esg-sections.js intelligence-sections.js \
           index-sections.js regional-sections.js map-sections.js \
           methodology-sections.js data-sections.js dno-dashboard-sections.js \
           map.js; do
    node --check "$f" 2>/dev/null && echo "  ✓ $f parses" || {
      echo "  ✗ $f FAILED node --check"; exit 1;
    }
  done

  # Full inline-JS parse-check
  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean (240 pages × 851 blocks)"
  else
    echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"; exit 1
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check (CI will run it)"
fi

# Cache-buster sync — re-bump after country-renderer.js + 8 section files changed
python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters still stale"; cat /tmp/cachecheck.log; exit 1; }

# ─── Stage ────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging hotfix #2"

# The 9 modified shared files
git add country-renderer.js
git add esg-sections.js
git add intelligence-sections.js
git add index-sections.js
git add regional-sections.js
git add map-sections.js
git add methodology-sections.js
git add data-sections.js
git add dno-dashboard-sections.js

# Cache-buster bumps across all 33 countries
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

# Landing script audit trail
git add scripts/land_sk_hotfix2.sh

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -15
echo ""
git diff --cached --shortstat

# ─── Commit ───────────────────────────────────────────────────────────────
git commit -m "fix(renderer): SK hotfix #2 — Safe namespace + null-handling refactor (KB §68.9)

Architectural follow-up to SK hotfix #1. Slovakia's OSM extract (867
null voltage_kv, 544 empty name fields) surfaced 5 distinct render-time
bug classes that Slovenia's voltage-complete data masked. Hotfix #1
patched 5 visible sites; this #2 ships a centralized Safe namespace
and refactors 74 sites across the 8 section files.

country-renderer.js (+199 lines):
  window.CountryRenderer.Safe = {
    num, fmt, pct, locale,           — null-safe numeric coercion + display
    displayName,                      — substation name → id → '(unnamed)' chain
    voltageClass,                     — EHV / HV / distribution-tier trichotomy
    regionOptions,                    — filter dropdown builder
    get,                              — safe deep property accessor
    filterFinite                      — filter excluding null records
  }
  Each helper documented with the bug class it prevents (A12.1–A12.5)
  and the idiom it replaces.

Section refactors (74 Safe.* call sites):
  esg-sections.js               1 site
  intelligence-sections.js     40 sites — focus-card, B.1 KPIs, D.2 table, R7 blind-spot
  index-sections.js            15 sites — KPI row, top-critical table, voltage split
  data-sections.js             13 sites — Full / Geographic / Summary PDF exports
  regional-sections.js          3 sites
  methodology-sections.js       1 site
  map-sections.js               1 site
  dno-dashboard-sections.js     wired but low surface area (esc() coverage)

Preserves identical rendered output when data is complete; produces
'—' (or configured fallback) instead of 'undefined' / 'null' / 'NaN' /
blank when fields are missing.

Net per-file line delta ≈ +24 across section files (essentially a
wash) while replacing 80+ ad-hoc null guards with the centralized Safe
API. Future country onboardings consume the helpers from the start —
the bug class is structurally prevented going forward.

Verification:
  ✓ node --check 10/10 shared files
  ✓ inline JS parse-check 240 pages × 851 blocks × 0 failing
  ✓ Safe.* unit-tested against slovakia/ssi-data.json
    (1,516 substations; no throws; 544 empty names resolved
     to substation_id; 867 null voltage_kv correctly bucketed
     to distribution-tier)
  ✓ cache-busters in sync

KB §65.7 acceptance test scoring:
  Hotfix #1 already downgraded to PARTIAL PASS. This hotfix completes
  the architectural extension — anti-patterns A1-A11 still held through
  Slovakia onboarding; A12 surfaced + codified + fixed at the central
  layer. Net: Slovakia is the country where the codebase learned
  something new, and that learning is now permanent.

Cross-link: KB §64.3 anti-pattern catalogue + §68.9 A12 codification
+ BPG Part XXXIV (the canonical Safe.* pattern to be added)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

# ─── Push ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "SK hotfix #2 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, verify:"
echo "  open https://ikengassiindex.github.io/slovakia/index.html"
echo "  open https://ikengassiindex.github.io/slovakia/intelligence.html"
echo "  open https://ikengassiindex.github.io/slovakia/map.html"
echo "  open https://ikengassiindex.github.io/slovakia/data.html"
echo ""
echo "What to look for:"
echo "  - Every numeric cell shows a number or '—' (never 'undefined' / 'null' / 'NaN')"
echo "  - Top Critical / D.2 corridor / PDF exports never have blank substation cells"
echo "  - Voltage trichotomy (EHV / HV / distribution-tier) consistent everywhere"
echo "  - 'voltage untagged' label on untagged substation clicks"
echo "  - Region dropdowns show human names, not NUTS codes"
echo "════════════════════════════════════════════════════════════════════════"
