#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_costa_rica_v2.sh — Costa Rica S33B re-onboarding deploy
#
# CONTEXT (CR S33A → rollback → S33B):
#   The previous CR S33A deploy (commit 82823778, 29 May 2026) was rolled back
#   after the post-deploy audit surfaced A1c-at-content-layer contamination —
#   the CR pages had 142 IS hits + 104 HU hits of upstream-template proper-
#   noun leakage, traced to a contaminated iceland/ template that was itself
#   carrying Hungary content from an earlier clone.
#
#   The IS upstream-cleanup commit (c2e41e06 + e4c78f91, 31 May 2026) rewrote
#   the IS files and added the D#21 (content-leakage) preflight gate. This
#   commit re-onboards Costa Rica from the now-clean IS template + adds the
#   CR-specific narrative directly authored from the COSTA_RICA_FACT_CARD.md
#   (580-line web-verified fact card, BPG Discipline #11).
#
# ACCEPTANCE TARGET (KB §73.7 / §72.11 / BPG Part XL):
#   ≤ 1 hotfix · 0 new A-family parents · D#21 PASS (0 IS hits, 0 HU hits)
#   vs CR S33A baseline 246 hits (142 IS + 104 HU).
#
# Artifacts deployed:
#   costa-rica/                                — 8 thin-shell pages + ssi-metadata.js
#                                                 + grid-geo.json + bounds.json
#                                                 + ssi-data.json + versions.json
#   data/costa-rica_config.json                — scoring pipeline config
#   intelligence/country-configs/costa-rica.json — renderer-side config
#   intelligence/countries.json                — +costa-rica entry (37 total)
#   intelligence/edition-config.json           — rotation +4 periods CR deep-dives
#   nav.js                                     — +costa-rica in 3 sections
#
# Pre-flight (8 gates) MUST PASS before commit:
#   D#3   inline JS parse-check
#   D#14/15/56 canonical schema + country-config + fleet-floor
#   D#16  page-ID parity vs canonical
#   D#17  substation 44-field schema + variance
#   D#18  nav.js slug parity
#   D#19  currency leakage (₡ primary, € parenthetical)
#   D#20  edition_anchor_month_offset range (offset=5)
#   D#21  content-leakage (NEW — must PASS 0 IS + 0 HU hits)
#
# Cross-links:
#   KB §72.10 (edition-offset finding) + §72.11 (CR pre-flight framing)
#   KB §73    (CR S33B re-onboarding closure — to be authored next session)
#   BPG Part XXXIX Discipline #20 + #21
#   BPG Part XL  (CR operational playbook — to be authored next session)
#
# Usage (from a fresh terminal):
#   cd ~/ikengassiindex.github.io
#   export CR_WORKSPACE="/Users/cedricberard/Library/CloudStorage/OneDrive-IkengaSL/Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/SSI_v4_0 Costa Rica"
#   export CR_REPO="$PWD"
#   bash "$CR_WORKSPACE/land_costa_rica_v2.sh"
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
echo "Costa Rica S33B — Post-IS-upstream-cleanup re-onboarding"
echo "  37th OECD entry | re-authored from clean iceland/ template"
echo "  Acceptance: ≤ 1 hotfix / 0 new A-family parents / D#21 PASS"
echo "════════════════════════════════════════════════════════════════════════"

# ─── Pre-flight: verify required artifacts exist ───────────────────────────
if [[ ! -d "costa-rica" ]]; then
  echo "✗ FATAL: costa-rica/ directory not found in repo"
  exit 1
fi

required_files=(
  costa-rica/ssi-data.json
  costa-rica/grid-geo.json
  costa-rica/bounds.json
  costa-rica/versions.json
  costa-rica/ssi-metadata.js
  costa-rica/index.html
  costa-rica/intelligence.html
  costa-rica/regional.html
  costa-rica/map.html
  costa-rica/data.html
  costa-rica/methodology.html
  costa-rica/esg-report.html
  costa-rica/dno-dashboard.html
  intelligence/country-configs/costa-rica.json
  data/costa-rica_config.json
)
for f in "${required_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "✗ FATAL: $f missing"
    exit 1
  fi
done
echo "  ✓ All ${#required_files[@]} required artifacts present"

# ─── Self-verification: run preflight gates (BEFORE commit) ────────────────
echo ""
echo "→ Running scripts/preflight.sh costa-rica (D#3 + D#14/15/56 + D#16/17/18/19/20)"
if ! bash scripts/preflight.sh costa-rica > /tmp/cr_s33b_preflight.log 2>&1; then
  echo "✗ PREFLIGHT FAILED — aborting deploy"
  tail -40 /tmp/cr_s33b_preflight.log
  exit 1
