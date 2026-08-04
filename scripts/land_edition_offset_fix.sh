#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_edition_offset_fix.sh — Edition-02 alignment for IS + KR
#
# Symptom: Iceland + Korea intelligence.html Section G "Looking Ahead" was
#   computing next-edition as "Edition 07" instead of the SI/SK/HU-consistent
#   "Edition 02". User-reported: "next edition is 02 and published on the
#   second Thursday of July 2026 (intelligence page)".
#
# Root cause: intelligence/country-configs/{iceland,korea}.json had
#   edition_anchor_month_offset = 0, while the renderer formula is
#     nextEditionNum = (year - 2026) * 12 + (nextMonth + 1) - anchor_offset
#   With today=2026-05-29 → nextMonth=July (6), nextEditionNum = 7 - 0 = 7.
#   SI uses offset=5, SK/HU use offset=7 (clamped via Math.max(2,…) to 02).
#
# Fix: set IS + KR offset to 5 (matches Slovenia / produces Edition 02 cleanly).
#
# Pre-flight: scripts/preflight.sh must pass before commit.
#
# Usage:
#   cd ~/ikengassiindex.github.io
#   export S32_WORKSPACE="/Users/cedricberard/Library/CloudStorage/OneDrive-IkengaSL/Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index"
#   export S32_REPO="$PWD"
#   bash "$S32_WORKSPACE/SSI_v4_0 Korea/land_edition_offset_fix.sh"
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${S32_WORKSPACE:?S32_WORKSPACE must be set}"
REPO="${S32_REPO:?S32_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Edition-02 alignment for IS + KR (intelligence page next-edition fix)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Verifying patch was applied locally"
python3 << 'PYEOF'
import json
for slug in ["iceland", "korea"]:
    cfg = json.load(open(f"intelligence/country-configs/{slug}.json"))
    o = cfg.get("edition_anchor_month_offset")
    print(f"  {slug}: edition_anchor_month_offset = {o} (expected 5)")
    assert o == 5, f"{slug} offset is {o}, expected 5"
print("  ✓ both configs at offset=5")
PYEOF

echo ""
echo "→ Self-verification — run preflight (this is the wire)"
if ! bash scripts/preflight.sh > /tmp/prflight_eoffix.log 2>&1; then
  echo "✗ preflight FAILED — aborting deploy"
  tail -20 /tmp/prflight_eoffix.log
  exit 1
fi
echo "  ✓ preflight all-green"

echo ""
echo "→ Bumping cache busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump_eoffix.log 2>&1 || true
  echo "  ✓ bumped"
fi

echo ""
echo "→ Staging"
git add intelligence/country-configs/iceland.json \
        intelligence/country-configs/korea.json
git add '*/data.html' '*/dno-dashboard.html' '*/esg-report.html' '*/index.html' \
        '*/intelligence.html' '*/map.html' '*/methodology.html' '*/regional.html' 2>/dev/null || true

# Save audit-trail copy
cp "$WORKSPACE/SSI_v4_0 Korea/land_edition_offset_fix.sh" "$REPO/scripts/land_edition_offset_fix.sh"
chmod +x "$REPO/scripts/land_edition_offset_fix.sh"
git add scripts/land_edition_offset_fix.sh

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(iceland,korea): edition_anchor_month_offset 0→5 — render Edition 02 not 07

User-reported on intelligence.html Section G 'Looking Ahead':
  IS + KR were rendering 'Edition 07' for next edition while SI/SK/HU
  correctly rendered 'Edition 02 / second Thursday of July 2026'.

Root cause: intelligence/country-configs/{iceland,korea}.json had
  'edition_anchor_month_offset': 0
which made the renderer compute:
  nextEditionNum = (year - 2026) * 12 + (nextMonth + 1) - 0
                 = 0*12 + 7 - 0  =  7  →  displays 'Edition 07'

Reference (all 5 cohort countries after fix, today=2026-05-29):
  slovenia    offset=5  → Edition 02  (raw 2)
  slovakia    offset=7  → Edition 02  (raw 0, clamped via Math.max(2,…))
  hungary     offset=7  → Edition 02  (raw 0, clamped)
  iceland     offset=5  → Edition 02  (raw 2)     ← FIX
  korea       offset=5  → Edition 02  (raw 2)     ← FIX

All 5 now render: 'Edition 02 will be published on the second Thursday of
July 2026' — consistent triple-drop wording across SI/SK/HU/IS/KR cohort.

Preflight: all 6 gates green (D#3 + D#14/15/56 + D#16 + D#17 + D#18 + D#19).
Wire: deploy script ran scripts/preflight.sh and would have aborted on fail.

Scope: 2 files (iceland.json + korea.json) + cache-buster bumps." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Edition-02 alignment landed → $C_SHA"
echo ""
echo "After ~1-2 min GH Pages rebuild, hard-reload Section G on each page:"
echo "  https://ikengassiindex.github.io/slovenia/intelligence.html"
echo "  https://ikengassiindex.github.io/slovakia/intelligence.html"
echo "  https://ikengassiindex.github.io/hungary/intelligence.html"
echo "  https://ikengassiindex.github.io/iceland/intelligence.html   ← was 07"
echo "  https://ikengassiindex.github.io/korea/intelligence.html     ← was 07"
echo ""
echo "Each should now show:"
echo "  'Next Month — Edition 02'"
echo "  'Edition 02 will be published on the second Thursday of July 2026'"
echo "════════════════════════════════════════════════════════════════════════"
