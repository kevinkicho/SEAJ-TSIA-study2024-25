---
layout: default
title: Time Series (Multi-Year)
nav_order: 7
---

# Master Time-Series — Multi-Year Financials

*Year-by-year financial history for every company where the annual or integrated report in this folder disclosed a multi-year summary. Sources are named per company; depths range from 2 to 11 fiscal years. Currencies are native — the chart below converts to any of USD / JPY / EUR / TWD / GBP / KRW / CNY on the fly via Frankfurter (with TWD hardcoded since it's not in the ECB reference list).*

---

## Interactive time-series chart

<div class="chart-view active"
     data-chart="master-ts"
     data-type="timeseries"
     data-companies="TSMC,Advantest,Shin-Etsu,Ebara,ASE Holdings,MediaTek,Applied Materials,Lam Research"
     data-metric="revenue"
     data-currency="USD"
     data-scale="linear"
     data-normalize="none" markdown="0"></div>

**How to use it:**
- Ctrl/Cmd+click companies in the first filter to multi-select (Advantest has 11 years, Shin-Etsu and Ebara have 10, CKD 12; most Taiwan issuers only disclose 2).
- Switch **Metric** to compare Revenue / Op Income / Net Income / Total Assets / Total Equity / Op Margin % / Gross Margin % / Net Margin %.
- Toggle **Normalize → Indexed (first year = 100)** to compare growth rates across companies regardless of absolute scale. This is the single best way to see that, e.g., Advantest's revenue has compounded faster than TSMC's off a much smaller base.
- Toggle **Scale → Log** when absolute values span orders of magnitude (e.g. Kokusai at ~¥200B vs Shin-Etsu at ~¥2.5T).

---

## Coverage summary (what's in the dataset)

| Depth tier | Companies | Why |
|---|---|---|
| **10+ fiscal years** | Advantest (11y, FY14–FY24), Shin-Etsu (10y, FY15–FY24), Ebara (10y, 2015–2024), CKD (12y, FY13–FY24) | Their integrated reports explicitly show 10–11 year summary tables |
| **5 fiscal years** | Kokusai Electric (FY20–FY24), ASE Holdings (FY20–FY24), Disco (FY15–FY19, **stale — current Disco is ~2.5× these figures**) | "5-year Financial Highlights" section near back of the report |
| **3 fiscal years** | Himax (2022–2024) | US-listed (Himax Technologies = 20-F filer), discloses 3y comparison |
| **2 fiscal years** | TSMC, UMC, MediaTek, ChipMOS, Phison, Lasertec, Nikon (partial), AMAT, Lam Research, KLA, Teradyne, ASM International | Annual reports show current-year vs prior-year comparison; deeper series exists in filings (20-F, 10-K historical) but wasn't extracted in this pass |
| **0–1 years (snapshot only)** | Realtek, Winbond, Nanya, PSMC, VIS, WIN Semi, KYEC, Sigurd, OSE, Spirox, ZDT, eMemory, M31, AP Memory, WPG, Topco, Marketech, MIC, Ardentec, Favite, CSUN, Gallant, Creating Nanotech, Leatec, Manz, ARM, Cadence, AMS OSRAM, JSR, Shimadzu, Horiba, JEOL, ULVAC, Screen, Daifuku, Micronics Japan, Marumae, Shibaura, Hitachi High-Tech, Canon, Lintec, UACJ, Senju, Ajinomoto, Fuji Electric, Panasonic Industry, Misumi, Daitron, Nagase, ITOCHU, Medipal, Seino, Organo, Adatech, Rikken Keiki, SINFONIA, CKD (has 12y — see above), DBJ, SANKI, ITRI, SGS, HCL Tech, GlobalFoundries | Either (a) single-year data was extracted, or (b) report is a summary/brochure without a multi-year table in the extracted pages, or (c) the multi-year section uses image-based tables that pdftotext couldn't read |

**Why "most Taiwan issuers only disclose 2"**: by TWSE rules, annual reports include a "Financial Status" section that mandates a 2-year comparison in the main narrative. Multi-year data (5-year is typical) is usually further back in the report (Section V, pages ~140–220 in a 200-page TW annual report). In this extraction pass I targeted page ranges that caught most balance-sheet and income-statement pages but not always the 5-year table. A targeted second-pass on each TW report could fill in 3 more years for most TW names.

---

## Spot data — a few illustrative series

The numbers below are pulled directly from the reports, for the companies with the deepest history. All figures are native currency (JPY millions for Japanese companies, unless noted). These are the rows that feed the chart above.

### Advantest (¥ millions, FY ends Mar 31 of following year)

| FY | Revenue | Op Income | Op Margin | Net Income | Total Assets |
|---|---|---|---|---|---|
| FY14 | 163,803 | 16,858 | 10.3% | 16,753 | 233,237 |
| FY15 | 162,111 | 12,597 | 7.8% | 6,694 | 210,451 |
| FY16 | 155,916 | 13,905 | 8.9% | 14,201 | 231,603 |
| FY17 | 207,223 | 24,487 | 11.8% | 18,103 | 254,559 |
| FY18 | 282,456 | 64,662 | 22.9% | 56,993 | 304,580 |
| FY19 | 275,894 | 58,708 | 21.3% | 53,532 | 355,777 |
| FY20 | 312,789 | 70,726 | 22.6% | 69,787 | 422,641 |
| FY21 | 416,901 | 114,734 | 27.5% | 87,301 | 494,696 |
| FY22 | 560,191 | 167,687 | 29.9% | 130,400 | 600,224 |
| FY23 | 486,507 | 81,628 | 16.8% | 62,290 | 671,229 |
| **FY24** | **779,707** | **228,161** | **29.3%** | **161,177** | **854,210** |

**Reads:** Advantest's revenue **4.8×'d in 10 years** (163,803 → 779,707). The FY22→FY23 dip (-13%) was the memory-tester correction; FY24's +60% is the HBM-AI snapback. Op margin breached 20% in FY18 and has held there except during the FY23 correction.

### Shin-Etsu Chemical (¥ millions, FY ends Mar 31)

| FY | Revenue | Op Income | Op Margin | Net Income | Total Assets | Net Assets |
|---|---|---|---|---|---|---|
| FY15 | 1,279,807 | 208,525 | 16.3% | 148,840 | 2,510,085 | 2,080,465 |
| FY16 | 1,237,405 | 238,617 | 19.3% | 175,912 | 2,655,636 | 2,190,082 |
| FY17 | 1,441,432 | 336,822 | 23.4% | 266,235 | 2,903,137 | 2,413,025 |
| FY18 | 1,594,036 | 403,705 | 25.3% | 309,125 | 3,038,717 | 2,532,556 |
| FY19 | 1,543,525 | 406,041 | 26.3% | 314,027 | 3,230,485 | 2,723,141 |
| FY20 | 1,496,906 | 392,213 | 26.2% | 293,732 | 3,380,615 | 2,886,625 |
| FY21 | 2,074,428 | 676,322 | 32.6% | 500,117 | 4,053,412 | 3,429,208 |
| FY22 | 2,808,824 | 998,202 | 35.5% | 708,238 | 4,730,394 | 4,026,209 |
| FY23 | 2,414,937 | 701,038 | 29.0% | 520,140 | 5,147,974 | 4,424,073 |
| **FY24** | **2,561,249** | **742,105** | **29.0%** | **534,021** | **5,636,601** | **4,837,585** |

**Reads:** Silicon wafer + PVC-chemicals diversification. Revenue **2×'d in 10 years**. Op margin climbed from 16% (FY15) to a peak of 35.5% (FY22) and has settled at 29% — a structural improvement, not a cyclical one. Total assets doubled to ¥5.6 T.

### Ebara (¥ millions, FY ends Dec since 2018)

| FY | Revenue | Op Income | Op Margin | Net Income | Total Assets |
|---|---|---|---|---|---|
| 2015 | 486,235 | 38,011 | 7.8% | 17,254 | 579,860 |
| 2016 | 476,104 | 29,995 | 6.3% | 20,587 | 588,457 |
| 2017* | 381,993 | 18,115 | 4.7% | 9,531 | 612,919 |
| 2018 | 509,175 | 32,482 | 6.4% | 18,262 | 591,592 |
| 2019 | 522,424 | 35,298 | 6.8% | 23,349 | 595,239 |
| 2020 | 522,478 | 37,566 | 7.2% | 24,236 | 644,711 |
| 2021 | 603,213 | 61,372 | 10.2% | 43,616 | 719,736 |
| 2022 | 680,870 | 70,572 | 10.4% | 50,488 | 828,049 |
| 2023 | 759,328 | 86,025 | 11.3% | 60,283 | 913,900 |
| **2024** | **866,668** | **97,953** | **11.3%** | **71,401** | **1,005,085** |

*2017 was a 9-month transition year (Mar→Dec fiscal change).

**Reads:** Revenue grew 78% over the decade. Op margin expanded from 6–7% to 11.3% as the **semi-segment (Precision Machinery) grew as a share of mix**. Net income quadrupled. Total assets crossed the ¥1 T mark in 2024.

### CKD (¥ millions, FY ends Mar 31)

| FY | Revenue | Op Income | Op Margin | ROE |
|---|---|---|---|---|
| FY13 | 75,491 | 7,883 | 10.4% | 10.1% |
| FY14 | 83,379 | 8,363 | 10.0% | 9.8% |
| FY15 | 88,117 | 8,107 | 9.2% | 8.3% |
| FY16 | 94,012 | 9,580 | 10.2% | 10.1% |
| FY17 | 115,700 | 12,472 | 10.8% | 12.1% |
| FY18 | 115,665 | 5,429 | 4.7% | 6.0% |
| FY19 | 100,717 | 5,230 | 5.2% | 4.5% |
| FY20 | 106,723 | 7,698 | 7.2% | 5.9% |
| FY21 | 142,199 | 17,879 | 12.6% | 12.1% |
| FY22 | 159,457 | 21,170 | 13.3% | 12.9% |
| FY23 | 134,425 | 13,113 | 9.8% | 6.7% |
| **FY24** | **155,634** | **19,018** | **12.2%** | **10.2%** |
| FY25 goal | 180,000 | 25,000 | 13.9% | 10–13% |

**Reads:** Very clear cycle — FY18 and FY19 were the trough (op margin fell below 5%). FY21–FY22 was the AI-capex peak. FY23 rolled over. FY24 recovery. FY25 guide implies another ~16% revenue growth.

### Kokusai Electric (¥ millions, FY ends Mar 31)

| FY | Revenue | Gross Profit | Op Income | Op Margin | Net Income | Total Assets |
|---|---|---|---|---|---|---|
| FY20 | 178,023 | 75,951 | 60,037 | 33.7% | 33,043 | 273,769 |
| FY21 | 245,425 | 107,069 | 70,652 | 28.8% | 51,339 | 356,532 |
| FY22 | 245,721 | 100,805 | 56,064 | 22.8% | 40,305 | 373,539 |
| FY23 | 180,838 | 74,965 | 30,745 | 17.0% | 22,374 | 375,433 |
| **FY24** | **238,933** | **101,743** | **51,320** | **21.5%** | **36,004** | **341,512** |

**Reads:** Revenue cycle peaked in FY21/22 at ~¥245 B, troughed at ¥181 B (FY23, -26% YoY), recovered +32% to ¥239 B in FY24. **Op margin compression** from 33.7% (FY20) to 21.5% (FY24) reflects both mix shift (more HBM-deposition vs. legacy) and scale dynamics.

### ASE Holdings (NT$ millions, FY ends Dec 31)

| FY | Revenue | Gross Profit | Op Income | Op Margin | Net Income | Total Assets |
|---|---|---|---|---|---|---|
| 2020 | 476,979 | 77,984 | 34,876 | 7.3% | 29,277 | 583,667 |
| 2021 | 569,997 | 110,369 | 62,124 | 10.9% | 66,014 | 672,934 |
| 2022 | 670,873 | 134,930 | 80,176 | 12.0% | 65,227 | 707,068 |
| 2023 | 581,915 | 91,757 | 40,328 | 6.9% | 33,557 | 667,052 |
| **2024** | **595,410** | **96,932** | **39,166** | **6.6%** | **33,926** | **740,698** |

**Reads:** OSAT revenue is highly cyclical. The 2022 peak (NT$671B) was the COVID-packaging surge. 2023 saw a 13% correction. 2024 essentially flat at the revenue line, but total assets grew +11% — CapEx-led investment in advanced packaging capacity ahead of the coming cycle.

---

## What this shows that the static tables don't

| Observation | Evidence |
|---|---|
| **Ten-year compounding is larger than one-year growth suggests.** | Advantest FY14 revenue ¥164B → FY24 ¥780B = **4.8× in 10 years** = 16.9% CAGR |
| **Op margin structural lift, not cyclical.** | Shin-Etsu expanded op margin from 16% (FY15) to 29% (FY24) through silicon-wafer pricing power + specialty chemicals mix shift. Each year it's ratcheting up; very few step-downs |
| **The 2023 WFE trough is visible everywhere at once.** | Advantest rev -13% FY23, Kokusai -26%, CKD op margin 13.3%→9.8%, ASE op margin 12.0%→6.9%. Then all recover in FY24 (Mar/Dec end) |
| **Reported fiscal years stagger.** | Advantest/Kokusai/Shin-Etsu end March; ASE/Ebara end December. A single calendar "2024" shows different WFE-cycle moments depending on which company you're reading |
| **Japan companies are the ones that disclose long series.** | 10-year summaries are a convention of Japanese integrated reports (META-guided). Taiwan 5-year tables exist but are buried; US 10-Ks dropped the "5-Year Selected Financial Data" requirement in 2021 and most companies no longer show it |

---

## Data gaps and known issues

| Gap | Impact |
|---|---|
| **Disco 2020 file is stale.** | Current Disco revenue is ~¥400B (FY24, estimated) — roughly 2.5× the FY19 peak in this table. A current Disco integrated report would transform the visible story. |
| **TSMC only has 2 years here.** | TSMC's 20-F SEC filing contains full 5-year selected financial data. Adding that single file would give TSMC a 5-year time series and dramatically improve the chart. |
| **Many Taiwan issuers default to 2 years.** | TW annual reports do have 5-year tables (usually Section V, ~p.140+) but they were outside the page ranges I extracted this pass. A second-pass extraction on the 10 biggest Taiwan issuers would add ~3 years to each. |
| **Nikon data is partial (Q1–Q3 only).** | The file in this folder is a 3Q result, not a full annual report. Full-year Nikon numbers for multi-year context are in their annual securities report. |
| **KLA, Lam, AMAT have only 2 years.** | Their 10-Ks include the most recent year and one comparison year — prior years are in **earlier 10-Ks** which aren't in this folder. |
| **Currency conversion introduces visible FX effects.** | When you switch the chart to USD, a company whose native currency weakened against USD (most JPY companies over 2021–2024) will look *weaker* than their local-currency performance. Toggle **Normalize → Indexed** to see underlying growth divorced from FX. |

---

## Methodology

| Step | Detail |
|---|---|
| **Source scan** | All 134 PDFs in the folder extracted via `pdftotext -layout` |
| **Pattern search** | `grep -E` for 3+ year header rows (FY20xx or 20xx patterns) and explicit section headers ("5-Year Summary", "11-Year Summary", "Ten-Year Summary", "Financial Highlights") |
| **Manual extraction** | For each company with a detected multi-year table, the cells were hand-extracted into structured JS (`assets/js/companies-timeseries.js`). Units and currency labeled per company. |
| **Column-order sanity check** | Per-company; see [`02_KEY_FINANCIALS.md`](./02_KEY_FINANCIALS.md) for notes on TW column-order variation |
| **FX conversion** | Live rates from frankfurter.dev (ECB), with **TWD hardcoded** because it's not in the ECB reference basket |
| **Normalization option** | The chart offers "indexed" mode (first disclosed year = 100) to compare growth rates across scales and currencies |

---

*Any company you want to add multi-year data for? Point me at the right page range in its PDF (e.g., "TSMC 5-year, look at pg 120 of the 2024 annual report") and I'll extend the dataset.*
