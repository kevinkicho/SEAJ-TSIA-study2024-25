---
layout: default
title: Known Limitations
nav_order: 8
---

# Known Limitations

*Every fab has process variations. Every mask has inspection blind spots. Every reticle has yield loss. This library is no different — below is the process-integration view of what this collection (and the docs built on top of it) cannot tell you. Read this before treating anything in `00_VALUE_CHAIN_MAP.md`, `01_DEEP_DIVE_ADVANCED_PACKAGING.md`, `02_KEY_FINANCIALS.md`, or `03_READING_LIST_GAPS.md` as ground truth.*

---

## 1. Process drift — the entire library has a ~12-month TTL

Every annual and integrated report in this folder describes a fiscal year that has **already ended**. The industry cycles faster than that: TSMC's CoWoS utilization, SK Hynix's HBM4 ramp, ASML's China shipments, NVIDIA's Blackwell/Rubin transitions, export-control rulings — all move material percentages of the WFE market *quarter over quarter*.

- As of **2026-04-23** (today), the freshest reports in this folder are dated late-2025; the oldest are from 2020 (Disco). That's 6–60 months of drift.
- **Consequence:** the *direction* of claims in the other docs (e.g., "Advantest is the purest HBM beneficiary") is durable. The *magnitudes* (e.g., "+60% revenue YoY") are last year's print.
- **Mitigation:** before treating any number as current, read the most recent quarterly earnings call transcript for that company.

---

## 2. Mask blind spots — selection bias you can map

What's in the folder is what was added. There is no process that enforces "you need ASML, SK Hynix, NVIDIA to complete the view." So the collection has **deliberate geographic concentration (JP + TW)** and **structural absences** that are visible once named:

- **Upstream:** no ASML → no EUV scanner supply picture.
- **Memory:** no SK Hynix / Samsung memory / Micron / Kioxia → the HBM thesis in `01_DEEP_DIVE_ADVANCED_PACKAGING.md` is resolved on the tool side but hollow on the supplier side.
- **End demand:** no NVIDIA / AMD / Broadcom → demand signal is inferred, not primary.
- **EDA/IP:** no Synopsys → EDA oligopoly view is half-complete.
- **China:** no SMIC / Naura / AMEC → counter-stack invisible.

The blind spot itself is information: this is a Japan-Taiwan axis library, built by someone interested in picks-and-shovels plus manufacturing scale. That shapes what questions it can and cannot answer.

---

## 3. Yield loss — what PDF extraction drops

The financial figures in `02_KEY_FINANCIALS.md` were pulled from the first ~40 pages of each PDF via `pdftotext -layout`. That tool preserves most table structure, but:

- Complex multi-line cells occasionally collapse.
- Charts and process-flow diagrams are images → invisible to text extraction. Sometimes the diagram *is* the data.
- Some Japanese reports render tables as bitmaps rather than vector text → unreadable until OCR is run.
- Footnotes tied to specific cells may be orphaned from their referents.
- Only the first ~40 pages were extracted; detailed segment tables and full financial statements usually start further back (typically pages 100–250).

**Consequence:** cells marked "—" in the financials table are extraction yield loss, not absence from the source. A targeted second pass on the financial-statement section of any specific report can fill them in — ask and I'll do it.

---

## 4. Primary-source slant — every report is a marketing artifact

Annual reports and integrated reports are not neutral documents. They are:

- Written by corporate communications, shaped by investor relations, and read before publication by a dozen reviewers including legal.
- Signed off by external auditors for *numbers*, but not for *strategic claims* ("monopoly," "#1 share," "leading edge").
- Annual in cadence → they amplify the year's story; they are structurally optimistic.
- ESG narratives in particular are marketing-grade, not compliance-grade. Claims like "first in Taiwan to achieve X" or carbon-reduction percentages should be cross-checked with independent sources before being cited.

**The library contains no sell-side research, expert-network calls, channel checks, customer interviews, or primary industry-association data (SEMI, WSTS, TrendForce).** That complementary layer is entirely absent.

---

## 5. Die-to-die variation — inconsistent disclosure across reports

Different companies disclose very different things:

| Report type | Typical disclosure quality |
|---|---|
| US 10-K (AMAT, KLA, Lam, Teradyne, ASM-US, GF) | SEC-mandated — consistent segments, strict GAAP |
| JP integrated report (Lasertec, Advantest, Disco, Ebara, JSR, Shin-Etsu) | METI/MoF-guided — more qualitative; non-GAAP "adjusted" metrics often headlined |
| TW annual report (TSMC, UMC, MediaTek, ASE, etc.) | TWSE-mandated — very deep governance / ownership / related-party tables; **lighter** segment economics |
| Presentation deck (Teradyne investor day, Daifuku Q4, Nikon 3Q) | In-house non-GAAP, selectively shown |
| Product brochure (Nanya, GF At-a-Glance) | Marketing-grade, almost no financials |

**Cross-company comparisons always carry apples-to-oranges risk.** Fiscal-year alignment alone is a landmine — Lasertec's "FY25" is 12 months ahead of AMAT's "FY25." The financials table tries to flag this, but the reader has to stay vigilant.

---

