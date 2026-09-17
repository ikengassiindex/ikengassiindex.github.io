# FINDING — what R7_cyber v2 actually is, and why the cutover has not happened

**Date** 17 September 2026
**Measured on** the deployed tree, all 39 countries, **622,104 substations, every
shard**. Full census, not a sample.
**Status** measurement only. Nothing published was changed.
**Scripts** `~/circ/mosaic_rungs.py` and the census reader in `~/circ/extract.py`
(scratch, outside the estate, read-only).

---

## Why this was measured

The operator's design intent, recorded 22 August 2026, is that **R7_cyber_v2
SUBSTITUTES v1 — never a dual-write**, so the cyber modifier is never counted
twice. The question put before building the substitution was simply: what state
is it in now?

`CLAUDE.md`'s 18 August 2026 entry answers that the cutover is done cohort-wide.
The deployed records answer otherwise.

## 1 — The cutover has not happened in the data

    _r7_cyber_v1_retired == False        619,522 records   99.6%
    _r7_cyber_v1_retired absent            2,582 records    0.4%
    _r7_cyber_v1_retired == True                 0 records   0.0%

Zero records anywhere are marked retired. Coverage of the two modifiers:

    modifiers.R7_cyber    (v1)           543,546 records   87.4%
    modifiers.R7_cyber_v2                619,522 records   99.6%

v2 is the WIDER of the two. **78,558 records carry v2 with no v1 beneath it** —
the substitution is not a uniform swap and those records need a stated
treatment, not a fall-through.

`FINDING_mult_product_is_three_populations.md` already records where the
published chain stands: v1-only in 30 countries (51.4% of records), v2-only in
six (canada, finland, norway, sweden, turkey, uk — 16.8%), neither in five
(france, germany, italy, japan, us — 31.5%).

## 2 — The reason: two code files state opposite policies

This is not a documentation error. `scripts/pipeline/scoring/` contains both
halves of the contradiction.

**`modifier_registry.py` has cut over.** The `R7_cyber` entry carries

    "retired": "v4.24 (18 August 2026, GATE-A-11-REVISED hard cutover; superseded by R7_cyber_v2)",
    "superseded_by": "R7_cyber_v2",

and `apply_modifiers()` skips any modifier carrying `retired`. Its own
`retired_skip_counts()` docstring gives the expected outcome: *"R7_cyber: skipped
on 534,443 substations (successor present)"*.

**`r7_cyber_v2.py` has not.** Its module docstring states v2 "co-exists during
the ~6-month dual-write transition per Gate A GATE-A-11" and that "R7 v1 remains
live + emitted"; line 97 specifies `_r7_cyber_v1_retired` is **"initialized False
at v0 first apply"**. `scripts/session_m_r7_v2_cohort_apply.py` writes the same
value for the same stated reason.

So the marker reads `False` on every record because the module that writes it is
faithfully executing the dual-write policy that GATE-A-11-REVISED retired and the
registry already abandoned. **Both files are doing exactly what they say. They
say different things.**

A third factor compounds it: the deployed data predates any full rescore. Phase ζ
(39-country Monte Carlo, ~4–6 h) is still listed in `CLAUDE.md` as a deferred
operator-execution phase. Even with the code reconciled, the published
`mult_product` does not change until a derivation runs.

**Consequence for the build.** The substitution is mostly NOT new scoring code.
The registry has already cut over. The work is (i) reconcile the emitting module
with the registry, (ii) decide the 78,558 no-v1 records, (iii) derive, (iv)
measure. Writing a fresh v2 implementation would be solving a problem that is
already solved in one file and contradicted in another.

## 3 — v2 is national, and half of it has never run

**Granularity.** `R7_cyber_v2` takes **30 distinct values across 622,104
records**. The value frequencies map onto jurisdictions exactly:

    1.034538   168,894   france
    1.034308   108,016   germany
    1.039385    73,859   us
    1.032462    41,662   italy
    1.024154    27,764   poland

One value per jurisdiction. This is a national regime constant, not a per-asset
quantity.

**The product layer has never operated.**

    _r7_cyber_v2_fallback_reason = product_layer_none_full_weight_on_entity
                                                 619,522 records   100.0%

CRA Article 14 carries `w_product = 0.45`. It resolves to nothing on every record
in every country, so v2 runs on the NIS2 Article 21 entity layer alone with the
weight redistributed to unity. **Nearly half the designed construct has never
operated anywhere.**

