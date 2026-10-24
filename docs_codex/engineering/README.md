# 工程接口与 ASIC 适配参考

返回[文档入口](../00_README.md) · [Agent 检索指南](../AGENT_DOCUMENTATION_GUIDE.md)

此目录保存现行工程契约与适配要求，不是历史日志，也不是已经实现的硬件。任务编号表示责任归属，不作为学习章节顺序。

| 文档 | 负责任务 | 查什么 |
| --- | --- | --- |
| [SoC 架构 v1：项目目标、改动范围与实施总纲](SoC_Architecture_v1_Master_Plan.md) | L01 整合，供 C00/E01/M01/I01/P01/S01/V01 接手 | 2026-10-18 用户确认的功能架构基线、第 9 页当前配图、需求/模块/阶段验收映射与历史冲突；工程待实现/待验证 |
| [LVDS 像素流直通：模式、控制与实现注意事项](LVDS_Raw_Bypass_Design.md) | I01，S01/V01/P01 配合 | 2026-10-22 修订：RX 解码后绕过 ISP/DDR/ROI，TX FIFO 前选源，由 C5/TX 内寄存器控制；明确反压隔离、全帧封装、CDC/吞吐及初始化条件；已从原 v1 最小修改 PPT/预览，RTL 待实现 |
| [三人团队分工与 2027 年投片排期](Team_Responsibilities_and_Tapeout_Schedule.md) | C00 协调，队长/HYH/TTY 使用 | 人员主责、前后端分工、月度排期、验收与进度对照；区分 6 月投片期望、6 月前端检查建议和 9 月条件目标 |
| [SoC 资源预算与 WireBond 封装预规划](SoC_Resource_and_Packaging_Plan.md) | P01，关联 M01/I01，C00 汇总 | 用户确认 SMIC55 工艺标识；PAD 周长、GB/NPU 候选、面积及 SI/PI 取舍与六类可维护预算表；算例不代表冻结参数或工程验收 |
| [固定向量 SoC 资源、存储组织与配置问答](Fixed_Vector_SoC_Resource_Guide.md) | E01，供 L01/P01/V01/S01 使用 | 当前 L1/LLC/VRF 数据与标签、bank/word、寄存器与 TLB/预测器、宏替换及扩容约束；静态推导，不代表综合面积或扩容验收 |
| [DMA 控制通路、访问错误与局部修复](DMA_Control_Path_and_Fix.md) | E01，供 S01/V01 使用 | CPU/HAL/AXI/寄存器及完成编号的逐层关系；官方局部回移与实测结果，另记录默认长搬运停滞及验收边界 |
| [实施难点、未决问题与关闭条件](Implementation_Challenges_and_Open_Questions.md) | L01 整合，供各工程任务关闭 | 13 类难点、已有讨论/初步方案、责任与阶段门槛、验收证据；配套 13 幅可编辑图，不表示工程已验收 |
| [IP 与 DDR 接口契约](IP_DDR_Interface_Contract.md) | M01，关联 I01/E01/S01/V01 | DDR/GB/设备接入、缓存和原子观察域、初始化、接口输入、验证责任；近期需求见第 12 节 |
| [DDR–GB 数据同步设计](DDR_GB_Coherence_Design.md) | L01 说明，供 M01/I01/S01/V01 评审 | 主要讲解入口：已按v1共享M5、四口DDR/共享前端更新，保留16步推理时序并补LVDS输出交接；接口及硬件待实现 |
| [DDR 供应商会议问题](DDR_Supplier_Coherence_Questions.md) | L01 整理，供 M01/S01/V01 使用 | 四口实际方向的读写交接、Controller与项目共享前端责任、错误及排空/复位；Q1–Q7待答复 |
| [DDR–GB 缓存一致性原规划](Cache_Coherence_Architecture.md) | L01 分析，供 M01/I01/S01/V01 评审 | 保留此前方案比较、接口讨论及证据；完整阅读路线见上面的数据同步设计 |
| [CPU–NPU 缓存一致性方案综述](CPU_NPU_Cache_Coherence_Survey.md) | L01 资料研究，供 M01/I01/S01/V01 评审 | 七组工业与学术案例、四张原文配图；比较一致性覆盖、缓存分配、本地 SRAM 和软硬件职责 |
| [边缘大模型推理的操作系统选择](Edge_LLM_OS_Selection.md) | L01 分析，供 S01/I01/M01/V01 评估 | 裸机/RTOS/Embedded Linux 对比、模型与 KV 内存、推理协作和当前工程缺口；含可编辑图，产品 OS 尚未选定 |
| [CPU＋NPU 模型推理体系调研](CPU_NPU_Inference_Systems_Survey.md) | L01 资料研究，供 S01/I01/M01/V01 评估 | 七组工业与学术方案的编译、运行时、驱动、计算及数据交接；重点分析 LLM，含四张可编辑图 |
| [ASIC 适配与验收证据](ASIC_Adaptation_and_Evidence.md) | P01，关联 E01/M01/S01/V01 | SRAM/ROM、时钟复位、PHY/PAD、DFT 所需语义和资料、验收边界 |

2026-10-11：两份原 M01/P01 顶层文件按职责迁入，去掉文件名任务前缀，正文任务归属和历史版本保留。引用已更新，旧路径见 [path_migrations.json](path_migrations.json)。未更改工程参数、实现状态或验证结论。

配合[02 提取规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)与[03 平台配置约定](../03_Platform_ROM_Clock_IP_Configuration.md)使用；具体执行权限仍由当前用户请求确定。
