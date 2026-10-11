# 预算输入、公式与证据边界

本目录输入为 2026-10-11 M01/I01 架构审查的敏感性估算。**没有目标硬件实测吞吐值**。12000×12000、30 Hz 是待确认的压力场景；12288×12288 单独作尺寸敏感性。DDR 速率、DQ 位宽、控制器端口、频率、效率、模型及 SRAM 宏组织都没有据此冻结。

`budget_inputs.json` 的每个数值都带 `classification`（`measured` / `source` / `assumption`）与 `source` 索引。当前仅系统 AXI 64-bit 引自源码默认值，其余数值均为压力场景或分析假设。默认值不是所有构建目标的最终生效值。要换用供应商资料或实测值，应同时更新数值、分类、来源和输入版本。

源码依据：输入提交 `2784340240915fe4338ec54bfd613723b127d62e`，`hw/cheshire_pkg.sv::DefaultCfg.AxiDataWidth` 和 `get_llc_size()`；`hw/cheshire_soc.sv::i_llc`、`AraDataWideWidth`、`i_ara_axi_dw_converter`。本轮未改源码、配置或构建清单。

## 复现

在仓库根目录执行（Python 标准库，无安装依赖）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/test_budget.py
PYTHONDONTWRITEBYTECODE=1 python3 docs_codex/reviews/2026-10-11_architecture/scripts/budget.py --input docs_codex/reviews/2026-10-11_architecture/inputs/budget_inputs.json --output-dir /tmp/cheshire-budget-review-new
```

输出目录内的 `budget.json` / `budget.md` 已存在时拒绝覆盖；请换一个新目录。正式结果在 `../results/final/`。JSON 带输入文件和计算脚本 SHA-256；无时间戳，相同输入可逐字复现。

Markdown 门限摘要选择输入的首个图像尺寸，格式优先选与容量预算位宽相同的 packed 格式，不存在时选首个格式。标题、帧率及 ROI 标注使用实际输入；JSON 保留所有尺寸和格式组合。自检包括将帧率改为 60 fps，以及替换成 2560×1440、10-bit、12.5 fps 自定义场景，防止只对默认场景正确。

## 带宽和帧预算

- `DDR_peak = DQ_bits / 8 × rate_MT/s × 10⁶`；MT/s 已经是双边沿传输率，不再乘 2。
- `AXI_direction_peak = DW_bits / 8 × clock_MHz × 10⁶`。R/W 通道可以并行，但 DDR 物理预算按读写合计。
- `DDR_effective = peak × DDR_efficiency`。效率 50% / 65% / 80% 统一承载刷新、行切换、读写翻转等开销；不是每种访问模式都能达到同一效率。
- 单帧 `F = align_up(ceil(width × storage_bits / 8), stride_alignment) × height`；输入有效负载不含 blanking、编码或同步符号。
- 落 DDR 的流量 `R = F × fps × read_passes`，`W = F × fps × write_passes`。示例同尺寸同位宽；不同 ISP 输出尺寸/位宽应拆开做两段预算，不能套用同一 F。
- 最高 fps 同时受 `(DDR_effective − reserve_R − reserve_W)/(F × (reads+writes))`、控制器每方向剩余能力和图像 ingress 每方向能力限制；脚本取最小值。
- 0 次落帧只表示这一段图像没有 DDR 流量，不表示像素处理、NPU 权重/张量搬运或片上 SRAM 没有瓶颈。

默认并发预留 0.6 GB/s 读 + 0.15 GB/s 写代表 CPU/Ara 的**假设**预算。`combined_workloads` 额外加入合成 CNN 或 LLM 推理流量，不把这两种推理同时叠加。它显式核对总 DDR、控制器 R/W、图像 R/W 和 NPU R/W。默认 CNN 的输入与图像处理张量关系未知，单独计入以避免漏算；实际若同一读流被同时计在图像 read pass 和 CNN input 中，应按真实数据流合并，防止重复计算。

图像共用一个有指定方向上限的 ingress 是保守场景，不是建议必须合并所有主设备。真实实现若独立端口，按各端口分别约束；最终仍合计到同一物理 DDR。

## FIFO、ROI 与压缩

- 一次全阻塞需至少 `peak_input_B/s × blocked_time_s`，再加已有占用、帧封装/CDC/对齐余量。
- 长期稳定要求平均输入小于保证平均服务，且有明确最坏服务空窗；若输入持续超过服务，`time_to_full = free_bytes/(average_input−service)`，有限 FIFO 只能延迟溢出。
- `active_peak_multiplier` 仅放大短时输入峰值，平均不足判据仍用帧均输入。没有采集 active/blanking 资料时默认 1 是下限。
- ROI 面积或 fps 线性缩放仅是理想有效负载门限。行粒度、对齐、突发和最低服务保证仍需真实流量验证。
- 未启用压缩折减；平均压缩率不能保证不可反压输入的最坏持续流量。若未来使用压缩，应给出无压缩/最坏扩张回退预算。

## 模型、容量与分块

- `W = parameters × weight_bits/8 × (1 + metadata_fraction)`。默认 5% 元数据仅是假设；4-bit 存储不保证 NPU 或 Ara 原生计算支持该格式。
- 全注意力 KV：`K = 2 × layers × batch × context × KV_heads × head_dim × KV_bits/8`。实际应使用 KV 头数，不能把 GQA 查询头数直接代入。原始张量维度依据 [Transformers 官方 cache 说明](https://huggingface.co/docs/transformers/en/cache_explanation)。这只支持公式语义，不证明当前工程具备该运行时。
- 默认 24 层、8 个 KV 头、head_dim 64、context 4096、FP16、batch 1 得 192 MiB。它与 0.5B / 1.5B / 3B 参数量是**独立合成扫描轴**，不指代任何已选型模型。
- Decode 每批步读权重、读已有 KV、写新增 KV，加指定激活读写；Prefill 每请求按 1 / 4 次权重读取、整段 KV 写入和指定激活流量估算。其他算子、中间缓冲溢出、KV 重排、反量化代价必须另加。
- 访存时间下界为 `max((R+W)/DDR_remaining, R/AXI_R_remaining, W/AXI_W_remaining)`，并逐方向限于 NPU 口。Decode token/s 是这个下界的倒数乘 batch；没有算力、内核效率及软件时间，不能报告为产品性能。
- 容量按 OS/软件、保留区、2 / 4 帧、权重（含假设元数据）、激活 workspace、KV 合计；名义容量够不代表连续物理区、地址窗口、DMA 位宽或 Linux 分配成功。
- CNN 是合成的 8 MiB 权重、4 MiB 输入、32 MiB 激活总流量场景，扫描权重 1 / 2 / 4 次读回，不能称为检测/分割模型实测。
- GEMM 512³、INT8 输入、INT32 输出、tile 64×64×128：独有张量 1.5 MiB；输出 tile 之间不复用 A/B 时 5 MiB；四个 K 分块都把部分和写回 DDR 时 11 MiB。有效字节未含 burst padding；实际 CNN 还需加 halo 重读。

## GB 容量、bank 与双缓冲

示例 `2×(input_tile + weight_tile + output_tile) + accumulators + Ara_reserve + ISP_lines`。这是假设各项同时存活；实际应由算子 schedule 和生命周期推导，不能任意重叠。

GB 示例假设单端口 SRAM：每 bank 读写共享 `bank_DW/8 × f × efficiency`。8 个 bank 的总和够，热点 bank 仍可能超预算。默认 NPU 读集中到 2 个 bank，而其他流量均匀分布，显示 aggregate 通过但热点失败。采用双端口宏、bank 分组或交错寻址时应重建服务约束；端口名称不会增加真实 bank 服务能力。

示例还比较一轮 tile 搬运字节 / 分配给 DMA 的总吞吐与 tile 计算时间。缓冲容量容得下双缓冲，不保证能把搬运隐藏在计算后面。

SRAM 复用和避免内存往返的原始实现参考为 [NVDLA 官方架构](https://nvdla.org/hw/v1/hwarch.html) 的 fused operation / convolution buffer；并非本项目已采用 NVDLA。没有 55nm 存储宏、PVT、端口与布局资料，脚本不输出面积、频率承诺或功耗数字。

首版若 GB 经系统 64-bit 外扩口供 CPU/Ara/iDMA 访问，应继续套用 `AXI_sensitivity` 的 64-bit 行并计入系统总线竞争；工具中的 GB bank 内部峰值不能替代该入口能力。Ara 独立 128-bit 分流是否值得实现，需后续实测流量触发。
