# FINDING — 90,476 records claim a NIVA provenance the NIVA raster cannot have produced

**Date:** 2026-09-21
**Status:** established by exhaustive measurement, not by inference
**Found:** while verifying the Task #450/#451 cohort repair, not while looking for it
**Severity:** Constitution §7.2 (no measured value typed) and §7.5 (no silent absence)

---

> ### CORRECTION — same day, before this document landed
>
> The first census behind this finding was **wrong, and wrong in the way this
> document condemns.** It read each country's `ssi-data.json` for a `substations`
> key. Six countries — france, germany, us, uk, italy, poland — are sharded:
> their index file carries `sharded: true` and `substations_shards`, and no
> `substations` key at all. The script read them as empty and **reported a total
> of 142,165 substations as though that were the estate.** The estate is 622,104.
>
> That is a silent absence produced by the measuring instrument — §7.5 — committed
> while documenting a §7.5 breach. It was caught because the `--force-rewrite`
> dry run reported france at 168,894 subs, a number the census said did not exist.
>
> The original figures are struck below and the corrected ones stand beside them.
> The finding's *mechanism* is unchanged and was never in doubt; only its **size**
> was understated, by 39%.


---

## 1. What was being done

The authorised `migration_score_semantic_normalise.py --cohort` repair ran and did
exactly what it promised: 531 Greek and 2,190 Mexican records rescaled out of
`[-4.5, 2.5]` and `[-5.0, 8.0]` into `[0, 1]`. A verification sweep across all 33
cohort countries confirmed 141,932 values, every one inside `[0, 1]`.

The same sweep showed something that was not being looked for: **`0.5000` is the
modal value in 14 countries, at concentrations no migration statistic produces.**
Portugal 13,517 of 13,563 (99.7%). Spain 12,008 of 12,437 (96.6%). Sweden 3,757 of
3,772 (99.6%). Slovenia 1,728 of 1,731.

## 2. The first hypothesis, and why it was wrong

`migration_score` is written by `map_raw_to_score`:

```
score = 0.5 + 0.5 * tanh(raw / K),  K = 200.0
```

`score == 0.5` if and only if `raw == 0`. The obvious hypothesis was that the NIVA
raster encodes nodata as `0`, that `sample_score`'s NoData branch was failing, and
that ocean and unpopulated cells were therefore being scored as "neutral migration".

**That hypothesis is false.** The raster was opened and measured:

| | |
|---|---|
| file | `docs/audits/raster_netMgr_2000_2019_20yrSum.tif` |
| MD5 | `97793810040b30dd4f4ffc889c52cef7` — **matches the pinned `_NIVA_FILE_MD5`** |
| shape / CRS | 2160 × 4320, EPSG:4326 |
| declared nodata | `nan` |
| NaN pixels | 7,408,993 of 9,331,200 (79.4%) |
| finite pixels | 1,922,207 |
| **pixels equal to exactly 0.0** | **0** |
| smallest \|raw\| present | 0.000154 |

There is no zero in the raster. The nodata is NaN, and NaN is caught correctly by
`sample_score` step 5 (`math.isfinite`), which returns `None`.

## 3. The finding, established exhaustively

All 1,922,207 finite pixels were run through the production formula:

```
pixels yielding EXACTLY 0.5        : 0
pixels within 1e-9 of 0.5          : 0
raw needed for score == 0.5        : |raw| < 2.2e-14   (smallest present: 1.54e-4)
```

**The NIVA raster cannot produce 0.5. Not for one substation, not for any.**

Yet the published cohort contains:

Census over the **full estate of 622,104 substations**, following shards
(struck figures are the withdrawn 142,165-substation census):

| class | records | share | ~~withdrawn~~ |
|---|---:|---:|---:|
| a value NIVA could actually produce | 526,887 | 84.7% | ~~73,335~~ |
| **`0.5` carrying `_migration_score_source: NIVA_2023_20YR_SUM_v4_2_task_452`** | **90,476** | **14.5%** | ~~64,967~~ |
| `0.5` carrying no marker at all | 3,775 | 0.6% | ~~3,630~~ |
| explicit `null` — Convention #56, honest | 964 | 0.2% | ~~231~~ |
| no `socio_economic` block | 2 | 0.0% | 2 |

By country, the false-provenance records:

| | | | |
|---|---:|---|---:|
| poland | 25,509 | denmark | 2,364 |
| portugal | 13,517 | slovenia | 1,728 |
| spain | 12,008 | slovakia | 1,512 |
| czechia | 7,825 | estonia | 1,178 |
| belgium | 5,428 | sweden | 1,177 |
| australia | 4,569 | switzerland | 1,064 |
| lithuania | 4,396 | luxembourg | 634 |
| netherlands | 3,807 | ireland | 282 |
| latvia | 3,425 | finland | 53 |

**Poland is the largest single block and the first census did not see it at all.**
france, germany, us, uk and italy — the other sharded countries — are clean.

