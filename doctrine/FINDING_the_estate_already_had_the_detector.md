# FINDING — the estate already had the detector, and it already refused

**Date** 21 September 2026
**Found by** the field-first Pin 14 scan
(`scripts/check_pin14_field_first.py`, new), which flagged
`ssi_derive_component_T.py` as writing a field from a hash. It is the opposite:
a guard.
**Status** measurement only. Nothing written; the run below is `--dry-run`.

---

## What was already there

`scripts/ssi_derive_component_T.py` derives `components.T` from the transition
block. Before it does, it correlates `stable_hash(name)` against each
sub-metric and refuses the country if the correlation exceeds `HASH_R = 0.99`.

Run cohort-wide today:

    REFUSED 14 of 39

    canada  france  germany  italy  japan  portugal  spain  uk  us
        "transition block is a hash of the substation name
         (DER_ratio r=1.000, DER_variability r=1.000, EV_load_ratio r=1.000)"

    belgium  czechia  iceland  luxembourg  netherlands
        "degenerate sub-metric, Method B declines
         (1 distinct value across N records)"

Its own closing line states the case better than anything written this week:

> their transition block is `vary(base, name, spread)`, so deriving T from it
> would produce **a real formula over a name hash and label it sourced**.

`r = 1.000` on all three sub-metrics, in nine countries including the five
largest. Exactly 1.000 because `vary(b, n, s) = b·(1 + (h − 0.5)·2s)` is linear
in the hash, so the correlation is not approximate — it is algebraic.

## What this changes about the week

The last several days rediscovered by hand what this script detects
automatically: `FINDING_what_the_components_fill_costs.md`,
`FINDING_the_name_hash_reaches_past_components.md`,
`FINDING_pin14_sweep_complete.md` and its retraction,
`FINDING_the_second_name_hash_generator.md`. All correct, all slower, and one
of them wrong in a way this instrument would not have been.

**So the estate's problem is not that nobody built the check.** Someone built a
very good one — it names the generator by its exact signature, distinguishes a
hashed input from a degenerate one, and refuses rather than degrading quietly.
The problem is that its output never reached the doctrine. `components.T` has
`_from_metrics` on zero records, the refusal explains precisely why, and that
explanation lived only in the stdout of a dry run nobody had run.

`SSI_CONFORMANCE_REGISTER.json` carries a related row — components and
`markov.risk_score` reproducing from the name in 7 countries — at sampled
precision. It was right, and it was the thing that caught the Pin 14 retraction.
But a row in a register is not the same as a refusal with a named cause, and
neither was routed into `judgement.yaml`.

## The pattern worth generalising

`ssi_derive_component_T.py` is the model every derivation script should follow:

1. State the formula and its canonical anchor in the docstring.
2. **Test the inputs against the name hash before using them.**
3. Refuse the country and print the reason, rather than deriving anyway.
4. Distinguish "input is fabricated" from "input is degenerate" — different
   defects needing different remedies.
5. Treat the refusal as a result: "A refusal is a result, not a crash."

Only the first of those is common across the estate's derivation scripts. The
other four are in this one file.

## What the run also says, and it is not nothing

42,244 records across the 25 non-refused countries WOULD derive, at
`med Δ +0.0000`, `p95 |Δ| 0.0000`, `ΔR_base +0.0000`. Deriving component T
where the inputs are clean changes the score by nothing measurable, because T
carries a global weight of 0.05 and the values it would write match what is
already there.

**So the guard is essentially the whole value of the script.** The derivation it
guards is a no-op; the refusal is the finding. That is worth knowing before
anyone schedules the other five component derivations expecting them to move
scores.

65,602 records lack a sub-metric entirely and were left untouched, per
Convention #56.

## Queued

- Route the refusal into the conformance register and `judgement.yaml`, so
  `components.T`'s status carries the reason it is absent rather than only the
  fact.
- Add the same input-against-hash guard to the other component derivations
  before they are written, not after.
- `check_pin14_field_first.py` needs to distinguish a hash used to GENERATE a
  value from a hash used to DETECT one. It currently reports both, which is how
  this file surfaced. Two of the six files it flags are detectors
  (`ssi_derive_component_T.py`, `ssi_provenance_sweep.py`); four are
  fabricators (`enrich_esg_gaps.py`, `refresh_v42_modifiers_re_composite.py`,
  `build_hungary_ssi.py`, `build_slovakia_ssi.py`).

## Re-derive

    python3 scripts/ssi_derive_component_T.py --all --dry-run
