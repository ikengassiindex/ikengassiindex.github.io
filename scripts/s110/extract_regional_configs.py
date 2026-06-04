#!/usr/bin/env python3
"""
S110.C-1 — Extract regional.html metadata for all 39 countries (v2 — full overrides).

For each <slug>/regional.html, pull:
  - descriptions.regional       ← <meta name="description" content="...">
  - regional.subheader          ← <p>...</p> inside page-header
  - regional.custom_header_html ← Colombia-style flex H1 with flag (if non-standard)
  - regional.extra_post_header  ← R3 tier cards / other narrative blocks (Colombia)
  - regional.ranking_tab_label  ← first tab-btn text
  - regional.compare_tab_label  ← second tab-btn text
  - regional.ranking_header     ← #tab-ranking h3 text
  - regional.ranking_count_text ← #ranking-count text
  - regional.ranking_column_header ← second <th> in ranking table
  - regional.compare_select_h3  ← "Select X to Compare" h3
  - regional.compare_a_label    ← div before #prov-a select
  - regional.compare_b_label    ← div before #prov-b select
  - regional.compare_empty_text ← #compare-tbody empty cell
  - regional.decomp_header      ← #tab-decomp h3
  - regional.decomp_subtext     ← #tab-decomp span.label-xs

In-place updates templates/configs/<slug>.yaml.

Usage:
  python3 scripts/s110/extract_regional_configs.py            # write
  python3 scripts/s110/extract_regional_configs.py --dry-run  # preview only
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.")
    sys.exit(1)

REPO_ROOT  = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = REPO_ROOT / "templates" / "configs"

# Regex patterns -----------------------------------------------------------
META_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]+)"', re.I)
TITLE_RE = re.compile(r'<title>([^<]+)</title>', re.I)
STANDARD_TITLE = "SSI Index — Regional Analysis"
# Page-header block — captures EVERYTHING between div.page-header start and end (the closing </div>)
# Handles both plain <h1> and Colombia's <h1 style="margin:0">Title — Colombia</h1>
PAGE_HEADER_RE = re.compile(
    r'<div class="page-header[^"]*">(.*?)</div>\s*\n\s*\n?\s*(?:<!--|<div class="tabs)',
    re.S | re.I
)
# Extra HTML INSIDE tab-ranking AFTER the ranking-table card — Colombia's R3 tier cards.
# Structure: <div id="tab-ranking"> ... <table>...</table> </div> [EXTRA HTML] </div>
# We capture everything between the </div> closing the ranking-table card and the </div>
# closing the tab-ranking outer div.
RANKING_EXTRA_RE = re.compile(
    r'<tbody id="ranking-tbody">.*?</tbody>\s*</table>\s*</div>\s*\n\s*(<!--[^\n]*\n\s*<div class="grid-[^>]+>.*?</div>\s*</div>)\s*\n\s*</div>\s*\n\s*<!-- Tab:',
    re.S | re.I,
)
H1_STD_RE = re.compile(r'^\s*<h1>Regional Analysis</h1>\s*$', re.M)
SUBHEADER_RE = re.compile(r'<p>(.*?)</p>', re.S)

TABS_RE = re.compile(
    r'<button class="tab-btn active"[^>]*>([^<]+)</button>\s*<button class="tab-btn"[^>]*>([^<]+)</button>',
    re.I | re.S
)
RANK_H3_RE = re.compile(r'<div id="tab-ranking">.*?<h3>(.*?)</h3>', re.S | re.I)
RANK_COUNT_RE = re.compile(r'<span[^>]*id="ranking-count"[^>]*>([^<]+)</span>', re.I)
RANK_COL_RE = re.compile(
    r'<tbody id="ranking-tbody">.*?',  # only finds tbody
    re.S
)
RANK_TH_RE = re.compile(
    r'<table class="data-table">\s*<thead>\s*<tr>.*?<th[^>]*>#</th>\s*<th[^>]*>([^<]+)</th>',
    re.S | re.I
)
COMPARE_H3_RE = re.compile(r'<div id="tab-compare"[^>]*>.*?<h3>(.*?)</h3>', re.S | re.I)
COMPARE_A_LABEL_RE = re.compile(r'<div class="label-xs"[^>]*>([^<]+)</div>\s*<select id="prov-a"', re.I | re.S)
COMPARE_B_LABEL_RE = re.compile(r'<div class="label-xs"[^>]*>([^<]+)</div>\s*<select id="prov-b"', re.I | re.S)
COMPARE_EMPTY_RE = re.compile(r'<tbody id="compare-tbody">\s*<tr><td[^>]*>([^<]+)</td>', re.I | re.S)
DECOMP_H3_RE = re.compile(r'<div id="tab-decomp"[^>]*>.*?<h3>(.*?)</h3>', re.S | re.I)
DECOMP_SUB_RE = re.compile(
    r'<div id="tab-decomp"[^>]*>.*?<h3>.*?</h3>\s*<span class="label-xs">([^<]+)</span>',
    re.S | re.I
)


def html_decode(s):
    """Decode the common HTML entities present in current pages back to native chars."""
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
    """Return dict of extracted strings, or {'_error': ...}.
    Reads from git HEAD (the last committed state) to avoid extracting from
    a locally-overwritten file. This makes extraction idempotent and safe to
    re-run after a botched build."""
    import subprocess
    try:
        html = subprocess.check_output(
            ['git', 'show', f'HEAD:{slug}/regional.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/regional.html"}
    out = {}

    m = META_RE.search(html)
    out['description'] = html_decode(m.group(1)) if m else None

    # Custom <title> override (only stored if non-standard)
    m_title = TITLE_RE.search(html)
    if m_title:
        title = html_decode(m_title.group(1).strip())
        out['page_title_override'] = title if title != STANDARD_TITLE else None
    else:
        out['page_title_override'] = None

    # Extra HTML inside tab-ranking (Colombia's R3 tier cards)
    m_rx = RANKING_EXTRA_RE.search(html)
    out['ranking_tab_extra_html'] = m_rx.group(1).strip() if m_rx else None

    # Page header: detect if it's the standard form or custom
    m_ph = PAGE_HEADER_RE.search(html)
    if m_ph:
        header_inner = m_ph.group(1).strip()
        # Standard form: just <h1>Regional Analysis</h1> + <p>...</p>
        if H1_STD_RE.search(header_inner):
            m_p = SUBHEADER_RE.search(header_inner)
            out['subheader'] = html_decode(m_p.group(1).strip()) if m_p else None
            out['custom_header_html'] = None
        else:
            # Non-standard — preserve the entire inner block as custom_header_html
            out['custom_header_html'] = header_inner
            out['subheader'] = None  # subheader subsumed into custom_header_html

    for key, rgx in [
        ('ranking_tab_label',    TABS_RE),
        ('ranking_header',       RANK_H3_RE),
        ('ranking_count_text',   RANK_COUNT_RE),
        ('ranking_column_header',RANK_TH_RE),
        ('compare_select_h3',    COMPARE_H3_RE),
        ('compare_a_label',      COMPARE_A_LABEL_RE),
        ('compare_b_label',      COMPARE_B_LABEL_RE),
        ('compare_empty_text',   COMPARE_EMPTY_RE),
        ('decomp_header',        DECOMP_H3_RE),
        ('decomp_subtext',       DECOMP_SUB_RE),
    ]:
        m = rgx.search(html)
        out[key] = html_decode(m.group(1).strip()) if m else None
    # compare_tab_label sits in TABS_RE second group
    m_tabs = TABS_RE.search(html)
    if m_tabs:
        out['ranking_tab_label'] = html_decode(m_tabs.group(1).strip())
        out['compare_tab_label'] = html_decode(m_tabs.group(2).strip())

    return out


def update_config(slug, extracted, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    # descriptions.regional
    cfg.setdefault('descriptions', {})
    if extracted.get('description'):
        cfg['descriptions']['regional'] = extracted['description']

    # regional block — full override capture
    reg = cfg.setdefault('regional', {})
    field_map = {
        'subheader':              'subheader',
        'custom_header_html':     'custom_header_html',
        'page_title_override':    'page_title_override',
        'ranking_tab_extra_html': 'ranking_tab_extra_html',
        'ranking_tab_label':      'ranking_tab_label',
        'compare_tab_label':      'compare_tab_label',
        'ranking_header':         'ranking_header',
        'ranking_count_text':     'ranking_count_text',
        'ranking_column_header':  'ranking_column_header',
        'compare_select_h3':      'compare_select_h3',
        'compare_a_label':        'compare_a_label',
        'compare_b_label':        'compare_b_label',
        'compare_empty_text':     'compare_empty_text',
        'decomp_header':          'decomp_header',
        'decomp_subtext':         'decomp_subtext',
    }
    for src, dst in field_map.items():
        v = extracted.get(src)
        if v is not None:
            reg[dst] = v
        elif dst in reg and src == 'custom_header_html':
            # If subheader was used in this run, drop any stale custom_header_html
            del reg[dst]

    # Preserve key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions','regional','map'):
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
    print(f"=== Extracting full regional override-set for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok = 0
    err = 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        # Diagnostic line — first few populated fields
        nonempty = {k: v for k, v in ex.items() if v}
        keys = list(nonempty.keys())[:5]
        custom = "CUSTOM-HEADER" if ex.get('custom_header_html') else ""
        tabs = (ex.get('ranking_tab_label','?'), ex.get('compare_tab_label','?'))
        print(f"  ✓ {slug:<14} fields={len(nonempty):2}  tabs={tabs}  {custom}")
        update_config(slug, ex, dry_run=dry_run)
        ok += 1

    print(f"\nUpdated {ok} configs, errors {err}")
    return 0 if err == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
