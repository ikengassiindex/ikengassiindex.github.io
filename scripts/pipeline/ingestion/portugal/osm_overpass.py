"""Portugal P33 Wave 4 — OSM Overpass API fetcher.

Sweden P32 Option B pattern INHERITED (canonical Wave 4 template):
  - `out center` on WAY subs (100% coord capture)
  - `out geom` on LINES (proper polyline geometry)
  - power=minor_line INCLUDED for wooden-pole rural MV
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Portugal-specific architecture:
  - Continental single-bbox (92k km², 5× smaller than Sweden)
  - Açores archipelago separate fetch (9 islands ~1,400 km west)
  - Madeira archipelago separate fetch (~1,000 km southwest)
  - Line query bbox-split fallback if continental single-bbox fails

Emits per-country cache files:
  portugal/_cache/overpass-subs-raw.json (aggregated all 3 zones)
  portugal/_cache/overpass-lines-raw.json (aggregated all zones)

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
# Portugal 3-zone bbox architecture (continental + islands)
# ─────────────────────────────────────────────────────────────

PORTUGAL_ZONES = [
    {
        "id": "continental",
        "bbox": (36.96, -9.51, 42.15, -6.19),
        "description": "Continental Portugal (Algarve → Minho, Atlantic → Spanish border)",
    },
    {
        "id": "azores",
        "bbox": (36.9, -31.3, 39.7, -25.0),
        "description": "Açores archipelago (9 populated islands, EDA islanded grid)",
    },
    {
        "id": "madeira",
        "bbox": (32.4, -17.3, 33.1, -16.3),
        "description": "Madeira archipelago (Madeira + Porto Santo + Selvagens, EEM islanded)",
    },
]


# ─────────────────────────────────────────────────────────────
# 6-zone bbox-split fallback for LINE query (continental only)
# ─────────────────────────────────────────────────────────────
# Continental Portugal 92k km² likely fits single bbox with `out geom`
# but bbox-split fallback ready if endpoint payload limits hit.
# Split aligned with NUTS 2 regions.

PORTUGAL_LINE_BBOX_ZONES = [
    {
        "id": "norte",
        "bbox": (40.60, -9.10, 42.15, -6.19),  # Minho + Douro + Trás-os-Montes
        "description": "Norte (Porto + Braga + Vila Real + Bragança + Douro Vinhateiro)",
    },
    {
        "id": "centro",
        "bbox": (39.30, -9.51, 40.60, -6.19),  # Centro NUTS 2
        "description": "Centro (Coimbra + Aveiro + Viseu + Guarda + Beira Interior)",
    },
    {
        "id": "lisboa_vale_tejo",
        "bbox": (38.60, -9.51, 39.30, -8.00),  # Lisboa + Vale do Tejo
        "description": "Lisboa + Vale do Tejo (Lisboa + Setúbal + Santarém)",
    },
    {
        "id": "alentejo",
        "bbox": (37.60, -9.00, 39.30, -6.19),  # Alentejo NUTS 2
        "description": "Alentejo (Évora + Beja + Portalegre + wooden-pole rural MV dense)",
    },
    {
        "id": "algarve",
        "bbox": (36.96, -9.10, 37.60, -7.30),  # Algarve NUTS 2
        "description": "Algarve (Faro + Portimão + Ria Formosa lagoons)",
    },
    {
        "id": "azores_lines",
        "bbox": (36.9, -31.3, 39.7, -25.0),  # Açores archipelago
        "description": "Açores 9 islands (EDA islanded grid)",
    },
    {
        "id": "madeira_lines",
        "bbox": (32.4, -17.3, 33.1, -16.3),  # Madeira archipelago
        "description": "Madeira + Porto Santo (EEM islanded grid)",
    },
]


# ─────────────────────────────────────────────────────────────
# Overpass QL query templates
# ─────────────────────────────────────────────────────────────


def _build_subs_query(bbox: tuple[float, float, float, float]) -> str:
    """Substation query — Wave 4 with `out center` (100% coord capture)."""
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
    """Line query — Sweden P32 Option B extended (INHERITED).

    Includes power=minor_line for wooden-pole rural MV distribution.
    Portugal Iberian rural network (Alentejo + Trás-os-Montes + Beira
    Interior) has significant wooden-pole 10-30 kV MV footprint.
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
# Fetchers — 3-zone architecture for subs + line bbox-split
# ─────────────────────────────────────────────────────────────


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch Portugal subs across 3 zones (continental + Açores + Madeira).

    Assembles per-zone raw JSON into single overpass-subs-raw.json.
    Convention #56: if any zone fails, `_partial_fetch: true` flag.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "overpass-subs-raw.json"
    if cache_path.exists():
        print(f"[subs] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[subs] fetching Portugal 3-zone architecture (continental + Açores + Madeira)")
    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in PORTUGAL_ZONES:
        zone_cache_path = cache_dir / f"overpass-subs-{zone['id']}.json"
        if zone_cache_path.exists():
            print(f"[subs/{zone['id']}] cache hit → {zone_cache_path}")
            zone_result = json.loads(zone_cache_path.read_text())
        else:
            print(f"[subs/{zone['id']}] {zone['description']}")
            print(f"[subs/{zone['id']}] bbox {zone['bbox']}")
            query = _build_subs_query(zone["bbox"])
            zone_result = _post_overpass(query, f"subs/{zone['id']}")
            if zone_result is None:
                failed_zones.append(zone["id"])
                partial_fetch = True
                print(f"[subs/{zone['id']}] ✗ zone failed — Convention #56 partial-fetch")
                continue
            zone_cache_path.write_text(json.dumps(zone_result))
            print(f"[subs/{zone['id']}] cached → {zone_cache_path}")

        n_zone_elements = len(zone_result.get("elements", []))
        print(f"[subs/{zone['id']}] +{n_zone_elements:,} elements")
        all_elements.extend(zone_result.get("elements", []))

        # Polite pause between zones
        time.sleep(5)

    assembled = {
        "version": 0.6,
        "generator": "SSI Index Foundation Portugal P33 Wave 4 3-zone",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[subs] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(PORTUGAL_ZONES)} zones failed: {failed_zones}"
        )

    print(f"[subs] ✓ assembled {len(all_elements):,} total sub elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[subs] cached → {cache_path}")
    return assembled


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch lines via 7-zone bbox-split (5 NUTS 2 + Açores + Madeira).

    Convention #56: if any zone fails, `_partial_fetch: true` flag.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "overpass-lines-raw.json"
    if cache_path.exists():
        print(f"[lines] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[lines] bbox-split fetching {len(PORTUGAL_LINE_BBOX_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in PORTUGAL_LINE_BBOX_ZONES:
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

    assembled = {
        "version": 0.6,
        "generator": "SSI Index Foundation Portugal P33 Wave 4 7-zone bbox-split",
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[lines] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(PORTUGAL_LINE_BBOX_ZONES)} zones failed: "
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
    cache_dir = Path("portugal/_cache")
    print("═" * 70)
    print("Portugal P33 Wave 4 — OSM Overpass fetch")
    print("🇵🇹 Iberian synchronous grid + Açores + Madeira archipelagos")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ Portugal P33 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
