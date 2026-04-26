#!/usr/bin/env python3.12
"""Master rasterization for all 9 PDFs.

Page picks combine the regex-based detector (for strong financial markers)
with numeric-density spot-checks (for Taiwan-style reports where the regex
under-fires) and contiguous-page expansion (to catch full statement spreads).

Output PNGs land in graphify-financial/<key>/pages/.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path("/mnt/c/Users/kevin/Desktop/SEAJ TSIA")

PLAN = {
    # key: (pdf filename, list of (page, role) tuples where role ∈ {"fin","people","both"})
    "wpg": ("2024_WPG_annual_report_E.pdf", [
        (23, "fin"), (41, "fin"), (79, "fin"), (80, "fin"),
        (127, "fin"), (128, "fin"),
        (18, "people"), (27, "people"), (33, "people"), (34, "people"),
    ]),
    "umc": ("2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf", [
        (87, "fin"), (88, "fin"), (114, "fin"), (115, "fin"), (116, "fin"),
        (17, "people"), (28, "people"), (35, "people"),
    ]),
    "amat": ("2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf", [
        (36, "fin"), (39, "fin"), (50, "fin"), (51, "fin"), (59, "fin"), (60, "fin"),
        (4, "people"), (9, "people"), (16, "people"),
    ]),
    "medipal": ("00 MEDIPAL integrated report 2025.pdf", [
        (9, "fin"), (10, "fin"), (11, "fin"), (12, "fin"), (13, "fin"), (18, "fin"),
        (57, "people"), (58, "people"), (64, "people"),
    ]),
    "alcor": ("2024_AnnualReport_EN.pdf", [
        (6, "fin"), (123, "fin"), (134, "fin"), (136, "fin"),
        (8, "people"), (9, "people"), (10, "people"), (13, "people"),
    ]),
    "itri": ("2024_Annual Report ITRI taiwan.pdf", [
        (11, "fin"), (14, "fin"), (17, "fin"), (68, "fin"),
        (67, "people"),
    ]),
    "ase": ("20250603150724453273521_en ASE holdings annual report 2024.pdf", [
        (8, "fin"), (93, "fin"), (159, "fin"), (160, "fin"),
        (13, "people"), (17, "people"), (27, "people"),
    ]),
    "vis": ("20250506232053383995188_en VIS annual report 2025.pdf", [
        (91, "fin"), (130, "fin"), (151, "fin"), (189, "fin"), (190, "fin"),
        (36, "people"), (53, "people"), (62, "people"),
    ]),
    "egis": ("EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf", [
        (6, "fin"), (90, "fin"), (126, "fin"), (135, "fin"),
        (15, "people"), (28, "people"), (29, "people"),
    ]),
}


def rasterize(pdf: Path, page: int, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # pdftoppm appends -NN.png based on page number — give it the prefix without extension
    prefix = str(out_path).removesuffix(".png")
    subprocess.run(
        ["nice", "-n", "19", "pdftoppm", "-r", "200", "-f", str(page), "-l", str(page), "-png",
         str(pdf), prefix],
        check=True, stderr=subprocess.DEVNULL,
    )


def main():
    total_pages = sum(len(v[1]) for v in PLAN.values())
    done = 0
    summary = {}
    for key, (pdf_name, pages) in PLAN.items():
        pdf_path = ROOT / pdf_name
        if not pdf_path.exists():
            print(f"[skip] missing PDF: {pdf_name}", file=sys.stderr)
            continue
        company_dir = ROOT / "graphify-financial" / key / "pages"
        company_dir.mkdir(parents=True, exist_ok=True)
        rasterized = []
        for page, role in pages:
            done += 1
            png_name = f"{key}_p{page:03d}.png"
            out_path = company_dir / png_name
            # If already exists with same content, skip
            existing = list(company_dir.glob(f"{key}_p{page:03d}-*.png"))
            if existing:
                print(f"  [{done}/{total_pages}] {key} p{page} {role} (cached: {existing[0].name})", file=sys.stderr)
                rasterized.append({"page": page, "role": role, "png": existing[0].name})
                continue
            print(f"  [{done}/{total_pages}] {key} p{page} {role}", file=sys.stderr)
            rasterize(pdf_path, page, out_path)
            # pdftoppm names the file as <prefix>-NN.png; find it
            actuals = list(company_dir.glob(f"{key}_p{page:03d}-*.png"))
            if actuals:
                rasterized.append({"page": page, "role": role, "png": actuals[0].name})
        summary[key] = {"pdf": pdf_name, "pages": rasterized}

    out = ROOT / "graphify-financial" / "rasterize_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nWrote {out}")
    for key, info in summary.items():
        print(f"  {key}: {len(info['pages'])} PNGs")


if __name__ == "__main__":
    main()
