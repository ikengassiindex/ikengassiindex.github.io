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

  /* ── 1b. Metadata schema normalization (anti-pattern A1b) ─────────────
     KB §68.11 / BPG Part XXXV.3 — schema-key drift at the metadata
     boundary. Each window.SSI_METADATA.* array consumed by section
     handlers can have a country-specific schema variant. Without
     per-array aliasing, fields silently render as `undefined` (label),
     '—' (sigma), or fall back to neutral defaults that mask the issue.

     Applied to window.SSI_METADATA BEFORE sections see it. Same shape as
     normalize(data) above: idempotent (re-running on already-normalised
     metadata is a no-op), non-destructive (variant fields preserved
     alongside canonical fields), defensive (operates on copies).

     Slovakia onboarding (2026-05-28) surfaced two real drift sites:
       - COMPONENTS_INDEX: ships {code, name, ceiling, drivers} but the
         Fleet-Average renderer reads {key, label, w, color}. Symptom:
         bar label rendered literal "undefined". Hotfix #3 spot-patched
         in index-sections.js; this central pass supersedes that.
       - MODIFIER_DEFS: ships {id, domain, range, description} but the
         Modifier-Impact renderer reads {key, label, domain, range}.
         Symptom: m.key is undefined so subs.modifiers[m.key] is always
         NaN → sigma column always renders '—'. Latent on live SK page.

     COMPONENTS / DATA_LAYERS / NORM_METHODS / VALIDATION_CHECKS /
     CHANGELOG audit (see KB §68.11): no drift between SI/SK and what
     methodology-sections.js reads — no aliasing needed.

     DATA_SOURCES carries a minor cosmetic drift (SI/SK don't ship the
     `category` field that drives the source-icon palette, so all
     sources render with the gray Standards icon). Not breaking; we
     leave the renderer's fallback in place rather than synthesise a
     `category` derivation here, because the right answer is for the
     metadata files to ship the field. Tracked for a future pass.
     ──────────────────────────────────────────────────────────────── */
  var COMPONENT_DEFAULT_PALETTE = {
    C: 'var(--crimson)', V: 'var(--terracotta)', I: 'var(--sage)',
    E: '#3b9eff',        S: 'var(--bronze)',     T: '#22d3ee'
  };

  function normalizeComponentBar(c) {
    /* {code, name, ceiling, drivers}  →  {key, label, w, color, drivers}
       Canonical {key, label, w, color} pass through untouched (idempotent). */
    if (!c || typeof c !== 'object') return c;
    var key   = c.key   != null ? c.key   : c.code;
    var label = c.label != null ? c.label : (c.name ? (key + ' — ' + c.name) : c.name);
    var w     = c.w     != null ? c.w     : c.ceiling;
    var color = c.color != null ? c.color : (COMPONENT_DEFAULT_PALETTE[key] || '#888');
    return {
      key: key, label: label, w: w, color: color,
      // preserve variant fields so callers that prefer them still work
      code: c.code != null ? c.code : key,
      name: c.name != null ? c.name : (label || ''),
      ceiling: c.ceiling != null ? c.ceiling : w,
      drivers: c.drivers || null
    };
  }

  function normalizeModifierDef(m) {
    /* {id, domain, range, description}  →  {key, label, domain, range, description}
       Slovakia's `id` (e.g. 'R3', 'R6a') maps to the canonical 4-modifier
       runtime key on substations (R3_C_mult, R6_restoration, …) via a
       lookup table. `label` defaults to `id`. Canonical input passes
       through untouched. */
    if (!m || typeof m !== 'object') return m;
    var key   = m.key   != null ? m.key   : MODIFIER_ID_TO_KEY[m.id] || m.id;
    var label = m.label != null ? m.label : (m.id != null ? String(m.id) : '');
    return {
      key: key,
      label: label,
      domain: m.domain != null ? m.domain : '',
      range:  m.range  != null ? m.range  : '',
      description: m.description || '',
      // preserve original id for downstream consumers
      id: m.id != null ? m.id : key
    };
  }

  /* MODIFIER_ID_TO_KEY: maps short ids (used in MODIFIER_DEFS arrays) to the
     canonical substation modifier keys. Same convention as
     DEFAULT_MODIFIER_DEFS in index-sections.js. */
  var MODIFIER_ID_TO_KEY = {
    R3: 'R3_C_mult',
    R4: 'R4_F_topo',
    R6a: 'R6_restoration',
    R6b: 'R6_seismic',
    R7: 'R7_cyber'
  };

  function normalizeMeta() {
    var meta = window.SSI_METADATA || window.SSIMetadata;
    if (!meta || typeof meta !== 'object') return;
    if (Array.isArray(meta.COMPONENTS_INDEX)) {
      meta.COMPONENTS_INDEX = meta.COMPONENTS_INDEX.map(normalizeComponentBar);
    }
    if (Array.isArray(meta.MODIFIER_DEFS)) {
      meta.MODIFIER_DEFS = meta.MODIFIER_DEFS.map(normalizeModifierDef);
    }
    // Mirror onto the dual-global alias (KB §45.6) so consumers that read
    // either name see the normalised arrays.
    if (window.SSIMetadata && window.SSIMetadata !== meta) {
      window.SSIMetadata = meta;
    }
    if (window.SSI_METADATA && window.SSI_METADATA !== meta) {
      window.SSI_METADATA = meta;
    }
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
    // PR-3 (audit memo 2026-06-08) added three provenance fields to every
    // substation record: mult_product (scalar Π of multiplicative modifiers),
    // add_sum (Σ of additive modifier deltas), and modifier_impacts (dict
    // of {modifier_name: round(value − 1.0, 4)}). They are pass-through here:
    // no legacy alias exists, so no normalization is required. Renderers
    // consume them directly from s.mult_product / s.add_sum / s.modifier_impacts.
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
      // Normalise window.SSI_METADATA arrays once, here, before any section
      // handler runs (KB §68.11 / BPG Part XXXV.3). Idempotent — safe even
      // if a country's ssi-metadata.js already ships canonical schemas.
      normalizeMeta();
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
      return ({ Low: '#5d8563', Medium: '#b8863a', High: '#aa4234', Critical: '#941914', Extreme: '#5a0d0a' })[band] || '#888';
    },
    el: function (id) { return document.getElementById(id); },
    setText: function (id, text) { var e = document.getElementById(id); if (e) e.textContent = text; },
    setHTML: function (id, html) { var e = document.getElementById(id); if (e) e.innerHTML = html; },
  };

  /* ─────────────────────────────────────────────────────────────────────────
     Safe — defensive helpers (KB §68.9 / anti-pattern A12)
     ─────────────────────────────────────────────────────────────────────────
     SK hotfix #2 shipped these to centralize the null/undefined defenses
     that were previously scattered across every section file. Slovakia's
     OSM extract surfaced 5 distinct bug classes that Slovenia's voltage-
     complete data masked:

       1. ${obj.field} where field doesn't exist → renders literal 'undefined'
       2. ${val.toFixed(n)} where val is null → TypeError, section dies
       3. (x || 0) >= N where N > 0 → null silently mis-counted (false negatives)
       4. s.name || '' → empty cell where data should be
       5. data.x.y.z accessor through optional sub-objects → TypeError

     Every helper here is documented with the bug class it prevents and the
     idiom it replaces. When a new section is added, prefer these to bare
     property access + .toFixed().
     ───────────────────────────────────────────────────────────────────── */
  var Safe = {
    /* ── num(v, dflt) ────────────────────────────────────────────────────
       Coerce v to a finite Number, else return dflt. Never returns NaN.

       Bug class: A12.3 — `(x || 0) >= M` for M > 0 returns false when x is
       null/undefined, silently mis-counting. Use Safe.num(x, -Infinity)
       when the comparison should EXCLUDE missing data, or Safe.num(x, 0)
       when 0 is genuinely the right neutral element (e.g. summing).

         var hv = subs.filter(function (s) {
           return Safe.num(s.voltage_kv, -Infinity) >= 132;
         }).length;
       ──────────────────────────────────────────────────────────────── */
    num: function (v, dflt) {
      if (v == null) return dflt;
      var n = Number(v);
      return isNaN(n) ? dflt : n;
    },

    /* ── fmt(v, dp, fallback) ────────────────────────────────────────────
       Like Number(v).toFixed(dp) but never throws on null/undefined/NaN.
       Default dp=3, default fallback='—'. Replace EVERY bare .toFixed()
       call site in renderers.

       Bug class: A12.2 — `${val.toFixed(3)}` blows up when val is null,
       killing the section AND any later code in the same render block.

         Safe.fmt(s.R_median, 3)          → '0.481' or '—'
         Safe.fmt(s.R_median, 3, 'N/A')   → '0.481' or 'N/A'
       ──────────────────────────────────────────────────────────────── */
    fmt: function (v, dp, fallback) {
      if (v == null) return fallback == null ? '—' : fallback;
      var n = Number(v);
      if (isNaN(n)) return fallback == null ? '—' : fallback;
      return n.toFixed(dp == null ? 3 : dp);
    },

    /* ── pct(v, dp, fallback) ────────────────────────────────────────────
       Like Safe.fmt but appends ' %'. Use for any value already on the
       0-100 scale; for 0-1 ratios multiply first. Default dp=1.

         Safe.pct(blindSpots.length / n * 100, 1)   → '12.3 %'
       ──────────────────────────────────────────────────────────────── */
    pct: function (v, dp, fallback) {
      if (v == null) return fallback == null ? '—' : fallback;
      var n = Number(v);
      if (isNaN(n)) return fallback == null ? '—' : fallback;
      return n.toFixed(dp == null ? 1 : dp) + '%';
    },

    /* ── locale(v, fallback) ─────────────────────────────────────────────
       Number(v).toLocaleString() but guards against null/NaN.

         Safe.locale(fleet.length)   → '1,516'
         Safe.locale(null)           → '—'
       ──────────────────────────────────────────────────────────────── */
    locale: function (v, fallback) {
      if (v == null) return fallback == null ? '—' : fallback;
      var n = Number(v);
      if (isNaN(n)) return fallback == null ? '—' : fallback;
      return n.toLocaleString();
    },

    /* ── displayName(s) ──────────────────────────────────────────────────
       Canonical substation display name resolution. Slovakia has 544
       substations with name='' — falling back to substation_id keeps the
       highest-R row from showing a blank cell. Single source of truth so
       every section agrees on what to render.

       Bug class: A12.4 — `s.name || ''` returns '' for missing data,
       producing blank table cells where an ID would do.

       Order: trimmed name → substation_id → internal_id → '(unnamed)'.
       ──────────────────────────────────────────────────────────────── */
    displayName: function (s) {
      if (!s || typeof s !== 'object') return '(unnamed)';
      if (s.name != null) {
        var trimmed = String(s.name).trim();
        if (trimmed) return trimmed;
      }
      if (s.substation_id) return String(s.substation_id);
      if (s.internal_id) return String(s.internal_id);
      return '(unnamed)';
    },

    /* ── voltageClass(v) ─────────────────────────────────────────────────
       Voltage trichotomy that respects null. Returns one of:
         'EHV'                ≥220 kV
         'HV'                 110-220 kV
         'distribution-tier'  <110 kV OR null/missing

       Bug class: A12.3 — `(v || 0) >= 220` mis-counts null as 0 → false,
       silently throwing all untagged substations into the lowest tier
       even when we have no idea what voltage they are. The
       'distribution-tier' label is the honest answer: "MV or unknown".
       ──────────────────────────────────────────────────────────────── */
    voltageClass: function (v) {
      if (v == null) return 'distribution-tier';
      var n = Number(v);
      if (isNaN(n)) return 'distribution-tier';
      if (n >= 220) return 'EHV';
      if (n >= 110) return 'HV';
      return 'distribution-tier';
    },

    /* ── regionOptions(regions) ──────────────────────────────────────────
       Build {value,label} option list for filter <select> elements. Drops
       null/empty region names. Use when you wire up the regional.html
       comparator dropdowns so they don't show a stray "undefined" option.

         var opts = Safe.regionOptions(data.regions);
         // [{ value: 'SI034', label: 'Savinjska (123)' }, ...]
       ──────────────────────────────────────────────────────────────── */
    regionOptions: function (regions) {
      if (!Array.isArray(regions)) return [];
      var out = [];
      for (var i = 0; i < regions.length; i++) {
        var r = regions[i];
        if (!r) continue;
        var v = r.region != null ? r.region : (r.name != null ? r.name : null);
        if (v == null) continue;
        var lbl = (r.name && r.name !== v) ? r.name : String(v);
        if (r.count != null) lbl += ' (' + r.count + ')';
        out.push({ value: String(v), label: lbl });
      }
      return out;
    },

    /* ── get(obj, path, dflt) ────────────────────────────────────────────
       Safe deep-property accessor — get(obj, 'a.b.c', 0) returns obj.a.b.c
       if every intermediate link exists, else dflt.

       Bug class: A12.5 — `data.fleet_summary.bands.Critical` throws if
       fleet_summary or bands is missing. Use this for any access path
       3+ levels deep, or 2 levels deep when the middle key is optional.

         Safe.get(data, 'fleet_summary.confidence_pct.high', 0)
         Safe.get(s, 'modifiers.R7_cyber')   // dflt = undefined
       ──────────────────────────────────────────────────────────────── */
    get: function (obj, path, dflt) {
      if (obj == null) return dflt;
      var parts = String(path).split('.');
      var cur = obj;
      for (var i = 0; i < parts.length; i++) {
        if (cur == null || typeof cur !== 'object') return dflt;
        cur = cur[parts[i]];
      }
      return cur == null ? dflt : cur;
    },

    /* ── filterFinite(subs, accessor, predicate) ─────────────────────────
       Filter an array by a predicate that only fires for finite numbers.
       Records with null/NaN at the accessor path are excluded from BOTH
       the numerator AND the denominator — the correct behaviour when the
       comparison is "of substations where we know X, how many have X≥M".

       Bug class: A12.3 — `(s.modifiers.R7_cyber || 0) < median` treats
       missing as 0 which is far below any reasonable median, mis-flagging
       every untagged substation as a "blind spot".

         var blind = Safe.filterFinite(fleet,
           function (s) { return s.modifiers && s.modifiers.R7_cyber; },
           function (v, s) { return v < medianR7 &&
             (s.classification === 'High' || s.classification === 'Critical' || s.classification === 'Extreme'); });
       ──────────────────────────────────────────────────────────────── */
    filterFinite: function (subs, accessor, predicate) {
      if (!Array.isArray(subs)) return [];
      var out = [];
      for (var i = 0; i < subs.length; i++) {
        var s = subs[i];
        var v = accessor ? accessor(s) : s;
        if (v == null) continue;
        var n = Number(v);
        if (isNaN(n)) continue;
        if (predicate(n, s)) out.push(s);
      }
      return out;
    }
  };

  /* ── 6. Public API ────────────────────────────────────────────────────── */
  window.CountryRenderer = {
    init: init,
    register: register,
    pickMonthlySubstation: pickMonthlySubstation,
    normalize: normalize,
    normalizeMeta: normalizeMeta,
    H: H,
    Safe: Safe,
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
