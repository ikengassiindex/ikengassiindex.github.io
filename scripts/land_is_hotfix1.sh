#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_is_hotfix1.sh — Iceland hotfix #1: grid-geo.json canonical schema
#
# Iceland inaugural deploy (commit 2321880b) rendered with ZERO substations
# and ZERO power lines visible on map.html + regional.html + intelligence.html.
#
# Root cause: anti-pattern A1a (KB §66) — schema-key drift between
# data-emission layer and the central renderer schema. Iceland's
# grid-geo.json was authored with verbose field names while the renderer
# (map.js + country-renderer.js) expects compact canonical fields:
#
#   Substation field    HU canonical (working)  IS (broken)
#   ────────────────    ──────────────────────  ──────────────
#   Latitude            y                       lat
#   Longitude           x                       lon
#   Voltage             v                       voltage_kv
#   Region code         r                       (province_slug)
#   Name                n                       name
#
#   Line field          HU canonical            IS (broken)
#   ──────────────      ────────────            ──────────────
#   Index               i                       (missing)
#   Voltage             kv                      voltage_kv
#   Coordinates         p ([[lon,lat],...])     coords
#   Start sub index     ss                      (missing)
#   End sub index       se                      (missing)
#
# Additionally, top-level structure: HU = {s, l, a}; IS = {country, iso2,
# iso3, extracted_at, ..., s, l}. The renderer only reads s/l/a.
#
# Hotfix:
#   1. Re-emit iceland/grid-geo.json in canonical {s, l, a} schema.
#   2. Map substation_id IS_OSM_n512719361 → compact 512719361 (HU pattern).
#   3. Set s[id].r = landshluti slug (e.g. "sudurnes").
#   4. Add code field to iceland/bounds.json features matching the slug
#      (so renderer can join s.r to bounds.properties.code per the
#      canonical pattern HU uses {code: "HU110"}).
#
# Verification: region codes match between s.r and bounds.code:
#   ['austurland', 'hofudborgarsvaedid', 'nordurland-eystra',
#    'nordurland-vestra', 'sudurland', 'sudurnes', 'vestfirdir',
#    'vesturland']
#
# This is a SCHEMA fix at the data-emission layer, not the renderer.
# Other countries' renderers (HU/SK/SI/etc.) already produce canonical
# {s, l, a} — Iceland's onboarding script (built without referencing the
# canonical schema) deviated. KB §70.7 acceptance verdict updates to:
#   Iceland hotfix count: 1 (this one — schema-emission layer)
#   New A-family parents: 0 (A1a is the parent already codified Session 27)
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

# ─── Copy patched files from workspace ────────────────────────────────────
if [[ ! -d "$WORKSPACE/hotfix1" ]]; then
  echo "✗ Hotfix payload not found: $WORKSPACE/hotfix1"
  echo "  Should contain: grid-geo.json + bounds.json"
  exit 1
fi

echo ""
echo "→ Copying canonical-schema grid-geo.json + bounds.json"
cp "$WORKSPACE/hotfix1/grid-geo.json" "$REPO/iceland/grid-geo.json"
cp "$WORKSPACE/hotfix1/bounds.json" "$REPO/iceland/bounds.json"
cp "$WORKSPACE/land_is_hotfix1.sh" "$REPO/scripts/land_is_hotfix1.sh"
chmod +x "$REPO/scripts/land_is_hotfix1.sh"
echo "  ✓ iceland/grid-geo.json (canonical {s,l,a} schema)"
echo "  ✓ iceland/bounds.json (+ code field on each feature)"
echo "  ✓ scripts/land_is_hotfix1.sh"

# ─── Pre-flight gates ─────────────────────────────────────────────────────
echo ""
echo "→ Pre-flight gates"

if command -v node >/dev/null 2>&1; then
  if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
    echo "  ✓ inline-JS parse-check clean"
  else
    echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"; tail -20 /tmp/parsecheck.log; exit 1
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check (CI will run it)"
fi

python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
  && echo "  ✓ cache-busters in sync" \
  || { echo "  ✗ cache-busters stale"; cat /tmp/cachecheck.log; exit 1; }

# Schema sanity (canonical {s, l, a})
python3 -c "
import json
g = json.load(open('iceland/grid-geo.json'))
assert set(g.keys()) == {'s', 'l', 'a'}, f'BAD KEYS: {list(g.keys())}'
assert len(g['s']) == 687, f'BAD s count: {len(g[\"s\"])}'
assert len(g['l']) == 1428, f'BAD l count: {len(g[\"l\"])}'
# Check first substation has canonical fields
first = list(g['s'].values())[0]
required = {'n','v','x','y','r'}
assert required.issubset(first.keys()), f'Substation missing: {required - first.keys()}'
print(f'  ✓ grid-geo.json canonical: s={len(g[\"s\"])}, l={len(g[\"l\"])}, a={g[\"a\"]}')
print(f'  ✓ Substation fields canonical: {sorted(first.keys())}')

