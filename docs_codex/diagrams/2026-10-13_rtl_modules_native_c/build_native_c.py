"""Native skill style experiment. Preserve every verified A wire and text.

Run with the existing publication-figures venv (CairoSVG/Pillow).
This script never generates B or changes A/chapter content.
"""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
import hashlib, json
import cairosvg

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / '2026-10-13_rtl_module_comparison'
REPO = ROOT.parents[2]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
def tag(s): return '{'+NS+'}'+s
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rectbox(e): return tuple(float(e.get(k, '0')) for k in ['x','y','width','height'])
def inside(a,b):
    x,y,w,h=a; X,Y,W,H=b
    return x>=X and y>=Y and x+w<=X+W and y+h<=Y+H

# A fill families are retained; palette is presentation, not a new RTL taxonomy.
PALETTE = {
    '#EAF1F8': ('#346DA6','#EFF6FD'),
    '#E8F2EA': ('#317E69','#EFF8F3'),
    '#EDF5EB': ('#317E69','#EFF8F3'),
    '#F2EEF8': ('#7552A1','#F6F1FB'),
    '#FFF0DB': ('#966017','#FFF8EB'),
    '#E8F2F0': ('#287E7A','#EFF9F7'),
    '#FBEDE5': ('#9C5443','#FFF4EF'),
}
def render(src, out):
    root=ET.parse(src).getroot()
    children=list(root)
    rects=[e for e in children if e.tag==tag('rect')]
    texts=[e for e in children if e.tag==tag('text')]
    modules=[]
    for e in rects:
        x,y,w,h=rectbox(e)
        if w<110 or h<55 or (x==0 and y==0): continue
        nested=[r for r in rects if r is not e and rectbox(r)[2]>100 and rectbox(r)[3]>55 and inside(rectbox(r),rectbox(e))]
        if nested:
            e.set('fill','#F8FAFD'); e.set('stroke','#A6B5C8'); e.set('rx','12')
            continue
        contained=[t for t in texts if x<float(t.get('x','0'))<x+w and y<float(t.get('y','0'))<y+h]
        if not contained: continue
        head=min(contained,key=lambda t:float(t.get('y')))
        color,fill=PALETTE.get(e.get('fill'),('#526A87','#F1F5FA'))
        e.set('fill',fill); e.set('stroke',color); e.set('stroke-width','1.8'); e.set('rx','8')
        height=float(head.get('y'))-y+10
        if len(contained)>1 and height<h*.72:
            # One inset band; does not alter the outer dashed planned boundary.
            band=ET.Element(tag('rect'),{'x':str(x+3),'y':str(y+3),'width':str(w-6),'height':str(height-3),'fill':color,'stroke':'none','rx':'5'})
            root.insert(list(root).index(e)+1,band)
            head.set('fill','#FFFFFF')
        else:
            head.set('fill',color)
        modules.append({'box':rectbox(e),'header':head.text,'color':color})
    for e in texts:
        if float(e.get('font-size','0'))>=30:
            e.set('fill','#214E79')
        if e.text and e.text.endswith('A：连续走线。'):
            e.text=e.text.replace('A：连续走线。','C：连续走线。')
    for e in root.iter(tag('polyline')):
        if e.get('id','').startswith('E'): e.set('stroke-width','2.8')
    ET.indent(root)
    ET.ElementTree(root).write(out,encoding='unicode')
    cairosvg.svg2png(url=str(out),write_to=str(out.with_suffix('.png')))
    cairosvg.svg2pdf(url=str(out),write_to=str(out.with_suffix('.pdf')))
    return modules

