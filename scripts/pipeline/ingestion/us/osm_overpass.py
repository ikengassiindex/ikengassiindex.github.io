"""US P39 Wave 4 — OSM Overpass API fetcher.

Portugal P33 bi-directional Option B pattern INHERITED with
US-specific 14-zone bbox architecture (12 main zones + 3 territory
subzones combined into US Territories macro-zone).

US-specific architecture:
  - 14-zone bbox split covering continental 48 + Alaska + Hawaii + 3
    territory subzones (PR+USVI + Guam+Mariana + American Samoa)
  - US 9.83M km² (2nd cohort-wide after Canada)
  - 4-continent territorial reach (mainland + Caribbean + Pacific +
    Alaska Arctic + Hawaii)
  - Anti-meridian crossing (Alaska Aleutians + Guam/Mariana Western Pacific)
  - 3-Interconnection triple-frequency-island system
  - ~3,200+ utilities (~3.5× Germany's 900 DSO fragmentation)
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Emits per-country cache files:
  us/_cache/overpass-subs-raw.json (aggregated 14 zones)
  us/_cache/overpass-lines-raw.json (aggregated 14 zones)

Convention #56: partial-fetch preserved end-to-end (HIGH likelihood
of multiple zone 504-timeouts for California + Texas + Northeast +
Southeast dense metros; cooldown-retry recipe from Germany P38
anticipated to apply repeatedly).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

import requests

# ─────────────────────────────────────────────────────────────
# Endpoint configuration + retry policy
# ─────────────────────────────────────────────────────────────

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

REQUEST_TIMEOUT_S = 120
OVERPASS_QL_TIMEOUT_S = 180  # Bumped from 120 for larger US zones


_HTTP_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ssi-index-foundation/v4.23",
}


# ─────────────────────────────────────────────────────────────
# US 14-zone bbox architecture
# ─────────────────────────────────────────────────────────────

US_ZONES = [
    {
        "id": "northeast",
        "bbox": (37.90, -80.52, 47.46, -66.90),
        "description": "Northeast (ME + NH + VT + MA + RI + CT + NY + NJ + PA + DE + MD + DC)",
    },
    # Southeast split into 2 subzones (originally single zone, but 11 states
    # + dense Miami/Atlanta/Nashville/New Orleans metros = too large for
    # single Overpass query — 18-attempt total failure across 2 rounds).
    # Split by latitude at 35.0°N. Bbox-split fix per Convention #56
    # cooldown-retry pattern extended to systemic-query-size failures.
    {
        "id": "southeast_north",
        "bbox": (35.00, -94.05, 39.14, -75.24),
        "description": "Southeast North (VA + WV + NC + SC + KY + TN) — split from original southeast zone",
    },
    {
        "id": "southeast_south",
        "bbox": (24.40, -94.05, 35.00, -75.24),
        "description": "Southeast South (GA + FL + AL + MS + LA + parts SC/TN) — split from original southeast zone",
    },
    {
        "id": "great_lakes",
        "bbox": (37.77, -97.24, 49.38, -80.52),
        "description": "Great Lakes (OH + MI + IN + IL + WI + MN)",
    },
    {
        "id": "plains",
        "bbox": (33.00, -104.05, 49.00, -89.09),
        "description": "Plains (IA + MO + AR + KS + NE + SD + ND)",
    },
    {
        "id": "texas",
        "bbox": (25.84, -106.65, 36.50, -93.51),
        "description": "Texas (largest single US state, own zone — ERCOT isolated grid)",
    },
    {
        "id": "southwest",
        "bbox": (31.33, -114.82, 37.00, -94.43),
        "description": "Southwest (OK + NM + AZ)",
    },
    {
        "id": "mountain",
        "bbox": (35.00, -117.24, 49.00, -102.04),
        "description": "Mountain (CO + UT + WY + MT + ID + NV)",
    },
    {
        "id": "california",
        "bbox": (32.53, -124.48, 42.01, -114.13),
        "description": "California (whole state — dense metros, likely cooldown-retry candidate like Germany Bayern+BW)",
    },
    {
        "id": "pacific_nw",
        "bbox": (41.99, -124.85, 49.00, -116.46),
        "description": "Pacific Northwest (OR + WA)",
    },
    {
        "id": "alaska",
        "bbox": (51.20, -179.15, 71.60, -129.98),
        "description": "Alaska (Arctic + Aleutian chain — approaches anti-meridian; Aleutians -180° to -170°)",
    },
    {
        "id": "hawaii",
        "bbox": (18.91, -160.25, 22.24, -154.75),
        "description": "Hawaii (6 islands ISOLATED grids each; no submarine interconnectors between islands)",
    },
    {
        "id": "puerto_rico_usvi",
        "bbox": (17.62, -67.98, 18.60, -64.50),
        "description": "Puerto Rico + US Virgin Islands (Caribbean territories ISOLATED grids)",
    },
    {
        "id": "guam_mariana",
        "bbox": (13.20, 144.60, 20.60, 146.10),
        "description": "Guam + Northern Mariana Islands (Western Pacific territories, ANTI-MERIDIAN crossing bbox)",
    },
    {
        "id": "american_samoa",
        "bbox": (-14.55, -170.85, -14.15, -169.40),
        "description": "American Samoa (South Pacific territory — smallest US zone)",
    },
]


# ─────────────────────────────────────────────────────────────
# Overpass QL query templates
# ─────────────────────────────────────────────────────────────


def _build_subs_query(bbox: tuple[float, float, float, float]) -> str:
    """Substation query — Wave 4 with `out center`."""
    lat_min, lon_min, lat_max, lon_max = bbox
    return f"""
