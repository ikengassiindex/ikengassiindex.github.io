#!/usr/bin/env python3
"""
Refresh the root landing page's per-country substation counts — DRY RUN BY DEFAULT.

Run from the repo root of ikengassiindex.github.io:

    python3 ssi_refresh_landing_counts.py            # report only
    python3 ssi_refresh_landing_counts.py --apply    # rewrite index.html

THE DEFECT
----------
index.html carries a `data-subs` attribute on each country's map path, shown
in the hover tooltip. Measured 27 August 2026 against the live cohort:
15 of 39 countries display the wrong number.

    France              0   vs 175,660     shows zero
    United Kingdom  2,551   vs  59,744     23x under
    Austria           741   vs  14,720     20x under
    Sweden         11,399   vs   1,192     9.6x over
    Spain          30,222   vs  12,621     2.4x over
    Germany       187,714   vs 168,776
    ...and nine more

The figures are not random — they are frozen at whatever the count was when
that country last went through a remediation run:

    Sweden  11,399 - 10,207 cross-border substations stripped = 1,192   exact
    Spain   30,222 - 17,601 cross-border substations stripped = 12,621  exact
    Austria    741 = the post-Discipline-#36 June figure, before Wave 4
                     ingestion took Austria to 14,720

WHY IT DRIFTED
--------------
Nothing maintains these attributes on their own. scripts/refresh_country_counts.py
updates the root `data-subs` only as a side effect of a per-country
remediation pass, and that pass requires a matching
ssi-data.json.pre-remediate-*.backup to derive its "before" figure. Wave 4
ingestion, the Convention #79 sharding work and the cross-border strips did
not run it, so those countries' figures simply stopped moving.

This utility closes that gap: it reads each country's true count from its own
ssi-data.json and writes it to the attribute, with no dependency on a backup
pair and no notion of "before".

WHAT IT TOUCHES
---------------
Only the VALUE inside data-subs="...". Nothing else in index.html — no
markup, no styling, no layout, no other attribute. The operating rule on this
repo is that the rendering is never modified, only what feeds it; an attribute
value is the feed.

Counts are read Convention #79 shard-aware, so the sharded countries
(france, germany, italy, poland, uk, us) report their real fleet rather than
zero — which is how France came to display 0 in the first place.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()


def cohort_slugs() -> list[str]:
    cj = json.loads((REPO / "intelligence" / "countries.json").read_text())
    return sorted(c["slug"] for c in cj["countries"] if "slug" in c)


def true_count(slug: str) -> int | None:
    """Substations actually present, whatever the storage shape."""
    p = REPO / slug / "ssi-data.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    if isinstance(d, list):
        return len(d)
    if d.get("substations_shards"):
        n = 0
        for e in d["substations_shards"]:
            rel = e["path"] if isinstance(e, dict) else e
            sp = p.parent / Path(rel).name
            if sp.exists():
                q = json.loads(sp.read_text())
                n += len(q if isinstance(q, list) else (q.get("substations") or []))
        return n
    return len(d.get("substations") or [])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="rewrite (default: dry run)")
    args = ap.parse_args()

    root = REPO / "index.html"
    if not root.exists():
        sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

    html = root.read_text()
    changes, unchanged, missing = [], 0, []

    for slug in cohort_slugs():
        actual = true_count(slug)
        if actual is None:
            missing.append(slug)
            continue

        pat = re.compile(
            r'(data-href="' + re.escape(slug) + r'/index\.html"[^>]*?data-subs=")([^"]*)(")',
            re.IGNORECASE)
        m = pat.search(html)
        if not m:
            missing.append(slug)
            continue

        shown_raw = m.group(2)
        shown = int(shown_raw.replace(",", "").strip() or -1)
        if shown == actual:
            unchanged += 1
            continue

        new_val = f"{actual:,}"
        html = pat.sub(lambda mm: mm.group(1) + new_val + mm.group(3), html, count=1)
        changes.append((slug, shown_raw, new_val, actual - shown))

    print(f"{'country':<14}{'landing page':>14}{'true count':>12}{'correction':>13}")
    print("-" * 53)
    for slug, old, new, delta in sorted(changes, key=lambda c: -abs(c[3])):
        print(f"{slug:<14}{old or '(blank)':>14}{new:>12}{delta:>+13,}")
    print("-" * 53)
    print(f"  {len(changes)} corrected · {unchanged} already right · "
          f"{len(cohort_slugs())} countries")
    if missing:
        print(f"  no data-subs or no ssi-data.json: {missing}")

    if args.apply and changes:
        root.write_text(html)
        print("\n  index.html rewritten — data-subs values only, nothing else touched.")
    elif not args.apply:
        print("\n  dry run — nothing written. Add --apply to correct them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
