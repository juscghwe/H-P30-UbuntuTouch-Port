# Unlock feasibility: software-only scope

Research date: **2026-11-12**, Europe/Berlin. Evidence catalog: [R01–R15](../raw/2026-11-12/01-research-sources.json). Owner constraint: [software-only research](../raw/2026-11-12/02-owner-constraint.txt).

## Decision

**No verified, complete software-only persistent-unlock procedure has been established for this phone, now owner-reported on EMUI 10.0.0 / 10.0.0.562(C431E15R2P7).** The earlier Settings build was 12.0.0.262(C431E3R2P2). This is a limit of the evidence found, not proof that no such method exists. Do not prescribe a further firmware change merely because an older generic unlock guide exists.

The owner has ruled out opening the phone for now. Physical test-point routes remain background evidence only. No tool was run against the phone, and no executable or firmware was downloaded during this research.

## Why downgrade is discussed

Ubuntu Touch does not intrinsically require EMUI 9.1. The relevant requirement belongs to specific persistent-unlock procedures. In the HCU workflow, the vendor explicitly requires Android 9; support-mode access on newer firmware can coexist with a normally locked bootloader. An ordinary cold boot into the custom system is the eventual acceptance criterion, not a transient service-tool status.

## Owner follow-up: 2026-11-13

[E13](../raw/2026-11-13/01-firmware-and-hisuite-offer.txt) again reports
`MAR-L21A 10.0.0.275(C431E8R2P7)`, Android 10, VNDK 29 and kernel 4.14.116.
These values also appeared under the earlier EMUI 12 state. In a later, separate
Settings report the owner confirms **EMUI 10.0.0 / build
10.0.0.562(C431E15R2P7)**, Kirin 710, 4 GB RAM and kernel 4.14.116. This establishes
the rollback result as owner-reported; preserve the differing ADB base identifier
as a separate observation. No persistent unlock has been demonstrated.

The owner reports no Android-9 rollback option. The supplied HiSuite screen
offers `12.0.0.232(C431E3R2P2)` with an Update button. Its release note describes
rollback from that offered system to EMUI 10, not a further Android-9 path.
The screen establishes what this view offers, not that every official rollback
path is impossible. A [targeted .562 follow-up](../raw/2026-11-13/03-unlock-followup.json)
finds that Huawei's generic guide presupposes the missing version-switch option,
while HCU still requires Android 9. A separate firsthand .562 P30 Lite report
describes downgrade failures, without a verified success in the retrieved replies.
The software-only unlock chain remains unresolved; neither
an ordinary DC-Unlocker purchase nor a forced package substitution is supported
by this result. No further rollback is needed solely to recapture firmware.

The vendor's software-testpoint guide permits some Android-10/EMUI-10 entry
paths, explicitly without a guarantee. That statement does not override HCU's
separate Android-9 requirement for a normally unlocked bootloader. Historical
release notes advertising Android-10 services describe other service features;
they do not establish persistent unlock on this .562 build. Attempting HCU on
Android 10 would therefore be outside the documented unlock prerequisite, not
a supported route inferred from successful service-mode detection.

## Evidence assessment

### Additional source reviews and owner fastboot query

[E15](../raw/2026-11-13/06-fastboot-state.txt) confirms that normal fastboot still
reports `locked` after the EMUI-10 rollback. A repeated-U unlock request returns
`invalid command`, not a successful unlock. Its nonnumeric argument and the lack
of a known-valid code prevent attributing that result specifically to a removed
command or a rejected argument. FRP remains unknown. A visible OEM-unlocking
permission switch is not evidence of a bootloader unlock or additional ADB access.

[Read-only candidate audits](../raw/2026-11-13/07-software-unlock-link-audit.json)
establish the following narrower findings:

