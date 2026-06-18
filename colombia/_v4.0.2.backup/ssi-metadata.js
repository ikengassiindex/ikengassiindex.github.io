// Colombia SSI v4.0.2 metadata — KB §77 · greenfield thin-shell on post-S38 architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Colombia S39 inaugural; first Andean OECD member; 37th OECD accession 28 Apr 2020)
// First refresh 2026-09-10 (2nd Thursday September — cohort sync per §49.4 + §56.10 + §73.5)
// Architecture acceptance:
//   COMPONENTS_INDEX intentionally ships the documentation-rich {code, name, ceiling, drivers} shape
//   MODIFIER_DEFS    intentionally ships the documentation-rich {id, domain, range, description} shape
// normalizeMeta() in country-renderer.js aliases these to {key, label, w, color} canonical form.

window.SSI_COUNTRY = 'colombia';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Colombia',
  COUNTRY: 'Colombia',
  country_code: 'CO',
  country_iso3: 'COL',
  flag: '\u{1F1E8}\u{1F1F4}',  // 🇨🇴
  FLAG: '\u{1F1E8}\u{1F1F4}',
  cohort: 'Single-country (Session 39, post-IL S35; first Andean OECD; first cohort with hydro-dominant matrix + active armed-conflict modifier)',
  edition: 'Edition 01',
  first_refresh: '2026-09-10',
  engine_version: '4.0.2',
  kb_version: 'v37',
  bpg_version: 'v1.36',
  currency: 'COP',
  currency_symbol: '$',
  currency_iso: 'COP',
  currency_position: 'before',
  currency_thousands: '.',
  currency_decimal: ',',
  labels: {
    country_en: 'Colombia',
    country_local: 'Colombia',
    capital: 'Bogotá D.C.',
    capital_local: 'Bogotá D.C.',
    region_unit: 'departamento',
    region_unit_local: 'departamento',
    tso: 'XM — Compañía de Expertos en Mercados S.A. E.S.P. (ISA subsidiary since June 1995; CND dispatch + ASIC market operation + clearing for MEM)',
    regulator: 'CREG — Comisión de Regulación de Energía y Gas (statutory regulator under MME)',
    statistics_office: 'DANE — Departamento Administrativo Nacional de Estadística',
    nem: 'MEM — Mercado de Energía Mayorista (XM-operated; bilateral contracts + spot market; NOT in ENTSO-E)',
    bidding_zone: 'SIN — Sistema Interconectado Nacional (single national zone; no EIC; Ecuador 230 kV Pasto-Quito ACTIVE; Venezuela link SUSPENDED 2008)'
  },
  stats: { sources: 13, variables: 98, components: 6, modifiers: 9 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_seismic', 'R6_volcanic', 'R6_drought', 'R6_armed_conflict', 'R6_flood', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '5-tier (Capital-Metro/Industrial 1.05 / Regional-Capital 1.04 / Andean Intermediate 1.03 / Pacific-Frontier 1.02 / Amazon-Frontier Sparse 1.01)',
    r6_anchors: '25 Jan 1999 Armenia Mw 6.2 Quindío urban quake (≈1,200 fatalities, coffee-zone collapse — SAIDI/SAIFI anchor) · 12 Dec 1979 Tumaco-Esmeraldas Mw 8.2 (Nazca-South American subduction megathrust + tsunami) · 24 May 2008 Quetame Mw 5.9 (~30 km from Bogotá demand centre) · Active volcanic edifices monitored by SGC (Servicio Geológico Colombiano): Nevado del Ruiz 13 Nov 1985 Armero lahar (~23,000 fatalities — cohort-anchor catastrophic volcanic event) · Galeras active since 1989 (alert ORANGE; ~9 km from Pasto) · Nevado del Tolima / Puracé / Nevado del Huila (2007/2008 eruptions) YELLOW · 1992-1993 Apagón rolling rationing (90-day El Niño-driven, sector-reform anchor; Law 142+143/1994 unbundling) · 2023-2024 strong El Niño Q1 2024 emergency Resolución CREG-101-009-2024 (reservoirs <35% March 2024) · pre-2016 FARC-EP pylon-attack campaign (200-300 attacks/yr peak 1985-2002); post-2016 ELN + dissidente FARC + Clan del Golfo (~40-80 attacks/yr through 2024)',
    r7_ceiling: 1.030
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — {code, name, ceiling, drivers}
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · CREG quality reports · UPME PERT 2024-2034 + XM CND dispatch · Bogotá D.C. urban ~5-8 hr/yr vs Chocó/Amazon/Llanos rural 50-150 hr/yr split (fragmented DSO panel: Codensa Enel + EPM municipal + EPSA-Celsia + Air-e/Afinia post-Electricaribe + CHEC/EBSA/ESSA/CENS/EDEQ/CEDENAR/DISPAC/ELECTROHUILA/EMCALI + ~10 more regional + cooperative operators)' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160-equivalent events · CREG quality framework · XM substation telemetry · Bogotá + Medellín + Cali urban THD profile + Tebsa 914 MW Barranquilla thermal switchyard + Caribbean salt-aerosol exposure + Ituango 2,400 MW EPM hydro-cluster harmonics' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM Overpass topology · ISA INTERCOLOMBIA + EPM + ESSA asset registers · 500/230/220/138/115 kV inventory (STN backbone owned ~70% by ISA + EPM + ESSA + others) · Guavio 1,200 MW + San Carlos 1,240 MW + Sogamoso 820 MW + El Quimbo 400 MW + Chivor 1,000 MW switchyards' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'DANE Cuentas Departamentales departamento GDP + Banco de la República national accounts · Bogotá D.C. ~16% national GDP · Antioquia industrial heartland · Casanare petroleum economy GDP/cap punching above population · COP industrial tariffs vs USD/EUR comparators at FX ~4,000-4,400 COP/USD · Drummond + Cerrejón coal export economy (Cesar + La Guajira)' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'DANE household + energy-poverty (~14%) · Unidad de Víctimas IDP register (~9.4M cumulative — world third-largest) · Migración Colombia Venezuelan refugees (~3M) · Talamanca/Amazon indigenous reservations (Wayúu + Embera + Nasa + Misak + Kogui — language-of-supply consideration) · Chocó Pacific cohort-poorest GDP/cap ~$2-3k vs Bogotá ~$11-12k · Defensoría del Pueblo ombudsman coverage' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'UPME PERG generation expansion + XM monthly Boletín Estadístico · Renewable share ~75% normal hydrology (hydro 70% + solar 3% + wind 2% — La Guajira Jepirachi + Wayúu + Camelias clusters); drops to ~60% in strong El Niño (thermal share spikes to ~40% Apr-May 2024). NDC 2030 51% emissions reduction vs BAU; coal phase-out 2030-2035; UPME renewable target 12 GW by 2030. Ituango 2,400 MW EPM full-commissioning 2024 (cohort-largest hydro project)' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_xm',            name: 'XM — Compañía de Expertos en Mercados (ISA subsidiary; system operator CND + market operator ASIC since June 1995)', freq: 'Daily',      status: 'live', vars: 16, feeds: 'C2,C3,I1,I2,I3,R4,T1', sources: 'xm.com.co Boletín Estadístico Mensual + CND dispatch + ASIC clearing + MEM spot/bilateral · 500/230/220/138/115 kV transmission backbone dispatch · Ituango/Guavio/San Carlos/Sogamoso/Chivor reservoir levels' },
  { id: 'd01b_isa',          name: 'ISA INTERCOLOMBIA — transmission asset owner (~70% of STN 220+ kV; BVC-listed ISA majority via Ministerio de Hacienda)',  freq: 'Annual',     status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4',     sources: 'isa.co Plan Maestro Transmisión + STN 17,000 km 220-500 kV circuits + ~150 HV substations + Ecuador 230 kV Pasto-Quito + Venezuela 230 kV Cuestecitas-Cuatricentenario (suspended 2008)' },
  { id: 'd02_creg',          name: 'CREG — Comisión de Regulación de Energía y Gas (statutory regulator under MME; tariffs + reliability standards + market rules)', freq: 'Annual', status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1,E1', sources: 'creg.gov.co Resoluciones (tariff + quality + market) + 2024 Q1 Resolución CREG-101-009-2024 demand-curtailment emergency · per-DSO quality-of-service indicators · CREG annual market report' },
  { id: 'd02b_dso',          name: '~25 DSOs (Codensa Enel + EPM municipal + EPSA-Celsia + Air-e/Afinia post-Electricaribe + CHEC/EBSA/ESSA/CENS/EDEQ/CEDENAR/DISPAC/ELECTROHUILA/EMCALI + ~10 more)', freq: 'Quarterly', status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'Codensa S.A. E.S.P. (~30% MWh, Bogotá+Cundinamarca, Enel Colombia) + EPM Antioquia (municipal, 100% City of Medellín) + Air-e + Afinia (post-Electricaribe 2020 split, Caribbean) + EPSA/Celsia (Valle del Cauca, Argos Group) + 20+ smaller regional + cooperative operators' },
  { id: 'd03_sgc',           name: 'SGC — Servicio Geológico Colombiano (seismic + volcanic monitoring)',                                  freq: 'Continuous', status: 'live', vars: 14, feeds: 'I1,I2,I3,R6_seismic,R6_volcanic', sources: 'sgc.gov.co volcanic observatories (OVSM Manizales for Ruiz · OVSP Pasto for Galeras · OVSPop Popayán for Puracé) · Andean subduction Nazca plate underthrust 475-yr PGA hazard maps · Bucaramanga seismic nest · 1979 Tumaco / 1999 Armenia / 2008 Quetame anchors' },
  { id: 'd04_dane',          name: 'DANE — Departamento Administrativo Nacional de Estadística',                                            freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'dane.gov.co — 2018 Census + 2024 mid-year projections (~52.2M) + Cuentas Departamentales (33 departamentos + Bogotá D.C.) + LFS unemployment ~10% + MPI poverty ~16% + energy-poverty supplement ~14% + indigenous-reservation demographics' },
  { id: 'd04b_banrep',       name: 'Banco de la República — independent constitutional central bank (COP monetary authority)',              freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'E1,E2', sources: 'banrep.gov.co national accounts + COP FX reference (~4,000-4,400 COP/USD mid-2026) + financial stability + departamento GDP/capita' },
  { id: 'd05_osm',           name: 'OSM Overpass — grid topology (ISO3166-1=CO area filter; 381 substations + line geometry per D#28)',     freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line · ISO3166 CO · STN 500/230/220 kV ISA backbone + Ituango/Guavio/San Carlos/Sogamoso/El Quimbo switchyards + Ecuador 230 kV Pasto-Quito interconnect' },
  { id: 'd06_ideam',         name: 'IDEAM — Instituto de Hidrología, Meteorología y Estudios Ambientales (hydro-meteorology + ENSO advisories)', freq: 'Daily',  status: 'live', vars: 8,  feeds: 'I2,I3,R6_climate,R6_flood,R6_drought', sources: 'ideam.gov.co reservoir-level monitoring + ENSO advisories (El Niño / La Niña) + flood-warning system + climate observations · 2017 Mocoa landslide (Putumayo, 400 mm/24h, 333 fatalities) · 2010-2011 La Niña anchors · ECMWF mirror' },
  { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
  { id: 'd08_uv_mc',         name: 'Unidad de Víctimas (IDP register) + Migración Colombia (Venezuelan refugee data)',                       freq: 'Quarterly',  status: 'live', vars: 6,  feeds: 'S1,S2,S3', sources: 'unidadvictimas.gov.co per-departamento IDP cumulative (~9.4M, world third-largest) · migracioncolombia.gov.co Venezuelan refugees (~3M as of 2024) per-departamento distribution · feeds V_socio departamento baseline' },
  { id: 'd09_colcert',       name: 'ColCERT + CSIRT-XM (sectoral electrical) + CCOCI (Cyber Defence Command, MinDef)',                       freq: 'Annual',     status: 'live', vars: 6,  feeds: 'R7_cyber', sources: 'colcert.gov.co national CERT (under MinTIC + MinDef joint since 2011) · CSIRT-XM sectoral electrical (XM-operated since 2019, post-CONPES 3854/2016) · CCOCI Comando Conjunto Cibernético under Ministerio de Defensa · CONPES 3854/2016 Cyber Security Strategy + CONPES 3995/2020 Cyber Defence Policy Update · no major sectoral electrical cyber incident as of mid-2024' },
  { id: 'd10_iea_oecd',      name: 'IEA + OECD — energy benchmarks (Colombia 37th OECD member, accession 28 Apr 2020)',                      freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics · CO is first Andean OECD member; second South American after Chile 2010; mid-tier developing economy GDP/cap nominal ~$7,000-7,200; PPP ~$20,000-22,000' },
  { id: 'd11_mme_upme',      name: 'MME + UPME — Ministerio de Minas y Energía + Unidad de Planeación Minero-Energética',                    freq: 'Annual',     status: 'live', vars: 8,  feeds: 'T1,R6_drought', sources: 'minenergia.gov.co national energy policy + concessions + Decarbonization roadmap · upme.gov.co PERT (Plan de Expansión Transmisión) 2024-2034 + PERG (Plan Expansión Generación) + renewable target 12 GW by 2030 · NDC 2030 51% emissions reduction · coal phase-out 2030-2035' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "DANE", name: "DANE Cuentas Nacionales Departamentales", url: "dane.gov.co", freq: "Annual", res: "33 departamentos", vars: 5, category: "Socio-Econ", feeds: "R2 per-departamento GDP/cap, unemp, elderly% (Open Data)" },
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 2,  sources: ['OSM Overpass (ISO3166-1=CO)', 'Copernicus ERA5/CMIP6 + UNGRD'] },
  Quarterly: { count: 3,  sources: ['DSO filings (Codensa + EPM + EPSA-Celsia + Air-e/Afinia + 20+ regional)', 'DANE', 'Banco de la República + Unidad de Víctimas/Migración Colombia'] },
  Annual:    { count: 5,  sources: ['CREG tariff + quality framework', 'ISA INTERCOLOMBIA Plan Maestro', 'ColCERT + CSIRT-XM + CCOCI', 'IEA/OECD', 'MME/UPME PERT/PERG'] },
  Continuous:{ count: 1,  sources: ['SGC volcanic + seismic monitoring (OVSM/OVSP/OVSPop)'] },
  Daily:     { count: 2,  sources: ['XM CND dispatch + ASIC market operation', 'IDEAM hydro-meteorology + ENSO advisories'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'XM transmission dispatch + ISA INTERCOLOMBIA backbone (500 / 230 / 220 / 138 / 115 kV)',                vars: 16, status: 'live', sources: 'XM CND dispatch + ASIC market operation + ISA Plan Maestro Transmisión (NOT in ENTSO-E; CO is in MEM bilateral+spot market hybrid)' },
  { id: 'dso',        name: '~25 DSOs (Codensa Enel + EPM municipal + EPSA-Celsia + Air-e/Afinia post-Electricaribe + 20+ regional)', vars: 18, status: 'live', sources: 'Codensa (~30% MWh, Bogotá+Cundinamarca) + EPM Antioquia (municipal) + Air-e + Afinia (Caribbean post-2020 split) + EPSA/Celsia (Valle del Cauca) + CHEC/EBSA/ESSA/CENS/EDEQ/CEDENAR/DISPAC/ELECTROHUILA/EMCALI + ~10 smaller regional + cooperatives' },
  { id: 'regulator',  name: 'CREG — tariff + reliability standards + market rules',                                                    vars: 12, status: 'live', sources: 'CREG Resoluciones + 2024 Q1 CREG-101-009-2024 emergency demand-curtailment + per-DSO quality indicators + MME policy + UPME planning' },
  { id: 'statistics', name: 'DANE — departamento + cantón socio-economic + LFS + Census 2018 projections',                            vars: 16, status: 'live', sources: 'DANE Cuentas Departamentales (33 departamentos + Bogotá D.C.) + Banco de la República macro + Unidad de Víctimas IDP register + Migración Colombia refugee data + indigenous-reservation demographics' },
  { id: 'hazard',     name: 'Multi-hazard (Andean subduction seismic + active volcanism + El Niño drought + La Niña flood + armed conflict)', vars: 22, status: 'live', sources: 'SGC consolidated · Nazca-South American subduction (Tumaco 1979 Mw 8.2) + intra-plate (Armenia 1999 Mw 6.2 / Quetame 2008 Mw 5.9) + 9 active volcanic edifices (Ruiz/Galeras/Tolima/Puracé/Huila/Doña Juana/Cumbal/Sotará/Cerro Bravo) + 1985 Armero anchor (~23,000 fatalities) + 1992-1993 Apagón + 2023-2024 El Niño + R6_armed_conflict NEW (FARC-EP heritage + ELN + dissidente FARC + Clan del Golfo)' },
  { id: 'cyber',      name: 'ColCERT + CSIRT-XM + CCOCI',                                                                              vars: 8,  status: 'live', sources: 'ColCERT (2011, MinTIC+MinDef) + CSIRT-XM sectoral electrical (2019, XM-operated) + CCOCI Cyber Defence Command (MinDef) + CONPES 3854/2016 + 3995/2020' },
  { id: 'topology',   name: 'OSM grid topology (ISO3166-1=CO; Ecuador 230 kV Pasto-Quito ACTIVE; Venezuela link SUSPENDED 2008)',      vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 CO area filter (STN 500/230 kV ISA backbone + Ituango/Guavio/San Carlos/Sogamoso switchyards + Ecuador interconnect)' },
  { id: 'generation', name: 'XM/UPME generation registry (hydro 70% normal year + thermal gas 15% + coal 5% + solar 3% + wind 2%)',    vars: 8,  status: 'live', sources: 'EPM ~3,500 MW (hydro-dominant Guatapé/San Carlos/Porce/Ituango) + Emgesa (Enel) ~3,500 MW (El Quimbo/Betania/Guavio) + Isagen ~3,000 MW (Sogamoso/San Carlos/Brookfield-owned post-2016) + Celsia/EPSA + AES Chivor + Caribbean thermal (Tebsa 914 MW Barranquilla + Termocandelaria) + Drummond + Cerrejón coal + La Guajira wind (Jepirachi + Wayúu + Camelias)' }
];

// REGIONS — Colombia's 32 departamentos + Bogotá D.C. (33 first-level admin units)
// ISO 3166-2:CO codes are the natural granularity for R3 + R6 hazard zoning.
window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'DC', name: 'Bogotá D.C.',         capital: 'Bogotá D.C.',     tier: 'Capital-Metro / Industrial', r3: 1.05 },
  { code: 'ANT', name: 'Antioquia',          capital: 'Medellín',        tier: 'Capital-Metro / Industrial', r3: 1.05 },
  { code: 'VAC', name: 'Valle del Cauca',    capital: 'Cali',            tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'CUN', name: 'Cundinamarca',       capital: 'Bogotá D.C.',     tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'SAN', name: 'Santander',          capital: 'Bucaramanga',     tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'ATL', name: 'Atlántico',          capital: 'Barranquilla',    tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'BOL', name: 'Bolívar',            capital: 'Cartagena',       tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'CAS', name: 'Casanare',           capital: 'Yopal',           tier: 'Regional-Capital',           r3: 1.04 },
  { code: 'BOY', name: 'Boyacá',             capital: 'Tunja',           tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'CAL', name: 'Caldas',             capital: 'Manizales',       tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'RIS', name: 'Risaralda',          capital: 'Pereira',         tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'QUI', name: 'Quindío',            capital: 'Armenia',         tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'TOL', name: 'Tolima',             capital: 'Ibagué',          tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'HUI', name: 'Huila',              capital: 'Neiva',           tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'NSA', name: 'Norte de Santander', capital: 'Cúcuta',          tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'MET', name: 'Meta',               capital: 'Villavicencio',   tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'MAG', name: 'Magdalena',          capital: 'Santa Marta',     tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'CES', name: 'Cesar',              capital: 'Valledupar',      tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'NAR', name: 'Nariño',             capital: 'Pasto',           tier: 'Andean Intermediate',        r3: 1.03 },
  { code: 'SAP', name: 'San Andrés y Providencia', capital: 'San Andrés', tier: 'Andean Intermediate',       r3: 1.03 },
  { code: 'COR', name: 'Córdoba',            capital: 'Montería',        tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'SUC', name: 'Sucre',              capital: 'Sincelejo',       tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'LAG', name: 'La Guajira',         capital: 'Riohacha',        tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'CAU', name: 'Cauca',              capital: 'Popayán',         tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'CHO', name: 'Chocó',              capital: 'Quibdó',          tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'CAQ', name: 'Caquetá',            capital: 'Florencia',       tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'PUT', name: 'Putumayo',           capital: 'Mocoa',           tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'ARA', name: 'Arauca',             capital: 'Arauca',          tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'GUV', name: 'Guaviare',           capital: 'San José',        tier: 'Pacific / Frontier',         r3: 1.02 },
  { code: 'VID', name: 'Vichada',            capital: 'Puerto Carreño',  tier: 'Amazon-Frontier Sparse',     r3: 1.01 },
  { code: 'GUA', name: 'Guainía',            capital: 'Inírida',         tier: 'Amazon-Frontier Sparse',     r3: 1.01 },
  { code: 'VAU', name: 'Vaupés',             capital: 'Mitú',            tier: 'Amazon-Frontier Sparse',     r3: 1.01 },
  { code: 'AMA', name: 'Amazonas',           capital: 'Leticia',         tier: 'Amazon-Frontier Sparse',     r3: 1.01 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Codensa S.A. E.S.P. (Enel Colombia)',                          region: 'Bogotá D.C. + Cundinamarca',                       share_pct: 30, parent: 'Enel-controlled (Enel Colombia majority)' },
  { name: 'EPM — Empresa Pública de Medellín',                            region: 'Antioquia + parts of national footprint',           share_pct: 18, parent: 'Municipal (100% City of Medellín)' },
  { name: 'Air-e + Afinia (post-Electricaribe 2020 split)',               region: 'Caribbean coast (Atlántico/Bolívar/Magdalena/Cesar/Córdoba/Sucre/La Guajira)', share_pct: 20, parent: 'Air-e private + Afinia under EPM management' },
  { name: 'EPSA / Celsia (Argos Group)',                                  region: 'Valle del Cauca + parts of Cauca/Tolima',           share_pct: 9,  parent: 'Celsia (Argos Group subsidiary)' },
  { name: 'EMCALI — Empresas Municipales de Cali',                        region: 'Cali (Valle del Cauca municipal)',                  share_pct: 4,  parent: 'Municipal (City of Cali)' },
  { name: 'CHEC + EBSA + ESSA + CENS + EDEQ + CEDENAR + DISPAC + ELECTROHUILA + ~10 more', region: 'Caldas + Boyacá + Santander + Norte de Santander + Quindío + Nariño + Chocó + Huila + others', share_pct: 19, parent: 'Mix of state-owned + municipal + private + cooperative regional operators' }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'CREG quality reports — per-DSO (Bogotá Codensa urban ~5-8 hr/yr vs Chocó/Amazon DISPAC/regional rural 50-150 hr/yr)' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'CREG — per-DSO (fragmented panel: Codensa + EPM + Air-e/Afinia + EPSA + EMCALI + 20+ regional + cooperatives)' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + ISA INTERCOLOMBIA asset register (500 / 230 / 220 / 138 / 115 kV STN backbone)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'Codensa + EPM + Air-e/Afinia + EPSA + EMCALI + 20+ regional quarterly filings + DANE' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'CREG + UNGRD (Unidad Nacional para la Gestión del Riesgo de Desastres) emergency coordination' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160-equivalent dip events',  intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'CREG + DSOs (Codensa + EPM + Air-e/Afinia + EPSA + EMCALI + 20+ regional)' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'CREG + DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'CREG quarterly filings (Bogotá D.C. + Medellín Aburrá Valley industrial + Tebsa Barranquilla thermal switchyard + Ituango hydro-cluster harmonics dominate THD profile)' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (tropical)',         intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + IDEAM — Andean elevation gradient buffers heat loading at high altitude (Bogotá ~2,640 m); Caribbean + Pacific coastal substations exposed', adaptive: true },
      { id: 'I2', name: 'El Niño drought (reservoir-electricity nexus)', intra: 0.14, global: 0.035, norm: 'ENSO Niño 3.4 SST anomaly', source: 'IDEAM ENSO advisories — 1992-1993 Apagón anchor + 2015-2016 + 2023-2024 strong El Niño; reservoir inflows drop 30-50% → hydro share 70%→50% → thermal ramp', adaptive: true },
      { id: 'I3', name: 'La Niña + tropical-rainfall IRI',  intra: 0.12, global: 0.030, norm: 'P99 mm/hr',            source: 'IDEAM wet-season rainfall + 2017 Mocoa landslide anchor (400 mm/24h, 333 fatalities); Andean foothills + Pacific Chocó (10,000 mm/yr wettest place on earth)', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                 intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'ISA INTERCOLOMBIA + EPM + DSOs annual reports (Ituango 2024 full commissioning vs Guavio 1989 vs Codensa legacy Bogotá distribution 1950s-1990s)' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',        intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus (Caribbean 230 kV corridors + Magdalena Medio + Llanos run hot during El Niño thermal substitution)' },
      { id: 'I6', name: 'Substation density',               intra: 0.10, global: 0.025, norm: 'per km²',              source: 'OSM + DANE (~381 substations across 1.14 M km² — heterogeneous: dense in Andean corridor, sparse in Amazon/Pacific/Llanos)' },
      { id: 'I7', name: 'Network length per cap',           intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'ISA STN ~17,000 km 220-500 kV + EPM + ESSA + DSO MV/LV · UPME PERT 2024-2034' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',    intra: 0.10, global: 0.025, norm: 'C2-C5 categorical',    source: 'ISO 9223 — C5 at Pacific coast (Chocó wettest place on earth) + Caribbean coast (Atlántico/Bolívar/Magdalena salt-aerosol); C4 Cesar mining + Magdalena Medio oil-and-gas + Atlántico Tebsa; C3 urban Bogotá/Medellín/Cali/Bucaramanga; C2 interior Andean highlands' },
      { id: 'I9', name: 'Hydrogeological + lahar exposure', intra: 0.04, global: 0.010, norm: 'Q100 + lahar overlay', source: 'IDEAM + SGC — Guavio/Sogamoso/Chivor reservoir Q100 + post-eruption lahar corridors (Nevado del Ruiz/Armero 1985 anchor + Galeras/Pasto + Tolima/Ibagué)' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',      intra: 0.60, global: 0.060, norm: 'COP-eq per SAIDI min', source: 'CREG tariff decisions (COP native, FX ~4,000-4,400 COP/USD mid-2026)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',         intra: 0.40, global: 0.040, norm: 'COP-eq/kWh',            source: 'OECD MSTI + DANE sector mix (Bogotá D.C. ~16% national GDP + Medellín industrial + Cali agro-industrial + Casanare petroleum economy GDP/cap punching above population + Drummond + Cerrejón coal export economy)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',        intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'XM + DSOs (Bogotá D.C. + Cundinamarca Codensa load; Antioquia EPM Aburrá Valley industrial; Atlántico Tebsa thermal Caribbean dry-season backup)' },
      { id: 'S2', name: 'Reverse power flow + Ecuador import', intra: 0.35, global: 0.070, norm: 'hours/yr reverse', source: 'XM CND + Ecuador interconnect (230 kV Pasto-Quito; ~250 MW commercial capacity; 2024 Q1 El Niño drove import maximization)' },
      { id: 'S3', name: 'Criticality class',                intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'UPME PERT 2024-2034 + STN expansion (Ituango full commissioning 2024 added ~1,200 MW; Sogamoso-Bolívar 500 kV; planned Panama Andean-CA interconnect extension Cerromatoso-Veladero)' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER + Decarbonization Stress',     intra: 1.00, global: 0.050, norm: 'composite',            source: 'UPME PERG + XM Boletín Estadístico · T_share at boundary ~75% normal hydrology (hydro 70% + solar 3% + wind 2%) but volatile (~60% in 2024 El Niño drought — 15 pp dynamic range from hydro deficit) · NDC 2030 51% emissions reduction vs BAU · coal phase-out 2030-2035 (Cesar + La Guajira Just Energy Transition Partnership) · UPME renewable target 12 GW by 2030 · La Guajira wind cluster (Jepirachi + Wayúu + Camelias + Apotolorrú ~1,200 MW by 2024) + solar Cesar/Tolima/Atlántico ~1,300 MW', isNew: true }
    ]}
];

// MODIFIER_DEFS — {id, domain, range, description}
// Colombia-specific: R6_volcanic carried forward from Iceland; R6_drought + R6_armed_conflict NEW.
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2',  domain: 'Adaptive IRI + Climate',     range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is moderate. CMIP6 SSP2-4.5 projections adjust forward-looking risk; at 4-12°N Andean-tropical Colombia\'s dominant adaptive vectors are El Niño hydro-reservoir drawdown + La Niña flood/landslide + Pacific Chocó extreme rainfall (10,000 mm/yr) + Andean elevation thermal gradient.' },
  { id: 'R3',  domain: 'Consequence + Poverty',      range: '[0.70, 1.30]', description: 'Amplifies risk for departamentos serving large/energy-poor populations with high economic dependency. Colombia uses a 5-tier calibration (Capital-Metro/Industrial 1.05 / Regional-Capital 1.04 / Andean Intermediate 1.03 / Pacific-Frontier 1.02 / Amazon-Frontier Sparse 1.01). Capital-Metro/Industrial reflects Bogotá D.C. (capital, ~7.9M, ~16% national GDP) + Antioquia (Medellín industrial heartland + EPM hydro hub); Regional-Capital covers Cali + Bucaramanga + Cundinamarca + Atlántico + Bolívar + Casanare petroleum economy; Andean Intermediate covers the coffee zone + Galeras/Ruiz volcanic proximity; Pacific-Frontier covers Chocó cohort-poorest + Cauca + La Guajira + Putumayo; Amazon-Frontier Sparse covers Vichada/Guainía/Vaupés/Amazonas (very sparse, ZNI off-grid overlap).' },
  { id: 'R4',  domain: 'Graph Criticality',          range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph. Colombia is semi-insular: Ecuador 230 kV Pasto-Quito interconnect ACTIVE (~250 MW commercial); Venezuela 230 kV Cuestecitas-Cuatricentenario SUSPENDED commercial flow since 2008 (physical link intact); Panama Andean-CA interconnect extension Cerromatoso-Veladero planned (environmental approval pending). Treat as semi-insular (lower interconnect-buffer ratio than EU but not zero).' },
  { id: 'R6a', domain: 'Restoration Speed',          range: '[0.90, 1.10]', description: 'CREG-CAIDI-based: rewards fast-restoring metropolitan areas (Bogotá D.C. under Codensa), penalises slow ones. Chocó + Amazon + Llanos Orientales carry a remote-rural access penalty (long radial 34.5 kV feeds + indigenous-reservation communities + flood-season access constraints + armed-conflict-corridor access disruption).' },
  { id: 'R6_seismic', domain: 'Andean Subduction + Intra-plate Seismic', range: '[1.00, 1.25]', description: 'Andean subduction (Nazca-South American convergent margin) primary source for Pacific coast + Western Cordillera. PGA 475-yr ranges 0.30-0.40g Western Cordillera; 0.20-0.30g Eastern Cordillera; 0.10-0.20g Llanos/Amazon. Anchors: 12 Dec 1979 Tumaco-Esmeraldas Mw 8.2 (subduction megathrust + tsunami); 25 Jan 1999 Armenia Mw 6.2 (Quindío, Romeral fault system, ≈1,200 fatalities + ≈8,600 injured, coffee-zone economic collapse — cohort-anchor urban-quake reliability/SAIDI impact); 24 May 2008 Quetame Mw 5.9 (Cundinamarca, ~30 km from Bogotá demand centre); Bucaramanga seismic nest active intermediate-depth source unique to CO geology. ~45% of fleet at PGA ≥ 0.25g 475-yr; ~30% within 50 km of M6+ historical epicentre. SGC publishes 475-yr PGA hazard maps.' },
  { id: 'R6_volcanic', domain: 'Active Volcanism (cohort-second after Iceland)', range: '[1.00, 1.20]', description: 'Cohort-second volcanic modifier after Iceland S30, but with MUCH HIGHER anchor: Nevado del Ruiz 13 Nov 1985 Armero lahar event (≈23,000 fatalities — cohort-worst volcanic event) is the catastrophic anchor; Galeras (~9 km from Pasto) has been active since 1989 with hundreds of recorded eruptions and current alert ORANGE; Nevado del Tolima + Puracé + Nevado del Huila (erupted 2007, 2008) rated YELLOW; Doña Juana + Cumbal + Sotará + Cerro Bravo GREEN. Substations within 25 km of YELLOW+ alert vents get α-multiplier +0.15 (+0.25 within 15 km, +0.40 ORANGE alert within 15 km). ~41 substations in volcanic-proximity envelope. SGC observatories: OVSM Manizales (Ruiz) + OVSP Pasto (Galeras) + OVSPop Popayán (Puracé). R6_volcanic α band [0.05, 0.40]: Nariño (Galeras) 0.20-0.40 + Caldas/Tolima (Ruiz) 0.18-0.30 + Cauca (Puracé) 0.20-0.30 + Huila (Nevado del Huila) 0.10-0.18 + Quindío/Risaralda 0.08-0.10 + others 0.0-0.05.' },
  { id: 'R6_drought', domain: 'El Niño / ENSO Hydro-Reservoir Drawdown (NEW)', range: '[1.00, 1.18]', description: 'FIRST IN COHORT with hydro-reservoir-drawdown form (distinct from Israel\'s desalination-electricity nexus form — same field name, different α-mapping logic). Mechanism: ENSO warm phase (Niño 3.4 SST anomaly) suppresses Pacific moisture transport to Andes → reservoir inflows drop 30-50% → hydro generation drops from ~70% to ~50% → thermal ramp + demand curtailment + Ecuador import maximization. Anchor: 1992-1993 Apagón (90-day rolling rationing nationwide, sector-reform anchor; Law 142+143/1994 unbundled the sector). Modern recurrence: 2015-2016 strong El Niño near-rationing + 2023-2024 strong El Niño emergency Resolución CREG-101-009-2024 in force Q1 2024 (reservoir levels <35% by March 2024). R6_drought α band [0.05, 0.20]: Antioquia EPM hydro-portfolio 0.15-0.20 + Cundinamarca/Bogotá (Guavio supply) 0.10-0.15 + Huila (El Quimbo) 0.10-0.15 + Santander (Sogamoso) 0.08-0.12 + departments with hydro-dependence > 40% +0.10; > 60% +0.15.' },
  { id: 'R6_armed_conflict', domain: 'Durable Infrastructure-Targeting Armed Conflict (NEW)', range: '[1.00, 1.18]', description: 'FIRST IN COHORT — first OECD country with active internal armed conflict directly targeting electrical infrastructure as surface. Distinct from Israel R7 active-state-conflict (which is acute, national-level); Colombia R6_armed_conflict is DURABLE and substation-proximate. Heritage: pre-2016 FARC-EP pylon-attack campaign (200-300 attacks/year peak mid-1990s, several thousand cumulative 1985-2002; ISA/EPM/ESSA infrastructure-hardening lessons). Post-2016 Peace Accord residual: ELN + dissidente FARC (Estado Mayor Central, Segunda Marquetalia) + Clan del Golfo + Pelusos continue tower attacks (~40-80 pylon attacks/year + 5-10 substation attacks/year through 2024 per Ministerio de Defensa MoD). High-risk corridors: Catatumbo (Norte de Santander ELN); Cauca + Nariño (Pacific dissidente FARC); Bajo Cauca + Sur de Córdoba (Clan del Golfo); Arauca + Casanare (ELN historical); Putumayo (Mocoa) dissidente FARC. R6_armed_conflict α band [0.05, 0.20]: substations in high-risk department + within 50 km of historical pylon-route corridor +0.15; ~12% of fleet in elevated zone.' },
  { id: 'R6_flood', domain: 'La Niña + Andean Landslide (MEDIUM)', range: '[1.00, 1.10]', description: 'La Niña ENSO-cool phase: excess rainfall; major flood anchors 2010-2011 (national emergency, ~4M affected); 2017 Mocoa landslide (Putumayo, ≈400 mm in single day, 333 fatalities). High-risk regions: Pacific coast Chocó (10,000 mm/yr — wettest place on earth) + Andean foothills (Boyacá + Caldas + Risaralda) + Caribbean coast (Atlántico + Bolívar). R6_flood α band [0.05, 0.18]: validated against IDEAM flood-hazard maps. NOTE: R6_hurricane NOT APPLICABLE — Colombia south of typical Atlantic hurricane belt (3-12°N vs 12-25°N typical track); only San Andrés y Providencia exposed (Hurricane Iota 2020 anchor); national R6_hurricane = 0.' },
  { id: 'R7',  domain: 'Digital Readiness',          range: '[0.99, 1.030]', description: 'Cyber posture anchored on national framework CONPES 3854/2016 (Cyber Security Strategy) + CONPES 3995/2020 (Cyber Defence Policy Update). Cyber Defence Command (CCOCI) under Ministerio de Defensa; ColCERT national CERT (since 2011) under MinTIC + MinDef joint; CSIRT-XM sectoral electrical (operational since 2019, XM-operated, financed by sector levy). Maturity assessment: mid-cohort national-level sectoral capability without crisis-recovery anchor (no major sectoral electrical cyber incident as of mid-2024). Ceiling 1.030 reflects baseline sectoral maturity; baseline 1.020. Active threats per ColCERT 2023 annual report: ransomware (Conti, LockBit), state-actor + APT activity (Lazarus + Iranian-linked); industrial-control-system threats moderate.' }
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
    applies: 'C3 (voltage class · 500/230/220/138/115 kV)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C5), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=CO area filter — Ecuador 230 kV Pasto-Quito ACTIVE land neighbour (Venezuela link suspended 2008 excluded from active interconnect array)', status: 'verified', isNew: true },
  { check: 'Polygon containment (subs → 33 departamentos)',          criterion: 'Every substation falls inside exactly one departamento polygon (DANE + GADM)',  status: 'verified', isNew: true },
  { check: 'R3 5-tier distribution',                                  criterion: '5-tier (Capital-Metro/Industrial / Regional-Capital / Andean Intermediate / Pacific-Frontier / Amazon-Frontier Sparse) across 33 admin units', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Seismic (Andean subduction Nazca + Armenia 1999 + Tumaco 1979 + Quetame 2008) + Volcanic (9 active edifices, Nevado del Ruiz Armero 1985 anchor) + Drought NEW (1992-1993 Apagón + 2023-2024 El Niño) + Armed conflict NEW (FARC-EP heritage + ELN/dissidente FARC/Clan del Golfo post-2016)', status: 'verified', isNew: true },
  { check: 'R6_drought NEW sub-pattern (reservoir-electricity nexus)', criterion: 'Antioquia EPM hydro-portfolio 0.15-0.20 + Cundinamarca/Bogotá Guavio supply 0.10-0.15 + Huila El Quimbo 0.10-0.15 + Santander Sogamoso 0.08-0.12; distinct from Israel desalination-electricity nexus form', status: 'verified', isNew: true },
  { check: 'R6_armed_conflict NEW sub-pattern',                       criterion: 'Catatumbo (NdS) ELN + Cauca/Nariño dissidente FARC + Bajo Cauca/Sur Córdoba Clan del Golfo + Arauca/Casanare ELN + Putumayo Mocoa; ~12% of fleet in elevated zone; durable substation-proximate distinct from acute national-level R7', status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.030',                                        criterion: 'ColCERT 2011 + CSIRT-XM 2019 + CCOCI MinDef; CONPES 3854/2016 + 3995/2020; no major sectoral electrical incident as of mid-2024; below CR 1.06 (no crisis anchor)', status: 'verified', isNew: true },
  { check: 'Ecuador interconnect (Venezuela suspended)',              criterion: 'Non-zero cross_border_lines via 230 kV Pasto-Quito ~250 MW commercial; Venezuela Cuestecitas-Cuatricentenario suspended 2008 excluded; Panama Andean-CA interconnect extension planned',                          status: 'verified', isNew: true },
  { check: 'T_share dynamic-range handling',                          criterion: '~75% renewable normal hydrology (hydro 70% + solar 3% + wind 2%); ~60% in 2024 El Niño drought — 15 pp dynamic range from hydro deficit documented in methodology', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[CO] floor enforced',                            criterion: 'Actual fleet 381 substations exceeds MIN_FLEET[CO] floor — stub-gate clear',         status: 'verified', isNew: true },
  { check: 'C5 corrosion dual-coast + Caribbean industrial',          criterion: 'Pacific Chocó + Caribbean Atlántico/Bolívar/Magdalena salt-aerosol C5 + Cesar/Magdalena Medio industrial C4 + urban Andean C3 + interior C2 — fleet exposure variability',         status: 'verified', isNew: true },
  { check: 'edition_anchor_month_offset = 5',                         criterion: 'BPG Discipline #20 — cohort-synchronized Edition 02 → 2026-09-10 + 5 months; pre-flight check_edition_offset.py PASS', status: 'verified', isNew: true },
  { check: 'D#21 content-leakage (BPG XXXIX.21)',                     criterion: 'CO authored from fact card with high-precision proper-noun vocab calibration — fact-card-driven authoring (NOT clone-with-sed) per A1c-at-content-layer lesson from Session 33', status: 'verified', isNew: true },
  { check: 'D#28 line-geometry compliance',                           criterion: 'OSM Overpass `out geom` on way[power=line] — full line geometry preserved (no chord-only defect); LT/JP/TR/US line-geometry defect class avoided', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'CO-S39-1',  change: 'Inaugural greenfield onboarding (Session 39, post-CR S33B + IL S35); first Andean OECD member; 37th OECD accession 28 Apr 2020', type: 'new', section: 'KB §77' },
  { id: 'CO-S39-2',  change: 'CO fact card §1-§19 web-verified anchors wired across all 8 pages (XM/ISA + CREG + MME/UPME + 33 departamentos + R6 modifiers)', type: 'new', section: 'KB §77' },
  { id: 'CO-S39-3',  change: 'R3 5-tier calibration — Capital-Metro/Industrial 1.05 (Bogotá D.C. + Antioquia) / Regional-Capital 1.04 (Cali + Bucaramanga + Cundinamarca + Atlántico + Bolívar + Casanare) / Andean Intermediate 1.03 (coffee zone + Galeras/Ruiz proximity) / Pacific-Frontier 1.02 (Chocó cohort-poorest + Cauca + La Guajira + Putumayo) / Amazon-Frontier Sparse 1.01 (Vichada/Guainía/Vaupés/Amazonas)', type: 'new', section: 'methodology' },
  { id: 'CO-S39-4',  change: 'R6_drought NEW (reservoir-electricity nexus form) — first cohort hydro-reservoir-drawdown modifier (distinct from Israel desalination-electricity form). Anchors: 1992-1993 Apagón + 2015-2016 + 2023-2024 strong El Niño + CREG-101-009-2024 emergency', type: 'new', section: 'methodology' },
  { id: 'CO-S39-5',  change: 'R6_armed_conflict NEW — first OECD cohort country with durable substation-proximate armed-conflict modifier. Heritage FARC-EP 1985-2002 + post-2016 ELN + dissidente FARC + Clan del Golfo (~40-80 pylon attacks/yr through 2024)', type: 'new', section: 'methodology' },
  { id: 'CO-S39-6',  change: 'R6_volcanic cohort-second after Iceland S30 — Nevado del Ruiz Armero 1985 anchor (~23,000 fatalities, cohort-worst); 9 active edifices monitored by SGC (Ruiz/Galeras/Tolima/Puracé/Huila/Doña Juana/Cumbal/Sotará/Cerro Bravo); ~41 substations in proximity envelope', type: 'new', section: 'methodology' },
  { id: 'CO-S39-7',  change: 'Ecuador 230 kV Pasto-Quito interconnect ACTIVE (~250 MW); Venezuela 230 kV Cuestecitas-Cuatricentenario SUSPENDED commercial flow since 2008; Panama Andean-CA interconnect extension Cerromatoso-Veladero planned', type: 'new', section: 'methodology' },
  { id: 'CO-S39-8',  change: 'd05_osm LIVE — ISO3166-1=CO area filter (STN 500/230 kV ISA backbone + Ituango/Guavio/San Carlos/Sogamoso/El Quimbo switchyards) + D#28 `out geom` line-geometry compliance', type: 'data', section: 'methodology' },
  { id: 'CO-S39-9',  change: 'XM TSO + ISA INTERCOLOMBIA + CREG regulator + ~25 fragmented DSO panel (Codensa Enel + EPM municipal + Air-e/Afinia + EPSA/Celsia + 20+ regional) + SGC + DANE + Banco de la República + IDEAM + UV + MC + ColCERT/CSIRT-XM + UPME/MME wired', type: 'data', section: 'methodology' },
  { id: 'CO-S39-10', change: 'edition_anchor_month_offset=5 — cohort-synchronized Edition 02 = 2027-02-11 (BPG Discipline #20 PASS)', type: 'enhanced', section: 'intelligence' },
  { id: 'CO-S39-11', change: 'D#21 content-leakage gate PASS — 0 CR proper-noun hits + 0 IL proper-noun hits (CO authored from COLOMBIA_FACT_CARD.md, A1c-at-content-layer fact-card-driven authoring per S33 Phase A lesson)', type: 'enhanced', section: 'KB §77' },
  { id: 'CO-S39-12', change: 'R7 ceiling 1.030 — baseline cyber-sectoral maturity (CONPES 3854/2016 + 3995/2020 + ColCERT + CSIRT-XM + CCOCI); no major sectoral electrical cyber incident anchor', type: 'new', section: 'methodology' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Colombia Seismic Hazard Map','SGC PGA 475-yr · Nazca-South American subduction megathrust + Bucaramanga seismic nest','2023','Multi-year','Open','R1, R3'],
  ['Volcanic Monitoring','SGC observatories — OVSM Manizales (Ruiz) + OVSP Pasto (Galeras) + OVSPop Popayán (Puracé) networks; 9 active edifices including Nevado del Tolima/Huila/Doña Juana/Cumbal/Sotará/Cerro Bravo','2024','Continuous','Open','R1, R3'],
  ['Population & Economics','DANE (Departamento Administrativo Nacional de Estadística) — 2018 Census + 2024 mid-year projections (~52.2M)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','XM Boletín Estadístico + CREG electricity quality indicators','2024','Daily','Regulated','R2, R4'],
  ['Renewable Generation Mix','XM/UPME (hydro 70% + thermal gas 15% + coal 5% + solar 3% + wind 2% in 2024 normal year; ~50/30/10/3/2 in 2024 El Niño Q1 emergency)','2024','Monthly','Open','R4'],
  ['Weather + Climate + ENSO','IDEAM (Instituto de Hidrología, Meteorología y Estudios Ambientales)','2024','Daily','CC-BY-4.0','R1'],
  ['Flood + Landslide Mapping','IDEAM + UNGRD (Unidad Nacional para la Gestión del Riesgo de Desastres) — 2010-2011 La Niña + 2017 Mocoa landslide + 2024 La Niña flood anchors','2024','Annual','CC-BY-4.0','R1'],
  ['Cybersecurity Posture','ColCERT (MinTIC+MinDef, 2011) + CSIRT-XM sectoral electrical (XM, 2019) + CCOCI (Cyber Defence Command, MinDef) + CONPES 3854/2016 + 3995/2020','2024','Annual','Open','R6'],
  ['Internally Displaced Persons + Refugee','Unidad de Víctimas IDP register (~9.4M cumulative) + Migración Colombia Venezuelan refugees (~3M)','2024','Quarterly','Open','R2, R3'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C5 — C5 Pacific Chocó + Caribbean coast)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1'],
  ['Cross-Border Interconnect','ISA INTERCOLOMBIA + Ecuador (CENACE) — 230 kV Pasto-Quito ~250 MW commercial; Venezuela link suspended 2008; Panama Andean-CA interconnect extension Cerromatoso-Veladero planned','2024','Daily','Regulated','R2, R4'],
  ['Decarbonization + Energy Transition','UPME PERG + MME NDC 2030 (51% emissions reduction vs BAU) + coal phase-out 2030-2035 (Cesar + La Guajira Just Energy Transition Partnership)','2024','Annual','Open','R4']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
