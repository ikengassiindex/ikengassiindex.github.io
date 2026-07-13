# SSI Index Dashboard — v4.0.2

**Systemic System Infrastructure Index** — a composite resilience score now spanning **39 SoT countries** (substations totalling >130k across Italy, US, France, Germany, Spain, Korea, Norway, UK and 31 more).

Italy reference baseline: 4,293 substations · 475 EHV (≥220 kV) · 3,035 HV (100–219 kV) · 115 MV (20–99 kV) · 668 LV (<20 kV)

95 variables · 30+ public data sources · 6 components · 20 metrics · 8 modifiers · 11 data layers · 10k Monte Carlo iterations

## Live Dashboard

Deploy to any static host (GitHub Pages, Netlify, Vercel).

### Local development (task #123)

**Opening `index.html` directly via `file://` will fail** with a "Data load failed"
error because modern browsers block `fetch()` calls to same-directory JSON files
from `file://` origins per the same-origin policy (CORS). This is a browser
security feature, not an SSI Index bug — hosted GitHub Pages / Netlify / any
`http://` or `https://` origin works normally.

**Local dev workflow** — serve the repository through Python's built-in HTTP
server (or any equivalent):

```bash
# From the repo root:
python3 -m http.server 8000

# Then open in your browser:
#   http://localhost:8000/               (landing page)
#   http://localhost:8000/austria/       (any country)
#   http://localhost:8000/map.html       (map explorer)
```

Ctrl-C to stop. The server serves the current directory tree with correct
`http://` origin semantics, so all `fetch()` calls resolve normally. Any port
works — `8000` is convention; use `8080`, `3000`, etc. if `8000` is busy.

Alternative one-liners for developers who prefer other stacks:

```bash
# Node.js
npx serve .

# PHP
php -S localhost:8000

# Ruby
ruby -run -e httpd . -p 8000
```

None of these require configuration or additional dependencies. Also useful
for reviewers who want to preview PRs without deploying to Pages first.

## Architecture

```
ssi-dashboard/
├── index.html          # Overview — KPIs, distribution, mini-map
├── map.html            # Map Explorer — interactive canvas map
├── regional.html       # Regional Analysis — ranking, province, decomposition
├── methodology.html    # Methodology — formula, components, data sources
├── data.html           # Data & Download — JSON/CSV/GeoJSON exports
├── style.css           # Complete Ikenga design system
├── nav.js              # Shared navigation + footer
├── ssi-engine.js       # SSI v4.0.2 calculation engine (client-side)
├── ssi-metadata.js     # Complete metadata registry (95 vars, 30 sources)
├── map.js              # Canvas map engine (pan/zoom/click/touch)
├── ssi-data.json       # SSI dataset (4,293 substations)
└── grid-geo.json       # Grid geometry (14,221 lines + substations)
```

## Formula

```
R_final = soft_clip_upper(R_base × F_topo × C_mult × R6a_rest × R6b_seis × Cyber_factor)

R_base  = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T

F_topo  = graph_criticality(degree, BC, bridge)               // R4  [0.80, 1.35]
C_mult  = consequence_sigmoid(pop, load, V_socio)              // R3  [0.70, 1.30]
R6a     = restoration_speed_sigmoid(CAIDI)                     // R6a [0.90, 1.10]
R6b     = seismic_hazard(PGA_g, zone_weight)                   // R6b [1.00, 1.25]
Cyber   = province_DESI_cyber(region, province, voltage)       // R7  [0.99, 1.05]
```

## Components

| Component | Weight | Metrics | Domain |
|-----------|--------|---------|--------|
| **C** Continuity | 0.30 | 4 | Outage frequency and duration |
| **V** Voltage | 0.10 | 1 | Power quality events |
| **I** Infrastructure | 0.25 | 9 | Physical asset condition |
| **E** Economic | 0.10 | 2 | Economic impact |
| **S** Saturation | 0.20 | 3 | Grid capacity utilisation |
| **T** Transition | 0.05 | 1 | Energy transition exposure |

## Data Sources

30+ verified public data sources per country — most fully open, ~3 require free registration (Copernicus CDS, ENTSO-E, US Census ACS).

Italy key sources: E-Distribuzione, ARERA TIQE, ISTAT, BdI QEF 737, GSE Atlaimpianti, Terna Open Data, OSM Overpass, Copernicus CDS/ERA5, OIPE LIHC, EEA Air Quality, ISPRA IdroGEO, Eurostat.

### Phase 1.5 ingestion (June 2026) — multi-country L1

Three data classes ingested for all 39 SoT countries:

| Class | Granularity | Sources |
|---|---|---|
| **Climate** | ERA5-Land 0.1° (~11 km mesh) + daily-statistics for true heat/ice day counts | Copernicus CDS |
| **Seismic** | GEM 2023.1 Global Seismic Hazard Map 0.05° (~5.5 km) — CC BY-NC-SA 4.0 | GEM Foundation + INGV (italy) + EAK (greece) |
| **Socio-economic** | NUTS-3 / state / canton / prefecture per-region | Eurostat (20 EU) + 16 non-EU per-agency (US Census ACS, ONS Nomis, StatCan, ABS, e-Stat, KOSIS, BFS, DANE, CBS, INEC, Hagstofa, Statistics Greenland) |

Full provenance + license catalog: [`scripts/pipeline/data/SOURCES_AND_LICENSES.md`](scripts/pipeline/data/SOURCES_AND_LICENSES.md)

## Technology

- **Vanilla JS** — no framework, no build step
- **Canvas rendering** — custom map engine with pan/zoom/click/touch
- **Static deployment** — works on any HTTP server or file:// protocol
- **Ikenga design system** — Playfair Display + DM Sans, warm palette

## Classification Bands

| Band | R Range | Meaning |
|------|---------|---------|
| Low | 0.00 – 0.25 | Good resilience |
| Medium | 0.25 – 0.50 | Moderate vulnerabilities |
| High | 0.50 – 0.75 | Investment priority |
| Critical | 0.75 – 1.00 | Urgent intervention |

## Deploy to GitHub Pages

1. Push this repository to GitHub
2. Go to Settings → Pages → Source: Deploy from branch → `main` / `/(root)`
3. Dashboard will be live at `https://<username>.github.io/<repo>/`

## Copyright

Copyright © 2026 Altinium Invest S.r.L. All Rights Reserved.

This software program is protected by the United States Copyright Law, and Società Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.
