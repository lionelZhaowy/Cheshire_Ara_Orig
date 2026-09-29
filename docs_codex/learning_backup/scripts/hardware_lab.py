#!/usr/bin/env python3
"""Bounded teaching calculations, NOT a SystemVerilog elaborator or AXI simulator."""
import argparse, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
LEARN=ROOT/'docs_codex/learning'
def verify_sources():
 baseline=json.loads((LEARN/'evidence/hardware-model-baseline.json').read_text())
 for name,digest in baseline.items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
   raise ValueError('Reviewed source changed; re-audit model before use: '+name)
def defaults():
 verify_sources()
 source=(ROOT/'hw/cheshire_pkg.sv').read_text().split('DefaultCfg =',1)[1]
 # Only decimal and hex literal fields used in these single-core scenarios.
 out={}
 for key,value in re.findall(r'^\s*(\w+)\s*:\s*((?:\d+)?\s*\x27h[0-9a-fA-F_]+|\d+)\s*,',source,re.M):
  out[key]=int(value.split('h')[-1].replace('_',''),16) if 'h'in value else int(value)
 return out
SCENARIOS={'default':{},'ara':{'Ara':1},'no-uart':{'Uart':0},'ara-ext2':{'Ara':1,'AxiExtNumMst':2},'llc-bypass':{'LlcNotBypass':0}}
def topology(name):
 c=defaults();c.update(SCENARIOS[name]);assert c['NumCores']==1
 masters=['CPU','Debug']+[label for flag,label in [('Ara','Ara'),('Dma','DMA'),('SerialLink','Link'),('Vga','VGA'),('Usb','USB')] if c[flag]]
 masters += ['Ext'+str(i) for i in range(c.get('AxiExtNumMst',0))]
 regs=['err','CLINT','PLIC','SoC regs']; rules=[]
 for flag,label,base in [('Bootrom','BootROM',0x02000000),('LlcNotBypass','LLC',0x03001000),('Uart','UART',0x03002000),('I2c','I2C',0x03003000),('SpiHost','SPI',0x03004000),('Gpio','GPIO',0x03005000),('SerialLink','Link',0x03006000),('Vga','VGA',0x03007000),('Usb','USB',0x03008000)]:
  if c[flag]:
   rules.append({'target':label,'index':len(regs),'base':hex(base)});regs.append(label)
 # This is an intentionally bounded model. Not a general rule generator.
 assert c['Clic']==c['IrqRouter']==c['AxiRt']==0
 if c['BusErr']:regs+=['BusErrVGA','BusErrDMA','BusErrCPU']
 return {'evidence':'teaching calculation; not RTL elaboration','scenario':name,'masters':dict(enumerate(masters)), 'xbar_target_id_bits':c['AxiMstIdWidth']+(len(masters)-1).bit_length(), 'reg_targets':dict(enumerate(regs)), 'selected_reg_rules':rules, 'llc_array_bytes_if_present':c['LlcSetAssoc']*c['LlcNumLines']*c['LlcNumBlocks']*c['AxiDataWidth']//8 if c['LlcNotBypass'] else 0}
def lane(offset,value):
 if offset not in (0,4) or not 0<=value<=0xffffffff:raise ValueError('Only aligned 32-bit accesses at offsets 0/4 are modeled')
 return {'size_log2_bytes':2,'offset':offset,'wdata_64':f'0x{value<<(8*offset):016x}','wstrb_64':hex(0xf<<offset),'reg_wdata_32':hex(value),'reg_wstrb':hex(0xf)}
def check_channel(trace):
 """Single ready/valid channel monitor; no burst/ordering/ATOP claim."""
 held=None;transfers=[]
 for cycle,(valid,ready,payload) in enumerate(trace):
  if held is not None and (not valid or payload!=held):raise ValueError(f'cycle {cycle}: changed stalled payload/valid')
  if valid and ready:transfers.append(payload)
  held=payload if valid and not ready else None
 if held is not None:raise ValueError('trace ended with pending beat')
 return transfers
def decode(addr,rules):
 # Local addr_decode precedence: higher array index wins; half-open ranges.
 hits=[target for lo,hi,target in rules if lo<=addr<hi]
 return hits[-1] if hits else 'DECERR'
def self_test():
 checks=[]
 def ck(name,condition):
  if not condition:raise AssertionError(name)
  checks.append(name)
 def reject(name,fn):
  try:fn()
  except ValueError:checks.append(name);return
  raise AssertionError('expected rejection: '+name)
 for name,n,w in [('default',6,5),('ara',7,5),('ara-ext2',9,6)]:
  t=topology(name);ck(name+' source count / ID',len(t['masters'])==n and t['xbar_target_id_bits']==w)
 a=topology('default');b=topology('no-uart')
 i=lambda t:next(x for x in t['selected_reg_rules'] if x['target']=='I2C')
 ck('I2C index shifts, address stable',i(a)['index']==7 and i(b)['index']==6 and i(a)['base']==i(b)['base']=='0x3003000')
 ck('UART removed',not any(x['target']=='UART'for x in b['selected_reg_rules']))
 ck('SPM size baseline/bypass',a['llc_array_bytes_if_present']==131072 and topology('llc-bypass')['llc_array_bytes_if_present']==0)
 ck('upper lane',lane(4,0x11223344)['wdata_64']=='0x1122334400000000' and lane(4,1)['wstrb_64']=='0xf0')
 ck('lower lane',lane(0,1)['wstrb_64']=='0xf')
 reject('unaligned rejected',lambda:lane(2,1))
 ck('stalled beat counted once',check_channel([(1,0,17),(1,0,17),(1,1,17),(0,1,99)])==[17])
 ck('back-to-back accepted beats',check_channel([(1,1,1),(1,1,2)])==[1,2])
 reject('payload mutation detected',lambda:check_channel([(1,0,1),(1,1,2)]))
 reject('valid withdrawal detected',lambda:check_channel([(1,0,1),(0,1,1)]))
 reject('unfinished trace detected',lambda:check_channel([(1,0,1)]))
 rules=[(0x1000,0x2000,'A'),(0x1800,0x1900,'B')]
 ck('decode start inclusive',decode(0x1000,rules)=='A')
 ck('decode end exclusive',decode(0x2000,rules)=='DECERR')
 ck('higher rule wins overlap',decode(0x1800,rules)=='B')
 ck('overlap end falls back',decode(0x1900,rules)=='A')
 print('\n'.join('PASS '+x for x in checks));print(f'PASS {len(checks)} teaching-model checks; no production RTL executed')
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 t=s.add_parser('topology');t.add_argument('--scenario',choices=SCENARIOS,default='default')
 l=s.add_parser('lane');l.add_argument('--offset',type=lambda v:int(v,0),required=True);l.add_argument('--value',type=lambda v:int(v,0),required=True)
 s.add_parser('self-test');a=p.parse_args()
 if a.command=='self-test':self_test()
 else:print(json.dumps(topology(a.scenario) if a.command=='topology'else lane(a.offset,a.value),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
