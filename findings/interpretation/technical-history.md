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
- Small block teardown, dummy sidecar, display/clock and calibration/timekeeper lifetime repairs pass incremental builds. Twenty-eight section mismatches, duplicate Wi-Fi exports, unversioned assembly exports and missing stock/Marie source data remain documented. See [build evidence and limits](baseline-build.md).

## Official reference firmware: 2026-11-12

- Independent static decoding of FirmFinder data located live Huawei manifests
  for MAR-L21A/C431 .275 and .562. The .275 base archive passes the published
  manifest SHA-256; its UPDATE.APP passes ZIP CRC and 46 record-bound checks.
- Reference kernel, ramdisk and DT image headers are now inspected. All seven
  selected reference GPT entry numbers agree with E10. One base FDT and 366
  compressed overlay entries pass gzip/FDT-header validation; the base and one
  example overlay also decompile with DTC.
- The reference 4.14.116 kernel embeds an older, different config. No original
  stock bytes, preferred source/toolchain or runtime hardware conclusion changed.
  See [acquisition evidence and limits](firmware-acquisition.md).

## Hardware-assisted Android-9/unlock result: 2026-11-20

- Physical entry enumerates `12d1:3609`; HCU Kirin710_P1_V2 communicates on `.562`. HCU Repair reports success, but ordinary fastboot remains locked after Android-10 startup.
- AUP KIRIN710 reaches factory fastboot with a second physical entry and battery reconnection at DDR `[4]`. Its GPT reader is unsupported; Phoenix exports actual partition data instead. The GUI's older map disagrees with the original Android-10 GPT.
- Android-9 FW Update (FB) has CUST/PRELOAD size-setting failures. Post-flash primary checksums pass; all named partition ranges match the pinned Android-9 base except userdata extended to actual capacity. The complete image-write log and restoration remain unverified.
- After the data-format prompt, the owner reports normal EMUI 9.1 startup and unlocked ordinary fastboot without a loader. No second HCU Repair on Android 9 is reported. See [evidence and limits](unlock-checkpoint.md).
- Prior compiled kernels/vendor evidence remain Android-10 research inputs. Recapture the retained vendor API/VNDK and kernel/configuration before selecting a current device build.
