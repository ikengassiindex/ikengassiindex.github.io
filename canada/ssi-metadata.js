// SSI v4.0.2 — Canada Metadata
// Generated 2026-03-13 by Ikenga Project

window.SSI_METADATA = {

  country: "Canada",
  country_code: "CA",
  flag: "\u{1F1E8}\u{1F1E6}",

  // ── Regional Labels ──
  labels: {
    level1: "Province / Territory",
    level1_plural: "Provinces & Territories",
    level2: "Census Division",
    level2_plural: "Census Divisions",
    ranking_tab: "Provincial Ranking",
    comparison_tab: "Census Division Comparison"
  },

  // ── Data Source Registry (35+ verified sources) ──
  dataSources: [
    { id: "D1",  name: "CER Provincial/Territorial Energy Profiles", agency: "Canada Energy Regulator (CER)", url: "https://www.cer-rec.gc.ca/en/data-analysis/energy-markets/provincial-territorial-energy-profiles/", feeds: "Generation, consumption, capacity by province", freq: "Annual", resolution: "Provincial", status: "LIVE" },
    { id: "D2",  name: "CER/NRCan Renewable Energy Registry", agency: "CER / Natural Resources Canada", url: "https://www.nrcan.gc.ca/energy/renewable-electricity/", feeds: "T1 (DER capacity, RE installations)", freq: "Quarterly", resolution: "Provincial / municipal", status: "LIVE" },
    { id: "D3",  name: "Statistics Canada CANSIM Electricity Tables", agency: "Statistics Canada", url: "https://www150.statcan.gc.ca/n1/en/type/data", feeds: "C1-C4 base data, S1 saturation KPI", freq: "Annual", resolution: "Provincial", status: "LIVE" },
    { id: "D4",  name: "ECCC Historical Climate Data", agency: "Environment and Climate Change Canada", url: "https://climate.weather.gc.ca/", feeds: "I1-I3 IRI climate metrics (snow/ice, tree-fall, heat-wave)", freq: "Daily", resolution: "Station + gridded", status: "LIVE" },
    { id: "D5",  name: "Statistics Canada CIS (Canadian Income Survey)", agency: "Statistics Canada", url: "https://www150.statcan.gc.ca/n1/en/catalogue/75F0002M", feeds: "R3 Energy poverty (V_socio)", freq: "Annual", resolution: "Provincial + CD estimates", status: "LIVE" },
    { id: "D6",  name: "CER + Provincial Regulator Reliability Reports", agency: "CER / OEB / AUC / BCUC / Regie QC", url: "https://www.oeb.ca/utility-performance/electricity-distributor-scorecard", feeds: "R6a CAIDI, SAIDI/SAIFI", freq: "Annual", resolution: "Utility service territory", status: "LIVE" },
    { id: "D7",  name: "OSM Power Infrastructure", agency: "OpenStreetMap Contributors", url: "https://overpass-turbo.eu/", feeds: "R4 Graph topology, ~20,000 substations", freq: "Live (Overpass)", resolution: "Node/edge level", status: "LIVE" },
    { id: "D8",  name: "NRCan/GSC NBCC 2020 Seismic Hazard (CanadaSHM6)", agency: "Natural Resources Canada / Geological Survey of Canada", url: "https://www.earthquakescanada.nrcan.gc.ca/hazard-alea/", feeds: "R6b PGA seismic (2%/50yr return)", freq: "Static", resolution: "Grid point (~10 km) + CD", status: "LIVE" },
    { id: "D9",  name: "Transport Canada ZEV + NRCan EV Charging", agency: "Transport Canada / NRCan", url: "https://tc.canada.ca/en/road-transportation/innovative-technologies/zero-emission-vehicles", feeds: "T1 EV/heat pump penetration", freq: "Annual", resolution: "Provincial / municipal", status: "LIVE" },
    { id: "D10", name: "Copernicus CDS / ERA5", agency: "ECMWF / Copernicus", url: "https://cds.climate.copernicus.eu/", feeds: "R2 Climate trajectory (CMIP6 SSP2-4.5)", freq: "Static / Hourly", resolution: "0.25deg (~25 km)", status: "LIVE" },
    { id: "D11", name: "Open-Meteo Weather API", agency: "Open-Meteo", url: "https://open-meteo.com/", feeds: "T_amb (ambient temperature for I5 thermal proxy)", freq: "Hourly", resolution: "~1 km", status: "LIVE" },
    { id: "D12", name: "Statistics Canada Census of Population", agency: "Statistics Canada", url: "https://www12.statcan.gc.ca/census-recensement/index-eng.cfm", feeds: "Pop density, aging, households, demographics", freq: "5-year", resolution: "CD / CSD", status: "LIVE" },
    { id: "D13", name: "Statistics Canada Business Register (CANSIM)", agency: "Statistics Canada", url: "https://www150.statcan.gc.ca/n1/en/type/data", feeds: "E2 beta weights (industry mix)", freq: "Annual", resolution: "CD x NAICS", status: "LIVE" },
    { id: "D14", name: "Bank of Canada / Statistics Canada Macro", agency: "Bank of Canada", url: "https://www.bankofcanada.ca/rates/", feeds: "VoLL/E2 beta + macro indicators", freq: "Quarterly", resolution: "Provincial / CD", status: "LIVE" },
    { id: "D15", name: "CRA Tax Statistics", agency: "Canada Revenue Agency", url: "https://www.canada.ca/en/revenue-agency/programs/about-canada-revenue-agency-cra/income-statistics-gst-hst-statistics.html", feeds: "Income per capita, fiscal capacity", freq: "Annual", resolution: "CD (~293)", status: "LIVE" },
    { id: "D16", name: "ISED Digital Economy + BDC Startup Data", agency: "Innovation, Science and Economic Development Canada", url: "https://ised-isde.canada.ca/site/digital-economy/en", feeds: "R7 Innovation composite, startup density, digital readiness", freq: "Annual", resolution: "Provincial / CD", status: "LIVE" },
    { id: "D17", name: "ECCC AQHI + NPRI", agency: "Environment and Climate Change Canada", url: "https://www.canada.ca/en/environment-climate-change/services/air-quality-health-index.html", feeds: "I8 Air quality corrosion proxy (PM2.5, NO2)", freq: "Annual", resolution: "Station + CD", status: "LIVE" },
    { id: "D18", name: "Provincial ISOs (IESO, AESO, NB SO)", agency: "IESO / AESO / NB Power", url: "https://www.ieso.ca/en/Power-Data", feeds: "T1 generation by type, DER variability", freq: "Weekly", resolution: "Zone / bidding area", status: "LIVE" },
    { id: "D19", name: "OEB Utility Scorecards (Ontario)", agency: "Ontario Energy Board", url: "https://www.oeb.ca/utility-performance/electricity-distributor-scorecard", feeds: "C1-C4 interruption data, detailed SAIDI/SAIFI", freq: "Annual", resolution: "LDC level (~60 distributors)", status: "LIVE" },
    { id: "D20", name: "Hydro-Quebec / BC Hydro / Hydro One Annual Reports", agency: "Provincial Crown Corporations", url: "https://www.hydroquebec.com/about/financial-results/annual-report.html", feeds: "C1-C4, voltage, asset condition", freq: "Annual", resolution: "Regional / CD-level", status: "LIVE" },
    { id: "D21", name: "Public Safety Canada / NRCan GeoScan", agency: "Public Safety Canada / NRCan", url: "https://geoscan.nrcan.gc.ca/", feeds: "I9 Flood/landslide risk, emergency management", freq: "Static/Annual", resolution: "CD + municipal", status: "LIVE" },
    { id: "D22", name: "CIHI Healthcare Data", agency: "Canadian Institute for Health Information", url: "https://www.cihi.ca/en", feeds: "Healthcare density (hospital proximity)", freq: "Annual", resolution: "Health region / CD", status: "LIVE" },
    { id: "D23", name: "IEEE C57.91 Thermal Model", agency: "IEEE Standards", url: "https://standards.ieee.org/", feeds: "I5 Transformer temp proxy", freq: "Standard", resolution: "Asset-level", status: "LIVE" },
    { id: "D24", name: "ISO 9223 Corrosion Classification", agency: "ISO / Derived from ECCC+NRCan", url: "https://www.iso.org/standard/53500.html", feeds: "Corrosion class C1-C4 for Markov model", freq: "Derived", resolution: "CD-level", status: "LIVE" },
    { id: "D25", name: "CIGRE TB 761 — Markov Degradation", agency: "CIGRE", url: "https://www.cigre.org/", feeds: "5-state transition matrices, Markov model calibration", freq: "Standard", resolution: "Cohort-level", status: "LIVE" },
    { id: "D26", name: "Statistics Canada Interprovincial Migration", agency: "Statistics Canada", url: "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710004501", feeds: "R3 Migration amplifier", freq: "Quarterly", resolution: "Provincial", status: "LIVE" },
    { id: "D27", name: "Provincial Microgeneration Registries", agency: "AUC (AB), OEB (ON), BCUC (BC)", url: "https://www.auc.ab.ca/", feeds: "T1 DER_ratio (micro-gen capacity)", freq: "Annual", resolution: "Municipal / utility", status: "LIVE" },
    { id: "D28", name: "CSE Cyber Threat Reports", agency: "Communications Security Establishment", url: "https://www.cse-cst.gc.ca/en/", feeds: "R7 Cyber threat intelligence (qualitative)", freq: "Annual", resolution: "National", status: "LIVE" },
    { id: "D29", name: "NRCan/GSC Geohazard Database", agency: "NRCan / GSC", url: "https://www.nrcan.gc.ca/science-and-data/science-and-research/natural-hazards/", feeds: "I9 Hydrogeological risk, landslide susceptibility", freq: "Static", resolution: "CD + municipal", status: "LIVE" },
    { id: "D30", name: "Statistics Canada LFS (Labour Force Survey)", agency: "Statistics Canada", url: "https://www.statcan.gc.ca/en/survey/household/3701", feeds: "E2 unemployment, industry employment shares", freq: "Monthly", resolution: "Provincial / CMA", status: "LIVE" },
    { id: "D31", name: "NRCan Energy Fact Book", agency: "Natural Resources Canada", url: "https://www.nrcan.gc.ca/science-data/data-analysis/energy-data-analysis/energy-facts/", feeds: "S1 generation/consumption context", freq: "Annual", resolution: "Provincial", status: "LIVE" },
    { id: "D32", name: "ERA5 Heat/Ice Days (Copernicus)", agency: "ECMWF / Copernicus", url: "https://cds.climate.copernicus.eu/", feeds: "Markov kappa_climate (heat_days, ice_days)", freq: "Derived annual", resolution: "0.25deg -> CD", status: "LIVE" },
    { id: "D33", name: "CMHC Housing Data", agency: "Canada Mortgage and Housing Corporation", url: "https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research", feeds: "Socio-economic context (housing age, energy efficiency)", freq: "Annual", resolution: "CMA / CD", status: "LIVE" },
    { id: "D34", name: "Statistics Canada HRST Education Tables", agency: "Statistics Canada", url: "https://www150.statcan.gc.ca/n1/en/type/data", feeds: "E2 Innovation enrichment (HRST %)", freq: "Annual", resolution: "Provincial / CD", status: "LIVE" },
    { id: "D35", name: "IEC 60076 / IEEE 80 Engineering Standards", agency: "IEC / IEEE", url: "https://www.iec.ch/", feeds: "I5/I6 voltage regulation + grounding proxies", freq: "Standard", resolution: "Asset-level", status: "LIVE" }
  ],

  // ── Methodology Sections ──
  methodology: {
    section1_components: "<h3>Six Risk Components</h3><p>The SSI v4.0.2 evaluates each substation across six weighted risk components: <strong>Continuity (C, 30%)</strong> measures outage frequency and duration using CER and provincial regulator reliability reports (OEB Scorecards, AUC Performance Reports, Hydro-Quebec Annual Reports). <strong>Voltage Quality (V, 10%)</strong> captures severity-weighted voltage dips from provincial regulatory filings and CSA C235 compliance data. <strong>Infrastructure (I, 25%)</strong> combines 9 sub-metrics including ECCC-derived climate risk indices (snow/ice storms, heat waves, tree-fall), network density from OSM, thermal stress (IEEE C57.91), load stress, air quality corrosion (ECCC AQHI + ISO 9223), and hydrogeological risk (NRCan/GSC). <strong>Economic (E, 10%)</strong> measures regulatory penalties (CER/provincial) and productivity loss coefficients calibrated from Statistics Canada Business Register and Bank of Canada research. <strong>Saturation (S, 20%)</strong> evaluates generation-to-consumption balance using CER electricity tables and Dimovski breakpoints. <strong>Energy Transition (T, 5%)</strong> is new in v4.0 and measures DER stress via CER/NRCan renewable energy registry, provincial ISO generation data, and Transport Canada ZEV statistics.</p>",

    section2_modifiers: "<h3>Eight Risk Modifiers</h3><p>Beyond the six base components, SSI applies multiplicative modifiers: <strong>R2 Adaptive IRI + Climate Trajectory</strong> uses CMIP6 SSP2-4.5 projections from Copernicus CDS to forward-adjust climate risk weights. <strong>R3 Consequence Multiplier</strong> incorporates population, load, and energy poverty vulnerability from Statistics Canada CIS data, with Atlantic provinces (Newfoundland EP_rate 13.7%) receiving higher consequence weights. <strong>R4 Graph Criticality</strong> uses NetworkX analysis of Canada's ~20,000 OSM substations, with betweenness centrality and Tarjan bridge detection — particularly impactful for northern Canada's radial feed networks. <strong>R6a Restoration Speed</strong> uses CAIDI from CER/provincial regulator reports. <strong>R6b Seismic Hazard</strong> applies NRCan/GSC NBCC 2020 (CanadaSHM6) PGA data — Vancouver/Victoria at PGA 0.45g receive 18% amplification (Cascadia subduction zone), Charlevoix at 0.35g receives 13.5%. <strong>R7 Cyber-Exposure</strong> uses ISED digital readiness scores + CSE cyber threat intelligence as a proxy.</p>",

    section3_normalisation: "<h3>Normalisation Methods</h3><p>Four normalisation methods are applied: <strong>Method A</strong> (fleet percentile, robust) for C1-C2 continuity metrics; <strong>Method B</strong> (fleet percentile, standard) for V, I4-I9, E1, S1, T1; <strong>Method C</strong> (bounded rescaling) for I1-I3 climate indices [0, 0.30] and E2; <strong>Method D</strong> (categorical mapping) for S2 reverse power flow and S3 criticality class. Inversion is applied to I4 (RTN density) and I6 (substation density) where higher values indicate better resilience.</p>",

    section4_montecarlo: "<h3>Monte Carlo Uncertainty Engine</h3><p>10,000 iterations per substation using a Gaussian copula with 20x20 empirical correlation matrix. Uncertainty sources include measurement error (sigma_meas 5-28%), spatial disaggregation (sigma_spatial 4-18%), and data staleness (sigma_staleness up to 35% for stale voltage data). Output includes R_median, asymmetric confidence intervals [R_P5, R_P95], skewness, and P_critical (tail-risk probability). For Canada, the dominant uncertainty source is voltage quality data (V) due to variable reporting standards across provincial regulators.</p>",

    section5_validation: "<h3>Validation Framework</h3><p>Internal consistency checks include the expected east-west gradient (Atlantic provinces higher risk than Prairie/Western), IRI-climate coherence (I1 peaks in Quebec/Ontario for ice, I3 in southern Ontario/BC interior for heat), and ratio test (R_worst/R_best >= 5x). External validation targets include OEB utility scorecards (r > 0.70 with C component), CER infrastructure investment plans (r > 0.50 with R), NRCan/GSC seismic hazard maps (r > 0.30 with I), and Statistics Canada CIS energy poverty data (r > 0.85 with V_socio).</p>",

    section6_canada_specific: "<h3>Canada-Specific Features</h3><p>Canada's grid presents unique characteristics: <strong>Hydroelectric dominance</strong> (60% of generation), creating long transmission lines from remote generation to load centres. <strong>Extreme cold</strong> with ice storms, freezing rain, and cold snap risk as primary I-component drivers — the 1998 Quebec/Ontario ice storm (3.4M customers, 33-day outages) demonstrates extreme vulnerability. <strong>Cascadia seismic zone</strong> in SW British Columbia (potential M9.0 megathrust). <strong>Provincial jurisdiction</strong> over electricity regulation creates 13 different data regimes. <strong>North-south disparity</strong> with northern/remote communities on diesel microgrids. <strong>Crown corporations</strong> as dominant provincial utilities (Hydro-Quebec, BC Hydro, SaskPower, Manitoba Hydro) providing generally more transparent data. The Markov 5-state degradation model is calibrated with NRCan/GSC seismic, ERA5 climate, and ISO 9223 corrosion data specific to Canadian conditions.</p>"
  },

  // ── Institutional Mapping ──
  institutions: {
    federal_regulator: "Canada Energy Regulator (CER)",
    statistics: "Statistics Canada",
    geological: "Natural Resources Canada / Geological Survey of Canada (NRCan/GSC)",
    environment: "Environment and Climate Change Canada (ECCC)",
    innovation: "Innovation, Science and Economic Development Canada (ISED)",
    cyber: "Communications Security Establishment (CSE)",
    housing: "Canada Mortgage and Housing Corporation (CMHC)",
    health: "Canadian Institute for Health Information (CIHI)",
    transport: "Transport Canada",
    revenue: "Canada Revenue Agency (CRA)",
    central_bank: "Bank of Canada",
    safety: "Public Safety Canada"
  },

  // ── Provincial Regulators ──
  provincial_regulators: {
    ON: "Ontario Energy Board (OEB)",
    QC: "Regie de l'energie du Quebec",
    BC: "BC Utilities Commission (BCUC)",
    AB: "Alberta Utilities Commission (AUC)",
    SK: "SaskPower (Crown Corporation)",
    MB: "Manitoba Public Utilities Board",
    NB: "New Brunswick Energy and Utilities Board",
    NS: "Nova Scotia Utility and Review Board (NSUARB)",
    NL: "Board of Commissioners of Public Utilities (PUB NL)",
    PE: "Island Regulatory and Appeals Commission (IRAC)",
    YT: "Yukon Utilities Board",
    NT: "Northwest Territories Public Utilities Board",
    NU: "Utility Rates Review Council of Nunavut"
  }
};

