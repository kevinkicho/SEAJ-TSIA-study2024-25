---
layout: default
title: Advanced Packaging
nav_order: 3
---

# Deep Dive — Advanced Packaging

*Why the center of gravity in semiconductors has shifted from the transistor to the package, and how the companies in your folder are positioned along this new frontier.*

---

## The thesis in one paragraph

For sixty years, "making chips better" meant shrinking transistors — Moore's Law. Starting around the **28 nm node (~2012)**, shrinking stopped being cheap: power-density, interconnect resistance, and lithography-cost problems piled up faster than performance gains. The industry's response was to **stop insisting that a chip be a single monolithic die**. Instead, multiple dies (different nodes, different functions, different vendors) are co-packaged into a single *system-in-package*. The package becomes the new unit of integration — and the packaging house becomes as technologically important as the foundry. This is the single most consequential structural change in the industry since the fabless–foundry split of the 1980s.

Your folder is unusually well-positioned to study it: you have the OSATs (ASE, ChipMOS, KYEC, Sigurd, Orient, Spirox), the substrate monopoly (Ajinomoto ABF), the glass/TGV challenger (Manz), the dicing/grinding monopoly (Disco), the probe-card leader (Micronics Japan), and the HBM test monopoly (Advantest). You just need to assemble the story.

---

## 1. Why packaging took over

### The transistor-side slowdown

- **Dennard scaling ended ~2005.** Transistors kept shrinking but could no longer run faster at lower power.
- **2D interconnect (wires on a chip) scales worse than transistors.** By 7 nm, RC delay in the metal stack consumes more power than the transistors themselves.
- **Leading-edge litho is a cost avalanche.** An EUV scanner runs ~US$180M; a High-NA EUV scanner $380M+. Masks have multiplied in cost too (a High-NA mask set can exceed $100M for a full design).
- **Result:** the cost-per-transistor curve, which had been monotonically declining since 1965, flattened after 10 nm and in some analyses *rose* from 7 nm → 3 nm.

### The package-side opportunity

Three ideas stack to form the new industry grammar:

1. **Heterogeneous integration.** If you can *co-package* a 3 nm compute die with a 7 nm I/O die and a 1y nm DRAM stack, you capture leading-edge benefits only where needed — and avoid paying 3 nm prices for the SRAM-heavy or analog blocks that don't benefit.
2. **Chiplet architecture.** Disaggregate a monolithic SoC into smaller specialized dies ("chiplets"). Each is higher yield (smaller area = fewer defects) and can be mixed across products. Cadence's and ARM's materials in your folder are about exactly this.
3. **Die-to-die bandwidth > package-to-package bandwidth.** Once you bond dies face-to-face (hybrid bonding) or through a silicon interposer, you get ~100× the inter-chip bandwidth at a fraction of the energy compared to PCB-level interconnect. This is why HBM can feed a GPU with >1 TB/s of bandwidth — something inconceivable across a motherboard.

Together these mean: **the highest-value chips in the world (NVIDIA B200, TSMC CoWoS-L; AMD MI300; Apple M-series)** are all packaging-limited, not lithography-limited, today. TSMC's CoWoS capacity — not the 3nm or 2nm fab — was the gating constraint on AI revenue through 2024 and most of 2025.

---

## 2. The packaging taxonomy (and where your companies play)

Advanced packaging is not one thing. It is a stack of formats, each with different costs and targets:

