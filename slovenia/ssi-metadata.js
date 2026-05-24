// Slovenia SSI v4.0.2 metadata — KB §64 · post-§57 normalization
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (inaugural) · first refresh 2026-07-09 (CEE-South cohort)

window.SSIMetadata = {
  country: 'Slovenia',
  country_code: 'SI',
  country_iso3: 'SVN',
  flag: '\u{1F1F8}\u{1F1EE}',  // 🇸🇮
  cohort: 'CEE-South-2026',
  edition: 'Edition 01',
  first_refresh: '2026-07-09',
  engine_version: '4.0.2',
  kb_version: 'v25',
  bpg_version: 'v1.24',
  labels: {
    country_en: 'Slovenia',
    country_local: 'Slovenija',
    capital: 'Ljubljana',
    capital_local: 'Ljubljana',
    region_unit: 'NUTS-3 statistical region',
    region_unit_local: 'statistična regija',
    tso: 'ELES (Elektro-Slovenija)',
    regulator: 'AGEN-RS (Agencija za energijo)',
    statistics_office: 'SURS (Statistični urad RS)',
    nem: 'Borzen / BSP SouthPool',
    bidding_zone: '10YSI-ELES-----O'
  },
  stats: { sources: 18, variables: 92, components: 6, modifiers: 5 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_restoration', 'R6_seismic', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '3-tier (Capital-Intensive / Industrial-Major / Light-Rural)',
    r6_anchors: '2023 Savinja floods (€10B) · 1998 Bovec M5.6 · 2014 ice storm · Krško NPP zone seismic',
    r7_ceiling: 1.04
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Post-declaration enrichment ──
window.SSI_METADATA.COMPONENTS = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · AGEN-RS quality reports · ELES network statement' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · DSO quarterly filings · 5 Elektro regions' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · ELES asset register · 400/220/110 kV inventory' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'SURS NUTS-3 GDP · BS regional accounts · business demography' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'SURS energy-poverty · elderly share · vulnerable populations' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'AGEN-RS DER registry · Borzen renewables · EV uptake' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_eles',        name: 'ELES — Elektro-Slovenija (TSO)',        freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4',      sources: 'eles.si network statement + ENTSO-E TP' },
  { id: 'd02_agen_rs',     name: 'AGEN-RS — Agencija za energijo',         freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1',        sources: 'agen-rs.si quality-of-supply + tariff' },
  { id: 'd02b_dso',        name: '5 Elektro DSOs (Lj/Mb/Ce/Pr/Gr)',        freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3',        sources: 'elektro-ljubljana / maribor / celje / primorska / gorenjska' },
  { id: 'd03_arso_seismic',name: 'ARSO + ZAG-EQS — Seismology',           freq: 'Continuous', status: 'live', vars: 4,  feeds: 'R6_seismic',            sources: 'arso.gov.si seismology + ZAG-EQS PGA 475-yr' },
  { id: 'd03b_drsv',       name: 'DRSV — Direkcija za vode (floods)',     freq: 'Monthly',    status: 'live', vars: 6,  feeds: 'R6c_flood',              sources: 'gov.si/drsv Q100 maps + 2023 floods overlay' },
  { id: 'd04_surs',        name: 'SURS — Statistični urad RS',             freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3',        sources: 'surs.si NUTS-3 demographics + regional GDP' },
  { id: 'd04b_bs',         name: 'Banka Slovenije — central bank',        freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2',                 sources: 'bsi.si national accounts + financial stability' },
  { id: 'd05_osm',         name: 'OSM Overpass — grid topology',          freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4',           sources: 'overpass-api.de power=substation/line · ISO3166 SI' },
  { id: 'd06_arso_met',    name: 'ARSO — Meteorology + climate',          freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R6_storm,R5_corrosion', sources: 'arso.gov.si meteo + bora wind + ice storm' },
  { id: 'd07_copernicus',  name: 'Copernicus ERA5 + CMIP6',               freq: 'Monthly',    status: 'live', vars: 4,  feeds: 'R6_climate',             sources: 'cds.climate.copernicus.eu SSP2-4.5' },
  { id: 'd08_ursjv',       name: 'URSJV — Nuclear safety (Krško)',        freq: 'Quarterly',  status: 'live', vars: 3,  feeds: 'R6_seismic,I3',          sources: 'ursjv.gov.si Krško NPP oversight' },
  { id: 'd09_si_cert',     name: 'SI-CERT — National CERT (1995)',         freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber',               sources: 'cert.si incident database + NIS2 reporting' },
  { id: 'd10_entsoe',      name: 'ENTSO-E TYNDP + Transparency',           freq: 'Annual',     status: 'live', vars: 6,  feeds: 'I1,I2,T1',              sources: 'tyndp.entsoe.eu + transparency.entsoe.eu' },
  { id: 'd11_eurostat',    name: 'Eurostat — EU-27 benchmarks',            freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1',              sources: 'ec.europa.eu/eurostat NUTS-3 + energy' },
  { id: 'd12_nek_krsko',   name: 'NEK Krško — SI/HR joint operator',       freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'I1,I3,R6_seismic',       sources: 'nek.si annual + URSJV PSR (2043 life-extension)' },
  { id: 'd13_hse',         name: 'HSE — Hydro + lignite generation',       freq: 'Annual',     status: 'live', vars: 5,  feeds: 'I1,T1',                  sources: 'hse.si annual reports · Drava+Soča+Sava cascades + TEŠ-6' },
  { id: 'd14_gen_energija',name: 'GEN Energija — Krško 50% + Brestanica',  freq: 'Annual',     status: 'live', vars: 3,  feeds: 'I1,T1',                  sources: 'gen-energija.si annual + JEK 2 planning' },
  { id: 'd15_iea_oecd',    name: 'IEA + OECD — energy benchmarks',         freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1',                  sources: 'iea.org + oecd.org energy statistics' }
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'DRSV (floods)', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 5,  sources: ['DSO filings (5 Elektros)', 'SURS', 'Banka Slovenije', 'URSJV (Krško)', 'NEK Krško'] },
  Annual:    { count: 7,  sources: ['AGEN-RS', 'ENTSO-E TYNDP', 'Eurostat', 'HSE', 'GEN Energija', 'IEA/OECD'] },
  Continuous:{ count: 3,  sources: ['ELES (TSO)', 'ARSO (seismic+met)', 'SI-CERT'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'ELES transmission (400/220/110 kV)', vars: 14, status: 'live', sources: 'ELES TP + ENTSO-E' },
  { id: 'dso',        name: '5 regional Elektro DSOs (35/20/10 kV)', vars: 18, status: 'live', sources: '5 Elektros + SODO holding' },
  { id: 'regulator',  name: 'AGEN-RS — quality + tariff',            vars: 12, status: 'live', sources: 'AGEN-RS annual reports' },
  { id: 'statistics', name: 'SURS — NUTS-3 socio-economic',           vars: 16, status: 'live', sources: 'SURS regional accounts' },
  { id: 'hazard',     name: 'Multi-hazard (seismic+flood+storm)',     vars: 15, status: 'live', sources: 'ARSO + ZAG-EQS + DRSV' },
  { id: 'cyber',      name: 'SI-CERT + URSIV',                        vars: 5,  status: 'live', sources: 'SI-CERT incidents + NIS2' },
  { id: 'topology',   name: 'OSM grid topology',                       vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 area' },
  { id: 'nuclear',    name: 'Krško NPP oversight',                     vars: 4,  status: 'live', sources: 'URSJV + NEK + GEN Energija' }
];

window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'SI031', name: 'Pomurska',              capital: 'Murska Sobota',  tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI032', name: 'Podravska',             capital: 'Maribor',         tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI033', name: 'Koroška',               capital: 'Slovenj Gradec',  tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI034', name: 'Savinjska',             capital: 'Celje',           tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI035', name: 'Zasavska',              capital: 'Trbovlje',        tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI036', name: 'Posavska',              capital: 'Krško',           tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI037', name: 'Jugovzhodna Slovenija', capital: 'Novo mesto',      tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI038', name: 'Primorsko-notranjska',  capital: 'Postojna',        tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI041', name: 'Osrednjeslovenska',     capital: 'Ljubljana',       tier: 'Capital-Intensive',  r3: 1.02 },
  { code: 'SI042', name: 'Gorenjska',             capital: 'Kranj',           tier: 'Industrial-Major',   r3: 1.04 },
  { code: 'SI043', name: 'Goriška',               capital: 'Nova Gorica',     tier: 'Light-Rural',        r3: 1.06 },
  { code: 'SI044', name: 'Obalno-kraška',         capital: 'Koper',           tier: 'Industrial-Major',   r3: 1.04 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Elektro Ljubljana',   region: 'Osrednjeslovenska + Gorenjska/Posavska/JV', share_pct: 33 },
  { name: 'Elektro Maribor',     region: 'Podravska + Pomurska + Koroška',            share_pct: 25 },
  { name: 'Elektro Celje',       region: 'Savinjska + Zasavska + Posavska',           share_pct: 20 },
  { name: 'Elektro Primorska',   region: 'Goriška + Obalno-kraška + Primorsko-notr.', share_pct: 14 },
  { name: 'Elektro Gorenjska',   region: 'Gorenjska (Kranj-Triglav)',                  share_pct: 8  }
];
