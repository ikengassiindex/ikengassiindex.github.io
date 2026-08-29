/* ═══════════════════════════════════════════════════════════
   SSI Dashboard — Shared Navigation Component
   v4.2 — Multi-country support (landing page + country subfolders) — 11 modifiers + Re composite (LP-10, 18 Jun 2026)
   ═══════════════════════════════════════════════════════════ */

// >>> BEGIN AUTO-GENERATED FROM countries.json (do not edit by hand)
// Single source of truth: intelligence/countries.json (regenerate via
// scripts/generate_nav_data.py — pre-commit hook does this automatically).
// 39 countries as of last regeneration.

var SSI_COUNTRY_SLUGS = [
  'australia',
  'austria',
  'belgium',
  'canada',
  'chile',
  'colombia',
  'costa-rica',
  'czechia',
  'denmark',
  'estonia',
  'finland',
  'france',
  'germany',
  'greece',
  'greenland',
  'hungary',
  'iceland',
  'ireland',
  'israel',
  'italy',
  'japan',
  'korea',
  'latvia',
  'lithuania',
  'luxembourg',
  'mexico',
  'netherlands',
  'new-zealand',
  'norway',
  'poland',
  'portugal',
  'slovakia',
  'slovenia',
  'spain',
  'sweden',
  'switzerland',
  'turkey',
  'uk',
  'us'
];
var SSI_COUNTRY_PATH_RE = new RegExp('/(' + SSI_COUNTRY_SLUGS.join('|') + ')/');

var SSI_COUNTRY_LABELS = {
  'australia': '\uD83C\uDDE6\uD83C\uDDFA Australia',
  'austria': '\uD83C\uDDE6\uD83C\uDDF9 Austria',
  'belgium': '\uD83C\uDDE7\uD83C\uDDEA Belgium',
  'canada': '\uD83C\uDDE8\uD83C\uDDE6 Canada',
  'chile': '\uD83C\uDDE8\uD83C\uDDF1 Chile',
  'colombia': '\uD83C\uDDE8\uD83C\uDDF4 Colombia',
  'costa-rica': '\uD83C\uDDE8\uD83C\uDDF7 Costa Rica',
  'czechia': '\uD83C\uDDE8\uD83C\uDDFF Czechia',
  'denmark': '\uD83C\uDDE9\uD83C\uDDF0 Denmark',
  'estonia': '\uD83C\uDDEA\uD83C\uDDEA Estonia',
  'finland': '\uD83C\uDDEB\uD83C\uDDEE Finland',
  'france': '\uD83C\uDDEB\uD83C\uDDF7 France',
  'germany': '\uD83C\uDDE9\uD83C\uDDEA Germany',
  'greece': '\uD83C\uDDEC\uD83C\uDDF7 Greece',
  'greenland': '\uD83C\uDDEC\uD83C\uDDF1 Greenland',
  'hungary': '\uD83C\uDDED\uD83C\uDDFA Hungary',
  'iceland': '\uD83C\uDDEE\uD83C\uDDF8 Iceland',
  'ireland': '\uD83C\uDDEE\uD83C\uDDEA Ireland',
  'israel': '\uD83C\uDDEE\uD83C\uDDF1 Israel',
  'italy': '\uD83C\uDDEE\uD83C\uDDF9 Italy',
  'japan': '\uD83C\uDDEF\uD83C\uDDF5 Japan',
  'korea': '\uD83C\uDDF0\uD83C\uDDF7 Republic of Korea',
  'latvia': '\uD83C\uDDF1\uD83C\uDDFB Latvia',
  'lithuania': '\uD83C\uDDF1\uD83C\uDDF9 Lithuania',
  'luxembourg': '\uD83C\uDDF1\uD83C\uDDFA Luxembourg',
  'mexico': '\uD83C\uDDF2\uD83C\uDDFD Mexico',
  'netherlands': '\uD83C\uDDF3\uD83C\uDDF1 Netherlands',
  'new-zealand': '\uD83C\uDDF3\uD83C\uDDFF New Zealand',
  'norway': '\uD83C\uDDF3\uD83C\uDDF4 Norway',
  'poland': '\uD83C\uDDF5\uD83C\uDDF1 Poland',
  'portugal': '\uD83C\uDDF5\uD83C\uDDF9 Portugal',
  'slovakia': '\uD83C\uDDF8\uD83C\uDDF0 Slovakia',
  'slovenia': '\uD83C\uDDF8\uD83C\uDDEE Slovenia',
  'spain': '\uD83C\uDDEA\uD83C\uDDF8 Spain',
  'sweden': '\uD83C\uDDF8\uD83C\uDDEA Sweden',
  'switzerland': '\uD83C\uDDE8\uD83C\uDDED Switzerland',
  'turkey': '\uD83C\uDDF9\uD83C\uDDF7 Türkiye',
  'uk': '\uD83C\uDDEC\uD83C\uDDE7 United Kingdom',
  'us': '\uD83C\uDDFA\uD83C\uDDF8 United States'
};

