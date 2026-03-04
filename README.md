# SSI Index Dashboard — v4.0

**Systemic System Infrastructure Index** — a composite resilience score for Italy's 4,293 substations.

475 EHV (≥220 kV) · 3,035 HV (100–219 kV) · 115 MV (20–99 kV) · 668 LV (<20 kV)

81 variables · 30 public data sources · 6 components · 20 metrics · 7 modifiers · 10k Monte Carlo iterations

## Live Dashboard

Deploy to any static host (GitHub Pages, Netlify, Vercel, or open `index.html` locally).

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
├── ssi-engine.js       # SSI v4.0 calculation engine (client-side)
├── ssi-metadata.js     # Complete metadata registry (81 vars, 30 sources)
├── map.js              # Canvas map engine (pan/zoom/click/touch)
├── ssi-data.json       # SSI dataset (4,293 substations)
└── grid-geo.json       # Grid geometry (14,221 lines + substations)
```

## Formula

```
R_final = soft_clip_upper(R_base × F_topo × C_mult × R6_mult × Cyber_factor)

R_base  = 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T

F_topo  = graph_criticality(degree, BC, bridge)      // R4 [0.80, 1.35]
C_mult  = consequence_sigmoid(pop, load, V_socio)     // R3 [0.70, 1.30]
R6_mult = restoration_speed_sigmoid(CAIDI)             // R6 [0.90, 1.10]
Cyber   = cyber_categorical(automation_level)          // R7 [0.95, 1.05]
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

30 verified public data sources — 28 fully open, 2 require free registration (Copernicus CDS, ENTSO-E).

Key sources: E-Distribuzione, ARERA TIQE, ISTAT, BdI QEF 737, GSE Atlaimpianti, Terna Open Data, OSM Overpass, Copernicus CDS/ERA5, OIPE LIHC, EEA Air Quality, ISPRA IdroGEO, Eurostat.

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
