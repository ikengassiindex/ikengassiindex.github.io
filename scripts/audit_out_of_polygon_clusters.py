#!/usr/bin/env python3
"""
audit_out_of_polygon_clusters.py — General-purpose out-of-polygon substation
cluster diagnostic for cross-border pollution detection.

USAGE
-----
    python3 scripts/audit_out_of_polygon_clusters.py <country_slug>

    # Example:
    python3 scripts/audit_out_of_polygon_clusters.py sweden
    python3 scripts/audit_out_of_polygon_clusters.py spain

WHAT IT DOES
------------
Reads <country>/ssi-data.json + <country>/bounds.json. Runs point-in-polygon
for every substation. Buckets the OUT-OF-POLYGON subs into likely-origin
clusters:

  - inside a neighbor country's bbox (empirically-defined per-country list)
  - offshore (over open water, e.g. Baltic Sea, Aegean, Atlantic)
  - unclear (would need finer diagnostic)

Emits summary table + writes JSON audit report to
  ~/out_of_polygon_audit_<country>_<timestamp>.json

Motivates operator decision:
  (a) Re-run Discipline #36 remediation (scripts/remediate_cross_border.py)
      if the pollution is at the ingestion layer
  (b) Re-run Wave 4 OSM Overpass with tighter bbox if the pollution is at
      the fetch layer (bbox overshoots into neighbor countries)
  (c) Both

CONTEXT
-------
Task #501 follow-on Item 1 (Sweden) + Item 2 (Spain) — the Task #501
polygon apply reported ~4,700 Sweden subs + ~7,300 Spain subs as
n_outside_polygons (Convention #56 fallback). This utility enumerates
which neighbor countries + offshore basins account for the pollution.

Convention #7 documented-proxy: neighbor bboxes are empirical envelopes
sourced from Natural Earth 1:10M country boundaries; bbox coverage is
conservative (tight bboxes to minimize false-positives).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Neighbor bboxes (empirical, Natural Earth 1:10M-derived) ──────────
# Format: (min_lon, min_lat, max_lon, max_lat)
#
# Each country's likely-pollution neighbor list, plus offshore basins.
# Ordered by likelihood; first match wins in the cluster attribution.

NEIGHBOR_BBOXES: Dict[str, List[Tuple[str, Tuple[float, float, float, float]]]] = {
    "sweden": [
        ("Denmark",         (8.0, 54.5, 12.7, 57.8)),
        ("Norway",          (4.5, 57.9, 11.5, 71.2)),
        ("Finland",         (19.5, 59.8, 31.6, 70.1)),
        ("Estonia",         (21.7, 57.5, 28.2, 59.7)),
        ("Latvia",          (20.9, 55.6, 28.3, 58.1)),
        ("Lithuania",       (20.9, 53.9, 26.9, 56.5)),
        ("Poland (N)",      (14.1, 53.9, 23.9, 55.9)),
        ("Baltic Sea offshore",   (11.5, 54.5, 21.0, 60.2)),
        ("Gulf of Bothnia offshore", (17.5, 60.5, 25.5, 65.9)),
        ("North Sea offshore",    (3.0, 55.0, 11.0, 60.0)),
    ],
    "spain": [
        ("France (SW)",     (-1.8, 42.3, 3.4, 43.8)),
        ("Portugal",        (-9.5, 36.9, -6.2, 42.2)),
        ("Andorra",         (1.4, 42.4, 1.8, 42.7)),
        ("Morocco (N)",     (-6.5, 27.6, -1.0, 35.9)),
        ("Algeria (N coast)", (-2.5, 34.5, 3.0, 37.5)),
        ("Gibraltar",       (-5.4, 36.1, -5.3, 36.2)),
        ("Balearic Sea offshore", (0.5, 38.5, 5.0, 41.0)),
        ("Bay of Biscay offshore", (-6.0, 43.5, -1.0, 46.5)),
        ("Atlantic offshore (Iberian)", (-11.0, 36.0, -6.0, 43.5)),
        ("Mediterranean offshore (SW)", (-1.0, 35.5, 5.0, 40.5)),
    ],
    "italy": [
        ("France (SE)",     (5.5, 43.4, 7.9, 45.5)),
        ("Switzerland",     (5.9, 45.8, 10.5, 47.8)),
        ("Austria",         (9.5, 46.4, 17.2, 49.0)),
        ("Slovenia",        (13.4, 45.4, 16.6, 46.9)),
        ("Croatia",         (13.4, 42.4, 19.4, 46.6)),
        ("Tunisia (N)",     (7.5, 32.5, 11.6, 37.6)),
        ("Malta",           (14.2, 35.8, 14.6, 36.1)),
        ("San Marino",      (12.4, 43.9, 12.5, 44.0)),
        ("Vatican",         (12.4, 41.9, 12.5, 41.91)),
        ("Adriatic Sea offshore", (12.5, 40.0, 19.5, 45.8)),
        ("Tyrrhenian Sea offshore", (9.0, 38.0, 15.5, 44.0)),
        ("Ionian Sea offshore",   (15.0, 35.0, 21.5, 40.5)),
        ("Ligurian Sea offshore", (7.0, 43.0, 10.5, 44.5)),
    ],
    "germany": [
        ("Denmark",         (8.0, 54.5, 12.7, 57.8)),
        ("Netherlands",     (3.3, 50.7, 7.3, 53.6)),
        ("Belgium",         (2.5, 49.4, 6.5, 51.5)),
        ("Luxembourg",      (5.7, 49.4, 6.6, 50.2)),
        ("France (E)",      (5.5, 47.3, 8.2, 49.2)),
        ("Switzerland",     (5.9, 45.8, 10.5, 47.8)),
        ("Austria",         (9.5, 46.4, 17.2, 49.0)),
        ("Czechia",         (12.0, 48.5, 18.9, 51.1)),
        ("Poland",          (14.1, 49.0, 24.2, 54.9)),
        ("North Sea offshore",    (3.0, 53.0, 9.0, 56.0)),
        ("Baltic Sea offshore",   (10.0, 53.5, 15.0, 55.5)),
    ],
    "france": [
        ("Spain (N)",       (-1.8, 42.3, 3.4, 43.8)),
        ("Andorra",         (1.4, 42.4, 1.8, 42.7)),
        ("Italy (NW)",      (6.5, 43.4, 9.1, 46.4)),
        ("Switzerland",     (5.9, 45.8, 10.5, 47.8)),
        ("Germany (W)",     (5.7, 47.3, 8.2, 49.6)),
        ("Luxembourg",      (5.7, 49.4, 6.6, 50.2)),
        ("Belgium",         (2.5, 49.4, 6.5, 51.5)),
        ("UK (S coast)",    (-6.0, 49.9, 1.8, 51.2)),
        ("Monaco",          (7.4, 43.7, 7.44, 43.75)),
        ("Bay of Biscay offshore", (-5.5, 43.5, -1.0, 47.5)),
        ("English Channel offshore", (-4.5, 49.5, 2.0, 51.0)),
        ("Mediterranean offshore", (3.0, 41.0, 9.0, 43.5)),
    ],
    "us": [
        ("Canada (mainland)",     (-141.0, 41.6, -52.6, 60.0)),
        ("Mexico",                (-118.4, 14.5, -86.7, 32.7)),
        ("Cuba",                  (-84.9, 19.8, -74.1, 23.3)),
        ("Bahamas",               (-79.1, 20.9, -72.7, 27.3)),
        ("Bermuda",               (-64.9, 32.2, -64.6, 32.4)),
        ("North Atlantic offshore", (-80.0, 24.0, -60.0, 45.0)),
        ("Gulf of Mexico offshore", (-98.0, 18.0, -80.0, 30.0)),
        ("North Pacific offshore", (-180.0, 30.0, -117.0, 60.0)),
        ("Alaska (main)",         (-179.0, 51.0, -130.0, 71.5)),
        ("Aleutian Islands",      (170.0, 51.0, 180.0, 55.5)),
        ("Hawaii",                (-162.0, 18.5, -154.5, 22.5)),
    ],
    "japan": [
        ("South Korea",     (125.9, 33.1, 129.6, 38.6)),
        ("Russia (Sakhalin/Kuriles)", (140.0, 43.0, 156.7, 54.5)),
        ("Taiwan",          (119.5, 21.5, 122.3, 25.5)),
        ("China (E coast)", (117.0, 30.0, 122.5, 41.0)),
        ("North Korea",     (124.2, 37.5, 130.7, 43.0)),
        ("Sea of Japan offshore", (127.0, 34.0, 141.0, 46.0)),
        ("Philippine Sea offshore", (128.0, 20.0, 142.0, 32.0)),
        ("East China Sea offshore", (122.0, 24.0, 130.0, 34.0)),
        ("Pacific Ocean offshore", (140.0, 22.0, 165.0, 46.0)),
    ],
    "portugal": [
        ("Spain",           (-9.5, 36.0, -0.5, 43.8)),
        ("Atlantic offshore (Iberian)", (-11.0, 36.0, -6.0, 43.5)),
        ("Azores offshore", (-32.0, 36.5, -24.5, 40.0)),
        ("Madeira offshore", (-17.5, 32.0, -16.0, 33.5)),
        ("Morocco (N coast)", (-7.0, 34.5, -1.0, 36.5)),
    ],
    # Additional countries as needed — extendable
}


def load_bounds_polygon(country_slug: str):
    """Load country bounds.json as shapely polygon."""
    from shapely.geometry import shape as shp_shape
    from shapely.geometry import MultiPolygon, Polygon

    bounds_path = REPO_ROOT / country_slug / "bounds.json"
    if not bounds_path.exists():
        raise FileNotFoundError(f"bounds.json not found for {country_slug} at {bounds_path}")

    with open(bounds_path) as f:
        bounds = json.load(f)

    # bounds.json shape varies: sometimes GeoJSON FeatureCollection,
    # sometimes bare Polygon/MultiPolygon geometry
    if bounds.get("type") == "FeatureCollection":
        geoms = []
        for feat in bounds.get("features", []):
            geoms.append(shp_shape(feat["geometry"]))
        if len(geoms) == 1:
            return geoms[0]
        return MultiPolygon([g for g in geoms if isinstance(g, Polygon)])
    elif bounds.get("type") == "Feature":
        return shp_shape(bounds["geometry"])
    elif bounds.get("type") in ("Polygon", "MultiPolygon"):
        return shp_shape(bounds)
    else:
        raise ValueError(f"Unrecognized bounds.json shape for {country_slug}: {bounds.get('type')}")


def load_ssi_data_substations(country_slug: str) -> List[dict]:
    """Load ssi-data.json (handles Convention #79 sharded format)."""
    ssi_path = REPO_ROOT / country_slug / "ssi-data.json"
    with open(ssi_path) as f:
        data = json.load(f)

    # Sharded format check
    if data.get("sharded"):
        subs = []
        for shard_ref in data.get("shards", []):
            shard_path = REPO_ROOT / country_slug / shard_ref["file"]
            with open(shard_path) as f:
                shard = json.load(f)
            subs.extend(shard.get("substations", []))
        return subs

    return data.get("substations", [])


def classify_out_of_polygon(
    lon: float, lat: float, country_slug: str
) -> str:
    """Bucket an out-of-polygon coordinate by neighbor bbox membership."""
    for label, bbox in NEIGHBOR_BBOXES.get(country_slug, []):
        min_lon, min_lat, max_lon, max_lat = bbox
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            return label
    return "UNCLASSIFIED (outside all neighbor bboxes)"


def audit_country(country_slug: str) -> dict:
    """Run out-of-polygon cluster diagnostic for a country."""
    from shapely.geometry import Point

    print(f"[{country_slug}] loading polygon + substations...")

    polygon = load_bounds_polygon(country_slug)
    subs = load_ssi_data_substations(country_slug)
    print(f"[{country_slug}] loaded {len(subs):,} substations")

    if not NEIGHBOR_BBOXES.get(country_slug):
        print(f"[{country_slug}] WARNING: no neighbor bboxes configured; "
              f"all out-of-polygon subs will be UNCLASSIFIED")
        print(f"  → Extend NEIGHBOR_BBOXES dict in this script for empirical clustering")

    n_inside = 0
    n_outside = 0
    n_missing_coords = 0
    cluster_counts: Dict[str, int] = {}
    cluster_samples: Dict[str, List[Tuple[float, float]]] = {}  # first N coords per cluster

    for sub in subs:
        lat = sub.get("latitude") or sub.get("lat")
        lon = sub.get("longitude") or sub.get("lon")
        if lat is None or lon is None:
            n_missing_coords += 1
            continue

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (ValueError, TypeError):
            n_missing_coords += 1
            continue

        pt = Point(lon_f, lat_f)
        if polygon.contains(pt) or polygon.touches(pt):
            n_inside += 1
        else:
            n_outside += 1
            label = classify_out_of_polygon(lon_f, lat_f, country_slug)
            cluster_counts[label] = cluster_counts.get(label, 0) + 1
            samples = cluster_samples.setdefault(label, [])
            if len(samples) < 5:
                samples.append((round(lon_f, 4), round(lat_f, 4)))

    report = {
        "country_slug": country_slug,
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "n_substations_total": len(subs),
        "n_inside_polygon": n_inside,
        "n_outside_polygon": n_outside,
        "n_missing_coords": n_missing_coords,
        "out_of_polygon_pct": (
            round(100.0 * n_outside / (n_inside + n_outside), 2)
            if (n_inside + n_outside) > 0 else 0.0
        ),
        "cluster_distribution": dict(sorted(
            cluster_counts.items(), key=lambda kv: -kv[1]
        )),
        "cluster_samples": cluster_samples,
    }

    return report


def print_report(report: dict) -> None:
    slug = report["country_slug"]
    print()
    print(f"─── {slug} out-of-polygon cluster audit ───")
    print(f"  Total substations           : {report['n_substations_total']:>7,}")
    print(f"  Inside polygon              : {report['n_inside_polygon']:>7,}")
    print(f"  Missing coordinates         : {report['n_missing_coords']:>7,}")
    print(f"  OUT OF POLYGON              : {report['n_outside_polygon']:>7,}  "
          f"({report['out_of_polygon_pct']}%)")
    print()
    print(f"  Cluster distribution (by likely origin):")
    for label, count in report["cluster_distribution"].items():
        samples = report["cluster_samples"].get(label, [])
        sample_str = ", ".join(f"({lo:.2f},{la:.2f})" for lo, la in samples[:3])
        print(f"    {count:>6,}  {label}")
        if samples:
            print(f"              samples: {sample_str}")
    print()


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <country_slug>")
        print(f"       Available: {', '.join(sorted(NEIGHBOR_BBOXES.keys()))}")
        sys.exit(1)

    country_slug = sys.argv[1].lower()

    try:
        report = audit_country(country_slug)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    print_report(report)

    # Write consolidated audit report
    out_path = Path.home() / (
        f"out_of_polygon_audit_{country_slug}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✓ Consolidated audit report: {out_path}")


if __name__ == "__main__":
    main()
