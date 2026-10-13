"""Verify archived originals and the current documentation; never regenerate graphics.

Run from any directory with publication-figures' existing Python environment.
Use --output with a new path; historical reports are not overwritten.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse, hashlib, json, subprocess, tarfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output and args.output.exists():
    parser.error('Choose a new report path')
errors = []

def check(ok, *why):
    if not ok:
        errors.append(why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = json.loads((ROOT / 'manifest.json').read_text())
archives = {}
for name, digest in [(manifest['archive'], manifest['archive_sha256']),
                     (manifest['supplemental_archive'], manifest['supplemental_archive_sha256'])]:
    check(sha(ROOT / name) == digest, 'archive hash', name)
    archives[name] = tarfile.open(ROOT / name)
for entry in manifest['entries']:
    archive = archives[entry.get('archive', manifest['archive'])]
    original = archive.extractfile(entry['archive_member']).read()
    check(hashlib.sha256(original).hexdigest() == entry['sha256'], 'member hash', entry['path'])
    check(len(original) == entry['bytes'], 'member size', entry['path'])
    if entry['action'] in ('archive', 'remove_redundant'):
        check(not (REPO / entry['path']).exists(), 'retired artifact restored', entry['path'])
for name, digest in manifest['preserved_files'].items():
    p = REPO / name
    check(p.exists() and sha(p) == digest, 'preserved file changed', name)
for p in sorted((REPO / 'docs_codex/rtl_modules').glob('[0-9]*.md')):
    old = archives[manifest['archive']].extractfile(str(p.relative_to(REPO))).read().decode()
    expected = old.replace('[A/C 对比](../diagrams/2026-10-13_rtl_modules_native_c/index.html#',
                           '[A 图总览](../diagrams/2026-10-13_rtl_module_comparison/index.html#')
    expected = expected.replace('A/C 均以连续连线表达连接，编号只用于查表。',
                                '主图以连续连线表达连接，编号只用于查表。')
    check(p.read_text() == expected, 'technical chapter changed', p.name)
for archive in archives.values():
    archive.close()

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.targets = []; self.ids = set(); self.feed(text)
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d: self.ids.add(d['id'])
        for key in ('href', 'src'):
            if key in d: self.targets.append(d[key])

html_links = 0
for name in manifest['modified_html']:
    p = REPO / name
    for target in Page(p.read_text()).targets:
        u = urlsplit(target)
        if u.scheme or target.startswith('//'): continue
        q = (p.parent / unquote(u.path)).resolve() if u.path else p
        html_links += 1
        check(q.exists(), 'HTML target missing', name, target)
        if q.exists() and u.fragment and q.suffix == '.html':
            check(unquote(u.fragment) in Page(q.read_text()).ids, 'HTML anchor missing', name, target)

python = Path.home() / '.codex/skills/publication-figures/.venv/bin/python'
commands = [
    ['python3', '-B', 'docs_codex/learning/scripts/check_site.py'],
    [str(python), '-B', 'docs_codex/diagrams/2026-10-13_rtl_module_comparison/verify_a.py'],
    ['git', 'diff', '--check'],
]
results = []
for command in commands:
    result = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
    results.append(dict(command=command, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr))
    check(result.returncode == 0, 'command failed', command)
protected_diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', '.', ':!docs_codex'], cwd=REPO, text=True).splitlines()
check(not protected_diff, 'non-document changes', protected_diff)
report = dict(date='2026-10-13', input_head=manifest['input_head'],
              archived_files=sum(e['action'] == 'archive' for e in manifest['entries']),
              redundant_files_removed=sum(e['action'] == 'remove_redundant' for e in manifest['entries']),
              archive_members_verified=len(manifest['entries']),
              preserved_files_verified=len(manifest['preserved_files']),
              chapter_content_comparisons=21, modified_html_links=html_links,
              non_document_changes=protected_diff, commands=results, errors=errors,
              rtl_simulated=False, board_tested=False, office_tested=False)
text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
if args.output:
    with args.output.open('x') as stream: stream.write(text)
print(text)
raise SystemExit(bool(errors))
