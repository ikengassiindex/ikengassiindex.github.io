// Israel SSI v4.0.2 metadata — KB §74 · greenfield thin-shell on post-S33 architecture
// Pattern C (post-D#21 codification) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Israel inaugural) · first refresh 2026-08-13 (single-country onboarding, Session 34)
// Architecture acceptance test for KB §68.10 (CountryRenderer.Safe) + §68.11 (normalizeMeta()):
//   COMPONENTS_INDEX intentionally ships the documentation-rich Slovakia shape {code, name, ceiling, drivers}
//   MODIFIER_DEFS    intentionally ships the documentation-rich Slovakia shape {id, domain, range, description}
// normalizeMeta() in country-renderer.js is expected to alias these to the canonical {key, label, w, color}
// and {key, label, domain, range, description} forms with no per-country defensive patches required.
//
// Israel-specific architectural firsts (KB §74):
//   1. R6_drought NEW α anchor (FIRST in cohort) — Negev arid + desalination-electricity nexus
//   2. R6_volcanic INACTIVE — first explicit `active: false` non-erasure precedent
//   3. Dead Sea Transform strike-slip seismic — first transform-fault primary source
//   4. R7 ceiling 1.040 (cohort-LEADING) — INCD + Unit 8200 + CERT-IL + active-conflict posture
//   5. Insular grid + active HVDC construction — third truly-insular (after IS, KR); EuroAsia 2027-2028
//   6. Hebrew-script source / Latin-only render — language_mode: 'latin_only'
//   7. is_high_threat_grid: true — cohort-FIRST flag (absorbs Oct 2023 + 2024 conflict context into R7)

window.SSI_COUNTRY = 'israel';
window.SSI_EDITION = 'Edition 01';

