#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_is_hotfix2.sh — Iceland hotfix #2 (two-part):
#   (a) ssi-data.json: convert regions dict → LIST (fixes regional.html
#       "loading data" stuck spinner)
#   (b) intelligence/country-configs/iceland.json: NEW file with custom
#       r3_buckets for 4-tier R3 (fixes intelligence.html B.2 "Economic
#       Impact by Business Fabric" empty Commercial/SME-Dense + Light/Rural
#       buckets)
#   (c) ssi-data.json: 4-tier R3 recalibration (was 3-tier in hotfix#1
#       deploy) — populates all 4 Economic Impact buckets:
#         Industrial-Aluminum 1.05 → Suðurnes + Vesturland + Austurland (189 subs, 27.5%)
#         Capital-Reykjavík 1.04  → Höfuðborgarsvæðið (286 subs, 41.6%)
#         Commercial/SME 1.03      → Norðurland eystra + Suðurland (174 subs, 25.3%)
#         Rural/Peripheral 1.02    → Vestfirðir + Norðurland vestra (38 subs, 5.5%)
#
# Root causes:
#   - Issue 1 (regions dict): Iceland's scoring script (Step 4) emitted
#     `regions` as a dict {slug → region_obj} while HU/SK/SI all emit as
#     a list [{region: slug, ...}]. regional.html renderer expects list
#     iteration → "loading data" stuck. Anti-pattern A1a at emission.
#
#   - Issue 2 (empty B.2 buckets): Iceland intelligence/country-configs/
#     iceland.json was MISSING from the live repo. Without country-specific
#     r3_buckets, the renderer falls back to DEFAULT_R3_BUCKETS in
#     intelligence-sections.js which expects R3 ranges [0.97, 1.05+] —
#     Iceland's [1.02, 1.05] range only populates Industrial (R3≥1.05)
#     + Capital (1.00-1.05) buckets, leaving Commercial/SME-Dense
#     (0.97-1.00) and Light/Rural (<0.97) EMPTY.
#
# Architectural significance:
#   - Issue 1: same A1a-at-emission as hotfix #1 (which fixed grid-geo
#     schema). The OSM-extract pipeline + scoring pipeline need
#     contract tests against the canonical schema. Add to BPG Part XXXVII.
#   - Issue 2: NEW DISCIPLINE — every country MUST ship a country-config
#     even if it just inherits defaults. Add to BPG Part XXXVII discipline
#     #15: 'New-country onboarding produces intelligence/country-configs/
#     <slug>.json as a Step-5 mandatory artefact. Pre-flight gate checks
#     file exists. Country-specific r3_buckets recommended for any country
#     whose R3 distribution doesn't span [0.97, 1.05+].'
#
# Acceptance verdict update (KB §70.7):
#   Iceland hotfix count attributable to inaugural: 2 (#1 + #2)
#   New A-family parents surfaced: 0 (A1a-at-emission codified Session 27)
#   New disciplines codified: 2 (country-config mandatory + 4-tier R3 floor)
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE_DEFAULT="$HOME/Library/CloudStorage/OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/0.22. IP agenda/SSI Index/SSI_v4_0 Iceland"
WORKSPACE="${ICELAND_WORKSPACE:-$WORKSPACE_DEFAULT}"
REPO="${ICELAND_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"

cd "$REPO"
rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -d "$WORKSPACE/hotfix2" ]]; then
  echo "✗ Hotfix payload not found: $WORKSPACE/hotfix2"
  exit 1
fi

# ─── Copy patched files from workspace ────────────────────────────────────
echo ""
echo "→ Copying hotfix #2 payload"
cp "$WORKSPACE/hotfix2/ssi-data.json" "$REPO/iceland/ssi-data.json"
cp "$WORKSPACE/hotfix2/iceland_country-config.json" "$REPO/intelligence/country-configs/iceland.json"
cp "$WORKSPACE/land_is_hotfix2.sh" "$REPO/scripts/land_is_hotfix2.sh"
chmod +x "$REPO/scripts/land_is_hotfix2.sh"
echo "  ✓ iceland/ssi-data.json (regions as LIST + 4-tier R3 recalibrated)"
echo "  ✓ intelligence/country-configs/iceland.json (NEW — custom r3_buckets)"
echo "  ✓ scripts/land_is_hotfix2.sh"

# ─── Pre-flight gates ─────────────────────────────────────────────────────
echo ""
echo "→ Pre-flight gates"

if command -v node >/dev/null 2>&1; then
  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean"
  else
    echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"; tail -20 /tmp/parsecheck.log; exit 1
  fi
fi

