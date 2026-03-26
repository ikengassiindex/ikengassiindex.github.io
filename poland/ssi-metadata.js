(function() {
  var META = {
    country: "Poland",
    country_code: "PL",
    currency: "zł",
    currency_code: "PLN",
    admin_l1: "Województwo",
    admin_l1_plural: "Województwa",
    admin_l2: "Powiat",
    admin_l2_plural: "Powiaty",
    grid_operator: "PSE S.A.",
    regulator: "URE",

    stats: {
      sources: 30,
      variables: 95,
      components: 6,
      modifiers: 5,
      fleet_size: 1685,
      fleet_median: 0.345,
      fleet_mean: 0.350,
      critical_count: 0,
      high_count: 289,
      data_freshness: 100
    },

    FREQ_DISTRIBUTION: {
      "Real-time": { count: 3, sources: ["PSE Dispatch", "GIOŚ Air Quality", "IMGW Warnings"] },
      "Hourly":    { count: 2, sources: ["PSE Generation", "ENTSO-E Flows"] },
      "Daily":     { count: 3, sources: ["IMGW Weather", "Copernicus ERA5", "PSE Load"] },
      "Monthly":   { count: 5, sources: ["ARE Energy Balance", "NBP Economics", "GUS Updates", "PSEW Wind", "KOBiZE Emissions"] },
      "Quarterly": { count: 4, sources: ["URE Reports", "DSO Performance", "CEN Forecasts", "Eurostat SILC"] },
      "Annual":    { count: 8, sources: ["GUS Census Updates", "UDT Inspections", "KZGW Flood Maps", "PIG Geology", "WUG Mining", "DSO Annual Reports", "CONAF Forest", "World Bank"] },
      "Static":    { count: 3, sources: ["OSM Power", "GUGiK Geodesy", "SolarGIS"] },
      "5-Year":    { count: 2, sources: ["GUS Census 2021", "KZGW ISOK Cycle"] }
    },

    DATA_SOURCES: [
      { id: "D01", name: "PSE — Polskie Sieci Elektroenergetyczne", freq: "Real-time", scope: "National grid dispatch, generation, cross-border flows", vars: "S1, G1, T1, transmission SCADA", url: "https://www.pse.pl" },
      { id: "D02", name: "URE — Urząd Regulacji Energetyki", freq: "Quarterly", scope: "Tariff studies, market oversight, SAIDI/SAIFI", vars: "E1–E2, V1, regulatory KPIs", url: "https://www.ure.gov.pl" },
      { id: "D03", name: "GUS — Główny Urząd Statystyczny", freq: "Annual", scope: "Census 2021, demographics, employment, income", vars: "C1–C6 (population, income, migration)", url: "https://stat.gov.pl" },
      { id: "D04", name: "IMGW-PIB — Meteorology & Water", freq: "Daily", scope: "Temperature, rainfall, wind, flood warnings, drought", vars: "I1, I3, I5 (weather extremes)", url: "https://danepubliczne.imgw.pl" },
      { id: "D05", name: "PIG-PIB — Geological Institute", freq: "Annual", scope: "Geological maps, mining subsidence, landslide inventory (SOPO)", vars: "H3 (subsidence), D2 (landslides)", url: "https://www.pgi.gov.pl" },
      { id: "D06", name: "WUG — State Mining Authority", freq: "Annual", scope: "Mining seismicity, subsidence maps, ground deformation", vars: "H1–H2 (mining tremors), κ_subsidence", url: "https://www.wug.gov.pl" },
      { id: "D07", name: "GIOŚ — Environmental Inspection", freq: "Real-time", scope: "Air quality (PM2.5, SO₂, NO₂), 400+ stations", vars: "H4–H5 (corrosion class, SO₂ exposure)", url: "https://www.gios.gov.pl" },
      { id: "D08", name: "UDT — Technical Inspection Office", freq: "Annual", scope: "Equipment compliance, transformer inspections", vars: "B2–B3 (equipment condition)", url: "https://www.udt.gov.pl" },
      { id: "D09", name: "OSM — OpenStreetMap (Power)", freq: "Static", scope: "Substation topology, transmission lines, HV graph", vars: "A2–A4 (topology), G2 (network)", url: "https://overpass-api.de" },
      { id: "D10", name: "Copernicus CDS — ESA Climate", freq: "Daily", scope: "ERA5 reanalysis, CMIP6 projections, satellite data", vars: "D3–D4 (temperature, precipitation)", url: "https://cds.climate.copernicus.eu" },
      { id: "D11", name: "KZGW — Wody Polskie (Water Authority)", freq: "Annual", scope: "ISOK flood risk maps, river basin plans, drought data", vars: "D5 (flood risk), D4 (water stress)", url: "https://wody.gov.pl" },
      { id: "D12", name: "KOBiZE — National Emissions Centre", freq: "Monthly", scope: "CO₂ emissions by installation, EU ETS data", vars: "H4 (SO₂/corrosion proxy)", url: "https://www.kobize.pl" },
      { id: "D13", name: "GUGiK — Geodesy & Cartography", freq: "Static", scope: "DEM, orthophotos, BDOT10k topographic database", vars: "Land use, infrastructure mapping", url: "https://www.geoportal.gov.pl" },
      { id: "D14", name: "ARE — Energy Market Agency", freq: "Monthly", scope: "Energy balances by voivodeship, coal consumption", vars: "E1 (energy market data)", url: "https://www.are.waw.pl" },
      { id: "D15", name: "NBP — National Bank of Poland", freq: "Monthly", scope: "GDP by voivodeship, economic indicators", vars: "V1 (VoLL), economic scaling", url: "https://www.nbp.pl" },
      { id: "D16", name: "PSEW — Polish Wind Energy Assoc.", freq: "Monthly", scope: "Wind capacity by region, curtailment data", vars: "T1 (wind integration)", url: "https://psew.pl" },
      { id: "D17", name: "IEO — Institute for Renewable Energy", freq: "Annual", scope: "Solar PV capacity, prosumer statistics, DER registry", vars: "T1 (DER/PV penetration)", url: "https://ieo.pl" },
      { id: "D18", name: "DSO Reports (PGE, Tauron, Enea, Energa, Stoen)", freq: "Annual", scope: "CAPEX, SAIDI/SAIFI, transformer inventories", vars: "F1–F2 (maintenance), B1 (age data)", url: "" },
      { id: "D19", name: "ENTSO-E Transparency Platform", freq: "Hourly", scope: "Cross-border flows, generation adequacy, outages", vars: "S1 (capacity), cross-border metrics", url: "https://transparency.entsoe.eu" },
      { id: "D20", name: "Eurostat — EU Statistics", freq: "Annual", scope: "EU-harmonized socio-economic, energy poverty (SILC)", vars: "C3 (energy poverty), cross-validation", url: "https://ec.europa.eu/eurostat" },
      { id: "D21", name: "IPCC / Copernicus Marine", freq: "Static", scope: "Baltic sea-level rise projections, coastal models", vars: "D5 (coastal inundation)", url: "https://climate.copernicus.eu" },
      { id: "D22", name: "SolarGIS — Global Solar Atlas", freq: "Static", scope: "Solar irradiance maps (GHI, DNI) for Poland", vars: "T1 (PV resource)", url: "https://globalsolaratlas.info" },
      { id: "D23", name: "Ministry of Health / NFZ", freq: "Annual", scope: "Hospital, clinic locations (critical infrastructure)", vars: "V2 (critical infrastructure mapping)", url: "" },
      { id: "D24", name: "BGK — National Development Bank", freq: "Annual", scope: "Infrastructure investment data by region", vars: "R5 (investment trend)", url: "https://www.bgk.pl" },
      { id: "D25", name: "RDOŚ — Environmental Directorates", freq: "Annual", scope: "Natura 2000, protected areas, environmental constraints", vars: "Environmental constraint mapping", url: "" },
      { id: "D26", name: "Ministry of Interior — Migration", freq: "Annual", scope: "Residence permits, Ukrainian refugee data", vars: "C6 (net migration)", url: "" },
      { id: "D27", name: "Port Authority (Gdańsk, Gdynia, Szczecin)", freq: "Quarterly", scope: "Baltic shipping, port operations", vars: "Regional economic proxy", url: "" },
      { id: "D28", name: "GDDKiA — Road Infrastructure", freq: "Annual", scope: "Road network, transport nodes", vars: "Infrastructure density proxy", url: "https://www.gddkia.gov.pl" },
      { id: "D29", name: "CIREN — Soil Data (PIG supplement)", freq: "Annual", scope: "Soil properties, corrosion classification", vars: "H5 (ISO 9223 by soil)", url: "" },
      { id: "D30", name: "World Bank / OECD", freq: "Annual", scope: "International benchmarks, socio-economic indicators", vars: "Cross-validation reference", url: "" }
    ],

    // Methodology sections
    methodology: {
      data_collection: "Poland's SSI v4.0.2 data pipeline integrates 30 institutional sources spanning grid operations (PSE real-time dispatch), regulation (URE performance benchmarks), demographics (GUS Census 2021), meteorology (IMGW-PIB open data portal), geology (PIG-PIB geological mapping), mining safety (WUG subsidence monitoring), and environmental monitoring (GIOŚ air quality network). EU membership provides additional data via Eurostat, ENTSO-E, and EU ETS registries. The data ingestion follows a 4-phase approach: Phase 1 covers core grid + demographic data from PSE/GUS/IMGW; Phase 2 adds secondary sources (KZGW flood maps, DSO reports, renewable energy data); Phase 3 derives Markov model outputs and Monte Carlo simulations; Phase 4 validates and deploys.",

      scoring_model: "The SSI v4.0.2 scoring model for Poland uses 95 variables across 6 risk components (R1–R6) calibrated to Poland's unique hazard profile. Unlike seismic-dominated countries (Chile, Japan), Poland's primary natural hazard is river flooding (Vistula, Oder basins — weight 0.35 in κ_climate). Mining subsidence in Upper Silesia (weight 0.25) is a Poland-specific hazard. The coal transition modifier (κ_coal_transition) captures stranding risk for substations feeding aging coal infrastructure. Component weights: R1=0.20, R2=0.18, R3=0.15, R4=0.18, R5=0.16, R6=0.13. R5 (Maintenance Trend) is weighted higher than most countries due to PRL-era (1945–1989) infrastructure aging.",

      risk_classification: "Risk bands follow the standard SSI v4.0.2 thresholds: Critical (R≥0.60), High (0.40–0.60), Medium (0.25–0.40), Low (<0.25). Poland's fleet median of 0.345 reflects moderate systemic risk, driven by aging PRL-era infrastructure and concentrated industrial demand in Śląskie. The absence of Critical-band substations reflects Poland's low natural seismicity — unlike Chile or Japan, Poland has no substations exposed to extreme natural hazards. The highest-risk substations are in Śląskie (mining subsidence + industrial stress) and flood-prone Oder basin (Dolnośląskie, Opolskie).",

      monte_carlo: "Each substation undergoes 2,000 Monte Carlo iterations with a 95-dimensional Gaussian copula. Input distributions are calibrated to Polish data uncertainty: wider σ for PRL-era vintage estimates (pre-1990), narrower σ for well-documented post-EU-accession assets (2004+). The Cholesky-decomposed correlation matrix captures dependencies between flood risk and mining subsidence in southern voivodeships. Output: R_median, CI=[P5, P95], P_critical per substation.",

      environmental: "Poland's environmental hazard profile is dominated by flooding (Vistula and Oder river basins, confirmed by 2024 Oder catastrophic flood). Secondary hazards include mining subsidence in Upper Silesia Coal Basin (USCB — 100+ years of extraction), Baltic coastal erosion (limited, ~528 km coastline), and increasing extreme weather events (heat waves, winter storms). Seismic risk is negligible (stable European craton, α=0.15) except for mining-induced tremors in USCB. The κ_climate shift matrix weights: flooding 0.35, mining subsidence 0.25, coal transition 0.20, extreme weather 0.15, coastal 0.05.",

      data_quality: "Data quality assessment: 53% full coverage (50 variables), 21% partial coverage (20 variables), 16% proxy/model-based (15 variables), 5% gaps (5 variables), 5% derived (5 variables). Key advantages: GUS Census 2021 (most recent in EU), IMGW open data portal (best-in-class for CEE), EU/Eurostat harmonized data, ENTSO-E cross-border transparency. Key gaps: substation vintage (PRL-era records incomplete), per-substation equipment condition (restricted DSO data), mining subsidence per-site mapping (zone-level from WUG)."
    },

    // Component labels
    component_labels: {
      C: "Continuity",
      V: "Voltage Quality",
      I: "Infrastructure Consequence",
      S: "Saturation & Topology",
      E: "Equipment Aging",
      T: "Transition & Hazard"
    },

    modifier_labels: {
      R3_C_mult: "R3 Consequence",
      R4_G_crit: "R4 Graph Criticality",
      R6a_restoration: "R6a Restoration",
      R6b_seismic: "R6b Mining/Hazard",
      R7_digital: "R7 Digital Readiness"
    },

    regions: [
      "Dolnośląskie", "Kujawsko-Pomorskie", "Lubelskie", "Lubuskie",
      "Łódzkie", "Małopolskie", "Mazowieckie", "Opolskie",
      "Podkarpackie", "Podlaskie", "Pomorskie", "Śląskie",
      "Świętokrzyskie", "Warmińsko-Mazurskie", "Wielkopolskie", "Zachodniopomorskie"
    ],

    dso_operators: [
      "PGE Dystrybucja", "Tauron Dystrybucja", "Enea Operator", "Energa-Operator", "Stoen Operator"
    ],

    band_thresholds: { critical: 0.60, high: 0.40, medium: 0.25 },

    weights: { R1: 0.20, R2: 0.18, R3: 0.15, R4: 0.18, R5: 0.16, R6: 0.13 }
  };

  window.SSI_METADATA = META;
  window.SSIMetadata = META;
})();