/* ── Methodology page data arrays (v4.0.2) ── */

window.SSI_METADATA.COMPONENTS = [
  {
    "id": "C",
    "name": "Continuity",
    "weight": 0.3,
    "color": "#941914",
    "desc": "Outage frequency and duration metrics for Canadian substations",
    "metrics": [
      {
        "id": "SAIDI",
        "name": "SAIDI",
        "intra": 0.4,
        "global": 0.3,
        "norm": "min-max",
        "source": "Provincial utilities",
        "desc": "System Average Interruption Duration Index"
      },
      {
        "id": "SAIFI",
        "name": "SAIFI",
        "intra": 0.3,
        "global": 0.25,
        "norm": "min-max",
        "source": "Provincial utilities",
        "desc": "System Average Interruption Frequency Index"
      },
      {
        "id": "CAIDI",
        "name": "CAIDI",
        "intra": 0.15,
        "global": 0.2,
        "norm": "min-max",
        "source": "Provincial utilities",
        "desc": "Customer Average Interruption Duration Index"
      },
      {
        "id": "MAIFI",
        "name": "MAIFI",
        "intra": 0.15,
        "global": 0.25,
        "norm": "min-max",
        "source": "Provincial utilities",
        "desc": "Momentary Average Interruption Frequency Index"
      }
    ]
  },
  {
    "id": "V",
    "name": "Voltage Quality",
    "weight": 0.1,
    "color": "#b8863a",
    "desc": "Voltage regulation compliance at Canadian substations",
    "metrics": [
      {
        "id": "V_reg",
        "name": "Voltage regulation",
        "intra": 1,
        "global": 1,
        "norm": "min-max",
        "source": "CER / Provincial utilities",
        "desc": "Voltage deviation from nominal at substation bus"
      }
    ]
  },
  {
    "id": "I",
    "name": "Infrastructure",
    "weight": 0.25,
    "color": "#5d8563",
    "desc": "Physical asset condition and topology metrics",
    "metrics": [
      {
        "id": "age",
        "name": "Asset age",
        "intra": 0.15,
        "global": 0.15,
        "norm": "min-max",
        "source": "CER filings",
        "desc": "Weighted average age of transformers and breakers"
      },
      {
        "id": "cap_util",
        "name": "Capacity utilisation",
        "intra": 0.2,
        "global": 0.2,
        "norm": "min-max",
        "source": "Provincial utilities",
        "desc": "Peak load as percentage of rated capacity"
      },
      {
        "id": "n_minus_1",
        "name": "N-1 compliance",
        "intra": 0.15,
        "global": 0.15,
        "norm": "binary",
        "source": "CER / NERC",
        "desc": "N-1 contingency compliance status"
      },
      {
        "id": "km_line",
        "name": "Line length",
        "intra": 0.1,
        "global": 0.1,
        "norm": "min-max",
        "source": "NRCan",
        "desc": "Total HV/MV line km feeding the substation"
      },
      {
        "id": "graph_deg",
        "name": "Graph degree",
        "intra": 0.1,
        "global": 0.1,
        "norm": "min-max",
        "source": "Topology model",
        "desc": "Number of adjacent nodes in the grid graph"
      },
      {
        "id": "graph_bc",
        "name": "Betweenness centrality",
        "intra": 0.1,
        "global": 0.1,
        "norm": "min-max",
        "source": "Topology model",
        "desc": "Betweenness centrality percentile in grid graph"
      },
      {
        "id": "seismic",
        "name": "Seismic zone",
        "intra": 0.05,
        "global": 0.05,
        "norm": "ordinal",
        "source": "NRCan seismic data",
        "desc": "Seismic hazard zone and PGA value"
      },
      {
        "id": "corrosion",
        "name": "Corrosion class",
        "intra": 0.05,
        "global": 0.05,
        "norm": "ordinal",
        "source": "Environment Canada",
        "desc": "ISO 9223 atmospheric corrosion classification"
      },
      {
        "id": "flood",
        "name": "Flood risk",
        "intra": 0.1,
        "global": 0.1,
        "norm": "ordinal",
        "source": "NRCan flood maps",
        "desc": "Flood risk zone classification",
        "adaptive": true
      }
    ]
  },
  {
    "id": "E",
    "name": "Economic",
    "weight": 0.1,
    "color": "#aa4234",
    "desc": "Socio-economic context of substation service area",
    "metrics": [
      {
        "id": "GDP_pc",
        "name": "GDP per capita",
        "intra": 0.5,
        "global": 0.5,
        "norm": "min-max",
        "source": "Statistics Canada",
        "desc": "Provincial GDP per capita"
      },
      {
        "id": "unemployment",
        "name": "Unemployment rate",
        "intra": 0.5,
        "global": 0.5,
        "norm": "min-max-inv",
        "source": "Statistics Canada",
        "desc": "Provincial unemployment rate"
      }
    ]
  },
  {
    "id": "S",
    "name": "Saturation",
    "weight": 0.2,
    "color": "#8e44ad",
    "desc": "DER penetration and hosting capacity stress",
    "metrics": [
      {
        "id": "DER_MW",
        "name": "DER capacity",
        "intra": 0.4,
        "global": 0.35,
        "norm": "min-max",
        "source": "CER / Provincial utilities",
        "desc": "Total installed DER capacity in MW"
      },
      {
        "id": "DER_ratio",
        "name": "DER stress ratio",
        "intra": 0.35,
        "global": 0.35,
        "norm": "min-max",
        "source": "Derived",
        "desc": "DER capacity as fraction of substation rating"
      },
      {
        "id": "EV_pct",
        "name": "EV penetration",
        "intra": 0.25,
        "global": 0.3,
        "norm": "min-max",
        "source": "Statistics Canada / IEA",
        "desc": "EV share in substation service area"
      }
    ]
  },
  {
    "id": "T",
    "name": "Energy Transition",
    "weight": 0.05,
    "color": "#0e7490",
    "desc": "Transition readiness and Markov chain risk",
    "metrics": [
      {
        "id": "markov",
        "name": "Markov risk",
        "intra": 1,
        "global": 1,
        "norm": "min-max",
        "source": "SSI model",
        "desc": "Markov chain expected time to critical state",
        "isNew": true,
        "submetrics": [
          {
            "id": "markov_risk",
            "name": "Risk probability",
            "desc": "Stationary failure probability"
          },
          {
            "id": "ETTC",
            "name": "ETTC",
            "desc": "Expected Time To Critical (years)"
          }
        ]
      }
    ]
  }
];