[out:json][timeout:{OVERPASS_QL_TIMEOUT_S}];
(
  node["power"="substation"]({lat_min},{lon_min},{lat_max},{lon_max});
  way["power"="substation"]({lat_min},{lon_min},{lat_max},{lon_max});
  relation["power"="substation"]({lat_min},{lon_min},{lat_max},{lon_max});
);
out center;
""".strip()


def _build_lines_query(bbox: tuple[float, float, float, float]) -> str:
    """Line query — Portugal P33 bi-directional Option B extended (INHERITED).

    Includes power=minor_line for wooden-pole rural MV distribution
    (US rural MV distribution VERY SIGNIFICANT in Appalachia + Ozarks +
    Great Plains + Rockies + Alaska rural + Puerto Rico rural +
    Native American reservations).
    """
    lat_min, lon_min, lat_max, lon_max = bbox
    return f"""
[out:json][timeout:{OVERPASS_QL_TIMEOUT_S}];
(
  way["power"="line"]({lat_min},{lon_min},{lat_max},{lon_max});
  way["power"="cable"]({lat_min},{lon_min},{lat_max},{lon_max});
  way["power"="minor_line"]({lat_min},{lon_min},{lat_max},{lon_max});
);
out geom;
""".strip()


# ─────────────────────────────────────────────────────────────
# Endpoint fallback + retry
# ─────────────────────────────────────────────────────────────


def _post_overpass(query: str, label: str) -> Optional[dict]:
    """POST query with 3-endpoint fallback + exponential backoff."""
    for endpoint_idx, endpoint in enumerate(OVERPASS_ENDPOINTS):
        for attempt in range(3):
            try:
                print(
                    f"[{label}] endpoint {endpoint_idx + 1}/3 attempt {attempt + 1}/3 "
                    f"→ {endpoint}"
                )
                response = requests.post(
                    endpoint,
                    data={"data": query},
                    headers=_HTTP_HEADERS,
                    timeout=REQUEST_TIMEOUT_S,
                )
                if response.status_code == 200:
                    print(f"[{label}] ✓ HTTP 200 ({len(response.content):,} bytes)")
                    return response.json()
                elif response.status_code in (429, 504):
                    backoff = 30 * (attempt + 1)
                    print(
                        f"[{label}] ⚠ HTTP {response.status_code} rate-limit/"
                        f"timeout, backing off {backoff}s"
                    )
                    time.sleep(backoff)
                elif response.status_code == 406:
                    print(f"[{label}] ⚠ HTTP 406 Not Acceptable — try next endpoint")
                    break
                else:
                    print(f"[{label}] ⚠ HTTP {response.status_code}")
                    time.sleep(15)
            except requests.RequestException as e:
                print(f"[{label}] ⚠ request failed: {e}")
                time.sleep(15)
    print(f"[{label}] ✗ ALL ENDPOINTS FAILED")
    return None


# ─────────────────────────────────────────────────────────────
# Fetchers — 14-zone architecture for both subs + lines
# ─────────────────────────────────────────────────────────────


def _fetch_zoned(cache_dir: Path, kind: str, query_builder) -> dict:
    """Generic 14-zone fetch."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"overpass-{kind}-raw.json"
    if cache_path.exists():
        print(f"[{kind}] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[{kind}] bbox-split fetching {len(US_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in US_ZONES:
        zone_cache_path = cache_dir / f"overpass-{kind}-{zone['id']}.json"
        if zone_cache_path.exists():
            print(f"[{kind}/{zone['id']}] cache hit → {zone_cache_path}")
            zone_result = json.loads(zone_cache_path.read_text())
        else:
            print(f"[{kind}/{zone['id']}] {zone['description']}")
            print(f"[{kind}/{zone['id']}] bbox {zone['bbox']}")
            query = query_builder(zone["bbox"])
            zone_result = _post_overpass(query, f"{kind}/{zone['id']}")
            if zone_result is None:
                failed_zones.append(zone["id"])
                partial_fetch = True
                print(
                    f"[{kind}/{zone['id']}] ✗ zone failed — "
                    f"Convention #56 partial-fetch"
                )
                continue
            zone_cache_path.write_text(json.dumps(zone_result))
            print(f"[{kind}/{zone['id']}] cached → {zone_cache_path}")

        n_zone_elements = len(zone_result.get("elements", []))
        print(f"[{kind}/{zone['id']}] +{n_zone_elements:,} elements")
        all_elements.extend(zone_result.get("elements", []))

        time.sleep(5)

    assembled = {
        "version": 0.6,
        "generator": f"SSI Index Foundation US P39 Wave 4 14-zone {kind}",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[{kind}] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(US_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[{kind}] ✓ assembled {len(all_elements):,} total {kind} elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[{kind}] cached → {cache_path}")
    return assembled


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch US subs across 14 zones."""
    return _fetch_zoned(cache_dir, "subs", _build_subs_query)


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch US lines across 14 zones."""
    return _fetch_zoned(cache_dir, "lines", _build_lines_query)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    cache_dir = Path("us/_cache")
    print("═" * 70)
    print("US P39 Wave 4 — OSM Overpass fetch — 🏆 FINAL TERMINAL CLOSURE")
    print("🇺🇸 14-zone (12 main + 3 territory subzones)")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ US P39 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
