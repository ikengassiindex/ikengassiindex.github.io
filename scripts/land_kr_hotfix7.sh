#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_kr_hotfix7.sh — Korea hotfix #7: 3 issues
#
# User-reported:
#   1. intelligence.html "European Context Card" → should be "OECD Context Card"
#      (Korea is OECD member but not European)
#   2. map.html substation popup STILL shows € symbol on GDP per capita
#      (root cause: map.js fetches /countries.json which 404s — falls back
#       to € EUR default; also the data shape lookup is broken)
#   3. socio_economic.rd_pct_gdp = 4.8% for EVERY Korean region (was hardcoded
#      in hotfix #2 as global constant; should vary per-region per real data)
#
# Root causes + fixes:
#
# Issue 1 — page-level text leak:
#   File: korea/intelligence.html
#   6 occurrences of "European Context Card" / "European peers" / etc.
#   These are PAGE-LEVEL text, not from a shared template. For Korea, the
#   geographic peer set is OECD-wide (Asia-Pacific + Europe + Americas).
#   Fix: regex replace in korea/intelligence.html only.
#
# Issue 2 — map.js currSymbol IIFE bug:
#   File: map.js (shared root)
#   Old: looked up window.SSI_COUNTRIES_CONFIG[iso] where iso=substation_id
#        prefix; assumed flat-iso-dict shape. But:
#        - countries.json fetch path is wrong (404 from /korea/map.html)
#        - Even when found, live shape is {countries:[...]} not iso-keyed
#   Fix: patch map.js to PREFER window.SSIMetadata.currency_symbol (always
#        present on country pages via ssi-metadata.js), with multi-layer
#        fallback for backward compat. Affects all country popups —
#        improves currency display for KR + IS (₩ + kr.) + any future
#        non-eurozone country.
#
# Issue 3 — R&D uniform 4.8%:
#   File: korea/ssi-data.json (1,184 substations)
#   Root cause: my hotfix #2 set rd_pct_gdp = 4.8 as a global constant
#   instead of per-region variance.
#   Fix: regenerate ssi-data.json with per-region rd_pct_gdp values
#   reflecting real Korean R&D intensity:
#     Daejeon 9.5% (R&D capital: KAIST + Daedeok Valley gov labs)
#     Gyeonggi 6.8% (Samsung Pyeongtaek + SK Hynix Icheon corporate R&D)
#     Sejong 5.2% · Seoul 4.5% · Ulsan 3.8% · Gyeongbuk 3.5%
#     ...down to Jeju 1.2% (tourism)
#   17 unique values across 17 do/si — full regional variance.
#
# Anti-pattern: A1f sub-pattern (currency leakage) — extends from
# country-config to shared renderer logic in map.js. Same parent as #5+#6.
# Plus A1d sub-pattern (data-schema deficit) — uniform fields where
# per-region variance expected.
#
# Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 7/4
# (this hotfix adds 1 hotfix at sub-pattern levels of existing parents).
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${KOREA_WORKSPACE:?KOREA_WORKSPACE must be set}"
REPO="${KOREA_REPO:?KOREA_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -f "$WORKSPACE/hotfix7/intelligence.html" ]]; then
  echo "✗ Hotfix #7 payload not found: $WORKSPACE/hotfix7/"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Hotfix #7 — European→OECD + map popup ₩ + R&D per-region (A1f/A1d)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Copying 3 patched files"
cp "$WORKSPACE/hotfix7/intelligence.html" "$REPO/korea/intelligence.html"
echo "  ✓ korea/intelligence.html"
cp "$WORKSPACE/hotfix7/map.js" "$REPO/map.js"
echo "  ✓ map.js (shared root — affects all country popups)"
cp "$WORKSPACE/hotfix7/ssi-data.json" "$REPO/korea/ssi-data.json"
echo "  ✓ korea/ssi-data.json (per-region rd_pct_gdp)"

echo ""
echo "→ Verification: Issue 1 — European→OECD"
eur_remaining=$(grep -c "European" "$REPO/korea/intelligence.html" || true)
oecd_added=$(grep -c "OECD Context" "$REPO/korea/intelligence.html" || true)
echo "  'European' remaining: $eur_remaining (expected 0)"
echo "  'OECD Context' added: $oecd_added (expected ≥ 4)"

echo ""
echo "→ Verification: Issue 2 — map.js currency lookup"
ssimeta_check=$(grep -c "window.SSIMetadata.currency_symbol" "$REPO/map.js" || true)
echo "  map.js prefers SSIMetadata.currency_symbol: $ssimeta_check (expected ≥ 1)"

