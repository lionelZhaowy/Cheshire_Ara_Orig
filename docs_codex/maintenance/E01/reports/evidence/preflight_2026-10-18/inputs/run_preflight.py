#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small serial compiler checks. Never invokes Bender, VCS, or RISC-V executables."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument('--out', required=True, help='New, nonexistent output directory')
args = p.parse_args()
src = Path(__file__).resolve().parent
out = Path(args.out).resolve()
allowed = Path.home() / 'CheshireAraPULP' / '_e01' / 'preflight'
if allowed.resolve() not in out.parents or out.exists():
    raise SystemExit('Refuse output outside preflight or existing output directory')
out.mkdir(parents=True, exist_ok=False)
logs = out / 'logs'
logs.mkdir()
prefix = '/opt/riscv/bin/riscv64-unknown-elf-'
cc = prefix + 'gcc'
cxx = '/opt/rh/gcc-toolset-13/root/usr/bin/g++'
vcs_include = '/eda/synopsys/vcs/W-2024.09-SP1/include'
records = []
checks = []

def run(label, cmd):
    start = time.monotonic()
    stdout, stderr = logs / (label + '.stdout'), logs / (label + '.stderr')
    with stdout.open('wb') as so, stderr.open('wb') as se:
        try:
            process = subprocess.run([str(x) for x in cmd], cwd=str(out),
                                     stdout=so, stderr=se, timeout=60)
            rc = process.returncode
        except subprocess.TimeoutExpired:
            rc = 124
        except OSError as e:
            se.write(str(e).encode())
            rc = 127
    rec = dict(label=label, command=[str(x) for x in cmd], cwd=str(out),
               timeout_seconds=60, exit_code=rc,
               elapsed_seconds=round(time.monotonic()-start, 3),
               stdout=str(stdout.relative_to(out)), stderr=str(stderr.relative_to(out)))
    records.append(rec)
    with (out / 'commands.jsonl').open('a') as f:
        f.write(json.dumps(rec) + '\n')
    print('{} rc={}'.format(label, rc), flush=True)
    return rc == 0

def check(name, ok, detail):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))

def content(label):
    return (logs / (label + '.stdout')).read_text(errors='replace')

inputs = {str(f.relative_to(src)): hashlib.sha256(f.read_bytes()).hexdigest()
          for f in sorted(src.rglob('*')) if f.is_file()}
(out / 'input_hashes.json').write_text(json.dumps(inputs, indent=2) + '\n')
for tool in ['gcc', 'as', 'ld', 'ar', 'objdump', 'readelf', 'nm']:
    run('version_' + tool, [prefix + tool, '--version'])
for label, option in [('triple', '-dumpmachine'), ('multilib', '-print-multi-lib'),
                      ('sysroot', '-print-sysroot'), ('as_path', '-print-prog-name=as'),
                      ('ld_path', '-print-prog-name=ld'),
                      ('lto_plugin', '-print-file-name=liblto_plugin.so')]:
    run(label, [cc, option])
run('host_version', [cxx, '--version'])
run('host_triple', [cxx, '-dumpmachine'])

