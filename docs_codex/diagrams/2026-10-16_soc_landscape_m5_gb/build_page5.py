#!/usr/bin/env python3
"""Append slide 5: two configuration rows, bidirectional DDR interfaces, original title."""
import argparse,json,subprocess
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from build_page4 import Diagram
from append_uniform_page import NS,REL,R,CT,EP,VT

D=Path(__file__).resolve().parent
DY=158.09517716535433
FULL_AXI=['llc-f0','mover-f1','frame-f2','roi-f3-request']+[f'front-ddr-{i}' for i in range(4)]

def make():
    model=json.loads((D/'evidence/page4-controls-build-04/slide-04.json').read_text())
    d=Diagram()
    for key in ['regions','boxes','texts','edges','dots']:setattr(d,key,deepcopy(model[key]))
    boxes={b['id']:b for b in d.boxes+d.regions};texts={t['id']:t for t in d.texts};edges={e['id']:e for e in d.edges}
    def move_object(id,dx=0,dy=0):
        b=boxes[id];b['x']+=dx;b['y']+=dy
        for t in d.texts:
            if t['owner']==id:t['x']+=dx;t['y']+=dy

    # Preserve the twenty Regbus endpoints and their fonts; compact only vertical spacing.
    ids=[['bootrom','clint','soc-regs','plic','llc-regs'],['uart','i2c','spi','gpio','slink-regs'],['vga-regs','usb-regs','err-vga','err-dma','err-cpu'],['irq-router','axi-rt-config','clic','reg-error','reg-ext']]
    shifts={}
    for row,group in enumerate(ids):
        delta=(1210+row*88)-(1230+row*100)
        for id in group:
            move_object(id,dy=delta)
            e=edges[id+'-cfg'];e['points']=[[x,y+delta] for x,y in e['points']]
        shifts[1269+row*100]=delta
    for col in range(5):edges[f'reg-column-{col}']['points'][-1][1]=1513
    boxes['reg-region']['h']=447  # bottom 1562, above the configuration trunk.
    d.dots[:]=[(x,y+shifts[y],k) for x,y,k in d.dots if y in shifts]

    # Eight groups per row under Regbus; second-row bottom equals the PLL bottom.
    width=(1680-7*14)/8
    for i in range(1,17):
        row=(i-1)//8;col=(i-1)%8;x=71.25+col*(width+14);y=[1587.1,1721.1][row]
        b=boxes[f'config-C{i}'];b.update(x=x,y=y,w=width,h=106)
        tag=boxes[f'reg-badge-C{i}'];move_object(tag['id'],x+7-tag['x'],y+5-tag['y'])
        labels=[t for t in d.texts if t['owner']==b['id']]
        for j,t in enumerate(labels):t['x']=x+width/2;t['y']=y+([65,97][j] if len(labels)==2 else 81)
    d.edges[:]=[e for e in d.edges if e['id'] not in {'regext-config','config-trunk'} and not e['id'].startswith('cfg-C')]
    d.edge('regext-config','reg-ext','config-spine',[(1726.25,1513),(1785,1513),(1785,1703.1)],'cfg',arrow=False)
    for row,trunk in enumerate([1569,1703.1]):
        d.edge(f'config-trunk-{row+1}','config-spine',f'config-row-{row+1}',[(1785,trunk),(71.25+width/2,trunk)],'cfg',arrow=False)
        d.dot(1785,trunk,'cfg')
        for col in range(8):
            i=1+row*8+col;b=boxes[f'config-C{i}'];x=b['x']+b['w']/2
            d.edge(f'cfg-C{i}',f'config-row-{row+1}',b['id'],[(x,trunk),(x,b['y'])],'cfg');d.dot(x,trunk,'cfg')
    for id in FULL_AXI:edges[id]['both']=True

    # Separate the two arrowheads on each short frontend-to-DDR interface.
    move_object('front-route',dy=-12)
    boxes['compression-front']['h']-=12
    boxes['metadata']['h']=50
    for t in d.texts:
        if t['owner']=='metadata':t['y']-=7.5
    for e in d.edges:
        if e['src']=='front-route':e['points'][0][1]-=12
        if e['dst']=='front-route':e['points'][-1][1]-=12
    edges['b-response']['points'][1][1]-=12
    edges['metadata-storage']['points'][0][1]=1430

    # Keep channel-flow arrows within the frontend distinct from complete interfaces.
    d.edges[:]=[e for e in d.edges if not e['id'].startswith('legend-')]
    d.texts[:]=[t for t in d.texts if not t['id'].startswith('legend-')]
    legends=[('axi-interface','data','AXI 请求 / 响应',True),('axi-request','data','AXI 请求方向',False),('gb','gb','GB 局部读写',True),('pixel','pixel','像素流',False),('cfg','cfg','配置 / 控制',False),('optional','optional','eMMC 接口',True)]
    for i,(name,kind,label,both) in enumerate(legends):
        y=710+i*61
        d.edge('legend-'+name,'legend','legend',[(3010,y),(3060,y)],kind,both=both)
        d.text('legend-'+name+'-text',3180,y+10,label,26,color=kind)
    d.text('legend-return',3160,1052,'单箭头接口：省略响应',24,color='data')
    d.text('legend-status',3160,1085,'虚线框：规划 / 可选',24,color='muted')

    # Shift the body, not its fonts or widths, to reproduce slide 3's title clearance.
    for b in d.regions+d.boxes:b['y']+=DY
    for t in d.texts:t['y']+=DY
    for e in d.edges:e['points']=[[x,y+DY] for x,y in e['points']]
    d.dots[:]=[(x,y+DY,k) for x,y,k in d.dots]
    boxes['soc-boundary']['h']=1825
    return d

