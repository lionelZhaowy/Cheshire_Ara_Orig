#!/usr/bin/env python3
"""Duplicate the supplied slide, changing only the agreed Ara/GB topology.

Original ZIP parts (including slide 1) are copied byte-for-byte unless named in
the package manifest. New native objects come from the installed skill backend.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E

NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
SCALE=12192000/3600
REMOVED={793,794,795,800,801,827,828}
CHANGED={778,787,797,798,816,860,883,886,947}


def xml(r):return E.tostring(r,encoding='UTF-8',xml_declaration=True,standalone=True)
def digest(b):return hashlib.sha256(b).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True)
    a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=False)
    overlay=a.out_dir/'new-connections.svg'
    overlay.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="3600" height="2025" viewBox="0 0 3600 2025">
<defs>
<marker id="data" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#314D66"/></marker>
<marker id="gb" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#187C78"/></marker>
</defs>
<line id="filter-width-direct" x1="606.25197" y1="541.13996" x2="826.25197" y2="541.13996" stroke="#314D66" stroke-width="7.68" fill="none" marker-end="url(#data)"/>
<path id="xbar-shared-gb" d="M 1040 878.13996 L 1040 615 L 1391.25197 615" fill="none" stroke="#187C78" stroke-width="7.68" stroke-linejoin="miter" marker-end="url(#gb)"/>
<rect id="gb-target-port" x="985" y="878.13996" width="110" height="29" fill="#D9EEE8" stroke="#187C78" stroke-width="4.8"/>
<text id="gb-target-label" x="1040" y="900.13996" font-family="Microsoft YaHei" font-size="24" font-weight="bold" text-anchor="middle" fill="#187C78">M_GB</text>
<text id="shared-gb-label" x="1220" y="568" font-family="Microsoft YaHei" font-size="30" text-anchor="middle" fill="#187C78">CPU / Ara 共享出口</text>
<text id="shared-gb-width" x="1220" y="604" font-family="Microsoft YaHei" font-size="28" text-anchor="middle" fill="#187C78">AXI64 → GB 适配</text>
</svg>
''')
    subprocess.run(['python3',str(a.native_skill_root/'scripts/run.py'),'--input',str(overlay),
                    '--out-dir',str(a.out_dir/'native-overlay'),'--aspect','source','--slide-width-in',str(12192000/914400),
                    '--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    with ZipFile(a.input) as source:
        parts={n:source.read(n) for n in source.namelist()}
    original=E.fromstring(parts['ppt/slides/slide1.xml'])
    slide=deepcopy(original);tree=slide.find('p:cSld/p:spTree',NS)
    def ident(el):
        pr=el.find('.//p:cNvPr',NS)
        return int(pr.get('id')) if pr is not None else None
    objects={ident(el):el for el in tree if ident(el) is not None}
    for id in REMOVED:tree.remove(objects[id])

    def text(id,value,x=None,width=None,font_px=None):
        el=objects[id];body=el.find('p:txBody',NS)
        para=body.find('a:p',NS);run=para.find('a:r',NS);assert run is not None
        props=deepcopy(run.find('a:rPr',NS))
        if font_px:props.set('sz',str(round(font_px*SCALE/127)))
        for c in list(body):
            if E.QName(c).localname=='p':body.remove(c)
        para=E.SubElement(body,'{'+NS['a']+'}p')
        E.SubElement(para,'{'+NS['a']+'}pPr',algn='ctr')
        r=E.SubElement(para,'{'+NS['a']+'}r');r.append(props)
        E.SubElement(r,'{'+NS['a']+'}t').text=value
        bp=body.find('a:bodyPr',NS);bp.set('wrap','none')
        xf=el.find('p:spPr/a:xfrm',NS)
        if x is not None:xf.find('a:off',NS).set('x',str(round(x*SCALE)))
        if width is not None:xf.find('a:ext',NS).set('cx',str(round(width*SCALE)))
    text(778,'SoC 架构：CPU / Ara 共享 GB 出口',x=1100,width=1200,font_px=42)
    text(787,'2 lanes · VLSU / AXI：64 bit')
    text(797,'等宽透传')
    text(798,'64 → 64 bit',font_px=24)
    text(816,'CPU / Ara / NPU / ISP 工作区',x=1680,width=465,font_px=28)
    text(883,'Ara AXI64')
    text(886,'7 × 5 基础端口 + GB / 扩展  |  64 bit 数据 / 48 bit 地址  |  地址译码 / 各目标仲裁',x=830,width=1310,font_px=28)
    text(947,'可选外部目标扩展')
    # The left ISP-GB jump crossed the deleted Ara branch. Keep the ISP path,
    # removing only this now-unnecessary jump; its other DDR crossing remains.
    isp_path=objects[860].find('p:spPr/a:custGeom/a:pathLst/a:path',NS)
    curves=isp_path.findall('a:cubicBezTo',NS);assert len(curves)==2
    old_curve=curves[-1];straight=E.Element('{'+NS['a']+'}lnTo')
    straight.append(deepcopy(old_curve[-1]));isp_path.replace(old_curve,straight)
    with ZipFile(a.out_dir/'native-overlay/diagrams.pptx') as z:
        overlay_root=E.fromstring(z.read('ppt/slides/slide1.xml'))
    new_objects=[]
    for el in overlay_root.find('p:cSld/p:spTree',NS):
        if E.QName(el).localname not in ['sp','cxnSp']:continue
        el=deepcopy(el);pr=el.find('.//p:cNvPr',NS)
        pr.set('id',str(1200+len(new_objects)));new_objects.append({'id':pr.get('id'),'name':pr.get('name')})
        tree.append(el)
    changed_parts={}
    changed_parts['ppt/slides/slide2.xml']=xml(slide)
    rels=E.fromstring(parts['ppt/slides/_rels/slide1.xml.rels'])
    for rel in rels:
        if rel.get('Type').endswith('/notesSlide'):rel.set('Target','../notesSlides/notesSlide2.xml')
    changed_parts['ppt/slides/_rels/slide2.xml.rels']=xml(rels)
    changed_parts['ppt/notesSlides/notesSlide2.xml']=parts['ppt/notesSlides/notesSlide1.xml']
    notesrels=E.fromstring(parts['ppt/notesSlides/_rels/notesSlide1.xml.rels'])
    for rel in notesrels:
        if rel.get('Type').endswith('/slide'):rel.set('Target','../slides/slide2.xml')
    changed_parts['ppt/notesSlides/_rels/notesSlide2.xml.rels']=xml(notesrels)
    pres=E.fromstring(parts['ppt/presentation.xml'])
    ids=pres.find('p:sldIdLst',NS);assert len(ids)==1
    E.SubElement(ids,'{'+NS['p']+'}sldId',{'id':str(int(ids[0].get('id'))+1),'{'+NS['r']+'}id':'rId10'})
    changed_parts['ppt/presentation.xml']=xml(pres)
    rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);assert not any(r.get('Id')=='rId10' for r in rels)
    E.SubElement(rels,'{'+REL+'}Relationship',Id='rId10',Type=NS['r']+'/slide',Target='slides/slide2.xml')
    changed_parts['ppt/_rels/presentation.xml.rels']=xml(rels)
    types=E.fromstring(parts['[Content_Types].xml'])
    for filename,content in [('slide','application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),('notesSlide','application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')]:
        folder='slides' if filename=='slide' else 'notesSlides'
        E.SubElement(types,'{'+CT+'}Override',PartName=f'/ppt/{folder}/{filename}2.xml',ContentType=content)
    changed_parts['[Content_Types].xml']=xml(types)
    app=E.fromstring(parts['docProps/app.xml']);ep=E.QName(app).namespace;vt='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    for tag in ['Slides','Notes']:app.find('{'+ep+'}'+tag).text='2'
    heading=app.find('{'+ep+'}HeadingPairs/{'+vt+'}vector')
    heading[-1][0].text='2'
    titles=app.find('{'+ep+'}TitlesOfParts/{'+vt+'}vector')
    E.SubElement(titles,'{'+vt+'}lpstr').text='SoC 架构：CPU / Ara 共享 GB 出口';titles.set('size',str(len(titles)))
    changed_parts['docProps/app.xml']=xml(app)
    dest=a.out_dir/'soc_landscape_shared_gb.pptx'
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,b in {**parts,**changed_parts}.items():z.writestr(n,b)
    report={'input':str(a.input),'input_sha256':digest(a.input.read_bytes()),'output_sha256':digest(dest.read_bytes()),
            'removed_shape_ids':sorted(REMOVED),'changed_shape_ids':sorted(CHANGED),'new_objects':new_objects,
            'changed_existing_package_parts':[n for n in changed_parts if n in parts],
            'new_package_parts':[n for n in changed_parts if n not in parts],
            'original_slide_xml_unchanged':True,'office_application_tested':False}
    (a.out_dir/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
