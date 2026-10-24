# E01 / 固定向量提取与服务器参考工程

## 修改记录

| 日期 | 角色 | 输入版本 | 修改与验证摘要 |
| --- | --- | --- | --- |
| 2026-10-23 | E01失败诊断与P3–P5局部修复；本地WSL SSH | C `p3-stopped` / `7b1c13f…` | P3残留SIMD mask与P4相邻段覆盖已定位修复，P5分RTL/HAL验证通过；`p3-pass`/`p4-pass`/`p5-pass`及两地备份已校验。累计7次新运行完成（6 PASS、SPI原限定告警接受），最终`p1-p5-pass=5e0f973…`、双份备份及R/F保护检查通过；见[当前记录](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p3-p5-repair-20261023) |
| 2026-10-23 | E01继续P3–P5；本地WSL SSH实施 | C `p2-pass` / `7ac2e12…` | P3官方一行修改后同ELF177/20→177/6，0/0多报DZ消失但其他向量fflags仍失败，按计划停止；`p3-stopped`=`7b1c13f…`，双份源码/18成员证据归档校验完成，R/F不变。P4/P5及累计回归未继续，见[结果及恢复](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p3-stop-20261023) |
| 2026-10-23 | E01 P2定位/局部修复；本地WSL SSH、本地子Agent只读复核 | C `p2-stopped` / `5a92bd4…` | 16项mask尾位计数与15项标量提前回应分别定位、单项修复；同ELF835/31→15→0，124/483补充检查及五项回归通过。`p2-pass`=`7ac2e12…`，双份bundle/50成员证据归档校验完成；R/F不变，P3–P5未继续，见[修复与回退](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p2-repair-20261023) |
| 2026-10-23 | E01 P1–P5阶段B；本地WSL SSH实施、本地子Agent只读评审/测试草稿 | R实际1084输入及既有修正；C baseline `043633d…` | P1定向及向量/RVV回归通过；P2官方补丁后835项仍31失败，按停止条件结束，P3–P5未实施。`p1-pass`与`p2-stopped`及两地bundle/日志保留，R/F保护检查全匹配；见[实测与回退](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p1-p5-stage-b-stop-20261023) |
| 2026-10-23 | 用户确认维护方向 | 沿本轮A/B评估输入，生产源码未变 | 用户接受在现有分支基础上选择性采用官方后续补丁，不迁移main；相关PR已由另一Agent梳理，本次询问补丁必要性的判断方法。此确认不表示采用所有候选或整包升级；本轮未重复实施补丁 |
| 2026-10-23 | E01开发基线评估；本地主协调及三项本地只读调查/复核 | L `c9abbb489…`；R `e040b7bbc…`加实际修正；F现行来源；官方main `6c6dd5e…` | 更新[既有评估](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#main-baseline-decision-20261023)，建议现阶段A；锁/实际依赖、接口、团队定制及修复覆盖核对，临时Git合并11/14冲突。未改生产、构建、目标仿真或迁移；建议不是用户已采纳决定 |
| 2026-10-23 | E01官方维护阶段A；本地主协调及三名本地只读子评审 | 本地`c9abbb489…`；R基底`e040b7bbc…`＋实际修正；F现行配置/入口 | 26依赖HEAD/差异及962目标来源哈希核对，官方diff/PR/后续问题调查，交付[维护评估与B/C计划](../maintenance/E01/planning/official_upstream_maintenance_assessment.md)。未改服务器、升级依赖、构建/运行；候选全部待验证，停止等待选择与B授权 |
| 2026-10-22 | E01 配置入口合并；本地子Agent只读复核 | 本地 `c9abbb489…`；正式工程修改前快照 | 独立cfg包合入cheshire_pkg，仅DefaultCfg.Ara默认0→1、有效值保持1；新目录重建soc/slink_rx，14次前后对照为12 PASS及2次SPI限定告警，配置/位宽/trace一致；默认值与恢复备忘见[第7.12节](../maintenance/E01/planning/server_reference_extraction_plan.md#config-entry-merge-defaults-20261022) |
| 2026-10-22 | E01 compile/start入口简化，本地实施与验证 | 本地`c9abbb489`；服务器正式工程1023份非输出文件快照 | 用户明确实施：Bash compile/start、输出复用WARNING、规范结果解析和Make依赖；10次串行仿真为7 PASS、SPI限定告警2、两项负例1/124，静态/依赖/范围检查通过。替代原run.py/每次新目录规则，详见[结果](../maintenance/E01/planning/server_reference_extraction_plan.md#entry-scripts-result-20261022) |
| 2026-10-22 | E01 用户文档使用定位补充 | 本地`c9abbb489`；沿用已交付两份指南 | 用户明确当前仅供个人使用和记录，后续团队共享前需重新审查、修改个人相关事项及依赖聊天背景的说明，使其他成员能够独立理解。仅记录后续要求，本轮未SSH或修改服务器文档 |
| 2026-10-22 | E01 独立工程用户文档阶段B，本地撰写/实施/复核 | 本地`c9abbb489`；服务器清理后的实际工程 | 用户同意后写入两份`docs/`指南、根README导航和现有来源清单相应记录；最终11段Bash语法/36链接、命令/配置/判据及范围检查通过，其他1019份文件保持，未构建或仿真。见[交付结果](../maintenance/E01/planning/server_reference_extraction_plan.md#user-documentation-result-20261022)，阶段完成并停止 |
| 2026-10-22 | E01 独立工程用户文档阶段A，本地规划/只读复核 | 本地`c9abbb489`；服务器清理后`~/CheshireAra`实际文件 | 只读核对README、compile/run.py/Make、配置/wrapper与启动/链接/来源摘要；建议两份用户文档、根README导航及现有来源清单更新，记录新输出要求、固定参数检查和软硬件手工对应；见[文档规划](../maintenance/E01/planning/server_reference_extraction_plan.md#user-documentation-plan-20261022)。未创建服务器docs、写服务器、构建或仿真，等待明确同意撰写 |
| 2026-10-22 | E01 验证后清理，本地WSL SSH | 本地`c9abbb489`；已完成2B–2D工程 | 用户授权后将2033份证据文件压缩并逐文件校验，删除旧输出/缓存和搬迁副本，保留正式源码及入口，净释放约3.44 GiB；见[清理结果](../maintenance/E01/planning/server_reference_extraction_plan.md#post-validation-cleanup-20261022) |
| 2026-10-22 | E01 步骤2D，本地实施/本地独立评审 | 本地 `c9abbb489`；服务器 `e040b7bbc`＋实际修正；原2B/2C源码保持 | 新位置从源重建四种硬件、23单元库/17ELF/镜像，31项对照保持基准分类；37份实际访问记录无旧工程/Bender/下载依赖参与，保护检查通过。保留run.py及已知限制，纠正全面禁网误解；见[2D结果](../maintenance/E01/planning/server_reference_extraction_plan.md#step2d-result-20261022)，阶段完成并停止 |
| 2026-10-22 | E01 步骤2C，本地实现/本地独立评审 | 本地 `c9abbb489`；服务器 `e040b7bbc`＋实际修正；2B硬件保持 | 迁入90份软件来源文件及一份Make，从新输出重建23单元库、17ELF和SPI镜像；19次对照分类符合既定判据，原ROM限定告警和3项LLC失败保留。保护检查通过，见[2C结果](../maintenance/E01/planning/server_reference_extraction_plan.md#step2c-result-20261022)；停止等待2D |
| 2026-10-21 | E01 步骤2B，本地协调/实现及本地子评审 | 本地 `c9abbb489`；服务器 `e040b7bbc`＋实际修正；目标 `~/CheshireAra` | 已提取624个原设计源/48组，集中配置/68端口wrapper及必要仿真配套从新输出重建；31次对照分类与参考一致，限定ROM告警和3项LLC旧失败保留。保护输入/产物不变，软件重建及搬迁验证未做；见[实施结果](../maintenance/E01/planning/server_reference_extraction_plan.md#step2b-result-20261021)，停止等待2C |
| 2026-10-21 | E01 步骤2A，本地主协调及三项只读子评审 | 本地 `c9abbb489`；服务器 `e040b7bbc`＋实际修正，26依赖HEAD与锁一致 | 已完成服务器源码/清单/产物/目标目录核查，更新[2A–2D计划](../maintenance/E01/planning/server_reference_extraction_plan.md#step2-plan)。步骤1结果及保留限制作为对照基准；无需先修完历史问题。用户补充允许本地子Agent，不委派服务器Agent。仅本地文档修改，未提取、导出Bender、构建、仿真或写服务器；等待2B授权 |
| 2026-10-21 | E01 用户验收决定 | 沿用第 12 节实际运行与定位结果 | 用户确认忽略原 ROM SPI 配置结构体 padding 含 X 的已知告警，接受本次 ROM/SPI 功能验收，不再列为待修或阻塞。仅豁免已核对的填充字节事件；其他断言及此前 DMA 限制保持。只更新现有文档，未 SSH、改 ROM/入口或重新测试；原日志和入口返回 2 的记录保留 |
| 2026-10-21 | E01 剩余参考验收，本地 WSL SSH | 本地 `c9abbb489`；服务器 `e040b7bbc`＋既有修正；复用 simv `e16fc6a7…` | ROM/SPI 自主运行 HelloWorld，48 KiB 搬运 trace 与镜像一致，但原 ROM padding 含 X 触发四条断言，原因已定位、未改 ROM。官方非 stub CSR、RVV 5976 项、访存原子 572 项均通过；负例目标41/simv0/入口1，断言入口2，故意限时124。339 项保护输入与根 diff 保持，无 RTL 重建或生产修改。见[完整结果](../maintenance/E01/reports/reference_rebuild_check.md#remaining-acceptance-20261021)；本轮检查结束，严格参考验收未全满足，不开始提取 |
| 2026-10-21 | E01 Serial Link RX 验证 | 服务器现有生产源码，新构建 simv `9cbc6b8d…` | 经原 LLC 写 DDR：64 KiB、CPU 并发 192 KiB、非对齐间断 8193 B 均通过；刷新后核对全部 DDR 数据及保护区，CPU/主机退出均 0。每次一个 RX 写突发，未覆盖多在途反压或同缓冲区缓存交接；339 输入及根 diff 保持。见[测试结果与范围](../maintenance/E01/reports/reference_rebuild_check.md#slink-rx-llc-ddr-20261021)；未修改生产 RTL/HAL或实施下一任务 |
| 2026-10-21 | E01 应用通路 DMA 验证 | 既有 #80/#204 正式 simv；后端按生产源码新构建 | 独立端点模型在默认 256/限制 64 拍、三种延迟下各 78 笔通过；SoC 共享 LLC 十组 4 通过/6 停滞，DDR 旁路两组通过。保留短窗口、测试副本 scoreboard 首轮失败并说明原因。339 输入及根 diff 保持，未改生产 RTL/HAL。用户决定不继续投入 SPM 内部死锁修复，按既定 DDR↔GB 绕 LLC 拓扑推进；GB/eMMC/缓存维护集成未验收。见[应用测试](../maintenance/E01/reports/reference_rebuild_check.md#dma-cross-memory-20261021) |
| 2026-10-21 | E01 本地 Agent 复查 LLC/SPM 旧失败组 | 正式路径 #80/#204 simv `e16fc6a7…`，14 个原 ELF 哈希匹配 | 7 通过、7 停滞，全部与回移前判定一致；读挡写、写挡读和 Bloom 行锁循环均仍在。前后 339 源码输入、根 diff、ELF/simv 保持；只增加运行输出和现有文档记录，未改 RTL/HAL/配置或扩展参数扫描。用户决定暂不继续处理 same_dst；完整组合与三变量结论见[复查报告](../maintenance/E01/reports/reference_rebuild_check.md#dma-llc-recheck-after-pr80-204)。未自动实施下一修复 |
| 2026-10-21 | E01 iDMA #80＋#204 局部回移 | 服务器 Cheshire `e040b7bbc` / iDMA `c12caf59`，本地 `c9abbb489` | 已在服务器回移通道控制和对应生成文件；原配置、LLC/HAL/其他依赖、本地 FPGA 保持。旧版 #115 与仅 #80 的反压错误得到对照；后端原平台 29/30，唯一失败确认为旧 TB 完全包含重叠漏判，测试副本修正后通过；6 项 SoC 回归及生产路径重建/HelloWorld 通过。#227/#273 仍开放，未移植；旧 LLC 失败组合本轮未复跑，通用无死锁未证明。见[本次报告](../maintenance/E01/reports/reference_rebuild_check.md#dma-pr80-204-20261021)；未开始提取或自动实施下一候选 |
| 2026-10-20 | E01 本地 Agent 修正服务器读数据断言 | 本地 `c9abbb489…`；服务器 `e040b7bbc…` / CVA6 `99eac9a6…` | 仅改 WT 两份仿真断言源码；54 项定向检查及 3 项 SoC 回归通过，CPU trace 与原运行一致；DMA/LLC 死锁仍未解决，见[断言修复结果](../maintenance/E01/reports/reference_rebuild_check.md#read-assertion-fix-20261020) |
| 2026-10-20 | E01 本地 Agent 实施 AW 按次配置及测试 | 本地 `c9abbb489…`；服务器 `e040b7bbc…` | 官方 HAL 接口局部回移；9 项目标成功，非对齐/不同步长写挡读死锁仍在；交付结构/过程图与原生 PPTX，整体定向验收未通过，见[DMA 长度与布局测试](../maintenance/E01/reports/reference_rebuild_check.md#dma-aw-config-20261020) |
| 2026-10-20 | E01 本地 Agent 实施 DMA 局部修复 | 本地 `c9abbb489…`；服务器 `e040b7bbc…` 与原锁定依赖 | 回移官方 wrapper 修复并改 HAL 四类指针；原失败项、字段访问和基本回归通过，默认长二维搬运失败，原 RTL 同样复现。测试副本 AW 解耦后数据通过但有断言警告，完整验收未通过；见[说明](../engineering/DMA_Control_Path_and_Fix.md)及[控制接口修复结果](../maintenance/E01/reports/reference_rebuild_check.md#dma-fix-20261020) |
| 2026-10-20 | E01 本地 Agent 执行服务器疑点测试 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；服务器 Cheshire `e040b7bbc…`，保留已有差异 | 已构建、运行 DMA/向量指定用例，并从空目录重建同配置调试版定位。向量修正副本 22 字节通过；DMA 数据比较通过但控制 ID/64 位字段访问失败；发现目标失败而主机退出 0。原件未修，stub 未运行，提取未开始，详见[控制接口测试](../maintenance/E01/reports/reference_rebuild_check.md#dma-vector-tests-20261020) |
| 2026-10-20 | E01 stub 停用与下一任务准备 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；保留既有未提交内容 | 按用户要求将 stub 用例标为勿用，撤下其适配复用建议；记录 DMA 配套访问假设和下一轮服务器验证范围。仅更新现有方案、状态、任务表及本交接，未 SSH、修改工程或运行 |
| 2026-10-20 | E01 本地实施第 1 步：测试梳理 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；读取 Cheshire `e040b7bbc…` / Ara `2895ba907…` 的 Git 原版；保护已有修改 | 用户改为本地 Agent 执行；完成 25 个集成测试的适用性、判据及覆盖差距，详见[既有方案第 6.1 节](../maintenance/E01/planning/server_reference_extraction_plan.md#existing-test-inventory)。仅更新五份现有 Markdown；未操作服务器、构建、仿真、修改 RTL/sw 或提取 |
| 2026-10-20 | E01 准确表达约定 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；保留已有文档修改和未跟踪图稿 | 按用户要求在[根约定](../../AGENTS.md#最小实现与分步说明2026-10-19-用户确认)补充具体动作、测试用词区分及简洁说明要求，常规检查不扩成独立审计任务；仅改 AGENTS.md 与本行，保存后重读并检查差异；未新增文档、修改工程或操作服务器 |
| 2026-10-20 | E01 协作约定落盘 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；本交接、指南已有修改，另有未跟踪测试平台图稿 | 同步用户于 2026-10-19 确认的 SoC 本地统筹/服务器实施与独立子系统边界；仅修改五份现有 Markdown，未授权调整验收顺序或执行工程任务，检查与保护记录见下节 |
| 2026-10-19 | E01 仿真测试平台图稿 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；指南及本交接已有未提交修改 | 交付工业/教学两版单页原生 PPTX、SVG、PNG及共用源码说明；仅静态源码与图稿检查，未构建、仿真或连接服务器；详见文末 |
| 2026-10-19 | E01 波形与验证效率说明 | 本地 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`，输入工作区干净 | 按用户确认方案扩充指南第7章：场景取舍、三类开销、全程指定层次默认示例、层次/数组/窗口及分步Debug；仅修改指南与本交接，未操作服务器或运行仿真 |
| 2026-10-19 | E01 UCLI波形调用修复 | 本地 `2f0f2d6f…`；服务器现有调试simv `d0836136…` | 修复服务器wave.tcl，改用官方原生dump；独立20μs短测和FSDB读取通过，未运行完整fmatmul或GUI。同步指南及本交接，失败日志保留，详见下节 |
| 2026-10-19 | E01 波形设置最小化 | 本地 `2f0f2d6f…`＋已有未提交文档；沿用本次服务器链接核查 | 指南第7章保留官方O2/KDB，使用`-debug_access+all`；撤下默认手动PLI链接，启动采集Tcl缩为7条命令，延后窗口按需说明。仅修改指南与本交接，未修改脚本或运行EDA |
| 2026-10-19 | E01 最新仿真检查与历史清理 | 本地 `2f0f2d6f…`＋已有未提交文档；服务器 Cheshire `e040b7bbc…` | 用户确认仿真结束后只读核对官方入口 fmatmul 成功，再按授权删除6个历史目录；394个保留文件清理前后哈希一致。主机退出状态未取得，未重跑；详见下节 |
| 2026-10-19 | E01 最小实现约定固化 | 本地 `2f0f2d6f…`＋已有未提交文档 | 按用户要求在根[AGENTS.md](../../AGENTS.md#最小实现与分步说明2026-10-19-用户确认)新增新对话约定：复用现有入口、逐项证明新增必要性、按当前步骤引入配置，避免用包装或搬移逻辑制造复杂度；只改入口说明与本交接，未操作工程或服务器 |
| 2026-10-19 | E01 按需配置再精简 | 本地 `2f0f2d6f…`＋已有未提交文档 | 第0节收敛为四项用户配置、失败停止及两个官方入口；波形移至第7章，不设开关或自动证据生成逻辑。仅修改指南与本交接，未执行服务器操作 |
| 2026-10-19 | E01 官方入口精简 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档；服务器依据沿用2026-10-18核查 | 按用户确认方案撤下指南中的config/build/run/view包装层，改为官方start顶部配置及三处最小修改，仅新增wave.tcl的保存说明；本轮只修改指南与本交接，未部署或运行EDA |
| 2026-10-19 | E01 文件配置式仿真指南 | 本地`2f0f2d6f…`及已有未提交文档 | 指南第0节提供config.sh/wave.tcl及build/run/view三个脚本的完整保存内容；替换第5/7节重复长命令入口。只改指南与本交接，未在服务器部署或运行 |
| 2026-10-19 | E01 参数开放策略文档同步 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档 | 按用户确认同步 02 规格、资源指南、服务器方案及本交接；固定功能组合、按构建锁定配置，基线对照后逐步开放参数。只改文档，未修改参数或执行提取/试验；检查记录见文末 |
| 2026-10-19 | E01 配置理解与文档整理 | 本地`2f0f2d6f…`；沿用2026-10-18服务器核查证据 | 扩展上手指南第4章与配置手册README/RECIPES，按来源、覆盖、消费者、影响和重做范围梳理pkg/TB/脚本；只改4份文档，未实施脚本封装或修改工程 |
| 2026-10-19 | E01 资源问答整理；独立只读复核 | 本地 `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋已有未提交文档；服务器版本沿用既有核查 | 新增固定向量资源专题并接入工程索引；只改正文、索引和本交接。静态复核 SRAM、寄存器/CSR、ROM 与配置约束；文档检查结果见下，未改硬件或远端工程 |
| 2026-10-18 | E01 上手指南撰写 | 本地 `2f0f2d6f…`；服务器 Cheshire `e040b7bbc…` / Ara `2895ba907…` | 按用户确认计划新增八章服务器使用指南并接入软件索引；只读核对源码、脚本和工具手册；教学构建/故障注入/波形与GUI均未实测；未改RTL或服务器 |
| 2026-10-18 | E01 主协调；硬件/VCS 与 S01/V01 只读复核 | `mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，已有 7 个文档修改、2 个未跟踪文档 | 完成只读调查、分步方案；未复制工程、编译或仿真；等待第 1 步确认 |
| 2026-10-18 | E01 / S01 第 1 步实施 | 同一 HEAD；用户明确“开始第1步” | 最小工具链检查完成；SPM标量/RVV与本机DPI源编译通过，发现libgcc特定DRAM高地址重定位失败并隔离；未执行VCS或目标程序，等待第2步确认 |
| 2026-10-18 | E01 来源方案比较 | 同一HEAD；用户明确不复制本地工程，改为官方GitHub重建并先分析 | 原第2步复制方案被替代；已核对部分历史绕过/修改与官方来源候选，未下载、构建或调整服务器 |
| 2026-10-18 | E01 同版本重建澄清 | 同一HEAD；用户明确重建当初clone的ara-pulp-v2 | 确认为原 `mp/ara-pulp-v2` 历史版本在服务器重建；本地Git定位基准e040b7bbc及原依赖锁，不再评选新版本；未执行第2步 |

## 范围与状态

<a id="p3-p5-repair-20261023"></a>

### 2026-10-23 P3–P5修复与累计回归完成

- **授权与执行：**用户要求失败后先定位并尝试修复；在原C从`p3-stopped`继续，范围内故障直接诊断/最小修复/复验，越界才暂停。仅本地Agent经WSL SSH，没有本轮子Agent或服务器Agent，不写R/F。
- **实际修改：**P3保留MVP #18并本地修正FPnew未用SIMD子单元及mask索引；P4按#191/#192分步后本地保留首拍非对齐地址，修复相邻段5字节覆盖；P5仅同步reps模板/既有派生RTL，再删HAL清零1行。接口/参数/ABI、wrapper、32位MMIO、CONF及#80/#204保持。
- **验证与版本：**P3同ELF177/6→0、补充753/28→0，RVV/fmatmul通过；P4四版本同六ELF对照，最终5195项及Hello通过；P5旧HAL同ELF18错→0，顺序3请求/9后端/138 B及三项既有DMA回归通过。`p3-pass=a7e837d…`、`p4-pass=2736992…`、`p5-pass=fe8d8cd…`，双份累计bundle及证据已校验；详细SHA、失败证据和实际调用见[稳定评估](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p3-p5-repair-20261023)。
- **累计交付与保护：**7次新运行完成：Hello/非stub CSR/向量复制/RVV5976/访存原子572/fmatmul均PASS，ROM/SPI目标0、入口2，仅原两读两写padding告警；49152 B执行store与镜像全匹配。复用同最终版本3项DMA回归。最终`p1-p5-pass=5e0f973c090ee26ba18ce520bc61beebe584e929`，服务器B/backups及本地`.e01_backups/P1_P5_20261023_154743/`的累计bundle/40成员证据包校验通过。R根/26依赖/1084输入及F962目标匹配原快照，C干净；五份文档写前核对并行状态，本地生产源码保持。阶段B完成并停止；R写回及阶段C同步仍需明确授权，恢复命令见评估。原ROM/FS/libgcc/共享LLC限制不变。


<a id="p3-stop-20261023"></a>

### 2026-10-23 历史停止记录：P3曾剩余标志失败（已由上方修复取代）

- **授权与输入：**用户“继续P3–P5”；从原隔离C的干净`p2-pass`开始。只改C，本地HEAD仍`c9abbb489…`，无服务器Agent；R/F及原有产物保持。
- **修改与结果：**测试提交`95beade…`，生产提交`fa7baaa…`仅回移MVP #18 / `2ec0514…`的一行。C现有Make构建软件、新目录构建硬件，同一ELF177项20错→6错；14项0/0标志错误消失。剩余6项均为FP32/64向量非零除零、普通除法和mask的fflags，值/保护元素通过；目标43、simv0、入口1，完整定向失败。静态汇总/valid线索尚非根因，见[完整结果](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p3-stop-20261023)。
- **版本与恢复：**`p3-stopped`=`7b1c13feb4323be10450ec1e4e47f344cba8bc63`，未创建p3-pass，已通过回退点仍p2-pass。累计bundle、17数据成员＋清单的证据归档、保护快照同存服务器`.../P1_P5_20261023_154743/backups/`与本地`.e01_backups/P1_P5_20261023_154743/`；完整trace在C原运行目录。恢复时先核对并发变化，再revert本轮生产提交，命令见评估；本次未回退或清理。
- **保护与下一步：**R根HEAD/status/diff、26依赖、1084输入及F962目标与原快照一致。按未解释失败停止，P3受影响回归、P4/P5及累计回归未继续；建议授权先定位并尝试修复6项，再恢复原顺序。未扩大到FS/#16/LLC/ROM，参考写回及阶段C仍未授权。五份现有E01文档写前匹配本轮备份，其他专题修改保留。

<a id="p2-repair-20261023"></a>

### 2026-10-23 P2失败定位与修复完成

- **授权/输入：**用户明确要求定位P2失败并尝试修复，调整审批模式后继续；沿原隔离C的`p2-stopped`实施，不写R/F，不继续P3–P5。
- **原因与修改：**16项失败来自VL外mask尾位被计数；仅回移未合并Ara PR #469内`2ce6c2c…`的6行裁剪。另15项来自共享MaskB仍忙时提前回应标量，且存储误入该分支；本地仅修正sequencer WAIT响应条件，保留VCPOP/VFIRST专用返回。官方P2的vmfpu修改保持，不升级依赖或改队列/接口/配置。
- **实际验证：**同一P2 ELF依次835/31→835/15→835/0；mask定向124/32→124/0；scalar补充旧版FIFO满断言→483/0，VMVXS/VFMVFS的占用等待各实际观察56拍。RVV5976、32×32 fmatmul、向量复制、非stub CSR、P1真实B门控/数据全部通过，目标/simv/入口均0。ROM/FS/libgcc/LLC限制保留；未称完整ISA/ASIC验收。
- **版本与恢复：**`p2-mask-pass`=`4b681ea…`，`p2-pass`=`7ac2e12b4bdfcf65d91ef5962439e4b0f13bdd6c`；服务器目录外及本地`.e01_backups/P1_P5_20261023_154743/`都有累计bundle与50成员证据归档，哈希/完整历史通过。旧失败源码、日志、标签保留，具体SHA/命令/逆序revert见[稳定评估文档](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p2-repair-20261023)。
- **保护与停止：**R HEAD/status/diff、26依赖、1084原输入及F 962目标全部匹配原快照；本地源码未改。五份现有文档写前核对并行状态，保留A/B记录。本轮在P2完成后停止；P3–P5及全组累计回归待后续安排，参考写回/阶段C正式同步均未实施、仍须明确授权。

<a id="p1-p5-stage-b-stop-20261023"></a>

### 2026-10-23 P1–P5阶段B历史记录：在P2验证失败处停止

本节为此前停止快照，后续已按新授权完成[P2定位修复](#p2-repair-20261023)。

- **授权与范围：**用户明确要求实施P1–P5局部修复计划；只在`~/CheshireAra_maintenance/P1_P5_20261023_154743/candidate`中操作，R参考原件/F正式工程不写回。不升级依赖、不调用Bender，不引入FS/性能/LLC额外修复；所有测试串行、无波形。
- **结果：**基准HelloWorld/向量/RVV通过；P1旧版B=4完成=0，修复版B=4完成=4、数据及两项回归通过。P2旧版真实返回错绑复现，官方修复后同ELF错绑观察为0，但835项仍31失败、目标42/入口1，首条为`vcpop=15`而预期1。不能将全部失败归为popcount或认定补丁通过；P2相关回归、P3–P5及累计回归未执行。
- **版本及证据：**`baseline`、`baseline-ready`、`p1-pass`、`p2-stopped`逐项提交/标签；目录外服务器备份及本地`.e01_backups/P1_P5_20261023_154743/`双份bundle与关键ELF/日志。首次bundle实际恢复，1084输入哈希匹配。官方完整SHA、提交、运行目录、哈希和恢复命令集中在[阶段B记录](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#p1-p5-stage-b-stop-20261023)。失败代码未回退，仍可查看；没有`p2-pass`。
- **保护与文档：**结束时R HEAD/status/diff、26依赖及1084输入、F 962活动目标均与进入时一致。当前P1/P2只在C；本地RTL/sw/FPGA未改。记录更新沿用五份现有文档，写前保存当时内容并保留并行A/B基线调查与用户选A决定；未覆盖其历史结论。
- **下一步：**按用户“新错误/未解释结果即停止”的条件，本轮已停止，不继续P3–P5。是否定位P2剩余失败、是否单独同步P1均待明确选择；阶段C仍需单独授权及正式复验。既有ROM限定告警、FS/libgcc、共享LLC失败保留。

<a id="main-baseline-decision-20261023"></a>

### 2026-10-23 最新：A/B开发基线评估完成

- **后续用户决定（同日）：**已接受方案A，在现有分支上选择性采用官方后续补丁；取代本节此前“建议尚未采纳”的状态。用户说明另一Agent已梳理PR并有Markdown记录，本轮解释必要性判据，不并行重复移植。具体候选的适用性、前置修改和验证结果仍以负责Agent实际记录为准。
- **范围与输入：**用户授权比较继续维护与main重新集成Ara，并允许必要小规模隔离验证。本地HEAD `c9abbb48946fe3a7244bfb3159919b7c9731cb59`，进入时记录521个已有修改/未跟踪文件；本地子Agent只读调查和独立复核，主Agent统一写文档，无服务器Agent。另观察到既有`.e01_backups/P1_P5_20261023_154743/`中的bundle和三个新备份由外部工作变化，本轮没有触碰，不能声称所有其他文件期间完全不变。
- **结论与证据：**正文统一在[既有评估的本轮结论](../maintenance/E01/planning/official_upstream_maintenance_assessment.md#main-baseline-decision-20261023)。建议现在A，以F实际已修组合为日常基准；main依赖仍是pulp-v2 `4c02b24…`，加旧Ara有源码依据，但没有候选动态验证。原issue #206、main真实修复收益、未覆盖项、VCU118官方已覆盖部分、OS异常和软件配套均分别记录；不把建议当用户决定。
- **实际执行：**本地26依赖HEAD/diff与现存生成清单核对；GitHub固定SHA/PR及源码比较；SSH只读R HEAD/status、F来源/配置哈希、Rocky8.10和VCS W-2024.09-SP1；结束前因外部备份活动重核F的962条目标哈希，0不匹配，R/F的VSTU/VMFPU仍与旧版一致。`/tmp`独立bare库获取官方对象并运行`merge-tree --write-tree`，官方向量分支与main为11冲突文件，L与main为14。日志、锁、依赖差异和静态接口比较见[原始证据目录](../maintenance/E01/reports/evidence/main_baseline_20261023/)。这不是编译/elaboration或目标仿真。
- **修改与保护：**仅更新本评估、本交接、PROJECT_STATE和AGENT_TASKS，并增加本轮原始证据；此前评估正文保留，写前备份在`/tmp/cheshire_main_assessment_20261023/before/`。未修改L/R/F源码、依赖、现有入口、产物或服务器文件，未运行Bender/构建/仿真/板测，未解决临时合并冲突。既有FS/DMA/断言修正、LLC限制、ROM限定告警和libgcc限制保持。
- **文档检查：**三项本地独立审阅后修正了完整CVA6配置派生、scan绑0、FS Clean保留、#203覆盖指代、#2989门控来源及工具成本边界。`python3 /tmp/cheshire_main_assessment_20261023/validate_docs.py`、`git diff --check`通过；231个本地链接检查无新增错误，2处原有历史锚点问题未改；表格/代码围栏正常、此前评估正文完整保留。除4份授权文档及已记录的外部备份变化，516个已有路径哈希不变；详见证据目录`validation.json`。
- **最小下一步：**沿现有局部维护候选选择具体修复及定向验证；main迁移仅在正文条件出现后重评。此次评估任务完成，不自动执行原阶段B/C或新迁移；生产状态不变。

<a id="upstream-maintenance-stage-a-20261023"></a>

### 2026-10-23 最新：官方后续维护调查与规划完成

- **同日用户补充：**明确“仅进行局部代码修复”，不整包升级；已写入维护评估的范围说明。尚未选择候选或授权阶段B，源码与测试保持停止状态。
- **授权与输入：**仅阶段A调查、只读核查及本地文档；本地HEAD `c9abbb48946fe3a7244bfb3159919b7c9731cb59`。进入时四份共享/主题文档已有未提交修改，本轮写入前哈希确认未并行改变；未覆盖其他图稿、源码及未跟踪产物。三个子Agent均在本地调查/评审，没有委派服务器Agent。
- **实际核查：**通过WSL SSH（后续沿Windows SSH通道）读取R=`~/CheshireAraPULP`、F=`~/CheshireAra`的README、锁/来源记录、配置、静态入口和候选调用路径。使用`git --no-optional-locks ... rev-parse/status/diff`、按现有manifest计算文件SHA256，26依赖实际HEAD/diff匹配reference记录，962条F目标哈希匹配活动manifest；所选候选实文件R/F一致。F配置已合入cheshire_pkg、Bash compile/start/check_result已实施；R当前start默认PRELMODE0，F为1，不能混用。另只读readelf确认17个现有ELF未覆盖SLINK所需布局；未执行目标代码。
- **结论与规划：**新增稳定[官方后续维护评估](../maintenance/E01/planning/official_upstream_maintenance_assessment.md)，由现有提取计划/任务表/共享状态链接。优先候选Ara #481/#482、MVP #18及iDMA #66中1D-in-ND reps修复；逐项列官方完整SHA、适用性、保留本地修正、最小文件范围、输入缺口、验证和停止点。Cheshire/CVA6主线分叉，不整包升级；MVP #16新增NX风险、FS #2936残留F2I/SD问题、SLINK #191非对齐截断推导、shared TLB关闭等在独立复核后修正分级。iDMA #227/#273未合并，LLC扩展排查仍暂停。
- **保护与验证边界：**本轮只新增上述一份本地规划Markdown，并更新本交接、既有提取计划、PROJECT_STATE、AGENT_TASKS；未修改服务器文件/源码/依赖、未构建/仿真/生成RTL、未恢复或清理产物。原FS Clean、DMA/HAL、#80/#204、WT断言、ROM padding限定告警、LLC旧失败、libgcc限制保持。临时核查/输入备份在本地`/tmp/e01_maintenance_stage_a/`，完整事实汇入专题；不新增脚本/维护框架。
- **下一步与停止点：**用户选择候选并授权B后，仅从参考实际源码制作必要范围的隔离候选并串行验证；建议不写回R原件，是否写回由该次授权明确。B报告后停，另等C授权逐文件同步F并新输出复验。**阶段A交付后已停止；本文不是实施授权。**

<a id="config-entry-merge-defaults-20261022"></a>

### 2026-10-22 最新：配置入口合并完成

- 用户明确授权取消 `cheshire_ara_asic_cfg_pkg.sv`。正式工程改由 `cheshire_pkg` 提供 Cfg、CPU派生配置和接口类型；只把 `DefaultCfg.Ara` 默认0改为1，原有效Ara已经是1。wrapper/fixture移除旧import，静态清单删除该文件，编译顺序/宏保持。现有来源清单、差异补丁和服务器配置文档同步，未改启动脚本、Make或软件。
- 默认值的唯一变更、定义迁移、实际文件及恢复关联项，集中见[配置入口合并与默认值变更](../maintenance/E01/planning/server_reference_extraction_plan.md#config-entry-merge-defaults-20261022)。恢复上游Ara=0但继续启用Ara不能只改一行；真正关闭Ara属于另一个功能变更。
- 修改前后soc/slink_rx均在新目录编译/展开；同一ELF/镜像14次串行对照，12 PASS及2次原SPI限定告警。完整有效SoC/CPU配置、30项接口位宽、目标输出、对应CPU trace和相关告警一致。LLC旧限制保持，未重跑扩展诊断；不表示ASIC/PHY/宏验收。
- 输出 `~/CheshireAra/sim/work/cfg_merge_20261022/`；修改前服务器备份 `/tmp/e01-cfg-20261022-5difdhgr/`，本地快照 `/tmp/e01-cfg-20261022-joge44so/`。1013份未涉及非输出文件、原soc关键产物和软件输入哈希保持。本地仅改四份既有Markdown，写入前检查无并行变化；未委派服务器Agent。
- **本轮完成后停止。** 以下“独立配置包”的提取/验收描述保留为历史事实，由本条更新当前组织方式；不据历史记录重新创建旧包。


<a id="entry-scripts-result-20261022"></a>

### 2026-10-22 最新：compile/start入口简化完成

- 用户明确要求并授权实施已讨论计划：软件单独Make；Bash start直接展开/运行，Python仅作内部结果解析；允许复用输出、WARNING后覆盖，脚本增加必要注释和空行。本条替代此前“保留run.py”“每次新目录”的决定。
- 服务器修改compile/Make、增加start、run.py迁为check_result并移除旧启动入口，同步根README、两份docs和现有来源清单。默认根目录命令为`make -C sw`、`./sim/scripts/compile.cheshire_soc.sh`、`./sim/scripts/start.cheshire_soc.sh`；普通600秒、串行、不导出波形。RTL、配置、软件源、参考工程和历史归档保持。
- 四种top完成编译/展开和代表用例，10次真实仿真为7项PASS、SPI目标0/simv0/入口2、目标负例41/0/1、超时null/124/124；默认目录最终为HelloWorld PASS。SPI四条padding断言范围保持；未重跑完整回归或排查LLC。Make重复运行/依赖、库成员及输入哈希检查通过；整库哈希因归档头含时间不作稳定判据，首次检查失败有记录。
- 完整改动、命令、实际结果及保留限制见[既有计划第7.11节](../maintenance/E01/planning/server_reference_extraction_plan.md#entry-scripts-result-20261022)。服务器检查输出在`~/CheshireAra/sim/work/entry_checks_20261022/`，备份`/tmp/e01-entry-20261022-zm5iis9_/`，本地备份`/tmp/e01-entry-20261022-txxkykpx/`。原1016份未涉及文件哈希不变，963条来源哈希、12段文档命令和36链接/锚点检查通过。
- 本次由本地Agent经WSL SSH完成，未委派服务器Agent；新输出保留。**本轮完成后停止，后续按用户使用反馈处理。** 以下为此前文档/提取记录。

### 2026-10-22 此前：独立工程用户文档已交付

**使用定位补充（用户于2026-10-22确认）：**当前两份指南先供用户个人使用和记录；后续泛化给团队共享前，另行审查并修改个人账号/路径、个人工具环境和操作前提，以及依赖既往聊天、个人习惯或个人决定才能理解的说明，使团队成员无需阅读聊天也能理解并操作。泛化时区分可复用的工程事实与个人相关事项，保留真实入口、必要环境条件、验证范围和已知限制；不能将个人验收中的限定接受直接写成团队通用通过标准。本次只记录后续要求，未开始团队版改写，未SSH、修改服务器文档或工程。

- 用户审核规划后明确“开始实施”，本地Agent通过WSL SSH按约定写入服务器`~/CheshireAra/docs/README.md`（196行）、`docs/CONFIGURATION_AND_DEVELOPMENT.md`（265行），根README仅增加导航；既有`provenance/source_manifest.json`更新根README哈希并追加两份正文的记录，960→962条。写入前检查目标/并行变化，未覆盖未知文件；未委派服务器Agent。
- 上手文档沿compile→Make all→run.py新ELF→结果检查，并把原ROM/SPI放为可选步骤；配置指南区分硬件、编译、运行、软件选项，说明五类改动的必要重建和适用测试。当前固定组合检查、lane自动读取而地址/容量手工对应、三层状态、SPI两读两写限定接受和三项LLC失败均写明；波形无独立全流程依据，不增加新入口。
- 从服务器最终交付文件重新读取并检查11段Bash语法、36个相对链接/锚点、命令路径/17个ELF目标、配置消费者和结果判据；962条当前来源哈希匹配。实际只新增/修改约定四文件，其他1019份既有文件哈希保持，旧输出仍不存在；未改脚本/RTL/软件/配置、参考工程、工具或归档，未恢复搬迁副本。
- 完整路径、检查范围和静态检查首次误用默认Python后改用既有3.9的记录见[计划第7.10节](../maintenance/E01/planning/server_reference_extraction_plan.md#user-documentation-result-20261022)，临时草稿与检查结果在本地`/tmp/e01-user-docs-20261022-h4f9ofkf/`。仅更新既有计划/本交接，未新增规划报告或服务器管理机制。**本轮未构建或仿真，历史验证不冒充新运行。** 交付入口后停止，用户使用前不主动优化流程。

### 2026-10-22 最新：独立工程用户文档规划完成，等待撰写授权

- 用户本轮只授权规划及只读核查。主Agent通过WSL SSH读取正式工程实际入口、集中配置/共同wrapper、必要启动/链接规则和已有来源/验收摘要；原生SSH不稳定时沿既有Windows SSH读取。本地子Agent只读复核范围/判据，未委派服务器Agent；未创建服务器`docs/`、写服务器文件、构建、运行仿真或解包归档。
- 确认正式根下只有源码、入口、许可与来源资料，`docs/`及已清理输出仍不存在。当前无服务器`.git`，来源版本按现有记录说明，不假设可用git管理。硬件唯一有序清单仍在compile脚本，run.py保留；Make拒绝已有输出且只接受lanes2，fixture检查固定向量组合；地址/容量需人工核对软件链接/头文件，只有lane自动读取。
- 建议`docs/README.md`承载最短上手、目录/工具及结果/限制，`docs/CONFIGURATION_AND_DEVELOPMENT.md`承载分层配置、五类修改、相关现有测试及按需调试。阶段B仅这两份正文、根README必要导航及`provenance/source_manifest.json`已有记录的相应更新；准确路径、章节依据、文档差异及静态验证见[计划第7.9节](../maintenance/E01/planning/server_reference_extraction_plan.md#user-documentation-plan-20261022)。不改流程/脚本/RTL/软件/配置，不写其他工程或归档。
- 普通使用先从新输出构建硬件、软件/镜像，再运行新ELF；重复运行只换运行目录，必要重建各自换新目录。run.py三层状态及0/1/2/3/4/124、SPI原padding两读两写限定豁免、三项LLC失败和stub勿用均保留。波形缺独立工程全流程实测依据，不复制参考工程start/wave流程或新增入口；现有日志/trace/map/dump/probe作为按需调试内容。
- 本轮只更新已有计划和本交接，不新增规划报告；既有修改/未跟踪文件保持。未发现阶段B必须实跑项，拟按实际源码、命令语法/路径/链接、配置消费者、结果判据和现有来源规则静态检查；历史2B–2D不是本次新运行。**阶段A完成后停止，等待用户明确同意撰写；阶段B交付后不主动优化工作流程。**

### 2026-10-22 最新：验证产物已归档清理

- 用户在清理范围说明后明确授权实施。正式工作区只保留`~/CheshireAra`；旧`sim/work/`、`sw/build/`、`sim/reference_inputs/`及搬迁副本已移除。完整日志、失败记录、CPU trace、strace、输入和来源资料压缩在`~/CheshireAra_validation_archive_20261022/validation.tar.gz`，2033份文件逐项校验通过；历史路径按归档内原目录名前缀定位。
- 正式工程1018份保留文件哈希不变；仅README及活动清单更新清理状态，源码、配置和compile/run.py/Make不改。净释放约3.44 GiB。参考工程、其他工程及本地已有修改未清理；未重新构建或仿真，后续使用按README重建。
- 详细范围、哈希和查阅方法见[计划第7.8节](../maintenance/E01/planning/server_reference_extraction_plan.md#post-validation-cleanup-20261022)。本地四份文档写入前与`/tmp/e01-cleanup-20261022/`备份一致。以下2D记录保留验收时状态，由本条更新其产物当前位置。

<a id="step2d-progress-20261022"></a>
<a id="step2d-result-20261022"></a>

### 2026-10-22 最新：步骤2D完成，独立提取及搬迁验证结束

- 工程位置仍为 `~/CheshireAra`；新位置 `~/CheshireAra_relocated_2d_20261022` 用987份明确文件验证搬迁，不带18份历史参考二进制或旧构建输出。四种硬件及23单元库、17ELF和SPI镜像均从新输出重建，三个活动入口无需修改；两处README已给出编译/运行方法，保留`run.py`，不新增start包装。
- 31项串行结果为25项正常PASS、SPI限定告警功能接受（入口2）、2项故意负例（1/124）、3项LLC已知失败（INCOMPLETE/4）。36份CPU trace逐字一致，SPI实际搬运49152字节正确，RX及后端计数/完成与基准一致；不写成全部测试通过。详细结果及证据路径见[方案第7.7节](../maintenance/E01/planning/server_reference_extraction_plan.md#step2d-result-20261022)，两处工程均有 `provenance/2d_summary.json`，原始构建、运行和比较记录留在搬迁目录。
- 软件、四种硬件、31次运行及单独入口拒绝的37份trace共4,075,541条事件：未读原工程、参考/.bender/TTY或旧编译缓存，无Bender/下载依赖工具执行。工具侧网络、用户路径及临时文件访问如实记录；不是全文件系统隔离承诺。最终检查原源码/参考版本差异、99份旧输出及全部新输入绑定保持，源码树只更新README及对应清单哈希。
- **用户纠正保持：**服务器可正常联网，VCS使用现有许可证及必要通信无需确认；限制是工程构建不依赖在线下载源码、解析或更新依赖、不擅自升级依赖。主Agent此前扩大为全面禁网而暂停EDA不当，已撤销该无依据条件并完成既有授权任务。
- 本地仅更新本交接、既有计划、PROJECT_STATE和AGENT_TASKS，写入前与续做快照一致，无并行变化；开工备份 `/tmp/e01-step2d-20261022-xx_ilia1/before/`。本地子Agent只读核查/独立评审，主Agent统一写入和串行测试，未委派服务器Agent。本地FPGA/RTL/sw、服务器参考工程及旧产物保持。
- **2D完成并停止。** ROM限定告警、DMA共享LLC失败、FS Dirty原因和libgcc高地址限制继续保留。后续参数开放、入口体验优化、新IP或工艺适配另行授权；本次不等于ASIC综合或流片验收。

<a id="step2c-result-20261022"></a>

### 2026-10-22 前次：步骤2C完成，当时等待2D

- **同日后续用户决定：**先保留 `sim/scripts/run.py`，后续根据用户实际使用习惯和反馈再改进优化；2D沿用现有入口，不预设改名或新增重复包装。已同步[方案第7.4节](../maintenance/E01/planning/server_reference_extraction_plan.md)，本次仅更新文档，未修改脚本或启动2D。

- 用户已授权“开始2C”，次日要求继续；本地经WSL SSH实施，本地子Agent按不重叠软件目录迁入并独立评审，主Agent统一Make、链接/来源记录、串行运行及共享文档。次日WSL原生SSH超时后沿既有Windows SSH通道续跑，先确认无遗留仿真，保留前五项已完成结果。
- 服务器 `~/CheshireAra/sw/` 已包含启动、链接、HAL/头及必要依赖和所选测试；新入口 `sw/Makefile` 从新 `sw/build/2c_02/` 重建23单元库、17ELF、map/dump和SPI raw/memh。未链接旧库/调用参考脚本，没有生成ROM或重编RTL。首次LTO插件路径失败输出 `2c_01` 保留；修正插件定位后构建成功。
- 17个ELF的可加载内容、布局及指令与参考一致；FS/VS顺序和DMA HAL保持，旧LLC测试仅补默认CONF实参且机器码未变。19次新软件对照为13项PASS、1项SPI限定告警功能接受（入口2）、2项故意负例（1/124）、3项LLC已知失败（INCOMPLETE/4）。详细比较、保护范围和命令见[方案第7.6节](../maintenance/E01/planning/server_reference_extraction_plan.md#step2c-result-20261022)，服务器摘要 `sim/work/2c_summary.json`；原2B及参考证据不改。
- 本地仅更新本交接、既有方案、PROJECT_STATE和AGENT_TASKS，写入前与续做备份比较无并行变化；备份在 `/tmp/e01-step2c-resume-20261022-3ucfa9fk/before/`。未改本地FPGA/RTL/sw、参考源码、TTY工程或外部工具；不自动修LLC、开放参数或新增IP。
- **2C完成后停止，等待用户明确授权2D。** 新软件在本工程内构建和运行已验证；搬迁后全新重建与实际文件访问检查仍未做，不宣称全部独立性或工艺验收完成。

<a id="step2b-result-20261021"></a>

### 2026-10-21 前次：步骤2B完成，当时等待2C

- 用户明确授权“开始实施2B”。本地WSL SSH实施，三个本地子任务按不重叠范围核查/补入来源资料；共享配置、清单、wrapper和文档由主Agent统一写入，未委派服务器Agent。未改本地FPGA/RTL/sw、服务器参考工程、TTY工程或外部工具。
- 目标为服务器 `~/CheshireAra`。实际提取、配置/端口、四种新构建及全部测试见[方案第7.5节](../maintenance/E01/planning/server_reference_extraction_plan.md#step2b-result-20261021)；入口说明在目标`README.md`和`src/config/README.md`。SoC新simv为`d4650902…`；使用同批参考ELF/镜像，未重建软件或ROM。
- 31次运行：25项正常PASS；SPI仅原四个padding事件，功能接受、入口2；故意目标失败/超时分别1/124；3项LLC旧失败均INCOMPLETE/4。fmatmul同ELF与历史摘要一致，旧完整trace已被后续运行覆盖，不宣称该项trace逐字相同。原失败日志和新后端首次KDB缺top的输出均保留，未以新目录覆盖旧输出。
- 服务器`provenance/2b_*`及`sim/work/`保存实际源/配置/ELF/simv/命令/退出状态和独立比较；339项生产输入、26项最终输入、15项参考产物及根/26组件版本与diff不变。本地四份目的文档写入前与开工备份一致，备份在`/tmp/e01-step2b-20261021-i8bw_594/before/`；只增改本方案、交接、PROJECT_STATE及AGENT_TASKS，保留已有修改/未跟踪文件。
- **2B完成后停止，等待用户明确授权2C。** 下一阶段在新工程重建启动/库/HAL/测试和SPI载荷，不能链接旧库宣布独立；2D搬迁与实际文件访问验证另行实施。未修复LLC、开放参数、加入新IP或进行工艺验收。

<a id="step2a-plan-20261021"></a>

### 2026-10-21 前次：步骤2A规划完成，当时等待2B

- 用户已明确参考基准可用于提取对照，保留 ROM padding 限定豁免及 DMA 共享 LLC 失败/暂缓修复决定；此前“严格无缺陷才可进入下一步”的历史表述不作为本次门槛。计划只涉及脱离 Bender 的独立工程，不含参数调整、功能裁切或新IP。
- 主Agent通过WSL SSH核对服务器实际文件；补充授权后，本地子Agent分别检查RTL/配置、软件/启动、仿真/验收，仅读取并提交结论，没有并行写共享文件或启动服务器Agent。该协作纠正已写入[根约定](../../AGENTS.md#local-server-collaboration)，不扩大本轮执行权限。
- `~/CheshireAra`仍存在且为空。生产分组清单66组/716唯一源/18include均存在，编译日志解析顺序一致；26依赖HEAD与锁一致，339保护输入、26最终输入、15产物及iDMA36部署文件哈希均匹配。FS、DMA wrapper/HAL、CVA6断言、iDMA回移及其他既有生成差异保留；来源不是本地版本或仅固定提交。实际清单足够，本计划不要求再运行Bender。
- [计划第5/7节](../maintenance/E01/planning/server_reference_extraction_plan.md#step2-plan)明确最小目录、唯一集中配置/共同wrapper、复用静态分组入口及测试来源：2B先同ELF/镜像比较硬件，2C从源重编23单元库和软件/raw，2D在另一新位置重新构建并检查实际旧路径/缓存依赖。每阶段报告后停止。原ROM不重生成、原SPI返回2不改写，已知DMA失败不计作成功；无新增架构决定待定。
- 本轮修改仅根AGENTS、既有计划、本交接、PROJECT_STATE及AGENT_TASKS；输入备份在`/tmp/e01-step2a-20261021-omnnfdfm/before/`，写入前五文件均与进入时一致。已有修改/未跟踪文件保持。仅检查文档及现有服务器记录，未复制工程、运行Bender、构建/仿真或修改服务器。
- 交付检查：本地只读复审了配置/清单和测试/独立性计划，澄清旧TB配置包不进入新活动配置、补全来源路径；新增链接/显式锚点、围栏及范围内`git diff --check`通过。fmatmul现存ELF哈希与2026-10-19记录一致。以上是文档与现有产物检查，不是新工程编译或仿真结果。
- **最小下一步：用户明确授权2B。** 目前停止于计划交付，不自动创建工程或开始剥离；后续阶段内常规细节自主处理，仿真串行。

### 2026-10-21 最新：四类剩余验收检查结束

**同日后续用户决定：**上述 ROM padding 字节不参与有效配置，本次启动和搬运结果正确，作为已知告警忽略并接受 ROM/SPI 功能验收；不再列为待修或验收阻塞。仅限这处已定位事件，不关闭其他断言；未改 ROM 或运行入口，历史失败日志与退出码保持。以下执行记录保留当时结果。

- 用户授权本地 Agent 经 WSL SSH 直接测试，不委派服务器 Agent 或自动子 Agent；仅向服务器新目录 `_e01/remaining_acceptance_20261021/` 写测试副本和产物。沿用原 CPU/Ara/SelectedCfg/UseDramSys 与 FS、DMA、iDMA、CVA6 断言修正；复用生产路径 simv，没有重编 RTL。
- [报告第 12 节](../maintenance/E01/reports/reference_rebuild_check.md#remaining-acceptance-20261021)保存参数、金值、实际 VL、异常 PC、退出状态、命令和产物绑定。ROM 的 847 B 官方 HelloWorld 镜像填充至 48 KiB，从 flash offset 0 自主搬入 SPM并执行；功能完成，但结构体两个 padding 字节含 X，引发两条读／两条写断言，未消除。不能写成无断言通过。
- 官方非 stub CSR 三次预期 Illegal Instruction/mcause=2；SEW32/64、m1 六种长度及小型精确浮点、保护区共 5976 项零错误；SPM/DDR 私有区的基础访存、AMO、LR/SC 共 572 项零错误。新增一个测试专用 `run.py` 解决原 TB 失败仍主机0的问题：正常0、目标失败1、断言2、超时124，均有实际运行记录。没有恢复 stub 测试。
- 服务器 `summary.json`、`final_inputs.json`、各运行 `result.json` 与日志保留全部依据；339 项输入、根 diff、simv 前后不变。四份本地目的文档写入前与初始备份哈希相同，未发现并行修改；备份 `/tmp/e01-remaining-20261021-i9giwe1c/`。本地只更新本交接、既有报告、PROJECT_STATE 和 AGENT_TASKS，保留原有未提交内容。
- 本轮任务完成并停止；ROM 告警按上述同日用户决定豁免，此前 DMA 共享 LLC 限制仍保留。用户暂缓 DMA 扩展修复的决定保持，不自动修 ROM/LLC、开始 Bender 剥离、改变参数、集成新 IP 或测试 DDR→Serial Link TX。真实 GB/eMMC、DDR PHY、独立提取与产品验收均未完成。

### 2026-10-21 最新：保留一次提交完整二维任务

- 用户否定 CPU 逐块配置／等待作为正常方案，要求重新分析；暂不改 RTL 的边界保持。本轮本地 Agent 与两个只读本地子任务复核现有短突发字段和 LLC 容量，不委派服务器实施。
- 输入本地 `c9abbb489…`；前次摘要的 27 份源码哈希仍一致。已保存的服务器 HAL 补丁可直接接收 CONF，不需新 API。未重新 SSH，服务器今日状态未核实。
- [专题 §5.3–5.4](../engineering/DMA_Control_Path_and_Fix.md#dma-bulk-short-burst)形成 `n×2^k<=8` 的条件性容量证明；n=8/4/2 分别配最大8/16/32 B突发、AW0/RW0。一次提交整笔二维任务，地址／行长／步长可保留8 B粒度。n为硬件配置，当前16不满足此保守条件，不代表短突发必然失败。CPU/Ara并发LLC仍无保证，未选定候选性能最优项。
- 仅更新专题、[报告说明](../maintenance/E01/reports/reference_rebuild_check.md#dma-bulk-source-analysis-20261021)和共享索引；旧测试结果保留。备份在 `/tmp/e01-bulk-source-20261021-libev5oc/before/`。未改RTL/HAL/配置、未构建/仿真/提交/提取。
- 后续若验证，先明确软件短突发诊断与硬件参数候选的范围，检查队列容量、旧反例和CPU并发；不要自动实施参数变化，也不要恢复CPU逐块方案为正常路径。

### 2026-10-20 前次：按源码推导参数与执行条件

- 用户要求由源码提取公式，不再靠随机/穷举实验归纳。本轮本地 Agent 完成分析，两个只读本地子任务分别复核 iDMA 与 LLC；未委派服务器实施。WSL SSH 只读核对 27 份源码，输入为本地 `c9abbb489…`、服务器 `e040b7bbc…`；26 份相同，wrapper 仅已知转换器补丁不同，backend 参数保持。
- [DMA 专题第 5 节](../engineering/DMA_Control_Path_and_Fix.md#dma-source-formulas)写入逐行地址、AX/LLC 分段、请求顺序边界、精确 Bloom 判断及三种循环条件。对齐只能证明几何关系，不能替代请求先后保证。hash 位公式由固定置换/XOR 展开，用基向量核对线性系数并对应原锁采样，未运行新仿真。
- 得到条件性构造：8 B 整拍，`q=min(remaining,64-S%64,64-D%64)`，每块单独二维 N=1、AW=0/RW=0，等 DONE 再提交。LLC R FIFO 容整块并可独立解锁，排除三类循环；前提是空闲起始、无其他 LLC 请求（含 CPU 取指/栈）、有效 SPM 与正常响应。**尚未实现、正式验证或性能测试，不是现有批量 HAL 的保证。**
- [报告范围说明](../maintenance/E01/reports/reference_rebuild_check.md#dma-source-analysis-20261020)和[源码摘要](../maintenance/E01/reports/evidence/dma_aw_config_20261020/source_analysis_20261020.json)保存来源；旧测试结果未改。修改前文档在 `/tmp/e01-source-proof-kxs4fzau/before/`。未改 RTL/HAL、配置、依赖或服务器产物；未编译、仿真、commit/push 或提取。
- 当时建议先隔离流量再验证 CPU 拆块；2026-10-21 此正常使用方向被上方“一次提交整笔任务”替代，旧构造仅保留为诊断。未实施。

### 2026-10-20 前次：三变量联合测试与行锁反例

- 输入仍为本地 `c9abbb489…`、服务器 `e040b7bbc…`，复用断言修复版 simv `f96fba4c…`。用户授权验证三个变量联合放宽，未授权改 RTL；本轮仅新建测试输出及修改相关文档。
- 17 组中 14 通过、3 失败；符合候选关系的 `src/dst=0x14008068/0x14010068, L=Ss=Sd=120, N=32` 仍失败。后三次为该失败复现、全 64 B 对齐对照通过、16 行对照通过。原失败与复跑 `.text` 一致。详见[参数、结果和原因](../maintenance/E01/reports/reference_rebuild_check.md#dma-joint-alignment-check-20261020)。
- 实测源读锁键 `3c04` 查询位图 `11` 被目的写锁键 `3c10` 的占用位图 `20011` 包含，形成行锁误判循环；源码哈希和哈希计算均核对。不能继续声称 8 B＋两项模 64 相等是充分条件；也不把 64 B 对照通过说成通用证明。
- 完整服务器输出为 `$AW/joint_alignment_check_20261020/`，诊断在 `lock_checks/`；本地[必要摘要](../maintenance/E01/reports/evidence/dma_aw_config_20261020/joint_alignment_check/README.md)。两组运行前后根 Git diff 和 85 项哈希均保持。文档修改前副本在 `/tmp/e01-joint-hzs4j59w/before/`；旧失败产物保留。未改 HAL/RTL、委派 Agent、提取或提交。
- 本任务已完成测试；后续若处理行锁或放宽使用范围，另定具体任务，不自动修改 RTL或新增未经测试的软件规则。

### 2026-10-20 前次：对齐粒度对照、断言复核及专题精简

- 当前输入为本地 `c9abbb489…`、服务器 `e040b7bbc…`，复用另一位 Agent 已修断言的 simv `f96fba4c…`。用户决定暂不修改 DMA/LLC RTL；本轮仅测试副本和文档。
- 11 组对照中 6 组连续两笔通过、5 组持续写挡读。8/16/32 B 统一规则均有反例；每行 24/120 B、源目的同为 8/32 B 块内偏移也有通过组合。64 B 只作为保守统一建议，不称最小或通用安全保证；未向 HAL 加自动限制或回退。详见[对齐粒度检查](../maintenance/E01/reports/reference_rebuild_check.md#dma-alignment-check-20261020)。
- 已只读核对另一位 Agent 的两份 CVA6 补丁、simv、已有 54 项检查摘要和三项回归的日志/ELF/trace；结果匹配，移除仿真区域后功能文本保持。未将复核称为重新执行其三项回归。
- 服务器新产物在既有 `$AW/alignment_check_20261020/`；两组运行前后根 Git diff 和 85 项输入保持。生产 RTL/HAL/依赖及本地 FPGA 源码未改。没有委派 Agent、提交或提取。
- 按用户要求整体精简 [DMA 专题](../engineering/DMA_Control_Path_and_Fix.md)，保留有效锚点及详细报告入口；修改前全文在 `/tmp/e01-alignment-nooyxpcl/before/`；用户随后要求主报告也精简，原报告完整正文已保存为[只读历史存档](../maintenance/E01/reports/evidence/reference_rebuild_check_detailed_20261020.md)，两份主文档按主题压缩，原测试内容与产物保留。后续若放宽软件组合，按实际应用另定范围；不自动跨入 RTL 修复。


### 2026-10-20 最新：读数据断言修正已实施并测试

- 服务器 CVA6 `core/cache_subsystem/wt_cache_subsystem.sv` 移除整字归约 OR 检查；`wt_dcache_ctrl.sv` 使用已有请求保存字段检查返回的有效字节，并用 `$sampled` 打印。两份文件差异全部在现有仿真专用区域，功能源码文本不变；本地对应源码未改。
- 空目录重建同配置 VCS；真实读控制器 54 项检查符合预期。原 `dma_long_aw_api`、HelloWorld、修正向量复制 ELF 均程序返回 0、SLINK SUCCESS、主机退出 0，无读断言告警；各自完整 CPU trace 与修改前一致。
- 新输出：`~/CheshireAraPULP/_e01/dma_vector_check/read_assertion_20261020/`；完整日志留服务器。准确行号、前后代码、命令、哈希、负例和保护检查见[断言修复结果](../maintenance/E01/reports/reference_rebuild_check.md#read-assertion-fix-20261020)及其本地摘要附件。85 项服务器、24 项本地保护哈希保持；未提交或发布 PR。
- 本次仅关闭已定位的断言误报/漏检及打印问题，下面第 11 节所述 DMA/LLC 死锁仍开放，不自动开始结构修改或提取。以下保留前次状态。


### 2026-10-20 最新：新死锁原因与单变量对照已核实

- 输入仍为本地 `c9abbb489…`、服务器 `e040b7bbc…`，HAL 与前次四文件改动保持。WSL SSH 超时后沿用已授权 Windows 通道；没有修改生产源码、重构平台或委派子 Agent。
- 原失败基准重新编译，`.text` 与旧 ELF 一致；新增 8 组单变量对照中 7 组通过、仅 14 行组复现。13 行通过、14/16 行失败仅适用于本组固定参数，不能推广为通用阈值。详见[原反例与原因对照](../maintenance/E01/reports/reference_rebuild_check.md#dma-cause-confirmation)。
- 实测第 14 行在当前 iDMA 的 2 KiB 边界分为 42＋81 B；第二段首个写拍需要 8 B，已有 4 B，补足数据的读被后续写挡住。通过的源起点对照把所需读先放行，掩码从 0x7f 变成 0xff，写恢复。原默认死锁则是 R 返回满、读挡写；直接等待链不同，共享描述符流水线是共同条件。
- 新产物在 `$AW/cause_check_20261020/`（`$AW` 为前次 `aw_config_20261020` 输出目录）。[本地摘要](../maintenance/E01/reports/evidence/dma_aw_config_20261020/cause_check/README.md)保留测试源码、命令及关键采样，大型日志/ELF 留服务器。诊断主动退出不算目标成功；已修正结果解析对 UCLI 命令回显的匹配，原中间文件保留。
- 生产 Git diff 与输入一致，83 项保护哈希保持，六份原因分析源码与现场一致。未执行通用修复或扩大参数扫描；下一步若要消除两类循环，另定共享流水线防死锁改动和回归范围。


### 2026-10-20 前次：方案一已实施，非对齐组合仍失败

- 用户已授权实施选定方案；通过 Windows SSH 完成参考工程操作（WSL 优先尝试但连接间歇超时）。服务器只改 `sw/include/dif/dma.h` 和三个现有测试调用点，官方来源为 Paul Scheffler 的 `4c2390f2` / PR #189；保留原 32 位 MMIO 修正、RTL、依赖、FS 和其他差异。
- 新输出在 `~/CheshireAraPULP/_e01/dma_vector_check/aw_config_20261020/`。12 个 ELF 构建，10 个功能测试中 9 个目标返回 0；两个 AXI-RT 用例只编译链接。原长搬运三笔 ID=2/3/4，数据和保护区通过，单次断言与前次同一指令/时间对应，未关闭断言。
- 非对齐、不同步长组合未完成，215.048 秒后主动停止，再用同一 ELF 采样到 2 ms。写单元等待数据，后续写描述符挡住源读，读单元空闲；这是与默认“读挡写”相反的循环。具体地址、采样与分析见[DMA 长度与布局测试](../maintenance/E01/reports/reference_rebuild_check.md#dma-aw-config-20261020)。**AW 解耦不是通用死锁修复，整体定向验收未通过。**
- 交付[结构/过程 SVG、PNG 和可编辑 PPTX](../diagrams/2026-10-20_dma_llc_deadlock/README.md)，图示原默认死锁及原对齐用例的解耦位置；新失败组合在报告单独解释。PPTX 结构检查完成，Office 未实测。
- 服务器 81 项范围外保护文件哈希、四项相关依赖及范围外 Git diff 保持；本地 25 项范围外哈希保持。未改本地生产 RTL/sw，未委派子 Agent、commit/push、发布 PR 或提取。补丁、摘要在[既有报告的证据目录](../maintenance/E01/reports/evidence/dma_aw_config_20261020/README.md)，详细日志/ELF 留服务器。
- 最小下一步：根据已复现的反向循环，另行确定支持范围或 LLC/iDMA 防死锁修改及对应验证。未自动启用 RW 解耦、拆分软件搬运或实施方案 B；不能删除失败用例换取通过。

以下为选择方案及实施前的历史记录。


2026-10-20 用户后续选择：采用方案 A，复用官方 `4c2390f2` 的按次配置接口，对目标 SPM 搬运启用 AW 解耦、保持 RW 耦合。当前先解释 CONF 配置位和 DMA 数据缓冲反压关系；本次仅本地源码核对及记录选择，未回移软件、修改 RTL 或运行服务器测试。方案 B 保留为备选，不同时实施。

### 2026-10-20 前次：DMA 解锁候选已梳理，未新增仿真结果

- 用户要求寻找解锁方案。本轮只读核对固定 LLC/iDMA 源码及官方提交，更新[专题第 7.4 节](../engineering/DMA_Control_Path_and_Fix.md#dma-unlock-options)与本交接；本地 HEAD 为 `c9abbb48946fe3a7244bfb3159919b7c9731cb59`，写入前备份为 `/tmp/e01-dma-unlock-mttemoiz/before/`。
- 推荐先验证每笔启用 AW 解耦的最小方案：已有本例成功记录，新增找到官方 PR #189 / `4c2390f2` 的按次 `conf` 接口，可局部采用并保留已修正的寄存器宽度；不是官方已关闭本例死锁。
- 默认模式的 RTL 候选是在 LLC 共享仲裁前预留读返回空间，并确保对应写数据已接收，必要时缩小内部子请求以适合现有 FIFO。只加读限流、写优先级或拆开描述符队列不足以证明消除双向等待；候选未实现，适用性及验证要求见专题。
- SSH 两次连接均超时，未登录服务器、重编或运行测试；没有新增“通过”结论。未改生产 RTL/sw、依赖、默认标志或现有测试，未回移上述提交；原默认长搬运失败保持。下一步按具体选定方案开展隔离验证，不据此自动实施生产修复。

### 2026-10-20 前次：长搬运死锁与单次断言原因已定位，生产修复待定

- 本地 Agent 按用户要求继续服务器诊断与官方 Git 核对，复用第 8 节的 simv/两份长测试 ELF，没有重编或修改生产源码。输入仍为 Cheshire `e040b7bbc`、CVA6 `99eac9a6`、iDMA `c12caf59`，LLC `559bcbd0`；完整记录见[死锁原因与对照](../maintenance/E01/reports/reference_rebuild_check.md#dma-stall-diagnosis-20261020)。
- 默认模式下六个 LLC 读描述符先于第一条写进入共同流水线；读返回满后，读请求挡住写描述符，写缓冲无法排出又阻止 DMA 收读数据，形成循环等待。解耦副本的写描述符提前到第三位，能继续搬运。**默认测试仍失败，未把解耦设为生产默认值。**
- 断言对应 `lwu 0x1001ff44`，返回整个字 `00000000_xxxxxxxx`，CPU 只取高 32 位；load_unit 实测 offset=4、valid=1、result=0，提交结果亦为 0。打印的 2 是下一条栈读取，因原 warning 未用 `$sampled`。此次告警原因已解释，不推广为所有 X 告警均可忽略。
- 官方 Cheshire #219 仍 open；iDMA #80/#204、Cheshire #294/#295 均已核对，尚无直接关闭本条 LLC 等待链的修复依据。CVA6 `e606cdfe` 修正其他 cache 的断言打印/检查，未涉及本例 WT 文件且保留整字检查限制。来源和适用性见[专题第 7.3 节](../engineering/DMA_Control_Path_and_Fix.md#dma-upstream-fixes)。
- 新日志和采样位于 `~/CheshireAraPULP/_e01/dma_vector_check/fix_validation_20261020/followup_diagnosis_20261020/`；首次 CPU 采样脚本有 Tcl 标签转义错误，保留并明确记为失败，修正后另目录重跑。所有运行是短窗口诊断，不重复计作三笔完整回归通过。
- 本地只更新专题、现有报告、本交接及 E01 共享状态，输入备份 `/tmp/e01-dma-followup-uvjgkv_1/before/`。下一步分别确定死锁修复与 WT/LSU 有效数据断言的最小改动，不自动实施、升级依赖或提取。
- 诊断结束时五项核心输入哈希不变；收尾 SSH 连续超时，未完成全工程 diff/旧 81 项哈希汇总，不能声称本轮已做该全量复核。关键采样此前已取回，各仿真进程已结束，详见报告第 9.5 节。

### 2026-10-20 前次实施：DMA 控制接口已修，默认长搬运仍未通过

- 按用户确认方案，仅修改服务器 `hw/cheshire_idma_wrap.sv` 与 `sw/include/dif/dma.h`：官方 `bca9aadb`/`ef11799d` 局部回移，另将四类单寄存器指针改为 32 位。新说明见[DMA 控制通路](../engineering/DMA_Control_Path_and_Fix.md)，实际命令、哈希、结果及限制集中于[控制接口修复结果](../maintenance/E01/reports/reference_rebuild_check.md#dma-fix-20261020)。
- 新产物在 `~/CheshireAraPULP/_e01/dma_vector_check/fix_validation_20261020/`，包含原件、分开的补丁、独立编译库、ELF、trace、采样和退出状态。原失败记录保留；依赖、FS 修正、默认硬件配置和生产 HAL 的解耦标志保持，未改本地 FPGA/RTL/sw、TTY 或 `/opt`，未启动子 Agent。
- 原编号/64 位读回两个失败项已通过；新 HAL 编号/字段检查、HelloWorld 和 22 字节向量复制通过。默认长二维搬运首笔停滞，原/修复 RTL 在同一 ELF 下出现相同总线状态。仅诊断副本置 `DECOUPLE_AW=1` 后三笔数据检查通过，但出现 CVA6 读数据断言警告；不能把它作为默认配置验收通过。
- 下一步应另定 R/AW 耦合与 LLC/SPM 等待关系、断言警告的排障/修复范围。此次不修改 iDMA/LLC 内部、默认标志或 1D 功能，不升级依赖，不开始提取。已对照官方 main `6c6dd5e8` 准备独立 HAL 贡献草案，未运行完整最新上游工程、commit、push 或发布 PR。
- 本地新增专题，并更新现有报告、工程索引、状态、任务表及本交接；进入时内容备份在 `/tmp/e01-dma-fix-pxoiby3o/before/`。下节“修复未实施”是本次实施前的历史记录。
- 交付检查：新增正文/报告部分的 13 个本地链接、11 张表、代码围栏及范围内 `git diff --check` 通过；报告原第 1–7 节字节保持。服务器 81 项受保护输入不变。进入时本地范围外 175 个文件哈希不变，另有 7 个 DDR/L01 文档及预览在本轮期间发生并行变化，本 Agent 未写入或回退它们；清单与增量差异在上述临时目录 `validation.json`。未将静态 Markdown 检查称为 GUI 渲染验收。


### 2026-10-20 修复前记录：服务器 DMA/向量疑点测试完成，DMA 修复未实施

- 用户已授权本地 Agent 通过 SSH 实施指定测试。完成原 DMA、原向量、向量最小修正副本、DMA 编号检查和字段读回；另用同源码/配置的新调试构建完成内部追踪。完整结果和原因集中在[控制接口测试](../maintenance/E01/reports/reference_rebuild_check.md#dma-vector-tests-20261020)，不以原用例 SUCCESS 代替控制路径检查。
- 向量副本 `errors=0 bytes=22`；原向量也能打印，实际打印的是编译器生成的向量栈副本。DMA 原 38 字节比较通过，但内部 ID=2 而 CPU 读到 0；64 位字段写只更新低半部。诊断分别返回 64/67，当前仿真进程却均退出 0。软件、RTL 控制适配及失败退出处理尚未修复，不据此断言 DMA 搬运核心损坏。
- 所有新源码副本、ELF、日志、CPU trace、Tcl 和构建库在服务器 `~/CheshireAraPULP/_e01/dma_vector_check/`。原输入 15 项哈希、根 Git 状态/diff 前后一致；四项相关依赖 HEAD 一致、受跟踪源码无差异。保留 FS 修正及旧结果，stub 未运行，不写提取目标、TTY 或 `/opt`，不委派子 Agent。
- 本地仅更新本交接、既有报告、方案、PROJECT_STATE、AGENT_TASKS；保护已有 AGENTS、仿真指南及未跟踪图稿。输入备份为 `/tmp/e01-reference-tests-smx315kj/`。本任务止于测试与报告；最小后续是另行确定 DMA 控制接口/HAL 修复范围及对应回归，不能把本轮作为开始提取的授权。

### 2026-10-20 测试前记录：stub 勿用，准备服务器验证（现已执行）

- 用户决定：stub 测试不纳入后续测试，不再安排去除 stub 后复用。现有 25 个入口调整为 4 个纳入、1 个待修正、15 个勿用、5 个配置不适用；15 个包括 13 个 `mmu_stub` 入口、寄存器用例及仍执行 stub 初始化的原版 `rvv_test_exceptions.c`，非 stub CSR 用例保留。此决定取代下节原“8 个需处理/确认”的建议，详见[现行测试表](../maintenance/E01/planning/server_reference_extraction_plan.md#existing-test-inventory)。
- 已定位 stub 硬件来自本地保留的 `mp/ara-pulpv1-os-debug` 分支；配套寄存器/硬件提交不在固定参考版本祖先中，具体提交及 Ara no-stub 兼容改动保存在上述方案。未从该分支复制或恢复硬件。
- 用户提出 DMA 的宽度/截位可能是特定配置下的配套约定。现保持为待验证解释：相邻 ID 属不同通道，当前未用通道置零，旧本地 GCC 15.2.0 汇编有两次 32 位读，但不能代替服务器 GCC 13.2.0 实际 ELF；下一轮先检查实际访问和原版运行，不先改驱动/RTL，也不称故障已经复现。
- [下一任务准备](../maintenance/E01/planning/server_reference_extraction_plan.md#dma-vector-reference-check)限定为服务器参考工程上的 DMA 原版测试/必要定位、向量 HelloWorld 测试副本的最小修正与结果比较；由本地 Agent 执行。用户明确下一轮再决定，本轮未登录服务器、构建、仿真或改工程。保护原件、现有 FS 修正及旧结果，完成后不自动提取。
- 本轮只更新方案、本交接、PROJECT_STATE、AGENT_TASKS；输入备份 `/tmp/e01-stub-exclusion-w67aavel/`。不新增报告、脚本或测试源，不改 AGENTS、仿真指南及未跟踪图稿。
- 保存后核对 25 个测试入口无遗漏或重复，15 个原版 stub 访问用例逐项标记勿用，非 stub CSR 用例保留；新增链接/锚点、围栏及 `git diff --check` 通过。这些是文档检查，服务器验证仍未执行。

### 2026-10-20 初次梳理：本地执行，现有测试梳理完成（分类已由上节调整）

- 用户暂不将 E01/Bender 剥离相关任务交给服务器 Agent，改由本地 Agent 执行；替代下节对此类任务的服务器实施分工，独立子系统约定不变。本次“第 1 步”是梳理现有测试，不是重做历史工具链检查。
- 结果集中保存于[方案第 6.1 节](../maintenance/E01/planning/server_reference_extraction_plan.md#existing-test-inventory)：Cheshire 官方软件入口 7 个、Ara 集成入口 18 个，分为 4 个纳入计划、8 个需处理/确认、13 个不适用。重点发现为缺失 stub 寄存器被原辅助头文件映射到偏移 0、向量 HelloWorld 的错误打印参数，以及现有用例尚未覆盖的既定验收项。
- 读取使用 `git ls-tree`、`git show`、定向 `rg` 与 `git diff`；Ara 工作区存在本地修改，未作为固定参考版读取。核对硬件配置、寄存器、测试入口/正文、软件构建规则及退出路径；未登录服务器，因此不把这次本地检查描述为服务器当前文件核验。原 HelloWorld/fmatmul 成功记录保持，未新增运行结论。
- 修改仅限 `AGENTS.md`、`PROJECT_STATE.md`、`AGENT_TASKS.md`、本交接和既有实施方案；旧记录和未提交内容保留，输入备份 `/tmp/e01-test-inventory-tev4gb5b/`。不新增测试、脚本、报告或协作机制；不改动仿真指南、RTL/sw 和未跟踪图稿。
- 保存后核对表中 25 个文件名与两个固定提交的测试入口一致，无遗漏或重复；新增链接/锚点、代码围栏及 `git diff --check` 检查通过。以上均为源码和文档检查，不是编译或仿真结果。
- 本步到此结束。下一任务应依据表中具体问题确定范围；不自动适配测试、运行参考工程或实施提取，不静默删减旧验收要求。

<a id="collaboration-decision"></a>

### 2026-10-20 协作约定同步（用户确认，文档交付）

- 正式约定见[根 AGENTS.md](../../AGENTS.md#local-server-collaboration)，消息级下发/回报格式与证据归属见[任务表](../AGENT_TASKS.md#server-task-brief)。Cheshire SoC 本地统筹、服务器按任务自主实施；NPU 等独立子系统由用户/负责人直接与服务器 Agent 推进，系统接口约束提前输入，集成时再对接，不要求内部逐项送回本地审批。
- **授权边界：**用户认可按明确任务授权，任务可含完整小闭环；本地依据本次实际差异/证据评审，可在授权内 SSH 只读核查，不同时修改服务器实施中的文件和产物。此次只授权文档同步，没有授权登录服务器、复跑 HelloWorld/fmatmul、提取、改配置或清理；未启动自动子 Agent。
- **尚未接受的建议：**“最小参考确认后开始提取、部分参考测试移至两工程对照”仍待讨论，不能当作新验收顺序。原参考验收要求及先参考验收、后提取的顺序保持；第一项具体服务器任务尚未授权。历史各节的“最小下一步”是建议，不构成本次执行指令。
- 本次修改路径：根 `AGENTS.md`、`docs_codex/AGENT_TASKS.md`、`docs_codex/PROJECT_STATE.md`、本交接及 `docs_codex/maintenance/E01/planning/server_reference_extraction_plan.md`。长期规则、简短任务格式、状态入口和旧计划授权口径分别归位；不新增协作平台、脚本或管理文件，不修改工程与仿真指南。
- 输入备份及范围核对基准：`/tmp/e01-collaboration-20261020-yq7dq3uv/`。保存后重读增量，确认 SoC/独立子系统职责、任务内自主权和未授权事项一致；五份 Markdown 的 9 个新增相对链接/显式锚点及代码围栏检查通过，`git diff --check` 退出 0。原交接全部既有内容保留，指南及测试平台图稿共 28 个文件哈希不变。未连接服务器、编译、仿真或提交 Git。
- 最小下一步：本地讨论并确定下一项具体 SoC 任务的目标、权限和完成判据，再由用户转交服务器；不依赖跨设备记忆，不全盘上传历史。独立子系统继续沿自身必要记录推进，到集成时提供摘要。

### 2026-10-19 波形采集与验证/Debug效率文档（当前说明）

- 用户确认普通回归默认不导出波形；启用波形后的首个示例为**全程、fixture和DUT本层、结构体采集**。这替代指南此前“首次固定前10μs”的默认教学方式，不改变历史短测事实，也未替用户修改服务器wave.tcl。
- 修改仅限`software/SERVER_SIMULATION_GUIDE.md`与本交接，输入HEAD为`c9abbb48946fe3a7244bfb3159919b7c9731cb59`。正式说明集中在[指南7.0](../software/SERVER_SIMULATION_GUIDE.md#wave-tradeoffs)及[7.5排障流程](../software/SERVER_SIMULATION_GUIDE.md#debug-evidence-flow)：区分构建调试能力、波形写盘和trace开销；说明不采集时的验证依据、层次/数组/窗口选择、not found排查及修复后回归。第8章增加入口链接，不新建专题、参数接口或脚本。
- 官方依据沿用此前已核对的固定版本start、UCLI手册dump命令及第108—109页数组选项。示例使用原生dump；带`[0]`的Ara路径用Tcl花括号保护。全程不等于全层次，关闭dump不等于恢复普通构建性能，不给出未经实测的减速比例。
- 文档检查：12个Bash代码块通过`bash -n`，4个Tcl块通过`info complete`语法完整性检查（未执行UCLI命令）；74个本地链接目标、新锚点、默认5行采集示例及路径保护检查通过。第0—6章操作正文、第8章原排障表/结尾及旧交接记录保持；只有上述两文件变化，`git diff --check`通过。以上不作为仿真/性能证据。
- 验证边界：既有20μs短测、前10μs本层FSDB及读取结果保持；全程示例、全层次、数组、完整波形版fmatmul和GUI仍未验收。本轮只检查文档，不访问服务器，不编译、仿真、采集或做性能测试；未改共享状态，未提交Git。最小下一步为用户按实际任务选择采集方式，取得新的运行证据后再更新结论。

### 2026-10-19 UCLI波形调用修复（短测通过，完整运行待用户执行）

- 用户波形版展开/KDB成功，但`wave.tcl`第1行`call fsdbDumpfile`报`UCLI-CALL-CMD-GENERAL`，退出于0ps，未取得本轮fmatmul成功。原文档中的该调用方式已被实际失败证据否定；不把它归因于RTL，也不因已链接pli.a推断任意UCLI调用都有效。
- 核对服务器安装手册`/eda/synopsys/vcs/W-2024.09-SP1/doc/UserGuide/pdf/vcs_ucli_ug.pdf`第3章dump命令（手册页106—117），采用`dump -file ... -type FSDB`、`dump -add ... -depth 1 -fsdb_opt +struct -fid FSDB0`和`dump -disable -fid FSDB0`。保持两个本层范围、10μs采集窗口和停采后继续运行；没有增加`-P`、包装脚本或修改RTL。
- **实际修复文件：**服务器`~/CheshireAraPULP/target/sim/vcs/wave.tcl`；本地仅`software/SERVER_SIMULATION_GUIDE.md`及本交接。服务器start原已有`-debug_access+all`及`-ucli -do wave.tcl`，无需修改。guide的7.2/7.4同类旧命令及排障表同步修正；可选延后窗口使用官方`dump -enable`，本轮未实测该可选窗口。
- **短测：**在服务器`/tmp/e01-wavefix-blj40e7a/`使用现有simv绝对路径，传入BOOTMODE=0/PRELMODE=1和现有fmatmul绝对路径，运行`-ucli -do probe.tcl`；60秒墙钟上限。probe前5行与交付wave.tcl一致，仅将末尾无限时长`run`换成`run 10us`，总计20μs后退出，主机rc=0。0ps成功打开FSDB，两个层次遍历及结构体支持正常，10μs停采后继续到20μs；无UCLI错误，保留原0ps RT-NCMUCS及ELF零填充提示。短测已开始预加载，不代表完成应用。
- **真实波形检查：**生成550384 B的`wave.fsdb`；用同版Verdi自带`fsdb2vcd wave.fsdb -o wave.vcd`读取成功、rc=0，734个变量，1ps时基。`fix.clk`有4001条值记录，`fix.rst_n`在25000ps释放；10μs处停采产生X记录，后续未继续记录时钟翻转。这验证了采集、可读性和停止采集，不等同于Verdi GUI检查。
- **保护与证据：**短测前无相关工具进程，失败wave.tcl、start及完整simulate/elaborate日志备份到上述临时目录的`before_*`，短测日志`probe.log`、退出值`probe.exit`、FSDB/VCD、读取日志`fsdb_read.log`及`repair_result.json`同目录保留。修复前后比较当前vcs目录其余224项（文件哈希/权限和链接目标）一致，未覆盖正式日志、trace、simv或数据库；start通过`bash -n`。本地两文档输入备份在`/tmp/e01-ucli-fix-2aewfeeg/`，不保存供应商手册正文。
- **交付哈希：**wave.tcl SHA256=`95af50128e8b156bf0b96bd71bf54ac13475c1e4853748e31a7b747de6359804`；短测及交付时现有simv SHA256=`d083613676b800e19c814d8509455cf393d6f35f5cd8945df246d5f86090c9e3`。未重编，未完整重跑fmatmul，未启动Verdi GUI或修改共享状态，未提交Git。
- **文档检查：**指南采集代码块与服务器交付哈希一致，第7章Bash示例通过`bash -n`；相对链接、围栏及`git diff --check`通过，可执行示例中的旧call命令已全部替换。两文档增量差异存于上述本地临时目录。
- **最小下一步：**用户在服务器`target/sim/vcs`执行`bash start.cheshire_soc.sh`，结束后立即读取`echo $?`，核对本轮Passed/SUCCESS及FSDB，再用匹配的simv.daidir打开Verdi。此前普通仿真通过仍是独立证据；本节替代下方“FSDB完全待实测”及旧call采集写法，保留历史失败和未验证范围。

2026-10-19 波形设置最小化（当前波形说明）：按用户要求精简[指南第7章](../software/SERVER_SIMULATION_GUIDE.md#waves)，复用官方start，保留`-O2/-kdb`，仅调整调试访问和增加`-ucli -do wave.tcl`。已有链接证据包含Verdi `pli.a`，撤下默认`VERDI_HOME/-P`配置；实际FSDB错误发生时才定向处理。启动采集Tcl只保留输出文件、两个本层采集范围、10us窗口、停采后运行至结束及退出，移除默认START/LENGTH变量和零时长跳过逻辑；后移窗口方法留在7.2按需查阅，保留限制层次/时间与继续完成程序的要求。此记录替代此前波形方案中“必加显式PLI链接”的要求，不改普通仿真及其验证结论。本轮仅编辑指南与本交接；未新建仓库脚本、访问服务器或运行仿真/Verdi，FSDB/GUI仍待实测。

本轮文档检查：第7章Bash块及将修改应用到官方脚本所得的临时文本通过`bash -n`；相对链接、代码围栏、7条采集命令及第8章未变检查通过，`git diff --check`通过。输入文档备份和增量差异位于`/tmp/e01-minimal-wave-fr15vj9k/`。这些是语法/范围检查，不证明FSDB命令在目标环境运行成功；未提交Git。

### 2026-10-19 最新普通仿真检查与清理（已完成）

- **范围与输入：**用户明确“本次仿真已结束”后才连接 `zhaowy24@172.16.0.243`；本地 HEAD=`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，服务器 Cheshire HEAD=`e040b7bbc7851a37faff3c4657ff8d656cc6e20a`。本轮仅删除下列服务器历史目录、更新本交接及既有核查报告的最新状态提示；未修改 RTL/sw、依赖、TTY、工具或共享状态文件，未重编/重跑。
- **本次运行定位：**工作目录为 `~/CheshireAraPULP/target/sim/vcs`，入口为 `compile.cheshire_soc.sh`、`start.cheshire_soc.sh`。start 当前设置 `set -e -o pipefail`、`BINARY="../../../sw/tests/fmatmul.spm.elf"`、`BOOTMODE=0`、`PRELMODE=1`、`SELCFG=3`；相对官方版本还恢复了首行 shebang，其余执行逻辑保持。`simulate.log`实际加载上述相对路径（解析为工程内 `sw/tests/fmatmul.spm.elf`），日志内部记载 Oct 19 07:44 启动、07:51:23 结束；`elaborate.log`为 Oct 19 07:44:12。识别依据还包括脚本内容、加载记录、展开重建命令及新 simv 链接库名；不是只按文件 mtime。旧备份实际是 Oct 18 的 HelloWorld，旧04为 Oct 18 fmatmul，不能与本次混用。
- **配置核对：**生成清单及实际 `AN.DB/make.vlogan`只含 `cv64a6_imafdcv_sv39_config_pkg.sv`、Ara 路径的真实 `cva6_accel_first_pass_decoder.sv`，宏为 `ARA/NR_LANES=2/VLEN=2048`；TB配置3明确 `Ara=1/AraNrLanes=2/AraVLEN=2048`。展开日志对 TB/fixture 均记录 `SelectedCfg=3`，`simv.daidir/vcs_rebuild`与官方 start 的展开选项一致。
- **阶段结论：**本次展开日志记录增量编译2个模块、链接完成、`../simv up to date`及 KDB 成功生成；运行日志依次显示标量/向量计算、`Verifying result...`、`Passed.`、`[SLINK] SUCCESS`和正常 `$finish`（26019135000 ps）。程序报告19883内核cycles，主机CPU Time为403.900秒。两份完整trace各1316145行，未检出 `Exception`。独立的 RTL `vlogan` 编译控制台日志未取得，只能确认当前编译库支持这次成功展开/运行，不能补称完整编译日志已审查。
- **退出状态：未取得。**目录未保存本次 `exit.status`；用户只观察到终端 SUCCESS，未保留刚结束时的 `$?`。SSH/检查命令退出0不是仿真退出码，旧04的0也不能移用于本次。
- **警告与边界：**展开仍有245条 SIOB、9条 ENUMASSIGN，未全部完成语义审查；运行有1条 `axi_inval_filter.sv:85` 的0ps RT-NCMUCS。另有 ELF 的 `0x8024` 零填充提示，与 LOAD 段 `MemSiz 0x9d84 − FileSiz 0x1d60`一致，源码crt0包含BSS清零；ASLR提示属于仿真器重执行信息。所读日志未发现错误，官方tee未单独保存stderr，不能声称检查过未留存终端输出。本次未要求/生成FSDB，不据此判失败；只确认官方32×32 fmatmul单例通过，完整RVV、SPI自主启动、FS Dirty原因及ASIC就绪均未验收。

**本轮读取时的SHA256**（检查时快照，不伪称运行前自动记录）：

| 文件（相对工程根） | SHA256 |
| --- | --- |
| `target/sim/vcs/start.cheshire_soc.sh` | `1fcef44a43b7aa6950303c4f6f04701cfc994193c7603ff9cb33f13b091dc680` |
| `target/sim/vcs/compile.cheshire_soc.sh` | `4ee24c78016eaea0800c2470cab3c3b08fe928184950aeae4e2c1bf0c36f9f52` |
| `target/sim/vcs/simv` | `0f3d70968014aebecbbf4cca8bc24b7c9f403ba48aa24ec653e0bc96ae70873e` |
| `sw/tests/fmatmul.spm.elf` | `4746bc7ebd17bae54adf2732e03720e385277ba92e88690474880b91152dc626` |
| `target/sim/vcs/elaborate.log` | `823b28eea33116eab8e561fb7351f809f6a4d3d5dad46679971b7a585ba51150` |
| `target/sim/vcs/simulate.log` | `27b81885f2581a07975c165519e3c68a80d190df8afeb347385775337af2271e` |

**清理清单与保留用途：**

| 处理 | 路径（相对工程根） | 理由/用途 |
| --- | --- | --- |
| 已删除 | `_e01/rvv_fmatmul_01`、`rvv_fmatmul_02`、`rvv_fmatmul_03`、`rvv_fmatmul_04`（均在`_e01`） | 旧失败/成功运行及trace；退出状态依次124/124/124/0，输入哈希与[报告第6节](../maintenance/E01/reports/reference_rebuild_check.md#6-首次-fmatmul-运行超时诊断2026-10-18-增量)所述一致；异常、FS诊断、有效推进超时与最终通过的历史结论已保存 |
| 已删除 | `_e01/vcs_before_wave` | 旧HelloWorld构建/运行备份，非波形运行；simv为旧`540e4f91…`，标量成功已记于报告第1—2节。备份start与服务器Git HEAD原文件逐字一致，compile与当前文件一致，无独有源码修订；没有FSDB |
| 已删除 | `_e01/rebuild_20261018_082329` | 已核实为空目录 |
| 全部保留 | `target/sim/vcs/` | 两个官方入口、完整展开/运行日志、两份trace、simv、运行/调试数据库、增量编译库与内部辅助文件；不把内部`csrc/clean.sh`当教学包装脚本 |
| 保留 | `target/sim/vcs/simv.daidir`、`work.lib++`、`AN.DB`、`csrc` | `readelf -d simv`确认直接依赖`_3946352_archive_1.so`和`_prev_archive_1.so`，均位于simv.daidir；KDB有3个链接指向当前work.lib++。其余用于编译/增量重建及设计查询，未拆分删除 |
| 保留 | `_e01/preflight/`、`_e01/eeprom.zip` | 前者为工具链检查及探针输入/输出；后者含3份EEPROM模型，属于来源包，不按仿真废物删除。软件副本及crt0源码备份均未触碰 |
| 暂留 | `target/sim/vcs/csrc/_3383237_archive_1.so` | 已存在的失效旧链接，当前simv的NEEDED不引用它；尚未全面证明VCS内部增量元数据是否依赖该项，因此随csrc保留。不是本轮删除造成，当前必需的两份设计库链接有效 |

删除前再次检查相关进程和打开文件，未发现VCS/simv/Verdi或目标产物使用者；检查实际路径、设备号与所有链接，使用6个明确路径及不跟随符号链接的删除方式。旧备份中指向当前work.lib++的链接仅随备份移除，目标文件未动。未发现独立的config/build/run/view教学包装脚本，无此类额外删除。

合计删除分配空间859054080 B（约819.26 MiB，未计顶层目录自身）；清理后`_e01`只剩`preflight`和`eeprom.zip`。清理前后对当前vcs全树、preflight、模型zip、当前ELF及crt0/备份共431项进行比较，其中394个普通文件SHA256一致，其余目录/链接的类型、权限、目标及链接有效性一致；服务器Git状态也一致。此为静态完整性检查，**没有重新运行仿真或Verdi**。

本地写入前备份：`/tmp/e01-cleanup-docs-4usb8j4u/`，仅备份两份待编辑文档，不搬存服务器旧产物。下方历史记录所称“保留四次运行/下一步保留旧目录”已由本次明确清理授权替代；历史结论继续有效，原服务器目录已删除。本轮未提交Git，未代改已有并行共享状态。最小下一步仍按用户后续选择开展验证；日常继续使用现有两个官方入口。

### 此前方案与验证记录

2026-10-19 按需配置再精简（当前方案）：按用户确认的“每一步只引入当下必需内容”，[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)只设BINARY/BOOTMODE/PRELMODE/SELCFG，工具环境沿用重建步骤；仅加`set -e -o pipefail`，保留官方执行末尾。取消上一版重复路径/空值/默认值、WAVES和限时变量、自动哈希及状态文件生成；限时验收引用已有命令。[第7章](../software/SERVER_SIMULATION_GUIDE.md#waves)按需设置调试/FSDB选项、保存wave.tcl并为原simv增加UCLI选项，直接打开Verdi。第2/4/5/6/8章引用与检查口径同步，详细配置追踪保留。只改指南和本交接；已有服务器文件不删除、不部署，原验收与缺陷状态不变。

2026-10-19 官方入口精简（历史，已被上方按需配置方案替代）：用户确认优先复用官方脚本，参数集中写入`start.cheshire_soc.sh`顶部。[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)现为“备份→编辑官方start及wave.tcl→compile/start→直接Verdi”四步；启动脚本只补充配置、调试/FSDB入口及超时/失败传播，保留官方阶段和日志位置。取消指南的config.sh、build.sh、run.sh、view.sh实现与构建/运行编号、配置指纹、数据库路径管理，第5/6/7章与练习同步。保留详细配置追踪及旧失败/成功证据，日常同名产物覆盖前须归档。该方案替代下面的五文件方案；未删除用户可能已建的服务器文件，也未修改本地或服务器官方脚本。FSDB联编、采集与GUI仍待目标实测，参数逐步开放策略及原验收缺口不变。

2026-10-19 文件配置式操作入口（历史，已被上方官方入口方案替代）：用户要求先在文件中修改参数，再以简短脚本运行VCS及Verdi，避免先读大量追踪参数。[指南第0节](../software/SERVER_SIMULATION_GUIDE.md#quick-workflow)现为首读入口，脚本内容放在折叠区供首次保存；日常改config.sh的ELF/RUN_NAME及wave.tcl采集设置，执行`bash build.sh/run.sh/view.sh`。该样例限定现有配置3/UseDramSys=0和已生成向量清单；不撤销已确认的后续参数逐步开放策略，也未建立独立提取工程。各次构建/运行拒绝覆盖已有目录，run核对所列构建设置，view使用运行记录的build.path；不声称自动识别全部RTL/include变化，源码变化须新建构建。旧第5/7节重复的显式长命令已替换为统一入口，软件构建详解继续保留。仅保存文档中的脚本内容，未生成服务器脚本文件，FSDB/PLI/GUI仍待实测。

2026-10-19 参数策略确认与文档同步：用户同意固定 CVA6＋Ara 功能组合，保留集中参数入口，每次构建锁定有效配置，在原基线完成提取对照后逐步开放 L1 容量/LLC 行数，再按瓶颈评估其他参数；应用结果与一致口径的面积、时序、功耗共同决定产品配置。此决定取代初版“长期只允许一个固定参数配置”的限制，不代表具体候选值、lane 数或最终产品配置已经选定/验收。已同步 [02 规格第 3.3 节](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md#parameter-policy)、[资源指南 Q7/Q8](../engineering/Fixed_Vector_SoC_Resource_Guide.md#q7)及[服务器方案](../maintenance/E01/planning/server_reference_extraction_plan.md)，配置目录统一为待实施的 `src/config/`；源码保留覆盖声明支持范围，TB/综合共用配置与 wrapper，按配置/运行保存独立证据。来源仍为同版本服务器参考 `~/CheshireAraPULP`，提取目标为 `~/CheshireAra`，旧本地复制及阶段 0 状态保留为历史。只改上述三份正文和本交接，保留并行配置导读和原始验证记录；硬件/软件/参数/共享状态均未改，未构建、仿真、综合或访问服务器。输入备份与保护哈希位于 `/tmp/e01-parameter-policy-uqiuf7qd/`，未提交 Git。

2026-10-19 配置导读整理：用户同意先理解当前配置来源/覆盖/作用，再收敛为配置文件与简短脚本。本轮仅文档实施：[上手指南第4章](../software/SERVER_SIMULATION_GUIDE.md#config)增加配置载体解释、CPU/SoC双路径图、Ara/LLC/启动/波形四例及只读判断练习；[配置流程首节](../configuration/RECIPES.md#server-config-trace)列文件地图、当前SoC/CPU关键值、TB/VIP参数与脚本/软件输入的消费者和重做范围；配置README链接并纠正“parameter都是硬件配置”等过度概括。字段全集沿用旧字典，不另建文档。旧本地清单问题及本地eew/printf默认值与服务器状态已分开；指南同步引用此前FS修正和单例成功记录，不新增运行结论。共享状态/其他主题文件不代改；config.sh/build.sh/run.sh尚未创建。

本轮依据与边界：定向阅读本地cheshire_pkg/SoC/typedef、TB/fixture/VIP、CVA6 profile/config/build_config及Ara集成入口；追踪了`Cfg.Ara→gen_ara`、`get_llc_size→i_llc`、`gen_cva6_cfg`覆盖及VIP实例绑定。SSH拟只读比较13个配置定义/消费者文件，但`ssh -o BatchMode=yes -o ConnectTimeout=10 …`在banner交换阶段超时，退出255（`Connection timed out during banner exchange`），未取得服务器文件哈希或新验证结果。表中取值标为当前源码推导，实际构建/运行仅引用2026-10-18报告，未把连接错误写成工程构建失败。文档验收记录见下方“配置导读检查”。

2026-10-19 资源问答文档：用户明确授权实施已确认整理计划，新增[固定向量 SoC 资源、存储组织与配置问答](../engineering/Fixed_Vector_SoC_Resource_Guide.md)，收录资源总览、Cache 策略、bank/word 地址、LLC 深度、TLB/预测器、宏替换、Cache/VRF 扩容和 v1 性能取舍。主要 SRAM 为 163744 B（159.90625 KiB）、48 个逻辑实例，仅含所列 Cache/VRF 数据和标签；采用实际选中的 `sram_pulp` 位宽，区分 TLB 声明/功能字段/综合网表、Boot ROM 内容/链接预算/地址窗口及未验证扩容。正文是技术说明，数值不代表综合总面积或完整 SoC 状态位数；既有服务器运行结论不扩大。本轮仅修改该正文、工程 README 和本交接，不修改共享状态、原封装预算、RTL、软件或依赖，不执行构建、仿真和服务器审计。输入备份与既有 206 个修改/未跟踪文件哈希保存在 `/tmp/e01-resource-guide-_r7jjgc6/`；最终检查见文末资源问答检查记录，未提交 Git。

2026-10-18 fmatmul通过与FS排障归档：用户完成 `_e01/rvv_fmatmul_04`，Agent只读核对Passed、SLINK SUCCESS及exit.status=0；ELF `4746bc7e…` 与03一致、simv不变。启动FS显式Clean修正已通过该32×32测试；程序报告19883内核cycles，VCS CPU Time 402.720秒。已更新[重建速查Q07](../maintenance/E01/planning/server_reference_rebuild_guide.md#q07)、[核查报告第6节](../maintenance/E01/reports/reference_rebuild_check.md)与本交接，保留四次运行及历史判断，备份位于 `/tmp/e01-fs-closure-med62rx7/`。硬件Dirty状态跟踪原因及完整参考/提取验收仍开放；本轮未远程修改或运行工程，不代改并行共享状态。

2026-10-18 第三次运行进展：用户 `_e01/rvv_fmatmul_03` 在180秒限时返回124。只读核对新ELF `4746bc7e…`、后读数FS=Clean(2)，完整trace未检出Exception，旧trap地址计数0；标量fmadd.d已执行24,413/32,768次（74.5%），完成762个输出元素，末尾索引仍推进。判定原FS关闭问题已被软件修正绕过，本次是标量参考计算尚未完成时被限时终止；向量及结果比较仍未验证。建议同一ELF/simv在新run_04目录以600秒限时重跑，不重编或改RTL。证据与范围见[核查报告第6节第三次运行](../maintenance/E01/reports/reference_rebuild_check.md)；硬件Dirty状态跟踪疑问仍开放，本轮未远程修改或执行仿真。

2026-10-18 第二次CSR诊断实证：用户运行 `_e01/rvv_fmatmul_02` 返回124。Agent只读确认新ELF哈希 `e51af8a5…` 与运行前记录一致，清位前t2=`0x0000000a00002000`、清位后t3=`0x0000000a00000000`，FS确由Initial降为Off；随后 `0x100012e8` 的c.fsdsp异常并进入原trap循环。替代此前“FS关闭待证”的状态。下一步建议在用户已改的服务器crt0中显式设置FS=Clean，重编单ELF再运行；尚未修改或验证修复，CVA6为何未置Dirty仍独立待查，见[报告第6节增量](../maintenance/E01/reports/reference_rebuild_check.md)。

2026-10-18 CSR诊断准备增量：用户自行备份服务器 `sw/lib/crt0.S.backup` 并直接修改原 `crt0.S`。Agent只读确认diff恰为原清FS低位指令前后新增 `csrr t2,mstatus`、`csrr t3,mstatus`，尚未修复FS、尚未重新构建。此用户选择替代此前“独立启动副本”的建议；本地原工程仍受保护。服务器fmatmul.c和fmatmul.o已由旧构建流程移除，ELF和测试头文件仍在，因此给出从同版本Ara恢复单个C源、沿官方参数仅重建crt0/库/fmatmul ELF及dump的命令；保留旧失败输入，未代执行构建或仿真。

2026-10-18 首次fmatmul超时：用户运行 `_e01/rvv_fmatmul_01` 返回124；Agent只读确认trace在 `0x100012e0` 的 `c.fsdsp fs0,24(sp)` 报Illegal Instruction，随后 `0x1000018c` 默认trap自循环2,238,884次，尚未执行printf或向量计算。原crt0清FS低位的写法为首要待证线索，现有trace不含mstatus读回，不能直接宣称FS=Off或硬件Dirty更新失效。最小下一步是在独立启动副本加入清位前后两次CSR读数，只重编一个诊断ELF、复用simv，由用户逐步执行；若证实FS关闭再做显式FS初始化修复。详见[核查报告第6节](../maintenance/E01/reports/reference_rebuild_check.md#6-首次-fmatmul-运行超时诊断2026-10-18-增量)。本轮仅本地报告/交接更新，无远程修改、编译或仿真；共享状态不代改。用户另要求后续围绕实际源码、ELF构建、TB输入输出及结果判定提供上手引导。

2026-10-18 上手指南交付：[正文](../software/SERVER_SIMULATION_GUIDE.md)采用用户选择的“实操与源码结合”，以VNC桌面中的Verdi为波形主线，已有重建文档继续负责安装/历史排障。修改文件仅新增正文、软件README入口及本交接；共享状态文件已有并行修改，不代为更新。服务器只读核对确认VCS/Verdi/DVE W-2024.09-SP1安装；原启动脚本未将VCSARGS追加到flags；文档因此给出独立输出目录中的显式调试流程，非已执行适配。核对fmatmul发现无符号输入减法、首元素失败后负下标打印、浮点比较及性能打印局限，已在指南说明；故障注入仅安排在教学副本索引1，不修改第三方源码。旧五步核查结论不因本轮文档交付扩大；新运行目录存在也不作为运行通过证据。下一步由用户分步执行练习，先核对原始fmatmul完整日志，再验证副本构建和有限窗口波形。文档检查见下方“上手指南检查”。

2026-10-18 五步完成核查（本地HEAD仍为`2f0f2d6f…`）：用户报告完成速查1—5步，Agent经SSH只读核对。参考根为e040b7bbc、26项依赖匹配；pip check实测通过（现有pip26.0.1）；向量profile、Ara decoder、2 lanes/VLEN2048及展开SelectedCfg=3正确。现有VCS日志确认标量HelloWorld的`[SLINK] SUCCESS`；18个Ara源的54个ELF及配套产物齐全，抽查含RVV指令。未发现向量运行日志，SPI自主启动/访存原子及独立提取未验收；展开日志245条SIOB、9条ENUMASSIGN和运行时0ps一条RT-NCMUCS需按范围审查。详见[五步核查报告](../maintenance/E01/reports/reference_rebuild_check.md)及其证据快照。本轮未构建、仿真或修改服务器；以下早期“未实施/待确认”保留为历史，不覆盖本段最新事实。

2026-10-18 用户选择版式A：重建速查现为“前半操作流程＋步骤旁问题链接，后半Q01—Q06排障索引及完整记录”，未新增排障文件。Q06补录 `-DEEW= -DPRINTF=`、预处理及连锁错误，给出 `eew=64 printf=1` 的最小命令修正和warning分类；修复后结果待确认。用户反馈第4步无新问题，尚未提供该步完整日志，不扩大为向量仿真通过。本轮仅文档重排及补录，旧稿备份 `/tmp/e01-guide-layout-5zb2j3nv/server_reference_rebuild_guide.md`；既有报错摘录保留，未操作服务器。

2026-10-18 排障说明补全：按用户要求将重建速查的 curl 7、curl 60、Bender E31/W28 及 pip 冲突补为可对应的关键原始日志、原因、处理命令和结果边界；W28附服务器已核对的include关系及清单路径。替代此前过度压缩的说明，不改变工程配置和警告处理结论，本轮仅修订文档。

2026-10-18 W28复核：用户日志显示 Flash 经单次 `curl -k` 下载后，Questa/VCS清单生成走完，剩余两项 `.svh` 未知类型警告。Agent经SSH只读确认服务器上的两份头文件、tracer include关系、VCS清单的tracer源及 `+incdir+` 均存在；判断低严重度，可暂时忽略，不修改Bender清单或源码。[速查第3节](../maintenance/E01/planning/server_reference_rebuild_guide.md#3-生成硬件和向量仿真清单)已补充依据与处理边界，替代此前E31修复结果待确认的状态；未执行RTL编译或仿真。

2026-10-18 清单生成顺序纠正：用户报告 `update_vsim_src` 在 Questa 清单生成阶段因缺少 `s25fs512s.v` 报 Bender E31。原速查将模型下载放在清单生成后，现已在第3节纠正顺序并补充文件检查；补齐模型后重试原入口，无需清理依赖。仅更新文档，未远程执行，修复后结果待确认。

2026-10-18 网络排障：用户第3节 `hw-all` 在下载 printf 子模块时超时。Agent经SSH只读确认 Mihomo HTTP端口17890、管理端口19090；显式使用代理执行 GitHub printf 的 `ls-remote HEAD` 成功、退出0。已在[速查第3节](../maintenance/E01/planning/server_reference_rebuild_guide.md#3-生成硬件和向量仿真清单)补充当前终端的代理设置与重试说明；未修改代理配置、未重跑构建，构建结果仍待用户反馈。

2026-10-18 用户手动实施增量（本地输入仍为 `2f0f2d6f…`）：用户已推进至重建速查第2节，报告 pip 20.2.4 安装后的 tclint 依赖冲突，并随后确认问题解决。[速查第2节](../maintenance/E01/planning/server_reference_rebuild_guide.md#2-准备工具环境)已记录现象、原因及启用 `--use-feature=2020-resolver` 后执行 `pip check` 的方案。未收到修复后完整输出/版本列表，Agent未远程复测；此前“重建尚未实施”仅保留为历史状态，不再代表用户当前进度，完整构建/仿真仍待验收。本轮仅更新两份E01文档，不代改共享状态。

2026-10-18 后续精简（同一输入HEAD）：用户明确“如无必要、勿增实体”。重建速查改用 Ara 官方 `update_vsim_src`，移除自定义 `run` 包装、手动依赖就绪标记和主流程中的扩展验收命令；日志/来源记录要求继续有效。VCS首次构建直接检验联编与许可，只有实际错误需隔离时再补小探针，替代旧方案中的强制前置探针。仅修改文档；上一版未提交速查备份于 `/tmp/e01-guide-before-simplify-kggmid1p/server_reference_rebuild_guide.md`。

2026-10-18 文档增量（输入仍为 `2f0f2d6f…`）：按用户要求交付[同版本重建速查](../maintenance/E01/planning/server_reference_rebuild_guide.md)，包含官方网页/固定源码依据、获取依赖、环境、硬件生成、VCS及软件/启动命令。只做来源与命令静态检查，未执行服务器重建。当前网页与旧版 Python 配方不同；原向量示例 `printf("%s", str_v)` 存在参数问题，正式RVV测试仍待准备。此前核对26个依赖HEAD均匹配原锁文件，不代表各依赖工作树无修改。共享状态不代改。

- 本轮用户最后要求：先规划，后续一步一步报告并由用户确认执行。不能按同条消息前面的连续实施授权跳过确认。
- 路径：服务器 `~/CheshireAraPULP` 为官方结构参考工程，`~/CheshireAra` 为 `cheshire_ara_asic` 提取工程；阶段0时均为空，第1步仅在前者新增 `_e01/preflight/`，后者仍为空。
- 保护：本地原 RTL/sw/FPGA、`.bender`、服务器 TTY 工程 `/home/zhaowy24/Desktop/mycheshire_24` 均未修改；`/opt`未修改。仅创建小型工具链探针与输出。
- 当前状态：参考工程已重建，标量HelloWorld及修正FS后的单个fmatmul向量运行通过；完整参考验收和固定工程提取仍未完成。原工具链S01-T01及FS Dirty状态跟踪原因未关闭。
- 最新来源决定：用户明确从GitHub重新获取当初clone的 `mp/ara-pulp-v2` 同版本，在服务器重新搭建环境和构建。按本地Git历史以 `e040b7bbc7851a37faff3c4657ff8d656cc6e20a` 及原锁文件为基准；不再重新评选官方版本。仍需核验官方可获取性，不能用当前分支尖端替代历史SHA。原快照复制方案仅留历史依据，比较与澄清见[方案第8节](../maintenance/E01/planning/server_reference_extraction_plan.md#8-官方重新获取与本地快照复现的比较来源调整)。

## 交付与证据

- [服务器参考工程使用与仿真上手指南](../software/SERVER_SIMULATION_GUIDE.md)：工程结构、配置阶段、仿真输入输出、fmatmul教学副本、有限窗口FSDB与VNC/Verdi操作；静态核对与待实测项分开记录。
- [实施方案](../maintenance/E01/planning/server_reference_extraction_plan.md)：输入版本、TTY 映射、工具链、官方入口、固定配置、测试判据、六步确认点。
- [只读检查摘要](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/findings.json)与[最后一组远端只读命令](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/remote_detail_check.py)、[脱敏输出](../maintenance/E01/reports/evidence/server_readonly_2026-10-18/remote_detail_check.txt)。不保存许可证环境、凭据或主机授权标识。
- 本轮新增上述 E01 文件，无 Git 提交。已有 PROJECT_STATE、AGENT_TASKS、handoffs/README 存在其他修改，本轮不代为合并。

阶段0历史结果（当时均为只读查询/源码确认；第1步实际检查增量见下）：

1. TTY 是标量 WB profile，308 个源码条目/12 个 include 均存在；配置 3 为 vCLIC，本地配置 3 为 Ara。其脚本写死另一主机路径，不能直接复制运行。
2. 服务器 RISC-V GCC 13.2.0、as/ld 2.43.1；默认 rv64gc/lp64d，单 multilib，libc/libgcc/向量头存在。首选待测，不是兼容验收通过。
3. 本机 C/C++ PATH 为 GCC/G++ 13.3.1；另有系统 GCC 8.5.0。VCS/DPI 与裸机交叉工具链独立核对。
4. `vcs -full64 -ID` 本轮退出 0，版本 `W-2024.09-SP1_Full64`；不表示许可证、编译、展开或运行通过。
5. 本地官方源码支持 VCS 入口；当前生成脚本却是标量配置并同时含 decoder stub/真实实现，须在新目录按向量入口重新受控导出。
6. 既定配置不变：`cv64a6_imafdcv_sv39` + Ara=1、2 lanes、VLEN=2048；完整 DefaultCfg、LLC/SPM/atomics/ROM/地址与外设保持。软件启动副本须在向量执行前开 VS，原 ROM 和生产源码不在本轮修改范围。
7. 当前 Ara README/RTL 走 RVV 1.0，但旧 DEPENDENCIES 提到 0.9；采用当前实现路线。默认 JTAG 流含改 dpc，另列 SPI raw 从复位启动项验收，不能用 HelloWorld/直接 ELF 加载代替。
8. 默认 Python 为 3.6.8，但已有 `/usr/bin/python3.9` 3.9.25（也有 3.11/3.12），可显式选择以满足官方 >=3.9 要求；依赖包尚未验证，无需因默认版本较旧直接升级系统。

本地文档检查：已有 9 个改动/未跟踪文档的 SHA256 与写入前一致；新增 Markdown 相对链接可解析，JSON 与证据脚本语法可读取（没有执行该脚本），方案/交接由两个只读复核角色检查。原始脱敏输出保留了行尾空格，不将日志格式告警当作功能验证失败或运行通过。

## 第 1 步实际结果

- [工具链检查报告](../maintenance/E01/reports/toolchain_preflight.md)、[原始输入及证据](../maintenance/E01/reports/evidence/preflight_2026-10-18/)；服务器证据根为 `~/CheshireAraPULP/_e01/preflight/`。
- run_001：45条命令，2项链接失败，脚本退出1；run_002：29条命令均退出0，隔离结果不关闭原失败。另有3条工具路径查询。全部串行、单条60秒超时。
- 标量/RVV 1.0探针在SPM地址实编/实链通过，实际拉入memcpy和libgcc 128-bit除法；ELF/ABI/反汇编核对通过。原版crt0汇编、SPM LTO链接通过；本机C++小程序运行通过，原样elfloader使用VCS头文件编译通过（22条告警）。
- **S01-T01未关闭**：`libgcc.a(_divdi3.o)`经`__udivmodti4`绝对引用`__clz_tab`，在`0x80000000`产生`R_RISCV_HI20`溢出；应用medany不改变已编好的库。去掉128-bit除法的libc-only隔离程序用原版链接脚本在SPM/DRAM均可链接，故不泛化为整个工具链不可用。
- 建议先用既定SPM布局验证向量与DDR模型访存；如实际DRAM驻留程序需要该库成员，再提同源同版本medany运行库的独立目录方案，未升级或修复`/opt`。
- 16个传输输入、本地取回183个产物/日志的SHA256核对通过；TTY先前抽查的7个文件hash未变。首次传输发现未来mtime，后续复制需避免make时间误判。
- 没有运行RISC-V程序、VCS或许可证检查；完整libcheshire、Boot ROM/LLC/RVV目标验收仍未完成。第1步运行的是新增探针，不是重新验证SoC。

## 按需配置再精简检查（2026-10-19）

- 只修改指南与本交接；输入HEAD为`2f0f2d6f85979709fbc99dd4098447cb5587ce5f`。第0节配置块恰好四项，波形设置只在第7章；沿用官方脚本与已配置工具环境，无新增仓库脚本或自动记录机制。
- 正文12个Bash块及从官方脚本生成的普通/波形两份临时示例均通过`bash -n`。用临时假命令检查普通运行、波形选项、展开失败停止、运行错误传播、展开日志写入失败停止，共5种场景；不调用VCS，不验证PLI、FSDB或GUI。链接/锚点、围栏、空白及`git diff --check`通过。
- 两份输入备份、增量差异、检查程序及结果在`/tmp/e01-minimal-guide-s0y0380n/`；范围外209个文件哈希不变（含本地官方启动脚本）。未修改服务器、RTL、软件、依赖或共享状态，未提交Git。此前真实运行证据保持，波形流程仍待用户目标实测。

## 官方入口精简检查（2026-10-19）

以下为上一版方案的历史检查；当前操作以按需配置再精简为准。

- 负责文件仅为`software/SERVER_SIMULATION_GUIDE.md`和本交接（相对`docs_codex/`）。对照当前本地`target/sim/vcs/start.cheshire_soc.sh`及官方`docs/tg/sim.md`，沿用2026-10-18服务器固定版本/安装路径证据；本轮没有新的服务器连接或工具核查。未将本地标量生成清单用作服务器向量输入。
- 从指南提取三段修改，应用到临时官方脚本副本：完整脚本及正文11个Bash块均通过`bash -n`。临时假命令检查8种情况：波形开启/关闭、展开失败、运行失败、展开日志写入失败、运行日志写入失败、缺少wave.tcl、无效波形开关；确认开关参数、失败停止和运行状态传播。没有调用EDA工具，假命令不验证VCS参数语义、PLI或FSDB有效性。
- 两文档相对链接/锚点、代码围栏和行尾空白检查通过，`git diff --check`通过；既有范围外209个文件的SHA256保持不变，其中包含本地原启动脚本。输入备份、提取的临时脚本、检查程序、模拟输出及`validation.json`在`/tmp/e01-official-entry-d4nifvkx/`。未新增仓库脚本、修改共享状态/RTL/软件/依赖或提交Git。
- 最小下一步：用户按指南先备份，再编辑服务器官方启动脚本和wave.tcl，逐步执行编译、展开、采集与Verdi查看；Agent据实际输出更新结论。已有单例fmatmul成功不扩大为新调试流程或完整向量验收成功。

## 文件配置式流程检查（2026-10-19）

本节保留上一版五文件方案的检查证据；该方案已被官方入口精简替代，不作为当前操作要求。

- 从指南提取11个Bash代码块做`bash -n`；相对链接和新增页内锚点检查通过。在`/tmp/e01-script-doc-check-expsooxf/`使用模拟vcs/simv/verdi检查构建/运行目录拒绝覆盖、配置不匹配拒绝运行、旧运行使用其保存的数据库、编译/展开/运行错误码传播。Tcl通过空操作命令检查变量/语法组织；这些检查没有调用EDA，不证明UCLI/PLI/FSDB或GUI可用。
- 写入前两文档备份在`/tmp/e01-file-config-before-c9wd8eki/`；其他208个已有修改/未跟踪文件哈希保持不变。`git diff --check`通过。未在服务器创建文件或运行工具，未改RTL/依赖/共享状态；未提交Git。

## 配置导读检查（2026-10-19）

- 四份修改文件：`software/SERVER_SIMULATION_GUIDE.md`、`configuration/README.md`、`configuration/RECIPES.md`及本交接。未新建文档或脚本。写入前备份在`/tmp/e01-config-docs-before-x5fgtgno/`，其他205个已有修改/未跟踪文件的SHA256保持不变；共享状态保持原状。
- 静态核对15个DefaultCfg关键取值、TB Ara函数的3项显式赋值及fixture传入VIP的参数集合；复算LLC=131072 B、AXI输入数7、下游ID宽5/6 bit。CPU覆盖/派生、宏消费者和实例链路按源码阅读核对；不称为SV展开测试。
- 四文件相对链接、新增显式锚点、表格列数与代码围栏配对通过；指南11个Bash代码块逐段`bash -n`通过；`git diff --check`通过。未执行这些命令、未渲染GUI/波形或运行仿真。仅以历史报告引用fmatmul成功及FS兼容修正，FS Dirty原因和完整验收仍开放。

## 上手指南检查（2026-10-18）

- 正文11个Bash代码块分别通过`bash -n`；检查了正文、软件README和本交接的相对链接，以及正文显式锚点。新正文/交接无行尾空白，`git diff --check`通过。未执行文档中的构建/仿真命令；语法检查不等于命令在目标环境运行通过。
- SSH只读核对Cheshire/Ara提交、fmatmul及其辅助头文件、官方软件参数、crt0/链接脚本、VIP结束协议和CPU/Ara实例名。波形命令形式按服务器安装的FSDB/UCLI手册及VCS帮助核对，只记录命令接口与受控文档位置，不保存厂商手册正文。GUI打开、许可、PLI联编、FSDB有效性和真实波形解释仍待用户运行验证。
- 写入前备份软件README和已有未跟踪E01交接到`/tmp/e01-guide-before-n5jyr3ge/`；9个已有共享/其他主题修改文件哈希保持不变。未修改本地RTL/sw、依赖、服务器文件或TTY工程，未新增通用执行脚本，未提交Git。

## 最小下一步

当前（2026-10-21步骤2A完成）：等待用户明确授权[阶段2B](../maintenance/E01/planning/server_reference_extraction_plan.md#step2-plan)。参考基准包含已验证结果及限定告警/已知DMA限制，不要求先修完历史问题；尚未开始提取。

历史（fmatmul刚通过时，已由上述进展替代）：曾安排FS Dirty原因、VL/尾部、SPI自主启动、访存/原子和warning检查；后续实际检查及未关闭项见本页最新记录，不重复执行旧任务。

### 历史下一步（五步执行前，已被上段替代）

1. 按已明确的同版本方向，核实原官方 `mp/ara-pulp-v2` 提交 `e040b7bbc` / Ara `2895ba90` / CVA6 `99eac9a6` 的可获取性与锁文件，列服务器环境及本地差异处理。报告第2步具体动作，待确认后获取/重建；保留preflight，不触碰TTY或`/opt`。
2. 后续第3步才执行完整参考SoC编译/展开/目标运行，检查VS/FS和原启动路径；保留S01-T01运行库限制及所有既知缺陷。
3. C00可合并：E01第1步完成，已明确官方GitHub同版本 `mp/ara-pulp-v2` 重建，具体第2步执行待确认；S01工具链部分编译/链接证据已取得，S01-T01开放；V01仍无目标仿真证据。共享文件本轮未代改。

后续只需读本交接、实施方案与 [02 规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)，再核对当前工作区和服务器目标是否变化。

## 资源问答文档检查（2026-10-19）

- 负责文件：`engineering/Fixed_Vector_SoC_Resource_Guide.md`、`engineering/README.md`、本交接，路径均相对 `docs_codex/`。原有两个文件只追加内容，已有记录保持；未修改共享状态和原封装预算。
- 静态复核：实际选择 `sram_pulp.sv`、SRAM 数据/标签形状、TLB/预测器与 CSR 字段、ROM 实例/链接/解码口径、Cache/VRF 扩容关系。独立审阅纠正“增路数改变每 way 粒度”的不准确表述，并将源码索引中的性能计数器及 Ara CSR 符号改为实际声明；未扩大到工程缺陷修复。
- 文档检查：三份文档的 123 个本地链接及 Markdown 锚点、19 张表的列数、代码围栏及空白检查通过；60 项容量/位宽/地址和扩容算例复算通过。原有 206 个修改/未跟踪文件中，除本轮授权追加的两份文件，其余 204 个文件哈希保持不变；唯一新增文件为资源正文，HEAD 未变。
- 可复查命令（仓库根）：`python3 /tmp/e01-resource-guide-_r7jjgc6/validate.py`、`git diff --check`。检查脚本、`validation.json`、输入备份及增量差异位于同一临时目录；临时 HTML 仅用于 Markdown 结构解析，不是仿真/性能证据。脚本与空白检查退出 0，未执行构建、仿真、综合、宏映射或新的服务器核查，未提交 Git。
- 当前结论和下一步：资源文档已交付；硬件固定配置及既有验收状态保持。后续如需扩容或选工艺宏，按正文 Q7 的参数联动和定向验证要求另立变更输入，不把候选配置当成已确认配置。

## 参数开放策略文档检查（2026-10-19）

- 输入：`mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`＋写入前已有未提交内容。负责文件仅为 `02_Cheshire_Ara_ASIC_Extraction_Handoff.md`、`engineering/Fixed_Vector_SoC_Resource_Guide.md`、`maintenance/E01/planning/server_reference_extraction_plan.md` 和本交接，路径均相对 `docs_codex/`。未新增专题或实现文件。
- 同步结果：固定向量功能组合，采用 `src/config/`，每次构建锁定配置；基线提取对照通过后先试 L1 容量/LLC 行数，再按瓶颈逐步开放。基线、候选、完整验收分开记录，源码闭包覆盖声明支持范围。应用比较区分目标周期与主机耗时、内核与完整任务，明确 LLC 全 SPM 启动条件；物理实现比较纳入宏、时序、功耗和 Pad 约束。具体候选值和最终产品配置仍待评估。
- 交叉审阅：核对四文档的来源/目标、配置入口、阶段顺序和证据边界；修正服务器方案两处旧表述，保留并溯源已有 FS=Clean 兼容修正，将最小 SV/DPI 探针统一为按需诊断。S01-T01、FS Dirty 原因及完整参考/提取验收仍未关闭。
- 静态检查：134 个本地链接（其中 28 个带 Markdown 锚点）、34 张表、14 个代码块的结构检查通过；旧锚点保留。资源 Q1—Q6、原有 83 行含数值表格、两份基线表和无关架构契约保持；47 项原容量/位宽及扩容算例复算通过。原交接仅插入内容，206 个范围外已有修改/未跟踪文件 SHA256 不变，HEAD 未变。
- 可复查命令（仓库根）：`python3 /tmp/e01-parameter-policy-uqiuf7qd/validate.py`、`git diff --check`，退出均为 0。输入备份、保护哈希、四文件增量差异及 `validation.json` 在同一临时目录。本次检查仅支持“文档同步完成”，未创建 RTL 配置目录，未运行构建、仿真、综合或服务器操作，未提交 Git。

共享状态合并建议（交 C00 汇总，本次未修改共享文件）：

- `PROJECT_STATE.md`：记录 2026-10-19 用户确认“固定 CVA6＋Ara 功能组合、集中可调参数、按构建锁定配置”；首次提取基线保持，后续以应用正确性/性能及面积、时序、功耗选择产品配置，替代长期只允许一个参数配置的旧限制。
- `AGENT_TASKS.md`：E01 参数策略文档同步完成；工程提取和参数试验未实施。最小下一步仍是按用户分步确认补齐参考验收，再提取并验证独立性，之后才开展受控参数试验；不把本次文档交付记为 E01 工程验收完成。


## 仿真测试平台结构与验证流程图稿（2026-10-19）

- **范围与输入：**本轮为 E01 参考工程的教学图稿子任务，输入 HEAD `c9abbb48946fe3a7244bfb3159919b7c9731cb59`；进入时本交接与 `software/SERVER_SIMULATION_GUIDE.md` 已有未提交修改。保留原内容，不修改 RTL、软件、官方 compile/start、配置及共享状态/任务表。
- **交付：**[两版图稿及共用说明](../diagrams/2026-10-19_simulation_testbench/README.md)。工业版和教学版各一张 16:9，包含原生 PPTX、SVG、PNG；真实接口连续连接，软件步骤单独标识。说明集中列出源码位置与版本差异，不在本交接重复正文。
- **源码确认：**DPI→VIP Serial Link→AXI→SPM；ROM 初始化并等待入口/启动标志；CPU/Ara 执行，CPU 内的软件计算参考 G 并比较 C；UART 自检文本、VIP 的 SLINK 状态、TB finish 与主机退出码分开。本地生成清单仍为非向量 CPU profile，本地 start 未写入指南四项配置，现有本地 ELF 与服务器交接 ELF 哈希不同，不能据 SELCFG=3 推断完整向量配置或新验证通过。
- **图稿检查：**skill 原生后端导出；python-pptx/ZIP XML 重读，各版 153 个原生对象、94 个文本、30 条完整箭头、16 个虚线对象、零整图图片；临时副本的文本/图形/线属性修改保存重读通过。Chrome/CDP 对最终 SVG 及从最终 PPTX DrawingML 重建的预览检查文字与线条；整页和关键局部已实际查看，两版对象/边语义一致。证据见图稿目录 `checks/validation.json`；Office 显示/编辑未实测。
- **检查命令与保护：**任务临时生成、导出、结构检查及本地预览命令位于 `/tmp/simulation-testbench-art/`；复用已安装 skill 的 `scripts/run.py` 和仓库现有 DrawingML/CDP 预览实现，未新增工程运行框架。输入交接备份为该目录 `handoff.before.md`；指南 SHA256 与输入一致；本交接只插入一条修改记录并追加本节。`git diff --check` 通过，未提交 Git。
- **证据边界与下一步：**只完成源码核对和图稿文件检查，未构建、仿真、连接服务器或板测。既有普通 fmatmul 成功和波形短测保持为历史记录；当前服务器配置、完整波形运行、主机退出状态及全部断言覆盖没有新增证据。下一位仅需按使用场景选图；如需真实运行验收，另按现有指南取得当次证据。无需更改 E01/V01 工程实施状态，也不改变 RTL 模块指南的 A 版决定。

- **汇报插图精简修订（同日）：**用户选择工业风用于汇报页，新增 `industrial_compact.svg/.pptx/.png`，1200×1010 画布；原工业/教学完整版保留。保留加载、CPU/Ara 访存、软件比较和 UART/SLINK 结果主线，细节沿用共用说明。输入 HEAD 未变；59 个原生对象的保存重读与临时副本属性编辑通过，最终 PPTX 整页及局部预览已查看，检查见图稿目录 `checks/compact-validation.json`。Office 未实测，未构建/仿真/连接服务器；本次选择不改变 RTL 模块指南 A 版决定。修订前交接备份为 `/tmp/simulation-testbench-art/handoff.before-compact.md`。

- **第 1 版纵向修订（同日）：**用户认为极简版不能充分说明结构与流程，改以第 1 版 `industrial.svg` 单页为输入，新增 `industrial_portrait.svg/.pptx/.png`（1500×1870）。保留 TB/fixture/VIP/DUT、加载与执行、自检、结果及波形支路，只合并内部日志框和检查说明框；原完整版及极简版保留。输入 HEAD 未变，现有文件内容追加保护。原生对象 141 个、文本 86 个、完整箭头 28 条，保存重读/临时副本编辑通过；已实际查看最终 PPTX 整页及连线/结果局部，检查见 `checks/portrait-validation.json`。Office 未实测，未修改工程代码、运行构建/仿真或连接服务器。修订前交接备份：`/tmp/simulation-testbench-art/handoff.before-portrait.md`；详细说明共用图稿 README。
