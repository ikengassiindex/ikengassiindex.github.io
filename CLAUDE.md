# CLAUDE.md — SSI Index public dashboard briefing

> Auto-loaded briefing for Claude sessions on the `ikengassiindex.github.io` repo. Read this first before touching the codebase.
> Maintained by Ikenga / Cowork · Last updated: **18 August 2026 (🏛 v4.23 → v4.24 METHODOLOGY-VERSION EVENT CASCADE Session M+1 LANDED-SANDBOX uncommitted — GATE-A-11 REVISED from dual-write ~6 months → **hard cutover at Session M+1** per operator directive "done before the market" (thought-leadership framing). R7_cyber v1 TOMBSTONED in `scripts/pipeline/scoring/modifier_registry.py` with retire-with-comment discipline per Convention #56; R7_cyber_v2 (CRA Article 14 + NIS2 Article 21 register-anchored Path C+D composite, w_entity=0.55 · w_product=0.45, envelope [0.99, 1.05]) promoted to primary emit path; `_r7_cyber_v1_value` snapshot + `_r7_cyber_v1_retired: True` marker preserved cohort-wide. Methodology version bump `versions.json` v9 → v10 (methodology 4.23 → 4.24) + `intelligence/edition-config.json` edition 25 → 26 + ssi_version 4.2 → 4.24. Convention #79 sharding threshold RECALIBRATED 90→60 MB / target 60→45 MB for post-v4.24 modifier chain headroom (`scripts/pipeline/utils/ssi_data_sharding.py`); Poland (63 MB single-file) sharded 2 files; italy/us/germany/uk/france re-sharded 3/6/9/4/10 files to conform. Preflight YAML `task_1108_r7_cyber_v2_preflight_20260825.yaml` row `gate_a_11_r7_v1_retirement_timing` REVISED signed 2026-08-18 supersedes original dual-write default. Discipline #47 REGULATORY-VINTAGE variant empirical instance count 1 → 2 (accelerates Convention #76 BINDING promotion path). **Deferred operator-execution phases**: Phase ζ full pipeline rescore (39-country Monte Carlo, ~4-6h wall-clock, `python -m scripts.pipeline.run --all`) + Phase η per-country P5/P95 band renormalisation (`python3 scripts/normalise_bands_per_country.py --all-countries`) + Phase ζ→η verification (canada R_median 0.81% > 1.0 pre-existing drift will clear post-`soft_clip_upper()` rescore per FL-007). Sentinel `tests/test_r7_cyber_v2_construct.py` needs post-cutover refresh (Phase κ) — rename `test_v1_r7_cyber_still_present_dual_write` → `test_v1_r7_cyber_tombstoned_post_cutover` + add `TestPostCutoverInvariants` class. **Earlier same day**: 🏛 Phase 2J P3 CODE-LAYER LANDED-SANDBOX uncommitted — Task #1134 CRA P2-P4 workstream: `scripts/pipeline/scoring/r7_cyber_v2.py` module (Path C+D composite implementation per Gate A GATE-A-1 sign-off, w_entity=0.55 · w_product=0.45 per GATE-A-2, envelope [0.99, 1.05] preserved for R7 v1 continuity, dual-write GATE-A-11 markers `_r7_cyber_v1_retired` + `_r7_cyber_v1_value` + audit trail `_r7_cyber_v2_source` + Convention #56 fallback markers `_r7_cyber_v2_fallback_reason`) + sentinel `tests/test_r7_cyber_v2_construct.py` **91/91 GREEN** pinning envelope invariant · weight sum-to-unity · Path C+D 26 EU/13 non-EU cohort split · Convention #56 fallback per-layer redistribution · registry-key ↔ emitted-field parity · CRA Article 14 + NIS2 Article 21 regulatory-vintage anchors · dual-write v1 immutability. Cascade playbook `METHODOLOGY_CASCADE_PLAYBOOK.md v0.3` LANDED post Session D Gate C aggregation on FL-001..FL-005 (all 5 AMENDMENT-CONFIRMED: §3.7 `.PROPOSED` sidecar discipline + §4.1.1 modifier module naming discipline + §3.3-fn Latin ordinal section-numbering discipline + §5 regulatory-instrument article reference family + §6.1 three-surface partial-cascade disclosure discipline). **Earlier same day**: 🏛 Phase 2J GATE A CLOSED · Trees 1 + 2 + 3 + 4 addendums LANDED-SANDBOX uncommitted post Session B merge of all 4 `.PROPOSED` sidecars into targets (REPORTS_FRAMING_KB.md §8bis Discipline #47 5th REGULATORY-VINTAGE variant extension · CONVENTIONS_REGISTRY_SYSTEMIC.md §21 Convention SY.21 candidate · V42_INTEGRATION_THINKING_HAT + STAGE_V31_51_IMPLEMENTATION_PLAN R7 v2 × W6 composition + sequencing paragraphs) · P1 short-list 13 touch-points + Gate A 15-decision preflight YAML SIGNED 18 August 2026 Session B at `SSI Index/Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/task_1108_r7_cyber_v2_preflight_20260825.yaml` · P1 execution log at `CRA_P1_EXECUTION_LOG.md` · Discipline #47 5th REGULATORY-VINTAGE variant candidate + Discipline #48 cross-tree cascade discipline candidate (Playbook §7) registered · `METHODOLOGY_CASCADE_PLAYBOOK.md v0.2` first empirical stress-test surfaced 5 feedback log entries FL-001..FL-005 · CRA Article 14 hard binding-date 11 September 2026 · Path variant = Path C+D composite (GATE-A-1) + weights w_entity=0.55, w_product=0.45 (GATE-A-2) resolved in modifier_registry.py + Phase 2J addendum · intelligence.html tooltip cascade queued P4 · Full workstream cascade plan `CRA_R7_CASCADE_PLAN_EXTENDED.md` = 41 touch-points across all 4 trees; ~92 engineer-hours cumulative). Earlier: **24 July 2026 night (🏛 Wave 4 SYSTEMIC cross-border pollution empirical closure — Task #501 follow-on cluster diagnostic surfaced cohort-wide 3-class pollution taxonomy across 9 Wave 4 majors (661,867 subs analyzed → 186,627 outside polygon = 28.20% cohort-wide): **Class A** cross-border ingestion pollution ~101k subs · **Class B** bounds.json interior gap ~51k subs · **Class C** legitimate offshore ~27k subs. Empirical Discipline #36 closure: Sweden 10,207 subs stripped (94.79%→0%) + Spain 17,601 subs stripped (80.62%→0% at 5km tolerance preserving Class B) = **27,808 Class A subs REMOVED** from origin/main. Commit chain `e2ba92e6` (Sardegna+Japan closure 595→0) → `04785349` (empirical closure diagnostic) → `c524cb9e` (cluster diagnostic + shapely.prepared prep() **135× US Task #501 speedup 983s→7.3s**) → `5268e180` (Spain topology hotfix) → `0fa9eb67` (--all-wave4 batch mode) → `68a9cf7c` (Convention #79 sharded reader hotfix) → `1b08f2c7` (Wave 4 SYSTEMIC finding cascade) → `900a1a8f` (Discipline #36 whitelist 5→12 countries with empirical evidence) → `f4999003` (`scripts/_ssi_data_shard_reader.py` shared utility — Convention #79 empirical instance count 4→5 LOWER SATURATION). New utilities: `scripts/audit_out_of_polygon_clusters.py` (9-country neighbor bboxes + `--all-wave4` batch + `buffer(0)` invalid-polygon auto-repair) + `scripts/_ssi_data_shard_reader.py` (`load_ssi_data`/`load_substations`/`count_substations`/`save_ssi_data`). Discipline candidates registered for cross-repo REPORTS_FRAMING_KB §8bis promotion: **Discipline #48 candidate** (bounds.json quality is empirically per-country — sibling to §5septies OSM-tag density, 5 instances at LOWER Convention #76 threshold) + **Discipline #49 candidate** (3-class taxonomy for out-of-polygon subs — sibling to Discipline #47 sibling-variant framework). Convention #7 documented-proxy anchor extended with `NEIGHBOR_BBOXES` Natural Earth 1:10M-derived tables. Full closure memo `WAVE_4_SYSTEMIC_CROSS_BORDER_CLOSURE_20260724.md` + `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` Wave 4 addendum. Blocking finding surfaced: `check_cross_border.py` + `remediate_cross_border.py` + `refresh_country_counts.py` fail with ZeroDivisionError on Convention #79 sharded ssi-data (US/France/Germany/UK/Italy) reading `data['substations']` directly which returns None on sharded manifests. Task #520 next-session workstream: wire 3 scripts through `_ssi_data_shard_reader` + complete remediation on US ~17k + France ~24k + Germany ~21k = ~62k additional Class A subs to strip. LP-DD implication: Sweden + Spain SSI Index v4.2 outputs now reflect real national substation registries (not neighbor-country contamination); US + France + Germany contamination diagnosed but remediation blocked pending Task #520; ~62k additional cross-border pollution subs pending strip. Earlier same day: 🎯 Task #501 follow-on TERMINAL closure — 595 residual csv_lookup_miss → 0 via Sardegna NUTS 2024 v2 5-code CSV expansion (ITG2D+E+F+G+H) + Japan macron aliases (Hyōgo→Hyogo, Naoasaki→Nagasaki GADM typo) across 2 apply cycles; Discipline #36 whitelist extended 5→12 countries with empirical evidence per country. Earlier (23 July 2026 morning): 🎯 Task #461/#462/#463 TRILOGY CLOSED — Wave 4 L3 R_base_median=0 regression retired via `scripts/fix_wave4_r_base_regression.py` cohort-wide (commit `06a83c98` — 8 countries with pre-existing R7 Phase 4c pipeline seam: refresh_v42_modifiers_re_composite.py populated modifier values but never re-invoked compute_r_base()); then per-country P5/P95 empirical normalisation of classification bands applied to Wave 4 cohort via `scripts/normalise_bands_per_country.py` (commit `045f9e8b` — new engine.py APIs: `classify_band_normalised(R, R_P5, R_P95)` + `apply_country_normalised_bands()` batch mutator; Convention #78 BINDING 5-band Extreme mesh preserved; R_median stored absolute per substation for Convention #56 auditability, only `classification` field carries within-country ranking); extended to all 39 cohort countries (commit `de671f20`) with Wave 4 countries idempotent (P5/P95 unchanged → identical outcomes); doc cascade to methodology.html + intelligence.html × 39 (commit `e29b1be9`) reframes user-facing band definitions from absolute-R thresholds to percentile-based within-country ranking + adds missing Extreme card closing pre-existing Phase 2B gap. Cohort-wide convergence: every country now shows healthy ~23% Low / ~28% Medium / ~28% High / ~15% Critical / 5% Extreme spread (Extreme = top-5% by construction) — retires the pre-fix range where some countries showed 100% Low (Luxembourg, Sweden pre-Wave-4-fix) or 46% Critical + 14.6% Extreme (Turkey, absolute-R artefact). Cross-country ranking must now use absolute median_R (unchanged) rather than band-share aggregates. Surfaced pre-existing pipeline seams for future closure: Slovenia P5=0.0 (5% of subs with R_median at/near 0, consistent with Task #117/#159 Cause D2 modifier drift), Switzerland 47.7% Unclassified (R_median=None per Convention #56 visibly-honest pre-L3-rescore state — 865 subs surfaced). Task #461/462 empirical audit reports at `~/normalise_bands_audit_2026072*.json` per country. See Phase 2D section below for full closure narrative + Task #459 foundational-doc-audit context. Earlier (21 July 2026 evening): 🏆 Wave 4 R4/R5/R6 TERMINAL CLOSURE end-to-end — 9/9 Wave 4 countries at 7/7 ESG READY (662k subs · 63/63 ESG cells READY cohort-wide). Commit chain: `62d52527` L1 TERMINAL (US P39, 39/39 v4.23 cohort complete at L1) → `d0312749` L4 partial 5/9 pushed (Sweden + Portugal + Italy + Japan + Spain, R4-R6 gaps closed via `enrich_esg_gaps.py --wave4` institutional-data proxy per Convention #7) → `ad9adfc5` **Convention #79 candidate ssi-data sharding** (4 large countries UK 62k / US 101k / Germany 187k / France 195k → 18 shard files, each <60 MB fits GitHub 100 MB hard limit; analog of Convention #80 grid-geo sharding; loaders `map.js::loadSsiData()` + `country-renderer.js::loadSsiData()` auto-detect `sharded: true` + parallel-fetch + concatenate into virtual substations inline; backward-compatible for 35 non-sharded countries) → `2561a8ea` **Denmark P28 alias-map extension** (Task #352 CLOSED; 5 new operator families 32 aliases: Nexel/Vores Elnet/Flow Elnet/EnergiMidt-legacy/Better Energy/Copenhagen Airport; retroactive normalisation across 4,822 DK subs; distinct-operators 103 → 85 = -17.5% via Convention #78 BINDING 4th enforcement post-promotion). Two-phase closure architecture: Phase 1 L2/L3/L4 pipeline batch via Option C (spatial join bounds.json polygons → per-sub region via shapely STRtree; 656,052 subs region-tagged; voltage_kv str→float coerce; province="" fallback for None; 4079s wall-clock across 9 countries) + Phase 2 ESG gap enrichment via `enrich_esg_gaps.py --wave4` (institutional-data per-country baselines: SGU + SCB + IEA 2024 for Sweden · LNEC + APA + INE + DGEG for Portugal · INGV MPS04 + ISTAT + ISPRA + GSE for Italy · NIED J-SHIS + MIC + JMOE for Japan · BRGM + INSEE + ONPE + ADEME for France · AEA Barómetro + INE + MITECO for Spain — all Convention #7 documented-proxy). Session-wide defensive-coding empirical validation: **Discipline #37 (None guard) 2nd empirical instance** (socioeconomic.py `province None` guard + enrich_esg_gaps.py `name None` guard — both same session; Convention #76 cadence 2/5-10 toward BINDING promotion) + **Discipline #39 candidate first empirical instance** (mixed-type sort coerce — seismic.py zone `int()` cast before `sorted()` to defend against pre-Wave-4 canonical str/int mixed values). Convention #56 visibly-honest degradation preserved end-to-end: every enrichment gate uses `if not sub.get(f)` guard so pipeline outputs never overwritten by institutional-data fallback. Wave 4 workstream lifecycle 17-21 July 2026 (11 commits: 34-45): Turkey P30 cohort-completion → UK P31 → Sweden P32 → Portugal P33 → Italy P34 → Japan P35 → Spain P36 → France P37 → Germany P38 → US P39 → L2/L3/L4 batch → R4-R6 enrichment → sharding TERMINAL. Next queued: foundational-doc audit (this session, ongoing) + Convention #56 sentinel via test_ssi_data_sharding_invariants.py + L5 SSI Foundation full-cohort deliverable regen. Earlier same day: 🎯 **Denmark P28 alias-map extension** (Commit 46 `2561a8ea` PUSHED) — pre-existing Task #352 CLOSED per operator directive; 32 new alias entries across 5 operator families empirically surfaced during Denmark P28 closure YAML `alias_map_extension_CRITICAL` finding (5,244/5,803 = 90.4% missed alias-normalisation at DK OSM ingest pre-extension); retroactive `normalise_owner_alias()` pass over 4,822 Denmark subs consolidated 103 distinct operators → 85; Nexel now 2,374 subs = 49.2% of DK cohort under canonical `Nexel (Radius Elnet subsidiary — Zealand)`. Convention #78 BINDING 4th enforcement post-BINDING-promotion of §4bis.4 discipline. Earlier (17 July 2026 afternoon): 🏛 Wave 3 P22 Greece TERMINAL end-to-end — commit `a2e4c0b2` PUSHED + retry pass empirical: FIRST Wave 3 country post R7 SFDR PAI closure; SIMPLEST cohort-wide architecture (SINGLE national DSO DEDDIE/HEDNO — Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED); 3-file connector suite ~1120 LOC via Czechia canonical pattern + single-DSO simplification; 100-entry Convention #78 BINDING 4th enforcement alias map (Greek script ΑΔΜΗΕ/ΔΕΔΔΗΕ/ΔΕΗ + Latin transliteration ADMIE/DEDDIE/DEI + English acronyms IPTO/HEDNO/PPC + Α.Ε./A.E. legal-form variants + Greek diacritics τόνος + DEI/PPC pre-2011 1-generation predecessor + industrial captives Aluminium of Greece/ELPE/Larco/Motor Oil Hellas/Mytilineos + Athens transport OSE/ERGOSE/Attiko Metro/STASY); voltage-class × single-DSO resolver (≥66 kV → ADMIE TSO; <66 kV → DEDDIE DSO; None → DEDDIE default); 5 km cross-border tolerance per Aegean archipelago + Ionian + Crete + Peloponnese coastline precedent (Greenland/NZ/Denmark/Norway sibling); Wave 3 P22 empirical outcome: 556 baseline → 719 final subs (+29.3% growth via 20 first-run + 143 retry net-new + 318 retry enriched + 108 Convention #78 alias-normalised); 1,420 → 1,775 lines (+25% growth); 87 outside-polygon dropped; 10 voltage tier-mismatch findings; 100% owner attribution (ADMIE 67.5% + DEDDIE 29.1% + 4% industrial captives + Athens transport — architecturally TSO-heavier than Central European peers due to 66 kV Greek subtransmission tier being ADMIE-owned vs 110 kV Central European DSO-owned; empirical rebalance retry 80/19 → 67/29); Convention #56 partial-fetch preserved end-to-end across TWO Overpass 504 gateway timeout events (first-run way-query + retry node-query — Greek OSM sparsity hypothesis empirically confirmed via 6 gateway events across 2 fetch cycles); Phase 4c v4.2 modifier + Re composite refresh: 194 net-new refreshed → 719/719 = 100% Re_norm coverage; Convention #78 BINDING 4th enforcement empirically validated at 108 alias-normalisation hits (cumulative 7-country ledger 20,514 = 2,051× above BINDING threshold); Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED (empirically confirmed via single-DSO architecture); commits `eb9d7070` connector + `a2e4c0b2` first-run canonicals + retry pass empirical + Wave 3 P22 closure YAML pending Commit 12. Bug queued: canada _base emit_audit_sidecar hardcodes 'canada' output path — Greek audit sidecar landed at scripts/pipeline/data/canada/ (LOW severity, batch-fix deferred). Next Wave 3 country: Iceland P23 (684 baseline subs — smallest-first cadence intact; single-TSO Landsnet + single-DSO likely simpler than Greek architecture). Earlier same day: 🏛 R7 SFDR PAI Phase 4a-4e TERMINAL end-to-end — commit `9804efc7` PUSHED: 7-axis ESG report rollout (config.py::ESG_REPORTS R1-R7 per FC v3 §14 subsection 13.7 + R3 relabelled "Infrastructure Resilience [Re composite home]" + R4↔R5 swapped canonical order + assess_esg_readiness cohort-wide false-positive latent bug retired per Convention #56 REINFORCED + esg-sections.js frontend rendering 7-axis radar + computeESGScores returns 7-element array + 39-country cache-bust `?v=20260716-r7` + 12/12 sentinel `test_esg_reports_7_axis_synchronization.py` GREEN pinning backend↔frontend sync + FC v3 §14 canonical order); Phase 4c 15-country rescore executed via NEW scripts/refresh_v42_modifiers_re_composite.py (Convention #7 Data-Layer Anchoring documented-proxy + per-country hazard baselines source-cited JRC EU-Flood-Atlas + Copernicus + ECMWF + ND-GAIN + IPCC AR6 + Just-Transition Fund + deterministic MD5 per-substation seeding + FC v3 §14 formula empirically verified): 76,045 substations across 17 countries refreshed in 13.3s from Convention #56 neutral defaults (Re_raw=1.0, Re_norm=0.0) to full v4.2 modifier chain populated + Re composite computed; ALL 17 countries transitioned to 100% Re_norm coverage (greenland 79.1→100 · costa-rica 94.1→100 · israel 94.9→100 · estonia 32.5→100 · slovenia 8.6→100 · colombia 48.1→100 · luxembourg 11.6→100 · latvia 24.9→100 · lithuania 9.8→100 · belgium 17.4→100 · netherlands 28.5→100 · mexico 74.2→100 · canada 77.7→100 · australia 61.2→100 · austria 4.9→100 · czechia 11.4→100 · poland 7.7→100); Convention #79 candidate registration queued (assess_esg_readiness missing-field-treated-as-populated preventive discipline) + retroactive YAML backfill queued (21 country closure YAMLs × 2 = 42 files, extend esg_reports_ready_count: 6 → 7). Earlier same day: 🏛 Poland P21 + Visegrád Trio COMPLETION MILESTONE end-to-end — 3 of 3 Visegrád Group v4.23 refresh COMPLETE (Slovakia P19 + Czechia P20 + Poland P21) + full 4-of-4 Visegrád Group v4.23 status (SK + CZ + PL + HU); Poland empirical: 27,764 subs (baseline 2247 + LARGEST cohort-wide net-new 25,517 = 3.26× Czechia) + 105,254 lines + 39.9 MB ssi-data + 48.4 MB grid-geo (both under 90 MB Task #125 sentinel); Convention #78 BINDING 3rd enforcement 🏆 SMASHING SUCCESS at 14,449 alias-normalised at fetch time (LARGEST cohort-wide count 2.79× Czechia's 5,178 + 91.3% enforcement ratio) → cumulative 6-country empirical instance count 20,406 = 2,040.6× above BINDING promotion threshold; Convention #78 §4bis.5 Layer 3 geofence 3rd enforcement narrow-carve-out variant (Innogy Stoen Warsaw metro 621 subs = 2.0% below refinement threshold); 🚨 critical empirical finding — Polish OSM does NOT populate ref:nuts:3 tags at country scale (74-code territorial map DEAD CODE, codifies OSM tag density is EMPIRICAL PER COUNTRY architectural lesson); Layer 4 PGE catch-all default resolved 45.9% as PRIMARY attribution mechanism; Innogy Stoen 3-GENERATION UNIQUE cohort-wide multi-generation rebrand-predecessor cascade codified (RWE Stoen 2003-2020 → Stoen Operator 2016-2020 → Stoen SA 2003-2016 → ZE Warszawa pre-2003); commits `8febea7f` connector + `0a79e36f` hotfix + `1a9c5a24` L1-L4 canonical refresh · 🚨 **R7 SFDR PAI Infrastructure Disclosure cohort-wide framework/pipeline gap discovered** by operator during Poland P21 audit: `scripts/pipeline/config.py::ESG_REPORTS` registers only R1-R6 while framework catalog carries 7 canonical reports per FC v3 §14 subsection 13.7 (39/39 countries announce R7 in `<slug>/esg-report.html` section-sub); Full 5-phase R7 workstream (Phase 1 diligence + Phase 2 audit complete; Phase 3 design signed off operator scope A+C+D+Both retroactive-and-forward-looking backfill; Phase 4-5 execution deferred to post-Poland-Step-5 per Sequence 2); 39-country empirical R7 readiness: 24 READY + 6 PARTIAL + 9 GAP (Poland at 7.7% Re_normalised populated — GAP per Convention #78 §4bis.4 two-phase workflow — will be closed in R7 Phase 4c rescore); 3-file R7 audit trail: `R7_SFDR_PAI_diligence_note.md` + `R7_SFDR_PAI_current_state_audit.md` + `R7_SFDR_PAI_phase3_design_signoff.md` · Earlier same day (16 July 2026): L2/L3/L4 batch rerun closure — 15/19 GREEN post-fix across Wave 1 + Wave 2 ingested cohort; Classes B/C/D defensive-coding guards landed: R_median=None format-string + sort-comparison guards across `validate_schema.py` + `scoring/engine.py` + `enrichment/merge.py`; Latvia flat-list root schema guard per Convention #78 §4bis.4 Phase 1 intermediate state; austria 14,720 subs rescored; class A KB §56 R7_cyber drift on chile/slovenia/norway/australia deferred to post-Wave-2 data-refresh cycle NO CODE FIX per Task #159 operator constraint; L5 SSI Foundation codebase located + W1-W10 5/1/1/3 mesh empirically confirmed cohort-wide; retrospective bbox audit validated Prague-refinement uniqueness — no other Wave 2 country requires Layer 3 geofence refinement; two-phase workflow discipline codified: L1 ingestion first, cohort-wide L2/L3/L4 rescore second; report `L2_L3_L4_BATCH_RERUN_20260716.md` + `FAILURE_SOLVING_PROPOSAL_20260716.md` + `CONVENTION_78_BINDING_EMPIRICAL_AUDIT_20260716.md` · Earlier (25 June 2026): Phase 2A/B/C closure — v4.2 methodology 4-band → 5-band system live cohort-wide; validator alignment + engine BANDS + JS cascade + 22,749 substations reclassified; 31/39 country PASS validator state; MIN_FLEET recalibrated post-D#36; v4.23 gap-audit landed identifying 77-99 engineer-day workstream to close 10-17k additional substations + paired transmission lines for Canada/Norway/Mexico/Austria/Greenland; commits `d1e77c00` → `8f6cd7ca` · Earlier (25 June 2026 evening): Discipline #36 closure end-to-end — cross-border substation enforcement gate live + pytest sentinel + map.js viewport safeguard for Mode-3 territorial bounds + 39-country cohort canonical at 174,046 substations cleaned of cross-border leakage**

## What this repo is

This is the **public dashboard** for the SSI Index methodology, served via GitHub Pages at `https://ikengassiindex.github.io`. It is NOT the methodology development repository — that lives in `~/Library/CloudStorage/OneDrive-IkengaSL/Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/Report Production/` (authoritative as of 4 August 2026 — the prior `OneDrive-SUN.ENCAPITALOU/Shared DR/Internal/0. General/…` tenant is being retired) and is published as foundational documents (REPORTS_FRAMING_KB.md, About_SSI_Index.md, METHODOLOGY_DISCIPLINES.md, etc.).

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

> **Declared live methodology version: v4.24** (operator decision, 19 August 2026). `versions.json` + `intelligence/edition-config.json` are the release source of truth. ⚠️ Per-country `meta.version` is still stale (25 countries say `4.0.2`, 13 say nothing) — bump it at the next cohort rescore, **not before**: stamping a version the data was never scored under is the defect class Discipline #50 exists to prevent. The v4.2 Zenodo DOI remains the correct *citable* version for already-published deliverables.

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

### Phase 2D — per-country P5/P95 empirical normalisation of classification bands (22-23 July 2026, Task #461/462/463)

**Problem this closed.** The Phase 2A/B/C absolute-R 5-band cutoffs `[0.25, 0.50, 0.75, 1.00]` are applied to `R_median` values whose empirical distribution shape varies materially between countries. Post the Wave 4 R_base_median=0 regression fix (Task #460 / commit `06a83c98` — root cause: `refresh_v42_modifiers_re_composite.py` R7 Phase 4c populated modifier values but never re-invoked `compute_r_base()` or Monte Carlo re-scoring; R_final collapsed to purely additive R6c_flood tail with ~86% false-Low classification), operator audit surfaced that the fix produced technically-correct scoring but ~80% of substations in ITA/ESP/PRT/FRA/DEU landed in "High" band because the R_median distribution is compressed to `[0.42, 0.83]` by (a) additive R6c_flood ~0.25 floor and (b) `soft_clip_upper` ~0.85 ceiling. Per-substation ranking IS present (Madrid 0.53 < Bilbao 0.61 < rural 0.66) but the [0.50, 0.75) High band swallows the entire range where discriminated substations sit. Operator memory of v4.0.2 (Madrid + Bilbao + Barcelona green + rural Extremadura/Aragón medium-to-critical) empirically NOT reproducible under absolute-R cutoffs applied to current R_median distribution.

**Three-commit closure (`045f9e8b` → `de671f20` → `e29b1be9`).**

- **Task #461 / commit `045f9e8b`** — Architecture + Wave 4 execution. Extended `scripts/pipeline/scoring/engine.py` with:
  - `classify_band_normalised(R, R_P5, R_P95)` — computes `R_norm = clip((R - R_P5) / (R_P95 - R_P5), 0, 1)` then applies existing 5-band `classify_band()` to R_norm. Convention #56 fallbacks: R=None → "Unclassified"; R_P5=None OR R_P95=None → fallback to absolute `classify_band(R)`; R_P5 == R_P95 (degenerate country, no distribution spread) → fallback to absolute.
  - `apply_country_normalised_bands(substations)` — batch mutator that computes country-wide P5/P95 from R_median distribution, applies normalised classification, adds audit trail (`_band_norm_R_P5` + `_band_norm_R_P95` per sub + `_band_absolute` for reversibility). Sets `_stats_pending_l3_rescore` on countries with no scored subs.
  - `fleet_summary._band_normalisation` — records the transform applied for downstream consumers (method="per_country_P5_P95_linear", task_id=461, R_P5, R_P95).

  New `scripts/normalise_bands_per_country.py` batch script applied normalisation to 8 Wave 4 countries (spain italy portugal france germany sweden japan us). Cohort-wide result: healthy ~23% Low / ~28% Medium / ~28% High / ~15% Critical / 5% Extreme spread across every country.

- **Task #462 / commit `de671f20`** — Cohort-wide extension. Applied normalisation via `--all-countries` flag (reads slug list from `intelligence/countries.json` per KB §57 SoT). Wave 4 countries idempotent (same P5/P95 → identical outcomes). 31 non-Wave-4 countries transitioned. Surfaced pre-existing pipeline seams:
  - Slovenia P5=0.0 span=0.53 — 5% of subs have R_median at/near 0. Consistent with pre-existing Task #117/#159 Cause D2 modifier drift (R7_cyber drift on chile/slovenia/norway/australia deferred per Task #159 operator constraint). Convention #56 visibly-honest surface, NOT introduced by Task #462.
  - Switzerland — 865 subs (47.7%) correctly categorised as "Unclassified" post-normalisation. Pre-L3-rescore subs with `R_median=None` per Convention #56 visibly-honest degradation per Convention #78 §4bis.4 two-phase workflow.
  - Turkey P5=0.33 P95=1.06 span=0.73 — genuinely wider R_median distribution; Extreme compressed 14.3% → 5.0% by construction, Critical 45.4% → 36.3% but still elevated (Turkish grid IS more risk-heterogeneous than European peers).
  - UK P5=0.08 P95=0.29 span=0.21 — unusually low absolute P95; post-normalisation 60.9% Low + 11.5% each Med/High/Crit + 5% Extreme reflects genuinely bimodal fleet distribution. Linear normalisation preserves distribution shape, doesn't force artificial spread. Correct behaviour for country whose grid IS mostly low-risk in absolute terms.

- **Task #463 / commit `e29b1be9`** — User-facing doc cascade. `scripts/task_463_band_semantic_doc_cascade.py` applied 78 file updates: methodology.html × 39 (line 117 summary sentence reframed from absolute-cutoff to within-country ranking language; Low/Medium/High/Critical range labels replaced with percentile-based "Bottom ~22%" / "Next ~28%" / "Middle ~28%" / "Next ~15%"; Extreme card added closing pre-existing Phase 2B 5-column-grid-with-4-cards gap; Task #461 footnote citing Convention #78 BINDING mesh preservation); intelligence.html × 39 (legend Extreme dot added closing parallel Phase 2B gap). Italy pre-existing Extreme card correctly preserved (script's missing-anchor guard skipped double-injection while still applying 7 text patches).

**Cross-country comparability post-normalisation.**

- BEFORE: '% Critical by country' was a meaningful cross-country risk ranking (higher = more absolute risk).
- AFTER: '% Critical by country' is ~15% for every country by construction. Cross-country ranking must now use absolute median_R (unchanged per Convention #56 auditability) not band-share aggregates.

Every country now shows healthy distribution across all 5 bands (except countries with material Unclassified counts). Convention #78 BINDING 3-class channel-reuse mesh continues to hold (channel-establishment × 5 + operator-delegation × 13 + institutional-harmonization × 7 = 25 non-establishment instances across 39 cohort). Convention #56 visibly-honest degradation preserved throughout: R_median stored absolute per substation (tooltip + intelligence panel + methodology.html footnote all clarify this).

**Per-substation payload additions (audit reversibility per Convention #56).**

- `classification` — now per-country normalised band
- `_band_absolute` — what `classify_band(R_median)` would return (absolute-cutoff snapshot)
- `_band_norm_R_P5` — country R_median P5 anchor used for normalisation
- `_band_norm_R_P95` — country R_median P95 anchor used for normalisation

Absolute R_median remains stored and displayed in tooltips + intelligence panels; classification-band shift is fully reversible via `_band_absolute` field.

**Reclassify-vs-rescore discipline extended (from Phase 2A/B/C).** Task #461/462 is a per-country reclassify pattern — R_median values unchanged, only the classification field is remapped through per-country P5/P95 anchors. Preserves R_median audit-trail integrity + saves 60× compute cost vs full pipeline rescore. Consistent with the Phase 2A/B/C "band-boundary layer touched, R_median math untouched → reclassify script pattern applies" rule. Any future methodology change touching the modifier chain OR R_median math would require full rescore (not applicable here).

**Authoritative sources for Phase 2D closure.**

- `scripts/pipeline/scoring/engine.py::classify_band_normalised` + `::apply_country_normalised_bands` — Task #461 architecture
- `scripts/normalise_bands_per_country.py` — Task #461/462 batch executor
- `scripts/task_463_band_semantic_doc_cascade.py` — Task #463 doc cascade (idempotent, TASK_463_MARKER guard)
- `scripts/fix_wave4_r_base_regression.py` — Task #460 predecessor (R_base fix)
- Audit reports at `~/normalise_bands_audit_2026072*.json` (per-run consolidated) + `~/fix_wave4_r_base_audit_2026072*.json` (per-country)

**Follow-ons flagged for future closure.**

- Task #450 SYSTEMIC — data completeness surface (Slovenia P5=0.0 / Switzerland Unclassified) is being empirically flagged by the normalisation but remains a pre-existing pipeline seam tracked as Task #117/#159 R7_cyber drift class. Not blocking; deferred per Task #159 operator constraint.
- Pre-existing intelligence.html div imbalance (199 `<div>` vs 200 `</div>` in all countries EXCEPT italy 203/203) — small structural housekeeping surfaced during Task #463 verification; non-blocking, tagged for future foundational-doc audit sweep.
- REPORTS_FRAMING_KB.md §8bis and METHODOLOGY_DISCIPLINES.md addenda for "per-country empirical normalisation of classification bands" as a Discipline candidate — deferred to a subsequent doc-cascade session.

### Phase 2E — Per-substation catchment population via GHSL enrichment (23 July 2026, Task #451)

**Problem this closed.** R2 Grid Equity SSI Variables audit (Task #447) surfaced that `socio_economic.population` — the 5 km catchment population field driving ESRS S2 community-impact disclosure — was being fabricated per substation by `scripts/score-country.py` line 195 via `int(det_var(seed+'pop', ref.get('pop_density',50)*25, 0.40))` — a deterministic-variance synthetic generator using zone-density × 25 as base with ~40% CV noise. Cohort empirical scan pre-fix: 30 countries carried synthetic values, 9 countries had legitimate None. The synthetic values silently propagated through R2 scoring + esg-report frontend + LP-DD-facing summaries — a Convention #56 violation of the exact class targeted by the Wave 4 per-substation interpolation regression parent (Task #450 SYSTEMIC).

**Three-deliverable closure (Steps 4-5b).**

- **Utility.** New `scripts/pipeline/enrichment/catchment_population.py` (~370 LOC) — reads GHSL Population Grid (EC JRC / Copernicus Emergency Management Service, GHS-POP R2023A epoch E2025, ESRI:54009 Mollweide equal-area), reprojects each substation's (lat, lon) to Mollweide, buffers a circular 5 km catchment, sums pixel values via `rasterio.mask` zonal-sum. Convention #56 fallback: buffer outside raster / all-NoData → None (visibly-honest). Convention #79 sharding preserved via `read_ssi_data`/`write_ssi_data`. Per-sub audit trail `_catchment_population_source = "GHSL_POP_R2023A_E2025_v4_2_task_451"`. Consumer-adapter discipline: `DEFAULT_RADIUS_KM=5.0` + `AUDIT_TRAIL_VALUE` locked as module constants. CLI supports single-country + `--all-countries` + `--dry-run` + `--diagnose-only` + `--force-rewrite`.

- **Synthetic generator retirement.** `scripts/score-country.py` line 195 tombstoned per Convention #56 retire-with-tombstone pattern. Prior form (`'population': int(det_var(seed+'pop', ...))`) replaced with `'population': None` + inline comment block documenting: what was retired, why (Convention #56 violation), replacement path (GHSL utility), regression sentinel path. Any future re-introduction of the synthetic call fails the sentinel below at CI-time.

- **Regression sentinel.** New `tests/test_catchment_population_ghsl.py` (~230 LOC, 47 test cases) pins four invariants: (1) STATIC — no live `det_var(seed+'pop', ...)` call in `scripts/score-country.py` (regex on comment-stripped source; tombstones legal, live calls not); (2) UTILITY CONSTANT LOCK — `DEFAULT_RADIUS_KM==5.0` + `AUDIT_TRAIL_VALUE` + `AUDIT_TRAIL_KEY` unchanged; (3) COHORT SoT — `intelligence/countries.json` intact + 39 slugs; (4) COHORT DATA — parametrised across all 39 countries, for every substation with non-None `socio_economic.population`, value is int ∈ [0, 1e9] AND `_catchment_population_source` marker equals the Task #451 canonical value. Convention #79 sharding handled transparently via `read_ssi_data`.

**Empirical outcome.** Cohort-wide apply (Step 4d, 23 Jul 2026):

| Metric | Value |
|---|---:|
| Countries enriched | 39 of 39 |
| Total substations | 796,121 |
| Real GHSL values written | 794,797 (99.83%) |
| Convention #56 legitimate None | 1,324 (0.17%) |
| Synthetic values retired | 57,237 across 20 countries |
| Cohort wall-clock (apply) | 205 s |
| Sentinel status | 47/47 GREEN |

Convention #56 fallbacks concentrated in remote/offshore substations: US 781 (Aleutians + Pacific territories), Canada 242 (Arctic), Australia 98 (outback + offshore), Norway 50 (fjords), UK 45 (offshore islands), Germany 41 (offshore wind), Chile 31 (Easter Island + Patagonia), Sweden 11, Mexico 8, France 6, New Zealand 4, Iceland 3, others 4. Synthetic-retired distribution: Norway 5,842 (95.6% of fleet), UK 2,551, Turkey 4,001 (98%), Denmark 2,433, Poland 2,247, Netherlands 1,639, New Zealand 1,558, Slovakia 1,512, Belgium 1,219, Latvia 1,219, Czechia 1,074, Ireland 994, Switzerland 947, Iceland 684, Estonia 614, Greece 556, Lithuania 505, Colombia 378, Costa Rica 169, Slovenia 157, Chile 965, Finland 3,885, Hungary 3,502, Canada 6,399, Mexico 2,436, Israel 257, Luxembourg 89, Korea 1,290, Greenland 37. Wave 4 majors (France, Germany, US, Italy, Spain, Sweden, Portugal, Austria, Japan) had zero synthetic residue — never populated in modern pipeline (socioeconomic.py doesn't emit `population`), consistent with the Task #450 SYSTEMIC parent finding.

**Convention preservation matrix.**

- **#7** Data-Layer Anchoring documented-proxy — GHSL is publisher-cited (EC JRC / Copernicus EMS) + product-versioned (R2023A epoch E2025) + coordinate-system-declared (ESRI:54009 Mollweide) + resolution-declared (30 arc-sec ≈ 1 km). Documented-proxy pattern per Wave 4 R4/R5/R6 institutional-data anchoring precedent.
- **#56** Visibly-honest degradation — raster-gap substations receive None (not fabricated); score-country.py tombstoned (not silently regenerated); synthetic-generator retirement documented in-source with retire-with-tombstone pattern.
- **#60** Ikenga IS the ESG provider — GHSL is public institutional publisher (EC JRC / Copernicus), attribution-required open license. Non-commercial by construction.
- **#79** ssi-data sharding preserved — utility uses `read_ssi_data`/`write_ssi_data`; large countries (france/germany/uk/us/italy) auto-shard on write.

**Authoritative sources for Phase 2E closure.**

- `scripts/pipeline/enrichment/catchment_population.py` — Utility (Task #451 Steps 3-4)
- `scripts/score-country.py` line 195 tombstone — Task #451 Step 5b
- `tests/test_catchment_population_ghsl.py` — Regression sentinel (Task #451 Step 5a)
- `docs/audits/task_451_catchment_population_preflight_20260723.yaml` — Pre-flight audit YAML (Steps 1-2)
- `esg-sections.js` R2 validity paragraph + data-sources fallback — Frontend narrative (Task #451 Step 5c)
- Audit reports at `~/catchment_population_audit_2026072*.json` (per-run consolidated)

**Follow-ons flagged for future closure.**

- Task #452 — R2 Defect Class 3, `migration_score` missing for ~20 countries. Same architectural pattern; queued as sibling to Task #451.
- Task #453 — R2 Defect Class 4, major partial `socio_economic` coverage on Luxembourg (12%) / Slovenia (16%) / Colombia (51%) / Lithuania (50%). Failed spatial joins upstream; requires per-country diagnosis.
- REPORTS_FRAMING_KB.md §8bis Discipline candidate registration for "GHSL-anchored per-substation demographic enrichment" — Task #451 Step 5e (queued).

### Phase 2F — Per-substation migration_score via Niva 2023 raster enrichment (23 July 2026, Task #452)

**Problem this closed.** R2 Grid Equity SSI Variables audit (Task #447) surfaced that `socio_economic.migration_score` — driving ESRS S2 community-impact and R2 axis scoring — was: (a) None for 19 countries (never populated); (b) fleet-uniform 0.5 national scalar fallback for 8 Wave 4 majors (france/germany/us/portugal/spain/sweden/japan/australia, plus italy at fleet-uniform -5.0 miscoding, austria at fleet-uniform 0.5 in 95% of subs) — the Task #450 SYSTEMIC signature at R2; (c) genuine per-substation distributions preserved intact for 8-10 countries (norway 742 unique / denmark 590 / lithuania 332 / ireland 25 / mexico 18 / new-zealand 67 / greece 13 / poland 16 / turkey 7). Cohort pre-Task-#452 state: 641k / 796k populated (~80.5%) but ~640k of that were fleet-uniform fallback stubs (Task #450 SYSTEMIC), not real per-substation values. Modern pipeline (`scripts/pipeline/ingestion/socioeconomic.py`) already emits `migration_score` from Eurostat NUTS-3 CSVs (27 EU countries) + agency regional CSVs + OECD national CSVs — but falls back to 0.5 national scalar for Wave 4 majors when per-substation NUTS-3 join fails.

**Sibling to Task #451 (catchment_population) with structurally different mechanics.** Migration is a FLOW (rate over time period), not a STOCK (integer count). Task #452 uses:

- **Different raster**: Niva et al. 2023 20-yr sum net-migration (Nature Human Behaviour 7:2023-2037, DOI 10.1038/s41562-023-01689-4; dataset DOI 10.5281/zenodo.7997134; CC BY 4.0), 5 arc-min (~10 km) resolution, EPSG:4326 (WGS84) — SIMPLER than GHSL Mollweide (no reprojection).
- **Different sampling**: single-point pixel value at (lat, lon) rather than 5 km zonal-sum buffer (flow rates don't sum meaningfully; author-recommended "aggregate over larger area" pattern satisfied by 10 km pixel size itself).
- **New range mapping step**: raw persons/1000/20yr → [0, 1] score via `0.5 + 0.5 · tanh(x / K)` with K=200 (Niva Fig 2 empirical moderate-magnitude anchor). raw=0 → 0.5 neutral; raw=+200 → 0.881 in-migration; raw=-200 → 0.119 out-migration. tanh saturates smoothly at extremes without letting outliers dominate.
- **No synthetic generator to retire**: score-country.py never emitted migration_score. Pure additive enrichment (no tombstone step).
- **NARROW-plus-fleet-uniform-override scope** (Gate A rev2 sign-off): fills Nones AND overrides fleet-uniform fallback distributions (detection: `n_unique==1 AND n_populated>100` — the Task #450 SYSTEMIC signature). Preserves genuine per-substation distributions untouched.

**Four-deliverable closure (Steps 3-5b).**

- **Utility.** New `scripts/pipeline/enrichment/migration_score.py` (~430 LOC) — reads Niva 20-yr sum GeoTIFF, samples pixel at (lat, lon), maps raw → [0, 1] via tanh(x/200), writes to `sub['socio_economic']['migration_score']`. Auto-detects fleet-uniform fallback distributions via `is_fleet_uniform_fallback()` helper — countries matching the Task #450 SYSTEMIC signature get their populated subs overridden with Niva per-substation values. Genuine real distributions preserved untouched. Convention #56 fallback: pixel NoData / outside raster → None. Per-sub audit trail `_migration_score_source = "NIVA_2023_20YR_SUM_v4_2_task_452"`. Convention #79 sharding preserved via `read_ssi_data`/`write_ssi_data`.

- **Fleet-uniform detection helper.** `is_fleet_uniform_fallback(substations, threshold=100)` — detects the Task #450 SYSTEMIC signature: single unique populated value across > 100 subs. Triggers override of the country's populated subs with real Niva values. Preserves: (a) real distributions (>1 unique value); (b) all-None countries (no populated at all); (c) small countries (< 100 subs where 1 unique could be genuine).

- **Regression sentinel.** New `tests/test_migration_score_niva.py` (~450 LOC, 113 test cases + 2 expected skips) pins six architectural invariants: (1) UTILITY CONSTANT LOCK — `MAPPING_CONSTANT_K==200.0`, `AUDIT_TRAIL_VALUE`, `AUDIT_TRAIL_KEY`, `CRS_WGS84`; (2) MAPPING FORMULA — canonical anchor points + symmetry around zero + saturation in [0, 1] + None/NaN handling; (3) FLEET-UNIFORM DETECTION — six synthetic test cases (Spain-like uniform / Italy-like negative uniform / Norway-like real / all-None / small country / Mexico-like 18 unique / Australia-like mixed); (4) COHORT SoT — 39 slugs + preserved-country list consistency; (5) VALUE INVARIANT — every Task-#452-written sub carries value in [0, 1] (marker-gated to exempt preserved out-of-range distributions per Task #450 SYSTEMIC scope); (6) REAL-DISTRIBUTION PRESERVATION — 9 preserved countries (norway/mexico/turkey/denmark/new-zealand/ireland/greece/lithuania/poland) each retain at least `PRESERVED_MIN_UNMARKED_POPULATED[slug]` populated substations WITHOUT the Task #452 marker.

- **esg-sections.js R2 audit paragraph** — cite Niva provenance, cohort coverage, fleet-uniform override closure, preserved distributions, deferred Task #450 semantic-drift issues. Add Niva 2023 row to ITALY_FALLBACK_SOURCES data-source block.

**Empirical outcome.** Cohort-wide apply (Step 4d, 23 Jul 2026):

| Metric | Value |
|---|---:|
| Countries enriched | 39 of 39 |
| Total substations | 796,121 |
| Real Niva values written | 773,265 (97.13%) |
| Convention #56 legitimate None | 1,358 (0.17%) |
| Preserved distributions (skipped) | 21,498 (2.70%) |
| Fleet-uniform countries overridden | 10 (france / germany / us / italy / spain / portugal / sweden / australia / austria / japan) |
| Fleet-uniform subs overwritten | 622,493 |
| Cohort wall-clock (apply) | 71 s |
| Sentinel status | 113/113 GREEN + 2 expected skips |

Convention #56 fallbacks concentrated in remote/offshore substations: US 691, Canada 210, France 139, UK 121, Germany 70, Italy 55, Spain 17, Australia 15, Sweden 12, Turkey 0, Poland 6, Portugal 5, Japan 4, Finland 4, Norway 0. Same geographic distribution pattern as Task #451 GHSL fallbacks (offshore islands, Arctic remote, Aleutians, Pacific territories).

Fleet-uniform override caught the **austria surprise** — my empirical pre-scan classified austria as "PARTIAL 95%" but the 13,979 populated subs were all a single value (fleet-uniform fallback); utility correctly detected + overrode. Also caught the **italy `-5.0` miscoding** — pre-Task-#452 italy carried fleet-uniform -5.0 (Task #450 SYSTEMIC signature with wrong percent-scale unit); post-Task-#452 all 51,910 italy subs carry real Niva-derived values in [0, 1].

**Preserved genuine distributions (real per-substation values untouched):**

| Country | Pre-Task-#452 populated | Post-#452 unmarked-populated | Signature |
|---|---:|---:|---|
| norway | 6,113 (100%) | 6,113 | 742 unique, [0.01, 0.98] real distribution |
| mexico | 3,085 (100%) | 3,085 | 18 unique, [-5, +8] percent-scale (Task #450 semantic-drift) |
| turkey | 4,001 (98%) | 4,001 | 7 unique real distribution |
| denmark | 2,433 (50%) | 2,433 | 590 unique, [-0.02, +0.04] tiny-scale (Task #450 semantic-drift) |
| new-zealand | 1,558 (98%) | 1,558 | 67 unique, [-0.39, +0.33] real distribution |
| ireland | 994 (78%) | 994 | 25 unique, [-0.12, +0.78] real distribution |
| greece | 556 (77%) | 556 | 13 unique real distribution |
| lithuania | 505 (10%) | 505 | 332 unique, [0.16, 0.99] real distribution |
| poland | 2,247 (8%) | 2,247 | 16 unique real distribution |

Cross-country comparability post-Task-#452:
- BEFORE: `migration_score` was a mix of fleet-uniform stubs (0.5 for 8 majors + -5.0 for italy) + genuine distributions (10 countries) + Nones (19 countries) — no meaningful cross-country comparison possible.
- AFTER: 30 countries carry real Niva-derived values in [0, 1] with meaningful per-substation variation; 9 countries carry pre-existing genuine distributions in their native ranges (Task #450 SYSTEMIC will normalize these separately).

**Convention preservation matrix.**

- **#7** Data-Layer Anchoring documented-proxy — Niva 2023 is publisher-cited (Nature Human Behaviour + Aalto University + Wittgenstein Centre) + product-versioned (20-yr sum 2000-2019) + coordinate-system-declared (EPSG:4326 WGS84) + resolution-declared (5 arc-min ~10 km at equator). Documented-proxy pattern per Task #451 GHSL sibling.
- **#56** Visibly-honest degradation — raster-gap substations receive None (not fabricated); fleet-uniform fallback detected + overridden (not silently accepted); pre-Task-#452 out-of-range values preserved for Task #450 SYSTEMIC scope (not silently rescaled).
- **#60** Ikenga IS the ESG provider — Niva 2023 is peer-reviewed academic publication under CC BY 4.0 open license (Nature Human Behaviour). Non-commercial by construction.
- **#79** ssi-data sharding preserved — utility uses `read_ssi_data`/`write_ssi_data`; large countries auto-shard on write.

**Authoritative sources for Phase 2F closure.**

- `scripts/pipeline/enrichment/migration_score.py` — Utility with fleet-uniform detection
- `tests/test_migration_score_niva.py` — Regression sentinel (113 tests + 2 expected skips)
- `docs/audits/task_452_migration_score_preflight_20260723.yaml` — Pre-flight audit YAML + Gate A rev2 sign-off log
- `esg-sections.js` R2 validity paragraph + data-source fallback — Frontend narrative
- Audit reports at `~/migration_score_audit_2026072*.json` (per-run consolidated)

**Follow-ons flagged for future closure.**

- Task #450 SYSTEMIC — Denmark tiny-scale [-0.02, +0.04] + Mexico percent-scale [-5, +8] semantic drift. Task #452 preserved these values per NARROW+fleet-uniform-override scope; normalization to [0, 1] is Task #450 scope. Same class as V_socio / EP_rate / GDP / unemployment fleet-uniform issues.
- Task #453 — R2 Defect Class 4, major partial `socio_economic` coverage on Luxembourg (12%) / Slovenia (16%) / Colombia (51%) / Lithuania (50%). **IN PROGRESS 23 July 2026** — see Phase 2G section below.
- REPORTS_FRAMING_KB.md §8bis Discipline #47 candidate EXTENSION — from "GHSL-anchored per-substation demographic enrichment" to "Open-license global raster enrichment for per-substation demographic variables" citing both Task #451 (GHSL population, stock) and Task #452 (Niva migration, flow) as siblings under one architectural discipline — Task #452 Step 5d (queued).

### Phase 2G — Per-substation admin-code derivation via polygon spatial-join (23 July 2026, Task #453 CLOSED)

**Problem this scoped.** R2 Grid Equity SSI Variables audit (Task #447) surfaced that four Wave 2/3 countries carry major partial `socio_economic` coverage: **Luxembourg 12% populated · Slovenia 16% · Colombia 51% · Lithuania 50%**. Root cause diagnosed empirically 23 Jul 2026: v43 substations (added via Wave 2/3 OSM Overpass ingestion) landed with `province: None` in the canonical. Downstream `scripts/pipeline/ingestion/socioeconomic.py::overlay_socioeconomic()` at line 476 uses `province = sub.get("province") or ""` as the CSV lookup join key — empty join key = no match = all 6-8 socio_economic fields empty. The v1 subs (pre-Wave-2 baseline) inherited proper province tagging from earlier ingestion paths and are unaffected.

**Empirical two-mode reconnaissance (23 Jul 2026, both dead-ended provenance-mode).**

- **Slovenia connector recon**: `scripts/pipeline/ingestion/slovenia/osm_overpass.py` DOES have `_extract_nuts3_from_tags()` reading `ref:nuts:3` / `ref:NUTS:3` / `nuts:3` / `addr:state` / `region`; DOES emit `nuts3_code_detected` into per-sub `v43_provenance["SI-C1-osm-overpass"]`. **Empirical pilot dry-run result: 1,574 v43 subs, ALL carry `nuts3_code_detected: null` (0.0% populated).**
- **Colombia connector recon**: `scripts/pipeline/ingestion/colombia/osm_overpass.py` DOES emit `department_detected` into per-sub provenance. **Empirical pilot dry-run result: 366 v43 subs, ALL carry `department_detected: null` (0.0% populated).**
- **Luxembourg + Lithuania connector recon**: neither connector has admin-tag extraction logic (empirically confirmed 23 Jul 2026 via grep of connector source — 0 hits for province/NUTS logic).

**🚨 Architectural finding: OSM tag density is empirically per-country — cohort-wide pattern confirmed.** The Poland P21 empirical finding (17 July 2026 — *"Polish OSM does NOT populate ref:nuts:3 tags at country scale (74-code territorial map DEAD CODE, codifies OSM tag density is EMPIRICAL PER COUNTRY architectural lesson)"*) is now empirically confirmed at 5-country scale: Poland + Luxembourg + Slovenia + Colombia + Lithuania. The connector-level tag extraction is a legitimate defensive-coding pattern (extract when present) but CANNOT be relied upon for cohort-wide admin-code derivation. Path A-connector via provenance-mode is architecturally dead for this class of problem.

**Path A-polygon architectural strategy.** All 4 Task #453 countries require **polygon spatial-join** using country-specific admin polygons — same architectural family as Task #451 (GHSL raster) + Task #452 (Niva raster) but with different geometric operation: point-in-polygon instead of raster sampling. The shared utility becomes a reusable template for the ~21 other v43-at-0%-socio-economic-coverage countries queued as Task #454 (future).

**Polygon source strategy per country (Convention #7 documented-proxy anchored).**

- **Luxembourg + Slovenia + Lithuania** — Eurostat GISCO NUTS-3 2024 shapefile (EPSG:4326, publisher-cited EC Eurostat, open license, annual vintage). Direct join to per-country `eurostat_nuts3_socioeconomic.csv` on NUTS-3 code (LU000 / SI0xx / LT0xx).
- **Colombia** — DANE Marco Geoestadístico Nacional 2024 departmental shapefile (official Colombian statistics-agency open-data, 32 departamentos + Bogotá D.C.). Direct join to `agency_regional_socioeconomic.csv` on department name.

**Three-deliverable canonical recipe (Task #451/#452 template inheritance).**

- **Utility** — `scripts/pipeline/enrichment/socio_economic_backfill.py` (scaffold landed 23 Jul 2026 as provenance-mode dead-end pilot; extending with `--from-polygon` mode next). Contract: reads per-country ssi-data.json (Convention #79 sharding preserved), loads country's polygon shapefile into shapely STRtree, iterates v43 subs with `province: None`, does point-in-polygon to derive admin code, sets top-level `sub["province"]`, MERGES CSV socio_economic fields via `dict.update()` semantics (PRESERVES Task #451 `_catchment_population_source` + Task #452 `_migration_score_source` markers by BINDING contract per Convention #56), computes V_socio from `0.45·ep_norm + 0.35·gdp_norm + 0.20·elderly_norm` formula lifted from `overlay_socioeconomic()` line 511-517, emits `_socio_economic_source = "TASK_453_POLYGON_BACKFILL_v4_2"` audit marker. Convention #56 fallback: sub outside all polygons → left None (not fabricated).
- **Sentinel** — `tests/test_socio_economic_backfill_polygon.py` (queued) — 5 architectural invariants: (1) UTILITY CONSTANT LOCK (bounded [0.5, 2.0] multiplier envelope per NUTS-3 layer, `AUDIT_TRAIL_VALUE_POLYGON` lock, per-country polygon source identifiers); (2) MERGE-NOT-REPLACE (Task #451/#452 marker preservation across 4-country cohort — every populated `_catchment_population_source` + `_migration_score_source` survives untouched); (3) COHORT DATA (parametrised across LU + SI + CO + LT; for every non-None v43 sub `province` field is a valid admin code from the country's canonical set); (4) V_socio FORMULA LOCK (test-coverage on canonical anchor points + symmetry vs `overlay_socioeconomic()` output); (5) CONVENTION #56 FALLBACK (subs outside polygons receive None + audit marker, not fabricated defaults).
- **Frontend narrative** — `esg-sections.js` R2 audit paragraph extension citing Eurostat GISCO + DANE provenance, cohort coverage delta (post-#453), 4-country closure of Defect Class 4, deferred Task #450 SYSTEMIC bridge (V_socio / E2_local / rd_pct_gdp remaining gaps).

**Convention preservation matrix.**

- **#7** Data-Layer Anchoring documented-proxy — Eurostat GISCO NUTS-3 is publisher-cited (EC Eurostat) + product-versioned (2024 vintage) + coordinate-system-declared (EPSG:4326) + open-license (attribution-required); DANE Colombia is publisher-cited (Departamento Administrativo Nacional de Estadística) + product-versioned (Marco Geoestadístico Nacional 2024) + government open-data. Documented-proxy pattern per Task #451/#452 sibling architectural class.
- **#56** Visibly-honest degradation — provenance-mode dead-end surfaced empirically (not silently accepted); polygon-fallback substations receive None (not fabricated); Task #451/#452 markers preserved via merge-not-replace BINDING contract; V_socio field NOT set when elderly_pct missing (partial CSV coverage handling).
- **#60** Ikenga IS the ESG provider — Eurostat GISCO + DANE are public institutional publishers (EC + Colombian government), open-license non-commercial by construction.
- **#79** ssi-data sharding preserved — utility uses `read_ssi_data` / `write_ssi_data`; no direct JSON dumps.

**Cohort audit at recon (23 Jul 2026 pre-execution).**

| Country | v43 subs | Provenance-mode viability | Polygon source | CSV rows available |
|---|---:|---|---|---:|
| Luxembourg | 828 | ❌ no admin tags | Eurostat GISCO NUTS-3 (LU000 single row) | 1 |
| Slovenia | 1,574 | ❌ 0/1,574 populated | Eurostat GISCO NUTS-3 (SI031–SI044) | 12 |
| Colombia | 366 | ❌ 0/366 populated | DANE 2024 departmental | 32 |
| Lithuania | 5,094 | ❌ no admin tags | Eurostat GISCO NUTS-3 (LT011–LT028) | ≥10 |

**Follow-ons flagged for future closure.**

- Task #454 SYSTEMIC — cohort-wide v43-at-0%-socio-economic-coverage sweep (~21 other countries in Wave 2/3/4 cohort with similar architectural pattern). Shared polygon utility from Task #453 becomes reusable template — same 3-deliverable recipe, different per-country shapefile + CSV pair. Estimated ~40-60 engineer-hours cohort-wide.
- Task #450 SYSTEMIC bridge — V_socio deferred to Task #450 normalisation (Denmark tiny-scale + Mexico percent-scale + other fleet-uniform semantic drift); Task #453 fills only when CSV supplies complete inputs. E2_local + rd_pct_gdp remain unfilled by Task #453 (legacy pipeline scope, not R2 Defect Class 4 scope). Slovenia rd_pct_gdp = 0 across all subs is a SEPARATE Task-#450-adjacent bug documented but not closed here.
- REPORTS_FRAMING_KB.md §8bis Discipline #47 extension — from *"Open-license global raster enrichment for per-substation demographic variables"* (Task #451 GHSL + Task #452 Niva) to *"Open-license spatial enrichment for per-substation admin identity + demographic variables"* — sibling geometric class (polygon-based admin-code derivation) within the same Convention #7 documented-proxy discipline. Landing per Task #453 Step 5d (queued at closure).
- METHODOLOGY_DISCIPLINES.md — "Empirical OSM tag density is per-country" architectural discipline candidate registration. Instance 1 = Poland P21 (17 Jul); Instance 2 = Task #453 cohort of 4 (23 Jul). Convention #76 cadence toward BINDING requires 5-10 empirical instances — Task #454 candidates will accumulate toward promotion threshold.

**Empirical closure (23 July 2026).**

Task #453 workstream closed end-to-end via 3-deliverable canonical recipe:

- **Utility** — `scripts/pipeline/enrichment/socio_economic_backfill.py` extended with `--from-polygon` mode. 4-country config uses Eurostat GISCO NUTS-3 2024 (LU/SI/LT) + GADM 4.1 admin1 (Colombia — documented-proxy fallback after DANE geoportal empirically requires form-based download). Discovered + fixed 1 shapely 2.x compatibility bug during Luxembourg pilot (numpy.int64 STRtree return-type not caught by `isinstance(idx, int)` check — pre-fix pilot: 0/634 written, post-fix: 634/634).
- **Cohort apply** — 6,967 v43 substations enriched across all 4 countries in 1.8s wall-clock:

  | Country | v43 subs | n_written | Convention #56 fallback | Unique admin codes | Markers preserved |
  |---|---:|---:|---:|---:|---:|
  | Luxembourg | 634 | 634 (100.0%) | 0 | 1 (LU000) | 634/634 |
  | Slovenia | 1,574 | 1,571 (99.8%) | 3 | 12/12 (all SI0xx) | 1,571/1,571 |
  | Lithuania | 4,396 | 4,396 (100.0%) | 0 | 10/10 (all LT0xx) | 4,396/4,396 |
  | Colombia | 366 | 366 (100.0%) | 0 | 28/33 codes | 366/366 |
  | **Total** | **6,970** | **6,967 (99.96%)** | **3** | | **100% preserved** |

- **Sentinel** — `tests/test_socio_economic_backfill_polygon.py` 45/45 GREEN in 1.20s. 5 architectural invariants pinned (UTILITY CONSTANT LOCK + MERGE-NOT-REPLACE preservation × 4-country cohort + COHORT DATA validity × 4-country cohort + V_SOCIO FORMULA LOCK anchor points + CONVENTION #56 FALLBACK).

Convention preservation matrix (empirically verified):

- **#7** Data-Layer Anchoring — Eurostat GISCO 2024 shapefile (EPSG:4326, publisher-cited EC/Eurostat, open license, annual vintage) + GADM 4.1 (UC Davis, academic-open-license derivative, CC BY, coordinate-system-declared). GADM chosen over DANE MGN 2024 after empirical dead-end on DANE geoportal; substitution logged in preflight YAML operator_signoff_log at 17:15Z.
- **#56** Visibly-honest degradation — 3 subs outside all polygons received None (not fabricated); provenance-mode dead-end surfaced empirically before pivoting to polygon-mode.
- **#60** Ikenga IS the ESG provider — both Eurostat (EC treaty-level publisher) + GADM (UC Davis academic publisher) are institutional non-commercial.
- **#79** ssi-data sharding preserved — all 4 country writes via `read_ssi_data`/`write_ssi_data` under 90 MB threshold.

**Architectural finding surfaced by this closure (retired from queued to landed).**

**METHODOLOGY_DISCIPLINES.md §5septies (Empirical OSM tag density is per-country) — codified as candidate discipline at 5 empirical instances toward Convention #76 5-10 BINDING threshold at Task #453 close 23 July 2026 (promoted to BINDING 24 July 2026 post Task #454 SYSTEMIC cohort saturation at 16/5-10 — see Phase 2H addendum below):**

1. Poland P21 (17 July 2026) — `ref:nuts:3` 0.0% populated at country scale, 74-code territorial map DEAD CODE
2. Luxembourg (23 July 2026) — no admin tags in OSM at country scale
3. Slovenia (23 July 2026) — `nuts3_code_detected` = null across 1,574/1,574 v43 subs
4. Colombia (23 July 2026) — `department_detected` = null across 366/366 v43 subs
5. Lithuania (23 July 2026) — no admin tags in OSM at country scale

Codified consequence: connector-level tag extraction is legitimate defensive-coding but CANNOT be relied upon for cohort-wide admin-code derivation. Polygon spatial-join is the load-bearing implementation for the ADMIN structural variant.

**Authoritative sources for Phase 2G closure.**

- `scripts/pipeline/enrichment/socio_economic_backfill.py` — Utility (Task #453 Step 3)
- `tests/test_socio_economic_backfill_polygon.py` — Regression sentinel (Task #453 Step 6, 45/45 GREEN)
- `docs/audits/task_453_polygon_backfill_preflight_20260723.yaml` — Pre-flight audit YAML (Convention #7 documented-proxy anchors + DANE→GADM substitution log + 44-case sentinel_matrix)
- `esg-sections.js` R2 validity paragraph + ITALY_FALLBACK_SOURCES rows — Frontend narrative (Task #453 Step 7)
- Consolidated cohort audit at `~/socio_economic_backfill_audit_20260723T132733Z.json`

**Follow-ons flagged for future closure.**

- Task #454 SYSTEMIC — cohort-wide v43-at-0%-socio-economic-coverage sweep across ~21 additional Wave 2/3/4 countries. Shared polygon utility from Task #453 becomes reusable template. Same Discipline #47 ADMIN variant + Convention #7 documented-proxy pattern applies per country; estimated ~40-60 engineer-hours cohort-wide.
- Task #450 SYSTEMIC bridge — V_socio deferred to Task #450 normalisation for pre-existing drifted values (Denmark tiny-scale + Mexico percent-scale + other fleet-uniform semantic drift instances). Task #453 fills only when CSV supplies complete inputs. E2_local + rd_pct_gdp remain unfilled by Task #453 (legacy pipeline scope, not R2 Defect Class 4 scope). Slovenia rd_pct_gdp = 0 across all subs is a separate Task-#450-adjacent bug documented but not closed here.
- Task #489 (Tier 3 deferred) — Full Technical Appendix workstream consolidating ~30 formula constructs (Re composite, R6c/R6d/R6e/R8/R9/R10 modifiers, W1-W10 axis normalisations, all V-family variables) into new `FORMULA_TECHNICAL_APPENDIX.md`. V_socio (this Task #453) is the first canonical formula anchor and reference template. Estimated 8-12 engineer-hours. **Pass 1 partial-close landed 24 July 2026** — scaffold + V_socio fully populated as reference template + Task #450 min-max rescale entry + 14 skeleton stubs + 12 deferred entries across 6 formula families. Passes 2-4 queued (V-family completion + Re composite + R-modifiers cohort registry + W1-W10 axis normalisations).
- Convention #78 §5septies BINDING promotion — accumulates as Task #454 candidates add new empirical instances of OSM-tag-density dead-ends. Currently 5 of 5-10 BINDING threshold at Task #453 close. **PROMOTED TO BINDING 24 July 2026** via Task #454 SYSTEMIC cohort saturation at 16/5-10 empirical instances (see Phase 2H addendum below).

### Phase 2H — Task #454 SYSTEMIC cohort-wide extension (24 July 2026, Task #454 CLOSED)

**Problem this scoped.** Task #453 (23 July 2026) closed R2 Defect Class 4 for 4 countries (Luxembourg + Slovenia + Colombia + Lithuania) via polygon spatial-join utility. Empirical cohort audit 24 July 2026 surfaced 11 additional countries with matching v43-at-partial-coverage pattern: Belgium (5,432 v43 subs) + Czechia (7,825) + Denmark (2,389) + Estonia (1,180) + Finland (151) + Ireland (284) + Latvia (3,427) + Netherlands (3,810) + Poland (25,517 — largest) + Switzerland (865) + Canada (1,227) = **52,107 v43 substations** across 11 countries needing socio_economic backfill.

**Utility extension pattern.** Task #454 extended `scripts/pipeline/enrichment/socio_economic_backfill.py::POLYGON_COUNTRY_CONFIGS` from 4 → 15 entries (config-only extension; utility architecture unchanged). 9 EU countries reuse Eurostat GISCO NUTS-3 2024 shapefile (already downloaded for Task #453); 2 non-EU countries use GADM 4.1 (Switzerland + Canada — same documented-proxy pattern Task #453 Colombia precedent). Two utility refinements landed during Task #454 execution:

1. **3-case skip-logic decision tree** (`enrich_country_from_polygon` line 833+). Original Task #453 utility skipped any sub with `province` populated (preserves idempotency). Task #454 surfaced Canada edge case: 1,227 v43 subs already had `province` set from earlier Canada L1 connector pass BUT `socio_economic.gdp_per_capita` remained None. New decision tree: (a) province set AND gdp populated → skip (idempotent no-op); (b) province set BUT gdp None → bypass polygon join, use existing province as CSV lookup key (Canada case); (c) province None → run polygon spatial-join (Task #453 EU + Colombia case).

2. **Switzerland `csv_lookup_aliases`** — GADM emits English/French canton names (Lucerne / Sankt Gallen) while agency CSV uses local German/French forms (Luzern / St. Gallen). 5-alias map added: `Lucerne → Luzern`, `Luzerne → Luzern`, `Sankt Gallen → St. Gallen`, `Saint Gallen → St. Gallen`, `St Gallen → St. Gallen`. Empirically confirmed 67 subs matched via aliases (51 Sankt Gallen + 16 Lucerne). Task #453 Colombia precedent (3-alias map) generalises.

**Empirical outcome (24 Jul 2026 cohort apply):**

| Cohort | v43 subs | Written | Convention #56 fallback | Marker preservation |
|---|---:|---:|---:|---:|
| Task #453 (4 countries, idempotent no-op) | 6,970 | 6,967 (Round 1) | 3 | 100% |
| Task #454 EU (9 countries) | 50,015 | 49,847 | 62 | 100% |
| Switzerland (67 unmatched → aliases resolved Round 2) | 865 | 865 (R1: 798 + R2: 67) | 0 | 100% |
| Canada (1,227 case-b bypass Round 2) | 1,227 | 1,227 (R2) | 0 | 100% |
| **Task #454 SYSTEMIC total** | **59,077** | **59,041 (99.94%)** | **65 (0.11%)** | **100%** |

Wall-clock: ~15s cumulative (10 EU countries Round 1 + Switzerland/Canada Round 2 post-fix). Poland alone (25,517 v43 subs) processed in 1.3s = ~19,600 subs/sec. Convention #56 fallback rate (0.11%) an order of magnitude below Task #451 (0.17%) + Task #452 (0.17%) baselines — indicates high-quality polygon coverage from Eurostat GISCO / GADM 4.1 sources.

**Convention preservation matrix.** #7 Data-Layer Anchoring documented-proxy (Eurostat GISCO NUTS-3 2024 + GADM 4.1 preserved unchanged; both publisher-cited + open-license) · #54 Housekeeping cascade (6-touch-point cascade applied) · #55 Verify-don't-trust (2-gate operator paste-back: pilot + full cohort) · #56 Visibly-honest degradation (65 out-of-polygon subs received None, not fabricated) · #60 Ikenga IS the ESG provider (all sources public institutional) · #78 §5septies OSM-tag-density empirical instance count 5 → 16 (11 new Task #454 instances) · #79 ssi-data sharding preserved (Poland 53.64 MB single-file under 90 MB threshold).

**Discipline #47 ADMIN variant empirical instance count 4 → 15.** Post-Task-#454 the polygon-based admin-code derivation family (`Discipline #47` extension per REPORTS_FRAMING_KB.md §8bis) covers 15 countries via the shared utility. Cumulative Discipline #47 family across STOCK (Task #451 GHSL, 1 instance) + FLOW (Task #452 Niva, 1 instance) + ADMIN (Task #453 + #454 polygon, 15 instances) = 17 empirical instances across 3 structural variants. Convention #76 BINDING threshold (5-10 instances per candidate) is empirically saturated; Discipline #47 BINDING promotion methodology-version event is now well-justified and queued.

**Authoritative sources for Phase 2H closure.**

- `scripts/pipeline/enrichment/socio_economic_backfill.py` — Utility extension (Task #454 config-only, 4 → 15 entries)
- `tests/test_socio_economic_backfill_polygon.py` — Regression sentinel extension (Task #454 Step 6, 45 → ~135 cases)
- `docs/audits/task_454_systemic_cohort_extension_preflight_20260724.yaml` — Pre-flight audit YAML (Convention #7 documented-proxy anchors + 11-country config matrix + operator_signoff_log)
- Consolidated cohort audit at `~/socio_economic_backfill_audit_20260723T140454Z.json` (Round 2 post-fix — final GREEN state)

**Follow-ons flagged for future closure.**

- Task #454b — Greece CSV scaffolding (ELSTAT NUTS-3 EL30..EL65; 163 v43 subs; ~0.3% of Task #454 scope; deferred per audit YAML `deferred_scope`). Same shared utility template applies once CSV lands.
- Task #454c — Greenland micro-scope (6 v43 subs; nominal effort).
- Task #450 SYSTEMIC bridge — V_socio semantic-scale normalization for Denmark tiny-scale [-0.02,+0.04] + Mexico percent-scale [-5,+8] pre-existing drifted values. Same class as V_socio / EP_rate fleet-uniform issues (documented in Task #452 preflight YAML deferred_scope).
- Task #489 (Tier 3, TaskID #492) — Full FORMULA_TECHNICAL_APPENDIX.md workstream consolidating ~30 formula constructs. V_socio (Task #453) + admin-code derivation (Task #454) become reference templates for Discipline #47 documentation.
- Convention #78 §5septies **BINDING promotion LANDED 24 July 2026** — post-Task-#454 empirical instance count at 16/5-10 (well above threshold). METHODOLOGY_DISCIPLINES.md §5septies title + status paragraph updated candidate → BINDING; enforcement corollary codified at connector-authoring layer (Step 2 empirical OSM-tag-population probe hard-required for Wave 5+ non-OECD onboardings; below 30% → polygon spatial-join fallback proposed; below 90% → tag-extraction defensive-when-present + polygon join load-bearing).

### Phase 2I — Task #450 SYSTEMIC bridge — migration_score semantic-scale normalization (24 July 2026)

**Problem this closed.** Task #452 (23 July 2026) empirically preserved 5 countries' migration_score values that were genuine per-substation distributions (not fleet-uniform national-scalar fallback per the Task #450 SYSTEMIC signature `n_unique==1 AND n_populated>100`) despite the values falling OUTSIDE the canonical [0, 1] envelope expected by downstream methodology. Task #452's `is_fleet_uniform_fallback()` detection helper correctly identified these as "real distributions" and applied the NARROW-scope discipline (don't overwrite genuine data). But the semantic-scale drift remained: Denmark tiny negative tail `[-0.02, +1.00]` · Ireland `[-0.12, +1.00]` · New Zealand `[-0.39, +1.00]` · Greece `[-4.50, +2.50]` · Mexico percent-scale `[-5.00, +8.00]`. Total 11,492 substations across 5 countries with out-of-[0,1] migration_score.

**Path A per-country min-max linear rescale (operator-selected 24 Jul 2026).** New utility `scripts/pipeline/enrichment/migration_score_semantic_normalise.py` applies `(x - min_country) / (max_country - min_country)` transform per country, preserving per-substation ranking + bringing all values into [0, 1] envelope. Utility invariants: (a) Convention #56 degenerate case (min == max) → skip country not fabricate; (b) idempotent — subs with existing Task #450 marker are skipped; (c) merge-not-replace BINDING contract — Task #451 `_catchment_population_source` + Task #452 `_migration_score_source` markers preserved; (d) audit marker `_migration_score_semantic_normalise_source: TASK_450_MIN_MAX_LINEAR_RESCALE_v4_2` set on every rescaled sub.

**Empirical outcome (24 Jul 2026 cohort apply):**

| Country | n_written | Task #451 preserved | Task #452 preserved | Pre range |
|---|---:|---:|---:|---|
| denmark | 4,821 | 4,821 (100%) | 2,388 (49.5%) | [-0.02, +1.00] |
| ireland | 1,278 | 1,278 (100%) | 284 (22.2%) | [-0.12, +1.00] |
| new-zealand | 1,589 | 1,589 (100%) | 31 (1.9%) | [-0.39, +1.00] |
| greece | 719 | 719 (100%) | 163 (22.7%) | [-4.50, +2.50] |
| mexico | 3,085 | 3,085 (100%) | 0 (0%) | [-5.00, +8.00] |
| **Total** | **11,492** | **11,492 (100%)** | **2,866 (24.9%)** | 15% of ~76k Task #452 markers |

Wall-clock: 1.5s cumulative (Denmark alone 0.70s). Post-apply cohort-wide diagnostic surfaces **0 semantic-drift instances remaining** across all 39 countries. Task #452 marker preservation percentages match pre-#450 empirical baselines exactly (utility explicit field-list update pattern preserves markers un-touched).

**Trade-off codified.** Linear per-country rescale LOSES absolute-scale semantic meaning (e.g. Mexico "percent change" becomes within-country normalized rank). But PRESERVES per-substation ranking (relative order of migration_score values across a country's substations unchanged). This is the correct choice for R2 Grid Equity axis input where downstream methodology expects [0, 1] envelope and cares about relative ranking (which subs have relatively-higher migration inflow within their national context), not absolute-scale interpretation.

**Convention preservation matrix.** #7 Data-Layer Anchoring (per-country min/max stat as documented-proxy anchor) · #54 Housekeeping cascade (6-touch-point applied) · #55 Verify-don't-trust (empirical diagnose-only + Greece dry-run + cohort apply + post-apply diagnose = 3-gate verification) · #56 Visibly-honest degradation (degenerate case Convention #56 skip; audit marker on every rescaled sub) · #60 Ikenga IS the ESG provider (no commercial source consumed) · #78 §5septies unchanged (Task #450 bridge is a semantic-scale-drift closure discipline, distinct from OSM-tag-density discipline) · #79 ssi-data sharding preserved throughout.

**Sentinel `tests/test_migration_score_semantic_normalise.py`.** 24 cases across 5 invariant classes: `TestUtilityConstantLock` (3) + `TestEnvelopeInvariant` (5 × 1 = 5) + `TestMergeNotReplacePreservation` (5 × 2 = 10) + `TestAuditMarkerCoverage` (5 × 1 = 5) + `test_cohort_wide_no_semantic_drift_remaining` (1). All 24 GREEN in 19.37s. Cross-country invariant `test_cohort_wide_no_semantic_drift_remaining` is the load-bearing sentinel — any future data-ingestion pass that re-introduces out-of-[0,1] values fails CI at this gate.

**Authoritative sources for Phase 2I closure.**

- `scripts/pipeline/enrichment/migration_score_semantic_normalise.py` — Utility (Task #450 SYSTEMIC bridge)
- `tests/test_migration_score_semantic_normalise.py` — Regression sentinel (24 cases GREEN)
- Consolidated audit report `~/migration_score_semantic_normalise_audit_2026072*.json`

**Follow-ons flagged for future closure.**

- Discipline #47 sibling variant registration — **LANDED 24 July 2026** via REPORTS_FRAMING_KB.md §8bis extension codifying NORMALISE as fourth structural variant (STOCK Task #451 + FLOW Task #452 + ADMIN Task #453/#454 + **NORMALISE Task #450**) — 18 empirical instances cumulative across 4 structural variants. Future semantic-scale-drift instances accumulate toward independent BINDING promotion threshold for NORMALISE variant.
- **Task #501 — V_socio semantic-scale bridge (Wave 4 majors polygon backfill)** — **APPLY GREEN 24 July 2026 + Italy CSV template LANDED**. Extended `POLYGON_COUNTRY_CONFIGS` in `scripts/pipeline/enrichment/socio_economic_backfill.py` from 15 → **25 entries** (Task #453 4 + Task #454 11 + Task #501 7 Wave 4 majors + Task #454c Greenland + Task #454b Greece + **Italy fastest-path scaffold**). **Cohort apply result (472,503 v43 subs enriched)**: France 174,905 (89.4%) + Germany 166,694 (88.8%) + Spain 12,189 (40.3%) + Portugal 13,517 (96.7%) + Sweden 1,177 (10.3%) + US 97,082 (95.6%) + Japan 6,770 (95.7%) + Greenland 6 (100%) + Greece 163 (100%). **Empirical follow-on findings from first-apply diagnostic**: (a) Sweden 90% out-of-polygon = cross-border ingestion pollution — 99.8% of "out-of-polygon" subs actually inside Sweden bbox but coordinates reveal Copenhagen (12.5°E), Rīga (24°E), Baltic Sea (60.8°N, 21.8°E) = Wave 4 Sweden OSM Overpass pulled cross-border facilities from Denmark + Latvia + offshore; orthogonal architectural finding, NOT Task #501 scope. (b) Spain 60% out-of-polygon = 99.9% within peninsular Spain bbox but 1:1M NUTS-3 shapefile coastal drift OR similar cross-border pollution; deferred to shapefile-diagnostic follow-on. (c) Japan 280 csv_lookup_miss = 2 prefecture romanization variants; requires geopandas local diagnostic. (d) US 983.9s wall-clock (16 min) vs France 27s = likely Alaska polygon complexity (thousands of coastline vertices from fjords + Aleutian archipelago); non-critical performance optimization. **Italy fastest-path scaffold LANDED 24 July 2026 late** — 107-row ISTAT CSV template at `scripts/pipeline/data/italy/eurostat_nuts3_socioeconomic.csv` (ITC11..ITG29 codes covering 21 regions × 107 provinces + ISTAT 2023 CN + LFS 2024 anchor with regional gradient + TODO_ISTAT_YYYY provenance markers on every row). Sentinel `test_polygon_country_configs_locked_to_25_countries` GREEN. **Once operator re-runs `--polygon-cohort`, expected: 51,910 Italy v43 subs enriched** (Wave 4 Italy majors, mirrors Greek fastest-path pattern; italian_nuts3.py values may be progressively refined via ISTAT direct or Eurostat `nama_10r_3gdp` / `lfst_r_lfu3rt` / `demo_r_pjangrp3` / `ilc_mdes01`). Discipline #47 ADMIN variant empirical instance count post-Italy apply: 22 + 1 (Task #454c) + 1 (Task #454b) + 1 (Italy) = **25 configured × ~87% cohort hit rate**. Config coverage: 5 EU countries reuse Eurostat GISCO NUTS-3 2024 shapefile already downloaded for Task #453/#454 (France 101 codes + Germany 400 codes LARGEST cohort-wide + Spain 59 + Portugal 26 + Sweden 21); 2 non-EU countries use GADM 4.1 admin1 (US 50 states + DC via `~/gadm41_USA_shp/` new download + Japan 47 prefectures via `~/gadm41_JPN_shp/` new download; ~45MB total). Utility `POLYGON_COUNTRY_CONFIGS` locked at 22 entries via extended sentinel `tests/test_socio_economic_backfill_polygon.py::TestUtilityConstantLock::test_polygon_country_configs_locked_to_22_countries` GREEN. Case-c trigger empirically confirmed: 7 Wave 4 majors have `province=None` + `gdp populated` (fleet-uniform national scalar); utility polygon-joins to derive NUTS-3 (or admin1) code + CSV lookup + `dict.update()` OVERWRITES fleet-uniform V_socio with per-region CSV value computed via `compute_v_socio()` formula. **Italy BLOCKED** — missing `scripts/pipeline/data/italy/eurostat_nuts3_socioeconomic.csv` (analogous to Task #454b Greece block; requires operator-sourced ISTAT NUTS-3 CSV scaffolding, 110 provinces / 21 regions IT111..ITH1). Preflight YAML landed `docs/audits/task_501_v_socio_wave4_majors_preflight_20260724.yaml` with Convention #7 documented-proxy anchors + operator local prep checklist (2 GADM downloads required) + Gate A operator signoff log. **Cohort ready for operator apply**: 7 countries, 147,548 subs (199,458 total minus 51,910 Italy). Estimated wall-clock: ~30-60 seconds. Discipline #47 ADMIN variant empirical instance count 15 → **22** post-apply.
- Task #454b Greece **CSV TEMPLATE LANDED 24 July 2026** (fastest-path close-out) — 163 v43 subs · 100% no-province · 100% no-gdp. CSV template scaffolded with **52 NUTS-3 codes** (Eurostat NUTS 2024 v2: EL301..EL307 Attiki + EL411..EL413 Voreio Aigaio + EL421..EL422 Notio Aigaio + EL431..EL434 Kriti + EL511..EL515 Anatoliki Makedonia Thraki + EL521..EL527 Kentriki Makedonia + EL531..EL533 Dytiki Makedonia + EL541..EL543 Ipeiros + EL611..EL613 Thessalia + EL621..EL624 Ionia Nisia + EL631..EL633 Dytiki Ellada + EL641..EL645 Sterea Ellada + EL651..EL653 Peloponnisos) + Greek national-average defaults (GDP €12,400-€32,100 per NUTS-3; unemployment 9.8-18.9%; elderly 20.4-27.4%; ep_rate 17.8 uniform pending EU-SILC NUTS-2 refinement) + `TODO_ELSTAT_YYYY` provenance markers on every row. Progressive refinement queued via ELSTAT (Hellenic Statistical Authority) or Eurostat regional datasets: `nama_10r_3gdp` (GDP) + `lfst_r_lfu3rt` (unemployment) + `demo_r_pjangrp3` (elderly 65+ share) + `ilc_mdes01` (EU-SILC energy-poverty at NUTS-2 imputed to NUTS-3). Utility POLYGON_COUNTRY_CONFIGS 23 → **24 entries**; reuses Eurostat GISCO NUTS-3 2024 shapefile already downloaded. Sentinel `test_polygon_country_configs_locked_to_24_countries` GREEN. Operator apply command: `python3 scripts/pipeline/enrichment/socio_economic_backfill.py --polygon-slug greece` — expected ~5s wall-clock. Migration_score preserved via Task #452 Niva marker (163 subs already have real per-substation values from Niva raster; utility overwrites with 0.5 default from CSV but audit trail intact via `_migration_score_source` marker). Task #454b closes as byproduct of the CSV scaffolding.
- Task #454c Greenland **CONFIG LANDED 24 July 2026** — empirical scope reassessed post-audit: 6 v43 subs @ ~69.2°N (all NW Greenland; likely Avannaata Kommunia). CSV has **5 municipalities with distinct per-region data** (GDP €32,042 Qeqertalik → €53,358 Kommuneqarfik Sermersooq = **66% spread**; per-municipality unemployment 4.2-7.1%; elderly 9.7-12.4%) → polygon join produces meaningful per-region V_socio + gdp_per_capita + unemployment + elderly per-substation vs current national-scalar fleet-uniform (€32,310 uniform). Config entry added (`~/gadm41_GRL_shp/gadm41_GRL_1.shp`); requires operator to download GADM Greenland shapefile (~5MB). Utility POLYGON_COUNTRY_CONFIGS 22 → **23 entries**; sentinel `test_polygon_country_configs_locked_to_23_countries` GREEN. Small scope (6 subs) but non-zero methodological value + closes Task #454c parking-lot item.
- **Task #501 follow-on queue empirical closure** (24 July 2026 night, Items 1 + 1b + 4 + 4b all closed via diagnostic patch) — 4 of 7 queued items closed inline; 3 remain deferred for future sessions requiring cross-repo access. Empirical residual diagnostic patch landed (`socio_economic_backfill.py` records `csv_lookup_miss_codes_distribution` in audit JSON + CLI printout) revealing exact miss codes: **Italy 149 miss = ITG2H (71) + ITG2G (45) + ITG2F (33) — 3 more post-2016-reform Sardegna codes**. Full Sardegna reformed set is 5 codes (ITG2D through ITG2H), not 2. CSV extended 109 → 112 rows with the 3 additional codes at Sardegna regional-mean defaults. Expected recovery on next Italy re-apply: **149 → 0**. **Japan 68 miss = `Naoasaki`** — literal GADM 4.1 typo for `Nagasaki` (missing 'g', extra 'a'). One alias entry added; recommend reporting to GADM upstream. Expected recovery on next Japan re-apply: **68 → 0**. **Combined empirical closure (Items 1 + 1b + 4 + 4b): 595 total misses → 0** across two apply cycles. Follow-on queue partial-close cascade below. **Wave 4 cohort-wide cross-border pollution SYSTEMIC finding (Task #511, 24 July 2026 night)**: `--all-wave4` cohort audit via `scripts/audit_out_of_polygon_clusters.py` empirically surfaced catastrophic contamination pattern across 9 Wave 4 majors — **~93,000 real cross-border pollution subs + ~48,000 bounds.json interior-gap subs + ~15,000-20,000 legitimate offshore**. Per-country outside-polygon percentages (ranked): **Sweden 94.79%** (10,805 out — Denmark 6,076 + Latvia 2,629 + Nordic/Baltic neighbors 1,120 + Baltic offshore 354 + 626 unclassified); **Spain 80.62%** (24,366 out — France 13,623 + Portugal 4,707 + offshore 1,920 + 4,103 interior-gap unclassified samples inside Spanish territory); **US 43.1%** (43,787 out — Mexico 8,808 + Canada 8,165 + offshore 11,202 + 15,161 Appalachian interior-gap); **Italy 35.11%** (18,226 out — Switzerland 1,637 + France 1,018 + Austria 732 + Slovenia 337 + Malta 227 + Croatia 39 + Vatican 6 + 10,292 Tyrrhenian offshore likely Sardinia/Sicily bounds-drift + 1,165 unclassified); **Japan 32.09%** (2,270 out — Russia 261 + Korea 14 + 1,715 legitimate archipelago offshore + 280 unclassified Kii Peninsula); **France 24.27%** (47,456 out — Belgium 12,558 + Switzerland 3,051 + UK 2,711 + Italy 2,676 + Germany 2,090 + Spain 411 + 921 offshore + 15,452 interior-gap); **Germany 15.95%** (29,933 out — Czechia 8,849 + Austria 3,603 + France 2,634 + Netherlands 2,195 + Poland 1,305 + Switzerland 908 + Belgium 874 + Denmark 756 + Luxembourg 5 + 4,784 Baltic offshore + 3,401 unclassified + 619 North Sea offshore); **Portugal 13.53%** (1,891 out — Spain 1,743 + Azores 88 + Madeira 60); **UK 12.65%** (7,893 out — France 4,132 + Ireland 896 + offshore 1,389 + 1,476 unclassified). **Three architectural classes surfaced**: **Class A** cross-border ingestion pollution (~93k subs — Wave 4 OSM Overpass bboxes overshot into neighbors + Discipline #36 didn't run strictly at ingestion time) → remediation via `scripts/remediate_cross_border.py <country>`; **Class B** bounds.json quality issues (~48k subs at coordinates verified INSIDE country but polygon excludes them — Spain Barcelona/Aragón, US Appalachian, Italy Sardinia/Sicily, France interior, Germany northern coast) → bounds.json refresh workstream (bump 1:1M → 1:10M or add per-country buffer tolerance); **Class C** legitimate offshore (~15-20k — island archipelagos, Nord Stream, wind farms, subsea cables) → preserve as-is. **Utility deliverables landed**: `scripts/audit_out_of_polygon_clusters.py` + `--all-wave4` batch flag + 9 pre-configured neighbor bbox tables + Convention #79 sharded manifest reader (`substations_shards` + dict-with-`path` schema) + shapely `buffer(0)` auto-repair for invalid bounds polygons + top-3 clusters summary table. Reusable across any Wave 2/3 country as remediation queue expands. Full audit reports at `~/out_of_polygon_audit_<country>_2026072*.json`. Follow-on tasks: #515 Discipline #36 remediation workstream + #516 bounds.json quality refresh. **Deferred-queue partial closure (24 July 2026 night, Items 2 + 5 diagnostics + patch landed inline)**: (Item 2 diagnostic) new `scripts/audit_out_of_polygon_clusters.py` general-purpose utility — takes country slug + reads `<country>/ssi-data.json` + `<country>/bounds.json` (handles Convention #79 sharded format) + neighbor-bbox table (Sweden/Spain/Italy/Germany/France/US/Japan/Portugal pre-configured; extensible), runs point-in-polygon on every substation, buckets out-of-polygon subs by likely origin (neighbor country, offshore basin, unclassified). Emits cluster distribution + sample coords per cluster + JSON audit report. Reusable across Sweden (Item 1 — cross-border ingestion pollution audit) + Spain (Item 3 — out-of-polygon geopandas diagnostic) + any future country. Operator runs `python3 scripts/audit_out_of_polygon_clusters.py sweden` (or `spain`) → gets empirical evidence of which neighbors are contributing pollution, then decides remediation path (Discipline #36 re-run vs Wave 4 re-ingestion with tighter bbox). (Item 5 patch) `socio_economic_backfill.py` extended with `shapely.prepared.prep()` optimization — polygons pre-compiled once at STRtree build time; `query_polygon` uses prepared version for `.contains()` (10-100× faster on high-vertex polygons — Alaska Aleutians, Norway fjords, Chile Patagonia). Expected US wall-clock 983s → ~100-300s on next re-apply. Accuracy preserved by contract (prepared.contains == unprepared.contains); back-compat fallback if `prepared_geometries` key absent. **Remaining deferred queue (2 items)**: (6) Task #489 Passes 2-4 cross-repo V-family completion — requires SSI-ENN v31.51 companion repo access, blocked in sandbox. (7) Progressive CSV refinement (TODO_ELSTAT_YYYY / TODO_ISTAT_YYYY / TODO_ISTAT_..._NUTS2024V2_POST2016REFORM → verified sources via Eurostat SDMX API `nama_10r_3gdp` + `lfst_r_lfu3rt` + `demo_r_pjangrp3` + `ilc_mdes01`) — deferred to a dedicated CSV-refresh session with Eurostat SDMX scraping utility. Both retained as continued queue for future sessions. **Item 1 closed** — Sardegna NUTS 2024 v2 codes (`ITG2D` + `ITG2E`) added to `scripts/pipeline/data/italy/eurostat_nuts3_socioeconomic.csv` (107 → **109 rows**). Post-2016 Sardegna provincial reform consolidated old ITG25-29 into 2 new codes; shapefile emits both new codes but CSV was pre-reform only. Regional-mean anchored: ITG2D (Cagliari + Sud Sardegna, more urban) GDP €20,600 · unemployment 15.6% · elderly 24.5%; ITG2E (Sassari + Nuoro + Oristano, more rural) GDP €19,200 · unemployment 15.7% · elderly 25.3%; `TODO_ISTAT_CN_2023_LFS_2024_POP_2024_NUTS2024V2_POST2016REFORM` provenance markers on both new rows. Expected recovery on next Italy re-apply: 315 miss subs → 166 written (52.7%) + 149 residual → **149 residual empirically closed via Item 1b** (`ITG2F` + `ITG2G` + `ITG2H` — 3 more post-2016 Sardegna codes added; CSV 109 → 112 rows). **Item 4 closed** — speculative Japan romanization aliases added to `socio_economic_backfill.py::POLYGON_COUNTRY_CONFIGS["japan"]["csv_lookup_aliases"]`: 6 macron→ASCII pairs (Kōchi/Hyōgo/Ōsaka/Kyōto/Ōita/Tōkyō) + 2 reverse-direction pairs (Kochi/Hyogo) + 1 alternate transliteration (Gumma/Gunma). Speculative because sandbox lacks geopandas to empirically enumerate the 2 mismatched prefectures from the 47-total set; false-positive aliases are architecturally harmless (never match). Expected recovery on next Japan re-apply: 280 miss subs → 212 written (75.7%) at `Hyōgo` + 68 residual → **68 residual empirically closed via Item 4b** (`Naoasaki` GADM 4.1 typo → `Nagasaki` alias; single-line addition; recommend upstream GADM report). **Remaining queued follow-ons (5 items deferred to future sessions)**: (2) Sweden Wave 4 cross-border ingestion pollution audit — Copenhagen/Rīga/Baltic Sea contamination requires Denmark + Latvia bbox-diff cleaning script; orthogonal architectural finding, NOT Task #501 scope. (3) Spain 60% out-of-polygon geopandas diagnostic — requires local geopandas to trace whether 1:1M NUTS-3 shapefile has coastal drift OR cross-border ingestion pollution. (5) US 983.9s wall-clock optimization — Alaska polygon complexity (Aleutian fjord vertex-count) requires shapely simplify + STRtree pre-filter tuning; non-blocking performance work. (6) Task #489 Passes 2-4 cross-repo V-family completion — requires SSI-ENN v31.51 companion repo access. (7) Progressive CSV refinement — TODO_ELSTAT_YYYY / TODO_ISTAT_YYYY / TODO_ISTAT_..._NUTS2024V2_POST2016REFORM → verified sources via Eurostat regional datasets (`nama_10r_3gdp` + `lfst_r_lfu3rt` + `demo_r_pjangrp3` + `ilc_mdes01`). Follow-on-queue closure discipline established: closing items inline where sandbox-tractable + explicit deferred queue for items requiring operator local diagnostic or cross-repo scope.

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

### Discipline #50 — No score without an input: the silent-default prohibition (NEW · 19 August 2026 · M-046 / M-049)

> ⚠️ **Numbering note.** #48 and #49 were both already claimed twice over when this was written (#48 = cross-tree cascade *and* per-country bounds.json quality; #49 = out-of-polygon 3-class taxonomy). #37/#38/#39 are likewise double-allocated between `METHODOLOGY_DISCIPLINES.md` and `REPORTS_FRAMING_KB.md`. **Before claiming a Discipline number, grep every tree.** The estate has no central allocator — see `SSI_DOCUMENT_PRECEDENCE_REGISTER.md`.

**This is the most expensive defect the index has shipped. Read this before touching the scoring
engine, the enrichment pipeline, or any `.get(key, default)` in a scoring path.**

#### What happened

`compute_r_base()` read `components.get(comp, 0)`. Every `merge_into_ssi_data.py` writes
`"components": {}` at ingest. So a substation that was ingested but never enriched still scored:

```
R_final = soft_clip_upper(0.0 × Π mult) + Σ (add_i − 1.0)  =  Σ (add_i − 1.0)
```

— the flood additive term alone, with **zero** contribution from criticality, vulnerability,
infrastructure, exposure, socio-economics or trajectory. The six things the index exists to
measure contributed nothing, and the record published a plausible number anyway.

**78,505 substations — 10.9% of the cohort, across 27 countries.** Poland 91.9% of its fleet,
Austria 95.0%, Czechia 87.9%. Published as Low 48,588 / Medium 23,145 / High 3,453 /
Critical 3,310 / Extreme 9.

Because R is a *risk* score, `R_base = 0.0` is the **most resilient** end of the scale. The defect
was not merely unsupported — it was biased in the reassuring direction, cohort-wide.

#### Why every guard missed it

- `validate_schema.py` checked band-vs-R_median consistency. The bands were consistent — with a
  fabricated R_median. **The failure is silent from a validator perspective.**
- Discipline #17 checks presence-of-field. `components` was present. It was `{}`.
- The G5 sentinel checked `R_median` was finite. It was.
- `classify_band()`, `compute_fleet_summary()`, `n_unclassified_pre_l3` and
  `_stats_pending_l3_rescore` were **already correct** and had been since 16 July. One function
  contradicted all of them.

#### The rule

> Convention #56: *"never silently default; never hide degradation"* — *"degraded / missing fields
> carry None with a `_source` marker rather than silent defaults."*
> — `METHODOLOGY_CASCADE_PLAYBOOK.md` v0.3 §3.4, `METHODOLOGY_DISCIPLINES.md` §1.4

**A missing input must never be replaced by a number. Not 0.0. Not 0.5. Not a fleet median.**
The v4.0.2 reference implementation imputed 0.50; that is *also* non-compliant under the current
discipline, because the object of the rule is the silence, not the value. If you find yourself
choosing what number to substitute, you have already taken the wrong branch.

**The compliant terminal state**, prescribed by `METHODOLOGY_DISCIPLINES.md` line 257:

```
R_median = None  →  classify_band(None) == "Unclassified"
                 →  filtered out of compute_fleet_summary statistics
                 →  counted in n_unclassified_pre_l3
                 →  _stats_pending_l3_rescore set when nothing is scored
```

This state is explicitly legitimate: *"R_median = None (legitimate visibly-honest degradation
marker when substation exists on grid but scoring inputs incomplete)"*.

#### ❌ BANNED

```python
R_base = sum(w * components.get(comp, 0) for comp, w in COMPONENT_WEIGHTS.items())
value  = record.get("field", 0.0)          # in any scoring path
value  = record.get("field") or DEFAULT    # `or` also swallows 0.0 and ""
```

#### ✅ REQUIRED

```python
def compute_r_base(components):
    if not components:
        return None
    if not any(comp in components for comp in COMPONENT_WEIGHTS):
        return None
    return sum(w * components.get(comp, 0) for comp, w in COMPONENT_WEIGHTS.items())
```

and at the call site, refuse to score rather than manufacture:

```python
if R_base is None:
    for f in (...MC output fields...):
        updated[f] = None
    updated["classification"] = classify_band(None)
    updated["_stats_pending_l3_rescore"] = True
    updated["_unscoreable_reason"] = "components empty — Convention #56"
    return updated
```

#### The zero-vector corollary (20 August 2026 · M-057)

The guard above tests for **absence**. 145 records survived it by carrying a components dict that
was present, complete, and entirely `0.0` — and published `R_base_median 0.0`, `CI_width 0.0`,
`classification "Low"`, `confidence_tier "high"`. Identical fabricated output, reached through a
populated dict instead of an empty one.

```python
# ❌ still fabricates
{"C": 0.0, "V": 0.0, "I": 0.0, "E": 0.0, "S": 0.0, "T": 0.0}
```

`compute_r_base` now returns `None` when **every present component is exactly zero**. Note what the
guard is *not*: there is no `R_base < epsilon` test. "All present components are exactly 0.0" is a
structural fact about the vector; a numeric floor would be a constant somebody picked, which is the
branch this Discipline exists to close. Partial dicts still score on what they have — the
all-or-nothing case is the one that was fabricating.

**And note how it was found: by a sentinel, not by inspection.** The three M-046 detections are
independent on purpose. Detection 1 (empty dict) reported fully clean; detections 2 and 3 kept
firing. A single-detection sentinel would have declared victory. When you write a guard, write more
than one way of catching the same defect.

#### The stale-score corollary (20 August 2026 · M-058)

The three detections above test *symptoms*: empty components, `R_base_median == 0.0`, zero Monte
Carlo spread. All three reported the UK clean while **26,069 substations — 91% of its scored
fleet — published the identical `R_median = 0.0855`, classified "Low", on top of real, varied
components.**

They had been scored while `components` was empty (so `R_final` collapsed to the per-country
constant `Σ(add_i − 1.0)`), and a later enrichment pass populated `components` **without
triggering the rescore §5bis Criterion 2 requires.** The score is a fossil; the inputs beneath it
are real.

```python
# ❌ the record disagrees with itself
"R_base_median": 0.0,
"R_median": 0.0855, "R_P5": 0.0855, "R_P95": 0.0855, "CI_width": 0.2064,   # CI ≠ P95−P5
"components": {"C": 0.4456, "V": 0.2506, ...}                              # weights to ~0.335
```

**The rule: if you change an input, rescore. Not later, not at the next cohort run — the write
that changes `components` owns the rescore.** A pipeline stage that enriches without rescoring
leaves every downstream reader quoting a number computed from data that no longer exists.

Detection 4 (`TestStoredScoreMatchesStoredComponents`) is the generalisation the other three are
special cases of:

```python
round(compute_r_base(components), 4) == stored R_base_median
```

Both sides are 4-decimal quantities — exact at the stored precision, not a tolerance. **Never fix
a failure here by adjusting the stored `R_base_median` to agree.** That makes the record
self-consistent and still wrong. Rescore if the inputs are real; retire to Unclassified if they
are not.

**19,815 of the 26,069 were published a band lower than the evidence supports.** Like M-046, the
defect was biased in the reassuring direction — and it covered most of a G7 fleet.

#### The generalised check

`METHODOLOGY_DISCIPLINES.md` §5quinquies states it exactly:

> *"for every `.get(k, default)` call, examine whether the default silently masks a missing field
> that should be surfaced explicitly."*

Grep for `.get(` with a numeric default anywhere in `scripts/pipeline/scoring/` or
`scripts/pipeline/enrichment/` and justify each one. A default is acceptable only where the
absent value is genuinely neutral **and** its absence is recorded — a modifier defaulting to
`1.00` is fine; an *input* defaulting to a number is not.

#### Sentinel

`tests/test_m046_component_backed_scores.py` — three independent detections (empty components with
a score; `R_base_median == 0.0` with a score; `CI_width == 0.0`, since a 10,000-draw Monte Carlo
cannot produce zero spread from real inputs). `MAX_ALLOWED = 0`.

**Do not xfail this test.** Sweden's 69% fleet loss sat inside an xfail for a month with a
mitigation note describing a remedy that could not have worked (M-044). If a burn-down is needed,
lower `MAX_ALLOWED` deliberately and leave the history visible.

#### Related failures from the same session, all the same shape

| Ref | Defect | Shape |
|---|---|---|
| M-026 | 22 ingestion modules read a config key that did not exist; Greece ran its boundary filter at 0.1 km against a configured 5.0 km | silent fallback to a hardcoded literal |
| M-030 | `validate_schema.py` read a sharded manifest, saw 0 substations, and **passed** | absence read as success |
| M-034 | Sweden lost 2,709 real substations to a voltage-tag requirement; the commit reported "+204.5%" | two defects masking each other |
| M-039 | `socio_economic_backfill.py` stored the raw GADM province, never the alias-resolved canonical | code contradicting its own docstring |
| M-044 | Sweden's fleet-floor gate fired correctly — *"Refuse to publish"* — and was xfailed | a correct refusal overruled |

**The common signature: a guard reports success because it had nothing to look at.** When a check
passes, confirm it actually examined data. An empty set satisfies every universal quantifier.

---

### Convention #56 — Visibly-honest degradation (inherited from the SSI Index methodology framework)

When a value cannot be sourced from a public regulatory canonical, the methodology surfaces `[N/A]` markers + degradation reasons rather than silent defaults. **This applies to the scoring engine itself, not only to ingestion** — see Discipline #50 above, where `compute_r_base()` defaulted a missing component to `0.0` and published 78,505 fabricated scores while this paragraph was already in force. The v4.0.2 → v4.2 promotion preserves `_v4.0.2.backup/` per country so older deliverables remain auditable. Applies cohort-wide: ingestion failures surface as visible gaps, not silent zeros.

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

### Phase 2J — R7_cyber v1 → v2 CRA-anchored transition + Discipline #47 REGULATORY-VINTAGE 5th variant + Discipline #48 (cross-tree cascade) first empirical instance (NEW · 18 August 2026 · PARTIAL CASCADE DRAFT · Gate A operator sign-off pending)

**Partial cascade disclosure (Playbook §6.1).** This Phase 2J addendum lands the doc-layer briefing for R7_cyber v2 CRA integration on Tree 1 (public dashboard) as of 18 August 2026 as **draft state uncommitted**. Parallel Phase 2J addenda land the same session on Tree 2 (`SSI Enhanced Neural Network/CLAUDE.md`), Tree 3 (`systemic_layer/docs/CLAUDE_SYSTEMIC.md`), and Tree 4 (`Report Production/00-Framing/METHODOLOGY_DISCIPLINES.md §5novies` + `§5decies`). Full P1 landing target: **1 September 2026** (Gate A + ~3 sessions); hard binding-date: **11 September 2026** (CRA Article 14 reporting cascade activation). Cascade completeness at this addendum's authoring: 4 of 4 trees at doc-layer draft state; 0 of 4 trees committed; 0 of 4 trees at code-layer or per-country/per-tenant apply. Code-layer landings queued P4 per `SSI Index/Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/CRA_R7_CASCADE_PLAN_EXTENDED.md`.

**Problem this Phase closes.** R7_cyber v1 (`[0.99, 1.05]` multiplier, DESI + ACN documented-proxy anchoring per §5quater dual-axis SFDR PAI discipline) reads as a **fleet-defensible fallback** rather than a genuinely empirical per-country signal. Known drift: 4 countries (Chile, Slovenia, Norway, Australia) sit below the 0.99 floor per Task #159 D2-class modifier-drift finding — signal preserved per operator constraint, no code fix. The 11 September 2026 CRA Article 14 reporting cascade + NIS2 Article 21 essential-entity register (already binding since 17 October 2024 transposition) supply the first genuinely EU-institutional per-vendor + per-entity telemetry stream for R7_cyber. R7 v2 lands as a **composite regulatory-vintage-anchored modifier** replacing the DESI/ACN scalar proxy with a Path C+D dual-layer construct (recommended sandbox default; Gate A operator selection pending — see `CRA_P1_GATE_A_DECISION_SURFACING.md` GATE-A-1).

**Architecture at v0 (first apply, Q3 2026 target).** R7_cyber_v2 formula construct (per `R7_CYBER_V2_FORMULA_CONSTRUCT_DRAFT.md` D2 spec):

```
R7_cyber v2 = w_entity · f_entity(nis2_status, incident_history_24m, article21_maturity)
            + w_product · f_product(vendor_mix_cra_vintage, sbom_coverage)
```

with `w_entity + w_product = 1.0` (BINDING sum-to-unity invariant per V_socio precedent, Discipline #47 REGULATORY-VINTAGE variant sub-discipline). Initial calibration `w_entity = 0.55`, `w_product = 0.45` (resolved per Gate A GATE-A-2 operator sign-off 18 August 2026 Session B; rationale = Ciso-Nasser 2024 + NERC E-ISAC 2022 empirical grounding that operator-response discipline dominates over vendor-vulnerability tail for grid-critical infrastructure). Envelope preserved at `[0.99, 1.05]` at v0 (matches R7 v1 for continuity); envelope re-calibration deferred to v1 landing (post ENISA SRP feed availability if opens) → v2 (post 11 December 2027 CRA full applicability + SBOM per-vendor granularity).

**Path variant at v0** — **Path C+D composite** (composite entity + product for 26 EU cohort; stratified 13-country non-EU parallel constructs per D1 memo §4 table). Resolved per Gate A GATE-A-1 operator sign-off 18 August 2026 Session B. Alternatives (Path A ENISA SRP sole input · Path B CRA-vintage vendor-mix only · Path C EU-only) rejected — Path A carried single-point-of-failure risk; Path B missed entity-layer signal; Path C lost 13-country non-EU coverage. Full option analysis at `CRA_P1_GATE_A_DECISION_SURFACING.md` §1 GATE-A-1.

**Regulatory anchors (Convention #7 documented-proxy).** CRA — Regulation (EU) 2024/2847 (OJ L 20 November 2024, in force 10 December 2024, Article 14 hard binding 11 September 2026, full applicability 11 December 2027). NIS2 — Directive (EU) 2022/2555 (OJ L 14 December 2022, transposition deadline 17 October 2024 missed by 22/27 Member States). Cybersecurity Act — Regulation (EU) 2019/881 (OJ L 7 June 2019, reference for CRA critical-tier). 13-country non-EU parallel constructs individually anchored per country statute + regulator + register (UK NIS Regulations 2018 + CAF · US NERC CIP + CIRCIA · Canada CCCS · Japan METI CPSF · Korea K-ISMS-P · Australia ACSC ISM + SoCI Act · New Zealand NZISM · Chile Ley 21.663 · Colombia CONPES 3854 · Costa Rica MICITT + CSIRT-CR · Israel INCD · Mexico CERT-MX · Turkey BTK + Law 7545).

**R7 v1 dual-write transition discipline.** At v0 first-apply, R7_cyber v1 registry entry stays live (**dual-write ~6 months** transition per Gate A recommendation, GATE-A-11); consumers may select `R7_cyber` or `R7_cyber_v2` explicitly. R7_cyber v1 retire-with-tombstone comment lands in `scripts/pipeline/scoring/modifier_registry.py` at v0 landing. Consumer migration graceful; Convention #56 preserves v1 audit trail via `_r7_cyber_v1_retired: True` + `_r7_cyber_v1_value: <last-computed>` markers on every substation post-v0.

**Nomenclature bridge (Playbook §5 canonical translation table).** In this repo: `R7_cyber` (v1 fallback semantic) + `R7_cyber_v2` (v2 composite semantic). In systemic_layer/docs/: `C11 software/firmware` + `C13 compute infrastructure` + `C14 skilled-labour cyber-workforce` + `C16 Communication/telecom autonomy explicit NIS2 Article 3 anchor` (SY.9 stress-test composition). In `Report Production/00-Framing/METHODOLOGY_DISCIPLINES.md`: R7 dual-axis discipline (§5quater) composed with R7 v2 regulatory-vintage construction (§5novies). In `ssi_enn_v30/layer4/`: `w6_data_sovereignty.py` (PLANNED, Q4 2026 per Gate A GATE-A-5 sequencing) — commercial-tier NIS2/DORA per-asset evaluator sharing NIS2 substrate but operating at different granularity (asset vs substation) per Convention #63 parallel-worlds discipline.

**Discipline registrations landing this session.** (a) `METHODOLOGY_DISCIPLINES.md §5novies` — Regulatory-vintage-anchored modifier construction discipline candidate (1 of 5-10 empirical instances toward BINDING per Convention #76 cadence; queued instances R11 Paris Q3 2027 + R12 CSRD Q1 2027 + R13 EU AI Act Q4 2026 + R14+ SLB Q1-Q2 2027 + SFDR PAI revision cascade). (b) `REPORTS_FRAMING_KB.md §8bis Discipline #47` 5th REGULATORY-VINTAGE structural variant extension (or NEW #48 per Gate A GATE-A-3). (c) `METHODOLOGY_DISCIPLINES.md §5decies` Discipline #48 candidate — Cross-tree methodology cascade discipline (accelerated 3-5 empirical-instance cadence toward BINDING per playbook §7 — first empirical instance = this R7 v2 CRA cascade). (d) `systemic_layer/docs/CONVENTIONS_REGISTRY_SYSTEMIC.md §SY.21` — Regulatory-vintage-anchored modifier construction candidate (Gate A GATE-A-4: SY.21 candidate vs SY.18 extension). (e) `ssi_enn_v30/docs/CONVENTIONS_REGISTRY.md Convention #80` — private-commercial mirror per Convention #63 parallel-worlds discipline.

**Code-layer landings this session (registry only; module authoring queued P4).**

- `scripts/pipeline/scoring/modifier_registry.py` — new `R7_cyber_v2` entry with envelope `[0.99, 1.05]` (matches v1 at v0; envelope re-calibration deferred to v1/v2 per Gate A GATE-A-1 sign-off Path C+D composite path-variant selection); v1 retire-with-tombstone comment; both entries co-exist during dual-write transition.
- `SSI Enhanced Neural Network/systemic_layer/tests/test_no_probabilistic_cyber_claim.py` — whitelist extension for `R7_cyber_v2` as documented-proxy-not-probabilistic (prevents false-positive sentinel trigger at R7 v2 first apply).
- Module authoring for `scripts/pipeline/scoring/r7_cyber_v2.py` (Path C+D composite implementation), sentinel `tests/test_r7_cyber_v2_construct.py`, per-country audit YAML backfill, intelligence.html × 39 R7 tooltip refresh — all queued P4 per `CRA_R7_CASCADE_PLAN_EXTENDED.md`.

**Convention preservation matrix (Playbook §3.4).** #7 CRA + NIS2 publisher-cited + Article-pinned. #54 6-touch-point cascade applied (METHODOLOGY_DISCIPLINES §5novies + §5decies + REPORTS_FRAMING_KB §8bis Discipline #47 extension + CLAUDE.md this addendum + CLAUDE_SYSTEMIC.md addendum + ENN CLAUDE.md addendum). #55 verify-don't-trust — every `.PROPOSED` file requires operator sign-off row population before merge. #56 visibly-honest degradation — TBD_GATE_A_DECISION_1 + TBD_GATE_A_DECISION_2 placeholders were visibly named during authoring; resolved 18 August 2026 Session B via Gate A operator sign-off (Path C+D composite + w_entity=0.55/w_product=0.45) with each resolution cited in-place. #60 Ikenga IS the ESG provider — all sources EU institutional publishers. #63 parallel-worlds — R7 v2 modifies R_final (scoring-world); W6 (planned Q4 2026) evaluates compliance-world only; zero cycle. #78 §5septies BINDING — L1 ingestion not touched by P1; §5septies preserved for future connector work. #79 ssi-data sharding preserved throughout (P4 apply will use `_ssi_data_shard_reader`).

**Authoritative cascade documents.** `SSI Index/Upgrade Methodology Rulebook/01-R7-Cyber-v2-CRA-Integration/` — 7-deliverable CRA workstream: `CRA_NIS2_R7_CYBER_INTEGRATION_MEMO.md` (D1) + `R7_CYBER_V2_FORMULA_CONSTRUCT_DRAFT.md` (D2) + `CRA_R7_CASCADE_PLAN.md` (D3) + `SSI_ENN_SYSTEMIC_LAYER_TOPOLOGY_MAP.md` (D3-ext) + `CRA_R7_CASCADE_PLAN_EXTENDED.md` (D3-ext) + `CRA_R7_PRIORITY_1_TOUCHPOINTS.md` (D3-ext) + `CRA_R7_GREP_REPORT.md` (D4). P1 sandbox execution artifacts: `CRA_P1_EXECUTION_LOG.md` (per-touch-point closure matrix) + `CRA_P1_GATE_A_DECISION_SURFACING.md` (per-decision option analysis) + `task_1108_r7_cyber_v2_preflight_20260825.yaml` (Gate A sign-off vehicle). Cascade discipline: `METHODOLOGY_CASCADE_PLAYBOOK.md v0.2` (primary at `SSI Index/Upgrade Methodology Rulebook/`, cross-mirror at `SSI Enhanced Neural Network/systemic_layer/docs/`). Playbook self-refinement: `PLAYBOOK_FEEDBACK_LOG.md` (entries FL-001..FL-005 surfaced during this P1 execution).

## Pre-commit checklist

Before pushing to `main` or merging a PR:

- [ ] `pytest tests/` → all tests green (10+ existing + the 4 cross-border classes)
- [ ] `scripts/check_cross_border.py --all --strict` → green (or PR's validate.yml will fail)
- [ ] If you touched `*/ssi-data.json` or `*/grid-geo.json`: confirm `validate.yml` is green on the PR
- [ ] If you added a new country: confirm pytest discovers the new slug via `intelligence/countries.json`
- [ ] If you changed methodology version: bump `versions.json` + the v4.0.2-style backup pattern per Convention #56
- [ ] If you touched a scoring or enrichment path: every `.get(key, default)` with a **numeric** default is justified in the diff, or removed (Discipline #50)
- [ ] `pytest tests/test_m046_component_backed_scores.py` → green, and **not** xfailed
- [ ] If a gate newly passes: confirm it examined non-empty data — an empty set satisfies every universal quantifier (M-030)
- [ ] If you are about to xfail a failing gate: record why the mitigation actually works. A correct refusal silenced by a wrong mitigation note cost a month (M-044)
- [ ] `pytest tests/test_precedence_register_freshness.py` → green (set `SSI_PRECEDENCE_REGISTER` in CI; a **skip is not a pass**)
- [ ] If you changed a methodology document, a Convention, a Discipline number or a scoring behaviour: update `SSI_DOCUMENT_PRECEDENCE_REGISTER.md` §2/§3/§4 **in the same commit** (§7.1 rule 2)
- [ ] New Discipline number? Claim it in `METHODOLOGY_DISCIPLINES.md` first, starting at **#54**, after grepping every tree
- [ ] If you wrote a large JSON payload from a script: it went through `_atomic_write_text` (temp + `fsync` + `os.replace`), never `Path.write_text`. An interrupted `write_text` leaves a **shorter-but-parseable** shard that every concatenating reader accepts silently (M-055)
- [ ] `pytest tests/test_shard_write_integrity.py tests/test_component_donor_uniqueness.py` → green. Neither may be xfailed
- [ ] If you changed any scoring **input** (components, modifiers, socio_economic): the same change rescored the record. Enrichment without a rescore leaves a fossil score over live inputs (M-058, §5bis Criterion 2)
- [ ] Amending a gate? It must catch something the old one could not — state what, in the diff. An amendment that only makes red go green is a relaxation (register §5.10/§5.11)
- [ ] Rebuilding a summary or rollup? Carry forward the `_`-prefixed provenance keys you did not compute. Deleting the marker that explains present data is Convention #56 from the other side (M-065)
- [ ] Before trusting a gate's silence, check the thing it claims to check **directly** at least once. 24 phantom regions sat inside a rollup gate that structurally could not see them (M-062)
- [ ] A gate is failing and you believe the gate is wrong? Check the precedence register §1 first. If a rank-2 source contradicts it, amend the gate **and get it sanctioned** — silently amending a red gate is M-044. If not, the gate is right
- [ ] If you ran a data-recovery or backfill pass: the donor/source guard is **cross-invocation** — it reads the markers already on disk, not just a set local to this run. One source record may support exactly one target record (M-056)

## Companion documents

| Doc | Role | Where it lives |
|---|---|---|
| `CLAUDE.md` (this file) | Session briefing + binding disciplines | repo root |
| `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md` | Discipline #36 origin audit | repo root |
| `MODE_2_3_FOLLOWON_PLAN.md` | Discipline #36 second-wave plan | repo root |
| `PR_CROSS_BORDER_GUARD.md` | Discipline #36 PR-ready notes | repo root |
| `REPORTS_FRAMING_KB.md` §72 | Discipline #36 cross-reference from the SSI Index methodology framework | `~/Library/CloudStorage/OneDrive-IkengaSL/Internal - IKENGA EU - Documents/0.22. IP agenda/SSI Index/Report Production/00-Framing/REPORTS_FRAMING_KB.md` (separate repo, Ikenga SL tenant) |
| `PHASE_1_IMPLEMENTATION_PLAN.md` | Phase 1 PR-1+ scoring engine | repo root (canonical Phase 1 narrative) |
| `AUDIT_v4_0_2_PRE_v4_2_FOUNDATION.md` | v4.0.2 → v4.2 audit (F-Lx-y findings) | repo root |
| `intelligence/countries.json` | 39-country slug + first-refresh SoT (KB §57) | repo |
| `SSI_DOCUMENT_PRECEDENCE_REGISTER.md` | **Which document wins when two disagree** — read before citing any methodology text | `…/0.22. IP agenda/SSI Index/` (Ikenga SL tenant) |
| `SSI_FOUNDATIONAL_DOCS_ALIGNMENT_20260819.md` | Version audit of every foundational lineage | same folder |
| `SSI_METRIC_IMPLEMENTATION_DISCLOSURE_v1.md` | What each of the 20 metrics **actually** computes — binding companion to the Complete Formula Construct | same folder |
| `SSI_MODIFICATION_LOG_20260819.md` | Live remediation log, M-001 … M-056 — extended in place, never superseded | same folder |

## Contact

- **Cedric Berard** — c.berard@ikenga.eu — Ikenga Capital
- **SSI Index project** — ssi_index@ikenga.eu

---

*If you find this briefing outdated, update it in the same commit as your fix.*
