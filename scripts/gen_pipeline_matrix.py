#!/usr/bin/env python3
"""Generate the pipeline matrix: 39 countries x ingestion -> scoring -> enrichment.

GENERATED, NOT WRITTEN. Rebuild with:
    for c in <countries>; do python3 scripts/pipeline_matrix_probe.py $c > /tmp/matrix/$c.json; done
    python3 scripts/gen_pipeline_matrix.py /tmp/matrix

DESIGN, and why it is this shape
────────────────────────────────
1. **Generated.** A hand-typed matrix is stale the day someone adds a fetcher.
   This estate has already paid for one stale authority.
2. **Assertion-shaped.** Every cell is a fact a sentinel could enforce, not a
   judgement. The matrix is therefore also a backlog of gates.
3. **Divergence is the signal, not quality.** Cells are scored by distance from
   the cohort MODE, because on 20 August 2026 ranking merge modules by code
   similarity alone put all eight defective countries in the top eight — before
   anyone looked at the data. Divergence has high recall for defect.

Rows are per-country because divergence is per-country. A fleet-weight column
is carried so coverage can be read either way without re-running: france,
germany and us alone are ~60% of the substations, and an unweighted read treats
greenland's 43 records as equal to france's 175,660.
"""
import sys, json, pathlib, collections, difflib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/matrix")
rows = [json.loads(p.read_text()) for p in sorted(SRC.glob("*.json")) if p.stat().st_size]
rows.sort(key=lambda r: -r["scoring"]["fleet"])
total_fleet = sum(r["scoring"]["fleet"] for r in rows)

