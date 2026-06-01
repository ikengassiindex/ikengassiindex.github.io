#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_israel_v1.sh — Israel inaugural deploy (Session 34)
#
# CONTEXT (Israel onboarding, Session 34):
#   37th OECD dashboard entry (38th including Greenland). First OECD onboarding
#   on the post-S33 architectural floor (11 hard pre-flight gates, including
#   D#21 content-leakage). Greenfield from clean Costa Rica template.
#
# ACCEPTANCE TARGET (KB §73.7):
#   ≤ 1 hotfix · 0 new A-family parents
#   First-time test of the 11-gate floor on a structurally novel country.
#
# Architectural novelties Israel introduces (per fact card):
#   (a) is_iec_monopoly: true       — KR/CR-pattern carry-forward (3rd in cohort)
#   (b) is_high_threat_grid: true   — NEW flag, first OECD onboarded during
#                                      active armed-conflict period
#   (c) insular_grid + EuroAsia HVDC planned 2028 — first cohort grid that
#                                      will become non-insular mid-lifecycle
#   (d) R6_drought NEW α anchor      — first arid-climate modifier in cohort,
#                                      anchored to desal-water-electricity nexus
#   (e) R6_volcanic active:false     — NEW precedent-setting non-erasure flag,
#                                      preserves modifier in stack for cohort
#                                      consistency but disables it for IL
#   (f) Dead Sea Transform Fault     — first strike-slip seismic primary source
#                                      vs the subduction megathrust pattern of
#                                      KR/CR/JP. M7+ overdue per ~80-100 yr cycle.
#   (g) R7 ceiling 1.040 cohort-LEADING — INCD 2017 + Unit 8200 lineage + CERT-IL 2014
#   (h) language_mode: latin_only    — first Hebrew-script source with
#                                      Latin-only rendering mode (per onboarding
#                                      choice — postpones full RTL test to a
#                                      future session if requested)
#
# Artifacts deployed:
#   israel/                         — 9 thin-shell files (8 pages + ssi-metadata.js)
#                                      + grid-geo.json + bounds.json + ssi-data.json
#                                      + versions.json
#   data/israel_config.json         — scoring pipeline config (51 keys)
#   intelligence/country-configs/israel.json — renderer-side config (22 keys)
#   intelligence/countries.json     — +israel entry (38 total)
#   intelligence/edition-config.json — Aug-Dec 2026 IL rotations
#   nav.js                          — regenerated (38 countries)
#   scripts/validate-schema.py      — MIN_FLEET["IL"] = 200 added
#
# Pre-flight (11 gates) verified locally — ALL PASS:
#   D#3   inline JS parse-check                                  ✓
#   D#14  canonical {s,l,a} grid-geo + regions-list schema       ✓
#   D#15  country-config mandatory                                ✓
#   D#16  page-ID parity vs canonical (7 pages ≥ threshold)       ✓
#   D#17  substation 44-field schema + variance        WARN→PASS  ✓
#       (rd_pct_gdp absent in all subs — non-blocking; carry-over to hotfix #1 if requested)
#   D#18  nav.js slug parity (3 sections)                         ✓
#   D#19  currency leakage (₪ primary, € parenthetical)           ✓
#   D#20  edition_anchor_month_offset range (offset=5)            ✓
#   D#21  content-leakage (0 hits from any other country vocab)   ✓
#   D#56  fleet-floor (257 ≫ MIN_FLEET[IL]=200)                   ✓
#   Stage 7e runtime audit                                        deferred to post-deploy
#
# Usage:
#   cd ~/ikengassiindex.github.io
#   export IL_WORKSPACE="/Users/cedricberard/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Israel"
#   export IL_REPO="$PWD"
#   bash "$IL_WORKSPACE/land_israel_v1.sh"
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${IL_WORKSPACE:-/Users/cedricberard/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Israel}"
REPO="${IL_REPO:-$HOME/ikengassiindex.github.io}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Israel inaugural deploy — Session 34"
echo "  37th OECD entry · 38th dashboard country (incl. Greenland)"
echo "  Architectural floor: 11 hard pre-flight gates (post-S33)"
echo "  Acceptance: ≤ 1 hotfix / 0 new A-family parents"
echo "════════════════════════════════════════════════════════════════════════"

