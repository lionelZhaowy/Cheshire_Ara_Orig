# 多对话任务分工与启动方式

创建于 2026-09-20。本表是任务路由，不是后台任务调度器，也不表示用户已授权实施所有任务。C00 协作文档初始化及 L01 配置/软件文档、离线入门教材已完成；M01/P01本轮仅完成文档子任务，其余工程实施未启动。

## 1. 任务表

| ID / 建议对话标题 | 当前状态 | 主要交付 | 依赖与写入边界 |
| --- | --- | --- | --- |
| C00 项目协调与交接 | 协作入口及三人分工/条件排期文档完成（2026-10-18）；工程未启动 | 汇总状态、决策和冲突；[团队排期与对照表](engineering/Team_Responsibilities_and_Tapeout_Schedule.md)、[本主题交接](handoffs/C00_team_execution_plan.md)；不包办所有技术任务 | `AGENTS.md`、共享状态/任务索引；人员排期不替代 Agent 授权，不顺手修改 RTL |
| E01 固定配置 ASIC 源码提取 | 未开始 | 独立 `cheshire_ara_asic/`、固定配置、静态清单、可运行入口、来源记录 | 按 02 文档；保护旧工程；首轮通常拥有新目录骨架及清单的编辑权 |
| V01 仿真与验收 | 未开始 | 回归用例、编译/展开/运行结果、可重现日志 | 计划可先做；新目录验证依赖 E01；与 E01 协调 TB、filelist 编辑权 |
| S01 裸机软件与启动 | 未开始 | 启动/链接/软件构建、向量结果验证、启动路径分析 | 与 E01 确认目录及地址布局后管理新目录软件；原 `sw/` 默认只读 |
| S01-B01 Platform ROM 返回路径修复 | 未开始（2026-10-06 已登记，尚未授权实施） | 对照官方 #187 最小修复、同步生成 ROM、验收正常返回及默认启动；[规格](03_Platform_ROM_Clock_IP_Configuration.md#s01-b01) | S01 主责，V01 验收、E01 同步提取；旧启动源码/生成 RTL 修改需另行明确授权，禁止为修复升级全工程依赖 |
| M01 DDR 旁路与存储一致性 | M01-D文档完成；工程未实施 | [IP/DDR接口契约](engineering/IP_DDR_Interface_Contract.md)、输入责任与验证矩阵 | 待供应商/I01真实接口及E01基线；top/config/address map修改须另行授权并协调 |
| I01 LVDS、ISP 与 NPU 集成 | 未开始 | 外部规格清单、控制/数据/中断接口、带宽预算和接入方案 | 依赖传感器/IP 资料和 M01 内存契约；RTL 实施另行明确 |
| P01 ASIC 工艺与实现准备 | 文档盘点及资源/封装预规划交付（2026-10-18）；工艺适配未实施 | [ASIC适配与证据手册](engineering/ASIC_Adaptation_and_Evidence.md)、[资源预算与封装专题](engineering/SoC_Resource_and_Packaging_Plan.md)、[主题交接](handoffs/P01_soc_resource_packaging.md) | 目标 SMIC55 工艺标识已确认；实际宏/PLL/PAD/PHY/封装/DFT/时序签核仍待配套输入及工程授权 |
| L01 学习与源码问答 | 教材整理完成；DDR–GB 评审答疑与文档修订完成（2026-10-16），工程未实施 | [教材](learning/index.html)、[21篇RTL模块指南](rtl_modules/README.md)、[RTL指南交接](handoffs/L01_rtl_module_guide.md)、[组织交接](handoffs/L01_documentation_organization.md) | 软件全链、trap/OS、ASIC机制与测量已落地；新增参考页未改课程生成页。无真人试读/本轮目标运行；生产缺口保留 |

2026-10-16 L01：DDR–GB 独立评审已由用户转交并完成文档处理，见[主题交接](handoffs/L01_cache_coherence_architecture.md)、[评审 Q&A](maintenance/L01/reviews/ddr_gb_coherence_review_qa.md)及[供应商会议问题](engineering/DDR_Supplier_Coherence_Questions.md)。供应商会议问题已对照 Datasheet V2.1 更新，区分手册已知能力和跨口／错误／恢复未决项。维护窗口／握手列为用户确认的实现要求；本轮仅修改 Markdown，接口与恢复硬件尚未实施。

2026-10-18 L01：已交付[实施难点专题与 13 幅可编辑图](engineering/Implementation_Challenges_and_Open_Questions.md)，供 M01/I01/S01/V01/P01/E01 按责任和门槛接手；[主题交接](handoffs/L01_implementation_challenges.md)记录文档与图稿检查。工程任务状态、人员分工和条件排期不变。

2026-10-18 L01图稿整理：[图稿总索引](diagrams/README.md)已建立，backup_no_use引用审查与迁移完成；仍用配图/依赖已移回，历史旧版归档。详见[组织交接](handoffs/L01_documentation_organization.md)，工程任务状态不变。

同一任务需要进一步拆分时用 `V01-a` 等子编号。不要为了分工一次性创建大量空专题文件。

2026-10-13 RTL 指南：正式采用 A 连续走线；B/C 试绘已归档，活动生成与检查只依赖 A。源代码和工程验证状态未变。

