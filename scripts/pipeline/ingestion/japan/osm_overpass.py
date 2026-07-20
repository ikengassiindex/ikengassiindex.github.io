"""Japan P35 Wave 4 — OSM Overpass API fetcher.

Portugal P33 bi-directional Option B pattern INHERITED with
Japan-specific voltage defaults (6.6 kV MV standard UNIQUE cohort-wide).

Japan-specific architecture:
  - 9-zone bbox-split aligned with 9 regional utility territories
    (Hokkaido + Tohoku + TEPCO Kanto + Chubu + Hokuriku + Kansai +
    Chugoku + Shikoku + Kyushu+Okinawa)
  - Japan mainland Honshu 227k km² + Hokkaido 78k km² + Kyushu 37k km²
    + Shikoku 18k km² + Okinawa + ~430 inhabited islands
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Emits per-country cache files:
  japan/_cache/overpass-subs-raw.json (aggregated 9 zones)
  japan/_cache/overpass-lines-raw.json (aggregated 9 zones)

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
# Japan 9-zone bbox architecture aligned with regional utilities
# ─────────────────────────────────────────────────────────────

JAPAN_ZONES = [
    {
        "id": "hokkaido",
        "bbox": (41.35, 139.75, 45.53, 145.82),
        "description": "Hokkaido island (HEPCO Network 50 Hz + Sapporo + Asahikawa + Hakodate + Rebun+Rishiri)",
    },
    {
        "id": "tohoku",
        "bbox": (36.75, 138.50, 41.60, 142.10),
        "description": "Tohoku region (Tohoku Network 50 Hz + Aomori + Iwate + Akita + Miyagi + Yamagata + Fukushima + Niigata)",
    },
    {
        "id": "kanto_tepco",
        "bbox": (34.90, 138.70, 37.10, 141.10),
        "description": "Kanto region (TEPCO Power Grid 50 Hz + Tokyo + Yokohama + Saitama + Chiba + Ibaraki + Tochigi + Gunma + Shizuoka east)",
    },
    {
        "id": "chubu",
        "bbox": (33.30, 135.90, 37.10, 138.90),
        "description": "Chubu region (Chubu Power Grid 60 Hz + Nagoya + Aichi + Gifu + Mie + Nagano + Shizuoka west)",
    },
    {
        "id": "hokuriku",
        "bbox": (35.90, 135.60, 37.60, 137.90),
        "description": "Hokuriku region (Hokuriku T&D 60 Hz + Toyama + Ishikawa + Fukui)",
    },
    {
        "id": "kansai",
        "bbox": (33.40, 134.20, 35.90, 136.60),
        "description": "Kansai region (Kansai T&D 60 Hz + Osaka + Kyoto + Hyogo + Nara + Wakayama + Shiga)",
    },
    {
        "id": "chugoku",
        "bbox": (33.75, 130.85, 35.85, 134.55),
        "description": "Chugoku region (Chugoku Network 60 Hz + Hiroshima + Okayama + Yamaguchi + Tottori + Shimane)",
    },
    {
        "id": "shikoku",
        "bbox": (32.70, 132.00, 34.55, 134.75),
        "description": "Shikoku island (Shikoku T&D 60 Hz + Kagawa + Ehime + Kochi + Tokushima)",
    },
    {
        "id": "kyushu_okinawa",
        "bbox": (24.05, 122.93, 33.90, 132.05),
        "description": "Kyushu island + Okinawa Prefecture (Kyushu T&D 60 Hz + Okinawa EPCO ISLANDED + Sakishima + Miyako + Ishigaki + Yonaguni + Amami)",
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
    (Japanese rural distribution 6.6 kV standard SIGNIFICANT in
    Tohoku + Hokkaido + Shikoku interior + Kyushu southern + Okinawa
    remote islands).
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
# Fetchers — 9-zone architecture for both subs + lines
# ─────────────────────────────────────────────────────────────


def _fetch_zoned(cache_dir: Path, kind: str, query_builder) -> dict:
    """Generic 9-zone fetch (works for both subs + lines).

    kind = "subs" or "lines"
    query_builder = _build_subs_query or _build_lines_query
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"overpass-{kind}-raw.json"
    if cache_path.exists():
        print(f"[{kind}] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[{kind}] bbox-split fetching {len(JAPAN_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in JAPAN_ZONES:
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

        # Polite pause between zones
        time.sleep(5)

    assembled = {
        "version": 0.6,
        "generator": (
            f"SSI Index Foundation Japan P35 Wave 4 9-zone {kind}"
        ),
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[{kind}] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(JAPAN_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[{kind}] ✓ assembled {len(all_elements):,} total {kind} elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[{kind}] cached → {cache_path}")
    return assembled


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch Japan subs across 9 zones."""
    return _fetch_zoned(cache_dir, "subs", _build_subs_query)


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch Japan lines across 9 zones."""
    return _fetch_zoned(cache_dir, "lines", _build_lines_query)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    cache_dir = Path("japan/_cache")
    print("═" * 70)
    print("Japan P35 Wave 4 — OSM Overpass fetch")
    print("🇯🇵 9-regional-utility architecture + 50/60 Hz frequency split")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ Japan P35 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
