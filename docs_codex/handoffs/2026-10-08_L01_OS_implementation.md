# 交接：L01-OS / 调度、地址空间、Linux 与设备使用

## 基本信息

- 日期：2026-10-08，多 Agent 实施的 OS 子任务；用户本轮明确授权子 Agent 实施。
- 状态：五页正文与作者检查完成；由主管统一生成和全站/浏览器验收。工程移植与目标运行未实施。
- 输入：`mp/ara-pulp-v2`，`459f9d6f5748e39063f7bb67e959c2f27859915d`；已有全站修改/报告/证据与用户 diagrams.pptx 均保护。五个新正文名开始时均不存在。
- 独占：content/{rtos,virtual-memory,linux,os-devices,os-debug}.html、自己的报告/evidence/本交接。未修改公共导航、状态、生成页、其他章节或生产工程。

## 本轮结果

- 四项教学完整落地：A→B→A 与同步；Sv39/保护/进程空间/设备地址；固件到 PID 1 与用户 C；同一 UART 操作三种软件环境。
- 独立 OS 诊断只收录本地输入/描述/上下文缺口，正常机制和接口完成条件保留正文。
- 版本事实：官方 FreeRTOS V11.1.0 仅作整数 port 参考；本地 Ara SDK 普通配置请求 Linux v5.10.7、V 配置请求 v6.5、展开源码声明 6.5.0、OpenSBI 版本头 0.9。已确认本地 Linux FP/RVV 状态代码存在，未证明当前镜像/硬件匹配或安全抢占。
- 定向发现：DTS ISA 未含 V、频率/RAM 常量和 UART 访问宽度需实际平台对齐；模板用户 V 默认开关缺 CONFIG_ 前缀，但已有 .config 对应符号为 y，不能简单写成“实际未开启”。UART flush TODO 保留源码注记等级。
- 等级：上述为源码确认；数学例为教学推演；本轮实测只限文档检查。既有 Platform ROM/iDMA/Ara 缺口不关闭。

## 改动与接口

- 详见 [实施报告](../L01_OS_Implementation_2026-10-08.md)，含前后对照与读者验收。
- 新 slug/title：rtos / RTOS 调度、上下文与同步；virtual-memory / 虚拟内存、保护与设备地址；linux / Linux 启动与用户程序；os-devices / 裸机、RTOS 与 Linux 的设备使用；os-debug / OS 启动、描述与上下文诊断（参考页）。主管可按统一目录措辞登记。
- 关键锚点：rtos#switch-walk/#queue-example/#fp-vector-context；virtual-memory#translation-walk/#two-spaces/#device-addresses；linux#firmware-to-kernel/#kernel-to-init/#version-evidence；os-devices#linux-uart/#completion-check；os-debug#boot-inputs/#description/#vector-context。
- 与 L01-S 对齐 runtime#abi、traps#software-context、boot#later-stages；已完整读 traps、measurement，跨章节职责和完成条件相符。
- 配置/profile/地址/宏/中断/位宽无变化。未 Git 提交。

## 验证证据

- 仓库根运行 `python3 docs_codex/learning/evidence/system-implementation-20261008/os/check_os.py`，退出 0；五页共 72 个本地链接/锚点检查通过、H2/H3 id 唯一，137 项总和与 Sv39 推演算术通过。
- `git diff --check` 退出 0。未跟踪新页由前一脚本实际读取，不能仅依靠 git diff 验证。
- `sources.json` 记录定向源码和内容哈希，`checks.txt` 保存命令/输出/退出码；[证据目录](../learning/evidence/system-implementation-20261008/os/README.md)。
- 作者未生成根页面或运行浏览器，主管串行执行后补充总体证据。未编译/未仿真/未板测/未运行 OS。

## 决策与下一步

1. 主管按所有权合入五页导航，生成后核全站链接、手机/桌面、无脚本与旧链接保护。
2. 交叉审读四项完整过程与正常/诊断分离，读者验收答案锚点见实施报告；真实用户试读仍未进行。
3. S01 接收版本/DTB/port 输入，E01/M01 提供硬件/内存契约，V01 再做独立运行。缺失输入与解锁层次见报告。
4. 共享状态建议写“OS 原理正文已实施，本地 SDK/向量上下文源码有落点，产品选择/移植/目标验证未完成”，不写“OS 已跑通”。OS 仍不是 E01 提取前置。

最少继续阅读：根 AGENTS、实施报告、本交接、learning/README/pages.json 与五页正文；来源细节见 sources.json，无需重新扫描全仓库。
