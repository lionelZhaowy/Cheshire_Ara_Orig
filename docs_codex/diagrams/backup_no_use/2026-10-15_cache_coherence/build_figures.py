#!/usr/bin/env python3
"""Generate the three L01 coherence figures; write into a new output directory."""
import argparse
import json
from html import escape
from pathlib import Path

W, H = 1920, 1080
C = dict(ink='#29292D', muted='#606773', data='#314D66', control='#765489',
         local='#187C78', cpu='#F1D7D9', memory='#D8E8F4', gb='#D9EEE8',
         interconnect='#F5E1C9', agent='#E8DFED')


class Figure:
    def __init__(self, name, title, subtitle):
        self.name = name
        self.boxes, self.arrows = {}, []
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                      f'<title>{escape(title)}</title>', '<defs>']
        for key in ('data', 'control', 'local'):
            self.parts.append(f'<marker id="{key}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{C[key]}"/></marker>')
        self.parts += ['</defs>', f'<rect id="background" x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF" stroke="none"/>']
        self.text(50, 54, title, 36, bold=True)
        self.text(50, 96, subtitle, 24, color=C['muted'])

    def text(self, x, y, text, size=25, color=None, anchor='start', bold=False, owner=''):
        tag = f' data-owner="{owner}"' if owner else ''
        self.parts.append(f'<text x="{x}" y="{y}" font-family="WenQuanYi Zen Hei" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color or C["ink"]}"{tag}>{escape(text)}</text>')

    def rect(self, key, x, y, w, h, fill, dashed=False):
        dash = ' stroke-dasharray="9 6"' if dashed else ''
        self.parts.append(f'<rect id="{key}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{C["ink"]}" stroke-width="1.7"{dash}/>')
        self.boxes[key] = dict(x=x, y=y, width=w, height=h)

    def box(self, key, x, y, w, h, title, lines=(), fill='memory', dashed=False):
        self.rect(key, x, y, w, h, C.get(fill, fill), dashed)
        n = len(lines)
        center = y + h/2
        first = center - n*17 + 10
        self.text(x+w/2, first, title, 27, anchor='middle', bold=True, owner=key)
        for i, line in enumerate(lines):
            self.text(x+w/2, first+35*(i+1), line, 24, anchor='middle', owner=key)

    def arrow(self, key, points, kind='data', both=False, start='', end='', jump=None):
        attrs = f'id="{key}" fill="none" stroke="{C[kind]}" stroke-width="2.8" stroke-linejoin="miter" marker-end="url(#{kind})"'
        if both:
            attrs += f' marker-start="url(#{kind})"'
        if jump:
            self.parts.append(f'<path {attrs} d="{jump}"/>')
        else:
            p = ' '.join(f'{x},{y}' for x,y in points)
            self.parts.append(f'<polyline {attrs} points="{p}"/>')
        self.arrows.append(dict(id=key, points=points, kind=kind, bidirectional=both,
                                source=start, target=end, jump=bool(jump)))

    def save(self, out):
        (out/f'{self.name}.svg').write_text('\n'.join(self.parts+['</svg>'])+'\n')
        return dict(name=self.name, canvas=[W,H], boxes=self.boxes, arrows=self.arrows)


