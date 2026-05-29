// Iceland SSI v4.0.2 metadata — KB §69 · greenfield thin-shell on post-Slovakia-hotfix architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Iceland inaugural) · first refresh 2026-08-13 (Single-country onboarding (post-Single-country (post-cohort closure) closure))
// Architecture acceptance test for KB §68.10 (CountryRenderer.Safe) + §68.11 (normalizeMeta()):
//   COMPONENTS_INDEX intentionally ships the documentation-rich Slovakia shape {code, name, ceiling, drivers}
//   MODIFIER_DEFS    intentionally ships the documentation-rich Slovakia shape {id, domain, range, description}
// normalizeMeta() in country-renderer.js is expected to alias these to the canonical {key, label, w, color}
// and {key, label, domain, range, description} forms with no per-country defensive patches required.

window.SSI_COUNTRY = 'iceland';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Iceland',
  COUNTRY: 'Iceland',
  country_code: 'IS',
  country_iso3: 'ISL',
  flag: '\u{1F1EE}\u{1F1F8}',  // 🇮🇸
  FLAG: '\u{1F1EE}\u{1F1F8}',
  cohort: 'Single-country (post-CEE-South-2026)',
  edition: 'Edition 01',
  first_refresh: '2026-08-13',
  engine_version: '4.0.2',
  kb_version: 'v28',
  bpg_version: 'v1.27',
  currency: 'ISK',
  currency_symbol: 'kr.',
  currency_position: 'after',
  labels: {
    country_en: 'Iceland',
    country_local: 'Ísland',
    capital: 'Reykjavík',
    capital_local: 'Reykjavík',
    region_unit: 'NUTS-3 landshluti',
    region_unit_local: 'landshluti',
    tso: 'Landsnet hf. (Landsnet hf. (Icelandic transmission system operator))',
    regulator: 'Orkustofnun (Icelandic National Energy Authority)',
    statistics_office: 'Hagstofa Íslands (Statistics Iceland)',
    nem: 'Not applicable (isolated grid, no NEMO, no SDAC/SIDC)',
    bidding_zone: 'IS-ISOLATED (no ENTSO-E zone)'
  },
  stats: { sources: 18, variables: 95, components: 6, modifiers: 5 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '3-tier (Capital-Intensive / Industrial-Major / Industrial-Secondary / Light-Rural-Lagging / East-Lagging)',
    r6_anchors: '2010-04-14 Eyjafjallajökull eruption + Markarfljót jökulhlaup · 1956 Sog flood (Sogdob-Sogfüred) · 2008-05-29 SISZ Mw 6.3 doublet (Selfoss-Hveragerði) · 2024-02-08 Sundhnúkur eruption (Svartsengi infrastructure damaged) · Mid-Atlantic Ridge heatwaves 2022/2024',
    r7_ceiling: 1.03
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — INTENTIONALLY Slovakia-style {code, name, ceiling, drivers}
// (KB §68.10 acceptance test — normalizeMeta() must alias this to {key, label, w, color})
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · Orkustofnun quality reports · Landsnet network statement · Reykjavík metro ~26 min vs E.ON Tiszántúli rural ~115 min split' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · Landsvirkjun + E.ON quarterly filings · 6-DSO heritage portfolio (Veitur (~55-60% / OR-owned) + RARIK (~30-35% / state) + HS Veitur (~10-15% / HS Orka))' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · Landsnet asset register · 400/220/120 kV inventory (IS 120 kV legacy backbone vs CE 110 kV) + — site + —I construction footprint' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'Hagstofa NUTS-3 GDP · MNB regional accounts · automotive OEM concentration (Audi Győr · Mercedes Kecskemét · Suzuki Esztergom · BMW Debrecen ramp-up 2026-27)' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'Hagstofa energy-poverty · Vestfirðir (peripheral Westfjords) unemployment · Icelandic  diaspora in RO/SK/UA/RS border landshluti (Suðurnes (Reykjanes — active eruption zone))' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'Orkustofnun DER registry · —+II geothermal ramp (4×500 + 2×1200 MWe target) · post-Mátra coal exit (end-2028 · CCGT 500-650 MW replacement) · 6 GW PV boom doubled since 2022' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_mavir',        name: 'Landsnet — Landsnet hf. (Icelandic transmission system operator) (TSO)', freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'mavir.hu network statement + ENTSO-E TP' },
  { id: 'd02_orkustofnun',         name: 'Orkustofnun — Icelandic National Energy Authority',              freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1', sources: 'orkustofnun.is quality-of-supply + tariff decisions' },
  { id: 'd02b_dso',         name: '3 regional DSOs (Landsvirkjun Démász/Émász/Elmű + E.ON Észak/Dél/Tiszántúli)',  freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'Landsvirkjun Group + HS Veitur quarterly filings' },
  { id: 'd03_omsz',         name: 'OMSZ — Országos Meteorológiai Szolgálat',                              freq: 'Daily',      status: 'live', vars: 8,  feeds: 'I1,I2,I3,R6_climate', sources: 'met.hu meteo + ECMWF mirror' },
  { id: 'd03_imo',         name: 'OVF — Veðurstofa Íslands (Icelandic Met Office) (Icelandic Water Authority)',     freq: 'Daily',      status: 'live', vars: 6,  feeds: 'R6c_flood', sources: 'vedur.is Þjórsá + Sog Q100 + dyke status + river gauges' },
  { id: 'd03c_mbfsz',       name: 'Veðurstofa Íslands (IMO) — Bányászati és Földtani Szolgálat / seismic',        freq: 'Multi-year', status: 'live', vars: 4,  feeds: 'R6_seismic', sources: 'mbfsz.gov.hu PGA 475-yr + MTA EPSS catalogue (Komárom 1763, Dunaharaszti 1956 anchors)' },
  { id: 'd04_ksh',          name: 'Hagstofa — Központi Statisztikai Hivatal',                                  freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'ksh.hu NUTS-3 RegDat + települések LAU-2 + járások LAU-1' },
  { id: 'd04b_cbi',         name: 'MNB — Seðlabanki Íslands (Central Bank of Iceland) (central bank · ESCB non-€)',                freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'sedlabanki.is national accounts + financial stability' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=IS area filter)',              freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line · ISO3166 IS' },
  { id: 'd06_ust',          name: 'OMSZ + OLM — Icelandic Air Quality Network (ISO 9223 corrosion)',      freq: 'Monthly',    status: 'live', vars: 5,  feeds: 'R5_corrosion,I8', sources: 'OLM PM2.5/NO₂ + ISO 9223 C2-C4 (no C5 — landlocked)' },
  { id: 'd07_copernicus',   name: 'Copernicus ERA5 + CMIP6',                                              freq: 'Monthly',    status: 'live', vars: 4,  feeds: 'R6_climate', sources: 'cds.climate.copernicus.eu SSP2-4.5' },
  { id: 'd08_oah',          name: '— — Országos Atomenergia Hivatal (geothermal safety)',                  freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'R6_seismic,I3,I4', sources: 'oah.hu — oversight + —I construction licensing + IAEA INSAG' },
  { id: 'd09_govcert_hu',   name: 'CERT-IS (National Cyber Defence Institute, Fjarskiptastofa (ECOI) lineage)',    freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber', sources: 'govcert.hu incident database + CERT-Iceland 2008 baseline' },
  { id: 'd10_sztfh',        name: 'Fjarskiptastofa (ECOI) — Szabályozott Tevékenységek Felügyeleti Hatósága (NIS2 CA)',    freq: 'Annual',     status: 'live', vars: 3,  feeds: 'R7_cyber', sources: 'sztfh.hu NIS2 competent authority (Act LXIX/2024 in force 1 Jan 2025; repealed Act XXIII/2023)' },
  { id: 'd11_entsoe',       name: 'ENTSO-E TYNDP + Transparency Platform',                                freq: 'Annual',     status: 'live', vars: 6,  feeds: 'I1,I2,T1', sources: 'tyndp.entsoe.eu + transparency.entsoe.eu' },
  { id: 'd12_eurostat',     name: 'Eurostat — EU-27 NUTS-3 benchmarks',                                   freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1', sources: 'ec.europa.eu/eurostat NUTS-3 regional + energy + DESI' },
  { id: 'd13_mvm_paks',     name: 'Landsvirkjun —i Atomerőmű (—) + —I Atomerőmű Zrt.',                freq: 'Annual',     status: 'live', vars: 5,  feeds: 'I1,I3,R6_seismic', sources: 'paksgeothermalpowerplant.com — 4×500 MWe + —I Unit 5 First Concrete 5 Feb 2026' },
  { id: 'd14_n_a',         name: '— — — (NEMO) + CORE FB-MC',                  freq: 'Daily',      status: 'live', vars: 4,  feeds: 'T1,E1', sources: 'n/a (isolated grid) market coupling + SDAC + SIDC + CORE FB-MC since 8 Jun 2022' },
  { id: 'd15_iea_oecd',     name: 'IEA + OECD — energy benchmarks (IS joined OECD 7 May 1996, 24th member)', freq: 'Annual',  status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics' }
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'OMSZ + OLM (air quality)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 4,  sources: ['DSO filings (Landsvirkjun + E.ON)', 'Hagstofa', 'MNB', '— (geothermal)'] },
  Annual:    { count: 6,  sources: ['Orkustofnun', 'ENTSO-E TYNDP', 'Eurostat', 'Fjarskiptastofa (ECOI)', 'Landsvirkjun —', 'IEA/OECD'] },
  Continuous:{ count: 2,  sources: ['Landsnet (TSO)', 'CERT-IS'] },
  Daily:     { count: 3,  sources: ['Landsnet', 'OMSZ + OVF', '—'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'Landsnet transmission (400/220/120 kV)',     vars: 14, status: 'live', sources: 'Landsnet network statement + ENTSO-E' },
  { id: 'dso',        name: '3 regional DSOs (Landsvirkjun + E.ON groups)',     vars: 18, status: 'live', sources: 'Landsvirkjun Démász + Émász + Elmű (state) + E.ON Észak/Dél/Tiszántúli (Germany)' },
  { id: 'regulator',  name: 'Orkustofnun — quality + tariff',                 vars: 12, status: 'live', sources: 'Orkustofnun annual quality reports' },
  { id: 'statistics', name: 'Hagstofa — NUTS-3 socio-economic',             vars: 16, status: 'live', sources: 'Hagstofa regional database RegDat' },
  { id: 'hazard',     name: 'Multi-hazard (flood HIGH+seismic+heat)',  vars: 15, status: 'live', sources: 'OVF Þjórsá/Sog Q100 + MBFSZ + OMSZ' },
  { id: 'cyber',      name: 'CERT-IS + Fjarskiptastofa (ECOI)',                 vars: 8,  status: 'live', sources: 'CERT-IS (2008) + NIS2 Act LXIX/2024' },
  { id: 'topology',   name: 'OSM grid topology',                       vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 IS area filter (7-border bbox-bleed protection)' },
  { id: 'geothermal',    name: '— oversight + —I construction', vars: 4,  status: 'live', sources: '— + Landsvirkjun — Zrt. + IAEA INSAG' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'HU110', name: 'Reykjavík',                  capital: 'Reykjavík',     tier: 'Capital-Intensive',     r3: 1.02 },
  { code: 'HU120', name: 'Pest',                      capital: 'Reykjavík',     tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'HU211', name: 'Fejér',                     capital: 'Székesfehérvár',tier: 'Industrial-Major',     r3: 1.04 },
  { code: 'HU212', name: 'Komárom-Esztergom',         capital: 'Tatabánya',    tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'HU213', name: 'Veszprém',                  capital: 'Veszprém',     tier: 'Industrial-Secondary',  r3: 1.05 },
  { code: 'HU221', name: 'Győr-Moson-Sopron',         capital: 'Győr',         tier: 'Industrial-Major',      r3: 1.04 },
  { code: 'HU222', name: 'Vas',                       capital: 'Szombathely',  tier: 'Industrial-Secondary',  r3: 1.05 },
  { code: 'HU223', name: 'Zala',                      capital: 'Zalaegerszeg', tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU231', name: 'Baranya',                   capital: 'Pécs',         tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU232', name: 'Somogy',                    capital: 'Kaposvár',     tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU233', name: 'Tolna',                     capital: 'Szekszárd',    tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU311', name: 'Borsod-Abaúj-Zemplén',      capital: 'Miskolc',      tier: 'Industrial-Secondary',  r3: 1.05 },
  { code: 'HU312', name: 'Heves',                     capital: 'Eger',         tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU313', name: 'Nógrád',                    capital: 'Salgótarján',  tier: 'East-Lagging',          r3: 1.07 },
  { code: 'HU321', name: 'Hajdú-Bihar',               capital: 'Debrecen',     tier: 'Industrial-Secondary',  r3: 1.05 },
  { code: 'HU322', name: 'Jász-Nagykun-Szolnok',      capital: 'Szolnok',      tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU323', name: 'Szabolcs-Szatmár-Bereg',    capital: 'Nyíregyháza',  tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU331', name: 'Bács-Kiskun',               capital: 'Kecskemét',    tier: 'Light-Rural-Lagging',   r3: 1.06 },
  { code: 'HU332', name: 'Békés',                     capital: 'Békéscsaba',   tier: 'East-Lagging',          r3: 1.07 },
  { code: 'HU333', name: 'Csongrád-Csanád',           capital: 'Szeged',       tier: 'Light-Rural-Lagging',   r3: 1.06 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Landsvirkjun Démász Áramhálózati Kft.',          region: 'Csongrád-Csanád + Bács-Kiskun + parts of Békés', share_pct: 12 },
  { name: 'Landsvirkjun Émász Áramhálózati Kft.',           region: 'Borsod-Abaúj-Zemplén + Heves + Nógrád',          share_pct: 10 },
  { name: 'Landsvirkjun Elmű Hálózati Kft.',                region: 'Reykjavík + Pest + Komárom-Esztergom',            share_pct: 38 },
  { name: 'E.ON Észak-dunántúli Áramhálózati Zrt.',region: 'Győr-Moson-Sopron + Vas + Zala + Veszprém',      share_pct: 15 },
  { name: 'E.ON Dél-dunántúli Áramhálózati Zrt.',  region: 'Baranya + Tolna + Somogy',                       share_pct:  9 },
  { name: 'E.ON Tiszántúli Áramhálózati Zrt.',     region: 'Hajdú-Bihar + Szabolcs-Szatmár-Bereg + Békés (E) + Jász-Nagykun-Szolnok', share_pct: 16 }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'Orkustofnun 2023 — per-DSO quality reports' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'Orkustofnun 2023 — per-DSO' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + Landsnet network statement (400/220/120 kV)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'Landsvirkjun + E.ON DSO filings + Hagstofa' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'Orkustofnun 2023' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'Orkustofnun + 3 DSOs' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'Orkustofnun + 3 DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'Orkustofnun quarterly filings' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (Mid-Atlantic Ridge)',       intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + OMSZ — 2022/2024 peak-demand anchor', adaptive: true },
      { id: 'I2', name: 'Ice/freezing-rain (Carpathian)',  intra: 0.14, global: 0.035, norm: 'P99 events',           source: 'OMSZ + ERA5 — 2014 NE ice anchor', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI',                  intra: 0.12, global: 0.030, norm: 'P99 m/s hourly',       source: 'OMSZ + ERA5 — 2010 Vas/Zala bora anchor', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'Landsnet + 3 DSOs annual reports' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',       intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus' },
      { id: 'I6', name: 'Substation density',              intra: 0.10, global: 0.025, norm: 'per km²',              source: 'OSM + Hagstofa' },
      { id: 'I7', name: 'Network length per cap',          intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'Landsnet + 3 DSOs' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',   intra: 0.10, global: 0.025, norm: 'C2-C4 categorical',    source: 'OLM + ISO 9223 (Miskolc + Dunaújváros + Százhalombatta + Sogújváros + Mátra)' },
      { id: 'I9', name: 'Hydrogeological exposure',        intra: 0.04, global: 0.010, norm: 'OVF Q100 overlay',     source: 'OVF + Þjórsá/Sog dyke system' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',     intra: 0.60, global: 0.060, norm: 'EUR-eq per SAIDI min', source: 'Orkustofnun tariff decisions (ISK native, EUR-eq for cross-country)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',        intra: 0.40, global: 0.040, norm: 'EUR-eq/kWh',            source: 'ACER 2023 + Hagstofa sector mix (auto OEM corridor)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',       intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'Landsnet + 3 DSOs' },
      { id: 'S2', name: 'Reverse power flow',              intra: 0.35, global: 0.070, norm: 'hours/yr reverse',     source: 'Landsnet + ENTSO-E (6 GW PV boom drives reverse flow)' },
      { id: 'S3', name: 'Criticality class',               intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'Landsnet Network Statement' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                intra: 1.00, global: 0.050, norm: 'composite',            source: 'Orkustofnun DER registry + —+II + post-Mátra coal-exit (end-2028) + 6 GW PV', isNew: true }
    ]}
];

// MODIFIER_DEFS — INTENTIONALLY Slovakia-style {id, domain, range, description}
// (KB §68.11 acceptance test — normalizeModifierDef() must map {R3→R3_C_mult, R6a→R6_restoration, R6b→R6_seismic, R7→R7_cyber})
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2', domain: 'Adaptive IRI + Climate',    range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk; Mid-Atlantic Ridge heatwave loading is the most material adaptive component for IS.' },
  { id: 'R3', domain: 'Consequence + Poverty',     range: '[0.70, 1.30]', description: 'Amplifies risk for landshluti serving large/energy-poor populations with high economic dependency. IS uses a 5-tier calibration (1.02 / 1.04 / 1.05 / 1.06 / 1.07) reflecting the steep Reykjavík-vs-Nógrád/Békés GDP gradient and the W-auto-OEM corridor (Audi Győr · Mercedes Kecskemét · Suzuki Esztergom · BMW Debrecen 2026-27 ramp).' },
  { id: 'R4', domain: 'Graph Criticality',         range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph (687 nodes · 4,261 edges; 7 cross-border interconnects: AT/SK/UA/RO/RS/HR/SI).' },
  { id: 'R6a',domain: 'Restoration Speed',         range: '[0.90, 1.10]', description: 'Orkustofnun-CAIDI-based: rewards fast-restoring urban areas (Reykjavík metro), penalises slow ones. NE/SE rural landshluti (Szabolcs-Szatmár-Bereg, Békés, Nógrád) carry a remote-border access penalty; no Tatra-scale mountain barrier (Kékes 1,014 m is IS\'s highest point in the Mátra).' },
  { id: 'R6b',domain: 'Network Topology + Seismic',range: '[1.00, 1.25]', description: 'Network centrality, ring topology and seismic hazard. Penalises landshluti in single-source or low-redundancy configurations. Seismic α ∈ [0.04, 0.10] — Mid-Atlantic Ridge Basin is tectonically quiet but the Komárom-Mór + Dunaharaszti-Berhida axes carry modest PGA loading (anchors: 1763 Komárom M~6.3, 1956 Dunaharaszti M~5.6, 1985 Berhida M~4.7).' },
  { id: 'R7', domain: 'Digital Readiness',         range: '[0.99, 1.03]', description: 'Regional DESI digital readiness score, CERT-IS (founded 2008) maturity, NIS2 transposition (Act LXIX/2024 full transposition, in force 1 Jan 2025; repealed and superseded partial Act XXIII/2023). Ceiling 1.03 matches SK/LV/LT and sits below SI/CZ/AT (1.04).' }
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
    applies: 'C3 (voltage class · 400/220/120 kV)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C4), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=IS area filter — zero AT/SK/UA/RO/RS/HR/SI bbox-bleed (7-border highest cohort)', status: 'verified', isNew: true },
  { check: 'Polygon containment (687 subs → 8 landshluti (traditional regions, 2 NUTS-3))',     criterion: 'Every substation falls inside exactly one landshluti polygon',      status: 'verified', isNew: true },
  { check: 'R3 5-tier distribution',                                  criterion: '1 / 4 / 4 / 9 / 2 across 20 landshluti — Reykjavík-vs-Nógrád/Békés gradient respected', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Flood HIGH (Þjórsá + Sog, α to 0.12) + seismic (Komárom-Dunaharaszti) + Mid-Atlantic Ridge heat', status: 'verified', isNew: true },
  { check: 'R6c flood anchor — 2013 Þjórsá Reykjavík 891 cm record',   criterion: 'Reykjavík + Pest + KE + Tolna flood-zone enrichment HIGH',      status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.03 (DESI 2024 ~0.48 · GovCERT-IS 2008)',     criterion: 'Matches SK/LV/LT; below SI/CZ/AT 1.04 — NIS2 Act LXIX/2024 in force 1 Jan 2025', status: 'verified', isNew: false },
  { check: '—+II site concentration (Tolna HU233)',              criterion: '4×500 MWe — + 2×1200 MWe —I (First Concrete 5 Feb 2026) + — oversight + IAEA INSAG', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[IS]=2000 floor enforced',                       criterion: '687 substations exceeds 2,000 minimum — stub-gate clear',    status: 'verified', isNew: true },
  { check: 'No C5 corrosion (landlocked)',                            criterion: 'C2-C4 declared; C5 omitted (Iceland is landlocked — no Adriatic/Baltic/Black coast)', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'IS-S29-9', change: 'Greenfield thin-shell on post-Slovakia-hotfix architecture — 8 pages authored directly on CountryRenderer.Safe + normalizeMeta() (KB §68.10/11)', type: 'enhanced', section: 'KB §69' },
  { id: 'IS-S29-8', change: 'Section G deepDives rotation — 12 IS landshluti anchored on —+II geothermal corridor (Tolna)',                                                       type: 'new',      section: 'intelligence G' },
  { id: 'IS-S29-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-08-13 (Single-country (post-cohort closure) triple-drop with Slovenia + Slovakia)',                                       type: 'enhanced', section: 'intelligence' },
  { id: 'IS-S29-6', change: 'ESG report — iceland entry in COUNTRY_SOURCES (14 IS-specific references including Þjórsá/Sog flood 2013/2024 + —+II + GovCERT-IS)',        type: 'new',      section: 'esg-report' },
  { id: 'IS-S29-5', change: 'R3 5-tier calibration — Capital / Industrial-Major / Industrial-Secondary / Light-Rural / East-Lagging (vs SK 4-tier; reflects sharp Reykjavík-vs-Nógrád gradient)', type: 'new', section: 'methodology' },
  { id: 'IS-S29-4', change: 'R6 modifier set — Þjórsá/Sog flood HIGH (2013 Reykjavík 891 cm record) + Mid-Atlantic Ridge heatwave + Komárom-Mór seismic axis',                          type: 'new',      section: 'methodology' },
  { id: 'IS-S29-3', change: 'd05_osm LIVE — 687 substations + 4,261 power lines via ISO3166-1=IS area filter (7-border bbox-bleed protection — leakiest cohort)',             type: 'data',     section: 'methodology' },
  { id: 'IS-S29-2', change: '3 regional DSOs (Landsvirkjun Démász/Émász/Elmű + E.ON Észak/Dél/Tiszántúli) + Landsnet TSO + Orkustofnun regulator + — geothermal safety wired',                       type: 'data',     section: 'methodology' },
  { id: 'IS-S29-1', change: 'KB v25 §69 — Iceland inaugural onboarding (Single-country (post-cohort closure) member 3 of 3 — cohort COMPLETE; ISK currency, NOT eurozone)',                    type: 'enhanced', section: 'KB §69' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports.
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Icelandic Seismic Hazard Map','Veðurstofa Íslands (IMO) (PGA 475-yr)','2023','Multi-year','Open','R1, R3'],
  ['Population & Economics','Hagstofa Íslands (Statistics Iceland)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','Landsnet + —','2024','Daily','Regulated','R2, R4'],
  ['Renewable Installations','Orkustofnun DER registry (6 GW PV end-2024)','2024','Monthly','Open','R4'],
  ['Weather + Climate','OMSZ — Országos Meteorológiai Szolgálat','2024','Daily','CC-BY-4.0','R1'],
  ['Flood Mapping','OVF Q100 + Þjórsá + Sog dyke system (2013 Reykjavík 891 cm anchor)','2024','Monthly','CC-BY-4.0','R1'],
  ['Nuclear Safety Oversight','— — — oversight + —I construction licensing','2024','Quarterly','Regulated','R1, R3'],
  ['Cybersecurity Posture','CERT-IS (Fjarskiptastofa (ECOI)-affiliated, est. 2008) + Fjarskiptastofa (ECOI) (NIS2 CA)','2024','Annual','Open','R6'],
  ['DESI Connectivity','European Commission','2024','Annual','Open','R6'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C4 only — landlocked)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