| Format | What it is | Typical use | Who leads |
|---|---|---|---|
| **Wire-bond BGA** | Legacy, die glued to substrate, bond wires carry signal | Low-end MCU, DDR memory | ChipMOS, ASE (commodity tier) |
| **Flip-chip BGA (FC-BGA)** | Die flipped, solder bumps onto **ABF substrate** | CPUs, GPUs, high-end ASICs | Every OSAT; **Ajinomoto monopolizes the dielectric film** |
| **Wafer-Level CSP (WLCSP)** | Package built on the wafer itself | Phones, wearables, power ICs | ASE, TSMC (InFO) |
| **Fan-out WLP / PLP** | Redistribute I/O by molding & re-wiring across a reconstituted wafer (or panel) | Mobile AP (Apple A-series early days), automotive | TSMC InFO, ASE FOCoS, Amkor SWIFT |
| **Silicon interposer (2.5D)** | Dies sit side-by-side on a silicon interposer with TSVs | GPU + HBM | **TSMC CoWoS** — ~85% share. Intel EMIB variant. Samsung I-Cube. |
| **3D IC / face-to-face bonding** | Stack dies directly, connect via microbumps or copper | AMD X3D V-cache, HBM stacks | TSMC SoIC, Samsung X-Cube, Intel Foveros |
| **Hybrid bonding** | Copper-to-copper direct bond, no solder — bandwidth ↑, pitch ↓ | Next-gen 3D, HBM4+ | **Besi (sole merchant tool supplier)** + AMAT; TSMC internal |
| **HBM stack** | 8–16 DRAM dies stacked with TSVs on a buffer die | AI GPUs | SK Hynix / Samsung / Micron make the stack; Advantest tests it |
| **Glass substrate / TGV** | Glass replaces organic ABF as the interposer substrate | Emerging — AI accelerators 2027+ | Intel (pilot), Samsung research, **Manz (TGV tool)** |
| **Fan-out Panel-Level (FOPLP)** | Fan-out, but on a rectangular panel (~600×600mm) instead of round wafer | Cost-reduced reconstituted packaging | Samsung, ASE, Powertech (your fan-out roadmap image is this) |

### Where each of your companies sits

**TSMC** (your `2024 Annual Report-E TSMC.pdf`) — **the pacesetter**. CoWoS (2.5D) + InFO (fan-out) + SoIC (3D) are TSMC-branded flows. They are officially a "foundry," but advanced-packaging revenue is now a material (and fast-growing) line item. Read the Chairman's letter and the "Technology" section in the annual report for explicit language on CoWoS capacity doubling in 2024 and again in 2025 — this is the single most important disclosure in the document for packaging study.

