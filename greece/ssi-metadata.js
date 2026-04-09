/**
 * SSI Metadata Configuration - Greece v4.0.2
 * Sustainability and Stability Index Dashboard for Greece
 * Provides comprehensive metadata configuration for all dashboard pages
 */

window.SSI_META = (function() {
  'use strict';

  return {
    // Country and Version Information
    country: 'Greece',
    countryCode: 'GR',
    version: '4.0.2',
    dashboard: 'SSI Greece Dashboard',

    // ===== DATA SOURCES (30 Verified Sources in 3 Tiers) =====
    sources: {
      tier1_core: [
        {
          id: 'ADMIE_IPTO_transparency',
          name: 'ADMIE/IPTO Transparency Platform',
          category: 'Grid Operations',
          description: 'Real-time electricity grid transparency and operational data',
          url: 'https://www.admie.gr/',
          reliability: 'high',
          updateFrequency: 'real-time'
        },
        {
          id: 'DEDDIE_HEDNO_SAIDI_SAIFI',
          name: 'DEDDIE/HEDNO SAIDI/SAIFI',
          category: 'Reliability Metrics',
          description: 'System Average Interruption Duration/Frequency Indices',
          url: 'https://www.hedno.gr/',
          reliability: 'high',
          updateFrequency: 'monthly'
        },
        {
          id: 'ELSTAT_Census',
          name: 'ELSTAT Census Data',
          category: 'Demographics',
          description: 'Hellenic Statistical Authority census and population data',
          url: 'https://www.statistics.gr/',
          reliability: 'high',
          updateFrequency: 'quinquennial'
        },
        {
          id: 'Hellenic_Cadastre',
          name: 'Hellenic Cadastre',
          category: 'Geospatial',
          description: 'Property and land registry information',
          url: 'https://www.ktimatologio.gr/',
          reliability: 'high',
          updateFrequency: 'continuous'
        },
        {
          id: 'EAK_2003_Seismic_Zones',
          name: 'EAK 2003 Seismic Zones',
          category: 'Hazard Data',
          description: 'Greek Seismic Code 2003 - seismic zone classifications',
          url: 'https://oasp.gein.noa.gr/',
          reliability: 'high',
          updateFrequency: 'static'
        },
        {
          id: 'NOA_Seismological_Network',
          name: 'NOA Seismological Network',
          category: 'Hazard Data',
          description: 'National Observatory of Athens seismic monitoring',
          url: 'https://www.gein.noa.gr/',
          reliability: 'high',
          updateFrequency: 'real-time'
        },
        {
          id: 'HEnEx_Energy_Exchange',
          name: 'HEnEx Energy Exchange',
          category: 'Energy Markets',
          description: 'Day-ahead and balancing electricity market prices',
          url: 'https://www.henex.gr/',
          reliability: 'high',
          updateFrequency: 'hourly'
        },
        {
          id: 'RAE_Regulatory_Reports',
          name: 'RAE Regulatory Reports',
          category: 'Regulatory',
          description: 'Regulatory Authority for Energy compliance and penalty data',
          url: 'https://www.rae.gr/',
          reliability: 'high',
          updateFrequency: 'quarterly'
        },
        {
          id: 'YPEKA_Environment_Ministry',
          name: 'YPEKA Environment Ministry',
          category: 'Environmental',
          description: 'Ministry of Environment environmental monitoring and forecasts',
          url: 'https://www.ypeka.gr/',
          reliability: 'high',
          updateFrequency: 'daily'
        },
        {
          id: 'Copernicus_CDS',
          name: 'Copernicus Climate Data Store',
          category: 'Climate Data',
          description: 'Satellite-derived climate and weather datasets',
          url: 'https://cds.climate.copernicus.eu/',
          reliability: 'high',
          updateFrequency: 'daily'
        }
      ],

      tier2_supplementary: [
        {
          id: 'Bank_of_Greece_Economic',
          name: 'Bank of Greece Economic Bulletin',
          category: 'Economic',
          description: 'Monthly economic indicators and analysis',
          url: 'https://www.bankofgreece.gr/',
          reliability: 'medium-high',
          updateFrequency: 'monthly'
        },
        {
          id: 'HEPI_Energy_Poverty',
          name: 'HEPI Energy Poverty Index',
          category: 'Social',
          description: 'Hellenic Energy Poverty Index household survey data',
          url: 'https://www.hepi.gr/',
          reliability: 'medium-high',
          updateFrequency: 'annual'
        },
        {
          id: 'ADMIE_RES_Registry',
          name: 'ADMIE RES Registry',
          category: 'Renewable Energy',
          description: 'Renewable energy source installation registry',
          url: 'https://www.admie.gr/',
          reliability: 'medium-high',
          updateFrequency: 'weekly'
        },
        {
          id: 'LAGIE_DAPEEP_RES_Operator',
          name: 'LAGIE/DAPEEP RES Operator',
          category: 'Renewable Energy',
          description: 'Operator data for renewable energy systems',
          url: 'https://www.lagie.gr/',
          reliability: 'medium-high',
          updateFrequency: 'daily'
        },
        {
          id: 'Municipal_Open_Data',
          name: 'Municipal Open Data Portals',
          category: 'Local Data',
          description: 'Municipal-level operational and infrastructure data',
          url: 'https://data.gov.gr/',
          reliability: 'medium',
          updateFrequency: 'variable'
        },
        {
          id: 'ERA5_Climate_Reanalysis',
          name: 'ERA5 Climate Reanalysis',
          category: 'Climate Data',
          description: 'ECMWF reanalysis weather data for Greece',
          url: 'https://www.ecmwf.int/',
          reliability: 'medium-high',
          updateFrequency: 'monthly'
        },
        {
          id: 'JRC_ENSPRESO',
          name: 'JRC ENSPRESO Dataset',
          category: 'Energy Potentials',
          description: 'Joint Research Centre renewable energy potentials',
          url: 'https://publications.jrc.ec.europa.eu/',
          reliability: 'medium-high',
          updateFrequency: 'annual'
        },
        {
          id: 'OSM_Overpass',
          name: 'OpenStreetMap Overpass API',
          category: 'Geospatial',
          description: 'Open-source mapping and infrastructure features',
          url: 'https://overpass-api.de/',
          reliability: 'medium',
          updateFrequency: 'continuous'
        },
        {
          id: 'GADM_Admin_Boundaries',
          name: 'GADM Administrative Boundaries',
          category: 'Geospatial',
          description: 'Global administrative boundaries for Greece',
          url: 'https://gadm.org/',
          reliability: 'medium-high',
          updateFrequency: 'annual'
        },
        {
          id: 'WorldPop_Population',
          name: 'WorldPop Population Data',
          category: 'Demographics',
          description: 'High-resolution population distribution estimates',
          url: 'https://www.worldpop.org/',
          reliability: 'medium-high',
          updateFrequency: 'annual'
        }
      ],

      tier3_derived_proxy: [
        {
          id: 'Markov_Degradation_Matrices',
          name: 'Markov Degradation Matrices',
          category: 'Derived Model',
          description: 'Infrastructure degradation state transition models',
          derived: true
        },
        {
          id: 'Sobol_Sensitivity_Indices',
          name: 'Sobol Sensitivity Indices',
          category: 'Derived Model',
          description: 'Global sensitivity analysis of model parameters',
          derived: true
        },
        {
          id: 'Monte_Carlo_Confidence_Bounds',
          name: 'Monte Carlo Confidence Bounds',
          category: 'Derived Model',
          description: '95% and 99% confidence intervals from MC sampling',
          derived: true
        },
        {
          id: 'Fleet_Percentiles',
          name: 'Fleet Age Percentiles',
          category: 'Derived Statistic',
          description: 'Age distribution percentiles for equipment fleet',
          derived: true
        },
        {
          id: 'Correlation_Matrices',
          name: 'Correlation Matrices',
          category: 'Derived Statistic',
          description: 'Inter-component correlation coefficients',
          derived: true
        },
        {
          id: 'Graph_Topology_Metrics',
          name: 'Graph Topology Metrics',
          category: 'Derived Metric',
          description: 'Degree, centrality, betweenness for network analysis',
          derived: true
        },
        {
          id: 'CIGRE_TB761_Aging_Curves',
          name: 'CIGRE TB 761 Aging Curves',
          category: 'Industry Model',
          description: 'CIGRE Technical Brochure 761 transformer aging models',
          derived: true
        },
        {
          id: 'Corrosion_Maps_ISO9223',
          name: 'Corrosion Maps (ISO 9223)',
          category: 'Environmental Proxy',
          description: 'Corrosion rate classification based on climate data',
          derived: true
        },
        {
          id: 'DER_Variability_Time_Series',
          name: 'DER Variability Time Series',
          category: 'Derived Forecast',
          description: 'High-frequency renewable generation variability',
          derived: true
        },
        {
          id: 'EV_Penetration_Forecasts',
          name: 'EV Penetration Forecasts',
          category: 'Derived Forecast',
          description: 'Electric vehicle adoption and load impact projections',
          derived: true
        }
      ]
    },

    // ===== COMPONENTS & METRICS =====
    components: {
      C: {
        name: 'Continuity',
        description: 'Grid supply continuity and outage performance',
        metrics: {
          C1: {
            name: 'SAIDI',
            description: 'System Average Interruption Duration Index (minutes)',
            unit: 'minutes/customer/year',
            weight: 0.40,
            direction: 'lower is better'
          },
          C2: {
            name: 'SAIFI',
            description: 'System Average Interruption Frequency Index',
            unit: 'interruptions/customer/year',
            weight: 0.30,
            direction: 'lower is better'
          },
          C3: {
            name: 'MT Exceedance',
            description: 'Medium-term threshold exceedance events',
            unit: 'count/quarter',
            weight: 0.15,
            direction: 'lower is better'
          },
          C4: {
            name: 'Planned Outages',
            description: 'Planned maintenance outage impact',
            unit: 'hours/circuit/year',
            weight: 0.15,
            direction: 'lower is better'
          }
        },
        totalWeight: 1.0
      },

      V: {
        name: 'Voltage Quality',
        description: 'Power quality and voltage disturbance metrics',
        metrics: {
          V1: {
            name: 'Severity-weighted Dips',
            description: 'Voltage dip severity and frequency combined metric',
            unit: 'dimensionless',
            weight: 1.0,
            direction: 'lower is better'
          }
        },
        totalWeight: 1.0
      },

      I: {
        name: 'Infrastructure',
        description: 'Physical infrastructure condition and exposure to stressors',
        metrics: {
          I1: {
            name: 'Snow/Ice IRI',
            description: 'Infrastructure risk from snow/ice events',
            unit: 'dimensionless 0-1',
            weight: 0.12,
            direction: 'lower is better'
          },
          I2: {
            name: 'Tree-fall IRI',
            description: 'Infrastructure risk from vegetation-induced failures',
            unit: 'dimensionless 0-1',
            weight: 0.12,
            direction: 'lower is better'
          },
          I3: {
            name: 'Heat-wave IRI',
            description: 'Infrastructure risk from high-temperature events',
            unit: 'dimensionless 0-1',
            weight: 0.12,
            direction: 'lower is better'
          },
          I4: {
            name: 'Network Density',
            description: 'Line density and circuit concentration',
            unit: 'km/km²',
            weight: 0.10,
            direction: 'context-dependent'
          },
          I5: {
            name: 'Thermal Stress',
            description: 'Cumulative thermal aging stress',
            unit: '% of rated capacity',
            weight: 0.10,
            direction: 'lower is better'
          },
          I6: {
            name: 'Line Length Exposure',
            description: 'Total line length exposure to environmental hazards',
            unit: 'km',
            weight: 0.10,
            direction: 'lower is better'
          },
          I7: {
            name: 'Age Factor',
            description: 'Weighted age distribution of critical assets',
            unit: 'years (effective)',
            weight: 0.12,
            direction: 'lower is better'
          },
          I8: {
            name: 'Corrosion Index',
            description: 'ISO 9223 corrosion risk classification',
            unit: 'dimensionless 0-1',
            weight: 0.12,
            direction: 'lower is better'
          },
          I9: {
            name: 'Flood Risk',
            description: 'Infrastructure flood inundation probability',
            unit: 'dimensionless 0-1',
            weight: 0.10,
            direction: 'lower is better'
          }
        },
        totalWeight: 1.0
      },

      E: {
        name: 'Economic',
        description: 'Economic impacts and productivity losses',
        metrics: {
          E1: {
            name: 'RAE Penalties',
            description: 'Regulatory Authority energy penalties and fines',
            unit: 'EUR millions/year',
            weight: 0.60,
            direction: 'lower is better'
          },
          E2: {
            name: 'Productivity Loss',
            description: 'Economic productivity loss from grid disruptions',
            unit: 'EUR millions/year',
            weight: 0.40,
            direction: 'lower is better'
          }
        },
        totalWeight: 1.0
      },

      S: {
        name: 'Saturation',
        description: 'System saturation and constraint management',
        metrics: {
          S1: {
            name: 'Municipal Gen/Consumption',
            description: 'Local DER generation vs local consumption ratio',
            unit: 'ratio 0-2+',
            weight: 0.75,
            direction: 'optimum at 1.0'
          },
          S2: {
            name: 'Reverse Power Flow',
            description: 'Feeders with reverse power flow occurrence',
            unit: '% of feeders',
            weight: 0.15,
            direction: 'lower is better'
          },
          S3: {
            name: 'Criticality Class',
            description: 'Critical loads and system node classification',
            unit: 'ordinal 1-5',
            weight: 0.10,
            direction: 'context-dependent'
          }
        },
        totalWeight: 1.0
      },

      T: {
        name: 'Transition',
        description: 'Energy transition stress and DER integration',
        metrics: {
          T1: {
            name: 'DER Stress (Composite)',
            description: 'Distributed energy resource integration stress',
            unit: 'dimensionless 0-1',
            weight: 1.0,
            direction: 'lower is better',
            subMetrics: {
              DER_ratio: {
                name: 'DER Penetration Ratio',
                description: 'DER installed capacity / total capacity',
                unit: 'ratio 0-2+',
                weight: 0.50
              },
              DER_variability: {
                name: 'DER Variability Index',
                description: 'Coefficient of variation of renewable output',
                unit: 'dimensionless 0-1',
                weight: 0.30
              },
              EV_load_ratio: {
                name: 'EV Load Ratio',
                description: 'EV charging load / peak system load',
                unit: 'ratio 0-1',
                weight: 0.20
              }
            }
          }
        },
        totalWeight: 1.0
      }
    },

    // ===== MODIFIERS (Risk Multipliers & Adjustments) =====
    modifiers: {
      R2: {
        id: 'R2',
        name: 'Climate Trajectory',
        description: 'Adaptive weighting based on climate scenario and region-specific IRI trajectories',
        parameters: {
          scenarioRCP: 'RCP 4.5 / 8.5',
          adaptiveWeighting: 'dynamic by region and year'
        }
      },

      R3: {
        id: 'R3',
        name: 'Consequence Multiplier',
        description: 'Risk consequence adjustment based on population, load served, and social vulnerability',
        parameters: {
          populationExposure: 'sigmoid function',
          loadCriticality: 'weighted by end-user type',
          vulnerabilityIndex: 'aggregated from HEPI and census data'
        }
      },

      R4: {
        id: 'R4',
        name: 'Graph Criticality',
        description: 'Network topology-based criticality: degree centrality, betweenness, bridge identification',
        parameters: {
          degreeCentrality: 'normalized node connectivity',
          betweennessCentrality: 'flow criticality',
          bridgeIdentification: 'redundancy reduction risk'
        }
      },

      R5: {
        id: 'R5',
        name: 'Wildfire Risk',
        description: 'Wildfire exposure and climate-fire coupling (Mediterranean regions)',
        parameters: {
          kappaWildfire: '1.10 - 1.35 multiplier range',
          seasonality: 'peaked in summer months',
          regions: ['Peloponnese', 'Attica', 'Central Greece', 'Thessaly']
        }
      },

      R6a: {
        id: 'R6a',
        name: 'Restoration Speed',
        description: 'Mean time to restore (MTTR) and CAIDI-based recovery capability',
        parameters: {
          CAIDI: 'Customer Average Interruption Duration Index (minutes)',
          crewAvailability: 'regional crew density',
          remotenessIndex: 'accessibility multiplier'
        }
      },

      R6b: {
        id: 'R6b',
        name: 'Seismic Hazard',
        description: 'EAK 2003 seismic zone classification and hazard acceleration',
        parameters: {
          eakZones: 'I, II, III, IV classification',
          alphaPGA: '0.45 baseline hazard parameter',
          returnPeriod: '475 years (475-year maximum credible earthquake)'
        }
      },

      R7: {
        id: 'R7',
        name: 'Cyber Exposure',
        description: 'Cyber risk exposure based on DESI digital infrastructure index',
        parameters: {
          desiIndex: 'Digital Economy and Society Index component',
          scadaExposure: 'control system vulnerability assessment',
          communicationReliability: 'network redundancy and encryption'
        }
      },

      R8: {
        id: 'R8',
        name: 'Island Isolation',
        description: 'Special risk factor for island grids with limited interconnection',
        parameters: {
          kappaIsland: '0.80 - 1.05 multiplier range',
          islandsAffected: 'applies to all island peripheries',
          interconnectionCapacity: 'submarine cable reliability'
        }
      }
    },

    // ===== BANDS & CLASSIFICATION =====
    bands: {
      Low: {
        min: 0.0,
        max: 0.25,
        label: 'Low Risk',
        color: '#5d8563',
        description: 'Satisfactory sustainability and stability'
      },
      Medium: {
        min: 0.25,
        max: 0.50,
        label: 'Medium Risk',
        color: '#b8863a',
        description: 'Acceptable with monitoring required'
      },
      High: {
        min: 0.50,
        max: 0.75,
        label: 'High Risk',
        color: '#aa4234',
        description: 'Elevated concerns requiring mitigation'
      },
      Critical: {
        min: 0.75,
        max: 1.0,
        label: 'Critical Risk',
        color: '#941914',
        description: 'Urgent action required'
      }
    },

    colors: {
      Low: '#5d8563',
      Medium: '#b8863a',
      High: '#aa4234',
      Critical: '#941914',
      neutral: '#e8e8e8',
      accent: '#1a5f7a'
    },

    // ===== GREEK ADMINISTRATIVE REGIONS (Peripheries) =====
    regions: [
      {
        id: 'ATT',
        name: 'Attica',
        code: 'Attiki',
        type: 'Periphery',
        peakLoad: 'highest',
        characteristics: ['capital region', 'dense urban', 'largest population']
      },
      {
        id: 'CEN',
        name: 'Central Greece',
        code: 'Sterea Ellada',
        type: 'Periphery',
        characteristics: ['mainland', 'mixed urban-rural']
      },
      {
        id: 'CNS',
        name: 'Central Macedonia',
        code: 'Kentrike Makedonia',
        type: 'Periphery',
        characteristics: ['mainland', 'industrial', 'Thessaloniki']
      },
      {
        id: 'CRT',
        name: 'Crete',
        code: 'Kriti',
        type: 'Periphery - Island',
        characteristics: ['large island', 'isolated grid', 'tourist region']
      },
      {
        id: 'EMA',
        name: 'East Macedonia & Thrace',
        code: 'Anatoliki Makedonia kai Thraki',
        type: 'Periphery',
        characteristics: ['northernmost', 'land borders']
      },
      {
        id: 'EPR',
        name: 'Epirus',
        code: 'Epeiros',
        type: 'Periphery',
        characteristics: ['northwestern', 'mountainous', 'low load']
      },
      {
        id: 'ION',
        name: 'Ionian Islands',
        code: 'Ionia Nisia',
        type: 'Periphery - Island',
        characteristics: ['western islands', 'isolated grids', 'small systems']
      },
      {
        id: 'NMA',
        name: 'North Aegean',
        code: 'Voria Aigaio',
        type: 'Periphery - Island',
        characteristics: ['aegean islands', 'very isolated', 'minimal grids']
      },
      {
        id: 'PEL',
        name: 'Peloponnese',
        code: 'Peloponnisos',
        type: 'Periphery',
        characteristics: ['peninsula', 'mixed load', 'interconnected']
      },
      {
        id: 'SAE',
        name: 'South Aegean',
        code: 'Notia Aigaio',
        type: 'Periphery - Island',
        characteristics: ['aegean islands', 'isolated grids', 'tourist regions']
      },
      {
        id: 'THY',
        name: 'Thessaly',
        code: 'Thessalia',
        type: 'Periphery',
        characteristics: ['central-east', 'agricultural', 'moderate load']
      },
      {
        id: 'WMA',
        name: 'West Macedonia',
        code: 'Dytiki Makedonia',
        type: 'Periphery',
        characteristics: ['northwestern', 'mountainous', 'lignite generation']
      },
      {
        id: 'WGR',
        name: 'Western Greece',
        code: 'Dytiki Ellada',
        type: 'Periphery',
        characteristics: ['western mainland', 'mixed load']
      }
    ],

    // ===== PROCESSING PIPELINE =====
    pipeline: {
      steps: [
        {
          step: 1,
          name: 'Ingestion',
          description: 'Data collection from 30 verified sources in real-time and batch modes',
          outputs: ['raw_data_lake'],
          frequency: 'continuous'
        },
        {
          step: 2,
          name: 'Validation',
          description: 'Quality checks, outlier detection, completeness assessment against grid standards',
          outputs: ['validation_report'],
          frequency: 'continuous'
        },
        {
          step: 3,
          name: 'Normalisation',
          description: 'Unit conversion, temporal alignment (hourly/daily/monthly), spatial interpolation',
          outputs: ['normalized_metrics'],
          frequency: 'continuous'
        },
        {
          step: 4,
          name: 'Aggregation',
          description: 'Component-level calculation (C, V, I, E, S, T) with fixed weights',
          outputs: ['component_scores'],
          frequency: 'continuous'
        },
        {
          step: 5,
          name: 'Modifiers',
          description: 'Application of 8 risk modifiers (R2-R8): climate, consequence, topology, wildfire, restoration, seismic, cyber, island',
          outputs: ['adjusted_scores'],
          frequency: 'continuous'
        },
        {
          step: 6,
          name: 'Monte Carlo',
          description: '10,000 iterations for uncertainty quantification; 95% and 99% confidence bounds',
          outputs: ['mc_distributions', 'confidence_intervals'],
          frequency: 'daily'
        },
        {
          step: 7,
          name: 'Classification',
          description: 'Band assignment (Low/Medium/High/Critical) and dashboard publication',
          outputs: ['ssi_index', 'band_classification', 'dashboard'],
          frequency: 'daily'
        }
      ]
    },

    // ===== GREECE-SPECIFIC PARAMETERS =====
    greece_specific: {
      seismic_zones: {
        zone_I: {
          label: 'Zone I (Very Low Seismic Risk)',
          alpha: 0.12,
          regions: ['Ionian Islands (partial)'],
          description: 'Minimal seismic activity'
        },
        zone_II: {
          label: 'Zone II (Low Seismic Risk)',
          alpha: 0.24,
          regions: ['Western Greece', 'Epirus', 'parts of Central Greece'],
          description: 'Low seismic hazard'
        },
        zone_III: {
          label: 'Zone III (Moderate Seismic Risk)',
          alpha: 0.36,
          regions: ['Most of mainland Greece', 'Crete', 'South Aegean'],
          description: 'Moderate seismic hazard - EAK baseline'
        },
        zone_IV: {
          label: 'Zone IV (High Seismic Risk)',
          alpha: 0.45,
          regions: ['East Macedonia & Thrace', 'North Aegean', 'parts of Crete'],
          description: 'High seismic activity - monitoring essential'
        }
      },

      wildfire_parameters: {
        kappaWildfire: {
          baseline: 1.10,
          peak: 1.35,
          seasonality: 'May-September peak'
        },
        highRiskRegions: [
          'Peloponnese',
          'Attica',
          'Central Greece',
          'Thessaly',
          'parts of Crete'
        ],
        climateProjection: 'Extended fire season under RCP 8.5 scenarios'
      },

      island_systems: {
        major_islands: [
          'Crete',
          'Rhodes (South Aegean)',
          'Kos (South Aegean)',
          'Lesbos (North Aegean)',
          'Chios (North Aegean)',
          'Samos (North Aegean)',
          'Corfu (Ionian)',
          'Zakynthos (Ionian)',
          'Kefalonia (Ionian)',
          'Mykonos (South Aegean)',
          'Santorini (South Aegean)',
          'Naxos (South Aegean)',
          'Paros (South Aegean)'
        ],
        nonInterconnected: [
          'North Aegean islands',
          'Some South Aegean islands',
          'Ionian Islands (non-Corfu)'
        ],
        submarineCables: 'Limited interconnection capacity; priority for grid stability'
      },

      environmental_factors: {
        mediterraneanClimate: 'Hot, dry summers; mild, wet winters',
        snowIceRisk: 'Localized to mountainous regions and high-elevation areas',
        floodRisk: 'Rivers and torrents; urban drainage challenges',
        temperatureExtremes: 'Heatwaves common July-August; cold snaps December-February',
        vegetationZones: 'Mediterranean scrub, forests in northern/mountain regions'
      },

      regulatory_context: {
        primaryRegulator: 'RAE (Regulatory Authority for Energy)',
        gridOperator: 'ADMIE/IPTO (Independent Power Transmission Operator)',
        distributionCompanies: [
          'HEDNO (major)',
          'regional & municipal operators'
        ],
        euDirectives: 'Clean Energy Package, Network Codes, REMIT compliance',
        nationalPlan: 'Climate Neutrality 2050 with interim 2030 targets'
      }
    },

    // ===== UTILITY FUNCTIONS =====
    getBandForScore: function(score) {
      if (score < 0.25) return 'Low';
      if (score < 0.50) return 'Medium';
      if (score < 0.75) return 'High';
      return 'Critical';
    },

    getColorForScore: function(score) {
      const band = this.getBandForScore(score);
      return this.colors[band];
    },

    getRegionById: function(regionId) {
      return this.regions.find(r => r.id === regionId);
    },

    getSourceById: function(sourceId) {
      const allSources = [
        ...this.sources.tier1_core,
        ...this.sources.tier2_supplementary,
        ...this.sources.tier3_derived_proxy
      ];
      return allSources.find(s => s.id === sourceId);
    },

    // Retrieve all metrics across all components
    getAllMetrics: function() {
      const metrics = {};
      Object.keys(this.components).forEach(componentKey => {
        const component = this.components[componentKey];
        metrics[componentKey] = component.metrics;
      });
      return metrics;
    },

    // Get total number of sources by tier
    getSourceCounts: function() {
      return {
        tier1: this.sources.tier1_core.length,
        tier2: this.sources.tier2_supplementary.length,
        tier3: this.sources.tier3_derived_proxy.length,
        total: this.sources.tier1_core.length +
               this.sources.tier2_supplementary.length +
               this.sources.tier3_derived_proxy.length
      };
    }
  };
})();

// Export for module systems if available
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.SSI_META;
}
