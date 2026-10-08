#!/usr/bin/env python3
"""Read-only comparison against this turn's input; writes only its own new report."""
from pathlib import Path
import hashlib, json, re, subprocess

repo = Path(__file__).resolve().parents[3]
site = repo / 'docs_codex/learning'
evidence = site / 'evidence/system-implementation-20261008'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((evidence / 'input.json').read_text())
allowed = {
    'docs_codex/00_README.md', 'docs_codex/PROJECT_STATE.md',
    'docs_codex/AGENT_TASKS.md', 'docs_codex/handoffs/README.md',
    'docs_codex/03-08_Topic_Readiness_2026-10-08.md',
    'docs_codex/L01_System_Textbook_Revision_Plan_2026-10-08.md',
    'docs_codex/L01_Next_Tasks_Prompts_2026-10-08.md',
    'docs_codex/software/README.md', 'docs_codex/learning/README.md',
    'docs_codex/learning/OFFICIAL_SOURCES.md',
}
allowed_scripts = {'build_site.py', 'pages.json', 'check_structure.py',
                   'preview_structure_site.py', 'build_research_figures.py'}
changed, preserved = [], []
for name, expected in baseline['files'].items():
    p = repo / name
    assert p.is_file(), ('input deleted', name)
    if sha(p) == expected:
        preserved.append(name)
        continue
    relative = p.relative_to(site) if p.is_relative_to(site) else None
    permitted = name in allowed or (relative is not None and (
        (relative.parent == Path('.') and p.suffix == '.html') or
        (relative.parent == Path('content') and p.suffix == '.html' and p.name != 'registers.html') or
        (relative.parent == Path('scripts') and p.name in allowed_scripts)))
    assert permitted, ('protected input changed', name)
    changed.append({'path': name, 'before': expected, 'after': sha(p)})

old_ids = 0
for old in (evidence / 'before-content').glob('*.html'):
    previous = set(re.findall(r'\bid="([^"]+)"', old.read_text()))
    current = set(re.findall(r'\bid="([^"]+)"', (site / 'content' / old.name).read_text()))
    assert previous <= current, ('old semantic IDs removed', old.name, sorted(previous-current))
    old_ids += len(previous)

sources = {}
for name, key in [('coordinator/sources.json', 'files'), ('software/sources.json', 'files'),
                  ('os/sources.json', 'local_sources'), ('asic/input.json', 'files')]:
    items = json.loads((evidence/name).read_text())[key]
    for path, value in items.items():
        if path.startswith('docs_codex/'):
            continue
        digest = value['sha256'] if isinstance(value, dict) else value
        assert sha(repo/path) == digest, ('source changed', name, path)
        sources[path] = digest

status = subprocess.check_output(['git', 'status', '--short'], cwd=repo, text=True)
outside = [line for line in status.splitlines() if not line[3:].startswith('docs_codex/')]
assert not outside, ('changes outside docs_codex', outside)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=repo, text=True).strip()
assert head == baseline['head'] and branch == baseline['branch']
diff = subprocess.run(['git', 'diff', '--check'], cwd=repo, text=True, capture_output=True)
assert diff.returncode == 0, diff.stdout + diff.stderr
record = {
    'head': head, 'branch': branch, 'input_files': len(baseline['files']),
    'preserved_files': len(preserved), 'changed_input_files': changed,
    'old_content_ids_preserved': old_ids, 'unchanged_targeted_sources': sources,
    'status': status, 'diff_check_exit': diff.returncode,
    'visual_samples': ['preview-mobile-linux.png', 'preview-asic-memory.png', 'preview-runtime.png'],
    'scope': 'Documentation only; no target execution or human reader test.',
}
out = Path(__file__).parent / 'protection.json'
assert not out.exists(), 'Choose a new evidence path; do not overwrite a prior check.'
out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(f'PASS {len(preserved)}/{len(baseline["files"])} input files unchanged; {len(changed)} authorized changes')
print(f'PASS all {old_ids} old content IDs preserved; {len(sources)} targeted source hashes unchanged')
print('PASS unchanged branch/HEAD; no changes outside docs_codex; git diff --check exit 0')