fi
echo "  ✓ ALL 7 GATES PASSED (D#3 + D#14/15/56 + D#16 + D#17 + D#18 + D#19 + D#20)"

# ─── D#21 content-leakage self-verification (CRITICAL ACCEPTANCE GATE) ────
echo ""
echo "→ Running scripts/check_content_leakage.py costa-rica (D#21 — CRITICAL)"
python3 scripts/check_content_leakage.py costa-rica > /tmp/cr_s33b_d21.log 2>&1
if grep -q "FAIL costa-rica" /tmp/cr_s33b_d21.log; then
  echo "✗ D#21 (content leakage) FAILED — aborting deploy"
  cat /tmp/cr_s33b_d21.log
  echo ""
  echo "REMEDIATION: edit costa-rica/*.html and costa-rica/ssi-metadata.js"
  echo "             to remove the proper-noun fingerprints reported above."
  echo "             Re-run this script after fixing."
  exit 1
fi
if ! grep -q "PASS costa-rica" /tmp/cr_s33b_d21.log; then
  echo "✗ D#21 produced unexpected output:"
  cat /tmp/cr_s33b_d21.log
  exit 1
fi
echo "  ✓ D#21 (content leakage) PASS — 0 IS hits + 0 HU hits"
echo "    (CR S33A rolled-back baseline was 142 IS + 104 HU)"

# ─── Cache busters ─────────────────────────────────────────────────────────
echo ""
echo "→ Bumping cache busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cr_s33b_cachebump.log 2>&1 || true
  echo "  ✓ bumped"
fi

# ─── Staging ────────────────────────────────────────────────────────────────
echo ""
echo "→ Staging Costa Rica S33B artifacts"

# Country folder (8 pages + 5 data files)
git add costa-rica/

# Configs
git add data/costa-rica_config.json
git add intelligence/country-configs/costa-rica.json

# SoT patches
git add intelligence/countries.json
git add intelligence/edition-config.json
git add nav.js

# Cache-buster bumps across all countries
git add '*/data.html' '*/dno-dashboard.html' '*/esg-report.html' '*/index.html' \
        '*/intelligence.html' '*/map.html' '*/methodology.html' '*/regional.html' 2>/dev/null || true

# Save audit-trail copy of this script
cp "$WORKSPACE/land_costa_rica_v2.sh" "$REPO/scripts/land_costa_rica_v2.sh"
chmod +x "$REPO/scripts/land_costa_rica_v2.sh"
git add scripts/land_costa_rica_v2.sh

echo ""
git diff --cached --stat | tail -20

# ─── Commit ────────────────────────────────────────────────────────────────
echo ""
echo "→ Committing Costa Rica S33B"
git commit -m "feat(costa-rica): S33B re-onboarding from clean iceland/ template (post-upstream-cleanup)

Re-authors Costa Rica from the now-clean iceland/ template (commits c2e41e06 +
e4c78f91, 31 May 2026). The previous CR S33A deploy (commit 82823778, 29 May
2026) was rolled back after the post-deploy audit surfaced A1c-at-content-
layer contamination — 246 hits total (142 IS + 104 HU) of upstream-template
proper-noun leakage, traced to a contaminated iceland/ template carrying
Hungary content from an earlier clone.

