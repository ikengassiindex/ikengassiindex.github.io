# PLAN — completing the R7_cyber v1 → v2 substitution

**Date** 17 September 2026
**Status** plan. Nothing has been changed.
**Authority** operator design intent 22 August 2026 — *v2 SUBSTITUTES v1, never a
dual-write*; operator decision 17 September 2026 to build, test and release.
**Sequence** `SEQUENCE_change_order.md` (Pin 16): decide → acquire → measure →
pin → derive → propagate → project → measure the result → land.
**Evidence this plan rests on** `FINDING_r7_cyber_v2_actual_state.md`,
`FINDING_mult_product_is_three_populations.md`,
`RESULT_what_completing_the_R7_cutover_costs.md`,
`RESULT_the_three_R7_cutover_residuals.md`,
`FINDING_the_name_hash_reaches_past_components.md`.

---

## What the change is, stated once

v1 (`modifiers.R7_cyber`) is `vary(1.02, name, 0.015)` — an MD5 hash of the
substation's name — on 88.9% of records carrying it. v2
(`modifiers.R7_cyber_v2`) is anchored on NIS2 Article 21. Pin 14 requires a
coefficient verified against a primary or secondary source. **A coarse regime
constant with a citation replaces a fabricated per-asset number.** That is the
whole justification, and it does not depend on v2 being granular.

It is NOT a new scoring implementation. `modifier_registry.py` has already cut
over; `r7_cyber_v2.py` and `session_m_r7_v2_cohort_apply.py` have not. The change
is to make them agree, declare what v2 does not do, derive, and measure.

## What is deliberately NOT in this change

- **Granularity.** Raising v2 from national to per-asset is an acquisition task
  on `owner` (16.9%) and `operator` (9.8%), not a modelling task, and it is a
  separate workstream. This change declares the shortfall; it does not close it.
- **The name hash elsewhere.** `R4_F_topo`, `R6_restoration`, `R6_seismic`,
  `E2_local` and the whole `graph_topology` block are the same generator. Out of
  scope here, and gated behind a full Pin 14 sweep that has not been run.
- **Component I rebuild.** Already held behind this cutover.
- **The public site's design.** Pin 1. Untouched.

## Steps

### 1 — Reconcile the code with itself  *(pin)*

Two files state opposite policies. Per the 22 August directive, the dual-write
one yields.

- `scripts/pipeline/scoring/r7_cyber_v2.py` — the module docstring's dual-write
  framing and the `V1_RETIRED_KEY` initialised `False` at first apply.
- `scripts/session_m_r7_v2_cohort_apply.py` — same value, same stated reason.
- `scripts/pipeline/scoring/modifier_registry.py` — already correct; do not touch
  beyond confirming it.

Retire-with-comment discipline per Convention #56: the superseded policy is
commented out with its date and authority, not deleted.

### 2 — Add the invariant that can actually see the cutover  *(pin)*

`TestPostCutoverInvariants` reads `versions.json`, `edition-config.json`, the
registry and the shard thresholds. Not one assertion reads a substation record,
which is why the suite is GREEN today while the cutover has not happened.

Add a data-layer sentinel that reads the published artefact and asserts, over the
deployed tree:

- `_r7_cyber_v1_retired` is `True` on every record carrying the marker;
- no record has `modifiers.R7_cyber` contributing to the published chain;
- `mult_product` reproduces from the published modifier set with v2 in and v1
  out, or the record is one of the declared exceptions in step 3.

**This sentinel must FAIL before step 4 and PASS after it.** A sentinel that
passes both sides of a change has not tested the change. Run it and watch it fail
first — that is the acceptance criterion for the sentinel itself.

### 3 — Pin the declarations in `SSI_FOUNDATION_judgement.yaml`  *(pin)*

Three things get declared before any derivation runs, not after:

- **The product layer is absent.** `w_product = 0.45` of the designed construct
  resolves to nothing on all 619,522 records. Declared on the I4 abstention
  pattern so the conformance check reads it, with the Convention #7 statements
  the construct needs. This is what makes the later granularity work a *declared
  swap completing* rather than a second unannounced restatement of published
  scores.
- **The 78,558 records carrying v2 with no v1.** They are not a substitution;
  there is nothing beneath them. State the treatment explicitly rather than
  letting them fall through the swap.
- **v1's retirement and its reason** — the Pin 14 failure, cited to
  `FINDING_the_name_hash_reaches_past_components.md`, so the retirement's basis
  is on the record and not only in a commit message.

Change-log entry and `to_version` restamp per Bible §8.

### 4 — Derive  *(derive → propagate)*

- One country first. Read the result before looping 39 — Pin 16, and it has
  caught a defect at least twice.
- Then cohort-wide.
- Pin 13: not in a bot window. `pipeline-enrichment.yml` 1st Thursday 06:00 UTC,
  `monthly-refresh.yml` 2nd Thursday 10:00 UTC, `esg-refresh.yml` 2nd Thursday
  11:00 UTC.
- Pin 5: this change lands before anything else starts.

### 5 — Measure the result  *(measure the result)*

Predicted from `RESULT_what_completing_the_R7_cutover_costs.md`: 31,726 band
changes (5.1%), 17,699 worse / 14,027 better, Critical +12.2%. **Measure against
that prediction and report the difference**, rather than re-citing the prediction
as the outcome.

Also measure, because it is the open question the cutover may or may not close:
does `mult_product` reproduce from the published chain afterwards? It currently
does not on 31.5% of the estate (france, germany, italy, japan, us). If the
cutover does not close that, say so plainly — it is a separate defect and must
not be quietly absorbed.

### 6 — Land  *(land)*

Master documents before the site repo. Operator runs every `git add`, `commit`
and `push`; explicit paths, no `-u` sweep. The public site and any R
recomputation are consequences needing their own operator decision, never
automatic.

## Test execution — decide before step 2

`pytest` is not installed in the Cowork device VM. Either the operator runs the
suite on his Mac, or the tests and `scripts/pipeline/` are staged into the cloud
container and run there. Pick one now, so "tests pass" is a fact rather than a
claim.

## What would stop this plan

- The data-layer sentinel in step 2 passing before the change. That would mean it
  does not test what it claims to, and step 4 must not run until it does.
- The one-country derivation in step 4 producing a band-change rate materially
  off the predicted 5.1%. Stop and diagnose rather than continuing to 39.
- Discovery that the 78,558 no-v1 records are not a clean population. They have
  not been characterised beyond their count.
