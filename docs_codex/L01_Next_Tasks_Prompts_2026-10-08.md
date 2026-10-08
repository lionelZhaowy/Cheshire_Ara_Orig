# L01后续新对话Prompt（2026-10-08）

> 实施后状态：本页及系统规划中的S/OS/ASIC/M/P文档任务已按最新授权实施，独立R复审亦已交付。见[主管报告](L01_System_Textbook_Implementation_2026-10-08.md)。以下代码块是可追溯的历史任务定义，不应再次机械执行或覆盖本轮产物。目标运行、工程修复和移植仍须各自输入与独立授权；它们未因本次文档任务完成而自动启动。

以下授权均为文档实施，不授权生产修复、提取或大型验证。每次复制一个完整代码块，不自动启动Agent。03/04整合现有材料；05/06合成接口契约；08与02分工；07教学可立即编写限定范围，具体移植/运行待输入。

**2026-10-08 追补：**用户确认论文实验需要OS，补充CVA6深度上限及ASIC机制教学要求。最新分期、文件所有权和可复制S/OS/ASIC Prompt见[系统教材深化规划](L01_System_Textbook_Revision_Plan_2026-10-08.md)。下列旧S/O块保留为上一轮方案，不再直接作为整轮实施入口；M/P/R可沿用但须先读更新结论。当时新规划尚未实施；最新实际状态以上方实施追补为准。

文件所有权：S拥有软件13–16及software；M/P各拥有新手册；R只写复审。用户可安排不同worktree并行。各自生成检查后，由O统一生成并串行汇总状态、任务、索引和pages.json。同一工作区中S与O不能同时改公共产物。

## L01-S：软件主线整合（原计划03）

~~~text
请按根AGENTS.md承担L01-S。读者有MIPS/自定义总线/SV/C经验，初学RISC-V/Cheshire/CVA6/Ara。现在开始文档实施，交付实际软件正文重组、修改前后对照、生成页、验证记录及独立交接，不另写重复的03启动大全。

先读PROJECT_STATE、AGENT_TASKS的L01/S01/S01-B01/V01，检查git status --short、分支、完整HEAD及未提交/未跟踪文件。必读learning/README.md、scripts/pages.json、L01_Teaching_Quality_Review_2026-10-08.md、03-08_Topic_Readiness_2026-10-08.md、handoffs/2026-10-08_L01_teaching_review_peripherals_ara.md、2026-10-06_L01_platform_rom_boot_review.md、2026-10-07_L01_review_fixes.md，并核对目录中相关更新交接。读取content/runtime/build/boot/boot-debug及labs、software现有构建/运行/库文档、现有03平台配置与02第7节。

拥有learning/content/runtime.html、build.html、boot.html、boot-debug.html，直接关联software文档，独立L01_Software_Revision_<日期>.md、新evidence目录和handoff。仅在独立worktree生成网页；不改pages.json、共享状态/任务/00索引。生产hw/sw/.bender/配置/地址图/链接脚本/构建入口及教材examples只读。保护用户图稿/PPTX、旧站和历史证据；需要图或脚本修改先说明最小必要性，遵循维护约定。

先给简短动作表，再完成C源码→编译链接→ELF→JTAG装载→默认ROM/应用crt0→main→库/驱动→MMIO→UART正常行为。主机/目标、构建/运行、库/驱动、ROM/crt0、section/装载段分别解释。先走到main，再讲介质、Platform ROM及OS支线。保留正确例子和旧语义锚点；正常前提与完成语义不能删，详细故障定位集中到独立入口，S01-B01及DMA阻塞短提示保留。

技术判断先查适用版本官方软件/启动资料，再定向核sw.mk、crt0、链接脚本、ROM、UART和ELF加载器。在线优先官方，注明版本差异；不得把官方修复当本地已应用，不扩大全仓审计。

只运行文档生成、结构/链接、临时生成一致性和离线浏览器，按README写新证据目录；不运行软件构建、RTL仿真/综合或板测。区分用户报告、源码确认、已有产物、本轮文档实测与方案。验收：不打开诊断能复述源文件到UART位流，标出机器/阶段/地址/成功条件；有故障能找到入口。网页通过不能代替教学验收。

缺模型/环境/地址输入时写待决、提供者和影响，继续有依据部分，不伪造成功输出。按HANDOFF_TEMPLATE记录命令/退出码/日志/未验证项/下一步，共享建议交O。真实运行依赖E01/S01/V01；工程修复另行授权。
~~~

## M01-D：IP与DDR接口契约（原计划05/06）

~~~text
请按AGENTS.md承担M01-D，面向有RTL/C经验、学习AXI和本SoC的集成工程师。现在授权文档实施：交付docs_codex/M01_IP_DDR_Interface_Contract.md、来源/缺口表和独立handoff，形成接口契约与验证矩阵，不重复HTML原理。

