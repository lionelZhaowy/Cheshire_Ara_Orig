#!/usr/bin/env python3
"""Generate the three L01 coherence figures; write into a new output directory."""
import argparse
import json
import xml.etree.ElementTree as ET
from copy import deepcopy
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
    """Extend the sole approved industrial base; keep every original geometry."""
    root_dir = Path(__file__).resolve().parents[3]
    base_dir = root_dir / 'docs_codex/diagrams/2026-10-12_industrial_redraw'
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('',ns)
    svg = ET.parse(base_dir/'ddr_interconnect.svg').getroot()
    source_layout = json.loads((base_dir/'ddr_interconnect.layout.json').read_text())
    elements = {e.get('id'):e for e in svg.iter() if e.get('id')}
    # Three local labels clarify the existing blocks; all coordinates stay fixed.
    for key,value in {'o8':'L1D / 写缓冲','o30':'共享数据代理','o79':'WB 缓存 / 片上 SPM'}.items():
        elements[key].text = value
    owners = {t['id']:t['owner'] for t in source_layout['texts']}
    for node in svg.findall(f'{{{ns}}}text'):
        node.set('font-family','WenQuanYi Zen Hei')
        owner = owners.get(node.get('id'))
        if owner: node.set('data-owner',owner)
    defs = svg.find(f'{{{ns}}}defs')
    marker = deepcopy(elements['a765489']);marker.set('id','control');defs.append(marker)
    f = Figure.__new__(Figure)
    f.name = 'system';f.canvas = source_layout['canvas'];f.autojump = True
    f.boxes = {key:dict(zip(['x','y','width','height'],values))
               for key,values in source_layout['blocks'].items() if key!='background'}
    f.arrows = []
    endpoints = {
        'ara-filter':('ara','filter'),'filter-split':('filter','split'),
        'split-width':('split','width'),'npu-router':('npu','router'),
        'router-gb':('router','gb'),'mover-router':('mover','router'),
        'ara-gb':('split','router'),'isp-gb':('isp','router'),
        'pixel0':('lvds','cdc'),'pixel1':('cdc','isp'),
        'pixel2':('isp','select'),'pixel3':('select','frame'),
        'cpu-xbar':('cpu','xbar'),'ara-xbar':('width','xbar'),
        'xbar-atomics':('xbar','atomics'),'atomics-llc':('atomics','llc'),
        'llc-ddr':('llc','ddr-port0'),'mover-ddr':('mover','ddr-port1'),
        'frame-ddr':('frame','ddr-port2'),'join0':('ddr-port0',''),
        'join1':('ddr-port1',''),'join2':('ddr-port2',''),
        'qos-in':('','qos'),'qos-core':('qos','scheduler'),
        'ddr-phy':('scheduler','phy-ddr')}
    for node in svg:
        tag=node.tag.rsplit('}',1)[-1]
        if tag=='line':
            points=[[float(node.get('x1')),float(node.get('y1'))],
                    [float(node.get('x2')),float(node.get('y2'))]]
        elif tag=='polyline':
            points=[list(map(float,p.split(','))) for p in node.get('points').split()]
        elif tag=='path' and node.get('id')=='isp-gb':
            points=[[2285,370],[2285,280],[1400,280],[1400,305]]
        else: continue
        source,target=endpoints.get(node.get('id'),('',''))
        f.arrows.append(dict(id=node.get('id'),points=points,source=source,target=target,
                             kind='original',bidirectional='marker-start' in node.attrib,
                             arrowed='marker-end' in node.attrib,jump=tag=='path'))
    f.parts=[ET.tostring(svg,encoding='unicode').removesuffix('</svg>')]
    # Use the existing clear band between the upper subsystems and the lower buses.
    f.box('coh-coordinator',960,650,850,125,'缓存一致性协调（候选）',
          ['行状态 / 写权限 / 在途事务 / 探测与完成确认'],fill='agent',dashed=True)
    f.arrow('coh-cpu',[(960,680),(925,680),(925,160),(200,160),(200,290)],
            'control',both=True,start='coh-coordinator',end='cpu')
    f.text(250,150,'L1D / 写缓冲：探测与排空',23,color=C['control'])
    f.arrow('coh-atomics',[(960,735),(40,735),(40,1240),(530,1240),(530,1185)],
            'control',both=True,start='coh-coordinator',end='atomics')
    f.text(70,765,'原子冲突协调',23,color=C['control'])
    f.arrow('coh-llc',[(1340,775),(1340,1220),(925,1220),(925,1185)],
            'control',both=True,start='coh-coordinator',end='llc')
    f.text(1000,1250,'LLC 探测 / 失效确认',23,color=C['control'])
    f.arrow('coh-s1',[(1810,700),(2050,700),(2050,980),(2010,980)],
            'control',both=True,start='coh-coordinator',end='ddr-port1')
    f.text(2065,685,'S1 请求准入 / 完成',23,color=C['control'])
    f.arrow('coh-s2',[(1810,745),(2100,745),(2100,900),(2420,900),(2420,980),(2400,980)],
            'control',both=True,start='coh-coordinator',end='ddr-port2')
    f.text(2435,895,'S2 请求准入 / 完成',23,color=C['control'])
    f.arrow('coh-ddr',[(1730,775),(1730,1140)],
            'control',both=True,start='coh-coordinator',end='qos')
    f.text(1750,1110,'在途 / 完成',23,color=C['control'])
    f.arrow('coh-legend',[(1720,1530),(1790,1530)],'control')
    f.text(1805,1538,'缓存一致性控制（新增）',22,color=C['control'])
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
    print(json.dumps({'figures':len(figs),'arrows':sum(e.get('arrowed',True) for f in figs for e in f.arrows)},ensure_ascii=False))


if __name__=='__main__':
    main()
