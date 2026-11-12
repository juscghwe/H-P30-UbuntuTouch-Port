# Baseline source validation

Source: Enjoy 10 / HarmonyOS 2 kernel at `c1e2747d8e839bedaa71a6436d24a51285d98509`. This is a research baseline, not a validated MAR-LX1A kernel. [Measured inputs and results](../raw/2026-11-12-build/01-source-and-config-validation.json) distinguish source/configuration checks from compilation and device testing.

## Provenance and compiler

The pinned source archive reconstructs upstream tree `2d661ac5023d56fd2e8b60f9803042158fc65757` and the exact pinned commit object. Source files are unchanged. The README's Clang `r353983c` is Android Clang 9.0.3, build 5484270. Its Android-10 release prebuilt and the Android GCC 4.9 tools were downloaded at pinned commits from AOSP; archive hashes are recorded with the inputs.

AOSP's compiler wrappers expect a `python` executable, absent in the build container. The recipe selects the unchanged native `clang.real`/`clang++.real` executables explicitly. The GCC 4.9 native binary reports `4.9.x 20150123`; its assembler/linker tools supply the cross-toolchain. No compiler fallback to GCC 12 is used for the baseline kernel.

## Kconfig: passed without patches

`merge_kirin710_defconfig` and stock-derived `olddefconfig` both exited 0. The only observed parser warnings concern CR characters in `drivers/huawei_platform/blpwm/Kconfig`; [the log](../raw/2026-11-12-build/04-kconfig.log) retains them.

The literal `-source` entries are **supported Huawei syntax**, not a demonstrated source defect. `scripts/kconfig/kconf_id.c` recognizes `T_EXISTSOURCE`; `zconf.y` calls `zconf_if_exist_nextfile()`, which skips missing files. The shipped generated parser contains the same extension. Replacing these entries with `source` would change their meaning and make absent optional directories fatal.

## Configuration coverage

The earlier literal comparison remains reproducible: 5,264 equal shared symbols, 13 different, 35 stock-only and one candidate-only. Definition search now separates those 35 entries into 17 with Kconfig definitions and 18 without. [Complete coverage](../raw/2026-11-12-build/02-stock-defconfig-coverage.json) records paths and line numbers.

| Area | Finding | Consequence |
| --- | --- | --- |
| Battery temperature | `HUAWEI_BATTERY_TEMP` and child `HUAWEI_MULTI_BTB_TEMP` exist; parent is disabled in candidate | Stock-only child is explained by configuration, not missing driver code |
| Battery identification | Battery-type selection and both PL061 onewire variants exist but candidate disables them | Preserve and inspect stock behavior before power bring-up |
| Charging | SC8545 and SM5450 definitions and drivers exist but are disabled; HL7139 has no definition or matching reference | Candidate is incomplete relative to configured stock support; active charging IC remains unmeasured |
| Audio | `HIFI_VIR_DAI` exists but is disabled; six `HWEVEXT_*` options have no definitions/references | External codec support cannot be restored merely by copying config values |
| Touch | Synaptics TCM exists; stock-only Himax-64 and Omnivision TCM options have no definitions | Missing alternative families do not contradict the observed Synaptics identifier |
| Module signing | Stock-only signing children exist behind `MODULE_SIG`, disabled in candidate | Existing stock modules are not assumed compatible |

More significantly, normalizing the **complete stock config** removes 66 explicit entries and adds one, with all 5,246 retained shared values unchanged. Of those removed entries, 65 have no Kconfig definition in this tree. Several were already present in the candidate's literal defconfig, so the earlier 35-entry difference did not reveal them. Lost stock-enabled entries include Huawei-specific TCPC/HI6526 and USB-PD controls, root/TEE measurement interfaces, DPM and Gator. Other Type-C/PD implementations, including Richtek RT1711H, remain configured; this does not identify the active controller. One removed entry, `CORESIGHT=n`, has a definition but is omitted under its dependencies. [The normalization record](../raw/2026-11-12-build/03-stock-normalization.json) is the complete list; absence from generated config must not be silently treated as preserved functionality.

The stock input remains byte-for-byte identical to E08. Candidate-pristine, stock-derived and Halium-probe outputs use separate directories. No signing key or proprietary binary is committed.

## Executed build results

- **Pristine candidate:** object compilation reached `LTO vmlinux.o`. The GNU-gold/LLVMgold linker was killed with status 137; make exited 2. The enclosing 8 GiB cgroup recorded an OOM kill. No `Image.gz` or complete module build resulted. The container requested a 6 GiB limit, but the observed enclosing limit was 8 GiB; requested limits are not presented as measured enforcement.
- **Unchanged stock-derived signing:** `certs/` failed because its Huawei-key branch expects `extract-cert` inside an Android product output directory. A diagnostic path-only correction reached the next missing dependency, `vendor/huawei/chipset_common/build/signkernel/signing_key_v11.x509`. That diagnostic patch is not selected for the build recipe.
- **Development signing:** changing only the key filename to `certs/signing_key.pem` allowed the unchanged source's certificate stage to pass. The key was generated locally outside this repository. Forced signatures, automatic signing, SHA-512 and module versioning remained enabled. This is a new trust root, not stock-module compatibility.
- **Stock-enabled driver probes:** battery temperature, battery-type identification, PL061 onewire, HiFi virtual DAI, SC8545 and SM5450 directory builds all passed. These are object/archive checks, not working-device tests or a complete stock-derived kernel.

The alternate LLD experiment uses the documented Clang prebuilt's linker with `--lto-O1`, retaining the candidate LTO/CFI config. An AArch64 bitcode link probe passed. Kernel preparation then rejected LLD through a GNU-gold-specific version check, despite Kconfig documenting both linkers. [The two-line build patch](../../patches/0001-build-allow-lld-for-lto.patch) exempts detected LLD from that gold parser while retaining the Clang check. Its kernel link also exhausted memory and was killed at `LTO vmlinux.o`; no image resulted. A fresh candidate-derived build with only debug-info generation disabled is now being tested with the original toolchain and LTO/CFI retained. A separate non-LTO/CFI diagnostic output is paused; it is not a completed build.

## Reproduction

Use a separate source checkout, output directory and unpacked toolchains. Pins, archive URLs and hashes are in the input manifest. With the documented build dependencies installed:

```bash
bash scripts/kernel-baseline.sh SOURCE OUTPUT CLANG_DIR GCC_DIR configure
bash scripts/kernel-baseline.sh SOURCE OUTPUT CLANG_DIR GCC_DIR build
python3 scripts/compare-configs.py STOCK_CONFIG SOURCE/arch/arm64/configs/merge_kirin710_defconfig --source SOURCE
python3 scripts/verify-findings.py
```

For the LLD experiment, apply the linked build patch to a separate source checkout and set `LTO_LINKER=lld` for the recipe. [development-signing.config](../../configs/development-signing.config) records the standalone signing probe; keys stay in the external build output. [candidate-nolto.config](../../configs/candidate-nolto.config) is the separately labelled resource diagnostic, which changes kernel hardening.

No boot-image packaging, flashing, custom boot, display, touchscreen or Wi-Fi result is claimed.
