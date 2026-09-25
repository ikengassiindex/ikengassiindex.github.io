# AUDIT — what the estate already holds for the sixteen metrics

**Date** 25 September 2026
**Status** Measured. Read-only. Nothing fetched, nothing derived, nothing written.
**Why it exists** Operator, 25 September 2026: *"as you have from time to time
missed things that were already in the estate, have you made an audit first (no
point to do things they may actually be clean)?"*
**It corrects** §6 of `PLAN_OF_WORK.md`, written earlier the same day, which
asserted absences it had not tested.

---

## 0. The challenge was correct

`PLAN_OF_WORK.md` §6 said of S1, T1, E2, S2, S3, I7 and I9: *"no acquisition
designed"*, *"no source located"*, *"nothing written"*. **None of those
statements survives an audit.** Designs exist, sources are named in the
construct, and for one metric a working public fetcher already runs.

This is the second instance of the same error in this estate. The first is on
the record: `intelligence/c1_acquisition_register.yaml` records Italy's ARERA
continuity data as *"ACQUIRED — real regulator data, never wired"*. The rule it
should have produced — audit before declaring absence — was written down and
then not applied to the next sixteen metrics.

## 1. The record already carries three of them

Census over all 39 jurisdictions, 50 records sampled per country:

| block / field | countries | which metric |
|---|---:|---|
| `transition.T1_score` | **38/39** | **T1** |
| `transition.DER_ratio` | 36/39 | T1 sub-metric |
| `transition.DER_variability` | 35/39 | T1 sub-metric |
| `transition.EV_load_ratio` | 35/39 | T1 sub-metric |
| `socio_economic.E2_local` | **38/39** | **E2** — the declared input |
| `markov.corrosion_class` | **38/39** | **I8** — ISO 9223 class |
| `governance.nis2_critical` | 2/39 | S3 candidate |
| `environmental.flood_zone` | 3/39 | I9 candidate |
| `socio_economic.load_GWh_annual` | 1/39 | I7 candidate |

Nothing anywhere carries a reverse-power-flow measure (**S2**) or a municipal
generation/consumption KPI (**S1**) under any name.

**None of these reach `metrics`.** The metric block holds I1–I6 and nothing else,
on all 39. So the estate holds derived quantities the scoring chain does not
consume — precisely the Italy-ARERA failure, repeated across three more metrics.

## 2. Every one of the sixteen is implemented in the France pipeline

`SSI Index/SSI_v4_0 France/france-pipeline/scoring/ssi_scorer.py` computes
**S1, S2, S3, E1, E2, I7, I8, I9 and T1** — the full set the plan called
undesigned — with a normalisation step and the same intra-weights as the live
engine (`"S": {"S1": 0.75, "S2": 0.125, "S3": 0.125}`, `σ(S2)=σ(S3)=0`).

The constructs, verbatim:

    S1_raw  = res_capacity_mw / avg_load_mw                    (ODRÉ)
    S2_raw  = f(S2_flood_score) → {0, 0.5, 1.0}
    S3_raw  = f(S3_nuc_km)      → {1.0 <20 km, 0.5 <50 km, 0.0}
    E1_raw  = C1_raw × avg_load_mw / 50000
    E2_raw  = 1.50 + 0.35 × soft_clip((E2_gdp_pc − 20000) / 50000)
    I8_raw  = 0.65 if dept in COASTAL_DEPTS else 0.30
    I9_raw  = S2_flood_score
    T1_raw  = 0.50·N(DER_ratio) + 0.30·N(DER_var) + 0.20·N(EV_ratio)

**The transfer question is therefore not "can a construct be found" but "is its
input real".**

## 3. Ten of the twelve France ingestion modules make no request

The test that settles it, run over every module in
`france-pipeline/ingestion/`:

