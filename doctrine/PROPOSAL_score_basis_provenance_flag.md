# PROPOSAL — `_score_basis`, a per-record declaration of what a score rests on

**Date** 20 September 2026
**Status** PROPOSAL. Not pinned, not derived. Requires an operator decision
before anything is written.
**Measured on** all 622,104 records, every shard.

---

## The problem it addresses, in one sentence

The index publishes a classification for every substation with identical
authority, whether it rests on six metrics derived from primary sources or on an
MD5 of the substation's own name — and the only way a reader can tell which is
to reproduce the hash.

`FINDING_R_base_is_hash_or_zero.md` establishes that `R_base` is a name hash on
77.5 per cent of records and exactly zero on 12.6 per cent.
`FINDING_the_name_hash_reaches_past_components.md` establishes the same for
R4_F_topo, R6_restoration, R7_cyber and the graph_topology block. None of the
remediations in the queue changes that for most of the estate, and the
acquisition programme that would is measured in months.

**This proposal does not fix anything. It makes the state legible.** That is
Convention #56 — visibly-honest degradation — applied at the record level, where
the honesty is currently only available to someone who re-derives the generator.

## Why it is the cheapest item in the queue

**It restates nothing.** It changes no component, no modifier, no `R_base`, no
`R_median`, no band. It is an additive derived field. Every other change in the
queue — seeding, `R_base`, the R7 cutover — moves published scores and needs a
restatement. This one does not, so it can land on its own, immediately, without
waiting for or entangling with them.

## The field

One string per record, following the pattern `_metrics_source` already sets
(present on 99.6 per cent of records, naming its authority).

    "_score_basis": "synthetic/6m"

Two parts. The first says what `components` — and therefore `R_base` — is made
of. The second says how many of the six I-metrics the record actually carries,
because that is the positive signal and it is the thing the estate has been
building all year.

    value        meaning                                           records      %
    synthetic    all six components reproduce from md5(name)       481,840   77.5
    absent       components {} — R_base is exactly 0                78,558   12.6
    unverified   components present, not from that generator        61,233    9.8
    mixed        some components reproduce, some do not                473    0.1

    metrics carried    6 metrics   511,162   82.2%
                       5 metrics   108,967   17.5%
                       2-4 metrics   1,975    0.3%

What the field would actually say, most common first:

    synthetic/6m   400,360   64.4%     fabricated components, six real metrics
    synthetic/5m    79,516   12.8%
    absent/6m       71,204   11.4%     no components, six real metrics
    unverified/6m   39,145    6.3%
    unverified/5m   22,082    3.5%
    absent/5m        7,349    1.2%

The first line is the estate's condition in one token: **the majority of records
hold fabricated components and six genuinely derived metrics at the same time.**

## Cost

30 bytes per record as JSON. 18.7 MB across the estate; at ~3.4 KB per record
that is **+0.9 per cent**, taking poland's largest shard from 66.3 to 66.9 MB.

Those files are already over Convention #79's 60 MB threshold — see
`FINDING_the_shard_threshold_is_already_breached.md`. The marginal cost here is
small and should be stated rather than used as a reason to withhold provenance.

## Decisions required before this is pinned

1. **Does the front end display it?** A field nobody surfaces is an audit trail,
   which has value on its own. A field the country page shows is a disclosure,
   which is a different act with a different audience. Data-feed change either
   way under Pin 1, but the second is an operator call, not a developer one.
2. **The token vocabulary.** "synthetic" is accurate and blunt. Alternatives
   exist that are accurate and less blunt. The word chosen is a judgement about
   how the index describes itself and belongs to the flag officer.
3. ~~**Scope.**~~ **RESOLVED 20 September 2026 — the Pin 14 sweep has run.**
   See `FINDING_pin14_sweep_complete.md`. The generator's writes were enumerated
   by AST from the generator itself and every one tested bit-for-bit, so
   `synthetic` can now be defined over a verified set rather than over whatever
   happened to be checked.

   The sweep also widens what the flag should carry. Two fields nobody had
   looked at are the estate's uncertainty apparatus:

       CI_width         vary(0.22, name, 0.15)   398,603   64.1%
       confidence_tier  the literal "medium"     493,076   90.7%

   A record whose interval width and confidence tier are both a function of its
   own name is making a claim about its reliability that it cannot support.
   That is precisely what this field exists to expose, so the proposed token
   should cover the uncertainty apparatus as well as `components` — a second
   part, or a wider vocabulary. Proposed for the operator rather than chosen
   here.

## What this is not

- Not a fix. `R_base` remains a hash on 77.5 per cent of records afterwards.
- Not a substitute for the acquisition programme directed on 29 August.
- Not verified beyond components and five modifiers — see decision 3.
- Not a score change, which is the whole point.

## Re-derive the distribution

Recompute `vary(0.35, name + '_' + K, 0.30)` per component against
`components[K]`, and count the metrics block. Both are single passes over the
published tree.
