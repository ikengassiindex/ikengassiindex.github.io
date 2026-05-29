/* ═══════════════════════════════════════════════════════════════════════════
   regional-sections.js — Phase 2d.2 (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Registers section renderers against CountryRenderer for the `regional`
   page. The shared rendering logic — Regional Ranking table, NUTS-3 region
   comparator (province dropdowns + radar chart + delta table), and the
   Component Decomposition stacked bars — lives here so every country's
   regional.html collapses to a thin-shell that calls:

       CountryRenderer.init('<country>', 'regional');

   Country-specific values live in `intelligence/country-configs/<slug>.json`:
     - `admin.l1.label_en` / `admin.l1.label_short`  — region label (e.g. 'NUTS-3 region')
     - `admin.l1.count`                              — region count
     - `regional_page.region_field`                  — name of the substation
                                                       field carrying the L1 region
                                                       label (defaults to `province`,
                                                       falling back to `region`)
     - `regional_page.fallback_region_field`         — secondary substation field
                                                       used when the primary field
                                                       is empty (defaults to `region`)
     - `regional_page.ranking_label`                 — header label suffix (default
                                                       falls back to `<plural label>
                                                       · sorted worst → best`)

   For countries that haven't been migrated yet, sensible defaults apply.

   Tab switching is owned by the HTML shell (lightweight inline helper). This
   file is exclusively concerned with data-driven section rendering against
   normalised ssi-data.json + country-configs/<slug>.json.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - ssi-metadata.js      (window.SSI_METADATA / window.SSIMetadata.*)
   No Chart.js dependency — the radar is drawn manually as inline SVG.

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[regional-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;
  var H = CR.H;
  var Safe = CR.Safe;  // SK hotfix #2 — KB §68.9

  /* ── Universal component palette (matches index-sections.js) ─────────── */
  var COMPONENT_DEFS = [
    { key: 'C', label: 'C Continuity',     color: 'var(--crimson)'    },
    { key: 'V', label: 'V Voltage',         color: 'var(--terracotta)' },
    { key: 'I', label: 'I Infrastructure',  color: 'var(--sage)'        },
    { key: 'E', label: 'E Economic',        color: '#3b9eff'             },
    { key: 'S', label: 'S Saturation',      color: 'var(--bronze)'      },
    { key: 'T', label: 'T Transition',      color: '#22d3ee'             }
  ];

  /* ── Defaults exposed for non-migrated countries ─────────────────────── */
  function getRegionLabel(cfg) {
    if (cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.label_en) {
      return cfg.admin.l1.label_en;
    }
    return 'region';
  }

  function getRegionLabelPlural(cfg) {
    var lbl = getRegionLabel(cfg);
    return /s$/i.test(lbl) ? lbl : lbl + 's';
  }

  function getRegionLabelTitle(cfg) {
    // Used in table headers — capitalise first letter and pluralise.
    var lbl = getRegionLabelPlural(cfg);
    return lbl.charAt(0).toUpperCase() + lbl.slice(1);
  }

  function getRegionFieldName(cfg) {
    if (cfg && cfg.regional_page && cfg.regional_page.region_field) {
      return cfg.regional_page.region_field;
    }
    return 'province';
  }

  function getFallbackRegionFieldName(cfg) {
    if (cfg && cfg.regional_page && cfg.regional_page.fallback_region_field) {
      return cfg.regional_page.fallback_region_field;
    }
    return 'region';
  }

  /* ── Colour helpers ──────────────────────────────────────────────────── */
  function scoreColor(val) {
    if (val == null || isNaN(val)) return 'var(--warm-grey)';
    if (val >= 0.75) return 'var(--crimson)';
    if (val >= 0.50) return 'var(--terracotta)';
    if (val >= 0.25) return 'var(--bronze)';
    return 'var(--sage)';
  }

  function deltaColor(d) {
    if (d > 0.01) return 'var(--crimson)';
    if (d < -0.01) return 'var(--sage)';
    return 'var(--warm-grey)';
  }

  // Thin pass-throughs to centralised Safe.* helpers (KB §68.9). Kept as
  // free functions so existing call sites stay one-liners.
  function fmt(v, dp) { return Safe.fmt(v, dp); }
  function pct(v)     { return Safe.pct(v, 1); }

  /* ── Province aggregate builder (shared by tabs 2 and 3) ─────────────── */
  function buildRegionAggregates(data, cfg) {
    var subs = (data && data.substations) || [];
    var primaryField = getRegionFieldName(cfg);
    var fallbackField = getFallbackRegionFieldName(cfg);
    var map = {};

    subs.forEach(function (s) {
      var pf = s[primaryField];
      var ff = s[fallbackField];
      var name = (pf != null && pf !== '') ? pf : ((ff != null && ff !== '') ? ff : '—');
      if (!map[name]) {
        map[name] = {
          province: name,
          region: s[fallbackField] || name,
          subs: []
        };
      }
      map[name].subs.push(s);
    });

    Object.keys(map).forEach(function (p) {
      var arr = map[p].subs;
      var n = arr.length;
      if (!n) return;
      arr.sort(function (a, b) { return (a.R_median || 0) - (b.R_median || 0); });
      var mid = Math.floor(n / 2);
      map[p].median_R = n % 2
        ? arr[mid].R_median
        : ((arr[mid - 1].R_median || 0) + (arr[mid].R_median || 0)) / 2;
      map[p].count = n;

      var comps = { C: 0, V: 0, I: 0, E: 0, S: 0, T: 0 };
      var mods = { R3: 0, R4: 0, R6a: 0, R6b: 0, R7: 0 };
      var epSum = 0, degSum = 0;
      arr.forEach(function (s) {
        var c = s.components || {};
        Object.keys(comps).forEach(function (k) { comps[k] += Number(c[k] || 0); });
        var m = s.modifiers || {};
        mods.R3 += Number(m.R3_C_mult || 0);
        mods.R4 += Number(m.R4_F_topo || 0);
        mods.R6a += Number(m.R6_restoration || 0);
        mods.R6b += Number(m.R6_seismic != null ? m.R6_seismic : 1.0);
        mods.R7 += Number(m.R7_cyber || 0);
        var se = s.socio_economic || {};
        epSum += Number(se.EP_rate_region != null ? se.EP_rate_region : (se.unemployment_rate || 0));
        var gt = s.graph_topology || {};
        degSum += Number(gt.degree || 0);
      });
      Object.keys(comps).forEach(function (k) { comps[k] /= n; });
      Object.keys(mods).forEach(function (k) { mods[k] /= n; });
      map[p].components = comps;
      map[p].modifiers = mods;
      map[p].EP_rate = epSum / n;
      map[p].avg_degree = degSum / n;
    });

    return map;
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country, page, doc}
     ssi-data.json is already loaded + normalised by CountryRenderer.init.
     ══════════════════════════════════════════════════════════════════════ */

  /* ── Tab 1: Regional Ranking ─────────────────────────────────────────── */
  CR.register('regional', 'ranking', function (ctx) {
    var data = ctx.data || {};
    var cfg = ctx.config || {};
    var regions = (data.regions || []).slice();
    if (!regions.length) return;

    regions.sort(function (a, b) { return (b.median_R || 0) - (a.median_R || 0); });

    var rankingLabel;
    if (cfg && cfg.regional_page && cfg.regional_page.ranking_label) {
      rankingLabel = regions.length + ' ' + cfg.regional_page.ranking_label;
    } else {
      var labelTitle = getRegionLabelTitle(cfg);
      rankingLabel = regions.length + ' ' + labelTitle + ' · sorted worst → best';
    }
    H.setText('ranking-count', rankingLabel);

    var tbody = document.getElementById('ranking-tbody');
    if (!tbody) return;

    tbody.innerHTML = regions.map(function (r, i) {
      var total = r.count || 0;
      var bands = r.bands || {};
      var pLow  = total ? ((bands.Low      || 0) / total * 100).toFixed(0) : 0;
      var pMed  = total ? ((bands.Medium   || 0) / total * 100).toFixed(0) : 0;
      var pHigh = total ? ((bands.High     || 0) / total * 100).toFixed(0) : 0;
      var pCrit = total ? ((bands.Critical || 0) / total * 100).toFixed(0) : 0;
      var displayName = (r.name && r.name !== r.region) ? r.name : (r.region || '—');
      return '<tr>' +
        '<td style="color:var(--warm-grey)">' + (i + 1) + '</td>' +
        '<td style="font-weight:500">' + displayName + '</td>' +
        '<td class="num" style="color:' + scoreColor(r.median_R) + ';font-weight:600">' + fmt(r.median_R) + '</td>' +
        '<td class="num">' + total + '</td>' +
        '<td class="num">' + pct(r.pct_critical) + '</td>' +
        '<td class="num">' + pct(r.pct_high) + '</td>' +
        '<td><div class="dist-bar" style="margin:0;width:140px;height:6px">' +
          '<div style="width:' + pLow + '%;background:var(--band-low)"></div>' +
          '<div style="width:' + pMed + '%;background:var(--band-medium)"></div>' +
          '<div style="width:' + pHigh + '%;background:var(--band-high)"></div>' +
          '<div style="width:' + pCrit + '%;background:var(--band-critical)"></div>' +
        '</div></td></tr>';
    }).join('');
  });

  /* ── Tab 2: Region Comparator (selects + delta table + radar) ────────── */
  CR.register('regional', 'comparator', function (ctx) {
    var data = ctx.data || {};
    var cfg = ctx.config || {};
    var provinceData = buildRegionAggregates(data, cfg);
    var names = Object.keys(provinceData).sort();
    if (!names.length) return;

    var selA = document.getElementById('prov-a');
    var selB = document.getElementById('prov-b');
    if (!selA || !selB) return;

    var html = names.map(function (p) {
      return '<option value="' + p + '">' + p + ' (' + provinceData[p].count + ')</option>';
    }).join('');
    selA.innerHTML = html;
    selB.innerHTML = html;

    // Smart defaults: worst NUTS-3 region in A, best in B.
    var sorted = names.slice().sort(function (a, b) {
      return (provinceData[b].median_R || 0) - (provinceData[a].median_R || 0);
    });
    selA.value = sorted[0] || names[0];
    selB.value = sorted[sorted.length - 1] || names[0];

    function updateComparison() {
      var nameA = selA.value;
      var nameB = selB.value;
      var a = provinceData[nameA];
      var b = provinceData[nameB];
      if (!a || !b) return;

      H.setText('th-prov-a', nameA);
      H.setText('th-prov-b', nameB);

      var rows = [];
      function addRow(label, va, vb, formatter, unit) {
        var fva = formatter ? formatter(va) : fmt(va);
        var fvb = formatter ? formatter(vb) : fmt(vb);
        var delta = (va || 0) - (vb || 0);
        var fdelta;
        if (unit === 'pp') fdelta = (delta >= 0 ? '+' : '') + delta.toFixed(1) + 'pp';
        else if (unit === 'int') fdelta = (delta >= 0 ? '+' : '') + delta.toFixed(0);
        else fdelta = (delta >= 0 ? '+' : '') + fmt(delta);
        var dc = deltaColor(delta);
        rows.push('<tr><td' + (label === 'Median R' ? ' style="font-weight:500"' : '') + '>' + label + '</td>' +
          '<td class="num" style="color:' + scoreColor(va) + ';font-weight:' + (label === 'Median R' ? '600' : '400') + '">' + fva + '</td>' +
          '<td class="num" style="color:' + scoreColor(vb) + ';font-weight:' + (label === 'Median R' ? '600' : '400') + '">' + fvb + '</td>' +
          '<td class="num" style="color:' + dc + '">' + fdelta + '</td></tr>');
      }

      addRow('Median R', a.median_R, b.median_R);
      addRow('C Continuity',     a.components.C, b.components.C);
      addRow('I Infrastructure', a.components.I, b.components.I);
      addRow('S Saturation',     a.components.S, b.components.S);
      addRow('V Voltage',        a.components.V, b.components.V);
      addRow('E Economic',       a.components.E, b.components.E);
      addRow('T Transition',     a.components.T, b.components.T);

      rows.push('<tr style="border-top:2px solid var(--card-border)"></tr>');
      addRow('Unemployment Rate', a.EP_rate, b.EP_rate, pct, 'pp');
      addRow('Avg Graph Degree', a.avg_degree, b.avg_degree, function (v) { return (v == null || isNaN(v)) ? '—' : Number(v).toFixed(1); }, 'int');
      addRow('Substations', a.count, b.count, function (v) { return (v == null || isNaN(v)) ? '—' : Number(v).toFixed(0); }, 'int');

      H.setHTML('compare-tbody', rows.join(''));
      drawRadar(a, b, nameA, nameB);
    }

    selA.addEventListener('change', updateComparison);
    selB.addEventListener('change', updateComparison);
    updateComparison();
  });

  /* ── SVG Radar Chart (used by the comparator) ────────────────────────── */
  function drawRadar(a, b, nameA, nameB) {
    var svg = document.getElementById('radar-svg');
    if (!svg) return;
    var cx = 140, cy = 120, R = 100;
    var comps = ['C', 'V', 'I', 'E', 'S', 'T'];

    var maxVal = 0;
    comps.forEach(function (k) {
      maxVal = Math.max(maxVal, a.components[k] || 0, b.components[k] || 0);
    });
    maxVal = Math.max(maxVal, 0.05);

    function polar(i, val) {
      var angle = (Math.PI * 2 * i / 6) - Math.PI / 2;
      var r = (1 - (val || 0) / maxVal) * R;
      return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
    }

    var html = '';
    [0.33, 0.66, 1.0].forEach(function (frac) {
      var pts = [];
      for (var i = 0; i < 6; i++) {
        var angle = (Math.PI * 2 * i / 6) - Math.PI / 2;
        pts.push((cx + frac * R * Math.cos(angle)).toFixed(1) + ',' + (cy + frac * R * Math.sin(angle)).toFixed(1));
      }
      html += '<polygon points="' + pts.join(' ') + '" fill="none" stroke="rgba(44,36,32,0.08)" stroke-width="1"/>';
    });

    for (var i = 0; i < 6; i++) {
      var angle = (Math.PI * 2 * i / 6) - Math.PI / 2;
      var x2 = cx + R * Math.cos(angle);
      var y2 = cy + R * Math.sin(angle);
      html += '<line x1="' + cx + '" y1="' + cy + '" x2="' + x2.toFixed(1) + '" y2="' + y2.toFixed(1) + '" stroke="rgba(44,36,32,0.06)" stroke-width="1"/>';
    }

    var ptsA = comps.map(function (k, i) { var p = polar(i, a.components[k]); return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    html += '<polygon points="' + ptsA + '" fill="rgba(148,25,20,0.12)" stroke="var(--crimson)" stroke-width="1.5"/>';

    var ptsB = comps.map(function (k, i) { var p = polar(i, b.components[k]); return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    html += '<polygon points="' + ptsB + '" fill="rgba(93,133,99,0.12)" stroke="var(--sage)" stroke-width="1.5"/>';

    comps.forEach(function (k, i) {
      var pa = polar(i, a.components[k]);
      html += '<circle cx="' + pa[0].toFixed(1) + '" cy="' + pa[1].toFixed(1) + '" r="3" fill="var(--crimson)"/>';
      var pb = polar(i, b.components[k]);
      html += '<circle cx="' + pb[0].toFixed(1) + '" cy="' + pb[1].toFixed(1) + '" r="3" fill="var(--sage)"/>';
    });

    var labelOffset = 16;
    comps.forEach(function (k, i) {
      var angle = (Math.PI * 2 * i / 6) - Math.PI / 2;
      var lx = cx + (R + labelOffset) * Math.cos(angle);
      var ly = cy + (R + labelOffset) * Math.sin(angle);
      var anchor = 'middle';
      if (lx < cx - 10) anchor = 'end';
      else if (lx > cx + 10) anchor = 'start';
      html += '<text x="' + lx.toFixed(1) + '" y="' + (ly + 4).toFixed(1) + '" text-anchor="' + anchor + '" font-size="11" fill="var(--warm-grey)" font-family="DM Sans" font-weight="500">' + k + '</text>';
    });

    html += '<text x="' + (cx + 4) + '" y="' + (cy - R - 6) + '" font-size="9" fill="var(--warm-grey-light)" font-family="DM Sans">0 (best)</text>';
    html += '<text x="' + (cx + 4) + '" y="' + (cy + 6) + '" font-size="9" fill="var(--warm-grey-light)" font-family="DM Sans">' + maxVal.toFixed(3) + '</text>';

    svg.innerHTML = html;

    H.setHTML('radar-legend',
      '<div style="display:flex;justify-content:center;gap:16px">' +
        '<div style="display:flex;align-items:center;gap:5px"><div style="width:12px;height:3px;background:var(--crimson);border-radius:2px"></div>' + nameA + '</div>' +
        '<div style="display:flex;align-items:center;gap:5px"><div style="width:12px;height:3px;background:var(--sage);border-radius:2px"></div>' + nameB + '</div>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--warm-grey);margin-top:6px;text-align:center">Larger area = lower risk = better resilience</div>');
  }

  /* ── Tab 3: Component Decomposition (stacked horizontal bars) ────────── */
  CR.register('regional', 'decomposition', function (ctx) {
    var data = ctx.data || {};
    var cfg = ctx.config || {};
    var fallbackField = getFallbackRegionFieldName(cfg);
    var subs = (data.substations || []);
    if (!subs.length) return;

    var regionMap = {};
    subs.forEach(function (s) {
      var region = s[fallbackField] || s.region || '—';
      if (!regionMap[region]) {
        regionMap[region] = { region: region, count: 0, C: 0, V: 0, I: 0, E: 0, S: 0, T: 0, R_sum: 0 };
      }
      var rm = regionMap[region];
      var c = s.components || {};
      rm.count++;
      rm.C += Number(c.C || 0);
      rm.V += Number(c.V || 0);
      rm.I += Number(c.I || 0);
      rm.E += Number(c.E || 0);
      rm.S += Number(c.S || 0);
      rm.T += Number(c.T || 0);
      rm.R_sum += Number(s.R_median || 0);
    });

    var regions = Object.keys(regionMap).map(function (k) {
      var rm = regionMap[k];
      var n = rm.count || 1;
      return {
        region: k,
        mean_R: rm.R_sum / n,
        C: rm.C / n, V: rm.V / n, I: rm.I / n,
        E: rm.E / n, S: rm.S / n, T: rm.T / n
      };
    }).sort(function (a, b) { return b.mean_R - a.mean_R; });

    if (!regions.length) return;

    var defs = COMPONENT_DEFS;

    var html = '<div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:11px;color:var(--warm-grey);padding-left:148px"><span>◀ Higher risk</span><span>Lower risk ▶</span></div>';
    html += regions.map(function (r) {
      var total = defs.reduce(function (a, d) { return a + (r[d.key] || 0); }, 0);
      if (total === 0) total = 1;
      var barWidth = Math.max(20, Math.min((1 - r.mean_R) * 100, 100));
      var segments = defs.map(function (d) {
        var w = (r[d.key] / total * 100).toFixed(1);
        return '<div style="width:' + w + '%;background:' + d.color + '" title="' + d.key + ': ' + r[d.key].toFixed(3) + '"></div>';
      }).join('');
      var displayName = (r.name && r.name !== r.region) ? r.name : r.region;
      return '<div style="margin-bottom:14px">' +
        '<div style="display:flex;align-items:center;margin-bottom:4px">' +
          '<span style="width:140px;font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">' + displayName + '</span>' +
          '<span style="margin-left:auto;font-size:11px;color:var(--warm-grey);font-variant-numeric:tabular-nums">' + r.mean_R.toFixed(3) + '</span>' +
        '</div>' +
        '<div style="display:flex;height:16px;border-radius:4px;overflow:hidden;width:' + barWidth.toFixed(0) + '%">' + segments + '</div>' +
      '</div>';
    }).join('');

    H.setHTML('decomp-bars', html);
  });

})();
