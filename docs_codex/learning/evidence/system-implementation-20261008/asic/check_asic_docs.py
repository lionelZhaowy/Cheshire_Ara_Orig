"""Read-only, bounded author check. Output is stdout; do not overwrite old logs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re
import subprocess

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[4]
LEARNING = ROOT / 'docs_codex/learning'
SLUGS = ['clocks', 'reset', 'power', 'future', 'asic-memory', 'cdc-rdc', 'physical-interfaces', 'timing-physical', 'manufacturing-test', 'silicon-bringup']
DOCS = ['docs_codex/L01_ASIC_Implementation_2026-10-08.md', 'docs_codex/P01_ASIC_Adaptation_and_Evidence.md', 'docs_codex/handoffs/2026-10-08_L01_asic_mechanisms_implementation.md']

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.headings = [], [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in ('h2', 'h3'):
            self.headings.append(attrs.get('id'))
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

def page(path):
    result = Page()
    result.feed(path.read_text())
    return result

def check_link(href, base):
    u = urlsplit(href)
    if u.scheme or not u.path:
        return False
    target = (base / unquote(u.path)).resolve()
    if target.parent == LEARNING and target.suffix == '.html':
        content = LEARNING / 'content' / target.name
        if content.exists():
            target = content
    assert target.exists(), (base, href)
    if u.fragment and target.suffix == '.html':
        assert unquote(u.fragment) in page(target).ids, (target, href)
    return True

count = 0
paths = []
for slug in SLUGS:
    path = LEARNING / 'content' / (slug + '.html')
    paths.append(str(path))
    content = page(path)
    assert len(content.ids) == len(set(content.ids)), slug
    assert all(content.headings), slug
    before = EVIDENCE / (slug + '-before.html')
    if before.exists():
        assert set(page(before).ids) <= set(content.ids), slug
    count += sum(check_link(href, LEARNING) for href in content.links)
print(f'PASS: {len(SLUGS)} pages, unique semantic IDs, all prior IDs retained; {count} local HTML links/resources')
md_count = 0
for rel in DOCS:
    p = ROOT / rel
    assert p.exists(), rel
    for href in re.findall(r'\]\(([^\s)]+)\)', p.read_text()):
        md_count += check_link(href, p.parent)
    assert all(line == line.rstrip() for line in p.read_text().splitlines()), rel
print(f'PASS: {len(DOCS)} Markdown deliverables, {md_count} local links, no trailing whitespace')
source_count = 0
for rel, sha in json.loads((EVIDENCE / 'input.json').read_text())['files'].items():
    if rel.startswith('docs_codex/learning/content/'):
        continue
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, rel
    source_count += 1
print(f'PASS: {source_count} protected source hashes unchanged')
for vlen in (2048, 4096):
    size = vlen * 32 // 8
    lane, bank = size // 2, size // 2 // 8
    assert size == 2 * 8 * bank
    print(f'VRF arithmetic: VLEN={vlen} bit, total={size} byte, lane={lane} byte, bank={bank} byte ({bank // 8} x 64 bit)')
result = subprocess.run(['git', 'diff', '--check', '--', *paths, *DOCS], cwd=ROOT, capture_output=True, text=True)
print(f'git diff --check: rc={result.returncode}; {result.stdout}{result.stderr}')
assert result.returncode == 0
print('Not run: generation/browser (coordinator), target build/simulation/synthesis/CDC/RDC/STA/DFT/board/silicon tests.')
