#!/usr/bin/env python3
"""
S110.C-5 — Extract esg-report.html metadata for all 39 countries.

Reads from git HEAD (idempotency per Lesson 2). Captures:
  - descriptions.esg_report        ← <title>...</title>
  - esg_report.edition_badge       ← .label-xs preamble
  - esg_report.flag_emoji          ← <h1> flag span
  - esg_report.h1_suffix           ← optional H1 suffix (Greenland "— Greenland")
  - esg_report.badge_style         ← optional inline style (Greenland sage color)

Greenland (#749) is BESPOKE (693 lines vs 167-173 cohort). Skipped from the sweep
per Lesson 9. Extraction still records its config (for posterity) but build_pages.py
should leave it untouched.

Usage:
  python3 scripts/s110/extract_esg_configs.py            # write
  python3 scripts/s110/extract_esg_configs.py --dry-run  # preview
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

TITLE_RE = re.compile(r'<title>([^<]+)</title>', re.I)

# .label-xs preamble (edition badge). Anchor on the substring "ANNUAL ESG DISCLOSURE"
# to avoid matching other label-xs elements on the page.
BADGE_RE = re.compile(
    r'<div\s+class="label-xs"([^>]*)>(ANNUAL ESG DISCLOSURE[^<]+)</div>',
    re.I,
)

# Flag emoji + optional H1 suffix
H1_RE = re.compile(
    r'<h1>\s*<span[^>]*>([^<]+)</span>\s*([^<]+?)\s*</h1>',
    re.I | re.S,
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
    try:
        html = subprocess.check_output(
            ['git', 'show', f'HEAD:{slug}/esg-report.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/esg-report.html"}

    out = {'_lines': html.count('\n') + 1}

    m_title = TITLE_RE.search(html)
    out['title'] = html_decode(m_title.group(1).strip()) if m_title else None

    m_badge = BADGE_RE.search(html)
    if m_badge:
        # Extract optional inline style attrs (e.g. Greenland's sage color)
        attrs = m_badge.group(1).strip()
        m_style = re.search(r'style="([^"]+)"', attrs)
        if m_style:
            out['badge_style'] = m_style.group(1).strip()
        out['edition_badge'] = html_decode(m_badge.group(2).strip())

    m_h1 = H1_RE.search(html)
    if m_h1:
        out['flag_emoji'] = m_h1.group(1).strip()
        h1_text = html_decode(m_h1.group(2).strip())
        # Default form: "Substation ESG Report". Anything beyond that is a suffix.
        DEFAULT_H1 = "Substation ESG Report"
        if h1_text != DEFAULT_H1 and h1_text.startswith(DEFAULT_H1):
            out['h1_suffix'] = h1_text[len(DEFAULT_H1):].strip()

    return out


def update_config(slug, ex, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())

    cfg.setdefault('descriptions', {})
    if ex.get('title'):
        cfg['descriptions']['esg_report_title'] = ex['title']

    e = cfg.setdefault('esg_report', {})
    # title is per-country (18+ have custom forms with their country name).
    # Stored on every country so the template can emit it verbatim.
    if ex.get('title'):
        e['title'] = ex['title']
    fields = ['edition_badge', 'flag_emoji', 'h1_suffix', 'badge_style']
    for f in fields:
        v = ex.get(f)
        if v:
            e[f] = v
        elif f in e and f in ('h1_suffix', 'badge_style'):
            # No longer non-standard; drop optional override
            del e[f]

    # Preserve canonical key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data','methodology','index','esg_report'):
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
    print(f"=== Extracting esg-report.html metadata for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok, err, bespoke = 0, 0, 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        lines = ex.pop('_lines', 0)
        flags = []
        if lines > 250:
            flags.append(f'BESPOKE({lines}L)')
            bespoke += 1
        if ex.get('h1_suffix'):  flags.append(f'H1+{ex["h1_suffix"]!r}')
        if ex.get('badge_style'): flags.append('CUSTOM-STYLE')
        badge = (ex.get('edition_badge') or '?')[:60]
        flags_str = ' '.join(flags) if flags else ''
        print(f"  ✓ {slug:<14} {lines:>4}L  badge={badge!r:62}  {flags_str}")
        update_config(slug, ex, dry_run=dry_run)
        ok += 1

    print(f"\nUpdated {ok} configs, errors {err}, bespoke {bespoke}")
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
