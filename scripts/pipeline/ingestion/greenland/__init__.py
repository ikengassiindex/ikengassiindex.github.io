"""
SSI Index v4.23 workstream — Greenland ingestion package.

Priority 5 Greenland workstream (Editorial Calendar Q1 2027).

Connectors:
  - osm_overpass.py            GL-C1  OSM Overpass API (primary — federal-canonical
                                      Nukissiorfiit data behind static PDF tariff
                                      schedules only, not machine-accessible)
  - merge_into_ssi_data.py     Step 4/5 federation merger (subs + lines one-shot)

Discovery + empirical anchors:
  - greenland/v4_23-ingestion-audit-greenland-preflight.yaml (Step 1)
  - greenland/v4_23-ingestion-audit-greenland-fetch.yaml     (Step 2)
  - greenland/v4_23-ingestion-audit-greenland-delta.yaml     (Step 4)
  - greenland/v4_23-ingestion-audit-greenland-merge.yaml     (Step 5)

Architectural distinctions vs Canada + Norway + Mexico + Austria:
  - SMALLEST v4.23 country (44 OSM subs + ~112 lines vs Austria 15,213 + 70,964)
  - PURE MONOPOLY market — Nukissiorfiit is the ONLY electricity utility for
    the entire country (state-owned + 100% market share).  Empirically confirmed:
    100% of tagged operators in BOTH substations (28/28) AND lines (2/2) are
    "Nukissiorfiit".  Unlike Mexico's CFE-monopoly (had industrial self-gen
    exceptions), Greenland has ZERO exceptions — safe to apply monopoly
    fallback with 100% confidence on the ~36% untagged sub tail + ~98%
    untagged line tail.
  - VALIDATION workstream not GROWTH workstream — existing baseline has 37 subs
    + 125 lines vs OSM's 44 + ~112.  Line densification opportunity is
    minimal or NEGATIVE (baseline richer than OSM).
  - Mode 2 fjord tolerance (5 km) — inherited via Discipline #36 task #60
    remediation.  88.7% ice cover + extreme coastline complexity require the
    larger tolerance envelope.
  - ~80 isolated settlement microgrids (no interconnected national grid).
    Each with own generation mix (hydro + diesel + wind).
  - NO bbox partitioning needed — Greenland's small OSM footprint fits in
    single-query per element type.  Simpler than Austria's 4-quadrant sweep.
"""
