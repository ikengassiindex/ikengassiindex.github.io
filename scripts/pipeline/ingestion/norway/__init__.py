"""
SSI Index v4.23 workstream — Norway ingestion package.

Priority 2 Norway workstream (Editorial Calendar Q4 2026).

Connectors:
  - nve_nettanlegg.py   NO-C1  NVE Nettanlegg WFS (federal canonical)
                              — EL_Transformatorstasjon (substations)
                              — EL_Luftlinje (overhead lines with spenning)
                              — EL_Sjøkabel (submarine cables)

Discovery + empirical anchors:
  - norway/v4_23-ingestion-audit-norway-preflight.yaml (Step 1)
  - norway/v4_23-ingestion-audit-norway-fetch.yaml (Step 2)
  - norway/v4_23-ingestion-audit-norway-line-schema.yaml (Step 2b)

Architectural discipline:
  - Discipline #36 cross-border filter — 5 km fjord tolerance
    (norway/cross_border_tolerances.json Mode 2)
  - Discipline #41 line-coupling — REVERSE inheritance:
    line-carries-spenning → endpoint-substation-inherits via 500m proximity
  - Convention #56 visibly-honest degradation — missing spenning → 0.0
  - Convention #60 non-commercial provenance — NVE + Statnett only
"""
