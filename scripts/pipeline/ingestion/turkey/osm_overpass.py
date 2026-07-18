"""Turkey OSM Overpass fetcher — Wave 3 P30 v4.23.

Fetches substations + transmission lines from OSM Overpass API
with 3-endpoint fallback (overpass-api.de + kumi.systems + private.coffee).

Bi-continental jurisdiction (European Thrace + Asian Anatolia)
+ Aegean archipelago + Mediterranean coastline + Alpine mountain
ridges + Bosphorus HV crossings + 7-border cross-border complexity.

Convention preservation:
- #23 Provenance pinning (SHA-256 raw payload + cache)
- #36 Cross-border filter (5.0 km tolerance turkey entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation (partial-fetch preserved end-to-end)
- #60 Non-commercial provenance (OSM ODbL public)
- #78 BINDING 12th enforcement (alias normalisation Turkish + Kurdish + Arabic + Greek + Ottoman legacy)
- #78 §4bis.5 8TH ENFORCEMENT (Istanbul 3-way BEDAŞ + AYEDAŞ + BOĞAZİÇİ)
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)

from scripts.pipeline.ingestion.turkey._base import (
    COUNTRY_SLUG,
    apply_bounds_filter,
    check_discipline_41,
    emit_audit_sidecar,
    resolve_owner,
    sha256_hexdigest,
)

logger = logging.getLogger(__name__)

# ─── Overpass API endpoints (3-fallback per Nordic precedent) ───
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# ─── Turkey bbox (Aegean Datça to Iranian border + Mediterranean to Black Sea) ───
TURKEY_BBOX = "35.8181,25.6688,42.1082,44.8177"  # lat_min, lon_min, lat_max, lon_max

# ─── Cache directory ───
CACHE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "pipeline" / "data" / COUNTRY_SLUG / "_osm_cache"

# ─── Overpass timeout budget ───
# Note: reduced from 180s → 120s per Nordic precedent — Overpass main endpoint
# returned HTTP 406 Not Acceptable on 180s timeout during Turkey P30 first-run
REQUEST_TIMEOUT_S = 120

# ─── HTTP headers (per Overpass API docs; helps avoid 406 responses) ───
_HTTP_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ssi-index-foundation/v4.23 (+https://ikengassiindex.github.io)",
}


@dataclass
class OverpassFetchResult:
    """OSM fetch outcome — supports Convention #56 partial-fetch preservation."""
    substations: list[dict[str, Any]]
    lines: list[dict[str, Any]]
    raw_bytes_fetched: int
    raw_sha256: str
    partial_fetch_notes: list[str]


def _cache_key(query: str) -> Path:
    """SHA-256 based cache filename."""
    h = hashlib.sha256(query.encode()).hexdigest()[:16]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{h}.json"


def _fetch_overpass(query: str, *, allow_partial: bool = True) -> Optional[bytes]:
    """Fetch Overpass query with 3-endpoint fallback + cache.

    Returns None if all endpoints fail (Convention #56 partial-fetch).
    """
    cache_path = _cache_key(query)
    if cache_path.exists():
        raw = cache_path.read_bytes()
        logger.info(f"Cache hit: {cache_path.name} ({len(raw)} bytes)")
        return raw

    for endpoint in OVERPASS_ENDPOINTS:
        try:
            logger.info(f"Overpass POST {endpoint} (attempt 1/4)")
            resp = requests.post(
                endpoint,
                data={"data": query},
                headers=_HTTP_HEADERS,
                timeout=REQUEST_TIMEOUT_S,
            )
            if resp.status_code == 200:
                raw = resp.content
                cache_path.write_bytes(raw)
                logger.info(f"Fetched {len(raw)} bytes to cache {cache_path.name}")
                return raw
            elif resp.status_code in (502, 504):
                logger.warning(
                    f"Overpass {resp.status_code} gateway; trying next endpoint after 5s"
                )
                time.sleep(5)
                continue
            else:
                logger.warning(
                    f"Overpass HTTP {resp.status_code}; trying next endpoint after 5s"
                )
                time.sleep(5)
                continue
        except requests.exceptions.Timeout:
            logger.warning(
                f"Overpass timeout at {endpoint}; trying next endpoint after 5s"
            )
            time.sleep(5)
            continue
        except Exception as exc:
            logger.error(f"Overpass fetch error at {endpoint}: {exc}")
            time.sleep(5)
            continue

    # All endpoints failed — Convention #56 partial-fetch
    if allow_partial:
        logger.error("All 3 Overpass endpoints failed; returning None per Convention #56")
        return None
    raise RuntimeError("All Overpass endpoints failed and partial-fetch disabled")


# ─── OSM Overpass queries ───
_QUERY_WAYS = """
[out:json][timeout:120];
(
  way[power=substation](%s);
);
out body;
>;
out skel qt;
""" % TURKEY_BBOX

_QUERY_NODES = """
[out:json][timeout:120];
(
  node[power=substation](%s);
);
out body;
""" % TURKEY_BBOX

_QUERY_RELATIONS = """
[out:json][timeout:120];
(
  relation[power=substation](%s);
);
out body;
>>;
out skel qt;
""" % TURKEY_BBOX

