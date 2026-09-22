#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Export a local learning configuration; does not compile RTL or edit old scripts.
set -euo pipefail
learn_dir=$(cd "$(dirname "$0")/.." && pwd)
repo_dir=$(cd "$learn_dir/../.." && pwd)
cd "$repo_dir"
command -v bender >/dev/null
cxx_path=$(command -v "${CXX:-g++}")
for model in s25fs512s.v 24FC1025.v; do
    test -s "target/sim/models/$model" || { echo "Missing model: $model; prepare it in the licensed environment" >&2; exit 2; }
done
out=$(mktemp -d "$learn_dir/evidence/sim.XXXXXX")
mkdir -p "$out/vsim" "$out/vcs" "$out/src"
flags=(-t sim -t test -t rtl -t cva6 -t cv64a6_imafdcv_sv39
       -t exclude_first_pass_decoder --define ARA --define NR_LANES=2 --define VLEN=2048)
bender --local script vsim "${flags[@]}" --vlog-arg='-suppress 2583 -suppress 13314 -timescale 1ns/1ps' > "$out/vsim/compile.cheshire_soc.tcl"
printf '\nvlog "%s/target/sim/src/elfloader.cpp" -ccflags "-std=c++11" -cpppath "%s"\n' "$repo_dir" "$cxx_path" >> "$out/vsim/compile.cheshire_soc.tcl"
bender --local script vcs "${flags[@]}" --vlog-arg='-kdb -nc -assert svaext +v2k -timescale=1ns/1ps' --vlogan-bin=vlogan > "$out/vcs/compile.cheshire_soc.sh"
cp target/sim/vsim/start.cheshire_soc.tcl "$out/vsim/"
cp target/sim/vcs/start.cheshire_soc.sh "$out/vcs/"
cp target/sim/src/elfloader.cpp "$out/src/"
for file in "$out/vsim/compile.cheshire_soc.tcl" "$out/vcs/compile.cheshire_soc.sh"; do
    if rg -q 'cva6_accel_first_pass_decoder_stub|cv64a6_imafdchsclic_sv39_wb_config_pkg' "$file"; then
        echo "Unexpected scalar profile/stub in $file" >&2; exit 3
    fi
    test "$(rg -c 'cv64a6_imafdcv_sv39_config_pkg.sv' "$file")" = 1
    test "$(rg -c '/cva6_accel_first_pass_decoder.sv' "$file")" = 1
done
printf 'Prepared only (not compiled): %s\n' "$out"
