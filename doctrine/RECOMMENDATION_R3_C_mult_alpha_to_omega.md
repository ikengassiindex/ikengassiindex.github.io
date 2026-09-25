# RECOMMENDATION — connect `R3_C_mult` alpha to omega

**Date** 21 September 2026
**Asked** what to do about a modifier that is sediment
**Answer** derive it from the one genuinely per-asset measurement the estate
already owns, and retire the jitter — the data that made the jitter
unnecessary arrived seven weeks after the jitter was applied

---

## 1 · The measurement that changes the answer

§19 concluded that `R3_C_mult` has no single writer and left three options,
all unattractive. A fourth exists, and it is better than all of them.

`socio_economic.population` — GHSL catchment population, per substation:

| | |
|---|---:|
| records carrying it | **618,534 of 622,104 (99.4%)** |
| carrying `_catchment_population_source` | 619,522 (99.6%) |
| declared source | `GHSL_POP_R2023A_E2025_v4_2_task_451` |

And it **varies per asset**, which is the whole point:

| country | records | distinct `population` | distinct `V_socio` |
|---|---:|---:|---:|
| spain | 12,438 | **10,022** | 47 |
| portugal | 13,564 | **11,968** | 21 |
| czechia | 8,899 | **8,155** | 26 |
| hungary | 3,507 | **3,169** | 57 |
| turkey | 4,031 | **3,679** | 6 |
| slovenia | 1,731 | **1,643** | 12 |

80–95% distinct, from a raster extraction. Against `V_socio` at 6–57 distinct
per country — which is precisely the regional uniformity commit `dc761257`
described as *"4-20 unique R3 values per country"* and answered with SHA-1
jitter.

> **The clustering that the jitter was invented to hide is fixed by data the
> estate acquired in July. The jitter was applied on 4 June; catchment
> population landed at task #451 on 23 July. The workaround outlived the gap
> it was working around by two months.**

Nobody did anything wrong. The remedy was reasonable in June and has been
obsolete since July, and nothing existed to notice.

---

## 2 · The chain, stated end to end

**α — inputs**

| input | status | tier |
|---|---|---|
| `population` — GHSL catchment extraction, per asset | **measured**, 99.4% coverage, 80–95% distinct | E1 |
| `V_socio` — from regional EP rate, GDP, elderly share | **regional**, 6–57 distinct per country — declare it as regional | E1, regional |
| `load_GWh_annual` | **present on 37 records of 622,104 (0.0%)** | absent |

**function** — `compute_r3` already exists and is nearly right:

```
z      = β_pop·log₂(pop/pop_med) + β_load·log₂(GWh/GWh_med) + β_vuln·V_socio
C_mult = range_lo + (range_hi − range_lo) / (1 + exp(−steepness·z))
```

**ω — effect**: `R3_C_mult` → `mult_product` → `soft_clip_upper(R_base ×
mult_product) + add_sum` → `R_median` → `classification` → published band.

Every link is already implemented. **Nothing needs inventing. What is missing
is that nothing calls it.**

---

## 3 · The four things to settle before it can be pinned

**3.1 The load term has no data.** `GWh` is present on 37 records. Either drop
`β_load` from the formula and say so, or declare the term absent under
Convention #56 — but it must not silently take a default, which is how the
migration defect began. **Recommendation: drop it.** A consequence function of
population and vulnerability is defensible; one with a phantom third term is
not.

**3.2 The seven constants are unsourced.** `β_pop 0.04, β_load 0.03,
β_vuln 0.02, pop_med 2456, GWh_med 3200, steepness 4, range [0.70, 1.30]`.
Pin 14 requires a coefficient to be verified against a primary or secondary
source. `pop_med = 2456` looks empirical — if it is a cohort median it should
be *derived and re-derived*, not frozen as a literal. Each constant needs a
citation or an explicit E3 declaration.

**3.3 The range disagrees with itself.** The engine says `range_hi = 1.30`;
the modifier registry and `judgement.yaml` say `1.50`; `validate_schema.py`
carries a note about the ceiling "drifting from pipeline's 1.50". Three
statements, two values. Settle it before pinning.

