# L01 / Ara宽口分流访问NPU Global Buffer可行性

## 基本信息与用户决定

- 日期2026-10-09；分支mp/ara-pulp-v2，HEAD `278434024`。本轮只分析与记录，不改生产RTL/sw、地址图、配置或DDR拓扑，不构建/仿真。
- 用户决定：近期保持主AXI Xbar64，后续按系统性能再决定是否扩128，以减少修改；不因本方案更改原固定提取基线。
- 用户设想：Ara扩4 lanes，增加Global Buffer访问路径；NPU256-bit通路旁路LLC访问DDR。
- 澄清答复：Global Buffer是独立片上SRAM，NPU通过256-bit AXI搬运DDR数据，Ara另有端口访问该SRAM。不是DDR逻辑区域，也不是透明一致性缓存。
- 状态：架构可行性与最小改动范围分析完成，尚无RTL方案验收或实现授权。

## 结论

- 可行的候选是Ara现有单128-bit AXI主端在128→64转换之前按物理地址分流；普通地址沿原路，GB范围直达独立SRAM端口。可以保持CPU/Xbar/LLC/Debug64，同时Ara→GB128。
- 64→128聚合本身不增加源端带宽；若GB路径经过64位主Xbar再加宽，仍受64位限制。GB应从Ara宽侧引出。
- Ara仍只有一个VLSU/AXI出口，分流不产生两个独立向量访存引擎，普通内存与GB合计共享该出口带宽和请求队列。

## 当前代码与候选接法

- `hw/cheshire_soc.sv:606` AraDataWideWidth=32×NrLanes；:818传给Ara；:841失效过滤；:861宽到系统转换；:889接主Xbar。
- 最小保守候选：Ara128→现有axi_inval_filter128→新增地址译码/axi_demux128；普通支路→现有128→64转换→主Xbar64→原子/LLC→DDR；GB支路→新SoC端口→GB访问适配/仲裁→片上SRAM。
- 保留公共filter能保持普通路径已有行为；GB不缓存后其失效通常没有命中目标，但仍可能造成握手开销。之后若分流置于filter之前，仅普通支路保留filter，需要单独证明GB所有CPU访问均不缓存、无缓存别名；本轮不推荐未经验证直接绕掉现有机制。
- NPU DDR master256必须在LLC下游DDR互连合流，不能经64位主Xbar。CPU LLC出口64经所需转换也接该DDR互连。DDR实际端口位宽待供应商规格，不假定256。
- NPU的DDR AXI master256不能直接等同GB SRAM的访问口宽度；GB还需明确供NPU计算、本地DMA搬运、Ara访问的端口、bank和仲裁。可原生Ara128端口，也可128→256适配到GB统一AXI从端；不据此宣称SRAM原生多端口。

## 地址、协议与软件条件

- “非法地址空间”应改称目前未映射但体系结构合法的物理地址窗口。新增后它对允许访问者是合法RAM；不是非canonical虚拟地址或权限禁止地址。
- Ara addrgen.sv:841使用翻译后mmu_paddr或无翻译时请求地址形成物理访问；分流按AXI物理地址做。保持OSSupport/MMU路径，未来OS配置合法VA→GB PA映射及权限，PMP/PMA适用性需按实际模式定向确认，不能由接线推导自动通过。
- 避免把普通DRAM地址仅对Ara改映射为SRAM，否则CPU/Ara相同地址指向不同存储。首版建议独立窗口，不作透明DDR cache。
- 基址/大小建议至少按4KiB对齐，并匹配实际SRAM容量；确认burst不跨窗口。addrgen.sv:668已有4KiB边界处理，但不能代替新窗口边界验收。越界应返回协议正确错误，不能简单丢高位造成别名。
- axi_demux遵循AW/W关联、B/R回程和同ID跨目的端顺序；不可手工只按当前地址mux五通道。默认保留ID跟踪，不能无依据设置UniqueIds。多master汇入GB/DDR时需配置ID区分、最大在途和响应路由。
- CPU仅传递指针/控制时可以不具有GB数据访问路径；若需CPU初始化/诊断，增加独立64位不缓存窗口到同一SRAM，不能认为Ara新端口自动赋予CPU访问能力。
- 对模型软件，向量普通load/store可使用GB地址，不需要因路由增加自定义向量指令；lane/VLEN软件宏及内核布局仍需同步。GB容量管理、tiling、DMA描述符和同步由软件明确。

## 共享数据正确性

