#!/usr/bin/env python3.12
"""Build a knowledge graph from financial_briefs/*.md.

Deterministic parser (no LLM cost): walks each brief's structured sections
(Income statement, Balance sheet, Leadership, Industry context) and emits
nodes + edges in graphify-compatible schema.

Output: financial_briefs/graphify-out/graph.json + minimal graph.html.

Why this script exists: the subagent that originally built the
financial-briefs graph used a similar parser but didn't preserve the
script. This is a reproducer so the graph can be regenerated whenever
the briefs change.
"""
from __future__ import annotations
import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
BRIEFS_DIR = ROOT / "financial_briefs"
OUT_DIR = BRIEFS_DIR / "graphify-out"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower().strip()).strip("_")


# Trend buckets for revenue growth + margin tagging
def revenue_growth_trend(yoy_pct: float | None) -> str | None:
    if yoy_pct is None:
        return None
    if yoy_pct > 25:  return "trend_high_revenue_growth"
    if yoy_pct > 10:  return "trend_double_digit_revenue_growth"
    if yoy_pct > 0:   return "trend_single_digit_revenue_growth"
    if yoy_pct > -5:  return "trend_flat_revenue_growth"
    return "trend_revenue_decline"


def margin_trend(gross_pct: float | None) -> str | None:
    if gross_pct is None:
        return None
    if gross_pct > 50: return "trend_high_gross_margin"
    if gross_pct < 20: return "trend_low_gross_margin"
    return None


TREND_LABELS = {
    "trend_high_revenue_growth": "High Revenue Growth (25%+)",
    "trend_double_digit_revenue_growth": "Double-Digit Revenue Growth",
    "trend_single_digit_revenue_growth": "Single-Digit Revenue Growth",
    "trend_flat_revenue_growth": "Flat Revenue Growth",
    "trend_revenue_decline": "Revenue Decline / Contraction",
    "trend_high_gross_margin": "High Gross Margin (>50%)",
    "trend_low_gross_margin": "Low Gross Margin (<20%)",
    "trend_strong_cagr": "Strong Multi-year CAGR (>15%)",
}


# Patterns
RE_TITLE = re.compile(r"^#\s+(.+?)\s+—\s+Financial Brief", re.M)
RE_INTRO = re.compile(r"is a ([\w-]+)-headquartered company in the ([\w_]+) segment", re.I)
RE_TICKER = re.compile(r"Ticker:\s*([^.\n]+)\.")
RE_REV = re.compile(r"reported revenue of (.+?) \(US\$([\d.]+)([BM])\)")
RE_REV_GROWTH = re.compile(r"Revenue growth versus \d{4} was ([+-]?[\d.]+)%")
RE_GM_OM = re.compile(r"Gross margin was ([\d.]+)%, and operating margin was ([\d.]+)%")
RE_CAGR = re.compile(r"compounded at a CAGR of ([\d.]+)%")
RE_PEERS = re.compile(r"alongside peers including (.+?)\.\s*These", re.S)
RE_LEDBY = re.compile(r"^- (.+?) serves as (.+?)\.\s*$", re.M)
RE_CROSSBOARD = re.compile(r"^- \*\*(.+?)\*\* \(([^)]+)\) also serves at (.+?), creating", re.M)
RE_COMPETES = re.compile(r"competes with: (.+?)\.\s*$", re.M)
RE_DEVELOPS = re.compile(r"develops: (.+?)\.\s*$", re.M)
RE_PRODUCES = re.compile(r"produces: (.+?)\.\s*$", re.M)
RE_CLASSIFIED = re.compile(r"classified as: (.+?)\.\s*$", re.M)


def parse_brief(path: Path) -> dict:
    text = path.read_text()
    company_id = path.stem
    out = {"company_id": company_id, "company_label": None, "country": None,
           "industry": None, "ticker": None, "revenue_native": None,
           "revenue_usd_b": None, "revenue_yoy_pct": None,
           "gross_margin_pct": None, "operating_margin_pct": None,
           "cagr_pct": None, "peers": [], "led_by": [],
           "cross_board": [], "competes_with": [], "develops": [],
           "produces": [], "classified_as": []}
    if m := RE_TITLE.search(text):
        out["company_label"] = m.group(1).strip()
    if m := RE_INTRO.search(text):
        out["country"] = m.group(1)
        out["industry"] = m.group(2)
    if m := RE_TICKER.search(text):
        out["ticker"] = m.group(1).strip()
    if m := RE_REV.search(text):
        out["revenue_native"] = m.group(1)
        rev_b = float(m.group(2))
        if m.group(3) == "M":
            rev_b = rev_b / 1000
        out["revenue_usd_b"] = rev_b
    if m := RE_REV_GROWTH.search(text):
        try: out["revenue_yoy_pct"] = float(m.group(1))
        except Exception: pass
    if m := RE_GM_OM.search(text):
        try:
            out["gross_margin_pct"] = float(m.group(1))
            out["operating_margin_pct"] = float(m.group(2))
        except Exception: pass
    if m := RE_CAGR.search(text):
        try: out["cagr_pct"] = float(m.group(1))
        except Exception: pass
    if m := RE_PEERS.search(text):
        out["peers"] = [p.strip() for p in m.group(1).split(",") if p.strip()]
    out["led_by"] = [(name.strip(), role.strip()) for name, role in RE_LEDBY.findall(text)]
    out["cross_board"] = [(n.strip(), r.strip(), o.strip()) for n, r, o in RE_CROSSBOARD.findall(text)]
    for pat, key in [(RE_COMPETES, "competes_with"), (RE_DEVELOPS, "develops"),
                     (RE_PRODUCES, "produces"), (RE_CLASSIFIED, "classified_as")]:
        for m in pat.finditer(text):
            out[key].extend([s.strip() for s in m.group(1).split(",") if s.strip()])
    return out


