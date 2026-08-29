#!/usr/bin/env python3
"""
Does a country's published band distribution match its own substations?

    python3 scripts/check_bands_match_classification.py --all
    python3 scripts/check_bands_match_classification.py us germany
    python3 scripts/check_bands_match_classification.py --all --strict

WHAT THIS CATCHES
-----------------
Two numbers describe the same thing and are produced by different code:

  * each substation's `classification` field, written by Task #461's
    per-country P5/P95 normalisation (engine.normalise_bands_per_country)
  * `fleet_summary.bands` / `band_pct` in the manifest, which the country
    page and the landing map read

engine.compute_fleet_summary rebuilds the second by calling classify_band on
R_median — the ABSOLUTE cutoffs Task #461 exists to replace. So any tool that
rewrites a country through that function silently reverts Phase 2D for the
published figure while leaving every substation's own label normalised.

On 28 August 2026 that had happened to four countries:

    country     substations             published
    us          Low 22.6%               Low  0.0%   High 65.6%
    germany     Low 23.0%               Low  0.0%   High 81.2%
    sweden      Low 24.9%               Low  0.0%   High 59.0%
    japan       Low 21.7%               Low  0.0%   High 69.0%

The map coloured each substation from `classification` and the header on the
same page quoted `band_pct`, so the two disagreed in public.

WHY NOTHING ELSE SAW IT
-----------------------
refresh_fleet_summary.py::_has_drift is the cohort's drift detector and it
checks median_R for None, n_scored against total, the presence of an Extreme
band, and whether the band counts SUM to the fleet size. This regression keeps
the sum exactly right — it moves substations between bands. The one check that
would have caught it is the one nobody had written: compare the counts against
the labels they are meant to be counting.

check_page_data_agreement.py does not close it either. It verifies the page
against the manifest. Both were wrong together, so it passed.

WHAT "MATCH" MEANS HERE
-----------------------
An exact tally. `fleet_summary.bands[b]` must equal the number of substations
whose `classification` is b, for every band. Not a tolerance — these are two
counts of one set, and any difference is a defect rather than rounding.

A country whose substations were never normalised is not a failure: its
`classification` is the absolute band, the tally still matches, and the check
passes. This asks only that the summary describe the data.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path.cwd()
if not (REPO / "intelligence" / "countries.json").exists():
    sys.exit("ABORT: run from the ikengassiindex.github.io repo root.")

BANDS = ("Low", "Medium", "High", "Critical", "Extreme", "Unclassified")


def load(slug):
    """Manifest and substations, shard-aware (Convention #79).

    Task #520 is the registered defect class for reading data['substations']
    on a sharded manifest and getting an empty list, so the shard list is
    consulted first and a sharded country never falls through to the flat key.
    """
    root = REPO / slug
    man = json.loads((root / "ssi-data.json").read_text())
    shards = man.get("substations_shards")
    if shards:
        subs = []
        for e in shards:
            p = root / pathlib.Path(e["path"]).name
            if not p.exists():
                return man, None, f"shard missing: {e['path']}"
            d = json.loads(p.read_text())
            subs.extend(d if isinstance(d, list) else (d.get("substations") or []))
        return man, subs, None
    subs = man.get("substations")
    if subs is None:
        return man, None, "no substations and no shard list"
    return man, subs, None


def tally(subs):
    counts = {b: 0 for b in BANDS}
    for s in subs:
        b = s.get("classification")
        counts[b if b in counts else "Unclassified"] += 1
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on any mismatch (for CI and the dedupe wrapper)")
    a = ap.parse_args()

    slugs = a.countries
    if a.all or not slugs:
        slugs = sorted(d.name for d in REPO.iterdir()
                       if d.is_dir() and (d / "ssi-data.json").exists())

    bad, skipped, regional = [], [], []
    for slug in slugs:
        man, subs, err = load(slug)
        if err:
            skipped.append((slug, err))
            continue
        fs = man.get("fleet_summary") or {}
        published = fs.get("bands") or {}
        actual = tally(subs)

        diff = {b: (published.get(b, 0), actual[b])
                for b in BANDS if published.get(b, 0) != actual[b]}
        if diff:
            bad.append((slug, len(subs), diff, fs.get("_bands_source")))

        # The regional layer, which this check used to ignore entirely. A
        # country could pass on its fleet total while every one of its regions
        # disagreed, and france did exactly that: 102 of 102 regions wrong,
        # 89,668 substations in the wrong regional band, fleet summary green.
        by_region = {}
        for x in subs:
            k = x.get("region") or "Unclassified"
            g = by_region.setdefault(k, {b: 0 for b in BANDS})
            b = x.get("classification")
            g[b if b in g else "Unclassified"] += 1
        off_regions, off_records = 0, 0
        for entry in (man.get("regions") or []):
            # Named `act`, not `a`: `a` is the argparse namespace in this
            # scope, and shadowing it makes --strict raise AttributeError
            # instead of returning an exit code.
            act = by_region.get(entry.get("region"))
            if act is None:
                continue
            pb = entry.get("bands") or {}
            d = sum(abs(pb.get(b, 0) - act[b]) for b in BANDS) // 2
            if d:
                off_regions += 1
                off_records += d
        if off_regions:
            regional.append((slug, off_regions, len(man.get("regions") or []),
                             off_records))

    n = len(slugs) - len(skipped)
    if not bad:
        print(f"   OK: published bands match the classification field "
              f"({n} countries)")
    else:
        for slug, total, diff, src in bad:
            print(f"   {slug}: fleet_summary.bands disagrees with "
                  f"{total:,} substations")
            for b, (pub, act) in diff.items():
                dp = 100 * pub / total if total else 0
                da = 100 * act / total if total else 0
                print(f"       {b:<13} published {pub:>8,} ({dp:4.1f}%)   "
                      f"substations {act:>8,} ({da:4.1f}%)")
            if src:
                # A provenance stamp that survived a rebuild which invalidated
                # it is worse than no stamp: it asserts the normalisation is
                # in force over counts that are not normalised.
                print(f"       _bands_source claims: {src}")
        print(f"\n   {len(bad)} of {n} countries publish a distribution that "
              f"their own substations contradict.")
        print(f"   Repair: python3 scripts/refresh_fleet_summary.py "
              f"{' '.join(s for s, *_ in bad)}")

    if regional:
        print()
        for slug, n, total, recs in sorted(regional, key=lambda r: -r[3]):
            print(f"   {slug}: {n} of {total} regions publish band counts their "
                  f"own substations contradict ({recs:,} records)")
        print(f"\n   {len(regional)} country(ies) with a regional-layer mismatch. "
              f"Repair: python3 scripts/ssi_repair_fleet_bands.py "
              f"{' '.join(s for s, *_ in regional)}")

    for slug, err in skipped:
        print(f"   SKIP {slug}: {err}")

    if (bad or regional) and a.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
