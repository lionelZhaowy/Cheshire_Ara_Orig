#!/usr/bin/env python3
"""Validate current pages against an explicit evidence batch; preserve old reports."""
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, re, subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from markdown_it import MarkdownIt
from build import ROOT, ENTRIES, rendered

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-dir', type=Path, default=ROOT/'evidence/complete-stack-20261013')
parser.add_argument('--out', type=Path, help='Optional NEW report file; otherwise print only')
args = parser.parse_args()
EVID = args.evidence_dir.resolve()
REPO = ROOT.parents[2]
OUT = args.out.resolve() if args.out else EVID/'validation.json'
if args.out and OUT.exists():
    parser.error('Report already exists; choose a new --out path')
errors = []
def require(condition, message):
    if not condition: errors.append(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def check_hash(path, expected, label):
    require(path.is_file() and sha(path) == expected, label)
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.links = []; self.ids = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'a' and 'name' in a: self.ids.append(a['name'])
        for field in ('href', 'src'):
            if field in a: self.links.append(a[field])
md = MarkdownIt('commonmark', {'html': True}).enable('table')
def parse(path):
    text = path.read_text()
    if path.suffix == '.md':
        page = Page(md.render(text))
        for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
            page.ids.append(re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-'))
        return page
    return Page(text)

config = json.loads((EVID/'checks.json').read_text())
sources = json.loads((EVID/'sources.json').read_text())
generated = list(rendered())
for slug, html, markdown in generated:
    require((ROOT/f'{slug}.html').read_text() == html, f'stale HTML: {slug}')
    require((ROOT/'markdown'/f'{slug}.md').read_text() == markdown, f'stale Markdown: {slug}')
documents = [ROOT/f'{p["slug"]}.html' for p in ENTRIES]
documents += [ROOT/'markdown'/f'{p["slug"]}.md' for p in ENTRIES]
documents += [REPO/name for name in config['extra_documents']]
count = 0
for path in documents:
    if not path.is_file():
        errors.append(f'missing document: {path}'); continue
    page = parse(path)
    if path.suffix == '.html':
        require(len(page.ids) == len(set(page.ids)), f'duplicate anchors: {path.name}')
    for link in page.links:
        u = urlsplit(link)
        if u.scheme or u.netloc: continue
        target = (path.parent/unquote(u.path)).resolve() if u.path else path
        count += 1
        require(target.exists() or target == OUT, f'missing: {path.name} -> {link}')
        if target.is_file() and u.fragment and target.suffix in ('.md', '.html'):
            require(unquote(u.fragment) in parse(target).ids, f'anchor: {path.name} -> {link}')
for name, expected in sources['files'].items():
    check_hash(REPO/name, expected, f'source identity changed: {name}')
for row in sources.get('module_equivalence', []):
    fragments = []
    for name in row['files']:
        match = re.search(r'\bmodule '+re.escape(row['module'])+r'\b.*?\bendmodule', (REPO/name).read_text(), re.S)
        fragments.append(match.group() if match else None)
    require(all(fragments) and len(set(fragments)) == 1, f'module mismatch: {row["module"]}')
browser = json.loads((EVID/config['browser']).read_text())
require(browser.get('status') == 'pass', 'browser checks incomplete')
require(browser.get('chapter_slugs') == [p['slug'] for p in ENTRIES], 'browser chapter list stale')
require(len(browser['pages']) == 2*len(ENTRIES), 'browser viewport count mismatch')
for name, expected in browser['html_sha256'].items():
    check_hash(ROOT/name, expected, f'HTML changed after preview: {name}')
for row in browser['figures']:
    check_hash(REPO/row['file'], row['sha256'], f'SVG changed after preview: {row["file"]}')
for name in config['export_reports']:
    export = json.loads((REPO/name).read_text())
    for row in export['figures']:
        check_hash(REPO/row['source'], row['sha256'], f'stale PPTX export: {row["source"]}')
for name in config['visual_reviews']:
    review = json.loads((REPO/name).read_text())
    require(bool(review['reviewed_figures']), f'empty visual review: {name}')
    for artifact, expected in review['artifacts'].items():
        check_hash(REPO/artifact, expected, f'visual review input changed: {artifact}')
initial = json.loads((EVID/'input.json').read_text())
for name, expected in initial['historical_evidence'].items():
    check_hash(REPO/name, expected, f'historical evidence changed: {name}')
protected = {name: (REPO/name).is_file() and sha(REPO/name) == expected
             for name, expected in initial['protected'].items()
             if name not in config['authorized_edits']}
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
require(head == sources['head'], 'HEAD changed')
for p in list((ROOT/'content').glob('*.html')) + list((ROOT/'scripts').glob('*')):
    if p.is_file():
        require(not any(line.rstrip() != line for line in p.read_text().splitlines()), f'trailing whitespace: {p}')
report = dict(status='pass' if not errors else 'fail', errors=errors,
              head=head, evidence_dir=str(EVID.relative_to(REPO)),
              html_markdown_pairs=len(generated), local_link_occurrences=count,
              referenced_source_files=len(sources['files']),
              preserved_historical_evidence=len(initial['historical_evidence']),
              browser_viewports=len(browser['pages']), svg_figures=len(browser['figures']),
              preexisting_protected_inputs=protected,
              external_input_changes=[name for name, same in protected.items() if not same],
              application_rebuilt=False, target_simulation=False, fpga_test=False,
              office_application_test=False)
encoded = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
if args.out:
    with OUT.open('x') as out: out.write(encoded)
print(encoded, end='')
sys.exit(bool(errors))
