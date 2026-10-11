# L01 / 软硬件分层图方案复核

## 基本信息

- 日期：2026-10-09；输入分支 `mp/ara-pulp-v2`，HEAD `278434024`。
- 用户授权：复核分层方案并讨论，明确要求同意后才实际绘图。
- 状态：完成静态复核；图稿方案待用户确认，未生成 SVG/PPTX。
- 已读取 `svg-pptx-diagrams/SKILL.md`，后续绘制按该技能执行。
- 本轮仅新增本记录；已有 M01 文档修改、交接和图示目录保留。

## 复核结论

- 上一方案把功能依赖、启动时序、构建输入与物理实现混在纵向层次中，需要修正；文件/目录是否独立不能单独决定架构分层。
- 应用本身也是软件。图中宜称“应用软件”和“基础软件”，并保留基础软件内部的通用功能、器件协议及 IP 接口职责区别。
- `printf.c:149,862` 经 `_putchar` 输出，`sw/lib/dif/uart.c:67` 接到 UART；`gpt.c:14,22` 经 read 回调访问介质，体现可复用功能对低层接口的依赖。
- `sw/lib/crt0.S:24,42,46,114` 建立栈/异常入口、清零 BSS 并调用 main，属于启动与运行支持；`sw/link/spm.ld:9-42` 为链接输入。它们不能作为每次 HAL 调用的必经上层。
- `sw/lib/hal/uart_debug.c:33-34` 还存在 HAL 直接 MMIO 访问，因此 HAL→DIF→MMIO 是主要职责/常见路径，不是强制封闭层。
- 软件/硬件边界包括 ISA、CSR/特权机制、内存与 MMIO 地址语义、异常/中断；MMIO helper 属于软件，实现方式是 CPU 执行访存指令。
- `hw/cheshire_soc.sv:646-682,802-836` 确认 CVA6 与 Ara 的专用请求响应连接，Ara 另有 AXI 访存口；向量计算不能统一画成 MMIO 启动外设。
- FPGA/ASIC 是实现维度，片外 DDR/Flash/SD 是连接对象，应在图中分开。软件函数调用、CPU执行及硬件事务连接需明确区分。

## 修订建议（未获用户确认）

- 主图由上到下：应用软件、基础软件、软硬件接口标注带、SoC 硬件、片外器件。
- 基础软件内部展示通用功能、器件/协议 HAL、IP 接口 DIF、MMIO 工具的职责及代表性依赖；lib 用归档注记。
- 启动/运行支持、主机构建工具和 FPGA/ASIC 实现分别置于侧边，不作为共同调用链的纵向层。
- OS 按可选执行环境独立标注，不把 Linux 接到现有裸机 HAL 上；未来 IP 与目标 OS 运行状态保持原有未验证边界。

## 证据与验证

- 命令：`git status --short`、`git rev-parse --short HEAD`，`nl -ba`/`sed` 定向读上述源码，`rg` 查 printf 及本地 OS 教材。
- 官方概念补充：[RISC-V 20240411 非特权规范引言](https://docs.riscv.org/reference/isa/v20240411/unpriv/intro.html)、[OpenTitan DIF 说明](https://opentitan.org/book/doc/contributing/sw/device_interface_functions.html)。用于接口和职责概念，不推导本工程符合该规范全部扩展，也不把 OpenTitan master 当成本地依赖版本。
- 仅静态复核；未编译、未仿真、未板测，未绘图。无生产接口或项目状态变化，未提交。

## 下一步

- 等待用户确认图稿范围与修订方案，然后读取技能 SVG 子集约束并在新目录绘制、导出和验证。
- 本轮无需更新共享项目状态或任务表。
