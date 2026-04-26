#!/usr/bin/env python3.12
"""Cross-validate extracted financials per company.

Runs a battery of internal-consistency checks (subtotals reconcile,
ratios computed from absolutes match printed percentages) and cross-page
duplicate-value reconciliation. Writes a single consolidated report.
"""
import json
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
COMPANIES = ["wpg", "umc", "amat", "medipal", "alcor", "itri", "ase", "vis", "egis"]

# Subtotal rules: for a given page object, given a set of metric names,
# verify e.g. (a + b == c).  Each rule is (rule_name, lambda(metrics_dict, year) -> (expected, computed) | None).
def gp_minus_opex(m, y):
    keys_gp = ["Gross profit", "Gross profit (consolidated)", "Gross operating profit", "Gross profit from operations"]
    keys_opex = ["Operating expenses", "Operating expenses (consolidated)"]
    keys_oi = ["Operating income", "Operating income (consolidated)", "Profit from operations", "Net operating profit", "Operating profit (loss)"]
    gp = next((m[k][y] for k in keys_gp if k in m and y in m[k]), None)
    ox = next((m[k][y] for k in keys_opex if k in m and y in m[k]), None)
    oi = next((m[k][y] for k in keys_oi if k in m and y in m[k]), None)
    if None in (gp, ox, oi): return None
    return ("GP - OpEx = OpInc", oi, gp - ox)

def pretax_minus_tax(m, y):
    keys_pt = ["Income before income tax", "Income before income tax (consolidated)", "Income from continuing operations before income tax", "Profit before income tax", "Pre-tax net loss", "Pre-tax net profit (loss)", "Pre-tax net loss (loss)", "Income before Income Tax"]
    keys_tax = ["Income tax expense", "Income tax expense (consolidated)", "Income Tax Expenses", "Income tax benefit"]
    keys_ni = ["Net income", "Net income (consolidated)", "Net Profit", "Net loss", "Net profit (loss) for the current period", "After-tax net profit (loss)", "Net Income"]
    pt = next((m[k][y] for k in keys_pt if k in m and y in m[k]), None)
    tx = next((m[k][y] for k in keys_tax if k in m and y in m[k]), None)
    ni = next((m[k][y] for k in keys_ni if k in m and y in m[k]), None)
    if None in (pt, tx, ni): return None
    # Handle sign: tax may be reported as positive (expense) or negative depending on convention
    # Common: NI = PT - Tax (when tax is positive expense) OR NI = PT + Tax (when tax was already negative)
    if abs((pt - tx) - ni) <= max(abs(ni)*0.001, 1):
        return ("PreTax - Tax = NetInc", ni, pt - tx)
    elif abs((pt + tx) - ni) <= max(abs(ni)*0.001, 1):
        return ("PreTax + Tax(negative) = NetInc", ni, pt + tx)
    return ("PreTax - Tax = NetInc", ni, pt - tx)

def assets_eq_liab_plus_eq(m, y):
    keys_ta = ["Total assets", "Total Assets"]
    keys_tl = ["Total liabilities", "Total Liabilities"]
    keys_te = ["Total equity", "Total Equity", "Total shareholders' equity"]
    ta = next((m[k][y] for k in keys_ta if k in m and y in m[k]), None)
    tl = next((m[k][y] for k in keys_tl if k in m and y in m[k]), None)
    te = next((m[k][y] for k in keys_te if k in m and y in m[k]), None)
    if None in (ta, tl, te): return None
    return ("Assets = Liab + Equity", ta, tl + te)

def gm_pct_check(m, y):
    keys_gp = ["Gross profit", "Gross profit (consolidated)", "Gross Profit"]
    keys_rev = ["Net revenue", "Net revenue (consolidated)", "Operating revenues", "Operating revenue", "Net Revenue", "Operating Revenue"]
    keys_pct = ["Gross profit margin (%)", "Gross profit margin (%) (consolidated)", "Gross margin (%)"]
    gp = next((m[k][y] for k in keys_gp if k in m and y in m[k]), None)
    rev = next((m[k][y] for k in keys_rev if k in m and y in m[k]), None)
    pct = next((m[k][y] for k in keys_pct if k in m and y in m[k]), None)
    if None in (gp, rev, pct): return None
    return (f"GM% computed (GP/Rev*100)", pct, round(100 * gp / rev, 1))

