// Iceland SSI v4.0.2 metadata — KB §70 · greenfield thin-shell on post-CEE-South-2026 architecture
// Pattern C (Wave 6c) — NO IIFE wrapper · KB §58.6 Canada IIFE root-cause
// Dual-global alias per KB §45.6
// Edition 01 (Iceland inaugural) · first refresh 2026-08-13 (Single-country onboarding, post-cohort closure)
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
  kb_version: 'v29',
  bpg_version: 'v1.28',
  currency: 'ISK',
  currency_symbol: 'kr.',
  currency_position: 'after',
  labels: {
    country_en: 'Iceland',
    country_local: 'Ísland',
    capital: 'Reykjavík',
    capital_local: 'Reykjavík',
    region_unit: 'landshluti',
    region_unit_local: 'landshluti',
    tso: 'Landsnet hf. (Icelandic transmission system operator; State 93.22% + Orkuveita Reykjavíkur 6.78%)',
    regulator: 'Orkustofnun (Icelandic National Energy Authority)',
    statistics_office: 'Hagstofa Íslands (Statistics Iceland)',
    nem: 'Not applicable (isolated grid, no NEMO, no SDAC/SIDC)',
    bidding_zone: 'IS-ISOLATED (no ENTSO-E zone)'
  },
  stats: { sources: 11, variables: 95, components: 6, modifiers: 7 },
  methodology: {
    formula: 'R = base − Σ component contributions × modifiers',
    components: ['C', 'V', 'I', 'E', 'S', 'T'],
    modifiers: ['R3_C_mult', 'R4_F_topo', 'R6_seismic', 'R6_volcanic', 'R6c_jokulhlaup', 'R7_cyber'],
    mc_iterations: 10000,
    r3_tiers: '4-tier (Industrial-Aluminum 1.05 / Capital-Reykjavík 1.04 / Commercial-SME 1.03 / Light-Rural 1.02)',
    r6_anchors: '19 Mar 2021 Reykjanes/Fagradalsfjall eruption cycle begins · 8 Feb 2024 Sundhnúkur eruption damages Svartsengi hot-water pipeline (~26,000 residents lose district heating ~4 days; Grindavík evacuated since 10 Nov 2023) · 2010-04-14 Eyjafjallajökull eruption + Markarfljót jökulhlaup · 1996 Skeiðará jökulhlaup (Grímsvötn-triggered) · 2008-05-29 SISZ Mw 6.3 doublet (Selfoss-Hveragerði)',
    r7_ceiling: 1.04
  }
};

// ── Dual-global alias (KB §45.6) ──
window.SSI_METADATA = window.SSIMetadata;

// ── Components, sources, layers, regions, DSOs ──

// COMPONENTS_INDEX — INTENTIONALLY Slovakia-style {code, name, ceiling, drivers}
// (KB §68.10 acceptance test — normalizeMeta() must alias this to {key, label, w, color})
window.SSI_METADATA.COMPONENTS_INDEX = [
  { code: 'C', name: 'Continuity',     ceiling: 0.30, drivers: 'SAIDI/SAIFI · Orkustofnun quality reports · Landsnet network statement · Reykjavík urban ~26 min vs Vestfirðir rural ~115 min split (3-DSO panel: Veitur / RARIK / HS Veitur)' },
  { code: 'V', name: 'Voltage Quality', ceiling: 0.18, drivers: 'EN 50160 events · Landsnet + 3-DSO quarterly filings · Veitur Reykjavík metro (~55-60% / OR-owned) + RARIK rural (~30-35% / state) + HS Veitur Suðurnes/Reykjanes (~10-15% / HS Orka)' },
  { code: 'I', name: 'Infrastructure', ceiling: 0.18, drivers: 'OSM topology · Landsnet asset register · 220/132/66 kV inventory (Byggðalína 220 kV ring backbone vs RARIK 33 kV rural legacy) + 3 aluminum smelter switchyards (Alcoa Fjarðaál 625 MW · Rio Tinto ISAL Straumsvík 400 MW · Century Aluminum Norðurál Grundartangi 540 MW)' },
  { code: 'E', name: 'Economic',       ceiling: 0.14, drivers: 'Hagstofa NUTS-2/3 + landshluti regional accounts · Seðlabanki Íslands national accounts · aluminum smelter ~70-80% national electricity demand · ISK industrial tariffs vs EUR comparators · data-center cluster ~6% (Verne Global Keflavík + atNorth + Borealis Blönduós)' },
  { code: 'S', name: 'Societal',       ceiling: 0.12, drivers: 'Hagstofa energy-poverty (<2%, lowest in cohort) · Vestfirðir (Westfjords, <7,000 pop. in 22,000 km²) peripheral exposure · Suðurnes/Reykjanes ongoing eruption-cycle community impact (Grindavík evacuated since 10 Nov 2023)' },
  { code: 'T', name: 'Transition',     ceiling: 0.08, drivers: 'Orkustofnun DER + generation registry · ~99.97% renewable mix (hydro 70.5% + geothermal 29.4% + fossil 0.1%) · T_share saturated near 1.0 (methodological note: T1 DER stress loses dynamic range) · Vaðölduver 120 MW wind (first utility wind, target 2027)' }
];

