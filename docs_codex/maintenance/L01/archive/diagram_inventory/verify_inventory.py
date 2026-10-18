"""Read-only diagram inventory/link/migration validation. Does not render diagrams."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse, hashlib, json, re, sys, unicodedata, tarfile

ROOT = Path(__file__).resolve().parents[5]
ARCHIVE = Path(__file__).resolve().parent
D = ROOT / 'docs_codex/diagrams'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output and args.output.exists():
    parser.error('Use a new report path')
manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
errors = []
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok, *why):
    if not ok: errors.append(why)

def snapshot(p):
    return any(x == 'evidence' or x.endswith('_evidence') or x == 'before' or x.startswith('before-') or x == 'skill' for x in p.parts)

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.targets = []; self.ids = set(); self.base = None; self.feed(text)
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'base':
            self.base = d.get('href'); return
        if 'id' in d: self.ids.add(d['id'])
        if tag == 'a' and 'name' in d: self.ids.add(d['name'])
        for key in ('href', 'src'):
            if d.get(key): self.targets.append(d[key])

def md_ids(text):
    ids = Page(text).ids
    seen = {}
    for title in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        title = re.sub(r'<[^>]+>', '', title).lower().replace('`', '')
        slug = ''.join(c for c in title if c in ' _-' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')
        n = seen.get(slug, 0); seen[slug] = n+1
        ids.add(slug+(f'-{n}' if n else ''))
    return ids

links = 0; diagram_targets = 0; bad_links = []; checked_pages = []
cache = {}
def check_link(p, target, base):
    global links, diagram_targets
    u = urlsplit(target)
    if u.scheme or target.startswith('//'): return
    q = (base / unquote(u.path)).resolve() if u.path else p
    links += 1
    if q.is_relative_to(D): diagram_targets += 1
    if not q.exists(): bad_links.append((str(p.relative_to(ROOT)), target)); return
    if not u.fragment or not q.is_file(): return
    fragment = unquote(u.fragment)
    if re.fullmatch(r'L[1-9][0-9]*', fragment):
        if int(fragment[1:]) > len(q.read_text().splitlines()): bad_links.append((str(p.relative_to(ROOT)), target))
    elif q.suffix in ('.md', '.html'):
        if q not in cache:
            cache[q] = md_ids(q.read_text()) if q.suffix == '.md' else Page(q.read_text()).ids
        if fragment not in cache[q]: bad_links.append((str(p.relative_to(ROOT)), target))

# Check all diagram Markdown/HTML, formal Markdown links, and the changed topic HTML.
changed = {item['file'] for item in manifest['link_changes']}
for p in (ROOT/'docs_codex').rglob('*'):
    if not p.is_file() or p.suffix not in ('.md', '.html') or snapshot(p): continue
    if p.is_relative_to(ROOT/'docs_codex/maintenance') and not p.is_relative_to(ARCHIVE) and str(p.relative_to(ROOT)) not in changed: continue
    if p.suffix == '.html' and not p.is_relative_to(D) and str(p.relative_to(ROOT)) not in changed: continue
    text = p.read_text()
    if p.suffix == '.md':
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        text = re.sub(r'`[^`]*`', '', text)
        targets = re.findall(r'\]\(([^\n)]+)\)', text)
    else: targets = []
    page = Page(text)
    targets += page.targets
    base = p.parent.parent if p.parent.name == 'content' and p.suffix == '.html' else p.parent
    if page.base: base = (base / unquote(page.base)).resolve()
    for target in targets: check_link(p, target, base)
    checked_pages.append(str(p.relative_to(ROOT)))
check(not bad_links, 'local links/anchors', bad_links)

artifacts = []; evidence = []; changed_text = []
for item in manifest['original_diagram_files']:
    p = ROOT / item['after']
    check(p.is_file(), 'missing moved/retained file', item['after'])
    if not p.is_file(): continue
    same = sha(p) == item['sha256_before']
    if p.suffix.lower() in ('.png', '.svg', '.pptx', '.pdf', '.jpg', '.jpeg', '.webp'):
        artifacts.append(item['after']); check(same, 'visual artifact changed', item['after'])
    if snapshot(Path(item['before'])):
        evidence.append(item['after']); check(same, 'evidence/snapshot changed', item['after'])
    if not same: changed_text.append(item['after'])
check(sha(ARCHIVE/manifest['backup']) == manifest['backup_sha256'], 'backup SHA')
with tarfile.open(ARCHIVE/manifest['backup']) as archive:
    for member in archive:
        if member.isfile(): archive.extractfile(member).read()

# Content templates must still reproduce exactly the edited HTML and Markdown pages.
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'docs_codex/software/interfaces/scripts'))
from build import rendered
pairs = 0
for slug, html, md in rendered():
    base = ROOT/'docs_codex/software/interfaces'
    check((base/(slug+'.html')).read_text() == html, 'HTML generation drift', slug)
    check((base/'markdown'/(slug+'.md')).read_text() == md, 'Markdown generation drift', slug)
    pairs += 1
report = dict(date='2026-10-18', input_head=manifest['input_head'],
              restored_directories=manifest['restored_directories'], archived_directories=manifest['archived_directories'],
              checked_pages=len(checked_pages), local_links=links, diagram_link_occurrences=diagram_targets,
              unchanged_visual_artifacts=len(artifacts), unchanged_evidence_files=len(evidence),
              checked_initial_files=len(manifest['original_diagram_files']), changed_text_files=changed_text,
              software_html_markdown_pairs=pairs, errors=errors,
              graphics_redrawn=False, office_tested=False, rtl_simulated=False)
encoded = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
if args.output:
    with args.output.open('x') as f: f.write(encoded)
print(encoded)
raise SystemExit(bool(errors))
