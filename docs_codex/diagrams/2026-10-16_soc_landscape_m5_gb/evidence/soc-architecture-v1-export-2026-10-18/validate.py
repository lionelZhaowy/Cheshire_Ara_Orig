"""Bounded delivery checks for v1 documentation/export; no engineering execution."""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote
import hashlib
import json
import re
import subprocess
from lxml import etree as E

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DIAGRAM = HERE.parents[1]
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
SVGNS = {'s': 'http://www.w3.org/2000/svg'}
report = {'date': '2026-10-18', 'scope': 'documentation and current v1 export only'}
failures = []

def check(name, condition, detail=None):
    report[name] = {'pass': bool(condition), 'detail': detail}
    if not condition:
        failures.append(name)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

initial = json.loads((HERE / 'input.json').read_text())
allowed = initial['allowed_existing_edits']
unexpected = [p for p, digest in initial['protected_sha256'].items()
              if p not in allowed and (not (ROOT / p).exists() or sha(ROOT / p) != digest)]
check('existing_file_protection', not unexpected,
      {'checked': len(initial['protected_sha256']) - len(allowed), 'unexpected': unexpected})
check('backup_matches_input', all(sha(HERE / 'before' / p) == initial['protected_sha256'][p]
                                 for p in allowed))
sources = json.loads((HERE / 'source-check.json').read_text())
check('targeted_source_protection', all(sha(ROOT / p) == digest for p, digest in sources.items()), len(sources))
check('head_unchanged', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == initial['head'])
check('branch_unchanged', subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == initial['branch'])
check('no_extraction_directory', not (ROOT / 'cheshire_ara_asic').exists())

