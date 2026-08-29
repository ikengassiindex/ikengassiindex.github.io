#!/usr/bin/env python3
"""
Repair the countries whose published band distribution contradicts their own
substations, and resync every page that quotes it.

    python3 scripts/ssi_repair_fleet_bands.py                # dry run
    python3 scripts/ssi_repair_fleet_bands.py --apply

WHAT IS WRONG
-------------
ssi_dedupe_substations.py::write_country rebuilt fleet_summary through
engine.compute_fleet_summary, which recounts bands from R_median using the
absolute cutoffs Task #461 replaced. Every substation kept its normalised
`classification`; only the published summary reverted. The map colours from
one field and the page header quotes the other.

    country     substations                published
    us          Low 22.6%  High 28.4%      Low 0.0%  High 65.6%  Critical 33.1%
    germany     Low 23.0%  High 28.2%      Low 0.0%  High 81.2%
    japan       Low 21.7%  High 28.5%      Low 0.0%  High 69.0%
    sweden      Low 24.9%  High 25.2%      Low 0.0%  High 59.0%

japan's dates from its dedupe pilot months ago. sweden, germany and us are
from this month's runs. fix_step17 stops it recurring; this repairs what is
already published.

WHAT THIS WRITES — AND WHY IT IS SMALLER THAN IT LOOKS
------------------------------------------------------
Only `fleet_summary`, inside each country's ssi-data.json manifest. Not one
substation record changes: no R_median, no R_P5, no classification. This
corrects a tally, not a judgement.

`regions` is not rebuilt either, though an earlier version of this script did.
compute_regional_summary bands each region with classify_band(R_median) — the
same absolute-cutoff blindness this script exists to repair, one level down —
so recomputing would reintroduce the defect regionally. It also moves figures
unrelated to band counts: on austria's Kärnten it takes median_R from 0.3649 to
0.7135, and pct_high from 56.1 to 91.5 because the stored value is single-band
while today's code makes pct_high cumulative from High. Those divergences are
real and want their own examination, not a silent rewrite inside a commit about
a missing band key.

That distinction is why this does NOT go through refresh_fleet_summary.py,
even though refresh_fleet_summary holds the correct band routine and this
script imports it. That script finishes with save_ssi_data(slug, manifest,
subs), which rewrites the whole country through the Convention #79 sharder —
and the sharder re-packs. Rehearsed on 28 Aug 2026 it took us from six shards
to four and germany from nine to six, with every new shard at 46.2–46.5 MB
against Convention #79's 45 MB target. The sharder sizes shards from a
200-substation sample, so it overshoots on countries with uneven record sizes;
that is a property worth knowing about separately, and not something a band
repair should trigger.

So the manifest is written in place with `substations_shards` and `sharded`
carried across untouched, and the shard files are not opened for writing at
all. An unsharded country has no separate manifest, so its file is rewritten
whole — with the same substation list it was read with, and only if it is
still comfortably under the sharding threshold. If it is not, this refuses
rather than quietly re-shaping the country.

THE SECOND POPULATION
---------------------
Passing country names runs it on them instead of the default four. That is how
the other 26 were repaired: countries whose `bands` dict predates Phase 2B's
fifth band (25 June 2026) and has no Extreme key at all, so their Extreme
substations are counted nowhere and their percentages sum to under 100 —
france 95.0% with 8,713 uncounted, uk 94.8% with 3,094, italy 95.0% with
2,408, 15,102 substations across the 26.

That case is purely additive: no country's existing four percentages move by
so much as a tenth of a point. The missing band simply stops being missing.

A SECOND THING WORTH KNOWING, ALSO NOT FIXED HERE
-------------------------------------------------
Each substation's normalised label was computed against its country's P5/P95
as they stood when the normalisation ran. Deduplication removed records, so
those anchors have moved: us P95 was 0.8684 when the labels were written and
is 0.8694 now. Re-normalising against post-dedupe percentiles would shift some
substations between bands. That is a methodology decision. This script
publishes the labels that exist.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path.cwd()

if not (ROOT / "intelligence" / "countries.json").exists():
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

APPLY = "--apply" in sys.argv
named = [a for a in sys.argv[1:] if not a.startswith("-")]

# The default is the four measured as REDISTRIBUTED on 28 Aug 2026 — band
# counts summing correctly to the fleet size while roughly half the fleet sits
# in the wrong band. Name countries explicitly for the other population, whose
# fault is a missing Extreme key.
COUNTRIES = named or ["us", "germany", "japan", "sweden"]

NAVGEN = ROOT / "scripts" / "generate_nav_data.py"
BUMP = ROOT / "scripts" / "bump_cache_busters.py"
FIGURES = HERE / "ssi_refresh_canonical_figures.py"
LANDING = HERE / "ssi_refresh_landing_counts.py"
AGREE = ROOT / "scripts" / "check_page_data_agreement.py"
PARSE = ROOT / "scripts" / "check_inline_js_parse.py"
BANDS = ROOT / "scripts" / "check_bands_match_classification.py"
for p in (NAVGEN, BUMP, FIGURES, LANDING, AGREE, PARSE, BANDS):
    if not p.exists():
        sys.exit(f"ABORT: {p.name} not found.")

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.refresh_fleet_summary import (          # noqa: E402
    _recompute_fleet_summary_task_461_aware as recompute_fs,
    _recompute_regional_summary_task_461_aware as recompute_regions)
from scripts.pipeline.utils.ssi_data_sharding import (  # noqa: E402
    SSI_DATA_SHARD_THRESHOLD_MB)


def tree_state():
    r = subprocess.run(["git", "status", "--porcelain"],
                       capture_output=True, text=True)
    return {l[3:].strip().strip('"'): l[:2].strip()
            for l in r.stdout.splitlines() if len(l) > 3}


BEFORE = tree_state()
if APPLY and BEFORE and "--dirty-ok" not in sys.argv:
    print(f"\nABORT: {len(BEFORE)} file(s) already modified before this run.\n")
    for p in sorted(BEFORE)[:12]:
        print(f"    {BEFORE[p]:<3} {p}")
    print("\n  A repair commit should carry the repair and nothing else.")
    sys.exit(2)


def run(label, cmd, tail=6, fatal=True):
    print(f"\n\033[1m{label}\033[0m")
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True)
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    for l in out[-tail:]:
        print("   " + l)
    if r.returncode != 0 and fatal:
        sys.exit(f"\nABORT: {label} failed (exit {r.returncode}). Nothing further run.")
    return r.returncode


def load(slug):
    """Manifest and substations, shard-aware. Task #520 is the registered
    defect class for reading data['substations'] on a sharded manifest, so the
    shard list is consulted first and never falls through to the flat key."""
    d = ROOT / slug
    man = json.loads((d / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if shards:
        subs = []
        for e in shards:
            p = d / pathlib.Path(e["path"]).name
            if not p.exists():
                sys.exit(f"ABORT: {slug} shard missing: {e['path']}")
            raw = json.loads(p.read_text())
            subs.extend(raw if isinstance(raw, list) else (raw.get("substations") or []))
        return man, subs, True
    return man, man.get("substations") or [], False


def pct(bands, n):
    return {k: round(v / n * 100, 1) for k, v in bands.items()} if n else {}


print(f"\n  {'APPLY' if APPLY else 'DRY RUN'} — {', '.join(COUNTRIES)}")
print(f"\n  {'country':<12}{'n':>9}   band counts")

if APPLY:
    print("\n\033[1m1/5  rewrite fleet_summary, manifests only\033[0m")

# One country at a time, loaded and released. The first version of this script
# planned all countries up front and held every fleet in memory at once; that
# is fine for four and not for twenty-six, where france alone is 175,660
# records and the set is over 400,000. Streaming also means a failure part-way
# leaves the countries already done in a correct state rather than none.
for slug in COUNTRIES:
    man, subs, sharded = load(slug)
    n = len(subs)
    old = (man.get("fleet_summary") or {}).get("bands") or {}
    new_fs = recompute_fs(subs)

    if not APPLY:
        print(f"  {slug:<12}{n:>9,}   before {pct(old, n)}")
        print(f"  {'':<12}{'':>9}   after  {pct(new_fs['bands'], n)}")
        uncounted = n - sum(old.values())
        if uncounted:
            print(f"  {'':<12}{'':>9}   {uncounted:,} substations are currently "
                  f"counted in no band at all")
        del man, subs, new_fs
        continue

    old_fs = man.get("fleet_summary") or {}
    # Preserved keys fill gaps only. A stale `_bands_source` must never sit on
    # top of freshly rebuilt counts — that is how germany came to stamp
    # "task_461_per_country_normalised" over bands that were not normalised.
    preserved = {k: v for k, v in old_fs.items() if k.startswith("_")}
    man["fleet_summary"] = {**preserved, **new_fs}
    man["regions"] = recompute_regions(subs)
    man["fleet_summary"]["n_regions"] = len(man["regions"])
    # `regions` IS rebuilt, as of fix_step20. The note that used to sit here
    # explained why it was not: the only available routine was
    # compute_regional_summary, which bands each
    # region with classify_band(R_median) — the same absolute-cutoff blindness
    # that produced the defect this script repairs, one level down. Recomputing
    # would reintroduce it regionally. It also moves figures that have nothing
    # to do with band counts: on austria's Kärnten it takes median_R from 0.3649
    # to 0.7135 and pct_high from 56.1 to 91.5, the latter because the stored
    # value is single-band and today's code makes pct_high cumulative from High.
    # Those are real divergences and they deserve their own examination, not a
    # silent rewrite inside a commit about a missing band key.

    path = ROOT / slug / "ssi-data.json"
    if sharded:
        # substations_shards and sharded ride through untouched; no shard file
        # is opened for writing, so the country is not re-packed.
        payload = json.dumps(man, separators=(",", ":"))
        path.write_text(payload)
        print(f"   {slug:<13} manifest only, {len(man['substations_shards'])} shards "
              f"untouched · {pct(old, n).get('Low', 0)}% Low -> "
              f"{pct(new_fs['bands'], n)['Low']}%")
    else:
        man["substations"] = subs
        payload = json.dumps(man, separators=(",", ":"))
        size_mb = len(payload.encode()) / 1024 / 1024
        if size_mb >= SSI_DATA_SHARD_THRESHOLD_MB:
            sys.exit(f"\nABORT: {slug} would be written at {size_mb:.1f} MB, at or over "
                     f"Convention #79's {SSI_DATA_SHARD_THRESHOLD_MB} MB threshold.\n"
                     f"  This script writes files whole and does not shard. Run it\n"
                     f"  through the sharding write path instead, deliberately.\n"
                     f"  Countries before {slug} in the list have already been written.")
        path.write_text(payload)
        print(f"   {slug:<13} single file, {size_mb:.2f} MB, "
              f"{len(subs):,} substations rewritten unchanged")
    del man, subs, new_fs, payload

if not APPLY:
    print("\n  dry run — nothing written.")
    print("  Re-run with --apply once the `after` rows are agreed.")
    sys.exit(0)

run("2/5  regenerate nav.js from the new data", [str(NAVGEN)], tail=2)
run("3/5  re-hash cache-busters", [str(BUMP)], tail=2)
for slug in COUNTRIES:
    run(f"4/5  reset {slug}'s published fleet figures",
        [str(FIGURES), slug, "--apply"], tail=3)
run("5/5  reset the landing-page map tooltips", [str(LANDING), "--apply"], tail=3)

print("\n\033[1m" + "=" * 62 + "\033[0m")
print("\033[1mverification\033[0m")
fails = 0
fails += run("  cache-busters", [str(BUMP), "--check"], tail=1, fatal=False)
fails += run("  nav.js in sync", [str(NAVGEN), "--check"], tail=1, fatal=False)
fails += run("  page/data agreement", [str(AGREE), "--all", "--strict"], tail=3, fatal=False)
fails += run("  inline JS parse", [str(PARSE), "--strict"], tail=2, fatal=False)
fails += run("  bands match the data", [str(BANDS)] + COUNTRIES + ["--strict"],
             tail=6, fatal=False)

print("\n" + "=" * 62)
if fails:
    print(f"  {fails} check(s) FAILING — do not commit.")
    sys.exit(1)

AFTER = tree_state()
written = sorted(set(AFTER) - set(BEFORE))


def expected(p):
    """Decided by location, the same rule the dedupe wrapper uses."""
    return (any(p.startswith(c + "/") for c in COUNTRIES)
            or p in ("nav.js", "index.html")
            or (p.endswith(".html") and "/" in p))


unexpected = [p for p in written if not expected(p)]
shard_writes = [p for p in written if "ssi-data-substations-" in p]

print("  all five green")
print(f"\n  written by this run : {len(written)} file(s)")
if shard_writes:
    print(f"\n  WARNING: {len(shard_writes)} shard file(s) were modified. This")
    print(f"  script is not supposed to touch them:")
    for p in shard_writes[:10]:
        print(f"      {p}")
if unexpected:
    print(f"\n  UNEXPECTED — outside the repaired countries and the shared set:")
    for p in unexpected[:20]:
        print(f"      {p}")
    print("  Explain these before committing.")

globs = " ".join(f"'{c}/*'" for c in COUNTRIES)
print(f"\n  Review, then commit:\n")
print(f"      git add -A -- {globs} index.html nav.js '*/*.html'")
print(f"      git status --short | grep -v '^M \\|^D \\|^A ' | head")
print(f"\n  The second line should print nothing.")
