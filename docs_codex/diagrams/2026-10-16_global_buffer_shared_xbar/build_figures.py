#!/usr/bin/env python3
"""Build the selected two-lane CPU/Ara shared-Xbar GB topology (L01)."""
import argparse
from html import escape
import json
from pathlib import Path

W, H = 2560, 1440
C = dict(ink='#29292D', muted='#606773', data='#314D66', local='#187C78',
         control='#765489', irq='#A05255', host='#B96043', cpu='#F1D7D9',
         memory='#D8E8F4', gb='#D9EEE8', xbar='#F5E1C9', regs='#E8DFED')


class Figure:
    def __init__(self, direct):
        self.name = 'shared-xbar'
        self.boxes, self.arrows = {}, []
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
                      '<title>CPU 与 Global Buffer 的连接方案</title>', '<defs>']
        for k in ['data', 'local', 'control', 'irq', 'host']:
            self.parts.append(f'<marker id="{k}" markerUnits="strokeWidth" markerWidth="3" markerHeight="3" viewBox="0 0 3 3" refX="3" refY="1.5" orient="auto-start-reverse"><polygon points="0,0 3,1.5 0,3" fill="{C[k]}"/></marker>')
        self.parts += ['</defs>', f'<rect id="background" x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF" stroke="none"/>']
        self.text(60, 63, '已选拓扑：CPU / Ara 共用主 Xbar 的 GB 出口', 42, bold=True)
        self.text(60, 112, 'Ara 保持 2 lanes / AXI64；不新增 Ara 直达 GB 支路。拓扑已确认，硬件尚未实施。', 28, color=C['muted'])

    def text(self, x, y, value, size=28, color=None, anchor='start', bold=False, owner=''):
        owner_attr = f' data-owner="{owner}"' if owner else ''
        self.parts.append(f'<text x="{x}" y="{y}" font-family="WenQuanYi Zen Hei" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color or C["ink"]}"{owner_attr}>{escape(value)}</text>')

    def rect(self, key, x, y, w, h, fill, dashed=False, color=None):
        dash = ' stroke-dasharray="10 7"' if dashed else ''
        self.parts.append(f'<rect id="{key}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{C.get(fill,fill)}" stroke="{color or C["ink"]}" stroke-width="1.8"{dash}/>')
        self.boxes[key] = dict(x=x, y=y, width=w, height=h)

    def box(self, key, x, y, w, h, title, lines=(), fill='memory', dashed=False, color=None):
        self.rect(key, x, y, w, h, fill, dashed, color)
        first = y+h/2-len(lines)*19+10
        self.text(x+w/2, first, title, 30, anchor='middle', bold=True, owner=key)
        for i, line in enumerate(lines):
            self.text(x+w/2, first+38*(i+1), line, 26, anchor='middle', owner=key)

    def arrow(self, key, points, source, target, kind='data', both=False, dashed=False):
        self.arrows.append(dict(id=key, points=points, source=source, target=target,
                                kind=kind, bidirectional=both, dashed=dashed))

    def render_arrows(self):
        """Later lines bridge earlier crossings with one continuous native path."""
        prior=[]
        for e in self.arrows:
            points=e['points']; d=[f'M {points[0][0]} {points[0][1]}']; jumps=[]
            for (x1,y1),(x2,y2) in zip(points,points[1:]):
                assert x1==x2 or y1==y2
                cross=[]
                for (a,b),(c,dv) in prior:
                    if y1==y2 and a==c and min(x1,x2)+10<a<max(x1,x2)-10 and min(b,dv)+1<y1<max(b,dv)-1:
                        cross.append(a)
                    if x1==x2 and b==dv and min(y1,y2)+10<b<max(y1,y2)-10 and min(a,c)+1<x1<max(a,c)-1:
                        cross.append(b)
                cross=sorted(set(cross), reverse=(x2<x1 or y2<y1))
                sign=1 if (x2>x1 or y2>y1) else -1
                for q in cross:
                    if y1==y2:
                        d.extend([f'L {q-sign*7} {y1}',f'Q {q} {y1-13} {q+sign*7} {y1}'])
                        jumps.append([q,y1])
                    else:
                        d.extend([f'L {x1} {q-sign*7}',f'Q {x1+13} {q} {x1} {q+sign*7}'])
                        jumps.append([x1,q])
                d.append(f'L {x2} {y2}')
            attrs=f'id="{e["id"]}" d="{" ".join(d)}" fill="none" stroke="{C[e["kind"]]}" stroke-width="{3.5 if e["kind"]=="host" else 2.8}" stroke-linejoin="miter" marker-end="url(#{e["kind"]})"'
            if e['bidirectional']: attrs+=f' marker-start="url(#{e["kind"]})"'
            if e['dashed']: attrs+=' stroke-dasharray="8 6"'
            self.parts.append(f'<path {attrs}/>')
            e['jumps']=jumps
            prior.extend(zip(points,points[1:]))

    def save(self, out):
        self.render_arrows()
        (out/(self.name+'.svg')).write_text('\n'.join(self.parts+['</svg>'])+'\n')
        return dict(name=self.name,canvas=[W,H],boxes=self.boxes,arrows=self.arrows)


