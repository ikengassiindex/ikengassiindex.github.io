"""
SSI Index v4.23 workstream — Austria ingestion package.

Priority 4 Austria workstream (Editorial Calendar Q1 2027).

Connectors:
  - osm_overpass.py            AT-C1  OSM Overpass API (primary — federal-canonical unavailable)
  - merge_into_ssi_data.py     Step 4 federation merger (subs + lines one-shot)

Discovery + empirical anchors:
  - austria/v4_23-ingestion-audit-austria-preflight.yaml (Step 1)
  - austria/v4_23-ingestion-audit-austria-fetch.yaml     (Step 2)
  - austria/v4_23-ingestion-audit-austria-delta.yaml     (Step 4a — arch anchors)
  - austria/v4_23-ingestion-audit-austria-merge.yaml     (Step 4b — pending operator local)

Architectural distinctions vs Canada + Norway + Mexico:
  - Federal-canonical machine-accessible data unavailable (APG TSO + E-Control
    regulator + data.gv.at CKAN all behind interactive UIs / PDFs from cloud IPs)
  - OSM Overpass empirically confirmed as PRIMARY canonical (15,213 substations
    — 20× ratio vs existing 741 baseline, LARGEST in v4.23)
  - BEST-IN-COHORT OSM tagging discipline: 77.2% operator + 79.8% voltage +
    75% name (vs Mexico 16.6% operator; vs Norway ~30% pre-NVE)
  - FRAGMENTED market structure — 9 distinct utilities dominant (APG TSO +
    Wiener Netze + 7 Bundesland DSOs + ÖBB railway traction)
  - NO monopoly-fallback rule needed (unlike Mexico's CFE-monopoly rule)
  - Convention #56 visibly-honest degradation applies only to ~23% untagged tail

Architectural discipline:
  - Discipline #36 cross-border filter — default 100m tolerance
    (Austria bounds already Mode-2 remediated per task #56, 2026-06-24)
  - Discipline #41 line-substation pairing preserved
  - Convention #56 visibly-honest degradation — missing OSM tags → None,
    not fabricated defaults
  - Convention #60 non-commercial provenance — OSM (ODbL) only; ENTSO-E
    Transparency Platform queued as Phase 2 candidate (open, needs token)

Merge strategy (Option A — subs + lines one-shot):
  - Unlike Mexico Step 5 (subs only, lines deferred to Step 5b for operator
    residential-IP execution), Austria connector supports ingest_lines=True by
    default and Overpass rate-limit posture allows one-shot from local Mac.
  - Line densification uses 100m midpoint + voltage-tier dedupe against
    existing austria/grid-geo.json 'l' array.
  - Sandbox execution deferred to operator local per Mexico Step 5b precedent
    (45s bash timeout < ~57s subs + ~30-90s lines cumulative wall-clock).

Phase 2+ candidates (queued):
  - AT-C2 ENTSO-E Transparency Platform (APG-tier transmission enrichment)
  - AT-C3 Bundesländer INSPIRE-compliant WFS federation (Vienna wien.gv.at + Salzburg + etc.)
"""
