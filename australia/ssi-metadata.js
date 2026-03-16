/*  SSI v4.0.2 — Metadata · Australia
    This file is loaded by every page in /australia/.
    Path convention: src="ssi-metadata.js" (local, no ../ prefix)  */

window.SSI_METADATA = {
  country: "Australia",
  country_code: "AU",
  currency: "AUD",
  version: "4.0.2",
  edition: "001",
  edition_month: "April 2026",
  substations_label: "substations",
  region_label: "State / Territory",
  region_label_plural: "States & Territories",
  admin_division_label: "Statistical Area Level 4",
  admin_division_label_short: "SA4",
  total_substations: 8500,
  total_departments: 87,
  total_regions: 8,
  voltage_tiers: {
    EHV: { label: "EHV (≥ 220 kV)", min_kv: 220 },
    HV:  { label: "HV (66–132 kV)", min_kv: 66 },
    MV:  { label: "MV (< 66 kV)", min_kv: 0 }
  },
  data_sources: [
    { id:"DS01", name:"AEMO — Transmission Network Data", url:"https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem", freq:"Monthly", resolution:"Substation", feeds:["C","I"] },
    { id:"DS02", name:"AER — Electricity Distribution Benchmarking", url:"https://www.aer.gov.au/industry/registers/resources/electricity-distribution-benchmarking", freq:"Annual", resolution:"DNSP", feeds:["C","V","I"] },
    { id:"DS03", name:"ABS — Census & Regional Statistics", url:"https://www.abs.gov.au/statistics", freq:"Annual", resolution:"SA4", feeds:["E","S"] },
    { id:"DS04", name:"CSIRO — Renewable Energy Integration", url:"https://www.csiro.au/en/research/technology-space/energy", freq:"Annual", resolution:"National", feeds:["T"] },
    { id:"DS05", name:"Bureau of Meteorology — Climate Data", url:"http://www.bom.gov.au/climate/data/", freq:"Monthly", resolution:"Station", feeds:["C","I"] },
    { id:"DS06", name:"Geoscience Australia — Seismic Hazard", url:"https://www.ga.gov.au/scientific-topics/community-safety/earthquake", freq:"Static", resolution:"Grid 0.1°", feeds:["I"] },
    { id:"DS07", name:"OpenStreetMap — Power Infrastructure", url:"https://www.openstreetmap.org/", freq:"Continuous", resolution:"Node", feeds:["I"] },
    { id:"DS08", name:"Copernicus ERA5 — Climate Reanalysis", url:"https://cds.climate.copernicus.eu/", freq:"Monthly", resolution:"Grid 0.25°", feeds:["C","I"] },
    { id:"DS09", name:"Clean Energy Regulator — DER Register", url:"https://www.cleanenergyregulator.gov.au/", freq:"Quarterly", resolution:"Postcode", feeds:["S","T"] },
    { id:"DS10", name:"AEMO — Integrated System Plan", url:"https://aemo.com.au/energy-systems/major-publications/integrated-system-plan-isp", freq:"Biennial", resolution:"REZ", feeds:["T","S"] }
  ],
  components: [
    { key:"C", label:"Continuity", weight:0.30, color:"var(--crimson)", description:"Measures outage frequency, duration, and restoration performance.", metrics:[{id:"C1",label:"SAIDI",intra_w:0.35,global_w:0.105,unit:"min/yr",norm:"A",source:"DS01,DS02,DS12"},{id:"C2",label:"SAIFI",intra_w:0.30,global_w:0.090,unit:"int/yr",norm:"A",source:"DS01,DS02,DS12"},{id:"C3",label:"CAIDI",intra_w:0.20,global_w:0.060,unit:"min/int",norm:"A",source:"DS01,DS02"},{id:"C4",label:"MAIFI",intra_w:0.15,global_w:0.045,unit:"int/yr",norm:"A",source:"DS01,DS14"}] },
    { key:"V", label:"Voltage Quality", weight:0.10, color:"var(--terracotta)", description:"Captures voltage stability, power factor, and harmonic distortion.", metrics:[{id:"V1",label:"ΔV deviation",intra_w:0.40,global_w:0.040,unit:"%",norm:"A",source:"DS02,DS19"},{id:"V2",label:"THD",intra_w:0.30,global_w:0.030,unit:"%",norm:"A",source:"DS02,DS19"},{id:"V3",label:"Power Factor",intra_w:0.30,global_w:0.030,unit:"ratio",norm:"B",source:"DS02"}] },
    { key:"I", label:"Infrastructure", weight:0.25, color:"var(--sage)", description:"Assesses physical asset condition, age, capacity, seismic and flood exposure.", metrics:[{id:"I1",label:"Asset Age",intra_w:0.20,global_w:0.050,unit:"years",norm:"A",source:"DS02,DS07"},{id:"I2",label:"Capacity Utilisation",intra_w:0.20,global_w:0.050,unit:"%",norm:"A",source:"DS01,DS02"},{id:"I3",label:"N-1 Compliance",intra_w:0.15,global_w:0.0375,unit:"binary",norm:"C",source:"DS01,DS14"},{id:"I4",label:"Graph Degree",intra_w:0.15,global_w:0.0375,unit:"int",norm:"B",source:"DS07"},{id:"I5",label:"Seismic PGA",intra_w:0.15,global_w:0.0375,unit:"g",norm:"A",source:"DS06"},{id:"I6",label:"Corrosion Class",intra_w:0.05,global_w:0.0125,unit:"class",norm:"D",source:"DS08"},{id:"I7",label:"Flood Risk",intra_w:0.10,global_w:0.025,unit:"class",norm:"D",source:"DS17"}] },
    { key:"E", label:"Economic", weight:0.10, color:"#3b9eff", description:"Links grid risk to regional economic exposure.", metrics:[{id:"E1",label:"Energy Price Index",intra_w:0.35,global_w:0.035,unit:"AUD/MWh",norm:"A",source:"DS18,DS20"},{id:"E2",label:"Unemployment Rate",intra_w:0.35,global_w:0.035,unit:"%",norm:"A",source:"DS03"},{id:"E3",label:"Business Density",intra_w:0.30,global_w:0.030,unit:"/km²",norm:"B",source:"DS03,DS11"}] },
    { key:"S", label:"Saturation", weight:0.20, color:"var(--bronze)", description:"Quantifies DER penetration stress and EV charging load.", metrics:[{id:"S1",label:"DER Capacity",intra_w:0.35,global_w:0.070,unit:"MW",norm:"A",source:"DS09,DS10,DS13"},{id:"S2",label:"DER Stress Ratio",intra_w:0.35,global_w:0.070,unit:"ratio",norm:"A",source:"DS09,DS01"},{id:"S3",label:"EV Penetration",intra_w:0.30,global_w:0.060,unit:"%",norm:"A",source:"DS15,DS16"}] },
    { key:"T", label:"Energy Transition", weight:0.05, color:"#22d3ee", description:"Measures clean energy transition pace.", metrics:[{id:"T1",label:"RE Share",intra_w:0.50,global_w:0.025,unit:"%",norm:"B",source:"DS04,DS09,DS13"},{id:"T2",label:"Transition Readiness",intra_w:0.50,global_w:0.025,unit:"score",norm:"A",source:"DS04,DS10"}] }
  ],
  modifiers: [
    { key:"R3_C_mult", label:"R3", domain:"Consequence", range:[0.70,1.30], description:"Population-weighted consequence multiplier." },
    { key:"R4_F_topo", label:"R4", domain:"Graph Criticality", range:[0.80,1.35], description:"Topological importance from betweenness centrality." },
    { key:"R6_restoration", label:"R6a", domain:"Restoration Speed", range:[0.90,1.10], description:"DNSP-level restoration time normalised against NEM benchmark." },
    { key:"R6_seismic", label:"R6b", domain:"Seismic Overlay", range:[1.00,1.25], description:"Peak ground acceleration hazard overlay." },
    { key:"R7_cyber", label:"R7", domain:"Digital Readiness", range:[0.99,1.05], description:"SCADA/ICS cyber-physical exposure proxy." }
  ],
  bands: [
    { label:"Low", min:0.00, max:0.25, color:"var(--band-low)", css:"low" },
    { label:"Medium", min:0.25, max:0.50, color:"var(--band-medium)", css:"medium" },
    { label:"High", min:0.50, max:0.75, color:"var(--band-high)", css:"high" },
    { label:"Critical", min:0.75, max:1.00, color:"var(--band-critical)", css:"critical" }
  ],
  data_layers: [
    { id:"L01", domain:"Substations", variables:12, source:"DS01,DS07", status:"LIVE" },
    { id:"L02", domain:"Outage Metrics", variables:10, source:"DS01,DS02,DS12", status:"LIVE" },
    { id:"L03", domain:"Voltage Quality", variables:8, source:"DS02,DS19", status:"LIVE" },
    { id:"L04", domain:"Asset Register", variables:10, source:"DS02,DS07", status:"LIVE" },
    { id:"L05", domain:"Graph Topology", variables:8, source:"DS07", status:"LIVE" },
    { id:"L06", domain:"Socio-Economic", variables:10, source:"DS03,DS11", status:"LIVE" },
    { id:"L07", domain:"DER Penetration", variables:8, source:"DS09,DS13", status:"LIVE" },
    { id:"L08", domain:"EV Adoption", variables:6, source:"DS15,DS16", status:"LIVE" },
    { id:"L09", domain:"Seismic Hazard", variables:5, source:"DS06", status:"LIVE" },
    { id:"L10", domain:"Climate Exposure", variables:10, source:"DS05,DS08", status:"LIVE" },
    { id:"L11", domain:"Markov Model", variables:8, source:"DS01,DS02", status:"LIVE" }
  ],
  normalisation: [
    { code:"A", label:"Min-Max", formula:"(x − x_min) / (x_max − x_min)" },
    { code:"B", label:"Min-Max Inverse", formula:"1 − (x − x_min) / (x_max − x_min)" },
    { code:"C", label:"Binary", formula:"0 if compliant, 1 if non-compliant" },
    { code:"D", label:"Ordinal Mapping", formula:"Lookup table" }
  ],
  monte_carlo: { iterations:10000, correlation_matrix:"20×20", seed:42, confidence_interval:0.95 },
  regions: ["New South Wales","Victoria","Queensland","South Australia","Western Australia","Tasmania","Northern Territory","Australian Capital Territory"],
  validation: [
    { check:"Weight sum = 1.0", target:1.0, tolerance:0.001 },
    { check:"Intra-weight sums per component", target:1.0, tolerance:0.001 },
    { check:"R_median ∈ [0,1]", target:true, tolerance:0 },
    { check:"Band boundaries contiguous", target:true, tolerance:0 },
    { check:"MC convergence (CV < 2%)", target:0.02, tolerance:0 },
    { check:"No null scores", target:0, tolerance:0 },
    { check:"Region coverage = 100%", target:1.0, tolerance:0 },
    { check:"Source freshness < 12 months", target:true, tolerance:0 },
    { check:"Substation ID uniqueness", target:true, tolerance:0 },
    { check:"Component score ∈ [0,1]", target:true, tolerance:0 }
  ],
  changelog: [
    { version:"4.0.2", date:"2026-03", note:"Australia country launch — 8,500 substations across 8 states/territories, 87 SA4 regions." },
    { version:"4.0.2", date:"2026-03", note:"Integrated AEMO NEM data, AER benchmarking, Clean Energy Regulator DER register." },
    { version:"4.0.2", date:"2026-03", note:"Added Geoscience Australia seismic + flood hazard overlays." },
    { version:"4.0.2", date:"2026-03", note:"BOM climate reanalysis integration for bushfire corridor exposure." }
  ]
};
