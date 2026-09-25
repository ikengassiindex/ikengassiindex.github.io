/* ═══════════════════════════════════════════════════════════
   SSI v4.0.2 — ESG Report shared helpers
   ───────────────────────────────────────────────────────────
   Pure, DOM-free helpers that are identical across all 22
   country ESG pages. Loaded via <script src="../esg-helpers.js">
   before the per-page inline script.

   v1.0 (Wave 3) — extracted from france/esg-report.html as the
   canonical variant. Mexico + denmark previously had `var`
   instead of `const` and an extra comment in monthSeed — those
   divergences are harmonised here.

   Functions exposed globally (ES5 var-scope, consistent with
   the rest of the stack): bandClass, displayName, monthSeed,
   readinessLabel, readinessText, seededIndex.
   ═══════════════════════════════════════════════════════════ */

function bandClass(classification) {
  if (!classification) return 'low';
  var c = classification.toLowerCase();
  if (c === 'critical') return 'critical';
  if (c === 'high') return 'high';
  if (c === 'medium') return 'medium';
  return 'low';
}

function displayName(d) {
  var n = d.name || "";
  if (n && !n.startsWith("UNKNOWN") && !n.startsWith("Sub_") && n !== "—") return n;
  var parts = [];
  if (d.province) parts.push(d.province);
  if (d.substation_id) {
    var sid = d.substation_id.replace(/^[A-Z]{2}_/, "");
    if (sid.startsWith("UNKNOWN")) sid = sid.replace("UNKNOWN", "#");
    parts.push("Station " + sid);
  } else if (d.region) {
    parts.push(d.region + " Station");
  }
  return parts.length ? parts.join(" · ") : (n || "Substation");
}

function monthSeed() {
  // Monthly rotation starts May 2026; keep March substation until then.
  var d = new Date(), y = d.getFullYear(), m = d.getMonth() + 1;
  if (y < 2026 || (y === 2026 && m < 5)) return 202603;
  return y * 100 + m;
}

function readinessLabel(score) {
  if (score >= 0.80) return 'ready';
  if (score >= 0.40) return 'partial';
  return 'gap';
}

function readinessText(score) {
  if (score >= 0.80) return 'READY';
  if (score >= 0.40) return 'PARTIAL';
  return 'GAP';
}

function seededIndex(seed, len) {
  if (len === 0) return 0;
  var h = seed;
  h = ((h >>> 16) ^ h) * 0x45d9f3b | 0;
  h = ((h >>> 16) ^ h) * 0x45d9f3b | 0;
  h = (h >>> 16) ^ h;
  return Math.abs(h) % len;
}
