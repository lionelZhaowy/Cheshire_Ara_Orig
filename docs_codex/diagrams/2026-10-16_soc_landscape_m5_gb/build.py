#!/usr/bin/env python3
"""Correct slide 2 of the existing two-page deck; retain every other ZIP part."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E

NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
SCALE=12192000/3600
REMOVED=set(range(1201,1206))
CHANGED={886,*range(936,948)}
CAPTION='7 × 6 基础端口 + 扩展 | 64 bit 数据 / 48 bit 地址 | 地址译码 / 各目标仲裁'


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True)
    a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=False)
    overlay=a.out_dir/'m5-connections.svg'
    overlay.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="3600" height="2025" viewBox="0 0 3600 2025">
<defs>
<marker id="data" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#314D66"/></marker>
<marker id="gb" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="#187C78"/></marker>
</defs>
<line id="m5-target-drop" x1="2436.25" y1="1042.1" x2="2436.25" y2="1093.1" stroke="#314D66" stroke-width="7.68" fill="none" marker-end="url(#data)"/>
<path id="gb-interface-to-controller" d="M 2566.25 1170 L 2581.25 1170 L 2581.25 1068.1 L 2736.75 1068.1 C 2736.75 1050.1 2760.75 1050.1 2760.75 1068.1 L 2940 1068.1 L 2940 730 L 1506.25 730 L 1506.25 726.1 Q 1526.25 716.1 1506.25 706.1 L 1506.25 638.1" fill="none" stroke="#187C78" stroke-width="7.68" stroke-linejoin="miter" marker-end="url(#gb)"/>
<rect id="target-port-m5" x="2388.25" y="1013.1" width="96" height="29" fill="#FFFFFF" stroke="#29292D" stroke-width="4.8"/>
<text id="target-label-m5" x="2436.25" y="1040" font-family="Microsoft YaHei" font-size="22.5" font-weight="bold" text-anchor="middle" fill="#29292D">M5</text>
<rect id="gb-axi-interface" x="2306.25" y="1093.1" width="260" height="155" fill="#D9EEE8" stroke="#29292D" stroke-width="4.8"/>
<text id="gb-interface-title" x="2436.25" y="1151" font-family="Microsoft YaHei" font-size="30" font-weight="bold" text-anchor="middle" fill="#29292D">GB AXI 接口</text>
<text id="gb-interface-clients" x="2436.25" y="1190" font-family="Microsoft YaHei" font-size="30" text-anchor="middle" fill="#29292D">CPU / Ara 共用</text>
<text id="gb-interface-width" x="2436.25" y="1228" font-family="Microsoft YaHei" font-size="30" text-anchor="middle" fill="#29292D">64-bit 数据窗口</text>
</svg>
''')
    subprocess.run(['python3',str(a.native_skill_root/'scripts/run.py'),'--input',str(overlay),
                    '--out-dir',str(a.out_dir/'native-overlay'),'--aspect','source','--slide-width-in',str(12192000/914400),
                    '--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    with ZipFile(a.input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);assert len(pres.find('p:sldIdLst',NS))==2
    slide=E.fromstring(parts['ppt/slides/slide2.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    objects={int(el.find('.//p:cNvPr',NS).get('id')):el for el in tree if E.QName(el).localname in ['sp','cxnSp']}
    for id in REMOVED:tree.remove(objects[id])

    def rect(id,x=None,y=None,w=None,h=None):
        xf=objects[id].find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
        for node,key,v in [(off,'x',x),(off,'y',y),(ext,'cx',w),(ext,'cy',h)]:
            if v is not None:node.set(key,str(round(v*SCALE)))

    def text(id,value,cx,width):
        el=objects[id];body=el.find('p:txBody',NS);para=body.find('a:p',NS)
        rp=deepcopy(para.find('a:r/a:rPr',NS));assert rp is not None
        for c in list(body):
            if E.QName(c).localname=='p':body.remove(c)
        para=E.SubElement(body,'{'+NS['a']+'}p');E.SubElement(para,'{'+NS['a']+'}pPr',algn='ctr')
        run=E.SubElement(para,'{'+NS['a']+'}r');run.append(rp);E.SubElement(run,'{'+NS['a']+'}t').text=value
        body.find('a:bodyPr',NS).set('wrap','none');rect(id,x=cx-width/2,w=width)
        pr=el.find('.//p:cNvPr',NS);pr.set('name',pr.get('name').split(':')[0]+': '+value)

    text(886,CAPTION,1486.25,1310)
    # M4 remains Serial Link TX; only this right-hand target group is compacted.
    rect(936,x=2146.25,y=1042.1,h=51)
    rect(937,x=2098.25)
    text(938,'M4',2146.25,70)
    rect(939,x=2016.25,w=260)
    text(940,'Serial Link TX',2146.25,240)
    text(941,'远端目标窗口',2146.25,240)
    # Keep the optional external target after the new fixed GB target.
    rect(942,x=2748.75,y=1042.1,h=51)
    rect(943,x=2700.75)
    text(944,'M_EXT',2748.75,86)
    rect(945,x=2596.25,w=305)
    text(946,'AXI 外部 slave',2748.75,285)
    text(947,'可选外部目标扩展',2748.75,285)
    # Rename the old optional port's object keys to avoid confusing its historic
    # internal suffix "5" with the newly drawn architectural M5 port.
    objects[942].find('.//p:cNvPr',NS).set('name','target-output-ext')
    objects[943].find('.//p:cNvPr',NS).set('name','target-port-ext')
    with ZipFile(a.out_dir/'native-overlay/diagrams.pptx') as z:
        overlay_root=E.fromstring(z.read('ppt/slides/slide1.xml'))
    new_objects=[]
    for el in overlay_root.find('p:cSld/p:spTree',NS):
        if E.QName(el).localname not in ['sp','cxnSp']:continue
        el=deepcopy(el);pr=el.find('.//p:cNvPr',NS);pr.set('id',str(1300+len(new_objects)))
        new_objects.append({'id':int(pr.get('id')),'name':pr.get('name')});tree.append(el)
    data=E.tostring(slide,encoding='UTF-8',xml_declaration=True,standalone=True)
    dest=a.out_dir/'soc_landscape_m5_gb.pptx'
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,data if n=='ppt/slides/slide2.xml' else b)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    report={'input':str(a.input),'input_sha256':sha(a.input.read_bytes()),'output_sha256':sha(dest.read_bytes()),
            'removed_shape_ids':sorted(REMOVED),'changed_shape_ids':sorted(CHANGED),'new_objects':new_objects,
            'changed_package_parts':['ppt/slides/slide2.xml'],'slide1_and_all_other_parts_unchanged':True,
            'target_order':['M0','M1','M2','M3','M4','M5','M_EXT'],
            'route_bridges':[{'over':'M_EXT target drop','x':2748.75,'y':1068.1},{'over':'ISP to GB','x':1506.25,'y':716.1}],
            'office_application_tested':False}
    (a.out_dir/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(dest),'removed':len(REMOVED),'changed':len(CHANGED),'added':len(new_objects)},ensure_ascii=False))


if __name__=='__main__':main()
