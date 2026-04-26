# Vision-Extraction Prompt for Sonnet 4.6

Use this prompt template when dispatching vision extraction for a single
company's pages. The orchestrator passes `<key>`, `<source_pdf>`, and the
list of PNG paths.

---

## Task

You are extracting structured financial and personnel data from annual-report
pages of a single company. Read the PNG images for `<source_pdf>`, identify
the company name from the cover/header, and emit a single JSON file.

## Output schema

Write `graphify-financial/<key>/<key>_extraction.json` with this exact shape:

```json
{
  "company": "Full company name as printed (e.g., \"MediaTek Inc.\")",
  "ticker": "TWSE:2454,NYSE:... (best-effort, null if unknown)",
  "country": "Taiwan | Japan | USA | ... ",
  "industry": "ic_design | semiconductor_foundry | wfe_equipment | semiconductor_packaging_test | electronics_distribution | pharma_distribution | research_nonprofit | specialty_foundry | biometric_ic | photonics | materials | ...",
  "currency_default": "TWD | JPY | USD | EUR | KRW | ...",
  "fiscal_year_end": "December | March | September | ...",
  "extracted_by": "sonnet-4.6 vision",
  "extracted_at": "2026-04-25",
  "source_pdf": "<bucket>/<source_pdf>",
  "financial_pages": [
    {
      "page_id": "<key>_p<NNN>",
      "is_financial_table": true | false,
      "is_company_actual": true | false,
      "table_type": "income_statement | balance_sheet | cash_flow | 5_year_highlights | financial_highlights | segment_breakdown | revenue_breakdown | capital_structure | other | non_financial",
      "currency": "TWD | JPY | USD | ...",
      "unit": "thousands | millions | billions | as_is | shares | per_share",
      "metrics": [
        {"name": "Net revenue", "values": {"2024": 12345.6, "2023": 11000.0}}
      ],
      "notes": "Anything notable (e.g., consolidated vs unconsolidated, footnotes, units quirks)"
    }
  ],
  "people_pages": [
    {
      "page_id": "<key>_p<NNN>",
      "page_section": "Board of Directors | Management Team | etc.",
      "people": [
        {
          "name": "Full Name",
          "role": "Chairman & CEO",
          "type": "board_director | independent_director | senior_vp | executive_officer | vp | committee_member | other",
          "tenure_start": "YYYY (or null)",
          "education": "PhD EE, Stanford (or null)",
          "concurrent_roles": ["Chairman, X Foundation"],
          "notes": "Optional"
        }
      ]
    }
  ]
}
```

## Critical rules

1. **`is_company_actual = true`** ONLY if the page reports the SUBJECT
   company's own financials. Set to `false` for industry forecasts, market
   sizing tables, peer benchmarks, third-party data (IDC/Gartner/IC
   Insights/TrendForce). When in doubt, set `false` and explain in `notes`.
2. **Currency and unit are required** for any `is_financial_table=true`
   page. Look for "in NT$ thousands", "百萬元" (=millions of NTD),
   "(¥ million)", etc.
3. **Metric names**: copy as printed. Don't paraphrase. Preserve case.
   For Taiwanese reports, prefer the English column header.
4. **Years** are 4-digit strings ("2024"). For ROC dates, convert: 民國113
   = 2024.
5. **Multi-year tables**: include EVERY year in the `values` dict, even if
   the year is older than 2020.
6. **Skip image-only / branding pages**: set `is_financial_table=false`
   and `metrics=[]` with a brief `notes`.
7. **EPS / dividends per share** stay in their printed unit (per-share);
   do NOT convert to thousands or millions.

## Self-check before writing the JSON

- Every `metric.values[year]` is a number (or omit it).
- Subtotals reconcile: GP - OpEx = OpInc; Assets = Liab + Equity.
  If they don't, flag in `notes` and keep the printed values.
- People deduplicated within the file (same person on board + management
  page should appear once per page section, not duplicated).
