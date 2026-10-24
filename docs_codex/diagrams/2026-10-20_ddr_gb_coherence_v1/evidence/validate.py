from pathlib import Path
import re,json,hashlib,subprocess,sys,importlib.util
import xml.etree.ElementTree as E
from zipfile import ZipFile
from urllib.parse import unquote,urlsplit
from html.parser import HTMLParser
import markdown
sys.dont_write_bytecode=True
R=Path.cwd();D=R/'docs_codex/diagrams/2026-10-20_ddr_gb_coherence_v1'; ev=D/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ev/'input.json').read_text());allowed=manifest['allowed'];fail=[]
def check(name,condition):
 if not condition:fail.append(name)
report={'date':'2026-10-20','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'failures':fail}
check('head',report['head']==manifest['head'])
changed=[p for p,h in manifest['sha256'].items() if not (R/p).is_file() or sha(R/p)!=h]
check('protected_inputs',not set(changed)-set(allowed))
report['protection']={'files':len(manifest['sha256']),'protected':len(manifest['sha256'])-len(allowed),'changed':changed,'unexpected_changes':sorted(set(changed)-set(allowed))}
# Preserve old review body: only the one entry note was inserted.
for name in ['qa','prompt']:
 p='docs_codex/maintenance/L01/reviews/ddr_gb_coherence_review_'+name+'.md'
 before=(ev/'before'/p).read_text();now=(R/p).read_text()
 extra=[l for l in now.splitlines() if l.startswith('> 2026-10-20')]
 check('historical_'+name,len(extra)==1 and now.replace(extra[0]+'\n\n','')==before)
main=R/'docs_codex/engineering/DDR_GB_Coherence_Design.md';before=(ev/'before'/main.relative_to(R)).read_text();now=main.read_text()
check('eight_chapters',len(re.findall(r'^## ',now,re.M))==8)
check('three_images',len(re.findall(r'!\[',now))==3)
check('pseudocode_unchanged',re.findall(r'```c\n(.*?)```',now,re.S)==re.findall(r'```c\n(.*?)```',before,re.S))
report['main']={'chapters':8,'images':3,'pseudocode_lines':len(re.findall(r'```c\n(.*?)```',now,re.S)[0].splitlines())}
svgns={'s':'http://www.w3.org/2000/svg'}
layouts=json.loads((D/'figures/layout.json').read_text());old=json.loads((D.parent/'2026-10-16_ddr_gb_coherence_review/figures/layout.json').read_text())
timeline=next(x for x in layouts if x['name']=='timeline');oldtime=next(x for x in old if x['name']=='timeline')
check('timeline_arrows_preserved',timeline['arrows']==oldtime['arrows'] and len(timeline['arrows'])==16)
txt=[''.join(x.itertext()) for x in E.parse(D/'figures/timeline.svg').findall('.//s:text',svgns)]
check('timeline_numbers', [int(re.match(r'^(\d+)\. ',x)[1]) for x in txt if re.match(r'^\d+\. ',x)]==list(range(1,17)))
for n in range(1,17):check('timeline_table_'+str(n),str(n) in now[now.index('| 应用层过程 |'):])
report['timeline']={'arrows':16,'geometry_order_preserved':timeline['arrows']==oldtime['arrows'],'numbered':True}
unchanged={}
for name in ['versions','handover','coverage','agent-types']:
 src=D.parent/('2026-10-16_ddr_gb_coherence_review' if name=='versions' else '2026-10-16_coherence_hybrid')/'figures'/(name+'.svg')
 unchanged[name]=sha(src)==sha(D/'figures'/(name+'.svg'));check('unchanged_'+name,unchanged[name])
report['unchanged_svgs']=unchanged
# Native PPTX save/re-read, texts, native arrows/dashes and zero bitmaps.
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
report['pptx']={};sysxml=[]
for name,figs in [('design',['system','versions','timeline']),('planning',['system','ownership','data-paths','handover','coverage','agent-types'])]:
 with ZipFile(D/'export'/name/'diagrams.pptx') as z:
  slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)];check(name+'_pages',len(slides)==len(figs));rows=[]
  sysxml.append(z.read('ppt/slides/slide1.xml'))
  for i,f in enumerate(figs,1):
   xml=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'));svg=E.parse(D/'figures'/(f+'.svg'))
   texts=[x.text or '' for x in xml.findall('.//a:t',ns)];source=[''.join(x.itertext()) for x in svg.findall('.//s:text',svgns)];check(f'{name}_{i}_texts',texts==source)
   pic=len(xml.findall('.//p:pic',ns));check(f'{name}_{i}_native',pic==0)
   arrows=sum(any(e.get('type','none')!='none' for e in ln.findall('a:headEnd',ns)+ln.findall('a:tailEnd',ns)) for ln in xml.findall('.//a:ln',ns))
   expected=len(next(l for l in layouts if l['name']==f)['arrows']);check(f'{name}_{i}_arrows',arrows==expected)
   dashes=len(xml.findall('.//a:custDash',ns)); expected_dash=sum('stroke-dasharray' in n.attrib for n in svg.getroot().iter());check(f'{name}_{i}_dashes',dashes==expected_dash)
   rows.append(dict(figure=f,texts=len(texts),arrows=arrows,dashes=dashes,pictures=pic))
  report['pptx'][name]={'sha256':sha(D/'export'/name/'diagrams.pptx'),'slides':rows}
