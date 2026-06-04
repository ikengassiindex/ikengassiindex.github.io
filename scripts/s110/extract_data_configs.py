#!/usr/bin/env python3
"""
S110.C-2 — Extract data.html metadata for all 39 countries.

Reads from git HEAD (idempotency). For each <slug>/data.html, captures:
  - descriptions.data         ← <meta name="description">
  - data.country_adjective    ← layer E label "X Open Data"
  - data.source_registry_count ← span "X+ verified · all free & public"
  - data.data_layers[]        ← 11 entries: {code, vars, sources}

Patches templates/configs/<slug>.yaml in-place.

Usage:
  python3 scripts/s110/extract_data_configs.py            # write
  python3 scripts/s110/extract_data_configs.py --dry-run  # preview only
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.")
    sys.exit(1)

REPO_ROOT  = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "templates" / "configs"

META_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]+)"', re.I)
# Layer E "Country Adjective Open Data" — may have " + Energy Policy" suffix
# Also captures the optional suffix so the full label can be reconstructed
COUNTRY_ADJ_RE = re.compile(
    r'<td>([^<]+?) Open Data( \+ Energy Policy)?</td>', re.I
)
SOURCE_REGISTRY_RE = re.compile(
    r'<h3>Data Source Registry</h3>\s*<span[^>]*>([^<]+?) verified', re.I | re.S
)
# Data layer row — capture code (text), vars, sources
LAYER_ROW_RE = re.compile(
    r'<tr>\s*<td[^>]*>([A-I](?:\.\d)?)</td>\s*<td>[^<]+</td>\s*'
    r'<td class="num">(\d+)</td>\s*<td>[^<]*<span[^>]*>[^<]+</span></td>\s*'
    r'<td[^>]*>([^<]+)</td>\s*</tr>',
    re.S | re.I
)


def html_decode(s):
    if not s:
        return s
    return (s.replace('&hellip;', '…')
             .replace('&mdash;', '—')
             .replace('&ndash;', '–')
             .replace('&middot;', '·')
             .replace('&minus;', '−')
             .replace('&#39;', "'")
             .replace('&apos;', "'")
             .replace('&quot;', '"')
             .replace('&amp;', '&'))


def extract_one(slug):
    """Return dict, or {'_error': ...}"""
    try:
        html = subprocess.check_output(
            ['git', 'show', f'HEAD:{slug}/data.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/data.html"}

    out = {}
    m = META_RE.search(html)
    out['description'] = html_decode(m.group(1)) if m else None

    m_adj = COUNTRY_ADJ_RE.search(html)
    if m_adj:
        out['country_adjective'] = html_decode(m_adj.group(1).strip())
        # Track whether the page uses the extended "+ Energy Policy" label variant
        out['layer_e_extended'] = bool(m_adj.group(2))
    else:
        out['country_adjective'] = None
        out['layer_e_extended'] = False

    m_reg = SOURCE_REGISTRY_RE.search(html)
    out['source_registry_count'] = html_decode(m_reg.group(1).strip()) if m_reg else None

    # Extract all 11 data layer rows
    layers = []
    for m_row in LAYER_ROW_RE.finditer(html):
        code = m_row.group(1).strip()
        vars_n = int(m_row.group(2))
        sources = html_decode(m_row.group(3).strip())
        layers.append({'code': code, 'vars': vars_n, 'sources': sources})
    out['data_layers'] = layers
    return out


def update_config(slug, extracted, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    cfg.setdefault('descriptions', {})
    if extracted.get('description'):
        cfg['descriptions']['data'] = extracted['description']

    d = cfg.setdefault('data', {})
    if extracted.get('country_adjective'):
        d['country_adjective'] = extracted['country_adjective']
    # Always set layer_e_extended so the template knows which variant to render
    d['layer_e_extended'] = extracted.get('layer_e_extended', False)
    if extracted.get('source_registry_count'):
        d['source_registry_count'] = extracted['source_registry_count']
    if extracted.get('data_layers'):
        d['data_layers'] = extracted['data_layers']

    # Preserve key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data'):
        if k in cfg:
            new_order[k] = cfg[k]
    for k, v in cfg.items():
        if k not in new_order:
            new_order[k] = v

    if not dry_run:
        cfg_path.write_text(yaml.safe_dump(new_order, sort_keys=False, allow_unicode=True))


def main():
    dry_run = '--dry-run' in sys.argv
    configs = sorted(CONFIG_DIR.glob("*.yaml"))
    print(f"=== Extracting data.html metadata for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok = 0
    err = 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        layer_count = len(ex.get('data_layers') or [])
        adj = ex.get('country_adjective') or '?'
        reg = ex.get('source_registry_count') or '?'
        print(f"  ✓ {slug:<14} layers={layer_count}  adj={adj!r}  reg={reg!r}")
        update_config(slug, ex, dry_run=dry_run)
        ok += 1

    print(f"\nUpdated {ok} configs, errors {err}")
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