2026-10-11 文档清理：用户已授权删除 learning_backup，728 文件移出仓库，现行教材入口及检查规则同步；其他备份/图稿/独立证据不在此次删除范围，勿据旧“保留旧站”描述重新生成该目录。

教材编写的历史规划、Prompt、审查和实施报告已统一归入 [maintenance/L01](maintenance/L01/README.md)，不再作为顶层学习文件；新对话按该索引按需追溯，不机械重跑旧 Prompt。

2026-10-11 L01 补充交付：[片外器件与接口参考](EXTERNAL_DEVICES_AND_INTERFACES.md)、[主题交接](handoffs/L01_interface_reference.md)。交接规则已改为任务主题文件持续更新，普通答疑不单独建日志；历史命名迁移不代表重新实施或验证历史任务。

2026-10-12 L01 图稿补充：使用 `industrial-svg-pptx`，完成旧图目录中 9 张非教程独立图的工业风格版；[新旧对照与下载](diagrams/2026-10-12_industrial_redraw/index.html)、[主题交接](handoffs/L01_native_reconstruction.md)。教程图及原目录不变，原生 SVG/PPTX 结构检查通过；Office 显示/编辑与目标硬件运行未新增验证。

## 2. 每个对话只带必要上下文

所有对话先读根 `AGENTS.md` 和 `PROJECT_STATE.md`。额外阅读：

| 任务 | 必读专题 | 按需查阅源码/教程 |
| --- | --- | --- |
| E01 | 02 全文 | `Bender.local`、Ara 集成 Makefile、SoC/配置和技术单元；01 第 3、10 节 |
| V01 | 02 第 3、7、9 节及 E01 最新交接 | `target/sim/src/`、DPI、01 第 6 节 |
| S01 / S01-B01 | 02 第 7 节及 E01 配置/地址交接；[Platform ROM 规格](03_Platform_ROM_Clock_IP_Configuration.md)及[缺陷证据](handoffs/L01_platform_rom_boot_review.md) | Boot ROM、`crt0.S`、`common.ldh`、01 第 5、7、9 节；官方修复 #187 |
| M01 | 02 第 8 节 | `cheshire_soc.sv` 的 atomics/LLC、LLC/AXI 实现、01 第 8、9 节 |
| I01 | M01 已确认接口契约 | 自有 IP 资料、SoC 控制/中断扩展边界 |
| P01 | 02 第 6、9 节；[Platform ROM 决策与接口边界](03_Platform_ROM_Clock_IP_Configuration.md) | `tech_cells_generic`、CVA6/Ara/LLC 存储实例、PLL/PHY 授权资料、01 第 10 节 |
| L01 | 当前问题对应小节 | 当前问题相关源码即可 |

初次接手不重复全仓库审计。遇到过期结论或缺失证据时，定向重新检查。

2026-10-06 用户已确认平台启动方向：沿官方 Platform ROM 钩子配置安全启动 PLL，并按需求安排其他 IP 初始化；保留运行软件可重复配置的接口。外部配置、受控调频和异常回退的具体实现需在 IP 契约确定后交付。此记录不表示已实现 PLL/DDR、运行时调频或 Linux 驱动，也不授予修复源码权限。

## 3. 启动任务与历史指令

任务表只提供路由；按当前用户请求确定范围，不自动执行旧 Prompt。原可复制任务指令已退出主入口，整理前全文保存在[维护归档](maintenance/L01/archive/documentation_organization/README.md)。E01 用现行02规格，其他任务按上表和最新主题交接接手。

## 4. 并行工作的实际约定

1. 用户选择任务后，对话先声明任务 ID、输入提交/未提交变更、计划修改路径。不要把本表中的“未开始”视为排他性锁。
2. 可并行开展 E01 提取、M01 设计分析、P01 盘点、I01 规格收集；V01/S01 可先规划。多个对话同时修改新目录时，先分配文件编辑权。
3. 同目录环境中的 Git 状态属于所有对话共享状态；不要擅自 checkout、stash、reset、提交他人的变更或清理输出。
4. 每个任务使用独立构建输出目录/日志名，避免共用 `work`、`simv`、Vivado 工程缓存。大型仿真/综合的机器资源与许可证应先协调。
5. 地址、配置和接口变更必须交接给依赖任务；不能只改 RTL 不同步软件/测试，也不能只更新文档就声称集成完成。
6. 实质变更更新 `handoffs/<任务ID>_<主题>.md`，在文件头追加日期、输入版本和修改/验证记录；同主题不逐日新建，普通答疑不单独建日志。独立评审保留角色后缀。发现更新冲突时不覆盖，交给 C00 或用户。

## 5. 状态和完成定义

状态只用：未开始、进行中、待输入、待验证、完成。进行中记录对话标识/负责范围；待输入记录具体缺失项；完成必须有交付和证据。仅写了方案时说“方案完成”，不把对应 RTL 任务设为完成。

每个任务的最终交接至少给出：做了什么、改了哪些文件、实测了什么、还缺什么、下一位从哪里继续。

2026-10-11 L01仅完成文档实施：同一HTML内容源生成51对HTML/Markdown；主阅读顺序、参考职责、字段解释和页面验收见最新交接。S01/V01新增源码复核输入为ROM C入口栈对齐；实际指令、动态影响和生产修复未在本轮执行，不授予旧源码修改权限。
