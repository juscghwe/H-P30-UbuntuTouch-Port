# Findings index

## Scope and status

Device evidence dates: **2026-11-11–20**; source research: **2026-11-12–17**; firmware/unlock assessment update: **2026-11-20**, Europe/Berlin. Device evidence was supplied by the owner as command output and selected transcriptions. Exact acquisition times and the phone's clock have not been independently verified. Numeric file timestamps are not used to infer firmware state.

Target: Ubuntu Touch with display, touchscreen and Wi-Fi. Cellular support is deferred; charging, thermal behavior, sleep/wake and reconnect reliability are required milestones.

**Latest checkpoint:** [normal EMUI 9.1 startup and persistent ordinary-fastboot unlock](interpretation/unlock-checkpoint.md). The earlier Android-10 builds and vendor evidence remain historical inputs; current runtime SDK/VNDK and kernel/configuration are pending.

## Sanitized raw evidence

| ID | File | Origin |
| --- | --- | --- |
| E01 | [Owner-reported specifications](raw/2026-11-11/01-owner-reported-device.txt) | Manually transcribed from Settings by owner |
| E02 | [ADB properties](raw/2026-11-11/02-adb-properties.txt) | Owner-pasted property queries and `uname` |
| E03 | [USB and bootloader checks](raw/2026-11-11/03-usb-and-bootloader.txt) | Separate owner-reported observations, explicitly delimited |
| E04 | [HiSuite rollback offer](raw/2026-11-11/04-hisuite-rollback-offer.txt) | Text transcribed from owner-provided screenshot |
| E05 | [First hardware probe](raw/2026-11-11/05-first-hardware-probe.txt) | Pasted diagnostic attachment; includes unsuccessful checks |
| E06 | [Graphics and input paths](raw/2026-11-11/06-graphics-and-input-paths.txt) | Owner-pasted follow-up command output |
| E07 | [Input device names](raw/2026-11-11/07-input-device-names.txt) | Latest pasted attachment; unrelated UI/window sections omitted |
| E08 | [Stock kernel configuration](raw/2026-11-11/08-stock-kernel.config) | Decompressed owner-uploaded `/proc/config.gz` |
| E09 | [Peripheral follow-up](raw/2026-11-12/03-peripheral-followup.txt) | Owner-pasted touch identifier, firmware filename and empty Wi-Fi property lookup |
| E10 | [Stock image names, access checks and firmware hash](raw/2026-11-12/07-stock-layout-and-access.txt) | Separate owner-pasted ADB replies; partition symlinks, stock touch hash and permission failures |
| E11 | [Board property and vendor INI access](raw/2026-11-12/09-board-id-and-ini-access.txt) | Owner-pasted board ID 7800, empty boot-board property and denied INI metadata reads |
| E12 | [Connectivity selector follow-up](raw/2026-11-12/10-connectivity-selector-report.txt) | Owner reports both selected boot-property values empty; no full terminal capture |
| E13 | [Firmware identity and HiSuite offer](raw/2026-11-13/01-firmware-and-hisuite-offer.txt) | ADB retains Android-10/VNDK-29/base-.275 values; owner later confirms Settings EMUI 10.0.0 / .562; no Android-9 offer |
| E14 | [Post-rollback kernel configuration](raw/2026-11-13/04-emui10-stock-kernel.config) | Exact decompressed owner upload after Settings EMUI 10/.562 confirmation; [hashes and generated comparisons](raw/2026-11-13/05-emui10-config-provenance-and-comparison.json) |
| E15 | [Post-rollback fastboot state](raw/2026-11-13/06-fastboot-state.txt) | Bootloader reports locked; historical repeated-U unlock request rejected as invalid command; FRP state not shown |
| — | [CUST capture validation](raw/2026-11-13/02-capture-validation.json) | Generated offline ZIP/metadata checks and selected index fields; PRELOAD transfer blocked by size limit |
| — | [Android-9 C431 package availability](raw/2026-11-13/08-android9-package-availability.json) | Decoded catalog rows, live Huawei manifests/range probes and full CUST hash/CRC/version checks; not downgrade authorization |
| — | [Android Utility static readiness](raw/2026-11-17/01-android-utility-static-readiness.json) | Publisher-linked archive hash/CRC, main executable manifest and selected static UI strings; no execution or phone test |
| E16 | [Owner USB Upgrade mode test](raw/2026-11-17/02-owner-usb-upgrade-mode-test.json) | DBAdapter detection, mode-switch report, 5% screen, blocked ADB query and automatic return to Android; no firmware transfer |
| — | [Complete firmware-package checks](raw/2026-11-17/03-firmware-package-verification.json) | Six Huawei archive sizes/digests/ZIP CRCs and bounded APP inventories; no signature or device-acceptance test |
| — | [Android-9/10 GPT comparison](raw/2026-11-17/04-partition-layout-comparison.json) | Explicit primary eMMC template selection, CRCs and partition ranges; placeholder capacity fields retained |
| — | [Recovery USB validation paths](raw/2026-11-17/05-recovery-usb-validation.json) | Offline DLOAD updater extraction, selected wait/hash-check control flow and PC-helper checks; no firmware program executed |
| E17 | [Retained component versions](raw/2026-11-17/06-component-versions.txt) | Owner read-only component properties after the automatic return to Android |
| E18 | [Failed Android-9 DLOAD attempt](raw/2026-11-17/07-owner-dload-failure.json) | Selected owner log/screen observations; BASE_VER failure, contradictory success banner, CUST continuation and user termination |
| E19 | [Post-attempt boot and component state](raw/2026-11-17/08-post-attempt-state.txt) | Owner reports boot completion and unchanged component labels; native recovery-log metadata access denied |
| — | [AUP failure propagation](raw/2026-11-17/09-aup-failure-handling.json) | Selected static x86 branches explaining the success-looking banner after failure; not the native error cause |
| E20 | [Hardware entry, downgrade and unlock output](raw/2026-11-20/01-owner-unlock-evidence.txt) | Selected owner reports/tool output; ordinary fastboot unlocked after normal EMUI 9.1 startup |
| — | [Actual primary GPT comparison](raw/2026-11-20/02-primary-gpt-comparison.json) | Sanitized generated arrays/CRCs from private pre/post-flash dumps; no GUIDs or binary images |
| — | [Readback and flash checks](raw/2026-11-20/03-readback-and-flash-checks.json) | Owner export sizes, large-offset extraction hash check and failed resize-record payloads |
| — | [Capture provenance](raw/2026-11-11/provenance.json) | Acquisition, normalization and sanitation metadata |
| — | [SHA-256 inventory](raw/2026-11-11/SHA256SUMS) | Integrity hashes of the committed evidence and provenance |

