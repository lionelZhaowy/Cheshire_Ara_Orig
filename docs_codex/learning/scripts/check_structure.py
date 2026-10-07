#!/usr/bin/env python3
"""Read-only course checks; --check-generated compares generation in a temporary copy."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,re,subprocess,tempfile,shutil,os
from build_site import ENTRIES,PARTS,MIGRATIONS
from report_run import start_run
R=Path(__file__).resolve().parent.parent;repo=R.parent.parent
args,OUT,META=start_run('checks',extra=True)
(OUT/'checks.txt').write_text('RUNNING: '+META['started_at']+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(OUT)}
before=snapshot(R)
report=[META['started_at'],'HEAD: '+META['head'],'Output: '+str(OUT),'Mode: read-only working tree; reports only in new output directory.']
def run(script,cwd=repo,args=()):
 x=subprocess.run([sys.executable,str(script),*map(str,args)],cwd=cwd,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 assert x.returncode==0,x.stdout+x.stderr
 return x.stdout.strip()
try:
 baseline=json.loads((R/'evidence/refinement-20260929-input.json').read_text())
 protected={n:h for n,h in baseline['files'].items() if n.startswith(('evidence/','examples/','assets/'))}
 for n,h in protected.items():assert sha(R/n)==h,('historical asset modified',n)
 assert sha(R.parent/'handoffs/2026-09-29_L01_structure_revision_review.md')==baseline['review_sha256']
 report.append(f'PASS {len(protected)} prior evidence/example/asset files unchanged; review preserved')
 b=R.parent/'learning_backup';m=json.loads((R/'evidence/restructure-backup.json').read_text())['files']
 assert {str(p.relative_to(b)) for p in b.rglob('*') if p.is_file()}==set(m)
 for n,item in m.items():assert sha(b/n)==item['sha256'],n
 report.append(f'PASS backup unchanged: {len(m)} files')
 assert len(PARTS)==7 and len(ENTRIES)==34
 assert [p['number'] for p in ENTRIES if p['kind']=='chapter']==list(range(1,31))
 bodies={p['slug']:(R/'content'/f'{p["slug"]}.html').read_text() for p in ENTRIES}
 for old,dest in MIGRATIONS.items():
  f,_,anchor=dest.partition('#');assert f[:-5] in bodies
  if anchor:assert f'id="{anchor}"' in bodies[f[:-5]],(old,dest)
 report.append(f'PASS seven parts / 30 chapters; {len(MIGRATIONS)} canonical migrations')
 assert sha(R/'content/registers.html')==baseline['files']['content/registers.html']
 sources=json.loads((R/'evidence/refinement-20260929/sources.json').read_text())['files']
 for n,h in sources.items():assert sha(repo/n)==h,n
 report.append(f'PASS register index unchanged and {len(sources)} targeted source hashes')
 nums={p['slug']:p['number'] for p in ENTRIES if p['kind']=='chapter'}
 for slug,body in bodies.items():
  for target,number in re.findall(r'<a href="([a-z-]+)\.html[^\"]*">第\s*(\d+)\s*章</a>',body):assert nums[target]==int(number),(slug,target,number)
  plain=re.sub(r'<a\b.*?</a>|<pre\b.*?</pre>','',body,flags=re.S)
  assert not re.search(r'第\s*\d+\s*章',plain),('unlinked chapter number',slug)
 required={'adapters':'dma.html#lanes','memory':'accelerators.html#ddr','integration':'accelerators.html#npu-topology','stream-io':'boot.html#serial-link','models':'labs.html#rvv-depth'}
 for slug,target in required.items():assert f'href="{target}"' in bodies[slug],(slug,target)
 assert '本章数组运算' not in bodies['models'] and '本章的非整倍' not in bodies['models']
 for ident in ['serial-link','uart-passive','gpt-raw','sd-boot','nor-boot','eeprom-boot']:assert f'<h3 id="{ident}">' in bodies['boot']
 assert bodies['boot-debug'].index('id="transport"')<bodies['boot-debug'].index('id="dmi-registers"')
 report.append('PASS chapter-number targets, reviewed topic links, boot subdivisions and Debug definition order')
 report.append(run(R/'scripts/check_site.py'))
 changes={n:{'before':h,'after':sha(R/n) if (R/n).exists() else None} for n,h in baseline['files'].items() if n.startswith('content/') and (not (R/n).exists() or sha(R/n)!=h)}
 (OUT/'content-changes.json').write_text(json.dumps(changes,indent=2)+'\n')
 if args.check_generated:
  with tempfile.TemporaryDirectory(prefix='l01-regen-') as td:
   clone=Path(td)/'repo/docs_codex/learning';clone.mkdir(parents=True)
   for folder in ['content','scripts','assets','figure_archive']:shutil.copytree(R/folder,clone/folder,ignore=shutil.ignore_patterns('__pycache__'))
   for p in R.glob('*.html'):shutil.copy2(p,clone/p.name)
   # Register extraction reads a bounded set of headers, copied as ordinary files.
   from build_registers import GROUPS
   for _,_,name,_ in GROUPS:
    target=clone.parent.parent/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/name,target)
   for name in ['build_registers.py','build_diagrams.py','build_depth_diagrams.py','build_mechanism_diagrams.py','build_waves.py','build_site.py']:run(clone/'scripts'/name,cwd=clone)
   fresh=clone/'_research-figures'
   run(clone/'scripts/build_research_figures.py',cwd=clone,args=['--out-dir',fresh])
   for p in fresh.iterdir():assert sha(p)==sha(R/'assets/figures-20261007'/p.name),('research figure generation mismatch',p.name)
   report.append('PASS 37 research SVG masters and manifest regenerated in a fresh temporary directory')
   products=list(clone.glob('*.html'))+list((clone/'assets').glob('*.svg'))+[clone/'content/registers.html']
   for p in products:assert sha(p)==sha(R/p.relative_to(clone)),('generated mismatch',str(p.relative_to(clone)))
   report.append(f'PASS temporary-copy generation matches {len(products)} products; no worktree regeneration')
 else:report.append('SKIP generation comparison (request --check-generated explicitly)')
 assert snapshot(R)==before,'check modified site files'
 report.append('PASS read-only site hashes before/after; old evidence never rewritten')
 report.append('NOT RUN: software build, RTL compile/simulation, board, performance or ASIC implementation.')
 (OUT/'checks.txt').write_text('\n'.join(report)+'\n');print('\n'.join(report))
except BaseException as e:
 (OUT/'checks.txt').write_text('\n'.join(report)+'\nFAIL: '+str(e)+'\n');raise
