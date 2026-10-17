#!/usr/bin/env python3
"""Build three narrative figures; preserve the approved industrial system layout."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
D = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'industrial_base', D.parent/'2026-10-16_cache_coherence/build_figures.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
Figure, C = base.Figure, base.C


def system():
    # This entry reads only 2026-10-12_industrial_redraw/ddr_interconnect.svg.
    f = base.system()
    replacements = {
        '缓存一致性协调（候选）': '范围维护引擎（规划）',
        '行状态 / 写权限 / 在途事务 / 探测与完成确认':
            '软件触发 / L1D 与 LLC 维护 / 搬运准入 / 完成确认',
        'L1D / 写缓冲：探测与排空': '软件请求 / L1D 排空与失效',
        '原子冲突协调': '原子域评审',
        'LLC 探测 / 失效确认': 'LLC 范围清理 / 失效确认',
        'S1 请求准入 / 完成': 'S1 维护后准入 / 完成',
        'S2 请求准入 / 完成': 'S2 维护后准入 / 完成',
        '在途 / 完成': '跨口可见 / 完成',
        '缓存一致性控制（新增）': '软件交接与硬件维护（规划）',
    }
    for old, new in replacements.items():
        assert any(old in p for p in f.parts), old
        f.parts = [p.replace(old, new) for p in f.parts]
    return f


def versions():
    f = Figure('versions', '缺少同步时，同一地址会出现不同数据版本',
               '三个独立场景：输入过期、输出旧副本、迟到脏写回。数值表示所示时刻的状态。', 2400, 1350)
    xs = [60, 525, 990, 1455, 1920]
    rows = [
        (145, '① 输入：CPU 写 x = 2，设备却搬到 x = 1', [
            ('CPU / L1D', ['L1D 阵列仍为 x = 1', 'CPU 读可前递到 2'], 'cpu'),
            ('写缓冲', ['待推进 x = 2', '下层尚未收到'], 'cpu'),
            ('WB LLC', ['当前仍为 x = 1', '收到新写后可持脏值 2'], 'memory'),
            ('DDR', ['x = 1', '设备可见的旧输入'], 'memory'),
            ('GB', ['搬入 x = 1', 'NPU 使用了旧输入'], 'gb'),
        ], '写缓冲排空之后，新值还可能只到达 WB LLC；输入 clean 继续把它推进 DDR。'),
        (510, '② 输出：设备已写 y = 9，CPU 仍命中 y = 0', [
            ('CPU / L1D', ['缓存副本 y = 0', 'CPU 读取命中旧值'], 'cpu'),
            ('写缓冲', ['此时为空', '没有待完成写'], 'cpu'),
            ('LLC', ['干净旧副本 y = 0', '下次回填也可能取旧值'], 'memory'),
            ('DDR', ['y = 9', '已收到设备结果'], 'memory'),
            ('GB', ['结果 y = 9', '设备向 DDR 搬出'], 'gb'),
        ], '输出交还 CPU 前，对 L1D 与 LLC 执行失效，并协调此前尚未完成的旧回填。'),
        (875, '③ 输出：设备先写 y = 9，LLC 的旧脏行随后覆盖它', [
            ('CPU / L1D', ['先前写过 y = 3', '此时 CPU 已停止访问'], 'cpu'),
            ('写缓冲', ['先前的写已推进', 'LLC 尚有脏数据'], 'cpu'),
            ('WB LLC', ['旧脏副本 y = 3', '稍后替换并写回'], 'memory'),
            ('DDR', ['y = 9 → y = 3', '设备结果被覆盖'], 'memory'),
            ('GB', ['结果 y = 9', '此前已完成搬出'], 'gb'),
        ], '输出写入前先排空旧写、clean + invalidate；写入后再失效旧读副本。'),
    ]
    for i, (y, title, boxes, note) in enumerate(rows):
        f.rect(f'panel{i}', 35, y, 2330, 320, '#F7F9FA')
        f.text(60, y+47, title, 30, bold=True)
        for j, (name, lines, color) in enumerate(boxes):
            f.box(f'r{i}b{j}', xs[j], y+90, 400, 150, name, lines, fill=color)
        f.text(60, y+287, note, 26)
    f.arrow('cpu-store', [(460,310),(525,310)], start='r0b0', end='r0b1')
    f.arrow('pending-store', [(925,310),(990,310)], start='r0b1', end='r0b2')
    f.parts[-1] = f.parts[-1].replace('stroke-width="2.8"', 'stroke-width="2.8" stroke-dasharray="7 5"')
    f.arrow('stale-input', [(1855,310),(1920,310)], 'local', start='r0b3', end='r0b4')
    f.arrow('output-write', [(1920,675),(1855,675)], 'local', start='r1b4', end='r1b3')
    f.arrow('late-old-write', [(1390,1040),(1455,1040)], start='r2b2', end='r2b3')
    f.arrow('earlier-device-write', [(1920,1040),(1855,1040)], 'local', start='r2b4', end='r2b3')
    f.text(60, 1260, '蓝色：CPU / 缓存写入    绿色：设备搬运（经过共享数据代理）    虚线：待完成写入', 26)
    f.text(60, 1310, '三个场景共同指向：输入先清理到 DDR，输出写前保护旧数据、写后清除旧副本。', 26)
    return f


def timeline():
    f = Figure('timeline', '裸机同步调用与硬件动作沿时间依次完成',
               '时间向下；首次维护前建立上下文。紫色：命令 / 确认；蓝色：缓存写入；绿色：设备搬运。', 2800, 1800)
    centers = [225, 695, 1165, 1635, 2105, 2575]
    headers = [
        ('CPU 裸机程序', '调用 HAL / 轮询', 'cpu'),
        ('范围维护引擎', '规划：汇合维护确认', 'agent'),
        ('L1D / 写缓冲', '排空与失效', 'cpu'),
        ('WB LLC', '清理与失效', 'memory'),
        ('DDR / 搬运器', '跨端口数据可见', 'memory'),
        ('共享代理 / GB / NPU', '装入、计算、搬出', 'gb'),
    ]
    for i, ((title, subtitle, fill), x) in enumerate(zip(headers, centers)):
        f.box(f'lane{i}', x-190, 130, 380, 95, title, [subtitle], fill=fill)
        f.parts.append(f'<line id="life{i}" x1="{x}" y1="225" x2="{x}" y2="1660" stroke="#BFC5CE" stroke-width="1.4" stroke-dasharray="7 7"/>')

    def message(key, a, b, y, label, kind='control', label_size=25):
        x1, x2 = centers[a], centers[b]
        f.arrow(key, [(x1,y),(x2,y)], kind)
        # White label backing keeps text readable where it crosses a lifeline.
        width = sum(label_size if ord(ch)>255 else label_size*.57 for ch in label)+24
        mid = (x1+x2)/2
        f.parts.append(f'<rect x="{mid-width/2}" y="{y-42}" width="{width}" height="35" fill="#FFFFFF" stroke="none"/>')
        f.text(mid, y-15, label, label_size, anchor='middle', color=C[kind])

    message('prepare', 0, 1, 290, '登记上下文后：同步输入 + 准备输出')
    message('drain', 1, 2, 370, '限制冲突新请求；排空已有读写')
    message('wt-store', 2, 3, 450, 'WT 先行写推进；LLC 保持接收', 'data')
    message('l1-drained', 2, 1, 530, '排空及输出 L1D 失效确认')
    message('clean', 1, 3, 610, '协调在途事务；输入 clean / 输出 clean + invalidate')
    message('writeback', 3, 4, 690, '经 S0 写回；检查错误响应', 'data')
    message('ddr-visible', 4, 1, 770, '跨端口可见；汇合缓存完成与错误状态')
    message('prepared', 1, 0, 850, '维护成功，退出窗口')
    message('submit', 0, 4, 930, '提交并确认接受：搬入 → 计算 → 搬出')
    message('dma-in', 4, 5, 1010, '输入搬入 GB', 'local')
    f.box('compute', 2385, 1050, 380, 65, 'NPU 计算，结果留在 GB', fill='gb')
    message('dma-out', 5, 4, 1170, '结果写入 DDR', 'local')
    message('task-done', 4, 0, 1250, '任务成功：搬出完成，CPU 端口可见')
    message('acquire', 0, 1, 1330, '同步输出：再次限制冲突新请求')
    message('post-l1', 1, 2, 1410, '排空旧回填，再最终失效')
    message('post-llc', 1, 3, 1490, '协调 LLC 在途事务，最终失效')
    message('acquired', 1, 0, 1610, '收齐确认且无错误；CPU 可读结果')
    f.text(55, 1700, '设备持有范围期间：CPU / Ara / 中断代码遵守访问约定；CPU 可处理其他独立数据。', 26)
    f.text(55, 1750, '错误或超时：保留上下文及 DDR / GB；停止新增请求，确认旧事务结束或有效隔离后再复用。', 26)
    return f


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    fs = [system(), versions(), timeline()]
    (args.out_dir/'layout.json').write_text(
        json.dumps([f.save(args.out_dir) for f in fs], ensure_ascii=False, indent=2)+'\n')
    print('Generated three figures:', ', '.join(f.name for f in fs))


if __name__ == '__main__':
    main()