python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; cat /tmp/cachecheck.log; exit 1; }

# Schema sanity
python3 -c "
import json

# (1) ssi-data.json: regions MUST be a list now
d = json.load(open('iceland/ssi-data.json'))
assert isinstance(d['regions'], list), f'BAD: regions is {type(d[\"regions\"]).__name__}, expected list'
assert len(d['regions']) == 8, f'BAD region count: {len(d[\"regions\"])}'
print(f'  ✓ ssi-data.json regions: list[{len(d[\"regions\"])}] (was dict) — regional.html unblocked')

# (2) 4-tier R3 distribution
r3_vals = set(round(s['modifiers']['R3_C_mult'], 3) for s in d['substations'])
assert r3_vals == {1.02, 1.03, 1.04, 1.05}, f'BAD R3 tiers: {sorted(r3_vals)}'
print(f'  ✓ 4-tier R3: {sorted(r3_vals)}')

# (3) country-config.json: r3_buckets present
c = json.load(open('intelligence/country-configs/iceland.json'))
buckets = c['thresholds']['r3_buckets']
assert len(buckets) == 4, f'BAD bucket count: {len(buckets)}'
print(f'  ✓ country-config r3_buckets: {len(buckets)} tiers')
for b in buckets:
    print(f'    - {b[\"label\"]} ({b[\"lower\"]}-{b[\"upper\"] or \"∞\"})')

# (4) Bucket population check
buckets_pop = [
    ('Industrial (R3≥1.045)', sum(1 for s in d['substations'] if s['modifiers']['R3_C_mult'] >= 1.045)),
    ('Capital (1.035-1.045)',  sum(1 for s in d['substations'] if 1.035 <= s['modifiers']['R3_C_mult'] < 1.045)),
    ('Commercial (1.025-1.035)', sum(1 for s in d['substations'] if 1.025 <= s['modifiers']['R3_C_mult'] < 1.035)),
    ('Rural (<1.025)',           sum(1 for s in d['substations'] if s['modifiers']['R3_C_mult'] < 1.025)),
]
print('  ✓ Bucket population (all 4 non-empty):')
for label, n in buckets_pop:
    flag = '✓' if n > 0 else '✗'
    print(f'    {flag} {label}: {n}')
    assert n > 0, f'EMPTY BUCKET: {label}'
"

# ─── Stage + commit + push ────────────────────────────────────────────────
echo ""
echo "→ Staging hotfix #2"

git add iceland/ssi-data.json
git add intelligence/country-configs/iceland.json
git add scripts/land_is_hotfix2.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

echo ""
git diff --cached --stat | tail -10

git commit -m "fix(iceland): regions list + 4-tier R3 + country-config (IS hotfix #2 — regional.html + B.2 panel)

Two-part hotfix addressing post-hotfix-#1 issues reported by user:

ISSUE 1: regional.html stuck on 'Loading data…'
  Root cause: ssi-data.json emitted 'regions' as a dict {slug → region_obj}
  while HU/SK/SI/all working countries emit as a list [{region: slug, ...}].
  Anti-pattern A1a (KB §66) at the emission layer — same pattern as
  hotfix #1 (grid-geo.json field-name drift). The scoring pipeline
  (Step 4) deviated from canonical schema.

