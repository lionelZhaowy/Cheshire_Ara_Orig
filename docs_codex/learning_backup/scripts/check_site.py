#!/usr/bin/env python3
"""Lightweight offline documentation checks (not browser or RTL verification)."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import xml.etree.ElementTree as ET
import re,subprocess,unicodedata
from html import unescape
from build_site import PAGES
ROOT=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
    def __init__(self,s):
        super().__init__(convert_charrefs=True); self.ids=[];self.links=[];self.assets=[];self.imgs=[];self.feed(s)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if 'href' in d:self.links.append(d['href'])
        if tag in ('script','img','iframe','source') and 'src' in d:self.assets.append(d['src']);self.links.append(d['src'])
        if tag=='link' and d.get('rel')=='stylesheet':self.assets.append(d.get('href',''))
        if tag=='img':self.imgs.append(d)
pages={p:Page(p.read_text()) for p in ROOT.glob('*.html')}
errors=[];links=0
# Markdown headings retain compatibility aliases when renamed.
def markdown_ids(text):
    text=re.sub(r"```.*?```", "", text, flags=re.S)
    ids=set(re.findall(r'<a\s+id="([^"]+)"', text)); seen={}
    for title in re.findall(r"^#{1,6} (.+)$", text, re.M):
        title=re.sub(r"<[^>]+>", "", title).lower().replace("`", "")
        slug="".join(c for c in title if c in " _-" or unicodedata.category(c)[0] in "LNM").replace(" ", "-")
        n=seen.get(slug,0);seen[slug]=n+1
        ids.add(slug+(f"-{n}" if n else ""))
    return ids

def check_local_link(p,link):
    u=urlsplit(link)
    if u.scheme or link.startswith('//'):return
    target=(p.parent/unquote(u.path)).resolve() if u.path else p
    if not target.exists():errors.append(f'missing {p}: {link}');return
    if u.fragment:
        if target.suffix=='.md':ids=markdown_ids(target.read_text())
        elif target.suffix=='.html':ids=(pages.get(target) or Page(target.read_text())).ids
        else:return
        if unquote(u.fragment) not in ids:errors.append(f'bad anchor {p}: {link}')

for slug,title,_ in PAGES:
    p=ROOT/(slug+'.html');html=p.read_text()
    if re.findall(r'<h1>(.*?)</h1>',html)!=[title]:errors.append(f'H1 mismatch: {slug}')
    if re.findall(r'<title>(.*?)</title>',html)!=[title+' | Cheshire 实验课堂']:errors.append(f'title mismatch: {slug}')
    sidebar=re.search(r'<nav aria-label="章节">(.*?)</nav>',html,re.S)[1]
    names=[(a,unescape(b)) for a,b in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>',sidebar)]
    if names!=[(x+'.html',y) for x,y,_ in PAGES]:errors.append(f'sidebar mismatch: {slug}')
    h2=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',html)
    toc=re.search(r'<nav class="toc"[^>]*>(.*?)</nav>',html,re.S)[1]
    if re.findall(r'<a href="#([^"]+)">(.*?)</a>',toc)!=[(a,re.sub('<[^>]+>','',b)) for a,b in h2]:errors.append(f'TOC mismatch: {slug}')
    i=[x[0] for x in PAGES].index(slug)
    adjacent=re.search(r'<nav class="nextprev"[^>]*>(.*?)</nav>',html,re.S)[1]
    if i and f'<a href="{PAGES[i-1][0]}.html">← {PAGES[i-1][1]}</a>' not in adjacent:errors.append(f'previous mismatch: {slug}')
    if i+1<len(PAGES) and f'<a href="{PAGES[i+1][0]}.html">{PAGES[i+1][1]} →</a>' not in adjacent:errors.append(f'next mismatch: {slug}')
    levels=[int(x) for x in re.findall(r'<h([1-4])\b',html)]
    if any(b>a+1 for a,b in zip(levels,levels[1:])):errors.append(f'heading level skipped: {slug}')

for p,page in pages.items():
    if len(page.ids)!=len(set(page.ids)):errors.append(f'duplicate IDs: {p}')
    for asset in page.assets:
        if urlsplit(asset).scheme or asset.startswith('//'):errors.append(f'external render asset: {asset}')
    for img in page.imgs:
        if not img.get('alt'):errors.append(f'missing alt: {p}')
    for link in page.links:
        u=urlsplit(link)
        if u.scheme or link.startswith('//'):continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        if not target.exists(): errors.append(f'missing {p.name}: {link}');continue
        links+=1
        if u.fragment and target.suffix=='.md':check_local_link(p,link)
        if u.fragment and target.suffix=='.html':
            other=pages.get(target) or Page(target.read_text())
            if unquote(u.fragment) not in other.ids:errors.append(f'bad anchor {p.name}: {link}')
    if p.stem not in ['index','evidence']:
        if 'class="goals"' not in p.read_text() or '<details>' not in p.read_text():errors.append(f'missing teaching structure: {p.name}')
# Tutorials, reference manuals and handoffs can all link to renamed headings.
markdown_links=0
for p in ROOT.parent.rglob('*.md'):
    if 'evidence' in p.parts:continue
    text=re.sub(r"```.*?```", "", p.read_text(), flags=re.S)
    for link in re.findall(r'\[[^]\n]*\]\(([^)]+)\)',text):
        check_local_link(p.resolve(),link);markdown_links+=1
for p in (ROOT/'assets').glob('*.svg'):ET.parse(p)
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix in ['.html','.css','.js','.py','.sh','.md'] and 'evidence' not in p.parts:
        s=p.read_text()
        if re.search(r'(?m)[ \t]+$',s): errors.append(f'trailing whitespace: {p}')
for p in (ROOT/'scripts').glob('*.sh'):
    r=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True)
    if r.returncode:errors.append(r.stderr)
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)} HTML pages, {links} local links/resources, anchors, {len(list((ROOT/"assets").glob("*.svg")))} SVG XML, alt text, offline assets, shell syntax, whitespace')
print(f'PASS: page titles/H1/sidebar/TOC/previous-next, heading levels; {markdown_links} Markdown links and fragments')
