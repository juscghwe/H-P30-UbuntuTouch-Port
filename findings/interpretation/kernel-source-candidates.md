# Kernel-source comparison

Initial static inspection on 2026-11-12. Comparisons use the stock 4.14.116 configuration, not a claim that either tree is the exact Huawei release for MAR-LX1A. Subsequent [executed validation](baseline-build.md) confirms Kconfig parsing and complete native kernel/module builds.

## Candidates

| Source and pinned commit | Kernel | Explicit config comparison against stock |
| --- | --- | --- |
| [yuioto/android_kernel_huawei_art-al00x](https://github.com/yuioto/android_kernel_huawei_art-al00x/tree/c1e2747d8e839bedaa71a6436d24a51285d98509) — Enjoy 10 / HarmonyOS 2 source | 4.14.116, kirin710 target | 5,277 shared symbols: 5,264 equal, 13 different; 35 stock-only, 1 candidate-only |
| [Kirin710/android_kernel_huawei_kirin710](https://github.com/Kirin710/android_kernel_huawei_kirin710/tree/4be3dcf8bcaa9f7c824d88e7045a8e4e1756c6df) | 4.14.116, kirin710 target | 4,704 shared symbols: 4,667 equal, 37 different; 608 stock-only, 285 candidate-only |

The Enjoy 10 tree is the stronger **candidate for further inspection**. It is a different handset's source, not an established P30 Lite build base. Counts compare explicit `CONFIG_` assignments and explicit `not set` entries by name/value; absent symbols are not treated as disabled. Config similarity does not measure boot compatibility, source completeness or working hardware.

[Comparison data](../raw/2026-11-12/04-kernel-source-comparison.json) records input hashes, Git blob IDs, pins, method and every differing/one-sided symbol. [Source excerpts](../raw/2026-11-12/05-source-inspection.json) preserve selected observations with pinned links.

## Useful matches

- The Enjoy 10 tree includes `drivers/gpu/arm/bifrost-r18p0-01rel0`; its Kbuild selects this directory for `CONFIG_MALI_SIGURD`, enabled in the stock config. The release family matches the phone's live Mali-G51 renderer (E06). Kernel/userspace ABI compatibility remains untested.
- Its `drivers/devkit/tpkit/panel/synaptics_tcm` implements the touchscreen family indicated by the phone's matching `MARI69110` identifier and `marie_synaptics_tcm_MARI69110.img` firmware filename (E09). The chip-info implementation can return a project ID in place of a plain manufacturer string. Neither the exact controller die nor panel supplier is established.
- It contains both `drivers/connectivity/hisi` and `drivers/connectivity/hi11xx`. The former reads `hi110x,subchip_type` from the device tree. This is a source lead, not identification of the phone's Wi-Fi chip: the phone-side lookup returned no output with errors suppressed (E09).

## Gaps before choosing a build base

1. The 35 stock-only entries split into 17 defined symbols and 18 missing definitions. Full stock normalization exposes 65 missing definitions, also absent from the comparison tree. Review the [complete coverage and build results](baseline-build.md), especially power, audio and security gaps; do not apply the candidate defconfig unchanged.
2. Reconcile the source with recovered Marie board data. Whole-tree preferred-source text inspection found no identified Marie/HWMAR/MARI69110 board description; the comparison tree's selected-marker search under `arch/` and `drivers/` also found none. An official .275 reference package now supplies base/overlay data: board ID 7800 uniquely matches overlay 186 and offline application resolves MAR-LX1A bindings. See [the board-matched reference](firmware-acquisition.md#board-7800-follow-up). Current phone DT bytes and complete matching vendor board sources remain unavailable.
3. Kconfig parsing now passes without source changes. The literal `-source` lines are Huawei's supported optional-include extension; see [the executed validation](baseline-build.md). No parser correction is required.
4. Clang `r353983c` plus GCC `aarch64-linux-android-4.9` now pass complete native candidate and Halium-probe builds. Full-LTO/CFI linking remains unresolved within the measured resource limit. This validates an offline research build, not MAR-LX1A compatibility. The older candidate's Clang `r346389c` has not been build-tested.
5. Resolve module compatibility deliberately. Stock enables forced signatures and versioning; an independently built kernel cannot simply be assumed to accept existing Huawei modules. No Huawei signing key is available.

## Existing port recipes

The [Kirin 710 Ubuntu Touch tree](https://github.com/kirin710-oss/ubports_huawei_kirin710/blob/aff092039160e7b1a54aa2f9f892a693398cec6c/deviceinfo) identifies **Nova 3I**, selects a **4.9** kernel source and hardcodes `datapart=/dev/mmcblk0p70`. Its Halium-11 branch name does not establish compatibility with this phone's Android-10 vendor base. Do not reuse its partition, boot-image or flashing values without measuring this handset.

The related [Mate 20 Lite Droidian project](https://github.com/jglasovic/droidian-kirin710/blob/3306469f46f8286379492236b4e99ea750a3ca93/device-config.sh) remains a reference for connectivity investigation. Its headless configuration disables charging and masks Android/LXC/UI services, so its installer is not an appropriate starting recipe for a touchscreen Ubuntu Touch home device. No installer was executed.

Software-only persistent unlocking remains a separate prerequisite for testing custom images; see [unlock feasibility](unlock-feasibility.md).
