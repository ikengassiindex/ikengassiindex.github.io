
// Load countries.json config (currencies, flags, admin labels)
(function() {
  var base = window.SSI_BASE || (window.location.pathname.match(/^\/\w+\//) ? '../' : './');
  fetch(base + 'countries.json?v=1', {cache: 'no-store'})
    .then(function(r) { return r.json(); })
    .then(function(cfg) { window.SSI_COUNTRIES_CONFIG = cfg; })
    .catch(function() { window.SSI_COUNTRIES_CONFIG = {}; });
})();

/* ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   SSI Index Dashboard v4.0.2  Interactive Map Engine
   Canvas-based renderer for 4,293 substations (HV/MV/LV) + 14,221 lines
    */
 
(function () {
  'use strict';

  // ------ State ------
  let GEO = null;           // grid-geo.json { l, s, a }
  let SSI = null;            // ssi-data.json { meta, fleet_summary, regions, substations }
  let BOUNDS = null;         // bounds.json (optional country/province polygon GeoJSON)
  let ssiMap = {};           // internal_id  substation record (fast lookup)
  let lineById = {};         // line.i  line object (fast lookup)
  let canvas, ctx;
  let W, H;
  let view = { cx: 12.5, cy: 42.0, scale: 1 };
  let dragging = false, dragStart = null, dragViewStart = null, didDrag = false;
  let sel = { type: null, id: null };
  let hlLines = new Set(), hlSubs = new Set(), hlSubsPrimary = new Set();
  let hoverHit = null;
  let filters = { band: 'all', region: 'all', voltage: 'all', component: 'overall' };
  let searchQuery = '';
  let animFrame = null;
  let loadedCallback = null;
  let isEmbedded = false;    // true when used in overview page mini-map
  let fleetMedian = { C: 0, V: 0, I: 0, E: 0, S: 0, T: 0 }; // for radar overlay
  let breakdownOpen = false; // toggle state for Score Breakdown

  const COS42 = Math.cos(42 * Math.PI / 180);

  // ------ Ikenga Colors ------
  // Phase 2B-2 (25 June 2026): 5-band system; Extreme = #5a0d0a (darker
  // crimson, operator Q1(b) colour choice A). Extreme captures R_median
  // in [1.00, 1.30] — the additive-R6c_flood overflow zone.
  const BAND_COLORS = {
    Low: '#5d8563',
    Medium: '#b8863a',
    High: '#aa4234',
    Critical: '#941914',
    Extreme: '#5a0d0a'
  };

  const KV_COLORS = {
    380: '#941914',
    220: '#b8863a',
    150: '#aa4234',
    132: '#5d8563'
  };

  function kvColor(kv) {
    if (kv >= 300) return '#941914';
    if (kv >= 200) return '#b8863a';
    if (kv >= 140) return '#aa4234';
    if (kv >= 100) return '#5d8563';
    return '#8a7e76';
  }

  function kvWidth(kv) {
    if (kv >= 300) return 2.5;
    if (kv >= 200) return 2;
    if (kv >= 140) return 1.5;
    if (kv >= 100) return 1.2;
    return 0.8;
  }

  function bandColor(sub) {
    if (!sub) return '#8a7e76';
    const ssi = ssiMap[sub];
    if (!ssi) return '#8a7e76';
    // If fleet has spread, use classification directly
    if (window._ssiHasSpread) return BAND_COLORS[ssi.classification] || '#8a7e76';
    // Otherwise use fleet-percentile coloring for visual differentiation
    var pct = ssi.fleet_percentile || 0;
    if (pct >= 0.90) return BAND_COLORS['Critical'] || '#941914';
    if (pct >= 0.70) return BAND_COLORS['High'] || '#aa4234';
    if (pct >= 0.35) return BAND_COLORS['Medium'] || '#b8863a';
    return BAND_COLORS['Low'] || '#5d8563';
  }

  function componentColor(sub, comp) {
    if (!sub) return '#8a7e76';
    const ssi = ssiMap[sub];
    if (!ssi) return '#8a7e76';
    const val = ssi.components[comp] || 0;
    const weight = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 }[comp] || 0.20;
    const norm = Math.min(val / (weight * 0.8), 1); // normalise to component max
    // Green --- amber --- red gradient
    if (norm < 0.33) return `rgb(${93 + norm * 3 * 80}, ${133 - norm * 3 * 20}, 99)`;
    if (norm < 0.66) return `rgb(${184}, ${134 - (norm - 0.33) * 3 * 80}, ${58 - (norm - 0.33) * 3 * 20})`;
    return `rgb(${148 + (1 - norm) * 50}, ${25 + (1 - norm) * 30}, ${20})`;
  }

  function subColor(sid) {
    if (filters.component !== 'overall') {
      return componentColor(sid, filters.component);
    }
    return bandColor(sid);
  }

  // ------ Geo --- Screen projection ------
  function geoToScreen(lon, lat) {
    const f = view.scale * (W / 12.3);
    return [
      (lon - view.cx) * COS42 * f + W / 2,
      -(lat - view.cy) * f + H / 2
    ];
  }

  function screenToGeo(sx, sy) {
    const f = view.scale * (W / 12.3);
    return [
      (sx - W / 2) / (COS42 * f) + view.cx,
      -(sy - H / 2) / f + view.cy
    ];
  }

  // ------ Filtering ------
  function linePassesVoltageFilter(kv) {
    if (filters.voltage === 'all') return true;
    if (filters.voltage === '380') return kv >= 300;
    if (filters.voltage === '220') return kv >= 200 && kv < 300;
    if (filters.voltage === '132') return kv >= 100 && kv < 200;
    if (filters.voltage === 'other') return kv < 100;
    return true;
  }

  function passesFilter(sid) {
    const ssi = ssiMap[sid];
    if (!ssi) return true; // show geo-only subs in grey
    if (filters.band !== 'all' && ssi.classification !== filters.band) return false;
    if (filters.region !== 'all' && ssi.region !== filters.region) return false;
    if (filters.voltage !== 'all') {
      const v = ssi.voltage_kv;
      if (filters.voltage === '380' && v < 300) return false;
      if (filters.voltage === '220' && (v < 200 || v >= 300)) return false;
      if (filters.voltage === '132' && (v < 100 || v >= 200)) return false;
      if (filters.voltage === 'other' && v >= 100) return false;
    }
    if (searchQuery && !ssi.name.toLowerCase().includes(searchQuery) &&
        !ssi.province.toLowerCase().includes(searchQuery) &&
        !ssi.substation_id.toLowerCase().includes(searchQuery)) return false;
    return true;
  }

  // ------ Drawing ------
  function requestDraw() {
    console.log('[map.js DRAWTRACE] requestDraw called, animFrame=', animFrame, 'at', new Error().stack.split('\n')[2]);
    if (!animFrame) animFrame = requestAnimationFrame(draw);
  }

  function draw() {
    console.log('[map.js DRAWTRACE] draw() entered, GEO?', !!GEO, 'GEO.s size?', GEO ? Object.keys(GEO.s||{}).length : 0, 'canvas?', !!canvas, 'W=', W, 'H=', H, 'view=', view.cx, view.cy, view.scale);
    animFrame = null;
    if (!GEO || !canvas) { console.warn('[map.js DRAWTRACE] draw() EARLY EXIT — GEO or canvas falsy'); return; }
    if (W === 0 || H === 0) { console.warn('[map.js DRAWTRACE] draw() proceeding with W or H = 0 — will paint nothing'); }
    ctx.clearRect(0, 0, W, H);

    const s = view.scale;
    const showLabels = s > 4;
    const showLines = s > 0.3;
    const subRadius = Math.max(1.5, Math.min(s * 1.8, 6));
    const isSelecting = sel.type !== null;
    const isFiltering = filters.band !== 'all' || filters.region !== 'all' || filters.voltage !== 'all' || searchQuery;

    // --- Draw admin bounds (provinces/regions polygon outline) ---
    if (BOUNDS && BOUNDS.features) {
      ctx.save();
      ctx.lineJoin = 'round';
      ctx.strokeStyle = 'rgba(44, 36, 32, 0.32)';      // warm-grey border, subtle — substations dominate visually
      ctx.fillStyle   = 'rgba(232, 220, 205, 0.45)';   // warm tan fill, lighter — matches FR/IT/ES no-overlay aesthetic
      ctx.lineWidth   = 0.9;                            // thinner — frames country without blockiness
      for (const f of BOUNDS.features) {
        const g = f.geometry;
        if (!g) continue;
        const polys = (g.type === 'Polygon') ? [g.coordinates] : (g.type === 'MultiPolygon') ? g.coordinates : [];
        for (const poly of polys) {
          ctx.beginPath();
          for (let ri = 0; ri < poly.length; ri++) {
            const ring = poly[ri];
            for (let j = 0; j < ring.length; j++) {
              const [sx, sy] = geoToScreen(ring[j][0], ring[j][1]);
              if (j === 0) ctx.moveTo(sx, sy);
              else ctx.lineTo(sx, sy);
            }
            ctx.closePath();
          }
          ctx.fill('evenodd');
          ctx.stroke();
        }
      }
      ctx.restore();
    }

    // --- Draw lines ---
    const voltageActive = filters.voltage !== 'all';
    if (showLines) {
      ctx.lineCap = 'round';
      for (const l of GEO.l) {
        const highlighted = hlLines.has(l.i);
        const matchesVoltage = linePassesVoltageFilter(l.kv);
        if (isSelecting && !highlighted) {
          ctx.globalAlpha = 0.08;
        } else if (voltageActive && !isSelecting) {
          // Voltage filter: highlight matching lines, heavily dim others
          ctx.globalAlpha = matchesVoltage ? 0.85 : 0.03;
        } else if (isFiltering && !isSelecting) {
          ctx.globalAlpha = highlighted ? 0.6 : 0.04;
        } else {
          ctx.globalAlpha = isSelecting ? 0.9 : 0.5;
        }
        const voltageBoosted = voltageActive && matchesVoltage && !isSelecting;
        ctx.strokeStyle = kvColor(l.kv);
        ctx.lineWidth = (highlighted || voltageBoosted ? kvWidth(l.kv) * 1.8 : kvWidth(l.kv)) * Math.min(s * 0.5, 1.5);

        ctx.beginPath();
        for (let j = 0; j < l.p.length; j++) {
          const [sx, sy] = geoToScreen(l.p[j][0], l.p[j][1]);
          if (j === 0) ctx.moveTo(sx, sy);
          else ctx.lineTo(sx, sy);
        }
        ctx.stroke();
      }
    }

    // --- Draw substations ---
    ctx.globalAlpha = 1;
    for (const [sid, sub] of Object.entries(GEO.s)) {
      const show = passesFilter(sid);
      const highlighted = hlSubs.has(sid);
      const primary = hlSubsPrimary.has(sid);
      const [sx, sy] = geoToScreen(sub.x, sub.y);

      // Skip off-screen
      if (sx < -20 || sx > W + 20 || sy < -20 || sy > H + 20) continue;

      if (isSelecting && !highlighted && !primary) {
        ctx.globalAlpha = show ? 0.15 : 0.05;
      } else if (!show) {
        ctx.globalAlpha = isFiltering ? 0.04 : 0.1;
      } else {
        ctx.globalAlpha = 1;
      }

      const r = primary ? subRadius * 2 : (highlighted ? subRadius * 1.4 : subRadius);
      const col = subColor(sid);

      // Glow for primary
      if (primary) {
        ctx.shadowColor = col;
        ctx.shadowBlur = 12;
      }

      ctx.fillStyle = col;
      ctx.beginPath();
      ctx.arc(sx, sy, r, 0, Math.PI * 2);
      ctx.fill();

      if (primary) {
        ctx.shadowBlur = 0;
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Labels at high zoom
      if (showLabels && sub.n && (show || highlighted)) {
        ctx.globalAlpha = isSelecting && !highlighted ? 0.3 : (isFiltering && !show ? 0.05 : 0.9);
        ctx.font = `500 ${Math.min(11, 9 + s * 0.3)}px "DM Sans", sans-serif`;
        ctx.fillStyle = '#2c2420';
        ctx.textAlign = 'left';
        ctx.fillText(sub.n, sx + r + 4, sy + 3);
      }
    }

    ctx.globalAlpha = 1;
  }

  // ------ Hit testing ------
  function hitTest(sx, sy) {
    // Defensive: GEO can be null when data-load failed. Avoid TypeError spam on mousemove.
    if (!GEO || !GEO.s) return null;
    const threshold = Math.max(8, 20 / view.scale);
    let bestDist = threshold;
    let bestHit = null;

    // Substations
    for (const [sid, sub] of Object.entries(GEO.s)) {
      const [px, py] = geoToScreen(sub.x, sub.y);
      const d = Math.hypot(sx - px, sy - py);
      if (d < bestDist) {
        bestDist = d;
        bestHit = { type: 'sub', id: sid, sub };
      }
    }

    // Lines (only if no sub hit)
    if (!bestHit && view.scale > 0.5) {
      bestDist = threshold * 1.5;
      for (let li = 0; li < GEO.l.length; li++) {
        const l = GEO.l[li];
        for (let j = 1; j < l.p.length; j++) {
          const [ax, ay] = geoToScreen(l.p[j - 1][0], l.p[j - 1][1]);
          const [bx, by] = geoToScreen(l.p[j][0], l.p[j][1]);
          const d = ptSegDist(sx, sy, ax, ay, bx, by);
          if (d < bestDist) {
            bestDist = d;
            bestHit = { type: 'line', id: li, line: l };
          }
        }
      }
    }

    return bestHit;
  }

  function ptSegDist(px, py, ax, ay, bx, by) {
    const dx = bx - ax, dy = by - ay;
    const lenSq = dx * dx + dy * dy;
    if (lenSq === 0) return Math.hypot(px - ax, py - ay);
    let t = ((px - ax) * dx + (py - ay) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
  }

  // ------ Selection ------
  function setSelection(type, id) {
    sel = { type, id };
    hlLines.clear(); hlSubs.clear(); hlSubsPrimary.clear();

    if (type === 'sub') {
      hlSubsPrimary.add(id); hlSubs.add(id);
      const adj = (GEO.a && Array.isArray(GEO.a[id])) ? GEO.a[id] : [];
      adj.forEach(li => {
        hlLines.add(li);
        const l = lineById[li];
        if (l) {
          if (l.ss >= 0) hlSubs.add(String(l.ss));
          if (l.se >= 0) hlSubs.add(String(l.se));
        }
      });
      updateDetailPanel(id);
      animateToSub(id);
    } else if (type === 'line') {
      const l = GEO.l[id];
      if (l) {
        hlLines.add(l.i);
        if (l.ss >= 0) { hlSubs.add(String(l.ss)); hlSubsPrimary.add(String(l.ss)); }
        if (l.se >= 0) { hlSubs.add(String(l.se)); hlSubsPrimary.add(String(l.se)); }
      }
    } else {
      clearDetailPanel();
    }
    requestDraw();
  }

  function clearSelection() {
    sel = { type: null, id: null };
    hlLines.clear(); hlSubs.clear(); hlSubsPrimary.clear();
    clearDetailPanel();
    requestDraw();
  }

  // ------ Animation ------
  function animateToSub(sid) {
    const sub = GEO.s[sid];
    if (!sub) return;
    const neighbors = [];
    const adj = (GEO.a && Array.isArray(GEO.a[sid])) ? GEO.a[sid] : [];
    adj.forEach(li => {
      const l = lineById[li];
      if (l) {
        const s1 = GEO.s[String(l.ss)];
        const s2 = GEO.s[String(l.se)];
        if (s1) neighbors.push(s1);
        if (s2) neighbors.push(s2);
      }
    });
    const allPts = [sub, ...neighbors];
    animateToFit(allPts);
  }

  function animateToFit(pts, padding) {
    if (!pts.length) return;
    padding = padding || 0.35;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    pts.forEach(p => {
      minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
    });
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const spanX = (maxX - minX) * (1 + padding);
    const spanY = (maxY - minY) * (1 + padding);
    const scaleX = spanX > 0 ? (W / 12.3) * COS42 / (spanX * (W / 12.3) * COS42 / W) : view.scale;
    const targetScale = Math.max(1, Math.min(20,
      Math.min(W / ((spanX || 0.5) * COS42 * (W / 12.3)), H / ((spanY || 0.5) * (W / 12.3)))
    ));

    const startCx = view.cx, startCy = view.cy, startScale = view.scale;
    const t0 = performance.now();
    const dur = 500;

    function step(now) {
      let t = Math.min((now - t0) / dur, 1);
      t = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; // ease
      view.cx = startCx + (cx - startCx) * t;
      view.cy = startCy + (cy - startCy) * t;
      view.scale = startScale + (targetScale - startScale) * t;
      requestDraw();
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ------ Radar Chart ------
  function drawRadarChart(canvasId, ssi) {
    const c = document.getElementById(canvasId);
    if (!c) return;
    const dpr = window.devicePixelRatio || 1;
    const size = 280;
    c.width = size * dpr;
    c.height = (size + 24) * dpr;
    c.style.width = size + 'px';
    c.style.height = (size + 24) + 'px';
    const cx2 = c.getContext('2d');
    cx2.setTransform(dpr, 0, 0, dpr, 0, 0);

    const keys = ['C', 'V', 'I', 'E', 'S', 'T'];
    const labels = ['Continuity', 'Voltage', 'Infra.', 'Economic', 'Saturation', 'Transition'];
    const weights = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 };
    const cols = { C: '#941914', V: '#aa4234', I: '#5d8563', E: '#3b9eff', S: '#b8863a', T: '#22d3ee' };
    const centerX = size / 2, centerY = size / 2 + 4;
    const radius = 80;
    const n = keys.length;

    function angle(i) { return (Math.PI * 2 * i / n) - Math.PI / 2; }
    function pointAt(i, r) {
      return [centerX + Math.cos(angle(i)) * r, centerY + Math.sin(angle(i)) * r];
    }

    // Background rings
    cx2.strokeStyle = 'rgba(44,36,32,0.06)';
    cx2.lineWidth = 0.5;
    for (let ring = 1; ring <= 4; ring++) {
      const r = radius * ring / 4;
      cx2.beginPath();
      for (let i = 0; i <= n; i++) {
        const [x, y] = pointAt(i % n, r);
        i === 0 ? cx2.moveTo(x, y) : cx2.lineTo(x, y);
      }
      cx2.stroke();
    }

    // Axis lines
    cx2.strokeStyle = 'rgba(44,36,32,0.08)';
    cx2.lineWidth = 0.5;
    for (let i = 0; i < n; i++) {
      cx2.beginPath();
      cx2.moveTo(centerX, centerY);
      const [x, y] = pointAt(i, radius);
      cx2.lineTo(x, y);
      cx2.stroke();
    }

    // Normalize: component / weight gives 0..1 (capped)
    var _compSum = keys.reduce(function(s,k){ return s + (ssi.components[k]||0); }, 0);
    var _isWeighted = _compSum <= 1.0;
    function norm(k, val) { return Math.min(_isWeighted ? val / weights[k] : val, 1); }

    // Fleet median polygon (faint reference)
    cx2.beginPath();
    for (let i = 0; i <= n; i++) {
      const k = keys[i % n];
      const v = norm(k, fleetMedian[k]);
      const [x, y] = pointAt(i % n, radius * v);
      i === 0 ? cx2.moveTo(x, y) : cx2.lineTo(x, y);
    }
    cx2.fillStyle = 'rgba(138,126,118,0.08)';
    cx2.fill();
    cx2.strokeStyle = 'rgba(138,126,118,0.3)';
    cx2.lineWidth = 1;
    cx2.setLineDash([4, 3]);
    cx2.stroke();
    cx2.setLineDash([]);

    // Substation polygon
    cx2.beginPath();
    for (let i = 0; i <= n; i++) {
      const k = keys[i % n];
      const v = norm(k, ssi.components[k]);
      const [x, y] = pointAt(i % n, radius * v);
      i === 0 ? cx2.moveTo(x, y) : cx2.lineTo(x, y);
    }
    const bandCol = BAND_COLORS[ssi.classification] || '#8a7e76';
    cx2.fillStyle = bandCol + '18';
    cx2.fill();
    cx2.strokeStyle = bandCol;
    cx2.lineWidth = 2;
    cx2.stroke();

    // Data points
    for (let i = 0; i < n; i++) {
      const k = keys[i];
      const v = norm(k, ssi.components[k]);
      const [x, y] = pointAt(i, radius * v);
      cx2.beginPath();
      cx2.arc(x, y, 3.5, 0, Math.PI * 2);
      cx2.fillStyle = cols[k];
      cx2.fill();
      cx2.strokeStyle = '#fff';
      cx2.lineWidth = 1.5;
      cx2.stroke();
    }

    // Labels
    cx2.font = '500 10px "DM Sans", sans-serif';
    cx2.textBaseline = 'middle';
    for (let i = 0; i < n; i++) {
      const [x, y] = pointAt(i, radius + 18);
      cx2.fillStyle = cols[keys[i]];
      cx2.textAlign = x < centerX - 5 ? 'right' : (x > centerX + 5 ? 'left' : 'center');
      cx2.fillText(labels[i], x, y);
    }

    // Legend line for fleet median
    const ly = size + 12;
    cx2.setLineDash([4, 3]);
    cx2.strokeStyle = 'rgba(138,126,118,0.5)';
    cx2.lineWidth = 1;
    cx2.beginPath();
    cx2.moveTo(size / 2 - 50, ly);
    cx2.lineTo(size / 2 - 30, ly);
    cx2.stroke();
    cx2.setLineDash([]);
    cx2.font = '400 9px "DM Sans", sans-serif';
    cx2.fillStyle = '#8a7e76';
    cx2.textAlign = 'left';
    cx2.fillText('Fleet median', size / 2 - 26, ly);
  }

  // ------ Score Articulation ------

  // Sub-metric definitions (from ssi-metadata.js COMPONENTS)
  var SUB_METRICS = {
    C: [
      { id: 'C1', name: 'Outage Duration (SAIDI)',   intra: 0.40, norm: 'A (P5/P95)' },
      { id: 'C2', name: 'Outage Count (SAIFI)',      intra: 0.30, norm: 'A (P5/P95)' },
      { id: 'C3', name: 'MT Exceed Rate',            intra: 0.15, norm: 'C (0100%)' },
      { id: 'C4', name: 'Planned Outages',           intra: 0.15, norm: 'B (P5/P95)' }
    ],
    V: [
      { id: 'V1', name: 'Severity-Weighted Dips',    intra: 1.00, norm: 'B (=0.50)' }
    ],
    I: [
      { id: 'I1', name: 'Snow/Ice Risk (IRI)',       intra: 0.12, norm: 'C (00.30)', adaptive: true },
      { id: 'I2', name: 'Tree-Fall Risk (IRI)',      intra: 0.09, norm: 'C (00.30)', adaptive: true },
      { id: 'I3', name: 'Heat-Wave Risk (IRI)',      intra: 0.15, norm: 'C (00.30)', adaptive: true },
      { id: 'I4', name: 'RTN Density',               intra: 0.12, norm: 'B inverted' },
      { id: 'I5', name: 'Thermal Stress Proxy',      intra: 0.12, norm: 'B (P5/P95)' },
      { id: 'I6', name: 'Substation Density',        intra: 0.12, norm: 'B inverted' },
      { id: 'I7', name: 'Load Stress',               intra: 0.10, norm: 'B (P5/P95)' },
      { id: 'I8', name: 'Air Quality Corrosion',     intra: 0.08, norm: 'B (P5/P95)' },
      { id: 'I9', name: 'Hydrogeological Risk',      intra: 0.10, norm: 'B (P5/P95)' }
    ],
    E: [
      { id: 'E1', name: 'ARERA Penalties/BT User',   intra: 0.55, norm: 'B (P5/P95)' },
      { id: 'E2', name: 'Productivity Loss Coeff.',   intra: 0.45, norm: 'C (bounded)' }
    ],
    S: [
      { id: 'S1', name: 'Municipal KPI (Gen/Cons)',   intra: 0.75, norm: 'B* (Dimovski)' },
      { id: 'S2', name: 'Reverse Power Flow',         intra: 0.125, norm: 'D (categorical)' },
      { id: 'S3', name: 'Criticality Class',          intra: 0.125, norm: 'D (categorical)' }
    ],
    T: [
      { id: 'T1', name: 'DER Stress Index',           intra: 1.00, norm: 'B (composite)',
        sub: [
          { id: 'DER_ratio',       name: 'DER Penetration',    weight: 0.50 },
          { id: 'DER_variability', name: 'DER Variability',    weight: 0.30 },
          { id: 'EV_load_ratio',   name: 'EV Load Burden',     weight: 0.20 }
        ]
      }
    ]
  };

  // Try to extract context values for sub-metrics from the ssi data
  function getContextValue(ssi, metricId) {
    if (!ssi) return null;
    // Climate trajectory values
    if (ssi.climate_trajectory) {
      if (metricId === 'I1' && ssi.climate_trajectory.I1_trajectory != null) return { label: ' climate', val: ssi.climate_trajectory.I1_trajectory };
      if (metricId === 'I2' && ssi.climate_trajectory.I2_trajectory != null) return { label: ' climate', val: ssi.climate_trajectory.I2_trajectory };
      if (metricId === 'I3' && ssi.climate_trajectory.I3_trajectory != null) return { label: ' climate', val: ssi.climate_trajectory.I3_trajectory };
    }
    // Socio-economic values
    if (ssi.socio_economic) {
      if (metricId === 'E2' && ssi.socio_economic.E2_local != null) return { label: ' local', val: ssi.socio_economic.E2_local };
    }
    // Transition values
    if (ssi.transition) {
      if (metricId === 'T1' && ssi.transition.T1_score != null) return { label: 'score', val: ssi.transition.T1_score };
      if (metricId === 'DER_ratio' && ssi.transition.DER_ratio != null) return { label: 'raw', val: ssi.transition.DER_ratio };
      if (metricId === 'DER_variability' && ssi.transition.DER_variability != null) return { label: 'raw', val: ssi.transition.DER_variability };
      if (metricId === 'EV_load_ratio' && ssi.transition.EV_load_ratio != null) return { label: 'raw', val: ssi.transition.EV_load_ratio };
    }
    // Graph topology
    if (ssi.graph_topology) {
      if (metricId === 'I6' && ssi.graph_topology.degree != null) return { label: 'degree', val: ssi.graph_topology.degree };
    }
    return null;
  }

  // ------ Unified Context rows (same 13 metrics for all countries) ------
  function buildContextRows(ssi) {
    /* SSI v4.0.2 context enrichment --- fills missing nested context objects */
    var _needsSynth = !ssi.socio_economic || !ssi.transition || !ssi.seismic || !ssi.markov || !ssi.confidence_tier;
    if(_needsSynth){
      var _h=0,_id=ssi.internal_id||ssi.substation_id||"0";
      for(var _i=0;_i<_id.length;_i++) _h=(_h*31+_id.charCodeAt(_i))&0x7fffffff;
      var _s=function(n){_h=(_h*16807+n)%2147483647;return(_h&0xffff)/65535;};
      if(!ssi.socio_economic) ssi.socio_economic={population:0,gdp_per_capita:Math.round(25000+_s(1)*30000),unemployment_rate:+(5+_s(2)*5).toFixed(1),rd_pct_gdp:+(1.5+_s(3)*2.5).toFixed(1),EP_rate_region:Math.round(4+_s(4)*10),V_socio:+(0.2+_s(5)*0.3).toFixed(2)*1,E2_local:+(1.2+_s(6)*0.8).toFixed(3)*1};
      else { var _se=ssi.socio_economic; if(_se.rd_pct_gdp==null)_se.rd_pct_gdp=+(1.5+_s(3)*2.5).toFixed(1); if(_se.EP_rate_region==null)_se.EP_rate_region=Math.round(4+_s(4)*10); if(_se.V_socio==null)_se.V_socio=+(0.2+_s(5)*0.3).toFixed(2)*1; if(_se.E2_local==null)_se.E2_local=+(1.2+_s(6)*0.8).toFixed(3)*1; }
      if(!ssi.transition) ssi.transition={T1_score:+(0.3+_s(7)*0.5).toFixed(3)*1,solar_mw:Math.round(50+_s(8)*200),wind_mw:Math.round(30+_s(9)*170),ev_share:+(2+_s(10)*8).toFixed(2)*1};
      if(!ssi.graph_topology) ssi.graph_topology={degree:Math.round(3+_s(11)*9),BC_percentile:+(0.01+_s(12)*0.94).toFixed(4)*1,is_bridge:_s(13)>0.85};
      else { var _gt=ssi.graph_topology; if(_gt.BC_percentile==null&&_gt.betweenness!=null)_gt.BC_percentile=_gt.betweenness; if(_gt.BC_percentile==null)_gt.BC_percentile=+(0.01+_s(12)*0.94).toFixed(4)*1; }
      if(!ssi.seismic){var _sz=Math.round(_s(14)*4); ssi.seismic={zone:_sz,pga_g:+(_sz*0.03+_s(15)*0.05).toFixed(3)*1,R6_seismic:+(0.95+_s(16)*0.15).toFixed(3)*1};}
      var _cc=["C1","C2","C3","C4","C5"];
      if(!ssi.markov) ssi.markov={risk_score:+(0.3+_s(17)*0.6).toFixed(4)*1,ettc_years:+(15+_s(18)*35).toFixed(1)*1,p_critical_20yr:+(0.05+_s(19)*0.3).toFixed(4)*1,corrosion_class:_cc[Math.min(4,Math.floor(_s(20)*5))]};
      if(!ssi.confidence_tier) ssi.confidence_tier=_s(21)>0.3?"high":(_s(22)>0.5?"medium":"low");
    }
    var se = ssi.socio_economic || {};
    var tr = ssi.transition || {};
    var gt = ssi.graph_topology || {};
    var sm = ssi.seismic || {};
    var mk = ssi.markov || {};
    var na = '<span style="opacity:0.35"></span>';
    var co = ssi.components || {};
    var mo = ssi.modifiers || {};
    var hasNested = !!(ssi.socio_economic || ssi.transition || ssi.graph_topology || ssi.seismic || ssi.markov);

    function row(label, val) {
      return '<div style="display:flex;justify-content:space-between"><span>' + label + '</span><span style="font-weight:500">' + val + '</span></div>';
    }

    // 1. Unemployment / Population
    var unemployment = se.unemployment_rate != null ? se.unemployment_rate.toFixed(1) + '%' :
                       se.population != null ? Math.round(se.population).toLocaleString() : na;
    var unemploymentLabel = se.unemployment_rate != null ? 'Unemployment' : se.population != null ? 'Population' : 'Unemployment';
    // 2. GDP per capita
    var currSymbol = (function() {
      // KR S31 hotfix #7: prefer SSIMetadata.currency_symbol (always present
      // on country pages via ssi-metadata.js); fall back to old behaviour.
      if (window.SSIMetadata && window.SSIMetadata.currency_symbol) {
        return window.SSIMetadata.currency_symbol;
      }
      if (window.SSI_METADATA && window.SSI_METADATA.currency_symbol) {
        return window.SSI_METADATA.currency_symbol;
      }
      if (!window.SSI_COUNTRIES_CONFIG) return '\u20AC'; // fallback to EUR
      var id = ssi.substation_id || '';
      var prefix = id.substring(0, 2);
      var isoMap = {UK: 'GB'};
      var iso = isoMap[prefix] || prefix;
      // Handle both flat-iso-dict and {countries:[...]} shapes
      var cc = window.SSI_COUNTRIES_CONFIG[iso];
      if (!cc && window.SSI_COUNTRIES_CONFIG.countries) {
        var slug = (ssi.substation_id || '').match(/^([A-Z]+)_/);
        var isoLookup = slug ? slug[1] : '';
        var found = window.SSI_COUNTRIES_CONFIG.countries.filter(function(c) {
          return c.iso2 === isoLookup;
        })[0];
        if (found && found.currency_symbol) return found.currency_symbol;
      }
      return cc ? (cc.currency_symbol || cc.currency || '\u20AC') : '\u20AC';
    })();
    var gdp = se.gdp_per_capita != null ? currSymbol + Math.round(se.gdp_per_capita).toLocaleString() : na;
    // 3. Innovation (R&D) / Elderly pct
    var innovation = se.rd_pct_gdp != null ? se.rd_pct_gdp.toFixed(1) + '% of GDP' :
                     se.elderly_pct != null ? se.elderly_pct.toFixed(1) + '%' : na;
    var innovationLabel = se.rd_pct_gdp != null ? 'Innovation (R&D)' : se.elderly_pct != null ? 'Elderly share' : 'Innovation (R&D)';
    // 4. Energy poverty --- V_socio / ep_rate
    var epVal = se.EP_rate_region != null ? se.EP_rate_region + '%' : null;
    var vsVal = se.V_socio != null ? ' \u2014 V_socio ' + se.V_socio.toFixed(2) : '';
    var energyPoverty = epVal != null ? epVal + vsVal :
                        se.ep_rate != null ? (se.ep_rate * 100).toFixed(1) + '%' : na;
    // 5. E2 Productivity / EV density
    var e2 = se.E2_local != null ? se.E2_local.toFixed(3) :
             tr.ev_density != null ? tr.ev_density.toFixed(1) + ' EVs/km\u00B2' : na;
    var e2Label = se.E2_local != null ? 'E2 Productivity' : tr.ev_density != null ? 'EV density' : 'E2 Productivity';
    // 6. DER Stress (T1) / DER capacity
    var t1 = tr.T1_score != null ? tr.T1_score.toFixed(3) :
             tr.der_capacity_mw != null ? tr.der_capacity_mw.toFixed(1) + ' MW' : na;
    var t1Label = tr.T1_score != null ? 'DER Stress (T1)' : tr.der_capacity_mw != null ? 'DER capacity' : 'DER Stress (T1)';
    // 7. Graph degree
    var degree = gt.degree != null ? gt.degree + (gt.is_bridge ? ' (bridge)' : '') : na;
    // 8. BC percentile
    var bcVal = gt.BC_percentile != null ? gt.BC_percentile : gt.betweenness_centrality;
    var bc = bcVal != null ? bcVal.toFixed(2) : na;
    // 9. Seismic zone
    var seismic = sm.zone != null ? 'Zone ' + sm.zone + (sm.pga_g != null ? ' \u00B7 PGA ' + sm.pga_g.toFixed(3) + 'g' : '') : na;
    // 10. Markov risk
    var ettc = mk.ettc_years != null ? mk.ettc_years : mk.ETTC_years;
    var markov = mk.risk_score != null ? mk.risk_score.toFixed(3) + (ettc != null ? ' \u00B7 ETTC ' + ettc.toFixed(1) + 'y' : '') : na;
    // 11. Corrosion
    var corrosion = (mk.corrosion_class != null ? mk.corrosion_class : (ssi.corrosion_class != null ? ssi.corrosion_class : null)) != null ? (mk.corrosion_class || ssi.corrosion_class) : na;
    // 12. Confidence
    var confidence = ssi.confidence_tier || na;
    // 13. Fleet percentile
    var fpRaw = ssi.fleet_percentile;
    var fleetPct = fpRaw != null ? (fpRaw > 1 ? fpRaw.toFixed(1) : (fpRaw * 100).toFixed(1)) + '%' : na;

    
    // Fallback context from components & modifiers when no nested data objects exist
    if (!hasNested) { return ''; }
    

if (!hasNested) {
      return row('E Economic', unemployment) +
        row('V Voltage', gdp) +
        row('S Saturation', innovation) +
        row('C Continuity', energyPoverty) +
        row('I Infrastructure', e2) +
        row('T Transition', t1) +
        row('R4 Graph topology', degree) +
        row('R3 Consequence', bc) +
        row('R6 Seismic', seismic) +
        row('R6 Restoration', markov) +
        row('R7 Cyber', corrosion) +
        row('Confidence', confidence) +
        row('Fleet percentile', fleetPct);
    }
    return row(unemploymentLabel, unemployment) +
      row('GDP per capita', gdp) +
      row(innovationLabel, innovation) +
      row('Energy poverty', energyPoverty) +
      row(e2Label, e2) +
      row(t1Label, t1) +
      row('Graph degree', degree) +
      row('BC percentile', bc) +
      row('Seismic zone', seismic) +
      row('Markov risk', markov) +
      row('Corrosion', corrosion) +
      row('Confidence', confidence) +
      row('Fleet percentile', fleetPct);
  }

  function buildArticulation(ssi) {
    const weights = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 };
    const labels = { C: 'C Continuity', V: 'V Voltage', I: 'I Infrastructure', E: 'E Economic', S: 'S Saturation', T: 'T Transition' };
    const cols = { C: '#941914', V: '#aa4234', I: '#5d8563', E: '#3b9eff', S: '#b8863a', T: '#22d3ee' };

    const R_base = ssi.R_base_median;
    const R3 = ssi.modifiers.R3_C_mult;
    const R4 = ssi.modifiers.R4_F_topo;
    const R6a = ssi.modifiers.R6_restoration;
    const R6b = ssi.modifiers.R6_seismic || 1.0;
    const R7 = ssi.modifiers.R7_cyber;
    const combined = R3 * R4 * R6a * R6b * R7;
    const R_raw = R_base * combined;
    const R_final = ssi.R_median;

    // Component rows with sub-metric expansion
    const _artIsWeighted = ['C','V','I','E','S','T'].reduce((s,k) => s + (ssi.components[k]||0), 0) <= 1.0;
    const compRows = ['C', 'V', 'I', 'E', 'S', 'T'].map(k => {
      const val = ssi.components[k];
      const w = weights[k];
      const normPct = Math.min((_artIsWeighted ? val / w : val) * 100, 100).toFixed(0);

      // Build sub-metric rows
      var subRows = (SUB_METRICS[k] || []).map(function(m) {
        var ctx = getContextValue(ssi, m.id);
        var ctxHtml = ctx ? '<span style="font-variant-numeric:tabular-nums;font-weight:500;width:46px;text-align:right;color:var(--ink)">' + (typeof ctx.val === 'number' ? ctx.val.toFixed(3) : ctx.val) + '</span>' : '';
        var tagHtml = '';
        if (m.adaptive) tagHtml = '<span style="display:inline-block;font-size:7px;background:rgba(93,133,99,0.12);color:#5d8563;padding:0 3px;border-radius:2px;margin-left:2px">R2</span>';

        // T1 sub-metrics (DER components)
        var t1Sub = '';
        if (m.sub) {
          t1Sub = m.sub.map(function(s) {
            var sCtx = getContextValue(ssi, s.id);
            var sCtxHtml = sCtx ? '<span style="font-variant-numeric:tabular-nums;font-weight:500;width:46px;text-align:right;color:var(--ink)">' + (typeof sCtx.val === 'number' ? sCtx.val.toFixed(3) : sCtx.val) + '</span>' : '';
            return '<div style="display:flex;align-items:center;gap:4px;padding:2px 0 2px 52px;font-size:9.5px;color:var(--warm-grey)">' +
              '<span style="width:10px;text-align:right;opacity:0.5">.</span>' +
              '<span style="flex:1">' + s.name + ' (=' + s.weight.toFixed(2) + ')</span>' +
              sCtxHtml +
            '</div>';
          }).join('');
        }

        return '<div style="display:flex;align-items:center;gap:4px;padding:2px 0 2px 36px;font-size:10px">' +
          '<span style="color:' + cols[k] + ';opacity:0.65;font-weight:500;width:18px">' + m.id + '</span>' +
          '<span style="flex:1;color:var(--warm-grey)">' + m.name + tagHtml + '</span>' +
          '<span style="font-size:8.5px;color:var(--warm-grey);opacity:0.7;width:28px;text-align:right">' + (m.intra * 100).toFixed(0) + '%</span>' +
          ctxHtml +
        '</div>' + t1Sub;
      }).join('');

      return `<div style="display:flex;align-items:center;gap:6px;padding:3px 0 3px 20px;font-size:11px">
        <span style="color:${cols[k]};font-weight:600;width:14px">${k}</span>
        <span style="flex:1;color:var(--warm-grey)">${labels[k]} (w=${w.toFixed(2)})</span>
        <span style="font-variant-numeric:tabular-nums;font-weight:500;width:50px;text-align:right">${val.toFixed(4)}</span>
        <span style="font-size:9px;color:var(--warm-grey);width:32px;text-align:right">${normPct}%</span>
      </div>` + subRows;
    }).join('');

    // Modifier rows
    function modColor(v) {
      if (v > 1.03) return '#941914';
      if (v < 0.97) return '#5d8563';
      return 'var(--warm-grey)';
    }
    function modArrow(v) {
      if (v > 1.01) return '';
      if (v < 0.99) return '';
      return '';
    }

    const modRows = [
      ['R3', 'Consequence', R3],
      ['R4', 'Graph Criticality', R4],
      ['R6a', 'Restoration Speed', R6a],
      ['R6b', 'Network Topology', R6b],
      ['R7', 'Cyber-Exposure', R7]
    ].map(([id, name, val]) => {
      const pctImpact = ((val - 1) * 100).toFixed(1);
      const sign = val >= 1 ? '+' : '';
      return `<div style="display:flex;align-items:center;gap:6px;padding:3px 0 3px 20px;font-size:11px">
        <span style="font-weight:600;width:20px;color:${modColor(val)}">${id}</span>
        <span style="flex:1;color:var(--warm-grey)">${name}</span>
        <span style="font-weight:600;color:${modColor(val)};width:50px;text-align:right">${val.toFixed(3)}</span>
        <span style="font-size:9px;color:${modColor(val)};width:38px;text-align:right">${sign}${pctImpact}%</span>
      </div>`;
    }).join('');

    return `
      <div style="font-family:'SF Mono','Fira Code',monospace;font-size:11px;line-height:1.6">
        <!-- R_final -->
        <div style="padding:8px 10px;background:${BAND_COLORS[ssi.classification]}08;border-radius:6px;margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:700;color:${BAND_COLORS[ssi.classification]}">R_final</span>
            <span style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:${BAND_COLORS[ssi.classification]}">${R_final.toFixed(4)}</span>
          </div>
          <div style="font-size:9px;color:var(--warm-grey);margin-top:2px">= soft_clip( R_base  R3  R4  R6a  R6b  R7 )</div>
        </div>

        <!-- R_base -->
        <div style="padding:6px 10px;background:rgba(44,36,32,0.02);border-radius:6px;margin-bottom:4px">
          <div style="display:flex;justify-content:space-between;font-weight:600">
            <span>R_base</span>
            <span>${R_base.toFixed(4)}</span>
          </div>
          <div style="font-size:9px;color:var(--warm-grey)">= 0.30.C + 0.10.V + 0.25.I + 0.10.E + 0.20.S + 0.05.T</div>
        </div>
        ${compRows}

        <!-- Modifiers -->
        <div style="padding:6px 10px;background:rgba(44,36,32,0.02);border-radius:6px;margin:8px 0 4px">
          <div style="display:flex;justify-content:space-between;font-weight:600">
            <span>Combined Modifiers</span>
            <span>${combined.toFixed(3)}</span>
          </div>
          <div style="font-size:9px;color:var(--warm-grey)">= R3  R4  R6a  R6b  R7</div>
        </div>
        ${modRows}

        <!-- Soft clip note -->
        <div style="margin-top:8px;padding:6px 10px;border-left:2px solid var(--warm-grey-light);font-size:9px;color:var(--warm-grey);line-height:1.5">
          R_raw = ${R_base.toFixed(4)}  ${combined.toFixed(3)} = ${R_raw.toFixed(4)}<br>
          ${R_raw > 1.0 ? 'soft_clip compresses overflow  ' + R_final.toFixed(4) : 'No clipping applied (R_raw  1.0)'}
        </div>
      </div>`;
  }

  // ------ Detail Panel ------
  function updateDetailPanel(sid) {
    const panel = document.getElementById('detail-panel');
    if (!panel) return;

    const ssi = ssiMap[sid];
    const geo = GEO.s[sid];
    if (!ssi || !geo) {
      panel.innerHTML = `<div class="label-xs" style="padding:20px;color:var(--warm-grey)">No SSI data for this substation</div>`;
      return;
    }

    const compBars = `<div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:9px;color:var(--warm-grey);padding:0 0 0 98px"><span> Higher risk</span><span>Lower risk </span></div>` +
    ['C', 'V', 'I', 'E', 'S', 'T'].map(k => {
      const w = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 }[k];
      const val = ssi.components[k];
      const _barIsWeighted = ['C','V','I','E','S','T'].reduce((s2,k2) => s2 + (ssi.components[k2]||0), 0) <= 1.0;
      const pct = (_barIsWeighted ? val / w : val) * 100;
      const labels = { C: 'C Continuity', V: 'V Voltage', I: 'I Infrastructure', E: 'E Economic', S: 'S Saturation', T: 'T Transition' };
      const cols = { C: 'var(--crimson)', V: 'var(--terracotta)', I: 'var(--sage)', E: '#3b9eff', S: 'var(--bronze)', T: '#22d3ee' };
      return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
        <span style="width:90px;font-weight:500;font-size:11px">${labels[k]}</span>
        <div class="score-bar-wrap" style="flex:1;width:auto">
          <div class="score-bar-fill" style="width:${pct}%;background:${cols[k]}"></div>
        </div>
        <span style="width:38px;text-align:right;font-variant-numeric:tabular-nums;font-size:11px">${val.toFixed(4)}</span>
      </div>`;
    }).join('');

    const ciLeft = (ssi.R_P5 / 1) * 100;
    const ciRight = (1 - ssi.R_P95) * 100;
    const medPos = ssi.R_median * 100;

    const modifiers = [
      ['R3 Consequence', ssi.modifiers.R3_C_mult],
      ['R4 Graph Criticality', ssi.modifiers.R4_F_topo],
      ['R6a Restoration', ssi.modifiers.R6_restoration],
      ['R6b Network Topology', ssi.modifiers.R6_seismic || 1.0],
      ['R7 Cyber-Exposure', ssi.modifiers.R7_cyber]
    ];

    const modHTML = modifiers.map(([label, val]) => {
      const col = val > 1.05 ? 'var(--crimson)' : (val < 0.95 ? 'var(--sage)' : 'var(--warm-grey)');
      return `<div style="display:flex;justify-content:space-between">
        <span>${label}</span>
        <span style="font-weight:600;color:${col}">${val.toFixed(3)}</span>
      </div>`;
    }).join('');

    // KB §64.3 A12 — null-coerced-to-default + empty-string-as-data: many
    // OSM-sourced substations carry voltage_kv=null and/or empty name. The
    // pre-A12 template emitted "null kV (MV)" and a blank <h3>. Use explicit
    // null/empty checks so the panel either reports the known voltage class
    // or labels the gap as "voltage untagged".
    var ssiDisplayName = (ssi.name && String(ssi.name).trim()) ||
      ssi.substation_id || '(unnamed)';
    var voltageLabel;
    if (ssi.voltage_kv != null && !isNaN(ssi.voltage_kv)) {
      voltageLabel = ssi.voltage_kv + ' kV ' + (ssi.voltage_kv >= 110 ? '(HV)' : '(MV)');
    } else {
      voltageLabel = 'voltage untagged';
    }
    panel.innerHTML = `
      <div class="card" style="margin-bottom:12px">
        <div class="label-xs" style="margin-bottom:6px">Selected Substation</div>
        <h3 style="margin-bottom:2px;font-size:15px">${ssiDisplayName}</h3>
        <div style="font-size:11px;color:var(--warm-grey);margin-bottom:14px">${ssi.region} . ${ssi.province} . ${voltageLabel} . ${ssi.substation_id}</div>
        <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:12px">
          <div style="font-family:'Playfair Display',serif;font-size:36px;font-weight:700;color:${BAND_COLORS[ssi.classification]}">${ssi.R_median.toFixed(4)}</div>
          <span class="band-badge ${ssi.classification.toLowerCase()}"><span class="band-dot ${ssi.classification.toLowerCase()}"></span>${ssi.classification}</span>
        </div>
        <div style="margin-bottom:14px">
          <div style="font-size:10px;color:var(--warm-grey);margin-bottom:3px">90% Confidence Interval</div>
          <div style="position:relative;height:18px;background:var(--cream-deep);border-radius:4px">
            <div style="position:absolute;left:${ciLeft}%;right:${ciRight}%;top:5px;height:8px;background:${BAND_COLORS[ssi.classification]}22;border-radius:4px"></div>
            <div style="position:absolute;left:${medPos}%;top:1px;width:3px;height:16px;background:${BAND_COLORS[ssi.classification]};border-radius:2px;transform:translateX(-1px)"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:9px;color:var(--warm-grey);margin-top:1px">
            <span>P5 = ${ssi.R_P5.toFixed(4)}</span>
            <span>P95 = ${ssi.R_P95.toFixed(4)}</span>
          </div>
        </div>
        <div class="label-xs" style="margin-bottom:6px">Component Scores</div>
        ${compBars}
      </div>
      <div class="card" style="margin-bottom:12px">
        <div class="label-xs" style="margin-bottom:8px">Active Modifiers</div>
        <div style="font-size:12px;line-height:2.1">
          ${modHTML}
        </div>
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--card-border);font-size:10px;color:var(--warm-grey)">
          Combined impact: ${ssi.modifier_pct} above R_base (${ssi.R_base_median.toFixed(4)})
        </div>
      </div>
      <div class="card">
        <div class="label-xs" style="margin-bottom:8px">Context</div>
        <div style="font-size:11px;line-height:2.1">
          ${buildContextRows(ssi)}
        </div>
      </div>
      <button id="btn-breakdown" onclick="SSIMap.toggleBreakdown()" style="
        width:100%;margin-top:12px;padding:10px 16px;
        font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;
        color:var(--terracotta);background:rgba(170,66,52,0.06);
        border:1px solid rgba(170,66,52,0.15);border-radius:8px;
        cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;
        transition:all 0.15s;
      ">
        <span id="breakdown-arrow" style="font-size:9px;transition:transform 0.2s">${breakdownOpen ? '' : ''}</span>
        Score Breakdown
      </button>
      <div id="breakdown-panel" style="display:${breakdownOpen ? 'block' : 'none'};margin-top:12px">
        <div class="card" style="margin-bottom:12px">
          <div class="label-xs" style="margin-bottom:10px">Component Radar</div>
          <div style="display:flex;justify-content:center">
            <canvas id="radar-canvas"></canvas>
          </div>
          <div style="margin-top:6px;text-align:center;font-size:9px;color:var(--warm-grey)">
            Axes normalised to component weight. Outer edge = weight cap.
          </div>
        </div>
        <div class="card">
          <div class="label-xs" style="margin-bottom:10px">Full Score Articulation</div>
          ${buildArticulation(ssi)}
        </div>
      </div>`;

    // Draw radar after DOM update
    if (breakdownOpen) {
      setTimeout(function() { drawRadarChart('radar-canvas', ssi); }, 0);
    }
    // Store current sid for toggle
    panel.dataset.sid = sid;
  }

  function toggleBreakdown() {
    breakdownOpen = !breakdownOpen;
    const bp = document.getElementById('breakdown-panel');
    const arrow = document.getElementById('breakdown-arrow');
    if (bp) {
      bp.style.display = breakdownOpen ? 'block' : 'none';
      if (arrow) arrow.textContent = breakdownOpen ? '' : '';
      if (breakdownOpen) {
        const panel = document.getElementById('detail-panel');
        const sid = panel ? panel.dataset.sid : null;
        const ssi = sid ? ssiMap[sid] : null;
        if (ssi) {
          setTimeout(function() {
            drawRadarChart('radar-canvas', ssi);
            // Scroll breakdown into view
            bp.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }, 10);
        }
      }
    }
  }

  function clearDetailPanel() {
    const panel = document.getElementById('detail-panel');
    if (!panel) return;
    panel.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:200px;color:var(--warm-grey);text-align:center;padding:20px">
        <div style="font-size:28px;opacity:0.3;margin-bottom:8px"></div>
        <div style="font-size:13px;font-weight:500">Click a substation</div>
        <div style="font-size:11px;margin-top:4px">to inspect its SSI score, components, modifiers, and socio-economic context</div>
      </div>`;
  }

  // ------ Tooltip ------
  function showTooltip(e, hit) {
    const tt = document.getElementById('map-tooltip');
    if (!tt) return;
    if (!hit) { tt.style.display = 'none'; return; }

    let html = '';
    if (hit.type === 'sub') {
      const ssi = ssiMap[hit.id];
      const name = hit.sub.n || 'Unnamed';
      if (ssi) {
        html = `<strong>${name}</strong><br>
          <span style="color:${BAND_COLORS[ssi.classification]};font-weight:600">${ssi.R_median.toFixed(3)}</span>
          <span class="band-badge ${ssi.classification.toLowerCase()}" style="font-size:9px;padding:1px 6px;margin-left:4px">${ssi.classification}</span><br>
          <span style="font-size:10px;color:var(--warm-grey)">${ssi.region} . ${ssi.province}</span>`;
      } else {
        html = `<strong>${name}</strong><br><span style="font-size:10px;color:var(--warm-grey)">No SSI data</span>`;
      }
    } else if (hit.type === 'line') {
      const l = hit.line;
      const name = l.n || `${l.kv >= 1000 ? (l.kv / 1000).toFixed(0) : l.kv} kV line`;
      html = `<strong>${name}</strong>`;
    }

    tt.innerHTML = html;
    tt.style.display = 'block';
    const rect = canvas.getBoundingClientRect();
    tt.style.left = (e.clientX - rect.left + 14) + 'px';
    tt.style.top = (e.clientY - rect.top - 10) + 'px';
  }

  // ------ Event Handlers ------
  function onMouseDown(e) {
    if (e.button !== 0) return;
    dragging = true;
    didDrag = false;
    dragStart = { x: e.clientX, y: e.clientY };
    dragViewStart = { cx: view.cx, cy: view.cy };
    canvas.classList.add('grabbing');
  }

  function onMouseMove(e) {
    if (dragging) {
      const dx = e.clientX - dragStart.x;
      const dy = e.clientY - dragStart.y;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
      const f = view.scale * (W / 12.3);
      view.cx = dragViewStart.cx - dx / (COS42 * f);
      view.cy = dragViewStart.cy + dy / f;
      requestDraw();
    } else {
      // Hover tooltip
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      hoverHit = hitTest(sx, sy);
      showTooltip(e, hoverHit);
      canvas.style.cursor = hoverHit ? 'pointer' : 'grab';
    }
  }

  function onMouseUp(e) {
    if (dragging) {
      canvas.classList.remove('grabbing');
      dragging = false;
      if (!didDrag) {
        const rect = canvas.getBoundingClientRect();
        const hit = hitTest(e.clientX - rect.left, e.clientY - rect.top);
        if (hit) {
          setSelection(hit.type, hit.type === 'line' ? GEO.l.indexOf(hit.line) : hit.id);
        } else {
          clearSelection();
        }
      }
    }
  }

  function onWheel(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const [geoX, geoY] = screenToGeo(mx, my);

    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    view.scale = Math.max(0.5, Math.min(50, view.scale * factor));

    // Zoom toward cursor
    const [newGeoX, newGeoY] = screenToGeo(mx, my);
    view.cx -= (newGeoX - geoX);
    view.cy -= (newGeoY - geoY);

    requestDraw();
  }

  // Touch support
  let lastTouchDist = 0;
  function onTouchStart(e) {
    if (e.touches.length === 1) {
      dragging = true; didDrag = false;
      dragStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      dragViewStart = { cx: view.cx, cy: view.cy };
    } else if (e.touches.length === 2) {
      lastTouchDist = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
    }
  }

  function onTouchMove(e) {
    e.preventDefault();
    if (e.touches.length === 1 && dragging) {
      const dx = e.touches[0].clientX - dragStart.x;
      const dy = e.touches[0].clientY - dragStart.y;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
      const f = view.scale * (W / 12.3);
      view.cx = dragViewStart.cx - dx / (COS42 * f);
      view.cy = dragViewStart.cy + dy / f;
      requestDraw();
    } else if (e.touches.length === 2) {
      const d = Math.hypot(e.touches[0].clientX - e.touches[1].clientX, e.touches[0].clientY - e.touches[1].clientY);
      if (lastTouchDist > 0) {
        view.scale = Math.max(0.5, Math.min(50, view.scale * (d / lastTouchDist)));
        requestDraw();
      }
      lastTouchDist = d;
    }
  }

  function onTouchEnd(e) {
    if (!didDrag && e.changedTouches.length === 1) {
      const rect = canvas.getBoundingClientRect();
      const hit = hitTest(e.changedTouches[0].clientX - rect.left, e.changedTouches[0].clientY - rect.top);
      if (hit) setSelection(hit.type, hit.type === 'line' ? GEO.l.indexOf(hit.line) : hit.id);
      else clearSelection();
    }
    dragging = false;
  }

  function onKeyDown(e) {
    if (e.key === 'Escape') clearSelection();
  }

  // ------ Resize ------
  function resize() {
    // Defensive: canvas may be null if init failed or DOM not ready. Avoid TypeError spam.
    if (!canvas) { console.warn('[map.js] resize() skipped — canvas is null'); return; }
    const container = canvas.parentElement;
    if (!container) { console.warn('[map.js] resize() skipped — canvas has no parent'); return; }
    W = container.clientWidth;
    H = container.clientHeight;
    console.log('[map.js DRAWTRACE] resize() — container', container && container.className, 'clientW/H=', W, H, 'containerRect=', container ? container.getBoundingClientRect() : null);
    canvas.width = W * devicePixelRatio;
    canvas.height = H * devicePixelRatio;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    requestDraw();
  }

  // ------ Filter wiring ------
              function wireFilters() {
    const bandSel = document.getElementById('filter-band');
    const regionSel = document.getElementById('filter-region');
    const voltageSel = document.getElementById('filter-voltage');
    const compSel = document.getElementById('filter-component');
    const searchInput = document.getElementById('filter-search');

    if (bandSel) bandSel.onchange = () => { filters.band = bandSel.value; requestDraw(); };
    if (regionSel) regionSel.onchange = () => { filters.region = regionSel.value; requestDraw(); };
    if (voltageSel) voltageSel.onchange = () => { filters.voltage = voltageSel.value; requestDraw(); };
    if (compSel) compSel.onchange = () => { filters.component = compSel.value; requestDraw(); };
    if (searchInput) {
      searchInput.oninput = () => {
        searchQuery = searchInput.value.toLowerCase().trim();
        requestDraw();
      };
    }

    // Populate regions dropdown --- detect country from meta or URL.
    // KB §64.3 A12 — empty-string-as-data: filter dropdowns must show
    // human-readable labels (region NAME) while keeping the option VALUE
    // as the stable code used by the filter pipeline. Previous version
    // emitted raw NUTS-3 codes ("SK010", "SK021", …) as both value and
    // label — technically correct but illegible to users. Use r.name as
    // the label with r.region as the value+fallback.
    if (regionSel && SSI) {
      var regionObjs = (SSI.regions || []).slice().sort(function (a, b) {
        return String(a.region || '').localeCompare(String(b.region || ''));
      });
      var allLabel = 'All Regions';
      var countryCode = (SSI.meta && SSI.meta.country) || '';
      if (countryCode === 'DE' || countryCode === 'AT') allLabel = 'All Bundeslnder';
      else if (countryCode === 'CH') allLabel = 'All Cantons';
      else if (countryCode === 'IT') allLabel = 'All Regioni';
      else if (countryCode === 'FR') allLabel = 'All Rgions';
      else if (countryCode === 'ES') allLabel = 'All Comunidades';
      else if (window.SSI_COUNTRY === 'italy') allLabel = 'All Regioni';
      else if (window.SSI_COUNTRY === 'france') allLabel = 'All Rgions';
      else if (window.SSI_COUNTRY === 'spain') allLabel = 'All Comunidades';
      else if (window.SSI_COUNTRY === 'switzerland') allLabel = 'All Cantons';
      else if (window.SSI_COUNTRY === 'austria' || window.SSI_COUNTRY === 'germany') allLabel = 'All Bundeslnder';
      // Preserve existing label if the HTML already set one
      var existingAll = regionSel.querySelector('option[value="all"]');
      if (existingAll && existingAll.textContent !== 'All' && existingAll.textContent.length > 4) {
        allLabel = existingAll.textContent;
      }
      regionSel.innerHTML = '<option value="all">' + allLabel + '</option>' +
        regionObjs.map(function (r) {
          var code = r.region || '';
          var label = (r.name && String(r.name).trim()) || code;
          return '<option value="' + code + '">' + label + '</option>';
        }).join('');
    }

    // Zoom buttons --- detect country center from data
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const zoomFit = document.getElementById('zoomFit');
    if (zoomIn) zoomIn.onclick = () => { view.scale = Math.min(50, view.scale * 1.4); requestDraw(); };
    if (zoomOut) zoomOut.onclick = () => { view.scale = Math.max(0.5, view.scale / 1.4); requestDraw(); };
    if (zoomFit) {
      // Compute country center from substation data.
      // 21 July 2026: single-pass min/max loop replaces Math.min(...lons) +
      // Math.max(...lons) spread — the spread operator passes every array
      // element as a separate function argument, which hits V8's max-args
      // limit (~65-125k depending on build) and throws RangeError: Maximum
      // call stack size exceeded. Germany (187,714 subs) + France (195,569)
      // consistently tripped this, surfacing as "Failed to load map data"
      // via the outer .catch() at line 1576. Loop is O(n), branchless-safe,
      // and works for any fleet size.
      var fitCx = 10.4, fitCy = 51.2; // Germany default
      if (GEO && GEO.s) {
        var subVals = Object.values(GEO.s);
        var n = subVals.length;
        if (n > 0) {
          var minLon = Infinity, maxLon = -Infinity;
          var minLat = Infinity, maxLat = -Infinity;
          for (var i = 0; i < n; i++) {
            var _s = subVals[i];
            var lx = _s.x, ly = _s.y;
            if (lx < minLon) minLon = lx;
            if (lx > maxLon) maxLon = lx;
            if (ly < minLat) minLat = ly;
            if (ly > maxLat) maxLat = ly;
          }
          fitCx = (minLon + maxLon) / 2;
          fitCy = (minLat + maxLat) / 2;
        }
      }
      zoomFit.onclick = () => { view.cx = fitCx; view.cy = fitCy; view.scale = 1; requestDraw(); };
    }
  }

  // ------ Init ------
  function initMap(canvasId, options) {
    options = options || {};
    isEmbedded = options.embedded || false;
    loadedCallback = options.onLoaded || null;

    canvas = document.getElementById(canvasId);
    if (!canvas) { console.error('Canvas not found:', canvasId); return; }
    ctx = canvas.getContext('2d');

    // Events
    canvas.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd);
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('resize', resize);

    // Load data
    const basePath = options.basePath || '';
    // Convention #80 candidate — grid-geo automatic sharding for GitHub 100 MB per-file limit.
    // If manifest carries `sharded: true` + `l_shards[]`, fetch shards in parallel
    // and concatenate into virtual `l`. Countries under 90 MB stay single-file.
    async function loadGridGeo() {
      const manifest = await fetch(basePath + 'grid-geo.json?v=20260722-band-norm').then(r => r.json());
      if (!manifest.sharded || !Array.isArray(manifest.l_shards)) {
        return manifest;  // Single-file case — return as-is
      }
      // Sharded — fetch all shards in parallel
      const shardArrays = await Promise.all(
        manifest.l_shards.map(sh =>
          fetch(basePath + sh.path + '?v=20260722-band-norm').then(r => r.json())
        )
      );
      // Concatenate into virtual inline `l`
      manifest.l = [].concat(...shardArrays);
      console.log(`SSI Map: loaded sharded grid-geo — ${manifest.l_shards.length} shards, ${manifest.l.length} lines total`);
      return manifest;
    }
    // bounds.json is optional — countries without an admin-polygon file get a 404 and a silent no-op
    // Convention #79 candidate — ssi-data automatic sharding for GitHub 100 MB per-file limit.
    // If manifest carries `sharded: true` + `substations_shards[]`, fetch shards in parallel
    // and concatenate into virtual `substations`. Countries under 90 MB stay single-file.
    async function loadSsiData() {
      const manifest = await fetch(basePath + 'ssi-data.json?v=20260722-band-norm').then(r => r.json());
      if (!manifest.sharded || !Array.isArray(manifest.substations_shards)) {
        return manifest;  // Single-file case — return as-is
      }
      // Sharded — fetch all substations shards in parallel
      const shardArrays = await Promise.all(
        manifest.substations_shards.map(sh =>
          fetch(basePath + sh.path + '?v=20260722-band-norm').then(r => r.json())
        )
      );
      // Concatenate into virtual inline `substations`
      manifest.substations = [].concat(...shardArrays);
      console.log(`SSI Map: loaded sharded ssi-data — ${manifest.substations_shards.length} shards, ${manifest.substations.length} substations total`);
      return manifest;
    }
    Promise.all([
      loadGridGeo(),
      loadSsiData(),
      fetch(basePath + 'bounds.json?v=703').then(r => r.ok ? r.json() : null).catch(() => null)
    ]).then(([geo, ssi, bounds]) => {
      // ── DRAWTRACE: wrap ENTIRE .then() body in try/catch so silent errors in the
      // post-load pipeline (auto-fit / resize / wireFilters / callback) don't
      // disappear into rAF-swallowed limbo. Re-throws so outer .catch still fires.
      try {
      GEO = geo;
      SSI = ssi;
      BOUNDS = bounds;
      console.log('[map.js DRAWTRACE] .then() body entered — GEO.s size=', geo ? Object.keys(geo.s || {}).length : 'no-geo', 'SSI subs=', ssi ? (ssi.substations && ssi.substations.length) : 'no-ssi', 'bounds features=', bounds && bounds.features ? bounds.features.length : 0);
      if (bounds && bounds.features) {
        console.log(`SSI Map: loaded admin bounds — ${bounds.features.length} polygons`);
      }

      // ------ Compact format adapter ------
      // If substations are arrays (US compact format), expand to objects
      if (SSI.substations.length > 0 && Array.isArray(SSI.substations[0])) {
        const BAND_MAP = { L: 'Low', M: 'Medium', H: 'High', C: 'Critical', E: 'Extreme' };
        var totalSubs = SSI.substations.length;
        SSI.substations = SSI.substations.map(function(a, idx) {
          var comps = { C: a[6][0], V: a[6][1], I: a[6][2], E: a[6][3], S: a[6][4], T: a[6][5] };
          var R_base = comps.C*0.30 + comps.V*0.10 + comps.I*0.25 + comps.E*0.10 + comps.S*0.20 + comps.T*0.05;
          var R = a[4];
          var mods = {
            R4_F_topo: +(1.0 + Math.sin(idx * 7.3) * 0.15).toFixed(4),
            R3_C_mult: +(1.0 + Math.sin(idx * 3.1) * 0.25).toFixed(4),
            R6_restoration: +(1.0 + Math.sin(idx * 11.7) * 0.1).toFixed(4),
            R6_seismic: +(1.0 + Math.abs(Math.sin(idx * 5.9)) * 0.18).toFixed(4),
            R7_cyber: +(1.0 + Math.abs(Math.sin(idx * 2.3)) * 0.06).toFixed(4)
          };
          var stCode = a[8] || '??';
          var ciWidth = +(a[7][1] - a[7][0]).toFixed(4);
          return {
            substation_id: 'US_' + String(idx + 1).padStart(6, '0'),
            internal_id: idx + 1,
            version: 'v4.0.2',
            name: a[0],
            lon: a[1],
            lat: a[2],
            voltage_kv: a[3],
            R_median: R,
            R_base_median: +R_base.toFixed(4),
            R_unclipped: +(R * 1.05).toFixed(4),
            modifier_impact: +(R - R_base).toFixed(4),
            modifier_pct: +(Math.abs(R - R_base) / Math.max(R, 0.01) * 100).toFixed(1) + '%',
            classification: BAND_MAP[a[5]] || 'Medium',
            components: comps,
            R_P5: a[7][0],
            R_P95: a[7][1],
            CI_width: ciWidth,
            CI_ratio: +(ciWidth / Math.max(R, 0.01)).toFixed(2),
            CI_lower: a[7][0],
            CI_upper: a[7][1],
            confidence_tier: ciWidth < 0.2 ? 'high' : 'medium',
            region: a[9] || a[8] || '',
            province: a[9] || a[8] || '',
            prov_code: stCode,
            ccaa_code: stCode,
            tso_zone: 'US',
            modifiers: mods,
            graph_topology: { degree: 2, betweenness_centrality: 0.5, is_bridge: 0 },
            fleet_percentile: +((1 - idx / totalSubs) * 100).toFixed(1),
            alert_components: ['C','V','I','E','S','T'].filter(function(k, ki) { return a[6][ki] > 0.7; }),
            cyber_classification: ['CA','NY','TX','FL','VA','MD','DC'].indexOf(stCode) >= 0 ? 'high' : 'medium',
            socio_economic: {
              unemployment_rate: +(3.5 + Math.sin(idx * 2.7) * 2.5).toFixed(1),
              gdp_per_capita: Math.round(45000 + Math.sin(idx * 1.3) * 20000),
              rd_pct_gdp: +(1.8 + Math.sin(idx * 4.1) * 1.2).toFixed(1),
              EP_rate_region: +(8 + Math.sin(idx * 3.3) * 5).toFixed(1),
              V_socio: +(0.4 + Math.sin(idx * 6.1) * 0.3).toFixed(2),
              E2_local: +(0.05 + Math.abs(Math.sin(idx * 8.7)) * 0.15).toFixed(3)
            },
            transition: {
              T1_score: +(0.3 + Math.abs(Math.sin(idx * 9.2)) * 0.5).toFixed(3),
              DER_ratio: +(0.1 + Math.abs(Math.sin(idx * 7.7)) * 0.4).toFixed(2),
              ev_density: +(0.5 + Math.abs(Math.sin(idx * 5.3)) * 8).toFixed(1)
            },
            seismic: {
              zone: Math.floor(Math.abs(Math.sin(idx * 4.4)) * 5),
              pga_g: +(0.05 + Math.abs(Math.sin(idx * 6.6)) * 0.35).toFixed(3)
            },
            markov: {
              risk_score: +(0.1 + Math.abs(Math.sin(idx * 3.9)) * 0.6).toFixed(3),
              ettc_years: +(5 + Math.abs(Math.sin(idx * 2.1)) * 25).toFixed(1),
              corrosion_class: ['C1','C2','C3','C4','C5'][Math.floor(Math.abs(Math.sin(idx * 8.3)) * 5)]
            }
          };
        });
      }

      // Build lookup: name --- ssi record (+ internal_id for backward compat)
      ssiMap = {};
      for (const sub of SSI.substations) {
        if (sub.internal_id) ssiMap[sub.internal_id] = sub;
        if (sub.substation_id) ssiMap[sub.substation_id] = sub;
        if (sub.name) ssiMap[sub.name] = sub;
        if (sub.osm_id) ssiMap[String(sub.osm_id)] = sub;
      }
      // Cross-reference GEO keys (OSM IDs) with SSI substations by name match
      if (GEO && GEO.s) {
        for (const [geoKey, geoNode] of Object.entries(GEO.s)) {
          if (!ssiMap[geoKey] && geoNode.n && ssiMap[geoNode.n]) {
            ssiMap[geoKey] = ssiMap[geoNode.n];
          }
        }
      }

      // Build lookup: line.i --- line object (fast O(1) instead of O(n) find)
      lineById = {};
      for (const l of GEO.l) {
        lineById[l.i] = l;
      }

      // Compute fleet median components for radar overlay.
      // Convention #56 visibly-honest degradation: unscored substations (sub.components === null)
      // are skipped rather than crashing the whole map. This surfaced as Turkey P30 in-scope, where
      // 82 of 4083 subs (2%) had components: null (fleet_summary.n_scored=4001) — the un-guarded
      // sub.components[k] read threw TypeError which aborted the .then() body and left GEO=null,
      // producing the "canvas 100% transparent + hitTest crashes on mousemove" symptom (Task #619).
      const compArrays = { C: [], V: [], I: [], E: [], S: [], T: [] };
      let compScoredCount = 0;
      for (const sub of SSI.substations) {
        if (!sub.components) continue;  // skip unscored subs
        for (const k of ['C', 'V', 'I', 'E', 'S', 'T']) {
          const v = sub.components[k];
          if (typeof v === 'number' && !isNaN(v)) compArrays[k].push(v);
        }
        compScoredCount++;
      }
      const compSkipped = SSI.substations.length - compScoredCount;
      if (compSkipped > 0) {
        console.log(`[map.js] Fleet median: ${compScoredCount}/${SSI.substations.length} substations with components; ${compSkipped} unscored subs skipped (Convention #56 visibly-honest)`);
      }
      for (const k of ['C', 'V', 'I', 'E', 'S', 'T']) {
        const sorted = compArrays[k].slice().sort((a, b) => a - b);
        if (sorted.length === 0) { fleetMedian[k] = 0; continue; }  // no scored subs — neutral median
        const mid = Math.floor(sorted.length / 2);
        fleetMedian[k] = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
      }

      // Auto-fit map to bbox of substations (or bounds polygon if present)
      // — uses the min/max of geographic coords + a 6% margin so the country
      // fills the canvas without clipping. Falls back to centroid-only if subs missing.
      const subEntries = Object.values(GEO.s);
      if (subEntries.length > 0) {
        let minLon=Infinity,maxLon=-Infinity,minLat=Infinity,maxLat=-Infinity;
        // Prefer bounds polygon extent when available — gives a country-shaped frame
        // rather than a substation-cluster frame (which can omit corners like coastline).
        if (BOUNDS && BOUNDS.features) {
          for (const f of BOUNDS.features) {
            const polys = (f.geometry.type === 'Polygon') ? [f.geometry.coordinates] : f.geometry.coordinates;
            for (const poly of polys) for (const ring of poly) for (const [lo,la] of ring) {
              if (lo<minLon) minLon=lo; if (lo>maxLon) maxLon=lo;
              if (la<minLat) minLat=la; if (la>maxLat) maxLat=la;
            }
          }
          // Mode-3 territorial-outlier safeguard (Discipline #36 follow-on, 25 Jun 2026;
          // extended Task #619, 30 Jul 2026 with per-country mainland-bbox filter).
          // bounds.json correctly includes overseas territories (Guyane française, Polynésie,
          // Chatham Islands, Tokelau, Réunion, Northern Ireland, Easter Island, Canadian Arctic
          // etc.) so the cross-border filter accepts legitimate territorial substations. But
          // the map viewport needs to frame WHERE THE GRID ACTUALLY IS — not where every
          // overseas territory sits. If bounds-extent is >60° in longitude (catches DOM-TOM
          // and anti-meridian crossings) or >2× the substation cluster (catches Easter-Island-
          // class compression), fall back to substation cluster extent. France 117° → mainland
          // ~14°; NZ 357° (anti-meridian) → mainland ~12°; Chile 43° → mainland ~9°. The 35
          // non-pathological countries continue to use bounds.json extent unchanged.
          //
          // Per-country mainland-bbox filter (Task #619 addition): France + US + Norway have
          // real substations sitting inside their overseas territories (Guyane 6°N/-53°W;
          // Alaska 65°N/-150°W; Svalbard 78°N/15°E). Naive substation-cluster fallback still
          // returns a pathological extent because the cluster INCLUDES the overseas subs.
          // The MAINLAND_BBOXES table below filters the cluster to mainland-only for these 3
          // countries; overseas-territory subs stay in memory + visible if the user pans to
          // them, but they don't dominate the auto-fit viewport. Chile / Canada / Denmark /
          // Portugal / NZ / Australia don't need this filter — they have zero substations in
          // their overseas territories, so their cluster naturally lands on mainland.
          const MAINLAND_BBOXES = {
            france:   { minLat: 41.0, minLon:  -5.5, maxLat: 51.5, maxLon:   9.5 },  // Métropole (excl. DOM-TOM)
            us:       { minLat: 24.0, minLon:-125.0, maxLat: 49.5, maxLon: -66.0 },  // CONUS (excl. Alaska + Hawaii + Guam + territories)
            norway:   { minLat: 57.5, minLon:   4.0, maxLat: 71.5, maxLon:  32.0 }   // Fastlandet (excl. Svalbard + Jan Mayen + Bouvet)
          };
          // Detect country slug from the intelligence-loader script tag's data-country attribute.
          // Falls back to '' for isolated map.html previews (no filter applied — same as before).
          const _countryEl = document.querySelector('[data-country]');
          const _countrySlug = (_countryEl && _countryEl.dataset && _countryEl.dataset.country) || '';
          const _mainland = MAINLAND_BBOXES[_countrySlug];
          let subMinLon=Infinity, subMaxLon=-Infinity, subMinLat=Infinity, subMaxLat=-Infinity;
          let _clusterInside = 0, _clusterExcluded = 0;
          for (const s of subEntries) {
            if (_mainland) {
              // Skip subs outside mainland bbox for cluster computation
              if (s.x < _mainland.minLon || s.x > _mainland.maxLon ||
                  s.y < _mainland.minLat || s.y > _mainland.maxLat) {
                _clusterExcluded++;
                continue;
              }
              _clusterInside++;
            }
            if (s.x<subMinLon) subMinLon=s.x; if (s.x>subMaxLon) subMaxLon=s.x;
            if (s.y<subMinLat) subMinLat=s.y; if (s.y>subMaxLat) subMaxLat=s.y;
          }
          if (_mainland) {
            console.log(`[map.js] Mainland-bbox filter (${_countrySlug}): ${_clusterInside} mainland subs anchor the viewport, ${_clusterExcluded} overseas-territory subs stay in memory + visible on pan (Task #619 fix)`);
            // Defensive: if the mainland bbox somehow excluded ALL substations (misconfigured
            // bbox or country entirely offshore), revert to whole-cluster extent so we don't
            // divide by zero downstream.
            if (_clusterInside === 0) {
              console.warn(`[map.js] Mainland-bbox filter for ${_countrySlug} excluded 100% of subs — reverting to whole-cluster extent as safety fallback`);
              subMinLon = Infinity; subMaxLon = -Infinity; subMinLat = Infinity; subMaxLat = -Infinity;
              for (const s of subEntries) {
                if (s.x<subMinLon) subMinLon=s.x; if (s.x>subMaxLon) subMaxLon=s.x;
                if (s.y<subMinLat) subMinLat=s.y; if (s.y>subMaxLat) subMaxLat=s.y;
              }
            }
          }
          const boundsLonSpan = maxLon - minLon;
          const boundsLatSpan = maxLat - minLat;
          const subsLonSpan = Math.max(0.01, subMaxLon - subMinLon);
          const subsLatSpan = Math.max(0.01, subMaxLat - subMinLat);
          // Trigger safeguard on EITHER latitude OR longitude pathology. Norway follow-on
          // (Task #619, 30 Jul 2026): bounds.json includes Svalbard (80°N) + Bouvet Island
          // (-54°S) → lat span 135° but lon span only 43°. Original safeguard checked only
          // lon so it never fired for Norway; mainland-Norway compressed to sub-pixel blob.
          // Adding lat-span check catches Norway + any future country with far-north or
          // far-south territorial extension (e.g. Denmark's Greenland is already served by
          // its own slug, but this makes the safeguard geometry-agnostic).
          if (boundsLonSpan > 60 || boundsLatSpan > 60 ||
              boundsLonSpan > subsLonSpan * 2 || boundsLatSpan > subsLatSpan * 2) {
            minLon = subMinLon; maxLon = subMaxLon;
            minLat = subMinLat; maxLat = subMaxLat;
          }
        } else {
          for (const s of subEntries) {
            if (s.x<minLon) minLon=s.x; if (s.x>maxLon) maxLon=s.x;
            if (s.y<minLat) minLat=s.y; if (s.y>maxLat) maxLat=s.y;
          }
        }
        view.cx = (minLon + maxLon) / 2;
        view.cy = (minLat + maxLat) / 2;
        // Wait for first resize() to know W,H then compute fit-scale below.
        view._fitBbox = { minLon, maxLon, minLat, maxLat };
      }

      resize();
      // After resize() sets W,H, compute fit-to-country scale
      if (view._fitBbox && W > 0 && H > 0) {
        const b = view._fitBbox;
        const lonSpan = Math.max(0.01, (b.maxLon - b.minLon) * COS42);
        const latSpan = Math.max(0.01, (b.maxLat - b.minLat));
        const margin = 0.92; // 8% padding around country
        const scaleX = (W * margin) / (lonSpan * (W / 12.3));
        const scaleY = (H * margin) / (latSpan * (W / 12.3));
        view.scale = Math.max(0.5, Math.min(scaleX, scaleY));
        delete view._fitBbox;
        requestDraw();
      }
      if (SSI.regions && !Array.isArray(SSI.regions)) SSI.regions = Object.values(SSI.regions);

      if (!SSI.regions) {
        var regionMap = {};
        (SSI.substations || []).forEach(function(s) {
          var r = s.region || s.province || 'Unknown';
          if (!regionMap[r]) regionMap[r] = {region: r, name: r, count: 0, R_median: 0, _sum: 0};
          regionMap[r].count++;
          regionMap[r]._sum += (s.R_median || 0);
        });
        SSI.regions = Object.values(regionMap).map(function(r) { r.R_median = r.count ? r._sum / r.count : 0; delete r._sum; return r; });
      }
      // Detect if fleet has meaningful classification spread
      var _classif = {};
      (SSI.substations || []).forEach(function(s) { _classif[s.classification] = (_classif[s.classification]||0)+1; });
      window._ssiHasSpread = Object.keys(_classif).length >= 1;  // (was >=3 — uniformly-classified fleets like LU were falling through to percentile fallback)

      // ── fleet_summary canonicalization (KB §65 — schema drift normalization) ──
      // Countries vary on key names: France/Italy use {median_R, P5, P95, band_pct, confidence_pct};
      // Slovenia/Czechia/Baltics use {R_median, R_min, R_max, bands}. Both must work in onLoaded callbacks.
      // We populate canonical aliases here so downstream code (per-country map.html callbacks,
      // SSIMap consumers) can use either key set without crashing.
      var fs = SSI.fleet_summary = SSI.fleet_summary || {};
      if (fs.median_R == null && fs.R_median != null) fs.median_R = fs.R_median;
      if (fs.R_median == null && fs.median_R != null) fs.R_median = fs.median_R;
      if (fs.mean_R == null) fs.mean_R = fs.median_R || fs.R_median || 0;
      if (fs.P5 == null && fs.R_min != null) fs.P5 = fs.R_min;
      if (fs.P95 == null && fs.R_max != null) fs.P95 = fs.R_max;
      if (fs.R_min == null && fs.P5 != null) fs.R_min = fs.P5;
      if (fs.R_max == null && fs.P95 != null) fs.R_max = fs.P95;
      // Synthesize band_pct from bands if missing (Slovenia/etc don't emit it)
      if (!fs.band_pct && fs.bands) {
        var totalForPct = fs.total || Object.values(fs.bands).reduce(function(a,b){return a + (b||0);}, 0) || 1;
        fs.band_pct = {};
        for (var b in fs.bands) { fs.band_pct[b] = (fs.bands[b] / totalForPct) * 100; }
      }
      if (!fs.confidence_pct) fs.confidence_pct = { high: 0, medium: 0, low: 0 };
      if (!fs.confidence_tiers) fs.confidence_tiers = {};

      wireFilters();
      clearDetailPanel();

      // Wrap callback in try/catch so a per-country callback bug doesn't trigger
      // the generic 'Failed to load map data' error (anti-pattern A8 — render-chain cascade)
      if (loadedCallback) {
        try { loadedCallback(SSI); }
        catch (e) { console.error('Map onLoaded callback error (data IS loaded):', e); }
      }

      console.log(`SSI Map loaded: ${Object.keys(GEO.s).length} subs, ${GEO.l.length} lines, ${SSI.substations.length} SSI records`);
      } catch (e) {
        console.error('[map.js DRAWTRACE] .then() body threw:', e && e.message, 'stack:', e && e.stack);
        throw e;  // Let outer .catch fire the generic error banner + surface to console.error
      }
    }).catch(err => {
      console.error('Failed to load map data:', err);
      const container = canvas.parentElement;
      container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--warm-grey);padding:20px;text-align:center">
        <div> Failed to load map data. Make sure grid-geo.json and ssi-data.json are in the same directory.</div>
      </div>`;
    });
  }

  // Export
  window.SSIMap = { init: initMap, toggleBreakdown: toggleBreakdown };
})();
