#!/bin/bash
# Build-only recipe for the pinned research candidate. Does not package or flash.
set -euo pipefail
if [ "$#" -lt 5 ]; then
    echo "Usage: $0 SOURCE OUTPUT CLANG_DIR GCC_DIR configure|build|stock-config|merge-config|modules-install [INPUTS...]" >&2
    exit 2
fi
src=$(realpath "$1")
mkdir -p "$2"
out=$(realpath "$2")
clang_dir=$(realpath "$3")
gcc_dir=$(realpath "$4")
action=$5
pin=c1e2747d8e839bedaa71a6436d24a51285d98509
test "$(git -C "$src" rev-parse HEAD)" = "$pin"
test "$src" != "$out"
export PATH="$gcc_dir/bin:$clang_dir/bin:$PATH"
export KBUILD_BUILD_USER=builder KBUILD_BUILD_HOST=kernel-build
export KBUILD_BUILD_TIMESTAMP='Thu Nov 12 00:00:00 UTC 2026'
# Use the native compiler behind AOSP's Python wrapper; leave prebuilts intact.
make_args=(-C "$src" "O=$out" ARCH=arm64 CROSS_COMPILE=aarch64-linux-android-
    CLANG_TRIPLE=aarch64-linux-gnu- "CLANG_PREBUILTS_PATH=$clang_dir/"
    "CC=$clang_dir/bin/clang.real" "HOSTCC=$clang_dir/bin/clang.real"
    "HOSTCXX=$clang_dir/bin/clang++.real")
case "${LTO_LINKER:-gold}" in
    gold) ;;
    lld)
        # Requires patches/0001-build-allow-lld-for-lto.patch in SOURCE.
        make_args+=("GCC_TOOLCHAIN=$gcc_dir" "LD=$clang_dir/bin/ld.lld --lto-O1") ;;
    *) echo "Unsupported LTO_LINKER" >&2; exit 2 ;;
esac
if [ -n "${GOLD_LTO_OPT:-}" ]; then
    case "$GOLD_LTO_OPT" in 0|1|2|3) ;; *) exit 2 ;; esac
    test "${LTO_LINKER:-gold}" = gold
    test "$action" = build
    grep -qx 'CONFIG_LTO_CLANG=y' "$out/.config"
    # Gold requires its plugin to be loaded before parsing plugin options.
    # Append the option only to commands that actually load LLVMgold.
    wrapper="$out/gold-lto-wrapper"
    {
        printf '#!/bin/bash\nset -euo pipefail\nopt=%s\n' "$GOLD_LTO_OPT"
        cat <<'SH'
for arg in "$@"; do
    case "$arg" in
        -plugin|--plugin|-plugin=*|--plugin=*)
            exec aarch64-linux-android-ld.gold "$@" "-plugin-opt=O$opt" ;;
    esac
done
exec aarch64-linux-android-ld.gold "$@"
SH
    } > "$wrapper"
    chmod 755 "$wrapper"
    make_args+=("LDGOLD=$wrapper")
fi
case "$action" in
    configure) make "${make_args[@]}" merge_kirin710_defconfig ;;
    stock-config)
        test "$#" -eq 6
        test ! -e "$out/.config"
        cp "$6" "$out/input.config"
        cp "$6" "$out/.config"
        make "${make_args[@]}" olddefconfig ;;
    merge-config)
        test "$#" -ge 6
        test -f "$out/.config"
        test ! -e "$out/pre-fragment.config"
        fragments=()
        for fragment in "${@:6}"; do fragments+=("$(realpath "$fragment")"); done
        cp "$out/.config" "$out/pre-fragment.config"
        # The vendor helper creates temporary files in CWD and can otherwise
        # hide failures. Merge only, then run make with the exact recipe flags.
        (cd "$out" && bash -e "$src/scripts/kconfig/merge_config.sh" \
            -m -O "$out" "$out/.config" "${fragments[@]}")
        make "${make_args[@]}" olddefconfig
        python3 - "$out" "${fragments[@]}" <<'PY'
import hashlib
import json
from pathlib import Path
import re
import sys

out = Path(sys.argv[1])
fragments = [Path(p) for p in sys.argv[2:]]
def values(path):
    result = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'(CONFIG_\w+)=(.*)', line)
        unset = re.fullmatch(r'# (CONFIG_\w+) is not set', line)
        if match:
            result[match[1]] = match[2]
        elif unset:
            result[unset[1]] = 'n'
    return result

actual = values(out / '.config')
requested = {}
for fragment in fragments:
    requested.update(values(fragment))
omitted = []
for key, value in requested.items():
    if actual.get(key) == value:
        continue
    # These dependent CFI options disappear when the explicit non-LTO
    # resource fragment is selected. No other omission is accepted.
    if (key in {'CONFIG_CFI_CLANG', 'CONFIG_CFI_CLANG_SHADOW'}
            and value == 'n' and key not in actual
            and actual.get('CONFIG_LTO_NONE') == 'y'):
        omitted.append(key)
        continue
    raise SystemExit(f'Fragment value not retained: {key}={value}, actual={actual.get(key)}')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {
    'input_config_sha256': digest(out / 'pre-fragment.config'),
    'fragments': [{'name': p.name, 'sha256': digest(p)} for p in fragments],
    'config_sha256': digest(out / '.config'),
    'dependency_omitted_requested_unset_symbols': omitted,
    'requested_values_verified': True,
}
(out / 'fragment-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
PY
        ;;
    build) make "${make_args[@]}" -j"${JOBS:-2}" Image.gz modules ;;
    modules-install)
        test "$#" -eq 6
        mkdir -p "$6"
        staging=$(realpath "$6")
        test "$staging" != /
        test "$staging" != "$src"
        make "${make_args[@]}" "INSTALL_MOD_PATH=$staging" modules_install ;;
    *) echo "Unknown action: $action" >&2; exit 2 ;;
esac
