#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Small teaching build derived from sw/sw.mk; never invokes the root make.
set -euo pipefail
learn_dir=$(cd "$(dirname "$0")/.." && pwd)
repo_dir=$(cd "$learn_dir/../.." && pwd)
stage=${1:-array}
mode=${2:-spm}
case "$stage" in hello) number=0;; array) number=1;; mmio) number=2;; timer) number=3;; dma) number=4;; rvv) number=5;; *) echo 'stage: hello array mmio timer dma rvv' >&2; exit 2;; esac
case "$mode" in spm|dram) ;; *) echo 'mode: spm dram' >&2; exit 2;; esac
if [[ $number -ge 4 && $mode != spm ]]; then echo 'DMA/RVV lab requires SPM and its explicit reserved buffers' >&2; exit 2; fi
prefix=${CROSS_COMPILE:-riscv64-unknown-elf-}
for tool in gcc ar readelf objdump nm size; do command -v "${prefix}${tool}" >/dev/null; done
out=$(mktemp -d "$learn_dir/evidence/${stage}-${mode}.XXXXXX")
printf 'Output: %s\n' "$out"
exec > >(tee "$out/build.log") 2>&1
set -x
"${prefix}gcc" --version
git -C "$repo_dir" rev-parse HEAD
flags=(-march=rv64gc_zifencei -mabi=lp64d -mcmodel=medany -mstrict-align
       -O2 -g -Wall -Wextra -fno-builtin -fno-tree-vectorize
       -ffunction-sections -fdata-sections
       -I"$repo_dir/sw/include" -I"$repo_dir/sw/deps/printf")
for src in sw/lib/dif/uart.c sw/lib/dif/clint.c sw/deps/printf/printf.c; do
    name=$(basename "${src%.c}")
    "${prefix}gcc" "${flags[@]}" -c "$repo_dir/$src" -o "$out/$name.o"
done
"${prefix}ar" rcs "$out/libsupport.a" "$out/uart.o" "$out/clint.o" "$out/printf.o"
"${prefix}gcc" "${flags[@]}" -c "$repo_dir/sw/lib/crt0.S" -o "$out/crt0.o"
"${prefix}gcc" "${flags[@]}" -DLESSON_STAGE="$number" -DINJECT_ERROR="${INJECT_ERROR:-0}" \
    -save-temps=obj -c "$learn_dir/examples/lesson.c" -o "$out/lesson.o"
extra=()
if [[ $stage == rvv ]]; then
    "${prefix}gcc" -march=rv64gcv_zifencei -mabi=lp64d -g \
        -c "$learn_dir/examples/rvv_add.S" -o "$out/rvv_add.o"
    extra+=("$out/rvv_add.o")
fi
"${prefix}gcc" "${flags[@]}" -nostartfiles -static -T "$repo_dir/sw/link/$mode.ld" \
    -Wl,-L"$repo_dir/sw/link" -Wl,--gc-sections -Wl,-Map,"$out/lesson.map" \
    "$out/crt0.o" "$out/lesson.o" "${extra[@]}" "$out/libsupport.a" -o "$out/lesson.$mode.elf"
"${prefix}readelf" -h -l -S "$out/lesson.$mode.elf" > "$out/readelf.txt"
"${prefix}objdump" -d -S "$out/lesson.$mode.elf" > "$out/lesson.dump"
"${prefix}nm" -n "$out/lesson.$mode.elf" > "$out/symbols.txt"
"${prefix}size" "$out/lesson.$mode.elf"
set +x
printf 'BUILD ONLY; hardware execution is unverified. ELF: %s\n' "$out/lesson.$mode.elf"
