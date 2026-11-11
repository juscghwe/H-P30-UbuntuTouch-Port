# Device and hardware assessment

## Target and firmware

E01 identifies a spare P30 Lite MAR-LX1A with Kirin 710, 4 GB RAM, 128 GB storage and a 1080 × 2312 display. These capacity values are owner-reported, not independently measured.

E02 confirms HWMAR, kirin710, ARM64 userspace support, Android 10 / SDK 29, VNDK 29, Treble enabled, and a running Linux 4.14.116 kernel. **EMUI 12 is running on an Android 10 base.** EMUI's major version is not the Android API version.

Settings and ADB show different build identifiers: Settings reports 12.0.0.262(C431E3R2P2), while `ro.build.display.id` reports MAR-L21A 10.0.0.275(C431E8R2P7). Both observations are retained. Their precise relationship has not been independently established; this discrepancy is not evidence of a completed downgrade, a counterfeit device, or root. The generic `test-keys` vendor fingerprint also does not establish root.

## Graphics: runtime evidence

E06 confirms an active ARM Mali-G51 renderer, EGL 1.4, OpenGL ES 3.2, and driver release r18p0-01rel0. E05 lists Mali userspace libraries plus `hwcomposer.kirin710.so` and `gralloc.kirin710.so` in 32-bit and 64-bit directories. E08 enables Huawei framebuffer V320, vendor Mali integration and HiSilicon ION support.

This points to reusing Huawei's kernel and Android graphics stack through Halium/libhybris. It does **not** establish that Lomiri, hardware composition or accelerated applications work under Ubuntu Touch. Vendor interfaces, device nodes, memory allocation, permissions and synchronization still need integration and testing.

The configuration symbol `MALI_MIDGARD` is not used to override the actual runtime report of a Bifrost Mali-G51; vendor source naming needs inspection.

## Connectivity: compiled support, active variant unresolved

E08 enables the Hi110x/Hi11xx family, including Hi1102, Hi1102A and Hi1105. It names source locations `drivers/connectivity/hisi` and `drivers/connectivity/hi11xx`; Hi1102 platform and Wi-Fi entries are configured as modules. This supports investigating Huawei's connectivity drivers, but does not identify the actual active chip or driver path.

E05 lists only `hisi_dummy_ko` in `/proc/modules`. This does not explain where the active Wi-Fi implementation lives. Multiple enabled variants, vendor build behavior, and additional evidence must be considered before changing linkage or choosing firmware. The absent `/sys/class/net/wlan0/device/driver` link does not establish a driver fault.

The related Mate 20 Lite Droidian project reports Hi1102 Wi-Fi working with vendor firmware and platform initialization. Treat that as research to compare, not a tested recipe for this phone. See [references](references.md).

## Touchscreen: active wrapper identified

E07 reports a physical input named **`huawei,ts_kit`**, with bus identifier 0x001c and zero vendor/product identifiers. This establishes the exposed Huawei touch-kit input interface, not the underlying controller vendor/model.

E08 enables several touchscreen families. The presence of THP options does not establish that THP is the active path; the observed input name is ts_kit. We still need the active device-tree selection and/or readable touchscreen identification attributes. No exact panel supplier or panel model has been identified.

E07 also lists fingerprint, power/volume keys and a headset-jack input. Their existence is not a test of those features under Ubuntu Touch.

## Confidence and current boundary

Confirmed: stock Android runtime identity, renderer, kernel configuration, USB access, bootloader lock, input wrapper and a rollback offer.

Unverified: exact Wi-Fi chip, exact touch controller/panel, matching complete build sources, final vendor base after unlocking, successful custom boot, graphics compatibility, Wi-Fi operation under Ubuntu Touch and suspend/reconnect behavior.
