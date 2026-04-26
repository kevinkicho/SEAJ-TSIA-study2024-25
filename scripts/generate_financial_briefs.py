#!/usr/bin/env python3.12
"""Generate one markdown brief per company from financials.db.

The briefs are written in natural prose (not tables) so that when
/graphify --update processes them, the LLM extraction picks up:
  - financial-derived entities (e.g., "record FY2024 revenue", "margin
    compression", "AI-driven test demand")
  - new relationships (cross-board people connecting two companies,
    customer/supplier links derived from the main graph, peer
    comparisons by community)
  - time-series trend nodes (e.g., "HBM-driven Advantest revenue surge")

Output: financial_briefs/<company_id>.md
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
from collections import defaultdict

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
DB = ROOT / "graphify-financial" / "financials.db"
OUT = ROOT / "financial_briefs"
OUT.mkdir(exist_ok=True)


def fmt_currency(v: float | None, currency: str | None) -> str:
    if v is None or currency is None:
        return "n/a"
    if abs(v) >= 1e12:
        return f"{v/1e12:.2f} trillion {currency}"
    if abs(v) >= 1e9:
        return f"{v/1e9:.2f} billion {currency}"
    if abs(v) >= 1e6:
        return f"{v/1e6:.1f} million {currency}"
    return f"{v:,.0f} {currency}"


def fmt_usd_b(v: float | None) -> str:
    if v is None:
        return "n/a"
    if abs(v) >= 1e9:
        return f"US${v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"US${v/1e6:.1f}M"
    return f"US${v:,.0f}"


def yoy_pct(curr: float | None, prev: float | None) -> str:
    if curr is None or prev is None or prev == 0:
        return ""
    pct = (curr - prev) / abs(prev) * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def get_metric_series(c, company_id: str, canonical: str) -> dict[str, dict]:
    """Return {year: {native, usd, currency}} for a company's canonical metric (FY actuals).
    Uses value_native_whole (unit-normalized) so 'thousands' vs 'millions' vs 'billions'
    units don't break the magnitude display. For percentages, value_native is already
    in [-100, 100] range so we use that. When multiple rows exist for the same
    company-year (consolidated vs parent), pick the maximum (consolidated)."""
    is_pct = canonical in ("gross_margin_pct", "operating_margin_pct", "net_margin_pct")
    is_per_share = canonical in ("eps", "dividend_per_share")
    val_col = "value_native" if (is_pct or is_per_share) else "value_native_whole"
    # Aggregate by year to handle consolidated/parent duplicates
    if is_pct:
        agg = "AVG"
    elif canonical == "employees":
        agg = "MAX"
    elif is_per_share:
        agg = "MAX"  # per-share values: prefer the printed (non-aggregated) value
    else:
        agg = "MAX"  # absolute amounts: prefer the consolidated (larger) value
    rows = c.execute(
        f"""SELECT year, {agg}({val_col}) AS v, {agg}(value_usd) AS usd, MAX(currency) AS currency
           FROM financial_metrics
           WHERE company_id=? AND canonical_name=? AND is_forecast=0 AND period IN ('FY','FY3')
             AND {val_col} IS NOT NULL
           GROUP BY year ORDER BY year""",
        (company_id, canonical),
    ).fetchall()
    return {r["year"]: {"native": r["v"], "usd": r["usd"], "currency": r["currency"]}
            for r in rows if r["v"] is not None}


def write_brief(c, company_id: str) -> str:
    co = c.execute("SELECT * FROM companies WHERE company_id=?", (company_id,)).fetchone()
    if not co:
        return ""
    label = co["label"]
    country = co["country"] or "Unknown"
    industry = co["industry"] or "unknown"
    ticker = co["ticker"] or "private"
    currency = co["currency_default"] or "USD"
    fye = co["fiscal_year_end"] or "December"

    lines = []
    lines.append(f"# {label} — Financial Brief")
    lines.append("")
    lines.append(f"{label} is a {country}-headquartered company in the {industry} segment of the semiconductor value chain.")
    lines.append(f"It reports in {currency} with fiscal year ending {fye}. Ticker: {ticker}.")
    lines.append("")

    # Pull canonical series
    rev = get_metric_series(c, company_id, "revenue")
    ni = get_metric_series(c, company_id, "net_income")
    oi = get_metric_series(c, company_id, "operating_income")
    gp = get_metric_series(c, company_id, "gross_profit")
    ta = get_metric_series(c, company_id, "total_assets")
    tl = get_metric_series(c, company_id, "total_liabilities")
    te = get_metric_series(c, company_id, "total_equity")
    gm = get_metric_series(c, company_id, "gross_margin_pct")
    om = get_metric_series(c, company_id, "operating_margin_pct")
    nm = get_metric_series(c, company_id, "net_margin_pct")
    eps = get_metric_series(c, company_id, "eps")
    emp = get_metric_series(c, company_id, "employees")

    # ---- Income statement narrative ----
    if rev:
        lines.append(f"## Income statement")
        lines.append("")
        years = sorted(rev.keys())
        latest = years[-1]
        lines.append(f"In fiscal year {latest}, {label} reported revenue of "
                     f"{fmt_currency(rev[latest]['native'], rev[latest]['currency'])} "
                     f"({fmt_usd_b(rev[latest]['usd'])}).")
        if len(years) >= 2:
            prev = years[-2]
            yoy = yoy_pct(rev[latest]["native"], rev[prev]["native"])
            if yoy:
                lines.append(f"Revenue growth versus {prev} was {yoy}.")
        if ni and latest in ni:
            lines.append(f"Net income was {fmt_currency(ni[latest]['native'], ni[latest]['currency'])} "
                         f"({fmt_usd_b(ni[latest]['usd'])}).")
        if oi and latest in oi:
            lines.append(f"Operating income reached {fmt_currency(oi[latest]['native'], oi[latest]['currency'])}.")
        if gm and latest in gm:
            lines.append(f"Gross margin was {gm[latest]['native']:.1f}%, "
                         f"and operating margin was {(om[latest]['native'] if om and latest in om else 0):.1f}%.")
        if eps and latest in eps:
            lines.append(f"Diluted earnings per share were {eps[latest]['native']:.2f} {eps[latest]['currency']}.")
        # Multi-year arc
        if len(years) >= 4:
            first = years[0]
            cagr_years = int(latest) - int(first) if first.isdigit() and latest.isdigit() else None
            if cagr_years and cagr_years > 0 and rev[first]['native'] > 0:
                cagr = ((rev[latest]['native']/rev[first]['native']) ** (1/cagr_years) - 1) * 100
                lines.append(f"Across the {first}–{latest} window, revenue compounded at a CAGR of {cagr:.1f}%.")
        lines.append("")

    # ---- Balance sheet narrative ----
    if ta:
        years = sorted(ta.keys())
        latest = years[-1]
        lines.append(f"## Balance sheet")
        lines.append("")
        lines.append(f"As of fiscal year {latest}, {label} reported total assets of "
                     f"{fmt_currency(ta[latest]['native'], ta[latest]['currency'])}.")
        if tl and latest in tl:
            lines.append(f"Total liabilities were {fmt_currency(tl[latest]['native'], tl[latest]['currency'])}, "
                         f"and total equity was "
                         f"{fmt_currency(te[latest]['native'] if te and latest in te else None, ta[latest]['currency'])}.")
        if te and latest in te and ta[latest]['native']:
            equity_ratio = te[latest]['native'] / ta[latest]['native'] * 100
            lines.append(f"The equity ratio (total equity / total assets) was {equity_ratio:.1f}%.")
        if len(years) >= 5:
            first = years[0]
            lines.append(f"Total assets data is available across {first}–{latest} ({len(years)} years), "
                         f"giving a multi-year view of capital deployment.")
        lines.append("")

    # ---- People & cross-board ----
    people = c.execute(
        """SELECT p.name, pa.role, pa.affiliation_type,
                  (SELECT GROUP_CONCAT(pa2.company_id, ', ')
                   FROM person_affiliations pa2
                   WHERE pa2.person_id = p.person_id AND pa2.company_id != pa.company_id) AS other_cos
           FROM person_affiliations pa
           JOIN people p ON p.person_id = pa.person_id
           WHERE pa.company_id = ?
           ORDER BY p.name LIMIT 25""",
        (company_id,)
    ).fetchall()
    if people:
        lines.append(f"## Leadership")
        lines.append("")
        # Highlight cross-board people first
        cross = [p for p in people if p["other_cos"]]
        if cross:
            lines.append("Notable cross-board affiliations:")
            for p in cross[:5]:
                others = p["other_cos"].replace(",", " and")
                lines.append(f"- **{p['name']}** ({p['role'] or p['affiliation_type']}) "
                             f"also serves at {others}, creating a governance link between these companies.")
            lines.append("")
        # Top-level executives
        exec_terms = ("chairman", "ceo", "president", "cfo", "coo")
        execs = [p for p in people if p["role"] and any(t in p["role"].lower() for t in exec_terms)][:5]
        if execs:
            for p in execs:
                lines.append(f"- {p['name']} serves as {p['role']}.")
            lines.append("")

    # ---- Main-graph community context ----
    e = c.execute(
        "SELECT entity_id, label, community, description FROM entities WHERE financial_company_id=? LIMIT 1",
        (company_id,)
    ).fetchone()
    if e and e["community"] is not None:
        lines.append(f"## Industry context")
        lines.append("")
        if e["description"]:
            lines.append(e["description"])
            lines.append("")
        # Other companies in same community
        peers = c.execute(
            """SELECT DISTINCT c.label
               FROM companies c
               JOIN entities e2 ON e2.financial_company_id = c.company_id
               WHERE e2.community = ? AND c.company_id != ?
               ORDER BY c.label LIMIT 8""",
            (e["community"], company_id)
        ).fetchall()
        if peers:
            peer_names = ", ".join(p["label"] for p in peers)
            lines.append(f"In the main industry knowledge graph, {label} is grouped in community {e['community']} "
                         f"alongside peers including {peer_names}. "
                         "These companies share structural relationships in the semiconductor supply chain.")
            lines.append("")
        # Outgoing supply-chain edges
        rels = c.execute(
            """SELECT r.relation, e2.label, e2.entity_type
               FROM relationships r
               JOIN entities e2 ON e2.entity_id = r.target_entity
               WHERE r.source_entity = ?
               ORDER BY r.relation LIMIT 10""",
            (e["entity_id"],)
        ).fetchall()
        if rels:
            by_rel = defaultdict(list)
            for r in rels:
                by_rel[r["relation"]].append(r["label"])
            for rel, targets in by_rel.items():
                lines.append(f"{label} {rel.replace('_', ' ')}: {', '.join(targets[:5])}.")
            lines.append("")

    # Footer
    lines.append("## Source")
    lines.append("")
    lines.append(f"This brief was synthesized from vision-extracted financial statements "
                 f"(see `graphify-financial/{company_id}/`) and from the main industry knowledge "
                 f"graph (`graphify-out/graph.json`). Source PDF: `{co['source_pdf'] or 'n/a'}`.")
    lines.append("")

    return "\n".join(lines)


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    n_written = 0
    n_skipped = 0
    for r in conn.execute("SELECT company_id FROM companies ORDER BY company_id"):
        cid = r["company_id"]
        body = write_brief(conn, cid)
        if not body or len(body) < 200:
            n_skipped += 1
            continue
        path = OUT / f"{cid}.md"
        path.write_text(body, encoding="utf-8")
        n_written += 1
    print(f"Wrote {n_written} briefs to {OUT.relative_to(ROOT)}/")
    print(f"Skipped {n_skipped} (insufficient data)")
    # Print a sample
    sample = OUT / "tsmc.md"
    if sample.exists():
        print(f"\n=== Sample: {sample.name} ===")
        print(sample.read_text()[:2000])
    conn.close()


if __name__ == "__main__":
    main()
