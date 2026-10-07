#!/usr/bin/env python3
"""Build an offline course from explicit part/chapter metadata and H2/H3 content."""
from pathlib import Path
from html import escape,unescape
import json,re
ROOT=Path(__file__).resolve().parent.parent
COURSE=json.loads((ROOT/'scripts/pages.json').read_text())
PARTS={p['id']:p for p in COURSE['parts']}
ENTRIES=COURSE['pages']
def title(p):return (f"{p['number']:02d} · " if p['kind']=='chapter' else '')+p['title']
PAGES=[(p['slug'],title(p),p['subtitle']) for p in ENTRIES]
MIGRATIONS=json.loads((ROOT/'scripts/anchor_migrations.json').read_text())
def plain(s):return unescape(re.sub('<[^>]+>','',s))
def headings(body,entry):
    rows=[];section=0;sub=0;ids=set()
    def repl(m):
        nonlocal section,sub
        level,ident,txt=m.groups();level=int(level)
        if ident in ids:raise ValueError('duplicate heading '+ident)
        ids.add(ident)
        if level==2:section+=1;sub=0
        else:
            if not section:raise ValueError('H3 before H2: '+entry['slug'])
            sub+=1
        number=f"{entry['number']}.{section}"+(f'.{sub}' if level==3 else '') if entry['kind']=='chapter' else ''
        display=(number+' ' if number else '')+plain(txt)
        rows.append((level,ident,display))
        prefix=f'<span class="section-number">{number}</span> ' if number else ''
        return f'<h{level} id="{ident}">{prefix}{txt}</h{level}>'
    return re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>',repl,body),rows

def toc_html(rows):
    groups=[]
    for level,id,txt in rows:
        if level==2:groups.append([id,txt,[]])
        else:groups[-1][2].append((id,txt))
    def link(id,txt):return f'<a href="#{escape(id)}">{escape(txt)}</a>'
    return '<ol>'+''.join('<li>'+link(i,t)+('<ol>'+''.join('<li>'+link(x,y)+'</li>' for x,y in kids)+'</ol>' if kids else '')+'</li>' for i,t,kids in groups)+'</ol>'

def nav_html(entry,rows):
    def chapter(p):
        current=p['slug']==entry['slug']
        a=f'<a class="chapter-link" href="{p["slug"]}.html"'+(' aria-current="page"' if current else '')+f'>{escape(title(p))}</a>'
        if current and p['kind']=='chapter':a+='<ul class="current-sections">'+''.join(f'<li><a href="#{id}">{escape(txt)}</a></li>' for level,id,txt in rows if level==2)+'</ul>'
        return a
    nav=chapter(ENTRIES[0])
    for part in COURSE['parts']:
        nav+=f'<details class="nav-part" data-part="{part["id"]}"'+(' open' if entry.get('part')==part['id'] else '')+f'><summary>{part["label"]} · {part["title"]}</summary><div class="part-chapters">'
        nav+=''.join(chapter(p) for p in ENTRIES if p.get('part')==part['id'])+'</div></details>'
    nav+='<details class="nav-part references"'+(' open' if entry['kind']=='reference' else '')+'><summary>实验与参考</summary><div class="part-chapters">'
    return nav+''.join(chapter(p) for p in ENTRIES if p['kind']=='reference')+'</div></details>'

