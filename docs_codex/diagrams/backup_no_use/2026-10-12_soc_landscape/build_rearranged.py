#!/usr/bin/env python3
"""Rearrange the previous SoC diagram as a landscape presentation figure.

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
W, H = 3400, 1850
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


def compact(d, ident, x, y, w, h, lines, color=BLUE, fill=LIGHTBLUE, dash=False, size=27):
    d.rect(ident,x,y,w,h,fill,color,dash,radius=6)
    step=31 if len(lines)>1 else 0
    first=y+h/2-(len(lines)-1)*step/2+size*.35
    if ident in {'npu-compute','global-buffer','npu-transfer','lvds','pixel-cdc',
                 'isp','frame-select','frame-dma','platform-clock','phy'}:
        first-=17  # Reserve the bottom edge for the C1–C9 control identities.
    for i,line in enumerate(lines):
        d.text(x+w/2,first+i*step,line,size if i==0 else size-3,
               INK if i==0 else MUTED,bold=i==0,owner=ident)


def draw():
    d=Drawing()
    d.rect('background',0,0,W,H,'#FFFFFF','none',radius=0)
    d.text(55,65,'Cheshire + CVA6 + Ara · SoC 扩展架构',46,bold=True,anchor='start')
    d.text(60,108,'版本 2 · 原版配色与结构重排',27,MUTED,anchor='start')
    # A right-hand notch keeps the physical DDR device outside the SoC outline.
    d.elem('path','soc-boundary',d='M 35 140 H 3350 V 870 H 3140 V 1080 H 3350 V 1755 H 35 Z',
           fill='#FBFCFE',stroke='#526A7C',stroke_width=2.5)

    # Prominent compute and imaging domains in the top half.
    d.rect('cpu-ara-domain',60,165,1080,290,'#F4F8FD',BLUE,radius=10)
    d.text(86,203,'CVA6–Ara 处理子系统',30,BLUE,bold=True,anchor='start')
    compact(d,'cpu',90,247,280,137,['CVA6 core 0','L1 I / D · MMU','AXI 适配'])
    d.rect('ara',460,247,650,160,LIGHTBLUE,BLUE)
    d.text(785,280,'Ara · VLSU / AXI 32 × lanes',28,bold=True,owner='ara')
    compact(d,'ara-filter',480,308,150,75,['失效过滤','现有 filter'],size=24,fill='#FFFFFF')
    compact(d,'ara-split',660,308,165,75,['地址分流','GB 分支'],PURPLE,LIGHTPURPLE,True,25)
    compact(d,'ara-width',855,308,230,75,['位宽适配','普通路径 → 64 bit'],size=25,fill='#FFFFFF')
    d.line('filter-split',[(630,345),(660,345)])
    d.line('split-width',[(825,345),(855,345)])
    d.line('cpu-ara-control',[(370,280),(460,280)],PURPLE,2.5,both=True)
    d.text(415,268,'指令',20,PURPLE)
    d.text(415,312,'MMU',20,PURPLE)

    d.rect('gb-npu-domain',1170,165,1090,290,'#F6FBF8',TEAL,True,radius=10)
    d.text(1195,203,'NPU / 独立 Global Buffer',30,TEAL,bold=True,anchor='start')
    compact(d,'npu-compute',1200,255,220,125,['NPU 计算引擎','GB 数据访问'],TEAL,LIGHTTEAL,False,27)
    d.badge('C6',1360,341)
    compact(d,'gb-adapter',1450,255,240,125,['GB 访问适配','仲裁 / bank 冲突'],TEAL,LIGHTTEAL,False,27)
    compact(d,'global-buffer',1720,255,270,125,['Global Buffer','独立分 bank SRAM'],TEAL,LIGHTTEAL,False,29)
    d.badge('C9',1930,341)
    compact(d,'npu-transfer',2020,235,210,176,['NPU / GB','搬运引擎','DDR ↔ GB'],TEAL,LIGHTTEAL,False,26)
    d.badge('C7',2170,368)
    d.line('npu-router',[(1420,317),(1450,317)],TEAL,3.5,both=True)
    d.line('router-gb',[(1690,317),(1720,317)],TEAL,3.5,both=True)
    d.line('transfer-router',[(2125,411),(2125,434),(1570,434),(1570,380)],TEAL,3.5,both=True)
    d.line('ara-gb',[(825,319),(840,319),(840,294),(1124,294),(1124,226),(1535,226),(1535,255)],TEAL,3.5)
    d.text(1300,244,'GB 分支',20,TEAL)

    d.rect('image-domain',2290,165,1030,290,'#FFFBF5',ORANGE,True,radius=10)
    d.text(2315,203,'LVDS / ISP / 图像帧写入',30,ORANGE,bold=True,anchor='start')
    compact(d,'lvds',2320,307,160,115,['LVDS 接收','解串 / 帧行'],ORANGE,LIGHTORANGE,False,26)
    compact(d,'pixel-cdc',2500,307,150,115,['CDC / FIFO','像素缓冲'],ORANGE,LIGHTORANGE,False,23)
    compact(d,'isp',2670,307,150,115,['ISP','行缓冲 / 处理'],ORANGE,LIGHTORANGE,False,25)
    compact(d,'frame-select',2840,307,160,115,['帧边界选择','RAW / ISP'],ORANGE,LIGHTORANGE,False,23)
    compact(d,'frame-dma',3020,307,270,115,['图像帧写入 DMA','地址 / stride / 打包'],ORANGE,LIGHTORANGE,False,26)
    for tag,x in [('C4',2420),('C5',2760),('C8',3230)]:d.badge(tag,x,381)
    for name,a,b in [('lvds-cdc',2480,2500),('cdc-isp',2650,2670),('isp-select',2820,2840),('select-dma',3000,3020)]:
        d.line(name,[(a,350),(b,350)],ORANGE,3)
    d.line('raw-path',[(2660,350),(2660,286),(2920,286),(2920,307)],ORANGE,2.8)
    d.elem('circle','raw-junction',cx=2660,cy=350,r=4,fill=ORANGE,stroke='none')
    d.text(2930,271,'RAW 旁路',20,ORANGE)
    # Hop over the RAW path; this is not a junction.
    d.elem('path','isp-gb',d='M 2745 307 L 2745 296 C 2763 296 2763 276 2745 276 L 2745 229 L 1645 229 L 1645 255',
           fill='none',stroke=TEAL,stroke_width=3,marker_start='url(#arrow'+TEAL[1:]+')',marker_end='url(#arrow'+TEAL[1:]+')')
    d.text(2510,250,'ISP 中间数据 ↔ GB',20,TEAL)

    # Full AXI source inventory; the two core data paths retain their own drops.
    masters=[('debug-master',290,160,['Debug / SBA'],'S1',370),
             ('idma-master',820,160,['iDMA 数据'],'S3',900),
             ('slink-master',1010,220,['Serial Link RX'],'S4',1120),
             ('vga-master',1250,160,['VGA 取帧'],'S5',1330),
             ('usb-master',1440,160,['USB DMA'],'S6',1520),
             ('axi-ext-master',1630,140,['AXI 扩展','master'],'S_EXT',1700)]
    d.text(1190,520,'AXI master / 发起端',24,BLUE,bold=True,anchor='start')
    for name,x,w,lines,pin,cx in masters:
        opt=pin=='S_EXT'
        compact(d,name,x,548,w,72,lines,GRAY if opt else BLUE,'#F4F6F8' if opt else LIGHTBLUE,opt,24)
        d.line('source-'+pin,[(cx,620),(cx,665)],GRAY if opt else BLUE,dash=opt)
    d.line('source-S0',[(230,384),(230,487),(170,487),(170,665)],BLUE,3.5)
    d.line('source-S2',[(970,383),(970,488),(650,488),(650,665)],BLUE,3.5)
    d.text(550,524,'Ara 普通地址',23,BLUE)
    d.rect('xbar',60,665,1720,140,'#DDEAF5',BLUE,radius=5,sw=3)
    d.text(920,720,'AXI Crossbar',38,bold=True,owner='xbar')
    d.text(920,760,'64 bit / 48 bit 地址 · 7 × 5 基础端口 + 扩展',27,owner='xbar')
    d.text(95,787,'地址译码 / 目标仲裁 / 响应返回',19,MUTED,anchor='start',owner='xbar')
    d.text(1745,787,'AXI RT 可选 · 空洞返回 DECERR',19,MUTED,anchor='end',owner='xbar')
    for name,x in [('S0',170),('S1',370),('S2',650),('S3',900),('S4',1120),('S5',1330),('S6',1520),('S_EXT',1700)]:
        d.rect('pin-'+name,x-43,650,86,31,'#FFFFFF',BLUE,radius=2)
        d.text(x,673,name,21,BLUE,bold=True)

    targets=[('debug-target',80,220,190,'M0',['Debug 目标','调试地址窗口']),
             ('reg-bridge',325,235,442,'M1',['AXI → Regbus','原子适配 / 桥接']),
             ('idma-target',585,275,722,'M3',['iDMA 配置','原子适配 → AXI→Reg']),
             ('slink-target',885,260,1015,'M4',['Serial Link TX','远端数据窗口']),
             ('axi-ext-target',1170,230,1285,'M_EXT',['AXI 扩展目标','CPU 直访 GB 待定'])]
    for name,x,w,cx,pin,lines in targets:
        opt=pin=='M_EXT'
        d.line('target-'+pin,[(cx,805),(cx,890)],GRAY if opt else BLUE,dash=opt)
        d.rect('pin-'+pin,cx-45,792,90,31,'#FFFFFF',BLUE,radius=2)
        d.text(cx,815,pin,21,BLUE,bold=True)
        compact(d,name,x,890,w,125,lines,PURPLE if pin=='M1' else GRAY if opt else BLUE,
                LIGHTPURPLE if pin=='M1' else '#F4F6F8' if opt else LIGHTBLUE,opt,26)
    d.line('target-M2',[(1600,805),(1600,890)])
    d.rect('pin-M2',1555,792,90,31,'#FFFFFF',BLUE,radius=2)
    d.text(1600,815,'M2',21,BLUE,bold=True)
    d.rect('memory-target',1425,890,350,125,LIGHTBLUE,BLUE)
    d.text(1600,919,'主存 / SPM 共用目标',24,bold=True,owner='memory-target')
    compact(d,'memory-atomics',1437,938,140,60,['AMO / LRSC'],size=20,fill='#FFFFFF')
    compact(d,'llc',1610,938,151,60,['LLC / SPM'],size=24,fill='#FFFFFF')
    d.line('atomics-llc',[(1577,968),(1610,968)])
    d.text(1145,852,'AXI slave / 目标端',22,BLUE,bold=True)

    # Horizontal DDR controller; three ports merge into one shared scheduler.
    compact(d,'platform-clock',1840,490,370,116,['PLL / 时钟与复位','RefClk / POR → 系统分发'],PURPLE,LIGHTPURPLE,True,27)
    d.badge('C1',2150,563)
    d.line('clock-distribution',[(1840,550),(1788,550),(1788,710),(1780,710)],GRAY,2.2,dash=True)
    d.rect('ddr-controller',1820,650,1040,430,LIGHTBLUE,BLUE,True,radius=10)
    d.text(1845,694,'DDR Controller · 三 AXI slave 端口',29,BLUE,bold=True,anchor='start',owner='ddr-controller')
    d.badge('C2',2798,666)
    for n,x,subtitle in [(0,1870,'LLC 下游'),(1,2270,'NPU / GB'),(2,2670,'图像帧写入')]:
        compact(d,'ddr-S'+str(n),x,740,160,90,['S'+str(n),subtitle],size=27,fill='#FFFFFF')
        d.line('ddr-port-'+str(n),[(x+80,830),(x+80,861)],BLUE,3,arrow=False)
    d.line('ddr-port-merge',[(1950,861),(2750,861)],BLUE,3,arrow=False)
    d.rect('ddr-arbitration',1860,890,960,140,'#FFFFFF','#92ADC7',radius=5)
    for ident,x,w,lines in [('ddr-qos',1880,275,['端口仲裁 / QoS']),('ddr-rw',2195,210,['读写调度']),('ddr-command',2445,355,['Bank / Row','命令调度'])]:
        compact(d,ident,x,919,w,82,lines,size=27,fill='#F3F7FC')
    d.line('ddr-merge-qos',[(2018,861),(2018,919)],BLUE,3)
    d.line('qos-rw',[(2155,960),(2195,960)])
    d.line('rw-command',[(2405,960),(2445,960)])
    compact(d,'phy',2890,900,210,130,['PHY','训练 / 校准'],BLUE,LIGHTBLUE,True,30)
    d.badge('C3',3040,987)
    compact(d,'dram-chip',3180,906,180,120,['DDR 器件','片外存储'],BLUE,'#F0F3F6',False,28)
    d.line('controller-phy',[(2820,960),(2890,960)],BLUE,3.5,both=True)
    d.line('phy-dram',[(3100,960),(3180,960)],BLUE,3.5,both=True)
    d.line('llc-ddr',[(1761,968),(1800,968),(1800,718),(1950,718),(1950,740)],BLUE,3.5)
    d.text(1640,1054,'LLC 外存出口',22,BLUE)
    d.line('transfer-ddr',[(2230,323),(2265,323),(2265,543),(2350,543),(2350,740)],BLUE,3.5,both=True)
    d.text(2470,588,'NPU / GB 统一 DDR 主口',23,BLUE)
    d.line('frame-ddr',[(3155,422),(3155,605),(2750,605),(2750,740)],BLUE,3.5)
    d.text(3000,587,'帧写事务',23,BLUE)

    # Horizontal Regbus with every internal target as an independent leaf.
    d.rect('reg-peripherals',60,1125,3260,355,'#FAF8FC','#B6A5C5',radius=9)
    d.text(88,1167,'Regbus 外设 / 配置目标',28,PURPLE,bold=True,anchor='start')
    d.rect('regbus',80,1295,3210,50,LIGHTPURPLE,PURPLE,radius=3,sw=2.5)
    d.text(1685,1330,'Regbus · 32 bit · 地址译码 / demux',27,PURPLE,bold=True,owner='regbus')
    d.line('bridge-regbus',[(442,1015),(442,1095),(46,1095),(46,1320),(80,1320)],PURPLE,3)
    items=[('bootrom','Boot ROM','启动代码',False),('clint','CLINT','软件 / 定时中断',False),
           ('soc-regs','SoC 寄存器','平台信息 / scratch',False),('plic','PLIC','外部中断控制',False),
           ('llc-regs','LLC 配置','SPM way / cache',False),('uart','UART','串口控制',False),
           ('i2c','I2C','两线串行控制',False),('spi','SPI host','Flash / SD 访问',False),
           ('gpio','GPIO','通用 IO',False),('slink-regs','Serial Link 配置','链路控制',False),
           ('vga-regs','VGA 配置','时序 / 帧缓冲',False),('usb-regs','USB 配置','OHCI 寄存器',False),
           ('err-vga','Bus-error · VGA','错误记录',False),('err-dma','Bus-error · iDMA','错误记录',False),
           ('err-cpu','Bus-error · CPU','每核错误记录',False),('irq-router','IRQ router','可选中断路由',True),
           ('axi-rt-regs','AXI RT 配置','可选流量调节',True),('clic','CLIC','可选每核中断控制',True),
           ('reg-error','reg_err_slv','未匹配地址错误响应',False),('reg-ext','RegExt 扩展','新增 IP 配置出口',True)]
    for i,(ident,title,sub,opt) in enumerate(items):
        row,col=divmod(i,10)
        x=80+320*col;y=1200 if row==0 else 1380
        compact(d,ident,x,y,300,75,[title,sub],GRAY if opt else PURPLE,'#FFFFFF',opt,25)
        d.line('reg-'+ident,[(x+150,1295 if row==0 else 1345),(x+150,1275 if row==0 else 1380)],PURPLE,2.3)

    # Register identities are paired with the corresponding blocks above.
    d.text(82,1520,'RegExt · 新增配置端',27,PURPLE,bold=True,anchor='start')
    d.line('regext-controls',[(3110,1455),(3110,1545)],PURPLE,3)
    d.line('config-rail',[(235,1545),(3115,1545)],PURPLE,3.5,arrow=False)
    configs=[('PLL / 时钟复位','配置 / 锁定 / 切换'),('DDR Controller','初始化 / QoS / 状态'),('DDR PHY','training / 校准'),
             ('LVDS','通道 / 对齐 / 帧行'),('ISP','尺寸 / 模式 / 参数'),('NPU 计算','命令 / GB 数据位置'),
             ('NPU / GB 搬运','地址 / 长度 / stride'),('帧写入 DMA','缓冲区 / 格式 / 帧状态'),('GB 管理','能力 / bank / 错误')]
    for i,(title,sub) in enumerate(configs):
        x=80+i*360
        d.line('config-drop-'+str(i),[(x+155,1545),(x+155,1580)],PURPLE,2.4)
        d.rect('config-C'+str(i+1),x,1580,310,135,LIGHTPURPLE,PURPLE,True)
        d.badge('C'+str(i+1),x+12,1592)
        d.text(x+174,1627,title,25,bold=True,owner='config-C'+str(i+1))
        d.text(x+155,1683,sub,23,owner='config-C'+str(i+1))
    for x,c,label in [(65,BLUE,'AXI 请求'),(410,TEAL,'GB 读写'),(755,ORANGE,'像素流'),(1100,PURPLE,'配置 / 专用控制')]:
        d.line('legend-'+c[1:],[(x,1795),(x+55,1795)],c,3,both=c==TEAL)
        d.text(x+70,1804,label,25,c,anchor='start')
    d.text(1650,1804,'灰虚线：可选模块   彩色虚线：新增候选',24,MUTED,anchor='start')
    d.text(2590,1804,'C1–C9：对应同一 IP 配置端',23,MUTED,anchor='start')
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--skill',type=Path,default=Path.home()/'.codex/skills/svg-pptx-diagrams-native')
    args=p.parse_args()
    if args.out_dir.exists() and any(args.out_dir.iterdir()):p.error('Output directory must be new or empty')
    args.out_dir.mkdir(parents=True,exist_ok=True)
    d=draw();name='soc_rearranged'
    svg=args.out_dir/(name+'.svg')
    ET.indent(d.root,space='  ')
    ET.ElementTree(d.root).write(svg,encoding='utf-8',xml_declaration=True)
    (args.out_dir/(name+'.layout.json')).write_text(json.dumps(dict(canvas=[W,H],blocks=d.blocks,texts=d.text_records),ensure_ascii=False,indent=2)+'\n')
    sys.path.insert(0,str(args.skill/'scripts'))
    from svg_to_pptx import read_svg,create_deck
    report=create_deck([read_svg(svg)],args.out_dir/(name+'.pptx'),'source',
                      font_file=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),slide_width_in=28)[0]
    report.update(skill='svg-pptx-diagrams-native',svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
                  office_display_editing_tested=False,source='soc_rearranged.svg')
    (args.out_dir/(name+'.export.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()


