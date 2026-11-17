# Android Utility USB Upgrade readiness

Status: **static preparation only; no phone test**. This is not a validated
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
identify the real format. No bundle program or driver was executed.

The main `AndroidUtility.exe` is a 32-bit Windows PE with no embedded Authenticode
certificate. Its actual PE-resource manifest requests administrator rights.
Its static UI string identifies `v200.01.0001:01:01:2026` Offline; this has not
been observed at runtime. Source provenance, a matching hash and archive CRCs do
not establish binary safety. An isolated Windows environment is preferable for
the first application launch; retain existing antivirus protections.

## Staged observations

1. Inspect the application's version and Huawei/Flasher controls with the phone
   disconnected. Preserve a cropped view of the relevant controls without PC
   identity or unrelated windows. Do not start an operation or install bundled
   chipset drivers merely to inspect the interface.
2. Identify USB Upgrade/DLOAD mode and its exact controls. Static strings confirm
   separate Upgrade/DLOAD and Fastboot labels, plus a message requiring an update
   base file for a transition. They do not prove which validation checks apply
   to each path or that a mode transition is independent of a write operation.
3. Before a write test, finish inspecting the intended base/CUST/PRELOAD set and
   recovery materials for the currently retained firmware. The [Android-9
   availability probes](firmware-acquisition.md) do not validate the full base
   and PRELOAD payloads, their signatures or the phone's rollback acceptance.
4. Treat an application success message separately from a running phone result.
   A failed full-firmware downgrade can prevent Android from booting and require
   a different recovery path. Do not infer that reconnecting or replacing the
   battery will restore overwritten boot-chain partitions.

Normal Fastboot partition writing and temporary Factory Fastboot are distinct
operations. No testpoint, guessed unlock code, partition erase, bootloader patch
or signature-check modification is part of the initial interface inspection.
