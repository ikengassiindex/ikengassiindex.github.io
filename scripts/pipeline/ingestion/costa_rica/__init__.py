"""SSI Pipeline — Costa Rica v4.23 ingestion package.

Wave 2 Priority 13 (task #220). Third application of the monopoly-class
pattern with expanded 7-DSO nested overlay:
  - ICE (Instituto Costarricense de Electricidad): state-owned TSO+DSO
    majority default (~40% direct + all transmission ≥138 kV)
  - 7 non-ICE DSOs handle specific cantons via nested geofence overlay:
    * CNFL (ICE subsidiary, San José metro)
    * ESPH (municipal Heredia)
    * JASEC (municipal Cartago)
    * Coopeguanacaste RL (NW rural Guanacaste)
    * Coopelesca RL (San Carlos north Alajuela)
    * Coopesantos RL (Los Santos south San José)
    * Coopealfaroruiz RL (Zarcero canton NW Alajuela)

Note: Python package uses underscore (costa_rica); data path uses hyphen
(costa-rica/) per intelligence/countries.json slug convention.
"""