def build_graph(briefs: list[dict]) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(node_id: str, **attrs):
        if node_id in nodes:
            for k, v in attrs.items():
                if v is not None and k not in nodes[node_id]:
                    nodes[node_id][k] = v
        else:
            nodes[node_id] = {"id": node_id, **attrs}

    def add_edge(s: str, t: str, relation: str, **attrs):
        edges.append({"source": s, "target": t, "relation": relation, **attrs})

    for b in briefs:
        cid = b["company_id"]
        # Company node
        add_node(cid, label=b["company_label"] or cid, type="company",
                 country=b["country"], industry=b["industry"], ticker=b["ticker"],
                 revenue_usd_b=b["revenue_usd_b"], revenue_yoy_pct=b["revenue_yoy_pct"],
                 gross_margin_pct=b["gross_margin_pct"],
                 operating_margin_pct=b["operating_margin_pct"],
                 source="EXTRACTED", source_file=f"financial_briefs/{cid}.md")
        # Country node
        if b["country"]:
            cn = "country_" + norm(b["country"])
            add_node(cn, label=b["country"], type="country")
            add_edge(cid, cn, "located_in")
        # Industry-segment node
        if b["industry"]:
            seg = "industry_" + norm(b["industry"])
            add_node(seg, label=b["industry"], type="industry_segment")
            add_edge(cid, seg, "operates_in")
        # Financial milestone (FY2024 most-recent revenue)
        if b["revenue_usd_b"] is not None:
            ms = f"milestone_{cid}_revenue"
            add_node(ms, label=f"FY{b.get('fy_label', '2024')} {b['company_label'] or cid} Revenue",
                     type="financial_milestone",
                     revenue_billion=b["revenue_usd_b"],
                     growth_pct=b["revenue_yoy_pct"],
                     gross_margin_pct=b["gross_margin_pct"])
            add_edge(cid, ms, "achieved")
            tr = revenue_growth_trend(b["revenue_yoy_pct"])
            if tr:
                add_node(tr, label=TREND_LABELS[tr], type="trend")
                add_edge(ms, tr, "exemplifies")
            mt = margin_trend(b["gross_margin_pct"])
            if mt:
                add_node(mt, label=TREND_LABELS[mt], type="trend")
                add_edge(ms, mt, "exemplifies")
            if b["cagr_pct"] is not None and b["cagr_pct"] > 15:
                add_node("trend_strong_cagr", label=TREND_LABELS["trend_strong_cagr"], type="trend")
                add_edge(cid, "trend_strong_cagr", "exemplifies")
        # People
        for name, role in b["led_by"]:
            pid = "person_" + norm(name)
            add_node(pid, label=name, type="person", primary_role=role)
            add_edge(pid, cid, "led_by")
        # Cross-board (people on multiple boards)
        for name, role, others in b["cross_board"]:
            pid = "person_" + norm(name)
            add_node(pid, label=name, type="person", primary_role=role)
            add_edge(pid, cid, "led_by", note="cross-board")
            for other in re.split(r",\s*|\s+and\s+", others):
                other_id = norm(other)
                if other_id and other_id != cid:
                    add_edge(cid, other_id, "shares_director_with",
                             via=name, source="INFERRED")
        # Peers (community-mates)
        for peer in b["peers"]:
            peer_id = norm(peer)
            if peer_id and peer_id != cid:
                add_edge(cid, peer_id, "shares_community_with", source="INFERRED")
        # Competes with
        for comp in b["competes_with"]:
            comp_id = norm(comp)
            if comp_id and comp_id != cid:
                add_edge(cid, comp_id, "competes_with", source="EXTRACTED")
        # Develops / produces
        for prod in b["develops"]:
            pid = "product_" + norm(prod)
            add_node(pid, label=prod, type="product")
            add_edge(cid, pid, "develops")
        for prod in b["produces"]:
            pid = "product_" + norm(prod)
            add_node(pid, label=prod, type="product")
            add_edge(cid, pid, "produces")
        # Classifications
        for cls in b["classified_as"]:
            tag = "tag_" + norm(cls)
            add_node(tag, label=cls, type="industry_tag")
            add_edge(cid, tag, "classified_as")

    return {
        "directed": True, "multigraph": False,
        "graph": {"title": "Financial-briefs knowledge subgraph",
                  "generated_at": "2026-04-25",
                  "extractor": "deterministic parser (scripts/build_briefs_graph.py)",
                  "schema_version": "briefs-v1"},
        "nodes": list(nodes.values()),
        "links": edges,
        "hyperedges": [],
    }


def main():
    briefs = []
    for path in sorted(BRIEFS_DIR.glob("*.md")):
        if path.parent != BRIEFS_DIR:
            continue
        briefs.append(parse_brief(path))
    print(f"Parsed {len(briefs)} briefs")
    g = build_graph(briefs)
    out = OUT_DIR / "graph.json"
    out.write_text(json.dumps(g, indent=2, ensure_ascii=False))
    print(f"Wrote {out.relative_to(ROOT)}: {len(g['nodes'])} nodes, {len(g['links'])} edges")


if __name__ == "__main__":
    main()
