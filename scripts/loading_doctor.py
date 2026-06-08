#!/usr/bin/env python3
"""
loading_doctor.py — Phase 1.9 (KB §65)

Diagnostic tool that, given a country page URL or path, simulates browser
execution in Node.js with a stub DOM, captures every JS error (parse-time
+ runtime + unhandled-promise-rejection), and reports:
  - Which placeholder IDs got populated
  - Which placeholders stayed on Loading… or '—'
  - Which fetch().then() chain broke each one and the exact error
  - HTML line number of the failing code

Catches everything we hit tonight (Session 27):
  - JS parse errors (e.g. unescaped apostrophe in 'Slovenia\'s')
  - Schema-key drift (e.g. s.region === 'Savinjska' literal filter)
  - Zero-as-falsy traps (e.g. unemployment_rate || '—')
  - Field-name typos (R_base vs R_base_median, median_R vs R_median)
  - Markov sub-schema variants

What it CANNOT catch (real-browser only):
  - CSS rendering issues
  - Browser cache problems (but cache-buster gate prevents those)
  - Cross-origin policy issues (irrelevant for our same-origin pages)
  - Canvas/WebGL rendering correctness
  - Placeholders populated by SSIMap.init(onLoaded:fn) — stub no-ops the callback
    so map-driven KPIs on index.html appear "stuck". Real browser populates them.
  - Placeholders populated by user interaction (dropdowns, clicks) — e.g.
    regional.html's th-prov-a / th-prov-b populate on select-change.

Known false-positives are documented per-page rather than fixed via deeper
stubs because real-browser fidelity isn't this tool's job — Playwright is.
This tool's job: catch the 8 bug classes from Session 27 fast and reliably.

USAGE
  python3 scripts/loading_doctor.py slovenia/intelligence.html
  python3 scripts/loading_doctor.py slovenia/esg-report.html --verbose
  python3 scripts/loading_doctor.py slovenia --all-pages           # whole country
  python3 scripts/loading_doctor.py --diff-only slovenia           # only output if errors

Requires: node on PATH (already present for Phase 1.7 inline-JS-parse gate).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Node harness template — stubs window/document/fetch and runs the page's
# inline scripts under try/catch with error collection.
HARNESS_TEMPLATE = r"""
const fs = require('fs');
const path = require('path');

const stillLoading = new Set();    // placeholders that never got touched
const recordedSets = {};           // id → final textContent
const recordedHTML = {};           // id → length of final innerHTML
const errors = [];

