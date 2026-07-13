"""
SSI Pipeline — Mexico L1 connector: OSM Overpass API.

Source ID:   MX-C1-osm-overpass (primary — federal-canonical unavailable per Step 1 audit)
Publisher:   OpenStreetMap contributors via Overpass API
Endpoint:    https://overpass-api.de/api/interpreter
Licence:     ODbL (Open Database License) — attribution required
Vintage:     Real-time (OSM Planet mirror, refreshed within ~1 minute)

Feature classes ingested (empirically anchored at Step 2, SHA-256 66b0c0328491):
  - power=substation      3,097 elements (3,041 ways + 44 nodes + 12 relations)
  - power=line          ~15,000-30,000 lines (literature-based; empirical retry
                          via rate-limit backoff at fetch time)
  - power=cable          minor (submarine + some urban)
  - power=minor_line     minor (small distribution branches)

CFE-MONOPOLY FALLBACK RULE (Mexico-specific per Step 2 audit):
  For substations without an OSM operator= tag, apply operator = "Comisión Federal
  de Electricidad" (CFE) as default UNLESS the substation carries substation=industrial
  (which typically indicates factory self-generation with private operators).  This
  covers ~2,500 of the 2,583 untagged substations per Step 2 empirical distribution
  (92.4% of tagged operators are CFE variants; industrial 521 subs skip default).

Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None (not 0.0 default)
  - Missing operator AND substation=industrial → owner = None (respect self-gen)
  - Missing operator AND not industrial → owner = "Comisión Federal de Electricidad"
    with provenance recorded as "cfe_monopoly_fallback"
  - Overpass 429/504 → retry with exponential backoff; if all attempts fail,
    return empty IngestionResult with warning listing Discipline reference

Convention #60 non-commercial provenance:
  - Only OSM (ODbL) + INEGI DENUE (public government open data) used; NO
    commercial ESG or utility-inventory paid feeds.

Discipline #36 cross-border filter — 100m default tolerance for Mexico bounds.
Discipline #41 line-substation pairing preserved.
"""

from __future__ import annotations

import hashlib
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
import json
from pathlib import Path

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "MX-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",     # fallback mirror
    "https://overpass.private.coffee/api/interpreter",   # secondary fallback
]

DEFAULT_TIMEOUT_SECS = 120
DEFAULT_QUERY_TIMEOUT_SECS = 90                         # server-side [timeout:N]
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

# CFE-monopoly fallback rule
CFE_CANONICAL_NAME = "Comisión Federal de Electricidad"
CFE_TAG_VARIANTS = frozenset({
    "CFE", "cfe", "C.F.E.", "C.F.E",
    "Comisión Federal de Electricidad",
    "Comision Federal de Electricidad",
    "Comisión Federal de Electricidad (CFE)",
    "Comisión Federal De Electricidad",
})
# Industrial self-gen — do NOT apply CFE monopoly fallback
INDUSTRIAL_SELF_GEN_SUBSTATION_TAGS = frozenset({
    "industrial",
    "industrial;generation",
    "generation;industrial",
})

# Rate-limit backoff
INITIAL_BACKOFF_SECS = 30                                # first retry after 30s
MAX_BACKOFF_SECS = 300                                    # cap at 5 minutes
MAX_RETRY_ATTEMPTS = 4                                    # per endpoint


# ── HTTP fetch with rate-limit backoff ──────────────────────────────────
def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
    """Fetch Overpass query with retry + endpoint fallback.

    Handles HTTP 429 (rate limit) with exponential backoff, HTTP 504
    (gateway timeout) with fallback endpoint, HTTP 406 (Not Acceptable —
    often triggered by data payload) with Accept header retry.
    """
    cache = cache_path_for(query)
    if cache.exists():
        body = cache.read_bytes()
        logger.info("Cache hit: %s (%d bytes)", cache.name, len(body))
        return body

    data = urllib.parse.urlencode({"data": query}).encode("ascii")
    last_err: Exception | None = None

    for endpoint_idx, endpoint in enumerate(OVERPASS_ENDPOINTS):
        backoff = INITIAL_BACKOFF_SECS
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=data,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                logger.info(
                    "Overpass POST %s (attempt %d/%d)",
                    endpoint, attempt + 1, MAX_RETRY_ATTEMPTS,
                )
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                cache.write_bytes(body)
                return body
            except urllib.error.HTTPError as exc:
                last_err = exc
                if exc.code == 429:
                    logger.warning(
                        "Overpass 429 rate-limited; backing off %.0fs (attempt %d)",
                        backoff, attempt + 1,
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECS)
                    continue
                elif exc.code in (502, 503, 504):
                    logger.warning(
                        "Overpass %d gateway; trying next endpoint after 5s",
                        exc.code,
                    )
                    time.sleep(5)
                    break  # try next endpoint
                elif exc.code == 406:
                    logger.warning("Overpass 406; retry with plain Accept in 5s")
                    time.sleep(5)
                    continue
                else:
                    logger.error("Overpass HTTP %d: %s", exc.code, exc.reason)
                    time.sleep(5)
                    continue
            except (urllib.error.URLError, TimeoutError) as exc:
                last_err = exc
                logger.warning("Overpass network error: %s; trying next endpoint after 5s", exc)
                time.sleep(5)
                break  # try next endpoint

    if last_err is not None:
        raise last_err
    raise RuntimeError("Overpass fetch failed on all endpoints without a specific error")


