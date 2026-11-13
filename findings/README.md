# Findings index

## Scope and status

Device evidence dates: **2026-11-11–13**; source research: **2026-11-12**; firmware/unlock assessment update: **2026-11-13**, Europe/Berlin. Device evidence was supplied by the owner as command output and selected transcriptions. Exact acquisition times and the phone's clock have not been independently verified. Numeric file timestamps are not used to infer firmware state.

Target: Ubuntu Touch with display, touchscreen and Wi-Fi. Cellular support is deferred; charging, thermal behavior, sleep/wake and reconnect reliability are required milestones.

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
| — | [Capture provenance](raw/2026-11-11/provenance.json) | Acquisition, normalization and sanitation metadata |
| — | [SHA-256 inventory](raw/2026-11-11/SHA256SUMS) | Integrity hashes of the committed evidence and provenance |

## Unlock research update: 2026-11-12

- [Source observations and limited excerpts](raw/2026-11-12/01-research-sources.json) — external primary sources, not new device measurements.
- [Owner constraint: software-only](raw/2026-11-12/02-owner-constraint.txt).
- [Research evidence checksums](raw/2026-11-12/SHA256SUMS).
- [Unlock feasibility assessment](interpretation/unlock-feasibility.md) — vendor requirements, same-model reports, rejected shortcuts and remaining gaps.
- [Kernel config comparisons](raw/2026-11-12/04-kernel-source-comparison.json) — generated static comparisons with source pins and input hashes.
- [Selected upstream source observations](raw/2026-11-12/05-source-inspection.json).
- [Additional same-model downgrade report](raw/2026-11-12/06-downgrade-report.json) — selected public comments, including the correction of a cross-model success claim.
- [Firmware catalog and live Huawei manifest observations](raw/2026-11-12-firmware/01-catalog-and-manifests.json) — decoded external metadata, not device compatibility or downgrade approval.
- [Verified reference archive and image observations](raw/2026-11-12-firmware/02-reference-image-inspection.json) and [reference/config comparison](raw/2026-11-12-firmware/03-reference-config-comparison.json) — offline official-package inspection, distinct from current phone measurements.
- [Board-7800 reference overlay application](raw/2026-11-12-firmware/04-board-7800-overlay.json) — unique matching table ID and resolved offline properties; current handset DT bytes remain unavailable.
- [Reference vendor recovery](raw/2026-11-12-firmware/05-super-vendor-extraction.json), [file/init observations](raw/2026-11-12-firmware/06-vendor-files-and-init.json) and [driver binding/firmware-format audit](raw/2026-11-12-firmware/07-driver-binding-audit.json) — offline sparse/LP/EROFS inspection and source comparison; no vendor code executed.

## Interpretation and reproducibility

- [Device and hardware assessment](interpretation/device-and-hardware.md)
- [Kernel configuration assessment](interpretation/kernel-configuration.md)
- [Kernel source candidates and remaining validation](interpretation/kernel-source-candidates.md)
- [Executed Kconfig validation and baseline build](interpretation/baseline-build.md)
- [Peripheral source trace, board data and read-only checks](interpretation/peripheral-integration.md)
- [Official firmware acquisition and experimental HiSuite URL observer](interpretation/firmware-acquisition.md)
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
