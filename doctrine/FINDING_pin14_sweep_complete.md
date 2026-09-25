> ## ⚠ THIS SWEEP WAS NOT COMPLETE — CORRECTED 21 September 2026
>
> **It tested 8 of 22 `vary()` writes.** The AST enumeration was correct; I then
> piped its output through `tail -45`, lost the head of the list, and treated
> the remainder as the whole. The claim below that the untested fields "are
> defaults and derivations rather than hashes" is **false** and is retracted.
>
> Caught because `SSI_CONFORMANCE_REGISTER.json` already carried a row naming
> `markov.risk_score` as reproducing from the substation name. The register was
> right and this document was wrong.
>
> The fourteen missed writes, tested over the full census:
>
>     tr.DER_ratio             488,401 / 494,518   98.8%
>     tr.DER_variability       488,408 / 494,518   98.8%
>     tr.EV_load_ratio         488,395 / 494,518   98.8%
>     se.rd_pct_gdp            489,402 / 491,936   99.5%
>     markov.ettc_years        489,424 / 543,509   90.0%
>     markov.p_critical_20yr   488,549 / 543,509   89.9%
>     markov.risk_score        485,833 / 543,546   89.4%
>     se.unemployment_rate      69,609 / 495,623   14.0%
>     se.V_socio                62,957 / 495,623   12.7%
>     se.gdp_per_capita         60,034 / 495,623   12.1%
>
> So the **Markov degradation model** — risk score, expected time to critical,
> probability of criticality at 20 years — and the **transition block** — DER
> ratio, DER variability, EV load ratio — are a hash of the substation's name
> on ~90 and ~99 per cent of records respectively. `markov.ettc_years` also
> carries `vary(0, name, 3.0)`, identically zero, so it reduces to
> `25 − risk_score × 50`: a deterministic function of a hashed input. Third
> instance of the dead `vary(0, …)` pattern after `is_bridge`.
>
> `transition.DER_ratio` was cited earlier in this session as a real per-asset
> field in the mosaic-ladder coverage table. It is not.
>
> The method lesson stands and sharpens: enumerate from the FIELD and ask what
> writes it. Enumerating from the generator is necessary and not sufficient —
> and truncating the enumeration makes it neither.

# FINDING — the Pin 14 sweep, complete

**Date** 20 September 2026
**Instrument** `scripts/check_pin14_name_hash_sweep.py` (new, read-only).
**Measured on** the deployed tree, all 39 countries, 622,104 records, every
shard. Exact bit-for-bit reproduction, not correlation.
**Status** measurement only. Nothing written.

---

## Pin 14

> "A coefficient must be verified against a primary or secondary source (we
> cannot state unverified as it is illogical)."

`scripts/enrich_esg_gaps.py` fills any absent field from
`vary(base, name, spread)` — a deterministic MD5 of the substation's own name.
Earlier findings tested the fields the work happened to reach. This sweep tests
**every** field that generator writes.

The field list was enumerated by **AST from the generator itself**, not by grep,
so it is complete for subscript assignments. That matters: two of the largest
results below are fields no previous pass had looked at.

## Result

    field / relation                     present  reproduced     rate
    -------------------------------------------------------------------
    gt.cluster_coeff                     536,340     489,137    91.2%
    confidence_tier == "medium"          543,403     493,076    90.7%   NEW
    mod.R7_cyber                         543,546     483,058    88.9%
    mod.R6_restoration                   543,546     483,028    88.9%
    mod.R4_F_topo                        543,546     483,018    88.9%
    components.V / .E                    543,546     481,949    88.7%
    components.C                         543,546     481,943    88.7%
    components.I / .S                    543,546     481,941    88.7%
    components.T                         543,546     481,931    88.7%
    CI_width                             622,039     398,603    64.1%   NEW
    seismic.R6 == f(pga)                 580,939     219,063    37.7%
    mod.R6_seismic                       597,557     216,022    36.2%
    R_P95 == R_median + CI/2             622,039      85,844    13.8%
    R_P5  == R_median - CI/2             622,039      84,110    13.5%
    se.E2_local                          540,927      65,102    12.0%
    fleet_percentile                     622,039         346     0.1%
    R_median == rbase x Pi(all mods)     541,208          70     0.0%
    modifier holds a NON-NUMERIC value     2,338           —        —   NEW