This is Convention #56 working as intended: the construct declares its own
degradation on every record it touches. It is the opposite of the silent failure
recorded in `FINDING_the_name_hash_reaches_past_components.md`, and the contrast
should govern remediation order — a modifier that declares its shortfall is less
urgent than one that conceals it.

## 4 — Why per-asset granularity is an acquisition problem

NIS2 Article 21 attaches to **entities**; CRA Article 14 attaches to **products**.
Per-asset resolution of either requires knowing who operates the asset, or what
equipment is in it. Full-census coverage of every field that could carry that:

    region                    596,235   95.8%
    voltage_kv                584,686   94.0%
    markov.corrosion_class    543,509   87.4%
    confidence_tier           543,403   87.3%
    v43_sources               110,794   17.8%
    osm_feature_id            107,691   17.3%
    owner                     105,046   16.9%   (1,588 distinct)
    operator                   61,100    9.8%   (423 distinct)
    tso_zone                   51,449    8.3%   (40 distinct)
    governance.nis2_critical    8,089    1.3%
    voltage_tier                4,021    0.6%
    vintage                     2,247    0.4%   (poland only)
    dso                         2,247    0.4%   (poland only)

The entity layer bottoms out at `owner` **16.9%** and `operator` **9.8%**. The
product layer has no candidate field at all above 0.4%, which is precisely why it
is at 100% fallback — the code is not failing, the data was never acquired.

**So enriching v2 from national to per-asset is an ACQUISITION task on
`owner`/`operator`, not a modelling task.** No assembly of public facts can
resolve an entity the estate does not record. The precedent for the acquisition
already exists: the Denmark P28 alias-map extension normalised operator identity
across 4,822 records from OSM operator tags.

## 5 — What this does and does not justify

**Justifies the substitution.** Pin 14 requires a coefficient verified against a
primary or secondary source. v2's entity layer is anchored on NIS2 Article 21, a
real instrument. v1 is `vary(1.02, name, 0.015)` — an MD5 hash of the
substation's name, on 88.9% of records carrying it
(`FINDING_the_name_hash_reaches_past_components.md`). One satisfies Pin 14; the
other cannot. That settles the substitution independently of granularity: a
coarse regime constant with a citation beats a fabricated per-asset number.

**Does not justify releasing it silently.** Publishing a construct running at 55%
of designed weight, without declaring it, means published scores restate a second
time when the entity acquisition lands. Two unannounced restatements are worse
than one plus a declared roadmap.

## 6 — Queued, not done

- Reconcile `r7_cyber_v2.py` and `session_m_r7_v2_cohort_apply.py` with the
  registry's retired status. One of the two policies yields; per the 22 August
  operator directive it is the dual-write one.
- Decide the 78,558 records carrying v2 with no v1.
- Declare the product layer's absence in `SSI_FOUNDATION_judgement.yaml`, on the
  I4 abstention pattern, so the later enrichment completes a declared swap rather
  than arriving as a second restatement.
- Cost is already measured: `RESULT_what_completing_the_R7_cutover_costs.md`
  (31,726 band changes, 5.1%, Critical +12.2%) and
  `RESULT_the_three_R7_cutover_residuals.md`.
- **The sentinel cannot detect this defect, and that is the item to fix first.**
  `CLAUDE.md` queues a Phase κ rename of `test_v1_r7_cyber_still_present_dual_write`
  and the addition of a `TestPostCutoverInvariants` class. Checked against the
  file: **no test of that name exists**, and `TestPostCutoverInvariants` is
  already present at line 474. The queued work is stale in both directions.

  More important than the bookkeeping: `TestPostCutoverInvariants` asserts
  `versions.json` methodology `4.24`, `edition-config.json` ssi_version `4.24`,
  that the registry marks v1 `retired` and v2 not, and the Convention #79 shard
  thresholds. **Every one of those reads code or config. Not one reads a
  substation record.** The suite is therefore GREEN while `_r7_cyber_v1_retired`
  is `False` on 619,522 records and v1 still drives `mult_product` in 30
  countries — with no contradiction, because nothing in it ever looks at a
  record.

  This is `DOCTRINE_a_check_must_read_the_artefact.md`, second instance. The
  cutover cannot be declared done until an invariant reads the published records:
  no record carries both a live v1 in the chain and a v2, and
  `_r7_cyber_v1_retired` is True cohort-wide.

- `pytest` is not installed in the Cowork device VM, so the suite cannot be run
  there. Test runs go on the operator's Mac, or the test files and the scoring
  package are staged into the cloud container and run there. Decide which before
  the build, so "tests pass" means something.
