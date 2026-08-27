#!/usr/bin/env python3
"""
ssi_dedupe_country.py — deduplicate one country and leave every check green.

    python3 scripts/ssi_dedupe_country.py spain              # dry run, writes nothing
    python3 scripts/ssi_dedupe_country.py spain --apply

Run from the repo root of ikengassiindex.github.io. This file and its three
siblings — ssi_dedupe_substations.py, ssi_refresh_canonical_figures.py,
ssi_refresh_landing_counts.py — live in scripts/; the script finds them beside
itself. The audit sidecar is written to ~/ssi-audit-trail by default, outside
the repo.

WHY THIS EXISTS
---------------
Deduplicating a country is one edit with four consequences, and skipping any of
them leaves a check red or, worse, leaves a wrong number on the site:

  1. dedupe            <slug>/ssi-data.json and grid-geo.json
  2. nav.js            regenerate — its footer figures are derived from the
                       data, so a data change makes it stale
  3. cache-busters     nav.js changed, so its ?v= hash changed on 273 pages
  4. canonical figures the country's own pages carry fleet.* spans set from
                       the old counts
  5. landing counts    the root index.html map tooltip carries data-subs

Steps 2 to 5 are each guarded by a CI check, so missing one fails the build
rather than reaching production — but only since 27 August 2026, when the
checks stopped hiding behind a failing step. Before that, a missed step went
to production silently. Japan's pages showed a two-generations-stale 5,981
through every remediation this year for exactly that reason.

The ordering is not arbitrary. nav.js must be regenerated before the busters
are bumped, or the bump records the pre-regeneration hash and the next check
fails.

WHAT IT DOES NOT DO
-------------------
It does not commit. The verification output is meant to be read before
anything is committed, and the exact git line is printed at the end.

It does not touch duplicate line geometries — roughly 298,660 cohort-wide.
That is a separate workstream requiring index remapping in grid-geo's
adjacency map, and it is not safe to bundle with substation removal.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path.cwd()

if not (ROOT / "intelligence" / "countries.json").exists():
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

args = [a for a in sys.argv[1:]]
APPLY = "--apply" in args
slugs = [a for a in args if not a.startswith("-")]
if len(slugs) != 1:
    sys.exit(f"usage: python3 {pathlib.Path(__file__).name} <country> [--apply]")
SLUG = slugs[0]

if not (ROOT / SLUG / "ssi-data.json").exists():
    sys.exit(f"ABORT: {SLUG}/ssi-data.json not found — check the slug.")

DEDUPE = HERE / "ssi_dedupe_substations.py"
FIGURES = HERE / "ssi_refresh_canonical_figures.py"
LANDING = HERE / "ssi_refresh_landing_counts.py"
for p in (DEDUPE, FIGURES, LANDING):
    if not p.exists():
        sys.exit(f"ABORT: {p.name} must sit beside this script.")

NAVGEN = ROOT / "scripts" / "generate_nav_data.py"
BUMP = ROOT / "scripts" / "bump_cache_busters.py"
AGREE = ROOT / "scripts" / "check_page_data_agreement.py"
PARSE = ROOT / "scripts" / "check_inline_js_parse.py"


def run(label, cmd, tail=6, fatal=True):
    print(f"\n\033[1m{label}\033[0m")
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True)
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    for l in out[-tail:]:
        print("   " + l)
    if r.returncode != 0 and fatal:
        sys.exit(f"\nABORT: {label} failed (exit {r.returncode}). Nothing further run.")
    return r.returncode


# ── 1. the edit ──
rc = run(f"1/5  deduplicate {SLUG}",
         [str(DEDUPE), SLUG] + (["--apply"] if APPLY else []), tail=7)

if not APPLY:
    print("\n  dry run — nothing written, nothing else run.")
    print(f"  Re-run with --apply once the numbers above are agreed:")
    print(f"      the grid-geo column is an independent count. delta 0 means")
    print(f"      the map and the canonical agree on the post-dedupe fleet,")
    print(f"      and edges 0 means no line loses an endpoint.")
    sys.exit(0)

# ── 2-5. the consequences, in dependency order ──
run("2/5  regenerate nav.js from the new data", [str(NAVGEN)], tail=2)
run("3/5  re-hash cache-busters (nav.js changed)", [str(BUMP)], tail=2)
run(f"4/5  reset {SLUG}'s published fleet figures", [str(FIGURES), SLUG, "--apply"], tail=3)
run("5/5  reset the landing-page map tooltips", [str(LANDING), "--apply"], tail=3)

# ── verification: the same four checks CI runs ──
print("\n\033[1m" + "=" * 62 + "\033[0m")
print("\033[1mverification — the four checks validate-schemas.yml runs\033[0m")
fails = 0
fails += run("  cache-busters", [str(BUMP), "--check"], tail=1, fatal=False)
fails += run("  nav.js in sync", [str(NAVGEN), "--check"], tail=1, fatal=False)
fails += run("  page/data agreement", [str(AGREE), "--all", "--strict"], tail=3, fatal=False)
fails += run("  inline JS parse", [str(PARSE), "--strict"], tail=2, fatal=False)

print("\n" + "=" * 62)
if fails:
    print(f"  {fails} check(s) FAILING — do not commit. Read the output above.")
    sys.exit(1)

changed = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
n = len([l for l in changed.stdout.splitlines() if l and not l.startswith("??")])
print(f"  all four green · {n} files changed")
print(f"\n  Review, then commit. Explicit paths, not `git add -A` — the tooling")
print(f"  now lives in scripts/, so -A would sweep an unrelated tooling edit")
print(f"  into a data commit:")
print(f"\n      git add {SLUG}/ssi-data.json {SLUG}/grid-geo.json nav.js index.html '*/*.html'")
print(f"      git status --short | grep -v '^M ' | head")
print(f"\n  The second line should print nothing — anything it prints is unstaged")
print(f"  and wants explaining before the commit.")