# ── Query builders ──────────────────────────────────────────────────────
_MX_AREA_HEADER = 'area["ISO3166-1"="MX"]->.mx'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type.

    Split by type (way / node / relation) because single-query full-country
    fetch triggers 504 gateway timeouts on public Overpass endpoints.
    """
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_MX_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.mx);'
        f'out center tags;'
    )


def _query_lines_bbox(south: float, west: float, north: float, east: float) -> str:
    """Build Overpass query for lines in a bbox (bbox-partitioned to avoid 504)."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'(way["power"="line"]({south},{west},{north},{east});'
        f'way["power"="cable"]({south},{west},{north},{east});'
        f'way["power"="minor_line"]({south},{west},{north},{east}););'
        f'out geom tags;'
    )


# Mexico bounding-box quadrants for line-fetch partitioning
_MX_LINE_QUADRANTS = [
    # (south, west, north, east, label)
    (14.5, -118.5, 23.6, -102.35, "SW"),
    (23.6, -118.5, 32.7, -102.35, "NW"),
    (14.5, -102.35, 23.6, -86.5, "SE"),
    (23.6, -102.35, 32.7, -86.5, "NE"),
]


# ── OSM element parsers ─────────────────────────────────────────────────
def _center_lat_lon(el: dict) -> tuple[float, float] | None:
    """Extract lat/lon from OSM element (node = lat/lon; way/relation = center)."""
    if el.get("type") == "node":
        lat = el.get("lat")
        lon = el.get("lon")
    else:
        center = el.get("center") or {}
        lat = center.get("lat")
        lon = center.get("lon")
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def _parse_voltage_kv(tag_value: str | None) -> float | None:
    """Parse OSM voltage= tag (in volts, may be semicolon-separated multi-values).

    Returns kV as float or None if unparseable.  When multi-valued (e.g.
    '115000;230000'), returns MAX (highest operating voltage class).
    """
    if not tag_value:
        return None
    values = []
    for token in tag_value.replace(",", "").split(";"):
        token = token.strip().rstrip("V").strip()
        try:
            v = float(token)
            if v > 0:
                values.append(v)
        except ValueError:
            continue
    if not values:
        return None
    max_v = max(values)
    # OSM standard: volts.  If already looks like kV (< 2000), pass through.
    return max_v / 1000.0 if max_v > 2000 else max_v


def _apply_cfe_monopoly_fallback(
    tags: dict,
) -> tuple[str | None, str | None]:
    """Apply CFE-monopoly fallback rule per Step 2 audit.

    Returns:
        (canonical_owner_name, provenance_tag)

    Rules:
        1. If OSM operator= tag present + matches any CFE variant → normalize to
           canonical Spanish name + provenance "osm_operator_tag_cfe_normalized"
        2. If OSM operator= tag present + non-CFE → use verbatim + provenance
           "osm_operator_tag_native"
        3. If OSM operator= tag absent + substation=industrial → owner = None +
           provenance "convention_56_industrial_self_gen_no_default"
        4. If OSM operator= tag absent + non-industrial → owner = CFE canonical +
           provenance "cfe_monopoly_fallback"
    """
    op_tag = (tags.get("operator") or "").strip()
    sub_tag = (tags.get("substation") or "").strip()

    if op_tag:
        # Case 1 or 2
        if op_tag in CFE_TAG_VARIANTS or op_tag.lower().startswith("comisión federal"):
            return CFE_CANONICAL_NAME, "osm_operator_tag_cfe_normalized"
        else:
            return op_tag, "osm_operator_tag_native"

    # No operator tag — apply CFE fallback
    if sub_tag in INDUSTRIAL_SELF_GEN_SUBSTATION_TAGS:
        # Case 3: industrial self-gen, Convention #56 respects the gap
        return None, "convention_56_industrial_self_gen_no_default"

    # Case 4: CFE monopoly fallback
    return CFE_CANONICAL_NAME, "cfe_monopoly_fallback"


