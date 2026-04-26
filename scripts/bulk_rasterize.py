#!/usr/bin/env python3.12
"""Bulk PDF page rasterization.

Reads graphify-financial/bulk_page_candidates.json, renders each selected
page as PNG @ 200 DPI via pdftoppm. Writes to graphify-financial/<key>/pages/.
Also writes graphify-financial/bulk_rasterize_summary.json mapping
key → {bucket, source_pdf, pages: [{page, role, png}]}.
"""
from __future__ import annotations
import json, multiprocessing, subprocess, time
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
CANDIDATES = GF / "bulk_page_candidates.json"
OUT = GF / "bulk_rasterize_summary.json"


def rasterize_one(args: tuple[str, str, str, int, str]) -> tuple[str, int, str, str | None]:
    """Render one page; returns (key, page, role, png_filename or None)."""
    key, bucket, pdf_name, page, role = args
    pdf_path = ROOT / bucket / pdf_name
    out_dir = GF / key / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / f"{key}_p{page:03d}"
    # Skip if already rendered
    existing = sorted(out_dir.glob(f"{key}_p{page:03d}-*.png")) + \
               ([prefix.with_suffix(".png")] if prefix.with_suffix(".png").exists() else [])
    if existing:
        return key, page, role, existing[0].name
    try:
        subprocess.run(
            ["nice", "-n", "19", "pdftoppm", "-r", "200",
             "-f", str(page), "-l", str(page), "-png",
             str(pdf_path), str(prefix)],
            check=True, stderr=subprocess.DEVNULL, timeout=120,
        )
    except Exception as e:
        return key, page, role, None
    actuals = sorted(out_dir.glob(f"{key}_p{page:03d}*.png"))
    return key, page, role, actuals[0].name if actuals else None


def main():
    cands = json.loads(CANDIDATES.read_text())
    tasks: list[tuple[str, str, str, int, str]] = []
    for key, info in cands.items():
        bucket = info["bucket"]
        pdf = info["filename"]
        for p in info.get("financial_pages", []):
            tasks.append((key, bucket, pdf, p, "fin"))
        for p in info.get("people_pages", []):
            tasks.append((key, bucket, pdf, p, "people"))

    print(f"Rasterizing {len(tasks)} pages across {len(cands)} PDFs...")
    t0 = time.time()
    n_workers = 4  # pdftoppm @ 200 DPI is CPU/IO heavy; 4 keeps machine responsive
    summary: dict[str, dict] = {}
    for key, info in cands.items():
        summary[key] = {
            "bucket": info["bucket"],
            "source_pdf": info["filename"],
            "total_pages": info["total_pages"],
            "pages": [],
        }
    done = 0
    failed = 0
    with multiprocessing.Pool(n_workers) as pool:
        for key, page, role, png in pool.imap_unordered(rasterize_one, tasks):
            done += 1
            if png:
                summary[key]["pages"].append({"page": page, "role": role, "png": png})
            else:
                failed += 1
            if done % 25 == 0 or done == len(tasks):
                print(f"  [{done:4d}/{len(tasks)}] failed={failed}")
    elapsed = time.time() - t0
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT}  ({elapsed:.1f}s)")
    n_ok = sum(1 for s in summary.values() if s["pages"])
    n_empty = sum(1 for s in summary.values() if not s["pages"])
    print(f"  Companies with at least one PNG: {n_ok}")
    print(f"  Companies with NO pages rasterized: {n_empty}")
    if n_empty:
        for key, s in summary.items():
            if not s["pages"]:
                print(f"    [empty] {key}: {s['source_pdf']}")


if __name__ == "__main__":
    main()