deck = DIAGRAM / 'soc_landscape_m5_gb.pptx'
check('source_ppt_hash', sha(deck) == 'b19710ba3cf23a34c93745c381051c4da5b03cae735f9d2e895416120cf05e3a', sha(deck))
with ZipFile(deck) as z:
    check('ppt_zip_crc', z.testzip() is None)
    pres = E.fromstring(z.read('ppt/presentation.xml'))
    rels = {r.get('Id'): r.get('Target') for r in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    rid = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    pages = []
    for n, entry in enumerate(pres.find('p:sldIdLst', NS), 1):
        target = rels[entry.get(rid)]
        part = target.lstrip('/') if target.startswith('/') else 'ppt/' + target
        node = E.fromstring(z.read(part))
        pages.append((n, part, node))
    found = [(n, part) for n, part, node in pages if '(v1)' in ''.join(node.xpath('.//a:t/text()', namespaces=NS))]
    check('presentation_order', len(pages) == 9 and found == [(9, 'ppt/slides/slide9.xml')], found)
    slide = pages[8][2]
    elems = [s for s in slide.find('p:cSld/p:spTree', NS) if E.QName(s).localname in ('sp', 'cxnSp')]
    by_name = {s.find('.//p:cNvPr', NS).get('name'): s for s in elems}
    text_by_name = {name: ''.join(s.xpath('.//a:t/text()', namespaces=NS)) for name, s in by_name.items()}
    shape_ids = [s.find('.//p:cNvPr', NS).get('id') for s in elems]
    check('native_objects', len(elems) == 558 and len(set(shape_ids)) == len(elems)
          and not slide.findall('.//p:pic', NS), len(elems))
    expect = {1: 'PLL / 时钟复位', 2: 'DDRController', 3: 'DDRPHY', 4: 'LVDSRX',
              5: 'LVDSTX', 6: '帧写入DMA', 7: '帧输出DMA', 8: 'ROI 任务/ 调度',
              9: 'ISP', 10: 'NPU计算', 11: 'GB搬运', 12: 'GB管理',
              13: 'eMMC Host/ DMA', 14: '压缩公共控制', 15: '压缩器', 16: '解压器'}
    compact = lambda s: re.sub(r'\s+', '', s)
    actual = {i: ''.join(v for k, v in text_by_name.items() if k.startswith(f'config-C{i}-title-')) for i in expect}
    check('configuration_groups', all(compact(actual[i]) == compact(expect[i]) for i in expect), actual)
    line_checks = []
    for name, dashed in [('llc-f0', False), ('mover-f1', True), ('frame-f2', True), ('roi-f3-request', True)] + [(f'front-ddr-{i}', False) for i in range(4)]:
        s = by_name[name]
        ln = s.find('p:spPr/a:ln', NS)
        native_dashed = ln.find('a:custDash', NS) is not None
        ends = [ln.find('a:' + k, NS).get('type') for k in ('headEnd', 'tailEnd')]
        line_checks.append({'name': name, 'dashed': native_dashed, 'arrow_ends': ends,
                            'pass': native_dashed == dashed and ends == ['triangle', 'triangle']})
    check('eight_ddr_interfaces_styles', all(x['pass'] for x in line_checks), line_checks)

svg = E.parse(str(DIAGRAM / 'soc-architecture-v1.svg'))
native_text = compact(''.join(slide.xpath('.//a:t/text()', namespaces=NS)))
svg_text = compact(''.join(svg.xpath('//s:text/text()', namespaces=SVGNS)))
check('svg_all_text_from_ppt', native_text == svg_text)
check('svg_is_current_export', (DIAGRAM / 'soc-architecture-v1.svg').read_bytes() == (HERE / 'preview/slide-09.svg').read_bytes())
check('svg_editable_no_images', not svg.findall('.//s:image', SVGNS))
check('png_reproduced', (DIAGRAM / 'soc-architecture-v1.png').read_bytes() == (HERE / 'raster-recheck/soc-architecture-v1.png').read_bytes())
check('crops_reproduced', all((HERE / (name + '.png')).read_bytes() == (HERE / 'raster-recheck' / (name + '.png')).read_bytes()
                            for name in ['title-core', 'gb-capture', 'storage-roi', 'controls', 'xbar-emmc']))

def anchors(path):
    text = path.read_text()
    ids = set(re.findall(r'<a\s+id=["\']([^"\']+)', text))
    counts = {}
    for title in re.findall(r'^#{1,6}\s+(.+)', text, re.M):
        title = re.sub(r'[`*_]', '', title).strip().lower()
        slug = re.sub(r'[^\w\- ]', '', title).replace(' ', '-')
        n = counts.get(slug, 0)
        ids.add(slug if n == 0 else f'{slug}-{n}')
        counts[slug] = n + 1
    return ids

def link_errors(path, text):
    errors = []
    for target in re.findall(r'\[[^\]]*\]\(([^)\n]+)\)', re.sub(r'```.*?```', '', text, flags=re.S)):
        if re.match(r'https?://|mailto:', target):
            continue
        route, _, anchor = unquote(target.strip('<>')).partition('#')
        dest = (path.parent / route).resolve() if route else path
        if not dest.exists():
            errors.append(target)
        elif anchor and dest.suffix == '.md' and anchor not in anchors(dest):
            errors.append(target)
    return errors

master = ROOT / 'docs_codex/engineering/SoC_Architecture_v1_Master_Plan.md'
docs = [master, HERE / 'README.md'] + [ROOT / p for p in allowed]
new_errors = {}
inherited_errors = {}
for path in docs:
    errs = link_errors(path, path.read_text())
    rel = str(path.relative_to(ROOT))
    previous = link_errors(path, (HERE / 'before' / rel).read_text()) if rel in allowed else []
    introduced = [x for x in errs if x not in previous]
    if introduced:
        new_errors[rel] = introduced
    if previous:
        inherited_errors[rel] = previous
check('markdown_new_links_and_anchors', not new_errors, {'new_errors': new_errors, 'inherited_errors': inherited_errors})
text = master.read_text()
check('nine_required_sections', len(re.findall(r'^## [1-9]\. ', text, re.M)) == 9)
check('six_end_to_end_sections', all(f'### 4.{i} ' in text for i in range(2, 7)) and '第 6.2 节输入同步' in text,
      '4.2–4.6 cover five application flows; 6.2 / 8.3 cover cache, completion and recovery')
check('requirement_mapping', all(f'需求 {i}：' in text for i in range(1, 13)))
table_errors = []
for doc in docs:
    expected = None
    for n, line in enumerate(doc.read_text().splitlines(), 1):
        if line.startswith('|') and line.endswith('|'):
            cells = len(re.split(r'(?<!\\)\|', line))
            if expected is not None and cells != expected:
                table_errors.append((str(doc.relative_to(ROOT)), n, cells, expected))
            expected = cells
        else:
            expected = None
check('table_columns', not table_errors, table_errors)
changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
original_changed = [line[3:] for line in initial['status'].splitlines() if line.startswith(' M ')]
check('tracked_change_scope', not set(changed) - set(original_changed) - set(allowed), changed)
gitcheck = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, text=True, capture_output=True)
check('git_diff_check', gitcheck.returncode == 0, gitcheck.stdout + gitcheck.stderr)
check('new_markdown_whitespace', all(not re.search(r'[ \t]+$', line) for line in text.splitlines()))
report['visual_review'] = {'performed': True, 'reviewer': 'L01 author, no subagent',
    'views': ['whole v1', 'title-core', 'gb-capture', 'storage-roi', 'controls', 'xbar-emmc'],
    'method': 'view_image on final-PPT-derived PNG and crops; local substitute-font rendering',
    'office_tested': False, 'hardware_tested': False}
report['output_hashes'] = {str(p.relative_to(ROOT)): sha(p) for p in [master, DIAGRAM / 'soc-architecture-v1.svg', DIAGRAM / 'soc-architecture-v1.png']}
report['failures'] = failures
report['pass'] = not failures
(HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'pass': not failures, 'failures': failures, 'report': str((HERE / 'validation.json').relative_to(ROOT))}, ensure_ascii=False))
raise SystemExit(bool(failures))