- GB是独立存储，DDR与GB之间需要显式搬运，无硬件自动一致性假设。
- 首版建议CPU映射GB为经验证的不缓存、不可执行、可重复访问的RAM；不能误标为带副作用MMIO后假定任意向量burst可用。实际PMA/页属性不能凭地址未使用推断。
- 保持CPU/NPU/Ara对同一GB字节使用同一物理语义，避免CPU缓存别名；现有filter只观察Ara写，不观察NPU/DMA写，也不维护LLC。
- 控制协议采用分块所有权/双缓冲，NPU完成GB写并达到共享可见点后才通知Ara；Ara完成读写并确保写入可见后才释放给NPU。发出指令、提交DMA描述符或仅单条fence不能未经验证等同数据已完成。
- CPU→Ara的等待/排序机制和Ara完成报告需复用并验证，特别是数据支路与控制doorbell不走同一路的跨端口顺序。正常B响应及下游可见点契约必须定义。
- 不把CPU共享锁/AMO/LRSC放在NPU旁路会写的区域；原子观察域不因新互连自动扩大。
- Ara vstu.sv:425有B错误未处理TODO。GB ECC/越界/复位中断如需软件可靠感知，必须专门闭环；不能靠错误slave存在就声称Ara异常处理完备。

## 性能推断与资源

- 同频满拍下64位为8B/cycle、128位为16B/cycle；GB直连Ara路径有机会提高持续加载带宽并省去DDR访问延迟。不是保证端到端2倍，也不是所有指令均满拍。
- Ara入口上限、VLSU在途数、短/strided/indexed访问、SRAM bank冲突、NPU竞争和CDC均可能限制收益。原路径转换器的4个在途读参数不能自动当作新GB路径设置或VLSU能力。
- 如果单个256位SRAM口每周期32B已经全部供NPU使用，无法同时保证Ara再读16B；需要时间分配、更多bank/独立端口或不同频率，并用请求模式验证。双缓冲能帮助隔离生产消费，但映射必须避免落同bank。
- 隔离Ara/GB实现风险范围通常小于全SoC加宽，但新增SRAM共享架构比单改lane复杂：协议/仲裁/完成和错误/软件搬运仍是主要工作。

## 最小实施范围和验收建议（未授权）

- 新Ara宽侧路由wrapper（decoder、demux、必要cut、边界与错误处理）；cheshire_soc接线及GB端口/类型；新平台GB控制器/多master仲裁及NPU-DDR合流；独立配置、地址契约、软件驱动/内核buffer安排及TB scoreboard。
- 不必因此改Ara lane/VLSU内部、CPU profile、主Xbar/LLC DW、Debug接口、现有DDR时钟/IP宽度；具体平台端口接法仍需统一。已有iDMA控制问题不因主Xbar保持64而解决；使用NPU自带DMA时明确不是已验证的Cheshire iDMA。
- 先用AXI SRAM模型检验普通/GB交错和同ID、AW/W错拍、背压、返回、无死锁；覆盖边界、WSTRB、未对齐和mask/tail；故障/复位注入。
- Ara真实向量读写GB，对比软件结果；NPU/搬运引擎并发使用GB，保护区与所有权检查；验证通知后可见性和旧块不被迟到写破坏。
- 最后接DDR模型/平台，测Ara有效B/cycle、等待周期、NPU与DMA吞吐、bank冲突和完整算子/模型时间。不要只比较接口位宽。

## 验证证据与下一步

- 本轮运行git状态/HEAD、定向rg/sed读取SoC、Ara addrgen/filter/vstu、CVA6 load_store_unit、AXI demux及M01接口契约；未编译/仿真/板测/综合。
- 官方固定AXI提交39f5f2d文档读取成功：https://raw.githubusercontent.com/pulp-platform/axi/39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7/doc/axi_demux.md 和同目录axi_xbar.md。复用模块有官方依据；GB/NPU拓扑为用户需求引出的定制设计建议，不称官方完整方案。
- 仅新增本交接，未提交。需协调者汇总：近期主Xbar64决定；用户新需求为Ara普通路径保留LLC、GB新支路直达SRAM，细化此前CPU/Ara全部保留LLC的概括；GB类型已确认，基址/容量/端口/时钟/VLEN未冻结。
- 下一步最少输入：GB容量/bank/端口及NPU实际访问模式、各口频率、DMA与计算是否并行、CPU是否访问GB。先定接口契约和资源预算，再取得实施授权。