check('same_system_page',sysxml[0]==sysxml[1])
# Validate generated integration outputs using the existing generator in memory.
p=R/'docs_codex/software/interfaces/scripts/build.py';spec=importlib.util.spec_from_file_location('integration_builder',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for slug,html,md in m.rendered():
 if slug=='integration':
  check('generated_html',(R/'docs_codex/software/interfaces/integration.html').read_text()==html)
  check('generated_markdown',(R/'docs_codex/software/interfaces/markdown/integration.md').read_text()==md)
# Local links, including GitHub-style Markdown heading IDs and explicit HTML IDs.
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set();self.base=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if tag=='base':self.base=a.get('href')
  if tag=='a' and 'href'in a:self.links.append(a['href'])
  if tag=='img' and 'src'in a:self.links.append(a['src'])
def parse(p):
 s=p.read_text();obj=Parser();obj.feed(markdown.markdown(s,extensions=['tables','fenced_code']) if p.suffix=='.md' else s)
 if p.suffix=='.md':
  seen={}
  for line in re.findall(r'^#{1,6}\s+(.+)$',s,re.M):
   plain=re.sub('<[^>]*>','',line).replace('`','').replace('*','')
   slug=re.sub(r'[^\w\-\s]','',plain.lower()).replace(' ','-');n=seen.get(slug,0);seen[slug]=n+1;obj.ids.add(slug+(f'-{n}' if n else ''))
 return obj
inputs=[R/p for p in allowed]+[D/'README.md',D/'design-preview.html',D/'architecture-preview.html',D/'supplier-preview.html']
errors=[];num=0;anchors=0
for p in inputs:
 o=parse(p);base=p.parent
 if p.parent.name=='content':base=base.parent
 if o.base:base=(base/o.base).resolve()
 for href in o.links:
  url=urlsplit(href)
  if url.scheme or href.startswith('//'):continue
  path=unquote(url.path);q=(base/path).resolve() if path else p
  num+=1
  if not q.exists():errors.append([str(p.relative_to(R)),href,'missing file']);continue
  if url.fragment and q.suffix in ['.md','.html']:
   anchors+=1
   if unquote(url.fragment) not in parse(q).ids:errors.append([str(p.relative_to(R)),href,'missing anchor'])
report['local_links']={'checked':num,'anchors':anchors,'errors':errors};check('local_links',not errors)
for rel in ['render-02/browser.json','ppt-design-render/browser.json','ppt-planning-render/browser.json','document-browser.json']:
 data=json.loads((ev/rel).read_text());check(rel,data['status']=='pass')
 if rel=='document-browser.json':
  for doc in data['documents']:check('preview_fresh_'+doc['source'],sha(R/doc['source'])==doc['sha256'])
report['visual_review']={'svg_full_pages':8,'pptx_full_pages':9,'details':['SVG system path','PPTX system path','PPTX timeline frontend'],'ppt_preview':'DrawingML subset + local font metrics + Chrome; not Office','office_tested':False}
proc=subprocess.run(['git','diff','--check'],text=True,capture_output=True);check('diff_check',proc.returncode==0);report['diff_check']=proc.stdout+proc.stderr
report['status']='pass' if not fail else 'fail'
(ev/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['protection','pptx']},ensure_ascii=False,indent=2));print('protected',report['protection']['protected']);print('changed',len(changed))
raise SystemExit(bool(fail))
