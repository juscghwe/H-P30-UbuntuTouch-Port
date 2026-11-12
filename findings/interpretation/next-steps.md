# Next steps and unresolved decisions

## Current boundary

The bootloader is locked. The documented source/toolchain pair produces offline research images, including a stock-derived Halium configuration, but there is no device-validated kernel, boot package or software-only persistent-unlock sequence. Hardware inventory remains owner-operated from stock Android.

## Unlock feasibility

**2026-11-12 update:** the owner requests software-only research. No verified end-to-end procedure for the current .262 build has been found. Read [the unlock feasibility assessment](unlock-feasibility.md) before any downgrade or tool purchase. HCU's own manual confirms an Android-9 prerequisite for its documented unlock; this does not prove that our offered .562 rollback reaches that state.

1. Retain the current sanitized firmware/configuration evidence before changing versions.
2. Determine a model- and customization-compatible downgrade/unlock sequence. E04 proves only that HiSuite offers EMUI 10.0.0.562(C431E15R2P7). A subsequent offer for EMUI 9.1 remains unknown.
3. The PotatoNV project's alternatives documentation lists Kirin-Tool for Kirin 710 and states EMUI 9.1-or-earlier support. PotatoNV itself excludes Kirin 710. The original Kirin-Tool website returned HTTP 403; exact MAR-LX1A firmware compatibility was not verified.
4. Boot-ROM/test-point research exists for a related Kirin 710 phone. It is not a validated P30 Lite procedure. Do not treat matching SoC alone as authorization to flash another device's bootloader or partition images.
5. If a rollback is performed, record its result and repeat selected firmware/kernel identification. Preserve matching stock recovery/restore materials before custom flashing.

## Source and peripheral identification

- Preserve the pinned [4.14.116 baseline build](baseline-build.md), configuration fragments and demonstrated repairs. Native compilation passes; full-LTO/CFI resource behavior, source gaps, generated assembly and remaining warnings need resolution before selecting a device build base.
- Preserve the Synaptics TCM path indicated by the `MARI69110` runtime identifier and matching firmware filename (E09). Identify exact silicon/panel only where it helps device-tree and driver matching; the family is already sufficiently narrowed to inspect the relevant driver.
- Determine the active Hi110x connectivity variant, firmware files and initialization services. Compare the related Mate 20 Lite research without assuming identical hardware/partitions.
- Preserve the matching vendor HAL/service configuration needed for graphics, connectivity, permissions and firmware loading. Review any additional captures for personal information before commit.

## Build and bring-up milestones

| Milestone | Evidence needed | Current status |
| --- | --- | --- |
| Choose source/toolchain | Sources contain required board/drivers and can reproduce a compatible kernel | Closer candidate and documented toolchain identified; not validated |
| Compile research kernels | Complete AArch64 image/modules, exact config and artifact verification | Candidate and stock-derived Halium native images passed; LTO/CFI disabled |
| Build adapted boot image | Actual Marie board data and verified device-specific image layout | Blocked on stock DT/image metadata; no boot package |
| Boot/debug access | Kernel boot and working USB debug shell on actual phone | Not done |
| Ubuntu Touch/Halium starts | Mounts, services, container and root filesystem function | Not done |
| GUI/touch | Accelerated Lomiri display and working touchscreen | Not done |
| Wi-Fi | Connect, DHCP, DNS and internet/LAN access; settings integration | Not done |
| Home-device reliability | Charging, thermal behavior, reboot, reconnect and screen sleep/wake verified | Not done |
| Later optional hardware | Audio/Bluetooth/cameras/cellular as needed | Deferred |

A Wi-Fi-only goal avoids initial telephony/VoLTE work but does not eliminate graphics, power, device permissions or connectivity integration. SIM functionality should be a separately evaluated later milestone.

The [owner follow-up E10](../raw/2026-11-12/07-stock-layout-and-access.txt) supplies actual named image-partition targets and a stock touch-firmware hash, which differs from the recovery reference. DT traversal and connectivity status reads are denied; the `hisi` property does not identify the chip. The four underlying kernel/ramdisk/dts/dto block nodes are `root:root` mode `0600`, blocking ordinary ADB extraction. Preserve the readable stock touch firmware privately and look for matching original update materials already obtained through HiSuite or another legitimate Huawei distribution. Inspect original headers before creating a device-specific packaging recipe; no partition constants from another handset are accepted.
