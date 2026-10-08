# L01 系统教材实施与主管验收

输入日期2026-10-08；分支 mp/ara-pulp-v2；HEAD 459f9d6f5748e39063f7bb67e959c2f27859915d。用户本轮明确要求创建多个子Agent实施，由主管协调验收，取代上一轮“仅规划”的范围。授权仍限教材与关联文档，生产RTL/sw/依赖/配置/地址/构建只读，无目标构建、仿真、综合、板测或OS移植。

## 分工与输入保护

主管在任何本轮编辑前记录2824个文档/资产/历史证据文件哈希、Git状态和完整旧正文副本，见learning/evidence/system-implementation-20261008/input.json及before-content。既有未提交教材、报告、用户diagrams.pptx均保留，不还原工作区、不提交他人改动。

|负责者|独占范围|汇总责任|
|---|---|---|
|software子Agent / L01-S|architecture/cva6/configuration/runtime/build/boot/boot-debug、traps、software-debug及直接相关software文档|软件完整过程、默认启动、trap；独立来源与handoff|
|os子Agent / L01-OS|rtos/virtual-memory/linux/os-devices/os-debug|官方参考版本、本地能力差距、OS正常教学；独立handoff|
|asic子Agent / L01-ASIC|clocks/reset/power/future及六个ASIC任务页|真实VRF消费者、物理实现机制与输入缺口；独立handoff|
|主管 / L01-O|互连/DDR/集成/仿真衔接、measurement/system-debug、首页/实验/来源、目录/脚本/生成页、共享状态|内容复核、跨章节前置、集中生成、浏览器与保护检查、最终验收|

子Agent均禁止写公共导航/生成页/共享状态；本轮没有自动扩权到工程任务。详细旧内容到新位置的规划见L01_System_Textbook_Revision_Plan_2026-10-08.md，本轮结果以本报告及各组交接为准。

## 修改前后与保留理由

|范围|修改前|本轮处理|读者应能完成|
|---|---|---|---|
|系统/CPU/配置|资源、字段表先于使用；软件链跨多个抽象层|基础使用模型提前，资源细节后置；明确四类配置各自职责|解释程序需要的ISA/ABI/状态/存储，而非背参数名|
|软件|组成、构建、启动、运行混为一次调用；crt0靠后|同一数组从C对象、ELF、默认装载到main/库/驱动/UART；多介质与OS阶段后置|标每步执行者、地址、输入输出和完成条件|
|trap与OS|通用现场与调度不足，OS只作后续概览|新增trap、RTOS、虚拟内存、Linux启动、OS设备；本地SDK版本与官方参考分开|画A→B→A、解释页表/设备地址、固件到用户程序及设备调用|
|外设/Ara|上一轮已经实际优化|保留正常链和原图，独立复审后只修定位明确的问题/回链|正常过程不依赖诊断页；已知阻塞不隐藏|
|地址/AXI/LLC|已有具体事务推演，多数内容正确|保留请求/背压/返回与缓存/SPM机制；公共MMIO补副作用/FIFO和握手边界|解释同一地址、一次访问与一次设备任务的不同含义|
|Reg集成|先官方实例/端口表，再具体设备任务|先A=7/B=9→START→DONE→RESULT=16→清完成，再接口接入|解释寄存器、控制器完成与软件消费如何对应|
|DDR与帧|正常初始化、诊断、配置表混排|先早期ROM/SPM资源，再初始化与测试/发布ready，再读路径和接口契约；一帧流程先于IP清单|不在DDR就绪前依赖DDR；区分均值带宽、服务间隔、缓冲容量|
|ASIC|资源清单与泛化延迟例为主|真实VRF bank→消费者→宏；六个任务页补跨域、物理接口、时序、制造测试、首硅|指出宏延迟/掩码或时钟复位改变影响哪条契约|
|测量|性能边界零散|新增完整测量任务，先独立正确性，再内核/设备/端到端窗口和重复记录|解释内核加速但应用变慢、可测量条件与证据范围|

### 目录与旧链接

当前发布九篇：系统与CPU使用模型→从C到结果→地址/互连/物理存储→异常/外设→Ara→OS→IP/DDR协作→ASIC→验证/测量。42主章节包含原30章与新增12章；首页、实验/参考另计。原页面slug和语义锚点优先保留，跨页诊断用原位置短提示及明确链接；原七篇首页锚点仍保留对应主题。

