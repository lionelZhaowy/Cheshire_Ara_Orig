#!/usr/bin/env python3
"""Generate the agreed architecture figure; refuse to replace an existing SVG."""
from pathlib import Path
import argparse
import json
import math
import xml.etree.ElementTree as ET
from PIL import ImageFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parent)
args = parser.parse_args()
ROOT = args.out_dir.resolve()
DEST = ROOT / 'cheshire_software_hardware.svg'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
svg = ET.Element(f'{{{NS}}}svg', width='2000', height='1500', viewBox='0 0 2000 1500')
INK, MUTED, BORDER = '#183247', '#536777', '#C6D3DE'
BLUE, PURPLE, TEAL, ORANGE = '#28619B', '#705293', '#21756C', '#AD6631'
FONT = 'Microsoft YaHei, WenQuanYi Zen Hei, sans-serif'
FONTFILE = Path('/mnt/c/Windows/Fonts/msyh.ttc')
FONTBOLD = Path('/mnt/c/Windows/Fonts/msyhbd.ttc')
text_checks = []


def el(tag, **attrs):
    return ET.SubElement(svg, f'{{{NS}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def rect(x, y, w, h, fill='#FFFFFF', stroke=BORDER, radius=10):
    return el('rect', x=x, y=y, width=w, height=h, rx=radius, fill=fill,
              stroke=stroke, stroke_width=1.5)


def line(x1, y1, x2, y2, color=BLUE, width=2):
    return el('line', x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=width)


def text(x, y, value, size=24, color=INK, bold=False, anchor='start', maxwidth=None):
    node = el('text', x=x, y=y, fill=color, font_family=FONT, font_size=size,
              font_weight='bold' if bold else 'normal', text_anchor=anchor)
    node.text = value
    fontpath = FONTBOLD if bold else FONTFILE
    if fontpath.is_file():
        font = ImageFont.truetype(str(fontpath), size)
        measured = font.getlength(value)
        if maxwidth is not None:
            assert measured <= maxwidth, (value, measured, maxwidth)
        left = x - (measured / 2 if anchor == 'middle' else measured if anchor == 'end' else 0)
        assert left >= 0 and left + measured <= 2000, value
        text_checks.append({'text': value, 'width': round(measured, 2), 'limit': maxwidth})
    return node


def arrow(x1, y1, x2, y2, color=BLUE, both=False):
    line(x1, y1, x2, y2, color, 2.5)
    def head(ax, ay, bx, by):
        dx, dy = bx-ax, by-ay
        length = math.hypot(dx, dy)
        ux, uy = dx/length, dy/length
        pts = [(bx, by), (bx-9*ux-4*uy, by-9*uy+4*ux),
               (bx-9*ux+4*uy, by-9*uy-4*ux)]
        el('polygon', points=' '.join(f'{x},{y}' for x,y in pts), fill=color, stroke='none')
    head(x1, y1, x2, y2)
    if both:
        head(x2, y2, x1, y1)


def planned(x, y, w, h):
    rect(x, y, w, h, '#FFF9EF', 'none', 0)
    # Independent line segments preserve editable dashed borders in the supported SVG subset.
    for sx, sy, ex, ey in [(x,y,x+w,y),(x,y+h,x+w,y+h),(x,y,x,y+h),(x+w,y,x+w,y+h)]:
        length = math.hypot(ex-sx, ey-sy)
        ux, uy = (ex-sx)/length, (ey-sy)/length
        for n in range(0, int(length), 20):
            end = min(n+11, length)
            line(sx+n*ux, sy+n*uy, sx+end*ux, sy+end*uy, ORANGE, 1.8)


def card(x, y, w, h, title, subtitle='', future=False, color=INK, title_size=26):
    if future:
        planned(x,y,w,h)
    else:
        rect(x,y,w,h)
    text(x+w/2, y+37, title, title_size, color, True, 'middle', w-24)
    if subtitle:
        text(x+w/2, y+(65 if h < 80 else 70), subtitle, 21, MUTED, anchor='middle', maxwidth=w-22)


def band(y, h, number, title, subtitle, fill, accent):
    rect(40,y,1500,h,fill,'none',12)
    rect(40,y,8,h,accent,'none',0)
    text(68,y+40,number,22,accent,True)
    text(68,y+82,title,29,INK,True,maxwidth=156)
    text(68,y+114,subtitle,19,MUTED,maxwidth=155)
    line(214,y+24,214,y+h-24,'#CFD9E2',1.5)


def rail(y,h,title,kicker,rows):
    rect(1570,y,390,h,'#F3F6F9','#D9E2E9')
    text(1592,y+36,kicker,19,BLUE,True,maxwidth=346)
    text(1592,y+74,title,28,INK,True,maxwidth=346)
    for i,row in enumerate(rows):
        text(1592,y+112+31*i,row,22,MUTED,maxwidth=346)


rect(0,0,2000,1500,'#FFFFFF','none',0)
text(40,65,'Cheshire SoC 软硬件分层结构',46,INK,True)
text(42,107,'以当前裸机工程为主线 · 通用功能、设备控制与指令执行各有明确边界',25,MUTED)
text(1960,65,'工程结构 / 规划扩展',22,TEAL,True,'end')
text(1960,101,'mp/ara-pulp-v2 · 278434024',20,MUTED,anchor='end')

# Application software: presence of an example is not a claim of successful execution.
band(150,140,'01','应用软件','表达计算与任务','#F0EAF8',PURPLE)
card(240,176,300,88,'裸机应用与测试','HelloWorld · 结果校验')
card(558,176,300,88,'向量算法','RVV · 矩阵计算')
card(876,176,302,88,'系统工具','介质烧写 · 下载执行')
card(1196,176,320,88,'图像处理与推理','ISP / NPU 工作负载〔规划〕',True,title_size=25)

# Foundation software. Arrows are representative function calls, not mandatory gates.
band(310,460,'02','基础软件','功能与设备控制','#EAF3FC',BLUE)
text(240,344,'通用功能与器件协议',22,BLUE,True)
text(1516,344,'应用可直接调用所需接口',20,MUTED,anchor='end')
card(240,361,264,94,'printf','格式化文本 → _putchar')
card(532,361,264,94,'GPT 解析','read 回调访问介质')
card(824,361,376,94,'存储器件 HAL','SPI Flash · SD · I²C EEPROM',title_size=25)
card(1228,361,288,94,'UART debug HAL','READ / WRITE / EXEC',title_size=24)
arrow(798,406,820,406)
arrow(372,458,372,510)
arrow(1012,458,1012,510)
text(570,493,'代表性函数调用',19,MUTED)
card(240,514,264,90,'UART DIF','初始化 · FIFO 字节收发')
card(532,514,668,90,'SPI / I²C / GPIO DIF','控制器配置 · 传输段 · 状态与寄存器操作',title_size=26)
card(1228,514,288,90,'CLINT / DMA 接口','计时 · 配置与提交',title_size=24)
arrow(372,606,372,642)
arrow(1012,606,1012,642)
arrow(1372,606,1372,642)
rect(240,646,1276,76,'#FFFFFF','#A9C3DD',8)
text(260,677,'MMIO 访问工具',25,BLUE,True)
text(515,677,'reg8 / reg32 · mmio_region_read / write',23,INK)
text(260,707,'基址 + 寄存器偏移 + 访问位宽；regs 头文件提供偏移和位字段',22,MUTED)
text(240,753,'其他专用库：LLC · AXI RT     |     libcheshire.a：代码归档方式，涵盖多个职责',22,MUTED)

# Interface stripe: architectural contracts, not a software service module.
band(790,150,'接口','接口边界','软件可见的契约','#E8F4F1',TEAL)
card(240,818,300,94,'指令执行','标量指令 · RVV',color=TEAL)
card(558,818,300,94,'CSR 与特权状态','处理器配置与控制',color=TEAL)
card(876,818,302,94,'内存与 MMIO','地址 · 属性 · 寄存器语义',color=TEAL,title_size=25)
card(1196,818,320,94,'异常与中断','事件入口 · 处理与返回',color=TEAL)

# SoC hardware: structural connectivity, not a complete bus netlist.
band(960,340,'03','SoC 硬件','执行、存储与传输','#FFF0E4',ORANGE)
card(240,1000,264,91,'CVA6','取指 · 执行 · 访存')
card(532,1000,264,91,'Ara','RVV 执行 · 向量访存')
card(824,1000,264,91,'iDMA','硬件数据搬运')
card(1116,1000,400,91,'NPU / ISP / 图像接入','自定义 IP 与接口〔规划〕',True,title_size=24)
arrow(506,1040,530,1040,ORANGE,True)
text(523,990,'专用请求 / 响应',19,ORANGE,anchor='middle')
for x in (372,664,956):
    arrow(x,1093,x,1127,ORANGE,True)
text(1316,1120,'接入与 DDR 旁路方案待实现',20,ORANGE,anchor='middle')
rect(240,1131,1276,46,'#F8D9BF','none',6)
text(878,1162,'AXI 互连与适配 · 地址路由 · 主设备共享访问',25,INK,True,'middle')
arrow(505,1179,505,1200,ORANGE,True)
arrow(1155,1179,1155,1200,ORANGE,True)
rect(240,1204,530,72,'#FFFFFF',BORDER,8)
text(505,1234,'原子适配 → LLC / SPM → 主存出口',23,INK,True,'middle',506)
text(505,1263,'SPM 复用 LLC 存储阵列',21,MUTED,anchor='middle')
rect(794,1204,722,72,'#FFFFFF',BORDER,8)
text(1155,1234,'寄存器总线 → 外设 / 平台控制',25,INK,True,'middle')
text(1155,1263,'UART · SPI · I²C · GPIO · 中断/定时器 · ROM 接口',21,MUTED,anchor='middle',maxwidth=696)

band(1320,112,'04','片外器件','经对应控制器连接','#F0F3F6',MUTED)
# Compact label position in the short bottom band.
# Move the label block's text upward to retain clear lower margins.
labels = list(svg)[-4:]
for node in labels:
    if node.tag.endswith('text'):
        node.set('y',str(float(node.get('y'))-20))
arrow(505,1278,505,1340,ORANGE,True)
arrow(1009,1278,1009,1340,ORANGE,True)
card(240,1343,530,74,'DDR 存储器','经 DDR 控制器 / PHY 接入',title_size=25)
card(794,1343,430,74,'Flash · SD 卡 · EEPROM','经 SPI / I²C 接入',title_size=24)
card(1242,1343,274,74,'图像传感器〔规划〕','LVDS 图像输入',True,title_size=23)

# Orthogonal concerns stay outside the main vertical architecture.
rail(150,200,'构建支持','开发主机上的工具',[
    '编译器 · 汇编器 · 链接器',
    'Makefile · 链接脚本 · 库归档',
    '生成 ELF，规定代码与数据布局'])
rail(370,308,'启动与运行支持','准备并维持软件执行环境',[
    'Boot ROM / 载荷加载',
    'crt0：栈、BSS、异常入口',
    '进入 main；异常处理与返回',
    '启动交接与函数调用分别表达',
    '运行期也可访问必要配置接口',
    '不是每次设备调用的必经层'])
rail(698,250,'可选操作系统','扩展方向 · 目标运行待验证',[
    'RTOS：任务、调度与同步',
    'Linux：用户态 / 内核 / 驱动',
    '依各自环境建立设备访问路径',
    '不假定直接复用整套裸机 HAL'])
rail(968,202,'硬件实现平台','同一结构的实现与适配维度',[
    'FPGA：现有 VCU118 工程',
    'ASIC：宏、时钟、PAD 等适配',
    'ASIC 实现与验证仍待完成'])
rect(1570,1190,390,242,'#F3F6F9','#D9E2E9')
text(1592,1228,'阅读图例',27,INK,True)
rect(1592,1250,35,23,'#FFFFFF',BORDER,2)
text(1642,1270,'实线框：已有代码 / 结构',21,MUTED,maxwidth=295)
planned(1592,1290,35,23)
text(1642,1310,'虚线框：规划中的扩展',21,MUTED,maxwidth=295)
arrow(1592,1340,1627,1340,BLUE)
text(1642,1347,'蓝色箭头：代表性调用',21,MUTED,maxwidth=295)
arrow(1592,1380,1627,1380,ORANGE,True)
text(1642,1387,'棕色箭头：硬件连接',21,MUTED,maxwidth=295)

text(40,1471,'说明：图示为职责与结构总览；模块按配置启用，已有结构不代表全部功能已仿真或板测。',21,MUTED)
text(1960,1471,'L01 · 2026-10-09',21,MUTED,anchor='end')

if DEST.exists():
    raise SystemExit(f'Refusing to overwrite {DEST}')
ROOT.mkdir(parents=True, exist_ok=True)
ET.indent(svg,space='  ')
with DEST.open('wb') as stream:
    ET.ElementTree(svg).write(stream,encoding='utf-8',xml_declaration=True)
    stream.write(b'\n')
(ROOT/'layout_checks.json').write_text(json.dumps({'canvas':[2000,1500],
    'font_measurement':str(FONTFILE), 'checks':text_checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(DEST)