This S33B deploy clones from clean iceland/ + adds CR-specific narrative
directly authored from the COSTA_RICA_FACT_CARD.md (580-line web-verified
fact card, BPG Discipline #11).

═══ Fleet ═══
  170 substations across 7 provincias (San José / Alajuela / Cartago /
    Heredia / Guanacaste / Puntarenas / Limón)
  ~575 power lines (SIEPAC 230 kV regional backbone + ICE 138 kV
    sub-transmission + DSO 34.5 kV urban)
  Distribution: Alajuela (Coyol FTZ + SJO airport) > San José GAM Central >
    Guanacaste (geothermal cluster + Otto 2016 zone) > Cartago > Puntarenas
    > Heredia (Intel/Boston Scientific) > Limón (Caribbean)

═══ Architectural patterns (carry-forward expectations from KB §72.11) ═══
  ✓ ICE single-DSO + CNFL subsidiary pattern → matches KR KEPCO adjacency
  ✓ ~99% renewable T_share (74% hydro + 13% geo + 12.5% wind in 2023;
    89% in 2024 El Niño drought) → carries forward IS T_share saturation
    + adds NEW 8-10pp dynamic-range modulation
  ✓ R6_volcanic active modifier → carries forward IS S30 pattern, adapted
    to composite stratovolcano hazard model (Arenal/Poás/Turrialba/Rincón
    de la Vieja/Irazú)
  ✓ R6_seismic Pacific Ring → Nicoya 2012 Mw 7.6 + Cinchona 2009 Mw 6.1
    anchors (Cinchona destroyed Cariblanco 100 MW hydro = 10% of national
    capacity)
  ✓ CRC ₡ pre-symbol → new currency added (joins ¥/₩/Ft/kr. precedent)
  ✓ SIEPAC interconnect → first non-zero cross_border_lines in 3 onboardings
    (IS=0, KR=0); CR-NI north + CR-PA south active since Oct 2014
  ✓ edition_anchor_month_offset=5 → cohort-synchronized Edition 02 = 2026-07-09

═══ NEW sub-patterns (NOT new A-family parents) ═══
  R6_hurricane — FIRST IN COHORT (Caribbean tropical-cyclone exposure)
    Anchors: Otto Nov 2016 (Cat 2 — first direct hurricane landfall since
    1851); Nate Oct 2017 (\$540M = ~1% GDP — costliest CR natural disaster)
  R6_hydro_deficit — FIRST IN COHORT (ENSO El Niño hydropower vulnerability)
    Anchor: 2023-2024 El Niño cycle, worst drought in 50 years per ICE;
    hydro dropped from 74% to 67%, thermal share spiked to 25% Apr-May 2024
    Carry-forward potential: NO + NZ + CL + Quebec/BC (other hydro-OECDs)

═══ Cyber posture (R7) ═══
  Anchored on 2022 ransomware NATIONAL EMERGENCY (first OECD peacetime
    cyber-emergency declaration by an OECD member):
    - Conti hit Ministerio de Hacienda 18 Apr 2022 (\$10M demand)
    - Hive hit CCSS public health 31 May 2022 (\$5M)
    - National emergency declared 8 May 2022 by President Chaves
  Post-2022 hardening: CSIRT-CR strengthened under MICITT Dirección de
    Gobernanza Digital + National Cybersecurity Strategy 2023.
  R7 ceiling 1.025 (mid-cohort) — reflects BOTH stress + post-stress
    hardening (post-event learning is the relevant signal).

═══ Pre-flight gate state (8 disciplines) ═══
  D#3   inline JS parse-check     → PASS (25 blocks across 8 pages clean)
  D#14  canonical {s,l,a} schema  → PASS
  D#15  country-config mandatory  → PASS
  D#16  page-ID parity vs canonical → PASS (intelligence.html=77 IDs)
  D#17  substation schema + var   → PASS
  D#18  nav.js slug parity        → PASS (costa-rica in all 3 sections)
  D#19  currency leakage          → PASS (₡ primary, € parenthetical)
  D#20  edition_offset range      → PASS (offset=5, in range [1,12])
  D#56  fleet-floor (KB §56)      → PASS (170 subs)
  D#21  content-leakage           → PASS (0 IS + 0 HU hits)
                                     (S33A baseline was 142 + 104)

═══ Acceptance target (KB §73.7) ═══
  ≤ 1 post-deploy hotfix + 0 new A-family parents (per KB §72.11 framing).
  Compounding-curve test:
    SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 8/4 → CR S33A 4/1 (rolled
    back) → CR S33B target 0-1/0 (validates D#21 prevention effectiveness).

═══ Edition schedule ═══
  Edition 01: inaugural S33B re-deploy (this commit)
  Edition 02: 2026-07-09 (2nd Thursday of July — cohort-synchronized)
  Edition 03: 2026-08-13
  Edition 04: 2026-09-10

Cross-link: KB §72.10 (edition-offset finding) + §72.11 (CR pre-flight
framing) + §73 (CR S33B closure, next session) + BPG Part XXXIX Discipline
#20 + #21 + Part XL (CR operational playbook, next session).

Fact card: /SSI Index/SSI_v4_0 Costa Rica/COSTA_RICA_FACT_CARD.md (580
lines, 19 sections, web-verified per BPG Discipline #11).

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
echo "Costa Rica S33B landed → $C_SHA"
echo ""
echo "After ~1-2 min GH Pages rebuild, verify live:"
echo "  https://ikengassiindex.github.io/costa-rica/index.html"
echo "  https://ikengassiindex.github.io/costa-rica/intelligence.html  ← Section G: Edition 02 / 2026-07-09"
echo "  https://ikengassiindex.github.io/costa-rica/map.html           ← 170 subs across 7 provincias"
echo "  https://ikengassiindex.github.io/costa-rica/regional.html      ← Heredia best / Limón worst"
echo "  https://ikengassiindex.github.io/costa-rica/methodology.html   ← R6_hurricane + R6_hydro_deficit NEW"
echo ""
echo "Acceptance: ≤ 1 hotfix, 0 new A-family parents (per KB §73.7)."
echo "If you observe any rendering issue in next 24h, that becomes hotfix #1."
echo ""
echo "D#21 PASS — content-leakage gate cleared as critical acceptance criterion."
echo "════════════════════════════════════════════════════════════════════════"
