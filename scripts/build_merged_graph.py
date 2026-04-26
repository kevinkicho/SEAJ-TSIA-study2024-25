#!/usr/bin/env python3.12
"""Merge TSMC + 9 new company extractions into one multi-company subgraph.

Schema-compatible with existing graphify graph.json: directed, multigraph=False,
nodes/links/hyperedges. Adds normalized canonical metric names for cross-company
sizing, and FX rates (to USD) for cross-company comparison.
"""
import json, re
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")

COMPANIES = {
    "tsmc":    {"label": "TSMC", "country": "Taiwan", "industry": "semiconductor_foundry", "ticker": "TWSE:2330,NYSE:TSM"},
    "wpg":     {"label": "WPG Holdings", "country": "Taiwan", "industry": "electronics_distribution", "ticker": "TWSE:3702"},
    "umc":     {"label": "United Microelectronics (UMC)", "country": "Taiwan", "industry": "semiconductor_foundry", "ticker": "TWSE:2303,NYSE:UMC"},
    "amat":    {"label": "Applied Materials", "country": "USA", "industry": "wfe_equipment", "ticker": "NASDAQ:AMAT"},
    "medipal": {"label": "MEDIPAL Holdings", "country": "Japan", "industry": "pharma_distribution", "ticker": "TSE:7459"},
    "alcor":   {"label": "Alcor Micro", "country": "Taiwan", "industry": "ic_design", "ticker": "TWSE:8054"},
    "itri":    {"label": "ITRI", "country": "Taiwan", "industry": "research_nonprofit", "ticker": None},
    "ase":     {"label": "ASE Technology Holding", "country": "Taiwan", "industry": "semiconductor_packaging_test", "ticker": "TWSE:3711,NYSE:ASX"},
    "vis":     {"label": "Vanguard International Semi (VIS)", "country": "Taiwan", "industry": "specialty_foundry", "ticker": "TWSE:5347"},
    "egis":    {"label": "Egis Technology", "country": "Taiwan", "industry": "biometric_ic", "ticker": "TWSE:6462"},
}

# FX rates to USD: load from fx_rates.json (fetched live from frankfurter.dev + open.er-api.com).
# Run scripts/fetch_fx.py to refresh.
_FX_PATH = ROOT / "graphify-financial" / "fx_rates.json"
if _FX_PATH.exists():
    _fx_data = json.loads(_FX_PATH.read_text())
    FX_TO_USD = _fx_data["rates_usd_per_unit"]
    FX_SOURCES = _fx_data.get("sources", {})
    FX_FETCHED_AT = _fx_data.get("fetched_at")
else:
    # Fallback (only if scripts/fetch_fx.py was never run)
    FX_TO_USD = {"TWD": 1/32.0, "JPY": 1/150.0, "USD": 1.0}
    FX_SOURCES = {}
    FX_FETCHED_AT = None

