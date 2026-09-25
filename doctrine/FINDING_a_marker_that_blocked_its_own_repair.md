# FINDING — an audit marker asserting work that did not happen, and blocking its own repair

**Measured** 21 September 2026 while closing the red sentinel
`test_migration_score_semantic_normalise`.

## What the sentinel said

Greece and Mexico carry `migration_score` outside the canonical `[0, 1]`
envelope — `[-4.500, 2.500]` and `[-5.000, 8.000]`. The test's own remedy:
*"Task #450 SYSTEMIC bridge utility should be re-applied to close these
instances."*

**Re-applying it would have done nothing, and would have reported success.**

## What is actually true

Every Greek record (719) and every Mexican record (3,085) **carries the
bridge's audit marker** `_migration_score_semantic_normalise_source =
TASK_450_MIN_MAX_LINEAR_RESCALE_v4_2`, and still holds the pre-bridge range.

The utility writes the rescaled score and the marker **in the same block**. It
cannot produce a marked, un-rescaled record. So the marker is genuine and the
value was **overwritten afterwards** by something that rewrote
`migration_score` while leaving its sibling marker intact.

## Why that was worse than a plain regression

The utility skipped on the marker alone, in two places — the min/max gather
and the write guard. So:

- Greece and Mexico reported **"no un-normalised migration_score to
  process"** while holding values five times outside the envelope.
- Denmark's population collapsed to a **single record**, which then looked
  degenerate (`min == max == 0.5`) and was skipped under Convention #56 for
  the wrong reason.
- **The repair was permanently blocked by its own audit trail.** The marker
  asserted the work; the assertion was trusted; the work was therefore never
  redone. A record could stay broken forever precisely because it had once
  been fixed.

This is Prohibition 5 in a new place. The estate has been finding absence that
reads as completeness in renderers, in gap engines and in change logs. Here it
is in a repair utility, and the failure is sharper: not a silence, but a
positive claim that the work was done.

## Fixed

Both the gather and the write guard now exclude a record only when it is
**marked AND inside the envelope**. A marker contradicted by the value is
evidence of a later overwrite, not of work already done — the reason to act,
not to skip.

With that correction, `--dry-run` reports what the utility should always have
reported:

    denmark      populated     1   write     0   degenerate (one unmarked record)
    ireland      populated     0   write     0   nothing outstanding
    new-zealand  populated     0   write     0   nothing outstanding
    greece       populated   531   write   531   [-4.500, 2.500] → [0, 1]
    mexico       populated 2,190   write 2,190   [-5.000, 8.000] → [0, 1]

Note that both countries are **mixed**: 531 of Greece's 719 and 2,190 of
Mexico's 3,085 are outstanding, the rest correctly normalised. A partial
overwrite, not a wholesale one.

## NOT resolved — what overwrites the value

**I have not found what rewrites `migration_score` after the bridge.** Nothing
in `scripts/` calls the utility, so it has never been part of the pipeline;
the 24 July 2026 run was manual and nothing re-applies it. Some enrichment
step writes `socio_economic.migration_score` by merge, preserving neighbouring
keys, and that step has not been identified.

### Two candidates eliminated, so the next search does not redo this

**Task #452 / NIVA (`_migration_score_source`) is not the overwriter — it is
the opposite.** Cross-tabulated across five countries, **every record carrying
the NIVA marker is inside the envelope**, without exception:

    greece   NIVA=False out-of-envelope 531 · NIVA=False in 25 · NIVA=True in 163
    mexico   NIVA=False out-of-envelope 2190 · NIVA=False in 895
    ireland  NIVA=False in 994 · NIVA=True in 284
    denmark  NIVA=False in 2433 · NIVA=True in 2389

Records touched by NIVA are clean. The damage is entirely among records it
never touched.

**`socio_economic_backfill.py` is not the overwriter either.** It carries an
explicit `DO_NOT_TOUCH_FIELDS` set naming `migration_score` and
`_migration_score_source`, and its merge is an explicit field-list assignment
— `gdp_per_capita`, `unemployment_rate`, `EP_rate_region`, `elderly_pct`,
`V_socio` — that never names the score. Read, not assumed.

That leaves `scripts/pipeline/ingestion/socioeconomic.py`, the ingestion
layer, which does write `migration_score` including a neutral 0.5 default.
But a re-ingestion that rebuilt the `socio_economic` block would have removed
the bridge marker too, and the marker is present on 100 % of records in both
countries. **So the mechanism is still not explained**, and the remaining
possibility worth testing is that the marker and the value were written by
DIFFERENT VERSIONS of the bridge — that the script which ran on 24 July 2026
marked records it did not transform, and was corrected later.

That was a question for the history, and the history answered it.

**The "two versions" hypothesis is dead.** The bridge has exactly two commits:
`d72d4eae`, the original Task #450, and today's guard correction. It was never
amended in between. So the script that ran on 24 July 2026 is the one now
read, it cannot mark without transforming, and the values **were** rescaled by
`da58a1e8` and reverted afterwards.

**The backfill is exonerated twice over.** `git log -S "DO_NOT_TOUCH_FIELDS"`
returns a single commit — `250e0e60`, the one that CREATED the utility — so
the protection was never added later in response to damage. Task #453 was also
scoped to LU/SI/LT/CO, which does not include either affected country.

### A guard that does not guard

Found while exonerating it, and worth its own line: **`DO_NOT_TOUCH_FIELDS` is
defined at `socio_economic_backfill.py:142` and referenced nowhere.** It is a
frozenset naming `migration_score`, `population` and their markers, declared
as a safety constraint and never consulted by any code path.

The behaviour is nonetheless correct — both write paths assign an explicit
field list that genuinely excludes the score — so nothing is broken today. But
the protection a reader would believe is enforced is not enforced, and the
next field added to either path will not be checked against it. I read that
constant an hour before reading the code and drew exactly the wrong conclusion
about why the file was safe.

Either wire it in or delete it. A named guard that only documents an intention
is worse than the explicit list it sits above, because the list is honest
about being manual.

### FOUND — it is this repository's own scheduled bot

`SSI Index/find_migration_revert.sh` bisected it. Observed range at each
commit that touched `greece/ssi-data.json`:

    da58a1e8  [0.000, 1.000]   Task #450 bridge — cohort apply        ← rescaled
    649df320  [0.000, 1.000]   Task #501+#454b+#454c cohort apply     ← EXONERATED
    4cb4227b  [0.000, 1.000]   Task #523+#525 v4.23 callout
    f7623ca6  [-4.500, 2.500]  pipeline: data enrichment run 2026-08-06  ← THE REVERSION
    6fa65088  [-4.500, 2.500]  monthly refresh Edition 025
    bdcaaa63  [-4.500, 2.500]  R7_cyber v2 cohort-wide first apply
    cb9d5cb4  [0.000, 1.000]   v4.24 realised                         ← restored
    bf3ec3e3  [-4.500, 2.500]  Revert "v4.24 realised"                ← undone again
    ...                        broken continuously to HEAD

**`f7623ca6` is `pipeline-enrichment.yml`.** Its commit is stamped
*2026-08-06 08:54 UTC*; 6 August 2026 was the **first Thursday of August**,
and that workflow runs every Thursday 06:00 UTC gated to day-of-month ≤ 7. Its
own commit message lists *"Socio-economic enrichment (national statistics)"*
among what it did.

So the overwriter is **this repository's own scheduled job**. It rewrites
`socio_economic.migration_score` from national statistics, leaves the sibling
markers alone — which is exactly the signature — and has done so every month
since. Task #501 and the polygon backfill are both exonerated: the values were
still `[0, 1]` when they ran.

The second event is a revert of a revert: v4.24 (`cb9d5cb4`) restored the
envelope as a side effect of its re-shard, and reverting v4.24 (`bf3ec3e3`)
took the restoration with it.

**Seven weeks, a monthly job silently undoing a manual repair, and nothing
noticed** — because the only thing watching was a sentinel nobody could run,
the suite having been OOM-killed at 16 %.

### Fixed by construction, not by memory

`pipeline-enrichment.yml` now runs the bridge after the pipeline and before
the gates and the commit, as a sibling of the existing post-ingestion
cross-border remediation. The utility is idempotent and — since today —
verifies the envelope rather than trusting its own marker, so it is safe to
run unconditionally: countries already inside report "already in [0, 1]".

**The order matters and it is tight.** The next scheduled run is
**1 October 2026**, nine days out. Repairing the data without the workflow
step would hold until then and no longer.

### A loop closed from this morning

`bf3ec3e3` is *Revert "v4.24 realised: M-006 soft_clip correction, R7_cyber v2
cutover, re-shard"*. The bisect confirms v4.24 was applied cohort-wide and
then reverted wholesale.

That answers a question left open in
`FINDING_r7_cyber_v2_actual_state.md`, which measured that 99.6 % of records
carry `_r7_cyber_v1_retired == False` while `CLAUDE.md` recorded the cutover as
done on 18 August. Both were true. **The cutover ran and was reverted**, and
the note recording it was never reverted with it. That is not the same defect
as a cutover that never happened, and the distinction should be carried into
that document.

### Where the hunt stood before it was found

The next data commit after the bridge is `649df320` — *"Task #501+#454b+#454c
cohort apply GREEN — 472,503 v43 subs enriched"*. #454b/#454c live in the
exonerated backfill. **Task #501 has no implementation anywhere in
`scripts/`**, so what that commit ran on 472,503 substations cannot be read
from the working tree.

`SSI Index/find_migration_revert.sh` bisects it: read-only `git show` at every
commit that touched `greece/ssi-data.json` since the bridge, printing the
observed range at each. The reversion will land on one commit rather than a
suspicion.

**This matters more than the repair.** Running the utility now restores the
invariant for 2,721 records, and if the overwriting step runs again it will
break them again. The sentinel will catch it, which is the system working —
but a repair applied outside the pipeline, against a corruption that happens
inside it, is a treadmill.

The durable fix is one of: identify and correct the overwriting step; or wire
the bridge into the pipeline after it, so the invariant is restored by
construction rather than by memory.

## Recommended sequence

1. Land the guard correction. Done in this change — it is a code fix and
   changes no published value.
2. Run the repair. It writes 2,721 records in two countries and is the
   operator's to execute, as every state change here is.
3. **Then** hunt the overwriting step, before assuming the repair holds.
