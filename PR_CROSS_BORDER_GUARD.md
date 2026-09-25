# PR — Cross-border substation enforcement gate (Discipline #36)

> **Lands:** 18 June 2026
> **Discipline:** #36 (KB §72.1)
> **Audit reference:** `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md`
> **Status:** Ready for review

---

## What changed

Three additions + two edits, all in the existing pipeline conventions:

### 1. `scripts/pipeline/utils/geo.py` (extended, ≈ +280 lines)

Added four pure-function helpers next to the existing `haversine_km`, `bilinear_interpolate`, `load_substations`:

- `load_country_polygon(country, repo_root=None, heal_topology=True)` — loads `{country}/bounds.json`, unions all sub-national features, optionally heals self-intersections via shapely `buffer(0)`. Returns `None` if `bounds.json` is missing (acceptable per Discipline #30 — `bounds.json` currently OPTIONAL for some countries).
- `is_inside_country(lat, lon, country_polygon, tolerance_km=0.1)` — point-in-polygon test with optional boundary-precision tolerance. Returns `(inside: bool, distance_km_outside: float)`.
- `filter_by_country_polygon(substations, country_polygon, tolerance_km=0.1)` — partitions substations into `(kept_inside, rejected_outside)`. Each rejected substation carries `_reject_reason` / `_reject_dist_km` / `_reject_tolerance_km` audit-trail fields.
- `cross_border_audit(country, ...)` — canonical entry point producing the per-country JSON report.

**shapely is lazy-imported** so existing `haversine_km` / `bilinear_interpolate` / `load_substations` keep working without the new dep.

### 2. `scripts/pipeline/requirements.txt` (1 line + comment)

Added `shapely>=2.0` with provenance comment referencing the audit.

### 3. `scripts/check_cross_border.py` (NEW, ≈ 220 lines)

Standalone deploy-gate, same pattern as `check_substation_schema.py` / `check_required_files.py`:

```bash
python3 scripts/check_cross_border.py                       # all countries (warn only)
python3 scripts/check_cross_border.py austria               # single country
python3 scripts/check_cross_border.py --all --strict        # fail-on-any-violation
python3 scripts/check_cross_border.py --tolerance-km 0.5    # 500m tolerance
python3 scripts/check_cross_border.py --json out.json       # machine-readable report
```

Exit codes:
- `0` — OK (all countries below threshold OR `--strict` not set)
- `1` — at least one country exceeds `--threshold` in `--strict` mode
- `2` — argument / environment error

Default thresholds: 5 % outside, 100 m tolerance buffer.

### 4. `italy/bounds.json` (healed)

12 of 20 Italian regional polygons had self-intersections (Lombardia, Veneto, Friuli-Venezia Giulia, Liguria, Emilia-Romagna, Toscana, Campania, Puglia, Basilicata, Calabria, Sicilia, Sardegna). All healed via `shapely.geometry.shape().buffer(0)` — preserves substantive shape, fixes ring topology.

Original preserved at `italy/bounds.json.pre-topology-fix-20260618T195451Z.backup`.

### 5. (NEW) `CROSS_BORDER_SUBSTATION_AUDIT_20260618.md`

Full audit memo at repo root — discovery, four failure modes, per-country results, remediation queue, reproducibility instructions.

---

## Why this matters

The 18 June 2026 audit found that the SSI Index's "174,046 substations across 39 OECD jurisdictions under continuous assessment" headline contained approximately 24,650 substations misattributed to the wrong country. Per-country worst cases:

| Country | Total subs | Outside | % Out | Failure mode |
|---|---:|---:|---:|---|
| greenland | 37 | 31 | 83.78 % | Coastline-precision polygon (Natural Earth simplification) |
| canada | 24,986 | 18,587 | 74.39 % | Polygon excludes Arctic islands / territories |
| **austria** | **1,406** | **665** | **47.30 %** | **Cross-border ingestion overshoot (Bavarian / Slovenian / South-Tyrolean / Engadin substations misattributed)** |
| norway | 6,495 | 1,464 | 22.54 % | Svalbard / coastline polygon gaps |
| mexico | 3,140 | 704 | 22.42 % | Ingestion overshoot |
| uk | 3,150 | 599 | 19.02 % | Crown Dependencies / overseas territories |
| chile | 1,095 | 130 | 11.87 % | Polygon gaps |
| france | 7,898 | 520 | 6.58 % | DOM-TOM not in `bounds.json` |
| new-zealand | 1,558 | 101 | 6.48 % | Coastline precision |
| denmark | 2,451 | 123 | 5.02 % | Greenland-handling overflow |

Italy — the Stage 4 pilot — post-topology-heal lands at **0.00 % outside** under the 100m default tolerance. The brief's empirical-anchor claim verified through the production gate.

---

## How to test locally

```bash
# 1. Install the new dep
pip install -r scripts/pipeline/requirements.txt

# 2. Sanity-check Italy (expect CLEAN)
python3 scripts/check_cross_border.py italy

# 3. Sanity-check Austria (expect SEVERE)
python3 scripts/check_cross_border.py austria

# 4. Full cohort sweep with machine-readable report
python3 scripts/check_cross_border.py --all --json audit/cross-border-$(date -u +%Y-%m-%d).json
```

Expected output for Italy:

```
italy                 4293    4293        0   0.00%     0.0 ✅ CLEAN
```

Expected output for Austria:

```
austria               1406     741      665  47.30%   103.6 🚨 SEVERE
```

---

## CI integration

Recommended wiring after every `.github/workflows/monthly-refresh.yml` cron run, after substation ingestion completes:

```yaml
      - name: Cross-border polygon gate (Discipline #36)
        run: |
          pip install shapely
          python3 scripts/check_cross_border.py --all --json \
            audit/cross-border-$(date -u +%Y-%m-%d).json
```

For LIFE-RESILINK 22 Sep 2026 submission readiness — wire as **strict gate**:

```yaml
      - name: Cross-border polygon gate (STRICT — Discipline #36)
        run: |
          pip install shapely
          python3 scripts/check_cross_border.py --all --strict \
            --threshold 5.0 --json audit/cross-border-$(date -u +%Y-%m-%d).json
```

The strict gate currently fails 10 of 39 countries; deploy in **warn-only mode** until the per-country remediation queue completes (see audit memo §Recommended remediation queue).

---

## Future-state: ingestion-time enforcement

This PR addresses **detection** (the gate catches drift at refresh time). The fuller fix is **prevention** (filter substations at ingestion source so foreign substations never enter `{country}/ssi-data.json` in the first place).

The helpers are designed for that next step:

```python
from scripts.pipeline.utils.geo import (
    load_country_polygon, filter_by_country_polygon,
)

# At ingestion time, after fetching from upstream source:
country_polygon = load_country_polygon("austria")
kept, rejected = filter_by_country_polygon(raw_substations, country_polygon)

# Persist rejection audit-trail for review:
with open("austria/ingestion_rejected.json", "w") as f:
    json.dump(rejected, f, indent=2)

# Write only kept substations into ssi-data.json:
data["substations"] = kept
```

This requires identifying the per-country ingestion entry points (build_hungary_ssi.py / build_slovakia_ssi.py / per-country scoring-XX pipelines) and inserting the filter at the right step. That's a separate PR — this one delivers the detection gate that prevents regression while the source-side fix lands.

---

## Backward compatibility

- **No breaking changes.** All new code; no existing behaviour modified.
- **shapely is lazy-imported** — environments without shapely still work for non-polygon helpers.
- **Italy `bounds.json` healed in place** with full backup preserved; downstream consumers (`country-renderer.js`, `map.html`) see identical polygon shape with self-intersections fixed.

---

## Files changed in this PR

```
A   CROSS_BORDER_SUBSTATION_AUDIT_20260618.md          (NEW, audit memo)
A   PR_CROSS_BORDER_GUARD.md                            (NEW, this PR description)
A   scripts/check_cross_border.py                       (NEW, deploy-gate)
M   scripts/pipeline/utils/geo.py                       (+280 lines: 4 helpers)
M   scripts/pipeline/requirements.txt                   (+10 lines: shapely + comment)
M   italy/bounds.json                                   (12 region polygons healed via buffer(0))
A   italy/bounds.json.pre-topology-fix-20260618*.backup (NEW, backup of pre-heal)
```

---

## Operator decisions queued

After this PR lands, two operator decisions arise from the audit:

1. **Per-country remediation order** — which countries to clean first? Suggested priority:
   - **Italy: DONE** (verified clean)
   - **Austria: NEXT** (worst SEVERE; user-surfaced; LIFE-RESILINK Stage 4 expansion target)
   - Greenland, Canada (SEVERE coastline / polygon-gap class)
   - Norway, Mexico, UK, Chile (MODERATE)
   - 13 MINOR countries last

2. **Disclosure path for Strategic Brief No. 01** — three options per the audit memo §Implications:
   - (a) Acknowledge the audit in a §1.3 footnote, commit cleanup to B1 September 2026 publication
   - (b) Hold publication until Priority-1 fixes land (mechanically modest — ~1 working week)
   - (c) Treat the audit as a separate methodology-validation publication
   - Recommended path: **(a) + (c)** — disclose in brief, fix immediately, position the validation discipline as a feature in B1

These decisions belong to the operator and are not in scope of this PR.

---

*PR_CROSS_BORDER_GUARD.md v1 · authored 18 June 2026 deep night · CC BY-SA 4.0*
