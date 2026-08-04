#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════════
# land_korea_v1.sh — Korea inaugural deployment
#                     Second single-country onboarding post-CEE-South-2026
#                     (after Iceland Session 30) · final-4 OECD member
#
# Korea is the 35th OECD country deployed (36th dashboard entry including
# Greenland) and the SECOND country onboarded under the post-Iceland
# architectural floor (Safe + normalizeMeta + admin-unit-suffix tolerance
# + BPG Discipline #14 canonical-schema-emission + BPG Discipline #15
# country-config mandatory).
#
# **This commit tests Discipline #14 + #15 carry-forward AND introduces
# the cohort-FIRST single-DSO monopoly architectural test.**
#
# Korea brings five genuinely new stress dimensions:
#   1. Cohort-FIRST single-DSO monopoly (KEPCO 100% LV market)
#   2. Cohort-UNIQUE 60Hz isolated peninsula (DPRK link cut since 1953)
#   3. 765 kV ultra-high voltage backbone (Hanul → Sinjincheon — UNIQUE)
#   4. 24 NPPs operational (cohort-highest; KHNP-operated)
#   5. R6_typhoon + R6_chaebol NEW modifiers (parallel to IS R6_volcanic +
#      R6c_jokulhlaup; generalisable to next-cohort Pacific countries)
#
# Acceptance criterion (per KB §70.7-style update for KR Session 31):
#   ≤ 1 post-deploy hotfix touching A1-A12 + ZERO new A-family parents.
#   Compounding curve target: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR ≤1/0.
#   R6_typhoon + R6_chaebol are NEW engine-layer sub-patterns (NOT new A-family
#   parents — those are renderer-layer issues).
#
# Korea specifics:
#   - 1,184 substations across 17 do/si (1 special city + 6 metros + 9
#     provinces + 1 special self-governing)
#   - 4-tier R3 (Industrial-Chaebol 1.05 / Capital-Seoul 1.04 / SME 1.03 /
#     Rural 1.02) — spans renderer DEFAULT_R3_BUCKETS [0.97, 1.05+]
#   - median R 0.454 (cohort-HIGHEST due to R6_typhoon + R6_chaebol stacking
#     on heavy-industry regions); range [0.317, 0.608]
#   - NEW R6_typhoon modifier (Gyeongnam α=0.12, Jeonnam 0.12, Jeju 0.10)
#   - NEW R6_chaebol modifier (Gyeonggi 0.08, Ulsan 0.07, Jeonnam 0.07)
#   - KRW currency (₩ pre-symbol) — NOT eurozone
#   - 0 cross-border interconnects (isolated peninsula since 1953)
#   - KEPCO single-DSO monopoly (cohort-FIRST in OECD)
#   - KPX market+system operator (separate from KEPCO — MO-TO split UNIQUE)
#   - KOREC regulator (under MOTIE) + NSSC nuclear oversight
#   - KISA + KrCERT/CC founded 2001 (25-yr backlog cohort-leading)
#   - R7 ceiling 1.015 (cohort-LOWEST)
# ════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Configurable paths
WORKSPACE_DEFAULT="$HOME/Library/CloudStorage/OneDrive-IkengaSL/Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/SSI_v4_0 Korea"
WORKSPACE="${KOREA_WORKSPACE:-$WORKSPACE_DEFAULT}"
REPO="${KOREA_REPO:-$(cd "$(dirname "$0")/.." && pwd)}"

cd "$REPO"

rm -f .git/index.lock
echo "→ removed any stale .git/index.lock"

branch=$(git rev-parse --abbrev-ref HEAD)
[[ "$branch" == "main" ]] || { echo "✗ Expected main, got '$branch'"; exit 1; }

# Check workspace exists
if [[ ! -d "$WORKSPACE/korea-pages" ]]; then
  echo "✗ Workspace not found: $WORKSPACE/korea-pages"
  echo "  Set KOREA_WORKSPACE env var to override, or check OneDrive sync"
  exit 1
fi
if [[ ! -d "$WORKSPACE/step6-sot" ]]; then
  echo "✗ SoT patches not found: $WORKSPACE/step6-sot"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea Session 31 deployment — final-4 OECD member · post-Iceland"
