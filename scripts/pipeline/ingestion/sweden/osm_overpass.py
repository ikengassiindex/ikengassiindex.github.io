"""Sweden P32 Wave 4 — OSM Overpass API fetcher.

Wave 4 CORRECTED architecture:
  - `out center` query hint on WAY subs (100% coord capture — UK P31
    proved this fix vs. Turkey P30's 91% miss rate)
  - `out geom` query hint on LINES (proper polyline geometry)
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - 6-zone bbox-split fallback for lines IF single-bbox query fails
  - HTTP headers Accept: application/json + User-Agent (Turkey P30
    rate-limit lesson)
  - Sweden 447k km² area (2× UK); single-bbox line query may exceed
    endpoint payload limits — bbox-split has been engineered from
    Wave 3 experience.

Emits per-country cache files:
  sweden/_cache/overpass-subs-raw.json
  sweden/_cache/overpass-lines-raw.json (may be assembled from 6 zone files)

Convention #56: partial-fetch preserved end-to-end. If 1-of-6 zones
fails during bbox-split, the assembled lines file carries a
`_partial_fetch: true` flag with the failed zones enumerated.
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

# Turkey P30 rate-limit lesson: 120s ceiling vs prior 180s
REQUEST_TIMEOUT_S = 120
OVERPASS_QL_TIMEOUT_S = 120

_HTTP_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ssi-index-foundation/v4.23",
}


# ─────────────────────────────────────────────────────────────
# Sweden national bbox (single-bbox subs query)
# ─────────────────────────────────────────────────────────────

# Sweden 55.34°/69.06° lat × 10.96°/24.17° lon
SWEDEN_BBOX = (55.34, 10.96, 69.06, 24.17)


# ─────────────────────────────────────────────────────────────
# 6-zone bbox-split fallback for LINE query (Wave 4 architecture)
# ─────────────────────────────────────────────────────────────
# Sweden's 447k km² area 2× UK. Single-bbox line query with `out geom`
# hint may exceed endpoint payload limits. Bbox-split partitions the
# country into 6 zones aligned with Terna-style bidding-zone geography:
#
# SE1_NORRLAND_NORTH  — Norrbotten + northern Västerbotten (Luleå/Kiruna)
# SE2_NORRLAND_SOUTH  — Southern Västerbotten + Norrland (Umeå/Sundsvall)
# SE3_NORTH           — Northern SE3 (Falun/Gävle/Uppsala corridor)
# SE3_SOUTH           — Southern SE3 (Stockholm/Göteborg/Örebro/Linköping)
# SE4                 — Southern Sweden (Malmö/Öresund/Blekinge/Skåne)
# GOTLAND_ÖLAND       — Islands (2 largest Baltic islands)

SWEDEN_LINE_BBOX_ZONES = [
    {
        "id": "se1_norrland_north",
        "bbox": (65.50, 15.00, 69.06, 24.17),  # South Boden → Treriksröset
        "description": "SE1 Norrland North (Luleå + Kiruna + Boden + Gällivare)",
    },
    {
        "id": "se2_norrland_south",
        "bbox": (61.50, 12.00, 65.50, 21.00),  # Sundsvall → Boden
        "description": "SE2 Norrland South (Umeå + Sundsvall + Östersund)",
    },
    {
        "id": "se3_north",
        "bbox": (59.20, 12.00, 61.50, 19.50),  # Uppsala → Sundsvall
        "description": "SE3 North (Uppsala + Gävle + Falun + Karlstad north)",
    },
    {
        "id": "se3_south",
        "bbox": (57.60, 10.96, 59.60, 19.50),  # Göteborg → Stockholm
        "description": "SE3 South (Stockholm + Göteborg + Örebro + Linköping)",
    },
    {
        "id": "se4",
        "bbox": (55.34, 12.00, 57.60, 16.50),  # Malmö → Kalmar
        "description": "SE4 South (Malmö + Öresund + Helsingborg + Kalmar)",
    },
    {
        "id": "gotland_oland",
        "bbox": (55.90, 16.00, 58.10, 19.30),  # Gotland + Öland
        "description": "Gotland + Öland (2 largest Baltic islands)",
    },
]


# ─────────────────────────────────────────────────────────────
# Overpass QL query templates
# ─────────────────────────────────────────────────────────────


def _build_subs_query(bbox: tuple[float, float, float, float]) -> str:
    """Substation query — Wave 4 architecture with `out center`.

    `out center` on ways emits center-of-mass lat/lon for each way,
    ensuring 100% coord capture (UK P31 fix vs Turkey P30 91% miss).
    """
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
    """Line query — Wave 4 architecture with `out geom`.

    `out geom` on ways emits full polyline geometry (list of nd coord
    pairs) for each way, enabling direct polyline conversion in the
    merger without a second Overpass roundtrip.

    OPTION B PATCH (Sweden P32 line-regression fix):
      - Added `power=minor_line` for Nordic MV distribution coverage.
        Sweden OSM community populates minor_line heavily for the
        wooden-pole 10-40 kV rural distribution network. Excluding
        it dropped Wave 4 line count 53% below baseline mixed-source.
      - Same pattern applies to Norway + Finland + Denmark
        post-baseline. Future Nordic re-refreshes should inherit.
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
    """POST query with 3-endpoint fallback + exponential backoff.

    Returns parsed JSON on success, None if all endpoints fail.
    """
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
                    print(
                        f"[{label}] ⚠ HTTP 406 Not Acceptable — try next endpoint"
                    )
                    break  # abandon this endpoint immediately
                else:
                    print(f"[{label}] ⚠ HTTP {response.status_code}")
                    time.sleep(15)
            except requests.RequestException as e:
                print(f"[{label}] ⚠ request failed: {e}")
                time.sleep(15)
    print(f"[{label}] ✗ ALL ENDPOINTS FAILED")
    return None


