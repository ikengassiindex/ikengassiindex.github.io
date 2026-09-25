# Mode 2/3 Follow-On Plan — Cross-border audit remediation, second wave

> **Anchor.** Companion to `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` and `PR_CROSS_BORDER_GUARD.md`. Authored 18 June 2026 deep night after the first-wave remediation (Italy topology heal + Austria + Mexico substation filter) closed the failure-mode-1 violators.
>
> **Scope.** Eight remaining countries that exceed the 5 % outside-polygon threshold under the production gate — all are failure mode 2 (coastline precision) or failure mode 3 (overseas territory / maritime polygon gap), NOT failure mode 1 (ingestion overshoot). They require bounds.json refresh + extension, NOT substation removal.
>
> **Posture.** This memo specifies the work; it does not execute it. Each country needs an upstream data acquisition step that is bigger than a single-script remediation. The right execution model is a second-wave PR sequence, one country at a time.

---

## Cohort state after first-wave remediation

| Severity | Count | Countries |
|---|---:|---|
| ✅ CLEAN (post-remediation included) | 17 | austria, belgium, colombia, costa-rica, czechia, estonia, hungary, iceland, ireland, israel, italy, korea, latvia, lithuania, mexico, netherlands, poland, slovakia, slovenia, switzerland, us — many at exact 0.00 % |
| ⚪ MINOR (1-5 %) | 14 | australia 4.96 %, denmark 5.02 %, finland 3.41 %, france 6.58 %, germany 4.70 %, greece 4.30 %, japan 1.47 %, luxembourg 2.20 %, new-zealand 6.48 %, portugal 1.23 %, spain 3.00 %, sweden 3.31 %, turkey 2.22 % — most below 5 % gate threshold; france, new-zealand, denmark just over |
| ⚠ MODERATE (10-30 %) | 3 | chile 11.87 %, norway 22.54 %, uk 19.02 % |
| 🚨 SEVERE (≥ 30 %) | 2 | canada 74.39 %, greenland 83.78 % |

Eight countries violate the 5 % `--strict` threshold: **greenland, canada, norway, uk, chile, france, new-zealand, denmark**.

---

## Per-country diagnosis + remediation plan

### Greenland (83.78 %, max 4.5 km, median 0.87 km) — Mode 2 coastline precision

**Diagnosis.** All rejected substations carry generic OSM IDs (`substation 659787193`) and sit in real Greenlandic regions (`Qeqertalik`, `Avannaata`, `Kujalleq`). Maximum drift is only 4.6 km — every rejection sits within boundary-precision distance of the polygon edge.

The Greenlandic bounds.json polygon is derived from a low-resolution coastline source (likely Natural Earth 110m or 50m) that simplifies the heavily indented fjord coastline into a much smoother boundary. Real Greenlandic substations sit on coastal fjord settlements that the simplified polygon excludes.

**Remediation.** Refresh `greenland/bounds.json` against Natural Earth 10m coastline data (admin0 + coastline layers). Alternative: apply a uniform 5 km tolerance buffer for Greenland (highest in cohort, but defensible given the geography).

**Effort.** Small — ~1 hour. Natural Earth 10m is open-licensed; can be loaded directly via `geopandas` + filtered to Greenland.

**Validation.** Post-refresh, re-run check gate. Expect ≥ 95 % inside.

---

### Canada (74.39 %, max 968.8 km, median 291 km) — Mode 3 territorial polygon gap

**Diagnosis.** 18,587 substations outside. Substations cover all Canadian regions — Manitoba, BC, Newfoundland — but the polygon misses huge areas. Max drift 968 km suggests Arctic islands (Nunavut, NWT high-latitude) entirely absent from bounds.json.

**Remediation.** Extend `canada/bounds.json` to include:
- All 13 provinces + territories (likely some currently missing)
- Northwest Territories (full extent)
- Nunavut (including Ellesmere Island, Baffin Island, Victoria Island)
- Yukon (full extent)
- Newfoundland and Labrador (full extent including Labrador interior)

