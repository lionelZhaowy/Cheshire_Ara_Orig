"""Read-only source checks for L01-S; no site generation or target execution."""
from pathlib import Path
from html.parser import HTMLParser
import json, re, hashlib, sys
ROOT = Path(__file__).resolve().parents[5]
CONTENT = ROOT / 'docs_codex/learning/content'
EVIDENCE = Path(__file__).resolve().parent
NAMES = ['architecture','cva6','configuration','runtime','build','boot','boot-debug','traps','software-debug']
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.images=[]; self.headings=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.append(d['id'])
        if tag in ['h2','h3']: self.headings.append((tag,d.get('id')))
        if tag=='a' and 'href' in d: self.links.append(d['href'])
        if tag=='img': self.images.append(d.get('src'))
def parse(path):
    p=Parser();p.feed(path.read_text());return p
failures=[];results={};old_count=0;link_count=0
for name in NAMES:
    path=CONTENT/(name+'.html');p=parse(path)
    if len(p.ids)!=len(set(p.ids)): failures.append([name,'duplicate ids'])
    if any(not anchor for _,anchor in p.headings):failures.append([name,'heading has no id'])
    before=EVIDENCE/'before'/(name+'.html')
    if before.exists():
        old=parse(before); old_count+=len(old.ids)
        missing=sorted(set(old.ids)-set(p.ids))
        if missing:failures.append([name,'removed legacy ids',missing])
        if sorted(old.images)!=sorted(p.images):failures.append([name,'changed figure references'])
    for href in p.links:
        if href.startswith(('http:','https:','mailto:')):continue
        target,_,anchor=href.partition('#')
        if not target: dest=path
        elif target.endswith('.html') and '/' not in target: dest=CONTENT/target
        else:dest=ROOT/'docs_codex/learning'/target
        link_count+=1
        if not dest.exists():failures.append([name,'target missing',href]);continue
        if anchor and dest.suffix=='.html' and anchor not in parse(dest).ids:failures.append([name,'anchor missing',href])
    results[name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'heading_ids':[a for _,a in p.headings],'image_count':len(p.images)}
checks=[('build sequence', ['translation-units','elf','layout','software-options'], 'build'),('default boot before alternatives',['default-path','rom','default-load','crt','normal-result','platform-rom','serial-link','sd-boot','later-stages'],'boot'),('CPU usage before reference',['programmer-state','privilege','csr-trap','memory-protection','implementation-reference','resource-consequences'],'cva6'),('traps causal order',['call-versus-trap','trap-entry','software-context','normal-service','trap-return','syscall-scheduling'],'traps')]
for title,ids,name in checks:
    headings=results[name]['heading_ids']; positions=[headings.index(i) for i in ids]
    if positions!=sorted(positions):failures.append([name,title])
# Formula is an independent expected value of the existing source algorithm.
assert sum(3*i+1 for i in range(137))==28085
print(json.dumps({'root':str(ROOT),'old_anchors_preserved':old_count,'local_links_checked':link_count,'pages':results,'failures':failures,'sum137':28085,'scope':'HTML source/link/order and formula only; no generation/browser/target execution'},ensure_ascii=False,indent=2))
sys.exit(bool(failures))
