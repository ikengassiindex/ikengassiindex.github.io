"""
SSI Pipeline — Switzerland L1 connector: OSM Overpass API.

Source ID:   CH-C1-osm-overpass
Publisher:   OpenStreetMap contributors via Overpass API
Licence:     ODbL (Open Database License) — attribution required

Feature classes ingested:
  - power=substation      expected 800-2000 elements (way)
                          expected 400-1000 elements (node)
                          expected 10-25 elements (relation)
  - power=line             expected 3000-8000 ways (Central European density)
  - power=cable            urban underground (Zürich + Geneva metros)
  - power=minor_line       MV distribution branches

DIFFERENCE FROM ICELAND CONNECTOR (Wave 3 P23 multi-DSO precedent):
  - LARGER SCALE — Switzerland is ~41k km² (~0.4× Iceland at 103k km²
    but 3× denser DSO population — Central European contributor
    density is HIGH vs Nordic-Arctic sparsity). Single-query per
    element type expected reliable. 504 gateway timeouts less likely
    than Iceland/Greek Nordic/Mediterranean sparsity but possible on
    line-query (largest payload) — Convention #56 partial-fetch
    preservation ready.

  - MULTI-METRO ATTRIBUTION cohort-wide — 5 major cantonal DSOs +
    3 metro DSO carve-outs + ~600 municipal DSOs (LARGEST DSO
    fragmentation cohort-wide). Convention #78 §4bis.5 Layer 3
    lat/lon geofence REQUIRED at 8-way partition:
      * ≥220 kV → Swissgrid — TSO (380/220 kV backbone)
      * <220 kV → 8-way geofence:
        - EWZ Zürich Stadt metro (Convention #78 §4bis.5 3rd
          enforcement candidate — narrow city carve-out)
        - SIG Geneva metro (Convention #78 §4bis.5 4th enforcement
          candidate)
        - SIL Lausanne metro (Convention #78 §4bis.5 5th enforcement
          candidate — smaller carve-out)
        - IWB Basel-Stadt metro
        - AET Ticino canton
        - Repower Graubünden canton
        - SIG Genève canton (broader)
        - Groupe E Fribourg + Neuchâtel
        - Romande Energie Vaud + Valais
        - CKW Zentralschweiz
        - BKW Bern + Jura
        - Axpo Grid Deutschschweiz default catch-all
      * 150 kV boundary → Swissgrid fallback (mixed tier)

  - 4-LANGUAGE SCRIPT COHABITATION + TRILINGUAL LEGAL-FORM +
    PREDECESSOR REBRAND UNICODE ALIAS NORMALISATION per Convention
    #78 BINDING 6th enforcement — Unicode NFC + case-insensitive
    lookup for:
      * German diacritics (ä ö ü ß + Swiss usage ß→ss) — DOMINANT
      * French diacritics (à é è ê ï ô ù û) — Romandie regions
      * Italian diacritics (à è ì ò ù) — Ticino canton
      * Romansh (rare — <5% Graubünden — SA legal form)
      * Trilingual legal-form variants (AG German / SA French/Romansh
        / SpA Italian)
      * Predecessor rebrand tags: NOK → Axpo Grid (2001 — 25-year
        LARGEST legacy) + Bernische Kraftwerke → BKW (2013) + EEF →
        Groupe E (2006) + EOS → Romande Energie (2007) + Rätia
        Energie → Repower (2007)
    ~150-entry alias map (LARGEST Wave 3 cohort; comparable to
    Poland 150 + Czechia 250+). Preserves original tag in
    raw_attributes.osm_original_operator for audit trail. Estimated
    500-2000 alias-normalisation hits (cumulative 9-country
    post-Switzerland: 21,018-22,518 — 2,101-2,251× above BINDING
    threshold).

  - TSO THRESHOLD 220 kV — Swissgrid operates 380/220 kV EHV
    backbone. Below 220 kV is DSO jurisdiction. 150 kV subtransmission
    is architecturally mixed (Layer 4 fallback to Swissgrid if
    geofence returns None; otherwise Layer 3 wins per resolver
    precedence).


Convention #56 visibly-honest degradation:
  - Missing OSM voltage tag → voltage_kv = None; owner defaults to
    Axpo Grid (LARGEST cantonal DSO catch-all)
  - Missing operator tag → owner via voltage-class × Layer 3 geofence
  - Overpass 429/504 → exponential backoff; graceful degradation
    (Central European OSM density is HIGH but 504 possible on
    line-query — largest payload)

Convention #60 non-commercial provenance:
  - OSM (ODbL) only. Public open-data cross-validation deferred.

Discipline #36 cross-border filter — 0.5 km default tolerance (per
_base — Alpine ridge-line + 41-interconnector precedent applied to
Switzerland's 1739 km international border with FR/DE/IT/AT/LI +
Büsingen DE + Campione d'Italia IT enclaves inside Swiss territory).

Discipline #41 line-substation pairing preserved.

Convention #78 §4bis.5 Layer 3 geofence — REQUIRED (8-way multi-metro
+ multi-cantonal territorial partition: EWZ + SIG + SIL + IWB + AET
+ Repower + Groupe E + Romande Energie + CKW + BKW + Axpo Grid).
Cumulative enforcement count post-Switzerland: 5 (Prague CZ +
Warsaw PL + EWZ Zürich + SIG Geneva + SIL Lausanne).
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
SOURCE_ID = "CH-C1-osm-overpass"
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
_CH_AREA_HEADER = 'area["ISO3166-1"="CH"]->.ch'


def _query_substations(feature_type: str = "way") -> str:
    """Build Overpass query for one substation element type."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_CH_AREA_HEADER};'
        f'{feature_type}["power"="substation"](area.ch);'
        f'out center tags;'
    )


