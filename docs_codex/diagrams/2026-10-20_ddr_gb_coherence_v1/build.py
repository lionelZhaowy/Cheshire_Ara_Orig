#!/usr/bin/env python3
"""v1 topic figures. Reuse existing figure helpers; never rewrite older outputs."""
import sys, json, re, importlib.util, shutil
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('v1_base',D.parent/'2026-10-16_cache_coherence/build_figures.py')
review=load('v1_review',D.parent/'2026-10-16_ddr_gb_coherence_review/build.py')
hybrid=load('v1_hybrid',D.parent/'2026-10-16_coherence_hybrid/build.py')
Figure,C=base.Figure,base.C

def system():
 f=Figure('system','SoC v1：DDR–GB 数据路径与范围维护',
 'CPU / Ara2 共享 M5；F0–F3 共享压缩前端；控制箭头表示逻辑职责，接口编码待实现。',3200,1800)
 f.autojump=True
 f.rect('compute-region',60,145,950,480,'#FAF2F3')
 f.box('cpu',80,180,360,120,'CVA6 CPU',['L1D / WT 写缓冲'],fill='cpu')
 f.box('ara',560,180,360,120,'Ara 2 lanes',['VLSU / AXI64'],fill='cpu')
 f.box('filter',560,350,360,80,'既有失效过滤 / 等宽转换',fill='cpu')
 f.box('xbar',80,500,900,90,'主 AXI Crossbar · 64 bit',['CPU / Ara 独立输入 · M2 主存 / M5 GB'],fill='interconnect')
 f.box('llc',90,730,420,130,'M2：原子适配 → LLC',['WB cache / 保留 SPM'],fill='memory')
 f.rect('gb-region',1080,145,1020,510,'#F0F8F5')
 f.box('npu',1120,200,400,120,'NPU 计算',['GB 操作数 / 结果'],fill='gb')
 f.box('mover',1670,200,400,120,'DDR ↔ GB 搬运器',['GB 本地口 / F1 DDR 口'],fill='gb')
 f.box('adapter',1120,500,380,120,'GB 共享访问适配',['仲裁 / bank 冲突处理'],fill='gb')
 f.box('gb',1600,500,390,120,'Global Buffer',['独立 SRAM · 非缓存映射建议'],fill='gb')
 f.box('isp',2250,200,400,120,'LVDS RX / ISP',['RAW 或处理后像素'],fill='interconnect')
 f.box('frame',2250,500,400,120,'帧写入 DMA',['F2：AW / W，返回 B'],fill='interconnect')
 f.box('roi',2750,740,360,160,'ROI 调度 / 二维读 DMA',['F3：AR，返回 R','源帧读完后交还'],fill='interconnect')
 f.box('tx',2750,1100,360,120,'输出 FIFO / LVDS TX',['像素整理与发送'],fill='interconnect')
 f.box('maint',800,740,900,125,'范围维护服务（逻辑职责）',['软件范围命令 · 排空 / clean / invalidate · 准入与完成'],fill='agent',dashed=True)
 f.box('frontend',550,1020,2100,320,'共享压缩前端 · 四入口共享服务',
 ['逻辑地址映射 · 共享压缩 / 解压 · 普通区域旁路',
 '数据与元数据发布 · 子事务错误聚合 · 读写响应匹配'],fill='gb')
 f.box('controller',550,1430,2100,180,'一个 DDR Controller · 四个 AXI slave',
 ['四口仲裁 / 共享物理 DDR 带宽 · 排空与跨口可见性待契约确认'],fill='memory')
 f.box('ddr',2750,1470,360,120,'DDR PHY / DDR',['片外存储'],fill='memory')
 # Data/control arrows: retain source and target for checks.
 def a(k,pts,src,dst,kind='data',both=True): f.arrow(k,pts,kind,both=both,start=src,end=dst)
 a('cpu-xbar',[(260,300),(260,500)],'cpu','xbar')
 a('ara-filter',[(740,300),(740,350)],'ara','filter')
 a('filter-xbar',[(740,430),(740,500)],'filter','xbar')
 a('m2-llc',[(300,590),(300,730)],'xbar','llc')
 a('m5-gb',[(980,545),(1120,545)],'xbar','adapter')
 f.text(1020,525,'M5',24)
 a('adapter-gb',[(1500,560),(1600,560)],'adapter','gb','local')
 a('npu-gb',[(1320,320),(1320,500)],'npu','adapter','local')
 a('mover-gb',[(1870,320),(1870,400),(1410,400),(1410,500)],'mover','adapter','local')
 a('isp-gb',[(2250,260),(2170,260),(2170,660),(1450,660),(1450,620)],'isp','adapter','local')
 a('isp-frame',[(2450,320),(2450,500)],'isp','frame','local',False)
 a('llc-f0',[(510,790),(680,790),(680,1020)],'llc','frontend')
 a('mover-f1',[(2070,260),(2110,260),(2110,940),(1280,940),(1280,1020)],'mover','frontend')
 a('frame-f2',[(2450,620),(2450,910),(1880,910),(1880,1020)],'frame','frontend')
 a('roi-f3',[(2750,800),(2680,800),(2680,970),(2480,970),(2480,1020)],'roi','frontend')
 a('roi-tx',[(2930,900),(2930,1100)],'roi','tx','local',False)
 for i,x in enumerate([680,1280,1880,2480]):
  f.box('f'+str(i),x-115,1020,230,55,['F0 · LLC','F1 · GB 搬运','F2 · 帧写','F3 · 帧读'][i],fill='memory')
  a('ddr-port'+str(i),[(x,1340),(x,1430)],'frontend','controller')
  f.box('s'+str(i),x-115,1430,230,50,'DDR.S'+str(i),fill='memory')
 a('controller-ddr',[(2650,1530),(2750,1530)],'controller','ddr')
 # Control paths use distinct routes; no implied data bypass.
 a('maint-cpu',[(800,765),(760,765),(760,690),(40,690),(40,240),(80,240)],'maint','cpu','control')
 a('maint-llc',[(800,830),(510,830)],'maint','llc','control')
 a('maint-mover',[(1700,770),(2090,770),(2090,355),(1950,355),(1950,320)],'maint','mover','control')
 a('maint-frame',[(1700,805),(2210,805),(2210,560),(2250,560)],'maint','frame','control')
 a('maint-roi',[(1700,840),(2750,840)],'maint','roi','control')
 a('maint-front',[(800,865),(800,980),(510,980),(510,1180),(550,1180)],'maint','frontend','control')
 a('maint-ddr',[(900,865),(900,960),(470,960),(470,1540),(550,1540)],'maint','controller','control')
 f.text(80,1680,'蓝：AXI 请求 / 返回（F2 仅写，F3 仅读）    绿：GB 局部访问 / 像素流    紫：软件命令、维护、准入与确认',28)
 f.text(80,1740,'GB 本地交接管理使用权；DDR 同步涵盖缓存、共享前端与控制器。未画出的外设 / 配置 / eMMC 路径沿用 v1。',27)
 return f

