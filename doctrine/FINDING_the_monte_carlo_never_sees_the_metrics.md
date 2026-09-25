# FINDING — the Monte Carlo never sees the metrics

**Date** 25 September 2026
**Occasion** Giving five Hungarian records their first component I published them as *high confidence* on one component of six. Establishing why exposed something larger.
**Measured on** the deployed engine at the pinned commit, and the published tree, 622,104 records.
**Status** measurement only. Nothing published was changed; the Hungarian write was reverted.

## The test

One published Israeli record. Its six real metrics — I1 to I6, present and
measured — shifted by +0.5. Components untouched. Rescored:

```
                    before        after
R_median            0.4544        0.4544     SAME
R_P5                0.3971        0.3971     SAME
R_P95               0.5133        0.5133     SAME
CI_width            0.1162        0.1162     SAME
confidence_tier     medium        medium     SAME
R_base_median       0.2992        0.2992     SAME
```

Nothing moved. The engine does not read the record's metrics when it scores it.

## Why

`engine.py:902`, inside `score_substation`:

```python
mc = monte_carlo(components, modifiers, iterations=10_000)
```

`metric_values` is not passed. `monte_carlo` therefore falls through to
`_derive_metric_values_from_components`, whose own docstring states what it
does:

> "For each metric m, the value is the score of its parent component. This
> approximation matches the pre-PR-2 component-level engine; once L2 enrichment
> is updated to pass raw metric values, this fallback can be retired."

The fallback was never retired, and `score_substation` — the canonical scoring
entry point — has no code path that passes raw metric values at all.

## What that means for every published interval

The 10,000-iteration Monte Carlo perturbs a vector in which **every metric is
its parent component's value**. So `R_P5`, `R_P95`, `CI_width` and
`confidence_tier` are functions of the six component values and of nothing else.

For 543,546 records, five of those six components are
`vary(0.35, name + '_' + K, 0.30)` — a hash of the substation's own name
(`FINDING_what_the_components_fill_costs.md`,
`FINDING_the_name_hash_reaches_past_components.md`).

**So the published confidence interval of 543,546 substations is, in five of its
six inputs, a function of the asset's name.** 497,631 of them are published as
*medium* confidence on that basis.

And the six metrics that ARE measured across ~620,000 records — I1, I2, I3, I4,
I5, I6, the work of the last month — reach the score through `components.I`
only, and reach the uncertainty estimate not at all.

## The confidence tier is inverted

```
components    records    median CI_width    confidence_tier
     0         78,520        0.0000         None
     1              5        0.0321         high
     6        543,546        0.1274         medium 91.6% · high 7.7% · low 0.7%
```

`classify_confidence` returns "high" for `ci <= 0.10`. A record with one
component has almost nothing to perturb, so its interval is narrow and it is
published as more certain than a record with six. **Confidence rises as
measurement falls.**

This is the second time this estate has met that inversion. The function's own
docstring records the first:

> "about 78,500 substations were published as high-confidence on the strength of
> a simulation that never happened"

The guard added then was `ci <= 1e-9 -> None`, which catches a degenerate zero
and not a thin interval. The docstring also asserts the two populations cannot
overlap, "the narrowest real 10,000-iteration interval is 0.042". The five
Hungarian records produced 0.0321 from a genuine 10,000-iteration run. That
stated separation no longer holds.

## Why the obvious fix cannot be applied yet

Pass `metric_values` into `monte_carlo` and the engine would receive real values
for I1–I6 and, through `metric_values.get(m, 0.0)`, **zero** for the other
fifteen — because C1–C4, V1, E1, E2, S1–S3 and T1 sit on no record in the estate
(`FINDING_the_index_declares_1097_sources_and_fetches_231.md`).

A vector of six real metrics and fifteen zeros is worse than the present
fallback, not better. The Monte Carlo cannot be corrected before the metric
layer exists. It joins the list blocked on 866 declared sources with no
acquisition route.

## What can be done now

`confidence_tier` should be `None` for any record that does not carry all six
components. The tier is derived from interval width; on a partial composite that
width measures how few components are present, not how certain the estimate is.
`classify_confidence` already returns `None` where there is no basis, and this
extends the same rule from *zero-width* to *incomplete*. It is Convention #56:
no field rather than a default, visibly honest rather than silently wrong.

That is a narrow change and it is not the fix. The fix is the metric layer.

Nothing here is proposed beyond that. Recorded because 497,631 substations carry
a published confidence tier that is a property of their names.

## Related

- `FINDING_the_name_hash_reaches_past_components.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_empty_component_records_are_the_clean_ones.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
