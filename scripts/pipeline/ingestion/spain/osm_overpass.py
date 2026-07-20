"""Spain P36 Wave 4 — OSM Overpass API fetcher.

Portugal P33 bi-directional Option B pattern INHERITED (canonical
Wave 4 template + Iberian sibling voltage defaults).

Spain-specific architecture:
  - 6-zone bbox-split: Peninsula North + Peninsula Center + Peninsula
    South + Balearic Islands + Canary Islands + Ceuta+Melilla exclaves
  - Spain mainland 493k km² area (larger than Italy 301k km²)
  - Canary Islands ~1,700 km offshore Africa-adjacent (remote zone)
  - Ceuta + Melilla North African exclaves (small precision zones)
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Emits per-country cache files:
  spain/_cache/overpass-subs-raw.json (aggregated 6 zones)
  spain/_cache/overpass-lines-raw.json (aggregated 6 zones)

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
# Spain 6-zone bbox architecture
# ─────────────────────────────────────────────────────────────

SPAIN_ZONES = [
    {
        "id": "peninsula_north",
        "bbox": (41.20, -9.30, 43.79, 3.35),
        "description": "Peninsula North (Galicia + Asturias + Cantabria + Basque + Navarra + Aragón + Cataluña + Castilla y León north)",
    },
    {
        "id": "peninsula_center",
        "bbox": (39.00, -7.60, 41.20, 3.20),
        "description": "Peninsula Center (Madrid + Castilla y León south + Castilla-La Mancha + Extremadura + Cataluña south + Valencia north + Aragón south)",
    },
    {
        "id": "peninsula_south",
        "bbox": (35.99, -7.60, 39.00, 0.90),
        "description": "Peninsula South (Andalucía + Murcia + Valencia south + Extremadura south)",
    },
    {
        "id": "balearic",
        "bbox": (38.65, 1.15, 40.10, 4.35),
        "description": "Balearic Islands (Mallorca + Menorca + Ibiza + Formentera; Cometa 400 MW HVDC to Peninsula)",
    },
    {
        "id": "canary",
        "bbox": (27.63, -18.16, 29.42, -13.42),
        "description": "Canary Islands (7 main: Tenerife + Gran Canaria + Lanzarote + Fuerteventura + La Palma + El Hierro + La Gomera; ~1,700 km SW mainland, 6 sub-systems ISLANDED)",
    },
    {
        "id": "ceuta_melilla",
        "bbox": (35.20, -5.40, 35.95, -2.85),
        "description": "Ceuta + Melilla (Spanish North African exclaves; Chafarinas + Alborán + Peñón de Vélez + Peñón de Alhucemas minor islands)",
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
    (Spanish rural MV distribution SIGNIFICANT in Extremadura + Castilla-
    La Mancha + Andalucía interior + Aragón + Castilla y León).
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
# Fetchers — 6-zone architecture for both subs + lines
# ─────────────────────────────────────────────────────────────


def _fetch_zoned(cache_dir: Path, kind: str, query_builder) -> dict:
    """Generic 6-zone fetch."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"overpass-{kind}-raw.json"
    if cache_path.exists():
        print(f"[{kind}] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[{kind}] bbox-split fetching {len(SPAIN_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in SPAIN_ZONES:
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
        "generator": f"SSI Index Foundation Spain P36 Wave 4 6-zone {kind}",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[{kind}] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(SPAIN_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[{kind}] ✓ assembled {len(all_elements):,} total {kind} elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[{kind}] cached → {cache_path}")
    return assembled


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch Spain subs across 6 zones."""
    return _fetch_zoned(cache_dir, "subs", _build_subs_query)


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch Spain lines across 6 zones."""
    return _fetch_zoned(cache_dir, "lines", _build_lines_query)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    cache_dir = Path("spain/_cache")
    print("═" * 70)
    print("Spain P36 Wave 4 — OSM Overpass fetch")
    print("🇪🇸 Iberian sibling to Portugal + 6-zone (Peninsula + Balearic + Canary + Ceuta+Melilla)")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ Spain P36 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