window.SSI_METADATA.NORM_METHODS = [
  {
    "id": "minmax",
    "name": "Min-Max",
    "formula": "(x - min) / (max - min)",
    "applies": "Most continuous metrics"
  },
  {
    "id": "minmax_inv",
    "name": "Min-Max Inverse",
    "formula": "1 - (x - min) / (max - min)",
    "applies": "Metrics where lower is worse"
  },
  {
    "id": "binary",
    "name": "Binary",
    "formula": "1 if compliant, 0 otherwise",
    "applies": "N-1 compliance"
  },
  {
    "id": "ordinal",
    "name": "Ordinal Mapping",
    "formula": "Lookup table to [0,1]",
    "applies": "Seismic zone, corrosion class, flood risk"
  }
];

window.SSI_METADATA.DATA_LAYERS = [
  {
    "id": "substations",
    "name": "Substations",
    "vars": [
      "name",
      "lat",
      "lon",
      "voltage_kV",
      "capacity_MVA"
    ],
    "status": "live",
    "sources": [
      "CER",
      "Provincial utilities"
    ]
  },
  {
    "id": "outage",
    "name": "Outage metrics",
    "vars": [
      "SAIDI",
      "SAIFI",
      "CAIDI",
      "MAIFI"
    ],
    "status": "live",
    "sources": [
      "Provincial utilities"
    ]
  },
  {
    "id": "voltage",
    "name": "Voltage quality",
    "vars": [
      "V_reg",
      "V_min",
      "V_max"
    ],
    "status": "live",
    "sources": [
      "CER"
    ]
  },
  {
    "id": "asset",
    "name": "Asset registry",
    "vars": [
      "age",
      "type",
      "manufacturer",
      "rating_MVA"
    ],
    "status": "live",
    "sources": [
      "CER filings"
    ]
  },
  {
    "id": "topology",
    "name": "Grid topology",
    "vars": [
      "graph_degree",
      "betweenness",
      "clustering"
    ],
    "status": "live",
    "sources": [
      "SSI topology model"
    ]
  },
  {
    "id": "economic",
    "name": "Socio-economic",
    "vars": [
      "GDP_pc",
      "unemployment",
      "population",
      "energy_poverty"
    ],
    "status": "live",
    "sources": [
      "Statistics Canada"
    ]
  },
  {
    "id": "DER",
    "name": "DER penetration",
    "vars": [
      "solar_MW",
      "wind_MW",
      "storage_MW",
      "DER_ratio"
    ],
    "status": "live",
    "sources": [
      "CER",
      "Provincial utilities"
    ]
  },
  {
    "id": "EV",
    "name": "EV adoption",
    "vars": [
      "EV_count",
      "EV_pct",
      "charger_count"
    ],
    "status": "live",
    "sources": [
      "Statistics Canada",
      "IEA"
    ]
  },
  {
    "id": "seismic",
    "name": "Seismic hazard",
    "vars": [
      "zone",
      "PGA_g",
      "fault_distance_km"
    ],
    "status": "live",
    "sources": [
      "NRCan"
    ]
  },
  {
    "id": "climate",
    "name": "Climate exposure",
    "vars": [
      "corrosion_class",
      "flood_zone",
      "ice_storm_risk"
    ],
    "status": "live",
    "sources": [
      "Environment Canada",
      "NRCan"
    ]
  },
  {
    "id": "markov",
    "name": "Markov model",
    "vars": [
      "risk_prob",
      "ETTC_years",
      "steady_state"
    ],
    "status": "live",
    "sources": [
      "SSI engine"
    ]
  }
];

