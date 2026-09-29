#!/usr/bin/env python3
"""Generate repository-native SVG teaching diagrams, no network or rendering library."""
from pathlib import Path
from html import escape
import unicodedata
ROOT=Path(__file__).resolve().parent.parent
COL={'data':'#245fc7','control':'#16806b','irq':'#b94b29','clock':'#8251af'}
def lines(s,maxunits):
 out=[];line='';n=0
 for c in s:
  k=2 if unicodedata.east_asian_width(c) in 'WF' else 1
  if n+k>maxunits:out.append(line);line='';n=0
  line+=c;n+=k
 if line:out.append(line)
 return out
class SVG:
 def __init__(self,title,sub,h=800):
  self.h=h;self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="{h}" viewBox="0 0 1240 {h}" role="img"><title>{escape(title)}</title><rect width="1240" height="{h}" fill="#f5f8fc"/><defs>']
  for k,c in COL.items():self.a.append(f'<marker id="{k}" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9" fill="{c}"/></marker>')
  self.a.append('</defs><g font-family="Noto Sans CJK SC,Microsoft YaHei,sans-serif">')
  self.text(32,40,title,25);self.text(32,73,sub,16)
 def text(self,x,y,s,size=16,color='#20334c'):
  self.a.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(s)}</text>')
 def box(self,x,y,w,h,title,body='',kind='data',dash=False):
  self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" stroke="{COL[kind]}" stroke-width="2"'+(' stroke-dasharray="7 5"'if dash else '')+'/>')
  self.text(x+15,y+29,title,18,COL[kind]);yy=y+56
  for paragraph in body.split('|'):
   for line in lines(paragraph,int((w-30)/8)):
    self.text(x+15,yy,line,15);yy+=22
  assert yy<=y+h+8,(title,yy,y+h)
 def arrow(self,pts,label='',kind='data',labelpos=None,dash=False):
  self.a.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{COL[kind]}" stroke-width="2.5" marker-end="url(#{kind})"'+(' stroke-dasharray="6 5"'if dash else '')+'/>')
  if label:
   x,y=labelpos or pts[0];self.text(x,y-9,label,14,COL[kind])
 def finish(self,name,notes):
  y=self.h-105
  for n in notes:self.text(32,y,n,16);y+=24
  self.text(32,self.h-22,'教学示意 · 蓝：数据/请求  绿：控制/响应  橙：中断/错误  紫：时钟/复位 · 未标拍数不代表零延迟',14)
  self.a.append('</g></svg>');(ROOT/'assets'/f'{name}.svg').write_text('\n'.join(self.a)+'\n')
def chain(name,title,sub,nodes,notes):
 s=SVG(title,sub)
 for i,(title,body) in enumerate(nodes):
  row,col=divmod(i,3);x=35+col*410;y=135+row*245
  s.box(x,y,350,160,title,body,'control'if i<3 else 'data')
  if col<2:s.arrow([(x+350,y+80),(x+399,y+80)],kind='control')
 s.arrow([(1150,295),(1150,335),(15,335),(15,460),(35,460)],'继续推导',kind='control',labelpos=(600,331))
 s.finish(name,notes)
chain('hw-route','硬件学习路线：从预测结构到验证行为','CVA6了解接口；互连与适配读到事务状态，不要求逐级研究CPU流水线。',[
 ('H01 参数化RTL','profile / 宏 / 生成文件|展开不等于综合映射'),('H02 CVA6功能配置','cache / MMU / FPU / acc|原值→覆盖→派生→消费者'),('H03 SoC结构生成','master / target / address rule|关闭UART、开启Ara、旁路LLC'),('H04–H05 互连与适配','decode / demux / mux / ID|lane / bridge / cut / CDC'),('H06–H08 系统原理','存储 / DMA / 外设 / IRQ|时钟 / 复位 / 平台契约'),('H09 + 实验：接入IP','Reg控制→IRQ→AXI数据口|静态 / 教学模型 / 单元 / SoC')],['阅读产物：一张配置追踪表、一条事务路径、一份修改影响清单和一组正常/注错验收。','沿途可返回既有寄存器和软件章节；不将配置字典重复抄为正文。'])
s=SVG('源码、配置与生成物如何汇入硬件展开','输入汇合，不是运行时执行链；软件不能新增已被删去的硬件。')
s.box(30,125,330,130,'CPU profile','唯一cva6_config_pkg|RVV / cache / MMU / FPU','control')
s.box(450,125,330,130,'SoC Cfg','DefaultCfg + TB/wrapper覆盖|总线 / 外设 / LLC / Ara','control')
s.box(870,125,330,130,'生成包与清单','PLIC / CLINT / 寄存器尺寸|宏、类型与依赖实现','control')
s.box(220,350,450,140,'合并与派生','gen_cva6_cfg → build_config|gen_axi_in/out / gen_reg_out|类型宽度与地址规则','control')
s.arrow([(195,255),(195,310),(325,310),(325,338)],kind='control')
s.arrow([(615,255),(615,338)],kind='control')
s.box(830,350,370,140,'编译 + 展开','解析定义、计算常量|展开generate，建立实例与连接')
s.arrow([(670,415),(818,415)],'配置/类型',kind='control',labelpos=(695,405))
s.arrow([(1035,255),(1035,338)],kind='control')
s.box(830,560,370,115,'综合与工艺映射','优化与单元映射|实际面积/时序需报告')
s.box(220,560,450,115,'仿真与运行时操作','CSR / MMIO改变已存在电路的状态|动态观测不同于配置推导')
s.arrow([(945,490),(945,548)],kind='data')
s.arrow([(830,460),(740,460),(740,610),(682,610)],kind='control')
s.finish('hw-elaboration',['需分别保留源码清单、有效配置、展开层级与动态结果；仿真层级不等于综合后网表。'])
s=SVG('配置如何改变结构：UART 与 Ara 两个独立维度','编号是数组索引；地址是路由规则；中断号又是另一张表。')
for x,title,body in [(35,'DefaultCfg：6个发起端','CPU0 / Debug1 / DMA2|Link3 / VGA4 / USB5'),(650,'Ara=1：7个发起端','CPU0 / Debug1 / Ara2 / DMA3|Link4 / VGA5 / USB6')]:s.box(x,120,550,130,title,body)
s.arrow([(585,180),(638,180)],kind='control')
s.box(35,300,550,165,'Reg默认索引','err0 / CLINT1 / PLIC2 / regs3|BootROM4 / LLC5 / UART6 / I2C7|UART=0x03002000；I2C=0x03003000')
s.box(650,300,550,165,'仅关闭UART','UART实例与规则消失，输出/IRQ绑零|I2C索引变为6，地址仍0x03003000|第一层Reg大窗口仍在')
s.arrow([(585,380),(638,380)],kind='control')
s.box(35,510,1165,145,'两层译码：以UART关闭后的访问为例','0x03002000 → AXI目标Reg桥 → Reg无匹配 → Reg错误目标|0x03003000 → AXI目标Reg桥 → I2C新索引6 → I2C寄存器|Ara加入不改变UART地址；ID位宽：6→7仍加3位，9个来源才加4位')
s.finish('hw-topology',['三个生成函数分别维护发起端、AXI目标、Reg目标；多个地址窗口可指向同一目标。'])
s=SVG('Crossbar 2×2：分流与汇聚的组合','省略cut与逐位通道；B/R沿响应路径回到原输入。',900)
for y,src in [(130,'CPU：原ID=1'),(380,'DMA：原ID=1')]:
 s.box(25,y,180,125,src,'发起者|接xbar slave端')
 s.box(260,y,270,150,'输入侧 decode + demux','AW/AR分别译码|ID→目标、在途计数|W目标选择')
 s.arrow([(205,y+62),(248,y+62)])
for y,dst in [(130,'Reg桥'),(380,'主存')]:
 s.box(750,y,265,150,'目标侧 mux','AW/AR仲裁 + ID前缀|W来源FIFO|B/R按来源返回')
 s.box(1060,y,155,125,dst,'目标|接xbar master端')
 s.arrow([(1015,y+62),(1048,y+62)])
for ya in [205,455]:
 for yb in [205,455]:s.arrow([(530,ya),(738,yb)])
s.a.append('<rect x="543" y="293" width="180" height="29" rx="4" fill="#f5f8fc"/>')
s.text(548,315,'Connectivity[i][j]',15)
s.arrow([(1135,505),(1135,570),(130,570),(130,510)],'示例B/R：主存返回 → 来源识别/去前缀 → DMA',kind='control',labelpos=(430,560))
s.box(260,615,550,130,'错误路径与顺序约束：两种机制','未映射 / 禁止连接 → axi_err_slv → DECERR|同输入、同ID、同方向跨目标：等待旧事务完成','irq')
s.arrow([(390,530),(390,600)],kind='irq')
s.finish('hw-xbar',['不同目标可并行；相同目标需仲裁。来源编号用于区分不同master的同名ID。','当前SoC：Connectivity=全1，默认目标关闭，CUT_ALL_PORTS，内部PipelineStages=0。'])
s=SVG('写事务的状态：AW ≠ W ≠ B','教学顺序，不是真实周期；AW/W独立，背压时payload保持稳定。',820)
headers=['阶段','AW / 路由选择','W / 数据流','B / 完成','必须保留的状态']
xs=[25,155,445,710,880];ws=[120,280,255,160,335]
rows=[['①','CPU写地址被选中','数据可先到或后到','尚无响应','仲裁选择锁定'],['②','目标接受地址','等待WREADY','尚无响应','记录来源/目标'],['③','可有后续地址排队','中间拍被背压','尚无响应','WDATA/STRB/LAST稳定'],['④','写选择已建立','WLAST握手','可能仍未返回','推进W选择；保留响应跟踪'],['⑤','可继续接收新请求','下一burst可推进','BVALID & BREADY','检查BID/BRESP，结束响应']]
for x,w,t in zip(xs,ws,headers):s.box(x,115,w,64,t,'')
for i,row in enumerate(rows):
 y=205+i*85
 for x,w,t in zip(xs,ws,row):
  s.a.append(f'<rect x="{x}" y="{y-20}" width="{w}" height="75" rx="4" fill="white" stroke="#c8d5e5"/>')
  for j,line in enumerate(lines(t,int((w-16)/8))):s.text(x+8,y+8+j*22,line,15)
s.finish('hw-write',['axi_mux的W来源FIFO遵守AW选择；W没有WID，不能每拍重新选“当前最优”来源。','数据发完不等于结果可用；还要核对目标响应、设备完成协议与缓冲区所有权。'])
s=SVG('接口适配：64位的 +4 访问如何进入32位寄存器','自然对齐32-bit示例：AxSIZE=2；窄访问和总线宽度是两回事。')
s.box(35,130,350,180,'64-bit AXI侧','地址偏移 +4|WDATA有效部分在[63:32]|0x1122334400000000|WSTRB = 0xf0')
s.box(450,130,350,180,'转换与事务状态','根据地址低位选择lane|搬移data与strobe|匹配AW/W，返回B错误')
s.box(865,130,340,180,'32-bit Reg侧','addr：仍指向+4寄存器|wdata = 0x11223344|wstrb = 0xf|valid & ready才生效')
s.arrow([(385,210),(438,210)]);s.arrow([(800,210),(853,210)])
for x,t,b in [(35,'ID适配','不能直接截断ID|需要映射/序列化与响应跟踪'),(450,'cut / spill','保存payload与有效状态|在READY低时保持待成交拍'),(865,'CDC / 异步FIFO','跨域同步指针/握手|复位也必须遵守事务契约')]:s.box(x,400,340,175,t,b,'control')
s.finish('hw-adapters',['三种适配解决不同问题；增加cut不能替代CDC，ID适配不能替代原子来源USER编码。','只取低32位会丢失本例有效数据；当前DMA旧桥问题仍待独立动态验证。'])
s=SVG('存储路径与一致性边界','缓存命中不出下一级总线；SPM别名共用阵列。',900)
s.box(30,125,310,160,'CVA6：L1 I/D cache','tag/data、WT或WB、写缓冲|MMU/TLB影响地址与权限')
s.box(455,125,330,160,'Ara：控制与VLSU','CPU专用指令/翻译协作|独立向量AXI→失效过滤/变宽')
s.box(900,125,300,160,'DMA / USB / VGA','独立AXI发起者|不自动获得Ara缓存协作')
for x in [185,620,1050]:s.arrow([(x,285),(x,340),(620,340),(620,375)])
s.box(420,385,400,100,'主 AXI Crossbar','地址选择与响应归属')
s.arrow([(620,485),(620,535)])
s.box(30,550,325,125,'SPM窗口与别名','cached / uncached|重映射到同一LLC阵列')
s.box(420,550,400,125,'原子适配 → LLC/SPM','AMO/LRSC边界在LLC之前|命中、回填、回写、way用途')
s.box(900,550,300,125,'外部存储接口','FPGA：DDR wrapper / MIG|ASIC：未来DDR控制器/PHY')
s.arrow([(355,610),(408,610)]);s.arrow([(820,610),(888,610)])
s.finish('hw-memory',['来源路径与内存属性一起决定可见性；volatile/fence/旁路LLC都不能单独完成所有缓存维护。','未来NPU/ISP若下游汇入DDR，需要重新论证原子可见性和buffer所有权，本图未实现该旁路。'])
chain('hw-devices','外设内部：从寄存器到物理事件再返回中断','数据、控制状态和IRQ是三条相关但不同的链。',[
 ('CPU寄存器访问','地址/访问宽度/WSTRB|valid & ready只成交一次'),('寄存器与FIFO','RW/W1C/START/读弹出|队列满空与副作用'),('状态机与引脚','UART移位 / SPI片选|I2C开漏 / GPIO同步采样'),('设备事件锁存','硬件置位与软件清除优先级|mask决定是否输出IRQ'),('PLIC / CLIC / CLINT','按路径路由/优先级/许可|timer与外部IRQ机制不同'),('CPU handler','claim→处理/清设备原因|complete；未清可再次触发')],['UART FIFO空不保证移位寄存器发完；软件注入GPIO事件不验证真实引脚同步链。','控制器存在、平台接出、有设备模型、端到端通过必须分别提供证据。'])
chain('hw-platform','SoC运行平台的六份契约','当前FPGA/仿真连接与未来ASIC实现分开；不虚构电源域。',[
 ('时钟与复位','主域 / DDR UI / PHY|各域复位释放与CDC'),('Boot / Debug','启动地址 / ROM返回|JTAG加载、halt与resume'),('片上与外部存储','SPM栈与程序空间|DDR初始化/校准ready'),('接口与引脚','AXI宽度/ID/USER|PAD、开漏、IRQ同步'),('停止与恢复','停止新请求→排空/隔离|复位后重新初始化'),('真实验收','首条指令→SPM→UART|DDR→IRQ→DMA/Ara并发')],['FPGA的MMCM/MIG/XPM不直接等于ASIC的PLL/DDR PHY/SRAM宏。','当前没有完整电源意图证据；clock gating不是power gating，也不是事务隔离。'])
s=SVG('自定义IP教学案例：控制→中断→主动访存','实线：独立Reg加法设备；虚线：后续SoC接入与DMA扩展方案。',850)
s.box(30,140,280,145,'CPU / AXI→Reg桥','未来接入现有RegExt|地址窗口和宽度契约','control',True)
s.box(435,140,360,180,'独立 lesson_reg_adder','A/B按字节写 → START锁存|busy计数 → RESULT/DONE|STATUS W1C；IRQ_EN','data')
s.box(920,140,280,145,'PLIC / CPU IRQ','irq = DONE & IRQ_EN|清设备原因后complete','irq',True)
s.arrow([(310,220),(423,220)],'配置/读取','control',labelpos=(330,211),dash=True)
s.arrow([(795,220),(908,220)],'电平IRQ','irq',labelpos=(814,211),dash=True)
s.box(435,440,360,150,'未来数组数据引擎','源/目的/长度/任务标识|读写FIFO、burst、错误/完成','data',True)
s.box(920,440,280,150,'AXI master → 存储','AxiExt增加发起者|不是自动LLC旁路','data',True)
s.arrow([(615,320),(615,428)],'未来扩展描述符','control',labelpos=(630,385),dash=True)
s.arrow([(795,510),(908,510)],'数据读写','data',labelpos=(808,500),dash=True)
s.finish('hw-ip',['独立示例不包含AXI五通道、缓存一致性或生产地址分配；单元通过不等于SoC集成通过。','依次验收字节写/错误/重入、IRQ清除、背压/ID/4KiB边界，最后验证共享buffer协议。'])
print('Built 10 hardware SVG diagrams')
