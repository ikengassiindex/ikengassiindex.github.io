// Costa Rica SSI v4.0.2 metadata — KB §73 · greenfield thin-shell on post-IS-upstream-cleanup architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Costa Rica S33B inaugural; re-onboarding after CR S33A rollback) · first refresh 2026-08-13
// Architecture acceptance test for KB §68.10 (CountryRenderer.Safe) + §68.11 (normalizeMeta()):
//   COMPONENTS_INDEX intentionally ships the documentation-rich Slovakia shape {code, name, ceiling, drivers}
//   MODIFIER_DEFS    intentionally ships the documentation-rich Slovakia shape {id, domain, range, description}
// normalizeMeta() in country-renderer.js is expected to alias these to the canonical {key, label, w, color}
// and {key, label, domain, range, description} forms with no per-country defensive patches required.

window.SSI_COUNTRY = 'costa-rica';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Costa Rica',
  COUNTRY: 'Costa Rica',
  country_code: 'CR',
  country_iso3: 'CRI',
  flag: '\u{1F1E8}\u{1F1F7}',  // 🇨🇷
  FLAG: '\u{1F1E8}\u{1F1F7}',
  cohort: 'Single-country (post-IS-upstream-cleanup, S33B re-onboarding)',
  edition: 'Edition 01',
  first_refresh: '2026-08-13',
  engine_version: '4.0.2',
  kb_version: 'v32',
  bpg_version: 'v1.31',
  currency: 'CRC',
  currency_symbol: '₡',
  currency_position: 'before',
  labels: {
    country_en: 'Costa Rica',
    country_local: 'Costa Rica',
    capital: 'San José',
    capital_local: 'San José',
    region_unit: 'provincia',
    region_unit_local: 'provincia',
    tso: 'ICE — Instituto Costarricense de Electricidad (autonomous state-owned vertically integrated TSO + dominant DSO + dominant generator; founded 8 Apr 1949)',
    regulator: 'ARESEP — Autoridad Reguladora de los Servicios Públicos (Ley 7593 / 9 Aug 1996)',
    statistics_office: 'INEC — Instituto Nacional de Estadística y Censos',
    nem: 'MER — Mercado Eléctrico Regional via SIEPAC (NOT in ENTSO-E SDAC/SIDC; coordinated by EOR + CRIE)',
    bidding_zone: 'MER-CR (Central American Regional Electricity Market — no EIC code)'
  },
  stats: { sources: 12, variables: 95, components: 6, modifiers: 8 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_seismic', 'R6_volcanic', 'R6_hurricane', 'R6_hydro_deficit', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '4-tier (Industrial-High-Tech 1.05 / Capital-Metro 1.04 / Commercial-Geothermal 1.03 / Light-Rural-Coastal 1.02)',
    r6_anchors: '5 Sep 2012 Nicoya Mw 7.6 subduction megathrust (defining instrumental event) · 8 Jan 2009 Cinchona Mw 6.1 (destroyed Cariblanco 100 MW hydro = 10% of national capacity) · 22 Apr 1991 Limón Mw 7.7 · Active volcanic edifices Arenal/Poás/Turrialba/Rincón de la Vieja/Irazú monitored by OVSICORI-UNA + RSN · Nov 2016 Hurricane Otto Cat 2 (first direct hurricane landfall since 1851, Guanacaste) · Oct 2017 Tropical Storm Nate ($540M, ~1% GDP — costliest CR natural disaster) · 2023-2024 El Niño cycle worst in 50 years per ICE (hydro share dropped from ~74% to ~67%, thermal share spiked to 25% Apr-May 2024, SIEPAC imports increased)',
    r7_ceiling: 1.025
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — INTENTIONALLY Slovakia-style {code, name, ceiling, drivers}
// (KB §68.10 acceptance test — normalizeMeta() must alias this to {key, label, w, color})
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · ARESEP quality reports · ICE Plan de Expansión + CENCE monthly bulletins · San José GAM urban ~25-40 min vs Limón Caribbean rural ~120-150 min split (single-DSO-dominant panel: ICE direct + CNFL subsidiary + ESPH/JASEC municipals + 4 cooperatives)' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160-equivalent events · ARESEP RJD-139-2015 tariff + quality framework · ICE Sabana Norte switchyard telemetry · Heredia Intel fab + Boston Scientific medical-device load THD profile + Miravalles 163.5 MW geothermal H₂S corrosion' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · ICE asset register · 230/138/34.5 kV inventory (SIEPAC 230 kV regional backbone + ICE 138 kV sub-transmission + CNFL/JASEC/ESPH urban 34.5 kV) + Reventazón 305.5 MW switchyard + Arenal-Corobicí cascade + Miravalles geothermal complex' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'INEC provincia GDP + BCCR national accounts · Heredia + Alajuela free-trade-zone medical-device + electronics exports ~$8-10 B/yr (3rd-largest medical-device exporter in Americas after US + MX) · CRC industrial tariffs vs USD/EUR comparators · Coyol FTZ + Boston Scientific Global Park concentration' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'INEC household + energy-poverty (~3-5%) · Talamanca + Térraba indigenous reservations (Bribri + Cabécar + Boruca, ~2.4% national, language-of-supply consideration) · Limón Caribbean coast lowest GDP/capita + border zones (NI north + PA south) high immigration + Limón Creole English' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'ICE Plan de Expansión + CENCE generation registry · ~99% renewable in normal hydrology (hydro 74% + geothermal 13% + wind 12.5% + solar 0.5% + biomass 0.1%, 2023) but volatile (89% in 2024 El Niño drought; thermal share peaked 25% Apr-May 2024). National Decarbonization Plan 2018-2050 — net-zero by 2050, 100% renewable electricity 2030 (drought-adjusted)' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_ice',          name: 'ICE — Instituto Costarricense de Electricidad (vertically integrated TSO + dominant DSO + dominant generator)', freq: 'Daily',      status: 'live', vars: 16, feeds: 'C2,C3,I1,I2,I3,R4,T1', sources: 'grupoice.com Plan de Expansión 2021-2031 + CENCE monthly generation bulletins + 230/138/34.5 kV transmission asset register + Reventazón/Arenal/Pirrís/Cachí dispatch' },
  { id: 'd02_aresep',       name: 'ARESEP — Autoridad Reguladora de los Servicios Públicos (Ley 7593 / 1996)',                  freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1,E1', sources: 'aresep.go.cr RJD-139-2015 tariff methodology + electricity quality-of-service indicators + DSO regulatory filings' },
  { id: 'd02b_dso',         name: '8 DSOs (ICE direct + CNFL subsidiary + ESPH + JASEC + 4 cooperatives Coopelesca/Coopeguanacaste/Coopealfaro Ruiz/Coopesantos)', freq: 'Quarterly', status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'CNFL (Greater San José metro, ICE subsidiary, ~41%) + ICE direct (national rural + Caribbean, ~38%) + ESPH (Heredia municipal, ~6%) + JASEC (Cartago municipal, ~6%) + 4 cooperatives (~9% aggregate) quarterly filings' },
  { id: 'd03_ovsicori',     name: 'OVSICORI-UNA + RSN (UCR-ICE) — volcanic + seismic monitoring',                              freq: 'Continuous', status: 'live', vars: 12, feeds: 'I1,I2,I3,R6_seismic,R6_volcanic', sources: 'ovsicori.una.ac.cr (Universidad Nacional volcanic observatory — 5 active edifices Arenal/Poás/Turrialba/Rincón de la Vieja/Irazú) + rsn.ucr.ac.cr (Red Sismológica Nacional, UCR + ICE co-operated; Middle America Trench Cocos megathrust monitoring; Nicoya 2012 + Cinchona 2009 anchors)' },
  { id: 'd04_inec',         name: 'INEC — Instituto Nacional de Estadística y Censos',                                          freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'inec.cr — 2011 census + 2023-2025 projections + 7 provincia regional accounts + 84 cantón LAU + indigenous-reservation demographics (Talamanca Bribri/Cabécar)' },
  { id: 'd04b_bccr',        name: 'BCCR — Banco Central de Costa Rica (CRC monetary authority)',                                freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'E1,E2', sources: 'bccr.fi.cr national accounts + CRC FX reference + financial stability + provincia GDP/capita' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=CR area filter)',                                   freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line/minor_line · ISO3166 CR · including 230 kV SIEPAC + ICE 138 kV backbone + Reventazón/Arenal-cascade/Miravalles/Las Pailas switchyards' },
  { id: 'd06_imn',          name: 'IMN — Instituto Meteorológico Nacional (under MINAE) + CNE Comisión Nacional de Emergencias', freq: 'Daily',     status: 'live', vars: 6,  feeds: 'I2,I3,R6_climate,R6_hurricane,R6_hydro_deficit', sources: 'imn.ac.cr meteorology + ITCZ + hurricane tracks in coordination with US NHC (Otto 2016 + Nate 2017 + Eta/Iota 2020 + Julia 2022 anchors) + CNE 2024 drought emergency · ECMWF mirror · IMN+ICE hydrology for Lake Arenal + Reventazón reservoirs' },
  { id: 'd07_copernicus',   name: 'Copernicus ERA5 + CMIP6',                                                                    freq: 'Monthly',    status: 'live', vars: 4,  feeds: 'R6_climate', sources: 'cds.climate.copernicus.eu SSP2-4.5 · 8-11°N tropical reanalysis + ENSO indices' },
  { id: 'd08_eor_epr',      name: 'EOR + EPR — Ente Operador Regional + Empresa Propietaria de la Red (SIEPAC operations)',     freq: 'Daily',      status: 'live', vars: 6,  feeds: 'I1,I2,S2', sources: 'enteoperador.org regional dispatch + eprsiepac.com 230 kV line operator · SIEPAC 1,793 km regional backbone (CR portion ~493-520 km) + CR-NI Cañas/Liberia↔Amayo + CR-PA Río Claro↔Veladero interconnects operational since Oct 2014 · CRIE regulatory oversight' },
  { id: 'd09_csirt_cr',     name: 'CSIRT-CR — Centro de Respuesta de Incidentes de Seguridad Informática (MICITT Dirección de Gobernanza Digital)', freq: 'Annual', status: 'live', vars: 5, feeds: 'R7_cyber', sources: 'micitt.go.cr CSIRT-CR RFC-2350 (created Mar 2012, formally opened 2015) · National Cybersecurity Strategy 2023 (post-2022 reform) · Directive 133-MP-MICITT · CSIRT Americas network member' },
  { id: 'd10_iea_oecd',     name: 'IEA + OECD — energy benchmarks (Costa Rica 38th OECD member, accession 25 May 2021)',         freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics · CR is 4th Latin American OECD member after MX (1994) + CL (2010) + CO (2020); industrial tariff ~$0.10-0.14/kWh' },
  { id: 'd11_minae_sepse',  name: 'MINAE + SEPSE — Ministerio de Ambiente y Energía + Secretaría de Planificación del Subsector de Energía', freq: 'Annual', status: 'live', vars: 8, feeds: 'T1,R6_hydro_deficit', sources: 'minae.go.cr policy + concessions + SEPSE National Energy Plans + National Decarbonization Plan 2018-2050 tracking · FONAFIFO PSA (Pago por Servicios Ambientales) forest-carbon program 1997-present ($524M cumulative, 1.3M ha)' }
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 2,  sources: ['OSM Overpass (ISO3166-1=CR)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 3,  sources: ['DSO filings (CNFL + ICE direct + ESPH + JASEC + 4 cooperatives)', 'INEC', 'BCCR'] },
  Annual:    { count: 5,  sources: ['ARESEP tariff methodology', 'CSIRT-CR + MICITT', 'IEA/OECD', 'MINAE/SEPSE National Energy Plans', 'IMN hurricane post-event reports'] },
  Continuous:{ count: 1,  sources: ['OVSICORI-UNA + RSN volcanic/seismic monitoring'] },
  Daily:     { count: 3,  sources: ['ICE generation + transmission dispatch', 'IMN meteorology + CNE emergency response', 'EOR + EPR SIEPAC regional dispatch'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'ICE transmission (230 / 138 / 34.5 kV) — vertically integrated state-owned',           vars: 16, status: 'live', sources: 'ICE Plan de Expansión 2021-2031 + CENCE dispatch (NOT in ENTSO-E; CR is MER member via SIEPAC)' },
  { id: 'dso',        name: '8 DSOs (ICE direct + CNFL + ESPH + JASEC + 4 cooperatives)',                          vars: 18, status: 'live', sources: 'CNFL (Greater San José, ICE subsidiary) + ICE direct (national rural + Caribbean) + ESPH (Heredia municipal) + JASEC (Cartago municipal) + Coopelesca/Coopeguanacaste/Coopealfaro Ruiz/Coopesantos cooperatives' },
  { id: 'regulator',  name: 'ARESEP — tariff regulation + quality-of-service',                                      vars: 12, status: 'live', sources: 'ARESEP Ley 7593 + RJD-139-2015 + electricity quality indicators + MINAE policy + SEPSE planning' },
  { id: 'statistics', name: 'INEC — provincia + cantón socio-economic',                                              vars: 16, status: 'live', sources: 'INEC regional accounts (7 provincias + 84 cantones LAU) + BCCR macro + indigenous-reservation demographics' },
  { id: 'hazard',     name: 'Multi-hazard (seismic + volcanic + hurricane + flood + hydro-deficit)',                vars: 18, status: 'live', sources: 'OVSICORI-UNA + RSN (UCR-ICE) consolidated · Middle America Trench megathrust + 5 active volcanic edifices + Caribbean hurricane (Otto 2016 + Nate 2017) + El Niño hydro-deficit anchors' },
  { id: 'cyber',      name: 'CSIRT-CR + MICITT',                                                                    vars: 8,  status: 'live', sources: 'CSIRT-CR (formed 2012, opened 2015; MICITT Dirección de Gobernanza Digital) + National Cybersecurity Strategy 2023 + 2022 ransomware-emergency anchor' },
  { id: 'topology',   name: 'OSM grid topology (ISO3166-1=CR; SIEPAC-interconnected north + south)',                 vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 CR area filter (SIEPAC 230 kV regional backbone + CR-NI north + CR-PA south interconnects)' },
  { id: 'generation', name: 'ICE generation operators (hydro 74% + geothermal 13% + wind 12.5% + solar 0.5%)',       vars: 6,  status: 'live', sources: 'ICE direct ~75-80% (Reventazón 305.5 MW + Arenal-Corobicí + Cachí + Pirrís + Angostura + Toro cascade + Miravalles 163.5 MW + Las Pailas 97.5 MW) + private IPPs + cooperative micro-generation' }
];

// REGIONS — Costa Rica's 7 provincias
// No NUTS-equivalent scheme; ISO 3166-2:CR codes (CR-SJ/A/C/H/G/P/L) are the natural granularity for
// R3 + R6_volcanic + R6_seismic + R6_hurricane + R6_hydro_deficit zoning.
window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'SJ', name: 'San José',  capital: 'San José',        tier: 'Capital-Metro',           r3: 1.04 },
  { code: 'A',  name: 'Alajuela',  capital: 'Alajuela',        tier: 'Capital-Metro',           r3: 1.04 },
  { code: 'C',  name: 'Cartago',   capital: 'Cartago',         tier: 'Commercial-Geothermal',   r3: 1.03 },
  { code: 'H',  name: 'Heredia',   capital: 'Heredia',         tier: 'Industrial-High-Tech',    r3: 1.05 },
  { code: 'G',  name: 'Guanacaste',capital: 'Liberia',         tier: 'Commercial-Geothermal',   r3: 1.03 },
  { code: 'P',  name: 'Puntarenas',capital: 'Puntarenas',      tier: 'Light-Rural-Coastal',     r3: 1.02 },
  { code: 'L',  name: 'Limón',     capital: 'Puerto Limón',    tier: 'Light-Rural-Coastal',     r3: 1.02 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'CNFL — Compañía Nacional de Fuerza y Luz', region: 'Greater San José Metropolitan Area (GAM Central)', share_pct: 41, parent: 'ICE subsidiary (wholly state-owned via ICE)' },
  { name: 'ICE direct',                                region: 'National rural + Caribbean coast + extra-metropolitan + parts of Pacific', share_pct: 38, parent: 'Instituto Costarricense de Electricidad (autonomous state-owned)' },
  { name: 'ESPH — Empresa de Servicios Públicos de Heredia', region: 'Heredia provincia', share_pct: 6, parent: 'Municipal (state-owned via Heredia municipalities)' },
  { name: 'JASEC — Junta Administrativa del Servicio Eléctrico de Cartago', region: 'Cartago provincia', share_pct: 6, parent: 'Municipal (state-owned via Cartago municipality)' },
  { name: 'Coopelesca + Coopeguanacaste + Coopealfaro Ruiz + Coopesantos', region: 'Rural northern zone + Guanacaste rural + Zarcero canton + Los Santos zone', share_pct: 9, parent: 'Rural electrification cooperatives (member-owned)' }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'ARESEP quality reports — per-DSO (CNFL urban ~25-40 min vs ICE direct rural Caribbean ~120-150 min)' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'ARESEP — per-DSO (single-DSO-dominant panel: ICE + CNFL + ESPH + JASEC + 4 cooperatives)' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + ICE asset register (230 / 138 / 34.5 kV — SIEPAC backbone)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'CNFL + ICE direct + ESPH + JASEC + 4 cooperatives quarterly filings + INEC' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'ARESEP + CNE (Comisión Nacional de Emergencias) civil protection coordination' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160-equivalent dip events',  intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'ARESEP + DSOs (CNFL + ICE direct + ESPH + JASEC + 4 cooperatives)' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'ARESEP + DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'ARESEP quarterly filings (Intel/Boston Scientific Heredia fab loads + Miravalles geothermal switchyard dominate THD profile)' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (tropical)',         intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + IMN — heat-wave loading is moderate at 8-11°N tropical zone with cooler highlands', adaptive: true },
      { id: 'I2', name: 'Hurricane + storm-surge',          intra: 0.14, global: 0.035, norm: 'P99 events',           source: 'IMN + CNE — Hurricane Otto Nov 2016 anchor (first direct landfall since 1851, Guanacaste) + Nate Oct 2017 ($540M = ~1% GDP)', adaptive: true },
      { id: 'I3', name: 'Tropical-storm rainfall IRI',      intra: 0.12, global: 0.030, norm: 'P99 mm/hr',            source: 'IMN wet-season May-Nov ITCZ rainfall + indirect cyclones; lahars from active volcanoes (Turrialba/Poás post-eruption mudflows)', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                 intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'ICE + DSOs annual reports (Reventazón 2016 + Miravalles 1994-2004 vs CNFL legacy urban distribution)' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',        intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus (Caribbean-slope 230 kV corridors run hot during El Niño thermal substitution)' },
      { id: 'I6', name: 'Substation density',               intra: 0.10, global: 0.025, norm: 'per km²',              source: 'OSM + INEC (~169-300 subs across 51,100 km²)' },
      { id: 'I7', name: 'Network length per cap',           intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'ICE Plan de Expansión + DSOs · ~2,500-2,700 km HV transmission expected 2025' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',    intra: 0.10, global: 0.025, norm: 'C2-C5 categorical',    source: 'ISO 9223 — C5 at Caribbean coast (Limón + Reventazón + Moín) + Pacific coast (Puntarenas + Quepos + Guanacaste tourist coast) + Miravalles + Las Pailas geothermal H₂S; C4 Coyol de Alajuela + Cartago industrial; C3 urban GAM; C2 interior highlands' },
      { id: 'I9', name: 'Hydrogeological exposure',         intra: 0.04, global: 0.010, norm: 'Q100 + lahar overlay', source: 'IMN + ICE hydrology — Lake Arenal + Reventazón reservoir + Pirrís + Pacific-slope wet-season Q100 + post-eruption lahar corridors' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',      intra: 0.60, global: 0.060, norm: 'EUR-eq per SAIDI min', source: 'ARESEP tariff decisions (CRC native, EUR-eq for cross-country at ~540 CRC/EUR May 2026)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',         intra: 0.40, global: 0.040, norm: 'EUR-eq/kWh',            source: 'ACER 2023 equivalent + INEC sector mix (medical devices + electronics ~$8-10 B/yr exports · tourism ~7-8% GDP · agriculture banana/pineapple/coffee · free-trade-zone industrial concentration)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',        intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'ICE + DSOs (Reventazón→Caribbean 230 kV corridor + Heredia fab-feeding 138 kV under fab-expansion pressure)' },
      { id: 'S2', name: 'Reverse power flow + SIEPAC import', intra: 0.35, global: 0.070, norm: 'hours/yr reverse',  source: 'ICE/CENCE + EOR (SIEPAC cross-border flow; 2024 El Niño drove ~10% thermal/SIEPAC import substitution Apr-May)' },
      { id: 'S3', name: 'Criticality class',                intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'ICE Plan de Expansión 2021-2031 SIEPAC second-circuit financing (BCIE) 2025-2027 lifts transfer capacity' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER + Decarbonization Stress',     intra: 1.00, global: 0.050, norm: 'composite',            source: 'ICE Plan de Expansión + CENCE generation registry · T_share at boundary ~98-99% normal hydrology but volatile (89% in 2024 El Niño drought — 8-10 pp dynamic range from hydro deficit) · National Decarbonization Plan 2018-2050 net-zero target · 100% renewable electricity 2030 drought-adjusted · Sep 2024 IPP commitments add 166 MW solar+wind under construction', isNew: true }
    ]}
];

// MODIFIER_DEFS — INTENTIONALLY Slovakia-style {id, domain, range, description}
// (KB §68.11 acceptance test — normalizeModifierDef() must map {R3→R3_C_mult, R6a→R6_restoration, R6b→R6_seismic, R7→R7_cyber})
// Costa Rica-specific: R6_volcanic carried forward from prior cohort; R6_hurricane + R6_hydro_deficit are NEW sub-patterns (first in cohort).
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2',  domain: 'Adaptive IRI + Climate',     range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is moderate. CMIP6 SSP2-4.5 projections adjust forward-looking risk; at 8-11°N tropical zone Costa Rica\'s dominant adaptive vectors are wet-season ITCZ rainfall + Caribbean hurricane exposure + 2023-2024 El Niño hydro-deficit.' },
  { id: 'R3',  domain: 'Consequence + Poverty',      range: '[0.70, 1.30]', description: 'Amplifies risk for provincias serving large/energy-poor populations with high economic dependency. Costa Rica uses a 4-tier calibration (Industrial-High-Tech 1.05 / Capital-Metro 1.04 / Commercial-Geothermal 1.03 / Light-Rural-Coastal 1.02). Industrial-High-Tech tier reflects the Heredia tech corridor (Intel + Boston Scientific Global Park, medical-device exports ~$8-10 B/yr); Capital-Metro reflects San José (~1.6M) + Alajuela (Juan Santamaría SJO airport + Coyol Free Trade Zone); Commercial-Geothermal covers Cartago + Guanacaste (Miravalles 163.5 MW + Las Pailas 97.5 MW); Light-Rural-Coastal covers Puntarenas + Limón (Caribbean banana/pineapple + Pacific tourism).' },
  { id: 'R4',  domain: 'Graph Criticality',          range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph. Costa Rica is SIEPAC-interconnected via 230 kV regional backbone (CR-NI north + CR-PA south, operational since Oct 2014) — re-activates the cross_border_lines array population path that was empty for IS (insular) and KR (synchronous-only). SIEPAC second-circuit BCIE-financed under construction 2025-2027.' },
  { id: 'R6a', domain: 'Restoration Speed',          range: '[0.90, 1.10]', description: 'ARESEP-CAIDI-based: rewards fast-restoring metropolitan areas (San José GAM under CNFL), penalises slow ones. Limón Caribbean + Talamanca indigenous reservations carry a remote-rural access penalty (long radial 34.5 kV feeds + Talamanca Bribri/Cabécar communities + flood-season access constraints).' },
  { id: 'R6_seismic', domain: 'Network Topology + Seismic', range: '[1.00, 1.25]', description: 'Network centrality + Pacific Ring of Fire seismic hazard. Costa Rica straddles the Cocos-Caribbean plate boundary with three active source zones — Middle America Trench (offshore Pacific subduction, defining megathrust, anchor: Nicoya 5 Sep 2012 Mw 7.6), Panama Fracture Zone (southwest strike-slip), and Costa Rica Deformed Belt (intra-arc, anchor: Cinchona 8 Jan 2009 Mw 6.1 — destroyed Cariblanco 100 MW hydro = ~10% of national capacity). R6_seismic α band [0.15, 0.30] — cohort-leading outside Japan. RSN (UCR-ICE) + CNE publish 475-yr PGA hazard maps; central CR ~0.30-0.45g, coastal Pacific Nicoya ~0.35-0.50g, Caribbean Limón ~0.25-0.40g.' },
  { id: 'R6_volcanic', domain: 'Volcanic Activity (carry-forward sub-pattern)', range: '[1.00, 1.20]', description: 'Carry-forward from prior cohort, adapted to composite stratovolcano hazard model (PDC + lahar + ashfall + edifice instability). Active + dormant volcanic edifices monitored by OVSICORI-UNA: Arenal (Alajuela, dormant since Oct 2010 post-1968-2010 eruption cycle), Poás (Alajuela, 2017 phreatomagmatic eruptions + 2009 Cinchona landslide source area), Turrialba (Cartago, most active currently — 2014-2019 ash on San José), Rincón de la Vieja (Guanacaste, frequent phreatic; ~5 km from Las Pailas geothermal), Irazú (Cartago, 1963-1965 major ash to San José for ~2 years), Tenorio/Miravalles/Barva dormant. R6_volcanic α band [0.05, 0.18]: Alajuela 0.13-0.18 + Cartago 0.12-0.16 + Guanacaste 0.10-0.15 + Heredia 0.06-0.10 + San José 0.05-0.10 + Limón/Puntarenas 0.02-0.05. Defining grid-impact anchor: Cinchona 2009 + Poás 2017 paired.' },
  { id: 'R6_hurricane', domain: 'Caribbean Tropical Cyclone (NEW sub-pattern)', range: '[1.00, 1.10]', description: 'FIRST IN COHORT with active Caribbean hurricane exposure (distinct from Pacific typhoon). Anchors: Hurricane Otto Nov 2016 (first direct hurricane landfall in CR since records began 1851; Cat 1-2 in NW CR Guanacaste; 9 fatalities; $185M damage), Tropical Storm Nate Oct 2017 ($540M = ~1% GDP — costliest CR natural disaster), Eta + Iota Nov 2020, Julia Oct 2022. R6_hurricane α band [0.03, 0.10]: Limón Caribbean coast 0.08-0.10 + Guanacaste Pacific NW (Otto landfall zone) 0.06-0.08 + Alajuela northern lowlands (San Carlos) 0.05-0.07 + Pacific central/south + Central Valley 0.03-0.05. Carries forward to next Caribbean/Pacific tropical-cyclone country (DO/JM/PR/PA/HN/NI).' },
  { id: 'R6_hydro_deficit', domain: 'El Niño / ENSO Hydro Deficit (NEW sub-pattern)', range: '[1.00, 1.12]', description: 'FIRST IN COHORT — hydropower deficit driving thermal + SIEPAC-import substitution. Mechanism: ENSO El Niño phase → reduced wet-season rainfall in CR Pacific watersheds → Lake Arenal + Reventazón reservoirs drop → hydro output curtailed → thermal generation activated + SIEPAC imports increased → tariff stress + emissions spike. Defining anchor: 2023-2024 El Niño cycle (ICE declared "worst drought in 50 years"; hydro share dropped from ~74% to ~67%, thermal share peaked 25% Apr-May 2024 vs ~1-2% baseline). R6_hydro_deficit α band [0.02, 0.10]: Guanacaste Pacific drought belt 0.10-0.16 + national baseline 0.05-0.10 + Atlantic-side Reventazón less affected. Carries forward to next hydro-dependent OECD (NO + NZ + CL + Quebec/BC).' },
  { id: 'R7',  domain: 'Digital Readiness',          range: '[0.99, 1.025]', description: 'Cyber posture anchored on the 2022 ransomware national emergency (Conti hit Ministerio de Hacienda 18 Apr 2022 with $10M demand; Hive hit CCSS public health 31 May 2022 with $5M; national emergency declared 8 May 2022 by President Chaves — first OECD peacetime cyber-emergency declaration). CSIRT-CR maturity (created Mar 2012, opened 2015; MICITT Dirección de Gobernanza Digital; CSIRT Americas network member). National Cybersecurity Strategy 2023 (post-2022 reform). Ceiling 1.025 — mid-cohort, reflecting BOTH the documented stress event AND the substantial post-2022 institutional hardening (the post-event learning is the relevant signal, not the event itself).' }
];

