---
layout: default
title: Value Chain Map
nav_order: 2
---

# Semiconductor Value Chain Map — SEAJ + TSIA Coverage

*Index of all companies in this folder, organized by where they sit in the chip value chain. Use this as a navigable table of contents — click/search any file name to jump to its report.*

---

## How to read this map

A chip is born from sand and finishes in your phone. Along the way, it passes through roughly these stages, each dominated by a handful of companies — often with **near-monopolies at specific choke points**:

```
Raw materials → Wafers & consumables → Fab equipment (WFE) → EDA + IP →
  Fabless design → Foundry/IDM manufacture → OSAT (test + package) →
    Distribution → End product
```

**Key insight up front:** the Japanese companies in your folder overwhelmingly live in **Materials** and **WFE**; the Taiwanese companies live in **Foundry**, **Fabless**, and **OSAT**. This division is not accidental — it is the outcome of 40 years of industrial policy, and together Japan + Taiwan effectively *are* the semiconductor supply chain.

---

## Layer 0 — Raw materials & consumables

Inputs consumed by fabs every shift.

| Company | HQ | Role | File |
|---|---|---|---|
| **Shin-Etsu Chemical** | JP | Silicon wafers (global #1, ~30% share) + photoresist | `Annual-Report-2025 SHINETSU.pdf` |
| **JSR** | JP | KrF/ArF/EUV photoresist (top-3 globally) | `JSR_annual report_2024_2025_e_all.pdf` |
| **Ajinomoto Fine-Techno** | JP | **ABF substrate film** — de facto monopoly for FC-BGA package dielectric; every Intel/AMD/NVIDIA CPU/GPU substrate uses it | `AJINOMOTO FINE INC ABF-presentation.pdf` |
| **Senju Metal Industry** | JP | Solder paste, preform, bonding materials for packaging | `SENJU 2025_soldering_materials_catalogue.pdf`, `bonding material performance SENJU chart01.png` |
| **Lintec** | JP | Back-grinding / dicing tapes — consumable used on every wafer | `Integrated_Report_2025_all LINTEC.pdf` |
| **UACJ** | JP | Aluminum (used in interposers, heat spreaders, can bodies) | `00 UACJ integrated report 2025.pdf` |
| **Leatec Fine Ceramics** | TW | Ceramic components for semi equipment (chucks, heaters) | `LEATEC FINE CERAMICS 2024Annual Report.pdf` |

---

## Layer 1 — Wafer Fab Equipment (WFE)

Tools that turn a blank wafer into a finished die. Sub-categorized by process step so you can see how each company fits.

### 1a. Lithography (pattern-printing)

| Company | HQ | Role | File |
|---|---|---|---|
| **Nikon** | JP | ArFi steppers; lost EUV race to ASML | `26third_all_e NIKON 3Q 2025 Result.pdf` |
| **Canon** | JP | ArFi + nano-imprint lithography (NIL) — long-shot alternative to EUV | `phase7-e CANON presentation JAN 2026.pdf`, `conf2025e CANON fy2025 result.pdf`, `Canon-Broadcast-CINEMA-Lens-Lineup.pdf` |
| **NuFlare Technology** | JP | E-beam **mask writers** for EUV masks (near-monopoly with IMS/Zeiss) | `img_business01 NUFLARE japan.png` |
| **Elionix** | JP | E-beam lithography for R&D / niche production | `ELIONIX JAPAN ELS-BODEN litography img6310549954213*.png` |

> **Gap:** ASML — the single most important WFE company globally (EUV monopoly) — is missing. Flagged in reading list.

### 1b. Mask inspection, metrology, process control

The "eyes" of the fab. Near-monopolies at the bleeding edge.

| Company | HQ | Role | File |
|---|---|---|---|
| **Lasertec** | JP | **EUV mask blank & actinic pattern inspection — 100% monopoly**. Every EUV mask in the world is inspected by a Lasertec tool | `Integrated report LASERTEC 2025.pdf` |
| **KLA** | US | Process control leader: wafer inspection, overlay, CD metrology — ~50% share | `KLAC 2025 Annual Report (bookmarked).pdf` |
| **Hitachi High-Tech** | JP | CD-SEM (critical dimension SEM) — near-monopoly in in-line CD metrology, plus etch + analytical | `naka_e HITACHI HIGH-TECH future.pdf`, `profile-en-pdf HITACH HIGH-TECH.pdf`, `csm_24.04_woven_9c6c4311dd HORIBA corporation.webp` |
| **JEOL** | JP | E-beam (TEM/SEM) + mass spec + NMR | `integrated_report_2025_a3_en JEOL.pdf` |
| **Shimadzu** | JP | Analytical — mass spec, chromatography, surface analysis | `shimadzu_integrated_report_2025 SHIMADZU.pdf` |
| **Horiba** | JP | Gas / flow / particle measurement, spectroscopy | *(photo file)* |
| **Zeiss** | DE | Optics for EUV; 3D metrology (ATOS/ARAMIS/TRITOP/ScanBox) | `20250826_zeiss_aramis_brochure_digital_en.pdf`, `2025_ScanBox_BR_Digital_EN.pdf`, `241210_zeiss_tritop_brochure_en.pdf`, `zeiss_atos_5_brochure_en.pdf` |
| **Accretech / Tokyo Seimitsu** | JP | Probers, dicers, metrology | `IntegratedReport2025_E ACCRETECH 2025.pdf` |

### 1c. Deposition (CVD, ALD, PVD, epi)

Building up the thin films that become transistors and interconnect.

| Company | HQ | Role | File |
|---|---|---|---|
| **Applied Materials** | US | Largest WFE company globally; broadest portfolio (PVD, CVD, epi, CMP, implant) | `2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf`, `APPLIED_MATERIALS_JP_03162026_zgC1WO.png` |
| **Lam Research** | US | #1 in etch + #1 in plasma ALD/CVD | `LAM+RESEARCH+CORP_BOOKMARKS_2025_V1 annual report 2025.pdf` |
| **ASM International** | NL | **ALD leader** (Atomic Layer Deposition) — critical for sub-7nm gate stacks, GAAFET | `asm-2025-annual-report.pdf`, `annual-report-2024-asm-final.pdf` |
| **ULVAC** | JP | PVD (sputtering), vacuum technology, evaporators | `ULVAC_CorporateProfile_en_2025.pdf` |
| **Kokusai Electric** | JP | Batch (vertical furnace) thermal processing & ALD | `CorporateProfile2025_en KOKUSAI ELECTRIC 2025.pdf` |
| **Shibaura Mechatronics** | JP | Wafer processing, PVD, dicing | `00 SHIBUARA integrated report 2025.pdf`, `2024 Shinagawa Update_20240530.pdf` |

> **Gap:** Tokyo Electron (TEL) — the #3 WFE company globally and dominant in coat/develop + etch — is missing. Flagged.

### 1d. Etch

See Lam Research (above) and Applied Materials. TEL missing.

### 1e. CMP (chemical-mechanical planarization)

| Company | HQ | Role | File |
|---|---|---|---|
| **Applied Materials** | US | Share leader in CMP | *(above)* |
| **Ebara Corporation** | JP | CMP (Mirra competitor) + **dry vacuum pumps** (#1 share in semi vacuum) | `INT25_all_EN_1 EBARA corporation 2024.pdf` |

### 1f. Wet / cleans / track

| Company | HQ | Role | File |
|---|---|---|---|
| **SCREEN Holdings** | JP | Single-wafer cleaners (#1 share) + coater/developer | `SPE_GeneralCatalog_Digital_251209 Screen japan.pdf` |

### 1g. Vacuum, gas delivery, components

The "plumbing" of every fab tool. Specialty Japanese makers dominate.

| Company | HQ | Role | File |
|---|---|---|---|
| **Ebara** | JP | Dry vacuum pumps (above) | |
| **ULVAC** | JP | Vacuum systems, pumps | *(above)* |
| **CKD** | JP | Pneumatics, gas valves, integrated gas systems | `CKD ckdreport2025en_all_web.pdf` |
| **AI Mechatec** | JP | Vacuum / bonding equipment (optical bonding, laminator) | `AI_MECHATEC_JP_*.jpg` (15 files) |
| **HTC Japan / HTC Vacuum** | JP | Vacuum valves, components | `HTC vacuum en-company-profile.pdf`, `htcvacuum-valves 2021 product guide.pdf` |
| **Ayumi Industries** | JP | Vacuum components | `AYUMI_JP_vacuum_*.jpg` |
| **Meiritz Seiki** | JP | Precision components | `MEIRITZ_JP_03182026_5bLz3l.jpg` |
| **Rikken Keiki** | JP | **Gas detection** — critical for fab safety (HF, SiH4, etc.) | `Integrated_report_2025_A4_eng RIKKEN KEIKI 2025.pdf`, `Financial_Results_Briefing_Materials_for_the_Fiscal_Year_Ended_March_2025 RIKKEN KEIKI.pdf` |
| **SINFONIA Technology** | JP | Vibration control, clean material handling | `EN_about-fig-11_2025 SINFONIA.jpg`, `about-fig-1 SINFONIA japan company.png` |
| **Organo** | JP | Ultrapure water systems for fabs | `ORGANO Financial-Results-for-First-Half-of-Fiscal-Year-Ending-March-31-2026.pdf` |
| **Adatech (Asahi Diamond? — verify)** | JP | Water / wastewater management | `ADATECH water industry 2026 Screenshot*.png` |
| **Marumae** | JP | Custom-machined parts (Al, quartz, SiC) for semi equipment | `MARUMAE_annual_report_2025en.pdf` |
| **Panasonic Industry** | JP | Components, capacitors, industrial devices | `PANASONIC INDUSTRY ir-pre2024_pid_e.pdf` |
| **Misumi Group** | JP | Components e-commerce / MRO for factories | `MISUMI_Integrated_Report_2025_English_all_ver.2.pdf` |

### 1h. Probing / dicing / grinding / bonding (backend prep)

Bridge between frontend and OSAT.

| Company | HQ | Role | File |
|---|---|---|---|
| **Disco** | JP | #1 in wafer dicing & grinding — near-monopoly | `dar2020 DISCO ANNUAL report 2020.pdf` |
| **Accretech** | JP | Probers + dicing + metrology | *(above)* |
| **Micronics Japan** | JP | **Probe cards** (especially advanced/HBM/vertical) | `LINEUP2026 MICRONICS JAPAN.pdf` |
| **Favite** | TW | Probe card / probe pin supplier | `FAVITE annual report 2024 113年報_英文版上傳.pdf` |
| **S-Takaya** | JP | Burn-in test boards, test sockets | `sty_pamphlet_en S-TAKAYA corporation japan 2021.pdf` |
| **Interaction** | JP | Back-end equipment, bonders | `INTERACTION_JP_Medium-Term-Business-Plan（2024-2028）.pdf` |

### 1i. Test equipment (ATE)

| Company | HQ | Role | File |
|---|---|---|---|
| **Advantest** | JP | **HBM memory test monopoly**; SoC ATE — ~55% share globally | `E_all_IAR2025 ADVANTEST annual report 2025.pdf` |
| **Teradyne** | US | SoC ATE (iPhone/AMD/NVIDIA); industrial robotics (UR + MiR) | `ALL_Analyst_Day_2025_IR_SITE_NEW TERADYNE investor day Mar 2025.pdf`, `Teradyne_EC Q4'25 Slides Feb2026.pdf` |

### 1j. Factory automation / AMHS

| Company | HQ | Role | File |
|---|---|---|---|
| **Daifuku** | JP | **AMHS monopoly** — overhead hoist transport (OHT) for fabs, global leader | `DAIFUKU_FY2025Q4e_presentation.pdf` |
| **Seino Holdings** | JP | Logistics (third-party, not semi-specific but supports fab supply) | `2024annual report SEINO.pdf` |

### 1k. Lithography niches / specialty

| Company | HQ | Role | File |
|---|---|---|---|
| **CSUN Manufacturing** | TW | Solar + semi production equipment (drying, cleaning, thermal) | `CSUN annual report 2024*.pdf` |
| **Creating Nanotech** | TW | Nano-imprint / patterning equipment | `CREATING NANOTECH 2025CNT_pdfc_*.pdf` |
| **Gallant Precision Machining (GPM)** | TW | LCD + semi equipment | `GALLANT annual report 2024*.pdf` |
| **Ardentec** | TW | Test services (testing house) | `ARDENTECH annual report 2024 年報ESG.pdf` |
| **Manz** | DE/TW | **TGV (through-glass via)** + IC substrate solutions — glass interposer play | `MANZ 2025_0923_TGV-solutions_DataSheet.pdf`, `MANZ 2025_EN_IC_substrate_flyer_1027.pdf`, `Manz_brochure_Contract-Manufacturing_EN-4.pdf` |
| **ITW / Lumex** | US | Tape & reel, packaging consumables | `Flyer-20221128-ITW-Lumex-EN-No-W_SD.pdf` |

---

## Layer 2 — EDA & Silicon IP

| Company | HQ | Role | File |
|---|---|---|---|
| **Cadence Design Systems** | US | EDA (#2) + chiplet-based Physical AI platform | `CADENCEchiplets-based-physical-ai-platform.jpg` |
| **ARM** | UK | CPU IP (Cortex-R/M/A) — ubiquitous | `ARM_Cortex-R52_datasheet.pdf` |
| **eMemory** | TW | **NVM IP** (OTP, MTP, anti-fuse) — embedded in almost every foundry PDK | `eMemory annual report 2024 0250521170001.pdf` |
| **M31 Technology** | TW | Foundation IP (I/O, PLL, interface IP) | `M31 annual report 2024 113M31股東會年報ENG-1.pdf` |
| **AP Memory (AP Memory Tech)** | TW | Specialty DRAM IP (PSRAM, low-power memory) | `AP MEMORY annual report 2024年度年報英文版.pdf` |

> **Gap:** Synopsys (EDA #1), Siemens EDA, RISC-V International, Imagination — all flagged.

---

## Layer 3 — Fabless design

### Taiwan fabless (the TSIA core)

| Company | HQ | Role | File |
|---|---|---|---|
| **MediaTek** | TW | SoC (mobile, Chromebook, smart TV, WiFi, auto) — #2 global SoC | `MEDIATEK 2024-English-Annual-Report.pdf` |
| **Realtek** | TW | PC/NB connectivity (audio codec, WiFi, LAN) | `2024_Annual_Report_REALTEK.pdf` |
| **Phison Electronics** | TW | NAND flash controllers — #1 or #2 globally | `Phison_Electronic_Corporation_2024_Annual_Report.pdf` |
| **Himax Technologies** | TW | Display drivers (TDDI), WLO, automotive LCD | `Himax_2024_Annual_Report.pdf` |
| **Megawin Technology** | TW | 8-bit MCUs, touch controllers | `2026H1_Megawin_Brochure(EN)_v1.0.pdf`, `MEGAWIN taiwan annual report 2024 chinese 113.pdf` |
| **Richwave Technology** | TW | RF ICs (WiFi FEM, PA/LNA) | `RICHWAVE annual report 2024*.pdf` |
| **Weltrend Semiconductor** | TW | USB-PD controllers, HID, monitor SoC | `Weltrend 2024 Sustainability Report.pdf` |
| **Alcor Micro** | TW | Card reader, USB/Thunderbolt hubs | `ALCOR fabless 2024_AnnualReport_EN.pdf`, `2024_AnnualReport_EN.pdf` |
| **EGIS Technology** | TW | Fingerprint sensors (Android) | `EGIS annual report 2024 神盾113年報-EN-上傳版-1.pdf` |
| **Grace Haozan** | TW | Fabless (mixed signal / LED) | `GRACE HAOZAN products list*.png` |
| **MIC (Microelectronics)** | TW | Design services / IP | `MIC taiwan annual report 2024 2505091655322f091.pdf` |

### Memory (IDM) — standalone layer between fabless & foundry

| Company | HQ | Role | File |
|---|---|---|---|
| **Nanya Technology** | TW | DRAM (DDR3/DDR4, niche LPDDR4) | `2025 Nanya Tech Product Brochure_V4.pdf` |
| **Winbond** | TW | Specialty memory — SpiFlash, SpiNAND, LPDDR niche | `4Q25-investor-conference_EN_Final Windbond 2025.pdf`, `2024 WIN Annual Report.pdf` |
| **Episil Technologies** | TW | Specialty IDM (power discrete, 150mm) | `EPISIL_News_20240701 annual report 2024.pdf` |

> **Gap:** Samsung (memory + foundry), SK Hynix (HBM king), Micron, Kioxia (NAND), YMTC — the entire memory giants are missing. Flagged as **priority 1** in reading list.

### Power / analog / sensors

| Company | HQ | Role | File |
|---|---|---|---|
| **Fuji Electric** | JP | IGBT, SiC power modules | `FUJI_ELECTRIC_ar2025_02_02_e.pdf`, `FUJI_ELECTRIC_ar2025_02_04_e.pdf` |
| **AMS OSRAM** | AT/DE | Optical sensors (PPG/SpO2, LiDAR emitters) | `AMS OSRAM sensor biomonitoring SFH 7072_EN.pdf` |

---

## Layer 4 — Foundry / IDM manufacture

| Company | HQ | Role | File |
|---|---|---|---|
| **TSMC** | TW | #1 foundry globally (~60% share); leading edge (N2, N3, CoWoS) | `2024 Annual Report-E TSMC.pdf`, `2024 Annual Report.pdf` |
| **UMC** | TW | #2 TW foundry; mature nodes (28nm, 22nm) | `2024AR_ENG_all UMC United Microelectronics Corporation Annual report 2024.pdf` |
| **VIS / Vanguard** | TW | 8" specialty foundry; JV with NXP in Singapore; ~30% owned by TSMC | `20250506232053383995188_en VIS annual report 2025.pdf`, `Screenshot 2026-03-09 123342 vis annual report 2001.png`, `vis company 030926`, `Screenshot 2026-03-09 120332.png` |
| **PSMC / Powerchip** | TW | Memory + logic foundry; JV with Tata (India fab) | `PSMC Annual_Reports_2024_EN.pdf` |
| **WIN Semiconductors** | TW | **GaAs compound-semi foundry** (#1 globally, RF PA) | `2024 WIN Annual Report.pdf` |
| **Global Foundries** | US | Specialty foundry (RF, auto, FD-SOI) | `GLOBAL FOUNDRIES-At-A-Glance-Feb2026.pdf` |

### Photomask (foundry's upstream supplier)

| Company | HQ | Role | File |
|---|---|---|---|
| **Taiwan Mask Corp (TMC)** | TW | Photomask manufacturer for TW foundries | `光罩113年年報-(英文定稿)_114.08.15_916123 taiwan mask company annual report 2024.pdf`, `taiwan mask corp annual report 2024 030926` |

---

## Layer 5 — OSAT / Advanced Packaging

(Expanded in detail in `01_DEEP_DIVE_ADVANCED_PACKAGING.md`.)

| Company | HQ | Role | File |
|---|---|---|---|
| **ASE Technology Holding** | TW | **#1 OSAT globally** — assembly + test + SiP + fan-out | `20250603150724453273521_en ASE holdings annual report 2024.pdf` |
| **ChipMOS Technologies** | TW | Memory/display-driver packaging + test | `CHIPMOS taiwan annual report 2024 en_ir_year_1820663809.pdf` |
| **KYEC (King Yuan Electronics)** | TW | **Test-only** specialist — MediaTek/Qualcomm/NVIDIA test | `KYEC(2449)_4Q25 Investor update_English.pdf` |
| **Sigurd Microelectronics** | TW | OSAT — test + assembly | `SIGURD annual report 2024 113q4_copy.pdf` |
| **Orient Semiconductor (OSE)** | TW | OSAT — assembly + test | `議事手冊114年(all)(EN)上傳檔 Orient Semiconductor 2024 ANNUAL REPORT.pdf` |
| **Spirox** | TW | Test handling & probe cards distribution | `SPIROX annual report 2024 113年度年報(英文).pdf` |
| **ZDT (Zhen Ding Technology)** | TW | PCBs + IC substrate + FPC | `ZDTCO annual report 2024annualreport_en_revised.pdf` |

### Advanced packaging input suppliers (cross-reference with Layer 0)

- **Ajinomoto** (ABF film — monopoly)
- **Manz** (TGV, glass interposer)
- **Senju Metal** (solder bumping)
- **Lintec** (dicing tape)
- **UACJ** (aluminum heat spreaders)

---

## Layer 6 — Distribution & trading houses

| Company | HQ | Role | File |
|---|---|---|---|
| **WPG Holdings** | TW | **#1 Asian semi distributor** (MediaTek, NXP, Qualcomm) | `2024_WPG_annual_report_E.pdf`, `2024_WPG_annual_report_E (1).pdf` |
| **Topco Global** | TW | TW distributor (electronics, semi) | `TOPCO GLOBAL annual 2024 ANNUAL-113ENG.pdf` |
| **Nagase & Co.** | JP | Chemical/specialty trading (photoresists, packaging materials) | `nagase2025_IR_Full NAGASE integrated report 2025.pdf` |
| **Daitron** | JP | Equipment + component distribution | `DAITRON_E_2025Q4_FR.pdf` |
| **Marketech International** | TW | Materials + sub-systems distribution | `MARKETECH annual report 2024*.pdf` |
| **Medipal Holdings** | JP | Pharma distribution (tangential — ESG / logistics template) | `00 MEDIPAL integrated report 2025.pdf` |
| **ITOCHU** | JP | General trading house with semi-materials exposure | `ITOCHU_ar2025E.pdf` |
| **HCL Technologies** | IN | IT services (chip design services, ERP for fabs) | `HCL_TECH_Annual-Report-2024-25.pdf` |

---

## Layer 7 — Research institutes, industry bodies, policy

| Entity | HQ | Role | File |
|---|---|---|---|
| **ITRI** | TW | Taiwan's national semi R&D institute — spawned TSMC, UMC, VIS | `2024_Annual Report ITRI taiwan.pdf`, `2024_Annual Report.pdf` |
| **ISTI / III** | TW | Industrial strategy / IT research | `About_ISTI.pdf` |
| **JEITA** | JP | Electronics industry association — monthly export/production stats | `JEITA export report 2026.pdf` |
| **DBJ (Development Bank of Japan)** | JP | State-backed financing (e.g., Rapidus investment) | `DBJIntegratedReport2025.pdf` |
| **SANKI** | JP | Industrial facility engineering (fab cleanrooms / HVAC) | `index_report2023_01 SANKI 2023.pdf`, `SG022_2026.pdf` (likely SAI Global / SGS 2025) |
| **SGS** | CH | Testing/certification (semi reliability labs) | `SGS 2025 Integrated Report EN.pdf` |
| **SNK (Saint Kobe — verify)** | JP | *Unclear from filename — needs inspection* | `ysuT SNK integrated report 2025.pdf` |

---

## Layer 8 — Architecture / standards / trend data

Not companies, but essential context:

| Topic | Role | File |
|---|---|---|
| **CXL (Compute Express Link)** | Coherent interconnect standard — enabling memory pooling / expansion for AI servers | `CXL-Specification_rev4p0_ver1p0_2026February26_clean_evalcopy_v2.pdf`, `CXL_4.0-Webinar_December-2025_FINAL.pdf`, `CXL_Q2-2025-Webinar_FINAL.pdf` |
| **HBM + GPU + AI trends** | Memory-for-accelerators trend data | `HBM_GPU_AI_Trends_2026.pdf` |
| **Fan-out panel roadmap** | Advanced packaging format roadmap | `fan-out-panel-roadmap 2019.jpg` |
| **Probe card market** | Market snapshot | `PROBE CARD 2021 Screenshot 2026-03-13 134947.png` |
| **AI market size** | Precedence Research 2024–2034 forecast | `artificial-intelligence-market-size PRECEDENCE research 2024to2034.webp` |
| **Vacuum tree (shinkunoki)** | JP industrial map of vacuum ecosystem | `JMA_tree_of_vacuum_img_eng_shinkunoki.png`, `JMA_tree_of_vacuum_img_shinkunoki.png` |
| **Intel Core Ultra Series 3** | End-product reference | `Intel Core Ultra Series 3 Processors - Product Brief v1.pdf` |

---

## Layer 9 — Tangential / non-semi (for reference)

Included in your folder but outside semi:

| File | Notes |
|---|---|
| `FUBON FINANCIAL annual report 2024 20250516180322-4.pdf` | TW financial holding — unrelated unless tracking TW capital markets |
| `Canon-Broadcast-CINEMA-Lens-Lineup.pdf` | Canon imaging — optics heritage feeds litho expertise, but product unrelated |
| `Los Angeles County Completion Certificate - June 2, 2026 Statewide Direct Primary Election.pdf` | **Personal document — probably misfiled** |
| `AS_162388_TG_689277_KA_US_2105_1.pdf` | Unclear — needs inspection |
| `HY_Report_2025.pdf` | Unclear — needs inspection |
| `2025120101-7640.pdf`, `2026010105-7725.pdf`, `2026010106-7715.pdf`, `p_DPS-i11KU-05.jpg` | Unclear IDs / product datasheets |
| `Flyer_OMNIA_GC_220-180_A4_EN.pdf.pdf` | Product flyer (likely Zeiss or measurement tool) |
| `2025Q3-Balance-Sheet.pdf` | Unclear company attribution |
| `CADDI_SAMPLE_2026_03162026_xSqDNf.png` | Caddi (JP — procurement platform) sample |
| `RAYDENT_03222026_35Pu4V.gif` | Raydent (JP — plating chemicals?) |

---

## What this map tells you about the industry

1. **Every process step has 1–3 real players.** Lasertec owns EUV mask inspection. Ajinomoto owns ABF. Daifuku owns AMHS. Disco owns dicing. These are not commodity businesses — they are process-integrated monopolies cultivated over decades.

2. **Japan's specialty:** materials + tools with high process integration, high switching cost, slow share shift. These companies rarely lose share; they lose *cycles*. If you want to study "compounding through industrial patience," Japan WFE is the textbook.

3. **Taiwan's specialty:** manufacturing scale + ecosystem density. TSMC didn't win alone — it won alongside ASE (OSAT), ChipMOS (memory test), WPG (distribution), MediaTek (biggest customer), Ajinomoto (substrate), Shin-Etsu (wafer). The cluster *is* the moat.

4. **What's coming:** the center of gravity is shifting from lithography (frontend) to **packaging** (backend). 2.5D/3D (CoWoS, FOPLP, HBM stacking) is where the next decade's S-curve sits. Your OSAT coverage is correctly positioned for this.

5. **What's hidden:** the most important company in the entire value chain (ASML) isn't here. Neither is the most important memory company (SK Hynix for HBM) or the most important compute customer (NVIDIA). See `03_READING_LIST_GAPS.md`.
