#!/usr/bin/env python3
"""Validate documentation artifacts only; no target build or simulator runs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
DOC=ROOT/'docs_codex/engineering/CPU_NPU_Inference_Systems_Survey.md'
HANDOFF=ROOT/'docs_codex/handoffs/L01_cpu_npu_inference_survey.md'
INDEX=ROOT/'docs_codex/engineering/README.md'
NAMES=('deployment-chain','invocation-paths','deeploy-siracusa','llm-phases')
NS={'s':'http://www.w3.org/2000/svg','p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-file',required=True,type=Path)
    out=ap.parse_args().out_file
    if out.exists():raise SystemExit('Refusing to overwrite evidence')
    checks=[]
    def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    text=DOC.read_text()
    count=len(re.findall(r'[\u4e00-\u9fff]',text))
    check('Chinese length',6000<=count<=8000,{'CJK_characters':count})
    check('seven case sections',all(x in text for x in ['### 2.1 NVDLA','### 2.2 Ethos-U','### 2.3 Rockchip','### 2.4 Qualcomm','### 3.1 Gemmini','### 3.2 Deeploy','### 3.3 llm.npu']))
    check('four embedded figures',len(re.findall(r'!\[[^]]*\]\([^)]*\.png\)',text))==4)
    missing=[];local_count=0;trailing=[]
    for p in (DOC,HANDOFF,D/'README.md',INDEX):
        s=p.read_text()
        for label,url in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',s):
            if '://' in url or url.startswith('#'):continue
            rel=url.split('#',1)[0]
            if rel:
                local_count+=1
                if not (p.parent/rel).exists() and (p.parent/rel).resolve()!=out.resolve():missing.append({'file':str(p.relative_to(ROOT)),'target':url})
        trailing.extend(f'{p.name}:{i}' for i,l in enumerate(s.splitlines(),1) if l.rstrip()!=l)
    check('local links exist',not missing,{'checked':local_count,'missing':missing})
    check('no trailing whitespace',not trailing,trailing)
    layouts=json.loads((D/'layout.json').read_text())
    browser=json.loads((D/'evidence/render-05/browser.json').read_text())
    visual=json.loads((D/'evidence/visual-review.json').read_text())
    check('final browser layout',browser['status']=='pass' and len(browser['figures'])==4)
    check('author PNG inspection',len(visual['figures'])==4 and all(x['pixels_file_identical_to_reviewed'] and x['sha256']==digest(D/(x['name']+'.png')) for x in visual['figures']))
    svg_roots=[];end_errors=[]
    def boundary(p,b):
        x,y=p;l,t,w,h=b['x'],b['y'],b['width'],b['height'];r,bot=l+w,t+h
        return ((x==l or x==r) and t<=y<=bot) or ((y==t or y==bot) and l<=x<=r)
    for name,layout,b in zip(NAMES,layouts,browser['figures']):
        svg=D/(name+'.svg');root=ET.parse(svg).getroot();svg_roots.append(root)
        ids=[n.get('id') for n in root.iter() if n.get('id')]
        check(name+' unique SVG IDs',len(ids)==len(set(ids)))
        check(name+' render source identity',digest(svg)==b['svg_sha256'])
        png=(D/(name+'.png')).read_bytes()
        check(name+' PNG dimensions',png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(2400,1350))
        check(name+' final PNG identity',png==(D/'evidence/render-05'/(name+'.png')).read_bytes())
        for edge in layout['arrows']:
            pts=edge['points']
            if not boundary(pts[0],layout['boxes'][edge['source']]) or not boundary(pts[-1],layout['boxes'][edge['target']]):
                end_errors.append([name,edge['id']])
            if any(a[0]!=b[0] and a[1]!=b[1] for a,b in zip(pts,pts[1:])):end_errors.append([name,edge['id'],'not orthogonal'])
    check('all connector endpoints on declared blocks',not end_errors,{'arrows':sum(len(x['arrows']) for x in layouts),'errors':end_errors})
    with tempfile.TemporaryDirectory(prefix='l01-inference-rebuild-') as t:
        dest=Path(t)/'generated'
        r=subprocess.run(['python3',str(D/'build_figures.py'),'--out-dir',str(dest)],capture_output=True,text=True)
        equal=r.returncode==0 and all((dest/(n+'.svg')).read_bytes()==(D/(n+'.svg')).read_bytes() for n in NAMES) and (dest/'layout.json').read_bytes()==(D/'layout.json').read_bytes()
        check('SVG generator reproducibility',equal,{'exit_code':r.returncode})
    ppt=[]
    with zipfile.ZipFile(D/'export/diagrams.pptx') as z:
        slides=sorted(n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
        check('PPTX four slides',len(slides)==4)
        media=[n for n in z.namelist() if n.startswith('ppt/media/')]
        check('PPTX no image media',not media,media)
        for name,slide,svg in zip(NAMES,slides,svg_roots):
            s=ET.fromstring(z.read(slide));texts=[t.text or '' for t in s.findall('.//a:t',NS)]
            expected=[t.text or '' for t in svg.findall('.//s:text',NS)]
            check(name+' editable PPTX text',texts==expected,{'text_objects':len(texts)})
            arrows=[];dashes=0
            for line in s.findall('.//a:ln',NS):
                a=line.find('a:headEnd',NS);b=line.find('a:tailEnd',NS)
                pair=(a is not None and a.get('type')=='triangle',b is not None and b.get('type')=='triangle')
                if any(pair):arrows.append(pair)
                if line.find('a:custDash',NS) is not None:dashes+=1
            expected_arrows=[(e.get('marker-start') is not None,e.get('marker-end') is not None) for e in svg.iter() if e.get('marker-end') or e.get('marker-start')]
            expected_dashes=sum(bool(e.get('stroke-dasharray')) for e in svg.iter())
            check(name+' whole native arrows',arrows==expected_arrows,{'arrows':len(arrows)})
            check(name+' native dashed shapes',dashes==expected_dashes,{'dashes':dashes})
            check(name+' no slide pictures',not s.findall('.//p:pic',NS))
            ppt.append(dict(name=name,text_objects=len(texts),native_arrows=len(arrows),native_dashed_objects=dashes,shapes=len(s.findall('.//p:sp',NS))+len(s.findall('.//p:cxnSp',NS))))
    report=json.loads((D/'export/export_report.json').read_text())
    check('exporter saved/reopened validation',report['pptx_created'] and len(report['slides'])==4 and not report['office_application_tested'])
    before=json.loads((D/'evidence/input.json').read_text());changed=[]
    index_path=str(INDEX.relative_to(ROOT))
    for rel,sha in before['sha256'].items():
        if rel==index_path:continue
        p=ROOT/rel
        if not p.is_file() or digest(p)!=sha:changed.append(rel)
    check('all other pre-existing files preserved',not changed,{'files_checked':len(before['sha256'])-1,'changes':changed})
    old=(D/'evidence/engineering_readme_before.md').read_text()
    new=INDEX.read_text();added=[l for l in new.splitlines(keepends=True) if 'CPU_NPU_Inference_Systems_Survey.md' in l]
    check('index preserves prior content',len(added)==1 and new.replace(added[0],'',1)==old)
    links=json.loads((D/'evidence/external-links.json').read_text())
    check('external links fetched',len(links['links'])>=20 and all(x.get('status')==200 for x in links['links']),{'links':len(links['links']),'failures':[x for x in links['links'] if x.get('status')!=200]})
    result={'date':'2026-10-16','status':'pass' if all(c['passed'] for c in checks) else 'fail','checks':checks,'pptx':ppt,'office_application_tested':False,'target_build_simulation_or_board_test':False}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[c for c in checks if not c['passed']],'pptx':ppt},ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['status']=='pass' else 1)


if __name__=='__main__':main()