The 90,476 are the finding. They hold the neutral default hard-coded in
`scripts/pipeline/ingestion/socioeconomic.py` (`'migration_score': 0.5,  # Neutral
default`, written at 22 separate country blocks) while wearing a provenance marker
that asserts they were sampled from NIVA. **The marker is falsifiable and it is
false.** The value was typed, not measured — §7.2 — and the absence it conceals is
declared nowhere — §7.5.

The 3,775 unmarked ones are the same default with no claim attached: silent absence
rather than false witness. Both are defects; the marked ones are the worse kind,
because the marker is what an auditor would check.

## 4. It is not cosmetic — it moves the score

`scripts/pipeline/scoring/engine.py:301`:

```python
if enrichments.get("migration_score") is not None:
    C_mult *= (1.0 + 0.08 * (1.0 - enrichments["migration_score"]))
```

At 0.5 this is `C_mult *= 1.04`. Every one of the **94,251** defaulted records receives
a 4% consequence uplift derived from a number nobody measured. The honest branch
already exists and is correct: when the value is `None`, the modifier is skipped
entirely. Convention #56 was built for exactly this case and fired honestly only
964 times.

## 5. How the state arose

`enrich_country()` in `migration_score.py` writes value and marker together:

```python
se["migration_score"] = score      # may legitimately be None
se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
```

In NARROW scope it *skips* records that already hold a value — and the ingestion
default 0.5 is a value — so a NARROW pass cannot produce this pairing. The pairing
requires a pass that wrote the marker, followed by something that re-supplied 0.5
underneath it. That is the same shape as the reversion traced this session to the
estate's own scheduled bot (`f7623ca6`): **ingestion re-running after enrichment,
restoring its default while the enrichment's marker survives.** The marker outlives
the value it was minted to describe.

## 6. Latent defect, separate, currently harmless

`sample_score` step 4:

```python
if self._nodata is not None and raw == self._nodata:
    return None
```

The raster's nodata is `nan`, and `raw == nan` is always False. **This branch has
never once fired.** It is saved entirely by step 5's `math.isfinite` guard. The
code reads as though two defences are in place; one of them is decorative. Record
it now: a NaN nodata must be compared with `isnan`, never with `==`.

## 7. What must NOT be done

Do not simply null the 94,251 and land it. Removing `×1.04` from 15.1% of the
estate is a propagation event: it moves `C_mult`, then R3, then the composite, then
bands. Under Pin 16 it goes decide → acquire → measure → pin → derive → propagate →
project → **measure** → land, and the band migration must be counted *before* the
render, not discovered after it.

## 8. Recommended course

1. **Pin the fact** that 0.5 is unreachable from NIVA, in `SSI_FOUNDATION_judgement.yaml`.
   It is a property of the instrument, and it is what makes the marker checkable.
2. **Re-run `enrich_country` with `force_rewrite=True`** across the 33-country cohort.
   Each record then gets either a real NIVA sample or an honest `None`. Expect a
   large number of `None`s: 79.4% of the raster is NaN, and substations sit on land
   the raster may not cover.
3. **Measure the band migration** before anything is rendered.
4. **Add a guard** that fails the build when `migration_score == 0.5` co-occurs with
   the NIVA marker. The invariant is exact and cheap: the instrument cannot emit it.
   This is the same discipline as the guard that now verifies the normalisation
   invariant rather than trusting its own marker.
5. **Fix step 4** to use `math.isnan` — not because it bites today, but because the
   next raster may declare `-9999`.
6. **Order ingestion after enrichment, or make ingestion refuse to overwrite a
   marked field.** Until that holds, this state will simply return on a Thursday.

## 9. What this says about markers generally

The estate now has two instances of the same lesson within one session: a marker
that blocked its own repair, and a marker that certifies a value its own instrument
cannot emit. Both were written as *assertions of history* and both were read as
*assertions of state*.

> **A provenance marker is evidence only if the claim it makes can be checked
> against the instrument. Where the instrument's range is knowable, the guard must
> check the value against the range — never the value against the marker.**

Here the check is a single comparison, and it would have failed on 90,476 records
the day the marker was written.


---

## 10. The repair, measured before it is written (item 2)

`rasterio` was installed on the operator machine and
`migration_score.py --all-countries --force-rewrite --dry-run` was run against
all 39 countries. It is fast — ~15,000 substations/second, 32 seconds for the
estate — and it is read-only.

**The repair is far cleaner than section 8 predicted.** Section 8 warned to
"expect a large number of `None`s, 79.4% of the raster is NaN". That reasoning
was about the raster as a whole, most of which is ocean. Substations are not
distributed like ocean. Measured:

| | |
|---|---:|
| substations processed | 622,104 |
| real NIVA values available | 621,056 (99.83%) |
| honest `None` — Convention #56 | 1,048 (0.17%) |
| missing coordinates | 0 |

The `None`s concentrate exactly where they should: us 504, canada 210, france 99,
uk 61, italy 46, norway 43 — remote and offshore sites. No country is degraded
wholesale.

