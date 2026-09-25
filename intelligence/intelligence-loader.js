/**
 * SSI Intelligence Loader v1.1
 * Auto-populates edition metadata from edition-config.json.
 *
 * Usage on the intelligence page (full integration — sets <title> + edition text):
 *   <script src="../intelligence/intelligence-loader.js" data-country="france"></script>
 *
 * Usage on an ESG page (metadata only, leaves page <title> alone):
 *   <script src="../intelligence/intelligence-loader.js"
 *           data-country="france" id="ssi-esg-page"></script>
 *
 * If the country is not in the active rotation, the loader exits quietly.
 * Pre-launch countries (listed in PRE_LAUNCH_COUNTRIES) don't even log.
 */
(function() {
  'use strict';

  // Detect country from script tag data-country attribute
  var scripts = document.getElementsByTagName('script');
  var thisScript = scripts[scripts.length - 1];
  var COUNTRY = thisScript.getAttribute('data-country') || '';
  if (!COUNTRY) {
    // Fallback: detect from URL path
    var pathParts = window.location.pathname.split('/').filter(Boolean);
    COUNTRY = pathParts.length > 0 ? pathParts[0] : '';
  }

  // Skip title rewrite for pages that have their own title (e.g. ESG report).
  var SKIP_TITLE = thisScript.id === 'ssi-esg-page' ||
                   thisScript.getAttribute('data-skip-title') === 'true';

  // Countries that are provisioned but not yet in the active rotation.
  // Silences the "No config for country" warning until they're live.
  var PRE_LAUNCH_COUNTRIES = ['portugal', 'new-zealand', 'czechia'];

  // Month names for display
  var MONTHS = ['January','February','March','April','May','June',
                'July','August','September','October','November','December'];

  // Compute current edition key (YYYY-MM)
  function currentEditionKey() {
    var d = new Date();
    var m = d.getMonth() + 1;
    return d.getFullYear() + '-' + (m < 10 ? '0' + m : m);
  }

  // Format month display
  function formatMonth(key) {
    var parts = key.split('-');
    return MONTHS[parseInt(parts[1], 10) - 1] + ' ' + parts[0];
  }

  // Expose config globally for inline scripts to use
  window.SSI_EDITION = null;
  window.SSI_COUNTRY = COUNTRY;
  window.SSI_CONFIG_READY = false;

  fetch('../intelligence/edition-config.json?v=' + Date.now())
    .then(function(r) { return r.json(); })
    .then(function(config) {
      // Use the active edition key set by the workflow (null = no edition yet)
      var key = config.active_edition_key;
      if (!key) {
        console.log('[SSI-Loader] No active edition yet (pre-launch)');
        document.dispatchEvent(new CustomEvent('ssi-config-ready', { detail: null }));
        return;
      }
      var rotation = config.rotation[key];
      if (!rotation) {
        console.warn('[SSI-Loader] No rotation found for active key:', key);
        document.dispatchEvent(new CustomEvent('ssi-config-ready', { detail: null }));
        return;
      }

      var countryConf = rotation.countries[COUNTRY];
      if (!countryConf) {
        if (PRE_LAUNCH_COUNTRIES.indexOf(COUNTRY) === -1) {
          // Unexpected miss: log loudly so ops notices.
          console.warn('[SSI-Loader] No config for country:', COUNTRY);
        }
        document.dispatchEvent(new CustomEvent('ssi-config-ready', { detail: null }));
        return;
      }

      // Build the edition object
      var edition = {
        number: config.current_edition,
        label: rotation.edition_label,
        version: config.ssi_version,
        month: formatMonth(key),
        monthKey: key,
        theme: rotation.theme_index,
        corridor: countryConf.corridor_name,
        corridorSubtitle: countryConf.corridor_subtitle,
        regionFilter: countryConf.region_filter,
        adminL1: countryConf.admin_l1,
        adminL2: countryConf.admin_l2,
        deepDiveLabel: countryConf.deep_dive_label,
        useNominatim: countryConf.use_nominatim || false,
        modifiers: (config.modifiers_by_country && config.modifiers_by_country[COUNTRY]) || [],
        dataFormat: (config.data_format && config.data_format[COUNTRY]) || 'object',
        saidi: config.saidi_benchmark || {},
        twelveMonthPlan: config.twelve_month_plan || [],
        country: COUNTRY
      };

      window.SSI_EDITION = edition;
      window.SSI_CONFIG_READY = true;

      // Auto-populate DOM elements with data-edition attributes
      populateEditionText(edition);

      // Dispatch event so inline scripts know config is ready
      document.dispatchEvent(new CustomEvent('ssi-config-ready', { detail: edition }));
    })
    .catch(function(err) {
      console.error('[SSI-Loader] Failed to load edition config:', err);
      // Still dispatch so pages don't hang
      document.dispatchEvent(new CustomEvent('ssi-config-ready', { detail: null }));
    });

  function populateEditionText(ed) {
    // Find and replace all elements with data-edition attribute
    var els = document.querySelectorAll('[data-edition]');
    els.forEach(function(el) {
      var field = el.getAttribute('data-edition');
      switch (field) {
        case 'number':    el.textContent = 'Edition ' + ed.label; break;
        case 'subtitle':  el.textContent = ed.corridorSubtitle; break;
        case 'month':     el.textContent = ed.month; break;
        case 'version':   el.textContent = 'SSI v' + ed.version; break;
        case 'corridor':  el.textContent = ed.corridor; break;
        case 'tagline':   el.textContent = 'Inaugural edition \u00b7 ' + ed.month + ' \u00b7 SSI v' + ed.version; break;
        case 'full-title': el.textContent = 'Edition ' + ed.label + ' \u2014 ' + ed.corridorSubtitle; break;
        case 'card-header': el.textContent = 'Ed. ' + ed.label + ' \u00b7 ' + ed.month; break;
        // Overview-page call to action. Sets text on the existing anchor rather
        // than wrapping the number in a new element: inserting a node changes
        // the DOM tree, which the layout-invariance check treats as a design
        // change - correctly, since section 7.7 forbids it.
        case 'cta':       el.textContent = 'Read Edition ' + ed.label + ' \u2192'; break;
      }
    });

    // Also populate <title> — skipped on ESG pages (they manage their own title).
    if (!SKIP_TITLE) {
      // Replace only the edition token, so the country name in the static
      // title survives. Overwriting the whole string dropped it:
      // "SSI Monthly Intelligence — Türkiye — Edition 006" became
      // "SSI Monthly Intelligence — Edition 006".
      // Rewrite ONLY the edition token, and ONLY on a page whose title already
      // declares one. The loader is also loaded by index/data/regional/
      // methodology/map, whose ids are not in SKIP_TITLE; assigning a title
      // unconditionally replaced "SSI Index — Türkiye — Overview (v4.2)" with
      // "SSI Monthly Intelligence — Edition 006" on every overview page.
      if (/Edition\s+\d{3}/.test(document.title)) {
        document.title = document.title.replace(/Edition\s+\d{3}/,
                                                'Edition ' + ed.label);
      }
    }

    // Populate the 12-month rotation box if it exists
    var rotationEl = document.getElementById('edition-rotation');
    if (rotationEl && ed.twelveMonthPlan.length) {
      var html = '<strong>Deep-dive rotation:</strong> Each edition features a substantive thematic analysis. The 12-month rotation: ';
      html += ed.twelveMonthPlan.map(function(t, i) {
        var bold = (i + 1 === ed.theme) ? '<strong>' + t + '</strong>' : t;
        return bold;
      }).join(' \u00b7 ');
      html += '.';
      rotationEl.innerHTML = html;
    }
  }
})();
