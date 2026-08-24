#!/usr/bin/env python3
"""
audit_connectivity.py — what connectivity the estate holds, and what it could
=============================================================================

R4 graph-theoretic criticality is computed from three per-substation fields —
`graph_topology.degree`, `.BC_percentile`, `.is_bridge`. `compute_r4()` in
`scripts/pipeline/scoring/engine.py` consumes exactly those three and nothing
else. So it is worth knowing where they come from.

They do not come from the estate's own connectivity. In a 34,144-substation
French sample, 30,658 substations are absent from the adjacency graph in
`grid-geo.json` yet carry a non-zero `degree`; of the 3,424 that are present,
47 have a degree matching their real neighbour count and 3,377 do not. Every
one of the 34,144 carries `_synthetic_graph_topology_retired`, pointing at
`enrich_esg_gaps.py:377 vary(0.015, name, 0.40)`. The generator was retired.
Its output was not.

Meanwhile connectivity *is* held, in two places, and neither is read by
scoring:

  1. `grid-geo.json::a` — an adjacency list keyed by `substation_id`.
  2. `grid-geo.json::l[].ss/se` — line endpoint indices into `::s`.

Both are partial and they cover different countries. This tool measures both,
then asks a third question: how much connectivity could be *reconstructed*
from the line geometry the estate already holds, for the countries where
neither representation is populated.

The reconstruction is the interesting part. Naively matching a line's first
and last coordinate to a nearby substation recovers very little — 3-36% —
because OSM splits power lines into way segments that meet at pylons, not at
substations. Welding the segments into a conductor graph and then contracting
every run of non-substation nodes into a hyper-edge between the substations it
touches does far better: on Greece it connects 86% of substations at a mean
degree of 3.5, against the synthetic values' uniform degree of 4-6 and their
`is_bridge = 0` for every substation in the country.

This tool only measures. It writes nothing into any canonical: replacing R4's
inputs is a Class M change and belongs in its own reviewed pass, not in an
audit.

Usage:
    python3 scripts/audit_connectivity.py --all
    python3 scripts/audit_connectivity.py greece chile --recover
    python3 scripts/audit_connectivity.py --all --json connectivity.json
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SNAP = 6            # coordinate rounding used to weld touching segment ends
TOL_M = 300.0       # substation-to-conductor snap distance
FANOUT = 8          # cap on pairs emitted per conductor group (see below)


def _load(slug):
    p = REPO / slug / "grid-geo.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _sub_ids(slug):
    """substation_id set, transparently across Convention #79 shards."""
    p = REPO / slug / "ssi-data.json"
    if not p.exists():
        return set(), 0
    d = json.loads(p.read_text(encoding="utf-8"))
    parts = []
    if isinstance(d.get("substations"), list):
        parts.append(d["substations"])
    else:
        for sh in d.get("substations_shards") or []:
            q = sh["path"] if isinstance(sh, dict) else sh
            parts.append(json.loads((REPO / slug / Path(q).name).read_text(encoding="utf-8")))
    ids, n = set(), 0
    for part in parts:
        for s in part:
            n += 1
            v = s.get("substation_id")
            if v is not None:
                ids.add(str(v))
    return ids, n


def _components(adj):
    seen, comps = set(), []
    for k in adj:
        if k in seen:
            continue
        stack, size = [k], 0
        seen.add(k)
        while stack:
            u = stack.pop()
            size += 1
            for w in adj.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        comps.append(size)
    comps.sort(reverse=True)
    return comps


def held(slug):
    """What connectivity the country actually stores today."""
    g = _load(slug)
    if not g:
        return {"slug": slug, "grid_geo": False}
    S, L = g.get("s") or {}, g.get("l") or []
    A = {str(k): [str(x) for x in v] for k, v in (g.get("a") or {}).items()}
    ids, n_subs = _sub_ids(slug)

    endpoints_ok = 0
    for e in L:
        a, b = e.get("ss"), e.get("se")
        if isinstance(a, int) and isinstance(b, int) and 0 <= a < len(S) and 0 <= b < len(S) and a != b:
            endpoints_ok += 1

    comps = _components(A)
    nodes = sum(comps)
    return {
        "slug": slug, "grid_geo": True,
        "substations": n_subs, "graph_nodes_s": len(S), "lines": len(L),
        "endpoints_resolvable": endpoints_ok,
        "endpoints_pct": 100 * endpoints_ok / max(len(L), 1),
        "adjacency_keys": len(A),
        "adjacency_joins_substation_id": len(set(A) & ids),
        "adjacency_join_pct": 100 * len(set(A) & ids) / max(len(A), 1),
        "adjacency_nodes": nodes,
        "adjacency_components": len(comps),
        "adjacency_largest_pct": 100 * (comps[0] if comps else 0) / max(nodes, 1),
    }


