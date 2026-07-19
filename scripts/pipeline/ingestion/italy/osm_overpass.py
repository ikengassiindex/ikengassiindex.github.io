"""Italy P34 Wave 4 — OSM Overpass API fetcher.

Portugal P33 bi-directional Option B pattern INHERITED (canonical
Wave 4 template post-Portugal):
  - `out center` on WAY subs
  - `out geom` on LINES
  - power=minor_line INCLUDED (Sweden P32 lines-side)

Italy-specific architecture:
  - 7-zone bbox-split aligned with post-2021 Terna bidding zones:
    NORD + CNOR + CSUD + SUD + CALA + SICI + SARD
  - Mainland Italy 301k km² comparable to UK, larger than Sweden per
    density (needs bbox-split for sub AND line queries)
  - 3-endpoint fallback (overpass-api.de → kumi.systems → private.coffee)
  - HTTP headers Accept: application/json + User-Agent
  - 120s timeout

Emits per-country cache files:
  italy/_cache/overpass-subs-raw.json (aggregated 7 zones)
  italy/_cache/overpass-lines-raw.json (aggregated 7 zones)

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
# Italy 7-zone bbox architecture aligned with Terna post-2021 zones
# ─────────────────────────────────────────────────────────────

ITALY_ZONES = [
    {
        "id": "nord",
        "bbox": (43.30, 6.63, 47.09, 13.90),
        "description": "NORD (Piemonte + Val d'Aosta + Lombardia + Liguria + Emilia-Romagna + Veneto + Trentino-Alto Adige + Friuli-Venezia Giulia)",
    },
    {
        "id": "cnor",
        "bbox": (42.20, 9.90, 44.50, 13.50),
        "description": "CNOR (Toscana + Umbria + Marche)",
    },
    {
        "id": "csud",
        "bbox": (40.80, 11.50, 42.90, 14.90),
        "description": "CSUD (Lazio + Abruzzo + Campania + Molise)",
    },
    {
        "id": "sud",
        "bbox": (39.50, 14.30, 42.20, 18.52),
        "description": "SUD (Puglia + Basilicata)",
    },
    {
        "id": "cala",
        "bbox": (37.80, 15.60, 40.20, 17.50),
        "description": "CALA (Calabria; split from SUD in 2021)",
    },
    {
        "id": "sici",
        "bbox": (35.49, 11.90, 38.35, 15.75),
        "description": "SICI (Sicilia + Aeolian + Egadi + Pelagie including Lampedusa)",
    },
    {
        "id": "sard",
        "bbox": (38.85, 8.10, 41.30, 9.90),
        "description": "SARD (Sardegna + minor Sardegna islands)",
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
    (Italian Mezzogiorno + Alpine valleys wooden-pole MV significant).
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
# Fetchers — 7-zone architecture for both subs + lines
# ─────────────────────────────────────────────────────────────


def _fetch_zoned(cache_dir: Path, kind: str, query_builder) -> dict:
    """Generic 7-zone fetch (works for both subs + lines).

    kind = "subs" or "lines"
    query_builder = _build_subs_query or _build_lines_query
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"overpass-{kind}-raw.json"
    if cache_path.exists():
        print(f"[{kind}] cache hit → {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"[{kind}] bbox-split fetching {len(ITALY_ZONES)} zones")

    all_elements: list = []
    failed_zones: list[str] = []
    partial_fetch = False

    for zone in ITALY_ZONES:
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
            f"SSI Index Foundation Italy P34 Wave 4 7-zone {kind}"
        ),
        "elements": all_elements,
    }
    if partial_fetch:
        assembled["_partial_fetch"] = True
        assembled["_partial_fetch_failed_zones"] = failed_zones
        print(
            f"[{kind}] ⚠ Convention #56 partial-fetch — "
            f"{len(failed_zones)}/{len(ITALY_ZONES)} zones failed: "
            f"{failed_zones}"
        )

    print(f"[{kind}] ✓ assembled {len(all_elements):,} total {kind} elements")
    cache_path.write_text(json.dumps(assembled))
    print(f"[{kind}] cached → {cache_path}")
    return assembled


def fetch_substations(cache_dir: Path) -> dict:
    """Fetch Italy subs across 7 zones."""
    return _fetch_zoned(cache_dir, "subs", _build_subs_query)


def fetch_lines(cache_dir: Path) -> dict:
    """Fetch Italy lines across 7 zones."""
    return _fetch_zoned(cache_dir, "lines", _build_lines_query)


# ─────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────


def main() -> None:
    cache_dir = Path("italy/_cache")
    print("═" * 70)
    print("Italy P34 Wave 4 — OSM Overpass fetch")
    print("🇮🇹 Post-2021 Terna 7-zone bidding architecture")
    print(f"cache_dir: {cache_dir}")
    print("═" * 70)

    subs = fetch_substations(cache_dir)
    print()
    lines = fetch_lines(cache_dir)

    print()
    print("═" * 70)
    print(
        f"✓ Italy P34 fetch complete: "
        f"{len(subs.get('elements', [])):,} sub elements + "
        f"{len(lines.get('elements', [])):,} line elements"
    )
    print("═" * 70)


if __name__ == "__main__":
    main()
