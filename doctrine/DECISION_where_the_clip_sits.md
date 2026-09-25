# DECISION REQUIRED — does the additive tail sit inside or outside the clip?

**Date** 21 September 2026
**Status** ANSWERED 21 September 2026, and SEQUENCED. The operator delegated
the decision. The answer is move it inside — **after M-006, not before** — and
the reason that qualifier exists is measured below. Nothing changed in the
equation, deliberately.
**Why it was open** it would supersede a standing operator pin, and it
cascades to 117 published files. See the ANSWER at the foot of this document;
everything between here and there is the reasoning as it stood before the
cost was measured, and §"What it costs today" in the answer supersedes the
figures in "What it costs" below.

---

## The two forms

    TODAY      R = soft_clip_upper( R_base × Π mult ) + Σ ( add − 1 )
    PROPOSED   R = soft_clip_upper( R_base × Π mult   +   Σ ( add − 1 ) )

## The case for today's form — your own pin

`master_equation.pin`, decided 8 June 2026:

> "The additive tail sits outside the soft clip so that flood exposure can push
> a score past the multiplicative ceiling, which is the behaviour the additive
> family was introduced to express."

That is deliberate and reasoned. Flood was made additive *and* put outside the
clip precisely so saturation could not absorb it.

## The case for moving it inside

Stated 21 September 2026: the normaliser exists "to cushion possible blows by
maintaining all substations within a relative range — absolute computation then
brought to relative terms". Under that intent, a term outside the clip is a term
outside the cushion.

Today that costs little, because one modifier is additive. If the five deferred
hazards ever move — and on the methodology they should, once their inputs are
real — then five more hazards sit outside the cushion and the compression
applies only to the capacity chain. The additive tail stops being a flood
exception and becomes the main hazard channel.

It also matches the operational precedent. The 2024 global multi-hazard risk
assessment aggregates as `S = Σ_k min(E_k, Σ_h I_{h,k})` — **the cap is on the
sum**, not on one term beside it. With the caveat that their cap is at exposure
value, a genuinely extensive quantity, while R is a normalised score, so the
analogy is suggestive rather than binding.

## What it costs today

Measured on the 223,966 attributable records, with the five hazards moved:

    clip outside (today)     115,578 band changes
    clip inside (proposed)   116,961 band changes
    the two forms differ on    1,763 records — 0.8 per cent

**With only flood additive, the difference is smaller still.** This is the
cheapest moment this decision will ever have: settling it now costs almost
nothing and it is already right whenever the additive channel grows.

## What it cascades to

The master equation is published in **117 files** — `methodology.html`,
`data.html` and `ssi-metadata.js` across all 39 countries — and appears in the
rendered foundation documents and the paper programme. Changing it is a
data-and-information change rather than a design change under Pin 1, but it is a
published methodological claim and every surface carrying it must be re-rendered
and proven render-identical in structure.

## The question

Do you supersede the 8 June pin?

- **Keep it outside** — flood retains the exemption it was given, and the
  deferred hazards inherit that exemption if they ever move. Coherent, and it
  means the cushion governs capacities only.
- **Move it inside** — the cushion governs everything, matching the stated
  intent and the precedent, and flood loses the specific property the 8 June pin
  gave it on purpose.

I recommend moving it inside, on the stated cushioning intent and because the
cost of deciding rises with every hazard that later becomes additive. But it
reverses a reasoned decision of yours, on a published equation, so it is not
mine to take.


---

# ANSWER — 21 September 2026

The operator delegated this ("solve for 18"). The recommendation above stands
in principle and **was incomplete**, because it did not account for what the
tail would be moved *into*.

## What it costs TODAY, which the section above never measured

The 115,578 figure above is the counterfactual with five hazards moved. With
only flood additive, measured across all 39 jurisdictions:

    records carrying an additive term            619,002
    R_final would change on                        5,019   0.811 %
    PUBLISHED BAND would change on                 3,132   0.504 % of the estate
    largest change in R_final                     0.731006

## And that largest change is not a number, it is a cliff

`soft_clip_upper` is discontinuous at 1.0 — defect **M-006**, documented in
`engine.py:133-142` and unrepaired:

    soft_clip_upper(0.9999) = 0.999900
    soft_clip_upper(1.0000) = 1.000000
    soft_clip_upper(1.0001) = 0.269335

The drop across that step is **0.7307**. The largest change the move produces
is **0.731006**. They are the same event.

Decomposing the 5,019:

    pushed ACROSS the 1.0 discontinuity by the move    1,419
    changed smoothly                                   3,600

    the 1,419 DROP by:  max 0.7310 · median 0.6356 · min 0.2472

**Moving the additive tail inside the clip today would take 1,419 substations
and cut their resilience scores by about two thirds — not because anything
about their risk changed, but because they crossed a known defect.** The
argument for moving it was that the cushion should govern everything. Today
the cushion has a cliff in it, and the move walks 1,419 assets off it.

## The answer

**Move it inside. After M-006 is repaired. Not before.**

That is a decision, not a deferral: the direction is settled, the precondition
is named, and the order is fixed. It also costs nothing to hold, because the
case for moving grows with each hazard that becomes additive and none have
moved yet.

This is consistent with what the estate already decided elsewhere and I had
not connected. `SEQUENCE_change_order.md` records that a recomputation of R is
its own decision and that **"M-006 step 5 is still blocked"** stands against
one, alongside `components.I` being a name hash on 456,184 records. Moving the
clip REQUIRES a recomputation. It is blocked by the same two conditions, and
this decision does not get to jump that queue.

## A note on the 8 June pin

It is superseded in principle and not yet in fact. The 8 June reasoning —
flood outside the clip so saturation cannot absorb it — was correct for the
regime it was written in, where the additive family was one modifier. What
changes it is the stated cushioning intent plus the prospect of five more
hazards joining. Neither has arrived, so nothing is restated today.

## What would close this

1. M-006 repaired, and re-scoped first per
   `DECISION_I3_normalisation_method_C.md` §3 — `soft_clip_upper` has two call
   sites the `clip_continuity` invariant does not watch,
   `ssi_derive_metrics_I4_I6.py:150` (54,377 records) and
   `ssi_derive_component_T.py:141` (unquantified).
2. `components.I` derived from real metrics rather than a hash.
3. Then the equation amended, the estate re-scored, and the 117 published
   surfaces re-rendered in one change.
