# Huawei P30 Lite Ubuntu Touch port investigation

Target: **Huawei P30 Lite MAR-LX1A / HWMAR, Kirin 710**. Initial goal: a usable Ubuntu Touch home device with touchscreen and Wi-Fi. Cellular support is deferred.

Start with [findings](findings/README.md). Evidence is separated into sanitized raw data and interpretation, including uncertainty and untested proposals.

**Current status (2026-11-20):** the owner reports normal stock EMUI 9.1 startup after a hardware-testpoint/factory-fastboot downgrade, followed by **unlocked ordinary fastboot** without a service loader. [The technical checkpoint](findings/interpretation/unlock-checkpoint.md) records the failed Android-10 persistence test, successful retained-installation check, GPT comparisons and remaining limits. No custom image or Ubuntu Touch boot has been demonstrated. Fresh kernel/configuration and vendor-version evidence is required for the retained Android-9 base.

This repository currently contains documentation and configuration evidence, not an installable port. The target is the **P30 Lite**, not the Kirin 980 P30/P30 Pro.

The pinned Enjoy 10 source and its documented Clang/GCC toolchain produced [candidate and stock-derived Halium kernel images](findings/interpretation/baseline-build.md) with LTO/CFI disabled. Four staged Halium modules pass offline development-signature verification. Full-LTO resource failures, remaining source gaps and unresolved warnings prevent treating these builds as a device port. Binaries and signing keys are not distributed here.

An official Huawei reference archive now supplies [board-7800 DT/vendor inputs](findings/interpretation/vendor-integration.md), including touch firmware identical to the owner-measured stock file. Driver bindings and loader ordering have been audited offline. Current image equality, peripheral operation and custom boot remain unverified; proprietary images and firmware stay outside this repository.
