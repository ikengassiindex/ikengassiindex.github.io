"""
SSI Index v4.3 workstream — Mexico ingestion package.

Priority 3 Mexico workstream (Editorial Calendar Q4 2026).

Connectors:
  - osm_overpass.py   MX-C1  OSM Overpass API (primary — federal-canonical unavailable)

Discovery + empirical anchors:
  - mexico/v4_3-ingestion-audit-mexico-preflight.yaml (Step 1)
  - mexico/v4_3-ingestion-audit-mexico-fetch.yaml (Step 2)

Architectural distinctions vs Canada + Norway:
  - Federal-canonical data ARCHITECTURALLY CLOSED (CENACE, SENER, CFE, CRE all
    behind interactive UIs / PDFs — none machine-accessible from cloud)
  - OSM Overpass empirically confirmed as PRIMARY canonical (3,097 substations)
  - CFE-monopoly market structure (92.4% of tagged operators = CFE variants) —
    default-fallback rule fills operator on 83% of untagged substations
  - Distribution grid essentially absent from OSM (1% of voltage-tagged subs
    at <33 kV) — DEFERRED to Phase 2 CFE Distribución PDF extraction

Architectural discipline:
  - Discipline #36 cross-border filter — default 100m tolerance
    (US border longest single-border in v4.3 at 3,145 km; no fjord complexity)
  - Discipline #41 line-substation pairing preserved
  - Convention #56 visibly-honest degradation — missing OSM tags → None,
    not fabricated defaults
  - Convention #60 non-commercial provenance — OSM + INEGI DENUE (public,
    ODbL + government-open-data licence) only

Phase 2+ candidates (queued):
  - MX-C2 INEGI DENUE SCIAN 2211 enrichment (needs operator-registered API token)
  - MX-C3 CENACE PRODESEN PDF extraction (10-15 engineer-days)
  - MX-C4 16 CFE Distribución divisiones PDFs (4-8 engineer-days per division)
"""
