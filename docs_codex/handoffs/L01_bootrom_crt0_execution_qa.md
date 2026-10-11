# L01 / Boot ROM 与应用 CRT0 的区别和执行顺序

> 记录日期：2026-10-08。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-08；任务 L01；用户要求解释 crt0.S、cheshire_bootrom.S、cheshire_bootrom.c 的职责、联系及复位后顺序。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；开始时 git status --short 无输出。
- 本轮读取当前状态/任务表、L01 软件实施及标题最新交接，定向核查三份源码、链接脚本、构建规则、SoC 入口、载荷跳转及 JTAG VIP。
- 状态：静态答疑完成；只写本交接，未修改生产代码/共享文档，未提交 Git。

## 源码确认

1. `cheshire_soc.sv:564` 选择 BootAddr（Bootrom 开启时为 AmBrom，关闭时为 PlatformRom），664 行连接 CVA6 boot_addr_i；当前 AmBrom 为 0x02000000。
2. `cheshire.mk:139` 将 hw/bootrom 的 S/C 与 libcheshire.a 链接为 Boot ROM ELF，145 行按 bin 生成 cheshire_bootrom.sv；hw/bootrom 的 ld 把 .text._start 放到 bootrom 开头。
3. `cheshire_bootrom.S::_start` 建立早期整数环境、sp/gp、LLC BIST/SPM/栈及可选平台钩子；`_boot` 通过 call main 进入 `cheshire_bootrom.c::main`。它不是先调用 sw/lib/crt0.S。
4. ROM C 的 main 读取启动模式/RTC 并测频；0 为被动装载服务，1 为 SPI SD，2 为 SPI NOR，3 为 I2C EEPROM。主动路径经 gpt_boot_part_else_raw 加载连续代码到 SPM，再调用 ROM 汇编的 boot_next_stage。
5. `sw/sw.mk:56` 收集 sw/lib/*.S（包括 crt0.S）到 libcheshire.a；28 行使用 -nostartfiles，108 行起将各应用对象与该库链接。common.ldh 的 ENTRY(_start) 及应用 ld 的 .text._start 布局决定应用入口。Boot ROM 自身已有 _start/main，库中启动对象不因存在于 archive 就与 ROM 启动强行合并；它们是不同镜像的同名符号。
6. 应用/ZSL 若沿用根 SDK 默认入口，进入其镜像中 crt0.S::_start，然后设置或继承 sp、设置 gp、安排入口返回现场、设置 mtvec、清 BSS、初始化 FPU并调用该程序自己的 main。原 crt0 没有 .data 从 ROM 复制到 RAM 的循环，此初值由加载器放置；不按通用教材补写本地不存在的步骤。
7. `common.ldh:30` 默认 __stack_pointer$=0，spm.ld 未覆盖，因此 crt0 的条件分支可继承进入时的栈，并非每个应用自动分配新栈。配置和入口需匹配；JTAG 场景不能只证明存储可写就认为 sp 已建立。
8. crt0 的 _exit 实际写 `(返回值<<1)|1` 到 scratch2，恢复所存 sp/gp/ra 后 ret；不会因为旧注释写 wait forever 就声称指令自循环。ROM 自身 C 返回路径则为其 _exit 的 ebreak/wfi。
9. 当前原 crt0 固定执行双精度 FP 初始化；VS 未在该文件统一开启。这是入口能力边界，不把应用环境当 OS 上下文实现。
10. `vip_cheshire_soc.sv:371` 的 jtag_elf_run 装载 ELF 后写 DPC（CSR 0x7b1）并恢复 CPU，因此可以直接进入应用 _start，不要求执行 ROM C 的介质装载。ROM 仍承担复位后可能需要的片上初始化；PRELMODE 和真实入口需分别判断。

## 默认执行链与例外

默认 Bootrom=1、PlatformRom=0、内部 LLC 存在且环境有效时，自主介质路径是：硬件复位释放 → ROM 汇编 _start → _boot → ROM C main → 介质读取到 SPM → boot_next_stage → 载荷 crt0 _start → 载荷 main（例如 HelloWorld 或 ZSL）。ROM C main 与载荷 main 不在同一个 ELF 中。

PlatformRom 非零的普通返回缺陷仍存在，已登记 S01-B01；不能在当前代码中把它画成已正常返回内置启动。直接调试装载、自定义入口、禁用 Bootrom 或后续 OpenSBI/U-Boot/Linux 采用不同入口，不保证全部执行这三个文件。

## 官方对照与验证

- [官方软件栈 / Boot Flow](https://pulp-platform.github.io/cheshire/um/sw/#boot-flow)：分开 Boot ROM 的早期启动与裸机应用 C runtime；[平台钩子](https://pulp-platform.github.io/cheshire/tg/integr/#platform-rom) 为集成扩展。当前实现差异以本地源码为准。
- 本轮只运行 git status/rev-parse/branch、rg、nl/sed 及官方页面读取；未编译/未仿真/未板测，没有把历史 ELF/HelloWorld 当成本轮运行。
- 最小继续步骤：后续按所选 boot_mode/PRELMODE，用实际 ELF/map/反汇编及 PC/sp 观察各入口；S01-B01 独立授权后处理平台返回路径并重新生成 ROM。
- 没有新增实现事实或任务状态变化，无需修改共享状态/任务表。
