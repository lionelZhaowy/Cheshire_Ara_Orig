#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Scoped follow-up to run_001 relocation failures; leaves original evidence intact."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

src = Path(__file__).resolve().parent
root = src.parent
out = root/'run_002'
if root != Path.home()/'CheshireAraPULP/_e01/preflight' or out.exists():
    raise SystemExit('Unexpected root or preexisting diagnostic output')
out.mkdir()
(out/'logs').mkdir()
prefix = '/opt/riscv/bin/riscv64-unknown-elf-'
cc = prefix+'gcc'
records = []
checks = []
def run(label, cmd, binary=None):
    stdout = out/binary if binary else out/'logs'/(label+'.stdout')
    stderr = out/'logs'/(label+'.stderr')
    start = time.monotonic()
    with stdout.open('wb') as so, stderr.open('wb') as se:
        try:
            rc = subprocess.run([str(x) for x in cmd], cwd=str(out),
                                stdout=so, stderr=se, timeout=60).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rec = dict(label=label, command=[str(x) for x in cmd], cwd=str(out),
               timeout_seconds=60, exit_code=rc, elapsed_seconds=round(time.monotonic()-start,3),
               stdout=str(stdout.relative_to(out)), stderr=str(stderr.relative_to(out)))
    records.append(rec)
    with (out/'commands.jsonl').open('a') as f: f.write(json.dumps(rec)+'\n')
    print(label, 'rc='+str(rc), flush=True)
    return rc==0
def text(label): return (out/'logs'/(label+'.stdout')).read_text(errors='replace')
def check(name, ok): checks.append(dict(name=name, passed=bool(ok)))

library=Path('/opt/riscv/lib/gcc/riscv64-unknown-elf/13.2.0/libgcc.a')
run('extract_divdi3',[prefix+'ar','p',library,'_divdi3.o'],binary='libgcc_divdi3.o')
run('libgcc_relocations',[prefix+'objdump','-dr',out/'libgcc_divdi3.o'])
run('libgcc_attributes',[prefix+'readelf','-hA',out/'libgcc_divdi3.o'])
check('cause_absolute_HI20_clz_tab', 'R_RISCV_HI20\t__clz_tab' in text('libgcc_relocations'))

for kind,isa in [('scalar','rv64gc_zifencei'),('vector','rv64gcv_zifencei')]:
    flags=['-march='+isa,'-mabi=lp64d','-mcmodel=medany','-mstrict-align']
    opt=['-O2','-fno-builtin','-ffunction-sections','-fdata-sections','-mexplicit-relocs']
    asm=root/'run_001'/(kind+'_asm.o')
    # Verify original startup can assemble. It is not linked or run in this probe.
    if run(kind+'_original_crt0_compile',[cc]+flags+['-c',src/'crt0.S','-o',out/(kind+'_crt0.o')]):
        run(kind+'_original_crt0_disassembly',[prefix+'objdump','-dr',out/(kind+'_crt0.o')])
    # Current project's LTO options, full libc+libgcc probe at the already-valid SPM address.
    lto=out/(kind+'_lto.o')
    if run(kind+'_lto_compile',[cc]+flags+opt+['-flto','-c',root/'inputs/probe.c','-o',lto]):
        run(kind+'_lto_spm_link',[cc]+flags+['-flto','-fuse-linker-plugin','-Wl,-flto',
            '-nostdlib','-static','-Wl,--defsym=PROBE_BASE=0x10000000',
            '-T',root/'inputs/probe.ld','-Wl,-Map='+str(out/(kind+'_lto.map')),
            asm,lto,'-Wl,--start-group','-lc','-lgcc','-Wl,--end-group',
            '-o',out/(kind+'_lto.elf')])
    subset=out/(kind+'_subset.o')
    if not run(kind+'_subset_compile',[cc]+flags+opt+['-c',src/'runtime_subset.c','-o',subset]):
        continue
    # Use current unchanged common.ldh and spm/dram.ld with the standalone _start.
    # Explicit __stack_top is needed only by the standalone probe, not by Cheshire crt0.
    for region,base in [('spm',0x10000000),('dram',0x80000000)]:
        tag=kind+'_subset_'+region
        elf=out/(tag+'.elf')
        ok=run(tag+'_link',[cc]+flags+['-nostdlib','-static','-Wl,-L'+str(src),
             '-T',src/(region+'.ld'),'-Wl,--defsym=__stack_top='+hex(base+0x10000),
             '-Wl,-Map='+str(out/(tag+'.map')),asm,subset,
             '-Wl,--start-group','-lc','-lgcc','-Wl,--end-group','-o',elf])
        if ok:
            run(tag+'_readelf',[prefix+'readelf','-hl',elf])
            run(tag+'_symbols',[prefix+'nm','-n',elf])
            run(tag+'_undefined',[prefix+'nm','-u',elf])
            check(tag+'_resolved',not text(tag+'_undefined').strip())
            check(tag+'_memcpy_without_divti3',' memcpy' in text(tag+'_symbols') and
                  '__divti3' not in text(tag+'_symbols'))
            check(tag+'_entry',hex(base) in text(tag+'_readelf'))

summary=dict(commands=len(records),command_failures=[r for r in records if r['exit_code']],
             checks=checks,passed=all(r['exit_code']==0 for r in records) and
             all(c['passed'] for c in checks),target_execution=False,vcs_invoked=False,
             limits='Run_001 high-address libgcc failure remains open; subset success is not a fix')
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
hashes={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted(out.rglob('*')) if f.is_file()}
(out/'artifact_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('SUMMARY',json.dumps(summary),flush=True)
raise SystemExit(0 if summary['passed'] else 1)
