#!/usr/bin/env python3
"""Per-country probe for the pipeline matrix. Emits one JSON row on stdout.

Run per country in a subprocess: a single process holding all 39 countries'
substations is an OOM (france alone is 175,660 records, us 97,915).

Every field here is chosen to be ASSERTION-SHAPED — a fact a sentinel could
later enforce — rather than a judgement. "seismic_tier: 2" not "seismic: ok".
The matrix grades nothing; the aggregator measures distance from the cohort
mode, because today's evidence is that divergence predicts defect.
"""
import sys, json, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tests._ssi_test_support import load_ssi_data
from scripts.pipeline.scoring.engine import classify_band, compute_r_base

ROOT = Path(__file__).resolve().parent.parent
c = sys.argv[1]
row = {"country": c}

manifest = json.loads((ROOT / c / "ssi-data.json").read_text(encoding="utf-8"))
meta = manifest.get("meta") or {}
fs = manifest.get("fleet_summary") or {}

# ── STAGE: code ────────────────────────────────────────────────────────
ing = ROOT / "scripts" / "pipeline" / "ingestion" / c.replace("-", "_")
row["code"] = {
    "ingestion_pkg": ing.name if ing.exists() else None,
    "has_osm_module": (ing / "osm_overpass.py").exists(),
    "has_merge_module": (ing / "merge_into_ssi_data.py").exists(),
    "has_base_module": (ing / "_base.py").exists(),
}

# ── STAGE: provenance ──────────────────────────────────────────────────
pipeline = meta.get("scoring_pipeline")
row["provenance"] = {
    "scoring_pipeline": pipeline,
    "pipeline_class": ("digital-twin" if pipeline and pipeline.startswith("digital-twin-")
                       else "score-country" if pipeline else None),
    "regen_method": meta.get("regen_method"),
    "meta_version": meta.get("version"),
}

# ── STAGE: ingestion caches ────────────────────────────────────────────
cache = ROOT / "scripts" / "pipeline" / ".cache"
row["ingestion"] = {
    "era5_cache": (cache / f"era5_baseline_{c}.json").exists(),
    "seismic_cache": (cache / f"seismic_{c}.json").exists(),
    "socio_cache": (cache / f"socioeconomic_{c}.json").exists(),
    "seismic_committed_csv": bool(list((ROOT / "scripts" / "pipeline" / "data" / c).glob("*.csv"))
                                  if (ROOT / "scripts" / "pipeline" / "data" / c).exists() else []),
}

# ── STAGE: grid geometry ───────────────────────────────────────────────
gg = ROOT / c / "grid-geo.json"
ggd = {}
if gg.exists():
    g = json.loads(gg.read_text(encoding="utf-8"))
    gsubs = g.get("s") or {}
    ggd = {
        "present": True,
        "sharded": bool(g.get("sharded")),
        "n_substations": len(gsubs) if isinstance(gsubs, dict) else None,
        "lines_inline": len(g.get("l") or []),
        "line_shards": len(list((ROOT / c).glob("grid-geo-l-*.json"))),
    }
else:
    ggd = {"present": False}
row["grid_geo"] = ggd

# ── data pass ──────────────────────────────────────────────────────────
doc = load_ssi_data(c, ROOT)
subs = doc.get("substations") or []
n = len(subs)

scored = comp = metrics = retired = recovered = 0
graph = mods = socio = seismic = climate = volt = 0
band_abs_ok = band_abs_missing = 0
r7v2 = 0
region_none = 0
for s in subs:
    if s.get("R_median") is not None:
        scored += 1
        ba = s.get("_band_absolute")
        if ba is None:
            band_abs_missing += 1
        elif ba == classify_band(s["R_median"]):
            band_abs_ok += 1
    if s.get("components"): comp += 1
    if s.get("metrics"): metrics += 1
    if s.get("_synthetic_components_retired"): retired += 1
    if s.get("_components_recovered"): recovered += 1
    if s.get("graph_topology"): graph += 1
    m = s.get("modifiers") or {}
    if m: mods += 1
    if "R7_cyber_v2" in m: r7v2 += 1
    if s.get("socio_economic"): socio += 1
    if s.get("seismic"): seismic += 1
    if s.get("climate_trajectory"): climate += 1
    if s.get("voltage_kv") is not None: volt += 1
    if not s.get("region"): region_none += 1

# grid-geo ID joinability — the divergence found on 20 Aug
join = None
if ggd.get("present") and ggd.get("n_substations"):
    g = json.loads(gg.read_text(encoding="utf-8"))
    gids = set(map(str, (g.get("s") or {}).keys()))
    fids = {str(s.get("substation_id")) for s in subs}
    exact = len(gids & fids)
    if exact:
        join = "exact" if exact >= 0.9 * min(len(gids), len(fids)) else "partial"
    else:
        stripped = {i.split("_", 1)[-1] for i in fids}
        join = "prefix_only" if len(gids & stripped) else "none"
row["grid_geo"]["id_join"] = join

pct = lambda x: round(100 * x / n, 1) if n else None
row["scoring"] = {
    "fleet": n, "scored": scored, "unclassified_pct": pct(n - scored),
    "with_components_pct": pct(comp),
    "band_normalised": bool((fs.get("_band_normalisation") or {}).get("applied")),
    "band_absolute_missing": band_abs_missing,
    "band_absolute_consistent": band_abs_ok == scored and band_abs_missing == 0,
}
row["enrichment"] = {
    "socio_pct": pct(socio), "seismic_pct": pct(seismic), "climate_pct": pct(climate),
    "graph_topology_pct": pct(graph), "modifiers_pct": pct(mods),
    "r7_cyber_v2_pct": pct(r7v2), "voltage_pct": pct(volt),
    "metrics_built_pct": pct(metrics),
    "synthetic_retired": retired, "components_recovered": recovered,
    "region_missing": region_none,
}
print(json.dumps(row))