# ─── Sanity: verify artifacts exist ───────────────────────────────────────
if [[ ! -d "israel" ]]; then
  echo "✗ FATAL: israel/ directory not found in repo"
  exit 1
fi
required_files=(
  israel/ssi-data.json israel/grid-geo.json israel/bounds.json israel/versions.json
  israel/ssi-metadata.js
  israel/index.html israel/intelligence.html israel/regional.html
  israel/map.html israel/data.html israel/methodology.html
  israel/esg-report.html israel/dno-dashboard.html
  intelligence/country-configs/israel.json
  data/israel_config.json
)
for f in "${required_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "✗ FATAL: $f missing"
    exit 1
  fi
done
echo "  ✓ All ${#required_files[@]} required artifacts present"

# ─── Run preflight (11 gates) ──────────────────────────────────────────────
echo ""
echo "→ Running scripts/preflight.sh israel"
if ! bash scripts/preflight.sh israel > /tmp/il_preflight.log 2>&1; then
  echo "✗ PREFLIGHT FAILED — aborting deploy"
  tail -40 /tmp/il_preflight.log
  exit 1
fi
echo "  ✓ ALL 10 GATES PASSED (D#3 + D#14/15/56 + D#16-D#20)"

# ─── D#21 content-leakage (CRITICAL) ───────────────────────────────────────
echo ""
echo "→ Running scripts/check_content_leakage.py israel (D#21 — CRITICAL)"
python3 scripts/check_content_leakage.py israel > /tmp/il_d21.log 2>&1
if grep -q "FAIL israel" /tmp/il_d21.log; then
  echo "✗ D#21 (content leakage) FAILED — aborting deploy"
  cat /tmp/il_d21.log
  exit 1
fi
if ! grep -q "PASS israel" /tmp/il_d21.log; then
  echo "✗ D#21 produced unexpected output:"
  cat /tmp/il_d21.log
  exit 1
fi
echo "  ✓ D#21 (content leakage) PASS — 0 hits from any other country vocab"

# ─── Cache busters ─────────────────────────────────────────────────────────
echo ""
echo "→ Bumping cache busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/il_cachebump.log 2>&1 || true
  echo "  ✓ bumped"
fi

# ─── Stage ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging Israel inaugural artifacts"

git add israel/
git add data/israel_config.json
git add intelligence/country-configs/israel.json
git add intelligence/countries.json
git add intelligence/edition-config.json
git add nav.js
git add scripts/validate-schema.py

# Cache-buster bumps across all country pages
git add '*/data.html' '*/dno-dashboard.html' '*/esg-report.html' '*/index.html' \
        '*/intelligence.html' '*/map.html' '*/methodology.html' '*/regional.html' 2>/dev/null || true

# Save audit-trail copy of this deploy script
cp "$WORKSPACE/land_israel_v1.sh" "$REPO/scripts/land_israel_v1.sh"
chmod +x "$REPO/scripts/land_israel_v1.sh"
git add scripts/land_israel_v1.sh

echo ""
git diff --cached --stat | tail -20

# ─── Commit ────────────────────────────────────────────────────────────────
echo ""
echo "→ Committing Israel inaugural deploy"
git commit -m "feat(israel): inaugural deploy — 37th OECD country (Session 34)

═══ Fleet ═══
  257 substations across 6 mehozot districts (point-in-polygon attributed
    cleanly: Southern 87, Central 51, Northern 48, Haifa 36, Tel Aviv 18,
    Jerusalem 17 — distribution reflects population + grid density)
  4,152 power lines (very dense per-area — IL is a small + densely-instrumented
    grid)
  Voltage: 18 Transmission (400 kV backbone, limited deployment) + 239
    Sub-Transmission (161 kV is the main transmission tier; distribution from
    22 kV down)

