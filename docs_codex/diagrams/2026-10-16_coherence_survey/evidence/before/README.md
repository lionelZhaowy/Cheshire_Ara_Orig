# 工程接口与 ASIC 适配参考

返回[文档入口](../00_README.md) · [Agent 检索指南](../AGENT_DOCUMENTATION_GUIDE.md)

此目录保存现行工程契约与适配要求，不是历史日志，也不是已经实现的硬件。任务编号表示责任归属，不作为学习章节顺序。

| 文档 | 负责任务 | 查什么 |
| --- | --- | --- |
| [IP 与 DDR 接口契约](IP_DDR_Interface_Contract.md) | M01，关联 I01/E01/S01/V01 | DDR/GB/设备接入、缓存和原子观察域、初始化、接口输入、验证责任；近期需求见第 12 节 |
| [DDR–GB 缓存一致性](Cache_Coherence_Architecture.md) | L01 分析，供 M01/I01/S01/V01 评审 | 双向搬运条件、脏行/部分写/在途竞争、三类架构比较与可编辑图；方案未选型、未实现 |
| [边缘大模型推理的操作系统选择](Edge_LLM_OS_Selection.md) | L01 分析，供 S01/I01/M01/V01 评估 | 裸机/RTOS/Embedded Linux 对比、模型与 KV 内存、推理协作和当前工程缺口；含可编辑图，产品 OS 尚未选定 |
| [ASIC 适配与验收证据](ASIC_Adaptation_and_Evidence.md) | P01，关联 E01/M01/S01/V01 | SRAM/ROM、时钟复位、PHY/PAD、DFT 所需语义和资料、验收边界 |

2026-10-11：两份原 M01/P01 顶层文件按职责迁入，去掉文件名任务前缀，正文任务归属和历史版本保留。引用已更新，旧路径见 [path_migrations.json](path_migrations.json)。未更改工程参数、实现状态或验证结论。

配合[02 提取规格](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)与[03 平台配置约定](../03_Platform_ROM_Clock_IP_Configuration.md)使用；具体执行权限仍由当前用户请求确定。
