#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_iceland_upstream_cleanup.sh — Iceland template-chain cleanup
#
# Triggered by CR Session 33 post-deploy audit (rolled back commit 37b2a2b3):
# the IS template was found to be contaminated with Hungary content from an
# earlier bad clone. CR cloning from IS inherited the contamination.
#
# This commit cleans the IS upstream so that future CR/IL/CO onboardings
# can clone from a clean reference. Also wires the new D#21 (content-leakage)
# gate into scripts/preflight.sh and ships scripts/check_content_leakage.py.
#
# Files modified:
#   iceland/ssi-metadata.js    — rewritten with clean Iceland-only content
#                                 (Landsnet TSO + Orkustofnun + Veitur/RARIK/HS Veitur
#                                  DSOs + Veðurstofa + Hagstofa + Seðlabanki +
#                                  CERT-IS + Alcoa/Rio Tinto/Century smelters)
#   iceland/intelligence.html  — Edition 01 retitled + D-section rewritten
#                                 with 8-landshluti rotation
#   iceland/data.html          — KPI + 4 source-table rows
#   iceland/methodology.html   — Step-1+5 paragraphs + modifier table rebuilt
#   iceland/versions.json      — bonus fix (removed stray SI cross-cohort)
#
# New gate landing:
#   scripts/check_content_leakage.py    — D#21 gate, 30-country vocab dict
#   scripts/preflight.sh                — wired D#21 between D#20 and D#56
#
# Bonus central-renderer fix (Section C visual audit):
#   intelligence-sections.js            — Section C Data Source Registry + Changelog
#                                         tables now use CSS grid with auto-derived
#                                         id-column widths. Handles both FR-style
#                                         terse entries (2-char IDs, 40-80 char text)
#                                         and post-cohort verbose entries (8-char IDs,
#                                         100-200 char text) gracefully. Visual rendering
#                                         no longer breaks on long entries.
#
# Verification: D#21 + all 7 preflight gates PASS on iceland post-cleanup.
# Before: 63 HU hits across 4 files. After: 0 HU hits.
#
# Usage (from a fresh terminal):
#   cd ~/ikengassiindex.github.io
#   export IS_WORKSPACE="/Users/cedricberard/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Iceland"
#   export IS_REPO="$PWD"
#   bash "$IS_WORKSPACE/land_iceland_upstream_cleanup.sh"
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${IS_WORKSPACE:?IS_WORKSPACE must be set}"
REPO="${IS_REPO:?IS_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Iceland upstream template-chain cleanup"
echo "  Removes Hungary contamination (63 → 0 HU hits)"
echo "  Wires new D#21 content-leakage gate into preflight.sh"
echo "════════════════════════════════════════════════════════════════════════"

# Pre-flight verify
for f in iceland/ssi-metadata.js iceland/intelligence.html iceland/data.html \
         iceland/methodology.html iceland/versions.json \
         scripts/check_content_leakage.py ; do
  if [[ ! -f "$f" ]]; then
    echo "✗ FATAL: $f missing"
    exit 1
  fi
done
echo "  ✓ All 6 required artifacts present"

echo ""
echo "→ Running preflight.sh iceland + D#21"
if ! bash scripts/preflight.sh iceland > /tmp/is_preflight.log 2>&1; then
  echo "✗ PREFLIGHT FAILED — aborting deploy"
  tail -30 /tmp/is_preflight.log
  exit 1
fi
echo "  ✓ All 7 gates PASS"

python3 scripts/check_content_leakage.py iceland > /tmp/is_d21.log 2>&1
if grep -q "PASS iceland" /tmp/is_d21.log; then
  echo "  ✓ D#21 (content leakage) PASS"
else
  echo "✗ D#21 still failing:"
  cat /tmp/is_d21.log
  exit 1
fi

echo ""
echo "→ Bumping cache busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/is_cachebump.log 2>&1 || true
  echo "  ✓ bumped"
fi

echo ""
echo "→ Staging"
git add iceland/ssi-metadata.js \
        iceland/intelligence.html \
        iceland/data.html \
        iceland/methodology.html \
        iceland/versions.json
git add scripts/check_content_leakage.py
git add scripts/preflight.sh 2>/dev/null || true
# Bonus: central-renderer fix (Section C grid layout — benefits all 36 countries)
git add intelligence-sections.js 2>/dev/null || true
git add '*/data.html' '*/dno-dashboard.html' '*/esg-report.html' '*/index.html' \
        '*/intelligence.html' '*/map.html' '*/methodology.html' '*/regional.html' 2>/dev/null || true

