# L01 / VCU118 系统频率与锁定后复位放行确认

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09；任务 L01；用户要求确认 VCU118 Cheshire/CVA6 系统频率，以及启动前稳定时钟的保证。
- 输入：`mp/ara-pulp-v2`，HEAD `278434024`；已有初始化图与答疑交接未跟踪，保留。本轮只新增此交接，未提交 Git。
- 状态：源码和历史生成 IP/时钟报告核查完成，未实现复位改动或重新板测。

## 频率证据

- `target/xilinx/scripts/impl_ip.tcl:91` VCU118 分支使用 250 MHz 输入，106 行请求 CLKOUT1=50 MHz，输出名称 clk_50。
- `target/xilinx/constraints/vcu118.xdc:15` 输入周期4 ns，20行系统周期20 ns，对应50 MHz。
- `cheshire_top_xilinx.sv:152` clk_50→soc_clk，525行 soc_clk→cheshire_soc.clk_i，SoC同域CVA6/Ara/互连均由该输入驱动。
- 既有 `build_ara/vcu118.clkwiz/clkwiz.gen/sources_1/ip/clkwiz/clkwiz_clk_wiz.v` 采用 MMCME4_ADV，DIVCLK_DIVIDE=5，CLKFBOUT_MULT_F=24，CLKOUT0_DIVIDE_F=24，输入周期4 ns。计算250×24/(5×24)=50 MHz；VCO为1200 MHz，不能把它或250 MHz输入视为CPU时钟。
- 既有 `build_ara/vcu118.cheshire/clocks.rpt:31` 列出 clk_50_clkwiz 周期20 ns；报告由 Vivado2022.1生成，报告日期2026-04-10。它是历史静态报告，不是本轮测量，也未核对当前板上bitstream与它的对应关系。

## 启动保证的实际缺口

- 当前 top 的 clkwiz.reset 固定0，locked 输出悬空。sys_rst只来自板级复位及VIO；rstgen在soc_clk域同步释放，不输入locked。
- common_cells rstgen_bypass 默认NumRegs=4。在正常模式和已有效置位复位的前提下，外部复位撤销后靠soc_clk边沿移入1释放；这不是MMCM锁定判断。
- 已有 XCI 的 USE_SAFE_CLOCK_STARTUP=false、USE_CLOCK_SEQUENCING=false；生成 primitive 的 STARTUP_WAIT="FALSE"，clk_50经普通BUFG输出。既有IP内也未看到以locked控制该输出的安全启动缓冲机制。
- 所以当前路径不能证明“每次CVA6开始执行都在MMCM已锁定之后”。已有HelloWorld仅说明历史具体运行建立了可执行条件，不能扩大为所有上电/复位/失锁情况已验证。
- 模块具体为MMCM而非这里另有ASIC PLL。用户所说硬件初始化，指其由bitstream配置后自行锁定，不是主SoC时钟的ASIC配置状态机。

## 官方建议与后续验证方向

- [AMD UG949 MMCM/PLL 使用建议](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Using-Clock-Modifying-Blocks-MMCM-and-PLL)要求把LOCKED用于复位实现、同步处理相应使用，并建议暴露调试状态；可靠时钟控制RST。在线页面为2026.1，作为通用建议；本地具体IP行为以Vivado2022.1生成的6.0配置/RTL为据。尝试访问2022.1同页返回不可读取，未声称读到了该版页面。
- 建议，未实施：将locked接入经过验证的复位/时钟就绪管理，未锁定保持SoC复位，稳定后在系统域同步释放，失锁按规定处理。不能把裸组合式钟门控或Boot ROM轮询当启动前保护。
- 接入可读/可观测锁定状态，使用稳定参考域采样PLL锁定、复位及CPU执行事件，验证未锁时rst_n不放行；正常软件阶段读取状态只能证明当时锁定，不能独立证明最早执行时刻。
- 当前FPGA RTC由soc_clk分频50并声明1 MHz；core_freq算法使用该声明和mcycle/mtime比值，不能将共源RTC测频当独立的真实绝对频率测量或PLL锁定证明。物理频率需独立参考或测量仪器；此处尚未执行。
- MMCM锁定与DDR训练完成是独立条件，本轮没有因此宣称DDR路径验证通过。

## 验证与下一步

- 执行Git状态/版本检查、rg/nl定向读取、官方文档检索；没有Vivado重建、RTL运行、板测、ILA新增或源码修复。
- 后续V01/P01针对时钟建立、复位释放、外部重置及失锁做验收；实现改动需另行授权并保留旧FPGA入口。
- 当前锁定放行缺口与先前记录一致，没有关闭任何任务；新增生成IP证据仅写本交接，不覆盖共享状态。
