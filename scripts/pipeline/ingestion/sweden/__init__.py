"""Sweden v4.23 L1 ingestion connector — Wave 4 P32.

🎉 NORDIC CLUSTER COMPLETION MILESTONE 🎉
2nd Wave 4 country. Post-Sweden: 5-of-5 Nordics v4.23-enhanced
(Iceland + Denmark + Finland + Norway + Sweden). Nordic cluster
COMPLETE.

Architecture: Wave 4 CORRECTED per UK P31 template.
  - out center query hint on way subs (100% coord capture)
  - out geom query hint on lines (proper polyline coords)
  - Compact {s, l, a} grid-geo schema (canonical)
  - Grid-based spatial index (0.1° cells, ~11 km, ~600× speedup)
  - 6-zone bbox-split fallback (SE1-SE4 + Gotland-Öland + Norrbotten)
  - Convention #80 grid-geo sharding integration (unlikely triggered
    — Sweden projected 30-45 MB well under 90 MB threshold)

Convention #78 BINDING 14TH ENFORCEMENT:
  Swedish + Sami (Northern/Southern/Lule) + Finnish/Meänkieli +
  English 4-language alias map with Swedish diacritics (ä å ö) +
  Sami special chars (ŧ ǧ) + Nordic language variants.

Convention #78 §4bis.5 Layer 3 10TH ENFORCEMENT:
  Stockholm metropolitan 2-way geofence (Ellevio Stockholm inner +
  Vattenfall Eldistribution Stockholm outer).

Discipline #36: 4.0 km cross-border tolerance (Nordic synchronous +
  6 HVDC subsea + Norwegian long AC land border + Stockholm skärgård
  30,000 islands + Gotland-Öland).

Discipline #41: baseline ratio 5.58 already ABOVE_HEALTHY_BAND;
  post-enhancement projected 8-15 (comparable to UK-post-enhancement).
"""

from ._base import (
    ALIAS_MAP,
    RESOLVER_LAYERS,
    STOCKHOLM_ELLEVIO_BBOX,
    STOCKHOLM_VATTENFALL_BBOX,
    SWEDEN_BBOX,
    resolve_operator,
)

__all__ = [
    "ALIAS_MAP",
    "RESOLVER_LAYERS",
    "STOCKHOLM_ELLEVIO_BBOX",
    "STOCKHOLM_VATTENFALL_BBOX",
    "SWEDEN_BBOX",
    "resolve_operator",
]
