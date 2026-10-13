# PROJECT GARDA — Conversation Log Addendum

Date: 2026-10-13

This addendum captures GARDA architecture decisions made after the original 2026-10-02 conversation log.

## 1. Server virtualization direction

The architecture evolved from Ubuntu Server bare metal to **Proxmox VE as the preferred physical host** when GARDA Linux services and a Windows environment must coexist on the same physical server.

Planned structure:

- Proxmox VE host
- Ubuntu/Linux GARDA VM or guest
- Windows VM for Windows-only and interactive desktop workloads

Linux remains the primary environment for GARDA services such as go2rtc, FFmpeg, FastAPI, PostgreSQL, Docker, YOLO, face recognition, LPR/OCR, event processing, and recording orchestration.

## 2. Windows use case

Windows is not merely an admin VM.

The intended Windows VM may be used by remote users for:

- gaming
- photo editing
- video editing
- rendering
- general Windows software

Recommended remote access distinction:

- RDP for administration and normal desktop workloads
- Sunshine + Moonlight or Parsec-class streaming for low-latency gaming / GPU-heavy interactive sessions

## 3. Hardware direction

User confirmed the server direction as:

- AMD Threadripper
- 128 GB RAM
- target of 4 GPUs

The detailed X399 hardware plan in this repository currently documents Threadripper 1950X + Gigabyte X399 AORUS PRO as the value baseline, with exact GPU model still pending unless superseded later.

## 4. Four-GPU allocation model

A four-GPU design is supported conceptually.

Preferred operational modes:

### GARDA MAX
- GARDA Linux: 4 GPUs
- Windows: off / no passed-through GPU

### BALANCED
- GARDA Linux: 3 GPUs
- Windows: 1 GPU

### WINDOWS GAMING / EDITING
- GARDA Linux: 2 GPUs
- Windows: up to 2 GPUs, subject to actual application benefit and passthrough validation

## 5. Dynamic GPU switching limitation

Consumer GPUs should not be assumed to be shareable simultaneously between GARDA Linux and Windows.

A GPU can be reassigned automatically only through a controlled workflow:

1. stop/drain AI workers on that GPU
2. release/rebind the GPU
3. start/restart the target VM with passthrough
4. after use, shut down the Windows VM cleanly
5. return the GPU to Linux
6. restart GARDA AI workers

This is **mode switching**, not live hot-swap.

## 6. Proxmox/IOMMU requirements

Final motherboard/BIOS validation must include:

- IOMMU support
- usable IOMMU grouping
- four physical/electrical GPU slots
- sufficient lane allocation
- physical GPU spacing/riser plan
- PSU and cooling design

## 7. Important procurement distinction

The Threadripper/X399 machine is currently treated as the development/lab/value workstation architecture unless procurement documents are changed.

The formal PUSADA TNI KAK AI-server requirement remains a different production specification: Xeon/EPYC, minimum 128 GB ECC, NVIDIA enterprise CUDA-compatible GPU, NVMe OS RAID 1, redundant PSU, 10GbE, rail kit, monitoring, and onsite warranty.

Do not silently substitute the Threadripper lab build for the contractual production AI server.
