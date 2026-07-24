# v4.23 refresh callouts — extracted from country pages

> **Extraction date**: 21 July 2026
> **Source**: 5 country `index.html` files (australia + belgium + chile + hungary + netherlands)
> **Reason**: consolidated to a future changelog page; removed from per-country landing pages to reduce chrome.
> **Original location**: line 46 of each country's `index.html` (below the fleet-summary paragraph, above the "Operated as a non-profit" strapline).
> **Original styling**: terracotta-tinted callout `<div>` with left border `3px solid var(--terracotta)`, 12 px body, 1.6 line-height.
>
> These are ready-to-paste inputs for the future changelog page. Audit trail links reference YAMLs at `<slug>/v4_23-ingestion-audit-<slug>-{preflight,fetch,merge}.yaml` (all still on-repo, unmoved).

---

## Wave 2 — 13 July 2026 refresh cycle

### 🇦🇺 Australia

**v4.23 refresh (13 July 2026):** Owner attribution + line densification via OpenStreetMap Overpass API (ODbL) + Australia-specific state-jurisdiction fallback across 8 states/territories (NSW/QLD/VIC/WA/SA/TAS/ACT/NT); 5 state TSOs (TransGrid/Powerlink/AEMO Victoria/ElectraNet/Western Power) + 13 DNSPs (Ausgrid/Endeavour/Essential/Energex/Ergon/CitiPower/Powercor/Jemena/AusNet/United Energy/SA Power Networks/TasNetworks/Evoenergy/Horizon Power/Power and Water Corp). 88 distinct operators post-merge · 37.2 % owner-tagged · Convention #56 visibly-honest degradation preserved (VIC 5-DNSP unresolved cases flagged explicitly).

Audit trail: [preflight](../australia/v4_23-ingestion-audit-australia-preflight.yaml) · [fetch](../australia/v4_23-ingestion-audit-australia-fetch.yaml) · [merge](../australia/v4_23-ingestion-audit-australia-merge.yaml).

---

### 🇧🇪 Belgium

**v4.23 refresh (13 July 2026):** Owner attribution + line densification via OpenStreetMap Overpass API (ODbL) + Belgium-specific 3-region jurisdiction fallback. Federal-fragmented DNSP architecture: Flanders → Fluvius (post-2018 Eandis+Infrax merger, single DNSP for 5 provinces), Wallonia → ORES (4-province default) + Resa (Liège metro geofence), Brussels-Capital → Sibelga. TSO Elia at ≥150 kV. 60 distinct operators post-merge · **100 % owner coverage** (from 0 % baseline — best v4.23 outcome cohort-wide) · 168 historical DNSP-alias-normalised (Eandis/Infrax → Fluvius; Tecteo → Resa; original OSM tag preserved for audit trail). Convention #56 zero unresolved.

Audit trail: [preflight](../belgium/v4_23-ingestion-audit-belgium-preflight.yaml) · [fetch](../belgium/v4_23-ingestion-audit-belgium-fetch.yaml) · [merge](../belgium/v4_23-ingestion-audit-belgium-merge.yaml).

---

### 🇨🇱 Chile

**v4.23 refresh (13 July 2026):** Owner attribution + line densification via OpenStreetMap Overpass API (ODbL) + Chile-specific latitude-band region geofence (5th v4.23 fallback class — first LatAm-cluster country). Post-2017 SEN unified national grid (SIC + SING merger via **CEN**). Fragmented transmission ownership: **TRANSELEC** ~60 % dominant EHV + **ISA InterChile** ~40 % (500 kV backbone) + IPPs. 6 primary DSOs by lat-band: **Enel Distribución** (Metropolitana Santiago, formerly Chilectra pre-2018), **Chilquinta** (Valparaíso), **Frontel** (Araucanía), **SAESA** (Los Ríos + Los Lagos), **Edelaysén** (Aysén), **Edelmag** (Magallanes). **CGE Distribución** nationwide default (9 remaining regions). 127 distinct operators post-merge (richest cohort diversity — includes mining industrial owners Codelco/Escondida/Collahuasi + generators Colbún/Engie/EFE railway) · **99.9 % owner coverage** (from 0 % baseline) · **0.0 % voltage-mismatch** rate (PERFECT — cleanest cohort-wide) · Convention #56 zero unresolved.

