# CPU–NPU 缓存一致性：工业实现与学术方案

返回[工程参考](README.md) · 项目方案：[DDR–GB 缓存一致性](Cache_Coherence_Architecture.md) · [IP／DDR／GB 契约](IP_DDR_Interface_Contract.md)

2026-10-16，L01。本文选取七组有公开依据的代表案例，面向架构学习与评审。外部资料分别标注版本；项目对照基于 `mp/ara-pulp-v2` / `322bd6ce9`，本轮完成资料与源码核对。

**CPU 与 NPU 共享数据时，一致性是常见的系统集成问题。成熟方案既包括任务交接时的软件维护，也包括逐次访问的硬件协调。选择依据是共享粒度、数据复用和并发需求。** 对采用独立 SRAM 的 NPU，系统内存访问可以具有硬件一致性，本地计算数据仍按任务显式装入和复用。这两个机制可以配合使用。

**当前项目规划采用“软件交接＋硬件范围维护”：L1D／LLC 均纳入维护，缓存与 GB 的数据统一经 DDR 交换。** 它在维护方式上接近下文 B，在数据拓扑上沿用 E 的设备旁路。此前优先评估的逐事务 I/O 一致性继续作为比较对象；缓存直接供数只用于成本分析，F 类设备私有一致性缓存退出项目候选。具体交接流程、接口与开销见[现行规划](Cache_Coherence_Architecture.md)。

## 1. 先沿一次推理看清问题

CPU 预处理图像时，新像素可能还在写缓冲或脏缓存行中。NPU 的 DMA 若直接读取 DDR，就可能取得上一版本。计算结束后，NPU 将结果写回系统内存，CPU 又可能命中自己的旧副本。因此，一次推理需要完成两次可靠交接：**提交任务前，设备能取得准备好的输入；发布完成后，CPU 能取得设备生成的结果。** 部分行写入还须保留同一行中其他字节的最新值，相关机制见[项目条件审查](Cache_Coherence_Architecture.md)。

分析一个方案时，建议分别回答三个问题：

| 判断维度 | 要问的问题 | 对架构的影响 |
|---|---|---|
| 一致性覆盖范围 | 哪些 CPU／设备缓存由硬件查询、供数和失效？剩余部分由谁维护？ | 决定软件交接动作和硬件探测职责 |
| 缓存分配策略 | 设备访问是否新分配 LLC 行？已有脏行如何参与？ | 决定复用收益、缓存污染和 DDR 流量 |
| 本地存储语义 | NPU SRAM 是独立 Scratchpad，还是同一物理地址的缓存？ | 决定显式搬运、数据保留及副本管理方式 |

例如，DDR 地址 A 搬到 GB 地址 G 后，G 保存该次任务取得的内容。CPU 随后更新 A，下一任务若需要新值，就再次装入 G；当前任务则可以继续使用自己的输入版本。缓存协议负责系统地址 A 的访问，任务调度负责 G 的生产、消费与复用。图像双缓冲、分块流水正是利用这种明确的生命周期，让多个部件并行工作。