**ASE Technology Holding** (`20250603150724453273521_en ASE holdings annual report 2024.pdf`) — **the OSAT scale leader and the primary TSMC alternative** for customers who want merchant packaging. ASE's advanced-package portfolio: **FOCoS** (fan-out chip-on-substrate — ASE's answer to TSMC CoWoS), **VIPack** (ASE's umbrella for vertical integration), **SiP** (system-in-package — Apple watch is an ASE SiP reference design). ASE is also the largest buyer of Micronics Japan probe cards and one of the top buyers of ABF.

**ChipMOS** (`CHIPMOS taiwan annual report 2024 en_ir_year_1820663809.pdf`) — **specialist in memory and display-driver packaging**. Less glamorous than HBM but a durable niche: every LCD TV/monitor display-driver IC is assembled and tested by someone, and ChipMOS is the #1. The memory piece is DRAM (not HBM) and NAND for the Chinese market.

**KYEC — King Yuan Electronics** (`KYEC(2449)_4Q25 Investor update_English.pdf`) — **test-only**, the largest dedicated test-house in Taiwan. Test is the stage of packaging where defects are culled; for HBM and advanced SoC the test time per device has grown from seconds to minutes, which is why Advantest and KYEC benefit together from every new AI accelerator ramp. KYEC is a major NVIDIA subcontractor.

**Sigurd Microelectronics** (`SIGURD annual report 2024 113q4_copy.pdf`) — mid-tier OSAT; WLCSP and flip-chip for driver ICs.

**Orient Semiconductor (OSE)** (`議事手冊114年(all)(EN)上傳檔 Orient Semiconductor 2024 ANNUAL REPORT.pdf`) — legacy OSAT, strong in memory modules and commodity packaging.

**Spirox** (`SPIROX annual report 2024 113年度年報(英文).pdf`) — not an OSAT itself; a **test-services + probe-card-distribution** company. Represents FormFactor (the US probe-card leader) in Taiwan. Useful as a proxy for probe-card demand in TW.

**Ajinomoto Fine-Techno Co. (AFT)** (`AJINOMOTO FINE INC ABF-presentation.pdf`) — **the packaging-world monopoly you cannot name in casual conversation but every engineer knows**. ABF (Ajinomoto Build-up Film) is the dielectric film used in essentially every FC-BGA substrate shipped globally. **Every Intel/AMD/NVIDIA CPU and GPU substrate contains ABF.** Their share is ~100% of the dielectric layer; yield-stabilized challengers (Taiyo Ink, Sekisui) have existed for years but never scaled. The chairman letter in the ABF deck is worth memorizing: their KPI is *yield-loss days* — one missed shift = global substrate shortage.

**Senju Metal Industry** (`SENJU 2025_soldering_materials_catalogue.pdf`) — solder paste, micro-bumps (<40 µm), and solder preforms. Every flip-chip bump and every TSV micro-bump uses solder; Senju and Japan's peer makers own the ultra-fine pitch solder materials market.

**Lintec** (`Integrated_Report_2025_all LINTEC.pdf`) — dicing/back-grinding tapes. Consumable with no substitute for specific bleeding-edge thicknesses. Boring but sticky.

**Disco** (`dar2020 DISCO ANNUAL report 2020.pdf`) — **the dicing/grinding monopoly**. Every wafer is diced into dies by a Disco saw; for HBM, wafers must be ground to 50 µm or thinner before stacking — a Disco process. Note your file is 2020; a fresher Disco annual would show the step-function demand from HBM and SoIC.

**Accretech / Tokyo Seimitsu** (`IntegratedReport2025_E ACCRETECH 2025.pdf`) — the #2 to Disco's #1 in dicing + probers. Their wafer probe business is directly tied to HBM test (larger die = more probe contacts = higher probe-card cost).

**Micronics Japan** (`LINEUP2026 MICRONICS JAPAN.pdf`) — **probe cards for advanced test**, including vertical probe cards for HBM and AI accelerators. Probe-card market is a quiet HBM beneficiary — every HBM stack is tested with a probe card, and HBM probe cards are among the most expensive ever built (>$500K per card). The `PROBE CARD 2021 Screenshot 2026-03-13 134947.png` in your folder is a market snapshot — revisit with 2024 data after you read the LINEUP2026.

**Favite** (`FAVITE annual report 2024 113年報_英文版上傳.pdf`) — TW probe pin/probe card supplier.

**Manz** (`MANZ 2025_0923_TGV-solutions_DataSheet.pdf`, `MANZ 2025_EN_IC_substrate_flyer_1027.pdf`) — **the glass substrate / TGV tool supplier you must not ignore**. TGV = through-glass via. If glass replaces organic ABF substrates at the leading edge (Intel is piloting, Samsung researching, TSMC watching), Manz's laser-drilling TGV tool is the pick-and-shovel play. This is speculative — glass substrate volume is near-zero today — but it's the clearest 2027+ catalyst in your folder.

**UACJ** (`00 UACJ integrated report 2025.pdf`) — aluminum for heat spreaders and IC packaging shells. Commodity-adjacent but positioned above the pure metals tier because aluminum-alloy formulation for thermal performance is a real spec.

---

## 3. The HBM thread (ties almost everything together)

HBM (High Bandwidth Memory) is the single technology that turned advanced packaging into an AI story. An AI training run can consume tens of terabytes per second of memory bandwidth; only HBM delivers that in a single package. And every HBM part is an **advanced-packaging object**: 8–12+ DRAM dies stacked vertically, connected by TSVs, on top of a buffer die, then placed next to a GPU on a silicon interposer (CoWoS).

The supply chain looks like this — notice how many of your companies touch it:

```
DRAM wafer    →  TSV etch         →  Die thinning  →  Stack bonding  →  HBM stack test
(SK Hynix/    (Lam, TEL, AMAT)    (Disco grinder)   (Besi, AMAT,     (Advantest HBM tester
Samsung/                                              TSMC/SK Hynix     + Micronics vertical
Micron —                                              internal)         probe card)
in your folder:
Nanya/Winbond
— similar flow
but LP/DDR
not HBM)

            ↓

GPU die         →  CoWoS assembly (TSMC)   →  Substrate: ABF on       →  OSAT final test
(NVIDIA/AMD/        Silicon interposer          Unimicron/Ibiden/          + ship
Broadcom —          + HBM stacks                Shinko substrate           (ASE, KYEC)
in your folder:                                  with **Ajinomoto ABF**
represented via
Intel Core Ultra)
```

Every arrow has one of "your" companies on it: **Disco** (thinning), **Advantest** (HBM test), **Micronics** (HBM probe card), **Ajinomoto** (substrate film), **TSMC** (CoWoS), **ASE** (alternative assembler + final test for some SKUs), **KYEC** (outsourced test for some SKUs).

The part you *don't* have is the HBM manufacturer itself (SK Hynix, Samsung, Micron). Closing that loop is priority 1 on your reading list.

---

## 4. The second thread: AI-accelerator substrates

You also have the **substrate** layer — less visible but equally important. A GPU die sitting on an interposer still needs to sit on an organic substrate that goes onto the motherboard. Organic substrates (ABF-based) were designed for 2000s-era CPUs (few hundred watts, few thousand I/O). AI accelerators push both limits: 1000W and 10,000+ I/O.

This is stressing the ABF stack to its limit. Two responses:

1. **Thicker, larger ABF substrates with more layers** — the current path. The Ajinomoto monopoly benefits most. Substrate makers (Unimicron, Ibiden, Shinko — not in your folder) also benefit. Even Nan Ya PCB, ZDT, Kinsus are scaling up.
2. **Replace the substrate with glass** — the future path. Zero glass substrate volume in 2024, tentative pilots in 2025–2027, meaningful volume 2028+. **Manz TGV** is in your folder on this angle.

If you want one variable to track over the next 24 months to calibrate this thesis: **Ajinomoto's ABF shipment growth rate** — disclosed in their IR decks. Flat = problem (glass transitioning). Accelerating = organic substrate still winning.

---

## 5. What to read from your folder (in order)

Given the 30+ files that touch packaging, here's a focused 2-hour reading path:

1. **TSMC 2024 Annual Report** — read the "Technology Leadership" and "CoWoS" sections. 20 min. (Jump to pages ~30–80 of the business overview.)
2. **ASE Holdings 2024 Annual Report** — read the Chairman's letter + "Advanced Packaging" overview. 25 min.
3. **Ajinomoto ABF presentation** — whole deck (it's short). 15 min.
4. **Micronics Japan LINEUP2026** — flip through the probe-card product pages to see HBM vs. SoC vs. memory card types. 15 min.
5. **Advantest 2025 Integrated Report** — read segment disclosures (you'll see a huge HBM test line item). 20 min.
6. **Disco 2020 Annual Report** — historical baseline; then mentally ask "how much has this business doubled given HBM demand?" (answered by reading a current Disco report you'd add). 15 min.
7. **CXL 4.0 webinar** — for the "memory disaggregation" alt-narrative that partially *substitutes* for HBM scaling. 15 min.

Two hours gives you the full vertical.

---

## 6. The five open questions this deep dive surfaces

After all this, the real investment/industry questions are:

1. **Can ASE take CoWoS-class share from TSMC?** ASE's FOCoS-Bridge is the best external alternative; the question is whether NVIDIA/AMD will dual-source meaningful volume.
2. **Who wins hybrid bonding at scale?** Besi (tools) is a lock for now; TSMC SoIC and Samsung X-Cube compete in manufacturing flows. AMAT + Besi are trying to make the second-source tool.
3. **When does glass substrate cross the 5% adoption threshold?** That's the tipping point. Manz is positioned; Ajinomoto has the most to lose.
4. **Does HBM4's new buffer-die architecture (more logic) shift value from SK Hynix back toward TSMC?** HBM4 lets foundries own the custom logic die at the bottom of the stack — a huge profit-pool transfer.
5. **Where does Japan fit?** Japan makes most of the *tools* (Disco, Advantest, Micronics, Accretech) and *materials* (Ajinomoto, Senju, Lintec) for advanced packaging. But Japan has almost no advanced-packaging service providers (no JP OSAT at scale). Will Japan stay a picks-and-shovels player or try to move downstream (e.g., Rapidus packaging, Rakuten TSMC JASM)? Follow the SEAJ statistics you have.

---

## Takeaway

Your collection is *exactly* the right shape to study advanced packaging. You have every layer except the memory/HBM manufacturers themselves (easy gap to fill). The mental model to hold: packaging = the new transistor. Companies that used to be "commodity back-end" are now process-differentiated monopolies. Tools that used to be consumables are now performance-critical. And the Japan-Taiwan axis — which is exactly the axis you've been collecting — is where this story is playing out.
