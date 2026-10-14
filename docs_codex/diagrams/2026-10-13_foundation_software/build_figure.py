#!/usr/bin/env python3
"""One editable software-stack diagram; actual calls and support relationships."""
from pathlib import Path
from html import escape
ROOT = Path(__file__).resolve().parent
colors = {'software': ('#eaf1fc', '#4775ac'), 'device': ('#e9f5f1', '#287d70'),
          'interface': ('#f1ecf7', '#8660a5'), 'host': ('#fff2e5', '#bb6d30')}
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1390" viewBox="0 0 1600 1390">', '<defs>']
for key, (_, color) in colors.items():
    parts.append(f'<marker id="{key}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{color}"/></marker>')
parts += ['</defs>', '<rect x="0" y="0" width="1600" height="1390" fill="#fafcff"/>']
def text(x, y, value, size=21, bold=False, anchor='start', color='#26384b'):
    parts.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei" font-size="{size}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')
def box(x, y, w, h, title, lines, kind='software'):
    fill, stroke = colors[kind]
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    text(x+w/2, y+32, title, 23, True, 'middle')
    for i, value in enumerate(lines):
        text(x+w/2, y+64+28*i, value, 20, anchor='middle')
def arrow(points, label, lx, ly, kind='software', anchor='middle'):
    parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{colors[kind][1]}" stroke-width="2.4" marker-end="url(#{kind})"/>')
    text(lx, ly, label, 19, anchor=anchor, color=colors[kind][1])
text(40, 48, 'Cheshire 软件栈：基础软件使用接口契约，主机工具构建并装载程序', 30, True)
text(40, 112, '开发主机', 23, True)
text(440, 124, '目标端：应用、基础软件与硬件接口', 23, True)
text(1270, 265, '平台启动支持', 23, True)
box(40, 150, 310, 145, '编译、归档与链接', ['GCC / as / ld / ar', '源码 + 库 + 链接脚本', 'ELF / map / bin'], 'host')
box(440, 145, 480, 95, '应用 / 启动固件', ['main · printf 调用 · 介质加载'])
box(985, 145, 195, 95, '向量内核', ['RVV 指令'])
box(455, 330, 290, 115, '格式化公共库', ['printf_ / _vsnprintf', '_out_char'])
box(830, 330, 290, 115, '介质公共服务', ['gpt_boot_part_else_raw', 'gpt_read_t 回调'])
box(830, 510, 290, 115, 'Flash 器件 HAL', ['spi_s25fs512s_*', '器件命令 / 地址 / 分块'], 'device')
box(455, 705, 290, 115, '本地 UART DIF', ['_putchar → uart_write', '初始化 / LSR 轮询'], 'device')
box(830, 705, 290, 115, 'SPI Host DIF', ['dif_spi_host_transaction', 'handle / FIFO / 命令'], 'device')
box(455, 910, 665, 105, 'MMIO / CSR 辅助代码', ['reg8 / reg32 · mmio_region_read/write', 'set_mie / set_mtie / get_mcycle'], 'device')
box(440, 1100, 740, 115, '软硬件接口契约', ['ISA / CSR / MMIO / 异常与中断', '地址与字段 · 访问宽度 · 顺序和数据可见性'], 'interface')
box(440, 1280, 740, 80, 'SoC 硬件', ['CVA6 / Ara · AXI / Reg · 存储与外设控制器'], 'interface')
box(1270, 300, 290, 190, 'Boot ROM / crt0', ['片内存储 / sp / gp', 'BSS / FS / trap 入口', '装载 / 进入 main', '分别属于固件与应用'])
box(1270, 650, 290, 140, '板级参数与连接', ['地址 / 频率 / 复位', 'PAD / 片外器件', '启动介质 / 调试连接'], 'host')
box(40, 550, 310, 140, '寄存器生成', ['Python / regtool', 'HJSON → C 宏 / RTL', '偏移、字段与访问语义'], 'host')
box(40, 1120, 310, 145, '装载、调试与检查', ['GDB / OpenOCD', 'readelf / nm / objdump', '入口、符号与实际指令'], 'host')
arrow([(350,215),(440,215)], 'ELF', 395, 201, 'host')
arrow([(600,240),(600,330)], '调用', 642, 290)
arrow([(850,240),(975,240),(975,330)], '调用', 1015, 290)
arrow([(600,445),(600,705)], '字符回调', 666, 586)
arrow([(975,445),(975,510)], '读回调', 1026, 487)
arrow([(975,625),(975,705)], '控制器调用', 1050, 674, 'device')
arrow([(600,820),(600,910)], '寄存器访问', 682, 870, 'device')
arrow([(975,820),(975,910)], '寄存器访问', 1054, 870, 'device')
arrow([(785,1015),(785,1100)], 'load/store、CSR 指令', 957, 1067, 'device')
arrow([(1180,192),(1215,192),(1215,1160),(1180,1160)], 'RVV', 1200, 855, 'interface', 'end')
arrow([(810,1215),(810,1280)], '指令执行 / 总线事务 / 事件', 1000, 1254, 'interface')
arrow([(1425,300),(1425,88),(730,88),(730,145)], '建立执行环境', 1090, 78)
arrow([(350,630),(390,630),(390,967),(455,967)], 'C 宏', 424, 949, 'host')
arrow([(350,1200),(395,1200),(395,1315),(440,1315)], '装载', 400, 1188, 'host')
arrow([(1270,726),(1245,726),(1245,1334),(1180,1334)], '平台', 1210, 1322, 'host')
text(40, 350, '基础软件提供可调用的实现；', 21)
text(40, 382, '接口层规定操作的含义。', 21)
text(40, 825, 'libcheshire.a 是主机归档，', 21)
text(40, 857, '不是目标上的独立执行层。', 21)
(ROOT/'software-stack.svg').write_text('\n'.join(parts+['</svg>'])+'\n')