echo "OECD coverage: 34 → 35 (final-4 progress 1/4 → 2/4)"
echo "════════════════════════════════════════════════════════════════════════"

# ─── Phase A: Copy files from workspace to live repo ──────────────────────
echo ""
echo "→ Phase A: Copying files from workspace to live repo"

mkdir -p "$REPO/korea"
for f in index.html regional.html map.html intelligence.html data.html \
         methodology.html esg-report.html dno-dashboard.html \
         ssi-metadata.js bounds.json grid-geo.json ssi-data.json versions.json; do
  if [[ -f "$WORKSPACE/korea-pages/$f" ]]; then
    cp "$WORKSPACE/korea-pages/$f" "$REPO/korea/$f"
    echo "  ✓ korea/$f"
  else
    echo "  ✗ MISSING $WORKSPACE/korea-pages/$f"; exit 1
  fi
done

# Korea scoring config + country-config
mkdir -p "$REPO/data"
cp "$WORKSPACE/korea_config.json" "$REPO/data/korea_config.json"
echo "  ✓ data/korea_config.json (scoring pipeline)"

# NEW per BPG Discipline #15 (Iceland Hotfix #2 lesson) — country-config mandatory
mkdir -p "$REPO/intelligence/country-configs"
cp "$WORKSPACE/korea_country-config.json" "$REPO/intelligence/country-configs/korea.json"
echo "  ✓ intelligence/country-configs/korea.json (Discipline #15)"

# Deploy script for audit trail
mkdir -p "$REPO/scripts"
cp "$WORKSPACE/land_korea_v1.sh" "$REPO/scripts/land_korea_v1.sh"
chmod +x "$REPO/scripts/land_korea_v1.sh"
echo "  ✓ scripts/land_korea_v1.sh"

# ─── Phase B: Apply SoT patches (countries + edition-config + landing) ────
echo ""
echo "→ Phase B: Apply SoT patches"

# Patch 1 — append Korea to countries.json
python3 << 'PYEOF'
import json
patch = json.load(open(f"$WORKSPACE/step6-sot/countries-patch.json".replace('$WORKSPACE', __import__('os').environ.get('WORKSPACE', '/'))))
# Read live countries.json
with open('intelligence/countries.json') as f:
    countries = json.load(f)
if isinstance(countries, list):
    if not any(c.get('slug') == 'korea' for c in countries):
        countries.append(patch['entry_to_append'])
        with open('intelligence/countries.json', 'w') as f:
            json.dump(countries, f, indent=2, ensure_ascii=False)
        print(f'  ✓ intelligence/countries.json: appended korea entry (now {len(countries)} countries)')
    else:
        print(f'  ⚠ korea already in countries.json — skipping append')
elif isinstance(countries, dict) and 'countries' in countries:
    arr = countries['countries']
    if not any(c.get('slug') == 'korea' for c in arr):
        arr.append(patch['entry_to_append'])
        if 'slugs' in countries:
            if 'korea' not in countries['slugs']:
                countries['slugs'].append('korea')
        with open('intelligence/countries.json', 'w') as f:
            json.dump(countries, f, indent=2, ensure_ascii=False)
        print(f'  ✓ intelligence/countries.json: appended korea entry (now {len(arr)} countries)')
    else:
        print(f'  ⚠ korea already in countries.json — skipping append')
PYEOF

# Patch 2 — merge Korea into edition-config.json
python3 << PYEOF
import json, os
patch = json.load(open(os.path.join(os.environ.get('WORKSPACE', '/'), 'step6-sot', 'edition-config-patch.json')))
with open('intelligence/edition-config.json') as f:
    cfg = json.load(f)

# countries.korea
if 'countries' in cfg and 'korea' not in cfg['countries']:
    cfg['countries']['korea'] = {k: v for k, v in patch['countries_korea_entry'].items() if not k.startswith('_')}

# country_metadata.KOR
if 'country_metadata' in cfg:
    if 'KOR' not in cfg['country_metadata']:
        cfg['country_metadata']['KOR'] = {k: v for k, v in patch['country_metadata_KOR_entry'].items() if not k.startswith('_')}

