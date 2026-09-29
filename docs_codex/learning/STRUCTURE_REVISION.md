# L01 篇章结构修订 · 2026-09-29

输入为 `69fabdd227e225bf9f5f0b9ec5fe9d056999fea6` 的深度扩充版本。依据[结构审查](../handoffs/2026-09-29_L01_structure_review.md)修订；该审查原文及索引记录保留。本次授权是教材、配图与必要维护工具，不涉及生产 RTL、软件、平台或依赖修改。

## 对上一轮问题的反思

上一轮把“补齐知识点”当成主要完成标准，继续向 16 个页面追加平级小节。正文加深了，目录却仍只理解 H2；既没有按新增主题调整章节职责，也没有同步检查前置关系。有效链接检查还漏掉了“目标存在但含义不对”和“历史记录被称为本轮”的问题。

本次以读者需要完成的任务划分章节，再迁移已有内容。全书为七篇、30 章，另有首页、六项实验合册及两页参考，共 34 个主页面。篇是导航分组，不增加空白篇首页。章节内部采用 H1 章、H2 节、H3 小节；不为追求层数强行添加 H4。

## 逐项回应审查

| 项目 | 已落实的修订 | 检查入口 |
| --- | --- | --- |
| R1 导航扁平 | 显式篇/章清单；当前篇默认展开，当前章列节；页内目录嵌套 H2/H3；面包屑、章号、上下章共用清单 | [目录清单](scripts/pages.json)、[生成器](scripts/build_site.py) |
| R2 职责过密 | 原存储页拆至 11/12/22/26；向量页拆至 24/25/26/29 | 下方目录及[148 个原 H2 归属](evidence/structure-20260929-allocation.json) |
| R3 顺序倒置 | 地址与协议先于 Crossbar；外设按结构/复位寄存器/初始化/操作/错误验证排列；实验 E 扩充降为 H3 | [UART/GPIO](uart-gpio.html)、[实验 E](labs.html#lab-e) |
| R4 重点不足 | 独立 CVA6、时钟、复位、电源、DDR；真实字段/消费者/约束表；寄存器索引直达关键语义；IP 交付边界表 | [配置](configuration.html#fields)、[DDR](ddr.html)、[扩展集成](accelerators.html#delivery-contracts) |
| R5 字段名 | `EnAra` 改为 `Cfg.Ara`；同处标明 `Cfg.AraNrLanes/AraVLEN`，不把配置层混写 | [配置依据](../../hw/cheshire_pkg.sv) |
| R6 启动依赖 | ROM 自主启动与 JTAG 接管分开；后者条件为相应配置下检查 `CFG_SPM_LOW.bit0`，再请求 halt 并等应答；没有等待 ROM C 测频 | [JTAG](boot-debug.html#takeover)、[VIP](../../target/sim/src/vip_cheshire_soc.sv) |
| R7 证据指向 | 本次结构报告为 `#structure`，此前扩充为 `#depth`，09-28 为 `#current`；V 仅在汇编内核的说法限定初始示例 | [证据页](evidence.html)、[RVV 编程](vector.html#programming) |

额外定向纠错：UART 的槽间隔为 4 字节，但当前 `uart.c` 使用 `reg8`，现已区分 C 访问宽度与 Reg/APB 接口宽度，并给出初始化调用、DLAB 顺序、分频合法范围与超时缺口。GPIO 的复位语义移到输出操作之前。

JTAG 配图同步修正：流程图标明检查配置位，WaveDrom 不再把 `BIST / SPM / stack` 合成一个已完成事件。ROM 写配置及 COMMIT 后还有扩展 sp 的指令；应用若继承栈须独立验收实际 PC/sp。两图均为教学图，不是仿真波形。时序继续由本地 WaveDrom 3.5.0 导出，无 0/1 表格拼图。

## 当前章节职责

| 篇 | 章 | 学习出口 |
| --- | --- | --- |
| 第一篇 | 01 · [整体架构与平台边界](architecture.html) | 沿取指、数组与字符输出辨认模块职责。 |
| 第一篇 | 02 · [CVA6 功能与 RISC-V 系统基础](cva6.html) | 把 ISA、CSR、访存与实现资源联系起来。 |
| 第一篇 | 03 · [Cheshire、CVA6、Ara 与软件配置](configuration.html) | 按真实字段及消费者建立自洽组合。 |
| 第二篇 | 04 · [时钟系统与 PLL](clocks.html) | 区分时钟域、使能、同步器和平台时钟源。 |
| 第二篇 | 05 · [复位体系与平台启动条件](reset.html) | 从请求生命周期定义复位、就绪与恢复。 |
| 第二篇 | 06 · [电源域与低功耗规划](power.html) | 区分现有 RTL 边界和待实现的电源契约。 |
| 第三篇 | 07 · [地址空间与访问属性](address-map.html) | 分别核对路由窗口、实际容量和 CPU 属性。 |
| 第三篇 | 08 · [AXI 通道、突发与握手](axi.html) | 沿真实握手语义理解一笔读写事务。 |
| 第三篇 | 09 · [AXI Crossbar 结构与事务路由](interconnect.html) | 追踪译码、仲裁、W 路由、ID 与响应。 |
| 第三篇 | 10 · [接口适配与 RegBus](adapters.html) | 解释位宽、协议、ID 转换及跨域边界。 |
| 第三篇 | 11 · [Cache、LLC/SPM 与存储路径](memory.html) | 区分缓存副本、地址别名与共享物理阵列。 |
| 第三篇 | 12 · [DDR 控制器、PHY 与 AXI4 接入](ddr.html) | 从平台初始化到软件可用建立交付条件。 |
| 第四篇 | 13 · [裸机 C 程序运行模型](runtime.html) | 从对象、调用和初始化理解存储布局。 |
| 第四篇 | 14 · [工具链、链接与 ELF](build.html) | 让同一数组程序形成可解释的装载产物。 |
| 第四篇 | 15 · [Boot ROM、启动模式与应用初始化](boot.html) | 分别追踪 ROM 服务、自主加载和应用入口。 |
| 第四篇 | 16 · [JTAG 与程序加载调试](boot-debug.html) | 核实外部调试接管的真实等待条件。 |
| 第四篇 | 17 · [Questa/VCS 仿真与结果验证](simulation.html) | 按阶段检查输入、运行、数值和退出。 |
| 第五篇 | 18 · [MMIO 驱动、UART 与 GPIO](uart-gpio.html) | 从寄存器语义推进到初始化与引脚行为。 |
| 第五篇 | 19 · [定时器与中断系统](interrupts.html) | 建立计时、使能、服务、清源与返回闭环。 |
| 第五篇 | 20 · [I2C 与 EEPROM](i2c.html) | 从线路、FIFO 和控制寄存器到器件读取。 |
| 第五篇 | 21 · [SPI、NOR 与 SD](spi.html) | 把控制器事务和外部设备协议分开。 |
| 第五篇 | 22 · [iDMA、流量管理与总线错误](dma.html) | 理解搬运提交、完成、限流与故障门槛。 |
| 第五篇 | 23 · [Serial Link、VGA 与 USB](stream-io.html) | 按设备追踪控制、数据、时钟及验证条件。 |
| 第六篇 | 24 · [Ara 结构与 CVA6 协处理器接口](ara.html) | 分清请求、应答、CPU 提交和实际完成。 |
| 第六篇 | 25 · [RVV 编程与结果验证](vector.html) | 用同一数组比较汇编、intrinsics 和自动向量化。 |
| 第六篇 | 26 · [CPU、Ara、DMA 与 NPU 的共享数据](sharing.html) | 建立可见性、所有权和有界恢复协议。 |
| 第七篇 | 27 · [自定义 IP 的控制、数据和中断接入](integration.html) | 从独立 Reg 单元逐步进入系统。 |
| 第七篇 | 28 · [LVDS、ISP、NPU 与外部 DDR 集成](accelerators.html) | 逐 IP 明确接口、缓冲、跨域和验收交付。 |
| 第七篇 | 29 · [模型任务划分与容量带宽预算](models.html) | 用透明假设衡量 Ara/NPU 协作成本。 |
| 第七篇 | 30 · [固定配置工程与 ASIC 集成验收](future.html) | 冻结可搬迁输入并形成分阶段实现证据。 |

首次运行程序走[首页短路线](index.html#route)：架构/配置/地址 → C 运行模型 → ELF → 实验 A → ROM/JTAG → 仿真与实验 B。其余硬件设计章节按需要查阅；每个正文页列具体前置章节。

## 内容和旧链接如何保留

原 20 个内容页中的 148 个 H2 均有归属记录。正文按职责移动，节号重新生成但语义锚点保留。原架构页的 ASIC 时钟/复位/电源混合节拆至 04/05/06，旧组合锚点指向 06 并链接相关两章。原介绍性目标段改写为新职责和前置；来源集中整理，旧源码链接仍可从相应章节访问。

[迁移清单](scripts/anchor_migrations.json)记录 373 条旧页/锚点到正文的映射。例如：

| 旧链接 | 当前位置 |
| --- | --- |
| `configuration.html#isa` | [02 指令能力](cva6.html#isa) |
| `interconnect.html#address-map` | [07 地址图](address-map.html#address-map) |
| `memory.html#ddr-subsystem` | [12 DDR](ddr.html#ddr-subsystem) |
| `memory.html#dma` | [22 iDMA](dma.html#dma) |
| `vector.html#interface` | [24 协处理器接口](ara.html#interface) |
| `vector.html#model-case` | [29 模型案例](models.html#model-case) |
| `future.html#calculator` | [29 容量计算器](models.html#calculator) |

保留的旧页面遇到已移走的 hash 会跳到新节；禁用 JavaScript 则在原锚点显示明确链接。更早的 20 个旧页继续保留兼容入口。生成器验证目的锚点必须存在于当前正文，禁止转到另一个迁移占位符；浏览器逐条验证跨页迁移。

## 验证和边界

[结构校验](evidence/structure-20260929-checks.txt)检查导航层次、标题、页内目录、上下章、链接/锚点、生成一致性、原内容归属与历史保护。[内容比对](evidence/structure-20260929-content-audit.json)逐块比对旧正文并列出有意改写；首页/参考页按专项规则检查。[浏览器记录](evidence/structure-20260929-browser.txt)覆盖桌面/手机、禁用脚本、目录展开、迁移、寄存器搜索、计算器和修订图的边界。

旧站 728 文件、此前 evidence、独立示例均保留原内容。没有重新构建软件、运行生产 RTL、板测或性能测量。源码核对不能替代执行；ASIC 电源域、PLL、DDR 寄存器与 NPU 接口仍是待实现/待交付方案。官方资料继续沿用[此前已记录的版本和查阅日期](OFFICIAL_SOURCES.md)，本次未重新核验上游网页。
