#!/usr/bin/env python3
"""
ssi_dedupe_country.py — deduplicate one country and leave every check green.

    python3 scripts/ssi_dedupe_country.py spain              # dry run, writes nothing
    python3 scripts/ssi_dedupe_country.py spain --apply
    python3 scripts/ssi_dedupe_country.py spain --apply --dirty-ok

--apply refuses to start when the working tree already has modifications. A
data commit should carry one country's dedupe and its four consequences and
nothing else. --dirty-ok overrides, and the pre-existing files are then
reported separately from the ones this run wrote.

The closing summary counts only what this run changed. It used to count the
whole working tree, which on 27 August 2026 reported "277 files changed" for a
run that wrote almost nothing — the tree was already carrying an earlier
apply — and cost twenty minutes to unpick.

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
    sys.exit(f"usage: python3 scripts/{pathlib.Path(__file__).name} "
             f"<country> [--apply] [--dirty-ok]")
SLUG = slugs[0]

if not (ROOT / SLUG / "ssi-data.json").exists():
    sys.exit(f"ABORT: {SLUG}/ssi-data.json not found — check the slug.")


def tree_state():
    """{path: status} for everything git considers changed. Taken before and
    after, so this run can report what IT wrote rather than what it found."""
    r = subprocess.run(["git", "status", "--porcelain"],
                       capture_output=True, text=True)
    out = {}
    for line in r.stdout.splitlines():
        if len(line) > 3:
            out[line[3:].strip().strip('"')] = line[:2].strip()
    return out


BEFORE = tree_state()

if APPLY and BEFORE and "--dirty-ok" not in args:
    print(f"\nABORT: {len(BEFORE)} file(s) already modified before this run.\n")
    for p in sorted(BEFORE)[:12]:
        print(f"    {BEFORE[p]:<3} {p}")
    if len(BEFORE) > 12:
        print(f"    ... and {len(BEFORE) - 12} more")
    print("\n  A data commit should carry one country's dedupe and its four")
    print("  consequences, nothing else. Commit or stash the above first.")
    print("\n  On 27 August 2026 a tree in exactly this state made a no-op run")
    print("  look like a 277-file change, and cost twenty minutes to unpick.")
    print("\n  If these changes genuinely belong with this dedupe, re-run with")
    print("  --dirty-ok and they will be reported separately.")
    sys.exit(2)

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
BANDS = ROOT / "scripts" / "check_bands_match_classification.py"


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
print("\033[1mverification — the four checks CI runs, plus bands-vs-data\033[0m")
fails = 0
fails += run("  cache-busters", [str(BUMP), "--check"], tail=1, fatal=False)
fails += run("  nav.js in sync", [str(NAVGEN), "--check"], tail=1, fatal=False)
fails += run("  page/data agreement", [str(AGREE), "--all", "--strict"], tail=3, fatal=False)
fails += run("  inline JS parse", [str(PARSE), "--strict"], tail=2, fatal=False)
# Fifth gate, added 28 Aug 2026. The four above all passed on a us dedupe that
# published Low 0.0% over substations that were 22.6% Low, because every one of
# them compares the page to the manifest or the manifest to itself. This one
# compares the manifest to the substations.
fails += run("  bands match the data", [str(BANDS), SLUG, "--strict"],
             tail=8, fatal=False)

print("\n" + "=" * 62)
if fails:
    print(f"  {fails} check(s) FAILING — do not commit. Read the output above.")
    sys.exit(1)

AFTER = tree_state()
written = sorted(set(AFTER) - set(BEFORE))
preexisting = sorted(set(BEFORE) & set(AFTER))

# What the five steps are entitled to touch. Anything else is worth a look
# before it goes into a commit describing a dedupe.
def expected(p):
    """What this country's chain is entitled to have changed.

    Decided by location, not by filename — a country's chain writes inside
    that country's directory, plus the two shared files and the cohort's HTML
    pages. The previous version listed name prefixes and missed
    germany/ssi-data-substations-*.json entirely, because a shard does not
    start with "germany/ssi-data.json". It printed a git add line without the
    nine shards, which would have committed a manifest claiming 108,016
    substations over shard files still holding 168,776.

    Anything a future step adds inside the country directory is covered by
    construction. Guessing filename shapes is what failed.
    """
    return (p.startswith(SLUG + "/")
            or p in ("nav.js", "index.html")
            or (p.endswith(".html") and "/" in p))

unexpected = [p for p in written if not expected(p)]

# Staging is decided by what the chain OWNS, not by what this run happened to
# write. sweden's canonical was modified by the restore and the pipeline before
# the wrapper started; building the git add line from `written` alone left it
# out, and the line would have committed the pages without the data.
stage_set = sorted(p for p in AFTER if expected(p))
found_not_ours = sorted(p for p in preexisting if not expected(p))

print(f"  all five green")
print(f"\n  written by this run : {len(written)} file(s)")
if preexisting:
    print(f"  already modified    : {len(preexisting)} file(s), untouched by this run")
    for p in preexisting[:8]:
        own = "" if expected(p) else "   <-- not part of this country's chain"
        print(f"                        {p}{own}")
    if len(preexisting) > 8:
        print(f"                        ... and {len(preexisting) - 8} more")
    if found_not_ours:
        print(f"  {len(found_not_ours)} of those are NOT staged by the line below — check them.")
if unexpected:
    print(f"\n  UNEXPECTED — the chain does not write these. Do not commit them")
    print(f"  without knowing why they changed:")
    for p in unexpected:
        print(f"                        {p}")

if not written:
    print(f"\n  Nothing was written by this run. {SLUG} was already deduplicated")
    print(f"  and every derived figure already matched its source.")
    print(f"  Check `git log -1 -- {SLUG}/ssi-data.json` and the audit trail")
    print(f"  before concluding anything is wrong.")
    if not stage_set:
        raise SystemExit(0)
    print(f"\n  There are still {len(stage_set)} changed file(s) this country's chain")
    print(f"  owns — staged below so they are not left behind.")

data = [p for p in stage_set if p.startswith(SLUG + "/")]
shared = [p for p in stage_set if p in ("nav.js", "index.html")]
pages = len([p for p in stage_set if p.endswith(".html") and p != "index.html"])
print(f"\n      {len(data)} {SLUG} data file(s) · {len(shared)} shared · {pages} page(s)")
print(f"\n  Review, then commit. Explicit paths, not `git add -A` — the tooling")
print(f"  lives in scripts/ now, and -A would sweep a tooling edit into a data")
print(f"  commit:")
print(f"\n      git add -A -- '{SLUG}/*' {' '.join(shared)} '*/*.html'")
print(f"      git status --short | grep -v '^M \\|^D \\|^A ' | head")
print(f"\n  The second line should print nothing — anything it prints is unstaged")
print(f"  and wants explaining before the commit.")