window.SSI_METADATA.DATA_SOURCES = [
  { id: 'd01_landsnet',     name: 'Landsnet — Icelandic transmission system operator (TSO; State 93.22% + OR 6.78%)', freq: 'Daily',      status: 'live', vars: 14, feeds: 'C2,C3,I1,I2,I3,R4', sources: 'landsnet.is network statement + Byggðalína 220 kV ring + 132/66 kV' },
  { id: 'd02_orkustofnun',  name: 'Orkustofnun — Icelandic National Energy Authority',                            freq: 'Annual',     status: 'live', vars: 12, feeds: 'C1,C2,V1,V2,T1,E1', sources: 'orkustofnun.is raforkutölfræði + quality-of-supply + tariff decisions + generation licenses' },
  { id: 'd02b_dso',         name: '3 regional DSOs (Veitur ohf. + RARIK ohf. + HS Veitur hf.)',                    freq: 'Quarterly',  status: 'live', vars: 18, feeds: 'C1,V1,V2,I2,I3', sources: 'Veitur (Reykjavík metro / OR) + RARIK (rural / State) + HS Veitur (Suðurnes / HS Orka) quarterly filings' },
  { id: 'd03_imo',          name: 'Veðurstofa Íslands (IMO/OVF) — meteorology + hydrology + seismology + volcanology', freq: 'Daily',  status: 'live', vars: 12, feeds: 'I1,I2,I3,R6_climate,R6_seismic,R6_volcanic,R6c_jokulhlaup', sources: 'vedur.is — single consolidated agency (met + Þjórsá Q100 + river gauges + Mid-Atlantic Ridge seismic catalogue + Reykjanes/Vatnajökull/Hekla volcanic monitoring + jökulhlaup forecasting)' },
  { id: 'd04_hagstofa',     name: 'Hagstofa Íslands — Statistics Iceland',                                        freq: 'Quarterly',  status: 'live', vars: 16, feeds: 'E1,E2,S1,S2,S3', sources: 'hagstofa.is NUTS-2 IS00 + NUTS-3 IS001+IS002 + 8 landshluti regional accounts + 62 sveitarfélög LAU-2' },
  { id: 'd04b_cbi',         name: 'Seðlabanki Íslands — Central Bank of Iceland (ESCB non-€; independent ISK)',    freq: 'Quarterly',  status: 'live', vars: 4,  feeds: 'E1,E2', sources: 'sedlabanki.is national accounts + financial stability' },
  { id: 'd05_osm',          name: 'OSM Overpass — grid topology (ISO3166-1=IS area filter)',                       freq: 'Monthly',    status: 'live', vars: 8,  feeds: 'I1,I2,I3,R4', sources: 'overpass-api.de power=substation/line/minor_line · ISO3166 IS · 687 substations + 1,428 lines (248 line + 1,180 minor_line)' },
  { id: 'd06_ust',          name: 'Umhverfisstofnun (UST) — Environment Agency of Iceland (ISO 9223 corrosion)',  freq: 'Monthly',    status: 'live', vars: 5,  feeds: 'R5_corrosion,I8', sources: 'ust.is PM2.5/NO₂ + H₂S geothermal + salt-aerosol coastal · ISO 9223 C2-C5 (C5 restored at Reykjanes coastal + Hellisheiði H₂S nodes)' },
  { id: 'd07_copernicus',   name: 'Copernicus ERA5 + CMIP6',                                                      freq: 'Monthly',    status: 'live', vars: 4,  feeds: 'R6_climate', sources: 'cds.climate.copernicus.eu SSP2-4.5 · 64-66°N reanalysis' },
  { id: 'd09_cert_is',      name: 'CERT-IS (National CSIRT, founded 2013; operated under Fjarskiptastofa)',        freq: 'Continuous', status: 'live', vars: 5,  feeds: 'R7_cyber', sources: 'cert.is incident database + FIRST + Nordic CERT Cooperation (NCC) baseline · Act 78/2019 + 2025 NIS2 amendment' },
  { id: 'd10_fjarskiptastofa', name: 'Fjarskiptastofa (ECOI) — Electronic Communications Office of Iceland (NIS2 CA)', freq: 'Annual',  status: 'live', vars: 3,  feeds: 'R7_cyber', sources: 'fjarskiptastofa.is NIS2 competent authority (Act 78/2019 + 2025 amendment via EEA process; in force 1 Jan 2026); 24h initial / 72h update / 30d full' },
  { id: 'd11_generation',   name: 'Landsvirkjun + ON Power + HS Orka generation operators (top-3 = 97%)',          freq: 'Quarterly',  status: 'live', vars: 8,  feeds: 'I1,I3,T1', sources: 'Landsvirkjun ~71-75% (State, Kárahnjúkar 690 MW + Þjórsá-Tungnaá complex) + ON Power ~9-12% (OR subsidiary, Hellisheiði 303 MW + Nesjavellir 120 MW) + HS Orka ~9% (Alterra, Svartsengi + Reykjanes 100 MW)' },
  { id: 'd12_eurostat',     name: 'Eurostat — EU-27 + EFTA/EEA benchmarks (Iceland via EEA since 1 Jan 1994)',     freq: 'Annual',     status: 'live', vars: 8,  feeds: 'E1,S1,T1', sources: 'ec.europa.eu/eurostat NUTS-2 IS00 + DESI EFTA-EEA proxy + energy benchmarks' },
  { id: 'd13_iea_oecd',     name: 'IEA + OECD — energy benchmarks (Iceland founding OECD member, 30 Sep 1961)',    freq: 'Annual',     status: 'live', vars: 6,  feeds: 'T1,E1', sources: 'iea.org + oecd.org energy statistics · Iceland industrial tariff ~$0.058/kWh (2nd cheapest in OECD after Norway)' }
];