window.SSI_METADATA.DATA_SOURCES = [
  {
    "id": "DS01",
    "name": "Statistics Canada",
    "url": "https://www.statcan.gc.ca",
    "freq": "Quarterly",
    "res": "Provincial",
    "vars": [
      "GDP_pc",
      "unemployment",
      "population",
      "CPI"
    ],
    "category": "Economic",
    "feeds": [
      "E",
      "I"
    ]
  },
  {
    "id": "DS02",
    "name": "Canada Energy Regulator (CER)",
    "url": "https://www.cer-rec.gc.ca",
    "freq": "Annual",
    "res": "Utility",
    "vars": [
      "outage_reports",
      "asset_filings",
      "pipeline_data"
    ],
    "category": "Regulatory",
    "feeds": [
      "C",
      "V",
      "I"
    ]
  },
  {
    "id": "DS03",
    "name": "Natural Resources Canada (NRCan)",
    "url": "https://www.nrcan.gc.ca",
    "freq": "Annual",
    "res": "National",
    "vars": [
      "seismic_hazard",
      "flood_maps",
      "energy_stats"
    ],
    "category": "Geoscience",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS04",
    "name": "Environment Canada",
    "url": "https://www.canada.ca/en/environment-climate-change.html",
    "freq": "Daily",
    "res": "Station",
    "vars": [
      "temperature",
      "precipitation",
      "wind",
      "ice_storm"
    ],
    "category": "Climate",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS05",
    "name": "Hydro-Quebec",
    "url": "https://www.hydroquebec.com",
    "freq": "Monthly",
    "res": "Substation",
    "vars": [
      "SAIDI",
      "SAIFI",
      "load",
      "DER_MW"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "V",
      "S"
    ]
  },
  {
    "id": "DS06",
    "name": "Ontario IESO",
    "url": "https://www.ieso.ca",
    "freq": "Hourly",
    "res": "Zone",
    "vars": [
      "demand",
      "generation",
      "price",
      "DER"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "S",
      "E"
    ]
  },
  {
    "id": "DS07",
    "name": "BC Hydro",
    "url": "https://www.bchydro.com",
    "freq": "Monthly",
    "res": "Region",
    "vars": [
      "SAIDI",
      "SAIFI",
      "capacity",
      "renewables"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "V",
      "S"
    ]
  },
  {
    "id": "DS08",
    "name": "Alberta AESO",
    "url": "https://www.aeso.ca",
    "freq": "Monthly",
    "res": "Zone",
    "vars": [
      "demand",
      "generation",
      "wind_MW",
      "solar_MW"
    ],
    "category": "Utility",
    "feeds": [
      "S",
      "T"
    ]
  },
  {
    "id": "DS09",
    "name": "SaskPower",
    "url": "https://www.saskpower.com",
    "freq": "Annual",
    "res": "Region",
    "vars": [
      "SAIDI",
      "load",
      "generation_mix"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "T"
    ]
  },
  {
    "id": "DS10",
    "name": "Manitoba Hydro",
    "url": "https://www.hydro.mb.ca",
    "freq": "Annual",
    "res": "Region",
    "vars": [
      "SAIDI",
      "SAIFI",
      "hydro_generation"
    ],
    "category": "Utility",
    "feeds": [
      "C"
    ]
  },
  {
    "id": "DS11",
    "name": "NB Power",
    "url": "https://www.nbpower.com",
    "freq": "Annual",
    "res": "Region",
    "vars": [
      "reliability",
      "nuclear",
      "wind"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "T"
    ]
  },
  {
    "id": "DS12",
    "name": "Nova Scotia Power",
    "url": "https://www.nspower.ca",
    "freq": "Annual",
    "res": "Region",
    "vars": [
      "SAIDI",
      "SAIFI",
      "coal_phase_out"
    ],
    "category": "Utility",
    "feeds": [
      "C",
      "T"
    ]
  },
  {
    "id": "DS13",
    "name": "NERC",
    "url": "https://www.nerc.com",
    "freq": "Annual",
    "res": "Regional",
    "vars": [
      "reliability_standards",
      "compliance",
      "N1_status"
    ],
    "category": "Standards",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS14",
    "name": "IEA Global EV Data",
    "url": "https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer",
    "freq": "Annual",
    "res": "National",
    "vars": [
      "EV_stock",
      "EV_sales",
      "charger_count"
    ],
    "category": "Transport",
    "feeds": [
      "S"
    ]
  },
  {
    "id": "DS15",
    "name": "OpenStreetMap",
    "url": "https://www.openstreetmap.org",
    "freq": "Continuous",
    "res": "Node",
    "vars": [
      "substation_location",
      "line_routing",
      "land_use"
    ],
    "category": "Geospatial",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS16",
    "name": "NRCan Seismic Hazard",
    "url": "https://earthquakescanada.nrcan.gc.ca",
    "freq": "Real-time",
    "res": "Point",
    "vars": [
      "PGA",
      "zone",
      "magnitude"
    ],
    "category": "Seismic",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS17",
    "name": "Canadian Census",
    "url": "https://www12.statcan.gc.ca/census-recensement",
    "freq": "5-year",
    "res": "Census division",
    "vars": [
      "population",
      "dwellings",
      "income",
      "age_dist"
    ],
    "category": "Demographic",
    "feeds": [
      "E"
    ]
  },
  {
    "id": "DS18",
    "name": "Canada Infrastructure Bank",
    "url": "https://cib-bic.ca",
    "freq": "Annual",
    "res": "Project",
    "vars": [
      "investment",
      "project_type",
      "region"
    ],
    "category": "Investment",
    "feeds": [
      "I",
      "T"
    ]
  },
  {
    "id": "DS19",
    "name": "ISO 9223 Corrosion Data",
    "url": "https://www.iso.org",
    "freq": "Static",
    "res": "Zone",
    "vars": [
      "corrosion_class",
      "salinity",
      "SO2"
    ],
    "category": "Materials",
    "feeds": [
      "I"
    ]
  },
  {
    "id": "DS20",
    "name": "SSI Engine (internal)",
    "url": "#",
    "freq": "On-demand",
    "res": "Substation",
    "vars": [
      "SSI_score",
      "components",
      "modifiers",
      "markov"
    ],
    "category": "Model",
    "feeds": [
      "C",
      "V",
      "I",
      "E",
      "S",
      "T"
    ]
  }
];

