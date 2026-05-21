#!/usr/bin/env python3
"""
Option 3 — Cross-validation gate (KB §49.11).

After Monday's Stage 7e cron lands, compare the findings.json produced
by today's LOCAL parity sweep against the cron-produced
runtime-audit-{ISO}.json. Any country where the two disagree gets
flagged for manual review before we declare its patch "verified".

Two failure modes worth catching:

  1. A refresh ran between the two reports, changing the schema mid-
     stream. Benign but worth noting in the PR.
  2. The local report saw something the cron didn't (or vice versa).
     Real bug — either in the harness, the parity generator, or the
     workflow's environment.

Exit code: 0 if reports agree, 1 if disagreements are found.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


def load_local(path: Path) -> dict:
    """Load the local findings.json produced by generate_parity_report.py."""
    data = json.loads(path.read_text())
    return {
        s["slug"]: s
        for s in data.get("summary_by_country", [])
    }


def load_cron(path: Path) -> dict:
    """Re-derive a slug→summary map from a raw runtime-audit-*.json."""
    from generate_parity_report import build_country_summary
    raw = json.loads(path.read_text())
    summaries = build_country_summary(raw.get("per_country", []))
    return {s["slug"]: s for s in summaries}


def diff_country(slug: str, a: dict, b: dict) -> list[str]:
    """Return a list of human-readable difference strings; empty = agree."""
    diffs = []
    if a["status"] != b["status"]:
        diffs.append(f"status: local={a['status']} · cron={b['status']}")
    if a["critical_keys"] != b["critical_keys"]:
        diffs.append(
            f"critical_keys: local={a['critical_keys']} · cron={b['critical_keys']}"
        )
    if a["warning_keys"] != b["warning_keys"]:
        diffs.append(
            f"warning_keys: local={a['warning_keys']} · cron={b['warning_keys']}"
        )
    # Per-category missing-key sets
    cats = set(a.get("by_category", {})) | set(b.get("by_category", {}))
    for cat in sorted(cats):
        ka = set(a.get("by_category", {}).get(cat, {}).get("missing", []))
        kb = set(b.get("by_category", {}).get(cat, {}).get("missing", []))
        only_local = ka - kb
        only_cron  = kb - ka
        if only_local:
            diffs.append(f"{cat}: only-local missing {sorted(only_local)}")
        if only_cron:
            diffs.append(f"{cat}: only-cron  missing {sorted(only_cron)}")
    return diffs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--local", required=True,
                   help="findings.json from generate_parity_report.py")
    p.add_argument("--cron", required=True,
                   help="runtime-audit-{ISO}.json from Monday's workflow run")
    args = p.parse_args()

    # Add script dir to path so we can import the generator's helpers
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    local = load_local(Path(args.local))
    cron  = load_cron(Path(args.cron))

    all_slugs = sorted(set(local) | set(cron))
    disagreements = {}
    for slug in all_slugs:
        if slug not in local:
            disagreements[slug] = ["only in cron report"]
            continue
        if slug not in cron:
            disagreements[slug] = ["only in local report"]
            continue
        d = diff_country(slug, local[slug], cron[slug])
        if d:
            disagreements[slug] = d

    if not disagreements:
        print(f"✓ Reports agree on all {len(all_slugs)} countries.")
        print("  Safe to mark patched countries as 'verified' (KB §49.11).")
        sys.exit(0)

    print(f"✗ {len(disagreements)} country/countries disagree between local + cron reports:")
    print()
    for slug, diffs in disagreements.items():
        print(f"  {slug}:")
        for d in diffs:
            print(f"    - {d}")
    print()
    print("Investigation order:")
    print("  1. Check if a refresh ran between the two reports "
          "(git log --since=<local-time> --until=<cron-time>).")
    print("  2. Re-run the local audit and see if it now matches cron.")
    print("  3. If still divergent, inspect runtime_audit.py and "
          "generate_parity_report.py for non-deterministic behaviour.")
    sys.exit(1)


if __name__ == "__main__":
    main()
