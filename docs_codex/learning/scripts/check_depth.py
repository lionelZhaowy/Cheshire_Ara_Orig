#!/usr/bin/env python3
"""Validate depth extension artifacts; never invokes RTL or invents target logs."""
from pathlib import Path
import hashlib,json,re,subprocess,tempfile,os
R=Path(__file__).resolve().parent.parent;repo=R.parent.parent;os.chdir(repo)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=['2026-09-29 L01 depth extension checks','Scope: documentation and independent software examples; no target execution.']
backup=R.parent/'learning_backup';m=json.loads((R/'evidence/restructure-backup.json').read_text())
assert {str(p.relative_to(backup)) for p in backup.rglob('*') if p.is_file()}==set(m['files'])
for name,item in m['files'].items():assert sha(backup/name)==item['sha256'],name
report.append(f'PASS backup unchanged: {len(m["files"])} files, {sum(x["bytes"] for x in m["files"].values())} bytes')
m=json.loads((R/'evidence/depth-20260929-input.json').read_text())
history={n:h for n,h in m['files'].items() if n.startswith('evidence/')}
for n,h in history.items():assert sha(R/n)==h,n
report.append(f'PASS pre-extension evidence unchanged: {len(history)} files')
m=json.loads((R/'evidence/depth-20260929-sources.json').read_text())
for n,h in m['files'].items():assert sha(repo/n)==h,n
report.append(f'PASS current source provenance: {len(m["files"])} hashes')
outputs=list(R.glob('*.html'))+list((R/'assets').glob('depth-*.svg'))
before={str(p):sha(p) for p in outputs}
for s in ['build_depth_diagrams.py','build_waves.py','build_site.py']:
 x=subprocess.run(['python3',str(R/'scripts'/s)],capture_output=True,text=True);assert x.returncode==0,x.stdout+x.stderr
assert before=={str(p):sha(p) for p in outputs},'non-deterministic generation'
report.append(f'PASS deterministic regeneration: {len(outputs)} generated HTML/SVG files')
for p in (R/'scripts').glob('*.py'):compile(p.read_text(),str(p),'exec')
report.append('PASS Python source syntax')
# Synthetic fixtures validate only log parser behavior, never CPU execution.
normal='[UART] LEARN stage=5 Hello Cheshire!\n[UART] RVV checked=137\n[UART] RVV_REDUCE n=137 sum=28085\n[UART] RVV_DEPTH cases=6 errors=0\n[UART] LEARN sum=28085 errors=0\n[JTAG] SUCCESS\n'
cases=[('complete synthetic fixture',normal,0),('missing reduction',normal.replace('[UART] RVV_REDUCE n=137 sum=28085\n',''),1),('wrong sum',normal.replace('RVV_REDUCE n=137 sum=28085','RVV_REDUCE n=137 sum=0'),1),('case failure',normal.replace('cases=6 errors=0','cases=6 errors=1'),1),('wrong stage',normal.replace('stage=5','stage=1'),1),('missing target completion',normal.replace('[JTAG] SUCCESS',''),1),('simulation error',normal+'** Error: injected\n',1),('software failure',normal.replace('LEARN sum=28085 errors=0','LEARN sum=28084 errors=1'),1)]
with tempfile.TemporaryDirectory(prefix='l01-parser-') as td:
 for name,body,expected in cases:
  p=Path(td)/'synthetic.log';p.write_text(body)
  x=subprocess.run(['python3',str(R/'scripts/check_run.py'),str(p),'--stage','rvv','--depth'],capture_output=True,text=True)
  assert x.returncode==expected,(name,x.stdout,x.stderr)
  report.append('PASS parser-only synthetic case: '+name)
# Small waveform checks catch misleading handshake teaching data.
for p in (R/'assets/waves').glob('*.json'):
 w=json.loads(p.read_text());assert '教学'in w['head']['text'];assert (R/'assets'/('depth-'+p.stem+'.svg')).exists()
 def samples(w):
  result=[]
  for char in w:
   assert char!='|','not used in these simple checks'
   result.append(result[-1] if char=='.' else char)
  return result
 sig={x['name']:samples(x['wave']) for x in w['signal']}
 if p.stem=='axi-backpressure':
  for v,r,data in [('AWVALID','AWREADY',['AWADDR/ID']),('WVALID','WREADY',['WDATA','WSTRB','WLAST']),('BVALID','BREADY',['BRESP/BID'])]:
   for i in range(len(sig[v])-1):
    if sig[v][i]=='1' and sig[r][i]=='0':assert sig[v][i+1]=='1' and all(sig[d][i]==sig[d][i+1] for d in data),(p,i,v)
  assert sum(v==r=='1' for v,r in zip(sig['WVALID'],sig['WREADY']))==2
 if p.stem=='vector-load':
  for i in range(len(sig['RVALID'])-1):
   if sig['RVALID'][i]=='1' and sig['RREADY'][i]=='0':assert sig['RDATA'][i]==sig['RDATA'][i+1],i
report.append('PASS six editable WaveDrom teaching sources; AXI and load backpressure payload stability')
changed=subprocess.check_output(['git','diff','--name-only','-z'],text=True).split('\0');assert all(not x or x.startswith('docs_codex/') for x in changed)
assert not subprocess.check_output(['git','diff','--name-only','--','hw','sw','target','.bender','Bender.yml','Bender.lock','cheshire.mk','Makefile'],text=True).strip()
report.append('PASS tracked changes confined to docs_codex; production RTL/sw/platform/dependencies unchanged')
x=subprocess.run(['git','diff','--check'],capture_output=True,text=True);assert x.returncode==0,x.stdout+x.stderr
report.append('PASS git diff --check')
# Write this real partial result so the self-referencing report link exists before site validation.
output=R/'evidence/depth-20260929-checks.txt';output.write_text('\n'.join(report)+'\nSite check pending within this invocation.\n')
x=subprocess.run(['python3',str(R/'scripts/check_site.py')],capture_output=True,text=True);assert x.returncode==0,x.stdout+x.stderr
report.append(x.stdout.strip())
report.append('NOT RUN: production RTL compile/elaboration/simulation, board, performance, NPU integration, synthesis, ASIC extraction.')
output.write_text('\n'.join(report)+'\n');print('\n'.join(report))
