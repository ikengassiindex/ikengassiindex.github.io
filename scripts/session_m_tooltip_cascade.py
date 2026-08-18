#!/usr/bin/env python3
"""session_m_tooltip_cascade.py — Task #1145 (18 August 2026)

Extends the Session F R7 v2 tooltip cascade from the 3-country pilot
(spain / italy / france, committed `9dcd5cd0`) to the remaining 36
countries of the 39-country cohort per operator Gate B B-4a sign-off.

Insert point (locus)
--------------------
Section B "Cyber & Economic Exposure Monitor" — after the ``<p>...
Why this section exists ...</p>`` line inside the ``<div class="card"``
block. The block is identical byte-wise across all 39 countries (Convention
#7 documented-locus).

Insert block (verbatim from committed spain/intelligence.html line 224)
-----------------------------------------------------------------------
    <p style="font-size:12px;line-height:1.7;margin:10px 0 0 0;
              color:var(--muted-ink)"><em>R7 v2 CRA-anchored transition
    (Q3 2026 → Q1 2027 dual-write):</em> the R7 signal is entering a
    dual-write window where the legacy R7_cyber (DESI + ACN scalar proxy)
    co-exists with R7_cyber_v2 (CRA Article 14 + NIS2 Article 21
    register-anchored composite, Path C+D). Consumers may select either;
    substation audit trail carries <code>_r7_cyber_v2_source</code> when
    v2 populated.</p>

Cache-bust stamp
----------------
- Bumps ``?v=<any>`` in intelligence.html asset refs to ``?v=20260818-r7v2``
  to match Session F cache-bust marker.

Idempotency
-----------
- Skips any file that already contains the ``R7 v2 CRA-anchored transition``
  string (Session F cohort — spain / italy / france).
- Skips gracefully if the anchor paragraph cannot be located (visibly-honest
  per Convention #56).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOT = REPO_ROOT / "intelligence" / "countries.json"

TOOLTIP_MARKER = "R7 v2 CRA-anchored transition"

# Verbatim from committed spain/intelligence.html line 224 (commit 9dcd5cd0).
TOOLTIP_INSERT = (
    ' <p style="font-size:12px;line-height:1.7;margin:10px 0 0 0;'
    'color:var(--muted-ink)"><em>R7 v2 CRA-anchored transition '
    '(Q3 2026 → Q1 2027 dual-write):</em> the R7 signal is entering a '
    'dual-write window where the legacy R7_cyber (DESI + ACN scalar proxy) '
    'co-exists with R7_cyber_v2 (CRA Article 14 + NIS2 Article 21 '
    'register-anchored composite, Path C+D). Consumers may select either; '
    'substation audit trail carries <code>_r7_cyber_v2_source</code> when '
    'v2 populated.</p>\n'
)

ANCHOR_RE = re.compile(
    r'(<p style="font-size:\d+px;line-height:1\.7;margin:0"><strong>Why '
    r'this section exists:</strong>[^<]+precisely the anticipatory '
    r'intelligence that infrastructure digitalisation planning '
    r'requires\.</p>\n)'
)

CACHE_BUST_STAMP = "?v=20260818-r7v2"
CACHE_BUST_RE = re.compile(r'\?v=[0-9A-Za-z_.\-]+')

# Session F cohort already committed via 9dcd5cd0.
SESSION_F_PILOT = {"spain", "italy", "france"}


def process_country(slug: str, dry_run: bool = False) -> dict:
    """Return a per-country result dict."""
    path = REPO_ROOT / slug / "intelligence.html"
    result = {"slug": slug, "path": str(path), "status": "unknown",
              "tooltip_inserted": False, "cache_stamps_bumped": 0}
    if not path.exists():
        result["status"] = "MISSING_FILE"
        return result
    text = path.read_text(encoding="utf-8")

    if TOOLTIP_MARKER in text:
        # Already carries Session F block (spain / italy / france pilot).
        result["status"] = "ALREADY_HAS_TOOLTIP_SKIP"
        # Still bump any lingering pre-Session-F cache stamps to keep parity.
        new_text, n_bumps = CACHE_BUST_RE.subn(CACHE_BUST_STAMP, text)
        result["cache_stamps_bumped"] = n_bumps
        # No write — Session F already committed the stamp.
        return result

    # Locate the "Why this section exists" paragraph.
    m = ANCHOR_RE.search(text)
    if not m:
        result["status"] = "ANCHOR_NOT_FOUND_SKIP"
        return result

    # Insert the tooltip immediately after the anchor paragraph.
    insertion = m.group(1) + TOOLTIP_INSERT
    new_text = text[: m.start()] + insertion + text[m.end():]

    # Cache-bust: bump every ?v=... stamp to Session F's `?v=20260818-r7v2`.
    new_text, n_bumps = CACHE_BUST_RE.subn(CACHE_BUST_STAMP, new_text)
    result["cache_stamps_bumped"] = n_bumps

    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    result["status"] = "OK_WROTE_TOOLTIP_AND_CACHE_BUST"
    result["tooltip_inserted"] = True
    return result


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    slugs = json.loads(SOT.read_text())["slugs"]

    print(f"Session M · R7 v2 tooltip cascade extension · cohort={len(slugs)}  "
          f"pilot_already_committed={sorted(SESSION_F_PILOT)}  dry_run={dry_run}")
    print("-" * 78)

    wrote = skipped_pilot = anchor_missing = 0
    per_country = []
    for slug in slugs:
        r = process_country(slug, dry_run=dry_run)
        per_country.append(r)
        if r["status"] == "OK_WROTE_TOOLTIP_AND_CACHE_BUST":
            wrote += 1
        elif r["status"] == "ALREADY_HAS_TOOLTIP_SKIP":
            skipped_pilot += 1
        elif r["status"] == "ANCHOR_NOT_FOUND_SKIP":
            anchor_missing += 1
        print(f"  [{slug:16s}] {r['status']:36s}  "
              f"tooltip={r['tooltip_inserted']}  "
              f"?v_bumps={r['cache_stamps_bumped']}")
    print("-" * 78)
    print(f"Summary: wrote={wrote}  skipped_already_pilot={skipped_pilot}  "
          f"anchor_missing={anchor_missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
