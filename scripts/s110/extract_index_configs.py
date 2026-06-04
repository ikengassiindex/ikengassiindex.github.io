#!/usr/bin/env python3
"""
S110.C-4 — Extract index.html metadata for all 39 countries.

Reads from git HEAD (idempotency per Lesson 2). Captures:
  - descriptions.index            ← <meta name="description">
  - index.og_description          ← <meta property="og:description">
  - index.subheader               ← full <p> text after page-header
  - index.kpi_total_sub           ← KPI #1 sub text (voltage + admin counts)
  - index.scale_sub_admin         ← Scale section's "X regions · N municipalities"
  - index.edition_label           ← "Edition 01 — Slovenia"
  - index.intelligence_teaser     ← Intelligence Report Teaser body text
  - index.top_critical_admin_label ← Table column header for region
  - index.quickfacts_regions      ← "12 NUTS-3 regions covered"
  Optional outlier overrides (Colombia):
  - index.h1_html                 ← Custom flag-prefixed H1 wrapper
  - index.tagline                 ← Custom secondary tagline

Usage:
  python3 scripts/s110/extract_index_configs.py            # write
  python3 scripts/s110/extract_index_configs.py --dry-run  # preview
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
OG_DESC_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]+)"', re.I)
# H1 inner — if non-standard, capture; standard is just "Systemic System Infrastructure Index"
# Some countries (Colombia) wrap H1 in a flex div with flag — capture that wrapper structure
PAGE_HEADER_RE = re.compile(
    r'<div class="page-header[^"]*">(.*?)<!-- ', re.S | re.I
)
# Subheader: first <p>...</p> immediately after the Playfair tagline div, before the
# "Operated as a non-profit" footer div. Works whether or not the `<!-- Page Header -->`
# comment exists, since we anchor on the Playfair font-family attribute (very stable across all 39).
SUBHEADER_RE = re.compile(
    r'<div style="font-family:\'Playfair Display\'[^"]*"[^>]*>[^<]+</div>\s*<p[^>]*>(.*?)</p>',
    re.S | re.I,
)
# Tagline: the div between h1 and <p>
TAGLINE_RE = re.compile(
    r'</h1>(?:.*?)<div style="font-family:[^"]*Playfair[^"]*"[^>]*>(.*?)</div>',
    re.S | re.I,
)
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S | re.I)
# KPI Substations Scored sub
KPI_TOTAL_SUB_RE = re.compile(
    r'<div class="kpi-label">Substations Scored</div>.*?<div class="kpi-sub"[^>]*>([^<]+)</div>',
    re.S | re.I,
)
# Scale section sub-admin info — captures trailing "· 212 občine" form.
# Anchors on scale-leaves line, then finds the next "X label · sublabel" line.
SCALE_SUB_ADMIN_RE = re.compile(
    r'id="scale-leaves"[\s\S]*?<div><strong>\d+</strong>[^<·]+·\s*([^<]+?)</div>',
    re.S,
)
# Edition label in Intelligence Report Teaser
EDITION_LABEL_RE = re.compile(
    r'<div style="font-family:[^"]*Playfair[^"]*"[^>]*>(Edition\s+\d+\s*[—-]\s*[^<]+)</div>',
    re.S | re.I,
)
# Intelligence teaser body
INTEL_TEASER_RE = re.compile(
    r'Monthly Intelligence Report</div>.*?</div>\s*<p[^>]*>([^<]+)</p>',
    re.S | re.I,
)
# Top Critical Substations admin column header
TOP_CRITICAL_ADMIN_RE = re.compile(
    r'<h3>Highest Risk Substations</h3>.*?<th>Substation</th>\s*<th>([^<]+)</th>',
    re.S | re.I,
)

STANDARD_H1 = "Systemic System Infrastructure Index"
STANDARD_TAGLINE = "The First Open Digital Twin Fusing Grid Risk with Societal Exposure"


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
    try:
        html = subprocess.check_output(
            ['git', 'show', f'HEAD:{slug}/index.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/index.html"}

    out = {}
    m = META_RE.search(html)
    out['description'] = html_decode(m.group(1)) if m else None

    m_og = OG_DESC_RE.search(html)
    out['og_description'] = html_decode(m_og.group(1)) if m_og else None

    # H1 inner — only stored as h1_html override if non-standard.
    # When non-standard, capture the page-header inner *up to but not including* the
    # Playfair tagline div (so the template can emit the tagline div separately from
    # the index.tagline string — Colombia case where the H1 is flag-wrapped).
    m_h1 = H1_RE.search(html)
    if m_h1:
        h1 = m_h1.group(1).strip()
        if h1 != STANDARD_H1:
            m_ph = PAGE_HEADER_RE.search(html)
            if m_ph:
                ph_inner = m_ph.group(1)
                tag_cut = ph_inner.find("font-family:'Playfair Display'")
                if tag_cut > 0:
                    # back up to the opening "<div" of that tagline block
                    div_cut = ph_inner.rfind('<div', 0, tag_cut)
                    out['h1_html'] = ph_inner[:div_cut].strip() if div_cut > 0 else ph_inner[:tag_cut].strip()
                else:
                    # fallback: cut at first <p>
                    pcut = ph_inner.find('<p>')
                    out['h1_html'] = (ph_inner[:pcut].strip() if pcut > 0 else ph_inner.strip())

    # Tagline — only stored as override if non-standard
    m_tag = TAGLINE_RE.search(html)
    if m_tag:
        tag = html_decode(m_tag.group(1).strip())
        if tag != STANDARD_TAGLINE:
            out['tagline'] = tag

    m_sub = SUBHEADER_RE.search(html)
    out['subheader'] = html_decode(m_sub.group(1).strip()) if m_sub else None

    m_kpi = KPI_TOTAL_SUB_RE.search(html)
    out['kpi_total_sub'] = html_decode(m_kpi.group(1).strip()) if m_kpi else None

    m_edition = EDITION_LABEL_RE.search(html)
    out['edition_label'] = html_decode(m_edition.group(1).strip()) if m_edition else None

    m_intel = INTEL_TEASER_RE.search(html)
    out['intelligence_teaser'] = html_decode(m_intel.group(1).strip()) if m_intel else None

    m_top = TOP_CRITICAL_ADMIN_RE.search(html)
    out['top_critical_admin_label'] = html_decode(m_top.group(1).strip()) if m_top else None

    m_scale = SCALE_SUB_ADMIN_RE.search(html)
    out['scale_sub_admin'] = html_decode(m_scale.group(1).strip()) if m_scale else None

    return out


def update_config(slug, ex, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    cfg.setdefault('descriptions', {})
    if ex.get('description'):
        cfg['descriptions']['index'] = ex['description']

    i = cfg.setdefault('index', {})
    fields = [
        'og_description', 'subheader', 'kpi_total_sub', 'scale_sub_admin',
        'edition_label', 'intelligence_teaser', 'top_critical_admin_label',
        'h1_html', 'tagline',
    ]
    for f in fields:
        v = ex.get(f)
        if v:
            i[f] = v
        elif f in i and f in ('h1_html', 'tagline'):
            # Was set as override; no longer needed — drop
            del i[f]

    # Preserve key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data','methodology','index'):
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
    print(f"=== Extracting index.html metadata for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok = 0
    err = 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        flags = []
        if ex.get('h1_html'): flags.append('CUSTOM-H1')
        if ex.get('tagline'): flags.append('CUSTOM-TAG')
        kpi = (ex.get('kpi_total_sub') or '?')[:40]
        edition = (ex.get('edition_label') or '?')[:30]
        top = (ex.get('top_critical_admin_label') or '?')[:20]
        flags_str = ' '.join(flags) if flags else ''
        print(f"  ✓ {slug:<14} kpi_sub={kpi!r:42}  edition={edition!r:32}  top_col={top!r:22}  {flags_str}")
        update_config(slug, ex, dry_run=dry_run)
        ok += 1

    print(f"\nUpdated {ok} configs, errors {err}")
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
