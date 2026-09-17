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
- `scripts/pipeline/scoring/modifier_registry.py` — the retired-skip guard is
  correct and stays. **One comment in it is not:** it states that "Sweden's
  published scores carry that double-count today". Zero Sweden records fit the
  both-hypothesis, and Sweden's published product ÷ chain(v2) is 1.000001
  (sd 0.000023). The claim is corrected in this step, in the same change —
  a present-tense assertion about published data, written into production code,
  that the published data contradicts. See `RESULT_the_r7_data_sentinel.md`.

Retire-with-comment discipline per Convention #56: the superseded policy is
commented out with its date and authority, not deleted.

**DONE, 17 September 2026.** Four files.

- `r7_cyber_v2.py` — dual-write text replaced throughout; the marker write now
  snapshots v1, removes `modifiers["R7_cyber"]`, and sets
  `_r7_cyber_v1_retired` True. Also recorded there: the module carried a
  tombstone date of "~Q1 2027", which GATE-A-11-REVISED had already moved to
  Session M+1.
- **The policy was extracted to one function**, `substitute_v1_with_v2`, and both
  call sites now use it. It had been written out twice, in two files — which is
  precisely how this module and the registry came to state opposite policies for
  a month with nothing noticing. Duplication was the root cause, not an
  incidental detail, so removing it is part of the fix rather than tidying.
- `session_m_r7_v2_cohort_apply.py` — inlined copy removed, calls the function.
- `modifier_registry.py` — the Sweden double-count claim corrected against the
  artefact. The guard itself is untouched.

**And the reason step 1 was not finished when the code was right.** After the
policy was reversed — `False` → `True`, and the modifier removed — the suite
still reported **95 passed**. Every existing test covered the pure compute path
or the registry constants; nothing covered the write path where the policy lives.
A reversal of the module's central behaviour was invisible to its own sentinel.
That is the second instance in one day of `DOCTRINE_a_check_must_read_the_artefact.md`,
the first being `TestPostCutoverInvariants`.

`TestSubstitutionSemantics` (9 tests) now pins it, and was verified the only way
worth anything: the superseded behaviour was restored in a scratch copy and the
suite run again. **4 failed, 100 passed.** Restored, **104 passed**. A test that
has not been seen to fail is not evidence.

`TestDualWriteSemantics` renamed `TestComputePathIsPure` — what it asserts is
still true and still wanted, but a test named for the superseded policy reads as
a pin on it.

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

**DONE, 17 September 2026** — `scripts/check_r7_cutover_complete.py`. Red on all
three conditions, as required. Its first run changed steps 4 and 5; see
`RESULT_the_r7_data_sentinel.md`. Two carry-overs from that run:

- **Condition C must be SPLIT before it gates a release.** It currently conflates
  "the chain uses v2" with "the published product reproduces at all". Those are
  different failures and only the first belongs to this change.
- The sentinel does not cover the front end (step 4b). Nothing automated does.

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

**DONE, 17 September 2026.** `SSI_FOUNDATION_judgement.yaml`, five edits plus two
change-log entries. `to_version` needed no restamp — it already reads
`judgement pin 2026-09-17`.

**The doctrine was ahead of the code, which is the reverse of the usual.** The
entry already carried `substitutes: R7_cyber`, `interaction: Mutually exclusive
… Both reaching the published product on one asset is a double count`, and a
`limitations` field stating plainly that the guard was not deployed and published
scores still reflected the superseded modifier. The 21 August rebuild was honest
about a gap the code then took a month to close. What needed correcting was
narrower than planned:

- **v1's retirement basis.** It read "no verifiable provenance". That understates
  it: an unverified coefficient might still measure something, and a name hash
  does not. Restated with the measurement and cited to the finding.
- **"Wherever that is so"** — the product layer's absence was declared
  conditionally. It is unconditional: 619,522 of 619,522.
- **The 30 distinct values** are now declared on the entry, so the national
  granularity is doctrine rather than an unrecorded property of the output.