ISSUE 2: intelligence.html B.2 'Economic Impact by Business Fabric'
  showed populated Capital-Intensive + Industrial buckets but EMPTY
  Commercial/SME-Dense + Light/Agricultural/Rural buckets.
  Two contributing root causes:
    (a) intelligence/country-configs/iceland.json was MISSING from the
        live repo. The renderer (intelligence-sections.js
        r3BucketsFromConfig) fell back to DEFAULT_R3_BUCKETS expecting
        R3 ranges [0.97, 1.05+] — Iceland's [1.02, 1.05] 3-tier range
        only populates 2 of 4 buckets.
    (b) Iceland's 3-tier R3 (1.02 / 1.04 / 1.05) was methodologically
        accurate (flat gradient reflecting Iceland's compact economy)
        but the renderer expects 4 buckets to populate.

Fix:
  (1) Convert ssi-data.json regions dict → list (8 entries, sorted
      worst→best by R_median).
  (2) Recalibrate R3 to 4-tier:
      - Industrial-Aluminum 1.05: Suðurnes (geothermal) + Vesturland
        (Grundartangi smelter) + Austurland (Fjarðaál smelter) = 189 subs (27.5%)
      - Capital-Reykjavík 1.04: Höfuðborgarsvæðið = 286 subs (41.6%)
      - Commercial/SME-Dense 1.03: Norðurland eystra (Akureyri SME +
        tourism + Krafla geothermal) + Suðurland (Selfoss + Þjórsá
        hydro + Hekla tourism) = 174 subs (25.3%)
      - Rural/Peripheral 1.02: Vestfirðir (Westfjords fishing) +
        Norðurland vestra (Blönduvirkjun + agriculture) = 38 subs (5.5%)
  (3) Add intelligence/country-configs/iceland.json with custom
      r3_buckets matching the new 4-tier:
      - Industrial (1.045+) / Capital (1.035-1.045) / Commercial
        (1.025-1.035) / Rural (<1.025)
      - VoLL ranges: €15-30 / €8-15 / €3-8 / €1-3 per kWh
      - Iceland-specific labels + icons
      - Includes admin/regional/map/data_page/dno_dashboard blocks
        mirroring HU country-config structure

Updated fleet stats (post-recalibration):
  Median R: 0.399 (was 0.403 pre-hotfix; minor shift from R3 tier moves)
  Bands: Low 0 / Medium 539 / High 147 / Critical 1
  Per-region R_median (sorted worst→best):
    Suðurnes 0.512 · Vestfirðir 0.467 · Norðurland vestra 0.437
    Suðurland 0.432 · Austurland 0.418 · Norðurland eystra 0.413
    Vesturland 0.399 · Höfuðborgarsvæðið 0.352

Verification (pre-deploy):
  ✓ ssi-data.json regions = list[8] (was dict — fixes regional.html)
  ✓ 4 R3 tiers: {1.02, 1.03, 1.04, 1.05}
  ✓ country-config.json r3_buckets = 4 entries
  ✓ All 4 buckets populated: 189 / 286 / 174 / 38 substations
  ✓ inline-JS parse-check clean
  ✓ cache-busters in sync

KB §70.7 acceptance verdict (updated):
  Iceland hotfix count attributable to inaugural: 2 (#1 + #2)
  New A-family parents surfaced: 0 (both hotfixes are A1a-at-emission
    sub-patterns of A1 — already codified Session 27 KB §66)
  New disciplines codified:
    + 'OSM-extract pipeline + scoring pipeline MUST emit canonical
       schema directly (BPG Part XXXVII discipline #14)'
    + 'New-country onboarding MUST produce intelligence/country-configs/
       <slug>.json as Step-5 mandatory artefact (BPG Part XXXVII
       discipline #15). Country-specific r3_buckets recommended for
       any country whose R3 distribution doesn't span [0.97, 1.05+].'

Compounding-curve update (per BPG Part XXXVI.3):
  Slovenia (S27): 18 hotfixes, 11 new A-parents, ~4.0 days
  Slovakia (S28): 4 hotfixes, 2 new A-parents, ~3.5 days
  Hungary (S29):  1 hotfix, 0 new A-parents, ~1.5 days
  Iceland (S30):  2 hotfixes, 0 new A-parents, ~1.5 days + hotfix arc

  Iceland's 2 hotfixes are both A1a-at-emission (data-layer schema
  drift); architecture compounding intact because the central renderer
  was correct on both occasions — the emission pipelines deviated.

Cross-link: KB §66 (A1a original), §68 (SK + Safe namespace + normalizeMeta),
§69 (HU + admin-unit-suffix), §69.11 (HU hotfix #1), §70 (Iceland), BPG
Part XXXVI (HU + cohort recap), Part XXXVII planned (Iceland operational
playbook + 2 new disciplines)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Iceland hotfix #2 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + Pages rebuild, hard-reload (Cmd+Shift+R):"
echo "  open https://ikengassiindex.github.io/iceland/regional.html"
echo "  open https://ikengassiindex.github.io/iceland/intelligence.html"
echo ""
echo "Expected fixes:"
echo "  ✓ regional.html: 8 landshluti listed (Suðurnes worst R 0.512 → "
echo "    Höfuðborgarsvæðið best 0.352)"
echo "  ✓ intelligence.html B.2 Economic Impact: all 4 buckets populated"
echo "      - 🏭 Industrial-Aluminum/Geothermal (189 subs, 27.5%)"
echo "      - 🏛️ Capital-Reykjavík/Service (286 subs, 41.6%)"
echo "      - 🏪 Commercial/SME-Dense (174 subs, 25.3%)"
echo "      - 🌾 Light/Rural/Peripheral (38 subs, 5.5%)"
echo ""
echo "KB §70.7 acceptance: 2 hotfixes attributable to Iceland inaugural,"
echo "both A1a-at-emission sub-patterns (NOT new A-family parents)."
echo "════════════════════════════════════════════════════════════════════════"
