# 32 · 模型任务划分与容量带宽预算

明确假设下的 Ara/NPU 协作与数据搬运成本。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/models.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../models.html) · [阅读路线](index.md)

- [32.1 Ara–NPU–Ara 协作的候选流程](#model-case)
  - [32.1.1 候选分工与交接次数](#partition)
  - [32.1.2 数据规模、数值与搬运成本](#cost)
  - [32.1.3 完整协作流程及未实现接口](#cooperation)
- [32.2 存储容量、数据流量与性能预算](#budget)
- [32.3 带明确假设的容量估算](#calculator)

**本章任务**

用透明假设衡量 Ara/NPU 协作成本。 前置：[12 · RVV 编程与结果验证](vector.md)、[13 · CPU、Ara、DMA 与 NPU 的共享数据](sharing.md)、[31 · LVDS、ISP、NPU 与外部 DDR 集成](accelerators.md)。

本章是应用规划选读：已理解数组与共享数据后，用一个小模型估算协作成本；它不是学习OS或ASIC平台的先决条件。故障后的隔离和缓冲回收见[系统诊断](system-debug.md#frames)，正常计时方法见[测量章](measurement.md)。

<a id="model-case"></a>

## 32.1 Ara–NPU–Ara 协作的候选流程

取一条小型全连接片段作为规划例：输入 X 为 1×137 的 int8，权重 W 为 137×64 的 int8，零点暂取 0，乘加输出 Y 为 1×64 的 int32；随后求 Y 的最大值或总和并按已约定的定点乘数、舍入和饱和规则产生 int8 输出。137 与[RVV 分块与尾部处理](vector.md#loop)使用同一数组长度。这里只固定教学算例，不冻结产品量化格式。

<a id="partition"></a>

### 32.1.1 候选分工与交接次数

一种候选划分是 CPU 分配描述符并校验边界，Ara 将输入从应用布局整理/量化成 NPU 约定布局，NPU 做矩阵乘加，Ara 对 64 项 int32 做归约、激活或再量化，CPU 检查并交还缓冲。另一种是 Ara 独自完成整个小矩阵；第三种让 NPU 融合后处理减少一次交接。单个 137×64 小任务可能被提交/同步成本主导，无法仅凭峰值 MAC 数选择。

<a id="cost"></a>

### 32.1.2 数据规模、数值与搬运成本

| 数据与工作 | 本教学例的规模 | 交接与测量关注点 |
| --- | --- | --- |
| X / W | 137 B / 8768 B | 原始大小未含对齐、padding 与 NPU tile 布局；权重能否复用决定实际 DDR 流量 |
| Y / 输出 | 256 B / 64 B | 两次生产者切换：Ara→NPU，NPU→Ara；另有 CPU 完成回收 |
| 未融合最低数据读写示例 | 中间输入写读 274 B、权重读 8768 B、Y 写读 512 B、最终输出写 64 B，共 9618 B | 未含原始输入读取、描述符、对齐放大、cache line 与重复权重加载，不能当总线实测带宽；这些是跨存储边界的逻辑读写量，采用[独立 GB](accelerators.md#global-buffer)后，GB 内部流量不能全部计入 DDR |
| 数值验证 | 独立 int64 累加参考再检查 int32 范围 | 最坏 137×16384=2244608 在 int32 内；量化舍入、饱和与 scale 另核对 |

<a id="cooperation"></a>

### 32.1.3 完整协作流程及未实现接口

```
/* 未来接口伪代码：尚无 NPU 驱动或寄存器地址 */
lease = acquire_buffer(layout, sizes, alignment);
ara_prepare_input(lease.input);          /* 此前仅数组/归约内核通过构建 */
publish_visible(lease.input, NPU);       /* 按实际缓存/拓扑契约实现 */
ticket = npu_submit(lease, shape, quant);
status = wait_bounded(ticket, deadline);
/* 仅成功分支可继续；失败/隔离契约见独立系统诊断。 */
if (status.success) {
    acquire_visible(lease.output, ARA);
    ara_postprocess(lease.output);
    publish_visible(lease.output, CPU);
    verify_and_release(lease);
}
```

此前通过构建的部分是[实验 E 的数组运算、尾部与整数归约](labs.md#rvv-depth)，并非本页完整模型流程；它们尚未完成当前 SoC 动态回归。伪代码中的 npu\_submit、可见性及失败恢复没有现成实现，未来规格必须定义 tensor layout、量化规则、完成码、epoch 和复位语义。完整所有权/交接时序见[第 13 章](sharing.md#handoff)，控制/数据拓扑实施计划见[第 31 章](accelerators.md#npu-topology)。

判断此划分是否值得采用，应对相同数值标准测量 Ara-only、NPU+Ara、NPU 融合三个端到端方案，改变 batch、权重复用次数和布局转换量，记录内核/搬运/同步时间以及 DDR 实际字节。当前没有 NPU IP、驱动和性能记录，案例用于设计实验，不承诺目标模型的吞吐、容量或生态支持。

<a id="budget"></a>

## 32.2 存储容量、数据流量与性能预算

模型权重的理想容量是参数量 P×每参数位数/8，实际还要加量化元数据、激活、工作区和对齐。例如 2B 参数 INT4 权重约 1 GB。KV cache 保存历史 token 的键和值，是软件模型数据，不是硬件 LLC；同构解码器的估算为 `2×层数×KV头数×每头维度×上下文×并发数×每元素字节`。

假设 24 层、8 个 KV 头、每头 128 维、上下文 4096、并发 1、KV 每元素 2 字节，则 KV 为 384 MiB。再假设工作区 256 MiB、总容量余量 20%，约需 1.87 GiB。这是透明的教学假设，实际算子调度和内核支持决定工作区；默认外存路由窗口 2 GiB 也不等于已经提供同容量的物理 DDR。

单请求逐 token 生成、每步从 DDR 读取全部权重与该请求 KV 且无权重复用时，10 token/s 的示例仅这两部分就约需 14 GB/s 有效读取。理想耗时下界可用 `max(运算量/有效算力, 数据量/有效带宽)`，再加入调度、同步、格式转换及其他流量。Ara 或未来 NPU 的精度内核、频率和有效利用率必须实测后才能评价最终应用。

<a id="calculator"></a>

## 32.3 带明确假设的容量估算

下面保留公式交互，用于把上下文从 4096 改为 8192 后观察 KV 翻倍。并发数影响容量，带宽按单请求估算，不自动假定批处理共享权重。关闭脚本仍可用上文公式计算。

<a id="ai-calc"></a>

交互计算见本章 HTML 版；以下保留输入与默认值。

参数量（B）（初值 `2`）

权重位数（初值 `4`）

层数（初值 `24`）

KV 头数（初值 `8`）

每头维度（初值 `128`）

上下文 token（初值 `4096`）

并发数（初值 `1`）

KV 元素字节（初值 `2`）

工作区 MiB（初值 `256`）

容量余量 %（初值 `20`）

单请求 token/s（初值 `10`）

<a id="calc-result"></a>

默认假设：权重 0.93 GiB，KV 0.375 GiB，含工作区与余量约 1.87 GiB；读取约 14 GB/s。**源码与进一步阅读**

[当前平台适配参考](../../../target/xilinx/src/dram_wrapper_xilinx.sv)；[Ara 实例与失效通路](../../../hw/cheshire_soc.sv)；[CPU 队列、非推测发射、pending 与 barrier](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/acc_dispatcher.sv)；[初译码与 VS/FS](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/cva6_accel_first_pass_decoder.sv)；[专用接口字段](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/ara/intf_typedef.svh)；[内部运行表与地址应答](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv)；[地址/翻译/对齐限制](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/addrgen.sv)；[load 完成](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vldu.sv)；[store 完成和 B 错误缺口](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vstu.sv)；[MMU 与保护消费者](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/load_store_unit.sv)；[本地支持声明与 ELEN](../../../.bender/git/checkouts/ara-2c7b103275a16c87/FUNCTIONALITIES.md)；[RVV 类型与编码](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/rvv_pkg.sv)；[随附官方 VRF/重排说明](../../../.bender/git/checkouts/ara-2c7b103275a16c87/docs/source/lane.rst)；[dispatcher / sequencer / lanes / VLSU](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara.sv)；[csr\_vl\_d 分块选择](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_dispatcher.sv)；[Ara 写失效](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/axi_inval_filter.sv)；[VS 与 acc\_cons 状态](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv)

---

[上一页：LVDS、ISP、NPU 与外部 DDR 集成](accelerators.md) · [下一页：电源域与低功耗规划](power.md)
