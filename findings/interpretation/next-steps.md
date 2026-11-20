# Next steps and unresolved decisions

## Current boundary

[The 2026-11-20 checkpoint](unlock-checkpoint.md) demonstrates ordinary fastboot unlocked after normal stock EMUI 9.1 startup, following hardware entry, HCU Repair on Android 10 and an AUP factory-fastboot Android-9 flash. No custom kernel, recovery or Ubuntu Touch boot has been demonstrated. Device binary backups remain private.

## Immediate implementation steps

1. Capture the retained runtime Android/vendor SDK, VNDK, kernel release, component versions and a fresh `/proc/config.gz`. Settings EMUI 9.1 and the Android-9 GPT do not substitute for those measurements.
2. Inspect the matching Android-9 stock boot/DT/vendor inputs and select the source/configuration and provisional Halium version against that base. Prior Enjoy-10 4.14.116 research builds target the earlier evidence; do not flash them as a validated Android-9 kernel.
3. Establish measured boot packaging and an early debug path before a custom boot attempt. Retain original stock boot images, primary-table snapshots and private calibration/identity backups. Restoring them has not been demonstrated.
4. Keep ordinary-fastboot persistence separate from authorization of every protected partition. Preserve the current retained firmware; later EMUI upgrades/relocks are not validated.

The earlier [DLOAD failure](android-utility-usb-upgrade.md) remains a separate failed workflow. The later FB result does not repair that client path or establish software-only entry. See the [checkpoint](unlock-checkpoint.md) for resize errors, actual GPT differences and the successful runtime acceptance check.

## Source and peripheral identification

- Preserve the pinned [4.14.116 baseline build](baseline-build.md), configuration fragments and demonstrated repairs. Native compilation passes; full-LTO/CFI resource behavior, source gaps, generated assembly and remaining warnings need resolution before selecting a device build base.
- Preserve the Synaptics TCM path indicated by the `MARI69110` runtime identifier and matching firmware filename (E09). Identify exact silicon/panel only where it helps device-tree and driver matching; the family is already sufficiently narrowed to inspect the relevant driver.
- Determine the active Hi110x connectivity variant, firmware files and initialization services. Compare the related Mate 20 Lite research without assuming identical hardware/partitions.
- Preserve the matching vendor HAL/service configuration needed for graphics, connectivity, permissions and firmware loading. Review any additional captures for personal information before commit.

## Build and bring-up milestones

| Milestone | Evidence needed | Current status |
| --- | --- | --- |
| Persistent unlock | Normal Android startup followed by ordinary fastboot without a service loader | Observed unlocked on retained EMUI 9.1; future firmware transitions untested |
| Choose source/toolchain | Sources contain required board/drivers and can reproduce a compatible kernel | Closer candidate and documented toolchain identified; not validated |
| Compile research kernels | Complete AArch64 image/modules, exact config and artifact verification | Candidate and stock-derived Halium native images passed; LTO/CFI disabled |
| Build adapted boot image | Correct active board/overlay and verified device-specific image layout | Board 7800 matches reference overlay 186; offline application passes; current-image equality unresolved; no boot package |
| Boot/debug access | Kernel boot and working USB debug shell on actual phone | Not done |
| Ubuntu Touch/Halium starts | Mounts, services, container and root filesystem function | Not done |
| GUI/touch | Accelerated Lomiri display and working touchscreen | Not done |
| Wi-Fi | Connect, DHCP, DNS and internet/LAN access; settings integration | Not done |
| Home-device reliability | Charging, thermal behavior, reboot, reconnect and screen sleep/wake verified | Not done |
| Later optional hardware | Audio/Bluetooth/cameras/cellular as needed | Deferred |

A Wi-Fi-only goal avoids initial telephony/VoLTE work but does not eliminate graphics, power, device permissions or connectivity integration. SIM functionality should be a separately evaluated later milestone.

The [owner follow-up E10](../raw/2026-11-12/07-stock-layout-and-access.txt) supplies actual named image-partition targets and a stock touch-firmware hash, which differs from the recovery reference. DT traversal and connectivity status reads are denied; the `hisi` property does not identify the chip. The four underlying kernel/ramdisk/dts/dto block nodes are `root:root` mode `0600`, blocking ordinary ADB extraction. Preserve the readable stock touch firmware privately and look for matching original update materials already obtained through HiSuite or another legitimate Huawei distribution. Inspect original headers before creating a device-specific packaging recipe; no partition constants from another handset are accepted.

The [firmware acquisition assessment](firmware-acquisition.md) records the log
search limit and an experimental HiSuite observer that is not selected. Direct
catalog decoding instead located live Huawei manifests; the .275 base archive
has been downloaded and hash-verified offline. Board ID 7800 now matches reference
overlay 186. The [offline driver/vendor audit](vendor-integration.md) maps its
bindings to candidate source readers and recovers touch firmware identical to
E10. Next implement the host/container visibility and initialization-order
contract as part of device adaptation; no vendor helper or firmware has been
executed. Do not repeat denied INI/DT reads or escalate access for this lookup.
Keep the older reference configuration separate from current stock and do not
start an update solely to obtain files.
