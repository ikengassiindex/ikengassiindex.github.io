#!/usr/bin/env python3
"""Task #463 doc cascade — reframe band semantics across per-country docs.

Follow-on to Task #461 (per-country P5/P95 normalisation, commit 045f9e8b)
and Task #462 (cohort-wide extension, commit de671f20).

After per-country P5/P95 normalisation, the classification field of every
substation carries a within-country risk ranking rather than an
absolute-R threshold classification. The 5-band Extreme system remains
intact (Convention #78 BINDING mesh integrity preserved).

Files updated (per Convention #54 6-touch-point housekeeping cascade):

  1. methodology.html × 39 — line 117 band-definition summary + the
     Classification Bands visual card (adds missing Extreme card too,
     closing the pre-existing Phase 2B 5-column-grid-with-4-cards gap).

  2. intelligence.html × 39 — legend at line ~401 (adds Extreme dot).

  3. CLAUDE.md — separate manual addendum (not batch-scriptable).

Idempotent: skips files that carry TASK_463_MARKER comment.

Usage:
  python3 scripts/task_463_band_semantic_doc_cascade.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
logging.basicConfig(format="%(levelname)-7s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

TASK_463_MARKER = "task-463-band-normalisation-doc-cascade"


# ── methodology.html patches (surgical single-line replacements) ──────
# Each line in the file starts with a single leading ASCII space (0x20).

# Line 117 — the summary sentence
METHODOLOGY_LINE_117_OLD = (
    ' <p>Five bands (v4.2): Low (0.00&ndash;0.25), Medium (0.25&ndash;0.50), '
    'High (0.50&ndash;0.75), Critical (0.75&ndash;1.00), Extreme (1.00&ndash;1.30). '
    'Alert flags trigger when any single component exceeds its P95 fleet threshold.</p>'
)
METHODOLOGY_LINE_117_NEW = (
    f' <!-- {TASK_463_MARKER} (23 Jul 2026) — per-country P5/P95 normalisation '
    'per Task #461/462; classification field is now within-country ranked. -->\n'
    ' <p>Five bands (v4.2, per-country ranked): Low, Medium, High, Critical, '
    'Extreme. Classification is normalised per country using P5/P95 anchors of '
    'R_median &mdash; &ldquo;Critical&rdquo; means &ldquo;top-15% risk ranking within '
    'this country&rdquo; rather than an absolute cross-country threshold. Absolute '
    'R_median remains stored per substation (tooltip + intelligence panel) for '
    'LP-DD auditability. Alert flags trigger when any single component exceeds '
    'its P95 fleet threshold.</p>'
)

# Line 333 — Low card range label
LOW_RANGE_OLD = ' <div style="font-size:12px;color:var(--band-low);margin:4px 0">0.00 &ndash; 0.25</div>'
LOW_RANGE_NEW = ' <div style="font-size:12px;color:var(--band-low);margin:4px 0">Bottom ~22%</div>'

# Line 338 — Medium card range label
MEDIUM_RANGE_OLD = ' <div style="font-size:12px;color:var(--band-medium);margin:4px 0">0.25 &ndash; 0.50</div>'
MEDIUM_RANGE_NEW = ' <div style="font-size:12px;color:var(--band-medium);margin:4px 0">Next ~28%</div>'

# Line 343 — High card range label
HIGH_RANGE_OLD = ' <div style="font-size:12px;color:var(--band-high);margin:4px 0">0.50 &ndash; 0.75</div>'
HIGH_RANGE_NEW = ' <div style="font-size:12px;color:var(--band-high);margin:4px 0">Middle ~28%</div>'

# Line 348 — Critical card range label
CRITICAL_RANGE_OLD = ' <div style="font-size:12px;color:var(--band-critical);margin:4px 0">0.75 &ndash; 1.00</div>'
CRITICAL_RANGE_NEW = ' <div style="font-size:12px;color:var(--band-critical);margin:4px 0">Next ~15%</div>'

# Line 344 — High card description ("Investment priority" → "Above average")
HIGH_DESC_OLD = ' <div style="font-size:11px;color:var(--warm-grey)">Elevated risk<br>Investment priority</div>'
HIGH_DESC_NEW = ' <div style="font-size:11px;color:var(--warm-grey)">Elevated risk<br>Above average</div>'

# Line 349 — Critical card description
CRITICAL_DESC_OLD = ' <div style="font-size:11px;color:var(--warm-grey)">Severe vulnerability<br>Urgent intervention</div>'
CRITICAL_DESC_NEW = ' <div style="font-size:11px;color:var(--warm-grey)">Severe vulnerability<br>Investment priority</div>'

# Add missing Extreme card + methodology footnote — INJECT after Critical card
# The Critical card closes at line 350 (` </div>`) and the grid closes at line 351.
# We inject a new Extreme <div> block + a `<p>` footnote before ` </div>\n </div>`.
EXTREME_ANCHOR_OLD = (
    ' <div style="font-size:11px;color:var(--warm-grey)">Severe vulnerability<br>Investment priority</div>\n'
    ' </div>\n'
    ' </div>\n'
    ' </div>'
)
EXTREME_ANCHOR_NEW = (
    ' <div style="font-size:11px;color:var(--warm-grey)">Severe vulnerability<br>Investment priority</div>\n'
    ' </div>\n'
    ' <div style="text-align:center;padding:16px 12px;border-radius:var(--radius-sm);background:var(--band-extreme-bg)">\n'
    ' <div style="font-family:\'Playfair Display\',serif;font-size:24px;font-weight:700;color:var(--band-extreme)">Extreme</div>\n'
    ' <div style="font-size:12px;color:var(--band-extreme);margin:4px 0">Top ~5%</div>\n'
    ' <div style="font-size:11px;color:var(--warm-grey)">Cascade-critical<br>Urgent intervention</div>\n'
    ' </div>\n'
    ' </div>\n'
    ' <p style="font-size:11px;color:var(--warm-grey);margin-top:12px;font-style:italic">'
    'Task #461 (22 Jul 2026): band membership reflects within-country risk ranking '
    '(P5/P95 normalisation of R_median). Absolute R_median in tooltips is unchanged '
    'and remains the primary LP-DD auditable score. Convention #78 BINDING 5-band '
    'Extreme mesh preserved.</p>\n'
    ' </div>'
)


# ── intelligence.html — legend fix (add Extreme dot) ──────────────────
INTEL_LEGEND_OLD = (
    ' <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
    'background:var(--band-critical);margin-right:3px"></span>Critical</span>'
)
INTEL_LEGEND_NEW = (
    ' <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
    'background:var(--band-critical);margin-right:3px"></span>Critical</span>\n'
    f' <!-- {TASK_463_MARKER} — legend extended with Extreme -->\n'
    ' <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
    'background:var(--band-extreme);margin-right:3px"></span>Extreme</span>'
)


def _patch_methodology(path: Path, *, dry_run: bool) -> tuple[str, list[str]]:
    content = path.read_text()
    if TASK_463_MARKER in content:
        return ("SKIP", ["already patched"])
    notes = []
    new = content
    patches = [
        ("line 117 summary", METHODOLOGY_LINE_117_OLD, METHODOLOGY_LINE_117_NEW),
        ("Low range", LOW_RANGE_OLD, LOW_RANGE_NEW),
        ("Medium range", MEDIUM_RANGE_OLD, MEDIUM_RANGE_NEW),
        ("High range", HIGH_RANGE_OLD, HIGH_RANGE_NEW),
        ("Critical range", CRITICAL_RANGE_OLD, CRITICAL_RANGE_NEW),
        ("High desc", HIGH_DESC_OLD, HIGH_DESC_NEW),
        ("Critical desc", CRITICAL_DESC_OLD, CRITICAL_DESC_NEW),
    ]
    for name, old, replacement in patches:
        if old in new:
            new = new.replace(old, replacement, 1)
            notes.append(name)
        else:
            notes.append(f"MISS:{name}")
    # Extreme card injection depends on Critical desc being patched first
    if EXTREME_ANCHOR_OLD in new:
        new = new.replace(EXTREME_ANCHOR_OLD, EXTREME_ANCHOR_NEW, 1)
        notes.append("Extreme card injected")
    else:
        notes.append("MISS:Extreme anchor")
    if new == content:
        return ("NOCHANGE", notes)
    if dry_run:
        return ("WOULD-WRITE", notes)
    path.write_text(new)
    return ("WROTE", notes)


def _patch_intelligence(path: Path, *, dry_run: bool) -> tuple[str, list[str]]:
    content = path.read_text()
    if TASK_463_MARKER in content:
        return ("SKIP", ["already patched"])
    if INTEL_LEGEND_OLD not in content:
        return ("NOCHANGE", ["legend anchor not found"])
    new = content.replace(INTEL_LEGEND_OLD, INTEL_LEGEND_NEW, 1)
    if dry_run:
        return ("WOULD-WRITE", ["legend Extreme dot added"])
    path.write_text(new)
    return ("WROTE", ["legend Extreme dot added"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    slugs = json.loads((REPO_ROOT / "intelligence" / "countries.json").read_text())["slugs"]
    log.info(f"Task #463 doc cascade across {len(slugs)} countries "
             f"({'DRY-RUN' if args.dry_run else 'APPLY'})")

    tally = {"methodology": {}, "intelligence": {}}
    for slug in slugs:
        for fname, patcher in (("methodology", _patch_methodology),
                               ("intelligence", _patch_intelligence)):
            p = REPO_ROOT / slug / f"{fname}.html"
            if not p.exists():
                tally[fname].setdefault("MISSING", []).append(slug)
                continue
            status, notes = patcher(p, dry_run=args.dry_run)
            tally[fname].setdefault(status, []).append(slug)
            log.info(f"[{slug:14s}] {fname}.html → {status} :: {'; '.join(notes)}")

    print("\n═══ Tally ═══")
    for fname, buckets in tally.items():
        print(f"\n{fname}.html:")
        for status, ss in sorted(buckets.items()):
            print(f"  {status:12s} — {len(ss):2d}  {', '.join(ss[:5])}"
                  f"{' ...' if len(ss) > 5 else ''}")


if __name__ == "__main__":
    main()