| Candidate | Inspected mechanism and limitation |
| --- | --- |
| ClashLuke/Huawei-Bootloader-Unlocker, pinned `5ec950f` | Executes a fastboot unlock command for sequential integers. No extraction, code-generation shortcut or verification bypass appears in its C source. |
| Computer Bild / PhoneRescue root article | Generic rooting claims, without a demonstrated MAR-LX1A/.562 exploit or persistent-unlock procedure. Root access could be a research input but is a separate result from custom-boot authorization. |
| Historical repeated-U guide | March 2014 firsthand Ascend-model tests; later clarification excludes newer devices. It does not supply a P30 Lite universal code. |

A basic string scan of the official reference FASTBOOT record was inconclusive;
it does not establish current command support or explain the rejection. No
candidate executable or repeated guessing loop was run by the research environment.

| Route / source | What is supported by the evidence | Remaining gap |
| --- | --- | --- |
| HCU + DC Phoenix software test point (R01–R03) | HCU documents Android 9 and either software/hardware TP. MAR-LX1A is listed. DC Phoenix offers an ADB-based software-TP path, but documents limited firmware support and no guarantee. | No supported no-opening entry/downgrade/exit chain demonstrated for .262; paid service required; Android version and EMUI label must both be considered. |
| Same-model vendor forum (R05) | C431 Android-10 owner reports a nonpersistent result; support advises downgrade and owner later reports success. | Old .197/.275 environment, no complete modern .262-to-9.1 package chain. The brief success reply does not independently establish all steps or long-term persistence. |
| Same-model failure report (R04) | In 2025, owner reports DC Phoenix software TP and HCU claiming unlock, followed by a locked normal fastboot screen. Support points to Android version; later downgrade attempt fails. | Not a working recipe; precise firmware chain unverified. |
| Same-model C431 report (R06) | Owner starts at EMUI 12 .251, uses physical TP, installs 9.1.0.399, and reports an Android GSI boot. | Different starting build from ours and requires opening phone; outside current owner constraint. |
| Remote commercial service (R07) | Provider explicitly lists MAR-LX1A and EMUI 9.1, with a USB/remote service description. | It does not validate .262 or supply the missing no-opening downgrade procedure. No purchase/contact performed. |
| Kirin-Tool (R08) | Original project supports the SoC and contains separate service-loader, software-TP and normal unlock operations. | No observed .262 persistent unlock. Feature names are not end-to-end compatibility evidence. |
| Broad universal-toolkit claims (R09) | README asserts broad firmware support; inspected module dispatches OEM memory-write requests and reports command return status. | No demonstrated target-build success or reboot-persistence test. Not accepted as a verified shortcut. |

## First-party requirements and constraints

