#!/usr/bin/env python3
"""Validate this documentation update without rewriting historical evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

E = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]
data = json.loads((E / 'input.json').read_text())
issues = []
links = 0

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for name, digest in data['before'].items():
    if sha(E / 'before' / name) != digest:
        issues.append('Backup changed: ' + name)
    p = ROOT / name
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', p.read_text()):
        if target.startswith(('http:', 'https:', '#')):
            continue
        local = (p.parent / unquote(target.split('#', 1)[0])).resolve()
        # This report is created at the end of this invocation.
        if local != E / 'validation.json' and not local.exists():
            issues.append(f'Missing local link: {name}: {target}')
        links += 1
    for n, line in enumerate(p.read_text().splitlines(), 1):
        if line.rstrip() != line:
            issues.append(f'Trailing whitespace: {name}:{n}')
for name, digest in data['protected'].items():
    if sha(ROOT / name) != digest:
        issues.append('Protected file changed: ' + name)
main_name = 'docs_codex/engineering/DDR_GB_Coherence_Design.md'
main = (ROOT / main_name).read_text()
before = (E / 'before' / main_name).read_text()
chapters = re.findall(r'^## (\d+)\.', main, re.M)
if chapters != list(map(str, range(1, 9))):
    issues.append('Main chapter structure changed')
if re.findall(r'^!\[.*', main, re.M) != re.findall(r'^!\[.*', before, re.M):
    issues.append('Main figure references changed')
if re.findall(r'```c\n.*?\n```', main, re.S) != re.findall(r'```c\n.*?\n```', before, re.S):
    issues.append('Pseudocode changed')
qa = (ROOT / 'docs_codex/maintenance/L01/reviews/ddr_gb_coherence_review_qa.md').read_text()
appendix = qa.split('## 8. 独立评审原文\n', 1)[1]
if hashlib.sha256(appendix.encode()).hexdigest() != data['review_appendix_sha256']:
    issues.append('Original review appendix changed')
diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, text=True, capture_output=True)
if diff.returncode:
    issues.append(diff.stdout + diff.stderr)
result = {
    'date': '2026-10-16', 'status': 'pass' if not issues else 'fail',
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'documents_checked': len(data['before']), 'local_links_checked': links,
    'protected_files_checked': len(data['protected']), 'backups_checked': len(data['before']),
    'main_chapters': chapters, 'review_appendix_unchanged': 'Original review appendix changed' not in issues,
    'git_diff_check_exit_code': diff.returncode, 'issues': issues,
    'output_sha256': {n: sha(ROOT / n) for n in data['before']},
    'browser_or_office_tested': False, 'hardware_execution': False,
}
(E / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'output_sha256'}, ensure_ascii=False, indent=2))
raise SystemExit(bool(issues))
