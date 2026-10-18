#!/usr/bin/env python3
"""Append a native clone of the corrected slide 6; edit only the agreed objects.

Existing objects keep their actual DrawingML styles, theme and shape IDs. The
native SVG backend is used only for nine changed/new path geometries. It does
not regenerate the page or supply styles for any inherited object.
"""
import argparse, hashlib, json, re, subprocess
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from append_uniform_page import NS, REL, R, CT, EP, VT
from build_page6 import named, replace_text
from build_page4 import Diagram, SVG

D = Path(__file__).resolve().parent
SCALE = 12192000 / 3600
EXPECTED = '7330221874eb045d9fd2511a834d64c6ba45b98e5c7fb7014c67dee088277f31'
NEW_TO_OLD = dict(enumerate([1,2,3,4,14,8,13,11,5,6,7,9,10,12,15,16], 1))
OLD_TO_NEW = {old:new for new,old in NEW_TO_OLD.items()}
MIRROR_BLOCKS = ['lvds-rx','rx-cdc','isp','frame-select','frame-dma']
PIXEL_EDGES = [a+'-to-'+b for a,b in zip(MIRROR_BLOCKS,MIRROR_BLOCKS[1:])]
EDIT_EDGES = set(PIXEL_EDGES + ['raw-bypass','isp-gb','frame-f2'])
NEW_EDGES = {'sensor-rx','tx-processor'}
serial = lambda e:E.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)

def translate(el, dx=0, dy=0):
    off = el.find('p:spPr/a:xfrm/a:off', NS)
    for axis,delta in [('x',dx),('y',dy)]:
        if delta:off.set(axis,str(int(off.get(axis))+round(delta*SCALE)))

def width_about_center(el, width):
    xf=el.find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
    mid=int(off.get('x'))+int(ext.get('cx'))/2;new=round(width*SCALE)
    off.set('x',str(round(mid-new/2)));ext.set('cx',str(new))

