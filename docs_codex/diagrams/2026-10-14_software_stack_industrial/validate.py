#!/usr/bin/env python3
"""Check new diagram against protected inputs; never overwrite a validation report."""
from pathlib import Path
import argparse,json,hashlib,zipfile,re,subprocess
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
D=Path(__file__).resolve().parent;R=D.parents[2];E=D/'evidence'
a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();out=args.out.resolve()
assert not out.exists(),'Choose a new report path'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
i=json.loads((E/'input.json').read_text());b=json.loads((E/'render-final/browser.json').read_text());ex=json.loads((D/'export/export_report.json').read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==i['head']
a=json.loads((D.parent/'2026-10-13_complete_software_stack/layout.json').read_text());n=json.loads((D/'layout.json').read_text())
assert set(a['boxes'])==set(n['boxes']);assert [x['id'] for x in a['arrows']]==[x['id'] for x in n['arrows']]
def ports(layout,point):
 x,y=point;res=[]
 for name,z in layout['boxes'].items():
  x0,y0=z['x'],z['y'];x1,y1=x0+z['width'],y0+z['height'];tol=.1
  if ((abs(x-x0)<tol or abs(x-x1)<tol) and y0-tol<=y<=y1+tol) or ((abs(y-y0)<tol or abs(y-y1)<tol) and x0-tol<=x<=x1+tol):res.append(name)
 return res
edges=[]
for oe,ne in zip(a['arrows'],n['arrows']):
 op=[ports(a,oe['points'][0]),ports(a,oe['points'][-1])];np=[ports(n,ne['points'][0]),ports(n,ne['points'][-1])]
 assert op==np,(oe['id'],op,np)
 edges.append({'id':oe['id'],'same_source_and_destination':True,'source':op[0],'destination':op[1]})
protected={p:sha(R/p)==h for p,h in i['protected'].items()};assert all(protected.values())
source_snapshot=json.loads((R/'docs_codex/software/interfaces/evidence/complete-stack-20261013/sources.json').read_text())
for name,h in source_snapshot['files'].items():
 if not name.startswith('docs_codex/'):assert sha(R/name)==h,name
assert b['status']=='pass';assert ex['figures'][0]['sha256']==sha(D/'software-stack-industrial.svg')==b['svg_sha256']
assert sha(D/'software-stack-industrial.png')==sha(E/'render-final/software-stack-industrial.png')
with zipfile.ZipFile(D/'export/diagrams.pptx') as z:
 assert not [f for f in z.namelist() if f.startswith('ppt/media/')]
 slides=[f for f in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',f)];assert len(slides)==1
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('src','href'):self.links.append(v)
links=[]
for name in ['index.html','README.md']:
 p=D/name;text=p.read_text();parser=Links();parser.feed(text);urls=parser.links+re.findall(r'\]\(([^)]+)\)',text)
 for url in urls:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  dest=(p.parent/unquote(u.path)).resolve();assert dest.exists() or dest==out,(name,url)
  if u.fragment and dest.suffix=='.html':assert f'id="{u.fragment}"' in dest.read_text(),url
  links.append(url)
obj={'date':'2026-10-14','status':'pass','head':i['head'],'scope':'industrial diagram and comparison page only','canvas':n['canvas'],'aspect_ratio':'16:9','component_groups':len(n['boxes']),'arrows':len(edges),'same_endpoint_relationships':edges,'all_old_artifacts_and_chapter_inputs_unchanged':all(protected.values()),'unchanged_source_references':i['unchanged_source_references'],'local_links_checked':len(links),'browser_status':b['status'],'visual_review':'Author inspected final 1920x1080 diagram and desktop/mobile comparison previews; no clipping or text/line overlap','pptx_native_structure':ex['slides'][0],'pptx_whole_image_media':False,'office_application_tested':False,'software_build_or_target_run':False,'artifacts':{str(p.relative_to(R)):sha(p) for p in [D/'software-stack-industrial.svg',D/'software-stack-industrial.png',D/'export/diagrams.pptx',D/'index.html',D/'build_figure.py',D/'preview.py',Path(__file__).resolve()]}}
with out.open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('PASS:',len(n['boxes']),'groups;',len(edges),'same edge endpoints;',len(links),'links;',len(protected),'old artifacts/inputs protected')
