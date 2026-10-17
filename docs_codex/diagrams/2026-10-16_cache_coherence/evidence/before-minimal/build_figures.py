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
    def __init__(self, name, title, subtitle, width=W, height=H):
        self.name = name
        self.canvas = [width, height]
        self.autojump = False
        self.boxes, self.arrows = {}, []
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      f'<title>{escape(title)}</title>', '<defs>']
        for key in ('data', 'control', 'local'):
            self.parts.append(f'<marker id="{key}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{C[key]}"/></marker>')
        self.parts += ['</defs>', f'<rect id="background" x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF" stroke="none"/>']
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
        if self.autojump and jump is None:
            jump = self.crossing_path(points)
        if jump:
            self.parts.append(f'<path {attrs} d="{jump}"/>')
        else:
            p = ' '.join(f'{x},{y}' for x,y in points)
            self.parts.append(f'<polyline {attrs} points="{p}"/>')
        self.arrows.append(dict(id=key, points=points, kind=kind, bidirectional=both,
                                source=start, target=end, jump=bool(jump)))

    def crossing_path(self, points):
        """Keep independent crossing routes continuous and visibly unconnected."""
        parts = [f'M {points[0][0]} {points[0][1]}']
        crossed = False
        for (x1,y1),(x2,y2) in zip(points,points[1:]):
            vertical = x1 == x2
            hits = []
            for edge in self.arrows:
                for (a,b),(c,d) in zip(edge['points'],edge['points'][1:]):
                    if vertical and b == d and min(a,c) < x1 < max(a,c) and min(y1,y2)+10 < b < max(y1,y2)-10:
                        hits.append(b)
                    elif not vertical and a == c and min(b,d) < y1 < max(b,d) and min(x1,x2)+10 < a < max(x1,x2)-10:
                        hits.append(a)
            sign = 1 if (y2-y1 if vertical else x2-x1) > 0 else -1
            for v in sorted(set(hits),reverse=sign<0):
                crossed = True
                if vertical:
                    parts += [f'L {x1} {v-sign*8}',f'Q {x1+13} {v} {x1} {v+sign*8}']
                else:
                    parts += [f'L {v-sign*8} {y1}',f'Q {v} {y1-13} {v+sign*8} {y1}']
            parts.append(f'L {x2} {y2}')
        return ' '.join(parts) if crossed else None

    def save(self, out):
        (out/f'{self.name}.svg').write_text('\n'.join(self.parts+['</svg>'])+'\n')
        return dict(name=self.name, canvas=self.canvas, boxes=self.boxes, arrows=self.arrows)


