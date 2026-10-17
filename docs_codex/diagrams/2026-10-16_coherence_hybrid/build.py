#!/usr/bin/env python3
"""Software-directed cache maintenance; preserve the approved industrial topology."""
import argparse
import importlib.util
import json
from pathlib import Path

D = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load('coherence_base', D.parent/'2026-10-16_cache_coherence/build_figures.py')
compare = load('coherence_compare', D.parent/'2026-10-16_coherence_comparison/build.py')
Figure, C = base.Figure, base.C


def replace(f, mapping):
    for old, new in mapping.items():
        assert any(old in s for s in f.parts), old
        f.parts = [s.replace(old, new) for s in f.parts]
    return f


def system():
    # base.system() reads only the approved 2026-10-12 industrial reference.
    return replace(base.system(), {
        '缓存一致性协调（候选）': '范围维护引擎（规划）',
        '行状态 / 写权限 / 在途事务 / 探测与完成确认': '软件触发 / L1D 与 LLC 维护 / 搬运准入 / 完成确认',
        'L1D / 写缓冲：探测与排空': '软件请求 / L1D 排空与失效',
        '原子冲突协调': '原子域评审',
        'LLC 探测 / 失效确认': 'LLC 范围清理 / 失效确认',
        'S1 请求准入 / 完成': 'S1 维护后准入 / 完成',
        'S2 请求准入 / 完成': 'S2 维护后准入 / 完成',
        '在途 / 完成': '跨口可见 / 完成',
        '缓存一致性控制（新增）': '软件交接与硬件维护（规划）',
    })


def ownership():
    f = Figure('ownership', '软件交接、硬件维护：一次推理的数据生命周期',
               '按缓冲区或计算分块同步；交接范围由软件保持所有权，CPU 可并行处理其他缓冲区。', 2400, 1350)
    f.autojump = True
    rows = [
        (140, '① 提交前：软件交出 DDR 输入与输出范围', 'cpu', [
            ('软件提交', ['地址 / 长度 / 方向', '确认各生产者完成']),
            ('L1D / 写缓冲', ['排空相关旧写', '输出失效 / 回填协调']),
            ('LLC 范围维护', ['输入：clean', '输出：clean + invalidate']),
            ('DDR 共享点', ['确认写回跨端口可见', '汇合缓存维护确认']),
            ('允许启动', ['返回维护完成', '软件发布 DMA 任务']),
        ], '输入的干净副本可保留；输出预清理保护未覆盖字节，预失效清除旧副本。'),
        (510, '② 设备持有期间：DDR 与 GB 显式搬运', 'gb', [
            ('DDR → GB', ['搬运器读取输入', '经共享数据代理写 GB']),
            ('GB ready', ['数据完整后交给', 'NPU / Ara 消费']),
            ('计算与分块复用', ['独立 SRAM 保存', '当前任务的数据']),
            ('GB → DDR', ['共享代理 → 搬运器', '按 WSTRB 更新输出']),
            ('设备完成', ['DDR 跨口可见', '返回任务身份与状态']),
        ], 'CPU / Ara 的 DDR 冲突访问由任务协议限制；GB 内部交接由其独立的分块调度负责。'),
        (880, '③ 消费前：硬件清除旧读副本，软件收回输出', 'agent', [
            ('软件等待完成', ['核对任务与错误', '请求输出范围同步']),
            ('处理旧回填', ['排空 / 作废旧响应', '保护失效过程']),
            ('L1D + LLC', ['输出 invalidate', '收齐实际完成确认']),
            ('交还所有权', ['建立完成到读取顺序', '输出可由 CPU 访问']),
            ('消费 / 复用', ['CPU 重新加载结果', '最后消费者释放缓冲']),
        ], '超时或写错误时保留缓冲区；确认迟到事务排空或受控恢复完成后，再允许复用。'),
    ]
    xs = [60, 525, 990, 1455, 1920]
    for i, (y, heading, color, boxes, note) in enumerate(rows):
        f.rect(f'panel{i}', 35, y, 2330, 310, '#F7F9FA')
        f.text(60, y+47, heading, 30, bold=True)
        for j, (title, lines) in enumerate(boxes):
            f.box(f'r{i}b{j}', xs[j], y+85, 400, 140, title, lines, fill=color)
            if j:
                f.arrow(f'r{i}e{j}', [(xs[j]-65,y+155),(xs[j],y+155)],
                        'local' if i==1 else 'control', start=f'r{i}b{j-1}', end=f'r{i}b{j}')
        f.text(65,y+275,note,26)
        if i<2:
            f.arrow(f'next{i}', [(2320,y+155),(2345,y+155),(2345,y+340),
                                (45,y+340),(45,y+525),(60,y+525)], 'control',
                    start=f'r{i}b4', end=f'r{i+1}b0')
    f.text(55,1260,'紫色箭头：阶段顺序与完成依赖    绿色箭头：设备搬运与计算阶段    维护动作以目标物理范围为单位',27)
    f.text(55,1310,'仅整模型前后交接时，同步集中在推理两端；CPU 与设备交替处理分块时，同步放在实际交接点。',27)
    return f


