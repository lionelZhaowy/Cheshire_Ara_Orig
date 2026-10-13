#!/usr/bin/env python3
"""Redraw nine non-learning figures. Export only to a new/empty directory."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
INK='#29292D';MUTED='#606773';AXI='#314D66';GB='#187C78';PIX='#B96043';CTL='#765489';GRAY='#93939D'
PINK='#F1D7D9';BLUE='#D8E8F4';TEAL='#D9EEE8';PEACH='#F5E1C9';PURPLE='#E8DFED';WHITE='#FFFFFF'
class D:
 def __init__(self,title,subtitle='',w=2400,h=1350):
  self.w,self.h=w,h;self.n=0;self.blocks={};self.texts=[]
  self.root=ET.Element('{'+NS+'}svg',width=str(w),height=str(h),viewBox=f'0 0 {w} {h}')
  ET.SubElement(self.root,'{'+NS+'}title').text=title
  defs=ET.SubElement(self.root,'{'+NS+'}defs')
  for c in [AXI,GB,PIX,CTL,GRAY]:
   m=ET.SubElement(defs,'{'+NS+'}marker',id='a'+c[1:],markerUnits='strokeWidth',markerWidth='3',markerHeight='3',viewBox='0 0 3 3',refX='3',refY='1.5',orient='auto-start-reverse')
   ET.SubElement(m,'{'+NS+'}polygon',points='0,0 3,1.5 0,3',fill=c)
  self.rect('background',0,0,w,h,WHITE,'none');self.text(45,65,title,43,bold=True,anchor='start')
  if subtitle:self.text(48,112,subtitle,24,color=MUTED,anchor='start')
 def el(self,tag,id=None,**attrs):
  self.n+=1;attrs={k.replace('_','-'):str(v) for k,v in attrs.items()};attrs['id']=id or f'o{self.n}'
  return ET.SubElement(self.root,'{'+NS+'}'+tag,attrs)
 def rect(self,id,x,y,w,h,fill=WHITE,stroke=INK,dash=False,sw=2):
  a=dict(x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=sw)
  if dash:a['stroke_dasharray']='10 6'
  self.el('rect',id,**a);self.blocks[id]=[x,y,w,h]
 def text(self,x,y,s,size=27,color=INK,bold=False,anchor='middle',owner=None):
  e=self.el('text',x=x,y=y,font_family='Microsoft YaHei',font_size=size,fill=color,font_weight='bold' if bold else 'normal',text_anchor=anchor);e.text=s
  self.texts.append(dict(text=s,x=x,y=y,size=size,anchor=anchor,owner=owner,id=e.get('id')))
 def box(self,id,x,y,w,h,title,sub=(),fill=BLUE,dash=False,size=28,subsize=24):
  self.rect(id,x,y,w,h,fill,dash=dash);lines=[title,*sub];gap=34
  first=y+h/2-(len(lines)-1)*gap/2+size*.34
  for i,s in enumerate(lines):self.text(x+w/2,first+i*gap,s,size if i==0 else subsize,color=INK if i==0 else MUTED,bold=i==0,owner=id)
 def domain(self,id,x,y,w,h,title,fill,dash=False):
  self.rect(id,x,y,w,h,fill,dash=dash);self.text(x+w/2,y+43,title,30,bold=True,owner=id)
 def line(self,id,pts,c=AXI,both=False,arrow=True,dash=False,sw=3):
  a=dict(fill='none',stroke=c,stroke_width=sw,stroke_linejoin='miter')
  if arrow:a['marker_end']='url(#a'+c[1:]+')'
  if both:a['marker_start']='url(#a'+c[1:]+')'
  if dash:a['stroke_dasharray']='9 6'
  if len(pts)==2:
   a.update(x1=pts[0][0],y1=pts[0][1],x2=pts[1][0],y2=pts[1][1]);self.el('line',id,**a)
  else:a['points']=' '.join(f'{x},{y}' for x,y in pts);self.el('polyline',id,**a)
 def path(self,id,path,c=AXI,both=False,sw=3):
  a=dict(d=path,fill='none',stroke=c,stroke_width=sw,marker_end='url(#a'+c[1:]+')')
  if both:a['marker_start']='url(#a'+c[1:]+')'
  self.el('path',id,**a)
 def legend(self,items):
  for i,(c,label) in enumerate(items):
   x=55+i*530;self.line('legend'+str(i),[(x,self.h-45),(x+65,self.h-45)],c,both=c==GB and '读写' in label,sw=2.5);self.text(x+80,self.h-37,label,22,color=c,anchor='start')

def example():
 d=D('数据处理与反馈','工业风格 · 原生矢量对象',1600,900)
 d.domain('pipeline',45,180,1510,520,'处理流水线',PEACH)
 for id,x,t,s,c in [('input',100,'输入数据','Input',BLUE),('process',650,'处理模块','Process',TEAL),('output',1200,'输出结果','Output',BLUE)]:d.box(id,x,330,280,150,t,[s],c,size=33,subsize=27)
 d.line('input-process',[(380,405),(650,405)])
 d.line('process-output',[(930,405),(1200,405)])
 d.path('feedback','M 1340 480 L 1340 545 C 1340 620 240 620 240 545 L 240 480',GB)
 d.text(790,657,'反馈路径 / Feedback',27,color=GB)
 d.legend([(AXI,'主数据流'),(GB,'反馈')]);return d

def ddr_qos_proposal():
 d=D('DDR 多端口仲裁与 QoS','历史独立主口方案：S0 = SoC · S1 = ISP · S2 = NPU（与后续 GB 三口方案区分）')
 d.domain('soc',60,190,960,390,'SoC 主存路径',PINK)
 d.box('cpu-ara',100,285,220,140,'CVA6 + Ara',['现有发起端'])
 d.box('xbar',380,285,220,140,'Crossbar',['地址路由'])
 d.box('llc',660,250,320,210,'原子适配 + LLC',['LLC 外存出口','SPM 访问可留在片内'])
 d.line('soc-xbar',[(320,355),(380,355)]);d.line('xbar-llc',[(600,355),(660,355)])
 d.domain('isp-domain',1070,190,560,390,'ISP 数据主口',PEACH,True)
 d.box('isp',1100,280,500,180,'ISP AXI Master',['写帧缓冲','绕过主 Crossbar / LLC'],WHITE)
 d.domain('npu-domain',1680,190,660,390,'NPU 数据主口',TEAL,True)
 d.box('npu',1730,280,560,180,'NPU AXI Master',['读写权重 / 特征图','绕过 LLC'],WHITE)
 d.domain('controller',60,740,1900,460,'DDR Controller 内部',BLUE,True)
 for n,x,sub in [(0,220,'SoC 外存'),(1,1150,'ISP 写入'),(2,1750,'NPU 读 / 写')]:
  d.box('port'+str(n),x,810,170,95,'S'+str(n),[sub],WHITE,size=27,subsize=22)
  d.line('portjoin'+str(n),[(x+85,905),(x+85,955)],arrow=False)
 d.line('llc-port',[(820,460),(820,640),(305,640),(305,810)])
 d.line('isp-port',[(1350,460),(1350,675),(1235,675),(1235,810)])
 d.line('npu-port',[(2010,460),(2010,640),(1835,640),(1835,810)])
 d.line('merge',[(305,955),(1835,955)],arrow=False)
 d.box('arbiter',160,1020,500,140,'端口仲裁 / QoS',['可配置优先级 · 轮询','页命中限制'],WHITE)
 d.box('core',900,1020,930,140,'Controller Core',['内部命令队列 · FR-FCFS','遵守 DRAM 时序'],WHITE)
 d.line('arbiter-in',[(410,955),(410,1020)]);d.line('arbiter-core',[(660,1090),(900,1090)])
 d.box('phy',2010,1015,330,150,'PHY + SDRAM',['共享外存带宽'],PURPLE)
 d.line('core-phy',[(1830,1090),(2010,1090)],both=True)
 d.legend([(AXI,'AXI 请求 / 数据')]);d.rect('dash-legend',585,1290,65,27,WHITE,GRAY,True);d.text(675,1313,'虚线分区：尚未集成',22,color=MUTED,anchor='start');return d

def crossbar_ara():
 d=D('Cheshire + CVA6 + Ara · AXI Crossbar','Ara 仿真配置：2 lanes / VLEN 2048 · 64-bit AXI · RT 关闭 · 7 × 5 全连接',2800,1575)
 d.domain('sources',50,185,520,1250,'AXI master / 发起端',PINK)
 d.domain('fabric',615,185,1320,1250,'每输入地址译码 → 每目标独立仲裁',PEACH)
 d.domain('targets',1980,185,770,1250,'AXI slave / 目标与下游',BLUE)
 ys=[340+i*155 for i in range(7)];outs=[355,560,800,1095,1280]
 names=[('CVA6 core 0','cheshire_cva6_wrap'),('Debug / SBA','调试总线发起端'),('Ara 访存','filter → 64→64 位宽适配'),('iDMA 数据','独立搬运主口'),('Serial Link RX','远端请求入口'),('VGA 取帧','帧缓冲读取'),('USB DMA','OHCI 数据访问')]
 for i,y in enumerate(ys):
  d.box('source'+str(i),80,y-60,450,120,f'S{i} · '+names[i][0],[names[i][1]],WHITE,size=28)
  d.box('demux'+str(i),655,y-43,245,86,f'DEMUX S{i}',['AR / AW 译码'],WHITE,size=27,subsize=23)
  d.line('input'+str(i),[(530,y),(655,y)])
 for i,y in enumerate(ys):
  for j,z in enumerate(outs):d.line(f'reach-{i}-{j}',[(900,y),(1615,z)],GRAY,arrow=False,sw=1)
 for i,j,c in [(0,1,PIX),(2,2,AXI),(3,2,GB)]:d.line(f'example-{i}-{j}',[(900,ys[i]),(1615,outs[j])],c,sw=3.3)
 for j,y in enumerate(outs):
  d.box('mux'+str(j),1615,y-45,260,90,f'MUX M{j}',['独立仲裁'],WHITE,size=27)
  d.line('output'+str(j),[(1875,y),(2020,y)])
 targets=[(0,355,130,'Debug 目标接口',['调试地址窗口 · 与 SBA 分开']),
 (1,560,190,'AXI → Regbus → demux',['ROM / CLINT / PLIC / SoC regs','UART / I²C / SPI / GPIO / LLC 等']),
 (2,800,265,'LLC / SPM 共用目标',['AMO/LRSC → cut / 地址重映射 → LLC','SPM 128 KiB · cached / uncached 别名','0x8000_0000 ≤ 外存 < 0x1_0000_0000','LLC 下游 → 平台 DDR；命中可留片内']),
 (3,1095,130,'iDMA 控制接口',['0x0100_0000 起 · 与数据主口分开']),
 (4,1280,150,'Serial Link TX',['0x1_0000_0000 ≤ addr < 0x2_0000_0000'])]
 for i,y,h,t,sub in targets:d.box('target'+str(i),2020,y-h/2,690,h,f'M{i} · '+t,sub,WHITE,size=29,subsize=24)
 d.text(1260,1398,'灰线：所有可达路径；彩线：同时请求示例',25,color=MUTED)
 d.text(65,1508,'不同目标可并行；竞争同一目标时由该目标仲裁。',28,anchor='start')
 d.text(2740,1508,'S / M 为 Crossbar 端口视角',26,color=MUTED,anchor='end');return d

def ddr_interconnect():
 d=D('DDR 互联候选结构 · 共享 Global Buffer','S0 = SoC / LLC · S1 = 统一 NPU / GB 搬运 · S2 = 图像帧写入',2800,1575)
 d.domain('cpu-domain',60,200,840,430,'CVA6–Ara 系统路径',PINK)
 d.box('cpu',90,290,220,135,'CVA6',['标量访存'])
 d.box('ara',400,290,465,110,'Ara',['单一 AXI 访存出口'])
 d.box('filter',400,455,125,100,'失效过滤',['现有'],WHITE,size=25,subsize=22)
 d.box('split',550,455,125,100,'地址分流',['新增'],PURPLE,True,size=25,subsize=22)
 d.box('width',700,455,165,100,'位宽适配',['普通地址'],WHITE,size=25,subsize=22)
 d.line('ara-filter',[(462,400),(462,455)]);d.line('filter-split',[(525,505),(550,505)]);d.line('split-width',[(675,505),(700,505)])
 d.domain('gb-domain',930,200,900,430,'独立 GB / NPU 子系统',TEAL,True)
 d.box('npu',960,305,220,140,'NPU 计算',['独立于搬运器'],PINK)
 d.box('router',1215,305,250,140,'GB 访问适配',['仲裁 / bank 冲突'],WHITE)
 d.box('gb',1500,305,290,140,'Global Buffer',['独立分 bank SRAM','工作区 / 双缓冲'],TEAL)
 d.box('mover',1500,495,290,100,'NPU / GB 搬运',['DDR ↔ GB'],BLUE)
 d.line('npu-router',[(1180,375),(1215,375)],GB,both=True);d.line('router-gb',[(1465,375),(1500,375)],GB,both=True)
 d.line('mover-router',[(1500,545),(1340,545),(1340,445)],GB,both=True)
 d.line('ara-gb',[(675,475),(686,475),(686,425),(913,425),(913,280),(1260,280),(1260,305)],GB)
 d.domain('image-domain',1860,200,880,430,'图像接收 / ISP / 帧写入',PEACH,True)
 for name,x,w,t,sub in [('lvds',1895,140,'LVDS','解串 / 帧行'),('cdc',2055,140,'CDC/FIFO','像素缓冲'),('isp',2215,140,'ISP','处理/行缓冲'),('select',2375,140,'帧选择','RAW / ISP'),('frame',2535,160,'帧 DMA','地址/stride')]:
  d.box(name,x,370,w,125,t,[sub],WHITE,size=26,subsize=20)
 for i,(a,b) in enumerate([(2035,2055),(2195,2215),(2355,2375),(2515,2535)]):d.line('pixel'+str(i),[(a,420),(b,420)],PIX)
 d.line('raw',[(2205,420),(2205,330),(2445,330),(2445,370)],PIX)
 d.el('circle','branch',cx=2205,cy=420,r=4,fill=PIX,stroke='none')
 d.text(2500,318,'RAW 旁路',22,color=PIX)
 d.path('isp-gb','M 2285 370 L 2285 340 C 2303 340 2303 320 2285 320 L 2285 280 L 1400 280 L 1400 305',GB,both=True)
 d.text(1910,273,'ISP 中间数据',21,color=GB)
 d.box('xbar',70,800,1260,120,'主 AXI Crossbar',['系统 64 bit'],PEACH,size=35)
 d.line('cpu-xbar',[(200,425),(200,700),(250,700),(250,800)])
 d.line('ara-xbar',[(782,555),(782,720),(700,720),(700,800)])
 d.box('atomics',400,1050,260,135,'原子适配',['AMO / LRSC'])
 d.box('llc',780,1050,290,135,'LLC / SPM',['保留 · 不等于 GB'])
 d.line('xbar-atomics',[(530,920),(530,1050)]);d.line('atomics-llc',[(660,1117),(780,1117)])
 d.rect('ddr',1400,800,1050,535,BLUE,dash=True);d.text(1925,1315,'DDR Controller · 多 AXI slave',29,bold=True)
 for n,x,sub in [(0,1460,'SoC / LLC'),(1,1850,'NPU / GB'),(2,2240,'帧写入')]:
  d.box('ddr-port'+str(n),x,930,160,100,'S'+str(n),[sub],WHITE,size=28,subsize=22)
  d.line('join'+str(n),[(x+80,1030),(x+80,1075)],arrow=False)
 d.line('llc-ddr',[(1070,1117),(1360,1117),(1360,895),(1540,895),(1540,930)])
 d.line('mover-ddr',[(1790,545),(1840,545),(1840,730),(1930,730),(1930,930)],both=True)
 d.line('frame-ddr',[(2615,495),(2615,730),(2320,730),(2320,930)])
 d.line('ports-merge',[(1540,1075),(2320,1075)],arrow=False)
 d.box('qos',1460,1140,310,130,'端口仲裁 / QoS',['共享 DDR 带宽'],WHITE)
 d.box('scheduler',1840,1140,550,130,'读写 / Bank / Row / 命令调度',[],WHITE,size=26)
 d.line('qos-in',[(1615,1075),(1615,1140)]);d.line('qos-core',[(1770,1205),(1840,1205)])
 d.box('phy-ddr',2500,1140,230,130,'PHY / DDR',['外存器件'],PURPLE)
 d.line('ddr-phy',[(2390,1205),(2500,1205)],both=True)
 d.text(715,1340,'GB 容量、bank、位宽及频率待定',27,color=MUTED)
 d.text(715,1385,'并行能力取决于 SRAM 带宽与分区',27,color=MUTED)
 d.legend([(AXI,'AXI / 外存通路'),(GB,'GB 本地读写'),(PIX,'像素流')]);return d

def initialization_hw_sw():
 d=D('启动初始化的软硬件对应关系','源码快照：Bootrom=1 · PlatformRom=0 · 内部 LLC · 根 SDK 载荷入口')
 d.domain('hardware',60,190,1210,960,'硬件：存储、总线与自主状态机',BLUE)
 d.domain('software',1450,190,890,960,'软件：由同一个 CVA6 执行',PINK)
 d.box('clock-reset',100,280,1130,60,'外围平台提供有效 clk_i / rst_ni',[],PURPLE,size=26)
 d.box('cpu',100,400,320,125,'CVA6',['取指并执行机器指令'],WHITE)
 d.box('bist',850,400,380,125,'LLC tag BIST',['复位后自主读写测试'],WHITE)
 d.line('clock-cpu',[(260,340),(260,400)],CTL);d.line('clock-bist',[(1040,340),(1040,400)],CTL)
 d.box('rom',100,610,470,210,'Boot ROM ① / ②',['0x02000000','cheshire_bootrom.sv','S / C 预编译为 ROM 内容'],WHITE)
 d.box('llc-regs',770,610,460,210,'LLC 配置寄存器',['DONE：完成 · BIST_OUT：错误','CFG_SPM / COMMIT'],PURPLE)
 d.line('cpu-rom',[(260,525),(260,610)]);d.line('bist-status',[(1040,525),(1040,610)])
 d.box('devices',100,940,470,150,'装载设备与通路',['SPI NOR / SD / EEPROM','UART / JTAG / Link'],WHITE)
 d.box('spm',770,940,460,150,'LLC 数据 / SPM',['载荷代码、数据与栈','tag BIST 不测试数据阵列'],TEAL)
 d.line('rom-driver',[(335,820),(335,940)],CTL)
 d.text(540,888,'ROM 中的设备驱动',24,color=CTL)
 d.line('load-bytes',[(570,1015),(770,1015)],GB)
 d.text(670,998,'搬运字节',22,color=GB)
 d.box('rom-asm',1500,280,790,220,'① Boot ROM 汇编',['cheshire_bootrom.S','整数环境、sp / gp；等待 LLC DONE','全 way 配为 SPM；建立早期栈'],WHITE,size=30,subsize=25)
 d.box('rom-c',1500,590,790,235,'② Boot ROM C 代码',['cheshire_bootrom.c','测频、boot_mode、装载驱动','把载荷装入内存 → 交接执行入口'],WHITE,size=30,subsize=25)
 d.box('crt0',1500,920,790,190,'③ 应用 / ZSL 启动代码',['sw/lib/crt0.S → 该载荷自己的 main','sp / gp、mtvec、BSS、FP 初始化','main 返回：发布 scratch2，然后 ret'],TEAL,size=30,subsize=25)
 d.line('asm-c',[(1895,500),(1895,590)],CTL);d.text(2060,555,'call ROM main',24,color=CTL)
 d.line('c-payload',[(1895,825),(1895,920)],GB);d.text(2090,880,'调用载荷入口',24,color=GB)
 d.line('poll-config',[(1500,390),(1360,390),(1360,715),(1230,715)],CTL)
 d.text(1360,775,'轮询 DONE',22,color=CTL);d.text(1360,810,'提交 SPM',22,color=CTL)
 d.line('image-entry',[(1230,1015),(1500,1015)],GB)
 d.text(1365,968,'镜像入口 _start',22,color=GB)
 d.text(950,1225,'装载驱动访问设备；应用 BSS 由该载荷 CRT0 清零',25,color=CTL)
 d.legend([(AXI,'硬件访问 / 状态'),(CTL,'软件调用 / 配置'),(GB,'载荷字节 / 入口对应')]);return d

def program_execution_flow():
 d=D('从复位到应用返回的程序执行流程','SPI NOR 自主启动：boot_mode=2 · PlatformRom=0 · 根 SDK CRT0')
 for id,x,w,t,c in [('rom-domain',60,740,'片上 Boot ROM 镜像',BLUE),('payload-domain',850,740,'SPM 中的应用 / ZSL 镜像',TEAL),('state-domain',1640,700,'完成后的状态与观察',PURPLE)]:
  d.domain(id,x,190,w,1030,t,c)
 stages=[('reset',100,280,660,100,'复位释放 → ROM _start',['cheshire_bootrom.S @ ROM'],WHITE),
 ('early',100,450,660,150,'早期环境与 LLC 初始化',['等待 BIST · 配置 SPM / 栈','PlatformRom=0：跳过平台钩子'],WHITE),
 ('rom-main',100,670,660,150,'cheshire_bootrom.c · main',['boot_mode / RTC 测频','boot_spi_s25fs512s 初始化 SPI'],WHITE),
 ('gpt-load',100,890,660,110,'gpt_boot_part_else_raw',['镜像字节 → SPM 的 code_buf'],WHITE),
 ('handoff',100,1080,660,95,'boot_next_stage',['jalr ra, 0(t0)'],WHITE),
 ('payload-start',890,280,660,100,'载荷 _start @ 镜像起点',['由 sw/lib/crt0.S 提供'],WHITE),
 ('runtime',890,450,660,160,'CRT0：应用运行环境',['sp / gp、mtvec、BSS、FP','保存进入应用的 ra；call main'],WHITE),
 ('app',890,710,660,170,'载荷自己的 main()',['执行任务','不返回则继续按程序运行'],WHITE),
 ('exit',890,1030,660,145,'应用 CRT0 · _exit',['scratch2 = (返回值 << 1) | 1','恢复栈上 sp / gp / ra，然后 ret'],WHITE),
 ('running',1680,280,620,220,'return 不会自动停机',['不自动复位 / 断电 / 换权限','CPU 仍由时钟驱动并继续取指'],WHITE),
 ('rom-return',1680,660,620,300,'当前 ROM 的调用后返回点',['boot_next_stage：jalr 后为 ret','未保存上一层 ra','可形成 ret 自循环（源码推导）','不是按设计进入 ROM _exit'],PINK),
 ('observer',1680,1040,620,150,'仿真 / 调试器等外部观察者',['读取 scratch2 完成标志','TB 可结束仿真；不等于 CPU 停机'],WHITE)]
 for id,x,y,w,h,t,s,c in stages:d.box(id,x,y,w,h,t,s,c,size=29,subsize=24)
 for i,(a,b) in enumerate([(380,450),(600,670),(820,890),(1000,1080)]):d.line('rom-step'+str(i),[(430,a),(430,b)])
 d.text(555,644,'call main',22,color=AXI)
 d.line('jalr-entry',[(760,1127),(820,1127),(820,330),(890,330)],GB)
 d.text(818,1280,'jalr：转入载荷入口',24,color=GB)
 d.line('start-runtime',[(1220,380),(1220,450)],GB)
 d.line('runtime-main',[(1220,610),(1220,710)],GB);d.text(1390,666,'call',23,color=GB)
 d.line('main-exit',[(1220,880),(1220,1030)],GB);d.text(1390,967,'main 正常返回',23,color=GB)
 d.line('return-rom',[(1550,1102),(1600,1102),(1600,810),(1680,810)],PIX)
 d.text(1610,780,'ret',22,color=PIX)
 d.line('observe',[(1550,1152),(1620,1152),(1620,1115),(1680,1115)],AXI)
 d.line('ret-loop',[(2300,810),(2320,810),(2320,610),(2100,610),(2100,660)],PIX)
 d.text(2100,585,'可能 ret 自循环',23,color=PIX)
 d.legend([(AXI,'ROM 流程 / 观察'),(GB,'载荷执行'),(PIX,'当前返回路径缺口')]);return d

def llc_cache_spm():
 d=D('LLC 多路组相联 Cache 与按 way 切换 SPM','DefaultCfg：8 way × 256 行/way × 8 个 64-bit 块/行 = 128 KiB；每 way 16 KiB',2800,1575)
 d.domain('cache',50,185,1650,920,'① 全 Cache · 8 路组相联 · CFG_SPM = 0x00',BLUE)
 d.domain('partition',1740,185,1010,920,'② 同一数据阵列按整 way 分配',TEAL)
 for id,x,w,t,s in [('tag',95,500,'Tag [47:14]','34 bit'),('set',595,350,'Set [13:6]','256 组'),('block',945,360,'Block [5:3]','8 个数据块'),('byte',1305,350,'Byte [2:0]','块内 8 字节')]:d.box(id,x,285,w,100,t,[s],WHITE,size=28)
 d.text(905,430,'选中一组；Tag 与各 way 的元数据并行比较',28,color=AXI)
 for c in range(8):d.text(325+170*c,480,'Way '+str(c),26,bold=True)
 d.rect('selected-set',230,713,1380,94,'#EDF6EE',GB,sw=2.5)
 for r,(y,label) in enumerate([(500,'组 0'),(610,'组 1'),(720,'组 42'),(915,'组 255')]):
  d.text(135,y+48,label,27,bold=r==2)
  for c in range(8):
   x=250+c*170;id=f'cell-{r}-{c}'
   d.box(id,x,y,150,80,'T / V / D',['64 B'],TEAL if (r,c)==(2,6) else WHITE,size=22,subsize=22)
   d.line('cell-sep-'+str(r)+'-'+str(c),[(x,y+40),(x+150,y+40)],GRAY,arrow=False,sw=1)
 for c in range(8):
  for k in range(3):d.el('circle',f'ellipsis-{c}-{k}',cx=325+170*c,cy=837+13*k,r=2.5,fill=MUTED,stroke='none')
 d.line('set-index',[(770,385),(770,400),(210,400),(210,760),(230,760)],GB)
 d.text(2245,264,'C = Cache · S = SPM',24,color=MUTED)
 d.text(905,1037,'示例命中：组 42 / Way 6，由 Tag + Valid 选 way',27,color=GB)
 d.text(905,1075,'未命中：替换 / 回填；Dirty 决定是否回写 DDR',25,color=MUTED)
 for r,(y,title,bits) in enumerate([(300,'0x00：128 KiB Cache','CCCCCCCC'),(495,'0x0F：64 KiB SPM + 64 KiB Cache','SSSSCCCC'),(690,'0xFF：128 KiB SPM；DDR 访问旁路','SSSSSSSS')]):
  d.text(1780,y,title,28,bold=True,anchor='start')
  for c,b in enumerate(bits):d.box(f'partition-{r}-{c}',1780+c*117,y+35,101,100,'W'+str(c),[b],PURPLE if b=='S' else WHITE,size=24)
 for y,s in [(920,'SPM 固定映射：base + way × 0x4000'),(964,'Way 2：0x10008000–0x1000BFFF'),(1008,'0x10008AAB → Way 2 / 组 42 / 块 5 / 字节 3'),(1052,'直接寻址；非 SPM way 的对应地址槽访问报错')]:d.text(2245,y,s,25)
 d.domain('transition',50,1150,2700,330,'③ 用途转换：软件目标位图 → 硬件协调提交与刷新',PEACH)
 seq=[('quiesce','停止相关访问',['迁移代码 / 栈 / 保留数据','协调缓冲与在途事务']),('cfg','写 CFG_SPM',['1 → SPM','0 → Cache']),('commit','写 COMMIT = 1',['发起配置提交']),('fsm','LLC 配置 FSM',['协调已有请求','必要 flush / Dirty 回写']),('resume','按寄存器契约确认完成',['恢复对新用途的访问'])]
 for i,(id,t,s) in enumerate(seq):
  x=85+i*535;d.box(id,x,1260,490,155,t,s,WHITE,size=28)
  if i<4:d.line('transition-'+str(i),[(x+490,1337),(x+535,1337)],CTL)
 d.text(75,1533,'SPM 复用原阵列；用途转换不自动复制数据。CPU L1 属性仍需单独处理。',27,anchor='start',color=MUTED);return d

def cheshire_software_hardware():
 d=D('Cheshire SoC 软硬件分层结构','裸机工程主线 · 功能库、设备控制、指令执行与片外器件分别表达',3200,1800)
 d.domain('applications',50,175,2500,170,'应用软件',PINK)
 apps=[('app-test','裸机应用与测试','HelloWorld / 结果校验'),('app-vector','向量算法','RVV / 矩阵计算'),('app-tools','系统工具','介质烧写 / 下载执行'),('app-image','图像处理与推理','ISP / NPU 工作负载〔规划〕')]
 for i,(id,t,s) in enumerate(apps):d.box(id,95+i*620,240,580,80,t,[s],WHITE,i==3,size=27,subsize=23)
 d.domain('base-software',50,385,2500,440,'基础软件 · 通用功能与设备控制',BLUE)
 for id,x,w,t,s in [('printf',100,330,'printf','格式化 → _putchar'),('gpt',480,350,'GPT 解析','read 回调访问介质'),('storage-hal',880,720,'存储器件 HAL','SPI Flash / SD / I²C EEPROM'),('debug-hal',1650,820,'UART debug HAL','READ / WRITE / EXEC')]:d.box(id,x,465,w,100,t,[s],WHITE,size=28)
 d.box('uart-dif',100,630,570,90,'UART DIF',['初始化 / FIFO 字节收发'],WHITE,size=28)
 d.box('serial-dif',720,630,1120,90,'SPI / I²C / GPIO DIF',['控制器配置 / 传输段 / 状态与寄存器'],WHITE,size=28)
 d.box('timer-dma',1890,630,580,90,'CLINT / DMA 接口',['计时 / 配置与提交'],WHITE,size=28)
 d.box('mmio',100,755,2370,50,'MMIO：reg8 / reg32 · mmio_region_read / write · 基址 + 偏移 + 位宽',[],PURPLE,size=25)
 d.line('printf-uart',[(265,565),(265,630)],CTL)
 d.line('gpt-hal',[(830,515),(880,515)],CTL)
 d.line('hal-dif',[(1240,565),(1240,630)],CTL)
 d.path('debug-uart','M 2060 565 L 2060 596 L 1254 596 C 1254 578 1226 578 1226 596 L 540 596 L 540 630',CTL)
 for i,x in enumerate([385,1280,2180]):d.line('dif-mmio'+str(i),[(x,720),(x,755)],CTL)
 d.domain('interfaces',50,865,2500,155,'软件可见的接口契约',TEAL)
 for i,(t,s) in enumerate([('指令执行','标量指令 / RVV'),('CSR 与特权状态','处理器配置与控制'),('内存与 MMIO','地址 / 属性 / 寄存器语义'),('异常与中断','事件入口 / 处理与返回')]):d.box('contract'+str(i),95+i*620,930,580,80,t,[s],WHITE,size=25,subsize=22)
 d.domain('hardware',50,1060,2500,435,'SoC 硬件 · 执行、存储与传输',PEACH)
 for i,(id,t,s,c) in enumerate([('cva6','CVA6','取指 / 执行 / 访存',BLUE),('ara','Ara','RVV / 向量访存',BLUE),('dma','iDMA','硬件数据搬运',BLUE),('future-ip','NPU / ISP / 图像接入','自定义 IP 与接口〔规划〕',TEAL)]):
  d.box(id,95+i*620,1140,580,100,t,[s],c,i==3,size=29)
 d.line('core-ara',[(675,1190),(715,1190)],CTL,both=True)
 d.box('axi',100,1290,2370,65,'AXI 互连与适配 · 地址路由 · 主设备共享访问',[],PEACH,size=30)
 for i,x in enumerate([385,1005,1625,2245]):d.line('hw-axi'+str(i),[(x,1240),(x,1290)],AXI,dash=i==3)
 d.box('memory',100,1400,1130,65,'原子适配 → LLC / SPM → 主存出口',[],BLUE,size=28)
 d.box('peripherals',1290,1400,1180,65,'Regbus → UART / SPI / I²C / GPIO / 中断 / 定时 / ROM',[],PURPLE,size=25)
 d.line('axi-memory',[(665,1355),(665,1400)]);d.line('axi-reg',[(1880,1355),(1880,1400)])
 d.domain('offchip',50,1535,2500,170,'片外器件 · 经对应控制器连接',WHITE)
 d.box('dram',100,1600,740,80,'DDR 存储器',['DDR Controller / PHY'],BLUE,size=27,subsize=23)
 d.box('media',890,1600,820,80,'Flash / SD / EEPROM',['SPI / I²C 控制器'],BLUE,size=27,subsize=23)
 d.box('sensor',1760,1600,710,80,'图像传感器〔规划〕',['LVDS 输入'],PEACH,True,size=27,subsize=23)
 d.line('memory-ddr',[(470,1465),(470,1600)],AXI)
 d.line('reg-media',[(1510,1465),(1510,1515),(1640,1515),(1640,1600)],AXI)
 # Peripheral input is a separate candidate route, not an output of the main bus.
 d.line('sensor-input',[(2470,1640),(2570,1640),(2570,1190),(2535,1190)],PIX,dash=True)
 sidebar=[('build',195,'开发主机：构建支持',['编译器 / 汇编器 / 链接器','Makefile / 链接脚本 / 库归档','生成 ELF 与代码数据布局'],BLUE,False),('runtime',535,'启动与运行支持',['Boot ROM / 载荷加载','crt0：栈 / BSS / 异常入口','进入 main；异常处理与返回'],PURPLE,False),('os',875,'可选操作系统',['RTOS：任务 / 调度 / 同步','Linux：用户态 / 内核 / 驱动','按各自环境建立设备访问路径'],TEAL,True),('platform',1215,'硬件实现与适配',['FPGA：现有 VCU118 工程','ASIC：宏 / 时钟 / PAD 适配','ASIC 实现与验证仍待完成'],PEACH,False)]
 for id,y,t,sub,c,opt in sidebar:d.box(id,2620,y,530,285,t,sub,c,opt,size=29,subsize=24)
 d.text(2885,1580,'LLC / AXI RT 等专用库',25,color=MUTED)
 d.text(2885,1620,'libcheshire.a 跨多个职责归档',23,color=MUTED)
 d.text(2885,1690,'虚线：规划扩展',24,color=MUTED)
 d.legend([(AXI,'硬件访问'),(CTL,'代表性调用 / 专用接口'),(PIX,'规划中的图像输入')]);return d

DRAWERS={f.__name__:f for f in [crossbar_ara,ddr_qos_proposal,example,initialization_hw_sw,program_execution_flow,cheshire_software_hardware,ddr_interconnect,llc_cache_spm]}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--out-dir',type=Path,required=True)
 p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
 p.add_argument('--skill',type=Path,default=Path.home()/'.codex/skills/svg-pptx-diagrams-native')
 a=p.parse_args()
 if a.out_dir.exists() and any(a.out_dir.iterdir()):p.error('Output directory must be new or empty')
 a.out_dir.mkdir(parents=True,exist_ok=True)
 source=a.repo/'docs_codex/diagrams/2026-10-11_native_reconstruction'
 input_names={p.stem for p in source.glob('*.svg') if not p.name.startswith('learn')}
 assert input_names==set(DRAWERS)|{'soc_full_architecture'},input_names
 module_path=Path(__file__).resolve().parent/'soc_layout.py'
 spec=importlib.util.spec_from_file_location('approved_soc_style',module_path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 drawings=[(n,f()) for n,f in DRAWERS.items()]+[('soc_full_architecture',mod.draw())]
 sys.path.insert(0,str(a.skill/'scripts'))
 from svg_to_pptx import read_svg,create_deck
 manifest=[];reports=[]
 for name,d in drawings:
  svg=a.out_dir/(name+'.svg');ET.indent(d.root,space='  ');ET.ElementTree(d.root).write(svg,encoding='utf-8',xml_declaration=True)
  canvas=[float(v) for v in d.root.get('viewBox').split()][2:]
  layout=dict(canvas=canvas,blocks=d.blocks,texts=d.texts)
  (a.out_dir/(name+'.layout.json')).write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
  report=create_deck([read_svg(svg)],a.out_dir/(name+'.pptx'),'source',font_file=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),slide_width_in=32)[0]
  report.update(source=name+'.svg',svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),office_display_editing_tested=False)
  (a.out_dir/(name+'.export.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');reports.append(report)
  original=source/(name+'.svg')
  manifest.append(dict(name=name,source=str(original.relative_to(a.repo)),source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
    method='regenerated user-approved industrial layout' if name=='soc_full_architecture' else 'redrawn layout and industrial styling',
    source_text=[''.join(e.itertext()) for e in ET.parse(original).getroot().iter() if e.tag.endswith('}text')]))
 deckreports=create_deck([read_svg(a.out_dir/(n+'.svg')) for n,_ in drawings],a.out_dir/'all_industrial.pptx','16:9',font_file=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),slide_width_in=32)
 (a.out_dir/'export_report.json').write_text(json.dumps(dict(figures=reports,combined_slides=deckreports,office_display_editing_tested=False),ensure_ascii=False,indent=2)+'\n')
 inventory=dict(input_head='c4162204cfee0c48b81158b4296860a678d92bec',skill='industrial-svg-pptx',figures=manifest,
 excluded_learning=[p.name for p in sorted(source.glob('learn*.svg'))],excluded_contact_sheets=[p.name for p in sorted(source.glob('contact-*.png'))])
 (a.out_dir/'source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(figures=len(drawings),objects=[r['objects'] for r in reports],native_arrows=[r['native_arrow_objects'] for r in reports]),ensure_ascii=False))
if __name__=='__main__':main()
