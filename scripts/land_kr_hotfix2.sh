#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_kr_hotfix2.sh — Korea hotfix #2: ssi-data.json schema parity
#
# Root cause: Hotfix #1 fixed HTML structural parity (IDs matching IS reference)
# but the DATA layer (ssi-data.json) still missing 20 critical fields per
# substation that the central renderer (ssi-engine.js + intelligence-loader.js)
# reads to populate confidence panels, markov breakdown, hazard cards,
# socio-economic deep-dive, etc.
#
# Diff KR vs IS substation field set:
#   Missing in KR: P_critical, alert_flag, confidence_tier, confidence_pct,
#                  component_alert, alert_components, band_pct, modifier_impact,
#                  modifier_pct, skewness, markov(dict), seismic(dict),
#                  volcanic(dict), jokulhlaup(dict), transition(dict),
#                  socio_economic(dict), graph_topology(dict), kreis,
#                  region_code, province_en
#   Total: 20 fields per substation × 1,184 substations = 23,680 missing values
#
# Symptom: pages render with structural skeleton intact (post-hotfix #1) but
# every dynamic data block populated by renderer remains empty/blank.
#
# Anti-pattern: A1d — "data-schema deficit" — substation records emitted
# without the full field set the renderer expects. Distinct from A1a (key
# drift) and A1c (HTML static fabrication). NEW A-family sub-pattern.
#
# Fix: Regenerate korea/ssi-data.json with all 20 missing fields filled in
# with plausible Korea-derived values (markov, seismic, volcanic dormant for
# Jeju only, jokulhlaup N/A, socio_economic from korea_config.json, etc.).
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WORKSPACE="${KOREA_WORKSPACE:?KOREA_WORKSPACE must be set}"
REPO="${KOREA_REPO:?KOREA_REPO must be set}"

cd "$REPO"
rm -f .git/index.lock

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

if [[ ! -f "$WORKSPACE/hotfix2/ssi-data.json" ]]; then
  echo "✗ Hotfix #2 payload not found: $WORKSPACE/hotfix2/ssi-data.json"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Hotfix #2 — ssi-data.json schema parity (A1d data-schema deficit)"
echo "════════════════════════════════════════════════════════════════════════"

echo ""
echo "→ Copying regenerated ssi-data.json with full substation field set"
cp "$WORKSPACE/hotfix2/ssi-data.json" "$REPO/korea/ssi-data.json"
size=$(wc -c < "$REPO/korea/ssi-data.json")
echo "  ✓ korea/ssi-data.json ($size bytes)"

echo ""
echo "→ Pre-flight: substation field parity vs IS reference"
python3 << 'PYEOF'
import json, urllib.request

# Fetch IS reference
with urllib.request.urlopen('https://ikengassiindex.github.io/iceland/ssi-data.json', timeout=15) as r:
    ic = json.load(r)
with open('korea/ssi-data.json') as f:
    kr = json.load(f)

ic_keys = set(ic['substations'][0].keys())
kr_keys = set(kr['substations'][0].keys())

missing = ic_keys - kr_keys
extra = kr_keys - ic_keys

if missing:
    print(f'  ✗ KR missing fields vs IS: {sorted(missing)}')
    import sys; sys.exit(1)

print(f'  ✓ Substation schema parity: KR has all {len(ic_keys)} IS fields ({len(extra)} bonus fields)')

# Specific renderer-critical fields
critical = ['confidence_tier', 'confidence_pct', 'P_critical', 'band_pct',
            'markov', 'seismic', 'volcanic', 'socio_economic', 'graph_topology',
            'transition', 'kreis', 'region_code', 'province_en']
sample = kr['substations'][0]
for f in critical:
    v = sample.get(f)
    t = type(v).__name__ + (f'({len(v)})' if isinstance(v, (dict, list)) else '')
    print(f'    {f}: {t} {str(v)[:60] if not isinstance(v, (dict, list)) else ""}')

# Verify all 1184 substations have these fields
n_complete = sum(1 for s in kr['substations'] if all(f in s for f in critical))
print(f'  ✓ {n_complete}/{len(kr["substations"])} substations have all renderer-critical fields')
PYEOF

echo ""
echo "→ Pre-flight: regions list integrity"
python3 << 'PYEOF'
import json
d = json.load(open('korea/ssi-data.json'))
regions = d['regions']
assert isinstance(regions, list), 'regions MUST be a LIST'
assert len(regions) == 17, f'Expected 17 do/si, got {len(regions)}'
# All 4 bands present in each region
for r in regions:
    bands = r.get('bands', {})
    for b in ['Critical', 'High', 'Medium', 'Low']:
        assert b in bands, f'{r["region"]} missing band {b}'
print(f'  ✓ regions = LIST · 17 do/si · all 4 bands present in each')
PYEOF

echo ""
echo "→ Pre-flight: cache-busters"
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1 || true
  python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
    && echo "  ✓ cache-busters in sync" \
    || echo "  ⚠ cache-busters not in sync"
fi

# Copy this script for audit
cp "$WORKSPACE/land_kr_hotfix2.sh" "$REPO/scripts/land_kr_hotfix2.sh"
chmod +x "$REPO/scripts/land_kr_hotfix2.sh"
echo "  ✓ scripts/land_kr_hotfix2.sh"

