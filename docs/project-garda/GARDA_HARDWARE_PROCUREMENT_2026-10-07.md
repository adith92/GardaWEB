# GARDA Hardware Procurement — 2026-10-07

Status: **active procurement shortlist**

This file records the current hardware-shopping decision for the GARDA custom 4-GPU workstation/server. It complements `GARDA_HARDWARE_PLAN_2026-10-06.md`.

## 1. Selected direction

### CPU — AMD Ryzen Threadripper 1950X
- 16 cores / 32 threads
- Socket TR4 / X399
- 64 PCIe lanes
- Current Shopee reference: Rp2,850,000
- Link: https://shopee.co.id/PROCESSOR-X399-AMD-TR4-THREADRIPPER-1950X-i.15915400.54710346558
- **Selected over Threadripper 1920X**
- 1920X reference: Rp2,355,000, 12C/24T
- The ~Rp495,000 saving is not attractive enough to lose 4 cores / 8 threads for GARDA NVR, FFmpeg, DB, VM and orchestration workloads.

1920X link:
https://shopee.co.id/PROCESSOR-X399-AMD-TR4-THREADRIPPER-1920X-i.15915400.55261812851

## 2. Motherboard — preferred

### Gigabyte X399 AORUS PRO
Current preferred board.

- TR4 / AMD X399
- 8 DDR4 DIMM sockets
- 128 GB official maximum
- Quad-channel
- ECC / non-ECC **unbuffered** DDR4
- 2 x PCIe 3.0 x16 electrical
- 2 x PCIe 3.0 x8 electrical
- 4-way graphics support
- 8 x SATA
- 3 x M.2
- Realtek ALC1220 onboard audio
- Current local price reference: Rp3,001,055

Shopee:
https://shopee.co.id/Motherboard-GIGABYTE-X399-Aorus-Pro-i.271960024.3557761736

Official:
https://www.gigabyte.com/id/Motherboard/X399-AORUS-PRO-rev-10/sp

Alternatives:
1. ASUS ROG Zenith Extreme X399 — hunt used if healthy and cheap.
2. MSI X399 SLI PLUS — technically good, only buy if second-hand price is competitive.
3. ASRock X399 Taichi — excellent 4-GPU topology, hunt used/bundle.

## 3. RAM decision

### RAM decision after deep compatibility check
**LOCK: 128 GB = 8 x 16 GB DDR4-2666 UDIMM, same part number where possible.**

The previously preferred **4 x 32 GB** layout is **NOT APPROVED for procurement on the X399 AORUS PRO** because it cannot be confirmed by official compatibility data.

Evidence:
- GIGABYTE official specification: 8 DIMM sockets, maximum 128 GB total, ECC/non-ECC **unbuffered** DDR4.
- GIGABYTE's published memory QVL for this board lists module densities up to **16 GB** and includes 128 GB configurations built from **8 x 16 GB** modules.
- Kingston's current configurator for X399 AORUS PRO states maximum 128 GB and says supported configurations are reached using **4 GB, 8 GB and 16 GB modules in groups of four**.
- G.SKILL sells 4 x 32 GB DDR4 kits, but their QVL for those 128 GB kits does **not** list X399 AORUS PRO.
- Latest GIGABYTE BIOS notes (through F3d, 2024) do not state added 32 GB-per-DIMM support or an increase beyond 128 GB.

Conclusion:
- **8 x 16 GB UDIMM = approved / procurement-safe path.**
- **4 x 32 GB UDIMM = unsupported/unverified for this board; do not buy unless a seller can demonstrate the exact board + 1950X + exact RAM part number booting and passing memory test.**

Preferred modules:
- Samsung
- SK Hynix
- Micron
- Standard desktop UDIMM / ECC UDIMM only when confirmed compatible.

### Critical compatibility rule
**DO NOT BUY DDR4 RDIMM / Registered / LRDIMM server memory for this X399 build.**

