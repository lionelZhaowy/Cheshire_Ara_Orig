# L01 / Cheshire ASIC PLL 接入边界核查

## 基本信息

- 日期：2026-10-06；任务 L01。
- 用户授权：阅读当前源码及官方资料，确认 ASIC 集成中是否预留 PLL IP 替换位置。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `5ddec4fb4e982b460b12c3f3587523807602d5d4`；已有未跟踪 diagrams/、tools/ 及同日交接保留。
- 状态：静态核查与答疑完成；PLL 实施及工艺验证未开展。
- 负责路径：仅本交接，无共享配置、RTL、脚本、教材修改；未提交 Git。

## 已确认事实

1. `hw/cheshire_soc.sv:26` 直接接收 `clk_i/rst_ni/test_mode_i/rtc_i`，101 行另有 `usb_clk_i/usb_rst_ni`；无专用 PLL 参考输入、锁定输入、控制输出或可替换 PLL 实例。
2. `cheshire_soc.sv:265` Crossbar、661 行 CVA6、827 行 Ara 均接同一系统 `clk_i/rst_ni`。PLL 输出可在上层接入该端口，CPU/Ara 分域不是当前默认能力。
3. `target/xilinx/src/cheshire_top_xilinx.sv:144` IBUFDS 接参考输入，152 行 `clkwiz` 生成系统与 USB 时钟；525 行 `i_cheshire_soc` 连接 `soc_clk`。`clkwiz.locked` 悬空，213 行 rstgen 只依据外部/VIO 复位同步释放，未纳入 PLL 锁定放行。
4. `target/xilinx/scripts/impl_ip.tcl:18` 创建 Xilinx clk_wiz 6.0 并配置 MMCM 参数，是 FPGA 平台实现，不是 ASIC PLL 的通用替换模板。
5. 根 `target/` 及 `Bender.yml` 提供 simulation/Xilinx 平台；未发现当前工程交付的 ASIC chip wrapper 或 PLL 宏。定向搜索根 `hw/target/docs/Bender.yml`，以及本地 `tech_cells_generic` 的 RTL/FPGA 文件、配置包和 SoC 寄存器定义，未发现内置 PLL/FLL 控制方案。
6. `tech_cells_generic/src/rtl/tc_clk.sv` 提供 gate/buffer/mux 等基础单元，不含 PLL 模型；其 64 行明确警告 `tc_clk_mux2` 不保证无毛刺。不能把基础单元映射等同于 PLL 适配完成。
7. `hw/cheshire_pkg.sv:118` 的 `RegExtNumSlv/RegExtNumRules/RegExtRegion*` 与 `cheshire_soc.sv:432` 外部 Regbus 连接，是可供平台 PLL 控制器使用的通用扩展口，不是现成 PLL 寄存器。
8. `Cfg.PlatformRom` 为外部平台 ROM 地址。`hw/bootrom/cheshire_bootrom.S:59` 先处理 LLC BIST/SPM，80 行起按 PLATFORM_ROM 非零跳转；C 入口随后按 RTC 测量系统频率。平台 ROM 可配置时钟，但必须先具备足以执行这些步骤的有效系统时钟和可达控制路径。

## 官方文档对照