## The two that are new, and the second is the worse one

**`CI_width` is `vary(0.22, name, 0.15)` on 398,603 records — 64.1 per cent.**
The published width of the confidence interval is a hash of the substation's
name on nearly two thirds of the estate. It is not a measure of uncertainty;
it is a measure of the letters in the asset's name.

**`confidence_tier` is the literal string `"medium"` on 493,076 records — 90.7
per cent.** Not computed, not degraded, not declared absent. Assigned. The field
that tells a reader how much to trust the record says "medium" on nine records
in ten because a fill wrote it there.

Together these are the index's entire uncertainty apparatus. A reader looking at
a substation sees a point estimate, an interval and a confidence tier, and on
most records two of those three are the name.

## What the sweep also settles, in the other direction

Three fields are largely NOT the hash, and that is worth recording as plainly as
the failures:

- **`fleet_percentile` — 0.1 per cent.** Effectively all real, computed against
  the fleet.
- **`R_median` — 0.0 per cent** against the fill's own approximation
  (`r_base x Pi(all modifiers)`, which is not even the master equation, since it
  multiplies the additive modifiers instead of adding them). R_median comes from
  the Monte Carlo, as it should.
- **`R_P5` / `R_P95` — 13.5 / 13.8 per cent** against the fill's
  `R_median ± CI_width/2`. Most come from the Monte Carlo.

So the score itself is computed. The uncertainty around it largely is not.

## A schema defect found in passing

2,338 records carry `modifiers.R3_tier` holding a STRING — `'Light-Rural'` and
similar — inside the numeric modifier namespace. Latvia 1,219, Estonia 614,
Lithuania 505. `compute_modifier_terms` skips unknown names so the chain is
unaffected, but any consumer that multiplies the modifier dict raises
`TypeError`, which is exactly what this sweep did on its first run. A label does
not belong in the modifiers block.

## What is now verified, and what is still not

**Verified bit-for-bit, all 622,104 records:** components C V I E S T,
graph_topology degree / BC_percentile / cluster_coeff / is_bridge,
modifiers R4_F_topo / R6_restoration / R6_seismic / R7_cyber, socio_economic
E2_local, CI_width, fleet_percentile, confidence_tier, R_median, R_P5, R_P95,
seismic R6-from-PGA.

**Not covered by this sweep**, because the generator does not write them:
`seismic.pga_g` itself (a national reference table with location logic —
Convention #7 documented proxy, a different question from a name hash),
`socio_economic.EP_rate_region`, `markov.corrosion_class` and `steady_state`
(constants from `MARKOV_DEFAULTS`), `transition.T1_score` (computed from DER
sub-metrics), and `modifiers.R3_C_mult` (derived from V_socio). Those are
defaults and derivations rather than hashes, and each needs its own provenance
question — they are not silently fabricated per asset in the way the table above
records.

## Consequence for the provenance flag

`PROPOSAL_score_basis_provenance_flag.md` left open whether its `synthetic`
token could be trusted when the sweep had not run. **It has now run.** The token
can be defined over the verified set above rather than over "what happened to be
checked", which was the objection. The proposal's decision 3 is resolved; its
other two — whether the front end surfaces the field, and the vocabulary —
remain operator decisions.

The proposal should also now carry the uncertainty apparatus, not only
`components`. A record whose `CI_width` and `confidence_tier` are the name is
making a claim about its own reliability that it cannot support, and that is
exactly what a provenance flag exists to expose.
