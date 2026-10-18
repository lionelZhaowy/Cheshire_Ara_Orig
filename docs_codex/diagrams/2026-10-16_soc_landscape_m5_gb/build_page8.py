#!/usr/bin/env python3
"""Clone the user's saved page 7 and change five native path geometries only."""
import argparse,hashlib,json,subprocess
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from append_uniform_page import NS,REL,R,CT,EP,VT
from build_page6 import named

D=Path(__file__).resolve().parent
SCALE=12192000/3600
SVG='http://www.w3.org/2000/svg'
EXPECTED='8916ac316a5d9244297545fe6a6dc751de79851fa4f21a1757ea295771453b1b'
EDITED={'mover-f1','frame-f2','isp-gb','emmc-physical','m5-gb'}
serial=lambda e:E.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)

def box(el):
    xf=el.find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
    return [int(v)/SCALE for v in [off.get('x'),off.get('y'),ext.get('cx'),ext.get('cy')]]

def commands(el):
    x,y,w,h=box(el);xf=el.find('p:spPr/a:xfrm',NS)
    assert not xf.get('rot') and not xf.get('flipH') and not xf.get('flipV')
    p=el.find('p:spPr/a:custGeom/a:pathLst/a:path',NS);assert p is not None
    return [(E.QName(c).localname,[[x+int(v.get('x'))/int(p.get('w'))*w,y+int(v.get('y'))/int(p.get('h'))*h] for v in c]) for c in p]

def route_spec(objs):
    """All anchors are measured from current PPT objects, not an old JSON page."""
    b={n:box(e) for n,e in objs.items()}
    centre_top=lambda name:[b[name][0]+b[name][2]/2,b[name][1]]
    mover=b['gb-mover'];old_f2=commands(objs['frame-f2']);old_m5=commands(objs['m5-gb'])
    f2_start=old_f2[0][1][0];f2_y=f2_start[1]+30
    f1_start=[mover[0]+mover[2],mover[1]+mover[3]-20]
    f1_end=centre_top('front-F1');f2_end=centre_top('front-F2')
    gb=b['gb-interface'];device=centre_top('emmc-device');host=centre_top('emmc-host')
    assert abs(device[1]-host[1])<.01
    # The preserved M5 right corridor and upper return are taken from its native
    # final vertices; earlier curved commands belong to the M_EXT crossing.
    m5_tail=[old_m5[-4][1][-1],old_m5[-3][1][-1],old_m5[-2][1][-1],old_m5[-1][1][-1]]
    assert abs(m5_tail[0][0]-2945)<.01 and abs(m5_tail[1][1]-678.095)<.01
    target6=commands(objs['target-6']);cross_x=target6[0][1][0][0]
    specs={
        'mover-f1':dict(src='gb-mover',dst='front-F1',points=[f1_start,[2975,f1_start[1]],[2975,1228.095],[f1_end[0],1228.095],f1_end]),
        'frame-f2':dict(src='frame-dma',dst='front-F2',points=[f2_start,[f2_start[0],f2_y],[3005,f2_y],[3005,1245.095],[f2_end[0],1245.095],f2_end]),
        'isp-gb':dict(src='isp',dst='gb-adapter',points=[c[1][0] for c in commands(objs['isp-gb'])]),
        'emmc-physical':dict(src='emmc-device',dst='emmc-host',points=[device,[device[0],device[1]-25],[host[0],host[1]-25],host]),
        'm5-gb':dict(src='gb-interface',dst='gb-adapter',points=[[gb[0]+gb[2]-25,gb[1]],[gb[0]+gb[2]-25,m5_tail[0][1]]]+m5_tail),
    }
    isp_x=specs['isp-gb']['points'][1][0];emmc_y=device[1]-25;m5_x=m5_tail[0][0]
    bridges=[
        dict(edge='isp-gb',over='frame-f2',at=[isp_x,f2_y],direction='right'),
        dict(edge='isp-gb',over='mover-f1',at=[isp_x,f1_start[1]],direction='right'),
        dict(edge='emmc-physical',over='m5-gb',at=[m5_x,emmc_y],direction='down'),
        dict(edge='emmc-physical',over='mover-f1',at=[2975,emmc_y],direction='down'),
        dict(edge='emmc-physical',over='frame-f2',at=[3005,emmc_y],direction='down'),
        dict(edge='m5-gb',over='target-6',at=[cross_x,m5_tail[0][1]],direction='up'),
    ]
    for bridge in bridges:bridge.update(radius=8,control_height=16)
    return specs,bridges

