#!/usr/bin/env python3
"""43 current-course figures. New output directory required; old assets are immutable."""
import sys
sys.dont_write_bytecode = True
import argparse, json, hashlib
from pathlib import Path
from figure_primitives import Figure, BLUE, TEAL, ORANGE, PURPLE, RED, LINE, MUTED, INK, PALE
ROOT = Path(__file__).resolve().parent.parent
FIGURES = {}

def register(name):
    def dec(fn): FIGURES[name] = fn; return fn
    return dec

def F(title, subtitle, source, future=False):
    return Figure(title, subtitle, source, '未来方案 / 待实现与验证' if future else '当前源码结构 / 教学示意；非运行证据')

@register('depth-xbar-full')
def xbar():
    d=F('AXI Crossbar：7 个发起端、5 个目标与两级译码',
        '示例配置：DefaultCfg + Ara=1；单核、无外部扩展端口。灰线为可达连接；橙/蓝线为两个请求示例。',
        '源码：hw/cheshire_pkg.sv::gen_axi_in / gen_axi_out / gen_reg_out；hw/cheshire_soc.sv::i_axi_xbar')
    d.panel(320,175,795,680,'i_axi_xbar：逐输入分流，逐目标独立仲裁','blue')
    d.text(45,205,'发起端 / 请求进入 S 端',25,INK,True)
    d.text(1145,205,'目标 / 请求离开 M 端',25,INK,True)
    inputs=[('CVA6 core 0','L1 / ID 适配'),('Debug / SBA','调试装载发起端'),('Ara VLSU','失效过滤 / 位宽适配'),('iDMA 数据','主动搬运内存'),('Link RX','Serial Link 接收侧'),('VGA 取帧','读帧缓冲'),('USB DMA','描述符 / 数据')]
    targets=[('M0 · Debug 目标','调试模块地址空间；与 SBA 发起端分开'),('M1 · AXI → Reg32','原子适配 / cut / 桥 → 下方二级译码'),('M2 · LLC / SPM 共用出口','AMO / LRSC → cut / 地址重映射 → LLC'),('M3 · iDMA 控制','0x0100_0000 起；与数据发起端 S3 分开'),('M4 · Serial Link TX','[0x1_0000_0000, 0x2_0000_0000)')]
    ys=[255+i*86 for i in range(7)]; yt=[266+i*127 for i in range(5)]
    for i, ((title,body), y) in enumerate(zip(inputs,ys)):
        d.node('s'+str(i),45,y-32,250,78,f'S{i} · {title}',[body], 'orange' if i==0 else 'blue',20)
        d.node('d'+str(i),345,y-31,235,62,f'DEMUX S{i}',[], 'blue')
        d.connect('s'+str(i),'d'+str(i))
    for j,((title,body),y) in enumerate(zip(targets,yt)):
        d.node('m'+str(j),930,y-38,160,77,'MUX M'+str(j),['独立仲裁'],'blue',22)
        d.node('t'+str(j),1145,y-45,610,102,title,[body], 'orange' if j==1 else 'blue',22)
        d.connect('m'+str(j),'t'+str(j))
    for i,y in enumerate(ys):
        for j,z in enumerate(yt): d.curve((580,y),(930,z),LINE,1.3)
    d.curve((580,ys[0]),(930,yt[1]),ORANGE,5,True)
    d.curve((580,ys[2]),(930,yt[2]),BLUE,5,True)
    d.text(610,238,'AR / AW 地址译码',22,MUTED)
    d.text(598,837,'W 保存路由；B/R 按来源 ID 返回',22,TEAL)
    d.note(45,887,500,'请求与响应的归属', ['输入 ID=2 位 + 7 来源前缀=3 位', 'Crossbar 目标侧为 5 位；后级可再适配'],h=137)
    d.note(575,887,625,'M1 下游：reg_demux 二次译码', ['ROM / CLINT / PLIC / SoC / LLC 控制', 'UART / I2C / SPI / GPIO / Link / VGA / USB', 'BusErr；本例 CLIC / IRQ Router 均关闭'], 'orange',137)
    d.note(1230,887,525,'M2 下游：命中与外存分支',['128 KiB 阵列：SPM / cache ways', 'SPM 或 cache 命中可在片内结束', 'LLC 下游 → 平台 AXI4 DDR'], 'blue',137)
    return d

@register('mechanism-xbar')
def xbar_state():
    d=F('Crossbar 内部：选择目标、预留 W、归还 ID', '2×2 教学模型：普通 AXI4；输入 ID 为 2 位；地址与延迟不使用生产地址图。', '依据：axi_xbar_unmuxed、axi_mux、axi_demux_simple、axi_demux_id_counters（本地 axi 依赖）')
    d.panel(325,182,1040,570,'路由结构：两套输入状态 × 两套目标仲裁','blue')
    for i,y in enumerate([270,520]):
        d.node('i'+str(i),50,y,225,100,f'I{i} · '+['CPU','DMA'][i],['AW / W / AR'])
        d.node('d'+str(i),350,y-25,355,160,f'DEMUX I{i} · 地址分流',['AW/AR ID → 目标 + 在途数','w_select_q：W 的目标','w_open：未结束 W 数'])
        d.node('m'+str(i),1000,y-25,335,160,f'目标 {i} · mux / 仲裁',['AW 轮转仲裁并预留来源','i_w_fifo 保存来源顺序','W 按队首来源前进'])
        d.node('t'+str(i),1430,y,300,100,f'T{i} · '+['慢存储','快寄存器'][i],['独立背压与响应'])
        d.connect('i'+str(i),'d'+str(i));d.connect('m'+str(i),'t'+str(i))
    for i in range(2):
        for j in range(2): d.curve(d.port('d'+str(i)),d.port('m'+str(j),'l'),LINE,2)
    d.curve(d.port('d0'),d.port('m0','l'),ORANGE,5,True)
    d.curve(d.port('d1'),d.port('m0','l'),BLUE,5,True)
    d.text(740,715,'两笔请求竞争 T0；T1 仲裁器独立',22,MUTED,anchor='middle')
    d.note(50,790,525,'① W 路由先被预留',['仲裁决定可能先于外部 AW 握手', '背压期间保持决定，避免重复入队', '内部 WLAST 握手后 FIFO 才推进'],'orange',160)
    d.note(615,790,525,'② 最后 W ≠ 写响应完成',['B 握手释放写 ID 计数','最后 R 握手释放读 ID 计数','同 ID 跨目标须等原事务释放'],'blue',160)
    d.note(1180,790,550,'③ B / R 按 ID 来源前缀返回',['I0/id01 → 001；I1/id01 → 101','返回时按前缀选来源，再去前缀','端口 cut 使内外握手不必同周期'],'teal',160)
    return d

@register('new-system')
@register('depth-system-full')
def system():
    d=F('Cheshire / CVA6 / Ara：计算、控制与存储边界','可选 IP 是否存在由 Cfg 决定；数据箭头表示请求，响应沿相应事务返回。','源码：cheshire_soc.sv::gen_ara / i_axi_xbar / i_reg_demux / gen_llc；cheshire_pkg.sv')
    d.panel(40,175,1720,665,'Cheshire 数字 SoC 边界','blue')
    d.node('cpu',75,245,380,125,'CVA6',['取指 / 标量 / FPU / MMU','L1 cache 与写缓冲'])
    d.node('ara',710,245,390,125,'Ara · 可选',['dispatcher / VRF / lanes','VLSU：独立 AXI 访存'])
    d.node('masters',1340,245,385,125,'其他发起端',['Debug SBA / iDMA / Link','VGA / USB 数据请求'])
    d.connect('cpu','ara',color=PURPLE)
    d.text(470,284,'指令 / 操作数',22,PURPLE)
    d.text(480,347,'MMU / 完成 / 失效协作',20,PURPLE)
    d.node('xbar',270,450,1260,98,'AXI Crossbar',['每输入译码 / 分流；每目标仲裁；W 路由与 ID 响应跟踪'],'teal')
    for key in ['cpu','ara','masters']:
        x=d.port(key,'b')[0];d.connect(key,'xbar','b','t',via=[(x,405),(900,405)])
    for key,x,title,body,color in [('reg',75,'AXI → Reg 桥',['二级地址译码 → 启动 ROM','CLINT / PLIC / MMIO 控制'],'orange'),('mem',680,'原子处理 → LLC / SPM',['SPM / cache 共用片上阵列','LLC 下游 AXI → 平台外存'],'blue'),('duo',1285,'Debug / iDMA / Link 目标',['配置或对端访问窗口','与各自的发起端口分开'],'gray')]:
        d.node(key,x,650,440,130,title,body,color)
        d.connect('xbar',key,'b','t',via=[(900,600),(x+220,600)])
    d.note(75,880,760,'寄存器、引脚与事件',['CPU 写 MMIO → 外设状态机 → UART / SPI / I2C / GPIO 引脚','外设 IRQ 经同步 / PLIC 等入口返回 CPU'],'orange',130)
    d.note(935,880,790,'平台外存边界',['仿真：RAM 模型；FPGA：MIG / DDR；ASIC：待采购 CTRL + PHY','CVA6–Ara 控制接口、AXI 数据口、MMIO 与 IRQ 是不同路径'],'blue',130)
    return d

