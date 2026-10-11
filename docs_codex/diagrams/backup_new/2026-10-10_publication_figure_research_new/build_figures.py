#!/usr/bin/env python3
"""Reproduce the new figure sources in a fresh directory; never edits old inputs."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import ImageFont

NS = 'http://www.w3.org/2000/svg'
E.register_namespace('', NS)
INK, BLUE, LIGHT, GRAY = '#222222', '#17658A', '#E5F0F4', '#666666'
FONT = 'Liberation Sans'
FONT_PATH = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'


class Figure:
    def __init__(self, name, h, caption, source, mapping):
        self.name, self.h, self.caption, self.source, self.mapping = name, h, caption, source, mapping
        self.root = E.Element('{'+NS+'}svg', {'width':'182mm', 'height':f'{h*182/720}mm', 'viewBox':f'0 0 720 {h}'})
        self.text_boxes = []
        self.rect(0, 0, 720, h, fill='#FFFFFF', stroke='none')

    def add(self, tag, **a):
        return E.SubElement(self.root, '{'+NS+'}'+tag, {k.replace('_','-'):str(v) for k,v in {'id':f'{self.name}-{len(self.root):03}', **a}.items()})

    def rect(self, x, y, w, h, fill='none', stroke=INK, dash=False):
        return self.add('rect', x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=1,stroke_dasharray='5 3' if dash else 'none')

    def text(self, x, y, s, size=14, anchor='middle', color=INK, bold=False):
        n=self.add('text',x=x,y=y,fill=color,stroke='none',font_family=FONT,font_size=size,text_anchor=anchor,font_weight='bold' if bold else 'normal'); n.text=s
        font=ImageFont.truetype(FONT_PATH.replace('Regular','Bold') if bold else FONT_PATH, round(size*10))
        width=font.getlength(s)/10
        left=x-({'start':0,'middle':.5,'end':1}[anchor])*width
        box=(left,y-size*.82,left+width,y+size*.22,s)
        if left < 3 or left+width>717 or y-size<0 or y+size*.25>self.h:
            raise ValueError(f'{self.name}: out of bounds text {s}: {box}')
        self.text_boxes.append(box)

    def block(self,x,y,w,h,label,fill='none',dash=False,size=14):
        self.rect(x,y,w,h,fill=fill,dash=dash)
        labels=label.split('\n'); spacing=17
        for i,s in enumerate(labels):
            self.text(x+w/2,y+h/2+(i-(len(labels)-1)/2)*spacing+4.5,s,size=size)

    def line(self, points, color=INK, width=1.2, dash=False):
        self.add('polyline',points=' '.join(f'{x},{y}' for x,y in points),fill='none',stroke=color,stroke_width=width,stroke_dasharray='5 3' if dash else 'none')

    def arrow(self,points,color=INK,both=False,dash=False):
        self.line(points,color,1.3,dash)
        def head(tip,base):
            dx,dy=tip[0]-base[0],tip[1]-base[1]; norm=math.hypot(dx,dy); dx/=norm; dy/=norm
            b=(tip[0]-6*dx,tip[1]-6*dy)
            self.add('polygon',points=f'{tip[0]},{tip[1]} {b[0]-2.8*dy},{b[1]+2.8*dx} {b[0]+2.8*dy},{b[1]-2.8*dx}',fill=color,stroke='none')
        head(points[-1],points[-2])
        if both: head(points[0],points[1])

    def dot(self,x,y,color=INK,r=2.3):
        self.add('circle',cx=x,cy=y,r=r,fill=color,stroke='none')

    def mux(self,x,y,w,h,label='MUX',down=False):
        points=f'{x},{y} {x+w},{y} {x+w-8},{y+h} {x+8},{y+h}' if down else f'{x},{y} {x+w},{y+8} {x+w},{y+h-8} {x},{y+h}'
        self.add('polygon',points=points,fill='#FFFFFF',stroke=INK,stroke_width=1)
        if label: self.text(x+w/2,y+h/2+5,label,size=13)

    def finish(self, folder):
        overlaps=[]
        for i,a in enumerate(self.text_boxes):
            for b in self.text_boxes[i+1:]:
                if min(a[2],b[2])-max(a[0],b[0])>1 and min(a[3],b[3])-max(a[1],b[1])>1:
                    overlaps.append([a[4],b[4]])
        if overlaps: raise ValueError(f'{self.name}: text overlaps {overlaps}')
        E.indent(self.root)
        E.ElementTree(self.root).write(folder/(self.name+'.svg'),encoding='utf-8',xml_declaration=True)
        return {'name':self.name,'height':self.h,'width_mm':182,'caption':self.caption,'source':self.source,'mapping':self.mapping,'text_count':len(self.text_boxes),'text_bbox_overlaps':overlaps}


def crossbar():
    f=Figure('crossbar_ara',480,
      '仿真 Ara 配置的 7×5 全连接 AXI Crossbar。每个输入按 AR/AW 地址译码；每个输出独立仲裁。矩阵实心点表示可达连接，蓝色折线是 Ara→主存端口的请求示例；不同输出可并行，同一输出在该处竞争。S 为 Crossbar 从端口，接发起者；M 为主端口，接目标。箭头是逻辑请求方向，R/B 返回通道省略。',
      '2026-10-06_axi_crossbar_ara/ppt_editable_final/crossbar_ara_ppt.svg',
      '7个输入、5个输出、每输入DEMUX/每输出MUX、全连接→本图；配置、地址窗口、RT与FPGA差异→图注补充。')
    f.text(85,25,'AXI masters',bold=True); f.text(251,25,'Decode',bold=True); f.text(438,25,'Reachability',bold=True)
    names=['CVA6','Debug SBA','Ara','iDMA data','Serial Link RX','VGA','USB DMA']
    cols=[330,382,434,486,538]
    for i,name in enumerate(names):
        y=62+i*36
        f.block(20,y-13,137,26,name); f.text(176,y+5,f'S{i}',size=13)
        f.arrow([(191,y),(215,y)])
        f.block(215,y-13,72,26,'DEMUX',size=13)
        f.line([(287,y),(538,y)],'#999999',.9)
        for x in cols: f.dot(x,y,color=GRAY,r=1.8)
    for i,x in enumerate(cols):
        f.line([(x,48),(x,330)],'#999999',.9)
        f.mux(x-20,330,40,30,label='arb.',down=True); f.text(x,384,f'M{i}',size=13)
    f.arrow([(287,134),(434,134),(434,330)],BLUE)
    f.text(620,138,'Ara request',size=13,color=BLUE)
    targets=[('M0','Debug target'),('M1','Regbus'),('M2','AMO / LLC / SPM'),('M3','iDMA control'),('M4','Serial Link TX')]
    # Target legend is the port map, not a prose explanation panel.
    for i,(port,label) in enumerate(targets):
        x=22+(i%3)*234; y=420+(i//3)*37
        f.text(x,y,port,anchor='start',bold=True); f.text(x+29,y,label,anchor='start',size=13)
    return f


def ddr_old():
    f=Figure('ddr_qos_proposal',300,
      '2026-10-06 三端口接入建议的重绘：SoC 经现有原子适配和 LLC 接 S0，ISP 与 NPU 数据分别旁路至 S1/S2。虚线轮廓表示候选控制器边界，内部逻辑为接入抽象；多端口共享同一 DDR 带宽。该历史方案与 2026-10-10 的 GB/统一搬运器方案并列保留，不把两个版本拼成已经实现的架构。',
      '2026-10-06_axi_crossbar_ara/ppt_editable_final/ddr_qos_proposal_ppt.svg',
      '三个请求源、LLC旁路、端口仲裁与命令调度→本图；供应商约束和一致性边界→图注。')
    f.block(16,42,118,44,'CVA6 + Ara'); f.block(166,42,112,44,'AXI Xbar'); f.block(310,42,124,44,'AMO / LLC')
    f.arrow([(134,64),(166,64)]); f.arrow([(278,64),(310,64)]); f.arrow([(434,64),(473,64)])
    f.block(310,122,124,38,'ISP master'); f.arrow([(434,141),(473,141)],BLUE)
    f.block(310,205,124,38,'NPU master'); f.arrow([(434,224),(473,224)],BLUE)
    f.rect(473,22,220,236,dash=True)
    f.text(583,15,'DDR controller (proposed)',size=13)
    for i,y in enumerate([64,141,224]): f.text(489,y-9,f'S{i}',size=13); f.line([(473,y),(516,y)])
    f.block(516,40,72,202,'Arbiter\n/ QoS'); f.block(612,40,64,202,'DRAM\nsched.',size=13)
    f.arrow([(588,141),(612,141)]); f.arrow([(644,242),(644,277),(470,277)])
    f.text(455,282,'PHY / DDR',anchor='end')
    return f


def boot_hw():
    f=Figure('initialization_hw_sw',380,
      'Bootrom=1、PlatformRom=0、内部 LLC 启用时的初始化对应关系。左侧各软件阶段由同一个 CVA6 执行；右侧为所访问的硬件资源。箭头按标签表示读取、配置或装载。LLC tag BIST 为硬件自主过程，DONE 仅表示完成，错误由 BIST_OUT 表示；不覆盖数据 SRAM。',
      '2026-10-08_boot_initialization/initialization_hw_sw.svg',
      '硬件/软件对应关系→本图；ROM与CRT0具体顺序→program_execution_flow；测试边界、平台钩子→图注。')
    f.text(140,26,'CVA6 execution',bold=True); f.text(550,26,'Hardware resources',bold=True)
    f.block(38,52,204,66,'Boot ROM assembly\ncheshire_bootrom.S')
    f.block(38,169,204,66,'Boot ROM C\ncheshire_bootrom.c')
    f.block(38,290,204,60,'Payload CRT0\nsw/lib/crt0.S')
    f.arrow([(140,118),(140,169)]); f.arrow([(140,235),(140,290)])
    f.block(476,52,203,66,'LLC configuration\nDONE / BIST_OUT\nCFG_SPM / COMMIT')
    f.block(476,168,203,55,'SPI / SD / EEPROM')
    f.block(476,279,203,71,'LLC data array / SPM\nCode · data · stack')
    f.arrow([(242,72),(476,72)]); f.text(356,63,'poll / configure',size=13)
    f.arrow([(242,188),(476,188)]); f.text(355,179,'device driver',size=13)
    f.arrow([(242,218),(363,218),(363,300),(476,300)]); f.text(351,265,'load',anchor='end',size=13)
    f.arrow([(242,326),(476,326)]); f.text(356,317,'stack / clear .bss',size=13)
    f.text(578,144,'Tag BIST (autonomous)',size=13); f.arrow([(578,130),(578,118)])
    return f


def boot_flow():
    f=Figure('program_execution_flow',465,
      'SPI NOR 自主启动（boot_mode=2）的代表控制流。ROM 经 GPT/raw 装载载荷后调用入口，载荷 CRT0 建立环境并调用 main。正常返回由 CRT0 写 scratch2=(返回值<<1)|1，再恢复入口 sp/gp/ra 并 ret。虚线返回段为当前源码推导的 ROM 返回缺陷，不是期望的停机过程，也不是实测轨迹。',
      '2026-10-08_boot_initialization/program_execution_flow.svg',
      'ROM→GPT/raw→载荷CRT0→main→_exit→ROM返回点→本图；观察者、返回契约区别→图注。')
    f.text(162,25,'Boot ROM',bold=True); f.text(532,25,'Payload in SPM',bold=True)
    blocks=[(44,'Reset → ROM _start'),(110,'LLC / SPM / stack'),(176,'ROM main / SPI init'),(242,'GPT or raw load'),(308,'boot_next_stage')]
    for y,s in blocks: f.block(46,y,230,40,s)
    for a,b in zip(blocks,blocks[1:]):f.arrow([(161,a[0]+40),(161,b[0])])
    right=[(44,'Payload _start'),(110,'CRT0: sp / gp / mtvec / .bss'),(176,'main()'),(242,'_exit: write scratch2'),(308,'Restore sp / gp / ra; ret')]
    for y,s in right: f.block(404,y,270,40,s,size=13 if y==110 else 14)
    for a,b in zip(right,right[1:]):f.arrow([(539,a[0]+40),(539,b[0])])
    f.arrow([(276,328),(334,328),(334,64),(404,64)],BLUE); f.text(326,202,'jalr',anchor='end',color=BLUE,size=13)
    f.block(46,376,230,34,'ROM ret (source-derived)')
    f.arrow([(539,348),(539,393),(276,393)],dash=True)
    f.arrow([(161,410),(161,443),(313,443),(313,406),(276,406)],dash=True)
    f.text(454,430,'ret self-loop',size=13)
    return f


def sw_calls():
    f=Figure('software_calls',335,
      '代表性的裸机调用关系。应用按需调用库，不要求经过全部层次：printf→_putchar→UART DIF，GPT 经 read 回调访问器件 HAL，HAL 再使用 SPI/I²C DIF；HAL 也可能直接使用 MMIO。DIF/HAL 名称遵循本工程职责，libcheshire.a 是归档方式而不是新的调用层。',
      '2026-10-09_software_hardware_layers/cheshire_software_hardware.svg',
      '通用功能/器件HAL/DIF/MMIO→本图；执行接口/硬件→hardware_paths；构建与启动侧栏→build_and_execution；OS与规划→图注。')
    f.text(24,28,'Application / tests',anchor='start',bold=True)
    f.line([(25,43),(695,43)])
    for x,s in [(25,'printf'),(260,'GPT parser'),(495,'Device control')]:
        f.block(x,75,195,38,s); f.arrow([(x+97,43),(x+97,75)])
    f.block(25,164,195,38,'UART DIF')
    f.block(260,145,195,38,'Storage HAL')
    f.block(260,212,195,38,'SPI / I²C DIF')
    f.block(495,164,195,61,'CLINT / DMA / GPIO\nLLC / AXI RT')
    f.arrow([(122,113),(122,164)]); f.text(132,143,'_putchar',anchor='start',size=13)
    f.arrow([(357,113),(357,145)]); f.text(368,134,'read callback',anchor='start',size=13)
    f.arrow([(357,183),(357,212)]); f.arrow([(592,113),(592,164)])
    f.block(25,283,665,34,'MMIO: address + offset + access width',fill=LIGHT)
    for x,y in [(122,202),(357,250),(592,225)]: f.arrow([(x,y),(x,283)])
    return f


def hardware():
    f=Figure('hardware_paths',425,
      '当前 SoC 的执行与访存结构抽象。CVA6 与 Ara 的专用请求/响应及 MMU 交互同 AXI 访存分开；RVV 不是 MMIO 外设启动。主存路径依次经过原子适配、LLC/SPM 和平台 DDR 子系统。箭头为逻辑事务连接，返回通道省略。SPM 使用 LLC 阵列；片外器件按平台配置连接。',
      '2026-10-09_software_hardware_layers/cheshire_software_hardware.svg',
      'CVA6/Ara专用接口、独立访存、主存/寄存器/片外器件→本图；规划扩展与FPGA/ASIC边界→图注。')
    f.block(45,45,130,48,'CVA6'); f.block(291,45,130,48,'Ara'); f.block(543,45,130,48,'iDMA')
    f.arrow([(175,64),(291,64)],both=True, color=BLUE); f.text(232,37,'issue / MMU',size=13,color=BLUE)
    f.block(45,147,628,32,'Main AXI interconnect',fill=LIGHT)
    for x in [110,356,608]:f.arrow([(x,93),(x,147)])
    f.block(28,231,181,43,'AMO / LRSC'); f.block(270,231,181,43,'Register bus'); f.block(512,231,181,43,'Other AXI targets')
    for x in [118,360,602]:f.arrow([(x,179),(x,231)])
    f.block(28,301,181,36,'LLC / SPM'); f.arrow([(118,274),(118,301)])
    f.block(28,373,181,36,'DDR ctrl / PHY → DDR',size=13)
    f.arrow([(118,337),(118,373)])
    f.block(270,301,181,36,'UART / SPI / I²C')
    f.arrow([(360,274),(360,301)])
    f.block(270,373,181,36,'Flash / SD / EEPROM',size=13)
    f.arrow([(360,337),(360,373)])
    return f


def build_execution():
    f=Figure('build_and_execution',300,
      '构建产物与运行环境分开：主机工具根据源代码、库和链接脚本生成 ELF；目标端通过启动/调试通路加载，CRT0 建立环境后由处理器执行应用。指令、CSR、内存/MMIO 和异常/中断是软件可见接口，不是四个必须逐层经过的软件模块。',
      '2026-10-09_software_hardware_layers/cheshire_software_hardware.svg',
      '工具链、链接/归档、Boot/CRT0、四类软硬件契约→本图；可选OS/ASIC实现维度→图注。')
    f.text(147,26,'Host',bold=True); f.text(495,26,'Target',bold=True)
    f.block(30,50,225,55,'Sources + libraries\nLinker script / Makefile')
    f.block(30,145,225,45,'Compiler / assembler / linker')
    f.arrow([(142,105),(142,145)])
    f.arrow([(255,168),(427,168)],BLUE); f.text(342,157,'ELF',color=BLUE)
    f.block(427,145,250,45,'Load → CRT0 → main')
    f.arrow([(552,190),(552,241)])
    f.block(30,241,647,39,'ISA / RVV     ·     CSR     ·     Memory / MMIO     ·     Trap / IRQ',fill=LIGHT)
    return f


def ddr_top():
    f=Figure('ddr_interconnect',450,
      '2026-10-10 候选互连，虚线模块/路径为新增。CVA6 与 Ara 的普通地址保持主 AXI→原子适配→LLC/SPM→DDR S0。Ara 的 GB 地址在现有失效过滤之后新增分流，经 GB 路由访问独立 SRAM。NPU、ISP 与统一搬运器也是 GB 客户端。GB/NPU 搬运经 S1，图像帧 DMA 经 S2；三个端口共享 DDR 控制器。',
      '2026-10-10_ddr_lvds_isp_gb/ddr_interconnect.svg',
      '系统主路径/Ara新增分流/GB客户端/DDR三口→本图；RAW/ISP/CDC与帧选择→image_gb_dataflow；三口条件和缓存维护→图注。')
    f.block(22,28,112,34,'CVA6'); f.block(172,28,112,34,'Ara')
    f.block(172,93,112,34,'Inval. filter'); f.arrow([(228,62),(228,93)])
    f.block(172,159,112,34,'Addr. split',dash=True); f.arrow([(228,127),(228,159)])
    f.block(172,225,112,34,'Width conv.'); f.arrow([(228,193),(228,225)])
    f.block(22,289,262,33,'Main AXI Xbar',fill=LIGHT)
    f.arrow([(78,62),(78,289)]); f.arrow([(228,259),(228,289)])
    f.block(22,350,112,34,'AMO / LRSC'); f.block(172,350,112,34,'LLC / SPM')
    f.arrow([(78,322),(78,350)]); f.arrow([(134,367),(172,367)])
    f.block(358,27,116,35,'NPU',dash=True); f.block(561,27,116,35,'ISP',dash=True)
    f.block(358,159,319,34,'GB local routing / arbitration',dash=True,fill=LIGHT)
    f.arrow([(416,62),(416,159)],dash=True); f.arrow([(619,62),(619,159)],dash=True)
    f.arrow([(284,176),(358,176)],BLUE,dash=True); f.text(322,163,'GB',color=BLUE,size=13)
    f.block(358,230,134,49,'GB SRAM\nbanked',dash=True)
    f.arrow([(425,193),(425,230)],both=True,dash=True)
    f.block(543,230,134,49,'GB / NPU DMA',dash=True,size=13)
    f.arrow([(610,193),(610,230)],both=True,dash=True)
    f.block(543,330,134,36,'Frame DMA',dash=True)
    f.rect(335,404,342,30,dash=True); f.text(500,425,'DDR controller → PHY / DDR',size=13)
    f.arrow([(284,367),(321,367),(321,419),(335,419)])
    f.text(309,400,'S0',size=13)
    f.arrow([(610,279),(505,279),(505,404)],dash=True); f.text(492,394,'S1',size=13)
    f.arrow([(610,366),(610,404)],dash=True); f.text(627,394,'S2',size=13)
    return f


def image_flow():
    f=Figure('image_gb_dataflow',340,
      '新增图像与 GB 数据流的展开。像素经 LVDS 接收和 CDC/FIFO 后分出 RAW 路径与 ISP 路径，在帧边界选择其一进入帧 DMA→DDR S2。当前假设不同时录制 RAW/处理帧。ISP 保留必要行缓冲，并可经 GB 路由访问中间数据；NPU 与 Ara 并行使用 GB，搬运器在 DDR S1 与 GB 之间读写。',
      '2026-10-10_ddr_lvds_isp_gb/ddr_interconnect.svg',
      'RAW旁路、ISP行缓冲、帧选择、DMA、GB与各客户端→本图；具体容量与带宽假设→图注。')
    f.block(18,56,92,49,'LVDS RX'); f.block(141,56,105,49,'CDC / FIFO'); f.block(296,56,122,49,'ISP\nline buffers')
    f.arrow([(110,80),(141,80)]); f.arrow([(246,80),(296,80)])
    f.dot(269,80); f.arrow([(269,80),(269,27),(484,27),(484,68.4)],BLUE); f.text(376,20,'RAW',size=13,color=BLUE)
    f.mux(472,66,40,64,''); f.text(492,106,'sel',size=13)
    f.arrow([(418,80),(472,80)]); f.text(491,149,'frame select',size=13)
    f.block(554,76,146,49,'Frame DMA\nDDR S2'); f.arrow([(512,98),(554,98)])
    f.block(18,191,92,38,'Ara'); f.block(18,273,92,38,'NPU')
    f.block(199,191,195,120,'GB routing\n+ banked SRAM',fill=LIGHT)
    f.arrow([(110,210),(199,210)],both=True); f.arrow([(110,292),(199,292)],both=True)
    f.arrow([(357,105),(357,191)],both=True); f.text(365,173,'workspace',anchor='start',size=13)
    f.block(486,234,204,49,'GB / NPU DMA\nDDR S1'); f.arrow([(394,258),(486,258)],both=True)
    return f


def cache_access():
    f=Figure('llc_cache_access',425,
      '全 Cache 基线的访问机制：48-bit 地址分成 Tag[47:14]、Set[13:6]、Block[5:3]、Byte[2:0]。Set 同时索引各 way 的 tag 与 data，Tag/Valid 比较产生命中 way，选择相应数据。图示仅展开代表 way，其余以 ×8 标注；tag 与 data 是分立 SRAM。Set 42 / hit Way 6 仅为教学例子。',
      '2026-10-10_llc_cache_spm/source_final/llc_cache_spm.svg',
      '地址字段/索引/Tag+Valid比较/way选择/独立阵列→本图；用途位图与SPM寻址→llc_spm_mapping；转换→llc_mode_transition。')
    fields=[(20,285,'Tag [47:14]'),(305,174,'Set [13:6]'),(479,115,'Block [5:3]'),(594,106,'Byte [2:0]')]
    for x,w,label in fields: f.block(x,25,w,36,label,size=13)
    f.text(545,112,'per way × 8',size=13)
    f.text(314,137,'Tag SRAM',bold=True); f.text(570,137,'Data SRAM',bold=True)
    f.rect(228,151,172,90); f.rect(464,151,213,90)
    f.rect(228,181,172,30,fill=LIGHT,stroke='none'); f.rect(464,181,213,30,fill=LIGHT,stroke='none')
    for y in [181,211]:
        f.line([(228,y),(400,y)],width=1); f.line([(464,y),(677,y)],width=1)
    for x in [344,374]: f.line([(x,151),(x,241)],width=1)
    for i in range(1,8): f.line([(464+i*213/8,151),(464+i*213/8,241)],width=.8)
    f.text(286,171,'Tag',size=13); f.text(359,171,'V',size=13); f.text(387,171,'D',size=13)
    f.text(286,201,'Tag[42]',size=13); f.text(359,201,'v',size=13); f.text(387,201,'d',size=13)
    f.text(314,258,'256 rows',size=13); f.text(570,258,'8 × 64 bit / row',size=13)
    f.arrow([(392,61),(392,89),(434,89),(434,196),(400,196)])
    f.arrow([(434,196),(464,196)]); f.dot(434,196)
    f.block(228,285,172,36,'Tag + Valid compare')
    f.arrow([(250,241),(250,285)])
    f.arrow([(162,61),(162,303),(228,303)])
    f.mux(514,285,114,54,'Way select',down=True)
    f.arrow([(640,241),(640,273),(571,273),(571,285)])
    f.arrow([(400,303),(517,303)],BLUE); f.text(454,289,'hit way',size=13,color=BLUE)
    f.arrow([(571,339),(571,369)]); f.block(467,369,211,37,'Block / byte select')
    f.arrow([(536,61),(536,75),(687,75),(687,354),(624,354),(624,369)])
    f.arrow([(646,61),(702,61),(702,388),(678,388)])
    f.text(128,364,'8 ways × 256 sets × 64 B',size=13)
    f.text(128,389,'128 KiB data capacity',bold=True)
    return f


def spm_mapping():
    f=Figure('llc_spm_mapping',370,
      '同一 128 KiB 数据阵列按 way 分配给 Cache 或 SPM。CFG_SPM 位为 1 表示 SPM，0 表示 Cache；每 way 为 16 KiB。SPM 固定槽不随位图压缩重排，已配置的 SPM 槽按地址直接选 way，不做 LLC Tag 比较。颜色和 C/S 标签共同编码用途。',
      '2026-10-10_llc_cache_spm/source_final/llc_cache_spm.svg',
      '0x00/0x0F/0xFF、容量守恒、固定地址槽、0x10008AAB示例→本图；别名/L1/错误返回→图注。')
    f.text(64,29,'CFG_SPM',bold=True); f.text(134,29,'Way',anchor='start',size=13)
    for i in range(8): f.text(198+i*64,29,str(i),size=13)
    for row,(cfg,count) in enumerate([('0x00',0),('0x0F',4),('0xFF',8)]):
        y=50+row*52; f.text(65,y+24,cfg)
        for i in range(8):f.block(168+i*64,y,59,36,'S' if i<count else 'C',fill=LIGHT if i<count else 'none')
    f.text(430,229,'C: Cache     S: SPM     16 KiB / way',size=13)
    f.block(26,272,198,55,'0x10008AAB\nSPM address')
    f.arrow([(224,299),(276,299)])
    for x,w,s in [(276,114,'Way 2'),(390,102,'Set 42'),(492,102,'Block 5'),(594,102,'Byte 3')]:f.block(x,282,w,35,s)
    f.text(481,349,'Way 2: [0x10008000, 0x1000C000)',size=13)
    return f


def spm_transition():
    f=Figure('llc_mode_transition',350,
      '运行期 Cache/SPM 切换的逻辑次序。软件先保护/迁移代码、栈与数据，管理上游缓存副本和在途访问，再写 CFG_SPM 并提交。硬件执行隔离、等待和必要刷新；软件按实际寄存器/FSM 契约确认完成后恢复访问。COMMIT 请求清零仅表示接受，不能当作全部刷新完成。',
      '2026-10-10_llc_cache_spm/source_final/llc_cache_spm.svg',
      '软件准备/配置提交/硬件协调/完成确认→本图；容量非复制、反向转换、全SPM外存旁路→图注。')
    f.text(162,29,'Software',bold=True); f.text(546,29,'LLC hardware',bold=True)
    f.block(30,56,260,54,'Quiesce / protect live data\nHandle caches and in-flight work',size=13)
    f.block(30,160,260,54,'Write CFG_SPM\nSubmit COMMIT')
    f.arrow([(160,110),(160,160)])
    f.block(420,160,270,54,'Accept request\nClear COMMIT request')
    f.arrow([(290,187),(420,187)])
    f.block(420,271,270,54,'Isolate / wait / flush\nReach completed state')
    f.arrow([(555,214),(555,271)])
    f.block(30,271,260,54,'Confirm completion\nResume accesses')
    f.arrow([(420,298),(290,298)],BLUE)
    return f


def example():
    f=Figure('example',185,
      '通用处理/反馈示例用于验证文本、矩形、曲线、箭头和独立对象导出，不表示实际硬件或实验结果。输入/处理/输出关系沿用旧验证图；外围说明移到本图注。',
      '2026-10-06_svg_pptx_skill_validation/example.editable.svg','输入/处理/输出/反馈→本图；可编辑性说明→导出报告。')
    f.block(30,36,148,50,'Input'); f.block(278,36,148,50,'Process',fill=LIGHT); f.block(542,36,148,50,'Output')
    f.arrow([(178,61),(278,61)]); f.arrow([(426,61),(542,61)])
    f.add('path',d='M 615 86 C 615 159 104 159 104 92',fill='none',stroke=INK,stroke_width=1.3)
    f.arrow([(104,97),(104,86)]); f.text(355,168,'Feedback',size=13)
    return f


EXTRA = {
 '2026-10-06_axi_crossbar_ara': '''配置快照沿用原图：Ara=1、2 lanes/VLEN 2048、AXI 数据64 bit、Cfg.AxiRt=0；不是对当前所有构建的声明。Ara 入端有失效过滤及位宽适配，此配置64→64。M2 经原子适配、cut/别名重映射与LLC，SPM/cache命中可片内完成；128 KiB SPM有 cached/uncached 别名。外存窗口[0x80000000,0x100000000)，M4 Serial Link TX窗口[0x100000000,0x200000000)，M3 iDMA控制从0x01000000起。M1涵盖Boot ROM、CLINT、PLIC、SoC regs与外设控制。未映射地址由每输入错误响应单元处理（图省略）。VCU118旧加源快照SerialLink=0/USB=0/Ara=1对应5×4，不能与仿真7×5混同。

DDR候选依据为原图记录的供应商V2.1授权接口摘要：最多8个AXI端口、端口优先级/QoS、命令调度；独立AXI Urgent接口不支持。精确寄存器、带宽保底、最坏延迟待用户手册确认。多端口不自动保证CPU/LLC缓存一致性或旁路写AMO/LRSC语义，RT是否增加需独立评估。未复制受限datasheet内容。''',
 '2026-10-08_boot_initialization': '''Boot ROM地址0x02000000，其S/C预编译为ROM内容。复位前有效时钟和复位由外围平台提供。ROM S配置整数环境、等待LLC DONE并提交全SPM；ROM C测频、选boot_mode、驱动介质并装载。CRT0还执行FP环境初始化；.bss清零不等于SRAM制造自测。DONE与错误位分开，tag BIST不测试data SRAM。PlatformRom=0跳过钩子，非零普通返回的S01-B01缺陷仍未修复。

当前boot_next_stage在jalr前未保存上层ra，普通载荷返回后可形成ret自循环；不应画成正常进入ROM _exit。main可以不返回；若返回，scratch2是完成通知，仿真TB/调试器可观察它，TB可结束仿真；CPU不会因此自动停机、复位、断电或换权限。JTAG直接改PC、UART invoke、OS退出属于不同契约。本组为源码推导，未新增目标运行证据。''',
 '2026-10-09_software_hardware_layers': '''三个图分别表达调用、硬件连接、构建/执行，不把所有职责强制堆成一条垂直调用链。应用包括HelloWorld/测试、RVV向量算法、烧写/下载工具；图像推理工作负载为规划。UART debug HAL提供READ/WRITE/EXEC；libcheshire.a覆盖多类职责。MMIO工具包括reg8/reg32和mmio_region接口，寄存器头文件给偏移与位字段。其他专用LLC/AXI RT库属于软件控制。

四类软件可见契约为指令/RVV、CSR、内存/MMIO、异常/中断。IRQ/异常处理含入口与返回；配置接口可在运行时重复访问，Boot/CRT0不是每次设备调用的必经层。可选RTOS提供任务/调度/同步，Linux有用户态/内核/驱动，不默认复用整套裸机HAL，也未声称目标OS已运行。

硬件图省略各外设控制连线、AXI逐通道和详细cache hit/miss。图像传感器/LVDS、ISP、NPU与DDR旁路为规划，未虚构已连通接口；新候选拓扑单列在DDR组。FPGA已有VCU118工程，ASIC的宏、时钟、PAD与物理实现仍待适配；供应商AXI4 DDR子系统未因图示而成为已集成能力。已存在结构不代表所有配置启用、全部功能通过验证。''',
 '2026-10-10_ddr_lvds_isp_gb': '''三口成立条件：NPU与GB共用S1搬运出口；若保留独立NPU master与GB DMA，可增加S3，不能强行串行化。DDR控制器候选最多8个AXI Slave，内部仲裁/QoS与DRAM Bank/Row调度共享DDR带宽。该组为候选，新增分流、GB、NPU/ISP/图像路径均未实施。

GB是独立分bank SRAM，不是LLC/SPM；容量、bank数、位宽、频率均未冻结。GB路由包含局部仲裁与访问适配，真实并行能力取决于端口、bank冲突和SRAM带宽。ISP工作区、NPU/Ara活跃区及DMA双缓冲是用途示意，不是固定分区。ISP保留必要行缓冲。帧DMA处理地址/stride/打包并生成AXI写；RAW/处理帧按帧切换，当前假设不同时录制。GB/NPU DMA与计算NPU不合并成一个IP。

系统图的箭头表示逻辑请求关系，双向GB线表示本地读写，返回通道省略；数据流图的箭头表示像素或数据移动。控制寄存器、中断、CDC细节、缓存维护与所有权协议另行设计；GB不自动一致，旁路写与原子观察域仍需验证。''',
 '2026-10-10_llc_cache_spm': '''参数来自当前DefaultCfg：48-bit地址、64-bit数据、8 way、每way256行、每行8×8 B=64 B；每way16 KiB，共128 KiB数据，不含tag存储。Cache way由命中或替换选择，不是cache地址中的字段。miss选择替换way，必要时写回脏行并从下游refill；为突出命中路径，图中未展开miss FSM。

CFG_SPM=0x00全Cache，0x0F为64 KiB Cache+64 KiB SPM，0xFF全SPM（ROM等待BIST后提交）。固定槽base+way×0x4000，Way2为[0x10008000,0x1000C000)，地址0x10008AAB→Way2/Set42/Block5/Byte3。访问未配置为SPM的槽返回SLVERR。全SPM且完成提交后，DDR流量从LLC旁路，SPM地址仍访问同一阵列；0x14000000未缓存别名重映射到同一SPM，上游L1属性/共享协议需独立核对。

切换不自动复制数据，也不新增RAM；必须保护代码/栈/数据并处理上游缓存和在途事务。SPM→Cache后原SPM内容不再保证固定驻留。COMMIT请求清零不等于全部刷新完成，须按实际完成契约确认。官方历史文档有把way称set的情况，本图采用常见cache术语：8way×256set。''' }


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out-root',type=Path,required=True)
    args=parser.parse_args()
    if args.out_root.exists(): parser.error('Choose a new output root')
    args.out_root.mkdir(parents=True)
    groups={
      '2026-10-06_axi_crossbar_ara':[crossbar(),ddr_old()],
      '2026-10-06_svg_pptx_skill_validation':[example(),crossbar(),ddr_old()],
      '2026-10-08_boot_initialization':[boot_hw(),boot_flow()],
      '2026-10-09_software_hardware_layers':[sw_calls(),hardware(),build_execution()],
      '2026-10-10_ddr_lvds_isp_gb':[ddr_top(),image_flow()],
      '2026-10-10_llc_cache_spm':[cache_access(),spm_mapping(),spm_transition()]}
    manifest={}
    for name,figures in groups.items():
        folder=args.out_root/(name+'_new'); folder.mkdir()
        data=[f.finish(folder) for f in figures]; manifest[name]=data
        (folder/'figures.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        lines=[f'# {name} · 新版图稿','', '使用 publication-figures；旧目录原样保留。所有图宽182 mm，英文短标签/中文图注。源图、PDF和PNG各自保持比例；PPT页宽182 mm，组内统一页面高度。', '', '[可编辑 PPTX](export/diagrams.pptx) · [导出报告](export/export_report.json)','']
        for f in figures:
            lines += [f'## {f.name}', '',f'![{f.name}](export/{f.name}.png)','', f'[SVG]({f.name}.svg) · [PDF](export/{f.name}.pdf) · [PNG](export/{f.name}.png) · [灰度](export/{f.name}.gray.png)','',f.caption,'',f'内容映射：{f.mapping}', '',f'原图：[旧母版](../{f.source})','']
        lines += ['## 随图补充','',EXTRA.get(name, '本组复用新版Crossbar与DDR候选图验证批量导出，技术图注补充见 [Crossbar组](../2026-10-06_axi_crossbar_ara_new/README.md)。不覆盖旧验证日志。'),'', '## 来源与验证边界','', '技术事实沿用原目录正式母版、README及对应交接，不升级依赖、不改RTL。实际重绘/导出测试见本组JSON及[总交付](../2026-10-10_publication_figure_research_new/README.md)。没有重新编译/仿真/板测；Office实际外观与编辑未验证。', '', '复现：使用总交付内 build_figures.py --out-root <新临时目录> 生成全部SVG，再用新skill的 scripts/run.py --width-mm 182 --render 导出；命令所用Python需安装对应依赖。']
        (folder/'README.md').write_text('\n'.join(lines)+'\n')
    (args.out_root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:len(v) for k,v in manifest.items()},indent=2))


if __name__=='__main__': main()
