# `ireland` — schema parity patch (medium priority)

_Source: Stage 7e audit 2026-05-22 UTC · KB §49.11_

## Findings

`substations[0]` missing `climate_trajectory`.

## Why this matters

Same as Australia — climate-risk band on the ESG report falls back
to "—". For Ireland this matters mainly for coastal substations
where storm-surge flood risk is meaningfully elevated.

## Patch

In `scoring-ie/publish.py`, inside the per-substation dict, add:

```python
"climate_trajectory": _climate_trajectory_for(s),
```

Helper (identical to the Australia/Chile spec):

```python
def _climate_trajectory_for(s):
    flood   = s["modifiers"].get("R6c_flood", 0)
    seismic = s["modifiers"].get("R6_seismic", 0)
    if   flood >= 0.04 or seismic >= 0.05: return "deteriorating"
    elif flood >= 0.02 or seismic >= 0.03: return "stable-watchful"
    else:                                    return "stable"
```

Ireland already emits `confidence_tier` (unlike AU/CL) — only
`climate_trajectory` is missing here.

## Verification

```
python3 scoring-ie/score-country.py
gh workflow run runtime-audit.yml \
    -R ikengassiindex/ikengassiindex.github.io \
    -f countries=ireland -f always_send=true
```

Expected next-run result: ireland shows ✓ clean.
