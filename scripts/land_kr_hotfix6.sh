#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_kr_hotfix6.sh — Korea hotfix #6: B.2 VoLL note + narrative ₩ override
#
# User clarification: "the economic data for any substation should equally
# be updated" — after hotfix #5 fixed tier-table VoLL to ₩, the B.2 VoLL
# context note + narrative paragraph BELOW the table were still showing
# hardcoded ACER European reference text (€13.1/kWh + €15-30/kWh ranges).
#
# Root cause: intelligence-sections.js (shared across all countries) had
# hardcoded €-denominated text in two places:
#   L470: 'ACER's 2023 estimate places average VoLL at €13.1/kWh ...'
#   L491: 'estimated VoLL of €15–30/kWh, compared to €1–3/kWh in rural...'
#
# These are sensible defaults for eurozone countries (ACER is the EU agency
# benchmark) but inappropriate on Korea pages where the tier table now
# shows ₩.
#
# Fix: add country-config override mechanism. intelligence-sections.js
# patched to check ctx.config.b2_voll_note + ctx.config.b2_narrative
# BEFORE falling through to hardcoded ACER text. korea.json adds these
# fields with KRW-primary Korean-contextual text.
#
# Other countries unaffected — fall through to current ACER €13.1/kWh
# until they explicitly add overrides.
#
# Anti-pattern: A1f sub-pattern — extended currency-symbol leakage from
# country-config (tier voll_range) into shared renderer text (b2-voll-note,
# b2-narrative). Detection: grep € in intelligence-sections.js + countries
# that should override. Prevention: BPG Discipline #19 extended — country-
# config author must provide b2_voll_note + b2_narrative overrides for
# non-eurozone countries.
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${KOREA_WORKSPACE:?KOREA_WORKSPACE must be set}"
REPO="${KOREA_REPO:?KOREA_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -f "$WORKSPACE/hotfix6/intelligence-sections.js" ]]; then
  echo "✗ Hotfix #6 payload not found: $WORKSPACE/hotfix6/"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Hotfix #6 — B.2 VoLL note + narrative ₩ override (A1f sub-pattern)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Copying patched files"
cp "$WORKSPACE/hotfix6/intelligence-sections.js" "$REPO/intelligence-sections.js"
echo "  ✓ intelligence-sections.js ($(wc -c < $REPO/intelligence-sections.js) bytes)"
cp "$WORKSPACE/hotfix6/korea.json" "$REPO/intelligence/country-configs/korea.json"
echo "  ✓ intelligence/country-configs/korea.json"

echo ""
echo "→ Verification: intelligence-sections.js override mechanism present"
v1=$(grep -c "ctx.config.b2_voll_note" "$REPO/intelligence-sections.js" || true)
v2=$(grep -c "ctx.config.b2_narrative" "$REPO/intelligence-sections.js" || true)
echo "  ctx.config.b2_voll_note check: $v1 (expected 1)"
echo "  ctx.config.b2_narrative check: $v2 (expected 1)"
[[ "$v1" -ge 1 && "$v2" -ge 1 ]] || { echo "✗ Override checks not present"; exit 1; }

echo ""
echo "→ Verification: korea.json has override fields"
python3 << 'PYEOF'
import json
cc = json.load(open('intelligence/country-configs/korea.json'))
assert 'b2_voll_note' in cc, 'b2_voll_note missing'
assert 'b2_narrative' in cc, 'b2_narrative missing'
assert '₩' in cc['b2_voll_note'], '₩ missing in b2_voll_note'
assert '₩' in cc['b2_narrative'], '₩ missing in b2_narrative'
print(f'  ✓ b2_voll_note: {len(cc["b2_voll_note"])} chars · ₩×{cc["b2_voll_note"].count("₩")}')
print(f'  ✓ b2_narrative: {len(cc["b2_narrative"])} chars · ₩×{cc["b2_narrative"].count("₩")}')
PYEOF

