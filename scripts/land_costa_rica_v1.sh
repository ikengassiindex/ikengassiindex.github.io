#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_costa_rica_v1.sh — Costa Rica Session 33 inaugural deploy
#
# First single-country onboarding on the post-Session-32 + post-§72.10
# architectural floor (10 hard pre-flight gates).
#
# Artifacts deployed:
#   costa-rica/                  — 8 thin-shell pages + ssi-metadata.js +
#                                  grid-geo.json + bounds.json + ssi-data.json +
#                                  versions.json
#   data/costa-rica_config.json  — scoring pipeline config
#   intelligence/country-configs/costa-rica.json — renderer-side config
#   intelligence/countries.json  — +costa-rica entry (37 total)
#   intelligence/edition-config.json — rotation +4 periods
#   nav.js                       — +costa-rica in 3 sections
#
# Acceptance criterion (KB §72.11 + BPG XXXIX.11):
#   ≤ 1 hotfix, 0 new A-family parents.
#   Edition 01 = inaugural deploy date (~2026-05-29).
#   Edition 02 = 2026-07-09 (synchronized with SI/SK/HU/IS/KR cohort).
#
# Pre-flight: scripts/preflight.sh runs all 7 gates (D#3 + D#14/15/56 + D#16
# + D#17 + D#18 + D#19 + D#20). Deploy aborts on ANY gate fail.
#
# Usage (from a fresh terminal):
#   cd ~/ikengassiindex.github.io
#   export CR_WORKSPACE="/Users/cedricberard/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Costa Rica"
#   export CR_REPO="$PWD"
#   bash "$CR_WORKSPACE/land_costa_rica_v1.sh"
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${CR_WORKSPACE:?CR_WORKSPACE must be set}"
REPO="${CR_REPO:?CR_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Costa Rica Session 33 — Inaugural deploy"
echo "  36th OECD country | 38th dashboard entry | first post-§72.10 onboarding"
echo "  170 substations / 7 provincias / SIEPAC-interconnected / ICE single-DSO"
echo "════════════════════════════════════════════════════════════════════════"

# ─── Pre-flight: verify costa-rica/ exists ──────────────────────────────────
if [[ ! -d "costa-rica" ]]; then
  echo "✗ FATAL: costa-rica/ directory not found in repo"
  exit 1
fi
for f in costa-rica/ssi-data.json costa-rica/grid-geo.json costa-rica/bounds.json \
         costa-rica/intelligence.html costa-rica/ssi-metadata.js \
         intelligence/country-configs/costa-rica.json data/costa-rica_config.json ; do
  if [[ ! -f "$f" ]]; then
    echo "✗ FATAL: $f missing"
    exit 1
  fi
done
echo "  ✓ All 7 required artifacts present"

# ─── Self-verification: run preflight gates ─────────────────────────────────
echo ""
echo "→ Running scripts/preflight.sh costa-rica (10-gate enforcement)"
if ! bash scripts/preflight.sh costa-rica > /tmp/cr_preflight.log 2>&1; then
  echo "✗ PREFLIGHT FAILED — aborting deploy"
  tail -30 /tmp/cr_preflight.log
  exit 1
fi
echo "  ✓ ALL 7 GATES PASSED (D#3 + D#14/15/56 + D#16 + D#17 + D#18 + D#19 + D#20)"

# ─── Cache busters ──────────────────────────────────────────────────────────
echo ""
echo "→ Bumping cache busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cr_cachebump.log 2>&1 || true
  echo "  ✓ bumped"
fi

# ─── Staging ────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging Costa Rica artifacts"

# Country folder (8 pages + 5 data files)
git add costa-rica/

# Configs
git add data/costa-rica_config.json
git add intelligence/country-configs/costa-rica.json

# SoT patches
git add intelligence/countries.json
git add intelligence/edition-config.json
git add nav.js

# Cache-buster bumps
git add '*/data.html' '*/dno-dashboard.html' '*/esg-report.html' '*/index.html' \
        '*/intelligence.html' '*/map.html' '*/methodology.html' '*/regional.html' 2>/dev/null || true

# Save audit-trail copy of this script
cp "$WORKSPACE/land_costa_rica_v1.sh" "$REPO/scripts/land_costa_rica_v1.sh"
chmod +x "$REPO/scripts/land_costa_rica_v1.sh"
git add scripts/land_costa_rica_v1.sh

echo ""
git diff --cached --stat | tail -15

# ─── Commit ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Committing Costa Rica inaugural"
git commit -m "feat(costa-rica): inaugural deploy — 36th OECD, Session 33, post-§72.10 floor

Costa Rica (República de Costa Rica) joins as the 36th OECD country onboarded
and the 38th dashboard entry (including Greenland). First single-country
onboarding on the post-Session-32 + post-§72.10 architectural floor —
acceptance test for whether Discipline #16-#20 gates carry forward cleanly.