def render():
    slugs={p['slug'] for p in ENTRIES}
    bodies={p['slug']:(ROOT/'content'/f'{p["slug"]}.html').read_text() for p in ENTRIES}
    # Every migration points to actual content, never another redirect or a phantom alias.
    for old,dest in MIGRATIONS.items():
        file,_,id=dest.partition('#');slug=file.removesuffix('.html')
        if slug not in bodies or (id and id not in re.findall(r'\bid="([^"]+)"',bodies[slug])):raise ValueError(f'Unresolved migration: {old} -> {dest}')
    for i,p in enumerate(ENTRIES):
        slug=p['slug'];body=bodies[slug];ids=set(re.findall(r'\bid="([^"]+)"',body));moved={};notices=[]
        for old,dest in MIGRATIONS.items():
            f,sep,id=old.partition('#')
            if f!=slug+'.html' or not sep or id in ids:continue
            df,_,target=dest.partition('#')
            if df==f:
                # Match any real element, including H3 and reference form fields. Fail loudly.
                pattern=r'(<[a-z][^>]*\bid="'+re.escape(target)+r'"[^>]*>)'
                body,n=re.subn(pattern,f'<span class="legacy-anchor" id="{escape(id)}"></span>\\1',body,count=1)
                if n!=1:raise ValueError(f'Missing alias target: {old} -> {dest}')
            else:
                moved[id]=dest;notices.append(f'<p id="{escape(id)}"><a href="{escape(dest)}">原位置 {escape(id)} 已移至：{escape(title(next(x for x in ENTRIES if x["slug"]+".html"==df)))} · {escape(target)}</a></p>')
            ids.add(id)
        body,rows=headings(body,p)
        body=re.sub(r'(<table\b.*?</table>)',r'<div class="table-wrap">\1</div>',body,flags=re.S)
        if notices:body+='<aside class="moved-sections"><strong>旧书签对应位置</strong><p>以下链接供关闭脚本时使用；正文目录指向当前章节内容。</p>'+''.join(notices)+'</aside>'
        scripts='<script type="application/json" id="moved-anchors">'+json.dumps(moved,ensure_ascii=False)+'</script>'
        part=PARTS.get(p.get('part'));label=part['label']+' · '+part['title'] if part else ('实验与参考' if p['kind']=='reference' else '全书路线')
        prev=f'<a href="{ENTRIES[i-1]["slug"]}.html">← {escape(title(ENTRIES[i-1]))}</a>' if i else '<a href="labs.html">打开实验手册 →</a>'
        nxt=f'<a href="{ENTRIES[i+1]["slug"]}.html">{escape(title(ENTRIES[i+1]))} →</a>' if i+1<len(ENTRIES) else '<a href="index.html">回到阅读路线</a>'
        number=f'第 {p["number"]} 章' if p['kind']=='chapter' else p['title']
        (ROOT/(slug+'.html')).write_text(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title(p))} | Cheshire 实验课堂</title><link rel="stylesheet" href="assets/site.css"><script defer src="assets/site.js"></script></head>
<body><a class="skip" href="#main">跳到正文</a><aside class="sidebar"><a class="brand" href="index.html">CHESHIRE <span>实验课堂</span></a><p class="edition">CVA6 × Ara · 工程教材</p><details class="site-menu" open><summary>全书目录</summary><nav aria-label="章节">{nav_html(p,rows)}</nav></details><div class="sidebar-foot">七篇 · 离线可读<br><a href="README.md">维护说明</a> · <a href="../learning_backup/index.html">历史备份</a></div></aside>
<div class="workspace"><header class="topbar"><nav aria-label="面包屑"><a href="index.html">L01</a> / <a href="index.html{('#part-'+part['id']) if part else ''}">{escape(label)}</a> / {escape(number)}</nav><a href="evidence.html#teaching-20261007">本轮验证记录 ↗</a></header><main id="main"><div class="chapter-head"><p class="eyebrow">{escape(label)}</p><h1>{escape(title(p))}</h1><p class="subtitle">{escape(p['subtitle'])}</p></div><details class="toc-panel"{(' open' if slug!='index' else '')}><summary>{("全书导览 · 展开查看各篇" if slug=="index" else "本章目录 · 节与小节")}</summary><nav class="toc" aria-label="本页目录">{toc_html(rows)}</nav></details>{body}<nav class="nextprev" aria-label="上下章">{prev}{nxt}</nav></main><footer>Cheshire / CVA6 / Ara · L01 中文工程教材 · 官方资料与源码解读 2026-10-07</footer></div>{scripts}</body></html>
''')
    retired=sorted({u.split('#')[0].removesuffix('.html') for u in MIGRATIONS}-slugs)
    for slug in retired:
        target=MIGRATIONS[slug+'.html'];anchors={old.split('#',1)[1]:dest for old,dest in MIGRATIONS.items() if old.startswith(slug+'.html#')}
        links=''.join(f'<p id="{escape(id)}"><a href="{escape(dest)}">{escape(id)} → 对应新节</a></p>' for id,dest in anchors.items())
        (ROOT/(slug+'.html')).write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旧链接迁移 | Cheshire 实验课堂</title><link rel="stylesheet" href="assets/site.css"></head><body><main class="compat"><h1>旧章节的位置已调整</h1><p><a href="{target}">进入对应章节</a> · <a href="../learning_backup/{slug}.html">历史版本</a></p><p>旧书签按具体小节迁移；关闭脚本可使用下面的链接。</p>{links}</main><script>const redirects={json.dumps(anchors,ensure_ascii=False)};location.replace(redirects[decodeURIComponent(location.hash.slice(1))]||{json.dumps(target)});</script></body></html>\n''')
    print(f'Built {len(ENTRIES)} main pages in {len(PARTS)} parts and {len(retired)} legacy redirects')
if __name__=='__main__':render()
