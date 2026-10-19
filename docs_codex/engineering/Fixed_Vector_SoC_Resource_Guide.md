# 固定向量 SoC 资源、存储组织与配置问答

返回[工程参考索引](README.md) · 配合[配置手册](../configuration/README.md)、[服务器仿真上手指南](../software/SERVER_SIMULATION_GUIDE.md)阅读。

更新：2026-10-19。本文整理固定 Cheshire/CVA6/Ara 配置的资源问答，面向 RTL 阅读、SRAM 宏盘点及后续容量评估。数值来自当前源码静态推导；本轮未编译、仿真、综合或访问服务器，未修改硬件配置。

2026-10-19 用户确认：提取工程保留集中配置入口，固定带 Ara 的功能组合，逐步开放资源参数，以应用验证和一致口径的面积/时序比较选择配置。**首次提取仍保持当前基线；认可评估方法不等于候选数值已支持、已验证或已选为产品配置。** 实施约束以 [ASIC 提取规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)为准，本文解释资源关系与评估方法。

## 问题索引

| 问题 | 阅读位置 |
| --- | --- |
| 统计的是哪个版本、哪组配置？ | [Q1：基线与统计口径](#q1) |
| 片上 SRAM、通用寄存器、CSR 和 ROM 各占多少？ | [Q2：资源总览](#q2) |
| L1I、L1D、LLC 分别是 WB 还是 WT？ | [Q3：缓存策略与 SPM](#q3) |
| 各 SRAM bank 的深度、宽度、端口是什么？word 是多少字节？ | [Q4：SRAM 与地址](#q4) |
| LLC 为什么是 256 组，却有 2048 深度？路数等于 bank 数吗？ | [Q4.2：逻辑组织与物理组织](#cache-organization) |
| TLB、RAS、BTB、BHT 的项数和每项开销？ | [Q5：地址转换与预测状态](#q5) |
| 哪些要换 MemCompiler 宏，哪些直接综合成寄存器？ | [Q6：ASIC 存储实现](#q6) |
| 怎样扩大 L1/LLC？参数能否独立更改？ | [Q7.1：Cache 扩容](#cache-resize) |
| VRF 与 VLEN、lane 的关系，能否改容量？ | [Q7.2：VRF 配置](#vrf-resize) |
| 哪些参数先开放，怎样保留统一配置？ | [Q7：开放顺序](#q7)、[Q7.4：集中配置](#config-management) |
| 当前资源对 v1 够用吗？优先提高什么？ | [Q8：性能与取舍](#q8) |
| 如何比较应用性能，Pad 限制下能否增加内部面积？ | [Q8.1：应用比较](#application-comparison)、[Q8.2：面积取舍](#area-tradeoffs) |

<a id="q1"></a>

## Q1．统计的是哪组配置？

本地输入为 `mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，含已有未提交文档。源码定位指向本仓库受保护的 `.bender/` 快照，不假定在线最新版本行为相同。

服务器参考工程为 `~/CheshireAraPULP`。已有核查记录的 Cheshire 为 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a`，Ara 为 `2895ba907e9eb14b3464609dc791a969d159a7c3`，CVA6 为 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`。此前核对的 716 个直接编译源两端哈希相同，但不代表全部 include、软件、宏及工具环境等价；详见[范围对比](../maintenance/E01/reports/local_server_build_comparison.md)。本文沿用这些历史证据，不新增服务器验证结论。

| 配置项 | 本文固定值 | 生效位置或注意点 |
| --- | --- | --- |
| CPU | 1 核，`cv64a6_imafdcv_sv39` | 编译时选择 profile；`SELCFG` 不替代 profile 选择 |
| CPU 位宽 | XLEN=64，地址容器 VLEN=64，PLEN=56，Sv39 | CPU 的 `VLEN` 不是 Ara 向量长度 |
| L1I | 4 KiB、4 路、16 B/行 | 64 组 |
| L1D | 8 KiB、4 路、32 B/行、WT | 64 组 |
| SoC AXI | 地址 48 bit，数据 64 bit | L1 标签按 CPU PLEN 推导，LLC 标签按 AXI 地址宽度推导 |
| LLC/SPM | 8 路、256 行/路、8 个 64-bit word/行 | 128 KiB 共用数据阵列 |
| Ara | 开启，2 lanes，VLEN=2048 bit | TB Ara 配置为 `SELCFG=3`；使用 Ara 的真实 first-pass decoder |
| SRAM 选择 | `FpgaEn=0`、`TechnoCut=0`，Cache USER 存储关闭 | CVA6 选入 `sram_pulp.sv`；不统计未生成分支 |
| TLB、预测器、PMP | ITLB/DTLB 各 16 项；RAS=2、BTB=32、BHT=128、PMP=0 | 后四项须检查 SoC 的 `gen_cva6_cfg()` 覆盖，不能只看 profile |

配置链是 **profile → `gen_cva6_cfg()` 覆盖 → `build_config()` 派生 → 模块实例**；Ara 还需核对 SoC 配置和构建宏。见 [CPU profile][cpu-profile]、[Cheshire 配置包][chs-pkg]、[派生配置][cpu-build]、[TB 配置][tb-cfg]。

统计统一采用 `1 KiB=1024 B`，并区分：

- **逻辑存储位数**：由 RTL 的有效配置和数组形状计算，数据与标签分别列出。
- **物理宏容量**：可能因工艺库尺寸、拼接或位宽取整而增大；逻辑实例数不等于最终宏数量。
- **综合/布局面积**：还包括比较器、选择器、控制、时钟、布线及宏周边空间，不能由 KiB 直接换算。

<a id="q2"></a>

## Q2．主要资源有多少？

### Q2.1 主要 SRAM 数据与标签

下表“深度”单位是该 SRAM 自己的 word，“宽度”单位是 bit。容量公式为 `bank 数 × 深度 × 宽度 / 8`；标签的字节数只是位数折算，不表示支持字节寻址。

| 对象 | bank 数 | 每 bank 深度 | 每 word 宽度 | 本行合计 B | 内容 |
| --- | ---: | ---: | ---: | ---: | --- |
| L1I 数据 | 4 | 64 | 128 | 4096 | 每路一个 bank，每项一整行 |
| L1I 标签/有效位 | 4 | 64 | 47 | 1504 | 46-bit tag＋valid |
| L1D 数据 | 4 | 64 | 256 | 8192 | 按行内 word 分 bank，每项含四路数据 |
| L1D 标签/有效位 | 4 | 64 | 46 | 1472 | 45-bit tag＋valid |
| LLC/SPM 数据 | 8 | 2048 | 64 | 131072 | 每路一个 bank，每行占 8 个 word |
| LLC 标签/状态 | 8 | 256 | 36 | 9216 | 34-bit tag＋valid＋dirty |
| Ara VRF | 16 | 64 | 64 | 8192 | 2 lanes × 8 banks/lane；没有 Cache 标签 |
| **合计** | **48** | — | — | **163744** | **159.90625 KiB** |

有效数据容量为 `4+8+128+8=148 KiB`，标签及其状态为 `11.90625 KiB`。**这是所列 Cache/VRF 的 48 个逻辑 `tc_sram` 实例，不是整个 SoC 的全部存储资源。** 外设 FIFO、队列、控制状态、ROM 和寄存器等未包含在此合计中。

标签宽度的推导：

```text
L1I：56 − log2(4096/4) = 46-bit tag；加 valid → 47 bit
L1D：56 − log2(8192/4) = 45-bit tag；加 valid → 46 bit
LLC：48 − log2(256) − log2(8) − log2(8 B) = 34-bit tag
     加 valid、dirty → 36 bit
```

这里不能统一把 56 替换成 AXI 的 48；也不能把所有标签都补成 64 bit 后称为当前 RTL 容量。实际清单选中 [sram_pulp.sv][sram-pulp]，保留传入位宽；同目录另一个未选中的 `sram.sv` 不是本表依据。此前按另一实现补齐所得的 161 KiB 推算不沿用。选择关系见 [CVA6 Bender 清单][cva6-bender]，数组见 [I-Cache][icache]、[D-Cache 存储][dcache-mem]、[LLC 数据][llc-data]、[LLC 标签][llc-tag]及 [VRF][vrf]。

### Q2.2 通用寄存器、浮点寄存器与已核查 CSR

| 对象 | 数量与宽度 | 唯一数据状态 | 实现/去重说明 |
| --- | --- | ---: | --- |
| GPR：`x0–x31` | 声明 32×64；x0 恒零 | 31×64＝1984 bit＝248 B | 当前 FF 实现，2 读/2 写；不含译码、MUX、旁路开销 |
| FPR：`f0–f31` | 32×64 | 2048 bit＝256 B | 当前 FF 实现，3 读/2 写；f0 可写，不是零寄存器 |
| cycle、instret | 2×64 | 128 bit | 用户/机器模式 CSR 访问名不各算一份存储 |
| HPM 计数器 | 6×64 | 384 bit | `PerfCounterEn=1`、`MHPMCounterNum=6` |
| HPM 事件选择 | 6×5 | 30 bit | 按实际选择字段统计，不把每个 CSR 地址都算成 64 bit |
| Ara `vl`、`vstart` | 各 `$clog2(2048+1)=12` | 24 bit | 当前有效元素数、恢复起点 |
| Ara `vtype` | vill/vma/vta 各 1，vsew/vlmul 各 3 | 9 bit | 读 CSR 时扩展到 XLEN，不增加同等存储 |
| Ara `vxrm`、`vxsat` | 2＋1 | 3 bit | `vcsr` 是这两者的组合访问；`vlenb=256` 为常量 |

GPR＋FPR 有效数据状态合计 **504 B**。表内 CVA6 计数器及事件选择共 **542 bit**，Ara 所列架构 CSR 共 **36 bit**；这些都是子集，不能相加后称为“整个 CPU/Ara 的全部寄存器”。M/S/debug CSR、异常状态、流水线和各级控制寄存器尚未逐位汇总；CSR 别名及组合下一状态 `_d/_n` 也不能重复计数。

出处：[寄存器堆实例][regfile-inst]、[FF 寄存器堆][regfile-ff]、[CPU CSR][cpu-csr]、[性能计数器][perf]、[ariane_pkg 的 HPM 数量][ariane-pkg]、[Ara dispatcher][ara-dispatcher]与 [RVV 类型][rvv-pkg]。PMP=0 是当前 SoC 覆盖结果，不应把 profile 中 8 项 PMP 当成有效实例。

还有一些已知规模但未在本文完整计位的结构：WT 写缓冲 8 项、scoreboard 8 项、load buffer 2 项，以及访存/互连/外设 FIFO。条目还包含地址、掩码、状态等，不能只乘 XLEN；最终总量需要综合资源报告。

### Q2.3 Boot ROM 是 8 KiB、16 KiB 还是 256 KiB？

三者是不同口径：

| 口径 | 当前值 | 依据 |
| --- | ---: | --- |
| 生成 ROM 的逻辑内容空间 | 2048×32 bit＝**8 KiB** | `cheshire_bootrom.sv` 的 `NumWords=2048`，SoC 实例 `DataWidth=32` |
| 软件链接预算 | **16 KiB** | `common.ldh` 的 `bootrom LENGTH=16K` |
| 上层地址解码窗口 | **256 KiB** | `AmBrom` 到 `AmBrom+0x40000` |

当前 ROM 是生成的组合 `case` 查表，不是 `tc_sram`；不能按地址窗口估算它的物理存储，也不计入前面的 SRAM 合计。最终可综合为常量逻辑，或另行适配 ROM 宏，面积待实现。出处：[生成 ROM][bootrom-rtl]、[SoC 实例][chs-soc]、[链接定义][link-common]和 [Cheshire 地址图][chs-pkg]。

<a id="q3"></a>

## Q3．L1I、L1D、LLC 是 WB 还是 WT？

| 存储 | 当前策略 | 对访问的含义 |
| --- | --- | --- |
| L1 I-Cache | 不适用普通数据写入的 WB/WT 分类 | 服务取指；回填写入 SRAM 不等于 CPU store，不维护数据脏行 |
| L1 D-Cache | **WT，write-through** | 写入通过写缓冲向下层传播；不等于当拍已写到 DDR |
| LLC 的 Cache ways | **WB，write-back** | 写命中可只更新 LLC 脏行，驱逐/flush 时回写下层 |
| LLC 的 SPM ways | 直接寻址的片上存储 | 数据本身就在 SPM 中，不采用 Cache 的 WB/WT 分类 |

CPU 的 WT 写入到达 WB LLC 后，仍可能只驻留于 LLC，不能据“L1D 是 WT”推断 CPU 与 DDR 设备自动一致。Ara 自身的访存也不经过 CPU L1D，设备共享问题应沿实际访问路径分析，见[DDR–GB 数据同步设计](DDR_GB_Coherence_Design.md)。

**LLC 和 SPM 共用 128 KiB 数据阵列，不能各计 128 KiB。** 当前 Boot ROM 等待 LLC 自测后把所有 way 设为 SPM，并据容量设置栈；未由软件重新分配前，这些 way 不承担 DDR 数据缓存。全部设为 SPM 时，LLC 的外部存储 Cache 路径旁路。后续可按 way 划分缓存/SPM，但要处理 flush、在途事务和仍驻留于 SPM 的栈/数据。

例如当前每 way 为 16 KiB，分配 4 ways 给 SPM、4 ways 给 Cache，分别是 64 KiB，而不是新增 64 KiB。该例只说明共享关系，本文未修改运行时分配。出处：[Boot ROM 初始化][bootrom-start]、[LLC 官方说明](https://pulp-platform.github.io/axi_llc/module.axi_llc_top)及[本地 LLC 文档][llc-doc]；官方页面中的默认容量不替代本工程 128 KiB 配置。

<a id="q4"></a>

## Q4．怎样读懂 SRAM 的 bank、深度和宽度？

### Q4.1 64 word 是否等于 64×8 个地址？

**word 是该 SRAM 一次寻址的数据宽度，不固定等于 CPU 的 64 bit。** 深度 64 表示内部有 64 个 word 地址（0～63），需要 6-bit 字地址。

| SRAM 形状 | 内部 word 地址数 | 每地址的数据量 | 总容量 |
| --- | ---: | ---: | ---: |
| 64×64 bit | 64 | 8 B | 512 B |
| 64×128 bit | 64 | 16 B | 1024 B |
| 64×256 bit | 64 | 32 B | 2048 B |
| 64×47 bit | 64 | 47 bit | 376 B 等效位数 |

只有把 `64×64 bit` SRAM 线性映射到 CPU 的字节地址空间时，才对应 **512 个字节地址**；SRAM 内部仍是 64 个 word 地址。设字节偏移为 `offset`：

```text
SRAM 字地址 = offset >> 3       // 选择 64 个 word 之一
字内字节位置 = offset[2:0]      // 选择该 64-bit word 中的字节
```

字节读取由选择逻辑完成；部分写由 byte enable 保留未写字节。Cache 标签和 VRF 不是简单映射的普通 CPU 内存，地址由 Cache 索引或向量寄存器映射逻辑产生。

<a id="cache-organization"></a>

### Q4.2 LLC 为什么 256 组对应 2048 深度？

**组数描述 Cache 的逻辑组织；深度描述一个 SRAM bank 的 word 数。一行可以占一个 word，也可以拆成多个 word。**

| 对比项 | 当前 L1I | 当前 LLC |
| --- | ---: | ---: |
| 路数 | 4 | 8 |
| 每路行数，即组数 | 64 | 256 |
| 每行字节数 | 16 B | 64 B |
| 每路数据 SRAM word 宽度 | 128 bit | 64 bit |
| 每行占用 word 数 | 1 | 8 |
| 每路数据 SRAM 深度 | 64×1＝64 | 256×8＝2048 |

选定 LLC 某一路后，它的数据 SRAM 可以理解为：

```text
SRAM 字地址   存储内容
0～7          第 0 组的一条 line，拆成 8 个 64-bit word
8～15         第 1 组的一条 line
...
2040～2047    第 255 组的一条 line

数据 SRAM 地址 = {8-bit 组索引, 3-bit 行内 word 索引}
               = 组索引 × 8 + 行内 word 索引
标签 SRAM 地址 = 8-bit 组索引
```

每条完整 line 只需一份 tag/valid/dirty，所以 LLC 标签仍为 `256×36 bit`，不随每行的 8 个 word 重复。64-bit word 内的 3-bit 字节偏移用于选择/写掩码，不再增加 SRAM 深度。

**“路数＝bank 数”也不是通用规则。** 当前 L1I、LLC 的数据 bank 按路组织；L1D 则按 32 B 行中的四个 64-bit word 位置分 bank，每个 bank 的一项包含四路各 64 bit：

```text
L1D 的某个组 s：
bank 0[s] = {way3.word0, way2.word0, way1.word0, way0.word0}
bank 1[s] = {way3.word1, way2.word1, way1.word1, way0.word1}
bank 2[s] = {way3.word2, way2.word2, way1.word2, way0.word2}
bank 3[s] = {way3.word3, way2.word3, way1.word3, way0.word3}
             每项 4×64＝256 bit；每 bank 深度 64
```

因此，“每路深度＝组数×每行 word 数”适用于按路存储的组织，不能直接套到这种跨路打包的 L1D bank。具体以 [wt_dcache_mem.sv 的 `gen_data_banks`][dcache-mem]为准。

### Q4.3 端口、写掩码与延迟

Q2 的所有逻辑 SRAM 当前均为 **单端口 1RW、读延迟 1 周期**；这是 SRAM 接口延迟，不是整个 Cache 命中或缺失的总延迟。

- L1I 数据及标签按整个 word 写入；L1D 数据按字节写入、标签整项写入。
- LLC 数据和 VRF 支持字节写掩码；LLC 标签将 tag/valid/dirty 作为整项写入。
- `1RW` 表示一个 bank 的共享读写端口，不等于一个 SoC 只有一个访问者；多个 bank、仲裁和流水线共同服务请求。

Cache 的链路为 `sram_cache → sram_pulp 中的 sram → tc_sram`；LLC/VRF 直接实例化 `tc_sram`。`rst_ni` 端口存在不代表 SRAM 内容能异步清零，初始化和有效位维护仍由上层流程完成。

<a id="q5"></a>

## Q5．TLB、RAS、BTB、BHT 占多少？

下表按当前 ASIC 分支统计数组状态，**不把 RTL 声明位数当作最终触发器数量**，也不含比较器、优先编码和读写控制。

| 结构 | 有效配置项数 | 每项存储字段/位数 | 数组位数 | 当前实现要点 |
| --- | ---: | --- | ---: | --- |
| ITLB | 16 | 通用声明 189 bit；Sv39 功能字段口径见下 | 3024 bit，按声明 | 寄存器＋并行匹配 |
| DTLB | 16 | 同 ITLB | 3024 bit，按声明 | 寄存器＋并行匹配 |
| TLB PLRU | 每个 TLB 一棵树 | 声明 30 bit；16 项树使用 15 个内部节点 | 两份声明共 60 bit | 与上两行条目存储分开计数 |
| Shared TLB 存储阵列 | 关闭 | `UseSharedTlb=0` | 0 | 关闭阵列不代表模块所有控制逻辑消失 |
| RAS | 2 | 返回地址 64＋valid 1＝65 bit | 130 bit | FF 栈 |
| BTB | 32 | 目标地址 64＋valid 1＝65 bit | 2080 bit | FF 表；不额外存一份完整 PC tag |
| BHT | 128 | 2-bit 饱和计数器＋valid＝3 bit | 384 bit | FF 表 |

当前启用压缩指令，每次取指对应两个预测位置，BTB 可看作 16 行×2 项、BHT 为 64 行×2 项；这不把总项数再翻倍。RAS/BTB 使用 CPU 的 64-bit 地址容器，不是 Ara 的 2048-bit 向量长度。

TLB 每项的 **189 bit 通用声明**分解如下：

```text
tags：ASID16 + VMID14 + VPN27 + 页尺寸标记2 + v_st_enbl1 + valid1 = 61 bit
content：PTE64 + GPTE64 = 128 bit
总计：61 + 128 = 189 bit/项
```

当前 H 扩展关闭，VMID、GPTE 等字段没有对应的有效功能状态。若保留完整 64-bit PTE，只按 Sv39 所需字段计算：

```text
ASID16 + VPN27 + 页尺寸标记2 + valid1 + PTE64 = 110 bit/项
```

**110 bit 仍不是综合后 DFF 数。** PTE 内还可能有保留/未消费位，常量传播会继续优化；`_q` 与下一状态 `_n` 也不能算成两份存储。PLRU 的 30-bit 声明与实际 15 节点同样应分开标注，最终以综合结果为准。

按全为 4 KiB 页计算，每个 16 项 TLB 最多同时覆盖 64 KiB 的不同页映射；大页会改变覆盖范围。这是翻译缓存覆盖量，不是数据缓存容量。

出处：[TLB tags/content/PLRU][tlb]、[PTE 定义][mmu]、[Shared TLB 条件生成][shared-tlb]、[frontend 类型][frontend]、[RAS][ras]、[BTB][btb]、[BHT][bht]。这里不采用 `FpgaEn=1` 下的 FPGA RAM 分支来判断 ASIC 实现。

<a id="q6"></a>

## Q6．哪些需要 MemCompiler 宏替换？

**大数据阵列优先映射 SRAM 宏；小状态和需要并行比较/多端口读取的结构按现有寄存器实现综合。** 是否使用宏最终还取决于工艺库提供的尺寸和时序，不由 SystemVerilog 数组语法单独决定。

| 对象 | 当前实现/首选方向 | 不能忽略的条件 |
| --- | --- | --- |
| L1I/D、LLC/SPM 数据 | `tc_sram`，优先映射 SRAM 宏 | 容量、端口、1 周期读延迟、写掩码、时序 |
| L1/LLC 标签及有效/脏位 | 当前也在 `tc_sram` 中 | 47/46/36-bit 特殊宽度；小标签阵列可评估 FF，但不能默认已经是 FF |
| Ara VRF | 每 lane 多个单端口 SRAM bank | 保留分 bank、字节写、时钟使能及访问时序 |
| TLB、RAS、BTB、BHT | 当前 ASIC 分支为 FF 及比较/控制逻辑 | 普通同步 SRAM 不能直接替代并行匹配和现有读时序 |
| GPR/FPR | 当前多端口 FF 寄存器堆 | 若换专用多端口宏，须另做端口、冲突及读写语义适配 |
| CSR、流水线与控制状态 | 标准单元寄存器/组合逻辑 | 常量及未启用功能由综合优化 |
| Boot ROM | 常量逻辑；或后续评估 ROM 宏 | 初始化内容、读延迟和启动可用性 |

不能指望“把 `tc_sram` 加进综合清单”自动生成所需工艺 SRAM。需要选择合法宏并提供适配层及库视图；否则工具可能把大阵列展开为标准单元，产生不可接受的面积/时序结果。

宏适配至少核对：有效电平、读写时序、写掩码粒度、同地址读写行为、使能/时钟门控、上电内容、测试接口，以及仿真模型、Liberty、LEF、MBIST/DFT 配套。例如只能获得 64-bit 宽宏时，47-bit 标签可以有未用位，但那是**物理映射开销**，不改写逻辑需求为 64 bit。48 个逻辑实例也可能因拼接/切分对应不同的物理宏数量。

LLC 源码中的启动 BIST 是现有功能机制，不自动等于已完成工艺宏 MBIST、量产测试或流片验收。进一步要求见 [ASIC 适配与验收证据](ASIC_Adaptation_and_Evidence.md)。

<a id="q7"></a>

## Q7．容量能改吗？哪些参数联动？

**不同 Cache 的容量可以分别配置；同一 Cache 内的容量、路数、组数、行长和 SRAM 形状存在派生关系。** 修改硬件参数需要重新编译/展开或综合，软件运行时不能增加物理容量。

这里“固定”指固定向量功能组合、选中的实现与**每次构建的完整配置**，并不要求删除底层参数化能力。先用当前取值完成参考/提取对照，再按下表逐步开放；后续参数不是默认全部开放。

| 阶段 | 可研究的参数范围 | 保持条件 |
| --- | --- | --- |
| 首次提取 | 当前 L1I 4 KiB、L1D 8 KiB、LLC/SPM 128 KiB、2 lanes/VLEN2048 | 保留地址、中断、外设、启动及原子路径，先证明提取正确 |
| 第一批容量试验 | L1I/D 总容量、LLC 每路行数 | 保持路数、行宽、WT、AXI 位宽及 Ara 配置，先逐项比较 |
| 后续按需开放 | TLB、预测器、队列深度及 VLEN | 先核查合法组合和关联逻辑，再增加定向验证；不因有参数就认定已支持 |
| 单独架构评估 | lane 数、总线宽度、Cache 类型 | 影响并行度、接口或可见性语义，不能混入普通容量调整 |

下文数值是候选算例，支持范围以每个配置的实际验收记录为准。只保留一个当前生效的构建配置，也可以保留基线和候选的配置快照，不需要复制整套工程。

<a id="cache-resize"></a>

### Q7.1 L1I、L1D 与 LLC 扩容

L1 的入口在 [CPU profile][cpu-profile]：

| 参数 | L1I 当前值 | 对应 L1D 参数/当前值 | 单位 |
| --- | --- | --- | --- |
| `CVA6ConfigIcacheByteSize` | 4096 | `CVA6ConfigDcacheByteSize=8192` | B，总数据容量 |
| `CVA6ConfigIcacheSetAssoc` | 4 | `CVA6ConfigDcacheSetAssoc=4` | 路 |
| `CVA6ConfigIcacheLineWidth` | 128 | `CVA6ConfigDcacheLineWidth=256` | bit/行 |

```text
组数 = 总数据容量 / (路数 × 每行字节数)
INDEX_WIDTH = log2(总数据容量 / 路数)  // 包含行内字节偏移
TAG_WIDTH = PLEN − INDEX_WIDTH
```

最直接的容量试验是保留路数和行宽，只增大 `ByteSize`，让 [build_config][cpu-build] 派生索引、标签及数组尺寸，不能仅修改底层 SRAM 参数。以下是未验证的扩容示例：

| 对象 | 容量变化 | 路/行长 | 组数变化 | 数据 bank 变化 |
| --- | --- | --- | --- | --- |
| L1I | 4→8 KiB | 4 路、16 B | 64→128 | 4×(64×128 bit) → 4×(128×128 bit) |
| L1D | 8→16 KiB | 4 路、32 B | 64→128 | 4×(64×256 bit) → 4×(128×256 bit) |

两例的标签深度也加倍，地址 tag 减少 1 bit。**保持总 `ByteSize` 不变而只改路数或行宽，不会扩容，只会改变组数和组织。**

当前 I/D 都有 `INDEX_WIDTH <= 12` 的源码断言，对应 4 KiB 页的索引限制，因此 **每路最多 4 KiB；保持 4 路时总容量最多 16 KiB**。不能直接设成 32 KiB/4 路。增加路数是进一步扩容的候选方法，但要核查替换算法、比较/选择电路及合法参数组合，不意味着任意路数都已支持并验证。断言位于 [cva6_icache.sv][icache] 和 [wt_dcache.sv][dcache] 的参数检查末尾。

LLC 则从 [Cheshire 配置包][chs-pkg]的 `LlcSetAssoc`、`LlcNumLines`、`LlcNumBlocks` 及 AXI 数据宽度计算：

```text
容量 = LlcSetAssoc × LlcNumLines × LlcNumBlocks × AxiDataWidth / 8
当前 = 8 × 256 × 8 × 64 / 8 = 128 KiB
```

保持 8 路、64 B 行长和 AXI64，只增加 `LlcNumLines` 的结构推算如下：

| `LlcNumLines` | 总数据容量 | 每路数据 SRAM | 每路标签 SRAM |
| ---: | ---: | --- | --- |
| 256，当前 | 128 KiB | 2048×64 bit | 256×36 bit |
| 512，候选 | 256 KiB | 4096×64 bit | 512×35 bit |
| 1024，候选 | 512 KiB | 8192×64 bit | 1024×34 bit |

`NumLines`、`NumBlocks` 需为至少 2 的 2 次幂，详见 [LLC 参数定义][llc-top]及[官方说明](https://pulp-platform.github.io/axi_llc/module.axi_llc_top)。保持其余参数不变时，增路数会增加总容量、可分配的 SPM way 数量及比较/选择逻辑，但每 way 的字节数不变；增 `NumBlocks` 会改变行长、回填和驱逐行为；改 AXI 宽度还会影响总线接口。仅为扩容时，增行数比同时改变这些参数更便于隔离影响。

**LLC 扩容同时扩大最大 SPM 容量**，还需复核地址解码、非缓存别名、CPU 区域属性、Boot ROM 自测/栈、运行时 way 分配及链接脚本。当前 SPM 链接预算仍为 64 KiB，RTL 扩容不会自动扩大软件预算；该预算也不表示物理阵列只有 64 KiB。

可以单独扩大一个 Cache，不需要同步扩大其他 Cache 或改变 WT/WB 策略；但不能保证没有新问题。Cache 更大可能降低缺失率，也可能增加读延迟、MUX 路径、功耗或宏适配成本。把 WT 改为 WB 是另一项行为变更，涉及脏数据和设备可见性，不应作为普通容量调整顺带进行。

<a id="vrf-resize"></a>

### Q7.2 VRF 容量由 VLEN 还是 lane 数决定？

当前 Ara 有 32 个架构向量寄存器，每个宽 VLEN bit，分布到各 lane：

```text
VRF 总容量（B） = 32 × VLEN / 8
每 lane 容量（B） = 32 × VLEN / (8 × NrLanes)
当前每 lane 固定 8 bank，每 bank word 宽 64 bit
每 bank 深度 = 32 × VLEN / (NrLanes × 8 × 64)
              = VLEN / (16 × NrLanes)
```

| VLEN | lane 数 | 总 VRF | 每 lane 容量 | 总 bank 数 | 每 bank 深度×宽度 | 状态 |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2048 | 2 | 8 KiB | 4 KiB | 16 | 64×64 bit | 当前基线 |
| 4096 | 2 | 16 KiB | 8 KiB | 16 | 128×64 bit | 结构推算，未验证 |
| 2048 | 4 | 8 KiB | 2 KiB | 32 | 32×64 bit | 结构推算，未验证 |
| 4096 | 4 | 16 KiB | 4 KiB | 32 | 64×64 bit | 结构推算，未验证 |

**固定 VLEN 增加 lane，总 VRF 不变；固定 lane 增加 VLEN，总 VRF 按比例增大。** 增 VLEN 扩大单个寄存器和单条指令的最大元素数，不直接增加运算单元；增 lane 增加并行通路，但速度还受指令、访存和调度限制。

VLEN 和 lane 是构建时硬件参数。运行时 `vsetvl` 改的是有效元素数 `vl`；LMUL 组合既有向量寄存器，都不会增加物理 VRF。例如当前 SEW=64、LMUL=1 时，`VLMAX=2048/64=32` 个元素。

当前 [ara.sv][ara-top]要求 lane 数为 2 的幂且不超过 16，VLEN 为正的 2 的幂并不小于 ELEN；官方 `2_lanes.mk` 还注明 VLEN>128。基本检查不是所有组合的验证保证。[ara_pkg 的 `vaddr()` 注释][ara-pkg]明确提到充分测试的组织保持 **VLEN/NrLanes=1024、每 lane 8 bank**。改变比例时，需要额外验证映射、shuffle、slide、mask、尾部和访存；符合该比例也不能替代本 SoC 回归。

当前 Cheshire 主路径按最终 SoC 配置的 `AraNrLanes/AraVLEN` 实例化 Ara，TB 函数直接写入 2/2048。[Ara 构建配置][ara-config]与[集成 Makefile][ara-make]虽导出 `NR_LANES/VLEN` 宏，单独修改宏不会改变这里的硬件取值。若保留使用这些宏的独立 Ara TB/Spyglass 入口，须把其值与所选配置对齐；不把没有实际消费者的宏当作必需的第二套配置。`VRFSize` 和 bank 深度继续从上层派生，不单独扩大底层数组后宣称 VLEN 已改变。

### Q7.3 修改后需要验证什么？

| 修改对象 | 最小验证关注点 |
| --- | --- |
| L1 容量/组织 | 正确 profile 与派生量；新增索引范围、同组冲突/替换、回填、写掩码及必要维护；D-Cache 写缓冲交互 |
| LLC/SPM | 最大地址及边界、脏行驱逐/flush、Cache/SPM way 分配、启动自测与栈、链接预算；测试时确实启用待验 Cache ways |
| VLEN/lane | 短向量、VLMAX、非整倍数长度；不同 SEW/LMUL、mask、slide、跨 lane 访存及结果比对 |
| 所有容量变更 | 重新编译/展开及宏尺寸核对；定向功能仿真；使用目标宏后的综合、时序和功耗评估 |

只跑一个落在旧容量范围内的小程序，不能证明扩展部分正确；扩容也不等于性能必然提高。这里是后续变更的验证要求，本轮没有实施任何参数调整。

验证分三层，控制试验成本，同时保留验收门槛：

| 层次 | 何时执行 | 能支持的结论 |
| --- | --- | --- |
| 静态核查与编译/展开 | 每个新候选配置 | 参数约束、派生宽度、源码闭包、模型/宏尺寸和实际配置一致；不能称功能通过 |
| 定向功能与应用筛选 | 静态层通过后 | 覆盖本次变化的索引/边界/冲突或向量情况，检查计算结果，再比较工作负载指标 |
| 候选完整回归 | 入选候选及最终组合 | 执行提取规格中的全部已定义测试，包括复位启动、标量、RVV/尾部、访存/原子及独立重建；不能以一个应用替代 |

先做单变量试验定位收益，再验证组合；单项通过不保证组合通过。新增支持的参数若改变硬件行为，应同步增加相应测试，不把旧基线的通过记录自动转给新配置。

<a id="config-management"></a>

### Q7.4 脱离 Bender 后如何保留集中配置？

拟在提取工程 `src/config/` 集中维护以下三类内容；这是待实现组织，不表示当前已存在这些文件：

| 内容 | 职责 |
| --- | --- |
| `cv64a6_imafdcv_sv39_config_pkg.sv` | 保留唯一 `cva6_config_pkg`，固定 ISA/Cache 类型，集中管理允许调整的 L1 等字段 |
| `cheshire_ara_asic_cfg_pkg.sv` | 导出本次唯一生效的 SoC 常量及统一派生类型，固定 Ara 开启，管理 LLC 和获准调整的 SoC 字段 |
| `README.md` | 参数单位、基线、允许范围、联动关系、重做阶段及验证状态；明确候选值与已支持值 |

继续复用 `profile → gen_cva6_cfg() → build_config()` 和 `CHESHIRE_TYPEDEF_ALL`；不手抄第二份 tag、索引或 AXI 位宽。仿真与综合实例化同一 wrapper，TB 读取同一个配置，只管理激励和模型，不再用旧 `SELCFG`/硬编码覆盖硬件取值。

每次构建将所选配置快照留在自己的独立输出目录，记录实际输入；同一次编译只选一份同名配置包。保留原模块/包接口名，不增加 presets 目录或配置生成器。

静态 filelist 可以覆盖参数化模块的容量变化；它不自动覆盖换 Cache 类型、ISA 或技术实现。提取时保留支持范围所需的 generate 分支、package/include 和依赖，不能仅按基线的一次展开结果删掉其他候选需要的源码。目录、来源和清单的具体约束沿用 [02 提取规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)，不另建配置生成框架。

<a id="q8"></a>

## Q8．对最终 SoC v1 是否够用，能否提高性能？

**当前配置可以作为固定参考与提取起点，尚无足够应用数据证明满足最终 v1 性能目标。** 已有服务器标量 HelloWorld、修正 FS 初始化后的单个 32×32 `fmatmul` 运行通过，不能替代产品数据规模、实时期限、缓存压力和多主设备竞争测试；既有证据见 [E01 交接](../handoffs/E01_fixed_vector_extraction.md)。

v1 中 CPU 主要负责控制与调度，Ara 提供向量处理，NPU/ISP 有各自的数据路径。Ara 访存不经过 CPU L1D，规划中的 NPU/ISP 访存绕过 LLC，因此扩大 CPU Cache 不直接解决这些模块的供数问题。独立 GB 的 2 MiB、NPU 的 1024 INT8 MAC 仍是评估起点，不能与当前已经存在的 LLC/VRF 混成一份已实现资源表。依据：[v1 总纲](SoC_Architecture_v1_Master_Plan.md)、[资源与封装预算](SoC_Resource_and_Packaging_Plan.md)。

| 对象 | 候选变化，具体数值均未验收或选定 | 有收益的前提/主要代价 |
| --- | --- | --- |
| L1I | 4→8/16 KiB，保持 4 路 | 代码工作集缺失显著；核对 SRAM 时序与取指路径 |
| L1D | 8→16 KiB，保留 WT | 数据重用能减少读缺失；不能据此消除 WT 写流量 |
| LLC/SPM | 128→256/512 KiB | 需要更多片上驻留数据，或确实启用 Cache 且有复用；同步审查 SPM/启动 |
| RAS/BTB/BHT | 例如 2→8/16、32→128、128→512 项 | 有返回/分支预测损失；更大表需合法性及时序检查 |
| ITLB/DTLB | 各 16→32/64 项 | 页工作集和实际 TLB 缺失值得优化；增加并行比较开销 |
| VRF | VLEN 2048→4096，容量 8→16 KiB | 更长向量/寄存器驻留有收益；不直接翻倍算力，保存恢复成本增加 |
| Ara lanes | 2→4，固定 VLEN 时 VRF 总量不变 | 有可利用并行度且访存能供数；运算、互连和功耗增加，属于 v1 基线之外的候选 |

优先用实测定位：L1/LLC 缺失、TLB 缺失、分支误预测、写缓冲等待、Ara 访存等待、GB/DDR 服务带宽及端到端完成时间；指标采集须核对当前计数器和接口实际支持范围。随后比较目标 SRAM 宏与综合时序，不能仅凭峰值 MAC、KiB 或“看到波形活动”决定扩容。

当前实施顺序仍是先保留既定 2 lanes/VLEN 2048 和 Cache/LLC 配置，完成参考对照与独立提取，再将性能改动作为有单独输入、回归和结果对比的配置版本。

<a id="application-comparison"></a>

### Q8.1 如何让应用比较有意义？

先选有明确结果检查、能代表目标工作量的程序，再逐步加入真实规模和并发流量；`fmatmul` 可作为向量计算起点，但不能单独代表控制代码、随机访存或图像/NPU 系统负载。

- **软件输入一致**：记录源码版本、编译器/选项、ELF 哈希和输入数据/规模。同一 ELF 能合法运行时优先复用；因 VLEN 假设或链接布局必须重编时，记录差异，避免同时改变算法而把收益归给硬件。
- **存储条件一致**：记录代码/数据/栈所在区域、链接布局、CPU 区域属性、LLC Cache/SPM way 分配、外部内存模型及延迟/带宽。只改容量而让数据从 DDR 移到 SPM，应作为另一种布局方案单独报告。
- **冷热状态明确**：冷启动或经过明确预热后计时，预热次数、初始化及计时边界保持一致；不能将一次冷缺失与另一次热命中混为容量收益。
- **时间口径明确**：分别记录内核和端到端目标 cycles；后者说明是否含初始化、搬运和结果比较。在固定目标频率下换算时间，另列各候选经目标工艺实现可达到的频率；VCS 的主机 CPU Time/墙钟时间只是仿真成本，不是芯片性能。
- **先看正确性，再看收益**：保存数值比较、程序返回、TB 结束及退出状态；记录缺失/等待/带宽指标的采集方法与支持范围，不凭一个更小的 cycles 数判定配置成功。

**LLC 比较尤其要先检查运行时模式。** 当前 Boot ROM 默认全 SPM；这种状态下扩大阵列测试的是 SPM 容量，不是 LLC 缓存命中收益。研究 LLC Cache 时必须显式启用待验 Cache ways，并保证栈/活跃数据不会被切换方式破坏；逐项记下 Cache 和 SPM 的实际字节数。若改变行数导致两者同时增大，也应说明这一联动。

每个候选可用一张小表记录，不需要新增数据库或脚本框架：

| 记录项 | 必填内容 |
| --- | --- |
| 身份与变量 | 配置名、源码/配置快照、相对基线改了什么；单变量或组合 |
| 软件与存储 | ELF/编译选项、输入、链接布局、Cache/SPM 分配、冷热状态、内存模型 |
| 功能与性能 | 验证层次、结果/退出状态、计时区间、目标频率、内核/端到端 cycles、原始日志位置 |
| 物理实现 | 工艺库/角、SRAM 宏与尺寸、时序约束、面积分类、可达频率、功耗估算及证据状态 |
| 结论 | 保留/淘汰/待验证及理由；未关闭问题和复现实验输入 |

<a id="area-tradeoffs"></a>

### Q8.2 面积小或 cycles 少，是否就应该采用？

不能只按一个数值排序。比较时固定综合工具、目标库/角、约束和优化条件，区分下列口径：

| 口径 | 用途与限制 |
| --- | --- |
| RTL 逻辑位数/SRAM 形状 | 早期预算；本文资源表采用此口径，不等于宏面积 |
| 通用存储模型综合结果 | 仅作注明模型的探索；大阵列若展开为标准单元，不能与映射 SRAM 宏后的结果直接比较 |
| 目标宏＋标准单元面积 | 按实际可生成的尺寸、拼接、掩码及接口计算；标准单元与宏面积分别列出，并避免重复统计 |
| 布局与性能约束 | 加入宏周边、布线、利用率、时钟/测试结构及功耗；面积能放下也不证明可达所需频率 |

更大 Cache 可能减少 cycles，却因 SRAM/选择路径变长而降低可达频率；评估应同时看目标完成时间、面积和功耗。功耗估算注明电压、频率与活动来源，没有相同活动条件就不作精确优劣结论。

如果实际 IO、宏布局和封装评估确认裸片主要受 Pad 周长限制，并且留出必要物理实现空间后仍有余量，可以放宽内部资源面积预算，评估更多 SRAM 或运算单元能否在不增加裸片尺寸的前提下提高应用性能。但新增资源仍消耗动态/漏电功耗、供电和布线能力，可能增加电源地连接及测试成本；WireBond Pad 多本身不等于已经获得可用面积或供电余量。

最终还要为新增 IP、DFT、时钟、供电、布线和实际 Pad/封装约束留余量；不能因核心区暂有空白就默认全部用于扩容。当前尚无目标宏/物理实现签核结果，先保留在性能、面积、功耗上各有优势的候选，再根据产品期限和资源预算选定，不把候选算例变成承诺。

## 来源定位与维护

源码链接指向当前仓库文件，查找符号比长期依赖固定行号更稳妥：

| 需追踪的事实 | 文件与定位符号 |
| --- | --- |
| 容量、profile、禁用项 | [CPU profile][cpu-profile]：`CVA6Config*`；[Cheshire][chs-pkg]：`DefaultCfg/gen_cva6_cfg/get_llc_size` |
| 位宽派生 | [build_config_pkg][cpu-build]：`ICACHE_INDEX_WIDTH/DCACHE_INDEX_WIDTH/PLEN` |
| Cache 实际 SRAM | [I-Cache][icache]：`gen_sram`；[D-Cache][dcache-mem]：`gen_data_banks/gen_tag_srams` |
| 技术单元选择 | [Bender][cva6-bender]：`sram_pulp.sv`；[sram_cache][sram-cache]：`TECHNO_CUT`；[sram_pulp][sram-pulp]：`i_tc_sram` |
| LLC 结构 | [top][llc-top]：`Cfg`；[data way][llc-data]：`i_data_sram`；[tag store][llc-tag]：`tag_data_t/i_tag_store` |
| VRF 结构与约束 | [lane][lane]：`VRFSizePerLane`；[vector_regfile][vrf]：`NumWords/data_sram`；[ara_pkg][ara-pkg]：`NrVRFBanksPerLane/vaddr` |
| TLB/预测器 | [TLB][tlb]：`tags_q/content_q/plru_tree_q`；[frontend][frontend]：`ras_t/btb_prediction_t`；[BHT][bht]：计数器和 valid |
| 寄存器/CSR | [issue_read_operands][regfile-inst]：`i_ariane_regfile/i_ariane_fp_regfile`；[perf][perf]：`generic_counter_q/mhpmevent_q`；[dispatcher][ara-dispatcher]：`csr_vl_q/csr_vstart_q/csr_vtype_q` |
| ROM/启动/链接 | [ROM][bootrom-rtl]：`NumWords`；[启动汇编][bootrom-start]：`_wait_llc_bist`；[链接定义][link-common]：`MEMORY` |

维护时重新核对选入的实现和最终配置；不要把其他 profile、FPGA 分支、未生成模块或仿真镜像数组加入统计。本文表格、算例和链接的检查属于文档/静态检查；没有综合后总面积、完整 CSR 清单、最终 SRAM 宏选型或扩容仿真结果。

[cpu-profile]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/cv64a6_imafdcv_sv39_config_pkg.sv
[cpu-build]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/build_config_pkg.sv
[chs-pkg]: ../../hw/cheshire_pkg.sv
[chs-soc]: ../../hw/cheshire_soc.sv
[tb-cfg]: ../../target/sim/src/tb_cheshire_pkg.sv
[cva6-bender]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/Bender.yml
[icache]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/cva6_icache.sv
[dcache]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/wt_dcache.sv
[dcache-mem]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cache_subsystem/wt_dcache_mem.sv
[sram-cache]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util/sram_cache.sv
[sram-pulp]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/common/local/util/sram_pulp.sv
[llc-top]: ../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_top.sv
[llc-data]: ../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_data_way.sv
[llc-tag]: ../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/hit_miss_detect/axi_llc_tag_store.sv
[llc-doc]: ../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/doc/axi_llc.md
[regfile-inst]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/issue_read_operands.sv
[regfile-ff]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/ariane_regfile_ff.sv
[cpu-csr]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv
[perf]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/perf_counters.sv
[ariane-pkg]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/ariane_pkg.sv
[ara-dispatcher]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_dispatcher.sv
[rvv-pkg]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/rvv_pkg.sv
[ara-pkg]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/ara_pkg.sv
[ara-top]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara.sv
[lane]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/lane.sv
[vrf]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vector_regfile.sv
[ara-config]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/config/2_lanes.mk
[ara-make]: ../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile
[tlb]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cva6_mmu/cva6_tlb.sv
[mmu]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cva6_mmu/cva6_mmu.sv
[shared-tlb]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/cva6_mmu/cva6_shared_tlb.sv
[frontend]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/frontend/frontend.sv
[ras]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/frontend/ras.sv
[btb]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/frontend/btb.sv
[bht]: ../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/frontend/bht.sv
[bootrom-rtl]: ../../hw/bootrom/cheshire_bootrom.sv
[bootrom-start]: ../../hw/bootrom/cheshire_bootrom.S
[link-common]: ../../sw/link/common.ldh
