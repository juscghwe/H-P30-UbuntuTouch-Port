# Android Utility USB Upgrade readiness

Status: **owner-observed mode entry and automatic return to Android; no firmware-write test**. This is not a validated
`.562` to Android-9 downgrade recipe.

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

## Next implementation step

Compare the two partition tables and the recovery validation paths against these
exact package inputs. Prepare host-side files and hashes before a firmware-write
test. A mode-entry success is insufficient reason to load a factory bootloader,
change partition tables or bypass a version check. Keep firmware binaries and
full build/download outputs outside this repository.
