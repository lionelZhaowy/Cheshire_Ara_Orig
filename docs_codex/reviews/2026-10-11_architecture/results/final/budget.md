# 带宽与容量计算结果

这是参数化估算，输入未含目标硬件实测值；所有频率、效率、模型和 SRAM 宏组织均未冻结。
单位：GB/s=10⁹ B/s；MiB=2²⁰ B；GiB=2³⁰ B。AXI 上限按每方向，DDR 上限按读写合计。

## DDR 敏感性

| DQ | MT/s | 假设效率 | 峰值 GB/s | 有效 GB/s |
|---|---|---|---|---|
| 16 | 1333 | 50% | 2.6660 | 1.3330 |
| 16 | 1333 | 65% | 2.6660 | 1.7329 |
| 16 | 1333 | 80% | 2.6660 | 2.1328 |
| 16 | 2133 | 50% | 4.2660 | 2.1330 |
| 16 | 2133 | 65% | 4.2660 | 2.7729 |
| 16 | 2133 | 80% | 4.2660 | 3.4128 |
| 32 | 1333 | 50% | 5.3320 | 2.6660 |
| 32 | 1333 | 65% | 5.3320 | 3.4658 |
| 32 | 1333 | 80% | 5.3320 | 4.2656 |
| 32 | 2133 | 50% | 8.5320 | 4.2660 |
| 32 | 2133 | 65% | 8.5320 | 5.5458 |
| 32 | 2133 | 80% | 8.5320 | 6.8256 |
| 64 | 1333 | 50% | 10.6640 | 5.3320 |
| 64 | 1333 | 65% | 10.6640 | 6.9316 |
| 64 | 1333 | 80% | 10.6640 | 8.5312 |
| 64 | 2133 | 50% | 17.0640 | 8.5320 |
| 64 | 2133 | 65% | 17.0640 | 11.0916 |
| 64 | 2133 | 80% | 17.0640 | 13.6512 |

## 图像格式

| 场景 | 格式 | 单帧 MiB | 输入有效负载 GB/s | 一次 DDR 写 GB/s |
|---|---|---|---|---|
| 12000x12000 (12000×12000，30 fps) | raw8_packed | 137.329 | 4.320 | 4.320 |
| 12000x12000 (12000×12000，30 fps) | raw12_packed | 205.994 | 6.480 | 6.480 |
| 12000x12000 (12000×12000，30 fps) | raw14_packed | 240.326 | 7.560 | 7.560 |
| 12000x12000 (12000×12000，30 fps) | raw16_packed | 274.658 | 8.640 | 8.640 |
| 12000x12000 (12000×12000，30 fps) | raw8_in16 | 274.658 | 4.320 | 8.640 |
| 12000x12000 (12000×12000，30 fps) | raw12_in16 | 274.658 | 6.480 | 8.640 |
| 12000x12000 (12000×12000，30 fps) | raw14_in16 | 274.658 | 7.560 | 8.640 |
| 12288x12288 (12288×12288，30 fps) | raw8_packed | 144.000 | 4.530 | 4.530 |
| 12288x12288 (12288×12288，30 fps) | raw12_packed | 216.000 | 6.795 | 6.795 |
| 12288x12288 (12288×12288，30 fps) | raw14_packed | 252.000 | 7.927 | 7.927 |
| 12288x12288 (12288×12288，30 fps) | raw16_packed | 288.000 | 9.060 | 9.060 |
| 12288x12288 (12288×12288，30 fps) | raw8_in16 | 288.000 | 4.530 | 9.060 |
| 12288x12288 (12288×12288，30 fps) | raw12_in16 | 288.000 | 6.795 | 9.060 |
| 12288x12288 (12288×12288，30 fps) | raw14_in16 | 288.000 | 7.927 | 9.060 |

## 12000×12000、16-bit、30 fps 场景门限

摘要选择输入首个尺寸 `12000x12000`、格式 `raw16_packed`；全部尺寸/格式的门限保留在 JSON。