# ── code divergence: similarity of each ingestion module to the cohort template
def similarity(fname):
    d = ROOT / "scripts" / "pipeline" / "ingestion"
    texts = {f.parent.name: f.read_text(encoding="utf-8", errors="replace").splitlines()
             for f in sorted(d.glob(f"*/{fname}"))}
    if not texts:
        return {}
    # reference = the module closest to the median length (the de facto template)
    med = sorted(len(v) for v in texts.values())[len(texts) // 2]
    ref_name = min(texts, key=lambda k: abs(len(texts[k]) - med))
    ref = texts[ref_name]
    return {k: difflib.SequenceMatcher(None, ref, v).quick_ratio() for k, v in texts.items()}

sim_merge = similarity("merge_into_ssi_data.py")
sim_osm = similarity("osm_overpass.py")

# ── cohort mode per categorical cell ───────────────────────────────────
def mode(path):
    vals = []
    for r in rows:
        v = r
        for k in path:
            v = (v or {}).get(k)
        vals.append(v)
    c = collections.Counter(v for v in vals if v is not None)
    return c.most_common(1)[0][0] if c else None

#: Where a NORMATIVE target is knowable, divergence is measured against it, not
#: against the cohort mode. This distinction is not cosmetic — see below.
#:
#: THE FLAW THIS FIXES. Naive mode-based divergence assumes the majority is
#: healthy. Measured on 20 August 2026 it is not, in three of five dimensions:
#:
#:   grid_geo.id_join   none 15 · exact 14 · prefix_only 10  -> modal value is
#:                      the BROKEN state, and italy (the one country whose
#:                      grid-geo joins exactly) was flagged as the outlier
#:   meta.version       4.0.2 25 · none 13 · v4.0.2 1        -> modal value is
#:                      stale; the live methodology version is 4.24
#:   pipeline_class     digital-twin 22 · none 10 · score-country 7
#:                      -> NO valid target exists: digital-twin is archived with
#:                      no producing code, score-country generates every
#:                      component from MD5 jitter, none is unrecorded (M-066)
#:
#: "Most countries do X" is evidence about the estate, not about correctness.
#: Reporting only mode-divergence would have penalised the one country that was
#: right — which is how a screen becomes a liability.
TARGETS = {
    "meta_version": {"value": "4.24",
                     "why": "register §5.5 — live methodology version; per-country meta.version "
                            "is stale in all 39 and bumps at the next cohort rescore"},
    "id_join": {"value": "exact",
                "why": "grid-geo must join the fleet by substation_id for I4 line-density to be "
                       "computable; 14 countries achieve it, so it is reachable"},
    "band_normalised": {"value": True,
                        "why": "Task #461 applies cohort-wide; greece was the sole exception"},
}
#: Cells where no defensible target exists — the absence is itself the finding.
NO_VALID_TARGET = {
    "pipeline_class": "all three observed values are unsatisfactory: digital-twin is archived "
                      "with no producing code, scripts/score-country.py generates every "
                      "component from MD5 jitter, and null is unrecorded provenance (M-066)",
}

MODAL = {
    "pipeline_class": mode(["provenance", "pipeline_class"]),
    "regen_method": mode(["provenance", "regen_method"]),
    "meta_version": mode(["provenance", "meta_version"]),
    "id_join": mode(["grid_geo", "id_join"]),
    "band_normalised": mode(["scoring", "band_normalised"]),
}

def divergence(r):
    """Cells where this country differs from its TARGET (or from the mode where
    no target is knowable). Never from a mode that is itself a known defect."""
    d = []
    # pipeline_class: no valid target — every country is reported, none singled out
    if r["provenance"]["regen_method"] != MODAL["regen_method"]:
        d.append("regen_method")
    if r["provenance"]["meta_version"] != TARGETS["meta_version"]["value"]:
        d.append("meta_version")
    if r["grid_geo"].get("id_join") != TARGETS["id_join"]["value"]:
        d.append("grid_geo_id_join")
    if r["scoring"]["band_normalised"] != TARGETS["band_normalised"]["value"]:
        d.append("band_normalised")
    if sim_merge.get(r["country"], 1.0) < 0.5:
        d.append("merge_module")
    if sim_osm.get(r["country"], 1.0) < 0.5:
        d.append("osm_module")
    if r["scoring"]["unclassified_pct"] == 100.0:
        d.append("fully_unclassified")
    if not r["ingestion"]["era5_cache"]:
        d.append("no_era5_cache")
    return d

for r in rows:
    r["_divergence"] = divergence(r)

out = []
w = out.append
w("# SSI Index — Pipeline Matrix")
w("")
w("**v1.0 · 20 August 2026 · 39 countries × ingestion → scoring → enrichment**")
w("")
w("**GENERATED, NOT HAND-WRITTEN.** `scripts/pipeline_matrix_probe.py` (per country) +")
w("`scripts/gen_pipeline_matrix.py` (aggregate). Regenerate in the same commit as any pipeline")
w("change. Every cell is a fact a sentinel could enforce, not a judgement — so this document is")
w("also the backlog of gates that do not yet exist.")
w("")
w("**Divergence is the signal, not quality.** Cells are measured as distance from the cohort")
w("*mode*. On 20 August 2026, ranking ingestion modules by code similarity alone put all eight")
w("defective countries in the top eight, before anyone looked at the data. Divergence has high")
w("recall for defect; it is a screen, not a verdict.")
w("")
w(f"**Cohort mode:** pipeline `{MODAL['pipeline_class']}` · regen `{MODAL['regen_method']}` · "
  f"meta.version `{MODAL['meta_version']}` · grid-geo join `{MODAL['id_join']}` · "
  f"band-normalised `{MODAL['band_normalised']}`")
w("")
w("---")
w("")
w("## 0. Where the cohort mode is itself the defect")
w("")
w("**Read this before the ranking.** Naive mode-based divergence assumes the majority is healthy.")
w("It is not, in three of five measured dimensions — so divergence here is measured against a")
w("**target** where one is knowable, and the mode is reported only as description.")
w("")
w("| Cell | Observed distribution | Target | Why |")
w("|---|---|---|---|")
for key, path in (("meta_version", ["provenance", "meta_version"]),
                  ("id_join", ["grid_geo", "id_join"]),
                  ("band_normalised", ["scoring", "band_normalised"])):
    dist = collections.Counter()
    for r in rows:
        v = r
        for k in path:
            v = (v or {}).get(k)
        dist[str(v)] += 1
    tgt = TARGETS[key]
    off = sum(v for k, v in dist.items() if k != str(tgt["value"]))
    w(f"| `{key}` | {' · '.join(f'{k} {v}' for k, v in dist.most_common())} | "
      f"**{tgt['value']}** ({off} countries off target) | {tgt['why']} |")
for key, why in NO_VALID_TARGET.items():
    dist = collections.Counter(str(r["provenance"].get(key)) for r in rows)
    w(f"| `{key}` | {' · '.join(f'{k} {v}' for k, v in dist.most_common())} | "
      f"**none exists** | {why} |")
w("")
w("The clearest instance: **italy is the only country whose grid-geo joins the fleet exactly,**")
w("and a mode-based screen flagged it as the outlier for it. A screen that penalises the one")
w("country that is right is worse than no screen.")
w("")
w("## 1. Divergence ranking")
w("")
w("Cells differing from **target** (§0), or from the cohort mode where no target is knowable.")
w("")
w("| Country | Fleet | % of cohort | Divergent cells | Which |")
w("|---|---:|---:|---:|---|")
for r in sorted(rows, key=lambda r: (-len(r["_divergence"]), -r["scoring"]["fleet"])):
    d = r["_divergence"]
    if not d:
        continue
    share = 100 * r["scoring"]["fleet"] / total_fleet
    w(f"| **{r['country']}** | {r['scoring']['fleet']:,} | {share:.1f}% | **{len(d)}** | "
      f"{', '.join(f'`{x}`' for x in d)} |")
clean = [r["country"] for r in rows if not r["_divergence"]]
w("")
w(f"**{len(clean)} countries match the cohort mode on every measured cell:** "
  f"{', '.join(clean) if clean else '—'}")
w("")
w("## 2. Ingestion")
w("")
w("| Country | Fleet | ERA5 | seismic cache | socio cache | committed CSV | grid-geo | lines | ID join |")
w("|---|---:|:-:|:-:|:-:|:-:|:-:|---:|---|")
tick = lambda b: "✅" if b else "—"
for r in rows:
    g = r["grid_geo"]
    lines = (g.get("lines_inline") or 0) + (g.get("line_shards") or 0) * 1
    lines_s = (f"{g.get('lines_inline'):,}" if g.get("lines_inline")
               else (f"{g.get('line_shards')} shards" if g.get("line_shards") else "—"))
    w(f"| {r['country']} | {r['scoring']['fleet']:,} | {tick(r['ingestion']['era5_cache'])} | "
      f"{tick(r['ingestion']['seismic_cache'])} | {tick(r['ingestion']['socio_cache'])} | "
      f"{tick(r['ingestion']['seismic_committed_csv'])} | {tick(g.get('present'))} | {lines_s} | "
      f"`{g.get('id_join') or '—'}` |")
w("")
w("## 3. Provenance and code")
w("")
w("| Country | Pipeline class | regen_method | meta.version | merge sim | osm sim |")
w("|---|---|---|---|---:|---:|")
for r in rows:
    p = r["provenance"]
    ms = sim_merge.get(r["country"]); os_ = sim_osm.get(r["country"])
    w(f"| {r['country']} | {p['pipeline_class'] or '**none**'} | {p['regen_method'] or '**none**'} | "
      f"{p['meta_version'] or '**none**'} | {f'{ms:.0%}' if ms is not None else '—'} | "
      f"{f'{os_:.0%}' if os_ is not None else '—'} |")
w("")
w("## 4. Scoring")
w("")
w("| Country | Fleet | Scored | Unclassified % | Components % | Normalised | `_band_absolute` |")
w("|---|---:|---:|---:|---:|:-:|:-:|")
for r in rows:
    s = r["scoring"]
    w(f"| {r['country']} | {s['fleet']:,} | {s['scored']:,} | {s['unclassified_pct']}% | "
      f"{s['with_components_pct']}% | {tick(s['band_normalised'])} | "
      f"{'✅' if s['band_absolute_consistent'] else '⚠️ ' + str(s['band_absolute_missing'])} |")
w("")
w("## 5. Enrichment")
w("")
w("| Country | socio | seismic | climate | graph | modifiers | R7v2 | voltage | metrics | retired | recovered | no region |")
w("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for r in rows:
    e = r["enrichment"]
    w(f"| {r['country']} | {e['socio_pct']}% | {e['seismic_pct']}% | {e['climate_pct']}% | "
      f"{e['graph_topology_pct']}% | {e['modifiers_pct']}% | {e['r7_cyber_v2_pct']}% | "
      f"{e['voltage_pct']}% | {e['metrics_built_pct']}% | {e['synthetic_retired']:,} | "
      f"{e['components_recovered']:,} | {e['region_missing']:,} |")
w("")
w("## 6. Cohort totals — unweighted and fleet-weighted")
w("")
def wavg(fn):
    num = sum(fn(r) * r["scoring"]["fleet"] for r in rows if fn(r) is not None)
    den = sum(r["scoring"]["fleet"] for r in rows if fn(r) is not None)
    return num / den if den else 0
def uavg(fn):
    vals = [fn(r) for r in rows if fn(r) is not None]
    return sum(vals) / len(vals) if vals else 0
w("| Measure | Unweighted (per country) | Fleet-weighted |")
w("|---|---:|---:|")
for label, fn in (
    ("Unclassified %", lambda r: r["scoring"]["unclassified_pct"]),
    ("With components %", lambda r: r["scoring"]["with_components_pct"]),
    ("socio_economic %", lambda r: r["enrichment"]["socio_pct"]),
    ("seismic %", lambda r: r["enrichment"]["seismic_pct"]),
    ("graph_topology %", lambda r: r["enrichment"]["graph_topology_pct"]),
    ("R7_cyber_v2 %", lambda r: r["enrichment"]["r7_cyber_v2_pct"]),
    ("metrics built %", lambda r: r["enrichment"]["metrics_built_pct"]),
):
    w(f"| {label} | {uavg(fn):.1f}% | {wavg(fn):.1f}% |")
w("")
w(f"Fleet **{total_fleet:,}** across **{len(rows)}** countries. The three largest "
  f"({', '.join(r['country'] for r in rows[:3])}) are "
  f"{100*sum(r['scoring']['fleet'] for r in rows[:3])/total_fleet:.0f}% of it — which is why both "
  f"columns are shown. Where they disagree, the unweighted number describes the estate's "
  f"*consistency* and the weighted one describes the *index*.")
w("")
w("---")
w("")
w("*Companion: `SSI_DATA_SOURCE_RECORD.md` · `SSI_INGESTION_ARCHITECTURE_AUDIT_20260820.md` ·")
w("`SSI_DOCUMENT_PRECEDENCE_REGISTER.md`.*")

print("\n".join(out))
