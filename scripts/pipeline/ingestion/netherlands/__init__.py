"""SSI Pipeline — Netherlands v4.23 ingestion package.

Wave 2 Priority 8 (task #195). Federal-fragmented compact EU country.
Reuses Belgium pattern:
  - Federal-fragmented (12 provinces × 6 DSOs post-2011 splitsingswet unbundling)
  - Single-query bbox (~42k km², slightly larger than Belgium's 30k)
  - Region-jurisdiction fallback by voltage class + geofence for small DSOs
  - DSO alias normalisation (Enduris → Stedin; Alliander → Liander; historical
    pre-2011 Nuon/Essent/Eneco tags preserved as osm_original_operator)
"""
