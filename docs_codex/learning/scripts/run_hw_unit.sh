#!/usr/bin/env bash
# Isolated teaching unit only. Never compiles the Cheshire SoC or production filelists.
set -euo pipefail
lesson_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for tool in vlib vmap vlog vsim timeout; do
  command -v "$tool" >/dev/null || { echo "BLOCKED: missing $tool" >&2; exit 2; }
done
lesson_out="$(mktemp -d /tmp/cheshire-hw-unit.XXXXXX)"
echo "OUTPUT=$lesson_out"
cd "$lesson_out"
timeout 30 vmap -c >setup.log 2>&1
timeout 30 vlib work >>setup.log 2>&1
timeout 60 vlog -sv -work work "$lesson_root/examples/hw/lesson_reg_adder.sv" \
  "$lesson_root/examples/hw/tb_lesson_reg_adder.sv" >compile.log 2>&1
# Fail explicitly on simulator errors; success also requires the TB's check marker.
timeout 60 vsim -c work.tb_lesson_reg_adder -do \
  'onerror {quit -code 1}; onbreak {quit -code 1}; run -all; quit -code 0' >run.log 2>&1
python3 "$lesson_root/scripts/check_hw_unit.py" "$lesson_out/run.log"
# The same TB must fail when deliberately injected; preserve its log and exit status.
set +e
timeout 60 vsim -c work.tb_lesson_reg_adder +INJECT_FAIL -do \
  'onerror {quit -code 1}; onbreak {quit -code 1}; run -all; quit -code 0' >injected.log 2>&1
lesson_inject_rc=$?
set -e
python3 - "$lesson_out/injected.log" "$lesson_inject_rc" <<'PY'
import pathlib,sys
s=pathlib.Path(sys.argv[1]).read_text(errors='replace');rc=int(sys.argv[2])
if rc==124 or 'injected checker failure' not in s or 'HW_UNIT_PASS' in s:
    raise SystemExit('FAIL: injected fault did not fail as intended')
print('Injected simulation raw rc='+str(rc)+'; require log checker rejection below')
PY
set +e
python3 "$lesson_root/scripts/check_hw_unit.py" "$lesson_out/injected.log" >injected-check.txt 2>&1
lesson_check_rc=$?
set -e
if [[ "$lesson_check_rc" != 1 ]]; then
  echo "FAIL: expected log checker exit 1, got $lesson_check_rc" >&2
  exit 1
fi
echo "PASS: injected failure rejected by log checker (exit 1)"
