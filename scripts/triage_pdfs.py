#!/usr/bin/env python3
"""
Triage 134 PDFs in /mnt/c/Users/kevin/Desktop/SEAJ TSIA/ into buckets for the
semiconductor-industry knowledge graph project.

Buckets:
  - annual_reports          (full annual reports, 10-Ks, integrated reports)
  - quarterly_reports       (Q1/Q2/Q3/Q4 results, FY supplementary briefings)
  - investor_presentations  (IR decks, analyst day slides)
  - brochures               (product brochures, datasheets, lens lineups)
  - industry_reports        (third-party reports, tech specs, market research)
  - unrelated               (off-topic / duplicates)

Strategy: pdfinfo for page count + pdftotext (first 5 pages) for text signals.
Combine filename heuristics with text heuristics.

Output: graphify-financial/triage.json
"""
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")
OUT = ROOT / "graphify-financial" / "triage.json"

ALREADY_PROCESSED = {
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

# Filename keyword patterns (case-insensitive)
# NOTE: ar2025/ar2024 in filenames almost always means "Annual Report" not a quarter.
FN_QUARTERLY = re.compile(
    r"(q[1-4][^a-z]|[1-4]q[^a-z]|quarterly|3q[-_ ]|4q[-_ ]|"
    r"\bresult\b|\bresults\b|briefing|consolidated_financial|supplementary"
    r"|first[-_ ]half|second[-_ ]half|\bh1\b|\bh2\b|hy[-_ ]?report|"
    r"financial[-_ ]results|fy20\d\dq[1-4]|\d{4}q[1-4])",
    re.IGNORECASE,
)
FN_ANNUAL = re.compile(
    r"(annual[-_ ]?report|annualreport|annual[-_ ]?\d|annual\b|10[-_]?k|"
    r"integrated[-_ ]?report|sustainability[-_ ]report|esg[-_ ]?report|"
    r"年報|年度年報|stockholder|ar20\d\d|"
    r"ckdreport|cnt_pdfc|index_report\d{4})",
    re.IGNORECASE,
)
FN_BROCHURE = re.compile(
    r"(brochure|datasheet|data[-_ ]sheet|flyer|catalog|catalogue|lineup|"
    r"line[-_ ]up|profile|guide|pamphlet|product[-_ ]brief|corporateprofile|"
    r"general[-_ ]catalog|company[-_ ]profile|at[-_ ]a[-_ ]glance)",
    re.IGNORECASE,
)
FN_IR_PRES = re.compile(
    r"(presentation|investor|analyst|conference|conf2025|webinar|"
    r"slides|investor[-_ ]?day|analyst[-_ ]?day|ir[-_ ]?site|ir[-_ ]?pre|"
    r"medium[-_ ]term|business[-_ ]plan|update_|investor.update|"
    r"ec.q[1-4]|ec_q[1-4])",
    re.IGNORECASE,
)
FN_INDUSTRY = re.compile(
    r"(\bcxl[-_ ]|\bcxl\.|jeita|\bidc\b|gartner|\bhbm[_ ]|"
    r"trends_20\d\d|spec[a-z]*_rev|specification|"
    r"market[-_ ]forecast|industry[-_ ]forecast)",
    re.IGNORECASE,
)
FN_UNRELATED = re.compile(
    r"(completion[-_ ]certificate|voter|los[-_ ]angeles[-_ ]county)",
    re.IGNORECASE,
)

# Text-content patterns
TXT_FIVE_YEAR = re.compile(
    r"(five[-_ ]year (financial )?(summary|highlights|review)|"
    r"5[-_ ]year (financial )?summary|consolidated balance sheet|"
    r"consolidated statements? of (income|operations|comprehensive))",
    re.IGNORECASE,
)
TXT_QUARTERLY = re.compile(
    r"(financial results for|results for the (first|second|third|fourth) quarter|"
    r"q[1-4] 20\d\d|fy20\d\d q[1-4]|three months ended|six months ended|"
    r"nine months ended|supplementary explanation|3q 20\d\d|4q 20\d\d|"
    r"quarterly report|fiscal year ended)",
    re.IGNORECASE,
)
TXT_ANNUAL = re.compile(
    r"(annual report 20\d\d|10[-_ ]?k|integrated report 20\d\d|"
    r"this annual report|stockholders? meeting|board of directors)",
    re.IGNORECASE,
)
TXT_BROCHURE = re.compile(
    r"(product (brochure|catalog|catalogue)|datasheet|features?\s*&\s*benefits|"
    r"specifications?|technical specifications?|product line[-_ ]up)",
    re.IGNORECASE,
)
TXT_IR_PRES = re.compile(
    r"(investor presentation|analyst day|investor day|forward[-_ ]looking|"
    r"safe harbor|q&a|earnings call|guidance for|cautionary statement)",
    re.IGNORECASE,
)
TXT_INDUSTRY = re.compile(
    r"(compute express link|cxl specification|hbm.*roadmap|"
    r"market forecast|market research|industry outlook|jeita|"
    r"semiconductor industry forecast)",
    re.IGNORECASE,
)


def get_pages(p: Path) -> int:
    try:
        r = subprocess.run(
            ["pdfinfo", str(p)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in r.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return -1


def get_text(p: Path, last_page: int = 5) -> str:
    try:
        r = subprocess.run(
            ["pdftotext", "-layout", "-f", "1", "-l", str(last_page), str(p), "-"],
            capture_output=True,
            text=True,
            timeout=60,
            errors="ignore",
        )
        return r.stdout or ""
    except Exception:
        return ""


def classify(filename: str, pages: int, text: str):
    fn = filename
    reasons = []

    # Special-case: known duplicates
    if filename == "2024_WPG_annual_report_E (1).pdf":
        return "unrelated", "high", ["duplicate of 2024_WPG_annual_report_E.pdf"], None
    if filename == "LAM+RESEARCH+CORP_BOOKMARKS_2025_V1.pdf":
        return (
            "unrelated",
            "high",
            ["duplicate (md5) of LAM+RESEARCH+CORP_BOOKMARKS_2025_V1 annual report 2025.pdf"],
            None,
        )

    # Filename signals
    fn_q = bool(FN_QUARTERLY.search(fn))
    fn_a = bool(FN_ANNUAL.search(fn))
    fn_b = bool(FN_BROCHURE.search(fn))
    fn_p = bool(FN_IR_PRES.search(fn))
    fn_i = bool(FN_INDUSTRY.search(fn))
    fn_u = bool(FN_UNRELATED.search(fn))

    # Text signals
    tx_5y = bool(TXT_FIVE_YEAR.search(text))
    tx_q = bool(TXT_QUARTERLY.search(text))
    tx_a = bool(TXT_ANNUAL.search(text))
    tx_b = bool(TXT_BROCHURE.search(text))
    tx_p = bool(TXT_IR_PRES.search(text))
    tx_i = bool(TXT_INDUSTRY.search(text))

    # 1) Unrelated by filename
    if fn_u:
        reasons.append(f"filename matches unrelated pattern")
        return "unrelated", "high", reasons, None

    # 2) Industry / spec docs (filename or text)
    if fn_i or tx_i:
        if fn_i:
            reasons.append("filename indicates industry/spec doc")
        if tx_i:
            reasons.append("text mentions industry/market/spec keywords")
        return "industry_reports", "high" if (fn_i and tx_i) else "med", reasons, None

    # 3) Quarterly first (since "Q4 result" docs may also mention 'annual')
    #    — but only if filename clearly says quarterly OR text strongly indicates partial period.
    if fn_q and not fn_a:
        reasons.append("filename has quarterly/result/briefing keyword")
        if tx_q:
            reasons.append("text mentions quarterly period")
            return "quarterly_reports", "high", reasons, None
        if pages >= 0 and pages <= 60:
            reasons.append(f"page count {pages} consistent with quarterly")
            return "quarterly_reports", "med", reasons, None
        return "quarterly_reports", "low", reasons, None

    # 4) Annual / integrated report — but exclude obvious news releases
    if fn_a and re.search(r"(?:^|[_\W])news(?:[_\W]|$)", fn, re.IGNORECASE):
        reasons.append(
            "filename has 'annual report' but also 'News' — treating as brochure/news"
        )
        return "brochures", "med", reasons, ["brochures", "annual_reports"]
    if fn_a:
        reasons.append("filename has annual/integrated/sustainability/年報")
        if tx_5y or pages >= 80:
            reasons.append(
                f"page count {pages} or 5-yr financial summary text confirms annual"
            )
            return "annual_reports", "high", reasons, None
        if pages >= 30:
            reasons.append(f"page count {pages} consistent with annual report")
            return "annual_reports", "med", reasons, None
        # Short doc with "annual report" in name — possibly an excerpt/news
        reasons.append(f"short page count {pages} — possibly excerpt; ambiguous")
        return "annual_reports", "low", reasons, ["annual_reports", "brochures"]

    # 5) Brochure (filename strong)
    if fn_b and not fn_p:
        reasons.append("filename has brochure/datasheet/catalog/profile/lineup")
        if pages >= 0 and pages <= 80:
            reasons.append(f"page count {pages} consistent with brochure")
            return "brochures", "high", reasons, None
        # Long "profile" docs (e.g., HITACHI HIGH-TECH) can be borderline integrated reports
        return "brochures", "med", reasons, ["brochures", "annual_reports"]

    # 6) Investor presentation
    if fn_p:
        reasons.append("filename has presentation/investor/analyst/conference")
        if tx_p or (pages >= 0 and pages <= 80):
            reasons.append(f"page count {pages} or text confirms presentation")
            return "investor_presentations", "high", reasons, None
        return "investor_presentations", "med", reasons, None

    # 7) Fall through — use page count + text signals
    if tx_5y or (pages >= 100 and tx_a):
        reasons.append(f"text shows 5-yr financials or page count {pages}+annual text")
        return "annual_reports", "med", reasons, None
    if tx_q:
        reasons.append("text mentions quarterly results")
        return "quarterly_reports", "med", reasons, None
    if tx_p:
        reasons.append("text mentions investor-presentation cues")
        return "investor_presentations", "low", reasons, None
    if tx_b or (pages >= 0 and pages <= 30):
        reasons.append(f"page count {pages} or brochure text — likely brochure")
        return "brochures", "low", reasons, ["brochures", "investor_presentations"]

    reasons.append("no strong signal; defaulting to brochures")
    return "brochures", "low", reasons, ["brochures", "investor_presentations", "annual_reports"]


def main():
    start = time.time()
    pdfs = sorted([p for p in ROOT.glob("*.pdf")])
    print(f"Found {len(pdfs)} PDFs in {ROOT}")

    buckets = {
        "annual_reports": [],
        "quarterly_reports": [],
        "investor_presentations": [],
        "brochures": [],
        "industry_reports": [],
        "unrelated": [],
    }
    ambiguous = []
    skipped = []

    for i, p in enumerate(pdfs, 1):
        name = p.name
        if name in ALREADY_PROCESSED:
            skipped.append(name)
            print(f"[{i:3}/{len(pdfs)}] SKIP (already processed): {name}")
            continue

        pages = get_pages(p)
        text = get_text(p, last_page=5)
        bucket, conf, reasons, alt = classify(name, pages, text)

        entry = {
            "filename": name,
            "pages": pages,
            "confidence": conf,
            "reason": "; ".join(reasons),
        }
        buckets[bucket].append(entry)

        if alt:
            ambiguous.append(
                {
                    "filename": name,
                    "candidates": alt,
                    "chosen": bucket,
                    "reason": "; ".join(reasons),
                }
            )

        print(f"[{i:3}/{len(pdfs)}] {bucket:24} ({conf:4}) p={pages:>4}  {name[:80]}")

    elapsed = time.time() - start

    out = {
        "generated_at": "2026-04-25",
        "total": len(pdfs),
        "already_processed": len(skipped),
        "buckets": buckets,
        "ambiguous": ambiguous,
        "elapsed_seconds": round(elapsed, 1),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT}")
    print(f"Elapsed: {elapsed:.1f}s")

    print("\n=== Counts ===")
    for k, v in buckets.items():
        print(f"  {k:24} {len(v):3}")
    print(f"  {'already_processed':24} {len(skipped):3}")
    print(f"  {'ambiguous (flagged)':24} {len(ambiguous):3}")


if __name__ == "__main__":
    main()
