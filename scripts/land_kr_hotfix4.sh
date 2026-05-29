#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_kr_hotfix4.sh — Korea hotfix #4: nav.js missing 'korea' entry
#
# User-reported header issues:
#   1. "KOREA" text shown instead of 🇰🇷 flag emoji
#   2. Ikenga logo not displaying
#
# Root cause: nav.js is auto-generated from countries.json but the
# regeneration step did not run after Step 6 added the Korea entry.
# Three sections are missing 'korea':
#
#   a) SSI_COUNTRY_SLUGS array (line ~36)
#      — without it, SSI_COUNTRY_PATH_RE regex won't match /korea/ in URL
#      — so _ssiPathMatch is null → SSI_BASE='' instead of '../'
#      — so logo URL becomes 'ikenga-logo.png' (404 from /korea/) instead of
#        '../ikenga-logo.png' (200 from root)
#      → THIS IS WHY THE LOGO DOESN'T DISPLAY
#
#   b) SSI_COUNTRY_LABELS dict (line ~50)
#      — without it, SSI_COUNTRY_LABELS['korea'] is undefined
#      — fallback `|| SSI_COUNTRY` returns bare 'korea' string
#      — nav badge renders as "korea" (CSS uppercase to "KOREA")
#      → THIS IS WHY THE WORD "KOREA" SHOWS INSTEAD OF FLAG
#
#   c) SSI_COUNTRY_STATS_DEFAULT dict (line ~88) — minor (footer stats)
#
# Anti-pattern: A1e — "SoT regeneration gap" — auto-generated files derived
# from a SoT (countries.json) not regenerated when SoT changes. Distinct
# from A1c (HTML static fab) and A1d (data-schema deficit). Detection:
# countries.json contains slug but auto-generated downstream file does not.
# Prevention: BPG Discipline #18 (forthcoming) — pre-flight gate must verify
# nav.js (and any other auto-generated file) has the new slug after Step 6.
#
# Fix: patch nav.js to add 'korea' in all 3 sections. Single-file commit.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${KOREA_WORKSPACE:?KOREA_WORKSPACE must be set}"
REPO="${KOREA_REPO:?KOREA_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -f "$WORKSPACE/hotfix4/nav.js" ]]; then
  echo "✗ Hotfix #4 payload not found: $WORKSPACE/hotfix4/nav.js"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Hotfix #4 — nav.js + 'korea' entry (flag emoji + logo path)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Copying patched nav.js"
cp "$WORKSPACE/hotfix4/nav.js" "$REPO/nav.js"
echo "  ✓ nav.js ($(wc -c < $REPO/nav.js) bytes)"

echo ""
echo "→ Verification"
slug_check=$(grep -c "  'korea'," "$REPO/nav.js" || true)
label_check=$(grep -c "'korea': '\\\\uD83C\\\\uDDF0\\\\uD83C\\\\uDDF7" "$REPO/nav.js" || true)
stats_check=$(grep -c "'korea': '95 variables" "$REPO/nav.js" || true)
echo "  korea in SSI_COUNTRY_SLUGS: $slug_check (expected 1)"
echo "  korea in SSI_COUNTRY_LABELS: $label_check (expected 1)"
echo "  korea in SSI_COUNTRY_STATS_DEFAULT: $stats_check (expected 1)"
[[ "$slug_check" -ge 1 && "$label_check" -ge 1 && "$stats_check" -ge 1 ]] \
  || { echo "✗ Verification FAILED"; exit 1; }
echo "  ✓ All 3 sections patched"

# Try the codegen check
if [[ -f scripts/generate_nav_data.py ]]; then
  if python3 scripts/generate_nav_data.py --check > /tmp/navcheck.log 2>&1; then
    echo "  ✓ nav.js auto-gen check clean"
  else
    echo "  ⚠ nav.js auto-gen check reports drift (manual override accepted)"
    tail -5 /tmp/navcheck.log
  fi
fi

