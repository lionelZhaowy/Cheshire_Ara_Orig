#!/usr/bin/env python3
"""Check this topic, without rebuilding software or changing source snapshots."""
import sys
sys.dont_write_bytecode = True
import hashlib, json, re, subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from markdown_it import MarkdownIt
from build import ROOT, rendered

REPO = ROOT.parents[2]
FIG = REPO / 'docs_codex/diagrams/2026-10-13_software_hardware_interfaces'
OUT = ROOT / 'evidence/validation.json'
errors = []
def require(condition, message):
    if not condition:
        errors.append(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
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
        body = md.render(text)
        page = Page(body)
        for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
            page.ids.append(re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-'))
        return page
    return Page(text)

generated = list(rendered())
for slug, html, markdown in generated:
    require((ROOT / f'{slug}.html').read_text() == html, f'stale HTML: {slug}')
    require((ROOT / 'markdown' / f'{slug}.md').read_text() == markdown, f'stale Markdown: {slug}')

documents = list(ROOT.glob('*.html')) + list((ROOT / 'markdown').glob('*.md'))
documents += [ROOT / 'README.md', FIG / 'README.md',
              REPO / 'docs_codex/handoffs/L01_software_hardware_interfaces.md']
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
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        count += 1
        # The report is written only after checking, so its self-reference is valid.
        require(target.exists() or target == OUT, f'missing: {path.name} -> {link}')
        if target.is_file() and u.fragment and target.suffix in ('.md', '.html'):
            require(unquote(u.fragment) in parse(target).ids, f'anchor: {path.name} -> {link}')

sources = json.loads((ROOT / 'evidence/sources.json').read_text())
for name, expected in sources['files'].items():
    p = REPO / name
    require(p.is_file() and sha(p) == expected, f'source identity changed: {name}')
builds = json.loads((ROOT / 'evidence/builds.json').read_text())
for name, expected in builds['artifacts'].items():
    p = ROOT / 'evidence' / name
    require(p.is_file() and sha(p) == expected, f'build evidence changed: {name}')
browser = json.loads((ROOT / 'evidence/browser-review/browser.json').read_text())
require(browser.get('status') == 'pass' and len(browser['pages']) == 16, 'browser checks incomplete')
for name, expected in browser['html_sha256'].items():
    require(sha(ROOT / name) == expected, f'HTML changed after preview: {name}')
for row in browser['figures']:
    require(sha(FIG / row['file']) == row['sha256'], f'SVG changed after preview: {row["file"]}')
export = json.loads((FIG / 'export-reviewed/export_report.json').read_text())
for row in export['figures']:
    require(sha(REPO / row['source']) == row['sha256'], f'stale PPTX export: {row["source"]}')
review = json.loads((FIG / 'visual_review.json').read_text())
require(review['reviewed_figures'] == ['boot', 'uart', 'dma', 'ara'], 'visual review incomplete')
for name, expected in review['artifacts'].items():
    require(sha(REPO / name) == expected, f'visual review input changed: {name}')

initial = json.loads((ROOT / 'evidence/input.json').read_text())
protected = {name: sha(REPO / name) == expected for name, expected in initial['protected'].items()
             if name != 'docs_codex/software/README.md'}
# Shared inputs may be edited concurrently. Report drift; never overwrite them.
# None of these files is a write target of this task.
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
require(head == sources['head'], 'HEAD changed')
for p in list((ROOT / 'content').glob('*.html')) + list((ROOT / 'scripts').glob('*')):
    if p.is_file():
        require(not any(line.rstrip() != line for line in p.read_text().splitlines()), f'trailing whitespace: {p}')

report = dict(status='pass' if not errors else 'fail', errors=errors,
              html_markdown_pairs=len(generated), local_link_occurrences=count,
              referenced_source_files=len(sources['files']), build_artifacts=len(builds['artifacts']),
              browser_viewports=len(browser['pages']), svg_figures=len(browser['figures']),
              preexisting_protected_inputs=protected,
              external_input_changes=[name for name, same in protected.items() if not same],
              external_input_note='Observed concurrent changes outside task write scope; original hashes retained in input.json. No restoration or baseline refresh performed.',
              authorized_existing_edit='docs_codex/software/README.md: topic navigation',
              target_simulation=False, fpga_test=False, office_application_test=False)
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(bool(errors))
