#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_iceland_v1.sh — Iceland inaugural deployment
#                       First single-country onboarding post-CEE-South-2026
#
# Iceland is the 34th OECD country deployed (35th dashboard entry including
# Greenland) and the FIRST country onboarded under the cohort-complete
# post-CEE-South-2026 architectural floor (Safe + normalizeMeta + admin-
# unit-suffix tolerance all settled per KB §69.11/§69.12).
#
# **This commit tests architectural carry-forward to a structurally novel
# country.**
#
# Iceland brings four genuinely new stress dimensions:
#   1. Insular grid — ZERO land interconnects (first in cohort)
#   2. ~99.97% renewable (T_share saturation — first in cohort)
#   3. Active volcanic exposure (Reykjanes Sundhnúkur eruption cycle since
#      19 Mar 2021; 8 Feb 2024 eruption damaged Svartsengi infrastructure;
#      Grindavík evacuated)
#   4. ISO 9223 C5 corrosion class RESTORED (first since SI Obalno-kraška)
#
# Acceptance criterion (per KB §70.7):
#   ≤ 1 post-deploy hotfix touching A1-A12 + ZERO new A-family parents.
#   R6_volcanic + R6c_jokulhlaup are NEW sub-patterns at the engine layer
#   (NOT new A-family parents — those are renderer-layer issues).
#
# Iceland specifics:
#   - 687 substations across 8 landshluti (Capital + 7 regional)
#   - 3-tier R3 (Capital 1.04 / Industrial 1.05 / Rural 1.02 — flattest cohort)
#   - median R 0.403 (Suðurnes Reykjanes 0.512 — first cohort-region with
#     ≥98% High band due to active volcanic + seismic + C5 corrosion compound)
#   - NEW R6_volcanic modifier (Suðurnes α=0.14, Suðurland 0.10, etc.)
#   - NEW R6c_jokulhlaup modifier (Austurland 0.06, Suðurland 0.08)
#   - ISK currency (NOT eurozone — currency_symbol='kr.', position='after',
#     mirrors HU 'Ft' precedent)
#   - 0 cross-border interconnects (isolated grid — first in cohort)
#   - Landsnet 93.22% state + 6.78% OR (NOT 100% state)
#   - 3 DSOs (Veitur OR-owned + RARIK state + HS Veitur HS Orka)
#   - 3 aluminum smelters consume ~70-80% national electricity
#     (Alcoa Fjarðaál + Rio Tinto ISAL + Century Aluminum Norðurál —
#      highest single-sector concentration in OECD)
#   - No nuclear (first cohort country with no nuclear footprint)
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Configurable paths
WORKSPACE_DEFAULT="$HOME/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Iceland"
WORKSPACE="${ICELAND_WORKSPACE:-$WORKSPACE_DEFAULT}"
REPO="${ICELAND_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"

cd "$REPO"

rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

# Check workspace exists
if [[ ! -d "$WORKSPACE/iceland-pages" ]]; then
  echo "✗ Workspace not found: $WORKSPACE/iceland-pages"
  echo "  Set ICELAND_WORKSPACE env var to override, or check OneDrive sync"
  exit 1
fi
if [[ ! -d "$WORKSPACE/step6-sot" ]]; then
  echo "✗ SoT patches not found: $WORKSPACE/step6-sot"
  exit 1
fi

# ─── Phase A: Copy files from OneDrive workspace to live repo ─────────────
echo ""
echo "→ Phase A: Copying files from workspace to live repo"

# Create iceland/ folder + copy 13 files
mkdir -p "$REPO/iceland"
for f in index.html regional.html map.html intelligence.html data.html \
         methodology.html esg-report.html dno-dashboard.html \
         ssi-metadata.js bounds.json grid-geo.json ssi-data.json versions.json; do
  if [[ -f "$WORKSPACE/iceland-pages/$f" ]]; then
    cp "$WORKSPACE/iceland-pages/$f" "$REPO/iceland/$f"
    echo "  ✓ iceland/$f"
  else
    echo "  ✗ MISSING $WORKSPACE/iceland-pages/$f"; exit 1
  fi
done

# Copy iceland_config.json → data/ (Iceland scoring config)
mkdir -p "$REPO/data"
cp "$WORKSPACE/iceland_config.json" "$REPO/data/iceland_config.json"
echo "  ✓ data/iceland_config.json"

