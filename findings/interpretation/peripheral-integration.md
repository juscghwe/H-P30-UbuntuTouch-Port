# Peripheral integration and board-data requirements

Static source trace: Enjoy 10 kernel `c1e2747d8e839bedaa71a6436d24a51285d98509`. [File hashes and line references](../raw/2026-11-12-build/05-peripheral-source-trace.json) support the observations below. These are source behaviors, not tests of this handset.

## Touchscreen

The Synaptics TCM driver registers through Huawei touch kit. Its late-init path finds a `huawei,ts_kit` DT node and a compatible TCM child, assigns SPI read/write operations and registers the chip with touch kit. The root supplies `bus_type`, `bus_id`, `irq_gpio`, optional `reset_gpio` and a `product` string. Child properties include interrupt configuration, coordinate limits, regulators, polarity/delays, SPI mode/frequency and project-ID handling. Defaults in another handset's driver do not establish suitable Marie values.

The firmware prefix is assembled from the product and chip names. The zeroflash path requests `ts/<prefix><project_id>.img` through `request_firmware()`. This fits the observed `marie_synaptics_tcm_MARI69110.img` filename. The loader searches host-visible firmware directories including `/lib/firmware`, `/odm/etc/firmware` and `/system/vendor/firmware`, with a configurable firmware-class path. A vendor directory visible only inside the Android container is not automatically a suitable early kernel firmware source.

The pinned Iceows Marie recovery tree includes the same filename. Its blob is 116,817 bytes with SHA-256 `6a6290b715a49c88bde3bd17160d225bc18f649ad12f60f3b0cb3ac2b745d01c`. This is an **external artifact hash**, not a stock-phone measurement or permission to redistribute firmware. A phone-side hash can establish equality without uploading the binary. The recovery's touch HAL/service recipe is a reference, not proof those services are necessary for basic Linux input from this driver.

The [subsequent stock-phone hash (E10)](../raw/2026-11-12/07-stock-layout-and-access.txt) is `e6ad1811b63fdc422985a74b0e8cf8e8421a43cfe1fff4c91b2c586d7e351d1f`. It differs from the recovery artifact despite the identical filename and measured size of 116,817 bytes. The stock file has mode `0644`; the displayed 2018-08-07 timestamp is not used to infer its firmware release. Preserve the matching stock firmware; the reference blob is not a byte-identical substitute. The hash difference alone does not explain the firmware revision, compatibility or controller silicon.

