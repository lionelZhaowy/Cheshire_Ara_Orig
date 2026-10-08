from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,math,hashlib,json,subprocess
root=Path(__file__).resolve().parents[3]
p=root/'docs_codex/M01_IP_DDR_Interface_Contract.md'
class P(HTMLParser):
 def __init__(self,t):super().__init__();self.ids=set();self.feed(t)
 def handle_starttag(self,t,a):
  d=dict(a)
  if 'id'in d:self.ids.add(d['id'])
errors=[];n=0;sources={}
for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
 u=urlsplit(href)
 if u.scheme:continue
 f=(p.parent/unquote(u.path)).resolve()
 if f.suffix=='.html' and f.parent==root/'docs_codex/learning' and (f.parent/'content'/f.name).exists():f=f.parent/'content'/f.name
 if not f.exists():errors.append(href);continue
 if u.fragment and f.suffix=='.html' and unquote(u.fragment) not in P(f.read_text()).ids:errors.append(href)
 n+=1
 if not str(f.relative_to(root)).startswith('docs_codex'):sources[str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
frame=1920*1080*2;rate=frame*60
assert frame==4147200 and 2*frame==8294400 and rate==248832000 and rate*2==497664000
assert math.ceil(rate/10000)==24884
assert '0x100000000' in p.read_text()
print('links',n,'missing',errors)
print('frame',frame,'two_buffers',2*frame,'B/s',rate,'write_read_B/s',rate*2,'100us_lower_bound',math.ceil(rate/10000))
for name in ['axi_riscv_lrsc.sv','axi_riscv_amos.sv']:
 f=root/'.bender/git/checkouts/axi_riscv_atomics-40ad8d2d0e0daa8b/src'/name
 sources[str(f.relative_to(root))]=hashlib.sha256(f.read_bytes()).hexdigest()
print('source files',len(sources))
if '--snapshot' in __import__('sys').argv:
 data={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_hashes':sources,'contract_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'static documentation only'}
 (Path(__file__).parent/'sources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
assert not errors
print('PASS; no target validation')
