// Local stub for intelligence-loader.js
// The live site has a full edition-rotation loader; the local audit doesn't need it.
// Sets SSI_COUNTRY from the data-country attribute so inline scripts have it.
(function() {
    var s = document.currentScript || document.getElementById('ssi-esg-page');
    if (s && s.getAttribute && s.getAttribute('data-country')) {
        window.SSI_COUNTRY = s.getAttribute('data-country');
    }
    if (typeof window.SSI_EDITION === 'undefined') {
        window.SSI_EDITION = { number: 1, label: 'Edition 01', first_refresh: '2026-06-11' };
    }
})();