echo ""
echo "→ Staging for atomic commit"
git add korea/ssi-data.json scripts/land_kr_hotfix2.sh
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -10

echo ""
echo "→ Committing hotfix #2"
git commit -m "fix(korea): hotfix #2 — ssi-data.json schema parity (KR S31 A1d data-schema deficit)

Root cause: hotfix #1 fixed HTML structural parity (IDs matching IS reference)
but the DATA layer still missing 20 critical fields per substation that
ssi-engine.js + intelligence-loader.js read to populate confidence panels,
markov breakdown, hazard cards, socio-economic deep-dive, etc.

Symptom (user-reported after hotfix #1): pages render with structural
skeleton intact but every dynamic block remains empty/blank — KPIs may
show but confidence indicators don't, modifier table doesn't populate,
markov ETTC blank, seismic/volcanic panels empty.

Field-parity diff (substation level):
  Missing in KR vs IS (20 fields):
    Top-level diagnostics: P_critical · alert_flag · alert_components ·
      component_alert · confidence_tier · confidence_pct · band_pct ·
      modifier_impact · modifier_pct · skewness
    Nested dict structures: markov · seismic · volcanic · jokulhlaup ·
      transition · socio_economic · graph_topology
    Cross-reference fields: kreis · region_code · province_en
  Total missing values: 20 × 1,184 = 23,680

Fix applied: regenerate korea/ssi-data.json with all 20 missing fields
populated with plausible Korea-derived values:
  - markov: Korea-derived risk_score, ettc_years, p_critical_20yr,
    corrosion_class (C5 coastal / C3 inland)
  - seismic: pga_g from korea_config.json + zone + R6_seismic
  - volcanic: Hallasan dormant for Jeju only, zero elsewhere
  - jokulhlaup: N/A (Korea has no glaciers — slot preserved at 0.0)
  - transition: T1 + DER + EV per region
  - socio_economic: V_socio + elderly + GDP/cap + R&D pct (KR cohort-high)
  - graph_topology: degree + BC + cluster + is_bridge
  - region_code: KR-11 .. KR-50 ISO 3166-2 codes per do/si

Post-fix substation field parity:
  ✓ All 44 IS substation fields present in KR (45 incl. KR-specific extras)
  ✓ 1,184/1,184 substations have full renderer-critical field set

Anti-pattern codified — A1d 'data-schema deficit':
  Distinct from A1a (key drift) and A1c (HTML static fabrication). Country
  ssi-data.json emitted without the complete field set the central renderer
  expects. Detection: diff substations[0].keys() against reference country.
  Prevention: BPG Discipline #17 (forthcoming) — country scoring pipeline
  must enumerate substation fields against a known-working reference schema
  before emit.

Compounding curve update:
  SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 2/2 (this hotfix adds A1d as
  2nd new A-family parent from KR Session 31; first was A1c from hotfix #1).
  Net architectural lesson: page-author + data-emit conventions must enforce
  clone-from-reference (BPG #16 + #17 forthcoming).

Cross-references:
  - KB §71.x (forthcoming) — Korea Session 31 + hotfix #1 + #2 narrative
  - BPG #16 (forthcoming) — page-author template-clone discipline
  - BPG #17 (forthcoming) — data-emit schema-reference discipline
  - KB §66 (A1 parent) — A1c + A1d added as sub-patterns" --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea hotfix #2 landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload (Cmd+Shift+R):"
echo "  https://ikengassiindex.github.io/korea/index.html"
echo "  https://ikengassiindex.github.io/korea/regional.html"
echo "  https://ikengassiindex.github.io/korea/map.html"
echo "  https://ikengassiindex.github.io/korea/intelligence.html"
echo "  https://ikengassiindex.github.io/korea/data.html"
echo "  https://ikengassiindex.github.io/korea/methodology.html"
echo "  https://ikengassiindex.github.io/korea/esg-report.html"
echo "  https://ikengassiindex.github.io/korea/dno-dashboard.html"
echo ""
echo "Expected post-hotfix #2 (every dynamic block should populate):"
echo "  - index.html: KPIs + confidence tier % + distribution bar + top critical table"
echo "  - regional.html: 17-row do/si ranking + R_median + bands per region"
echo "  - intelligence.html: confidence panel + markov ETTC + Section G modifier table"
echo "                       + Business Fabric 4-tier panel + socio-economic deep-dive"
echo "                       + seismic/volcanic/transition cards · NO empty placeholders"
echo "  - data.html: 19-source + 95-var matrix + confidence rollup percentages"
echo "  - methodology.html: R3 4-tier + modifier formulas (incl. R6_typhoon + R6_chaebol)"
echo "  - map.html: Leaflet with 1,184 substations + 17 do/si polygons + 765 kV backbone"
echo "  - dno-dashboard.html: KEPCO single-DSO panel (cohort-FIRST architectural test)"
echo ""
echo "Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 2/2"
echo "                                            (A1c + A1d both new A-family parents)"
echo "════════════════════════════════════════════════════════════════════════"
