/* ═══════════════════════════════════════════════════════════════════════════
   map-sections.js — Phase 2d.3 (KB §65) — Thin-shell section handler
   ───────────────────────────────────────────────────────────────────────────
   Registers the `map-stats` section renderer against CountryRenderer for the
   `map` page (interactive substation explorer). The heavy lifting — canvas
   panning/zooming, substation hit-testing, line drawing, admin-polygon
   overlay, detail-panel articulation, filter wiring — is owned by `map.js`
   at the repo root (and `SSIMap.init` runs the auto-fit + fleet_summary
   canonicalisation pipeline before any callback fires). This file therefore
   handles ONLY:

     1. Computing the country-specific `SSIMap.init` options (center, zoom,
        region_unit_label) from `intelligence/country-configs/<slug>.json`,
        with sane defaults for non-migrated countries.

     2. Wiring the `onLoaded` callback that populates the top-right
        `#map-stats` overlay with the substations × regions × critical ×
        median-R summary, using the canonical fleet_summary keys
        (median_R / R_median, bands.Critical, regions.length).

   Country-specific values live in
     intelligence/country-configs/<slug>.json under:
        map_page.center            — { lat, lon } (default: data-driven fit)
        map_page.zoom              — initial scale hint (default: 8)
        map_page.region_unit_label — '12 NUTS-3 regions', '47 Prefectures',
                                     '16 Bundesländer', etc. Used inside the
                                     #map-stats overlay.
     admin.l1.label_en             — fallback singular ('NUTS-3 region')
     admin.l1.count                — fallback count

   Usage from a thin-shell HTML:

       <script src="../map.js?v=…"></script>
       <script src="../country-renderer.js?v=700"></script>
       <script src="../map-sections.js?v=700"></script>
       <script>
         document.addEventListener('DOMContentLoaded', function () {
           CountryRenderer.init('<country>', 'map');
         });
       </script>

   The DOMContentLoaded ordering matters: `SSIMap.init` is invoked from
   inside the `map-stats` section so that (a) the canvas is in the DOM, and
   (b) `CountryRenderer` has already loaded + normalised ssi-data.json /
   country-config.json, letting us hand the canonical fleet_summary straight
   into the overlay without a second fetch.

   The file has no module footer — sections register themselves at load time.
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (!window.CountryRenderer) {
    console.error('[map-sections] CountryRenderer not loaded — section registrations skipped');
    return;
  }
  var CR = window.CountryRenderer;

  /* ── Defaults exposed for non-migrated countries ─────────────────────── */
  function getMapCenter(cfg) {
    if (cfg && cfg.map_page && cfg.map_page.center &&
        typeof cfg.map_page.center.lat === 'number' &&
        typeof cfg.map_page.center.lon === 'number') {
      return cfg.map_page.center;
    }
    // `null` lets map.js auto-fit to the substation bbox (preferred path).
    return null;
  }

  function getMapZoom(cfg) {
    if (cfg && cfg.map_page && typeof cfg.map_page.zoom === 'number') {
      return cfg.map_page.zoom;
    }
    return 8;
  }

  function getRegionUnitLabel(data, cfg) {
    // Explicit override wins.
    if (cfg && cfg.map_page && cfg.map_page.region_unit_label) {
      return cfg.map_page.region_unit_label;
    }
    // Otherwise synthesise from admin.l1 + actual region count in data.
    var n = (data && data.regions && data.regions.length) || 0;
    if (!n && cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.count) {
      n = cfg.admin.l1.count;
    }
    var label = 'regions';
    if (cfg && cfg.admin && cfg.admin.l1 && cfg.admin.l1.label_en) {
      var l1 = cfg.admin.l1.label_en;
      label = /s$/i.test(l1) ? l1 : l1 + 's';
    }
    return n ? n + ' ' + label : label;
  }

  function fmt3(v) {
    if (v == null || isNaN(v)) return '—';
    return Number(v).toFixed(3);
  }

  /* ══════════════════════════════════════════════════════════════════════
     SECTION REGISTRATION — receives ctx = { data, config, country, page, doc }
     ssi-data.json is already loaded + normalised by CountryRenderer.init.
     ══════════════════════════════════════════════════════════════════════ */

  /* ── Map stats overlay + SSIMap initialiser ─────────────────────────── */
  CR.register('map', 'map-stats', function (ctx) {
    if (!window.SSIMap || typeof SSIMap.init !== 'function') {
      console.error('[map-sections] SSIMap not loaded — map.js must be included before map-sections.js');
      return;
    }
    var cfg = ctx.config || {};
    var data = ctx.data || {};

    var center = getMapCenter(cfg);
    var zoom = getMapZoom(cfg);
    var regionUnitLabel = getRegionUnitLabel(data, cfg);

    var initOptions = {
      zoom: zoom,
      onLoaded: function (ssi) {
        var stats = document.getElementById('map-stats');
        if (!stats) return;
        var fs = (ssi && ssi.fleet_summary) || {};
        var total = (fs.total != null ? fs.total : (ssi && ssi.substations ? ssi.substations.length : 0)) || 0;
        var critical = (fs.bands && fs.bands.Critical != null) ? fs.bands.Critical : 0;
        var medianR = (fs.median_R != null) ? fs.median_R
                    : (fs.R_median != null ? fs.R_median : null);
        var nRegions = (ssi && ssi.regions && ssi.regions.length) || 0;
        var regionsLabel = regionUnitLabel || (nRegions + ' regions');
        // If regionUnitLabel doesn't already encode the count, prefer the
        // live count from the loaded SSI payload.
        var hasCountInLabel = /\b\d+\b/.test(regionsLabel);
        var regionPart = hasCountInLabel ? regionsLabel : (nRegions + ' ' + regionsLabel);

        stats.innerHTML =
          '<b>' + Number(total).toLocaleString() + '</b> substations · ' +
          regionPart + ' · ' +
          '<b>' + critical + '</b> critical · ' +
          'median R = <b>' + fmt3(medianR) + '</b>';
      }
    };
    if (center) initOptions.center = center;

    SSIMap.init('ssi-map-canvas', initOptions);
  });

})();
