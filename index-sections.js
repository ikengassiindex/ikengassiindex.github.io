/* ═══════════════════════════════════════════════════════════════════════════
   index-sections.js — Phase 2d (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `index` page
   (Overview / landing). The shared rendering logic — KPI row, fleet
   distribution bar, top-critical table, component contribution bars,
   confidence distribution, modifier fleet stats, and the scale-stats
   Quick-Facts panel — lives here so every country's index.html collapses
   to a thin-shell that calls:

       CountryRenderer.init('<country>', 'index');

   Country-specific values live in:
     - `intelligence/country-configs/<slug>.json`
         · `admin.l1.count`               — region count used in KPI subs
         · `admin.l1.label_en`            — singular region label (e.g. 'NUTS-3 region')
         · `index_page.critical_threshold` — R-band cutoff for "Critical Band" KPI sub
                                            (default 0.75)
         · `index_page.r3_label` / etc.   — optional KPI subtitle overrides
     - `<country>/ssi-metadata.js`
         · `window.SSI_METADATA.COMPONENTS` — fed into the fleet-average bar.
           Defaults to a universal SSI v4.0 catalogue if absent.
         · `window.SSI_METADATA.MODIFIER_DEFS` (optional) — overrides the
           default R3/R4/R6a/R6b/R7 panel.

   The mini-map is still initialised by the HTML shell calling
   `SSIMap.init('mini-map-canvas', { embedded: true })`. CountryRenderer
   does NOT own the map — it owns the data-driven sections only.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js   (provides window.CountryRenderer)
     - ssi-metadata.js       (window.SSI_METADATA.*; optional COMPONENTS)
     - map.js                (only for the embedded mini-map block)

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[index-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var H = CR.H;
  var Safe = CR.Safe;  // SK hotfix #2 — KB §68.9

  /* ── Universal palette ──────────────────────────────────────────────── */
  var BAND_VAR = {
    Low: 'var(--band-low)',
    Medium: 'var(--band-medium)',
    High: 'var(--band-high)',
    Critical: 'var(--band-critical)',
    // Phase 2B-2 (25 June 2026): 5-band system; Extreme for R_median in
    // [1.00, 1.30]. Front-page distribution bar preserves 4-segment shape
    // by folding Extreme into Critical (both are 'R >= 0.75' semantically);
    // Extreme is separately visible in intelligence-page widgets.
    Extreme: 'var(--band-extreme)'
  };

  /* ── Default fleet-average component catalogue (SSI v4.0.2 universal).
       Each country can override via window.SSI_METADATA.COMPONENTS_INDEX or
       fall back to the canonical 6-component weighting if absent. ─────── */
  var DEFAULT_COMPONENT_BARS = [
    { key: 'C', label: 'C — Continuity',         w: 0.30, color: 'var(--crimson)' },
    { key: 'I', label: 'I — Infrastructure',     w: 0.25, color: 'var(--sage)' },
    { key: 'S', label: 'S — Saturation',         w: 0.20, color: 'var(--bronze)' },
    { key: 'V', label: 'V — Voltage Quality',    w: 0.10, color: 'var(--terracotta)' },
    { key: 'E', label: 'E — Economic',           w: 0.10, color: '#3b9eff' },
    { key: 'T', label: 'T — Energy Transition',  w: 0.05, color: '#22d3ee' }
  ];

  /* ── Default modifier panel — 5 modifiers (R3, R4, R6a, R6b, R7). ──── */
  var DEFAULT_MODIFIER_DEFS = [
    { key: 'R4_F_topo',      label: 'R4',  domain: 'Graph Criticality',   range: '[0.80, 1.35]' },
    { key: 'R3_C_mult',      label: 'R3',  domain: 'Consequence',          range: '[0.70, 1.30]' },
    { key: 'R6_restoration', label: 'R6a', domain: 'Restoration Speed',    range: '[0.90, 1.10]' },
    { key: 'R6_seismic',     label: 'R6b', domain: 'Network Topology',     range: '[1.00, 1.25]' },
    { key: 'R7_cyber',       label: 'R7',  domain: 'Digital Readiness',    range: '[0.99, 1.05]' }
  ];

  /* ── Defaults exposed for non-migrated countries ─────────────────────── */
  function getCriticalThreshold(cfg) {
    if (cfg && cfg.index_page && typeof cfg.index_page.critical_threshold === 'number') {
      return cfg.index_page.critical_threshold;
    }
    if (cfg && cfg.thresholds && typeof cfg.thresholds.critical_threshold === 'number') {
      return cfg.thresholds.critical_threshold;
    }
    return 0.75;
  }

  function getRegionLabel(cfg) {
    if (cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.label_en) {
      return cfg.admin.l1.label_en;
    }
    return 'region';
  }

  function getRegionLabelPlural(cfg) {
    var lbl = getRegionLabel(cfg);
    // Avoid a stray trailing 's' if config already supplied a plural-ready form.
    return /s$/i.test(lbl) ? lbl : lbl + 's';
  }

  /* COMPONENTS_INDEX consumers — schema normalisation now lives in
     CountryRenderer.normalizeMeta() (KB §68.11 / BPG Part XXXV.3), which
     runs once at load time, before any section handler. The metadata
     reaching this file is already in canonical {key, label, w, color}
     shape regardless of what the country ssi-metadata.js shipped. We
     only need to choose between the country-supplied array and the
     universal default fallback. */
  function getComponentBars() {
    var meta = window.SSI_METADATA || {};
    if (Array.isArray(meta.COMPONENTS_INDEX) && meta.COMPONENTS_INDEX.length) {
      return meta.COMPONENTS_INDEX;
    }
    return DEFAULT_COMPONENT_BARS;
  }

  function getModifierDefs() {
    var meta = window.SSI_METADATA || {};
    if (Array.isArray(meta.MODIFIER_DEFS) && meta.MODIFIER_DEFS.length) {
      return meta.MODIFIER_DEFS;
    }
    return DEFAULT_MODIFIER_DEFS;
  }

  /* ── Helpers ─────────────────────────────────────────────────────────── */
  function fmtScale(v) {
    if (v == null || isNaN(v)) return '—';
    if (v >= 1e9) return (v / 1e9).toFixed(2) + ' B';
    if (v >= 1e6) return (v / 1e6).toFixed(1) + ' M';
    if (v >= 1e3) return v.toLocaleString('en-US');
    return String(v);
  }

  function bandLower(b) { return (b || '').toLowerCase(); }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country, page, doc}
     ssi-data.json is already loaded + normalized by CountryRenderer.init.
     ══════════════════════════════════════════════════════════════════════ */

  /* ── 1. Scale-stats panel (Quick Facts → computations, MC runs, dp) ─── */
  CR.register('index', 'scale-stats', function (ctx) {
    var data = ctx.data || {};
    var subs = data.substations || [];
    var n = subs.length;
    if (!n) return;

    // KB §64.3 A12 — null-coerced-to-default in numeric comparisons:
    // Many countries' OSM extracts have substations with voltage_kv=null
    // (untagged). The pre-A12 pattern `Number(s.voltage_kv || 0) >= 132`
    // coerces null to 0, then 0 >= 132 is false, silently mis-counting
    // every untagged substation as MV. Fix: explicit null check before
    // comparison. Counts shift to "known HV (≥132 kV) + everything else".
    // Safe.num with -Infinity sentinel: any null v is excluded from the
    // >=132 count, so 'mv = n - hv' captures both "known MV" and "unknown".
    var isArr = Array.isArray(subs[0]);
    var hv = subs.filter(function (s) {
      var v = isArr ? s[3] : s.voltage_kv;
      return Safe.num(v, -Infinity) >= 132;
    }).length;
    var mv = n - hv;

    var mcIter = (data.meta && data.meta.mc_iterations) || 10000;
    var vars = (data.meta && data.meta.variables) || 95;
    var mc = n * mcIter;
    var comp = Math.round(mc * vars / 9.19);
    var dp = Math.round(n * 60.05);

    H.setText('scale-comp', fmtScale(comp));
    H.setText('scale-mc', fmtScale(mc));
    H.setText('scale-dp', fmtScale(dp));
    H.setText('scale-subs', n.toLocaleString('en-US') + ' substation risk scores · ' +
      hv.toLocaleString('en-US') + ' HV · ' + mv.toLocaleString('en-US') + ' MV');
    // Total power-line kilometrage — sourced from SSI_CANONICAL_LITERALS
    // (baked at build time from grid-geo.json haversine sum over l[].p polylines).
    // Falls back to em-dash when the canonical is missing so degradation stays honest.
    var gridKm = (window.SSI_CANONICAL_LITERALS &&
                  window.SSI_CANONICAL_LITERALS['fleet.grid_lines_km']) || '—';
    H.setText('scale-lines', gridKm);
    H.setText('scale-leaves', String(vars));
  });

  /* ── 2. Headline KPI row (total / median / critical / freshness) ────── */
  CR.register('index', 'kpi-row', function (ctx) {
    var data = ctx.data || {};
    var fs = data.fleet_summary || {};
    var cfg = ctx.config || {};
    var critThr = getCriticalThreshold(cfg);
    var regionLabel = getRegionLabelPlural(cfg);

    var total = fs.total || (data.substations ? data.substations.length : 0);
    var medianR = fs.median_R != null ? fs.median_R : (fs.R_median != null ? fs.R_median : 0);
    var p5 = fs.P5 != null ? fs.P5 : (fs.R_min != null ? fs.R_min : 0);
    var p95 = fs.P95 != null ? fs.P95 : (fs.R_max != null ? fs.R_max : 0);
    var bands = fs.bands || {};
    var bandPct = fs.band_pct || {};
    // Phase 2B-2 (25 June 2026): 5-band system; kpi-critical now shows
    // Critical+Extreme aggregated (both are 'R >= 0.75' semantically).
    // Preserves the "Critical Band" KPI label truthfulness since Extreme
    // R_median in [1.00, 1.30] is by definition also above the threshold.
    var critCount = (bands.Critical || 0) + (bands.Extreme || 0);
    var critPct = (bandPct.Critical != null ? bandPct.Critical : 0) +
                  (bandPct.Extreme  != null ? bandPct.Extreme  : 0);

    H.setText('kpi-total', Safe.locale(total));
    H.setText('kpi-median', Safe.fmt(medianR, 3));
    H.setText('kpi-median-sub',
      'P5 = ' + Safe.fmt(p5, 3) + ' · P95 = ' + Safe.fmt(p95, 3));
    H.setText('kpi-critical', String(critCount));
    H.setText('kpi-critical-sub',
      Safe.pct(critPct, 1) + ' of fleet · R ≥ ' + Safe.fmt(critThr, 2));

    // Voltage-class split for the total-sub line (deferring to data when
    // available, falling back to the existing static markup if absent).
    // KB §64.3 A12 — null-coerced-to-default: untagged OSM substations have
    // voltage_kv=null. Explicit null check before threshold compare so the
    // "EHV / HV / distribution-tier" trichotomy is honest about what we know.
    var subs = data.substations || [];
    if (subs.length) {
      // Three-way voltage trichotomy via Safe.voltageClass — single source
      // of truth for the EHV/HV/distribution-tier split (KB §68.9).
      var ehvCount = 0, hvCount = 0;
      subs.forEach(function (s) {
        var cls = Safe.voltageClass(s.voltage_kv);
        if (cls === 'EHV') ehvCount++;
        else if (cls === 'HV') hvCount++;
      });
      var distCount = total - ehvCount - hvCount;  // distribution-tier + untagged
      var nRegions = (data.regions && data.regions.length) ||
        (cfg.admin && cfg.admin.l1 && cfg.admin.l1.count) || 0;
      H.setText('kpi-total-sub',
        ehvCount.toLocaleString() + ' EHV · ' +
        hvCount.toLocaleString() + ' HV · ' +
        distCount.toLocaleString() + ' distribution-tier · ' +
        nRegions + ' ' + regionLabel);
    }
  });

  /* ── 3. Fleet distribution bar + legend ──────────────────────────────── */
  CR.register('index', 'distribution-bar', function (ctx) {
    var data = ctx.data || {};
    var fs = data.fleet_summary || {};
    var bp = fs.band_pct || {};
    var bc = fs.bands || {};
    var total = fs.total || (data.substations ? data.substations.length : 0);

    H.setText('dist-count', total.toLocaleString() + ' substations');

    var setWidth = function (id, pct) {
      var el = document.getElementById(id);
      if (el) el.style.width = Number(pct || 0) + '%';
    };
    setWidth('dist-low', bp.Low);
    setWidth('dist-med', bp.Medium);
    setWidth('dist-high', bp.High);
    // Phase 2B-2 (25 June 2026): dist-crit segment now shows
    // Critical+Extreme aggregated (both are 'R >= 0.75' semantically).
    // The legend label follows suit. Extreme is separately visible in
    // the intelligence-page distribution widgets.
    var critAndExtremePct = Number(bp.Critical || 0) + Number(bp.Extreme || 0);
    var critAndExtremeCnt = Number(bc.Critical || 0) + Number(bc.Extreme || 0);
    setWidth('dist-crit', critAndExtremePct);

    var setLegend = function (id, label, count, pct) {
      H.setText(id, label + ' ' + Number(count || 0).toLocaleString() +
        ' (' + Number(pct || 0).toFixed(1) + '%)');
    };
    setLegend('legend-low', 'Low', bc.Low, bp.Low);
    setLegend('legend-med', 'Medium', bc.Medium, bp.Medium);
    setLegend('legend-high', 'High', bc.High, bp.High);
    var critLabel = (bc.Extreme > 0) ? 'Crit+Ext' : 'Critical';
    setLegend('legend-crit', critLabel, critAndExtremeCnt, critAndExtremePct);
  });

  /* ── 4. Top critical substations table (top 8 by R_median) ──────────── */
  CR.register('index', 'top-critical', function (ctx) {
    var data = ctx.data || {};
    var subs = (data.substations || []).slice();
    if (!subs.length) return;

    var top8 = subs.sort(function (a, b) { return Safe.num(b.R_median, 0) - Safe.num(a.R_median, 0); }).slice(0, 8);
    var tbody = document.getElementById('top-critical-tbody');
    if (!tbody) return;

    // Safe.displayName + Safe.fmt — single source of truth for null-safe
    // rendering (KB §68.9 A12.4 / A12.2).
    tbody.innerHTML = top8.map(function (s) {
      var band = s.classification || 'Low';
      var bandLow = bandLower(band);
      return '<tr><td style="font-weight:500">' + Safe.displayName(s) + '</td>' +
        '<td>' + (s.province || '') + '</td>' +
        '<td class="num">' + Safe.fmt(s.R_median, 3) + '</td>' +
        '<td><span class="band-badge ' + bandLow + '"><span class="band-dot ' + bandLow + '"></span>' + band + '</span></td></tr>';
    }).join('');
  });

  /* ── 5. Component contribution bars (fleet average) ──────────────────── */
  CR.register('index', 'component-bars', function (ctx) {
    var data = ctx.data || {};
    var subs = data.substations || [];
    if (!subs.length) return;
    var defs = getComponentBars();

    var sums = {};
    defs.forEach(function (d) { sums[d.key] = 0; });
    subs.forEach(function (s) {
      var c = s.components || {};
      defs.forEach(function (d) {
        sums[d.key] += Safe.num(c[d.key], 0);
      });
    });
    var n = subs.length;
    defs.forEach(function (d) { sums[d.key] /= n; });

    var html = '<div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:11px;color:var(--warm-grey)">' +
      '<span>◀ Higher risk</span><span>Lower risk ▶</span></div>';
    html += defs.map(function (c) {
      var avg = sums[c.key];
      var barPct = Safe.fmt(Math.min(avg * 100, 100), 1);
      return '<div style="margin-bottom:14px">' +
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px">' +
          '<span style="font-size:13px;font-weight:500">' + c.label + '</span>' +
          '<span style="font-size:12px;color:var(--warm-grey)">w = ' + Safe.fmt(c.w, 2) + ' · avg = ' + Safe.fmt(avg, 3) + '</span>' +
        '</div>' +
        '<div style="height:8px;background:var(--cream-deep);border-radius:4px;overflow:hidden">' +
          '<div style="width:' + barPct + '%;height:100%;background:' + c.color + ';border-radius:4px"></div>' +
        '</div></div>';
    }).join('');
    H.setHTML('comp-bars', html);
  });

  /* ── 6. Confidence distribution (high/medium/low) ────────────────────── */
  CR.register('index', 'confidence-bars', function (ctx) {
    var data = ctx.data || {};
    var fs = data.fleet_summary || {};
    var cp = fs.confidence_pct || { high: 0, medium: 0, low: 0 };

    var defs = [
      { label: 'High',   pct: cp.high   || 0, color: 'var(--sage)' },
      { label: 'Medium', pct: cp.medium || 0, color: 'var(--bronze)' },
      { label: 'Low',    pct: cp.low    || 0, color: 'var(--terracotta)' }
    ];
    var html = defs.map(function (c) {
      var pct = Number(c.pct).toFixed(1);
      return '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">' +
        '<div style="width:60px;font-size:12px;font-weight:500;color:' + c.color + '">' + c.label + '</div>' +
        '<div style="flex:1;height:8px;background:var(--cream-deep);border-radius:4px;overflow:hidden">' +
          '<div style="width:' + pct + '%;height:100%;background:' + c.color + ';border-radius:4px"></div>' +
        '</div>' +
        '<div style="width:50px;font-size:12px;text-align:right;color:var(--warm-grey)">' + pct + '%</div></div>';
    }).join('');
    H.setHTML('confidence-bars', html);
  });

  /* ── 7. Modifier impact table (R3/R4/R6a/R6b/R7 fleet stats) ─────────── */
  CR.register('index', 'modifier-stats', function (ctx) {
    var data = ctx.data || {};
    var subs = data.substations || [];
    if (!subs.length) return;
    var defs = getModifierDefs();

    var modStats = defs.map(function (m) {
      var vals = subs.map(function (s) {
        return (s.modifiers && s.modifiers[m.key] != null) ? Number(s.modifiers[m.key]) : NaN;
      }).filter(function (v) { return !isNaN(v); });
      if (!vals.length) {
        return { label: m.label, domain: m.domain, range: m.range, sigma: NaN };
      }
      var mean = vals.reduce(function (a, b) { return a + b; }, 0) / vals.length;
      var variance = vals.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / vals.length;
      return { label: m.label, domain: m.domain, range: m.range, sigma: Math.sqrt(variance) };
    });
    modStats.sort(function (a, b) {
      var sa = isNaN(a.sigma) ? -1 : a.sigma;
      var sb = isNaN(b.sigma) ? -1 : b.sigma;
      return sb - sa;
    });

    var tbody = document.getElementById('modifier-tbody');
    if (!tbody) return;
    tbody.innerHTML = modStats.map(function (m) {
      return '<tr><td style="font-weight:500">' + m.label + '</td>' +
        '<td>' + m.domain + '</td>' +
        '<td class="num">' + m.range + '</td>' +
        '<td class="num">' + (isNaN(m.sigma) ? '—' : m.sigma.toFixed(3)) + '</td></tr>';
    }).join('');
  });

})();