The X399 AORUS PRO specification supports ECC and non-ECC **unbuffered** DIMMs. Cheap HP/Dell/Lenovo server RDIMMs are therefore rejected.

Rejected user candidates:
- Generic server ECC RDIMM listing
- Samsung 64GB 4DRx4 ECC RDIMM
- Samsung 64GB DDR4 2400T ECC REGISTER

### 32 GB-per-DIMM desktop kits
User-supplied 64GB 2x32 kits are now **test-only / not approved for procurement** on X399 AORUS PRO. If an experimental test is ever attempted:
- use genuine UDIMM
- update/check BIOS
- boot at JEDEC / 2666 first
- run MemTest for an extended period
- do not mix different kits if avoidable

Current candidates:
- Team T-Create 64GB 2x32 3200
- Team Vulcan Z 64GB 2666
- Corsair Vengeance 64GB 2x32 used
- V-GEN Tsunami 64GB 2666
- Generic 64GB 2x32 only if exact part number and return policy are clear

## 4. Chassis shortlist

### Rank 1 — Phanteks Enthoo Pro II Server Edition
**Selected chassis.**

- Full tower
- 11 PCI slots
- Up to 10 x 3.5-inch HDD in Server Edition
- 4 HDD brackets included
- Need two additional 3.5-inch brackets for the initial 6-HDD target
- Excellent space for GPU risers / airflow
- Current local reference: about Rp2.599m–Rp2.749m

Shopee:
https://shopee.co.id/Phanteks-Enthoo-Pro-2-Pro-II-Server-Edition-Closed-Panel-Satin-Black-i.1586516705.57256282856

Official manual:
https://phanteks.com/manuals/Enthoo_Pro2_Server_Edition_Manual_v1.1.pdf

### Other options
- Fractal Define 7 XL — premium storage option, 6 universal drive brackets included, up to 18 positions, 9+3 expansion slots.
- Corsair 7000D Airflow — 6 x 3.5-inch HDD bays, 8 horizontal + 3 vertical expansion slots.
- Cooler Master HAF 700 — 9 combo drive bays and 8 expansion slots; large and expensive.
- Phanteks Enthoo Pro original — watch for a cheap used unit.

## 5. PSU shortlist

The final PSU must be selected **after the exact four GPU models and power limits are locked**.

### Budget 1200W candidate
Phanteks AMP GH 1200W Platinum
- about Rp2.589m–Rp2.649m
- only select after total GPU TDP confirms adequate headroom

### Preferred 1200W baseline
FSP Hydro PTM Pro 1200W Platinum
- about Rp4.099m
- baseline for four mid-power / power-limited GPUs

Shopee:
https://shopee.co.id/FSP-PSU-HYDRO-PTM-PRO-1200W-80-PLATINUM-Modular-ATX3.0-PCIe-Gen5-PSU-Power-Supply-i.1093155061.27986171445

### Safer unknown-GPU option
Corsair AX1600i 1600W Platinum
- about Rp8.985m
- preferred if the four GPU models remain unknown and the goal is to avoid replacing the PSU later

Shopee:
https://shopee.co.id/Power-Supply-Corsair-AX1600i-%E2%80%94-1600W-80-Platinum-Fully-Modular-i.24517949.23534708229

## 6. Storage / cooling / operator peripherals

### SSD
Target: 1 TB NVMe for initial OS/apps.
Current value candidate:
- Team MP33 1TB NVMe Gen3
- around Rp1.35m–Rp1.44m
- X399 runs PCIe Gen3, so paying heavily for a high-end Gen4 SSD is unnecessary for this first drive.

### CPU cooler
Noctua NH-U14S TR4-SP3
- TR4-specific cold plate
- around Rp1.435m–Rp1.68m
- preferred for simple 24/7 operation

### Case fans
Deepcool FK120 3-pack x2
- 6 PWM fans total
- approximately Rp918,000 total using Rp459,000 per 3-pack reference

