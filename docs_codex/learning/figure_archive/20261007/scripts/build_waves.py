#!/usr/bin/env python3
"""Render editable WaveDrom JSON into standalone offline SVG using pinned local JS."""
from browser_cdp import CDP
import subprocess,tempfile,time,json,http.client,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent
profile=tempfile.mkdtemp(prefix='l01-wavedrom-')
p=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 f=Path(profile)/'DevToolsActivePort'
 for _ in range(100):
  if f.exists():break
  time.sleep(.05)
 c=http.client.HTTPConnection('127.0.0.1',int(f.read_text().splitlines()[0]));c.request('GET','/json')
 cdp=CDP(next(t['webSocketDebuggerUrl'] for t in json.loads(c.getresponse().read()) if t['type']=='page'))
 cdp.call('Runtime.enable')
 # Evaluate local vendored assets. No HTTP, server, npm, or network is required.
 cdp.js((R/'assets/vendor/wavedrom-3.5.0/default.js').read_text())
 cdp.js((R/'assets/vendor/wavedrom-3.5.0/wavedrom.min.js').read_text())
 for source in sorted((R/'assets/waves').glob('*.json')):
  obj=json.loads(source.read_text())
  cdp.js('document.body.innerHTML=\'<div id="WaveDrom_Display_0"></div>\'')
  cdp.js('WaveDrom.RenderWaveForm(0,'+json.dumps(obj)+',"WaveDrom_Display_")')
  svg=cdp.js('document.querySelector("svg").outerHTML')
  assert svg and 'xmlns='in svg,source
  (R/'assets'/('depth-'+source.stem+'.svg')).write_text(svg+'\n')
  print('WaveDrom 3.5.0:',source.name)
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 shutil.rmtree(profile,ignore_errors=True)