| module | lines | HTTP calls | verdict |
|---|---:|---:|---|
| `odre_registre.py` | 180 | **1** | **FETCHES** — ODRÉ OpenDataSoft v2.1 |
| `rte_eco2mix.py` | 334 | **2** | **FETCHES** — RTE Open API (OAuth) |
| `insee_demographics.py` | 1,102 | 0 | no request |
| `insee_economics.py` | 327 | 0 | no request |
| `environmental_hazards.py` | 244 | 0 | no request |
| `ademe_socio.py` | 217 | 0 | no request |
| `meteofrance_climate.py` | 168 | 0 | no request |
| `osm_topology.py` | 160 | 0 | no request |
| `copernicus_era5.py` | 158 | 0 | no request |
| `cre_tiqe.py` | 122 | 0 | no request |
| `cyber_resilience.py` | 106 | 0 | no request |
| `brgm_seismic.py` | 98 | 0 | no request |

`cre_tiqe.py` was already known — recorded this morning as *"typed constants
behind a function named fetch()"*. **It is not the exception. It is ten of
twelve.** `insee_demographics.py` is the clearest case: 1,102 lines, 92
per-département dictionary entries, 509 numeric literals, **zero URLs anywhere in
the file**, and a `fetch()` whose own docstring says *"from hardcoded INSEE
statistics"*.

§7.2 — no measured value typed. §7.6 — no citation not read.

## 4. One real acquisition exists, and it is the largest metric in the index

`odre_registre.py` runs against
`https://odre.opendatasoft.com/api/explore/v2.1`, the national register of
electricity production and storage installations, and its own header states
**"No API key required — fully public endpoint."** It returns per-département
`total_capacity_mw`, `res_capacity_mw`, `res_share`, `cap_mw_solaire`,
`cap_mw_eolien`, `total_installations`.

That feeds, directly:

- **S1** — `res_capacity_mw / avg_load_mw`, global weight **0.150**, the largest
  single metric in the index;
- **T1's `DER_ratio`**, global weight 0.050.

**0.200 of the composite has a working, open, key-free fetcher already written,
against a real endpoint, and it is not wired into the live pipeline.** It is
France-only as it stands; the ODRÉ analogue in each other jurisdiction is the
acquisition question, and it is a far smaller question than "design S1".

Pin 15 and the open-data constraint are both satisfied by this route.

## 5. Three defects the audit found on the way

**5.1 — `S2` is mapped off a flood score.** `ssi_scorer.py:259` computes
S2 — *reverse power flow*, per the construct's `{No RPF→0, >1%→0.5, >5%→1.0}` —
from `S2_flood_score`. A flood score cannot be a reverse-power-flow measure under
any reading. The field name carries the `S2` prefix and the mapping appears to
have followed the name. Whatever else S2 needs, it does not need this.

**5.2 — `transition.T1_score` is a hash where `score-country.py` wrote it.**

    scripts/score-country.py:186
    'T1_score': round(max(0.01, min(1.0, det_var(seed+'t1', T*0.8, 0.20))), 3)

`ssi_derive_component_T.py` already measured the other side of this and its
finding stands: T1_score correlates **0.9996** with the published formula in
france, germany and italy — *real, not fabricated* — but **1.0000 with
`DER_ratio` alone**, so it is one sub-metric where the construct specifies three;
and in **norway it correlates 0.0762 with its own inputs**. The field is three
different things in three places.

**5.3 — `socio_economic.E2_local` is a typed per-country constant.**
`enrich_esg_gaps.py` carries a table of the form `{'V_socio': 0.28, 'E2_local':
0.95}` per country. Note also that the sampled Australian value, **1.4**, is
below the construct's own declared lower bound of **1.50** — so
`N(E2) = (E2_local − 1.50) / (1.85 − 1.50)` would be negative on it. Unverified
across the cohort; flagged, not measured.

## 6. The correction that matters most: V's definition is wrong in two places

`SSI_v4_2_Complete_Formula_Construct_Italy_v3.html`, section 02, canonical:

