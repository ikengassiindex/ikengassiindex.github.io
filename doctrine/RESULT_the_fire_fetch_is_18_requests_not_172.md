# RESULT — the fire fetch is 18 requests, not 172

**Measured** 21 September 2026 · `scripts/estimate_fire_fetch_cost.py --sweep`
· dataset `cems-fire-historical-v1` (EWDS) · priced server-side, nothing queued,
nothing downloaded.

## What was assumed

`PLAN_hazard_raster_acquisition.md` carried, in two places, the sentence *"one
year of one daily variable is 365 units, inside the 400 limit"*. The 400 came
from CERRA. It was carried across to a different data store on a different
dataset and never re-checked. That is the same class of error as a coefficient
stated without a source: a number that is true somewhere, asserted where it was
never tested.

## What was measured

| years | cost | limit | verdict | ratio to 1 y |
|---:|---:|---:|:--|---:|
| 1 | 366.0 | 3720.0 | OK | ×1.00 |
| 2 | 731.0 | 3720.0 | OK | ×2.00 |
| 5 | 1827.0 | 3720.0 | OK | ×4.99 |
| 10 | 3653.0 | 3720.0 | OK | ×9.98 |
| 11 | 4018.0 | 3720.0 | **OVER** | ×10.98 |
| 20 | 7305.0 | 3720.0 | **OVER** | ×19.96 |

Two things are settled by this, neither of them by argument.

**Cost is the exact day count.** 366 is leap-year 2024. 731 is 2023 + 2024.
1827 is 2020–2024 with one leap. The rule *cost = variables × days, and area
does not enter* holds here to the unit, on a store we had not previously
priced.

**The limit is 3720, not 400.** Ten years fit in one request. Eleven do not.
The boundary is measured, not inferred from the arithmetic, because the
arithmetic was what produced the 400 in the first place.

## What it changes

1940–2025 fetched as nine windows per variable:

    1940-1949  1950-1959  1960-1969  1970-1979  1980-1989
    1990-1999  2000-2009  2010-2019  2020-2025 (6 years, 2192 units)

**9 per variable, 18 in total**, against the 172 the plan specified. Queue
latency is per request and independent of payload, so request count is the only
lever on wall-clock: at ~24 h median latency and requests queued together, this
is the difference between a queue we watch and a queue we wait out.

The window edges do not need to align with the 1991–2020 standard normal. The
normal is computed from the retained series after the fetch; it is not a fetch
boundary.

## A second defect, found in the instrument itself

The first sweep returned `cost 0.0, limit 0.0` for every year count, and read as
"free". It was not free. `estimate_costs()` returns a **mapping**,
`{'id': 'size', 'cost': 366.0, 'limit': 3720.0}`, and the script read it with
`getattr(costs, "cost", 0)`, which on a mapping returns the default silently.

A cost probe whose failure mode is printing zero is worse than no cost probe,
because zero is the answer you want. Fixed by reading it as a mapping and
**raising rather than defaulting**, so a future shape change is loud:

```python
def field(costs, name):
    if isinstance(costs, dict):
        return float(costs[name])
    return float(getattr(costs, name))
```

Caught only because the one-year figure printed by the older code path (366.0,
via `print`) contradicted the sweep's 0.0 three lines below it. Two instruments
disagreeing on the same page is why both were on the page.

## Still open on this leg

- Whether the pre-1979 back-extension carries the same confidence — the CEMS
  user guide is silent, and this must be answered from ERA5's own documentation
  before that portion enters a published statistic. Unchanged by this result.
- The EWDS key in the credential store is the one pasted into a chat window on
  20 September. It is to be treated as compromised until rotated. **This probe
  ran on it**, which is a read-only pricing call and no reason to defer the
  rotation.
