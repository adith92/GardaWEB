# GARDA Hardware Plan — Threadripper X399 Baseline

Date: 2026-10-06
Status: Selected direction / procurement shortlist

## Decision summary

For the first production-capable GARDA build, use an AMD Ryzen Threadripper + X399 + DDR4 workstation platform instead of AMD EPYC.

Reason: GARDA needs a practical low-cost used workstation platform with 4 GPU capability, 128 GB DDR4, multiple internal SATA HDDs, NVMe storage, Linux/Proxmox compatibility, and later Windows VM GPU passthrough. EPYC remains technically strong but is not required for the current phase and would complicate motherboard/chassis procurement.

This hardware baseline supersedes the older Dell R630 concept for current procurement planning. The existing software/architecture PRD remains valid unless specifically revised.

## GARDA workload that this machine must run

- Proxmox VE or Linux/Ubuntu host
- GARDA web/API services
- RTSP + ONVIF camera ingestion
- MediaMTX/go2rtc/FFmpeg-class streaming components
- Continuous CCTV recording independent of AI processing
- PostgreSQL + vector/metadata workloads
- Object/person/vehicle detection
- Face detection and face recognition
- License-plate detection and OCR/ANPR
- Multi-camera live view and playback
- PTZ control
- Event processing, alerts, audit logs, storage health
- Optional Windows VM with one dedicated GPU later

## CPU shortlist

### Preferred value: AMD Ryzen Threadripper 1950X

- Socket: sTR4 / TR4
- Chipset: X399
- 16 cores / 32 threads
- Base 3.4 GHz, boost up to 4.0 GHz
- TDP 180 W
- Quad-channel DDR4
- 64 PCIe 3.0 lanes on Threadripper 1000 platform
- Recommended minimum CPU for GARDA X399 build

Reason: considerably better fit than 1900X for simultaneous NVR, database, FFmpeg, virtualization, and AI orchestration while GPUs perform the heavy inference work.

### Cheapest absolute X399 entry: Threadripper 1900X

- 8 cores / 16 threads
- 64 PCIe lanes
- Quad-channel DDR4
- 180 W

Not recommended as the main GARDA purchase unless budget is extremely constrained. It preserves the useful PCIe topology but halves CPU core count versus 1950X.

### Optional upgrade: Threadripper 2950X

- 16 cores / 32 threads
- 2nd generation Threadripper
- 180 W
- Compatible with X399 boards when BIOS support is present

Buy only if a genuinely good used price appears. New-old-stock pricing is currently poor compared with 1950X value.

## Motherboard shortlist

### Rank 1 — Gigabyte X399 AORUS PRO

Current preferred board.

- Socket TR4 / AMD X399
- Supports 1st and 2nd gen Threadripper
- 8 x DDR4 DIMM
- Maximum officially listed memory: 128 GB
- Quad-channel DDR4
- ECC unbuffered and non-ECC unbuffered DDR4 support
- GPU slots:
  - 2 x PCIe 3.0 x16 electrical
  - 2 x PCIe 3.0 x8 electrical
  - additional PCIe 2.0 x4 physical x16 slot
- 4-way graphics support
- 8 x SATA 6 Gb/s
- 3 x M.2
- ATX form factor

GARDA verdict: best current price/spec fit for 4 GPU + 128 GB + 6 internal HDD.

### Rank 2 — MSI X399 SLI PLUS

- Socket TR4 / X399
- Supports 1st and 2nd gen Threadripper
- 8 x DDR4 DIMM
- Up to 128 GB officially listed in detailed specification
- Quad-channel DDR4
- ECC UDIMM support
- 4 GPU slots: 2 x PCIe 3.0 x16 + 2 x PCIe 3.0 x8
- 8 x SATA 6 Gb/s
- 3 x M.2
- Additional motherboard PCIe power connector
- ATX

GARDA verdict: excellent electrically for multi-GPU, but current local pricing is less attractive than X399 AORUS PRO.

### Rank 3 — ASRock X399 Taichi

- 8 x DDR4 DIMM
- Up to 128 GB
- Quad-channel DDR4
- ECC/non-ECC unbuffered DDR4
- 4 x PCIe 3.0 x16 physical
- Four-GPU topology: x16 / x8 / x16 / x8
- 8 x SATA
- 3 x Ultra M.2
- Dual Intel Gigabit LAN
- ATX

GARDA verdict: technically excellent; buy if a good used local unit appears.

### Fallback — ASUS X399 ROG Zenith Extreme / Prime X399-A

Acceptable when used pricing is competitive. Do not pay a premium just for gaming features.

## RAM baseline

Target: 128 GB DDR4.

Recommended low-cost configuration:

- 8 x 16 GB DDR4-2666 UDIMM desktop memory
- Prefer identical Samsung / SK Hynix / Micron modules where possible
- Run quad-channel with balanced population across memory channels

Important compatibility rule:

- DO NOT buy cheap server DDR4 RDIMM / Registered ECC just because it is inexpensive.
- X399 boards in this shortlist support unbuffered DIMMs. ECC is acceptable only when it is ECC UDIMM and the board/QVL supports it.
- Standard non-ECC DDR4 UDIMM is the easiest used-market option.

## GPU design

