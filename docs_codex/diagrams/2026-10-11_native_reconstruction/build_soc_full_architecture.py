#!/usr/bin/env python3
"""Draw the SoC overview as semantic SVG; export with svg-pptx-diagrams-native.

Run with the native skill's Python and a NEW --out-dir. Existing outputs are
never overwritten. Rendering the PNG is a separate local CairoSVG operation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
W, H = 3400, 2440
INK, MUTED = '#21374B', '#61758A'
BLUE, TEAL, ORANGE, PURPLE, GRAY = '#347BB2', '#16867F', '#C17A30', '#8663A9', '#8B99A7'
LIGHTBLUE, LIGHTTEAL, LIGHTORANGE, LIGHTPURPLE = '#EDF4FB', '#EAF5F1', '#FFF2DF', '#F3EDF8'


class Drawing:
    def __init__(self):
        self.root = ET.Element(f'{{{NS}}}svg', {
            'width': str(W), 'height': str(H), 'viewBox': f'0 0 {W} {H}'})
        ET.SubElement(self.root, f'{{{NS}}}title').text = 'Cheshire + CVA6 + Ara · SoC 扩展架构'
        defs = ET.SubElement(self.root, f'{{{NS}}}defs')
        for color in [BLUE, TEAL, ORANGE, PURPLE, GRAY]:
            m = ET.SubElement(defs, f'{{{NS}}}marker', {
                'id': 'arrow'+color[1:], 'markerUnits': 'strokeWidth',
                'markerWidth': '3', 'markerHeight': '3', 'viewBox': '0 0 3 3',
                'refX': '3', 'refY': '1.5', 'orient': 'auto-start-reverse'})
            ET.SubElement(m, f'{{{NS}}}polygon', {'points': '0,0 3,1.5 0,3', 'fill': color})
        self.seq = 0
        self.text_records = []
        self.blocks = {}

    def elem(self, tag, ident=None, **attrs):
        self.seq += 1
        attrs = {k.replace('_', '-'): str(v) for k, v in attrs.items()}
        attrs['id'] = ident or f'obj-{self.seq:03d}'
        return ET.SubElement(self.root, f'{{{NS}}}{tag}', attrs)

    def rect(self, ident, x, y, w, h, fill='white', color=GRAY, dash=False, radius=6, sw=2):
        args = dict(x=x, y=y, width=w, height=h, rx=radius,
                    fill=fill, stroke=color, stroke_width=sw)
        if dash:
            args['stroke_dasharray'] = '10 6'
        self.blocks[ident] = [x, y, w, h]
        self.elem('rect', ident, **args)

    def text(self, x, y, value, size=27, color=INK, bold=False, anchor='middle', owner=None):
        e = self.elem('text', x=x, y=y, font_family='Microsoft YaHei',
                      font_size=size, fill=color, text_anchor=anchor,
                      font_weight='bold' if bold else 'normal')
        e.text = value
        self.text_records.append(dict(id=e.get('id'), text=value, x=x, y=y,
                                      size=size, anchor=anchor, owner=owner))

    def line(self, ident, pts, color=BLUE, width=3, arrow=True, both=False, dash=False):
        attrs = dict(fill='none', stroke=color, stroke_width=width,
                     stroke_linejoin='miter')
        if arrow:
            attrs['marker_end'] = 'url(#arrow'+color[1:]+')'
        if both:
            attrs['marker_start'] = 'url(#arrow'+color[1:]+')'
        if dash:
            attrs['stroke_dasharray'] = '8 6'
        if len(pts) == 2:
            attrs.update(x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1])
            self.elem('line', ident, **attrs)
        else:
            attrs['points'] = ' '.join(f'{x},{y}' for x, y in pts)
            self.elem('polyline', ident, **attrs)

    def box(self, ident, x, y, w, h, title, details=(), color=BLUE, fill=LIGHTBLUE,
            dash=False, title_size=29):
        self.rect(ident, x, y, w, h, fill, color, dash)
        self.text(x+w/2, y+43, title, title_size, bold=True, owner=ident)
        for i, s in enumerate(details):
            self.text(x+w/2, y+80+i*33, s, 25, owner=ident)

    def badge(self, name, x, y):
        self.rect('tag-'+name+'-'+str(self.seq), x, y, 48, 31, LIGHTPURPLE, PURPLE, radius=3, sw=1.5)
        self.text(x+24, y+23, name, 20, PURPLE, bold=True)


def draw():
    d = Drawing()
    d.rect('background', 0, 0, W, H, '#FFFFFF', 'none', radius=0)
    d.text(55, 75, 'Cheshire + CVA6 + Ara · SoC 扩展架构', 49, bold=True, anchor='start')
    d.text(58, 121, 'AXI 主从端口 · Regbus 全外设 · 独立 GB 与三端口 DDR', 28, MUTED, anchor='start')
    d.rect('soc-boundary', 40, 150, 3060, 2140, '#FBFCFE', '#526A7C', radius=12, sw=3)
    d.text(3059, 194, 'SoC', 30, MUTED, bold=True, anchor='end')

    # Masters. S labels refer to Xbar slave-side ports, not device roles.
    d.text(90, 217, 'AXI master / 发起端', 25, BLUE, bold=True, anchor='start')
    d.box('cpu', 90, 250, 330, 180, 'CVA6 core 0', ['L1 I-cache / D-cache', 'MMU · AXI 适配'])
    d.box('debug-master', 455, 250, 220, 180, 'Debug / SBA', ['系统总线访问', 'JTAG 调试入口'])
    d.rect('ara', 710, 250, 570, 180, LIGHTBLUE, BLUE)
    d.text(995, 294, 'Ara · VLSU / AXI 32 × lanes', 28, bold=True, owner='ara')
    for ident, x, w, title, detail, candidate in [
        ('ara-filter',730,140,'失效过滤','现有 filter',False),
        ('ara-split',890,140,'地址分流','新增 GB 支路',True),
        ('ara-width',1050,210,'位宽适配','普通路径 → 64 bit',False)]:
        d.rect(ident, x, 326, w, 82, LIGHTPURPLE if candidate else '#FFFFFF', PURPLE if candidate else BLUE, candidate)
        d.text(x+w/2, 357, title, 24, bold=True, owner=ident)
        d.text(x+w/2, 387, detail, 19, MUTED, owner=ident)
    d.line('filter-to-split',[(870,367),(890,367)])
    d.line('split-to-width',[(1030,367),(1050,367)])
    d.line('cpu-ara-control',[(370,250),(370,226),(790,226),(790,250)], PURPLE, 2.5, both=True)
    d.text(575, 216, '指令 / MMU 协作', 21, PURPLE)
    d.box('idma-master',1315,250,220,180,'iDMA 数据',['AXI 搬运主口','内存 ↔ 内存'])
    d.box('slink-master',1570,250,240,180,'Serial Link RX',['远端请求入口'])
    d.box('vga-master',1845,250,190,180,'VGA',['帧缓冲读取'])
    d.box('usb-master',2070,250,190,180,'USB DMA',['OHCI 主口'])
    d.box('axi-ext-master',2295,250,205,180,'AXI 扩展',['外部 master','可选入口'], color=GRAY, fill='#F4F6F8', dash=True, title_size=27)

    d.rect('xbar',90,500,2410,172,'#DDEAF5',BLUE,radius=4,sw=3)
    d.text(1295,566,'AXI Crossbar',42,bold=True,owner='xbar')
    d.text(1295,610,'7 × 5 基础端口 + 扩展 · 64 bit 数据 / 48 bit 地址 · 按地址译码 / 各目标独立仲裁',27,owner='xbar')
    d.text(135,650,'输入侧 AXI RT：按配置可选',21,MUTED,anchor='start',owner='xbar')
    d.text(2420,650,'DECERR：未映射请求',21,MUTED,anchor='end',owner='xbar')
    for name, x in [('S0',255),('S1',565),('S2',995),('S3',1425),('S4',1690),('S5',1940),('S6',2165),('S_EXT',2397)]:
        pts = [(x,430),(x,500)] if name != 'S2' else [(1155,408),(1155,463),(995,463),(995,500)]
        d.line('master-'+name,pts,GRAY if name=='S_EXT' else BLUE,dash=name=='S_EXT')
        d.rect('pin-'+name,x-48,490,96,34,'#FFFFFF',BLUE, radius=2)
        d.text(x,515,name,23,BLUE,bold=True)

    # Five internal target classes plus optional external slave ports.
    target_rows = [('M0',225),('M1',570),('M2',985),('M3',1385),('M4',1740),('M_EXT',2095)]
    for name, x in target_rows:
        d.line('slave-'+name,[(x,672),(x,765)],GRAY if name=='M_EXT' else BLUE,dash=name=='M_EXT')
        d.rect('pin-'+name,x-49,654,98,34,'#FFFFFF',BLUE,radius=2)
        d.text(x,680,name,23,BLUE,bold=True)
    d.text(2380,737,'AXI slave / 目标端',25,BLUE,bold=True)
    d.box('debug-target',90,765,270,170,'Debug 目标',['调试模块地址窗口','与 SBA 主口分开'],title_size=28)
    d.box('reg-bridge',405,765,330,170,'AXI → Regbus',['原子适配 / 桥接','32 bit 寄存器访问'],color=PURPLE,fill=LIGHTPURPLE)
    d.rect('memory-target',785,765,400,170,LIGHTBLUE,BLUE)
    d.text(985,799,'主存 / SPM 共用目标',26,bold=True,owner='memory-target')
    d.rect('memory-atomics',800,822,165,89,'#FFFFFF',BLUE)
    d.text(882,854,'原子适配',24,bold=True,owner='memory-atomics')
    d.text(882,886,'AMO / LRSC',21,owner='memory-atomics')
    d.line('atomics-llc',[(965,866),(990,866)])
    d.rect('llc',990,822,180,89,'#FFFFFF',BLUE)
    d.text(1080,854,'LLC / SPM',24,bold=True,owner='llc')
    d.text(1080,886,'同一 SRAM 阵列',19,owner='llc')
    d.box('idma-target',1230,765,310,170,'iDMA 配置',['原子适配 → AXI→Reg','wrapper 内部寄存器'],title_size=28)
    d.box('slink-target',1585,765,310,170,'Serial Link TX',['远端数据目标窗口','经链路送往对端'],title_size=28)
    d.box('axi-ext-target',1940,765,310,170,'AXI 扩展目标',['外部 slave','CPU 直访 GB 待定'],color=GRAY,fill='#F4F6F8',dash=True,title_size=28)

    # Clock / reset is one platform distribution block, not a frozen domain plan.
    d.box('platform-clock',2640,250,360,180,'PLL / 时钟与复位',['安全时钟选择 / 分频','clk_i / rst_ni 分发'],color=PURPLE,fill=LIGHTPURPLE,dash=True)
    d.badge('C1',2940,390)
    d.line('refclk',[(2820,201),(2820,250)],GRAY)
    d.text(2820,190,'RefClk / POR',24,MUTED)
    d.line('clock-to-soc',[(2640,355),(2580,355),(2580,620),(2500,620)],GRAY,2.4,dash=True)
    d.text(2830,481,'平台时钟源',24,PURPLE)

    # Regbus demultiplexer: every gen_reg_out target represented separately.
    d.rect('reg-peripherals',90,994,645,988,'#FAF8FC','#B6A5C5',radius=8)
    d.text(412,1035,'Regbus decode / demux',30,PURPLE,bold=True,owner='reg-peripherals')
    d.line('bridge-to-demux',[(570,935),(570,965),(65,965),(65,1055),(412,1055),(412,1070)],PURPLE,3)
    d.line('reg-spine',[(412,1070),(412,1937)],PURPLE,4,arrow=False)
    peripherals = [
        ('bootrom','Boot ROM','启动代码',False),('clint','CLINT','软件 / 定时中断',False),
        ('soc-regs','SoC 寄存器','平台信息 / scratch',False),('plic','PLIC','外部中断控制',False),
        ('llc-regs','LLC 配置','SPM way / cache 控制',False),('uart','UART','串口控制',False),
        ('i2c','I2C','两线串行控制',False),('spi','SPI host','Flash / SD 访问',False),
        ('gpio','GPIO','通用 IO',False),('slink-regs','Serial Link 配置','链路控制',False),
        ('vga-regs','VGA 配置','显示时序 / 帧地址',False),('usb-regs','USB 配置','OHCI 寄存器',False),
        ('err-vga','Bus-error · VGA','错误记录',False),('err-dma','Bus-error · iDMA','错误记录',False),
        ('err-cpu','Bus-error · CPU','每核错误记录',False),('irq-router','IRQ router','可选中断路由',True),
        ('axi-rt-regs','AXI RT 配置','可选流量调节',True),('clic','CLIC','可选每核中断控制',True),
        ('reg-error','reg_err_slv','未匹配寄存器地址',False),('reg-ext','RegExt 扩展','新增 IP 配置出口',True)]
    for i,(ident,title,sub,opt) in enumerate(peripherals):
        col,row=i%2,i//2
        x=110 if col==0 else 455
        y=1070+row*89
        d.rect(ident,x,y,260,70,'#FFFFFF',GRAY if opt else '#A993BD',opt,radius=4)
        d.text(x+130,y+28,title,24,bold=True,owner=ident)
        d.text(x+130,y+55,sub,20,MUTED,owner=ident)
        d.line('reg-'+ident,[(412,y+35),(370 if col==0 else 455,y+35)],PURPLE,2.2)

    # DDR target ports. Their numbering is independent of the main AXI Xbar.
    d.rect('ddr-controller',2610,765,290,1215,LIGHTBLUE,BLUE,dash=True,radius=10)
    d.text(2755,809,'DDR Controller',29,bold=True,owner='ddr-controller')
    d.text(2755,846,'三 AXI slave 端口',24,owner='ddr-controller')
    d.badge('C2',2818,866)
    d.rect('ddr-arbiter',2743,943,132,972,'#FFFFFF','#91ADCA',radius=6)
    for y,s in [(1225,'端口仲裁'),(1270,'QoS'),(1380,'读写调度'),(1480,'Bank / Row'),(1530,'命令调度')]:
        d.text(2809,y,s,23,bold=y in [1225,1380],owner='ddr-arbiter')
    for n,y,sub in [(0,1040,'LLC'),(1,1430,'NPU / GB'),(2,1835,'帧写入')]:
        d.rect('ddr-S'+str(n),2630,y-35,87,70,'#FFFFFF',BLUE,radius=5)
        d.text(2673,y+10,'S'+str(n),29,BLUE,bold=True)
        d.text(2673,y+67,sub,18,MUTED)
        d.line('ddr-port-'+str(n),[(2717,y),(2743,y)],BLUE,3,both=n==1)
    d.box('phy',2930,1340,140,180,'PHY',['训练 / 校准'],color=BLUE,fill=LIGHTBLUE,dash=True,title_size=29)
    d.badge('C3',3008,1478)
    d.line('controller-to-phy',[(2875,1430),(2930,1430)],BLUE,3,both=True)
    d.box('dram-chip',3180,1325,170,210,'DDR',['片外器件'],color=BLUE,fill='#F0F3F6',title_size=34)
    d.line('phy-to-dram',[(3070,1430),(3180,1430)],BLUE,4,both=True)
    d.line('llc-ddr',[(1080,911),(1080,1040),(2630,1040)],BLUE,4)
    d.text(1790,1023,'LLC 外存出口 · AXI 64 bit',26,BLUE)

    # Shared SRAM subsystem. The GB router is shared by all local visitors.
    d.rect('gb-subsystem',785,1130,1725,458,'#F8FCFA',TEAL,dash=True,radius=10)
    d.text(813,1170,'独立 GB / NPU 子系统',29,TEAL,bold=True,anchor='start')
    d.box('npu-compute',820,1210,290,155,'NPU 计算引擎',['GB 数据读写'],color=TEAL,fill=LIGHTTEAL)
    d.badge('C6',1050,1321)
    d.box('gb-adapter',1160,1210,280,155,'GB 访问适配',['局部仲裁 / 路由','bank 冲突处理'],color=TEAL,fill=LIGHTTEAL,title_size=28)
    d.box('global-buffer',1490,1190,420,195,'Global Buffer',['独立片上 SRAM · 分 bank','ISP / NPU–Ara 共享数据','双缓冲 / 工作区'],color=TEAL,fill=LIGHTTEAL,title_size=32)
    d.badge('C9',1850,1340)
    d.line('compute-gb-router',[(1110,1285),(1160,1285)],TEAL,4,both=True)
    d.line('router-gb',[(1440,1285),(1490,1285)],TEAL,4,both=True)
    d.box('npu-transfer',2110,1350,360,160,'NPU / GB 搬运引擎',['DDR ↔ GB','统一 DDR 主口 · 256 bit 候选'],color=TEAL,fill=LIGHTTEAL,title_size=28)
    d.badge('C7',2410,1468)
    d.line('transfer-gb-router',[(2110,1430),(1280,1430),(1280,1365)],TEAL,4,both=True)
    d.text(1670,1468,'GB 读写通路',23,TEAL)
    d.line('transfer-ddr',[(2470,1430),(2630,1430)],BLUE,4,both=True)

    # One continuous Ara branch with two explicit crossing hops (clock, DDR).
    d.elem('path','ara-gb-branch',d='M 960 326 L 960 315 L 1295 315 L 1295 175 L 2540 175 L 2540 605 C 2564 605 2564 635 2540 635 L 2540 1025 C 2564 1025 2564 1055 2540 1055 L 2540 1100 L 1300 1100 L 1300 1210',
           fill='none',stroke=TEAL,stroke_width=3.5,marker_end='url(#arrow'+TEAL[1:]+')')
    d.text(1860,1082,'Ara 宽侧 GB 地址分支',25,TEAL)

    # Stream subsystem with frame-boundary RAW/ISP selection.
    d.rect('image-subsystem',785,1623,1725,359,'#FFFBF5',ORANGE,dash=True,radius=10)
    d.text(813,1663,'LVDS / ISP / 图像帧写入',29,ORANGE,bold=True,anchor='start')
    d.box('lvds',810,1760,235,150,'LVDS 接收',['解串 / 帧行解析'],color=ORANGE,fill=LIGHTORANGE,title_size=29)
    d.badge('C4',985,1866)
    d.box('pixel-cdc',1080,1760,190,150,'CDC / FIFO',['像素流缓冲'],color=ORANGE,fill=LIGHTORANGE,title_size=27)
    d.box('isp',1310,1760,200,150,'ISP',['行缓冲 / 处理'],color=ORANGE,fill=LIGHTORANGE,title_size=32)
    d.badge('C5',1450,1866)
    d.box('frame-select',1590,1760,260,150,'帧边界选择',['RAW / ISP 二选一'],color=ORANGE,fill=LIGHTORANGE,title_size=29)
    d.box('frame-dma',2050,1760,420,150,'图像帧写入 DMA',['地址 / stride / 像素打包','产生 AXI 写事务'],color=ORANGE,fill=LIGHTORANGE,title_size=30)
    d.badge('C8',2410,1866)
    for ident,a,b in [('lvds-cdc',1045,1080),('cdc-isp',1270,1310),('isp-select',1510,1590),('select-writer',1850,2050)]:
        d.line(ident,[(a,1835),(b,1835)],ORANGE,4)
    d.line('raw-bypass',[(1288,1835),(1288,1720),(1720,1720),(1720,1760)],ORANGE,3)
    d.elem('circle','raw-junction',cx=1288,cy=1835,r=5,fill=ORANGE,stroke='none')
    d.text(1690,1705,'RAW 旁路',23,ORANGE)
    d.elem('path','isp-gb-router',d='M 1410 1760 L 1410 1735 C 1434 1735 1434 1705 1410 1705 L 1410 1608 L 1130 1608 L 1130 1330 L 1160 1330',
           fill='none',stroke=TEAL,stroke_width=3,marker_start='url(#arrow'+TEAL[1:]+')',marker_end='url(#arrow'+TEAL[1:]+')')
    d.text(964,1560,'ISP 中间数据 ↔ GB',23,TEAL)
    d.line('frame-to-ddr',[(2470,1835),(2630,1835)],BLUE,4)

    # Controls use paired C-labels; these are registers in the same IPs above.
    d.text(90,2036,'RegExt · 新增 IP 配置寄存器',29,PURPLE,bold=True,anchor='start')
    d.line('regext-to-config-rail',[(585,1941),(585,2077)],PURPLE,3)
    d.line('config-rail',[(230,2077),(2870,2077)],PURPLE,4,arrow=False)
    configs=[('PLL / 时钟复位','配置 / 锁定 / 切换'),('DDR Controller','初始化 / QoS / 状态'),('DDR PHY','training / 校准 / 状态'),
             ('LVDS','通道 / 对齐 / 帧行'),('ISP','尺寸 / 模式 / 参数'),('NPU 计算','命令 / GB 数据位置'),
             ('NPU / GB 搬运','地址 / 长度 / stride'),('帧写入 DMA','缓冲区 / 格式 / 帧状态'),('GB 管理','能力 / bank / 错误')]
    for i,(title,sub) in enumerate(configs):
        x=80+330*i
        ident='config-C'+str(i+1)
        d.line('config-drop-'+str(i),[(x+150,2077),(x+150,2120)],PURPLE,2.5)
        d.rect(ident,x,2120,300,130,LIGHTPURPLE,PURPLE,dash=True)
        d.badge('C'+str(i+1),x+12,2132)
        d.text(x+166,2164,title,25,bold=True,owner=ident)
        d.text(x+150,2214,sub,23,owner=ident)

    # Only a concise visual legend on canvas; engineering caveats live in notes.
    legend=[(80,BLUE,'AXI 请求通路'),(580,TEAL,'GB 读写'),(1000,ORANGE,'像素流'),(1400,PURPLE,'配置 / 专用控制')]
    for x,c,label in legend:
        d.line('legend-'+c[1:],[(x,2350),(x+65,2350)],c,3,both=c==TEAL)
        d.text(x+82,2359,label,26,c,anchor='start')
    d.rect('legend-optional',2005,2334,65,32,'#FFFFFF',GRAY,dash=True,radius=3)
    d.text(2090,2359,'灰虚线：可选',25,MUTED,anchor='start')
    d.rect('legend-candidate',2370,2334,65,32,'#FFFFFF',TEAL,dash=True,radius=3)
    d.text(2455,2359,'彩色虚线：新增候选',25,MUTED,anchor='start')
    d.text(80,2400,'C1–C9：同一 IP 的配置端对应关系；AXI 返回通道合并示意。',24,MUTED,anchor='start')
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--skill',type=Path,default=Path.home()/'.codex/skills/svg-pptx-diagrams-native')
    p.add_argument('--svg-only',action='store_true')
    a=p.parse_args()
    if a.out_dir.exists() and any(a.out_dir.iterdir()):
        p.error('Refusing to overwrite a nonempty directory')
    a.out_dir.mkdir(parents=True,exist_ok=True)
    d=draw()
    name='soc_full_architecture'
    svg=a.out_dir/(name+'.svg')
    ET.indent(d.root,space='  ')
    ET.ElementTree(d.root).write(svg,encoding='utf-8',xml_declaration=True)
    (a.out_dir/(name+'.layout.json')).write_text(json.dumps(dict(
        canvas=[W,H],blocks=d.blocks,texts=d.text_records),ensure_ascii=False,indent=2)+'\n')
    if not a.svg_only:
        sys.path.insert(0,str(a.skill/'scripts'))
        from svg_to_pptx import read_svg, create_deck
        fig=read_svg(svg)
        report=create_deck([fig],a.out_dir/(name+'.pptx'),'source',
                           font_file=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),
                           slide_width_in=28)[0]
        report.update(skill='svg-pptx-diagrams-native',source_svg=name+'.svg',
                      svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
                      office_display_editing_tested=False,
                      scope='Diagram only; candidate topology, not implemented RTL')
        (a.out_dir/(name+'.export.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2))
    print(svg)


if __name__=='__main__':
    main()
