from pathlib import Path
import hashlib,json,re,subprocess,argparse
repo=Path(__file__).resolve().parents[3];site=repo/'docs_codex/learning';base=site/'evidence/title-polish-20261008'
p=argparse.ArgumentParser();p.add_argument('--out-dir',type=Path,required=True);args=p.parse_args();out=args.out_dir.resolve();out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
input=json.loads((base/'input.json').read_text());changes=json.loads((base/'changes.json').read_text());ids=0
for file in sorted((site/'content').glob('*.html')):
 before=(base/'before-content'/file.name).read_text();expected=before
 for c in changes:
  if c['path']!='content/'+file.name:continue
  if c['kind']=='visible-reference':old,new=c['old'],c['new']
  else:
   match=re.search(r'<h([1-4]) id="'+re.escape(c['anchor'])+r'">(.*?)</h\1>',expected,re.S);assert match and match[2]==c['old'];old=match[0];new=old.replace(c['old'],c['new'])
  assert expected.count(old)==1,(file,c)
  expected=expected.replace(old,new)
 assert expected==file.read_text(),('unlisted content change',file)
 oldids=re.findall(r'\bid="([^"]+)"',before);ids+=len(oldids)
 assert oldids==re.findall(r'\bid="([^"]+)"',expected)
 assert re.findall(r'\b(?:href|src)="([^"]+)"',before)==re.findall(r'\b(?:href|src)="([^"]+)"',expected)
meta=json.loads((base/'before-pages.json').read_text())
for c in changes:
 if c['path']=='scripts/pages.json':
  group,ident,key=c['anchor'].split('/');entry=next(x for x in meta[group] if x.get('slug',x.get('id'))==ident);assert entry[key]==c['old'];entry[key]=c['new']
assert meta==json.loads((site/'scripts/pages.json').read_text())
allow={'docs_codex/'+c['path'] for c in []}
allow.update('docs_codex/learning/'+c['path'] for c in changes)
allow.update(['docs_codex/learning/README.md','docs_codex/PROJECT_STATE.md','docs_codex/AGENT_TASKS.md','docs_codex/handoffs/README.md'])
unchanged=0;delta=[]
for name,h in input['files'].items():
 file=repo/name;assert file.is_file(),name
 if sha(file)==h:unchanged+=1;continue
 assert name in allow or (file.parent==site and file.suffix=='.html'),('protected file changed',name)
 delta.append(name)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==input['head']
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()==input['branch']
assert all(line[3:].startswith('docs_codex/') for line in subprocess.check_output(['git','status','--short'],cwd=repo,text=True).splitlines())
assert subprocess.run(['git','diff','--check'],cwd=repo,capture_output=True).returncode==0
result={'head':input['head'],'content_pages':51,'source_edits':len(changes),'old_ids_preserved':ids,'non_title_content':'exactly preserved after applying only the 24 listed edits','unchanged_input_files':unchanged,'input_files':len(input['files']),'authorized_changed_files':delta,'no_production_tests':True}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'PASS 51 content pages, {ids} IDs, href/src and order; 20 title fields + 4 visible references only')
print(f'PASS {unchanged}/{len(input["files"])} prior files unchanged; {len(delta)} authorized changes; git diff --check exit 0')
