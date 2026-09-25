# PLAN OF WORK — everything that must be done, and the order it must be done in

**Date** 25 September 2026
**Status** Reference. Nothing here is executed by this document.
**Authority** Operator, 25 September 2026: *"before starting work, let us first
have a plan of work for all that must be done, in that way we have a reference."*
**Sequence** Every item obeys `SEQUENCE_change_order.md` (Pin 16):
decide → acquire → measure → pin → derive → propagate → project → measure → land.
**Rule of this document** every figure is measured and carries the command that
re-derives it. Where a figure is recorded rather than re-measured today, it says so.
**Audited twice.** Sections 5 and 6 were written before the estate was audited
and were wrong in eight places; D2 was then found already complete
(`FINDING_the_T_guard_tests_one_generator_of_two.md`). The first audit read the
records and the pipeline code and **not the git history**, which is where three
of the four errors were visible. Rule now in force: *before an item enters this
plan as pending, `git log --grep` it and read the whole docstring of any
instrument it names.*
Sections 5 and 6 were They are corrected here from
`AUDIT_what_the_estate_already_holds_for_the_sixteen_metrics.md`, which must be
read with this document.

---

## 0. A note on the labels

The workstream labels used in conversation — **B1–B7**, **W1–W10**, **R4** — are
**not written down in any artefact**. A search of the site repo, `doctrine/` and
the SSI Index estate returns exactly one surviving use: `B7`, in
`DESIGN_the_public_private_boundary.md` and
`FINDING_the_conformance_register_reads_the_engine_against_itself.md`. `W1`–`W10`
and `R4` both exist in the repository as *different things* — the ENN axis
normalisations, and `R4_F_topo` in the modifier registry — so neither can be read
back as a workstream label.

That is the reason this document exists. A plan that lives only in a conversation
is lost when the conversation is.

**This document renumbers.** Workstreams are **A** to **F** below. If the
original B1–B7 / W1–W10 mapping matters, the flag officer restores it and this
document is amended under §8. The renumbering is a convenience, not a decision.

---

## 1. The one number that orders everything

The published score is `Σ component_weight × Σ intra_weight × metric`. Measuring
how much of that sum is actually derived from a measurement:

| component | weight | intra-weight measured | contribution measured |
|---|---:|---:|---:|
| C — Continuity | 0.30 | 0.000 | 0.000 |
| V — Voltage quality | 0.10 | 0.000 | 0.000 |
| **I — Infrastructure** | **0.25** | **0.720** | **0.180** |
| E — Economic | 0.10 | 0.000 | 0.000 |
| S — Saturation | 0.20 | 0.000 | 0.000 |
| T — Transition | 0.05 | 0.000 | 0.000 |
| | **1.00** | | **0.180** |

> **18 per cent of the composite is measured. 82 per cent is a hash of the
> substation's own name** — `vary(0.35, name + '_' + K, 0.30)`, per
> `FINDING_every_traced_component_is_a_hash.md`.

And of that 18 per cent, **none reaches a published score yet**: component I is
written alongside as `_I_from_metrics`, never into `components.I`, per the
31 August decision to swap once coverage is complete.

Re-derive:

    python3 -c "import sys;sys.path.insert(0,'scripts');
    from pipeline.scoring.engine import INTRA_WEIGHTS,COMPONENT_WEIGHTS;
    have={'I1','I2','I3','I4','I5','I6'};
    print(sum(COMPONENT_WEIGHTS[c]*sum(v for k,v in w.items() if k in have)
              for c,w in INTRA_WEIGHTS.items()))"

**Everything in this plan is, directly or indirectly, about moving that 0.180.**

## 2. The ledger — all nineteen metrics, their state and their blocker

Global weight = component weight × intra-weight. Sources as named in
`SSI_v4_2_Complete_Formula_Construct_Italy_v3.html`.