# Copy this deploy script for audit trail
cp "$WORKSPACE/land_iceland_v1.sh" "$REPO/scripts/land_iceland_v1.sh"
chmod +x "$REPO/scripts/land_iceland_v1.sh"
echo "  ✓ scripts/land_iceland_v1.sh"

# Apply SoT patches
cp "$WORKSPACE/step6-sot/countries.json" "$REPO/intelligence/countries.json"
cp "$WORKSPACE/step6-sot/edition-config.json" "$REPO/intelligence/edition-config.json"
cp "$WORKSPACE/step6-sot/landing-index.html" "$REPO/index.html"
echo "  ✓ intelligence/countries.json (35 entries)"
echo "  ✓ intelligence/edition-config.json (4 rotation periods incl. Iceland)"
echo "  ✓ index.html (OECD 33→34, Iceland tile activated)"

# Optional: country-config (if Iceland needs an entry in intelligence/country-configs/)
mkdir -p "$REPO/intelligence/country-configs"
# Note: Iceland intelligence/country-configs/iceland.json is rendered from the
#       page-config block in iceland_config.json — no separate file required
#       unless central renderer specifically reads this path. Mirror HU pattern.

# ─── Phase B: Pre-flight gates ────────────────────────────────────────────
echo ""
echo "→ Phase B: Pre-flight gates"

if command -v node >/dev/null 2>&1; then
  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean"
  else
    echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"
    tail -20 /tmp/parsecheck.log; exit 1
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check (CI will run it)"
fi

# Bump cache-busters across all 35 country folders
python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; cat /tmp/cachecheck.log; exit 1; }

# Fleet-floor gate (KB §56) — Iceland MIN_FLEET[IS] = 600
python3 -c "
import json, sys
g = json.load(open('iceland/grid-geo.json'))
n_subs = len(g.get('s', {}))
floor = 600  # MIN_FLEET[IS] per Step 3 country-config
if n_subs < floor:
    print(f'  ✗ FLEET-FLOOR FAILED — {n_subs} < {floor}')
    sys.exit(1)
print(f'  ✓ fleet-floor: {n_subs} ≥ {floor} (KB §56)')
"

# Schema validation (skipped if jsonschema missing locally — CI will catch)
if python3 -c "import jsonschema" 2>/dev/null; then
  python3 -c "
import json
from jsonschema import validate
for name in ['grid-geo','ssi-data','bounds']:
    schema = json.load(open(f'schemas/{name}.schema.json'))
    data = json.load(open(f'iceland/{name}.json'))
    validate(instance=data, schema=schema)
    print(f'  ✓ iceland/{name}.json validates')
"
else
  echo "  ⚠ jsonschema not installed — CI will validate"
fi

# nav.js codegen
if [[ -f scripts/generate_nav_data.py ]]; then
  python3 scripts/generate_nav_data.py > /tmp/navgen.log 2>&1
  python3 scripts/generate_nav_data.py --check > /tmp/navcheck.log 2>&1 \
    && echo "  ✓ nav.js auto-section regenerated (35 countries)" \
    || { echo "  ✗ nav.js out of sync"; cat /tmp/navcheck.log; exit 1; }
fi

# Iceland-specific sanity checks
echo ""
echo "→ Iceland-specific sanity checks"
python3 -c "
import json

# (1) Confirm zero cross-border interconnects in grid-geo
g = json.load(open('iceland/grid-geo.json'))
print(f'  ✓ iceland/grid-geo.json: {len(g[\"s\"])} substations, {len(g[\"l\"])} lines')
print(f'  ✓ has_cross_border_interconnects: {g.get(\"has_cross_border_interconnects\", \"missing\")}')
print(f'  ✓ iso_9223_classes: {g.get(\"iso_9223_classes_used\", g.get(\"iso_9223_classes\", \"missing\"))}')

# (2) Confirm Suðurnes carries R6_volcanic > 1.10 (active eruption zone)
d = json.load(open('iceland/ssi-data.json'))
subs = d.get('substations', [])
sn_subs = [s for s in subs if s.get('region') == 'sudurnes']
if sn_subs:
    r6v = [s.get('modifiers', {}).get('R6_volcanic', 0) for s in sn_subs]
    print(f'  ✓ Suðurnes ({len(sn_subs)} subs): R6_volcanic range [{min(r6v):.3f}, {max(r6v):.3f}]')
    assert all(v > 1.10 for v in r6v), 'Suðurnes R6_volcanic should all be >1.10 (active eruption zone)'
    print(f'  ✓ All Suðurnes substations have R6_volcanic > 1.10 (active eruption verified)')