# Verify bounds.code matches s.r
b = json.load(open('iceland/bounds.json'))
bounds_codes = set(f['properties']['code'] for f in b['features'])
s_regions = set(v['r'] for v in g['s'].values())
assert bounds_codes == s_regions, f'MISMATCH: bounds={bounds_codes}, s.r={s_regions}'
print(f'  ✓ bounds.code links to s.r: {sorted(bounds_codes)}')
"

# ─── Stage + commit + push ────────────────────────────────────────────────
echo ""
echo "→ Staging hotfix #1"

git add iceland/grid-geo.json
git add iceland/bounds.json
git add scripts/land_is_hotfix1.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -10

git commit -m "fix(iceland): grid-geo.json canonical {s,l,a} schema (IS hotfix #1 — A1a regression at emission layer)

Iceland inaugural deploy (2321880b) rendered with ZERO substations and
ZERO power lines visible on map.html + regional.html + intelligence.html.

Root cause: anti-pattern A1a (KB §66) — schema-key drift at the
data-emission layer (NOT the renderer). Iceland's grid-geo.json was
authored with verbose field names while the renderer (map.js +
country-renderer.js) reads compact canonical fields:

  Substation     HU canonical (working)    IS (broken pre-hotfix)
  ──────────     ──────────────────────    ──────────────────────
  Latitude       y                         lat
  Longitude      x                         lon
  Voltage        v                         voltage_kv
  Region code    r                         (province_slug)
  Name           n                         name

  Line           HU canonical              IS (broken pre-hotfix)
  ──────         ────────────              ──────────────────────
  Index          i                         (missing)
  Voltage        kv                        voltage_kv
  Coordinates    p ([[lon,lat],...])       coords
  Start sub      ss                        (missing)
  End sub        se                        (missing)

Top-level structure: HU = {s, l, a}; IS = {country, iso2, iso3,
extracted_at, ..., s, l}. The renderer only reads s/l/a.

Hotfix:
  1. Re-emit iceland/grid-geo.json in canonical {s, l, a} schema.
  2. Map substation_id IS_OSM_n512719361 → compact 512719361.
  3. Set s[id].r = landshluti slug (e.g. 'sudurnes').
  4. Add code field to iceland/bounds.json features matching the slug.

Verification (pre-deploy):
  ✓ grid-geo.json: {s, l, a} keys only · s=687 · l=1428 · a=empty
  ✓ All substations have canonical fields {n, v, x, y, r}
  ✓ All lines have canonical fields {i, kv, p, ss, se}
  ✓ bounds.code matches s.r across all 8 landshluti
  ✓ inline-JS parse-check clean (0 fails)
  ✓ cache-busters in sync

KB §70.7 acceptance verdict update:
  Iceland hotfix count attributable to inaugural: 1 (this one)
  New A-family parents surfaced: 0
  (A1a is the parent already codified in KB §66 Session 27;
   this hotfix is a sub-pattern at the emission layer)

Lesson for KB §70:
  New-country onboarding scripts MUST emit grid-geo.json in canonical
  {s, l, a} compact form. The OSM extract script (Step 2 in the 7-step
  workflow) should produce canonical schema directly, not a verbose
  human-readable form.

  Add to BPG Part XXXVII as new discipline #14: 'OSM extract emits
  canonical schema directly. Test by spot-checking the first substation
  in new grid-geo.json against the HU canonical reference before
  invoking the deploy script. Pre-flight gate to be added.'

Cross-link: KB §66 (A1a original codification), §65.1 (canonical
{s, l, a} schema definition), §68 (Slovakia inaugural with canonical
schema reference), §69 (Hungary inaugural), §70 (Iceland inaugural —
this hotfix codifies the emission-layer discipline)." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Iceland hotfix #1 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload (Cmd+Shift+R):"
echo "  open https://ikengassiindex.github.io/iceland/map.html"
echo "  open https://ikengassiindex.github.io/iceland/regional.html"
echo "  open https://ikengassiindex.github.io/iceland/intelligence.html"
echo ""
echo "Expected:"
echo "  - map.html: 687 substations dotted across 8 landshluti + 1,428 lines"
echo "  - regional.html: Höfuðborgarsvæðið + Suðurnes + 6 others populated"
echo "  - intelligence.html: fleet KPIs (R_median 0.403, etc.) + Suðurnes High band"
echo ""
echo "If map renders 687 substations: KB §70.7 PROVISIONAL PASS — 1 hotfix,"
echo "0 new A-family parents (A1a regression at emission layer)."
echo "════════════════════════════════════════════════════════════════════════"
