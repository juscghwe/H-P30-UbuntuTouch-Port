# Android Utility USB Upgrade readiness

**Latest result, 2026-11-20:** the separate [hardware-assisted FW Update (FB) sequence](unlock-checkpoint.md) reached normal EMUI 9.1 startup and persistent ordinary-fastboot unlock. That sequence had resize-record failures and required independent GPT checks; it is not a general restoration guarantee.

Historical DLOAD status, 2026-11-17: **Android-9 DLOAD attempt failed during BASE-PTABLE metadata; Android 10 boots afterward**. The remainder of this document records that earlier path and static package inspection.

The [MFDL changelog](https://www.mfdl.io/changelog) lists Huawei USB firmware
updates through DLOAD/Upgrade mode separately from Fastboot partition operations
and Kirin factory-loader access. A successful factory-loader procedure that uses
physical testpoint does not establish an ordinary locked-phone USB Upgrade path.

## Inspected download

The publisher's current `/gsm-tools/` listing links this
[MediaFire archive](https://www.mediafire.com/file/dp73po1rf9x4rgz/AndroidUtility.v200.7z/file).
[Inspection metadata](../raw/2026-11-17/01-android-utility-static-readiness.json)
pins the page and downloaded file. The archive is 331,167,214 bytes, SHA-256:

```text
bbad153b50b56bf98b1ca97a5262de38bac3e0b8620cd22f3610d1df4742b8eb
```

The downloaded file is an encrypted ZIP despite its `.7z` extension; a
password-assisted archive CRC test passed for all 1,016 members. The publisher's
directory declares a slightly different size, so record the actual hash rather
than treating the directory size as verified. A compatible archive reader can
identify the real format. The research environment did not execute any bundle
program or driver. The owner later launched the application on Windows.

The main `AndroidUtility.exe` is a 32-bit Windows PE with no embedded Authenticode
certificate. Its actual PE-resource manifest requests administrator rights.
Its static UI string identifies `v200.01.0001:01:01:2026` Offline; the owner
subsequently supplied a matching running interface. Source provenance, a matching
hash and archive CRCs do
not establish binary safety. An isolated Windows environment is preferable for
the first application launch; retain existing antivirus protections.

## Owner-observed mode-entry test

[Selected observations](../raw/2026-11-17/02-owner-usb-upgrade-mode-test.json)
record the running Huawei/Service interface and a failed initial DBAdapter
lookup. After the documented Manufacture Mode setup, Windows listed DBAdapter,
PCUI, ADB and Huawei ACM interfaces. `Huawei Normal To Upgrade` then reported a
successful reboot command. No firmware files were loaded or update action requested.

The phone displayed an installation screen at 5%, remained there across follow-ups,
and eventually rebooted itself into normal Android. The same Windows interfaces
remained listed during the test. An ADB property query failed as unauthorized;
no recovery-service or bootmode value was obtained. The precise waiting/reboot
cause remains unknown. This demonstrates the observed entry/exit sequence, not
acceptance of an Android-9 image or a persistent unlock.

The separate `Load Factory Fastboot` control is grouped under HiSilicon USB1.0.
Its observed default was KIRIN620, not this phone's Kirin 710; it was not used.
Do not carry its dropdown selection or factory-loader assumptions into the
Normal-to-Upgrade operation.

## Failed Android-9 DLOAD attempt

[E18](../raw/2026-11-17/07-owner-dload-failure.json) records successful Windows
preparation of all six reference archives/APP extractions, followed by a DLOAD
attempt using the Android-9 files. The phone displayed Software install failed.
AUP reported these early BASE-PTABLE records:

| Record | Size | AUP result |
| --- | --- | --- |
| SHA256RSA | 804 bytes | Ok |
| CRC | 20 bytes | Ok |
| BASE_VERLIST | 330 bytes | Ok |
| BASE_VER | 25 bytes | fail |

Those sizes match the independently inventoried Android-9 PTABLE.APP. The failure
occurred before the large base UPDATE.APP stage was shown; the unobserved GUI
offset beyond 4 GiB does not explain this particular failure. The log does not
show a completed GPT transfer, but it cannot prove that every stored value stayed
unchanged.

AUP then printed `Download ptable base partitions ok!` and started CUST despite
the failure. [Selected binary control flow](../raw/2026-11-17/09-aup-failure-handling.json)
confirms this behavior: the failed-transfer branch at `0x12ddac3` reaches the
failure message, then jumps at `0x12e011e` into the success-looking banner and
subsequent package stage. This is a client error-handling problem; it does not
identify the native refusal or make the failed transfer successful.

The owner stopped AUP and reported normal Android returning. [E19](../raw/2026-11-17/08-post-attempt-state.txt)
then reports `sys.boot_completed=1` with the same `.562` / `.15(C431)` /
`.7(C431R2)` component labels as E17. Partition/OEMINFO equality was not measured.
Selected native recovery-log metadata reads were denied, so no native error code
was obtained. Version policy, package handling and transport failure remain
possible explanations; hardware anti-rollback is not established as the cause.

Do not repeat this workflow unchanged, omit metadata as a guessed fix, or follow
a generic suggestion to alter OEMINFO. Further phone writes need evidence that
addresses the failed metadata exchange and the client's failure propagation.
The software-only downgrade/unlock chain remains unverified.

## Full firmware-package inspection

[Package verification](../raw/2026-11-17/03-firmware-package-verification.json)
pins six full Huawei downloads: Android-9 base `.399`, CUST `.6(C431)` and
PRELOAD `.3(C431R2)`, plus Android-10 reference base `.562`, CUST `.15(C431)`
and PRELOAD `.7(C431R2)`. Manifest sizes/digests and every ZIP member CRC pass.
The Android-9 base manifest supplies only MD5; its recorded SHA-256 was computed
locally. PTABLE.APP and UPDATE.APP record bounds parse for every package. These
checks do not validate Huawei signatures or device rollback authorization.

| Base package | UPDATE.APP records | Selected layout | Internal BASE_VER |
| --- | --- | --- | --- |
| Android 9 / `.399` | 43 | SYSTEM, VENDOR, ODM, PRODUCT | `Marie-LGRP2-OVS 9.1.0.279` |
| Android 10 / `.562` | 44 | SUPER and additional vbmeta images | `MAR-LGRP2-OVS 10.0.0.1` |

The Android-9 BASE_VERLIST does not include the Android-10 base identifier.
This is a validation concern, not proof of a specific rejection mechanism.
The different image sets also require a partition-layout migration assessment;
this cannot be treated as a kernel-only downgrade.

The Android-10 CUST has the same version label and VERSION payload as the owner
capture, but its ZIP and UPDATE.APP differ. PACKAGE_TYPE timestamps and
signature/CRC records differ. It is a version-matched reference, not an identical
HiSuite capture or a demonstrated restore package.

## Partition-table comparison

[Primary eMMC template checks](../raw/2026-11-17/04-partition-layout-comparison.json)
pass GPT header and array CRCs for both packages. The Android-10 indices match
all seven owner-supplied by-name links. At a supplied 512 bytes per logical sector:

| Image / area | Android-9 reference entry | Android-10 reference entry | Byte range |
| --- | --- | --- | --- |
| kernel | 43 `kernel_a` | 48 `kernel` | Equal |
| recovery ramdisk | 45 `recovery_ramdisk_a` | 50 `recovery_ramdisk` | Equal |
| DTS | 47 `dts_a` | 52 `dts` | Equal |
| DTO | 48 `dto_a` | 53 `dto` | Equal |
| userdata | 70 | 71 | Equal template extent; live userdata index not collected |

Android 10 splits Android-9 `reserved2` into ramdisk and five vbmeta partitions,
changes `reserved3_a` to kpatch, enlarges PREAS by 32 MiB and moves PREAVS.
Its SUPER replaces several separate Android-9 filesystem partitions. Terminal
`_a` removal is only a comparison aid, not proof of A/B slot support.

Both selected GPT headers have zero backup/last-usable LBAs and a 4 GiB userdata
template extent. They do not establish actual storage capacity or provide a
validated full-device partition table. Other embedded GPT signatures are not
selected as this eMMC phone's geometry. The full base UPDATE.APP also contains
HISIUFS_GPT, so omitting the separate PTABLE input does not prove GPT writes are avoided.

## Recovery wait and version validation

[Static recovery analysis](../raw/2026-11-17/05-recovery-usb-validation.json)
extracts a separate compiled DLOAD updater from the `.562` recovery ramdisk.
Its USB wait path logs 300 seconds and calls a no-action reboot routine. That
is consistent with the observed automatic exit, without proving current phone
recovery-byte equality or a measured five-minute wait.

Selected control flow reads a 32-byte comparison value through OEMINFO item 156,
hashes version-list lines with SHA-256 and has a rejection branch on a failed
list check. Error/state-dependent paths also exist. Thus the list check is more
than a static label, but the phone's actual stored comparison value is unknown.
No validation check was patched or bypassed.

[E17 component properties](../raw/2026-11-17/06-component-versions.txt) confirm
base `.562`, CUST `.15(C431)` and PRELOAD `.7(C431R2)` after return to Android.
Those properties are not interchangeable with BASE_VER payloads or the stored
comparison hash. Neither the missing Android-10 text in the Android-9 list nor
matching component labels alone proves the exact acceptance result.

## PC-side preparation

[`prepare-huawei-firmware.ps1`](../../scripts/prepare-huawei-firmware.ps1) downloads
the six pinned archives from Huawei HTTPS, checks exact sizes/SHA-256 and optionally
extracts only PTABLE.APP and UPDATE.APP into separate component directories.
It pins the [inspection manifest](../raw/2026-11-17/03-firmware-package-verification.json)
by SHA-256, preserves existing partial/invalid files and runs no archive program,
ADB, Fastboot or phone operation. Failed extraction output stays `.part` for review.

From a repository checkout, this is one physical Windows PowerShell line:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\prepare-huawei-firmware.ps1 -Set Both -Extract
```

The execution-policy option applies to this process, not a permanent policy
change. The helper was checked with Linux PowerShell 7.7.0, including a ZIP64
member exceeding 4 GiB, hash rejection and partial-file preservation. Windows
PowerShell version on the owner PC was not collected; E18 confirms that Windows
downloads and all APP extractions completed. Firmware
signatures and phone rollback acceptance are separate from these integrity checks.

The Android-9 attempt above failed before a successful downgrade. Keep the phone
in normal Android while analyzing the metadata/protocol refusal. Prepared files
are research inputs, not a validated flash or restoration procedure.