def append(input,overlay,output):
    serial=lambda e:E.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS);assert len(sids)==4
    slide=E.fromstring(parts['ppt/slides/slide4.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    old={el.find('.//p:cNvPr',NS).get('name').split(': ')[0]:el for el in tree if E.QName(el).localname in ['sp','cxnSp']}
    for el in list(tree):
        if E.QName(el).localname not in ['nvGrpSpPr','grpSpPr']:tree.remove(el)
    # Copy the exact two native title objects, including their typography and theme references.
    third=E.fromstring(parts['ppt/slides/slide3.xml'])
    for el in third.findall('p:cSld/p:spTree/p:sp',NS):
        if el.find('p:nvSpPr/p:cNvPr',NS).get('id') in ['7','9']:tree.append(deepcopy(el))
    with ZipFile(overlay) as z:generated=E.fromstring(z.read('ppt/slides/slide1.xml'))
    for i,el in enumerate(generated.find('p:cSld/p:spTree',NS)):
        if E.QName(el).localname not in ['sp','cxnSp']:continue
        el=deepcopy(el);pr=el.find('.//p:cNvPr',NS);pr.set('id',str(1000+i));name=pr.get('name').split(': ')[0]
        if name in old:
            # Keep slide 4's explicit fill (and slide 3's inherited theme modifiers).
            fill=old[name].find('p:spPr/a:solidFill',NS)
            if fill is not None:
                sp=el.find('p:spPr',NS)
                for f in sp.findall('a:solidFill',NS):sp.remove(f)
                sp.insert(2,deepcopy(fill))
        tree.append(el)
    parts['ppt/slides/slide5.xml']=serial(slide)
    for source,target in [('ppt/slides/_rels/slide4.xml.rels','ppt/slides/_rels/slide5.xml.rels'),('ppt/notesSlides/_rels/notesSlide4.xml.rels','ppt/notesSlides/_rels/notesSlide5.xml.rels')]:
        rels=E.fromstring(parts[source])
        for rel in rels:rel.set('Target',rel.get('Target').replace('notesSlide4.xml','notesSlide5.xml').replace('slides/slide4.xml','slides/slide5.xml'))
        parts[target]=serial(rels)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide4.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='5'
    for sp in notes.findall('p:cSld/p:spTree/p:sp',NS):
        if sp.find('p:nvSpPr/p:nvPr/p:ph[@type="body"]',NS) is None:continue
        body=sp.find('p:txBody',NS)
        for para in body.findall('a:p',NS):body.remove(para)
        para=E.SubElement(body,'{'+NS['a']+'}p');r=E.SubElement(para,'{'+NS['a']+'}r');E.SubElement(r,'{'+NS['a']+'}t').text='第5页：F0–F3及四条下游DDR接口双向表示请求/响应；F2写入的反向是B响应，F3读取的反向是R数据，不改变发起者。C1–C8/C9–C16位于Regbus下方两行；恢复第3页原生标题，正文下移，不缩小字体。仅图稿规划，未修改RTL或冻结接口参数。'
    parts['ppt/notesSlides/notesSlide5.xml']=serial(notes)
    rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rid='rId'+str(max(int(r.get('Id')[3:]) for r in rels)+1)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide5.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(e.get('id')) for e in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serial(pres);parts['ppt/_rels/presentation.xml.rels']=serial(rels)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for path,kind in [('slides/slide5.xml','slide'),('notesSlides/notesSlide5.xml','notesSlide')]:E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+path,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serial(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='5'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='5'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector');E.SubElement(titles,'{'+VT+'}lpstr').text='SoC硬件层：双向DDR接口 / 两行扩展配置';titles.set('size',str(len(titles)));parts['docProps/app.xml']=serial(app)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for n,raw in parts.items():z.writestr(n,raw)

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True);a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=False)
    d=make();svg=a.out_dir/'slide-05.svg';d.save(svg)
    subprocess.run(['python3','-B',str(a.native_skill_root/'scripts/run.py'),'--input',str(svg),'--out-dir',str(a.out_dir/'native'),'--aspect','source','--slide-width-in',str(12192000/914400),'--font','Microsoft YaHei','--font-file','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'],check=True)
    append(a.input,a.out_dir/'native/diagrams.pptx',a.out_dir/'soc_landscape_m5_gb.pptx')
    (a.out_dir/'edit_report.json').write_text(json.dumps({'pages':5,'shift_y':DY,'title_copied_from_slide':3,'title_shape_ids':[7,9],'full_axi_interfaces':FULL_AXI,'config_rows':[list(range(1,9)),list(range(9,17))],'font_sizes_unchanged':True,'office_tested':False},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