@register('depth-address-map')
def address():
    d=F('地址路由窗口与物理资源的映射','区间含起点、不含终点；图不按地址跨度比例。容量、权限与就绪状态分别判断。','源码：cheshire_pkg.sv::gen_axi_out / gen_reg_out / get_llc_size；默认配置')
    d.text(65,205,'AXI 地址范围',27,INK,True); d.text(1010,205,'路由去向与实际资源',27,INK,True)
    rows=[('0x0000_0000 … 0x0004_0000','Debug 目标','256 KiB 地址窗口；与 Debug SBA 发起口不同','gray'),('0x0100_0000 … 0x0100_1000','iDMA 控制','4 KiB 控制窗口；数据传输使用独立发起口','gray'),('0x0200_0000 … 0x0C00_0000','Reg 桥 → 二级译码','160 MiB 总窗口；包含空洞，不是连续 RAM','orange'),('0x1000_0000 / 0x1400_0000','同一 LLC / SPM 阵列','默认每个 SPM 别名各 128 KiB；并非双份容量','blue'),('0x8000_0000 … 0x1_0000_0000','LLC 下游主存','2 GiB 路由窗；实际 DDR 容量取决于平台','blue'),('0x1_0000_0000 … 0x2_0000_0000','Serial Link TX','4 GiB 对端窗口；受配置与地址映射约束','teal')]
    for i,(rng,title,body,color) in enumerate(rows):
        y=245+i*117
        d.node('a'+str(i),65,y,735,88,rng,[],color)
        d.node('b'+str(i),960,y,775,88,title,[body],color,22)
        d.connect('a'+str(i),'b'+str(i),color={'orange':ORANGE,'teal':TEAL}.get(color,BLUE))
    d.text(80,1000,'同一目标可有多个地址规则；关闭设备不等于其上层总窗口消失。未匹配访问应完成错误应答。',25,MUTED)
    return d

@register('new-memory')
def memory():
    d=F('LLC / SPM：两个别名如何访问同一组 ways','默认阵列：8 ways × 256 lines × 8 blocks × 8 B = 128 KiB；图中 way 分配仅示意。','源码：cheshire_pkg.sv::get_llc_size；cheshire_soc.sv::gen_llc；axi_llc 依赖')
    d.node('low',55,235,515,130,'低 SPM 别名 · 0x1000_0000',['CPU 属性允许缓存','与高别名映射同一物理阵列'],'orange')
    d.node('high',55,470,515,130,'高 SPM 别名 · 0x1400_0000',['教材共享实验仅通过此别名访问','仍须遵守缓冲区独占与可见性协议'],'teal')
    d.panel(785,200,930,530,'同一片上阵列：SPM 直接定位，cache 通过标签定位','blue')
    for i in range(8):
        x=810+i*109
        d.rect(x,290,98,300,PALE['blue'] if i<4 else PALE['teal'],LINE,5)
        d.text(x+49,333,'way '+str(i),21,INK,anchor='middle')
        d.text(x+49,387,'16 KiB',21,MUTED,anchor='middle')
        for j in range(4): d.line(x+8,425+j*35,x+90,425+j*35,LINE,1)
    d.text(820,650,'运行时分配可变；切换前处理脏行、栈、数据与在途事务',24,MUTED)
    d.arrow([(570,300),(690,300),(690,430),(785,430)],ORANGE)
    d.arrow([(570,535),(720,535),(720,495),(785,495)],TEAL)
    d.node('dram',55,820,690,150,'外存窗口 · 0x8000_0000 起',['cache 查标签：命中在片内完成','缺失：必要时脏行写回，再由外存填充'],'blue')
    d.node('out',980,820,735,150,'LLC 下游 AXI → 平台内存 / DDR',['SPM 地址命中不需要访问 DDR','ROM 主线在内部 LLC 存在时配置全 SPM'],'gray')
    d.connect('dram','out');d.arrow([(1240,730),(1240,790),(1320,790),(1320,820)])
    return d

@register('new-lanes')
def lanes():
    d=F('64 位 AXI 数据拍中的 32 位寄存器访问','一个 64 位总线拍有 8 个字节 lane；地址、WSTRB、数据位置与读返回必须一致适配。','依据：AXI byte-lane 语义；cheshire_idma_wrap 与 idma_reg64_2d_reg_top 的当前接口差异')
    d.text(60,220,'地址 +0：低 32 位有效',29,ORANGE,True)
    d.text(60,525,'地址 +4：高 32 位有效',29,BLUE,True)
    for row in range(2):
        y=260+row*305
        for i in range(8):
            active=(i<4 if row==0 else i>=4); x=65+i*209
            d.node(f'l{row}-{i}',x,y,196,165,'lane '+str(i),[f'bit {8*i+7}:{8*i}',f'STRB[{i}] = {int(active)}','有效字节' if active else '不写入'],('orange' if row==0 else 'blue') if active else 'gray',23)
        d.text(75,y+212,'WSTRB = '+['0x0F；WDATA[31:0] = value','0xF0；WDATA[63:32] = value'][row],26,[ORANGE,BLUE][row])
    d.note(65,885,790,'桥的写方向',['按地址选择 lane → 提取对应 32 位 → 保持字节使能','只改变 typedef 位宽，不会自动完成数据搬移'],'orange',128)
    d.note(905,885,825,'桥的读方向',['32 位寄存器值须回填到正确的 64 位总线 lane','DMA 控制位宽与 HAL ID 访问问题仍待专项验证'],'blue',128)
    return d

@register('new-transaction')
def transaction():
    d=F('AXI 写事务：地址、数据与响应三条独立通道','同一笔两拍写入；AW 与 W 可以独立提出。W 没有 WID，互连需要保存目标与来源。','依据：本地 axi_xbar / axi_mux / axi_demux_simple；教学事件图，不表示固定周期')
    xs=[190,665,1140,1615]; labels=['发起者','输入 demux','目标 mux','目标设备']
    for x,label in zip(xs,labels):
        d.node(label,x-140,185,280,72,label,[], 'blue');d.line(x,270,x,855,LINE,2,layer=d.back)
    events=[(325,0,3,'AW：addr / ID / LEN=1',ORANGE),(445,0,3,'W：D0 / STRB / LAST=0',BLUE),(565,0,3,'W：D1 / STRB / LAST=1',BLUE),(780,3,0,'B：ID / RESP；软件仍需检查结果',TEAL)]
    for y,a,b,label,color in events:
        d.arrow([(xs[a],y),(xs[b],y)],color,4);d.text(890,y-17,label,25,color,anchor='middle')
    d.node('saved',455,650,880,75,'路由状态跨周期保存',['目标 / 来源 FIFO / 同 ID 在途数'],'gray',22)
    d.note(55,900,530,'AW 被接收',['该接口接受写地址','不代表目标已经写入'],'orange',120)
    d.note(630,900,530,'W 末拍握手',['该接口结束本 burst 数据','B 响应仍可能在途'],'blue',120)
    d.note(1205,900,540,'B 握手并检查 RESP',['AXI 写事务响应已返回','设备动作完成语义仍由寄存器定义'],'teal',120)
    return d

@register('depth-cva6-ara')
def interface():
    d=F('CVA6–Ara：控制协议与 AXI 数据通路分离','当前 CvxifEn=0；名为 cvxif 的连接承载本地专用接口，不等于通用 CORE-V XIF。','源码：acc_dispatcher.sv；ara/intf_typedef.svh；cheshire_soc.sv::gen_ara')
    d.panel(50,185,440,650,'CVA6 标量核','orange');d.panel(1300,185,450,650,'Ara 向量单元','blue')
    d.node('decode',80,260,380,140,'译码 / scoreboard',['first-pass decoder','trans_id 关联标量指令'],'orange')
    d.node('acc',80,555,380,195,'acc_dispatcher',['队列 / 非推测发出','pending 与完成等待','CPU resp_ready 固定为 1'],'orange')
    d.node('dispatch',1330,260,390,140,'dispatcher / sequencer',['完整译码、vl / vtype','依赖与处理单元运行表'])
    d.node('vlsu',1330,555,390,195,'VRF / lanes / VLSU',['算术在分布式 VRF 上执行','地址检查 / 可选 MMU 翻译','独立 AXI 读写数据'])
    d.connect('decode','acc','b','t',ORANGE);d.connect('dispatch','vlsu','b','t',BLUE)
    for y,label,reverse,color in [(280,'req_valid / insn / rs1 / rs2 / frm / trans_id',False,ORANGE),(375,'req_ready；resp_valid / result / exception / ID',True,BLUE),(470,'load/store_complete / store_pending / fflags',True,TEAL),(565,'MMU 请求与应答；L1 invalidate 协作',True,PURPLE)]:
        d.arrow([(1300 if reverse else 490,y),(490 if reverse else 1300,y)],color,3)
        d.text(890,y-18,label,22,color,anchor='middle')
    d.note(535,670,715,'接受、应答、数据完成分别观察',['算术指令可能先应答，VRF 随后完成','load 地址应答不表示所有 AXI 数据已返回'],'teal',132)
    d.node('axi',400,910,1200,100,'Ara AXI → invalidation filter → 位宽适配 → Crossbar',['与 CPU L1 数据口分开；B 错误处理的本地 TODO 仍需动态验证'],'blue',23)
    d.connect('vlsu','axi','b','t',via=[(1525,860),(1000,860)])
    return d

