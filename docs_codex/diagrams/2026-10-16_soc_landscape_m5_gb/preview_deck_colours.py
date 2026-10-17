#!/usr/bin/env python3
"""Local SVG inspection of this deck's explicit DrawingML shapes, not Office rendering.

Supports the ungrouped rect/ellipse/line/custom-path subset found in the supplied
deck. The PPTX remains authoritative for fonts, theme and text layout.
"""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from PIL import ImageFont
from revise_page4_layout import resolve_colour

NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
SVG='http://www.w3.org/2000/svg'
FONT='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'


def preview(deck, out):
    out.mkdir(parents=True,exist_ok=False)
    reports=[]
    with ZipFile(deck) as z:
        pres=E.fromstring(z.read('ppt/presentation.xml'))
        size=pres.find('p:sldSz',NS); scale=int(size.get('cx'))/3600
        height=int(size.get('cy'))/scale
        theme=E.fromstring(z.read('ppt/theme/theme1.xml'))
        colors={E.QName(n).localname:'#'+n[0].get('lastClr',n[0].get('val'))
                for n in theme.find('a:themeElements/a:clrScheme',NS)}
        colors.update(bg1=colors['lt1'],tx1=colors['dk1'])

        def color(node, fallback='none'):
            if node is None:return fallback
            if node.find('a:noFill',NS) is not None:return 'none'
            fill=node.find('a:solidFill',NS)
            if fill is None:return fallback
            c=fill[0]
            return resolve_colour(fill,{k:v.removeprefix('#') for k,v in colors.items()})

        for slide_index in range(1,len(pres.find('p:sldIdLst',NS))+1):
            root=E.Element('{'+SVG+'}svg',nsmap={None:SVG},width='3600',height=str(height),viewBox=f'0 0 3600 {height}')
            def add(tag,**attrs):
                return E.SubElement(root,'{'+SVG+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
            defs=add('defs'); marker_colors=set()
            def marker(c):
                key='arrow'+c[1:]
                if c not in marker_colors:
                    m=E.SubElement(defs,'{'+SVG+'}marker',id=key,markerUnits='strokeWidth',markerWidth='3',markerHeight='3',viewBox='0 0 3 3',refX='3',refY='1.5',orient='auto-start-reverse')
                    E.SubElement(m,'{'+SVG+'}polygon',points='0,0 3,1.5 0,3',fill=c)
                    marker_colors.add(c)
                return 'url(#'+key+')'
            add('rect',id='canvas',x=0,y=0,width=3600,height=height,fill='#FFFFFF',stroke='none')
            slide=E.fromstring(z.read(f'ppt/slides/slide{slide_index}.xml'))
            texts=[]; shapes=[]
            for el in slide.find('p:cSld/p:spTree',NS):
                kind=E.QName(el).localname
                if kind in ['nvGrpSpPr','grpSpPr']:continue
                assert kind in ['sp','cxnSp'],kind
                pr=el.find('.//p:cNvPr',NS);name=pr.get('name');id=pr.get('id')
                sp=el.find('p:spPr',NS); xf=sp.find('a:xfrm',NS)
                assert xf is not None and not xf.get('rot')
                off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
                x,y=float(off.get('x'))/scale,float(off.get('y'))/scale
                w,h=float(ext.get('cx'))/scale,float(ext.get('cy'))/scale
                flipx=xf.get('flipH')=='1';flipy=xf.get('flipV')=='1'
                def point(px,py):return (x+(w-px if flipx else px),y+(h-py if flipy else py))
                ln=sp.find('a:ln',NS);stroke=color(ln)
                sw=float(ln.get('w','12700'))/scale if ln is not None else 0
                attrs={'id':'shape-'+id,'fill':color(sp),'stroke':stroke,'stroke_width':sw,'stroke_linejoin':'miter'}
                if ln is not None and stroke!='none':
                    dash=ln.find('a:custDash',NS)
                    if dash is not None:attrs['stroke_dasharray']=' '.join(str(float(n.get(k))/100000*sw) for n in dash for k in ['d','sp'])
                    for key,svgkey in [('headEnd','marker_start'),('tailEnd','marker_end')]:
                        end=ln.find('a:'+key,NS)
                        if end is not None and end.get('type','none')!='none':
                            assert end.get('type')=='triangle'
                            attrs[svgkey]=marker(stroke)
                geom=sp.find('a:prstGeom',NS)
                if geom is not None:
                    g=geom.get('prst')
                    if g=='rect':add('rect',x=x,y=y,width=w,height=h,**attrs)
                    elif g=='ellipse':add('ellipse',cx=x+w/2,cy=y+h/2,rx=w/2,ry=h/2,**attrs)
                    elif g=='line':
                        p1=point(0,0);p2=point(w,h)
                        add('line',x1=p1[0],y1=p1[1],x2=p2[0],y2=p2[1],**attrs)
                    else:raise ValueError(g)
                else:
                    paths=sp.findall('a:custGeom/a:pathLst/a:path',NS);assert len(paths)==1
                    path=paths[0];sx=w/float(path.get('w'));sy=h/float(path.get('h'));commands=[]
                    for cmd in path:
                        op={'moveTo':'M','lnTo':'L','cubicBezTo':'C','quadBezTo':'Q','close':'Z'}[E.QName(cmd).localname]
                        coords=[point(float(p.get('x'))*sx,float(p.get('y'))*sy) for p in cmd]
                        commands.append(op+' '+' '.join(f'{a:.4f} {b:.4f}' for a,b in coords))
                    add('path',d=' '.join(commands),**attrs)
                shapes.append({'id':id,'name':name,'box':[x,y,w,h]})
                body=el.find('p:txBody',NS)
                if body is None:continue
                bp=body.find('a:bodyPr',NS); paras=body.findall('a:p',NS)
                lines=[]
                for para in paras:
                    txt=''.join(para.xpath('.//a:t/text()',namespaces=NS))
                    if not txt:continue
                    rp=para.find('a:r/a:rPr',NS)
                    if rp is None:rp=para.find('a:pPr/a:defRPr',NS)
                    fs=float(rp.get('sz','800'))/100*12700/scale
                    fill=color(rp,'#29292D');bold=rp.get('b')=='1'
                    pp=para.find('a:pPr',NS);align=pp.get('algn','l') if pp is not None else 'l'
                    left=float(bp.get('lIns','91440'))/scale;right=float(bp.get('rIns','91440'))/scale
                    f=ImageFont.truetype(FONT,max(1,round(fs*10)))
                    def width(t):return f.getlength(t)/10
                    chunks=['']
                    for c in txt:
                        if bp.get('wrap')!='none' and width(chunks[-1]+c)>w-left-right and chunks[-1]:chunks.append('')
                        chunks[-1]+=c
                    for chunk in chunks:lines.append((chunk,fs,fill,bold,align,left,right,width(chunk)))
                top=float(bp.get('tIns','45720'))/scale;bottom=float(bp.get('bIns','45720'))/scale
                total=sum(t[1]*1.2 for t in lines)
                ty=y+top
                if bp.get('anchor')=='ctr':ty=y+top+(h-top-bottom-total)/2
                elif bp.get('anchor')=='b':ty=y+h-bottom-total
                for n,(txt,fs,fill,bold,align,left,right,tw) in enumerate(lines):
                    tx={'ctr':x+left+(w-left-right)/2,'r':x+w-right}.get(align,x+left)
                    anchor={'ctr':'middle','r':'end'}.get(align,'start')
                    baseline=ty+fs*.94
                    te=add('text',id=f'text-{id}-{n}',x=tx,y=baseline,font_family='WenQuanYi Zen Hei',font_size=fs,font_weight='bold' if bold else 'normal',fill=fill,text_anchor=anchor)
                    te.text=txt
                    ink_font=ImageFont.truetype(FONT,max(1,round(fs*10)))
                    il,it,ir,ib=[v/10 for v in ink_font.getbbox(txt,anchor='ls')]
                    left=tx-({'middle':tw/2,'end':tw}.get(anchor,0))
                    texts.append({'shape_id':id,'text':txt,'box':[left+il,baseline+it,ir-il,ib-it]})
                    ty+=fs*1.2
            E.ElementTree(root).write(str(out/f'slide-{slide_index:02d}.svg'),encoding='utf-8',xml_declaration=True,pretty_print=True)
            reports.append({'slide':slide_index,'shapes':shapes,'texts':texts})
    (out/'preview_layout.json').write_text(json.dumps({'renderer':'explicit DrawingML subset; font/layout approximation, not Office','slides':reports},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--deck',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args();preview(a.deck,a.out_dir)
