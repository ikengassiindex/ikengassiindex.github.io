"""SSI Pipeline — Belgium v4.23 ingestion package.

Wave 2 Priority 7 (task #190). Federal-fragmented compact EU country.
Reuses Austria pattern:
  - Federal-fragmented (3 regions × distinct DNSPs) — no monopoly rule
  - Single-query bbox (small — 30k km²) — no partitioning
  - Region-jurisdiction fallback by voltage class + Liege metro geofence
"""
