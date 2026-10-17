#!/usr/bin/env python3
"""Render the standalone DDR–GB explanation with installed Chrome."""
import ast
import base64
import hashlib
import http.client
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import time

import markdown

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
OUT=D/'previews'
source=(ROOT/'docs_codex/learning/scripts/preview_structure_site.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='CDP')
exec(compile(ast.Module(body=[node],type_ignores=[]),'local_cdp_transport','exec'))
profile=tempfile.mkdtemp(prefix='ddr-gb-design-chrome-')
log=(D/'evidence/document-chrome.log').open('w')
proc=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu',
    '--disable-dev-shm-usage','--disable-background-networking','--no-first-run',
    '--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}',
    'about:blank'],stdout=subprocess.DEVNULL,stderr=log)
report={'status':'incomplete','documents':[],
        'chrome':subprocess.check_output(['google-chrome','--version'],text=True).strip()}
try:
    port_file=Path(profile)/'DevToolsActivePort'
    for _ in range(120):
        if port_file.exists():break
        if proc.poll() is not None:raise RuntimeError('Chrome exited; see log')
        time.sleep(.05)
    conn=http.client.HTTPConnection('127.0.0.1',int(port_file.read_text().splitlines()[0]))
    conn.request('GET','/json')
    cdp=CDP(next(t['webSocketDebuggerUrl'] for t in json.loads(conn.getresponse().read()) if t['type']=='page'))
    cdp.call('Page.enable');cdp.call('Runtime.enable')
    cdp.call('Emulation.setDeviceMetricsOverride',{'width':1500,'height':1100,'deviceScaleFactor':1,'mobile':False})
    for stem,name in [('design','DDR_GB_Coherence_Design.md')]:
        doc=ROOT/'docs_codex/engineering'/name
        body=markdown.markdown(doc.read_text(),extensions=['tables','fenced_code','toc'])
        page=D/(stem+'-preview.html')
        page.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<base href="../../engineering/">'
            '<title>DDR–GB 数据同步设计</title>'
            '<style>body{max-width:1250px;margin:40px auto;padding:0 24px;'
            'font:17px/1.85 "WenQuanYi Zen Hei",sans-serif;color:#243042}'
            'h1,h2,h3{line-height:1.4;color:#143d5c}h2{margin-top:2em;'
            'border-bottom:1px solid #cdd8e0;padding-bottom:.35em}'
            'a{color:#176296}img{display:block;max-width:100%;height:auto;margin:24px auto}'
            'table{border-collapse:collapse;width:100%;font-size:15px}'
            'th,td{border:1px solid #cdd8e0;text-align:left;padding:8px 11px}'
            'th{background:#edf3f7}code{background:#f0f3f6;padding:2px 4px}'
            'pre{padding:14px;background:#f0f3f6;overflow:auto;font-size:14px;line-height:1.6}'
            '</style>'+body+'</html>')
        cdp.call('Page.navigate',{'url':page.as_uri()})
        for _ in range(120):
            try:
                if cdp.js('location.href')==page.as_uri() and cdp.js('document.readyState')=='complete':break
            except RuntimeError:pass
            time.sleep(.03)
        assert cdp.js('location.href')==page.as_uri()
        cdp.js('document.fonts.ready.then(()=>true)')
        result=cdp.js('({images:Array.from(document.images,i=>({src:i.getAttribute("src"),'
            'loaded:i.complete&&i.naturalWidth>0})),overflow:document.documentElement.scrollWidth>innerWidth,'
            'headings:Array.from(document.querySelectorAll("h2"),e=>e.textContent)})')
        result.update(source=str(doc.relative_to(ROOT)),sha256=hashlib.sha256(doc.read_bytes()).hexdigest())
        assert all(i['loaded'] for i in result['images']) and not result['overflow']
        cdp.shot(stem+'-top.png')
        for i in range(len(result['images'])):
            cdp.js(f'document.images[{i}].scrollIntoView({{block:"center"}})')
            cdp.shot(f'{stem}-figure-{i+1}.png')
        report['documents'].append(result)
    report['status']='pass'
finally:
    proc.terminate();proc.wait(timeout=10);log.close()
    (D/'evidence/document-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
