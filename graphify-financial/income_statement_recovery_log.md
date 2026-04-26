# Income Statement Recovery Log

Recovery pass on 2026-04-25 to backfill canonical revenue for 5 companies whose income-statement page was missed in the original page-detection pass.

## Method

For each PDF, ran `pdftotext -layout` over candidate pages, grepped for `STATEMENTS OF (COMPREHENSIVE )?INCOME`, `Net revenue`, `Operating income`, `Ordinary income`, `Revenues`, `Net profit`, `Five-year`. All 5 PDFs had an extractable text layer (no OCR needed). Extracted metrics directly from the pdftotext output (verified accurate against the rasterized PNG); appended new entries to each `<key>_extraction.json` under `financial_pages` with `table_type=income_statement`, `is_financial_table=true`, `is_company_actual=true`. Existing entries left untouched. All JSONs validated with `json.load`.

## Per-company results

### 1. WPG Holdings (TWSE:3702)
- **Page picked**: PDF p129 (Section 5.2.1 Consolidated Statement - Financial Performance Comparison)
- **PNG**: `wpg/pages/wpg_p129-129.png` (1272x1799)
- **New entry**: `wpg_p129` (income_statement, TWD thousands)
- **Revenue (FY2024 vs FY2023)**: Operating revenue 880,552,335 vs 671,888,131 (+31.06%)
- **Net income**: 7,415,736 vs 8,197,737 (-9.54%)
- **Operating profit**: 14,700,513 vs 10,394,708

### 2. Phison Electronics (TWSE:8299)
- **Page picked**: PDF p159 (Section 5.2.1 Consolidated Statements of Comprehensive Income)
- **PNG**: existing `phison_2024_annual_report/pages/phison_2024_annual_report_p159-159.png`
- **New entry**: `phison_2024_annual_report_p159_income_statement` (income_statement, TWD thousands)
- **Note**: Existing JSON entry `phison_2024_annual_report_p159` was mis-categorized as balance_sheet; its data actually came from PDF p158 (the balance sheet page). The PNG referenced by that page_id is the income statement. Added new entry rather than modify existing one (per task rules).
- **Revenue**: Operating revenue 58,935,513 vs 48,221,630 (+22.22%)
- **Net profit**: 7,953,999 vs 3,624,428 (+119.46%)
- **Net operating income**: 3,533,084 vs 3,621,868 (-2.45%)

### 3. Fubon Financial Holdings (TWSE:2881)
- **Page picked**: PDF p308 (Section 5.2(1) Consolidated comprehensive income statement)
- **PNG**: `fubon_financial_annual_report_2024/pages/fubon_financial_annual_report_2024_p308-308.png` (1273x1800)
- **New entry**: `fubon_financial_annual_report_2024_p308` (income_statement, TWD thousands)
- **Net revenue**: 347,463,495 vs 167,798,693 (+107.07%) — canonical revenue line for financial holding
- **Net income**: 150,861,039 vs 65,042,302 (+131.94%)
- **Net interest revenue**: 181,744,840 vs 169,017,304

### 4. ITOCHU Corporation (TYO:8001)
- **Page picked**: PDF p48 'Selected Financial Data' (re-rasterized at 200dpi to 1800x1272)
- **PNG**: `itochu_ar2025e/pages/itochu_ar2025e_p048-48-v2.png`
- **New entry**: `itochu_ar2025e_p048_v2` (income_statement, JPY millions, 5 years FY2021-FY2025)
- **Revenues (FY2025 vs FY2024)**: 14,724,234 vs 14,029,910 (+4.95%)
- **Net profit attributable to ITOCHU**: 880,251 vs 801,770 (+9.79%)
- **Total assets**: 15,134,264 vs 14,489,701
- **Note**: Original p048 entry was empty (vision couldn't read multi-column 11-year table); pdftotext extraction succeeded cleanly.

### 5. Development Bank of Japan (DBJ)
- **Page picked**: PDF p54 'Consolidated Financial Summary' (re-rasterized at 200dpi to 1800x694; very wide 12-year table)
- **PNG**: `dbjintegratedreport2025/pages/dbjintegratedreport2025_p054-54-v2.png`
- **New entry**: `dbjintegratedreport2025_p054_v2` (income_statement, JPY billions, 5 years FY2020-FY2024)
- **Total income (FY2024 vs FY2023)**: 392.0 vs 410.8 billion (-4.6%)
- **Ordinary income**: 113.3 vs 147.8
- **Net income attributable to owners of parent**: 83.7 vs 103.2
- **Total assets**: 21,549.3 vs 21,698.6 billion
- **Note**: DBJ fiscal year ends March 31; FY2024 = Apr 2024 - Mar 2025. Original p054 entry was empty.

## Outcome

All 5 companies now have canonical Revenue (or revenue-equivalent), Net Income, and Operating Income captured for at least the most recent 2 fiscal years. None required vision Read because pdftotext returned clean tabular data on every PDF. All 5 JSONs validate successfully.

Parent session should rebuild SQLite index to pick up the new entries.