Target: up to 4 NVIDIA GPUs.

X399 is appropriate because Threadripper exposes enough PCIe connectivity for four GPUs. The recommended boards expose four high-bandwidth PCIe 3.0 GPU slots.

Important physical constraint:

- Four modern 2.5-slot or 3-slot GPUs will NOT fit directly next to each other on a normal ATX layout.
- For direct motherboard mounting, prefer true 2-slot/blower-style cards and a chassis with at least 8 expansion-slot positions.
- Otherwise use high-quality PCIe x16 riser/extension mounting and design airflow around the GPUs.

For GARDA AI inference, PCIe 3.0 x8 is acceptable for secondary GPUs because most inference traffic remains in GPU VRAM after models/frames are transferred.

Virtualization note:

- One consumer GPU should normally be dedicated either to Linux GARDA workloads or passed through to a Windows VM.
- Do not plan on one consumer GPU being simultaneously dedicated to both guests.
- Example future allocation: GPU 1-3 = GARDA AI, GPU 4 = Windows VM.

## Internal storage baseline

Initial requirement: 6 x 4 TB SATA HDD.

- Raw capacity: 24 TB decimal
- Motherboard requirement: 6 SATA ports minimum; preferred X399 boards provide 8 SATA ports.
- No additional HBA is required for the initial six-drive build.
- Keep remaining PCIe resources focused on GPUs.

Recommended layout:

- NVMe 1: Proxmox/Linux OS + applications
- NVMe 2: database / metadata / cache / thumbnails
- 6 x 4 TB SATA HDD: CCTV recording pool

Recommended resilient CCTV pool:

- ZFS RAIDZ2 for 6 HDD where footage retention and drive-failure tolerance matter.
- Approximate parity layout: 24 TB raw -> ~16 TB decimal before filesystem/reservation overhead (about 14.55 TiB).
- Two-drive failure tolerance.

Alternative RAID10 offers simpler performance behavior but only ~12 TB decimal usable from 6 x 4 TB.

External JBOD / large HDD enclosure is deferred to the next procurement phase.

## PSU strategy

For only six HDDs, a separate SATA PSU is not required.

Preferred approach:

- Use one high-quality large PSU when total GPU power allows it.
- For a future 4 x RTX 3060-class configuration, target a quality 1200-1600 W PSU depending on the exact GPU models, power limits, CPU, fans, and accessories.
- 1600 W gives the cleanest headroom for the 1950X + four mid-power GPUs + six HDDs.

If dual PSU becomes necessary for higher-power GPUs:

- Use a proper synchronized dual-PSU controller / Add2PSU-class solution.
- Do not split the power of one device unpredictably across two independent PSUs.
- If GPUs use powered risers, power each GPU and its riser from the same PSU.
- HDD PSU must start synchronously with the motherboard so drives are available during boot.

## HDD power and SATA

Six 3.5-inch HDDs are easy to support electrically with a quality workstation PSU, but plan for spin-up current.

Use:

- proper native SATA power leads where possible
- quality powered backplane only if needed
- avoid cheap molded SATA-to-Molex power adapters
- active airflow across all HDDs

## Chassis requirement

Chassis will be purchased new.

Minimum requirements:

- ATX / E-ATX-compatible full tower or rack chassis
- at least 8 rear expansion-slot positions if four dual-slot GPUs are mounted directly
- six or more 3.5-inch HDD bays
- strong front-to-back airflow
- room for TR4 cooling
- room for large PSU / possible future dual-PSU arrangement

Do not select the chassis only by appearance. GPU thickness and HDD bay layout must be verified first.

## CPU cooling

Threadripper 1950X is a 180 W CPU and needs a TR4-specific cooler with good cold-plate coverage.

Prefer:

- large TR4/SP3 air cooler for simplicity and 24/7 reliability, or
- quality AIO specifically suitable for TR4 heat-spreader coverage.

## Current procurement priority

1. AMD Threadripper 1950X used
2. Gigabyte X399 AORUS PRO used / tested
3. 8 x 16 GB DDR4-2666 UDIMM used, preferably matched
4. TR4 cooler
5. New high-airflow chassis with 8+ expansion positions and 6+ HDD bays
6. NVMe OS/database drives
7. 6 x 4 TB CCTV HDD
8. PSU sized after exact four-GPU model is locked
9. GPU procurement

## Current decision

Recommended baseline:

- CPU: Ryzen Threadripper 1950X
- Motherboard: Gigabyte X399 AORUS PRO
- RAM: 128 GB = 8 x 16 GB DDR4-2666 UDIMM
- GPU: 4-GPU capable, exact NVIDIA model pending
- Storage: 2 x NVMe + 6 x 4 TB SATA HDD
- CCTV pool: ZFS RAIDZ2 recommended
- OS: Proxmox VE or Linux host with Ubuntu GARDA workload
- Windows: optional dedicated GPU passthrough VM later
- HDD expansion: external JBOD/storage chassis deferred to later phase

## Items still to lock

- exact GPU model and quantity for phase 1
- chassis model
- PSU model and wattage
- TR4 cooler
- NVMe sizes
- HDD model/health standard
- whether to start with Proxmox or Ubuntu bare metal
- exact retention target by number of cameras and bitrate
