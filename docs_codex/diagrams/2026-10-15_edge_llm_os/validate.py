#!/usr/bin/env python3
"""Validate this document/figure delivery; never overwrite prior evidence.

Uses only Python's standard library. Does not execute hardware/software builds.
Generation reproducibility is checked in a new temporary directory.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import ZipFile

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
DOC=ROOT/'docs_codex/engineering/Edge_LLM_OS_Selection.md'
HANDOFF=ROOT/'docs_codex/handoffs/L01_edge_llm_os_architecture.md'
INDEX=ROOT/'docs_codex/engineering/README.md'
SVG='{http://www.w3.org/2000/svg}'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-file',type=Path,required=True)
    args=ap.parse_args()
    args.out_file.parent.mkdir(parents=True,exist_ok=True)
    # Reserve the destination before checking self-referential report links.
    with args.out_file.open('x') as fp:fp.write('{}\n')
    results=[]
    def check(name,ok,detail=None):
        results.append(dict(name=name,passed=bool(ok),detail=detail))

    try:
        input_record=json.loads((D/'evidence/input.json').read_text())
        changed=[]
        for name,expected in input_record['files'].items():
            if name==input_record['allowed_existing_edit']:continue
            p=ROOT/name
            if not p.is_file() or sha(p)!=expected:changed.append(name)
        check('protected_input_files',not changed,{'checked':len(input_record['files'])-1,'changed':changed})
        before=(D/'evidence/engineering_readme_before.md').read_text()
        index_lines=INDEX.read_text().splitlines(keepends=True)
        new_lines=[s for s in index_lines if 'Edge_LLM_OS_Selection.md' in s]
        check('index_only_adds_one_entry',len(new_lines)==1 and ''.join(s for s in index_lines if s not in new_lines)==before)

        local_links=[];bad=[];external=set()
        for p in (DOC,HANDOFF,D/'README.md',INDEX):
            content=p.read_text()
            for href in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',content):
                u=urlsplit(href)
                if u.scheme in ('https','http'):
                    external.add(href);continue
                target=(p.parent/unquote(u.path)).resolve() if u.path else p
                local_links.append({'from':str(p.relative_to(ROOT)),'href':href})
                if not target.exists():bad.append(local_links[-1])
                elif u.fragment:
                    # This delivery uses file-level local links only.
                    bad.append({**local_links[-1],'reason':'anchor requires explicit checking'})
        check('local_links',not bad,{'count':len(local_links),'broken':bad})
        check('official_sources_retained',all(any(host in u for u in external) for host in [
            'github.com/ucb-bar/gemmini','arm-software.github.io/CMSIS-Ethos-U',
            'developer.nvidia.com','github.com/NVIDIA/TensorRT-Edge-LLM',
            'github.com/ggml-org/llama.cpp','docs.kernel.org/6.5',
            'huggingface.co/blog/kv-cache-quantization','www.freertos.org']),sorted(external))

        content=DOC.read_text()
        required=['## 1.','## 2.','## 3.','## 4.','## 5.','## 6.','## 7.',
                  '用户尚未冻结','192 MiB','500,000,000','201,326,592',
                  '不是同一个已选模型','v5.10.7','v6.5','未仿真']
        # Hardware validation boundary is also stated explicitly in the handoff.
        combined=content+'\n'+HANDOFF.read_text()
        check('document_topics_and_boundaries',all(x in combined for x in required),required)
        weights=10**9*4//8
        kv=2*24*1*4096*8*64*2
        check('memory_examples',weights==500000000 and kv==201326592 and kv//2**20==192,
              {'weight_bytes':weights,'weight_MiB':weights/2**20,'kv_bytes':kv,'kv_MiB':kv/2**20})

        browser=json.loads((D/'evidence/render-02/browser.json').read_text())
        check('browser_layout',browser['status']=='pass' and all(not f[k] for f in browser['figures'] for k in [
            'outside_canvas','box_text_overflow','text_line_intersections','text_overlaps']),
            {'browser':browser['chrome'],'figures':len(browser['figures'])})
        visual=json.loads((D/'evidence/visual_review.json').read_text())
        check('author_visual_review',visual['status']=='pass' and len(visual['figures'])==2)
        export=json.loads((D/'export/export_report.json').read_text())
        totals=Counter()
        with ZipFile(D/'export/diagrams.pptx') as z:
            slides=sorted(n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
            check('pptx_two_pages_and_no_images',len(slides)==2 and not any(n.startswith('ppt/media/') for n in z.namelist()) and z.testzip() is None)
            for i,name in enumerate(['software-stacks','inference-flow']):
                svg_path=D/f'{name}.svg'
                svg=ET.parse(svg_path).getroot()
                texts=[n.text or '' for n in svg.iter(SVG+'text')]
                arrows=[n for n in svg.iter() if n.get('marker-start') or n.get('marker-end')]
                dashed=[n for n in svg.iter() if n.get('stroke-dasharray')]
                elements=list(svg.iter())
                expected_ends=sum(bool(n.get(a)) for n in arrows for a in ['marker-start','marker-end'])
                slide=ET.fromstring(z.read(slides[i]))
                ppt_text=[n.text or '' for n in slide.findall('.//a:t',NS)]
                ends=[n for tag in ['a:headEnd','a:tailEnd'] for n in slide.findall('.//'+tag,NS) if n.get('type')=='triangle']
                dashes=slide.findall('.//a:custDash',NS)
                check(name+'_native_text_and_lines',ppt_text==texts and len(ends)==expected_ends and len(dashes)==len(dashed) and not slide.findall('.//p:pic',NS),
                      {'text_objects':len(texts),'arrow_objects':len(arrows),'arrow_endpoints':len(ends),'dashed_objects':len(dashes)})
                check(name+'_svg_semantics',not any(n.tag in [SVG+'image',SVG+'use'] or n.get('transform') for n in elements) and all(n.tag in [SVG+'line',SVG+'polyline',SVG+'path'] for n in arrows))
                meta=next(f for f in browser['figures'] if f['name']==name)
                check(name+'_same_source',sha(svg_path)==meta['svg_sha256']==export['figures'][i]['sha256']==sha(D/'evidence/source-01'/f'{name}.svg'))
                png=D/f'{name}.png'
                raw=png.read_bytes()
                check(name+'_png',raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(2400,1350) and sha(png)==sha(D/'evidence/render-02'/png.name))
                totals.update(text_objects=len(texts),arrow_objects=len(arrows),dashed_objects=len(dashed))
        check('export_readback_report',not export['office_application_tested'] and len(export['slides'])==2 and sum(s['text_objects'] for s in export['slides'])==totals['text_objects'])

        with tempfile.TemporaryDirectory(prefix='edge-llm-repro-') as tmp:
            out=Path(tmp)/'source'
            generation=subprocess.run([sys.executable,str(D/'build_figures.py'),'--out-dir',str(out)],capture_output=True,text=True)
            matches=generation.returncode==0 and all(sha(out/f)==sha(D/'evidence/source-01'/f) for f in ['software-stacks.svg','inference-flow.svg','layout.json'])
            check('generator_reproducibility',matches,{'returncode':generation.returncode,'stderr':generation.stderr})

        whitespace=[]
        for p in [DOC,HANDOFF,D/'README.md',*D.glob('*.py')]:
            for i,line in enumerate(p.read_text().splitlines(),1):
                if line.rstrip()!=line:whitespace.append(f'{p.relative_to(ROOT)}:{i}')
        diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
        check('whitespace_and_git_diff_check',not whitespace and diff.returncode==0,{'new_file_trailing_whitespace':whitespace,'git_diff_returncode':diff.returncode,'output':diff.stdout+diff.stderr})
        final_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
        manifests=[DOC,HANDOFF,INDEX,D/'README.md',*D.glob('*.py'),*D.glob('*.svg'),*D.glob('*.png'),D/'export/diagrams.pptx',D/'export/export_report.json']
        observation_path=D/'evidence/external_change.json'
        observation=json.loads(observation_path.read_text()) if observation_path.exists() else None
        recognized_external=bool(observation and changed==[observation['path']]
                                 and sha(ROOT/observation['path'])==observation['observed_sha256']
                                 and observation['input_sha256']==input_record['files'][observation['path']]
                                 and not observation['task_wrote_this_path'])
        failures=[r for r in results if not r['passed']]
        status='pass' if not failures else 'fail'
        if recognized_external and [r['name'] for r in failures]==['protected_input_files']:
            status='pass_with_external_changes'
        report={'date':'2026-10-15','head':input_record['head'],'status':status,
                'checks':results,'totals':dict(totals),'files':{str(p.relative_to(ROOT)):sha(p) for p in manifests},
                'status_after':final_status,'protected_input_snapshot_matches':not changed,
                'external_change_observation':observation,'office_application_tested':False,'target_build_or_run':False}
    except Exception as error:
        report={'status':'error','checks':results,'error':repr(error),'office_application_tested':False,'target_build_or_run':False}
    args.out_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(results),'failures':[r for r in results if not r['passed']],'error':report.get('error'),'totals':report.get('totals')},ensure_ascii=False,indent=2))
    return 0 if report['status'] in ('pass','pass_with_external_changes') else 1


if __name__=='__main__':raise SystemExit(main())
