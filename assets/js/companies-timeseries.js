/* =====================================================================
   Multi-year time-series financial data extracted from the annual /
   integrated reports in this folder. Each entry is a company with an
   array of per-fiscal-year objects.

   All absolute amounts are in MILLIONS of native currency.
   Margins are percentages. "fy" is the fiscal year label the company
   itself uses (Japan = "FY ends Mar 31 of next calendar year" → label
   is the Apr-start year). "endDate" is the actual fiscal-year end.

   Coverage depth reflects how deep the company's own integrated report
   goes — Advantest shows 11 years, Ebara and Shin-Etsu 10, CKD 12,
   Taiwan issuers typically only 2 in their 2024 annual report.
   ===================================================================== */

window.TIMESERIES = {

  // ============= ADVANTEST — 11 years (FY ends Mar) =============
  'Advantest': {
    name: 'Advantest', ticker: '6857.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'E_all_IAR2025 ADVANTEST annual report 2025.pdf — 11 Year Financial Highlights',
    fiscal: [
      { fy: 2014, endDate: '2015-03-31', revenue: 163803, opIncome:  16858, netIncome:  16753, totalAssets: 233237, totalEquity: 101810, grossMargin: 56.0, opMargin: 10.3, netMargin: 10.2, rd: 29507 },
      { fy: 2015, endDate: '2016-03-31', revenue: 162111, opIncome:  12597, netIncome:   6694, totalAssets: 210451, totalEquity:  93619, grossMargin: 56.4, opMargin:  7.8, netMargin:  4.1, rd: 31298 },
      { fy: 2016, endDate: '2017-03-31', revenue: 155916, opIncome:  13905, netIncome:  14201, totalAssets: 231603, totalEquity: 109517, grossMargin: 57.6, opMargin:  8.9, netMargin:  9.1, rd: 31170 },
      { fy: 2017, endDate: '2018-03-31', revenue: 207223, opIncome:  24487, netIncome:  18103, totalAssets: 254559, totalEquity: 124610, grossMargin: 51.4, opMargin: 11.8, netMargin:  8.7, rd: 33540 },
      { fy: 2018, endDate: '2019-03-31', revenue: 282456, opIncome:  64662, netIncome:  56993, totalAssets: 304580, totalEquity: 198731, grossMargin: 54.5, opMargin: 22.9, netMargin: 20.2, rd: 37852 },
      { fy: 2019, endDate: '2020-03-31', revenue: 275894, opIncome:  58708, netIncome:  53532, totalAssets: 355777, totalEquity: 231452, grossMargin: 56.7, opMargin: 21.3, netMargin: 19.4, rd: 40070 },
      { fy: 2020, endDate: '2021-03-31', revenue: 312789, opIncome:  70726, netIncome:  69787, totalAssets: 422641, totalEquity: 280369, grossMargin: 53.8, opMargin: 22.6, netMargin: 22.3, rd: 42678 },
      { fy: 2021, endDate: '2022-03-31', revenue: 416901, opIncome: 114734, netIncome:  87301, totalAssets: 494696, totalEquity: 294621, grossMargin: 56.6, opMargin: 27.5, netMargin: 20.9, rd: 48367 },
      { fy: 2022, endDate: '2023-03-31', revenue: 560191, opIncome: 167687, netIncome: 130400, totalAssets: 600224, totalEquity: 368694, grossMargin: 57.0, opMargin: 29.9, netMargin: 23.3, rd: 60094 },
      { fy: 2023, endDate: '2024-03-31', revenue: 486507, opIncome:  81628, netIncome:  62290, totalAssets: 671229, totalEquity: 431178, grossMargin: 50.6, opMargin: 16.8, netMargin: 12.8, rd: 65492 },
      { fy: 2024, endDate: '2025-03-31', revenue: 779707, opIncome: 228161, netIncome: 161177, totalAssets: 854210, totalEquity: 506539, grossMargin: 57.1, opMargin: 29.3, netMargin: 20.7, rd: 71399 }
    ]
  },

  // ============= EBARA — 10 years (FY ends Dec since 2018) =============
  'Ebara': {
    name: 'Ebara', ticker: '6361.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'INT25_all_EN_1 EBARA corporation 2024.pdf — 10-Year Financial Summary (pg 113)',
    fiscal: [
      { fy: 2015, endDate: '2016-03-31', revenue: 486235, opIncome: 38011, netIncome: 17254, totalAssets: 579860, totalEquity: 250444, opMargin: 7.8 },
      { fy: 2016, endDate: '2017-03-31', revenue: 476104, opIncome: 29995, netIncome: 20587, totalAssets: 588457, totalEquity: 277509, opMargin: 6.3 },
      { fy: 2017, endDate: '2017-12-31', revenue: 381993, opIncome: 18115, netIncome:  9531, totalAssets: 612919, totalEquity: 284788, opMargin: 4.7, note: '9-month transition year' },
      { fy: 2018, endDate: '2018-12-31', revenue: 509175, opIncome: 32482, netIncome: 18262, totalAssets: 591592, totalEquity: 286778, opMargin: 6.4 },
      { fy: 2019, endDate: '2019-12-31', revenue: 522424, opIncome: 35298, netIncome: 23349, totalAssets: 595239, totalEquity: 291827, opMargin: 6.8 },
      { fy: 2020, endDate: '2020-12-31', revenue: 522478, opIncome: 37566, netIncome: 24236, totalAssets: 644711, totalEquity: 296877, opMargin: 7.2 },
      { fy: 2021, endDate: '2021-12-31', revenue: 603213, opIncome: 61372, netIncome: 43616, totalAssets: 719736, totalEquity: 321655, opMargin: 10.2 },
      { fy: 2022, endDate: '2022-12-31', revenue: 680870, opIncome: 70572, netIncome: 50488, totalAssets: 828049, totalEquity: 369725, opMargin: 10.4 },
      { fy: 2023, endDate: '2023-12-31', revenue: 759328, opIncome: 86025, netIncome: 60283, totalAssets: 913900, totalEquity: 421572, opMargin: 11.3 },
      { fy: 2024, endDate: '2024-12-31', revenue: 866668, opIncome: 97953, netIncome: 71401, totalAssets: 1005085, totalEquity: 485336, opMargin: 11.3 }
    ]
  },

  // ============= SHIN-ETSU — 10 years (FY ends Mar) =============
  'Shin-Etsu': {
    name: 'Shin-Etsu', ticker: '4063.T', hq: 'JP', layer: 'Materials', cur: 'JPY',
    source: 'Annual-Report-2025 SHINETSU.pdf — Ten-Year Summary (pg 69)',
    fiscal: [
      { fy: 2015, endDate: '2016-03-31', revenue: 1279807, opIncome: 208525, netIncome: 148840, totalAssets: 2510085, totalEquity: 2080465, opMargin: 16.3, netMargin: 11.6, rd: 53165 },
      { fy: 2016, endDate: '2017-03-31', revenue: 1237405, opIncome: 238617, netIncome: 175912, totalAssets: 2655636, totalEquity: 2190082, opMargin: 19.3, netMargin: 14.2, rd: 49020 },
      { fy: 2017, endDate: '2018-03-31', revenue: 1441432, opIncome: 336822, netIncome: 266235, totalAssets: 2903137, totalEquity: 2413025, opMargin: 23.4, netMargin: 18.5, rd: 51768 },
      { fy: 2018, endDate: '2019-03-31', revenue: 1594036, opIncome: 403705, netIncome: 309125, totalAssets: 3038717, totalEquity: 2532556, opMargin: 25.3, netMargin: 19.4, rd: 56436 },
      { fy: 2019, endDate: '2020-03-31', revenue: 1543525, opIncome: 406041, netIncome: 314027, totalAssets: 3230485, totalEquity: 2723141, opMargin: 26.3, netMargin: 20.3, rd: 48536 },
      { fy: 2020, endDate: '2021-03-31', revenue: 1496906, opIncome: 392213, netIncome: 293732, totalAssets: 3380615, totalEquity: 2886625, opMargin: 26.2, netMargin: 19.6, rd: 51264 },
      { fy: 2021, endDate: '2022-03-31', revenue: 2074428, opIncome: 676322, netIncome: 500117, totalAssets: 4053412, totalEquity: 3429208, opMargin: 32.6, netMargin: 24.1, rd: 62455 },
      { fy: 2022, endDate: '2023-03-31', revenue: 2808824, opIncome: 998202, netIncome: 708238, totalAssets: 4730394, totalEquity: 4026209, opMargin: 35.5, netMargin: 25.2, rd: 67201 },
      { fy: 2023, endDate: '2024-03-31', revenue: 2414937, opIncome: 701038, netIncome: 520140, totalAssets: 5147974, totalEquity: 4424073, opMargin: 29.0, netMargin: 21.5, rd: 65785 },
      { fy: 2024, endDate: '2025-03-31', revenue: 2561249, opIncome: 742105, netIncome: 534021, totalAssets: 5636601, totalEquity: 4837585, opMargin: 29.0, netMargin: 20.9, rd: 73129 }
    ]
  },

  // ============= CKD — 12 years (FY ends Mar) =============
  'CKD': {
    name: 'CKD', ticker: '6407.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'CKD ckdreport2025en_all_web.pdf — 11-Year Summary',
    fiscal: [
      { fy: 2013, endDate: '2014-03-31', revenue:  75491, opIncome:  7883, opMargin: 10.4, roe: 10.1 },
      { fy: 2014, endDate: '2015-03-31', revenue:  83379, opIncome:  8363, opMargin: 10.0, roe:  9.8 },
      { fy: 2015, endDate: '2016-03-31', revenue:  88117, opIncome:  8107, opMargin:  9.2, roe:  8.3 },
      { fy: 2016, endDate: '2017-03-31', revenue:  94012, opIncome:  9580, opMargin: 10.2, roe: 10.1 },
      { fy: 2017, endDate: '2018-03-31', revenue: 115700, opIncome: 12472, opMargin: 10.8, roe: 12.1 },
      { fy: 2018, endDate: '2019-03-31', revenue: 115665, opIncome:  5429, opMargin:  4.7, roe:  6.0 },
      { fy: 2019, endDate: '2020-03-31', revenue: 100717, opIncome:  5230, opMargin:  5.2, roe:  4.5 },
      { fy: 2020, endDate: '2021-03-31', revenue: 106723, opIncome:  7698, opMargin:  7.2, roe:  5.9 },
      { fy: 2021, endDate: '2022-03-31', revenue: 142199, opIncome: 17879, opMargin: 12.6, roe: 12.1 },
      { fy: 2022, endDate: '2023-03-31', revenue: 159457, opIncome: 21170, opMargin: 13.3, roe: 12.9 },
      { fy: 2023, endDate: '2024-03-31', revenue: 134425, opIncome: 13113, opMargin:  9.8, roe:  6.7 },
      { fy: 2024, endDate: '2025-03-31', revenue: 155634, opIncome: 19018, opMargin: 12.2, roe: 10.2 }
    ]
  },

  // ============= KOKUSAI ELECTRIC — 5 years (FY ends Mar) =============
  'Kokusai Electric': {
    name: 'Kokusai Electric', ticker: '6525.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'CorporateProfile2025_en KOKUSAI ELECTRIC 2025.pdf — Key Items (pg 58)',
    fiscal: [
      { fy: 2020, endDate: '2021-03-31', revenue: 178023, opIncome: 60037, netIncome: 33043, totalAssets: 273769, totalEquity:  64943, grossMargin: 42.7, opMargin: 33.7, netMargin: 18.6 },
      { fy: 2021, endDate: '2022-03-31', revenue: 245425, opIncome: 70652, netIncome: 51339, totalAssets: 356532, totalEquity: 119519, grossMargin: 43.6, opMargin: 28.8, netMargin: 20.9 },
      { fy: 2022, endDate: '2023-03-31', revenue: 245721, opIncome: 56064, netIncome: 40305, totalAssets: 373539, totalEquity: 160881, grossMargin: 41.0, opMargin: 22.8, netMargin: 16.4 },
      { fy: 2023, endDate: '2024-03-31', revenue: 180838, opIncome: 30745, netIncome: 22374, totalAssets: 375433, totalEquity: 187388, grossMargin: 41.5, opMargin: 17.0, netMargin: 12.4 },
      { fy: 2024, endDate: '2025-03-31', revenue: 238933, opIncome: 51320, netIncome: 36004, totalAssets: 341512, totalEquity: 196168, grossMargin: 42.6, opMargin: 21.5, netMargin: 15.1 }
    ]
  },

  // ============= ASE HOLDINGS — 5 years (FY ends Dec) =============
  'ASE Holdings': {
    name: 'ASE Holdings', ticker: '3711.TW', hq: 'TW', layer: 'OSAT', cur: 'TWD',
    source: '20250603...ASE holdings annual report 2024.pdf — Executive Summary (pg 3)',
    fiscal: [
      { fy: 2020, endDate: '2020-12-31', revenue: 476979, opIncome:  34876, netIncome: 29277, totalAssets: 583667, totalEquity: 234263, grossMargin: 16.3, opMargin:  7.3, netMargin:  6.1 },
      { fy: 2021, endDate: '2021-12-31', revenue: 569997, opIncome:  62124, netIncome: 66014, totalAssets: 672934, totalEquity: 274633, grossMargin: 19.4, opMargin: 10.9, netMargin: 11.6 },
      { fy: 2022, endDate: '2022-12-31', revenue: 670873, opIncome:  80176, netIncome: 65227, totalAssets: 707068, totalEquity: 319925, grossMargin: 20.1, opMargin: 12.0, netMargin:  9.7 },
      { fy: 2023, endDate: '2023-12-31', revenue: 581915, opIncome:  40328, netIncome: 33557, totalAssets: 667052, totalEquity: 318110, grossMargin: 15.8, opMargin:  6.9, netMargin:  5.8 },
      { fy: 2024, endDate: '2024-12-31', revenue: 595410, opIncome:  39166, netIncome: 33926, totalAssets: 740698, totalEquity: 345787, grossMargin: 16.3, opMargin:  6.6, netMargin:  5.7 }
    ]
  },

  // ============= DISCO — 5 years (FY ends Mar) — NOTE: stale FY2020 report =============
  'Disco': {
    name: 'Disco', ticker: '6146.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'dar2020 DISCO ANNUAL report 2020.pdf — 5-Year Summary (historical, stale)',
    fiscal: [
      { fy: 2015, endDate: '2016-03-31', revenue: 127800, opIncome: 30300, netIncome: 23000, opMargin: 23.7, netMargin: 18.1 },
      { fy: 2016, endDate: '2017-03-31', revenue: 134200, opIncome: 31300, netIncome: 24200, opMargin: 23.4, netMargin: 18.0 },
      { fy: 2017, endDate: '2018-03-31', revenue: 167300, opIncome: 50900, netIncome: 37100, opMargin: 30.5, netMargin: 22.2 },
      { fy: 2018, endDate: '2019-03-31', revenue: 147500, opIncome: 38600, netIncome: 28800, opMargin: 26.2, netMargin: 19.5 },
      { fy: 2019, endDate: '2020-03-31', revenue: 141100, opIncome: 36400, netIncome: 27600, opMargin: 25.8, netMargin: 19.6 }
    ]
  },

  // ============= HIMAX — 3 years (FY ends Dec) =============
  'Himax': {
    name: 'Himax', ticker: 'HIMX', hq: 'TW', layer: 'Fabless', cur: 'USD',
    source: 'Himax_2024_Annual_Report.pdf — Year-to-Year Comparisons (pg 65)',
    fiscal: [
      { fy: 2022, endDate: '2022-12-31', revenue:   1201, opIncome:  258, netIncome:  237, totalAssets: null, opMargin: 21.4, netMargin: 19.7 },
      { fy: 2023, endDate: '2023-12-31', revenue:    945, opIncome:   43, netIncome:   51, totalAssets: 1643, opMargin:  4.6, netMargin:  5.4 },
      { fy: 2024, endDate: '2024-12-31', revenue:    907, opIncome:   68, netIncome:   80, totalAssets: 1640, opMargin:  7.5, netMargin:  8.8 }
    ]
  },

  // ============= APPLIED MATERIALS — 2 years (FY ends late Oct) =============
  'Applied Materials': {
    name: 'Applied Materials', ticker: 'AMAT', hq: 'US', layer: 'Equipment', cur: 'USD',
    source: '2025 Annual Report (Bookmarked) APPLIED MATERIALS.pdf',
    fiscal: [
      { fy: 2024, endDate: '2024-10-27', revenue: 27176, opIncome: 7867, totalAssets: 34409, totalEquity: 19001, grossMargin: 47.5, opMargin: 28.9 },
      { fy: 2025, endDate: '2025-10-26', revenue: 28368, opIncome: 8289, totalAssets: 36299, totalEquity: 20415, grossMargin: 48.7, opMargin: 29.2 }
    ]
  },

  // ============= LAM RESEARCH — 2 years (FY ends late Jun) =============
  'Lam Research': {
    name: 'Lam Research', ticker: 'LRCX', hq: 'US', layer: 'Equipment', cur: 'USD',
    source: 'LAM+RESEARCH+CORP_BOOKMARKS_2025_V1 annual report 2025.pdf',
    fiscal: [
      { fy: 2024, endDate: '2024-06-30', revenue: null,  totalAssets: 18745, totalEquity: null, note: 'Only partial data extracted' },
      { fy: 2025, endDate: '2025-06-29', revenue: 18400, totalAssets: 21345, totalEquity:  9862, note: 'EPS $4.15 record; op cash flow $6.2B' }
    ]
  },

  // ============= ASM INTERNATIONAL — 2 years (FY ends Dec) =============
  'ASM International': {
    name: 'ASM International', ticker: 'ASM.AS', hq: 'EU', layer: 'Equipment', cur: 'EUR',
    source: 'asm-2025-annual-report.pdf',
    fiscal: [
      { fy: 2024, endDate: '2024-12-31', revenue: null, totalAssets: 5162, grossMargin: 50.5, opMargin: null },
      { fy: 2025, endDate: '2025-12-31', revenue: 3200, totalAssets: 5337, totalEquity: 4006, grossMargin: 51.8, opMargin: 30.2 }
    ]
  },

  // ============= TSMC — 2 years from the 2024 report =============
  'TSMC': {
    name: 'TSMC', ticker: '2330.TW', hq: 'TW', layer: 'Foundry', cur: 'TWD',
    source: '2024 Annual Report-E TSMC.pdf — Financial Status + Chairman Letter',
    fiscal: [
      { fy: 2023, endDate: '2023-12-31', revenue: 2161736, opIncome:  920918, netIncome:  838498, totalAssets: 5532371, totalEquity: 3483263, grossMargin: 54.4, opMargin: 42.6, netMargin: 38.8 },
      { fy: 2024, endDate: '2024-12-31', revenue: 2894308, opIncome: 1323060, netIncome: 1173270, totalAssets: 6691938, totalEquity: 4323576, grossMargin: 56.1, opMargin: 45.7, netMargin: 40.5, rd: 206500 }
    ]
  },

  // ============= UMC — 2 years (FY ends Dec) =============
  'UMC': {
    name: 'UMC', ticker: '2303.TW', hq: 'TW', layer: 'Foundry', cur: 'TWD',
    source: '2024AR_ENG_all UMC...pdf — Financial Status',
    fiscal: [
      { fy: 2023, endDate: '2023-12-31', revenue: 222533, opIncome: 57891, netIncome: 60990, totalAssets: 559187, totalEquity: 359579, grossMargin: null, opMargin: 26.0, netMargin: 27.4 },
      { fy: 2024, endDate: '2024-12-31', revenue: 232303, opIncome: 51613, netIncome: 47211, totalAssets: 570201, totalEquity: 378185, grossMargin: 32.6, opMargin: 22.2, netMargin: 20.3, rd: 15600 }
    ]
  },

  // ============= MEDIATEK — 2 years (FY ends Dec) =============
  'MediaTek': {
    name: 'MediaTek', ticker: '2454.TW', hq: 'TW', layer: 'Fabless', cur: 'TWD',
    source: 'MEDIATEK 2024-English-Annual-Report.pdf',
    fiscal: [
      { fy: 2023, endDate: '2023-12-31', revenue: 433446, opIncome: 71874,  netIncome: null, totalAssets: 635038, totalEquity: 374205, grossMargin: 47.8, opMargin: 16.6 },
      { fy: 2024, endDate: '2024-12-31', revenue: 530586, opIncome: 102393, netIncome: null, totalAssets: 697868, totalEquity: 405055, grossMargin: 49.6, opMargin: 19.3 }
    ]
  },

  // ============= CHIPMOS — 2 years (FY ends Dec) =============
  'ChipMOS': {
    name: 'ChipMOS', ticker: '8150.TW', hq: 'TW', layer: 'OSAT', cur: 'TWD',
    source: 'CHIPMOS taiwan annual report 2024 en_ir_year_1820663809.pdf',
    fiscal: [
      { fy: 2023, endDate: '2023-12-31', revenue: null, opIncome: null, netIncome: null, totalAssets: 46160, totalEquity: null, ppe: 19140 },
      { fy: 2024, endDate: '2024-12-31', revenue: 22700, opIncome: null, netIncome: 1420, totalAssets: 45380, totalEquity: 25074, ppe: 19997 }
    ]
  },

  // ============= PHISON — 2 years (FY ends Dec) =============
  'Phison': {
    name: 'Phison', ticker: '8299.TW', hq: 'TW', layer: 'Fabless', cur: 'TWD',
    source: 'Phison_Electronic_Corporation_2024_Annual_Report.pdf',
    fiscal: [
      { fy: 2023, endDate: '2023-12-31', revenue: null, totalAssets: 64963, totalEquity: 42788 },
      { fy: 2024, endDate: '2024-12-31', revenue: null, netIncome: 7953, totalAssets: 69339, totalEquity: 49066 }
    ]
  },

  // ============= LASERTEC — reconstructed 2-year (FY ends Jun) =============
  'Lasertec': {
    name: 'Lasertec', ticker: '6920.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: 'Integrated report LASERTEC 2025.pdf — CEO message',
    fiscal: [
      { fy: 2023, endDate: '2024-06-30', revenue: 213500, opIncome:  81300, netIncome:  59000, opMargin: 38.1, netMargin: 27.6 },
      { fy: 2024, endDate: '2025-06-30', revenue: 251400, opIncome: 122800, netIncome:  84600, opMargin: 48.8, netMargin: 33.7 }
    ]
  },

  // ============= NIKON — partial Q1-Q3 (FY ends Mar) =============
  'Nikon': {
    name: 'Nikon', ticker: '7731.T', hq: 'JP', layer: 'Equipment', cur: 'JPY',
    source: '26third_all_e NIKON 3Q 2025 Result.pdf (Q1-Q3 only, partial year)',
    fiscal: [
      { fy: 2023, endDate: '2024-12-31', revenue: 512600, opIncome:   8100, opMargin:   1.6, note: 'Q1-Q3 cumulative Apr-Dec' },
      { fy: 2024, endDate: '2024-12-31', revenue: 483900, opIncome: -103600, opMargin: -21.4, note: 'Q1-Q3 FY25 (Apr-Dec 24) with ¥90.6B Digital impairment' }
    ]
  },

  // ============= TERADYNE — partial from Q4'25 + Analyst Day =============
  'Teradyne': {
    name: 'Teradyne', ticker: 'TER', hq: 'US', layer: 'Equipment', cur: 'USD',
    source: 'Teradyne_EC Q4\'25 Slides Feb2026.pdf',
    fiscal: [
      { fy: 2024, endDate: '2024-12-31', revenue: 2822, opIncome:  576, grossMargin: 58.6, opMargin: 20.4 },
      { fy: 2025, endDate: '2025-12-31', revenue: 3185, opIncome:  710, grossMargin: 58.3, opMargin: 22.3 }
    ]
  },

  // ============= KLA — partial from 10-K =============
  'KLA': {
    name: 'KLA', ticker: 'KLAC', hq: 'US', layer: 'Equipment', cur: 'USD',
    source: 'KLAC 2025 Annual Report (bookmarked).pdf',
    fiscal: [
      { fy: 2024, endDate: '2024-06-30', revenue:  9812, note: '2024 revenue from prior-year disclosure' },
      { fy: 2025, endDate: '2025-06-30', revenue: 12156, note: 'Semi Process Control = 90% of revenue (+25%)' }
    ]
  }

};

/* Companies WITHOUT multi-year data in this folder (only 0-1 years extracted):
   Realtek, Winbond, Nanya, PSMC, WIN Semi, Sigurd, OSE, KYEC, Ardentec,
   eMemory, M31, AP Memory, WPG, Topco, Marketech, HCL Tech, Fuji Electric,
   Panasonic Industry, AMS OSRAM, Ajinomoto, Shibaura, JSR, Shimadzu, Horiba,
   JEOL, ULVAC, SCREEN, Daifuku, Micronics Japan, Marumae, Accretech, Lintec,
   UACJ, Senju, Medipal, Nagase, ITOCHU, Global Foundries, Misumi, Daitron,
   Rikken Keiki, Organo, Seino, DBJ, SANKI, SGS, ITRI.

   Most of these have 3-5 year data in their full annual reports, but the
   financial-statement pages fell outside my extraction page ranges or
   use image-based tables pdftotext couldn't read.              */