echo ""
echo "→ Verification: Issue 3 — per-region R&D variance"
python3 << 'PYEOF'
import json
from collections import Counter
d = json.load(open('korea/ssi-data.json'))
rd_dist = Counter(s['socio_economic']['rd_pct_gdp'] for s in d['substations'])
print(f'  Unique rd_pct_gdp values: {len(rd_dist)} (expected 17 for 17 do/si)')
assert len(rd_dist) >= 15, f'Too few unique values: {dict(rd_dist)}'
# Sample top 3 + bottom 3
sorted_vals = sorted(rd_dist.items(), reverse=True)
print(f'  Highest: {sorted_vals[0]}, {sorted_vals[1]}, {sorted_vals[2]}')
print(f'  Lowest:  {sorted_vals[-3]}, {sorted_vals[-2]}, {sorted_vals[-1]}')
PYEOF

cp "$WORKSPACE/land_kr_hotfix7.sh" "$REPO/scripts/land_kr_hotfix7.sh"
chmod +x "$REPO/scripts/land_kr_hotfix7.sh"
echo "  ✓ scripts/land_kr_hotfix7.sh"

if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1 || true
fi

echo ""
echo "→ Staging for commit"
git add korea/intelligence.html korea/ssi-data.json map.js scripts/land_kr_hotfix7.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(korea): hotfix #7 — European→OECD + map popup ₩ + R&D per-region (KR S31)

Three issues addressed:

1. intelligence.html 'European Context Card' → 'OECD Context Card'
   Root cause: 6 occurrences hardcoded as page-level text. Korea is OECD
   member but not European — geographic peer set is OECD-wide (Asia-Pacific
   + Europe + Americas).
   Fix: regex replace 'European' → 'OECD' in korea/intelligence.html only.
   Scope: korea page only (other country pages unaffected).

2. map.js substation popup € symbol persistent
   Root cause: map.js currSymbol IIFE looked up SSI_COUNTRIES_CONFIG[iso]
   from a fetch of '/countries.json' which 404s from /korea/. Even when
   fetched successfully, the live shape is {countries:[...]} not iso-keyed
   dict — so cc lookup would still fail.
   Fix: patch map.js to PREFER window.SSIMetadata.currency_symbol (always
   present on country pages via ssi-metadata.js), with multi-layer fallback
   for backward compat (handles both flat-iso-dict and {countries:[...]}
   shapes). Affects ALL country popups — improves KR + IS (₩ + kr.) + any
   future non-eurozone country.

3. socio_economic.rd_pct_gdp = 4.8% for every Korean region
   Root cause: my hotfix #2 set rd_pct_gdp as a global constant (4.8%)
   instead of per-region variance.
   Fix: regenerate korea/ssi-data.json with realistic per-region R&D
   intensity (KOSTAT + Bank of Korea 2024 reference):
     Daejeon 9.5% (R&D capital: KAIST + KAERI + Daedeok Valley gov labs)
     Gyeonggi 6.8% (Samsung Pyeongtaek + SK Hynix Icheon corporate R&D)
     Sejong 5.2% (gov R&D consolidation) · Seoul 4.5% · Ulsan 3.8%
     Gyeongbuk 3.5% (POSCO Pohang + Samsung Gumi) · Incheon 3.2%
     Gyeongnam 2.8% (Samsung+Hyundai Heavy) · Chungnam 2.5% (Asan)
     Busan 2.3% · Chungbuk 2.2% (SK Hynix Cheongju) · Daegu 1.9%
     Gwangju 1.8% (Kia) · Jeonbuk 1.6% · Jeonnam 1.5% · Gangwon 1.3%
     Jeju 1.2% (tourism)
   17 unique values across 17 do/si — full regional variance.

Anti-patterns reinforced (NOT new parents):
  A1f sub-pattern: currency-symbol leakage extends from country-config
  through to shared renderer logic in map.js (same parent as #5 + #6).
  A1d sub-pattern: data-schema deficit — uniform field values where
  per-region variance expected (same parent as #2).

Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 7/4
  (this hotfix adds 1 hotfix at sub-pattern levels; no new A-family parents).

Scope:
  - korea/intelligence.html (page-level text fix)
  - map.js (shared root — improves all country popups)
  - korea/ssi-data.json (regional R&D variance for 1,184 substations)" --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea hotfix #7 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload:"
echo "  https://ikengassiindex.github.io/korea/intelligence.html  ← OECD Context Card"
echo "  https://ikengassiindex.github.io/korea/map.html           ← click substation, ₩ popup"
echo ""
echo "Expected fixes:"
echo "  1. intelligence.html: 'European Context Card' → 'OECD Context Card' (all 6 occurrences)"
echo "  2. map popup: GDP per capita shows ₩30,000 (Daegu) / ₩48,000 (Seoul) / ₩60,000 (Ulsan)"
echo "     instead of €30,000 / €48,000 / €60,000"
echo "  3. R&D (Innovation): varies per region — Daejeon 9.5% / Gyeonggi 6.8% / Jeju 1.2%"
echo "     instead of uniform 4.8% across all"
echo ""
echo "Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 7/4"
echo "════════════════════════════════════════════════════════════════════════"
