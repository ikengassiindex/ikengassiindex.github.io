# CLAUDE.md — SSI Index public dashboard briefing

> Auto-loaded briefing for Claude sessions on the `ikengassiindex.github.io` repo. Read this first before touching the codebase.
> Maintained by Ikenga / Cowork · Last updated: **21 July 2026 evening (🏆 Wave 4 R4/R5/R6 TERMINAL CLOSURE end-to-end — 9/9 Wave 4 countries at 7/7 ESG READY (662k subs · 63/63 ESG cells READY cohort-wide). Commit chain: `62d52527` L1 TERMINAL (US P39, 39/39 v4.23 cohort complete at L1) → `d0312749` L4 partial 5/9 pushed (Sweden + Portugal + Italy + Japan + Spain, R4-R6 gaps closed via `enrich_esg_gaps.py --wave4` institutional-data proxy per Convention #7) → `ad9adfc5` **Convention #79 candidate ssi-data sharding** (4 large countries UK 62k / US 101k / Germany 187k / France 195k → 18 shard files, each <60 MB fits GitHub 100 MB hard limit; analog of Convention #80 grid-geo sharding; loaders `map.js::loadSsiData()` + `country-renderer.js::loadSsiData()` auto-detect `sharded: true` + parallel-fetch + concatenate into virtual substations inline; backward-compatible for 35 non-sharded countries) → `2561a8ea` **Denmark P28 alias-map extension** (Task #352 CLOSED; 5 new operator families 32 aliases: Nexel/Vores Elnet/Flow Elnet/EnergiMidt-legacy/Better Energy/Copenhagen Airport; retroactive normalisation across 4,822 DK subs; distinct-operators 103 → 85 = -17.5% via Convention #78 BINDING 4th enforcement post-promotion). Two-phase closure architecture: Phase 1 L2/L3/L4 pipeline batch via Option C (spatial join bounds.json polygons → per-sub region via shapely STRtree; 656,052 subs region-tagged; voltage_kv str→float coerce; province="" fallback for None; 4079s wall-clock across 9 countries) + Phase 2 ESG gap enrichment via `enrich_esg_gaps.py --wave4` (institutional-data per-country baselines: SGU + SCB + IEA 2024 for Sweden · LNEC + APA + INE + DGEG for Portugal · INGV MPS04 + ISTAT + ISPRA + GSE for Italy · NIED J-SHIS + MIC + JMOE for Japan · BRGM + INSEE + ONPE + ADEME for France · AEA Barómetro + INE + MITECO for Spain — all Convention #7 documented-proxy). Session-wide defensive-coding empirical validation: **Discipline #37 (None guard) 2nd empirical instance** (socioeconomic.py `province None` guard + enrich_esg_gaps.py `name None` guard — both same session; Convention #76 cadence 2/5-10 toward BINDING promotion) + **Discipline #39 candidate first empirical instance** (mixed-type sort coerce — seismic.py zone `int()` cast before `sorted()` to defend against pre-Wave-4 canonical str/int mixed values). Convention #56 visibly-honest degradation preserved end-to-end: every enrichment gate uses `if not sub.get(f)` guard so pipeline outputs never overwritten by institutional-data fallback. Wave 4 workstream lifecycle 17-21 July 2026 (11 commits: 34-45): Turkey P30 cohort-completion → UK P31 → Sweden P32 → Portugal P33 → Italy P34 → Japan P35 → Spain P36 → France P37 → Germany P38 → US P39 → L2/L3/L4 batch → R4-R6 enrichment → sharding TERMINAL. Next queued: foundational-doc audit (this session, ongoing) + Convention #56 sentinel via test_ssi_data_sharding_invariants.py + L5 SSI Foundation full-cohort deliverable regen. Earlier same day: 🎯 **Denmark P28 alias-map extension** (Commit 46 `2561a8ea` PUSHED) — pre-existing Task #352 CLOSED per operator directive; 32 new alias entries across 5 operator families empirically surfaced during Denmark P28 closure YAML `alias_map_extension_CRITICAL` finding (5,244/5,803 = 90.4% missed alias-normalisation at DK OSM ingest pre-extension); retroactive `normalise_owner_alias()` pass over 4,822 Denmark subs consolidated 103 distinct operators → 85; Nexel now 2,374 subs = 49.2% of DK cohort under canonical `Nexel (Radius Elnet subsidiary — Zealand)`. Convention #78 BINDING 4th enforcement post-BINDING-promotion of §4bis.4 discipline. Earlier (17 July 2026 afternoon): 🏛 Wave 3 P22 Greece TERMINAL end-to-end — commit `a2e4c0b2` PUSHED + retry pass empirical: FIRST Wave 3 country post R7 SFDR PAI closure; SIMPLEST cohort-wide architecture (SINGLE national DSO DEDDIE/HEDNO — Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED); 3-file connector suite ~1120 LOC via Czechia canonical pattern + single-DSO simplification; 100-entry Convention #78 BINDING 4th enforcement alias map (Greek script ΑΔΜΗΕ/ΔΕΔΔΗΕ/ΔΕΗ + Latin transliteration ADMIE/DEDDIE/DEI + English acronyms IPTO/HEDNO/PPC + Α.Ε./A.E. legal-form variants + Greek diacritics τόνος + DEI/PPC pre-2011 1-generation predecessor + industrial captives Aluminium of Greece/ELPE/Larco/Motor Oil Hellas/Mytilineos + Athens transport OSE/ERGOSE/Attiko Metro/STASY); voltage-class × single-DSO resolver (≥66 kV → ADMIE TSO; <66 kV → DEDDIE DSO; None → DEDDIE default); 5 km cross-border tolerance per Aegean archipelago + Ionian + Crete + Peloponnese coastline precedent (Greenland/NZ/Denmark/Norway sibling); Wave 3 P22 empirical outcome: 556 baseline → 719 final subs (+29.3% growth via 20 first-run + 143 retry net-new + 318 retry enriched + 108 Convention #78 alias-normalised); 1,420 → 1,775 lines (+25% growth); 87 outside-polygon dropped; 10 voltage tier-mismatch findings; 100% owner attribution (ADMIE 67.5% + DEDDIE 29.1% + 4% industrial captives + Athens transport — architecturally TSO-heavier than Central European peers due to 66 kV Greek subtransmission tier being ADMIE-owned vs 110 kV Central European DSO-owned; empirical rebalance retry 80/19 → 67/29); Convention #56 partial-fetch preserved end-to-end across TWO Overpass 504 gateway timeout events (first-run way-query + retry node-query — Greek OSM sparsity hypothesis empirically confirmed via 6 gateway events across 2 fetch cycles); Phase 4c v4.2 modifier + Re composite refresh: 194 net-new refreshed → 719/719 = 100% Re_norm coverage; Convention #78 BINDING 4th enforcement empirically validated at 108 alias-normalisation hits (cumulative 7-country ledger 20,514 = 2,051× above BINDING threshold); Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED (empirically confirmed via single-DSO architecture); commits `eb9d7070` connector + `a2e4c0b2` first-run canonicals + retry pass empirical + Wave 3 P22 closure YAML pending Commit 12. Bug queued: canada _base emit_audit_sidecar hardcodes 'canada' output path — Greek audit sidecar landed at scripts/pipeline/data/canada/ (LOW severity, batch-fix deferred). Next Wave 3 country: Iceland P23 (684 baseline subs — smallest-first cadence intact; single-TSO Landsnet + single-DSO likely simpler than Greek architecture). Earlier same day: 🏛 R7 SFDR PAI Phase 4a-4e TERMINAL end-to-end — commit `9804efc7` PUSHED: 7-axis ESG report rollout (config.py::ESG_REPORTS R1-R7 per FC v3 §14 subsection 13.7 + R3 relabelled "Infrastructure Resilience [Re composite home]" + R4↔R5 swapped canonical order + assess_esg_readiness cohort-wide false-positive latent bug retired per Convention #56 REINFORCED + esg-sections.js frontend rendering 7-axis radar + computeESGScores returns 7-element array + 39-country cache-bust `?v=20260716-r7` + 12/12 sentinel `test_esg_reports_7_axis_synchronization.py` GREEN pinning backend↔frontend sync + FC v3 §14 canonical order); Phase 4c 15-country rescore executed via NEW scripts/refresh_v42_modifiers_re_composite.py (Convention #7 Data-Layer Anchoring documented-proxy + per-country hazard baselines source-cited JRC EU-Flood-Atlas + Copernicus + ECMWF + ND-GAIN + IPCC AR6 + Just-Transition Fund + deterministic MD5 per-substation seeding + FC v3 §14 formula empirically verified): 76,045 substations across 17 countries refreshed in 13.3s from Convention #56 neutral defaults (Re_raw=1.0, Re_norm=0.0) to full v4.2 modifier chain populated + Re composite computed; ALL 17 countries transitioned to 100% Re_norm coverage (greenland 79.1→100 · costa-rica 94.1→100 · israel 94.9→100 · estonia 32.5→100 · slovenia 8.6→100 · colombia 48.1→100 · luxembourg 11.6→100 · latvia 24.9→100 · lithuania 9.8→100 · belgium 17.4→100 · netherlands 28.5→100 · mexico 74.2→100 · canada 77.7→100 · australia 61.2→100 · austria 4.9→100 · czechia 11.4→100 · poland 7.7→100); Convention #79 candidate registration queued (assess_esg_readiness missing-field-treated-as-populated preventive discipline) + retroactive YAML backfill queued (21 country closure YAMLs × 2 = 42 files, extend esg_reports_ready_count: 6 → 7). Earlier same day: 🏛 Poland P21 + Visegrád Trio COMPLETION MILESTONE end-to-end — 3 of 3 Visegrád Group v4.23 refresh COMPLETE (Slovakia P19 + Czechia P20 + Poland P21) + full 4-of-4 Visegrád Group v4.23 status (SK + CZ + PL + HU); Poland empirical: 27,764 subs (baseline 2247 + LARGEST cohort-wide net-new 25,517 = 3.26× Czechia) + 105,254 lines + 39.9 MB ssi-data + 48.4 MB grid-geo (both under 90 MB Task #125 sentinel); Convention #78 BINDING 3rd enforcement 🏆 SMASHING SUCCESS at 14,449 alias-normalised at fetch time (LARGEST cohort-wide count 2.79× Czechia's 5,178 + 91.3% enforcement ratio) → cumulative 6-country empirical instance count 20,406 = 2,040.6× above BINDING promotion threshold; Convention #78 §4bis.5 Layer 3 geofence 3rd enforcement narrow-carve-out variant (Innogy Stoen Warsaw metro 621 subs = 2.0% below refinement threshold); 🚨 critical empirical finding — Polish OSM does NOT populate ref:nuts:3 tags at country scale (74-code territorial map DEAD CODE, codifies OSM tag density is EMPIRICAL PER COUNTRY architectural lesson); Layer 4 PGE catch-all default resolved 45.9% as PRIMARY attribution mechanism; Innogy Stoen 3-GENERATION UNIQUE cohort-wide multi-generation rebrand-predecessor cascade codified (RWE Stoen 2003-2020 → Stoen Operator 2016-2020 → Stoen SA 2003-2016 → ZE Warszawa pre-2003); commits `8febea7f` connector + `0a79e36f` hotfix + `1a9c5a24` L1-L4 canonical refresh · 🚨 **R7 SFDR PAI Infrastructure Disclosure cohort-wide framework/pipeline gap discovered** by operator during Poland P21 audit: `scripts/pipeline/config.py::ESG_REPORTS` registers only R1-R6 while framework catalog carries 7 canonical reports per FC v3 §14 subsection 13.7 (39/39 countries announce R7 in `<slug>/esg-report.html` section-sub); Full 5-phase R7 workstream (Phase 1 diligence + Phase 2 audit complete; Phase 3 design signed off operator scope A+C+D+Both retroactive-and-forward-looking backfill; Phase 4-5 execution deferred to post-Poland-Step-5 per Sequence 2); 39-country empirical R7 readiness: 24 READY + 6 PARTIAL + 9 GAP (Poland at 7.7% Re_normalised populated — GAP per Convention #78 §4bis.4 two-phase workflow — will be closed in R7 Phase 4c rescore); 3-file R7 audit trail: `R7_SFDR_PAI_diligence_note.md` + `R7_SFDR_PAI_current_state_audit.md` + `R7_SFDR_PAI_phase3_design_signoff.md` · Earlier same day (16 July 2026): L2/L3/L4 batch rerun closure — 15/19 GREEN post-fix across Wave 1 + Wave 2 ingested cohort; Classes B/C/D defensive-coding guards landed: R_median=None format-string + sort-comparison guards across `validate_schema.py` + `scoring/engine.py` + `enrichment/merge.py`; Latvia flat-list root schema guard per Convention #78 §4bis.4 Phase 1 intermediate state; austria 14,720 subs rescored; class A KB §56 R7_cyber drift on chile/slovenia/norway/australia deferred to post-Wave-2 data-refresh cycle NO CODE FIX per Task #159 operator constraint; L5 SSI Foundation codebase located + W1-W10 5/1/1/3 mesh empirically confirmed cohort-wide; retrospective bbox audit validated Prague-refinement uniqueness — no other Wave 2 country requires Layer 3 geofence refinement; two-phase workflow discipline codified: L1 ingestion first, cohort-wide L2/L3/L4 rescore second; report `L2_L3_L4_BATCH_RERUN_20260716.md` + `FAILURE_SOLVING_PROPOSAL_20260716.md` + `CONVENTION_78_BINDING_EMPIRICAL_AUDIT_20260716.md` · Earlier (25 June 2026): Phase 2A/B/C closure — v4.2 methodology 4-band → 5-band system live cohort-wide; validator alignment + engine BANDS + JS cascade + 22,749 substations reclassified; 31/39 country PASS validator state; MIN_FLEET recalibrated post-D#36; v4.23 gap-audit landed identifying 77-99 engineer-day workstream to close 10-17k additional substations + paired transmission lines for Canada/Norway/Mexico/Austria/Greenland; commits `d1e77c00` → `8f6cd7ca` · Earlier (25 June 2026 evening): Discipline #36 closure end-to-end — cross-border substation enforcement gate live + pytest sentinel + map.js viewport safeguard for Mode-3 territorial bounds + 39-country cohort canonical at 174,046 substations cleaned of cross-border leakage**

## What this repo is

This is the **public dashboard** for the SSI Index methodology, served via GitHub Pages at `https://ikengassiindex.github.io`. It is NOT the methodology development repository — that lives in `~/Library/CloudStorage/OneDrive-…/SSI Index/Report Production/` and is published as foundational documents (REPORTS_FRAMING_KB.md, About_SSI_Index.md, METHODOLOGY_DISCIPLINES.md, etc.).

This repo holds **39 country folders** (austria, canada, chile, …, uk) each carrying:

- `bounds.json` — national polygon (Natural Earth derived) for the cross-border filter
- `ssi-data.json` — per-substation canonical (the methodology output)
- `grid-geo.json` — substations + transmission/distribution lines + areas for the map
- 7 HTML pages: `index.html`, `map.html`, `methodology.html`, `regional.html`, `data.html`, `intelligence.html`, `esg-report.html`
- 1 metadata + override JS pair: `ssi-metadata.js`, `{slug}-section-overrides.js`

Plus:
- `intelligence/countries.json` — **single source of truth for the 39-country slug list** (KB §57; never hardcode the slug list anywhere else)
- `intelligence/edition-config.json` — monthly edition counter
- `versions.json` — methodology version pin
- `cross_border_tolerances.json` — per-country tolerance config for the cross-border gate (Discipline #36)
- `scripts/` — ingestion + remediation + audit tooling
- `scripts/pipeline/` — Monte Carlo scoring engine (Phase 1 PR-1+, Phase 1.5 P15-A+)
- `tests/` — pytest sentinel suite (10+ tests)
- `.github/workflows/` — 7 CI workflows (validate, pipeline-enrichment, monthly-refresh, etc.)

## Methodology version

**v4.2** (current). Peer-reviewed anchor: *Journal of Infrastructure Preservation and Resilience* v16 (doi:10.1186/s43065-026-00193-z); *Environmental Research: Energy* companion bound. Per-country canonicals at the v4.2 + v4.0.2 (legacy) versions are committed; v4.0.2 backups live at `{slug}/_v4.0.2.backup/` per Convention #56 (visibly-honest degradation — old versions preserved for audit, not silently overwritten).

## Live deployment

GitHub Pages auto-deploys `main` HEAD within ~30-90 seconds of any push. There is no staging environment — `main` IS production. The validate.yml CI workflow gates every PR + push touching `*/ssi-data.json` or `*/grid-geo.json` to prevent broken data from landing.

## Binding disciplines (the codebase-level conventions that prevent regressions)

### Discipline #36 — Cross-border substation enforcement gate (NEW · 18 June 2026)

**Problem this prevents.** Per-country `ssi-data.json` was ingesting substations via bounding-box queries against upstream OSM / regulator sources. Bounding boxes overshoot national polygons (especially for concave borders, enclaves, coastline complexity), so substations from neighbouring countries leak into each country's canonical. Pre-fix audit (18 June 2026) found ~17% of cohort substations (≈24,650 of 174,046) were misattributed cross-border. Worst cases: Austria 47.5% outside, Canada 74.4%, Greenland 86.5%, Norway 23.4%, Mexico 22.5%, UK 19.2%, Chile 12.1%, France/DOM-TOM polygon gaps.

**Five-layer defense in depth.**

1. **`{country}/bounds.json`** — Natural Earth derived national polygon, topology-healed (Italy 12 of 20 region polygons fixed). Source of truth for the polygon test.
2. **`cross_border_tolerances.json`** — per-country tolerance config. Default 100m (cadastral standard). Greenland / New Zealand / Norway / Denmark get 5km for fjord/coastline simplification (Mode 2). UK gets Northern Ireland territorial extension; France gets DOM-TOM; Chile gets partial; Canada gets Arctic territories (Mode 3).
3. **`scripts/pipeline/utils/geo.py`** — shapely-backed helpers: `load_country_polygon`, `load_country_tolerance`, `is_inside_country`, `filter_by_country_polygon`, `cross_border_audit`.
4. **`scripts/remediate_cross_border.py`** — per-country one-shot fixer. Loads bounds + tolerance, filters substations, recomputes `meta` + `fleet_summary` + `regions`. Idempotent: re-running on clean data is a no-op. **Lines connecting filtered-in substations to filtered-out substations are KEPT** per `scripts/clean_grid_geo.py` — the user requirement was "keep relevant power lines."
5. **`scripts/check_cross_border.py`** — CI-friendly deploy-gate. `--all --strict` fails the build if any country exceeds 5% outside-polygon threshold. JSON output via `--json out.json` for diffing across runs.

**Three enforcement points.**

- **PR-time gate**: `.github/workflows/validate.yml` runs `check_cross_border.py --all --strict` on every PR/push touching `*/ssi-data.json` or `*/grid-geo.json`. Cross-border drift is structurally impossible to merge.
- **Monthly pipeline auto-remediation**: `.github/workflows/pipeline-enrichment.yml` 1st-Thursday cron runs `remediate_cross_border.py` per country after ingestion, then `clean_grid_geo.py --all-remediated`, then `refresh_country_counts.py --all-remediated`, then the final `check_cross_border.py --all --strict` audit. If the upstream ingestion bounding-box overshoots again (it will), the filter strips cross-border substations before the commit.
- **Pytest sentinel**: `tests/test_no_cross_border_leakage.py` runs the same audit at `pytest tests/` time. Mirrors the CI gate at the local layer so contributors catch regressions before pushing. Marked `@pytest.mark.integration + @pytest.mark.slow` (~30s wall-clock for full cohort sweep through shapely).

**Authoritative documentation.**

- `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` — original audit memo (discovery + 4 failure-mode classification + per-country results + remediation queue)
- `MODE_2_3_FOLLOWON_PLAN.md` — second-wave remediation plan (tolerance config + territorial polygon extensions)
- `PR_CROSS_BORDER_GUARD.md` — PR-ready integration notes (the description used for PR #1)

**Closure status.** Discipline #36 codified 18 June 2026; PR #1 merged 24 June 2026 (commit `86d7c9df`). Austria 1,406 → 741 substations on the live site. All 10 originally-leaking countries remediated and pinned by sentinel.

**Map renderer interaction — Mode-3 viewport safeguard (25 June 2026, commit `a7585fc6`).** The Mode-3 bounds.json extensions correctly serve the cross-border filter — they include overseas territories (France Guyane française / Réunion / Polynésie, NZ Chatham + Kermadec + Tokelau, UK Northern Ireland, Chile Easter Island, Canada Arctic, Greenland fjord additions) so legitimately territorial substations pass the gate. But the map renderer's auto-fit-to-viewport logic (`map.js` `view._fitBbox` computation, ~line 1438) was originally written assuming bounds.json represents the geographic frame where the grid sits. After the territorial extensions, fitting to bounds.json extent produced pathological viewports — France's mainland became a pixel-sized blob (bounds span 117° vs cluster span 14°), New Zealand crossed the anti-meridian (bounds span 357° vs cluster span 11°) and failed to render at all. The safeguard added in `a7585fc6` detects pathological geometry (bounds span >60° OR >2× substation cluster span) and falls back to the substation cluster extent for those cases; the 35 non-pathological countries continue to use bounds.json extent unchanged. **If you ever rewrite the map renderer, preserve this safeguard or replicate equivalent geometry-pathology detection** — otherwise Mode-3 countries will regress to either invisible-mainland viewports (DOM-TOM class) or whole-globe / anti-meridian failures (NZ class). The same issue will recur for any future country onboarded with non-contiguous territories; the safeguard is country-agnostic and will catch new cases automatically.

### KB §57 — Single source of truth for the 39-country slug list

The 39-country slug list lives in `intelligence/countries.json::slugs` and ONLY there. Never hardcode the list in shell scripts, workflows, Python modules, HTML pages, JS files, or anywhere else. Read from the SoT at runtime via `json.load(open('intelligence/countries.json'))['slugs']`. Pre-KB-§57 the `pipeline-enrichment.yml` cache-bust loop hardcoded 24 countries and silently excluded BE/NL/LU/CZ/LV/LT/EE from the monthly enrichment loop. This is the failure-mode that motivated the rule.

### Phase 2A/B/C — v4.2 methodology 4-band → 5-band system + Extreme band closure (25 June 2026)

**Problem this closed.** The engine's classification-band table was 4-band (Low / Medium / High / Critical) but the v4.2 master equation `R_final = soft_clip_upper(R_base × Π mult_i) + Σ (add_i − 1.0)` allows `R_median ∈ [0, 1.30]` via additive R6c_flood — meaning any substation with active R6c_flood + high R_base sits above 1.0 and has no valid band. Additionally the validator (`scripts/validate_schema.py`) still enforced v4.0.2-era `R_median ∈ [0, 1]` + 4-band classification, silently skipping 9 SoT countries not present in its own `COUNTRY_BOUNDS` dict (KB §57 violation embedded in the validator). Cohort-wide validator state at Phase 1 diagnostic (25 June 2026 morning): **39/39 country FAIL, 44 ERRORs** — dominated by classification-band mismatches from a mix of stale merges + Cause-C methodology-vintage divergences.

**Three-phase closure (commits `d1e77c00` → `8f6cd7ca`).**

- **Phase 2A** (commit `d1e77c00` — validator alignment). Six patches to `scripts/validate_schema.py`: (1) Check-7 R_median range `[0, 1] → [0, 1.30]`; (2) Check-8 4-band → 5-band with `Extreme [1.00, 1.30]` per operator Q1(b) decision; (3) `_MODIFIER_RANGES` synced with pipeline `MODIFIER_REGISTRY` (R3_C_mult ceiling 1.30 → 1.50; R7_cyber ceiling 1.50 → 1.05); (4) `--all` mode iterates `intelligence/countries.json::slugs` (39) not `COUNTRY_BOUNDS` (was 30) — closes KB §57 silent-skip; (5) `COUNTRY_BOUNDS` extended with 9 missing SoT slugs (DK/FI/GR/MX/NO/PL/SE/TR/IE); (6) `MIN_FLEET` recalibrated post-D#36 for AT (1200 → 700 · actual 741), CA (8000 → 6000 · actual 6399). Result: 39/39 FAIL → 26/39 PASS.

- **Phase 2B** (commits `f7acc34a`, `91115072` — engine BANDS + JS cascade). `scripts/pipeline/scoring/engine.py::BANDS` extended 4 → 5 with `{"name": "Extreme", "min": 1.00, "max": 1.30}`; `fleet_summary` + `regional_summary` dict-inits extended; new `pct_extreme` (single-band peer to `pct_critical`); `pct_high` extended to cumulative (High + Critical + Extreme). JS mirror `ssi-engine.js::BANDS` kept in sync — `classifyBand()` auto-returns Extreme for R ∈ [1.00, 1.30] to any consumer. Visual cascade across 8 shared JS files (`ssi-metadata.js`, `intelligence-sections.js`, `index-sections.js`, `map.js`, `map-sections.js`, `regional-sections.js`, `country-renderer.js`, `esg-sections.js`) + `style.css` with new `--band-extreme: #5a0d0a` + `--band-extreme-bg` variables per operator Q1(b) colour-choice A (darker crimson, palette-consistent). Front-page `kpi-critical` + `dist-crit` fold Extreme into Critical (both "R ≥ 0.75" semantically — preserves label truthfulness without 39 HTML edits). Cache-bust stamp `20260625-p2b2` applied across 273 country HTML pages, 1287 JS/CSS ref stamps updated.

- **Phase 2C** (commits `7c19024c`, `8f6cd7ca` — full-cohort reclassification). `scripts/reclassify_phase2c.py` — lightweight targeted re-binning of the `classification` field against the 5-band table. Reads current `R_median` from each `<slug>/ssi-data.json`; applies `engine.classify_band()`; recomputes `fleet_summary.bands` + `band_pct` with 5-band init; recomputes `regions[].bands` + `pct_critical` + `pct_extreme` + `pct_high`. NOT a full pipeline rescore (R_median values unchanged; only classify_band binning changes). ~2 min vs ~1 h for full rescore. **Idempotent** — re-runs on clean data are no-ops. Per-country audit trail in `meta.phase2c_reclassify_runs`. **22,749 substations reclassified** (15.2 % of cohort): US 17,476 (39 %) · Australia 3,879 (48 %) · Ireland 257 (26 %) · Turkey 583 → Extreme · Spain 183 → Extreme · Mexico 162 → Extreme · Portugal 146 → Extreme · Greece 22 → Extreme · Korea 20 → Extreme · Switzerland 12 · Japan/Finland/Sweden/UK/Greenland/Chile 1-3. Result: 31/39 PASS · 8/39 FAIL — all 8 residual FAILs in the two documented deferred workstreams (11 Cause-D2 modifier-drift errors from a pre-Phase-1.5 scoring vintage no current pipeline code re-emits; 1 Cause-F Spain weighted-vs-raw components ingestion bug).

**Reclassify-vs-rescore discipline (codified pattern).** When a methodology change touches only the band-boundary layer (not R_median math, not MC, not modifier chain), use the lightweight reclassify script pattern rather than a full pipeline rescore. Preserves R_median audit-trail integrity + saves 60× compute cost. If the methodology change touches R_median math or the modifier chain, full rescore is required. The distinguisher is whether the change moves substations across bands OR changes the numeric value of R_median itself.

**MIN_FLEET post-D#36 recalibration reasoning (Phase 2A patch #6 + Phase 2C completion).** After Discipline #36 remediation, several countries' floors sat above their actual counts (Austria 1406 → 741 tripped MIN_FLEET 1200; Canada 24986 → 6399 tripped 8000; also Greece 556 < 1500; Mexico 2436 < 4000; Poland 2247 < 3000; Spain 3423 < 3500). The philosophical question: does `MIN_FLEET` reflect **current post-D#36 reality** (no-regression floor) or **aspirational counts** (under-collection detection gate)? The answer per Phase 2A design: MIN_FLEET reflects current cohort reality with ~5-10 % headroom. Aspirational per-country targets stay in the v4.23 gap-audit workstream (this document), not encoded in the validator. Recalibrated: AT 1200→700 · CA 8000→6000 · GR 1500→500 · MX 4000→2200 · PL 3000→2100 · ES 3500→3300. Each carries a Phase 2A/2C code comment with the reasoning + current-count-at-time-of-recalibration.

**Convention #56 preserved throughout.** Every stale classification `[N/A]` was replaced by a computed classification from current `R_median` — no silent defaults, no invented data. The `meta.phase2c_reclassify_runs` audit trail in each `ssi-data.json` records the transition (timestamp UTC + `changed_count` + engine bands version). Cause-D2 modifier drift stays deferred as a known-scoped workstream (Q3 workstream); the Cause-F Spain weighted-format bug stays deferred as an ingestion-layer follow-on. Both surface honestly in the validator output rather than being papered over.

**Authoritative sources for Phase 2 closure.**

- `scripts/validate_schema.py` — Phase 2A patches inline-documented at each patch site
- `scripts/pipeline/scoring/engine.py::BANDS` — Phase 2B-1 5-band table
- `ssi-engine.js::BANDS` + 8 sibling JS files — Phase 2B-2 visual cascade
- `scripts/reclassify_phase2c.py` — targeted reclassify script, compact-JSON discipline (do NOT re-introduce `indent=2` on `ssi-data.json` writes — inflates US file to 114 MB, tripping GitHub's 100 MB per-file limit; discipline pinned in module docstring)
- `Report Production/02-v4_23-gap-audit-2026-07/v4_23-gap-audit.md` — forward-reference for the v4.23 substation + line ingestion workstream

### v4.23 gap-closure forward-reference — substation + line coupling invariant (25 June 2026)

The v4.23 gap-audit (`Report Production/02-v4_23-gap-audit-2026-07/`) identifies 10,260–17,025 additional substations across five countries (Canada, Norway, Mexico, Austria, Greenland) where public regulator sources are not yet in the ingestion chain. Engineering scope: **77-99 engineer-days** including paired transmission-line ingestion. Priority sequencing: Canada Q3 2026 (standalone workstream, 25-32 days); Norway + Mexico Q4 2026 (batched, 28-35 days); Austria + Greenland Q1 2027 (batched with Wave 2 cohort expansion, 21-29 days).

**Operator directive 25 June 2026 (binding for v4.23 workstream).** Every new substation added to the cohort MUST be paired with the ingestion of its connecting transmission lines. This extends the Discipline #36 invariant ("transmission lines connecting filtered-in substations to filtered-out substations are KEPT") in the additive direction: "transmission lines connecting a newly-ingested substation to the existing grid graph MUST be ingested in the same pipeline pass." Both preserve topology honesty — the substation graph is only meaningful if edges (transmission lines) accompany nodes (substations). Without paired line ingestion, R4 Graph-Theoretic Network Criticality (S_i=0.37 in Italy Sobol) + R6b Network Topology (S_i=0.99, dominant per-modifier sensitivity) modifiers become disconnected from ground truth for every new substation, artificially depressing Betweenness Centrality signals and inflating zero-degree flags.

**Sentinel commitment (Q3 2026 alongside first Canada landing).** Extend `tests/test_no_cross_border_leakage.py` with new `TestSubstationLineParity` class: (a) every substation in `<country>/ssi-data.json` has ≥1 transmission line touching it in `<country>/grid-geo.json` (except explicitly islanded Greenland-class settlement subs); (b) no transmission line has zero endpoints in the substation registry (line orphaned by substation removal); (c) line-count / substation-count ratio stays within its pre-v4.23 country-specific empirical distribution ±2σ. This preserves the Convention #55 verify-don't-trust discipline the D#36 sentinel established.

**Auditability chain for v4.23 line-ingestion events.** Every per-country line-ingestion pass emits `v4_23-line-ingestion-audit-<country>.yaml` recording: source URL + retrieval date (UTC) + SHA-256 of downloaded artefact + line-count delta + orphan-check status + commit hash + CI job run URL + cross-reference to the substation-ingestion audit YAML for the same pass. Traceable at read-time by any reader / contributor / LP-DD reviewer.

### KB §91.A / §91.B — Cron-gate discipline

GitHub Actions cron uses OR semantics when both day-of-month AND day-of-week are restricted. `'0 6 1-7 * 4'` looks like "1st Thursday at 06:00 UTC" but actually fires ~10×/month. Workflows that need "1st Thursday" / "2nd Thursday" must use a narrow cron (`'0 6 * * 4'` = every Thursday) plus a runtime DOM gate inside the workflow (DOM ≤ 7 for 1st Thursday; 8 ≤ DOM ≤ 14 for 2nd Thursday). Manual `workflow_dispatch` invocations always proceed regardless of the gate.

### Discipline #37 — Defensive coding: None-guard + flat-list-root guard across L2/L3/L4 pipeline (NEW · 16 July 2026)

**Problem this prevents.** Post-Wave-2 L1 ingestion, per-country `ssi-data.json` files carry two legitimate Convention #56 states that historically crashed downstream code:

1. **R_median = None** — legitimate visibly-honest degradation marker per Convention #56 when substation exists on grid but scoring inputs incomplete. Phase 2C reclassify-vs-rescore discipline (`meta.phase2c_reclassify_runs`) explicitly permits this state. Downstream code assumed R_median is always float.

2. **Flat-list root schema** — Latvia (Task #248 Convention #78 BINDING promotion event) ships `ssi-data.json` as `[{sub1}, {sub2}, ...]` instead of `{"substations": [...]}`. This is **Convention #78 §4bis.4 Phase 1 intermediate state** — deliberately not rewrapped during L1 ingestion because rewrapping would mask the flat-list-vs-wrapped topology signal that Convention #78 sub-convention exists to codify. Operator confirmation 16 July 2026: *"we would first bring all additional substations and power lines, and only after we would run the layers scoring etc"* — Latvia flat-list is NOT a bug to rewrap; it is the intermediate state that downstream L2/L3/L4 code MUST accommodate defensively.

**Guards codified (four defensive-coding sites).**

1. **`scripts/pipeline/utils/geo.py::load_substations()`** — after `json.load(f)`: `if isinstance(data, list): data = {"substations": data}` with INFO log citing Convention #78 §4bis.4.

2. **`scripts/validate_schema.py::validate_file()`** — same flat-list guard + Check 7 (R_median min/max) filters None values + Check 8 `_expected_band_v42(r)` returns 'Unclassified' for None + format-string guard `r_str = f"{r:.4f}" if isinstance(r, (int, float)) else "None"` + skip None subs from classification-band mismatch tally.

3. **`scripts/pipeline/scoring/engine.py`** — `classify_band(R)` returns "Unclassified" if R is None + `compute_fleet_summary(substations)` filters None from stats, adds "Unclassified" band + `n_scored` + `n_unclassified_pre_l3` audit fields + `_stats_pending_l3_rescore` flag when no scored subs + `compute_regional_summary(substations)` applies same filter pattern.

4. **`scripts/pipeline/enrichment/merge.py`** — same flat-list guard + `if "meta" not in data: data["meta"] = {}` bootstrap for Latvia (which has no meta block yet in Phase 1) + fleet_percentile sort filters None R_median + assigns `sub["fleet_percentile"] = None` for None-R_median subs.

**Sentinel commitment (queued for next commit cycle).**

- `tests/test_validate_schema_handles_none_r_median.py` — feeds synthetic country with 10% None R_median; asserts exit 0 + 'Unclassified' band populated + no format crash
- `tests/test_validate_schema_handles_flat_list_root.py` — feeds flat-list `ssi-data.json`; asserts wrap + validate success + INFO log citing Convention #78 §4bis.4
- `tests/test_handles_all_none_r_median.py` — 100% None R_median edge case; asserts `_stats_pending_l3_rescore` flag emitted + no crash

**What this discipline does NOT do.** It does NOT rewrap Latvia's canonical on disk (Convention #78 §4bis.4 preservation of Phase 1 intermediate state), does NOT reclassify any None R_median as a numeric value (Convention #56 preservation of visibly-honest degradation), does NOT modify `_MODIFIER_RANGES` R7_cyber 0.99 floor (Task #159 operator constraint against masking genuine cyber-risk signal drift).

**Empirical impact (16 July 2026 batch rerun).** Pre-fix: 12/19 countries passed L2/L3/L4 rescore across recently-ingested cohort. Post-fix: 15/19 GREEN including austria (14,720 subs), greenland, luxembourg, netherlands (Class B format crash), lithuania, estonia, hungary (Class C sort crash), latvia (Class D flat-list). 4 residual failures are all Class A KB §56 R7_cyber drift (chile 57.7% below 0.99 floor + slovenia 59.2% + norway 92.5% + australia 24.1%) — deferred to post-Wave-2 data-refresh cycle per Task #159 operator constraint. See `L2_L3_L4_BATCH_RERUN_20260716.md` + `FAILURE_SOLVING_PROPOSAL_20260716.md`.

### Discipline #38 — Nested-field navigation must use explicit membership check, not empty-dict fallback (NEW · 16 July 2026)

**Problem this prevents.** `assess_esg_readiness()` in `scripts/pipeline/enrichment/merge.py` (and any similar field-navigation logic across the codebase) MUST use explicit `p not in val` membership check when walking dotted-path fields on substation dicts. The banned anti-pattern is `val.get(p, {})` empty-dict fallback which silently masks missing fields as populated:

```python
# ❌ BANNED — silent false-positive
for p in parts:
    val = val.get(p, {}) if isinstance(val, dict) else None
    if val is None:
        break
# post-loop: val is {} → treated as populated when field was missing

# ✅ REQUIRED — explicit membership check per Convention #56
missing = False
for p in parts:
    if isinstance(val, dict):
        if p not in val:
            missing = True
            break
        val = val[p]
    else:
        missing = True
        break
if missing or val is None:
    continue  # NOT populated
```

**The failure mode this closes (R7 SFDR PAI Phase 4a discovery, 16 July 2026 late evening).** Pre-fix `assess_esg_readiness()` was silently reporting **ALL 6 ESG reports as READY** for 15 recently-L1-refreshed countries when the empirical reality was **5 of 6 GAP** across R2/R4/R5/R6/R7. Every prior country closure YAML (Wave 1 P1-P5 + Wave 2 P1-P21 = 26+ files) with `esg_reports_ready_count: 6` was falsely-positive for recently-refreshed countries — the actual empirical R1-R6 readiness was hidden because nested fields like `socio_economic.V_socio` navigate through a top-level dict that may not exist on net-new subs. When `sub.get("socio_economic", {})` returned `{}` for a net-new sub, the subsequent `{}.get("V_socio", {})` returned `{}` again — passing the `val is not None` gate and counting as populated because `{}` isn't in the `_is_default_value` known-defaults list.

**Post-fix state (16 July 2026 late evening):** Poland empirical readiness now surfaces correctly as R1 89.3% READY + R3 100% READY + R2/R4/R5/R6/R7 all ~8.1% GAP (matching the 2,247/27,764 baseline sub count). 91.9% of Poland's substations were revealed to be in Convention #78 §4bis.4 two-phase workflow Phase 1 intermediate state — awaiting the L2/L3/L4 modifier-chain rescore closed via `scripts/refresh_v42_modifiers_re_composite.py` Phase 4c pass (76,045 subs across 17 countries transitioned to 100% coverage in 13.3s).

**Generalises to.** Any future codebase function that walks dotted-path fields on JSON records — validators, readiness assessors, coverage counters, drift detectors. The generalisable rule: **`{}` (empty dict) is not None, so `val is not None` is not sufficient to distinguish "populated" from "missing". Track missing-ness with an explicit boolean flag, or check `p in val` membership before descending.** This composes with Discipline #37 (defensive coding for None + flat-list root) as sister rules for Convention #56 preservation at the read-back layer.

**Regression sentinel commitment.** `tests/test_esg_reports_7_axis_synchronization.py` (12/12 GREEN as of commit `9804efc7`) pins the backend↔frontend R1-R7 sync + FC v3 §14 canonical order. A follow-on sentinel to explicitly test `assess_esg_readiness()` against synthetic net-new subs with missing top-level fields is queued as Phase 5 continuation work.

**Authoritative documentation.** `R7_SFDR_PAI_phase4a_cohort_wide_false_positive_finding.md` — full latent-bug forensic + empirical impact matrix + cross-repo Re_norm vs Re_normalised naming inconsistency (Convention #66 documented follow-on) + Convention #78 §4bis.4 two-phase workflow signal now empirically visible.

**Closure status.** Discipline #38 codified 16 July 2026 late evening as part of R7 SFDR PAI Phase 5 doc cascade (task #310). Preventive discipline — no immediate operator action required; existing pipeline runs land the fixed logic on next `pipeline.run <country>` invocation.

### KB §91.A pull-rebase race defuse

Multiple workflows can push to `main` concurrently (intelligence + ESG monthly refresh + manual dispatches). Each push step does `git pull --rebase --autostash origin main` with 3 attempts, falling back to `merge -X ours` if the rebase conflicts (the cron's enrichment + edition bump always wins over a competing external push). The `concurrency: monthly-refresh-main` block at workflow level prevents same-workflow race.

### Convention #56 — Visibly-honest degradation (inherited from the SSI Index methodology framework)

When a value cannot be sourced from a public regulatory canonical, the methodology surfaces `[N/A]` markers + degradation reasons rather than silent defaults. The v4.0.2 → v4.2 promotion preserves `_v4.0.2.backup/` per country so older deliverables remain auditable. Applies cohort-wide: ingestion failures surface as visible gaps, not silent zeros.

## Quick reference — running the tooling

```bash
# Run the full pytest suite (locally; CI runs validate.yml on push)
pytest tests/                                                  # all tests
pytest tests/test_no_cross_border_leakage.py -v                # Discipline #36 sentinel only
pytest tests/ -m "not slow"                                    # skip slow integration tests

# Cross-border audit (manual diagnostic)
python3 scripts/check_cross_border.py --all                    # full cohort report
python3 scripts/check_cross_border.py --all --strict           # fail on any violation
python3 scripts/check_cross_border.py austria                  # single country
python3 scripts/check_cross_border.py --all --json out.json    # machine-readable

# Per-country remediation (one-shot)
python3 scripts/remediate_cross_border.py austria              # fix Austria
python3 scripts/remediate_cross_border.py austria --dry-run    # preview only
python3 scripts/clean_grid_geo.py --all-remediated             # propagate to grid-geo
python3 scripts/refresh_country_counts.py --all-remediated     # propagate to HTML pages

# Pipeline run (manual; cron is monthly 1st Thursday 06:00 UTC)
python -m scripts.pipeline.run --all                           # full pipeline
python -m scripts.pipeline.run austria germany italy           # specific countries
python -m scripts.pipeline.run --all --skip-rescore --dry-run  # fast preview
```

## When you need to modify something

| Change type | Where to edit | How to verify |
|---|---|---|
| Fix a country's substation data | `{slug}/ssi-data.json` (rarely manually; usually via pipeline + remediation) | `pytest tests/test_no_cross_border_leakage.py -v` + `scripts/check_cross_border.py {slug}` |
| Extend a country's bounds (add territorial polygon) | `{slug}/bounds.json` (Natural Earth + manual additions documented in `MODE_2_3_FOLLOWON_PLAN.md`) | Re-run remediation + verify pytest green |
| Add a tolerance for a new Mode 2 country | `cross_border_tolerances.json::per_country` | Verify pytest `TestToleranceConfig` passes |
| Add a new country to the cohort | `intelligence/countries.json::slugs` + create `{slug}/` folder + drop `bounds.json` + run pipeline | Verify all 39+1 tests pass; CI gate runs on PR |
| Change the cross-border threshold | `scripts/check_cross_border.py` default + `tests/test_no_cross_border_leakage.py::THRESHOLD_PCT` + workflow files (find via grep `THRESHOLD_PCT`) | The threshold lives in three places — keep in sync |
| Extend a country's bounds.json with overseas territory (Mode-3 pattern: DOM-TOM, anti-meridian islands, Arctic territories, etc.) | `{slug}/bounds.json` + add a tolerance to `cross_border_tolerances.json` if coastline simplification (Mode 2) | Run `python3 scripts/check_cross_border.py {slug}` + `pytest tests/test_no_cross_border_leakage.py -v`. The map.js viewport safeguard (auto-fit-to-bounds at ~line 1438) will auto-detect the pathological span and fall back to substation cluster — no map.js change needed |
| Rewrite or refactor `map.js` | the whole file is fair game, BUT preserve the Mode-3 viewport safeguard at `~line 1438` (substation-cluster fallback when bounds span >60° OR >2× cluster span) | Without it: France's mainland becomes a pixel-sized blob; New Zealand crosses the anti-meridian and fails to render at all. The 35 non-pathological countries are unaffected by the safeguard either way. See commit `a7585fc6` |
| Add a new pipeline modifier | `scripts/pipeline/scoring/modifier_registry.py` + write tests | `pytest tests/test_modifier_registry.py -v` |

## Pre-commit checklist

Before pushing to `main` or merging a PR:

- [ ] `pytest tests/` → all tests green (10+ existing + the 4 cross-border classes)
- [ ] `scripts/check_cross_border.py --all --strict` → green (or PR's validate.yml will fail)
- [ ] If you touched `*/ssi-data.json` or `*/grid-geo.json`: confirm `validate.yml` is green on the PR
- [ ] If you added a new country: confirm pytest discovers the new slug via `intelligence/countries.json`
- [ ] If you changed methodology version: bump `versions.json` + the v4.0.2-style backup pattern per Convention #56

## Companion documents

| Doc | Role | Where it lives |
|---|---|---|
| `CLAUDE.md` (this file) | Session briefing + binding disciplines | repo root |
| `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` | Discipline #36 origin audit | repo root |
| `MODE_2_3_FOLLOWON_PLAN.md` | Discipline #36 second-wave plan | repo root |
| `PR_CROSS_BORDER_GUARD.md` | Discipline #36 PR-ready notes | repo root |
| `REPORTS_FRAMING_KB.md` §72 | Discipline #36 cross-reference from the SSI Index methodology framework | `~/Library/CloudStorage/OneDrive-…/SSI Index/Report Production/00-Framing/REPORTS_FRAMING_KB.md` (separate repo) |
| `PHASE_1_IMPLEMENTATION_PLAN.md` | Phase 1 PR-1+ scoring engine | repo root (canonical Phase 1 narrative) |
| `AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md` | v4.0.2 → v4.2 audit (F-Lx-y findings) | repo root |
| `intelligence/countries.json` | 39-country slug + first-refresh SoT (KB §57) | repo |

## Contact

- **Cedric Berard** — c.berard@ikenga.eu — Ikenga Capital
- **SSI Index project** — ssi_index@ikenga.eu

---

*If you find this briefing outdated, update it in the same commit as your fix.*
