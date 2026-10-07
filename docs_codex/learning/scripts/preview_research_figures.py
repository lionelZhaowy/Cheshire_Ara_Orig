#!/usr/bin/env python3
"""Render all figure masters with local Chrome; record bounds and text collisions.

No production tools. Output must be a new directory. Contact sheets are a
separate visual review aid; this check does not claim PowerPoint rendering.
"""
import sys
sys.dont_write_bytecode = True
import argparse, base64, hashlib, http.client, json, shutil, subprocess, tempfile, time
from pathlib import Path
from browser_cdp import CDP

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir', required=True, type=Path)
    ap.add_argument('--out-dir', required=True, type=Path)
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=False)
    sources=sorted(args.input_dir.glob('*.svg')); assert len(sources)==37
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    profile=tempfile.mkdtemp(prefix='l01-figure-browser-')
    proc=subprocess.Popen(['google-chrome','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage',
        '--disable-background-networking','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    report={'renderer':'Chrome SVG, not PowerPoint','hashes':hashes,'figures':{}}
    try:
        portfile=Path(profile)/'DevToolsActivePort'
        for _ in range(150):
            if portfile.exists(): break
            time.sleep(.05)
        c=http.client.HTTPConnection('127.0.0.1',int(portfile.read_text().splitlines()[0]));c.request('GET','/json')
        cdp=CDP(next(t['webSocketDebuggerUrl'] for t in json.loads(c.getresponse().read()) if t['type']=='page'))
        cdp.call('Page.enable');cdp.call('Runtime.enable')
        cdp.call('Emulation.setDeviceMetricsOverride',{'width':1800,'height':1125,'deviceScaleFactor':1,'mobile':False})
        for p in sources:
            cdp.call('Page.navigate',{'url':p.resolve().as_uri()})
            for _ in range(100):
                try:
                    if cdp.js('document.readyState==="complete" && location.href==='+json.dumps(p.resolve().as_uri())):break
                except RuntimeError: pass
                time.sleep(.03)
            cdp.js('document.fonts.ready.then(()=>true)')
            result=cdp.js('''(()=>{
              const all=[...document.querySelectorAll('text')].map(e=>({e,b:e.getBBox(),t:e.textContent}));
              const outside=[], cards=[], overlaps=[];
              for(const {e,b,t} of all){
                if(b.x<0||b.y<0||b.x+b.width>1800.5||b.y+b.height>1125.5) outside.push(t);
                const id=e.getAttribute('data-box');
                if(id){const box=document.getElementById(id).getBBox();
                  if(b.x<box.x||b.y<box.y||b.x+b.width>box.x+box.width+1||b.y+b.height>box.y+box.height+1) cards.push({id,t});
                }
              }
              for(let i=0;i<all.length;i++)for(let j=i+1;j<all.length;j++){
                const a=all[i].b,b=all[j].b;
                if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>2 && Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>2)
                  overlaps.push([all[i].t,all[j].t]);
              }
              return {texts:all.length,outside,cards,overlaps};
            })()''')
            report['figures'][p.name]=result
            shot=cdp.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
            (args.out_dir/(p.stem+'.png')).write_bytes(base64.b64decode(shot['data']))
        report['inputs_unchanged']=all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.name] for p in sources)
        report['pass']=report['inputs_unchanged'] and all(not(v['outside'] or v['cards'] or v['overlaps']) for v in report['figures'].values())
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        shutil.rmtree(profile,ignore_errors=True)
        (args.out_dir/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    issues={k:v for k,v in report['figures'].items() if v['outside'] or v['cards'] or v['overlaps']}
    print(json.dumps({'count':len(report['figures']),'pass':report['pass'],'issues':issues},ensure_ascii=False,indent=2))
    return 0 if report['pass'] else 1

if __name__=='__main__':raise SystemExit(main())
