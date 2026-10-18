#!/usr/bin/env python3
"""Local Chrome render and geometry review; create a new evidence directory."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,subprocess,tempfile,time,json,socket,base64,os,struct,http.client,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
a=argparse.ArgumentParser();a.add_argument('--out-dir',required=True);args=a.parse_args()
OUT=Path(args.out_dir).resolve();OUT.mkdir(parents=True,exist_ok=False)
source=(ROOT/'docs_codex/learning/scripts/preview_structure_site.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='CDP')
exec(compile(ast.Module(body=[node],type_ignores=[]),'course_cdp_client','exec'))
profile=tempfile.mkdtemp(prefix='software-stack-industrial-')
p=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=(OUT/'chrome.log').open('w'))
report={'date':'2026-10-14','office_application_tested':False}
try:
 f=Path(profile)/'DevToolsActivePort'
 for _ in range(100):
  if f.exists():break
  if p.poll() is not None:raise RuntimeError('Chrome exited: see chrome.log')
  time.sleep(.05)
 conn=http.client.HTTPConnection('127.0.0.1',int(f.read_text().splitlines()[0]));conn.request('GET','/json');targets=json.loads(conn.getresponse().read());cdp=CDP(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'))
 cdp.call('Page.enable');cdp.call('Runtime.enable')
 def go(path):
  uri=path.as_uri();cdp.call('Page.navigate',{'url':uri})
  for _ in range(100):
   try:
    if cdp.js('location.href')==uri and cdp.js('document.readyState')=='complete':break
   except Exception:pass
   time.sleep(.03)
  cdp.js('document.fonts.ready.then(()=>true)')
 svg=D/'software-stack-industrial.svg';layout=json.loads((D/'layout.json').read_text())
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':2880,'height':1620,'deviceScaleFactor':1,'mobile':False});go(svg)
 bounds=json.loads(cdp.js('JSON.stringify([...document.querySelectorAll("text")].map(t=>({text:t.textContent,anchorX:+t.getAttribute("x"),baseline:+t.getAttribute("y"),...Object.fromEntries(["x","y","width","height"].map(k=>[k,t.getBBox()[k]]))})))'))
 outside=[t['text'] for t in bounds if t['x']<0 or t['y']<0 or t['x']+t['width']>2880 or t['y']+t['height']>1620]
 hits=[];box_overflow=[]
 for edge in layout['arrows']:
  for (x1,y1),(x2,y2) in zip(edge['points'],edge['points'][1:]):
   assert x1==x2 or y1==y2,edge['id']
   for t in bounds:
    l,top,rr,bot=t['x']+2,t['y']+2,t['x']+t['width']-2,t['y']+t['height']-2
    if (x1==x2 and l<x1<rr and max(min(y1,y2),top)<min(max(y1,y2),bot)) or (y1==y2 and top<y1<bot and max(min(x1,x2),l)<min(max(x1,x2),rr)):
     hits.append([edge['id'],t['text']])
 for name,b in layout['boxes'].items():
  for t in bounds:
   if abs(t['anchorX']-b['x']-b['width']/2)<1 and b['y']<t['baseline']<b['y']+b['height']:
    if t['x']<b['x']+7 or t['x']+t['width']>b['x']+b['width']-7 or t['y']+t['height']>b['y']+b['height']-3:
     box_overflow.append([name,t['text']])
 cdp.shot('software-stack-industrial.png')
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':1920,'height':1080,'deviceScaleFactor':1,'mobile':False})
 cdp.js('document.documentElement.setAttribute("width","1920");document.documentElement.setAttribute("height","1080")')
 cdp.shot('presentation-1920.png')
 report.update(svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),text_bounds=bounds,outside_canvas=outside,text_line_intersections=hits,box_text_overflow=box_overflow)
 page=D/'index.html'
 if page.exists():
  report['comparison_page']=[]
  for width,height in [(1440,1000),(390,844)]:
   cdp.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False});go(page)
   data=json.loads(cdp.js('JSON.stringify({overflow:document.documentElement.scrollWidth>innerWidth+1,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0)})'))
   assert not data['overflow'] and data['images'],data
   cdp.shot(f'comparison-{width}.png');report['comparison_page'].append(dict(width=width,**data))
 report['status']='pass' if not (outside or hits or box_overflow) else 'needs-layout-adjustment'
finally:
 p.terminate();p.wait(timeout=10);(OUT/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='text_bounds'},ensure_ascii=False,indent=2))
