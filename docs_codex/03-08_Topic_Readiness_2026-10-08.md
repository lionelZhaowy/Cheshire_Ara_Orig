# 原计划03–08专题的实施条件评估

2026-10-08 实施追补：用户随后授权多Agent实施。软件主线、OS四章及通用trap、ASIC六章与系统测量已落入HTML；05/06的限定契约和08的适配手册已经交付。见[主管报告](L01_System_Textbook_Implementation_2026-10-08.md)、[M01契约](M01_IP_DDR_Interface_Contract.md)、[P01手册](P01_ASIC_Adaptation_and_Evidence.md)。下表更新当前载体，后续分篇分析保留初次评估的原目标/依赖；其中旧章号对应当时七篇30章，应按主题slug访问当前九篇42章。文档交付不改变工程与运行缺口。

评估日期2026-10-08，基准 `459f9d6f5748e39063f7bb67e959c2f27859915d` / `mp/ara-pulp-v2`。原始目标取自 [00_README](00_README.md) 的规划表，当前实现与缺口以源码、[项目状态](PROJECT_STATE.md)及最新交接为准。没有创建六份占位正文，也没有启动提取/修复/回归。

## 总体结论

|计划文件|明确分类|建议载体与职责|
|---|---|---|
|03_Boot_and_Baremetal_Debugging.md|**已有内容足够，建议整合**（本轮已完成主线整合）|runtime→build→boot→boot-debug，通用traps与software-debug，software目录继续作操作参考|
|04_CVA6_Ara_and_Memory_System.md|**已有内容足够，建议整合**（本轮已收敛CPU主线并复审Ara）|cva6→ara/vector/sharing，OS地址/上下文另章；configuration保留字典，目标性能待测|
|05_AXI_Address_Map_and_Custom_IP.md|**可立即编写限定范围**（限定文档已交付）|HTML解释Reg任务；M01_IP_DDR_Interface_Contract.md写双方接口/责任/验收，不分配最终地址或IRQ|
|06_DDR_and_Platform_Integration.md|**可立即编写限定范围**（限定文档已交付）|HTML补早期SPM→DDR就绪及帧预算；与05共用M01手册；供应商具体配方仍待输入|
|07_RTOS_and_Linux.md|**可立即编写限定范围**（教学已交付）|traps/rtos/virtual-memory/linux/os-devices及os-debug；本地6.5源码与官方参考有据，真实移植/镜像/运行仍待输入|
|08_ASIC_Migration_and_Verification.md|**可立即编写限定范围**（限定文档已交付）|HTML机制与P01_ASIC_Adaptation_and_Evidence.md契约互补；02仍负责提取，未知工艺/IP不写成既定实现|

“足够”指覆盖范围已有，不表示教学组织或动态证据合格。当前没有一篇能按原计划所有工程实验宣布“可立即完整编写”：可写的机制/契约与尚缺运行环境的具体流程必须分开。不能因没板测否定源码分析，也不能因能画接口图就授权工程实现。

## 共用输入、环境与证据边界

已核对路径：Python、RISC-V bare-metal GCC、Questa vsim、Chrome、Bender在PATH；VCS/vlogan不在PATH。只确认可执行文件位置，不确认许可证、完整工程可编译或仿真可跑。`cheshire_ara_asic/` 尚无交付目录。现有ELF/dump、用户VCU118 HelloWorld、独立小Reg历史测试分别保持原证据等级。当前生产仿真profile/decoder组合、iDMA宽度、Ara运行、Platform ROM返回路径等缺口未关闭。