| rank | metric | global w | state | source / blocker |
|---:|---|---:|---|---|
| 1 | **S1** Municipal KPI gen/consumption | **0.150** | hash | Dimovski et al. breakpoints 1.29 / 7.78. **No acquisition designed.** |
| 2 | **C1** Duration (SAIDI) | **0.120** | hash → italy measured | regulator continuity return. See §5. |
| 3 | **V1** Severity-weighted dips | **0.100** | hash | same acquisition as C1 (V1 = SAIDI × V_socio) |
| 4 | **C2** Count (SAIFI) | **0.090** | hash → italy measured | same acquisition as C1 |
| 5 | **E1** Penalties per LV user | **0.055** | hash | half-blocked on `C1_raw` + `avg_load_MW` |
| 6 | **T1** DER Stress Index | **0.050** | hash | DER penetration + output variability + EV load. No acquisition designed. |
| 7 | **E2** Productivity loss coefficient | **0.045** | hash | Method C, bounds [1.50, 1.85]. Bounds exist; the input does not. |
| 8 | C3 MT exceedance % | 0.045 | hash → italy proxy | **structurally unpublished** — `FINDING_C3_is_not_published_where_C1_C2_C4_are.md` |
| 8 | C4 Planned/unplanned split | 0.045 | hash → italy measured | same acquisition as C1 |
| 10 | I3 Heat-wave deviation | 0.0375 | **MEASURED 39/39** | — |
| 11 | I1 Sea-level / coastal | 0.030 | **MEASURED 39/39** | — |
| 11 | I4 Transmission density | 0.030 | **MEASURED 37/39** | iceland, luxembourg absent |
| 11 | I5 Thermal stress (C57.91) | 0.030 | **MEASURED 39/39** | — |
| 11 | I6 Substation density | 0.030 | **MEASURED 39/39** | — |
| 15 | I7 Load stress | 0.025 | absent | Terna Open Data + GME. No acquisition designed. |
| 15 | I9 Hydrogeological risk | 0.025 | absent | ISPRA PAI. No acquisition designed. |
| 15 | S2 Reverse power flow | 0.025 | hash | categorical {none→0, >1%→0.5, >5%→1.0}. σ = 0. |
| 15 | S3 Criticality class | 0.025 | hash | categorical {non-critical→0, hospital/transport→0.5, multiple→1.0}. σ = 0. |
| 19 | I2 Wind gust | 0.0225 | **MEASURED 29/39** | CERRA domain — 108,550 records outside it. `PLAN_I2_cerra_five_years.md` |
| 20 | I8 Air-quality corrosion | 0.020 | absent | **BLOCKED**: ISO 9223 needs SO₂ and chloride *deposition*; neither is in ERA5. |

Two things this table says that were not obvious:

1. **S1 is the single largest metric in the index**, at 0.150 global weight —
   larger than C1 — and it has no acquisition designed, no source located, and no
   finding written about it. It is the largest unexamined thing in the estate.
2. **S2 and S3 are categorical with σ = 0.** They are the cheapest 0.050 of
   global weight available anywhere, and they need a classification, not a fetch.

## 3. Workstream A — land what is already built

Nothing new is built. Four things are finished and waiting. Pin 5: each lands
before the next starts. Pin 6: the operator runs every git command.

| # | item | state |
|---|---|---|
| A1 | `land_20260925_DW.sh` — boundary source, cross-border gate that fails closed, preflight strict default | **written, five gates verified, unlanded** |
| A2 | `land_20260925_DX.sh` — the R7 re-measurement and a withdrawn claim | **written, three gates verified, unlanded** |
| A3 | Execute the cross-border write — `ssi_resolve_cross_border.py --write`: remove 3,197, reassign 342 | manifest landed by A1; write not run |
| A4 | Italy's C and V — built, held on *"Hold V until C is ready too"* and *"all countries"* | **built, held** |

A3 runs at the head of the refresh, not before: it changes fleet membership, and
every measurement taken before it is taken against a different fleet.

