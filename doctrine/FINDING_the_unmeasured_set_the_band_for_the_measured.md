# FINDING — in thirteen jurisdictions, the unmeasured set the band for the measured

**Date** 25 September 2026
**Occasion** Validating a refactor on Greece before rebuilding it. Greece was not rebuilt; the dry run's numbers did not look like any of the thirteen countries already done, and the reason was not the refactor.
**Measured on** the deployed tree, the thirteen jurisdictions that carry a significant empty-components population — 85,186 records.
**Status** measurement only. Nothing published was changed, and none of these thirteen has been rebuilt.

## What this is not

It is not a consequence of the component I rebuild. Every measurement below is
of the tree **as published**, and of a rebuild **simulated and discarded**. The
defect is live now.

## The mechanism, stated before the numbers

The published `classification` is a per-country percentile: `R_norm =
clip((R_median − country_P5) / (country_P95 − country_P5), 0, 1)`, banded on the
five cut points. `scripts/normalise_bands_per_country.py` computes P5 and P95
over **every record in the country that carries an `R_median`**.

78,525 records estate-wide carry an empty `components` dict and a published
`R_median` that is the flood additive term alone
(`FINDING_78525_scores_are_the_flood_term_alone.md`). They carry an `R_median`,
so they are full members of their country's percentile pool.

In thirteen jurisdictions they are most of it.

## What they do to the anchors

```
country         n      held   held%    P5 all   P5 excl   P95 all  P95 excl
austria      14,720   13,979   95.0%   0.0605    0.3322    0.2813    0.8505
poland       27,764   25,517   91.9%   0.0607    0.3769    0.5724    0.8793
slovenia      1,731    1,574   90.9%   0.0605    0.3034    0.5445    0.8943
lithuania     4,901    4,396   89.7%   0.0465    0.3196    0.5155    0.7629
czechia       8,899    7,825   87.9%   0.0768    0.4429    0.5012    0.7203
belgium       6,651    5,432   81.7%   0.1043    0.4552    0.7868    0.9533
latvia        4,646    3,427   73.8%   0.0497    0.2641    0.6324    0.8696
netherlands   5,449    3,810   69.9%   0.1614    0.4498    0.8996    0.9498
estonia       1,794    1,180   65.8%   0.0401    0.3144    0.8254    0.9005
denmark       4,822    2,389   49.5%   0.0709    0.3256    0.8587    0.9163
switzerland   1,812      865   47.7%   0.0779    0.4747    0.7784    0.8009
greece          719      163   22.7%   0.0877    0.3714    0.9167    0.9906
ireland       1,278      284   22.2%   0.1290    0.2937    0.9518    0.9566

  13 jurisdictions · 85,186 records · 70,841 held · 83.2 per cent
```

Austria's P5 is **0.0605**. Excluding the records that have no components, it is
**0.3322** — five and a half times higher. Every measured Austrian substation is
normalised against an anchor set by 13,979 records whose score is a flood term.

## What that does to the published band

Recomputing the percentile over the measured records alone, and asking how many
of them would carry a different published band:

```
austria       703 of   741   94.9%        netherlands  1,048 of 1,639   63.9%
poland      2,131 of 2,247   94.8%        estonia        525 of   614   85.5%
slovenia      149 of   157   94.9%        denmark      1,822 of 2,433   74.9%
lithuania     479 of   505   94.9%        switzerland    838 of   947   88.5%
czechia     1,020 of 1,074   95.0%        greece         477 of   556   85.8%
belgium     1,158 of 1,219   95.0%        ireland        383 of   994   38.5%
latvia      1,158 of 1,219   95.0%
```

**Roughly nineteen in twenty measured Austrian, Polish, Slovenian, Lithuanian,
Czech, Belgian and Latvian substations carry a published band determined by
records that were never measured.**

## It also reverses the rebuild's direction

Greece and Ireland were simulated twice — once with the held records inside the
percentile pool, as the deployment computes it, once with them outside:

```
greece    pool = all 719        334 worse,  33 better    ratio 10.12
greece    pool = 556 rebuilt      6 worse, 357 better    ratio  0.02

ireland   pool = all 1,278      379 worse,  95 better    ratio  3.99
ireland   pool = 994 rebuilt     52 worse, 467 better    ratio  0.11
```

The direction **inverts**. Read one way, rebuilding Greece makes 334 substations
worse. Read the other, it makes 357 better and 6 worse. The records that decide
which are the ones carrying no measurement at all.

This is why none of the thirteen has been rebuilt. It is not that the rebuild
would be wrong there; it is that its published result would be a statement about
the empty records rather than about the metrics.

## Why the thirteen rebuilt so far are not affected

Eight carry no empty-components records at all — israel, sweden, italy, germany,
france, the uk, spain, portugal. Five carry a trace: hungary 5 of 3,507,
slovakia 5 of 1,517, turkey 30 of 4,031, finland 54 of 3,939, norway 271 of
6,113. Norway's 4.4 per cent is the largest attempted and produced a band
movement of 1,310 worse against 1,080 better — a ratio of 1.21, against greece's
10.12.

The ordering is not perfectly monotonic in held share. The uk holds none and its
ratio is 1.32, above norway's. Held share is therefore not the only thing that
moves this number, and this document does not claim it is — what the greece and
ireland trials establish is the *direction reversal*, which is a controlled
comparison on one country at a time, not a correlation across countries.

## What this does not decide

It does not decide which pool is correct.

Excluding the unmeasured records from the percentile would make each measured
substation's band a statement about the measured fleet. It would also change the
published band of most substations in seven jurisdictions at a stroke, and it
would leave the excluded records to be banded by some other rule or not at all.

The literature points at a third option. Under the inclusion rule of a
JRC-audited index — at least two thirds data availability, units below it
excluded from the index entirely — a record with zero of six components does not
receive a published score, and the question of which pool it belongs to does not
arise. See `RECOMMENDATION_the_treatment_of_absent_components.md`, which
assembles that evidence and declines to declare the threshold.

Three questions now sit together and should be answered together rather than
one at a time:

1. what is published for a record with no components — the 78,525;
2. whether such records belong in their country's percentile pool — this
   document;
3. what availability threshold governs both.

Nothing here is proposed. Recorded because the thirteen are blocked on it, and
because the defect is on the site today whether or not anything is rebuilt.

## Related

- `FINDING_78525_scores_are_the_flood_term_alone.md`
- `RECOMMENDATION_the_treatment_of_absent_components.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
