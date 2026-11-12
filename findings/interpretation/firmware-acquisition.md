# Official firmware acquisition

Stock `kernel`, `ramdisk`, `dts` and `dto` block nodes are mode `0600` (E10).
Ordinary ADB cannot extract them. A matching original update archive remains
the preferred source for offline image/header and board-data inspection.

The Huawei P30 Lite support page exposes no verified firmware archive in this
inspection. HiSuite's update workflow couples download/install/restart; do not
start an update or rollback solely to obtain a file. The existing .562 offer is
a different firmware base from the retained .262/.275 observations.

The two inspected owner-side SystemUpdate logs contain no HTTP/URL text. Their
empty URL search is not evidence of a regex failure or unavailable firmware.
Client version 14.0.0.380_OVE is reported by the owner. Its official installer
matches Huawei's published SHA-256; static inspection finds OpenSSL 3 imports
and a decompression export. Its 32-bit `HiSuite.exe` manifest requests
`requireAdministrator`; ordinary-user Frida attachment failed before agent
readiness. The observer therefore needs matching administrator access. The
downloaded installer was unpacked as data, never executed in the research environment.
See the [source observations](../raw/2026-11-12/08-hisuite-static-inspection.json).

An [experimental URL observer](../../scripts/hisuite-capture/README.md) uses those
incoming-buffer interfaces without modifying certificate validation. The filter
and synthetic callbacks pass offline tests; **successful Windows attachment and
actual package capture remain unverified**. Python and the older HiSuite client are not
required. It must be stopped rather than advancing to Update/Restore/Rollback
if viewing version offers produces no URL.

HiSuite-Proxy is not selected: its historical certificate-validation patch
conflicts with preserving TLS verification. WinHTTP tracing is not selected
because the inspected HTTP component imports OpenSSL directly; this does not
establish that every component avoids WinHTTP.

The selected next approach is acquisition of an original archive from verified
distribution metadata, without process instrumentation. A Python interface to
Frida would retain its process-attachment mechanism.

Any resulting CDN link still requires manifest/package inspection, model and
customization matching, hashes and licensing review. A downloadable package is
neither an unlock route nor permission to flash. Keep proprietary archives
outside the public checkout.
