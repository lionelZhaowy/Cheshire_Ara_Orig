#!/usr/bin/env bash
# Compile existing source in an empty directory. No production object is reused.
set -euo pipefail
repo_dir=$(cd "$(dirname "$0")/../../../.." && pwd)
out=${1:?Pass a new output directory}
mkdir -p "$out"
[[ -z $(ls -A "$out") ]] || { echo 'Output must be empty' >&2; exit 2; }
out=$(cd "$out" && pwd)
support_dir=${2:?Pass this session scalar-build directory}
prefix=${CROSS_COMPILE:-riscv64-unknown-elf-}
exec > >(tee "$out/build.log") 2>&1
set -x
"${prefix}gcc" --version
flags=(-march=rv64gc_zifencei -mabi=lp64d -mcmodel=medany -mstrict-align -O2 -g -Wall -Wextra -fno-builtin -ffunction-sections -fdata-sections -I"$repo_dir/sw/include" -I"$repo_dir/sw/deps/printf")
"${prefix}gcc" "${flags[@]}" -c "$repo_dir/sw/tests/helloworld.c" -o "$out/helloworld.o"
"${prefix}gcc" "${flags[@]}" -nostartfiles -static -T "$repo_dir/sw/link/spm.ld" -Wl,-L"$repo_dir/sw/link" -Wl,--gc-sections -Wl,-Map,"$out/hello.map" "$support_dir/crt0.o" "$out/helloworld.o" "$support_dir/libsupport.a" -o "$out/hello.spm.elf"
"${prefix}readelf" -h -l "$out/hello.spm.elf" > "$out/readelf.txt"
"${prefix}objdump" -d -S "$out/hello.spm.elf" > "$out/hello.dump"
# Generated compile-only probe: execute neither NEXT_ID nor DMA on hardware.
cat > "$out/dma-probe.c" <<'C'
#include "dif/dma.h"
uint64_t probe_next(void) { return *sys_dma_nextid_ptr(); }
uint64_t probe_done(void) { return *sys_dma_done_ptr(); }
C
"${prefix}gcc" "${flags[@]}" -c "$out/dma-probe.c" -o "$out/dma-probe.o"
"${prefix}objdump" -dr "$out/dma-probe.o" > "$out/dma-probe.dump"
echo 'Compile and link only; no target execution.'