window.SSI_METADATA.FREQ_DISTRIBUTION = {
  Weekly:    { count: 0,  sources: [] },
  Monthly:   { count: 3,  sources: ['OSM Overpass', 'Umhverfisstofnun (UST) air quality', 'Copernicus ERA5/CMIP6'] },
  Quarterly: { count: 4,  sources: ['DSO filings (Veitur + RARIK + HS Veitur)', 'Hagstofa Íslands', 'Seðlabanki Íslands', 'Generation operators (Landsvirkjun + ON Power + HS Orka)'] },
  Annual:    { count: 4,  sources: ['Orkustofnun', 'Eurostat', 'Fjarskiptastofa (ECOI)', 'IEA/OECD'] },
  Continuous:{ count: 2,  sources: ['Landsnet (TSO)', 'CERT-IS'] },
  Daily:     { count: 2,  sources: ['Landsnet', 'Veðurstofa Íslands (IMO)'] }
};

window.SSI_METADATA.DATA_LAYERS = [
  { id: 'tso',        name: 'Landsnet transmission (220 / 132 / 66 kV) — Byggðalína ring',          vars: 14, status: 'live', sources: 'Landsnet network statement (no ENTSO-E membership; isolated grid)' },
  { id: 'dso',        name: '3 regional DSOs (Veitur + RARIK + HS Veitur)',                          vars: 18, status: 'live', sources: 'Veitur (Reykjavík metro / OR) + RARIK (rural / State) + HS Veitur (Suðurnes / HS Orka)' },
  { id: 'regulator',  name: 'Orkustofnun — quality + tariff + generation licensing',                  vars: 12, status: 'live', sources: 'Orkustofnun raforkutölfræði + annual quality reports' },
  { id: 'statistics', name: 'Hagstofa — landshluti + NUTS-3 socio-economic',                          vars: 16, status: 'live', sources: 'Hagstofa Íslands regional accounts (NUTS-2 IS00 + NUTS-3 IS001/IS002 + 8 landshluti)' },
  { id: 'hazard',     name: 'Multi-hazard (seismic + volcanic + jökulhlaup + storm + icing)',          vars: 15, status: 'live', sources: 'Veðurstofa Íslands (IMO) consolidated · Reykjanes/Vatnajökull/Hekla + SISZ/Tjörnes + Skeiðará/Eyjafjallajökull anchors' },
  { id: 'cyber',      name: 'CERT-IS + Fjarskiptastofa (ECOI)',                                       vars: 8,  status: 'live', sources: 'CERT-IS (founded 2013, FIRST + NCC member) + Act 78/2019 + 2025 NIS2 amendment' },
  { id: 'topology',   name: 'OSM grid topology (ISO3166-1=IS area filter; insular grid)',             vars: 8,  status: 'live', sources: 'OSM Overpass ISO3166 IS area filter (zero cross-border interconnects — first in cohort)' },
  { id: 'generation', name: 'Top-3 generation operators (97% national)',                              vars: 6,  status: 'live', sources: 'Landsvirkjun (Kárahnjúkar + Þjórsá-Tungnaá) + ON Power (Hellisheiði + Nesjavellir) + HS Orka (Svartsengi + Reykjanes)' }
];

