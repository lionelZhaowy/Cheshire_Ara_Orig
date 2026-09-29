# L01 机制讲解与维护完善 · 2026-09-29

保留七篇/30章，落实[复审 F1–F6](../handoffs/2026-09-29_L01_structure_revision_review.md)。输入为 HEAD `69fabdd227e225bf9f5f0b9ec5fe9d056999fea6` 加未提交的上一轮结构修订。历史评审和证据保持原样，本次范围为教材、五张机制结构图及维护工具。

| 复审项 | 本次落实 | 阅读入口 |
| --- | --- | --- |
| F1 引用错位 | iDMA、DDR 旁路、Serial Link、模型数组语境改为主题链接；普通章号引用变成可校验链接；核查“本章/下文/上下章” | [iDMA 缺口](dma.html#lanes)、[模型边界](models.html#cooperation) |
| F2 机制不足 | 两输入×两目标同组请求推演；DDR 从 AR 到命令、PHY、R；PLL 两域和隔离/保持例子 | [Crossbar](interconnect.html#two-by-two)、[DDR](ddr.html#read-path)、[时钟](clocks.html#pll-loop)、[电源](power.html#isolation-example) |
| F3 启动组织 | Serial Link/UART/SD/NOR/EEPROM 独立 H3，共用 GPT/raw 只解释一次；Debug 先定义 DTM/DMI/DM/SBA | [启动](boot.html#other-loaders)、[Debug](boot-debug.html#transport) |
| F4 术语 | 电源术语先定义；CVA6 功能图与 scoreboard/提交/缓冲/预测资源对应；解释 generated clock/false path | [CVA6](cva6.html#functional-units)、[电源](power.html#asic-clock-power) |
| F5 证据覆盖 | 两个检查入口采用新输出目录，已存在就拒绝；只读检查和临时副本生成比较分开；寄存器生成器不再覆盖固定来源报告 | [维护入口](README.md#当前维护入口) |
| F6 编辑收尾 | 标题采用教材语气；Debug 寄存器偏移去重；CVA6、PLL、电源、DDR、Boot 增加因果自测 | 各章末尾 |

## 源码推演与教学假设

Crossbar 源码来自本地 `axi-ecdc900686449c15`。图例使用 I0/I1、T0/T1、两位 ID 和示意地址；这些不是生产配置。`i_w_fifo` 在仲裁决定有效且有容量时预留 W 来源，`lock_aw_valid_q` 防止 AW 背压时重复入队；demux 的 `w_open/w_select_q` 管理未结束 W 的目标，ID 计数分别等待 B 或最后 R 握手。端口 cut/spill 意味着内部释放与外部完成可能不在同一周期。正文按实际符号说明，未产生新的 RTL 波形。

Boot 依据 ROM、GPT 和 UART HAL：UART 的 EXEC 使用显式地址，GPT/raw 介质加载器从 SPM `code_buf` 起点调用；两者不是同一 ELF 入口解析流程。分区选择保留本地首分区回退行为和验证缺口。JTAG 等待配置位的说明保持精确，不扩大为 ROM C/测频完成。

[本次来源哈希](evidence/refinement-20260929/sources.json)用于定位本地实现。五张新图是功能、连接或数据路径图；原六张 WaveDrom 教学时序保留原内容，没有用数值表格充当时序图。DDR/PLL/电源机制属于通用教学，具体控制器寄存器、电压、频率与域划分继续待交付。

## 本次查阅的公开原理资料

以下为 2026-09-29 定向查阅，不替代本工程具体 IP 手册：

- [Intel MAX 10 Clocking and PLL User Guide，ID 683047](https://www.intel.com/programmable/technical-pdfs/683047.pdf)：检索可读的 2023-12-26 章节说明 M/N/C 频率关系；[组合手册](https://www.intel.com/programmable/technical-pdfs/max10-handbook.pdf)可见锁定容差定义。仅用于 PLL 原理，未把 MAX 10 参数移到 Xilinx 或 ASIC。
- [Microchip Optimized Access Functionality](https://onlinedocs.microchip.com/oxy/GUID-B822915F-C375-4172-91BD-AB6F326EB783-en-US-1/GUID-F3B24B38-CBB2-434E-A89A-EC8BB4810756.html)、[tRCD/tRP 字段定义](https://onlinedocs.microchip.com/oxy/GUID-82119957-1E11-4B69-84AC-EF0EA08F5595-en-US-5/GUID-3CC38BA3-A3F0-42A5-AA1C-72E98F86D154.html)、[DDR Memory 参数说明](https://onlinedocs.microchip.com/oxy/GUID-AFCB5DCC-964F-4BE7-AA46-C756FA87ED7B-en-US-21/GUID-A29420D1-4E36-4920-B9BB-DD0B63F5E787.html)：检索可见命令/时序、行保持与自刷新说明；部分网页直连返回 503，未宣称完整下载或核验其全部寄存器。本书只取通用定义，不移植编码与时序数值。
- [Synopsys Power Optimization Kits](https://www.synopsys.com/designware-ip/memories-logic-libraries/power-optimization-kit.html)及[低功耗设计白皮书](https://www.synopsys.com/content/dam/synopsys/solutions/documents/a-holistic-approach-to-energy-efficient-soc-design-wp.pdf)：隔离/电平转换及 UPF 的职责；不表示选用了这些商业库。

## 验证入口与边界

本次发布的[结构检查](evidence/refinement-20260929/checks/checks.txt)、[浏览器检查](evidence/refinement-20260929/browser/browser.txt)和[输出保护检查](evidence/refinement-20260929/output-protection.json)分别记录结果。报告目录含实际运行时间、HEAD、未提交状态及输入哈希；以后运行必须选新目录。

只读检查不更改网页；`--check-generated` 在临时副本生成并比较。旧证据/示例/资产 875 个文件及旧站 728 文件逐一校验。旧逐段审计保留为历史；本次记录实际修改的 content 哈希，不把改写段落默认为逐字保留。现有 373 条 URL 迁移继续有效。

本次没有软件构建、生产 RTL 编译/仿真、板测、性能测量或 ASIC 实施。SD 模型、NOR/EEPROM 镜像、JTAG 段尾/继承栈、DMA 桥宽及 Ara 访存错误等动态验证门槛继续保留。