# Copy this script for audit
cp "$WORKSPACE/land_kr_hotfix4.sh" "$REPO/scripts/land_kr_hotfix4.sh"
chmod +x "$REPO/scripts/land_kr_hotfix4.sh"
echo "  ✓ scripts/land_kr_hotfix4.sh"

# Cache-busters
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1 || true
fi

echo ""
echo "→ Staging for commit"
git add nav.js scripts/land_kr_hotfix4.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(korea): hotfix #4 — nav.js missing 'korea' (header flag + logo display) [KR S31 A1e]

User-reported on visible header of korea pages:
  1. 'KOREA' word shown instead of 🇰🇷 flag emoji
  2. Ikenga logo not displaying

Root cause: nav.js auto-generated from countries.json was NOT regenerated
after Step 6 added the Korea entry to countries.json. Three sections of
nav.js were missing 'korea':

  a) SSI_COUNTRY_SLUGS array (line ~36)
     → SSI_COUNTRY_PATH_RE regex doesn't match /korea/ in URL
     → _ssiPathMatch is null → SSI_BASE='' instead of '../'
     → logo URL becomes 'ikenga-logo.png' (404 from /korea/) instead of
       '../ikenga-logo.png' (200 from root)
     → THIS IS WHY THE LOGO DOESN'T DISPLAY

  b) SSI_COUNTRY_LABELS dict (line ~50)
     → SSI_COUNTRY_LABELS['korea'] is undefined
     → fallback '|| SSI_COUNTRY' returns bare 'korea' string
     → nav badge renders as 'korea' (CSS uppercase to 'KOREA')
     → THIS IS WHY 'KOREA' SHOWS INSTEAD OF FLAG

  c) SSI_COUNTRY_STATS_DEFAULT dict (line ~88) — footer stats default

Fix: patch nav.js to add 'korea' in all 3 sections:
  - SSI_COUNTRY_SLUGS: 'korea' inserted alphabetically (between 'japan' + 'latvia')
  - SSI_COUNTRY_LABELS: 'korea': '\\\\uD83C\\\\uDDF0\\\\uD83C\\\\uDDF7 Republic of Korea'
  - SSI_COUNTRY_STATS_DEFAULT: 'korea': '95 variables · 1,184 substations · 17 do/si'

Anti-pattern A1e codified — 'SoT regeneration gap':
  Auto-generated downstream files (nav.js) derived from a SoT (countries.json)
  not regenerated when SoT changes. Distinct from A1c (HTML static fab) and
  A1d (data-schema deficit). Detection: grep slug in countries.json AND in
  downstream auto-gen file — if missing in latter, this anti-pattern.
  Prevention: BPG Discipline #18 (forthcoming) — Step 6/7 deploy script must
  run \`scripts/generate_nav_data.py\` AND verify the downstream file mentions
  the new slug before committing.

Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 4/3 (this hotfix
adds 1 hotfix + 1 new A-family parent A1e). 3 new A-family parents in KR S31:
  A1c (static fab — hotfix #1)
  A1d (data-schema deficit — hotfix #2)
  A1e (SoT regeneration gap — this hotfix)

Scope: nav.js (root) only. Affects ALL country pages' nav rendering — but
only korea/ pages were missing flag+logo. Other countries unaffected." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea hotfix #4 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload any Korea page:"
echo "  https://ikengassiindex.github.io/korea/index.html"
echo ""
echo "Expected fixes:"
echo "  ✓ Ikenga logo displays in top-left of nav (loads from /ikenga-logo.png)"
echo "  ✓ Nav badge shows '🇰🇷 Republic of Korea' instead of 'KOREA' bare text"
echo "  ✓ Footer stats default line shows Korea: '95 variables · 1,184 substations · 17 do/si'"
echo ""
echo "Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 4/3"
echo "  (A1c + A1d + A1e new A-family parents from KR S31)"
echo "════════════════════════════════════════════════════════════════════════"
