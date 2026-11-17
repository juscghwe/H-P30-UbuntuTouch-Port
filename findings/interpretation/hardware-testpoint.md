# Hardware testpoint assessment

Research date: **2026-11-17**. [Source and binary observations](../raw/2026-11-17/10-hardware-testpoint-research.json).
Hardware-route investigation is now in scope. No disassembly, testpoint connection
or factory-loader execution has been demonstrated on the target phone.

## What the testpoint changes

A hardware testpoint provides entry to the Kirin USB download path. It does not
itself remove the normal bootloader lock. Keep these results separate:

| Result | Required evidence |
| --- | --- |
| Download-mode entry | Correct USB enumeration; `12d1:3609` is used by the inspected Kirin 710 research client |
| Temporary factory fastboot | Compatible loader runs and answers selected queries; a tool's unlocked field is insufficient |
| Persistent unlock | Normal fastboot still reports unlocked after leaving the loader session and rebooting |
| Custom boot | Independently bootable, device-compatible custom image; not established by mode detection |

**Android 9 remains a prerequisite of HCU's documented persistent-unlock method,
including hardware entry.** It was not needed solely to obtain software testpoint
access. DC Phoenix separately documents a loader-based unlock lasting only until
restart. Neither statement proves that every possible hardware method requires
Android 9; no direct persistent-unlock method for this phone's `.562` firmware has
been verified.

## Closest model-specific route

[CatWithCode's report](https://catwithcode.moe/Blog/2026.08.06_P30_Lite_Root/P30_Lite_Root.html)
starts with MAR-LX1A, C431, 4 GB/128 GB and EMUI 12 `.251`. It uses hardware
testpoint and factory fastboot, then Android-9 firmware through **FW Update (FB)**,
then another loader session and an unlock operation. It later reports a GSI boot.
The firmware catalog IDs match the already verified Android-9 reference set.

This is a credible research lead, not a reproduced `.562` procedure. It uses a
**patched** Android Utility build with no verified artifact hash here. The linked
XDA procedure and post returned HTTP 502. The report also describes continued
loader use for protected partitions; it does not supply a complete independent
normal-fastboot persistence test. Do not equate its later GSI boot with proof that
every flashing operation became permanently authorized.

This **FB** route differs from the failed [DLOAD attempt](android-utility-usb-upgrade.md).
Its existence does not repair that failure or establish acceptance of an FB
downgrade on the target. Do not switch to FB in normal locked fastboot.

## Loader provenance narrowed

The publisher-linked AUP v200 archive contains `KIRIN/KIRIN710/boot0` through
`boot7`. Three files have exactly the same Git blob IDs as files at
[map220v/kirin710_bootrom_exploit, `f8998dd`](https://github.com/map220v/kirin710_bootrom_exploit/tree/f8998dda9352496074faa4d8fa0e7e024b167894):

| AUP member | Public research file | Bytes |
| --- | --- | ---: |
| `boot3` | `xloader-orig.img` | 147456 |
| `boot4` | `uce.img` | 40960 |
| `boot7` | `fastboot.img` | 4675584 |

The research project's patched `xloader.img` has a different blob ID from
`boot3`. Its script loads a patched xloader and decrypted fastboot into memory;
that is not evidence that AUP applies the same patches or sequence. Matching
three inputs identifies shared components, not the provenance of all eight files
or compatibility of the complete workflow.

The public project reports testing on **Honor 8X JSN-L21 / EMUI 9.1**. Its README
warns that the supplied bootloaders depend on EMUI-9 board data for display,
charging, fuel-gauge and vibrator operation. This is a loader-specific limitation,
not proof of a universal Android-9 requirement. No downloaded code or loader was
executed during this audit.

## Physical preparation and first checkpoint

[iDoc's P30 Lite repair guide](https://www.idoc.eu/guides/en/huawei/huawei-p30-lite/battery-replacement/838)
shows a glued glass back, a fingerprint flex attached to it, motherboard covers
and the battery-connector bracket. Accessing the board and disconnecting the
battery are separate from extracting the battery cell. Battery replacement is
optional and adds adhesive-removal work.

For an opening attempt, prepare a controlled heat source, suction cup, thin
plastic picks, plastic spudger, correctly fitting small Phillips driver, fine
tweezers, screw storage and replacement back-cover adhesive. The glass, flex and
battery are the main handling risks. Keep the phone off and USB disconnected
during opening; disconnect the battery as soon as safely accessible. Do not bend,
puncture or heat the cell directly. A repair shop can perform the opening without
being asked to flash or unlock the device.

The closest report includes a close-up of the testpoint beside a shield. Match
the actual board and connector layout to the photograph before selecting a pad;
the image alone does not establish the target board revision. No motherboard
removal or battery-cell extraction requirement has been established here.

The first future device checkpoint should be **board identification and USB
download-mode enumeration only**, with no flashing tool job active. Then establish
a compatible loader and readback/exit behavior. Before any downgrade, retain the
actual GPT and device-specific calibration/identity partitions privately if the
loader permits reading them, and verify that reads are complete. Catalog firmware
is not a backup of those partitions. The `.562` reference package is also not
byte-identical to the owner's earlier HiSuite capture, and restoration through
factory fastboot has not been demonstrated.

Do not start a second write while those gaps remain. Do not erase xloader as a
substitute for physical entry, copy another handset's identity partitions, or run
the later GSI/repartitioning steps as part of testpoint detection.
