/* ═══════════════════════════════════════════════════════════
   SSI Dashboard — Shared Navigation Component
   v4.1 — Multi-country support (landing page + country subfolders)
   ═══════════════════════════════════════════════════════════ */

// >>> BEGIN AUTO-GENERATED FROM countries.json (do not edit by hand)
// Single source of truth: intelligence/countries.json (regenerate via
// scripts/generate_nav_data.py — pre-commit hook does this automatically).
// 38 countries as of last regeneration.

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
  'turkey': '\uD83C\uDDF9\uD83C\uDDF7 Turkey',
  'uk': '\uD83C\uDDEC\uD83C\uDDE7 United Kingdom',
  'us': '\uD83C\uDDFA\uD83C\uDDF8 United States'
};

var SSI_COUNTRY_STATS_DEFAULT = {
  'australia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'austria': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'belgium': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'canada': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'chile': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'colombia': '95 variables \u00b7 substations: 381 \u00b7 33 regions',
  'costa-rica': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'czechia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'denmark': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'estonia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'finland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'france': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'germany': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'greece': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'greenland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'hungary': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'iceland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'ireland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'israel': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'italy': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'japan': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'korea': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'latvia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'lithuania': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'luxembourg': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'mexico': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'netherlands': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'new-zealand': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'norway': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'poland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'portugal': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'slovakia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'slovenia': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'spain': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'sweden': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'switzerland': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'turkey': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'uk': '95 variables \u00b7 substations: ? \u00b7 ? regions',
  'us': '95 variables \u00b7 substations: ? \u00b7 ? regions'
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
        '<h1 style="margin:0;font-size:15px">SSI <span>Index</span> <span class="topnav-version">v4.0.2</span></h1>' +
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
  var countryStats = {
    italy: '95 variables · 30 sources · 4,293 substations (475 HV · 3,818 MV)',
    germany: '95 variables · 35 sources · 401 Kreise across 16 Bundesländer',
    austria: '95 variables · 35 sources · 1,406 substations (1,144 HV · 262 MV) across 9 Bundesländer',
    switzerland: '95 variables · 25 sources · 947 substations (147 HV · 776 MV) across 26 Cantons',
    japan: '95 variables \u00b7 30+ sources \u00b7 5,981 substations (299 EHV \u00b7 5,682 HV) across 10 EPCO territories',
      australia: '95 variables · 20+ sources · 8,500 substations (1,705 HV · 6,795 MV) across 8 states/territories',
    france: '95 variables · 35 sources · 7,898 substations (996 HV · 6,902 MV) across 13 Régions',
    spain: '95 variables · 30 sources · 3,793 substations across 52 Provincias · 19 Comunidades Autónomas',
    us: '95 variables · 40 sources · 45,003 substations (1,726 HV · 36,654 MV) across 52 states',
    mexico: '95 variables · 25+ sources · 3,140 substations · 30,396 power lines across 32 Estados',
    greece: '95 variables · 30 sources · 581 substations (71 HV · 410 MV · 100 LV) across 13 Periphereies',
    turkey: '95 variables · 30 sources · 4,092 substations (1,132 HV · 2,960 MV) across 81 İller',
    ireland: '95 variables · 30 sources · 994 substations (319 HV · 675 MV) · 4,505 power lines across 26 Counties · 4 Provinces',
    portugal: '95 variables · 28 sources · 10,191 substations (168 HV · 708 MV) · 11,043 power lines across 20 Distritos · 7 Regiões',
    'new-zealand': '95 variables · 28 sources · 1,558 substations (200 HV ≥110 kV · 1,358 MV <110 kV) across 16 Regions · 2 Islands',
    greenland: '95 variables · 25 sources · ~250 substations (15 HV · 235 MV) · ~70 islanded micro-grids across 5 Kommuner · Pituffik excluded',
    czechia: '95 variables · 30 sources · 1,077 substations (7 HV · 288 MV · 782 distribution-tier) · 6,484 power lines across 14 Kraje · 206 ORP',
    belgium: '95 variables · 28 sources · 1,220 substations (254 HV ≥110 kV · 202 MV 20–110 kV · 764 distribution-tier) · 4,017 power lines across 11 Provinces · 581 Communes/Gemeenten',
    netherlands: '95 variables · 28 sources · 1,640 substations (528 HV ≥110 kV · 265 MV 20–110 kV · 847 distribution-tier) · 4,757 power lines across 12 Provinces · 342 Gemeenten',
  estonia: '95 variables · 28 sources · 614 substations (165 HV · 37 MV · 412 distribution-tier) · 3,769 power lines / 9,484 km transmission network across 15 Maakond · 79 Omavalitsus',
  latvia: '95 variables · 28 sources · 1,219 substations (132 HV ≥330 kV · 628 HV 110-330 kV · 459 distribution-tier) · 16,245 power lines / 27,056 km transmission network across 6 NUTS-3 regions · 43 novadi (post-2021 reform)',
  lithuania: '95 variables · 28 sources · 505 substations (298 HV ≥110 kV · 170 MV 33-110 kV · 24 MV-low · 13 untagged) · 2,527 power lines across 10 NUTS-3 apskritys · 60 savivaldybės (LAU)',
  slovenia: '95 variables · 30+ sources · 158 substations (21 EHV 400/220 kV · 137 HV 110 kV) · 4,384 power lines / ~860 grid lines across 12 NUTS-3 statistical regions · 212 občine (LAU) · ELES TSO + 5 Elektro DSOs under SODO'
};
  var stats = SSI_COUNTRY && countryStats[SSI_COUNTRY] ? countryStats[SSI_COUNTRY] : 'Open data, open methodology · Pan-European grid resilience';

  var footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.setAttribute('role', 'contentinfo');
  footer.innerHTML =
    '<div>SSI Index v4.0.2 · Systemic System Infrastructure Index · <a href="https://ikenga.eu" target="_blank" rel="noopener noreferrer">Ikenga</a></div>' +
    '<div>' + stats + '</div>' +
    '<div class="copyright-notice">Copyright &copy; 2026 Altinium Invest S.r.L. All Rights Reserved. This software program protected by the United States Copyright Law, and Societ&agrave; Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.</div>';
  document.body.appendChild(footer);
}
