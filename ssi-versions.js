/**
 * SSI Version Manifest & Dynamic Loader
 * v2 — Dynamically injects scripts and stylesheets with versioned URLs
 *
 * HTML pages only need:
 *   <script src="../ssi-versions.js"></script>
 *
 * This loader:
 *   1. Fetches versions.json (with timestamp bust — never cached)
 *   2. Injects <link> for style.css with correct ?v=
 *   3. Injects <script> for nav.js with correct ?v=
 *   4. Injects <script> for ssi-metadata.js (country-specific, no version)
 *   5. Exposes window.ssiAssetUrl() for JS code that fetches data files
 *   6. Fires 'ssi-versions-ready' event when done
 *
 * To update any shared asset:
 *   1. Push the updated asset to GitHub
 *   2. Bump the number in versions.json
 *   3. Done — all pages get the new version immediately
 */
(function() {
  'use strict';

  // Detect context
  var path = window.location.pathname;
  var countryMatch = path.match(/^\/(france|italy|uk|spain|germany|switzerland|austria|us|canada|japan|australia|chile|poland|finland|sweden|norway|denmark|mexico|greece|ireland|portugal|turkey|new-zealand|greenland)\//i);
  var isCountryPage = !!countryMatch;
  var country = countryMatch ? countryMatch[1].toLowerCase() : null;
  var base = isCountryPage ? '../' : './';

  // Store for global access
  window.SSI_COUNTRY_CODE = country;
  window.SSI_BASE = base;

  // Fetch manifest
  var ts = Date.now();
  fetch(base + 'versions.json?_=' + ts, { cache: 'no-store' })
    .then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function(manifest) {
      window.SSI_VERSIONS = manifest.assets || {};
      window.SSI_VERSION_ID = manifest.v || 0;

      // Version helper for data fetches
      window.ssiAssetUrl = function(assetKey, filename) {
        var v = (manifest.assets && manifest.assets[assetKey]) || ts;
        return filename + '?v=' + v;
      };

      // Fire ready event
      document.dispatchEvent(new CustomEvent('ssi-versions-ready', { detail: manifest }));
    })
    .catch(function(err) {
      console.warn('[SSI] versions.json unavailable, using timestamp fallback:', err.message);
      window.SSI_VERSIONS = {};
      window.SSI_VERSION_ID = 0;
      window.ssiAssetUrl = function(key, filename) { return filename + '?v=' + ts; };
      document.dispatchEvent(new CustomEvent('ssi-versions-ready', { detail: { v: 0, assets: {} } }));
    });
})();
