# Huawei P30 Lite Ubuntu Touch port investigation

Target: **Huawei P30 Lite MAR-LX1A / HWMAR, Kirin 710**. Initial goal: a usable Ubuntu Touch home device with touchscreen and Wi-Fi. Cellular support is deferred.

Start with [findings](findings/README.md). Evidence is separated into sanitized raw data and interpretation, including uncertainty and untested proposals.

**Current status:** stock Android is accessible over ADB and fastboot; the bootloader is locked. An official HiSuite rollback to EMUI 10 has been offered, but completion and a subsequent EMUI 9.1 route have not been reported. As of 2026-11-12 the owner requests software-only research; no verified complete unlock sequence for the current .262 firmware has been established. No custom kernel has been built, flashed or boot-tested in this investigation.

This repository currently contains documentation and configuration evidence, not an installable port. The target is the **P30 Lite**, not the Kirin 980 P30/P30 Pro.