**Also in the tree and not a workstream:** 259 modified `.html` (37 countries × 7
pages), uncommitted since 24 Sept 13:45. Diffed: cache-bust fingerprints only
(`style.css?v=`, `nav.js?v=`), no content change. They are what Pin 7 exists to
keep out of the wrong commit. Decision needed: land them alone, or let the
closing render supersede them.

## 4. Workstream B — the public/private boundary (the original B7)

The rule is decided: **what produces the scores is private; what checks them is
public.** `DESIGN_the_public_private_boundary.md` measures the cut and settles
`automation/` (four files public, `apply_parity_patches.py` private).

Measured today, none of it has been executed:

| # | item | measured state |
|---|---|---|
| B1 | Land `DESIGN_the_public_private_boundary.md` | **untracked** — the design exists on disk and in no commit |
| B2 | **SUPERSEDED.** Untracking cannot meet the requirement — it does not unpublish. Replaced by Option C in `AMENDMENT_DRAFT_the_engine_leaves_the_public_repository.md`: make this repository private, publish a fresh public one. **BLOCKED on signature.** Probed: private 270 / public 1,802 by closure; 4,290 page references, 0 in the private tranche; all validators pass. | **`git ls-files scripts/` returns 660.** Nothing untracked. |
| B3 | `.gitignore` entries so `git add scripts/` cannot resurrect it | absent — `.gitignore` names only caches and data under `scripts/` |
| B4 | Confirm `validate.yml` and `validate-schemas.yml` unchanged | decided in the design; not yet asserted by a gate |
| B5 | Move `apply_parity_patches.py` private | not done |

B2 is the item with a blast radius: eight scripts are invoked by the two public
workflows, and one of them (`check_cross_border.py`) imports
`scripts.pipeline.utils.geo`. The design measured that cost. It has not been paid.

## 5. Workstream C — the C mosaic, 39 jurisdictions

`METHOD_the_C_mosaic.md` is the method; `intelligence/c1_acquisition_register.yaml`
is the state. One acquisition class — the regulator continuity return — unblocks
**C (0.30) and part of E1 (0.055) = 0.355 of the composite**, the single largest
lever in the estate.

> **CORRECTED BY AUDIT.** This previously read 0.455, including V. It is not V.
> The construct defines V as `N(V1_total × (1 + 0.50 × V2_severe_ratio))` —
> severity-weighted voltage dips, source BdI QEF 737 — **not SAIDI**. Both the C
> register's V1 line and `scripts/ssi_derive_component_V.py` took the definition
> from the metric registry's *blocker string* rather than from the construct.
> **That instrument must not be landed as written.** It is held, so nothing
> published is affected. V needs a power-quality source that has not been
> searched for in any jurisdiction — see D13.

Register state, `compiled: 2026-09-25`: **5 of 39 researched**, 34 not yet.

| # | item | state |
|---|---|---|
| C1 | **italy** — C1/C2/C4 at 107 provinces, gated on the publisher's own totals; C3 as a declared TIQE art. 32 proxy | **ACQUIRED, built, held (A4)** |
| C2 | **france** — C3 at 94 départements, gated to 14 significant figures; C1/C2/C4 national only (18 records) | **ACQUIRED** |
| C3 | **italy** — the remaining 14.2% of LV users: nine DSOs each publishing their own art. 58 Rapporto | located, unread |
| C4 | **italy L1** — ARERA *Relazione Annuale* as a national anchor | **NOT LOCATED** |
| C5 | **spain** — TIEPI / NIEPI at *municipio × zona*, programmed separated from unplanned, CSV + Excel | **finest unit located anywhere.** Named next acquisition. |
| C6 | **norway** — RME, at *nettselskap* / *fylke* / *sluttbrukargruppe*, kortvarige and langvarige separated | route read, not fetched |
| C7 | **switzerland** — SFOE / Swissgrid SAIDI/SAIFI by canton, CSV. Today Switzerland's C is one value, 0.5, on 947 records | route named, nothing fetched |
| C8 | the remaining 33, in descending record count | not researched |

