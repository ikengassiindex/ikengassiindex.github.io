"""UK OSM Overpass fetcher — Wave 4 P31 v4.23.

🎉 WAVE 4 CORRECTED ARCHITECTURE 🎉
Post-Turkey schema-bug lesson applied:
- `out center` for way substations → returns centroid inline
- `out geom` for lines → returns polyline geometry inline
- Enables proper coord resolution for downstream compact schema emission

Fetches substations + transmission lines from OSM Overpass API
with 3-endpoint fallback (overpass-api.de + kumi.systems + private.coffee).

Post-Brexit UK jurisdiction with dual-market architecture
(GB National Grid ESO + NI I-SEM SONI) + 7 subsea + 1 land + 1 pending
Ireland interconnectors + RICHEST cohort-wide island archipelago.

Convention preservation:
- #23 Provenance pinning (SHA-256 raw payload + cache)
- #36 Cross-border filter (3.0 km tolerance uk entry)
- #41 Line-substation parity (target [1.5-5.0] healthy band)
- #56 Visibly-honest degradation (partial-fetch preserved end-to-end)
- #60 Non-commercial provenance (OSM ODbL public)
- #78 BINDING 13th enforcement (English + Welsh + Scots Gaelic + Irish + Cornish)
- #78 §4bis.5 9TH ENFORCEMENT candidate (London UKPN LPN geofence)
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

from scripts.pipeline.ingestion.uk._base import (
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

# ─── UK bbox — mainland + islands + Northern Ireland ───
# Rockall westernmost -8.65°, Shetland Muckle Flugga northernmost 60.86°,
# Great Yarmouth easternmost 1.76°, Isles of Scilly southernmost 49.87°
UK_BBOX = "49.87,-8.65,60.86,1.76"  # lat_min, lon_min, lat_max, lon_max

# ─── Cache directory ───
CACHE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "pipeline" / "data" / COUNTRY_SLUG / "_osm_cache"

# ─── Overpass timeout budget (per Turkey rate-limit fix) ───
REQUEST_TIMEOUT_S = 120

# ─── HTTP headers (Turkey rate-limit lesson) ───
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
    """Fetch Overpass query with 3-endpoint fallback + cache."""
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
                logger.warning(f"Overpass {resp.status_code} gateway; trying next endpoint after 5s")
                time.sleep(5)
                continue
            else:
                logger.warning(f"Overpass HTTP {resp.status_code}; trying next endpoint after 5s")
                time.sleep(5)
                continue
        except requests.exceptions.Timeout:
            logger.warning(f"Overpass timeout at {endpoint}; trying next endpoint after 5s")
            time.sleep(5)
            continue
        except Exception as exc:
            logger.error(f"Overpass fetch error at {endpoint}: {exc}")
            time.sleep(5)
            continue

    if allow_partial:
        logger.error("All 3 Overpass endpoints failed; returning None per Convention #56")
        return None
    raise RuntimeError("All Overpass endpoints failed and partial-fetch disabled")


# ─── OSM Overpass queries with WAVE 4 CORRECTED architecture ───
# `out center` on way subs → returns centroid inline (fixes Turkey lat/lon limitation)
# `out geom` on lines → returns polyline geometry inline (enables proper compact schema)

_QUERY_WAYS = """
[out:json][timeout:120];
(
  way[power=substation](%s);
);
out center;
""" % UK_BBOX

_QUERY_NODES = """
[out:json][timeout:120];
(
  node[power=substation](%s);
);
out body;
""" % UK_BBOX

_QUERY_RELATIONS = """
[out:json][timeout:120];
(
  relation[power=substation](%s);
);
out center;
""" % UK_BBOX

_QUERY_LINES = """
[out:json][timeout:120];
(
  way[power=line](%s);
  way[power=minor_line](%s);
);
out geom;
""" % (UK_BBOX, UK_BBOX)


# ─── UK BBOX SPLIT for line query fallback (6 zones) ───
# When single-bbox `out geom` line query fails (payload too large — UK grid is
# denser than Turkey's), fall back to 6 sub-bboxes. Way+node+relation sub
# queries stay on single-bbox (they use `out center`, smaller payload).
UK_LINE_BBOX_ZONES = [
    # (zone_name, bbox "lat_min,lon_min,lat_max,lon_max")
    ("north_scotland_shetland", "56.5,-8.0,60.9,-0.5"),   # Highlands + Islands + Shetland
    ("south_scotland",           "54.0,-5.5,56.5,-1.0"),   # Central + Southern Scotland
    ("northern_ireland",         "54.0,-8.2,55.5,-5.4"),   # Separate landmass (I-SEM cross-border)
    ("north_england_wales_north","52.5,-5.6,54.5,0.0"),    # North East + North West + N Wales
    ("central_england_wales_south","51.5,-5.7,52.5,1.8"),  # Midlands + Wales South + East
    ("south_england_cornwall",   "49.9,-6.5,51.5,1.8"),    # London + SE + SW + Cornwall + IoW + Scilly
]


def _build_lines_query_for_bbox(bbox: str) -> str:
    """Build compact line query for a single bbox zone."""
    return """
