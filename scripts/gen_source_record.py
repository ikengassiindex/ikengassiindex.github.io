"""Generate the Tree-4 data-source record FROM the code registries.

Written as a generator rather than a hand-authored document on purpose: a
source record that is typed by hand drifts from the pipeline the moment
anyone adds a fetcher, and a stale source-of-record is the failure the
precedence register exists to prevent (§7.2). Re-run this after any ingestion
change; the same-commit rule applies.
"""
import sys, json, pathlib, collections
sys.path.insert(0, ".")
from scripts.pipeline.ingestion.components import METRIC_REGISTRY, implemented_metrics, blocked_metrics
from scripts.pipeline.ingestion.continuity import CONTINUITY_SOURCES, UNRESEARCHED, coverage_report
from scripts.pipeline.scoring.engine import COMPONENT_WEIGHTS, INTRA_WEIGHTS

ROOT = pathlib.Path(".")
countries = sorted(p.parent.name for p in ROOT.glob("*/ssi-data.json"))

# what the estate actually caches per domain
cache = pathlib.Path("scripts/pipeline/.cache")
fam = collections.Counter()
for f in cache.glob("*.json"):
    fam["era5_baseline" if f.name.startswith("era5_baseline") else
        "seismic" if f.name.startswith("seismic") else
        "socioeconomic" if f.name.startswith("socioeconomic") else "other"] += 1

out = []
w = out.append
w("# SSI Index — Data Source Record")
w("")
w("**v1.0 · 20 August 2026 · Tree-4 source-of-record for every connected data source**")
w("")
w("**GENERATED, NOT HAND-WRITTEN.** Produced by `scripts/gen_source_record.py` from the live code")
w("registries (`ingestion/components.py`, `ingestion/continuity.py`, `scoring/engine.py`). A source")
w("record typed by hand drifts from the pipeline the moment anyone adds a fetcher, and a stale")
w("source-of-record is precisely the failure the precedence register exists to prevent. Re-run it")
w("in the same commit as any ingestion change.")
w("")
w("## Why this document exists")
w("")
w("Until today the estate had **no foundational record of its data sources**. The only catalogues")
w("were `scripts/pipeline/data/SOURCES_AND_LICENSES.md` — excellent, but a repo artefact, which the")
w("precedence register ranks **5**, *authoritative for behaviour, never for intent* — and")
w("`SSI_v4_0_Data_Architecture.html`, which describes the **Italy v4.0 single-country pilot** while")
w("declaring *81 LIVE sources, 0 BLOCKED*. Read as current, that document overstates the cohort's")
w("data position by an order of magnitude. Nothing in it says it is pilot scope.")
w("")
w("That gap is why a five-month-old single-country map could stand unchallenged as the cohort's")
w("data architecture. See `SSI_INGESTION_ARCHITECTURE_AUDIT_20260820.md`.")
w("")
w("---")
w("")
w("## 1. Implemented ingestion domains")
w("")
w("Four stages. The first three write into the **modifier** chain; the fourth (new, M-061) is the")
w("first producer of the **component** vector that `compute_r_base` consumes.")
w("")
w("| Stage | Module | Writes | Tier chain | Cache coverage |")
w("|---|---|---|---|---|")
w(f"| Seismic | `ingestion/seismic.py` | `seismic{{pga_g, zone, R6_seismic}}` | national fetcher → committed CSV → cache → live API → GEM 2023.1 | {fam['seismic']}/39 cached |")
w(f"| Climate | `ingestion/climate.py` | `climate_trajectory{{I1/I2/I3_trajectory}}` | national met fetchers (empty stubs) → GHCN-D → ERA5-Land | {fam['era5_baseline']}/39 cached |")
w(f"| Socio-economic | `ingestion/socioeconomic.py` | `socio_economic{{V_socio, E2_local, …}}` | Eurostat SDMX → OECD.Stat → national (ISTAT, NOMIS) | {fam['socioeconomic']}/39 cached |")
w("| **Components** | **`ingestion/components.py`** | **`metrics{…}` → `components{…}`** | ERA5-Land cached baseline | 39/39 |")
w("| Grid geometry | `ingestion/<country>/osm_overpass.py` | `grid-geo.json` | OSM Overpass | 39 modules |")
w("")
w("## 2. Metric coverage — what actually feeds a score")
w("")
w(f"**{len(implemented_metrics())} of {len(METRIC_REGISTRY)} metrics have an ingestion path.**")
w("A component letter is emitted only when *every* metric feeding it is present, so no component")
w("currently rolls up. That is the honest position, not a defect: a partial letter would count the")
w("unmeasured weight as zero risk (M-046 / M-061).")
w("")
w("| Metric | Component | Intra | Global weight | Status | Source or blocker |")
w("|---|---|---:|---:|---|---|")
for mid, spec in sorted(METRIC_REGISTRY.items(), key=lambda kv: (kv[1]["component"], kv[0])):
    comp = spec["component"]
    gw = COMPONENT_WEIGHTS[comp] * spec["intra"]
    status = "✅ implemented" if spec["status"] == "implemented" else "⛔ blocked"
    detail = (", ".join(spec.get("inputs") or []) if spec["status"] == "implemented"
              else spec.get("blocked_on", "—"))
    w(f"| **{mid}** | {comp} | {spec['intra']:.3f} | **{gw:.3f}** | {status} | {detail} |")