- **The 78,558 no-v1 records** are declared, with the reason the retirement
  marker is still set on them.

**A regression I introduced and caught before landing.** I first wrote v1's
explanation into `source:`. `render2.py` treats a truthy `source` as a CITATION —
it would have printed that prose in the Source row, and dropped R7_cyber from
both the blocked-source table and the conformance gap. The file's own words:
"A citation that was never read is worse than an admitted gap." `source` is back
to `null` and the substance sits in `blocked_on`, which is the field the renderer
prints in the blocked table. Verified after the fix: 30 elements carry a blocked
source and R7_cyber is among them.

**Not rendered.** Pin 16 puts *project* after *derive*, and render once and last.
The documents therefore lag the YAML until step 4 runs. Deliberate, and stated
here so it is not mistaken for an omission.

### 4 — Derive  *(derive → propagate)*

**Revised 17 September 2026 by the sentinel's first run.** Five countries —
france, germany, us, italy, japan — hold 398,599 records, **64.1% of the
estate**, and on **397,852** of them the published `mult_product` reproduces from
the record's own modifiers under NO cyber hypothesis. The ratio of published to recomputed runs at a median 1.0085–1.1004
with a standard deviation near 0.047: a distribution, not a scalar. Their
published product predates their current modifier values.

**So the cutover cannot be applied to those five countries as a delta.** There is
no reproducible baseline to apply a delta to. They need the Phase ζ rescore
(39-country Monte Carlo, ~4–6 h) — which was already a deferred
operator-execution phase, and is now on this change's critical path rather than
beside it.

The other 34 countries (223,505 records) reproduce and can take the delta, bar 57
scattered records the sentinel also reports as non-reproducing.
Splitting the cohort that way is a decision, not a workaround, and it gets stated
in the judgement file at step 3.

**REVISED AGAIN, 17 September 2026, by the step-4 dry run. THE SUBSTITUTION MUST
NOT RESCORE.** `scripts/r7_substitute_and_rescore.py` exists and its dry run did
its job: on 300 Sweden records it changed `mult_product` on zero of them — the
retired-skip guard already excluded v1, so removing the field is arithmetically
inert — while bands appeared to move anyway. The control (rescore twice, no
substitution) found the Monte Carlo is unseeded:
`engine.py:707` calls it without a seed and the docstring at 560 says
`None = non-deterministic`. See `FINDING_the_monte_carlo_is_unseeded.md`,
which also records that my first measurement of the effect was wrong by an order
of magnitude and why.

So step 4 becomes a DELTA, not a rescore:

- Where `mult_product` does not change, write nothing. Rescoring injects noise
  for no benefit. On Sweden that is every record.
- Where it changes, propagate arithmetically. `soft_clip_upper` is the identity
  at or below 1.0 on 99.4 per cent of records, so the shift is exact there and
  first-order in the compressed remainder.
- The five non-reproducing countries still cannot take a delta against a baseline
  that does not reproduce. They are the one population that needs recomputation,
  and that decision now carries the seeding question with it.

`scripts/r7_substitute_and_rescore.py` is therefore SUPERSEDED BEFORE FIRST USE
in its rescoring form. It stays on disk, dry-run by default, as the instrument
that found this; it is not to be run with `--write`.

- One country first, from the reproducing 34. Read the result before looping —
  Pin 16, and it has now caught a defect three times.
- Then cohort-wide.
- Pin 13: not in a bot window. `pipeline-enrichment.yml` 1st Thursday 06:00 UTC,
  `monthly-refresh.yml` 2nd Thursday 10:00 UTC, `esg-refresh.yml` 2nd Thursday
  11:00 UTC.
- Pin 5: this change lands before anything else starts.

### 4b — The front end reads v1 by name  *(propagate)*

Found while scoping step 2, and it is not optional — the cutover has a
presentation cascade:

