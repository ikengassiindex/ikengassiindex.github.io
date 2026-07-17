"""
SSI Pipeline — Greece L1 connector: OSM Overpass API.

Source ID:   GR-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 1500-3500 elements (way)
                          expected 500-1500 elements (node)
                          expected 10-30 elements (relation)
  - power=line             expected 5000-15000 ways (Balkan line-density)
  - power=cable            urban underground (Athens metro core)
  - power=minor_line       MV distribution branches

DIFFERENCE FROM CZECHIA CONNECTOR (post-Convention #78 BINDING 3rd-enforcement
Poland close-out — Wave 3 first-country simplification):
  - SMALLER SCALE — Greece is ~131k km² (~2.7× Czechia). But smaller
    infrastructure footprint due to lower population density + more
    dispersed rural coverage + Aegean island fragmentation.
    Single-query per element type is safe; no bbox partitioning needed.

  - SIMPLEST ATTRIBUTION cohort-wide — SINGLE national DSO (DEDDIE/HEDNO)
    consolidated at 2012 unbundling from PPC. No sub-national DSO
    territorial partition. NO Convention #78 §4bis.5 Layer 3 lat/lon
    geofence needed. Attribution reduces to:
      * ≥66 kV → ADMIE (IPTO) — TSO
      * <66 kV → DEDDIE (HEDNO) — SINGLE national DSO
      * Voltage None → DEDDIE (HEDNO) default (distribution-tier dominant)
    Private infrastructure (Greek Railways OSE/ERGOSE, Athens Metro
    Attiko Metro, Aluminium of Greece, Hellenic Petroleum, Larco,
    industrial captives) surfaces via direct OSM operator= tag.

  - GREEK SCRIPT + LATIN TRANSLITERATION + ENGLISH ACRONYM + ΑΕ/SA
    LEGAL-FORM + GREEK DIACRITICS UNICODE ALIAS NORMALISATION per
    Convention #78 BINDING 4th enforcement — Unicode NFC + case-
    insensitive lookup for:
      * Greek script (ΑΔΜΗΕ / ΔΕΔΔΗΕ / ΔΕΗ / ΑΕ — dominant class)
      * Latin transliteration (ADMIE / DEDDIE / DEI)
      * English acronyms (IPTO / HEDNO / PPC)
      * Legal-form variants (ΑΕ / Α.Ε. / SA / S.A. / Anonymos Etaireia)
      * Greek diacritics (τόνος + διαλυτικά — accented letters)
      * DEI/PPC pre-2011 predecessor tags (single-generation rebrand —
        SHALLOWER than Poland's 3-generation cascade)
    ~50-80 entry alias map (vs Poland's 100-150 entries; Czechia's 250+).
    Preserves original tag in raw_attributes.osm_original_operator for
    audit trail. Estimated 800-2500 alias-normalisation hits (cumulative
    7-country post-Greece: 21,206-22,906 — 2,120-2,290× above BINDING
    threshold).

  - TSO THRESHOLD 66 kV — Greece's ADMIE/IPTO operates 400/150/66 kV
    including sub-transmission (unlike Central European countries where
    TSO operates 220+ kV only and 110 kV is DSO). 66 kV subtransmission
    below main HV mesh is architecturally TSO in Greece. Below 66 kV
    → DEDDIE distribution jurisdiction.


Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None; owner defaults to
    DEDDIE (distribution-tier dominant per baseline empirical distribution)
  - Missing operator tag → owner via voltage-class + single-DSO default
  - Overpass 429/504 → exponential backoff; graceful degradation

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred.

Discipline #36 cross-border filter — 100m default tolerance (per _base).
Greece's national territory defined by greece/bounds.json 14-polygon
(mainland + island clusters).
Discipline #41 line-substation pairing preserved.

Convention #78 §4bis.5 Layer 3 geofence — NOT REQUIRED (single national DSO).
"""

from __future__ import annotations

import hashlib
import logging
import time
import urllib.request
import urllib.error
import urllib.parse
import json

from ._base import (
    SubstationRecord,
    TransmissionLineRecord,
    IngestionResult,
    apply_bounds_filter,
    assert_line_parity,
    emit_audit_sidecar,
    cache_path_for,
    now_utc_iso,
    resolve_owner_from_region_jurisdiction,
    normalise_owner_alias,
)

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────
SOURCE_ID = "GR-C1-osm-overpass"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

DEFAULT_TIMEOUT_SECS = 120
DEFAULT_QUERY_TIMEOUT_SECS = 90
USER_AGENT = "SSI-Index-Foundation/1.0 (+https://ikengassiindex.github.io)"

INITIAL_BACKOFF_SECS = 30
MAX_BACKOFF_SECS = 300
MAX_RETRY_ATTEMPTS = 4


# ── HTTP fetch with rate-limit backoff ──────────────────────────────────
def _fetch_overpass(query: str, timeout: int = DEFAULT_TIMEOUT_SECS) -> bytes:
    """Fetch Overpass query with retry + endpoint fallback."""
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
                    break
                elif exc.code == 406:
                    logger.warning("Overpass 406; retry in 5s")
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
                break

    if last_err is not None:
        raise last_err
    raise RuntimeError("Overpass fetch failed on all endpoints without a specific error")


# ── Query builders ──────────────────────────────────────────────────────
_GR_AREA_HEADER = 'area["ISO3166-1"="GR"]->.gr'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_GR_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.gr);'
        f'out center tags;'
    )


