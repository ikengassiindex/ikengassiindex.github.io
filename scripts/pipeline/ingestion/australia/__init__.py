"""SSI Pipeline — Australia v4.23 ingestion package.

Wave 2 Step 3 (task #185). Federal-fragmented + continental-scale.
Reuses Austria/Greenland patterns:
  - Federal-fragmented (like Austria) — no monopoly-fallback rule
  - Continental-scale bbox partitioning (like Greenland) — 8 state/territory partitions
  - State-jurisdiction fallback by voltage class + metro/rural geofence for
    the untagged tail (Australia-specific extension)
"""
