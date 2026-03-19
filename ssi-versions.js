/**
 * SSI Version Manifest Loader
 *
 * Single source of truth for all asset cache-bust versions.
 * Every HTML page loads this ONE file (with a timestamp-based cache-bust).
 * This file then provides the correct version for every other asset.
 *
 * To update any shared asset:
 *   1. Push the updated asset to GitHub
 *   2. Increment the version number in versions.json
 *   3. Done — all 84+ pages automatically use the new version
 *
 * Architecture:
 *   HTML page → ssi-versions.js?_=timestamp → versions.json → correct ?v= for all assets
 */
(function() {
  'use strict';

  // Detect base path: country pages use ../, root pages use ./
  var path = window.location.pathname;
  var isCountryPage = /^\/(france|italy|uk|spain|germany|switzerland|austria|us|canada|japan|australia|chile)\//i.test(path);
  var base = isCountryPage ? '../' : './';

  // Fetch versions.json with timestamp cache-bust (never cached)
  var ts = Date.now();
  fetch(base + 'versions.json?_=' + ts, { cache: 'no-store' })
    .then(function(r) { return r.json(); })
    .then(function(manifest) {
      window.SSI_VERSIONS = manifest.assets;
      window.SSI_VERSION_ID = manifest.v;

      // Helper: get versioned URL for any asset
      window.ssiAssetUrl = function(assetKey, filename) {
        var v = (manifest.assets && manifest.assets[assetKey]) || ts;
        return filename + '?v=' + v;
      };

      // Fire event so pages can react
      document.dispatchEvent(new CustomEvent('ssi-versions-ready', { detail: manifest }));
    })
    .catch(function(err) {
      console.warn('[SSI-Versions] Failed to load versions.json, using timestamp fallback:', err.message);
      // Fallback: use timestamp-based cache-busting (always fresh, no caching benefit)
      window.SSI_VERSIONS = {};
      window.SSI_VERSION_ID = 0;
      window.ssiAssetUrl = function(key, filename) { return filename + '?v=' + ts; };
      document.dispatchEvent(new CustomEvent('ssi-versions-ready', { detail: { v: 0, assets: {} } }));
    });
})();