def system():
    f = Figure('system', 'DDR–GB：逐行 I/O 一致性候选',
               '设备数据不分配 LLC 行；缓存探测、在途事务与访问次序仍需协调')
    f.rect('cva6',60,210,440,270,C['cpu'])
    f.text(280,260,'CVA6',30,anchor='middle',bold=True)
    f.text(280,298,'缓存侧需扩展探测与冲突处理',23,anchor='middle')
    f.box('l1d',90,330,170,110,'L1D',['WT / 读副本'],fill='memory')
    f.box('wbuffer',290,330,180,110,'写缓冲',['在途标量写'],fill='memory')
    f.box('ara',620,250,250,160,'Ara',['独立 AXI 访存','保留现有协作机制'],fill='cpu')
    f.box('device',1090,250,300,160,'NPU / ISP 数据代理',['任务 / 搬运事务','候选一致性入口'],fill='memory',dashed=True)
    f.box('gb',1530,250,300,160,'GB 独立 SRAM',['显式搬运 / 分块所有权','不跟踪 DDR 后续修改'],fill='gb')
    f.box('xbar',60,570,810,110,'主 Xbar / 原子适配',['普通内存路径；reservation 观察域需重审'],fill='interconnect')
    f.box('llc',110,770,600,130,'LLC',['WB 数据阵列 + 候选逐行探测 / 供数接口'],fill='memory')
    f.box('coord',1000,570,480,250,'一致性协调点（候选职责）',
          ['逐行串行化 / 在途跟踪','探测、失效确认与数据来源选择','缓存侧与各访存入口共同配合'],fill='agent',dashed=True)
    f.box('controller',1600,630,260,120,'DDR Controller',['AXI4 下游接口'])
    f.box('ddr',1600,850,260,120,'DDR',['外部主存'])
    f.arrow('cpu-path',[(280,480),(280,570)],both=True,start='cva6',end='xbar')
    f.arrow('ara-path',[(745,410),(745,570)],both=True,start='ara',end='xbar')
    f.arrow('xbar-llc',[(400,680),(400,770)],both=True,start='xbar',end='llc')
    f.text(420,733,'普通请求 / 返回',23,color=C['data'])
    f.arrow('llc-path',[(710,835),(900,835),(900,740),(1000,740)],both=True,start='llc',end='coord')
    f.text(730,878,'普通数据路径',23,color=C['data'])
    f.arrow('device-path',[(1240,410),(1240,570)],both=True,start='device',end='coord')
    f.text(1260,490,'不分配 LLC 行',24,color=C['data'])
    f.arrow('device-gb',[(1390,330),(1530,330)],'local',both=True,start='device',end='gb')
    f.text(1460,302,'搬运',24,color=C['local'],anchor='middle')
    f.arrow('ara-gb',[(870,285),(930,285),(930,170),(1680,170),(1680,250)],'local',both=True,start='ara',end='gb')
    f.text(1210,154,'Ara→GB 候选支路',24,color=C['local'])
    f.arrow('coord-ddr',[(1480,690),(1600,690)],both=True,start='coord',end='controller')
    f.arrow('controller-ddr',[(1730,750),(1730,850)],both=True,start='controller',end='ddr')
    f.arrow('probe-l1',[(1000,600),(950,600),(950,515),(175,515),(175,440)],'control',both=True,start='coord',end='l1d',
            jump='M 1000 600 L 950 600 L 950 515 L 755 515 Q 745 500 735 515 L 290 515 Q 280 500 270 515 L 175 515 L 175 440')
    f.text(480,500,'L1 探测 / 确认',23,color=C['control'])
    f.arrow('probe-llc',[(1000,785),(955,785),(955,947),(400,947),(400,900)],'control',both=True,start='coord',end='llc')
    f.text(485,932,'LLC 探测 / 确认 / 必要时供数',23,color=C['control'])
    f.text(55,1020,'蓝灰：数据访问（请求 / 返回合并画）    紫：候选一致性接口    绿：GB 访问',24)
    f.text(55,1055,'虚线框：新增职责。缓存直接供数为待评审路径；不是仅在 LLC 出口增加一个桥。',23,color=C['muted'])
    return f


def read_to_gb():
    f = Figure('read-to-gb','DDR 地址数据搬入 GB：最新版本从哪里来',
               '先满足发布顺序，再协调目标行；一致性读不要求把所有数据先写入 DDR')
    rows = [
        (150,'A  DDR 已最新，无冲突在途事务',
         [('DDR',['最新版本可读'],'memory'),('协调点',['确认无更新缓存版本'],'agent'),('搬运器',['接收本次读取结果'],'memory'),('GB',['写入后发布 ready'],'gb')],
         'L1D / LLC 的干净副本可以保留；不需要无条件 flush。'),
        (435,'B  LLC 持有最新脏数据',
         [('LLC 脏行',['比 DDR 更新'],'memory'),('协调点',['取得缓存数据'],'agent'),('搬运器',['接收最新版本'],'memory'),('GB',['保存显式快照'],'gb')],
         '本行画候选缓存供数；若限定仅从 DDR 读取，则先 clean 到 DDR，再读取。'),
        (720,'C  CPU 有按顺序必须先完成的写',
         [('CPU 写缓冲',['建立发布顺序 / 排空'],'cpu'),('LLC / 共享点',['接收已排序的更新'],'memory'),('协调后搬运',['不抢读旧 DDR'],'agent'),('GB',['数据完整后才 ready'],'gb')],
         '协调同址回填 / 替换；不要求外部读看见尚未发布的任意 CPU 写。')]
    xs, widths = [70,570,1070,1550],[380,380,350,290]
    for i,(y,title,boxes,note) in enumerate(rows):
        f.rect(f'row-{i}',40,y,1840,250,'#F7F9FA')
        f.text(65,y+40,title,27,bold=True)
        for j,(label,lines,color) in enumerate(boxes):
            f.box(f'r{i}-{j}',xs[j],y+72,widths[j],110,label,lines,fill=color)
        for j in range(3):
            f.arrow(f'r{i}-flow-{j}',[(xs[j]+widths[j],y+127),(xs[j+1],y+127)],'local' if j==2 else 'data',start=f'r{i}-{j}',end=f'r{i}-{j+1}')
        f.text(70,y+222,note,24,color=C['muted'])
    f.text(55,1030,'箭头表示受协调的数据传递。GB 就绪后，源 DDR 的后续变化不会自动更新这份副本。',25)
    return f


