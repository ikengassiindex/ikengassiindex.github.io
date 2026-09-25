# ESG Report — climate_trajectory shape audit (39-country cohort)

> **Trigger**: Operator observation 22 July 2026 — "on ESG report page, I note we still have some '—' for ERA5 items and we have some 'GAP', I looked at Australia as an illustration (Canada on the contrary, for instance, is clean)"
>
> **Diagnostic scope**: Section 1 (Climate Physical Risk Assessment) → "SSI Variables Feeding This Report" table → I1 Snow/Ice IRI / I2 Tree-fall IRI / I3 Heat-wave IRI rows
>
> **Author**: Sandbox audit — no code committed by this doc
>
> **Related tasks**: #443 (v4.23 gap audit — parent), #448 (this — reopened + retitled), #450 (Wave 4 systemic uniformity — parallel)

## Findings

### 1. Root cause is a data-shape mismatch, not a data-source outage

The frontend at `esg-sections.js` lines 74-76 renders these three rows via:

```javascript
['I1', 'Snow/Ice IRI',
  (d.climate_trajectory && d.climate_trajectory.I1_trajectory != null)
    ? d.climate_trajectory.I1_trajectory.toFixed(3)
    : '—',
  'ESRS E1-9: Financial effects from physical risks',
  (d.climate_trajectory && d.climate_trajectory.I1_trajectory != null) ? 'ready' : 'gap'],
```

It expects the substation record to carry:

```json
{
  "climate_trajectory": {
    "I1_trajectory": 0.983,
    "I2_trajectory": 1.050,
    "I3_trajectory": 1.026
  }
}
```

That is the v4.2 CMIP6-derived dict shape emitted by `scripts/pipeline/enrichment/climate_trajectory.py`.

### 2. 39-country empirical shape distribution

| Shape | Count | Frontend behaviour | Countries |
|---|---:|---|---|
| **Dict (v4.2, correct)** | **32** | Real values, `READY` | 32/39 — see per-country breakdown below |
| **Str (legacy v4.0.2)** | **3** | `—` + `GAP` | 🇦🇺 Australia · 🇨🇱 Chile · 🇮🇪 Ireland |
| **None (missing)** | **4** | `—` + `GAP` | 🇨🇴 Colombia · 🇨🇷 Costa Rica · 🇮🇸 Iceland · 🇮🇱 Israel |
| **Total showing gap** | **7** | Matches doc claim word-for-word | |

The narrative already displayed on the page ("Any PARTIAL status now reflects country-specific gaps: 7 Wave 2-3 countries (Australia, Chile, Colombia, Costa Rica, Iceland, Ireland, Israel) await the next L2 climate pass") is **empirically confirmed**.

### 3. Australia empirical sample (the operator's illustration)

```
Sub #0: id=AU_100001
  climate_trajectory type: str
  climate_trajectory value: "deteriorating"

Sub #1: id=AU_100002
  climate_trajectory type: str
  climate_trajectory value: "deteriorating"

Sub #2: id=AU_100003
  climate_trajectory type: str
  climate_trajectory value: "deteriorating"
```

Every Australian substation carries the same 3-way categorical trajectory label (deteriorating / stable / improving) that predates the v4.2 CMIP6 upgrade. The label is truthful at the country-fleet level — it just isn't the per-metric per-substation shape the frontend now wants.

### 4. Canada empirical sample (the operator's clean baseline)

```
Sub #0: id=CA_281360782
  climate_trajectory: {'I1_trajectory': 0.9828, 'I2_trajectory': 1.05, 'I3_trajectory': 1.0258}

Sub #1: id=CA_315649176
  climate_trajectory: {'I1_trajectory': 0.9828, 'I2_trajectory': 1.05, 'I3_trajectory': 1.0258}

Sub #2: id=CA_432772923
  climate_trajectory: {'I1_trajectory': 0.9828, 'I2_trajectory': 1.05, 'I3_trajectory': 1.0258}
```

Canada carries the v4.2 dict shape → frontend displays real values → `READY`. Note: Canada shows **uniform values across all 20-sub sample** — that's the per-substation interpolation regression (Task #450) but at least the shape contract is met and the tier calibration lands honest values.

### 5. Full 39-country dict-shape audit (per-substation uniformity flag included)

**Dict + varies (14 countries — proper Wave 4 interpolation)**: austria · finland · hungary · italy · new-zealand · norway · poland · slovakia · slovenia · switzerland · turkey · france · us · (implicitly others sampled 2+ variants).

