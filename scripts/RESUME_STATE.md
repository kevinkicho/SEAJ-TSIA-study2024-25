# Resume state — Marker + graphify financial extension

Interrupted: 2026-04-24, system slowdown (Marker layout-detection is RAM-heavy on CPU).
3 parallel Marker processes were killed cleanly before reboot.

## What's safe on disk

### Main graphify deliverables (`graphify-out/`)
- `graph.html` (1.0 MB) — interactive graph, 1,512 nodes / 1,848 edges / 174 communities
- `graph.json` (1.2 MB) — GraphRAG-ready
- `graph.svg` (5.4 MB) — static vector
- `graph.graphml` (1.2 MB) — for Gephi / yEd
- `GRAPH_REPORT.md` (82 KB) — audit trail
- `manifest.json` — per-file checksums for `--update`
- `cost.json` — cumulative token cost (~600K input / 112K output)
- `obsidian/` — 1,681 markdown notes
- `financial_spike.json` — pdfplumber spike results (80.9% precision across 5 files)

### Scripts (`scripts/`)
- `financial_spike.py` (115 lines) — pdfplumber-based extractor, header-rule classifier
- `marker_extract_financials.py` (180 lines) — Marker JSON parser with forecast-rejection, currency/unit detection, cell-level row matching

### Partial Marker output (`graphify-marker/`)
- `2024 Annual Report-E TSMC/` (11 MB) — full run, 101 tables, 94 pages
- `2024_WPG_annual_report_E/` (6.3 MB) — full run, 86 tables, 101 pages

## What's NOT done (resume here)

### Remaining Marker runs
Missing 3 of 5 files. Narrow page ranges chosen based on where ground-truth income statements live:

```bash
# Shin-Etsu — 10-Year Summary on page 69 (0-indexed 68)
marker_single --output_dir graphify-marker --output_format json \
    --disable_image_extraction --page_range 60-72 \
    "Annual-Report-2025 SHINETSU.pdf"

# Advantest — Integrated Report; financial highlights on pages 11, 70 (0-indexed 10, 69)
marker_single --output_dir graphify-marker --output_format json \
    --disable_image_extraction --page_range 0-20 \
    "E_all_IAR2025 ADVANTEST annual report 2025.pdf"

# ASE — Executive Summary 5-year table on page 8 (0-indexed 7); consolidated statements pages 100-180
marker_single --output_dir graphify-marker --output_format json \
    --disable_image_extraction --page_range 0-20 \
    "20250603150724453273521_en ASE holdings annual report 2024.pdf"
```

Observation: single-threaded CPU marker uses ~8 GB RAM per process. Do NOT run 3 in parallel again — run serially to keep the machine responsive.

### Analysis steps not yet run
1. `python3 scripts/marker_extract_financials.py` — parse all 5 Marker JSON outputs
2. Compare to `graphify-out/financial_spike.json` (pdfplumber baseline = 80.9% precision)
3. Ingest `FinancialMetric` nodes into graph.json, re-cluster
4. Regenerate `graph.html` / `graph.svg` / report
5. Write quantitative + qualitative comparison

## Open questions to resolve next session
- Does Marker correctly reject the Gartner forecast on WPG page 90 (pdfplumber's false positive)? → Spot-checked yes — `<th>2025(F)</th>` correctly captured as separate cells
- Does Marker recover Shin-Etsu's Net sales row that pdfplumber missed?
- Does Marker on ASE page 8 match pdfplumber's 20/21 correct extractions, or does it add the missed 1?
- For TSMC/Advantest Integrated Reports that have no income statement — does Marker correctly return zero financial-metric tuples (the right answer)?

## Dependencies installed (preserved across reboot)
- `pdfplumber==0.11.9` on Python 3.14 (linuxbrew)
- `marker-pdf` on Python 3.12 (/usr/bin/python3.12, user site: ~/.local/lib/python3.12/)
- `magic-pdf==1.3.12` on Python 3.12 (installed but not used — pivoted to Marker)
- Marker models auto-cached in `~/.cache/datalab/` — will reload instantly next time

## How to resume after reboot
```bash
cd "/mnt/c/Users/kevin/Desktop/SEAJ TSIA"
cat scripts/RESUME_STATE.md       # refresh memory
# Tell Claude: "resume the marker pipeline from RESUME_STATE.md"
```