**3.4 The enrichments branch.** `compute_r3` has an unreachable branch
applying `migration_score`, `fiscal_energy_composite` and
`elderly_vuln_weight`. **Recommendation: remove the migration term.** Net
migration is a socio-economic trend, not a consequence-of-failure variable;
folding it into a criticality multiplier is a category error. That also
resolves the open `migration_score` question — it becomes, explicitly, a
published attribute that is not a scoring input.

---

## 4 · Where it must run

**In the engine, called from the deployment path. Not a repair script.**

The register already carries `published record / write paths` as BLOCKING with
22 unsanctioned writers. A one-off re-derivation would be the twenty-third and
would make the estate's worst structural row worse while fixing a narrower
one. Derived in the engine and invoked by the pipeline, this row gets *better*,
because one more field stops being written from outside.

This also means the Phase-ζ lesson applies: `merge_and_rescore` gates on
`needs_rescore = has_seismic or has_climate or has_socio`, and a formula change
is not an input change. Whatever mechanism is chosen must not be input-gated,
or it will leave another 11,361 records behind.

---

## 5 · Continuity is not owed here, and that makes this cheap

Normally, replacing a modifier across 622,104 published records demands a
migration plan. **It does not here.** §19 established that the existing column
is sediment — three writers by era, one unidentified, over a key that does not
survive its own history. There is nothing to preserve, because the old values
were never a measurement of anything.

So the change is a recomputation, not a migration. No before/after
reconciliation is owed beyond measuring the band movement, which is owed for
any score change.

---

## 6 · The verification, which is the point of "alpha to omega"

One conformance row, and it is the `variance provenance` aspect proposed in
`DESIGN_three_aspects_the_conformance_register_is_missing.md`:

| | |
|---|---|
| declared | `R3_C_mult = compute_r3(population, V_socio)`, constants pinned |
| observed | % of published values reproducing from that call, per country |
| conforms | 100% |

Today the honest observed value would read *"reproduces from SHA-1 of the
substation id on costa-rica and czechia; from MD5 of id+name on five
countries; unidentified elsewhere."* After the change it reads 100% or it
names its own defect. **That row is what "connects alpha to omega" means in
practice: a published number that reproduces from a named measurement through
a named function, checkable by anyone.**

---

## 7 · What this closes

| open item | closed by this |
|---|---|
| `R3_C_mult` provenance is sediment (§19) | yes — one writer, in the engine |
| D#29 discrete clustering | yes, and **honestly** — variance from a raster, not a hash |
| `judgement.yaml` pins a formula matching no implementation | yes — pin what is computed |
| foundational re-render blocked | unblocked once pinned |
| `migration_score` consumed by nothing | resolved by decision: declared a non-input |
| `variance provenance` conformance aspect | has something to pass |
| unsanctioned writers, trending | improved by one rather than worsened |

---

## 8 · Risks, stated plainly

**8.1 It is a large score movement.** Every record's first modifier changes.
Expect more band migration than today's 80,474. It must be measured against a
snapshot before landing, and it must not be bundled with anything else — today
showed how quickly two simultaneous changes become inseparable.

**8.2 Population is right-skewed and the sigmoid is unbounded in `z`.** `log₂`
handles the skew; the sigmoid handles the tails. But `pop_med` now
*determines* where the estate sits on the curve, so it stops being a harmless
constant and becomes the single most consequential number in the modifier.
It needs a derivation and a source, not a literal.

**8.3 3,570 records have no population** (622,104 − 618,534). They must take
Convention #56 — declared absent, modifier not applied — and **not** a default.
That is the discipline the whole of today's finding exists to enforce.

**8.4 `V_socio` remains regional.** After this change R3's variance comes
almost entirely from population. That is honest and should be *said*: the
consequence multiplier is driven by catchment population, modulated by a
regional vulnerability term.

---

## 9 · Recommendation in one line

