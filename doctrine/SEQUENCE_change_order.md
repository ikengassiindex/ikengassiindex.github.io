# The order of a change — PINNED DOCTRINE

Pinned by the operator, 2026-09-10: "agreed, we proceed with your order of
sequences." Raised the same day, from what the I1 landing cost when it was done
out of order. Applies to any change that touches a metric, a component, a
modifier or a data source.

---

## 0. The two things that make the order non-obvious

**Documents are projections, never edits.** The Construct and the Appendix are
rendered from `SSI_FOUNDATION_taxonomy.yaml`, `SSI_FOUNDATION_judgement.yaml`
and the deployed repository. A hand-edited rendering is void (Bible §7
prohibition 1). So "update the foundational documents" always means: change the
YAML, then re-render.

**Some values cannot be pinned before they are measured.** An anchor, a
threshold, a percentile band. I3's anchor and I1's anchor could not have been
chosen before their fleets existed. So a doctrine-first rule, applied
literally, is impossible for that class of change.

The resolution is that the pin SPLITS. The definition is pinned before the
data. The parameter is pinned after it. Both are §8 acts; they are just not the
same act.

## 1. The sequence

    PHASE 1 — DECIDE                                  nothing derived
      1.1  Write the amendment or decision as a DRAFT in doctrine/.
           What is measured, in what units, on what interval, with what
           declared gaps and Convention #7 exposures.
      1.2  Operator pins the DEFINITION. If a parameter cannot be chosen
           yet, say so in the draft and leave it undeclared — the taxonomy
           guard will report it as pending on every document, which is the
           point, not a failure.

    PHASE 2 — ACQUIRE                                 nothing derived
      2.1  Price the request before designing the fetch (estimate_costs).
      2.2  Ask what variables the source actually offers before concluding
           what cannot be computed from it.
      2.3  Fetch. Refusals counted, never defaulted.

    PHASE 3 — MEASURE                                 no published metric
      3.1  Derive RAW only. Write `_X_raw` diagnostics; do NOT write
           `metrics.X`.
      3.2  Report the fleet distribution and every refusal and clamp.
      3.3  Interrogate the tail before trusting it. I1's P100 of 7.23 m was
           a glacier; 40 records of 622,079, and the anchor was not set by
           them — but that had to be measured, not assumed.

    PHASE 4 — PIN                                     doctrine changes here
      4.1  Operator pins the PARAMETER against the measured fleet.
      4.2  Record it in judgement.yaml: value, frozen, basis, provenance,
           and every declaration that must travel with the published value.
      4.3  Add the change_log entry. `element` must be a registry id — a
           bare metric id, not `I1.anchor`.

    PHASE 5 — DERIVE                                  published metric written
      5.1  Set the parameter in the derivation and re-run. `metrics.X` lands.
      5.2  Verify the written record two ways, not one. A value scan AND a
           text search. `v < 0` does not catch negative zero; it published
           "-0.0" on 23,997 records.

    PHASE 6 — PROPAGATE                               downstream data
      6.1  Re-run anything that reads the metric block —
           `ssi_derive_component_from_metrics.py` above all. Skipping this
           leaves coverage stale and the register measuring nothing.

    PHASE 7 — PROJECT                                 ONCE, and only now
      7.1  Render master, then all 39 countries, with `--out <folder>`.
      7.2  Render ONE country first and read it. A change_log entry that
           failed its guard was caught this way before it reached 39
           documents.

      Render last, because the documents measure the repository. Rendering
      before phase 6 publishes stale coverage. Today this was rendered three
      times for want of that rule.

    PHASE 8 — MEASURE THE RESULT
      8.1  Conformance register. Read what MOVED, by diffing against HEAD,
           not by reading the new file alone.
      8.2  Gates: provenance citations, data file sizes, cross-border,
           schema.

    PHASE 9 — LAND
      9.1  master documents FIRST, then the site repo. The site's records
           cite doctrine that master documents defines; the other order
           opens a window where the published estate cites doctrine the
           repository does not carry.
      9.2  One change per commit. Phase 1 to 9 completes before the next
           change starts.

## 2. Where your proposed order inverts

You put the foundational documents first, then the construct and appendix, then
the website, then recomputation. Phases 4 and 7 are exactly that. The inversion
is only that phases 2 and 3 — acquire and measure — must sit BEFORE the
foundational documents can be completed, whenever the change carries a
parameter that has to be measured.

For a change with no such parameter — a weight, a definition, a declared
limitation, a source swap — your order stands unaltered and phases 2 and 3
simply do not occur.

## 3. What is NOT in the sequence, deliberately

**The public website and the R recomputation are consequences, not steps.**
They do not follow automatically from a metric landing, and making them
automatic is how a rendering change or a score movement arrives without anyone
deciding it.

    Website.  Pin 1: the design is never touched. Data and information evolve
              normally, so a data change reaching the site needs no decision.
              A change to what the site CLAIMS does need one, and it is the
              operator's, raised separately with the evidence attached.

    R scores. A recomputation is its own decision with its own pin. Two things
              currently stand against one:
                - M-006 step 5 is still blocked.
                - components.I is enrich_esg_gaps.py:317 —
                  vary(0.35, name + '_' + K, 0.30) — on 456,184 records.
                  Measured correlation between the published component and its
                  own metrics: +0.0074 across 543,546 substations, with four
                  metrics measured. Recomputing R today would compute a more
                  precise function of a hash.

              The recomputation that matters is not R from the current
              components. It is components from their metrics — and that waits
              for coverage, per the decision of 31 August.

## 4. The single rule, if only one is kept

**A change lands before the next one starts.** Five derivations run across one
working tree over three days could not afterwards be separated into honest
commits, and had to land as two with the reason stated. Everything above is
downstream of that.