def make(direct):
    f=Figure(direct)
    # Preserve the comparison figures' industrial layout; remove the Ara split.
    f.rect('host-domain',60,160,1510,430,'#F8ECEC')
    f.text(85,202,'CVA6 / Ara 计算与访存',30,bold=True)
    f.rect('accelerator-domain',1780,160,720,430,'#ECF2F7',dashed=True)
    f.text(1805,202,'NPU 与显式搬运（规划）',30,bold=True)
    f.rect('gb-domain',1780,620,720,520,'#EEF7F3',dashed=True)
    f.text(2135,661,'独立片上共享存储（规划）',28,bold=True,anchor='middle')

    f.box('cpu',110,240,300,150,'CVA6',['标量 load / store','GB 访问属性单独配置'],fill='cpu')
    f.box('ara',560,240,280,150,'Ara · 2 lanes',['单一 AXI64 出口'],fill='cpu')
    f.box('filter',940,240,260,150,'现有失效过滤',['关联 CVA6 L1D'])
    f.text(1280,292,'2 × 32 = 64-bit',28,color=C['data'])
    f.text(1280,337,'不增加 GB 分流',27,color=C['muted'])
    f.box('converter',700,430,400,120,'既有宽度转换器',['64 → 64：等宽直接透传'])
    f.box('interrupt',440,470,190,90,'外部中断',['PLIC / CLIC'],fill='regs')
    f.box('npu',1820,235,280,150,'NPU 计算',['GB 数据读写'],fill='cpu',dashed=True)
    f.box('mover',2180,235,280,150,'DDR ↔ GB 搬运器',['引擎实现待定'],dashed=True)
    f.box('device-regs',1820,480,640,80,'NPU / 搬运器控制与完成状态',fill='regs',dashed=True)
    f.box('xbar',110,690,1430,120,'主 AXI Xbar · 64-bit',['普通内存、寄存器与外部存储目标'],fill='xbar')
    f.box('arbiter',1810,680,650,150,'GB 多入口适配 / 仲裁 / bank 调度',['位宽、ID、字节选通；按需 CDC','逻辑入口数不等于 SRAM 物理端口数'],fill='gb',dashed=True)
    f.box('sram',1860,960,570,160,'GB SRAM',['独立物理存储 · 容量 / bank / 端口待定','CPU 可达时建议不缓存、不可执行'],fill='gb',dashed=True)
    f.box('regext',110,960,320,120,'Reg 扩展配置路径',['AXI → Reg → RegExt'],fill='regs')
    f.box('atomics',650,940,300,100,'现有原子适配',['普通内存路径'])
    f.box('llc',650,1130,300,120,'LLC / SPM',['预留 SPM 可作结果暂存'])
    f.box('merge',1050,1130,270,120,'DDR 合流边界',['端口 / 适配待定'],fill='xbar',dashed=True)
    f.box('ddr-controller',1420,1130,300,120,'Controller / PHY',['AXI4 接入'],dashed=True)
    f.box('ddr',1830,1190,280,100,'DDR',['外部主存'])
    if direct:
        f.box('host-port',1160,850,350,120,'CPU / Ara 共享 GB 出口',['AXI64 出口 / GB 适配'],fill='xbar',dashed=True,color=C['host'])
    else:
        f.text(1170,890,'CPU 标量端无 GB 数据出口',27,color=C['muted'])
        f.text(1170,932,'GB 窗口不在主 Xbar 上映射',25,color=C['muted'])

    f.arrow('cpu-memory',[(260,390),(260,690)],'cpu','xbar')
    f.text(280,449,'64-bit',27,color=C['data'])
    f.arrow('cpu-ara',[(410,285),(560,285)],'cpu','ara','control',both=True)
    f.text(485,264,'RVV',27,color=C['control'],anchor='middle')
    f.text(485,324,'指令 / 结果',22,color=C['control'],anchor='middle')
    f.arrow('ara-filter',[(840,320),(940,320)],'ara','filter')
    f.arrow('filter-invalidate',[(1070,240),(1070,217),(260,217),(260,240)],'filter','cpu','control')
    f.text(800,201,'L1D 失效请求',23,color=C['control'])
    f.text(1100,417,'64-bit',25,color=C['data'])
    f.arrow('filter-converter',[(1070,390),(1070,430)],'filter','converter')
    f.arrow('converter-xbar',[(900,550),(900,690)],'converter','xbar')
    f.text(920,579,'64-bit',25,color=C['data'])
    f.arrow('npu-gb',[(1820,310),(1770,310),(1770,650),(1920,650),(1920,680)],'npu','arbiter','local')
    f.arrow('mover-gb',[(2460,360),(2490,360),(2490,650),(2360,650),(2360,680)],'mover','arbiter','local')
    f.arrow('gb-sram',[(2135,830),(2135,960)],'arbiter','sram','local')
    f.text(2160,900,'bank 读写服务',27,color=C['local'])
    f.arrow('xbar-atomics',[(800,810),(800,940)],'xbar','atomics')
    f.text(820,884,'主存 / SPM',27,color=C['data'])
    f.arrow('atomics-llc',[(800,1040),(800,1130)],'atomics','llc')
    f.arrow('llc-ddr',[(950,1190),(1050,1190)],'llc','merge')
    f.arrow('merge-controller',[(1320,1190),(1420,1190)],'merge','ddr-controller')
    f.arrow('controller-ddr',[(1720,1190),(1770,1190),(1770,1240),(1830,1240)],'ddr-controller','ddr')
    f.arrow('mover-ddr',[(2460,280),(2520,280),(2520,1340),(1185,1340),(1185,1250)],'mover','merge')
    f.text(1740,1323,'搬运器 DDR 主口 · 绕过 LLC',27,color=C['data'])
    f.arrow('xbar-reg',[(260,810),(260,960)],'xbar','regext')
    f.text(280,905,'配置访问',27,color=C['control'])
    f.arrow('reg-config',[(110,1010),(40,1010),(40,650),(1740,650),(1740,520),(1820,520)],'regext','device-regs','control',dashed=True)
    f.text(1120,632,'RegExt 配置 / 状态访问',26,color=C['control'])
    f.arrow('regs-npu',[(1880,480),(1880,385)],'device-regs','npu','control',dashed=True)
    f.arrow('regs-mover',[(2230,480),(2230,385)],'device-regs','mover','control',dashed=True)
    f.arrow('device-irq',[(1820,545),(1710,545),(1710,600),(590,600),(590,560)],'device-regs','interrupt','irq',dashed=True)
    f.text(1120,585,'完成 / 错误 IRQ',26,color=C['irq'])
    f.arrow('irq-cpu',[(440,515),(80,515),(80,330),(110,330)],'interrupt','cpu','irq',dashed=True)
    if direct:
        f.arrow('xbar-host',[(1340,810),(1340,850)],'xbar','host-port','host')
        f.arrow('host-gb',[(1510,910),(1680,910),(1680,790),(1810,790)],'host-port','arbiter','host')
        f.text(1530,946,'CPU / Ara → GB',27,color=C['host'])

    f.text(60,1378,'蓝灰：普通访存    绿：GB 访存    紫：指令 / 配置    暗红：完成通知    橙：CPU / Ara 共享 GB 通路',26)
    f.text(60,1418,'箭头表示请求方向，存储响应省略；RVV 双向线含结果。跳线处不连接。虚线框标示尚未实施的规划部件。',25,color=C['muted'])
    return f


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',type=Path,required=True)
    args=p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=False)
    layouts=[make(True).save(args.out_dir)]
    (args.out_dir/'layout.json').write_text(json.dumps(layouts,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'figures':len(layouts),'arrows':[len(f['arrows']) for f in layouts]}))


if __name__=='__main__':
    main()