window.SSI_METADATA.VALIDATION_CHECKS = [
  {
    "check": "Component weights sum to 1.0",
    "criterion": "C+V+I+E+S+T = 1.00",
    "status": "Pass"
  },
  {
    "check": "Intra-component weights sum to 1.0",
    "criterion": "Per component metric weights = 1.00",
    "status": "Pass"
  },
  {
    "check": "Global weights sum to 1.0",
    "criterion": "Per component global weights = 1.00",
    "status": "Pass"
  },
  {
    "check": "SSI range [0, 100]",
    "criterion": "All SSI scores in [0, 100]",
    "status": "Pass"
  },
  {
    "check": "No missing SAIDI values",
    "criterion": "SAIDI coverage > 95%",
    "status": "Pass"
  },
  {
    "check": "No missing SAIFI values",
    "criterion": "SAIFI coverage > 95%",
    "status": "Pass"
  },
  {
    "check": "Voltage within CSA limits",
    "criterion": "V_reg within CSA C235 tolerance",
    "status": "Pass"
  },
  {
    "check": "Asset age plausibility",
    "criterion": "Age in [0, 80] years",
    "status": "Pass"
  },
  {
    "check": "DER capacity non-negative",
    "criterion": "DER_MW >= 0",
    "status": "Pass"
  },
  {
    "check": "Markov transition matrix stochastic",
    "criterion": "Row sums = 1.0 +/- 1e-6",
    "status": "Pass"
  },
  {
    "check": "ETTC positive",
    "criterion": "ETTC > 0 years",
    "status": "Pass"
  },
  {
    "check": "Province count",
    "criterion": "12 provinces/territories with data",
    "status": "Pass"
  },
  {
    "check": "Substation coordinate bounds",
    "criterion": "Lat [41, 84], Lon [-141, -52]",
    "status": "Pass"
  },
  {
    "check": "Monte Carlo convergence",
    "criterion": "CV < 2% at 10k iterations",
    "status": "Pass"
  },
  {
    "check": "Cross-validation R-squared",
    "criterion": "R2 > 0.85 on holdout set",
    "status": "Pass"
  }
];

