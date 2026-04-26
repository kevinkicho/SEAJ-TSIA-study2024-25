"""
marker_extract_financials.py — parse Marker JSON output, find income-statement
tables, emit structured financial metrics as {company, metric, period, value,
currency, unit, source_file, source_page} tuples.

Usage:
    python3 scripts/marker_extract_financials.py
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

TARGETS = {
    "tsmc":         "2024 Annual Report-E TSMC",
    "shin_etsu":    "Annual-Report-2025 SHINETSU",
    "advantest":    "E_all_IAR2025 ADVANTEST annual report 2025",
    "ase_holdings": "20250603150724453273521_en ASE holdings annual report 2024",
    "wpg_holdings": "2024_WPG_annual_report_E",
}

PERIOD_RE = re.compile(r"(?:FY\s*)?(?:3\s*/\s*)?(20\d{2})(?!\s*-)")
FORECAST_RE = re.compile(r"\(\s*F\s*\)|forecast|estimate|projection|target", re.I)

METRIC_PATTERNS = [
    (re.compile(r"^\s*(net\s+sales|operating\s+revenue|revenues?|net\s+revenue|total\s+revenue)\b", re.I), "revenue"),
    (re.compile(r"^\s*(gross\s+profit)\b", re.I), "gross_profit"),
    (re.compile(r"^\s*(operating\s+income|income\s+from\s+operations|profit\s+from\s+operations)\b", re.I), "operating_income"),
    (re.compile(r"^\s*(ordinary\s+income)\b", re.I), "ordinary_income"),
    (re.compile(r"^\s*(profit\s+before\s+income\s+tax|income\s+before\s+tax)\b", re.I), "pretax_income"),
    (re.compile(r"^\s*(net\s+(?:income|profit)|profit\s+for\s+the\s+(?:year|period)|net\s+profit)\b", re.I), "net_income"),
    (re.compile(r"^\s*(total\s+assets)\b", re.I), "total_assets"),
    (re.compile(r"^\s*(total\s+(?:stockholders|shareholders)?'?\s*equity|total\s+equity|net\s+assets)\b", re.I), "total_equity"),
    (re.compile(r"^\s*(cash\s+flows?\s+from\s+operating\s+activities|operating\s+cash\s+flow)\b", re.I), "operating_cash_flow"),
    (re.compile(r"^\s*(capital\s+expenditures?|capex)\b", re.I), "capex"),
    (re.compile(r"^\s*(r\s*&\s*d\s+(?:costs?|expenses?|expenditures?))\b", re.I), "rd_expense"),
    (re.compile(r"^\s*(depreciation\s+and\s+amortization|d\s*&\s*a)\b", re.I), "depreciation_amortization"),
]

CURRENCY_PATTERNS = [
    (re.compile(r"¥|\byen\b", re.I),   "JPY"),
    (re.compile(r"NT\s*\$|NTD", re.I), "TWD"),
    (re.compile(r"US\s*\$|USD|\bdollars?\b", re.I), "USD"),
    (re.compile(r"€|EUR|\beuros?\b", re.I), "EUR"),
]

UNIT_PATTERNS = [
    (re.compile(r"thousands?", re.I),                     1_000),
    (re.compile(r"millions?|mn\b", re.I),                 1_000_000),
    (re.compile(r"billions?|bn\b", re.I),                 1_000_000_000),
    (re.compile(r"hundred\s+millions?|百万", re.I),       100_000_000),
]


class TP(HTMLParser):
    def __init__(self): super().__init__(); self.rows=[]; self.cur=[]; self.cell=[]
    def handle_starttag(self, tag, attrs):
        if tag == "tr": self.cur = []
        if tag in ("td", "th"): self.cell = []
    def handle_endtag(self, tag):
        if tag in ("td", "th"): self.cur.append("".join(self.cell).strip())
        if tag == "tr" and self.cur: self.rows.append(self.cur)
    def handle_data(self, data): self.cell.append(data)


def parse_html(html): p = TP(); p.feed(html); return p.rows


def iter_blocks(node, page=0):
    if node.get("block_type") == "Page":
        page = int(node.get("id", "/page/0/").split("/")[2])
    yield page, node
    for ch in node.get("children", []) or []:
        yield from iter_blocks(ch, page)


def parse_number(s):
    if s is None: return None
    t = str(s).strip().replace(",", "").replace("$", "").replace("¥", "").replace("NT", "")
    if t in ("", "-", "—", "--", "N/A"): return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    if not re.match(r"^-?\d+(?:\.\d+)?$", t): return None
    try:
        v = float(t)
        return -v if neg else v
    except ValueError:
        return None


def find_period_cols(header_rows, all_headers_text):
    """Find columns with period years. Returns {col_idx: (period, is_forecast)}."""
    periods = {}
    for row in header_rows:
        for i, cell in enumerate(row):
            if not cell: continue
            is_fcst = bool(FORECAST_RE.search(cell))
            m = PERIOD_RE.search(str(cell))
            if m:
                year = int(m.group(1))
                periods[i] = (str(year), is_fcst)
    return periods


def detect_currency_unit(context_text):
    currency = None
    for pat, c in CURRENCY_PATTERNS:
        if pat.search(context_text):
            currency = c
            break
    unit = 1
    unit_label = "raw"
    for pat, mult in UNIT_PATTERNS:
        if pat.search(context_text):
            unit = mult
            unit_label = pat.pattern.split("|")[0].replace("s?", "s").replace("\\b", "")
            break
    return currency, unit, unit_label


def extract_from_table(rows, context_text):
    """Return list of tuples: (metric, period, value, is_forecast)."""
    if len(rows) < 2: return []
    # Scan first 5 rows for period header
    periods = find_period_cols(rows[:5], context_text)
    if not periods: return []
    out = []
    for row in rows:
        if not row or not row[0]: continue
        label = str(row[0]).strip()
        for pat, metric in METRIC_PATTERNS:
            if pat.search(label):
                for col, (period, is_fcst) in periods.items():
                    if col >= len(row): continue
                    val = parse_number(row[col])
                    if val is not None:
                        out.append((metric, period, val, is_fcst))
                break
    return out


def scan(marker_json_path: Path, company_id: str, source_file: str):
    d = json.load(open(marker_json_path))
    blocks = list(iter_blocks(d))
    # Build per-page text for context
    page_text = {}
    for page, block in blocks:
        if block.get("block_type") in ("Text", "SectionHeader", "Caption"):
            txt = block.get("html", "") or ""
            # Strip tags naïvely
            stripped = re.sub(r"<[^>]+>", " ", txt)
            page_text.setdefault(page, []).append(stripped)

    tuples = []
    forecast_count = 0
    tables_seen = 0
    tables_with_metrics = 0
    for page, block in blocks:
        if block.get("block_type") != "Table": continue
        tables_seen += 1
        html = block.get("html", "") or ""
        rows = parse_html(html)
        context = " ".join(page_text.get(page, []))[:2000] + " " + html[:2000]
        extracted = extract_from_table(rows, context)
        if not extracted: continue
        tables_with_metrics += 1
        currency, unit, unit_label = detect_currency_unit(context)
        for metric, period, value, is_fcst in extracted:
            if is_fcst:
                forecast_count += 1
                continue   # skip forecasts — they're market data, not actuals
            tuples.append({
                "company_id": company_id,
                "metric": metric,
                "period": period,
                "value": value,
                "currency": currency,
                "unit_multiplier": unit,
                "unit_label": unit_label,
                "source_file": source_file,
                "source_page": page + 1,
            })
    return {
        "company_id": company_id,
        "source_file": source_file,
        "tables_seen": tables_seen,
        "tables_with_metrics": tables_with_metrics,
        "forecasts_rejected": forecast_count,
        "metrics": tuples,
    }


def main():
    cwd = Path.cwd()
    out = {}
    for cid, dirname in TARGETS.items():
        jpath = cwd / "graphify-marker" / dirname / f"{dirname}.json"
        if not jpath.exists():
            out[cid] = {"error": f"marker output not found: {jpath}"}
            continue
        out[cid] = scan(jpath, cid, dirname + ".pdf")

    output = cwd / "graphify-out" / "marker_financials.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(out, indent=2))
    print(f"wrote {output}\n")
    print("=== summary ===")
    for cid, res in out.items():
        if "error" in res:
            print(f"  {cid:14s}  ERROR: {res['error']}")
            continue
        unique_pairs = {(m["metric"], m["period"]) for m in res["metrics"]}
        by_metric = {}
        for m in res["metrics"]:
            by_metric.setdefault(m["metric"], set()).add(m["period"])
        mx = ", ".join(f"{k}×{len(v)}" for k, v in sorted(by_metric.items()))
        print(
            f"  {cid:14s}  tables={res['tables_seen']:4d}  hit={res['tables_with_metrics']:3d}  "
            f"rejected_forecasts={res['forecasts_rejected']:3d}  metrics={len(res['metrics']):4d}  "
            f"unique(metric,period)={len(unique_pairs):3d}"
        )
        if by_metric:
            print(f"    {mx}")


if __name__ == "__main__":
    main()
