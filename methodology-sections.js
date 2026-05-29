/* ═══════════════════════════════════════════════════════════════════════════
   methodology-sections.js — Phase 2d.4 (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `methodology`
   page. The static reference content (Thesis, Pipeline, Master Equation,
   Component table, Modifiers table, Classification bands, MC card, Competitive
   Positioning) lives inline in the HTML shell — those blocks are universal
   across countries and don't need a renderer. The data-driven blocks are:

      #method-metrics-detail   — 6 components × N metrics, fed from SSIMetadata.COMPONENTS
      #method-norm             — 4 normalisation methods, fed from SSIMetadata.NORM_METHODS
      #method-layers tbody     — 11 data layers, fed from SSIMetadata.DATA_LAYERS
      #method-sources tbody    — 30+ data sources, fed from SSIMetadata.DATA_SOURCES
      #method-validation tbody — validation checks, fed from SSIMetadata.VALIDATION_CHECKS
      #method-changelog tbody  — v3.4 → v4.0.2 changelog, fed from SSIMetadata.CHANGELOG

   All six tables iterate metadata arrays already provided by the per-country
   ssi-metadata.js. No country-specific JSON values are read here — every
   country's metadata file ships its own COMPONENTS/NORM/DATA_LAYERS/SOURCES/
   VALIDATION/CHANGELOG arrays, and the renderer is purely a HTML formatter.

   Cross-country defaults: if `window.SSIMetadata` is absent (which would
   indicate a misconfigured per-country page), the registrations fall back to
   universal SSI v4.0.2 reference arrays so the page still renders. Real
   countries always override.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - ssi-metadata.js      (window.SSI_METADATA / window.SSIMetadata.*)

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[methodology-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var Safe = CR.Safe;  // SK hotfix #2 — KB §68.9

  /* ── Universal SSI v4.0.2 defaults (used only when ssi-metadata.js is
       missing arrays — every country should override). ─────────────────── */
  var DEFAULT_COMPONENTS = [
    { id: 'C', name: 'Continuity',     weight: 0.30, color: 'var(--crimson)',    metrics: [] },
    { id: 'V', name: 'Voltage',         weight: 0.10, color: 'var(--terracotta)', metrics: [] },
    { id: 'I', name: 'Infrastructure',  weight: 0.25, color: 'var(--sage)',        metrics: [] },
    { id: 'E', name: 'Economic',        weight: 0.10, color: '#3b9eff',            metrics: [] },
    { id: 'S', name: 'Saturation',      weight: 0.20, color: 'var(--bronze)',      metrics: [] },
    { id: 'T', name: 'Transition',      weight: 0.05, color: '#22d3ee',             metrics: [] }
  ];

  var DEFAULT_NORM_METHODS = [
    { id: 'A', name: 'Robust fleet percentile (P5/P95)',
      formula: 'x_norm = clip((x - P5) / (P95 - P5), 0, 1)',
      applies: 'continuity, economic, infrastructure stress metrics' },
    { id: 'B', name: 'Standard fleet percentile',
      formula: 'x_norm = (rank(x) - 1) / (n - 1)',
      applies: 'density + saturation metrics' },
    { id: 'C', name: 'Bounded rescaling (log)',
      formula: 'x_norm = log10(x / x_min) / log10(x_max / x_min)',
      applies: 'voltage class' },
    { id: 'D', name: 'Categorical mapping',
      formula: 'x_norm = lookup[x] where lookup maps ordinal → [0,1]',
      applies: 'corrosion class, criticality class' }
  ];

  function meta() {
    return window.SSIMetadata || window.SSI_METADATA || {};
  }

  function getComponents() {
    var m = meta();
    return (Array.isArray(m.COMPONENTS) && m.COMPONENTS.length) ? m.COMPONENTS : DEFAULT_COMPONENTS;
  }

  function getNormMethods() {
    var m = meta();
    return (Array.isArray(m.NORM_METHODS) && m.NORM_METHODS.length) ? m.NORM_METHODS : DEFAULT_NORM_METHODS;
  }

  function getDataLayers() {
    var m = meta();
    return Array.isArray(m.DATA_LAYERS) ? m.DATA_LAYERS : [];
  }

  function getDataSources() {
    var m = meta();
    return Array.isArray(m.DATA_SOURCES) ? m.DATA_SOURCES : [];
  }

  function getValidationChecks() {
    var m = meta();
    return Array.isArray(m.VALIDATION_CHECKS) ? m.VALIDATION_CHECKS : [];
  }

  function getChangelog() {
    var m = meta();
    return Array.isArray(m.CHANGELOG) ? m.CHANGELOG : [];
  }

  /* ── Helpers ─────────────────────────────────────────────────────────── */
  function fmtNum(v, dp) { return Safe.fmt(v, dp); }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country, page, doc}
     ssi-data.json is already loaded + normalized by CountryRenderer.init,
     but methodology sections are purely metadata-driven (no ssi-data lookups).
     ══════════════════════════════════════════════════════════════════════ */

  /* ── 1. Metric Detail — 6 components × N metrics (intra/global weights) ── */
  CR.register('methodology', 'metrics-detail', function (ctx) {
    var detailEl = document.getElementById('method-metrics-detail');
    if (!detailEl) return;
    var components = getComponents();

    var html = '<div class="card-header"><h3>Metric Detail — 20 Metrics</h3></div>';
    components.forEach(function (comp) {
      var weight = (typeof comp.weight === 'number') ? comp.weight : 0;
      html += '<div style="margin:16px 0 8px">' +
              '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:' +
              (comp.color || '#888') + ';margin-right:6px"></span>' +
              '<strong style="color:' + (comp.color || '#888') + '">' + (comp.id || '') + '</strong> ' +
              (comp.name || '') + ' — <strong>' + weight.toFixed(2) + '</strong>';
      if (comp.isNew) {
        html += ' <span style="font-size:10px;color:#0e7490;background:#e0f7fa;padding:1px 6px;border-radius:2px;font-weight:600">NEW v4.0</span>';
      }
      html += '</div>';
      html += '<table class="data-table" style="margin-bottom:12px">' +
              '<thead><tr><th>Metric</th><th style="text-align:right">Intra</th>' +
              '<th style="text-align:right">Global</th><th>Norm</th><th>Source</th></tr></thead><tbody>';
      var metrics = Array.isArray(comp.metrics) ? comp.metrics : [];
      metrics.forEach(function (mt) {
        var intra = (typeof mt.intra === 'number') ? mt.intra : 0;
        var glob = (typeof mt.global === 'number') ? mt.global : 0;
        html += '<tr' + (mt.isNew ? ' style="background:#e0f7fa11"' : '') + '>';
        html += '<td><strong>' + (mt.id || '') + '</strong> ' + (mt.name || '');
        if (mt.isNew)    html += ' <span style="font-size:9px;color:#0e7490;font-weight:600">NEW</span>';
        if (mt.inverted) html += ' <span style="font-size:9px;color:var(--sage);font-weight:600">↓INV</span>';
        if (mt.adaptive) html += ' <span style="font-size:9px;color:var(--terracotta);font-weight:600">R2</span>';
        html += '</td>';
        html += '<td class="num">' + intra.toFixed(intra < 0.1 ? 3 : 2) + '</td>';
        html += '<td class="num">' + glob.toFixed(3) + '</td>';
        html += '<td style="font-size:11px">' + (mt.norm || '') + '</td>';
        html += '<td style="font-size:11px;color:var(--warm-grey)">' + (mt.source || '') + '</td>';
        html += '</tr>';
      });
      html += '</tbody></table>';
    });
    detailEl.innerHTML = html;
  });

  /* ── 2. Normalisation methods card body ─────────────────────────────── */
  CR.register('methodology', 'norm-methods', function (ctx) {
    var normEl = document.getElementById('method-norm');
    if (!normEl) return;
    var methods = getNormMethods();
    normEl.innerHTML = methods.map(function (n) {
      return '<div style="margin-bottom:12px;padding:12px 16px;background:var(--cream);' +
             'border-radius:var(--radius-sm);border-left:2px solid var(--terracotta)">' +
             '<div style="font-weight:600;font-size:13px;margin-bottom:4px">Method ' +
             (n.id || '') + ' — ' + (n.name || '') + '</div>' +
             '<div class="formula-block" style="margin:8px 0;padding:8px 12px;font-size:12px">' +
             (n.formula || '') + '</div>' +
             '<div style="font-size:11px;color:var(--warm-grey)">Applies to: ' +
             (n.applies || '') + '</div>' +
             '</div>';
    }).join('');
  });

  /* ── 3. Data Layers table ────────────────────────────────────────────── */
  CR.register('methodology', 'data-layers', function (ctx) {
    var tbody = document.querySelector('#method-layers tbody');
    if (!tbody) return;
    var layers = getDataLayers();
    var totalVars = 0;
    var rows = layers.map(function (l) {
      var status = l.status || '';
      var statusColor = status === 'LIVE'      ? 'var(--sage)' :
                        status.indexOf('NEW') !== -1 ? '#0e7490' : 'var(--bronze)';
      var vars = (typeof l.vars === 'number') ? l.vars : 0;
      totalVars += vars;
      return '<tr' + (l.isNew ? ' style="background:#e0f7fa11"' : '') + '>' +
             '<td><strong>' + (l.id || '') + '</strong> ' + (l.name || '') + '</td>' +
             '<td class="num">' + vars + '</td>' +
             '<td style="font-size:11px;font-weight:600;color:' + statusColor + '">' + status + '</td>' +
             '<td style="font-size:11px;color:var(--warm-grey)">' + (l.sources || '') + '</td></tr>';
    }).join('');
    var totalLabel = totalVars > 0 ? totalVars : 95;
    rows += '<tr style="border-top:2px solid var(--ink)">' +
            '<td><strong>Total</strong></td>' +
            '<td class="num"><strong>' + totalLabel + '</strong></td>' +
            '<td colspan="2"></td></tr>';
    tbody.innerHTML = rows;
  });

  /* ── 4. Data Sources table ───────────────────────────────────────────── */
  CR.register('methodology', 'data-sources', function (ctx) {
    var tbody = document.querySelector('#method-sources tbody');
    if (!tbody) return;
    var sources = getDataSources();
    tbody.innerHTML = sources.map(function (s) {
      return '<tr><td style="font-size:12px"><strong>' + (s.name || '') + '</strong>' +
             (s.registration ? ' <span style="font-size:9px;color:var(--terracotta)">⚠ registration</span>' : '') +
             '</td><td style="font-size:11px">' + (s.category || '') + '</td>' +
             '<td style="font-size:11px">' + (s.freq || '') + '</td>' +
             '<td style="font-size:11px">' + (s.res || '') + '</td>' +
             '<td class="num">' + (s.vars != null ? s.vars : '') + '</td>' +
             '<td style="font-size:11px;color:var(--warm-grey)">' + (s.feeds || '') + '</td></tr>';
    }).join('');
  });

  /* ── 5. Validation Framework table + count ──────────────────────────── */
  CR.register('methodology', 'validation', function (ctx) {
    var tbody = document.querySelector('#method-validation tbody');
    var count = document.getElementById('method-val-count');
    if (!tbody) return;
    var checks = getValidationChecks();
    tbody.innerHTML = checks.map(function (v) {
      var status = v.status || '';
      var statusIcon  = status === 'verified' ? '✓' :
                       status === 'expected' ? '✓ expected' : '⏳ new';
      var statusColor = status === 'verified' ? 'var(--sage)' :
                        status === 'expected' ? 'var(--sage)' : '#0e7490';
      return '<tr' + (v.isNew ? ' style="background:#e0f7fa11"' : '') + '>' +
             '<td style="font-weight:500">' + (v.check || '') + '</td>' +
             '<td style="font-size:12px">' + (v.criterion || '') + '</td>' +
             '<td style="font-size:12px;font-weight:600;color:' + statusColor + '">' + statusIcon + '</td></tr>';
    }).join('');
    if (count) count.textContent = checks.length + ' checks';
  });

  /* ── 6. Changelog table ─────────────────────────────────────────────── */
  CR.register('methodology', 'changelog', function (ctx) {
    var tbody = document.querySelector('#method-changelog tbody');
    if (!tbody) return;
    var entries = getChangelog();
    var typeColors = { new: '#0e7490', enhanced: 'var(--terracotta)', data: 'var(--bronze)' };
    tbody.innerHTML = entries.map(function (c) {
      var t = c.type || '';
      var col = typeColors[t] || 'var(--ink)';
      return '<tr><td style="font-family:monospace;font-weight:600">' + (c.id || '') + '</td>' +
             '<td style="font-size:12px">' + (c.change || '') + '</td>' +
             '<td><span style="font-size:10px;font-weight:600;color:' + col +
             ';background:' + col + '15;padding:1px 8px;border-radius:2px">' +
             (t ? t.toUpperCase() : '') + '</span></td></tr>';
    }).join('');
  });

})();
