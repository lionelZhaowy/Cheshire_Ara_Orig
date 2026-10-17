#!/usr/bin/env python3
"""Append a locally rearranged copy of slide 2; preserve every existing slide part."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from build import NS, SCALE

REL='http://schemas.openxmlformats.org/package/2006/relationships'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
EP='http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
VT='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
CENTERS=[71.25+(i+.5)*2830/7 for i in range(7)]
GROUPS=[(912,913,914,915,[916,917]),(918,919,920,921,[922,923]),
        (924,925,926,927,[928]),(929,930,931,932,[933,934,935]),
        (936,937,938,939,[940,941]),(1300,1302,1303,1304,[1305,1306,1307]),
        (942,943,944,945,[946,947])]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--native-skill-root',type=Path,required=True)
    args=ap.parse_args();args.out_dir.mkdir(parents=True,exist_ok=False)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    with ZipFile(args.input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS)
    assert len(sids)==2,'Input must be the protected two-page baseline'
    slide=E.fromstring(parts['ppt/slides/slide2.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    objects={int(el.find('.//p:cNvPr',NS).get('id')):el for el in tree if E.QName(el).localname in ['sp','cxnSp']}
    before={i:E.tostring(el) for i,el in objects.items()}

    def rect(i,x=None,y=None,w=None,h=None):
        xf=objects[i].find('p:spPr/a:xfrm',NS)
        for tag,key,v in [('off','x',x),('off','y',y),('ext','cx',w),('ext','cy',h)]:
            if v is not None:xf.find('a:'+tag,NS).set(key,str(round(v*SCALE)))

    def center_text(i,cx,width):
        rect(i,x=cx-width/2,w=width)
        body=objects[i].find('p:txBody',NS)
        body.find('a:bodyPr',NS).set('wrap','none')
        for p in body.findall('a:p',NS):
            pp=p.find('a:pPr',NS)
            if pp is None:pp=E.Element('{'+NS['a']+'}pPr');p.insert(0,pp)
            pp.set('algn','ctr')

    for idx,(cx,group) in enumerate(zip(CENTERS,GROUPS)):
        drop,port,label,target,texts=group;w=400 if idx==2 else 360
        rect(drop,x=cx,y=1042.1,h=51)
        rect(port,x=cx-48)
        center_text(label,cx,86 if idx==6 else 70)
        rect(target,x=cx-w/2,w=w)
        for i in texts:center_text(i,cx,w-20)
    # Preserve font sizes and the two inline memory stages inside a narrower box.
    mem=CENTERS[2]
    rect(948,x=mem-190,w=185)
    center_text(949,mem-97.5,175);center_text(950,mem-97.5,175)
    rect(951,x=mem+20,w=170)
    center_text(952,mem+105,160);center_text(953,mem+105,160)
    rect(954,x=mem-5,w=25)
    rect(958,x=CENTERS[1])
    # Keep a visible margin between the initiator-row heading and the M5 return.
    rect(911,x=1106.25)

    # Use the installed native backend for complete semantic arrow objects.
    gb_right=CENTERS[5]+180;corridor=(gb_right+CENTERS[6]-180)/2
    ext=CENTERS[6]
    overlay=args.out_dir/'page3-connections.svg'
    overlay.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="3600" height="2025" viewBox="0 0 3600 2025">
<defs>
<marker id="gb" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#187C78"/></marker>
<marker id="data" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#314D66"/></marker>
</defs>
<path id="isp-gb" d="M 2656.25 543.1 L 2641.25 543.1 L 2641.25 680.1 C 2617.25 680.1 2617.25 706.1 2641.25 706.1 L 2641.25 716.1 L 1506.25 716.1 L 1506.25 638.1" fill="none" stroke="#187C78" stroke-width="7.44" stroke-dasharray="24 14.4" stroke-linejoin="miter" marker-start="url(#gb)" marker-end="url(#gb)"/>
<path id="llc-ddr" d="M {mem+105} 1237.1 L {mem+105} 1266.1 L 2216.25 1266.1 L 2216.25 1353.1" fill="none" stroke="#314D66" stroke-width="8.64" stroke-linejoin="miter" marker-end="url(#data)"/>
<path id="gb-interface-to-controller" d="M {gb_right} 1170 L {corridor} 1170 L {corridor} 1068.1 L {ext-12} 1068.1 C {ext-12} 1050.1 {ext+12} 1050.1 {ext+12} 1068.1 L 2940 1068.1 L 2940 730 L 1436.25 730 L 1436.25 638.1" fill="none" stroke="#187C78" stroke-width="7.68" stroke-linejoin="miter" marker-end="url(#gb)"/>
</svg>
''')
    subprocess.run(['python3','-B',str(args.native_skill_root/'scripts/run.py'),
                    '--input',str(overlay),'--out-dir',str(args.out_dir/'native-overlay'),
                    '--aspect','source','--slide-width-in',str(12192000/914400),
                    '--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    with ZipFile(args.out_dir/'native-overlay/diagrams.pptx') as z:
        over=E.fromstring(z.read('ppt/slides/slide1.xml'))
    replacements={'isp-gb':860,'llc-ddr':1086,'gb-interface-to-controller':1301}
    for el in over.find('p:cSld/p:spTree',NS):
        if E.QName(el).localname not in ['sp','cxnSp']:continue
        pr=el.find('.//p:cNvPr',NS);i=replacements[pr.get('name')]
        # Preserve original native stroke/endpoint properties exactly; replace geometry.
        orig=objects[i];sp=orig.find('p:spPr',NS);newsp=el.find('p:spPr',NS)
        for tag in ['xfrm','custGeom']:
            old=sp.find('a:'+tag,NS);sp.replace(old,deepcopy(newsp.find('a:'+tag,NS)))

    serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
    parts['ppt/slides/slide3.xml']=serialize(slide)
    slide_rels=E.fromstring(parts['ppt/slides/_rels/slide2.xml.rels'])
    for rel in slide_rels:
        if rel.get('Type').endswith('/notesSlide'):rel.set('Target','../notesSlides/notesSlide3.xml')
    parts['ppt/slides/_rels/slide3.xml.rels']=serialize(slide_rels)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide2.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='3'
    parts['ppt/notesSlides/notesSlide3.xml']=serialize(notes)
    notes_rels=E.fromstring(parts['ppt/notesSlides/_rels/notesSlide2.xml.rels'])
    for rel in notes_rels:
        if rel.get('Type').endswith('/slide'):rel.set('Target','../slides/slide3.xml')
    parts['ppt/notesSlides/_rels/notesSlide3.xml.rels']=serialize(notes_rels)
    prels=E.fromstring(parts['ppt/_rels/presentation.xml.rels'])
    rid='rId'+str(max(int(r.get('Id')[3:]) for r in prels)+1)
    E.SubElement(prels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide3.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(s.get('id')) for s in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serialize(pres)
    parts['ppt/_rels/presentation.xml.rels']=serialize(prels)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for name,kind in [('slides/slide3.xml','slide'),('notesSlides/notesSlide3.xml','notesSlide')]:
        E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+name,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serialize(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='3'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='3'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector')
    E.SubElement(titles,'{'+VT+'}lpstr').text='SoC 架构：等距目标端口 / GB 接入位置调整'
    titles.set('size',str(len(titles)));parts['docProps/app.xml']=serialize(app)
    dest=args.out_dir/'soc_landscape_m5_gb.pptx'
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)
    changed=[i for i,el in objects.items() if E.tostring(el)!=before[i]]
    report={'input':str(args.input),'input_sha256':sha(args.input.read_bytes()),'output_sha256':sha(dest.read_bytes()),
            'pages':3,'copied_from_page':2,'changed_shape_ids_on_page3':changed,
            'unchanged_shapes_on_page3':len(objects)-len(changed),'target_centers':CENTERS,'target_pitch':2830/7,
            'gb_adapter_bottom':{'M5':[1436.25,638.1],'ISP':[1506.25,638.1]},
            'remaining_bridges':['ISP over DDR bypass','M5 over M_EXT target drop'],
            'office_application_tested':False}
    (args.out_dir/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