开始查git status --short、分支、完整HEAD及涉及文件。必读PROJECT_STATE、AGENT_TASKS的E01/V01/S01/M01/I01/P01、00_README、02第8节、现有03平台配置、03-08_Topic_Readiness_2026-10-08.md、handoffs/2026-09-22_M01_DDR_interface_feasibility.md、2026-10-08_L01_teaching_review_peripherals_ara.md及相关更新交接；读HTMLaddress-map/axi/adapters/sharing/integration/accelerators/ddr和configuration对应字段。

只拥有新M01手册、docs_codex/reviews/M01_<日期>/新证据目录和独立handoff。共享索引/状态/任务、HTML和他人专题不改；已有目标文件先核对所有权。生产hw/sw/.bender/top/config/filelist/地址图/链接脚本只读；不建cheshire_ara_asic、不提取、不升级、不跑大型验证，保护历史证据和用户资产。

范围：Reg宽度/副作用/启动完成/IRQ，AXI地址/ID/突发/响应/背压，复位时在途事务，共享buffer可见性/所有权，DDRcontroller/PHY/PAD责任与就绪。以一帧串起契约；CPU/Ara保留LLC、NPU/ISP旁路是需求而非已实施拓扑。明确LLC副本和LR/SC观察边界；未知位宽/容量/频率/地址/型号标待决，不冻结DMA区。已有原理和Reg实验F只引用。

先查适用版本Cheshire官方集成资料及本地AXI/LLC/原子实现，再定向核cheshire_soc/pkg消费者。外购已确认AXI4，不沿旧AXI3假设加桥。官方未覆盖的选择标自定义建议/理由；机密只写授权摘要和受控位置。

检查限Markdown链接、源路径/符号/方向/字段核对及小量预算算式；不执行工程构建/仿真。区分用户需求、源码、旧产物、文档实测、候选方案。验收：能解释一帧谁写/读、何时可见/复用，每个未知有负责人及受影响验收，不凭空保证共享原子。

缺输入列明用户/IP供应商/I01/P01提供的字段，继续可写契约。按HANDOFF_TEMPLATE写命令/结果/未验证/下一步，注明无工程修改；E01/S01/V01/I01/P01接收建议，O汇总索引。真实集成等待资料与独立工程授权。
~~~

## P01-D：ASIC技术适配与证据（原计划08）

~~~text
请按AGENTS.md承担P01-D，开始实施文档。面向从FPGA转ASIC、具备SystemVerilog经验的工程师，交付docs_codex/P01_ASIC_Adaptation_and_Evidence.md、来源/缺口清单和独立handoff。02负责固定源码提取，本手册负责技术替换要保持的语义及验收，不另造提取规格。

先检查git status --short、分支、完整HEAD及已有修改。必读PROJECT_STATE、AGENT_TASKS的P01/E01/V01/S01/M01/I01、02第6/9节、现有03平台配置、03-08_Topic_Readiness_2026-10-08.md、handoffs/2026-10-08_L01_teaching_review_peripherals_ara.md、2026-10-06_L01_platform_rom_decision_tracking.md及目录相关最新交接；读HTMLclocks/reset/power/future和configuration平台条目。

仅拥有新P01手册、docs_codex/reviews/P01_<日期>/新目录和独立handoff；共享状态/任务/索引交协调者。保护用户PPTX、旧站和历史证据；目标文件已有内容先核对所有权。hw/sw/.bender/配置/构建/filelist只读，不提取、不生成假宏/约束、不升级，不运行综合/仿真/物理实现。

范围：定向盘点XPM/MIG/MMCM、tc_sram/ROM、clock gating/reset、DDR/USB PHY、PAD和DFT/MBIST边界。每项给当前来源/接口、替换要保持的极性/周期/byte-enable/初始化语义、输入缺口、负责者及功能/CDC/RDC/等价/实现验收。用现有SRAM k+1/k+2例说明不能只换模块名，链接HTML而不复制整章。未知PLL频率、电源域、宏/PAD型号和DFT策略不成为决策。

优先读本地随附官方技术单元资料和维护者实现，再看调用实例与平台wrapper。在线仅用版本适用的官方源；受限资料只记授权摘要/受控位置。检查限Markdown链接、源路径/版本、接口/延迟与清单交叉核对，不跑目标工程。

区分用户报告、源码、旧产物、文档检查与建议。验收：读者能对SRAM/时钟/PHY替换列出保持语义、资料和观察点；可综合不等于时序/DFT/签核通过。缺PDK/宏/PAD/PLL/PHY/EDA资料时标提供者和受影响工作，继续有据盘点。

按HANDOFF_TEMPLATE记录文件、命令/结果、未编译/仿真/板测/签核、最小下一步，建议交E01/V01/S01/M01/I01/P01和O。工程替换和验证另行授权，不由本Prompt顺带启动。
~~~

## L01-R：独立复审外设/Ara（原计划04质量门槛）

