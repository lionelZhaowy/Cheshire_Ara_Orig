#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from validate import NS,objects,box,text,points,intersects

def inspect(build,preview):
    model=json.loads((build/'slide-06.json').read_text());layout=json.loads((preview/'preview_layout.json').read_text())['slides'][5]
    with ZipFile(build/'soc_landscape_m5_gb.pptx') as z:objs=objects(E.fromstring(z.read('ppt/slides/slide6.xml')))
    names={i:o.find('.//p:cNvPr',NS).get('name').split(': ')[0] for i,o in objs.items()};native={names[i]:o for i,o in objs.items()}
    definitions={t['id']:t for t in model['texts']};shapes={b['id']:b for b in model['boxes']+model['regions']}
    issues={'text_outside_owner':[],'text_overlap':[],'line_through_text':[],'line_through_box':[]}
    texts=layout['texts']
    for i,t in enumerate(texts):
        id=names[int(t['shape_id'])];x,y,w,h=t['box'];owner=definitions.get(id,{}).get('owner')
        if owner:
            b=shapes[owner];bx,by,bw,bh=[b[k] for k in ['x','y','w','h']]
            if not (bx<=x and by<=y and x+w<=bx+bw and y+h<=by+bh):issues['text_outside_owner'].append([id,owner,t['box'],[bx,by,bw,bh]])
        for u in texts[i+1:]:
            xx,yy,ww,hh=u['box']
            if min(x+w,xx+ww)-max(x,xx)>1 and min(y+h,yy+hh)-max(y,yy)>1:issues['text_overlap'].append([id,names[int(u['shape_id'])]])
    for e in model['edges']:
        path=points(native[e['id']])
        for t in texts:
            if any(intersects(a,b,t['box'],1) for a,b in zip(path,path[1:])):issues['line_through_text'].append([e['id'],names[int(t['shape_id'])]])
        for b in model['boxes']:
            if b['id'].startswith('badge-'):continue
            # Intentional nested memory implementation and its external exit.
            if b['id']=='memory-target' and e['id'] in ['atomics-llc','llc-f0']:continue
            r=[b['x']+.02,b['y']+.02,b['w']-.04,b['h']-.04]
            if any(intersects(a,c,r) for a,c in zip(path,path[1:])):issues['line_through_box'].append([e['id'],b['id']])
    return issues

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--preview',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    r=inspect(a.build,a.preview);assert not a.report.exists();a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
