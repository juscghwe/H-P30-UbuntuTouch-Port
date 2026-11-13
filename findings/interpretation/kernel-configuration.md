# Stock kernel configuration assessment

Evidence: [E08](../raw/2026-11-11/08-stock-kernel.config), decompressed from the owner's `/proc/config.gz`. Header: Linux/arm64 4.14.116. This is a configuration audit, not a successful build or a complete Halium compatibility check.

## Post-rollback configuration: E14

The owner supplied a fresh `/proc/config.gz` after Settings confirmed EMUI
10.0.0 / `.562(C431E15R2P7)`. Its [exact payload](../raw/2026-11-13/04-emui10-stock-kernel.config)
is 165,429 bytes, SHA-256
`39e8fe7311c7af288e344fa1b98315597e57ca5fee3f1c250dc16b265a379bf3`.
Keep it separate from E08 and the existing research builds. [Generated comparisons
and provenance](../raw/2026-11-13/05-emui10-config-provenance-and-comparison.json)
record the inputs and method.

Compared with pre-rollback E08, 4,598 common settings match, 34 differ, 680
explicit settings appear only in E08 and 270 only in E14. Missing entries are
not automatically disabled settings. Battery identification/temperature settings
change from `y` to `n`; this is compiled configuration, not evidence of broken
stock charging or permission to remove power-management behavior.

The official `.275` reference kernel is much closer: 4,898 shared settings match,
only `HISEE_SUPPORT_INSE_ENCRYPT` differs (`n` to `y`), and E14 adds explicit
`GENERAL_SEE_PINCODE=y`, `HUAWEI_MINCORE_CLASSIC=n` and `UNIX_SCM=y` entries. This
supports the reference's relevance to the retained Android base, not kernel,
bootloader or vendor-image byte equality. Forced module signing, module versioning,
disabled namespaces and disabled AppArmor remain in E14. Rebase the stock-derived
Halium configuration deliberately before claiming a build for this firmware.

## Concrete starting points

| Area | Selected stock settings | Implication |
| --- | --- | --- |
| Architecture | `ARM64=y`, `64BIT=y` | ARM64 cross-compilation target |
| Debugging | `IKCONFIG=y`, `IKCONFIG_PROC=y`; pstore/ram-console support enabled | Current config captured; persistent logs may help later if the device exposes them |
| Android IPC | `ANDROID_BINDER_IPC=y`, devices `binder,hwbinder,vndbinder` | Existing Android driver interface to preserve where appropriate |
| Filesystems | ext4 and overlay enabled; loop devices enabled | Useful existing building blocks; final image layout still requires validation |
| Device filesystem | `DEVTMPFS=y`, automatic mount disabled | Explicit mounting/boot configuration must be checked |
| Wi-Fi | Hi110x/Hi11xx paths; `HI1102_PLATFORM=m`, `HI1102_WIFI=m` | Locate full driver sources and identify actual variant/init/firmware |
| Display | `HISI_FB_V320=y`, `MALI_PLATFORM_HISILICON=y`, HiSilicon ION | Preserve the board-specific display/memory stack during first bring-up |

## Known gaps

Stock disables `NAMESPACES`, `SYSVIPC`, `FHANDLE` and `VT`. The current UBports minimum configuration includes namespaces and these facilities. Individual namespace options must be resolved in the actual source tree once their parent dependencies are enabled.

`SECURITY_APPARMOR` and `SECURITY_PATH` are disabled. Ubuntu Touch security support needs the appropriate kernel patch set and configuration, rather than simply selecting a config symbol. Do not treat disabling confinement as a finished port.

`CGROUP_DEVICE`, `CGROUP_PIDS`, `BRIDGE` and `VETH` are disabled. Evaluate these against the selected Halium/LXC/userspace setup. This list is not a claim that every symbol is mandatory for every porting method. Squashfs is also disabled; whether it is needed depends on the chosen image arrangement.

## Module compatibility constraint

`MODULE_SIG_FORCE=y`, `MODVERSIONS=y`, `MODULE_SIG_ALL=y`, and the generic signing-key filename `huawei_signing_key.pem` are present. The key itself was not provided and is not in this repository. The filename is an ordinary build setting, not a private key.

An unchanged stock module is not guaranteed to load into a rebuilt kernel even if the release string is identical. Signature policy, symbol versions, configuration and vendor ABI all matter. Four modules now [compile and pass offline signature verification](baseline-build.md) with a new local development certificate; none was loaded. The candidate builds Hi110x objects in through vendor Makefile controls despite literal `m` entries. Neither result establishes compatibility with the phone's stock modules or active Wi-Fi hardware.

## Source and toolchain selection

Kernel version equality alone does not establish source compatibility. Validate the board device trees, Huawei drivers, build scripts, config symbols, generated headers, and external modules against the captured configuration. The first milestone is a reproducible compatible kernel build; then add minimal porting changes incrementally.

The documented source/toolchain pair now produces offline research images, but no device-validated pair has been selected. Do not substitute a generic mainline kernel or a P30/P30 Pro Kirin 980 tree. After any firmware change, recapture the running configuration and align source/vendor components with the firmware actually retained.

Reference: [UBports building the kernel](https://docs.ubports.com/en/latest/porting/build_and_boot/standalone_kernel_build.html).