// REGIONS — Iceland's 8 traditional landshluti
// NUTS-2 is single (IS00); NUTS-3 binary split (IS001 Höfuðborgarsvæðið / IS002 Landsbyggð) is too coarse
// for tier stratification. Landshluti are the natural granularity for R3 + R6_volcanic + R6_seismic.
// Codes here are 3-letter convenience tags (HOF/SUN/VES/VFJ/NLV/NLE/AUS/SUL) since landshluti
// have no formal Eurostat code at this granularity.
window.SSI_METADATA.REGIONS_NUTS3 = [
  { code: 'HOF', name: 'Höfuðborgarsvæðið',  capital: 'Reykjavík',     tier: 'Capital-Reykjavík',     r3: 1.04 },
  { code: 'SUN', name: 'Suðurnes',           capital: 'Reykjanesbær',  tier: 'Industrial-Aluminum',   r3: 1.05 },
  { code: 'VES', name: 'Vesturland',         capital: 'Borgarnes',     tier: 'Industrial-Aluminum',   r3: 1.05 },
  { code: 'VFJ', name: 'Vestfirðir',         capital: 'Ísafjörður',    tier: 'Light-Rural-Peripheral',r3: 1.02 },
  { code: 'NLV', name: 'Norðurland vestra',  capital: 'Sauðárkrókur',  tier: 'Light-Rural-Peripheral',r3: 1.02 },
  { code: 'NLE', name: 'Norðurland eystra',  capital: 'Akureyri',      tier: 'Commercial-SME',        r3: 1.03 },
  { code: 'AUS', name: 'Austurland',         capital: 'Egilsstaðir',   tier: 'Industrial-Aluminum',   r3: 1.05 },
  { code: 'SUL', name: 'Suðurland',          capital: 'Selfoss',       tier: 'Commercial-SME',        r3: 1.03 }
];

window.SSI_METADATA.DSO_PANEL = [
  { name: 'Veitur ohf.',     region: 'Höfuðborgarsvæðið (Greater Reykjavík, 6 Faxaflói municipalities)', share_pct: 58, parent: 'Orkuveita Reykjavíkur (OR) — state-owned via Reykjavík + 2 municipalities' },
  { name: 'RARIK ohf.',      region: 'Rural Iceland (~85% of country by area; outside Reykjavík + Suðurnes)', share_pct: 32, parent: 'Icelandic State (100%)' },
  { name: 'HS Veitur hf.',   region: 'Suðurnes / Reykjanes peninsula (Keflavík + Grindavík + Vestmannaeyjar)', share_pct: 10, parent: 'HS Orka (Alterra majority) + minority State' }
];


// ── Extended metadata for methodology.html / data.html / intelligence.html C-section ──
// KB §58.6 compliant — no IIFE wrapper, dual-global alias preserved above.