- [SoC Integration](https://pulp-platform.github.io/cheshire/tg/integr/) 将 clock sources、IO pads、memories、PHYs 列为周边平台资源，并说明 platform ROM 可进行启动设置。此表述与仓库 `docs/tg/integr.md:78` 一致。
- [Targets](https://pulp-platform.github.io/cheshire/tg/) 说明 ASIC 目标可以由外部仓库提供，内置文档目标为 simulation/Xilinx，与本地 `docs/tg/index.md` 一致。
- [Software Stack / Boot Flow](https://pulp-platform.github.io/cheshire/um/sw/#boot-flow) 说明 LLC 初始化后调用平台 ROM，与本地启动汇编一致。
- 官方页面反映当前上游，未视为本地依赖版本；当前实现结论以本地 HEAD 和上述文件为准。官方列举的 Basilisk/Carfield 仅作外部集成实例；本轮未审计它们的完整时钟实现，不将其能力归入本地工程。

## 结论及建议

- 结论：有明确的时钟输入和平台集成边界，可在 SoC 外接 55 nm PLL；没有预置的、填入供应商宏便完成的专用 PLL 插槽/时钟控制器。
- 建议，尚未实施：新 ASIC chip wrapper 管理参考时钟/PAD、PLL 宏、旁路及测试时钟、启动/失锁处理与各域复位；系统输出接 clk_i，USB 如保留则接相应时钟输入。
- 若需要软件重配，用外部 Regbus 接平台控制器并配置地址规则，跨域访问需自行实现。固定硬件配置与软件启动配置是两种方案，不默认要求都实现。
- PLL 启动可选硬件锁定后放行，或先由有效安全时钟运行平台软件再切换；不能让 CPU 先依赖尚未启用的 PLL 再要求它执行启用代码。
- 主 SoC 新频率作用于 CPU/Ara/互连等；NPU/ISP 分域、DDR 时钟及 CDC、动态调频和测试方案需另外设计。具体 55 nm PLL 宏未提供，不能确认频率、输出、锁定或电源行为。

## 验证与下一步

- 仓库根目录运行 git 状态/提交/分支只读检查，`rg` 定向搜索、`nl -ba`/`sed -n` 阅读源码和文档，并读取官方页面。
- 未编译/仿真/综合/STA/板测；本轮未实现 PLL。
- 最小下一步：P01 在取得具体 foundry/PDK、PLL datasheet 和交付视图后定义时钟/复位契约，E01 提取时保留工艺无关 SoC 与 chip wrapper 边界，再由验证任务覆盖锁定、旁路、失锁及复位场景。
- 无已实施架构事实变化，不需修改共享状态或任务表。

## 同日后续：系统域及 PLL 启动依赖

- 用户追问 CPU/Ara/Crossbar 是否同频，以及 PLL 未启动时 Boot ROM 的时钟来源。
- 源码确认：Crossbar/CVA6/Ara/LLC 使用同一 clk_i；UART（1351 行）、I2C（1388 行）、SPI Host（1453 行）、CLINT（1231 行）也接 clk_i。低速串行引脚速率不能推导为独立低频内部时钟域。USB PHY、Link 接收、平台 DDR 属另外的接口边界。
- Boot ROM 是指令存储及访问逻辑，执行者是 CVA6。`cheshire_soc.sv:1303` ROM 响应寄存器也使用 clk_i；仅让 PLL 控制寄存器位于参考时钟域，不会使没有时钟的 CPU 或 Regbus 自动发起配置。
- 复位补充：异步复位置位不必等待时钟；同步释放、同步复位、寄存器写入及启动状态机推进需要有效时钟。当前 rstgen_bypass 的 53 行异步清零、56 行起靠采样时钟移入 1，体现置位/释放区别。PLL 模拟/POR 规则须按供应商资料确认。
- 未实施候选 A：参考时钟驱动独立平台启动 FSM，以固定值/strap/可用配置源初始化 PLL；CPU 保持复位，PLL 稳定后在目标域同步释放，再执行 Boot ROM。外部 Regbus 此时可以只是后续软件访问入口。
- 未实施候选 B：上电默认旁路，参考时钟或安全分频输出驱动整个 Cheshire 主域；CPU 执行内置 Boot ROM 并调用 Platform ROM，软件写 PLL 寄存器并等待锁定，由平台时钟控制器安全切换主域至 PLL，然后继续启动。切换不能使用未经验证的组合 mux/软件直接切 sel，且切换后控制路径仍须可用。
- `Cfg.PlatformRom` 钩子位于 LLC BIST/SPM 初始化后、C 入口前；安全启动时钟必须满足前段 CPU/互连/ROM/LLC 访问。当前钩子未自带 PLL 程序，当前 Xilinx wrapper 也没有上述旁路启动流程。
- 如果 PLL 控制器保留参考时钟域，切换后的 SoC Regbus 与其关系需要有效的跨域协议或已证明的相关时钟时序；lock 等状态亦需适当同步。不能靠“同为一个晶振来源”直接省略验证。
- 当前 FPGA RTC 分频源为 soc_clk（wrapper 445 行），启动测频以 RtcFreq 为依据（bootrom.c:75）；ASIC 采用旁路/调频时须明确稳定 RTC 来源，不能无条件照搬该分频与固定 RTC 频率值。
- 本轮仍为静态核查和官方 Platform ROM 文档对照，未修改生产代码或实施上述方案。
