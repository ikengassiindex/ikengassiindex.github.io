"""Minimal ESRI shapefile reader for the NUTS polygon layer.

fiona and geopandas are not installed here, and neither is needed: the NUTS
layer is a single geometry type (polygon, shape type 5) in EPSG:4326, and the
.shp format for that type is a short, well-specified binary layout. Reading it
directly keeps the dependency surface at shapely alone.

Handles shape type 5 (Polygon) and 15/25 (PolygonZ/PolygonM) by ignoring the
trailing Z/M arrays, and skips null shapes (type 0) rather than failing on them.
Ring orientation decides outer vs inner: the shapefile spec makes outer rings
clockwise and holes counter-clockwise, measured by signed area.
"""
from __future__ import annotations

import struct


def _rings(buf, off, n_parts, n_points):
    parts = list(struct.unpack_from(f"<{n_parts}i", buf, off))
    off += 4 * n_parts
    pts = struct.unpack_from(f"<{2 * n_points}d", buf, off)
    off += 16 * n_points
    parts.append(n_points)
    out = []
    for i in range(n_parts):
        a, b = parts[i], parts[i + 1]
        out.append([(pts[2 * j], pts[2 * j + 1]) for j in range(a, b)])
    return out, off


def _signed_area(ring):
    s = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def read_shapes(shp_path):
    """Yield shapely geometries in file order, None for null shapes."""
    from shapely.geometry import Polygon, MultiPolygon

    with open(shp_path, "rb") as f:
        blob = f.read()

    pos = 100                      # main header
    n = len(blob)
    while pos < n:
        _num, clen = struct.unpack_from(">ii", blob, pos)
        pos += 8
        end = pos + clen * 2
        (stype,) = struct.unpack_from("<i", blob, pos)
        if stype == 0:
            yield None
            pos = end
            continue
        if stype not in (5, 15, 25):
            raise ValueError(f"unsupported shape type {stype}")
        off = pos + 4 + 32                       # skip type + bbox
        n_parts, n_points = struct.unpack_from("<ii", blob, off)
        off += 8
        rings, _ = _rings(blob, off, n_parts, n_points)

        outers, holes = [], []
        for r in rings:
            if len(r) < 4:
                continue
            (outers if _signed_area(r) < 0 else holes).append(r)
        # The spec orients outer rings clockwise, which gives a negative signed
        # area under the y-up convention used here. A file that disagrees would
        # otherwise yield zero outers, so fall back rather than drop the shape.
        if not outers:
            outers, holes = holes, []

        polys = []
        for o in outers:
            inner = [h for h in holes if Polygon(o).contains(Polygon(h).representative_point())] \
                if holes else []
            polys.append(Polygon(o, inner))
        yield polys[0] if len(polys) == 1 else MultiPolygon(polys)
        pos = end


def read_dbf(dbf_path, fields=None):
    """Yield dicts of the requested fields, in file order."""
    with open(dbf_path, "rb") as f:
        head = f.read(32)
        nrec, hlen, rlen = struct.unpack("<I H H", head[4:12])
        cols = []
        while True:
            d = f.read(32)
            if d[:1] in (b"\r", b""):
                break
            cols.append((d[0:11].split(b"\x00")[0].decode("latin-1"), d[16]))
        f.seek(hlen)
        want = set(fields) if fields else None
        for _ in range(nrec):
            rec = f.read(rlen)
            if not rec:
                break
            off, row = 1, {}
            for name, ln in cols:
                if want is None or name in want:
                    row[name] = rec[off:off + ln].decode("utf-8", "replace").strip()
                off += ln
            yield row
