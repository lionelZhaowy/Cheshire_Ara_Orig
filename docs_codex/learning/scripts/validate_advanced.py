#!/usr/bin/env python3
"""Lightweight software/evidence checks only. Does NOT run HDL simulators."""
from pathlib import Path
import subprocess,os,json,hashlib,re,sys
ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from check_advanced_run import check
def run(args,**kw):
    return subprocess.run(args,cwd=REPO,capture_output=True,text=True,**kw)
report=['L01 advanced: SOFTWARE BUILD / STATIC CHECKS ONLY; no RTL run or board operation.']
logs=ROOT/'evidence/advanced_build_logs';logs.mkdir(exist_ok=True)
variants=[('gpio','gpio',{}),('timer','timer',{}),('capstone-guard','capstone',{}),
          ('capstone-path','capstone',{'DMA_INTERFACE_VALIDATED':'1'}),
          ('capstone-corrupt','capstone',{'DMA_INTERFACE_VALIDATED':'1','INJECT_ERROR':'1'}),
          ('gpio-missing','gpio',{'OMIT_GPIO_TRIGGER':'1'}),('eeprom','eeprom',{}),('flash','flash',{})]
prefix=os.environ.get('CROSS_COMPILE','riscv64-unknown-elf-')
for label,stage,env in variants:
    r=run(['bash',str(ROOT/'scripts/build_advanced.sh'),stage],env={**os.environ,**env})
    (logs/f'{label}.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise SystemExit(f'{label} build failed ({r.returncode}); inspect log')
    out=Path(re.search(r'^Output: (.+)$',r.stdout,re.M)[1]);elf=out/'advanced.spm.elf'
    syms=(out/'symbols.txt').read_text();rd=(out/'readelf.txt').read_text()
    assert '0x10000000' in rd,(label,'entry')
    end=int(re.search(r'^([0-9a-f]+)\s+\w\s+__bss_end$',syms,re.M)[1],16)
    assert end<0x10010000,(label,'application overlaps reserved DMA region')
    if stage in ('gpio','timer','capstone'):
        assert re.search(r'\bT trap_vector$',syms,re.M),(label,'weak trap not overridden')
        dump=(out/'advanced.dump').read_text()
        body=dump.split('<trap_vector>:')[1].split('\n\n00000000')[0]
        # Check actual disassembled instructions in the handler, not C comments.
        ops=re.findall(r'^\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\S+)',body,re.M)
        assert not any(x.startswith(('fl','fs','fm','fc','v')) and x!='fence' for x in ops),(label,'F/V operation in ISR')
    report.append(f'PASS {label}: exit=0 entry=0x10000000 bss_end=0x{end:x} elf_sha256={hashlib.sha256(elf.read_bytes()).hexdigest()} warnings={(r.stdout+r.stderr).count("warning:")} output={out.relative_to(REPO)}')
# Semantic negative cases: no simulation claims, only testing the log checker.
cases=[('gpio-ok','gpio','[UART] ADV stage=1 gpio=1 timer=0 errors=0\n[JTAG] SUCCESS',True),
 ('timer-ok','timer','[UART] ADV stage=2 gpio=1 timer=2 errors=0\n[JTAG] SUCCESS',True),
 ('capstone-ok','capstone','[UART] ADV stage=3 gpio=1 timer=3 errors=0\n[JTAG] SUCCESS',True),
 ('eeprom-ok','eeprom','[UART] STORAGE stage=4 bytes=16 errors=0\n[JTAG] SUCCESS',True),
 ('flash-ok','flash','[UART] STORAGE stage=5 bytes=16 errors=0\n[JTAG] SUCCESS',True),
 ('missing-irq','timer','[UART] ADV stage=2 gpio=0 timer=2 errors=0\n[JTAG] SUCCESS',False),
 ('too-few-ticks','timer','[UART] ADV stage=2 gpio=1 timer=1 errors=0\n[JTAG] SUCCESS',False),
 ('corrupt','capstone','[UART] ADV stage=3 gpio=1 timer=2 errors=1\n[JTAG] SUCCESS',False),
 ('no-vip','gpio','[UART] ADV stage=1 gpio=1 timer=0 errors=0',False),
 ('blocked','capstone','[UART] ADV BLOCKED rc=16\n[JTAG] FAILED: 16',False),
 ('rtl-error','gpio','** Error: invalid\n[UART] ADV stage=1 gpio=1 timer=0 errors=0\n[JTAG] SUCCESS',False),
 ('wrong-stage','flash','[UART] STORAGE stage=4 bytes=16 errors=0\n[JTAG] SUCCESS',False)]
for label,stage,log,expected in cases:
    assert all(check(log,stage).values())==expected,label
report.append(f'PASS {len(cases)} SYNTHETIC log-checker cases (not target logs)')
# Compare legacy and one-word access code generation, without target execution.
audit=run([prefix+'gcc','-march=rv64gc_zifencei','-mabi=lp64d','-mcmodel=medany','-mstrict-align','-O2','-S',
           '-I'+str(REPO/'sw/include'),str(ROOT/'examples/dma_access_audit.c'),'-o','-'])
assert audit.returncode==0,audit.stderr
(ROOT/'evidence/advanced-dma-access.s').write_text(audit.stdout)
report.append('PASS DMA access comparison compiled to evidence/advanced-dma-access.s; this is NOT RTL lane validation')
# Preserve original protected sources against the previous teaching baseline.
baseline=json.loads((ROOT/'evidence/source_manifest.json').read_text())
for item in baseline['sources']:
    assert hashlib.sha256((REPO/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
report.append(f'PASS {len(baseline["sources"])} protected source hashes equal previous baseline')
(ROOT/'evidence/advanced-builds.txt').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