- `map.js:820` — `const R7 = ssi.modifiers.R7_cyber;`
- `map.js:975` — `['R7 Cyber-Exposure', ssi.modifiers.R7_cyber]` in the popup
  modifier table
- `country-renderer.js:159` — `R7: 'R7_cyber'` in the key map
- `country-renderer.js:502, 526` — reads and a median comparison on the same field

Leave `modifiers.R7_cyber` in the payload and a reader sees the RETIRED value
labelled "R7 Cyber-Exposure" while the score behind it comes from v2. Remove it
and the same cards render undefined. Neither is acceptable, so the front end must
read `R7_cyber_v2`.

**This is a data-feed change, not a design change** — Pin 1 as the operator
clarified it on 2026-09-03: the field a card reads is data; the card is design.
Same cards, same positions, same labels. It must still be proven render-identical
before it ships, per Bible §7 ("enforced in code, not requested in review"), and
it is named here rather than discovered mid-build.

Whether the displayed LABEL changes from "R7 Cyber-Exposure" is a separate
operator decision, not a developer one.

### 5 — Measure the result  *(measure the result)*

Predicted from `RESULT_what_completing_the_R7_cutover_costs.md`: 31,726 band
changes (5.1%), 17,699 worse / 14,027 better, Critical +12.2%. **Measure against
that prediction and report the difference**, rather than re-citing the prediction
as the outcome.

**Caveat that must travel with that prediction.** It was computed before the
stale-baseline finding. For the five non-reproducing countries a band change
measured against a baseline that does not reproduce is not a measurement of this
change — it is the two effects summed. Report the 34 reproducing countries and
the 5 rescored countries **separately**, and never quote a single cohort-wide
band-change figure that mixes them.

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

## What would stop this plan

- The data-layer sentinel in step 2 passing before the change. That would mean it
  does not test what it claims to, and step 4 must not run until it does.
- The one-country derivation in step 4 producing a band-change rate materially
  off the predicted 5.1%. Stop and diagnose rather than continuing to 39.
- Discovery that the 78,558 no-v1 records are not a clean population. They have
  not been characterised beyond their count.

## Flagged in passing, NOT part of this change

`map.js:1385` guards a branch that, when a country's `substations` array holds
arrays rather than objects, expands each row into a full record with values
generated from sine functions of the row index — `R7_cyber`, `unemployment_rate`,
`gdp_per_capita`, `V_socio`, `E2_local`, `DER_ratio`, `seismic.zone`,
`seismic.pga_g`, `markov.risk_score`, `markov.ettc_years`,
`markov.corrosion_class` — plus a hardcoded
`graph_topology: {degree: 2, betweenness_centrality: 0.5, is_bridge: 0}`.

Measured: all 622,104 published records are objects, not arrays, so the branch is
unreachable on today's data. It is live code, in the served page, that would
fabricate silently if any country were ever published in compact form. Recorded
here so it is not re-discovered; it belongs to the Pin 14 sweep, not to R7.

## Test execution — RESOLVED 17 September 2026

Both environments work; the question is settled by measurement, not preference.

- **Cloud container.** 15 files staged (the test, `conftest.py`, `pytest.ini`,
  `versions.json`, `intelligence/edition-config.json`, `intelligence/countries.json`,
  and the `scripts.pipeline.scoring` / `.utils` modules — all stdlib imports).
  `95 passed in 0.28s`. No path or import problems.
- **Device VM.** `pip3 install pytest --break-system-packages` succeeds; pytest
  9.1.1 available.

Use the container for the code-level suite (fast iteration) and the device VM for
any check that must read the 2.1 GB of deployed records, which the container does
not have.

**Note:** the suite is 95 tests, not the 91 `CLAUDE.md` records. Minor staleness,
recorded not corrected — the count is not load-bearing.

**And the point that matters:** those 95 tests pass right now, today, with the
cutover not done. Confirmed by execution, not inferred. The suite cannot see the
defect, which is why step 2 exists.
