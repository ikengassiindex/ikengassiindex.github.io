# RESULT — the circularity test for the mosaic-gain measurement

**Date** 17 September 2026
**Measured on** the deployed tree, all 39 countries, **622,104 substations, every
shard**. Full census, not a sample.
**Status** measurement only. Nothing in the estate was changed.
**Scripts** `~/circ/extract.py`, `~/circ/circ_test.py`, `~/circ/verify_synth.py`,
`~/circ/verify_mods.py` (scratch, outside the estate; all read-only).

---

## The question

Mosaic gain compares what an adversary learns from open data (B1) against what
they learn from open data plus the index (B2), scored against a "true
high-consequence set".

*(Framing corrected 21 September 2026. The doctrine this construct rests on was
defined wrongly in `THINKING_I2_mosaic.md` §3 and is corrected there. In short:
this estate's case is the open-data MOSAIC EFFECT, not the securities mosaic —
there is no non-public leg, because the index is published. The measurement
below is unaffected; what changes is its reading. 0.151 -> 0.538 does not say
"the index adds material information". It says the index supplies the
ASSEMBLY — an index is not a tile in the mosaic, it is the assembled mosaic —
and the expensive step it spares an adversary is the linkage.)* If that ground truth is defined using quantities the index
already publishes, B2 wins by construction and the measurement is the index
computing the thing it computes. Three candidate ground truths were to be tested:

  (a) topological criticality  (b) catchment population served  (c) cascade consequence

Method: out-of-sample R^2 on a seeded 70/30 split, country fixed effects as the
baseline (an adversary knows the country), missing values mean-imputed **with a
missingness indicator** because absence is visible too. Ridge (lambda=10) on the
re-run, because unregularised OLS blew up on the collinear countries.

---

## (c) Cascade consequence — UNAVAILABLE

`ssi_enn_v30/layer4/externality_cascade.py` is a pollutant-monetisation cascade
(NOx / PM2.5 / SO2 damage costs, 30-year NPV, DALY) over 17 Config B BESS sites.
`ssi_enn_v30/layer3/cascade_v33_to_v32_release.py` is a DCF/IRR re-run, and is
marked DEPRECATED under a Convention #56 exemption. Neither models power flow;
neither produces per-substation output. The caveat raised before the test was the
right one: the ENN "cascade" is economic externality propagation, not physical.

**Candidate (c) does not exist on this estate.** It is not circular; there is
nothing there.

---

## (a) Topological criticality — VACUOUS, which is worse than circular

The regression was never reached in a meaningful form, because the ground truth
turned out not to be a measurement.

`graph_topology.BC_percentile` is present on 539,625 records (86.7%).
**488,378 of them — 90.5% — reproduce bit-for-bit** from

    vary(base, name, spread) = round(base * (1 + (md5_01(name + ":42") - 0.5) * 2 * spread), 4)

with `base = GRAPH_TOPO_DEFAULTS[country]['BC']` and `spread = 0.25`, at
`scripts/enrich_esg_gaps.py:373`. The input is the **MD5 hash of the substation's
name**. There is no grid structure anywhere in the computation.

    graph_topology.BC_percentile   488,378 of 539,625   90.5% reproduced exactly
    graph_topology.degree          493,485 of 543,546   90.8%
    graph_topology.cluster_coeff   489,137 of 536,340   91.2%

Eight countries reproduce at **100.0%** — france, germany, italy, japan, portugal,
spain, uk, us — which is **484,345 records, 77.9% of the estate**.

Three independent confirmations, in case the hash match is not enough:

1. **The support is wrong.** France's BC_percentile occupies exactly
   [0.2475, 0.4125] = 0.33 x [0.75, 1.25], and every one of the 1,651 grid points
   at 1e-4 resolution is occupied. A *percentile* that never goes below 0.2475 or
   above 0.4125 is not a percentile. A betweenness distribution is heavy-tailed
   with most nodes near zero; this is uniform on a narrow band.
2. **Degree takes three distinct values** across 168,894 French substations.
3. **Five countries publish one constant for every record** — belgium,
   costa-rica, greenland, luxembourg, netherlands: BC = 0.05 on all 13,035.

There is also a dead branch. The fill is

    gt['is_bridge'] = 1 if gt['degree'] <= 2 and vary(0, name + '_bridge') > 0.7 else 0

and `vary(0, ...)` is identically `0.0`, which is never `> 0.7`. **The bridge fill
can only ever write 0.** Consistently, `is_bridge = 1` appears on 11,243 records
across 23 countries and on **none** of the seven countries the fill reached
completely (uk carries 145, from the 3.5% of records the fill did not reach).

**Candidate (a) is discarded.** Not because the index predicts it — because on
78% of the estate there is no topology there to predict. Regressing on it would
have produced a number, and the number would have meant nothing.

*Not established:* the ~10% of BC values that do **not** reproduce from this
generator are simply not from it. Whether they are measured is a separate
question this test did not answer.

---

## (b) Catchment population served — SURVIVES

`socio_economic.population` is present on 618,534 records (99.4%), and 619,522
(99.6%) carry `_catchment_population_source = GHSL_POP_R2023A_E2025_v4_2_task_451`.
`enrich_esg_gaps.py` never writes this field. It is genuinely per-asset: 83,369
distinct values across 168,894 French substations — a raster extraction, not a
regional constant repeated.

Out-of-sample R^2 on log(1 + population), n = 618,534, ridge lambda = 10:

    country fixed effects only                   0.151
    + everything the index publishes as score    0.538
    + published raw covariates as well           0.550
    index score outputs alone, no country        0.484

Within country, scores only, 32 countries with >= 800 records:

    median 0.571     quartiles 0.483 / 0.669     min 0.297 (italy)     max 0.821 (hungary)

So roughly **half** of catchment population is already recoverable from the
published payload, and roughly **half is not**. That is the shape a usable ground
truth has: informative enough that the index is doing something, independent
enough that the index is not simply restating it.

**Candidate (b) survives.**

---

## The finding that outranks the result

Both candidates are **published per asset in the deployed payload**. Checked
against `ikengassiindex-deploy-nl/luxembourg/ssi-data.json`: the deploy record is
76 fields, and `graph_topology.BC_percentile`, `graph_topology.degree` and
`socio_economic.population` are three of them. (The deploy copy is an older
edition — its population value differs from the current tree, which carries the
later GHSL catchment — but the fields are present.)

An adversary holding the index does not have to *infer* the ground truth. They
read it. B2 = 1 by direct lookup, for any ground truth drawn from these files,
and the regression above only matters under a posture that withholds the
ground-truth field.

This is a constraint on the measurement's design, not a defect: it means the
mosaic-gain construct must either

  - define its ground truth from a source **outside** the published payload, or
  - measure gain **against a declared redaction** — "with population withheld,
    the index recovers 54% of it" is a real number and an honest one.

The second is the more interesting paper, and it is measurable today: 0.538
against a 0.151 baseline is the answer to "how much does publishing the SSI tell
you about who it serves, if you are not told directly."

---

## What this changes

- Candidate (c) is struck. There is no cascade model on this estate.
- Candidate (a) is struck, and its striking is a defect report, not a test
  outcome — see `FINDING_the_name_hash_reaches_past_components.md`.
- Candidate (b) is the ground truth the construct gets built on, under a declared
  redaction of `socio_economic.population` from the adversary's B2 payload.
- The half-day this cost was the right half-day. A formula construct, a fetch
  plan and two paper drafts built on candidate (a) would have measured the
  reproducibility of an MD5 hash.
