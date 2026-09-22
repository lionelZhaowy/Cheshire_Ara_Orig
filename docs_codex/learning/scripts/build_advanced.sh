#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Only compile/link; never invokes Make/Bender/RTL simulation or writes original sw/.
set -euo pipefail
learn_dir=$(cd "$(dirname "$0")/.." && pwd)
repo_dir=$(cd "$learn_dir/../.." && pwd)
stage=${1:-capstone}
case "$stage" in gpio) number=1;; timer) number=2;; capstone) number=3;; eeprom) number=4;; flash) number=5;; *) echo 'stage: gpio timer capstone eeprom flash' >&2; exit 2;; esac
prefix=${CROSS_COMPILE:-riscv64-unknown-elf-}
for tool in gcc ar readelf objdump nm size; do command -v "${prefix}${tool}" >/dev/null; done
out=$(mktemp -d "$learn_dir/evidence/adv-${stage}-spm.XXXXXX")
printf 'Output: %s\n' "$out"
exec > >(tee "$out/build.log") 2>&1
set -x
"${prefix}gcc" --version
git -C "$repo_dir" rev-parse HEAD
otp="$repo_dir/.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a"
flags=(-march=rv64gc_zifencei -mabi=lp64d -mcmodel=medany -mstrict-align
       -O2 -g -Wall -Wextra -fno-builtin -fno-tree-vectorize -DOT_PLATFORM_RV32
       -ffunction-sections -fdata-sections -I"$repo_dir/sw/include"
       -I"$repo_dir/sw/deps/printf" -I"$otp" -I"$otp/sw/include")
sources=("$repo_dir/sw/lib/dif/uart.c" "$repo_dir/sw/lib/dif/clint.c" "$repo_dir/sw/deps/printf/printf.c")
input="$learn_dir/examples/advanced.c"
if [[ $number -ge 4 ]]; then
    input="$learn_dir/examples/storage_read.c"
    kind=i2c; hal=i2c_24fc1025
    if [[ $number == 5 ]]; then kind=spi_host; hal=spi_s25fs512s; fi
    sources+=("$repo_dir/sw/lib/hal/$hal.c"
              "$otp/sw/device/lib/dif/dif_$kind.c"
              "$otp/sw/device/lib/dif/autogen/dif_${kind}_autogen.c"
              "$otp/sw/device/lib/base/mmio.c" "$otp/sw/device/lib/base/memory.c")
fi
objects=(); n=0
for src in "${sources[@]}"; do
    "${prefix}gcc" "${flags[@]}" -c "$src" -o "$out/support-$n.o"
    objects+=("$out/support-$n.o"); n=$((n+1))
done
"${prefix}ar" rcs "$out/libsupport.a" "${objects[@]}"
"${prefix}gcc" "${flags[@]}" -c "$repo_dir/sw/lib/crt0.S" -o "$out/crt0.o"
"${prefix}gcc" "${flags[@]}" -DADV_STAGE="$number" -DINJECT_ERROR="${INJECT_ERROR:-0}" \
    -DOMIT_GPIO_TRIGGER="${OMIT_GPIO_TRIGGER:-0}" -DDMA_INTERFACE_VALIDATED="${DMA_INTERFACE_VALIDATED:-0}" \
    -save-temps=obj -c "$input" -o "$out/advanced.o"
"${prefix}gcc" "${flags[@]}" -nostartfiles -static -T "$repo_dir/sw/link/spm.ld" \
    -Wl,-L"$repo_dir/sw/link" -Wl,--gc-sections -Wl,-Map,"$out/advanced.map" \
    "$out/crt0.o" "$out/advanced.o" "$out/libsupport.a" -o "$out/advanced.spm.elf"
"${prefix}readelf" -h -l -S "$out/advanced.spm.elf" > "$out/readelf.txt"
"${prefix}objdump" -d -S "$out/advanced.spm.elf" > "$out/advanced.dump"
"${prefix}nm" -n "$out/advanced.spm.elf" > "$out/symbols.txt"
"${prefix}size" "$out/advanced.spm.elf"
set +x
printf 'BUILD ONLY, target unverified: %s\n' "$out/advanced.spm.elf"