@register('depth-ara-internals')
def ara():
    d=F('Ara 内部：向量元素分散到 lanes，再重排回内存','示例：VLEN=2048、2 lanes、32 个向量寄存器；每个寄存器 256 B，VRF 总计 8 KiB。','源码：ara.sv / lane.sv / vlsu.sv；数据分布示意，不表示每周期恰好完成一元素')
    d.node('disp',55,200,1680,98,'dispatcher → sequencer',['vtype / vl / vstart → 依赖跟踪、功能单元发出与完成汇总'],'purple')
    for i,x in enumerate([55,965]):
        d.panel(x,355,770,430,'lane '+str(i)+'：VRF 4 KiB','blue')
        d.node('vrf'+str(i),x+30,420,710,112,'分布式寄存器字节',['e32 元素 '+('0、2、4、6 …' if i==0 else '1、3、5、7 …'),'VLEN 与 lane 数共同决定存储分片'])
        d.node('alu'+str(i),x+30,610,330,115,'操作数队列 → ALU',['整数 / MUL / FPU'],'teal')
        d.node('res'+str(i),x+415,610,325,115,'结果写回 VRF',['按目标寄存器归位'],'blue')
        d.connect('vrf'+str(i),'alu'+str(i),'b','t',via=[(x+385,570),(x+195,570)])
        d.connect('alu'+str(i),'res'+str(i));d.arrow([(x+580,610),(x+580,565),(x+625,565),(x+625,532)],TEAL)
    d.node('cross',635,820,525,70,'masku / sldu：使能与跨 lane 交换',[],'purple')
    for x in [440,1350]:d.arrow([(x,298),(x,420)],PURPLE)
    d.arrow([(825,755),(900,755),(900,820)],PURPLE)
    d.arrow([(965,755),(925,755),(925,820)],PURPLE)
    d.arrow([(710,820),(710,800),(765,800),(765,785)],TEAL)
    d.arrow([(1090,820),(1090,800),(1040,800),(1040,785)],TEAL)
    d.node('vlsu',55,930,1680,83,'VLSU：连续内存 → load 分发 → lanes → store 重排 → AXI',['VRF 与临时 FIFO 不构成 NPU 可寻址共享 cache'],'orange',22)
    d.arrow([(440,785),(440,930)],BLUE);d.arrow([(1350,785),(1350,930)],BLUE)
    return d

@register('depth-vector-memory')
def vmem():
    d=F('向量访存：地址翻译与数据搬运是两条路径','控制平面确定地址、权限与异常；数据平面在 AXI 和分布式 VRF 之间传输。','源码：Ara addrgen / vldu / vstu；CVA6 load_store_unit；cheshire_soc::gen_ara')
    d.panel(45,185,1710,340,'地址 / 权限 / 异常平面','purple')
    d.node('regs',75,280,410,150,'CVA6 标量寄存器',['rs1 = base；rs2 = stride','vstart / 元素索引影响地址'],'orange')
    d.node('addr',660,280,430,150,'Ara addrgen',['base + 元素偏移','可选地址翻译与异常处理'],'purple')
    d.node('mmu',1295,280,430,150,'CVA6 MMU / LSU',['仲裁翻译、PMP / 权限','物理地址或异常返回'],'purple')
    d.connect('regs','addr',color=ORANGE);d.connect('addr','mmu',fa=.35,fb=.35,color=PURPLE)
    d.connect('mmu','addr','l','r',fa=.8,fb=.8,color=TEAL)
    d.panel(45,575,1710,280,'load / store 数据平面','blue')
    d.node('vrf',75,655,410,135,'VRF / lanes',['store 数据 / index / mask','load 目的寄存器'],'blue')
    d.node('vlsu',660,655,430,135,'VLSU · vldu / vstu',['队列、重排、字节计数','地址应答与数据完成分开'],'blue')
    d.node('axi',1295,655,430,135,'Ara AXI',['AR → / R ←','AW、W → / B ←'],'teal')
    d.connect('vrf','vlsu',fa=.35,fb=.35);d.connect('vlsu','vrf','l','r',fa=.8,fb=.8,color=TEAL)
    d.connect('vlsu','axi');d.connect('addr','vlsu','b','t',color=PURPLE)
    d.note(55,915,1690,'系统路径与验收边界',['失效过滤 / 位宽适配 → Crossbar → SPM 或 LLC → 外存；AXI 口独立于 CPU L1 数据口', '本地 store B 错误处理仍有 TODO；complete 不能单独作为传输成功证据'],'gray',115)
    return d

@register('mechanism-cva6')
def cva6():
    d=F('CVA6 功能层次：发射、执行、提交与系统接口','以职责和接口组织；不展开每一级流水线电路，也不把图中连线当成精确时序。','源码：core/cva6.sv / issue_stage.sv / ex_stage.sv / commit_stage.sv')
    d.node('front',60,220,480,160,'取指前端 / Icache',['PC 与指令流','RAS / BTB / BHT 分支预测'],'orange')
    d.node('issue',660,220,480,160,'译码 / 发射 / scoreboard',['操作数、依赖与资源检查','未完成指令与 trans_id 跟踪'],'blue')
    d.node('csr',1260,220,480,160,'CSR / trap 控制',['特权级、异常与中断','FS / VS 等运行时状态'],'purple')
    d.connect('front','issue');d.connect('csr','issue','l','r',color=PURPLE)
    cols=[(60,'整数 / 分支',['地址与标量计算','分支结果与控制流'],'orange'),(505,'标量 FPU',['浮点计算 / fflags','使用前正确设置 FS'],'blue'),(950,'标量 load / store',['MMU / PMP / Dcache','地址权限与数据返回'],'teal'),(1395,'Ara 专用接口',['请求 / 应答 / pending','Ara 自身 AXI 独立'],'purple')]
    for i,(x,t,b,c) in enumerate(cols):
        d.node('ex'+str(i),x,505,345,165,t,b,c)
        d.arrow([(900,380),(900,445),(x+172,445),(x+172,505)],BLUE)
    d.node('commit',250,805,1300,150,'结果关联与顺序提交',['返回结果匹配未完成指令；满足条件后更新架构状态','异常、重定向与资源等待属于控制反馈；本图仅保留主要职责联系'],'teal')
    for i,(x,_,_,_) in enumerate(cols): d.arrow([(x+172,670),(x+172,740),(900,740),(900,805)],TEAL)
    return d

@register('new-vector')
def vector():
    d=F('137 个 e32 元素：按实际 vl 分批执行','e32,m1；VLEN=2048 → VLMAX=64。示例 a[i]+b[i]→c[i]，尾部 9 个元素同样需要校验。','依据：教材 journey.c；RVV vsetvli 语义与当前 Ara 配置；非运行结果')
    d.node('cpu',55,215,465,160,'CPU 维护循环状态',['启用 VS；a0/a1/a2 = 数组地址','remaining 初值 137','调用 vsetvli 取得实际 vl'],'orange')
    d.node('ara',685,215,510,160,'Ara 执行一批',['vle32 a、b → vadd → vse32 c','本轮只处理 vl 个有效元素','地址增加 vl × 4 字节'],'blue')
    d.node('loop',1360,215,385,160,'循环继续条件',['remaining -= vl','非零则再设定 vl','不能每轮固定加 64'],'teal')
    d.connect('cpu','ara');d.connect('ara','loop');d.arrow([(1550,375),(1550,440),(290,440),(290,375)],TEAL)
    d.panel(55,500,1690,290,'内存中的逻辑序列（每格仅表示一段，不代表一个 lane）','gray')
    widths=[700,700,150]; x=85
    for i,(w,title,body) in enumerate(zip(widths,['第 1 批 · vl=64','第 2 批 · vl=64','尾批'],[['元素 0…63','256 B'],['元素 64…127','256 B'],['128…136','9 / 36 B']])):
        d.node('batch'+str(i),x,595,w,135,title,body,['blue','teal','orange'][i],22);x+=w+30
    d.note(55,875,520,'静态指令证据',['ELF 反汇编存在 V 指令','只能确认程序文件内容'],'gray',130)
    d.note(635,875,520,'执行轨迹证据',['目标确实执行向量路径','不能用构建成功代替'],'blue',130)
    d.note(1215,875,530,'数值与边界证据',['137 项结果逐项相等','尾部保护字保持预期'],'teal',130)
    return d

@register('depth-shared-current')
def current_sharing():
    d=F('当前共享数据：Ara 的失效协作有明确参与者','CPU / Ara 的协作不自动扩展到 iDMA、其他设备或未来 NPU。','源码：csr_regfile / acc_dispatcher / axi_inval_filter / cheshire_soc.sv')
    d.node('cpu',65,215,470,190,'CPU · WT L1D + 写缓冲',['一致性 CSR 与 pending 等待','是否存在缓存副本取决于属性','fence 与 cache 操作职责不同'],'orange')
    d.node('ara',665,215,470,190,'Ara · VRF / VLSU',['无独立地址标记 D-cache','store 通过自身 AXI AW/W','VRF 是寄存器文件'],'blue')
    d.node('other',1265,215,470,190,'iDMA / 其他设备',['独立 AXI 发起端','未自动加入 Ara 失效协议','驱动需管理数据可见性'],'gray')
    d.node('inval',665,525,470,125,'Ara AW 失效过滤',['向 CPU L1 发 line invalidate','同时处理系统方向访存'],'purple')
    d.connect('ara','inval','b','t');d.arrow([(665,585),(295,585),(295,405)],PURPLE)
    d.text(65,555,'L1 line invalidation',22,PURPLE)
    d.node('mem',280,775,1240,150,'Crossbar → 主存原子处理 → LLC / SPM → 外存',['CPU 属性、SPM 别名和 LLC way 模式共同决定缓存副本存在条件','全路径可见性须包含写缓冲、cache、副本、通知与消费者获取顺序'],'teal')
    for key,x in [('cpu',135),('inval',900),('other',1500)]:
        p=d.port(key,'b',.15 if key=='cpu' else .5); d.arrow([p,(x,715),(900,715),(900,775)],BLUE)
    d.text(70,1000,'教材实验：独占高别名 SPM 缓冲区；实验结果不能推导出任意主设备之间的硬件一致性。',25,MUTED)
    return d

@register('new-ownership')
def ownership():
    d=F('缓冲区交接：地址相同还需要所有权与可见性','以 CPU → 设备 → CPU 为例；三条泳道分别记录写入者、数据可见性和控制通知。','依据：教材共享缓冲区协议；fence 不替代 cache 清理 / 失效；非硬件自动一致性')
    cols=[(315,'CPU 拥有','orange'),(805,'硬件拥有','blue'),(1295,'CPU 重新拥有','teal')]
    for x,t,c in cols: d.panel(x,205,450,660,t,c)
    for y,label in [(340,'数据操作'),(540,'可见性操作'),(735,'控制交接')]: d.text(50,y,label,27,INK,True)
    data=[['写源数据 / 描述符','同步缓存并排空必要写入','发布任务 / doorbell'],['DMA / Ara / 设备读写','完成访问并排空结果写入','发布完成状态 / IRQ'],['读取并校验结果','acquire / 排序 / 必要失效','确认 token / 回收缓冲区']]
    for i,(x,_,c) in enumerate(cols):
        for j,t in enumerate(data[i]): d.node(f'o{i}{j}',x+25,285+j*200,400,105,t,[],c)
    for i in range(2): d.connect(f'o{i}2',f'o{i+1}2',color=TEAL)
    d.note(55,920,1690,'每次交接分别回答三个问题',['请求是否接受？设备是否处理完成？结果是否已对消费者可见？三者不能互相替代。'],'gray',100)
    return d