w("")
blocked_weight = sum(COMPONENT_WEIGHTS[s["component"]] * s["intra"]
                     for m, s in METRIC_REGISTRY.items() if s["status"] != "implemented")
impl_weight = sum(COMPONENT_WEIGHTS[s["component"]] * s["intra"]
                  for m, s in METRIC_REGISTRY.items() if s["status"] == "implemented")
# Present as exact fractions of the total so the two figures sum to 1.000 —
# summing independently-rounded values produced 0.068 + 0.933 = 1.001, which in
# a governance document reads as an arithmetic error rather than rounding.
_tot = impl_weight + blocked_weight
assert abs(_tot - 1.0) < 1e-9, f"component weights do not sum to 1: {_tot}"
w(f"**Weight with an ingestion path: {impl_weight:.3f} of 1.000. "
  f"Blocked: {1.0 - round(impl_weight, 3):.3f}.**")
w("")
w("## 3. Continuity domain — the largest single unlock")
w("")
cov = coverage_report()
w(f"`C` is weight {COMPONENT_WEIGHTS['C']:.2f} and `V` ({COMPONENT_WEIGHTS['V']:.2f}) is computed from SAIDI, so continuity data unlocks")
c1c2 = COMPONENT_WEIGHTS['C'] * (INTRA_WEIGHTS['C']['C1'] + INTRA_WEIGHTS['C']['C2'])
w(f"**{c1c2 + COMPONENT_WEIGHTS['V']:.2f} of R_base from SAIDI + SAIFI alone**, and {COMPONENT_WEIGHTS['C'] + COMPONENT_WEIGHTS['V']:.2f} once C3/C4 arrive.")
w("")
w("**The granularity constraint governs everything here.** Components normalise on a per-country")
w("fleet percentile, so a national figure gives every substation the same value, P5 == P95, and the")
w("metric carries no within-country information. `norm_percentile` returns `None` in that case")
w("rather than the construct's 0.5, so an all-national feed yields an absent metric rather than an")
w("inert constant. **Sub-national or it does not help.**")
w("")
w(f"Researched **{cov['researched']} of {cov['total_countries']}** countries. Usable granularity: **{len(cov['usable_granularity'])}**.")
w("")
w("| Status | Countries |")
w("|---|---|")
for st, cs in cov["by_status"].items():
    w(f"| `{st}` | {', '.join(cs)} |")
w(f"| `unresearched` | {', '.join(UNRESEARCHED)} |")
w("")
w("**This domain has no Tier 2.** The obvious international fallback, the CEER/ECRB Benchmarking")
w("Report, is national-only and its continuity series ends in **2018** — eight years stale, PDF")
w("only, no machine-readable annex. Unlike climate and seismic, continuity cannot fall back to a")
w("universal international layer. Countries in `absent` and `national_only` will not get a C")
w("component from published data.")
w("")
w("| Country | Publisher | Granularity | Vintage | Format | Note |")
w("|---|---|---|---|---|---|")
for c in sorted(CONTINUITY_SOURCES):
    s = CONTINUITY_SOURCES[c]
    note = (s["note"] or "")[:150]
    w(f"| {c} | {s['publisher']} | `{s['granularity']}` | {s['vintage'] or '—'} | {s['format'] or '—'} | {note} |")
w("")
w("## 4. Declared-but-not-implemented (the v4.0 Italy pilot architecture)")
w("")
w("`SSI_v4_0_Data_Architecture.html` (3 Mar 2026) declares 30 sources / 94 variables / 81 LIVE /")
w("0 BLOCKED. Cross-checked against `scripts/pipeline/ingestion/`, these have **no fetcher**:")
w("")
w("ARERA TIQE · E-Distribuzione · Terna Open Data · ENTSO-E Transparency · GSE Atlaimpianti ·")
w("JRC DSO Observatory · ISPRA IdroGEO · EEA Air Quality · Dimovski 2025 · OIPE LIHC ·")
w("IEEE/IEC/CIGRÉ · MEF IRPEF · MIMIT InfoCamere · DESI · SVIMEZ · Min. Salute · ENEA RAEE ·")
w("ISPRA SCIA · Protezione Civile · Consip/ANAC · MASE/SISEN · BdI QEF 737 · ISO 9223")
w("")
w("ARERA and Terna appear only in code comments; JRC, Dimovski, OIPE and IEEE have zero")
w("occurrences anywhere in the pipeline. **That document is Italy-pilot scope and should be")
w("labelled as such** — it is not a cohort data architecture and must not be cited as one.")
w("")
w("## 5. Maintenance")
w("")
w("- Regenerate with `python3 scripts/gen_source_record.py` **in the same commit** as any change to")
w("  an ingestion module, the metric registry, or the continuity registry.")
w("- A new source is added to its registry in code **first**; this document follows from it.")
w("- `unresearched` is not `absent`. Absence of research is not absence of data — M-030.")
w("")
w("---")
w("")
w("*Companion: `SSI_INGESTION_ARCHITECTURE_AUDIT_20260820.md` · `SSI_DOCUMENT_PRECEDENCE_REGISTER.md`")
w("· `scripts/pipeline/data/SOURCES_AND_LICENSES.md` (Tree 1, licences and DOIs).*")

print("\n".join(out))