So the repair replaces 94,251 typed defaults with **measured values**, not with
absences. Only 1,048 records estate-wide lose the modifier to an honest null.
(`n_written + n_none + n_skipped + n_missing = 622,104` — the audit JSON
reconciles exactly to the estate.)

### What still must be measured before landing

The dry run tells us what `migration_score` becomes. It does **not** tell us what
the *score* becomes. Every one of the 94,251 currently receives `C_mult *= 1.04`;
after the repair each receives `C_mult *= (1 + 0.08·(1 − m))` for its own measured
`m`, which ranges across the full `[0, 1]`. The raster's own score distribution is
strongly bimodal — p25 = 0.041, p50 = 0.393, p75 = 0.965 — so individual records
will move in **both** directions, some by considerably more than 4%.

Under Pin 16 the band migration is counted before the render, not after it.

## 11. Second correction to my own reasoning, recorded

Section 8 step 2 said to expect many nulls. That was an inference from the
raster's NaN fraction, and it was wrong by three orders of magnitude — 1,048
rather than the tens of thousands implied. The error was to reason about the
instrument's coverage instead of measuring the instrument *at the sample points*.

> **Coverage of a raster is not coverage of the estate. The only honest statement
> about how much data an instrument yields is the count at the actual sample
> points.**

Two errors in one document, both mine, both of the same family: a statement about
a population made without querying the population. They are left in rather than
edited out, because the finding is precisely that markers and inferences are not
measurements.

---

## 12. Projection of the repair's effect on the modifier (read-only)

The raster was sampled directly at the coordinates of all 94,251 defaulted
records, and the production modifier recomputed. Nothing was written.

| | |
|---|---:|
| records at the typed default `0.5` | 94,251 |
| → become a **measured** value | 94,216 |
| → become an honest `null` (lose the modifier) | 35 |

**Migration modifier, now versus after:**

| | now | after p5 | p25 | p50 | p75 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| `C_mult` factor | ×1.0400 | ×1.0009 | ×1.0134 | ×1.0367 | ×1.0583 | ×1.0742 |
| ratio to today | — | ×0.9624 | ×0.9744 | ×0.9968 | ×1.0176 | ×1.0329 |

**Direction of travel — it is not one-sided:**