var SSI_COUNTRY_STATS_DEFAULT = {
  'australia': '95 variables \u00B7 20+ sources \u00B7 12,565 substations (2,050 EHV \u2265220 kV \u00B7 2,855 HV 110\u2013220 kV \u00B7 7,660 distribution-tier) \u00B7 45,776 power lines across 8 states/territories',
  'austria': '95 variables \u00B7 35 sources \u00B7 14,720 substations (95 EHV \u2265220 kV \u00B7 555 HV 110\u2013220 kV \u00B7 14,070 distribution-tier) \u00B7 35,377 power lines across 40 Bundesl\u00E4nder',
  'belgium': '95 variables \u00B7 28 sources \u00B7 6,651 substations (71 EHV \u2265220 kV \u00B7 200 HV 110\u2013220 kV \u00B7 6,380 distribution-tier) \u00B7 7,232 power lines across 45 Provinces \u00B7 581 Communes/Gemeenten',
  'canada': '95 variables \u00B7 7,506 substations (786 EHV \u2265220 kV \u00B7 1,355 HV 110\u2013220 kV \u00B7 5,365 distribution-tier) \u00B7 19,553 power lines across 12 regions',
  'chile': '95 variables \u00B7 1,035 substations (381 EHV \u2265220 kV \u00B7 331 HV 110\u2013220 kV \u00B7 323 distribution-tier) \u00B7 4,191 power lines across 16 regions',
  'colombia': '95 variables \u00B7 744 substations (125 EHV \u2265220 kV \u00B7 333 HV 110\u2013220 kV \u00B7 286 distribution-tier) \u00B7 2,692 power lines across 33 regions',
  'costa-rica': '95 variables \u00B7 169 substations (91 EHV \u2265220 kV \u00B7 76 HV 110\u2013220 kV \u00B7 2 distribution-tier) \u00B7 770 power lines across 7 regions',
  'czechia': '95 variables \u00B7 30 sources \u00B7 8,899 substations (53 EHV \u2265220 kV \u00B7 434 HV 110\u2013220 kV \u00B7 8,412 distribution-tier) \u00B7 54,743 power lines across 14 Kraje \u00B7 206 ORP',
  'denmark': '95 variables \u00B7 4,822 substations (37 EHV \u2265220 kV \u00B7 149 HV 110\u2013220 kV \u00B7 4,636 distribution-tier) \u00B7 4,924 power lines across 16 regions',
  'estonia': '95 variables \u00B7 28 sources \u00B7 1,794 substations (22 EHV \u2265220 kV \u00B7 149 HV 110\u2013220 kV \u00B7 1,623 distribution-tier) \u00B7 5,753 power lines across 15 Maakond \u00B7 79 Omavalitsus',
  'finland': '95 variables \u00B7 3,939 substations (93 EHV \u2265220 kV \u00B7 3,766 HV 110\u2013220 kV \u00B7 80 distribution-tier) \u00B7 23,601 power lines across 20 regions',
  'france': '95 variables \u00B7 35 sources \u00B7 168,894 substations (47,172 EHV \u2265220 kV \u00B7 72 HV 110\u2013220 kV \u00B7 121,650 distribution-tier) \u00B7 274,201 power lines across 13 R\u00E9gions',
  'germany': '95 variables \u00B7 35 sources \u00B7 108,016 substations (4,463 EHV \u2265220 kV \u00B7 4,735 HV 110\u2013220 kV \u00B7 98,818 distribution-tier) \u00B7 262,134 power lines across 409 Bundesl\u00E4nder',
  'greece': '95 variables \u00B7 30 sources \u00B7 719 substations (65 EHV \u2265220 kV \u00B7 422 HV 110\u2013220 kV \u00B7 232 distribution-tier) \u00B7 1,775 power lines across 55 Periphereies',
  'greenland': '95 variables \u00B7 25 sources \u00B7 43 substations (0 EHV \u2265220 kV \u00B7 0 HV 110\u2013220 kV \u00B7 43 distribution-tier) \u00B7 128 power lines across 5 Kommuner \u00B7 Pituffik excluded',
  'hungary': '95 variables \u00B7 3,507 substations (65 EHV \u2265220 kV \u00B7 307 HV 110\u2013220 kV \u00B7 3,135 distribution-tier) \u00B7 32,278 power lines across 20 regions',
  'iceland': '95 variables \u00B7 685 substations (21 EHV \u2265220 kV \u00B7 261 HV 110\u2013220 kV \u00B7 403 distribution-tier) \u00B7 1,566 power lines across 8 regions',
  'ireland': '95 variables \u00B7 30 sources \u00B7 1,278 substations (58 EHV \u2265220 kV \u00B7 268 HV 110\u2013220 kV \u00B7 952 distribution-tier) \u00B7 59,129 power lines across 26 Counties \u00B7 4 Provinces',
  'israel': '95 variables \u00B7 257 substations (18 EHV \u2265220 kV \u00B7 239 HV 110\u2013220 kV \u00B7 0 distribution-tier) \u00B7 6,363 power lines across 6 regions',
  'italy': '95 variables \u00B7 30 sources \u00B7 41,662 substations (1,187 EHV \u2265220 kV \u00B7 3,802 HV 110\u2013220 kV \u00B7 36,673 distribution-tier) \u00B7 94,407 power lines across 117 regions',
  'japan': '95 variables \u00B7 30+ sources \u00B7 6,168 substations (459 EHV \u2265220 kV \u00B7 578 HV 110\u2013220 kV \u00B7 5,131 distribution-tier) \u00B7 43,328 power lines across 10 EPCO territories',
  'korea': '95 variables \u00B7 1,291 substations (191 EHV \u2265220 kV \u00B7 755 HV 110\u2013220 kV \u00B7 345 distribution-tier) \u00B7 4,245 power lines across 17 regions',
  'latvia': '95 variables \u00B7 28 sources \u00B7 4,646 substations (21 EHV \u2265220 kV \u00B7 133 HV 110\u2013220 kV \u00B7 4,492 distribution-tier) \u00B7 18,000 power lines across 6 NUTS-3 regions \u00B7 43 novadi (post-2021 reform)',
  'lithuania': '95 variables \u00B7 28 sources \u00B7 4,901 substations (37 EHV \u2265220 kV \u00B7 271 HV 110\u2013220 kV \u00B7 4,593 distribution-tier) \u00B7 3,982 power lines across 10 NUTS-3 apskritys \u00B7 60 savivaldyb\u0117s (LAU)',
  'luxembourg': '95 variables \u00B7 723 substations (19 EHV \u2265220 kV \u00B7 0 HV 110\u2013220 kV \u00B7 704 distribution-tier) \u00B7 1,343 power lines across 12 regions',
  'mexico': '95 variables \u00B7 25+ sources \u00B7 3,085 substations (627 EHV \u2265220 kV \u00B7 1,867 HV 110\u2013220 kV \u00B7 591 distribution-tier) \u00B7 17,208 power lines across 32 Estados',
  'netherlands': '95 variables \u00B7 28 sources \u00B7 5,449 substations (128 EHV \u2265220 kV \u00B7 450 HV 110\u2013220 kV \u00B7 4,871 distribution-tier) \u00B7 8,693 power lines across 43 Provinces \u00B7 342 Gemeenten',
  'new-zealand': '95 variables \u00B7 28 sources \u00B7 1,589 substations (91 EHV \u2265220 kV \u00B7 110 HV 110\u2013220 kV \u00B7 1,388 distribution-tier) \u00B7 76,379 power lines across 15 regions',
  'norway': '95 variables \u00B7 6,113 substations (217 EHV \u2265220 kV \u00B7 585 HV 110\u2013220 kV \u00B7 5,311 distribution-tier) \u00B7 154,728 power lines across 21 regions',
  'poland': '95 variables \u00B7 27,764 substations (166 EHV \u2265220 kV \u00B7 2,123 HV 110\u2013220 kV \u00B7 25,475 distribution-tier) \u00B7 105,254 power lines across 74 regions',
  'portugal': '95 variables \u00B7 28 sources \u00B7 13,564 substations (1,444 EHV \u2265220 kV \u00B7 52 HV 110\u2013220 kV \u00B7 12,068 distribution-tier) \u00B7 78,971 power lines across 29 regions',
  'slovakia': '95 variables \u00B7 1,517 substations (39 EHV \u2265220 kV \u00B7 955 HV 110\u2013220 kV \u00B7 523 distribution-tier) \u00B7 20,188 power lines across 8 regions',
  'slovenia': '95 variables \u00B7 30+ sources \u00B7 1,731 substations (20 EHV \u2265220 kV \u00B7 2 HV 110\u2013220 kV \u00B7 1,709 distribution-tier) \u00B7 4,510 power lines across 12 NUTS-3 statistical regions \u00B7 212 ob\u010Dine (LAU) \u00B7 ELES TSO + 5 Elektro DSOs under SODO',
  'spain': '95 variables \u00B7 30 sources \u00B7 12,438 substations (1,028 EHV \u2265220 kV \u00B7 1,043 HV 110\u2013220 kV \u00B7 10,367 distribution-tier) \u00B7 96,761 power lines across 65 regions',
  'sweden': '95 variables \u00B7 3,774 substations (239 EHV \u2265220 kV \u00B7 3,120 HV 110\u2013220 kV \u00B7 415 distribution-tier) \u00B7 15,421 power lines across 21 regions',
  'switzerland': '95 variables \u00B7 25 sources \u00B7 1,812 substations (158 EHV \u2265220 kV \u00B7 200 HV 110\u2013220 kV \u00B7 1,454 distribution-tier) \u00B7 8,657 power lines across 26 Cantons',
  'turkey': '95 variables \u00B7 30 sources \u00B7 4,031 substations (1,120 EHV \u2265220 kV \u00B7 1 HV 110\u2013220 kV \u00B7 2,910 distribution-tier) \u00B7 8,061 power lines across 84 regions',
  'uk': '95 variables \u00B7 59,744 substations (766 EHV \u2265220 kV \u00B7 1,979 HV 110\u2013220 kV \u00B7 56,999 distribution-tier) \u00B7 190,235 power lines across 12 regions',
  'us': '95 variables \u00B7 40 sources \u00B7 73,859 substations (7,107 EHV \u2265220 kV \u00B7 23,112 HV 110\u2013220 kV \u00B7 43,640 distribution-tier) \u00B7 875,933 power lines across 52 states'
};
// <<< END AUTO-GENERATED

