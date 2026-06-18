// Hungary SSI v4.0.2 metadata — KB §69 · greenfield thin-shell on post-Slovakia-hotfix architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (inaugural) · first refresh 2026-07-09 (CEE-South-2026 cohort triple-drop with Slovenia + Slovakia)
// Architecture acceptance test for KB §68.10 (CountryRenderer.Safe) + §68.11 (normalizeMeta()):
//   COMPONENTS_INDEX intentionally ships the documentation-rich Slovakia shape {code, name, ceiling, drivers}
//   MODIFIER_DEFS    intentionally ships the documentation-rich Slovakia shape {id, domain, range, description}
// normalizeMeta() in country-renderer.js is expected to alias these to the canonical {key, label, w, color}
// and {key, label, domain, range, description} forms with no per-country defensive patches required.

window.SSI_COUNTRY = 'hungary';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Hungary',
  COUNTRY: 'Hungary',
  country_code: 'HU',
  country_iso3: 'HUN',
  flag: '\u{1F1ED}\u{1F1FA}',  // 🇭🇺
  FLAG: '\u{1F1ED}\u{1F1FA}',
  cohort: 'CEE-South-2026',
  edition: 'Edition 01',
  first_refresh: '2026-07-09',
  engine_version: '4.0.2',
  kb_version: 'v25',
  bpg_version: 'v1.26',
  currency: 'HUF',
  currency_symbol: 'Ft',
  currency_position: 'after',
  labels: {
    country_en: 'Hungary',
    country_local: 'Magyarország',
    capital: 'Budapest',
    capital_local: 'Budapest',
    region_unit: 'NUTS-3 megye',
    region_unit_local: 'megye',
    tso: 'MAVIR ZRt. (Magyar Villamosenergia-ipari Átviteli Rendszerirányító)',
    regulator: 'MEKH (Magyar Energetikai és Közmű-szabályozási Hivatal)',
    statistics_office: 'KSH (Központi Statisztikai Hivatal)',
    nem: 'HUPX Zrt. (Hungarian Power Exchange) · KELER CCP settlement',
    bidding_zone: '10YHU-MAVIR----U'
  },
  stats: { sources: 18, variables: 95, components: 6, modifiers: 5 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '5-tier (Capital-Intensive / Industrial-Major / Industrial-Secondary / Light-Rural-Lagging / East-Lagging)',
    r6_anchors: '2013 Danube flood (Budapest 891 cm record) · 1956 Tisza flood (Tiszadob-Tiszafüred) · 1956 Dunaharaszti M~5.6 quake · 2024 Sep Danube flood (Budapest ~833 cm) · Pannonian heatwaves 2022/2024',
    r7_ceiling: 1.03
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — INTENTIONALLY Slovakia-style {code, name, ceiling, drivers}
// (KB §68.10 acceptance test — normalizeMeta() must alias this to {key, label, w, color})
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · MEKH quality reports · MAVIR network statement · Budapest metro ~26 min vs E.ON Tiszántúli rural ~115 min split' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · MVM + E.ON quarterly filings · 6-DSO heritage portfolio (MVM ~60% / E.ON ~40%)' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · MAVIR asset register · 400/220/120 kV inventory (HU 120 kV legacy backbone vs CE 110 kV) + Paks I site + Paks II construction footprint' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'KSH NUTS-3 GDP · MNB regional accounts · automotive OEM concentration (Audi Győr · Mercedes Kecskemét · Suzuki Esztergom · BMW Debrecen ramp-up 2026-27)' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'KSH energy-poverty · Nógrád + Békés unemployment · Hungarian-minority diaspora in RO/SK/UA/RS border megyék (Csongrád-Csanád, Békés, Szabolcs-Szatmár-Bereg)' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'MEKH DER registry · Paks I+II nuclear ramp (4×500 + 2×1200 MWe target) · post-Mátra coal exit (end-2028 · CCGT 500-650 MW replacement) · 6 GW PV boom doubled since 2022' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_mavir',        name: 'MAVIR — Magyar Villamosenergia-ipari Átviteli Rendszerirányító (TSO)', freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'mavir.hu network statement + ENTSO-E TP' },
  { id: 'd02_mekh',         name: 'MEKH — Magyar Energetikai és Közmű-szabályozási Hivatal',              freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1', sources: 'mekh.hu quality-of-supply + tariff decisions' },
  { id: 'd02b_dso',         name: '6 regional DSOs (MVM Démász/Émász/Elmű + E.ON Észak/Dél/Tiszántúli)',  freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'MVM Group + E.ON Hungary quarterly filings' },
  { id: 'd03_omsz',         name: 'OMSZ — Országos Meteorológiai Szolgálat',                              freq: 'Daily',      status: 'live', vars: 8,  feeds: 'I1,I2,I3,R6_climate', sources: 'met.hu meteo + ECMWF mirror' },
  { id: 'd03b_ovf',         name: 'OVF — Országos Vízügyi Főigazgatóság (Hungarian Water Authority)',     freq: 'Daily',      status: 'live', vars: 6,  feeds: 'R6c_flood', sources: 'ovf.hu Danube + Tisza Q100 + dyke status + river gauges' },
  { id: 'd03c_mbfsz',       name: 'MBFSZ + MTA EPSS — Bányászati és Földtani Szolgálat / seismic',        freq: 'Multi-year', status: 'live', vars: 4,  feeds: 'R6_seismic', sources: 'mbfsz.gov.hu PGA 475-yr + MTA EPSS catalogue (Komárom 1763, Dunaharaszti 1956 anchors)' },
  { id: 'd04_ksh',          name: 'KSH — Központi Statisztikai Hivatal',                                  freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'ksh.hu NUTS-3 RegDat + települések LAU-2 + járások LAU-1' },
  { id: 'd04b_mnb',         name: 'MNB — Magyar Nemzeti Bank (central bank · ESCB non-€)',                freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'mnb.hu national accounts + financial stability' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=HU area filter)',              freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line · ISO3166 HU' },
  { id: 'd06_aqi',          name: 'OMSZ + OLM — Hungarian Air Quality Network (ISO 9223 corrosion)',      freq: 'Monthly',    status: 'live', vars: 5,  feeds: 'R5_corrosion,I8', sources: 'OLM PM2.5/NO₂ + ISO 9223 C2-C4 (no C5 — landlocked)' },
  { id: "CDS", name: "Copernicus CDS / ERA5-Land", url: "cds.climate.copernicus.eu", freq: "Annual", res: "0.1° (~11 km, ERA5-Land + daily-stats)", vars: 5, category: "Climate", feeds: "R2 Δ_climate (t_mean_c, heat_days, ice_days at 0.1° land grid)", registration: true },
  { id: 'd08_oah',          name: 'OAH — Országos Atomenergia Hivatal (nuclear safety)',                  freq: 'Quarterly',  status: 'live', vars: 5,  feeds: 'R6_seismic,I3,I4', sources: 'oah.hu Paks I oversight + Paks II construction licensing + IAEA INSAG' },
  { id: 'd09_govcert_hu',   name: 'GovCERT-Hungary (National Cyber Defence Institute, SZTFH lineage)',    freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber', sources: 'govcert.hu incident database + CERT-Hungary 2008 baseline' },
  { id: 'd10_sztfh',        name: 'SZTFH — Szabályozott Tevékenységek Felügyeleti Hatósága (NIS2 CA)',    freq: 'Annual',     status: 'live', vars: 3,  feeds: 'R7_cyber', sources: 'sztfh.hu NIS2 competent authority (Act LXIX/2024 in force 1 Jan 2025; repealed Act XXIII/2023)' },
  { id: 'd11_entsoe',       name: 'ENTSO-E TYNDP + Transparency Platform',                                freq: 'Annual',     status: 'live', vars: 6,  feeds: 'I1,I2,T1', sources: 'tyndp.entsoe.eu + transparency.entsoe.eu' },
  { id: 'd12_eurostat',     name: 'Eurostat — EU-27 NUTS-3 benchmarks',                                   freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1', sources: 'ec.europa.eu/eurostat NUTS-3 regional + energy + DESI' },
  { id: 'd13_mvm_paks',     name: 'MVM Paksi Atomerőmű (Paks I) + Paks II Atomerőmű Zrt.',                freq: 'Annual',     status: 'live', vars: 5,  feeds: 'I1,I3,R6_seismic', sources: 'paksnuclearpowerplant.com Paks I 4×500 MWe + Paks II Unit 5 First Concrete 5 Feb 2026' },
  { id: 'd14_hupx',         name: 'HUPX — Hungarian Power Exchange (NEMO) + CORE FB-MC',                  freq: 'Daily',      status: 'live', vars: 4,  feeds: 'T1,E1', sources: 'hupx.hu market coupling + SDAC + SIDC + CORE FB-MC since 8 Jun 2022' },
  { id: 'd15_iea_oecd',     name: 'IEA + OECD — energy benchmarks (HU joined OECD 7 May 1996, 24th member)', freq: 'Annual',  status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics' },
    { id: "GEM", name: "GEM Global Seismic Hazard Map 2023.1", url: "globalquakemodel.org", freq: "Static", res: "0.05° (~5.5 km, rock-site PGA 475-yr)", vars: 1, category: "Hazard", feeds: "R6a seismic PGA, substation-level overlay (CC BY-NC-SA 4.0)" },
    { id: "Eurostat-NUTS3", name: "Eurostat NUTS-3 Regional Statistics", url: "ec.europa.eu/eurostat", freq: "Annual", res: "NUTS-3 (province / NUTS-2 unemployment)", vars: 5, category: "Socio-Econ", feeds: "R2 GDP/cap, unemp, elderly%, ep_rate, migration (CC BY 4.0)" },
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'OMSZ + OLM (air quality)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 4,  sources: ['DSO filings (MVM + E.ON)', 'KSH', 'MNB', 'OAH (nuclear)'] },
  Annual:    { count: 6,  sources: ['MEKH', 'ENTSO-E TYNDP', 'Eurostat', 'SZTFH', 'MVM Paks I + Paks II', 'IEA/OECD'] },
  Continuous:{ count: 2,  sources: ['MAVIR (TSO)', 'GovCERT-Hungary'] },
  Daily:     { count: 3,  sources: ['MAVIR', 'OMSZ + OVF', 'HUPX'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'MAVIR transmission (400/220/120 kV)',     vars: 14, status: 'live', sources: 'MAVIR network statement + ENTSO-E' },
  { id: 'dso',        name: '6 regional DSOs (MVM + E.ON groups)',     vars: 18, status: 'live', sources: 'MVM Démász + Émász + Elmű (state) + E.ON Észak/Dél/Tiszántúli (Germany)' },
  { id: 'regulator',  name: 'MEKH — quality + tariff',                 vars: 12, status: 'live', sources: 'MEKH annual quality reports' },
  { id: 'statistics', name: 'KSH — NUTS-3 socio-economic',             vars: 16, status: 'live', sources: 'KSH regional database RegDat' },
  { id: 'hazard',     name: 'Multi-hazard (flood HIGH+seismic+heat)',  vars: 15, status: 'live', sources: 'OVF Danube/Tisza Q100 + MBFSZ + OMSZ' },
  { id: 'cyber',      name: 'GovCERT-Hungary + SZTFH',                 vars: 8,  status: 'live', sources: 'GovCERT-Hungary (2008) + NIS2 Act LXIX/2024' },
  { id: 'topology',   name: 'OSM grid topology',                       vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 HU area filter (7-border bbox-bleed protection)' },
  { id: 'nuclear',    name: 'Paks I oversight + Paks II construction', vars: 4,  status: 'live', sources: 'OAH + MVM Paks I + Paks II Zrt. + IAEA INSAG' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'HU110', name: 'Budapest',                  capital: 'Budapest',     tier: 'Capital-Intensive',     r3: 1.02 },
  { code: 'HU120', name: 'Pest',                      capital: 'Budapest',     tier: 'Industrial-Major',      r3: 1.04 },
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
  { name: 'MVM Démász Áramhálózati Kft.',          region: 'Csongrád-Csanád + Bács-Kiskun + parts of Békés', share_pct: 12 },
  { name: 'MVM Émász Áramhálózati Kft.',           region: 'Borsod-Abaúj-Zemplén + Heves + Nógrád',          share_pct: 10 },
  { name: 'MVM Elmű Hálózati Kft.',                region: 'Budapest + Pest + Komárom-Esztergom',            share_pct: 38 },
  { name: 'E.ON Észak-dunántúli Áramhálózati Zrt.',region: 'Győr-Moson-Sopron + Vas + Zala + Veszprém',      share_pct: 15 },
  { name: 'E.ON Dél-dunántúli Áramhálózati Zrt.',  region: 'Baranya + Tolna + Somogy',                       share_pct:  9 },
  { name: 'E.ON Tiszántúli Áramhálózati Zrt.',     region: 'Hajdú-Bihar + Szabolcs-Szatmár-Bereg + Békés (E) + Jász-Nagykun-Szolnok', share_pct: 16 }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'MEKH 2023 — per-DSO quality reports' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'MEKH 2023 — per-DSO' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + MAVIR network statement (400/220/120 kV)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'MVM + E.ON DSO filings + KSH' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'MEKH 2023' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'MEKH + 6 DSOs' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'MEKH + 6 DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'MEKH quarterly filings' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (Pannonian)',       intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + OMSZ — 2022/2024 peak-demand anchor', adaptive: true },
      { id: 'I2', name: 'Ice/freezing-rain (Carpathian)',  intra: 0.14, global: 0.035, norm: 'P99 events',           source: 'OMSZ + ERA5 — 2014 NE ice anchor', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI',                  intra: 0.12, global: 0.030, norm: 'P99 m/s hourly',       source: 'OMSZ + ERA5 — 2010 Vas/Zala bora anchor', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'MAVIR + 6 DSOs annual reports' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',       intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus' },
      { id: 'I6', name: 'Substation density',              intra: 0.10, global: 0.025, norm: 'per km²',              source: 'OSM + KSH' },
      { id: 'I7', name: 'Network length per cap',          intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'MAVIR + 6 DSOs' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',   intra: 0.10, global: 0.025, norm: 'C2-C4 categorical',    source: 'OLM + ISO 9223 (Miskolc + Dunaújváros + Százhalombatta + Tiszaújváros + Mátra)' },
      { id: 'I9', name: 'Hydrogeological exposure',        intra: 0.04, global: 0.010, norm: 'OVF Q100 overlay',     source: 'OVF + Danube/Tisza dyke system' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',     intra: 0.60, global: 0.060, norm: 'EUR-eq per SAIDI min', source: 'MEKH tariff decisions (HUF native, EUR-eq for cross-country)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',        intra: 0.40, global: 0.040, norm: 'EUR-eq/kWh',            source: 'ACER 2023 + KSH sector mix (auto OEM corridor)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',       intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'MAVIR + 6 DSOs' },
      { id: 'S2', name: 'Reverse power flow',              intra: 0.35, global: 0.070, norm: 'hours/yr reverse',     source: 'MAVIR + ENTSO-E (6 GW PV boom drives reverse flow)' },
      { id: 'S3', name: 'Criticality class',               intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'MAVIR Network Statement' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                intra: 1.00, global: 0.050, norm: 'composite',            source: 'MEKH DER registry + Paks I+II + post-Mátra coal-exit (end-2028) + 6 GW PV', isNew: true }
    ]}
];

// MODIFIER_DEFS — INTENTIONALLY Slovakia-style {id, domain, range, description}
// (KB §68.11 acceptance test — normalizeModifierDef() must map {R3→R3_C_mult, R6a→R6_restoration, R6b→R6_seismic, R7→R7_cyber})
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2', domain: 'Adaptive IRI + Climate',    range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk; Pannonian heatwave loading is the most material adaptive component for HU.' },
  { id: 'R3', domain: 'Consequence + Poverty',     range: '[0.70, 1.30]', description: 'Amplifies risk for megyék serving large/energy-poor populations with high economic dependency. HU uses a 5-tier calibration (1.02 / 1.04 / 1.05 / 1.06 / 1.07) reflecting the steep Budapest-vs-Nógrád/Békés GDP gradient and the W-auto-OEM corridor (Audi Győr · Mercedes Kecskemét · Suzuki Esztergom · BMW Debrecen 2026-27 ramp).' },
  { id: 'R4', domain: 'Graph Criticality',         range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph (3,502 nodes · 4,261 edges; 7 cross-border interconnects: AT/SK/UA/RO/RS/HR/SI).' },
  { id: 'R6a',domain: 'Restoration Speed',         range: '[0.90, 1.10]', description: 'MEKH-CAIDI-based: rewards fast-restoring urban areas (Budapest metro), penalises slow ones. NE/SE rural megyék (Szabolcs-Szatmár-Bereg, Békés, Nógrád) carry a remote-border access penalty; no Tatra-scale mountain barrier (Kékes 1,014 m is HU\'s highest point in the Mátra).' },
  { id: 'R6b',domain: 'Network Topology + Seismic',range: '[1.00, 1.25]', description: 'Network centrality, ring topology and seismic hazard. Penalises megyék in single-source or low-redundancy configurations. Seismic α ∈ [0.04, 0.10] — Pannonian Basin is tectonically quiet but the Komárom-Mór + Dunaharaszti-Berhida axes carry modest PGA loading (anchors: 1763 Komárom M~6.3, 1956 Dunaharaszti M~5.6, 1985 Berhida M~4.7).' },
  { id: 'R7', domain: 'Digital Readiness',         range: '[0.99, 1.03]', description: 'Regional DESI digital readiness score, GovCERT-Hungary (founded 2008) maturity, NIS2 transposition (Act LXIX/2024 full transposition, in force 1 Jan 2025; repealed and superseded partial Act XXIII/2023). Ceiling 1.03 matches SK/LV/LT and sits below SI/CZ/AT (1.04).' }
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
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=HU area filter — zero AT/SK/UA/RO/RS/HR/SI bbox-bleed (7-border highest cohort)', status: 'verified', isNew: true },
  { check: 'Polygon containment (3,502 subs → 20 NUTS-3 megyék)',     criterion: 'Every substation falls inside exactly one megye polygon',      status: 'verified', isNew: true },
  { check: 'R3 5-tier distribution',                                  criterion: '1 / 4 / 4 / 9 / 2 across 20 megyék — Budapest-vs-Nógrád/Békés gradient respected', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Flood HIGH (Danube + Tisza, α to 0.12) + seismic (Komárom-Dunaharaszti) + Pannonian heat', status: 'verified', isNew: true },
  { check: 'R6c flood anchor — 2013 Danube Budapest 891 cm record',   criterion: 'Budapest + Pest + KE + Tolna flood-zone enrichment HIGH',      status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.03 (DESI 2024 ~0.48 · GovCERT-HU 2008)',     criterion: 'Matches SK/LV/LT; below SI/CZ/AT 1.04 — NIS2 Act LXIX/2024 in force 1 Jan 2025', status: 'verified', isNew: false },
  { check: 'Paks I+II site concentration (Tolna HU233)',              criterion: '4×500 MWe Paks I + 2×1200 MWe Paks II (First Concrete 5 Feb 2026) + OAH oversight + IAEA INSAG', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[HU]=2000 floor enforced',                       criterion: '3,502 substations exceeds 2,000 minimum — stub-gate clear',    status: 'verified', isNew: true },
  { check: 'No C5 corrosion (landlocked)',                            criterion: 'C2-C4 declared; C5 omitted (Hungary is landlocked — no Adriatic/Baltic/Black coast)', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'HU-S29-9', change: 'Greenfield thin-shell on post-Slovakia-hotfix architecture — 8 pages authored directly on CountryRenderer.Safe + normalizeMeta() (KB §68.10/11)', type: 'enhanced', section: 'KB §69' },
  { id: 'HU-S29-8', change: 'Section G deepDives rotation — 12 HU megyék anchored on Paks I+II nuclear corridor (Tolna)',                                                       type: 'new',      section: 'intelligence G' },
  { id: 'HU-S29-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-07-09 (CEE-South-2026 triple-drop with Slovenia + Slovakia)',                                       type: 'enhanced', section: 'intelligence' },
  { id: 'HU-S29-6', change: 'ESG report — hungary entry in COUNTRY_SOURCES (14 HU-specific references including Danube/Tisza flood 2013/2024 + Paks I+II + GovCERT-HU)',        type: 'new',      section: 'esg-report' },
  { id: 'HU-S29-5', change: 'R3 5-tier calibration — Capital / Industrial-Major / Industrial-Secondary / Light-Rural / East-Lagging (vs SK 4-tier; reflects sharp Budapest-vs-Nógrád gradient)', type: 'new', section: 'methodology' },
  { id: 'HU-S29-4', change: 'R6 modifier set — Danube/Tisza flood HIGH (2013 Budapest 891 cm record) + Pannonian heatwave + Komárom-Mór seismic axis',                          type: 'new',      section: 'methodology' },
  { id: 'HU-S29-3', change: 'd05_osm LIVE — 3,502 substations + 4,261 power lines via ISO3166-1=HU area filter (7-border bbox-bleed protection — leakiest cohort)',             type: 'data',     section: 'methodology' },
  { id: 'HU-S29-2', change: '6 regional DSOs (MVM Démász/Émász/Elmű + E.ON Észak/Dél/Tiszántúli) + MAVIR TSO + MEKH regulator + OAH nuclear safety wired',                       type: 'data',     section: 'methodology' },
  { id: 'HU-S29-1', change: 'KB v25 §69 — Hungary inaugural onboarding (CEE-South-2026 cohort member 3 of 3 — cohort COMPLETE; HUF currency, NOT eurozone)',                    type: 'enhanced', section: 'KB §69' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports.
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Hungarian Seismic Hazard Map','MBFSZ + MTA EPSS (PGA 475-yr)','2023','Multi-year','Open','R1, R3'],
  ['Population & Economics','KSH (Központi Statisztikai Hivatal)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','MAVIR + HUPX','2024','Daily','Regulated','R2, R4'],
  ['Renewable Installations','MEKH DER registry (6 GW PV end-2024)','2024','Monthly','Open','R4'],
  ['Weather + Climate','OMSZ — Országos Meteorológiai Szolgálat','2024','Daily','CC-BY-4.0','R1'],
  ['Flood Mapping','OVF Q100 + Danube + Tisza dyke system (2013 Budapest 891 cm anchor)','2024','Monthly','CC-BY-4.0','R1'],
  ['Nuclear Safety Oversight','OAH — Paks I oversight + Paks II construction licensing','2024','Quarterly','Regulated','R1, R3'],
  ['Cybersecurity Posture','GovCERT-Hungary (SZTFH-affiliated, est. 2008) + SZTFH (NIS2 CA)','2024','Annual','Open','R6'],
  ['DESI Connectivity','European Commission','2024','Annual','Open','R6'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C4 only — landlocked)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
