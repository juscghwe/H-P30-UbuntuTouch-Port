# Android-9 boot and persistent-unlock checkpoint

Evidence date: **2026-11-20**. [Selected owner output](../raw/2026-11-20/01-owner-unlock-evidence.txt), [primary GPT analysis](../raw/2026-11-20/02-primary-gpt-comparison.json), [readback/extraction checks](../raw/2026-11-20/03-readback-and-flash-checks.json).

## Result and acceptance boundary

The owner reports normal stock Android startup with Settings **EMUI 9.1**, followed by ordinary Volume-Down/USB fastboot entry without testpoint or a service-loader job. The screen shows **PHONE unlocked / FRP unlocked**, and `fastboot oem get-bootinfo` returns `unlocked`. This establishes persistence beyond the temporary loader session on the retained installation. No custom image or Ubuntu Touch boot has been tested; future firmware upgrades and access to every protected partition remain untested.

The prepared input set was base **9.1.0.399**, CUST **9.0.1.6(C431)** and PRELOAD **9.0.1.3(C431R2)**, pinned in the [full-package inventory](../raw/2026-11-17/03-firmware-package-verification.json). Exact post-boot component properties, API/VNDK and kernel/configuration have not yet been recaptured. Do not replace that missing runtime evidence with package labels.

## Observed sequence

1. Physical testpoint entry enumerated `12d1:3609`, then HUAWEI USB COM 1.0 after driver binding. Battery and USB power were removed before positioning the bridge.
2. HCU **1.0.0.0382 / Kirin710_P1_V2** read the retained `.562` firmware and reported factory FB unlocked but user lock locked. Repair wrote OEMINFO and reported unlock-restrictions success. Ordinary fastboot after normal Android-10 startup still reported **locked**.
3. AUP **v200.01.0001:01:01:2026 / KIRIN710** reached factory fastboot after the requested second physical USB/testpoint entry. The owner removed the bridge at enumeration and reconnected the battery at DDR `[4]`. Ordinary fastboot queries then answered in that temporary session. The publisher-linked binary is [pinned separately](../raw/2026-11-17/01-android-utility-static-readiness.json).
4. AUP's GPT reader rejected `oem dump-emmc ptable` with `invalid command` under both loaders. Its following invalid-table message did not establish disk corruption. [DC-Phoenix's EMMC dump workflow](https://www.dc-unlocker.com/dcphoenix-emmc-dump) instead exported the table, critical partitions, stock boot inputs and an actual-name `super` image. Backups remain private.
5. AUP **FW Update (FB)** wrote the Android-9 set. CUST/PRELOAD size-setting records failed; screenshots separately show actual VERSION and PRELOAD image writes succeeding. A complete per-partition flash log has not been reviewed. Final banners alone are not accepted as write verification.
6. The post-flash primary GPT matches the Android-9 reference's partition names and ranges, with userdata extended to the phone capacity. A data-corruption/format prompt preceded the subsequent normal Android startup. Ordinary fastboot then passed the persistence check above.

No second HCU Repair after the downgrade was reported. The combined sequence succeeded; the independent contribution of the earlier OEMINFO write, temporary-loader patches and replacement stock bootloader was not isolated. Do not describe this as a verified direct HCU unlock on Android 10 or a software-only route.

## Partition and metadata findings

The original exported GPT contains the Android-10 `ramdisk`, per-filesystem vbmeta entries and **5,343,543,296-byte `super`**. Phoenix's GUI instead displayed an older suffixed-name map. Selected NV/calibration and kernel/DT/recovery ranges coincide across both layouts, but the large filesystem ranges do not. GUI labels cannot substitute for inspecting the raw table.

The failed records contain only `version=33554432` and `preload=1199570944`. After flashing, `version_a` is **603,979,776 bytes**, matching the base Android-9 reference rather than the requested CUST resize; `preload_a` is **1,199,570,944 bytes**, as expected. Primary-header and entry-array CRCs pass and populated partition ranges do not overlap. This does not validate the uncaptured backup GPT or every stored image.

Userdata's start moved **570,425,344 bytes**. The subsequent stock-recovery data-format prompt is consistent with that migration and the changed system base; it does not by itself identify failing storage.

## Next porting boundary

- Preserve this retained firmware and private backups. No relock or return to a newer EMUI release has been validated.
- Capture runtime Android/vendor SDK, VNDK, kernel release, component properties and `/proc/config.gz` before selecting the next source/configuration or Halium version.
- Keep prior Android-10 stock/reference evidence and research builds separate. The existing Enjoy-10 4.14.116 images are not demonstrated compatible with this retained Android-9 installation.
- Use ordinary fastboot for subsequent read-only identification. Boot-image packaging, custom boot and restoration remain separate implementation milestones.
