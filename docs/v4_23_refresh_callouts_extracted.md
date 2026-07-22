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