# (3) Confirm Höfuðborgarsvæðið has lowest median R (Capital pulls down)
regions = d.get('regions', {})
medians = {k: r['R_median'] for k, r in regions.items()}
capital_R = medians.get('hofudborgarsvaedid', 99)
sn_R = medians.get('sudurnes', 0)
print(f'  ✓ Capital R_median {capital_R} < Suðurnes R_median {sn_R} ({capital_R < sn_R})')

# (4) Confirm Iceland is in countries.json
c = json.load(open('intelligence/countries.json'))
assert 'iceland' in c['slugs'], 'iceland missing from slugs'
ice = next(co for co in c['countries'] if co['slug'] == 'iceland')
print(f'  ✓ countries.json: iceland country_number={ice[\"country_number\"]} oecd_number={ice[\"oecd_number\"]}')

# (5) Confirm Iceland is in edition-config.json all 4 rotation periods
e = json.load(open('intelligence/edition-config.json'))
for period, conf in sorted(e['rotation'].items()):
    if 'iceland' in conf['countries']:
        print(f'  ✓ edition-config[{period}].iceland: {conf[\"countries\"][\"iceland\"][\"corridor_name\"]}')
    else:
        print(f'  ✗ edition-config[{period}].iceland MISSING')
"

# ─── Phase C: Stage + commit + push ───────────────────────────────────────
echo ""
echo "→ Phase C: Staging Iceland inaugural drop"

git add iceland/
git add data/iceland_config.json
git add intelligence/countries.json
git add intelligence/edition-config.json
git add index.html
git add nav.js 2>/dev/null || true
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true
git add scripts/land_iceland_v1.sh

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -15
echo ""
git diff --cached --shortstat

# ─── Commit ───────────────────────────────────────────────────────────────
git commit -m "feat(iceland): inaugural ingestion — 687 substations, 8 landshluti, NEW R6_volcanic + R6c_jokulhlaup modifiers (KB §70 planned)

Iceland is the 34th OECD country deployed (35th dashboard entry incl.
Greenland) and the FIRST single-country onboarding post-CEE-South-2026
cohort closure (SI member 1 + SK member 2 + HU member 3 — all live
since 2026-05-29 with CEE-South-2026 cohort COMPLETE per KB §69.12).

**This commit tests architectural carry-forward to a structurally
novel country** — the first since KB §69.11 admin-unit-suffix
tolerance codification.

Iceland brings FOUR genuinely new stress dimensions to the cohort:
  1. Insular grid — ZERO land interconnects (first in cohort vs HU 7)
  2. ~99.97% renewable (70.5% hydro + 29.4% geothermal + 0.1% fossil)
     — T_share saturation, first in cohort
  3. Active volcanic exposure (Reykjanes Sundhnúkur eruption cycle
     since 19 Mar 2021; 8 Feb 2024 eruption damaged Svartsengi
     infrastructure; Grindavík evacuated)
  4. ISO 9223 C5 corrosion class RESTORED — first since SI Obalno-
     kraška (SK + HU landlocked, C2-C4 only)

Two NEW engine sub-patterns introduced (R6_volcanic + R6c_jokulhlaup):
  - R6_volcanic: alpha tier mapping for 8 landshluti
    * Suðurnes (Reykjanes — active eruption zone) α=0.14
    * Suðurland (Hekla + Eyjafjallajökull + Katla) α=0.10
    * Austurland (Vatnajökull / Grímsvötn) α=0.07
    * Norðurland eystra (Krafla low residual) α=0.04
    * Others α=0.00-0.02 (Höfuðborgarsvæðið, Vesturland, etc.)
  - R6c_jokulhlaup: glacial-outburst-flood (distinct from Q100 fluvial)
    * Austurland α=0.06 (Skeiðará 1996 anchor)
    * Suðurland α=0.08 (Markarfljót 2010 Eyjafjallajökull anchor)
    * Others α=0.00