**Two standing corrections this workstream carries:**

- France's critère B is *"hors événements exceptionnels et hors RTE"* and must be
  set against Italy's *altre cause* 44.840, not its all-causes 73.11. On the
  matched basis France is **19 per cent worse**, not 27 per cent better. Both
  definitions files carry a `do_not_compare` block.
- `arera_tiqe_2024_regional.csv` publishes CAIDI built on D1L / N1L. The two
  indices are not on the same basis (D1L excludes short interruptions, N1L
  includes them). **That ratio must not feed a score and the inference drawn from
  it must not be repeated.**

## 6. Workstream D — the sixteen metrics that are still a hash

**Corrected by audit.** As first written this section said "no acquisition
designed" of seven metrics. None of those statements survived. Every one of the
sixteen is implemented in `france-pipeline/scoring/ssi_scorer.py`; what is
missing is not a construct but a real input. **Ten of that pipeline's twelve
ingestion modules make no HTTP request at all.**

The work is therefore not sixteen designs. It is: **one working fetcher to
generalise, ten typed producers to replace, one construct to rebuild, one
definition to correct, and one genuine blank to research.**

| # | item | global w | as measured |
|---|---|---:|---|
| D1 | **S1 + T1's DER_ratio via ODRÉ** | **0.200** | **IN PROGRESS — phase 1 decided.** Numerator real and **live-verified 25 Sept**: ODRÉ, 600 dept×filière rows, 104 départements, 176,443.9 MW, no key. **Denominator is not.** `avg_load_mw` = national load × population share, emitted with `"data_source": "rte_live"`. S1 needs **two series per jurisdiction, not one**, and nobody has looked for the second. See `DECIDE_S1_needs_two_series_not_one.md`. |
| ~~D2~~ | **T — DONE** | 0.050 | **Already landed**, `cced85da`, 21 jurisdictions; Italy's was landed and reverted (`124b1624`). The dry run reports Δ 0.0000 everywhere because it is idempotent. Replaced by D2a/D2b/D2c. |
| D2a | **extend the T guard to the second hash generator** | — | The guard tests `vary`/`stable_hash(name)` only. `score-country.py` uses `det_var`/md5(`substation_id`+`name`+suffix). On `DER_variability` — the one sub-metric with a country-constant base — the second generator reproduces at chile 96.2%, ireland 97.8%, norway 89.4%, slovenia 79.0%, all of which the guard **passed**. |
| D2b | **re-examine the 21 landed jurisdictions** | — | under the extended guard. `components.T` may have to be withdrawn where it fails. |
| D2c | T's real acquisition | — | per-unit DER capacity and consumption — **this is D1**. T is not a separate acquisition. |
| D3 | **S3** — criticality class | 0.025 | categorical, σ=0. France: distance to nuclear site. `governance.nis2_critical` on 2/39. Cheapest real weight in the estate. |
| D4 | **S2** — reverse power flow | 0.025 | **rebuild, do not transfer.** `ssi_scorer.py:259` computes it from `S2_flood_score`. A flood score is not a reverse-power-flow measure; the mapping followed the field name. |
| D5 | **E1** — penalties per LV user | 0.055 | construct written (`C1_raw × avg_load_mw / 50000`); source named BdI QEF 737 / ARERA; needs `avg_load_MW`, which is on 1 of 39 records |
| D6 | **E2** — productivity loss | 0.045 | `E2_local` on **38/39** but typed per country in `enrich_esg_gaps.py`. Australia's sampled 1.4 is **below the construct's own lower bound of 1.50**, which would make N(E2) negative. Verify across the cohort. |
| D7 | **I9** — hydrogeological | 0.025 | construct written (Géorisques flood score); `environmental_hazards.py` makes no request |
| D8 | **I7** — load stress | 0.025 | construct written; `socio_economic.load_GWh_annual` on 1/39 |
| D9 | **I8** — air-quality corrosion | 0.020 | the ERA5 finding stands — ISO 9223 needs SO₂ and chloride *deposition*, absent from ERA5. **But** `markov.corrosion_class` is on 38/39 (defaulted to `'C3'` for everyone) and France uses a coastal-département proxy. Decide: declare absent, or pin the proxy under Pin 14. |
| D10 | **I2** — close the CERRA gap | — | 108,550 records outside the domain. `PLAN_I2_cerra_five_years.md`. Mosaic tested twice, failed twice. |
| D11 | **I4** — iceland, luxembourg | — | two countries with no transmission line-km |
| D12 | **R2** — Adaptive IRI + climate trajectory | — | declared in the issued master, absent from `judgement.yaml` and from all 622,104 records. Operator decision 24 Sept: declare and implement. Needs a CMIP6 acquisition that does not exist. |
| D13 | **V** — the one genuine blank | **0.100** | severity-weighted voltage dips, `N(V1_total × (1 + 0.50 × V2_severe_ratio))`, BdI QEF 737. **No jurisdiction in this estate has been searched for a power-quality source.** The existing V instrument is built on the wrong definition. |
| D14 | the hazard rasters | — | `PLAN_hazard_raster_acquisition.md` — unblocks R6c/R6d/R6e and three country hazards, all currently a national constant jittered by a name hash |

