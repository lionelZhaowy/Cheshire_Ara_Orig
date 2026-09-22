# Cheshire-Ara 工程学习手册

> 2026-09-20 协作入口更新：新对话先读根 [AGENTS.md](../AGENTS.md)、[项目共享状态](PROJECT_STATE.md) 和 [任务分工](AGENT_TASKS.md)，无需默认通读全部教程。用户已确认 DDR 可采用 AXI4；当前近期目标是固定配置的独立 ASIC 源码提取，而不是长期维护 Bender。下文原始调查范围和路线保留为历史参考。

> 2026-09-16 更新：主仓库现已纳入 `.bender` 依赖源码快照及 `Bender.local` 相对路径配置，见[依赖快照说明](../.bender/README.md)。下文的版本/工作区状态是编写教程时的历史快照，不表示依赖修改仍未上传。

## 1. 目标与本轮边界

这套手册面向会 SystemVerilog 和 C、具备处理器基础但没有 Cheshire 使用经验的工程师。目标是读懂当前工程，建立可复现的软硬件基线，再逐步形成包含 CVA6、Ara、自研神经网络处理器（NPU）、图像信号处理器（ISP）和外部 DDR 存储子系统的异构片上系统（SoC）。

CVA6 不只是 NPU 的控制 MCU：它承担操作系统、运行时、通用控制及部分计算；Ara 承担适合向量化的计算；NPU 承担适合专用数据通路的模型计算。最终任务分配应由实测的精度、延迟、带宽和功耗决定。

本轮只新增本索引及第一篇入门教程，不修改 RTL、软件、构建脚本或配置，不执行构建、仿真、烧录或工程重建。后续文档只是规划，不创建占位文件。

## 2. 依据、版本与可信度

分析日期：2026-09-15。第一依据是本地源码，不是官方最新主分支。

