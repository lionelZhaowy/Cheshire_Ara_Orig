"""Draw a source-grounded LLC figure; refuse to replace an existing SVG."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
BLUE, GREEN, INK = '#4478AA', '#34816B', '#172B4D'
PALE_BLUE, PALE_GREEN = '#E8F0FA', '#E6F4EE'
AMBER, PALE_AMBER = '#B68A2F', '#FFF3D9'


def build():
    root = ET.Element(f'{{{NS}}}svg', width='1680', height='1120', viewBox='0 0 1680 1120')
    ET.SubElement(root, f'{{{NS}}}title').text = 'LLC 多路组相联 Cache 与按 way 切换 SPM'
    ET.SubElement(root, f'{{{NS}}}desc').text = (
        '当前 DefaultCfg 的 8-way、256组、64字节行、128KiB数据阵列。'
        '左侧为全Cache逻辑结构，右侧为整way用途组合和SPM固定映射，底部为受控转换流程。')

    def element(tag, **attrs):
        return ET.SubElement(root, f'{{{NS}}}{tag}', {k: str(v) for k, v in attrs.items()})

    def rect(x, y, w, h, fill='#FFFFFF', stroke='#B8C6D4', radius=8, sw=2):
        return element('rect', x=x, y=y, width=w, height=h, rx=radius,
                       fill=fill, stroke=stroke, **{'stroke-width': sw})

    def text(x, y, value, size=22, color=INK, bold=False, anchor='start'):
        node = element('text', x=x, y=y, fill=color, **{
            'font-family': 'Microsoft YaHei, WenQuanYi Zen Hei, sans-serif',
            'font-size': size, 'font-weight': 'bold' if bold else 'normal', 'text-anchor': anchor})
        node.text = value
        return node

    def line(x1, y1, x2, y2, color=BLUE, sw=3):
        return element('line', x1=x1, y1=y1, x2=x2, y2=y2,
                       stroke=color, **{'stroke-width': sw})

    def arrow(x1, y1, x2, y2, color=BLUE):
        if y1 == y2:
            sign = 1 if x2 > x1 else -1
            line(x1, y1, x2-sign*12, y2, color)
            pts = f'{x2},{y2} {x2-sign*12},{y2-7} {x2-sign*12},{y2+7}'
        elif x1 == x2:
            sign = 1 if y2 > y1 else -1
            line(x1, y1, x2, y2-sign*12, color)
            pts = f'{x2},{y2} {x2-7},{y2-sign*12} {x2+7},{y2-sign*12}'
        else:
            raise ValueError('Use an explicit route for non-orthogonal arrows')
        element('polygon', points=pts, fill=color)

    rect(0, 0, 1680, 1120, '#FFFFFF', '#FFFFFF', radius=0)
    text(40, 63, 'LLC 多路组相联 Cache 与按 way 切换 SPM', 40, bold=True)
    text(40, 105, '当前 DefaultCfg：8 way × 256 行/way × 8 个 64-bit 数据块/行 = 128 KiB；每 way 16 KiB', 23, '#526477')

    rect(40, 138, 1020, 630, '#F5F7FA', radius=14)
    rect(1090, 138, 550, 630, '#F5F7FA', radius=14)
    text(68, 178, '① 全 Cache：8 路组相联（CFG_SPM = 0x00）', 28, bold=True)
    text(68, 211, '每一组有 8 个候选缓存行；每单元上部是 Tag/V/D，下部是 64 B 数据', 21, '#526477')

    fields = [(68, 400, 'Tag  [47:14]', '34 bit'),
              (468, 230, 'Set  [13:6]', '8 bit → 256 组'),
              (698, 180, 'Block  [5:3]', '8 个数据块'),
              (878, 150, 'Byte  [2:0]', '块内 8 字节')]
    for x, width, title, detail in fields:
        rect(x, 230, width, 60, PALE_BLUE, BLUE, radius=0)
        text(x+width/2, 255, title, 22, anchor='middle', bold=True)
        text(x+width/2, 279, detail, 19, '#526477', anchor='middle')
    element('path', d='M 583 290 L 583 306 L 150 306 L 150 522 L 168 522',
            fill='none', stroke=AMBER, **{'stroke-width': 3})
    element('polygon', points='180,522 168,515 168,529', fill=AMBER)
    text(171, 322, 'Set 索引选中同一组，Tag 与各 way 元数据并行比较', 19, '#82601B')

    for way in range(8):
        x = 180 + way*106
        rect(x, 336, 100, 35, PALE_BLUE, BLUE, radius=5)
        text(x+50, 361, f'Way {way}', 22, anchor='middle', bold=True)
    rows = [(0, 375), (1, 435), (42, 495), (255, 615)]
    rect(170, 489, 864, 66, PALE_AMBER, AMBER, radius=5)
    for index, y in rows:
        text(80, y+34, f'组 {index}', 22, bold=(index == 42))
        for way in range(8):
            x = 180 + way*106
            hit = index == 42 and way == 6
            fill = PALE_GREEN if hit else PALE_AMBER if index == 42 else PALE_BLUE
            stroke = GREEN if hit else AMBER if index == 42 else BLUE
            rect(x, y, 100, 26, fill, stroke, radius=0)
            rect(x, y+26, 100, 28, PALE_GREEN if hit else '#FFFFFF', stroke, radius=0)
            text(x+50, y+20, 'T / V / D', 18, anchor='middle')
            text(x+50, y+47, '64 B', 19, anchor='middle', bold=hit)
    text(94, 590, '⋮', 32, '#526477', anchor='middle')
    for way in range(8):
        text(230+way*106, 590, '⋮', 32, '#526477', anchor='middle')
    text(68, 701, '命中举例：组 42 的 Way 6；Way 由 Tag+Valid 命中结果选择，不是 Cache 地址字段', 21)
    text(68, 731, '未命中：在 Cache way 中替换 / 回填；Dirty 决定是否向下游 DDR 回写', 21)
    text(68, 756, '图中为逻辑行对应关系；Tag SRAM 与 Data SRAM 是不同存储阵列。', 19, '#526477')

    text(1118, 178, '② 复用同一数据阵列：按整 way 分配', 26, bold=True)
    text(1118, 211, '位图：1 = SPM（S），0 = Cache（C）', 21, '#526477')
    states = [(247, 270, 0x00, '全 Cache 0x00：128 KiB Cache'),
              (352, 375, 0x0F, '混合示例 0x0F：64 KiB SPM + 64 KiB Cache'),
              (457, 480, 0xFF, '启动全 SPM 0xFF：128 KiB SPM')]
    for label_y, y, mask, label in states:
        text(1118, label_y, label, 21, bold=True)
        for way in range(8):
            x = 1118 + way*61
            spm = bool(mask & (1 << way))
            rect(x, y, 58, 54, PALE_GREEN if spm else PALE_BLUE,
                 GREEN if spm else BLUE, radius=5)
            text(x+29, y+22, f'W{way}', 19, anchor='middle')
            text(x+29, y+46, 'S' if spm else 'C', 22, anchor='middle', bold=True)
    text(1118, 553, '全 SPM：DDR 访问走旁路，SPM 访问留在阵列', 18, '#526477')
    text(1118, 583, 'SPM 固定映射：base + way × 0x4000', 22, bold=True)
    text(1118, 608, 'Way 2：0x10008000–0x1000BFFF', 21)
    text(1118, 639, '地址 0x10008AAB → Way 2 / 组 42', 21)
    text(1118, 669, '块 5 / 字节 3；直接寻址，不比较 Tag', 21)
    text(1118, 704, '未设为 SPM 的 way，其 SPM 槽访问报错', 20, '#9B4141')
    text(1118, 734, '用途改变不压缩地址槽；不是新增加一块 RAM', 20, '#526477')

    rect(40, 795, 1600, 243, '#F5F7FA', radius=14)
    text(68, 836, '③ 转换控制：软件提出目标位图，LLC 硬件协调提交与所需刷新', 28, bold=True)
    steps = [(70, 275, ['停止相关访问', '迁移代码 / 栈 / 保留数据', '协调缓冲与在途事务']),
             (390, 225, ['写 CFG_SPM', '1 → SPM；0 → Cache']),
             (660, 240, ['写 COMMIT = 1', '发起配置提交']),
             (945, 320, ['LLC 配置 FSM', '等待 / 协调已有请求', '必要的 flush / Dirty 回写']),
             (1310, 290, ['按寄存器契约确认完成', '恢复对新用途的访问'])]
    for idx, (x, width, lines) in enumerate(steps):
        rect(x, 867, width, 103, PALE_GREEN if idx == 4 else PALE_BLUE,
             GREEN if idx == 4 else BLUE, radius=10)
        for j, value in enumerate(lines):
            text(x+width/2, 896+j*28, value, 21 if j else 22,
                 anchor='middle', bold=(j == 0))
        if idx < len(steps)-1:
            arrow(x+width, 918, steps[idx+1][0], 918, GREEN)
    text(68, 1008, 'SPM → Cache 前保存所需内容；转换不会自动把数据复制到另一块 RAM，原 SPM 内容将失去固定驻留保证。', 21, '#9B4141')
    text(40, 1072, '注意：SPM 绕过的是 LLC Tag 管理，不等于 CPU L1 一定不缓存；0x14000000 别名映射同一 SPM 阵列。', 20, '#526477')
    text(40, 1104, '依据：cheshire_pkg / cheshire_soc；axi_llc_burst_cutter / hit_miss / config；Boot ROM · HEAD 278434024 · 2026-10-10 · 未新增目标运行', 17, '#526477')
    ET.indent(root, space='  ')
    return ET.tostring(root, encoding='unicode')+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f'Refusing to replace existing figure: {args.output}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(), encoding='utf-8')
    print(args.output)