def system():
    f = Figure('system', 'DDR–GB：数据存储互连与一致性协调',
               '普通主存、GB 访问与 DDR 搬运分路；虚线表示新增或待扩展职责',2400,1350)
    f.autojump = True
    f.rect('cpu-domain',50,140,1710,510,C['cpu'])
    f.text(75,175,'CVA6–Ara 普通主存路径与 GB 分流',29,bold=True)
    f.rect('gb-domain',50,700,1710,345,C['gb'],dashed=True)
    f.text(75,735,'共享 GB：计算访问与显式搬运',29,bold=True)
    f.rect('controller',2100,140,260,920,C['memory'],dashed=True)
    f.text(2230,195,'DDR 控制器',28,anchor='middle',bold=True)
    f.text(2230,238,'合流位置示意',24,anchor='middle')
    f.rect('cva6',70,210,400,200,'#FFFFFF')
    f.text(270,248,'CVA6',28,anchor='middle',bold=True)
    f.box('l1d',90,280,160,100,'L1D',['WT / 读副本'],fill='memory')
    f.box('wbuffer',280,280,170,100,'写缓冲',['在途标量写'],fill='memory')
    f.box('ara',70,490,220,110,'Ara',['单一 AXI 出口'],fill='cpu')
    f.box('filter',350,490,230,110,'失效过滤',['现有 Ara 机制'],fill='#FFFFFF')
    f.box('split',650,490,250,110,'地址分流',['普通地址 / GB'],fill='#FFFFFF',dashed=True)
    f.box('width',1040,480,300,120,'位宽适配',['普通地址 → 64-bit'],fill='#FFFFFF')
    f.box('xbar',1040,210,300,130,'主 AXI Xbar',['系统 64-bit'],fill='interconnect')
    f.box('atomics',1430,210,300,130,'原子适配',['AMO / LRSC'],fill='interconnect')
    f.box('llc',1430,445,300,150,'LLC / SPM',['WB 缓存 / 片上 SPM','逐行协调接口待扩展'],fill='memory')
    f.box('npu',70,760,270,110,'NPU 计算',['GB 数据读写'],fill='cpu')
    f.box('isp',70,900,270,110,'ISP / 帧写入器',['GB 工作区 / DDR 帧'],fill='interconnect')
    f.box('proxy',630,770,300,190,'共享数据代理',['Ara / NPU / ISP / 搬运器','GB 适配 / 仲裁 / bank'],fill='#FFFFFF',dashed=True)
    f.box('gb',1060,780,300,150,'Global Buffer',['独立 SRAM','工作区 / 双缓冲'],fill='gb')
    f.box('mover',1450,780,300,150,'DDR–GB 搬运器',['显式搬入 / 写回','独立于计算访问'],fill='memory',dashed=True)
    f.box('entry',1820,775,240,180,'设备一致性入口',['请求准入 / 完成','不分配 LLC 行'],fill='agent',dashed=True)
    f.box('arb',2130,400,200,580,'合流 / 仲裁',['读写调度','在途跟踪','共享 DDR 带宽'],fill='#FFFFFF')
    f.box('ddr',2110,1150,250,140,'PHY / DDR',['外部主存'],fill='memory')
    f.box('coord',600,1140,1150,150,'一致性协调（候选职责）',
          ['逐行排序 / 副本与写权限 / 冲突访问',
           '汇合探测响应、失效确认、在途状态与完成事件'],fill='agent',dashed=True)
    # Normal CPU/Ara memory requests and returns.
    f.arrow('cpu-xbar',[(470,275),(1040,275)],both=True,start='cva6',end='xbar')
    f.text(700,258,'标量内存访问',24,color=C['data'])
    f.arrow('cpu-ara-order',[(170,410),(170,490)],'control',both=True,start='cva6',end='ara')
    f.text(195,455,'pending / barrier',23,color=C['control'])
    f.arrow('ara-invalidate',[(465,490),(465,450),(390,450),(390,410)],'control',both=True,start='filter',end='cva6')
    f.text(410,435,'写失效',23,color=C['control'])
    f.arrow('ara-filter',[(290,545),(350,545)],both=True,start='ara',end='filter')
    f.arrow('filter-split',[(580,545),(650,545)],both=True,start='filter',end='split')
    f.arrow('split-width',[(900,545),(1040,545)],both=True,start='split',end='width')
    f.arrow('width-xbar',[(1170,480),(1170,340)],both=True,start='width',end='xbar')
    f.arrow('xbar-atomics',[(1340,275),(1430,275)],both=True,start='xbar',end='atomics')
    f.arrow('atomics-llc',[(1580,340),(1580,445)],both=True,start='atomics',end='llc')
    f.arrow('llc-ddr',[(1730,520),(2130,520)],both=True,start='llc',end='arb')
    f.text(1805,497,'回填 / 写回 / 透传',24,color=C['data'])
    # All GB users enter the shared proxy; the mover has its own DDR port.
    f.arrow('ara-proxy',[(775,600),(775,770)],'local',both=True,start='split',end='proxy')
    f.text(795,685,'GB 地址分支',24,color=C['local'])
    f.arrow('npu-proxy',[(340,815),(630,815)],'local',both=True,start='npu',end='proxy')
    f.arrow('isp-proxy',[(340,950),(500,950),(500,910),(630,910)],'local',both=True,start='isp',end='proxy')
    f.arrow('proxy-gb',[(930,855),(1060,855)],'local',both=True,start='proxy',end='gb')
    f.arrow('mover-proxy',[(1600,930),(1600,990),(820,990),(820,960)],'local',both=True,start='mover',end='proxy')
    f.text(1070,975,'搬运器的 GB 端',23,color=C['local'])
    f.arrow('mover-entry',[(1750,855),(1820,855)],both=True,start='mover',end='entry')
    f.arrow('frame-entry',[(205,1010),(205,1030),(1880,1030),(1880,955)],both=True,start='isp',end='entry')
    f.text(970,1058,'图像帧写入：独立设备事务',23,color=C['data'])
    f.arrow('entry-ddr',[(2060,855),(2130,855)],both=True,start='entry',end='arb')
    f.arrow('controller-ddr',[(2230,980),(2230,1150)],both=True,start='arb',end='ddr')
    f.arrow('cache-supply',[(1680,595),(1680,670),(1940,670),(1940,775)],start='llc',end='entry')
    f.text(1810,650,'缓存直接供数（候选）',23,color=C['data'])
    # Logical coherence interfaces also cover buffered writes and atomic observers.
    f.arrow('probe-cpu',[(650,1140),(650,1080),(25,1080),(25,370),(70,370)],'control',both=True,start='coord',end='cva6')
    f.text(75,1064,'L1D / 写缓冲探测与排空',23,color=C['control'])
    f.arrow('probe-atomics',[(750,1140),(750,1100),(610,1100),(610,390),(1510,390),(1510,340)],'control',both=True,start='coord',end='atomics')
    f.text(790,420,'原子冲突协调',23,color=C['control'])
    f.arrow('probe-llc',[(1600,1140),(1600,1080),(1780,1080),(1780,580),(1730,580)],'control',both=True,start='coord',end='llc')
    f.text(1440,1064,'LLC 探测 / 确认',23,color=C['control'])
    f.arrow('entry-coordination',[(1680,1140),(1680,1110),(1980,1110),(1980,955)],'control',both=True,start='coord',end='entry')
    f.arrow('ddr-inflight',[(1750,1230),(2040,1230),(2040,1080),(2200,1080),(2200,980)],'control',both=True,start='coord',end='arb')
    f.text(1775,1210,'DDR 在途协调',23,color=C['control'])
    f.text(50,1330,'蓝灰：AXI / 数据返回    绿：GB 本地读写    紫：一致性接口    跳线处交叉而无连接；双向线合并请求与返回。',23)
    return f


