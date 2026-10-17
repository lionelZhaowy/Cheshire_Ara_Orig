#!/usr/bin/env python3
"""Aligned mechanism comparisons; independent of the project's full SoC diagram."""
import argparse
import importlib.util
import json
from pathlib import Path

D = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('drawing', D.parent/'2026-10-16_cache_coherence/build_figures.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
Figure, C = mod.Figure, mod.C


def panel(f, ox, oy, code, title, tag):
    def box(key, x, y, w, h, title, lines=(), fill='memory', dashed=False):
        f.box(code+key, ox+x, oy+y, w, h, title, lines, fill, dashed)
    def arrow(key, pts, kind='data', both=True):
        f.arrow(code+key, [(ox+x,oy+y) for x,y in pts], kind, both)
    def text(x,y,t,size=23,color=None,bold=False):
        f.text(ox+x,oy+y,t,size,color=color,bold=bold)
    f.rect(code+'panel',ox,oy,800,740,'#F5FAF7' if code=='E' else '#FAFBFC')
    text(25,37,code+'  '+title,30,bold=True)
    text(25,76,tag,23,C['local'] if code=='E' else C['muted'])
    box('cpu',60,110,200,55,'CPU',fill='cpu')
    box('private',60,220,200,85,'L1 / L2',('写缓冲',),fill='cpu')
    box('llc',60,430,200,85,'LLC',('系统侧缓存',))
    box('ddr',60,580,680,60,'内存接入 / DDR',fill='agent')
    box('device',520,110,220,95,'加速器',('独立本地 SRAM',),fill='gb')
    box('dma',520,245,220,55,'DMA')
    arrow('cpu-private',[(160,165),(160,220)])
    arrow('private-llc',[(160,305),(160,430)])
    arrow('llc-ddr',[(160,515),(160,580)])
    arrow('local-dma',[(630,205),(630,245)],'local')
    if code=='F':
        box('devcache',520,340,220,55,'设备私有缓存',fill='cpu')
        arrow('dma-cache',[(630,300),(630,340)],'local')
        arrow('cache-fabric',[(630,395),(630,430)],'local')
    else:
        arrow('dma-fabric',[(630,300),(630,430)],'local')
    names={'A':('普通互连','软件交接'), 'B':('维护 / 准入引擎','搬运边界'),
           'C':('LLC 接入','局部协调'), 'D':('一致性协调点','含缓存分配'),
           'E':('一致性协调点','设备不分配 LLC'), 'F':('一致性互连','多缓存代理')}
    box('fabric',440,430,300,85,*[names[code][0]],lines=(names[code][1],),fill='interconnect',dashed=code in ['B','E'])
    if code in ['A','B','E']:
        arrow('device-ddr',[(590,515),(590,580)],'local')
    else:
        arrow('device-llc',[(440,457),(260,457)],'local')
    if code in ['A','C']:
        box('driver',305,110,170,55,'驱动',fill='agent')
        arrow('sw-private',[(305,137),(285,137),(285,248),(260,248)],'control')
        if code=='A':
            arrow('sw-llc',[(390,165),(390,490),(260,490)],'control')
    if code in ['B','D','E','F']:
        arrow('probe-private',[(440,445),(325,445),(325,270),(260,270)],'control')
        arrow('probe-llc',[(440,492),(260,492)],'control')
    if code=='F':
        arrow('probe-devcache',[(740,490),(775,490),(775,368),(740,368)],'control')
    notes={
      'A':['交接前后由软件 clean / invalidate','设备直访 DDR；交接区限制冲突访问'],
      'B':['硬件排空、维护并确认；传输期范围排他','项目低成本候选：以块 / 任务为边界'],
      'C':['CPU 私有缓存由软件维护','LLC 可供数；设备访问经过 LLC'],
      'D':['硬件协调 CPU 私有缓存和 LLC','设备可分配 LLC 行，利用片上复用'],
      'E':['项目优先评估：逐行排序、每笔事务协调','控制访问缓存；供数路径见下一张详图'],
      'F':['设备私有缓存也接收探测并返回数据','本地 SRAM 仍显式管理；分配策略另设']}
    for i,line in enumerate(notes[code]):text(25,683+i*32,line,23)


def comparison(name,title,panels):
    f=Figure(name,title,'同一布局：左侧为 CPU 缓存层次，右侧为设备；沿绿线比较设备接入位置。',1680,945)
    f.autojump=True
    for x,args in zip([25,855],panels):panel(f,x,130,*args)
    f.text(30,916,'蓝灰：CPU 常规访存    绿色：设备访问 / 数据    紫色：维护 / 探测与确认（双向合并）',23)
    return f


def candidate():
    f=Figure('recommended-data','E：同属 I/O 一致性的两种供数实现','比较场景：CPU 的最新数据在 LLC 脏行中，DMA 将该行搬入独立 GB。',2400,1350)
    f.autojump=True
    for side,ox in [('clean',50),('supply',1230)]:
        oy=145
        def box(k,x,y,w,h,t,lines=(),fill='memory',dashed=False):
            f.box(side+k,ox+x,oy+y,w,h,t,lines,fill,dashed)
        def edge(k,pts,kind='data',both=False):
            f.arrow(side+k,[(ox+x,oy+y) for x,y in pts],kind,both)
        def txt(x,y,t,s=28,c=None):f.text(ox+x,oy+y,t,s,color=c)
        f.rect(side+'panel',ox,oy,1120,790,'#FAFBFC')
        txt(25,48,'E1  先清理到 DDR，再搬运' if side=='clean' else 'E2  缓存直接供数（待评审路径）',34)
        box('private',40,150,240,90,'L1D / 写缓冲',fill='cpu')
        box('llc',40,340,240,100,'LLC',('持有最新脏行',))
        box('coord',400,150,600,90,'一致性协调点',('逐行准入、探测、冲突排序及完成确认',),'interconnect',True)
        box('ddr',40,580,240,90,'DDR',fill='agent')
        box('dma',400,580,240,90,'搬运器 / DMA')
        box('proxy',760,580,240,90,'共享数据代理')
        box('gb',760,340,240,100,'GB',('独立 SRAM',),'gb')
        edge('private-llc',[(160,240),(160,340)],both=True)
        edge('llc-ddr',[(160,440),(160,580)],both=True)
        edge('probe-private',[(400,175),(280,175)],'control',True)
        edge('probe-llc',[(400,215),(320,215),(320,375),(280,375)],'control',True)
        edge('admit',[(600,240),(600,580)],'control',True)
        if side=='clean':
            edge('clean-data',[(220,440),(220,580)],'local')
            edge('ddr-data',[(280,625),(400,625)],'local')
            txt(285,492,'② clean',27,C['local'])
            txt(285,531,'等待 DDR 可见',27,C['local'])
        else:
            edge('ddr-fallback',[(280,650),(400,650)],both=True)
            edge('cache-data',[(280,410),(360,410),(360,520),(520,520),(520,580)],'local')
            txt(380,486,'② 最新数据',27,C['local'])
            txt(25,726,'DDR 可暂时保留旧值；由 LLC 提供本次读数据。',26)
        edge('dma-proxy',[(640,625),(760,625)],'local')
        edge('proxy-gb',[(880,580),(880,440)],'local')
        txt(650,298,'① 受保护的探测与访问',27,C['control'])
        txt(910,504,'③ 写入 GB',27,C['local'])
        if side=='clean':txt(25,726,'保留 DDR 供数路径；脏数据经历写回与再次读取。',26)
        txt(25,767,'两种实现均保持：设备不分配 LLC 行，GB 按任务管理。',26)
    f.text(55,996,'设备写入时，两种实现共同需要的逻辑步骤',32,bold=True)
    labels=['准入与冲突排序','保护未覆盖字节','旧副本失效确认','提交新数据','发布完成']
    for i,label in enumerate(labels):
        x=55+i*465
        f.box('write'+str(i),x,1040,405,90,label,fill='agent' if i!=3 else 'memory')
        if i: f.arrow('write-seq'+str(i),[(x-60,1085),(x,1085)],'control')
    f.text(55,1192,'E1 / E2 均须保护从探测到访问完成的过程；整块传输期间，其他地址仍可并发访问。',30)
    f.text(55,1240,'边界维护方案 B 则在交接时维护整个范围，并在传输期间限制该范围的冲突访问。',30)
    f.text(55,1300,'蓝灰：常规访存 / 后备路径    绿色：本场景的数据    紫色：控制与确认    虚线框：项目候选职责',25)
    return f


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
    a.out_dir.mkdir(exist_ok=False,parents=True)
    fs=[comparison('handover','① 交接方式：谁在什么时候维护缓存',[
          ('A','软件维护 + 非一致性 DMA','软件维护全层次；硬件直接访问内存'),
          ('B','搬运边界硬件维护','由硬件执行范围维护；传输期间范围排他')]),
        comparison('coverage','② 协调范围：只到 LLC，还是覆盖 CPU 私有缓存',[
          ('C','LLC-coherent DMA','LLC 硬件协调；CPU 私有缓存仍需软件维护'),
          ('D','I/O 一致性 · 分配缓存行','CPU 缓存由硬件协调；允许设备分配 LLC')]),
        comparison('recommended','③ 项目建议在哪里：I/O 一致性的一种分配策略',[
          ('E','I/O 一致性 · 不分配 LLC','项目优先评估；与 D 同类，改变分配策略'),
          ('F','完整缓存代理一致性','设备新增同地址私有缓存，参与探测和权限转移')]),candidate()]
    (a.out_dir/'layout.json').write_text(json.dumps([f.save(a.out_dir) for f in fs],ensure_ascii=False,indent=2)+'\n')
    print('Generated',len(fs),'figures')

if __name__=='__main__':main()
