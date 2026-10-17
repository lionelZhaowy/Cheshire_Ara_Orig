# CPU 接入 Global Buffer：方案比较与连接设计

2026-10-15，L01 分析与图稿交付。输入：`mp/ara-pulp-v2` / `322bd6ce964c96cd4337ceb98e5ce89d1bb478d8`。本页交付方案说明，不实施 RTL、软件或地址配置；CPU 是否接入仍待架构评审确认。

配套：[IP/DDR/GB 契约](IP_DDR_Interface_Contract.md) · [DDR–GB 缓存一致性](Cache_Coherence_Architecture.md) · [原集成导航](../software/interfaces/markdown/integration.md#accelerators) · [图稿与复现说明](../diagrams/2026-10-15_global_buffer_cpu_access/README.md) · [两页可编辑 PPTX](../diagrams/2026-10-15_global_buffer_cpu_access/export/diagrams.pptx)

## 1. 结论与适用场景

用户选择的近期场景是：**NPU/Ara 先缩减数据，CPU 对少量候选结果、索引做排序和灵活后处理。** 对此建议保留 CPU 的 64-bit GB 访问通路，将它作为辅助入口；少量字段可直接读取，反复排序时优先复制到 CPU 私有工作区。

这个选择的价值是减少结果交接环节、提高算法和调试的灵活性，不能仅凭结构图承诺性能提升。用户本轮确认的是分析、Markdown 与图稿交付，不是冻结 CPU 接入、GB 参数或实施硬件。

“CPU 直接访问”指 CPU 执行普通 load/store 即可访问 GB 地址。它可以经过既有主 Xbar 和外部 AXI 从设备出口，**不要求给 CVA6 增加专用 SRAM 端口，也不要求把主 Xbar 加宽。** 新入口是 GB 的逻辑访问口，不自动增加 SRAM 宏的物理端口。

本页沿用已确认边界：主 Xbar 保持 64-bit；GB 是独立片上 SRAM；DDR 与 GB 显式搬运；NPU 的 DDR 数据流绕过 LLC。Ara 的 GB 支路仍为候选，当前生产源码没有这条分流。

## 2. 当前源码与官方复用路径

Cheshire 随附的[集成说明](../../docs/tg/integr.md)和[架构说明](../../docs/um/arch.md)提供外部 AXI/Reg 扩展机制；[上游官方说明](https://github.com/pulp-platform/cheshire/blob/main/docs/um/arch.md)用于核对机制，不以最新上游替代本地实现。

| 对象 | 定义 → 实例化/连接 → 实际消费者 | 本次结论 |
|---|---|---|
| CPU 可达的外部存储 | `cheshire_pkg::AxiExtNumSlv/NumRules/Region*` → `gen_axi_out()` → `cheshire_soc::gen_ext_axi_slv` / `axi_ext_slv_req_o/rsp_i` | 可将 GB 作为主 Xbar 的独立目标；不是把 NPU 数据主口接回 LLC 上游 |
| 当前 Ara 路径 | `AraDataWideWidth = 32 * Cfg.AraNrLanes` → `i_ara_axi_inval_filter` → `i_ara_axi_dw_converter` → `axi_in_req[AxiIn.ara]` | 拟议分流放在过滤器之后、收窄之前；普通支路继续原连接 |
| CPU 属性 | `gen_cva6_cfg()` → cached / non-idempotent / execute 区域 → CVA6 cache 与 load 单元 | 地址译码与缓存/执行属性不是同一配置，不能只增加 Xbar 窗口 |
| 普通主存和 SPM | `gen_axi_out()` → `gen_llc_atomics` → LLC/SPM / 外存出口 | GB 新目标不自动继承此处的原子支持；SPM 仍依赖 LLC 阵列 |
| 主设备可达性 | `i_axi_xbar.Connectivity = '1` → 所有主设备共享目标译码 | 新窗口不天然限定为 CPU 专用，还需审查 DMA、调试和外部主设备 |

源码入口：[cheshire_pkg.sv](../../hw/cheshire_pkg.sv)、[cheshire_soc.sv](../../hw/cheshire_soc.sv)。本地依赖采用路径快照，源版本记录为 Ara `2895ba90`、CVA6 `99eac9a6`、AXI `39f5f2d5`（0.39.6）；实际内容仍以本仓库文件为准，见 [SNAPSHOT.tsv](../../.bender/SNAPSHOT.tsv)。

GB 适配、仲裁、所有权和 Ara 分流是本项目新增需求，尚无本工程完整实现或验收结果。图中宽侧标为 `32 × NrLanes`，不把未冻结的 4-lane/128-bit 当作现有配置。NPU DDR 端的 256-bit 需求与 Controller 实际端口宽度分别填写，不能据图推断 GB 原生宽度。

## 3. 方案一：CPU 标量端不直接访问 GB

![CPU 标量端不直接访问 GB](../diagrams/2026-10-15_global_buffer_cpu_access/cpu-isolated.png)

[SVG 母版](../diagrams/2026-10-15_global_buffer_cpu_access/cpu-isolated.svg)。箭头表示请求方向，存储返回省略；RVV 双向线含指令和结果。跳线处不连接。虚线框是尚未实施的规划部件。NPU/搬运器的寄存器框表达控制与状态职责集合，不代表二者已合并为一个寄存器 IP。

CPU 标量访存仍走主 Xbar；GB 窗口不在该 Xbar 上映射。Ara 通过新增分流访问 GB，其普通访存仍经宽度适配进入主 Xbar。NPU 计算端、搬运器 GB 端和 Ara 在 GB 侧仲裁；搬运器 DDR 主口在 LLC 下游合流。

CPU 继续负责 RVV 指令发起、NPU 任务配置与完成处理，只是无法用标量指针直接读取 GB 数组。主 Xbar 上未映射的 GB 访问应明确报错，不能让同一物理地址被错误解释为 DDR。

CPU 后处理有两条主要交接路线：

| 路线 | 具体数据流 | 条件和代价 |
|---|---|---|
| Ara 转存到 SPM | CPU 发出向量加载 GB 的指令，再发出向量存储到预留 SPM 的指令；CPU 随后消费 | 增加复制，占用 Ara 单一 VLSU/AXI 出口和 SPM；须等待有效交接 |
| 搬运器转存到 DDR | GB → 搬运器 → DDR；CPU 经普通内存路径读取 | 增加 DDR 流量、调度及缓存同步；不能把设备写完成等同于 CPU/LLC 副本最新 |

**CPU 不接入 GB 不等于结果必须经 DDR 中转。** 对少量结果，Ara→SPM 是合理的比较基线。SPM 中的暂存区必须独立预留，避开 Boot ROM 栈、应用栈和其他数据；明确使用的地址别名及缓存策略，不能让旧缓存副本与新数据混用。

若只需返回一个索引或计数，可评估 Ara 的向量到标量结果通路。本地 `ara_dispatcher.sv` 有 `vmv.x.s` / `VMVXS` 解码；它不是通用数组访问机制，也不是已完成本项目 GB 运行验证。

本方案减少一个 GB 主机入口及其仲裁、隔离和验证工作；但后处理更依赖 Ara 或搬运器，调试导出和标量算子补位也多一步。GB 仍需处理 NPU、搬运器和 Ara 的竞争，不会因为排除 CPU 就变成无需共享协议的存储。

## 4. 方案二：增加 CPU 可达的 GB 访问口

![CPU 通过 64-bit 主机口访问 GB](../diagrams/2026-10-15_global_buffer_cpu_access/cpu-accessible.png)

[SVG 母版](../diagrams/2026-10-15_global_buffer_cpu_access/cpu-accessible.svg)。布局与方案一一致，橙色为新增主机支路。图中的“GB 主机访问适配”包含外部 AXI 出口后的适配职责；其细化模块、CDC 和 SRAM 组织待实际参数确定。

新增路径为：`CPU 标量 load/store → 主 Xbar64 → 外部 AXI 从设备出口 → GB 主机访问适配 → GB 仲裁/bank 调度 → SRAM`。CPU 的 GB 访问绕过 LLC；其普通 DDR 访问、Ara 普通路径和搬运器 DDR 旁路保持原职责。

Ara GB 支路仍在收窄前分流，不应为了接入 CPU 而把所有 GB 请求先压到 64-bit。各入口最终需要统一存储语义和响应路由；主 Xbar 出口包含扩展的 AXI ID 位，不能直接按 Ara 原始 ID 宽度截断。AXI 官方[对应版本 Xbar 文档](https://raw.githubusercontent.com/pulp-platform/axi/39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7/doc/axi_xbar.md)说明了 ID 扩展和同 ID 跨目标的顺序约束。

GB 的适配/仲裁可以按 bank 复用物理端口；逻辑入口增加不等于需要多端口 SRAM 宏。代价仍包括路由、适配、仲裁、队列、必要的 CDC/复位和验证，不能在综合前宣称面积或时序代价可忽略。

64-bit 接口每拍最多承载 8 B 有效数据，`8 × f` 只是满负载时每方向的理论上限。实际标量读速率受请求依赖、在途数、往返延迟、bank 冲突和背压影响；宽度转换不能凭空增加 CPU 持续带宽。

## 5. 比较与推荐工作流程

| 维度 | CPU 不直接接入 GB | CPU 接入 GB |
|---|---|---|
| 硬件增量 | 少一个主机入口及适配、隔离 | 新增译码、适配、仲裁输入及必要隔离 |
| 标量算法灵活性 | 需要先转存，或将操作交给 Ara | 可直接读写候选表、索引和中间结果 |
| 小结果交接 | 有准备、复制和通知开销 | 可省去仅为“变得可达”而进行的中转 |
| GB 竞争 | 无 CPU 直接竞争，但转存仍占带宽 | 窄访问可能干扰 NPU/Ara，须提供服务保证 |
| 反复排序 | 转存后可选合适的 CPU 工作区 | 非缓存 GB 随机访问可能较慢，宜先复制 |
| 调试与算法补位 | 依赖 Ara/搬运器导出 | CPU 可直接检查数据或运行标量参考算法 |
| 缓存可见性 | 转存目的地仍需同步 | GB 非缓存映射可简化共享；缓存映射另增协调要求 |
| Ara 占用 | 可能兼任结果搬运 | CPU 可自行取小结果，减少 Ara 依赖 |

针对近期场景，建议采用以下流程：

1. NPU 在 GB 的已分配缓冲区产生结果。
2. Ara 完成适合向量化的过滤或变换，形成较小的候选集合。
3. 生产者停止修改该结果，满足数据可见和顺序要求，再发布有效长度与任务完成身份。
4. CPU 获取所有权，直接检查少量字段；需要多轮排序时，一次复制到自己的可缓存工作区。
5. 复制完成后及时释放 GB；CPU 在私有副本上继续排序，避免长时间占住 GB。

例如 `256 条 × 16 B = 4096 B = 4 KiB`，适合用来说明“一次取走小表、私有区多次访问”。这不是容量配置、缓存命中保证或性能目标；真实阈值需要与 NPU/Ara 并发负载一起测量。

## 6. 接入必须落实的软硬件契约

首版建议 GB 数据窗口采用**不缓存、不可执行、普通 SRAM 幂等语义，加明确的缓冲区所有权交接**。CVA6 的属性由硬件区域配置决定，软件指针、`volatile` 或某个页表名称不能单独建立非缓存路径；原子能力也由下游系统负责。[官方 PMA 文档](https://docs.openhwgroup.org/projects/cva6-user-manual/01_cva6_user/PMA.html)

| 条目 | 必须明确的行为与影响 |
|---|---|
| 地址与类型 | CPU/Ara 对同一 GB 物理地址访问同一 SRAM；GB 与 DDR 地址不互为透明别名，窗口不与现有路由重叠 |
| 属性与权限 | `gen_cva6_cfg()` 中缓存、幂等和执行区域分别核对；当前外部 CIE/non-CIE 默认分组不能直接代替所需属性；PMP/页表另管权限 |
| 字节与边界 | 明确 8/16/32/64-bit 标量访问、WSTRB、对齐、跨边界和支持的 burst；未选中字节保持不变，越界必须正确结束 |
| 多入口响应 | 适配实际 ID/USER 宽度，保留请求归属、AW/W 配合、R/B 错误和在途限制；不把各口请求线直接合并 |
| bank 与服务 | 确认 NPU/Ara/搬运/CPU 的同时使用矩阵；兼顾 NPU 吞吐与 CPU 有界等待，不采用可能饿死 CPU 的无限期低优先级 |
| 完成与释放 | 定义共享可见点、有效长度、任务身份及发布顺序；IRQ、fence 或单个 B 响应不能独立构成完整交接证明 |
| 原子操作 | GB 支路不经过 LLC 前原子单元；首版不以 GB 存放 AMO/LRSC 共享控制数据，不支持的操作有明确拒绝/错误处理 |
| 驱动与启动 | GB 就绪后才发布分配范围；驱动维护所有权和结果有效性。CPU 直访本身不要求新增专用 IRQ，也不应形成早期启动依赖 |
| 可达性与隔离 | 现主 Xbar 全连接，外部 GB 目标可能被其他 master 访问；CPU PMP 不能替代所有主设备的总线访问隔离 |
| 构建与系统软件 | 后续实施才加入新适配/仲裁模块的静态清单，保持旧 FPGA 入口；裸机分配/链接与 Linux 平台资源描述各自同步 |

CPU 私有副本应与设备正在修改的对象分离；若后续还要交回设备，则再次履行发布协议，不能因为叫“私有工作区”就忽略新的共享边界。

**GB 直访与 DDR 硬件一致性是两项独立抉择。** 即使采用非缓存 GB，搬运器对 DDR 的旁路仍需处理 CPU/LLC 的脏行、在途访问和可见性。已有[一致性比较](Cache_Coherence_Architecture.md)保持“先比较、未选型”的状态，本页不把其候选机制视为已经具备的能力。

## 7. 最小验证、失败处理和未决输入

以下是后续 V01/S01/M01 的验收设计，本次未执行目标测试。

| 场景 | 通过判据与需要记录的证据 |
|---|---|
| 相同后处理负载 | 方案一 Ara→SPM、必要时 GB→DDR，与方案二直读/复制分别执行相同任务；结果与独立参考一致 |
| 基本访问 | 合法标量宽度、WSTRB、首尾/越界、高地址别名和不支持操作正确；保护字不受损 |
| 路由与顺序 | Ara 普通/GB 地址交错、同 ID 跨目标、AW/W 分离背压；响应归属、拍数和顺序正确，无死锁 |
| 并发与所有权 | 不同 bank 并发及同 bank 冲突数据正确；旧生产者不再修改已交出的结果；记录每源最大无服务间隔 |
| 完成与可见性 | 数据未到达约定共享点时不得消费；完成身份、有效长度、读取结果一致；禁止过早复用 |
| 异常与恢复 | R/B 错误、非法访问、超时、复位和迟到写不被报告为成功；受影响缓冲隔离，排空或受控复位后才释放 |
| 性能及回归 | 测量端到端延迟、CPU 等待、Ara 占用、GB 有效字节和实际 DDR 流量；回归普通内存、SPM/启动及既有原子域 |

既有 Ara `vstu.sv` 的 B 通道错误处理 TODO 保持开放。把结果“读回来碰巧正确”或看到 store 完成，不足以关闭传输错误的软件闭环；Cheshire iDMA 的控制接口缺口也不能被“搬运器”这个图中名称掩盖。

超时后先停止新提交，保留任务身份和部分结果无效范围；不能仅因软件停止等待就释放 GB。是否能取消、如何阻止迟到写、何时允许局部复位，要由真实 IP 的协议保证。本设计不承诺事务自动回滚。

尚待输入：最终 CPU 接入决定、候选表规模/访问次数/期限、GB 容量与 bank/宏端口/时钟、可交付接口、搬运引擎、地址及访问权限、仲裁服务目标。首个最小推进动作是用代表性小结果填出字节数、CPU 访问次数和并发窗口，再评审两个方案的资源与延迟预算；不据示例冻结频率或容量。

## 8. 本次交付与验证边界

本页、两张 SVG/PNG 和两页原生 PPTX 是文档与图稿产物。正文来源核对、布局测量、图形端点及 PPTX 对象检查见[图稿说明](../diagrams/2026-10-15_global_buffer_cpu_access/README.md)和[主题交接](../handoffs/L01_global_buffer_cpu_access.md)。Office 显示/编辑是否实测与生产硬件验证分别记录。

本次未修改生产 RTL/sw、地址、IRQ、配置、静态清单、依赖或旧 FPGA 脚本；未改原 `integration.md`、IP/DDR 契约和已有一致性文档。无软件/RTL 编译、展开、仿真、板测或 ASIC 验收，VCU118 HelloWorld 也不作为本方案证据。
