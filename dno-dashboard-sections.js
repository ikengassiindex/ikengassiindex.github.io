/* ═══════════════════════════════════════════════════════════════════════════
   dno-dashboard-sections.js — Phase 2d.6 (KB §65) — Thin-shell section handlers
   ───────────────────────────────────────────────────────────────────────────
   Final Phase 2d migration. Registers section renderers against
   CountryRenderer for the `dno-dashboard` page — the country-specific
   DSO segmented view (Slovenia: 5 Elektros; Czechia: 3 distributors;
   Belgium: 3; Netherlands: 7; Slovakia: 3; etc.). The page composition is
   universal, but the data plane is per-country and lives in:

       intelligence/country-configs/<slug>.json
         dno_dashboard: {
           subtitle:       "5 Elektro DSOs · ~1.0 M LV customers · …",
           intro:          "Slovenia's distribution is split across…",
           governance: [
             { label, value, sub },   // 4-tile KPI grid (TSO / Reg / Holding / Misc)
             …
           ],
           dsos: [
             { name, share_pct, customers, color, badge_bg, badge_color,
               coverage, hazard_notes },
             …
           ],
           saidi: {
             headline:      "Slovenia's national SAIDI (~38 min…",
             peers: [
               { country, saidi_min, notes, highlight: true|false }, …
             ]
           },
           notes: [
             { id: "nuclear" | "transition" | …,
               heading: "Krško NPP — Distribution-Side Impact",
               sub_heading: "Single-unit cascade risk",
               body: "Although Krško NPP is a transmission-level asset…" },
             …
           ]
         }

   Renderers fill the following containers (provided by the thin shell):
     #dno-subtitle            — page subtitle byline
     #dno-governance-grid     — 4× KPI tiles
     #dno-intro               — single-paragraph intro
     #dno-dso-grid            — N DSO cards
     #dno-saidi-headline      — SAIDI peer-table preamble paragraph
     #dno-saidi-table tbody   — peer rows
     #dno-notes               — N supplementary cards (nuclear, transition, …)

   Universal defaults (KB §65 anti-pattern A6 closure):
     - If cfg.dno_dashboard is absent → render a single-card "Single-DSO
       market — not applicable" message in #dno-dso-grid and hide the
       SAIDI + notes sections gracefully. Page never breaks.
     - If cfg.dno_dashboard.dsos.length < 2 → same fallback.

   Dependencies (loaded by the HTML shell):
     - country-renderer.js  (provides window.CountryRenderer)
     - ssi-metadata.js      (optional — used only for country-name flavour)

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[dno-dashboard-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;

  /* ── Helpers ─────────────────────────────────────────────────────────── */
  function getCfg(ctx) {
    return (ctx && ctx.config && ctx.config.dno_dashboard) || null;
  }

  function setText(id, text) {
    var el = document.getElementById(id);
    if (el && text != null) el.textContent = text;
  }

  function setHTML(id, html) {
    var el = document.getElementById(id);
    if (el != null) el.innerHTML = html;
  }

  function esc(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function hexToRgb(hex) {
    // Accepts '#rrggbb' or '#rgb'; returns 'r,g,b' string or null.
    if (!hex || typeof hex !== 'string') return null;
    var h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map(function (c) { return c + c; }).join('');
    if (h.length !== 6) return null;
    var r = parseInt(h.slice(0, 2), 16);
    var g = parseInt(h.slice(2, 4), 16);
    var b = parseInt(h.slice(4, 6), 16);
    if (isNaN(r) || isNaN(g) || isNaN(b)) return null;
    return r + ',' + g + ',' + b;
  }

  function countryNameFromCtx(ctx) {
    var cfg = ctx && ctx.config;
    if (cfg && cfg.country_name) return cfg.country_name;
    var c = ctx && ctx.country;
    if (!c) return '';
    return c.charAt(0).toUpperCase() + c.slice(1);
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATIONS — each receives ctx = {data, config, country,
     page, doc}. ssi-data.json is already loaded + normalized by
     CountryRenderer.init.
     ══════════════════════════════════════════════════════════════════════ */

  /* ── 1. Subtitle byline ─────────────────────────────────────────────── */
  CR.register('dno-dashboard', 'subtitle', function (ctx) {
    var d = getCfg(ctx);
    if (!d || !d.subtitle) return;
    setText('dno-subtitle', d.subtitle);
  });

  /* ── 2. Governance Stack — 4-tile KPI grid ──────────────────────────── */
  CR.register('dno-dashboard', 'governance-stack', function (ctx) {
    var d = getCfg(ctx);
    var grid = document.getElementById('dno-governance-grid');
    if (!grid) return;
    var tiles = (d && Array.isArray(d.governance)) ? d.governance : [];
    if (!tiles.length) {
      // Hide the whole section if no governance data was supplied.
      var section = document.getElementById('dno-governance-section');
      if (section) section.style.display = 'none';
      return;
    }
    grid.innerHTML = tiles.map(function (t) {
      return '<div class="kpi-card">' +
        '<div class="kpi-label">' + esc(t.label || '') + '</div>' +
        '<div class="kpi-value" style="font-size:22px">' + esc(t.value || '') + '</div>' +
        '<div class="kpi-sub">' + esc(t.sub || '') + '</div>' +
        '</div>';
    }).join('');
  });

  /* ── 3. Intro paragraph ─────────────────────────────────────────────── */
  CR.register('dno-dashboard', 'intro', function (ctx) {
    var d = getCfg(ctx);
    var el = document.getElementById('dno-intro');
    if (!el) return;
    if (d && d.intro) {
      el.textContent = d.intro;
    } else {
      // Fallback: synthesise a neutral one-liner for non-migrated countries.
      var name = countryNameFromCtx(ctx);
      el.textContent = (name || 'This country') + '’s distribution segmentation is not yet decomposed in the country-config dno_dashboard block. See methodology for the consolidated single-DSO view.';
    }
  });

  /* ── 4. DSO card grid — the headline section ────────────────────────── */
  CR.register('dno-dashboard', 'dso-grid', function (ctx) {
    var d = getCfg(ctx);
    var grid = document.getElementById('dno-dso-grid');
    if (!grid) return;
    var dsos = (d && Array.isArray(d.dsos)) ? d.dsos : [];

    // Universal fallback for non-migrated countries OR single-DSO markets:
    // render one informative card rather than breaking the page.
    if (dsos.length < 2) {
      var name = countryNameFromCtx(ctx);
      var only = dsos.length === 1 ? dsos[0] : null;
      var msg = only
        ? '<strong>' + esc(only.name || (name + ' national DSO')) + '</strong> operates the entire distribution network. No multi-DSO segmentation applies.'
        : 'No multi-DSO segmentation has been configured for ' + esc(name) + ' yet. ' +
          'The country-config <code>dno_dashboard.dsos</code> array is empty — many markets ' +
          'operate a single national DSO and don’t require this view.';
      grid.innerHTML =
        '<div class="dso-card animate-in" style="border-left:4px solid var(--terracotta);padding:16px;background:var(--cream);border-radius:var(--radius);grid-column:1/-1">' +
          '<h3 style="margin-top:0">Single-DSO view</h3>' +
          '<p style="font-size:13px;line-height:1.7;margin:8px 0 0">' + msg + '</p>' +
        '</div>';
      return;
    }

    grid.innerHTML = dsos.map(function (d, i) {
      var color = d.color || '#941914';
      var rgb = hexToRgb(color) || '148,25,20';
      var badgeBg = d.badge_bg || ('rgba(' + rgb + ',0.1)');
      var badgeColor = d.badge_color || color;
      var share = (d.share_pct != null) ? (d.share_pct + '%') : '';
      var customers = d.customers || '';
      var customersLabel = d.customers_label || 'LV customers';
      var name = d.name || '';
      var coverage = d.coverage || d.hazard_notes || '';
      var delayClass = 'delay-' + (((i) % 4) + 1);
      return '<div class="dso-card animate-in ' + delayClass + '" ' +
          'style="border-left:4px solid ' + esc(color) + ';padding:16px;background:var(--cream);border-radius:var(--radius)">' +
        (share ? '<span class="badge" style="background:' + esc(badgeBg) + ';color:' + esc(badgeColor) +
          ';font-size:11px;padding:2px 8px;border-radius:3px;font-weight:600">' + esc(share) + '</span>' : '') +
        '<h3 style="margin-top:8px">' + esc(name) + '</h3>' +
        (customers ? '<div style="font-family:\'Playfair Display\',serif;font-size:24px;font-weight:700;color:' +
          esc(color) + '">' + esc(customers) + '</div>' : '') +
        (customers ? '<div style="font-size:11px;color:var(--warm-grey)">' + esc(customersLabel) + '</div>' : '') +
        (coverage ? '<p style="font-size:12px;line-height:1.6;margin-top:8px">' + esc(coverage) + '</p>' : '') +
        '</div>';
    }).join('');
  });

  /* ── 5. SAIDI peer-table block ──────────────────────────────────────── */
  CR.register('dno-dashboard', 'saidi', function (ctx) {
    var d = getCfg(ctx);
    var section = document.getElementById('dno-saidi-section');
    var saidi = d && d.saidi;
    if (!saidi || !Array.isArray(saidi.peers) || !saidi.peers.length) {
      if (section) section.style.display = 'none';
      return;
    }
    setText('dno-saidi-headline', saidi.headline || '');
    var tbody = document.querySelector('#dno-saidi-table tbody');
    if (!tbody) return;
    tbody.innerHTML = saidi.peers.map(function (p) {
      var bg = p.highlight ? ' style="background:#fff8db"' : '';
      var name = p.highlight
        ? '<strong>' + esc(p.country || '') + '</strong>'
        : esc(p.country || '');
      var saidiCell = p.highlight
        ? '<strong>' + esc(p.saidi_min || '') + '</strong>'
        : esc(p.saidi_min || '');
      return '<tr' + bg + '><td>' + name + '</td><td>' + saidiCell + '</td><td>' + esc(p.notes || '') + '</td></tr>';
    }).join('');
  });

  /* ── 6. Supplementary notes (nuclear / transition / cyber / …) ──────── */
  CR.register('dno-dashboard', 'notes', function (ctx) {
    var d = getCfg(ctx);
    var container = document.getElementById('dno-notes');
    if (!container) return;
    var notes = (d && Array.isArray(d.notes)) ? d.notes : [];
    if (!notes.length) {
      container.style.display = 'none';
      return;
    }
    container.innerHTML = notes.map(function (n) {
      var id = n.id ? ' id="' + esc(n.id) + '"' : '';
      return '<section' + id + ' style="margin-bottom:32px">' +
        (n.heading ? '<h2>' + esc(n.heading) + '</h2>' : '') +
        '<div class="card animate-in" style="margin-top:24px">' +
          (n.sub_heading ? '<h3>' + esc(n.sub_heading) + '</h3>' : '') +
          '<p style="font-size:13px;line-height:1.7">' + esc(n.body || '') + '</p>' +
        '</div>' +
      '</section>';
    }).join('');
  });

})();