# Canonical metric mapping: maps various raw labels to a unified canonical name.
# Used for cross-company comparison/sizing. Native labels are preserved in the per-page metrics.
CANONICAL_MAP = {
    # Revenue
    "net revenue": "revenue",
    "consolidated revenue": "revenue",
    "operating revenue": "revenue",
    "operating revenues": "revenue",
    "net sales": "revenue",
    "net sales (consolidated)": "revenue",
    "total revenue": "revenue",
    "total revenues": "revenue",
    "net operating revenue": "revenue",
    "net revenue (consolidated)": "revenue",
    "revenue": "revenue",
    "revenues": "revenue",
    "sales": "revenue",
    "consolidated net sales": "revenue",
    "net sales revenue": "revenue",
    "consolidated revenues": "revenue",
    # Taiwanese / Japanese accounting variants
    "net operating income (revenue)": "revenue",
    "operating income (revenue)": "revenue",
    "net sales of completed construction contracts": "revenue",
    "net sales of completed construction contracts (consolidated)": "revenue",
    "operating revenue (revenue)": "revenue",
    "consolidated net operating revenue": "revenue",
    "net operating revenues": "revenue",
    # Net income
    "net income": "net_income",
    "net profit": "net_income",
    "net income (consolidated)": "net_income",
    "net loss": "net_income",
    "net profit (loss) for the current period": "net_income",
    "after-tax net profit (loss)": "net_income",
    # Japanese / IFRS standard "Profit attributable to owners of parent" — same as net income
    "profit attributable to owners of parent": "net_income",
    "profit attributable to owners of the parent": "net_income",
    "net income attributable to owners of parent": "net_income",
    "net income attributable to owners of the parent": "net_income",
    "profit attributable to owners of parent company": "net_income",
    "net income attributable to shareholders of the parent": "net_income",
    "net profit attributable to the parent company": "net_income",
    "net profit attributable to owners of parent": "net_income",
    "net earnings": "net_income",
    "net earnings from operations": "net_income",
    "net profit after tax": "net_income",
    "after tax net profit": "net_income",
    "after tax net income": "net_income",
    "consolidated net income": "net_income",
    "consolidated net profit": "net_income",
    # Operating income
    "operating income": "operating_income",
    "profit from operations": "operating_income",
    "operating income (consolidated)": "operating_income",
    "operating profit": "operating_income",
    "operating profit (loss)": "operating_income",
    "net operating income": "operating_income",
    "operating income from operations": "operating_income",
    "consolidated operating income": "operating_income",
    "consolidated operating profit": "operating_income",
    "income from operations": "operating_income",
    # Total assets
    "total assets": "total_assets",
    "consolidated total assets": "total_assets",
    "total assets (consolidated)": "total_assets",
    # Total liabilities (newly added canonical)
    "total liabilities": "total_liabilities",
    "consolidated total liabilities": "total_liabilities",
    "total liabilities (consolidated)": "total_liabilities",
    "total liabilities (parent only)": "total_liabilities",
    "total liabilities (parent)": "total_liabilities",
    # Total equity
    "total equity": "total_equity",
    "total shareholders' equity": "total_equity",
    "total stockholders' equity": "total_equity",
    "total stockholders equity": "total_equity",
    "total shareholders equity": "total_equity",
    "total net assets": "total_equity",
    "shareholders' equity": "total_equity",
    "total equity attributable to owners of parent": "total_equity",
    "total equity attributable to shareholders of the parent": "total_equity",
    "total equity attributable to shareholders of the parent company": "total_equity",
    "consolidated total equity": "total_equity",
    "total equity (parent only)": "total_equity",
    # Employees
    "number of employees": "employees",
    # Gross profit
    "gross profit": "gross_profit",
    "gross profit (consolidated)": "gross_profit",
    "gross profit from operations": "gross_profit",
    "gross operating profit": "gross_profit",
    # Margins
    "gross profit margin (%)": "gross_margin_pct",
    "gross margin (%)": "gross_margin_pct",
    "gross profit margin (%) (consolidated)": "gross_margin_pct",
    "gross profit margin": "gross_margin_pct",
    "operating margin (%)": "operating_margin_pct",
    "operating margin (%) (consolidated)": "operating_margin_pct",
    "operating margin": "operating_margin_pct",
    "operating profit margin": "operating_margin_pct",
    "operating profit margin (%)": "operating_margin_pct",
    "net margin (%)": "net_margin_pct",
    "net profit margin": "net_margin_pct",
    "net profit margin (%)": "net_margin_pct",
    # EPS
    "diluted earnings per share (nt$)": "eps",
    "earnings per diluted share": "eps",
    "diluted eps (nt$)": "eps",
    "basic eps (nt$)": "eps",
    # Dividend
    "total cash dividend per share (nt$)": "dividend_per_share",
    "annual cash dividend per share (¥)": "dividend_per_share",
    "cash dividend (nt$)": "dividend_per_share",
}

CANONICAL_UNITS = {
    "revenue": "currency_native",
    "net_income": "currency_native",
    "operating_income": "currency_native",
    "total_assets": "currency_native",
    "total_liabilities": "currency_native",
    "total_equity": "currency_native",
    "gross_profit": "currency_native",
    "employees": "count",
    "gross_margin_pct": "pct",
    "operating_margin_pct": "pct",
    "net_margin_pct": "pct",
    "eps": "currency_per_share",
    "dividend_per_share": "currency_per_share",
}


def to_canonical(name: str) -> str | None:
    """Map a printed metric name to a canonical key (e.g., revenue, net_income).

    Normalization sequence (each layer is a fallback if the prior misses):
      1. raw lowercase exact match
      2. strip parenthetical qualifiers, e.g. "(consolidated)", "(FY2024)"
      3. strip trailing year tokens, e.g. "Net Sales 2024" → "net sales"
         (vision sometimes emits the year in the metric name + values dict)
      4. strip leading "consolidated"/"the company" prefixes
    """
    import re as _re
    raw = name.strip().lower()
    if raw in CANONICAL_MAP:
        return CANONICAL_MAP[raw]
    # Layer 2: strip parentheticals
    n = _re.sub(r"\s*\([^)]*\)\s*", " ", raw).strip()
    n = _re.sub(r"\s+", " ", n)
    if n in CANONICAL_MAP:
        return CANONICAL_MAP[n]
    # Layer 3: strip trailing year (4-digit or FY+year)
    n2 = _re.sub(r"\s+(?:FY\s*)?\d{4}(?:[\s_]+\dQ)?\s*$", "", n, flags=_re.I).strip()
    if n2 != n and n2 in CANONICAL_MAP:
        return CANONICAL_MAP[n2]
    # Layer 4: strip leading "consolidated"/"company"/"the company" markers
    n3 = _re.sub(r"^(consolidated|the company['s]*|company)\s+", "", n2, flags=_re.I).strip()
    if n3 != n2 and n3 in CANONICAL_MAP:
        return CANONICAL_MAP[n3]
    return None