window.SSI_METADATA.COMPONENTS = [
  { id: 'C', name: 'Continuity', weight: 0.30, color: '#941914', isNew: false,
    metrics: [
      { id: 'C1', name: 'SAIDI (planned + unplanned)',     intra: 0.30, global: 0.090, norm: 'P5/P95 inverse',  source: 'Orkustofnun raforkutölfræði — per-DSO quality reports (Veitur urban ~26 min vs RARIK rural ~115 min)' },
      { id: 'C2', name: 'SAIFI (interruption frequency)',   intra: 0.25, global: 0.075, norm: 'P5/P95 inverse',  source: 'Orkustofnun — per-DSO (3-DSO panel: Veitur + RARIK + HS Veitur)' },
      { id: 'C3', name: 'Voltage class (max kV)',           intra: 0.20, global: 0.060, norm: 'log-scaled',      source: 'OSM Overpass + Landsnet network statement (220 / 132 / 66 kV — Byggðalína ring)' },
      { id: 'C4', name: 'Customer count (catchment)',       intra: 0.15, global: 0.045, norm: 'P5/P95 inverse',  source: 'Veitur + RARIK + HS Veitur DSO filings + Hagstofa Íslands' },
      { id: 'C5', name: 'CAIDI restoration speed',          intra: 0.10, global: 0.030, norm: 'P5/P95 inverse',  source: 'Orkustofnun + Almannavarnir (civil protection coordination)' }
    ]},
  { id: 'V', name: 'Voltage Quality', weight: 0.10, color: '#aa4234', isNew: false,
    metrics: [
      { id: 'V1', name: 'EN 50160 dip events',              intra: 0.40, global: 0.040, norm: 'count per 1000 cust/yr', source: 'Orkustofnun + 3 DSOs (Veitur + RARIK + HS Veitur)' },
      { id: 'V2', name: 'Voltage swell events',             intra: 0.30, global: 0.030, norm: 'count per 1000 cust/yr', source: 'Orkustofnun + 3 DSOs' },
      { id: 'V3', name: 'Harmonic distortion (THD)',        intra: 0.30, global: 0.030, norm: 'P95 of weekly THD',      source: 'Orkustofnun quarterly filings (aluminum-smelter loads dominate THD profile at Fjarðaál / Straumsvík / Grundartangi)' }
    ]},
  { id: 'I', name: 'Infrastructure', weight: 0.25, color: '#5d8563', isNew: false,
    metrics: [
      { id: 'I1', name: 'Heat-wave IRI (sub-Arctic)',       intra: 0.18, global: 0.045, norm: 'GDD anomaly',         source: 'Copernicus ERA5 + Veðurstofa Íslands — heat-wave loading is structurally low at 64-66°N', adaptive: true },
      { id: 'I2', name: 'Storm + icing (winter windstorm)', intra: 0.14, global: 0.035, norm: 'P99 events',           source: 'Veðurstofa Íslands — 10-11 Dec 2019 N-Iceland storm anchor (40 transmission towers failed)', adaptive: true },
      { id: 'I3', name: 'Wind storm IRI',                   intra: 0.12, global: 0.030, norm: 'P99 m/s hourly',       source: 'Veðurstofa Íslands wind atlas — sustained >25 m/s autumn-winter; Vestfirðir + Mt. Hekla foothills peak gusts', adaptive: true },
      { id: 'I4', name: 'Asset age cohort',                 intra: 0.14, global: 0.035, norm: 'Markov-weighted',      source: 'Landsnet + 3 DSOs annual reports (RARIK 33 kV rural legacy vs Landsnet 220 kV backbone)' },
      { id: 'I5', name: 'Thermal stress (R6 proxy)',        intra: 0.10, global: 0.025, norm: 'IEEE C57.91',          source: 'IEEE C57.91 + Copernicus (smelter-feeding 220 kV corridors run hot continuously)' },
      { id: 'I6', name: 'Substation density',               intra: 0.10, global: 0.025, norm: 'per km²',              source: 'OSM + Hagstofa Íslands (687 subs across 102,775 km²)' },
      { id: 'I7', name: 'Network length per cap',           intra: 0.08, global: 0.020, norm: 'P5/P95',               source: 'Landsnet + 3 DSOs (1,428 power lines: 248 line + 1,180 minor_line)' },
      { id: 'I8', name: 'Industrial corrosion ISO 9223',    intra: 0.10, global: 0.025, norm: 'C2-C5 categorical',    source: 'Umhverfisstofnun (UST) + ISO 9223 (C5 at Reykjanes coastal + Hellisheiði H₂S; C4 at 3 smelter nodes Fjarðaál + Straumsvík + Grundartangi)' },
      { id: 'I9', name: 'Hydrogeological exposure',         intra: 0.04, global: 0.010, norm: 'Q100 + jökulhlaup overlay', source: 'Veðurstofa Íslands — Þjórsá Q100 + Skeiðará/Markarfljót jökulhlaup corridors' }
    ]},
  { id: 'E', name: 'Economic', weight: 0.10, color: '#3b9eff', isNew: false,
    metrics: [
      { id: 'E1', name: 'Regulatory penalty exposure',      intra: 0.60, global: 0.060, norm: 'EUR-eq per SAIDI min', source: 'Orkustofnun tariff decisions (ISK native, EUR-eq for cross-country)' },
      { id: 'E2', name: 'Productivity loss (VoLL)',         intra: 0.40, global: 0.040, norm: 'EUR-eq/kWh',            source: 'ACER 2023 + Hagstofa Íslands sector mix (aluminum ~70-80% national load · tourism ~10% GDP · data centers ~6% national electricity)' }
    ]},
  { id: 'S', name: 'Saturation', weight: 0.20, color: '#b8863a', isNew: false,
    metrics: [
      { id: 'S1', name: 'Regional KPI — saturation',        intra: 0.45, global: 0.090, norm: 'load/capacity %',     source: 'Landsnet + 3 DSOs (Kárahnjúkar→Fjarðaál dedicated 220 kV near saturation)' },
      { id: 'S2', name: 'Reverse power flow',               intra: 0.35, global: 0.070, norm: 'hours/yr reverse',     source: 'Landsnet (insular grid, no cross-border; reverse flow limited to local DER + Vaðölduver wind from 2027)' },
      { id: 'S3', name: 'Criticality class',                intra: 0.20, global: 0.040, norm: 'categorical 1-5',      source: 'Landsnet Network Statement (Byggðalína ring strengthening 2023-2026 lifts capacity ~130 MW → 210-250 MW eventual ~600 MW)' }
    ]},
  { id: 'T', name: 'Transition', weight: 0.05, color: '#22d3ee', isNew: true,
    metrics: [
      { id: 'T1', name: 'DER Stress Index',                 intra: 1.00, global: 0.050, norm: 'composite',            source: 'Orkustofnun DER + generation registry · T_share saturated near 1.0 (hydro 70.5% + geothermal 29.4% + fossil 0.1%) · Vaðölduver 120 MW wind first utility-scale, target 2027', isNew: true }
    ]}
];

