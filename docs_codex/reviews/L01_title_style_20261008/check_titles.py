#!/usr/bin/env python3
"""Validate only-title edits against the immutable title-phase input snapshot."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from collections import Counter

repo = Path(__file__).resolve().parents[3]
out = Path(__file__).parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out-dir', type=Path, help='A new, non-existing report directory; never overwrite evidence.')
args = parser.parse_args()
report_out = args.out_dir.resolve() if args.out_dir else out
if args.out_dir:
    report_out.mkdir(parents=True, exist_ok=False)
site = repo / 'docs_codex/learning'
baseline_dir = site / 'evidence/title-style-20261008'
baseline = json.loads((baseline_dir/'input.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
heading = re.compile(r'<h([1-4]) id="([^"]+)">(.*?)</h\1>', re.S)
goal = re.compile(r'(<div class="goals">\s*<strong>)(.*?)(</strong>)', re.S)
references = json.loads((out/'root-references.json').read_text())
reasons = {}
for name, key in [('root.json', None), ('software.json', 'changes'),
                  ('os-vector.json', 'entries'), ('asic.json', 'changes')]:
    data = json.loads((out/name).read_text())
    for row in data[key] if key else data:
        reasons[(row.get('path'), row.get('anchor'))] = row.get('reason', '准确表述本节技术对象及适用范围')

inventory, body_protection = [], []
for p in sorted((site/'content').glob('*.html')):
    relative = str(p.relative_to(repo))
    before = (baseline_dir/'before-content'/p.name).read_text()
    after = p.read_text()
    old_heads, new_heads = list(heading.finditer(before)), list(heading.finditer(after))
    assert [(x[1], x[2]) for x in old_heads] == [(x[1], x[2]) for x in new_heads], relative
    for a, b in zip(old_heads, new_heads):
        inventory.append({'path': relative, 'anchor': a[2], 'kind': 'H'+a[1],
                          'old': a[3], 'new': b[3], 'changed': a[3] != b[3],
                          'reason': reasons.get((relative, a[2]), '原有技术主题符合规范，保留' if a[3]==b[3] else '正式技术主题；范围与正文一致')})
    a, b = goal.search(before), goal.search(after)
    assert bool(a) == bool(b)
    if a:
        inventory.append({'path': relative, 'anchor': 'goals/strong', 'kind': 'entry-label',
                          'old': a[2], 'new': b[2], 'changed': a[2]!=b[2],
                          'reason': '正式入口标签；保留或改为技术主题，任务正文不变'})
    reverted = after
    for ref in references:
        if ref['path'] == relative:
            assert reverted.count(ref['new']) == ref['count'], ('reference count', ref)
            reverted = reverted.replace(ref['new'], ref['old'])
    mask = lambda s: goal.sub(lambda m: m[1]+'__FORMAL_ENTRY__'+m[3],
                              heading.sub(lambda m: f'<h{m[1]} id="{m[2]}">__TITLE__</h{m[1]}>', s))
    assert mask(before) == mask(reverted), ('non-title content changed', relative)
    assert re.findall(r'\bid="([^"]+)"', before) == re.findall(r'\bid="([^"]+)"', after)
    assert re.findall(r'\b(?:href|src)="([^"]+)"', before) == re.findall(r'\b(?:href|src)="([^"]+)"', after)
    body_protection.append({'path': relative, 'headings': len(old_heads),
                            'non_title_content': 'byte-identical after listed title-reference normalization',
                            'before_sha256': hashlib.sha256(before.encode()).hexdigest(), 'after_sha256': sha(p)})

before_meta = json.loads((baseline_dir/'before-pages.json').read_text())
after_meta = json.loads((site/'scripts/pages.json').read_text())
for group, identity, fields in [('parts', 'id', ['title']), ('pages', 'slug', ['title', 'subtitle'])]:
    assert len(before_meta[group]) == len(after_meta[group])
    for a, b in zip(before_meta[group], after_meta[group]):
        assert {k:v for k,v in a.items() if k not in fields} == {k:v for k,v in b.items() if k not in fields}
        for field in fields:
            ident = f'{group}/{a[identity]}/{field}'
            inventory.append({'path': 'docs_codex/learning/scripts/pages.json', 'anchor': ident,
                              'kind': ('part-' if group=='parts' else 'page-')+field,
                              'old': a[field], 'new': b[field], 'changed': a[field]!=b[field],
                              'reason': reasons.get(('docs_codex/learning/scripts/pages.json', ident), '规范技术标题/副标题保留')})

candidate_pattern = re.compile(r'为什么|为何|如何|怎样|什么|是否|哪些|哪里|多少|先.*再|跟随|跟读|走一遍|讲完整|可解释的|读懂|这笔|这条|同一轮|让.*|把.*')
candidates = [r for r in inventory if candidate_pattern.search(r['new'])]
assert [(r['path'],r['anchor'],r['new']) for r in candidates] == [
    ('docs_codex/learning/content/rtos.html', 'tick-and-event', '时钟节拍、主动让出与设备事件')]
# “主动让出” is the technical action yield, not a teaching instruction.

allowed_files = {'docs_codex/learning/scripts/pages.json', 'docs_codex/learning/README.md',
                 'docs_codex/learning/scripts/build_registers.py', 'docs_codex/learning/scripts/check_structure.py',
                 'docs_codex/PROJECT_STATE.md', 'docs_codex/AGENT_TASKS.md', 'docs_codex/00_README.md',
                 'docs_codex/handoffs/README.md', 'docs_codex/L01_System_Textbook_Implementation_2026-10-08.md'}
preserved, changed = [], []
for name, digest in baseline['files'].items():
    p = repo/name
    assert p.is_file(), ('input file deleted', name)
    if sha(p) == digest:
        preserved.append(name)
    else:
        rel = p.relative_to(site) if p.is_relative_to(site) else None
        allowed = name in allowed_files or (rel is not None and p.suffix == '.html' and rel.parent in [Path('.'),Path('content')])
        assert allowed, ('protected file changed', name)
        changed.append(name)

assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip() == baseline['head']
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip() == baseline['branch']
status = subprocess.check_output(['git','status','--short'],cwd=repo,text=True)
assert all(line[3:].startswith('docs_codex/') for line in status.splitlines()), status
assert subprocess.run(['git','diff','--check'],cwd=repo,capture_output=True).returncode == 0

counts = Counter(r['kind'] for r in inventory if r['changed'])
record = {'input_head': baseline['head'], 'pages': len(body_protection), 'inventory_count': len(inventory),
          'changed_count': sum(counts.values()), 'changed_by_kind': dict(counts),
          'input_files': len(baseline['files']), 'unchanged_input_files': len(preserved),
          'changed_input_paths': changed, 'body_protection': body_protection,
          'candidate_exceptions': [{'title': candidates[0]['new'], 'reason': '主动让出为yield技术用语，人工复核保留'}],
          'references': references, 'diff_check_exit': 0,
          'not_run': 'target build, simulation, synthesis, board, new technical audit'}
for name,data in [('inventory.json',inventory),('check-result.json',record)]:
    assert not (report_out/name).exists(), 'Do not overwrite an earlier check; use --out-dir for a new run.'
    (report_out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(f'PASS {len(inventory)} title/subtitle/entry fields; {sum(counts.values())} changes: {dict(counts)}')
print(f'PASS {len(body_protection)} pages: non-title content, IDs, references and order preserved')
print(f'PASS {len(preserved)}/{len(baseline["files"])} prior files unchanged; all remaining edits authorized')
print('PASS fixed structure/slugs/migrations; keyword candidate manually retained; git diff --check exit 0')
