# TSMC Financial Cross-Validation Report

**Generated:** 2026-04-24
**Source:** `tsmc_financials.json` (Sonnet 4.6 vision extraction over 12 pages)
**Result: 11/11 checks passed**

## Reconciliations

| Check | Expected | Computed | Diff | Result |
|---|---|---|---|---|
| GrossProfit - OpExp = OpIncome (2024 consol) | 1377902 | 1377902 | 0 | **PASS** |
| OpIncome + NonOp = IncomeBeforeTax (2024 consol) | 1421459 | 1421459 | 0 | **PASS** |
| IncomeBeforeTax - TaxExp = NetIncome (2024 consol) | 1173244 | 1173244 | 0 | **PASS** |
| GrossProfit / NetRev = GrossMargin% (2024) | 56.1 | 56.1 | 0.0 | **PASS** |
| OpIncome / NetRev = OpMargin% (2024) | 47.6 | 47.6 | 0.0 | **PASS** |
| Cross-page: Consolidated revenue 2024 (p007 billions vs p064 millions) | 2894308 | 2894310.0 | 2.0 | **PASS** |
| Cross-page: Net income 2024 (p007 billions vs p064 consolidated millions) | 1173244 | 1173270.0 | 26.0 | **PASS** |
| Cross-page: Gross margin % 2024 (p007 vs p064 consolidated) | 56.1 | 56.1 | 0.0 | **PASS** |
| Cross-page: Dividend total 2024 (p007 annual vs p029 quarterly sum) | 14.0 | 14.0 | 0.0 | **PASS** |
| Unconsol: GrossProfit - OpExp = OpIncome (2024) | 1320930 | 1320930 | 0 | **PASS** |
| 2023 Consol: GrossProfit - OpExp = OpIncome | 938401 | 938401 | 0 | **PASS** |

## Notes

- All internal subtotal reconciliations (GrossProfit - OpEx = OpIncome; OpInc + NonOp = PreTax; PreTax - Tax = NetIncome) passed exactly at the NT$ million level, demonstrating the income-statement values extracted on p064 are internally consistent.
- Cross-page consistency between the infographic (p007, billions) and the detailed income statement (p064, millions) is within 0.01%% — differences are pure rounding artifacts.
- Gross margin and operating margin percentages computed from absolute values match printed percentages within 0.1pp.
- Quarterly dividend sum on p029 reconciles exactly to the annual NT$14.0/share on p007.
- **Confidence: high.** The extracted dataset is consistent both internally and across different presentations of the same data in the filing.