// Detect base path + active country from URL (uses SLUGS + REGEX from auto-section above)
var _ssiPathMatch = window.location.pathname.match(SSI_COUNTRY_PATH_RE);
var SSI_BASE = _ssiPathMatch ? '../' : '';
var SSI_COUNTRY = _ssiPathMatch ? _ssiPathMatch[1] : null;

// Ikenga logo
var SSI_LOGO = '<img src="' + SSI_BASE + 'ikenga-logo.png" alt="Ikenga" style="height:187px;width:auto;display:block" />';

function renderNav(activePage) {
  var pages = [
    { id: 'overview', label: 'Overview', href: 'index.html' },
    { id: 'map', label: 'Map Explorer', href: 'map.html' },
    { id: 'regional', label: 'Regional', href: 'regional.html' },
    { id: 'methodology', label: 'Methodology', href: 'methodology.html' },
    { id: 'data', label: 'Data & Download', href: 'data.html' },
    { id: 'intelligence', label: 'Intelligence', href: 'intelligence.html' },
    { id: 'esg-report', label: 'ESG Report', href: 'esg-report.html' },
  ];

  // Skip-link for keyboard/screen-reader users
  var skip = document.createElement('a');
  skip.href = '#main-content';
  skip.className = 'skip-link';
  skip.textContent = 'Skip to main content';
  document.body.prepend(skip);

  // Noscript banner
  var noscript = document.createElement('noscript');
  noscript.innerHTML = '<div class="noscript-banner">This dashboard requires JavaScript to display interactive data and maps.</div>';
  document.body.prepend(noscript);

  var countryLabel = SSI_COUNTRY ? SSI_COUNTRY_LABELS[SSI_COUNTRY] || SSI_COUNTRY : '';
  var backLink = SSI_COUNTRY ? '<a href="' + SSI_BASE + 'index.html" class="nav-back" aria-label="Back to country selection">← All Countries</a>' : '';

  var nav = document.createElement('nav');
  nav.className = 'topnav';
  nav.setAttribute('role', 'navigation');
  nav.setAttribute('aria-label', 'Main navigation');
  nav.innerHTML =
    '<a class="topnav-brand" href="https://ikenga.eu" target="_blank" rel="noopener" aria-label="Ikenga — Visit website" style="gap:10px">' +
      SSI_LOGO +
      '<div style="display:flex;flex-direction:column;justify-content:center;line-height:1.15">' +
        '<h1 style="margin:0;font-size:15px">SSI <span>Index</span> <span class="topnav-version">v4.2</span></h1>' +
      '</div>' +
    '</a>' +
    (countryLabel ? '<div class="nav-country-badge">' + countryLabel + '</div>' : '') +
    backLink +
    '<button class="nav-toggle" onclick="document.querySelector(\'.topnav-links\').classList.toggle(\'open\')" aria-label="Toggle navigation menu" aria-expanded="false">' +
      '<span></span><span></span><span></span>' +
    '</button>' +
    '<div class="topnav-links" role="menubar">' +
      pages.map(function(p) {
        return '<a href="' + p.href + '" role="menuitem" ' +
          (p.id === activePage ? 'class="active" aria-current="page"' : '') + '>' +
          p.label + '</a>';
      }).join('') +
    '</div>';

  document.body.prepend(nav);

  // Wire toggle aria-expanded
  var toggle = nav.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var links = nav.querySelector('.topnav-links');
      var open = links.classList.contains('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Add id to main for skip link
  var main = document.querySelector('main');
  if (main) main.id = 'main-content';
}

// ── Registration Gate ──
var SSI_REGISTRATION_ENDPOINT = 'https://script.google.com/macros/s/AKfycbyxWmA3HaVqFbF-OQQGJWRUmdVE4ciRI9ZgDavJ8ZJ21Irgq9fuUmUEgRmAqbL1BzLJ2g/exec';

function isRegistered() {
  try { return localStorage.getItem('ssi-registered') === '1'; } catch(e) { return false; }
}

function showRegistrationGate(onSuccess) {
  if (document.querySelector('.registration-overlay')) return;

  var overlay = document.createElement('div');
  overlay.className = 'registration-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-labelledby', 'reg-title');

  overlay.innerHTML = '<div class="registration-modal">' +
    '<h2 id="reg-title">Breaking the Silos</h2>' +
    '<p class="reg-subtitle">Power grid resilience is inseparable from its socio-economic context. ' +
    'A substation serving an energy-poor region with slow restoration times and weak fiscal capacity ' +
    'is fundamentally more vulnerable than one with identical electrical characteristics in a prosperous area. ' +
    'The SSI captures this reality by fusing traditional grid metrics with socio-economic, environmental, ' +
    'and energy-transition data\u00a0\u2014\u00a0all from public sources.</p>' +
    '<form id="reg-form" autocomplete="on">' +
      '<label for="reg-email">Email</label>' +
      '<input id="reg-email" name="email" type="email" required placeholder="you@organisation.com" autocomplete="email">' +
      '<label for="reg-org">Organisation</label>' +
      '<input id="reg-org" name="organisation" type="text" required placeholder="Company or institution name" autocomplete="organization">' +
      '<label for="reg-type">Organisation type</label>' +
      '<select id="reg-type" name="org_type" required>' +
        '<option value="" disabled selected>Select\u2026</option>' +
        '<option value="Company">Company</option>' +
        '<option value="Research">Research</option>' +
        '<option value="Regulator">Regulator</option>' +
        '<option value="Other">Other</option>' +
      '</select>' +
      '<label for="reg-role">Your role</label>' +
      '<input id="reg-role" name="role" type="text" required placeholder="e.g. Grid Analyst, Head of Strategy" autocomplete="organization-title">' +
      '<button type="submit">Access the SSI Index</button>' +
    '</form>' +
    '<div class="reg-footer">Your data is handled by Altinium Invest S.r.L. and will not be shared with third parties.</div>' +
    '<div class="reg-copyright" style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(44,36,32,0.08);font-size:8.5px;line-height:1.5;color:#8a7e76;text-align:center">Copyright \u00a9 2026 Altinium Invest S.r.L. All Rights Reserved.</div>' +
  '</div>';

  document.body.appendChild(overlay);

  setTimeout(function() {
    var first = document.getElementById('reg-email');
    if (first) first.focus();
  }, 100);

  document.getElementById('reg-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var btn = this.querySelector('button[type="submit"]');
    btn.textContent = 'Submitting\u2026';
    btn.disabled = true;

    var payload = {
      email: document.getElementById('reg-email').value.trim(),
      organisation: document.getElementById('reg-org').value.trim(),
      org_type: document.getElementById('reg-type').value,
      role: document.getElementById('reg-role').value.trim(),
      country: SSI_COUNTRY || 'landing',
      page: window.location.pathname,
      timestamp: new Date().toISOString()
    };

    try {
      var params = Object.keys(payload).map(function(k) {
        return encodeURIComponent(k) + '=' + encodeURIComponent(payload[k]);
      }).join('&');
      var img = new Image();
      img.src = SSI_REGISTRATION_ENDPOINT + '?' + params;
    } catch(err) {}

    try { localStorage.setItem('ssi-registered', '1'); } catch(err) {}
    overlay.style.animation = 'regFadeIn 0.3s ease reverse forwards';
    setTimeout(function() {
      overlay.remove();
      if (typeof onSuccess === 'function') onSuccess();
    }, 300);
  });
}