软件还要分别处理**地址、数据和任务**：IOMMU／SMMU 负责设备地址翻译与访问权限；缓存维护或一致性互连负责数据可见性；屏障、描述符、门铃和完成事件建立执行先后。Linux DMA API 将前两类平台差异封装给驱动，驱动仍需按设备协议提交任务和等待完成。[Linux 6.5 DMA 指南](https://docs.kernel.org/6.5/core-api/dma-api-howto.html)

## 2. 用同一布局比较机制与项目候选

![Cohmeleon 原文：四种加速器存储访问模式](../diagrams/2026-10-16_coherence_survey/previews/cohmeleon-modes.png)

图 1：Zuckerman 等，*Cohmeleon*（MICRO 2021，arXiv v1），原文 Fig. 1。沿彩色连线观察设备访问进入哪一级存储；带独立 cache 的设备另列一类。图中 local mem 对应显式管理的本地存储。[原文](https://arxiv.org/html/2109.06382v1#S1.F1) · [原始 SVG](../diagrams/2026-10-16_coherence_survey/originals/cohmeleon-modes.svg)

下面把论文四类模式展开成六个工程示例：加入软硬件协同的范围维护 B，并把 I/O 一致性按分配策略拆成 D／E。三张对比图保持模块位置一致，绿色表示设备数据路径，紫色表示维护、探测和确认。左侧 L1／L2 泛指 CPU 私有缓存，LLC 单列为系统侧缓存；各芯片实际层数不同。这些图解释机制，项目完整互连及 DDR 三个 AXI 入口仍以[现行架构图](Cache_Coherence_Architecture.md)为准。[ESP 2018 论文](https://www.cs.columbia.edu/~davide_giri/pdf/giri_nocs18.pdf)、[Cohmeleon §2](https://arxiv.org/html/2109.06382v1#S2)

![对比一：软件维护与搬运边界硬件维护](../diagrams/2026-10-16_coherence_hybrid/previews/handover.png)

**对比一：A 与 B 改变“谁执行维护”，都在任务边界交接缓冲区。** A 的驱动维护 CPU 私有缓存和 LLC，然后让 DMA 直访 DDR；B 新增硬件维护／准入引擎，执行排空、清理、失效并返回确认。两者在传输期间都需保持交接范围的所有权，CPU 可继续处理其他区域。B 由软件发起范围请求，硬件执行和汇合确认，是本项目采用的维护方向。软件约束范围访问；若另加硬件违规访问阻挡，还需覆盖 L1 命中路径。Ethos-U 是 A 的软件契约实例。

![对比二：LLC 局部协调与覆盖 CPU 缓存的 I/O 一致性](../diagrams/2026-10-16_coherence_hybrid/previews/coverage.png)

**对比二：C 与 D 改变“硬件负责哪些副本”。** C 按 ESP 的 LLC-coherent DMA 定义，只在 LLC 层协调，驱动仍维护 CPU 私有缓存。D 把私有缓存也纳入硬件探测，冲突在事务级排序；图中选择允许设备分配 LLC 行，便于 CPU 与设备复用刚访问的数据，同时带来容量与替换竞争。D 属于 coherent DMA，具体分配行为取决于系统实现。它相对 C 增加探测响应、在途访问管理及更多并发验证组合。

![对比三：I/O 一致性的分配策略与设备私有缓存代理](../diagrams/2026-10-16_coherence_hybrid/previews/agent-types.png)

**对比三：E 比较分配策略，F 比较设备是否拥有可探测的缓存。** E 与 D 都在事务级协调 CPU 私有缓存和 LLC，E 让设备访问不分配 LLC 行，以降低缓存容量竞争。本项目沿用其旁路数据拓扑，维护则放到软件交接点。F 增加同地址设备私有缓存，需要探测、供数和权限转移；本项目的独立 GB 采用显式搬运，F 留作文献分类。接到 L2 的 DMA 与设备私有缓存是不同对象，Gemmini 的 Scratchpad 不能仅因 L2 接入位置归入 F。

AMD HPC／ACP 可分别帮助理解 E／D 的能力差别，但其比较对象是该平台的 CPU L2；图中的通用 LLC 用于表达系统角色。Ethos-N 的 ACE-Lite 接口支持 I/O 一致性方向，公开简报尚不足以判定其具体分配策略。[AMD PG201 端口表](https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface) · [当前图稿与可编辑 PPTX](../diagrams/2026-10-16_coherence_hybrid/README.md)

**软件维护的核心是交接所有权。** CPU 准备输入后，将脏数据清理到设备可见点，再发布任务；设备写入前也要处理目标范围的旧脏副本，避免它们稍后覆盖结果。设备完成后，CPU 按平台要求失效旧副本并读取。维护范围按缓存行隔离，可以保护与缓冲区相邻的对象。传输期间，CPU 可处理其他任务，但交接区内的冲突访问要由调度约束。

**硬件一致性把上述协调细化到访存事务。** 一次设备读可以由持有最新数据的缓存供数；一次写则协调旧副本、在途访问及必要的权限。ACE-Lite 的 `ReadOnce`、`WriteUnique`、`WriteLineUnique` 为这类设备访问提供标准语义。互连和缓存侧执行这些职责，DDR 控制器可以承接普通内存事务。完整行覆盖与部分写对旧数据的需求不同，协议选择和字节有效掩码必须匹配。[Arm IHI 0022H，D3／D6／D11](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)

硬件维护副本后，软件依然通过发布与完成同步表达任务依赖。若一个结果占据多行，整帧交接可使用双缓冲或完成标志；这样 CPU 在设备写入过程中还能安全处理另一帧。

这些模式对应不同的共享习惯。只读取一次的大权重块，更关注持续带宽和较低的缓存占用；CPU 刚生成的小输入，可能受益于从片上缓存取得数据；频繁交换的小型控制结构，则更看重低延迟和细粒度同步。同一个 NPU 也可能同时出现三种流量。工程上可先按输入、输出、权重和控制结构分别描述访问者、复用次数与交接时机，再确定各类流量的属性，避免用一个缓存开关承担全部策略。

## 3. 工业界怎样落地

### 3.1 Arm Ethos-U：把维护放到推理交接处

Arm 官方驱动的 `Data caching` 章节给出了直接的软件契约：应用在调用推理前完成 clean／flush；启用数据缓存的平台实现 `ethosu_invalidate_dcache`，由驱动在推理完成后调用。旧的 `ethosu_flush_dcache` 钩子已标为 deprecated。本文固定到提交 `9a825eec770d`，以这一修订的接口说明为准。[驱动原文](https://github.com/ARM-software/CMSIS-Ethos-U/blob/9a825eec770dac8987ffb7703aadc34753720f2d/source/README.md#data-caching)

这类做法适合输入、输出边界明确的推理任务。平台可以保留 CPU 日常缓存能力，只维护交接缓冲区。主要成本来自维护范围和调用频率：小任务可能被交接开销主导，大任务则通常有更多计算可摊薄成本。驱动要求缓冲区按缓存行对齐，并按 base pointer 范围维护；因此内存分配器也参与正确性设计。应用调度还需保证推理期间输入稳定、输出由设备独占写入。

### 3.2 Arm Ethos-N：通过 ACE-Lite 进入一致性系统

Arm 2020 年 Ethos-N 系列产品简报列出 ACE-Lite 主接口及可选 SMMU 集成，接口表标注 ACE-5 Lite。这提供了另一条产品路线：NPU 的系统内存请求进入能协调 CPU 缓存的一致性基础设施，同时利用片上 SRAM 和算子级联减少外部搬运。[产品简报，2020](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/AI-ML%20Datasheet%20and%20briefs/Arm%20Ethos-N%20Product%20Brief%20-%20May%202020.pdf)

集成方需要配齐互连、缓存响应能力和共享属性，软件负责缓冲区与任务同步。简报能够确认产品接口方向；具体事务集合、系统缓存分配及共享原子能力，仍需对应型号的 TRM 和集成手册确认。对本项目有价值的经验是：**本地 SRAM 的计算效率与系统侧硬件一致性，可以在同一 NPU 中同时实现。**

### 3.3 AMD Zynq UltraScale+：把多种路径做成明确端口

AMD PG201 v3.5 的接口表把几种选择放在同一个 SoC 中，尤其适合对照“设备旁路又保持 CPU 缓存”的需求：[官方端口表](https://docs.amd.com/r/en-US/pg201-zynq-ultrascale-plus-processing-system/Slave-Interface)。

| PL 发起访问所用端口 | 官方定义的能力 | 适合比较的设计目标 |
|---|---|---|
| HP | 非一致性路径，到主交换网络和 DDR | 大块搬运，由软件维护共享缓冲区 |
| HPC | 经 CCI 提供 I/O 一致性；不分配 CPU L2 行 | 获取正确数据，同时降低设备流量对 CPU 缓存驻留的影响 |
| ACP | I/O 一致性，并分配 L2 行 | CPU 与加速器近期会复用同一批数据 |
| ACE | 双向一致性路径 | PL 中存在需要被探测的缓存代理 |

这里的“不分配 L2”描述新行的分配策略；HPC 仍通过一致性基础设施处理已有 CPU 副本。这正好说明缓存污染与数据正确性可以分别设计。实际使用时，还需启用 CPU 侧 snoop，并使事务属性满足该平台的一致性条件；AMD 官方示例给出了配置和传输测试。[AMD 一致性示例](https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/18842098/Zynq+UltraScale+MPSoC+Cache+Coherency)

### 3.4 NVDLA：NPU 本体与存储系统各负其责

![NVDLA 官方系统接口图](../diagrams/2026-10-16_coherence_survey/previews/nvdla-system.png)

图 2：NVIDIA，NVDLA v2 *Integrator’s Manual* 的 System Diagram 原图。CPU 通过控制接口配置任务，DBBIF／SRAMIF 分别服务系统内存与片上 SRAM，完成状态通过中断交接。[原文](https://nvdla.org/hw/v2/integration_guide.html#system-diagram) · [原始 PNG](../diagrams/2026-10-16_coherence_survey/originals/nvdla-system.png)

NVDLA 的主存接口通常连接 DRAM，可选次级接口连接低延迟 SRAM。包含 Bridge DMA 的 v1 设计还能在两类存储之间显式搬运。SRAM 为计算提供带宽，系统侧则决定共享数据怎样与 CPU 缓存协调。[集成手册](https://nvdla.org/hw/v2/integration_guide.html#system-data-interfaces-dbbif-and-sramif)、[v1 Bridge DMA](https://nvdla.org/hw/v1/ias/unit_description.html#bridge-dma)

因此，复用 NVDLA 时应分三层阅读：NPU 本体产生读写与完成事件；SoC 选择普通或一致性接入路径；驱动采用该平台的 DMA 映射、同步和所有权协议。不同配置提供的 SRAM 接口和搬运单元要逐项核对。对自研 NPU／GB，这种职责划分比“支持 AXI4”更能说明集成工作量。

## 4. 开源与学术界怎样扩展这些方案

### 4.1 Gemmini：Scratchpad 与主机一致性层次配合

![Gemmini 论文系统架构原图](../diagrams/2026-10-16_coherence_survey/previews/gemmini-system.png)

图 3：Genc 等，*Gemmini: An Agile Systolic Array Generator Enabling Systematic Evaluations of Deep-Learning Architectures*，arXiv `1911.09925v2`，Fig. 1。观察 CPU、共享 L2、DMA 和 Scratchpad 的连接；本地数据由搬运指令管理。[原文](https://arxiv.org/html/1911.09925v2#S2.F1) · [原始 SVG](../diagrams/2026-10-16_coherence_survey/originals/gemmini-system.svg)

Gemmini 的 DMA 在主存与本地 Scratchpad／Accumulator 之间搬运，默认经 System Bus 连接 L2。为确认具体系统，本文检查了 Chipyard **1.11.0 的 `GemminiRocketConfig`**：它采用 `DefaultGemminiConfig`，继承的 `AbstractConfig` 启用 `WithInclusiveCache` 和 `WithCoherentBusTopology`。对应 Gemmini 子模块为 `8c8b38b9dea3`，DMA 声明读、写 TileLink 客户端。[配置入口](https://github.com/ucb-bar/chipyard/blob/1.11.0/generators/chipyard/src/main/scala/config/RoCCAcceleratorConfigs.scala)、[缓存与总线配置](https://github.com/ucb-bar/chipyard/blob/1.11.0/generators/chipyard/src/main/scala/config/AbstractConfig.scala)、[DMA 源码](https://github.com/ucb-bar/gemmini/blob/8c8b38b9dea3e4d6ba9695346a883b2094bd7388/src/main/scala/gemmini/DMA.scala)

这条配置链把 DMA 接入主机的一致性缓存层次，协调服务由系统提供。本地 SRAM 则保留显式副本语义，计算与搬运可重叠执行。迁移这一思想时，需要保留请求到一致性管理点的完整连接；若改成独立 DDR 旁路，就应重新定义共享契约。此处为配置静态核对，尚未展开或运行该参考系统。[Gemmini 维护者说明，固定提交](https://github.com/ucb-bar/gemmini/blob/2c98ce3ec634b1d0995080d040aaa32980c0cc12/README.md#architecture)

### 4.2 ESP／Cohmeleon：按任务和竞争情况选择模式

ESP 将加速器封装为可接入多种存储路径的 tile。早期研究比较非一致性、LLC 一致性与完整一致性，发现大块流式访问、LLC 内复用和设备私有缓存内复用分别可能偏好不同模式。它的价值是将选择落实到可配置硬件和驱动，并通过 FPGA 实验比较。[ESP，NOCS 2018](https://www.cs.columbia.edu/~davide_giri/pdf/giri_nocs18.pdf)

Cohmeleon 在具备四种模式的 ESP 上进一步按每次调用选择路径：观察负载与并发状态，选择模式，再用执行时间和片外访问计数反馈学习。采用这一方法的前提是硬件已经支持各条路径，并能在切换时完成必要维护。[Cohmeleon，§4](https://arxiv.org/html/2109.06382v1#S4)

![Cohmeleon 多加速器并发实验原图](../diagrams/2026-10-16_coherence_survey/previews/cohmeleon-concurrency.png)

图 4：Cohmeleon Fig. 3，蓝柱为执行时间，红柱为片外访问量，均越低越好。实验采用约 256 KB 负载，FFT、Night-vision、Sort、SPMV 各三个实例，比较 1／4／8／12 个并发；各类结果先相对各自“单实例、非一致性 DMA”归一化，再取平均。缓存配置为 32 KB 私有缓存、1 MB 分区 LLC。该图衡量混合加速器竞争。[原文 §3](https://arxiv.org/html/2109.06382v1#S3) · [原始 SVG](../diagrams/2026-10-16_coherence_survey/originals/cohmeleon-concurrency.svg)

图中的模式排序随并发情况变化。工程上应同时测量单任务收益和共享资源竞争，再决定是否值得增加多路径选择；动态策略还需要计数器、切换协议和足够稳定的收益。

### 4.3 Spandex／细粒度特化：按访问选择一致性行为

Spandex 的后续细粒度研究把选择推进到单次请求：读操作可采用共享权限或同步点自失效，写操作可获取所有权或写直达，并研究向已有持有者转发更新。其出发点是根据复用与通信方向支付相应的协议成本。[Alsop 等，*A Case for Fine-grain Coherence Specialization in Heterogeneous Systems*，2021 v1](https://arxiv.org/html/2104.11678v1)

该文用 CPU–GPU 模拟系统评估，依赖无数据竞争的同步约定；访问类型选择还使用执行轨迹分析。借鉴到 NPU 时，需要硬件支持相应请求、软件或编译器提供可靠的访存信息，并验证同步与协议正确性。它为未来多代理共享提供研究思路，适用性要通过 NPU 负载重新评估。

## 5. 对 Cheshire＋CVA6＋Ara＋GB 的启示

当前向量 profile 的 **WT L1D 保留读副本和写缓冲，LLC 为 WB**；Ara 已有专用失效与顺序配合，LLC 维护主要按 way 组织，相关符号和版本见[源码依据](Cache_Coherence_Architecture.md#evidence)。当前规划采用独立 GB、设备 DDR 旁路和软件触发的范围维护。

从这些案例中，本项目主要借鉴三项机制：任务交接时显式同步、缓存侧可靠维护与完成确认，以及独立 SRAM 的分块复用。软件提交地址、长度和方向；硬件排空相关写，维护 L1D／LLC，再开放设备搬运。输入 clean 到 DDR；输出写前 clean＋invalidate、写后 invalidate。软件维持缓冲区所有权，CPU 可处理其他缓冲区，GB 内的 Ara／NPU 消费由本地任务协议组织。

这类选择减少了对持续逐事务探测的需求，同时保留 CPU 日常缓存。代价集中在交接时的 tag 端口竞争、脏写回和失效后重填。当前 L1D 的外部失效按索引清除全部 way，LLC 的 way 维护会隔离入口；把它们改进为范围维护并给出可靠完成确认，是具体实现中的主要工作。

![本项目经 DDR 的路径及缓存直供成本比较](../diagrams/2026-10-16_coherence_hybrid/previews/data-paths.png)

**路径比较：左侧为当前规划，右侧为成本参照。** LLC 持有最新脏行时，左侧先 clean 到 DDR，再经搬运器与共享数据代理送入 GB。右侧直接从缓存取得数据，可减少当次 DDR 往返，但需要新增缓存数据响应、仲裁与背压路径。本项目采用左侧，维护控制仍覆盖 L1D 和 LLC。若 DDR 已最新，直接读取；若先行 CPU 写尚在途，则先处理相关写缓冲和回填。

软件范围交接与逐行透明 I/O 一致性可以使用相近的数据路径，其区别在于谁保证传输期间的访问纪律。当前方案由软件保持交接范围所有权，硬件完成同步操作。只在同步点维护的实现，应按显式同步的设备契约接入驱动。后续若需要 CPU 与设备任意细粒度共享，再单独评估事务级保护和原子域。

评估负载至少包含 CPU 预处理后立即提交、NPU 连续读取大权重、ISP 写帧同时 CPU／Ara 处理另一帧，以及 CPU 修改部分行后设备更新其他字节。每组记录 **CPU 停顿与维护时间、DDR 读写字节、LLC 命中与替换、设备吞吐及多设备尾延迟**；同时比较冷数据、缓存已有输入、整模型同步和分块同步。

测量时拆开准备、维护、等待、搬运、计算和完成交接。计算占主导时，降低维护成本的收益可能有限；搬运受限时，则需观察 DDR 竞争和双缓冲重叠。性能评估以读取版本、部分写保护及迟到事务处理正确为前提。正式流程、接口职责和验收项集中在[软硬件协同维护规划](Cache_Coherence_Architecture.md)，四张原文配图来源见[资料清单](../diagrams/2026-10-16_coherence_survey/README.md)，本轮更新图稿见[图稿目录](../diagrams/2026-10-16_coherence_hybrid/README.md)。
