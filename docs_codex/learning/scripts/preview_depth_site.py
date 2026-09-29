#!/usr/bin/env python3
"""Check the current offline course using local Chrome/CDP; never invokes RTL tools."""
import subprocess,tempfile,time,json,socket,base64,os,struct,http.client,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PAGES=json.loads((ROOT/'scripts/pages.json').read_text())
class CDP:
 def __init__(self,url):
  from urllib.parse import urlsplit
  u=urlsplit(url);self.s=socket.create_connection((u.hostname,u.port),timeout=15);self.n=0;self.events=[]
  key=base64.b64encode(os.urandom(16)).decode()
  self.s.sendall(f'GET {u.path} HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
  b=b''
  while not b.endswith(b'\r\n\r\n'):b+=self.s.recv(1)
  assert b.startswith(b'HTTP/1.1 101'),b
 def take(self,n):
  b=b''
  while len(b)<n:
   x=self.s.recv(n-len(b))
   if not x:raise RuntimeError('closed')
   b+=x
  return b
 def recv(self):
  a,b=self.take(2);n=b&127
  if n==126:n=struct.unpack('!H',self.take(2))[0]
  elif n==127:n=struct.unpack('!Q',self.take(8))[0]
  if b&128:mask=self.take(4)
  data=self.take(n)
  if b&128:data=bytes(v^mask[i%4] for i,v in enumerate(data))
  return json.loads(data)
 def call(self,method,params={}):
  self.n+=1;p=json.dumps({'id':self.n,'method':method,'params':params}).encode();mask=os.urandom(4);n=len(p)
  h=bytes([129,128|n]) if n<126 else (bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n))
  self.s.sendall(h+mask+bytes(v^mask[i%4] for i,v in enumerate(p)))
  while True:
   r=self.recv()
   if r.get('id')==self.n:
    if 'error'in r:raise RuntimeError(r)
    return r.get('result',{})
   self.events.append(r)
 def js(self,s):
  r=self.call('Runtime.evaluate',{'expression':s,'returnByValue':True,'awaitPromise':True})
  if 'exceptionDetails'in r:raise RuntimeError(r)
  return r['result'].get('value')
 def shot(self,name):
  r=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
  (ROOT/'evidence'/('depth-20260929-'+name)).write_bytes(base64.b64decode(r['data']))
