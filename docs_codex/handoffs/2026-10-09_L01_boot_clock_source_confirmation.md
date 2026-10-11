# L01 / Boot ROM 时钟来源与 PLL 切换现状确认

## 基本信息

- 日期：2026-10-09；任务 L01；用户要求读源码确认 Platform ROM 配 PLL 之前的启动时钟、ROM 驱动时钟及锁定后切换。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；已有初始化图目录与四份同日/前日答疑交接未跟踪，均保留。
- 状态：源码/官方文档核对完成；不实施 PLL、切钟或 ROM 修复。本轮仅新建此记录，未提交 Git。

## 当前代码确认

- `hw/cheshire_soc.sv:26` 仅接收主域 clk_i；没有该主域的 RefClk 或 PLL_LOCK 输入，没有内置 RefClk/PLL 选择器。
- 661 行 CVA6 接 clk_i，1312 行 ROM 的 reg_to_mem 接 clk_i，1303 行 ROM 响应寄存器接 clk_i，1331 行 ROM 实例端口也接 clk_i。
- `hw/bootrom/cheshire_bootrom.sv:29` 内容读取由 always_comb case 译码，模块的 clk_i/rst_ni 没有参与内部存储译码；这不等于 CPU、总线和寄存响应可以无时钟运行。执行 ROM 程序的驱动时钟是 CPU 的系统 clk_i。
- `target/xilinx/src/cheshire_top_xilinx.sv:144` IBUFDS → sys_clk；152 行 clkwiz 的 clk_50 → soc_clk；525 行 SoC 的 clk_i 接 soc_clk。没有参考输入直接旁路路径，也没有 PLL 锁定后自动选择时钟的逻辑。
- clkwiz 参数由 `target/xilinx/scripts/impl_ip.tcl:18` 在生成 FPGA IP 时设置，不需要 CPU 运行 Platform ROM 才完成最初配置。locked 输出悬空；rstgen 不依据 locked 放行，不能描述为已实现完整锁定启动协议。
- Boot ROM S:59 先等待 LLC BIST/SPM/栈设置，80 行才调用 Platform ROM。因此在平台代码执行前，CVA6/ROM访问/互连/LLC 都必须已有可用 clk_i 及所需存储条件。
- rtc_i 是计时参考，不自动替代系统 clk_i。当前默认 PlatformRom=0，没有实际 PLL/DDR 初始化例程被执行。

## 结论与目标方案边界

- 在“PLL 必须软件初始化之后才有输出”的 IP 条件下，用户理解的 RefClk 先启动是合理的目标方案，但不是当前工程已实现事实，也不是 Cheshire 要求必须使用未分频的 PLL RefClk。
- 目标芯片 wrapper 可以将 RefClk 或安全分频时钟先送入 clk_i，再由 CPU 执行 Boot ROM/Platform ROM 配 PLL。PLL 输出稳定、请求完成条件满足后，由外围安全时钟控制器把同一 clk_i 的来源切换为 PLL；不另给 ROM 单独时钟。
- 如果唯一连接的是未启动 PLL 输出且无备用源，CPU 无法执行 ROM，也无法配置该 PLL；Cheshire 不会在内部解决此循环。另一可行平台是 PLL 用复位默认值/strap/硬件初始化先产生启动时钟，再让软件重配，具体按 IP 契约。
- 官方 [Platform ROM 集成说明](https://pulp-platform.github.io/cheshire/tg/integr/#platform-rom) 将时钟源作为外围平台资源，并要求内置启动所需的稳定时钟/存储条件；它没有提供通用 PLL 宏或时钟切换实现。
- 本地 clk_mux_glitch_free 可作为候选，要求切换时两源稳定、工艺时钟单元映射正确；不能单独当完整 PLL_LOCK/复位/故障控制器。
- 用户已确认的安全 PLL 启动方向仍见 03_Platform_ROM_Clock_IP_Configuration.md；S01-B01 返回缺陷尚未修复，与启动时钟来源是不同问题。

## 验证与下一步

- git 状态/版本、rg/nl/sed 定向读取及官方页面对照；未编译、未仿真、未测实际时钟或板测。
- 后续 P01 在真实 PLL 接口到位后确定默认 RefClk 旁路、POR与配置银行时钟、锁定同步及安全切钟契约；S01/V01 验证 CPU/LLC 能在启动源下执行并处理失败留在安全时钟。
- 无实现事实或授权边界变化，不更新共享状态/任务表。
