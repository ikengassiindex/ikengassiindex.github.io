# SSI Index — v4.2

**Systemic System Infrastructure Index** — an open-licensed, peer-reviewed, per-substation composite resilience score for civil critical-infrastructure grids under climate, cyber, and socio-economic stress. Live cohort at [`ikengassiindex.github.io`](https://ikengassiindex.github.io/).

> **Cohort at a glance (post Wave 4 TERMINAL closure, July 2026).** 796,121 substations across 39 countries (38 OECD member states + Greenland autonomous territory). 11 resilience modifiers on a heptagonal CVIESTR analytical surface. Peer-reviewed methodology anchored by *Journal of Infrastructure Preservation and Resilience* v16 (doi:10.1186/s43065-026-00193-z) and *Environmental Research: Energy* companion (doi:10.1088/2753-3751/ae87a5). Open-licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Stewardship targeted for the forthcoming Fondazione SSI Index (Naples, DPR 361/2000, 2027-2028).

---

## What SSI Index is

SSI Index publishes a per-substation resilience score for every electricity substation in each covered country's national grid, refreshed against upstream public regulator canonicals on a documented monthly cadence, with a v4.2 methodology that composes six baseline components with eleven multiplicative and additive modifiers to yield a bounded composite Re score at substation granularity, aggregated up to LAU-2 municipal, NUTS-3 provincial, regional, and national levels.

The methodology is peer-reviewed. The code is public. The data is open. The audit trail — cross-border point-in-polygon verification, historical event-validation battery, Sobol sensitivity, five-sigma tail-risk prism, Monte Carlo Gaussian copula, per-country classification-band calibration — is reproducible by any reader against the published canonicals.

## Cohort scope (39 countries, post Wave 4 TERMINAL closure)

| Wave | Closed | Countries |
|---|---|---|
| Wave 1 (initial cohort) | Q2-Q3 2026 | Italy · Australia · Austria · Belgium · Canada · Chile · Costa Rica · Denmark · Estonia · Finland · France · Germany · Greece · Greenland · Hungary · Iceland · Ireland · Israel · Japan · Korea · Latvia · Lithuania · Luxembourg · Mexico · Netherlands · New Zealand · Norway · Poland · Portugal · Slovakia · Slovenia · Spain · Sweden · Switzerland · Turkey · UK · US · Czechia · Colombia |
| Wave 2 (Feb 2026 refresh) | Q2 2026 | 15-country batch — Australia + Belgium + Netherlands + Chile + Hungary + Luxembourg + Slovenia + Costa Rica + Israel + Colombia + Lithuania + Estonia + Latvia + Slovakia + Czechia |
| Wave 3 (May 2026 refresh) | Q2-Q3 2026 | 9-country batch — Greece + Iceland + Switzerland + Ireland + Korea + New Zealand + Denmark + Finland + Turkey |
| Wave 4 (Jul 2026 refresh — TERMINAL) | Jul 2026 | 9-country batch — UK + Sweden + Portugal + Italy + Japan + Spain + France + Germany + US |

**Post-Wave-4 substation totals** — total 796,121; per-country sample: US 101k · Germany 187k · France 195k · UK 62k · Italy 51,910 · Spain 130k · Japan 5.4k · Portugal 5.7k · Sweden 42k. The Italian Stage 4 acceptance baseline of 4,293 substations remains the peer-reviewed methodology validation reference; the current Italian fleet grew via the Wave 4 refresh cycle.

## v4.2 methodology

### Six baseline components + R composite

Every substation is scored on six baseline components composed into a weighted R base:

| Component | Weight | Domain |
|---|---:|---|
| **C** Continuity | 0.30 | Outage frequency + duration (SAIDI, SAIFI, CAIDI) |
| **V** Voltage | 0.10 | Power quality, voltage stability margin, reactive support |
| **I** Infrastructure | 0.25 | Physical asset condition, substation loading, protection maturity |
| **E** Economic | 0.10 | Regional GDP per capita, energy-cost burden, fiscal capacity |
| **S** Saturation | 0.20 | DER penetration + curtailment risk, capacity utilisation |
| **T** Transition | 0.05 | Alignment with national + EU energy-transition pathways |

`R_base = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T`

### Master equation

```
R_final = soft_clip_upper(R_base × Π multiplicative_i) + Σ (additive_i − 1.0)

R_final ∈ [0, 1.30]
```

The multiplicative modifier chain compounds through `soft_clip_upper` toward an asymptotic ceiling near 1.0; the additive R6c_flood term then adds up to +0.30 on top, producing the Extreme band `R ≥ 1.00`. This is the mathematical signature of the v4.2 update — flood risk cannot be diluted by multiplication with well-behaved co-modifiers, so it enters additively.

### Eleven modifiers (v4.2 surface)

| Modifier | Range | Domain |
|---|---|---|
| R3 Consequence | [0.70, 1.30] | Population + load + socio-vulnerability at each substation catchment |
| R4 Graph criticality | [0.80, 1.35] | Degree, betweenness centrality, bridge detection |
| R6a Restoration speed | [0.90, 1.10] | CAIDI-anchored recovery |
| R6b Seismic hazard | [1.00, 1.25] | PGA (INGV / GEM / EMSC baseline) |
| R6c Flood (additive) | [0.00, +0.30] | ISPRA IdroGEO + Copernicus + national flood-risk atlases |
| R6d Wildfire | [1.00, 1.15] | EFFIS + national wildfire agencies |
| R6e Winter storm | [1.00, 1.10] | ERA5-anchored cold-snap frequency |
| R7 Cyber | [0.99, 1.05] | Province-level DESI / cyber-readiness proxy |
| R8 Adaptive capacity | [0.85, 1.15] | Adaptation-strategy alignment + governance capacity |
| R9 Compound-event concurrence | [1.00, 1.20] | Simultaneous multi-hazard exposure |
| R10 Distributive justice | [0.80, 1.20] | Deprivation + energy-poverty modulation |

**R7 dual-axis note.** The methodology carries R7 in two distinct roles: R7 Cyber as the multiplicative modifier in the R_final chain (above), and R7 SFDR PAI as the ESG-disclosure axis in the seven-axis ESG report set per FC v3 §14 subsection 13.7. Both axes coexist by design; readers looking at ESG report R7 are seeing the SFDR PAI infrastructure-disclosure surface, readers looking at the R_final chain are seeing the cyber-readiness proxy.

### Heptagonal CVIESTR

The v4.2 radar surface is a seven-vertex heptagon with axes:

**C**ontinuity · **V**oltage · **I**nfrastructure · **E**conomic · **S**aturation · **T**ransition · **R**esilience (Re composite)

The R (Resilience) axis is the composite of the eleven modifiers integrated over Markov-degraded state transitions and Monte Carlo-simulated cascade dependencies. It is the seventh vertex added in the v4.2 methodology to make explicit the compound-resilience signal that the six baseline components together do not capture. The v4.0.2 hexagonal radar (C·V·I·E·S·T only) is preserved for backward compatibility on the SSI-ENN valuation-side product per full-clone bifurcation (see `docs/methodology/SSI_v4_0_2_vs_v4_2_comparison.md`).

### Classification bands (5-band system, v4.2)

| Band | R range | Meaning |
|---|---|---|
| Low | 0.00 – 0.25 | Good resilience |
| Medium | 0.25 – 0.50 | Moderate vulnerabilities |
| High | 0.50 – 0.75 | Investment priority |
| Critical | 0.75 – 1.00 | Urgent intervention |
| **Extreme** | **1.00 – 1.30** | **Extreme intervention** (additive R6c_flood territory) |

The Extreme band is unique to v4.2 and captures substations where the additive R6c_flood modifier pushes R_final past what the multiplicative chain alone can produce. Sobol first-order sensitivity indices (validated 12 June 2026 against Italy's 4,293-substation Stage 4 reference set, 33/33 checks GREEN) rank R6c_flood second at S_i = 0.96 among all modifier signals.

## Peer-reviewed methodology anchors

- **JIPR v16** (June 2026) — *Journal of Infrastructure Preservation and Resilience*, doi:10.1186/s43065-026-00193-z — the peer-review anchor for the Markov degradation methodology, cross-border discipline, and Italian-pilot Stage 4 acceptance.
- **ERE companion** (July 2026) — *Environmental Research: Energy*, doi:10.1088/2753-3751/ae87a5 — the peer-review anchor for the compound-hazard R9 modifier calibration, Monte Carlo Gaussian copula 20×20 methodology, and the heptagonal CVIESTR + R additive-modifier extension.

## Data sources

Public regulator canonicals only. ~30-34 verified upstream sources per country; most fully open; roughly three require free registration (Copernicus CDS, ENTSO-E Transparency Platform, US Census ACS).

**Italy reference sources** — E-Distribuzione, Terna Open Data + Rapporto Mensile, ARERA TIQE, ISTAT, Banca d'Italia QEF, GSE Atlaimpianti, OSM Overpass, Copernicus CDS/ERA5, OIPE LIHC deprivation register, EEA Air Quality, ISPRA IdroGEO + INEMAR + Atlas, INGV Model MPS04, Eurostat.

**Per-country equivalents** — for every non-Italian country, an analogous public regulator canonical set. Full provenance + licence catalogue at [`scripts/pipeline/data/SOURCES_AND_LICENSES.md`](scripts/pipeline/data/SOURCES_AND_LICENSES.md).

**Phase 1.5 multi-country ingestion (June 2026 completion).** Three data classes ingested cohort-wide for all 39 countries:

| Class | Granularity | Sources |
|---|---|---|
| **Climate** | ERA5-Land 0.1° (~11 km) + daily statistics for heat/ice-day frequency | Copernicus CDS |
| **Seismic** | GEM 2023.1 Global Seismic Hazard Map 0.05° (~5.5 km) — CC BY-NC-SA 4.0 | GEM Foundation + INGV (Italy) + EAK (Greece) + national USGS/GSI equivalents |
| **Socio-economic** | NUTS-3 / state / canton / prefecture per-region | Eurostat (20 EU) + 19 non-EU per-agency (US Census ACS, ONS Nomis, StatCan, ABS, e-Stat, KOSIS, BFS, DANE, CBS, INEC, Hagstofa, Statistics Greenland, plus additional Wave 2/3/4 additions) |

**CMIP6 climate trajectories** (v4.2 refresh cycle) — SSP2-4.5 + SSP5-8.5 mid-century climate projections at ~11 km NUTS-3-consistent mesh, joined per substation for the R6c flood + R6d wildfire + R6e winter-storm forward-projection band.

## Discipline #36 — cross-border enforcement

Every substation in every country canonical is verified against its national polygon via point-in-polygon test at ingestion time. Bounds are defined per country in [`{country}/bounds.json`](https://ikengassiindex.github.io/) (Natural Earth-derived + territorial-extension corrections for Mode-3 countries like France DOM-TOM, UK NI, Canada Arctic, Greenland fjords, NZ Chatham + Kermadec + Tokelau, Chile Easter Island). Per-country tolerance (default 100 m; Greenland/NZ/Norway/Denmark 5 km for fjord/coastline simplification) is declared in `cross_border_tolerances.json`.

Five layers of defense: (1) per-country bounds.json; (2) tolerance config; (3) shapely-backed geometric helpers; (4) per-country one-shot remediation script; (5) CI deploy-gate and pytest sentinel that fail the build if any country exceeds 5% outside-polygon leakage. The 18 June 2026 audit found ~17% cohort-wide leakage (Austria 47.5% outside, Canada 74.4%, Greenland 86.5%, Norway 23.4%, Mexico 22.5%, UK 19.2%, Chile 12.1%) — all remediated cohort-wide. See [`CROSS_BORDER_SUBSTATION_AUDIT_20260618.md`](CROSS_BORDER_SUBSTATION_AUDIT_20260618.md) for the full audit memo.

## Wave 2/3/4 architectural conventions

The Wave 2/3/4 cohort expansion (Feb 2026 → Jul 2026 TERMINAL closure) produced two architectural conventions codified through empirical accretion:

- **Convention #78 BINDING** (3-class channel-reuse-mechanism taxonomy) — every new-country onboarding uses one of three architectural mechanisms: (1) fresh single-script build; (2) precedent-inheritance from an existing country's L1 connector; (3) multi-script decomposition for large or heterogeneous grids. Codified through 3-country empirical enforcement (Slovakia + Czechia + Poland) and promoted to BINDING at 3rd enforcement event.

- **Convention #79 candidate** (ssi-data sharding for large-country >100 MB canonicals) — countries whose per-substation `ssi-data.json` would exceed GitHub's 100 MB per-file hard limit are sharded into multiple ≤60 MB files (UK 62k, US 101k, Germany 187k, France 195k). Renderer patches in `map.js::loadSsiData()` and `country-renderer.js::loadSsiData()` auto-detect `sharded: true` sidecars and parallel-fetch + concatenate at load time. Fully backward-compatible for the 35 non-sharded countries. Empirical instance count 4; promotion to BINDING queued.

## Repository architecture

```
ikengassiindex.github.io/
├── index.html                    # Landing page — cohort overview + Wave 4 TERMINAL
├── map.html                      # Cohort map explorer (Leaflet + custom vector layer)
├── methodology.html              # v4.2 methodology brief
├── intelligence.html             # Intelligence section (per-axis analytical panels)
├── regional.html                 # Regional analysis (per-NUTS-3 ranking + comparison)
├── esg-report.html               # 7-axis ESG report (R1..R7 per FC v3 §14 subsection 13.7)
├── style.css                     # Ikenga design system
├── nav.js                        # Shared navigation
├── ssi-engine.js                 # v4.2 scoring engine (client-side)
├── ssi-metadata.js               # 101-variable metadata registry
├── map.js                        # Vector-canvas renderer (pan/zoom/click/touch)
├── country-renderer.js           # Per-country page renderer
├── esg-sections.js               # ESG report section builder
├── intelligence-sections.js      # Intelligence panel builder
├── regional-sections.js          # Regional analysis panel builder
│
├── {country}/                    # Per-country tree (39 countries)
│   ├── bounds.json               # National polygon for point-in-polygon
│   ├── ssi-data.json             # Per-substation canonical (sharded for 4 countries)
│   ├── grid-geo.json             # Grid geometry (substations + transmission lines)
│   ├── index.html                # Country landing page
│   ├── map.html                  # Country-specific map
│   ├── methodology.html          # Country-specific methodology page
│   ├── regional.html             # Country-specific regional analysis
│   ├── data.html                 # JSON/CSV/GeoJSON export page
│   ├── intelligence.html         # Country-specific intelligence panels
│   └── esg-report.html           # Country-specific 7-axis ESG report
│
├── intelligence/
│   ├── countries.json            # 39-country slug list (single source of truth)
│   └── edition-config.json       # Monthly edition counter
│
├── cross_border_tolerances.json  # Per-country tolerance config
├── versions.json                 # Methodology version pin
│
├── scripts/
│   ├── pipeline/                 # Monte Carlo scoring engine (Phase 1 PR-1+)
│   ├── check_cross_border.py     # CI-friendly cohort audit
│   ├── remediate_cross_border.py # Per-country one-shot remediation
│   ├── reclassify_phase2c.py     # Lightweight 5-band re-binning
│   └── ...
│
├── tests/
│   ├── test_no_cross_border_leakage.py           # Discipline #36 sentinel
│   ├── test_esg_reports_7_axis_synchronization.py # R7 dual-axis sync
│   └── ...
│
├── .github/workflows/            # 7 CI workflows (validate, pipeline, monthly refresh, etc.)
│
└── Report Production/            # Public reports (Strategic Briefs, Themed Analyses)
```

## Live dashboard

Deployed automatically to GitHub Pages within ~30-90 seconds of any push to `main`. No staging environment — `main` IS production. The `validate.yml` CI workflow gates every PR + push touching `*/ssi-data.json` or `*/grid-geo.json` to prevent broken data from landing.

**Landing page:** [`https://ikengassiindex.github.io/`](https://ikengassiindex.github.io/)

**Per-country page:** `https://ikengassiindex.github.io/{country}/` — e.g. [`italy`](https://ikengassiindex.github.io/italy/), [`germany`](https://ikengassiindex.github.io/germany/), [`france`](https://ikengassiindex.github.io/france/).

## Local development

**Opening `index.html` directly via `file://` will fail** with a "Data load failed" error because modern browsers block `fetch()` calls to same-directory JSON files from `file://` origins per the same-origin policy (CORS). This is a browser security feature, not an SSI Index bug — hosted GitHub Pages / Netlify / any `http://` or `https://` origin works normally.

Serve the repository through Python's built-in HTTP server (or any equivalent):

```bash
# From the repo root:
python3 -m http.server 8000

# Then open in your browser:
#   http://localhost:8000/               (landing page)
#   http://localhost:8000/austria/       (any country)
#   http://localhost:8000/map.html       (map explorer)
```

Ctrl-C to stop. Any port works — `8000` is convention.

Alternative one-liners:

```bash
npx serve .                # Node.js
php -S localhost:8000      # PHP
ruby -run -e httpd . -p 8000  # Ruby
```

## Foundation stewardship

Long-term stewardship of the SSI Index methodology + platform is targeted for the forthcoming **Fondazione SSI Index** in Naples under Italian association law DPR 361/2000, with establishment targeted for 2027-2028. The Foundation will hold the methodology, the code, the platform, the community, and the diversified post-grant funding stream that anchors permanence beyond any single grant cycle. Until Foundation establishment, the platform is operated by Altinium Invest S.r.L. as a public-good project under CC BY-SA 4.0 open licensing.

Academic peer-review anchor: the Information Processing and Telecommunications Centre (IPTC) at Universidad Politécnica de Madrid — Rubén San Segundo Hernández as overall academic anchor and Prof. Pedro Reviriego (GING research group) as substantive contributor.

## License

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** for the methodology, the code, and the per-country canonicals. This means:

- **Attribution** — you must credit "SSI Index" and link back to `https://ikengassiindex.github.io/`.
- **ShareAlike** — derivative works must be licensed under CC BY-SA 4.0 or a compatible license.
- **No additional restrictions** — you may not add legal or technological measures that restrict others from anything the license permits.

Full licence text: [`https://creativecommons.org/licenses/by-sa/4.0/`](https://creativecommons.org/licenses/by-sa/4.0/).

Third-party data sources retain their own licences (see `scripts/pipeline/data/SOURCES_AND_LICENSES.md`); the SSI Index composite score and the per-substation canonical are open-licensed under CC BY-SA 4.0.

## Contact

- **Cedric Berard** — c.berard@ikenga.eu — Altinium Invest S.r.L. / Ikenga Capital
- **SSI Index project** — ssi_index@ikenga.eu
- **Live cohort** — [`https://ikengassiindex.github.io/`](https://ikengassiindex.github.io/)
- **Companion valuation product (SSI-ENN)** — separate proprietary commercial vehicle under Convention #63 parallel-worlds discipline; SSI Index is the open-data open-methodology public-good pillar.