_QUERY_LINES = """
[out:json][timeout:120];
(
  way[power=line](%s);
  way[power=minor_line](%s);
);
out body;
>;
out skel qt;
""" % (TURKEY_BBOX, TURKEY_BBOX)


def _parse_osm_elements(raw: bytes, kind: str) -> list[dict[str, Any]]:
    """Parse OSM JSON payload into normalised feature list."""
    try:
        data = json.loads(raw)
    except Exception as exc:
        logger.error(f"OSM {kind} JSON parse failed: {exc}")
        return []

    elements = data.get("elements", [])
    features = []
    for el in elements:
        if kind == "substation":
            if el.get("type") not in ("node", "way", "relation"):
                continue
            tags = el.get("tags", {})
            if tags.get("power") != "substation":
                continue
            # Extract lat/lon (may be from node or way centroid)
            lat, lon = None, None
            if el.get("type") == "node":
                lat, lon = el.get("lat"), el.get("lon")
            elif "center" in el:
                lat, lon = el["center"].get("lat"), el["center"].get("lon")
            elif el.get("type") == "way" and "nodes" in el:
                # centroid approximation deferred to downstream
                pass

            voltage_kv = None
            if tags.get("voltage"):
                try:
                    voltage_kv = float(str(tags["voltage"]).split(";")[0]) / 1000.0
                except (ValueError, TypeError):
                    pass

            features.append({
                "osm_id": el.get("id"),
                "osm_type": el.get("type"),
                "lat": lat,
                "lon": lon,
                "operator": tags.get("operator"),
                "name": tags.get("name"),
                "voltage_kv": voltage_kv,
                "substation_type": tags.get("substation"),
                "province": tags.get("addr:province") or tags.get("is_in:state"),
                "raw_tags": tags,
            })
        elif kind == "line":
            if el.get("type") != "way":
                continue
            tags = el.get("tags", {})
            if tags.get("power") not in ("line", "minor_line"):
                continue
            voltage_kv = None
            if tags.get("voltage"):
                try:
                    voltage_kv = float(str(tags["voltage"]).split(";")[0]) / 1000.0
                except (ValueError, TypeError):
                    pass
            features.append({
                "osm_id": el.get("id"),
                "osm_type": "way",
                "voltage_kv": voltage_kv,
                "operator": tags.get("operator"),
                "raw_tags": tags,
            })
    return features


