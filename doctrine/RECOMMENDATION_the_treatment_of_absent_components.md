# RECOMMENDATION — the treatment of absent components

**Date** 24 September 2026
**Occasion** The operator directed that the literature be checked before any rule for missing components is chosen, and stated the position it must serve: *an absent component must be brought in and scored.*
**Status** Evidence assembled for a pin NOT YET TAKEN. Nothing is declared and nothing was changed.
**Reach** Governs whether 78,525 published records should carry a score at all, and what `R_base` does with an absent component on every record.

## The question

`compute_r_base` is `Σ w_c · components.get(c, 0)`. An absent component contributes
zero. Three treatments were on the table:

1. renormalise the weights over the components present;
2. keep zero, as the declared master equation has it;
3. withhold the score where too little is present.

The instruction was to let the literature guide the choice rather than reason
to one.

## What was read, and what was not

Read, and cited below on that basis:

- **JRC, *Tools for Composite Indicators Building*, EUR 21682 EN** (Nardo,
  Saisana, Saltelli, Tarantola) — §4, §4.1, §4.2 on missing data and imputation.
- **EC Knowledge4Policy, *10-Step Guide*, Step 3 — Imputation of missing data.**
- **COINr documentation, ch. 6, *Missing data and imputation*** — the JRC's own
  composite-indicator toolkit.
- **WIPO / JRC, *Global Innovation Index 2017*, Annex 3 — JRC statistical audit.**

**NOT read, and therefore not cited for anything:** the OECD/JRC *Handbook on
Constructing Composite Indicators* (2008), which is the canonical reference here.
Both publisher hosts refuse automated retrieval. It needs a manual download
before it can support a declaration. §7.6 and the anti-theatre rule bind the
author of this document exactly as they bind any other — a reference named
without being read would be a fabricated E2, and an admitted gap outranks one.

## Finding 1 — renormalising is not "no imputation". It is mean imputation.

COINr states the identity plainly: excluding a missing value from a weighted
mean is mathematically equivalent to assigning that group's mean to the missing
value.

So option 1 is not a neutral accommodation of absence. On the 78,525 records it
would assert that a substation's continuity, voltage quality, economic
consequence, saturation and transition scores each equal its infrastructure
exposure — an unevidenced claim about five quantities, made silently, on an
eighth of the estate.

Evidence tier **E1** — a definitional identity, not a contested empirical claim.

## Finding 2 — the established practice is an inclusion threshold, not a fill

The Global Innovation Index, under JRC statistical audit, does not score an
economy that lacks the data. It requires **at least 66 per cent data
availability within each sub-index separately** — 36 of 54 variables in the
Input Sub-Index, 18 of 27 in the Output Sub-Index — and at least two of three
sub-pillars computable per pillar. An economy below that is excluded from the
index entirely.

The audit gives the reason: the criterion exists so that published scores are
not particularly sensitive to the missing values.

Evidence tier **E2** — published practice in a peer-audited index, with the
threshold stated and its rationale given.

## Finding 3 — even above the threshold, absence distorts

The same audit records what happens inside an included economy under a
no-imputation rule: the available indicators in an incomplete pillar may
dominate, biasing ranks up or down. It also notes the perverse incentive — a
no-imputation rule can encourage a unit not to report low values.

The first of those is the SSI estate precisely: component I dominating a record
where nothing else was measured.

Evidence tier **E2**.

## Finding 4 — the warning, with its correct provenance

The line usually attached to the OECD Handbook is not the Handbook's. JRC
EUR 21682 §4 quotes **Dempster and Rubin (1983)**, who call imputation
"both seductive and dangerous" — seductive because it lets the user believe the
data are complete after all.

Recorded because this estate has a rule about citations that travel without
their source, and this one travels constantly.

## The three options, as the literature ranks them

| | what it actually is | standing |
|---|---|---|
| Withhold below threshold | the GII's published practice | **supported, E2** |
| Renormalise over present | implicit mean imputation | documented to bias ranks |
| Zero-fill — **the current deployment** | implicit imputation of the *best possible* value, since higher is worse | unsupported anywhere read |

Current practice is the worst of the three, and it is worst in the direction
that matters: an absent component reads as no risk. It is what produces 48,478
substations published as Low on no measurement at all.

## The SSI Index measured against the threshold

```
78,525 records   components {}                  0 of 6 present
                 after an I-only rebuild        0.25 of weight
543,546 records  6 of 6 present, five a hash    0.25 × 0.720 = 0.18 of weight real

  component I's own metric coverage             0.720   ABOVE the 2/3 threshold
  the 107,559 records at coverage               0.630   BELOW it
```

Stated plainly: **under the inclusion rule of a JRC-audited index, the SSI Index
as deployed today is below threshold nearly everywhere.** Not because its
definitions are wrong — because 866 of 1,097 declared sources are fetched by
nothing (`FINDING_the_index_declares_1097_sources_and_fetches_231.md`).

The one part that passes is component I, at 0.720.

## What this recommends

**It recommends the operator's own position, and finds evidence for it.** The
literature's answer to sub-threshold coverage is not a better treatment rule. It
is the data. An absent component is brought in and scored; until it is, the
honest options are to withhold or to declare, and neither is a substitute for
acquisition.

Concretely, for a pin:

1. **A declared availability threshold, at 2/3**, applied per component and per
   composite, on the GII precedent. Component I passes it at 0.720; the 107,559
   records at 0.630 do not.
2. **Rebuild component I where the components already exist** — 543,546 records.
   No missing-component treatment arises there; all six are present, five are a
   hash, and replacing one of them with a measured value needs no rule.