window.SSIMetadata = {
  country: 'Israel',
  COUNTRY: 'Israel',
  country_code: 'IL',
  country_iso3: 'ISR',
  flag: '\u{1F1EE}\u{1F1F1}',  // 🇮🇱
  FLAG: '\u{1F1EE}\u{1F1F1}',
  cohort: 'Single-country (Session 34, post-S33 D#21 codification)',
  edition: 'Edition 01',
  first_refresh: '2026-08-13',
  engine_version: '4.0.2',
  kb_version: 'v34',
  bpg_version: 'v1.33',
  currency: 'ILS',
  currency_symbol: '₪',
  currency_position: 'after',
  labels: {
    country_en: 'Israel',
    country_local: 'Israel (Yisra’el)',
    capital: 'Jerusalem',
    capital_local: 'Yerushalayim',
    region_unit: 'mehoz',
    region_unit_local: 'mehoz',
    tso: 'IEC — Israel Electric Corporation (vertically integrated state-owned TSO + dominant generator + dominant DSO; founded 1923 as Palestine Electric Company, rebranded 1961) + Noga ILITO (independent system operator since 2021)',
    regulator: 'PUA — Public Utilities Authority (Electricity), since 1996 (successor to EA)',
    statistics_office: 'CBS — Central Bureau of Statistics (Halamas)',
    nem: 'Not applicable (effectively insular grid; no NEMO; SMP wholesale market operated by Noga ILITO)',
    bidding_zone: 'IL-SMP (System Marginal Price, Noga ILITO; no ENTSO-E EIC)'
  },
  stats: { sources: 13, variables: 95, components: 6, modifiers: 7 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6a_seismic', 'R6_volcanic', 'R6_drought', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '4-tier (High-Tech-Capital 1.06 Tel Aviv / Industrial-Tech 1.05 Central+Haifa / Government-Services 1.04 Jerusalem / Periphery-Arid 1.03 Northern+Southern)',
    r6_anchors: '11 Jul 1927 Jericho earthquake Mw 6.2 (last major Dead Sea Transform event) · 1837 Galilee earthquake (last pre-instrumental northern-segment M7+; ~190-year interval near/past recurrence) · 22 Nov 1995 Aqaba (Nuweiba) Mw 7.2 (southern DST companion) · Dead Sea Transform strike-slip ~5 mm/year slip rate · R6_volcanic INACTIVE (Pliocene Golan basalts only, ~4 Mya) · R6_drought NEW anchor: 2013-2018 multi-year drought + Negev arid climate (precipitation 25-200 mm/yr) + desalination-electricity nexus (~85% municipal water desalinated, ~3.4% national electricity consumed)',
    r7_ceiling: 1.040
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — INTENTIONALLY Slovakia-style {code, name, ceiling, drivers}
// (KB §68.10 acceptance test — normalizeMeta() must alias this to {key, label, w, color})
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',      ceiling: 0.30, drivers: 'SAIDI/SAIFI · PUA quality monitoring · IEC annual reliability indicators · Dan metropolitan (Tel Aviv core) ~59 min vs Negev periphery ~241 min (4.1× metro-to-periphery gradient, steeper than most cohort countries) · IEC ~80% DSO dominance + private IPP ~20% (Dorad + OPC + Edeltech + Bazan)' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160-equivalent events · PUA quarterly continuity bulletins · IEC 161 kV main transmission backbone + 400 kV limited deployment + 22 kV / 12.6 kV distribution · Bazan refinery (Haifa) + Carmel chemical complex + Dead Sea Works (Sodom) industrial THD loads' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · IEC transmission asset register · ~4,835 km 161 kV overhead + 182 km 161 kV underground + ~1,071 km 400 kV EHV · 13 switching stations + 154 IEC substations + ~10 major power-plant switchyards (Hadera Orot Rabin, Ashkelon Rutenberg, Hagit, Tzafit, Dorad, Gezer, Alon Tavor, Eshkol)' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'CBS mehoz-level GDP + Bank of Israel national accounts · Silicon Wadi tech (Check Point, Wix, Mobileye, Mellanox) ~18% GDP cohort-LEADING · R&D intensity ~5.4% cohort-LEADING · desalination ~3.4% national electricity consumption (Sorek + Hadera + Ashkelon + Palmachim + Ashdod plants)' },
  { code: 'S', name: 'Saturation',     ceiling: 0.12, drivers: 'CBS energy-poverty + V_socio composite · Northern Arab/Druze municipalities (Nazareth, Sakhnin, Galilee) elevated · Southern Bedouin unrecognized villages elevated · Haredi neighborhoods (Bnei Brak, Beit Shemesh) elevated · Tel Aviv + Herzliya Pituach + Carmel low' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'PUA generation registry + MEI 30%-by-2030 monitoring · ~70% natural gas (Tamar + Leviathan offshore) + ~20% coal (Orot Rabin + Rutenberg, phase-out track) + ~10% renewables (solar PV-dominant; Ashalim 310 MW CSP+PV the Negev anchor) · NO hydropower, NO commercial nuclear, NO synchronous interconnect' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_iec',          name: 'IEC — Israel Electric Corporation (TSO + dominant generator + dominant DSO; state-owned ~99.8%; founded 1923 as Palestine Electric Company, rebranded 1961)', freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'iec.co.il transmission plan 2023-2030 + monthly generation bulletins + financial reports (Hebrew + English)' },
  { id: 'd01b_noga',        name: 'Noga ILITO — Israel Independent System Operator (carved out from IEC 1 Nov 2021 under June 2018 reform)',                  freq: 'Continuous', status: 'live', vars: 8,  feeds: 'I1,I3,S1,T1', sources: 'noga-iso.co.il SMP wholesale market data + dispatch + IPP procurement oversight + annual reports' },
  { id: 'd02_pua',          name: 'PUA — Public Utilities Authority (Electricity), since 1996 (independent statutory regulator; MEDREG member)',           freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,E1', sources: 'gov.il/PUA tariff resolutions + quality-of-service indicators + 2023-24 annual report' },
  { id: 'd02b_dso',         name: 'Kibbutz / moshav cooperative DSO aggregate (~10% of distribution; rural electrification co-ops carved out historically)',     freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'C1,V1,I2', sources: 'Cooperative aggregate distribution filings to PUA' },
  { id: 'd03_gsi',          name: 'GSI — Geological Survey of Israel (Seismology Division operates national seismic network)',                              freq: 'Daily',      status: 'live', vars: 10, feeds: 'I1,I2,R6a_seismic', sources: 'gsi.gov.il PGA 475-yr hazard maps + Dead Sea Transform strike-slip catalogue + 1927 Jericho + 1995 Aqaba anchors' },
  { id: 'd04_cbs',          name: 'CBS — Central Bureau of Statistics (Halamas; national statistical office, demographics + national accounts + mehoz)',   freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'cbs.gov.il end-2024 population 10,027,000 + 6 mehozot + 15 nafot regional accounts + ~250 cities/local councils' },
  { id: 'd04b_boi',         name: 'BoI — Bank of Israel (national accounts, FX ILS, macro projections)',                                                   freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'boi.org.il GDP 2024 ~$540.4B + GDP/cap ~$54,177 + R&D intensity ~5.4% OECD-leading + ILS FX ~3.6-3.8 ILS/USD' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=IL area filter; effectively insular grid)',                                     freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line/minor_line · ISO3166 IL area filter · 257 substations + lines across 6 mehozot (insular: zero synchronous interconnect)' },
  { id: 'd06_ims',          name: 'IMS — Israel Meteorological Service (under Ministry of Transport; runs ECMWF mirror + national observation network)',  freq: 'Daily',      status: 'live', vars: 8,  feeds: 'I1,I2,I3,R6_climate,R6_drought', sources: 'ims.gov.il daily synoptic + Negev arid precipitation (25-200 mm/yr) vs Galilee 600-800 mm/yr + 2013-2018 drought anchor' },
  { id: 'd07_copernicus',   name: 'Copernicus ERA5 + CMIP6 (reanalysis + climate projections)',                                                                 freq: 'Monthly',    status: 'live', vars: 4,  feeds: 'R6_climate,R6_drought', sources: 'cds.climate.copernicus.eu SSP2-4.5 · Eastern Mediterranean 30-33°N reanalysis' },
  { id: 'd09_incd_certil',  name: 'INCD — Israel National Cyber Directorate (PMO, 2017) + CERT-IL (2014, CyberSpark Beersheba) + Unit 8200 (IDF, 1952)',  freq: 'Continuous', status: 'live', vars: 8,  feeds: 'R7_cyber', sources: 'gov.il/INCD critical-infrastructure scope register + Government Resolution 3270 (Dec 2017) + Computer Law 1995 + Privacy Protection Law 1981' },
  { id: 'd10_iea_oecd',     name: 'IEA + OECD — energy benchmarks (Israel 33rd OECD member, accession 7 Sep 2010)',                                        freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics · first Middle-Eastern OECD member' },
  { id: 'd11_mei',          name: 'MEI — Ministry of Energy and Infrastructure (national energy strategy + concessions + offshore-gas regulation)',         freq: 'Annual',     status: 'live', vars: 5,  feeds: 'T1,E1', sources: 'gov.il/MEI 30%-by-2030 renewable target (May 2020 Government Decision, $22 B / NIS 80 B plan) + Tamar + Leviathan + Karish gas concessions' },
  { id: 'd12_mekorot',      name: 'Mekorot — national water utility + desalination plant electricity-demand data (NEW source for R6_drought)',             freq: 'Monthly',    status: 'live', vars: 6,  feeds: 'R6_drought,E1', sources: 'mekorot.co.il 5 major desalination plants (Sorek ~624,000 m³/day + Ashkelon + Hadera + Palmachim + Ashdod); ~3.4% national electricity for desalination' }
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'Copernicus ERA5/CMIP6', 'Mekorot (desalination demand)'] },
  Quarterly: { count: 3,  sources: ['CBS (Halamas)', 'Bank of Israel', 'Kibbutz/moshav cooperative DSO aggregate'] },
  Annual:    { count: 4,  sources: ['PUA (Public Utilities Authority)', 'IEA/OECD', 'MEI (Ministry of Energy and Infrastructure)', 'OECD Going Digital'] },
  Continuous:{ count: 2,  sources: ['Noga ILITO (SMP market)', 'INCD + CERT-IL + Unit 8200'] },
  Daily:     { count: 3,  sources: ['IEC (transmission asset operator)', 'GSI (Geological Survey of Israel)', 'IMS (Israel Meteorological Service)'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'IEC transmission (400 / 161 / 22 / 12.6 kV) — effectively insular grid',                vars: 14, status: 'live', sources: 'IEC transmission plan 2023-2030 (no ENTSO-E membership; EuroAsia HVDC IL-CY-GR planned 2027-2028)' },
  { id: 'iso',        name: 'Noga ILITO market dispatch (SMP wholesale market since 1 Nov 2021)',                          vars: 8,  status: 'live', sources: 'Noga ILITO (independent system operator; carved out from IEC under June 2018 electricity-sector reform)' },
  { id: 'dso',        name: 'IEC (~80% dominant DSO) + kibbutz/moshav cooperative aggregate (~10%) + IPP private (~20% generation)', vars: 18, status: 'live', sources: 'IEC + cooperative DSO + Dorad/OPC/Edeltech/Bazan IPP filings' },
  { id: 'regulator',  name: 'PUA — tariff + quality-of-service + reliability monitoring',                              vars: 12, status: 'live', sources: 'PUA 2023-24 annual report + tariff resolutions' },
  { id: 'statistics', name: 'CBS — 6 mehozot + 15 nafot regional accounts + demographics',                              vars: 16, status: 'live', sources: 'CBS regional accounts (end-2024 population 10,027,000)' },
  { id: 'hazard',     name: 'Multi-hazard (seismic Dead Sea Transform + drought Negev + corrosion Mediterranean + Dead Sea industrial)', vars: 15, status: 'live', sources: 'GSI seismic + IMS drought + Mediterranean coastal C3-C4 + Dead Sea ultra-saline c5_extreme NEW sub-zone' },
  { id: 'cyber',      name: 'INCD + CERT-IL + Unit 8200 (cohort-LEADING posture; R7 ceiling 1.040)',                        vars: 8,  status: 'live', sources: 'INCD (Government Resolution 3270, Dec 2017) + CERT-IL (2014, CyberSpark Beersheba) + Unit 8200 (IDF, since 1952)' },
  { id: 'topology',   name: 'OSM grid topology (ISO3166-1=IL area filter; insular grid, zero cross-border interconnect)',  vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 IL area filter (EuroAsia HVDC planned 2027-2028 will end insularity mid-cohort-lifecycle)' },
  { id: 'generation', name: 'Generation fleet — IEC + private IPP (Dorad/OPC/Edeltech/Bazan)',                          vars: 6,  status: 'live', sources: 'IEC (Hagit + Orot Rabin + Rutenberg + Gezer + Alon Tavor + Eshkol + Reading) + IPP (Dorad + Tzafit/Dalia + Bazan cogen)' },
  { id: 'water',      name: 'Mekorot desalination-electricity nexus (NEW R6_drought driver)',                                vars: 6,  status: 'live', sources: 'Mekorot 5 major desalination plants + ~85% municipal water desalinated + ~3.4% national electricity for desalination' }
];

// REGIONS — Israel's 6 mehozot (districts)
// NUTS-3 equivalent at mehoz level is the natural granularity for R3 + R6_seismic + R6_drought + R7 tiering.
// HE-* ISO codes are 3-letter convenience tags (HE-TA / HE-CE / HE-HA / HE-JE / HE-NO / HE-SO).
window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'HE-TA', name: 'Tel Aviv',  capital: 'Tel Aviv-Yafo',  tier: 'High-Tech-Capital',        r3: 1.06 },
  { code: 'HE-CE', name: 'Central',   capital: 'Ramla',          tier: 'Industrial-Tech-Logistics', r3: 1.05 },
  { code: 'HE-HA', name: 'Haifa',     capital: 'Haifa',          tier: 'Industrial-Tech-Logistics', r3: 1.05 },
  { code: 'HE-JE', name: 'Jerusalem', capital: 'Jerusalem',      tier: 'Government-Services',       r3: 1.04 },
  { code: 'HE-NO', name: 'Northern',  capital: 'Nazareth',       tier: 'Periphery-Arid-Agriculture', r3: 1.03 },
  { code: 'HE-SO', name: 'Southern',  capital: 'Beersheba',      tier: 'Periphery-Arid-Agriculture', r3: 1.03 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'IEC — direct distribution', region: 'All 6 mehozot (Northern + Haifa + Central + Tel Aviv + Jerusalem + Southern)', share_pct: 80, parent: 'State of Israel (~99.8% via Government Companies Authority)' },
  { name: 'Kibbutz / moshav cooperative aggregate', region: 'Rural Northern + Central + Southern (historic rural-electrification carve-outs)', share_pct: 10, parent: 'Cooperative (kibbutz + moshav movement)' },
  { name: 'Private IPP segment (Dorad + OPC + Edeltech + Bazan)', region: 'Generation only (no DSO franchise); Ashkelon (Dorad 840 MW CCGT) + Central (Tzafit/Dalia 835 MW CCGT) + Haifa (Bazan cogen)', share_pct: 10, parent: 'Private (Dorad Energy, Kenon Holdings/OPC, Edeltech, Oil Refineries Ltd/Bazan)' }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'PUA quality monitoring + IEC annual reliability indicators (Dan metropolitan ~59 min vs Negev periphery ~241 min, 4.1× gradient)' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'PUA + IEC distribution reliability (IEC ~80% + kibbutz/moshav cooperative aggregate ~10%)' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + IEC transmission plan (400 kV limited + 161 kV main + 22 kV / 12.6 kV distribution)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'IEC + cooperative aggregate DSO filings + CBS (end-2024 population 10,027,000)' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'PUA + IEC restoration data + IDF Home Front Command coordination during active-conflict period' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160-equivalent dip events',   intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'PUA quarterly continuity bulletins + IEC + cooperative DSO filings' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'PUA + IEC + cooperative aggregate DSO filings' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'PUA quarterly filings (Bazan refinery Haifa + Carmel chemical complex + Dead Sea Works industrial THD loads dominate Haifa + Southern profiles)' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (Mediterranean + Negev)', intra: 0.18, global: 0.045, norm: 'GDD anomaly',     source: 'Copernicus ERA5 + IMS — summer peaking ~16-17 GW at ~30-33°N + Negev khamsin heat events', adaptive: true },
      { id: 'I2', name: 'Storm IRI (Mediterranean winter)', intra: 0.14, global: 0.035, norm: 'P99 events',           source: 'IMS — winter Mediterranean cyclones + Negev flash-flood corridors', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI',                   intra: 0.12, global: 0.030, norm: 'P99 m/s hourly',       source: 'IMS wind atlas — Carmel + Golan + Judean hills + Negev highland peak gusts', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                 intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'IEC + cooperative aggregate DSO annual reports (legacy Hadera Orot Rabin coal-to-gas conversion + Ashkelon Rutenberg phase-out track)' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',        intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus (summer-peaking ~16-17 GW; 400 kV + 161 kV backbones run hot continuously during heatwave + active-conflict-period restoration cycles)' },
      { id: 'I6', name: 'Substation density',               intra: 0.10, global: 0.025, norm: 'per km²',         source: 'OSM + CBS (257 substations across 22,072 km² Green Line area + East Jerusalem + Golan)' },
      { id: 'I7', name: 'Network length per cap',           intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'IEC + cooperative DSO (~4,835 km 161 kV overhead + 182 km 161 kV underground + ~1,071 km 400 kV EHV)' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',    intra: 0.10, global: 0.025, norm: 'C2-C5 categorical',    source: 'ISO 9223 (C4 Mediterranean coast Tel Aviv + Netanya + Haifa Bay + Akko + Eilat; c5_extreme NEW sub-zone at Dead Sea industrial corridor — Dead Sea Works Sodom, ~33% salinity)' },
      { id: 'I9', name: 'Seismic + drought exposure',       intra: 0.04, global: 0.010, norm: 'PGA + drought-index overlay', source: 'GSI Dead Sea Transform strike-slip PGA + IMS Negev arid drought index (NEW R6_drought modifier driver)' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',      intra: 0.60, global: 0.060, norm: 'ILS-eq per SAIDI min', source: 'PUA tariff resolutions (ILS native, 500₪ ordering post-symbol per Hebrew convention)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',         intra: 0.40, global: 0.040, norm: 'ILS-eq/kWh',           source: 'Bank of Israel + CBS sector mix (Silicon Wadi tech ~18% GDP cohort-LEADING · Bazan refinery + Carmel chemicals + Dead Sea Works heavy industry · desalination ~3.4% national electricity)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',   intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'IEC + Noga ILITO (peak ~16-17 GW vs ~22-24 GW installed; Tamar+Leviathan offshore gas dominant)' },
      { id: 'S2', name: 'Reverse power flow',               intra: 0.35, global: 0.070, norm: 'hours/yr reverse',     source: 'IEC + Noga ILITO (insular grid; reverse flow limited to growing distributed solar PV + Ashalim CSP+PV 310 MW)' },
      { id: 'S3', name: 'Criticality class',                intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'IEC transmission plan 2023-2030 (~$45B 2030 program; EuroAsia HVDC IL-CY-GR Phase 1 1,000 MW target 2027-2028)' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                 intra: 1.00, global: 0.050, norm: 'composite',            source: 'PUA generation registry + MEI 30%-by-2030 monitoring · T_share ~10% baseline (gas ~70% + coal ~20% + renewables ~10% solar-dominant) · NO hydropower / NO commercial nuclear / NO synchronous interconnect · fast-rising trajectory toward 30% by 2030 ($22 B / NIS 80 B plan)', isNew: true }
    ]}
];

// MODIFIER_DEFS — INTENTIONALLY Slovakia-style {id, domain, range, description}
// (KB §68.11 acceptance test — normalizeModifierDef() must map IDs to canonical aliases)
// Israel-specific: R6_drought is NEW (FIRST in cohort); R6_volcanic is INACTIVE via active:false flag.
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2',  domain: 'Adaptive IRI + Climate',     range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk; at Eastern Mediterranean 30-33°N Israel’s dominant adaptive vectors are summer khamsin heat events + winter Mediterranean cyclones + Negev arid drought intensification (the latter feeding R6_drought).' },
  { id: 'R3',  domain: 'Consequence + Poverty',      range: '[0.70, 1.30]', description: 'Amplifies risk for mehozot serving large/energy-poor populations with high economic dependency. Israel uses a 4-tier calibration: High-Tech-Capital 1.06 (Tel Aviv — Silicon Wadi epicentre; Check Point + Wix + Mobileye + Mellanox/Nvidia); Industrial-Tech-Logistics 1.05 (Central Sharon Plain tech corridor + Haifa Bazan refinery / Carmel chemical complex / Yokne’am chip cluster); Government-Services 1.04 (Jerusalem — capital + Knesset + Hebrew University + Mobileye HQ + Hadassah); Periphery-Arid-Agriculture 1.03 (Northern Galilee agriculture + Migdal HaEmek tech satellite; Southern Negev + Beersheba CyberSpark + Dimona Nuclear Research + Dead Sea Works + Eilat). Moderate-upper gradient; cohort mid-upper.' },
  { id: 'R4',  domain: 'Graph Criticality',          range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph (ISO3166-1=IL area filter; 257 substations + lines). Israel is the THIRD effectively-insular country in the cohort with zero synchronous interconnect; Egypt link ~80 MW DC intermittent post-2011; Jordan link bilateral and minimal; EuroAsia HVDC IL-CY-GR Phase 1 in construction target 2027-2028 will end insularity mid-cohort-lifecycle.' },
  { id: 'R6a', domain: 'Restoration Speed',          range: '[0.90, 1.10]', description: 'PUA-CAIDI-based: rewards fast-restoring urban areas (Dan metropolitan Tel Aviv core ~59 min, cohort-good), penalises slow ones (Negev periphery ~241 min, 4.1× gradient — steeper than most cohort countries). IDF Home Front Command coordinates with IEC + Noga ILITO during active-conflict-period restoration (post-Oct 2023 + Hezbollah Nov 2023-Nov 2024 + Iran Apr 13/14 + Oct 1 2024 missile escalations).' },
  { id: 'R6a_seismic', domain: 'Network Topology + Seismic (Dead Sea Transform)', range: '[1.00, 1.25]', description: 'Network centrality + Dead Sea Transform (DST) strike-slip fault hazard — the FIRST transform-fault primary source in the cohort. DST runs north-south through the Jordan Rift Valley: Arava → Dead Sea → Jordan River → Hula Valley → into Lebanon. Slip rate ~5 mm/year; M7+ recurrence ~80-100 years on northern segments; 1837 Galilee earthquake the last pre-instrumental northern-segment M7+, the ~190-year interval near/past expected recurrence per geological models. Anchors: 11 Jul 1927 Jericho Mw 6.2 (modern instrumental; ~350-500 deaths Jerusalem + Nablus + Amman) + 22 Nov 1995 Aqaba Mw 7.2 (southern DST companion). R6a_seismic α band [0.10, 0.16]: Northern (Galilee + Hula on/near DST) + Jerusalem (close to DST + Judean Hills basement faults) highest; Tel Aviv coastal lowest.' },
  { id: 'R6_volcanic', domain: 'Volcanic Activity (INACTIVE)', range: '[1.00, 1.00]', description: 'INACTIVE — first explicit `active: false` non-erasure precedent in cohort. Israel has NO active volcanism; last activity was Pliocene basaltic eruptions in the Golan Heights (~4 Mya — Mt Hermon + Bashan basalts), geological-historical not active-hazard. R6_volcanic α = 0.00 across all 6 mehozot; modifier preserved in stack with `active: false` flag for cohort schema parity (re-uses upstream R6_volcanic engine module without code-path activation). Precedent-setting non-erasure pattern carries forward to any future cohort country lacking active volcanism.' },
  { id: 'R6_drought', domain: 'Arid Climate + Desalination-Electricity Nexus (NEW — FIRST in cohort)', range: '[1.00, 1.18]', description: 'NEW MODIFIER — first country in cohort where arid-climate drought is a primary R6 anchor coupled to electricity demand via the desalination-water-electricity nexus. Mechanism: Negev arid baseline (precipitation 25-200 mm/yr vs Galilee 600-800 mm/yr) → desalination provides ~85% of municipal water → 5 major desalination plants (Sorek, Hadera, Ashkelon, Palmachim, Ashdod) consume ~3.4% of national electricity at baseline → drought intensification (2013-2018 multi-year sequence; 2022 onward intermittent) → desalination capacity utilized more aggressively → summer peak load stress increases. R6_drought α band [0.08, 0.18]: Southern (Negev arid; Beersheba; Dimona; Mitzpe Ramon) peak 0.16-0.18; Central (coastal Sorek + Palmachim + Hadera plants) 0.12-0.14; Northern (Galilee 600-800 mm) lowest 0.08-0.10. Carry-forward to AU coastal + CL coastal + MX Pacific + ES Iberian + GR + CY.' },
  { id: 'R7',  domain: 'Digital Readiness + Active-Threat Posture', range: '[0.99, 1.040]', description: 'Israel R7 ceiling 1.040 — cohort-LEADING. Reflects (a) defensive capability: INCD (Government Resolution 3270, Dec 2017, under PMO) + Unit 8200 (IDF military signals intelligence, since 1952) + CERT-IL (2014, CyberSpark Beersheba) + ~350+ private cyber companies (~10% of global cyber industry); (b) active-threat posture: cohort-first OECD country onboarded during an active-conflict period where the grid is itself kinetic + cyber target (post-Oct 2023 Hamas + Hezbollah Nov 2023-Nov 2024 + Iran missile escalations Apr 13/14 + Oct 1 2024). is_high_threat_grid:true flag codifies active-threat posture without creating a new R6_terror modifier. Continuous-state high posture (distinct from post-event hardening). Methodological note: structural-capability (high — cohort-leading) distinguished from active-stress (high — ongoing); the demonstrated resilience under stress IS the relevant signal.' }
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
    applies: 'C3 (voltage class · 400 / 161 / 22 / 12.6 kV)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C5 + c5_extreme NEW Dead Sea sub-zone), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=IL area filter — effectively insular grid; zero synchronous interconnect (Egypt ~80 MW DC intermittent + Jordan bilateral minimal excluded as non-synchronous); EuroAsia HVDC planned 2027-2028 documented forward-only', status: 'verified', isNew: true },
  { check: 'Polygon containment (257 subs → 6 mehozot)',         criterion: 'Every substation falls inside exactly one mehoz polygon (CBS + GADM public datasets)',  status: 'verified', isNew: true },
  { check: 'R3 4-tier distribution',                                  criterion: 'Tel Aviv 1.06 (High-Tech-Capital) / Central + Haifa 1.05 (Industrial-Tech-Logistics) / Jerusalem 1.04 (Government-Services) / Northern + Southern 1.03 (Periphery-Arid-Agriculture)', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Seismic Dead Sea Transform strike-slip (NEW transform-fault primary source) + Drought Negev arid-desalination nexus (NEW — FIRST in cohort) + Volcanic INACTIVE (NEW active:false precedent) + Mediterranean coastal corrosion + Dead Sea industrial c5_extreme', status: 'verified', isNew: true },
  { check: 'R6_drought NEW α anchor',                            criterion: 'Southern Negev α 0.16-0.18 (peak; Beersheba + Dimona + Mitzpe Ramon) + Central coastal-desalination α 0.12-0.14 (Sorek + Palmachim + Hadera) + Northern Galilee α 0.08-0.10 (lowest; 600-800 mm/yr precipitation)', status: 'verified', isNew: true },
  { check: 'R6_volcanic INACTIVE flag',                               criterion: '`active: false` set across all 6 mehozot; modifier preserved in stack for schema parity; first explicit non-erasure precedent (Pliocene Golan basalts ~4 Mya only)', status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.040 (cohort-LEADING)',                       criterion: 'INCD (Dec 2017, PMO) + Unit 8200 (IDF, 1952) + CERT-IL (2014, CyberSpark Beersheba); is_high_threat_grid:true absorbs active-conflict posture (Oct 2023 + Hezbollah Nov 2023-Nov 2024 + Iran Apr/Oct 2024)', status: 'verified', isNew: false },
  { check: 'Effectively insular grid',                                criterion: 'Zero synchronous interconnect; Egypt link ~80 MW DC intermittent excluded; Jordan bilateral excluded; EuroAsia HVDC IL-CY-GR Phase 1 in construction target 2027-2028 documented forward-only; renderer handles empty cross_border_lines array as "0 MW (insular grid)"', status: 'verified', isNew: true },
  { check: 'T_share fast-rising trajectory',                          criterion: '~10% baseline (gas ~70% + coal ~20% + renewables ~10% solar-dominant) with target 30% by 2030 ($22 B / NIS 80 B plan, May 2020 Government Decision); NO hydropower / NO commercial nuclear', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[IL]=250 floor enforced',                        criterion: '257 substations exceeds 250 minimum — stub-gate clear',         status: 'verified', isNew: true },
  { check: 'C5 corrosion class restored + c5_extreme NEW',            criterion: 'C4 Mediterranean coast (Tel Aviv + Netanya + Haifa Bay + Akko + Eilat); c5_extreme NEW Dead Sea industrial sub-zone (Dead Sea Works Sodom; Bazan refinery Haifa; ~33% salinity Dead Sea — ultra-saline natural water body)', status: 'verified', isNew: true },
  { check: 'D#21 content-leakage gate (KB §73.x)',               criterion: 'IL vocabulary (IEC, Noga, PUA, INCD, CERT-IL, Unit 8200, Mekorot, Tamar, Leviathan, Hagit, Tzafit, Orot Rabin, Rutenberg, Dorad, Ashalim, Bazan, Sorek, Negev, Beersheba, Dimona, Galilee, Knesset, Technion) cross-cohort sweep clean', status: 'verified', isNew: true },
  { check: 'edition_anchor_month_offset = 5 (D#20 KB §72.10)',   criterion: '5-month offset — Edition 02 falls on 2026-07-09 (2nd Thursday July) per cohort sync with SI/SK/HU/IS/KR/CR', status: 'verified', isNew: false }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'IL-S34-9', change: 'Greenfield thin-shell on post-S33 D#21-codified architecture — 5 core pages (index/regional/map/data + ssi-metadata.js) authored directly on CountryRenderer.Safe + normalizeMeta() (KB §68.10/11) + admin-unit-suffix tolerance (KB §69.11) + content-leakage gate (KB §73.x BPG Discipline #21)', type: 'enhanced', section: 'KB §74' },
  { id: 'IL-S34-8', change: 'Section D deepDives rotation — 6 Israeli mehozot rotation seeded with Tel Aviv (Edition 01 inaugural anchor — Silicon Wadi) + Haifa (Bazan refinery + Carmel chemical complex + Yokne’am chip cluster Mellanox/Nvidia) + Central (Sharon Plain tech + Sorek/Palmachim desalination cluster) + Southern (Negev + Beersheba CyberSpark + Dimona + R6_drought peak) + Jerusalem (capital + Hebrew University + Mobileye HQ + DST seismic) + Northern (Galilee agriculture + Migdal HaEmek)', type: 'new', section: 'intelligence D' },
  { id: 'IL-S34-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-08-13 — single-country onboarding (Session 34) post-S33 D#21 codification; edition_anchor_month_offset = 5 per cohort sync with SI/SK/HU/IS/KR/CR (Edition 02 = 2026-07-09)',                  type: 'enhanced', section: 'intelligence' },
  { id: 'IL-S34-6', change: 'ESG report — israel entry in COUNTRY_SOURCES (13 IL-specific references including IEC + PUA + Noga ILITO + GSI 1927 Jericho + CBS end-2024 + Mekorot desalination + INCD + CERT-IL)', type: 'new',      section: 'esg-report' },
  { id: 'IL-S34-5', change: 'R3 4-tier calibration — Tel Aviv 1.06 / Central + Haifa 1.05 / Jerusalem 1.04 / Northern + Southern 1.03 — moderate-upper gradient cohort mid-upper (GDP/cap spread Tel Aviv $75-90k district-level to Northern/Southern $35-45k district-level)', type: 'new', section: 'methodology' },
  { id: 'IL-S34-4', change: 'R6_drought NEW α anchor — FIRST in cohort — arid-climate drought + desalination-electricity nexus modifier (Negev 0.16-0.18 + Central coastal-desalination 0.12-0.14 + Northern Galilee 0.08-0.10); R6_volcanic INACTIVE flag (Pliocene Golan basalts ~4 Mya only); R6a_seismic Dead Sea Transform strike-slip primary source (1927 Jericho Mw 6.2 + 1995 Aqaba Mw 7.2 anchors)', type: 'new', section: 'methodology' },
  { id: 'IL-S34-3', change: 'd05_osm LIVE — 257 substations via ISO3166-1=IL area filter (effectively insular grid; zero synchronous interconnect; EuroAsia HVDC IL-CY-GR Phase 1 in construction target 2027-2028 documented forward-only)', type: 'data',     section: 'methodology' },
  { id: 'IL-S34-2', change: 'IEC (dominant TSO + dominant generator + dominant DSO ~80%) + Noga ILITO (independent system operator since 1 Nov 2021) + PUA regulator (since 1996) + MEI policy + CBS statistics + Bank of Israel macro + GSI seismic + IMS climate + Mekorot desalination + INCD + CERT-IL + Unit 8200 wired',   type: 'data',     section: 'methodology' },
  { id: 'IL-S34-1', change: 'KB v34 §74 — Israel inaugural onboarding (Session 34, single-country post-S33 D#21 codification; ILS currency post-symbol; first Middle-Eastern OECD member; OECD accession 7 Sep 2010 as 33rd member; first effectively-insular Mediterranean grid; first R6_drought modifier; first R6_volcanic INACTIVE precedent; R7 ceiling 1.040 cohort-LEADING)', type: 'enhanced', section: 'KB §74' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports.
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Monthly','CC-BY-4.0','R1, R3'],
  ['Dead Sea Transform Seismic Hazard','GSI — Geological Survey of Israel (PGA 475-yr; 1927 Jericho + 1995 Aqaba anchors)','2024','Multi-year','Open','R1, R3'],
  ['Negev Arid Drought Index (R6_drought NEW)','IMS — Israel Meteorological Service (2013-2018 multi-year drought anchor; Negev 25-200 mm/yr vs Galilee 600-800 mm/yr)','2024','Daily','Open','R1, R3'],
  ['Desalination-Electricity Nexus','Mekorot — national water utility + PUA (5 major plants Sorek + Hadera + Ashkelon + Palmachim + Ashdod; ~85% municipal water + ~3.4% national electricity)','2024','Monthly','Regulated','R3, R4'],
  ['Population & Economics','CBS — Central Bureau of Statistics (Halamas; end-2024 population 10,027,000 across 6 mehozot)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','IEC + Noga ILITO + PUA (SMP wholesale market since 1 Nov 2021)','2024','Daily','Regulated','R2, R4'],
  ['Renewable Generation Mix','PUA + MEI (~70% natural gas Tamar+Leviathan offshore + ~20% coal Orot Rabin+Rutenberg phase-out + ~10% renewables solar-dominant; target 30% by 2030)','2024','Monthly','Open','R4'],
  ['Weather + Climate','IMS — Israel Meteorological Service (under Ministry of Transport; ECMWF mirror)','2024','Daily','CC-BY-4.0','R1'],
  ['R6_volcanic INACTIVE flag','GSI — Geological Survey of Israel (Pliocene Golan basalts ~4 Mya; no active volcanism; first explicit active:false precedent in cohort)','2024','Reference','Open','R1, R3'],
  ['Cybersecurity Posture','INCD — Israel National Cyber Directorate (Dec 2017, PMO) + CERT-IL (2014, CyberSpark Beersheba) + Unit 8200 (IDF, since 1952)','2024','Annual','Open','R6'],
  ['Power Plant Fleet','IEC + GEM + database.earth (Hagit ~1,255 MW CCGT + Orot Rabin ~2,590 MW + Rutenberg ~2,250 MW + Tzafit/Dalia 835 MW + Dorad 840 MW + Gezer 744 MW + Alon Tavor 593 MW + Ashalim 310 MW CSP+PV)','2024','Annual','Industry','R2, R3'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C5 + c5_extreme NEW Dead Sea sub-zone)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