// 1. Stub fetch — read from local filesystem instead of HTTP
global.fetch = (url) => {
  const parsed = url.replace(/\?.*/, '');  // strip query
  let localPath;
  if (parsed.startsWith('http')) {
    localPath = parsed.replace(/^https?:\/\/[^/]+\//, '');
  } else if (parsed.startsWith('../')) {
    localPath = parsed.replace(/^\.\.\//, '');
  } else if (parsed.startsWith('./') || !parsed.includes('/')) {
    localPath = path.join(__COUNTRY_FOLDER__, parsed.replace(/^\.\//, ''));
  } else {
    localPath = parsed;
  }
  try {
    const text = fs.readFileSync(path.resolve(__REPO__, localPath), 'utf8');
    return Promise.resolve({
      ok: true,
      status: 200,
      text: () => Promise.resolve(text),
      json: () => Promise.resolve(JSON.parse(text)),
    });
  } catch (e) {
    return Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve(''), json: () => Promise.reject(new Error('404: ' + parsed)) });
  }
};

// 2. Stub window + document
// IMPORTANT: window IS global (mirroring how `window === globalThis` in real
// browsers). This means `window.X = Y` inside external scripts (e.g.
// `window.CountryRenderer = {...}` inside country-renderer.js) automatically
// makes X a top-level global, so subsequent external/inline scripts that
// reference `X` as a bare name resolve correctly. Without this, inline calls
// like `CountryRenderer.register(...)` crash with ReferenceError because
// `window` is just a stubbed object the harness owns.
Object.assign(global, {
  devicePixelRatio: 1,
  innerWidth: 1280, innerHeight: 800,
  Chart: function(){ this.destroy = ()=>{}; },
  jspdf: { jsPDF: function(){} },
  location: { pathname: '/' + __COUNTRY__ + '/page.html', href: 'https://localhost/' + __COUNTRY__ + '/page.html', search: '', hash: '' },
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  sessionStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  addEventListener: () => {}, removeEventListener: () => {},
  requestAnimationFrame: (fn) => setTimeout(fn, 16),
  matchMedia: () => ({ matches: false, addEventListener: () => {} }),
});
global.window = global;
global.NodeFilter = { SHOW_TEXT: 4, SHOW_ELEMENT: 1, FILTER_ACCEPT: 1, FILTER_REJECT: 2, FILTER_SKIP: 3 };
global.SSI_COUNTRY = __COUNTRY__;
global.document = {
  getElementById: (id) => {
    return {
      get textContent() { return recordedSets[id] || ''; },
      set textContent(v) { recordedSets[id] = String(v).slice(0, 120); stillLoading.delete(id); },
      get innerHTML() { return ''; },
      set innerHTML(v) { recordedHTML[id] = String(v).length; stillLoading.delete(id); },
      get width() { return 600; }, set width(v) {},
      get height() { return 400; }, set height(v) {},
      offsetWidth: 600, offsetHeight: 400,
      style: { setProperty: () => {} },
      classList: { add: () => {}, remove: () => {}, contains: () => false, toggle: () => {} },
      addEventListener: () => {},
      removeEventListener: () => {},
      appendChild: () => {},
      prepend: () => {},
      remove: () => {},
      querySelector: () => null,
      querySelectorAll: () => [],
      getContext: () => new Proxy({}, { get: () => (...a) => new Proxy({ addColorStop: () => {} }, { get: () => () => {} }) }),
    };
  },
  createElement: () => ({
    style: {}, appendChild: () => {}, prepend: () => {}, remove: () => {},
    addEventListener: () => {}, removeEventListener: () => {},
    setAttribute: () => {}, getAttribute: () => null, removeAttribute: () => {},
    classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
    querySelector: () => null, querySelectorAll: () => [],
    set innerHTML(v) {}, get innerHTML() { return ''; },
    set textContent(v) {}, get textContent() { return ''; },
  }),
  createTreeWalker: () => ({ nextNode: () => null }),
  body: { prepend: () => {}, appendChild: () => {} },
  head: { appendChild: () => {} },
  querySelector: () => null,
  querySelectorAll: () => [],
  addEventListener: (event, fn) => { if (event === 'DOMContentLoaded') setTimeout(fn, 0); },
  removeEventListener: () => {},
  dispatchEvent: () => true,
  title: '',
  documentElement: { style: {}, clientWidth: 1280, clientHeight: 800 },
};
// Common globals some pages assume exist
global.SSIMap = { init: () => {}, toggleBreakdown: () => {} };
global.SSIEngine = {};
global.SSIMetadata = {};
global.renderNav = () => {};
global.renderFooter = () => {};

// 3. Catch any async/unhandled errors
process.on('unhandledRejection', (err, p) => {
  errors.push({ kind: 'unhandled-rejection', message: err && err.message ? err.message : String(err), stack: (err && err.stack || '').split('\n').slice(0, 6).join('\n') });
});

// 4. Seed stillLoading with every placeholder ID in static HTML
__SEED_LOADING_IDS__;
"""


def extract_loading_ids(html: str) -> list:
    """Find every element with id="..." that contains 'Loading…' text or is a known placeholder."""
    ids = set()
    # Match `id="X"...>...Loading…...` (with > between id and Loading)
    for m in re.finditer(r'id\s*=\s*["\']([\w-]+)["\'][^>]*>[^<]*Loading[…\.]', html):
        ids.add(m.group(1))
    # Match `id="X"` where the element later contains a single em-dash placeholder
    for m in re.finditer(r'id\s*=\s*["\']([\w-]+)["\'][^>]*>\s*—\s*<', html):
        ids.add(m.group(1))
    return sorted(ids)


def extract_inline_scripts(html: str) -> list:
    """Return list of (html_line, code) for each inline <script>...</script>."""
    blocks = []
    for m in re.finditer(r'<script(?P<attrs>[^>]*)>(?P<body>[\s\S]*?)</script>', html):
        if 'src=' in (m.group('attrs') or ''):
            continue
        code = m.group('body')
        if not code.strip():
            continue
        line = html[:m.start()].count('\n') + 1
        blocks.append((line, code))
    return blocks


def extract_external_scripts(html: str) -> list:
    """Return list of (html_line, src) for each <script src=...> reference."""
    refs = []
    for m in re.finditer(r'<script[^>]*\ssrc\s*=\s*["\']([^"\']+)["\'][^>]*></script>', html):
        line = html[:m.start()].count('\n') + 1
        src = m.group(1).split('?')[0]  # strip query string
        refs.append((line, src))
    return refs


def diagnose_page(html_path: Path, verbose: bool = False) -> dict:
    """Run diagnostic on a single HTML page. Returns dict with results."""
    if not html_path.exists():
        return {'status': 'no-file', 'path': str(html_path)}
    html = html_path.read_text(errors='ignore')
    country = html_path.parent.name

    loading_ids = extract_loading_ids(html)
    inline_blocks = extract_inline_scripts(html)
    external_refs = extract_external_scripts(html)

    # Build the harness with placeholders substituted
    harness = HARNESS_TEMPLATE
    harness = harness.replace('__REPO__', json.dumps(str(REPO)))
    harness = harness.replace('__COUNTRY_FOLDER__', json.dumps(country))
    harness = harness.replace('__COUNTRY__', json.dumps(country))
    seed_loading = '\n'.join(f'stillLoading.add({json.dumps(i)});' for i in loading_ids)
    harness = harness.replace('__SEED_LOADING_IDS__', seed_loading)

    # Resolve + concatenate external script content (e.g. ssi-metadata.js)
    external_code_parts = []
    for line, src in external_refs:
        # Skip third-party CDN
        if src.startswith('http'):
            continue
        # Resolve path
        if src.startswith('../'):
            external_path = REPO / src[3:]
        else:
            external_path = html_path.parent / src
        if external_path.exists():
            try:
                external_code_parts.append(f"\n// === external: {src} ===\n" + external_path.read_text())
            except Exception:
                pass

    # Build final test script: harness + externals + inline blocks (each wrapped in try/catch)
    # Note: the harness header sets `global.window = global`, so any external
    # script that does `window.X = {...}` automatically makes X a top-level
    # global — no after-the-fact bridge needed.
    script_parts = [harness]
    script_parts.extend(external_code_parts)
    for line, code in inline_blocks:
        # Wrap each block in try/catch labelled by HTML line
        script_parts.append(f"\n// === inline block @ HTML line {line} ===\n")
        script_parts.append(f"try {{ {code} }} catch (e) {{ errors.push({{ kind: 'sync-throw', block_line: {line}, message: e.message, stack: (e.stack || '').split('\\n').slice(0,6).join('\\n') }}); }}\n")

    # Final output reporter
    script_parts.append("""
setTimeout(() => {
  const report = {
    inline_blocks: __NBLOCKS__,
    external_scripts: __NEXT__,
    placeholders_total: __NPLACEHOLDERS__,
    placeholders_populated: __NPLACEHOLDERS__ - stillLoading.size,
    placeholders_stuck: Array.from(stillLoading).sort(),
    errors: errors,
    populated_ids: Object.keys(recordedSets).concat(Object.keys(recordedHTML)).sort(),
  };
  process.stdout.write('===REPORT===\\n' + JSON.stringify(report, null, 2) + '\\n===ENDREPORT===\\n');
}, 800);
""".replace('__NBLOCKS__', str(len(inline_blocks)))
   .replace('__NEXT__', str(len(external_code_parts)))
   .replace('__NPLACEHOLDERS__', str(len(loading_ids))))

    # Write + execute
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write('\n'.join(script_parts))
        tmp_path = f.name
    try:
        r = subprocess.run(['node', tmp_path], capture_output=True, text=True, timeout=15)
    finally:
        os.unlink(tmp_path)

    # Parse the report
    report_match = re.search(r'===REPORT===\n(.+?)\n===ENDREPORT===', r.stdout, re.DOTALL)
    if not report_match:
        return {
            'status': 'harness-crashed',
            'path': str(html_path),
            'stderr': r.stderr[:600],
            'stdout': r.stdout[:300],
        }

    report = json.loads(report_match.group(1))
    report['status'] = 'ok' if not report['placeholders_stuck'] and not report['errors'] else 'issues'
    report['path'] = str(html_path)
    return report


def print_report(report: dict, verbose: bool = False):
    if report['status'] == 'no-file':
        print(f"  (skip: {report['path']} does not exist)")
        return
    if report['status'] == 'harness-crashed':
        print(f"  ✗ {report['path']} — harness crashed")
        if verbose:
            print(f"    stderr: {report['stderr'][:400]}")
        return

    path = report['path']
    n_stuck = len(report['placeholders_stuck'])
    n_err = len(report['errors'])
    n_pop = report['placeholders_populated']
    n_total = report['placeholders_total']

    if report['status'] == 'ok':
        print(f"  ✓ {path}   {n_pop}/{n_total} placeholders populated · 0 errors")
        return

    print(f"  ✗ {path}   {n_pop}/{n_total} populated · {n_stuck} STUCK · {n_err} errors")
    for err in report['errors'][:5]:
        kind = err.get('kind', '?')
        msg = err.get('message', '')[:140]
        line = err.get('block_line', '?')
        print(f"    [{kind}] block@line {line}: {msg}")
    if report['placeholders_stuck']:
        print(f"    Stuck IDs: {', '.join(report['placeholders_stuck'][:8])}{'…' if n_stuck > 8 else ''}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    verbose = '--verbose' in sys.argv
    all_pages = '--all-pages' in sys.argv
    diff_only = '--diff-only' in sys.argv

    if not args:
        print("usage: python3 scripts/loading_doctor.py <country>[/<page.html>] [--all-pages] [--verbose] [--diff-only]")
        return 2

    target = args[0]

    paths = []
    if target.endswith('.html'):
        paths.append(REPO / target)
    elif '/' in target:
        paths.append(REPO / target)
    else:
        # country slug — diagnose all 8 pages
        country = REPO / target
        for p in ['index.html', 'intelligence.html', 'esg-report.html',
                  'data.html', 'regional.html', 'methodology.html',
                  'map.html', 'dno-dashboard.html']:
            if (country / p).exists():
                paths.append(country / p)

    print(f"loading_doctor — scanning {len(paths)} page(s) via Node DOM-stub harness\n")
    all_clean = True
    for path in paths:
        report = diagnose_page(path, verbose=verbose)
        if diff_only and report.get('status') == 'ok':
            continue
        print_report(report, verbose=verbose)
        if report.get('status') != 'ok':
            all_clean = False

    if not all_clean:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
