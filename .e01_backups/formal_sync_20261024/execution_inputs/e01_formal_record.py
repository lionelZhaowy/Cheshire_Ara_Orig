import json,hashlib,os,stat,sys,re
from pathlib import Path
F=Path('/home/zhaowy24/CheshireAra');R=Path('/home/zhaowy24/CheshireAraPULP');B=Path('/home/zhaowy24/CheshireAra_maintenance/formal_sync_20261024')
def sha(p):return hashlib.sha256(os.readlink(str(p)).encode() if p.is_symlink() else p.read_bytes()).hexdigest()
def save(p,d):
 ascii_only=p.read_text().isascii() if p.exists() else False;p.write_text(json.dumps(d,indent=2,ensure_ascii=ascii_only)+'\n')
def inventory():
 out={}
 for root,dirs,files in os.walk(str(F)):
  dirs[:]=[n for n in dirs if str((Path(root)/n).relative_to(F)) not in ('sim/work','sw/build')]
  for n in files:
   p=Path(root)/n;out[str(p.relative_to(F))]={'sha256':sha(p),'mode':stat.S_IMODE(p.lstat().st_mode)}
 return out
stage=sys.argv[1];report_path=F/'provenance/p1_p5_sync_20261024.json';d=json.loads(report_path.read_text());prepared=json.loads((B/'prepared.json').read_text());ref=d['reference']['passed_commit']
if stage=='record':
 assert d['status']=='source_synchronized_pending_formal_validation'
 expected_after=json.loads((B/'all_inputs_after_apply.json').read_text());actual_before_record=inventory()
 assert set(actual_before_record)==set(expected_after),'Inputs added/removed since apply'
 for path,expected_file in expected_after.items():
  assert actual_before_record[path]['sha256']==expected_file['sha256'] and actual_before_record[path]['mode']==expected_file['mode'],('Concurrent change before metadata',path)
 for rel in ['README.md','docs/README.md','docs/CONFIGURATION_AND_DEVELOPMENT.md']:
  p=F/rel;s=p.read_text();s,n=re.subn(r'17\s*个\s*ELF','31个ELF',s);assert n==1,(rel,n);p.write_text(s)
 p=F/'README.md';s=p.read_text();s += '\n## P1–P5 局部维护（2026-10-24）\n\n已按参考工程通过版本同步局部修复，未升级依赖；当前验证状态与逐项来源见[同步记录](provenance/p1_p5_sync_20261024.json)。默认关闭的定向控制/监控及14个软件目标随源码保存。备份在工程外`~/CheshireAra_maintenance/formal_sync_20261024/`，并有本地副本；回退前核对实施后哈希，避免覆盖后续修改。\n';p.write_text(s)
 p=F/'docs/CONFIGURATION_AND_DEVELOPMENT.md';s=p.read_text();s+='''

### P1–P5 定向检查（2026-10-24）

本次新增14个软件目标，继续通过现有soc的compile/start运行。P4另用`sw/link/p4_single.ld`与`p4_multi.ld`构造加载段；不替换通常的spm/rom链接脚本。控制/监控默认关闭，附加参数如下：

| 软件目标 | start附加参数 | 必须核对 |
| --- | --- | --- |
| p1_vstu_wrap | +P1_VSTU_GATE | 确实触发四条未完成存储、B=4/done=4、队列清空、64字节数据 |
| p2_vmfpu_order | +P2_VMFPU_MONITOR +P2_MASK_MONITOR +P2_SCALAR_MONITOR | 835检查、两个lane重叠执行、错绑/提前回应为0 |
| p2_vcpop_boundaries | +P2_MASK_MONITOR +P2_SCALAR_MONITOR | 124检查，尾部mask不参与计数 |
| p2_scalar_overlap | +P2_SCALAR_MONITOR | 483检查，标量/存储回应归属正确 |
| p3_div_flags / p3_mask_matrix | +P3_FLAGS_MONITOR | 177/753检查，无效lane标志污染为0 |
| p4_01至p4_06 | +P4_SLINK_OBSERVE +P4_CASE=N | missing/bad/errors=0、launch=1，六例共5195检查 |
| p5_dma_1d / p5_dma_sequence | +P5_DMA_MONITOR | 18/138字节，真实backend=1/9，完成ID及保护区 |

示例（先在对应新BUILD_DIR执行compile，并用Make构建对应OUT）：

```bash
BUILD_DIR=sim/work/my_check RUN_DIR=sim/work/my_check/p1 BINARY=sw/build/my_check/p1_vstu_wrap.elf ./sim/scripts/start.cheshire_soc.sh +P1_VSTU_GATE
```

完整结果见`provenance/p1_p5_sync_20261024.json`，不能将仅编译或普通PASS当作所有定向触发成立。来源仅按原结构更新；未引入Bender路径、在线依赖操作、配置生成器或新测试框架。
''';p.write_text(s)
 # Preserve original upstream hashes and revisions, append the adopted local state.
 manifest_path=F/'provenance/source_manifest.json';m=json.loads(manifest_path.read_text());known={x['destination']:x for x in m}
 touched=set(d['source_map'].values())|{'src/tb/src/tb_cheshire_soc.sv','sw/Makefile','README.md','docs/README.md','docs/CONFIGURATION_AND_DEVELOPMENT.md'}
 for rel in touched:
  row=known[rel];row.setdefault('local_maintenance',[]).append({'date':'2026-10-24','reference_commit':ref,'previous_sha256':row['sha256'],'report':'provenance/p1_p5_sync_20261024.json'});row['sha256']=sha(F/rel)
 for rel in prepared['new_paths']:
  if rel==str(report_path.relative_to(F)):continue
  assert rel not in known;m.append({'source':rel,'destination':rel,'source_sha256':sha(R/rel),'sha256':sha(F/rel),'component':'maintenance_tests','revision':ref,'purpose':'P1-P5 directed regression input; copied from verified reference without production configuration changes'})
 save(manifest_path,m)
 p=F/'provenance/generation_inputs.json';g=json.loads(p.read_text());found=0
 for row in g['records']:
  if row['target'].endswith('/idma/src/frontend/reg/tpl/idma_reg.sv.tpl'):
   row['local_maintenance']={'date':'2026-10-24','reference_commit':ref,'previous_sha256':row['sha256'],'report':'provenance/p1_p5_sync_20261024.json'};row['sha256']=sha(Path(row['target']));found+=1
 assert found==1;save(p,g)
 d['status']='source_and_provenance_synchronized_pending_validation';d['pending']=['Run formal builds and full comparison tests','Check protected inputs and archive results'];save(report_path,d);save(B/'after_metadata.json',inventory());print('FORMAL_METADATA_READY',len(m))
