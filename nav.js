/* ═══════════════════════════════════════════════════════════
   SSI Dashboard — Shared Navigation Component
   v4.0 — Session 5 Polish (logo, a11y, noscript)
   ═══════════════════════════════════════════════════════════ */

// Ikenga logo
const SSI_LOGO = `<img src="ikenga-logo.png" alt="Ikenga" style="height:187px;width:auto;display:block" />`;

function renderNav(activePage) {
  const pages = [
    { id: 'overview', label: 'Overview', href: 'index.html' },
    { id: 'map', label: 'Map Explorer', href: 'map.html' },
    { id: 'regional', label: 'Regional', href: 'regional.html' },
    { id: 'methodology', label: 'Methodology', href: 'methodology.html' },
    { id: 'data', label: 'Data & Download', href: 'data.html' },
  ];

  // Skip-link for keyboard/screen-reader users
  const skip = document.createElement('a');
  skip.href = '#main-content';
  skip.className = 'skip-link';
  skip.textContent = 'Skip to main content';
  document.body.prepend(skip);

  // Noscript banner (shows if JS somehow fails after initial load)
  const noscript = document.createElement('noscript');
  noscript.innerHTML = '<div class="noscript-banner">This dashboard requires JavaScript to display interactive data and maps.</div>';
  document.body.prepend(noscript);

  const nav = document.createElement('nav');
  nav.className = 'topnav';
  nav.setAttribute('role', 'navigation');
  nav.setAttribute('aria-label', 'Main navigation');
  nav.innerHTML = `
    <a class="topnav-brand" href="index.html" aria-label="SSI Index — Home" style="gap:10px">
      ${SSI_LOGO}
      <div style="display:flex;flex-direction:column;justify-content:center;line-height:1.15">
        <h1 style="margin:0;font-size:15px">SSI <span>Index</span> <span class="topnav-version">v4.0.2</span></h1>
      </div>
    </a>
    <button class="nav-toggle" onclick="document.querySelector('.topnav-links').classList.toggle('open')" aria-label="Toggle navigation menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <div class="topnav-links" role="menubar">
      ${pages.map(p => `<a href="${p.href}" role="menuitem" ${p.id === activePage ? 'class="active" aria-current="page"' : ''}>${p.label}</a>`).join('')}
    </div>
  `;

  document.body.prepend(nav);

  // Wire toggle aria-expanded
  const toggle = nav.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      const links = nav.querySelector('.topnav-links');
      const open = links.classList.contains('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Add id to main for skip link
  const main = document.querySelector('main');
  if (main) main.id = 'main-content';

  // Registration gate removed from page load — only triggered on download
}

// ── Registration Gate ──
// Google Sheets Apps Script endpoint — replace with your own
var SSI_REGISTRATION_ENDPOINT = 'https://script.google.com/macros/s/AKfycbyxWmA3HaVqFbF-OQQGJWRUmdVE4ciRI9ZgDavJ8ZJ21Irgq9fuUmUEgRmAqbL1BzLJ2g/exec';

function isRegistered() {
  try { return localStorage.getItem('ssi-registered') === '1'; } catch(e) { return false; }
}

function showRegistrationGate(onSuccess) {
  if (document.querySelector('.registration-overlay')) return; // already showing

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
    '<div class="reg-copyright" style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(44,36,32,0.08);font-size:8.5px;line-height:1.5;color:#8a7e76;text-align:center">Copyright \u00a9 2026 Altinium Invest S.r.L. All Rights Reserved. This software program protected by the United States Copyright Law, and Societ\u00e0 Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.</div>' +
  '</div>';

  document.body.appendChild(overlay);

  // Focus first input
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
      page: window.location.pathname,
      timestamp: new Date().toISOString()
    };

    // Send to Google Sheets via GET (Image beacon — reliable cross-origin)
    try {
      var params = Object.keys(payload).map(function(k) {
        return encodeURIComponent(k) + '=' + encodeURIComponent(payload[k]);
      }).join('&');
      var img = new Image();
      img.src = SSI_REGISTRATION_ENDPOINT + '?' + params;
    } catch(err) {}

    // Mark registered and remove overlay
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

// Called before downloads — returns true if registered, shows gate if not
function requireRegistration(callback) {
  if (isRegistered()) return true;
  showRegistrationGate(callback);
  return false;
}

function renderFooter() {
  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.setAttribute('role', 'contentinfo');
  footer.innerHTML = `
    <div>SSI Index v4.0.2 · Systemic System Infrastructure Index · <a href="https://ikenga.eu" target="_blank" rel="noopener noreferrer">Ikenga</a></div>
    <div>95 variables · 30 sources · 4,293 substations (475 HV · 3,818 MV) · Open data, open methodology</div>
    <div class="copyright-notice">Copyright &copy; 2026 Altinium Invest S.r.L. All Rights Reserved. This software program protected by the United States Copyright Law, and Societ&agrave; Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.</div>
  `;
  document.body.appendChild(footer);
}