window.SSI_METADATA.NORM_METHODS = [
  { id: 'A', name: 'Robust fleet percentile (P5/P95)',
    formula: 'x_norm = clip((x - P5) / (P95 - P5), 0, 1)',
    applies: 'C1, C2, C4, C5, E1, E2, I7' },
  { id: 'B', name: 'Standard fleet percentile',
    formula: 'x_norm = (rank(x) - 1) / (n - 1)',
    applies: 'I4, S1, S2' },
  { id: 'C', name: 'Bounded rescaling (log)',
    formula: 'x_norm = log10(x / x_min) / log10(x_max / x_min)',
    applies: 'C3 (voltage class · 230/138/34.5 kV)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C5), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=CR area filter — SIEPAC-interconnected, CR-NI north + CR-PA south land neighbours (first non-zero cross-border in 3 consecutive onboardings)', status: 'verified', isNew: true },
  { check: 'Polygon containment (subs → 7 provincias)',              criterion: 'Every substation falls inside exactly one provincia polygon (INEC + GADM)',  status: 'verified', isNew: true },
  { check: 'R3 4-tier distribution',                                  criterion: '4-tier (Industrial-High-Tech / Capital-Metro / Commercial-Geothermal / Light-Rural-Coastal) across 7 provincias', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Seismic (Middle America Trench Nicoya 2012 + Cinchona 2009) + Volcanic (5 active edifices, carry-forward) + Hurricane NEW (Otto 2016 + Nate 2017) + Hydro-deficit NEW (2023-2024 El Niño)', status: 'verified', isNew: true },
  { check: 'R6_hurricane NEW sub-pattern',                            criterion: 'Limón Caribbean 0.08-0.10 + Guanacaste Pacific NW 0.06-0.08 + Alajuela northern 0.05-0.07 + Central Valley 0.03-0.05', status: 'verified', isNew: true },
  { check: 'R6_hydro_deficit NEW sub-pattern',                        criterion: 'Guanacaste Pacific drought belt 0.10-0.16 + national baseline 0.05-0.10; 2023-2024 El Niño anchor',         status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.025 (CSIRT-CR 2012 · 2022 emergency · 2023 NCS)', criterion: 'Mid-cohort; reflects 2022 emergency stress + post-2022 institutional hardening', status: 'verified', isNew: true },
  { check: 'SIEPAC cross-border interconnects',                       criterion: 'Non-zero cross_border_lines — CR-NI Cañas/Liberia↔Amayo + CR-PA Río Claro↔Veladero (operational since Oct 2014); SIEPAC second-circuit under construction 2025-2027 BCIE-financed', status: 'verified', isNew: true },
  { check: 'T_share dynamic-range handling',                          criterion: '~99% renewable normal hydrology (hydro 74% + geothermal 13% + wind 12.5% + solar 0.5% + biomass 0.1%, 2023); 89% in 2024 El Niño drought — 8-10 pp dynamic range documented in methodology', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[CR] floor enforced',                            criterion: 'Actual fleet ≥ 169 substations exceeds MIN_FLEET[CR]=150 — stub-gate clear',         status: 'verified', isNew: true },
  { check: 'C5 corrosion class restored',                             criterion: 'Dual-coast C5 (Caribbean Limón + Pacific Puntarenas/Guanacaste) + Miravalles + Las Pailas geothermal H₂S — strongest C5 exposure post-KR', status: 'verified', isNew: true },
  { check: 'edition_anchor_month_offset = 5',                         criterion: 'BPG Discipline #20 — cohort-synchronized Edition 02 = 2026-07-09; pre-flight check_edition_offset.py PASS', status: 'verified', isNew: true },
  { check: 'D#21 content-leakage (BPG XXXIX.21)',                     criterion: 'Post-IS-upstream-cleanup re-onboarding; 0 IS hits + 0 HU hits vs CR S33A rolled-back baseline (142 IS + 104 HU)', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'CR-S33B-1', change: 'Post-IS-upstream-cleanup re-onboarding from clean Iceland template (commits c2e41e06 + e4c78f91)', type: 'new', section: 'KB §73' },
  { id: 'CR-S33B-2', change: 'CR fact card §1-§17 web-verified anchors wired across all 8 pages (ICE + ARESEP + 7 provincias + R6 modifiers)', type: 'new', section: 'KB §73' },
  { id: 'CR-S33B-3', change: 'R3 4-tier calibration — Industrial-High-Tech 1.05 (Heredia Intel/Boston Scientific) / Capital-Metro 1.04 (San José + Alajuela) / Commercial-Geothermal 1.03 (Cartago + Guanacaste) / Light-Rural-Coastal 1.02 (Puntarenas + Limón)', type: 'new', section: 'methodology' },
  { id: 'CR-S33B-4', change: 'R6_hurricane + R6_hydro_deficit NEW sub-patterns — first Caribbean tropical-cyclone + first El-Niño-anchored hydro-deficit modifiers in cohort (Otto 2016 + Nate 2017 + 2023-2024 El Niño anchors)', type: 'new', section: 'methodology' },
  { id: 'CR-S33B-5', change: 'SIEPAC cross-border re-activation — CR-NI north + CR-PA south interconnects (first non-zero cross_border_lines in 3 onboardings)', type: 'enhanced', section: 'methodology' },
  { id: 'CR-S33B-6', change: 'd05_osm LIVE — ISO3166-1=CR area filter (SIEPAC + ICE backbone + Reventazón/Arenal/Miravalles/Las Pailas switchyards)', type: 'data', section: 'methodology' },
  { id: 'CR-S33B-7', change: 'ICE single-DSO + CNFL subsidiary + 2 municipals + 4 cooperatives + ARESEP regulator + OVSICORI-UNA/RSN + INEC/BCCR + IMN + EOR/EPR + CSIRT-CR/MICITT + MINAE/SEPSE wired', type: 'data', section: 'methodology' },
  { id: 'CR-S33B-8', change: 'edition_anchor_month_offset=5 — cohort-synchronized Edition 02 = 2026-07-09 (BPG Discipline #20 PASS)', type: 'enhanced', section: 'intelligence' },
  { id: 'CR-S33B-9', change: 'D#21 content-leakage gate PASS (0 IS + 0 HU hits; CR S33A baseline was 142 + 104)', type: 'enhanced', section: 'KB §73' },
  { id: 'CR-S33B-10', change: 'R7 ceiling 1.025 — 2022 ransomware national emergency anchor (Conti Hacienda + Hive CCSS) + post-2022 hardening (CSIRT-CR + NCS 2023)', type: 'new', section: 'methodology' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Costa Rica Seismic Hazard Map','RSN (UCR-ICE) + CNE PGA 475-yr · Middle America Trench Cocos megathrust','2023','Multi-year','Open','R1, R3'],
  ['Volcanic Monitoring','OVSICORI-UNA — Arenal/Poás/Turrialba/Rincón de la Vieja/Irazú networks','2024','Continuous','Open','R1, R3'],
  ['Population & Economics','INEC (Instituto Nacional de Estadística y Censos)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','ICE Plan de Expansión + ARESEP electricity quality indicators','2024','Daily','Regulated','R2, R4'],
  ['Renewable Generation Mix','ICE/CENCE (hydro 74% + geothermal 13% + wind 12.5% + solar 0.5%, 2023; 67/13/11/1 in 2024 El Niño)','2024','Monthly','Open','R4'],
  ['Weather + Climate','IMN (Instituto Meteorológico Nacional, under MINAE)','2024','Daily','CC-BY-4.0','R1'],
  ['Hurricane Track + Storm-Surge Mapping','IMN + US NHC HURDAT — Otto 2016 + Nate 2017 + Eta/Iota 2020 + Julia 2022 anchors','2024','Annual','CC-BY-4.0','R1'],
  ['Cybersecurity Posture','CSIRT-CR (MICITT Dirección de Gobernanza Digital, formed 2012, opened 2015) + National Cybersecurity Strategy 2023','2024','Annual','Open','R6'],
  ['Free-Trade-Zone Industrial Load','Intel + Boston Scientific Heredia/Coyol + CINDE industrial customer reporting','2024','Annual','Industry','R2, R3'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C5 — C5 dual-coast + Miravalles H₂S)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1'],
  ['SIEPAC Regional Dispatch','EOR + EPR (Ente Operador Regional + Empresa Propietaria de la Red) · 230 kV regional backbone since Oct 2014','2024','Daily','Regulated','R2, R4'],
  ['Decarbonization + PSA Forest Carbon','MINAE National Decarbonization Plan 2018-2050 + FONAFIFO PSA program 1997-present ($524M, 1.3M ha)','2024','Annual','Open','R4']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