def _query_lines() -> str:
    """Build Overpass query for all lines within Greece.

    Single-query safe for medium-compact country — Greece ~131k km²
    with dispersed rural + island coverage means lower per-km² line
    density than Central European countries (Czechia was single-query
    at ~49k km² with 54k lines — Greece expected ~8-18k lines within
    the timeout budget)."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_GR_AREA_HEADER};'
        f'(way["power"="line"](area.gr);'
        f'way["power"="cable"](area.gr);'
        f'way["power"="minor_line"](area.gr););'
        f'out geom tags;'
    )


# ── OSM element parsers ─────────────────────────────────────────────────
def _center_lat_lon(el: dict) -> tuple[float, float] | None:
    if el.get("type") == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def _parse_voltage_kv(tag_value: str | None) -> float | None:
    """Parse OSM voltage= tag (in volts, may be semicolon-separated)."""
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
    return max_v / 1000.0 if max_v > 2000 else max_v


def _substation_from_osm(el: dict) -> SubstationRecord | None:
    """Parse OSM substation element.

    Greek-specific: direct OSM operator= tag propagation with Greek
    script + Latin transliteration + English acronyms + Greek
    diacritics + ΑΕ/SA legal-form + DEI/PPC pre-2011 predecessor
    Unicode alias normalisation per Convention #78 BINDING 4th
    enforcement; if untagged, voltage-class × single-DSO resolver
    (ADMIE ≥66 kV OR DEDDIE <66 kV OR DEDDIE default for voltage-None).
    NO NUTS-3 map + NO Layer 3 geofence needed (single national DSO)."""
    coords = _center_lat_lon(el)
    if coords is None:
        return None
    lat, lon = coords
    tags = el.get("tags", {}) or {}

    osm_id = f"osm_{el.get('type', '?')}_{el.get('id', 0)}"
    voltage_kv = _parse_voltage_kv(tags.get("voltage"))

    op_tag = (tags.get("operator") or "").strip()

    if op_tag:
        owner = normalise_owner_alias(op_tag)
        owner_provenance = (
            "osm_operator_tag_direct_alias_normalised" if owner != op_tag
            else "osm_operator_tag_direct"
        )
    else:
        # Voltage-class × single-DSO resolver (SIMPLEST cohort-wide)
        nuts3 = tags.get('ref:nuts:3') or tags.get('nuts:3') or tags.get('nuts_3')
        owner, owner_provenance = resolve_owner_from_region_jurisdiction(
            voltage_kv, lat, lon, nuts3=nuts3
        )

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
            "osm_original_operator": op_tag if op_tag and op_tag != owner else None,
        },
    )


def _line_from_osm(el: dict) -> TransmissionLineRecord | None:
    """Parse OSM power=line element."""
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
    owner = normalise_owner_alias(op_tag) if op_tag else None

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
) -> IngestionResult:
    """Fetch OSM Greece substations + lines (single-query per element type).

    Compact-medium country — no partitioning needed. Uses OSM operator=
    tag with Greek script + Latin + English acronyms + ΑΕ/SA legal-form +
    diacritics + DEI/PPC predecessor Unicode alias normalisation per
    Convention #78 BINDING 4th enforcement, then voltage-class ×
    single-DSO fallback (ADMIE ≥66 kV OR DEDDIE <66 kV OR DEDDIE
    default) for untagged. Convention #56 preserved."""
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="GR",
    )

    # ── Substations (split by element type) ──
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

    # ── Lines (single-query, no partitioning) ──
    if ingest_lines:
        try:
            body = _fetch_overpass(_query_lines())
            try:
                data = json.loads(body)
                for el in data.get("elements", []):
                    rec = _line_from_osm(el)
                    if rec is not None:
                        result.transmission_lines.append(rec)
            except json.JSONDecodeError as exc:
                result.warnings.append(
                    f"Convention #56 — OSM lines JSON parse error: {exc}"
                )
        except Exception as exc:
            result.warnings.append(
                f"Convention #56 partial — OSM lines fetch failed: {exc}"
            )
        logger.info("Parsed %d lines from OSM Overpass", len(result.transmission_lines))

    # ── Discipline #36 bounds filter ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Greece polygon "
                "(100m default tolerance)."
            )

    # ── Owner enrichment summary ──
    if result.substations:
        from collections import Counter
        prov_counter = Counter(
            s.raw_attributes.get("owner_provenance", "none")
            for s in result.substations
        )
        direct = sum(
            v for k, v in prov_counter.items()
            if k.startswith("osm_operator_tag_direct")
        )
        admie_tso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_ADMIE")
        )
        deddie_dso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_DEDDIE")
        )
        alias_normalised = prov_counter.get("osm_operator_tag_direct_alias_normalised", 0)
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + %d ADMIE_TSO + %d DEDDIE_DSO",
            direct, alias_normalised, admie_tso, deddie_dso,
        )
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%; "
            f"of these {alias_normalised} alias-normalised incl. Greek script + Latin transliteration + English acronyms + ΑΕ/SA legal-form + Greek diacritics + DEI/PPC pre-2011 predecessor per Convention #78 BINDING 4th enforcement); "
            f"{admie_tso} ADMIE_TSO + {deddie_dso} DEDDIE_DSO "
            f"({100 * (admie_tso + deddie_dso) / len(result.substations):.1f}%)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass GR L1 connector — Greece voltage-class × single-DSO via ADMIE ≥66kV + DEDDIE <66kV + Convention #78 BINDING 4th-enforcement test (Greek script + Latin transliteration + English acronyms + ΑΕ/SA legal-form + Greek diacritics + DEI/PPC pre-2011 predecessor)")
    parser.add_argument("--skip-lines", action="store_true",
                        help="Skip line ingestion (subs only)")
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

    ops = Counter(s.owner for s in result.substations if s.owner)
    print(f"  Distinct operators: {len(ops)}")
    print("  Top 15 operators:")
    for k, v in ops.most_common(15):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