@register('depth-ownership')
def future_owner():
    d=F('未来异构任务：所有权状态与异常回收','硬件完成令牌须同时匹配 buffer、epoch 与状态；IRQ 仅触发软件查询。','依据：教材异构协议伪代码；NPU / ISP 尚未集成',True)
    states=[('free',65,240,'FREE',['分配 buffer','选择新 epoch'],'gray'),('prod',685,240,'PRODUCER',['独占写入','禁止并发修改'],'orange'),('pub',1305,240,'PUBLISHED',['排空结果写入','发布描述符'],'teal'),('rec',65,610,'RECLAIM',['确认消费者排空','回收前验证状态'],'teal'),('cons',685,610,'CONSUMER',['读取 / 计算','可写自己的结果'],'blue'),('queue',1305,610,'QUEUED',['通知消费者','转移所有权'],'purple')]
    for k,x,y,t,b,c in states:d.node(k,x,y,420,155,t,b,c)
    for a,b,sa,sb in [('free','prod','r','l'),('prod','pub','r','l'),('pub','queue','b','t'),('queue','cons','l','r'),('cons','rec','l','r'),('rec','free','t','b')]: d.connect(a,b,sa,sb,TEAL)
    d.note(65,880,1660,'任意在途状态发生超时 / 错误 → QUARANTINED',['先隔离并确认设备停止，再决定恢复或回收；过期完成令牌不得释放新 epoch 的缓冲区。'],'red',120)
    d.text(620,505,'正常转移形成闭环；异常路径进入隔离状态',26,MUTED)
    return d

@register('depth-npu-bypass')
@register('depth-shared-future')
def bypass():
    d=F('未来 DDR 旁路：数据汇合不等于一致性自动成立','CPU / Ara 保留 LLC 路径；NPU / ISP 数据绕过 LLC 是用户目标，尚未实现。','依据：当前 cheshire_soc.sv 主存路径与 M01 待定义接口契约',True)
    d.panel(60,190,755,540,'现有 CPU / Ara 主存路径','blue');d.panel(975,190,760,540,'未来 NPU / ISP 旁路','purple')
    d.node('cpu',105,270,665,135,'CPU / Ara / 当前互连',['L1 cache 与 pending 协作','访问共享数据须遵循所有权协议'])
    d.node('llc',105,535,665,130,'现有原子处理 → LLC / SPM',['缓存维护与 AMO / LRSC 监视边界','小块共享 SRAM / SPM 需另定义接入口'])
    d.node('npu',1020,270,670,135,'NPU / ISP 独立数据主端',['普通读写绕过 LLC','控制寄存器与完成 IRQ 另走控制面'],'purple')
    d.node('bridge',1020,535,670,130,'旁路适配：CDC / 限流 / ID',['宽度、突发、在途数与错误恢复','旁路普通写也可能影响 reservation'],'purple')
    d.connect('cpu','llc','b','t');d.connect('npu','bridge','b','t',PURPLE)
    d.node('ddr',405,820,990,100,'新增仲裁 / ID 与顺序适配 → AXI4 DDR CTRL + PHY',['共享地址布局、全路径可见性与原子协议需要联合验证'],'teal',23)
    d.connect('llc','ddr','b','t',via=[(437,770),(900,770)]);d.connect('bridge','ddr','b','t',PURPLE,via=[(1355,770),(900,770)])
    d.text(65,998,'契约选择：禁止设备进入共享原子区，或设计覆盖所有访问者的原子 / 一致性协议并验证。',25,RED)
    return d

@register('depth-clocks-current')
def clocks_current():
    d=F('当前时钟与事件：SoC 主域、异步入口、FPGA DDR 域','时钟域由真实连接划分；UART / SPI / I2C 的分频节拍不自动成为独立 SoC 输入时钟。','源码：cheshire_soc.sv；target/xilinx/src/dram_wrapper_xilinx.sv；各外设同步逻辑')
    d.panel(660,185,680,680,'clk_i / rst_ni：SoC 主时钟域','blue')
    d.node('soc',710,455,580,160,'CVA6 / Ara / AXI / LLC / Reg',['LLC 下游 AXI 仍属于 clk_i','外设状态机在其实际连接域运行','DM ndmreset_o 在本 SoC 未连接'])
    items=[('rtc_i','CLINT 同步后计数'),('JTAG tck / trst_n','DTM → DMI 跨域'),('Serial Link RX clock','源同步接收与跨域 FIFO'),('USB PHY clock/reset','PHY 域与系统逻辑'),('GPIO / 外部 IRQ','按配置同步 → 中断控制')]
    for i,(t,b) in enumerate(items):
        y=210+i*125;d.node('e'+str(i),60,y,485,96,t,[b],'orange',22)
        d.arrow([(545,y+48),(615,y+48),(615,535),(710,535)],ORANGE)
    d.node('cdc',1440,460,300,140,'AXI CDC',['FPGA 平台','跨域事务队列'],'purple')
    d.node('mig',1390,720,355,145,'MIG UI clock 域',['DDR 控制器 / PHY','平台复位与校准'],'teal')
    d.connect('soc','cdc');d.connect('cdc','mig','b','t',TEAL)
    d.note(60,925,1680,'跨域不是只给信号加寄存器',['单比特事件、计数、多位数据和 AXI 事务需不同同步契约；FIFO / CDC 的两侧复位还需协调在途事务。'],'gray',100)
    return d

@register('mechanism-clocks')
def pll():
    d=F('PLL、分频与门控：时钟生成和事务跨域分别设计','候选原理图：未指定最终 ASIC 频率、倍频值、电压或域划分。','依据：时钟生成通用原理；当前平台边界见 depth-clocks-current',True)
    d.node('ref',50,280,280,115,'参考时钟',['f_ref'],'orange')
    d.panel(410,205,610,440,'PLL 反馈环（简化原理）','purple')
    d.node('divn',445,285,235,115,'参考 ÷N',['送相位比较'],'purple')
    d.node('vco',745,285,235,115,'相位 / 振荡源',['闭环调节'],'purple')
    d.node('feedback',545,490,350,100,'反馈 ÷M',['锁定状态由平台监测'],'purple')
    d.connect('ref','divn',color=ORANGE);d.connect('divn','vco',color=PURPLE)
    d.arrow([(860,400),(860,465),(720,465),(720,490)],PURPLE)
    d.arrow([(545,540),(425,540),(425,435),(565,435),(565,400)],PURPLE)
    d.node('c0',1120,220,240,100,'输出 ÷C0',['系统时钟'],'blue')
    d.node('sys',1460,220,285,130,'系统域',['复位同步释放','CPU / 互连'],'blue')
    d.node('c1',1120,535,240,125,'输出 ÷C1',['门控：停止脉冲','安全开关时钟'],'teal')
    d.node('per',1460,535,285,130,'外设候选域',['本域复位同步','事务通过 CDC'],'teal')
    d.arrow([(980,345),(1070,345),(1070,270),(1120,270)],PURPLE)
    d.arrow([(980,345),(1070,345),(1070,597),(1120,597)],PURPLE)
    d.connect('c0','sys');d.connect('c1','per',color=TEAL)
    d.connect('sys','per','b','t',color=TEAL);d.text(1520,450,'CDC 桥',23,TEAL)
    d.note(50,790,790,'常开控制的事务顺序',['停发 → 排空 → 切换 / lock → 域内复位 / 就绪 → 放行','lock、复位释放与设备可工作是三个不同条件'],'orange',145)
    d.note(930,790,815,'分频 / 门控 / clock-enable',['分频改变周期；门控停止时钟脉冲','clock-enable 决定寄存器是否更新，不是新的时钟域'],'teal',145)
    return d

@register('depth-clocks-future')
def future_clocks():
    d=F('未来 ASIC：时钟、复位、电源分别划分责任','下列域为候选边界；具体频率、电压、PLL 数量和电源意图尚未冻结。','依据：平台启动与配置约定；工艺/IP 交付待确认',True)
    d.node('aon',55,220,475,615,'常开控制候选域',['参考时钟 / 安全启动源','PLL lock 同步与切换策略','复位原因 / 超时 / 故障回退','门控、隔离与保持控制','固件可重复访问的配置接口'],'orange')
    candidates=[(680,220,'CPU / Ara / SRAM',['同域或分域由时序与功耗决定','SRAM 宏与复位策略配套'],'blue'),(1250,220,'DDR CTRL / PHY',['参考时钟与训练 / 校准','init done 后允许新内存事务'],'teal'),(680,610,'NPU / ISP 候选域',['跨域 FIFO / AXI CDC','停发、排空、隔离与状态恢复'],'purple'),(1250,610,'PAD / LVDS / 外部 IO',['电平与源同步采样','CDC / RDC 与引脚约束'],'purple')]
    for i,(x,y,t,b,c) in enumerate(candidates):
        d.node('domain'+str(i),x,y,495,220,t,b,c)
    d.arrow([(530,400),(600,400),(600,330),(680,330)],ORANGE)
    d.arrow([(530,300),(575,300),(575,180),(1497,180),(1497,220)],ORANGE)
    d.arrow([(530,600),(600,600),(600,720),(680,720)],ORANGE)
    d.arrow([(530,750),(575,750),(575,875),(1497,875),(1497,830)],ORANGE)
    d.note(55,915,1690,'域边界交付需要成套证据',['时钟约束 + 复位时序 + CDC/RDC + 电源意图/库单元 + 固件控制 + 故障恢复测试；图中候选域不是已实现电源域。'],'gray',110)
    return d