def route_d(spec,bridges):
    pts=spec['points'];result=f'M {pts[0][0]} {pts[0][1]}';used=[]
    for a,b in zip(pts,pts[1:]):
        horizontal=abs(a[1]-b[1])<.001
        assert horizontal or abs(a[0]-b[0])<.001,(a,b)
        axis=0 if horizontal else 1;sgn=1 if b[axis]>a[axis] else -1
        hits=[j for j in bridges if abs(j['at'][1-axis]-a[1-axis])<.001 and min(a[axis],b[axis])<j['at'][axis]<max(a[axis],b[axis])]
        for j in sorted(hits,key=lambda j:sgn*j['at'][axis]):
            x,y=j['at'];r=j['radius'];h=j['control_height'];used.append(j)
            assert min(abs(j['at'][axis]-a[axis]),abs(j['at'][axis]-b[axis]))>r
            if horizontal:
                assert j['direction'] in ['up','down'];dy=h if j['direction']=='down' else -h
                result+=f' L {x-sgn*r} {y} Q {x} {y+dy} {x+sgn*r} {y}'
            else:
                assert j['direction']=='right';result+=f' L {x} {y-sgn*r} Q {x+h} {y} {x} {y+sgn*r}'
        result+=f' L {b[0]} {b[1]}'
    assert len(used)==len(bridges)
    return result

def append_slide(parts,slide):
    parts['ppt/slides/slide8.xml']=serial(slide)
    for source,target in [('ppt/slides/_rels/slide7.xml.rels','ppt/slides/_rels/slide8.xml.rels'),('ppt/notesSlides/_rels/notesSlide7.xml.rels','ppt/notesSlides/_rels/notesSlide8.xml.rels')]:
        rels=E.fromstring(parts[source])
        for rel in rels:rel.set('Target',rel.get('Target').replace('notesSlide7.xml','notesSlide8.xml').replace('slides/slide7.xml','slides/slide8.xml'))
        parts[target]=serial(rels)
    notes=E.fromstring(parts['ppt/notesSlides/notesSlide7.xml'])
    for field in notes.xpath('//a:fld[@type="slidenum"]/a:t',namespaces=NS):field.text='8'
    for sp in notes.findall('p:cSld/p:spTree/p:sp',NS):
        if sp.find('p:nvSpPr/p:nvPr/p:ph[@type="body"]',NS) is None:continue
        body=sp.find('p:txBody',NS)
        for para in body.findall('a:p',NS):body.remove(para)
        para=E.SubElement(body,'{'+NS['a']+'}p');run=E.SubElement(para,'{'+NS['a']+'}r')
        E.SubElement(run,'{'+NS['a']+'}t').text='第8页：复制用户手动保存的第7页（输入SHA-256 8916ac31…），仅修改F1、F2、ISP↔GB、eMMC和M5回接五条连线的几何。F1/F2平行通道，接口仍独立；六处跳线对应实际交叉。所有原生线样式、箭头、字体、模块位置、配置编号和图例保持，前七页及依赖原字节保留。未修改RTL或协议契约；Office显示/编辑未实测。'
    parts['ppt/notesSlides/notesSlide8.xml']=serial(notes)
    pres=E.fromstring(parts['ppt/presentation.xml']);sids=pres.find('p:sldIdLst',NS);assert len(sids)==7
    rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);rid='rId'+str(max(int(r.get('Id')[3:]) for r in rels)+1)
    E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/slide',Target='slides/slide8.xml')
    E.SubElement(sids,'{'+NS['p']+'}sldId',{'id':str(max(int(e.get('id')) for e in sids)+1),'{'+R+'}id':rid})
    parts['ppt/presentation.xml']=serial(pres);parts['ppt/_rels/presentation.xml.rels']=serial(rels)
    ct=E.fromstring(parts['[Content_Types].xml'])
    for path,kind in [('slides/slide8.xml','slide'),('notesSlides/notesSlide8.xml','notesSlide')]:
        E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/'+path,ContentType='application/vnd.openxmlformats-officedocument.presentationml.'+kind+'+xml')
    parts['[Content_Types].xml']=serial(ct)
    app=E.fromstring(parts['docProps/app.xml'])
    for tag in ['Slides','Notes']:app.find('{'+EP+'}'+tag).text='8'
    app.find('{'+EP+'}HeadingPairs').findall('.//{'+VT+'}i4')[-1].text='8'
    titles=app.find('{'+EP+'}TitlesOfParts/{'+VT+'}vector');E.SubElement(titles,'{'+VT+'}lpstr').text='SoC硬件层：长线通道与六处跳线';titles.set('size',str(len(titles)))
    parts['docProps/app.xml']=serial(app)