Source: Statistics Canada Geographic Reference Files (open data, CC-BY) or Natural Earth admin-1 layer.

**Effort.** Medium — ~2-3 hours. Canada's Arctic geography is complex; the polygon needs to include numerous Arctic islands.

**Validation.** Post-refresh, expect ≥ 99 % inside. If still > 5 %, investigate name evidence for cross-border US substations (Detroit-Windsor / Niagara / Alaska panhandle ambiguities).

---

### Norway (22.54 %, max 415.3 km, median 3.2 km) — Mode 2 + 3 (coastline + Svalbard)

**Diagnosis.** Bimodal distribution. Median drift is only 3.2 km (coastline precision — Norwegian fjords are even more indented than Greenland's). But the top tier hits 415 km — that's Svalbard (Spitsbergen archipelago, ~74-81°N).

The current bounds.json includes mainland Norway only. Svalbard is Norwegian territory under the 1920 Spitsbergen Treaty and hosts power infrastructure (Longyearbyen, Sveagruva, Ny-Ålesund).

**Remediation.**
1. Refresh mainland coastline against Natural Earth 10m.
2. Add Svalbard polygon (separate MultiPolygon feature in bounds.json).
3. Consider Jan Mayen if any substations land there.

**Effort.** Small — ~1.5 hours.

**Validation.** Post-refresh, expect ≥ 98 % inside.

---

### UK (19.02 %, max 173 km, median 17 km) — Mode 3 territorial gap

**Diagnosis.** Name evidence shows substations in:
- Northern Ireland (`BSP Tyrone 3102` — Tyrone is a Northern Ireland county) — likely missing from bounds.json
- Possibly Shetland / Orkney (high northern Scottish islands)
- Possibly Crown Dependencies (Isle of Man, Jersey, Guernsey — technically not UK but often included in UK datasets)
- Some 173 km drift cases may be coordinate errors (e.g. mistakenly geocoded substations) — needs investigation

**Remediation.**
1. Verify Northern Ireland is in `uk/bounds.json` — if absent, add.
2. Verify Shetland + Orkney are included.
3. Decide policy on Crown Dependencies (in or out — methodological choice).
4. Identify and quarantine remaining outliers as either real polygon gaps OR upstream coordinate errors.

**Effort.** Medium — ~2 hours including the Crown Dependencies policy decision.

**Validation.** Post-refresh + Northern Ireland addition, expect ≥ 95 % inside.

---

### Chile (11.87 %, max 244.9 km, median 82 km) — Mixed Mode 1 + Mode 3

**Diagnosis.** Name evidence shows two patterns:
- `Subestación MAG 1023` + `Estación Transformadora Río Santa Cruz` — region `Magallanes` — drift 240-245 km. Río Santa Cruz is in Argentinian Patagonia. These look like Argentinian substations misattributed.
- Other `Subestación MAU` (Maule region) and `Loncopué` (Biobío region) — drift 40-80 km. May be Argentinian-side substations near the Andes border.

**Remediation.**
1. Name-evidence sweep against `argentina/ssi-data.json` (if Argentina is in cohort — it's not currently) to confirm misattribution.
2. For the Patagonian-island question: confirm whether the southernmost Chilean territories (Tierra del Fuego south, Diego Ramírez Islands, Antarctic Territory claim) are in `chile/bounds.json`.
3. Apply Mode 1 remediation (filter out) for clearly Argentinian substations; extend bounds.json for legitimate Chilean Patagonian islands.

**Effort.** Medium — ~2 hours including the binary diagnosis on each outlier.

**Validation.** Expect ≥ 95 % inside after remediation.

---

### France (6.58 %, max 287.3 km, median 27 km) — Mode 3 DOM-TOM polygon gap

**Diagnosis.** Top outliers are `Poste Pyrénées-Atlantiques 065/012` in `Nouvelle-Aquitaine` region with 287 km drift. Pyrénées-Atlantiques borders Spain; 287 km drift puts them in central Spain (Madrid area?). May be misattribution or geocode error.

Mid-tier outliers (`Poste Savoie 073` at 27 km) are likely real French substations in Savoie that sit just over the Italian-Swiss-French Alpine border. Boundary precision.

The French overseas departments and territories (Guadeloupe, Martinique, French Guiana, Réunion, Mayotte, Saint-Pierre-et-Miquelon, French Polynesia, New Caledonia, Wallis-and-Futuna) are typically NOT in metropolitan bounds.json — but if any substations land in those territories, they should be included or explicitly scoped out.

**Remediation.**
1. Diagnose top outliers (287 km) — investigate whether Spanish-side ingestion or coordinate error.
2. Refresh bounds.json with high-precision French metropolitan boundary.
3. Decide policy on DOM-TOM inclusion (likely separate per-territory polygons or explicit methodology scope-out).

**Effort.** Medium — ~2 hours.

**Validation.** Expect ≥ 97 % inside.

---

### New Zealand (6.48 %, max 3.8 km, median 0.78 km) — Mode 2 coastline precision

**Diagnosis.** All 101 outliers sit within 3.8 km of the polygon edge, with median 0.78 km. New Zealand's coastline is heavily indented; the bounds.json polygon is too simplified.

**Remediation.** Refresh `new-zealand/bounds.json` against Natural Earth 10m or LINZ (Land Information New Zealand) coastline data.

**Effort.** Small — ~1 hour.

**Validation.** Expect ≥ 99 % inside.

---

### Denmark (5.02 %, max 33.6 km, median 0.8 km) — Mode 2/3 maritime / offshore wind

**Diagnosis.** Top outliers include `Transformerplatform Anholt Havmøllepark` (Anholt offshore wind farm in the Kattegat, between Jutland and Sweden) with drift 27 km. These are Danish offshore wind transformer platforms in Danish territorial waters but NOT in the terrestrial bounds.json.

The 33 km top outlier (`KFA`) needs investigation — could be a substation on a small island OR a coordinate error.

**Remediation.**
1. Extend `denmark/bounds.json` to include Danish territorial waters (12-nautical-mile EEZ buffer) OR add explicit polygons for the major Danish offshore wind farm areas (Anholt, Horns Rev, Kriegers Flak, etc.).
2. Decide methodology policy: are offshore wind farm transformer platforms "Danish substations" for the purposes of the resilience surface? Likely YES, but the methodology brief should state this explicitly.

**Effort.** Small-medium — ~1.5 hours including the methodology policy decision.

**Validation.** Expect ≥ 98 % inside.

---

## Sequencing recommendation

Order by ease + impact:

1. **New Zealand** (Mode 2, ~1 hour) — easy quick win; pure Natural Earth refresh
2. **Greenland** (Mode 2, ~1 hour) — pure Natural Earth refresh + tolerance discussion
3. **Norway** (Mode 2 + 3, ~1.5 hours) — refresh + add Svalbard polygon
4. **Denmark** (Mode 2/3, ~1.5 hours) — refresh + offshore wind policy decision
5. **France** (Mode 3, ~2 hours) — refresh + DOM-TOM policy decision + diagnose 287 km outliers
6. **UK** (Mode 3, ~2 hours) — Northern Ireland addition + Crown Dependencies policy
7. **Chile** (Mixed, ~2 hours) — Patagonian polygon + Argentinian-substation filter
8. **Canada** (Mode 3, ~3 hours) — full Arctic territorial extension

Total estimated effort: 12-15 hours of focused work across all 8 countries.

---

## Aggregate cohort impact

Before any second-wave remediation, the cohort substation total is 174,046. After all eight Mode 2/3 fixes, the headline number stays the same (no substations removed — only bounds.json extended/refreshed). The change is in the verification rate:

| State | Total subs | Verifiably inside | % verified |
|---|---:|---:|---:|
| Pre-first-wave (18 Jun audit) | 174,046 | ≈ 149,396 | 85.8 % |
| Post-first-wave (Italy heal + Austria + Mexico fix) | 172,677 (−1,369) | 149,396 | 86.5 % |
| Post-second-wave (8 Mode-2/3 polygon fixes) | 172,677 | ≈ 170,000 | ≥ 98 % |

The brief's 174,046 headline becomes 172,677 after first-wave remediation. After second-wave, the verifiability moves from 86 % to ≥ 98 % — methodologically defensible against any hostile reviewer.

---

## Required external data sources

For the second-wave work:

| Source | Purpose | Licence | URL |
|---|---|---|---|
| Natural Earth 10m admin-0 + admin-1 | High-resolution country + first-level polygons | Public domain | https://www.naturalearthdata.com/downloads/10m-cultural-vectors/ |
| Natural Earth 10m coastline | High-resolution coastline | Public domain | https://www.naturalearthdata.com/downloads/10m-physical-vectors/ |
| OpenStreetMap admin boundaries | Country-cadastral-grade boundaries | ODbL | https://overpass-turbo.eu (or osm2pgsql extracts) |
| GeoBoundaries v6 | Cleaner per-country sub-national boundaries | CC-BY | https://www.geoboundaries.org/ |
| Marine Regions (Flanders Marine Institute) | EEZ + territorial waters polygons | CC-BY | https://www.marineregions.org |
| Statistics Canada GRF | Canadian provinces + territories | Statistics Canada Open Licence | https://www.statcan.gc.ca |
| INSEE COG | French metropolitan + DOM-TOM | INSEE Open Data | https://www.insee.fr |
| OS Open Boundaries | UK administrative boundaries inc. NI | OS OpenData | https://www.ordnancesurvey.co.uk |

All are open-licensed and reusable under SSI Index CC BY-SA 4.0 output licence.

---

## Methodology questions for operator decision

Several second-wave fixes raise methodology policy questions:

1. **Greenland coastline precision tolerance.** Apply a uniform 5 km buffer for all coastal-precision countries, OR refresh each country's bounds.json individually with high-resolution coastline? The buffer is simpler; the refresh is more accurate but per-country work.

2. **UK Crown Dependencies.** Isle of Man, Jersey, Guernsey are not UK but often included in UK datasets. Should the SSI Index methodology include them as "UK substations" or scope them out? (They have their own governance — Jersey is the largest at 100k population.)

3. **France DOM-TOM scope.** Should overseas territories be included as French substations (population 2.7M across all DOM-TOM)? If yes, separate polygons; if no, explicit scope-out statement in methodology brief.

4. **Denmark + Greenland relationship.** Greenland is constitutionally part of the Kingdom of Denmark but has its own canonical (`greenland/`). Are offshore wind farms between Denmark and Greenland coded under Denmark, Greenland, or split?

5. **Canadian Arctic / Norwegian Svalbard scope.** Are Arctic-territory substations included or explicitly scoped out as "post-2031 forecast-horizon issue"?

These belong to operator decision — the technical fixes are independent of the methodology policy on each.

---

## Companion artifacts

- `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` — original audit memo (the discovery)
- `PR_CROSS_BORDER_GUARD.md` — first-wave PR description (gate + filter + Italy heal)
- `scripts/check_cross_border.py` — deploy-gate (already shipped)
- `scripts/remediate_cross_border.py` — substation filter (already shipped, used for Austria + Mexico)
- `scripts/pipeline/utils/geo.py` — helper functions (already shipped)
- `austria/ingestion_rejected_20260618T201324Z.json` — 665 Austrian rejects (audit trail)
- `mexico/ingestion_rejected_20260618T201601Z.json` — 704 Mexican rejects (audit trail)

For second-wave work, a new script `scripts/refresh_bounds.py` would be the natural home — one country at a time, takes an external GeoJSON or Natural Earth slice, validates, healing topology, writes the country's bounds.json.

---

*MODE_2_3_FOLLOWON_PLAN.md v1 · authored 18 June 2026 deep night · second-wave remediation plan · CC BY-SA 4.0*
