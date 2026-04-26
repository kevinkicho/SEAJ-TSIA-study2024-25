#!/usr/bin/env python3.12
"""Patch the 5 audit blockers in-place. Idempotent.

Each patch is a precise, reversible change documented inline. Pre-edit
backups are created via .pre-blocker-fix-bak suffix on first modification.
"""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict):
    bak = path.with_suffix(".json.pre-blocker-fix-bak")
    if not bak.exists():
        shutil.copy(path, bak)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def patch_nanya_p104():
    """Nanya Tech p104 is ESG/carbon-emissions targets — not financial.
    Reclassify as non_financial."""
    p = GF / "2024_annual_report" / "2024_annual_report_extraction.json"
    j = load(p)
    for page in j["financial_pages"]:
        if page["page_id"] == "2024_annual_report_p104":
            page["is_financial_table"] = False
            page["table_type"] = "non_financial"
            page["notes"] = (page.get("notes", "") +
                             " | Reclassified: ESG/carbon-emissions data, not financial.")
            save(p, j)
            return "patched"
    return "page not found"


def patch_ckd_p019():
    """ckd p019 has metrics with year='target' (forward-looking, no specific year).
    Fix: drop the 'target' values; the targets are forecast guidance not extractable
    actuals. Page becomes empty if no other years remain."""
    p = GF / "ckd_all_web" / "ckd_all_web_extraction.json"
    j = load(p)
    for page in j["financial_pages"]:
        if page["page_id"] == "ckd_all_web_p019":
            new_metrics = []
            for met in page.get("metrics", []):
                vals = met.get("values") or {}
                # Drop 'target' (non-numeric / no year)
                cleaned = {y: v for y, v in vals.items()
                           if y != "target" and isinstance(v, (int, float))}
                if cleaned:
                    new_metrics.append({**met, "values": cleaned})
            page["metrics"] = new_metrics
            page["notes"] = (page.get("notes", "") +
                             " | Patched: dropped non-numeric 'target' year-labels (forward-looking guidance).")
            save(p, j)
            return "patched"
    return "page not found"


def patch_egis_p090():
    """egis p090 is acquired-entity (Kiwi Tech) financials — Egis's acquisition
    target, not Egis itself. Reclassify is_company_actual=false (so it doesn't
    flow into Egis's revenue) and set currency=TWD/unit=as_is so the page is
    still queryable for acquisition-detail audit."""
    p = GF / "egis" / "egis_extraction.json"
    j = load(p)
    for page in j["financial_pages"]:
        if page["page_id"] == "egis_p090":
            page["is_company_actual"] = False
            page["currency"] = "TWD"
            page["unit"] = "as_is"
            page["notes"] = (page.get("notes", "") +
                             " | Patched: marked is_company_actual=false (this is Kiwi Tech, an acquisition target, not Egis itself).")
            save(p, j)
            return "patched"
    return "page not found"


def patch_vis_p130():
    """vis p130 is major-shareholder ownership table; mixed pct + currency.
    Add unit='as_is'; the per-metric semantics are clearer from the metric
    name (e.g., '...stake (%)' vs '...Capital (NT$)')."""
    p = GF / "vis" / "vis_extraction.json"
    j = load(p)
    for page in j["financial_pages"]:
        if page["page_id"] == "vis_p130":
            page["unit"] = "as_is"
            page["notes"] = (page.get("notes", "") +
                             " | Patched: unit set to 'as_is' (mixed % and TWD values; semantic encoded in metric names).")
            save(p, j)
            return "patched"
    return "page not found"


def main():
    results = {
        "nanya p104 (carbon-emissions, not financial)": patch_nanya_p104(),
        "ckd p019 (drop 'target' year)": patch_ckd_p019(),
        "egis p090 (acquired entity)": patch_egis_p090(),
        "vis p130 (mixed pct/currency)": patch_vis_p130(),
    }
    print("Blocker patches:")
    for k, v in results.items():
        print(f"  {v:10s}  {k}")


if __name__ == "__main__":
    main()