def _query_lines() -> str:
    """Build Overpass query for all lines within Switzerland.

    Single-query safe for medium-scale country — Switzerland ~41k km²
    with HIGH Central European OSM contributor density. Expected
    3000-8000 lines within timeout budget; 504 possible on largest
    payload — Convention #56 partial-fetch preservation preserved."""
    return (
        f'[out:json][timeout:{DEFAULT_QUERY_TIMEOUT_SECS}];'
        f'{_CH_AREA_HEADER};'
        f'(way["power"="line"](area.ch);'
        f'way["power"="cable"](area.ch);'
        f'way["power"="minor_line"](area.ch););'
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

    Switzerland-specific: direct OSM operator= tag propagation with
    4-language script cohabitation (German + French + Italian +
    Romansh) + trilingual legal-form variants (AG/SA/SpA) + Swiss
    diacritics + predecessor rebrand cascades (NOK → Axpo Grid /
    Bernische Kraftwerke → BKW / EEF → Groupe E / EOS → Romande
    Energie / Rätia Energie → Repower) Unicode alias normalisation
    per Convention #78 BINDING 6th enforcement; if untagged,
    voltage-class × Layer 3 8-way multi-metro + multi-cantonal DSO
    resolver (Swissgrid ≥220 kV OR EWZ/SIG/SIL/IWB/AET/Repower/
    Groupe E/Romande Energie/CKW/BKW via geofence OR Axpo Grid
    default). Layer 3 geofence REQUIRED (8-way territorial partition
    with 3 metro carve-outs — Convention #78 §4bis.5 3rd + 4th + 5th
    enforcement candidates)."""
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
        # Voltage-class × Layer 3 8-way multi-metro/multi-cantonal DSO resolver
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
    """Fetch OSM Switzerland substations + lines (single-query per element type).

    Medium-scale country — no partitioning needed. Uses OSM operator=
    tag with 4-language script cohabitation (German + French + Italian
    + Romansh) + trilingual legal-form (AG/SA/SpA) + Swiss diacritics
    + predecessor rebrand cascades (NOK/Bernische Kraftwerke/EEF/EOS/
    Rätia Energie) Unicode alias normalisation per Convention #78
    BINDING 6th enforcement, then voltage-class × Layer 3 8-way
    multi-metro/multi-cantonal DSO fallback (Swissgrid ≥220 kV OR
    EWZ/SIG/SIL/IWB/AET/Repower/Groupe E/Romande Energie/CKW/BKW via
    geofence OR Axpo Grid default) for untagged. Convention #56
    preserved."""
    result = IngestionResult(
        source_id=SOURCE_ID,
        fetched_at_utc=now_utc_iso(),
        source_url=OVERPASS_ENDPOINTS[0],
        provincial_scope="CH",
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

    # ── Discipline #36 bounds filter (0.5 km Alpine ridge-line tolerance) ──
    if apply_bounds:
        subs_kept, subs_dropped = apply_bounds_filter(result.substations)
        lines_kept, lines_dropped = apply_bounds_filter(result.transmission_lines)
        result.substations = subs_kept
        result.transmission_lines = lines_kept
        if subs_dropped or lines_dropped:
            result.warnings.append(
                f"Discipline #36 — dropped {len(subs_dropped)} substations + "
                f"{len(lines_dropped)} lines outside Switzerland polygon "
                "(0.5 km Alpine ridge-line tolerance)."
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
        swissgrid_tso = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_Swissgrid")
        )
        axpo_grid = sum(
            v for k, v in prov_counter.items()
            if k.startswith("region_jurisdiction_fallback_Axpo Grid")
            or k.startswith("region_jurisdiction_fallback_Axpo_Grid")
        )
        bkw = sum(
            v for k, v in prov_counter.items()
            if "BKW" in k
        )
        ckw = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_CKW" in k
        )
        groupe_e = sum(
            v for k, v in prov_counter.items()
            if "Groupe E" in k or "Groupe_E" in k
        )
        romande = sum(
            v for k, v in prov_counter.items()
            if "Romande Energie" in k or "Romande_Energie" in k
        )
        ewz = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_EWZ" in k
        )
        sig = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_SIG" in k
        )
        sil = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_SIL" in k
        )
        iwb = sum(
            v for k, v in prov_counter.items()
            if "IWB" in k
        )
        aet = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_AET" in k
        )
        repower = sum(
            v for k, v in prov_counter.items()
            if "region_jurisdiction_fallback_Repower" in k
        )
        alias_normalised = prov_counter.get("osm_operator_tag_direct_alias_normalised", 0)
        logger.info(
            "Owner enrichment: %d direct OSM (%d alias-normalised) + "
            "%d Swissgrid_TSO + %d Axpo_Grid + %d BKW + %d CKW + "
            "%d Groupe_E + %d Romande_Energie + %d EWZ + %d SIG + "
            "%d SIL + %d IWB + %d AET + %d Repower",
            direct, alias_normalised, swissgrid_tso, axpo_grid, bkw, ckw,
            groupe_e, romande, ewz, sig, sil, iwb, aet, repower,
        )
        dso_total = axpo_grid + bkw + ckw + groupe_e + romande + ewz + sig + sil + iwb + aet + repower
        result.warnings.append(
            f"Owner enrichment: {direct}/{len(result.substations)} direct "
            f"OSM operator= tag ({100 * direct / len(result.substations):.1f}%; "
            f"of these {alias_normalised} alias-normalised incl. German (ä ö ü ß) + French (à é è ê ï ô ù û) + Italian (à è ì ò ù) + Romansh + trilingual AG/SA/SpA legal-form + NOK/Bernische Kraftwerke/EEF/EOS/Rätia Energie predecessor per Convention #78 BINDING 6th enforcement); "
            f"{swissgrid_tso} Swissgrid_TSO + {dso_total} regional DSOs "
            f"(Axpo_Grid {axpo_grid} + BKW {bkw} + CKW {ckw} + Groupe_E {groupe_e} + "
            f"Romande_Energie {romande} + EWZ {ewz} + SIG {sig} + SIL {sil} + "
            f"IWB {iwb} + AET {aet} + Repower {repower}) "
            f"({100 * (swissgrid_tso + dso_total) / len(result.substations):.1f}%)."
        )

    # ── Discipline #41 parity ──
    parity_ok, findings = assert_line_parity(result, outbound_border_ok=False)
    for f in findings:
        logger.info("Discipline #41: %s", f)

    return result


# ── CLI harness ──────────────────────────────────────────────────────────
def _cli_main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="OSM Overpass CH L1 connector — Switzerland voltage-class × Layer 3 8-way multi-metro/multi-cantonal DSO via Swissgrid ≥220kV + EWZ/SIG/SIL/IWB metro carve-outs + AET/Repower/Groupe E/Romande Energie/CKW/BKW cantonal geofence + Axpo Grid default + Convention #78 BINDING 6th-enforcement test (4-language script cohabitation: German ä ö ü ß + French à é è ê ï ô ù û + Italian à è ì ò ù + Romansh + trilingual AG/SA/SpA legal-form + NOK/Bernische Kraftwerke/EEF/EOS/Rätia Energie predecessor)")
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
    print("  Top 25 operators:")
    for k, v in ops.most_common(25):
        print(f"    {v:>5}  {k}")

    for w in result.warnings:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    _cli_main()
