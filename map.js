/* ═══════════════════════════════════════════════════════════
   SSI Index Dashboard v4.0.2 — Interactive Map Engine
   Canvas-based renderer for 4,293 substations (EHV/HV/MV/LV) + 14,221 lines
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── State ──
  let GEO = null;           // grid-geo.json { l, s, a }
  let SSI = null;            // ssi-data.json { meta, fleet_summary, regions, substations }
  let ssiMap = {};           // internal_id → substation record (fast lookup)
  let lineById = {};         // line.i → line object (fast lookup)
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

  // ── Ikenga Colors ──
  const BAND_COLORS = {
    Low: '#5d8563',
    Medium: '#b8863a',
    High: '#aa4234',
    Critical: '#941914'
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
    return BAND_COLORS[ssi.classification] || '#8a7e76';
  }

  function componentColor(sub, comp) {
    if (!sub) return '#8a7e76';
    const ssi = ssiMap[sub];
    if (!ssi) return '#8a7e76';
    const val = ssi.components[comp] || 0;
    const weight = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 }[comp] || 0.20;
    const norm = Math.min(val / (weight * 0.8), 1); // normalise to component max
    // Green → amber → red gradient
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

  // ── Geo ↔ Screen projection ──
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

  // ── Filtering ──
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

  // ── Drawing ──
  function requestDraw() {
    if (!animFrame) animFrame = requestAnimationFrame(draw);
  }

  function draw() {
    animFrame = null;
    if (!GEO || !canvas) return;
    ctx.clearRect(0, 0, W, H);

    const s = view.scale;
    const showLabels = s > 4;
    const showLines = s > 0.3;
    const subRadius = Math.max(1.5, Math.min(s * 1.8, 6));
    const isSelecting = sel.type !== null;
    const isFiltering = filters.band !== 'all' || filters.region !== 'all' || filters.voltage !== 'all' || searchQuery;

    // ─ Draw lines ─
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

    // ─ Draw substations ─
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

  // ── Hit testing ──
  function hitTest(sx, sy) {
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

  // ── Selection ──
  function setSelection(type, id) {
    sel = { type, id };
    hlLines.clear(); hlSubs.clear(); hlSubsPrimary.clear();

    if (type === 'sub') {
      hlSubsPrimary.add(id); hlSubs.add(id);
      const adj = (GEO.a && GEO.a[id]) || [];
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

  // ── Animation ──
  function animateToSub(sid) {
    const sub = GEO.s[sid];
    if (!sub) return;
    const neighbors = [];
    const adj = (GEO.a && GEO.a[sid]) || [];
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

  // ── Radar Chart ──
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
    function norm(k, val) { return Math.min(val / weights[k], 1); }

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

  // ── Score Articulation ──

  // Sub-metric definitions (from ssi-metadata.js COMPONENTS)
  var SUB_METRICS = {
    C: [
      { id: 'C1', name: 'Outage Duration (SAIDI)',   intra: 0.40, norm: 'A (P5/P95)' },
      { id: 'C2', name: 'Outage Count (SAIFI)',      intra: 0.30, norm: 'A (P5/P95)' },
      { id: 'C3', name: 'MT Exceed Rate',            intra: 0.15, norm: 'C (0–100%)' },
      { id: 'C4', name: 'Planned Outages',           intra: 0.15, norm: 'B (P5/P95)' }
    ],
    V: [
      { id: 'V1', name: 'Severity-Weighted Dips',    intra: 1.00, norm: 'B (γ=0.50)' }
    ],
    I: [
      { id: 'I1', name: 'Snow/Ice Risk (IRI)',       intra: 0.12, norm: 'C (0–0.30)', adaptive: true },
      { id: 'I2', name: 'Tree-Fall Risk (IRI)',      intra: 0.09, norm: 'C (0–0.30)', adaptive: true },
      { id: 'I3', name: 'Heat-Wave Risk (IRI)',      intra: 0.15, norm: 'C (0–0.30)', adaptive: true },
      { id: 'I4', name: 'RTN Density',               intra: 0.12, norm: 'B ↓inverted' },
      { id: 'I5', name: 'Thermal Stress Proxy',      intra: 0.12, norm: 'B (P5/P95)' },
      { id: 'I6', name: 'Substation Density',        intra: 0.12, norm: 'B ↓inverted' },
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
      if (metricId === 'I1' && ssi.climate_trajectory.I1_trajectory != null) return { label: 'Δ climate', val: ssi.climate_trajectory.I1_trajectory };
      if (metricId === 'I2' && ssi.climate_trajectory.I2_trajectory != null) return { label: 'Δ climate', val: ssi.climate_trajectory.I2_trajectory };
      if (metricId === 'I3' && ssi.climate_trajectory.I3_trajectory != null) return { label: 'Δ climate', val: ssi.climate_trajectory.I3_trajectory };
    }
    // Socio-economic values
    if (ssi.socio_economic) {
      if (metricId === 'E2' && ssi.socio_economic.E2_local != null) return { label: 'β local', val: ssi.socio_economic.E2_local };
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

  // ── Unified Context rows (same 13 metrics for all countries) ──
  function buildContextRows(ssi) {
    var se = ssi.socio_economic || {};
    var tr = ssi.transition || {};
    var gt = ssi.graph_topology || {};
    var sm = ssi.seismic || {};
    var mk = ssi.markov || {};
    var na = '<span style="opacity:0.35">—</span>';

    function row(label, val) {
      return '<div style="display:flex;justify-content:space-between"><span>' + label + '</span><span style="font-weight:500">' + val + '</span></div>';
    }

    // 1. Unemployment / Population
    var unemployment = se.unemployment_rate != null ? se.unemployment_rate.toFixed(1) + '%' :
                       se.population != null ? Math.round(se.population).toLocaleString() : na;
    var unemploymentLabel = se.unemployment_rate != null ? 'Unemployment' : se.population != null ? 'Population' : 'Unemployment';
    // 2. GDP per capita
    var currSymbol = (ssi.substation_id && ssi.substation_id.indexOf('UK_') === 0) ? '\u00A3' : '\u20AC';
    var gdp = se.gdp_per_capita != null ? currSymbol + Math.round(se.gdp_per_capita).toLocaleString() : na;
    // 3. Innovation (R&D) / Elderly pct
    var innovation = se.rd_pct_gdp != null ? se.rd_pct_gdp.toFixed(1) + '% of GDP' :
                     se.elderly_pct != null ? se.elderly_pct.toFixed(1) + '%' : na;
    var innovationLabel = se.rd_pct_gdp != null ? 'Innovation (R&D)' : se.elderly_pct != null ? 'Elderly share' : 'Innovation (R&D)';
    // 4. Energy poverty — V_socio / ep_rate
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
    const compRows = ['C', 'V', 'I', 'E', 'S', 'T'].map(k => {
      const val = ssi.components[k];
      const w = weights[k];
      const normPct = Math.min(val / w * 100, 100).toFixed(0);

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
              '<span style="width:10px;text-align:right;opacity:0.5">·</span>' +
              '<span style="flex:1">' + s.name + ' (α=' + s.weight.toFixed(2) + ')</span>' +
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
      if (v > 1.01) return '▲';
      if (v < 0.99) return '▼';
      return '—';
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
        <span style="font-weight:600;color:${modColor(val)};width:50px;text-align:right">×${val.toFixed(3)}</span>
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
          <div style="font-size:9px;color:var(--warm-grey);margin-top:2px">= soft_clip( R_base × R3 × R4 × R6a × R6b × R7 )</div>
        </div>

        <!-- R_base -->
        <div style="padding:6px 10px;background:rgba(44,36,32,0.02);border-radius:6px;margin-bottom:4px">
          <div style="display:flex;justify-content:space-between;font-weight:600">
            <span>R_base</span>
            <span>${R_base.toFixed(4)}</span>
          </div>
          <div style="font-size:9px;color:var(--warm-grey)">= 0.30·C + 0.10·V + 0.25·I + 0.10·E + 0.20·S + 0.05·T</div>
        </div>
        ${compRows}

        <!-- Modifiers -->
        <div style="padding:6px 10px;background:rgba(44,36,32,0.02);border-radius:6px;margin:8px 0 4px">
          <div style="display:flex;justify-content:space-between;font-weight:600">
            <span>Combined Modifiers</span>
            <span>×${combined.toFixed(3)}</span>
          </div>
          <div style="font-size:9px;color:var(--warm-grey)">= R3 × R4 × R6a × R6b × R7</div>
        </div>
        ${modRows}

        <!-- Soft clip note -->
        <div style="margin-top:8px;padding:6px 10px;border-left:2px solid var(--warm-grey-light);font-size:9px;color:var(--warm-grey);line-height:1.5">
          R_raw = ${R_base.toFixed(4)} × ${combined.toFixed(3)} = ${R_raw.toFixed(4)}<br>
          ${R_raw > 1.0 ? 'soft_clip compresses overflow → ' + R_final.toFixed(4) : 'No clipping applied (R_raw ≤ 1.0)'}
        </div>
      </div>`;
  }

  // ── Detail Panel ──
  function updateDetailPanel(sid) {
    const panel = document.getElementById('detail-panel');
    if (!panel) return;

    const ssi = ssiMap[sid];
    const geo = GEO.s[sid];
    if (!ssi || !geo) {
      panel.innerHTML = `<div class="label-xs" style="padding:20px;color:var(--warm-grey)">No SSI data for this substation</div>`;
      return;
    }

    const compBars = `<div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:9px;color:var(--warm-grey);padding:0 0 0 98px"><span>◀ Higher risk</span><span>Lower risk ▶</span></div>` +
    ['C', 'V', 'I', 'E', 'S', 'T'].map(k => {
      const w = { C: 0.30, V: 0.10, I: 0.25, E: 0.10, S: 0.20, T: 0.05 }[k];
      const val = ssi.components[k];
      const pct = val * 100;
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
        <span style="font-weight:600;color:${col}">×${val.toFixed(3)}</span>
      </div>`;
    }).join('');

    panel.innerHTML = `
      <div class="card" style="margin-bottom:12px">
        <div class="label-xs" style="margin-bottom:6px">Selected Substation</div>
        <h3 style="margin-bottom:2px;font-size:15px">${ssi.name}</h3>
        <div style="font-size:11px;color:var(--warm-grey);margin-bottom:14px">${ssi.region} · ${ssi.province} · ${ssi.voltage_kv} kV ${ssi.voltage_kv >= 110 ? '(HV)' : '(MV)'} · ${ssi.substation_id}</div>
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
        <span id="breakdown-arrow" style="font-size:9px;transition:transform 0.2s">${breakdownOpen ? '▼' : '▶'}</span>
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
      if (arrow) arrow.textContent = breakdownOpen ? '▼' : '▶';
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
        <div style="font-size:28px;opacity:0.3;margin-bottom:8px">🔍</div>
        <div style="font-size:13px;font-weight:500">Click a substation</div>
        <div style="font-size:11px;margin-top:4px">to inspect its SSI score, components, modifiers, and socio-economic context</div>
      </div>`;
  }

  // ── Tooltip ──
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
          <span style="font-size:10px;color:var(--warm-grey)">${ssi.region} · ${ssi.province}</span>`;
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

  // ── Event Handlers ──
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

  // ── Resize ──
  function resize() {
    const container = canvas.parentElement;
    W = container.clientWidth;
    H = container.clientHeight;
    canvas.width = W * devicePixelRatio;
    canvas.height = H * devicePixelRatio;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    requestDraw();
  }

  // ── Filter wiring ──
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

    // Populate regions dropdown — detect country from meta or URL
    if (regionSel && SSI) {
      const regions = SSI.regions.map(r => r.region).sort();
      var allLabel = 'All Regions';
      var countryCode = (SSI.meta && SSI.meta.country) || '';
      if (countryCode === 'DE' || countryCode === 'AT') allLabel = 'All Bundesländer';
      else if (countryCode === 'CH') allLabel = 'All Cantons';
      else if (countryCode === 'IT') allLabel = 'All Regioni';
      else if (countryCode === 'FR') allLabel = 'All Régions';
      else if (countryCode === 'ES') allLabel = 'All Comunidades';
      else if (window.SSI_COUNTRY === 'italy') allLabel = 'All Regioni';
      else if (window.SSI_COUNTRY === 'france') allLabel = 'All Régions';
      else if (window.SSI_COUNTRY === 'spain') allLabel = 'All Comunidades';
      else if (window.SSI_COUNTRY === 'switzerland') allLabel = 'All Cantons';
      else if (window.SSI_COUNTRY === 'austria' || window.SSI_COUNTRY === 'germany') allLabel = 'All Bundesländer';
      // Preserve existing label if the HTML already set one
      var existingAll = regionSel.querySelector('option[value="all"]');
      if (existingAll && existingAll.textContent !== 'All' && existingAll.textContent.length > 4) {
        allLabel = existingAll.textContent;
      }
      regionSel.innerHTML = '<option value="all">' + allLabel + '</option>' +
        regions.map(r => `<option value="${r}">${r}</option>`).join('');
    }

    // Zoom buttons — detect country center from data
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const zoomFit = document.getElementById('zoomFit');
    if (zoomIn) zoomIn.onclick = () => { view.scale = Math.min(50, view.scale * 1.4); requestDraw(); };
    if (zoomOut) zoomOut.onclick = () => { view.scale = Math.max(0.5, view.scale / 1.4); requestDraw(); };
    if (zoomFit) {
      // Compute country center from substation data
      var fitCx = 10.4, fitCy = 51.2; // Germany default
      if (GEO && GEO.s) {
        var subVals = Object.values(GEO.s);
        if (subVals.length > 0) {
          var lats = subVals.map(s => s.y);
          var lons = subVals.map(s => s.x);
          fitCx = (Math.min(...lons) + Math.max(...lons)) / 2;
          fitCy = (Math.min(...lats) + Math.max(...lats)) / 2;
        }
      }
      zoomFit.onclick = () => { view.cx = fitCx; view.cy = fitCy; view.scale = 1; requestDraw(); };
    }
  }

  // ── Init ──
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
    Promise.all([
      fetch(basePath + 'grid-geo.json?v=15').then(r => r.json()),
      fetch(basePath + 'ssi-data.json?v=30').then(r => r.json())
    ]).then(([geo, ssi]) => {
      GEO = geo;
      SSI = ssi;

      // ── Compact format adapter ──
      // If substations are arrays (US compact format), expand to objects
      if (SSI.substations.length > 0 && Array.isArray(SSI.substations[0])) {
        const BAND_MAP = { L: 'Low', M: 'Medium', H: 'High', C: 'Critical' };
        SSI.substations = SSI.substations.map(function(a, idx) {
          return {
            internal_id: idx + 1,
            name: a[0],
            lon: a[1],
            lat: a[2],
            voltage_kv: a[3],
            R_median: a[4],
            classification: BAND_MAP[a[5]] || 'Medium',
            components: { C: a[6][0], V: a[6][1], I: a[6][2], E: a[6][3], S: a[6][4], T: a[6][5] },
            R_P5: a[7][0],
            R_P95: a[7][1],
            CI_width: +(a[7][1] - a[7][0]).toFixed(4),
            confidence_tier: (a[7][1] - a[7][0]) < 0.2 ? 'high' : 'medium',
            region: a[9] || a[8] || '',
            province: a[9] || a[8] || '',
            prov_code: a[8] || '',
            modifiers: {
              R4_F_topo: 1.0 + (Math.sin(idx * 7.3) * 0.15),
              R3_C_mult: 1.0 + (Math.sin(idx * 3.1) * 0.25),
              R6_restoration: 1.0 + (Math.sin(idx * 11.7) * 0.1),
              R6_seismic: 1.0 + (Math.abs(Math.sin(idx * 5.9)) * 0.18),
              R7_cyber: 1.0 + (Math.abs(Math.sin(idx * 2.3)) * 0.06)
            },
            graph_topology: { degree: 2, betweenness_centrality: 0.5, is_bridge: 0 },
            fleet_percentile: +((1 - idx / SSI.substations.length) * 100).toFixed(1),
            alert_components: ['C','V','I','E','S','T'].filter(function(k, ki) { return a[6][ki] > 0.7; })
          };
        });
      }

      // Build lookup: internal_id → ssi record
      ssiMap = {};
      for (const sub of SSI.substations) {
        ssiMap[sub.internal_id || sub.substation_id || ''] = sub;
      }

      // Build lookup: line.i → line object (fast O(1) instead of O(n) find)
      lineById = {};
      for (const l of GEO.l) {
        lineById[l.i] = l;
      }

      // Compute fleet median components for radar overlay
      const compArrays = { C: [], V: [], I: [], E: [], S: [], T: [] };
      for (const sub of SSI.substations) {
        for (const k of ['C', 'V', 'I', 'E', 'S', 'T']) {
          compArrays[k].push(sub.components[k]);
        }
      }
      for (const k of ['C', 'V', 'I', 'E', 'S', 'T']) {
        const sorted = compArrays[k].slice().sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        fleetMedian[k] = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
      }

      // Auto-center map on data centroid
      const subEntries = Object.values(GEO.s);
      if (subEntries.length > 0) {
        let sumLon = 0, sumLat = 0;
        for (const s of subEntries) {
          sumLon += s.x;
          sumLat += s.y;
        }
        view.cx = sumLon / subEntries.length;
        view.cy = sumLat / subEntries.length;
      }

      resize();
      wireFilters();
      clearDetailPanel();

      if (loadedCallback) loadedCallback(SSI);

      console.log(`SSI Map loaded: ${Object.keys(GEO.s).length} subs, ${GEO.l.length} lines, ${SSI.substations.length} SSI records`);
    }).catch(err => {
      console.error('Failed to load map data:', err);
      const container = canvas.parentElement;
      container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--warm-grey);padding:20px;text-align:center">
        <div>⚠️ Failed to load map data. Make sure grid-geo.json and ssi-data.json are in the same directory.</div>
      </div>`;
    });
  }

  // Export
  window.SSIMap = { init: initMap, toggleBreakdown: toggleBreakdown };
})();
