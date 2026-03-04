/* ═══════════════════════════════════════════════════════════
   SSI Index Dashboard — Interactive Map Engine
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

    // ─ Draw lines ─
    if (showLines) {
      ctx.lineCap = 'round';
      for (const l of GEO.l) {
        const highlighted = hlLines.has(l.i);
        if (isSelecting && !highlighted) {
          ctx.globalAlpha = 0.08;
        } else {
          ctx.globalAlpha = isSelecting ? 0.9 : 0.5;
        }
        ctx.strokeStyle = kvColor(l.kv);
        ctx.lineWidth = (highlighted ? kvWidth(l.kv) * 1.8 : kvWidth(l.kv)) * Math.min(s * 0.5, 1.5);

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
        ctx.globalAlpha = 0.1;
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
        ctx.globalAlpha = isSelecting && !highlighted ? 0.3 : 0.9;
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
      const adj = GEO.a[id] || [];
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
    const adj = GEO.a[sid] || [];
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
      const pct = Math.max(0, Math.min((1 - val / w) * 100, 100));
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
      ['R6 Restoration Speed', ssi.modifiers.R6_restoration],
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
        <div style="font-size:11px;color:var(--warm-grey);margin-bottom:14px">${ssi.region} · ${ssi.province} · ${ssi.voltage_kv} kV · ${ssi.substation_id}</div>
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
          <div style="display:flex;justify-content:space-between"><span>Energy poverty</span><span style="font-weight:500">${ssi.socio_economic.EP_rate_region}% — V_socio ${ssi.socio_economic.V_socio.toFixed(2)}</span></div>
          <div style="display:flex;justify-content:space-between"><span>E2 Productivity</span><span style="font-weight:500">${ssi.socio_economic.E2_local.toFixed(3)}</span></div>
          <div style="display:flex;justify-content:space-between"><span>DER Stress (T1)</span><span style="font-weight:500">${ssi.transition.T1_score.toFixed(3)}</span></div>
          <div style="display:flex;justify-content:space-between"><span>Graph degree</span><span style="font-weight:500">${ssi.graph_topology.degree}${ssi.graph_topology.is_bridge ? ' (bridge)' : ''}</span></div>
          <div style="display:flex;justify-content:space-between"><span>BC percentile</span><span style="font-weight:500">${ssi.graph_topology.BC_percentile.toFixed(2)}</span></div>
          <div style="display:flex;justify-content:space-between"><span>Confidence</span><span style="font-weight:500">${ssi.confidence_tier}</span></div>
          <div style="display:flex;justify-content:space-between"><span>Fleet percentile</span><span style="font-weight:500">${(ssi.fleet_percentile * 100).toFixed(1)}%</span></div>
        </div>
      </div>`;
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

    // Populate regions dropdown
    if (regionSel && SSI) {
      const regions = SSI.regions.map(r => r.region).sort();
      regionSel.innerHTML = '<option value="all">All Regions</option>' +
        regions.map(r => `<option value="${r}">${r}</option>`).join('');
    }

    // Zoom buttons
    const zoomIn = document.getElementById('zoomIn');
    const zoomOut = document.getElementById('zoomOut');
    const zoomFit = document.getElementById('zoomFit');
    if (zoomIn) zoomIn.onclick = () => { view.scale = Math.min(50, view.scale * 1.4); requestDraw(); };
    if (zoomOut) zoomOut.onclick = () => { view.scale = Math.max(0.5, view.scale / 1.4); requestDraw(); };
    if (zoomFit) zoomFit.onclick = () => { view.cx = 12.5; view.cy = 42.0; view.scale = 1; requestDraw(); };
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
      fetch(basePath + 'grid-geo.json').then(r => r.json()),
      fetch(basePath + 'ssi-data.json').then(r => r.json())
    ]).then(([geo, ssi]) => {
      GEO = geo;
      SSI = ssi;

      // Build lookup: internal_id → ssi record
      ssiMap = {};
      for (const sub of SSI.substations) {
        ssiMap[sub.internal_id] = sub;
      }

      // Build lookup: line.i → line object (fast O(1) instead of O(n) find)
      lineById = {};
      for (const l of GEO.l) {
        lineById[l.i] = l;
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
  window.SSIMap = { init: initMap };
})();
