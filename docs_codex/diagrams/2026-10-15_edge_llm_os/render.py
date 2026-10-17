#!/usr/bin/env python3
"""Render SVGs and check layout in a fresh directory.

Adapted from the repository L01 coherence renderer (2026-10-15).
Uses the tracked learning/scripts/preview_structure_site.py CDP transport only.
Does not run or modify that script or any prior figure.
"""
import argparse
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

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
ap=argparse.ArgumentParser()
ap.add_argument('--source-dir',type=Path,required=True)
ap.add_argument('--out-dir',type=Path,required=True)
args=ap.parse_args()
OUT=args.out_dir.resolve()
OUT.mkdir(parents=True,exist_ok=False)
# Reuse only the repository's dependency-free CDP transport, not its test runner.
source=(ROOT/'docs_codex/learning/scripts/preview_structure_site.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='CDP')
exec(compile(ast.Module(body=[node],type_ignores=[]),'local_cdp_transport','exec'))
layouts=json.loads((args.source_dir/'layout.json').read_text())
profile=tempfile.mkdtemp(prefix='l01-edge-llm-os-chrome-')
log=(OUT/'chrome.log').open('w')
p=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu',
 '--disable-dev-shm-usage','--disable-background-networking','--no-first-run',
 '--no-default-browser-check','--remote-debugging-port=0',f'--user-data-dir={profile}',
 'about:blank'],stdout=subprocess.DEVNULL,stderr=log)
report={'date':'2026-10-15','chrome':subprocess.check_output(['google-chrome','--version'],text=True).strip(),
        'office_application_tested':False,'figures':[],'status':'incomplete'}
try:
    port_file=Path(profile)/'DevToolsActivePort'
    for _ in range(120):
        if port_file.exists():break
        if p.poll() is not None:raise RuntimeError('Chrome exited; see chrome.log')
        time.sleep(.05)
    conn=http.client.HTTPConnection('127.0.0.1',int(port_file.read_text().splitlines()[0]))
    conn.request('GET','/json')
    targets=json.loads(conn.getresponse().read())
    cdp=CDP(next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'))
    cdp.call('Page.enable');cdp.call('Runtime.enable')
    for layout in layouts:
        svg=(args.source_dir/(layout['name']+'.svg')).resolve()
        w,h=layout['canvas']
        cdp.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
        uri=svg.as_uri()
        cdp.call('Page.navigate',{'url':uri})
        for _ in range(120):
            try:
                if cdp.js('location.href')==uri and cdp.js('document.readyState')=='complete':break
            except RuntimeError:pass
            time.sleep(.03)
        assert cdp.js('location.href')==uri
        cdp.js('document.fonts.ready.then(()=>true)')
        bounds=cdp.js('Array.from(document.querySelectorAll("text"),t=>({text:t.textContent,owner:t.dataset.owner||"",...Object.fromEntries(["x","y","width","height"].map(k=>[k,t.getBBox()[k]]))}))')
        outside=[];overflows=[];hits=[];overlaps=[]
        for t in bounds:
            if t['x']<0 or t['y']<0 or t['x']+t['width']>w or t['y']+t['height']>h:
                outside.append(t['text'])
            if t['owner']:
                b=layout['boxes'][t['owner']]
                if t['x']<b['x']+6 or t['x']+t['width']>b['x']+b['width']-6 or t['y']<b['y'] or t['y']+t['height']>b['y']+b['height']-3:
                    overflows.append(t['text'])
        for i,t in enumerate(bounds):
            for u in bounds[i+1:]:
                if max(t['x'],u['x'])<min(t['x']+t['width'],u['x']+u['width'])-2 and max(t['y'],u['y'])<min(t['y']+t['height'],u['y']+u['height'])-2:
                    overlaps.append([t['text'],u['text']])
        for edge in layout['arrows']:
            for (x1,y1),(x2,y2) in zip(edge['points'],edge['points'][1:]):
                assert x1==x2 or y1==y2
                for t in bounds:
                    l,top,r,b=t['x']+2,t['y']+2,t['x']+t['width']-2,t['y']+t['height']-2
                    if (x1==x2 and l<x1<r and max(min(y1,y2),top)<min(max(y1,y2),b)) or (y1==y2 and top<y1<b and max(min(x1,x2),l)<min(max(x1,x2),r)):
                        hits.append([edge['id'],t['text']])
        cdp.shot(layout['name']+'.png')
        entry=dict(name=layout['name'],svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
                   text_count=len(bounds),outside_canvas=outside,box_text_overflow=overflows,
                   text_line_intersections=hits,text_overlaps=overlaps,text_bounds=bounds)
        report['figures'].append(entry)
    failed=any(f[k] for f in report['figures'] for k in ['outside_canvas','box_text_overflow','text_line_intersections','text_overlaps'])
    report['status']='needs-layout-adjustment' if failed else 'pass'
finally:
    p.terminate();p.wait(timeout=10);log.close()
    (OUT/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'figures':[{k:v for k,v in f.items() if k!='text_bounds'} for f in report['figures']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if report['status']=='pass' else 1)