@register('mechanism-power')
def power():
    d=F('关电域与常开域：隔离、保持、电平转换各有职责','示例 done 为有效高，接收协议允许隔离时钳为 0；实际钳位值按接口协议决定。','依据：ASIC 低功耗通用机制；需工艺库、UPF 与平台协议支持',True)
    d.panel(60,215,525,505,'可关断设备域','purple')
    d.node('state',100,330,440,185,'计算状态机',['普通寄存器掉电后丢失','done 输出 / 任务内部状态','电源撤除前先完成事务'],'purple')
    d.panel(715,215,1040,505,'常开控制与隔离供电边界','orange')
    d.node('isolation',750,330,445,185,'输出隔离单元',['隔离有效：done_out = 0','隔离解除：透传 done','钳低不能撤销已接受 AXI'],'orange')
    d.node('mail',1300,330,415,185,'完成邮箱 / 控制器',['记录 epoch 与所有权','匹配状态后回收 buffer','处理超时与错误'],'teal')
    d.connect('state','isolation',color=PURPLE);d.connect('isolation','mail',color=ORANGE)
    d.node('retain',130,600,365,90,'保持资源：独立供电',['仅保存选定状态'],'teal',22)
    d.connect('state','retain','b','t',TEAL)
    d.note(60,815,815,'关断顺序（需 IP 规范确认）',['停发并排空 → 保存必要状态 → 隔离','按平台顺序关时钟 / 电源；处理异常在途事务'],'orange',160)
    d.note(935,815,815,'恢复顺序与电平兼容',['供电 / 时钟稳定 → 复位 → 恢复 / 重建 → 就绪 → 解除隔离','电平转换负责电压兼容；保持负责状态，均不替代隔离'],'teal',160)
    return d

@register('depth-ddr')
def ddr_boundary():
    d=F('DDR 子系统：AXI 事务、控制器、PHY 与器件引脚','AXI 是事务接口；DQ / DQS / 命令引脚是存储器电气接口。两侧不能直接相连。','依据：现有 FPGA dram_wrapper_xilinx 边界；ASIC 供应商控制器/PHY 接口尚未冻结')
    d.panel(400,190,1050,470,'平台存储子系统：实现由 FPGA / ASIC 平台承担','teal')
    cols=[(50,270,'SoC LLC 下游',['AXI4 事务','ID / burst / STRB','RESP / 背压'],'blue'),(450,270,'适配 / 控制器',['可选 CDC / 宽度适配','地址映射、队列、调度','刷新与错误状态'],'teal'),(1000,270,'DDR PHY',['训练、采样、对齐','时钟与 DQ / DQS','命令 / 电气时序'],'purple'),(1500,270,'DRAM 器件',['bank / row / column','存储单元 / 刷新','引脚与板级连线'],'gray')]
    widths=[280,435,350,245]
    for i,((x,y,t,b,c),w) in enumerate(zip(cols,widths)):d.node('n'+str(i),x,y,w,245,t,b,c,23)
    for i in range(3):d.connect('n'+str(i),'n'+str(i+1),color=TEAL)
    d.node('fw',65,805,500,165,'平台初始化固件',['配置 PLL / 控制寄存器','轮询状态、超时与失败回退','运行软件可重复查询状态'],'orange')
    d.node('ready',710,805,1030,165,'放行条件：PLL lock + 初始化 / 校准完成 + 复位协调',['执行初始化的代码、栈必须先位于可用存储','供应商需给出 AXI 限制、容量、ECC / 错误、寄存器、模型与复位顺序'],'teal')
    d.connect('fw','ready',color=ORANGE);d.arrow([(970,805),(970,735),(665,735),(665,515)],ORANGE)
    return d

@register('mechanism-ddr')
def ddr_read():
    d=F('一次 DDR 读：请求调度与返回数据分别穿过控制器','通用原理图；地址位分配、bank 策略、队列容量与训练寄存器由实际供应商确定。','依据：DDR 控制器/PHY 通用职责；不表示固定周期，也不代表已完成 DDR 验证')
    titles=['AXI AR 队列','映射 / 调度','PHY 命令接口','DRAM bank']; bodies=[['保存地址 / ID / burst','接受 AR 只表示收下请求'],['bank / row / column','处理行命中、冲突、刷新'],['ACT / READ / PRE','满足器件命令时序'],['开行 / 列读 / 刷新','存储阵列输出数据']]
    for i,(t,b) in enumerate(zip(titles,bodies)):d.node('q'+str(i),55+i*440,245,370,175,t,b,['blue','teal','purple','gray'][i],23)
    for i in range(3):d.connect('q'+str(i),'q'+str(i+1))
    rets=[('AXI R 通道',['RID / RLAST / RESP','RREADY 背压时保持数据']),('返回缓冲',['按 AXI beat 重组','与原事务 ID 对应']),('PHY 采样 / 对齐',['训练确定采样关系','DQ / DQS 转为内部数据']),('DQ / DQS',['器件返回读数据','引脚电气时序'])]
    for i,(t,b) in enumerate(rets):d.node('r'+str(i),55+i*440,630,370,175,t,b,['blue','teal','purple','gray'][i],23)
    d.connect('q3','r3','b','t',TEAL)
    for i in range(3,0,-1):d.connect('r'+str(i),'r'+str(i-1),'l','r',TEAL)
    d.note(55,900,1690,'一次请求的延迟取决于多层状态',['行命中可以省去换行操作；行冲突、刷新、仲裁、跨域队列和 R 背压都会改变 AXI 侧观察到的延迟。'],'gray',110)
    return d

@register('new-configuration')
@register('teaching-config-contract')
def config():
    d=F('配置契约：profile、SoC Cfg、软件与运行状态共同约束','编译时配置生成硬件能力；软件 ISA / ABI / 链接布局必须与硬件及启动环境匹配。','源码：cheshire_pkg::gen_cva6_cfg / gen_axi_in/out；build_config_pkg；sw/sw.mk')
    for x,label,c in [(55,'CPU 配置链','blue'),(665,'系统结构配置链','teal'),(1275,'软件构建链','orange')]: d.panel(x,195,470,620,label,c)
    nodes=[('profile',80,275,'CVA6 profile',['ISA / cache / 资源原值'],'blue'),('override',80,500,'gen_cva6_cfg',['平台覆盖 PMP / CLIC 等字段','再由 build_config 派生内部能力'],'blue'),('cfg',690,275,'Cheshire Cfg',['Cfg.Ara / 核数 / 外设开关','Ara lanes / VLEN'],'teal'),('ports',690,500,'端口、类型与地址规则',['gen_axi_in / out / reg','数量变化影响索引与来源 ID'],'teal'),('sw',1300,275,'工具链 / 源码 / 库',['-march / -mabi / 链接脚本','启动对象与驱动头文件'],'orange'),('elf',1300,500,'ELF / map / dump',['字节、符号、入口与装载段','不能由编译成功推断目标运行'],'orange')]
    for k,x,y,t,b,c in nodes:d.node(k,x,y,420,150,t,b,c,23)
    for a,b in [('profile','override'),('cfg','ports'),('sw','elf')]:d.connect(a,b,'b','t')
    d.connect('cfg','override','l','r',color=PURPLE,via=[(610,350),(610,575)])
    d.text(560,450,'覆盖',22,PURPLE)
    d.text(90,745,'RTL 展开：CVA6 / Ara / 互连 / LLC / 外设',23,BLUE)
    d.text(1300,745,'装载程序与有效硬件匹配',23,ORANGE)
    d.note(55,895,1690,'运行时初始化不是再次生成硬件',['VS / FS、MMIO 配置、存储就绪、有效栈与入口：软件使用已存在的资源；SELCFG 不会自动替换 CPU profile。'],'purple',120)
    return d

@register('new-build')
def build():
    d=F('主机上的构建产物：每个文件回答不同问题','C / 汇编是程序描述；目标文件保存编码与重定位；ELF 将符号解析与内存布局落实。','依据：sw/sw.mk；sw/lib/crt0.S；当前链接脚本与教材 journey 构建入口')
    artifacts=[('journey.c','算法与结果校验','源程序'),('journey.i','宏展开、包含头文件','预处理结果'),('journey.s','选定 ISA 的指令序列','编译结果'),('journey.o','字节、符号、重定位','汇编结果')]
    for i,(t,b,c) in enumerate(artifacts):
        d.node('a'+str(i),55+i*440,230,370,165,t,[b,c],'blue',23)
        if i:d.connect('a'+str(i-1),'a'+str(i))
    d.node('lib',55,590,470,175,'crt0.o + libsupport.a',['入口 / BSS / FS 初始化','UART / CLINT / printf 等实现','库只提供被链接进程序的代码'],'orange')
    d.node('link',675,590,470,175,'链接器 + .ld',['解析符号与重定位','安排运行地址与装载段','检查容量、对齐与段布局'],'teal')
    d.node('elf',1295,590,450,175,'journey.spm.elf',['e_entry：应用入口','PT_LOAD：装载段','文件字节数与运行大小可不同'],'blue')
    d.connect('lib','link',color=ORANGE);d.connect('link','elf')
    d.arrow([(1560,395),(1560,475),(910,475),(910,590)],BLUE)
    d.note(55,885,1690,'旁证文件与验收用途',['map：段与符号来自哪里；nm：符号地址；dump：反汇编与静态指令。链接成功之后仍须装载、执行和检查数值。'],'gray',120)
    return d

