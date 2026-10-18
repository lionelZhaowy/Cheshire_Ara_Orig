#!/usr/bin/env python3
"""Rasterize SVG masters or locally render this skill's final native PPTX objects.
PPTX mode reads DrawingML, not master SVG; it is not an Office renderer.
Requires cairosvg. Unsupported PPTX geometry/text fails explicitly.
"""
import argparse,html,json,zipfile,posixpath
from pathlib import Path
from xml.etree import ElementTree as E
import cairosvg
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def q(n):p,l=n.split(':');return '{'+N[p]+'}'+l
def color(node,default='none'):
 if node is None:return default
 c=node.find('a:solidFill/a:srgbClr',N)
 return '#'+c.get('val') if c is not None else default
def ppt_svg(package,slide_path,width,height):
 root=E.fromstring(package.read(slide_path));scale=1600/width;H=height*scale;items=[];defs=[];count=0
 items.append(f'<rect width="1600" height="{H}" fill="#FFFFFF"/>')
 for node in root.find('p:cSld/p:spTree',N):
  if node.tag in (q('p:nvGrpSpPr'),q('p:grpSpPr')):continue
  assert node.tag in (q('p:sp'),q('p:cxnSp')),node.tag
  sp=node.find('p:spPr',N);xf=sp.find('a:xfrm',N);assert xf is not None
  off=xf.find('a:off',N);ext=xf.find('a:ext',N)
  x,y,w,h=[float(t)*scale for t in [off.get('x'),off.get('y'),ext.get('cx'),ext.get('cy')]]
  assert xf.get('rot','0')=='0'
  txt=node.find('p:txBody',N)
  if txt is not None and txt.findall('.//a:t',N):
   paras=txt.findall('a:p',N);assert len(paras)==1
   runs=paras[0].findall('a:r',N);assert len(runs)==1
   run=runs[0];s=run.find('a:t',N).text;rp=run.find('a:rPr',N)
   size=float(rp.get('sz'))/100*12700*scale
   pp=paras[0].find('a:pPr',N);align=pp.get('algn','l')
   anchor={'l':'start','ctr':'middle','r':'end'}[align];xx=x+{'l':0,'ctr':w/2,'r':w}[align]
   items.append(f'<text x="{xx}" y="{y+1.08*size}" font-family="Microsoft YaHei" font-size="{size}" font-weight="{"bold" if rp.get("b")=="1" else "normal"}" fill="{color(rp)}" text-anchor="{anchor}">{html.escape(s)}</text>');count+=1;continue
  ln=sp.find('a:ln',N);sw=float(ln.get('w','0'))*scale if ln is not None else 0;stroke=color(ln);fill=color(sp)
  attrs=f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'
  if ln is not None:
   dash=ln.find('a:custDash',N)
   if dash is not None:
    vals=[]
    for ds in dash:vals.extend(float(ds.get(k))/100000*sw for k in ['d','sp'])
    attrs+=' stroke-dasharray="'+' '.join(str(v) for v in vals)+'"'
   for end,mark in [('headEnd','start'),('tailEnd','end')]:
    en=ln.find('a:'+end,N)
    if en is not None and en.get('type')=='triangle':
     mid=f'm{count}{mark}';defs.append(f'<marker id="{mid}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{stroke}"/></marker>');attrs+=f' marker-{mark}="url(#{mid})"'
  if node.tag==q('p:cxnSp'):
   x1,x2=(x+w,x) if xf.get('flipH')=='1' else (x,x+w)
   y1,y2=(y+h,y) if xf.get('flipV')=='1' else (y,y+h)
   items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {attrs}/>')
  elif sp.find('a:custGeom',N) is not None:
   paths=sp.findall('a:custGeom/a:pathLst/a:path',N);assert len(paths)==1
   path=paths[0];pw,ph=float(path.get('w')),float(path.get('h'));d=[]
   for cmd in path:
    tag=cmd.tag.split('}')[1];op={'moveTo':'M','lnTo':'L','cubicBezTo':'C','close':'Z'}[tag]
    coords=' '.join(f'{x+float(pt.get("x"))/pw*w},{y+float(pt.get("y"))/ph*h}' for pt in cmd)
    d.append(op+' '+coords)
   items.append('<path d="'+' '.join(d)+f'" {attrs}/>')
  else:
   geom=sp.find('a:prstGeom',N);typ=geom.get('prst');assert typ in ('rect','roundRect')
   rx=0
   if typ=='roundRect':
    gd=geom.find('a:avLst/a:gd',N);adj=float(gd.get('fmla').split()[-1])/100000;rx=min(w,h)*adj
   items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {attrs}/>')
  count+=1
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="'+str(H)+'" viewBox="0 0 1600 '+str(H)+'"><defs>'+''.join(defs)+'</defs>'+''.join(items)+'</svg>',count

def raster(s,out):cairosvg.svg2png(bytestring=s.encode(),write_to=str(out))
def crops(s,d,name):
 # All complex areas: full-width detail strips retain exact vector geometry.
 for label,(x,y,w,h) in {'upper':(20,135,1560,290),'lower':(20,425,1560,400)}.items():
  root=E.fromstring(s);root.set('width',str(w));root.set('height',str(h));root.set('viewBox',f'{x} {y} {w} {h}')
  cairosvg.svg2png(bytestring=E.tostring(root),write_to=str(d/f'{name}-{label}.png'))
if __name__=='__main__':
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--svg-dir',type=Path);g.add_argument('--pptx',type=Path);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--crops',action='store_true');a=ap.parse_args();a.out_dir.mkdir(parents=True,exist_ok=False)
 if a.svg_dir:
  for p in sorted(a.svg_dir.glob('*.svg')):
   s=p.read_text();raster(s,a.out_dir/(p.stem+'.png'))
   if a.crops:crops(s,a.out_dir,p.stem)
 else:
  with zipfile.ZipFile(a.pptx) as z:
   pres=E.fromstring(z.read('ppt/presentation.xml'));sz=pres.find('p:sldSz',N);rels=E.fromstring(z.read('ppt/_rels/presentation.xml.rels'));mapping={r.get('Id'):r.get('Target') for r in rels};reports=[]
   for i,sld in enumerate(pres.find('p:sldIdLst',N),1):
    target=posixpath.normpath(posixpath.join('ppt',mapping[sld.get(q('r:id'))]));s,count=ppt_svg(z,target,float(sz.get('cx')),float(sz.get('cy')));name=f'slide-{i:02d}'
    (a.out_dir/(name+'.svg')).write_text(s);raster(s,a.out_dir/(name+'.png'))
    if a.crops:crops(s,a.out_dir,name)
    reports.append({'page':i,'part':target,'native_objects_rendered':count})
   (a.out_dir/'render-report.json').write_text(json.dumps({'source':str(a.pptx),'method':'local DrawingML subset, not Office','pages':reports},indent=2)+'\n')
 print('Rendered',a.out_dir)
