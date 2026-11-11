# Privacy and sanitation review

## Retained

Technical model/codename/SoC identifiers, firmware/customization versions, generic build fingerprints, generic kernel build identity, GPU build strings, device-node paths, module/library filenames, zero-valued hardware vendor/product IDs, and the stock kernel configuration. These are needed to compare sources and firmware.

## Removed or excluded

- USB/ADB/fastboot device serials are replaced with `[REDACTED_DEVICE_SERIAL]`.
- Personal Windows usernames and absolute Downloads paths are omitted; commands are shown relative to the Platform-Tools directory.
- The latest input capture included unrelated application/window/activity names, object handles, process/user IDs, focus state and input-channel records because the filter was too broad. The entire trailing UI section was omitted rather than publishing it with partial redactions.
- Original pasted attachments, raw screenshots and gzip container metadata are not committed. The kernel configuration payload is retained as reviewed text.
- No IMEI/MEID, network MACs, SSIDs/passwords, authentication tokens, private keys, account credentials or phone userdata are intentionally included.

## Normalization and integrity

Text captures have normalized LF line endings; chat transport escapes and wrapping artifacts are not reproduced as literal device output. Owner-reported transcriptions and screenshot selections are labeled as such, not presented as direct machine captures. No missing output was invented.

The stock configuration payload is preserved byte-for-byte from gzip decompression after inspection of fields that can contain paths/identifiers. `CONFIG_MODULE_SIG_KEY="huawei_signing_key.pem"` is only a generic filename; no signing key is present. Original and decompressed config SHA-256 values are recorded in provenance.

SHA256SUMS covers the committed sanitized evidence and provenance. A successful scan is a review aid, not a guarantee that future uploads are safe. Review every future capture before staging. `.gitignore` excludes common unreviewed/build/binary paths but cannot enforce privacy on text.
