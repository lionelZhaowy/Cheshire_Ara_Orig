#!/usr/bin/env python3
"""Build a local comparison page from the figure manifest."""
from html import escape
import json
from pathlib import Path

here=Path(__file__).resolve().parent
groups=json.loads((here/'manifest.json').read_text())
titles=['Crossbar 与早期 DDR 方案','可编辑导出验证','启动初始化','软硬件关系','DDR / LVDS / ISP / GB','LLC / Cache / SPM']
page=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>科研图新旧对照</title>
<style>
*{box-sizing:border-box}body{margin:0;color:#222;background:#fff;font:16px/1.65 system-ui,sans-serif}
main{max-width:1540px;margin:auto;padding:28px}h1{font-size:28px}h2{font-size:23px;margin:40px 0 18px;border-bottom:1px solid #aaa}
a{color:#17658a}nav a{margin-right:22px;display:inline-block}.controls{position:sticky;top:0;background:#fff;padding:12px 0;border-bottom:1px solid #aaa;z-index:2}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:start}figure{margin:0 0 30px}figcaption{max-width:720px;margin-top:10px}h3{font-size:18px;margin:12px 0}
.picture{overflow:auto}img{display:block;width:var(--figure-width,688px);max-width:none;height:auto}body.gray img{filter:grayscale(1)}
details{margin:12px 0}summary{cursor:pointer}.muted{color:#555}label{margin-right:20px}input{vertical-align:middle}
@media(max-width:900px){.pair{grid-template-columns:1fr}main{padding:16px}img{max-width:100%;height:auto}.controls{position:static}}
</style><main><h1>科研图新旧对照</h1>
<p>新版以短标签表达关系，解释放在图注。左右使用相同显示宽度；复杂主题已拆图。新版采用英文标签与中文图注，因此本页是工作对照，不是控制语言、版面面积的读者 A/B 实验。</p>
<p><a href="README.md">交付说明</a> · <a href="skill/publication-figures/SKILL.md">新 skill 快照</a></p>
<div class="controls"><label>显示宽度 <input id="width" type="range" min="350" max="1000" value="688"> <output id="width-value">688 px</output></label><label><input id="gray" type="checkbox">灰度对照</label></div><nav>''']
for i,title in enumerate(titles): page.append(f'<a href="#g{i}">{title}</a>')
page.append('</nav>')
for i,((group,figs),title) in enumerate(zip(groups.items(),titles)):
    new='../'+group+'_new/'
    page.append(f'<section id="g{i}"><h2>{title}</h2><p><a href="{new}README.md">完整图注与条件</a> · <a href="{new}export/diagrams.pptx">可编辑 PPTX</a></p><div class="pair"><div><h3>旧版</h3>')
    seen=set()
    for f in figs:
        if f['source'] in seen:continue
        seen.add(f['source'])
        path='../'+f['source']
        page.append(f'<figure><div class="picture"><a href="{path}"><img src="{path}" alt="旧版 {escape(f["name"])}"></a></div></figure>')
    page.append('</div><div><h3>新版</h3>')
    for f in figs:
        name=f['name']; svg=new+name+'.svg'
        page.append(f'<figure><div class="picture"><a href="{svg}"><img src="{svg}" alt="新版 {escape(name)}"></a></div><figcaption>{escape(f["caption"])}<p><a href="{svg}">SVG</a> · <a href="{new}export/{name}.pdf">PDF</a> · <a href="{new}export/{name}.png">PNG</a></p><details><summary>内容映射</summary>{escape(f["mapping"])}</details></figcaption></figure>')
    page.append('</div></div></section>')
page.append('''<p class="muted">图稿与导出检查不新增 SoC 运行证据。PPTX 已做结构检查，未在 Office 实测显示与编辑。</p></main>
<script>
document.querySelector('#width').addEventListener('input',e=>{document.documentElement.style.setProperty('--figure-width',e.target.value+'px');document.querySelector('#width-value').value=e.target.value+' px'});
document.querySelector('#gray').addEventListener('change',e=>document.body.classList.toggle('gray',e.target.checked));
</script></html>''')
(here/'index.html').write_text('\n'.join(page))
print('index.html generated')