# ─────────────────────────────────────────────────────────────
# Fetchers
# ─────────────────────────────────────────────────────────────


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch Sweden national bbox substations."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "overpass-subs-raw.json"
    if cache_path.exists():
        print(f"[subs] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    query = _build_subs_query(SWEDEN_BBOX)
    print(f"[subs] fetching Sweden national bbox: {SWEDEN_BBOX}")
    result = _post_overpass(query, "subs")
    if result is None:
        print("[subs] ✗ FATAL — cannot proceed without substations")
        sys.exit(1)

    n_elements = len(result.get("elements", []))
    print(f"[subs] ✓ {n_elements:,} raw OSM elements fetched")
    cache_path.write_text(json.dumps(result))
    print(f"[subs] cached → {cache_path}")
    return result


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch lines via bbox-split fallback (6 zones).

    Sweden's large area + `out geom` payload size guarantees single-
    bbox query will fail. Skip straight to bbox-split.

    Convention #56: if 1-of-6 zones fails, assembled file carries
    `_partial_fetch: true` flag with failed zones enumerated.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "overpass-lines-raw.json"
    if cache_path.exists():
        print(f"[lines] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[lines] bbox-split fetching {len(SWEDEN_LINE_BBOX_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in SWEDEN_LINE_BBOX_ZONES:
        zone_cache_path = cache_dir / f"overpass-lines-{zone['id']}.json"
        if zone_cache_path.exists():
            print(f"[lines/{zone['id']}] cache hit → {zone_cache_path}")
            zone_result = json.loads(zone_cache_path.read_text())
        else:
            print(f"[lines/{zone['id']}] {zone['description']}")
            print(f"[lines/{zone['id']}] bbox {zone['bbox']}")
            query = _build_lines_query(zone["bbox"])
            zone_result = _post_overpass(query, f"lines/{zone['id']}")
            if zone_result is None:
                failed_zones.append(zone["id"])
                partial_fetch = True
                print(f"[lines/{zone['id']}] ✗ zone failed — Convention #56 partial-fetch")
                continue
            zone_cache_path.write_text(json.dumps(zone_result))
            print(f"[lines/{zone['id']}] cached → {zone_cache_path}")

        n_zone_elements = len(zone_result.get("elements", []))
        print(f"[lines/{zone['id']}] +{n_zone_elements:,} elements")
        all_elements.extend(zone_result.get("elements", []))

        # Polite pause between zones
        time.sleep(5)

    # Assemble aggregate file
    assembled = {
        "version": 0.6,
        "generator": "SSI Index Foundation Sweden P32 Wave 4 bbox-split",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[lines] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(SWEDEN_LINE_BBOX_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[lines] ✓ assembled {len(all_elements):,} total line elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[lines] cached → {cache_path}")
    return assembled


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    """Fetch Sweden P32 subs + lines to cache."""
    cache_dir = Path("sweden/_cache")
    print("═" * 70)
    print("Sweden P32 Wave 4 — OSM Overpass fetch")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ Sweden P32 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
