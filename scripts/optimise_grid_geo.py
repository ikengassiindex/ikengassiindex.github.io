#!/usr/bin/env python3
"""
SSI Index — grid-geo.json coordinate optimiser.

Reduces file size via two independent passes:
  1. Coordinate precision rounding — round to N decimals (default 5 ≈ 1.1m
     precision at the equator, plenty for grid-geo display purposes).
     Norway's raw output is 6-decimal (~11 cm precision), which is overkill
     for a visualization layer.  Rounding to 5 decimals typically shaves
     10-15% off compact JSON size.
  2. Douglas-Peucker polyline simplification — for lines with >20 vertices,
     apply the Ramer-Douglas-Peucker algorithm at ~25m tolerance to drop
     redundant intermediate vertices while preserving the shape.  Norway has
     6,248 lines with >20 vertices (4% of total) but they represent a
     disproportionate share of bytes because bytes-per-line ≈ 15 × vertices.

Trigger: task #157 — Norway grid-geo.json was 60.9 MB, approaching the 90 MB
sentinel threshold.  After this pass, expected size ~40-45 MB (25-35% reduction).

Usage:
    python3 scripts/optimise_grid_geo.py norway
    python3 scripts/optimise_grid_geo.py norway --dry-run
    python3 scripts/optimise_grid_geo.py norway --precision 5 --dp-tolerance-m 25
    python3 scripts/optimise_grid_geo.py --all         # all 39 countries
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres."""
    R = 6_371_000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def point_to_line_distance_m(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float,
) -> float:
    """Approximate perpendicular distance from point P to segment AB (metres).

    Uses local flat-earth approximation via equirectangular projection.  Fine
    for small distances (grid-geo lines are typically <100 km each).
    """
    # Convert to metres using local scaling at the segment's midpoint latitude
    lat_ref = (a_lat + b_lat) / 2
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat_ref))
    ax = a_lon * m_per_deg_lon; ay = a_lat * m_per_deg_lat
    bx = b_lon * m_per_deg_lon; by = b_lat * m_per_deg_lat
    px = p_lon * m_per_deg_lon; py = p_lat * m_per_deg_lat
    dx = bx - ax; dy = by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 1e-9:
        # A == B, return distance to A
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    nearest_x = ax + t * dx
    nearest_y = ay + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)


def douglas_peucker(points: list[list[float]], tolerance_m: float) -> list[list[float]]:
    """Ramer-Douglas-Peucker polyline simplification.

    points: list of [lon, lat] pairs.
    tolerance_m: max perpendicular distance from simplified line to original
                 point, in metres.  Points within tolerance are dropped.
    """
    if len(points) < 3:
        return points[:]

    # Find point with max distance from segment[first, last]
    p0 = points[0]
    pn = points[-1]
    max_d = 0.0
    max_idx = 0
    for i in range(1, len(points) - 1):
        p = points[i]
        d = point_to_line_distance_m(p[1], p[0], p0[1], p0[0], pn[1], pn[0])
        if d > max_d:
            max_d = d
            max_idx = i

    if max_d > tolerance_m:
        # Recurse on both halves
        left = douglas_peucker(points[:max_idx + 1], tolerance_m)
        right = douglas_peucker(points[max_idx:], tolerance_m)
        # Concat, dropping duplicate midpoint
        return left[:-1] + right
    else:
        # All intermediate points within tolerance — return endpoints only
        return [p0, pn]


def optimise_polyline(
    pts: list[list[float]],
    precision: int,
    dp_tolerance_m: float,
    long_line_threshold: int,
) -> list[list[float]]:
    """Apply precision rounding + DP simplification (if long enough)."""
    # Simplify long polylines first — cheaper than rounding then simplifying
    if len(pts) > long_line_threshold and dp_tolerance_m > 0:
        pts = douglas_peucker(pts, dp_tolerance_m)
    # Round to precision
    return [[round(p[0], precision), round(p[1], precision)] for p in pts]