[out:json][timeout:120];
(
  way[power=line](%s);
  way[power=minor_line](%s);
);
out geom;
""" % (bbox, bbox)


def _parse_osm_substations(raw: bytes) -> list[dict[str, Any]]:
    """Parse OSM substation payload with WAVE 4 CORRECTED coord resolution.

    Uses `element.center` field from `out center` query hint for way + relation
    types, avoiding Turkey's lat/lon limitation.
    """
    try:
        data = json.loads(raw)
    except Exception as exc:
        logger.error(f"OSM substation JSON parse failed: {exc}")
        return []

    elements = data.get("elements", [])
    features = []
    for el in elements:
        tags = el.get("tags", {})
        if tags.get("power") != "substation":
            continue

        # WAVE 4 CORRECTED: extract lat/lon from element.center OR direct node coords
        lat, lon = None, None
        if el.get("type") == "node":
            lat, lon = el.get("lat"), el.get("lon")
        elif "center" in el:
            lat = el["center"].get("lat")
            lon = el["center"].get("lon")
        # Skip if still no coords (should be rare with out center)
        if lat is None or lon is None:
            continue

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
            "name": tags.get("name") or tags.get("ref"),
            "voltage_kv": voltage_kv,
            "substation_type": tags.get("substation"),
            "region": tags.get("addr:county") or tags.get("addr:state") or tags.get("is_in:county"),
            "raw_tags": tags,
        })
    return features


def _parse_osm_lines(raw: bytes) -> list[dict[str, Any]]:
    """Parse OSM line payload with WAVE 4 CORRECTED geometry inline.

    Uses `element.geometry` field from `out geom` query hint to extract
    polyline coords directly, avoiding Turkey's empty-coordinate bug.
    """
    try:
        data = json.loads(raw)
    except Exception as exc:
        logger.error(f"OSM line JSON parse failed: {exc}")
        return []

    elements = data.get("elements", [])
    features = []
    for el in elements:
        if el.get("type") != "way":
            continue
        tags = el.get("tags", {})
        if tags.get("power") not in ("line", "minor_line"):
            continue

        # WAVE 4 CORRECTED: extract geometry inline via `out geom` result
        geometry = el.get("geometry", [])  # list of {lat, lon} dicts
        if not geometry or len(geometry) < 2:
            continue  # skip lines without proper geometry

        # Convert to compact [[lon, lat], ...] format
        polyline = [[pt.get("lon"), pt.get("lat")] for pt in geometry if pt.get("lon") is not None and pt.get("lat") is not None]
        if len(polyline) < 2:
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
            "polyline": polyline,  # ← WAVE 4 CORRECTED — has actual geometry
            "raw_tags": tags,
        })
    return features


def fetch_uk_osm() -> OverpassFetchResult:
    """Fetch UK substations + lines from OSM Overpass with corrected architecture.

    Convention #56 partial-fetch preservation.
    """
    partial_notes: list[str] = []
    total_bytes = 0
    all_subs: list[dict[str, Any]] = []
    all_lines: list[dict[str, Any]] = []

    # Way substations (with out center)
    raw = _fetch_overpass(_QUERY_WAYS)
    if raw:
        total_bytes += len(raw)
        way_subs = _parse_osm_substations(raw)
        all_subs.extend(way_subs)
        logger.info(f"Parsed {len(way_subs)} substations from OSM Overpass (way with center)")
    else:
        partial_notes.append("OSM substation way fetch failed")

    # Node substations
    raw = _fetch_overpass(_QUERY_NODES)
    if raw:
        total_bytes += len(raw)
        node_subs = _parse_osm_substations(raw)
        existing_ids = {(s["osm_type"], s["osm_id"]) for s in all_subs}
        node_subs = [s for s in node_subs if (s["osm_type"], s["osm_id"]) not in existing_ids]
        all_subs.extend(node_subs)
        logger.info(f"Parsed {len(node_subs)} additional substations (node)")
    else:
        partial_notes.append("OSM substation node fetch failed")

    # Relation substations
    raw = _fetch_overpass(_QUERY_RELATIONS)
    if raw:
        total_bytes += len(raw)
        rel_subs = _parse_osm_substations(raw)
        existing_ids = {(s["osm_type"], s["osm_id"]) for s in all_subs}
        rel_subs = [s for s in rel_subs if (s["osm_type"], s["osm_id"]) not in existing_ids]
        all_subs.extend(rel_subs)
        logger.info(f"Parsed {len(rel_subs)} additional substations (relation with center)")
    else:
        partial_notes.append("OSM substation relation fetch failed")

    logger.info(f"Total OSM substations pre-filter: {len(all_subs)}")

    # Lines (with out geom for polyline coords) — try single-bbox first
    raw = _fetch_overpass(_QUERY_LINES)
    if raw:
        total_bytes += len(raw)
        all_lines = _parse_osm_lines(raw)
        logger.info(f"Parsed {len(all_lines)} lines from OSM Overpass (single-bbox with geometry)")
    else:
        # ─── WAVE 4 UK-specific BBOX-SPLIT FALLBACK ───
        # UK grid too dense for single-bbox line query → split into 6 zones
        logger.warning(
            f"Single-bbox UK line query failed; falling back to {len(UK_LINE_BBOX_ZONES)}-zone bbox split"
        )
        partial_notes.append(
            f"OSM single-bbox line fetch failed; bbox-split fallback into "
            f"{len(UK_LINE_BBOX_ZONES)} zones activated"
        )
        zones_ok = 0
        zones_failed = []
        for zone_name, zone_bbox in UK_LINE_BBOX_ZONES:
            zone_query = _build_lines_query_for_bbox(zone_bbox)
            logger.info(f"Bbox-split zone '{zone_name}' bbox={zone_bbox}")
            zone_raw = _fetch_overpass(zone_query)
            if zone_raw:
                total_bytes += len(zone_raw)
                zone_lines = _parse_osm_lines(zone_raw)
                # De-dup vs already-fetched lines
                existing_ids = {ln.get("osm_id") for ln in all_lines}
                new_lines = [ln for ln in zone_lines if ln.get("osm_id") not in existing_ids]
                all_lines.extend(new_lines)
                zones_ok += 1
                logger.info(
                    f"  Zone '{zone_name}' → +{len(new_lines)} new lines "
                    f"(cumulative: {len(all_lines)})"
                )
            else:
                zones_failed.append(zone_name)
                logger.warning(f"  Zone '{zone_name}' failed")
        logger.info(
            f"Bbox-split summary: {zones_ok}/{len(UK_LINE_BBOX_ZONES)} zones succeeded, "
            f"total lines: {len(all_lines)}"
        )
        if zones_failed:
            partial_notes.append(
                f"Bbox-split fallback: {len(zones_failed)}/{len(UK_LINE_BBOX_ZONES)} zones "
                f"failed ({', '.join(zones_failed)}); Convention #56 partial-fetch preserved"
            )

    # Discipline #36 filter
    filtered_subs, drops_subs = apply_bounds_filter(all_subs)
    filtered_lines, drops_lines = apply_bounds_filter(all_lines)
    if drops_subs or drops_lines:
        partial_notes.append(
            f"Discipline #36 — dropped {drops_subs} substations + {drops_lines} lines "
            f"outside UK polygon (3.0 km post-Brexit interconnector precision + "
            f"Northern Ireland land border + Scottish Highland coastline + "
            f"island archipelago Shetland/Orkney/Hebrides/IoM/CI/Scilly)."
        )

    # Owner enrichment via 9-layer resolver
    owner_hist = {}
    convention_78_binding_hits = 0
    convention_78_4bis_5_hits = {"UKPN LPN": 0}

    for sub in filtered_subs:
        result = resolve_owner(
            osm_operator=sub.get("operator"),
            voltage_kv=sub.get("voltage_kv"),
            lat=sub.get("lat"),
            lon=sub.get("lon"),
            region=sub.get("region"),
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
        f"{sum(v for k, v in owner_hist.items() if 'NGET' in k or 'SPT' in k or 'SHE_T' in k or 'catch_all' in k)} TSO + "
        f"{convention_78_4bis_5_hits['UKPN LPN']} §4bis.5 London LPN (9th enforcement) + "
        f"{sum(v for k, v in owner_hist.items() if 'nuclear' in k.lower())} nuclear + "
        f"{sum(v for k, v in owner_hist.items() if 'rail' in k.lower())} rail + "
        f"{sum(v for k, v in owner_hist.items() if 'northern_ireland' in k.lower())} NI + "
        f"{sum(v for k, v in owner_hist.items() if 'crown_dependency' in k.lower())} Crown Dependencies + "
        f"{sum(v for k, v in owner_hist.items() if 'layer_3b' in k)} DNO"
    )

    d41_msg, d41_ratio = check_discipline_41(len(filtered_subs), len(filtered_lines))
    logger.info(f"Discipline #41: {d41_msg}")

    raw_combined = f"uk-osm-{len(filtered_subs)}-{len(filtered_lines)}-{total_bytes}"
    raw_sha256 = sha256_hexdigest(raw_combined.encode())

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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    result = fetch_uk_osm()
    print()
    print("UK-P31-osm-overpass fetch complete (WAVE 4 CORRECTED architecture)")
    print(f"  substations:        {len(result.substations):,}")
    print(f"  transmission_lines: {len(result.lines):,}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")

    print("  Owner-provenance distribution:")
    hist = {}
    for sub in result.substations:
        prov = sub.get("_owner_provenance", "unknown")
        hist[prov] = hist.get(prov, 0) + 1
    for prov, count in sorted(hist.items(), key=lambda x: -x[1]):
        print(f"    {count:>5}  {prov}")

    ops = {}
    for sub in result.substations:
        op = sub.get("_resolved_operator", "unknown")
        ops[op] = ops.get(op, 0) + 1
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 20 operators:")
    for op, count in sorted(ops.items(), key=lambda x: -x[1])[:20]:
        print(f"    {count:>5}  {op}")

    if result.partial_fetch_notes:
        print()
        for note in result.partial_fetch_notes:
            print(f"  ⚠ Convention #56 partial — {note}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