**Dict + uniform (18 countries — Wave 4 interpolation regression, Task #450)**: belgium · canada · czechia · denmark · estonia · greece · greenland · japan · korea · latvia · lithuania · luxembourg · mexico · netherlands · portugal · spain · germany · uk.

**Str (3 countries — legacy v4.0.2 categorical)**: australia · chile · ireland.

**None (4 countries — field absent entirely)**: colombia · costa-rica · iceland · israel.

### 6. Second observation — Migration Score also shows "—"

This is not Australia-specific. Both Australia and Canada show `Migration Score: —` in Section 2 (Grid Equity). This is Task #452 (already pending): 20 countries missing the `migration_score` field entirely. Not related to the climate_trajectory issue but worth surfacing in the same audit.

### 7. Third observation — R7 top-radar vs section body inconsistency

At the top of the page (ESG Radar overview), the R7 · SFDR PAI Infrastructure badge shows:
- **Australia**: `READY` (top radar) / `READY` (section body) — consistent
- **Canada**: `GAP` (top radar) / `READY` (section body) — inconsistent!

Canada's Re_norm = 0.590 with 6/8 modifiers populated → section body correctly marks READY. But the top-radar Re_norm gate threshold (probably `Re_normalised != None` field-name mismatch with `Re_norm`) trips a false GAP. Separate mini-bug — worth filing but not in this audit's primary scope.

## Recommended paths

### Path A — Backend pipeline fix (proper, addresses root cause)

Extend `scripts/pipeline/enrichment/climate_trajectory.py` to write the v4.2 dict shape for the 7 affected countries. The CMIP6 SSP2-4.5 5-model ensemble data + ERA5 baseline are already ingested — this is a compute step, not a fresh L1 fetch.

**Per-country expected outcome:**
- **AU · CL · IE (str-shape)**: Overwrite `climate_trajectory: "deteriorating"` → `{I1_trajectory, I2_trajectory, I3_trajectory}` dict.
- **CO · CR · IS · IL (None-shape)**: Insert the dict field.

**Cost estimate**: Sandbox script exists (`scripts/pipeline/enrichment/climate_trajectory.py`) and has been used successfully on the 32-country cohort. Running it on the 7 remaining countries is a ~15-30 min per-country compute job × 7 = 2-4 hours. All 7 fit under the ssi-data 100 MB unshared limit (no Convention #79 sharding needed).

**Expected UI impact**: 7 countries' ESG reports flip from `—`/`GAP` on I1/I2/I3 to real `READY` values. Consistent with 32-country baseline.

### Path B — Frontend graceful fallback (cosmetic, doesn't fix data)

Extend `esg-sections.js` lines 74-76 to recognise the legacy string shape:

```javascript
// Handle legacy v4.0.2 categorical trajectory string
const isDict = d.climate_trajectory && typeof d.climate_trajectory === 'object';
const isStr = typeof d.climate_trajectory === 'string';
const label = isDict ? d.climate_trajectory.I1_trajectory.toFixed(3)
            : isStr ? `[${d.climate_trajectory} — v4.0.2]`
            : '—';
const status = isDict ? 'ready' : isStr ? 'partial' : 'gap';
```

**Cost estimate**: 15-min patch.

**UI impact**: AU/CL/IE would display `[deteriorating — v4.0.2]` + PARTIAL for I1/I2/I3 instead of `—` + GAP. The 4 None-shape countries still show GAP.

**Recommendation**: Path A is the honest fix. Path B is a placeholder that masks a real data-shape gap. Ship Path A.

### Path C — Both paths sequentially

Ship Path B first as an interim UX improvement (few days visible improvement while backend work runs), then Path A when the L2 pipeline lands. Rollback Path B when Path A is verified.

## Follow-on tasks (already tracked, no new tasks needed)

- **Task #448** (this — reopened + retitled to reflect empirical scope): CMIP6 climate_trajectory shape fix for AU/CL/CO/CR/IS/IL/IE
- **Task #450**: Wave 4 systemic per-substation interpolation regression (fixes the 18 uniform-values countries — separate class from this issue)
- **Task #451**: R2 catchment population missing (9 countries)
- **Task #452**: R2 migration_score missing (~20 countries — the second observation above)
- **Task #453**: R2 partial socio_economic coverage (LU/SI/CO/LT)

## Cross-references

- Frontend row emitter: `esg-sections.js` lines 74-76 (I1/I2/I3 rows)
- Frontend validity narrative: `esg-sections.js` line 84 (already documents the 7-country gap accurately)
- Backend pipeline entry point: `scripts/pipeline/enrichment/climate_trajectory.py`
- Related parent audit: Task #443 (v4.23 gap audit ERA5 wiring investigation)
