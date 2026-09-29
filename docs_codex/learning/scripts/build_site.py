#!/usr/bin/env python3
"""Offline site assembler. pages.json is the single ordered chapter manifest."""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parent.parent
PAGES=json.loads((ROOT/'scripts/pages.json').read_text())
LEGACY=json.loads((ROOT/'scripts/legacy_links.json').read_text())
def render():
    for i,(slug,title,subtitle) in enumerate(PAGES):
        body=(ROOT/'content'/f'{slug}.html').read_text()
        ids=set(re.findall(r'\bid="([^"]+)"',body))
        for old,dest in LEGACY.get(slug,{}).get('anchors',{}).items():
            if old in ids:continue
            section=dest.partition('#')[2]
            body=body.replace(f'<h2 id="{section}">',f'<span class="legacy-anchor" id="{old}"></span><h2 id="{section}">',1)
            ids.add(old)
        # Tables remain internally scrollable with JavaScript disabled.
        body=re.sub(r'(<table\b.*?</table>)',r'<div class="table-wrap">\1</div>',body,flags=re.S)
        nav=''
        for j,(s,t,_) in enumerate(PAGES):
            if j in (0,17):nav+=f'<p class="nav-group">{"学习主线" if j==0 else "实验与参考"}</p>'
            nav+=f'<a href="{s}.html"'+(' aria-current="page"' if s==slug else '')+f'>{escape(t)}</a>'
        heads=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body)
        toc=''.join(f'<a href="#{id}">{re.sub("<[^>]+>","",txt)}</a>' for id,txt in heads)
        prev=f'<a href="{PAGES[i-1][0]}.html">← {PAGES[i-1][1]}</a>' if i else '<a href="labs.html">打开实验手册 →</a>'
        nxt=f'<a href="{PAGES[i+1][0]}.html">{PAGES[i+1][1]} →</a>' if i+1<len(PAGES) else '<a href="index.html">回到阅读路线</a>'
        (ROOT/f'{slug}.html').write_text(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Cheshire 实验课堂</title><link rel="stylesheet" href="assets/site.css"><script defer src="assets/site.js"></script></head>
<body><a class="skip" href="#main">跳到正文</a><aside class="sidebar"><a class="brand" href="index.html">CHESHIRE <span>实验课堂</span></a><p class="edition">CVA6 × Ara · 从硬件到程序</p><nav aria-label="章节">{nav}</nav><div class="sidebar-foot">离线可读 · 单线课程<br><a href="README.md">维护说明</a> · <a href="../learning_backup/index.html">旧版备份</a></div></aside>
<div class="workspace"><header class="topbar"><span>L01 / {"学习主线" if i<17 else "实验与参考"}</span><a href="evidence.html">来源与验证记录 ↗</a></header><main id="main"><div class="chapter-head"><p class="eyebrow">UNDERSTAND · TRACE · BUILD · VERIFY</p><h1>{title}</h1><p class="subtitle">{subtitle}</p></div><nav class="toc" aria-label="本页目录">{toc}</nav>{body}<nav class="nextprev" aria-label="上下章">{prev}{nxt}</nav></main><footer>Cheshire / CVA6 / Ara · L01 中文工程教材 · 2026-09-29</footer></div></body></html>
''')
    slugs={s for s,_,_ in PAGES}
    for slug,entry in LEGACY.items():
        if slug in slugs:continue
        links=''.join(f'<p id="{escape(id)}"><a href="{escape(dest)}">原章节位置：{escape(id)} → 新教材</a></p>' for id,dest in entry['anchors'].items())
        # Static destinations work even when scripts are unavailable.
        mapping=json.dumps(entry['anchors'],ensure_ascii=False)
        target=json.dumps(entry['target'])
        (ROOT/f'{slug}.html').write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旧链接迁移 | Cheshire 实验课堂</title><link rel="stylesheet" href="assets/site.css"></head><body><main class="compat"><h1>本章已并入单线教材</h1><p><a href="{entry['target']}">进入新教材对应章节</a> · <a href="../learning_backup/{slug}.html">查看原版内容</a></p><p>旧书签继续可用；以下链接供关闭脚本时使用。</p>{links}</main><script>const redirects={mapping};location.replace(redirects[decodeURIComponent(location.hash.slice(1))]||{target});</script></body></html>\n''')
    print(f'Built {len(PAGES)} main pages and {len(set(LEGACY)-slugs)} legacy redirects')
if __name__=='__main__':render()
