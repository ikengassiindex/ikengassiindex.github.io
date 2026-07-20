"""France P37 Wave 4 — OSM Overpass API fetcher.

Portugal P33 bi-directional Option B pattern INHERITED with
France-specific voltage defaults.

France-specific architecture:
  - 11-zone bbox-split: 5 mainland zones (North + Center + South +
    West Bretagne + East Alsace-Lorraine-Alpes) + Corsica + 5 DOM
    territories (Guadeloupe + Martinique + Guyane + Réunion +
    Mayotte + Saint-Pierre-et-Miquelon)
  - France mainland 552k km² (larger than Spain 493k km²)
  - DOM territories globally distributed (Caribbean + Indian Ocean +
    South America + North Atlantic)
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Emits per-country cache files:
  france/_cache/overpass-subs-raw.json (aggregated 11 zones)
  france/_cache/overpass-lines-raw.json (aggregated 11 zones)

Convention #56: partial-fetch preserved end-to-end.
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
OVERPASS_QL_TIMEOUT_S = 120

_HTTP_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ssi-index-foundation/v4.23",
}


# ─────────────────────────────────────────────────────────────
# France 11-zone bbox architecture (5 mainland + Corsica + 5 DOM)
# ─────────────────────────────────────────────────────────────

FRANCE_ZONES = [
    {
        "id": "mainland_north",
        "bbox": (48.50, -1.50, 51.10, 4.50),
        "description": "Mainland North (Hauts-de-France + Île-de-France + Normandie + Grand Est west)",
    },
    {
        "id": "mainland_center",
        "bbox": (45.50, -1.50, 48.50, 5.50),
        "description": "Mainland Center (Centre-Val de Loire + Bourgogne-Franche-Comté + Pays de la Loire east + Grand Est center)",
    },
    {
        "id": "mainland_south",
        "bbox": (42.30, -1.50, 45.50, 7.80),
        "description": "Mainland South (Nouvelle-Aquitaine south + Occitanie + Provence-Alpes-Côte d'Azur + Auvergne-Rhône-Alpes south)",
    },
    {
        "id": "mainland_west",
        "bbox": (46.20, -5.15, 48.50, -0.80),
        "description": "Mainland West (Bretagne + Pays de la Loire west + Nouvelle-Aquitaine north)",
    },
    {
        "id": "mainland_east",
        "bbox": (45.50, 5.50, 49.20, 9.60),
        "description": "Mainland East (Alsace + Lorraine + Franche-Comté + Auvergne-Rhône-Alpes east + Alpes)",
    },
    {
        "id": "corsica",
        "bbox": (41.30, 8.50, 43.05, 9.65),
        "description": "Corsica (Corse ISLANDED via SACOI HVDC to Sardinia+Italy)",
    },
    {
        "id": "guadeloupe",
        "bbox": (15.83, -61.85, 16.52, -61.00),
        "description": "Guadeloupe (Caribbean DOM ISLANDED EDF SEI)",
    },
    {
        "id": "martinique",
        "bbox": (14.38, -61.25, 14.88, -60.80),
        "description": "Martinique (Caribbean DOM ISLANDED EDF SEI)",
    },
    {
        "id": "guyane",
        "bbox": (2.10, -54.60, 5.80, -51.60),
        "description": "Guyane française (South America DOM ISLANDED EDF SEI)",
    },
    {
        "id": "reunion_mayotte",
        "bbox": (-21.40, 45.00, -12.60, 55.85),
        "description": "Réunion + Mayotte (Indian Ocean DOM ISLANDED EDF SEI + EDM)",
    },
    {
        "id": "saint_pierre_miquelon",
        "bbox": (46.75, -56.45, 47.15, -56.10),
        "description": "Saint-Pierre-et-Miquelon (North Atlantic DOM ISLANDED EDF SEI)",
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
    (French rural MV distribution SIGNIFICANT in Auvergne + Limousin +
    Bourgogne + Champagne-Ardenne + Bretagne + Lorraine + Corsica
    interior + all DOM territories).
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
# Fetchers — 11-zone architecture for both subs + lines
# ─────────────────────────────────────────────────────────────


def _fetch_zoned(cache_dir: Path, kind: str, query_builder) -> dict:
    """Generic 11-zone fetch."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"overpass-{kind}-raw.json"
    if cache_path.exists():
        print(f"[{kind}] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[{kind}] bbox-split fetching {len(FRANCE_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in FRANCE_ZONES:
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
        "generator": f"SSI Index Foundation France P37 Wave 4 11-zone {kind}",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[{kind}] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(FRANCE_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[{kind}] ✓ assembled {len(all_elements):,} total {kind} elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[{kind}] cached → {cache_path}")
    return assembled


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch France subs across 11 zones."""
    return _fetch_zoned(cache_dir, "subs", _build_subs_query)


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch France lines across 11 zones."""
    return _fetch_zoned(cache_dir, "lines", _build_lines_query)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    cache_dir = Path("france/_cache")
    print("═" * 70)
    print("France P37 Wave 4 — OSM Overpass fetch")
    print("🇫🇷 11-zone (5 mainland + Corsica + 5 DOM globally distributed)")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ France P37 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
