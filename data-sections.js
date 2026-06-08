/* ═══════════════════════════════════════════════════════════════════════════
   data-sections.js — Phase 2d.5 (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `data` page
   (Data & Download). The shared rendering logic — KPI counts, source-registry
   grid, engine info, PDF download wiring (4 generators), and the live schema
   sample — lives here so every country's data.html collapses to a thin-shell
   that calls:

       CountryRenderer.init('<country>', 'data');

   The static reference content (page header copy, Data Layers table, Engine
   Info card body) lives inline in the HTML shell — those blocks are either
   universal SSI v4.0.2 reference text or country-specific static rows that
   don't need JS to render.

   Country-specific values live in:
     - `<country>/ssi-metadata.js`
         · `window.SSI_METADATA.DATA_SOURCES` — feeds the source-registry grid
     - `intelligence/country-configs/<slug>.json`
         · `data_page.file_slug`        — embedded in PDF filenames
                                          (default: country slug)
         · `data_page.region_field`     — substation field carrying L1 region
                                          label for PDF tables (default 'region')
         · `data_page.region_label_short` — used in PDF table headers
                                          (default 'NUTS-3 Region')
         · `data_page.region_label_code`  — used in PDF table headers
                                          (default 'NUTS-3 Code')
         · `data_page.formula_pdf_layers` — replacement text for the Formula
                                          Construct PDF "Data Layers" section
                                          (default: universal SSI v4.0.2 text)
         · `data_page.formula_pdf_extra` — array of extra { title, text } blocks
                                          appended to the Formula Construct PDF

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - ssi-metadata.js      (window.SSI_METADATA.DATA_SOURCES)
     - nav.js               (provides requireRegistration() global)
     - jspdf + jspdf-autotable (CDN scripts in the HTML shell)
     - ssi-engine.js        (window.SSIEngine for the function-count tile)

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[data-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var Safe = CR.Safe;  // SK hotfix #2 — KB §68.9

  /* ── Source-registry icon + colour palette (keyed by `category`). ──────
       DATA_SOURCES entries lacking a `category` field fall back to the
       Standards icon/colour so the grid still renders. ──────────────── */
  var CAT_ICONS = {
    Grid: '⚡', Economic: '🏛️', 'Socio-Econ': '📊', Standards: '📐',
    Climate: '🌍', Infrastructure: '🗺️', Transition: '☀️',
    Hazard: '🌊', Environment: '🌡️'
  };
  var CAT_COLORS = {
    Grid: '148,25,20', Economic: '184,134,58', 'Socio-Econ': '93,133,99',
    Standards: '170,66,52', Climate: '59,158,255', Infrastructure: '34,211,238',
    Transition: '255,140,66', Hazard: '255,140,66', Environment: '170,66,52'
  };

  /* ── Universal SSI v4.0.2 Formula Construct PDF sections.
       Countries may override `data_page.formula_pdf_layers` (and append via
       `data_page.formula_pdf_extra`) to replace the data-layer narrative
       block with country-specific language. ──────────────────────────── */
  var DEFAULT_FORMULA_LAYERS_TEXT =
    'A — SSI v4.0 Resilience: asset age, condition, load factor, SAIDI/SAIFI\n' +
    'B.1 — Grid Telemetry Open: weather, regulator monitoring\n' +
    'B.2 — Grid Telemetry Proxy: thermal stress, transformer loading\n' +
    'B.3 — Grid Telemetry Fuzzy: IEEE/CIGRÉ degradation curves\n' +
    'C — Socio-Economic: income, energy poverty, digital readiness\n' +
    'D — Environmental Hazards: floods, landslides, corrosion, wildfire\n' +
    'E — National Open Data: regional regulator + open data feeds\n' +
    'F — Network Transitions: state transition probabilities\n' +
    'G — Modifier Inputs: regulator quality, topology, JRC DSO data\n' +
    'H — Network & Topology: TSO data, hazard catalogues, ring analysis\n' +
    'I — Output Scores: risk score, ETTC, stationary probabilities';

  function getFormulaSections(cfg) {
    var dp = (cfg && cfg.data_page) || {};
    var layersText = dp.formula_pdf_layers || DEFAULT_FORMULA_LAYERS_TEXT;
    var sections = [
      { title: 'SSI v4.0.2 Composite Formula',
        text: 'R = softclip( w_C·C + w_V·V + w_I·I + w_E·E + w_S·S + w_T·T ) × R3 × R4 × R6a × R6b × R7\n\nwhere softclip(x) = 1 / (1 + exp(-12·(x - 0.5))) compresses overflow beyond [0,1].' },
      { title: 'Component Weights',
        text: 'w_C = 0.30  Condition (asset health & age)\nw_V = 0.20  Vulnerability (exposure to hazards)\nw_I = 0.15  Importance (criticality & load)\nw_E = 0.15  Environment (socio-economic context)\nw_S = 0.10  Stress (DER penetration & grid strain)\nw_T = 0.10  Transition (energy transition readiness)' },
      { title: 'Modifier Functions',
        text: 'R3 — Consequence sigmoid: amplifies scores for high-consequence regions\nR4 — Graph criticality: betweenness centrality & bridge status from network topology\nR6a — Restoration speed: DSO historical MTTR or Bayesian estimate\nR6b — Network topology: Centrality and ring topology from physical network analysis\nR7 — Digital readiness: DESI digital index & smart meter penetration proxy' },
      { title: 'Monte Carlo Uncertainty',
        text: '10,000 iterations per substation, computed server-side by the canonical Python pipeline (scripts/pipeline/scoring/engine.py).\nNumpy-vectorized; 20×20 Gaussian copula correlation matrix via Cholesky decomposition preserves empirical correlations between metrics.\nPer-metric perturbation against the 20-metric SIGMA_TOTAL table:\n  Mean-shift error: zero (centred draws)\n  Per-metric σ: 0.13-0.45 depending on confidence tier (see SIGMA_TOTAL)\nOutputs persisted to ssi-data.json: R_median, R_P5, R_P95, CI_width, P_critical, skewness.\nBrowser-side MC retired (PR-4, audit memo 2026-06-08); ssi-engine.js now reads precomputed values.' },
      { title: 'Classification Bands',
        text: 'LOW risk: R_median < 0.35\nMEDIUM-LOW: 0.35 ≤ R < 0.45\nMEDIUM: 0.45 ≤ R < 0.55\nMEDIUM-HIGH: 0.55 ≤ R < 0.65\nHIGH risk: R_median ≥ 0.65' },
      { title: 'Data Layers (11 layers, 95 variables)',
        text: layersText },
      { title: 'Normalisation',
        text: 'All metrics normalised to [0, 1] using min-max scaling across the fleet.\nHigher score = higher risk. Inverted metrics (where high raw value = low risk) are flipped: x_norm = 1 - (x - min) / (max - min).' }
    ];
    if (Array.isArray(dp.formula_pdf_extra)) {
      dp.formula_pdf_extra.forEach(function (s) {
        if (s && s.title && s.text) sections.push({ title: s.title, text: s.text });
      });
    }
    return sections;
  }

  /* ── Helpers ─────────────────────────────────────────────────────────── */
  function meta() {
    return window.SSIMetadata || window.SSI_METADATA || {};
  }

  function getDataSources() {
    var m = meta();
    return Array.isArray(m.DATA_SOURCES) ? m.DATA_SOURCES : [];
  }

  function getFileSlug(country, cfg) {
    if (cfg && cfg.data_page && cfg.data_page.file_slug) return cfg.data_page.file_slug;
    if (cfg && cfg.slug) return cfg.slug;
    return country || 'country';
  }

  function getRegionField(cfg) {
    if (cfg && cfg.data_page && cfg.data_page.region_field) return cfg.data_page.region_field;
    if (cfg && cfg.regional_page && cfg.regional_page.region_field) return cfg.regional_page.region_field;
    return 'region';
  }

  function getRegionLabelShort(cfg) {
    if (cfg && cfg.data_page && cfg.data_page.region_label_short) return cfg.data_page.region_label_short;
    if (cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.label_short) return cfg.admin.l1.label_short + ' Region';
    return 'NUTS-3 Region';
  }

  function getRegionLabelCode(cfg) {
    if (cfg && cfg.data_page && cfg.data_page.region_label_code) return cfg.data_page.region_label_code;
    if (cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.label_short) return cfg.admin.l1.label_short + ' Code';
    return 'NUTS-3 Code';
  }

  // Substations can carry both `region` and `province` — the regional field
  // for the PDF tables defaults to `region`, but the "code" cell traditionally
  // shows the inverse. Allows config to flip the pair via region_field.
  function regionCellsFor(s, cfg) {
    var primary = getRegionField(cfg);
    var fallback = (cfg && cfg.regional_page && cfg.regional_page.fallback_region_field) ||
                   (primary === 'region' ? 'province' : 'region');
    return {
      code: s[primary] != null ? s[primary] : (s[fallback] != null ? s[fallback] : ''),
      name: s[fallback] != null ? s[fallback] : (s[primary] != null ? s[primary] : '')
    };
  }

  function safeRequireRegistration(cb) {
    // nav.js exposes this as a global; if it's missing, fall through (no gate).
    if (typeof window.requireRegistration === 'function') {
      return window.requireRegistration(cb);
    }
    return true;
  }

  function num(v, dp) {
    return (v == null || isNaN(v)) ? 0 : Number(v);
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country, page, doc}
     ssi-data.json is already loaded + normalized by CountryRenderer.init.
     ══════════════════════════════════════════════════════════════════════ */

  /* ── 1. KPI counters — substations / region count / dl-full info ─────── */
  CR.register('data', 'kpi-counts', function (ctx) {
    var subs = (ctx.data && ctx.data.substations) || [];
    var regs = (ctx.data && ctx.data.regions) || [];
    var n = subs.length;
    var nStr = n.toLocaleString();
    var regionLabel = (ctx.config && ctx.config.admin && ctx.config.admin.l1 && ctx.config.admin.l1.label_en) || 'NUTS-3';
    var regionPlural = /s$/i.test(regionLabel) ? regionLabel : regionLabel + 's';

    var subsEl = document.getElementById('data-subs');
    if (subsEl) subsEl.textContent = nStr;
    var subsSubEl = document.getElementById('data-subs-sub');
    if (subsSubEl) subsSubEl.textContent = nStr + ' substations · ' + regs.length + ' ' + regionPlural;
    var dlFullInfo = document.getElementById('dl-full-info');
    if (dlFullInfo) dlFullInfo.textContent = nStr + ' substations · all fields';
  });

  /* ── 2. Source-Registry grid (#data-source-grid) ─────────────────────── */
  CR.register('data', 'source-grid', function (ctx) {
    var grid = document.getElementById('data-source-grid');
    if (!grid) return;
    var sources = getDataSources();
    grid.innerHTML = sources.map(function (s) {
      var cat = s.category || 'Standards';
      var c = CAT_COLORS[cat] || '93,133,99';
      var icon = CAT_ICONS[cat] || '📊';
      var vars = (s.vars != null) ? s.vars : 0;
      var freq = s.freq || '';
      var name = s.name || '';
      var warn = s.registration ? ' <span style="font-size:9px;color:var(--terracotta)">⚠</span>' : '';
      return '<div class="source-card">' +
        '<div class="source-icon" style="background:rgba(' + c + ',0.1)">' + icon + '</div>' +
        '<div class="source-meta"><div class="source-name">' + name + warn + '</div>' +
        '<div class="source-detail">' + vars + ' variable' + (vars > 1 ? 's' : '') +
        (freq ? ' · ' + freq : '') + '</div></div></div>';
    }).join('');
  });

  /* ── 3. Engine info — public API function count ─────────────────────── */
  CR.register('data', 'engine-info', function (ctx) {
    var engEl = document.getElementById('engine-fns');
    if (engEl && window.SSIEngine) {
      engEl.textContent = Object.keys(window.SSIEngine).length;
    }
  });

  /* ── 4. PDF download wiring (4 buttons, registration-gated) ──────────── */
  CR.register('data', 'pdf-downloads', function (ctx) {
    if (!window.jspdf || !window.jspdf.jsPDF) {
      console.warn('[data-sections] jsPDF not loaded — PDF buttons inert');
      return;
    }
    var jsPDF = window.jspdf.jsPDF;
    var data = ctx.data || {};
    var subs = data.substations || [];
    var n = subs.length;
    var cfg = ctx.config || {};
    var slug = getFileSlug(ctx.country, cfg);
    var fnPrefix = 'ssi-index-v402-' + slug;
    var regionLabelShort = getRegionLabelShort(cfg);
    var regionLabelCode = getRegionLabelCode(cfg);

    function pdfHeader(doc, title, subtitle) {
      doc.setFillColor(148, 25, 20);
      doc.rect(0, 0, doc.internal.pageSize.width, 32, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);
      doc.text('SSI Index v4.0.2', 14, 14);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(title, 14, 22);
      if (subtitle) {
        doc.setFontSize(8);
        doc.text(subtitle, 14, 28);
      }
      doc.setTextColor(0, 0, 0);
      return 40;
    }

    function pdfFooter(doc) {
      var pageCount = doc.internal.getNumberOfPages();
      for (var i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(7);
        doc.setTextColor(150, 150, 150);
        doc.text(
          'SSI Index v4.0.2 · © 2026 Altinium Invest S.r.L. · Page ' + i + '/' + pageCount,
          doc.internal.pageSize.width / 2, doc.internal.pageSize.height - 8, { align: 'center' }
        );
      }
    }

    /* ── Full Dataset PDF ── */
    var dlFull = document.getElementById('dl-full');
    if (dlFull) {
      dlFull.addEventListener('click', function () {
        function doFullPDF() {
          var doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
          var y = pdfHeader(doc, 'Full Dataset Export',
            n.toLocaleString() + ' substations · Generated ' + new Date().toLocaleDateString());

          doc.autoTable({
            startY: y,
            styles: { fontSize: 5.5, cellPadding: 1.5 },
            headStyles: { fillColor: [148, 25, 20], textColor: 255, fontSize: 6 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [['ID', 'Name', regionLabelCode, regionLabelShort, 'kV', 'R_med', 'R_P5', 'R_P95', 'CI', 'Band', 'Pct', 'C', 'V', 'I', 'E', 'S', 'T', 'R3', 'R4', 'R6a', 'R6b', 'R7', 'Network', 'Output', 'Tier']],
            body: subs.map(function (s) {
              var rc = regionCellsFor(s, cfg);
              var comp = s.components || {};
              var mods = s.modifiers || {};
              return [
                s.internal_id || '', Safe.displayName(s), rc.code, rc.name,
                s.voltage_kv != null ? s.voltage_kv : '',
                Safe.fmt(s.R_median, 3), Safe.fmt(s.R_P5, 3),
                Safe.fmt(s.R_P95, 3), Safe.fmt(s.CI_width, 3),
                s.classification || '', Safe.fmt(num(s.fleet_percentile) * 100, 0) + '%',
                num(comp.C).toFixed(2), num(comp.V).toFixed(2), num(comp.I).toFixed(2),
                num(comp.E).toFixed(2), num(comp.S).toFixed(2), num(comp.T).toFixed(2),
                num(mods.R3_C_mult).toFixed(2), num(mods.R4_F_topo).toFixed(2),
                num(mods.R6_restoration).toFixed(2), num(mods.R6_seismic || 1.0).toFixed(2),
                num(mods.R7_cyber).toFixed(2),
                s.network ? s.network.topology : '-',
                s.markov ? num(s.markov.risk_score).toFixed(2) : '-',
                s.confidence_tier
              ];
            }),
            margin: { left: 8, right: 8 }
          });

          pdfFooter(doc);
          doc.save(fnPrefix + '-full-dataset.pdf');
        }
        if (!safeRequireRegistration(doFullPDF)) return;
        doFullPDF();
      });
    }

    /* ── Summary Report PDF ── */
    var dlSummary = document.getElementById('dl-summary');
    if (dlSummary) {
      dlSummary.addEventListener('click', function () {
        function doSummaryPDF() {
          var doc = new jsPDF({ unit: 'mm', format: 'a4' });
          var y = pdfHeader(doc, 'Summary Report',
            'Fleet overview · Generated ' + new Date().toLocaleDateString());

          // Band distribution
          var bands = {};
          subs.forEach(function (s) { bands[s.classification] = (bands[s.classification] || 0) + 1; });
          doc.setFontSize(11); doc.setFont('helvetica', 'bold');
          doc.text('Classification Distribution', 14, y); y += 6;

          doc.autoTable({
            startY: y,
            styles: { fontSize: 9, cellPadding: 3 },
            headStyles: { fillColor: [148, 25, 20], textColor: 255 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [['Band', 'Count', 'Share']],
            body: Object.keys(bands).sort().map(function (b) {
              return [b, bands[b], (bands[b] / n * 100).toFixed(1) + '%'];
            }),
            margin: { left: 14, right: 14 }
          });
          y = doc.lastAutoTable.finalY + 10;

          // Regional summary
          doc.setFontSize(11); doc.setFont('helvetica', 'bold');
          doc.text('Regional Summary', 14, y); y += 6;

          var regField = getRegionField(cfg);
          var regData = {};
          subs.forEach(function (s) {
            var rkey = s[regField] || s.region || '';
            if (!regData[rkey]) regData[rkey] = { sum: 0, count: 0, min: 1, max: 0 };
            regData[rkey].sum += num(s.R_median);
            regData[rkey].count++;
            if (num(s.R_median) < regData[rkey].min) regData[rkey].min = num(s.R_median);
            if (num(s.R_median) > regData[rkey].max) regData[rkey].max = num(s.R_median);
          });

          doc.autoTable({
            startY: y,
            styles: { fontSize: 8, cellPadding: 2.5 },
            headStyles: { fillColor: [148, 25, 20], textColor: 255 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [[regionLabelShort, 'Substations', 'Mean R', 'Min R', 'Max R']],
            body: Object.keys(regData).sort().map(function (r) {
              var d = regData[r];
              return [r, d.count, (d.sum / d.count).toFixed(3), d.min.toFixed(3), d.max.toFixed(3)];
            }),
            margin: { left: 14, right: 14 }
          });
          y = doc.lastAutoTable.finalY + 10;

          // Top/bottom substations
          var sorted = subs.slice().sort(function (a, b) {
            return num(a.R_median) - num(b.R_median);
          });

          doc.setFontSize(11); doc.setFont('helvetica', 'bold');
          doc.text('Top 20 Most Resilient Substations', 14, y); y += 6;
          doc.autoTable({
            startY: y,
            styles: { fontSize: 8, cellPadding: 2 },
            headStyles: { fillColor: [93, 133, 99], textColor: 255 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [['#', 'Name', regionLabelShort, 'kV', 'R_median', 'Band']],
            body: sorted.slice(0, 20).map(function (s, i) {
              var rc = regionCellsFor(s, cfg);
              return [i + 1, Safe.displayName(s), rc.code,
                s.voltage_kv != null ? s.voltage_kv : '',
                Safe.fmt(s.R_median, 4), s.classification || ''];
            }),
            margin: { left: 14, right: 14 }
          });
          y = doc.lastAutoTable.finalY + 10;

          if (y > 240) { doc.addPage(); y = 20; }
          doc.setFontSize(11); doc.setFont('helvetica', 'bold');
          doc.text('Top 20 Most Vulnerable Substations', 14, y); y += 6;
          doc.autoTable({
            startY: y,
            styles: { fontSize: 8, cellPadding: 2 },
            headStyles: { fillColor: [170, 66, 52], textColor: 255 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [['#', 'Name', regionLabelShort, 'kV', 'R_median', 'Band']],
            body: sorted.slice(-20).reverse().map(function (s, i) {
              var rc = regionCellsFor(s, cfg);
              return [i + 1, Safe.displayName(s), rc.code,
                s.voltage_kv != null ? s.voltage_kv : '',
                Safe.fmt(s.R_median, 4), s.classification || ''];
            }),
            margin: { left: 14, right: 14 }
          });

          pdfFooter(doc);
          doc.save(fnPrefix + '-summary-report.pdf');
        }
        if (!safeRequireRegistration(doSummaryPDF)) return;
        doSummaryPDF();
      });
    }

    /* ── Geographic Data PDF ── */
    var dlGeo = document.getElementById('dl-geo');
    if (dlGeo) {
      dlGeo.addEventListener('click', function () {
        function doGeoPDF() {
          var doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
          var y = pdfHeader(doc, 'Geographic Data Export',
            'Coordinates + SSI scores · Generated ' + new Date().toLocaleDateString());

          doc.autoTable({
            startY: y,
            styles: { fontSize: 6, cellPadding: 1.5 },
            headStyles: { fillColor: [148, 25, 20], textColor: 255, fontSize: 6.5 },
            alternateRowStyles: { fillColor: [252, 249, 244] },
            head: [['ID', 'Name', regionLabelCode, regionLabelShort, 'Longitude', 'Latitude', 'kV', 'R_median', 'Band', 'C', 'V', 'I', 'E', 'S', 'T']],
            body: subs.map(function (s) {
              var rc = regionCellsFor(s, cfg);
              var comp = s.components || {};
              return [
                s.internal_id || '', Safe.displayName(s), rc.code, rc.name,
                Safe.fmt(s.lon, 5), Safe.fmt(s.lat, 5),
                s.voltage_kv != null ? s.voltage_kv : '',
                Safe.fmt(s.R_median, 3), s.classification || '',
                Safe.fmt(comp.C, 2), Safe.fmt(comp.V, 2), Safe.fmt(comp.I, 2),
                Safe.fmt(comp.E, 2), Safe.fmt(comp.S, 2), Safe.fmt(comp.T, 2)
              ];
            }),
            margin: { left: 8, right: 8 }
          });

          pdfFooter(doc);
          doc.save(fnPrefix + '-geographic-data.pdf');
        }
        if (!safeRequireRegistration(doGeoPDF)) return;
        doGeoPDF();
      });
    }

    /* ── Formula Construct PDF ── */
    var dlFormula = document.getElementById('dl-formula');
    if (dlFormula) {
      dlFormula.addEventListener('click', function () {
        function doFormulaPDF() {
          var doc = new jsPDF({ unit: 'mm', format: 'a4' });
          var y = pdfHeader(doc, 'Formula Construct — Technical Reference',
            'SSI v4.0.2 complete specification');

          var sections = getFormulaSections(cfg);
          doc.setFontSize(9);
          sections.forEach(function (sec) {
            if (y > 260) { doc.addPage(); y = 20; }
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.setTextColor(148, 25, 20);
            doc.text(sec.title, 14, y); y += 6;
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(50, 50, 50);
            var lines = doc.splitTextToSize(sec.text, 180);
            doc.text(lines, 14, y);
            y += lines.length * 4.2 + 6;
          });

          pdfFooter(doc);
          doc.save(fnPrefix + '-formula-construct.pdf');
        }
        if (!safeRequireRegistration(doFormulaPDF)) return;
        doFormulaPDF();
      });
    }
  });

  /* ── 5. Live schema sample — mid-fleet substation JSON snippet ───────── */
  CR.register('data', 'schema-sample', function (ctx) {
    var block = document.getElementById('schema-block');
    if (!block) return;
    var subs = (ctx.data && ctx.data.substations) || [];
    if (!subs.length) {
      block.innerHTML = 'No fleet data available.';
      return;
    }
    var s = subs[Math.floor(subs.length / 2)];
    var comp = s.components || {};
    var mods = s.modifiers || {};
    var socio = s.socio_economic || {};
    var graph = s.graph_topology;
    var trans = s.transition || {};

    function nfmt(v, dp) {
      return (v == null || isNaN(v)) ? '—' : Number(v).toFixed(dp);
    }

    var schemaHTML = '{\n' +
      '  <span class="hl-var">"substation_id"</span>: <span class="hl-num">"' + (s.substation_id || '') + '"</span>,\n' +
      '  <span class="hl-var">"version"</span>: <span class="hl-num">"' + (s.version || '') + '"</span>,\n' +
      '  <span class="hl-var">"name"</span>: <span class="hl-num">"' + (s.name || '') + '"</span>,\n' +
      '  <span class="hl-var">"region"</span>: <span class="hl-num">"' + (s.region || '') + '"</span>,  ' +
        '<span class="hl-var">"province"</span>: <span class="hl-num">"' + (s.province || '') + '"</span>,\n' +
      '  <span class="hl-var">"R_median"</span>: <span class="hl-num">' + nfmt(s.R_median, 4) + '</span>,\n' +
      '  <span class="hl-var">"R_P5"</span>: <span class="hl-num">' + nfmt(s.R_P5, 4) + '</span>,  ' +
        '<span class="hl-var">"R_P95"</span>: <span class="hl-num">' + nfmt(s.R_P95, 4) + '</span>,\n' +
      '  <span class="hl-var">"classification"</span>: <span class="hl-num">"' + (s.classification || '') + '"</span>,\n' +
      '  <span class="hl-var">"fleet_percentile"</span>: <span class="hl-num">' + nfmt(s.fleet_percentile, 2) + '</span>,\n' +
      '  <span class="hl-var">"components"</span>: { ' +
        '<span class="hl-num">"C"</span>: ' + nfmt(comp.C, 3) + ', ' +
        '<span class="hl-num">"V"</span>: ' + nfmt(comp.V, 3) + ', ' +
        '<span class="hl-num">"I"</span>: ' + nfmt(comp.I, 3) + ', ' +
        '<span class="hl-num">"E"</span>: ' + nfmt(comp.E, 3) + ', ' +
        '<span class="hl-num">"S"</span>: ' + nfmt(comp.S, 3) + ', ' +
        '<span class="hl-num">"T"</span>: ' + nfmt(comp.T, 3) + ' },\n' +
      '  <span class="hl-var">"modifiers"</span>: { ' +
        '<span class="hl-num">"R3"</span>: ' + nfmt(mods.R3_C_mult, 3) + ', ' +
        '<span class="hl-num">"R4"</span>: ' + nfmt(mods.R4_F_topo, 3) + ', ' +
        '<span class="hl-num">"R6a"</span>: ' + nfmt(mods.R6_restoration, 3) + ', ' +
        '<span class="hl-num">"R6b"</span>: ' + nfmt(mods.R6_seismic != null ? mods.R6_seismic : 1.0, 3) + ', ' +
        '<span class="hl-num">"R7"</span>: ' + nfmt(mods.R7_cyber, 3) + ' },\n' +
      '  <span class="hl-var">"socio_economic"</span>: { ' +
        '<span class="hl-num">"population"</span>: ' + (socio.population || 0) + ', ' +
        '<span class="hl-num">"gdp_per_capita"</span>: ' + (socio.gdp_per_capita ? Number(socio.gdp_per_capita).toFixed(0) : '—') + ', ' +
        '<span class="hl-num">"unemployment_rate"</span>: ' + (socio.unemployment_rate ? Number(socio.unemployment_rate).toFixed(1) : '—') + ' },\n' +
      (graph ? '  <span class="hl-var">"graph_topology"</span>: { ' +
        '<span class="hl-num">"degree"</span>: ' + (graph.degree != null ? graph.degree : '—') + ', ' +
        '<span class="hl-num">"BC_pct"</span>: ' + nfmt(graph.BC_percentile, 2) + ', ' +
        '<span class="hl-num">"bridge"</span>: ' + (graph.is_bridge != null ? graph.is_bridge : '—') + ' },\n' : '') +
      '  <span class="hl-var">"transition"</span>: { ' +
        '<span class="hl-num">"T1_score"</span>: ' + (trans.T1_score != null ? Number(trans.T1_score).toFixed(3) : '—') + ', ' +
        '<span class="hl-num">"solar_mw"</span>: ' + (trans.solar_mw != null ? Number(trans.solar_mw).toFixed(1) : '—') + ', ' +
        '<span class="hl-num">"wind_mw"</span>: ' + (trans.wind_mw != null ? Number(trans.wind_mw).toFixed(1) : '—') + ' },\n' +
      '  <span class="hl-var">"confidence_tier"</span>: <span class="hl-num">"' + (s.confidence_tier || '') + '"</span>\n' +
      '}';
    block.innerHTML = schemaHTML;
  });

})();