def read_to_gb():
    f = Figure('read-to-gb','DDR 地址数据搬入 GB：最新版本从哪里来',
               '先发布输入并协调目标行，再由 DDR 或持有最新数据的缓存供数')
    rows = [
        (150,'A  DDR 已最新，无冲突在途事务',
         [('DDR',['最新版本可读'],'memory'),('设备一致性入口',['确认 DDR 版本已最新'],'agent'),('搬运器',['接收本次读取结果'],'memory'),('GB（经共享代理）',['写入后发布 ready'],'gb')],
         'DDR 已保存最新版本，L1D / LLC 的干净副本可以继续使用。'),
        (435,'B  LLC 持有最新脏数据',
         [('LLC 脏行',['比 DDR 更新'],'memory'),('设备一致性入口',['取得缓存数据'],'agent'),('搬运器',['接收最新版本'],'memory'),('GB（经共享代理）',['保存本次读取版本'],'gb')],
         '缓存可直接供数（候选）；采用 DDR 供数路径时，先 clean 到 DDR 再读取。'),
        (720,'C  CPU 有按顺序必须先完成的写',
         [('CPU 写缓冲',['建立发布顺序 / 排空'],'cpu'),('LLC / 共享点',['接收已排序的更新'],'memory'),('协调后搬运',['等待先行写可见'],'agent'),('GB（经共享代理）',['数据完整后才 ready'],'gb')],
         'CPU 先发布输入；协调点等待相关写完成，并处理同址回填与替换。')]
    xs, widths = [70,570,1070,1550],[380,380,350,290]
    for i,(y,title,boxes,note) in enumerate(rows):
        f.rect(f'row-{i}',40,y,1840,250,'#F7F9FA')
        f.text(65,y+40,title,27,bold=True)
        for j,(label,lines,color) in enumerate(boxes):
            f.box(f'r{i}-{j}',xs[j],y+72,widths[j],110,label,lines,fill=color)
        for j in range(3):
            f.arrow(f'r{i}-flow-{j}',[(xs[j]+widths[j],y+127),(xs[j+1],y+127)],'local' if j==2 else 'data',start=f'r{i}-{j}',end=f'r{i}-{j+1}')
        f.text(70,y+222,note,24,color=C['muted'])
    f.text(55,1030,'GB 保存本次搬入的数据版本；后续计算需要更新后的源数据时，重新搬运。',25)
    return f


def write_to_ddr():
    f=Figure('write-to-ddr','GB 数据写入 DDR：先协调，再发布新版本',
             '完整覆盖与部分更新都需处理在途冲突、失效确认及任务完成；下图为逻辑阶段')
    xs=[60,430,800,1170,1540]; width=300
    f.rect('full-panel',40,150,1840,350,'#F7F9FA')
    f.text(65,194,'A  完整覆盖所有相关一致性粒度',28,bold=True)
    full=[('GB 数据（经代理）',['全行备妥','全部字节有效'],'gb'),('目标行协调',['排序在途访问','取得本次写权限'],'agent'),
          ('L1D / LLC',['失效并确认','完整覆盖可省回写'],'memory'),('DDR 写入',['写入完整新行','保持约定访问次序'],'memory'),('完成 / 释放',['达到约定可见点','再发布任务状态'],'agent')]
    for j,(title,lines,color) in enumerate(full):
        f.box(f'full-{j}',xs[j],235,width,150,title,lines,fill=color)
    for j in range(4):
        f.arrow(f'full-flow-{j}',[(xs[j]+width,310),(xs[j+1],310)],'control',start=f'full-{j}',end=f'full-{j+1}')
    f.text(70,443,'“完整”按实际缓存粒度判断：满 WSTRB 的一个 beat，可能仍只覆盖缓存行的一部分。',25)
    f.rect('partial-panel',40,545,1840,435,'#F7F9FA')
    f.text(65,589,'B  部分行更新：先保护未覆盖字节的最新值',28,bold=True)
    partial=[('GB 数据（经代理）',['地址 / 长度','字节有效掩码'],'gb'),('目标行协调',['安排冲突访问次序','协调回填 / 替换'],'agent'),
             ('L1D / LLC',['clean 或取数暂存','失效旧副本并确认'],'memory'),('DDR 更新',['按 WSTRB 更新','或写入已合并新行'],'memory'),('完成 / 释放',['等待写入与确认','再发布任务状态'],'agent')]
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
    f.text(1515,850,'保留 A / C / D',25)
    f.text(70,934,'出错时记录部分完成范围，暂停复用缓冲；排空迟到事务或受控复位后恢复。',25)
    f.text(55,1030,'需要整帧一致视图时，用版本、所有权或双缓冲组织跨行数据交接。',25)
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