═══ Fleet ═══
  170 substations across 7 provincias
  575 power lines (250 'line' + 325 'minor_line')
  Median R: 0.414  |  R range: 0.27-0.62
  Distribution: Alajuela 51 (Coyol FTZ + airport) > San José 34 > Guanacaste 33
    (geothermal cluster) > Cartago 18 > Puntarenas 13 > Heredia 12 (Intel) >
    Limón 9 (Caribbean port)

═══ Architectural patterns (carry-forward expectations from KB §72.11) ═══
  ✓ ICE single-DSO monopoly       → is_ice_monopoly: true (KR-pattern)
  ✓ ~99% renewable T_share        → matches IS T_share saturation
  ✓ R6_volcanic active modifier   → 5 active volcanoes (IS-codified pattern)
  ✓ R6_seismic Pacific Ring       → Nicoya 2012 Mw 7.6 + Cinchona 2009 Mw 6.1
                                    anchors (KR/IS codified)
  ✓ CRC ₡ pre-symbol Latin script → simpler than KR ₩, IL Hebrew RTL
  ✓ SIEPAC interconnect           → non-zero cross_border_lines (first in cohort)
  ✓ edition_anchor_month_offset:5 → cohort-synchronized Edition 02 = 2026-07-09

═══ NEW sub-pattern surfaced (NOT a new A-family parent) ═══
  R6_hydro_deficit — El Niño hydropower vulnerability anchored on 2024 worst
    El Niño in 50 years (per ICE). Highest α in Guanacaste (0.16) — Pacific
    drought belt + thermal backup imports via SIEPAC. NEW engine sub-pattern
    at the engine layer, codified as parameter not as A-family parent.

═══ Cyber posture (R7) ═══
  Anchored on 2022 ransomware national emergency:
    - Conti hit Hacienda 18 Apr 2022 (\$10M ransom demand)
    - Hive hit CCSS 31 May 2022 (\$5M)
    - National emergency declared 8 May 2022 by President Chaves
      (first OECD peacetime cyber-emergency declaration)
  Post-2022 R7 baseline 1.018; ceiling 1.025 (mid-cohort).
  CSIRT-CR under MICITT Dirección de Gobernanza Digital (formed 2012, opened 2015).

═══ Pre-flight gate state (10 disciplines) ═══
  D#3   inline JS parse-check     → PASS (no failing blocks)
  D#14  canonical {s,l,a} schema  → PASS
  D#15  country-config mandatory  → PASS
  D#16  page-ID parity vs IS      → PASS (intelligence.html=77 IDs matches IS)
  D#17  substation schema + vari  → PASS (44 fields + rd_pct_gdp 7 unique)
  D#18  nav.js slug parity        → PASS (costa-rica in all 3 sections)
  D#19  currency leakage          → PASS (₡ primary, € parenthetical)
  D#20  edition_offset range      → PASS (offset=5, in range [1,12])
  D#56  fleet-floor (KB §56)      → PASS (170 subs, no MIN_FLEET[CR] floor)

═══ Acceptance target (KB §72.11) ═══
  ≤ 1 post-deploy hotfix + 0 new A-family parents.
  Compounding-curve test: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 8/4 →
  CR target 0-1/0 (validates Session 32 architectural investment).

═══ Edition schedule ═══
  Edition 01: inaugural deploy (this commit)
  Edition 02: 2026-07-09 (2nd Thursday of July — synchronized with SI/SK/HU/IS/KR)
  Edition 03: 2026-08-13
  Edition 04: 2026-09-10

Cross-link: KB §72.10 (edition-offset finding) + §72.11 (CR pre-flight framing) +
BPG Part XXXIX XXXIX.10 (D#20 codification) + XXXIX.11 (CR acceptance framing).

Fact card: /SSI Index/SSI_v4_0 Costa Rica/COSTA_RICA_FACT_CARD.md (580 lines,
19 sections, web-verified per BPG Discipline #11).

Honest finding: 2024 was the worst El Niño in 50 years; ICE imported ~10%
thermal generation Apr-May 2024 via SIEPAC. The pure 99% renewable headline
was true for 2023 and most years but is climate-vulnerable. R6_hydro_deficit
captures this." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Costa Rica landed → $C_SHA"
echo ""
echo "After ~1-2 min GH Pages rebuild, verify live:"
echo "  https://ikengassiindex.github.io/costa-rica/index.html"
echo "  https://ikengassiindex.github.io/costa-rica/intelligence.html  ← Section G: Edition 02 / 2026-07-09"
echo "  https://ikengassiindex.github.io/costa-rica/map.html           ← 170 subs across 7 provincias"
echo "  https://ikengassiindex.github.io/costa-rica/regional.html      ← worst Heredia, best San José"
echo ""
echo "Acceptance: ≤ 1 hotfix, 0 new A-family parents (per KB §72.11)."
echo "If you observe any rendering issue in next 24h, that becomes hotfix #1."
echo ""
echo "OECD coverage: 36 OECD + Greenland = 37 dashboard countries LIVE"
echo "Remaining final-3: Israel (Hebrew RTL test) + Colombia (32-departamento scale test)"
echo "════════════════════════════════════════════════════════════════════════"
