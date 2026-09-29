#!/usr/bin/env python3
"""Optional local Chrome/CDP preview; Python stdlib only. No RTL commands."""
import subprocess,tempfile,time,json,socket,base64,os,struct,http.client,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--editorial',action='store_true');parser.add_argument('--advanced',action='store_true');parser.add_argument('--hardware',action='store_true');options=parser.parse_args()
shot_prefix='editorial-'if options.editorial else 'hardware-'if options.hardware else 'advanced-'if options.advanced else ''
page_count=len(list(ROOT.glob('*.html')))
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
  if options.editorial and name not in ('preview-index.png','preview-configuration.png','preview-mobile.png'):return
  r=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
  (ROOT/'evidence'/(shot_prefix+name)).write_bytes(base64.b64decode(r['data']))
profile=tempfile.mkdtemp(prefix='l01-browser-')
p=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
report=[]
try:
 f=Path(profile)/'DevToolsActivePort'
 for _ in range(100):
  if f.exists():break
  time.sleep(.05)
 port=int(f.read_text().splitlines()[0]);c=http.client.HTTPConnection('127.0.0.1',port);c.request('GET','/json');targets=json.loads(c.getresponse().read());cdp=CDP(next(t['webSocketDebuggerUrl']for t in targets if t['type']=='page'))
 cdp.call('Page.enable');cdp.call('Runtime.enable');cdp.call('Network.enable')
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1100,'deviceScaleFactor':1,'mobile':False})
 for page in sorted(ROOT.glob('*.html')):
  cdp.call('Page.navigate',{'url':page.as_uri()})
  for _ in range(100):
   if cdp.js('document.readyState')=='complete':break
   time.sleep(.05)
  cdp.js('document.fonts.ready.then(()=>true)')
  cdp.js('document.documentElement.style.scrollBehavior="auto"');r=cdp.js('({title:document.title,h1:document.querySelectorAll("h1").length,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth+1,nav:document.querySelectorAll(".sidebar nav a").length})')
  assert r['h1']==1 and r['images']and not r['overflow']and r['nav']==page_count,(page,r)
  report.append('PASS desktop 1440x1100 '+page.name+' / images, navigation, no horizontal page overflow')
  if page.stem in (['index','configuration','lifecycle','hardware-devices'] if options.editorial else ['hardware','soc-topology','axi-crossbar','axi-adapters','ip-integration'] if options.hardware else ['system','execution','uart-gpio','dma-llc','stream-io'] if options.advanced else ['architecture','foundations','lifecycle','memory']):
   query='(document.querySelector("figure")||document.querySelector("h2")).scrollIntoView()'
   if page.stem=='lifecycle':query='document.querySelector("#boot").scrollIntoView()'
   if options.editorial:query='window.scrollTo(0,0)'
   cdp.js(query);time.sleep(.1);cdp.shot('preview-'+page.stem+'.png')
  if options.advanced and page.stem=='system':
   assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-fit]").click();return f.querySelector("img").clientWidth<=f.clientWidth})()')
   assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-full]").click();return f.querySelector("img").clientWidth>=f.querySelector("img").naturalWidth})()')
   report.append('PASS system figure fit-to-width and full-size reading controls')
   cdp.js('document.querySelector("#clocks").scrollIntoView()');time.sleep(.1);cdp.shot('preview-clocks.png')
  if options.advanced and page.stem=='registers':
   result=cdp.js('(()=>{const x=document.querySelector("#reg-search");x.value="GPIO_MASKED_OUT_LOWER";x.dispatchEvent(new Event("input"));return {visible:[...document.querySelectorAll("[data-register]")].filter(r=>!r.hidden).length,text:document.querySelector("#reg-count").textContent}})()')
   assert result['visible']==1,result
   report.append('PASS register search matches exactly one masked GPIO register; offline')
   cdp.js('document.querySelector("#reg-search").scrollIntoView()');time.sleep(.1);cdp.shot('preview-register-search.png')
   assert cdp.js('(()=>{const x=document.querySelector("#reg-search");x.value="no_such_register_xyz";x.dispatchEvent(new Event("input"));return [...document.querySelectorAll("[data-register]")].every(r=>r.hidden)})()')
   assert cdp.js('(()=>{const x=document.querySelector("#reg-search");x.value="";x.dispatchEvent(new Event("input"));return [...document.querySelectorAll("[data-register]")].every(r=>!r.hidden)})()')
   report.append('PASS register search no-match and clear restores complete table')
  if options.advanced and page.stem=='capstone':
   assert cdp.js('(()=>{const b=document.querySelector("[data-stepper]");const old=b.querySelector(".step-text").textContent;b.querySelector("button").click();return old!==b.querySelector(".step-text").textContent&&b.querySelectorAll(".active").length===1})()')
   cdp.js('document.querySelector("[data-stepper]").scrollIntoView()');time.sleep(.1);cdp.shot('preview-capstone.png')
   report.append('PASS capstone explanatory step control (not simulation)')
  if page.stem=='lifecycle':
   r=cdp.js('(()=>{const b=document.querySelector("[data-stepper]");const old=b.querySelector(".step-text").textContent;b.querySelector("button").click();return old!==b.querySelector(".step-text").textContent&&b.querySelectorAll(".active").length===1})()');assert r
   report.append('PASS lifecycle step button changes explanation and active step')
   assert cdp.js('(()=>{const d=document.querySelector(".quiz details");d.querySelector("summary").click();return d.open})()')
   report.append('PASS details question expands via summary click')
  if page.stem=='future':
   before=cdp.js('document.querySelector("#calc-result").textContent');assert '0.38 GiB'in before,before
   after=cdp.js('(()=>{let x=document.querySelector("[name=context]");x.value=8192;x.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelector("#calc-result").textContent})()');assert '0.75 GiB'in after,after
   report.append('PASS calculator context 4096->8192 doubles KV 0.38->0.75 GiB')
   cdp.js('document.querySelector("#calculator").scrollIntoView()');time.sleep(.1);cdp.shot('preview-calculator.png')
 # Mobile all pages, table/figure internal scrolling is intentional.
 cdp.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
 for page in sorted(ROOT.glob('*.html')):
  cdp.call('Page.navigate',{'url':page.as_uri()});time.sleep(.12)
  r=cdp.js('({ready:document.readyState,overflow:document.documentElement.scrollWidth>innerWidth+1,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0)})')
  assert r['ready']=='complete'and not r['overflow']and r['images'],(page,r)
  report.append('PASS mobile 390x844 '+page.name+' / images, no horizontal page overflow')
  if page.stem==('index'if options.editorial else 'hardware'if options.hardware else 'advanced'if options.advanced else 'labs'):cdp.shot('preview-mobile.png')
 # Inspect same page without script.
 cdp.call('Emulation.setScriptExecutionDisabled',{'value':True});cdp.call('Page.navigate',{'url':(ROOT/'lifecycle.html').as_uri()});time.sleep(.15)
 # Runtime.evaluate can inspect even when page scripts disabled.
 assert cdp.js('document.querySelectorAll("h2").length>=6')
 report.append('PASS script-disabled lifecycle still has core headings/content (enhancements unavailable by design)')
 if options.advanced:
  cdp.call('Page.navigate',{'url':(ROOT/'registers.html').as_uri()});time.sleep(.15)
  assert cdp.js('document.querySelectorAll("[data-register]").length==429')
  report.append('PASS script-disabled register reference retains all 429 entries')
  cdp.call('Emulation.setScriptExecutionDisabled',{'value':False})
  cdp.call('Emulation.setDeviceMetricsOverride',{'width':1600,'height':1400,'deviceScaleFactor':1,'mobile':False})
  for name in ['system-detail','clock-reset-detail','software-hardware','core-ara-detail','peripheral-internals','interrupt-detail','ownership-detail','stream-io-detail']:
   cdp.call('Page.navigate',{'url':(ROOT/'assets'/(name+'.svg')).as_uri()});time.sleep(.1)
   overflow=cdp.js('(()=>{const v=document.documentElement.viewBox.baseVal;return [...document.querySelectorAll("text")].filter(t=>{const b=t.getBBox();return b.x<0||b.x+b.width>v.width||b.y<0||b.y+b.height>v.height}).map(t=>t.textContent)})()')
   assert not overflow,(name,overflow)
   if name in ('system-detail','clock-reset-detail'):cdp.shot('svg-'+name+'.png')
  report.append('PASS 8 advanced SVGs: no text outside their viewBox; topology is illustrative')
 if options.hardware:
  cdp.call('Page.navigate',{'url':(ROOT/'axi-crossbar.html').as_uri()});time.sleep(.15)
  assert cdp.js('document.querySelectorAll("h2").length>=8 && document.querySelectorAll("details").length>=3')
  report.append('PASS script-disabled crossbar retains explanations and quizzes')
  cdp.call('Emulation.setScriptExecutionDisabled',{'value':False})
  cdp.call('Page.navigate',{'url':(ROOT/'axi-crossbar.html').as_uri()});time.sleep(.15)
  assert cdp.js('(()=>{const d=document.querySelector("details");d.querySelector("summary").click();return d.open})()')
  assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-fit]").click();return f.querySelector("img").clientWidth<=f.clientWidth})()')
  assert cdp.js('(()=>{const f=document.querySelector("figure");f.querySelector("[data-figure-full]").click();return f.querySelector("img").clientWidth>=f.querySelector("img").naturalWidth})()')
  assert cdp.js('(()=>{const b=document.querySelector("[data-stepper]");const old=b.querySelector(".step-text").textContent;b.querySelector("button").click();return old!==b.querySelector(".step-text").textContent&&b.querySelectorAll(".active").length===1})()')
  report.append('PASS hardware write-transaction stepper (teaching animation, not waveform)')
  report.append('PASS hardware quiz and figure fit/full controls')
  cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':1000,'deviceScaleFactor':1,'mobile':False})
  for svg in sorted((ROOT/'assets').glob('hw-*.svg')):
   cdp.call('Page.navigate',{'url':svg.as_uri()});time.sleep(.1)
   overflow=cdp.js('(()=>{const v=document.documentElement.viewBox.baseVal;return [...document.querySelectorAll("text")].filter(t=>{const b=t.getBBox();return b.x<0||b.x+b.width>v.width||b.y<0||b.y+b.height>v.height}).map(t=>t.textContent)})()')
   assert not overflow,(svg.name,overflow)
   if svg.stem in ('hw-xbar','hw-write','hw-adapters'):cdp.shot('svg-'+svg.stem+'.png')
  report.append('PASS 10 hardware SVGs: text within viewBox (not topology validation)')
 errors=[e for e in cdp.events if e.get('method')=='Runtime.exceptionThrown']
 external=[e['params']['request']['url']for e in cdp.events if e.get('method')=='Network.requestWillBeSent'and e['params']['request']['url'].startswith(('http:','https:'))]
 assert not errors,errors
 assert not external,external
 report.append('PASS no JavaScript exceptions and no HTTP(S) page resource requests')
 (ROOT/'evidence'/('editorial-browser.txt'if options.editorial else 'hardware-browser.txt'if options.hardware else 'advanced-browser.txt'if options.advanced else 'browser.txt')).write_text(subprocess.check_output(['google-chrome','--version'],text=True).strip()+'; file:// offline preview; '+time.strftime('%Y-%m-%d')+'\n'+'\n'.join(report)+'\n')
 print('\n'.join(report))
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill()
