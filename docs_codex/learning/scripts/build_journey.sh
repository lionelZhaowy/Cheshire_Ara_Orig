#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Small teaching build derived from sw/sw.mk; never invokes the root make.
set -euo pipefail
learn_dir=$(cd "$(dirname "$0")/.." && pwd)
repo_dir=$(cd "$learn_dir/../.." && pwd)
stage=${1:-scalar}
mode=${2:-spm}
case "$stage" in scalar) number=0;; rvv|rvv-intrinsics|rvv-auto) number=1;; *) echo 'mode: scalar rvv rvv-intrinsics rvv-auto' >&2; exit 2;; esac
case "$mode" in spm|dram) ;; *) echo 'placement: spm dram' >&2; exit 2;; esac
if [[ $number -eq 1 && $mode != spm ]]; then echo 'RVV requires reserved uncached SPM buffers' >&2; exit 2; fi
prefix=${CROSS_COMPILE:-riscv64-unknown-elf-}
for tool in gcc ar readelf objdump nm size; do command -v "${prefix}${tool}" >/dev/null; done
if [[ -n ${JOURNEY_OUT:-} ]]; then
    mkdir -p "$JOURNEY_OUT"
    out=$(cd "$JOURNEY_OUT" && pwd)
    if [[ -n $(ls -A "$out") ]]; then echo 'JOURNEY_OUT must be empty' >&2; exit 2; fi
else
    out=$(mktemp -d "$learn_dir/evidence/journey-${stage}-${mode}.XXXXXX")
fi
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
"${prefix}gcc" "${flags[@]}" -DJOURNEY_RVV="$number" -DJOURNEY_DEPTH="${JOURNEY_DEPTH:-0}" -DINJECT_ERROR="${INJECT_ERROR:-0}" \
    -save-temps=obj -c "$learn_dir/examples/journey.c" -o "$out/journey.o"
extra=()
if [[ $number -eq 1 ]]; then
    if [[ $stage == rvv ]]; then
        "${prefix}gcc" -march=rv64gcv_zifencei -mabi=lp64d -g \
            -c "$learn_dir/examples/rvv_add.S" -o "$out/rvv_add.o"
        extra+=("$out/rvv_add.o")
        if [[ ${JOURNEY_DEPTH:-0} == 1 ]]; then
            "${prefix}gcc" -march=rv64gcv_zifencei -mabi=lp64d -g \
                -c "$learn_dir/examples/rvv_reduce.S" -o "$out/rvv_reduce.o"
            extra+=("$out/rvv_reduce.o")
        fi
    else
        kernel=rvv_intrinsics
        if [[ $stage == rvv-auto ]]; then kernel=rvv_auto; fi
        # Only this compilation unit may use V. CRT/main/library stay scalar.
        "${prefix}gcc" -march=rv64gcv_zifencei -mabi=lp64d -mcmodel=medany \
            -O3 -g -Wall -Wextra -ftree-vectorize -fno-vect-cost-model \
            -ffunction-sections -fdata-sections -fopt-info-vec-all="$out/vectorization.txt" \
            -c "$learn_dir/examples/$kernel.c" -o "$out/vector_kernel.o"
        extra+=("$out/vector_kernel.o")
    fi
fi

"${prefix}gcc" "${flags[@]}" -nostartfiles -static -T "$repo_dir/sw/link/$mode.ld" \
    -Wl,-L"$repo_dir/sw/link" -Wl,--gc-sections -Wl,-Map,"$out/journey.map" \
    "$out/crt0.o" "$out/journey.o" "${extra[@]}" "$out/libsupport.a" -o "$out/journey.$mode.elf"
"${prefix}readelf" -h -l -S "$out/journey.$mode.elf" > "$out/readelf.txt"
"${prefix}objdump" -d -S "$out/journey.$mode.elf" > "$out/journey.dump"
"${prefix}nm" -S -n "$out/journey.$mode.elf" > "$out/symbols.txt"
"${prefix}size" "$out/journey.$mode.elf"
set +x
printf 'BUILD ONLY; hardware execution is unverified. ELF: %s\n' "$out/journey.$mode.elf"
