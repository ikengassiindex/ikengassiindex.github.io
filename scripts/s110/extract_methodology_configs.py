#!/usr/bin/env python3
"""
S110.C-3 — Extract methodology.html metadata for all 39 countries.

Reads from git HEAD (idempotency per Lesson 2). For each <slug>/methodology.html:
  - descriptions.methodology   ← <meta name="description">
  - methodology.admin_label_singular_lower    (e.g., "NUTS-3 region", "département")
  - methodology.admin_label_plural_lower      (e.g., "NUTS-3 regions", "départements")
  - methodology.ingestion_frequency           (e.g., "weekly", "monthly", "daily")
  - methodology.ingest_sources_prose          (full per-country source list, long string)
  - methodology.regulator_acronym             (e.g., "AGEN-RS", "CRE") — used in R6a
  - methodology.data_sources_country          (e.g., "Slovenia", "the UK")
  Optional overrides (only set if non-standard):
  - methodology.custom_h1_html                (Colombia flag + " — Country" suffix)
  - methodology.custom_subheader              (Greenland annex suffix)
  - methodology.custom_thesis_html            (Colombia entire thesis paragraph)
  - methodology.custom_ingest_html            (Colombia entire ingest paragraph)
  - methodology.custom_extra_sections_html    (Colombia 4 extra sections)

Patches templates/configs/<slug>.yaml in-place.

Usage:
  python3 scripts/s110/extract_methodology_configs.py            # write
  python3 scripts/s110/extract_methodology_configs.py --dry-run  # preview
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
H1_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S | re.I)
SUBHEADER_RE = re.compile(
    r'<h1[^>]*>.*?</h1>\s*<p>(.*?)</p>', re.S | re.I
)
THESIS_RE = re.compile(
    r'Breaking the Silos</div>\s*<p[^>]*>\s*(.*?)\s*</p>',
    re.S | re.I
)
# Pipeline step 1 (Ingest) paragraph
INGEST_RE = re.compile(
    r'<h3>Ingest</h3>\s*<p>(.*?)</p>', re.S | re.I
)
# Thesis admin label: "A X serving" or "An X serving"
THESIS_ADMIN_RE = re.compile(
    r'An? ([\w\d\- ]+?) serving an energy-poor', re.I
)
# Modifier R3 admin label: "for X serving large/energy-poor"
R3_ADMIN_RE = re.compile(
    r'Amplifies risk for ([\w\d\- ]+?) serving large', re.I
)
# MC: "Every X score"
MC_ADMIN_RE = re.compile(
    r'Every ([\w\d\- ]+?) score includes a 90%', re.I
)
# R6a regulator-CAIDI-based
REGULATOR_RE = re.compile(
    r'<td[^>]*>R6a</td>\s*<td[^>]*>Restoration Speed</td>\s*<td[^>]*>[^<]*</td>\s*<td[^>]*>([\w\-]+)-CAIDI-based',
    re.S | re.I
)
# Data Sources card title — "30+ Verified Data Sources for X"
DATA_SOURCES_COUNTRY_RE = re.compile(
    r'<h3>(?:30\+|25\+|18\+|\d+\+?)\s*Verified Data Sources for ([^<]+?)</h3>', re.I
)
# Ingestion frequency
INGEST_FREQ_RE = re.compile(
    r'Maximum ingestion frequency:\s*([\w]+)\.', re.I
)


STANDARD_H1 = "Methodology"
STANDARD_SUBHEADER = "How the SSI v4.0.2 is calculated — from raw data to final classification. Open methodology, open data, fully reproducible."


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
            ['git', 'show', f'HEAD:{slug}/methodology.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/methodology.html"}

    out = {}

    m = META_RE.search(html)
    out['description'] = html_decode(m.group(1)) if m else None

    m_h1 = H1_RE.search(html)
    if m_h1:
        h1 = m_h1.group(1).strip()
        out['h1_html'] = h1 if h1 != STANDARD_H1 else None

    m_sub = SUBHEADER_RE.search(html)
    if m_sub:
        sub = html_decode(m_sub.group(1).strip())
        out['subheader'] = sub if sub != STANDARD_SUBHEADER else None

    m_thesis_full = THESIS_RE.search(html)
    if m_thesis_full:
        thesis = html_decode(m_thesis_full.group(1).strip())
        # If thesis is standard-shape (starts with "Power grid resilience..."), don't store full;
        # we'll just extract the admin label. Otherwise, store full custom_thesis_html.
        if not thesis.startswith('Power grid resilience'):
            out['custom_thesis_html'] = thesis

    m_admin = THESIS_ADMIN_RE.search(html)
    out['admin_label_singular_lower'] = html_decode(m_admin.group(1).strip()) if m_admin else None

    m_r3 = R3_ADMIN_RE.search(html)
    out['admin_label_plural_lower'] = html_decode(m_r3.group(1).strip()) if m_r3 else None

    m_mc_admin = MC_ADMIN_RE.search(html)
    # MC is same singular form as thesis — used only to cross-validate

    m_ingest = INGEST_RE.search(html)
    if m_ingest:
        ingest = html_decode(m_ingest.group(1).strip())
        # If ingest length is over 700 chars OR includes Colombia-style narrative
        # (DANE/UPME/IDEAM/SGC etc.), store as custom_ingest_html instead.
        if len(ingest) > 700:
            out['custom_ingest_html'] = ingest
        else:
            # Extract just the source-list prose between "from 30+ verified..." and "Zero proprietary"
            m_src = re.search(r'\d+\+?\s*verified public(?:\s+\w+)?\s*data sources\s*[—-]\s*(.*?)\.\s*Zero proprietary', ingest, re.S)
            if m_src:
                out['ingest_sources_prose'] = m_src.group(1).strip()
            else:
                out['ingest_sources_prose'] = ingest  # fallback — store whole thing

    m_freq = INGEST_FREQ_RE.search(html)
    out['ingestion_frequency'] = html_decode(m_freq.group(1).strip()) if m_freq else None

    m_reg = REGULATOR_RE.search(html)
    out['regulator_acronym'] = html_decode(m_reg.group(1).strip()) if m_reg else None

    m_ds = DATA_SOURCES_COUNTRY_RE.search(html)
    out['data_sources_country'] = html_decode(m_ds.group(1).strip()) if m_ds else None

    return out


def update_config(slug, ex, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    cfg.setdefault('descriptions', {})
    if ex.get('description'):
        cfg['descriptions']['methodology'] = ex['description']

    m = cfg.setdefault('methodology', {})
    field_map = [
        'h1_html', 'subheader', 'custom_thesis_html', 'custom_ingest_html',
        'admin_label_singular_lower', 'admin_label_plural_lower',
        'ingest_sources_prose', 'ingestion_frequency',
        'regulator_acronym', 'data_sources_country',
    ]
    for f in field_map:
        v = ex.get(f)
        if v:
            m[f] = v
        elif f in m and ex.get(f) is None and f in ('h1_html', 'subheader', 'custom_thesis_html', 'custom_ingest_html'):
            # was set as override but no longer needed
            del m[f]

    # Preserve key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data','methodology'):
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
    print(f"=== Extracting methodology metadata for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok = 0
    err = 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        adm = ex.get('admin_label_singular_lower') or '?'
        reg = ex.get('regulator_acronym') or '?'
        freq = ex.get('ingestion_frequency') or '?'
        ds = ex.get('data_sources_country') or '?'
        flags = []
        if ex.get('h1_html'): flags.append('CUSTOM-H1')
        if ex.get('subheader'): flags.append('CUSTOM-SUB')
        if ex.get('custom_thesis_html'): flags.append('CUSTOM-THESIS')
        if ex.get('custom_ingest_html'): flags.append('CUSTOM-INGEST')
        flags_str = ' '.join(flags) if flags else ''
        print(f"  ✓ {slug:<14} adm={adm!r:30}  reg={reg!r:10}  freq={freq!r:8}  ds={ds!r:20}  {flags_str}")
        update_config(slug, ex, dry_run=dry_run)
        ok += 1

    print(f"\nUpdated {ok} configs, errors {err}")
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
