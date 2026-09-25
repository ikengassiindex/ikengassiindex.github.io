# `australia` — schema parity patch (medium priority)

_Source: Stage 7e audit 2026-05-22 UTC · KB §49.11_

## Findings

`substations[0]` missing `climate_trajectory`, `confidence_tier`.

## Why this matters

`climate_trajectory` is read by the ESG report's climate-risk band
("deteriorating" / "stable-watchful" / "stable"). `confidence_tier`
drives the per-substation confidence pill in map popovers. Both
fields fall back to "—" in the current Australia pages.

## Patch

In `scoring-au/publish.py`, inside the per-substation dict, add:

```python
"climate_trajectory": _climate_trajectory_for(s),
"confidence_tier":    _confidence_tier_from_ci_width(s["CI_width"]),
```

Helper implementations (same as Chile's spec — these belong in
`scoring-common/` if a shared module exists):

```python
def _climate_trajectory_for(s):
    flood   = s["modifiers"].get("R6c_flood", 0)
    seismic = s["modifiers"].get("R6_seismic", 0)
    if   flood >= 0.04 or seismic >= 0.05: return "deteriorating"
    elif flood >= 0.02 or seismic >= 0.03: return "stable-watchful"
    else:                                    return "stable"

def _confidence_tier_from_ci_width(w):
    if w < 0.10: return "high"
    if w < 0.20: return "medium"
    return "low"
```

For Australia specifically, `R6c_flood` is dominated by cyclonic
storm-surge zones along the QLD/NSW coast — the trajectory tags
will skew toward "stable-watchful" for those substations and
"stable" elsewhere. That's the desired behaviour.

## Verification

```
python3 scoring-au/score-country.py
python3 -c "
import json
d = json.load(open('australia/ssi-data.json'))
subs = d['substations']
first = subs[0] if isinstance(subs, list) else next(iter(subs.values()))
assert 'climate_trajectory' in first, 'still missing climate_trajectory'
assert 'confidence_tier'    in first, 'still missing confidence_tier'
print(f'climate_trajectory: {first[\"climate_trajectory\"]}')
print(f'confidence_tier:    {first[\"confidence_tier\"]}')
"
gh workflow run runtime-audit.yml \
    -R ikengassiindex/ikengassiindex.github.io \
    -f countries=australia -f always_send=true
```

Expected next-run result: australia shows ✓ clean.
