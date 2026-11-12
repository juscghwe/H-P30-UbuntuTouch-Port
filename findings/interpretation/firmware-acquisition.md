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

## Live catalog and manifest results

Direct data inspection of FirmFinder at
[`a324a862`](https://github.com/ProfessorJTJ/professorjtj.github.io/tree/a324a862c60764e84d398fe7b641e67b1873344c)
found two relevant root-catalog rows. Both listed Huawei hosts serve their
`full/filelist.xml` over HTTPS with normal certificate validation:

| Catalog ID | Catalog model/customization | Base label | Manifest package size |
| --- | --- | --- | --- |
| 442187 | MAR-L21A / C431 / hw-eea | MAR-LGRP2-OVS 10.0.0.275 | 3,791,534,847 bytes |
| 639061 | MAR-L21A / C431 / hw-eea | MAR-LGRP2-OVS 10.0.0.562 | 3,199,657,640 bytes |

Both manifests return HTTP 200 and name `update_full_base.zip`, with SHA-256
hashes. Exact catalog pins, input/output hashes, selected rows and live manifest
observations are [recorded separately](../raw/2026-11-12-firmware/01-catalog-and-manifests.json).
The manifests establish available metadata. The catalog's model/region labels
remain third-party claims pending inspection of package contents.

The independent [catalog decoder](../../scripts/inspect-firmfinder-catalog.py)
parses saved data without executing website JavaScript. Full JSON validation
passes for all four catalogs: root 40,691 rows; BaseArchive 32,375; Downgrade
4,089; v2 19,774. Decoding includes the LZW dictionary reset needed by large
catalogs. [Fixtures](../../scripts/check-firmfinder-decoder.py) cover that boundary
and exact version/customization selection.

Save input catalogs and firmware outside this checkout. Example inspection:

```sh
python3 scripts/inspect-firmfinder-catalog.py /path/outside/checkout/catalog.hash --model MAR-L21A --customization C431 --version 10.0.0.275 --version 10.0.0.562
```

## Verified .275 reference archive

The 3,791,534,847-byte archive downloaded from Huawei over verified HTTPS and
matches the manifest SHA-256
`60e8983f148e29027af1bc921d6ed0de5f65752ee423d93d008cf9153831f1a4`.
`VERSION.mbn` identifies `MAR-LGRP2-OVS 10.0.0.275`; `SOFTWARE_VER.mbn` separately
says `MAR-LGRP2-OVS 10.0.0.1`. Neither is silently substituted for the other.
No updater binary or script was executed.

`UPDATE.APP` extracted with ZIP CRC verification: 4,621,458,336 bytes, SHA-256
`b7a78fa69e62d9ef444f1e1fc9397502c85b0d7c6dfc028dff7e7f4a1ea30737`.
The independent [APP inspector](../../scripts/inspect-update-app.py) validates
46 record bounds after a 92-byte zero preamble. Selected images were copied to
private storage. Huawei signatures and internal record checksums are unverified.

The reference GPT header and entry-array CRCs pass. All seven selected partition
numbers agree with E10; reference sizes include kernel 24 MiB, ramdisk 2 MiB,
dts 8 MiB and dto 24 MiB. This does not authorize using its offsets or table to
modify the handset.

Observed image formats:

- `KERNEL`: an uninterpreted 4,096-byte prefix, then Android boot header v1,
  page size 2,048, and an 18,655,580-byte gzip kernel. Decompression passes and
  the payload reports Linux 4.14.116.
- `RAMDISK` and `RECOVERY_RAMDISK`: Android boot headers v0, page size 2,048.
- `DTS`: an HSDT v1 table at offset 4,096 with one compressed base FDT. Gzip CRC,
  numeric FDT bounds and native DTC decompilation pass.
- `DTO`: an Android DT table v1 at offset 4,096, with 366 gzip entries. All pass
  gzip CRC and numeric FDT-header bounds. The earlier v0-only image inspector
  correctly rejected this table; the separate
  [container inspector](../../scripts/inspect-dt-containers.py) handles v1.

One inspected overlay (index 3, ID 7844) contains `synaptics_tcm`, a static
`hi110x,subchip_type="hi1102"` property and a Marie AL00 INI path. **It is an
example, not the selected C431 handset overlay.** Multiple board IDs and panel
alternatives are present. The active panel, Wi-Fi variant and bootloader overlay
selection remain unresolved.

The archive kernel embeds a different configuration: SHA-256
`49ea2e02650dcc5a5525f6bade77a7e00c4dfb3518f82362ba13a174970119be`.
Against retained runtime stock, 4,595 common symbols agree, 35 differ, 682 are
stock-only and 269 reference-only. Battery information/temperature/type and
SCHARGER_V600 are enabled in retained stock but disabled in this older reference.
Do not replace the retained stock config or adopt those power settings.

[Image observations](../raw/2026-11-12-firmware/02-reference-image-inspection.json)
and the [complete literal config comparison](../raw/2026-11-12-firmware/03-reference-config-comparison.json)
contain exact hashes, offsets and limitations. These are offline source inputs,
not a device-validated kernel, boot package, unlock route or flash instructions.

Any resulting CDN link still requires manifest/package inspection, model and
customization matching, hashes and licensing review. A downloadable package is
neither an unlock route nor permission to flash. Keep proprietary archives
outside the public checkout.
