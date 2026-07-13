"""SSI Pipeline — Hungary v4.23 ingestion package.

Wave 2 Priority 10 (task #205). EU cluster continuation.
Reuses Belgium/Netherlands region-jurisdiction × voltage-class pattern:
  - Post-2020 E.ON Hungária consolidation of all Hungarian DSOs
  - 2-DSO fallback: ELMŰ-ÉMÁSZ (Budapest + Northeast) + E.ON Hungária (rest)
  - MAVIR TSO ≥120 kV
  - NUTS-3 code + lat/lon dual-mode geofence
  - Case-insensitive alias normalisation with accented character support
    (ELMŰ ↔ ELMÜ, ÉMÁSZ, DÉMÁSZ pre-2018 → E.ON Hungária)
"""