def timeline():
 f=review.timeline()
 mapping={'DDR / 搬运器':'前端 / DDR / 搬运器','跨端口数据可见':'逻辑合并：跨口可见',
 '经 S0 写回；检查错误响应':'经 F0 写回；检查聚合响应',
 '跨端口可见；汇合缓存完成与错误状态':'前端数据 / 元数据可见；汇合完成与错误',
 '输入搬入 GB':'经 F1 读 DDR，搬入 GB','结果写入 DDR':'GB 经 F1 写回 DDR',
 '任务成功：搬出完成，CPU 端口可见':'任务成功：前端发布完成，F0 读取可见'}
 # Rebuild labels with same geometry so their white backings fit the revised strings.
 source=(D.parent/'2026-10-16_ddr_gb_coherence_review/build.py').read_text()
 start=source.index('def timeline():');end=source.index('\n\ndef main()',start)
 body=source[start:end]
 for a,b in mapping.items(): body=body.replace(a,b)
 body=body.replace("def message(key, a, b, y, label, kind='control', label_size=25):", "number = 0\n    def message(key, a, b, y, label, kind='control', label_size=25):\n        nonlocal number\n        number += 1\n        label = str(number) + '. ' + label")
 env={'Figure':Figure,'C':C};exec(body,env);return env['timeline']()

def revised_ownership():
 f=hybrid.ownership()
 return hybrid.replace(f,{'DDR 共享点':'前端 / DDR 共享点','确认写回跨端口可见':'数据 / 元数据跨口可见','DDR 跨口可见':'前端发布 / 跨口可见','排空 / 作废旧响应':'排空相关旧响应'})

def revised_paths():
 f=hybrid.data_paths()
 return hybrid.replace(f,{'本方案：先清理到 DDR，再搬运':'本方案：经前端清理，再搬运',
 '等待 DDR 可见':'等待前端 / DDR 可见',
 '保留 DDR 供数路径；脏数据经历写回与再次读取。':'经共享前端供数；数据与元数据按逻辑地址发布。',
 '脏行经 DDR 需写回后重读；缓存直供减少当次 DDR 往返，同时增加片上数据响应通路。':'N + D 为上游逻辑字节；DDR 实际字节另计压缩、元数据及部分块处理。'})

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out-dir',type=Path,required=True);out=p.parse_args().out_dir
 out.mkdir(parents=True,exist_ok=False)
 fs=[system(),timeline(),revised_ownership(),revised_paths()]
 layouts=[f.save(out) for f in fs]
 # Preserve unchanged figures byte for byte, including their original layout metadata.
 for directory,names in [('2026-10-16_ddr_gb_coherence_review',['versions']),('2026-10-16_coherence_hybrid',['handover','coverage','agent-types'])]:
  src=D.parent/directory/'figures'; old=json.loads((src/'layout.json').read_text())
  for name in names:
   shutil.copy2(src/(name+'.svg'),out/(name+'.svg'))
   layouts.append(next(x for x in old if x['name']==name))
 (out/'layout.json').write_text(json.dumps(layouts,ensure_ascii=False,indent=2)+'\n')
 print('Generated',len(layouts),'figures')
if __name__=='__main__':main()
