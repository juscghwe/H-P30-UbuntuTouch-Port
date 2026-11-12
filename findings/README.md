# Findings index

## Scope and status

Device evidence dates: **2026-11-11–12**; source/unlock research update: **2026-11-12**, Europe/Berlin. Device evidence was supplied by the owner as command output and selected transcriptions. Exact acquisition times and the phone's clock have not been independently verified. Numeric file timestamps are not used to infer firmware state.

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

## Interpretation and reproducibility

- [Device and hardware assessment](interpretation/device-and-hardware.md)
- [Kernel configuration assessment](interpretation/kernel-configuration.md)
- [Kernel source candidates and remaining validation](interpretation/kernel-source-candidates.md)
- [Technical checkpoints and corrections](interpretation/technical-history.md)
- [Collection commands and limitations](interpretation/collection-methods.md)
- [Unlock and porting plan](interpretation/next-steps.md)
- [References and their limitations](interpretation/references.md)
- [Privacy review](interpretation/privacy-review.md)

## Evidence rules

Raw data contains supplied observations, not a transcript of all chat text. Missing evidence and failed commands are retained as such. A driver being compiled or a library being installed is not evidence that a particular chip is active. The original diagnostic attachments remain outside the repository; only reviewed extracts are committed.

The available snapshot describes the stock Android 10/EMUI 12 environment reported by the owner. Repeat firmware identification and capture the kernel configuration again after any downgrade; do not silently combine outputs from different firmware bases.
