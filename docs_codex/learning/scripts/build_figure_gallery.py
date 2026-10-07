#!/usr/bin/env python3
"""Build a portable, offline old/new comparison gallery in a NEW directory.

The page is intended for figures/20261007/index.html; --out-dir allows isolated
generation and comparison before installing a changed gallery.
"""
import argparse, html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',required=True,type=Path)
    args=ap.parse_args();args.out_dir.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'assets/figures-20261007/manifest.json').read_text())
    old=json.loads((ROOT/'figure_archive/20261007/manifest.json').read_text())
    for wave in sorted((ROOT/'assets/waves').glob('*.json')):
        obj=json.loads(wave.read_text());name='depth-'+wave.stem
        manifest[name]={'title':obj['head']['text'],'previous':'assets/'+name+'.svg',
            'current':'assets/'+name+'.svg','status':'WaveDrom 3.5.0 教学时序，保持原绘制方式',
            'source':'信号母版：assets/waves/'+wave.name,'wave':wave.name}
    manifest=dict(sorted(manifest.items()))
    h=html.escape
    parts=['''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>教材插图 · 新旧对照</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f7fa;color:#19364b;font:16px/1.7 system-ui,"WenQuanYi Zen Hei",sans-serif}
main{max-width:1680px;margin:auto;padding:30px}a{color:#216bb1}h1{font-size:32px}h2{font-size:23px;margin:0 0 12px}
nav{display:flex;gap:20px;flex-wrap:wrap}section{background:white;border:1px solid #c8d6e0;border-radius:10px;margin:30px 0;padding:24px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}.pair img{width:100%;height:auto;display:block}figure{margin:0;min-width:0}
figcaption{font-size:14px;color:#536b7d;margin-bottom:10px}p{overflow-wrap:anywhere}details li{margin:5px 0}
@media(max-width:850px){main{padding:16px}.pair{grid-template-columns:1fr}section{padding:15px}}
</style></head><body><main><h1>教材插图：37 张重绘结构图 + 6 张 WaveDrom 波形</h1>
<p>结构图按对象、接口、空间关系与因果过程重绘；波形继续用 WaveDrom 生成，保留原始 JSON 与渲染文件。点击图片可打开完整 SVG。</p>
<nav><a href="../../index.html">返回教材</a><a href="editable/diagrams.pptx">下载 37 页结构图可编辑 PPTX</a>
<a href="../../FIGURES.md">维护与验证说明</a><a href="editable/export_report.json">PPTX 结构检查</a></nav>
<p>SVG 保留文本；PPTX 使用独立形状与文本框。已做 SVG 浏览器检查与 PPTX 结构检查，未在 Office 实测。</p><details><summary>按图跳转</summary><ol>''']
    for name,item in manifest.items():parts.append(f'<li><a href="#{name}">{h(item["title"])}</a></li>')
    parts.append('</ol></details>')
    for i,(name,item) in enumerate(manifest.items(),1):
        pages=[p for p,refs in old['pages'].items() if item['previous'] in refs]
        links=' · '.join(f'<a href="../../{p}">{p.removesuffix(".html")}</a>' for p in pages)
        extra=(f'<a href="../../assets/waves/{item["wave"]}">WaveDrom JSON 母版</a>' if 'wave' in item else f'<a href="editable/{name}.editable.svg">导出器规范化 SVG</a>')
        parts.append(f'<section id="{name}"><h2>{i:02d} · {h(item["title"])}</h2><p>教材位置：{links} · {extra}</p><div class="pair">')
        for label,url in [('WaveDrom 当前版本' if 'wave' in item else '新版','../../'+item['current']),('旧图归档',f'../../figure_archive/20261007/assets/{name}.svg')]:
            parts.append(f'<figure><figcaption>{label}</figcaption><a href="{url}"><img src="{url}" alt="{h(item["title"])} · {label}" loading="lazy"></a></figure>')
        parts.append(f'</div><p>{h(item["status"])}。{h(item["source"])}</p></section>')
    parts.append('</main></body></html>')
    (args.out_dir/'index.html').write_text('\n'.join(parts)+'\n')
    print('Generated 43-pair gallery:',args.out_dir/'index.html')

if __name__=='__main__':main()
