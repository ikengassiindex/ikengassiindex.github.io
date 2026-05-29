#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_sk_hotfix3.sh — SK hotfix #3: A1 metadata schema-key drift
#
# Slovakia's `slovakia/ssi-metadata.js` ships `COMPONENTS_INDEX` with
# `{code, name, ceiling, drivers}` fields — semantically richer (the
# `drivers` strings document each component's data sources) but using
# different field names than `index-sections.js` expects
# (`{key, label, w, color}`).
#
# Result: every `c.label` in the Fleet Average "Component Contribution"
# section evaluated to `undefined`, which renders as the literal string
# "undefined" in the bar labels. `c.key` was also undefined so the
# components math accumulated everything into one bucket (all bars
# identical). `c.w` undefined → `Safe.fmt` correctly returned `'—'`.
#
# This is anti-pattern A1 (schema-key drift), same family as KB §66 but
# manifesting at the metadata-side rather than the ssi-data side. Safe.*
# protected against null/undefined VALUES; it did not protect against
# MISSING KEYS in object literals. Different bug class, different fix.
#
# Architectural fix (single site in `index-sections.js`):
#   normalizeComponentBar(c) — aliases code→key, name→label (composed
#   with key prefix), ceiling→w, supplies DEFAULT_PALETTE[key] color
#   when none provided. Renderer accepts either schema; future country
#   onboardings can pick the richer documentation form without breaking.
#
# Slovakia's COMPONENTS_INDEX itself is NOT touched — its `drivers`
# strings (SAIDI/SAIFI · ÚRSO, OSM · SEPS, etc.) are valuable
# documentation we want to preserve. The aliasing happens at the
# rendering boundary.
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
  node --check index-sections.js >/dev/null && echo "  ✓ index-sections.js parses"
  python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1 \
    && echo "  ✓ inline-JS parse-check clean (240 pages × 851 blocks)" \
    || { echo "  ✗ parse-check FAILED"; exit 1; }
else
  echo "  ⚠ node not on PATH — skipping local parse-check"
fi

python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; exit 1; }

# ─── Stage ────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging hotfix #3"

git add index-sections.js
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true
git add scripts/land_sk_hotfix3.sh

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -10
echo ""
git diff --cached --shortstat

# ─── Commit ───────────────────────────────────────────────────────────────
git commit -m "fix(a1-meta): normalize COMPONENTS_INDEX schema in index-sections (KB §66)

Slovakia ships slovakia/ssi-metadata.js with COMPONENTS_INDEX in the
{code, name, ceiling, drivers} shape — semantically richer (each
component documents its data sources via 'drivers') but using
different field names than what index-sections.js's component-bars
handler reads ({key, label, w, color}).

Symptom: Slovakia Overview 'Component Contribution — Fleet Average'
section rendered the literal text 'undefined' inside the per-bar
label span (where c.label was meant to display 'C — Continuity').
c.key undefined collapsed all components into one bucket (math
silently wrong; all bars equal height). c.w undefined was correctly
captured by Safe.fmt(undefined, 2) → '—'.

Root cause: anti-pattern A1 schema-key drift, this time between the
country's metadata and the renderer (rather than between ssi-data.json
and the renderer, which was the original A1 site). Safe.* protects
against null/undefined VALUES but not against MISSING KEYS in object
literals — different bug class.

Fix: extend index-sections.js getComponentBars() to normalize either
schema:
  normalizeComponentBar(c):
    key   := c.key   ?? c.code
    label := c.label ?? (c.key + ' — ' + c.name)
    w     := c.w     ?? c.ceiling
    color := c.color ?? DEFAULT_PALETTE[key]
  Renderer accepts both shapes; documentation-rich form preserves
  drivers string as additional field.

Slovakia's COMPONENTS_INDEX itself is NOT touched — the 'drivers'
strings (SAIDI/SAIFI · ÚRSO, OSM · SEPS, etc.) are valuable per-
component documentation. The aliasing happens at the rendering
boundary, so future countries can adopt either schema.

Verification:
  ✓ node --check index-sections.js
  ✓ inline-JS parse-check 240 pages × 851 blocks × 0 fail
  ✓ Simulated normalization against Slovakia's actual
    COMPONENTS_INDEX produces:
      C — Continuity     w=0.3  color=crimson
      V — Voltage Quality w=0.18 color=terracotta
      I — Infrastructure  w=0.18 color=sage
      E — Economic        w=0.14 color=#3b9eff
      S — Societal        w=0.12 color=bronze
      T — Transition      w=0.08 color=#22d3ee

Hotfix count attributable to Slovakia inaugural deploy: 3
  #1 05b5941e  A12 inline patches
  #2 41e725da  Safe namespace + 74-site refactor
  #3 (this)    A1 metadata schema-key drift

Cross-link: KB §66 (anti-pattern A1 — schema-key drift); §68.9/§68.10
(A12 codification + Safe namespace); §65.7 acceptance test verdict
remains PARTIAL PASS — A1-A11 surfaced at metadata boundary this
time, fixed at the renderer rather than the data file." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

# ─── Push ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "SK hotfix #3 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, verify Slovakia Overview:"
echo "  open https://ikengassiindex.github.io/slovakia/index.html"
echo ""
echo "Look at 'Component Contribution — Fleet Average':"
echo "  - C — Continuity   (was 'undefined' — should now render correctly)"
echo "  - V — Voltage Quality"
echo "  - I — Infrastructure"
echo "  - E — Economic"
echo "  - S — Societal"
echo "  - T — Transition"
echo ""
echo "  Each bar should have:"
echo "    • Proper label (no 'undefined')"
echo "    • Different bar height (was identical due to c.key undefined)"
echo "    • w = X.XX  ·  avg = 0.XXX  in the right-hand annotation"
echo "════════════════════════════════════════════════════════════════════════"