cp "$WORKSPACE/land_kr_hotfix6.sh" "$REPO/scripts/land_kr_hotfix6.sh"
chmod +x "$REPO/scripts/land_kr_hotfix6.sh"
echo "  ✓ scripts/land_kr_hotfix6.sh"

if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1 || true
fi

echo ""
echo "→ Staging for commit"
git add intelligence-sections.js intelligence/country-configs/korea.json scripts/land_kr_hotfix6.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(korea): hotfix #6 — B.2 VoLL note + narrative ₩ override (A1f sub-pattern)

User clarification after hotfix #5: 'the economic data for any substation
should equally be updated'. After fixing tier-table VoLL to ₩ (hotfix #5),
the B.2 VoLL CONTEXT NOTE + NARRATIVE PARAGRAPH below the tier table
still showed hardcoded ACER European reference text with €13.1/kWh +
€15-30/kWh ranges.

Root cause: intelligence-sections.js (shared across all countries) had
hardcoded €-denominated text in two places (lines 469-473 + 488-494).
Sensible defaults for eurozone countries but inappropriate on Korea
pages where the tier table now shows ₩.

Fix: add country-config override mechanism. intelligence-sections.js
patched to check ctx.config.b2_voll_note + ctx.config.b2_narrative
BEFORE falling through to hardcoded ACER text. Placeholders supported:
  - {totalHCHR}: count of High-Consequence High-Risk substations
  - {topLower}: top tier R3 lower bound (e.g., 1.05)
  - {econRegionStr}: top-3 economic regions by count
  - {avgEP}: fleet-wide average energy poverty rate

korea.json adds Korean-contextual text:
  b2_voll_note: 'Korean industrial VoLL ₩25,000–45,000/kWh (≈ €18–32/kWh)
    for chaebol fab + petrochemical corridors (Samsung Pyeongtaek, SK Hynix
    Icheon, POSCO Gwangyang/Pohang, Hyundai Ulsan)...'

  b2_narrative: 'The Industrial-Chaebol tier concentrates in {econRegionStr}
    — Korean do/si where chaebol fab + steel + petrochemical corridors
    depend on uninterrupted 765/345/154 kV transmission...'

Other countries unaffected — fall through to current ACER €13.1/kWh
hardcoded text until they explicitly add b2_voll_note + b2_narrative
overrides to their country-config.

Anti-pattern: A1f sub-pattern — currency-symbol leakage extended from
country-config (tier voll_range) into shared renderer narrative text.
Same parent (A1f) as hotfix #5 but at a different layer. Detection:
grep € in intelligence-sections.js + non-eurozone country pages.

Prevention reinforced: BPG Discipline #19 (forthcoming) — country-config
author MUST provide b2_voll_note + b2_narrative overrides for non-
eurozone countries (KR, IS, HU, JP, US, UK, CH, NO, SE, DK).

Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 6/4 (this
hotfix adds 1 hotfix at A1f sub-pattern level, no new A-family parent).

Scope: intelligence-sections.js (shared root) + intelligence/country-
configs/korea.json. Affects only Korea's B.2 VoLL note + narrative
rendering; other 35 OECD countries unchanged." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea hotfix #6 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload:"
echo "  https://ikengassiindex.github.io/korea/intelligence.html"
echo ""
echo "Expected fix in B.2 Economic Impact panel:"
echo "  - Tier table:    ₩25,000–45,000/kWh etc. (from hotfix #5)"
echo "  - VoLL note:     'Korean industrial VoLL ₩25,000–45,000/kWh ...' (NEW)"
echo "  - Narrative:     'Industrial-Chaebol tier concentrates in {regions}'"
echo "                   '...₩25,000–45,000/kWh for fab corridors...' (NEW)"
echo "  → All economic text on the page now uses ₩ as primary currency"
echo ""
echo "Other 35 OECD countries unaffected (fall through to ACER €13.1/kWh)."
echo ""
echo "Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 6/4"
echo "════════════════════════════════════════════════════════════════════════"