**D1 is the recommendation, and it is now a stronger one than before the audit.**
It is 0.200 of the composite — the largest single move available — and the fetcher
is already written against a real, open, key-free endpoint. The question is
generalising it to 38 more jurisdictions, not designing it.

## 7. Workstream E — integrity defects, each already measured

None of these change a component. All of them are things the estate currently
publishes that it should not.

| # | item | measured |
|---|---|---|
| E1 | **The R7 editorial cutover.** `_r7_cyber_v1_retired` True on **0** of 622,104; `modifiers.R7_cyber` emitted on **543,546** | `RESULT_the_R7_cutover_is_arithmetically_done_and_editorially_not.md` |
| E2 | **The front end reads the retired modifier.** `R7_cyber_v2` appears in **no `.js` file**. On 78,558 records the NIS2 cell renders `gap` when the record carries a v2 term — a published compliance statement that is false | same |
| E3 | 38 of 39 `ssi-metadata.js` publish R7 bounds `[1.00, 1.10]` against the registry's `(0.99, 1.05)` | same |
| E4 | All 39 `intelligence.html` say *"consumers may select either"* — the score uses v2 only, the page displays v1 only | same |
| E5 | **23 records** publish a product of 1.00–1.10 against their own chain of 1.16–1.61; ten of them exactly `1.0000` | same |
| E6 | **84 records** carry v2 and their published product excludes it | same |
| E7 | **turkey: 30 records** with no `mult_product` key | same |
| E8 | **sweden: 2,582 records** carry no cyber term at any version; the registry comment asserts the opposite | same |
| E9 | **The gates that pass by not running.** Five instances. `check_r7_cutover_complete.py` prints "CUTOVER COMPLETE", exit 0, on an empty set | `FINDING_the_gate_that_passed_by_not_running.md` |
| ~~E10~~ | **The run gate — FIXED.** `cmd_fetch` now returns 1 when any class fails and names every failing country×class. Sentinel `tests/test_the_run_gate_fails_on_a_failed_class.py`, red against HEAD, green after. | landed in EA |
| E10b | **The install step** — `netCDF4`, `rasterio`, `cdsapi` declared and never installed; `numpy` arriving only via `shapely`. **Not actionable here**: only `validate.yml` and `validate-schemas.yml` remain in this repo and neither runs `fetch_data.py`. The five pipeline workflows went private in `41df6ab6`. **This belongs in the private repo.** | `FINDING_the_climate_chain_declares_what_it_never_derives.md` |
| E16 | **Two permanently red sentinels**, both pre-existing and unrelated to EA: `test_a_record_without_an_id_does_not_stop_a_country::test_4_no_record_is_dropped`, and `test_components_are_measured::test_the_live_register_reproduces_the_finding` — the latter red because france's `I` is no longer a hash, so the old finding no longer reproduces six of six. A test asserting a finding that progress has superseded. §7.8 | measured 25 Sept |
| ~~E17~~ | **WITHDRAWN.** `requirements.txt` is not absent — it is at `scripts/pipeline/requirements.txt` and declares `numpy`, `cdsapi`, `netCDF4`, `rasterio`, `shapely`: exactly the five the climate-chain finding says never get installed. That sharpens E10b rather than adding an item. | measured 25 Sept |
| E11 | The five health-check disclosures: D#30 (24 countries missing files), D#26 (14 countries), D#28 (cannot complete — stalls past 900 s), italy/spain `rd_pct_gdp` (3 unique values across 117 and 65 regions) | measured 25 Sept; **re-measure at execution** |
| E12 | `alert_components` is derived by nothing | `FINDING_alert_components_is_derived_by_nothing.md` — **untracked** |
| E14 | **`avg_load_mw` carries `"data_source": "rte_live"`** for a value that is a national total times a population share. Same class as the NIVA migration marker | `DECIDE_S1_needs_two_series_not_one.md` §3.1 |
| E20 | **161 unresolved links on the published site**, pre-existing and unchanged by any split: 39 to `reference-docs/` formula constructs that live in OneDrive not the repo, 39 directory-style `../methodology/` links, 83 relative paths inside the shared `esg-report-shared.html` template | measured 25 Sept |
| E18 | **13 of 26 `check_*.py` are run by nothing** — including `check_cross_border.py`, which the public workflow does run, and `check_r7_cutover_complete.py`. A checker nothing runs is not a check, public or private | `AMENDMENT_DRAFT_the_boundary_is_forward_looking.md` §6.2 |
| E19 | **The public workflow runs the weaker cross-border gate.** `validate.yml:110` runs v1; v2 (fails closed) runs only in `preflight.sh`. Promoting v2 needs a GISCO download step, which is blocked pending authorisation to `ssi_index@ikenga.eu` | same, §7 |
| E15 | **Paths resolved from one environment.** `ssi_boundary_source.py` and `ssi_repair_italy_province_from_coords.py` hardcoded the device-VM mount; repaired in DW. `session_k_r7_v2_dryrun.py:45` still carries `/sessions/wonderful-exciting-fermi/...` — a sandbox that no longer exists | `FINDING_the_pipeline_resolves_data_from_its_own_location.md` |
| E13 | The shard threshold is already breached | `FINDING_the_shard_threshold_is_already_breached.md` — **untracked** |