def build(source,out,native_root):
    assert hashlib.sha256(source.read_bytes()).hexdigest()==EXPECTED,'Input changed; do not overwrite the user edit'
    out.mkdir(parents=True,exist_ok=False)
    with ZipFile(source) as z:parts={n:z.read(n) for n in z.namelist()}
    slide=E.fromstring(parts['ppt/slides/slide7.xml']);objs=named(slide);specs,bridges=route_spec(objs)
    root=E.Element('{'+SVG+'}svg',nsmap={None:SVG},width='3600',height='2025',viewBox='0 0 3600 2025')
    defs=E.SubElement(root,'{'+SVG+'}defs');colours=set()
    for name in sorted(EDITED):
        el=objs[name];ln=el.find('p:spPr/a:ln',NS);colour='#'+ln.find('a:solidFill/a:srgbClr',NS).get('val');sw=int(ln.get('w'))/SCALE
        if colour not in colours:
            m=E.SubElement(defs,'{'+SVG+'}marker',id='arr'+colour[1:],markerUnits='strokeWidth',markerWidth='3',markerHeight='3',viewBox='0 0 3 3',refX='3',refY='1.5',orient='auto-start-reverse')
            E.SubElement(m,'{'+SVG+'}polygon',points='0,0 3,1.5 0,3',fill=colour);colours.add(colour)
        attrs={'id':name,'d':route_d(specs[name],[j for j in bridges if j['edge']==name]),'fill':'none','stroke':colour,'stroke-width':str(sw),'stroke-linejoin':'miter'}
        for tag,attr in [('headEnd','marker-start'),('tailEnd','marker-end')]:
            end=ln.find('a:'+tag,NS)
            if end is not None and end.get('type')=='triangle':attrs[attr]='url(#arr'+colour[1:]+')'
        dash=ln.find('a:custDash',NS)
        if dash is not None:attrs['stroke-dasharray']=' '.join(str(int(s.get(k))/100000*sw) for s in dash for k in ['d','sp'])
        E.SubElement(root,'{'+SVG+'}path',attrs)
    E.ElementTree(root).write(str(out/'edited-paths.svg'),encoding='utf-8',xml_declaration=True)
    subprocess.run([str(native_root/'.venv/bin/python'),'-B',str(native_root/'scripts/run.py'),'--input',str(out/'edited-paths.svg'),'--out-dir',str(out/'path-native'),'--aspect','source','--slide-width-in',str(12192000/914400)],check=True)
    with ZipFile(out/'path-native/diagrams.pptx') as z:fresh=named(E.fromstring(z.read('ppt/slides/slide1.xml')))
    for name in EDITED:
        sp=objs[name].find('p:spPr',NS);newsp=fresh[name].find('p:spPr',NS)
        for tag in ['xfrm','custGeom']:
            before=sp.find('a:'+tag,NS);after=newsp.find('a:'+tag,NS);assert before is not None and after is not None
            sp.replace(before,deepcopy(after))
    append_slide(parts,slide)
    with ZipFile(out/'soc_landscape_m5_gb.pptx','w',ZIP_DEFLATED) as z:
        for name,raw in parts.items():z.writestr(name,raw)
    report=dict(input_sha256=EXPECTED,source_page=7,pages=8,geometry_source='current native PPT only',changed_geometry=sorted(EDITED),routes=specs,bridges=bridges,office_tested=False)
    (out/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--native-skill-root',type=Path,required=True)
    a=p.parse_args();build(a.input,a.out_dir,a.native_skill_root)
