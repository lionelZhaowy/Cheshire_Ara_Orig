# 工程接口与 ASIC 适配参考

返回[文档入口](../00_README.md) · [Agent 检索指南](../AGENT_DOCUMENTATION_GUIDE.md)

此目录保存现行工程契约与适配要求，不是历史日志，也不是已经实现的硬件。任务编号表示责任归属，不作为学习章节顺序。

| 文档 | 负责任务 | 查什么 |
| --- | --- | --- |
| [IP 与 DDR 接口契约](IP_DDR_Interface_Contract.md) | M01，关联 I01/E01/S01/V01 | DDR/GB/设备接入、缓存和原子观察域、初始化、接口输入、验证责任；近期需求见第 12 节 |
| [DDR–GB 数据同步设计](DDR_GB_Coherence_Design.md) | L01 说明，供 M01/I01/S01/V01 评审 | 主要讲解入口：从裸机推理解释数据版本、输入输出维护、HAL 调用、硬件扩展与开销；接口及硬件待实现 |
| [DDR 供应商会议问题](DDR_Supplier_Coherence_Questions.md) | L01 整理，供 M01/S01/V01 使用 | 跨端口读写例子、错误及部分写入、停止／复位队列范围；待供应商答复 |
| [DDR–GB 缓存一致性原规划](Cache_Coherence_Architecture.md) | L01 分析，供 M01/I01/S01/V01 评审 | 保留此前方案比较、接口讨论及证据；完整阅读路线见上面的数据同步设计 |
| [CPU–NPU 缓存一致性方案综述](CPU_NPU_Cache_Coherence_Survey.md) | L01 资料研究，供 M01/I01/S01/V01 评审 | 七组工业与学术案例、四张原文配图；比较一致性覆盖、缓存分配、本地 SRAM 和软硬件职责 |
| [边缘大模型推理的操作系统选择](Edge_LLM_OS_Selection.md) | L01 分析，供 S01/I01/M01/V01 评估 | 裸机/RTOS/Embedded Linux 对比、模型与 KV 内存、推理协作和当前工程缺口；含可编辑图，产品 OS 尚未选定 |
| [CPU＋NPU 模型推理体系调研](CPU_NPU_Inference_Systems_Survey.md) | L01 资料研究，供 S01/I01/M01/V01 评估 | 七组工业与学术方案的编译、运行时、驱动、计算及数据交接；重点分析 LLM，含四张可编辑图 |
| [ASIC 适配与验收证据](ASIC_Adaptation_and_Evidence.md) | P01，关联 E01/M01/S01/V01 | SRAM/ROM、时钟复位、PHY/PAD、DFT 所需语义和资料、验收边界 |

2026-10-11：两份原 M01/P01 顶层文件按职责迁入，去掉文件名任务前缀，正文任务归属和历史版本保留。引用已更新，旧路径见 [path_migrations.json](path_migrations.json)。未更改工程参数、实现状态或验证结论。

配合[02 提取规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)与[03 平台配置约定](../03_Platform_ROM_Clock_IP_Configuration.md)使用；具体执行权限仍由当前用户请求确定。
