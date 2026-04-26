#!/usr/bin/env python3.12
"""Generate graph-financial.html with 2D ⇄ 3D toggle.

2D: vis-network (keeps all existing controls + click→sidebar)
3D: 3d-force-graph (Three.js / WebGL)

Both render from the same buildData() output. Click handler populates the
same sidebar in either mode.
"""
import json
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")

graph = json.loads((ROOT / "graphify-financial/graph-financial.json").read_text())
graph_js = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SEAJ TSIA — Multi-Company Financial Graph</title>
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<!-- THREE first; three-spritetext UMD expects window.three (lowercase).
     three-viewport-gizmo reads window.THREE. -->
<script src="https://unpkg.com/three@0.158.0/build/three.min.js"></script>
<script>window.three = window.THREE;</script>
<script src="https://unpkg.com/three-spritetext@1.8.2/dist/three-spritetext.min.js"></script>
<script src="https://unpkg.com/three-viewport-gizmo@2.2.0/dist/three-viewport-gizmo.umd.cjs"></script>
<script src="https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #0b1220; color: #e5e7eb; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  header { padding: 10px 16px; background: #111827; border-bottom: 1px solid #1f2937; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
  header h1 { font-size: 15px; font-weight: 600; color: #93c5fd; }
  header .meta { font-size: 11px; color: #6b7280; }
  .view-toggle { display: inline-flex; border: 1px solid #374151; border-radius: 4px; overflow: hidden; }
  .view-toggle button { background: #1f2937; color: #9ca3af; border: none; padding: 6px 12px; font-size: 12px; cursor: pointer; font-family: inherit; }
  .view-toggle button.active { background: #1e3a8a; color: #dbeafe; }
  .controls { display: flex; gap: 14px; align-items: end; margin-left: auto; flex-wrap: wrap; }
  .control { display: flex; flex-direction: column; gap: 3px; }
  .control label { font-size: 10px; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.05em; }
  .control select, .control input { background: #1f2937; color: #e5e7eb; border: 1px solid #374151; padding: 5px 8px; border-radius: 4px; font-size: 12px; }
  .control input[type="range"] { width: 180px; }
  .control select.focus { background: #1e3a8a; border-color: #3b82f6; font-weight: 500; }
  main { flex: 1; display: flex; min-height: 0; position: relative; }
  .canvas-wrap { flex: 1; position: relative; background: #0b1220; }
  #network-2d, #network-3d { position: absolute; inset: 0; }
  #network-3d { display: none; }
  body.is-3d #network-2d { display: none; }
  body.is-3d #network-3d { display: block; }
  aside { width: 360px; background: #111827; border-left: 1px solid #1f2937; padding: 14px; overflow-y: auto; font-size: 12px; }
  aside h2 { font-size: 13px; color: #93c5fd; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #1f2937; }
  aside .empty { color: #6b7280; font-style: italic; }
  .badge { display: inline-block; background: #1e3a8a; color: #bfdbfe; padding: 1px 6px; border-radius: 8px; font-size: 9px; margin-right: 3px; }
  .badge-warn { background: #7c2d12; color: #fed7aa; }
  .kv { margin-bottom: 4px; }
  .kv .k { color: #9ca3af; font-size: 10px; text-transform: uppercase; }
  .kv .v { color: #e5e7eb; }
  .metric-row { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #1f2937; font-size: 11px; }
  .metric-row .name { color: #9ca3af; }
  .metric-row .val { color: #d1fae5; font-variant-numeric: tabular-nums; font-weight: 500; }
  .metric-block { margin-bottom: 10px; }
  .metric-block .title { font-size: 11px; color: #f3f4f6; font-weight: 500; margin-bottom: 3px; }
  footer { padding: 6px 16px; background: #111827; border-top: 1px solid #1f2937; font-size: 10px; color: #6b7280; display: flex; gap: 12px; flex-wrap: wrap; }
  .legend-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
  .year-display { font-size: 14px; font-weight: 600; color: #93c5fd; min-width: 40px; text-align: center; }
  details summary { cursor: pointer; color: #9ca3af; font-size: 11px; padding: 4px 0; }
  .aids-panel { position: absolute; top: 12px; left: 12px; background: rgba(17,24,39,0.88); border: 1px solid #1f2937; border-radius: 6px; padding: 8px 10px; font-size: 11px; z-index: 10; display: none; backdrop-filter: blur(4px); }
  body:not(.is-3d) .tvg-container { display: none !important; }
  .tvg-container { z-index: 11 !important; }
  body.is-3d .aids-panel { display: block; }
  .aids-title { color: #93c5fd; font-weight: 600; margin-bottom: 6px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; }
  .aids-row { display: flex; gap: 6px; margin-bottom: 5px; align-items: center; flex-wrap: wrap; }
  .aids-row:last-child { margin-bottom: 0; }
  .aid-toggle { display: inline-flex; align-items: center; gap: 4px; color: #d1d5db; cursor: pointer; user-select: none; padding: 2px 4px; }
  .aid-toggle input { cursor: pointer; margin: 0; }
  .aid-btn { background: #1f2937; color: #e5e7eb; border: 1px solid #374151; padding: 3px 9px; border-radius: 3px; cursor: pointer; font-size: 11px; font-family: inherit; }
  .aid-btn:hover { background: #374151; border-color: #4b5563; }
  .aid-btn.primary { background: #1e3a8a; border-color: #3b82f6; color: #dbeafe; }
  .aid-divider { width: 1px; height: 18px; background: #374151; margin: 0 4px; }
</style>
</head>
<body>
<header>
  <div>
    <h1>SEAJ TSIA — Multi-Company Financial Graph</h1>
    <div class="meta">__META__</div>
  </div>
  <div class="view-toggle" role="tablist">
    <button id="btn2d" class="active">2D</button>
    <button id="btn3d">3D</button>
  </div>
  <div class="controls">
    <div class="control">
      <label>Focus</label>
      <select id="companyFocus" class="focus"></select>
    </div>
    <div class="control">
      <label>Size by metric</label>
      <select id="metricSelect"></select>
    </div>
    <div class="control">
      <label>Year</label>
      <input type="range" id="yearSlider">
      <div class="year-display" id="yearDisplay">2024</div>
    </div>
    <div class="control">
      <label>Currency</label>
      <select id="currencySelect">
        <option value="usd">USD (cross-comparable)</option>
        <option value="native">Native</option>
      </select>
    </div>
    <div class="control">
      <label>People</label>
      <select id="peopleFilter">
        <option value="all">Show everyone</option>
        <option value="directors">Board only</option>
        <option value="executives">Executives only</option>
        <option value="cross">Cross-company links only</option>
        <option value="none">Hide all people</option>
      </select>
    </div>
  </div>
</header>
<main>
  <div class="canvas-wrap">
    <div id="network-2d"></div>
    <div id="network-3d"></div>
    <div class="aids-panel" id="aidsPanel">
      <div class="aids-title">3D View aids</div>
      <div class="aids-row">
        <label class="aid-toggle" title="Show world XYZ axes at origin"><input type="checkbox" id="aidAxes"> Axes</label>
        <label class="aid-toggle" title="Fade distant nodes for depth perception"><input type="checkbox" id="aidFog"> Fog</label>
        <label class="aid-toggle" title="Slow continuous rotation"><input type="checkbox" id="aidRotate"> Auto-rotate</label>
      </div>
      <div class="aids-row">
        <button class="aid-btn primary" id="aidHome" title="Fit all nodes in view">⌂ Home / Fit</button>
        <span style="color:#6b7280;font-size:10px;margin-left:6px">Top/Front/Side/Iso → use the cube ↗</span>
      </div>
    </div>
  </div>
  <aside>
    <h2>Details</h2>
    <div id="details"><p class="empty">Use <strong>Focus</strong> to drill into one company, or click any node for source-linked details.</p></div>
  </aside>
</main>
<footer>
  <span><span class="legend-dot" style="background:#3b82f6"></span>Company</span>
  <span><span class="legend-dot" style="background:#f59e0b"></span>Board / Director</span>
  <span><span class="legend-dot" style="background:#10b981"></span>Executive Officer / SVP</span>
  <span><span class="legend-dot" style="background:#a78bfa"></span>VP</span>
  <span><span class="legend-dot" style="background:#ef4444"></span>Cross-company person</span>
  <span style="margin-left:auto" id="fxFooter">FX rates loading…</span>
</footer>
<script>
const GRAPH = __GRAPH__;
const FX = GRAPH.graph.fx_to_usd || {};
const FX_SOURCES = GRAPH.graph.fx_sources || {};
const FX_FETCHED = GRAPH.graph.fx_fetched_at;

const METRIC_LABELS = {
  revenue: "Revenue", net_income: "Net income", operating_income: "Operating income",
  total_assets: "Total assets", total_equity: "Total equity", gross_profit: "Gross profit",
  employees: "Employees", gross_margin_pct: "Gross margin %", operating_margin_pct: "Operating margin %",
  eps: "Earnings per share", dividend_per_share: "Dividend per share",
};

const PERSON_COLORS = {
  board_director: "#f59e0b", independent_director: "#f59e0b",
  executive_officer: "#10b981", senior_vp: "#10b981",
  vp: "#a78bfa", committee_member: "#f59e0b", other: "#6b7280",
};

const COMPANY_NODES = GRAPH.nodes.filter(n => n.type === "company");
const PEOPLE_NODES = GRAPH.nodes.filter(n => n.type === "person");

function shortTicker(t) {
  if (!t) return "";
  for (const p of t.split(",")) { const m = p.match(/:(\\S+)$/); if (m) return m[1]; }
  return t.slice(0, 8);
}

const companyFocus = document.getElementById("companyFocus");
companyFocus.appendChild(Object.assign(document.createElement("option"), {value:"_all", textContent:"All companies"}));
COMPANY_NODES.slice().sort((a,b)=>a.label.localeCompare(b.label)).forEach(c => {
  const tk = shortTicker(c.ticker);
  companyFocus.appendChild(Object.assign(document.createElement("option"), {value:c.id, textContent: tk?`${c.label} (${tk})`:c.label}));
});
companyFocus.value = "_all";

const ALL_YEARS = [...new Set(COMPANY_NODES.flatMap(n => Object.values(n.metrics_canonical || {}).flatMap(m => Object.keys(m.values))))].sort();
const ALL_METRICS = [...new Set(COMPANY_NODES.flatMap(n => Object.keys(n.metrics_canonical || {})))];

const metricSel = document.getElementById("metricSelect");
ALL_METRICS.sort().forEach(m => {
  metricSel.appendChild(Object.assign(document.createElement("option"), {value:m, textContent: METRIC_LABELS[m] || m}));
});
metricSel.value = "revenue";

const yearSlider = document.getElementById("yearSlider");
const yearDisplay = document.getElementById("yearDisplay");
yearSlider.min = 0; yearSlider.max = ALL_YEARS.length - 1;
yearSlider.value = ALL_YEARS.length - 1; yearSlider.step = 1;
yearDisplay.textContent = ALL_YEARS[yearSlider.value];

const currencySel = document.getElementById("currencySelect");
const peopleFilter = document.getElementById("peopleFilter");

function updateFxFooter() {
  const parts = [];
  for (const [c, rate] of Object.entries(FX)) {
    if (c === "USD") continue;
    const src = FX_SOURCES[c] || "";
    const srcShort = src.includes("frankfurter") ? "frankfurter" : src.includes("er-api") ? "open.er-api" : "constant";
    parts.push(`1 USD = ${(1/rate).toFixed(2)} ${c} (${srcShort})`);
  }
  const dt = FX_FETCHED ? FX_FETCHED.slice(0, 10) : "?";
  document.getElementById("fxFooter").textContent = `FX (${dt}): ${parts.join("  ·  ")}`;
}
updateFxFooter();

function fmtVal(v, metric, currencyMode) {
  if (v == null) return "—";
  if (metric.endsWith("_pct")) return v.toFixed(1) + "%";
  if (metric === "employees") return Math.round(v).toLocaleString();
  if (metric === "eps" || metric === "dividend_per_share") return (currencyMode === "usd" ? "$" : "") + v.toFixed(2);
  if (Math.abs(v) >= 1e9) return (v/1e9).toFixed(2) + "B";
  if (Math.abs(v) >= 1e6) return (v/1e6).toFixed(1) + "M";
  if (Math.abs(v) >= 1e3) return (v/1e3).toFixed(1) + "K";
  return v.toFixed(0);
}
function getMetricValue(node, metric, year, currencyMode) {
  const m = node.metrics_canonical?.[metric];
  if (!m) return null;
  const v = m.values[year];
  if (!v) return null;
  return currencyMode === "usd" ? v.usd : v.native;
}
const CROSS = new Set(PEOPLE_NODES.filter(p => (p.linked_companies || []).length > 1).map(p => p.id));

function buildData() {
  const focus = companyFocus.value;
  const metric = metricSel.value;
  const year = ALL_YEARS[yearSlider.value];
  const currencyMode = currencySel.value;
  const pfilter = peopleFilter.value;
  const focusKey = focus === "_all" ? null : focus.replace(/^company_/, "");

  const nodes = [], edges = [];
  const scopeCompanies = focus === "_all" ? COMPANY_NODES : COMPANY_NODES.filter(c => c.id === focus);
  const refVals = COMPANY_NODES.map(c => Math.abs(getMetricValue(c, metric, year, currencyMode) || 0));
  const maxVal = Math.max(1, ...refVals);

  for (const c of scopeCompanies) {
    const v = getMetricValue(c, metric, year, currencyMode);
    let size2d = focus === "_all" ? 18 : 60;
    let size3d = focus === "_all" ? 6 : 14;
    if (v != null && maxVal > 0) {
      const ratio = Math.sqrt(Math.abs(v) / maxVal);
      size2d = (focus === "_all" ? 20 : 40) + ratio * (focus === "_all" ? 70 : 60);
      size3d = (focus === "_all" ? 4 : 8) + ratio * 14;
    }
    const tk = shortTicker(c.ticker);
    nodes.push({
      id: c.id,
      label: tk ? `${c.label}\\n(${tk})\\n${fmtVal(v, metric, currencyMode)}` : `${c.label}\\n${fmtVal(v, metric, currencyMode)}`,
      labelShort: tk ? `${c.label} (${tk})` : c.label,
      title: `${c.label}${tk?" — "+tk:""}\\n${METRIC_LABELS[metric]} (${year}): ${fmtVal(v, metric, currencyMode)} ${currencyMode==='usd'?'USD':c.currency_default}`,
      shape: "dot",
      color: { background: "#3b82f6", border: "#93c5fd" },
      _color3d: "#3b82f6",
      size: size2d,
      _val3d: size3d,
      font: { color: "#e5e7eb", size: 13, face: "system-ui", strokeWidth: 0 },
      borderWidth: 2,
      _kind: "company",
    });
  }

  for (const p of PEOPLE_NODES) {
    if (pfilter === "none") continue;
    const isCross = CROSS.has(p.id);
    if (pfilter === "directors" && !["board_director","independent_director","committee_member"].includes(p.person_type)) continue;
    if (pfilter === "executives" && !["executive_officer","senior_vp","vp"].includes(p.person_type)) continue;
    if (pfilter === "cross" && !isCross) continue;
    if (focusKey && !(p.linked_companies || []).includes(focusKey)) continue;

    const color = isCross ? "#ef4444" : (PERSON_COLORS[p.person_type] || "#6b7280");
    const isDirector = ["board_director","independent_director"].includes(p.person_type);
    nodes.push({
      id: p.id,
      label: p.label,
      labelShort: p.label,
      title: `${p.label} — ${p.primary_role}${isCross ? ' [also at: '+p.linked_companies.filter(k=>k!==p.primary_company).join(', ')+']' : ''}`,
      shape: isDirector ? "diamond" : (isCross ? "star" : "dot"),
      color: { background: color, border: isCross ? "#fee2e2" : "#1f2937" },
      _color3d: color,
      size: isCross ? 18 : (isDirector ? 14 : 10),
      _val3d: isCross ? 5 : (isDirector ? 3.5 : 2.5),
      font: { color: "#d1d5db", size: 10 },
      borderWidth: isCross ? 2 : 1,
      _kind: "person",
    });
  }

  const nodeIds = new Set(nodes.map(n => n.id));
  for (const e of GRAPH.links) {
    if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) continue;
    const isCross = CROSS.has(e.source);
    edges.push({
      from: e.source, to: e.target,
      source: e.source, target: e.target,
      label: e.relation,
      color: { color: isCross ? "#ef4444" : "#374151" },
      _color3d: isCross ? "#ef4444" : "#374151",
      font: { color: "#6b7280", size: 8, strokeWidth: 0, align: "top" },
      width: isCross ? 2 : (e.weight || 1),
      arrows: { to: { enabled: true, scaleFactor: 0.4 } },
      smooth: { type: "curvedCW", roundness: 0.1 },
    });
  }

  return { nodes, edges };
}

// ===== 2D renderer (vis-network) =====
let net2d = null;
function render2D() {
  const data = buildData();
  if (!net2d) {
    net2d = new vis.Network(document.getElementById("network-2d"), data, {
      physics: {
        barnesHut: { gravitationalConstant: -10000, springLength: 200, avoidOverlap: 0.4 },
        stabilization: { iterations: 200, fit: true },
      },
      interaction: { hover: true, tooltipDelay: 200, dragNodes: true },
    });
    net2d.on("click", params => handleClick(params.nodes[0]));
    net2d.once("stabilizationIterationsDone", () => net2d.setOptions({ physics: { enabled: false } }));
  } else {
    net2d.setOptions({ physics: { enabled: true, stabilization: { iterations: 80, fit: true } } });
    net2d.setData(data);
    net2d.once("stabilizationIterationsDone", () => net2d.setOptions({ physics: { enabled: false } }));
  }
}

// ===== 3D renderer (3d-force-graph) =====
let net3d = null;
function render3D() {
  const data = buildData();
  // Convert vis-network style to 3d-force-graph style
  const fgData = {
    nodes: data.nodes.map(n => ({
      id: n.id, label: n.label, labelShort: n.labelShort, title: n.title,
      color: n._color3d, val: n._val3d, _kind: n._kind,
    })),
    links: data.edges.map(e => ({
      source: e.source, target: e.target, color: e._color3d,
      width: e.width, label: e.label,
    })),
  };
  if (!net3d) {
    const el = document.getElementById("network-3d");
    net3d = ForceGraph3D({ controlType: "orbit" })(el)
      .backgroundColor("#0b1220")
      .nodeColor(n => n.color)
      .nodeVal(n => n.val)
      .nodeLabel(n => n.title)
      .nodeOpacity(0.95)
      .nodeResolution(12)
      .linkColor(l => l.color)
      .linkWidth(l => l.width || 1)
      .linkDirectionalArrowLength(2.5)
      .linkDirectionalArrowRelPos(1)
      .linkOpacity(0.5)
      .cooldownTicks(120)
      .onNodeClick(n => handleClick(n.id))
      .graphData(fgData);
    // Add text label sprites for company nodes (gracefully skip if SpriteText missing)
    if (typeof SpriteText !== "undefined") {
      net3d.nodeThreeObjectExtend(true);
      net3d.nodeThreeObject(n => {
        if (n._kind !== "company") return null;
        const sprite = new SpriteText(n.labelShort);
        sprite.material.depthWrite = false;
        sprite.color = "#e5e7eb";
        sprite.textHeight = 4;
        sprite.padding = 2;
        sprite.backgroundColor = "rgba(17,24,39,0.7)";
        return sprite;
      });
    }
  } else {
    net3d.graphData(fgData);
  }
}

// ===== shared click handler =====
function handleClick(nodeId) {
  const details = document.getElementById("details");
  if (!nodeId) {
    details.innerHTML = '<p class="empty">Click a node for source-linked details.</p>';
    return;
  }
  const node = GRAPH.nodes.find(n => n.id === nodeId);
  if (!node) return;
  const currencyMode = currencySel.value;

  let html = `<h2>${node.label}</h2>`;
  if (node.type === "company") {
    const tk = shortTicker(node.ticker);
    if (tk) html += `<div class="kv"><span class="k">Ticker</span> <span class="v">${node.ticker}</span></div>`;
    html += `<div class="kv"><span class="k">Country</span> <span class="v">${node.country}</span></div>`;
    html += `<div class="kv"><span class="k">Industry</span> <span class="v">${node.industry || '—'}</span></div>`;
    html += `<div class="kv"><span class="k">Currency</span> <span class="v">${node.currency_default || 'TWD'}</span></div>`;
    html += `<div class="kv"><span class="k">Fiscal year end</span> <span class="v">${node.fiscal_year_end || '—'}</span></div>`;

    const linkedPeople = PEOPLE_NODES.filter(p => (p.linked_companies||[]).includes(node.norm_label));
    html += `<div class="kv" style="margin-top:8px"><span class="k">Linked people</span> <span class="v">${linkedPeople.length} (${linkedPeople.filter(p=>p.person_type==='board_director'||p.person_type==='independent_director').length} board / ${linkedPeople.filter(p=>['executive_officer','senior_vp','vp'].includes(p.person_type)).length} exec)</span></div>`;

    const canonical = node.metrics_canonical || {};
    if (Object.keys(canonical).length > 0) {
      html += `<h2 style="margin-top:12px">Canonical metrics (cross-comparable)</h2>`;
      for (const [name, m] of Object.entries(canonical)) {
        html += `<div class="metric-block"><div class="title">${METRIC_LABELS[name] || name}</div>`;
        for (const [y, v] of Object.entries(m.values).sort()) {
          const val = currencyMode === "usd" ? v.usd : v.native;
          const cur = currencyMode === "usd" ? "USD" : v.currency;
          html += `<div class="metric-row"><span class="name">${y} <span class="badge" style="font-size:8px">${v.source_page}</span></span><span class="val">${fmtVal(val, name, currencyMode)} ${cur}</span></div>`;
        }
        html += `</div>`;
      }
    }

    const native = node.metrics_native || {};
    if (Object.keys(native).length > 0) {
      html += `<details><summary>All native-label metrics (${Object.keys(native).length})</summary>`;
      for (const [name, info] of Object.entries(native)) {
        const ys = Object.keys(info.values).sort();
        if (ys.length === 0) continue;
        html += `<div class="metric-block"><div class="title" style="color:#9ca3af;font-size:10px">${name}</div>`;
        for (const y of ys) html += `<div class="metric-row"><span class="name">${y}</span><span class="val">${info.values[y].toLocaleString()} ${info.unit||''}</span></div>`;
        html += `</div>`;
      }
      html += `</details>`;
    }
  } else {
    const isCross = CROSS.has(node.id);
    if (isCross) html += `<div class="kv"><span class="badge badge-warn">CROSS-COMPANY</span></div>`;
    html += `<div class="kv"><span class="k">Role</span> <span class="v">${node.primary_role || '—'}</span></div>`;
    html += `<div class="kv"><span class="k">Type</span> <span class="v"><span class="badge">${node.person_type}</span></span></div>`;
    html += `<div class="kv"><span class="k">Companies</span> <span class="v">${(node.linked_companies||[]).join(', ')}</span></div>`;
    if (node.tenure_start) html += `<div class="kv"><span class="k">Since</span> <span class="v">${node.tenure_start}</span></div>`;
    if (node.education) html += `<div class="kv"><span class="k">Education</span> <span class="v">${node.education}</span></div>`;
    if (node.concurrent_roles && node.concurrent_roles.length > 0)
      html += `<div class="kv"><span class="k">Concurrent roles</span> <span class="v">${node.concurrent_roles.join('; ')}</span></div>`;
  }
  details.innerHTML = html;
}

// ===== view toggle =====
let activeView = "2d";
const btn2d = document.getElementById("btn2d");
const btn3d = document.getElementById("btn3d");
function setView(v) {
  activeView = v;
  document.body.classList.toggle("is-3d", v === "3d");
  btn2d.classList.toggle("active", v === "2d");
  btn3d.classList.toggle("active", v === "3d");
  render();
}
btn2d.addEventListener("click", () => setView("2d"));
btn3d.addEventListener("click", () => setView("3d"));

function render() {
  if (activeView === "2d") render2D(); else render3D();
}

// SpriteText is now loaded via static <script> tag at top (after THREE).
// Reference window.SpriteText if available, else 3D mode runs without text labels.
const SpriteText = window.SpriteText;

// ===== View aids (3D only) =====
// Blender-style infinite axes + grid floor
let axesObjects = [];
function setAxes(on) {
  if (!net3d) return;
  const scene = net3d.scene();
  if (on && axesObjects.length === 0) {
    const axisLength = 5000;
    const axisDefs = [
      { dir: [1,0,0], hex: 0xff5555, name: "+X" },
      { dir: [0,1,0], hex: 0x66dd55, name: "+Y" },
      { dir: [0,0,1], hex: 0x4d99ff, name: "+Z" },
    ];
    for (const a of axisDefs) {
      const v = new THREE.Vector3(a.dir[0], a.dir[1], a.dir[2]);
      const points = [v.clone().multiplyScalar(-axisLength), v.clone().multiplyScalar(axisLength)];
      const geom = new THREE.BufferGeometry().setFromPoints(points);
      const mat = new THREE.LineBasicMaterial({ color: a.hex, transparent: true, opacity: 0.55, fog: true });
      const line = new THREE.Line(geom, mat);
      scene.add(line); axesObjects.push(line);
      if (typeof SpriteText !== "undefined") {
        const s = new SpriteText(a.name);
        s.color = "#" + a.hex.toString(16).padStart(6, "0");
        s.textHeight = 4; s.padding = 2;
        s.backgroundColor = "rgba(11,18,32,0.7)";
        s.position.copy(v.clone().multiplyScalar(60));
        scene.add(s); axesObjects.push(s);
      }
    }
    const grid = new THREE.GridHelper(600, 60, 0x666666, 0x2a2a3a);
    grid.material.transparent = true;
    grid.material.opacity = 0.35;
    grid.material.fog = true;
    scene.add(grid); axesObjects.push(grid);
  } else if (!on) {
    for (const o of axesObjects) {
      scene.remove(o);
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        if (Array.isArray(o.material)) o.material.forEach(m => m.dispose());
        else o.material.dispose();
      }
    }
    axesObjects = [];
  }
}
// Linear fog. Three.js bakes fog support into shader at compile time, so
// toggling scene.fog alone doesn't update already-rendered materials —
// we have to flip material.fog and force needsUpdate on every material.
function setFog(on) {
  if (!net3d) return;
  const scene = net3d.scene();
  scene.fog = on ? new THREE.Fog(0x0b1220, 30, 250) : null;
  scene.traverse(obj => {
    if (!obj.material) return;
    const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
    for (const m of mats) {
      m.fog = !!on;
      m.needsUpdate = true;
    }
  });
}
function setAutoRotate(on) {
  if (!net3d) return;
  const c = net3d.controls();
  if (c) { c.autoRotate = on; c.autoRotateSpeed = 1.2; }
}
function homeView() {
  if (net3d) net3d.zoomToFit(900, 50);
}
document.getElementById("aidAxes").addEventListener("change", e => setAxes(e.target.checked));
document.getElementById("aidFog").addEventListener("change", e => setFog(e.target.checked));
document.getElementById("aidRotate").addEventListener("change", e => setAutoRotate(e.target.checked));
document.getElementById("aidHome").addEventListener("click", homeView);

// ===== Fusion-style ViewCube via three-viewport-gizmo =====
let viewCube = null;
function initViewCube() {
  if (viewCube || !net3d || !window.ThreeViewportGizmo) return;
  const { ViewportGizmo } = window.ThreeViewportGizmo;
  viewCube = new ViewportGizmo(net3d.camera(), net3d.renderer(), {
    type: "cube",
    size: 128,
    placement: "top-right",
    offset: { top: 12, right: 12, left: 0, bottom: 0 },
    container: document.querySelector(".canvas-wrap"),
    background: { enabled: true, color: 0x111827, opacity: 0.55, hover: { color: 0x1e3a8a, opacity: 0.85 } },
    font: { family: "system-ui, sans-serif", weight: 600 },
  });
  if (viewCube.domElement && viewCube.domElement.classList) viewCube.domElement.classList.add("tvg-container");
  viewCube.target = net3d.controls().target;
  if (typeof viewCube.attachControls === "function") {
    viewCube.attachControls(net3d.controls());
  } else {
    net3d.controls().addEventListener("change", () => viewCube.update());
    viewCube.addEventListener("change", () => net3d.controls().update());
  }
  (function tick() {
    if (viewCube && document.body.classList.contains("is-3d")) viewCube.render();
    requestAnimationFrame(tick);
  })();
}

companyFocus.addEventListener("change", render);
metricSel.addEventListener("change", render);
yearSlider.addEventListener("input", () => { yearDisplay.textContent = ALL_YEARS[yearSlider.value]; render(); });
currencySel.addEventListener("change", render);
peopleFilter.addEventListener("change", render);

render();
// Init the ViewCube once the 3D renderer exists
setTimeout(initViewCube, 100);
</script>
</body>
</html>
"""

n_company = sum(1 for n in graph["nodes"] if n.get("type") == "company")
n_person = sum(1 for n in graph["nodes"] if n.get("type") == "person")
n_edge = len(graph.get("links") or graph.get("edges") or [])
meta = f"{n_company} companies · {n_person} unique people · {n_edge} edges"

html = HTML.replace("__GRAPH__", graph_js).replace("__META__", meta)
out = ROOT / "graphify-financial" / "graph-financial.html"
out.write_text(html, encoding="utf-8")
print(f"Wrote {out}  ({len(html):,} bytes)  ({meta})")