## 6. Noise floor — tangential and unidentified files

Signal is diluted by files that are off-topic or unlabeled:

- `Los Angeles County Completion Certificate - June 2, 2026 Statewide Direct Primary Election.pdf` → personal / voting record.
- `FUBON FINANCIAL annual report 2024...pdf` → Taiwan financial holding, unrelated to semis.
- `Canon-Broadcast-CINEMA-Lens-Lineup.pdf` → consumer optics.
- `2025120101-7640.pdf`, `2026010105-7725.pdf`, `2026010106-7715.pdf`, `2025Q3-Balance-Sheet.pdf`, `HY_Report_2025.pdf`, `AS_162388_TG_689277_KA_US_2105_1.pdf` → unidentifiable from filename alone.
- `desktop.ini` → OS metadata.

None of these corrupt the analysis, but they cost navigation time. A one-pass folder cleanup would reduce this.

---

## 7. Export controls — language-dependent information

Several Japanese niche suppliers (AI Mechatec, Ayumi, Meiritz, Raydent, Elionix, S-Takaya, Interaction) publish only *fragments* in English — product screenshots rather than complete disclosures. The fuller story for these companies is in Japanese only:

- Full annual filings (有価証券報告書 / yuho) are Japanese-only.
- IR Q&A transcripts, history pages, and trade-press coverage are Japanese-only.
- Industry-association publications (SEAJ monthly reports, JEITA breakouts) exist in English at a summary level but the underlying data is Japanese.

**Implication:** you have enough to know these companies *exist* and roughly what they do, but not enough to evaluate any of them rigorously on financials or competitive position.

---

## 8. Thermal budget — my own process margin (this analyst's limits)

Specific to the docs I produced (00–03):

- **Training cutoff:** my knowledge base ends January 2026. Any event after that — results calls, M&A announcements, new export-control rulings, tech roadmap pivots — I did not ingest. Today is 2026-04-23, so I have **~3 months of blind time**.
- **Filename inference:** for some companies (SNK Holdings, Adatech, the unnamed PDFs), I inferred role from filename alone. Some inferences may be wrong.
- **Depth limit:** I read the first ~40 pages of ~30 PDFs, not all ~130 files cover-to-cover. Claims of "monopoly" or "market share" are synthesized from my background industry knowledge *cross-referenced* with what each report asserts about itself. They are not independently audited.
- **No live data:** I cannot see today's stock prices, today's spot DRAM prices, or today's press wires.

---

## 9. Thesis gap — this is a library, not a view

The docs `00`–`03` are **descriptive**: what is in the folder, what the pieces mean, what to add. They are not **prescriptive**: there is no "buy / hold / sell," no allocation model, no forecast.

Going from library → view requires layers the folder cannot supply on its own:

- A **supply/demand model** for WFE by segment (lithography / etch / deposition / test / packaging equipment).
- A **valuation framework** (EV/revenue, EV/EBITDA, DCF) company-by-company.
- **Position sizing** / portfolio construction if this is investment-directed.
- A **catalyst calendar** — earnings dates, capex announcements, export-control review windows, industry conferences (Semicon West, SEMICON Japan, SEMICON Taiwan, ISSCC, IEDM).

If you want any of those as next-step deliverables, ask and I will structure them.

---

## 10. Uncertainty quantification — the part data can't fix

Everything above can be improved by adding more or fresher data. These cannot:

- **Geopolitical optionality.** US–China export controls, Taiwan Strait tensions, METI industrial-policy shifts, EU Chips-Act disbursement timing — low-probability, high-magnitude events that remap the value chain. No quantity of annual reports produces a base rate for them.
- **Technology S-curve surprises.** Nano-imprint lithography, glass substrates, photonic compute, chiplet protocol wars (UCIe vs. proprietary), memory-type transitions (HBM4 → HBM5 → CXL DRAM) — the folder can only *observe* these as they appear; it cannot predict which ones stick.
- **Customer-concentration unwinds.** NVIDIA dual-sourcing CoWoS, Apple swapping a supplier, hyperscalers insourcing ASICs — episode-specific events that don't show up in reports until they're already in motion.

**The library is a snapshot of a moving system. The questions that matter most are about what changes next.** That's the part to keep humble about.

---

## TL;DR

| Dimension | Status |
|---|---|
| **Temporal freshness** | 6–60 months stale; pair with quarterly calls before acting |
| **Geographic balance** | JP+TW deep, Korea/China/EU shallow, US moderate — see `03_READING_LIST_GAPS.md` |
| **Source bias** | Marketing-grade, not auditor-grade, on strategic claims |
| **Extraction quality** | `02_KEY_FINANCIALS.md` blanks are pdftotext yield loss, not missing data |
| **Analyst cutoff (me)** | Jan 2026 → I'm ~3 months behind real-world |
| **Thesis status** | Library only. No view, no allocation, no forecast built in |
| **The unknowables** | Geopolitics, S-curve surprises, customer-concentration shocks |

---

*The right frame: treat this collection the way Lasertec treats a reticle — a faithful, carefully inspected image of what was true at tape-out, not a guarantee of what prints on silicon today. The value is high; the shelf life is real; the blind spots are named.*
