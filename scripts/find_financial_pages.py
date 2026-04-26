#!/usr/bin/env python3.12
"""Page-finder for the financial-extension pipeline.

For each PDF in the list, scans every page once and emits two candidate sets:
  - financial pages (income statement / 5-yr summary / financial highlights)
  - people pages (board / executive listings)

Output: graphify-financial/page_candidates.json
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
OUT = ROOT / "graphify-financial" / "page_candidates.json"

PDFS = [
    ("wpg",       "2024_WPG_annual_report_E.pdf"),
    ("umc",       "2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf"),
    ("amat",      "2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf"),
    ("medipal",   "00 MEDIPAL integrated report 2025.pdf"),
    ("alcor",     "2024_AnnualReport_EN.pdf"),
    ("itri",      "2024_Annual Report ITRI taiwan.pdf"),
    ("ase",       "20250603150724453273521_en ASE holdings annual report 2024.pdf"),
    ("vis",       "20250506232053383995188_en VIS annual report 2025.pdf"),
    ("egis",      "EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf"),
]

# Financial markers: prioritize "statement of comprehensive income" / "5-year financial" / "financial highlights"
# We weight markers — page must hit a strong marker to be a real income statement
STRONG_FIN = re.compile(
    r"(STATEMENTS?\s+OF\s+(COMPREHENSIVE\s+)?INCOME|"
    r"CONSOLIDATED\s+STATEMENTS?\s+OF\s+(INCOME|OPERATIONS|COMPREHENSIVE)|"
    r"FIVE[-\s]YEAR\s+(FINANCIAL|SUMMARY)|"
    r"TEN[-\s]YEAR\s+SUMMARY|"
    r"FINANCIAL\s+HIGHLIGHTS|"
    r"CONSOLIDATED\s+BALANCE\s+SHEETS?|"
    r"Income\s+Statement|"
    r"Selected\s+Financial\s+Data)",
    re.IGNORECASE | re.MULTILINE,
)

# Weaker markers (need to co-occur with at least one strong marker or another weak marker)
WEAK_FIN = re.compile(
    r"(Net\s+revenue|Net\s+sales|Operating\s+income|EARNINGS\s+PER\s+SHARE|"
    r"Gross\s+profit|Total\s+assets|Operating\s+expenses|Income\s+tax\s+expense|"
    r"Cost\s+of\s+revenue|Cash\s+flows?\s+from)",
    re.IGNORECASE,
)

# Reject markers: forecast / 3rd-party / market sizing
REJECT = re.compile(
    r"(Source:\s*Gartner|Source:\s*IDC|Source:\s*IC\s*Insights|Source:\s*TrendForce|"
    r"Estimated\s+Revenue\s+of\s+the\s+Global|Industry\s+Forecast|Market\s+Forecast|"
    r"\(F\)|\(forecast\)|industry\s+overview)",
    re.IGNORECASE,
)

# People markers: board, exec, committees
PEOPLE_STRONG = re.compile(
    r"(BOARD\s+OF\s+DIRECTORS?\s*$|"
    r"INFORMATION\s+REGARDING\s+(BOARD|MANAGEMENT|DIRECTORS)|"
    r"EXECUTIVE\s+OFFICERS?|"
    r"DIRECTORS?\s+AND\s+EXECUTIVE|"
    r"COMPENSATION\s+OF\s+(DIRECTORS|MANAGEMENT|CEO))",
    re.IGNORECASE | re.MULTILINE,
)
PEOPLE_WEAK = re.compile(
    r"(Senior\s+Vice\s+President|Independent\s+Director|Chief\s+Financial\s+Officer|"
    r"Chief\s+Operating\s+Officer|Chairman\s+of\s+the\s+Board|Audit\s+Committee\s+Chair)",
    re.IGNORECASE,
)


def get_pages(pdf_path: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(pdf_path)], stderr=subprocess.DEVNULL).decode()
    m = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    return int(m.group(1))


def page_text(pdf_path: Path, page: int) -> str:
    try:
        return subprocess.check_output(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
            stderr=subprocess.DEVNULL,
        ).decode(errors="ignore")
    except subprocess.CalledProcessError:
        return ""


def score_financial(text: str) -> tuple[int, list[str]]:
    """Return (score, hit_phrases). 0 = not financial. Higher = more confident."""
    if REJECT.search(text):
        # Still allow if also strong-fin matches (the page mixes content)
        strong = STRONG_FIN.findall(text)
        if not strong:
            return -1, [text[:80]]  # explicitly rejected
    strong = STRONG_FIN.findall(text)
    weak = WEAK_FIN.findall(text)
    score = len(strong) * 3 + len(weak)
    phrases = list({(s if isinstance(s, str) else s[0]) for s in strong}) + list({(w if isinstance(w, str) else w[0]) for w in weak})[:3]
    return score, phrases[:5]


def score_people(text: str) -> tuple[int, list[str]]:
    strong = PEOPLE_STRONG.findall(text)
    weak = PEOPLE_WEAK.findall(text)
    score = len(strong) * 3 + len(weak)
    phrases = list({(s if isinstance(s, str) else s[0]) for s in strong}) + list({(w if isinstance(w, str) else w[0]) for w in weak})[:3]
    return score, phrases[:5]


def find_runs(pages: list[int], gap: int = 2) -> list[tuple[int, int]]:
    """Cluster contiguous pages: list of (first, last)."""
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


def process(pdf_path: Path, key: str) -> dict:
    n = get_pages(pdf_path)
    fin_hits, ppl_hits = {}, {}
    for p in range(1, n + 1):
        text = page_text(pdf_path, p)
        if not text.strip():
            continue
        fin_score, fin_phrases = score_financial(text)
        ppl_score, ppl_phrases = score_people(text)
        if fin_score >= 3:
            fin_hits[p] = {"score": fin_score, "phrases": fin_phrases}
        if ppl_score >= 3:
            ppl_hits[p] = {"score": ppl_score, "phrases": ppl_phrases}

    # Pick top financial pages: highest score, but prefer no more than ~12 per PDF
    fin_top = sorted(fin_hits.items(), key=lambda x: -x[1]["score"])[:12]
    fin_pages = sorted(p for p, _ in fin_top)
    # Pick top people pages: top ~5
    ppl_top = sorted(ppl_hits.items(), key=lambda x: -x[1]["score"])[:5]
    ppl_pages = sorted(p for p, _ in ppl_top)

    return {
        "key": key,
        "pdf": pdf_path.name,
        "total_pages": n,
        "financial_pages": fin_pages,
        "financial_runs": find_runs(fin_pages),
        "financial_hits": {p: fin_hits[p] for p in fin_pages},
        "people_pages": ppl_pages,
        "people_runs": find_runs(ppl_pages),
        "people_hits": {p: ppl_hits[p] for p in ppl_pages},
    }


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, name in PDFS:
        path = ROOT / name
        if not path.exists():
            print(f"[skip] missing: {name}", file=sys.stderr)
            continue
        print(f"[scan] {key}: {name}", file=sys.stderr)
        results[key] = process(path, key)
        print(f"       {results[key]['total_pages']} pages → {len(results[key]['financial_pages'])} financial, {len(results[key]['people_pages'])} people", file=sys.stderr)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT}")
    # Summary
    print("\n=== SUMMARY ===")
    for key, r in results.items():
        print(f"  {key}: {r['total_pages']}pp; fin={r['financial_pages']}; people={r['people_pages']}")


if __name__ == "__main__":
    main()
