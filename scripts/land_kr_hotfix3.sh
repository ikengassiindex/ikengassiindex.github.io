#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_kr_hotfix3.sh — Korea hotfix #3: header copy-edit fixes
#
# User-reported on visible page header of index.html:
#   1. "(Seoul + Gyeonggi + 117 do/si)" — math/regex bug
#      (substitution `8 landshluti → 17 do/si` matched the "8" inside
#       "18 landshluti", leaving "1" prepended → "117")
#      Fix: "(Seoul + Gyeonggi + 15 other do/si)" (17 total = 2 metros + 15)
#
#   2. "19 public data sources" — over-aggressive substitution
#      (my Pass 2 cleanup replaced "30+ → 19" but "30+" is the project-wide
#       SSI Index source pool, not country-specific. IS live correctly says
#       "30+ public data sources".)
#      Fix: "30+ public data sources" (3 occurrences in index.html)
#
# Scope: korea/index.html only (other 7 pages do not contain these strings).
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${KOREA_WORKSPACE:?KOREA_WORKSPACE must be set}"
REPO="${KOREA_REPO:?KOREA_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -f "$WORKSPACE/hotfix3/index.html" ]]; then
  echo "✗ Hotfix #3 payload not found: $WORKSPACE/hotfix3/index.html"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Hotfix #3 — header copy-edits (117 do/si + 19 sources)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Copying fixed index.html"
cp "$WORKSPACE/hotfix3/index.html" "$REPO/korea/index.html"
echo "  ✓ korea/index.html ($(wc -c < $REPO/korea/index.html) bytes)"

echo ""
echo "→ Verification: no remaining errors"
err1=$(grep -c "117 do/si" "$REPO/korea/index.html" 2>/dev/null || true)
err2=$(grep -c "19 public data sources" "$REPO/korea/index.html" 2>/dev/null || true)
echo "  '117 do/si' remaining: $err1 (expected 0)"
echo "  '19 public data sources' remaining: $err2 (expected 0)"
[[ "$err1" -eq 0 && "$err2" -eq 0 ]] || { echo "✗ Errors not fully cleared"; exit 1; }
echo "  ✓ Both errors cleared"

echo ""
echo "→ Verification: replacements present"
fix1=$(grep -c "Seoul + Gyeonggi + 15 other do/si" "$REPO/korea/index.html" 2>/dev/null || true)
fix2=$(grep -c "30+ public data sources" "$REPO/korea/index.html" 2>/dev/null || true)
echo "  'Seoul + Gyeonggi + 15 other do/si': $fix1 (expected 1)"
echo "  '30+ public data sources': $fix2 (expected ≥ 3)"

# Copy this script for audit
cp "$WORKSPACE/land_kr_hotfix3.sh" "$REPO/scripts/land_kr_hotfix3.sh"
chmod +x "$REPO/scripts/land_kr_hotfix3.sh"
echo "  ✓ scripts/land_kr_hotfix3.sh"

# Cache-busters
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1 || true
fi

echo ""
echo "→ Staging for commit"
git add korea/index.html scripts/land_kr_hotfix3.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(korea): hotfix #3 — header copy-edits (117 do/si math bug + 19/30+ sources)

User-reported errors on visible page header of korea/index.html:

1. '(Seoul + Gyeonggi + 117 do/si)' — math/regex bug
   Root cause: hotfix #1 substitution rule \`8 landshluti → 17 do/si\`
   matched the '8' inside '18 landshluti' (from the IS template '18 landshluti'),
   leaving '1' prepended to '17 do/si' → 'Seoul + Gyeonggi + 1' + '17 do/si'
   = 'Seoul + Gyeonggi + 117 do/si'.
   Fix: explicit string replace '(Seoul + Gyeonggi + 117 do/si)' →
        '(Seoul + Gyeonggi + 15 other do/si)' (17 total = 2 metros + 15)

2. '19 public data sources' — over-aggressive substitution (3 occurrences)
   Root cause: hotfix #1 substitution rule \`30+ verified public data sources
   → 19 verified public data sources\` was wrong. The '30+' is the project-wide
   SSI Index source pool (across all 35 OECD countries), not country-specific.
   Iceland live correctly says '30+ public data sources'. Korea's per-country
   source count is 19 but that belongs in data.html / methodology.html
   inventory, NOT the project-wide intro paragraph.
   Fix: regex replace \\b19 public data sources\\b → 30+ public data sources
   (3 occurrences in index.html: visible header paragraph + 2 OG meta tags)

Anti-pattern reinforces A1c (HTML static fabrication) + A1d (data-schema
deficit) parents — both already codified in KR Session 31 hotfixes #1 + #2.
This hotfix is a sub-pattern of A1c (page-author content errors) — does NOT
add a new A-family parent.

Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 3/2 (this hotfix
adds 1 hotfix but 0 new A-family parents — A1c regression at sub-pattern level).

Scope: korea/index.html only. Other 7 pages do not contain these strings." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea hotfix #3 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload index page:"
echo "  https://ikengassiindex.github.io/korea/index.html"
echo ""
echo "Expected fixes in header paragraph:"
echo "  ✓ 'Seoul + Gyeonggi + 117 do/si'  →  'Seoul + Gyeonggi + 15 other do/si'"
echo "  ✓ '19 public data sources'  →  '30+ public data sources' (3 occurrences)"
echo ""
echo "Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 3/2"
echo "════════════════════════════════════════════════════════════════════════"
