# Technical checkpoints and corrections

## Stock inventory: 2026-11-11

- Selected Settings and ADB captures establish MAR-LX1A/HWMAR, Kirin 710, Android 10/VNDK 29 under EMUI 12 and kernel 4.14.116. Settings and ADB firmware identifiers differ; both are retained.
- Fastboot initially waited for a device, then enumerated successfully. The precise Windows driver cause is unknown. `oem get-bootinfo` reports locked; FRP was not captured.
- HiSuite offered 10.0.0.562(C431E15R2P7); no completed rollback was reported. An Android-10 offer does not establish an Android-9 downgrade or persistent-unlock route.
- The first graphics probe failed because of nested-shell quoting. Filtering on Windows produced the Mali-G51/r18p0 renderer. Input filtering initially returned paths and later overmatched UI records; only the physical inventory is retained.
- The decompressed stock configuration is preserved with its original payload hash. Driver configuration and library presence do not establish active peripheral variants or Ubuntu Touch functionality.
- Halium 10 is a provisional candidate for the observed Android-10 vendor base. Retained vendor firmware and compatibility determine the approach.

## Unlock assessment: 2026-11-12

- HCU documents Android 9 for persistent unlock. Same-model reports include transient service-tool success followed by locked normal fastboot.
- The closer C431 modification report uses physical test points and is outside the software-only scope.
- No complete software-only chain for 12.0.0.262(C431E3R2P2) is verified. No downgrade, unlock or custom boot is demonstrated. See [unlock assessment](unlock-feasibility.md).

## Source and touch assessment: 2026-11-12

- `MARI69110` and the matching `marie_synaptics_tcm_MARI69110.img` filename indicate Synaptics TCM; exact silicon and panel supplier remain unknown.
- Static configuration comparison identifies the pinned Enjoy 10 4.14.116 source as closer than the older Kirin710 candidate. Only selected source files and two defconfigs were retrieved for that comparison; no complete source checkout or compile was performed.
- The empty Wi-Fi property search suppressed errors and cannot identify the chip or prove the property absent.
- HiSuite-Proxy issue #94 records P30 Lite Android-9 downgrade failures. Its later success report concerns a P20 Pro, not a P30 Lite.

## Executed source/build validation: 2026-11-12

- The complete pinned Enjoy 10 tree was reconstructed and hash-verified, then built with its documented Clang r353983c and Android GCC 4.9 tools. Candidate and stock-derived Kconfig parsing pass; Huawei's `-source` syntax needs no repair.
- Native candidate and Halium-probe images/modules compile with LTO/CFI disabled after full-LTO memory failures. Embedded configs and image integrity pass; four staged Halium modules pass development-certificate signature verification. No binary is offered as flash-ready.
- Small block teardown, dummy sidecar and display/clock lifetime repairs pass incremental builds. Thirty section mismatches, duplicate Wi-Fi exports, unversioned assembly exports and missing stock/Marie source data remain documented. See [build evidence and limits](baseline-build.md).