E10 is the one that compounds: while it returns 0, every other gate's greenness
is unverified.

## 8. Workstream F — the refresh, and the render

Pin 16 phases 6–9. **This workstream runs last and runs once.**

| # | item |
|---|---|
| F1 | The §8.5 amendment series render — 31 gaps closed first, per `PLAN_closing_the_31_gaps.md` |
| F2 | Execute A3 (the cross-border write) at the head of the refresh |
| F3 | Re-run everything that reads the metric block — `ssi_derive_component_from_metrics.py` above all |
| F4 | The per-country rescore, then `normalise_bands_per_country.py` — **not optional after any rescore**, because `score_substation` writes the absolute band into `classification` |
| F5 | Render master, then ONE country, read it, then the other 38 |
| F6 | Conformance register: read what MOVED by diffing against HEAD, not by reading the new file |
| F7 | Land: master documents first, then the site repo |

**The country-by-country refresh already run** — component I on its own metrics,
13 of 39 landed 24–25 September (israel, sweden, italy, germany, france, uk,
spain, portugal, hungary, slovakia, turkey, finland, norway) — is superseded in
shape by this workstream. Completing the remaining 26 on I alone would land 26
commits that F3 then redoes. **Recommendation: do not resume the per-country I
refresh as a separate sequence.** Fold it into F3.

