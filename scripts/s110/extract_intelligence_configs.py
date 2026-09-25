#!/usr/bin/env python3
"""
S110.C-6 — Extract intelligence.html for all 39 countries.

Architecture decision: SHELL + PER-COUNTRY BODY PARTIALS.
The intelligence page is highest-variance in the cohort (~80% of each page is
country-specific editorial narrative — Section D deep-dives, Section E SAIDI
context, Section F neural-net topics, Section G outlook). Templating the body
via override fields would mean encoding ~500 lines of narrative HTML per country
in YAML — not a win. Instead:

  * templates/intelligence.html.j2 = SHELL ONLY (head, scripts, footer, edition
    auto-patcher harness).
  * templates/partials/intelligence/<slug>.html = full <main>...</main> body
    extracted verbatim from each country's live intelligence.html.
  * Template uses {% include 'partials/intelligence/' + slug + '.html' %} to
    splice the body into the shell.

This script:
  1. Reads from git HEAD (idempotent per Lesson 2).
  2. Extracts the <main>...</main> + <footer>...</footer> block per country.
  3. Writes each to templates/partials/intelligence/<slug>.html.
  4. Captures `<title>` + edition auto-patcher anchor metadata into
     templates/configs/<slug>.yaml `intelligence:` block.

Usage:
  python3 scripts/s110/extract_intelligence_configs.py            # write
  python3 scripts/s110/extract_intelligence_configs.py --dry-run  # preview
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
PARTIAL_DIR = REPO_ROOT / "templates" / "partials" / "intelligence"

TITLE_RE = re.compile(r'<title>([^<]+)</title>', re.I)
META_DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]+)"', re.I)
# Page-specific inline <style> block in <head> (Greenland-style locked-card CSS)
HEAD_STYLE_RE = re.compile(r'<style>\s*([\s\S]*?)\s*</style>', re.I)
# Body block: from <main> all the way through the last </script> before </body>.
# Captures main + footer + (thin-shell footer scripts) + (edition auto-patcher).
# This is "everything between <body>'s body-top scripts and the closing </body>" minus
# the body-top scripts which are templated in the shell.
BODY_RE = re.compile(
    r"(<main[^>]*>[\s\S]*</script>)\s*(?:<!--[^>]*-->\s*)*</body>",
    re.I,
)
# Edition auto-patcher anchor month/year — captured for posterity
ANCHOR_RE = re.compile(
    r'monthsSinceAnchor\s*=\s*\(y-(\d{4})\)\*12\s*\+\s*\(m\+1\)\s*-\s*(\d{1,2})',
    re.I,
)


def extract_one(slug):
    try:
        html = subprocess.check_output(
            ['git', 'show', f'HEAD:{slug}/intelligence.html'],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {'_error': f"git HEAD has no {slug}/intelligence.html"}

    out = {'_lines': html.count('\n') + 1}

    m_title = TITLE_RE.search(html)
    out['title'] = m_title.group(1).strip() if m_title else None

    # Limit head-scanning to the actual <head>...</head> block
    head_block = html.split('</head>', 1)[0] if '</head>' in html else html

    m_desc = META_DESC_RE.search(head_block)
    out['description'] = m_desc.group(1).strip() if m_desc else None

    m_style = HEAD_STYLE_RE.search(head_block)
    out['head_style'] = m_style.group(1).strip() if m_style else None

    m_body = BODY_RE.search(html)
    out['body_html'] = m_body.group(1) if m_body else None

    m_anchor = ANCHOR_RE.search(html)
    if m_anchor:
        out['anchor_year'] = int(m_anchor.group(1))
        out['anchor_month'] = int(m_anchor.group(2))

    return out


def write_partial(slug, body_html, dry_run=False):
    PARTIAL_DIR.mkdir(parents=True, exist_ok=True)
    path = PARTIAL_DIR / f"{slug}.html"
    if not dry_run:
        path.write_text(body_html)
    return path


def update_config(slug, ex, dry_run=False):
    cfg_path = CONFIG_DIR / f"{slug}.yaml"
    cfg = yaml.safe_load(cfg_path.read_text())
    i = cfg.setdefault('intelligence', {})
    if ex.get('title'):
        i['title'] = ex['title']
    if ex.get('description'):
        i['description'] = ex['description']
    if ex.get('head_style'):
        i['head_style'] = ex['head_style']
    elif 'head_style' in i:
        # No longer needed; drop the override
        del i['head_style']
    if 'anchor_year' in ex:
        i['anchor_year'] = ex['anchor_year']
    if 'anchor_month' in ex:
        i['anchor_month'] = ex['anchor_month']

    # Preserve canonical key ordering
    new_order = {}
    for k in ('schema_version','slug','country_name','country_possessive',
              'fleet_count','admin','edition','descriptions',
              'regional','map','data','methodology','index','esg_report',
              'intelligence'):
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
    print(f"=== Extracting intelligence.html for {len(configs)} countries (dry_run={dry_run}) ===\n")

    ok, err, no_body = 0, 0, 0
    for cfg_path in configs:
        slug = cfg_path.stem
        ex = extract_one(slug)
        if '_error' in ex:
            print(f"  ✗ {slug:<14} {ex['_error']}")
            err += 1
            continue
        lines = ex.pop('_lines', 0)
        body = ex.get('body_html')
        if not body:
            print(f"  ✗ {slug:<14} NO BODY MATCH (lines={lines})")
            no_body += 1
            err += 1
            continue
        body_lines = body.count('\n') + 1
        title = (ex.get('title') or '?')[:50]
        anchor = ''
        if 'anchor_year' in ex:
            anchor = f"anchor={ex['anchor_year']}/{ex['anchor_month']:02d}"
        write_partial(slug, body, dry_run=dry_run)
        update_config(slug, ex, dry_run=dry_run)
        print(f"  ✓ {slug:<14} {lines:>4}L total → {body_lines:>4}L body  title={title!r:52}  {anchor}")
        ok += 1

    print(f"\nUpdated {ok} configs + partials, errors {err}, no_body {no_body}")
    return 0 if err == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
