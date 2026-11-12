#!/bin/bash
# Apply the two 4.14 socket-mediation commits linked by the UBports guide.
set -euo pipefail
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $0 SOURCE PATCH_CACHE [--check]" >&2
    exit 2
fi
src=$(realpath "$1")
mkdir -p "$2"
cache=$(realpath "$2")
mode=${3:---apply}
test "$mode" = --apply || test "$mode" = --check
test "$(git -C "$src" rev-parse HEAD)" = c1e2747d8e839bedaa71a6436d24a51285d98509
test -z "$(git -C "$src" status --porcelain --untracked-files=all)"
commits=(559e4f447556e1ea0b24b035965023b6fba8f2f8 f076c3083d908253d32d26b49d64faaf4f80b442)
hashes=(00f1bf609436cef86dcf227f9b98c944accf82368ede62239cc62866d4e3d6ff 7bebc2494dc4ca578e71e333bedaad7e93f8f6096508f5b2bd603ec0bebc905b)
for i in 0 1; do
    file="$cache/${commits[$i]}.patch"
    if [ ! -f "$file" ]; then
        curl --fail --location --max-time 120 \
            "https://github.com/kdrag0n/proton_zf6/commit/${commits[$i]}.patch" -o "$file.tmp"
        mv "$file.tmp" "$file"
    fi
    printf '%s  %s\n' "${hashes[$i]}" "$file" | sha256sum -c -
done
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
git -C "$src" archive HEAD security/apparmor | tar -xf - -C "$scratch"
# The exported source lacks this ignore file; excluding it changes no kernel code.
for commit in "${commits[@]}"; do
    git -C "$scratch" apply --exclude=security/apparmor/.gitignore "$cache/$commit.patch"
done
if [ "$mode" = --apply ]; then
    for commit in "${commits[@]}"; do
        git -C "$src" apply --exclude=security/apparmor/.gitignore "$cache/$commit.patch"
    done
fi
echo "AppArmor patches: $mode passed"
