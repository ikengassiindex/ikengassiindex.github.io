/**
 * SSI Intelligence Loader v1.0
 * Auto-populates edition metadata from edition-config.json
 * Usage: <script src="../intelligence/intelligence-loader.js" data-country="france"></script>
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
      var key = currentEditionKey();
      var rotation = config.rotation[key];

      // Fallback: find the latest available rotation
      if (!rotation) {
        var keys = Object.keys(config.rotation).sort();
        key = keys[keys.length - 1] || keys[0];
        rotation = config.rotation[key];
      }

      if (!rotation) {
        console.warn('[SSI-Loader] No rotation found for', key);
        return;
      }

      var countryConf = rotation.countries[COUNTRY];
      if (!countryConf) {
        console.warn('[SSI-Loader] No config for country:', COUNTRY);
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
      }
    });

    // Also populate <title>
    document.title = 'SSI Monthly Intelligence \u2014 Edition ' + ed.label;

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
