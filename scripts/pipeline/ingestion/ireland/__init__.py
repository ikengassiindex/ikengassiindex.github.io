"""Ireland v4.23 substation + power-line ingestion package.

Wave 3 Priority 25 (fourth Wave 3 country; smallest-first cadence
post-Switzerland at 994 baseline subs).

Architecture (SIMPLER than Switzerland via single-DSO simplification):
- EirGrid federal TSO ≥110 kV (established 2006 via BFE unbundling
  from ESB Group per EU 3rd Package)
- ESB Networks SINGLE national DSO covering ALL 26 Republic of Ireland
  counties (analogous to Greek DEDDIE simplification)
- SONI sister TSO in Northern Ireland (SEM/I-SEM coordination)
- Moyle Interconnector 500 MW HVDC (undersea to Scotland/GB)
- East-West Interconnector 500 MW HVDC (undersea to Wales/GB)
- Northern Ireland AC land border (~500 km, excluded via bounds.json)

Convention #78 BINDING 7th enforcement:
- English-language DOMINANT (~90% of operator= tags)
- 🆕 FIRST English-language Wave 3 country cohort event
- Minimal Gaeilge (Irish) diacritics (á é í ó ú + Éirid)
- Legal-form variants: Ltd + Limited + plc + DAC + Teoranta + Teo +
  Cuideachta (English + Gaeilge)
- Predecessor rebrand: ESB Distribution → ESB Networks 2010 (15-yr legacy)

Convention #78 §4bis.5 Layer 3 geofence NOT NEEDED — single national
DSO covers Dublin metropolitan area + all 26 counties (Greek DEDDIE
precedent applies).

Author: ikenga-ssi-foundation
Date: 17 July 2026
"""
