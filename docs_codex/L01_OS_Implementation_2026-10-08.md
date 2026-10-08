# L01-OS：RTOS/Linux 系统教学实施

日期：2026-10-08。输入分支 `mp/ara-pulp-v2`，HEAD `459f9d6f5748e39063f7bb67e959c2f27859915d`。本轮用户已明确授权多个 Agent 实施教材；本子任务仅拥有四页 OS 正文、一页诊断、自己的报告/证据/交接，导航与生成由主管 Agent 统一处理。

## 修改前后与覆盖

开始时五个同名正文均不存在；没有覆盖既有正文或另一个 Agent 的修改。前置章节由 L01-S 实施，锚点已协调。

| 页面 / 教学任务 | 修改前的缺口 | 本轮实际内容 | 可复述/完成的验收与答案位置 |
|---|---|---|---|
| [rtos](learning/rtos.html) / RTOS 调度、上下文与同步 | 只有 OS 名称和未来选型问题，缺完整任务切换 | 两份栈/TCB，A→B→A，tick/yield/事件，137 元素消息闭环，再引入同步与 FP/RVV | 画出暂停与恢复对象；解释 B 阻塞后谁运行；`#state-and-stack`、`#switch-walk`；消息成功/算法成功区别在 `#queue-example` |
| [virtual-memory](learning/virtual-memory.html) / 虚拟内存、保护与设备地址 | 链接地址、物理缓存与未来 OS 地址空间脱节 | 物理对象→保护→Sv39 页表→两个地址空间→正常缺页→设备 DMA 地址 | 推导 VA 0x40001008 的三级索引和 PA 0x80021008；同指针 A/B 的 11/22/11；`#translation-walk`、`#two-spaces`、`#address-exercise` |
| [linux](learning/linux.html) / Linux 启动与用户程序 | ZSL/固件/内核/rootfs 容易堆成一条名词链 | 本地候选启动链逐阶段输入输出，内核到 PID 1，DTS 职责，完整标量用户程序及版本边界 | 复述 ROM/ZSL/SBI/加载器/内核/init/应用的责任；区分各阶段输出；`#firmware-to-kernel`、`#kernel-to-init`、`#user-program` |
| [os-devices](learning/os-devices.html) / 裸机、RTOS 与 Linux 的设备使用 | 设备机制与 OS 服务之间没有共同实例 | 同一结果文本的三个完整使用过程；所有者/队列/TTY/ISR/缓冲/关闭及五个完成点 | 区分基址、fd、用户指针和 DMA 地址；沿真实函数名解释一行文本；`#baremetal-uart`、`#rtos-uart`、`#linux-uart`、`#completion-check` |
| [os-debug](learning/os-debug.html) / OS 启动、描述与上下文诊断 | 正常教学不应反复插入缺陷核查 | 只收录本地启动输入、DTS、UART 注记、向量配置与运行门槛；回链既有诊断 | 从最后已确认交接找缺失输入；`#boot-inputs`、`#description`、`#vector-context` |

均按正文完整过程编写；不是占位页、只有目标/小结的扩写或寄存器百科。未建立新的图资产，状态/地址推演用正文内文本示意，明确不是实测波形。已有外设/Ara 图、PPTX、历史证据和旧锚点未修改。

## 事实来源与关键边界

- RTOS 采用官方 FreeRTOS Kernel **V11.1.0** 的 GCC/RISC-V `portASM.S`、`portContext.h`、task/queue/semphr 头文件作为教学参考。不是产品选型，没有下载或修改工程依赖。通用 port 默认基本整数状态，额外状态通过 chip-specific 宏；不宣称本地已有 FP/RVV RTOS port。
- 本地 Ara SDK 存在完整展开的 Linux **6.5.0** 源码，可读 `switch_to.h`、`vector.h`、`vector.c`、TTY/8250、DMA 文档及 init。应修正“本地没有 OS 材料”的笼统表达。**源码存在不等于某个本地镜像的版本溯源成立，也不等于已运行。**
- SDK 普通 RV64 配置请求 **v5.10.7**，V 配置请求 **v6.5**；OpenSBI 版本头声明 **0.9**。Linux 6.12 官方启动文档仅作注明版本的补充，正文以本地 6.5 实现落点为主。
- `linux64_V_defconfig` 的 `RISCV_ISA_V_DEFAULT_ENABLE=y` 缺 `CONFIG_` 前缀；已有展开 `.config` 则确实含 `CONFIG_RISCV_ISA_V_DEFAULT_ENABLE=y`。两项均记录，未把模板拼写直接推断成实际运行未开启，也未修改配置。
- cheshire.dtsi 的 CPU ISA 未含 V，50 MHz/1 MHz、1 GiB RAM、UART `reg-io-width=4` 都是文件描述；必须与实际 profile、板级、RAM 和驱动契约核对。裸机 UART 使用 reg8，不能用 DTS 注释“only 32-bit access”否定本地已有访问事实。尚未动态验证哪种 Linux 访问适用。
- 既有 Platform ROM、iDMA、Ara 门槛保持；`uart_write_flush` 顺序 TODO 是源码注记，未被本轮复现为硬件故障。正常使用语义保留正文，细节集中诊断。
- `measurement#boundaries/#observation/#repeat` 已全文复核：与 OS 页共同区分队列接受、设备完成、对端正确、内核/端到端窗口。用户地址到设备地址和平台一致性边界相符，无需改主管正文。

## 示例等级

| 示例 | 当前可做 | 未做/解锁输入 |
|---|---|---|
| A→B→A、137 元素队列 | 机制推演、数学结果与 API 对照 | 本地 RTOS port/BSP/config、S01 集成与 V01 运行 |
| Sv39 地址推演 | 纸面映射；Python 校验索引/偏移算术 | 实际页表/OS/RAM、目标访问观察 |
| Linux 137 元素 C 程序 | 阅读完整 C、推导 sum=28085/errors=0 | Linux 用户工具链/库/根文件系统/部署与运行环境 |
| UART 裸机链 | 静态读真实 API | 既有运行证据按原记录；本轮未重跑 |
| RTOS 日志/IRQ、Linux fd/write/drain | 明确前提的连续机制与条件片段 | 所用 port/驱动/设备节点/配置/接收端及目标验证 |

## 文档检查

证据目录：[learning/evidence/system-implementation-20261008/os](learning/evidence/system-implementation-20261008/os/README.md)。作者检查五页唯一 H2/H3 id、内容链接/源码路径、数学推演及差异；生成、全站链接、浏览器由主管汇总，不能用作者静态检查提前称已发布验收。

没有运行 OS、用户目标程序、目标编译、RTL 仿真、综合、板测或性能测量。没有编写或修复 port/BSP/驱动，没有修改配置、地址图或生产构建入口。

## 衔接与后续

建议顺序：软件/ABI→traps→事件→RTOS→虚拟内存→Linux→OS 设备；FP/RVV 上下文同时向 Ara/共享内存提供回链，首读可暂留其进阶段。导航章号由主管生成，正文不硬编码章号。

S01 提供产品 OS/固件/工具链/用户空间、真实 DTB 和 port 支持；E01/M01 提供平台/RAM/一致性契约；V01 验证整数任务与启动，再验证 FP/RVV 抢占、设备和结果。用户/论文负责人确定工作负载和测量目标。缺这些输入限制工程实验，不阻止本轮原理教学交付，OS 不是 E01 提取前置。