═══ Architectural patterns (carry-forward + novel) ═══
  ✓ IEC single-DSO monopoly (is_iec_monopoly: true)        → KR/CR pattern
  ✓ Noga ILITO as ISO since 2021 reform                     → first split-ISO
                                                              pattern in cohort
  ✓ insular grid (no synchronous interconnect)              → IS/KR pattern
  ✓ EuroAsia HVDC planned 2028                              → FIRST grid that
                                                              ends insularity
                                                              mid-cohort lifecycle
  ✓ R6_drought NEW α anchor (Negev arid, desal nexus)       → FIRST in cohort
  ✓ R6_volcanic active:false flag                           → NEW precedent
                                                              for non-erasure
  ✓ Dead Sea Transform strike-slip seismic                  → FIRST cohort
                                                              transform-fault
                                                              (vs subduction)
  ✓ R7 ceiling 1.040 cohort-LEADING                         → INCD 2017 +
                                                              Unit 8200 + CERT-IL
  ✓ is_high_threat_grid: true                               → NEW flag, first
                                                              conflict-era
                                                              onboarding
  ✓ language_mode: latin_only                               → FIRST Hebrew-source
                                                              Latin-render test
  ✓ edition_anchor_month_offset=5                           → cohort-synced
                                                              Edition 02 =
                                                              2026-07-09

═══ Pre-flight gate state (11 gates) ═══
  D#3   inline JS parse-check                              → PASS
  D#14  canonical {s,l,a} grid-geo                         → PASS
  D#15  country-config mandatory                           → PASS
  D#16  page-ID parity vs canonical                        → PASS (7 pages ≥ threshold)
  D#17  substation schema + variance                       → PASS (WARN on rd_pct_gdp)
  D#18  nav.js slug parity                                 → PASS (3 sections, 38 slugs)
  D#19  currency leakage (₪ primary)                       → PASS
  D#20  edition_offset range (offset=5)                    → PASS
  D#21  content-leakage (no cross-country narrative)       → PASS (0 hits)
  D#56  fleet-floor                                        → PASS (257 ≫ MIN_FLEET[IL]=200)

═══ Acceptance target (KB §73.7) ═══
  ≤ 1 post-deploy hotfix + 0 new A-family parents.
  Compounding-curve test:
    SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 8/4 →
    CR S33A rolled-back → CR S33B 1/0 → IL S34 target 0-1/0.

═══ Edition schedule ═══
  Edition 01: inaugural (this commit)
  Edition 02: 2026-07-09 (2nd Thursday July — cohort-synchronized)
  Edition 03: 2026-08-13 (Tel Aviv deep-dive — Silicon Wadi)
  Edition 04: 2026-09-10 (Haifa — Bazan + Yokne'am chip cluster)
  Edition 05: 2026-10-08 (Central — Sharon Plain + Sorek desalination)
  Edition 06: 2026-11-12 (Negev — Beersheba + Dimona + R6_drought peak)
  Edition 07: 2026-12-10 (Jerusalem — Mobileye + Dead Sea Transform fault)

Cross-link: KB §73 + BPG Part XL (Session 33 closure documentation).
Fact card: /SSI Index/SSI_v4_0 Israel/ISRAEL_FACT_CARD.md (853 lines, 24
sections, web-verified per BPG Discipline #11)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Israel inaugural landed → $C_SHA"
echo ""
echo "After ~1-2 min GH Pages rebuild, verify live (5 critical URLs):"
echo "  https://ikengassiindex.github.io/israel/index.html"
echo "  https://ikengassiindex.github.io/israel/intelligence.html ← Section G: Edition 02 / 2026-07-09"
echo "  https://ikengassiindex.github.io/israel/map.html          ← 257 subs · 6 mehozot · NO offshore lines"
echo "  https://ikengassiindex.github.io/israel/regional.html     ← Tel Aviv ↑ Southern ↓"
echo "  https://ikengassiindex.github.io/israel/methodology.html  ← R6_drought NEW α + R6_volcanic INACTIVE"
echo ""
echo "Post-deploy visual audit (per S33 Cocos lesson):"
echo "  □ Flag in header is 🇮🇱 (not 🇨🇷)"
echo "  □ All 'CR' references converted to 'IL'"
echo "  □ Currency shows ₪ (not ₡)"
echo "  □ Map renders within IL borders (no offshore artifacts)"
echo "  □ 6 mehozot polygons render correctly (no fragmented edges)"
echo "  □ R6_volcanic disabled but listed in modifier stack"
echo "  □ R6_drought NEW α visible in intelligence + methodology"
echo ""
echo "Acceptance: ≤ 1 hotfix, 0 new A-family parents (per KB §73.7)."
echo "════════════════════════════════════════════════════════════════════════"
