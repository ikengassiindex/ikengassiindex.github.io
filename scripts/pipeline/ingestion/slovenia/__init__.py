"""SSI Pipeline — Slovenia v4.23 ingestion package.

Wave 2 Priority 12 (task #215). Fifth application of the region-jurisdiction ×
voltage-class fallback pattern:
  - ELES d.o.o. (state-owned TSO) attributed at ≥110 kV
  - 5 regional DSOs mapped to NUTS-3 territories (SI### codes):
    * Elektro Ljubljana:  SI041 + SI037 + SI038 + SI036 (central Slovenia)
    * Elektro Maribor:    SI032 + SI033 + SI031 (NE)
    * Elektro Celje:      SI043 + SI034 (central-east Savinjska)
    * Elektro Gorenjska:  SI042 (NW Alps)
    * Elektro Primorska:  SI044 + SI035 (W + coast)
"""
