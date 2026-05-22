# `us` — schema parity patch (low priority)

_Source: Stage 7e audit 2026-05-22 UTC · KB §49.11_

## Findings

`substations[0]` missing `internal_id`.

## Why this matters

`internal_id` is the audit-trail handle distinct from `substation_id`
(the public-facing ID). LV/LT/EE/CZ/LU/BE/NL all emit both. The US
dataset uses `substation_id` alone — likely because the original
US-specific scoring pipeline pre-dates the `internal_id` convention.

In practice the dashboard JS falls back to `substation_id` everywhere
it would have used `internal_id`, so this finding is largely cosmetic.
But it does mean: any future tooling that joins audit logs against
`internal_id` will silently miss the US fleet.

## Patch

In `scoring-us/publish.py`, inside the per-substation dict, add:

```python
"internal_id": s.get("substation_id"),   # US: identity mapping
```

The values are identical (US doesn't have a separate audit-trail ID),
but emitting the key ensures consistency with the rest of the fleet.

Alternative: if scoring-us has its own auto-incrementing internal
counter, use that instead:

```python
"internal_id": f"US_{idx:06d}",
```

where `idx` is the row position in the substations list.

## Verification

```
python3 scoring-us/score-country.py
gh workflow run runtime-audit.yml \
    -R ikengassiindex/ikengassiindex.github.io \
    -f countries=us -f always_send=true
```

Expected next-run result: us shows ✓ clean.

## If `scoring-us` doesn't exist as a separate repo

The US dataset may have been built by an earlier monolithic pipeline
that no longer runs. In that case, the cheapest fix is a one-time
edit to `us/ssi-data.json` directly via a small migration script:

```python
import json
d = json.load(open("us/ssi-data.json"))
subs = d["substations"] if isinstance(d["substations"], list) else list(d["substations"].values())
for s in subs:
    if "internal_id" not in s:
        s["internal_id"] = s["substation_id"]
json.dump(d, open("us/ssi-data.json", "w"), indent=2, ensure_ascii=False)
```

This is a one-shot JSON migration, NOT a recurring hotpatch — fine
to do once when no scoring repo exists. Document under "legacy
migration" rather than "publish.py patch".
