#!/usr/bin/env python3
"""Check this Markdown revision; preserve previous figure/browser evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

EVIDENCE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]
inputs = json.loads((EVIDENCE / 'input.json').read_text())
names = list(inputs['before']) + [
    'docs_codex/engineering/DDR_Supplier_Coherence_Questions.md',
    'docs_codex/maintenance/L01/reviews/ddr_gb_coherence_review_qa.md',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


issues = []
links = 0
for name in names:
    path = ROOT / name
    body = path.read_text()
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', body):
        if target.startswith(('http://', 'https://', '#')):
            continue
        local = unquote(target.split('#', 1)[0])
        if not (path.parent / local).exists():
            issues.append(f'Missing link in {name}: {target}')
        links += 1
    for number, line in enumerate(body.splitlines(), 1):
        if line.rstrip() != line:
            issues.append(f'Trailing whitespace: {name}:{number}')

for name, digest in inputs['protected'].items():
    if sha(ROOT / name) != digest:
        issues.append(f'Protected file changed: {name}')
for name, digest in inputs['before'].items():
    if sha(EVIDENCE / 'before' / name) != digest:
        issues.append(f'Backup changed: {name}')

main = (ROOT / names[0]).read_text()
chapters = re.findall(r'^## (\d+)\.', main, re.M)
if chapters != list(map(str, range(1, 9))):
    issues.append('Main document no longer has exactly chapters 1–8')
if len(re.findall(r'^!\[', main, re.M)) != 3:
    issues.append('Main document no longer has three images')
code = re.search(r'```c\n(.*?)\n```', main, re.S).group(1)
before = (EVIDENCE / 'before' / names[0]).read_text()
if code != re.search(r'```c\n(.*?)\n```', before, re.S).group(1):
    issues.append('Conceptual pseudocode changed')

raw = (EVIDENCE / 'review_original.txt').read_text()
expected = re.sub(
    r'\]\(' + re.escape(str(ROOT)) + r'/([^\)]+)\)',
    lambda match: '](../../../../' + re.sub(r':\d+$', '', match[1]) + ')', raw)
expected = re.sub(r'^(#{1,4}) ', r'#\1 ', expected, flags=re.M)
qa = (ROOT / names[-1]).read_text()
if not qa.endswith(expected.rstrip() + '\n'):
    issues.append('Review appendix differs beyond stated link/heading normalization')
if sha(EVIDENCE / 'review_original.txt') != inputs['review_original_sha256']:
    issues.append('Original attachment bytes changed')

diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
if diff.returncode:
    issues.append(diff.stdout + diff.stderr)
result = {
    'date': '2026-10-16',
    'status': 'pass' if not issues else 'fail',
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'local_links_checked': links,
    'documents_checked': len(names),
    'protected_files_unchanged': len(inputs['protected']) if not issues else None,
    'backups_checked': len(inputs['before']),
    'main_chapters': chapters,
    'main_images': 3,
    'pseudocode_lines': len(code.splitlines()),
    'full_review_retained': not any('review' in issue.lower() or 'attachment' in issue.lower() for issue in issues),
    'git_diff_check': diff.returncode,
    'document_sha256': {name: sha(ROOT / name) for name in names},
    'browser_or_office_tested': False,
    'hardware_execution': False,
    'issues': issues,
}
(EVIDENCE / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items() if key != 'document_sha256'}, ensure_ascii=False, indent=2))
raise SystemExit(bool(issues))