function renderRegistrationGate() {
  if (!isRegistered()) {
    showRegistrationGate();
  }
}

function requireRegistration(callback) {
  if (isRegistered()) return true;
  showRegistrationGate(callback);
  return false;
}

function renderFooter() {
  // Figures come from SSI_COUNTRY_STATS_DEFAULT in the auto-generated
  // section above, which generate_nav_data.py derives from the data
  // files. The hand-written map that used to live here disagreed with
  // its own data on 22 of 22 countries across 110 pages.
  var stats = (SSI_COUNTRY && typeof SSI_COUNTRY_STATS_DEFAULT !== 'undefined'
               && SSI_COUNTRY_STATS_DEFAULT[SSI_COUNTRY])
    ? SSI_COUNTRY_STATS_DEFAULT[SSI_COUNTRY] : 'Open data, open methodology · Pan-European grid resilience';

  var footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.setAttribute('role', 'contentinfo');
  footer.innerHTML =
    '<div>SSI Index v4.2 · Systemic System Infrastructure Index · <a href="https://ikenga.eu" target="_blank" rel="noopener noreferrer">Ikenga</a></div>' +
    '<div>' + stats + '</div>' +
    '<div class="copyright-notice">Copyright &copy; 2026 Altinium Invest S.r.L. All Rights Reserved. This software program protected by the United States Copyright Law, and Societ&agrave; Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.</div>';
  document.body.appendChild(footer);
}
