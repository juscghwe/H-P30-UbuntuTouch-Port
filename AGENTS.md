# Project conventions

- Keep project findings in `/findings/raw` and `/findings/interpretation`.
- Raw evidence must be sanitized before staging. Remove device serials, IMEI/MEID, MAC addresses, SSIDs, network credentials, personal Windows paths, account details, input descriptors/unique IDs, and unrelated app/window/activity data. Retain technical model, firmware and driver identifiers.
- Preserve supplied output faithfully except documented redactions, omissions and line-ending normalization. Do not put conclusions or reconstructed output into raw evidence without labeling its origin.
- Distinguish observed runtime hardware, enabled kernel support, third-party claims, hypotheses and proposed actions. Link conclusions to their evidence.
- Record commands, failures and corrections. Do not mark a downgrade, unlock, build, flash or hardware test complete without evidence.
- Device evidence is collected with Windows Platform-Tools. Record collection commands and distinguish device output from source analysis.
- Use Conventional Commit prefixes and review staged evidence before committing.
