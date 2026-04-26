#!/usr/bin/env python3.12
"""Bulk financial-page detection across the bucket folders.

Processes annual_reports/, quarterly_reports/, investor_presentations/.
Skips the 10 already-processed companies. Multiprocessing-parallel.

Output: graphify-financial/bulk_page_candidates.json
"""
from __future__ import annotations
import json, multiprocessing, re, subprocess, sys, time
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
GF = ROOT / "graphify-financial"
OUT = GF / "bulk_page_candidates.json"

BUCKETS_TO_PROCESS = ["annual_reports", "quarterly_reports", "investor_presentations"]

# These 10 already have JSON extractions — skip
ALREADY_PROCESSED_FILENAMES = {
    "2024 Annual Report-E TSMC.pdf",
    "2024_WPG_annual_report_E.pdf",
    "2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf",
    "2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf",
    "00 MEDIPAL integrated report 2025.pdf",
    "2024_AnnualReport_EN.pdf",
    "2024_Annual Report ITRI taiwan.pdf",
    "20250603150724453273521_en ASE holdings annual report 2024.pdf",
    "20250506232053383995188_en VIS annual report 2025.pdf",
    "EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf",
}

STRONG_FIN = re.compile(
    r"(STATEMENTS?\s+OF\s+(COMPREHENSIVE\s+)?INCOME|"
    r"CONSOLIDATED\s+STATEMENTS?\s+OF\s+(INCOME|OPERATIONS|COMPREHENSIVE)|"
    r"FIVE[-\s]YEAR\s+(FINANCIAL|SUMMARY|HIGHLIGHTS)|"
    r"TEN[-\s]YEAR\s+SUMMARY|"
    r"FINANCIAL\s+HIGHLIGHTS|"
    r"FINANCIAL\s+SUMMARY|"
    r"CONSOLIDATED\s+BALANCE\s+SHEETS?|"
    r"BALANCE\s+SHEETS?\s+\(consolidated\)|"
    r"Income\s+Statement|"
    r"Selected\s+Financial\s+Data|"
    r"Operating\s+Results)",
    re.IGNORECASE | re.MULTILINE,
)

WEAK_FIN = re.compile(
    r"(Net\s+revenue|Net\s+sales|Operating\s+income|EARNINGS\s+PER\s+SHARE|"
    r"Gross\s+profit|Total\s+assets|Operating\s+expenses|Income\s+tax\s+expense|"
    r"Cost\s+of\s+revenue|Cash\s+flows?\s+from|Total\s+equity|Total\s+liabilities|"
    r"Net\s+income|Diluted\s+earnings|Operating\s+revenues?)",
    re.IGNORECASE,
)

REJECT = re.compile(
    r"(Source:\s*Gartner|Source:\s*IDC|Source:\s*IC\s*Insights|Source:\s*TrendForce|"
    r"Estimated\s+Revenue\s+of\s+the\s+Global|Industry\s+Forecast|Market\s+Forecast|"
    r"\(F\)|\(forecast\)|industry\s+overview)",
    re.IGNORECASE,
)

PEOPLE_STRONG = re.compile(
    r"(BOARD\s+OF\s+DIRECTORS?|"
    r"INFORMATION\s+REGARDING\s+(BOARD|MANAGEMENT|DIRECTORS)|"
    r"EXECUTIVE\s+OFFICERS?|"
    r"DIRECTORS?\s+AND\s+EXECUTIVE|"
    r"COMPENSATION\s+OF\s+(DIRECTORS|MANAGEMENT|CEO)|"
    r"Officers\s+and\s+Directors|"
    r"Members?\s+of\s+the\s+Board)",
    re.IGNORECASE | re.MULTILINE,
)
PEOPLE_WEAK = re.compile(
    r"(Senior\s+Vice\s+President|Independent\s+Director|Chief\s+Financial\s+Officer|"
    r"Chief\s+Operating\s+Officer|Chairman\s+of\s+the\s+Board|Audit\s+Committee\s+Chair|"
    r"President\s+and\s+CEO|President\s+&\s+CEO|Director\s+and\s+CEO)",
    re.IGNORECASE,
)


def filename_to_key(fn: str) -> str:
    """Generate a stable per-PDF directory key. Uses file stem, normalized."""
    stem = Path(fn).stem
    # Strip common noise
    stem = re.sub(r"[A-Za-z0-9]{8,}_+", "", stem)  # long hex-ish tokens
    stem = re.sub(r"\s+\d{6,}.*$", "", stem)
    stem = re.sub(r"[^A-Za-z0-9_]+", "_", stem.lower())
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem[:60] or "unknown"