elif stage=='finish':
 results={p.stem:json.loads(p.read_text()) for p in (B/'results').glob('*.json')};cmps={p.stem:json.loads(p.read_text()) for p in (B/'comparisons').glob('*.json')}
 expected=set(['p1', 'p2_order', 'p2_mask', 'p2_scalar', 'p3_flags', 'p3_matrix', 'p4_01', 'p4_02', 'p4_03', 'p4_04', 'p4_05', 'p4_06', 'p5_1d', 'p5_sequence', 'final_hello', 'final_csr', 'final_vector', 'final_rvv', 'final_memory', 'final_fmatmul', 'final_spi', 'p5_dma_original', 'p5_dma_reg_lanes', 'p5_dma_long_aw_api', 'extra_slink_idle_64k', 'extra_slink_cpu_concurrent_192k', 'extra_slink_cpu_concurrent_unaligned_gapped', 'extra_idma_ideal_issue115_aw0_rw0', 'extra_idma_ideal_issue115_aw0_rw1', 'extra_idma_ideal_issue115_aw1_rw0', 'extra_idma_ideal_issue115_aw1_rw1', 'extra_idma_ideal_mixed_modes', 'extra_idma_ideal_pr80_asymmetric', 'extra_idma_throttle_issue115_aw0_rw0', 'extra_idma_throttle_issue115_aw0_rw1', 'extra_idma_throttle_issue115_aw1_rw0', 'extra_idma_throttle_issue115_aw1_rw1', 'extra_idma_throttle_mixed_modes', 'extra_idma_throttle_pr80_asymmetric'])
 assert set(cmps)==expected and set(results)==expected|{'negative_target','negative_timeout'},(sorted(results),sorted(cmps))
 for n,x in results.items():
  expected='TIMEOUT' if n=='negative_timeout' else 'TARGET_FAIL' if n=='negative_target' else 'ASSERTION_OR_SIM_ERROR' if n=='final_spi' else 'PASS';assert x['status']==expected,(n,x['status'])
 # Exact known warning contexts, with only project/hierarchy path normalization.
 spi=results['final_spi'];rspi=json.loads((R/'work/runs/sync_final_spi/result.json').read_text())
 norm=[x.replace(str(F/'src/cheshire_soc/cva6'),str(R/'.bender/git/checkouts/cva6-20c9d7cbe0dd6995')).replace('fix.dut.i_soc.','fix.dut.') for x in spi['errors']]
 assert norm==rspi['errors'],'SPI warning context differs'
 data=bytearray(49152);seen=set();stores=0;entry=False;other_helper_stores=[]
 with (F/'sim/work/p1_p5_20261024/runs/final_spi/trace_hart_0.log').open() as f:
  for line in f:
   if re.search(r' M 0000000010000000 ',line):entry=True;break
   q=re.search(r' M 0000000002000aae .*\bsw\s+a6, 0\(a1\).*a6\s*:([0-9a-f]{16}).*PA: ([0-9a-f]+)',line)
   if q:
    off=int(q[2],16)-0x10000000
    if not 0<=off<len(data)-3:
     other_helper_stores.append({'address':hex(int(q[2],16)),'data':q[1]});continue
    data[off:off+4]=(int(q[1],16)&0xffffffff).to_bytes(4,'little');seen.update(range(off,off+4));stores+=1
 assert other_helper_stores==json.loads((R/'provenance/reference_sync_20261023.json').read_text())['spi_acceptance']['outside_image_helper_stores']
 assert entry and stores==12288 and len(seen)==49152 and bytes(data)==(F/'sw/build/p1_p5_20261024/spi_raw.bin').read_bytes()
 before=json.loads((B/'all_inputs_before.json').read_text());after=inventory();allowed=set(prepared['existing'])|set(prepared['new_paths'])
 assert set(after)-set(before)==set(prepared['new_paths']);assert not (set(before)-set(after))
 for rel,v in before.items():
  if rel not in allowed:assert after[rel]['sha256']==v['sha256'] and after[rel]['mode']==v['mode'],rel
 for src,dst in d['source_map'].items():assert (R/src).read_bytes()==(F/dst).read_bytes(),dst
 manifest=json.loads((F/'provenance/source_manifest.json').read_text())
 for row in manifest:assert sha(F/row['destination'])==row['sha256'],row['destination']
 d.update(status='verified_in_formal_project',results=results,comparisons=cmps,pending=[],counts={'runs':41,'normal_pass':38,'rom_padding_limited_acceptance':1,'expected_negative':2,'reference_compared':39},spi_acceptance={'same_known_warnings':True,'loaded_bytes':49152,'cpu_stores':stores,'outside_image_helper_stores':other_helper_stores,'mismatches':0,'limit':'Executed-store reconstruction, not independent memory-model dump.'},protected_inputs={'before':len(before),'after':len(after),'all_unselected_unchanged':True},rollback={'backup':prepared['backup'],'sha256':prepared['backup_sha256'],'before_metadata':str(B/'prepared.json'),'after_metadata':str(B/'final_after.json'),'new_paths':prepared['new_paths'],'rule':'Before restoring any selected file, check all selected current hashes against final_after; refuse on concurrent changes. Restore only old members with original permissions and remove only listed new files with matching hashes. Preserve logs and outputs.'},limitations=['Original FS, libgcc and shared LLC limitations remain','No synthesis, PPA or ASIC acceptance','Unused iDMA derived configurations are not dynamically validated'])
 save(report_path,d);save(B/'formal_result.json',d);save(B/'final_after.json',inventory());print('FORMAL_VALIDATED',d['counts'])
else:raise ValueError(stage)
