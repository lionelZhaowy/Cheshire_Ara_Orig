"""Unique, non-overwriting output directories for documentation checks."""
from pathlib import Path
import argparse,datetime,tempfile,json,subprocess,hashlib

def start_run(kind,extra=False):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,help='New directory; even an existing empty directory is rejected.')
    if extra:parser.add_argument('--check-generated',action='store_true',help='Generate in a temporary copy and compare; never regenerate the working tree.')
    args=parser.parse_args()
    if args.out_dir:
        out=args.out_dir.resolve()
        try:out.mkdir(parents=True,exist_ok=False)
        except FileExistsError:parser.error('Output directory already exists; choose a new path: '+str(out))
    else:out=Path(tempfile.mkdtemp(prefix='l01-'+kind+'-'))
    root=Path(__file__).resolve().parent.parent
    now=datetime.datetime.now().astimezone().isoformat()
    meta={'started_at':now,'kind':kind,'output':str(out),'site':str(root),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'worktree_status':subprocess.check_output(['git','status','--short'],cwd=root,text=True),'inputs':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['content','scripts','assets'] for p in sorted((root/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}}
    # Separate generated pages actually loaded by the browser from source inputs.
    meta['tested_html']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('*.html'))}
    (out/'run.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print('Report directory:',out,flush=True)
    return args,out,meta