@register('new-runtime')
def runtime():
    d=F('C 对象与运行内存：指令、初值、零初始化与栈','编译器按语义与优化分配存储；局部变量可以留在寄存器，不必全部占栈。','源码：教材 journey.c；sw/lib/crt0.S；sw/link/common.ldh 与 spm.ld')
    d.node('source',55,225,540,455,'C 层对象',['代码：main / make_value','已初始化：seed = 1','常量：greeting[]','零初始化：result[137]','局部 temporary：可在寄存器','函数参数 / 返回值：依 ABI'],'orange')
    rows=[('.text','机器指令，CPU 按 PC 取指','blue'),('.misc','常量与已初始化数据：greeting / seed','teal'),('.bss','运行时空间：137 × 4 = 548 B；crt0 清零','blue'),('stack / 寄存器','调用保存必要状态；无默认堆','purple')]
    for i,(t,b,c) in enumerate(rows):
        d.node('r'+str(i),820,220+i*145,915,110,t,[b],c,23)
        d.arrow([(595,300+i*90),(725,300+i*90),(725,275+i*145),(820,275+i*145)],COL(c))
    d.note(55,875,790,'函数调用示例',['main → make_value → ret；a0 传参 / 返回值，ra 保存返回地址','跨调用仍需保留的值按 ABI 约定保存'],'orange',135)
    d.note(925,875,810,'SPM 链接时的栈前提',['__stack_pointer$ = 0 表示应用沿用既有栈','不能把 0 写入 sp；首次栈访问前须有有效可写存储'],'purple',135)
    return d

def COL(c):return {'blue':BLUE,'teal':TEAL,'orange':ORANGE,'purple':PURPLE,'gray':MUTED}[c]

@register('new-boot')
@register('teaching-code-to-execution')
def boot():
    d=F('JTAG 直接装载：主机与目标两条时间线如何汇合','当前保留内部 LLC 的启动基线；VIP 只检查指定配置位，不能由此推断栈和 ROM C 已完成。','源码：hw/bootrom；sw/lib/crt0.S；elfloader.cpp；vip_cheshire_soc.sv')
    d.panel(55,190,745,780,'主机：构建器 / TB / JTAG VIP','orange')
    d.panel(990,190,755,780,'目标：ROM / 存储 / 应用','blue')
    left=[('ELF 与链接信息',['构建字节、入口、PT_LOAD','map / dump 用于静态核对']),('VIP 检查 SPM 配置位',['CFG_SPM_LOW.bit0','随后请求调试 halt']),('halt → SBA 写装载段',['目标存储须可写','按装载规则处理初值与零区']),('设置 DPC = ELF entry',['resume 后观察 UART / 状态','逐项结果与返回码共同判定'])]
    right=[('复位 PC → Boot ROM',['内部 LLC 存在：BIST / SPM 配置','按容量调整栈是独立步骤']),('CPU 进入调试暂停',['暂停不自动证明 sp 有效','核对 PC / sp；SBA 写入段']),('应用 _start / crt0',['继承有效栈；gp / BSS / FS','向量入口另正确设置 VS']),('main 与退出状态',['计算 / MMIO / UART','scratch2=(code<<1)|1；crt0 ret'])]
    for i,((lt,lb),(rt,rb)) in enumerate(zip(left,right)):
        y=265+i*165;d.node('l'+str(i),85,y,685,123,lt,lb,'orange',23);d.node('r'+str(i),1020,y,695,123,rt,rb,'blue',23)
        if i:d.connect('l'+str(i-1),'l'+str(i),'b','t',ORANGE);d.connect('r'+str(i-1),'r'+str(i),'b','t')
    d.connect('l1','r1',color=ORANGE)
    d.connect('l2','r1','r','l',ORANGE,via=[(885,657),(885,525)],fb=.78)
    d.connect('l3','r2','r','l',ORANGE,via=[(945,800),(945,657)],fa=.32)
    d.connect('r3','l3','l','r',TEAL,fa=.83,fb=.83)
    d.text(810,462,'halt',21,ORANGE);d.text(810,625,'段字节',21,ORANGE)
    d.text(806,760,'resume',21,ORANGE);d.text(810,845,'结果',21,TEAL)
    d.text(65,1015,'无内部 LLC：平台另供首次栈访问前的存储与有效 sp。Bootrom=0：平台承担第一阶段启动。',24,MUTED)
    return d

@register('new-device')
def device():
    d=F('一次 UART 寄存器访问：地址、寄存器副作用与引脚','同一地址访问谁由译码决定；写入产生什么动作由寄存器语义、访问宽度与设备状态决定。','源码：UART DIF / HAL；AXI→Reg / APB 适配；UART 寄存器实现')
    d.node('cpu',55,240,340,190,'CPU / 驱动',['volatile + 正确访问宽度','读取 LSR 检查发送条件','写 THR 提交一个字符'],'orange')
    d.node('bridge',505,240,345,190,'AXI → Reg / APB',['地址译码','byte lane / 字节使能','握手与错误响应'],'blue')
    d.node('fifo',960,240,345,190,'寄存器 / TX FIFO',['DLAB 选择寄存器用途','写入入队 / 状态更新','访问成功不代表发送结束'],'teal')
    d.node('pin',1415,240,330,190,'串行状态机',['波特率分频','起始位 / 数据 / 停止位','TX 引脚输出'],'purple')
    for a,b in [('cpu','bridge'),('bridge','fifo'),('fifo','pin')]:d.connect(a,b)
    d.panel(55,575,1690,235,'同时观察控制寄存器与外部波形','gray')
    d.text(90,650,'LSR / FIFO 状态',26,TEAL,True);d.text(660,650,'UART TX',26,PURPLE,True)
    d.lines(90,680,['可继续写入？FIFO 空？移位器也已空？','三个问题按具体状态位定义判断。'],500,24)
    pts=[(860,680),(940,680),(940,740),(1020,740),(1020,680),(1100,680),(1100,740),(1180,740),(1180,680),(1260,680),(1260,740),(1340,740),(1340,680),(1690,680)]
    d.arrow(pts,PURPLE,3,False);d.text(960,780,'起始位',22,MUTED);d.text(1190,780,'数据位示意',22,MUTED);d.text(1550,780,'停止位',22,MUTED)
    d.note(55,900,1690,'其他外设仍沿同一分析方法',['W1C、读弹出 FIFO、忙时写入、GPIO 电平都需要各自的寄存器契约；寄存器地址正确只是访问的第一步。'],'orange',110)
    return d

@register('new-interrupt')
def interrupt():
    d=F('外设事件进入 CPU：设备状态、PLIC 与 trap 服务闭环','PLIC 外部中断与 CLINT 定时器走不同入口；complete 不自动清除设备事件。','源码：PLIC / CLINT 接入；CPU 中断门控；现有驱动与 trap handler')
    nodes=[('dev',55,240,390,'设备事件',['FIFO / 状态置位','保持 IRQ 直到按协议清源'],'orange'),('plic',705,240,390,'PLIC',['pending / priority','enable / threshold'],'blue'),('cpu',1355,240,390,'CPU CSR 门控',['mie / mstatus / mcause','跳转 mtvec 的 trap 入口'],'purple')]
    for k,x,y,w,t,b,c in nodes:d.node(k,x,y,w,160,t,b,c)
    d.connect('dev','plic',color=ORANGE);d.connect('plic','cpu',color=PURPLE)
    d.node('handler',1190,590,555,165,'软件 handler',['识别外部中断 → PLIC claim','读取设备数据 / 清事件','PLIC complete → mret'],'teal')
    d.connect('cpu','handler','b','t',PURPLE)
    d.arrow([(1190,675),(250,675),(250,400)],TEAL);d.text(400,650,'处理并清设备源，再 complete；避免中断立即重入',24,TEAL)
    d.note(55,855,795,'PLIC 的 claim / complete',['claim 确认待服务来源；complete 结束服务状态','设备电平仍有效时，后续可能再次 pending'],'blue',150)
    d.note(950,855,795,'CLINT：独立的计时器入口',['mtime ≥ mtimecmp → MTIP → CPU 定时器中断','处理后将比较值推迟到下一次到期时间'],'purple',150)
    return d

@register('new-serial')
def serial():
    d=F('I2C EEPROM 与 SPI NOR：控制器动作映射到器件协议','固定读 16 字节；下图表示协议阶段与片选边界，不表示按比例绘制的电气时序。','依据：本地 EEPROM HAL 的 STOP/START 流程；SPI NOR 0x13 读命令；VIP 预填值 0x9a')
    d.panel(55,210,1690,325,'I2C：SDA / SCL 开漏，需要器件地址和内部地址','teal')
    seq=[('START + 写址','选择 EEPROM'),('16 位内部地址','设定器件读指针'),('STOP；新 START','本地 HAL 行为'),('读址 + 16 字节','接收并检查数据')]
    for i,(t,b) in enumerate(seq):
        d.node('i'+str(i),85+i*415,315,355,135,t,[b],'teal',22)
        if i:d.connect('i'+str(i-1),'i'+str(i),color=TEAL)
    d.panel(55,610,1690,260,'SPI NOR：控制器主动驱动 SCK；一次 CS1 有效覆盖命令、地址和读数据','blue')
    for i,(t,b) in enumerate([('CS1 有效','选择 Flash'),('命令 0x13','四字节地址读'),('四字节地址','指定读取起点'),('RX 16 字节','检查预期内容')]):
        d.node('s'+str(i),85+i*415,690,355,120,t,[b],'blue',22)
        if i:d.connect('s'+str(i-1),'s'+str(i))
    d.note(55,915,1690,'器件协议与平台支持分别验证',['EEPROM 当前流程不能标成 repeated START；SD 虽共用 SPI 控制器，但使用不同命令、响应与块校验协议。'],'gray',110)
    return d

