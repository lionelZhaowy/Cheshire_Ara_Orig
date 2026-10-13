#!/usr/bin/env python3
"""Industrial SoC overview; semantic SVG and native PowerPoint shapes.

Outputs refuse overwrite. The old dated figure directory is read-only input.
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
W, H = 3600, 2025
INK = '#29292D'
MUTED = '#606773'
AXI = '#314D66'
GB = '#187C78'
PIX = '#B96043'
CTL = '#765489'
GRAY = '#93939D'
PINK = '#F1D7D9'
BLUE = '#D8E8F4'
TEAL = '#D9EEE8'
PEACH = '#F5E1C9'
PURPLE = '#E8DFED'


class Drawing:
    def __init__(self):
        self.root = ET.Element(f'{{{NS}}}svg', {
            'width': str(W), 'height': str(H), 'viewBox': f'0 0 {W} {H}'})
        ET.SubElement(self.root, f'{{{NS}}}title').text = 'Cheshire + CVA6 + Ara · 完整 SoC 架构（工业框图版）'
        defs = ET.SubElement(self.root, f'{{{NS}}}defs')
        for c in (INK, AXI, GB, PIX, CTL, GRAY):
            m = ET.SubElement(defs, f'{{{NS}}}marker', {
                'id': 'arrow'+c[1:], 'markerUnits': 'strokeWidth',
                'markerWidth': '3', 'markerHeight': '3', 'viewBox': '0 0 3 3',
                'refX': '3', 'refY': '1.5', 'orient': 'auto-start-reverse'})
            ET.SubElement(m, f'{{{NS}}}polygon', {'points': '0,0 3,1.5 0,3', 'fill': c})
        self.n = 0
        self.blocks = {}
        self.texts = []

    def el(self, tag, ident=None, **a):
        self.n += 1
        a = {k.replace('_','-'): str(v) for k,v in a.items()}
        a['id'] = ident or f'object-{self.n:03}'
        return ET.SubElement(self.root, f'{{{NS}}}{tag}', a)

    def rect(self, ident, x, y, w, h, fill='#FFFFFF', stroke=INK, dash=False, sw=2):
        a = dict(x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=sw)
        if dash: a['stroke_dasharray']='10 6'
        self.el('rect',ident,**a)
        self.blocks[ident]=[x,y,w,h]

    def text(self,x,y,s,size=27,bold=False,anchor='middle',color=INK,owner=None):
        e=self.el('text',x=x,y=y,font_family='Microsoft YaHei',font_size=size,
                  font_weight='bold' if bold else 'normal',text_anchor=anchor,fill=color)
        e.text=s
        self.texts.append(dict(id=e.get('id'),text=s,x=x,y=y,size=size,anchor=anchor,owner=owner))

    def line(self,ident,points,color=AXI,both=False,dash=False,width=3,arrow=True):
        a=dict(fill='none',stroke=color,stroke_width=width,stroke_linejoin='miter')
        if arrow: a['marker_end']='url(#arrow'+color[1:]+')'
        if both: a['marker_start']='url(#arrow'+color[1:]+')'
        if dash: a['stroke_dasharray']='10 6'
        if len(points)==2:
            a.update(x1=points[0][0],y1=points[0][1],x2=points[1][0],y2=points[1][1])
            self.el('line',ident,**a)
        else:
            a['points']=' '.join(f'{x},{y}' for x,y in points)
            self.el('polyline',ident,**a)

    def path(self,ident,d,color=AXI,both=False,dash=False,width=3):
        a=dict(d=d,fill='none',stroke=color,stroke_width=width,marker_end='url(#arrow'+color[1:]+')')
        if both:a['marker_start']='url(#arrow'+color[1:]+')'
        if dash:a['stroke_dasharray']='10 6'
        self.el('path',ident,**a)

    def box(self,ident,x,y,w,h,title,subs=(),fill='#FFFFFF',dash=False,title_size=29):
        self.rect(ident,x,y,w,h,fill,dash=dash)
        # A short coloured heading bar reproduces the reference's nested IP style.
        self.text(x+w/2,y+37,title,title_size,bold=True,owner=ident)
        for i,s in enumerate(subs):
            self.text(x+w/2,y+73+32*i,s,25,owner=ident)

    def tag(self,num,x,y):
        self.rect('cfg-tag-'+num+'-'+str(self.n),x,y,47,29,PURPLE,CTL,sw=1.4)
        self.text(x+23.5,y+22,num,20,bold=True,color=CTL)


def draw():
    d=Drawing()
    d.rect('background',0,0,W,H,'#FFFFFF','none')
    d.text(50,66,'Cheshire + CVA6 + Ara  |  SoC 扩展架构',46,True,'start')
    d.text(3350,66,'工业框图版 · 2026-10-12',25,False,'end',MUTED)
    d.rect('soc-boundary',45,105,3325,1825,'#FFFFFF','#645C5D',sw=5)
    d.text(3290,145,'SoC',27,True,'end',MUTED)

    # Compute / memory / imaging sit above the two horizontal interconnects.
    d.rect('cpu-platform',95,175,935,425,PINK)
    d.text(562,214,'CVA6–Ara 计算平台',32,True)
    d.box('cva6',120,255,250,215,'CVA6 core 0',('L1 I / D cache','MMU · AXI 适配'),BLUE)
    d.box('ara-core',420,255,580,125,'Ara 向量处理器',('VLSU / AXI：32 × lanes bit',),BLUE)
    d.line('cva6-ara-control',[(370,315),(420,315)],CTL,both=True,width=2.5)
    d.text(396,245,'指令 / MMU',19,color=CTL)
    d.box('ara-filter',440,425,190,86,'失效过滤',('现有 filter',),BLUE,title_size=25)
    d.box('ara-split',665,425,150,86,'地址分流',('GB 候选',),TEAL,True,25)
    d.box('ara-width',850,425,150,86,'位宽适配',('→ 64 bit',),BLUE,title_size=25)
    d.line('vlsu-filter',[(535,380),(535,425)])
    d.line('filter-split',[(630,468),(665,468)])
    d.line('split-width',[(815,468),(850,468)])

    d.rect('npu-subsystem',1085,175,1135,425,TEAL,dash=True)
    d.text(1652,214,'NPU / 独立 Global Buffer 子系统',32,True)
    d.box('npu-compute',1110,255,270,175,'NPU 计算引擎',('GB 数据读写',),PINK)
    d.tag('C6',1320,385)
    d.box('gb-router',1415,330,230,235,'GB 访问适配',('局部仲裁 / 路由','bank 冲突处理'),'#FFFFFF',title_size=27)
    d.box('global-buffer',1685,255,505,170,'Global Buffer',('独立 SRAM · 分 bank','ISP / NPU–Ara 工作区'),TEAL,title_size=32)
    d.tag('C9',2130,378)
    d.line('npu-router',[(1380,360),(1415,360)],GB,both=True,width=4)
    d.line('router-sram',[(1645,385),(1685,385)],GB,both=True,width=4)
    d.box('npu-transfer',1685,460,505,120,'NPU / GB 搬运引擎',('DDR ↔ GB · 统一 AXI 主口',),BLUE,title_size=29)
    d.tag('C7',2130,538)
    d.line('transfer-router',[(1685,520),(1645,520)],GB,both=True,width=4)
    d.line('ara-gb',[(740,511),(740,585),(1530,585),(1530,565)],GB,both=True,dash=True,width=3.2)
    d.text(1190,574,'Ara 宽侧 GB 分支',23,color=GB)

    d.rect('image-subsystem',2270,175,1065,425,PEACH,dash=True)
    d.text(2802,214,'图像采集与 ISP',32,True)
    for ident,x,w,title,sub,tag in [
        ('lvds',2295,165,'LVDS 接收','解串 / 帧行','C4'),
        ('pixel-cdc',2490,160,'CDC / FIFO','像素流缓冲',None),
        ('isp',2680,165,'ISP','行缓冲 / 处理','C5'),
        ('frame-select',2875,180,'帧边界选择','RAW / ISP',None),
        ('frame-dma',3090,215,'帧写入 DMA','地址 / stride','C8')]:
        d.box(ident,x,315,w,185,title,(sub,),PINK if ident=='isp' else '#FFFFFF',title_size=26)
        if tag:d.tag(tag,x+w-60,455)
    for ident,a,b in [('lvds-cdc',2460,2490),('cdc-isp',2650,2680),('isp-select',2845,2875),('select-dma',3055,3090)]:
        d.line(ident,[(a,405),(b,405)],PIX,width=3.5)
    d.line('raw-bypass',[(2665,405),(2665,270),(2965,270),(2965,315)],PIX,width=3)
    d.el('circle','raw-tap',cx=2665,cy=405,r=4.5,fill=PIX,stroke='none')
    d.text(2830,258,'RAW 旁路',23,color=PIX)
    d.text(2970,552,'RAW / ISP 二选一 · 帧打包',24,color=MUTED)
    d.path('isp-gb','M 2680 470 L 2665 470 L 2665 607 C 2641 607 2641 633 2665 633 L 2665 643 L 1460 643 L 1460 599 C 1438 599 1438 573 1460 573 L 1460 565',GB,both=True,dash=True,width=3.1)
    d.text(2490,632,'ISP 中间数据 ↔ GB',24,color=GB)

    # AXI master row. Every enabled default master plus an extension is explicit.
    masters=[('debug-sba',420,255,'Debug / SBA','JTAG 总线访问',False),
             ('idma-master',1150,275,'iDMA 数据主口','内存 ↔ 内存',False),
             ('slink-rx',1490,285,'Serial Link RX','远端请求入口',False),
             ('vga-master',1840,255,'VGA','帧缓冲读取',False),
             ('usb-master',2160,250,'USB DMA','OHCI 主口',False),
             ('ext-master',2480,370,'AXI 外部 master','可选扩展入口',True)]
    for ident,x,w,title,sub,opt in masters:
        d.box(ident,x,680,w,100,title,(sub,),BLUE if not opt else '#F5F5F7',opt,27)
    d.line('cpu-master',[(245,470),(245,820)],AXI,width=3.2)
    d.line('ara-master',[(925,511),(925,820)],AXI,width=3.2)
    d.text(223,755,'CPU AXI',25,anchor='end',color=AXI)
    d.text(905,755,'Ara 普通地址',25,anchor='end',color=AXI)
    d.rect('axi-crossbar',95,820,2830,135,PEACH)
    d.text(1510,870,'AXI Crossbar',40,True)
    d.text(1510,915,'7 × 5 基础端口 + 扩展  |  64 bit 数据 / 48 bit 地址  |  地址译码 / 各目标仲裁',27)
    d.text(128,940,'输入侧 AXI RT：按配置可选',19,anchor='start',color=MUTED)
    d.text(2895,940,'未映射请求：DECERR',19,anchor='end',color=MUTED)
    for idx,x in enumerate([245,547,925,1287,1632,1967,2285,2665]):
        if idx not in (0,2):d.line('master-input-'+str(idx),[(x,780),(x,820)],GRAY if idx==7 else AXI,dash=idx==7)
        d.rect('master-port-'+str(idx),x-48,805,96,29,'#FFFFFF',GRAY if idx==7 else INK,sw=1.5)
        d.text(x,827,'S_EXT' if idx==7 else 'S'+str(idx),20,True)
    d.text(1150,668,'AXI master / 请求发起端',24,True,'start',AXI)

    # Five target classes; memory's SPM and external-memory regions share M2.
    targets=[('debug-target',95,320,'Debug 目标',('调试模块地址窗口',),BLUE),
             ('reg-bridge',475,500,'AXI → Regbus',('原子适配 / 桥接 · 32 bit',),PURPLE),
             ('memory-target',1040,480,'主存 / SPM 共用目标',(),BLUE),
             ('idma-config',1580,400,'iDMA 配置',('原子适配 → AXI→Reg','wrapper 内部寄存器'),BLUE),
             ('slink-tx',2040,420,'Serial Link TX',('远端数据目标窗口',),BLUE),
             ('ext-target',2515,410,'AXI 外部 slave',('可选扩展 / CPU 直访 GB 待定',),'#F5F5F7')]
    for i,(ident,x,w,title,subs,fill) in enumerate(targets):
        cx=x+w/2
        d.line('target-output-'+str(i),[(cx,955),(cx,1020)],GRAY if i==5 else AXI,dash=i==5)
        d.rect('target-port-'+str(i),cx-48,940,96,29,'#FFFFFF',GRAY if i==5 else INK,sw=1.5)
        d.text(cx,962,'M_EXT' if i==5 else 'M'+str(i),20,True)
        d.box(ident,x,1020,w,155,title,subs,fill,i==5,28)
    d.box('atomics',1060,1080,195,84,'原子适配',('AMO / LRSC',),'#FFFFFF',title_size=23)
    d.box('llc-spm',1300,1080,195,84,'LLC / SPM',('同一 SRAM 阵列',),'#FFFFFF',title_size=23)
    d.line('atomics-llc',[(1255,1118),(1300,1118)])

    # Peripheral fabric has one horizontal main spine and five parallel tap trunks.
    d.rect('reg-subsystem',75,1210,1945,500,'#FAF8FB')
    d.rect('regbus',95,1230,1905,70,PURPLE)
    d.text(1047,1277,'Regbus decode / demux  ·  32 bit',32,True)
    d.line('axi-regbus',[(725,1175),(725,1230)],CTL,width=3.5)
    peripherals=[
        ('bootrom','Boot ROM','启动代码',False),('clint','CLINT','软件 / 定时中断',False),
        ('soc-regs','SoC 寄存器','平台信息 / scratch',False),('plic','PLIC','外部中断控制',False),
        ('llc-regs','LLC 配置','SPM way / cache',False),('uart','UART','串口控制',False),
        ('i2c','I2C','两线串行控制',False),('spi','SPI host','Flash / SD',False),
        ('gpio','GPIO','通用 IO',False),('slink-regs','Serial Link 配置','链路控制',False),
        ('vga-regs','VGA 配置','时序 / 帧地址',False),('usb-regs','USB 配置','OHCI 寄存器',False),
        ('err-vga','Bus-error · VGA','错误记录',False),('err-dma','Bus-error · iDMA','错误记录',False),
        ('err-cpu','Bus-error · CPU','每核错误记录',False),('irq-router','IRQ router','可选中断路由',True),
        ('axi-rt-config','AXI RT 配置','可选流量调节',True),('clic','CLIC','可选每核中断控制',True),
        ('reg-error','reg_err_slv','未匹配地址',False),('reg-ext','RegExt 扩展','新增 IP 配置出口',True)]
    for col in range(5):
        x=150+375*col
        d.line('regbus-trunk-'+str(col),[(x-20,1300),(x-20,1649)],CTL,arrow=False,width=2.2)
    for i,(ident,title,sub,opt) in enumerate(peripherals):
        col,row=i%5,i//5
        x,y=150+375*col,1330+92*row
        d.rect(ident,x,y,320,78,'#FFFFFF',GRAY if opt else INK,opt,1.8)
        d.text(x+160,y+31,title,25,True)
        d.text(x+160,y+61,sub,22,color=MUTED)
        d.line('reg-drop-'+ident,[(x-20,y+39),(x,y+39)],CTL,width=2.2)

    d.rect('ddr-controller',2110,1280,970,370,BLUE,dash=True)
    d.text(2595,1631,'DDR Controller · 3 个 AXI slave',30,True)
    d.tag('C2',3010,1611)
    for n,x,sub in [(0,2240,'SoC / LLC'),(1,2570,'NPU / GB 搬运'),(2,2900,'图像帧写入')]:
        d.rect('ddr-S'+str(n),x-110,1280,220,100,'#FFFFFF')
        d.text(x,1320,'S'+str(n),30,True)
        d.text(x,1358,sub,24,color=AXI)
        d.line('ddr-S-to-arb-'+str(n),[(x,1380),(x,1410)],AXI,width=2.8,arrow=False)
    d.line('ddr-port-collect',[(2240,1410),(2900,1410)],AXI,width=2.8,arrow=False)
    d.line('ddr-all-to-arbiter',[(2300,1410),(2300,1470)],AXI,width=2.8)
    d.rect('ddr-scheduler',2150,1470,895,135,'#FFFFFF')
    for i,(title,sub) in enumerate([('端口仲裁 / QoS','共享 DDR 带宽'),('读写调度','Bank / Row'),('命令调度','控制器 → PHY')]):
        cx=2300+297*i
        d.text(cx,1518,title,27,True)
        d.text(cx,1557,sub,24,color=MUTED)
        if i<2:d.line('ddr-schedule-step-'+str(i),[(cx+128,1530),(cx+165,1530)],AXI,width=2.5)
    d.text(2700,1450,'共享同一 DDR 地址空间',23,color=MUTED)
    d.box('ddr-phy',3130,1467,200,140,'DDR PHY',('训练 / 校准',),PURPLE,True,28)
    d.tag('C3',3268,1567)
    d.line('ddr-phy-path',[(3045,1530),(3130,1530)],AXI,both=True,width=3.5)
    d.box('dram',3420,1467,150,140,'DDR',('片外器件',),'#EAECEE',title_size=31)
    d.line('phy-dram',[(3330,1530),(3420,1530)],AXI,both=True,width=3.7)

    # Independent DDR paths go around the main AXI fabric; they terminate at
    # edge-mounted ports and never disappear underneath controller geometry.
    d.path('npu-ddr','M 2190 520 L 2242 520 L 2242 620 L 3070 620 L 3070 1233 L 2570 1233 L 2570 1280',AXI,both=True,dash=True,width=3.5)
    d.text(3094,914,'S1',25,True,color=AXI)
    d.path('frame-ddr','M 3215 500 L 3215 1195 L 2900 1195 L 2900 1220 C 2874 1220 2874 1246 2900 1246 L 2900 1280',AXI,dash=True,width=3.5)
    d.text(3240,914,'S2',25,True,color=AXI)
    d.line('llc-ddr',[(1400,1164),(1400,1193),(2240,1193),(2240,1280)],AXI,width=3.6)
    d.text(1790,1226,'S0 · LLC 外存出口',24,color=AXI)

    # Clock distribution shown as a platform function, without fixed domain claims.
    d.box('clock-reset',2150,1680,525,74,'PLL / 时钟与复位分发',(),PEACH,True,28)
    d.tag('C1',2604,1701)
    d.text(2865,1726,'RefClk / POR → clk_i / rst_ni',25,color=CTL)

    # C labels pair RegExt controls with the same IPs in the data plane.
    d.line('regext-control-bus',[(1970,1645),(2050,1645),(2050,1780)],CTL,width=2.8,arrow=False)
    d.line('config-bus',[(265,1780),(3195,1780)],CTL,width=3,arrow=False)
    configs=[('PLL / 时钟复位','配置 / 锁定 / 切换'),('DDR Controller','初始化 / QoS / 状态'),('DDR PHY','training / 校准'),
             ('LVDS','通道 / 对齐 / 帧行'),('ISP','尺寸 / 模式 / 参数'),('NPU 计算','命令 / GB 数据位置'),
             ('NPU / GB 搬运','地址 / 长度 / stride'),('帧写入 DMA','缓冲区 / 格式 / 帧状态'),('GB 管理','能力 / bank / 错误')]
    for i,(title,sub) in enumerate(configs):
        x=95+365*i
        d.line('cfg-drop-'+str(i),[(x+165,1780),(x+165,1805)],CTL,width=2.2)
        d.rect('config-C'+str(i+1),x,1805,335,100,PURPLE,INK,True,1.8)
        d.tag('C'+str(i+1),x+8,1814)
        d.text(x+190,1845,title,25,True)
        d.text(x+167,1884,sub,23)

    # A short legend preserves line semantics while leaving notes out of the drawing.
    for x,c,label in [(80,AXI,'AXI 请求 / 数据'),(540,GB,'GB 读写'),(905,PIX,'像素流'),(1240,CTL,'配置 / 控制')]:
        d.line('legend-'+c[1:],[(x,1970),(x+66,1970)],c,both=c==GB,width=3)
        d.text(x+82,1978,label,25,anchor='start',color=c)
    d.rect('legend-dash',1690,1956,54,26,'#FFFFFF',GRAY,True,1.8)
    d.text(1760,1978,'虚线：可选或新增候选',25,anchor='start',color=MUTED)
    d.text(2420,1978,'C1–C9：同一 IP 配置端',25,anchor='start',color=MUTED)
    d.text(3370,1978,'AXI 返回通道合并示意',23,anchor='end',color=MUTED)
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--skill',type=Path,default=Path.home()/'.codex/skills/svg-pptx-diagrams-native')
    p.add_argument('--svg-only',action='store_true')
    a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    stem='soc_reference_style'
    names=[a.out_dir/(stem+s) for s in ('.svg','.pptx','.export.json','.layout.json')]
    if any(x.exists() for x in names):p.error('Refusing to overwrite existing outputs')
    d=draw()
    ET.indent(d.root,space='  ')
    svg=names[0]
    ET.ElementTree(d.root).write(svg,encoding='utf-8',xml_declaration=True)
    names[3].write_text(json.dumps(dict(canvas=[W,H],blocks=d.blocks,texts=d.texts),ensure_ascii=False,indent=2)+'\n')
    if not a.svg_only:
        sys.path.insert(0,str(a.skill/'scripts'))
        from svg_to_pptx import read_svg,create_deck
        r=create_deck([read_svg(svg)],names[1],'source',
                      font_file=Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),slide_width_in=32)[0]
        r.update(source_svg=svg.name,svg_sha256=hashlib.sha256(svg.read_bytes()).hexdigest(),
                 skill='svg-pptx-diagrams-native',office_display_editing_tested=False,
                 scope='L01 diagram; candidate topology and no frozen addresses; no RTL modification')
        names[2].write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(r,ensure_ascii=False))
    print(svg)


if __name__=='__main__':main()