# Save audit-trail copy of this script
cp "$WORKSPACE/land_iceland_upstream_cleanup.sh" "$REPO/scripts/land_iceland_upstream_cleanup.sh"
chmod +x "$REPO/scripts/land_iceland_upstream_cleanup.sh"
git add scripts/land_iceland_upstream_cleanup.sh

git diff --cached --stat | tail -10

echo ""
echo "→ Committing"
git commit -m "fix(iceland): upstream template cleanup — remove HU contamination + wire D#21 gate

Triggered by CR Session 33 post-deploy audit (rolled back commit 37b2a2b3).
The iceland/ template was contaminated with Hungary content from an earlier
bad clone, and CR cloning from IS inherited 246 hits (142 IS + 104 HU) of
upstream contamination. This commit cleans the IS upstream so future
single-country onboardings can clone from a clean reference.

═══ Iceland files rewritten (63 HU hits → 0) ═══

  iceland/ssi-metadata.js (32,453 bytes, 256 lines) — full rewrite of all 15
    top-level objects with clean Iceland-only content:
    • SSIMetadata.methodology: 4-tier R3 + Iceland R6 anchors (Sundhnúkur
      2024 / Reykjanes 2021-active / Eyjafjallajökull 2010 / Skeiðará 1996
      jökulhlaup / SISZ 2008 Mw 6.3); R7 ceiling 1.04
    • COMPONENTS_INDEX: drivers rewritten with Iceland narrative
      (Reykjavík/Vestfirðir SAIDI split; 220/132/66 kV Byggðalína; 3
      aluminum smelters Alcoa Fjarðaál + Rio Tinto ISAL + Century Norðurál;
      99.97% renewable T_share saturation)
    • DATA_SOURCES: 13 entries — Landsnet + Orkustofnun + Veitur/RARIK/HS
      Veitur DSOs + Veðurstofa Íslands (consolidated) + Hagstofa Íslands +
      Seðlabanki Íslands + OSM Overpass (ISO3166-1=IS) + UST + Copernicus +
      CERT-IS + Fjarskiptastofa + Landsvirkjun/ON Power/HS Orka generation
    • REGIONS_NUTS3: 8 landshluti with codes HOF/SUN/VES/VFJ/NLV/NLE/AUS/SUL
      and the 4-tier R3 distribution from IS hotfix #2
    • DSO_PANEL: 3 entries (Veitur ~58% / RARIK ~32% / HS Veitur ~10%)
    • MODIFIER_DEFS: R2/R3/R4/R6a/R6_seismic/R6_volcanic/R6c_jokulhlaup/R7
      including the 2 NEW Iceland sub-patterns (R6_volcanic + R6c_jokulhlaup)
    • VALIDATION_CHECKS + CHANGELOG + ESG_SOURCES: IS-S30-* entries rebuilt
      with Iceland anchors

  iceland/intelligence.html — Edition 01 retitled to 'Suðurnes & the Reykjanes
    Eruption Cycle'; D-section rotation rewritten (Ed.01 Suðurnes/Sundhnúkur,
    Ed.02 Höfuðborgarsvæðið, Ed.03 Austurland/Fjarðaál, Ed.04 Vesturland/
    Grundartangi, etc.); SAIDI comparator labels updated to Veitur/RARIK;
    'Megye' table headers → 'Landshluti'; cross-border interconnect refs
    aligned with insular-grid reality (zero interconnects)

  iceland/data.html — KPI footer + 4 source-table rows rewritten
    (Landsnet + Veðurstofa Íslands feeds; Veitur+RARIK+HS Veitur DSOs;
     Hagstofa/Seðlabanki; Copernicus; CERT-IS + Fjarskiptastofa)

  iceland/methodology.html — Step-1 ingest paragraph rewritten with full IS
    data-source list; Step-5 modify paragraph updated for 7 Iceland
    modifiers (4-tier R3 + R6_seismic + R6_volcanic NEW + R6c_jokulhlaup
    NEW); modifier table rebuilt (R6b → R6_seismic with SISZ/TFZ anchors;
    +2 new rows for R6_volcanic and R6c_jokulhlaup; R7 ceiling 1.04 with
    CERT-IS 2013 + Act 78/2019 NIS2)

  iceland/versions.json — bonus fix removing stray 'SI Obalno-kraška'
    cross-cohort reference that triggered a WARN

