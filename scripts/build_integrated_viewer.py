#!/usr/bin/env python3.12
"""Build graphify-financial/graph-integrated.html — a unified per-company viewer.

For each financial company, joins:
  - financial_metrics (canonical, multi-year, local-currency + USD)
  - entities + relationships from the main graph (community, products, suppliers, etc.)
  - person_affiliations (cross-board people)

Output is a single self-contained HTML page (~1–3 MB) with embedded JSON.
"""
from __future__ import annotations
import json, sqlite3
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
DB_PATH = ROOT / "graphify-financial" / "financials.db"
OUT = ROOT / "graphify-financial" / "graph-integrated.html"


def build_company_dossier(conn: sqlite3.Connection, company_id: str) -> dict:
    """Return everything we know about a single company, joined across both layers."""
    c = conn.execute("SELECT * FROM companies WHERE company_id=?", (company_id,)).fetchone()
    if not c:
        return {}
    d = {"company_id": c["company_id"], "label": c["label"],
         "country": c["country"], "industry": c["industry"],
         "ticker": c["ticker"], "currency_default": c["currency_default"],
         "fiscal_year_end": c["fiscal_year_end"], "source_pdf": c["source_pdf"]}

    # Canonical financial metrics by year (FY actuals, exclude forecasts)
    rows = conn.execute("""
        SELECT canonical_name, year, value_native, value_usd, currency, period
        FROM financial_metrics
        WHERE company_id=? AND canonical_name IS NOT NULL AND is_forecast=0
          AND period IN ('FY','FY3')
        ORDER BY canonical_name, year
    """, (company_id,)).fetchall()
    metrics: dict[str, dict[str, dict]] = {}
    for r in rows:
        metrics.setdefault(r["canonical_name"], {})[r["year"]] = {
            "native": r["value_native"], "usd": r["value_usd"],
            "currency": r["currency"], "period": r["period"],
        }
    d["metrics"] = metrics

    # Main-graph entity link
    e = conn.execute(
        "SELECT * FROM entities WHERE financial_company_id=? LIMIT 1",
        (company_id,),
    ).fetchone()
    if e:
        d["graph_entity_id"] = e["entity_id"]
        d["graph_label"] = e["label"]
        d["community"] = e["community"]
        d["graph_description"] = e["description"]
        # Outgoing relationships (this company → other entities)
        out_rels = conn.execute("""
            SELECT r.relation, e2.label, e2.entity_type
            FROM relationships r
            JOIN entities e2 ON e2.entity_id = r.target_entity
            WHERE r.source_entity = ?
            ORDER BY r.relation, e2.label
            LIMIT 50
        """, (e["entity_id"],)).fetchall()
        d["outgoing_edges"] = [
            {"relation": r["relation"], "target": r["label"], "type": r["entity_type"]}
            for r in out_rels
        ]
        # Incoming relationships (other entities → this company)
        in_rels = conn.execute("""
            SELECT r.relation, e2.label, e2.entity_type
            FROM relationships r
            JOIN entities e2 ON e2.entity_id = r.source_entity
            WHERE r.target_entity = ?
            ORDER BY r.relation, e2.label
            LIMIT 50
        """, (e["entity_id"],)).fetchall()
        d["incoming_edges"] = [
            {"relation": r["relation"], "source": r["label"], "type": r["entity_type"]}
            for r in in_rels
        ]
    else:
        d["graph_entity_id"] = None
        d["outgoing_edges"] = []
        d["incoming_edges"] = []

    # People + cross-board flags
    ppl = conn.execute("""
        SELECT p.person_id, p.name, pa.role, pa.affiliation_type,
               (SELECT COUNT(DISTINCT pa2.company_id) FROM person_affiliations pa2
                WHERE pa2.person_id = p.person_id) AS n_affiliations
        FROM person_affiliations pa
        JOIN people p ON p.person_id = pa.person_id
        WHERE pa.company_id = ?
        ORDER BY n_affiliations DESC, p.name
    """, (company_id,)).fetchall()
    d["people"] = [
        {"name": r["name"], "role": r["role"],
         "type": r["affiliation_type"], "n_affiliations": r["n_affiliations"]}
        for r in ppl
    ]

    return d


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Build dossiers for every company
    companies = sorted([r["company_id"] for r in
                        conn.execute("SELECT company_id FROM companies")])
    dossiers = {cid: build_company_dossier(conn, cid) for cid in companies}

    # FX rates for unit conversion in the UI
    fx = {r["currency"]: r["rate_to_usd"] for r in
          conn.execute("SELECT currency, rate_to_usd FROM fx_rates")}

    # Communities lookup
    comms = {r["community_id"]: {"n_members": r["n_members"],
                                 "sample_labels": r["sample_labels"]}
             for r in conn.execute("SELECT * FROM communities")}

    payload = {
        "generated_at": "2026-04-25",
        "n_companies": len(dossiers),
        "n_linked": sum(1 for d in dossiers.values() if d.get("graph_entity_id")),
        "fx_to_usd": fx,
        "communities": comms,
        "companies": dossiers,
    }
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SEAJ TSIA — Integrated Company Explorer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #0b1220; color: #e5e7eb; min-height: 100vh; }
  header { padding: 14px 22px; background: #111827; border-bottom: 1px solid #1f2937; }
  header h1 { font-size: 17px; color: #93c5fd; font-weight: 600; }
  header .meta { font-size: 11px; color: #6b7280; margin-top: 4px; }
  main { display: grid; grid-template-columns: 280px 1fr; min-height: calc(100vh - 56px); }
  aside.list { background: #0f172a; border-right: 1px solid #1f2937; overflow-y: auto; max-height: calc(100vh - 56px); }
  aside.list .filter { padding: 12px; border-bottom: 1px solid #1f2937; position: sticky; top: 0; background: #0f172a; }
  aside.list input[type="text"] { width: 100%; background: #1f2937; color: #e5e7eb; border: 1px solid #374151; padding: 6px 9px; border-radius: 4px; font-size: 12px; }
  aside.list .item { padding: 9px 14px; border-bottom: 1px solid #111827; cursor: pointer; font-size: 12px; color: #d1d5db; }
  aside.list .item:hover { background: #1e293b; }
  aside.list .item.active { background: #1e3a8a; color: #dbeafe; }
  aside.list .item .country { font-size: 9px; color: #6b7280; text-transform: uppercase; margin-top: 2px; letter-spacing: 0.04em; }
  aside.list .item.unlinked .label { color: #9ca3af; }
  aside.list .item.unlinked::before { content: "•"; color: #f59e0b; margin-right: 4px; }
  section.detail { padding: 22px 30px; overflow-y: auto; max-height: calc(100vh - 56px); }
  section.detail .empty { color: #6b7280; font-style: italic; }
  section.detail h2 { color: #93c5fd; font-size: 22px; margin-bottom: 4px; }
  section.detail h3 { color: #93c5fd; font-size: 13px; margin: 24px 0 8px; padding-bottom: 4px; border-bottom: 1px solid #1f2937; text-transform: uppercase; letter-spacing: 0.06em; }
  section.detail .sub { color: #9ca3af; font-size: 12px; margin-bottom: 8px; }
  .badge { display: inline-block; background: #1e3a8a; color: #bfdbfe; padding: 1px 7px; border-radius: 8px; font-size: 10px; margin-right: 4px; }
  .badge-warn { background: #7c2d12; color: #fed7aa; }
  .badge-ok { background: #064e3b; color: #d1fae5; }
  table.metrics { width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 6px; }
  table.metrics th, table.metrics td { padding: 4px 8px; text-align: right; border-bottom: 1px solid #1f2937; font-variant-numeric: tabular-nums; }
  table.metrics th { color: #9ca3af; font-weight: 500; text-transform: uppercase; font-size: 9px; letter-spacing: 0.05em; }
  table.metrics td:first-child, table.metrics th:first-child { text-align: left; color: #93c5fd; }
  .grid-cols-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
  .edge-row { font-size: 11px; padding: 3px 0; color: #d1d5db; }
  .edge-row .relation { color: #93c5fd; font-weight: 500; }
  .edge-row .ent-type { color: #6b7280; font-size: 9px; margin-left: 4px; }
  .person-row { font-size: 11px; padding: 3px 0; color: #d1d5db; }
  .person-row .role { color: #9ca3af; font-size: 10px; }
  .cross-board { color: #fbbf24; font-weight: 500; }
  .kvgrid { display: grid; grid-template-columns: 110px 1fr; gap: 4px 12px; font-size: 12px; }
  .kvgrid .k { color: #9ca3af; font-size: 10px; text-transform: uppercase; }
  .kvgrid .v { color: #e5e7eb; }
  footer { padding: 6px 22px; background: #111827; border-top: 1px solid #1f2937; color: #6b7280; font-size: 10px; }
</style>
</head>
<body>
<header>
  <h1>SEAJ TSIA — Integrated Company Explorer</h1>
  <div class="meta" id="meta">…</div>
</header>
<main>
  <aside class="list">
    <div class="filter"><input id="filter" type="text" placeholder="Filter companies…"></div>
    <div id="list"></div>
  </aside>
  <section class="detail">
    <div id="detail" class="empty">Select a company on the left to see its integrated profile.</div>
  </section>
</main>
<footer>Local-currency + USD financials joined with main-graph community + relationships. <span id="footer-stats"></span></footer>
<script>
const DATA = __DATA__;
const fmtNum = (n, d=0) => n == null ? "—" : (d>0 ? n.toFixed(d) : Math.round(n).toLocaleString());
const fmtMillions = (n, currency) => {
  if (n == null) return "—";
  if (Math.abs(n) >= 1e9) return (n/1e9).toFixed(2) + " B " + currency;
  if (Math.abs(n) >= 1e6) return (n/1e6).toFixed(1) + " M " + currency;
  return n.toLocaleString() + " " + currency;
};

document.getElementById("meta").textContent =
  `${DATA.n_companies} companies · ${DATA.n_linked} cross-linked to main graph · ${Object.keys(DATA.communities).length} communities · generated ${DATA.generated_at}`;
document.getElementById("footer-stats").textContent =
  `Cross-link rate: ${(100*DATA.n_linked/DATA.n_companies).toFixed(0)}%`;

// Sort companies: linked first, then alphabetical by label
const COMPANIES = Object.values(DATA.companies).sort((a,b) => {
  if ((a.graph_entity_id?1:0) !== (b.graph_entity_id?1:0)) return (b.graph_entity_id?1:0) - (a.graph_entity_id?1:0);
  return (a.label||"").localeCompare(b.label||"");
});

let activeId = null;

function renderList(filter="") {
  const f = filter.trim().toLowerCase();
  const list = document.getElementById("list");
  list.innerHTML = "";
  for (const c of COMPANIES) {
    const text = `${c.label} ${c.country||""} ${c.industry||""} ${c.ticker||""}`.toLowerCase();
    if (f && !text.includes(f)) continue;
    const div = document.createElement("div");
    div.className = "item" + (c.graph_entity_id ? "" : " unlinked") + (c.company_id===activeId ? " active" : "");
    div.innerHTML = `<div class="label">${c.label}</div>
                     <div class="country">${[c.country, c.industry, c.ticker].filter(Boolean).join(" · ")}</div>`;
    div.onclick = () => { activeId = c.company_id; renderList(filter); renderDetail(c); };
    list.appendChild(div);
  }
}

function renderDetail(c) {
  const out = [];
  out.push(`<h2>${c.label}</h2>`);
  out.push(`<div class="sub">${[c.country, c.industry, c.ticker].filter(Boolean).join(" · ")}</div>`);

  out.push(`<div class="kvgrid">`);
  out.push(`<div class="k">Default currency</div><div class="v">${c.currency_default||"—"}</div>`);
  out.push(`<div class="k">Fiscal year end</div><div class="v">${c.fiscal_year_end||"—"}</div>`);
  out.push(`<div class="k">Source PDF</div><div class="v" style="font-size:11px;color:#9ca3af">${c.source_pdf||"—"}</div>`);
  if (c.community != null) {
    const com = DATA.communities[c.community];
    out.push(`<div class="k">Main-graph community</div><div class="v">#${c.community} (${com?com.n_members:"?"} members)<span class="badge-ok badge">linked</span></div>`);
  } else {
    out.push(`<div class="k">Main-graph link</div><div class="v"><span class="badge badge-warn">no main-graph entity</span></div>`);
  }
  if (c.graph_description) {
    out.push(`<div class="k">Main-graph notes</div><div class="v" style="font-size:11px">${c.graph_description}</div>`);
  }
  out.push(`</div>`);

  // Financial profile
  out.push(`<h3>Financial profile (canonical, FY actuals, local + USD)</h3>`);
  const metrics = c.metrics || {};
  const allYears = new Set();
  Object.values(metrics).forEach(yrs => Object.keys(yrs).forEach(y => allYears.add(y)));
  const years = Array.from(allYears).sort();
  if (!years.length) {
    out.push(`<div class="sub">No canonical metrics extracted.</div>`);
  } else {
    out.push(`<table class="metrics"><thead><tr><th>Metric</th>`);
    years.forEach(y => out.push(`<th>${y}</th>`));
    out.push(`</tr></thead><tbody>`);
    const order = ["revenue","gross_profit","operating_income","net_income","total_assets","total_liabilities","total_equity","employees","gross_margin_pct","operating_margin_pct","eps","dividend_per_share"];
    const seen = new Set();
    [...order, ...Object.keys(metrics).filter(k => !order.includes(k))].forEach(m => {
      if (!metrics[m] || seen.has(m)) return;
      seen.add(m);
      out.push(`<tr><td>${m}</td>`);
      years.forEach(y => {
        const v = metrics[m][y];
        if (!v) { out.push(`<td>—</td>`); return; }
        const isPct = m.endsWith("_pct");
        const isPerShare = m === "eps" || m === "dividend_per_share";
        if (isPct) out.push(`<td>${fmtNum(v.native, 1)}%</td>`);
        else if (isPerShare) out.push(`<td>${fmtNum(v.native, 2)} ${v.currency}</td>`);
        else if (m === "employees") out.push(`<td>${fmtNum(v.native)}</td>`);
        else out.push(`<td>${fmtMillions(v.native, v.currency)}</td>`);
      });
      out.push(`</tr>`);
    });
    out.push(`</tbody></table>`);
  }

  // Structural neighbors
  out.push(`<div class="grid-cols-2">`);
  out.push(`<div><h3>Outgoing relationships <span style="color:#6b7280;font-size:10px;font-weight:400">(${c.outgoing_edges?.length||0})</span></h3>`);
  if (!c.outgoing_edges?.length) out.push(`<div class="sub">None</div>`);
  c.outgoing_edges?.forEach(e =>
    out.push(`<div class="edge-row"><span class="relation">${e.relation}</span> → ${e.target}<span class="ent-type">[${e.type||"?"}]</span></div>`)
  );
  out.push(`</div>`);

  out.push(`<div><h3>Incoming relationships <span style="color:#6b7280;font-size:10px;font-weight:400">(${c.incoming_edges?.length||0})</span></h3>`);
  if (!c.incoming_edges?.length) out.push(`<div class="sub">None</div>`);
  c.incoming_edges?.forEach(e =>
    out.push(`<div class="edge-row">${e.source}<span class="ent-type">[${e.type||"?"}]</span> <span class="relation">${e.relation}</span> →</div>`)
  );
  out.push(`</div>`);
  out.push(`</div>`);

  // People
  out.push(`<h3>People (${c.people?.length||0})</h3>`);
  if (!c.people?.length) out.push(`<div class="sub">None extracted</div>`);
  c.people?.forEach(p => {
    const cross = p.n_affiliations > 1 ? `<span class="cross-board">cross-board (${p.n_affiliations} cos)</span>` : "";
    out.push(`<div class="person-row">${p.name} ${cross}<div class="role">${p.role||""} (${p.type||"?"})</div></div>`);
  });

  document.getElementById("detail").innerHTML = out.join("");
}

document.getElementById("filter").oninput = (e) => renderList(e.target.value);
renderList();
</script>
</body>
</html>
"""
    html = HTML.replace("__DATA__", blob)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}  ({len(html):,} bytes)")
    print(f"  Companies: {payload['n_companies']}")
    print(f"  Cross-linked to main graph: {payload['n_linked']} ({100*payload['n_linked']//payload['n_companies']}%)")
    print(f"  Communities referenced: {len(payload['communities'])}")

    conn.close()


if __name__ == "__main__":
    main()