3. **Hold the 78,525 empty-component records.** A 1-of-6 composite is a
   treatment decision, and the literature says a unit that far below threshold
   should not carry a published score.
4. **Read the Handbook before pinning the threshold.** The GII precedent is
   sufficient to act on and not sufficient to legislate from alone.

## What this does not decide

It does not decide the threshold's value — 2/3 is a precedent, not a derivation,
and the GII applies it to variable counts while this estate would apply it to
intra-weight, which is a different quantity. It does not decide what is
published in place of a withheld score. And it does not touch the declared
master equation, which still reads `Σ w_c · component_c` and would have to be
amended under §8 for any renormalisation.

## Related

- `FINDING_78525_scores_are_the_flood_term_alone.md`
- `FINDING_the_index_declares_1097_sources_and_fetches_231.md`
- `FINDING_what_the_components_fill_costs.md`
- `FINDING_the_chain_is_closed_and_the_residual_moved.md`

---

# ADDENDUM — 25 September 2026: the Handbook, read

The document above was written with the OECD/JRC *Handbook on Constructing
Composite Indicators* (2008) **unread**, because both publisher hosts refuse
automated retrieval, and it cited the Handbook for nothing. The operator
downloaded it. It is now read, and it does not support the recommendation above.

## What it actually says

**Three mechanisms, and ours must be classified.** §1.3 distinguishes MCAR
(missingness independent of everything), MAR (conditional on other observed
variables) and NMAR (dependent on the missing values themselves). It states
there is no statistical test for NMAR and often no basis for judging which
applies, and that most imputation methods require MCAR or MAR.

**The SSI's missingness is MAR, and demonstrably so.** The 78,558 empty-component
records are not spread evenly: austria is 95.0 per cent missing, poland 91.9,
czechia 87.9, while france, germany, italy, the uk, spain, portugal, sweden and
israel are at zero. Missingness is conditional on the country — an observed
variable — and on nothing about the substation's resilience. That is MAR by the
Handbook's own definition.

**Which rules out the recommendation above.** §1.3 on case deletion: it produces
unbiased estimates only where the deleted records are a random sub-sample, the
MCAR assumption. Ours are not random — deleting them would remove most of
austria, poland, czechia, slovenia, lithuania, belgium and latvia while removing
none of france or germany, and would bias the cohort comparison the index exists
to make.

**And it gives a threshold, pointing the other way.** The Handbook's rule of
thumb, attributed to Little & Rubin (2002): above 5 per cent missing, cases are
not deleted. The estate is at 12.6 per cent on components and far higher on
C, V, E, S and T. By that rule exclusion is not available at all.

**Its expected end state is a complete dataset**, with a reliability measure per
imputed value so the imputation's effect on the composite can be explored, and
the procedure documented.

**Box 4 offers no single method** — the choice depends on the data, the amount
missing and which country and indicator it is missing for — and proposes
validation by in-sample/out-of-sample: withhold known values, impute them,
compare.

## Why the GII precedent and the Handbook disagree

They answer different questions. The Global Innovation Index rule — at least
66 per cent availability per sub-index, below which an economy is excluded — is
a **publication** rule about which units an index reports. The Handbook's §1.3
is an **analysis** rule about how to construct a dataset. The document above
took the first as though it settled the second. It does not, and the two
genuinely conflict on this estate: the GII rule would exclude, the Handbook says
that at this level of missingness exclusion biases the result.

Where they agree is that the absence must be visible and its effect measurable.
Neither sanctions what the deployment does now, which is to fill components from
a hash of the substation's name and publish the result without a reliability
measure.

## The distinction neither source addresses, and it is the governing one

Every imputation method in the Handbook — unconditional mean, regression,
expected maximisation, multiple imputation by MCMC — learns from **observed
values of the same variable**. Box 4's validation requires a complete part of
the dataset to withhold from.

The SSI Index has no observed values of C1–C4, V1, E1, E2, S1–S3 or T1. Not
few: none. Fifteen of the twenty-one metrics sit on zero records
(`FINDING_the_index_declares_1097_sources_and_fetches_231.md`). These are not
missing values in a measured variable. They are **unmeasured variables**, and no
method in the Handbook applies to them, because there is nothing to learn from.

That is why the operator's direction — that an absent component must be brought
in and scored, not treated — is the position the literature supports once the
distinction is made. Imputation doctrine governs gaps in something measured. It
has nothing to say about a variable never collected, and the estate's problem is
overwhelmingly the second.

**Component I is the exception**, and the only one. Six of its nine metrics are
observed on ~620,000 records, `_I_from_metrics` renormalises over those present
— which COINr establishes is arithmetically mean imputation — and Box 4's
in-sample/out-of-sample test is therefore available for it and for nothing else.

## What changes

1. The recommendation of a **2/3 availability threshold with exclusion below it**
   is WITHDRAWN. It rested on the GII precedent read as though it were general,
   and the Handbook's case-deletion rule contradicts it at this level of
   missingness.
2. The `--coverage-threshold` parameter in `scripts/ssi_rebuild_component_I.py`
   remains a parameter and remains unpinned. Records below it are skipped and
   counted, which is a statement about what was rebuilt, not a publication rule.
   Nothing about the sub-threshold tails in france, spain, the uk, portugal or
   turkey is settled by this.
3. What does NOT change: no fill from a name hash, under any reading. The
   Handbook requires a reliability measure per imputed value and documentation
   of the procedure; `vary(0.35, name, 0.30)` has neither and no base.

Still not decided, and still the operator's: what a record with no components
publishes in the interim. The Handbook's answer is to impute and report the
uncertainty; it cannot be followed for C, V, E, S and T because there is nothing
to impute from; and the acquisition that would make it followable is the 866
declared sources with no route.
