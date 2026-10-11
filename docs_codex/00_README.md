# Cheshire-Ara 工程文档入口

本文是当前入口。教材解释机制，参考手册提供字段和命令，工程契约记录实施条件；历史调查保留在页末，不再承担现行阅读路线。

## 推荐阅读顺序

从 [HTML 教材首页](learning/index.html) 或 [同步 Markdown 教材](learning/markdown/index.md) 开始，按以下顺序阅读同一套正文：

1. **系统与程序执行**：Cheshire、CVA6、Ara 的职责；C/汇编→编译链接→ELF→装载→入口→`main`。
2. **地址、互连与存储**：地址窗口、AXI 主从与译码；Cache 的组/路/行；LLC/SPM 与 DDR 的边界。
3. **数据搬运与计算协作**：iDMA、Ara/RVV、共享缓冲区和缓存可见性。
4. **启动与软件运行**：Boot ROM、Platform ROM、外部介质/JTAG、应用初始化、trap 与外设。
5. **系统管理与配置**：时钟、复位以及参数默认值、目标覆盖和消费者。
6. **OS、扩展集成与验证**：RTOS/Linux 的软件职责，自研 IP/AXI4 DDR 接入，ASIC 资源适配和验证方法。

九篇、42 章的完整顺序由 [pages.json](learning/scripts/pages.json) 生成。首次动手从 [ELF 布局实验](learning/labs.html#lab-a)开始；详细启动之后进行 [装载实验](learning/labs.html#lab-b)。每项实验的环境和运行门槛在实验页给出。

## 文档职责与查询入口

新 Agent 的最短接手路线、历史检索方法和旧路径映射见[文档定位指南](AGENT_DOCUMENTATION_GUIDE.md)。现行接口契约与 ASIC 适配见[工程参考索引](engineering/README.md)。

| 职责 | 入口 | 使用方式 |
| --- | --- | --- |
| 主教程 | [HTML](learning/index.html) / [Markdown](learning/markdown/index.md) | 连续理解原理、过程和本地源码，二者由同一正文源生成 |
| 配置参考 | [configuration/README.md](configuration/README.md) | 按 Cheshire/CVA6/Ara/外设查参数，结合目标覆盖和修改验证 |
| 软件操作参考 | [software/README.md](software/README.md) / [实验手册](learning/labs.html) | 工具链、构建、装载、库/驱动和排错；预期结果与已执行证据分开 |
| 分层与工具查询 | [软硬件层次与工具索引](software/LAYERS_AND_TOOLS.md) | 对照结构图定位各层源码、脚本、主机工具及流程产物 |
| 器件与接口查询 | [片外器件与接口实现参考](EXTERNAL_DEVICES_AND_INTERFACES.md) | 型号、RTL、仿真对端、软件入口、FPGA/ASIC 支持边界 |
| 地址与寄存器 | [地址空间](learning/address-map.html) / [寄存器索引](learning/registers.html) | 区分默认路由窗口、资源容量与真实寄存器偏移 |
| 固定配置提取 | [02 提取交接书](02_Cheshire_Ara_ASIC_Extraction_Handoff.md) | 独立目录、静态清单与最小验收规格；工程尚未提取 |
| 平台启动 | [03 平台配置约定](03_Platform_ROM_Clock_IP_Configuration.md) | 已确认的启动方向、Platform ROM 修复依赖与未冻结 IP 参数 |
| 扩展契约 | [M01 IP/DDR](engineering/IP_DDR_Interface_Contract.md) / [P01 ASIC](engineering/ASIC_Adaptation_and_Evidence.md) | 接口、所有权、责任和验收条件，不表示 IP 已接入 |
| 协作与证据 | [项目状态](PROJECT_STATE.md)、[任务表](AGENT_TASKS.md)、[交接索引](handoffs/README.md) | Agent 先定任务和边界，再读对应章节与源码 |
| 教材维护资料 | [L01 规划、评审与实施报告](maintenance/L01/README.md) | 按需追溯教材维护；不属于用户学习主线，历史 Prompt 不作为新任务指令 |

旧规划中的 03/04 启动与处理器主题现由主教程和软件/配置参考承担；05/06 由 IP/DDR 章节与 M01 承担；07 由 OS 四章承担；08 由 ASIC 篇与 P01 承担。无需重复创建旧计划中的六个文件。

## 项目方向与事实边界

CVA6 同时承担控制和通用计算；Ara 承担向量计算，尤其是 NPU 不适合的部分浮点向量运算。自研 ISP、NPU、LVDS、外购 AXI4 DDR 和独立片上 Global Buffer 是扩展目标。近期主 AXI Xbar 保持 64-bit；GB、Ara 分流和 NPU/ISP 旁路仍属待实现需求，具体边界见 M01。原始资料中的 AXI3 描述保留其历史身份，不作为当前目标接口，也不能据目标推断当前 RTL 已完成替换。

已知运行证据是用户报告 VCU118 HelloWorld；Platform ROM 返回路径、iDMA 控制通路、Ara 与设备并发等缺口未因此关闭。裸机、OS 上游支持和本工程当前已验证能力分别记录。文档重构不修改 RTL/驱动，不构成重新仿真、板测或 ASIC 签核。

## 维护与审查

主教程在 `learning/content/*.html` 修改，通过既有 [build_site.py](learning/scripts/build_site.py) 同步生成 HTML 和 Markdown 阅读版。配置/软件 Markdown 保留参考和操作职责；不要把历史问答逐条追加成新的主线。生成、链接、内容保护与浏览器检查见 [教材维护说明](learning/README.md)。

本轮问题、内容迁移、事实修正及验证结果见 [2026-10-11 重构记录](learning/STRUCTURE_REVISION.md#review-20261011)和 [独立交接](handoffs/L01_documentation_restructure.md)。旧入口、语义锚点、图源、PPTX 和历史证据保留。

## 历史调查与早期规划

以下内容是 2026-09-15 起的原始调查及截至 2026-10-08 的补记；其中“本轮”“当前”“计划”和版本表都属于相应历史日期，不替代上方入口或当前 checkout。保留它们是为了追溯独有分析、旧命令的适用条件和规划演变。

<details>
<summary>展开原始调查、早期路线与版本记录</summary>

# Cheshire-Ara 工程学习手册

> 2026-10-08 系统教材实施完成：[当前九篇42章](learning/index.html)，[软件/OS/ASIC与测量实施及验收](maintenance/L01/reports/system_acceptance.md)。全站正式标题按[既定规范专项修正](maintenance/L01/reports/title_style.md)。原03–08主题通过教材、[IP/DDR接口契约](engineering/IP_DDR_Interface_Contract.md)和[ASIC适配手册](engineering/ASIC_Adaptation_and_Evidence.md)承载；生产工程和目标验证未实施。

> 2026-09-29 教材扩充：新版 [HTML 教材](learning/index.html) 保持单线结构，增加 [CVA6–Ara/RVV](learning/vector.html)、[共享数据交接](learning/memory.html#sharing) 和 [ASIC/NPU 接口规划](learning/integration.html#npu-topology)。时序图统一采用 WaveDrom 源文件与离线 SVG；[本轮证据](learning/evidence.html#depth)区分软件构建、教学图与未执行的目标验证。

> 2026-09-20 协作入口更新：新对话先读根 [AGENTS.md](../AGENTS.md)、[项目共享状态](PROJECT_STATE.md) 和 [任务分工](AGENT_TASKS.md)，无需默认通读全部教程。用户已确认 DDR 可采用 AXI4；当前近期目标是固定配置的独立 ASIC 源码提取，而不是长期维护 Bender。下文原始调查范围和路线保留为历史参考。

> 2026-09-16 更新：主仓库现已纳入 `.bender` 依赖源码快照及 `Bender.local` 相对路径配置，见[依赖快照说明](../.bender/README.md)。下文的版本/工作区状态是编写教程时的历史快照，不表示依赖修改仍未上传。

<a id="1-目标与本轮边界"></a>

## 1. 文档目标与范围

这套手册面向会 SystemVerilog 和 C、具备处理器基础但没有 Cheshire 使用经验的工程师。目标是读懂当前工程，建立可复现的软硬件基线，再逐步形成包含 CVA6、Ara、自研神经网络处理器（NPU）、图像信号处理器（ISP）和外部 DDR 存储子系统的异构片上系统（SoC）。

CVA6 不只是 NPU 的控制 MCU：它承担操作系统、运行时、通用控制及部分计算；Ara 承担适合向量化的计算；NPU 承担适合专用数据通路的模型计算。最终任务分配应由实测的精度、延迟、带宽和功耗决定。

本轮只新增本索引及第一篇入门教程，不修改 RTL、软件、构建脚本或配置，不执行构建、仿真、烧录或工程重建。后续文档只是规划，不创建占位文件。

<a id="2-依据版本与可信度"></a>

## 2. 源码版本与证据类别

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

<a id="3-本轮阅读范围"></a>

## 3. 源码阅读范围

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
| 已创建 | [单线离线教材](learning/index.html) / [实验手册](learning/labs.html) / 旧版备份（旧站已于 2026-10-11 移除） | 2026-09-29 完善为七篇/30 章，另有六项实验和两页参考；分层目录与首次 C 程序短路线，补重点机制图和分模式启动；429 项寄存器索引，历史构建与本次网页检查分开记录 |
| 计划 | `03_Boot_and_Baremetal_Debugging.md` | ELF、链接、启动、异常、中断、定时器、DMA、UART/JTAG 调试的可执行实验 |
| 计划 | `04_CVA6_Ara_and_Memory_System.md` | CVA6/Ara 调度、向量编程、MMU、各级缓存、数据一致性和性能定位 |
| 计划 | `05_AXI_Address_Map_and_Custom_IP.md` | 地址设计、AXI、寄存器、中断、NPU/ISP 接入及数据所有权协议 |
| 计划 | `06_DDR_and_Platform_Integration.md` | 外购 AXI4 DDR 控制器/PHY、旁路共享存储、时钟复位、FPGA 与 ASIC 平台差异、验证矩阵 |
| 计划 | `07_RTOS_and_Linux.md` | 上下文保存、调度、设备树、OpenSBI、Linux 驱动与异构运行时 |
| 计划 | `08_ASIC_Migration_and_Verification.md` | 通用顶层、工艺存储器、可测性设计、时钟域检查、等价与回归、综合和物理实现交接 |

人类初学者可按 01 顺序学习；新 Agent 按共享状态和任务表定向阅读。计划中的专题尚未创建，不代表对应实施已经开始。

**当前优先项是按 02 交接书实施 E01。** 该方案文档已完成，但源码提取和新目录验证尚未完成；实施需在对应对话中获得授权。

<a id="5-从-bare-metal-到-asic-的学习路线"></a>

## 5. 裸机软件与 ASIC 系统的学习路线

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

<a id="6-建议的实际实施顺序"></a>

## 6. 后续工程实施顺序

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

## 2026-10-08 教学质量与专题规划复核

上方03–08文件表保留为历史主题规划；相关评估、旧 Prompt、作者报告和验收现统一收录于[教材维护资料](maintenance/L01/README.md)，不作为新的学习章节或执行待办。现有03平台配置文件保持原职责。

</details>
