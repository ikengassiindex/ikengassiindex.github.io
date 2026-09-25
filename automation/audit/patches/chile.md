# `chile` — schema parity patch (HIGH priority)

_Source: Stage 7e audit 2026-05-22 UTC · KB §49.11_

## Findings

1. `substations[0]` missing `climate_trajectory`, `confidence_tier`
2. `regions[0]` missing `region`, `bands`, `mean_R`, `median_R`,
   `pct_critical`, `pct_high` — **the regions array is structurally
   degraded**, currently emits only `count` per entry.

## Why this matters

The regions[] gap is the most concerning finding in the entire fleet.
Without `region` (the region's name as a string), Chile's
`regional.html` cannot label its rows. Without `mean_R`/`median_R`/
`bands`/`pct_critical`/`pct_high`, the regional risk distribution
widgets render as empty. This is almost certainly visible to users
right now on https://ikengassiindex.github.io/chile/regional.html

## Patch — substation block

In `scoring-cl/publish.py`, inside the per-substation dict literal,
add:

```python
"climate_trajectory": _climate_trajectory_for(s),   # see helper below
"confidence_tier":    _confidence_tier_from_ci_width(s["CI_width"]),
```

`climate_trajectory` should be a string label derived from the
substation's flood + seismic + temperature delta over the planning
horizon. Reference implementation (from `scoring-lv/publish.py`):

```python
def _climate_trajectory_for(s):
    flood   = s["modifiers"].get("R6c_flood", 0)
    seismic = s["modifiers"].get("R6_seismic", 0)
    if   flood >= 0.04 or seismic >= 0.05: return "deteriorating"
    elif flood >= 0.02 or seismic >= 0.03: return "stable-watchful"
    else:                                    return "stable"
```

`confidence_tier` is a per-substation tier derived from `CI_width`:

```python
def _confidence_tier_from_ci_width(w):
    if w < 0.10: return "high"
    if w < 0.20: return "medium"
    return "low"
```

## Patch — regions block (CRITICAL)

The regions[] generator in `scoring-cl/publish.py` is emitting only
the count. Replace the regions loop with the LV-reference shape:

```python
regions = []
for region_name, subs in group_by_region(all_substations):
    Rs = [s["R_median"] for s in subs]
    band_count = bands_count(Rs, thresholds=BAND_THRESHOLDS)
    regions.append({
        "region":         region_name,
        "count":          len(subs),
        "mean_R":         statistics.mean(Rs),
        "median_R":       statistics.median(Rs),
        "bands":          band_count,          # {"low": …, "medium": …, …}
        "pct_critical":   100.0 * band_count["critical"] / len(subs),
        "pct_high":       100.0 * band_count["high"]     / len(subs),
    })
```

`BAND_THRESHOLDS` should match Chile's calibrated tier breakpoints
(probably already defined elsewhere in `scoring-cl/`). `bands_count`
is the standard helper from `scoring-common/` if it exists, else
inline it.

## Verification

```
python3 scoring-cl/score-country.py
python3 -m json.tool chile/ssi-data.json | head -200
```

Check that `regions[0]` now has all 7 fields. Then:

```
gh workflow run runtime-audit.yml \
    -R ikengassiindex/ikengassiindex.github.io \
    -f countries=chile -f always_send=true
```

Expected next-run result: chile shows ✓ clean.
