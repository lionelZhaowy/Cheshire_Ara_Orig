from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import hashlib,json,subprocess
repo=Path(__file__).resolve().parents[5]
site=repo/'docs_codex/learning'
names=['rtos','virtual-memory','linux','os-devices','os-debug']
class Page(HTMLParser):
 def __init__(self,p):
  super().__init__();self.ids=[];self.links=[];self.headings=[];self.feed(p.read_text())
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag in ['h2','h3']:self.headings.append((tag,a.get('id')))
  if tag=='a' and 'href' in a:self.links.append(a['href'])
fail=[];count=0
for name in names:
 p=site/'content'/f'{name}.html';d=Page(p)
 duplicates=[x for x,c in Counter(d.ids).items() if c>1]
 if duplicates:fail.append((name,'duplicate ids',duplicates))
 if any(x[1] is None for x in d.headings):fail.append((name,'missing heading id'))
 for href in d.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  target=(site/unquote(u.path)).resolve() if u.path else p
  if target.parent==site and target.suffix=='.html' and (site/'content'/target.name).exists():target=site/'content'/target.name
  if not target.exists():fail.append((name,'missing target',href));continue
  if u.fragment and target.suffix=='.html' and unquote(u.fragment) not in Page(target).ids:fail.append((name,'missing id',href))
  count+=1
 print(name,'bytes',p.stat().st_size,'headings',len(d.headings),'ids',len(d.ids))
print('local links checked',count)
print('sum',sum(3*i+1 for i in range(137)))
a=0x40001008
print('Sv39 indices',[(a>>n)&511 for n in (30,21,12)],'offset',hex(a&4095),'physical',hex(0x80021000+(a&4095)))
assert sum(3*i+1 for i in range(137))==28085
assert [(a>>n)&511 for n in (30,21,12)]==[1,0,1]
assert (a&4095)==8
if fail:
 print(json.dumps(fail,ensure_ascii=False,indent=2));raise SystemExit(1)
print('PASS: five source pages structure/links and teaching arithmetic; no OS target execution')