def normalize_to_native_currency_native_unit(value, unit, currency):
    """Normalize value to native currency in 'whole units' (e.g., NT$ as-is, not millions)."""
    if value is None: return None
    if unit in ("millions", "million"):
        return value * 1_000_000
    if unit in ("thousands", "thousand"):
        return value * 1_000
    if unit in ("billions", "billion"):
        return value * 1_000_000_000
    return value


def native_to_usd_value(value, currency):
    if value is None: return None
    rate = FX_TO_USD.get(currency, 1.0)
    return value * rate


def load_extraction(key, ext_path):
    if key == "tsmc":
        # Use the existing TSMC files
        fin = json.loads((ROOT / "graphify-financial/tsmc/tsmc_financials.json").read_text())
        ppl = json.loads((ROOT / "graphify-financial/tsmc/tsmc_people.json").read_text())
        # Convert to combined extraction format
        return {
            "company": "TSMC",
            "ticker": "TWSE:2330,NYSE:TSM",
            "currency_default": "TWD",
            "fiscal_year_end": "December",
            "financial_pages": fin["pages"],
            "people_pages": ppl["pages"],
        }
    return json.loads(ext_path.read_text())


def collect_canonical_metrics(extraction):
    """Build {canonical_name: {year: {value_native, currency, unit_native, value_usd}}}.
    Prefers higher-quality pages (income_statement > 5_year_highlights > financial_highlights > others).
    """
    PRIORITY = {"income_statement": 4, "balance_sheet": 4, "5_year_highlights": 3,
                "financial_highlights": 2, "segment_breakdown": 1, "revenue_breakdown": 1,
                "cash_flow": 2, "capital_structure": 1, "other": 0, "non_financial": -1}
    out = {}
    for page in extraction.get("financial_pages", []):
        if not page.get("is_financial_table") or not page.get("is_company_actual", True):
            continue
        prio = PRIORITY.get(page.get("table_type", "other"), 0)
        currency = page.get("currency") or extraction.get("currency_default") or "TWD"
        unit = page.get("unit") or "as_is"
        for met in page.get("metrics", []):
            canon = to_canonical(met["name"])
            if not canon: continue
            vals = met.get("values", {})
            for y, v in vals.items():
                if not isinstance(y, str) or not re.match(r"^\d{4}$", y):
                    continue
                if not isinstance(v, (int, float)):
                    continue
                key = (canon, y)
                # Convert to native whole-unit and USD
                v_native = normalize_to_native_currency_native_unit(v, unit, currency)
                # Margins/percentages: don't convert
                if canon in ("gross_margin_pct", "operating_margin_pct"):
                    v_native = v
                v_usd = native_to_usd_value(v_native, currency) if canon not in ("gross_margin_pct", "operating_margin_pct", "employees") else v_native
                # Keep highest-priority page's value (most authoritative)
                existing = out.get(key)
                if existing and existing["_prio"] >= prio:
                    continue
                out[key] = {
                    "_prio": prio,
                    "value_native": v_native,
                    "value_usd": v_usd,
                    "currency": currency,
                    "source_page": page["page_id"],
                }
    # Strip _prio
    final = {}
    for (canon, year), v in out.items():
        final.setdefault(canon, {"unit": CANONICAL_UNITS.get(canon, "unknown"), "values": {}})
        final[canon]["values"][year] = {"native": v["value_native"], "usd": v["value_usd"], "currency": v["currency"], "source_page": v["source_page"]}
    return final