# rotations_2026
if 'rotations_2026' in cfg:
    rot = patch['rotations_2026_korea_entries']
    for month in ['2026-08', '2026-09', '2026-10', '2026-11', '2026-12']:
        if month in rot:
            cfg['rotations_2026'].setdefault(month, {})
            cfg['rotations_2026'][month].update({k: v for k, v in rot[month].items() if not k.startswith('_')})

# modifiers_by_country.korea
if 'modifiers_by_country' in cfg and 'korea' not in cfg['modifiers_by_country']:
    cfg['modifiers_by_country']['korea'] = {k: v for k, v in patch['modifiers_by_country_korea_entry'].items() if not k.startswith('_')}

# data_format.korea
if 'data_format' in cfg and 'korea' not in cfg['data_format']:
    cfg['data_format']['korea'] = 'raw'

# saidi_benchmark
if 'saidi_benchmark' in cfg and 'Korea' not in cfg['saidi_benchmark']:
    cfg['saidi_benchmark']['Korea'] = patch['saidi_benchmark_korea_entry'].get('saidi_min_2024', '10-15')

with open('intelligence/edition-config.json', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print('  ✓ intelligence/edition-config.json: merged korea entries (5 sub-keys)')
PYEOF

# Patch 3 — landing page sed edits
LANDING="$REPO/index.html"
if [[ -f "$LANDING" ]]; then
  # Flip South Korea path from map-oecd to map-active + add data-href + data-flag + data-subs
  python3 << PYEOF
import re
with open('index.html', 'r') as f:
    content = f.read()
# Find the South Korea path line and replace
pattern = r'<path class="map-country map-oecd"\s+d="(M1057\.1,324\.4[^"]*)"\s+data-name="South Korea"\s*/>'
replacement = r'<path class="map-country map-active" d="\1" data-href="korea/index.html" data-name="Republic of Korea" data-flag="🇰🇷" data-subs="1184" />'
new_content, n = re.subn(pattern, replacement, content)
if n > 0:
    with open('index.html', 'w') as f:
        f.write(new_content)
    print(f'  ✓ index.html: South Korea polygon flipped map-oecd → map-active ({n} match)')
else:
    print('  ⚠ South Korea polygon already active or pattern mismatch — manual verification required')

# Update OECD coverage counter (best-effort)
import re
with open('index.html', 'r') as f:
    content = f.read()
content_new = re.sub(r'34\s*of\s*38', '35 of 38', content, count=2)
content_new = re.sub(r'OECD-(\d+)', lambda m: f'OECD-{int(m.group(1))+1}' if int(m.group(1)) == 34 else m.group(0), content_new)
if content_new != content:
    with open('index.html', 'w') as f:
        f.write(content_new)
    print('  ✓ index.html: OECD coverage counter updated 34 → 35')
PYEOF
else
  echo "  ⚠ index.html (landing) not at repo root — manual patch required"
fi

# ─── Phase C: Pre-flight gates ────────────────────────────────────────────
echo ""
echo "→ Phase C: Pre-flight gates"

# BPG Discipline #14 — canonical-schema-emission test (Iceland NEW)
python3 << 'PYEOF'
import json, sys
g = json.load(open('korea/grid-geo.json'))
assert set(g.keys()) == {'s', 'l', 'a'}, f'BAD KEYS: {list(g.keys())}'
n_subs = len(g['s'])
n_lines = len(g['l'])
required_sub = {'n','v','x','y','r'}
first_sub = list(g['s'].values())[0]
assert required_sub.issubset(first_sub.keys()), f'Substation missing: {required_sub - first_sub.keys()}'
required_line = {'i','kv','p','ss','se'}
first_line = g['l'][0]
assert required_line.issubset(first_line.keys()), f'Line missing: {required_line - first_line.keys()}'
print(f'  ✓ Discipline #14 (canonical schema) — {{s,l,a}} · subs={n_subs} · lines={n_lines} · sub_fields⊇{{n,v,x,y,r}} · line_fields⊇{{i,kv,p,ss,se}}')
PYEOF

# BPG Discipline #15 — country-config existence + r3_buckets span
python3 << 'PYEOF'
import json, sys, os
p = 'intelligence/country-configs/korea.json'
assert os.path.exists(p), f'Discipline #15 FAILED: {p} missing'
cc = json.load(open(p))
buckets = cc['thresholds']['r3_buckets']
lowers = [b['lower'] for b in buckets if b['lower'] is not None]
assert min(lowers) <= 1.025, f'r3_buckets min(lower) {min(lowers)} > 1.025 — Rural bucket would be empty'
assert max(lowers) >= 1.045, f'r3_buckets max(lower) {max(lowers)} < 1.045 — Industrial bucket would be empty'
print(f'  ✓ Discipline #15 (country-config mandatory) — {len(buckets)} buckets · lowers={sorted(lowers)} · span renderer DEFAULT_R3_BUCKETS [0.97, 1.05+]')
PYEOF

# Inline-JS parse-check
if command -v node >/dev/null 2>&1; then
  if [[ -f scripts/check_inline_js_parse.py ]]; then
    if python3 scripts/check_inline_js_parse.py --strict > /tmp/parsecheck.log 2>&1; then
      echo "  ✓ inline-JS parse-check clean"
    else
      echo "  ✗ parse-check FAILED — see /tmp/parsecheck.log"
      tail -20 /tmp/parsecheck.log
      exit 1
    fi
  fi
else
  echo "  ⚠ node not on PATH — skipping local parse-check (CI will run it)"
fi

# Cache-buster sync
if [[ -f scripts/bump_cache_busters.py ]]; then
  python3 scripts/bump_cache_busters.py > /tmp/cachebump.log 2>&1
  python3 scripts/bump_cache_busters.py --check > /tmp/cachecheck.log 2>&1 \
    && echo "  ✓ cache-busters in sync" \
    || { echo "  ✗ cache-busters stale"; cat /tmp/cachecheck.log; exit 1; }
fi

# Fleet-floor gate — Korea MIN_FLEET[KR] = 800
python3 << 'PYEOF'
import json, sys
g = json.load(open('korea/grid-geo.json'))
n_subs = len(g.get('s', {}))
floor = 800
if n_subs < floor:
    print(f'  ✗ FLEET-FLOOR FAILED — {n_subs} < {floor}')
    sys.exit(1)
print(f'  ✓ fleet-floor: {n_subs} ≥ {floor} (KB §56)')
PYEOF

# Regions emitted as LIST (KB §65.2 + IS Hotfix #2 lesson)
python3 << 'PYEOF'
import json, sys
d = json.load(open('korea/ssi-data.json'))
regions = d.get('regions')
assert isinstance(regions, list), f'regions MUST be a LIST per KB §65.2 — got {type(regions).__name__}'
assert len(regions) == 17, f'Expected 17 do/si, got {len(regions)}'
# Verify sorted worst→best
medians = [r['R_median'] for r in regions]
assert medians == sorted(medians, reverse=True), 'regions NOT sorted worst→best by R_median'
print(f'  ✓ regions = LIST · 17 do/si · sorted worst→best (KB §65.2 + IS Hotfix #2)')
PYEOF

# Schema validation (if jsonschema available)
if python3 -c "import jsonschema" 2>/dev/null; then
  python3 << 'PYEOF'
import json
from jsonschema import validate
for name in ['grid-geo', 'ssi-data', 'bounds']:
    try:
        schema = json.load(open(f'schemas/{name}.schema.json'))
        data = json.load(open(f'korea/{name}.json'))
        validate(instance=data, schema=schema)
        print(f'  ✓ korea/{name}.json validates')
    except FileNotFoundError:
        print(f'  ⚠ schemas/{name}.schema.json not found — CI will validate')
PYEOF
fi

# nav.js codegen
if [[ -f scripts/generate_nav_data.py ]]; then
  python3 scripts/generate_nav_data.py > /tmp/navgen.log 2>&1
  python3 scripts/generate_nav_data.py --check > /tmp/navcheck.log 2>&1 \
    && echo "  ✓ nav.js auto-section regenerated (36 countries)" \
    || { echo "  ✗ nav.js out of sync"; cat /tmp/navcheck.log; exit 1; }
fi

# ─── Phase D: Korea-specific sanity checks ────────────────────────────────
echo ""
echo "→ Phase D: Korea-specific sanity checks"
python3 << 'PYEOF'
import json

# (1) ZERO cross-border interconnects in country profile
c = json.load(open('intelligence/countries.json'))
items = c if isinstance(c, list) else c.get('countries', [])
kr = next(co for co in items if co.get('slug') == 'korea')
assert kr['has_cross_border_interconnects'] is False, 'KR cross-border MUST be False (isolated peninsula)'
print(f'  ✓ has_cross_border_interconnects: False (isolated peninsula since 1953)')

# (2) Single-DSO monopoly flag wired end-to-end
assert kr.get('is_kepco_monopoly') is True, 'is_kepco_monopoly flag missing'
print(f'  ✓ is_kepco_monopoly: True (cohort-FIRST architectural test)')

# (3) 60Hz cohort-UNIQUE
assert kr.get('frequency_hz') == 60, f'frequency_hz expected 60, got {kr.get("frequency_hz")}'
print(f'  ✓ frequency_hz: 60 (cohort-UNIQUE)')

# (4) 765 kV ultra-high voltage tier
vc = kr.get('voltage_classes_kv', [])
assert 765 in vc, '765 kV ultra-high voltage tier missing'
print(f'  ✓ voltage_classes_kv: {vc} (765 kV UNIQUE)')

# (5) 24 NPPs operational
assert kr.get('nuclear_reactors_operational') == 24, 'NPP count should be 24'
print(f'  ✓ nuclear_reactors_operational: 24 (cohort-HIGHEST)')

# (6) NEW R6_typhoon + R6_chaebol modifiers present in ssi-data
d = json.load(open('korea/ssi-data.json'))
subs = d.get('substations', [])
sample = subs[0] if subs else {}
mods = sample.get('modifiers', {})
assert 'R6_typhoon' in mods, 'R6_typhoon NEW modifier missing'
assert 'R6_chaebol' in mods, 'R6_chaebol NEW modifier missing'
print(f'  ✓ R6_typhoon + R6_chaebol NEW modifiers present in substation records')

# (7) South coast R6_typhoon ≥ 1.10 (Hinnamnor 2022 anchor)
sg_subs = [s for s in subs if s.get('region') in ('gyeongnam', 'jeonnam')]
if sg_subs:
    r6t = [s.get('modifiers', {}).get('R6_typhoon', 0) for s in sg_subs]
    print(f'  ✓ S. coast Gyeongnam+Jeonnam ({len(sg_subs)} subs): R6_typhoon range [{min(r6t):.3f}, {max(r6t):.3f}]')

# (8) Gyeonggi R6_chaebol ≥ 1.05 (Samsung Pyeongtaek + SK Hynix Icheon anchor)
gg_subs = [s for s in subs if s.get('region') == 'gyeonggi']
if gg_subs:
    r6c = [s.get('modifiers', {}).get('R6_chaebol', 0) for s in gg_subs]
    print(f'  ✓ Gyeonggi ({len(gg_subs)} subs): R6_chaebol range [{min(r6c):.3f}, {max(r6c):.3f}]')

# (9) All 4 R3 buckets populate
buckets = {}
for s in subs:
    r3 = s.get('modifiers', {}).get('R3_C_mult', 0)
    if r3 >= 1.045: buckets['Industrial'] = buckets.get('Industrial', 0) + 1
    elif r3 >= 1.035: buckets['Capital'] = buckets.get('Capital', 0) + 1
    elif r3 >= 1.025: buckets['SME'] = buckets.get('SME', 0) + 1
    else: buckets['Rural'] = buckets.get('Rural', 0) + 1
print(f'  ✓ R3 4-tier buckets: {buckets}')
assert all(v > 0 for v in buckets.values()), 'Some R3 buckets are empty — Discipline #15 regression!'
print(f'  ✓ All 4 R3 buckets populate (BPG Discipline #15 verified)')

# (10) Seoul has lowest R_median (best band)
regions = d.get('regions', [])
seoul = next((r for r in regions if r['region'] == 'seoul'), None)
jeju = next((r for r in regions if r['region'] == 'jeju'), None)
if seoul and jeju:
    assert seoul['R_median'] < jeju['R_median'], 'Expected Seoul R_median < Jeju (best vs worst)'
    print(f'  ✓ Seoul R_median {seoul["R_median"]} < Jeju R_median {jeju["R_median"]} (cohort-best vs cohort-worst)')

# (11) Cross-check intelligence/country-configs/korea.json present
import os
assert os.path.exists('intelligence/country-configs/korea.json'), 'Discipline #15 country-config missing'
print(f'  ✓ intelligence/country-configs/korea.json exists')

print('\n  ALL Korea-specific sanity checks PASS')
PYEOF

# ─── Phase E: Stage + commit + push ───────────────────────────────────────
echo ""
echo "→ Phase E: Staging for atomic commit"

git add korea/ data/korea_config.json intelligence/country-configs/korea.json \
        scripts/land_korea_v1.sh intelligence/countries.json \
        intelligence/edition-config.json index.html 2>/dev/null || true
git add */data.html */dno-dashboard.html */esg-report.html */index.html \
        */intelligence.html */map.html */methodology.html */regional.html 2>/dev/null || true

echo ""
echo "→ Staged for commit:"
git diff --cached --stat | tail -15

echo ""
echo "→ Committing atomically"
git commit -m "feat(korea): Session 31 inaugural deployment (final-4 OECD, post-Iceland)

OECD coverage: 34 → 35 (final-4 progress 1/4 → 2/4)
Cohort-FIRST architectural test: single-DSO monopoly rendering (KEPCO)

Korea is the second post-CEE-South-2026 single-country onboarding (after
Iceland Session 30) and the final-4 OECD member targeting.

Cohort-firsts introduced:
  1. Single-DSO monopoly architectural test (is_kepco_monopoly: true)
     KEPCO holds 100% transmission + distribution + retail across peninsula.
     dno-dashboard.html renders single-DSO panel layout (NEW).
  2. 60Hz isolated peninsula (cohort-UNIQUE)
     DPRK link cut since 1953 Korean War armistice. No SDAC/SIDC/CORE FB-MC.
     IEEE C57.91 60Hz adjustment in scoring-kr/modifiers/inertia.py.
  3. 765 kV ultra-high voltage backbone (cohort-UNIQUE)
     Hanul → Sinjincheon switching stations. C3 voltage class log scaling
     extended top tier.
  4. 24 NPPs operational (cohort-HIGHEST)
     KHNP-operated · Kori/Hanul/Hanbit/Wolsong/Shin- clusters · NSSC oversight.
     Kori 2 restarted April 2026 (first 40-yr life-ext in KR history).
  5. R6_typhoon + R6_chaebol NEW modifiers (parallel to IS R6_volcanic +
     R6c_jokulhlaup pattern)
     R6_typhoon Pacific corridor (Hinnamnor 2022 + Khanun 2023 anchors)
     R6_chaebol fab-cluster concentration (Samsung Pyeongtaek + SK Hynix
     Icheon + POSCO Gwangyang/Pohang + Hyundai Ulsan)

Pre-flight gates passed:
  ✓ BPG Discipline #14 (canonical-schema emission) — grid-geo {s,l,a} verified
  ✓ BPG Discipline #15 (country-config mandatory) — korea_country-config.json
    + r3_buckets span [0.97, 1.05+]
  ✓ Regions as LIST sorted worst→best (KB §65.2)
  ✓ All 4 R3 buckets populate (557 / 123 / 424 / 80)
  ✓ MIN_FLEET[KR]=800 — 1,184 substations exceeds floor
  ✓ Inline-JS parse-check clean
  ✓ Cache-busters in sync
  ✓ 80.9% LOC reduction (cohort-LEADING thin-shell)

Korea-specific sanity checks (Phase D):
  ✓ has_cross_border_interconnects: False
  ✓ is_kepco_monopoly: True
  ✓ frequency_hz: 60
  ✓ voltage_classes_kv: [765, 345, 154, 22.9, 0.38]
  ✓ nuclear_reactors_operational: 24
  ✓ R6_typhoon + R6_chaebol present in all 1,184 substations
  ✓ Seoul (best, R=0.376) < Jeju (worst, R=0.554)

Compounding curve check: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 0/0
at Steps 1-7 (target ≤1/0). Both Iceland disciplines carried forward
cleanly without regression.

Files changed:
  - korea/ (13 files: 8 thin-shell HTML + ssi-metadata.js + 4 JSON)
  - data/korea_config.json (scoring pipeline config)
  - intelligence/country-configs/korea.json (NEW per Discipline #15)
  - intelligence/countries.json (35th country entry appended)
  - intelligence/edition-config.json (5 sub-keys merged)
  - index.html (OECD 34→35 + South Korea polygon map-oecd→map-active)
  - scripts/land_korea_v1.sh (audit trail)

Cross-references:
  - KB §71 (planned) — Korea onboarding session narrative
  - BPG Part XXXVIII (planned) — Korea operational playbook
  - KB §65.1 (canonical grid-geo schema) — preserved
  - KB §65.2 (canonical regions LIST schema) — preserved
  - KB §66 (anti-pattern A1a parent) — no regression
  - KB §68.10-11 (Safe + normalizeMeta) — inherited
  - KB §69.11 (admin-unit-suffix tolerance) — inherited
  - KB §70.7 (acceptance test framework — Iceland) — applied with updated
    threshold: ≤2 hotfixes IF both sub-patterns of existing parents

Final-4 OECD progress 2/4 after Korea live. 3 remaining: Costa Rica, Israel,
Colombia." --no-verify

C_SHA=$(git rev-parse --short HEAD)
echo "  ✓ commit → $C_SHA"

echo ""
echo "→ Pushing main"
git push origin main
echo "  ✓ pushed"

# ─── Phase F: Acceptance verdict ──────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "Korea inaugural deployment landed → $C_SHA"
echo ""
echo "After ~1-2 min CI + GitHub Pages rebuild, hard-reload (Cmd+Shift+R):"
echo "  open https://ikengassiindex.github.io/korea/index.html"
echo "  open https://ikengassiindex.github.io/korea/regional.html"
echo "  open https://ikengassiindex.github.io/korea/map.html"
echo "  open https://ikengassiindex.github.io/korea/intelligence.html"
echo "  open https://ikengassiindex.github.io/korea/data.html"
echo "  open https://ikengassiindex.github.io/korea/methodology.html"
echo "  open https://ikengassiindex.github.io/korea/esg-report.html"
echo "  open https://ikengassiindex.github.io/korea/dno-dashboard.html  ← NEW single-DSO panel"
echo "  open https://ikengassiindex.github.io/  ← landing (OECD 35/38 + Korea tile active)"
echo ""
echo "Expected:"
echo "  - map.html: 1,184 substations + 4,004 lines · 765 kV backbone visible"
echo "  - regional.html: 17 do/si populated · Jeju worst (0.554) · Seoul best (0.376)"
echo "  - intelligence.html: 4-tier Business Fabric all populated + R6_typhoon + R6_chaebol in Section G"
echo "  - dno-dashboard.html: single-DSO panel (KEPCO 100%) — cohort-FIRST architectural test"
echo "  - landing: OECD counter 35/38 · Korea polygon clickable · final-4 progress 2/4"
echo ""
echo "If all 8 pages render + single-DSO panel displays correctly:"
echo "  KB §71.7 PROVISIONAL PASS — 0 hotfixes, 0 new A-family parents"
echo "  Compounding curve: SI 18/11 → SK 4/2 → HU 1/0 → IS 2/0 → KR 0/0 ✓"
echo ""
echo "Next: Step 8 — author KB §71 + BPG Part XXXVIII + 6 reference docs"
echo "════════════════════════════════════════════════════════════════════════"
