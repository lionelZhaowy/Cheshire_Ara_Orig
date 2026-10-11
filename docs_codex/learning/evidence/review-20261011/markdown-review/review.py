#!/usr/bin/env python3
"""Independent read-only Markdown export review; writes only a new --out-dir.

Run from the repository root, or pass --repo-root explicitly. Uses the already
installed markdown-it-py renderer. Never calls build_site.render().
"""
import argparse
import collections
import hashlib
import importlib.metadata
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo-root', type=Path, default=Path.cwd())
parser.add_argument('--out-dir', type=Path, required=True)
args = parser.parse_args()
repo = args.repo_root.resolve()
output = args.out_dir.resolve()
output.mkdir(parents=True, exist_ok=False)
shutil.copyfile(Path(__file__).resolve(), output / 'review.py')
learning = repo / 'docs_codex/learning'
sys.path.insert(0, str(learning / 'scripts'))
from markdown_export import Exporter, Tree, render_markdown
from build_site import ENTRIES, MIGRATIONS, content_bodies, headings
from markdown_it import MarkdownIt
renderer = MarkdownIt('commonmark', {'html': True}).enable('table')

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.pres = []
        self.headings = []
        self.cells = []
        self.tags = collections.Counter()
        self.ordered_starts = []
        self.text = []
        self.active = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags[tag] += 1
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'img':
            self.images.append((attrs.get('src'), attrs.get('alt')))
            self.links.append(attrs.get('src', ''))
        if tag == 'ol':
            self.ordered_starts.append(int(attrs.get('start', 1)))
        if tag in ('pre', 'h2', 'h3', 'td', 'th'):
            self.active.append([tag, attrs.get('id'), []])
        if tag == 'br':
            for capture in self.active:
                capture[2].append('\n')

    def handle_endtag(self, tag):
        if self.active and self.active[-1][0] == tag:
            kind, ident, parts = self.active.pop()
            text = ''.join(parts)
            if kind == 'pre':
                self.pres.append(text.strip('\n'))
            elif kind in ('h2', 'h3'):
                self.headings.append((kind, ident, text))
            else:
                self.cells.append((kind, text))

    def handle_data(self, text):
        self.text.append(text)
        for capture in self.active:
            capture[2].append(text)


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def markdown_ids(text):
    clean = re.sub(r'(?ms)^(`{3,}|~{3,}).*?^\1\s*$', '', text)
    ids = set(re.findall(r'<a\s+id="([^"]+)"', clean))
    seen = {}
    for title in re.findall(r'^#{1,6} (.+)$', clean, re.M):
        title = re.sub(r'<[^>]+>', '', title).lower().replace('`', '')
        slug = ''.join(c for c in title if c in ' _-' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')
        number = seen.get(slug, 0)
        seen[slug] = number + 1
        ids.add(slug + (f'-{number}' if number else ''))
    return ids


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


watched = sorted(set(learning.glob('*.html')) | set((learning / 'markdown').glob('*.md')) | set((learning / 'content').glob('*.html')) | {learning / 'scripts/markdown_export.py', learning / 'scripts/build_site.py', learning / 'scripts/pages.json', learning / 'scripts/anchor_migrations.json'})
before_hashes = {str(path.relative_to(repo)): digest(path) for path in watched}
errors = []
bodies = content_bodies()
pages = []
parsed_pages = {}
for entry in ENTRIES:
    slug = entry['slug']
    body, rows = headings(bodies[slug], entry)
    source = Document(body)
    path = learning / 'markdown' / f'{slug}.md'
    if not path.exists():
        errors.append(f'missing generated Markdown: {slug}')
        continue
    generated = path.read_text()
    rendered = Document(renderer.render(generated))
    parsed_pages[path.resolve()] = rendered
    current = []
    if set(source.ids) - set(rendered.ids):
        current.append('source anchor loss: ' + repr(sorted(set(source.ids) - set(rendered.ids))))
    if len(rendered.ids) != len(set(rendered.ids)):
        current.append('duplicate rendered ID')
    if source.pres != rendered.pres:
        current.append('pre/code contents differ')
    if [alt for _, alt in source.images] != [alt for _, alt in rendered.images]:
        current.append('image alt contents differ')
    exp = Exporter(slug, ENTRIES, MIGRATIONS)
    if [(exp.url(src), alt) for src, alt in source.images] != rendered.images:
        current.append('image path conversion differs')
    if [(kind, normalize(text)) for kind, _, text in source.headings] != [(kind, normalize(text)) for kind, _, text in rendered.headings]:
        current.append('source/generated heading order or text differs')
    if [(kind, normalize(text)) for kind, text in source.cells] != [(kind, normalize(text)) for kind, text in rendered.cells]:
        current.append('table cell type/order/text differs')
    # Generated explicit anchors delimit body from metadata and the chapter TOC.
    prefix = generated.split('<a id=', 1)[0]
    toc = re.findall(r'(?m)^\s*- \[(.*?)\]\(#([^)]*)\)', prefix)
    expected_toc = [(text, ident) for _, ident, text in rows]
    if toc != expected_toc:
        current.append(f'TOC differs: expected {len(expected_toc)}, got {len(toc)}')
    errors.extend(f'{slug}: {message}' for message in current)
    pages.append({'slug': slug, 'source_headings': len(rows), 'markdown_toc_entries': len(toc), 'pre_blocks': len(source.pres), 'images': len(source.images), 'table_cells': len(source.cells), 'source_ids': len(source.ids), 'errors': current})

links = 0
for path, parsed in parsed_pages.items():
    for link in parsed.links:
        u = urlsplit(link)
        if u.scheme or link.startswith('//'):
            continue
        links += 1
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        if not target.exists():
            errors.append(f'{path.name}: missing {link}')
            continue
        if u.fragment:
            if target in parsed_pages:
                ids = set(parsed_pages[target].ids)
            elif target.suffix == '.html':
                ids = set(Document(target.read_text()).ids)
            elif target.suffix == '.md':
                ids = markdown_ids(target.read_text())
            else:
                continue
            if unquote(u.fragment) not in ids:
                errors.append(f'{path.name}: missing anchor {link}')

entry = next(e for e in ENTRIES if e['slug'] == 'runtime')
sample_sources = {
    'inline_anchor_text': '<p>before <a id="embedded">KEPT_TEXT</a> after</p>',
    'nested_list': '<ul><li>parent<ul><li>child one</li><li>child two</li></ul></li></ul>',
    'ordered_start': '<ol start="5"><li>fifth</li><li>sixth</li></ol>',
    'complex_table': '<table><tr><th>header</th></tr><tr><td><p>para1</p><p>para2</p><pre><code>a = 1\nb = 2</code></pre></td></tr></table>',
    'code_pipe_entities': '<p><code>a | b</code> &lt;literal&gt; _x_ &amp; asterisk*</p><pre><code>if (a &lt; b) {\n  printf("``` | \\n");\n}</code></pre><table><tr><th>code</th></tr><tr><td><code>a | b</code></td></tr></table>',
    'nested_headings': '<section><h2 id="group">Group</h2><h3 id="child">Child</h3></section>',
    'merged_table': '<table id="merged"><tr><th colspan="2">Two</th></tr><tr><td>A</td><td>B</td></tr></table>',
}
samples = []
for name, body in sample_sources.items():
    generated = render_markdown(entry, body, ENTRIES, MIGRATIONS)
    html = renderer.render(generated)
    parsed = Document(html)
    source = Document(body)
    current = []
    if not set(source.ids) <= set(parsed.ids) or len(parsed.ids) != len(set(parsed.ids)):
        current.append('lost/duplicate ID')
    if source.pres != parsed.pres:
        current.append('pre text differs')
    if name == 'inline_anchor_text' and 'KEPT_TEXT' not in ''.join(parsed.text):
        current.append('anchor child text lost')
    if name == 'nested_list' and '<li>parent\n<ul>' not in html:
        current.append('parent/child list nesting differs')
    if name == 'ordered_start' and source.ordered_starts != parsed.ordered_starts:
        current.append('ordered start differs')
    if name == 'complex_table' and ('<p>para1</p><p>para2</p>' not in html or '<table>' not in html):
        current.append('complex table structure not preserved')
    if name == 'code_pipe_entities' and '<td><code>a | b</code></td>' not in html:
        current.append('pipe in table code differs')
    if name == 'nested_headings' and ('- [Group](#group)' not in generated or '- [Child](#child)' not in generated):
        current.append('nested heading missing from TOC')
    if name == 'merged_table' and 'colspan="2"' not in html:
        current.append('merged table lost colspan')
    (output / f'sample-{name}.md').write_text(generated)
    (output / f'sample-{name}.html').write_text(html)
    errors.extend(f'sample {name}: {message}' for message in current)
    samples.append({'name': name, 'errors': current})

rejections = []
for name, source in [('unknown', '<p>ok<video>secret</video></p>'), ('mismatched', '<p><strong>x</p>'), ('unclosed', '<p>x')]:
    try:
        Tree(source)
        errors.append(f'{name}: invalid input accepted')
        rejections.append({'case': name, 'rejected': False})
    except ValueError as exc:
        rejections.append({'case': name, 'rejected': True, 'message': str(exc)})

after_hashes = {str(path.relative_to(repo)): digest(path) for path in watched}
if before_hashes != after_hashes:
    errors.append('source/generated input files changed during review')
report = {
    'status': 'PASS' if not errors else 'FAIL',
    'review_date': '2026-10-11',
    'input_head': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
    'renderer': 'markdown-it-py ' + importlib.metadata.version('markdown-it-py') + ', CommonMark + HTML + table rule',
    'scope': 'Existing 51 generated Markdown files and in-memory synthetic cases; no site generation, browser, target build, RTL or board run.',
    'generated_pages': len(pages),
    'headings_and_toc_entries': sum(p['source_headings'] for p in pages),
    'pre_blocks_preserved': sum(p['pre_blocks'] for p in pages),
    'images_preserved': sum(p['images'] for p in pages),
    'table_cells_preserved': sum(p['table_cells'] for p in pages),
    'source_ids_preserved': sum(p['source_ids'] for p in pages),
    'local_links_checked': links,
    'read_only_input_files': len(watched),
    'pages': pages,
    'samples': samples,
    'rejection_cases': rejections,
    'errors': errors,
    'input_sha256': before_hashes,
}
(output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
summary = {key: value for key, value in report.items() if key not in ('pages', 'samples', 'input_sha256')}
(output / 'checks.txt').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