已扣输入指定的并发预留；按共同图像 ingress 限制各方向。零 DDR 落帧不意味端到端无限吞吐。

| 硬件候选 | 数据流程 | 读+写 GB/s | 最高平均 fps | 30 fps 的 ROI 面积占比上限 |
|---|---|---|---|---|
| x16_1333_ctrl64 | stream_ISP_then_write | 8.640 | 3.413 | 11.38% |
| x64_1333_ctrl256 | stream_ISP_then_write | 8.640 | 21.464 | 71.55% |
| x64_2133_ctrl256 | stream_ISP_then_write | 8.640 | 25.000 | 83.33% |
| x16_1333_ctrl64 | write_then_NPU_read | 17.280 | 1.706 | 5.69% |
| x64_1333_ctrl256 | write_then_NPU_read | 17.280 | 10.732 | 35.77% |
| x64_2133_ctrl256 | write_then_NPU_read | 17.280 | 17.954 | 59.85% |
| x16_1333_ctrl64 | raw_write_ISP_read_write_NPU_read | 34.560 | 0.853 | 2.84% |
| x64_1333_ctrl256 | raw_write_ISP_read_write_NPU_read | 34.560 | 5.366 | 17.89% |
| x64_2133_ctrl256 | raw_write_ISP_read_write_NPU_read | 34.560 | 8.977 | 29.92% |
| x16_1333_ctrl64 | direct_ISP_to_NPU_no_frame_spill | 0.000 | 不适用 | 不适用 |
| x64_1333_ctrl256 | direct_ISP_to_NPU_no_frame_spill | 0.000 | 不适用 | 不适用 |
| x64_2133_ctrl256 | direct_ISP_to_NPU_no_frame_spill | 0.000 | 不适用 | 不适用 |

## Global Buffer

```json
{
  "assumed_macro_type": "single-port: reads + writes share each bank service",
  "required_live_bytes": 2717440,
  "candidate_capacity_fits": [
    {
      "MiB": 1,
      "fits": false
    },
    {
      "MiB": 2,
      "fits": false
    },
    {
      "MiB": 4,
      "fits": true
    }
  ],
  "bank_service_GB_s": 1.28,
  "aggregate_service_GB_s": 10.24,
  "aggregate_demand_GB_s": 9.46,
  "uniform_bank_demand_GB_s": 1.1825,
  "uniform_fits": true,
  "hot_bank_demand_GB_s": 3.0575,
  "hotspot_fits": false,
  "tile_transfer_bytes": 1048576,
  "tile_DMA_time_lower_bound_us": 699.0506666666666,
  "assumed_compute_tile_us": 250,
  "double_buffer_can_hide_this_DMA_budget": false,
  "area_or_timing_result": null
}
```

## 解释边界

- 先比较物理 DDR 总读写预算，再比较 controller 和各发起端各方向；多 AXI 入口不增加物理总带宽。
- 0.5/0.65/0.8 DDR 效率包含刷新、读写切换、bank/row 冲突等的统一假设；不是承诺或实测。实际效率依流量改变。
- ROI 门限仅按负载线性缩减，实际 stride、padding、burst 粒度和最坏服务间隔还需验证。
- 输入流带宽是有效像素负载；LVDS 编码、blanking 和行有效期峰值另加，默认 active_peak_multiplier=1 只是下限。
- FIFO 只分析指定单次全阻塞及恒定服务差；时延上界、排空间隔及 CDC 余量未经证明。
- LLM 的 tokens/s 是仅由输入假设得到的访存上限，prefill 时间是访存下界；均不预测算力、精度和软件开销。
- GB 假设单端口宏：每 bank 的读写服务合计受限；均匀分布可通过而热点仍失败。没有 55nm 宏时不生成面积/时序数字。
- 完整 AXI、FIFO、LLM、容量、CNN、GEMM 分块记录在 budget.json。容量满足不证明地址窗口及 DMA 可达性满足。
