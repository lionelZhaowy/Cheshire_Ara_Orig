# 项目共享状态

2026-10-26 E01 [剩余工作区按用户授权发布](handoffs/E01_fixed_vector_extraction.md#workspace-publish-20261026)：R两处原诊断文件已单独提交并推送`29f1e6f9`，远端读回一致，受管工作区干净；本地原17修改/4新增纳入本次提交，目标为个人`Cheshire_Ara_Orig/main`。未改功能源码或重跑仿真，F保持；下方“诊断/本地未提交”为此前快照。

2026-10-26 E01 [LLVM默认编译器迁移已完成](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-resume-20261026)：先R38新ELF/40项主矩阵及两探针，再F49新ELF/51项独立运行；正常PASS为36/47，另各SPI限定告警1、保留LLC未完成1及预期负例2。混合465/0＋22字节0错、P7 68组/13416项和P6 508组/38452项0错，F Ara11目标59case/147比较0错。当前目标软件默认LLVM20.1.0/newlib/compiler-rt，无目标GCC/libgcc依赖；宿主g++保留，输出`sw/build/llvm_p7`。原件/after两地实际恢复及结果包核对通过，未改RTL/参数/Boot ROM；随后R八文件已提交并推送[`6f2b2a3b`](https://github.com/lionelZhaowy/CheshireAraPULP/commit/6f2b2a3be50eeb15eb93c0ada2164029a102c94c)，远端main读回一致。R两份原诊断修改及本地17修改/4未跟踪保留，未混推；详见[发布与剩余内容](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-github-push-20261026)。旧GCC/输出保留。下方“GCC默认/迁移停止”为历史。

2026-10-26 E01 [P7已同步正式工程并验证，参考工程已提交GitHub](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-reference-formal-sync-20261026)：F自身重建RTL及14 ELF后，17次串行仿真全部PASS；P7共68组/13416项0错，归档原LLVM向量及两标量均未重编即465/0、复制22字节0错，12回归通过。F保留既有布局，维护目标29→31，日常7/Ara11保持；其余1046原输入及R全部4394输入内容/权限保持。随后仅R四份P7源码提交并推送`4e30feec`，两处诊断修改保留；两地前后恢复/归档核对完成。默认仍GCC13.2，LLVM构建规则尚未重新适配、迁移验收未完成；未综合/板测/公开上游PR。下方仅R、未提交及F未同步均为前阶段历史。

2026-10-26 E01 [P7仅R修复并验证通过](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-emul-local-fix-20261025)：dispatcher＋VALU共32增4删，复用已有状态/队列；68组/13416项0错，原LLVM失败ELF未重编即465/0及复制22字节0错，两标量和12回归全PASS。22次实际运行保留旧版/中间失败，4318其他原输入及两处诊断修改保持，双份备份/实际恢复检查通过。R未提交修复保留，F未同步、LLVM迁移未恢复，未综合/发布。下方候选回退为前轮历史。

2026-10-25 E01 [P7候选未通过、R已回退](maintenance/E01/reports/official_pr_failure_fixes_review.md#p7-implementation-result-20261025)：#483固定7增1删编译成功，初版两次诊断存在不支持的非零vstart算术X/断言，候选第51组VMACC m2另有数据错；实际OPMVV默认EMUL=1的重排/EEW链及字节模型匹配首错，未扩改。用户批准替换两组，修订ELF构建后未运行，17项修订验收/原LLVM/回归均未执行。R 4321项原输入/HEAD/原Git差异实际恢复，新C及失败材料双份保留；F未写、LLVM迁移未恢复、无提交推送。下方“尚未实施RTL修复”为此前阶段。

2026-10-25 E01 [LLVM迁移及失败原因分析](maintenance/E01/planning/llvm_toolchain_migration_plan.md#llvm-vector-failure-analysis-20261025)：固定LLVM20.1.0工具链/阶段A通过，R36 ELF构建通过；新增自动向量化465项/256错，验收停止。GCC/LLVM同源标量及换目的寄存器对照均465/0，实际Ara布局模型匹配257/257输出，指向源重排条件缺口；尚未修改/验证RTL修复。LLD全局+D遗漏可消ABI告警但可装载内容保持。R六处源码已实际回退、原差异保持，F未写；迁移未完成，新输出/双份备份保留，无提交推送。下方“未确认新RTL缺陷”为此前静态核查范围，不能替代本轮动态结果。

2026-10-25 E01 [P6已上云并同步F验证](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-reference-formal-sync-20261025)：R六文件单独提交/推送`cb20a03c`，远端main读回一致、两处原诊断修改保留；F按目录映射同步，维护目标24→29、日常7/Ara11保持。F自身重建后11次仿真全PASS，P6共508组/38452项0错，P2三项及vector/RVV/fmatmul通过；F其余1043输入保持，两地前后恢复/归档核对完成。未为F初始化Git、提交/推送或做综合/板测；下方“仅R/未提交/F未同步”为此前阶段。

2026-10-25 E01 [P6已在R实施并验证](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-fix-20261025)：3RTL采用#475/#480局部并修正MASKU数据归属、compress完整结束，新增2C及显式Make组。17次仿真16 PASS＋1预期旧版停滞；生产路径8次全PASS，5个P6目标508组/38452项0错。其余4298跟踪输入及原修改保持，两地备份/恢复校验完成。R仍为5986ba02上的未提交修改，F未同步、未推送；#479不纳入，无综合/板测。下方候选及未修复描述为此前阶段记录。

2026-10-25 E01 [P6候选检查完成](maintenance/E01/reports/official_pr_failure_fixes_review.md#p6-candidate-check-20261025)：R独立副本21次仿真，#475消除VL1死锁、#469部分选择7800/0、#480消除原VL4重复请求；组合仍有历史数据归属错误及compress全不选/VL130停滞。既有P2回归483/0；提出本地修改方案，P6未完成修复。#479暂不继续处理；R/F生产源码、HEAD和原修改保持，未综合或发布，源码/证据已两地校验。

2026-10-25 E01 [Ara MaskB定向测试完成](maintenance/E01/reports/official_pr_failure_fixes_review.md#ara-maskb-tests-20261025)：仅R `5986ba02` 新增测试，#475三种序列复现；#479两组各120次/8056检查通过但冲突接收窗口为0，未排除缺陷。另复现#450相符的compress终止停滞，保留延迟提取错误值待定位；既有P2标量483项再通过。4302跟踪文件/HEAD/原Git状态保持，两地证据已校验；未修RTL、改F、综合或发布。

2026-10-25 E01 [ABC正式源码核查完成](handoffs/E01_fixed_vector_extraction.md#abc-review-20261025)：本地资源/配置、SRAM适配、P2/P3评审三份既有文档更新并配两图；71份服务器输入结束哈希保持。配置基线/48逻辑SRAM数量不变，未确认新RTL缺陷；明确P3当前向量测试VL4，非整拍VL1/3异常屏蔽仍缺动态覆盖。复核F五项历史结果，未新运行、修改服务器或启动宏替换/综合。


2026-10-25 E01 [第3轮provenance归类完成](maintenance/E01/planning/server_reference_extraction_plan.md#provenance-organization-plan-20261025)：35份历史记录移入history，顶层43→8、总数217保持；只更新两份导航及其来源条目。文件内容/权限、986活动哈希、1010其他输入和双份备份/实际恢复检查通过。未构建、仿真、清理产物或修改参考工程，三轮授权工作完成；下方“第3轮未开展”为历史进度。

2026-10-25 E01 [第2轮特殊测试整理完成](maintenance/E01/planning/server_reference_extraction_plan.md#special-tests-organization-plan-20261025)：F已移动7个P1–P5 C和2个P4 ld，默认all改为7项、其余24项显式regressions，Ara目标保持。32项ELF前后可装载内容/布局一致，7次代表性运行PASS；源码/入口及历史证据保护、两地备份/恢复核对完成。保留后续ELF/TARGET文档更新，回退须合并对应文档/来源条目；未改R或RTL，第3轮provenance整理未开展。下方默认all保持为上一轮历史状态。

2026-10-25 E01 [Ara首批测试迁移已完成](maintenance/E01/planning/server_reference_extraction_plan.md#ara-tests-migration-plan-20261025)：正式`~/CheshireAra`新增11个官方C测试/4头文件及显式构建目标，59个case/147组比较通过；18次验收为17 PASS及1预期负例，既有RVV/P2/P3/fmatmul结果与此前一致。两地备份与实际恢复检查完成，保留并发排版记录；生产RTL及默认all保持。未修改参考工程或推送，特殊用例归档/provenance整理仍留后续轮次。

2026-10-24 E01同步复验完成：R已合入P1–P5，48次验证后推送GitHub `5986ba02`；随后F按映射同步并独立重建31ELF/四种仿真目标，41次运行（38 PASS、ROM/SPI原限定告警1、预期负例2），39项与R一致。R4390文件、F修改前17/修改后27文件恢复匹配，两地源码/证据备份已校验；原配置/wrapper/静态入口及FS/libgcc/LLC限制保持。见[版本、结果与回退](maintenance/E01/planning/official_upstream_maintenance_assessment.md#reference-formal-sync-20261024)。本轮完成停止；下方未同步/未授权描述为历史。

2026-10-23 E01 云端基线同步成功：经用户新授权的SSH deploy key，已将R基线main及`rebuild-baseline-20261023`原子推送到`lionelZhaowy/CheshireAraPULP`；重新读取云端main/标签解引用，均为`424e4d2cd9f7e129bbda7e595504a48952b150e9`。R工作区干净并跟踪personal/main；未合入P1–P5、未构建、C/F不变。连接器新仓库权限仍不可用，不影响SSH；Actions设置未独立读取。见[同步证据与后续顺序](maintenance/E01/planning/server_reference_rebuild_guide.md#github-cloud-baseline-20261023)。下方“待仓库/密钥授权”属于历史记录。

2026-10-23 E01 GitHub托管准备完成：用户选择`lionelZhaowy/CheshireAraPULP`私有仓库，并授权基线上云后分项同步P1–P5到R。R保留官方历史，个人`main`基线`424e4d2c…`/标签`rebuild-baseline-20261023`已保存实际依赖及既有修正；4,358文件从bundle恢复匹配，双份bundle校验通过。仅版本配置/文档改变，生产源及C/F未改；未push、未合入P1–P5、未构建。待用户新建空私有仓库、停用继承CI并授权专用deploy key，见[当前步骤](maintenance/E01/planning/server_reference_rebuild_guide.md#github-personal-baseline-20261023)。受限EEPROM模型不上传、原件保留；原ROM/FS/libgcc/LLC限制保持。以下为历史记录。

2026-10-23 E01：隔离C的P3残留SIMD标志、P4相邻段覆盖及P5一维搬运已定位修复，逐项验证和累计回归完成。累计7次新运行中6 PASS、ROM/SPI按原padding限定告警接受；同版本3项DMA回归已通过。最终`p1-p5-pass=5e0f973…`及双份源码/证据备份校验完成，R根/26依赖/1084输入、F962目标均保持，未写回R/F。阶段B完成停止，阶段C仍待授权；见[实测与回退](maintenance/E01/planning/official_upstream_maintenance_assessment.md#p3-p5-repair-20261023)、[交接](handoffs/E01_fixed_vector_extraction.md#p3-p5-repair-20261023)。原ROM/FS/libgcc/LLC限制保持；下方为历史记录。

2026-10-23 E01 P2定位修复完成：只在隔离C修复16项mask尾位计数和15项标量提前回应，同一ELF835/31→15→0，124/483补充检查及RVV/fmatmul/向量/非stub CSR/P1五项回归通过。`p2-pass`=`7ac2e12…`，服务器/本地累计bundle与关键证据已校验；R/F保护核对全匹配，未同步。P3–P5及全组累计回归未执行，本轮停止；阶段C仍需单独授权。见[原因、实测与恢复](maintenance/E01/planning/official_upstream_maintenance_assessment.md#p2-repair-20261023)、[交接](handoffs/E01_fixed_vector_extraction.md#p2-repair-20261023)。以下停止及阶段A条目保留为历史记录。

2026-10-23 E01局部维护阶段B历史停止记录：仅隔离候选实施，P1完成定向及向量/RVV回归；P2错绑观察消失但835项仍31失败，按计划停止，P3–P5未实施。`p1-pass`/`p2-stopped`及服务器/本地备份保留，首次恢复1084文件匹配；R/F保护检查全匹配、未同步正式工程。见[实测与回退](maintenance/E01/planning/official_upstream_maintenance_assessment.md#p1-p5-stage-b-stop-20261023)及[交接](handoffs/E01_fixed_vector_extraction.md#p1-p5-stage-b-stop-20261023)。后续定位P2或同步P1需另行明确；下方此前各轮“未构建/等待B授权”不代表当前隔离候选状态。

2026-10-23 E01开发基线比较完成：[评估结论](maintenance/E01/planning/official_upstream_maintenance_assessment.md#main-baseline-decision-20261023)建议现在选A，保留正式F实际修正；不是已接受的迁移决定。官方main为`6c6dd5e…`，仍无Ara，但锁定CPU `4c02b24…`的专用接口支持作为后续集成候选；main只覆盖部分修复，Ara/MVP及iDMA已回移项仍需维护。现场确认Rocky8.10/VCS2024.09-SP1；隔离Git合并试验11/14文件冲突，未构建/仿真或迁移、未改生产源码。详见[本轮交接](handoffs/E01_fixed_vector_extraction.md#main-baseline-decision-20261023)；以下阶段A记录保留。

2026-10-23 E01官方维护评估阶段A完成：两工程只读核查，26依赖HEAD/差异与来源记录一致、962条活动目标哈希匹配；[评估与计划](maintenance/E01/planning/official_upstream_maintenance_assessment.md)区分局部正确性修复、性能及架构/工具变化，明确FS、浮点标志和SLINK后续风险。未改服务器源码/依赖，未构建或运行；工程版本及已知限制保持。**停止等待用户选择候选和阶段B授权**，见[交接](handoffs/E01_fixed_vector_extraction.md#upstream-maintenance-stage-a-20261023)。

2026-10-22 E01配置入口合并完成：正式工程取消独立cfg包，`cheshire_pkg`统一提供有效配置及类型；仅`DefaultCfg.Ara`默认0→1，原有效值1保持。soc/slink_rx新目录重建及14次前后对照完成（12 PASS、2次SPI限定告警入口2），完整配置、30项位宽、CPU trace及相关告警一致；旧输出和软件保持。默认值/恢复备忘见[第7.12节](maintenance/E01/planning/server_reference_extraction_plan.md#config-entry-merge-defaults-20261022)，详细范围见[交接](handoffs/E01_fixed_vector_extraction.md#config-entry-merge-defaults-20261022)。本轮完成后停止；下方独立配置包描述为历史记录。

2026-10-22 E01入口简化完成：用户明确实施后，正式工程恢复Bash compile/start，Python仅解析结果；软件单独Make，默认输出复用并打印WARNING，替代原run.py及强制新目录规则。四种top及10次代表性仿真分类符合预期（7 PASS、SPI限定告警入口2、负例1/124），Make依赖和文档/范围检查通过；新产物保留，默认HelloWorld为PASS。RTL/配置/软件源和历史归档未改，LLC旧限制保持；见[结果](maintenance/E01/planning/server_reference_extraction_plan.md#entry-scripts-result-20261022)及[交接](handoffs/E01_fixed_vector_extraction.md#entry-scripts-result-20261022)。本轮完成后停止。下方清理/旧入口记录为历史快照。

2026-10-22 LVDS 最小改图：用户取消右扩展布局及外部强制切入，重新从原单页 v1 增加 RX 解码/CDC 后到 TX FIFO 前的像素直通线和 2:1 MUX，由 C5 所属 LVDS TX 内配置寄存器选源。已更新[既有目录 PPT/预览](diagrams/2026-10-22_soc_lvds_bypass/README.md)及[设计说明](engineering/LVDS_Raw_Bypass_Design.md)，画布保持 3600×2025，正常 DDR/ROI 通路保留。切换需要 CPU/配置访问可用；DDR 反压隔离、图像域初始化、CDC/缓冲及全帧吞吐仍须实现验证。仅交付图稿和文档，未改 RTL 或执行硬件测试；见[主题交接](handoffs/L01_lvds_isp_gb_soc_topology.md#lvds-minimal-v1-20261022)。E01 状态与授权保持。

2026-10-22 E01验证后清理完成：仅保留`~/CheshireAra`作为正式工作区，旧输出/缓存及搬迁副本已删除；2033份必要验收证据压缩保存至`~/CheshireAra_validation_archive_20261022/`，逐文件验证通过，净释放约3.44 GiB。源码/入口保持，下一次使用须重编；下方历史产物路径按归档内原目录名前缀定位。见[清理结果](maintenance/E01/planning/server_reference_extraction_plan.md#post-validation-cleanup-20261022)。

2026-10-22 E01步骤2D完成：在 `~/CheshireAra_relocated_2d_20261022` 从新输出重建四种硬件、软件和镜像，31项对照为25项PASS、1项SPI限定告警功能接受、2项负例判定正确、3项LLC旧失败保持。实际访问无Bender/依赖下载、旧工程源码或缓存参与，参考输入和原产物保护检查通过。工程仍在 `~/CheshireAra`，保留run.py；服务器正常联网及VCS现有许可通信无需确认。见[结果](maintenance/E01/planning/server_reference_extraction_plan.md#step2d-result-20261022)及[交接](handoffs/E01_fixed_vector_extraction.md#step2d-result-20261022)。**本阶段完成并停止，后续功能/参数/工艺工作另行授权。** 以下为此前记录。

2026-10-22 E01步骤2C完成：`~/CheshireAra`内重建23单元库、17ELF和SPI镜像，19次新软件串行对照按既定判据完成；原ROM限定告警、3项LLC失败保留，参考输入和2B硬件/产物不变。见[结果](maintenance/E01/planning/server_reference_extraction_plan.md#step2c-result-20261022)及[交接](handoffs/E01_fixed_vector_extraction.md#step2c-result-20261022)。**停止等待2D授权**，搬迁及实际文件访问验证未做。以下为此前记录。

2026-10-21 E01步骤2B完成：服务器`~/CheshireAra`已提取硬件/最小仿真配套并从新输出重建，无Bender调用；31次同ELF/镜像对照按既定判据完成，原ROM限定告警和3项LLC失败保留，参考保护输入/产物不变。见[结果](maintenance/E01/planning/server_reference_extraction_plan.md#step2b-result-20261021)及[交接](handoffs/E01_fixed_vector_extraction.md#step2b-result-20261021)。软件仍复用参考产物，2D搬迁验证未做；**停止等待2C授权**。以下为此前记录。

2026-10-21 E01步骤2A：用户确认步骤1现有结果及保留限制可作为提取对照基准；本地WSL SSH已完成只读核查并交付[2A–2D计划](maintenance/E01/planning/server_reference_extraction_plan.md#step2-plan)。服务器`e040b7bbc`及实际修正保持，26依赖HEAD与锁一致；成功清单66组/716源/18include可复用，无需预设再次Bender导出；`~/CheshireAra`存在且为空。用户补充允许本地子Agent协助核查，主Agent统一写文档，不委派服务器Agent。本轮未复制、构建、仿真或写服务器；**停止并等待2B授权**。ROM限定告警、DMA共享LLC失败及其他未关闭项保留，见[交接](handoffs/E01_fixed_vector_extraction.md#step2a-plan-20261021)。以下为此前记录。

2026-10-21 剩余参考验收：本地 WSL SSH 已完成四类检查。非 stub CSR、RVV 5976 项和 SPM／DDR 模型访存原子 572 项通过；原 ROM/SPI 自主运行 HelloWorld，48 KiB 搬运 trace 与镜像一致，原 ROM 结构体 padding 含 X 的四条断言已定位且未影响本次功能；用户于同日确认忽略，接受 ROM/SPI 功能验收，不再列为阻塞，原日志保留。测试入口实测正常0、目标失败1、断言2、故意超时124；339 项生产输入、根 diff、simv 不变。见[结果与退出状态](maintenance/E01/reports/reference_rebuild_check.md#remaining-acceptance-20261021)。本轮检查结束，ROM 告警按上述限定范围豁免；DMA 共享 LLC 限制及暂缓修复决定保持，未开始提取或新集成。以下为此前记录。

2026-10-21 Serial Link 接收验证：经现有 LLC 写 DDR 的 64 KiB、CPU 并发 192 KiB、非对齐间断 8193 B 三项通过，刷新后 DDR 数据及保护区正确。共享 LLC 本身不等于死锁；此前 DMA 的循环依赖不能直接套用到外部供数的 RX。每次一个 RX 写突发，未验证多在途反压及同缓冲区缓存交接。339 项生产输入及根 diff 保持，见[结果与范围](maintenance/E01/reports/reference_rebuild_check.md#slink-rx-llc-ddr-20261021)。

2026-10-21 最新应用通路测试：用户决定暂不继续投入 SPM 内部 DMA 死锁修复。独立源/目的模型（绕过 LLC）在默认 256/限制 64 拍和三种延迟下均通过；当前 SoC 共享 LLC 十组 4 通过/6 停滞，DDR 旁路两组通过。仅切成 LLC 模式不足以避开问题；继续按既定设备绕 LLC、DDR 与 GB 独立端口方案推进。实际 GB/eMMC、DDR 前端及缓存维护尚未集成验收。生产 RTL/HAL/参数不变，见[本次范围与结果](maintenance/E01/reports/reference_rebuild_check.md#dma-cross-memory-20261021)。以下为历史记录。

2026-10-21 最新 DMA 复查：使用 #80/#204 后正式路径 simv 和 14 个原 ELF，7 通过、7 停滞，与回移前一致；默认读挡写、AW 解耦写挡读及 Bloom 行锁循环仍在。三变量全 32 B 倍数仍有反例，24 B/123 B 行长有具体通过组合，尚无通用倍数规则。见[完整参数表与结论](maintenance/E01/reports/reference_rebuild_check.md#dma-llc-recheck-after-pr80-204)。本轮只运行及更新文档，339 项源码输入、根 diff、ELF/simv 保持；不继续处理 same_dst，不自动改 RTL/配置、移植 #227 或提取。以下为此前记录。

2026-10-21 最新 DMA 修复：服务器固定 iDMA 已局部回移 #80＋#204，配置（在途数 16）、LLC、HAL 和其他依赖保持。原版 #115 停滞与仅 #80 的 AW 反压错误在配套修复后通过；后端原平台 29/30，唯一失败是旧 TB 重叠漏判，测试副本修正后通过；6 项 SoC 回归及生产路径重建/HelloWorld 通过。未发现本次覆盖内新增功能错误，**不代表通用无死锁**；旧 LLC 失败组合本轮未复跑，官方开放 #227/#273 未移植。见[结果与边界](maintenance/E01/reports/reference_rebuild_check.md#dma-pr80-204-20261021)。本地 FPGA 未改，未提取、提交或发布 PR。以下为此前分析/测试快照。

2026-10-21 最新 DMA 源码推导：用户要求一次提交完整二维任务，CPU 逐块等待不作为正常方案。发现已有 CONF 可让 DMA 自动短突发；形成受限 SPM 流量下的容量条件 `DmaNumAxInFlight×最大突发拍数<=8`，如 n=2、最大32 B。这需改变一个现有硬件配置参数，**尚未修改或测试，CPU/Ara 并发 LLC 不在证明范围**；当前 n=16 没有由此得到通用软件规则。见[机制与前提](engineering/DMA_Control_Path_and_Fix.md#dma-bulk-short-burst)、[本轮核对范围](maintenance/E01/reports/reference_rebuild_check.md#dma-bulk-source-analysis-20261021)。本轮仅本地源码与文档，未 SSH、改 RTL/HAL 或运行；旧测试记录保留，通用修复、完整验收和提取未完成。以下为前次记录。

2026-10-20 最新原因复核：已核对新死锁的 42＋81 B 分段及写侧 `0xff` 所需/`0x0f` 有效掩码，确认“写等数据、后续写挡住所需读”，与原“读返回满、读挡写”方向不同。新增 8 组单变量对照中 7 组通过、14 行组复现；源起点通过组的请求顺序与掩码变化支持该解释，不能归纳为非对齐/不同步长必然失败。见[原反例与原因对照](maintenance/E01/reports/reference_rebuild_check.md#dma-cause-confirmation)。本轮仅测试副本与诊断，生产源码未改，通用死锁修复及提取仍未完成。以下为前次记录。

2026-10-20 最新 E01 结果：已回移官方 `4c2390f2` 的 DMA 按次配置接口，原对齐长搬运用 AW 解耦通过；10 个功能测试中 9 个目标返回 0，非对齐/不同步长用例仍死锁，**定向验收未全通过**。新采样确认“写等数据、后续写挡住所需源读”的反向循环。原单次 CVA6 断言仍保留并对应同一已定位事件。见[DMA 长度与布局测试](maintenance/E01/reports/reference_rebuild_check.md#dma-aw-config-20261020)、[结构图与缺陷判断](engineering/DMA_Control_Path_and_Fix.md#dma-aw-implementation)。服务器只改 HAL 与三个调用点，RTL/依赖/FS 保持；下一步需另定新失败组合的处理范围，未自动实施 LLC 修改或提取。以下为前次状态记录。

2026-10-20 最新 E01 进展：DMA 控制接口/HAL 局部修复及基本回归完成。继续排查已确认：默认长搬运因 LLC 共同流水线中的读请求阻挡写请求而死锁；AW 解耦副本的单次断言来自栈上未使用的 32 位含 X，实际 load 结果正确，并非该次 DMA 数据比较失败。官方 #219 仍未关闭；相关 iDMA PR 尚不能认定修复本例，CVA6 `e606cdfe` 的断言调整也未覆盖当前 WT 文件。见[信号链说明](engineering/DMA_Control_Path_and_Fix.md#dma-llc-deadlock)和[死锁原因与对照](maintenance/E01/reports/reference_rebuild_check.md#dma-stall-diagnosis-20261020)。**默认长搬运仍未修复，完整定向验收未通过。** 本轮复用既有 simv/ELF，仅新增诊断输出和文档；依赖、FS 修正、生产默认标志保持，未改本地 RTL/sw，未提取、提交或发布 PR。stub 继续勿用；目标仍为 `~/CheshireAra`，暂不委派服务器 Agent。下列为历史快照。

2026-10-20 协作约定同步（用户于 2026-10-19 确认）：Cheshire SoC 改造由本地 Agent 统筹、服务器 Agent 按明确任务自主实施；NPU 等独立子系统由用户/负责人直接与服务器 Agent 推进，到 SoC 集成时再交接。详见[根约定](../AGENTS.md#local-server-collaboration)、[最小任务格式](AGENT_TASKS.md#server-task-brief)和[E01 决策交接](handoffs/E01_fixed_vector_extraction.md#collaboration-decision)。此次仅落盘协作方式，未接受调整参考验收与提取顺序，未授权复跑、提取、改配置或清理；下列工程状态保留原快照口径，实际进度查主题最新交接。

更新：2026-10-18，记录用户已确认 SoC 架构 v1 功能基线、总纲及三人分工/条件排期文档交付，输入 `mp/ara-pulp-v2` / `09798c1ded457e423b927844f66faae87583a20c`；保留 2026-10-16 DDR–GB 更新及其余 2026-10-13 文档整理快照。原整理输入：`mp/ara-pulp-v2` / `5a1338e0a0bf115ddd54c19e0ae367ac2d541892`。这是当前事实与未验证项索引，不是测试报告或实施授权。新对话再核对实际 HEAD 和工作区；按[任务表](AGENT_TASKS.md)、[定位指南](AGENT_DOCUMENTATION_GUIDE.md)及对应主题交接接手。

2026-10-18 补充：输入 `mp/ara-pulp-v2` / `2f0f2d6f85979709fbc99dd4098447cb5587ce5f`，已保存用户确认的 SMIC55 工艺标识、WireBond 倾向及[资源预算专题](engineering/SoC_Resource_and_Packaging_Plan.md)。同日后续纠正：DDR DQ x64 保持；LVDS RX/TX 各 128 个通道组，每组 1 对时钟＋N 对数据，像素暂按 16 bit，专题更新至 v1.2，替代原“每方向总计 128 对”的理解。仅文档与算例交付；实际工艺库、IP 视图和封装能力仍待核实，[P01 交接](handoffs/P01_soc_resource_packaging.md)区分初版和增量检查。 **此处 LVDS/像素为历史口径，已由下述最新预算更新替代。**

2026-10-26 P01/I01 当前输入（v1.7）：**RX 改为 64 数据＋4 时钟、4 组 1C16D**（2026-10-26 用户因面积限制确认）；TX 保留 128 数据＋暂定 16 时钟、1C8D。每数据对 500 Mbit/s、12288×12288 灰度/14 bit 和 30 FPS 目标保持。RX 为 136 个信号 PAD，TX 为 288，双向 LVDS 为 424；沿用其余接口假设后条件信号小计 592，比 v1.6 减少 136，电源地及额外端另计。**RX 仅 32 Gbit/s，不能满足 30 FPS 的 63.41787648 Gbit/s 净需求；无开销上限约 15.137688 FPS**，目标与容量的取舍待决定。 若沿用逐行相邻像素分配，RX 为每行 192×64 像素（待传感器确认），纯像素发送 66.060288 ms/帧。旧 128-lane [WaveDrom 图](diagrams/2026-10-23_lvds_rx_timing/README.md)标为历史；[专题](engineering/SoC_Resource_and_Packaging_Plan.md)与[P01 交接](handoffs/P01_soc_resource_packaging.md#lvds-rx64-20261026)记录新预算。本轮仅 Markdown 更新，E01、RTL、配置和图稿未改。

## 1. 最终目标与近期目标

最终目标：以 Cheshire + CVA6 + Ara 为起点，集成 LVDS 图像输入、ISP、脉动阵列/NPU、采购的 DDR 控制器及相关 IP，裁切无用模块，迁移到团队 EDA 服务器，完成 IC 设计、验证、DFT 与物理实现并流片。

团队背景：有 MIPS 处理器及自定义总线经验，RISC-V/标准 AXI 的软硬件经验尚在积累；项目时间紧，希望分阶段学习、直接推进必要工作。

近期目标：把正确的向量组合提取到服务器 `~/CheshireAra`，不再嵌套 `cheshire_ara_asic/`；沿 `src/config/` 集中配置和静态清单，首次保持基线，后续参数开放另行实施，不继续把 Bender 工程管理当作主要任务。

现行教材、参考手册和 RTL 模块指南已交付。E01已按授权完成2B硬件/仿真配套、2C软件重建与2D搬迁验证；后续生产功能修改、新集成与工艺适配按具体范围另行授权。

当前提取状态：**2026-10-22已完成2B、2C、2D；`~/CheshireAra`含硬件、集中配置/共同wrapper、静态构建/运行入口以及从源重建的软件/镜像。** 已在另一新位置完成全新重建、对照运行和实际文件访问检查；独立提取完成，已知ROM告警、LLC失败及其他保留限制不因此关闭。


## 2. 需求、建议和未决项

| 性质 | 内容 |
| --- | --- |
| 用户确认（2026-10-18） | 当前“SoC 架构(v1)”在功能规划层面满足现阶段需求，作为后续实现基线；见[实施总纲](engineering/SoC_Architecture_v1_Master_Plan.md)。CPU/Ara2 经主 Xbar64 共享 M5 访问独立 GB，eMMC 参数加载、RAW/ISP 采集、≤256 ROI 裁切和四入口共享压缩 DDR 纳入目标；新增工程待实现/待验证，参数缺失不撤销拓扑选择 |
| 用户澄清（2026-10-18） | 软件数据流为上电复位、DDR 就绪后 eMMC→DDR，ISP 工作时按需 DDR→GB。S7→M5 的硬件可达性保留，但不作为 eMMC→GB 软件加载流程；此前文档混淆已修正，见[总纲 §4.3](engineering/SoC_Architecture_v1_Master_Plan.md#43-emmc-先加载-ddrisp-工作时再从-ddr-装入-gb)与[修订交接](handoffs/L01_implementation_challenges.md)。搬运采用 CPU 拷贝或软件启动 Host DMA 尚未选定，工程未实施 |
| 用户输入（2026-10-18） | 队长/HYH/TTY 三人全职，多数新增模块从零开发，均未独立完成完整流片；可申请实验室指导，关键资源未齐。上级期望 2027 年 6 月投片，用户说明可延后三个月；取舍为保留 v1、争取专项支持 |
| 排期建议（2026-10-18） | [团队分工与进度对照](engineering/Team_Responsibilities_and_Tapeout_Schedule.md)：6 月前端交付检查、9 月有条件提交 GDS；不表示上级已批准日期调整或工程已启动。分工、依赖与验收见正文，[交接](handoffs/C00_team_execution_plan.md)记录本轮文档变更 |
| 用户确认 | DDR 供应商可以提供 AXI4 版本，不再把 AXI3 桥列为必选项 |
| 当前确认/暂定输入（2026-10-26 / v1.7） | DDR DQ x64；LVDS RX 64 数据＋4 时钟、1C16D，TX 128 数据＋暂定 16 时钟、1C8D；每数据对 500 Mbit/s。12288×12288 灰度、14 bit、30 FPS 目标保持，但 RX 容量不足；192×64 的逐行映射、协议及采样仍须确认，见[资源预算 §3](engineering/SoC_Resource_and_Packaging_Plan.md#lvds-rx-timing) |
| 用户要求 | NPU/ISP 数据通路需要绕过 LLC 直接访问 DDR，避免其流量污染 CPU 的 LLC |
| 用户要求 | 提取独立 `cheshire_ara_asic`；不在 Bender 和旧脚本体系上投入过多精力 |
| 用户要求 | 使用多个独立对话分工，交接信息保存在仓库中 |
| 用户要求（2026-10-06） | 软硬件方案先采用当前版本适用的官方建议；官方未覆盖或新增 IP 的抉择才补充自定义方案，见根 AGENTS.md |
| 用户确认（2026-10-06，待实现） | 沿官方 Platform ROM 钩子，以安全启动频率配置 PLL，并按依赖完成必要 IP 配置；保留运行软件可重复访问的配置接口，支持受控动态调整；具体频率/IP/时钟域未冻结 |
| 提取执行建议 | `cv64a6_imafdcv_sv39` + Ara 2 lanes / VLEN 2048，以当前 Ara 仿真配置取值快照作为首个固定基线；见 02 文档 |
| 用户确认方向（2026-10-16，待实现/待验证） | DDR 共享范围采用软件显式交接＋L1D/写缓冲/LLC 硬件范围维护，落实维护窗口、实际完成握手与错误闭环；具体接口仍待细化。GB 本地交接另行管理，见[总纲 §6](engineering/SoC_Architecture_v1_Master_Plan.md#6-跨模块接口与软硬件约束) |
| 未决 | 最终外设保留表、地址分配、DMA 区大小、最终性能/功耗/面积指标 |
| 用户确认（2026-10-18） | 目标工艺标识为 `smic55ll_ulp_rf_09121825_1P9M_7Ic_1TMc_1MTTc_ALPA1_oa_cds_v1.16_2`；名称确认不代表已核验 PDK、库或 IP 交付，见[资源预算专题](engineering/SoC_Resource_and_Packaging_Plan.md) |
| 用户倾向与评估建议（2026-10-26 / v1.7） | WireBond 倾向保持；RX/TX 信号 PAD 为 136/288，双向 LVDS 424，条件信号小计 592，电源地/额外端另计。RX 32 Gbit/s 的无开销上限约 15.137688 FPS，不能满足 30 FPS；GB/NPU、DDR 共享压缩及服务预算分别验证，片内压缩不能修复 RX 缺口 |
| 未决 | 已选工艺的实际 PDK/库配套、SRAM 宏、PLL/PAD、DDR 控制器/PHY 细节、封装/板条件、DFT/MBIST 和 EDA 工具版本/许可 |
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
| 资源与封装预算（2026-10-26 更新至 v1.7） | [专题及六类预算表](engineering/SoC_Resource_and_Packaging_Plan.md)更新 RX 64 lane、PAD/几何和吞吐；[交接](handoffs/P01_soc_resource_packaging.md#lvds-rx64-20261026)记录文档与算例检查。旧时序图为历史，未修改图稿，未综合、布局、STA、SI/PI或性能实测 |
| DDR–GB 同步说明（2026-10-16） | [主说明](engineering/DDR_GB_Coherence_Design.md)已纳入用户转交的独立评审及答疑；[供应商会议问题](engineering/DDR_Supplier_Coherence_Questions.md)已按用户提供的 Datasheet V2.1 核对能力、页码及待澄清项，尚无会议答复；保存[评审 Q&A](maintenance/L01/reviews/ddr_gb_coherence_review_qa.md)。输入 `322bd6ce9`；用户确认维护窗口／握手需实现，当前仅修订文档，硬件与故障恢复未验收 |
| 实施难点专题（2026-10-18） | [13 类难点与关闭条件](engineering/Implementation_Challenges_and_Open_Questions.md)及 13 幅 SVG/PNG、13 页原生 PPTX 已交付；引用已有同步等方案，区分已确认方向、未决输入、实现缺口和静态缺陷。仅文档/图稿检查，Office 与工程运行未实测；[交接](handoffs/L01_implementation_challenges.md) |
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
10. **iDMA 控制访问问题已复现，未修复（2026-10-20）。** 服务器 GCC 13.2.0 同样把 HAL 的 ID 读取拆为两个 32 位读；内部有效 ID=2，但 +0x44/+0x84 的 AXI 返回放在低半部，CPU 按地址取高半部而得到 0。64 位配置写只更新低 32 位，高字段未写。原小用例 38 字节比较通过不能关闭控制访问问题；这是 HAL 与 RTL 控制接口适配问题，不能据此断言搬运核心损坏。实际信号、原因及未关闭项见[测试报告](maintenance/E01/reports/reference_rebuild_check.md#dma-vector-tests-20261020)。原件未改，该 wrapper 没有 DMA 完成 IRQ；教材 capstone 的默认 BLOCKED/rc16 仍只是保护设置。
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

- 2026-10-18 图稿已建立[按内容检索的目录索引](diagrams/README.md)：区分正式配图、生成依赖、独立交付和backup_no_use历史资料；整理未改变图稿内容或工程验证状态，见[组织交接](handoffs/L01_documentation_organization.md)。

- 当前阅读总入口：[00_README](00_README.md)；Agent 按[定位指南](AGENT_DOCUMENTATION_GUIDE.md)只读相关主题。
- 2026-10-11 用户移除 `learning_backup/`，不得重建；旧“保留旧站”仅为当日历史状态。旧哈希清单和目录外独立证据保留。
- 旧图目录现为 `2026-10-11_native_reconstruction`，不得恢复旧目录名。现行工程契约在 `engineering/`，不能作为过程日志清理。
- 2026-10-13 本次让 A 阅读与检查独立于 B/C，历史试绘退出主路线；压缩本页重复过程叙述，日期、输入、失败/未关闭项仍在原主题交接与原始证据中。完整整理前快照、恢复清单和本次检查见[组织交接](handoffs/L01_documentation_organization.md)。
- 小型维护更新已有主题 handoff；过程报告归 `maintenance/`，不在入口追加聊天流水。用户报告、源码确认、历史产物、本次实测和方案建议须区分。