Audit trail: [preflight](../chile/v4_23-ingestion-audit-chile-preflight.yaml) · [fetch](../chile/v4_23-ingestion-audit-chile-fetch.yaml) · [merge](../chile/v4_23-ingestion-audit-chile-merge.yaml).

---

### 🇭🇺 Hungary

**v4.23 refresh (13 July 2026):** Owner attribution + line densification via OpenStreetMap Overpass API (ODbL) + Hungary-specific NUTS-3 code region jurisdiction fallback. Post-2020 E.ON Hungária consolidation of all Hungarian DSOs: **ELMŰ-ÉMÁSZ** (Budapest metro + Pest + Northeast counties HU110/HU120/HU311-HU313/HU321-HU323 — traditional brand preserved by E.ON) + **E.ON Hungária** (Transdanubia + Southern Great Plain, 12 remaining NUTS-3 codes; consolidated national DSO covering former DÉMÁSZ 2018 + Innogy 2019 + 3× E.ON regional). TSO **MAVIR** operates 220/400 kV EHV backbone (state-owned; 132 kV is HV DSO tier). 72 distinct operators including state industrials (NKM + MOL) + rail (MÁV + BKV) · **99.9 % owner coverage** (from 0 % baseline — 4th cohort-country at near-100 %) · 0.03 % voltage-mismatch (2nd cleanest after Chile 0.0 %) · 501 accent-insensitive alias normalisations (biggest cohort-wide — ELMŰ/ELMÜ/ELMU variants + Hungarian legal entity forms) · Convention #56 zero unresolved.

Audit trail: [preflight](../hungary/v4_23-ingestion-audit-hungary-preflight.yaml) · [fetch](../hungary/v4_23-ingestion-audit-hungary-fetch.yaml) · [merge](../hungary/v4_23-ingestion-audit-hungary-merge.yaml).

---

### 🇳🇱 Netherlands

**v4.23 refresh (13 July 2026):** Owner attribution via OpenStreetMap Overpass API (ODbL) + Netherlands-specific 12-province jurisdiction fallback. Post-2011 splitsingswet DSO architecture: **Liander** (4 provinces — Noord-Holland/Gelderland/Friesland/Flevoland), **Stedin** (3 provinces — Zuid-Holland/Utrecht/Zeeland via Enduris subsidiary), **Enexis** (5 provinces — Overijssel/Drenthe/Groningen/Noord-Brabant/Limburg), plus 3 small regional DSOs geofence-resolved (**Coteq** Almelo, **Rendo** Zwolle/Steenwijk, **Westland Infra** horticultural). TSO **TenneT** ≥110 kV. 60 distinct operators post-merge · **100 % owner coverage** (from 0 % baseline; 2nd cohort-country to reach full attribution after Belgium) · 0.6 % voltage-mismatch rate (cleanest cohort-wide) · Convention #56 zero unresolved.

Audit trail: [preflight](../netherlands/v4_23-ingestion-audit-netherlands-preflight.yaml) · [fetch](../netherlands/v4_23-ingestion-audit-netherlands-fetch.yaml) · [merge](../netherlands/v4_23-ingestion-audit-netherlands-merge.yaml).

---

## Wave 2 continuation + Wave 3 refresh cycles — mid-July 2026