RULES = [gp_minus_opex, pretax_minus_tax, assets_eq_liab_plus_eq, gm_pct_check]

def collect_metrics(extraction):
    """Flatten financial_pages into per-page metric dicts."""
    out = []
    for page in extraction.get("financial_pages", []):
        if not page.get("is_financial_table"):
            continue
        m = {met["name"]: met.get("values", {}) for met in page.get("metrics", [])}
        out.append((page["page_id"], m))
    return out

def cross_page_consistency(pages):
    """Find any metric name that appears on >1 page; flag mismatches."""
    seen = {}
    flags = []
    for pid, m in pages:
        for name, vals in m.items():
            for y, v in vals.items():
                k = (name, y)
                if k in seen:
                    other_pid, other_v = seen[k]
                    if v is None or other_v is None:
                        continue
                    if abs(v - other_v) > max(abs(v)*0.001, 1) + 0.5:
                        flags.append({"metric": name, "year": y, "page1": other_pid, "val1": other_v, "page2": pid, "val2": v})
                else:
                    seen[k] = (pid, v)
    return flags

def main():
    out = {}
    summary_lines = ["# Cross-Validation Summary — 9 companies (2026-04-24)", ""]
    summary_lines.append("| Company | Internal checks pass | Cross-page conflicts | Years | People |")
    summary_lines.append("|---|---|---|---|---|")
    for key in COMPANIES:
        path = ROOT / "graphify-financial" / key / f"{key}_extraction.json"
        if not path.exists():
            print(f"[skip] {key}: no extraction"); continue
        ex = json.loads(path.read_text())
        pages = collect_metrics(ex)
        # Run all subtotal rules for each page
        results = []
        for pid, m in pages:
            years = set()
            for vals in m.values():
                years.update(vals.keys())
            for y in years:
                for rule in RULES:
                    r = rule(m, y)
                    if r is None: continue
                    label, expected, computed = r
                    if expected == 0 and computed == 0:
                        ok = True
                    else:
                        # Allow 0.5% tolerance for rounding
                        tol = max(abs(expected) * 0.005, 1)
                        ok = abs(expected - computed) <= tol
                    results.append({"page": pid, "year": y, "rule": label, "expected": expected, "computed": computed, "pass": ok})
        cross = cross_page_consistency(pages)
        passed = sum(1 for r in results if r['pass'])
        total = len(results)
        years_covered = sorted({r['year'] for r in results}) if results else []
        people_count = sum(len(p.get("people", [])) for p in ex.get("people_pages", []))
        out[key] = {"checks": results, "cross_page_conflicts": cross, "passed": passed, "total": total, "years": years_covered, "people": people_count}
        summary_lines.append(f"| **{key}** ({ex.get('company','')[:30]}) | {passed}/{total} | {len(cross)} | {','.join(years_covered)} | {people_count} |")
        print(f"  {key}: {passed}/{total} subtotal checks; {len(cross)} cross-page conflicts; years {years_covered}; people {people_count}")
    summary_lines.append("")
    summary_lines.append("## Notes")
    summary_lines.append("- Internal checks: GrossProfit−OpEx=OpIncome; PreTax−Tax=NetIncome; Assets=Liab+Equity; GM% reconstruction.")
    summary_lines.append("- Cross-page conflicts: same metric+year reported on multiple pages with diverging values (>0.1% diff).")
    summary_lines.append("- Where a check returns None, the metric pair was not present on the page (skipped, not failed).")
    (ROOT / "graphify-financial" / "validation_consolidated.json").write_text(json.dumps(out, indent=2))
    (ROOT / "graphify-financial" / "VALIDATION_SUMMARY.md").write_text("\n".join(summary_lines))
    print("\nWrote graphify-financial/validation_consolidated.json")
    print("Wrote graphify-financial/VALIDATION_SUMMARY.md")

if __name__ == "__main__":
    main()
