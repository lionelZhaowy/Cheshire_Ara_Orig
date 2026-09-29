#!/usr/bin/env python3
"""Verify this restructuring snapshot and preserve its evidence boundaries."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path(__file__).resolve().parent.parent;b=r.parent/'learning_backup';repo=r.parent.parent
# Git subprocesses use this repository even when invoked from another directory.
import os
os.chdir(repo)
report=['2026-09-28 L01 final integrity checks','Scope: documentation / independent software build inputs; NO production RTL execution.']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((r/'evidence/restructure-backup.json').read_text())
assert {str(p.relative_to(b)) for p in b.rglob('*') if p.is_file()}==set(m['files'])
for name,item in m['files'].items():
 assert sha(b/name)==item['sha256'],name
 assert (b/name).stat().st_size==item['bytes'],name
report.append(f'PASS backup: {len(m["files"])} files, {sum(x["bytes"] for x in m["files"].values())} bytes; exact SHA256 and file set')
history={n:item for n,item in m['files'].items() if n.startswith('evidence/')}
for n,item in history.items():assert (r/n).is_file() and sha(r/n)==item['sha256'],n
report.append(f'PASS preserved historical evidence: {len(history)} original files unchanged')
sm=json.loads((r/'evidence/restructure-sources.json').read_text())
for n,h in sm['files'].items():assert sha(repo/n)==h,n
report.append(f'PASS current source/reference provenance: {len(sm["files"])} hashes match')
# Site generation includes references and figures; same source inputs produce identical bytes.
outputs=list(r.glob('*.html'))+list((r/'assets').glob('new-*.svg'))+[r/'content/registers.html',r/'evidence/restructure-register-sources.json']
before={str(p):sha(p) for p in outputs}
for script in ['build_diagrams.py','build_registers.py','build_site.py']:
 p=subprocess.run(['python3',str(r/'scripts'/script)],text=True,capture_output=True);assert p.returncode==0,p.stderr
assert before=={str(p):sha(p) for p in outputs}
report.append(f'PASS deterministic regeneration: {len(outputs)} generated files unchanged')
p=subprocess.run(['python3',str(r/'scripts/check_site.py')],text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;report.append(p.stdout.strip())
for p in (r/'scripts').glob('*.py'):compile(p.read_text(),str(p),'exec')
report.append('PASS Python source syntax (no simulator invocation)')
pages=json.loads((r/'scripts/pages.json').read_text());slugs={x[0] for x in pages};legacy=set(json.loads((r/'scripts/legacy_links.json').read_text()))-slugs
for slug,_,_ in pages:
 text=(r/'content'/f'{slug}.html').read_text()
 assert all(name.startswith('new-') for name in re.findall(r'src="assets/([^"]+)"',text)),slug
 assert not set(re.findall(r'href="([\w-]+)\.html',text)) & legacy,slug
report.append('PASS main content uses only new figures and does not depend on retired teaching pages')
oldparas=set()
for p in (b/'content').glob('*.html'):oldparas.update(re.findall(r'<p>(.*?)</p>',p.read_text(),re.S))
reused=[]
for slug,_,_ in pages:
 if slug=='registers':continue
 for para in re.findall(r'<p>(.*?)</p>',(r/'content'/f'{slug}.html').read_text(),re.S):
  if len(re.sub('<[^>]+>','',para))>35 and para in oldparas:reused.append(slug)
report.append(f'Editorial audit: {len(reused)} verbatim old paragraphs (>35 characters), excluding generated register reference')
changed=subprocess.check_output(['git','diff','--name-only','-z'],text=True).split('\0');assert all(not x or x.startswith('docs_codex/') for x in changed)
assert not subprocess.check_output(['git','diff','--name-only','--','hw','sw','target','.bender','Bender.yml','Bender.lock','cheshire.mk','Makefile'],text=True).strip()
report.append('PASS tracked changes confined to docs_codex; production RTL/sw/platform/dependencies/shared build inputs unchanged')
p=subprocess.run(['git','diff','--check'],text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr
report.append('PASS git diff --check')
report.append('Not executed: production RTL compilation/elaboration, full SoC simulation, synthesis, board operations, ASIC extraction, or repeat of historical Reg unit.')
(r/'evidence/restructure-checks.txt').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
