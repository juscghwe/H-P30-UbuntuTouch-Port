# Board-7800 vendor integration inputs

Scope: offline analysis of the verified official `.275` reference archive,
the board-matched merged DT and the pinned Enjoy 10 source. This is not a
phone boot, hardware test or claim that the newer runtime vendor is identical.

## Vendor recovery

`SUPER` is Android sparse v1.0: 617 chunks representing 5,343,543,296 logical
bytes. LP metadata v10.0 has one slot and five partitions: `system`,
`hw_product`, `cust`, `vendor`, `odm`. Both geometry checksums, the metadata
header/table SHA-256 values and matching primary/backup copies pass.

The [offline SUPER reader](../../scripts/inspect-super.py) extracted the
501,219,328-byte `vendor` partition directly through sparse extents; no full
SUPER expansion or filesystem mount was needed. Its SHA-256 is
`b2648997286f4974ea27bab946a0c8b061daf405f2c7b2eb1243b6e014a5ca29`.
`fsck.erofs` 1.5 returns success while checking and extracting the EROFS files,
using a read-only input and ordinary-user output permissions. Input hash remains
unchanged. No program or script from the firmware was executed.

[Recovery evidence](../raw/2026-11-12-firmware/05-super-vendor-extraction.json)
records source offsets/hashes and validated metadata. The reader supports the
observed sparse/LP versions and one block device; it rejects nonzero sparse
image CRC fields or CRC chunks rather than silently skipping verification.
Sparse holes are modeled as zero, not as observed contents of live storage.

Equivalent extraction from the already verified `UPDATE.APP`, with output
outside this repository:

```sh
python3 scripts/inspect-super.py /path/reference/UPDATE.APP --offset 979801402 --length 3577762232 --extract-partition vendor --output /path/reference/vendor.img
fsck.erofs --extract=/path/reference/vendor-files --no-preserve /path/reference/vendor.img
```

## Touch inputs

The recovered `marie_synaptics_tcm_MARI69110.img` is 116,817 bytes and has the
**same SHA-256 as the owner-measured stock file (E10)**:
`e6ad1811b63fdc422985a74b0e8cf8e8421a43cfe1fff4c91b2c586d7e351d1f`.
It differs from the previously inspected recovery-tree blob. No phone-side file
upload is needed to obtain these matching bytes legitimately.

Independent inspection matches the candidate TCM loader's container magic and
validates bounds/CRC32 for `BOOT_CONFIG`, `F35_APP_CODE`, `APP_CONFIG` and
`DISPLAY`. A fifth entry has different magic and is skipped by that source's
parser; it was not interpreted as a valid area. The kernel parser itself was
not executed. Container checks do not identify the exact controller silicon or
prove its firmware will load under a rebuilt kernel.

The source finds `huawei,ts_kit`, reads `bus_type`/`bus_id`, and finds a
`synaptics_tcm` child. Those names agree with the resolved reference DT. It
constructs `ts/<product>_<chip>_<project>.img` and uses `request_firmware()`.
An early private initramfs/rootfs copy under `/lib/firmware/ts/` is a candidate
for making the matching blob visible before Android vendor mounts; this has not
been built or boot-tested. Do not assume container-only paths are visible to
every firmware-loader context.

## Wi-Fi inputs and ordering

| Reference input | Source/init correspondence |
| --- | --- |
| `/hi110x`, compatible `hisilicon,hi1102`, `subchip_type="hi1102"` | Candidate board reader recognizes this selector |
| `/hisi_cust_cfg`, compatible `hi1102,customize` | INI reader obtains the DT filename |
| `/vendor/etc/cfg_marie_lx1a_hisi.ini` | Matching reference file recovered; hash recorded |
| `/vendor/firmware/bfgx_and_wifi_cfg`, `wifi_cfg`, `bfgx_cfg` | Candidate default configuration paths exist in the reference vendor |
| `CPU_RAM_SCHED.bin`, `CPU_RAM_WBS.bin`, `cr4_asic.bin` | Files named by those configuration records exist; sizes/hashes recorded |
| `/dev/ttyAMA4` | Board BFGX UART setting and reference init permissions agree |

The reference init chain imports files using `ro.boot.odm.conn.chiptype` and
`ro.boot.odm.conn.schiptype`. [E12](../raw/2026-11-12/10-connectivity-selector-report.txt)
reports empty shell reads for both. That does not establish property absence
or prove which branch the current firmware executes.

In the reference Hi1102 branch, `hisi_bfg` invokes `start_connectivity_hisi`
with `dir_p_mode`. Static reading shows that it:

1. Reads the DT INI path, searches `CUST_POLICY_DIRS` in reverse priority order
   and then tries the direct path, creating `/data/vendor/cust_conn/ini_cfg`.
2. Uses built-in platform/Wi-Fi initialization when `/sys/hisys/boot` exists;
   otherwise attempts separate `plat.ko`/`wifi.ko` modules. These two modules
   are absent from this reference vendor, which contains only `hisi_dummy_ko.ko`.
3. Sets a completion property based on a device-node existence check. This is
   a service-ordering trigger, not a Wi-Fi functional test.

This corroborates the earlier Makefile finding: literal `HI1102_PLATFORM=m`
and `HI1102_WIFI=m` options do not establish actual module linkage. It does not
justify loading stock modules into a rebuilt kernel or disabling other stock
Hi110x variants solely from older reference data.

The reference declares Wi-Fi HAL 1.3, hostapd 1.1, supplicant 1.2 and Huawei
extensions. Its vendor SDK is 29/Android 10 and its fingerprint matches E02;
this strengthens the provisional Halium 10 base choice. It does not establish
full vendor equality or compatibility with Ubuntu Touch networking services.

## Next implementation boundary

Preserve the board-matched DT, exact firmware bytes, INI policy and loader
ordering as inputs to device adaptation. Audit path visibility and privilege
boundaries deliberately; do not execute the stock helper as an investigation
shortcut. Current initialization, live Wi-Fi silicon, calibration/NVRAM, power
behavior, signatures and successful custom boot remain unverified.

[File/init observations](../raw/2026-11-12-firmware/06-vendor-files-and-init.json)
and the [source-pinned binding/format audit](../raw/2026-11-12-firmware/07-driver-binding-audit.json)
contain hashes and selected facts. Firmware binaries, full init scripts, INI
contents and extracted filesystems remain outside the public checkout.
