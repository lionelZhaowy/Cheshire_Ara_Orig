import sys,json,tarfile,hashlib,io,stat
from pathlib import Path
phase=sys.argv[1];assert phase in ('reference','formal')
R=Path('/home/zhaowy24/CheshireAraPULP' if phase=='reference' else '/home/zhaowy24/CheshireAra')
B=Path('/home/zhaowy24/CheshireAra_maintenance')/('reference_sync_20261023' if phase=='reference' else 'formal_sync_20261024')
selected={}
def add(p,n):
 if p.is_file():selected[n]=p
for p in B.rglob('*'):
 rel=p.relative_to(B)
 if any(x.startswith(('final_restore_check','restore_check')) for x in rel.parts[:-1]):continue
 if p.suffix in ('.bundle','.gz','.tar') or p.name=='evidence_manifest.json':continue
 add(p,'backup/'+str(rel))
work=R/('work/reference_sync_20261023' if phase=='reference' else 'sim/work/p1_p5_20261024')
for p in work.rglob('*'):
 if p.name in ('commands.json','command.json','source_manifest.json','result.json') or (p.suffix=='.log' and (p.name.startswith(('build','compile','entry','simulate','elaborate')))):
  add(p,'project/'+str(p.relative_to(R)))
if phase=='reference':
 for run in (R/'work/runs').glob('sync_*'):
  for name in ('result.json','simulate.log'):add(run/name,'project/'+str((run/name).relative_to(R)))
for out in (R/'sw/build').glob('reference_sync*' if phase=='reference' else 'p1_p5_20261024'):
 for name in ('build.log','commands.json'):add(out/name,'project/'+str((out/name).relative_to(R)))
for p in Path('/tmp').glob('e01_*'):
 if p.is_file() and p.suffix in ('.py','.json') and any(s in p.name for s in ('sync_reference','reference_extra','reference_finish','reference_recovery','reference_push','formal_prepare','formal_record','formal_test','archive_sync')):
  add(p,'execution_inputs/'+p.name)
manifest=[];archive=B/'validation_evidence.tar.gz';assert not archive.exists()
with tarfile.open(str(archive),'w:gz') as t:
 for n,p in sorted(selected.items()):
  blob=p.read_bytes();manifest.append({'name':n,'sha256':hashlib.sha256(blob).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode),'bytes':len(blob)})
  t.add(str(p),arcname=n,recursive=False)
 data=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('manifest.json');info.size=len(data);t.addfile(info,io.BytesIO(data))
result={'archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'data_members':len(manifest),'full_trace_policy':'Full CPU traces remain in original run directories; archive contains commands, summaries and simulator/build logs.'}
(B/'evidence_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