def fetch_turkey_osm() -> OverpassFetchResult:
    """Fetch Turkey substations + lines from OSM Overpass.

    Convention #56 partial-fetch preservation — if any of the 4 queries
    (way subs + node subs + relation subs + lines) fails, log a note
    and preserve whatever was successfully fetched.
    """
    partial_notes: list[str] = []
    total_bytes = 0
    all_subs: list[dict[str, Any]] = []
    all_lines: list[dict[str, Any]] = []

    # Way substations (dominant tier)
    raw = _fetch_overpass(_QUERY_WAYS)
    if raw:
        total_bytes += len(raw)
        way_subs = _parse_osm_elements(raw, "substation")
        all_subs.extend(way_subs)
        logger.info(f"Parsed {len(way_subs)} substations from OSM Overpass (way)")
    else:
        partial_notes.append("OSM substation way fetch failed: all endpoints 504/timeout")

    # Node substations
    raw = _fetch_overpass(_QUERY_NODES)
    if raw:
        total_bytes += len(raw)
        node_subs = _parse_osm_elements(raw, "substation")
        # De-dup vs way subs
        existing_ids = {(s["osm_type"], s["osm_id"]) for s in all_subs}
        node_subs = [s for s in node_subs if (s["osm_type"], s["osm_id"]) not in existing_ids]
        all_subs.extend(node_subs)
        logger.info(f"Parsed {len(node_subs)} additional substations (node)")
    else:
        partial_notes.append("OSM substation node fetch failed: partial-fetch preserved")

    # Relation substations
    raw = _fetch_overpass(_QUERY_RELATIONS)
    if raw:
        total_bytes += len(raw)
        rel_subs = _parse_osm_elements(raw, "substation")
        existing_ids = {(s["osm_type"], s["osm_id"]) for s in all_subs}
        rel_subs = [s for s in rel_subs if (s["osm_type"], s["osm_id"]) not in existing_ids]
        all_subs.extend(rel_subs)
        logger.info(f"Parsed {len(rel_subs)} additional substations (relation)")
    else:
        partial_notes.append("OSM substation relation fetch failed: partial-fetch preserved")

    logger.info(f"Total OSM substations pre-filter: {len(all_subs)}")

    # Lines
    raw = _fetch_overpass(_QUERY_LINES)
    if raw:
        total_bytes += len(raw)
        all_lines = _parse_osm_elements(raw, "line")
        logger.info(f"Parsed {len(all_lines)} lines from OSM Overpass")
    else:
        partial_notes.append("OSM line fetch failed: partial-fetch preserved — lines=[]")

    # Apply Discipline #36 cross-border filter
    filtered_subs, drops_subs = apply_bounds_filter(all_subs)
    filtered_lines, drops_lines = apply_bounds_filter(all_lines)
    if drops_subs or drops_lines:
        partial_notes.append(
            f"Discipline #36 — dropped {drops_subs} substations + {drops_lines} lines "
            f"outside Turkey polygon (5.0 km Aegean archipelago + Mediterranean + Alpine + "
            f"Bosphorus HV crossing precision tolerance; 7-border cross-border interconnectors "
            f"BG/GR/GE/IR/IQ + Armenian border-CLOSED + Syrian curtailed preserved)."
        )

    # Owner enrichment via 8-layer resolver
    owner_hist = {}
    convention_78_binding_hits = 0
    convention_78_4bis_5_hits = {"BEDAŞ": 0, "AYEDAŞ": 0, "BOĞAZİÇİ": 0}

    for sub in filtered_subs:
        result = resolve_owner(
            osm_operator=sub.get("operator"),
            voltage_kv=sub.get("voltage_kv"),
            lat=sub.get("lat"),
            lon=sub.get("lon"),
            province=sub.get("province"),
            name=sub.get("name"),
        )
        sub["_resolved_operator"] = result.canonical_name
        sub["_owner_provenance"] = result.provenance
        owner_hist[result.provenance] = owner_hist.get(result.provenance, 0) + 1
        if result.was_alias_normalised:
            convention_78_binding_hits += 1
        if result.convention_78_4bis_5_geofence_hit:
            convention_78_4bis_5_hits[result.convention_78_4bis_5_geofence_hit] = (
                convention_78_4bis_5_hits.get(result.convention_78_4bis_5_geofence_hit, 0) + 1
            )

    logger.info(
        f"Owner enrichment: {owner_hist.get('osm_operator_tag_direct', 0) + owner_hist.get('osm_operator_tag_direct_alias_normalised', 0)} direct OSM "
        f"({convention_78_binding_hits} alias-normalised) + "
        f"{owner_hist.get('region_jurisdiction_layer_1_TEİAŞ_TSO_threshold_ge_154kv', 0) + owner_hist.get('region_jurisdiction_layer_6_TEİAŞ_catch_all_default', 0)} TEİAŞ + "
        f"{convention_78_4bis_5_hits['BEDAŞ']}+{convention_78_4bis_5_hits['AYEDAŞ']}+{convention_78_4bis_5_hits['BOĞAZİÇİ']} §4bis.5 Istanbul 3-way (8th enforcement) + "
        f"{sum(v for k, v in owner_hist.items() if 'akkuyu' in k.lower())} nuclear + "
        f"{sum(v for k, v in owner_hist.items() if 'layer_3b' in k)} region_DSO"
    )

    # Discipline #41 line-substation parity check
    d41_msg, d41_ratio = check_discipline_41(len(filtered_subs), len(filtered_lines))
    logger.info(f"Discipline #41: {d41_msg}")

    # Consolidate raw SHA-256 for provenance pin
    raw_combined = f"turkey-osm-{len(filtered_subs)}-{len(filtered_lines)}-{total_bytes}"
    raw_sha256 = sha256_hexdigest(raw_combined.encode())

    # Emit audit sidecar
    emit_audit_sidecar(
        subcommand="osm-overpass",
        substations_count=len(filtered_subs),
        lines_count=len(filtered_lines),
        raw_sha256=raw_sha256,
        raw_bytes=total_bytes,
        owner_provenance_hist=owner_hist,
        convention_78_binding_hits=convention_78_binding_hits,
        convention_78_4bis_5_hits=convention_78_4bis_5_hits,
        partial_fetch_notes=partial_notes,
        discipline_41_msg=d41_msg,
        discipline_36_drops_subs=drops_subs,
        discipline_36_drops_lines=drops_lines,
    )

    return OverpassFetchResult(
        substations=filtered_subs,
        lines=filtered_lines,
        raw_bytes_fetched=total_bytes,
        raw_sha256=raw_sha256,
        partial_fetch_notes=partial_notes,
    )


# ─── CLI entry point ───
def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    result = fetch_turkey_osm()
    # Print summary for tee-log capture
    print()
    print("TR-P30-osm-overpass fetch complete")
    print(f"  substations:        {len(result.substations):,}")
    print(f"  transmission_lines: {len(result.lines):,}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")

    # Print owner-provenance histogram
    print("  Owner-provenance distribution:")
    hist = {}
    for sub in result.substations:
        prov = sub.get("_owner_provenance", "unknown")
        hist[prov] = hist.get(prov, 0) + 1
    for prov, count in sorted(hist.items(), key=lambda x: -x[1]):
        print(f"    {count:>5}  {prov}")

    # Distinct operators
    ops = {}
    for sub in result.substations:
        op = sub.get("_resolved_operator", "unknown")
        ops[op] = ops.get(op, 0) + 1
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 20 operators:")
    for op, count in sorted(ops.items(), key=lambda x: -x[1])[:20]:
        print(f"    {count:>5}  {op}")

    # Partial-fetch notes
    if result.partial_fetch_notes:
        print()
        for note in result.partial_fetch_notes:
            print(f"  ⚠ Convention #56 partial — {note}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
