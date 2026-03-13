// SSI v4.0.2 — Japan Metadata
// Generated 2026-03-13 by Ikenga Project

window.SSI_METADATA = {

  country: "Japan",
  country_code: "JP",
  flag: "🇯🇵",

  // ── Regional Labels ──
  labels: {
    level1: "Prefecture",
    level1_plural: "Prefectures",
    level2: "EPCO Territory",
    level2_plural: "EPCO Territories",
    ranking_tab: "Prefecture Ranking",
    comparison_tab: "EPCO Territory Comparison"
  },

  // ── Data Source Registry (35 verified sources) ──
  dataSources: [
    { id: "D1",  name: "OCCTO Area Supply-Demand Statistics", agency: "Organization for Cross-regional Coordination of Transmission Operators (OCCTO)", url: "https://www.occto.or.jp/en/", feeds: "Cross-regional transmission, supply-demand balance, interconnector flows", freq: "Monthly", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D2",  name: "ISEP Energy Statistics", agency: "Institute for Sustainable Energy Policies (ISEP)", url: "https://www.isep.or.jp/en/", feeds: "Renewable energy share, generation mix by prefecture", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D3",  name: "METI Electricity Business Statistics", agency: "Ministry of Economy, Trade and Industry (METI)", url: "https://www.enecho.meti.go.jp/statistics/electric_power/", feeds: "Generation capacity, consumption, demand profiles by utility", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D4",  name: "SBJ Population Census / Current Population Survey", agency: "Statistics Bureau of Japan (SBJ)", url: "https://www.stat.go.jp/english/data/jinsui/", feeds: "Population, elderly ratio, density, household counts by prefecture", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D5",  name: "NIED J-SHIS Seismic Hazard Maps", agency: "National Research Institute for Earth Science and Disaster Resilience (NIED)", url: "https://www.j-shis.bosai.go.jp/en/", feeds: "Peak Ground Acceleration (PGA) probabilistic maps, fault line proximity", freq: "Updated periodically", resolution: "250m mesh", status: "LIVE" },
    { id: "D6",  name: "JMA Seismological Bulletin / Typhoon Statistics", agency: "Japan Meteorological Agency (JMA)", url: "https://www.jma.go.jp/jma/en/Activities/earthquake.html", feeds: "Seismic event catalogue, typhoon frequency and tracks, extreme heat days", freq: "Real-time + Annual", resolution: "National/Regional", status: "LIVE" },
    { id: "D7",  name: "JAXA Satellite-Derived Climate Data", agency: "Japan Aerospace Exploration Agency (JAXA)", url: "https://www.eorc.jaxa.jp/", feeds: "Land surface temperature, vegetation stress, flood inundation extent", freq: "Quarterly", resolution: "Regional", status: "LIVE" },
    { id: "D8",  name: "OpenStreetMap Overpass API — Japan Grid", agency: "OpenStreetMap Contributors", url: "https://overpass-turbo.eu/", feeds: "Substation locations, voltage levels, operator tagging (6,003 verified)", freq: "Continuous", resolution: "Site-level", status: "LIVE" },
    { id: "D9",  name: "TEPCO Grid Reliability Reports", agency: "Tokyo Electric Power Company Holdings (TEPCO)", url: "https://www.tepco.co.jp/en/", feeds: "SAIDI, SAIFI, CAIDI, outage statistics for Kanto region", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D10", name: "Kansai Electric Reliability Data", agency: "Kansai Electric Power Company (KEPCO)", url: "https://www.kepco.co.jp/english/", feeds: "Outage frequency, duration, supply interruption metrics", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D11", name: "Chubu Electric Power Reliability Reports", agency: "Chubu Electric Power Company", url: "https://www.chuden.co.jp/english/", feeds: "SAIDI, CAIDI, service restoration times", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D12", name: "Kyushu Electric Power Reliability Data", agency: "Kyushu Electric Power Company", url: "https://www.kyuden.co.jp/en/", feeds: "Outage statistics, typhoon impact assessments", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D13", name: "Hokkaido Electric Power Reports", agency: "Hokkaido Electric Power Company (HEPCO)", url: "https://www.hepco.co.jp/english/", feeds: "Cold-climate outage data, snow/ice impact metrics", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D14", name: "Tohoku Electric Power Data", agency: "Tohoku Electric Power Company", url: "https://www.tohoku-epco.co.jp/english/", feeds: "Reliability metrics, earthquake recovery performance", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D15", name: "Hokuriku / Shikoku / Chugoku / Okinawa EPCO Reports", agency: "Hokuriku / Shikoku / Chugoku / Okinawa EPCOs", url: "https://www.occto.or.jp/en/", feeds: "Regional reliability statistics, outage reports", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D16", name: "MLIT Flood and Landslide Hazard Maps", agency: "Ministry of Land, Infrastructure, Transport and Tourism (MLIT)", url: "https://disaportal.gsi.go.jp/", feeds: "Flood inundation zones, landslide susceptibility, tsunami risk", freq: "Updated periodically", resolution: "Municipality", status: "LIVE" },
    { id: "D17", name: "GSI Elevation and Terrain Data", agency: "Geospatial Information Authority of Japan (GSI)", url: "https://www.gsi.go.jp/ENGLISH/", feeds: "DEM, terrain classification, slope stability indices", freq: "Static", resolution: "10m mesh", status: "LIVE" },
    { id: "D18", name: "ISO 9223 / JIS Z 2381 Atmospheric Corrosion Maps", agency: "ISO / Japanese Industrial Standards Committee", url: "https://www.jisc.go.jp/eng/", feeds: "Corrosion classification (C1-C5) by coastal proximity and climate", freq: "Static", resolution: "Prefecture", status: "LIVE" },
    { id: "D19", name: "AIST Geological Survey Data", agency: "National Institute of Advanced Industrial Science and Technology (AIST)", url: "https://www.gsj.jp/en/", feeds: "Soil liquefaction susceptibility, geological formation stability", freq: "Static", resolution: "Regional", status: "LIVE" },
    { id: "D20", name: "NISC Cybersecurity Reports", agency: "National center of Incident readiness and Strategy for Cybersecurity (NISC)", url: "https://www.nisc.go.jp/eng/", feeds: "Critical infrastructure cyber incident trends, threat intelligence", freq: "Annual", resolution: "National", status: "LIVE" },
    { id: "D21", name: "MHLW Regional Health Statistics", agency: "Ministry of Health, Labour and Welfare (MHLW)", url: "https://www.mhlw.go.jp/english/", feeds: "Hospital density, healthcare access, elderly care capacity", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D22", name: "MIC Digital Transformation Index", agency: "Ministry of Internal Affairs and Communications (MIC)", url: "https://www.soumu.go.jp/english/", feeds: "Smart grid readiness, broadband penetration, digital governance scores", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D23", name: "Cabinet Office GDP / Regional Economic Accounts", agency: "Cabinet Office / Economic and Social Research Institute (ESRI)", url: "https://www.esri.cao.go.jp/en/sna/menu.html", feeds: "Prefectural GDP, industrial output, economic resilience indicators", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D24", name: "FDMA Fire and Disaster Management Statistics", agency: "Fire and Disaster Management Agency (FDMA)", url: "https://www.fdma.go.jp/en/", feeds: "Disaster response times, emergency infrastructure, vulnerability scores", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D25", name: "JEPX Wholesale Electricity Market Data", agency: "Japan Electric Power Exchange (JEPX)", url: "https://www.jepx.org/en/", feeds: "Spot prices, price volatility, market stress indicators", freq: "Daily", resolution: "Area", status: "LIVE" },
    { id: "D26", name: "BOJ Regional Economic Reports (Sakura Report)", agency: "Bank of Japan (BOJ)", url: "https://www.boj.or.jp/en/research/brp/rer/index.htm", feeds: "Regional economic conditions, business sentiment, investment trends", freq: "Quarterly", resolution: "Regional", status: "LIVE" },
    { id: "D27", name: "NRA Nuclear Safety Reports", agency: "Nuclear Regulation Authority (NRA)", url: "https://www.nra.go.jp/english/", feeds: "Nuclear plant status, safety assessments, evacuation zone data", freq: "As needed", resolution: "Site-level", status: "LIVE" },
    { id: "D28", name: "METI Smart Grid Demonstration Data", agency: "METI / NEDO", url: "https://www.nedo.go.jp/english/", feeds: "Smart meter deployment, demand response capacity, grid modernisation", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" },
    { id: "D29", name: "IEEE C57.91 Thermal Loading Standards", agency: "Institute of Electrical and Electronics Engineers (IEEE)", url: "https://standards.ieee.org/", feeds: "Transformer thermal derating curves, ambient temperature factors", freq: "Static", resolution: "Equipment-level", status: "REFERENCE" },
    { id: "D30", name: "IEC 61850 / JEC Standards Compliance", agency: "IEC / Japanese Electrotechnical Committee (JEC)", url: "https://www.iec.ch/", feeds: "Substation automation readiness, digital twin compatibility", freq: "Static", resolution: "Equipment-level", status: "REFERENCE" },
    { id: "D31", name: "MIC Housing and Land Survey", agency: "Ministry of Internal Affairs and Communications (MIC)", url: "https://www.stat.go.jp/english/data/jyutaku/", feeds: "Housing vulnerability, building stock age, urbanisation metrics", freq: "Quinquennial", resolution: "Prefecture", status: "LIVE" },
    { id: "D32", name: "MEXT University/Research Infrastructure Atlas", agency: "Ministry of Education, Culture, Sports, Science and Technology (MEXT)", url: "https://www.mext.go.jp/en/", feeds: "Research capacity, technical workforce density", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D33", name: "MIC Migration Statistics (Jumin-Kihon-Daicho)", agency: "Ministry of Internal Affairs and Communications (MIC)", url: "https://www.soumu.go.jp/english/", feeds: "Net migration rate, population growth/decline by prefecture", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D34", name: "NPA Crime Statistics and Security Reports", agency: "National Police Agency (NPA)", url: "https://www.npa.go.jp/english/", feeds: "Critical infrastructure physical security indicators", freq: "Annual", resolution: "Prefecture", status: "LIVE" },
    { id: "D35", name: "METI Equipment Age Survey / TEPCO Asset Reports", agency: "METI / General EPCOs", url: "https://www.enecho.meti.go.jp/", feeds: "Transformer age distribution, asset lifecycle data, retirement forecasts", freq: "Annual", resolution: "EPCO Territory", status: "LIVE" }
  ],

  // ── Methodology Sections ──
  methodology: {
    section1_components: "<h3>Six Risk Components</h3><p>The SSI v4.0.2 evaluates each substation across six weighted risk components: <strong>Continuity (C, 25%)</strong> measures outage frequency and duration using EPCO reliability reports (TEPCO, KEPCO, Chubu, Kyushu, Tohoku, Hokkaido, Hokuriku, Chugoku, Shikoku, Okinawa) and OCCTO cross-regional data. <strong>Voltage Quality (V, 15%)</strong> captures severity-weighted voltage dips from EPCO regulatory filings and JEC/IEC 61000 compliance data. <strong>Infrastructure (I, 20%)</strong> combines 9 sub-metrics including JMA-derived climate risk indices (typhoon frequency, extreme heat, snow/ice), OSM network density, IEEE C57.91 thermal stress, MLIT flood/landslide risk, ISO 9223 atmospheric corrosion, and AIST liquefaction susceptibility. <strong>Economic (E, 15%)</strong> measures regulatory penalties and productivity loss coefficients calibrated from Cabinet Office Prefectural GDP, BOJ Sakura Report regional indicators, and JEPX market stress. <strong>Societal (S, 20%)</strong> fuses SBJ population density, MHLW elderly dependency ratios (super-ageing society factor), MIC digital governance scores, hospital density, and FDMA disaster resilience indices. <strong>Temporal (T, 5%)</strong> captures seasonal risk cycles including typhoon season (June–October), extreme heat peaks, and Nankai Trough seismic clustering patterns from JMA bulletins.</p><p>Japan-specific calibration features include: <strong>50 Hz/60 Hz dual-frequency boundary</strong> (Itoigawa–Shizuoka Tectonic Line), with 3 frequency converter stations (Shin-Shinano, Sakuma, Higashi-Shimizu) flagged as <em>is_bridge=1</em> critical nodes; <strong>R6b seismic modifier</strong> calibrated with α=0.30, PGA_ref=0.10g, cap=1.40 to amplify scores in the Nankai Trough zone (Shizuoka, Mie, Wakayama, Kochi); <strong>Markov 5-state degradation</strong> with κ_seismic up to 1.12 and κ_corrosion up to 1.18 for coastal C5 zones; and <strong>quantile calibration</strong> (piecewise linear) ensuring fleet distribution matches §9 targets (Low 20%, Medium 40%, High 25%, Critical 15%).</p>",
    section2_normalisation: "<h3>Normalisation &amp; Aggregation</h3><p>Each raw metric is normalised to [0, 1] using sigmoid transformations with Japan-calibrated parameters: <code>N(x) = 1 / (1 + exp(-k · (x - μ)))</code>. The mid-point μ and steepness k are set per-metric from NIED, EPCO, SBJ, and JMA distributions. Continuity metrics (C1–C4) use EPCO CAIDI as the primary driver (k=0.10 for C1, k=0.08 for C2) to prevent over-sensitivity from Japan’s already-low outage durations. Infrastructure sub-metrics (I1–I9) combine climate hazard (JMA/MLIT), network topology (OSM), and equipment stress (IEEE C57.91). Component scores are computed as weighted sums within each domain, then aggregated into <code>R_base = Σ(w_k · C_k)</code> with weights [C=0.25, V=0.15, I=0.20, E=0.15, S=0.20, T=0.05]. Five modifiers are applied multiplicatively: <strong>R2 topology</strong> (±0.05 for mesh vs radial), <strong>R3 cohort</strong> (age-based 0.90–1.15), <strong>R5 Markov degradation</strong> (5-state transition with seismic and corrosion κ), <strong>R6a CAIDI rest</strong> (sigmoid [0.85, 1.15]), and <strong>R6b seismic amplification</strong> (α=0.30, PGA-driven). A <strong>quantile calibration function</strong> then maps R_raw to standardised band space via piecewise linear interpolation at Q20=0.3585, Q60=0.4289, Q85=0.4907. Finally, 10,000 Monte Carlo iterations with σ=0.03 noise produce per-substation confidence intervals.</p>",
    section3_modifiers: "<h3>Risk Modifiers</h3><p>Five Japan-calibrated modifiers adjust the base score: <strong>R2 (Topology)</strong> applies ±0.05 based on OSM-derived network connectivity (mesh=−0.05, radial=+0.05); the three 50/60 Hz converter stations receive <em>is_bridge=1</em> forcing radial classification. <strong>R3 (Cohort)</strong> assigns age-bracket multipliers from METI equipment surveys: new (0–10y)=0.90, modern (11–20y)=0.95, mature (21–35y)=1.00, aging (36–50y)=1.08, old (50y+)=1.15. <strong>R5 (Markov Degradation)</strong> runs a 5-state Markov chain over 10-year horizon with transition rates boosted by κ_seismic (up to 1.12 for PGA≥0.30g) and κ_corrosion (up to 1.18 for C5 coastal zones in Kagoshima, Oita). <strong>R6a (CAIDI Rest)</strong> applies a sigmoid function: <code>clip(0.85 + 0.30/(1+exp(-3·(caidiRatio−1))), 0.85, 1.15)</code> where caidiRatio = prefecture CAIDI / national median. <strong>R6b (Seismic)</strong> computes <code>1 + 0.30 · log(1 + PGA/0.10g)</code> capped at 1.40, amplifying scores in high-PGA zones (Shizuoka 0.65g, Kochi 0.55g, Mie 0.55g, Wakayama 0.45g, Tokyo 0.45g).</p>",
    section4_montecarlo: "<h3>Monte Carlo Confidence</h3><p>Each substation’s risk score undergoes 10,000 Monte Carlo iterations using a seeded Mulberry32 PRNG for full reproducibility. In each iteration, Gaussian noise (σ=0.03) is added to the raw pre-calibration score, then the quantile calibration function maps the noisy R_raw to band space. The distribution of calibrated scores yields a robust median, 5th/95th percentile confidence interval, and band probability vector [P(Low), P(Medium), P(High), P(Critical)]. The engine reports fleet-wide statistics including mean confidence width, band transition sensitivity, and per-prefecture aggregated risk profiles. This approach captures both aleatoric uncertainty (measurement noise) and epistemic uncertainty (model parameter sensitivity). The seeded PRNG ensures identical results across runs, supporting regulatory audit requirements.</p>",
    section5_validation: "<h3>Validation &amp; Governance</h3><p>The Japan SSI pipeline is validated through: (1) <strong>Geographic coherence</strong> — highest-risk prefectures (Okinawa, Hokkaido, Shizuoka, Kochi) align with known grid vulnerability factors (island isolation, extreme climate, Nankai Trough exposure); (2) <strong>Band distribution</strong> conformance to §9 targets (Low 15–25%, Medium 35–45%, High 20–30%, Critical 5–15%); (3) <strong>Cross-country consistency</strong> — Japan’s median score (~0.38) reflects its high-reliability grid balanced against extreme natural hazard exposure; (4) <strong>Sensitivity analysis</strong> — R6b seismic modifier correctly produces 20–40% amplification in Nankai Trough prefectures; (5) <strong>Data lineage</strong> — all 35 sources are public, independently verifiable, with no proprietary dependencies. The methodology is fully open and reproducible through the browser-based engine.</p>"
  },

  // ── Institutional Mapping ──
  institutions: {
    energy_regulator: "Ministry of Economy, Trade and Industry (METI) / Agency for Natural Resources and Energy",
    grid_coordinator: "Organization for Cross-regional Coordination of Transmission Operators (OCCTO)",
    statistics: "Statistics Bureau of Japan (SBJ)",
    geological: "National Research Institute for Earth Science and Disaster Resilience (NIED)",
    meteorological: "Japan Meteorological Agency (JMA)",
    environment: "Ministry of the Environment (MOE)",
    cyber: "National center of Incident readiness and Strategy for Cybersecurity (NISC)",
    disaster: "Fire and Disaster Management Agency (FDMA)",
    health: "Ministry of Health, Labour and Welfare (MHLW)",
    transport: "Ministry of Land, Infrastructure, Transport and Tourism (MLIT)",
    digital: "Ministry of Internal Affairs and Communications (MIC)",
    central_bank: "Bank of Japan (BOJ)",
    nuclear: "Nuclear Regulation Authority (NRA)",
    space: "Japan Aerospace Exploration Agency (JAXA)"
  },

  // ── EPCO Territories (10 General Electricity Utilities) ──
  epco_territories: {
    "Hokkaido":  "Hokkaido Electric Power Company (HEPCO)",
    "Tohoku":    "Tohoku Electric Power Company",
    "TEPCO":     "Tokyo Electric Power Company Holdings (TEPCO)",
    "Chubu":     "Chubu Electric Power Company",
    "Hokuriku":  "Hokuriku Electric Power Company",
    "Kansai":    "Kansai Electric Power Company (KEPCO)",
    "Chugoku":   "Chugoku Electric Power Company",
    "Shikoku":   "Shikoku Electric Power Company",
    "Kyushu":    "Kyushu Electric Power Company",
    "Okinawa":   "Okinawa Electric Power Company"
  },

  // ── Japan Extension Block ──
  // Prefecture-level metadata with seismic, corrosion, frequency, and EPCO mapping
  japan: {
    prefectures: [
      {code:"01",name:"Hokkaido",epco:"Hokkaido",freq:50,pga:0.12,corr:"C3",caidi:22,pop:5224614,elderly:0.324,density:66,lat:43.06,lon:141.35},
      {code:"02",name:"Aomori",epco:"Tohoku",freq:50,pga:0.18,corr:"C3",caidi:18,pop:1237984,elderly:0.339,density:129,lat:40.82,lon:140.74},
      {code:"03",name:"Iwate",epco:"Tohoku",freq:50,pga:0.22,corr:"C2",caidi:19,pop:1210534,elderly:0.340,density:79,lat:39.70,lon:141.15},
      {code:"04",name:"Miyagi",epco:"Tohoku",freq:50,pga:0.38,corr:"C3",caidi:17,pop:2301996,elderly:0.282,density:316,lat:38.27,lon:140.87},
      {code:"05",name:"Akita",epco:"Tohoku",freq:50,pga:0.15,corr:"C2",caidi:20,pop:959502,elderly:0.381,density:83,lat:39.72,lon:140.10},
      {code:"06",name:"Yamagata",epco:"Tohoku",freq:50,pga:0.18,corr:"C2",caidi:19,pop:1068027,elderly:0.348,density:115,lat:38.24,lon:140.34},
      {code:"07",name:"Fukushima",epco:"Tohoku",freq:50,pga:0.35,corr:"C2",caidi:18,pop:1833152,elderly:0.327,density:133,lat:37.75,lon:140.47},
      {code:"08",name:"Ibaraki",epco:"TEPCO",freq:50,pga:0.32,corr:"C3",caidi:14,pop:2867009,elderly:0.300,density:470,lat:36.34,lon:140.45},
      {code:"09",name:"Tochigi",epco:"TEPCO",freq:50,pga:0.28,corr:"C2",caidi:14,pop:1933146,elderly:0.292,density:302,lat:36.57,lon:139.88},
      {code:"10",name:"Gunma",epco:"TEPCO",freq:50,pga:0.22,corr:"C2",caidi:14,pop:1939110,elderly:0.302,density:305,lat:36.39,lon:139.06},
      {code:"11",name:"Saitama",epco:"TEPCO",freq:50,pga:0.35,corr:"C3",caidi:12,pop:7344765,elderly:0.272,density:1932,lat:35.86,lon:139.65},
      {code:"12",name:"Chiba",epco:"TEPCO",freq:50,pga:0.40,corr:"C3",caidi:13,pop:6284480,elderly:0.282,density:1218,lat:35.60,lon:140.12},
      {code:"13",name:"Tokyo",epco:"TEPCO",freq:50,pga:0.45,corr:"C3",caidi:11,pop:14047594,elderly:0.234,density:6410,lat:35.68,lon:139.69},
      {code:"14",name:"Kanagawa",epco:"TEPCO",freq:50,pga:0.42,corr:"C3",caidi:12,pop:9237337,elderly:0.258,density:3824,lat:35.45,lon:139.64},
      {code:"15",name:"Niigata",epco:"Tohoku",freq:50,pga:0.20,corr:"C3",caidi:18,pop:2201272,elderly:0.332,density:175,lat:37.90,lon:139.02},
      {code:"16",name:"Toyama",epco:"Hokuriku",freq:60,pga:0.18,corr:"C2",caidi:16,pop:1034814,elderly:0.328,density:244,lat:36.70,lon:137.21},
      {code:"17",name:"Ishikawa",epco:"Hokuriku",freq:60,pga:0.25,corr:"C3",caidi:17,pop:1132526,elderly:0.310,density:270,lat:36.59,lon:136.63},
      {code:"18",name:"Fukui",epco:"Hokuriku",freq:60,pga:0.20,corr:"C2",caidi:16,pop:766863,elderly:0.318,density:183,lat:36.07,lon:136.22},
      {code:"19",name:"Yamanashi",epco:"TEPCO",freq:50,pga:0.30,corr:"C1",caidi:15,pop:809974,elderly:0.318,density:182,lat:35.66,lon:138.57},
      {code:"20",name:"Nagano",epco:"Chubu",freq:60,pga:0.22,corr:"C1",caidi:15,pop:2048011,elderly:0.332,density:151,lat:36.23,lon:138.18},
      {code:"21",name:"Gifu",epco:"Chubu",freq:60,pga:0.25,corr:"C1",caidi:14,pop:1978742,elderly:0.312,density:186,lat:35.39,lon:136.72},
      {code:"22",name:"Shizuoka",epco:"Chubu",freq:60,pga:0.65,corr:"C3",caidi:14,pop:3633202,elderly:0.304,density:467,lat:34.98,lon:138.38},
      {code:"23",name:"Aichi",epco:"Chubu",freq:60,pga:0.40,corr:"C3",caidi:13,pop:7542415,elderly:0.260,density:1460,lat:35.18,lon:136.91},
      {code:"24",name:"Mie",epco:"Chubu",freq:60,pga:0.55,corr:"C3",caidi:15,pop:1770254,elderly:0.310,density:307,lat:34.73,lon:136.51},
      {code:"25",name:"Shiga",epco:"Kansai",freq:60,pga:0.30,corr:"C2",caidi:13,pop:1413610,elderly:0.272,density:352,lat:35.00,lon:135.87},
      {code:"26",name:"Kyoto",epco:"Kansai",freq:60,pga:0.32,corr:"C3",caidi:13,pop:2578087,elderly:0.298,density:560,lat:35.01,lon:135.77},
      {code:"27",name:"Osaka",epco:"Kansai",freq:60,pga:0.38,corr:"C3",caidi:12,pop:8837685,elderly:0.278,density:4631,lat:34.69,lon:135.50},
      {code:"28",name:"Hyogo",epco:"Kansai",freq:60,pga:0.35,corr:"C3",caidi:13,pop:5465002,elderly:0.298,density:651,lat:34.69,lon:135.18},
      {code:"29",name:"Nara",epco:"Kansai",freq:60,pga:0.30,corr:"C1",caidi:14,pop:1324473,elderly:0.322,density:359,lat:34.69,lon:135.83},
      {code:"30",name:"Wakayama",epco:"Kansai",freq:60,pga:0.45,corr:"C3",caidi:15,pop:922584,elderly:0.342,density:195,lat:34.23,lon:135.17},
      {code:"31",name:"Tottori",epco:"Chugoku",freq:60,pga:0.18,corr:"C2",caidi:17,pop:553407,elderly:0.332,density:158,lat:35.50,lon:134.24},
      {code:"32",name:"Shimane",epco:"Chugoku",freq:60,pga:0.15,corr:"C2",caidi:18,pop:671126,elderly:0.352,density:100,lat:35.47,lon:133.05},
      {code:"33",name:"Okayama",epco:"Chugoku",freq:60,pga:0.22,corr:"C3",caidi:15,pop:1888432,elderly:0.302,density:266,lat:34.66,lon:133.93},
      {code:"34",name:"Hiroshima",epco:"Chugoku",freq:60,pga:0.20,corr:"C3",caidi:15,pop:2799702,elderly:0.292,density:330,lat:34.40,lon:132.46},
      {code:"35",name:"Yamaguchi",epco:"Chugoku",freq:60,pga:0.15,corr:"C3",caidi:16,pop:1342059,elderly:0.348,density:220,lat:34.19,lon:131.47},
      {code:"36",name:"Tokushima",epco:"Shikoku",freq:60,pga:0.35,corr:"C3",caidi:17,pop:719559,elderly:0.348,density:173,lat:34.07,lon:134.56},
      {code:"37",name:"Kagawa",epco:"Shikoku",freq:60,pga:0.28,corr:"C3",caidi:16,pop:950244,elderly:0.328,density:506,lat:34.34,lon:134.04},
      {code:"38",name:"Ehime",epco:"Shikoku",freq:60,pga:0.28,corr:"C3",caidi:17,pop:1334841,elderly:0.338,density:235,lat:33.84,lon:132.77},
      {code:"39",name:"Kochi",epco:"Shikoku",freq:60,pga:0.55,corr:"C3",caidi:18,pop:691527,elderly:0.362,density:97,lat:33.56,lon:133.53},
      {code:"40",name:"Fukuoka",epco:"Kyushu",freq:60,pga:0.22,corr:"C3",caidi:14,pop:5135214,elderly:0.278,density:1031,lat:33.59,lon:130.40},
      {code:"41",name:"Saga",epco:"Kyushu",freq:60,pga:0.20,corr:"C2",caidi:15,pop:811442,elderly:0.318,density:333,lat:33.25,lon:130.30},
      {code:"42",name:"Nagasaki",epco:"Kyushu",freq:60,pga:0.18,corr:"C3",caidi:16,pop:1312317,elderly:0.338,density:318,lat:32.74,lon:129.87},
      {code:"43",name:"Kumamoto",epco:"Kyushu",freq:60,pga:0.35,corr:"C3",caidi:15,pop:1738301,elderly:0.308,density:235,lat:32.79,lon:130.74},
      {code:"44",name:"Oita",epco:"Kyushu",freq:60,pga:0.30,corr:"C5",caidi:16,pop:1123852,elderly:0.338,density:177,lat:33.24,lon:131.61},
      {code:"45",name:"Miyazaki",epco:"Kyushu",freq:60,pga:0.35,corr:"C3",caidi:16,pop:1069576,elderly:0.332,density:138,lat:31.91,lon:131.42},
      {code:"46",name:"Kagoshima",epco:"Kyushu",freq:60,pga:0.30,corr:"C5",caidi:16,pop:1588256,elderly:0.332,density:172,lat:31.56,lon:130.56},
      {code:"47",name:"Okinawa",epco:"Okinawa",freq:60,pga:0.10,corr:"C3",caidi:32,pop:1467480,elderly:0.228,density:644,lat:26.34,lon:127.80}
    ],
    frequencyBoundary: "Itoigawa-Shizuoka Tectonic Line (ISTL) — 50 Hz east / 60 Hz west",
    converterStations: ["Shin-Shinano (600 MW)", "Sakuma (300 MW)", "Higashi-Shimizu (300 MW)"],
    totalCapacity_MW: 1200,
    substationCount: 6003,
    osmVerified: true
  }

};
