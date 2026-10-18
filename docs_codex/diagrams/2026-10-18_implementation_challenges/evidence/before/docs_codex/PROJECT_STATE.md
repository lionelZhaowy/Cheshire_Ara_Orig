# 项目共享状态

更新：2026-10-18，记录用户已确认 SoC 架构 v1 功能基线、总纲及三人分工/条件排期文档交付，输入 `mp/ara-pulp-v2` / `09798c1ded457e423b927844f66faae87583a20c`；保留 2026-10-16 DDR–GB 更新及其余 2026-10-13 文档整理快照。原整理输入：`mp/ara-pulp-v2` / `5a1338e0a0bf115ddd54c19e0ae367ac2d541892`。这是当前事实与未验证项索引，不是测试报告或实施授权。新对话再核对实际 HEAD 和工作区；按[任务表](AGENT_TASKS.md)、[定位指南](AGENT_DOCUMENTATION_GUIDE.md)及对应主题交接接手。

## 1. 最终目标与近期目标

最终目标：以 Cheshire + CVA6 + Ara 为起点，集成 LVDS 图像输入、ISP、脉动阵列/NPU、采购的 DDR 控制器及相关 IP，裁切无用模块，迁移到团队 EDA 服务器，完成 IC 设计、验证、DFT 与物理实现并流片。

团队背景：有 MIPS 处理器及自定义总线经验，RISC-V/标准 AXI 的软硬件经验尚在积累；项目时间紧，希望分阶段学习、直接推进必要工作。

近期目标：把正确的向量组合提取为能独立搬迁的 `cheshire_ara_asic/`。只维护一个目标配置、静态源码清单和团队自己的脚本，不继续把 Bender 工程管理当作主要任务。

现行教材、参考手册和 RTL 模块指南已交付；本次仅整理文档、图稿和维护脚本。工程提取、生产 RTL/sw 修改及大型构建不在本次授权范围。

当前提取状态：**尚未实施；整理时该目录不存在。** 已有提取规格与协作资料，不代表已实施 RTL 提取。


## 2. 需求、建议和未决项