def recover(slug):
    """Reconstruct substation adjacency from the line geometry.

    Segments are welded at shared coordinates into a conductor graph;
    substations are snapped onto it; then every connected run of
    non-substation nodes is contracted into a group, and the substations that
    group touches are recorded as mutually connected.

    FANOUT caps how many pairs a single group emits. A long distribution
    conductor can touch hundreds of substations, and emitting the full clique
    would both explode the edge count and overstate adjacency — being on the
    same feeder is not the same as being neighbours. The cap keeps the result
    a lower bound, which is the right direction for an audit.
    """
    g = _load(slug)
    if not g:
        return {"slug": slug, "grid_geo": False}
    S = g.get("s") or {}
    L = [e for e in (g.get("l") or []) if e.get("p") and len(e["p"]) >= 2]
    if not S or not L:
        return {"slug": slug, "recoverable": False, "reason": "no lines or no nodes"}

    def key(p):
        return (round(p[0], SNAP), round(p[1], SNAP))

    adj = collections.defaultdict(set)
    for e in L:
        pts = [key(q) for q in e["p"]]
        for u, v in zip(pts, pts[1:]):
            if u != v:
                adj[u].add(v)
                adj[v].add(u)

    bucket = collections.defaultdict(list)
    for p in adj:
        bucket[(round(p[0], 2), round(p[1], 2))].append(p)

    def snap(x, y):
        best, bd = None, 1e9
        for dx in (-0.01, 0, 0.01):
            for dy in (-0.01, 0, 0.01):
                for p in bucket.get((round(x + dx, 2), round(y + dy, 2)), ()):
                    d = math.hypot((p[0] - x) * 111320 * math.cos(math.radians(y)),
                                   (p[1] - y) * 110540)
                    if d < bd:
                        bd, best = d, p
        return best if bd <= TOL_M else None

    at = {}
    for sid, v in S.items():
        try:
            p = snap(float(v["x"]), float(v["y"]))
        except (KeyError, TypeError, ValueError):
            continue
        if p is not None:
            at.setdefault(p, sid)

    seen, edges = set(), set()
    for n in adj:
        if n in seen or n in at:
            continue
        stack, touch = [n], set()
        seen.add(n)
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w in at:
                    touch.add(at[w])
                elif w not in seen:
                    seen.add(w)
                    stack.append(w)
        if len(touch) >= 2:
            t = sorted(touch)
            for i in range(len(t)):
                for j in range(i + 1, min(i + FANOUT, len(t))):
                    edges.add((t[i], t[j]))

    deg = collections.Counter()
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    radj = collections.defaultdict(set)
    for a, b in edges:
        radj[a].add(b)
        radj[b].add(a)
    comps = _components(radj)
    return {
        "slug": slug, "recoverable": True,
        "substations": len(S),
        "snapped_to_network": len(at),
        "snapped_pct": 100 * len(at) / max(len(S), 1),
        "recovered_edges": len(edges),
        "connected_substations": len(deg),
        "connected_pct": 100 * len(deg) / max(len(S), 1),
        "mean_degree": sum(deg.values()) / max(len(deg), 1),
        "components": len(comps),
        "largest_component_pct": 100 * (comps[0] if comps else 0) / max(sum(comps), 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("countries", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--recover", action="store_true",
                    help="also attempt reconstruction from line geometry (slower)")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    slugs = a.countries
    if a.all or not slugs:
        slugs = sorted(json.loads(
            (REPO / "intelligence" / "countries.json").read_text(encoding="utf-8"))["slugs"])

    print(f"{'country':<13}{'subs':>8}{'geo-nodes':>10}{'a-keys':>8}{'join%':>7}"
          f"{'ss/se%':>8}{'connected now':>14}"
          + ("   reconstructed (of geo-nodes)" if a.recover else ""))
    out = []
    for s in slugs:
        h = held(s)
        if not h.get("grid_geo"):
            print(f"{s:<13}   no grid-geo.json")
            continue
        now = h["adjacency_joins_substation_id"]
        line = (f"{s:<13}{h['substations']:>8,}{h['graph_nodes_s']:>10,}"
                f"{h['adjacency_keys']:>8,}{h['adjacency_join_pct']:>6.0f}%"
                f"{h['endpoints_pct']:>7.0f}%"
                f"{now:>10,} ({100 * now / max(h['substations'], 1):>3.0f}%)")
        rec = None
        if a.recover:
            rec = recover(s)
            if rec.get("recoverable"):
                line += (f"   {rec['connected_substations']:>7,} "
                         f"({rec['connected_pct']:>3.0f}%) deg {rec['mean_degree']:.1f}")
            else:
                line += "   —"
        print(line)
        out.append({"held": h, "recovered": rec})

    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
