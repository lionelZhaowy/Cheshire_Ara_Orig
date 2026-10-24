import os,sys,json,re,subprocess,hashlib,time,shutil
from pathlib import Path
F=Path('/home/zhaowy24/CheshireAra');R=Path('/home/zhaowy24/CheshireAraPULP');B=Path('/home/zhaowy24/CheshireAra_maintenance/formal_sync_20261024');W=F/'sim/work/p1_p5_20261024';S=F/'sw/build/p1_p5_20261024'
plan=json.loads(Path('/tmp/e01_reference_extra_plan.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def compile(target):
 d=W/target;assert not d.exists(),d;d.parent.mkdir(parents=True,exist_ok=True)
 a=[str(F/'sim/scripts/compile.cheshire_soc.sh'),str(d),target];print('FORMAL_BUILD',target,flush=True)
 with (B/('compile_'+target+'.log')).open('w') as f:subprocess.run(a,cwd=str(F),stdout=f,stderr=subprocess.STDOUT,check=True)
 save(B/('compile_'+target+'.json'),{'cmd':a,'source_manifest_sha256':sha(d/'source_manifest.json')})
def run(name,artifact,extra=(),target='soc',spi=False,allow=0,limit=600):
 out=W/'runs'/name;assert not out.exists(),out;out.mkdir(parents=True)
 env=os.environ.copy();env.update(TARGET=target,BUILD_DIR=str(W/target),RUN_DIR=str(out),SIM_TIMEOUT=str(limit),BOOTMODE='2' if spi else '0',PRELMODE='1')
 env['JOB_FILE' if target.startswith('idma_') else ('IMAGE' if spi else 'BINARY')]=str(artifact)
 a=[str(F/'sim/scripts/start.cheshire_soc.sh')]+list(extra);print('FORMAL_RUN',name,flush=True)
 save(out/'command.json',{'cmd':a,'settings':{k:env[k] for k in ('TARGET','BUILD_DIR','RUN_DIR','SIM_TIMEOUT','BOOTMODE','PRELMODE')},'artifact':str(artifact)})
 with (out/'entry.log').open('w') as f:p=subprocess.run(a,cwd=str(F),env=env,stdout=f,stderr=subprocess.STDOUT)
 d=json.loads((out/'result.json').read_text());print(name,d['status'],d['target_rc'],d['simv_host_rc'],d['entry_host_rc'],flush=True);assert p.returncode==allow,(name,p.returncode)
 save(B/'results'/(name+'.json'),d)
 if allow==0:assert d['status']=='PASS'
 if name=='final_spi':assert d['target_rc']==0 and d['simv_host_rc']==0 and d['entry_host_rc']==2
 if name.startswith('negative_'):return
 ref=(R/'work/runs'/('sync_extra_'+name[6:] if name.startswith('extra_') else 'sync_'+name))
 rd=json.loads((ref/'result.json').read_text());assert [d[k] for k in ('status','target_rc','simv_host_rc','entry_host_rc')]==[rd[k] for k in ('status','target_rc','simv_host_rc','entry_host_rc')],name
 log=(out/'simulate.log').read_text(errors='replace');rlog=(ref/'simulate.log').read_text(errors='replace')
 uart=[x.strip() for x in re.findall(r'\[UART\]([^\n]*)',log)];ruart=[x.strip() for x in re.findall(r'\[UART\]([^\n]*)',rlog)]
 assert uart==ruart,(name,'UART output differs',uart,ruart)
 if artifact.suffix!='.elf':assert d['artifact_sha256']==rd['artifact_sha256'],(name,'input hash differs')
 pats=[r'\[P1_PROTOCOL_PASS\][^\n]+',r'\[UART\] P1_VSTU_DATA[^\n]+',r'\[UART\] P2[^\n]*DONE[^\n]+',r'\[P2_SCALAR_SUMMARY\][^\n]+',r'\[P2_OBS_SUMMARY\][^\n]+',r'\[UART\] P3_DONE[^\n]+',r'\[P3_FLAGS_SUMMARY\][^\n]+',r'\[UART\] P4_DONE[^\n]+',r'\[P4_OBS_DONE\][^\n]+',r'\[UART\] P5[^\n]+',r'\[P5_OBS_DONE\][^\n]+',r'SLINK_RX_PASS[^\n]+',r'BACKEND_PASS[^\n]+']
 matches=[]
 for pat in pats:
  x=[s.strip() for s in re.findall(pat,log)];y=[s.strip() for s in re.findall(pat,rlog)];assert x==y,(name,pat,x,y);matches+=x
 if name.startswith(('p1','p2','p3','p4','p5_1d','p5_sequence','extra_')):assert matches,(name,'missing matched monitor')
 cmp={'reference_result':str(ref/'result.json'),'formal_result':str(out/'result.json'),'status_equal':True,'monitor_lines_equal':matches,'uart_lines_equal':uart,'non_elf_input_hash_equal':None if artifact.suffix=='.elf' else True}
 # ELF debug/source paths differ; compare the actual loadable payload instead.
 if artifact.suffix=='.elf':
  old=next(x.split('=',1)[1] for x in rd['cmd'] if x.startswith('+BINARY='));bins=[]
  for n,pth in [('formal',str(artifact)),('reference',old)]:
   dest=out/(n+'_payload.bin');subprocess.check_call(['/opt/riscv/bin/riscv64-unknown-elf-objcopy','-O','binary',pth,str(dest)]);bins.append(sha(dest))
  cmp['loadable_payload_sha256']=bins;assert bins[0]==bins[1],(name,'loadable payload differs',bins)
 save(B/'comparisons'/(name+'.json'),cmp)
stage=sys.argv[1]
if stage=='build':
 assert (B/'apply_journal.json').exists();assert not S.exists();S.mkdir(parents=True)
 a=['make','-C',str(F/'sw'),'OUT='+str(S),'all'];save(B/'software_command.json',{'cmd':a})
 with (B/'software_build.log').open('w') as f:subprocess.run(a,cwd=str(F),stdout=f,stderr=subprocess.STDOUT,check=True)
 compile('soc')
elif stage=='direct':
 run('p1',S/'p1_vstu_wrap.elf',['+P1_VSTU_GATE'])
 run('p2_order',S/'p2_vmfpu_order.elf',['+P2_VMFPU_MONITOR','+P2_MASK_MONITOR','+P2_SCALAR_MONITOR'])
 run('p2_mask',S/'p2_vcpop_boundaries.elf',['+P2_MASK_MONITOR','+P2_SCALAR_MONITOR']);run('p2_scalar',S/'p2_scalar_overlap.elf',['+P2_SCALAR_MONITOR'])
 run('p3_flags',S/'p3_div_flags.elf',['+P3_FLAGS_MONITOR']);run('p3_matrix',S/'p3_mask_matrix.elf',['+P3_FLAGS_MONITOR'])
 for i in range(1,7):run('p4_%02d'%i,S/('p4_%02d.elf'%i),['+P4_SLINK_OBSERVE','+P4_CASE='+str(i)])
 run('p5_1d',S/'p5_dma_1d.elf',['+P5_DMA_MONITOR']);run('p5_sequence',S/'p5_dma_sequence.elf',['+P5_DMA_MONITOR'])
elif stage=='regressions':
 for n,e in [('hello','helloworld'),('csr','rvv_test_vstart_csrs.spm'),('vector','vector_fixed'),('rvv','rvv_bounds.spm'),('memory','memory_atomic.spm'),('fmatmul','fmatmul.spm')]:run('final_'+n,S/(e+'.elf'))
 for e in ['dma_original','dma_reg_lanes','dma_long_aw_api']:run('p5_'+e,S/(e+'.elf'))
 run('final_spi',S/'spi_raw.memh',spi=True,allow=2)
elif stage=='extras':
 compile('slink_rx')
 for c in plan['slink']['cases']:run('extra_slink_'+c['name'],S/c['elf'],['+CASE='+str(c['mode']),'+ntb_random_seed=1'],target='slink_rx')
 for mode in plan['idma']['modes']:
  target=mode['formal_target'];compile(target)
  for j in plan['idma']['jobs']:run('extra_idma_'+mode['name']+'_'+j['name'],Path(j['F']),['+ntb_random_seed=1'],target=target)
elif stage=='negative':
 run('negative_target',S/'rvv_negative.spm.elf',allow=1)
 run('negative_timeout',S/'rvv_test_vstart_csrs.spm.elf',allow=124,limit=1)
else:raise ValueError(stage)
print('FORMAL_STAGE_DONE',stage,flush=True)
