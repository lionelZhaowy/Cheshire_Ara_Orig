# 多对话任务分工与启动方式

2026-10-26 E01 [剩余工作区按用户授权发布](handoffs/E01_fixed_vector_extraction.md#workspace-publish-20261026)：R两处原诊断文件已单独提交并推送`29f1e6f9`，远端读回一致，受管工作区干净；本地原17修改/4新增纳入本次提交，目标为个人`Cheshire_Ara_Orig/main`。未改功能源码或重跑仿真，F保持；下方“诊断/本地未提交”为此前快照。

创建于 2026-09-20。本表是任务路由，不是后台任务调度器，也不表示用户已授权实施所有任务。C00 协作文档初始化及 L01 配置/软件文档、离线入门教材已完成；M01/P01本轮仅完成文档子任务，其余工程实施未启动。

## 1. 任务表

2026-10-26 E01 [LLVM默认编译器迁移已完成](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-resume-20261026)：先R38新ELF/40项主矩阵及两探针，再F49新ELF/51项独立运行；正常PASS为36/47，另各SPI限定告警1、保留LLC未完成1及预期负例2。混合465/0＋22字节0错、P7 68组/13416项和P6 508组/38452项0错，F Ara11目标59case/147比较0错。当前目标软件默认LLVM20.1.0/newlib/compiler-rt，无目标GCC/libgcc依赖；宿主g++保留，输出`sw/build/llvm_p7`。原件/after两地实际恢复及结果包核对通过，未改RTL/参数/Boot ROM；随后R八文件已提交并推送[`6f2b2a3b`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/6f2b2a3be50eeb15eb93c0ada2164029a102c94c)，远端main读回一致。R两份原诊断修改及本地17修改/4未跟踪保留，未混推；详见[发布与剩余内容](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-github-push-20261026)。旧GCC/输出保留。下方“GCC默认/迁移停止”为历史。

2026-10-26 E01 [P7已同步正式工程并验证，参考工程已提交GitHub](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-reference-formal-sync-20261026)：F自身重建RTL及14 ELF后，17次串行仿真全部PASS；P7共68组/13416项0错，归档原LLVM向量及两标量均未重编即465/0、复制22字节0错，12回归通过。F保留既有布局，维护目标29→31，日常7/Ara11保持；其余1046原输入及R全部4394输入内容/权限保持。随后仅R四份P7源码提交并推送`4e30feec`，两处诊断修改保留；两地前后恢复/归档核对完成。默认仍GCC13.2，LLVM构建规则尚未重新适配、迁移验收未完成；未综合/板测/公开上游PR。下方仅R、未提交及F未同步均为前阶段历史。

2026-10-26 E01 [P7仅R修复并验证通过](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-emul-local-fix-20261025)：dispatcher＋VALU共32增4删，复用已有状态/队列；68组/13416项0错，原LLVM失败ELF未重编即465/0及复制22字节0错，两标量和12回归全PASS。22次实际运行保留旧版/中间失败，4318其他原输入及两处诊断修改保持，双份备份/实际恢复检查通过。R未提交修复保留，F未同步、LLVM迁移未恢复，未综合/发布。下方候选回退为前轮历史。

2026-10-25 E01增量：[P7候选未通过并已回退](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-implementation-result-20261025)。固定#483局部候选编译成功，但初版VMACC m2仍错，独立EMUL缺口超出计划；非零vstart控制经用户批准替换，修订ELF已构建未运行，17项验收未执行。R 4321原输入/原差异恢复、F未写、LLVM迁移仍停止，无提交推送。下段为此前LLVM分析阶段。

2026-10-25 E01此前增量：[LLVM迁移](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-vector-failure-analysis-20261025)阶段A及R36 ELF构建通过，新增自动向量化运行失败后已恢复R六处源码，F未写。GCC/LLVM同源标量、换向量目的寄存器均465/0；布局模型与257项trace一致，彼时源重排缺口尚未实施RTL修复，迁移未完成。原P1–P6验收及其他任务边界保持。

| ID / 建议对话标题 | 当前状态 | 主要交付 | 依赖与写入边界 |
| --- | --- | --- | --- |
| C00 项目协调与交接 | 协作入口及三人分工/条件排期文档完成（2026-10-18）；工程未启动 | 汇总状态、决策和冲突；[团队排期与对照表](engineering/Team_Responsibilities_and_Tapeout_Schedule.md)、[本主题交接](handoffs/C00_team_execution_plan.md)；不包办所有技术任务 | `AGENTS.md`、共享状态/任务索引；人员排期不替代 Agent 授权，不顺手修改 RTL |
| E01 固定配置 ASIC 源码提取 | P1–P7及LLVM默认迁移已验证 | [版本、测试与回退](maintenance/E01/planning/official_upstream_maintenance_assessment.md#reference-formal-sync-20261024) | R已验证上云5986ba02；F独立41次运行、39项对照一致，前后源码及证据双份备份/恢复核对完成。原配置/wrapper/静态入口和既有限制保持；[Ara首批11项迁入F并验证](maintenance/E01/planning/server_reference_extraction_plan.md#ara-tests-migration-plan-20261025)：59case/147比较，17 PASS＋1预期负例；既有4回归一致，两地备份/恢复核对完成，[特殊测试/ld整理](maintenance/E01/planning/server_reference_extraction_plan.md#special-tests-organization-plan-20261025)已完成：9文件移动、默认7/维护24，32 ELF对照及7次PASS，保留后续文档并记录回退合并要求；[第3轮provenance整理](maintenance/E01/planning/server_reference_extraction_plan.md#provenance-organization-plan-20261025)已完成：35历史文件归类、顶层43→8；内容/引用/两地恢复检查通过，未构建仿真；[ABC核查](handoffs/E01_fixed_vector_extraction.md#abc-review-20261025)完成，只改本地图文；P3非整拍VL异常屏蔽列待补测，未新增运行；[本轮R测试](maintenance/E01/reports/official_pr_failure_fixes_review.md#ara-maskb-tests-20261025)：#475三种序列复现，#479各120组/8056检查通过但窗口0，#450相符停滞及延迟旧值待处理，原P2标量483项再通过；未修RTL/F；[P6候选检查](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-candidate-check-20261025)：#475/#469局部/#480部分有效，仍有历史数据归属及compress全不选/跨字错误；仅独立副本，生产未改，#479暂不继续处理；[P6实施完成](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-fix-20261025)：3RTL＋2C/Make，17次运行16 PASS＋1旧版预期停滞，生产8次全PASS，508组/38452项0错；4298其他输入保持，两地前后恢复验证，R未提交/推送，F未同步；前述候选状态由本结果更新；[P6提交及F复验完成](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-reference-formal-sync-20261025)：R六文件`cb20a03c`已推送；F按regressions布局同步、7/29/11构建组，11次全PASS、P6 508组/38452项0错；1043其他输入保持、两地恢复/归档通过，前述F未同步状态由本结果更新；[LLVM默认迁移完成](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-resume-20261026)：R38/F49新ELF、40/51项各按判据完成，普通PASS36/47，原SPI/LLC边界保留；恢复检查与两地结果包通过，R八文件LLVM提交6f2b2a3b已推送main；其他诊断和本地修改保留 |
| V01 仿真与验收 | 未开始 | 回归用例、编译/展开/运行结果、可重现日志 | 计划可先做；新目录验证依赖 E01；与 E01 协调 TB、filelist 编辑权 |
| S01 裸机软件与启动 | 未开始 | 启动/链接/软件构建、向量结果验证、启动路径分析 | 与 E01 确认目录及地址布局后管理新目录软件；原 `sw/` 默认只读 |
| S01-B01 Platform ROM 返回路径修复 | 未开始（2026-10-06 已登记，尚未授权实施） | 对照官方 #187 最小修复、同步生成 ROM、验收正常返回及默认启动；[规格](03_Platform_ROM_Clock_IP_Configuration.md#s01-b01) | S01 主责，V01 验收、E01 同步提取；旧启动源码/生成 RTL 修改需另行明确授权，禁止为修复升级全工程依赖 |
| M01 DDR 旁路与存储一致性 | M01-D文档完成；工程未实施 | [IP/DDR接口契约](engineering/IP_DDR_Interface_Contract.md)、输入责任与验证矩阵 | 待供应商/I01真实接口及E01基线；top/config/address map修改须另行授权并协调 |
| I01 LVDS、ISP 与 NPU 集成 | RX 时序说明/图稿完成（2026-10-23）；RTL 未开始 | 外部规格清单、控制/数据/中断接口、带宽预算和接入方案 | 依赖传感器/IP 资料和 M01 内存契约；RTL 实施另行明确 |
| P01 ASIC 工艺与实现准备 | 资源/封装预规划更新至 v1.7（2026-10-26）；工艺适配未实施 | [ASIC适配与证据手册](engineering/ASIC_Adaptation_and_Evidence.md)、[资源预算与封装专题](engineering/SoC_Resource_and_Packaging_Plan.md)、[主题交接](handoffs/P01_soc_resource_packaging.md) | 目标 SMIC55 工艺标识已确认；实际宏/PLL/PAD/PHY/封装/DFT/时序签核仍待配套输入及工程授权 |
| L01 学习与源码问答 | 教材整理完成；DDR–GB 评审答疑与文档修订完成（2026-10-16），工程未实施 | [教材](learning/index.html)、[21篇RTL模块指南](rtl_modules/README.md)、[RTL指南交接](handoffs/L01_rtl_module_guide.md)、[组织交接](handoffs/L01_documentation_organization.md) | 软件全链、trap/OS、ASIC机制与测量已落地；新增参考页未改课程生成页。无真人试读/本轮目标运行；生产缺口保留 |

2026-10-23 I01/P01（历史输入，已由下述 v1.7 替代）：已按合作方确认的逐行 96×128 像素、12288 行和 RX 最低 8 时钟要求更新[资源专题](engineering/SoC_Resource_and_Packaging_Plan.md#lvds-rx-timing)，交付[两张 WaveDrom 接收时序图](diagrams/2026-10-23_lvds_rx_timing/README.md)。SDR/上升沿/LSB 先发仅当前绘图约定，行帧同步/消隐仍待定；按 RX 8/TX 暂定 16 计算 560/728 信号，30 FPS/500 Mbit/s 保持。见[P01交接](handoffs/P01_soc_resource_packaging.md#lvds-rx-timing-20261023)；仅文档及新时序图，工程实施与 E01 状态不变。

2026-10-26 I01/P01：RX 因面积限制改为 64 数据＋4 时钟、1C16D；TX 128 数据＋暂定 16 时钟保持。双向 LVDS/条件信号为 424/592；500 Mbit/s 时 RX 无法满足既定 30 FPS，取舍待确认。已更新[资源专题](engineering/SoC_Resource_and_Packaging_Plan.md)及相关说明，旧时序图标为历史输入；见[P01 交接](handoffs/P01_soc_resource_packaging.md#lvds-rx64-20261026)。仅文档与算例，工程实施与 E01 状态不变。

2026-10-22 L01/I01 最小图稿修订：从原 3600×2025 单页 v1 增加 RX 像素直通线、TX FIFO 前 2:1 MUX 和 TX 寄存器短控制线；取消右扩展布局及外部强制，切换要求 CPU/配置总线可用。[现有目录图稿](diagrams/2026-10-22_soc_lvds_bypass/README.md)、[设计说明](engineering/LVDS_Raw_Bypass_Design.md)及[主题交接](handoffs/L01_lvds_isp_gb_soc_topology.md#lvds-minimal-v1-20261022)已同步；反压隔离、CDC 和吞吐待实现验证。仅完成图稿与说明，I01/P01 工程实施未开始，E01 不受影响。

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

本地仓库对话先读根 `AGENTS.md` 和 `PROJECT_STATE.md`。服务器任务只传必要上下文，并遵守服务器已有工作区约定；不要求全盘上传本地文档。独立子系统按其自身约定推进，不强制进入本地 SoC 审批流程。职责边界见[本地与服务器 Agent 约定](../AGENTS.md#local-server-collaboration)。本地额外阅读：

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

<a id="server-task-brief"></a>

### Cheshire SoC 服务器任务：最小下发与回报

2026-10-20：用户已暂停将 E01/Bender 剥离相关任务交给服务器 Agent，改由本地 Agent 执行。2026-10-21补充：允许本地子Agent协助规划、核查和评审，服务器操作仍由本地WSL SSH完成，主Agent统一更新计划/交接/共享文件；不扩大当前仅规划权限。以下格式保留供其他适用任务使用，不作为下发服务器Agent实施E01的依据。

直接用于任务消息，不要求新建文件；模板须明确填写并获授权后才成为可执行任务。长期保护约束按本次适用范围摘录，任务背景随输入更新，不依赖上一对话的记忆。

```text
任务：ID / 具体目标；完成什么后停止。
输入：主机、工程路径、预期主工程/依赖版本及已有差异；现场重新核实。
背景：本任务需要的配置、已确认决策、必要修正与未关闭问题。
允许操作：可修改文件/目录、构建与运行权限、测试和资源边界、输出位置。
保护：适用的受保护对象、禁止事项、服务器已有约定；范围内自主，越界报告。
验收：明确通过判据及未测项口径。
交付：结果摘要、差异和证据位置；完成后不自动进入下一任务。
```

E01 下发时明确参考 `~/CheshireAraPULP`、既定目标 `~/CheshireAra`，实施前核实目录状态；保护参考工程、本地 FPGA/RTL/sw、`.bender` 源码和差异、服务器 TTY 工程及 `/opt`。首次提取不升级依赖、不改硬件参数、不裁切外设、不加入新 IP；保留 FS 修正及来源、许可证，Bender 至多用于必要的一次性离线解析。这些约束不表示已授权提取或运行。

```text
结论：完成 / 部分完成 / 阻塞；结论适用范围。
实际输入：版本、差异、有效配置、工具；与任务预期不一致之处。
改动：文件列表、原因、可审阅差异位置；是否超出范围。
验证：工作目录、实际命令、构建及 ELF/image 标识、结果、退出码和日志位置。
未关闭项：已有/新增问题、未测项，是否阻塞下一步及理由。
需要决定：无则写“无”；下一步只建议，不自动执行。
```

服务器源码、配置、工具和日志是实现事实依据；本地保存需求、决策及评审结论。每次构建绑定源码/清单、有效配置、差异、工具和输出位置；每次运行绑定实际 `simv` 与 ELF/image 路径及 SHA256、参数、日志和退出状态，不能混用同名 ELF、旧日志或不同构建。构建库及运行依赖一并定位，不把单个 `simv` 当作完整构建。复用已有产物及必要手动记录，不新增自动归档框架。

日志、FSDB、trace 和构建库主要留服务器，本地通常接收摘要、差异及证据位置；配置/清单或补丁存在争议、摘要不能解释失败时，按需取回具体文件或日志片段。用户按任务转交下发与结果；SoC 记录更新既有主题交接，独立子系统保留自身记录，集成时提供必要摘要。

## 4. 并行工作的实际约定

2026-10-20 同步用户已确认分工：Cheshire SoC 由本地统筹、服务器实施；本地按本次差异和现场证据评审，可在授权内 SSH 只读核查，不同时修改服务器任务负责的文件和产物。独立子系统由用户/负责人直接与服务器 Agent 协作；本表 I01 的 SoC 集成职责不构成对子系统内部工作的逐项审批。此次不改变工程任务状态或验收顺序，具体授权以任务说明为准。

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