### Sound
**No discrete sound card required.**
The X399 AORUS PRO already has Realtek ALC1220 onboard audio. A PCIe sound card would consume valuable physical PCIe space in a four-GPU build. Use onboard audio or a small USB audio device if a Windows VM needs dedicated audio.

### Keyboard
Budget:
- Fantech Atom61 MK211 mechanical — about Rp198,000

Better operator layout:
- Ajazz AK820 V2 75% — about Rp379,000

### Mouse
- Logitech G102 — around Rp280,000–300,000

### Monitor
Used target:
- Dell P2419H 23.8/24-inch FHD IPS — approximately Rp1.1m–Rp1.45m depending condition

New alternative:
- Lenovo L24-4E 24-inch IPS 100Hz — about Rp1.233m
- ViewSonic VA240A-H 24-inch IPS 120Hz — about Rp1.339m

## 7. Current rough budget

Excludes:
- all four GPUs
- six CCTV HDDs
- shipping
- HDD bracket extras / GPU risers if required

### Baseline with 1200W FSP
Approx. **Rp23.915m** using the approved 8x16GB RAM target.
using:
- 1950X
- X399 AORUS PRO
- Rp6m target budget for used 8x16GB UDIMM
- Phanteks Enthoo Pro II Server Edition
- FSP 1200W
- 1TB NVMe
- Noctua TR4 cooler
- 6 case fans
- budget mechanical keyboard
- G102 mouse
- used 24-inch monitor

If RAM costs Rp8m and monitor Rp1.45m, baseline rises to about **Rp26.265m**.

### Safer 1600W configuration
Replacing FSP 1200W with Corsair AX1600i:
- low estimate: **Rp28.801m**
- higher RAM/monitor estimate: **Rp31.151m**

## 8. Shared procurement sheet

Google Sheets:
https://docs.google.com/spreadsheets/d/1Xfl4xU2JY4I9O01GhaXXIu7XEX1EHRK4ceStVMH275Y/edit

Current tabs include:
- MASTER
- ANPR_COMPARE
- PTZ_LOCAL
- HW_SELECTED
- CPU_RAM
- MOBO_CASE_PSU
- STORAGE_IO
- BUDGET

## Next procurement locks

Before buying:
1. Confirm physical condition and pin/socket health of used 1950X/X399 board.
2. Lock exact GPU models and TDP/power limits.
3. Decide PSU 1200W vs 1600W after GPU power budget.
4. Buy RAM only after confirming UDIMM and exact part numbers.
5. For 2x32GB RAM experiments, require a return window and perform MemTest before deployment.


## Interactive HTML report

Interactive standalone report:
https://github.com/adith92/GardaWEB/blob/main/docs/project-garda/GARDA_HARDWARE_REPORT_2026-10-07.html

Path:
`docs/project-garda/GARDA_HARDWARE_REPORT_2026-10-07.html`

Features:
- selected-build dashboard
- compatibility guard
- searchable/filterable alternatives
- interactive budget calculator
- persistent procurement/burn-in checklist
- links to Shopee and the shared Google Sheet


## 9. Report UI update

The interactive HTML hardware report was updated to a **bright/light theme** for easier viewing and sharing.

Current RAM display policy:
- Preferred: **4 x 32 GB DDR4 UDIMM**, only after compatibility proof.
- Safe fallback: **8 x 16 GB DDR4-2666 UDIMM**, generally easier to source used and safer for this X399 generation.


## 10. 4x32GB compatibility verdict

**Verdict: DO NOT BUY 4x32GB for X399 AORUS PRO + Threadripper 1950X as a planned configuration.**

Official and vendor compatibility evidence converges on 16GB-per-module as the supported path for this board. A 4x32GB configuration may work only as an undocumented edge case on some combinations, but it is not strong enough evidence for GARDA procurement. The procurement baseline is therefore restored to **8x16GB DDR4-2666 UDIMM**.
