---
layout: default
title: Balance Sheets
nav_order: 6
---

# Master Balance-Sheet Datasheet

*One-row-per-company consolidated balance-sheet snapshot for every PDF in this project where balance-sheet data could be extracted. Figures are as disclosed in each company's consolidated statement of financial position, most-recent fiscal year. Currencies vary — always read the **Currency** column before comparing. USD-converted column is a rough benchmark only.*

---

## Reading notes

- **Fiscal year-ends differ.** Most Taiwan companies: December. Most Japanese companies: March. Lasertec: June. Applied Materials: late October. KLA / Lam: late June. Shin-Etsu, JSR, Advantest, Kokusai, Accretech, Shimadzu, JEOL, Medipal, UACJ, Misumi, Lintec, Nagase, Itochu, SNK, Shibaura Mechatronics: March. Disco row is stale — FY2019 (ended 2020-03).
- **Currency units vary** and are labeled per row: NT$ thousands (most Taiwan), NT$ millions (ASE summary, ITRI, Fubon totals), US$ thousands (US 10-Ks + INFICON), € millions (ASM Intl), ¥ millions (most Japanese), ¥ billions (DBJ summary), ₹ crores (HCL Tech). Do not do apples-to-apples comparisons in the native-currency columns — use the USD column.
- **`n/e` = not extracted.** The integrated report or annual report PDF in this folder showed only a summary balance sheet (totals / multi-year highlights) and did not break out that specific line item. Full audited statements for those companies live in separate securities filings (有価証券報告書 in Japan, MOPS in Taiwan, 10-K appendices for US issuers).
- **FX rates applied to the USD column** (pulled fresh rather than using round estimates):

  | Pair | Rate | Source | Reference date |
  |---|---|---|---|
  | 1 USD → JPY | 159.48 | [Frankfurter](https://frankfurter.dev/) (ECB reference rates) | 2026-04-23 |
  | 1 USD → EUR | 0.85514 | Frankfurter (ECB) | 2026-04-23 |
  | 1 USD → INR | 94.11 | Frankfurter (ECB) | 2026-04-23 |
  | 1 USD → CHF | 0.78476 | Frankfurter (ECB) | 2026-04-23 |
  | 1 USD → TWD | 31.576278 | [open.er-api.com / exchangerate-api.com](https://www.exchangerate-api.com/) | 2026-04-24 00:02 UTC |

  **Why two sources:** ECB reference rates (which Frankfurter mirrors) do not publish a TWD quote, so TWD is sourced from `open.er-api.com` on 2026-04-24 and attributed separately. All other quotes come from Frankfurter on 2026-04-23. Rates update daily; values in the USD column are a snapshot and will drift.

- **Consolidated over parent-only.** Where both are shown side-by-side (TSMC, MediaTek, etc.), the consolidated figure is used.
- **J-GAAP "Net assets"** is reported in the **Total Equity** column with a note, since the J-GAAP term includes non-controlling interests similarly to IFRS/US-GAAP "Total equity."
- **Banks and research institutes have non-industrial BS structure** — Fubon Financial, DBJ, and ITRI rows are present for completeness but their asset-side categories (loans, securities, bank reserves, "Funds and Surplus") do not map to the industrial columns used here. Use top-line totals only.
- **Stale rows** (Disco FY2019, Seino FY2024-03, Sanki FY2022-23) have today's FX applied to prior-year balances. The FX is current; the balances are not. Treated as "best available" rather than "fresh."

---

## Extraction summary

| Bucket | Count | Notes |
|---|---|---|
| Total PDFs in folder | 134 | — |
| Annual / integrated reports with extractable BS | ~55 | rows below |
| Product brochures / catalogues / datasheets / spec sheets | ~45 | no financial data (e.g. SENJU soldering catalogue, Canon cinema-lens lineup, AMS OSRAM SFH 7072 datasheet, ARM Cortex-R52, CXL specification, ZEISS scanner brochures, Manz flyers, Richtek product guide) |
| Quarterly earnings / investor-day decks / presentations | ~15 | mostly P&L highlights only; some have summary BS (see "Non-extractable" list below) |
| Industry / government reports / research-institute profiles | ~8 | JEITA, SEAJ quarterly releases, GlobalFoundries "at-a-glance", HBM trends, ISTI, KEYENCE profile |
| Misfiled / unrelated | 1 | `Los Angeles County Completion Certificate - June 2, 2026 Statewide Direct Primary Election.pdf` |
| Byte-identical duplicates | 6 pairs | see "Files processed" section |
| File problems (image-only PDF, press release, CSR only) | 3 | Creating Nanotech (image-only — needs OCR), Episil (press release, not AR), Weltrend (sustainability report only) |

---

## The mastersheet

Rows are sorted by ≈USD total assets, descending (using FX rates above). Bank / conglomerate / nonprofit rows are present but flagged — do not mix their ratios with the industrial semi peers.

| # | Company | Ticker | FY end | Cur. (units) | Total Assets | Cash & equiv. | Inventories | PP&E (net) | Total Liabilities | LT Debt | Total Equity | Retained Earnings | ≈ USD Assets |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Fubon Financial** 🏦 | TW 2881 | 2024-12-31 | NT$ thousands | 12,067,311,207 | 819,400,000 (cash+central bank) | n/a (bank) | 71,800,000 | 11,101,516,452 | 360,500,000 (bonds payable) | 965,794,755 | 645,589,960 | **~US$382.2 B** |
| 2 | **TSMC** | TW 2330 | 2024-12-31 | NT$ thousands | 6,691,938,000 | n/e | n/e | 3,234,980,070 | 2,368,362,135 | n/e | 4,323,575,865 | n/e | **~US$211.9 B** |
| 3 | **Development Bank of Japan** 🏦 | JP state-owned | 2025-03-31 | ¥ billions | 21,549.3 | 1,162.3 | n/a | 466.3 | 17,387.3 | Bonds 6,606.8 + Borrowings 9,720.6 | 4,161.9 | 929.2 (+ 1,602.0 special reserve) | **~US$135.1 B** |
| 4 | **Itochu** 🏢 | JP 8001 | 2025-03-31 | ¥ millions | 15,134,264 | 549,573 | n/e | n/e | ~9,379,192 | 2,723,640 (non-current) | 5,755,072 | n/e | **~US$94.9 B** |
| 5 | **Applied Materials** | US AMAT | 2025-10-26 | US$ thousands | 36,299,000 | 7,241,000 | 5,915,000 | 4,610,000 | 15,884,000 | 6,455,000 | 20,415,000 | n/e | **~US$36.3 B** |
| 6 | **Shin-Etsu Chemical** | JP 4063 | 2025-03-31 | ¥ millions | 5,636,601 | n/e | n/e | n/e | ~799,016 | 33,904 (all interest-bearing debt) | 4,837,585 (Net assets) | n/e | **~US$35.3 B** |
| 7 | **ASE Holdings** | TW 3711 | 2024-12-31 | NT$ millions (summary) | 740,697.8 | ~76,493 (from cash-flow) | n/e | 312,531.5 | 394,911.2 | n/e | 345,786.6 | n/e | **~US$23.5 B** |
| 8 | **MediaTek** | TW 2454 | 2024-12-31 | NT$ thousands | 697,867,530 | n/e | n/e | 56,917,043 | 292,812,183 | n/e | 405,055,347 | 299,907,267 | **~US$22.1 B** |
| 9 | **Lam Research** | US LRCX | 2025-06-29 | US$ thousands | 21,345,260 | 6,390,659 | 4,307,991 | n/e | 11,483,641 | 3,730,194 (+754,311 current) | 9,861,619 | n/e | **~US$21.3 B** |
| 10 | **UMC** | TW 2303 | 2024-12-31 | NT$ thousands | 570,200,677 | n/e | n/e | 279,059,037 | 192,015,673 | n/e (NC liab 116,755,484) | 378,185,004 | 226,848,505 | **~US$18.1 B** |
| 11 | **Delta Electronics** | TW 2308 | 2024-12-31 | NT$ thousands | 531,897,717 | ~117,459,250 | n/e (in CA 310,924,848) | 115,710,424 | 252,332,381 | n/e (NCL 100,049,255) | 279,565,336 | 141,467,800 | **~US$16.8 B** |
| 12 | **KLA** | US KLAC | 2025-06-30 | US$ thousands | 16,067,926 | 2,078,908 (+ 2,415,715 mkt sec.) | 3,212,149 | 1,252,775 | 11,375,473 | 5,884,257 | 4,692,453 | 2,179,330 | **~US$16.1 B** |
| 13 | **WPG Holdings** | TW 3702 | 2024-12-31 | NT$ thousands | 405,992,805 | 22,688,320 | 152,788,754 | 11,799,184 | 321,622,146 | 31,288,120 (+ 15,624,687 current) | 84,370,659 | n/e | **~US$12.9 B** |
| 14 | **Medipal Holdings** 🏢 | JP 7459 | 2025-03-31 | ¥ millions | 1,824,984 | n/e | n/e | n/e | ~1,067,037 | n/e | 757,947 (Net assets) | n/e | **~US$11.4 B** |
| 15 | **HCL Technologies** | IN HCLTECH | 2025-03-31 | ₹ crores | 105,544 | 8,245 (+ 13,044 bank bal. + 7,473 invts) | 133 | 4,501 | 35,871 | 70 (+ 2,221 current) | 69,673 | n/e | **~US$11.2 B** |
| 16 | **ZDT / Zhen Ding Tech** | TW 4958 | 2024-12-31 | NT$ thousands | 265,993,292 | n/e | n/e | 110,172,595 | 113,969,682 | n/e (NCL 44,765,432) | 152,023,610 | 59,158,398 | **~US$8.4 B** |
| 17 | **JSR Corp** (post-LBO) | JP 4185 | 2025-03-31 | ¥ millions | 1,142,060 | n/e | n/e | n/e | 772,380 | 478,568 | 338,594 | n/e | **~US$7.2 B** |
| 18 | **Nanya Technology** | TW 2408 | 2024-12-31 | NT$ thousands | 206,706,317 | 61,902,779 | n/e (~+NT$7.7B YoY) | n/e | 41,653,042 | n/e (NT$4B bonds issued 2024) | 165,053,275 | 97,477,979 | **~US$6.5 B** |
| 19 | **Ebara** | JP 6361 | 2024-12-31 | ¥ millions | 1,005,085 | 171,031 | n/e | n/e | n/e | n/e | 485,336 (Net assets) | 272,382 | **~US$6.3 B** |
| 20 | **ASM International** | NL ASM | 2025-12-31 | € millions | 5,337.0 | 1,026.9 | 552.1 | 573.2 | 1,331.3 | n/e | 4,005.7 | n/e | **~US$6.2 B** |
| 21 | **UACJ** 🏢 | JP 5741 | 2025-03-31 | ¥ millions | 970,006 | n/e | n/e | n/e | ~650,418 | 340,700 (interest-bearing total) | 319,588 | n/e | **~US$6.1 B** |
| 22 | **PSMC / Powerchip** | TW 6770 | 2024-12-31 | NT$ thousands | 188,920,850 | ~18,348,499 (opening 2025) | n/e | 124,236,098 | 100,275,185 | n/e (NCL 69,850,428) | 88,645,665 | 19,534,425 | **~US$6.0 B** |
| 23 | **Advantest** | JP 6857 | 2025-03-31 | ¥ millions | 854,210 | 262,544 | n/e | n/e | ~347,671 | n/e | 506,539 | n/e | **~US$5.4 B** |
| 24 | **Nagase & Co** 🏢 | JP 8012 | 2025-03-31 | ¥ millions | 808,143 | 66,310 | 166,224 | 91,671 | 401,682 | Bonds 40,000 + LT loans 64,926 | 406,459 (Net assets) | 312,244 | **~US$5.1 B** |
| 25 | **VIS / Vanguard** | TW 5347 | 2024-12-31 | NT$ thousands | 148,705,702 | n/e | n/e | n/e | 80,038,677 | n/e | 68,667,025 (calc.) | n/e | **~US$4.7 B** |
| 26 | **Seino Holdings** 🏢 | JP 9076 | 2024-03-31 (stale 1 yr) | ¥ millions | 689,525 | 75,378 | 20,615 | 345,655 | 253,947 | 40,501 | 435,578 (Net assets) | 321,349 | **~US$4.3 B** |
| 27 | **Shimadzu** | JP 7701 | 2025-03-31 | ¥ millions | 672,177 | 137,190 | n/e | n/e | ~225,014 | 1,372 (interest-bearing total) | 447,163 | n/e | **~US$4.2 B** |
| 28 | **Realtek Semiconductor** | TW 2379 | 2024-12-31 | NT$ thousands | 113,896,730 | 14,812,459 | n/e | n/e (NCA 29,238,723) | 60,939,242 | n/e (NCL 2,978,267) | 52,957,488 | 40,934,415 | **~US$3.6 B** |
| 29 | **Misumi Group** | JP 9962 | 2025-03-31 | ¥ millions | 419,574 | n/e | n/e | n/e | ~70,290 | n/e (interest coverage 386.7×) | 349,284 | n/e | **~US$2.6 B** |
| 30 | **Phison** | TW 8299 | 2024-12-31 | NT$ thousands | 69,339,167 | 19,982,162 | 24,614,049 | 7,745,010 | 20,273,104 | 5,611,070 (bonds) | 49,066,063 | 34,283,152 | **~US$2.2 B** |
| 31 | **Kokusai Electric** | JP 6525 | 2025-03-31 | ¥ millions | 341,512 | n/e | n/e | n/e | ~145,344 | n/e (interest-bearing 60,184) | 196,168 | n/e | **~US$2.1 B** |
| 32 | **Lintec** | JP 7966 | 2025-03-31 | ¥ millions | 340,471 | 50,703 | n/e | 116,931 | ~94,345 | 3,794 | 246,126 (Net assets) | n/e | **~US$2.1 B** |
| 33 | **Lasertec** | JP 6920 | 2025-06-30 | ¥ millions | 329,601 | 86,087 | n/e | n/e | 119,701 | ~1,782 (NCL only) | 209,900 (Net assets) | n/e | **~US$2.1 B** |
| 34 | **WIN Semiconductors** | TW 3105 | 2024-12-31 | NT$ thousands | 64,258,757 | n/e | n/e | 28,264,866 | 25,120,706 | n/e (NCL 17,517,468) | 39,138,051 | 17,997,492 | **~US$2.0 B** |
| 35 | **Disco** (STALE FY2019) | JP 6146 | 2020-03-31 | ¥ millions | 274,325 | 87,909 | 50,368 | 93,415 | 47,435 | 0 (debt-free) | 226,890 (Net assets) | 181,239 | **~US$1.7 B (balance stale)** |
| 36 | **Himax** | TW HIMX | 2024-12-31 | US$ thousands | 1,639,521 | 218,148 | 158,746 | 121,280 | 743,194 | 28,500 | 896,327 (calc.) | n/e | **~US$1.64 B** |
| 37 | **Accretech** | JP 7729 | 2025-03-31 | ¥ millions | 237,952 | 34,457 | n/e | n/e | n/e | n/e | n/e | n/e | **~US$1.5 B** |
| 38 | **Marketech International** | TW 6196 | 2024-12-31 | NT$ thousands | 46,657,323 | ~11,442,714 | n/e | 3,445,599 | 34,631,453 | n/e (NCL 5,081,921) | 12,025,870 | ~7,371,428 | **~US$1.5 B** |
| 39 | **ChipMOS** | TW 8150 | 2024-12-31 | NT$ thousands | 45,379,852 | n/e | n/e | 19,996,760 | 20,305,618 | n/e | 25,074,234 (calc.) | n/e | **~US$1.4 B** |
| 40 | **JEOL** | JP 6951 | 2025-03-31 | ¥ millions | 222,486 | 34,605 | n/e | n/e | 85,833 | n/e | 136,653 | n/e | **~US$1.4 B** |
| 41 | **Sigurd Microelectronics** | TW 6257 | 2024-12-31 | NT$ thousands | 39,634,648 | 11,249,315 | 414,994 | 15,440,055 | 16,585,938 | Bonds 2,987,713 + LT loans 5,521,913 | 23,048,710 | 12,449,818 | **~US$1.3 B** |
| 42 | **Topco Scientific** | TW 5434 | 2024-12-31 | NT$ thousands | 37,274,912 | n/e | n/e | 9,375,455 | 19,268,399 | n/e (NCL 4,314,522) | 18,006,513 | 11,760,485 | **~US$1.2 B** |
| 43 | **Sanki Engineering** (STALE FY22) | JP 1961 | 2023-03-31 | ¥ millions | 172,305 | 24,949 | n/e | 13,037 | 81,392 | 1,400 | 90,913 (Net assets) | 73,051 | **~US$1.1 B (balance stale)** |
| 44 | **Ardentec** | TW 3264 | 2024-12-31 | NT$ thousands | 33,688,840 | 2,161,694 | n/e | 21,398,030 | 15,389,766 | n/e (NCL 9,752,014) | 18,299,074 | 12,392,520 | **~US$1.1 B** |
| 45 | **ITRI** 🎓 (nonprofit) | TW research inst | 2024-12-31 | NT$ millions | 28,486 | 6,608 | 1 | 8,683 | 12,935 | n/e (NCL 2,974) | 15,551 (Funds+Surplus) | 12,345 (Accum. Surplus) | **~US$902 M** |
| 46 | **SNK / Shin Nippon Air Tech** | JP 1952 | 2025-03-31 | ¥ millions | 118,166 | n/e | n/e | n/e | 48,872 | n/e (D/E 0.1×) | 69,226 (Net assets) | n/e | **~US$741 M** |
| 47 | **Gudeng Precision** (filename mislabeled "Leatec") | TW 3680 | 2024-12-31 | NT$ thousands | 21,366,322 | n/e | n/e | 7,975,505 | 9,838,248 | n/e (NCL 5,608,651) | 11,528,074 | 1,484,989 | **~US$677 M** |
| 48 | **Taiwan Mask Corp** | TW 2338 | 2024-12-31 | NT$ thousands | 20,815,145 | n/e | n/e | 10,382,141 | 16,743,237 | n/e (NCL 7,290,989) | 4,071,908 | 1,445,786 | **~US$659 M** |
| 49 | **Orient Semiconductor (OSE)** | TW 2329 | 2024-12-31 | NT$ thousands | 19,535,717 | 4,445,344 | 1,571,803 | 6,455,962 | 7,965,664 | 1,009,786 (+ 372,122 current) | 11,570,053 | 3,934,319 | **~US$619 M** |
| 50 | **Egis Technology** | TW 6462 | 2024-12-31 | NT$ thousands | 18,970,864 | ~1,663,563 | n/e | 234,069 | 8,518,065 | n/e (NCL 1,751,459) | 10,452,799 | 1,329,158 | **~US$601 M** |
| 51 | **Shibaura Mechatronics** (file mislabeled "Shibuara") | JP 6590 | 2025-03-31 | ¥ millions | 95,244 | n/e | n/e | n/e | ~47,927 | n/e | 47,317 (Net assets) | n/e | **~US$597 M** |
| 52 | **INFICON Holding** (half-year) | CH INFN | 2025-06-30 (interim) | US$ thousands | 588,752 | 141,662 | 157,525 | 144,290 | 204,282 | n/e | 384,470 | 381,695 | **~US$589 M** |
| 53 | **AP Memory** | TW 6531 | 2024-12-31 | NT$ thousands | 13,008,288 | 4,188,544 (+ 4,752,325 term dep.) | 1,203,177 | 66,155 | 1,101,231 | n/e (NCL 136,212) | 11,907,057 | 4,719,073 | **~US$412 M** |
| 54 | **CSUN Manufacturing** | TW 2467 | 2024-12-31 | NT$ thousands | 10,772,494 | n/e | n/e | 1,059,732 | 5,521,706 | 2,376,534 (LT liab.) | 5,250,788 | 1,587,739 | **~US$341 M** |
| 55 | **Alcor Micro** | TW 8054 | 2024-12-31 | NT$ thousands | 6,980,423 | 1,268,876 | n/e | 161,711 | 2,665,871 | n/e (NCL 686,281) | 4,314,552 | (290,996) deficit | **~US$221 M** |
| 56 | **eMemory Technology** | TW 3529 | 2024-12-31 | NT$ thousands | 4,458,552 | n/e (in CA 3,636,784) | n/e (IP licensing) | 482,569 | 873,873 | n/e (NCL 13,970) | 3,584,679 | 2,701,085 | **~US$141 M** |
| 57 | **Gallant Precision** | TW 5443 | 2024-12-31 | NT$ thousands | 3,864,077 | ~628,918 | n/e | n/e | 2,141,470 | n/e (NCL 477,852) | 1,722,607 | 649,591 | **~US$122 M** |
| 58 | **Richwave Technology** | TW 4968 | 2024-12-31 | NT$ thousands | 3,367,925 | ~1,013,365 | n/e | 158,408 | 807,910 | n/e (NCL 96,954) | 2,560,015 | 780,335 | **~US$107 M** |
| 59 | **Spirox** | TW 3055 | 2024-12-31 | NT$ thousands | 2,592,266 | n/e | n/e | 589,402 | 464,919 | n/e (NCL 147,423) | 2,127,347 | 784,819 | **~US$82 M** |
| 60 | **M31 Technology** | TW 6643 | 2024-12-31 | NT$ thousands | 2,159,212 | ~208,901 (derived) | n/e (IP licensing) | 591,847 | 239,908 | n/e (NCL 22,690) | 1,919,304 | 754,609 | **~US$68 M** |
| 61 | **Favite Inc.** | TW 3479 | 2024-12-31 | NT$ thousands | 1,639,426 | ~186,545 | n/e | 412,369 | 479,616 | 185,543 (LT loan) | 1,159,810 | 274,020 | **~US$52 M** |
| 62 | **Megawin Technology** | TW 3064 | 2024-12-31 | NT$ thousands | 705,024 | 96,326 | 72,093 | 148,104 | 271,411 | 189,141 (corp. bonds) | 433,613 | (46,400) deficit | **~US$22 M** |

Some companies mentioned in earlier versions of this file are partially disclosed and remain `n/e` across most columns pending a re-extraction or external data:

| # | Company | Ticker | Status | What we have |
|---|---|---|---|---|
| 63 | **KYEC (King Yuan Electronics)** | TW 2449 | Only Q4'25 investor-deck in folder | Market cap NT$302,629M; no BS line items. Refer to TWSE MOPS for FY24 AR. |
| 64 | **Fuji Electric** | JP 6504 | Only single-page report excerpts in folder | Equity ¥691.8 B; net interest-bearing debt ¥42.2 B; other BS lines `n/e`. |
| 65 | **Shinagawa Refractories** | JP 5351 | Only 37-pp 2024 IR presentation deck | Net sales ¥144.1 B; ordinary income ¥14.9 B; BS not in deck. |
| 66 | **Episil Technologies** | TW 3707 | File in folder is a July-2024 press release, not an AR | BS not available from this PDF. |
| 67 | **Creating Nano Technologies** | TW 4174 | File is scanned image-only (no text layer) | `pdftotext` returns 0 characters. Requires OCR (tesseract) to proceed. |
| 68 | **Weltrend Semiconductor** | TW 2436 | File is 2024 Sustainability / CSR report | Discloses revenue (NT$3,094,619k) but no BS. |

---

## Cross-company sizing (top 25 by ≈USD total assets)

Sorted for quick pecking-order intuition. The top is dominated by financial institutions and diversified conglomerates — **TSMC is the largest pure-play semiconductor entity** in the folder.

| Rank | Entity | ~USD Total Assets | Category |
|---|---|---|---|
| 1 | Fubon Financial | ~$382.2 B | 🏦 TW bank/insurance holding |
| 2 | TSMC | ~$211.9 B | TW foundry |
| 3 | Development Bank of Japan | ~$135.1 B | 🏦 JP state-owned policy bank |
| 4 | Itochu | ~$94.9 B | 🏢 JP general trading house |
| 5 | Applied Materials | ~$36.3 B | US WFE |
| 6 | Shin-Etsu Chemical | ~$35.3 B | JP semi materials (silicon wafers) |
| 7 | ASE Holdings | ~$23.5 B | TW OSAT (world's largest) |
| 8 | MediaTek | ~$22.1 B | TW fabless |
| 9 | Lam Research | ~$21.3 B | US WFE |
| 10 | UMC | ~$18.1 B | TW foundry |
| 11 | Delta Electronics | ~$16.8 B | TW power systems / ODM |
| 12 | KLA | ~$16.1 B | US process control |
| 13 | WPG Holdings | ~$12.9 B | TW IC distribution (asset-heavy: NT$167B receivables + NT$153B inventory) |
| 14 | Medipal Holdings | ~$11.4 B | 🏢 JP pharma distribution (not semi — context peer for DBJ/Itochu scale) |
| 15 | HCL Technologies | ~$11.2 B | IN IT services / engineering |
| 16 | ZDT / Zhen Ding Tech | ~$8.4 B | TW HDI/PCB (Apple supplier) |
| 17 | JSR (post-LBO) | ~$7.2 B | JP semi materials (photoresists) — **balance sheet inflated 48% YoY from JIC take-private LBO financing** |
| 18 | Nanya Technology | ~$6.5 B | TW DRAM |
| 19 | Ebara | ~$6.3 B | JP semi CMP/pumps + broader industrials |
| 20 | ASM International | ~$6.2 B | NL ALD pure-play |
| 21 | UACJ | ~$6.1 B | 🏢 JP aluminum (not semi — context peer) |
| 22 | PSMC / Powerchip | ~$6.0 B | TW DRAM / mature-node foundry |
| 23 | Advantest | ~$5.4 B | JP test equipment |
| 24 | Nagase & Co | ~$5.1 B | 🏢 JP chemical trading house (semi materials reseller) |
| 25 | VIS / Vanguard | ~$4.7 B | TW specialty foundry (VSMC JV ramp) |

Rank changes since the previous version of this file (which used round FX estimates of NT$32.5, ¥151, €0.93, ₹83):

- **AMAT jumps past Shin-Etsu** to #5. JPY weakened from 151 to 159.48, cutting Shin-Etsu's USD figure by ~5%, while AMAT's USD is unchanged.
- **HCL Technologies drops from #13 to #15**, below WPG Holdings and Medipal. INR weakened sharply (83 → 94.11), cutting HCL's USD figure by ~12%.
- **ASM International rises from #22 to #20**. EUR strengthened (0.93 → 0.855) lifting its USD figure by ~9%.
- **Nagase** moves into the top 25 at #24 (proper sort; previously sorted out of order at row 29 in the v2 file).
- **TSMC / Fubon / DBJ / Itochu** all shifted up or down a few percent each, but their tier placements remain unchanged.

---

## What the table reveals

### 1. Pure-play semi peak is TSMC

The financial institutions and diversified houses above TSMC (Fubon, DBJ, Itochu) are NOT comparable to the rest of the table — they aggregate insurance float, loan books, or pan-industry trading assets. Of actual semi companies, **TSMC's ~$212 B dwarfs #2 AMAT by 5.8×** and the #3 semi entity (ASE, $23.5 B) by 9×. TSMC's PP&E alone (~$102 B at the current rate) is bigger than every other non-TSMC semi total-assets figure here.

### 2. Two balance-sheet archetypes in WFE

**Foundries** (TSMC, UMC, PSMC) carry 48–66% of their assets as PP&E. These are industrial capital-deployment businesses.

**WFE / process control** (AMAT, Lam, KLA, ASM Intl) carry only 10–15% of assets as PP&E. They're IP + design + assembly businesses. Same industry label, completely different economic engine.

Compare asset turnover (rough, using most-recent disclosed revenue):
- TSMC: $90 B revenue / $212 B assets → 0.42×
- AMAT: $28.4 B revenue / $36.3 B assets → 0.78×
- KLA: $12 B revenue / $16.1 B assets → 0.74×
- Lam: $18.4 B revenue / $21.3 B assets → 0.86×

### 3. OSAT/test plant-heavy, fabless asset-light

- **ZDT (HDI/PCB for Apple)** — $8.4 B assets, PP&E 41% of assets.
- **Ardentec** — $1.1 B assets, **PP&E 63% of assets** (test house PP&E intensity).
- **ChipMOS** — $1.4 B assets, PP&E 44% of assets.
- **eMemory** (IP licensing, pure fabless) — $141 M assets, PP&E 11% of assets, zero inventory, ~0% debt.
- **AP Memory** (PSRAM fabless) — $412 M assets, **PP&E 0.5% of assets**, cash+term deposits = 69% of assets.
- **M31 Technology** (semi IP licensing) — $68 M assets, PP&E 27%, zero inventory.

### 4. Cash hoards

Companies running >20% of assets as cash are mostly WFE and asset-light fabless:

- **AP Memory**: 69% of assets in cash + short-term investments.
- **Lam Research**: 30% cash.
- **Advantest**: 31% cash (¥262,544 M of ¥854,210 M).
- **AMAT**: 20% cash.
- **ASM Intl**: 19% cash.
- **INFICON**: 24% cash.
- **Shimadzu**: 20% cash.

Foundries and OSATs run much tighter — cash is reinvested into PP&E.

### 5. Debt structures to watch

- **JSR**: long-term debt jumped from ¥81 B (FY23) to **¥479 B (FY24)** — 5.9× — reflecting the 2024 JIC Capital take-private LBO. Total assets +48% YoY for the same reason. This is one-time capital structure reshuffling, not operational growth.
- **UACJ**: interest-bearing debt ¥340.7 B = 107% of equity. Aluminum is a cyclical, leveraged business — not a semi-peer ratio.
- **Sigurd**: Bonds ¥2.99 B + LT loans ¥5.52 B = notable ~22% of total assets (unusually leveraged for an OSAT).
- **Phison**: NT$5.6 B in new convertible bonds issued 2024 ("second CB") — watch for dilution risk when they convert.
- **Himax**: strikingly debt-light at ~2% LT debt / total assets. Classic fabless.
- **Disco** (FY19 data): zero long-term debt. Disco has remained debt-free into current periods per external sources.
- **Shin-Etsu**: ¥33.9 B total interest-bearing debt on ¥5.6 T assets = 0.6%. Near-zero leverage despite being the world's largest silicon-wafer supplier.

### 6. Two IDM DRAM companies, two stories

**Nanya Tech** (TW 2408): $6.5 B total assets, FY2024 operating loss NT$10.55 B. Carries NT$21 B in short-term bank borrowings. Added NT$4 B in corporate bonds in 2024 to shore up the balance sheet.

**PSMC / Powerchip** (TW 6770): $6.0 B total assets, FY2024 net loss NT$6.78 B from P5/Tongluo depreciation + China mature-node price competition. Retained earnings fell 25% YoY from the loss.

The DRAM trough of 2023-2024 cut both balance sheets by drawing down retained earnings and raising leverage. This is a useful reminder that "commodity memory" companies look very different from specialty / IP fabless on the BS.

### 7. Balance-sheet size does not equal revenue rank

**WPG Holdings** has **$12.9 B in total assets** — bigger than HCL Tech, Medipal, and most Japanese equipment companies. But it's an **IC distributor**: the balance sheet is dominated by **NT$167 B accounts receivable + NT$153 B inventory**. Distribution businesses swell the BS without adding equity-value proportionately (WPG total equity is only NT$84 B = 21% of assets; debt ratio ~79%). Comparing WPG to, say, Advantest (same rough USD-total-assets range, but 59% equity-to-assets) without category context would be misleading.

### 8. Research institute / nonprofit disclosures

**ITRI** does publish a balance sheet — rare for a government-backed research institute — but uses nonprofit terminology ("Funds and Surplus" instead of "Equity", "Accumulated Surplus" instead of "Retained Earnings"). ~$902 M total assets with PP&E at ~30% (labs, equipment).

### 9. FX sensitivity is real

Revisiting the same balance sheets under updated rates (Frankfurter + open.er-api.com, 2026-04-23/24) vs. the round-number estimates used in v2 of this file:

- Shin-Etsu USD value fell **~5%** purely from JPY weakness (151 → 159.48).
- HCL Technologies fell **~12%** in USD on INR weakness (83 → 94.11).
- ASM International rose **~9%** in USD on EUR strength (0.93 → 0.855).
- TWD-denominated companies rose **~3%** (32.5 → 31.576).

Large multi-year comparisons across these currencies without normalizing to a single-date FX series will over- or under-state growth. A fair cross-year comparison should pick one reference FX date and hold it fixed — or compare in native currency.

---

## Files processed — status matrix

Reference list of every PDF in the folder and how it was handled. Click-through from here when adding new extractions.

### Annual / integrated reports with extractable BS (in table above)

See rows 1–62 above, plus the partially-disclosed rows 63–68.

### PDFs explicitly skipped: product brochures / catalogues / spec sheets (no BS data)

- `2025 Nanya Tech Product Brochure_V4.pdf`
- `2025_0923_TGV-solutions_DataSheet.pdf` (Manz)
- `2025_EN_IC_substrate_flyer_1027.pdf` (Manz)
- `2025_ScanBox_BR_Digital_EN.pdf.pdf` (ZEISS)
- `20250826_zeiss_aramis_brochure_digital_en.pdf.pdf`
- `241210_zeiss_tritop_brochure_en.pdf.pdf`
- `2026H1_Megawin_Brochure(EN)_v1.0.pdf`
- `AMS OSRAM sensor biomonitoring SFH 7072_EN.pdf`
- `ARM_Cortex-R52_datasheet.pdf`
- `Canon-Broadcast-CINEMA-Lens-Lineup.pdf`
- `CXL-Specification_rev4p0_ver1p0_2026February26_clean_evalcopy_v2.pdf`
- `CXL_4.0-Webinar_December-2025_FINAL.pdf`
- `CXL_Q2-2025-Webinar_FINAL.pdf`
- `Flyer-20221128-ITW-Lumex-EN-No-W_SD.pdf`
- `Flyer_OMNIA_GC_220-180_A4_EN.pdf.pdf`
- `Intel Core Ultra Series 3 Processors - Product Brief v1.pdf`
- `LINEUP2026 MICRONICS JAPAN.pdf`
- `MANZ 2025_0923_TGV-solutions_DataSheet.pdf`
- `MANZ 2025_EN_IC_substrate_flyer_1027.pdf`
- `Manz_brochure_Contract-Manufacturing_EN-4.pdf`
- `SENJU 2025_soldering_materials_catalogue.pdf`
- `SG022_2026.pdf` (Richtek product selection guide)
- `SPE_GeneralCatalog_Digital_251209 Screen japan.pdf`
- `htcvacuum-valves 2021 product guide.pdf`
- `sty_pamphlet_en S-TAKAYA corporation japan 2021.pdf`
- `zeiss_atos_5_brochure_en.pdf.pdf`
- `AS_162388_TG_689277_KA_US_2105_1.pdf` (KEYENCE corporate profile)
- `HTC vacuum en-company-profile.pdf`
- `GLOBAL FOUNDRIES-At-A-Glance-Feb2026.pdf` (1-page company summary; need GF 10-K for BS)
- `HBM_GPU_AI_Trends_2026.pdf` (industry report)
- `INTERACTION_JP_Medium-Term-Business-Plan（2024-2028）.pdf`
- `ULVAC_CorporateProfile_en_2025.pdf`
- `naka_e HITACHI HIGH-TECH future.pdf` (future-vision doc)
- `profile-en-pdf HITACH HIGH-TECH.pdf`
- `About_ISTI.pdf` (Taiwan gov policy center)
- `AJINOMOTO FINE INC ABF-presentation.pdf` (2019 product deck)
- `JEITA export report 2026.pdf`
- `2025120101-7640.pdf` (SEAJ quarterly world stats)
- `2026010105-7725.pdf` (SEAJ Japan monthly billings — English)
- `2026010106-7715.pdf` (SEAJ Japan monthly billings — Japanese FPD)

### Quarterly / investor-day decks with summary BS or P&L highlights only

- `01_25.3Q_Consolidated_Financial_Results_e.pdf` → Iwatani (JP 8088) 3Q FY25 results — summary highlights
- `02_25.3Q_Supplementary_Explanation_e.pdf` → Iwatani supplement
- `26third_all_e NIKON 3Q 2025 Result.pdf`
- `4Q25-investor-conference_EN_Final Windbond 2025.pdf` (Winbond)
- `ALL_Analyst_Day_2025_IR_SITE_NEW TERADYNE investor day Mar 2025.pdf`
- `Teradyne_EC Q4'25 Slides Feb2026.pdf`
- `conf2025e CANON fy2025 result.pdf`
- `phase7-e CANON presentation JAN 2026.pdf`
- `DAIFUKU_FY2025Q4e_presentation.pdf`
- `DAITRON_E_2025Q4_FR.pdf`
- `PANASONIC INDUSTRY ir-pre2024_pid_e.pdf`
- `ORGANO Financial-Results-for-First-Half-of-Fiscal-Year-Ending-March-31-2026.pdf`
- `Financial_Results_Briefing_Materials_for_the_Fiscal_Year_Ended_March_2025 RIKKEN KEIKI.pdf`
- `Integrated_report_2025_A4_eng RIKKEN KEIKI 2025.pdf`
- `KYEC(2449)_4Q25 Investor update_English.pdf` — see row 63 above
- `2025Q3-Balance-Sheet.pdf` → Alcor Micro Q3'25 standalone BS (supplements row 55)

### File-specific issues

| File | Issue |
|---|---|
| `ALCOR fabless 2024_AnnualReport_EN.pdf` | Byte-identical duplicate of `2024_AnnualReport_EN.pdf` (Alcor Micro). MD5 af2117... |
| `MIC taiwan annual report 2024 2505091655322f091.pdf` | Content is Marketech (TW 6196), not MIC / Microelectronics Technology (TW 3021). Filename misleading; file is a re-copy of `MARKETECH annual report 2024 2505091655322f091.pdf`. |
| `2024_WPG_annual_report_E.pdf` and `2024_WPG_annual_report_E (1).pdf` | Byte-identical duplicates (1,456,081 bytes each). |
| `2024_Annual Report.pdf` and `2024_Annual Report ITRI taiwan.pdf` | Byte-identical duplicates (9,595,444 bytes each). Same ITRI report. |
| `LAM+RESEARCH+CORP_BOOKMARKS_2025_V1 annual report 2025.pdf` and `LAM+RESEARCH+CORP_BOOKMARKS_2025_V1.pdf` | Byte-identical duplicates (5,311,599 bytes each). |
| `EPISIL_News_20240701 annual report 2024.pdf` | Actually a 2-page press release, not an annual report. |
| `CREATING NANOTECH 2025CNT_pdfc_7917259_132442_3461176.pdf` | Image-only PDF (no embedded text). Requires OCR. |
| `Weltrend 2024 Sustainability Report.pdf` | CSR report; only revenue split disclosed, no BS. |
| `2024 Shinagawa Update_20240530.pdf` | 37-pp IR presentation deck, not AR. |
| `FUJI_ELECTRIC_ar2025_02_02_e.pdf`, `FUJI_ELECTRIC_ar2025_02_04_e.pdf` | Only "Business Areas" and "Value Creation" cutouts from the FY25 report — no BS section. |
| `Los Angeles County Completion Certificate - June 2, 2026 Statewide Direct Primary Election.pdf` | Misfiled — unrelated election document. |

### Ticker / entity corrections picked up during extraction

| Company / file | Original label | Corrected |
|---|---|---|
| ZDTCo / Zhen Ding Tech | "TW 6643" | **TW 4958** (6643 is M31) |
| CSUN Manufacturing | "TW 3532" | **TW 2467** (志聖工業) |
| Episil | "TW 2452" | **TW 3707** (file itself is a press release — BS not extractable) |
| Leatec Fine Ceramics | "TW 8088" | File content is **Gudeng Precision (TW 3680)** — the AR inside is mislabeled in filename |
| Shibaura Machine | "JP 6104" | File content is **Shibaura Mechatronics (JP 6590)** — different company despite similar name |
| SNK Corp | "JP 1952 assumed = Sanoh 7487 or Sanki 1961" | **Shin Nippon Air Technologies (JP 1952)** — HVAC/facilities engineering, distinct from Sanki Engineering (1961), both are separately covered above |

---

## Methodology

| Step | Detail |
|---|---|
| **Extraction tool** | `pdftotext -layout -f <start> -l <end>` on page ranges targeted at each report's financial-statements section |
| **Target page ranges** | TW annual reports: BS typically pages 90–250. US 10-Ks: BS pages 60–90. JP integrated reports: 10-year / 11-year highlights pages 60–120. |
| **Locating the BS** | `grep -in "total assets\|total liabilities\|total equity\|net assets\|cash and cash\|inventories\|property, plant"` on the extracted text |
| **Column-order verification** | Some TW reports list 2024 first, others 2023 first. Each row checked against the stated YoY change-% column, or against the heading line, to confirm the correct year is in the "current" column. |
| **Units** | TW annual reports: NT$ thousands. US 10-Ks: US$ thousands or millions. JP integrated reports: ¥ millions (DBJ uses ¥ billions for summary). ASM: € millions. HCL Tech: ₹ crores. INFICON: US$ thousands (Swiss-domiciled but USD reporter). |
| **J-GAAP vs IFRS** | J-GAAP reporters disclose "Net assets" (includes NCI) where IFRS/US-GAAP show "Total equity." Reported in the same column with label noted. |
| **Consolidated vs parent** | Where both are shown, consolidated is chosen. |
| **USD conversion** | Applied using rates pulled on **2026-04-23** from [Frankfurter](https://frankfurter.dev/) (ECB reference rates) for JPY, EUR, INR, CHF, and on **2026-04-24 00:02 UTC** from [open.er-api.com](https://www.exchangerate-api.com/) for TWD (Frankfurter/ECB doesn't publish TWD). Rates: 1 USD = 159.48 JPY = 0.85514 EUR = 94.11 INR = 0.78476 CHF = 31.576278 TWD. |

---

## Changelog

- **2026-04-24 v2.1** — applied live FX rates from Frankfurter (ECB reference, 2026-04-23) for JPY, EUR, INR, CHF and from open.er-api.com (2026-04-24 00:02 UTC) for TWD (Frankfurter/ECB does not publish TWD). Updated all USD-equivalent values. Re-sorted mastersheet and top-25 rankings by the new USD figures. Notable shifts: AMAT passes Shin-Etsu at #5 (JPY weaker), HCL Tech drops below WPG & Medipal (INR weaker), ASM International rises into top 20 (EUR stronger). Added FX attribution block to Reading Notes and Methodology.
- **2026-04-23 v2** — expanded from 21 to 62 extracted companies via six parallel `pdftotext` subagent batches. Filled prior `n/e` rows for ASE, PSMC, Advantest, Lasertec, Shin-Etsu, JSR, Disco (FY2019 stale), Kokusai, KLA. Added banks (Fubon, DBJ), conglomerates (Itochu, Medipal, UACJ, Seino, Nagase), research institute (ITRI), Indian IT services (HCL Tech), Swiss equipment (INFICON), and ~40 TW / JP mid-and-small-cap annual reports. Added status matrix for all 134 PDFs. Corrected ticker / entity errors (ZDT→4958, CSUN→2467, Shibaura→Mechatronics 6590, SNK→Shin Nippon Air Tech 1952, Leatec file→Gudeng 3680). Flagged stale rows (Disco FY2019, Seino FY2024-03, Sanki FY2022-23). Flagged one-off LBO impact on JSR's FY2024 BS (+48% total assets).
- **2026-04-23 v1** — initial 21-company mastersheet.

---

*Final note on precision:* a balance sheet is a point-in-time photograph, not a trend. The YoY columns in individual cells give some feel for direction, but for multi-year trend see the securities filings (有価証券報告書 for Japan, MOPS for Taiwan, 10-K appendices for US). Cash-flow dynamics live in the earnings calls, not here.