def _substation_from_osm(el: dict) -> SubstationRecord | None:
    """Parse OSM substation element to SubstationRecord."""
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    owner, owner_provenance = _apply_cfe_monopoly_fallback(tags)

    return SubstationRecord(
        source_id=SOURCE_ID,
        feature_id=osm_id,
        latitude=lat,
        longitude=lon,
        voltage_kv=voltage_kv,
        owner=owner,
        operator_station_name=tags.get("name"),
        raw_attributes={
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "osm_tags": tags,
            "owner_provenance": owner_provenance,
            "osm_substation_subtype": tags.get("substation"),
            "osm_location": tags.get("location"),
            "osm_ref": tags.get("ref"),
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
    """Parse OSM power=line element to TransmissionLineRecord."""
    geom = el.get("geometry") or []
    if not geom or len(geom) < 2:
        return None
    coords: list[list[float]] = []
    for pt in geom:
        lat = pt.get("lat")
        lon = pt.get("lon")
        if lat is None or lon is None:
            continue
        coords.append([float(lon), float(lat)])
    if len(coords) < 2:
        return None

    tags = el.get("tags", {}) or {}
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))
    op_tag = (tags.get("operator") or "").strip()
    owner = None
    if op_tag:
        if op_tag in CFE_TAG_VARIANTS or op_tag.lower().startswith("comisión federal"):
            owner = CFE_CANONICAL_NAME
        else:
            owner = op_tag
    else:
        # CFE monopoly default for HV+ lines; keep None for smaller/local
        power_tag = tags.get("power", "").strip()
        if power_tag == "line" and voltage_kv and voltage_kv >= 34.5:
            owner = CFE_CANONICAL_NAME

    return TransmissionLineRecord(
        source_id=SOURCE_ID,
        feature_id=f"osm_way_{el.get('id', 0)}",
        coordinates_multilinestring=[coords],
        voltage_kv=voltage_kv,
        owner=owner,
        line_name=tags.get("name"),
        raw_attributes={
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "osm_tags": tags,
            "osm_power_class": tags.get("power"),
            "osm_cables": tags.get("cables"),
            "osm_wires": tags.get("wires"),
            "osm_circuits": tags.get("circuits"),
        },
    )


