/* =====================================================================
   Company financials dataset — native currency, tagged for filtering.
   All revenue / income / asset figures are in MILLIONS of native currency
   (TWD, JPY, USD, EUR). Margins are percentages. YoY is percent change
   in local-currency revenue vs prior fiscal year.

   Layers: "Materials", "Equipment", "EDA/IP", "Fabless", "IDM",
           "Foundry", "OSAT", "Distribution", "Research".
   Regions: "TW", "JP", "US", "EU", "Other".

   Null values = data not extracted from this folder's PDFs. The company
   still appears in non-financial filters but is excluded from charts.
   ===================================================================== */

window.COMPANIES = [
  // ======================= TAIWAN — Foundry =======================
  {
    name: 'TSMC', ticker: '2330.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 2894310, revenueYoy: 33.9,
    opIncome: 1322700, netIncome: 1173270,
    totalAssets: 6691938, totalEquity: 4323576,
    grossMargin: 56.1, opMargin: 45.7, netMargin: 40.5,
    note: 'Leading-edge + CoWoS advanced pkg'
  },
  {
    name: 'UMC', ticker: '2303.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 232300, revenueYoy: null,
    opIncome: 51571, netIncome: 47211,
    totalAssets: 570201, totalEquity: 378185,
    grossMargin: 32.6, opMargin: 22.2, netMargin: 20.3,
    note: 'Mature-node foundry (28/22nm)'
  },
  {
    name: 'VIS / Vanguard', ticker: '5347.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: 148706, totalEquity: 68667,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '8" specialty foundry; NXP JV'
  },
  {
    name: 'PSMC / Powerchip', ticker: '6770.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 44700, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Foundry + Tata India JV'
  },
  {
    name: 'WIN Semiconductors', ticker: '3105.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'GaAs RF PA foundry #1'
  },

  // ======================= TAIWAN — Fabless =======================
  {
    name: 'MediaTek', ticker: '2454.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 530600, revenueYoy: 22.4,
    opIncome: 102406, netIncome: null,
    totalAssets: 697868, totalEquity: 405055,
    grossMargin: 49.6, opMargin: 19.3, netMargin: null,
    note: '#2 SoC globally; entering AI-ASIC'
  },
  {
    name: 'Realtek', ticker: '2379.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'PC connectivity leader'
  },
  {
    name: 'Phison', ticker: '8299.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: 7953,
    totalAssets: 69339, totalEquity: 49066,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'NAND flash controllers #1-2'
  },
  {
    name: 'Himax', ticker: 'HIMX', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'USD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: 1640, totalEquity: 896,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Display driver ICs; 82.9% rev concentration'
  },
  {
    name: 'Megawin', ticker: '6215.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null,
    opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '8-bit MCUs'
  },
  {
    name: 'Richwave', ticker: '4968.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'WiFi FEM / RF PA'
  },
  {
    name: 'Weltrend', ticker: '2436.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'USB-PD controllers'
  },
  {
    name: 'Alcor Micro', ticker: '3227.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'USB hubs, card readers'
  },
  {
    name: 'EGIS Tech', ticker: '6462.TW', hq: 'TW', layer: 'Fabless',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Fingerprint sensors'
  },

  // ======================= TAIWAN — Memory IDM =======================
  {
    name: 'Nanya Technology', ticker: '2408.TW', hq: 'TW', layer: 'IDM',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'DRAM (DDR3/DDR4)'
  },
  {
    name: 'Winbond', ticker: '2344.TW', hq: 'TW', layer: 'IDM',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Specialty memory (SpiFlash)'
  },
  {
    name: 'Episil', ticker: '3438.TW', hq: 'TW', layer: 'IDM',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Power discrete IDM (150mm)'
  },

  // ======================= TAIWAN — OSAT =======================
  {
    name: 'ASE Holdings', ticker: '3711.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 595410, revenueYoy: 2.3,
    opIncome: 39166, netIncome: 33926,
    totalAssets: null, totalEquity: null,
    grossMargin: 16.3, opMargin: 6.6, netMargin: 7.6,
    note: '#1 OSAT globally'
  },
  {
    name: 'ChipMOS', ticker: '8150.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: 22700, revenueYoy: null,
    opIncome: null, netIncome: 1420,
    totalAssets: 45380, totalEquity: 25074,
    grossMargin: null, opMargin: null, netMargin: 6.3,
    note: 'Memory + display driver packaging'
  },
  {
    name: 'KYEC', ticker: '2449.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'TW largest test-only house; NVIDIA subcontractor'
  },
  {
    name: 'Sigurd', ticker: '6257.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Mid-tier OSAT (WLCSP)'
  },
  {
    name: 'Orient Semi (OSE)', ticker: '2329.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Legacy OSAT'
  },
  {
    name: 'ZDT', ticker: '4958.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'PCBs + IC substrates'
  },

  // ======================= TAIWAN — EDA/IP =======================
  {
    name: 'eMemory', ticker: '3529.TW', hq: 'TW', layer: 'EDA/IP',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Embedded NVM IP monopoly'
  },
  {
    name: 'M31 Technology', ticker: '6643.TW', hq: 'TW', layer: 'EDA/IP',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Foundation IP'
  },
  {
    name: 'AP Memory', ticker: '6531.TW', hq: 'TW', layer: 'EDA/IP',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'PSRAM / low-power memory IP'
  },

  // ======================= TAIWAN — Distribution & Niche =======================
  {
    name: 'WPG Holdings', ticker: '3702.TW', hq: 'TW', layer: 'Distribution',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '#1 Asian semi distributor'
  },
  {
    name: 'Topco Global', ticker: '3706.TW', hq: 'TW', layer: 'Distribution',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'TW electronics distributor'
  },
  {
    name: 'Marketech', ticker: '6196.TW', hq: 'TW', layer: 'Distribution',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'TW materials + subsystems'
  },
  {
    name: 'Spirox', ticker: '3055.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Probe card distribution'
  },
  {
    name: 'Leatec Fine Ceramics', ticker: null, hq: 'TW', layer: 'Materials',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Equipment ceramics'
  },
  {
    name: 'Taiwan Mask', ticker: '2338.TW', hq: 'TW', layer: 'Foundry',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Photomask maker'
  },
  {
    name: 'Favite', ticker: '3131.TW', hq: 'TW', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Probe pin / probe card'
  },
  {
    name: 'CSUN Mfg', ticker: '6274.TW', hq: 'TW', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Solar + semi production eq'
  },
  {
    name: 'Creating Nanotech', ticker: '3055.TW', hq: 'TW', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Nano-imprint equipment'
  },
  {
    name: 'Gallant PM', ticker: '5443.TW', hq: 'TW', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'LCD + semi equipment'
  },
  {
    name: 'Ardentec', ticker: '3264.TW', hq: 'TW', layer: 'OSAT',
    fyEnd: '2024-12-31', cur: 'TWD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Independent test house'
  },

  // ======================= JAPAN — Equipment =======================
  {
    name: 'Lasertec', ticker: '6920.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-06-30', cur: 'JPY',
    revenue: 251400, revenueYoy: 17.8,
    opIncome: 122800, netIncome: 84600,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: 48.8, netMargin: 33.7,
    note: 'EUV mask inspection monopoly'
  },
  {
    name: 'Advantest', ticker: '6857.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: 779700, revenueYoy: 60.3,
    opIncome: 228455, netIncome: 161200,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: 29.3, netMargin: 20.7,
    note: 'HBM test monopoly; SoC ATE'
  },
  {
    name: 'Disco', ticker: '6146.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2020-03-31', cur: 'JPY',
    revenue: 147500, revenueYoy: null,
    opIncome: 38053, netIncome: 28868,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: 25.8, netMargin: 19.6,
    note: 'Dicing/grinding monopoly (file is FY20 — stale)'
  },
  {
    name: 'Ebara', ticker: '6361.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'JPY',
    revenue: 800000, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: 1005085, totalEquity: 485336,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'CMP + vacuum pumps'
  },
  {
    name: 'Accretech', ticker: '7729.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: 150500, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: 237952, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Probers + dicing'
  },
  {
    name: 'Kokusai Electric', ticker: '6525.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: 238900, revenueYoy: 32.0,
    opIncome: 51320, netIncome: 36004,
    totalAssets: null, totalEquity: null,
    grossMargin: 42.6, opMargin: 21.5, netMargin: 15.1,
    note: 'Batch ALD / thermal'
  },
  {
    name: 'Nikon', ticker: '7731.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: 483900, revenueYoy: -5.6,
    opIncome: -103600, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: -21.4, netMargin: null,
    note: 'Litho #2 (Q1-Q3 partial + impairment)'
  },
  {
    name: 'Canon', ticker: '7751.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-12-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'ArFi + nano-imprint litho'
  },
  {
    name: 'Hitachi High-Tech', ticker: null, hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'CD-SEM near-monopoly'
  },
  {
    name: 'JEOL', ticker: '6951.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'E-beam / TEM / SEM'
  },
  {
    name: 'Shimadzu', ticker: '7701.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Analytical instruments'
  },
  {
    name: 'Horiba', ticker: '6856.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Gas / particle / spectroscopy'
  },
  {
    name: 'ULVAC', ticker: '6728.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-06-30', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Vacuum + PVD'
  },
  {
    name: 'Shibaura Mech', ticker: '6590.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Wafer processing + PVD'
  },
  {
    name: 'Screen Holdings', ticker: '7735.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '#1 single-wafer cleaner'
  },
  {
    name: 'Daifuku', ticker: '6383.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'OHT AMHS monopoly'
  },
  {
    name: 'Micronics Japan', ticker: '6871.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Advanced probe cards (HBM)'
  },
  {
    name: 'Marumae', ticker: '6264.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-08-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Custom Al/quartz/SiC parts'
  },
  {
    name: 'CKD', ticker: '6407.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Pneumatics, gas valves'
  },
  {
    name: 'Rikken Keiki', ticker: '7734.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Gas detection (HF, SiH4)'
  },
  {
    name: 'SINFONIA Tech', ticker: '6507.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Clean material handling'
  },
  {
    name: 'Organo', ticker: '6368.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2026-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Ultrapure water systems'
  },
  {
    name: 'Misumi Group', ticker: '9962.T', hq: 'JP', layer: 'Equipment',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Components e-commerce'
  },

  // ======================= JAPAN — Materials =======================
  {
    name: 'Shin-Etsu', ticker: '4063.T', hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Silicon wafers #1 globally'
  },
  {
    name: 'JSR', ticker: '4185.T', hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Photoresist top-3'
  },
  {
    name: 'Ajinomoto Fine-Techno', ticker: '2802.T', hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'ABF substrate monopoly'
  },
  {
    name: 'Senju Metal', ticker: null, hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Solder paste + bumps'
  },
  {
    name: 'Lintec', ticker: '7966.T', hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Back-grinding / dicing tape'
  },
  {
    name: 'UACJ', ticker: '5741.T', hq: 'JP', layer: 'Materials',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Aluminum for packaging'
  },
  {
    name: 'Nagase', ticker: '8012.T', hq: 'JP', layer: 'Distribution',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Specialty chemicals trading'
  },

  // ======================= JAPAN — Power / IDM =======================
  {
    name: 'Fuji Electric', ticker: '6504.T', hq: 'JP', layer: 'IDM',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'IGBT + SiC modules'
  },
  {
    name: 'Panasonic Industry', ticker: '6752.T', hq: 'JP', layer: 'IDM',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Capacitors + components'
  },

  // ======================= JAPAN — Distribution / Research =======================
  {
    name: 'Daitron', ticker: '7609.T', hq: 'JP', layer: 'Distribution',
    fyEnd: '2025-12-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Equipment + components'
  },
  {
    name: 'ITOCHU', ticker: '8001.T', hq: 'JP', layer: 'Distribution',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Trading house'
  },
  {
    name: 'Medipal', ticker: '7459.T', hq: 'JP', layer: 'Distribution',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Pharma distribution (tangential)'
  },
  {
    name: 'Seino', ticker: '9076.T', hq: 'JP', layer: 'Distribution',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '3PL logistics'
  },
  {
    name: 'SANKI', ticker: '1961.T', hq: 'JP', layer: 'Research',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Cleanroom / HVAC engineering'
  },
  {
    name: 'DBJ', ticker: null, hq: 'JP', layer: 'Research',
    fyEnd: '2025-03-31', cur: 'JPY',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'State bank — Rapidus funder'
  },

  // ======================= US — Equipment =======================
  {
    name: 'Applied Materials', ticker: 'AMAT', hq: 'US', layer: 'Equipment',
    fyEnd: '2025-10-26', cur: 'USD',
    revenue: 28368, revenueYoy: 4.4,
    opIncome: 8289, netIncome: null,
    totalAssets: 36299, totalEquity: 20415,
    grossMargin: 48.7, opMargin: 29.2, netMargin: null,
    note: '#1 WFE by revenue'
  },
  {
    name: 'KLA', ticker: 'KLAC', hq: 'US', layer: 'Equipment',
    fyEnd: '2025-06-30', cur: 'USD',
    revenue: 12200, revenueYoy: 24.0,
    opIncome: null, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Process control leader (~50% share)'
  },
  {
    name: 'Lam Research', ticker: 'LRCX', hq: 'US', layer: 'Equipment',
    fyEnd: '2025-06-29', cur: 'USD',
    revenue: 18400, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: 21345, totalEquity: 9862,
    grossMargin: null, opMargin: null, netMargin: null,
    note: '#1 etch; plasma ALD/CVD'
  },
  {
    name: 'Teradyne', ticker: 'TER', hq: 'US', layer: 'Equipment',
    fyEnd: '2025-12-31', cur: 'USD',
    revenue: 3200, revenueYoy: null,
    opIncome: 714, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: 58.3, opMargin: 22.3, netMargin: null,
    note: 'SoC ATE + robotics'
  },
  {
    name: 'Global Foundries', ticker: 'GFS', hq: 'US', layer: 'Foundry',
    fyEnd: '2025-12-31', cur: 'USD',
    revenue: 6790, revenueYoy: null,
    opIncome: null, netIncome: null,
    totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Specialty foundry (RF/auto)'
  },

  // ======================= Europe — Equipment & Sensors =======================
  {
    name: 'ASM International', ticker: 'ASM.AS', hq: 'EU', layer: 'Equipment',
    fyEnd: '2025-12-31', cur: 'EUR',
    revenue: 3200, revenueYoy: 3.4,
    opIncome: 966, netIncome: null,
    totalAssets: 5337, totalEquity: 4006,
    grossMargin: 51.8, opMargin: 30.2, netMargin: null,
    note: 'ALD leader'
  },
  {
    name: 'Zeiss', ticker: null, hq: 'EU', layer: 'Equipment',
    fyEnd: '2024-09-30', cur: 'EUR',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'EUV optics (private)'
  },
  {
    name: 'AMS OSRAM', ticker: 'AMS.SW', hq: 'EU', layer: 'IDM',
    fyEnd: '2025-12-31', cur: 'EUR',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'Optical/biometric sensors'
  },
  {
    name: 'Manz', ticker: 'M5Z.DE', hq: 'EU', layer: 'Equipment',
    fyEnd: '2024-12-31', cur: 'EUR',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'TGV / glass substrate tools'
  },

  // ======================= US/EU — EDA/IP =======================
  {
    name: 'Cadence', ticker: 'CDNS', hq: 'US', layer: 'EDA/IP',
    fyEnd: '2025-12-31', cur: 'USD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'EDA #2 + chiplet Physical AI'
  },
  {
    name: 'ARM', ticker: 'ARM', hq: 'Other', layer: 'EDA/IP',
    fyEnd: '2025-03-31', cur: 'USD',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'CPU IP ubiquity'
  },

  // ======================= India =======================
  {
    name: 'HCL Technologies', ticker: 'HCLTECH', hq: 'Other', layer: 'Distribution',
    fyEnd: '2025-03-31', cur: 'INR',
    revenue: null, revenueYoy: null, opIncome: null, netIncome: null, totalAssets: null, totalEquity: null,
    grossMargin: null, opMargin: null, netMargin: null,
    note: 'IT / ER&D services for semi'
  }
];

/* Hardcoded fallback FX rates (USD base) — used when Frankfurter is
   unreachable or doesn't include a currency. Frankfurter covers ECB daily
   reference rates (~30 currencies) but TWD is NOT in that list, so it's
   always hardcoded here. Values as of 2026-04 approximate spot:  */
window.FX_FALLBACK = {
  asOf: '2026-04-23',
  rates: {
    USD: 1.00,
    TWD: 32.5,      // not in ECB — hardcoded
    JPY: 151.0,     // from Frankfurter if available
    EUR: 0.93,
    GBP: 0.79,
    KRW: 1355,
    CNY: 7.22,
    INR: 83.5,
    HKD: 7.78
  }
};
