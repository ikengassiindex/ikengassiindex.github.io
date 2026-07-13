"""SSI Pipeline — Colombia v4.23 ingestion package.

Wave 2 Priority 15 (task #230). Sixth region-jurisdiction × voltage-class
instance with LARGEST DSO cardinality yet (~30 DSOs vs Slovenia's 5):
  - ISA (Interconexión Eléctrica S.A.): state-linked TSO ≥220 kV
  - XM SA ESP: system operator spun out from ISA (non-owner of infrastructure)
  - 30+ regional distributors mapped by department name:
    * EPM (Antioquia) — largest municipal utility
    * Enel-Codensa (Bogotá + Cundinamarca) — Italian ENEL group
    * Emcali (Cali metro) + EPSA (rest of Valle del Cauca)
    * Air-e (Atlántico + Magdalena + La Guajira — former Electricaribe SW)
    * Afinia (Bolívar + Cesar + Córdoba + Sucre — former Electricaribe NE)
    * CENS (Norte de Santander) + EBSA (Boyacá) + Essa (Santander)
    * Chec (Eje Cafetero: Caldas + Quindío + Risaralda)
    * Cedenar (Nariño) + Electrohuila (Huila) + Enertolima (Tolima)
    * ~15 smaller regional utilities for remaining departments

Novel pattern: department-name lookup as primary Layer 2 (baseline 100%
populated with department names, cleanest resolver base yet).
"""