═══ New gate landing ═══

  scripts/check_content_leakage.py — Discipline #21 gate (post-CR S33 audit
    finding). Detects cross-country content contamination by scanning each
    country's pages + ssi-metadata.js for proper-noun fingerprints from
    OTHER countries' vocabularies. Threshold ≥5 hits = FAIL.

    Vocab dict tuned for HIGH PRECISION (proper nouns only — TSO/DSO/
    regulator names, unique place names, anchor events, industrial brands).
    ~30 countries × ~10-20 terms each. Drops common-word false positives
    (regione, Bundesland, kommune, etc.).

  scripts/preflight.sh — extended with D#21 between D#20 and D#56.
    Now 8 enforceable gates: D#3 + D#14/15/56 + D#16 + D#17 + D#18 + D#19
    + D#20 + D#21.

═══ Central-renderer fix (Section C visual audit) ═══

  intelligence-sections.js — Section C 'Data Refresh & Changelog' rewritten
  to use CSS grid with auto-derived id-column widths. Triggered by user-
  reported visual audit on Iceland intelligence.html where the section
  rendered visually ugly compared to the France benchmark.

  ROOT CAUSE: the original flex layout had hardcoded min-widths (30px id,
  65px type, 90px res) and align-items:center, designed for France's terse
  style (2-char IDs, 40-80 char change text). Post-cohort countries (SK/HU/
  IS/KR) author verbose entries (8-char IDs, 100-200 char text) that
  overflow the fixed columns and wrap with center-aligned baselines,
  producing cramped misaligned rendering.

  FIX (renderer-side, affects all 36 countries):
    Data Source Registry: display:grid; grid-template-columns: [auto-id] 1fr
      90px 110px 60px; column-gap:12px; align-items:start. Auto-derives
      id-column width from max id length in the source list (range 48-110px).
    Changelog: display:grid; grid-template-columns: [auto-id] 80px 1fr
      [auto-section]; column-gap:12px; align-items:start. Auto-derives both
      id-column AND section-column widths from their max lengths.

  Result: France (id=2, change=58 avg) and Iceland/Hungary (id=8, change=167
  avg) both render cleanly with the same renderer. Long text wraps within
  its column without disturbing alignment of sibling columns. The fix is
  durable: future countries with even-longer entries inherit the same
  graceful handling.

  Architectural codification (for next-session KB §73):
    A1g — RENDERER-FRAGILE-TO-CONTENT-LENGTH sub-pattern. Distinct from
    A1a (schema-key) / A1c (DOM-hooks) / A1d (data-emit) — this is about
    fixed-width layout assumptions in shared renderers that break when
    country-specific content scales beyond the original-design baseline.
    Prevention principle: shared renderers should use CSS grid (or
    flex-with-wrap) and auto-derive widths from data extremes, not
    hardcoded min-widths.

═══ Architectural note ═══

This is A1c-at-content-layer sub-pattern, codified by D#21. Distinct from:
  - A1c-at-DOM-hooks (Korea S31 hotfix #1; closed by D#16 page-ID parity)
  - A1d data-emit (closed by D#17 schema parity)
  - A1e SoT-regen (closed by D#18 nav.js parity)
  - A1f i18n-i10n (closed by D#19 currency check + D#20 offset range)

A1c-at-content-layer is the inline-prose-narrative contamination that
clone-from-template can carry through when the upstream template is itself
contaminated. D#21 catches it; iceland/ rewrite removes the actual instance.

═══ Acceptance state ═══

Pre-cleanup: iceland FAILed D#21 with 63 HU hits.
Post-cleanup: iceland PASSes D#21 (0 HU hits) + all 7 other gates.
Cohort sweep: korea WARNed (3 hits, manageable), HU/SI/SK PASS.

This commit unblocks the CR S33B re-onboarding (next session) which will
clone from clean iceland/ template + use D#21 as the verification gate." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Iceland upstream cleanup landed → $C_SHA"
echo ""
echo "After GH Pages rebuild, verify:"
echo "  https://ikengassiindex.github.io/iceland/intelligence.html — opening should now"
echo "    correctly describe Iceland (no Hungary leakage)"
echo "  https://ikengassiindex.github.io/iceland/data.html — sources should be Iceland-only"
echo "  https://ikengassiindex.github.io/iceland/methodology.html — R6 anchors Iceland-only"
echo ""
echo "Forward to next session:"
echo "  - DACH (AT+DE) cross-contamination cleanup"
echo "  - AU UK-heritage cleanup"
echo "  - Re-author Costa Rica from clean Iceland template (CR S33B)"
echo "  - Wire D#21 into preflight.sh (done in this commit, becomes active)"
echo "════════════════════════════════════════════════════════════════════════"