The later [official vendor extraction](vendor-integration.md#touch-inputs)
recovers a blob that **does** match E10's size and SHA-256 exactly. Four recognized
TCM image areas pass independent bounds/CRC checks against the candidate source
format; a fifth differently tagged entry is skipped as in that source. This
replaces the need to substitute the differing recovery blob, while leaving
runtime loading and exact silicon/panel identification untested.

## Wi-Fi linkage and initialization

In this source, `CONNECTIVITY_HI1102=y` descends into `hisi/`; its platform and Wi-Fi subdirectories use `obj-y`. Their Makefiles choose built-in versus module linkage through the separate vendor variable `CONFIG_HI110X_KERNEL_MODULES_BUILD_SUPPORT`, defaulting to `no`. The candidate build generated both `platform/built-in.o` and `wifi/built-in.o` archives containing the corresponding objects, although its defconfig says `HI1102_PLATFORM=m` and `HI1102_WIFI=m`.

This explains why literal `m` settings alone cannot determine actual linkage. It is a plausible lead for the stock phone's sparse `/proc/modules`, not proof that stock uses this exact source or that Hi1102 is the active chip.

The built-in path registers `/sys/hisys/boot/plat` and `/sys/hisys/boot/wifi`. Their **show** handlers return `running`, `uninit` or a failure result. Their store handlers can initialize hardware; no writes to these nodes are part of evidence collection. Stock init services and ordering need to be retained or deliberately reproduced after the chip is identified.

Board selection reads `hi110x,subchip_type` from a `hisilicon,hi1102` compatible node. Firmware configuration paths include `/vendor/firmware/bfgx_and_wifi_cfg`, `wifi_cfg` and `bfgx_cfg`; the INI path is read from DT. GPIOs, SDIO/UART transport, clocks, calibration and NVRAM dependencies must match the real board. Calibration/NVRAM contents may contain personal identifiers and should remain private.

The earlier `find /proc/device-tree ... 2>/dev/null` result is inconclusive. Besides permissions, `/proc/device-tree` may be a symlink that `find` did not traverse. Inspect the actual path and preserve errors before interpreting an empty result.

E10 confirms `ADB_OK` and `sys.boot_completed=1`, followed by permission denial on both connectivity status files. The owner also reports denied device-tree traversal. This establishes an access restriction in a responding Android session, not an initialization-state result. `ro.connectivity.chiptype=hisi` selects a vendor family without identifying the active Hi110x variant; `ro.hardware.wlan` produced no value. The selected shallow init-file search returned no matching text, with no captured exit status; it does not establish absence of initialization elsewhere.

## Board data and image packaging

A search of the complete preferred tree found no Marie/HWMAR/MARI69110 board description. Matches for the word Marie were unrelated Linux author credits. The included HiSilicon DTS files describe reference boards. This is stronger coverage than the initial single-directory inspection, but it does not establish where Huawei distributed this handset's board data.

The Marie recovery reference uses a dummy kernel and separately configured recovery packaging. Its `BoardConfig.mk` offsets, sizes, anti-rollback settings and partition constants are not measured values for this phone and must not be copied into a port. The candidate also ships an opaque prebuilt `tools/mkbootimg`; it has not been executed or accepted as a device packaging specification.

E10 now supplies an actual named-partition map. Both `/dev/block/by-name` and `/dev/block/bootdevice/by-name` agree for these selected entries:

| Name | Observed target |
| --- | --- |
| `kernel` | `/dev/block/mmcblk0p48` |
| `ramdisk` | `/dev/block/mmcblk0p21` |
| `dts` | `/dev/block/mmcblk0p52` |
| `dto` | `/dev/block/mmcblk0p53` |
| `recovery_ramdisk` | `/dev/block/mmcblk0p50` |
| `erecovery_kernel` | `/dev/block/mmcblk0p45` |
| `erecovery_ramdisk` | `/dev/block/mmcblk0p46` |

These are owner-observed symlink targets, not proposed flashing commands. The four primary underlying nodes (`p21`, `p48`, `p52`, `p53`) have mode `0600`, owner/group `root:root`, so an ordinary non-root ADB shell cannot read their contents. Symlink mode `0777` does not grant access through these restrictions. The symlinks do not establish image formats, sizes or contents; in particular, `dts`/`dto` names alone do not prove standard DTB/DTBO encoding. Filesystem timestamps are not used to date firmware or infer an acquisition time.

Legitimate next inputs are a readable runtime FDT/DT subtree, or original kernel/DTB/DTBO/ramdisk images from a matching official Huawei update package already obtained for this handset. A live FDT may contain bootloader edits and does not replace the original DTB/DTBO inventory. Preserve original files and hashes privately, inspect selected board properties, and determine the split kernel/ramdisk and DT packaging from actual headers and partition metadata. Do not publish raw DT data without reviewing serial/MAC properties. No firmware or block-device image has been acquired from this phone during source validation.

[inspect-image.py](../../scripts/inspect-image.py) provides a read-only first pass over a regular image file. It reports SHA-256, numeric Android boot v0–v2 fields and component bounds/hashes, Android DT-table v0 entries, or FDT v17-compatible header bounds. It omits boot command lines, image names and DT properties. Unknown formats remain unknown; it does not infer a Huawei-specific layout, validate AVB signatures, extract data or generate flashable images.

```bash
python3 scripts/inspect-image.py ORIGINAL_IMAGE > reviewed-header.json
```

The implementation follows the AOSP [boot-header](https://source.android.com/docs/core/architecture/bootloader/boot-image-header) and [DT-table](https://source.android.com/docs/core/architecture/dto/partitions) specifications. Ten generated-fixture checks cover legacy headers, DT bounds, malformed/truncated inputs, unchanged input hashes and omission of embedded names/command lines. [Results](../raw/2026-11-12-build/08-image-inspector-validation.json) are host-tool validation, not inspection of an actual Huawei stock image.

Reproduce the generated-fixture checks with `python3 scripts/check-image-inspector.py` on a host with `dtc`; it creates no files in the checkout.

The subsequent [official .275 reference archive inspection](firmware-acquisition.md)
recovers real HSDT base-tree and Android DT-table v1 overlay inputs, plus split
kernel/ramdisk header observations. Its GPT agrees with all seven selected E10
entry numbers. The initial arbitrary overlay example contains AL00 and other
Marie INI paths, so its individual fragments cannot select the handset board.
E11 subsequently reports board ID 7800, matching exactly reference overlay 186.
Offline application to the base tree resolves MAR-LX1A/MAR_LX1A_VD, the LX1A INI,
Hi1102 and a SPI touch-kit/Synaptics TCM configuration. See the
[resolved evidence](../raw/2026-11-12-firmware/04-board-7800-overlay.json).
This supplies a board-matched integration reference without establishing current
stock-image equality, exact Wi-Fi silicon or Ubuntu Touch peripheral operation.

The reference vendor is now recovered through sparse/LP/EROFS inspection.
Its LX1A INI, Hi1102 firmware paths and built-in/module init branches correspond
to the candidate source. See the [vendor integration inputs](vendor-integration.md)
for the visibility/order requirements and the limits of this static match.

## Small read-only collection set

Run from the Windows Platform-Tools directory with Android booted. These commands do not reboot, write sysfs, request root, read block contents or change firmware. Preserve errors; review paths and output before sharing.

1. Check DT access and the selected Wi-Fi property:

```powershell
.\adb.exe shell 'ls -ld /proc/device-tree /sys/firmware/devicetree/base; ls -l /sys/firmware/fdt; find /sys/firmware/devicetree/base/ -name hi110x,subchip_type -print -exec od -An -tc {} \;'
```

2. Read initialization status and only the matching static init rules:

```powershell
.\adb.exe shell 'cat /sys/hisys/boot/plat /sys/hisys/boot/wifi; grep -n hisys /vendor/etc/init/*.rc /odm/etc/init/*.rc /system/etc/init/*.rc'
```

3. List relevant image partitions and hash the already identified touch firmware:

```powershell
.\adb.exe shell 'for d in /dev/block/by-name /dev/block/bootdevice/by-name; do ls -ld "$d"; ls -l "$d"/*dt* "$d"/*kernel* "$d"/*ramdisk*; done; sha256sum /vendor/firmware/ts/marie_synaptics_tcm_MARI69110.img'
```

If a path is denied or absent, that result is sufficient; no privilege escalation is implied. E10 records executed follow-ups and their exact commands separately from these templates. If firmware has changed, first repeat the selected identity queries in [collection methods](collection-methods.md).
