#!/usr/bin/env python3
"""Record the bounded local sources cited by hardware lessons; not a validation result."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];LEARN=ROOT/'docs_codex/learning'
PAGES=['hardware','rtl-elaboration','cpu-config','soc-topology','axi-crossbar','axi-adapters','hardware-memory','hardware-devices','hardware-platform','ip-integration','hardware-labs']
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=set()
 def handle_starttag(self,tag,attrs):
  h=dict(attrs).get('href','')
  if h.startswith('../../'):self.links.add(h[6:])
a=Links()
for name in PAGES:a.feed((LEARN/'content'/(name+'.html')).read_text())
entries=[]
for name in sorted(a.links):
 p=ROOT/name
 if not p.is_file():raise SystemExit('Missing cited source '+name)
 entries.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
data={'date':'2026-09-23','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'evidence':'bounded cited local source snapshot; no production RTL simulation','sources':entries}
(LEARN/'evidence/hardware-source-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Recorded',len(entries),'cited source hashes')