## 9. What blocks what

    A1 A2  ──────────────────────────────► (nothing depends on them; they are debt)
    A3 ────────────────────────────────► F2   (fleet membership changes)

    C1..C8 ───► C measured (0.30) ───► part of E1 (D5)
                     │
                     └─────────────────► F3 F4   (the swap)
                  ✗  C does NOT unblock V. See the audit: V is
                     severity-weighted dips, not SAIDI.

    D1  ODRÉ ───► S1 numerator  ✓ live-verified              0.200
         └──► S1 DENOMINATOR ── not located in any jurisdiction
    D2  T   ───► land the written instrument   ───► F3 F4     0.050
    D3  S3  ───► categorical, sigma 0          ───► F3 F4     0.025
    D4  S2  ───► rebuild first                 ───► F3 F4     0.025
    D13 V   ───► needs a power-quality source that has not been
                 searched for in ANY jurisdiction               0.100
    D12 R2  ───► needs a CMIP6 acquisition that does not exist
    D14 hazards ─► R6c / R6d / R6e reclassification

    E10 (the run gate) ──────────────────► EVERY gate's greenness
    E1..E8 (R7) ─────────────────────────► F5   (the render publishes the fix)
    B1..B5 ──────────────────────────────► independent of all of the above

Two things are independent of everything and can be done at any time: **workstream
B** and **A1/A2**. Everything else funnels into F.

**The critical path is not C.** Ranked by weight unblocked against work required:

    D1  ODRÉ generalisation     0.200   numerator live-verified; denominator unlocated
    C   continuity acquisition  0.355   34 of 39 jurisdictions unresearched
    D2  land T                  0.050   instrument written, one decision to make
    D3  S3                      0.025   a classification, not a fetch
    D13 V                       0.100   nothing located anywhere

## 10. What is deliberately NOT in this plan

- **Zenodo and the JIS manuscript** — excluded by operator direction, 29 Aug.
- **The public site's design** — Pin 1. Data and claims evolve; layout does not.
- **Any paid data source** — Pin 15, and the standing constraint: open public data only.
- **Cross-country comparison of C** — already excluded by the per-country band,
  and now by `do_not_compare` in the definitions files.

## 11. For the flag officer

Five decisions this plan cannot make for itself.

1. **The label mapping.** Restore B1–B7 / W1–W10 / R4, or adopt A–F as written.
2. **What "R4 write" was.** It cannot be recovered from any artefact.
3. **Order.** This plan recommends: **A1 → A2 → D1 (generalise ODRÉ: S1 + T1's
   DER_ratio, 0.200 of the composite) → D2 (land T) → C5 (Spain) → E10 (the run
   gate)**, with workstream B run whenever convenient because it blocks nothing.
4. **`ssi_derive_component_V.py`.** Built on the wrong definition of V. Hold it,
   or withdraw it. It is not landed and nothing published is affected.
5. **The 259 cache-bust pages.** Land alone, or let F5 supersede them.

## Re-derive every figure in §1 and §2

    cd <site repo>
    python3 -c "import sys;sys.path.insert(0,'scripts');
      from pipeline.scoring.engine import INTRA_WEIGHTS,COMPONENT_WEIGHTS;print(INTRA_WEIGHTS)"
    python3 -c "import yaml;d=yaml.safe_load(open('intelligence/c1_acquisition_register.yaml'));
      print(d['researched'], len(d['not_yet_researched']))"
    git ls-files scripts/ | wc -l
    git log --oneline --grep='^components: ' | wc -l
