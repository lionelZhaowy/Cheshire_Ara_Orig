#!/usr/bin/env python3
"""Render unchanged source figures and preview the survey with installed Chrome."""
import ast
import base64
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

import markdown

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
OUT = D / 'previews'
OUT.mkdir(exist_ok=True)
source = (ROOT / 'docs_codex/learning/scripts/preview_structure_site.py').read_text()
node = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == 'CDP')
exec(compile(ast.Module(body=[node], type_ignores=[]), 'local_cdp_transport', 'exec'))
profile = tempfile.mkdtemp(prefix='coherence-survey-chrome-')
log = (D / 'evidence/chrome.log').open('w')
proc = subprocess.Popen(['google-chrome', '--headless', '--no-sandbox', '--disable-gpu',
    '--disable-dev-shm-usage', '--disable-background-networking', '--no-first-run',
    '--no-default-browser-check', '--remote-debugging-port=0', f'--user-data-dir={profile}',
    'about:blank'], stdout=subprocess.DEVNULL, stderr=log)
report = {'chrome': subprocess.check_output(['google-chrome', '--version'], text=True).strip(),
          'figures': [], 'status': 'incomplete'}
try:
    port_file = Path(profile) / 'DevToolsActivePort'
    for _ in range(120):
        if port_file.exists():
            break
        if proc.poll() is not None:
            raise RuntimeError('Chrome exited; see evidence/chrome.log')
        time.sleep(.05)
    conn = http.client.HTTPConnection('127.0.0.1', int(port_file.read_text().splitlines()[0]))
    conn.request('GET', '/json')
    cdp = CDP(next(t['webSocketDebuggerUrl'] for t in json.loads(conn.getresponse().read()) if t['type'] == 'page'))
    cdp.call('Page.enable')
    cdp.call('Runtime.enable')

    def navigate(path, width, height):
        cdp.call('Emulation.setDeviceMetricsOverride',
                 {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': False})
        cdp.call('Page.navigate', {'url': path.as_uri()})
        for _ in range(120):
            if cdp.js('location.href') == path.as_uri() and cdp.js('document.readyState') == 'complete':
                break
            time.sleep(.03)
        cdp.js('document.fonts.ready.then(()=>true)')

    for item in json.loads((D / 'sources.json').read_text())['figures']:
        src = D / item['file']
        if src.suffix == '.svg':
            _, _, w, h = map(float, ET.parse(src).getroot().attrib['viewBox'].split())
            width, height = 1800, math.ceil(1800 * h / w)
        else:
            # PNG IHDR dimensions; preserve the original raster resolution.
            width, height = struct.unpack('>II', src.read_bytes()[16:24])
        wrapper = Path(profile) / (src.stem + '.html')
        wrapper.write_text('<!doctype html><meta charset="utf-8"><style>'
            'html,body{margin:0;background:white}img{display:block;width:100%;height:auto}</style>'
            f'<img src="{src.as_uri()}">')
        navigate(wrapper, width, height)
        assert cdp.js('document.images[0].complete && document.images[0].naturalWidth>0')
        cdp.shot(src.stem + '.png')
        report['figures'].append({'source': item['file'], 'width': width, 'height': height,
            'sha256': hashlib.sha256(src.read_bytes()).hexdigest(), 'loaded': True})

    doc = ROOT / 'docs_codex/engineering/CPU_NPU_Cache_Coherence_Survey.md'
    report['document_sha256'] = hashlib.sha256(doc.read_bytes()).hexdigest()
    body = markdown.markdown(doc.read_text(), extensions=['tables', 'fenced_code'])
    page = D / 'preview.html'
    # Resolve relative Markdown links from the document directory, including local PNGs.
    page.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>CPU–NPU 缓存一致性方案综述</title>'
        '<base href="../../engineering/">'
        '<style>body{max-width:1050px;margin:40px auto;padding:0 24px;color:#243042;'
        'font:17px/1.85 "WenQuanYi Zen Hei",sans-serif}h1,h2,h3{line-height:1.4;'
        'color:#143d5c}h2{margin-top:2em;border-bottom:1px solid #cdd8e0;padding-bottom:.35em}'
        'a{color:#176296}img{display:block;max-width:100%;height:auto;margin:24px auto;'
        'background:white}table{border-collapse:collapse;width:100%;font-size:15px}'
        'th,td{border:1px solid #cdd8e0;text-align:left;padding:8px 11px}'
        'th{background:#edf3f7}code{background:#f0f3f6;padding:2px 4px}'
        '</style>' + body + '</html>')
    navigate(page, 1360, 1000)
    report['document'] = cdp.js('({images:Array.from(document.images,i=>({src:i.getAttribute("src"),'
        'loaded:i.complete&&i.naturalWidth>0})),overflow:document.documentElement.scrollWidth>innerWidth,'
        'headings:Array.from(document.querySelectorAll("h2"),e=>e.textContent)})')
    cdp.shot('document-top.png')
    for i in range(4):
        cdp.js(f'document.images[{i}].scrollIntoView({{block:"center"}})')
        cdp.shot(f'document-figure-{i+1}.png')
    assert all(i['loaded'] for i in report['document']['images'])
    assert not report['document']['overflow']
    report['status'] = 'pass'
finally:
    proc.terminate()
    proc.wait(timeout=10)
    log.close()
    (D / 'evidence/browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
