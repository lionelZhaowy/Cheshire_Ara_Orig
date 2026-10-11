#!/usr/bin/env python3
"""Low-risk artifact/link and pre-existing-file protection checks."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[2]

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        for key in ('href', 'src'):
            if key in a: self.links.append(a[key])

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

errors = []
page = BASE / 'Architecture_Review_Report.html'
parser = Links(); parser.feed(page.read_text())
local_links = 0
for link in parser.links:
    u = urlsplit(link)
    if u.scheme or u.netloc: continue
    local_links += 1
    if u.path and not (BASE / unquote(u.path)).exists(): errors.append('missing link: '+link)
    if not u.path and u.fragment and unquote(u.fragment) not in parser.ids:
        errors.append('missing anchor: '+link)
svg_files = list((BASE/'figures').glob('*.svg'))
for p in svg_files:
    root = ET.parse(p).getroot()
    if not root.findall('.//{http://www.w3.org/2000/svg}text'): errors.append('no editable text: '+str(p))
    png = p.with_suffix('.png')
    if not png.is_file() or png.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n': errors.append('missing PNG: '+str(png))
initial = json.loads((BASE/'evidence/initial_worktree.json').read_text())
changed = []
for name, oldhash in initial['files'].items():
    path = REPO/name
    if not path.is_file() or sha(path) != oldhash: changed.append(name)
head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
if head != initial['head']: errors.append('HEAD changed')
status = subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True)
unexpected = []
initial_status = set((BASE/'evidence/initial_git_status.txt').read_text().splitlines())
allowed = ('docs_codex/reviews/2026-10-11_architecture/', 'docs_codex/PROJECT_STATE.md',
           'docs_codex/AGENT_TASKS.md', 'docs_codex/handoffs/AR_architecture_review.md')
for line in status.splitlines():
    if line not in initial_status and not line[3:].startswith(allowed): unexpected.append(line)
outside_docs = [x for x in unexpected if not x[3:].startswith('docs_codex/')]
if outside_docs: errors.append('unexpected changes outside documentation: '+str(outside_docs))
snapshot = json.loads((BASE/'evidence/source_snapshot.json').read_text())
source_changes = [name for name, value in snapshot['source_sha256'].items()
                  if not (REPO/name).is_file() or sha(REPO/name) != value]
if source_changes: errors.append('reviewed source changed: '+str(source_changes))
production_diff = subprocess.check_output(['git','diff','--name-only','--','hw','sw','target','.bender'],cwd=REPO,text=True).splitlines()
if production_diff: errors.append('production tracked diff: '+str(production_diff))
for p in BASE.rglob('*.md'):
    if p.read_text().count('```') % 2: errors.append('unbalanced fences: '+str(p))
record = {'head':head,'local_links_checked':local_links,'svg_png_pairs':len(svg_files),
          'protected_input_files':len(initial['files']),'changed_input_files':changed,
          'unexpected_worktree_changes':unexpected,'errors':errors,
          'reviewed_source_hashes_unchanged':not source_changes,
          'production_tracked_diff':production_diff,
          'input_protection_passed':not changed and not unexpected,
          'artifact_checks_passed':not errors,
          'worktree_observation':'Concurrent documentation/figure changes were observed and left untouched; this is not a claim that all input files remained byte-identical.',
          'scope':'Artifact checks only; no RTL, simulation, board, or signoff result.'}
(BASE/'evidence/artifact_checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['changed_input_files','unexpected_worktree_changes']},ensure_ascii=False,indent=2))
print('Concurrent changed input files:',len(changed),'additional status entries:',len(unexpected))
raise SystemExit(bool(errors))