for kind, isa in [('scalar', 'rv64gc_zifencei'), ('vector', 'rv64gcv_zifencei')]:
    flags = ['-march=' + isa, '-mabi=lp64d', '-mcmodel=medany', '-mstrict-align']
    for label, option in [('multi_dir', '-print-multi-directory'),
                          ('libc', '-print-file-name=libc.a'),
                          ('libgcc', '-print-libgcc-file-name')]:
        run(kind + '_' + label, [cc] + flags + [option])
    asm, obj = out / (kind + '_asm.o'), out / (kind + '_c.o')
    asm_ok = run(kind + '_assemble', [cc] + flags + ['-c', src/'probe.S', '-o', asm])
    c_ok = run(kind + '_compile', [cc] + flags + ['-O2', '-Wall', '-Wextra',
              '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections',
              '-c', src/'probe.c', '-o', obj])
    if not (asm_ok and c_ok):
        check(kind + '_objects', False, 'See compile/assembly logs; dependent links skipped')
        continue
    run(kind + '_object_attributes', [prefix+'readelf', '-hA', asm, obj])
    attr = content(kind + '_object_attributes')
    check(kind + '_object_abi', 'double-float ABI' in attr, 'readelf ELF flags')
    check(kind + '_object_isa', ('_v1p0' in attr) == (kind == 'vector'),
          'Vector objects require v1p0; scalar objects must not require it')
    for region, base in [('spm', '0x10000000'), ('dram', '0x80000000')]:
        tag = kind + '_' + region
        elf, mapfile = out/(tag+'.elf'), out/(tag+'.map')
        ok = run(tag + '_link', [cc] + flags + ['-nostdlib', '-static',
                 '-Wl,--defsym=PROBE_BASE='+base, '-T', src/'probe.ld',
                 '-Wl,-Map='+str(mapfile)+',--cref', asm, obj,
                 '-Wl,--start-group', '-lc', '-lgcc', '-Wl,--end-group', '-o', elf])
        if not ok:
            check(tag + '_link', False, 'See linker error; ELF checks skipped')
            continue
        run(tag + '_readelf', [prefix+'readelf', '-hAl', elf])
        run(tag + '_disassembly', [prefix+'objdump', '-d', elf])
        run(tag + '_undefined', [prefix+'nm', '-u', elf])
        run(tag + '_symbols', [prefix+'nm', '-n', elf])
        header, dis, symbols = content(tag+'_readelf'), content(tag+'_disassembly'), content(tag+'_symbols')
        check(tag + '_elf', 'ELF64' in header and 'RISC-V' in header and
              'double-float ABI' in header and re.search(r'Entry point address:\s+'+base+r'\b', header),
              'ELF64 RISC-V lp64d and requested entry')
        check(tag + '_resolved', not content(tag+'_undefined').strip(), 'No undefined ELF symbols')
        mapping = mapfile.read_text()
        check(tag + '_libc_libgcc', 'libc.a(' in mapping and 'libgcc.a(' in mapping
              and re.search(r'\bmemcpy\b', symbols) and re.search(r'\b__divti3\b', symbols),
              'Actual archive members and memcpy/__divti3 definitions in final ELF')
        required = ['fence.i', 'amoadd.d', 'amoswap.w', 'lr.d', 'sc.d', 'fadd.d', 'fadd.s']
        if kind == 'vector':
            required += ['vsetvli', 'vsetivli', 'vle32.v', 'vadd.vv', 'vse32.v', 'vfmacc.vv']
        check(tag + '_instructions', all(x in dis for x in required), required)

host = out / 'host_probe'
if run('host_compile_link', [cxx, '-std=c++11', '-O2', '-Wall', '-Wextra',
                            src/'host.cpp', '-o', host]):
    run('host_execution', [host])
    check('host_native_run', 'E01_NATIVE_CXX_PASS sum=10' in content('host_execution'),
          'Runs only x86_64 host program, never RISC-V or VCS')
    run('host_dynamic_libraries', ['ldd', host])
loader = out / 'elfloader.o'
if run('elfloader_compile', [cxx, '-std=c++11', '-O2', '-Wall', '-Wextra', '-fPIC',
                            '-I'+vcs_include, '-c', src/'elfloader.cpp', '-o', loader]):
    run('elfloader_header', ['readelf', '-h', loader])
    run('elfloader_symbols', ['nm', '-g', loader])
    check('elfloader_host_arch', 'X86-64' in content('elfloader_header'), 'DPI object is x86_64')
    check('elfloader_api', all(re.search(r' T '+x+r'$', content('elfloader_symbols'), re.M)
          for x in ['read_elf','get_entry','get_section','read_section']), 'Exported C API')
    check('elfloader_simulator_dependency', 'svGetArrayPtr' in content('elfloader_symbols'),
          'Expected unresolved simulator API; VCS link/run is deferred')

summary = dict(stage='E01 step 1', commands=len(records),
               command_failures=[r for r in records if r['exit_code']], checks=checks,
               passed=all(r['exit_code']==0 for r in records) and all(c['passed'] for c in checks),
               target_execution=False, vcs_invoked=False,
               limits='Standalone probes only; full Cheshire startup/runtime and RTL remain untested')
(out/'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
artifacts = {str(f.relative_to(out)): hashlib.sha256(f.read_bytes()).hexdigest()
             for f in sorted(out.rglob('*')) if f.is_file()}
(out/'artifact_hashes.json').write_text(json.dumps(artifacts, indent=2) + '\n')
print('SUMMARY passed={} commands={} check_failures={}'.format(summary['passed'], len(records),
      [c['name'] for c in checks if not c['passed']]), flush=True)
raise SystemExit(0 if summary['passed'] else 1)
