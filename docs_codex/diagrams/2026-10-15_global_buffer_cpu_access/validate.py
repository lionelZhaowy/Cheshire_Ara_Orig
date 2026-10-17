#!/usr/bin/env python3
"""Validate GB documentation/artifacts; this does not test RTL behavior."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
NS={'s':'http://www.w3.org/2000/svg','a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-file',type=Path,required=True)
    args=p.parse_args()
    assert not args.out_file.exists(),'Refusing to overwrite evidence'
    inputs=json.loads((D/'evidence/input.json').read_text())
    protected={path:sha(ROOT/path)==digest for path,digest in inputs['protected'].items()}
    sources={path:sha(ROOT/path)==digest for path,digest in inputs['source_inputs'].items()}
    assert all(protected.values()),[p for p,v in protected.items() if not v]
    assert all(sources.values()),[p for p,v in sources.items() if not v]
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==inputs['head']
    docs=[ROOT/'docs_codex/engineering/Global_Buffer_CPU_Access.md',D/'README.md',
          ROOT/'docs_codex/handoffs/L01_global_buffer_cpu_access.md']
    links=[]
    for doc in docs:
        content=doc.read_text()
        assert content.count('```')%2==0
        for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',content):
            if re.match(r'https?://',dest):continue
            path,_,anchor=dest.partition('#')
            target=(doc.parent/path).resolve() if path else doc
            assert target.exists() or target==args.out_file.resolve(),(doc,dest)
            if anchor:assert f'id="{anchor}"' in target.read_text(),(doc,dest)
            links.append({'source':str(doc.relative_to(ROOT)),'target':dest})
    layout=json.loads((D/'layout.json').read_text())
    browser=json.loads((D/'evidence/render-03/browser.json').read_text())
    export=json.loads((D/'export/export_report.json').read_text())
    assert browser['status']=='pass'
    assert len(layout)==2
    left,right=layout
    assert left['boxes']=={k:v for k,v in right['boxes'].items() if k!='host-port'}
    assert left['arrows']==[e for e in right['arrows'] if e['id'] not in ['xbar-host','host-gb']]
    assert not any(e['target']=='arbiter' and e['source']=='xbar' for e in left['arrows'])
    slides=[]
    with ZipFile(D/'export/diagrams.pptx') as z:
        names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        assert len(names)==2
        assert not any(n.startswith('ppt/media/') for n in z.namelist())
        for i,fig in enumerate(layout):
            name=fig['name'];svg=ET.parse(D/(name+'.svg')).getroot()
            source_texts=[''.join(t.itertext()) for t in svg.findall('s:text',NS)]
            ppt=ET.fromstring(z.read(f'ppt/slides/slide{i+1}.xml'))
            ppt_texts=[t.text for t in ppt.findall('.//a:t',NS)]
            assert Counter(source_texts)==Counter(ppt_texts),(name,'text mismatch')
            assert not ppt.findall('.//p:pic',NS)
            assert len(ppt.findall('.//a:tailEnd',NS))==len(fig['arrows'])
            assert len(ppt.findall('.//a:headEnd',NS))==sum(e['bidirectional'] for e in fig['arrows'])
            assert export['figures'][i]['sha256']==sha(D/(name+'.svg'))==browser['figures'][i]['svg_sha256']
            assert (D/(name+'.png')).read_bytes()==(D/'evidence/render-03'/(name+'.png')).read_bytes()
            for edge in fig['arrows']:
                for endpoint,index in [('source',0),('target',-1)]:
                    b=fig['boxes'][edge[endpoint]];x,y=edge['points'][index]
                    on_edge=((x==b['x'] or x==b['x']+b['width']) and b['y']<=y<=b['y']+b['height']) or ((y==b['y'] or y==b['y']+b['height']) and b['x']<=x<=b['x']+b['width'])
                    assert on_edge,(name,edge['id'],endpoint)
                for (x1,y1),(x2,y2) in zip(edge['points'],edge['points'][1:]):
                    for key,b in fig['boxes'].items():
                        if key.endswith('-domain'):continue
                        l,r,t,bt=b['x']+1,b['x']+b['width']-1,b['y']+1,b['y']+b['height']-1
                        hit=(x1==x2 and l<x1<r and max(min(y1,y2),t)<min(max(y1,y2),bt)) or (y1==y2 and t<y1<bt and max(min(x1,x2),l)<min(max(x1,x2),r))
                        assert not hit,(name,edge['id'],'line enters module',key)
            slides.append({'name':name,'text_objects':len(ppt_texts),'native_arrows':len(fig['arrows']),
                           'endpoint_geometry':'pass','lines_cross_module_interiors':False,'rasterized_picture_objects':False})
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stdout+diff.stderr
    for f in [*docs,*D.glob('*.py')]:
        for n,line in enumerate(f.read_text().splitlines(),1):assert line==line.rstrip(),(f,n)
    artifacts=[*docs,*D.glob('*.svg'),*D.glob('*.png'),*D.glob('*.py'),D/'layout.json',
               D/'export/diagrams.pptx',D/'export/export_report.json']
    report={'date':'2026-10-15','status':'pass','head':inputs['head'],'scope':'Documentation and figures only',
            'local_links_checked':len(links),'links':links,'slides':slides,'common_layout':'identical',
            'protected_files':protected,'source_inputs':sources,'browser_report':'evidence/render-03/browser.json',
            'visual_review':'Author inspected both final PNGs; continuous connections and readable labels.',
            'office_application_tested':False,'software_or_rtl_execution':False,'git_diff_check':'pass',
            'artifacts':{str(f.relative_to(ROOT)):sha(f) for f in artifacts}}
    args.out_file.parent.mkdir(parents=True,exist_ok=True)
    args.out_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','local_links_checked','slides','office_application_tested','software_or_rtl_execution']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
