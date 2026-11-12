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

More significantly, normalizing the **complete stock config** removes 66 explicit entries and adds one, with all 5,246 retained shared values unchanged. Of those removed entries, 65 have no Kconfig definition in this tree. Several were already present in the candidate's literal defconfig, so the earlier 35-entry difference did not reveal them. Lost stock-enabled entries include Huawei TCPC/USB-PD support, root/TEE measurement interfaces, DPM and Gator. One removed entry, `CORESIGHT=n`, has a definition but is omitted under its dependencies. [The normalization record](../raw/2026-11-12-build/03-stock-normalization.json) is the complete list; absence from generated config must not be silently treated as preserved functionality.

The stock input remains byte-for-byte identical to E08. Candidate-pristine, stock-derived and future Halium outputs use separate directories. No signing key or proprietary binary is committed. `certs/Makefile` additionally contains a Huawei-specific Android output-directory assumption when `MODULE_SIG_KEY="huawei_signing_key.pem"`; the stock-derived signing path needs separate validation.

## Reproduction

Use a separate source checkout, output directory and unpacked toolchains. Pins, archive URLs and hashes are in the input manifest. With the documented build dependencies installed:

```bash
bash scripts/kernel-baseline.sh SOURCE OUTPUT CLANG_DIR GCC_DIR configure
bash scripts/kernel-baseline.sh SOURCE OUTPUT CLANG_DIR GCC_DIR build
python3 scripts/compare-configs.py STOCK_CONFIG SOURCE/arch/arm64/configs/merge_kirin710_defconfig --source SOURCE
python3 scripts/verify-findings.py
```

The candidate baseline is compiling with two jobs and a 6 GiB memory limit. A complete `Image.gz`/module result is pending. No boot-image packaging, flashing, custom boot, display, touchscreen or Wi-Fi result is claimed.