~~~text
请按AGENTS.md承担L01-R，独立只读教学复审，不启动其他Agent。读者具备MIPS/自定义总线/SV/C，初学RVV/Ara。交付docs_codex/L01_Independent_Review_<日期>.md及独立handoff，检验正常链能否讲通。

先查git status --short、分支、完整HEAD及已有修改。必读PROJECT_STATE、AGENT_TASKS L01、learning/README/pages.json、L01_Teaching_Quality_Review_2026-10-08.md、L01_Peripherals_Revision_2026-10-08.md、L01_Ara_RVV_Revision_2026-10-08.md、handoffs/2026-10-08_L01_teaching_review_peripherals_ara.md及相关最新交接。完整审读18–26、peripheral-debug、vector-debug和实验C/D/E，定向回查CVA6/配置/寄存器入口。

仅写自己复审报告、新evidence目录及handoff。教材正文/生成页/脚本/图稿、共享状态及生产源码全部只读。技术疑点先查随附官方资料/规范，再核本地消费者及版本；纯编排不扩大全仓审计。不运行目标软件构建、RTL仿真/综合或板测。

分别验收：不打开诊断可否复述正常全过程；故障能否找到入口；阻塞是否被隐藏。手算VLEN/vl/SEW/LMUL/lane及两lane映射，解释指令/标量/数据路径、CPU应答后的在途工作和SPM交接。设备需解释支持层、接线/时钟/复位、关键寄存器和完成条件。每项问题给锚点/短摘录/影响/具体修法，区分事实、前置依赖、组织、措辞；好的段落说明保留理由。

按README运行只读结构/链接/临时生成一致性及浏览器检查，输出到新目录，记录退出码。自动检查不替代全文阅读；没有真人试读须说明。工具缺失不伪造通过，继续独立审读。保留用户报告、源码、旧产物、文档检查、建议等级，Platform ROM/iDMA/Ara目标缺口不关闭。

用HANDOFF_TEMPLATE交接证据与最小修订任务，需要正文修正只提供有定位的建议，由拥有者或O串行汇总。真实工程验证仍依赖E01/S01/V01，超出本Prompt。
~~~

## L01-O：串行汇总与剩余全书优化

~~~text
请按AGENTS.md承担L01-O，仅实施文档协调和剩余教学组织优化。目标读者有MIPS/自定义总线/SV/C经验，初学本SoC。交付阅读路线/职责映射、范围内实际正文、旧链接保护、验证记录和独立交接。

先核git状态/分支/完整HEAD及文件所有权，读PROJECT_STATE、AGENT_TASKS、00_README、HANDOFF_TEMPLATE、learning/README/pages.json、2026-10-08全书审查/条件评估/Prompt及handoffs/2026-10-08_L01_teaching_review_peripherals_ara.md；再读最新S/M/P/R交接及输入提交，不能默认同版本。尚未交付的文件不覆盖，继续不重叠部分。

串行拥有共享状态/任务/00索引/handoffs索引、learning导航及生成页，以及全书审查中剩余02/03、04–06/12导读、10公共语义、27–30任务顺序、来源页。S的软件13–16仅在其交付后协调，不并行覆盖；M/P技术正文尊重其所有权。保护图稿/PPTX/旧站/历史证据，生产RTL/sw/依赖/地址图/工程脚本只读。

先列具体移动/合并表再落实：首页给首次运行和工程进阶路线；配置字典按需读；27从Reg任务起、28从一帧起、29大模型为选读。原03–08标历史规划并映射现有载体，现有03平台文件原名保留。章数可依收益调整但须说明成本，保留slug/id；跨页用anchor_migrations及无脚本入口，避免旧URL失效。

事实先查版本适用官方资料和定向源码；纯重排不扩大审计。运行文档生成、结构/链接、临时生成一致性、桌面/手机/无脚本浏览器，证据写新目录。验收读者能从源程序走到设备行为，知道何时需要AXI/cache/平台章；工程读者能由Reg任务推进到帧交接。字数/图数/网页通过不能代替教学验收。

缺用户/IP/工艺/OS输入只标相应待决和提供者，继续有据内容；不冻结未知参数、不编运行通过。按HANDOFF_TEMPLATE独立交接，汇总状态保留各证据等级，明确未软件构建/RTL运行/板测。Platform ROM/iDMA/Ara缺口继续开放。后续E01/V01/S01/M01/I01/P01工程修改另行授权，07不作提取前置。
~~~

## 暂缓项目解锁条件

07的本平台工程移植/运行等待OS/RTOS版本、启动链、RAM、设备、实时性和向量上下文约定；S01核官方port/BSP/DTS/工具链，M01落实存储契约，V01提供运行环境。教学需要OS已确认，系统教学不等待这些输入，使用新规划的L01-OS任务。05/06真实IP/DDR接入等待I01/供应商接口；08工艺映射等待P01受控资料和工程授权。没有为这些尚未具备条件的工程任务生成立即实施Prompt。