// MODIFIER_DEFS — INTENTIONALLY Slovakia-style {id, domain, range, description}
// (KB §68.11 acceptance test — normalizeModifierDef() must map {R3→R3_C_mult, R6a→R6_restoration, R6b→R6_seismic, R7→R7_cyber})
// Iceland-specific: R6_volcanic + R6c_jokulhlaup are NEW sub-patterns (first in cohort).
window.SSI_METADATA.MODIFIER_DEFS = [
  { id: 'R2',  domain: 'Adaptive IRI + Climate',     range: 'internal',     description: 'Shifts weight from climate-IRI to structural metrics where local climate risk is low. CMIP6 SSP2-4.5 projections adjust forward-looking risk; at 64-66°N Iceland\'s heat-wave loading is structurally low and the dominant adaptive vectors are winter windstorm + atmospheric icing.' },
  { id: 'R3',  domain: 'Consequence + Poverty',      range: '[0.70, 1.30]', description: 'Amplifies risk for landshluti serving large/energy-poor populations with high economic dependency. Iceland uses a 4-tier calibration (Industrial-Aluminum 1.05 / Capital-Reykjavík 1.04 / Commercial-SME 1.03 / Light-Rural 1.02) — the flattest gradient in cohort. Industrial-Aluminum tier reflects the 3-smelter corridors (Alcoa Fjarðaál, Rio Tinto ISAL Straumsvík, Century Aluminum Norðurál Grundartangi) consuming ~70-80% of national electricity; Capital-Reykjavík reflects ~64% of population in Höfuðborgarsvæðið.' },
  { id: 'R4',  domain: 'Graph Criticality',          range: '[0.80, 1.35]', description: 'Penalises topological bottlenecks: high betweenness centrality, bridge nodes, low degree. Built from OSM power graph (687 substations + 1,428 power lines: 248 line + 1,180 minor_line). Iceland is the FIRST country in the cohort with ZERO cross-border interconnects — the IceLink HVDC-to-UK stalled feasibility 2026; Greenland-Iceland-Canada unverified.' },
  { id: 'R6a', domain: 'Restoration Speed',          range: '[0.90, 1.10]', description: 'Orkustofnun-CAIDI-based: rewards fast-restoring urban areas (Reykjavík metro under Veitur), penalises slow ones. Vestfirðir + Norðurland vestra carry a remote-rural access penalty (long radial 132 kV feeds, sparse population <7,000 in 22,000 km² Westfjords).' },
  { id: 'R6_seismic', domain: 'Network Topology + Seismic', range: '[1.00, 1.25]', description: 'Network centrality + Mid-Atlantic Ridge seismic hazard. Iceland straddles the ridge with two active source zones — the South Iceland Seismic Zone (SISZ, anchor: 29 May 2008 Mw 6.3 doublet Selfoss-Hveragerði) and the Tjörnes Fracture Zone (TFZ, Norðurland eystra). R6_seismic α band [0.05, 0.20] — HIGHEST in cohort outside New Zealand. Veðurstofa Íslands publishes 475-yr PGA hazard maps.' },
  { id: 'R6_volcanic', domain: 'Volcanic Activity (NEW sub-pattern)', range: '[1.00, 1.20]', description: 'FIRST IN COHORT — codifies active-volcanism exposure. R6_volcanic α band [0.00, 0.20]: Reykjanes/Sundhnúkur peak 0.14 (active eruption cycle since 19 Mar 2021 Fagradalsfjall; 8 Feb 2024 Sundhnúkur eruption damaged Svartsengi hot-water pipeline, ~26,000 residents lost district heating ~4 days, Grindavík evacuated since 10 Nov 2023); Suðurland 0.10 (Hekla last erupted Feb 2000 · Katla overdue · Eyjafjallajökull April-May 2010); Austurland 0.07 (Vatnajökull / Grímsvötn / Bárðarbunga Holuhraun 2014-2015); Vestfirðir + Norðurland vestra 0.00-0.02 (no active volcanism). Carries forward to next cohort country with volcanism (KR Jeju / IT Etna+Vesuvius / JP nationwide).' },
  { id: 'R6c_jokulhlaup', domain: 'Glacial-Outburst Flood (NEW sub-pattern)', range: '[1.00, 1.15]', description: 'FIRST IN COHORT — Iceland\'s flood risk is structurally jökulhlaup-dominant, not Q100-fluvial. Sub-glacial volcanic activity melts ice within Vatnajökull / Mýrdalsjökull / Eyjafjallajökull, water accumulates in a sub-glacial lake, then bursts as flash flood. Anchors: 1996 Skeiðará jökulhlaup (Grímsvötn-triggered, destroyed bridges along the Ring Road south coast), 14 April 2010 Eyjafjallajökull (Markarfljót valley flooded), 2011 Grímsvötn. α band [0.00, 0.15] concentrated in Suðurland + Austurland 132 kV transmission corridors.' },
  { id: 'R7',  domain: 'Digital Readiness',          range: '[0.99, 1.04]', description: 'Regional DESI digital readiness score (Iceland EFTA-EEA proxy ~0.65-0.70), CERT-IS maturity (founded 2013, FIRST + NCC member), NIS2 transposition (Act 78/2019 + 2025 amendment via EEA process, in force 1 Jan 2026; Fjarskiptastofa/ECOI is the competent authority). Ceiling 1.04 — above SK 1.03 but matches SI 1.04; reflects Iceland\'s OECD top-5 fiber penetration >99% + digital-government ~95% adoption despite later CERT founding date.' }
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
    applies: 'C3 (voltage class · 220/132/66 kV)' },
  { id: 'D', name: 'Categorical mapping',
    formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
    applies: 'I8 (ISO 9223 C2-C5), S3 (criticality class)' }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  { check: 'Schema validation',                                       criterion: 'All required top-level + sub keys present, no nulls',          status: 'verified', isNew: false },
  { check: 'OSM Overpass ISO3166 area filter',                        criterion: 'ISO3166-1=IS area filter — insular grid, no cross-border bbox bleed possible (zero land neighbours)', status: 'verified', isNew: true },
  { check: 'Polygon containment (687 subs → 8 landshluti)',           criterion: 'Every substation falls inside exactly one landshluti polygon (Eurostat GISCO + Hagstofa)',  status: 'verified', isNew: true },
  { check: 'R3 4-tier distribution',                                  criterion: '189 (Industrial-Aluminum 27.5%) / 286 (Capital-Reykjavík 41.6%) / 174 (Commercial-SME 25.3%) / 38 (Light-Rural 5.5%) across 8 landshluti', status: 'verified', isNew: true },
  { check: 'R6 multi-hazard coverage',                                criterion: 'Seismic (Mid-Atlantic Ridge SISZ + TFZ) + Volcanic (Reykjanes/Vatnajökull/Hekla NEW) + Jökulhlaup (NEW) + Storm + Icing', status: 'verified', isNew: true },
  { check: 'R6_volcanic NEW sub-pattern',                             criterion: 'Reykjanes α 0.14 (2021- active cycle) + Suðurland 0.10 (Hekla/Eyjafjallajökull) + Austurland 0.07 (Vatnajökull) + Vestfirðir 0.00-0.02', status: 'verified', isNew: true },
  { check: 'R6c_jokulhlaup NEW sub-pattern',                          criterion: 'Skeiðará 1996 + Eyjafjallajökull/Markarfljót 2010 anchors; Suðurland + Austurland 132 kV corridors',         status: 'verified', isNew: true },
  { check: 'R7 ceiling 1.04 (CERT-IS 2013 · DESI EFTA-EEA ~0.65-0.70)', criterion: 'Matches SI; above SK 1.03 — Act 78/2019 + 2025 NIS2 amendment in force 1 Jan 2026', status: 'verified', isNew: false },
  { check: 'Zero cross-border interconnects',                         criterion: 'Insular grid — 0 land interconnects; IceLink HVDC-to-UK stalled feasibility 2026; renderer handles empty cross_border_lines array as "0 MW (isolated grid)"', status: 'verified', isNew: true },
  { check: 'T_share saturation handling',                             criterion: '~99.97% renewable (hydro 70.5% + geothermal 29.4% + fossil 0.1%); T1 DER stress methodological note documents flat T_share is correct', status: 'verified', isNew: true },
  { check: 'MIN_FLEET[IS]=250 floor enforced',                        criterion: '687 substations exceeds 250 minimum — stub-gate clear',         status: 'verified', isNew: true },
  { check: 'C5 corrosion class restored',                             criterion: 'C5 at Reykjanes coastal substations + Hellisheiði H₂S geothermal nodes (Iceland coastline + H₂S volcanic emissions drive industrial-marine class)', status: 'verified', isNew: true }
];