def write_to_ddr():
    f=Figure('write-to-ddr','GB 数据写入 DDR：先协调，再发布新版本',
             '完整覆盖与部分更新都需处理在途冲突、失效确认及任务完成；下图为逻辑阶段')
    xs=[60,430,800,1170,1540]; width=300
    f.rect('full-panel',40,150,1840,350,'#F7F9FA')
    f.text(65,194,'A  完整覆盖所有相关一致性粒度',28,bold=True)
    full=[('GB 新数据',['全行备妥','全部字节有效'],'gb'),('目标行协调',['排序在途访问','取得本次写权限'],'agent'),
          ('L1D / LLC',['失效并确认','条件满足可弃旧脏行'],'memory'),('DDR 写入',['提交完整新行','旧写不得迟到覆盖'],'memory'),('完成 / 释放',['达到约定可见点','再发布任务状态'],'agent')]
    for j,(title,lines,color) in enumerate(full):
        f.box(f'full-{j}',xs[j],235,width,150,title,lines,fill=color)
    for j in range(4):
        f.arrow(f'full-flow-{j}',[(xs[j]+width,310),(xs[j+1],310)],'control',start=f'full-{j}',end=f'full-{j+1}')
    f.text(70,443,'“完整”按实际缓存粒度判断：满 WSTRB 的一个 beat，可能仍只覆盖缓存行的一部分。',25)
    f.rect('partial-panel',40,545,1840,435,'#F7F9FA')
    f.text(65,589,'B  部分行更新：先保护未覆盖字节的最新值',28,bold=True)
    partial=[('GB 新字节',['地址 / 长度','字节有效掩码'],'gb'),('目标行协调',['阻止冲突越过','排序回填 / 替换'],'agent'),
             ('L1D / LLC',['clean 或取数暂存','失效旧副本并确认'],'memory'),('DDR 更新',['按 WSTRB 更新','或写入已合并新行'],'memory'),('完成 / 释放',['不把请求接收','当作全部动作完成'],'agent')]
    for j,(title,lines,color) in enumerate(partial):
        f.box(f'part-{j}',xs[j],630,width,150,title,lines,fill=color)
    for j in range(4):
        f.arrow(f'part-flow-{j}',[(xs[j]+width,705),(xs[j+1],705)],'control',start=f'part-{j}',end=f'part-{j+1}')
    f.text(75,850,'最新旧行',24)
    for j,label in enumerate('ABCD'):
        f.box(f'old-{j}',225+j*85,805,78,70,label,fill='memory')
    f.text(610,850,'+ GB 仅更新第二段 X',25,color=C['local'])
    f.arrow('merge-example',[(910,840),(1080,840)],'local')
    for j,label in enumerate('AXCD'):
        f.box(f'new-{j}',1120+j*85,805,78,70,label,fill='gb' if j==1 else 'memory')
    f.text(1515,850,'A / C / D 不丢失',25)
    f.text(70,934,'旧 dirty 行不能在新写之后再覆盖 DDR；失败或超时不能直接复用缓冲，也不承诺自动回滚。',25)
    f.text(55,1030,'逐行协调不等于整帧快照；跨行数据发布仍需版本、所有权或双缓冲。',25)
    return f


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out-dir',required=True,type=Path)
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=False)
    figs=[system(),read_to_gb(),write_to_ddr()]
    layout=[f.save(args.out_dir) for f in figs]
    (args.out_dir/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'figures':len(figs),'arrows':sum(len(f.arrows) for f in figs)},ensure_ascii=False))


if __name__=='__main__':
    main()