| 项目 | 本次读取的基线 |
| --- | --- |
| 根仓库 | 分支 `mp/ara-pulp-v2`，提交 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` |
| CVA6 | `.bender/git/checkouts/cva6-20c9d7cbe0dd6995`，提交 `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` |
| Ara | `.bender/git/checkouts/ara-2c7b103275a16c87`，提交 `2895ba907e9eb14b3464609dc791a969d159a7c3` |
| 依赖定义 | [Bender.yml](../Bender.yml) 描述依赖与源文件选择；[Bender.lock](../Bender.lock) 固定解析后的版本 |
| 工作区状态 | 根仓库存在 10 个已跟踪文件修改；另有本地测试、VCU118 约束、FPGA 工程及产物；Ara 依赖内部也有修改 |

因此，“根仓库提交号相同”不等于“工程相同”。迁移时必须保留根仓库补丁、未跟踪源文件、依赖内部补丁、锁文件、工具版本和构建参数。不要用删除 `.bender` 的方式清理当前唯一工作副本。

文中使用以下证据边界：

- **源码确认**：由当前代码、配置或脚本直接得出，给出路径和关键符号。
- **已有产物**：本地已有 ELF、工程文件或报告可佐证，但不证明它们由当前全部源码重新生成。
- **官方资料**：用于背景或外部路线，不覆盖本地实现。
- **推断／待验证**：静态阅读发现的风险，尚未通过目标工具或硬件验证。
- **未来设计建议**：尚未在当前工程实现的方案。

教程中的命令按当前脚本整理，是供后续执行的操作说明，不是本轮运行记录。

## 3. 本轮阅读范围

扫描了工程目录、文件清单和依赖关系；重点阅读顶层、配置、构建及启动链，并沿接口定向追踪依赖。这里的“系统性阅读”不表示逐行审计所有第三方 IP、SDK 和生成文件。

| 范围 | 本轮重点 |
| --- | --- |
| 根目录 | `README.md`、`Makefile`、`cheshire.mk`、`Bender.yml`、`Bender.lock` |
| `hw/` | `cheshire_pkg.sv`、`cheshire_soc.sv`、类型宏、寄存器描述、Boot ROM、iDMA 封装 |
| `.bender/git/checkouts/` | CVA6 配置和加速器接口、Ara 接口与集成 Makefile、AXI、LLC、中断和外设相关依赖 |
| `sw/` | 软件 Makefile、链接脚本、启动汇编、驱动、Hello World、DMA 与向量测试、ZSL |
| `target/sim/` | 测试平台、fixture、VIP、ELF 加载器、Questa/VCS 启动及已有编译脚本 |
| `target/xilinx/` | VCU118 顶层、DDR 封装、宏、Tcl、构建规则及已有工程和时序报告 |
| `util/`、`docs/` | Boot ROM 生成、调试与烧录入口、现有架构和软件说明 |

三个影响上手的发现：

1. **编译配置和 SoC 参数是两层配置。** `SELCFG=3` 不会自动把 CVA6 编译成支持向量扩展的版本。
2. **SPM 由 LLC 存储阵列提供。** Boot ROM 会初始化它；不能把它理解为一个始终可用的独立 SRAM。
3. **当前工作区不能等同于原版演示工程。** Hello World、软件镜像规则、VCU118 集成及依赖中均有本地变化。

## 4. 文档索引与推荐阅读顺序

| 状态 | 文档 | 解决的问题 |
| --- | --- | --- |
| 已创建 | [00_README.md](00_README.md) | 目标、证据范围、学习和实施路线 |
| 已创建 | [01_Cheshire_Ara_Quick_Start.md](01_Cheshire_Ara_Quick_Start.md) | 从目录、配置、构建到裸机启动、UART、Ara 和扩展边界的第一条完整路径 |
| 已创建 | [02_Cheshire_Ara_ASIC_Extraction_Handoff.md](02_Cheshire_Ara_ASIC_Extraction_Handoff.md) | 固定 Ara 配置、静态 filelist、独立目录提取及 DDR 旁路契约；替代原“02 配置管理专题”的近期优先安排 |
| 已创建 | [PROJECT_STATE.md](PROJECT_STATE.md) / [AGENT_TASKS.md](AGENT_TASKS.md) | 当前目标、证据边界、待办、不同对话分工和启动提示词 |
| 已创建 | [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) / [交接索引](handoffs/README.md) | 各任务的独立结果记录与跨对话交接 |
| 已创建 | [离线教材入口](learning/index.html) / [进阶全外设](learning/advanced.html) | 24页中文教材、18张SVG、429项寄存器索引；系统/时钟复位、C到硬件执行、驱动与中断/DMA综合案例，明确运行缺口 |
| 计划 | `03_Boot_and_Baremetal_Debugging.md` | ELF、链接、启动、异常、中断、定时器、DMA、UART/JTAG 调试的可执行实验 |
| 计划 | `04_CVA6_Ara_and_Memory_System.md` | CVA6/Ara 调度、向量编程、MMU、各级缓存、数据一致性和性能定位 |
| 计划 | `05_AXI_Address_Map_and_Custom_IP.md` | 地址设计、AXI、寄存器、中断、NPU/ISP 接入及数据所有权协议 |
| 计划 | `06_DDR_and_Platform_Integration.md` | 外购 AXI4 DDR 控制器/PHY、旁路共享存储、时钟复位、FPGA 与 ASIC 平台差异、验证矩阵 |
| 计划 | `07_RTOS_and_Linux.md` | 上下文保存、调度、设备树、OpenSBI、Linux 驱动与异构运行时 |
| 计划 | `08_ASIC_Migration_and_Verification.md` | 通用顶层、工艺存储器、可测性设计、时钟域检查、等价与回归、综合和物理实现交接 |

人类初学者可按 01 顺序学习；新 Agent 按共享状态和任务表定向阅读。计划中的专题尚未创建，不代表对应实施已经开始。

**当前优先项是按 02 交接书实施 E01。** 该方案文档已完成，但源码提取和新目录验证尚未完成；实施需在对应对话中获得授权。

## 5. 从 Bare-metal 到 ASIC 的学习路线

知识理解顺序可以是：

```text
Bare-metal → RTOS → Linux → NPU/异构运行时 → ASIC
```

这表示逐步理解软件依赖，不表示必须等 Linux 移植完成才能验证 NPU。项目实施中，NPU 的寄存器、DMA 和数值验证应先用裸机完成。

| 阶段 | 学习重点 | 建议的退出条件（未来验收标准） |
| --- | --- | --- |
| Bare-metal | 编译、链接、启动、MMIO、UART、异常、定时器 | 同一源码在仿真和 VCU118 上得到可核验的结果；失败能定位到 PC、异常原因或总线事务 |
| RTOS | 机器态中断、上下文切换、栈、同步、缓存维护 | 抢占和压力测试稳定；明确浮点/向量状态保存策略 |
| Linux | MMU、特权态、设备树、OpenSBI、驱动和 DMA 缓冲区 | 内存、串口、定时器、中断稳定；设备树与硬件版本匹配 |
| NPU/异构运行时 | CVA6/Ara/NPU 分工、缓冲区所有权、完成通知和带宽 | 数值对齐、异常恢复和并发压力通过，而不只测单次吞吐率 |
| ASIC | 工艺 IP、时钟复位、SRAM、测试、验证覆盖率、实现约束 | 交付可追溯的 RTL/软件/约束/验证基线；满足项目签核要求 |

## 6. 建议的实际实施顺序

下面保持八个工程阶段，便于分别建立验收点；具体排期取决于团队人数、IP 交付和工具支持情况。

| 阶段 | 实施内容 | 需要掌握的当前模块／文件 |
| --- | --- | --- |
| 1 | Bare-metal Cheshire 基线 | `cheshire.mk`、`sw/sw.mk`、Boot ROM、`crt0.S`、链接脚本、仿真 VIP |
| 2 | CVA6 + Ara 软件开发 | 两层配置、`acc_dispatcher.sv`、`ara.sv`、向量访存和一致性路径 |
| 3 | Custom NPU integration | 外部 AXI 主/从端口、寄存器端口、中断、iDMA、共享存储契约 |
| 4 | ISP integration | 图像输入时钟域、流接口/行缓存、DDR 写入、缓冲区调度；LVDS 实现单独规划 |
| 5 | External DDR controller integration | LLC 输出、AXI 协议转换、位宽/ID、CDC、DDR 初始化和错误处理 |
| 6 | RTOS | `crt0.S` 的不足、CLINT/PLIC、完整任务上下文和缓存策略 |
| 7 | Linux | `sw/boot/`、SDK、设备树、OpenSBI、DMA 驱动及向量上下文 |
| 8 | ASIC migration | 通用 SoC 顶层、SRAM 映射、PAD/PLL/DDR PHY、DFT 和验证/实现流程 |

ASIC 约束应提前影响设计：阶段 1 就记录工具兼容性、接口和复位要求；不应等最后才发现某段 FPGA IP 无法替换。

## 7. 使用及更新约定

- 每次改变 `Bender.lock`、CVA6 profile、Ara lanes/VLEN 或地址映射，都检查相关章节是否失效。
- 每次新增实测结论，附上源码/依赖版本、命令、日志位置和通过标准；不要把旧 `.elf`、`.bit` 当成当前版本的测试结果。
- 未来迁移 EDA 服务器，先复现标量与向量最小测试，再扩大外设和 DDR 覆盖。VCS 2018 是否支持当前组合，以编译、展开和运行回归为准。
- 修改寄存器或地址时，同时检查 RTL 解码、软件链接符号、驱动、设备树、测试平台和调试脚本。
- 保持原始可运行基线；兼容性改写与功能开发分别提交。涉及依赖内部修改时，也必须纳入版本管理和回归。

当前官方网页会继续变化。例如[官方 Getting Started](https://pulp-platform.github.io/cheshire/gs/)的工具安装方式已与本地版本存在差异。本手册不会把网页中的新依赖管理方式直接套到当前 checkout。
