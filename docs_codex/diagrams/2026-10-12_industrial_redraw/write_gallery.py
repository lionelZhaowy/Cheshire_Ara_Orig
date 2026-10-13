#!/usr/bin/env python3
"""Write an offline old/new gallery without touching source figures."""
import argparse,html,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
names={'crossbar_ara':'AXI Crossbar 实际结构','ddr_qos_proposal':'DDR 多端口仲裁与 QoS（历史方案）','example':'数据处理与反馈','initialization_hw_sw':'启动初始化的软硬件对应','program_execution_flow':'从复位到应用返回','cheshire_software_hardware':'SoC 软硬件分层','ddr_interconnect':'DDR / GB / 图像互联候选','llc_cache_spm':'LLC Cache / SPM','soc_full_architecture':'完整 SoC 架构'}
figs=json.loads((a.directory/'source_inventory.json').read_text())['figures']
parts=['''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>工业风格重绘 · 2026-10-12</title>
<style>
body{margin:0;background:#f0f1f3;color:#29292d;font:16px/1.6 system-ui,sans-serif}main{max-width:2200px;margin:auto;padding:28px}
h1{font-size:28px;margin:0}h2{font-size:23px;margin:0 0 8px}p{margin:8px 0 16px}a{color:#314d66}
nav{display:flex;gap:18px;flex-wrap:wrap;align-items:center}button,select{font:inherit;padding:7px 13px;border:1px solid #93939d;background:white;color:#29292d;cursor:pointer}button[aria-pressed=true]{background:#d8e8f4;border-color:#314d66}
article{background:white;margin:28px 0;padding:20px;border:1px solid #bdc5ce}.images{display:grid;grid-template-columns:1fr;gap:20px}.old{display:none}.compare .images{grid-template-columns:1fr 1fr}.compare .old{display:block}figure{margin:18px 0 0}figcaption{color:#606773;margin-bottom:8px}img{width:100%;height:auto;display:block}small{color:#606773}[hidden]{display:none!important}
@media(max-width:1000px){.compare .images{grid-template-columns:1fr}}
</style><main><h1>工业风格重绘 · 9 张独立图稿</h1>
<p>2026-10-12 · 非 learn 前缀图稿 · 横向组织、原生 SVG / PPTX。点击图片可打开矢量母版。</p>
<nav><a href="all_industrial.pptx">下载 9 页 PPTX 合辑</a><a href="README.md">交付说明</a><a href="figure_notes.md">图意与版本边界</a></nav>
<nav style="margin-top:18px"><button id="new" aria-pressed="true">仅看新版</button><button id="both" aria-pressed="false">新旧对照</button><label>选择图稿 <select id="pick"><option value="all">全部 9 张</option>''']
for f in figs:
 n=f['name'];parts.append(f'<option value="{n}">{html.escape(names[n])}</option>')
parts.append('</select></label></nav>')
for i,f in enumerate(figs,1):
 n=f['name'];title=html.escape(names[n]);old='../2026-10-11_native_reconstruction/'+n
 parts.append(f'''<article data-name="{n}" id="{n}"><h2>{i:02} · {title}</h2>
<nav><a href="{n}.svg">SVG</a><a href="{n}.png">PNG</a><a href="{n}.pptx">可编辑 PPTX</a><a href="{old}.svg">原图 SVG</a></nav>
<div class="images"><figure class="old"><figcaption>原版 · 保留未改</figcaption><a href="{old}.svg"><img loading="lazy" src="{old}.png" alt="{title}原图"></a></figure>
<figure><figcaption>工业风格版</figcaption><a href="{n}.svg"><img loading="lazy" src="{n}.png" alt="{title}工业风格新版"></a></figure></div></article>''')
parts.append('''<small>PNG 为 SVG 渲染，非 Office 截图。原图技术快照与候选状态保留；Office 显示/编辑未实测。</small></main>
<script>
const fresh=document.getElementById('new'),both=document.getElementById('both');
function setMode(compare){document.body.classList.toggle('compare',compare);fresh.setAttribute('aria-pressed',String(!compare));both.setAttribute('aria-pressed',String(compare))}
fresh.onclick=()=>setMode(false);both.onclick=()=>setMode(true);
document.getElementById('pick').onchange=e=>document.querySelectorAll('article').forEach(a=>a.hidden=e.target.value!=='all'&&a.dataset.name!==e.target.value);
</script></html>''')
out=a.directory/'index.html';assert not out.exists(),out;out.write_text('\n'.join(parts)+'\n')
print(out)
