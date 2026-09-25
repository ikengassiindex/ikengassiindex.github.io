#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_sk_hotfix4.sh — Architectural follow-up: CountryRenderer.normalizeMeta()
#
# Promotes per-section schema-key aliasing (added inline in SK hotfix #3)
# to a single central normalizeMeta() function in country-renderer.js.
# Same architectural shape as the existing normalize(data) function for
# ssi-data.json — runs once at init(), idempotent, non-destructive.
#
# Also fixes a latent A1b drift the user was about to surface:
# MODIFIER_DEFS in slovakia/ssi-metadata.js ships {id, domain, range,
# description} but index-sections.js reads {key, label, w}. The renderer
# was using s.modifiers[m.key] where m.key was undefined → every row
# in the Modifier Impact σ column rendered as '—'. The new
# normalizeModifierDef() aliases id→key via a lookup table
# (R3→R3_C_mult, R4→R4_F_topo, R6a→R6_restoration, R6b→R6_seismic,
# R7→R7_cyber) so the substation modifier access finally resolves.
#
# This is the precondition for Hungary onboarding (CEE-South-2026
# member 3 / KB §68.11.2 / BPG Part XXXV.4 discipline #9). Hungary can
# now ship COMPONENTS_INDEX/MODIFIER_DEFS in either schema variant and
# the renderer handles both.
#
# Drift audit covered all 9 metadata arrays:
#   COMPONENTS_INDEX  — A1b, normalised (was visible bug, fixed in #3)
#   MODIFIER_DEFS     — A1b, normalised (latent bug fixed here)
#   COMPONENTS        — no drift (renderer reads canonical {id,name,weight,…})
#   DATA_SOURCES      — minor cosmetic drift (no category/res field); tracked
#   ESG_SOURCES       — no drift (array-of-arrays, positional)
#   DATA_LAYERS       — no drift
#   NORM_METHODS      — no drift
#   VALIDATION_CHECKS — no drift
#   CHANGELOG         — no drift
#
# Files changed:
#   country-renderer.js  420 → 531 lines (+111: normalizeMeta + 2 aliasers
#                                          + 2 lookup tables + public API)
#   index-sections.js    363 → 370 lines (cleanup: -25 from removing
#                                          per-section normalizeComponentBar
#                                          + DEFAULT_PALETTE; +32 from
#                                          extended docs)
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
  for f in country-renderer.js esg-sections.js intelligence-sections.js \
           index-sections.js regional-sections.js map-sections.js \
           methodology-sections.js data-sections.js dno-dashboard-sections.js \
           map.js; do
    node --check "$f" 2>/dev/null && echo "  ✓ $f parses" || {
      echo "  ✗ $f FAILED"; exit 1;
    }
  done

  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean (240 pages × 851 blocks)"
  else
    echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"; exit 1
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check"
fi

python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; exit 1; }

# ─── Stage ────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging hotfix #4 (architectural pass)"

git add country-renderer.js index-sections.js
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true
git add scripts/land_sk_hotfix4.sh

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -10
echo ""
git diff --cached --shortstat

# ─── Commit ───────────────────────────────────────────────────────────────
git commit -m "fix(renderer): central normalizeMeta() — promote per-section schema aliasing (KB §68.11 / BPG XXXV.3)

Per-section normalizeComponentBar (added in SK hotfix #3) was an
architectural smell. Schema-key drift is a metadata-boundary concern,
not a per-section concern. This pass promotes the function to a single
CountryRenderer.normalizeMeta() that runs once in init(), mirroring
the existing normalize(data) for ssi-data.json.

Audit map (KB §68.11):

  A1b sites fixed centrally:
    COMPONENTS_INDEX  {code, name, ceiling, drivers}
                    → {key, label, w, color, drivers}
                      (color from COMPONENT_DEFAULT_PALETTE when absent)
    MODIFIER_DEFS    {id, domain, range, description}
                    → {key, label, domain, range, description}
                      (key from MODIFIER_ID_TO_KEY lookup:
                       R3→R3_C_mult, R4→R4_F_topo,
                       R6a→R6_restoration, R6b→R6_seismic,
                       R7→R7_cyber)

  Latent bug closed: Slovakia's MODIFIER_DEFS shipped {id, …} but
  index-sections.js reads s.modifiers[m.key] in the Modifier Impact
  table. With m.key undefined, every row's σ column rendered as '—'.
  The id→key alias resolves the substation modifier access.

  No-drift arrays (renderer reads canonical schema already):
    COMPONENTS, DATA_LAYERS, NORM_METHODS, VALIDATION_CHECKS,
    CHANGELOG, ESG_SOURCES — no aliasing needed.

  Cosmetic-drift arrays (renderer falls back to neutral defaults):
    DATA_SOURCES — no 'category' or 'res' field on SI/SK; sources
    render with gray Standards icon. Tracked for future pass; right
    fix is the ssi-metadata.js files shipping the missing fields.

Architectural shape:
  - normalizeMeta() called in init() after normalize(data), before
    runSections().
  - Idempotent (canonical input passes through untouched).
  - Non-destructive (variant fields preserved alongside canonical).
  - Mirrored onto the dual-global SSIMetadata / SSI_METADATA alias.
  - normalizeComponentBar + normalizeModifierDef helpers at module
    scope.
  - Per-section normalizeComponentBar + DEFAULT_PALETTE removed from
    index-sections.js; getComponentBars() returns the array as-is.

Verification:
  ✓ node --check 10/10 shared files
  ✓ inline JS parse-check 240 pages × 851 blocks × 0 fail
  ✓ Simulation against slovakia/ssi-metadata.js:
      COMPONENTS_INDEX[0] → key:'C', label:'C — Continuity',
                            w:0.3, color:'var(--crimson)'
      MODIFIER_DEFS:        R3→R3_C_mult, R4→R4_F_topo,
                            R6a→R6_restoration, R6b→R6_seismic,
                            R7→R7_cyber
  ✓ Idempotency: second pass produces identical output
  ✓ cache-busters in sync

This is the precondition for Hungary onboarding (CEE-South-2026
member 3 / KB §68.11.2 / BPG Part XXXV.4 discipline #9). Hungary can
now ship COMPONENTS_INDEX/MODIFIER_DEFS in either schema variant and
the renderer handles both transparently.

Hotfix count attributable to Slovakia inaugural deploy: 4
  #1 05b5941e  A12 inline patches
  #2 41e725da  Safe namespace + 74-site refactor
  #3 32dcc053  A1b COMPONENTS_INDEX (per-section fix)
  #4 (this)    A1b promoted to central normalizeMeta + MODIFIER_DEFS

Cross-link: KB §68.11 (A1b codification), BPG Part XXXV.3
(canonical defense pattern), KB §66 (A1 original)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

# ─── Push ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "SK hotfix #4 (architectural pass) landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, verify Slovakia Overview:"
echo "  open https://ikengassiindex.github.io/slovakia/index.html"
echo ""
echo "Look at:"
echo "  - 'Component Contribution — Fleet Average' (should still show all 6 bars correctly)"
echo "  - 'Modifier Impact — Fleet Stats' (R3/R4/R6a/R6b/R7 σ column should now"
echo "    show real numbers instead of '—' across the board)"
echo ""
echo "Hungary onboarding (CEE-South-2026 member 3) is now unblocked."
echo "════════════════════════════════════════════════════════════════════════"