旧七篇/30章图放首页折叠的历史对照，原SVG/PPTX与WaveDrom资产不改；不让旧图的章号冒充当前目录。生成器、维护说明、结构检查按实际课程同步，历史记录保持原数字。

## 证据等级与仍待工程验证

本轮教材中的规范语义以适用官方版本为参照，本地实现以定向源码核对为依据，假设数字明确作为算例。OS源码/SDK配方存在不等于当前镜像能启动或向量任务切换已通过；ASIC逻辑接口说明不等于宏、时序、DFT和工艺签核。

Platform ROM S01-B01、iDMA控制宽度与Ara错误处理/动态运行缺口继续开放。DDR/IP/工艺参数、最终OS方案和论文指标仍需对应责任方输入。原VCU118 HelloWorld是用户报告，历史编译/单元测试仍属原日期产物，不计作本轮目标实测。

## 审读覆盖与主管验收边界

“作者完整”表示负责者完整审读并实施自己负责的正文，不称为独立复审；“独立完整”表示另一负责者读完段落、表格、示例和诊断入口。“主管定向”明确不是新一轮整章技术审计。上轮[30章完整审查](L01_Teaching_Quality_Review_2026-10-08.md)仍是旧版基线，不冒充本轮新增12章的独立验收。

[独立复审](L01_System_Independent_Review_2026-10-08.md)覆盖17页：OS五页、测量、外设/Ara九章及原两个诊断；软件作者不验收自己为“独立通过”。ASIC作者另完整读了traps/boot/boot-debug，但结论限于时钟、复位、栈、平台钩子与Debug边界。主管统一核相邻前置、真实入口、旧语义ID、主要算式、生成页与资产保护；尚无真人试读或新目标运行。

