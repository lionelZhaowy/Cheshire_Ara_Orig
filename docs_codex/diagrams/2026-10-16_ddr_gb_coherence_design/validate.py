#!/usr/bin/env python3
"""Validate the standalone explanation, native figures, topology and existing-file protection."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import markdown

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
REPORT=D/'evidence/validation.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((D/'evidence/input.json').read_text())
allowed=set(inputs['allowed_existing_edits'])
protected=[]
for path,digest in inputs['protected'].items():
    if path in allowed:continue
    assert (ROOT/path).is_file() and sha(ROOT/path)==digest,path
    protected.append(path)
for path,digest in inputs['source_hashes'].items():assert sha(ROOT/path)==digest,path
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==inputs['head']

doc=ROOT/'docs_codex/engineering/DDR_GB_Coherence_Design.md'
docs=[doc]+[ROOT/p for p in inputs['allowed_existing_edits']]+[D/'README.md']
links=[]
for p in docs:
    text=p.read_text()
    assert text.count('```')%2==0,p
    for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
        if '://' in dest:continue
        path,sep,anchor=dest.partition('#')
        target=(p.parent/unquote(path)).resolve() if path else p
        assert target.exists() or target==REPORT,(p,dest)
        if anchor and target.exists():
            html=markdown.markdown(target.read_text(),extensions=['toc','tables'])
            assert f'id="{unquote(anchor)}"' in html,(p,dest)
        links.append({'source':str(p.relative_to(ROOT)),'target':dest})

NS={'s':'http://www.w3.org/2000/svg','a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
base=ET.parse(ROOT/'docs_codex/diagrams/2026-10-12_industrial_redraw/ddr_interconnect.svg').getroot()
system=ET.parse(D/'figures/system.svg').getroot()
by_id={e.get('id'):e for e in system.iter() if e.get('id')}
labels={'o8':'L1D / 写缓冲','o30':'共享数据代理','o79':'WB 缓存 / 片上 SPM'}
base_ids=[]
for old in base.iter():
    key=old.get('id')
    if not key:continue
    new=by_id[key]
    attrs=lambda e:{k:v for k,v in e.attrib.items() if k not in ['font-family','data-owner']}
    assert old.tag==new.tag and attrs(old)==attrs(new),(key,'geometry/style changed')
    if old.tag.endswith('}text'):assert new.text==labels.get(key,old.text),(key,'base label changed')
    base_ids.append(key)
assert system.get('viewBox')==base.get('viewBox')
layout=json.loads((D/'figures/layout.json').read_text())
edges={(e['source'],e['target']) for e in layout[0]['arrows']}
paths=[['cpu','xbar','atomics','llc','ddr-port0'],['ara','filter','split','width','xbar'],
       ['split','router','gb'],['npu','router','gb'],['isp','router','gb'],
       ['mover','router','gb'],['mover','ddr-port1'],['frame','ddr-port2']]
for path in paths:assert all(edge in edges for edge in zip(path,path[1:])),path
assert ('ara','gb') not in edges and ('llc','gb') not in edges

browser=json.loads((D/'previews/browser.json').read_text())
assert browser['status']=='pass'
slides=[]
with ZipFile(D/'export/diagrams.pptx') as z:
    assert len([p for p in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',p)])==3
    assert not any(p.startswith('ppt/media/') for p in z.namelist())
    for i,fig in enumerate(layout):
        name=fig['name'];svg=ET.parse(D/'figures'/(name+'.svg')).getroot()
        ppt=ET.fromstring(z.read(f'ppt/slides/slide{i+1}.xml'))
        st=[''.join(e.itertext()) for e in svg.findall('s:text',NS)]
        pt=[e.text for e in ppt.findall('.//a:t',NS)]
        assert Counter(st)==Counter(pt),(name,'text mismatch')
        assert not ppt.findall('.//p:pic',NS)
        arrows=sum(e.get('arrowed',True) for e in fig['arrows'])
        assert len(ppt.findall('.//a:tailEnd',NS))==arrows
        assert len(ppt.findall('.//a:headEnd',NS))==sum(e['bidirectional'] for e in fig['arrows'])
        dashed=sum('stroke-dasharray' in e.attrib for e in svg)
        assert len(ppt.findall('.//a:custDash',NS))==dashed
        assert sha(D/'figures'/(name+'.svg'))==browser['figures'][i]['svg_sha256']
        for edge in fig['arrows']:
            for (x,y),(a,b) in zip(edge['points'],edge['points'][1:]):assert x==a or y==b
            for endpoint,index in [('source',0),('target',-1)]:
                if not edge[endpoint]:continue
                b=fig['boxes'][edge[endpoint]];x,y=edge['points'][index]
                on_edge=((x==b['x'] or x==b['x']+b['width']) and b['y']<=y<=b['y']+b['height']) or ((y==b['y'] or y==b['y']+b['height']) and b['x']<=x<=b['x']+b['width'])
                assert on_edge,(name,edge['id'],endpoint)
        slides.append(dict(name=name,texts=len(pt),native_arrows=arrows,native_dashed_shapes=dashed,pictures=0))

doc_browser=json.loads((D/'evidence/document-browser.json').read_text())
assert doc_browser['status']=='pass'
for d in doc_browser['documents']:assert sha(ROOT/d['source'])==d['sha256'],d['source']
assert [len(d['images']) for d in doc_browser['documents']]==[3]
cp=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert cp.returncode==0,cp.stdout+cp.stderr
for p in docs+list(D.glob('*.py')):
    assert all(l==l.rstrip() for l in p.read_text().splitlines()),p
counts={p.name:len(re.findall(r'[\u4e00-\u9fff]',p.read_text())) for p in [doc]}
body=doc.read_text()
assert len(re.findall(r'^## ',body,re.M))==8
assert len(re.findall(r'!\[',body))==3
assert 5000 <= counts[doc.name] <= 6500
assert not re.search(r'\b[A-F]\s*类|如何|为什么|怎样|[？?]', '\n'.join(re.findall(r'^## .+',body,re.M)))
assert not re.search(r'\b[A-F]\s*类',body)
assert len(body.split('```c\n')[1].split('```')[0].splitlines())<=35
old=ROOT/'docs_codex/engineering/Cache_Coherence_Architecture.md'
old_before=(D/'evidence/before/docs_codex/engineering/Cache_Coherence_Architecture.md').read_text()
added='本方案的主要讲解入口已更新为[《DDR–GB 数据同步设计：从裸机推理到缓存维护》](DDR_GB_Coherence_Design.md)，沿一次推理解释数据版本、同步调用及硬件职责。本页保留此前的规划讨论与证据。\n\n'
assert old.read_text().replace(added,'',1)==old_before
handoff=ROOT/'docs_codex/handoffs/L01_cache_coherence_architecture.md'
assert handoff.read_text().startswith((D/'evidence/before/docs_codex/handoffs/L01_cache_coherence_architecture.md').read_text())
report=dict(status='pass',date='2026-10-16',head=inputs['head'],chinese_characters=counts,
            local_links_checked=len(links),links=links,slides=slides,
            protected_files_unchanged=len(protected),protected_files=protected,
            source_files_unchanged=list(inputs['source_hashes']),approved_base_objects_preserved=len(base_ids),
            required_data_paths=paths,base_geometry_and_data_lines='unchanged',
            diagram_browser='previews/browser.json',document_browser='evidence/document-browser.json',
            visual_review='All three PNGs inspected; final version-data correction inspected; no clipping, text overlap or broken connections.',
            office_application_tested=False,hardware_execution=False,git_diff_check='pass')
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','chinese_characters','local_links_checked','slides','protected_files_unchanged','approved_base_objects_preserved']},ensure_ascii=False,indent=2))
