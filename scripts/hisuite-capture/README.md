# Experimental HiSuite package URL observer

Purpose: obtain an official firmware package URL for **offline inspection** when
HiSuite's existing logs contain no URL. Requires Windows 10/11 with `curl.exe`,
Windows PowerShell, and an already installed HiSuite 14.0.0.380_OVE. Python is
unnecessary. HiSuite 14's executable manifest requests `requireAdministrator`;
run the helper from PowerShell opened with **Run as administrator**, using the
same Windows account as HiSuite. The launcher checks this before downloading.

## Status and limits

**No successful Windows attachment yet.** Owner attempts from ordinary PowerShell
returned `Process not found` by name and `Unable to access process` by PID, before
any agent readiness was confirmed. Offline tests cover
the URL filter and synthetic hook callbacks, not Frida injection, the actual
updater response, or successful firmware acquisition. An offer may not disclose
a download URL until a later workflow step; do not initiate an update to obtain it.

The agent temporarily instruments `SSL_read`, `SSL_read_ex` and the exact x86
`AppBaseHttpClient::UnGzip` export. It reads incoming/decompressed buffers and
never changes arguments, return values, requests, responses or certificate
validation. This is debugger attachment to the PC application and can disrupt
it. Use only while viewing offers, with no transfer/update in progress.

Only Huawei `dbankcdn`/`hicloud` package paths beginning `/TDS/data/files/` or
`/download/data/` are printed. Credentials, query strings and fragments are
excluded; other contents are discarded. Bounded stream tails stay in process
memory for the observation window. There are no memory dumps or raw traffic logs.
Compressed responses through other decompression paths, UTF-16 and unsupported
URL forms may be missed. Empty output establishes no firmware availability claim.

## Run

1. Save `capture.js` and `run.cmd` in a new folder outside any public checkout.
2. From an administrator PowerShell window, run `run.cmd`. It downloads hash-pinned official portable 7-Zip and Frida
   tools into that folder, verifies them before execution, and pauses.
3. Open the existing HiSuite normally, connect the phone and reach its home
   screen. Resume the helper by pressing a key in its window.
4. Look for `ACTIVE` and `READY` lines. Reopen only the view listing available
   versions. **Do not start Update, Restore or Rollback.**
5. Copy only `PACKAGE_URL` and `READY` lines. The agent removes its observers
   after five minutes (`STOPPED`). Close HiSuite to end the attachment, or close
   it sooner to stop. The helper does not preserve itself after process exit.

If attachment is still denied from that administrator window, no hooks appear,
or security software blocks the tool, stop and report the short error. Do not
disable protection or change certificate settings. Native CLI errors may contain private
paths or crash reports; do not publish a full console dump.

No client installer, root certificate, service, phone command, flash or recovery
operation is included. Downloaded executables remain outside this repository;
remove the local helper folder when finished. Tool license notices/source links
are provided by the upstream [7-Zip](https://github.com/ip7z/7zip/tree/26.06) and
[Frida](https://github.com/frida/frida) projects; the 7-Zip archive includes its
license. Sources and hashes are in `run.cmd`.

## Reproduce the offline checks

```sh
node scripts/hisuite-capture/check-filter.js
```

The Frida API and CLI are documented in the
[JavaScript API](https://frida.re/docs/javascript-api/) and
[`frida-inject` source](https://github.com/frida/frida-core/blob/main/inject/inject.vala).
The observer supports only the inspected 32-bit Windows client ABI and refuses
other architectures/process names.