def data_paths():
    f = compare.candidate()
    f.name = 'data-paths'
    return replace(f, {
        'E：同属 I/O 一致性的两种供数实现': '经 DDR 与缓存直供：数据路径和代价',
        'E1  先清理到 DDR，再搬运': '本方案：先清理到 DDR，再搬运',
        'E2  缓存直接供数（待评审路径）': '比较项：缓存直供（本方案不采用）',
        '一致性协调点': '缓存维护与协调',
        '逐行准入、探测、冲突排序及完成确认': '软件交接 / 缓存维护 / 搬运准入与完成',
        '① 受保护的探测与访问': '① 交接与缓存维护',
        '两种实现均保持：设备不分配 LLC 行，GB 按任务管理。': '设备不分配 LLC 行；GB 按任务显式管理。',
        '设备写入时，两种实现共同需要的逻辑步骤': '本方案的输出交接：先保护旧字节，最后清除旧读副本',
        '准入与冲突排序': '交接目标范围',
        '保护未覆盖字节': '写前清理与失效',
        '旧副本失效确认': 'GB → DDR',
        '提交新数据': '写后失效确认',
        '发布完成': 'CPU 获取结果',
        'E1 / E2 均须保护从探测到访问完成的过程；整块传输期间，其他地址仍可并发访问。': '脏行经 DDR 需写回后重读；缓存直供减少当次 DDR 往返，同时增加片上数据响应通路。',
        '边界维护方案 B 则在交接时维护整个范围，并在传输期间限制该范围的冲突访问。': '当前规划采用左侧路径；右侧用于成本比较。软件保持交接范围的所有权，硬件完成维护。',
        '虚线框：项目候选职责': '虚线框：待实现的维护职责',
    })


def handover():
    f = compare.comparison('handover', '① 交接方式：软件发起，缓存维护由谁执行', [
        ('A','软件维护 + 非一致性 DMA','软件维护全层次；硬件直接访问内存'),
        ('B','软硬件协同范围维护','软件触发批量维护；传输期保持范围所有权')])
    replace(f, {'硬件排空、维护并确认；传输期范围排他':'软件交接所有权；硬件排空、维护并确认',
                '项目低成本候选：以块 / 任务为边界':'本项目方向：按缓冲区 / 分块批量同步'})
    f.box('Bdriver',1160,240,170,55,'驱动',fill='agent')
    f.arrow('Bsoftware-submit',[(1245,295),(1245,525),(1445,525),(1445,560)],
            'control',both=True,start='Bdriver',end='Bfabric')
    return f


def agents():
    f = compare.comparison('agent-types', '③ 分配策略与设备缓存：区分两个分类维度', [
        ('E','I/O 一致性 · 不分配 LLC','逐事务协调机制；供文献比较'),
        ('F','完整缓存代理一致性','设备持有可探测的私有缓存；本项目不采用')])
    return replace(f, {
        '项目优先评估：逐行排序、每笔事务协调':'逐事务协调；设备不分配 LLC 行',
        '控制访问缓存；供数路径见下一张详图':'本项目沿用旁路拓扑，采用软件范围交接',
    })


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);a=ap.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=False)
    fs=[system(),ownership(),data_paths(),handover(),
        compare.comparison('coverage','② 协调范围：只到 LLC，还是覆盖 CPU 私有缓存',[
            ('C','LLC-coherent DMA','LLC 硬件协调；CPU 私有缓存仍需软件维护'),
            ('D','I/O 一致性 · 分配缓存行','CPU 缓存由硬件协调；允许设备分配 LLC')]),agents()]
    (a.out_dir/'layout.json').write_text(json.dumps([f.save(a.out_dir) for f in fs],ensure_ascii=False,indent=2)+'\n')
    print('Generated',len(fs),'figures')


if __name__=='__main__':main()