> **V — Voltage Quality 0.10. V Severity-weighted dips (1.00).
> V = N(V1_total × (1 + γ × V2_severe_ratio)), γ = 0.50.**
> Global weight ranking, rank 3: *"V Severity-weighted dips 0.100 — BdI QEF 737"*.

V is **severity-weighted voltage dips**, sourced to Banca d'Italia *Questioni di
Economia e Finanza* no. 737. It is **not SAIDI**.

Two artefacts built today say otherwise:

1. `intelligence/c1_acquisition_register.yaml` states the regulator continuity
   return is *"the sole dependency of V1 ('SAIDI; V_socio is already present at
   100% coverage')"*.
2. `scripts/ssi_derive_component_V.py` computes
   `V1_raw = C1_saidi_min(province) × V_socio(substation)` and says in its own
   docstring that it took that from *"the metric registry"*.

Both took the definition from **the metric registry's blocker string** rather
than from the construct. The blocker string names a source class that would
*unblock* the metric; it is not the metric's definition. §7.4 — no document
derived from another.

**Consequence.** `ssi_derive_component_V.py` is built on the wrong definition and
**must not be landed as written**. It is held, so nothing published is affected.
The C register's V1 line is corrected by this audit. The claim in
`METHOD_the_C_mosaic.md` and in the register that one continuity acquisition
unblocks **C + V + half of E1 = 0.455** is **overstated: it unblocks C (0.30) and
part of E1, not V.** The corrected figure is **0.355**, and V (0.10) needs a
power-quality source that no jurisdiction in this estate has been searched for.

## 7. What this changes in the plan

| plan item | as written | as measured |
|---|---|---|
| D1 — S1 | "no acquisition designed, no source located" | construct + normalisation written; **ODRÉ fetcher real and working**; source named (Dimovski et al., breakpoints 1.29 / 7.78) |
| D2 — S2, S3 | "needs a classification, not a fetch" | stands for S3; **S2 is currently mapped off a flood score and must be rebuilt, not transferred** |
| D3 — E1 | "half-blocked on C1_raw + avg_load_MW" | construct is exactly that; source named BdI QEF 737 / ARERA; input typed |
| D4 — T1 | "no acquisition designed" | **wrong** — instrument written, inputs on 87.4%, DER_ratio has a real fetcher |
| D5 — E2 | "bounds declared; the input is not" | **wrong** — `E2_local` on 38/39 and a construct from GDP/capita; both typed |
| D6 — I9 | "no acquisition designed" | construct written (Géorisques flood); producer makes no request |
| D7 — I7 | "no acquisition designed" | construct written; `load_GWh_annual` on 1/39 |
| D10 — I8 | "BLOCKED: ERA5 has no deposition" | the ERA5 statement stands, **but** `corrosion_class` is on 38/39 (default `'C3'`) and France uses a coastal-département proxy |
| §5 — C | one acquisition unblocks 0.455 | **0.355.** V is not SAIDI. |

**The shape of the work changes.** It is not sixteen acquisitions to design. It is:
**one working fetcher to generalise (ODRÉ → S1, T1), ten typed producers to
replace with real ones, one construct to rebuild (S2), one definition to correct
(V), and one genuine blank to research (V's power-quality source).**

## Re-derive

    cd "SSI Index/SSI_v4_0 France/france-pipeline/ingestion"
    for f in *.py; do echo "$f $(grep -c 'requests\.\(get\|post\)\|urlopen' $f)"; done

    cd <site repo>
    grep -n "T1_score" scripts/score-country.py
    grep -n "E2_local" scripts/enrich_esg_gaps.py | head
    python3 -c "import re,html;t=open('<construct>.html',encoding='utf-8',errors='replace').read();
      x=re.sub(r'<[^>]+>',' ',t);print([s for s in re.findall(r'[^.]*V2_severe[^.]*',html.unescape(x))])"
