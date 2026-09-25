# PLAN — closing the 31 blocking gaps, then rendering once

**Date** 21 September 2026. **Status** plan for signature; nothing changed yet.
**Operator direction:** *"we must solve any gaps, what practical course of
action should we take?"*

That direction supersedes the recommendation in
`FINDING_the_render_debt.md` §3, which was to render and let the gaps print.
Printing them is honest but it is the cheaper option, and it leaves 31 gaps
standing in 43 packages. Closing them first and rendering once is better, **and
it also dissolves the Pin 16 / §8.5 conflict** rather than choosing a side:
close the gaps, land the pending amendments, then render ONCE and LAST. §8.5's
substance is discharged by that single closing render; Pin 16 is honoured
literally.

## What the gate actually asks

`render2.py` was changed **18 September 05:17** to stop printing a missing pin
or tier as "–" beside a passing mark. Its own comment: *"an amendment enacted by
nobody, on no date, on no stated evidence rendered green. That is Prohibition 5
— absence that reads as completeness — committed by the enforcement layer."*

Per change-log entry it requires three things: the element in the registry,
`decided_on` (§8.2 provenance pin), and `tier` (§8.3 evidence tier).

**The tier scale, and the line that shrinks this problem:**

    E0  the index's own peer-reviewed publication
    E1  definitional — fixed by a standard outside this estate
    E2  empirical — supported by published research, load-bearing
    E3  operator judgement — a human chose it, no literature determines it

and `render2.py:378` — **"Undeclared is a defect, E3 is not."** The gate is not
demanding research. It is demanding that someone say which *kind* of evidence
stands behind each decision. **E3 is an available, honest answer**, and for
several of these it is the correct one.

## The triage — 31 gaps, four buckets, three owners

### Bucket A — 21 gaps: doctrine declared MUST and never written. OPERATOR.

Four sections are declared MUST in `SSI_FOUNDATION_taxonomy.yaml`, **absent
entirely from `SSI_FOUNDATION_judgement.yaml`**, and three of the four are
absent from the renderer too:

    slot_commercial_axes    10 fields   taxonomy ✓  judgement ✗  renderer ✗
    slot_esg_reports         5 fields   taxonomy ✓  judgement ✗  renderer ✗
    e2_beta_decomposition    4 fields   taxonomy ✓  judgement ✗  renderer ✓
    slot_market_coupling     2 fields   taxonomy ✓  judgement ✗  renderer ✗

These are not a rendering omission. They are doctrine that was declared
required and never authored. **Two ways to close each, and they say different
things:**

1. **Declare them specified-but-not-populated.** The estate already has this
   idiom — `specified_not_populated` is a real citekey at
   `SSI_FOUNDATION_evidence.yaml:348`, rendered elsewhere as
   `E3 specified_not_populated`. This converts silence into a declared absence,
   which is what §7.5 asks for, **without inventing content the estate does not
   have.**
2. **Demote them in the taxonomy from MUST.** If commercial axes and ESG report
   slots were declared mandatory aspirationally, then the declaration was the
   error and correcting it is the honest fix — not manufacturing ten commercial
   axes so a gate goes quiet.

**Recommendation: (1) for all four, now; (2) considered separately and at
leisure.** (1) closes the gaps today and asserts nothing false. (2) is a real
question about what the taxonomy should require, and it should not be decided
under time pressure from a renderer.

Work implied: judgement entries declaring the four sections, plus emit paths in
`render2.py` for the three it does not know about. **Tooling is mine; the
declaration is the operator's.**

### Bucket B — 6 gaps: a tier, and nothing else. OPERATOR SIGNATURE, PREPARED BY ME.

Six entries carry a valid `decided_on` and no `tier`. Every one of them records
work that was actually done; only the evidence *kind* is unstated. **Proposed
tiers below are proposals for signature, with the reason — not decisions:**

| entry | pinned | proposed | because |
|:--|:--|:--|:--|
| `I5` | 2026-09-17 | **E1** | the quantity is IEEE C57.91's ageing acceleration factor — a standard outside this estate |
| `I4` | 2026-09-17 | **E1** | both floors moved on the TSOs' own published definitions (Terna's "150-132-120 kV" tier; CENACE's "iguales o mayores a 69 kV"). *Mixed:* the Definition-A choice rests on a variance decomposition, which is E2 |
| `I6` | 2026-09-17 | **E3** | self-referential count of the estate's own register; no literature determines the 3×3 block or the inversion |
| `I3` | 2026-09-17 | **E3** | corrects a declaration to match Construct §03's own normalisation definition — internal, not an outside standard |
| `I2` | 2026-09-12 | **E3** | same correction as I1, same basis |
| `I1` | 2026-09-12 | **E3** | bounded_interval corrected to match Construct §03; an estate definition, not an external one |

Four of six are **E3**, and that is not a weakness — it is the accurate label
for a choice the estate made and can defend.

### Bucket C — 3 gaps: no pin, no tier, one not in the registry. ONE OF THEM IS MINE.

    R7_cyber                            no pin, no tier
    R7_cyber_v2                         no pin, no tier
    modifier composition (add vs mult)  not in registry, no pin, no tier

**The third is mine, written this morning in COMMIT_L.** I added a change-log
entry without a provenance pin, without an evidence tier, and under a prose
label that is not a registry element — the same §8 omission the 18 September
gate was built to catch, committed four days after it was built. Owned here
rather than left in the pile.

Its proper form is **not one entry**. The composition pin touched several real
elements — `R6_seismic`, `R9_compound`, the five deferred hazards,
`R6_drought` — so it should be one entry per element, each naming a registry
id, each pinned `2026-09-21`, each tiered. Proposed: **E2** where the
composition follows published form (R6_seismic on Hazus conditional fragility),
**E3** where it is a deferral the estate chose.

R7_cyber and R7_cyber_v2 pin to **2026-09-17** and propose **E1** — CRA
Article 14 and NIS2 Article 21 are standards outside the estate.

### Bucket D — 1 gap: `derived_composites / E2_beta.formula — not declared`.

Not yet diagnosed. `e2_beta_decomposition` is the one Bucket-A section the
renderer does know about, so this is likely the same root cause seen from the
other side. **To be looked at before the plan is executed, not assumed.**

## Sequence

1. **Operator signs Bucket B** (six tiers) and **Bucket C** (three entries,
   split per element, pinned and tiered). Cheap — it is six-plus-a-few
   one-word judgements, and E3 is available.
2. **I diagnose Bucket D** and fold it in.
3. **Operator decides Bucket A**: declare specified-not-populated (recommended),
   or demote in the taxonomy.
4. **I implement**: judgement entries, registry entries, and the three missing
   renderer emit paths. Landed as one change under Pin 5.
5. **The band-rule amendment lands in the same series** — the operator's
   decision of 21 September is to publish both an absolute band and a
   within-country rank, distinctly named, which is itself a judgement.yaml
   amendment. Batching it here is what makes the single render legitimate.
6. **Render ONCE and LAST**, 43 packages plus MASTER, and re-run the gap count.
   The target is zero blocking gaps, and any that remain are named, not
   absorbed.

Nothing in steps 4–6 starts before 1 and 3. The gaps are doctrine, and doctrine
is signed before it is rendered.

## The BIBLE is not in this plan

`SSI_FOUNDATION_BIBLE.md` is hand-authored — no `.py` file in either tree
contains the string "BIBLE". It cannot be rendered and will not be touched by
step 6. Its month of staleness is an authoring debt on a separately authored
constitution, and it is the flag officer's alone.
