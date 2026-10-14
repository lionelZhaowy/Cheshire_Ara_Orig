#!/usr/bin/env python3
"""Render this focused topic with the existing course HTML/Markdown components."""
import sys,json,re
from pathlib import Path
from html import escape
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent
LEARN=ROOT.parents[1]/'learning'
sys.path.insert(0,str(LEARN/'scripts'))
from build_site import headings,toc_html
from markdown_export import render_markdown
ENTRIES=json.loads((ROOT/'scripts/pages.json').read_text())
def rendered():
 for i,p in enumerate(ENTRIES):
  slug=p['slug'];raw=(ROOT/'content'/f'{slug}.html').read_text();body,rows=headings(raw,p)
  md=render_markdown(p,body,ENTRIES,{})
  body=re.sub(r'(<table\b.*?</table>)',r'<div class="table-wrap">\1</div>',body,flags=re.S)
  nav=''.join(f'<a class="chapter-link" href="{q["slug"]}.html"'+(' aria-current="page"' if q==p else '')+f'>{j:02d} · {escape(q["title"])}</a>' for j,q in enumerate(ENTRIES))
  prev=f'<a href="{ENTRIES[i-1]["slug"]}.html">← {ENTRIES[i-1]["title"]}</a>' if i else '<a href="../README.md">← 软件参考手册</a>'
  nxt=f'<a href="{ENTRIES[i+1]["slug"]}.html">{ENTRIES[i+1]["title"]} →</a>' if i+1<len(ENTRIES) else '<a href="index.html">返回专题入口</a>'
  html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(p['title'])} | Cheshire 软硬件接口</title><link rel="stylesheet" href="../../learning/assets/site.css"><script defer src="../../learning/assets/site.js"></script></head><body><a class="skip" href="#main">跳到正文</a><aside class="sidebar"><a class="brand" href="index.html">CHESHIRE <span>软硬件接口</span></a><p class="edition">L01 · 当前工程源码专题</p><details class="site-menu" open><summary>专题目录</summary><nav aria-label="章节">{nav}</nav></details><div class="sidebar-foot"><a href="README.md">维护说明</a> · <a href="../../learning/index.html">主教材</a></div></aside><div class="workspace"><header class="topbar"><a href="index.html">专题入口</a><a href="labs.html#evidence">本轮验证记录</a></header><main id="main"><div class="chapter-head"><p class="eyebrow">{escape(p.get("layer", "软硬件接口层"))}</p><h1>{escape(p['title'])}</h1><p class="subtitle">{escape(p['subtitle'])}</p><p class="format-link"><a href="markdown/{slug}.md">Markdown 阅读版</a></p></div><details class="toc-panel" open><summary>本页目录</summary><nav class="toc">{toc_html(rows)}</nav></details>{body}<nav class="nextprev">{prev}{nxt}</nav></main><footer>L01 · 2026-10-13 · 源码分析与文档验证；目标运行另行验收</footer></div></body></html>\n'''
  yield slug,html,md
def build():
 for slug,html,md in rendered():
  (ROOT/f'{slug}.html').write_text(html)
  (ROOT/'markdown'/f'{slug}.md').write_text(md)
 print(f'Built {len(ENTRIES)} HTML/Markdown pairs; existing course output untouched')
if __name__=='__main__':build()
