"""Export active A variant through the native arrow backend. Never overwrite a deck."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parent
SKILLS=Path.home()/'.codex/skills'
for variant in ['A']:
 sources=sorted((ROOT/variant).glob('*.svg'));out=ROOT/variant/'editable'
 command=[sys.executable,str(SKILLS/'svg-pptx-diagrams-native/scripts/run.py'),'--input',*map(str,sources),'--out-dir',str(out),'--aspect','source']
 with (ROOT/'evidence'/('export_'+variant+'.log')).open('w') as log:
  result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise SystemExit(f'{variant}: export failed; see evidence/export_{variant}.log')
 print(variant,'native deck exported;',len(sources),'slides')