> **Derive `R3_C_mult` in the engine from GHSL catchment population and a
> declared-regional `V_socio`, drop the load term, source or declare every
> constant, pin the formula to what is computed, and prove it with a
> reproduction row at 100%.**

The jitter was a reasonable answer to a real problem in June. The data that
makes it unnecessary has been sitting in the estate since July.

---

## 10 · Addendum, 21 September evening — two operator questions, both measured

### 10.1 The range does not disagree with itself. §3.3 was wrong.

Searched the audit trail, as directed. `engine.py:305`:

```python
return soft_clip(C_mult, p["range_lo"], 1.50)
```

and the sigmoid above it is `range_lo + (range_hi − range_lo)/(1+e^…)` with
`range_hi = 1.30`. **The function can only emit (0.70, 1.30), so the 1.50 clip
never binds.** These are not two claims about one bound: 1.30 is the sigmoid's
asymptote, 1.50 is the registry's declared range. `validate_schema.py`'s note
records syncing the *validator* to the registry, not the engine to anything.

§3.3 is withdrawn. What remains is milder and still worth fixing: **the
declared range [0.70, 1.50] is wider than anything the function can produce.**
Under a declared-versus-observed posture that is slack in the declaration —
the published range overstates the modifier's authority by 20 points. Either
tighten the declaration to [0.70, 1.30], or widen the sigmoid deliberately and
say why.

### 10.2 "A substation serves a different catchment — countryside versus capital"

Correct, and the measurement is larger than the intuition. Catchment
population across 618,251 records:

| | |
|---|---:|
| min | 1 |
| p1 | 71 |
| p10 | 2,276 |
| **p50** | **27,513** |
| p90 | 239,293 |
| p99 | 876,913 |
| max | 3,278,543 |

**p99/p1 = 12,351× — 13.6 doublings.** The rural-to-capital span is four
orders of magnitude, and it is exactly the signal R3 should carry.

#### The miscalibration this exposes

> **`pop_med = 2456` sits at the 11th percentile of the actual distribution.**

The sigmoid is centred on `pop_med`. With it at p11, **89% of the estate sits
above the centre of the curve** — the function is calibrated for a fleet that
does not exist. Whatever 2,456 described once, it is not the median catchment
now. This alone settles §3.2: the constant must be **derived, not cited**.
A literal cannot track a cohort that grew from 174,046 substations to 622,104.

#### Cohort median or per-country median

Per-country medians span 37×:

| | | | |
|---|---:|---|---:|
| norway | 2,021 | spain | 17,812 |
| greenland | 3,196 | iceland | 20,678 |
| slovenia | 12,016 | france | 20,956 |
| germany | 33,014 | **turkey** | **74,344** |

Under a **per-country** median, a Norwegian substation serving 2,021 people
and a Turkish one serving 74,344 both score `C_mult ≈ 1.0`, because each is
median for its own country. That is within-country relativism, and it is the
same defect the estate already carries with two band rules: a number that
means a different thing in each jurisdiction.

Under the **cohort** median (27,513), a substation serving 27,513 people
scores ≈ 1.0 wherever it stands. Norway's fleet mostly scores below it,
Turkey's mostly above.

> **Consequence of failure is an absolute quantity. A substation serving 2,000
> people has less consequence than one serving 500,000, and that is true
> regardless of which country each sits in. Per-country normalisation would
> erase precisely the signal a policy instrument exists to carry.**

**Recommendation: cohort median, re-derived every run.** It is self-sourcing
under Pin 14, it tracks cohort growth, and it keeps R3 comparable across
borders — which is the one property the band labels have already lost.

#### A calibration question that follows

With `β_pop = 0.04` and `steepness = 4`, the full p1→p99 population span maps
to roughly `C_mult` 0.884 → 1.177. **Twelve thousand times the population buys
a 33% spread in the modifier.** Recentring on the true median fixes *where*
the curve sits; it does not change how flat it is. Whether that sensitivity is
right is a separate, declared choice — and it should be made with the ceiling
question in 10.1, not before it.