def build(input, out, native_skill_root):
    assert hashlib.sha256(input.read_bytes()).hexdigest()==EXPECTED, 'Use corrected six-page input'
    out.mkdir(parents=True,exist_ok=False)
    with ZipFile(input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS);assert len(sids)==6
    slide=E.fromstring(parts['ppt/slides/slide6.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    objs=named(slide)  # Never rebuild this map during a simultaneous renumbering.
    model=json.loads((D/'evidence/page6-f3-build/slide-06.json').read_text())
    boxes={b['id']:b for b in model['boxes']+model['regions']}
    texts={t['id']:t for t in model['texts']};edges={e['id']:e for e in model['edges']}
    original=deepcopy(model);oldboxes={b['id']:b for b in original['boxes']+original['regions']}
    moved=set();renamed={};text_changed=set()

    def move(name,dx=0,dy=0):
        if not dx and not dy:return
        translate(objs[name],dx,dy);moved.add(name)
        item=boxes.get(name,texts.get(name));item['x']+=dx;item['y']+=dy

    def text_edit(name,value):
        if texts[name]['text']==value:return
        replace_text(objs[name],value);texts[name]['text']=value;text_changed.add(name)

    # Move the original function group to its new slot. All lookups use old IDs.
    for old,new in OLD_TO_NEW.items():
        origin=oldboxes[f'config-C{old}'];dest=oldboxes[f'config-C{new}']
        dx,dy=dest['x']-origin['x'],dest['y']-origin['y']
        prefix=f'config-C{old}';badge=f'reg-badge-C{old}'
        move(prefix,dx,dy);move(badge,dx,dy)
        for t in original['texts']:
            if t['owner'] in [prefix,badge]:move(t['id'],dx,dy)
        for tag in [f'reg-badge-C{old}-text',f'badge-C{old}-text']:
            text_edit(tag,f'C{new}')
            if old!=new:width_about_center(objs[tag],49)
    text_edit('config-C7-title-0','GB')
    text_edit('config-C12-title-0','压缩公共')
    text_edit('config-C13-title-1','DMA')
    text_edit('roi-vdma-title','帧输出 DMA')

    # Horizontal mirror the five blocks; translate the text without flipping it.
    mirror=2*boxes['image-rx']['x']+boxes['image-rx']['w']
    module_badges={'lvds-rx':'badge-C4','isp':'badge-C5','frame-dma':'badge-C8'}
    for name in MIRROR_BLOCKS:
        b=boxes[name];dx=mirror-2*b['x']-b['w'];move(name,dx)
        for t in original['texts']:
            if t['owner']==name:move(t['id'],dx)
        if name in module_badges:
            tag=module_badges[name];move(tag,dx);move(tag+'-text',dx)
    for name in PIXEL_EDGES+['raw-bypass']:
        edges[name]['points']=[[mirror-x,y] for x,y in edges[name]['points']]
    move('raw-bypass-label',mirror-2*texts['raw-bypass-label']['x'])
    # Keep the old shared GB horizontal channel, with a new left ISP exit.
    isp=boxes['isp'];edges['isp-gb']['points'][0][0]=isp['x']
    edges['isp-gb']['points'][1][0]=isp['x']-16.25
    edges['isp-gb']['points'][2][0]=isp['x']-16.25
    dma=boxes['frame-dma'];path=edges['frame-f2']['points'];floor=dma['y']+dma['h']+45
    edges['frame-f2']['points']=[[dma['x']+dma['w']/2,dma['y']+dma['h']],
        [dma['x']+dma['w']/2,floor],[path[1][0],floor]]+deepcopy(path[2:])

    # Atomic ID/name/owner rewrite from the original function-to-number map.
    def remap(name):
        if name is None:return None
        return re.sub(r'^(config-C|reg-badge-C|badge-C)(\d+)(?=-|$)',
            lambda m:m[1]+str(OLD_TO_NEW[int(m[2])]),name)
    for collection in ['boxes','texts']:
        for item in model[collection]:
            old=item['id'];new=remap(old);item['id']=new
            if 'owner' in item:item['owner']=remap(item['owner'])
            if new!=old:renamed[old]=new
            el=objs[old];pr=el.find('.//p:cNvPr',NS)
            if old in renamed or old in text_changed:
                pr.set('name',new+(': '+item['text'] if collection=='texts' else ''))

    next_id=max(int(p.get('id')) for p in slide.findall('.//p:cNvPr',NS))+1
    def add_native(el,name):
        nonlocal next_id
        pr=el.find('.//p:cNvPr',NS);pr.set('id',str(next_id));pr.set('name',name)
        next_id+=1;tree.append(el)

    # Two outside devices copy the existing eMMC object and typography exactly.
    external_specs=[('image-sensor',boxes['lvds-rx']['y']+90-50,['图像传感器','LVDS 输出']),
                    ('output-processor',boxes['lvds-tx']['y'],['后级处理','LVDS 接收'])]
    external_objects=[]
    template=oldboxes['emmc-device']
    for name,y,lines in external_specs:
        dy=y-template['y'];b=deepcopy(template);b.update(id=name,y=y);model['boxes'].append(b)
        el=deepcopy(objs['emmc-device']);translate(el,dy=dy);external_objects.append((el,name))
        for i,line in enumerate(lines):
            old=f'emmc-device-t{i}';t=deepcopy(texts[old]);t.update(id=name+f'-t{i}',owner=name,text=line,y=t['y']+dy)
            model['texts'].append(t);el=deepcopy(objs[old]);translate(el,dy=dy);replace_text(el,line)
            width_about_center(el,190);external_objects.append((el,t['id']+': '+line))
    sensor_y=external_specs[0][1]+50;tx_y=external_specs[1][1]+50
    model['edges'] += [dict(id='sensor-rx',src='image-sensor',dst='lvds-rx',
        points=[[3370,sensor_y],[boxes['lvds-rx']['x']+boxes['lvds-rx']['w'],sensor_y]],
        kind='pixel',both=False,arrow=True,dash=False),
        dict(id='tx-processor',src='lvds-tx',dst='output-processor',
        points=[[boxes['lvds-tx']['x']+boxes['lvds-tx']['w'],tx_y],[3370,tx_y]],
        kind='pixel',both=False,arrow=True,dash=False)]

    # Detect crossings against the complete ordered edge set, but export only
    # the nine authorized geometries through the installed native backend.
    overlay=Diagram();overlay.edges=deepcopy(model['edges']);overlay.save(out/'path-context.svg')
    model['bridges']=overlay.bridges
    svg=E.parse(str(out/'path-context.svg'));root=svg.getroot()
    for el in list(root):
        if E.QName(el).localname=='defs':continue
        if el.get('id') not in EDIT_EDGES|NEW_EDGES:root.remove(el)
    # The new F2/ISP crossing is surrounded by ample whitespace. Give this
    # bridge a wider hump so that it stays distinguishable at whole-page scale.
    f2=root.find('{'+SVG+'}path[@id="frame-f2"]')
    x=isp['x']-16.25;y=floor
    old=f'L {x-6} {y} Q {x} {y-8} {x+6} {y}'
    new=f'L {x-11} {y} Q {x} {y-20} {x+11} {y}'
    assert old in f2.get('d');f2.set('d',f2.get('d').replace(old,new,1))
    for bridge in model['bridges']:
        if bridge['edge']=='frame-f2' and bridge['over']=='isp-gb':
            bridge.update(radius=11,control_height=20)
    svg.write(str(out/'edited-paths.svg'),encoding='utf-8',xml_declaration=True)
    subprocess.run([str(native_skill_root/'.venv/bin/python'),'-B',str(native_skill_root/'scripts/run.py'),
        '--input',str(out/'edited-paths.svg'),'--out-dir',str(out/'path-native'),
        '--aspect','source','--slide-width-in',str(12192000/914400)],check=True)
    with ZipFile(out/'path-native/diagrams.pptx') as z:path_objects=named(E.fromstring(z.read('ppt/slides/slide1.xml')))
    for name in sorted(EDIT_EDGES):
        sp=objs[name].find('p:spPr',NS);fresh=path_objects[name].find('p:spPr',NS)
        for tag in ['xfrm','custGeom']:
            old=sp.find('a:'+tag,NS);new=fresh.find('a:'+tag,NS);assert old is not None and new is not None
            sp.replace(old,deepcopy(new))  # a:ln, including dash/head/tail, is untouched.
    for name in sorted(NEW_EDGES):add_native(deepcopy(path_objects[name]),name)
    for el,name in external_objects:add_native(el,name)
    parts['ppt/slides/slide7.xml']=serial(slide)

    # Append slide and notes without reserializing any pre-existing slide/dependency.
    for source,target in [('ppt/slides/_rels/slide6.xml.rels','ppt/slides/_rels/slide7.xml.rels'),
                          ('ppt/notesSlides/_rels/notesSlide6.xml.rels','ppt/notesSlides/_rels/notesSlide7.xml.rels')]:
        rels=E.fromstring(parts[source])
        for rel in rels:rel.set('Target',rel.get('Target').replace('notesSlide6.xml','notesSlide7.xml').replace('slides/slide6.xml','slides/slide7.xml'))
        parts[target]=serial(rels)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide6.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='7'
    for sp in notes.findall('p:cSld/p:spTree/p:sp',NS):
        if sp.find('p:nvSpPr/p:nvPr/p:ph[@type="body"]',NS) is None:continue
        body=sp.find('p:txBody',NS)
        for para in body.findall('a:p',NS):body.remove(para)
        para=E.SubElement(body,'{'+NS['a']+'}p');run=E.SubElement(para,'{'+NS['a']+'}r')
        E.SubElement(run,'{'+NS['a']+'}t').text='第7页：从含F3虚线补修的第6页原生复制。C1～C16按功能重排并同步模块标记；旧公共控制C12变为C14。图像采集区左右镜像，文字正常；RAW仍绕过ISP。新增片外图像传感器→LVDS RX、LVDS TX→后级处理的橙色实线数据连接。帧输出DMA仍为二维AXI读。保持F1/F2/F3深蓝双向虚线、ISP↔GB绿色双向虚线、F0及四条下游DDR双向实线。前六页、主题、母版、布局与依赖原样保留。配置编号不是寄存器地址；未改RTL；Office未实测。'
    parts['ppt/notesSlides/notesSlide7.xml']=serial(notes)
    rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rid='rId'+str(max(int(r.get('Id')[3:]) for r in rels)+1)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide7.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(e.get('id')) for e in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serial(pres);parts['ppt/_rels/presentation.xml.rels']=serial(rels)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for path,kind in [('slides/slide7.xml','slide'),('notesSlides/notesSlide7.xml','notesSlide')]:
        E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+path,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serial(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='7'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='7'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector')
    E.SubElement(titles,'{'+VT+'}lpstr').text='SoC硬件层：功能配置重排 / 片外LVDS连接';titles.set('size',str(len(titles)))
    parts['docProps/app.xml']=serial(app)
    with ZipFile(out/'soc_landscape_m5_gb.pptx','w',ZIP_DEFLATED) as z:
        for n,raw in parts.items():z.writestr(n,raw)
    (out/'slide-07.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    (out/'edit_report.json').write_text(json.dumps(dict(source_page=6,pages=7,input_sha256=EXPECTED,
        new_to_old=NEW_TO_OLD,moved=sorted(moved),renamed=renamed,text_changed=sorted(text_changed),
        edited_paths=sorted(EDIT_EDGES),new_paths=sorted(NEW_EDGES),office_tested=False),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--native-skill-root',type=Path,required=True);a=p.parse_args();build(a.input,a.out_dir,a.native_skill_root)