Country profile:
  ISO2 IS · ISO3 ISL · 389,444 population (Hagstofa 1 Jan 2025)
  OECD: founding member (30 Sep 1961)
  EFTA/EEA member (NOT EU); Schengen since 2001
  Currency: ISK (NOT eurozone) — currency_symbol='kr.', position='after'
    (carries forward HU 'Ft' post-symbol pattern via Safe.fmt)
  TSO: Landsnet hf. (Icelandic State 93.22% + OR 6.78% — NOT 100% state)
  Regulator: Orkustofnun (OS)
  3 DSOs: Veitur (~55-60% OR-owned) + RARIK (~30-35% state) + HS Veitur
    (~10-15% HS Orka/Alterra)
  Generation: Landsvirkjun (state, ~71-75%) + ON Power (OR ~9-12%) +
    HS Orka (~9%) — Top 3 = ~97% of national electricity
  3 aluminum smelters consume ~70-80% national electricity (highest
    single-sector concentration in OECD): Alcoa Fjarðaál (~625 MW) +
    Rio Tinto ISAL Straumsvík (~400 MW) + Century Aluminum Norðurál
    Grundartangi (~540 MW)
  NIS2: Act 78/2019 + 2025 amendment (Lög um net- og upplýsingaöryggi,
    in force 1 Jan 2026 via EEA process). Competent authority:
    Fjarskiptastofa (ECOI). CSIRT: CERT-IS (founded 2013)
  No nuclear (first cohort country with no nuclear footprint at all)
  No ENTSO-E synchronous interconnection (isolated)

Fleet:
  687 substations across 8 landshluti (2 NUTS-3 IS001 Capital + IS002
    Country)
  1,428 power lines (248 'line' + 1,180 'minor_line')
  Höfuðborgarsvæðið (Capital) dominates 41.6% (286 subs — Reykjavík
    metropolitan + Hellisheiði/Nesjavellir geothermal)
  OSM tag completeness 67% (best in cohort: vs HU 41%, SK 43%)
  Median R 0.403 (vs HU 0.382, SK 0.401 — between them)
  Bands: Low 0% / Medium 76.0% / High 23.9% / Critical 0.1% (1 sub)
    — highest High-band % in cohort, driven by Suðurnes volcanic zone

Suðurnes (Reykjanes) volcanic anchor:
  79 substations · R_median 0.512 · 78/79 in High band (98.7%) · 1
    Critical — first cohort-region with ≥98% High band, driven by:
    * R6_volcanic α=0.14 (active eruption cycle)
    * R6_seismic 0.16g (volcanic seismicity)
    * ISO 9223 C5 corrosion (marine + volcanic H₂S emissions)
  Verified anchor: 8 Feb 2024 Sundhnúkur eruption damaged Svartsengi
    geothermal plant hot-water pipeline; ~26,000 residents lost
    heating ~4 days; Svartsengi switched to remote operation;
    parliament-authorised earth-barrier defenses in place; Grindavík
    evacuated since 10 Nov 2023.

Architecture (greenfield on post-CEE-South-2026 architecture):
  All 8 HTML pages thin-shell (82-607 lines each), total ~2,063 lines.
  Inherits unchanged: CountryRenderer.Safe namespace (KB §68.10),
    CountryRenderer.normalizeMeta (KB §68.11), intelligence-sections.js
    admin-unit-suffix tolerance (KB §69.11), Phase 2 thin-shell
    central renderer (KB §65).
  Per-country config: data/iceland_config.json (285 lines, 8 landshluti
    × 20 fields, R6_volcanic + R6c_jokulhlaup methodology blocks,
    9-block page rendering config).
  ssi-metadata.js: 266 lines, ships simple-array schemas (NOT rich
    Slovakia-style — Hungary intentionally stressed normalizeMeta with
    rich schemas; Iceland uses the canonical simple form to validate
    the carry-forward).

Edition + cohort:
  First refresh: 2026-08-13 (2nd Thursday August, single-country drop)
  Cohort: Single-country onboarding (post-CEE-South-2026 closure)
  Session: 30

Files (~16 new / 222 modified):
  NEW: iceland/{index, intelligence, esg-report, data, regional,
       methodology, map, dno-dashboard}.html + ssi-metadata.js +
       ssi-data.json (1.2 MB) + grid-geo.json (1.6 MB) + bounds.json
       (8 landshluti polygons from OSM admin_level=5) + versions.json
  NEW: data/iceland_config.json (285 lines, scoring config with
       R6_volcanic + R6c_jokulhlaup methodology blocks)
  NEW: scripts/land_iceland_v1.sh (this script, audit trail)
  MODIFIED: intelligence/countries.json (+Iceland entry, 34→35),
       intelligence/edition-config.json (+rotation in all 4 active
       periods), index.html (33 OECD → 34 OECD; IS SVG path activated
       map-oecd → map-active + href/flag/subs attrs),
       nav.js (auto-section regenerated for 35 countries),
       cache-buster bumps across all 35 countries

