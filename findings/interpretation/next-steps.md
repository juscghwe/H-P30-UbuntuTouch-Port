# Next steps and unresolved decisions

## Current boundary

The bootloader is locked. There is no tested custom boot image, selected complete kernel source revision, validated build toolchain or confirmed full downgrade/unlock sequence. Hardware inventory can proceed from stock Android while charging; do not interrupt an update/rollback if one is already in progress.

## Unlock feasibility

1. Retain the current sanitized firmware/configuration evidence before changing versions.
2. Determine a model- and customization-compatible downgrade/unlock sequence. E04 proves only that HiSuite offers EMUI 10.0.0.562(C431E15R2P7). A subsequent offer for EMUI 9.1 remains unknown.
3. The PotatoNV project's alternatives documentation lists Kirin-Tool for Kirin 710 and states EMUI 9.1-or-earlier support. PotatoNV itself excludes Kirin 710. The original Kirin-Tool website returned HTTP 403; exact MAR-LX1A firmware compatibility was not verified.
4. Boot-ROM/test-point research exists for a related Kirin 710 phone. It is not a validated P30 Lite procedure. Do not treat matching SoC alone as authorization to flash another device's bootloader or partition images.
5. If a rollback is performed, record its result and repeat selected firmware/kernel identification. Preserve matching stock recovery/restore materials before custom flashing.

## Source and peripheral identification

- Match E08 against complete Huawei/community kernel sources, including vendor driver directories, board device trees and build dependencies. Search by board/kernel/driver details, not model marketing name alone.
- Determine the exact active touch controller and panel through the device tree, readable vendor identification attributes, or matching stock firmware. `huawei,ts_kit` is currently the observed input interface.
- Determine the active Hi110x connectivity variant, firmware files and initialization services. Compare the related Mate 20 Lite research without assuming identical hardware/partitions.
- Preserve the matching vendor HAL/service configuration needed for graphics, connectivity, permissions and firmware loading. Review any additional captures for personal information before commit.

## Build and bring-up milestones

| Milestone | Evidence needed | Current status |
| --- | --- | --- |
| Choose source/toolchain | Sources contain required board/drivers and can reproduce a compatible kernel | Not done |
| Build adapted kernel/image | Reproducible build and verified device-specific image layout | Not done |
| Boot/debug access | Kernel boot and working USB debug shell on actual phone | Not done |
| Ubuntu Touch/Halium starts | Mounts, services, container and root filesystem function | Not done |
| GUI/touch | Accelerated Lomiri display and working touchscreen | Not done |
| Wi-Fi | Connect, DHCP, DNS and internet/LAN access; settings integration | Not done |
| Home-device reliability | Charging, thermal behavior, reboot, reconnect and screen sleep/wake verified | Not done |
| Later optional hardware | Audio/Bluetooth/cameras/cellular as needed | Deferred |

A Wi-Fi-only goal avoids initial telephony/VoLTE work but does not eliminate graphics, power, device permissions or connectivity integration. SIM functionality should be a separately evaluated later milestone.
