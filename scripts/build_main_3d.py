#!/usr/bin/env python3.12
"""Generate graphify-out/graph-3d.html — 2D/3D viewer for the main 1,512-node graph.

Sibling to the existing graph.html (which stays untouched).
- 2D: vis-network
- 3D: 3d-force-graph (Three.js / WebGL)
- Color by community, size by degree
- Filters: node type, community
- Search box + sidebar with details
"""
import json
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
graph = json.loads((ROOT / "graphify-out/graph.json").read_text())

# Compute degree per node (used for sizing)
deg = {}
for e in graph.get("links", []):
    deg[e["source"]] = deg.get(e["source"], 0) + 1
    deg[e["target"]] = deg.get(e["target"], 0) + 1

# Pre-compute degree on each node (for faster JS)
for n in graph["nodes"]:
    n["_degree"] = deg.get(n["id"], 0)

graph_js = json.dumps(graph, ensure_ascii=False, default=str).replace("</", "<\\/")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SEAJ TSIA — Main Knowledge Graph (2D/3D)</title>
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<!-- THREE first; three-spritetext UMD looks for window.three (lowercase),
     not window.THREE (uppercase) that three.min.js exposes — so alias it.
     three-viewport-gizmo also reads window.THREE. -->
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
  .controls { display: flex; gap: 12px; align-items: end; margin-left: auto; flex-wrap: wrap; }
  .control { display: flex; flex-direction: column; gap: 3px; }
  .control label { font-size: 10px; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.05em; }
  .control select, .control input { background: #1f2937; color: #e5e7eb; border: 1px solid #374151; padding: 5px 8px; border-radius: 4px; font-size: 12px; min-width: 140px; }
  main { flex: 1; display: flex; min-height: 0; position: relative; }
  .canvas-wrap { flex: 1; position: relative; background: #0b1220; }
  #network-2d, #network-3d { position: absolute; inset: 0; }
  #network-3d { display: none; }
  body.is-3d #network-2d { display: none; }
  body.is-3d #network-3d { display: block; }
  aside { width: 320px; background: #111827; border-left: 1px solid #1f2937; padding: 14px; overflow-y: auto; font-size: 12px; }
  aside h2 { font-size: 13px; color: #93c5fd; margin-bottom: 6px; padding-bottom: 4px; border-bottom: 1px solid #1f2937; }
  aside .empty { color: #6b7280; font-style: italic; }
  .badge { display: inline-block; background: #1e3a8a; color: #bfdbfe; padding: 1px 6px; border-radius: 8px; font-size: 9px; margin-right: 3px; }
  .kv { margin-bottom: 4px; }
  .kv .k { color: #9ca3af; font-size: 10px; text-transform: uppercase; }
  .kv .v { color: #e5e7eb; word-break: break-word; }
  .neighbor { padding: 4px 6px; margin: 3px 0; border-left: 2px solid #374151; cursor: pointer; font-size: 11px; }
  .neighbor:hover { background: #1f2937; border-left-color: #60a5fa; }
  .neighbor .n-label { color: #e5e7eb; }
  .neighbor .n-rel { color: #6b7280; font-size: 10px; }
  footer { padding: 6px 16px; background: #111827; border-top: 1px solid #1f2937; font-size: 10px; color: #6b7280; display: flex; gap: 12px; }
  #search { background: #1f2937; color: #e5e7eb; border: 1px solid #374151; padding: 6px 10px; border-radius: 4px; font-size: 12px; min-width: 200px; outline: none; }
  #search:focus { border-color: #3b82f6; }
  #search-results { position: absolute; top: 100%; left: 0; right: 0; background: #111827; border: 1px solid #374151; max-height: 300px; overflow-y: auto; z-index: 100; display: none; border-radius: 4px; margin-top: 4px; }
  #search-results.show { display: block; }
  .search-item { padding: 6px 10px; cursor: pointer; font-size: 12px; border-bottom: 1px solid #1f2937; }
  .search-item:hover { background: #1e3a8a; }
  .search-item .type { color: #6b7280; font-size: 10px; margin-left: 6px; }
  .search-wrap { position: relative; }
  .aids-panel { position: absolute; top: 12px; left: 12px; background: rgba(17,24,39,0.88); border: 1px solid #1f2937; border-radius: 6px; padding: 8px 10px; font-size: 11px; z-index: 10; display: none; backdrop-filter: blur(4px); pointer-events: auto; }
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
    <h1>SEAJ TSIA — Main Knowledge Graph</h1>
    <div class="meta">1,512 nodes · 1,848 edges · 174 communities · sibling to graph.html</div>
  </div>
  <div class="view-toggle">
    <button id="btn2d">2D</button>
    <button id="btn3d" class="active">3D</button>
  </div>
  <div class="controls">
    <div class="control search-wrap">
      <label>Search</label>
      <input id="search" type="text" placeholder="Search nodes…">
      <div id="search-results"></div>
    </div>
    <div class="control">
      <label>Type filter</label>
      <select id="typeFilter"></select>
    </div>
    <div class="control">
      <label>Min degree</label>
      <select id="degreeFilter">
        <option value="0">All (1,512)</option>
        <option value="2">≥2 connections</option>
        <option value="3">≥3 connections</option>
        <option value="5">≥5 connections</option>
        <option value="10">≥10 connections</option>
      </select>
    </div>
    <div class="control">
      <label>Color by</label>
      <select id="colorMode">
        <option value="community">Community (174)</option>
        <option value="type">Node type</option>
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
        <button class="aid-btn primary" id="aidHome" title="Reset / fit all nodes in view">⌂ Home / Fit</button>
        <span style="color:#6b7280;font-size:10px;margin-left:6px">Top/Front/Side/Iso → use the cube ↗</span>
      </div>
    </div>
  </div>
  <aside>
    <h2>Details</h2>
    <div id="details"><p class="empty">Click any node, or use search. 3D mode: drag to rotate, scroll to zoom.</p></div>
  </aside>
</main>
<footer>
  <span><strong>Legend:</strong></span>
  <span style="color:#3b82f6">company</span>
  <span style="color:#10b981">product</span>
  <span style="color:#f59e0b">technology</span>
  <span style="color:#a78bfa">paper</span>
  <span style="color:#ef4444">person</span>
  <span style="margin-left:auto">Drag nodes to reposition. Click for details.</span>
</footer>
<script>
const GRAPH = __GRAPH__;
const NODES = GRAPH.nodes;
const LINKS = GRAPH.links;

// Build adjacency for sidebar neighbor lists
const ADJ = new Map();
for (const e of LINKS) {
  if (!ADJ.has(e.source)) ADJ.set(e.source, []);
  if (!ADJ.has(e.target)) ADJ.set(e.target, []);
  ADJ.get(e.source).push({other: e.target, rel: e.relation, dir: "out"});
  ADJ.get(e.target).push({other: e.source, rel: e.relation, dir: "in"});
}

// Community color: golden-angle hue spread for 174 distinct colors
function communityColor(c) {
  if (c == null || c < 0) return "#6b7280";
  const hue = (c * 137.508) % 360;
  return `hsl(${hue.toFixed(0)}, 65%, 60%)`;
}

// Type colors (for the "Color by type" mode)
const TYPE_COLORS = {
  company: "#3b82f6", product: "#10b981", technology: "#f59e0b",
  paper: "#a78bfa", document: "#a78bfa", person: "#ef4444",
  application: "#06b6d4", industry: "#84cc16", process_step: "#ec4899",
  business_segment: "#f43f5e", competitor: "#f87171", equipment: "#22d3ee",
  market: "#fbbf24", product_category: "#34d399", organization: "#60a5fa",
  material: "#fcd34d", subsidiary: "#818cf8", code: "#9ca3af",
};
function typeColor(t) { return TYPE_COLORS[t] || "#6b7280"; }

// Pre-collect node types for filter
const TYPES_PRESENT = [...new Set(NODES.map(n => n.type || n.file_type || "unknown"))].sort();

const typeFilter = document.getElementById("typeFilter");
typeFilter.appendChild(Object.assign(document.createElement("option"), {value: "_all", textContent: "All types"}));
TYPES_PRESENT.forEach(t => {
  const c = NODES.filter(n => (n.type || n.file_type) === t).length;
  typeFilter.appendChild(Object.assign(document.createElement("option"), {value: t, textContent: `${t} (${c})`}));
});
typeFilter.value = "_all";

const degreeFilter = document.getElementById("degreeFilter");
const colorMode = document.getElementById("colorMode");

// Search
const searchInput = document.getElementById("search");
const searchResults = document.getElementById("search-results");
searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q || q.length < 2) { searchResults.classList.remove("show"); return; }
  const matches = NODES.filter(n => (n.label || n.norm_label || "").toLowerCase().includes(q)).slice(0, 30);
  searchResults.innerHTML = matches.map(n =>
    `<div class="search-item" data-id="${n.id}">${n.label}<span class="type">${n.type || n.file_type || ""}</span></div>`
  ).join("");
  searchResults.classList.toggle("show", matches.length > 0);
});
searchResults.addEventListener("click", e => {
  const item = e.target.closest(".search-item");
  if (!item) return;
  const id = item.dataset.id;
  searchResults.classList.remove("show");
  searchInput.value = "";
  handleClick(id);
  focusNode(id);
});
document.addEventListener("click", e => {
  if (!e.target.closest(".search-wrap")) searchResults.classList.remove("show");
});

function buildData() {
  const tFilter = typeFilter.value;
  const dFilter = parseInt(degreeFilter.value);
  const cMode = colorMode.value;

  const visibleNodes = NODES.filter(n => {
    if (n._degree < dFilter) return false;
    if (tFilter !== "_all" && (n.type || n.file_type) !== tFilter) return false;
    return true;
  });
  const visibleIds = new Set(visibleNodes.map(n => n.id));

  const nodes = visibleNodes.map(n => {
    const color = cMode === "type" ? typeColor(n.type || n.file_type) : communityColor(n.community);
    const size2d = 6 + Math.sqrt(n._degree) * 3;
    const size3d = 1 + Math.sqrt(n._degree) * 1.4;
    return {
      id: n.id,
      label: n.label || n.norm_label,
      title: `${n.label || n.norm_label}\\n${n.type || n.file_type || ''}\\ncommunity ${n.community} · degree ${n._degree}`,
      color: { background: color, border: "#1f2937" },
      _color3d: color,
      size: size2d,
      _val3d: size3d,
      font: { color: "#d1d5db", size: 9 },
      borderWidth: 1,
      shape: "dot",
      _degree: n._degree,
      _kind: n.type || n.file_type,
    };
  });

  const edges = LINKS
    .filter(e => visibleIds.has(e.source) && visibleIds.has(e.target))
    .map(e => ({
      from: e.source, to: e.target,
      source: e.source, target: e.target,
      label: e.relation,
      color: { color: "#374151", opacity: 0.5 },
      _color3d: "rgba(120,120,140,0.35)",
      width: 0.8, font: { color: "#6b7280", size: 7, strokeWidth: 0 },
      arrows: { to: { enabled: true, scaleFactor: 0.3 } },
      smooth: { type: "continuous" },
    }));

  return { nodes, edges };
}

// ===== 2D renderer (vis-network) =====
let net2d = null;
function render2D() {
  const data = buildData();
  if (!net2d) {
    net2d = new vis.Network(document.getElementById("network-2d"), data, {
      physics: {
        barnesHut: { gravitationalConstant: -3000, springLength: 100, avoidOverlap: 0.2 },
        stabilization: { iterations: 300, fit: true },
      },
      interaction: { hover: true, dragNodes: true, tooltipDelay: 200 },
    });
    net2d.on("click", params => handleClick(params.nodes[0]));
    net2d.once("stabilizationIterationsDone", () => net2d.setOptions({ physics: { enabled: false } }));
  } else {
    net2d.setOptions({ physics: { enabled: true, stabilization: { iterations: 100, fit: true } } });
    net2d.setData(data);
    net2d.once("stabilizationIterationsDone", () => net2d.setOptions({ physics: { enabled: false } }));
  }
}

// ===== 3D renderer (3d-force-graph) =====
let net3d = null;
function render3D() {
  const data = buildData();
  const fgData = {
    nodes: data.nodes.map(n => ({
      id: n.id, label: n.label, title: n.title,
      color: n._color3d, val: n._val3d, _kind: n._kind, _degree: n._degree,
    })),
    links: data.edges.map(e => ({ source: e.source, target: e.target, color: e._color3d })),
  };
  if (!net3d) {
    net3d = ForceGraph3D({ controlType: "orbit" })(document.getElementById("network-3d"))
      .backgroundColor("#0b1220")
      .nodeColor(n => n.color)
      .nodeVal(n => n.val)
      .nodeLabel(n => n.title)
      .nodeOpacity(0.9)
      .nodeResolution(8)
      .linkColor(l => l.color)
      .linkOpacity(0.4)
      .linkWidth(0.5)
      .cooldownTicks(150)
      .onNodeClick(n => { handleClick(n.id); focusNode(n.id); })
      .graphData(fgData);
    // Show text labels only on high-degree nodes (degree >= 5) to avoid clutter.
    // Gracefully skip if SpriteText didn't load.
    if (typeof SpriteText !== "undefined") {
      net3d.nodeThreeObjectExtend(true);
      net3d.nodeThreeObject(n => {
        if (n._degree < 5) return null;
        const sprite = new SpriteText(n.label);
        sprite.material.depthWrite = false;
        sprite.color = "#e5e7eb";
        sprite.textHeight = 2 + Math.sqrt(n._degree) * 0.4;
        sprite.padding = 1;
        sprite.backgroundColor = "rgba(11,18,32,0.6)";
        return sprite;
      });
    } else {
      console.warn("SpriteText not loaded; 3D labels disabled (hover for tooltip).");
    }
  } else {
    net3d.graphData(fgData);
  }
}

function focusNode(id) {
  if (activeView === "3d" && net3d) {
    const node = net3d.graphData().nodes.find(n => n.id === id);
    if (node && node.x != null) {
      const distance = 80;
      const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
      net3d.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
        node, 1500
      );
    }
  } else if (activeView === "2d" && net2d) {
    net2d.focus(id, { scale: 1.2, animation: { duration: 800, easingFunction: "easeInOutCubic" } });
  }
}

function handleClick(nodeId) {
  const details = document.getElementById("details");
  if (!nodeId) {
    details.innerHTML = '<p class="empty">Click a node, or use search.</p>';
    return;
  }
  const node = NODES.find(n => n.id === nodeId);
  if (!node) return;

  let html = `<h2>${node.label || node.norm_label}</h2>`;
  html += `<div class="kv"><span class="k">Type</span> <span class="v"><span class="badge">${node.type || node.file_type || '—'}</span></span></div>`;
  html += `<div class="kv"><span class="k">Community</span> <span class="v">${node.community ?? '—'}</span></div>`;
  html += `<div class="kv"><span class="k">Degree</span> <span class="v">${node._degree}</span></div>`;
  if (node.country) html += `<div class="kv"><span class="k">Country</span> <span class="v">${node.country}</span></div>`;
  if (node.industry) html += `<div class="kv"><span class="k">Industry</span> <span class="v">${node.industry}</span></div>`;
  if (node.ticker) html += `<div class="kv"><span class="k">Ticker</span> <span class="v">${node.ticker}</span></div>`;
  if (node.description) html += `<div class="kv"><span class="k">Description</span> <span class="v">${node.description}</span></div>`;
  if (node.source_file) html += `<div class="kv"><span class="k">Source</span> <span class="v">${node.source_file}${node.source_location?' '+node.source_location:''}</span></div>`;
  if (node.confidence_score != null) html += `<div class="kv"><span class="k">Confidence</span> <span class="v">${node.confidence_score}</span></div>`;
  if (node.attributes) {
    html += `<div class="kv"><span class="k">Attributes</span> <span class="v">${typeof node.attributes === 'object' ? JSON.stringify(node.attributes).slice(0, 200) : node.attributes}</span></div>`;
  }

  // Neighbors
  const adj = ADJ.get(nodeId) || [];
  if (adj.length) {
    html += `<h2 style="margin-top:14px">Neighbors (${adj.length})</h2>`;
    for (const a of adj.slice(0, 30)) {
      const o = NODES.find(n => n.id === a.other);
      if (!o) continue;
      const arrow = a.dir === "out" ? "→" : "←";
      html += `<div class="neighbor" data-id="${o.id}"><div class="n-label">${arrow} ${o.label || o.norm_label}</div><div class="n-rel">${a.rel || ""}</div></div>`;
    }
    if (adj.length > 30) html += `<div style="color:#6b7280;font-size:11px;margin-top:6px">…and ${adj.length-30} more</div>`;
  }
  details.innerHTML = html;
  // Wire up neighbor clicks
  details.querySelectorAll(".neighbor").forEach(el => {
    el.addEventListener("click", () => { handleClick(el.dataset.id); focusNode(el.dataset.id); });
  });
}

// ===== view toggle =====
let activeView = "3d";
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

typeFilter.addEventListener("change", render);
degreeFilter.addEventListener("change", render);
colorMode.addEventListener("change", render);

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
        s.textHeight = 6; s.padding = 2;
        s.backgroundColor = "rgba(11,18,32,0.7)";
        s.position.copy(v.clone().multiplyScalar(120));
        scene.add(s); axesObjects.push(s);
      }
    }
    // Blender-style grid floor on XZ plane
    const grid = new THREE.GridHelper(2000, 100, 0x666666, 0x2a2a3a);
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
  scene.fog = on ? new THREE.Fog(0x0b1220, 80, 600) : null;
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
  if (net3d) net3d.zoomToFit(900, 60);
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
  // Render loop for the cube (3d-force-graph manages its own render loop, but the
  // gizmo needs its own render() call each frame).
  (function tick() {
    if (viewCube && document.body.classList.contains("is-3d")) viewCube.render();
    requestAnimationFrame(tick);
  })();
}

// Default to 3D on first load (it's the headline feature)
document.body.classList.add("is-3d");
render();
// Init the ViewCube once the 3D renderer exists (after first render3D call)
setTimeout(initViewCube, 100);
</script>
</body>
</html>
"""

html = HTML.replace("__GRAPH__", graph_js)
out = ROOT / "graphify-out" / "graph-3d.html"
out.write_text(html, encoding="utf-8")
print(f"Wrote {out}  ({len(html):,} bytes)")
print(f"Nodes: {len(graph['nodes'])}, Links: {len(graph['links'])}")
