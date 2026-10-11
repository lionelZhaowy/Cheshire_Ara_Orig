#!/usr/bin/env python3
"""Render the local review as a standalone HTML document using installed Markdown."""
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'Architecture_Review_Report.md'
engine = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
body = engine.convert(source.read_text())
style = '''
body{margin:0;background:#f4f7fa;color:#233348;font:17px/1.75 "WenQuanYi Zen Hei",sans-serif}
main{max-width:1180px;margin:24px auto;padding:36px 42px;background:white;border:1px solid #dce4eb}
h1{font-size:30px;line-height:1.4}h2{font-size:25px;color:#20527a;margin-top:2em;border-bottom:1px solid #cfdde8}
h3{font-size:20px;margin-top:1.6em}a{color:#156ba2}p{overflow-wrap:anywhere}
table{border-collapse:collapse;display:block;overflow-x:auto;font-size:15px;line-height:1.65;margin:18px 0}
th,td{border:1px solid #cfd9e2;padding:9px 12px;min-width:105px;vertical-align:top}
th{background:#eaf1f7}tr:nth-child(even){background:#f7f9fb}
code{font-family:monospace;font-size:.9em;overflow-wrap:anywhere;background:#edf2f6;padding:1px 3px}
pre{overflow:auto;padding:18px;background:#edf2f6;line-height:1.5}pre code{overflow-wrap:normal}
img{max-width:100%;height:auto}li{margin:7px 0}.toc{font-size:15px}.toc ul{padding-left:22px}
details{background:#f4f8fb;padding:14px 20px}summary{cursor:pointer;font-weight:bold}
@media(max-width:700px){body{font-size:16px}main{margin:0;padding:20px 16px;border:0}h1{font-size:25px}h2{font-size:22px}}
@media print{body{background:white}main{border:0;margin:0;padding:0}details{display:none}table{display:table;font-size:9pt}img{break-inside:avoid}}
'''
output = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cheshire–CVA6–Ara 架构审查</title><style>{style}</style></head>
<body><main><p><a href="Architecture_Review_Report.md">Markdown 源文件</a> · <a href="results/final/budget.md">预算结果</a></p>
<details><summary>报告目录</summary>{engine.toc}</details>{body}</main></body></html>
'''
target = source.with_suffix('.html')
target.write_text(output)
print(target)