[HCU's own instructions](https://hcu-client.com/huawei-bootloader-unlock-via-testpoint/) require Android 9 for the documented unlock and a timed account or activated dongle. Its [model table](https://hcu-client.com/supported-models.php) separately warns that software TP can fail on Android 10 and newer. A supported-model row does not override these firmware caveats.

[DC Phoenix's instructions](https://www.dc-unlocker.com/dcphoenix-enable-software-tp) describe support through Android 10/EMUI 10, sometimes requiring an earlier downgrade. They offer ADB, fastboot and update-mode methods; firmware files may be needed, and entry is not guaranteed. Our EMUI 12/Android 10 combination must not be presumed eligible merely because its Android API is 29. The [exit procedure](https://www.dc-unlocker.com/dcphoenix-disable-software-testpoint) is also necessary research before any attempt.

The [2021 C431 thread](https://forum.dc-unlocker.com/forum/modems-and-phones/huawei/193989-enable-testpoint-p30-lite-emui-10-0-0-1) is useful evidence of the persistence issue. The [2025 failure report](https://forum.dc-unlocker.com/forum/modems-and-phones/huawei/199602-huawei-p30-lite-mar-lx1a-unsuccessful-bootloader-unlock-kirin710_p1_v2) shows that a service-tool success message is insufficient. These pages were available as search-indexed text; direct retrieval timed out. No personal forum device identifiers are retained.

## Scope of the same-model report

[CatWithCode's firsthand report](https://catwithcode.moe/Blog/2026.08.06_P30_Lite_Root/P30_Lite_Root.html) is the closest model/customization match found, but it is not a software-only example. It is useful as evidence that the handset family has been modified; it cannot establish suitability for our current build or eliminate the opening requirement. Its linked XDA procedure and post could not be read during this research (HTTP 502/403), so their full details remain unreviewed.

The [service provider description](https://ministryofsolutions.com/huawei-p30-lite-bootloader-unlock-mar-lx1a-lx1m-lx2a-lx2b-lx3a-al00/) is model-specific but older and commercially supplied; its claims are not an independent test on the owner's device. No current pricing or reliability recommendation is made.

## What static source review establishes

The [original Kirin-Tool repository](https://github.com/kethily-daniel/Kirin-Tool) was inspected by reference, without execution or copying its source into this repository. Its software-TP operation modifies and flashes an xloader from a supplied firmware package. Its unlock UI ultimately invokes an OEM unlock request; its loader operation supplies a service environment. This separates mechanisms but supplies no firmware-specific success proof. We have not audited the complete tool or verified its binaries.

The [other toolkit](https://github.com/FrgfA4ftfzTdfyyyr5f6tESD3/huawei_kirin_toolkit) likewise has not been tested or audited. No proposed OEM memory writes, xloader modifications or unknown unlock payloads are recommended for execution from the current evidence.

## Current recommendation and next evidence needed

### Additional same-model downgrade failure

[HiSuite-Proxy issue #94](https://github.com/ProfessorJTJ/HISuite-Proxy/issues/94) reports MAR-L21A C431 moving from 10.0.0.470 to 10.0.0.167 but failing to install both 9.0.1.120 and 9.1.0.399. No later P30 Lite success is recorded in the inspected comments. [Selected excerpts](../raw/2026-11-12/06-downgrade-report.json) retain the important correction: another participant's eventual official-HiSuite downgrade success was on a **P20 Pro CLT-AL00**, not this model. That participant's earlier fuse/underlying-data explanation was speculation and was subsequently questioned by their own result; it does not establish the P30 Lite's anti-rollback mechanism or an exact firmware threshold.

This strengthens the reason to verify the entire chain: an accepted Android-10 downgrade does not demonstrate an accepted Android-9 downgrade. It neither proves the current phone cannot be downgraded nor supplies a procedure for doing so.

### Exact-build service claims remain insufficient

An additional [Octoplus service-report thread](https://forum.gsmhosting.com/vbb/f1053/p30-ele-l09-unlock-first-octoplus-2900885/index27.html) contains MAR-LX1A / C431 `.262` direct-unlock reports. The recorded operation starts from Huawei USB COM service mode and does not demonstrate software-only entry, a persistent normal-fastboot unlock after reboot, or a custom-image boot. The vendor [lists direct unlock and bootloader lock/unlock as separate operations](https://octopusbox.com/eng/news/details/854). A service-mode FB-unlocked field or an operation named “unlock” does not close the persistent-bootloader evidence gap. No tool or package was downloaded or run from these reports; personal identifiers and full service logs are excluded.

### Remaining requirements

Keep the current stock firmware while investigating. The screenshot proves an official offer of 10.0.0.562(C431E15R2P7), not that this version permits software TP or a subsequent Android-9 downgrade. Matching package names in old posts are insufficient to authorize a modern downgrade.

A credible software-only candidate must establish all of the following for MAR-LX1A C431 and the actual firmware chain:

1. Entry into the required service mode without opening the phone.
2. A compatible Android-9 downgrade, if that unlock procedure requires it, with available matching packages and a restoration path.
3. The persistent unlock operation and a supported way to leave service mode.
4. Normal fastboot reporting unlocked after reboot and an independently bootable custom kernel, not only a transient flashing session.

The most useful next external confirmation would be from the tool vendor about the exact starting build, the offered .562 intermediate build, whether disassembly is ever required, and recovery/exit requirements. No vendor was contacted: the owner's instruction authorized research, not sending messages. Do not purchase a license based only on a model list.

This investigation narrows the reason for downgrading but does not turn the earlier generic rollback recommendation into a verified installation procedure.
