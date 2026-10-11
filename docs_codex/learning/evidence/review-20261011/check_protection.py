#!/usr/bin/env python3
"""Read-only preservation check for this review; write a new report directory."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys
from collections import Counter
BASE=Path(__file__).resolve().parent
REPO=BASE.parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(REPO/'docs_codex/learning/scripts'))
from build_site import content_bodies
parser=argparse.ArgumentParser();parser.add_argument('--out-dir',type=Path,required=True);args=parser.parse_args()
args.out_dir.mkdir(parents=True,exist_ok=False)
baseline=json.loads((BASE/'input.json').read_text())
report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'protected_files':len(baseline['protected']),'pages':{},'not_run':['software build','RTL compile/simulation','synthesis','board']}
try:
 for name,digest in baseline['protected'].items():
  assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==digest,('original work changed',name)
 current=content_bodies()
 for name,before in baseline['content_at_head'].items():
  if '/content/' not in name:continue
  slug=Path(name).stem;after=current[slug]
  ids=set(re.findall(r'\bid="([^"]+)"',before));new=set(re.findall(r'\bid="([^"]+)"',after))
  assert ids<=new,(slug,'lost source anchors',ids-new)
  images=lambda s:Counter(re.findall(r'<img[^>]+src="([^"]+)"',s))
  assert images(before)==images(after),(slug,'image paths changed')
  code=lambda s:Counter(re.findall(r'<pre\b[^>]*>(.*?)</pre>',s,re.S))
  if slug=='vector':
   # Reviewed clarification: commands are unchanged; make the required output
   # directory explicit rather than imply any kernel object has this name.
   before=before.replace('# 具体内核按 build_journey.sh 编译；逐个对象检查能力边界。','# LEARN_RVV 必须是实验 E 本次汇编构建的输出目录。')
  assert code(before)==code(after),(slug,'code example changed')
  report['pages'][slug]={'old_ids':len(ids),'new_ids':len(new),'images':sum(images(after).values()),'code_blocks':sum(code(after).values())}
 for filename in ['CHESHIRE.md','CVA6.md']:
  path='docs_codex/configuration/'+filename
  before=subprocess.check_output(['git','show',baseline['head']+':'+path],cwd=REPO,text=True)
  after=(REPO/path).read_text()
  fields=lambda s:Counter(re.findall(r'^\| `([^`]+)`',s,re.M))
  assert fields(before)==fields(after),(filename,'parameter identifiers lost')
  report[filename]={'table_field_entries':sum(fields(after).values()),'identifiers_preserved':True}
 changed=subprocess.check_output(['git','diff','--name-only'],cwd=REPO,text=True).splitlines()
 assert all(n=='README.md' or n.startswith('docs_codex/') for n in changed),'production source changed'
 immutable=['docs_codex/learning_backup/','docs_codex/learning/figures/','docs_codex/learning/figure_archive/','docs_codex/learning/examples/','docs_codex/diagrams/']
 assert not any(n.startswith(tuple(immutable)) for n in changed),'historical figure/example changed'
 assert not any(n.startswith('docs_codex/learning/assets/') and not n.endswith(('site.css','site.js')) for n in changed),'figure asset changed'
 assert not any(n.startswith('docs_codex/learning/evidence/') and '/review-20261011/' not in n for n in changed),'historical evidence changed'
 report['result']='PASS'
except BaseException as e:
 report['result']='FAIL';report['error']=repr(e)
 (args.out_dir/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise
(args.out_dir/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS',report['protected_files'],'existing work files;',len(report['pages']),'source pages; all old IDs/images/code and parameter identifiers; production/history unchanged')
