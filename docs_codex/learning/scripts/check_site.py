#!/usr/bin/env python3
"""Lightweight offline documentation checks (not browser or RTL verification)."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import xml.etree.ElementTree as ET
import re,subprocess
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
        if u.fragment and target.suffix=='.html':
            other=pages.get(target) or Page(target.read_text())
            if unquote(u.fragment) not in other.ids:errors.append(f'bad anchor {p.name}: {link}')
    if p.stem not in ['index','evidence']:
        if 'class="goals"' not in p.read_text() or '<details>' not in p.read_text():errors.append(f'missing teaching structure: {p.name}')
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