# ── Public entry ─────────────────────────────────────────────────────────
def fetch(
    *,
    apply_bounds: bool = True,
    ingest_lines: bool = True,
    max_line_quadrants: int | None = None,
) -> IngestionResult:
    """Fetch OSM Mexico substations + lines.

    Discipline #41 line-substation pairing satisfied by ingesting both classes
    in the same fetch pass.  Convention #56 visibly-honest degradation applied
    to missing voltage / operator tags.  CFE-monopoly fallback rule applied
    per Step 2 audit finding.
    """
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="MX",
    )

    # ── Substations (split by element type to avoid 504) ──
    all_sub_bytes = bytearray()
    for feat_type in ("way", "node", "relation"):
        try:
            body = _fetch_overpass(_query_substations(feat_type))
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — OSM substation {feat_type} fetch failed: {exc}"
            )
            continue
        all_sub_bytes.extend(body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            result.warnings.append(
                f"Convention #56 — OSM {feat_type} JSON parse error: {exc}"
            )
            continue
        for el in data.get("elements", []):
            rec = _substation_from_osm(el)
            if rec is not None:
                result.substations.append(rec)

    result.raw_bytes_fetched = len(all_sub_bytes)
    result.raw_sha256 = hashlib.sha256(bytes(all_sub_bytes)).hexdigest()
    logger.info("Parsed %d substations from OSM Overpass", len(result.substations))

    # ── Lines (bbox-partitioned quadrants to avoid 504) ──
    if ingest_lines:
        quadrants = _MX_LINE_QUADRANTS
        if max_line_quadrants is not None:
            quadrants = quadrants[:max_line_quadrants]
        for (south, west, north, east, label) in quadrants:
            try:
                body = _fetch_overpass(_query_lines_bbox(south, west, north, east))
            except Exception as exc:
                result.warnings.append(
                    f"Convention #56 partial — OSM lines quadrant {label} fetch failed: {exc}"
                )
                continue
            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                result.warnings.append(
                    f"Convention #56 — OSM lines {label} JSON parse error: {exc}"
                )
                continue
            for el in data.get("elements", []):
                rec = _line_from_osm(el)
                if rec is not None:
                    result.transmission_lines.append(rec)
            logger.info(
                "Parsed lines from quadrant %s: %d cumulative",
                label, len(result.transmission_lines),
            )

    # ── Discipline #36 bounds filter ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Mexico polygon "
                "(100m default tolerance per cross_border_tolerances.json)."
            )

    # ── Owner enrichment summary (CFE fallback rule) ──
    if result.substations:
        cfe_total = sum(
            1 for s in result.substations
            if s.owner == CFE_CANONICAL_NAME
        )
        cfe_from_osm_tag = sum(
            1 for s in result.substations
            if s.owner == CFE_CANONICAL_NAME
            and s.raw_attributes.get("owner_provenance") == "osm_operator_tag_cfe_normalized"
        )
        cfe_from_fallback = sum(
            1 for s in result.substations
            if s.owner == CFE_CANONICAL_NAME
            and s.raw_attributes.get("owner_provenance") == "cfe_monopoly_fallback"
        )
        industrial_no_owner = sum(
            1 for s in result.substations
            if s.owner is None
            and s.raw_attributes.get("owner_provenance") == "convention_56_industrial_self_gen_no_default"
        )
        non_cfe_named = sum(
            1 for s in result.substations
            if s.owner is not None and s.owner != CFE_CANONICAL_NAME
        )
        logger.info(
            "CFE monopoly fallback: %d CFE total (%d from OSM tag, %d from fallback); "
            "%d industrial no-default; %d non-CFE named",
            cfe_total, cfe_from_osm_tag, cfe_from_fallback,
            industrial_no_owner, non_cfe_named,
        )
        result.warnings.append(
            f"CFE fallback rule applied: {cfe_total}/{len(result.substations)} "
            f"substations attributed to Comisión Federal de Electricidad "
            f"({cfe_from_osm_tag} OSM-tagged + {cfe_from_fallback} monopoly-fallback); "
            f"{industrial_no_owner} industrial subs preserved without owner default."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    """Manual invocation harness for empirical validation runs."""
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass MX L1 connector")
    parser.add_argument("--skip-lines", action="store_true",
                        help="Skip line ingestion (subs only, faster smoke test)")
    parser.add_argument("--max-quadrants", type=int, default=None,
                        help="Cap number of line quadrants (for smoke testing)")
    parser.add_argument("--no-bounds", action="store_true",
                        help="Skip Discipline #36 filter")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    result = fetch(
        apply_bounds=not args.no_bounds,
        ingest_lines=not args.skip_lines,
        max_line_quadrants=args.max_quadrants,
    )

    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    audit_path = emit_audit_sidecar(result, parity_findings=findings)

    print(f"\n{SOURCE_ID} fetch complete")
    print(f"  substations:        {len(result.substations):,}")
    print(f"  transmission_lines: {len(result.transmission_lines):,}")
    print(f"  raw_bytes_fetched:  {result.raw_bytes_fetched:,}")
    print(f"  raw_sha256:         {result.raw_sha256}")
    print(f"  audit_sidecar:      {audit_path}")

    from collections import Counter
    prov = Counter(
        s.raw_attributes.get("owner_provenance", "none")
        for s in result.substations
    )
    print("  Owner-provenance distribution:")
    for k, v in prov.most_common():
        print(f"    {v:>5}  {k}")

    if result.transmission_lines:
        v_bucket = Counter()
        for ln in result.transmission_lines:
            kv = ln.voltage_kv or 0
            if kv >= 300: v_bucket['≥300kV transmission'] += 1
            elif kv >= 115: v_bucket['115-230kV HV'] += 1
            elif kv >= 33: v_bucket['33-115kV MV/HV'] += 1
            elif kv > 0: v_bucket['<33kV distribution'] += 1
            else: v_bucket['unspecified'] += 1
        print("  Line voltage-tier distribution:")
        for k, v in v_bucket.most_common():
            print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
