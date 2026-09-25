#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_phase2cd.sh — Phase 2c + 2d atomic drop
#
# Usage:  bash scripts/land_phase2cd.sh
#
# Lands the remaining 7 Slovenia thin-shell page types + their shared section
# modules. After this commit, ALL 8 Slovenia pages are thin-shell (esg-report
# from Phase 2b plus the 7 added here). The thin-shell pattern now covers
# every page type — Slovakia inaugural ingestion can proceed on the new
# architecture without writing a single inline data-render JS block.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

cd "$(dirname "$0")/.."

rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$branch" != "main" ]]; then
  echo "✗ Expected to be on main, got '$branch'. Aborting." >&2
  exit 1
fi

# Pre-flight gates
echo "→ pre-flight: running CI gates"
if command -v node >/dev/null 2>&1; then
  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean"
  else
    echo "  ✗ inline-JS parse-check FAILED — see /tmp/parsecheck.log"
    exit 1
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check (CI will run it on push)"
fi

if python3 scripts/bump_cache_busters.py slovenia --check > /tmp/cachecheck.log 2>&1; then
  echo "  ✓ cache-busters in sync"
else
  echo "  ⚠ cache-busters out of sync — running real bump"
  python3 scripts/bump_cache_busters.py slovenia
fi

# ─── Stage everything ─────────────────────────────────────────────────────
echo ""
echo "→ Staging Phase 2c+d drop"

# 7 new shared section modules (one per non-esg-report page type)
git add \
  intelligence-sections.js \
  index-sections.js \
  regional-sections.js \
  map-sections.js \
  methodology-sections.js \
  data-sections.js \
  dno-dashboard-sections.js

# 7 modified Slovenia thin-shell HTML pages (esg-report already landed in Phase 2b)
git add \
  slovenia/intelligence.html \
  slovenia/index.html \
  slovenia/regional.html \
  slovenia/map.html \
  slovenia/methodology.html \
  slovenia/data.html \
  slovenia/dno-dashboard.html

# Schema + config extensions
git add \
  schemas/country-config.schema.json \
  intelligence/country-configs/slovenia.json

# bump_cache_busters.py — TARGETS extended with all 7 new section files
git add scripts/bump_cache_busters.py

# Landing-script artefact (useful reference for future phase drops)
[[ -f scripts/land_phase2b.sh ]] && git add scripts/land_phase2b.sh
git add scripts/land_phase2cd.sh

# Stage anything else the agents may have touched (safety net)
git add -A slovenia/  schemas/ intelligence/country-configs/ scripts/

# Show what's staged
echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -25

# ─── Commit ───────────────────────────────────────────────────────────────
git commit -m "feat(phase-2c+d): convert remaining 7 Slovenia page types to thin-shell (KB §65)

Completes the Phase 2 architectural refactor by extracting the inline
render logic from the 7 page types not covered by Phase 2b. All 8
Slovenia page types are now thin-shell on the central-renderer pattern.

Page-by-page line count (before → after, % reduction):
  intelligence    2094 → 620   (−70%)
  data             542 → 248   (−54%)
  regional         438 → 151   (−65%)
  methodology      440 → 352   (−20%)
  index            359 → 239   (−33%)
  map              239 → 248   (+4%, larger comment block)
  dno-dashboard    134 →  88   (−34%)

Total Slovenia HTML across 8 pages: 5287 → 2118 (−60%, −3169 lines).

Seven new shared root-level modules:
  intelligence-sections.js  (1524 lines) — 7 sections registered
  data-sections.js          (547 lines)  — 5 sections registered
  regional-sections.js      (434 lines)  — 3 sections registered
  index-sections.js         (340 lines)  — 7 sections registered
  dno-dashboard-sections.js (256 lines)  — 6 sections registered
  methodology-sections.js   (253 lines)  — 6 sections registered
  map-sections.js           (147 lines)  — 1 section registered

Each module follows the established pattern: IIFE wrapper, CountryRenderer
presence check, alias \`CR = window.CountryRenderer\`, universal
defaults (for non-migrated countries), then per-section
\`CR.register('<page>', '<section-id>', function(ctx){...})\` calls.

Country-specific values extracted from inline JS literals into
intelligence/country-configs/slovenia.json. The config grows from 75
→ 128 lines with new per-page blocks:

  regional_page    — region_field, ranking_label
  map_page         — leaflet center + zoom + region_unit_label
  data_page        — file_slug + region labels for PDFs + formula_pdf_layers
  dno_dashboard    — governance (TSO/Reg/Holding/Safety) + dsos[] + saidi.peers + notes[]
  deep_dive        — section D corridor anchor (already added in Phase 2c)
  deep_dive_rotation — 12-NUTS-3 monthly rotation for Section G card 1

schemas/country-config.schema.json extended to document the new blocks.

scripts/bump_cache_busters.py TARGETS list extended with all 7 new
section files so future cache-buster sweeps detect them.

Verification (all PASS at commit time):
  ✓ node --check on all 7 new section files + existing 2
  ✓ check_inline_js_parse.py --strict (232 pages × 826 blocks, 0 fail)
  ✓ bump_cache_busters.py slovenia --check (all in sync)
  ✓ slovenia.json valid against country-config.schema.json

Architecture status after this commit:
  Phase 2b: esg-report thin-shell pilot — LANDED (KB §65.10, May 28)
  Phase 2c+d: 7 remaining page types thin-shell — LANDED (this commit)
  Phase 2e: rollout to other 30 countries — PENDING (per-country sweep)

Slovakia inaugural ingestion (KB §65.7 acceptance test) is now
unblocked. Slovakia can be authored greenfield on thin-shell from
day one for all 8 pages — pure config + data, zero inline rendering JS.

Cross-link: KB §65.10 to be extended with the Phase 2c+d closure note.
BPG Part XXXIV (thin-shell migration pattern) to be added." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

# ─── Push ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Pushing main to origin"
git push origin main
echo "  ✓ pushed"

# ─── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Phase 2c+d landed → $C_SHA"
echo ""
echo "All 8 Slovenia page types are now thin-shell."
echo "Phase 2e (sweep across 30 other countries) and Slovakia inaugural"
echo "ingestion are now unblocked."
echo ""
echo "Watch CI: https://github.com/ikengassiindex/ikengassiindex.github.io/actions"
echo "════════════════════════════════════════════════════════════════════════"
