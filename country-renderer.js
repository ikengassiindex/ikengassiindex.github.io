/* ═══════════════════════════════════════════════════════════════════════════
   country-renderer.js — Phase 2 (KB §65.5) — Central rendering module
   ───────────────────────────────────────────────────────────────────────────
   ONE module that:
     1. Loads per-country data (ssi-data.json) + config (country-configs/*.json)
        ONCE per page (not 5-10× as today's per-section IIFEs do)
     2. NORMALIZES schema drift (median_R/R_median, P5/R_min, modifier_pct/_impact,
        markov.steady_state array vs dict, etc.) so renderer code never has to
        second-guess which key name applies — eliminates KB §64.3 anti-pattern A1
     3. Calls registered section renderers via try/catch ISOLATION so a single
        section bug never cascades into "everything stays on Loading" — closes
        KB §64.3 anti-pattern A8
     4. Reads per-country THRESHOLDS from intelligence/country-configs/{slug}.json
        instead of hardcoded numeric literals — closes anti-pattern A7

   USAGE in a thin-shell HTML page:
     <script src="../country-renderer.js?v=700"></script>
     <script>CountryRenderer.init('slovenia', 'esg-report');</script>

   Sections register themselves via CountryRenderer.register(page, id, fn) where
   fn receives (ctx) with {data, config, country, page, doc}. See bottom of
   this file for the Markov KPIs pilot section.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var CACHE_BUSTER = '700';  // bump when any of the data/config schemas change

  // ── Section registry: { 'esg-report': { 'markov-kpis': fn, ... }, ... } ──
  var registry = {};

  /* ── 1. Schema normalization (anti-pattern A1) ─────────────────────────
     Applied to data BEFORE sections see it. Section renderers can assume
     the canonical key names regardless of which country's pipeline emitted
     the data file. */
  function normalize(data) {
    if (!data || typeof data !== 'object') return data;

    var fs = data.fleet_summary = data.fleet_summary || {};
    if (fs.median_R == null && fs.R_median != null) fs.median_R = fs.R_median;
    if (fs.R_median == null && fs.median_R != null) fs.R_median = fs.median_R;
    if (fs.mean_R == null) fs.mean_R = fs.median_R || fs.R_median || 0;
    if (fs.P5 == null && fs.R_min != null) fs.P5 = fs.R_min;
    if (fs.P95 == null && fs.R_max != null) fs.P95 = fs.R_max;
    if (fs.R_min == null && fs.P5 != null) fs.R_min = fs.P5;
    if (fs.R_max == null && fs.P95 != null) fs.R_max = fs.P95;
    if (!fs.band_pct && fs.bands) {
      var total = fs.total || Object.values(fs.bands).reduce(function (a, b) { return a + (b || 0); }, 0) || 1;
      fs.band_pct = {};
      for (var b in fs.bands) fs.band_pct[b] = (fs.bands[b] / total) * 100;
    }
    if (!fs.confidence_pct) fs.confidence_pct = { high: 0, medium: 0, low: 0 };

    if (Array.isArray(data.substations)) {
      for (var i = 0; i < data.substations.length; i++) {
        normalizeSubstation(data.substations[i]);
      }
    }
    return data;
  }

  function normalizeSubstation(s) {
    if (!s) return;
    // R_base ↔ R_base_median
    if (s.R_base == null && s.R_base_median != null) s.R_base = s.R_base_median;
    if (s.R_base_median == null && s.R_base != null) s.R_base_median = s.R_base;
    // modifier_pct: compute from modifier_impact / R_base_median
    if (s.modifier_pct == null && s.modifier_impact != null && s.R_base_median) {
      s.modifier_pct = (s.modifier_impact / s.R_base_median * 100).toFixed(1);
    }
    // Markov sub-schema (KB §64.3 anti-pattern A1)
    var mk = s.markov;
    if (mk && typeof mk === 'object') {
      // ETTC_years ↔ ettc_years
      if (mk.ettc_years == null && mk.ETTC_years != null) mk.ettc_years = mk.ETTC_years;
      if (mk.ETTC_years == null && mk.ettc_years != null) mk.ETTC_years = mk.ettc_years;
      // p_crit_20yr ↔ p_critical_20yr (Estonia/Latvia/Lithuania)
      if (mk.p_critical_20yr == null && mk.p_crit_20yr != null) mk.p_critical_20yr = mk.p_crit_20yr;
      if (mk.p_crit_20yr == null && mk.p_critical_20yr != null) mk.p_crit_20yr = mk.p_critical_20yr;
      // stationary_critical: derive from steady_state if missing
      if (mk.stationary_critical == null) {
        if (Array.isArray(mk.steady_state) && mk.steady_state.length >= 4) {
          mk.stationary_critical = mk.steady_state[3];
        } else if (mk.steady_state && typeof mk.steady_state === 'object') {
          // Mexico uses dict form
          mk.stationary_critical = mk.steady_state.Critical || mk.steady_state.critical || 0;
        }
      }
      // steady_state: if dict, also expose as array
      if (mk.steady_state && !Array.isArray(mk.steady_state) && typeof mk.steady_state === 'object') {
        var ss = mk.steady_state;
        mk.steady_state_array = [
          ss.Good || ss.Healthy || ss.good || 0,
          ss.Acceptable || ss.Aging || ss.acceptable || 0,
          ss.Degraded || ss.degraded || 0,
          ss.Critical || ss.critical || 0,
        ];
      } else if (Array.isArray(mk.steady_state)) {
        mk.steady_state_array = mk.steady_state;
      }
    }
  }

  /* ── 2. Section registration ─────────────────────────────────────────── */
  function register(page, sectionId, fn) {
    if (!registry[page]) registry[page] = {};
    registry[page][sectionId] = fn;
  }

  /* ── 3. Load + render entry point ────────────────────────────────────── */
  function init(country, page, options) {
    options = options || {};
    var base = options.basePath || '';
    var dataUrl = base + 'ssi-data.json?v=' + CACHE_BUSTER;
    var configUrl = base + '../intelligence/country-configs/' + country + '.json?v=' + CACHE_BUSTER;

    Promise.all([
      fetch(dataUrl).then(function (r) {
        if (!r.ok) throw new Error('ssi-data.json HTTP ' + r.status);
        return r.json();
      }),
      // Country config is OPTIONAL — pages still work without one (renderer
      // applies sane defaults). 404 → null, no error propagated.
      fetch(configUrl).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }),
    ]).then(function (results) {
      var data = normalize(results[0]);
      var config = results[1] || defaultConfig(country, data);
      runSections(country, page, data, config);
    }).catch(function (err) {
      console.error('[CountryRenderer] load failed:', err);
      // Try to surface the error to the user instead of leaving all Loading…
      var banner = document.createElement('div');
      banner.style.cssText = 'background:#fbe9e7;color:#941914;padding:12px 16px;margin:12px 0;border-radius:8px;font-size:13px;';
      banner.textContent = 'Data load failed: ' + err.message + ' — pages may show Loading… placeholders.';
      var main = document.querySelector('main');
      (main || document.body).prepend(banner);
    });
  }

  function defaultConfig(country, data) {
    // Synthesize a minimal config when the file is missing
    var n_regions = (data.regions && data.regions.length) ||
      (data.meta && data.meta.regions) || 1;
    return {
      slug: country,
      country_name: country.charAt(0).toUpperCase() + country.slice(1),
      admin: { l1: { label_en: 'region', count: n_regions } },
    };
  }

  function runSections(country, page, data, config) {
    var sections = registry[page] || {};
    var ctx = { data: data, config: config, country: country, page: page, doc: document };
    Object.keys(sections).forEach(function (sectionId) {
      try {
        sections[sectionId](ctx);
      } catch (e) {
        console.error('[CountryRenderer] section ' + page + '/' + sectionId + ' failed:', e);
        // Section-level failure isolation (anti-pattern A8 closure)
      }
    });
  }

  /* ── 4. Substation picker (deterministic monthly seed) ─────────────────
     Single canonical implementation. Today every country page duplicates
     this logic inline. */
  function pickMonthlySubstation(data) {
    if (!data || !Array.isArray(data.substations) || !data.substations.length) return null;
    var now = new Date();
    var seed = now.getFullYear() * 100 + (now.getMonth() + 1);
    var h = seed;
    h = (((h >>> 16) ^ h) * 0x45d9f3b) | 0;
    h = (((h >>> 16) ^ h) * 0x45d9f3b) | 0;
    h = (h >>> 16) ^ h;
    return data.substations[Math.abs(h) % data.substations.length];
  }

  /* ── 5. Helpers exposed to section renderers ──────────────────────────── */
  var H = {
    fmt: function (v, dp) { return (v == null || isNaN(v)) ? '—' : Number(v).toFixed(dp == null ? 3 : dp); },
    pct: function (v, dp) { return (v == null || isNaN(v)) ? '—' : Number(v).toFixed(dp == null ? 1 : dp) + '%'; },
    bandColor: function (band) {
      return ({ Low: '#5d8563', Medium: '#b8863a', High: '#aa4234', Critical: '#941914' })[band] || '#888';
    },
    el: function (id) { return document.getElementById(id); },
    setText: function (id, text) { var e = document.getElementById(id); if (e) e.textContent = text; },
    setHTML: function (id, html) { var e = document.getElementById(id); if (e) e.innerHTML = html; },
  };

  /* ── 6. Public API ────────────────────────────────────────────────────── */
  window.CountryRenderer = {
    init: init,
    register: register,
    pickMonthlySubstation: pickMonthlySubstation,
    normalize: normalize,
    H: H,
    _registry: registry,  // exposed for debugging only
  };
})();


/* ═══════════════════════════════════════════════════════════════════════════
   PILOT SECTION — esg-report / markov-kpis
   ───────────────────────────────────────────────────────────────────────────
   Replaces the inline <script> block in slovenia/esg-report.html lines
   778-783 (the renderMarkov function). Demonstrates the pattern:
     - No fetch (data already loaded + normalized by CountryRenderer.init)
     - All field accesses use canonical names from normalization layer
     - try/catch is at the caller layer (runSections), not here
   ═══════════════════════════════════════════════════════════════════════════ */
CountryRenderer.register('esg-report', 'markov-kpis', function (ctx) {
  var sub = CountryRenderer.pickMonthlySubstation(ctx.data);
  if (!sub) return;
  var mk = sub.markov || {};
  var H = CountryRenderer.H;

  H.setText('markovRiskScore', H.fmt(mk.risk_score, 3));
  H.setText('markovETTC', mk.ettc_years != null ? mk.ettc_years + ' yr' : '—');
  H.setText('markovPCrit', mk.p_critical_20yr != null ? (mk.p_critical_20yr * 100).toFixed(1) + '%' : '—');
  H.setText('markovCorrosion', mk.corrosion_class || '—');
});