def gallery(graphs):
    ap='../'+BASE.name+'/A/'
    css='body{font:17px/1.65 system-ui,sans-serif;color:#23354b;background:#f3f6fa;margin:0}header,main{max-width:1750px;margin:auto;padding:24px}section,header{background:white}section{padding:24px;margin:24px 0;border:1px solid #ccd7e4}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}.wide .pair{grid-template-columns:1fr}figure{margin:0}img{width:100%;height:auto}a{color:#235e98}button,select{font:inherit;padding:6px 12px}nav{display:flex;gap:20px;flex-wrap:wrap}table{border-collapse:collapse;width:100%;font-size:15px}td,th{border:1px solid #ccd7e4;padding:8px;text-align:left;vertical-align:top}summary{cursor:pointer}@media(max-width:1000px){.pair{grid-template-columns:1fr}}'
    out=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RTL 模块图 A / C 连续走线比较</title><style>'+css+'</style><header><h1>A / C：连续走线，两种视觉表达</h1><p>用户比较 C 后已确认继续采用 A，后续补图与修订沿用 A；C 仅保留试绘记录。C 使用 svg-pptx-diagrams-native 的协调配色、模块标题带、浅色主体与柔和边框；复用 A 的布局、全文和全部真实连线，便于直接比较。E 编号只辅助查信号，不替代连线。</p><p>B 端口配对版已按用户意见弃用，不再展示为候选，也不再生成。历史产物仅留档。颜色不定义新协议或时钟域，仍以图中文字及连接表为准。</p><nav><a href="../../rtl_modules/README.md">模块指南</a><a href="C/editable/diagrams.pptx">C 原生 PPTX</a><a href="'+ap+'editable/diagrams.pptx">A 原生 PPTX</a><a href="README.md">图源与检查说明</a><button id="layout">切换并排 / 上下</button></nav><p><select id="jump"><option value="">跳转模块…</option>']
    out += [f'<option value="{g["name"]}">{escape(g["title"])}</option>' for g in graphs]
    out.append('</select></p></header><main>')
    for g in graphs:
        n=g['name'];nodes={v['id']:v for v in g['nodes']}
        out.append(f'<section id="{n}"><h2>{escape(g["title"])}</h2><a href="../../rtl_modules/{g["doc"]}">详细解读与源码对应</a><div class="pair">')
        for label,prefix in [('A · 当前采用',ap),('C · 试绘留档','C/')]:
            out.append(f'<figure><figcaption>{label} · <a href="{prefix}{n}.svg">SVG</a> · <a href="{prefix}{n}.pdf">PDF</a></figcaption><a href="{prefix}{n}.png"><img loading="lazy" src="{prefix}{n}.png" alt="{escape(g["title"])} {label}"></a></figure>')
        out.append('</div><details><summary>展开共用连接表（E 编号 → 信号与用途）</summary><table><tr><th>连线</th><th>端点</th><th>信号与含义</th></tr>')
        for e in g['edges']:
            relation=nodes[e['source']]['lines'][0]+(' ↔ ' if e.get('both') else ' → ')+nodes[e['target']]['lines'][0]
            out.append(f'<tr><td>{e["id"]}</td><td>{escape(relation)}</td><td>{escape(e.get("detail",e.get("label","")))}</td></tr>')
        out.append('</table></details></section>')
    out.append('</main><script>document.getElementById("layout").onclick=()=>document.body.classList.toggle("wide");document.getElementById("jump").onchange=e=>{if(e.target.value)location.hash=e.target.value};</script></html>')
    (ROOT/'index.html').write_text('\n'.join(out))

def main():
    manifest=json.loads((BASE/'source_manifest.json').read_text())
    for name,digest in manifest['source_sha256'].items():
        assert sha(REPO/name)==digest, ('source drift', name)
    (ROOT/'C').mkdir(exist_ok=True)
    inventory=[]
    for src in sorted((BASE/'A').glob('*.svg')):
        out=ROOT/'C'/src.name
        modules=render(src,out)
        inventory.append({'name':src.stem,'A_sha256':sha(src),'C_sha256':sha(out),'png_sha256':sha(out.with_suffix('.png')),'styled_modules':modules})
    graphs=json.loads((BASE/'connections.json').read_text())
    (ROOT/'connections.json').write_text(json.dumps(graphs,ensure_ascii=False,indent=2))
    (ROOT/'render_manifest.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
    gallery(graphs['figures'])
    print('Rendered',len(inventory),'continuous-wire C figures; copied verified connection inventory.')

if __name__=='__main__': main()