|当前章|页面/职责|本轮阅读等级与处理|
|---|---|---|
|1|[整体架构与平台边界](learning/architecture.html)|软件作者完整；主管定向复核，已实施|
|2|[CVA6与RISC-V程序使用模型](learning/cva6.html)|软件作者完整；主管定向复核，已实施|
|3|[Cheshire、CVA6、Ara 与软件配置](learning/configuration.html)|软件作者完整；主管定向复核，已实施|
|4|[裸机 C 程序运行模型](learning/runtime.html)|软件作者完整；主管定向复核，已实施|
|5|[工具链、链接与 ELF](learning/build.html)|软件作者完整；主管定向复核，已实施|
|6|[Boot ROM、启动模式与应用初始化](learning/boot.html)|软件作者完整；主管定向复核，已实施；ASIC完整交叉阅读启动/上下文接口|
|7|[JTAG 与程序加载调试](learning/boot-debug.html)|软件作者完整；主管定向复核，已实施；ASIC完整交叉阅读启动/上下文接口|
|8|[地址空间与访问属性](learning/address-map.html)|主管定向审读；保留按地址走译码的主线，仅同步章号|
|9|[AXI 通道、突发与握手](learning/axi.html)|主管定向审读；保留通道握手推演，仅同步章号|
|10|[AXI Crossbar 结构与事务路由](learning/interconnect.html)|主管定向审读；保留路由/仲裁/响应的因果，仅同步章号|
|11|[接口适配与 RegBus](learning/adapters.html)|主管定向审读；补公共MMIO/W1C/FIFO与逐次握手语义|
|12|[Cache、LLC/SPM 与存储路径](learning/memory.html)|主管定向审读；保留cache/SPM分层，仅同步章号|
|13|[异常、中断与上下文](learning/traps.html)|软件作者完整；主管定向复核，已实施；ASIC完整交叉阅读启动/上下文接口|
|14|[MMIO 驱动、UART 与 GPIO](learning/uart-gpio.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|15|[定时器与中断系统](learning/interrupts.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|16|[I2C 与 EEPROM](learning/i2c.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|17|[SPI、NOR 与 SD](learning/spi.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|18|[iDMA、流量管理与总线错误](learning/dma.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|19|[Serial Link、VGA 与 USB](learning/stream-io.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|20|[Ara 结构与 CVA6 协处理器接口](learning/ara.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|21|[RVV 编程与结果验证](learning/vector.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|22|[CPU、Ara、DMA 与 NPU 的共享数据](learning/sharing.html)|独立完整复审；保留已有连续主线，按IR问题局部修正/回链|
|23|[RTOS任务、调度与同步](learning/rtos.html)|OS作者完整；独立完整复审，保留正常任务与条件边界|
|24|[保护、页表与进程地址空间](learning/virtual-memory.html)|OS作者完整；独立完整复审，保留正常任务与条件边界|
|25|[嵌入式Linux启动与用户程序](learning/linux.html)|OS作者完整；独立完整复审，保留正常任务与条件边界|
|26|[操作系统中的设备与缓冲区](learning/os-devices.html)|OS作者完整；独立完整复审，保留正常任务与条件边界|
|27|[自定义 IP 的控制、数据和中断接入](learning/integration.html)|主管定向审读；一次Reg正常任务提前，完整接口后置|
|28|[DDR 控制器、PHY 与 AXI4 接入](learning/ddr.html)|主管定向审读；早期SPM与初始化提前，详细诊断迁出|
|29|[LVDS、ISP、NPU 与外部 DDR 集成](learning/accelerators.html)|主管定向审读；完整帧先行，新增生命周期/带宽/缓冲推演|
|30|[模型任务划分与容量带宽预算](learning/models.html)|主管定向审读；保留透明算例，标选读，恢复细节迁出|
|31|[时钟系统与 PLL](learning/clocks.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|32|[复位体系与平台启动条件](learning/reset.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|33|[电源域与低功耗规划](learning/power.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|34|[从VRF实例到SRAM宏接口](learning/asic-memory.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|35|[跨时钟与复位域的事务交接](learning/cdc-rdc.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|36|[从逻辑信号到PAD、封装与设备](learning/physical-interfaces.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|37|[时序约束与物理实现反馈](learning/timing-physical.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|38|[Scan、MBIST与制造测试](learning/manufacturing-test.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|39|[首硅启动与系统可观测性](learning/silicon-bringup.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|40|[固定配置工程与 ASIC 集成验收](learning/future.html)|ASIC作者完整；主管定向复核实例/相邻依赖，已实施|
|41|[Questa/VCS 仿真与结果验证](learning/simulation.html)|主管定向审读；保留正常运行/验证方法，故障定位迁出|
|42|[正确性、性能与论文实验记录](learning/measurement.html)|主管完整编写；OS交叉阅读，独立完整复审|

首页重新给出唯一完整阅读顺序和首个软件任务前缀，保留旧篇锚点；labs保留六个现有实验，补四个不依赖目标运行的系统推演任务；registers正文及429项索引不变，evidence分当前文档结果与历史运行证据。software-debug为软件作者完整编写，system-debug为主管完整编写，os-debug及原外设/向量诊断均在17页独立审读中。首页/labs/evidence/registers由主管定向核衔接与生成，不能记为独立全文技术审计。

## 问题闭环与链接迁移账本

|ID/类别|准确位置与原断点|已实施动作与复核|
|---|---|---|
|IR-01 入口事实|vector#loop 将构建入口写成 examples/build_journey.sh|改为真实 scripts/build_journey.sh；独立者已复核，未运行脚本|
|IR-02 教学组织|uart-gpio#uart-init 连续重复初始化和THR/flush|合并成单位/前提→完整调用→初始化因果→返回与完成→结果；独立者已重新读该节|
|IR-03 前置依赖|sharing页首要求先读vector，而vector先要求共享契约|sharing仅要求memory/Ara，vector按任务引用ownership最小前提；独立者复核无强制循环|
|IR-04 图文事实|sharing#ownership图注描述图中不存在的隔离分支|第一图只讲正常过程；未来图#handoff给system-debug#frames入口，图不改|
|IR-05 诊断导航|os-debug#locate-stage缺裸机构建/启动诊断入口|补software-debug链接，独立者复核|
|S-自查 技术范围|boot#nor-boot把single_flash写擦CR3V问题扩大到single_read|按真实调用路径收窄影响；读路径仍有自身模式/镜像/目标条件，不误标为已运行|
|O-01 接口语义|adapters#reg-contract对连续valid的措辞可能让人误认重复握手不会访问|明确ready=0是等待，每个valid&ready边沿为独立访问，副作用据接受次数发生|
|O-02 前置依赖|runtime过早依赖完整地址章；integration基本Reg任务要求DMA|runtime补最小物理地址/SPM解释，前置回到architecture/cva6；Reg任务去掉无关DMA强前置|
|O-03 维护输入|旧路线图生成器自动读改版后的pages.json|固定对应旧目录快照，原SVG及manifest逐字节复现；不是删除检查或覆盖历史图|

正文迁移采用“保留原语义锚点和最小说明→明确链接到新详细内容”，未删除旧ID，因此未新增anchor_migrations规则。具体跨页映射：simulation#debug→system-debug#simulation；原共享未来图恢复语义→system-debug#frames；DDR排查→system-debug#ddr，早期SPM正常前提留ddr#spm-diagnostics；future#sram-example保留延迟入口并引asic-memory完整消费者。软件故障按作者报告迁至software-debug，平台ready限制集中system-debug#platform-readiness。既有373项迁移仍全部核对。

新增12章、3个诊断参考页带来15个主页面增量；原slug全部保留，旧章号按链接目标同步。迁移成本是导航、前置与生成规则；收益是软件读者先完成一条过程，OS/ASIC新增机制有明确输入输出，诊断不再打断正常任务。共用维护脚本仅改当前结构规则、截图覆盖、导航篇数、证据入口及旧图复现输入；没有修改教材示例代码或工程脚本。

## 按读者任务的验收答案

这些答案来自正文与交叉审读，不代表真实读者已经试读。

|验收问题|正文给出的连续答案/可检查产物|
|---|---|
|一个C程序怎样产生UART文本？|runtime#software-stack区分构成/构建/启动/运行；build从对象与符号走到ELF；boot默认ROM/装载/crt0后到main；runtime#runtime-call和uart-gpio讲格式化、DIF、MMIO、FIFO/移位器及接收结果。每步可标主机或目标，不把链接器画为运行调用层|
|为什么中断返回不等于任务切换？|traps中硬件只保存规定CSR，软件保存寄存器/栈现场；rtos#switch-walk按A栈→调度选择→B栈→B返回→A恢复推演，普通函数ABI不足以替代异步上下文|
|同一buffer有几种地址？|virtual-memory#translation-walk给Sv39具体索引与PA；#device-addresses和os-devices区分用户VA、内核指针、物理及DMA地址，MMIO基址/fd不是同一对象|
|Linux怎样走到用户程序？|linux连续交接固件/内核/DTB/rootfs/init/应用；OS设备章用同一UART比较轮询、RTOS队列/唤醒、Linux write/TTY/driver，保留各自完成条件|
|外设怎样判断一次操作成功？|独立复审覆盖UART、GPIO/事件、I2C、SPI、DMA、流接口；数据/地址/单位与提交、控制器完成、设备完成、结果正确分开。iDMA运行阻塞与器件/引脚条件仍在例子附近|
|Ara参数与完成时间怎样区别？|ara/vector/sharing保留VLEN硬件容量、lane并行资源、SEW/LMUL/vl运行状态；137项按实际vl推进，指令/标量接口与AXI数据路分开，应答/提交不等于所有执行与访存结束|
|换SRAM宏为什么不是替名字？|asic-memory用当前2lane/VLEN2048推得8KiB VRF、每lane8个64×64-bit bank；#k-plus-two指出数据和valid/队列身份错配，timing-physical接真实路径与setup/hold约束|
|正常调频/复位/跨域怎样处置工作？|clocks/reset/power先停止新任务并完成必要交接，再切换/释放/重新就绪；cdc-rdc解释多位握手/异步FIFO及两侧复位契约，不用两级同步器包办事务|
|一帧预算怎样约束DDR与buffer？|accelerators#buffer-lifetime及M01第8节按同一假设计算容量、每次读写流量和服务间隔；平均100μs积累量只是下界，真实峰值/最长等待由IP方提供|
|怎样证明更快？|measurement先独立校验，再分别记录内核、设备服务、端到端窗口。相同输出不等于同一工作量，计数器与实际频率/完成点对应，示意数字不是性能证据|

## 03–08载体落地与待解锁部分

03/04“已有内容足够，建议整合”的工作已在软件/CVA6主线与Ara复审中落实；05/06“可立即编写限定范围”合并交付[M01工程手册](M01_IP_DDR_Interface_Contract.md)，HTML承担机制；07限定范围的系统教学已经完整交付；08限定范围由ASIC正文和[P01手册](P01_ASIC_Adaptation_and_Evidence.md)落实，02仍是提取规格。没有创建六篇重复或占位正文，现有03平台配置文件未改名/覆盖。

剩余输入具体影响工程：供应商给DDR/PHY/PLL/PAD/宏/模型及合法参数；I01给帧格式/峰值/背压/控制完成契约；用户与S01定OS/固件/工作负载，E01给唯一工程基线，V01提供目标证据。OS教学不再等待“是否需要OS”，但本地移植/向量抢占与性能不能凭源码存在验收。旧实施Prompt现标为已执行历史定义，避免新对话覆盖成果；[Prompt入口](L01_Next_Tasks_Prompts_2026-10-08.md)仍保留原任务授权边界。

## 实际文档检查与失败处理

运行目录为仓库根；Python 3.13.5，Google Chrome 151.0.7922.108。命令和退出码也写入[总交接](handoffs/2026-10-08_L01_system_implementation_acceptance.md)。

|检查|实际结果与证据|
|---|---|
|统一生成、链接/标题/导航/TOC/资源|build_site退出0，51主页面+20旧入口；check_site退出0，5068本地链接、108个SVG XML；最终Markdown计数见收尾日志|
|结构与隔离生成|[release-generated-final/checks.txt](learning/evidence/system-implementation-20261008/release-generated-final/checks.txt)：退出0，九篇42章前置顺序、373迁移、143产物一致、37结构SVG母版及manifest一致|
|浏览器|[release-browser/browser.txt](learning/evidence/system-implementation-20261008/release-browser/browser.txt)：退出0，51页1440×1100与390×844、12页无脚本、199跨页旧书签、交互/寄存器/图形；71个被测HTML和输入哈希前后不变|
|主管视觉抽查|查看Linux手机版、VRF/SRAM桌面、C运行桌面截图，目录/标题/前提和正文未见遮挡；属于3张抽查，不扩大为人工逐页看完所有像素|
|本轮输入保护|[protection.json](reviews/L01_system_acceptance_20261008/protection.json)：2824输入文件中2744不变，80项变化均在授权文档白名单；383个旧内容ID全部保留，77个定向源哈希不变；分支/HEAD不变，无docs_codex外变化|
|作者/独立复审|软件7+2、OS4+1、ASIC4+6作者检查；17页独立完整审读及5项修正复核；M01/P01链接/契约/公式检查分别见作者交接|
|格式与算式|git diff --check退出0；137项和28085、Sv39示例、VRF尺寸与帧预算仅作静态复算，未计作目标测试|

保留的失败记录：[首次沙箱生成](learning/evidence/system-implementation-20261008/release-generated/checks.txt)因Chrome无DevToolsActivePort退出1；主机重试揭示[旧路线图输入不一致](learning/evidence/system-implementation-20261008/release-generated-host/checks.txt)，固定历史输入后通过。预检查还修复os-debug缺统一教学入口容器；并未删减检查。参见[preflight.txt](learning/evidence/system-implementation-20261008/coordinator/preflight.txt)。

所有检查属于文档与静态源核对。未进行目标软件编译、RTL展开/仿真、综合、板测、OS移植、性能测量、STA/CDC/RDC/DFT/物理签核，也未做真人试读或Office/PPTX打开验证。用户已有HelloWorld、旧ELF/bitstream和历史实验各保留原证据等级。没有Git提交。

后续同轮标题修正：用户指出口语/提问/授课式标题违反既定规范，已另建标题前快照并实施专项修正。技术内容与篇章结构保留；标题修正后的准确清单和重新生成/浏览器结果见[L01标题规范修正](L01_Title_Style_Revision_2026-10-08.md)。上表计数与网页截图仍对应标题修正前快照，不回填历史检查。
