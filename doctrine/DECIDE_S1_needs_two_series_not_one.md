# DECIDE — S1 needs two series, not one, and only one of them exists

**Date** 25 September 2026
**Status** Pin 16 phase 1 — DECIDE. Nothing acquired, nothing derived, nothing
written to any record.
**Item** `PLAN_OF_WORK.md` D1 — generalise ODRÉ for S1 and T1's `DER_ratio`.
**Operator direction** 25 September 2026: *"proceed with your suggested order."*
**Corrects** `PLAN_OF_WORK.md` D1, which said 0.200 of the composite was
available because *"the fetcher is already written against a real, open,
key-free endpoint."* Half of that is true. The other half is the subject here.

---

## 1. What S1 is

`SSI_v4_2_Complete_Formula_Construct_Italy_v3.html`, global metric ranking,
rank 1:

> **S1 Municipal KPI 0.150 — 15.0% cumulative — Dimovski et al.**

Component weight `S` = 0.20, intra-weight `S1` = 0.75, so **global weight
0.150 — the largest single metric in the index.** Normalisation is Method B
(`soft_clip((x − P5)/(P95 − P5))`) over that country's own fleet, with the
construct naming Dimovski breakpoints 1.29 / 7.78.

The implementation, `france-pipeline/scoring/ssi_scorer.py:252`:

    S1_raw = res_capacity_mw / avg_load_mw

A generation-to-consumption ratio. **Two series, not one.**

## 2. The numerator is real, and it was fetched live today

`ingestion/odre_registre.py` against
`https://odre.opendatasoft.com/api/explore/v2.1`, dataset
`registre-national-installation-production-stockage-electricite-agrege`. Its
own header: *"No API key required — fully public endpoint."*

Run from the device VM, 25 September 2026, the estate's own module, unmodified:

    HTTP 200
    600 département × filière combinations
    104 départements
    10 filières
    176,443.9 MW total installed capacity

That is a real, open, per-unit generation-capacity series, reachable from this
session without a credential. **It is the best-conditioned acquisition located
anywhere in this estate so far.** It also carries `cap_mw_solaire` and
`cap_mw_eolien`, which are T1's `DER_variability` inputs.

## 3. The denominator is a population allocation wearing a live-data marker

`ingestion/rte_eco2mix.py` does make real requests — two, OAuth-authenticated,
against `digital.iservices.rte-france.com`. They return the **national** load.
Then, at line 218:

    dept_load_mw = national_load_mw * pop_frac      # pop_frac from DEPT_POPULATION

and every field built on it:

    peak_load_mw      = dept_load_mw × {1.25 Île-de-France, 1.22 AURA/PACA, 1.18 else}
    base_load_mw      = dept_load_mw × {0.85, 0.83, 0.80}
    annual_load_twh   = dept_load_mw × 8760 / 1e6
    nuclear_gen_twh   = annual × 0.66      wind × 0.13      solar × 0.05
    hydro_gen_twh     = annual × 0.12      thermal × 0.04
    wind_capacity_mw  = pop_frac × 25,000 × regional multiplier
    solar_capacity_mw = pop_frac × 21,000 × regional multiplier

and the row is emitted with:

    "data_source": "rte_live"

**`avg_load_mw` carries no départemental information whatsoever.** It is the
national total times a population share. The generation mix is five typed
national fractions with typed regional multipliers.

So, as implemented:

    S1 = res_capacity_mw / (national_load × population_share)
       = (installed capacity per head) × a constant

That is not a generation-to-consumption ratio. It is **renewable capacity per
capita**, which is a real and defensible quantity — but it is not what the
construct defines, and the denominator is not measured.

### 3.1 The marker is a §7.9 defect and belongs in workstream E

`"data_source": "rte_live"` asserts live RTE data for a value that is a
population-share allocation of a national total. This is the same class as
`FINDING_the_migration_marker_claims_a_source_that_cannot_have_produced_it.md`
— 90,476 records carrying a provenance marker asserting a source that cannot
emit the value they held. The live request *does* happen; what it returns is
not what the marker claims the field is. **Add to workstream E.**

