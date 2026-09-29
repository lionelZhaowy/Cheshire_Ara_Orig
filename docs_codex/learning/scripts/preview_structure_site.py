#!/usr/bin/env python3
"""Check the current offline course using local Chrome/CDP; never invokes RTL tools."""
import sys
sys.dont_write_bytecode=True
import subprocess,tempfile,time,json,socket,base64,os,struct,http.client,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
from build_site import PAGES,ENTRIES,MIGRATIONS
from report_run import start_run
args,OUT,META=start_run('browser')
HISTORY={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'evidence').rglob('*') if p.is_file() and not p.is_relative_to(OUT)}
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
  (OUT/name).write_bytes(base64.b64decode(r['data']))
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
 def uri(relative):
  path,sep,anchor=relative.partition('#')
  return (ROOT/path).as_uri()+(sep+anchor if sep else '')
 def go(relative,expected=None):
  cdp.call('Page.navigate',{'url':uri(relative)})
  want=uri(expected or relative)
  for _ in range(100):
   try:
    if cdp.js('location.href')==want and cdp.js('document.readyState')=='complete':break
   except RuntimeError as error:
    if not any(t in str(error) for t in ['Inspected target navigated','Cannot find context','Execution context was destroyed']):raise
   time.sleep(.03)
  assert cdp.js('location.href')==want,(relative,want,cdp.js('location.href'))
  cdp.js('document.fonts.ready.then(()=>true)')
  cdp.js('document.documentElement.style.scrollBehavior="auto"')
 def inspect():
  return cdp.js('({h1:document.querySelectorAll("h1").length,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth+1,nav:document.querySelectorAll(".chapter-link").length,active:document.querySelectorAll(".chapter-link[aria-current=page]").length,parts:[...document.querySelectorAll(".nav-part[data-part][open]")].map(e=>e.dataset.part)})')
 for width,height,mobile in [(1440,1100,False),(390,844,True)]:
  cdp.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':mobile})
  for entry in ENTRIES:
   slug=entry['slug'];go(slug+'.html');r=inspect()
   assert r['h1']==1 and r['images'] and not r['overflow'] and r['nav']==len(PAGES) and r['active']==1,(slug,width,r)
   assert r['parts']==([entry['part']] if entry.get('part') else []),(slug,r)
   assert cdp.js('document.querySelector(".site-menu").open')== (not mobile),(slug,'menu')
   assert cdp.js('(()=>{const d=document.querySelector(".toc-panel");const before=d.open;d.querySelector("summary").click();const changed=d.open!==before;d.querySelector("summary").click();return changed&&d.open===before})()')
   if mobile and slug=='ara':
    assert cdp.js('(()=>{const d=document.querySelector(".site-menu");d.querySelector("summary").click();return d.open&&document.querySelector(".chapter-link[aria-current=page]").getClientRects().length>0})()')
    cdp.shot('preview-mobile-menu.png')
    cdp.js('document.querySelector(".site-menu summary").click()')
   if slug=='ara':
    assert cdp.js('(()=>{const a=document.querySelector(".toc ol ol a");a.click();return location.hash===a.hash})()')
    assert cdp.js('(()=>{const e=document.getElementById(decodeURIComponent(location.hash.slice(1)));const y=e.getBoundingClientRect().top;return y>=0&&y<innerHeight})()')
    if not mobile:cdp.shot('preview-ara-section.png')
   if not mobile and slug in ('index','ddr','vector','interconnect','clocks','power','boot','cva6'):cdp.shot('preview-'+slug+'.png')
   if mobile and slug in ('index','vector'):cdp.shot('preview-mobile-'+slug+'.png')
   if not mobile and slug=='interconnect':
    assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-fit]").click();return f.querySelector("img").clientWidth<=f.clientWidth})()')
    assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-full]").click();return f.querySelector("img").clientWidth>=f.querySelector("img").naturalWidth})()')
    assert cdp.js('(()=>{const d=document.querySelector("details.quiz");d.querySelector("summary").click();return d.open})()')
    report.append('PASS figure fit/full and quiz expand')
   if not mobile and slug=='registers':
    for term,count in [('GPIO_MASKED_OUT_LOWER',1),('no_such_register_xyz',0),('',429)]:
     value=cdp.js('(()=>{const x=document.querySelector("#reg-search");x.value='+json.dumps(term)+';x.dispatchEvent(new Event("input"));return [...document.querySelectorAll("[data-register]")].filter(r=>!r.hidden).length})()')
     assert value==count,(term,value)
    report.append('PASS register search: one hit, no hit, clear restores 429')
   if not mobile and slug=='models':
    assert '0.38 GiB' in cdp.js('document.querySelector("#calc-result").textContent')
    assert '0.75 GiB' in cdp.js('(()=>{const x=document.querySelector("[name=context]");x.value=8192;x.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelector("#calc-result").textContent})()')
    assert '有限数值' in cdp.js('(()=>{const x=document.querySelector("[name=context]");x.value=0;x.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelector("#calc-result").textContent})()')
    report.append('PASS moved calculator: context doubles KV; rejects zero')
   report.append(f'PASS {width}x{height}: {slug}; images, current part/chapter, collapsible menu/TOC, no page overflow')
 cdp.call('Emulation.setScriptExecutionDisabled',{'value':True})
 for slug in ['index','ara','vector','ddr','sharing','boot-debug','registers']:
  go(slug+'.html');r=inspect();assert r['images'] and not r['overflow'],(slug,r)
  assert cdp.js('document.querySelector(".site-menu").open')
  assert cdp.js('document.querySelector(".toc").querySelectorAll("a").length')>0
  assert cdp.js('(()=>{const d=document.querySelector(".toc-panel");const before=d.open;d.querySelector("summary").click();const ok=d.open!==before;d.querySelector("summary").click();return ok&&d.open===before})()')
  report.append(f'PASS no-script mobile: {slug}; native navigation/TOC and content')
 for old,dest in [('vector.html#interface','ara.html#interface'),('memory.html#dma','dma.html#dma'),('axi-adapters.html#width','adapters.html#width')]:
  go(old)
  assert cdp.js('(()=>{const e=document.getElementById(location.hash.slice(1));return !!e&&e.querySelector("a").getAttribute("href")==='+json.dumps(dest)+'})()'),old
  report.append('PASS no-script old bookmark fallback: '+old+' -> '+dest)
 cdp.call('Emulation.setScriptExecutionDisabled',{'value':False})
 moved={old:dest for old,dest in MIGRATIONS.items() if old.split('#')[0]!=dest.split('#')[0]}
 for old,dest in moved.items():
  go(old,dest)
  if '#' in dest:assert cdp.js('!!document.getElementById(decodeURIComponent(location.hash.slice(1)))'),(old,dest)
  report.append('PASS precise bookmark redirect: '+old+' -> '+dest)
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1000,'deviceScaleFactor':1,'mobile':False})
 for name in ['new-boot.svg','depth-boot-phases.svg']+[p.name for p in sorted((ROOT/'assets').glob('mechanism-*.svg'))]:
  go('assets/'+name)
  overflow=cdp.js('(()=>{const v=document.documentElement.viewBox.baseVal;return [...document.querySelectorAll("text")].filter(t=>{const b=t.getBBox(),m=document.documentElement.getScreenCTM().inverse().multiply(t.getScreenCTM());return [[b.x,b.y],[b.x+b.width,b.y+b.height]].some(([x,y])=>{const p=new DOMPoint(x,y).matrixTransform(m);return p.x<v.x-1||p.x>v.x+v.width+1||p.y<v.y-1||p.y>v.y+v.height+1})}).map(t=>t.textContent)})()')
  assert not overflow,(name,overflow)
  cdp.shot('svg-'+name+'.png');report.append('PASS edited SVG viewBox text bounds: '+name)
 errors=[e for e in cdp.events if e.get('method')=='Runtime.exceptionThrown']
 external=[e['params']['request']['url'] for e in cdp.events if e.get('method')=='Network.requestWillBeSent' and e['params']['request']['url'].startswith(('http:','https:'))]
 failed=[e for e in cdp.events if e.get('method')=='Network.loadingFailed' and not e.get('params',{}).get('canceled')]
 assert not errors,errors
 assert not external,external
 assert not failed,failed
 report.append('PASS no JavaScript exception, failed resources or HTTP(S) page requests')
 assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in HISTORY.items()),'history modified'
 assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in META['inputs'].items()),'input modified'
 assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.html')}==META['tested_html'],'tested HTML modified'
 report.append('PASS tested HTML hashes unchanged: '+str(len(META['tested_html'])))
 report.append('PASS existing evidence and content/script/asset hashes unchanged during browser check')
 (OUT/'browser.txt').write_text(META['started_at']+'; '+subprocess.check_output(['google-chrome','--version'],text=True).strip()+'; file:// offline\n'+'\n'.join(report)+'\n')
 print(f'PASS {len(PAGES)} pages at desktop/mobile, 7 no-script pages, {len(moved)} cross-page bookmark redirects, interactions and edited SVGs')
except BaseException as error:
 (OUT/'browser.txt').write_text(META['started_at']+'\n'+'\n'.join(report)+'\nFAIL: '+str(error)+'\n')
 raise
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 shutil.rmtree(profile,ignore_errors=True)
