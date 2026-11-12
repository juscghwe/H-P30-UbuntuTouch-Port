#!/bin/bash
# Build-only recipe for the pinned research candidate. Does not package or flash.
set -euo pipefail
if [ "$#" -lt 5 ]; then
    echo "Usage: $0 SOURCE OUTPUT CLANG_DIR GCC_DIR configure|build|stock-config [STOCK_CONFIG]" >&2
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
case "$action" in
    configure) make "${make_args[@]}" merge_kirin710_defconfig ;;
    stock-config)
        test "$#" -eq 6
        test ! -e "$out/.config"
        cp "$6" "$out/input.config"
        cp "$6" "$out/.config"
        make "${make_args[@]}" olddefconfig ;;
    build) make "${make_args[@]}" -j"${JOBS:-2}" Image.gz modules ;;
    *) echo "Unknown action: $action" >&2; exit 2 ;;
esac
