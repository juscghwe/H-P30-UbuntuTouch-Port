# Provisional Halium approach

## Vendor base determines the target

Current device evidence is Android 10 / SDK 29 / VNDK 29 beneath EMUI 12. Provisionally use **Halium 10**, preserving the matching stock vendor/ODM stack. The [current UBports version table](https://docs.ubports.com/en/latest/porting/introduction/Intro.html#android-and-halium-versions) maps Android 10 to Halium 10 / LineageOS 17.1. If an eventual unlock procedure leaves Android-9 vendor firmware, reassess for Halium 9 and recapture the kernel configuration. An EMUI label, GSI's Android version or another port's branch name does not settle vendor compatibility.

Use the [standalone kernel + Halium GSI workflow](https://docs.ubports.com/en/latest/porting/build_and_boot/standalone_kernel_build.html) provisionally. It allows kernel validation without first downloading a full Android source tree. The device repository will need measured kernel/ramdisk/DT layout and partition names before any usable `deviceinfo` or image can be produced. The Nova 3I recipe's 4.9 kernel and hardcoded data partition remain excluded.

## Configuration and AppArmor probe

[halium10-probe.config](../../configs/halium10-probe.config) enables namespace/IPC/device-filesystem facilities from the UBports minimum, plus the reviewed cgroup/network and AppArmor settings. It is an experimental fragment, not a complete compatible kernel configuration. Merge it into a separate stock-derived output; check every requested value after `olddefconfig` rather than assuming the merge survived dependencies.

The [UBports AppArmor instructions](https://docs.ubports.com/en/latest/porting/configure_test_fix/Apparmor.html) link the 4.14 socket-mediation commits in `kdrag0n/proton_zf6`. The two latest same-date commits are pinned as:

1. `559e4f447556e1ea0b24b035965023b6fba8f2f8`: base socket mediation.
2. `f076c3083d908253d32d26b49d64faaf4f80b442`: AF_UNIX mediation.

Their canonical patches apply to this source after excluding a missing `.gitignore` hunk, which changes no kernel code. [apply-apparmor.sh](../../scripts/apply-apparmor.sh) verifies patch hashes and preflights both against a temporary copy before modifying a clean source checkout. It does not replace the entire AppArmor directory. Source-level application alone does not establish the policy features needed by the chosen Ubuntu Touch userspace; compilation and eventual confinement tests are separate checks.

The kernel's config merge helper creates a temporary file in its **current directory** and can report success even after a failed `mktemp`. Run it from a writable output directory with `bash -e`, verify the resulting config exists, and check requested symbols before compiling. An initial probe run from a read-only directory failed this way and produced an invalid minimal config; that attempt is discarded and is not evidence of a stock-source CMA defect.

A correctly merged probe exposed a real configuration collision: both Huawei `HW_CGROUP_PIDS` and standard `CGROUP_PIDS` register the `pids` subsystem. The probe fragment selects standard `CGROUP_PIDS` and disables `HW_CGROUP_PIDS`; the stock and candidate configurations remain separate. This choice still needs container/runtime validation.

## Integration boundary

Preserve stock display/touch firmware and connectivity calibration/init dependencies while integrating the Halium GSI. The official [Wi-Fi guide](https://docs.halium.org/en/latest/porting/debug-build/wifi.html) documents Qualcomm/Broadcom examples, not this Hi110x initialization path. Use the [source trace and selected phone checks](peripheral-integration.md) instead of copying those chipset commands or disabling module signatures.

The stock-derived resource probe changes 18 shared explicit values, omits 78 stock entries and adds 31 entries. [The complete generated comparison](../raw/2026-11-12-build/12-stock-halium-config-differences.json) includes source-normalization losses and dependent entries, rather than equating omissions with disabled options. It switches the default security module from SELinux to AppArmor and adds namespace, cgroup and networking requirements. Its separately labelled resource fragment disables LTO/CFI; this configuration is an offline compilation probe, not an accepted device security or compatibility baseline. See the [executed merge recipe](baseline-build.md#reproduction).

Next implementation order: obtain a complete baseline image, validate the derived configuration and AppArmor code, recover actual board/image metadata, then build a device-specific boot recipe. Persistent unlocking remains necessary before any phone test. No Ubuntu Touch boot or working peripheral is demonstrated.