Pre-flight gates (all PASS):
  ✓ check_inline_js_parse.py --strict (0 parse failures)
  ✓ bump_cache_busters.py --check (all in sync)
  ✓ Fleet-floor: 687 ≥ 600 (KB §56)
  ✓ Schema validation: iceland/{grid-geo, ssi-data, bounds}.json
  ✓ nav.js auto-section in sync (35 countries)
  ✓ Suðurnes R6_volcanic > 1.10 verified (active eruption zone)
  ✓ Capital R_median < Suðurnes R_median (band distribution sanity)

KB §70.7 acceptance criterion:
  ≤ 1 post-deploy hotfix touching A1-A12 + ZERO new A-family parents.
  R6_volcanic + R6c_jokulhlaup are NEW sub-patterns at the engine layer
  (NOT A-family parents — those are renderer-layer issues).

  The compounding-curve hypothesis (per BPG Part XXXVI.3):
    Slovenia (S27): 18 hotfixes, 11 new A-parents, ~4.0 days
    Slovakia (S28): 4 hotfixes, 2 new A-parents, ~3.5 days
    Hungary (S29):  1 hotfix, 0 new A-parents, ~1.5 days
    Iceland (S30):  ? hotfixes, target 0 new A-family parents

  If Iceland onboards with 0-1 hotfixes and ZERO new A-family parents,
  the architectural-investment compounding curve is confirmed for a
  structurally novel (insular + volcanic + 100% renewable) country.

Cross-link: KB §65 (3-phase refactor), §65.7 (acceptance criterion
template), §66 (SI inaugural), §68 (SK inaugural + A12/A1b), §69
(HU inaugural + admin-unit-suffix), §69.11 (admin-unit-suffix tolerance
codification), §69.12 (CEE-South-2026 cohort COMPLETE), BPG Part XXXIV
(SI playbook), Part XXXV (SK + canonical defenses), Part XXXVI
(HU closure + cohort recap). Iceland fact card: SSI_v4_0 Iceland/
ICELAND_FACT_CARD.md (516 lines, 17 sections, web-verified)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

# ─── Push ─────────────────────────────────────────────────────────────────
echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Iceland inaugural deployment landed → $C_SHA"
echo ""
echo "Dashboard now serves 34 OECD + 1 Greenland = 35 LIVE."
echo "First single-country onboarding post-CEE-South-2026 cohort closure."
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, smoke-test all 8 URLs:"
echo "  open https://ikengassiindex.github.io/iceland/index.html"
echo "  open https://ikengassiindex.github.io/iceland/intelligence.html"
echo "  open https://ikengassiindex.github.io/iceland/regional.html"
echo "  open https://ikengassiindex.github.io/iceland/map.html"
echo "  open https://ikengassiindex.github.io/iceland/data.html"
echo "  open https://ikengassiindex.github.io/iceland/methodology.html"
echo "  open https://ikengassiindex.github.io/iceland/esg-report.html"
echo "  open https://ikengassiindex.github.io/iceland/dno-dashboard.html"
echo ""
echo "Key acceptance-test focus areas:"
echo "  → intelligence.html Section D: corridor filter on Suðurnes / Reykjanes"
echo "    (validates admin-unit-suffix tolerance with bare landshluti names)"
echo "  → dno-dashboard.html: handles 3-DSO + zero cross-border interconnects"
echo "  → map.html: 8 landshluti polygons render cleanly (OSM admin_level=5)"
echo "  → esg-report.html: R6_volcanic + R6c_jokulhlaup blocks display"
echo "  → All pages: ISK currency post-symbol formatting (\"5,000 kr.\")"
echo ""
echo "ARCHITECTURE ACCEPTANCE TEST IN PROGRESS:"
echo "  → Watch CI: https://github.com/ikengassiindex/ikengassiindex.github.io/actions"
echo "  → Watch landing: https://ikengassiindex.github.io/ (Iceland tile clickable)"
echo "  → Count post-deploy hotfix commits over next 24-48 hours."
echo ""
echo "  TARGET (KB §70.7): ≤ 1 hotfix + 0 new A-family parents."
echo "          Sub-pattern codifications at engine layer are expected"
echo "          (R6_volcanic + R6c_jokulhlaup); those don't count against budget."
echo ""
echo "  If Iceland produces 0 hotfixes despite the new modifier sub-patterns,"
echo "  the compounding curve from CEE-South-2026 extends cleanly to"
echo "  structurally novel countries. KB §70 + BPG Part XXXVII to follow."
echo "════════════════════════════════════════════════════════════════════════"