window.SSI_METADATA.CHANGELOG = [
  { id: 'IS-S30-9', change: 'Greenfield thin-shell on post-CEE-South-2026 architecture — 8 pages authored directly on CountryRenderer.Safe + normalizeMeta() (KB §68.10/11) + admin-unit-suffix tolerance (KB §69.11)', type: 'enhanced', section: 'KB §70' },
  { id: 'IS-S30-8', change: 'Section D deepDives rotation — 8 Icelandic landshluti rotation seeded with Suðurnes/Reykjanes Sundhnúkur (Ed. 01) + Höfuðborgarsvæðið capital + Austurland/Vesturland aluminum-corridor regions', type: 'new',      section: 'intelligence D' },
  { id: 'IS-S30-7', change: 'Edition patcher anchored at FIRST_REFRESH 2026-08-13 — single-country onboarding post-cohort-closure (§49.4 + §56.10 cohort-cooldown respected)',                  type: 'enhanced', section: 'intelligence' },
  { id: 'IS-S30-6', change: 'ESG report — iceland entry in COUNTRY_SOURCES (12 IS-specific references including Reykjanes Sundhnúkur 2024 + Skeiðará 1996 jökulhlaup + CERT-IS + Act 78/2019)', type: 'new',      section: 'esg-report' },
  { id: 'IS-S30-5', change: 'R3 4-tier calibration — Industrial-Aluminum 1.05 / Capital-Reykjavík 1.04 / Commercial-SME 1.03 / Light-Rural 1.02 — flattest gradient in cohort (post-IS hotfix #2)', type: 'new', section: 'methodology' },
  { id: 'IS-S30-4', change: 'R6_volcanic + R6c_jokulhlaup NEW sub-patterns — first volcanic + glacial-outburst-flood modifiers in cohort (Reykjanes/Vatnajökull/Hekla + Skeiðará/Eyjafjallajökull anchors)', type: 'new', section: 'methodology' },
  { id: 'IS-S30-3', change: 'd05_osm LIVE — 687 substations + 1,428 power lines (248 line + 1,180 minor_line) via ISO3166-1=IS area filter (insular grid, no bbox bleed possible)', type: 'data',     section: 'methodology' },
  { id: 'IS-S30-2', change: '3 regional DSOs (Veitur + RARIK + HS Veitur) + Landsnet TSO + Orkustofnun regulator + Veðurstofa Íslands consolidated met/hydro/seismic/volcanic + CERT-IS + Fjarskiptastofa wired',   type: 'data',     section: 'methodology' },
  { id: 'IS-S30-1', change: 'KB v29 §70 — Iceland inaugural onboarding (Session 30, post-CEE-South-2026 cohort closure; ISK currency, NOT eurozone; EFTA + EEA only, never EU; ENTSO-E NOT a member)',         type: 'enhanced', section: 'KB §70' }
];

