# HiSuite download snapshots

`watch-hisuite-downloads.ps1` targets Windows PowerShell 5.1 without Python,
administrator access, process attachment or network interception. Start it before
an owner-selected HiSuite download. It neither starts nor cancels a phone operation.

```powershell
& .\watch-hisuite-downloads.ps1
```

Leave the window running during the download. Ctrl+C stops only this watcher.
Default output is a timestamped `Downloads\P30-Firmware-Capture-*` folder. Allow
space for both HiSuite's download and the copies; renamed sources can produce
duplicate copies. Watch free space during use.

Candidates include Documents/HiSuite/ROM, common per-user/system HiSuite folders,
and recognizable Huawei packages in temporary/download directories. Locations
are candidates, not a confirmed HiSuite 14 storage contract. Backups, directory
links and the destination subtree are excluded. Generic temporary files require
a Huawei package marker. An optional `-WatchPath 'D:\custom-cache'` replaces the
default roots when a different download location is known.

The watcher uses short shared reads, appends growing files and periodically reads
them again to handle preallocation or rewriting. It does not retain source handles
between chunks. Locked files may remain unreadable; fast cleanup or a source change
during copying can leave an incomplete or inconsistent snapshot. The `.capture`
suffix deliberately does not imply a complete ZIP or image. Match size and SHA-256
against the corresponding Huawei manifest before extraction or use. Copy success
does not authenticate a firmware signature or establish rollback compatibility.

`capture-index.json` records original local paths and read errors. Keep the entire
capture folder private; do not commit it or upload the index as a diagnostic log.
The watcher uploads nothing. It does not change antivirus or execution policies.
If local policy blocks it, retain the block and report the error.

Validation: `python3 scripts/check-hisuite-watcher.py --pwsh /path/to/pwsh` uses
synthetic packages and temporary folders. This checks copying and exclusions on
the available PowerShell runtime; it does not validate Windows locking behavior
or guarantee discovery of a particular HiSuite download.

Validated with PowerShell 7.7.0 on Linux: growing and truncated files, rewritten
preallocated content, more than eight candidates, UPDATE.APP magic at offset 92,
exclusion of backups and an unrelated ZIP, and a real 4 MiB read from a sparse
3,199,657,640-byte input. Both arguments to the read-size minimum are explicitly
64-bit: mixed integer types previously selected a 32-bit overload and raised
`MethodException` before reading the base ZIP. Windows PowerShell 5.1 is the
syntax target; a Windows runtime test remains pending.