## Unlock research update: 2026-11-12

- [Source observations and limited excerpts](raw/2026-11-12/01-research-sources.json) — external primary sources, not new device measurements.
- [Owner constraint: software-only](raw/2026-11-12/02-owner-constraint.txt).
- [Research evidence checksums](raw/2026-11-12/SHA256SUMS).
- [Unlock feasibility assessment](interpretation/unlock-feasibility.md) — vendor requirements, same-model reports, rejected shortcuts and remaining gaps.
- [Hardware testpoint assessment](interpretation/hardware-testpoint.md) — physical access, temporary versus persistent unlock, and [pinned loader comparisons](raw/2026-11-17/10-hardware-testpoint-research.json); superseded by the [owner-tested checkpoint](interpretation/unlock-checkpoint.md).
- [Kernel config comparisons](raw/2026-11-12/04-kernel-source-comparison.json) — generated static comparisons with source pins and input hashes.
- [Selected upstream source observations](raw/2026-11-12/05-source-inspection.json).
- [Additional same-model downgrade report](raw/2026-11-12/06-downgrade-report.json) — selected public comments, including the correction of a cross-model success claim.
- [Firmware catalog and live Huawei manifest observations](raw/2026-11-12-firmware/01-catalog-and-manifests.json) — decoded external metadata, not device compatibility or downgrade approval.
- [Verified reference archive and image observations](raw/2026-11-12-firmware/02-reference-image-inspection.json) and [reference/config comparison](raw/2026-11-12-firmware/03-reference-config-comparison.json) — offline official-package inspection, distinct from current phone measurements.
- [Board-7800 reference overlay application](raw/2026-11-12-firmware/04-board-7800-overlay.json) — unique matching table ID and resolved offline properties; current handset DT bytes remain unavailable.
- [Reference vendor recovery](raw/2026-11-12-firmware/05-super-vendor-extraction.json), [file/init observations](raw/2026-11-12-firmware/06-vendor-files-and-init.json) and [driver binding/firmware-format audit](raw/2026-11-12-firmware/07-driver-binding-audit.json) — offline sparse/LP/EROFS inspection and source comparison; no vendor code executed.

## Interpretation and reproducibility

- [Persistent-unlock checkpoint and retained-base boundary](interpretation/unlock-checkpoint.md)
- [Device and hardware assessment](interpretation/device-and-hardware.md)
- [Kernel configuration assessment](interpretation/kernel-configuration.md)
- [Kernel source candidates and remaining validation](interpretation/kernel-source-candidates.md)
- [Executed Kconfig validation and baseline build](interpretation/baseline-build.md)
- [Peripheral source trace, board data and read-only checks](interpretation/peripheral-integration.md)
- [Official firmware acquisition and experimental HiSuite URL observer](interpretation/firmware-acquisition.md)
- [Android Utility USB Upgrade readiness](interpretation/android-utility-usb-upgrade.md) — owner-observed mode entry, verified full reference archives and remaining partition/version constraints; not a validated downgrade recipe.
- [Board-7800 vendor, touchscreen and Wi-Fi integration inputs](interpretation/vendor-integration.md)
- [Provisional Halium approach and configuration probe](interpretation/halium-approach.md)
- [Technical checkpoints and corrections](interpretation/technical-history.md)
- [Collection commands and limitations](interpretation/collection-methods.md)
- [Unlock and porting plan](interpretation/next-steps.md)
- [References and their limitations](interpretation/references.md)
- [Privacy review](interpretation/privacy-review.md)

## Evidence rules

Raw data contains supplied observations, not a transcript of all chat text. Missing evidence and failed commands are retained as such. A driver being compiled or a library being installed is not evidence that a particular chip is active. The original diagnostic attachments remain outside the repository; only reviewed extracts are committed.

E01–E12 describe the earlier stock Android 10/EMUI 12 state. E13 confirms the later owner-reported EMUI 10.0.0 / .562 Settings state while ADB still reports the .275 base identifier. E14 supplies a distinct post-rollback kernel configuration. The retained E08 and research builds using it predate this rollback. Do not silently combine outputs from different firmware bases.

E20 records the subsequent hardware-assisted Android-9 layout migration and owner-reported EMUI 9.1 boot. Ordinary fastboot is now unlocked on that retained installation. E08/E14 and their research builds must not be relabeled as captures/builds of the new base.