@register('new-integration')
def integration():
    d=F('新增 IP：控制面、主动数据面与完成事件独立定义','从只读写寄存器的计算单元起步，再按需求增加 AXI 主端与 IRQ；不改变现有接口就不能假定具备新能力。','依据：Cheshire 扩展 Reg / AXI 端口；教材独立 Reg 单元；未来数据面尚需实现',True)
    d.node('cpu',55,280,385,205,'CPU / 驱动',['写参数 → START','轮询 STATUS / 读取 RESULT','中断模式仍需检查设备状态'],'orange')
    d.panel(595,200,680,650,'自有 IP 的职责边界','purple')
    d.node('reg',640,270,590,170,'Reg 目标：START / BUSY / DONE / ERROR',['地址、字节写、副作用与复位值','忙时提交、参数快照与结果稳定条件'],'orange')
    d.node('compute',640,580,590,180,'内部状态机 / 计算资源',['接受一次任务 → 执行 → 发布结果','局部复位要处理已接受事务','异常结束须保留可诊断状态'],'purple')
    d.connect('cpu','reg',color=ORANGE);d.connect('reg','compute','b','t',PURPLE)
    d.node('axi',1420,275,325,185,'可选 AXI 主端',['地址 / 长度 / 对齐','ID / 在途 / 错误恢复','共享缓冲区所有权'],'blue')
    d.node('irq',1420,595,325,165,'可选 IRQ → PLIC',['设备事件清除','claim / complete','不替代结果检查'],'teal')
    d.connect('compute','axi',color=BLUE);d.connect('compute','irq',color=TEAL)
    d.note(55,915,1690,'系统验收必须跨过接口边界',['寄存器副作用 → 一次受控任务 → 数值结果 → 错误 / 超时 / 重置；增加主端还要验证地址权限、缓存可见性与跨域排空。'],'gray',110)
    return d

@register('new-future')
def future_pipeline():
    d=F('未来图像系统：流数据、帧缓冲与控制路径分层','LVDS / ISP / NPU 均为待集成模块；带宽与缓存规模必须由分辨率、格式、帧率和访问次数推导。','依据：用户产品方向与未来 IP 集成契约；不代表已实现 RTL 或已验证吞吐',True)
    d.panel(55,210,1690,360,'像素 / 张量处理通路：每段需要格式、背压与时钟契约','purple')
    specs=[('LVDS 接收',['解串 / 像素打包','源同步采样 / 跨域 FIFO']),('ISP',['行缓存与图像算法','格式、位宽与边界处理']),('脉动阵列 / NPU',['命令与张量布局','片上复用与 AXI 读写']),('CPU / Ara',['调度与后处理','结果核对 / 下一阶段'])]
    for i,(t,b) in enumerate(specs):
        d.node('p'+str(i),85+i*415,310,350,175,t,b,'purple',23)
        if i:d.connect('p'+str(i-1),'p'+str(i),color=PURPLE)
    d.node('ddr',340,715,1120,160,'共享帧 / 张量缓冲 → AXI4 DDR 子系统',['NPU / ISP 数据旁路 LLC：需新增互连、仲裁、ID 与 CDC 契约','所有权、可见性、QoS、背压、异常恢复与带宽预算需联合设计'],'blue')
    for x in [675,1090,1505]:d.arrow([(x,485),(x,630),(900,630),(900,715)],BLUE)
    d.note(55,925,1690,'工程实施边界',['独立 cheshire_ara_asic/、固定配置、静态清单；Bender 至多用于一次性离线解析。图中系统仍需正式提取与验证。'],'orange',100)
    return d

@register('teaching-asic-responsibilities')
def asic():
    d=F('ASIC 交付边界：数字逻辑消费什么，工艺平台提供什么','当前 RTL 的功能边界与未来 SRAM / PLL / PAD / DDR 实现分层；不预设供应商或最终工艺。','依据：Cheshire 集成接口；tech_cells_generic；平台启动与配置约定',True)
    d.node('rtl',55,215,1690,130,'当前数字系统：CVA6 / Ara / AXI / Reg / LLC / 外设',['固定 Cfg、接口类型、软件地址与启动契约；RTL 存在不代表工艺实现可直接签核'],'blue')
    specs=[(55,'存储抽象 → 宏适配',['SRAM / ROM 端口、深度、位宽','读延迟、字节写、碰撞语义','DFT / MBIST / 修复脚','多一拍延迟须与消费者匹配'],'blue'),(635,'时钟 / 复位 / 电源',['PLL、门控与复位同步','安全启动、动态切换与回退','CDC / RDC、隔离与保持','频率 / 电压 / 域划分待确认'],'purple'),(1215,'外部 IO 与外存',['PAD、电平与引脚复用','DDR controller + PHY','训练、命令 / 数据时序与错误','授权接口摘要及受控模型'],'teal')]
    for i,(x,t,b,c) in enumerate(specs):
        d.node('r'+str(i),x,475,530,285,t,b,c)
        d.arrow([(x+265,345),(x+265,475)],COL(c))
    d.note(55,890,1690,'成套交付与验证',['宏模型 + RTL 适配 + 平台固件 + STA / CDC / RDC 约束 + DFT / MBIST + 电源意图；依次验收单元、平台启动和系统回归。'],'orange',125)
    return d

@register('new-route')
def route():
    d=F('七篇、30 章：由系统概念进入实现与验证','每一篇给出后续会消费的知识；章节编号从当前 pages.json 生成，避免沿用旧目录。','维护依据：scripts/pages.json；离线教材当前目录')
    meta=json.loads((ROOT/'scripts/pages.json').read_text())
    colors=['blue','purple','teal','orange','blue','purple','teal']
    desc=['辨认硬件职责、CPU 能力与配置约束','理解域边界、启动条件与安全恢复','跟踪地址、协议、存储和 DDR 事务','从源程序、ELF、启动到可观察执行','由 MMIO、驱动和外部事件解释设备','追踪向量指令、共享数据与异构交接','定义新 IP 契约与工艺平台交付']
    for i,(part,c,explain) in enumerate(zip(meta['parts'],colors,desc)):
        pages=[p for p in meta['pages'] if p.get('part')==part['id']]
        lo,hi=pages[0]['number'],pages[-1]['number'];y=195+i*117
        d.node('part'+str(i),55,y,545,92,f'{part["label"]} · {lo:02d}—{hi:02d}',[part['title']],c,23)
        d.node('knowledge'+str(i),745,y,990,92,explain,['进入各章后结合本地源码、使用条件与验证边界阅读'],c,22)
        d.connect('part'+str(i),'knowledge'+str(i),color=COL(c))
    return d

# Different abstraction levels receive different layouts, rather than duplicate pictures.
@register('new-system')
def system_example():
    d=F('三种访问辨认 SoC：字符输出、数组计算、调试装载','用具体请求区分控制面与数据面；Ara 由 CPU 向量指令驱动，并通过自身 AXI 口访存。','源码：cheshire_soc.sv；UART DIF；CVA6–Ara 专用控制接口')
    lanes=[(215,'① CPU 输出字符',['CPU store → UART THR','走寄存器控制路径'],['Crossbar → AXI/Reg → UART','TX FIFO / 串行状态机 → TX 引脚'],'orange'),(470,'② Ara 处理数组',['CPU 发向量指令 / 操作数','Ara VLSU 主动读写数据'],['Crossbar → LLC / SPM','片上命中或 LLC 下游外存'],'blue'),(725,'③ Debug 装载程序',['主机 JTAG → DTM / DM','SBA 成为 AXI 请求发起端'],['Crossbar → 目标可写内存','halt / 写段 / DPC / resume'],'teal')]
    for i,(y,t,a,b,c) in enumerate(lanes):
        d.panel(55,y,1690,215,t,c)
        d.node('a'+str(i),85,y+65,635,115,a[0],[a[1]],c,23)
        d.node('b'+str(i),1005,y+65,710,115,b[0],[b[1]],c,23)
        d.connect('a'+str(i),'b'+str(i),color=COL(c))
    d.text(65,1008,'控制寄存器口、主动数据口、完成事件口是不同角色；完整连接结构见下一张系统图。',25,MUTED)
    return d

@register('depth-shared-future')
def future_memory_spaces():
    d=F('未来共享存储：资源位置、访问路径与协议职责','共享地址空间只是第一步；选择 SPM / SRAM 或 DDR 还会改变容量、延迟和缓存边界。','依据：未来 M01 / I01 契约；当前 VRF 不是可被 NPU 共享寻址的 cache',True)
    d.node('cpu',55,230,440,150,'CPU / Ara',['任务控制与后处理','现有 LLC 路径'],'blue')
    d.node('npu',1305,230,440,150,'NPU / ISP',['独立数据发起端','未来 DDR 旁路'],'purple')
    d.node('sram',655,230,490,150,'共享 SPM / SRAM 候选',['小块数据 / 明确地址与所有权','新增接入路径需单独定义'],'teal')
    d.connect('cpu','sram');d.connect('npu','sram','l','r',PURPLE)
    d.node('llc',55,555,440,150,'现有 LLC 路径',['缓存副本与脏数据处理','CPU / Ara 维护条件'],'blue')
    d.node('bypass',1305,555,440,150,'旁路互连候选',['CDC / ID / 带宽与错误','与 LLC 下游汇合'],'purple')
    d.connect('cpu','llc','b','t');d.connect('npu','bypass','b','t',PURPLE)
    d.node('ddr',600,840,600,145,'AXI4 DDR CTRL + PHY + DRAM',['共用数据布局与可见性协议','普通旁路写也纳入原子 / LRSC 验证'],'teal')
    d.connect('llc','ddr','b','l',via=[(275,912)]);d.connect('bypass','ddr','b','r',PURPLE,via=[(1525,912)])
    d.note(655,525,490,'一次任务的协议',['谁可写？何时可读？','由谁发布、观察并核对完成？','超时后谁保证设备已停止？'],'orange',200)
    return d

