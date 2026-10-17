#!/usr/bin/env python3
"""Clone native slide 5; restore five line styles and add a legend sample only."""
import argparse,json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from append_uniform_page import NS,REL,R,CT,EP,VT

D=Path(__file__).resolve().parent
SCALE=12192000/3600
RESTORE={'isp-gb':('page4','isp-gb'),'mover-f1':('page4','mover-f1'),'frame-f2':('page4','frame-f2'),'master-8':('page3','master-input-7'),'target-6':('page3','target-output-ext')}
GRAY={'master-8','target-6'}
def named(root):
    return {p.find('.//p:cNvPr',NS).get('name').split(': ')[0]:p for p in root.find('p:cSld/p:spTree',NS) if E.QName(p).localname in ['sp','cxnSp']}
def dash_from(el,source):
    ln=el.find('p:spPr/a:ln',NS)
    for tag in ['prstDash','custDash']:
        for child in ln.findall('a:'+tag,NS):ln.remove(child)
    dash=source.find('p:spPr/a:ln/a:custDash',NS);assert dash is not None
    # DrawingML: dash follows fill and precedes join / end decorations.
    ln.insert(1,deepcopy(dash))
def shift_y(el,delta):
    off=el.find('p:spPr/a:xfrm/a:off',NS);off.set('y',str(int(off.get('y'))+round(delta*SCALE)))
def rename(el,id,name):
    pr=el.find('.//p:cNvPr',NS);pr.set('id',str(id));pr.set('name',name)
def replace_text(el,value):
    ts=el.findall('.//a:t',NS);assert len(ts)==1;ts[0].text=value

def build(input,out):
    out.mkdir(parents=True,exist_ok=False)
    serial=lambda e:E.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(input) as z:parts={n:z.read(n) for n in z.namelist()}
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS);assert len(sids)==5
    slide=E.fromstring(parts['ppt/slides/slide5.xml']);tree=slide.find('p:cSld/p:spTree',NS);objs=named(slide)
    refs={'page3':named(E.fromstring(parts['ppt/slides/slide3.xml']))}
    with ZipFile(D/'evidence/page4-controls-before/soc_landscape_m5_gb.pptx') as z:refs['page4']=named(E.fromstring(z.read('ppt/slides/slide4.xml')))
    model=json.loads((D/'evidence/page5-build-02/slide-05.json').read_text());edges={e['id']:e for e in model['edges']};texts={t['id']:t for t in model['texts']}
    for name,(page,ref) in RESTORE.items():
        dash_from(objs[name],refs[page][ref]);edges[name]['dash']=True
        if name in GRAY:
            objs[name].find('p:spPr/a:ln/a:solidFill/a:srgbClr',NS).set('val','93939D');edges[name]['kind']='optional'
    # Reflow only the existing legend; body objects are copied without editing.
    legends=['axi-interface','axi-request','gb','pixel','cfg','optional']
    for i,name in enumerate(legends):
        delta=(700+i*48)-(710+i*61)
        for suffix in ['', '-text']:shift_y(objs['legend-'+name+suffix],delta)
        for pt in edges['legend-'+name]['points']:pt[1]+=delta
        texts['legend-'+name+'-text']['y']+=delta
    new_id=max(int(p.get('id')) for p in slide.findall('.//p:cNvPr',NS))+1
    line=deepcopy(objs['legend-optional']);rename(line,new_id,'legend-dashed');shift_y(line,48)
    line.find('p:spPr/a:ln',NS).remove(line.find('p:spPr/a:ln/a:headEnd',NS));dash_from(line,refs['page3']['master-input-7']);tree.append(line)
    label=deepcopy(objs['legend-optional-text']);rename(label,new_id+1,'legend-dashed-text: 虚线：规划 / 可选');shift_y(label,48);replace_text(label,'虚线：规划 / 可选');tree.append(label)
    # Widen only the new legend textbox around its original centre, retaining font.
    xf=label.find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
    cx=round(260*SCALE);centre=int(off.get('x'))+int(ext.get('cx'))/2;off.set('x',str(round(centre-cx/2)));ext.set('cx',str(cx))
    edge=deepcopy(edges['legend-optional']);edge.update(id='legend-dashed',both=False,dash=True)
    for pt in edge['points']:pt[1]+=48
    model['edges'].append(edge)
    label_model=deepcopy(texts['legend-optional-text']);label_model.update(id='legend-dashed-text',text='虚线：规划 / 可选',y=label_model['y']+48);model['texts'].append(label_model)
    replace_text(objs['legend-status'],'虚实与箭头方向独立');texts['legend-status']['text']='虚实与箭头方向独立'
    pr=objs['legend-status'].find('.//p:cNvPr',NS);pr.set('name','legend-status: 虚实与箭头方向独立')
    for name,delta in [('legend-return',1028-1052),('legend-status',1054-1085)]:
        shift_y(objs[name],delta);texts[name]['y']+=delta
    parts['ppt/slides/slide6.xml']=serial(slide)
    for source,target in [('ppt/slides/_rels/slide5.xml.rels','ppt/slides/_rels/slide6.xml.rels'),('ppt/notesSlides/_rels/notesSlide5.xml.rels','ppt/notesSlides/_rels/notesSlide6.xml.rels')]:
        rels=E.fromstring(parts[source])
        for rel in rels:rel.set('Target',rel.get('Target').replace('notesSlide5.xml','notesSlide6.xml').replace('slides/slide5.xml','slides/slide6.xml'))
        parts[target]=serial(rels)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide5.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='6'
    for sp in notes.findall('p:cSld/p:spTree/p:sp',NS):
        if sp.find('p:nvSpPr/p:nvPr/p:ph[@type="body"]',NS) is None:continue
        body=sp.find('p:txBody',NS)
        for para in body.findall('a:p',NS):body.remove(para)
        para=E.SubElement(body,'{'+NS['a']+'}p');run=E.SubElement(para,'{'+NS['a']+'}r');E.SubElement(run,'{'+NS['a']+'}t').text='第6页：用户先规划后明确授权实施。直接复制第5页，仅恢复 ISP↔GB、搬运器↔F1、帧写入DMA↔F2 的虚线，以及 S_EXT/M_EXT 外部扩展的灰色虚线；保持第5页箭头方向、几何、字号、填充、主题及两行配置/标题布局。图例新增虚线样例；虚实与箭头方向独立，沿用规划/可选标记，不代表实现或验收状态。前五页完整保留。Office未实测；无RTL修改。'
    parts['ppt/notesSlides/notesSlide6.xml']=serial(notes)
    rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rid='rId'+str(max(int(r.get('Id')[3:]) for r in rels)+1)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide6.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(e.get('id')) for e in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serial(pres);parts['ppt/_rels/presentation.xml.rels']=serial(rels)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for path,kind in [('slides/slide6.xml','slide'),('notesSlides/notesSlide6.xml','notesSlide')]:E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+path,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serial(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='6'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='6'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector');E.SubElement(titles,'{'+VT+'}lpstr').text='SoC硬件层：恢复五条虚线 / 保留双向接口';titles.set('size',str(len(titles)));parts['docProps/app.xml']=serial(app)
    with ZipFile(out/'soc_landscape_m5_gb.pptx','w',ZIP_DEFLATED) as z:
        for n,raw in parts.items():z.writestr(n,raw)
    (out/'slide-06.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    (out/'edit_report.json').write_text(json.dumps({'pages':6,'source_page':5,'restored_lines':RESTORE,'gray_lines':sorted(GRAY),'geometry_and_arrow_directions':'unchanged outside legend','office_tested':False},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args();build(a.input,a.out_dir)
