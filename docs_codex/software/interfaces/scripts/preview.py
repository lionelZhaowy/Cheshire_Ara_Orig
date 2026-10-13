#!/usr/bin/env python3
"""Reuse the course CDP client; preview only this topic, with fresh evidence."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,subprocess,tempfile,time,json,socket,base64,os,struct,http.client,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--out-dir',required=True);args=parser.parse_args()
OUT=Path(args.out_dir).resolve();OUT.mkdir(parents=True,exist_ok=False)
source=(ROOT.parents[1]/'learning/scripts/preview_structure_site.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='CDP')
exec(compile(ast.Module(body=[node],type_ignores=[]),'course_cdp_client','exec'))
files=list(ROOT.glob('*.html'))
initial={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
profile=tempfile.mkdtemp(prefix='l01-interface-chrome-')
cmd=['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank']
p=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=(OUT/'chrome.log').open('w'))
report={'pages':[],'figures':[],'html_sha256':initial}
try:
 f=Path(profile)/'DevToolsActivePort'
 for _ in range(100):
  if f.exists():break
  if p.poll() is not None:raise RuntimeError('Chrome exited; see chrome.log')
  time.sleep(.05)
 port=int(f.read_text().splitlines()[0]);conn=http.client.HTTPConnection('127.0.0.1',port);conn.request('GET','/json');targets=json.loads(conn.getresponse().read());cdp=CDP(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'))
 cdp.call('Page.enable');cdp.call('Runtime.enable')
 def go(path):
  uri=path.as_uri();cdp.call('Page.navigate',{'url':uri})
  for _ in range(100):
   try:
    if cdp.js('location.href')==uri and cdp.js('document.readyState')=='complete':break
   except Exception:pass
   time.sleep(.03)
  cdp.js('document.fonts.ready.then(()=>true)')
 for w,h in [(1440,1000),(390,844)]:
  cdp.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
  for path in files:
   go(path)
   data=cdp.js('''JSON.stringify({title:document.title,overflow:document.documentElement.scrollWidth>innerWidth+1,images:[...document.images].map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0})),headings:document.querySelectorAll('h2,h3').length,nav:document.querySelectorAll('nav[aria-label="章节"] a').length})''')
   data=json.loads(data);data.update(page=path.name,width=w)
   assert not data['overflow'],data
   assert data['nav']==8 and data['headings']>0,data
   assert all(i['ok'] for i in data['images']),data
   report['pages'].append(data)
   if path.stem in ('index','cases','integration','labs'):cdp.shot(f'{path.stem}-{w}.png')
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':1400,'height':900,'deviceScaleFactor':1,'mobile':False})
 figure_dir=ROOT.parents[1]/'diagrams/2026-10-13_software_hardware_interfaces'
 for path in figure_dir.glob('*.svg'):
  go(path)
  boxes=json.loads(cdp.js('JSON.stringify([...document.querySelectorAll("text")].map(t=>({text:t.textContent,...Object.fromEntries(["x","y","width","height"].map(k=>[k,t.getBBox()[k]]))})))'))
  assert all(b['x']>=-1 and b['y']>=-1 and b['x']+b['width']<=1401 and b['y']+b['height']<=901 for b in boxes),boxes
  cdp.shot(f'figure-{path.stem}.png')
  report['figures'].append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'text_bounds':boxes})
 assert initial=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'HTML changed while previewing'
 report['status']='pass'
finally:
 p.terminate();p.wait(timeout=10)
 (OUT/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(report['pages']),'page viewports;',len(report['figures']),'SVG previews')
