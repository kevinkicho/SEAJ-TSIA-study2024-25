#!/usr/bin/env python3.12
"""Build per-batch manifests for balance-sheet recovery.

For each company missing complete balance sheet (TA + TL + TE), assemble
a manifest entry with the source PDF path. Outputs N batch JSONs in
graphify-financial/balance_sheet_batches/.
"""
from __future__ import annotations
import argparse, json, sqlite3
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=int, default=6)
    args = ap.parse_args()

    c = sqlite3.connect(GF / "financials.db")
    c.row_factory = sqlite3.Row

    # Build target list: each company missing any of TA/TL/TE
    targets = []
    for r in c.execute("SELECT company_id, source_pdf FROM companies ORDER BY company_id"):
        co = r["company_id"]
        src = r["source_pdf"]
        ta = c.execute("SELECT 1 FROM financial_metrics WHERE company_id=? AND canonical_name='total_assets' LIMIT 1", (co,)).fetchone()
        tl = c.execute("SELECT 1 FROM financial_metrics WHERE company_id=? AND canonical_name='total_liabilities' LIMIT 1", (co,)).fetchone()
        te = c.execute("SELECT 1 FROM financial_metrics WHERE company_id=? AND canonical_name='total_equity' LIMIT 1", (co,)).fetchone()
        needs = []
        if not ta: needs.append("total_assets")
        if not tl: needs.append("total_liabilities")
        if not te: needs.append("total_equity")
        if not needs:
            continue
        targets.append({"key": co, "source_pdf": src, "needs": needs,
                        "extraction_json": f"graphify-financial/{co}/{co}_extraction.json"
                                           if co != "tsmc" else f"graphify-financial/tsmc/tsmc_financials.json"})

    out_dir = GF / "balance_sheet_batches"
    out_dir.mkdir(exist_ok=True)
    # Round-robin distribute
    batches = [[] for _ in range(args.batches)]
    for i, t in enumerate(targets):
        batches[i % args.batches].append(t)

    written = []
    for bi, batch in enumerate(batches, start=1):
        if not batch:
            continue
        path = out_dir / f"bs_batch_{bi:02d}.json"
        path.write_text(json.dumps({
            "batch_id": bi,
            "companies": batch,
        }, indent=2, ensure_ascii=False))
        written.append((path, len(batch)))

    print(f"Wrote {len(written)} balance-sheet batch manifests to {out_dir}/")
    for p, n in written:
        print(f"  {p.name}: {n} companies")
    print(f"\nTotal companies needing balance sheet recovery: {len(targets)}")


if __name__ == "__main__":
    main()