> Extracted from country landing pages 24 July 2026 (Task #523). These are the follow-on Wave 2 + Wave 3 refresh cycles that landed after the initial 5-country Wave 2 batch (AU/BE/CL/HU/NL, Task #457). Five paragraph-format callouts (LU/CO/SI/CR/IL) + five span-pill callouts (EE/LV/SK/LT/CZ) consolidated here + removed from each country's `index.html` to reduce chrome.

### 🇱🇺 Luxembourg

**v4.23 owner enrichment landed 13 July 2026** — OSM Overpass ingestion + Creos monopoly-class fallback closed the country at 100% owner coverage (Creos 669 · Sudstroum 34 · Ville de Diekirch 11 · Ville d'Ettelbruck 2 · 5 small industrial/joint), 89 → 723 substations (+712%), 628 → 1,343 lines. Second application of Greenland monopoly-class pattern with nested municipal-DSO geofence overlay.

Audit trail: [preflight](../luxembourg/v4_23-ingestion-audit-luxembourg-preflight.yaml) · [fetch](../luxembourg/v4_23-ingestion-audit-luxembourg-fetch.yaml) · [merge](../luxembourg/v4_23-ingestion-audit-luxembourg-merge.yaml).

---

### 🇨🇴 Colombia

**v4.23 owner enrichment landed 13 July 2026** — OSM Overpass ingestion + 4-layer resolver (ISA TSO threshold ≥220 kV + department-name → DSO map + Cali metro Emcali geofence + ISA state-utility default) + baseline-department promotion in merge + Step 5 alias-retighten pass closed the country at 100% owner coverage. 381 → 744 substations (+95%), 2,278 → 2,692 lines. **55 distinct operators** — richest DSO diversity in the cohort yet — reflecting Colombia's post-1994 unbundled electricity market regulated by CREG. Attribution: ISA 321 (43%) + Enel-Codensa 93 + EPM 54 + Afinia 34 + Emcali 27 + Air-e 27 + Chec 26 + Essa 23 + EPSA 17 + EBSA 15 + Enerca 13 + Emsa 10 + 43 more. 6th application of the region-jurisdiction × voltage-class fallback pattern with the LARGEST DSO cardinality yet cohort-wide.

Audit trail: [preflight](../colombia/v4_23-ingestion-audit-colombia-preflight.yaml) · [fetch](../colombia/v4_23-ingestion-audit-colombia-fetch.yaml) · [merge](../colombia/v4_23-ingestion-audit-colombia-merge.yaml).

---

### 🇸🇮 Slovenia

**v4.23 owner enrichment landed 13 July 2026** — OSM Overpass ingestion + 4-layer resolver (ELES TSO threshold ≥110 kV + NUTS-3 map + lat/lon geofence across 5 DSO territories) closed the country at 99.7% owner coverage (Elektro Maribor 661 + Primorska 423 + Ljubljana 299 + Gorenjska 138 + Celje 122 + ELES 60 + 22 small industrial/railway), 157 → 1,731 substations (+1,003%), 4,384 → 4,510 lines. 5th application of the region-jurisdiction × voltage-class fallback pattern, with the empirically-novel Layer 3 lat/lon geofence (OSM Slovenia doesn't populate NUTS-3 tags).

Audit trail: [preflight](../slovenia/v4_23-ingestion-audit-slovenia-preflight.yaml) · [fetch](../slovenia/v4_23-ingestion-audit-slovenia-fetch.yaml) · [merge](../slovenia/v4_23-ingestion-audit-slovenia-merge.yaml).

---

### 🇨🇷 Costa Rica

**v4.23 owner enrichment landed 13 July 2026** — OSM Overpass ingestion + 3-layer monopoly-with-overlay resolver (ICE TSO threshold ≥138 kV + 7-DSO territorial geofence + ICE monopoly default) closed the country at **100% coverage across all three dimensions** (owner + voltage + region) — the FIRST cohort-country to achieve this. Attribution: ICE 138 (81.7%) + CNFL 16 (SJ metro subsidiary) + Coopesantos 6 + Coopelesca 3 + ESPH 3 + Coopeguanacaste 2 + JASEC 1 = 7 distinct operators. 3rd application of the monopoly-class pattern (after Greenland pure + Luxembourg + municipal overlay) with expanded 7-DSO nested overlay depth.

Audit trail: [preflight](../costa-rica/v4_23-ingestion-audit-costa-rica-preflight.yaml) · [fetch](../costa-rica/v4_23-ingestion-audit-costa-rica-fetch.yaml) · [merge](../costa-rica/v4_23-ingestion-audit-costa-rica-merge.yaml).

---

### 🇮🇱 Israel

**v4.23 owner enrichment landed 13 July 2026** — OSM Overpass ingestion + IEC pure-monopoly resolver (Layer 1 TSO threshold ≥161 kV + Layer 2 IEC monopoly default) closed the country at **100% coverage across all three dimensions** (owner + voltage + region) — the 2nd cohort-country to achieve this simultaneously (after Costa Rica). Attribution: IEC 256 (99.6%) + ATM 1 (preserved honestly per Convention #56) = 2 distinct operators. 3rd application of the pure-monopoly-class pattern (after Greenland Nukissiorfiit + Costa Rica ICE though CR extended with 7-DSO overlay). Novel Hebrew Unicode alias normalisation with NFC (חברת חשמל לישראל / חשמל / חברת החשמל).

Audit trail: [preflight](../israel/v4_23-ingestion-audit-israel-preflight.yaml) · [fetch](../israel/v4_23-ingestion-audit-israel-fetch.yaml) · [merge](../israel/v4_23-ingestion-audit-israel-merge.yaml).

---

### 🇪🇪 Estonia

**v4.23 owner-attribution — 100%** (Elering TSO + Elektrilevi monopoly via Eesti Energia state holding, 16 distinct operators, +192% OSM growth, Baltic Trio 2nd instance).

Audit trail: [preflight](../estonia/v4_23-ingestion-audit-estonia-preflight.yaml) · [merge](../estonia/v4_23-ingestion-audit-estonia-merge.yaml).

---

### 🇱🇻 Latvia

**v4.23 owner-attribution — 100%** (AST TSO + Sadales tīkls monopoly via Latvenergo state holding, 6 distinct operators, +281% OSM growth, Baltic Trio empirical completion + Convention #78 sub-convention BINDING promotion event).

Audit trail: [preflight](../latvia/v4_23-ingestion-audit-latvia-preflight.yaml) · [merge](../latvia/v4_23-ingestion-audit-latvia-merge.yaml).

---

### 🇸🇰 Slovakia

**v4.23 owner-attribution — 100%** (SEPS TSO + ZSD/SSD/VSD region-jurisdiction DSO partition via Layer 3 lat/lon geofence, 34 distinct operators, +0.3% OSM growth (Slovak OSM sub-sparse, line-dense), Convention #78 BINDING first-enforcement SUCCESS + NEW Layer 3 geofence sub-convention codified).

Audit trail: [preflight](../slovakia/v4_23-ingestion-audit-slovakia-preflight.yaml) · [merge](../slovakia/v4_23-ingestion-audit-slovakia-merge.yaml).

---

### 🇱🇹 Lithuania

**v4.23 owner-attribution — 100%** (Litgrid TSO + ESO monopoly via EPSO-G state holding, 8 distinct operators cohort-cleanest, +871% OSM growth).

Audit trail: [preflight](../lithuania/v4_23-ingestion-audit-lithuania-preflight.yaml) · [merge](../lithuania/v4_23-ingestion-audit-lithuania-merge.yaml).

---

### 🇨🇿 Czechia

**v4.23 owner-attribution — 100%** (ČEPS TSO + ČEZ Distribuce + EG.D + PRE distribuce Layer 3 lat/lon geofence with Prague-refined bbox per Task #262, +725% OSM growth via 5,178 alias-normalised at fetch time (SECOND-HIGHEST cohort-wide, 8.7× Slovakia; E.ON→EG.D 2021 rebrand LARGEST predecessor class), Convention #78 BINDING 2nd enforcement post-promotion SUCCESS + Layer 3 geofence sub-convention 2nd enforcement post-BINDING; Visegrád Trio 2 of 3 shipped).

Audit trail: [preflight](../czechia/v4_23-ingestion-audit-czechia-preflight.yaml) · [merge](../czechia/v4_23-ingestion-audit-czechia-merge.yaml).

---

## Priority 1-5 gap-closure cycle — Jun-Jul 2026 (originating v4.23 workstream)

> Extracted from country landing pages 22 Jul 2026. These are the ORIGINAL five countries in the `v4_23-gap-audit-2026-07/` workstream — Priority 1 Canada + Priority 2 Norway + Priority 3 Mexico + Priority 4 Austria + Priority 5 Greenland. The Wave 2 batch above (Australia + Belgium + Chile + Hungary + Netherlands) followed as the second cohort.

### 🇨🇦 Canada (Priority 1)

**v4.23 data refresh (13 July 2026):** +1,227 substations via NRCan Atlas + CanVec Res_MGT + NACEI + Yukon Energy + Nova Scotia NSTDB federated multi-source ingest. Full auditability chain in the merge audit YAML — provenance-classed per Convention #56 visibly-honest degradation.

Audit trail: [preflight](../canada/v4_23-ingestion-audit-canada-preflight.yaml) · [merge](../canada/v4_23-ingestion-audit-canada-merge.yaml).

---

### 🇳🇴 Norway (Priority 2)

**v4.23 data refresh (13 July 2026):** +271 substations via NVE Nettanlegg WFS with reverse Discipline #41 line-carries-spenning → endpoint-substation-inherits pattern. Full auditability chain in the merge audit YAML — provenance-classed per Convention #56 visibly-honest degradation.

Audit trail: [merge](../norway/v4_23-ingestion-audit-norway-merge.yaml).

---

### 🇲🇽 Mexico (Priority 3)

**v4.23 data refresh (13 July 2026):** +649 substations via OSM Overpass + CFE-monopoly fallback with industrial self-generation exceptions. Full auditability chain in the merge audit YAML — provenance-classed per Convention #56 visibly-honest degradation.

Audit trail: [merge](../mexico/v4_23-ingestion-audit-mexico-merge.yaml).

---

### 🇦🇹 Austria (Priority 4)

**v4.23 data refresh (13 July 2026):** +13,979 substations +30,132 lines via OSM Overpass (fragmented multi-utility — 9+ distinct DSOs including APG TSO + Wiener Netze + 7 Bundesland utilities + ÖBB railway traction). Full auditability chain in the merge audit YAML — provenance-classed per Convention #56 visibly-honest degradation.

Audit trail: [merge](../austria/v4_23-ingestion-audit-austria-merge.yaml).

---

### 🇬🇱 Greenland (Priority 5)

**v4.23 data refresh (13 July 2026):** +6 substations +3 lines via OSM Overpass + PURE MONOPOLY Nukissiorfiit fallback (100% concentration confirmed empirically). Full auditability chain in the merge audit YAML — provenance-classed per Convention #56 visibly-honest degradation.

Audit trail: [merge](../greenland/v4_23-ingestion-audit-greenland-merge.yaml).

---

## Cohort-wide highlights (extracted from callouts)

| Metric | Best cohort-wide | Country |
|---|---|---|
| Owner coverage (from 0 % baseline) | **100 %** | 🇧🇪 Belgium, 🇳🇱 Netherlands (tied) |
| Voltage-mismatch rate | **0.0 %** | 🇨🇱 Chile |
| Distinct operators post-merge (diversity) | **127** | 🇨🇱 Chile |
| Alias normalisations (accent-insensitive) | **501** | 🇭🇺 Hungary |
| First LatAm-cluster country in Wave 2 | — | 🇨🇱 Chile |

---

## Follow-on (when building the public changelog page)

- Publish as `docs/changelog.html` (or `changelog/index.html`) with the same design DNA as other pages (Playfair Display + Cormorant Garamond, mercury/paper backdrop, terracotta accents on section rules).
- Link from landing `index.html` footer and/or About page under "Methodology transparency" — the audit YAMLs are the source-of-truth citation anchor.
- Consider extending the changelog with Wave 3 + Wave 4 refresh cycles by pulling the same information from the closure YAMLs in `Report Production/` and the `docs/v4_23-gap-audit-2026-07/` workstream deliverables (Canada P1 through US P39).
- Cross-reference from `About_SSI_Index.md` and `REPORTS_FRAMING_KB.md` §8bis "Discipline #79 candidate — data-artifact size handling" (the sharding architecture co-emerged with these refreshes).
