#!/usr/bin/env python3
"""
relabel_unresolved_rail_traction.py — make a default look like a default
========================================================================

20,492 US substations — 20.9% of the US fleet, 2.8% of the whole cohort —
carry:

    operator          "Amtrak Northeast Corridor 12.5"
    voltage_kv        12.47      (every one, no variation)
    resolution_layer  rail_traction_25kv_ac_amtrak_voltage_inferred

They span longitude -165.4 to +144.9 and latitude 13.5 to 70.3 — Alaska to
Guam. Only 3.8% fall inside a generous Northeast Corridor bounding box. The
largest concentrations are Illinois (2,129), California (1,517), Texas
(1,467), Missouri (1,363) and Oklahoma (998), none of which has Amtrak
electrification. The layer name says 25 kV AC; the value assigned is 12.47 kV,
the standard US distribution voltage. The label contradicts the data it wrote.

**Why this is worth a script rather than a shrug.** Germany has a larger
default block — 120,210 substations, 71% of its fleet — and it is *fine*,
because its operator string reads `E.ON group DSO (fallback default)` in plain
text. Anyone reading a record knows what they have. That is Convention #56
working as designed. The US block asserts a specific named operator and a
specific voltage, both of which read as observed and are wrong for 96% of the
rows. It is the same degradation wearing a disguise.

So this tool does not try to work out who these substations belong to. It
makes the estate say what it actually knows:

  * `operator_canonical` -> "Unresolved rail traction (fallback default)"
  * `_owner_provenance`  -> names the rule that assigned it and why it is void
  * `_voltage_inferred`  -> True, with `_voltage_inference_basis` recording
    that 12.47 kV was a connector default, not a reading
  * `_rail_traction_review` -> "inside_northeast_corridor" for the 778 that
    could genuinely be Amtrak, "outside_electrified_network" for the rest

`voltage_kv` itself is left alone. Setting 20,492 voltages to None would be
the strictly honest move, but it silently moves every fleet-summary and band
statistic in the country, and that is a scoring change dressed as a labelling
fix. The inference is now declared where a reader will see it; correcting the
value belongs to whoever resolves these properly.

Nothing here touches scoring, geometry, or any rendered page.

Usage:
    python3 scripts/relabel_unresolved_rail_traction.py --dry-run
    python3 scripts/relabel_unresolved_rail_traction.py --write
"""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts._ssi_data_shard_reader import load_ssi_data, save_ssi_data  # noqa: E402

LAYER = "rail_traction_25kv_ac_amtrak_voltage_inferred"
FALSE_OPERATOR = "Amtrak Northeast Corridor 12.5"
NEW_OPERATOR = "Unresolved rail traction (fallback default)"
MARKER = "_rail_traction_review"

# Amtrak's electrified network is the Northeast Corridor plus the Keystone
# line. This box is deliberately generous — Washington DC to Boston, inland to
# Harrisburg — so that anything it excludes is excluded comfortably.
NEC = {"lon_min": -77.5, "lon_max": -71.0, "lat_min": 38.8, "lat_max": 42.4}


def inside_nec(sub) -> bool:
    try:
        lon, lat = float(sub["lon"]), float(sub["lat"])
    except (KeyError, TypeError, ValueError):
        return False
    return (NEC["lon_min"] <= lon <= NEC["lon_max"]
            and NEC["lat_min"] <= lat <= NEC["lat_max"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="us")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.write or a.dry_run):
        print("Specify --dry-run or --write")
        return 2

    data, subs, sharded = load_ssi_data(a.country)
    hits, already, inside, outside = 0, 0, 0, 0
    states = collections.Counter()

    for s in subs:
        if s.get("resolution_layer") != LAYER:
            continue
        hits += 1
        if s.get(MARKER):
            already += 1
            continue
        in_nec = inside_nec(s)
        inside += in_nec
        outside += not in_nec
        states[s.get("region") or s.get("province")] += 1

        if not a.dry_run:
            s["operator_canonical"] = NEW_OPERATOR
            if s.get("owner") == FALSE_OPERATOR:
                s["owner"] = NEW_OPERATOR
            s["_owner_provenance"] = (
                "connector fallback rule 'rail_traction_25kv_ac_amtrak'; "
                "prior value asserted Amtrak Northeast Corridor for substations "
                "outside the electrified network — void, not an observation")
            s["_voltage_inferred"] = True
            s["_voltage_inference_basis"] = (
                "connector default 12.47 kV applied by the rail-traction rule; "
                "the rule is named for 25 kV AC, so the value is not even the "
                "default the rule describes")
            s[MARKER] = ("inside_northeast_corridor" if in_nec
                         else "outside_electrified_network")

    print(f"country            : {a.country}")
    print(f"substations         : {len(subs):,}")
    print(f"rail-traction layer : {hits:,} ({100 * hits / max(len(subs), 1):.1f}%)")
    print(f"  already relabelled: {already:,}")
    print(f"  inside NEC box    : {inside:,}  (kept, flagged for review)")
    print(f"  outside           : {outside:,}")
    print(f"  top regions       : {states.most_common(6)}")

    if a.dry_run:
        print("\nDRY RUN — nothing written. Re-run with --write to apply.")
        return 0
    if not (inside or outside):
        print("\nnothing to do")
        return 0
    save_ssi_data(a.country, data, subs, sharded)
    print(f"\nwrote {a.country}/ssi-data.json ({'sharded' if sharded else 'single file'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