def main():
    nodes, edges = [], []
    person_dedup = {}  # global by (norm_name) -> node_id (so cross-company appearances merge)

    def norm_name(s):
        return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")

    for key, meta in COMPANIES.items():
        ext_path = ROOT / "graphify-financial" / key / f"{key}_extraction.json"
        if not ext_path.exists() and key != "tsmc":
            print(f"[skip] {key}: no extraction file"); continue
        ex = load_extraction(key, ext_path)

        canonical = collect_canonical_metrics(ex)
        # Also build the raw native-label metric set for the company panel
        native_metrics = {}
        for page in ex.get("financial_pages", []):
            if not page.get("is_financial_table"): continue
            for m in page.get("metrics", []):
                native_metrics.setdefault(m["name"], {"page": page["page_id"], "currency": page.get("currency"), "unit": page.get("unit"), "values": {}})
                for y, v in m.get("values", {}).items():
                    if isinstance(v, (int, float)):
                        native_metrics[m["name"]]["values"][y] = v

        company_node = {
            "id": f"company_{key}",
            "label": meta["label"],
            "norm_label": key,
            "type": "company",
            "file_type": "company",
            "country": meta["country"],
            "industry": meta["industry"],
            "ticker": meta["ticker"],
            "currency_default": ex.get("currency_default", "TWD"),
            "fiscal_year_end": ex.get("fiscal_year_end"),
            "metrics_canonical": canonical,
            "metrics_native": native_metrics,
            "community": 0,
            "confidence_score": 1.0,
            "source": "EXTRACTED",
            "extraction_type": "EXTRACTED",
        }
        nodes.append(company_node)

        for ppage in ex.get("people_pages", []):
            for person in ppage.get("people", []):
                pname = person.get("name") or ""
                if not pname: continue
                nkey = norm_name(pname)
                if nkey in person_dedup:
                    pid = person_dedup[nkey]
                    # Merge concurrent role onto existing node
                    existing = next(n for n in nodes if n["id"] == pid)
                    if "linked_companies" not in existing: existing["linked_companies"] = []
                    if key not in existing["linked_companies"]:
                        existing["linked_companies"].append(key)
                else:
                    pid = f"person_{nkey}"
                    person_dedup[nkey] = pid
                    nodes.append({
                        "id": pid,
                        "label": pname,
                        "norm_label": nkey,
                        "type": "person",
                        "file_type": "person",
                        "person_type": person.get("type", "other"),
                        "primary_role": person.get("role", ""),
                        "primary_company": key,
                        "linked_companies": [key],
                        "tenure_start": person.get("tenure_start"),
                        "education": person.get("education"),
                        "concurrent_roles": person.get("concurrent_roles", []),
                        "community": 0,
                        "confidence_score": 0.95,
                        "source": "EXTRACTED",
                        "extraction_type": "EXTRACTED",
                    })
                rel = {
                    "board_director": "serves_on_board_of",
                    "independent_director": "serves_on_board_of",
                    "executive_officer": "executive_of",
                    "senior_vp": "executive_of",
                    "vp": "executive_of",
                    "committee_member": "serves_on_committee_of",
                    "other": "affiliated_with",
                }.get(person.get("type", "other"), "affiliated_with")
                edges.append({
                    "source": pid,
                    "target": f"company_{key}",
                    "relation": rel,
                    "role": person.get("role", ""),
                    "confidence": 0.95,
                    "confidence_score": 0.95,
                    "source_file": "vision_extraction",
                    "weight": 2.0 if "director" in person.get("type", "") else 1.0,
                })

    # Persist graph
    graph = {
        "directed": True,
        "multigraph": False,
        "graph": {
            "title": "Multi-Company Financial Subgraph (10 companies)",
            "generated_at": "2026-04-24",
            "extractor": "sonnet-4.6 vision + pdftoppm",
            "schema_version": "financial-v2",
            "fx_to_usd": FX_TO_USD,
            "fx_sources": FX_SOURCES,
            "fx_fetched_at": FX_FETCHED_AT,
            "canonical_metric_keys": list(CANONICAL_UNITS.keys()),
            "canonical_metric_units": CANONICAL_UNITS,
        },
        "nodes": nodes,
        "links": edges,
        "hyperedges": [],
    }
    out = ROOT / "graphify-financial" / "graph-financial.json"
    out.write_text(json.dumps(graph, indent=2, ensure_ascii=False))
    print(f"Wrote {out}")
    n_companies = sum(1 for n in nodes if n["type"] == "company")
    n_people = sum(1 for n in nodes if n["type"] == "person")
    print(f"  Companies: {n_companies}")
    print(f"  People:    {n_people} unique (deduped across companies)")
    print(f"  Edges:     {len(edges)}")
    # Cross-company person counts
    multi_company_people = [n for n in nodes if n["type"] == "person" and len(n.get("linked_companies", [])) > 1]
    print(f"  People appearing on >1 company: {len(multi_company_people)}")
    for p in multi_company_people:
        print(f"    {p['label']}: {p['linked_companies']}")
    # Years coverage per metric
    print(f"\n  Canonical metric coverage:")
    metric_year_count = {}
    for n in nodes:
        if n["type"] != "company": continue
        for m, info in n.get("metrics_canonical", {}).items():
            metric_year_count.setdefault(m, set()).update(info["values"].keys())
    for m, ys in sorted(metric_year_count.items()):
        print(f"    {m}: {sorted(ys)}")

if __name__ == "__main__":
    main()
