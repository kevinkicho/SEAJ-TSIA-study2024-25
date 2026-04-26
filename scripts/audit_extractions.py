#!/usr/bin/env python3.12
"""Comprehensive extraction-quality audit.

Runs every extraction JSON through a battery of automated quality checks
and writes a per-page severity report. This is the closest we get to
"verifying" extractions without HITL — flags suspicious patterns for
human review.

Categories:
    blocker  — extraction is unusable (missing currency on a financial table,
               magnitude that can't possibly be right, etc.)
    warning  — extraction is suspect (huge YoY swings, page marked financial
               but empty, canonical-mapping gaps)
    info     — observation only (cross-page divergence likely consolidated/
               parent-only, etc.)

Output: graphify-financial/AUDIT_REPORT.md + audit_findings.json
"""
from __future__ import annotations
import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"

# Known canonical-name suffix patterns to strip before checking presence
import sys; sys.path.insert(0, str(ROOT / "scripts"))
from build_merged_graph import to_canonical
from year_normalizer import normalize as normalize_year


def discover_extractions() -> dict[str, dict]:
    out = {}
    for d in sorted(GF.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "tsmc":
            fin_path = d / "tsmc_financials.json"
            if fin_path.exists():
                fin = json.loads(fin_path.read_text())
                ppl = json.loads((d / "tsmc_people.json").read_text())
                out["tsmc"] = {
                    "company": "TSMC",
                    "currency_default": "TWD",
                    "financial_pages": fin["pages"],
                    "people_pages": ppl["pages"],
                }
            continue
        ext = d / f"{d.name}_extraction.json"
        if ext.exists():
            try:
                out[d.name] = json.loads(ext.read_text())
            except Exception as e:
                out[d.name] = {"_load_error": str(e)}
    return out


def audit_page(key: str, page: dict, ex: dict) -> list[dict]:
    """Return list of finding dicts for one page."""
    findings = []
    page_id = page.get("page_id", "?")
    is_fin = page.get("is_financial_table")
    is_actual = page.get("is_company_actual", True)
    metrics = page.get("metrics", []) or []
    currency = page.get("currency")
    unit = page.get("unit")

    # Blocker: financial table without currency or unit
    if is_fin and not currency:
        findings.append({"severity": "blocker", "page_id": page_id,
                         "issue": "is_financial_table=true but no currency"})
    if is_fin and not unit:
        findings.append({"severity": "blocker", "page_id": page_id,
                         "issue": "is_financial_table=true but no unit"})

    # Warning: financial table marked but empty metrics
    if is_fin and is_actual and not metrics:
        findings.append({"severity": "warning", "page_id": page_id,
                         "issue": "is_financial_table=true and is_company_actual=true but metrics=[]"})

    # Check each metric
    for met in metrics:
        name = met.get("name", "")
        vals = met.get("values") or {}
        if not name:
            findings.append({"severity": "warning", "page_id": page_id,
                             "issue": "metric with no name"})
        # Year format check — uses the central normalizer; only flag if truly unparseable
        for y, v in vals.items():
            yr, _, _ = normalize_year(y) if isinstance(y, str) else (None, None, False)
            if yr is None:
                findings.append({"severity": "warning", "page_id": page_id,
                                 "issue": f"unparseable year label '{y}' on metric '{name}'"})
            if v is not None and not isinstance(v, (int, float)):
                findings.append({"severity": "blocker", "page_id": page_id,
                                 "issue": f"metric '{name}' year {y} value not numeric: {type(v).__name__}"})
        # Plausibility: huge YoY swings (>5x or <0.2x for absolute money values)
        numeric = [(y, v) for y, v in vals.items() if isinstance(v, (int, float)) and v != 0
                   and re.match(r"^\d{4}$", str(y))]
        canon = to_canonical(name)
        if canon and canon not in ("gross_margin_pct", "operating_margin_pct", "eps", "dividend_per_share"):
            sorted_pairs = sorted(numeric, key=lambda x: x[0])
            for (y1, v1), (y2, v2) in zip(sorted_pairs, sorted_pairs[1:]):
                if v1 == 0 or v2 == 0:
                    continue
                ratio = abs(v2 / v1) if v1 else 0
                # Same-sign ratio
                if v1 * v2 > 0 and (ratio > 5 or ratio < 0.2):
                    findings.append({"severity": "info", "page_id": page_id,
                                     "issue": f"YoY swing on '{name}' ({canon}) {y1}={v1} → {y2}={v2}; ratio {ratio:.1f}x"})

    # Magnitude sanity: revenue/total_assets unreasonably small or large
    for met in metrics:
        canon = to_canonical(met.get("name", ""))
        for y, v in (met.get("values") or {}).items():
            if not isinstance(v, (int, float)):
                continue
            if canon == "revenue":
                # Typical large company revenue: $100M to $1T USD-equiv
                # Per-currency unit thresholds (in raw value before normalization)
                if unit == "thousands":
                    abs_native = abs(v) * 1000
                elif unit == "millions":
                    abs_native = abs(v) * 1_000_000
                elif unit == "billions":
                    abs_native = abs(v) * 1_000_000_000
                else:
                    abs_native = abs(v)
                # In native currency, expect roughly $1M USD-equiv at minimum for any company on this list
                # Lower bound: 100k native (extremely conservative)
                if 0 < abs_native < 100_000:
                    findings.append({"severity": "warning", "page_id": page_id,
                                     "issue": f"revenue {v} {currency} {unit} → native magnitude {abs_native:.0f} suspiciously small"})

    return findings


def main():
    extractions = discover_extractions()
    all_findings: list[dict] = []
    by_company: dict[str, list[dict]] = defaultdict(list)
    by_severity: dict[str, int] = defaultdict(int)

    for key, ex in extractions.items():
        if "_load_error" in ex:
            f = {"severity": "blocker", "page_id": "(none)",
                 "issue": f"extraction file unparseable: {ex['_load_error']}"}
            all_findings.append({**f, "company_id": key})
            by_company[key].append(f)
            by_severity["blocker"] += 1
            continue
        for page in ex.get("financial_pages", []):
            for f in audit_page(key, page, ex):
                all_findings.append({**f, "company_id": key})
                by_company[key].append(f)
                by_severity[f["severity"]] += 1

    # Write JSON
    out_json = {
        "summary": {
            "n_companies": len(extractions),
            "n_findings": len(all_findings),
            "by_severity": dict(by_severity),
            "n_companies_clean": sum(1 for k in extractions if not by_company.get(k)),
        },
        "by_company": {k: v for k, v in by_company.items()},
    }
    (GF / "audit_findings.json").write_text(json.dumps(out_json, indent=2, ensure_ascii=False))

    # Write Markdown report
    lines = [
        "# SEAJ TSIA — Extraction Audit Report",
        f"_Generated: 2026-04-25_",
        "",
        f"## Summary",
        f"- Companies audited: **{len(extractions)}**",
        f"- Companies with no findings: **{out_json['summary']['n_companies_clean']}**",
        f"- Total findings: **{len(all_findings)}**",
        f"  - Blockers: {by_severity['blocker']}",
        f"  - Warnings: {by_severity['warning']}",
        f"  - Info: {by_severity['info']}",
        "",
        "## Companies with findings",
        "",
    ]
    for company_id, findings in sorted(by_company.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"### `{company_id}` — {len(findings)} findings")
        # Group by severity
        for sev in ("blocker", "warning", "info"):
            same = [f for f in findings if f["severity"] == sev]
            if not same:
                continue
            lines.append(f"**{sev.title()}** ({len(same)})")
            for f in same[:8]:
                lines.append(f"- `{f['page_id']}`: {f['issue']}")
            if len(same) > 8:
                lines.append(f"- _(+{len(same) - 8} more)_")
            lines.append("")
        lines.append("")

    (GF / "AUDIT_REPORT.md").write_text("\n".join(lines))
    print(f"Audited {len(extractions)} companies; {len(all_findings)} findings")
    print(f"  Blockers: {by_severity['blocker']}, Warnings: {by_severity['warning']}, Info: {by_severity['info']}")
    print(f"  Companies clean: {out_json['summary']['n_companies_clean']}/{len(extractions)}")
    print(f"\nWrote {GF / 'AUDIT_REPORT.md'}")
    print(f"Wrote {GF / 'audit_findings.json'}")


if __name__ == "__main__":
    main()
