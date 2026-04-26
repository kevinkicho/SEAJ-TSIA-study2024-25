"""
financial_spike.py — pdfplumber-based financial table extractor (weekend spike).

Goal: can we pull revenue / operating income / net income time series
from 5 representative annual reports with simple header-match rules,
without needing an LLM or vision model?

Usage:
    python3 scripts/financial_spike.py

Output: graphify-out/financial_spike.json (one entry per file)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

TARGETS = {
    "tsmc": "2024 Annual Report-E TSMC.pdf",
    "shin_etsu": "Annual-Report-2025 SHINETSU.pdf",
    "advantest": "E_all_IAR2025 ADVANTEST annual report 2025.pdf",
    "ase_holdings": "20250603150724453273521_en ASE holdings annual report 2024.pdf",
    "wpg_holdings": "2024_WPG_annual_report_E.pdf",
}

# Header phrases that identify the table we want (case-insensitive).
INCOME_HEADERS = [
    "consolidated statements of income",
    "consolidated statements of comprehensive income",
    "consolidated statements of operations",
    "consolidated statements of profit or loss",
    "statements of income",
    "income statement",
    "statement of comprehensive income",
]

# Row-label regexes mapped to a canonical metric name.
METRIC_PATTERNS = [
    (re.compile(r"^\s*(net\s+sales|revenues?|net\s+revenue|total\s+revenue|operating\s+revenue)\b", re.I), "revenue"),
    (re.compile(r"^\s*(gross\s+profit)\b", re.I), "gross_profit"),
    (re.compile(r"^\s*(operating\s+income|income\s+from\s+operations|profit\s+from\s+operations)\b", re.I), "operating_income"),
    (re.compile(r"^\s*(net\s+income|profit\s+for\s+the\s+(year|period)|net\s+profit)\b", re.I), "net_income"),
]

# Period-header regex: "2024", "FY2024", "Year ended December 31, 2024", "2024/12/31", etc.
PERIOD_RE = re.compile(r"(?:FY\s*)?(20\d{2})(?:\s*/\s*(\d{1,2})(?:\s*/\s*(\d{1,2}))?)?")

NUMBER_RE = re.compile(r"^-?[\(\s]*[\d,]+(?:\.\d+)?[\)\s]*$")


def parse_number(s: str) -> float | None:
    """Parse '1,234', '(1,234)', '12.3', '-' → float or None."""
    if s is None:
        return None
    t = str(s).strip().replace(",", "").replace("$", "").replace("¥", "")
    if t in ("", "-", "—", "--"):
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    if not re.match(r"^-?\d+(?:\.\d+)?$", t):
        return None
    try:
        v = float(t)
        return -v if neg else v
    except ValueError:
        return None


def find_periods(header_row: list[str]) -> dict[int, str]:
    """Map column-index → period label (e.g. {2: '2024', 3: '2023'})."""
    periods = {}
    for i, cell in enumerate(header_row or []):
        if not cell:
            continue
        m = PERIOD_RE.search(str(cell))
        if m:
            periods[i] = m.group(1)
    return periods


def is_income_table(table: list[list[str]], page_text: str) -> bool:
    """Accept a table if it contains ANY recognizable income-statement metric row
    AND at least one column header looking like a period-year.

    Don't gate on the page-text banner — many financial tables repeat mid-report
    without a matching header phrase on the same page.
    """
    # Need period-year columns.
    has_period = False
    for row in table[:5]:
        if row and find_periods(row):
            has_period = True
            break
    if not has_period:
        return False
    # Need at least one metric row (revenue / operating income / net income / profit).
    for row in table:
        if not row or not row[0]:
            continue
        label = str(row[0]).strip()
        for pat, _metric in METRIC_PATTERNS:
            if pat.search(label):
                return True
    return False


def extract_from_table(table: list[list[str]]) -> dict[str, dict[str, float]]:
    """For a single table, return {metric: {period: value}}."""
    out: dict[str, dict[str, float]] = {}
    # Look through first 5 rows for a header row with period years.
    periods = {}
    for row in table[:5]:
        p = find_periods(row)
        if p:
            periods = p
            break
    if not periods:
        return out

    for row in table:
        if not row or not row[0]:
            continue
        label = str(row[0]).strip()
        for pat, metric in METRIC_PATTERNS:
            if pat.search(label):
                for col, period in periods.items():
                    if col >= len(row):
                        continue
                    val = parse_number(row[col])
                    if val is not None:
                        out.setdefault(metric, {})[period] = val
                break
    return out


def scan_pdf(pdf_path: Path, max_pages: int | None = None) -> dict:
    """Walk every page (unless capped), run table extraction, collect metrics."""
    result = {
        "file": pdf_path.name,
        "pages_scanned": 0,
        "tables_seen": 0,
        "tables_classified_as_income": 0,
        "metrics": {},   # metric → {period: value}
        "hits_by_page": [],
    }
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages) if max_pages is None else min(max_pages, len(pdf.pages))
        result["pages_scanned"] = n
        for i in range(n):
            page = pdf.pages[i]
            try:
                tables = page.extract_tables() or []
            except Exception:
                continue
            result["tables_seen"] += len(tables)
            if not tables:
                continue
            page_text = page.extract_text() or ""
            for t_idx, table in enumerate(tables):
                if not table or not is_income_table(table, page_text):
                    continue
                result["tables_classified_as_income"] += 1
                extracted = extract_from_table(table)
                if extracted:
                    result["hits_by_page"].append({"page": i + 1, "table_idx": t_idx, "metrics": extracted})
                    for metric, series in extracted.items():
                        merged = result["metrics"].setdefault(metric, {})
                        for period, value in series.items():
                            if period not in merged:
                                merged[period] = value
    return result


def main():
    cwd = Path.cwd()
    out = {}
    for company_id, filename in TARGETS.items():
        path = cwd / filename
        if not path.exists():
            out[company_id] = {"error": f"file not found: {filename}"}
            continue
        print(f"scanning {company_id} ({path.stat().st_size / 1e6:.1f} MB)...")
        try:
            out[company_id] = scan_pdf(path, max_pages=None)
        except Exception as exc:
            out[company_id] = {"file": filename, "error": str(exc)}

    output_path = cwd / "graphify-out" / "financial_spike.json"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2))

    print(f"\nwrote {output_path}")
    print("\n=== summary ===")
    for company_id, res in out.items():
        if "error" in res:
            print(f"  {company_id:14s}  ERROR: {res['error']}")
            continue
        metric_count = sum(len(v) for v in res["metrics"].values())
        metrics_label = ", ".join(f"{m}×{len(v)}" for m, v in res["metrics"].items()) or "(nothing)"
        print(
            f"  {company_id:14s}  pages={res['pages_scanned']:3d}  "
            f"tables={res['tables_seen']:3d}  income_tables={res['tables_classified_as_income']}  "
            f"metric_values={metric_count:3d}  → {metrics_label}"
        )


if __name__ == "__main__":
    main()
