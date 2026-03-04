/* ═══════════════════════════════════════════════════════════
   SSI Dashboard — Shared Navigation Component
   v4.0 — Session 5 Polish (logo, a11y, noscript)
   ═══════════════════════════════════════════════════════════ */

// Ikenga-inspired logo mark (abstract shield/grid motif)
const SSI_LOGO = `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="2" y="2" width="10" height="10" rx="2" fill="#941914"/>
  <rect x="16" y="2" width="10" height="10" rx="2" fill="#aa4234"/>
  <rect x="2" y="16" width="10" height="10" rx="2" fill="#b8863a"/>
  <rect x="16" y="16" width="10" height="10" rx="2" fill="#5d8563"/>
  <rect x="9" y="9" width="10" height="10" rx="2" fill="#2c2420" fill-opacity="0.9"/>
  <text x="14" y="17" text-anchor="middle" font-size="7" font-weight="700" font-family="DM Sans, sans-serif" fill="white">SSI</text>
</svg>`;

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
    <a class="topnav-brand" href="index.html" aria-label="SSI Index — Home">
      ${SSI_LOGO}
      <h1>SSI <span>Index</span></h1>
      <span class="topnav-version">v4.0</span>
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
}

function renderFooter() {
  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.setAttribute('role', 'contentinfo');
  footer.innerHTML = `
    <div>SSI Index v4.0 · Systemic System Infrastructure Index · <a href="https://ikenga.eu" target="_blank" rel="noopener noreferrer">Ikenga</a></div>
    <div>81 variables · 30 sources · 4,293 substations · Open data, open methodology</div>
    <div class="copyright-notice">Copyright &copy; 2026 Altinium Invest S.r.L. All Rights Reserved. This software program protected by the United States Copyright Law, and Societ&agrave; Italiana degli Autori ed Editori, under the Berne Convention. Unauthorised reproduction, distribution, or modification of this software program is strictly prohibited and protected under international copyright treaties.</div>
  `;
  document.body.appendChild(footer);
}