// ── ESG-report data-source registry (Phase 2b — KB §65) ──
// Row form: [name, source, vintage, frequency, license, reports_tag, blocked_flag?]
// Consumed by esg-sections.js → getReportSources() to render the
// "Data Sources & Vintage" card on each of the 6 ESG reports.
window.SSI_METADATA.ESG_SOURCES = [
  ['ERA5 Climate Reanalysis','Copernicus CDS','2024','Weekly','CC-BY-4.0','R1, R3'],
  ['Icelandic Seismic Hazard Map','Veðurstofa Íslands (IMO) PGA 475-yr','2023','Multi-year','Open','R1, R3'],
  ['Icelandic Volcanic Monitoring','Veðurstofa Íslands (IMO) — Reykjanes/Vatnajökull/Hekla networks','2024','Continuous','Open','R1, R3'],
  ['Population & Economics','Hagstofa Íslands (Statistics Iceland)','2024','Annual','Open','R2, R3'],
  ['Energy Market Data','Landsnet + Orkustofnun raforkutölfræði','2024','Daily','Regulated','R2, R4'],
  ['Renewable Generation Mix','Orkustofnun (hydro 70.5% + geothermal 29.4% + fossil 0.1%)','2024','Monthly','Open','R4'],
  ['Weather + Climate','Veðurstofa Íslands (IMO/OVF) — consolidated agency','2024','Daily','CC-BY-4.0','R1'],
  ['Jökulhlaup + Q100 Flood Mapping','Veðurstofa Íslands — Skeiðará 1996 + Markarfljót 2010 anchors','2024','Monthly','CC-BY-4.0','R1'],
  ['Cybersecurity Posture','CERT-IS (Fjarskiptastofa-operated, founded 2013) + Fjarskiptastofa (ECOI NIS2 CA)','2024','Annual','Open','R6'],
  ['Aluminum Smelter Loads','Alcoa Fjarðaál + Rio Tinto ISAL Straumsvík + Century Aluminum Norðurál Grundartangi (~70-80% national)','2024','Annual','Industry','R2, R3'],
  ['IEEE C57.91 Thermal Model','IEEE','Standard','N/A','Published','R1'],
  ['CIGRE TB 761 Markov','CIGRE','2019','N/A','Published','R1, R3'],
  ['ISO 9223 Corrosion (C2-C5 — C5 at Reykjanes coastal + Hellisheiði H₂S)','ISO','2012','N/A','Published','R5'],
  ['CMIP6 SSP2-4.5 Projections','Copernicus CDS','2024','Multi-year','CC-BY-4.0','R1']
];

// Mirror onto the lower-case alias too
window.SSIMetadata = window.SSI_METADATA;
