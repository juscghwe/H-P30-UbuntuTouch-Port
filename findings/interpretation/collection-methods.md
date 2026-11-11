# Collection commands and limitations

Device outputs were collected in Windows PowerShell from the official Android Platform-Tools directory and supplied for analysis. No direct USB access was used for source analysis. An administrator shell was not established as necessary.

## Initial setup

Download Windows Platform-Tools from Google's official page. Extract it, open PowerShell in the directory containing `adb.exe` and `fastboot.exe`, enable Developer options and USB debugging on the phone, connect a data-capable cable, and accept the USB debugging authorization prompt. HiSuite/Huawei drivers may be needed separately for Windows fastboot access. HDB is HiSuite's authorization mechanism, distinct from ADB.

```powershell
.\adb.exe version
.\adb.exe devices
```

Device serials in enumeration output must be removed before sharing/committing. Successful ADB access does not establish successful fastboot access or an unlocked bootloader.

## Firmware identity

The following one-line query produced E02:

```powershell
'ro.product.model','ro.product.device','ro.board.platform','ro.build.display.id','ro.build.version.release','ro.build.version.sdk','ro.build.version.emui','ro.product.cpu.abilist','ro.treble.enabled','ro.vndk.version','ro.vendor.build.fingerprint' | ForEach-Object { "$_ = $(& .\adb.exe shell getprop $_)" }; .\adb.exe shell uname -a
```

This intentionally queries selected properties instead of dumping all properties, which could include private identifiers. Firmware fingerprints are technical build identifiers; retain only after inspection.

## Bootloader inspection

```powershell
.\adb.exe reboot bootloader
```

After the fastboot/rescue screen appears:

```powershell
.\fastboot.exe devices
.\fastboot.exe oem get-bootinfo
```

Return to Android:

```powershell
.\fastboot.exe reboot
```

Reboot changes the current operating mode but does not itself flash/unlock/erase. The lock query is read-only. Initially the combined enumeration/query command waited for a device. After Windows fastboot access worked, the query returned locked. Do not infer FRP status from PHONE Locked.

## First hardware probe: known failures

The initial probe attempted `/proc/bus/input/devices`, SurfaceFlinger with an Android-side quoted alternation filter, `/proc/modules`, `/sys/class/net/wlan0/device/driver`, selected vendor library directories, and `/proc/config.gz` metadata. E05 preserves the outputs.

Android denied proc input access. The remote graphics filter's quotes did not survive the PowerShell/ADB/shell chain, causing EGL/HWC command errors. Missing symlink paths are inconclusive. The module list is not a complete inventory of built-in or active hardware drivers.

## Corrected graphics probe and config retrieval

```powershell
.\adb.exe pull /proc/config.gz .\p30-stock-config.gz; "--- Graphics ---"; .\adb.exe shell dumpsys SurfaceFlinger | Select-String -Pattern 'GLES:|EGL implementation|HWC version'; "--- Input hardware ---"; .\adb.exe shell dumpsys input | Select-String -Pattern 'Name:|Path:|Vendor:|Product:'
```

E06 records the returned excerpts. Filtering runs on Windows, avoiding the earlier nested-shell quoting problem. The initial input filter returned only paths. Use `adb pull` for binary files; avoid redirecting binary stdout through Windows PowerShell text pipelines.

## Follow-up input filter and sanitation

The command that produced E07 was:

```powershell
.\adb.exe shell dumpsys input | Select-String -Pattern '^\s*(Device\s+)?-?\d+:|^\s*Identifier:|^\s*Location:'
```

It matched the desired device headers but also numbered window/channel lines later in the dump. Only the physical/virtual device inventory before the first window record was retained. Application/window names, object handles, process/user identifiers, focus state and channel records were omitted.

For future collection, restrict capture to the device inventory before UI/window/channel sections and review the result before sharing. Do not collect another broad dump solely to repeat an already answered question.

## HiSuite offer inspection

With Android running, authorize HiSuite/HDB, choose System update / Systemaktualisierung, then Switch to other version / Zu anderer Version wechseln. Reading the offered version does not perform a rollback. E04 is a transcription of the offer only. Actual rollback erases data and requires the supported model/region/firmware sequence and sufficient charge; the screenshot states more than 50%.