| 性质 | 内容 |
| --- | --- |
| 用户确认（2026-10-18） | 当前“SoC 架构(v1)”在功能规划层面满足现阶段需求，作为后续实现基线；见[实施总纲](engineering/SoC_Architecture_v1_Master_Plan.md)。CPU/Ara2 经主 Xbar64 共享 M5 访问独立 GB，eMMC 参数加载、RAW/ISP 采集、≤256 ROI 裁切和四入口共享压缩 DDR 纳入目标；新增工程待实现/待验证，参数缺失不撤销拓扑选择 |
| 用户输入（2026-10-18） | 队长/HYH/TTY 三人全职，多数新增模块从零开发，均未独立完成完整流片；可申请实验室指导，关键资源未齐。上级期望 2027 年 6 月投片，用户说明可延后三个月；取舍为保留 v1、争取专项支持 |
| 排期建议（2026-10-18） | [团队分工与进度对照](engineering/Team_Responsibilities_and_Tapeout_Schedule.md)：6 月前端交付检查、9 月有条件提交 GDS；不表示上级已批准日期调整或工程已启动。分工、依赖与验收见正文，[交接](handoffs/C00_team_execution_plan.md)记录本轮文档变更 |
| 用户确认 | DDR 供应商可以提供 AXI4 版本，不再把 AXI3 桥列为必选项 |
| 用户要求 | NPU/ISP 数据通路需要绕过 LLC 直接访问 DDR，避免其流量污染 CPU 的 LLC |
| 用户要求 | 提取独立 `cheshire_ara_asic`；不在 Bender 和旧脚本体系上投入过多精力 |
| 用户要求 | 使用多个独立对话分工，交接信息保存在仓库中 |
| 用户要求（2026-10-06） | 软硬件方案先采用当前版本适用的官方建议；官方未覆盖或新增 IP 的抉择才补充自定义方案，见根 AGENTS.md |
| 用户确认（2026-10-06，待实现） | 沿官方 Platform ROM 钩子，以安全启动频率配置 PLL，并按依赖完成必要 IP 配置；保留运行软件可重复访问的配置接口，支持受控动态调整；具体频率/IP/时钟域未冻结 |
| 提取执行建议 | `cv64a6_imafdcv_sv39` + Ara 2 lanes / VLEN 2048，以当前 Ara 仿真配置取值快照作为首个固定基线；见 02 文档 |
| 用户确认方向（2026-10-16，待实现/待验证） | DDR 共享范围采用软件显式交接＋L1D/写缓冲/LLC 硬件范围维护，落实维护窗口、实际完成握手与错误闭环；具体接口仍待细化。GB 本地交接另行管理，见[总纲 §6](engineering/SoC_Architecture_v1_Master_Plan.md#6-跨模块接口与软硬件约束) |
| 未决 | 最终外设保留表、地址分配、DMA 区大小、最终性能/功耗/面积指标 |
| 未决 | 工艺、SRAM 宏、PLL/PAD、DDR 控制器/PHY 细节、DFT/MBIST 和 EDA 工具版本/许可 |
| 用户要求（2026-10-08，教学已交付） | 论文实验需要OS，系统补齐RTOS/Linux；CVA6主线以正确使用为限，ASIC按机制/实例深化。具体OS选型/移植/运行尚未完成，OS不是裸机ASIC提取前置 |
| 未决 | 最终启动介质、OS/RTOS具体版本及平台方案、论文指标、是否需要跨 CPU/设备的共享原子控制数据 |

首次最小提取基线与 v1 产品功能基线分阶段验收；v1 拓扑已确认，最终参数、外设裁切表和未来优化仍按未决输入处理。


## 3. 已交付内容与证据边界

| 事项 | 当前结论与入口 |
| --- | --- |
| VCU118 HelloWorld、既有 FPGA/仿真流程 | 用户报告已跑通；本次未重新执行，不推及 Ara/DDR 全功能或 ASIC 就绪 |
| 依赖与构建 | `.bender/` 是受保护的源码与本地修改；FPGA 工程保留。历史离线解析不是本次编译/仿真 |
| 教材 | [HTML](learning/index.html) / [Markdown](learning/markdown/index.md)：九篇42章、51对页面，同一内容源；[重构交接](handoffs/L01_documentation_restructure.md)记录日期、源码纠错和实际检查 |
| 查询参考 | [配置](configuration/README.md)、[软件](software/README.md)、[层次与工具](software/LAYERS_AND_TOOLS.md)、[片外接口](EXTERNAL_DEVICES_AND_INTERFACES.md)，按问题查阅 |
| RTL 模块指南 | [21 篇正文、24 张 A 图、213 条连接](rtl_modules/README.md)；2026-10-13 最终采用 A 连续走线，B 弃用、C 未采用；[技术交接](handoffs/L01_rtl_module_guide.md)保留审阅与缺口 |
| 工程契约 | [IP/DDR/GB](engineering/IP_DDR_Interface_Contract.md)、[ASIC适配](engineering/ASIC_Adaptation_and_Evidence.md)是正式参考，工程尚未实施 |
| DDR–GB 同步说明（2026-10-16） | [主说明](engineering/DDR_GB_Coherence_Design.md)已纳入用户转交的独立评审及答疑；[供应商会议问题](engineering/DDR_Supplier_Coherence_Questions.md)已按用户提供的 Datasheet V2.1 核对能力、页码及待澄清项，尚无会议答复；保存[评审 Q&A](maintenance/L01/reviews/ddr_gb_coherence_review_qa.md)。输入 `322bd6ce9`；用户确认维护窗口／握手需实现，当前仅修订文档，硬件与故障恢复未验收 |
| 历史检查 | 软件构建、独立教学 Reg 单元、浏览器/图稿检查均只对各次记录的输入有效；按[交接索引](handoffs/README.md)追溯，不合并成一次生产 SoC 验证 |

OS/RTOS 具体平台、镜像溯源、系统启动和向量抢占仍未验收。教材中的 Linux 6.5 源码、SDK 配方版本与 OpenSBI 头声明不是运行证据；RTOS/Linux 教学已交付，OS 不是裸机 ASIC 提取前置。

## 4. 必须共享的技术事实

1. **两层硬件配置不自动联动。** 根 `cheshire.mk` 默认选择不带 V 的 `cv64a6_imafdchsclic_sv39_wb`；`SELCFG=3` 只选择开启 Ara 的 SoC 参数，不能改掉已选 CPU profile。正确向量 profile 是 `cv64a6_imafdcv_sv39`，并排除 CVA6 first-pass decoder stub。
2. **FPGA 配置不等于仿真配置。** `add_sources.vcu118.tcl` 已选向量 profile/ARA/2 lanes/2048；但生成文件正确不证明当前 bitstream 与全部源码一一对应。FPGA 清单也不能直接作为 ASIC 清单。
3. **软件要单独核对。** 根软件默认 ISA 不带 V；Ara 软件入口会加 V。程序需在首条向量指令前启用 VS，浮点还涉及 FS。HelloWorld 设置 VS 并不证明执行了向量计算。
4. **Ara 接口不要按名字误判。** 当前 `gen_cva6_cfg()` 设置 `CvxifEn=0`；相关 `cvxif` 端口名在此组合承载专用加速器/MMU 交互，不是可任意替换的通用插槽。
5. **SPM 使用 LLC 存储阵列。** 默认 128 KiB，Boot ROM 等待自测并配置为全 SPM 后设置栈。可按 way 在运行时切换/混合，但需管理栈、数据、事务和 cache flush。移除 LLC 会同时影响启动片上存储。
6. **ATOP 是 AXI4 之外、来自 AXI5 的原子事务扩展。** 当前主存路径在 LLC 前处理原子操作，下游 AXI4 DDR 无需因此自行实现 AMO。不要用返回错误的 ATOP filter 替代原子执行器。
7. **设备旁路可行，但不是自动一致。** 旁路写不会自动被上游原子/LRSC 监视器看到；CPU/Ara/LLC 缓存副本也可能过期。禁止把“不发 AMO”推导成“普通写不影响原子性”。将原子单元移到 LLC 后面或新增 DDR 互连都不会自动解决这些问题。
8. **裸机也可以使用 GPT。** 本地通用 GPT 镜像规则已注释，Boot ROM 的 GPT/raw 启动解析代码仍在；直接加载 ELF 通常不依赖 GPT。镜像打包停用不等于硬件启动能力被删除。
9. **依赖快照不是完整 SDK 离线镜像。** 可选 benchmark、未初始化子仓库等排除项见 `.bender/README.md`；不要声称所有软件环境都完整。
10. **iDMA控制接口增加运行门槛（L01进阶静态复核）。** `cheshire_idma_wrap`使用64-bit Regbus，`idma_reg64_2d_reg_top`固定DW=32，旧桥未显示lane搬移；原HAL对+0x44/+0x84的32位ID用64位指针，GCC实测拆成两次32位读。需S01/V01独立统一并验收；教材capstone默认BLOCKED/rc16，不表示DMA通过，未改RTL/sw。该wrapper没有DMA完成IRQ。
11. **外设RTL存在不等于当前平台可验证。** fixture的GPIO输入绑零、VGA输出悬空、USB PHY时钟绑零；VCU118未启用I2C/SD/VGA/USB引脚功能，Serial Link未接出。Link隔离/门控输出在SoC悬空，不能据寄存器名推断实际隔离或电源域。详见进阶支持矩阵和时钟图。
12. **Platform ROM 普通返回路径有待修复缺陷（2026-10-06）。** 输入 HEAD `5ddec4fb4` 的 `cheshire_bootrom.S` 在 `jalr t0` 后紧接 `boot_next_stage`，普通返回不会进入内置介质启动入口；当前生成的 ROM 指令也保留该布局。已有官方修复 `9b4c222df72f74f90ab9f36d80ba7b527f92e62b`（#187），本地尚未应用。默认 `PlatformRom=0` 绕过该路径。已登记 S01-B01，启用钩子前须修复、重新生成 ROM 并验收；[证据](handoffs/L01_platform_rom_boot_review.md)为源码及现有指令核对，不是目标仿真通过。

13. **ROM C 栈对齐待复核（2026-10-11）。** 源码默认 SPM 顶端−8 后调用 ROM C main，sp 模16为8；非零 Platform ROM 钩子同样需核对。实际指令、动态影响和修复未验收，见[重构交接](handoffs/L01_documentation_restructure.md)。
14. **新增软件静态疑点未关闭（2026-10-13）。** CLINT `clint_sleep_until()` 早退条件、MTIME 快照及比较寄存器分拆写；I²C EEPROM 分块推进和 STOP 枚举/注释不一致，见[RTL 指南交接](handoffs/L01_rtl_module_guide.md)。只是源码发现，需 S01/V01 定向复核，未修复或动态复现。
15. **近期产品拓扑以 v1 总纲为准（2026-10-18）。** Ara2/AXI64、CPU/Ara 独立输入共享 M5；DDR/GB 显式搬运，四路 F0～F3 接一个 Controller 的 DDR.S0～S3。旧契约第12节的 Ara4/独立支路/CPU待定及三口资料由[总纲冲突表](engineering/SoC_Architecture_v1_Master_Plan.md#91-冲突与替代关系)标明替代；容量/地址/宏/实际四口交付仍待输入，硬件及性能未验收。

## 5. 近期待办及依赖关系

1. **E01 源码提取**：按 02 文档实现固定配置、静态清单和独立 wrapper。
2. **V01 验证、S01 软件**：可先制定测试/软件计划；对新目录的实现与回归依赖 E01 确定的目录和接口。
3. **M01 DDR/共享存储**：可立即做只读分析与接口契约，实际修改拓扑需另行授权并基于提取基线。
4. **I01 图像/NPU、P01 工艺**：先明确外部规格和需求；不要在未有资料时虚构 IP 实现。
5. 外设裁切在最小回归后进行，并先确认产品保留表。Linux/RTOS 不作为当前裸机提取的强制前置。
6. **S01-B01 / P01 平台启动**：先按官方修复处理 Platform ROM 返回缺陷，再定义安全启动 PLL、配置接口及运行时调整契约。外部配置可由后续固件读取并校验后应用；Boot ROM/固定平台 ROM 与可更新固件的职责、其他 IP 的初始化阶段见 [平台启动与配置约定](03_Platform_ROM_Clock_IP_Configuration.md)。本次只记录，不授权实施，不冻结附件中的频率、电压或多 PLL 示例。

任务定义、负责文件及可复制的新对话提示词见 [AGENT_TASKS.md](AGENT_TASKS.md)。


## 6. 文档维护决策

- 当前阅读总入口：[00_README](00_README.md)；Agent 按[定位指南](AGENT_DOCUMENTATION_GUIDE.md)只读相关主题。
- 2026-10-11 用户移除 `learning_backup/`，不得重建；旧“保留旧站”仅为当日历史状态。旧哈希清单和目录外独立证据保留。
- 旧图目录现为 `2026-10-11_native_reconstruction`，不得恢复旧目录名。现行工程契约在 `engineering/`，不能作为过程日志清理。
- 2026-10-13 本次让 A 阅读与检查独立于 B/C，历史试绘退出主路线；压缩本页重复过程叙述，日期、输入、失败/未关闭项仍在原主题交接与原始证据中。完整整理前快照、恢复清单和本次检查见[组织交接](handoffs/L01_documentation_organization.md)。
- 小型维护更新已有主题 handoff；过程报告归 `maintenance/`，不在入口追加聊天流水。用户报告、源码确认、历史产物、本次实测和方案建议须区分。
