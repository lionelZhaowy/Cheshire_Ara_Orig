#!/usr/bin/env python3
"""Standard-library-only architecture estimates. No RTL or hardware measurements.

All input numbers require provenance. Outputs refuse overwrite. B = byte;
GB/s = 10**9 B/s; GiB = 2**30 B; MT/s is transfers, not DDR clock MHz.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def number(value, label, minimum=0, integer=False, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{label}: finite number required')
    if not math.isfinite(value) or value < minimum or (positive and value == 0):
        raise ValueError(f'{label}: invalid range')
    if integer and int(value) != value:
        raise ValueError(f'{label}: integer required')
    return value


def efficiency(value):
    number(value, 'efficiency', positive=True)
    if value > 1:
        raise ValueError('efficiency > 1')
    return value


def unwrap(node, sources, path='parameters'):
    if isinstance(node, dict) and 'value' in node:
        if node.get('source') not in sources:
            raise ValueError(f'{path}: unknown source')
        if node.get('classification') not in ('measured', 'source', 'assumption'):
            raise ValueError(f'{path}: missing evidence classification')
        return node['value']
    if isinstance(node, dict):
        return {k: unwrap(v, sources, f'{path}.{k}') for k, v in node.items()}
    if isinstance(node, list):
        return [unwrap(v, sources, f'{path}[{i}]') for i, v in enumerate(node)]
    if isinstance(node, (float, int)):
        raise ValueError(f'{path}: bare numeric input has no provenance')
    return node


def ddr_bandwidth(dq_bits, mt_s, eff=1):
    number(dq_bits, 'DQ width', integer=True, positive=True)
    if dq_bits % 8:
        raise ValueError('DQ width must be byte aligned')
    number(mt_s, 'MT/s', positive=True)
    return dq_bits / 8 * mt_s * 1e6 * efficiency(eff)


def axi_bandwidth(data_bits, mhz, eff=1):
    """Per direction: R and W have separate channels, DDR total remains shared."""
    return ddr_bandwidth(data_bits, mhz, eff)


def frame_bytes(width, height, storage_bits, stride_alignment):
    for k, v in locals().copy().items():
        number(v, k, integer=True, positive=True)
    row_bytes = math.ceil(width * storage_bits / 8)
    stride = math.ceil(row_bytes / stride_alignment) * stride_alignment
    return stride * height


def max_image_fps(frame, reads, writes, ddr_total, controller_dir,
                  image_dir, reserve_read, reserve_write):
    """Conservative common-ingress directional constraints plus physical sum.

    If several engines have independent ports, replace image_dir with their
    actual per-port constraints; this function must not invent port parallelism.
    """
    for label, value in locals().copy().items():
        number(value, label)
    number(frame, 'frame', positive=True)
    total = reads + writes
    if not total:
        return None  # Image stream itself creates no DDR traffic; not infinite FPS.
    caps = [max(0, ddr_total - reserve_read - reserve_write) / (frame * total)]
    for count, reserve in ((reads, reserve_read), (writes, reserve_write)):
        if count:
            caps.extend((max(0, controller_dir - reserve) / (frame * count),
                         image_dir / (frame * count)))
    return min(caps)


def fifo_budget(arrival_Bps, guaranteed_service_Bps, block_us, capacity_bytes,
                sustained_arrival_Bps=None):
    if sustained_arrival_Bps is None:
        sustained_arrival_Bps = arrival_Bps
    for key, value in locals().copy().items():
        number(value, key)
    needed = arrival_Bps * block_us / 1e6
    deficit = max(0, sustained_arrival_Bps - guaranteed_service_Bps)
    return {'needed_for_single_block_bytes': needed,
            'single_block_fits': needed <= capacity_bytes,
            'empty_to_full_if_constant_deficit_s': capacity_bytes / deficit if deficit else None,
            'long_term_stable': sustained_arrival_Bps < guaranteed_service_Bps,
            'note': 'At equality there is no catch-up margin after stalls; framing/CDC margin excluded.'}


def kv_bytes(layers, batch, context, kv_heads, head_dim, bits):
    for key, value in locals().copy().items():
        number(value, key, integer=True, positive=True)
    return 2 * layers * batch * context * kv_heads * head_dim * bits / 8


def transfer_time_lower_bound(read_bytes, write_bytes, ddr_Bps, read_Bps, write_Bps):
    """Fluid service lower bound; real arbitration/latency can only add time."""
    for key, value in locals().copy().items():
        number(value, key)
    times = []
    for payload, service in ((read_bytes + write_bytes, ddr_Bps),
                             (read_bytes, read_Bps), (write_bytes, write_Bps)):
        if payload:
            if service == 0:
                return None  # Cannot make forward progress under this allocation.
            times.append(payload / service)
    return max(times, default=0)


def calculate(p):
    # Uniformly reject non-finite / negative values before calculations.
    def validate_tree(n, path='parameters'):
        if isinstance(n, dict):
            for k, v in n.items():
                validate_tree(v, path + '.' + k)
        elif isinstance(n, list):
            for v in n:
                validate_tree(v, path)
        elif isinstance(n, (int, float)):
            number(n, path)
    validate_tree(p)
    ddr_rows = []
    for dq in p['ddr']['dq_bits']:
        for rate in p['ddr']['rates_mt_s']:
            for eff in p['ddr']['efficiencies']:
                peak = ddr_bandwidth(dq, rate)
                ddr_rows.append({'dq_bits': dq, 'mt_s': rate, 'efficiency': eff,
                                 'peak_GB_s': peak / 1e9, 'effective_GB_s': peak * eff / 1e9})
                efficiency(eff)
    axi_rows = []
    for width in p['axi']['widths_bits']:
        for freq in p['axi']['clocks_mhz']:
            peak = axi_bandwidth(width, freq)
            axi_rows.append({'width_bits': width, 'clock_mhz': freq,
                             'peak_per_direction_GB_s': peak / 1e9,
                             'effective_per_direction_GB_s': peak / 1e9 * efficiency(p['axi']['efficiency'])})

    hardware = []
    for h in p['hardware_cases']:
        ddr = ddr_bandwidth(h['dq_bits'], h['mt_s'], h['ddr_efficiency'])
        ctrl = axi_bandwidth(h['controller_bits'], h['controller_mhz'], h['axi_efficiency'])
        image = axi_bandwidth(h['image_bits'], h['image_mhz'], h['axi_efficiency'])
        hardware.append({'id': h['id'], 'ddr_Bps': ddr,
                         'controller_direction_Bps': ctrl, 'image_direction_Bps': image,
                         'write_only_limit_Bps': min(ddr, ctrl, image),
                         'balanced_RW_limit_Bps': min(ddr, 2 * ctrl, 2 * image)})

    im = p['image']
    number(im['fps'], 'fps', positive=True)
    reserve = p['concurrency']
    rr, rw = reserve['read_GB_s'] * 1e9, reserve['write_GB_s'] * 1e9
    image_rows, limit_rows = [], []
    for shape in im['shapes']:
        for fmt in im['formats']:
            size = frame_bytes(shape['width'], shape['height'], fmt['storage_bits'], im['stride_alignment_bytes'])
            sensor_rate = shape['width'] * shape['height'] * fmt['sensor_bits'] / 8 * im['fps']
            image_rows.append({'shape': shape['id'], 'format': fmt['id'], 'frame_bytes': size,
                               'width': shape['width'], 'height': shape['height'], 'fps': im['fps'],
                               'sensor_bits': fmt['sensor_bits'], 'storage_bits': fmt['storage_bits'],
                               'frame_MiB': size / 2**20, 'input_payload_GB_s': sensor_rate / 1e9,
                               'one_DDR_write_GB_s': size * im['fps'] / 1e9,
                               'double_frame_MiB': 2 * size / 2**20})
            for pipe in im['pipelines']:
                for h in hardware:
                    maxfps = max_image_fps(size, pipe['reads'], pipe['writes'], h['ddr_Bps'],
                                          h['controller_direction_Bps'], h['image_direction_Bps'], rr, rw)
                    limit_rows.append({'shape': shape['id'], 'format': fmt['id'],
                                       'pipeline': pipe['id'], 'hardware': h['id'],
                                       'read_GB_s': size * im['fps'] * pipe['reads'] / 1e9,
                                       'write_GB_s': size * im['fps'] * pipe['writes'] / 1e9,
                                       'max_fps_after_reservation': maxfps,
                                       'max_ROI_fraction_at_requested_fps': min(1, maxfps / im['fps']) if maxfps is not None else None,
                                       'meets_average_budget': maxfps >= im['fps'] if maxfps is not None else None})

    primary_shape = im['shapes'][0]
    primary_frame = frame_bytes(primary_shape['width'], primary_shape['height'], im['capacity_storage_bits'], im['stride_alignment_bytes'])
    arrival = primary_frame * im['fps'] * im['active_peak_multiplier']
    fifo_rows = []
    for h in hardware:
        service = min(max(0, h['ddr_Bps'] - rr - rw),
                      max(0, h['controller_direction_Bps'] - rw), h['image_direction_Bps'])
        for block_us in p['fifo']['block_us']:
            row = fifo_budget(arrival, service, block_us, p['fifo']['capacity_bytes'], primary_frame * im['fps'])
            row.update({'hardware': h['id'], 'block_us': block_us, 'arrival_Bps': arrival,
                        'sustained_arrival_Bps': primary_frame * im['fps'],
                        'allocated_service_Bps': service,
                        'caveat': 'Service is an assumed allocation, not a measured latency guarantee.'})
            fifo_rows.append(row)

    llm = p['llm']
    if llm['weight_external_fraction'] > 1:
        raise ValueError('weight external fraction > 1')
    kv = kv_bytes(llm['layers'], llm['batch'], llm['context'], llm['kv_heads'], llm['head_dim'], llm['kv_bits'])
    per_step_kv = kv / llm['context']
    llm_rows, capacity_rows = [], []
    for params in llm['parameter_counts']:
        for bits in llm['weight_bits']:
            weights = params * bits / 8 * (1 + llm['weight_metadata_fraction'])
            decode_read = (weights * llm['weight_external_fraction'] * llm['decode_weight_reloads'] +
                           kv * llm['decode_kv_read_multiplier'] + llm['decode_activation_read_bytes'])
            decode_write = per_step_kv + llm['decode_activation_write_bytes']
            decode = decode_read + decode_write
            for h in hardware:
                bw = max(0, h['ddr_Bps'] - rr - rw)
                npu_dir = axi_bandwidth(llm['npu_bits'], llm['npu_mhz'], p['axi']['efficiency'])
                read_bw = min(max(0, h['controller_direction_Bps'] - rr), npu_dir)
                write_bw = min(max(0, h['controller_direction_Bps'] - rw), npu_dir)
                decode_time = transfer_time_lower_bound(decode_read, decode_write, bw, read_bw, write_bw)
                for reloads in llm['prefill_weight_reloads']:
                    prefill_read = weights * llm['weight_external_fraction'] * reloads + llm['prefill_activation_read_bytes']
                    prefill_write = kv + llm['prefill_activation_write_bytes']
                    prefill = prefill_read + prefill_write
                    prefill_time = transfer_time_lower_bound(prefill_read, prefill_write, bw, read_bw, write_bw)
                    llm_rows.append({'parameters': params, 'weight_bits': bits, 'hardware': h['id'],
                                     'weights_bytes_including_assumed_metadata': weights,
                                     'KV_bytes': kv, 'decode_bytes_per_batch_step': decode,
                                     'decode_read_bytes': decode_read, 'decode_write_bytes': decode_write,
                                     'decode_aggregate_token_s_memory_ceiling': llm['batch'] / decode_time if decode_time else None,
                                     'prefill_weight_reloads': reloads, 'prefill_bytes_per_request': prefill,
                                     'prefill_read_bytes': prefill_read, 'prefill_write_bytes': prefill_write,
                                     'prefill_memory_time_lower_bound_s': prefill_time})
            for cap in p['capacity']['DDR_GiB']:
                for count in p['capacity']['image_frame_counts']:
                    items = {'OS_and_software': p['capacity']['OS_bytes'],
                             'reserved': p['capacity']['reserved_bytes'],
                             'image_buffers': primary_frame * count,
                             'weights': weights, 'activation_workspace': p['capacity']['activation_bytes'], 'KV': kv}
                    total = sum(items.values())
                    capacity_rows.append({'DDR_GiB': cap, 'parameters': params, 'weight_bits': bits,
                                          'frame_count': count, 'components_bytes': items,
                                          'total_GiB': total / 2**30, 'spare_GiB': cap - total / 2**30,
                                          'fits_nominal_capacity': total <= cap * 2**30})

    cnn = p['cnn']
    cnn_rows = []
    for repeats in cnn['weight_reload_counts']:
        per_run = cnn['weights_bytes'] * repeats + cnn['input_bytes'] + cnn['activation_traffic_bytes']
        cnn_rows.append({'weight_reload_count': repeats, 'bytes_per_inference': per_run,
                         'at_requested_fps_GB_s': per_run * cnn['fps'] / 1e9})

    # A separate workload composition; the earlier image tables reserve only
    # CPU/Ara traffic, whereas these rows explicitly add synthetic inference.
    number(cnn['activation_read_fraction'], 'activation read fraction')
    if cnn['activation_read_fraction'] > 1:
        raise ValueError('activation read fraction > 1')
    workloads = [{'id': 'synthetic_CNN',
                  'read_Bps': (cnn['weights_bytes'] + cnn['input_bytes'] + cnn['activation_traffic_bytes'] * cnn['activation_read_fraction']) * cnn['fps'],
                  'write_Bps': cnn['activation_traffic_bytes'] * (1 - cnn['activation_read_fraction']) * cnn['fps']}]
    first_llm = llm_rows[0]
    workloads.append({'id': 'synthetic_LLM_first_parameter_and_bits',
                      'read_Bps': first_llm['decode_read_bytes'] * p['combined']['decode_batch_steps_s'],
                      'write_Bps': first_llm['decode_write_bytes'] * p['combined']['decode_batch_steps_s']})
    combined_rows = []
    npu_dir = axi_bandwidth(llm['npu_bits'], llm['npu_mhz'], p['axi']['efficiency'])
    for fps in p['combined']['image_fps']:
        for pipe in im['pipelines']:
            image_read = primary_frame * fps * pipe['reads']
            image_write = primary_frame * fps * pipe['writes']
            for w in workloads:
                reads, writes = image_read + w['read_Bps'] + rr, image_write + w['write_Bps'] + rw
                for h in hardware:
                    checks = {'DDR_total': reads + writes <= h['ddr_Bps'],
                              'controller_R': reads <= h['controller_direction_Bps'],
                              'controller_W': writes <= h['controller_direction_Bps'],
                              'image_R': image_read <= h['image_direction_Bps'],
                              'image_W': image_write <= h['image_direction_Bps'],
                              'NPU_R': w['read_Bps'] <= npu_dir, 'NPU_W': w['write_Bps'] <= npu_dir}
                    combined_rows.append({'hardware': h['id'], 'image_fps': fps, 'pipeline': pipe['id'],
                                          'inference': w['id'], 'total_GB_s': (reads + writes) / 1e9,
                                          'read_GB_s': reads / 1e9, 'write_GB_s': writes / 1e9,
                                          'average_constraints': checks, 'meets_all': all(checks.values())})

    gemm = p['gemm']
    for key in ('M', 'N', 'K', 'tile_M', 'tile_N', 'tile_K', 'input_bits', 'output_bits'):
        number(gemm[key], key, integer=True, positive=True)
    a = gemm['M'] * gemm['K'] * gemm['input_bits'] / 8
    b = gemm['K'] * gemm['N'] * gemm['input_bits'] / 8
    c = gemm['M'] * gemm['N'] * gemm['output_bits'] / 8
    mt, nt, kt = (math.ceil(gemm[x] / gemm['tile_' + x]) for x in ('M', 'N', 'K'))
    tile_rows = {'unique_tensor_bytes': a + b + c,
                 'no_cross_output_tile_reuse_bytes': a * nt + b * mt + c,
                 'with_partial_sum_spills_bytes': a * nt + b * mt + c * (2 * kt - 1),
                 'A_reload_factor': nt, 'B_reload_factor': mt, 'K_chunks': kt,
                 'note': 'Exact useful payload for this loop model; DMA padding/halo traffic is additional.'}

    gb = p['gb']
    number(gb['banks'], 'GB banks', integer=True, positive=True)
    number(gb['hot_banks'], 'hot banks', integer=True, positive=True)
    if gb['hot_banks'] > gb['banks']:
        raise ValueError('hot banks exceed total banks')
    bank_bw = axi_bandwidth(gb['bank_bits'], gb['clock_mhz'], gb['efficiency'])
    gb_capacity = (2 * (gb['input_tile_bytes'] + gb['weight_tile_bytes'] + gb['output_tile_bytes']) +
                   gb['accumulator_bytes'] + gb['Ara_reserve_bytes'] +
                   frame_bytes(primary_shape['width'], gb['ISP_line_count'], im['capacity_storage_bits'], im['stride_alignment_bytes']))
    demand = sum(x['read_GB_s'] + x['write_GB_s'] for x in gb['clients']) * 1e9
    hot_demand = gb['clients'][0]['read_GB_s'] * 1e9
    other_per_bank = (demand - hot_demand) / gb['banks']
    max_bank_demand = hot_demand / gb['hot_banks'] + other_per_bank
    tile_transfer = gb['input_tile_bytes'] + gb['weight_tile_bytes'] + gb['output_tile_bytes']
    number(gb['DMA_allocated_GB_s'], 'GB DMA allocation', positive=True)
    tile_transfer_us = tile_transfer / (gb['DMA_allocated_GB_s'] * 1e9) * 1e6
    gb_result = {'assumed_macro_type': 'single-port: reads + writes share each bank service',
                 'required_live_bytes': gb_capacity,
                 'candidate_capacity_fits': [{'MiB': cap, 'fits': cap * 2**20 >= gb_capacity} for cap in gb['capacity_MiB']],
                 'bank_service_GB_s': bank_bw / 1e9, 'aggregate_service_GB_s': bank_bw * gb['banks'] / 1e9,
                 'aggregate_demand_GB_s': demand / 1e9,
                 'uniform_bank_demand_GB_s': demand / gb['banks'] / 1e9,
                 'uniform_fits': demand <= bank_bw * gb['banks'],
                 'hot_bank_demand_GB_s': max_bank_demand / 1e9,
                 'hotspot_fits': max_bank_demand <= bank_bw,
                 'tile_transfer_bytes': tile_transfer, 'tile_DMA_time_lower_bound_us': tile_transfer_us,
                 'assumed_compute_tile_us': gb['compute_tile_us'],
                 'double_buffer_can_hide_this_DMA_budget': tile_transfer_us <= gb['compute_tile_us'],
                 'area_or_timing_result': None}
    # The Markdown summary follows the first configured shape, preferring its
    # packed capacity format. Fall back to the first format if none matches.
    summary_format = next((fmt for fmt in im['formats']
                           if fmt['sensor_bits'] == fmt['storage_bits'] == im['capacity_storage_bits']),
                          im['formats'][0])
    image_summary = {'shape': primary_shape['id'], 'width': primary_shape['width'],
                     'height': primary_shape['height'], 'format': summary_format['id'],
                     'storage_bits': summary_format['storage_bits'], 'requested_fps': im['fps']}
    return {'DDR_sensitivity': ddr_rows, 'AXI_sensitivity': axi_rows, 'hardware_cases': hardware,
            'image_summary': image_summary,
            'image_formats': image_rows, 'image_limits': limit_rows, 'FIFO': fifo_rows,
            'LLM': llm_rows, 'capacity': capacity_rows, 'CNN': cnn_rows, 'combined_workloads': combined_rows,
            'GEMM_tile_reloads': tile_rows, 'GB': gb_result}


def render(r):
    summary = r['image_summary']
    requested_fps = summary['requested_fps']
    lines = ['# 带宽与容量计算结果', '',
             '这是参数化估算，输入未含目标硬件实测值；所有频率、效率、模型和 SRAM 宏组织均未冻结。',
             '单位：GB/s=10⁹ B/s；MiB=2²⁰ B；GiB=2³⁰ B。AXI 上限按每方向，DDR 上限按读写合计。', '',
             '## DDR 敏感性', '', '| DQ | MT/s | 假设效率 | 峰值 GB/s | 有效 GB/s |', '|---|---|---|---|---|']
    for x in r['DDR_sensitivity']:
        lines.append(f"| {x['dq_bits']} | {x['mt_s']} | {x['efficiency']:.0%} | {x['peak_GB_s']:.4f} | {x['effective_GB_s']:.4f} |")
    lines += ['', '## 图像格式', '', '| 场景 | 格式 | 单帧 MiB | 输入有效负载 GB/s | 一次 DDR 写 GB/s |', '|---|---|---|---|---|']
    for x in r['image_formats']:
        lines.append(f"| {x['shape']} ({x['width']}×{x['height']}，{x['fps']:g} fps) | {x['format']} | {x['frame_MiB']:.3f} | {x['input_payload_GB_s']:.3f} | {x['one_DDR_write_GB_s']:.3f} |")
    lines += ['', f"## {summary['width']}×{summary['height']}、{summary['storage_bits']}-bit、{requested_fps:g} fps 场景门限", '',
              f"摘要选择输入首个尺寸 `{summary['shape']}`、格式 `{summary['format']}`；全部尺寸/格式的门限保留在 JSON。", '',
              '已扣输入指定的并发预留；按共同图像 ingress 限制各方向。零 DDR 落帧不意味端到端无限吞吐。', '',
              f'| 硬件候选 | 数据流程 | 读+写 GB/s | 最高平均 fps | {requested_fps:g} fps 的 ROI 面积占比上限 |', '|---|---|---|---|---|']
    for x in r['image_limits']:
        if x['shape'] != summary['shape'] or x['format'] != summary['format']:
            continue
        fps, roi = x['max_fps_after_reservation'], x['max_ROI_fraction_at_requested_fps']
        lines.append(f"| {x['hardware']} | {x['pipeline']} | {x['read_GB_s']+x['write_GB_s']:.3f} | " +
                     (f'{fps:.3f} | {roi:.2%} |' if fps is not None else '不适用 | 不适用 |'))
    lines += ['', '## Global Buffer', '', '```json', json.dumps(r['GB'], ensure_ascii=False, indent=2), '```', '',
              '## 解释边界', '',
              '- 先比较物理 DDR 总读写预算，再比较 controller 和各发起端各方向；多 AXI 入口不增加物理总带宽。',
              '- 0.5/0.65/0.8 DDR 效率包含刷新、读写切换、bank/row 冲突等的统一假设；不是承诺或实测。实际效率依流量改变。',
              '- ROI 门限仅按负载线性缩减，实际 stride、padding、burst 粒度和最坏服务间隔还需验证。',
              '- 输入流带宽是有效像素负载；LVDS 编码、blanking 和行有效期峰值另加，默认 active_peak_multiplier=1 只是下限。',
              '- FIFO 只分析指定单次全阻塞及恒定服务差；时延上界、排空间隔及 CDC 余量未经证明。',
              '- LLM 的 tokens/s 是仅由输入假设得到的访存上限，prefill 时间是访存下界；均不预测算力、精度和软件开销。',
              '- GB 假设单端口宏：每 bank 的读写服务合计受限；均匀分布可通过而热点仍失败。没有 55nm 宏时不生成面积/时序数字。',
              '- 完整 AXI、FIFO、LLM、容量、CNN、GEMM 分块记录在 budget.json。容量满足不证明地址窗口及 DMA 可达性满足。', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    data = json.loads(raw)
    p = unwrap(data['parameters'], data['sources'])
    result = calculate(p)
    result['provenance'] = {'input_sha256': hashlib.sha256(raw).hexdigest(),
                            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                            'input_version': data['input_version'],
                            'method': 'analytic estimate, not measured hardware throughput'}
    outputs = {'budget.json': json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
               'budget.md': render(result)}
    for name in outputs:
        if (args.output_dir / name).exists():
            raise FileExistsError(f'refuse overwrite: {args.output_dir / name}')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        with (args.output_dir / name).open('x', encoding='utf-8') as output:
            output.write(content)
    print(f'Created {args.output_dir / "budget.json"} and budget.md')


if __name__ == '__main__':
    main()
