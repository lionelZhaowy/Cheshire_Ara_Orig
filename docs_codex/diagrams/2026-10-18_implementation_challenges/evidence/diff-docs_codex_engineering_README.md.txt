--- before/docs_codex/engineering/README.md
+++ docs_codex/engineering/README.md
@@ -8,6 +8,7 @@
 | --- | --- | --- |
 | [SoC 架构 v1：项目目标、改动范围与实施总纲](SoC_Architecture_v1_Master_Plan.md) | L01 整合，供 C00/E01/M01/I01/P01/S01/V01 接手 | 2026-10-18 用户确认的功能架构基线、第 9 页当前配图、需求/模块/阶段验收映射与历史冲突；工程待实现/待验证 |
 | [三人团队分工与 2027 年投片排期](Team_Responsibilities_and_Tapeout_Schedule.md) | C00 协调，队长/HYH/TTY 使用 | 人员主责、前后端分工、月度排期、验收与进度对照；区分 6 月投片期望、6 月前端检查建议和 9 月条件目标 |
+| [实施难点、未决问题与关闭条件](Implementation_Challenges_and_Open_Questions.md) | L01 整合，供各工程任务关闭 | 13 类难点、已有讨论/初步方案、责任与阶段门槛、验收证据；配套 13 幅可编辑图，不表示工程已验收 |
 | [IP 与 DDR 接口契约](IP_DDR_Interface_Contract.md) | M01，关联 I01/E01/S01/V01 | DDR/GB/设备接入、缓存和原子观察域、初始化、接口输入、验证责任；近期需求见第 12 节 |
 | [DDR–GB 数据同步设计](DDR_GB_Coherence_Design.md) | L01 说明，供 M01/I01/S01/V01 评审 | 主要讲解入口：从裸机推理解释数据版本、输入输出维护、HAL 调用、硬件扩展与开销；接口及硬件待实现 |
 | [DDR 供应商会议问题](DDR_Supplier_Coherence_Questions.md) | L01 整理，供 M01/S01/V01 使用 | 跨端口读写例子、错误及部分写入、停止／复位队列范围；待供应商答复 |