def optimise_country(
    country: str,
    repo_root: Path,
    precision: int,
    dp_tolerance_m: float,
    long_line_threshold: int,
    dry_run: bool,
) -> dict:
    """Run the optimisation on a single country's grid-geo.json.

    Returns stats dict for reporting.
    """
    fp = repo_root / country / 'grid-geo.json'
    if not fp.exists():
        return {'country': country, 'skipped': 'no grid-geo.json'}

    original_size = fp.stat().st_size
    data = json.loads(fp.read_text())
    lines = data.get('l', [])

    original_vertices = sum(len(ln.get('p', [])) for ln in lines)
    simplified_line_count = 0

    for ln in lines:
        pts = ln.get('p')
        if not pts or len(pts) < 2:
            continue
        original_len = len(pts)
        new_pts = optimise_polyline(pts, precision, dp_tolerance_m, long_line_threshold)
        ln['p'] = new_pts
        if len(new_pts) < original_len:
            simplified_line_count += 1

    final_vertices = sum(len(ln.get('p', [])) for ln in lines)

    if dry_run:
        # Serialise to estimate output size
        new_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        final_size = len(new_bytes)
    else:
        fp.write_text(json.dumps(data, ensure_ascii=False))
        final_size = fp.stat().st_size

    return {
        'country': country,
        'lines': len(lines),
        'simplified_lines': simplified_line_count,
        'vertices_before': original_vertices,
        'vertices_after': final_vertices,
        'vertex_reduction_pct': round(100 * (1 - final_vertices / max(original_vertices, 1)), 1),
        'size_before_mb': round(original_size / (1024 * 1024), 2),
        'size_after_mb': round(final_size / (1024 * 1024), 2),
        'size_reduction_pct': round(100 * (1 - final_size / max(original_size, 1)), 1),
        'dry_run': dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('country', nargs='?', help='Country slug (e.g. norway)')
    parser.add_argument('--all', action='store_true', help='Process all 39 countries')
    parser.add_argument('--precision', type=int, default=5,
                        help='Coordinate decimal places (default 5 = ~1.1m precision)')
    parser.add_argument('--dp-tolerance-m', type=float, default=25.0,
                        help='Douglas-Peucker tolerance in metres (default 25m; 0 = disable)')
    parser.add_argument('--long-line-threshold', type=int, default=20,
                        help='Apply DP only to polylines with more than N vertices')
    parser.add_argument('--dry-run', action='store_true', help='Estimate reduction without writing')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    args = parser.parse_args()

    if not args.country and not args.all:
        parser.error('Specify a country slug or --all')

    if args.all:
        countries = sorted(
            d.name for d in args.repo_root.iterdir()
            if d.is_dir() and not d.name.startswith('.') and (d / 'grid-geo.json').exists()
        )
    else:
        countries = [args.country]

    print(f'grid-geo.json optimiser  ·  precision={args.precision}  ·  DP tolerance={args.dp_tolerance_m}m'
          f'  ·  long-line threshold={args.long_line_threshold} vertices  ·  {"DRY RUN" if args.dry_run else "WRITE"}')
    print()

    total_before = total_after = 0
    for country in countries:
        stats = optimise_country(
            country, args.repo_root.resolve(),
            args.precision, args.dp_tolerance_m, args.long_line_threshold,
            args.dry_run,
        )
        if 'skipped' in stats:
            continue
        total_before += stats['size_before_mb']
        total_after += stats['size_after_mb']
        print(f'  {country:15s}  '
              f'{stats["size_before_mb"]:>6.1f} MB → {stats["size_after_mb"]:>6.1f} MB  '
              f'({stats["size_reduction_pct"]:+.1f}% size, '
              f'{stats["vertex_reduction_pct"]:+.1f}% vertices, '
              f'{stats["simplified_lines"]:,} lines simplified)')

    print()
    print(f'  TOTAL           {total_before:>6.1f} MB → {total_after:>6.1f} MB'
          f'  ({100 * (1 - total_after / max(total_before, 1)):+.1f}% total)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