| | records | share |
|---|---:|---:|
| modifier decreases (record's consequence falls) | 50,203 | 53.3% |
| modifier increases (record's consequence rises) | 44,013 | 46.7% |
| \|change\| > 2% | 50,004 | 53.1% |
| \|change\| > 3% | 23,553 | 25.0% |
| full range of the swing | ×0.9615 … ×1.0385 | |

The swing is **bounded by construction**: the modifier is `1 + 0.08·(1 − m)`
with `m ∈ [0,1]`, so it can only live in `[1.00, 1.08]`, and the ratio against
today's `1.04` can only live in `[0.9615, 1.0385]`. No record can move more than
3.85% on this factor.

This is the modifier, **not** the score. `C_mult` enters R3, R3 enters the
composite, and the composite is what bands. The band migration itself is a derive
output and is still uncounted. It is the last thing that must be measured before
anything is rendered or landed.

Worth stating plainly, because it cuts against the instinct to treat this as a
clean-up: the median record barely moves (×0.9968), but a quarter of them move
more than 3%, and they move in **both** directions. This repair does not
uniformly improve or worsen the estate. It replaces a uniform fiction with a
distribution.

---

## 13. The repair, executed and verified (item 2 complete)

Run 2026-09-21 15:14, 39 countries, 69 seconds. Verified against the **full
estate**, shards followed:

| class | before | after |
|---|---:|---:|
| measured value | 526,887 | **621,056** (99.8%) |
| `0.5` with false NIVA provenance | 90,476 | **0** |
| `0.5` undeclared | 3,775 | **0** |
| explicit `null` (Convention #56) | 964 | 1,048 |
| stale `_migration_score_semantic_normalise_source` | 11,492 | **0** |
| values outside `[0,1]` | 0 | 0 |
| records with no provenance marker | 3,775 | **0** |

### 13.1 A second marker defect, caught before it was created

`migration_score.py` never touched `_migration_score_semantic_normalise_source`.
A bare `--force-rewrite` would therefore have left **11,492 records** asserting
a rescale of a value that had just been replaced — this document's defect,
manufactured a second time, by the repair for the first.

The write site now clears any marker describing the value it replaces:

```python
STALE_ON_REWRITE = ("_migration_score_semantic_normalise_source",)
...
se["migration_score"] = score
se[AUDIT_TRAIL_KEY] = AUDIT_TRAIL_VALUE
for _stale in STALE_ON_REWRITE:
    if se.pop(_stale, None) is not None:
        n_stale_markers_cleared += 1
```

> **Whoever replaces a value removes the markers that describe the old one.**

### 13.2 Band migration, projected

`R_median` is the median of a 10,000-sample Monte Carlo, so it does not equal
the deterministic `soft_clip_upper(R_base × mult_product) + add_sum`. The gap
is ordinary — median 0.0046, p95 0.016 — and an earlier pass that treated it
as a defect and excluded 48% of the estate was **wrong**. Projecting the
*difference* cancels the offset, and coverage rises to everything except the
M-006 neighbourhood.

| | records | share |
|---|---:|---:|
| unchanged by the repair | 487,107 | 78.3% |
| carry no `R3_C_mult` — migration never applied to them | 78,493 | 12.6% |
| **projected** | **54,608** | 8.8% |
| inside the M-006 neighbourhood — not projectable | 1,829 | 0.3% |

**`R_median` shift across the 54,608:** p25 −0.014, median −0.006, p75 +0.006,
range −0.307 … +0.327. **33,959 improve, 20,649 worsen.**

| band migration | records |
|---|---:|
| absolute rule | **3,174** of 54,608 (5.81%) |
| normalised rule, country P5/P95 held fixed | **6,219** |
| normalised rule, country P5/P95 recomputed | 43,673 |

The largest single flow is `High → Medium` (1,069 absolute, 1,308 normalised),
and the reverse flows are substantial in both directions. **This is not a
clean-up that improves the estate; it is a correction that moves it both ways.**

The third row is not the repair's doing. Recomputing each country's percentiles
re-bands records the repair never touched — an order of magnitude more movement
from Phase η than from the repair itself. **The two must not be landed together
or their effects cannot be told apart.**

### 13.3 Two things this surfaced that are not yet closed

1. **78,493 records (12.6%) carry no `R3_C_mult` at all**, so the migration
   modifier has never applied to them. Whether that is legitimate or a further
   silent absence is not established here.
2. `pipeline-enrichment.yml` runs the pipeline (the derive) at step "Run
   pipeline" and the enrichment steps *after* it, committing at the end. If
   that ordering is what it appears to be, published `R_median` routinely lags
   its own enrichments by a cycle. **Stated as a question, not a finding** — it
   has not been verified.

---

## 14. The mechanism, found by name — and Phase ζ stopped before it ran

§5 said the false pairing "requires a pass that wrote the marker, followed by
something that re-supplied 0.5 underneath it", and §13.3 left that as a
question. It is now answered, and the answer was found **while preparing Phase
ζ, one command before starting a 4–6 hour run that would have re-created the
defect.**

`scripts/pipeline/scoring/engine.py`, `score_substation`:

```python
if socio_update and "V_socio" in socio_update:
    se = updated.get("socio_economic", {})
    for key in ["V_socio", "EP_rate_region", "gdp_per_capita", "unemployment_rate",
                 "E2_local", "rd_pct_gdp", "elderly_pct", "migration_score"]:   # <—
        if key in socio_update:
            se[key] = socio_update[key]
```

`socio_update` is the socio-economic **ingestion's** block. Its province tables
carry a `migration_score` column, and for most countries that column is the
hard-coded `0.5, # Neutral default`. So every rescore of a matched substation
replaced the enrichment's measured value with the ingestion's default — and
left `_migration_score_source` untouched, because nothing in this path knows
the marker exists.

**The marker is not overwritten because it is not in the list. The value is
overwritten because it is.**

### 14.1 Measured, immediately after the repair

`overlay_socioeconomic()` was run for real and its output fed to
`score_substation()` against the freshly repaired records:

| country | rescored | `migration_score` the ingestion would supply | repaired values overwritten |
|---|---:|---|---:|
| slovenia | 1,728 | `0.5` for all 1,728 | **1,728** |
| luxembourg | 723 | real values (its table has migration data) | **634** |

Slovenia is the clean case: **every** gated record straight back to exactly
0.5, under a NIVA marker, hours after being repaired.

### 14.2 A hypothesis falsified on the way, worth keeping

The first empirical check used **greenland**, and it returned real values with
nulls passed through as `None` — apparently exonerating the path. Greenland has
no province-table match and falls through `else: # Keep existing data`, which
returns the record's own block. The sample was unrepresentative and nearly
produced the opposite conclusion.

> **An empirical check on a case that takes the other branch is not evidence
> about the branch under suspicion.**

### 14.3 The fix

`migration_score` removed from the copy list, with the measurement recorded at
the site. The rule it encodes:

> **A field with an enrichment owner is not the ingestion's to write.**

Re-measured after the change: slovenia 1,728 rescored, **0** values moved;
luxembourg 723 rescored, **0** moved.

`tests/test_enrichment_owned_fields_survive_rescore.py`, 4 assertions, green,
and verified to fail — 3 of 4 — when the field is put back. It pins both the
list (by AST, not grep) and the behaviour, and separately pins that a
substation with no measured value stays declared-absent rather than acquiring
the default, which is Convention #56 rather than a typed 0.5.

### 14.4 What this means for the schedule

Phase ζ was one command away. Had it run first, it would have reset the
repaired records on every country whose province table carries the default,
re-stamped nothing, and produced a 39-country rescore built on the value the
whole workstream exists to remove — at 4–6 hours, and with the published
`R_median` then *consistent* with the false value, which is worse than the
inconsistency it was meant to resolve.

The three bot windows are governed by Pin 13. This path was not. It is now.

---

## 15 · CORRECTION — the repair has no scoring consequence, and §4 was wrong

§4 of this document is headed *"It is not cosmetic — it moves the score"* and
asserts that `engine.py:301` applies `C_mult *= 1.04` to every defaulted record.
**That is false.** §12 and §13.2 then projected a band migration from it. Those
projections were arithmetic over a code path that never executes.

### How it was established

Phase ζ ran. Measured against the pre-ζ snapshot, **532,187 records moved in
`R_median` and 78,118 did not.** The split is perfect and it is not about
migration:

| | n | median ratio | moved up |
|---|---:|---:|---:|
| carries the retired `R7_cyber` | 543,546 | 1.0086 | 85.6% |
| never carried it (control) | 78,118 | **1.0000** | **0.0%** |

Not one record without the retired modifier moved. So ζ's entire effect is the
**v4.24 R7_cyber v1 retirement** finally being applied — the deferred
methodology cutover — and none of it is the migration repair.

That prompted the question §4 should have asked at the outset:

```
compute_r3(pop, GWh, V_socio, enrichments=None)     engine.py:288
```

**Call sites of `compute_r3` in the entire repository: one.**
`run_greenland_s1.py:180`, which passes no enrichments. **Occurrences of
`enrichments=` anywhere in the repository: zero.**

The enrichments branch at `engine.py:296–303` — which contains the
`migration_score` term — **is never reached in production.**

`R3_C_mult` is written in exactly one production place:

```python
# scripts/enrich_esg_gaps.py:341
if not sub['modifiers'].get('R3_C_mult'):
    v_socio = se.get('V_socio', 0.30)
    sub['modifiers']['R3_C_mult'] = round(1.0 - v_socio * 0.15, 4)
```

From `V_socio` alone. No migration term. And **write-once** — guarded by
`if not ...get(...)`, so once set it never updates, which is why ζ left it
untouched.

### What this does and does not change

**Unchanged.** The finding itself stands entirely. 90,476 published records
carried a provenance marker asserting a source that could not have produced the
value; the instrument cannot emit 0.5; the repair replaced 94,251 typed
defaults with measured values. §7.2 and §7.5 are breached by a false
provenance claim whether or not the field is scored.

**Wrong and withdrawn:**
- §4's claim that the defect moves the score.
- §12's projected modifier shift (54,608 records).
- §13.2's projected band migration (3,174 absolute / 6,219 normalised).

All three assumed a consumer that does not exist.

### The error, named

I traced the **callee** and not the **caller**. `engine.py:301` reads as though
it applies the modifier, and it would — if anything called it that way. Nothing
does. One `grep` for the call site would have settled it, and that grep came
eighth, after the projection had been written, landed and reported.

> **"Is this field consumed by any published score?" is answered at the call
> site, never at the definition. A function that would apply a term is not a
> term applied.**

The estate's own pre-paper Q&A asks exactly this question — *"Is
`graph_topology` consumed by any published score, band, ranking or component?
Name every consumer"* — and calls it the most consequential question in the
document. It is the right question and it was not asked here.

### Two things this opens, neither closed here

1. **`migration_score` is, on this evidence, consumed by nothing.** It is
   published, it now carries measured values and honest provenance, and no
   score depends on it. Whether it should be scored, or declared as a published
   attribute that is not an input, is an open decision.
2. **`R3_C_mult` — a live modifier in the published chain — is a hard-coded
   linear function of one input**, written by `enrich_esg_gaps.py`: the same
   script the circularity test found generating `graph_topology` from the MD5
   of substation names. The `0.15` coefficient has no cited source. Pin 14.

---

## 16 · Two corrections to §15, and an open provenance question bigger than this finding

§15 was written between the ζ/η measurement and the AW commit. It contains an
error of its own, which the AW commit message repeats and which is now pushed.

### 16.1 What §15 got wrong

§15 stated that `R3_C_mult` is written in exactly one production place,
`enrich_esg_gaps.py:341`, as `round(1.0 - v_socio * 0.15, 4)`.

**That line is a write-once fallback**, guarded by
`if not sub['modifiers'].get('R3_C_mult')`, and **the published values do not
match it.** Measured on slovenia: three records share `V_socio = 0.2435` and
carry `R3_C_mult` of 0.985201, 1.051591 and 0.967523. A function of `V_socio`
alone cannot produce three values from one input.

### 16.2 What still stands from §15

Unaffected, and re-verified:

- `compute_r3(pop, GWh, V_socio, enrichments=None)` has **one call site in the
  repository** — `run_greenland_s1.py:180`, passing no enrichments — and
  `enrichments=` appears **nowhere**. The migration term at `engine.py:296–303`
  is unreachable in production.
- The migration repair therefore has no scoring consequence, and §4, §12 and
  §13.2 remain withdrawn.

### 16.3 Three candidates eliminated; the writer is unidentified

| candidate | verdict |
|---|---|
| `enrich_esg_gaps.py:341` — `1 − 0.15·V_socio` | **no** — write-once fallback; published values do not match |
| `score-country.py:124` — `det_var(seed+'R3', 1.0, 0.08)` | **no** — reproduces 9.1% of slovenia, 0.0% of luxembourg, greece, portugal, czechia |
| `refresh_v42_modifiers_re_composite.py` | **no** — writes only R6c, R6d, R6e, R8, R9, R10; never touches R3_C_mult |

> **`R3_C_mult` is a live multiplicative modifier in every published score and
> nothing in this repository has been shown to produce its published values.**

That is a larger exposure than the finding this document is named for. The
migration marker was a false claim about a field that turns out to be scored by
nothing. `R3_C_mult` is scored by everything and its provenance is unknown.

### 16.4 What the search did establish

`score-country.py:85`:

```python
def det_var(seed, base, pct=0.15):
    """Deterministic spatial variation using MD5 hash."""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return base * (1 + (h * 2 - 1) * pct)
```

with `seed = sid + name`. On the greenfield onboarding path, **R3_C_mult,
R4_F_topo, R6_restoration, R6_seismic and R7_cyber are all MD5 variates of
substation id and name** — the same generator the circularity test found behind
`graph_topology`, here inside the modifier chain.

And `refresh_v42_modifiers_re_composite.py:553` computes six live v4.2
modifiers — R6c_flood, R6d_wildfire, R6e_winter, R8_adapt, R9_compound,
R10_just — as **MD5-seeded jitter around a country hazard baseline**:

```python
seed_base = f"{sid}|{name}|v42"
center = r_min + exposure * (r_max - r_min)     # exposure is a COUNTRY constant
value  = _det_var(f"{seed_base}|{mod_name}", center, jitter_pct)
```

This is **declared** — Convention #7 documented-proxy, Convention #29 to avoid
discrete clustering — and it is not concealed. But it means those six modifiers
carry a country baseline plus per-substation hash noise, and **no
per-substation measurement**. Whether that is declared to a *reader of the
index*, as against a reader of the source, is a separate question and is not
answered here.

### 16.5 Consequences for the foundational documents

1. `SSI_FOUNDATION_judgement.yaml` pins
   `R3 = clip( 1 + k · consequence_index , range )` with *"k: sensitivity
   constant fixed in the engine"*. **No implementation matching that has been
   found.** `compute_r3` is a sigmoid in pop, load and V_socio; `enrich_esg_gaps`
   is linear and negative in V_socio; `score-country` is an MD5 variate. The
   pinned formula matches none of them.
2. The `R7_cyber` entry states it is *"retained only so that stored scores
   produced under it remain explicable"*. After ζ, **no published score is
   produced under it** — yet 543,546 records still carry the `R7_cyber` key in
   `modifiers` with a value that is no longer applied. A reader of the payload
   sees a modifier that does nothing.
3. The rendered packages were produced 21 September 11:00–12:28, **before** the
   repair (15:14) and before ζ/η (14:08–15:45). Every data-derived figure in
   them is stale. `render2.py` measures the cohort at render time, so this part
   is mechanical: re-render.

### 16.6 The pattern, stated plainly

Three hypotheses about `R3_C_mult` were formed and all three were wrong, each
refuted in minutes by a measurement. The cost of the wrong ones was two
incorrect statements reaching a pushed commit message.

> **A modifier's definition tells you what it would be. Only reproducing the
> published value tells you what it is.**

---

## 17 · §16 narrowed: 1.2% of `R3_C_mult` is explained, and a rule that should have been standing

§16.3 said the writer of `R3_C_mult` is unidentified. That is now too strong in
one direction and too weak in another.

### 17.1 The measurement

Reproducing every published `R3_C_mult` against
`det_var(substation_id + name + "R3", base=1.0, pct=0.08)` clipped to
[0.85, 1.15], to six decimals:

| country | records carrying `R3_C_mult` | reproduced | |
|---|---:|---:|---:|
| hungary | 3,502 | 3,502 | **100.0%** |
| slovakia | 1,512 | 1,512 | **100.0%** |
| iceland | 684 | 684 | **100.0%** |
| israel | 257 | 257 | **100.0%** |
| slovenia | 157 | 157 | **100.0%** |
| every other country | 509,680 | 6 | ~0.0% |

**Estate: 6,118 of 515,798 — 1.2%.** `R4_F_topo` and `R6_restoration` track it
almost exactly (6,133 and 6,676), which is expected: they come from the same
generator in the same block of `score-country.py`.

A further **106,306 records carry no `R3_C_mult` at all** (622,104 − 515,798).

### 17.2 What this establishes and what it leaves open

**Established.** For five countries the modifier chain's first term is the MD5
hash of the substation's id and name, at 100% reproduction. This is the
`graph_topology` circularity finding reaching into the published score itself —
not an adjacent display field.

**Open.** For 509,680 records — 98.8% — the writer of a live multiplicative
modifier in every published score remains unidentified. Four candidates are
eliminated: `enrich_esg_gaps.py:341`, `score-country.py:124` (explains only the
1.2%), `refresh_v42_modifiers_re_composite.py`, and `compute_r3`, which nothing
calls.

### 17.3 The rule this should have produced hours earlier

The previous section of this document was written after testing slovenia alone,
where reproduction was 157 of 157, and it concluded the mechanism was general.
It is not; slovenia is one of the five.

That is the **second** time in one day that a single-country sample produced a
confident and wrong generalisation. The first was greenland, in §14.2, where
the "keep existing data" branch made the socio-economic path look innocent and
nearly closed an investigation that was correct.

> **On a 39-country estate, one country is never evidence about the cohort. A
> mechanism claim is measured across the cohort or it is not measured.**

Both failures share a shape worth naming beyond the arithmetic: the sample was
chosen for convenience — smallest file, fastest read — and convenience is
correlated with atypicality. Greenland was small because it has no province
table. Slovenia carried only 157 modifier values because most of its fleet has
none. **The cheapest country to test is, for that reason, the least likely to
be representative.**

### 17.4 Next step, and it is not another hypothesis

Four hypotheses have now been formed and refuted, each within minutes of a
measurement, and two of them reached a pushed commit message before being
caught. The efficient move is not a fifth.

It is **git archaeology**: for two or three of the large countries, find the
commit that last changed a specific record's `R3_C_mult`. That names the script
directly instead of inferring it. It is read-only, and under Pin 6 it is the
operator's to run.

---

## 18 · Provenance found: the variance in `R3_C_mult` was manufactured to pass a health metric

Git archaeology, binary-searching the commits that touched each country's
`ssi-data.json` for the point where one probe substation's `R3_C_mult` last
changed. Two of three probes land on the same commit.

| country | probe | commit that introduced the current value |
|---|---|---|
| costa-rica | `w656375582` | **`dc761257`, 4 June 2026** |
| czechia | `CZ_12409927581` | **`dc761257`, 4 June 2026** |
| spain | `9000000005` | `d0312749`, 21 July — but the previous value is `NO_RECORD`, so that probe was a *new* substation and the result is inconclusive |

`dc761257` — *"fix(R3): Session 101 — extend per-substation R3_C_mult jitter to
19 FAIL countries (cohort cleanup)"*. Its message is explicit, detailed, and
hides nothing:

> *"D#29 cohort sweep post-Session 100 surfaced 19 of 39 countries with severe
> discrete-R3 clustering … regional socio-economic data applied uniformly to
> all substations in each admin unit, producing 4-20 unique R3 values per
> country."*
>
> *"Applied identical Session 100 hash-deterministic jitter: SHA-1(substation_id)
> first 4 bytes → uniform [0,1) → [-1,+1) → *0.025 (+/- 2.5% multiplicative)."*
>
> *"Also tightened D#29 precision (round(v,4) → round(v,6)) which had been
> masking US's true post-jitter variance (US: 13 unique → 30,886 unique at
> 6-decimal precision = 68.6% ratio). Final cohort D#29 health: 34 PASS /
> 5 WARN / 0 FAIL."*

### 18.1 What this says, read carefully

The real defect is named in the commit itself: **the underlying socio-economic
data is regional, applied uniformly to every substation in an admin unit.**
Four to twenty genuinely distinct values per country. That is the honest state
of the input.

A health metric, D#29, measured distinct-values-per-country and failed 19
countries on it. The remedy applied was **not** to obtain per-substation data.
It was to add a deterministic hash jitter of ±2.5% and to increase stored
precision from four decimals to six.

The metric then passed: 34 PASS / 5 WARN / 0 FAIL.

> **US: 13 genuinely distinct values became 30,886 "unique" values, and the
> health metric read 68.6%.**

Nothing was concealed. The mechanism, the constant, the precision change and
the resulting metric are all written down in the commit message, and the
motivation — defeating discrete-clustering that broke a tier display — was
real. This is not deception. It is something more ordinary and harder to catch:
**a measurement problem answered with a presentation fix, and a metric that
could not tell the difference.**

### 18.2 Why this is the most serious item in this document

The finding this document is named for — 90,476 records under a false
provenance marker — concerns a field that turns out to be **scored by nothing**.

`R3_C_mult` is scored by everything. It is the first multiplicative term in the
modifier chain of every published record. And for the countries traced, its
per-substation variation is **SHA-1 of the substation id**, sitting on top of a
value that is genuinely regional.

A reader of the payload sees 30,886 distinct US values and infers
per-substation measurement. The truth is 13 regional values and a hash.

> **A metric that counts distinct values cannot distinguish measurement from
> noise. Any health check whose failure can be cured by adding entropy is not
> a health check.**

### 18.3 What is established, and what is not

**Established.** For costa-rica and czechia, the published `R3_C_mult` was
written by `dc761257` and is regional value × SHA-1 jitter. The commit names 19
countries: AU BE CO CR CZ DE FI GR HU IS IT JP KR NL NO PT SE TR US.

**Not established, and not to be assumed:**

1. **Spain is unresolved.** The probe substation did not exist before the
   commit found. Re-probe with a record present in the earliest revision.
2. **The two generators are not reconciled.** Five countries — hungary,
   slovakia, iceland, israel, slovenia — reproduce at 100% from
   `score-country.py`'s `det_var`, which is MD5 of *id + name* at ±8%, not
   SHA-1 of *id* at ±2.5%. Hungary and iceland appear in the Session 101 list,
   so something overwrote the jitter for them afterwards. The obvious candidate
   is the v4.23 re-onboarding, which ran `score-country.py` fresh — **but that
   is a hypothesis, it is the fifth in this document, and the previous four
   were wrong. It is to be measured, not assumed.**
3. **Whether D#29 still exists and still passes on this basis** is unchecked.

### 18.4 The method that finally worked

Four hypotheses formed from reading code, all refuted. One binary search over
the commit history, answered in a minute, with the mechanism stated by the
author at the time.

> **When the question is "what produced this value", the commit that wrote it
> is a primary source and the code that could have written it is not.**

---

## 19 · `R3_C_mult` has no single writer — it is sediment, and substation ids are not stable

Round two of the archaeology, probing with a record present in the **oldest**
revision of each file. Two results, both negative in the useful way.

### 19.1 Substation ids do not survive re-ingestion

| country | result |
|---|---|
| spain | *no record both present at the start and carrying `R3_C_mult` now* |
| portugal | same |
| iceland | same |

The id sets do not intersect across history. Whatever `spain/ssi-data.json`
contained at its first commit, **none of those substation ids is still carried
by a record holding `R3_C_mult` today.** The identifiers turned over.

This is a finding in its own right, and it is larger than the probe that
exposed it:

> **`substation_id` is not a stable key across the estate's history.
> Any longitudinal comparison keyed on it — archaeology, drift analysis, a
> before/after of a rescore — silently compares different assets, or nothing.**

It also explains why round one worked at all: costa-rica and czechia happen to
have kept their ids. Two countries out of five probed. It sits beside the
535 records already found carrying duplicate or null ids (australia 438,
turkey 30) — the same key, failing in a second way.

### 19.2 Hungary was written by a June refactor, not the v4.23 re-onboarding

| | |
|---|---|
| probe | `HU_102562`, current `0.953453` |
| introduced by | **`4c09d4cd`, 8 June 2026** — *"Phase 1 v4.0.2 pre-v4.2 foundation refactor: PR-1 through PR-7 + ops follow-up"* |
| previous value | `0.996187`, from `4fee9e32`, 4 June — *"Session 108 — Scoring + ingestion residual cleanup"* |

**The fifth hypothesis — that the v4.23 re-onboarding overwrote the Session 101
jitter — is wrong.** The overwrite happened on 8 June, in an engine refactor,
six weeks before v4.23 re-onboarding began.

### 19.3 What `R3_C_mult` actually is

Three distinct writers are now identified across history, and they are
stratified by when each country was last touched:

| era | writer | countries evidenced |
|---|---|---|
| 4 June 2026 | `dc761257` — Session 101, SHA-1(`substation_id`) ±2.5% jitter over a regional value | costa-rica, czechia |
| 8 June 2026 | `4c09d4cd` — engine refactor PR-1…PR-7 | hungary |
| later | unidentified — ids turned over, ID-keyed archaeology cannot reach it | spain, portugal, iceland |

> **`R3_C_mult` is not one mechanism. It is sediment: each country carries
> whatever generator last ran over it, and no single formula describes the
> published column.**

This was the outcome flagged as possible before round one — *"if they point at
different ones, then `R3_C_mult` has been written by several generators over
time, which would be worse and worth knowing before the foundational
re-render."* It is that case.

### 19.4 The consequence for the foundational re-render

`SSI_FOUNDATION_judgement.yaml` pins:

> `R3 = clip( 1 + k · consequence_index , range )`, *"k: sensitivity constant
> fixed in the engine"*

**No single formula can be correct here, because the deployment does not have
one.** The doctrine cannot be corrected to match the code; there is no one code
to match. The options are therefore narrower and harder than "update the
entry":

1. **Declare the stratification.** The entry states that the published column
   is heterogeneous by era, names the three writers, and declares the tier as
   E3. Honest, and it makes the index's own documentation say that its first
   modifier is not a single measurement.
2. **Re-derive `R3_C_mult` uniformly** from one declared formula across all
   39 countries, and then pin that. This is a data change, it touches every
   published record, and it needs the write-path question resolved first —
   the register already carries 22 unsanctioned writers as BLOCKING.
3. **Retire the modifier**, as `R7_cyber` was, if no defensible formula exists.

This is an operator decision, not a repair. It should be taken before the
foundational documents are re-rendered, because a re-render reprints the pinned
formula either way.

### 19.5 Count

Hypotheses formed about `R3_C_mult` today: five. Refuted: five. Established by
archaeology: three writers, one unidentified stratum, and a key that does not
survive its own history.

> **Reading code tells you what a value could be. Reading history tells you
> what it was. Neither tells you there is only one answer — that has to be
> measured too.**