技术依据优先采用随附官方实现和文档，再对照当前源码。在线 [Cheshire软件手册](https://pulp-platform.github.io/cheshire/um/sw/) 与 [集成手册](https://pulp-platform.github.io/cheshire/tg/integr/)用于职责/契约；在线内容演进不代表本地已同步。CPU配置参照 [CVA6官方参数](https://cva6.readthedocs.io/en/latest/01_cva6_user/Parameters_Configuration.html)并读本地profile消费者。Ara以本地README、FUNCTIONALITIES、lane文档及RTL为准。Bender.lock的本地Path引用不能被写成已重新下载某上游版本；固定本轮提交与定向源码哈希更可靠。

## 03：启动与裸机调试

原目标是把ELF、链接、启动、异常/中断、DMA和UART/JTAG变成可执行实验。需要这套学习能力，但内容已经分布在HTML13–19、22、labs A–D、software的BUILD_AND_SDK/RUNTIME_AND_DEBUG/LIBRARIES，以及02第7节。缺的是顺序和一个统一证据入口，继续另写03容易复制并发生结论漂移。

可立即整合：C到ELF与PT_LOAD、SPM布局、JTAG载入、默认ROM路径、应用crt0、UART/事件、只读介质的条件步骤，按失败阶段索引现有材料。可以编写实验说明和预期结果，但本轮已有例子不应重复造生产驱动。DMA只能说明门槛和机制，非零PlatformRom例必须标S01-B01阻塞；DDR程序依赖内存就绪条件。

缺少的具体输入：E01提供固定CPU profile/真实decoder/Ara清单及新目录布局；S01提供启动栈/链接/装载约定与B01修复授权后的产物；V01提供有效target及正常/注错日志。M01提供DDR可用区与缓存契约，P01提供平台复位/时钟就绪；I01仅在扩展设备实验时参与，不阻塞SPM文档。文档整合可立即做；实验叙述可立即写；实际SoC执行须先核对环境和单项授权；工程代码修复不包含在文档Prompt中。

### 与现有“03平台配置”的区别

[03_Platform_ROM_Clock_IP_Configuration.md](03_Platform_ROM_Clock_IP_Configuration.md)记录用户确认的安全PLL启动方向、运行配置接口、Platform ROM边界及B01修复验收。它是平台决策/工程约定，不是计划中的裸机学习实验。必须原名保留、独立引用，不能用03启动教程覆盖它。建议将00原六篇保留为“历史规划主题”，通过映射指向现有载体；若以后确需新启动文件，采用无冲突的 `software/BAREMETAL_LAB_GUIDE.md`，无需重新抢数字03。本轮仅给方案，未创建占位文件。

## 04：CVA6、Ara和存储系统

原目标仍有必要：理解CPU/Ara协作、向量编程、MMU/cache和性能。本轮已将24–26实际优化，02/03、11和12分别提供CPU基础、配置、cache/SPM及DDR；configuration的CPU/Ara字段、software的ABI/启动说明和02第3/7/8节提供工程边界。无需另写同内容04。

立即可做是独立复审本轮连续数组案例、参数/状态表、端口与协作过程，补最小缺失的交叉链接。实验E源码/构建入口已存在，归约/尾部/三编程入口可以解释；运行时序、AXI错误和加速比不能由文档静态推导。OSSupport与MMU端口存在不能当成操作系统向量上下文已经通过。

E01决定固定清单，S01确保VS/FS、ISA/ABI、栈与共享区，V01提供动态退休/Ara/AXI/结果证据，M01负责跨CPU/Ara/未来NPU内存契约。I01给出未来算子需求才谈协作性能；P01提供SRAM/时钟实现参数才谈物理频率/面积。没有这些输入不妨碍教材完整说明当前机制，但不能完成原计划的性能定位实测。建议先独立审读而非再开同章并行重写对话。

## 05：AXI、地址图与自定义IP

HTML07–10已讲地址/路由/适配，27含独立Reg任务和实验F，28/26含NPU接口与所有权；configuration有扩展字段，02第8节明确旁路方向。新的价值在于**把IP接入评审要求写成可填写契约**，不是重讲AXI五通道。

立即可写限定范围：控制寄存器访问宽度/副作用/完成/中断定义、AXI主口地址/ID/突发/背压/错误要求、重置时在途事务所有权、输入资料清单与验收矩阵。独立Reg实验可引用现有F，新增真实IP实验只能形成条件计划。不能分配最终地址、中断号、ID宽度或默认所有设备都接DMA。

缺失输入由I01/IP开发者提供：LVDS传感器型号/时序、ISP/NPU控制与数据协议、像素格式/最大帧率、DMA和并发需求；E01提供扩展端口及冻结地址基础；M01提供共享区/旁路/原子边界；S01提供驱动及完成语义；V01提供总线/中断验收环境；P01给出时钟/PAD/CDC实现限制。前两类契约可先写未知字段及其影响，工程接入必须等待资料与授权。

## 06：DDR与平台集成

HTML12、04–06、26/28已覆盖DDR读路径、训练/就绪、平台边界及旁路风险。02第8节、[M01可行性](handoffs/2026-09-22_M01_DDR_interface_feasibility.md)和现有03平台约定已有关键决策：外购接口为AXI4；CPU/Ara保留LLC，NPU/ISP旁路是需求而非已实施拓扑。不能又按历史AXI3默认加桥。

立即可写限定范围：供应商AXI4协议/位宽/ID/突发/原子支持问卷、controller/PHY/PAD责任、初始化成功到CPU可用的状态条件、SPM诊断程序的条件、缓存副本与LR/SC观察边界、验证矩阵。和05的内存契约合为一个M01文档更省重复。可提出单写者/独占buffer等候选方案，明确待决，不冻结DMA区/旁路译码。

需DDR/IP供应商经用户提供授权接口摘要：实际位宽、容量/地址、时钟/复位、初始化寄存器与训练结果、模型/许可证、可接受响应/超时、PHY/DFI边界；P01/工艺方提供PAD/电源/时序；用户确认性能与容量目标；I01提供帧流量；E01提供可改集成基线；M01/S01明确一致性与启动契约；V01提供模型环境。写文档可立即，实验计划可条件化；真实DDR实验及工程拓扑都未具备完整输入。无法板测不影响问卷/契约交付。

## 07：RTOS与Linux

原目标包括调度/上下文、DTS、固件、驱动和异构运行时。已有HTML boot后阶段、software BUILD_AND_SDK及CPU/Ara的CSR/MMU说明只能提供定位，不能替代系统教学。用户在本次补充对话中确认论文实验需要OS，原“07整体暂缓”的判断因此修订。

可立即编写：任务A→B→A的栈/上下文与调度、同步/优先级、从物理地址到保护/页表/进程空间、固件到首个Linux用户进程、同一设备在裸机/RTOS/Linux中的调用与缓冲交接。以版本明确的官方参考实现解释机制，再列本地能力差距；参考选型不等于产品选型。完整解释进入HTML，工程配方和详细工具用法与software分工。实验机制与条件说明可立即写，不能伪造本平台命令或结果。

本平台移植及运行仍需用户/系统负责人确定RTOS项目/版本或Linux内核/BSP/用户空间、启动介质、RAM、特权/实时要求、必须设备及向量上下文策略。S01核官方port/固件/工具链/DTS，E01提供平台基线，M01/供应商提供存储契约，V01提供控制台/定时/中断/启动环境，I01/P01按设备和物理条件参与。缺这些输入只阻塞对应工程落地，不阻塞原理和官方参考教学。

**RTOS/Linux不是E01固定裸机ASIC提取的强制前置**。新的L01-OS Prompt仅授权文档实施，见[系统教材深化规划](L01_System_Textbook_Revision_Plan_2026-10-08.md)；OS移植、运行验证和工程修改必须另行明确授权。

## 08：ASIC迁移与验证

02已有提取规格/静态清单/版权与本地差异/验收范围；HTML30和04–06、configuration、现有03平台约定覆盖存储映射、时钟复位、平台启动。不应另写第二份冲突的提取规格。

立即可写限定范围：定向技术单元盘点（XPM/MIG/MMCM、tc_sram、ROM、clock gating/reset、PAD、USB/DDR PHY）、每类替换必须保持的接口/延迟/字节使能语义、CDC/RDC/DFT/MBIST和等价/回归交付责任，以及输入缺口。k+1/k+2 SRAM例可链接HTML30，ASIC证据分阶段写清。

E01负责实际提取与filelist，V01负责功能/时序语义回归，S01负责ROM/软件契约，M01负责DDR系统边界，I01负责新增IP可综合/复位契约，P01主责工艺适配。用户/工艺与IP供应商需提供受控PDK库、SRAM宏规格、PAD/ESD、电源、时钟/PLL、DFT策略、EDA工具/许可证与签核目标。没有这些只能写接口模板和检查方案，不能给假宏、假时钟约束或声称综合/物理实现就绪。真实工程替换另行授权。

## 工作组织建议

先做L01-S软件主线，再接L01-OS系统教学；L01-ASIC深化HTML机制，M01-D/P01-D分别编工程契约和适配验收手册，不能用手册替代正文。04由既有成果的独立复审承接。文件所有权、依赖与新S/OS/ASIC Prompt以[系统教材深化规划](L01_System_Textbook_Revision_Plan_2026-10-08.md)为准；M/P/R的完整任务块仍可见[原后续Prompt](L01_Next_Tasks_Prompts_2026-10-08.md)。共享状态/导航/生成页由L01-O串行汇总，不自动启动并行Agent。
