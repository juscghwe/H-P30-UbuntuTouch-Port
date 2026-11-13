# Device and hardware assessment

## Target and firmware

E01 identifies a spare P30 Lite MAR-LX1A with Kirin 710, 4 GB RAM, 128 GB storage and a 1080 × 2312 display. These capacity values are owner-reported, not independently measured.

E02 confirms HWMAR, kirin710, ARM64 userspace support, Android 10 / SDK 29, VNDK 29, Treble enabled, and a running Linux 4.14.116 kernel. **The earlier EMUI 12 state used an Android 10 base.** EMUI's major version is not the Android API version.

Settings and ADB show different build identifiers: Settings reports 12.0.0.262(C431E3R2P2), while `ro.build.display.id` reports MAR-L21A 10.0.0.275(C431E8R2P7). Both observations are retained. Their precise relationship has not been independently established; this discrepancy is not evidence of a completed downgrade, a counterfeit device, or root. The generic `test-keys` vendor fingerprint also does not establish root.

In the later [E13 follow-up](../raw/2026-11-13/01-firmware-and-hisuite-offer.txt),
the owner confirms Settings **EMUI 10.0.0 / build 10.0.0.562(C431E15R2P7)** after
the official rollback. ADB still reports `.275`, Android 10, VNDK 29 and kernel
4.14.116. Keep both current identifiers and the earlier EMUI-12 evidence; the
unchanged kernel release does not establish equal config or kernel bytes.
The retained E08 configuration predates this rollback and must not be relabeled
as a fresh .562 configuration. [E14](../raw/2026-11-13/04-emui10-stock-kernel.config)
now supplies the distinct post-rollback configuration; see the
[configuration comparison](kernel-configuration.md).

## Graphics: runtime evidence

E06 confirms an active ARM Mali-G51 renderer, EGL 1.4, OpenGL ES 3.2, and driver release r18p0-01rel0. E05 lists Mali userspace libraries plus `hwcomposer.kirin710.so` and `gralloc.kirin710.so` in 32-bit and 64-bit directories. E08 enables Huawei framebuffer V320, vendor Mali integration and HiSilicon ION support.

This points to reusing Huawei's kernel and Android graphics stack through Halium/libhybris. It does **not** establish that Lomiri, hardware composition or accelerated applications work under Ubuntu Touch. Vendor interfaces, device nodes, memory allocation, permissions and synchronization still need integration and testing.

The configuration symbol `MALI_MIDGARD` is not used to override the actual runtime report of a Bifrost Mali-G51; vendor source naming needs inspection.

## Connectivity: compiled support, active variant unresolved

E08 enables the Hi110x/Hi11xx family, including Hi1102, Hi1102A and Hi1105. It names source locations `drivers/connectivity/hisi` and `drivers/connectivity/hi11xx`; Hi1102 platform and Wi-Fi entries are configured as modules. This supports investigating Huawei's connectivity drivers, but does not identify the actual active chip or driver path.

E05 lists only `hisi_dummy_ko` in `/proc/modules`. This does not explain where the active Wi-Fi implementation lives. Multiple enabled variants, vendor build behavior, and additional evidence must be considered before changing linkage or choosing firmware. The absent `/sys/class/net/wlan0/device/driver` link does not establish a driver fault.

The related Mate 20 Lite Droidian project reports Hi1102 Wi-Fi working with vendor firmware and platform initialization. Treat that as research to compare, not a tested recipe for this phone. See [references](references.md).

E09's lookup for `hi110x,subchip_type` below `/proc/device-tree` returned no output with errors suppressed. It does not distinguish an absent property from inaccessible device-tree data and does not confirm a Hi1102 fallback. The candidate driver reading this property is documented in [source inspection](kernel-source-candidates.md).

## Touchscreen: Synaptics TCM family indicated

E07 reports a physical input named **`huawei,ts_kit`**, with bus identifier 0x001c and zero vendor/product identifiers. This establishes the exposed Huawei touch-kit input interface, not the underlying controller vendor/model.

E09 reads `MARI69110` from `/sys/touchscreen/touch_chip_info` and lists `marie_synaptics_tcm_MARI69110.img` from the requested firmware directories; the other three requested directories do not exist. The matching project identifier and filename strongly indicate the **Synaptics TCM family**. The source candidate contains this driver and a chip-info path that can expose a project ID instead of the manufacturer string. See [source inspection](kernel-source-candidates.md).

E08 enables several touchscreen families; those options alone are not active-hardware evidence. The exact controller silicon, panel supplier and panel model remain unidentified. No touch operation outside stock Android has been tested.

E07 also lists fingerprint, power/volume keys and a headset-jack input. Their existence is not a test of those features under Ubuntu Touch.

## Confidence and current boundary

Confirmed: stock Android runtime identity, renderer, kernel configuration, USB access, bootloader lock, input wrapper, touchscreen project ID/firmware filename and a rollback offer.

E11 reports `ro.board.boardid=7800`. This uniquely matches an overlay in the
official .275 reference archive; offline application resolves MAR-LX1A and
Hi1102/LX1A INI settings. It narrows board integration, while the newer runtime
firmware's DT bytes and active Wi-Fi die remain unverified. See
[board-matched reference evidence](firmware-acquisition.md#board-7800-follow-up).

Unverified: exact Wi-Fi chip, exact touch controller/panel, matching complete build sources, final vendor base after unlocking, successful custom boot, graphics compatibility, Wi-Fi operation under Ubuntu Touch and suspend/reconnect behavior. The closer 4.14.116 candidate has passed [offline research builds](baseline-build.md); no device boot has been tested.