def get_pages(pdf_path: Path) -> int:
    try:
        info = subprocess.check_output(
            ["pdfinfo", str(pdf_path)], stderr=subprocess.DEVNULL, timeout=30
        ).decode(errors="ignore")
        m = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0


def page_text(pdf_path: Path, page: int) -> str:
    try:
        return subprocess.check_output(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
            stderr=subprocess.DEVNULL, timeout=20,
        ).decode(errors="ignore")
    except Exception:
        return ""


def score_financial(text: str) -> int:
    if REJECT.search(text):
        if not STRONG_FIN.search(text):
            return -1
    s = len(STRONG_FIN.findall(text)) * 3 + len(WEAK_FIN.findall(text))
    return s


def score_people(text: str) -> int:
    return len(PEOPLE_STRONG.findall(text)) * 3 + len(PEOPLE_WEAK.findall(text))


def find_runs(pages: list[int], gap: int = 2) -> list[tuple[int, int]]:
    if not pages:
        return []
    pages = sorted(pages)
    runs = [[pages[0], pages[0]]]
    for p in pages[1:]:
        if p - runs[-1][1] <= gap:
            runs[-1][1] = p
        else:
            runs.append([p, p])
    return [tuple(r) for r in runs]


def process_pdf(args: tuple[str, str]) -> dict:
    """Worker: returns the per-PDF dict."""
    bucket, fname = args
    pdf_path = ROOT / bucket / fname
    n = get_pages(pdf_path)
    fin_hits, ppl_hits = {}, {}
    # Limit page scans for very long PDFs (HCL has 423, CXL has 1276 etc.) — cap at 250
    scan_limit = min(n, 250)
    for p in range(1, scan_limit + 1):
        text = page_text(pdf_path, p)
        if not text.strip():
            continue
        fs = score_financial(text)
        ps = score_people(text)
        if fs >= 3:
            fin_hits[p] = fs
        if ps >= 3:
            ppl_hits[p] = ps
    # Caps to control vision-extraction cost: top 12 financial, top 5 people
    fin_top = sorted(fin_hits.items(), key=lambda x: -x[1])[:12]
    ppl_top = sorted(ppl_hits.items(), key=lambda x: -x[1])[:5]
    fin_pages = sorted(p for p, _ in fin_top)
    ppl_pages = sorted(p for p, _ in ppl_top)
    return {
        "key": filename_to_key(fname),
        "filename": fname,
        "bucket": bucket,
        "total_pages": n,
        "scanned_pages": scan_limit,
        "financial_pages": fin_pages,
        "financial_runs": find_runs(fin_pages),
        "people_pages": ppl_pages,
        "people_runs": find_runs(ppl_pages),
    }


def main():
    tasks: list[tuple[str, str]] = []
    for bucket in BUCKETS_TO_PROCESS:
        bdir = ROOT / bucket
        if not bdir.exists():
            continue
        for pdf in bdir.glob("*.pdf"):
            if pdf.name in ALREADY_PROCESSED_FILENAMES:
                continue
            tasks.append((bucket, pdf.name))

    print(f"Scanning {len(tasks)} PDFs across {len(BUCKETS_TO_PROCESS)} buckets...")
    t0 = time.time()
    n_workers = max(1, min(8, len(tasks)))
    results: list[dict] = []
    with multiprocessing.Pool(n_workers) as pool:
        for i, r in enumerate(pool.imap_unordered(process_pdf, tasks), start=1):
            results.append(r)
            print(f"  [{i:3d}/{len(tasks)}] {r['bucket']}/{r['filename'][:60]:60s} "
                  f"  {r['total_pages']:4d}pp -> fin={len(r['financial_pages'])}, "
                  f"ppl={len(r['people_pages'])}")

    # Detect key collisions
    by_key: dict[str, list[str]] = {}
    for r in results:
        by_key.setdefault(r["key"], []).append(r["filename"])
    collisions = {k: v for k, v in by_key.items() if len(v) > 1}
    if collisions:
        print("\n[warn] key collisions — disambiguating with index suffix:")
        for k, files in collisions.items():
            for i, fn in enumerate(sorted(files)):
                if i == 0: continue
                for r in results:
                    if r["filename"] == fn:
                        r["key"] = f"{k}_{i+1}"
                        print(f"   {fn}  ->  {r['key']}")

    # Group by key for output
    out = {r["key"]: r for r in results}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    elapsed = time.time() - t0
    print(f"\nWrote {OUT}  ({elapsed:.1f}s, {n_workers} workers)")
    print(f"  PDFs: {len(out)}")
    no_fin = [r for r in results if not r["financial_pages"]]
    print(f"  No financial pages found: {len(no_fin)}")
    for r in no_fin:
        print(f"    [no-fin] {r['filename']}")


if __name__ == "__main__":
    main()
