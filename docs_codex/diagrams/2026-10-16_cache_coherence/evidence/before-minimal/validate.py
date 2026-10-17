#!/usr/bin/env python3
"""Check this documentation delivery; no RTL behavior is tested."""
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
ap=argparse.ArgumentParser()
ap.add_argument('--out-file',type=Path,required=True)
args=ap.parse_args()
assert not args.out_file.exists(),'Refusing to overwrite previous evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((D/'evidence/input.json').read_text())
protected={p:sha(ROOT/p)==h for p,h in inputs['protected'].items()}
sources={p:sha(ROOT/p)==h for p,h in inputs['source_inputs'].items()}
references={p:sha(ROOT/p)==h for p,h in inputs['reference_inputs'].items()}
backups={p:sha(D/'evidence/before'/Path(p).name)==h for p,h in inputs['editable_inputs'].items()}
assert all(protected.values()),'Protected input changed'
assert all(sources.values()),'Source input changed'
assert all(references.values()),'Reference input changed'
assert all(backups.values()),'Original document backup mismatch'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==inputs['head']

docs=[ROOT/'docs_codex/engineering/Cache_Coherence_Architecture.md',
      ROOT/'docs_codex/engineering/README.md',D/'README.md',
      ROOT/'docs_codex/handoffs/L01_cache_coherence_architecture.md']
links=[]
for p in docs:
    content=p.read_text()
    assert content.count('```')%2==0
    for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',content):
        if re.match(r'https?://',dest):continue
        path,sep,anchor=dest.partition('#')
        target=(p.parent/path).resolve() if path else p
        # This report is intentionally created only after all checks pass.
        assert target.exists() or target==args.out_file.resolve(),(p,dest)
        if anchor:
            assert f'id="{anchor}"' in target.read_text(),(p,dest)
        links.append(dict(source=str(p.relative_to(ROOT)),target=dest))

layout=json.loads((D/'layout.json').read_text())
system_edges={(e['source'],e['target']) for e in layout[0]['arrows']}
required_paths=[['cva6','xbar','atomics','llc','arb','ddr'],
                ['ara','filter','split','proxy','gb'],
                ['npu','proxy','gb'],['isp','proxy','gb'],
                ['mover','proxy','gb'],['mover','entry','arb'],['isp','entry','arb']]
for path in required_paths:
    assert all(pair in system_edges for pair in zip(path,path[1:])),path
assert ('ara','gb') not in system_edges and ('split','gb') not in system_edges
browser=json.loads((D/'evidence/render-05/browser.json').read_text())
assert browser['status']=='pass'
export=json.loads((D/'export/export_report.json').read_text())
NS={'s':'http://www.w3.org/2000/svg','a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
slides=[]
with ZipFile(D/'export/diagrams.pptx') as z:
    slide_names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
    assert len(slide_names)==3
    assert not any(n.startswith('ppt/media/') for n in z.namelist())
    for i,fig in enumerate(layout):
        name=fig['name']; svg=ET.parse(D/(name+'.svg')).getroot()
        source_texts=[''.join(t.itertext()) for t in svg.findall('s:text',NS)]
        ppt=ET.fromstring(z.read(f'ppt/slides/slide{i+1}.xml'))
        ppt_texts=[t.text for t in ppt.findall('.//a:t',NS)]
        assert Counter(source_texts)==Counter(ppt_texts),(name,'text mismatch')
        assert not ppt.findall('.//p:pic',NS)
        assert len(ppt.findall('.//a:tailEnd',NS))==len(fig['arrows'])
        assert len(ppt.findall('.//a:headEnd',NS))==sum(e['bidirectional'] for e in fig['arrows'])
        dashed=len([e for e in svg if 'stroke-dasharray' in e.attrib])
        assert len(ppt.findall('.//a:custDash',NS))==dashed
        assert sha(D/'evidence/source-04'/(name+'.svg'))==sha(D/(name+'.svg'))
        assert export['figures'][i]['sha256']==sha(D/(name+'.svg'))==browser['figures'][i]['svg_sha256']
        assert (D/(name+'.png')).read_bytes()==(D/'evidence/render-05'/(name+'.png')).read_bytes()
        for edge in fig['arrows']:
            for endpoint,index in [('source',0),('target',-1)]:
                if not edge[endpoint]:continue
                b=fig['boxes'][edge[endpoint]];x,y=edge['points'][index]
                on_edge=((x==b['x'] or x==b['x']+b['width']) and b['y']<=y<=b['y']+b['height']) or ((y==b['y'] or y==b['y']+b['height']) and b['x']<=x<=b['x']+b['width'])
                assert on_edge,(name,edge['id'],endpoint)
        slides.append(dict(name=name,text_objects=len(ppt_texts),native_arrows=len(fig['arrows']),
                           native_dashed_shapes=dashed,whole_image_media=False,endpoint_geometry='pass'))

diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert diff.returncode==0,diff.stdout+diff.stderr
for p in [*docs,*D.glob('*.py')]:
    for n,line in enumerate(p.read_text().splitlines(),1):
        assert line==line.rstrip(),(p,n,'trailing whitespace')
doc=docs[0].read_text()
chinese_chars=len(re.findall(r'[\u4e00-\u9fff]',doc))
assert 2500<=chinese_chars<=3500,chinese_chars
assert len(re.findall(r'^!\[',doc,re.M))==3
artifacts=[*docs,*D.glob('*.svg'),*D.glob('*.png'),*D.glob('*.py'),D/'layout.json',D/'export/diagrams.pptx',D/'export/export_report.json']
report=dict(date='2026-10-16',status='pass',head=inputs['head'],scope='Documentation and diagrams only',
            chinese_characters=chinese_chars,local_links_checked=len(links),links=links,
            slides=slides,protected_files=protected,source_inputs=sources,
            reference_inputs=references,original_backups=backups,required_data_paths=required_paths,
            browser_report='evidence/render-05/browser.json',visual_review='Author inspected all three final PNGs; no clipping, text overlap, or broken connections.',
            office_application_tested=False,software_or_rtl_execution=False,git_diff_check='pass',
            artifacts={str(p.relative_to(ROOT)):sha(p) for p in artifacts})
args.out_file.parent.mkdir(parents=True,exist_ok=True)
args.out_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','chinese_characters','local_links_checked','slides','office_application_tested','software_or_rtl_execution']},ensure_ascii=False,indent=2))