window.SSI_METADATA.CHANGELOG = [
  {
    "id": "CL01",
    "section": "Global",
    "change": "Initial Canada SSI v4.0 framework release",
    "type": "Major"
  },
  {
    "id": "CL02",
    "section": "Data",
    "change": "Integrated CER annual filing data for 2024",
    "type": "Data"
  },
  {
    "id": "CL03",
    "section": "Data",
    "change": "Added Statistics Canada economic indicators",
    "type": "Data"
  },
  {
    "id": "CL04",
    "section": "Components",
    "change": "Calibrated component weights for Canadian grid topology",
    "type": "Model"
  },
  {
    "id": "CL05",
    "section": "Infrastructure",
    "change": "Added NRCan seismic hazard zones",
    "type": "Data"
  },
  {
    "id": "CL06",
    "section": "Infrastructure",
    "change": "Added Environment Canada corrosion classification",
    "type": "Data"
  },
  {
    "id": "CL07",
    "section": "Infrastructure",
    "change": "Integrated flood risk from NRCan mapping",
    "type": "Data"
  },
  {
    "id": "CL08",
    "section": "Saturation",
    "change": "Added provincial DER capacity from CER filings",
    "type": "Data"
  },
  {
    "id": "CL09",
    "section": "Saturation",
    "change": "Integrated IEA EV penetration data",
    "type": "Data"
  },
  {
    "id": "CL10",
    "section": "Transition",
    "change": "Calibrated Markov chain transition matrices for Canadian fleet",
    "type": "Model"
  },
  {
    "id": "CL11",
    "section": "Economic",
    "change": "Added provincial GDP and unemployment from StatCan",
    "type": "Data"
  },
  {
    "id": "CL12",
    "section": "Topology",
    "change": "Built graph model from Canadian transmission network",
    "type": "Model"
  },
  {
    "id": "CL13",
    "section": "Validation",
    "change": "Monte Carlo simulation with 10k iterations",
    "type": "QA"
  },
  {
    "id": "CL14",
    "section": "Normalisation",
    "change": "Applied min-max scaling across Canadian substation fleet",
    "type": "Model"
  },
  {
    "id": "CL15",
    "section": "Data",
    "change": "Added Hydro-Quebec, IESO, BC Hydro, AESO utility feeds",
    "type": "Data"
  },
  {
    "id": "CL16",
    "section": "Global",
    "change": "v4.0.1 bug fixes and data quality improvements",
    "type": "Patch"
  },
  {
    "id": "CL17",
    "section": "Global",
    "change": "v4.0.2 methodology page and dashboard alignment",
    "type": "Patch"
  }
];

/* ── SSIMetadata alias for methodology.html ── */
window.SSIMetadata = window.SSI_METADATA;
