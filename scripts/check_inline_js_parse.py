#!/usr/bin/env python3
"""
check_inline_js_parse.py — Phase 1.7 (KB §65.4.7).

Extracts every inline <script> block from every country's HTML pages
and validates that each parses cleanly via `node --check`.

Catches the bug class that produced Slovenia's commit 5620a651:
    'Slovenia's industrial' (unescaped apostrophe) → entire Section D
    script block fails to parse → all its placeholders stay on Loading.

Static-HTML linters and JSON schema validators DO NOT catch this class.
Only attempting to actually parse the JS does.

USAGE:
  python3 scripts/check_inline_js_parse.py             # all countries
  python3 scripts/check_inline_js_parse.py slovenia    # one country
  python3 scripts/check_inline_js_parse.py --strict    # exit 1 on any fail

Requires: node (any modern version) on PATH.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COUNTRIES_JSON = REPO / 'intelligence' / 'countries.json'

# Pages to scan per country
PAGE_NAMES = [
    'index.html', 'intelligence.html', 'esg-report.html',
    'data.html', 'regional.html', 'methodology.html',
    'map.html', 'dno-dashboard.html',
]


def load_slugs():
    cj = json.loads(COUNTRIES_JSON.read_text())
    return sorted([c['slug'] for c in cj['countries'] if 'slug' in c])


def extract_inline_scripts(html: str) -> list:
    """Return list of (start_line, code) for each <script>...</script>
    block that has inline content (i.e. no src= attribute)."""
    blocks = []
    # Match <script>…</script> only when there's no 'src=' in the opening tag
    for m in re.finditer(r'<script(?P<attrs>[^>]*)>(?P<body>[\s\S]*?)</script>', html):
        attrs = m.group('attrs') or ''
        if 'src=' in attrs:
            continue  # external script — skip
        code = m.group('body')
        if not code.strip():
            continue
        start = html[:m.start()].count('\n') + 1
        blocks.append((start, code))
    return blocks


def parse_check_node(code: str) -> tuple[bool, str]:
    """Write code to a temp file, run `node --check`, return (ok, error_message)."""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        r = subprocess.run(
            ['node', '--check', tmp_path],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            return True, ''
        # Extract just the first SyntaxError line
        stderr = r.stderr.strip()
        err_match = re.search(r'(?:SyntaxError|ReferenceError|TypeError): .+', stderr)
        msg = err_match.group(0) if err_match else stderr.split('\n')[0]
        # Try to extract the offending line number
        line_match = re.search(r':(\d+)', stderr)
        line_no = line_match.group(1) if line_match else '?'
        return False, f'(JS line {line_no}) {msg[:140]}'
    finally:
        os.unlink(tmp_path)


def check_page(country: str, page: str) -> dict:
    """Check all inline scripts in a single page. Return per-page summary."""
    path = REPO / country / page
    if not path.exists():
        return {'status': 'no-file', 'blocks': 0, 'errors': []}
    html = path.read_text(errors='ignore')
    blocks = extract_inline_scripts(html)
    errors = []
    for start_line, code in blocks:
        ok, err = parse_check_node(code)
        if not ok:
            errors.append({'html_line': start_line, 'message': err})
    return {
        'status': 'ok' if not errors else 'fail',
        'blocks': len(blocks),
        'errors': errors,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    strict = '--strict' in sys.argv

    # Verify node is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('ERROR: node not found on PATH (required for --check). Install Node.js.')
        return 2

    slugs = args if args else load_slugs()
    print(f'Inline-JS parse-checking {len(slugs)} countries × up to {len(PAGE_NAMES)} pages each')
    print(f'(via `node --check`)')
    print()

    total_pages = total_blocks = total_errors = 0
    failing_pages = []

    for slug in slugs:
        page_results = []
        for page in PAGE_NAMES:
            res = check_page(slug, page)
            if res['status'] == 'no-file':
                continue
            total_pages += 1
            total_blocks += res['blocks']
            if res['errors']:
                total_errors += len(res['errors'])
                failing_pages.append((slug, page, res['errors']))
                page_results.append(f"{page}({len(res['errors'])}✗)")
            else:
                page_results.append(f"{page}({res['blocks']}✓)")
        if page_results:
            ok_count = sum(1 for p in page_results if '✗' not in p)
            mark = '✓' if ok_count == len(page_results) else '✗'
            print(f'  {mark} {slug:<13} {ok_count}/{len(page_results)} pages clean')

    print()
    print(f'─── SUMMARY ───────────────────────────')
    print(f'  Pages scanned:      {total_pages}')
    print(f'  Inline JS blocks:   {total_blocks}')
    print(f'  Failing blocks:     {total_errors}')
    print(f'  Failing pages:      {len(failing_pages)}')

    if failing_pages:
        print(f'\n─── FAILURE DETAILS ───')
        for slug, page, errors in failing_pages:
            print(f'\n  {slug}/{page}:')
            for err in errors:
                print(f"    HTML line ~{err['html_line']}: {err['message']}")

    if strict and total_errors:
        print(f'\nSTRICT MODE: {total_errors} parse error(s) → exit 1')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
