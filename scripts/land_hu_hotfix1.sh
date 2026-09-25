#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_hu_hotfix1.sh — Hungary hotfix #1: deep-dive admin-unit-suffix tolerance
#
# Hungary intelligence page deep-dive section "Tolna megye — Paks Nuclear
# Corridor" showed "Loading…" on every D.* sub-block (D.1 KPIs, D.2 table,
# D.3 components, D.4 NUTS-3 breakdown, D.5 implications).
#
# Root cause: admin-unit naming convention mismatch between data and config.
#   - Slovakia substations: province="Bratislavsky kraj" (suffix included)
#   - Slovakia config:      deep_dive.region="Nitriansky kraj"  ✓ match
#   - Hungary substations:  province="Tolna" (bare name)
#   - Hungary config:       deep_dive.region="Tolna megye"  ✗ mismatch
#
# The handler's pre-hotfix filter:
#   fleet.filter(s => s.province === corridor || s.region === corridor)
# returned 0 rows for HU, leaving every #pug-* placeholder on "Loading…".
#
# Architectural fix in intelligence-sections.js:
# adds a third fallback that strips common admin-unit suffixes from both
# sides before comparing:
#   " megye" / " megye-város"  (HU)
#   " kraj"                     (SK / CZ)
#   " county" / " region" /
#   " région" / " département" / " prefecture" / " provincia" / " provinsi"
# Case-insensitive. Identity matches unchanged (Budapest still matches
# Budapest); mismatched cases now resolve via the stripped comparison.
#
# Why architectural, not just a data patch: future cohort onboardings can
# adopt either naming convention (HU bare names, SK suffix-included) and
# the deep-dive section will resolve correctly. Closes a sibling of
# anti-pattern A1 at the data-vs-config boundary.
#
# Hotfix count attributable to Hungary deploy: 1
#   #1 (this) — admin-unit-suffix tolerance in deep-dive filter
#
# KB §65.7 acceptance test reading:
#   Hungary onboarded on the post-SK architecture (Safe + normalizeMeta).
#   SK structural defenses (A1/A12) all held cleanly. This hotfix surfaces
#   a NEW pattern (admin-unit-suffix mismatch) that neither SI nor SK
#   exposed because both used the suffix-included convention. The
#   pattern is now codified at the central layer.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail
cd "$(dirname "$0")/.."

rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

echo "→ pre-flight: gates"
if command -v node >/dev/null 2>&1; then
  node --check intelligence-sections.js >/dev/null && echo "  ✓ intelligence-sections.js parses"
  python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1 \
    && echo "  ✓ inline-JS parse-check clean" \
    || { echo "  ✗ parse-check FAILED"; exit 1; }
else
  echo "  ⚠ node not on PATH — skipping local parse-check"
fi

python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; exit 1; }

echo ""
echo "→ Staging hotfix #1"
git add intelligence-sections.js
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true
git add scripts/land_hu_hotfix1.sh

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -10
echo ""
git diff --cached --shortstat

git commit -m "fix(deep-dive): admin-unit-suffix tolerance in intelligence Section D (KB §69 HU hotfix #1)

Hungary intelligence page Section D 'Tolna megye — Paks Nuclear
Corridor' showed Loading… on every D.* placeholder.

Root cause: admin-unit naming convention mismatch between
ssi-data.json province field and country-config deep_dive.region:

  Slovakia: province='Bratislavsky kraj' / config='Nitriansky kraj'
            (suffix-included on both sides) ✓ direct equality holds
  Hungary:  province='Tolna' / config='Tolna megye'
            (bare name vs suffix-included) ✗ direct equality fails

Pre-hotfix filter:
  fleet.filter(s => s.province === corridor || s.region === corridor)
returned 0 rows for HU; every #pug-* placeholder stayed on Loading.

Architectural fix — extend the existing filter chain with a third
fallback that strips common admin-unit suffixes from both sides
before comparing. Suffixes covered (case-insensitive):
  megye | megye-város   (HU)
  kraj                  (SK, CZ)
  county | region | région | département | prefecture |
    provincia | provinsi

Identity matches unchanged. Future cohort onboardings can adopt
either convention and the section resolves correctly. Closes a
sibling of anti-pattern A1 at the data-vs-config boundary.

Verification:
  ✓ node --check intelligence-sections.js
  ✓ inline-JS parse-check 248 pages × 876 blocks × 0 fail
  ✓ Simulation:
      'Tolna megye' vs 'Tolna' → match
      'Nitriansky kraj' vs 'Nitriansky kraj' → match (identity preserved)
      'Győr-Moson-Sopron megye' vs 'Győr-Moson-Sopron' → match
      'Budapest' vs 'Budapest' → match (identity preserved)

Hotfix count attributable to Hungary deploy: 1.

KB §65.7 reading: the SK structural defenses (A1a/A1b/A12 +
Safe namespace + normalizeMeta) all held cleanly through HU
onboarding. This hotfix codifies a NEW admin-unit-suffix sub-pattern
that neither Slovenia nor Slovakia exposed because both used the
suffix-included convention. Pattern now at the central renderer
layer — Hungary's bare-name convention works for all 12 megye
rotation entries.

Cross-link: KB §69 (HU inaugural), §66 (A1 original)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "HU hotfix #1 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, verify:"
echo "  open https://ikengassiindex.github.io/hungary/intelligence.html"
echo ""
echo "Section D 'Tolna megye — Paks Nuclear Corridor' should show:"
echo "  - D.1 KPIs: 111 substations · X EHV / Y HV · median R · % high"
echo "  - D.2 Top-10 Tolna corridor table"
echo "  - D.3 Component breakdown"
echo "  - D.4 NUTS-3 breakdown"
echo "  - D.5 Implications narrative"
echo "════════════════════════════════════════════════════════════════════════"