@register('new-configuration')
def config_phases():
    d=F('配置何时生效：源码选择、展开结构与运行状态','同一个选项名可能属于不同阶段；软件写寄存器不能凭空增加 RTL 实例。','源码：cheshire.mk；cheshire_pkg；gen_cva6_cfg；sw/sw.mk')
    columns=[(55,'构建输入','orange'),(650,'展开后的硬件','blue'),(1245,'程序与运行状态','teal')]
    for x,t,c in columns:d.panel(x,205,500,650,t,c)
    entries=[['CPU profile / 宏 / targets','SoC Cfg 与 Ara lanes / VLEN','软件 -march / -mabi / .ld'],['有效 CVA6Cfg 与派生参数','端口数、索引、地址规则','实例存在性与接口位宽'],['ELF 指令与 ABI / 内存布局','VS / FS、设备 MMIO 状态','存储就绪、有效栈、装载入口']]
    for j,(x,t,c) in enumerate(columns):
        for i,txt in enumerate(entries[j]):d.node(f'c{j}{i}',x+25,300+i*175,450,110,txt,[],c)
    for i in [0,1]:d.connect(f'c0{i}',f'c1{i}',color=BLUE)
    d.connect('c02','c20','r','t',ORANGE,via=[(590,705),(590,185),(1495,185)])
    d.note(55,915,1690,'例：增加 AXI 发起端会牵动系统结构',['默认 6 来源，加 Ara 为 7；再增加两个外部来源为 9，来源前缀由 3 位增到 4 位。有效组合仍需检查软件与启动契约。'],'gray',110)
    return d

@register('teaching-code-to-execution')
def execution():
    d=F('从 C 到执行：主机产物如何变成目标内存与 CPU 状态','JTAG 直接加载路径；自主介质启动另由 ROM 按 GPT/raw 等规则读取镜像。','源码：sw/lib/crt0.S；hw/bootrom；elfloader.cpp；vip_cheshire_soc.sv')
    d.panel(55,205,725,665,'主机侧：字节、布局与入口','orange')
    d.panel(990,205,755,665,'目标侧：存储、寄存器与执行','blue')
    for k,x,y,t,b,c in [('source',85,285,'journey.c + crt0 + 支持库',['预处理 / 编译 / 汇编 / 链接'],'orange'),('elf',85,485,'ELF / map / dump',['PT_LOAD 决定段字节与地址','e_entry 决定应用入口'],'orange'),('loader',85,695,'主机 / VIP ELF loader',['解析段 → JTAG SBA 写内存','设置 DPC → resume'],'orange'),('rom',1020,285,'复位 PC → Boot ROM',['时钟 / 复位与存储初始化','独立确认首次栈访问条件'],'blue'),('mem',1020,485,'目标处于 halt 且存储可写',['代码、初值到达段地址','目标寄存器可由调试接口设置'],'blue'),('run',1020,695,'_start → crt0 → main',['gp / BSS / FS；向量入口设置 VS','MMIO / UART / 数值与退出状态'],'blue')]:
        d.node(k,x,y,665 if x==85 else 695,125,t,b,c,23)
    d.connect('source','elf','b','t',ORANGE);d.connect('elf','loader','b','t',ORANGE)
    d.connect('rom','mem','b','t');d.connect('mem','run','b','t')
    d.connect('loader','mem','r','l',ORANGE,via=[(885,757),(885,547)])
    d.text(810,465,'段字节',22,ORANGE);d.text(810,825,'DPC / resume',22,ORANGE)
    d.note(55,930,1690,'三个地址属于不同阶段',['复位 PC：最早取指位置；ELF e_entry：应用入口；main：由启动代码调用的 C 函数。它们不能互相替代。'],'gray',100)
    return d

WAVE_NOTES={
 'axi-backpressure':('背压区间保持负载；两拍 W 分别握手，最后再等 B。','AWVALID 与 AWREADY / WVALID 与 WREADY / BVALID 与 BREADY 各自决定接受。'),
 'boot-phases':('VIP 的配置位检查是观察点，不是 ROM 栈已完成的证明。','保留 LLC 的示例；halt 后另核对 sp 与可写存储，应用入口与复位 PC 分开。'),
 'vector-arithmetic':('请求接受与 CPU 应答先发生；VRF 的算术写回随后进行。','图为因果教学模型：CPU commit、Ara running、VRF write 不保证同周期结束。'),
 'vector-load':('地址应答、AR 接受、R 数据返回、load_complete 是不同事件。','RREADY=0 时数据保持；最后 R 及内部接收完成仍须分别核对。'),
 'reset-release':('电源、PLL、复位、DDR 就绪是分开的放行条件。','未来候选协议：各域异步置位 / 同步释放；图中跨域延迟省略。'),
 'handoff':('所有权变化需要可见性操作与匹配的完成令牌。','未来协议：epoch / status 匹配后再获取；超时进入隔离，不能直接复用缓冲区。')}

def waveform(stem):
    obj=json.loads((ROOT/'assets/waves'/f'{stem}.json').read_text()); signals=obj['signal']
    d=F(obj['head']['text'].split('（')[0], '保留原始信号序列；编号表示教学时间区间，不是实测周期。彩色数据块保持到边界所示事件。',
        '信号母版：assets/waves/'+stem+'.json；所有文字、波形段与总线块可独立编辑',stem in ['reset-release','handoff'])
    x0=345; total=1380; n=max(len(s['wave']) for s in signals); step=total/n
    top=230; rh=min(62,660/len(signals))
    for j in range(n+1):
        x=x0+j*step;d.line(x,210,x,top+rh*len(signals),LINE,1,layer=d.back);d.text(x,195,str(j),20,MUTED,anchor='middle')
    for i,sig in enumerate(signals):
        y=top+i*rh;d.rect(55,y-20,1690,rh, '#FFFFFF' if i%2 else '#F5F8FB','#FFFFFF',layer=d.back)
        d.text(72,y+18,sig['name'],22,INK,True)
        wave=sig['wave']; states=[];prev='x';data=iter(sig.get('data',[]));segments=[]
        for j,c in enumerate(wave):
            if c!='.':prev=c
            states.append(prev)
            if c in '23456789':segments.append((j,next(data,' '),c))
        if states[0]=='p':
            pts=[]
            for j in range(n):
                x=x0+j*step;pts += [(x,y+27),(x,y),(x+step*.5,y),(x+step*.5,y+27),(x+step,y+27)]
            d.arrow(pts,MUTED,2,False)
        elif all(s in '01' for s in states):
            pts=[];last=None
            for j,s in enumerate(states):
                yy=y+(0 if s=='1' else 27);x=x0+j*step
                if last is not None:pts.append((x,last))
                pts.extend([(x,yy),(x+step,yy)]);last=yy
            d.arrow(pts,BLUE,2.5,False)
        else:
            for j,s in enumerate(states):
                x=x0+j*step
                if s=='x': d.line(x,y+14,x+step,y+14,LINE,1.5)
            for j,label,c in segments:
                end=j+1
                while end<len(wave) and wave[end]=='.':end+=1
                x=x0+j*step;w=(end-j)*step
                d.emit('polygon',dict(points=f'{x},{y+14} {x+6},{y} {x+w-6},{y} {x+w},{y+14} {x+w-6},{y+28} {x+6},{y+28}',fill=PALE['teal' if c in '45' else 'orange'],stroke=TEAL if c in '45' else ORANGE,stroke_width=1.5))
                size=min(21,max(15,(w-8)/max(len(label)*.58,1)))
                d.text(x+w/2,y+22,label,size,INK,anchor='middle')
    for j in range(n+1):
        xx=x0+j*step; d.line(xx,210,xx,top+rh*len(signals),LINE,.6,layer=d.back)
    expanded={}
    for i,sig in enumerate(signals):
        state='x'; values=[]
        for char in sig['wave']:
            if char!='.':state=char
            values.append(state)
        expanded[sig['name']]=(i,values)
    for valid,ready in [('AWVALID','AWREADY'),('WVALID','WREADY'),('BVALID','BREADY'),('ARVALID','ARREADY'),('RVALID','RREADY'),('req_valid','req_ready'),('resp_valid','resp_ready')]:
        if valid not in expanded or ready not in expanded:continue
        i,vs=expanded[valid]; ri,rs=expanded[ready]
        for j,(v,r) in enumerate(zip(vs,rs)):
            xx=x0+j*step
            if v=='1' and r=='0':d.rect(xx,top+i*rh-20,step,(ri-i+1)*rh,PALE['orange'],PALE['orange'],layer=d.back)
            if v=='1' and r=='1':d.emit('circle',dict(cx=xx+step/2,cy=top+i*rh+13,r=4,fill=TEAL,stroke=TEAL,stroke_width=1))
    a,b=WAVE_NOTES[stem]
    if any('VALID' in sig['name'] or 'valid' in sig['name'] for sig in signals):
        d.text(55,910,'浅橙底：VALID=1、READY=0；绿点：两者同高的教学区间',20,MUTED)
    d.note(55,925,1690,a,[b],'teal',103)
    return d

for stem in WAVE_NOTES: FIGURES['depth-'+stem] = lambda s=stem:waveform(s)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out-dir',required=True,type=Path);args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=False)
    archive=json.loads((ROOT/'figure_archive/20261007/manifest.json').read_text())
    expected={Path(p).stem for p in archive['figures']};assert set(FIGURES)==expected,(set(FIGURES)-expected,expected-set(FIGURES))
    manifest={}
    for name,fn in sorted(FIGURES.items()):
        try:d=fn();p=args.out_dir/(name+'.svg');d.save(p)
        except Exception as e:raise RuntimeError('Figure '+name) from e
        manifest[name]={'title':d.title,'source':d.source,'status':d.status,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'previous':'assets/'+name+'.svg','current':'assets/figures-20261007/'+name+'.svg'}
    (args.out_dir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated {len(manifest)} structured SVG masters in {args.out_dir}')

if __name__=='__main__':main()
