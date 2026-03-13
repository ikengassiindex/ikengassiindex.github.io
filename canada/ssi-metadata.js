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