profile=tempfile.mkdtemp(prefix='l01-browser-')
p=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
report=[]
try:
 f=Path(profile)/'DevToolsActivePort'
 for _ in range(100):
  if f.exists():break
  time.sleep(.05)
 port=int(f.read_text().splitlines()[0]);c=http.client.HTTPConnection('127.0.0.1',port);c.request('GET','/json');targets=json.loads(c.getresponse().read());cdp=CDP(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'))
 cdp.call('Page.enable');cdp.call('Runtime.enable');cdp.call('Network.enable')
 def go(path):
  cdp.call('Page.navigate',{'url':path.as_uri()})
  for _ in range(100):
   if cdp.js('document.readyState')=='complete' and cdp.js('location.pathname')==str(path):break
   time.sleep(.05)
  cdp.js('document.fonts.ready.then(()=>true)')
  cdp.js('document.documentElement.style.scrollBehavior="auto"')
 def inspect():
  return cdp.js('({h1:document.querySelectorAll("h1").length,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth+1,nav:document.querySelectorAll(".sidebar nav a").length})')
 for width,height,mobile in [(1440,1100,False),(390,844,True)]:
  cdp.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':mobile})
  for slug,_,_ in PAGES:
   go(ROOT/(slug+'.html'));r=inspect()
   assert r['h1']==1 and r['images'] and not r['overflow'] and r['nav']==len(PAGES),(slug,width,r)
   report.append(f'PASS {width}x{height}: {slug}; images, navigation, no page overflow')
   if not mobile and slug in ('index','runtime','boot-debug'):
    if slug!='index':cdp.js('document.querySelector("figure").scrollIntoView()')
    cdp.shot('preview-'+slug+'.png')
   if mobile and slug=='index':cdp.shot('preview-mobile.png')
   if not mobile and slug=='interconnect':
    assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-fit]").click();return f.querySelector("img").clientWidth<=f.clientWidth})()')
    assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-full]").click();return f.querySelector("img").clientWidth>=f.querySelector("img").naturalWidth})()')
    assert cdp.js('(()=>{const d=document.querySelector("details");d.querySelector("summary").click();return d.open})()')
    report.append('PASS figure fit/full and quiz expand')
   if not mobile and slug=='registers':
    for term,count in [('GPIO_MASKED_OUT_LOWER',1),('no_such_register_xyz',0),('',429)]:
     value=cdp.js('(()=>{const x=document.querySelector("#reg-search");x.value='+json.dumps(term)+';x.dispatchEvent(new Event("input"));return [...document.querySelectorAll("[data-register]")].filter(r=>!r.hidden).length})()')
     assert value==count,(term,value)
    report.append('PASS register search: one hit, no hit, clear restores 429')
   if not mobile and slug=='future':
    assert '0.38 GiB' in cdp.js('document.querySelector("#calc-result").textContent')
    assert '0.75 GiB' in cdp.js('(()=>{const x=document.querySelector("[name=context]");x.value=8192;x.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelector("#calc-result").textContent})()')
    assert '有限数值' in cdp.js('(()=>{const x=document.querySelector("[name=context]");x.value=0;x.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelector("#calc-result").textContent})()')
    report.append('PASS calculator: context doubles KV; rejects zero')
 cdp.call('Emulation.setScriptExecutionDisabled',{'value':True})
 for slug in ['runtime','boot-debug','registers','vector','memory']:
  go(ROOT/(slug+'.html'));r=inspect();assert r['images'] and not r['overflow'],(slug,r)
  assert cdp.js('document.querySelectorAll("h2").length')>=5
  if slug=='registers':assert cdp.js('document.querySelectorAll("[data-register]").length')==429
  report.append(f'PASS no-script mobile: {slug}; readable text/images/tables')
 cdp.call('Emulation.setScriptExecutionDisabled',{'value':False})
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1000,'deviceScaleFactor':1,'mobile':False})
 for svg in sorted(list((ROOT/'assets').glob('new-*.svg'))+list((ROOT/'assets').glob('depth-*.svg'))):
  go(svg)
  overflow=cdp.js('(()=>{const v=document.documentElement.viewBox.baseVal;return [...document.querySelectorAll("text")].filter(t=>{const b=t.getBBox(),m=document.documentElement.getScreenCTM().inverse().multiply(t.getScreenCTM());return [[b.x,b.y],[b.x+b.width,b.y+b.height]].some(([x,y])=>{const p=new DOMPoint(x,y).matrixTransform(m);return p.x<v.x-1||p.x>v.x+v.width+1||p.y<v.y-1||p.y>v.y+v.height+1})}).map(t=>t.textContent)})()')
  assert not overflow,(svg.name,overflow)
  if svg.stem in ('new-boot','new-lanes','new-vector','depth-vector-arithmetic','depth-handoff','depth-system-full'):cdp.shot('svg-'+svg.stem+'.png')
  report.append('PASS SVG viewBox text bounds: '+svg.name)
 legacy=json.loads((ROOT/'scripts/legacy_links.json').read_text());slugs={s for s,_,_ in PAGES}
 for slug,entry in legacy.items():
  if slug in slugs:continue
  cdp.call('Page.navigate',{'url':(ROOT/(slug+'.html')).as_uri()})
  for _ in range(100):
   if cdp.js('location.href')==(ROOT/entry['target'].split('#')[0]).as_uri()+('#'+entry['target'].split('#')[1] if '#' in entry['target'] else ''):break
   time.sleep(.05)
  assert cdp.js('location.pathname')==str(ROOT/entry['target'].split('#')[0]),slug
  report.append('PASS legacy redirect: '+slug+' -> '+entry['target'])
 errors=[e for e in cdp.events if e.get('method')=='Runtime.exceptionThrown']
 external=[e['params']['request']['url'] for e in cdp.events if e.get('method')=='Network.requestWillBeSent' and e['params']['request']['url'].startswith(('http:','https:'))]
 failed=[e for e in cdp.events if e.get('method')=='Network.loadingFailed' and not e.get('params',{}).get('canceled')]
 assert not errors,errors
 assert not external,external
 assert not failed,failed
 report.append('PASS no JavaScript exception, failed resources or HTTP(S) page requests')
 (ROOT/'evidence/depth-20260929-browser.txt').write_text('2026-09-29; '+subprocess.check_output(['google-chrome','--version'],text=True).strip()+'; file:// offline\n'+'\n'.join(report)+'\n')
 print('\n'.join(report))
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 shutil.rmtree(profile,ignore_errors=True)