## 4. None of it ever reached the estate

Scanned 1,170 published records across all 39 jurisdictions for
`avg_load_mw`, `res_capacity_mw`, `res_share`, `S1`, `S1_raw`, `peak_load_mw`:

    found:  load_GWh_annual on 30 records, one jurisdiction
    found:  nothing else, anywhere

The France S1 implementation is a working construct that was never wired into
the live pipeline. Published `components.S` is the name hash on the whole
cohort. This is the third instance of the pattern — after Italy's ARERA
continuity data and `transition.T1_score` — and it is now the estate's
characteristic failure: **derive it, then never connect it.**

## 5. What D1 therefore requires

Not one acquisition per jurisdiction. **Two.**

| | series | unit | France route | 38 others |
|---|---|---|---|---|
| numerator | installed generation capacity by filière | département | **ODRÉ — verified live today** | the national production register, per jurisdiction |
| denominator | electricity consumption | département | Enedis open data — slug not yet identified | the DSO or TSO consumption series, per jurisdiction |

**The denominator is the harder half and it is the one nobody has looked for.**

### 5.1 The France denominator, and why it is not settled here

`opendata.enedis.fr` serves the Explore v2.1 API and a known slug resolves:

    /api/explore/v2.1/catalog/datasets/indicateur-continuite-dalimentation/records
    → HTTP 200, total_count 94

which, incidentally, **independently re-verifies the C3 acquisition**: 94
départements, exactly the count `ssi_build_c_metrics_france.py` gates on.

But the catalog itself is not browsable from this session —
`/catalog/datasets` returns **410** (*"Cette couche de compatibilité pour la
version d'API précédente ne supporte pas cette requête"*) and the v1 search
path returns **404**. Guessed slugs return `Dataset not found`.

So dataset *discovery* on this portal is the operator's browser, per the
standing pattern (Overpass, Geofabrik, CERRA, and the C3 dataset itself). Once
the slug is known, the fetch runs from here.

**Requested:** the Enedis dataset id for annual electricity consumption per
département. Everything else on the France leg is ready.

## 6. What is decided, and what is not

**Decided, and it does not need a pin:**

1. S1 is acquired as **two series**, numerator and denominator, per
   jurisdiction. A single-series S1 is not the construct's S1.
2. ODRÉ is the France numerator. It is open, key-free, live-verified and it is
   the estate's own module — no new fetcher is written.
3. `avg_load_mw` as currently produced **must not be used as the denominator**,
   and the `rte_live` marker on it is a defect to be raised, not a source to be
   consumed.

**For the flag officer, because a parameter cannot be chosen before it is
measured (Pin 16 §0):**

4. **The Dimovski breakpoints, 1.29 and 7.78.** The construct names them; Method B
   uses the country's own P5/P95. Whether the breakpoints are the anchors or the
   normalisation is fleet-relative cannot be settled before a real S1 fleet
   exists. Deferred to phase 4, declared pending — which the taxonomy guard will
   print on every document, as intended.
5. **Whether S1's denominator is consumption or population.** If a consumption
   series cannot be had in most jurisdictions, capacity-per-capita is the
   honest fallback — but it is then a *different metric*, declared as such, not
   S1 with a substituted input. **Do not let the fallback inherit S1's name.**

## 7. Next step, and it is small

Phase 2 — ACQUIRE — on the France leg only, once the Enedis slug is known:
fetch both series, reproduce the publisher's own aggregates as a gate (the
pattern `ssi_build_c_metrics_france.py` established), and write
`data/s1_metrics/france.csv` plus `data/s1_definitions/france.yaml`. No record
is touched. Italy second, per the C precedent of building the definitional layer
before the second jurisdiction.

## Re-derive

    cd "SSI Index/SSI_v4_0 France/france-pipeline"
    python3 -c "import sys;sys.path.insert(0,'.');from ingestion import odre_registre as O;
                d=O.fetch_dept_capacity();print(len(d), d['codedepartement'].nunique(), round(d['total_mw'].sum(),1))"
    sed -n '215,250p' ingestion/rte_eco2mix.py       # the population allocation
