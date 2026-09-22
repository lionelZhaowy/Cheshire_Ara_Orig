# 其他模块、存储与平台配置手册

返回 [配置导航](README.md)。本页覆盖当前 SoC 集成直接相关的模块参数、生成尺寸和运行时配置入口；不穷举所有第三方 IP 的内部 debug/test 参数，也不替代外设寄存器手册。全部 SoC 开关与默认值见 [Cheshire 参数表](CHESHIRE.md)。

## 1. iDMA：按正在阅读的 cheshire_idma_wrap.sv 理解

来源：[wrapper](../../hw/cheshire_idma_wrap.sv)、[后端生成 RTL](../../.bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_backend_rw_axi.sv)、[当前软件驱动](../../sw/include/dif/dma.h)。

```text
CPU 访问 0x01000000 控制窗口
 → SoC 原子适配器 → axi_to_reg → reg64_2d 前端
 → Job FIFO → ND midend（把 2D 分解为若干传输）
 → idma_backend_rw_axi → axi_rw_join → SoC AXI xbar → 目标存储
```

DMA 控制端是“被 CPU 访问的 slave”，搬运端是“主动访问存储的 master”。因此有两组 ID 宽度和两组事务参数。

| wrapper 参数 | 默认 SoC 下实际值 | 来自哪里 / 意义 |
| --- | --- | --- |
| AxiAddrWidth | 48 | Cfg.AddrWidth |
| AxiDataWidth | 64 | Cfg.AxiDataWidth；当前前端选择 reg64 |
| AxiIdWidth | 2 | 搬运主端口 Cfg.AxiMstIdWidth |
| AxiUserWidth | 2 | Cfg.AxiUserWidth |
| AxiSlvIdWidth | 5 | 控制从端口接 xbar 输出的扩展 ID；Ara 仿真也为 5 |
| NumAxInFlight | 16 | Cfg.DmaNumAxInFlight；搬运后端事务并发 |
| MemSysDepth | 8 | Cfg.DmaMemSysDepth；存储系统深度预算 |
| JobFifoDepth | 2 | Cfg.DmaJobFifoDepth；任务描述符 FIFO |
| RAWCouplingAvail | 1 | Cfg.DmaRAWCouplingAvail；R 与 AW 耦合硬件 |
| IsTwoD | 1 | Cfg.DmaConfEnableTwoD |
| axi_mst_req_t / axi_mst_rsp_t | SoC master 类型 | 搬运端口请求/响应结构 |
| axi_slv_req_t / axi_slv_rsp_t | SoC slave 类型 | 控制端口请求/响应结构 |

wrapper 的整型/bit 默认大多为 0，类型默认为 logic；它依靠 SoC 传参，不是可直接运行的默认实例。

### 1.1 wrapper 没暴露的固定设置

| 项目 | 当前值 | 含义 |
| --- | --- | --- |
| IdCounterWidth | 32 | 软件提交/完成任务 ID 计数宽度，与 AXI ID 不同 |
| NumDim / RepWidth | 2 / 32 | 二维模式 / 重复计数宽度 |
| TfLenWidth | 32 | 单段长度计数宽度；有效最大长度还受表示范围、地址空间与前端限制 |
| 前端 NumRegs / NumStreams | 1 / 1 | 单组配置/单 stream |
| 后端 CombinedShifter | 0 | 保留分离数据对齐处理 |
| BufferDepth | 3 | 内部 reorder/dataflow 缓冲深度；后端注释说明 3 有利于未对齐传输 |
| MaskInvalidData | 1 | 屏蔽无效数据 |
| HardwareLegalizer | 1 | 硬件把传输分解为符合 AXI 约束的事务 |
| RejectZeroTransfers | 1 | 拒绝零长度传输；软件不能依赖零长任务正常完成 |
| ErrorCap | NO_ERROR_HANDLING | 未接入完整 iDMA 错误恢复；上游 BusErr 记录不等于自动恢复 |
| PrintFifoInfo | 0 | 关闭 elaboration 信息打印 |
| 后端 MetaFifoDepth | 3+16+8=27 | 源码公式 BufferDepth+NumAxInFlight+MemSysDepth |

### 1.2 运行时常用配置

| 软件动作 | 对应概念 | 实际使用提醒 |
| --- | --- | --- |
| 设置 SRC_ADDR / DST_ADDR | 源/目的 byte 地址 | 需是 DMA 可访问的物理/总线地址 |
| 设置 LENGTH | 每段搬运 byte 数 | 不等于元素个数或 AXI beat 数 |
| 2D SRC_STRIDE / DST_STRIDE | 相邻行起点增量 | 用 byte 表示；按实际 midend/驱动定义验证 |
| REPS / ENABLE_ND | 重复次数 / 2D 模式 | 使用现有 dma_2d_memcpy 接口并用小图样验证，避免自行猜计数是否减一 |
| 读取 NEXT_ID | 提交任务并取得 ID 的驱动入口 | 有副作用，不能当成纯状态寄存器反复读 |
| 轮询 DONE_ID | 判断任务完成 | DMA 完成后仍需按共享区约定保证 CPU 读到新数据 |

`sw/include/dif/dma.h` 当前使用 `IDMA_REG64_2D_*` 常量；不能只把 IsTwoD 改 0 继续沿用该布局。现有 `dma_memcpy()` 已可在 2D 硬件上进行一维搬运，通常不必为普通 memcpy 裁掉 2D。

源码待核查项：1D 分支 `.busy_i(idma_busy)`，本 wrapper 实际声明的是 `busy`，未见 `idma_busy` 声明。这是静态发现的可疑接线；可能受隐式 net/编译检查方式影响，不能写成已验证可用的 1D 配置。本轮未修复。另有驱动中两个 decouple 宏均使用 AW 位号的表达式；当前两个宏值均为 0，若要开启 RW decouple，需要单独核对，不能直接套例程。

## 2. LLC、SPM、原子通路

来源：[SoC gen_llc](../../hw/cheshire_soc.sv)、[LLC top](../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/src/axi_llc_top.sv)、[Boot ROM 启动汇编](../../hw/bootrom/cheshire_bootrom.S)、[LLC 软件寄存器头](../../sw/include/regs/axi_llc.h)。

默认硬件有 128 KiB LLC 数据阵列，**启动时 Boot ROM 等待 BIST，然后把所有 way 设为 SPM**。因此“LLC 已实例化”与“当前有多少 way 在做 cache”是不同问题。

| 硬件/运行时设置 | 用法 | 需同步检查 |
| --- | --- | --- |
| LlcSetAssoc/NumLines/NumBlocks | 决定总容量和组织 | tag/data SRAM、line 大小、软件容量读取 |
| CFG_SPM_LOW/HIGH | 按 way 分配 SPM | 正在使用的栈/代码/数据、flush/事务静止和容量 |
| LlcNotBypass=0, LlcOutConnect=1 | 下游路径继续存在，但旁路 LLC | 内部 SPM 消失；替代启动 RAM/栈必需 |
| LlcOutRegionStart/End | 设定 LLC 下游可缓存窗口 | CPU PMA、地址路由、链接脚本、DDR 实际容量 |
| LlcMaxReadTxns/WriteTxns | LLC 前原子单元容量 | 不是一键提高 DDR 带宽 |

默认 8 ways、每 way 16 KiB；若设计成 4 ways SPM + 4 ways cache，容量各 64 KiB，这是计算例子，**不是本轮已执行的运行时配置**。不能在栈还占用将被回收的 SPM 时切走对应 way。

CPU 主存请求先经过原子适配器再进入 LLC。ATOP 属于 AXI4 之外的原子事务扩展；当前 DDR 接口契约可以是普通 AXI4，由上游执行原子语义。NPU/ISP 新旁路会绕开已有监视点，普通 DMA 写同样会影响 LR/SC 和共享数据可见性，不能用“设备不发 AMO”推导安全。

## 3. 中断、调试与生成参数

| 模块/参数源 | 当前值 | 如何理解和修改 |
| --- | --- | --- |
| [rv_plic.cfg.hjson](../../hw/rv_plic.cfg.hjson) | src=58、target=2、prio=7、nonstd_regs=0 | 2 个 context 对应 1 hart 的 M/S；新增核/中断需重生成 RTL 与软件常量 |
| cheshire_int_intr_t | 58 bit（含保留 zero） | 包含 UART、I2C、SPI、USB、GPIO、CPU/DMA/VGA 错误；NumExtPlicIntrs=58−58=0 |
| [cheshire.mk](../../cheshire.mk) 的 CLINTCORES | 1 | 生成包 NumCores=1；改 Cfg.NumCores 不自动更改它 |
| CLIC | 默认关闭，INTCTLBITS=8 | 开启时每核系统输入数量=58+NumExtClicIntrs，再加 16 核内中断位 |
| IRQ router | 默认关闭 | 关闭时直接扇出；开启时按寄存器分发目标 |
| Debug Module | 内部 1 hart，无外部 hart | 修改核数时检查 hartinfo、halt 请求、JTAG/DMI/SBA |
| JTAG IDCODE | 0x1c5e5db3 | 用于工具识别；不是 CPU ISA 编码 |

默认 NumExtInIntrs=0 仍产生一个占位输入位；wrapper 应绑 0。当前 58 个 PLIC 源已由内部向量占满；扩展外部 PLIC 输入需要调整生成包，并确认中断编号、触发方式与驱动。不能仅按 SoC 配置中的 64 位计数字段任意扩容。

## 4. UART、I2C、SPI、GPIO、VGA、USB、Serial Link

| 模块 | 硬件配置入口 | 常用运行时设置 / 来源 | 联动 |
| --- | --- | --- | --- |
| UART | Cfg.Uart；SoC 实例 apb_uart | 分频、数据格式、中断；Boot ROM 使用 115200 | 核时钟/RTC 测频、串口工具、引脚 |
| I2C | Cfg.I2c；OpenTitan I2C IP | SCL/SDA 时序、FIFO、主机命令、IRQ；sw/include/regs 与驱动 | open-drain PAD、上拉、外部设备速率 |
| SPI host | Cfg.SpiHost；生成包 NumCS=3 | 时钟分频、片选、方向/段长度；最后一个 CS 为 dummy，对外 SpihNumCs=2 | SD/Flash 模式、板级片选连接 |
| GPIO | Cfg.Gpio/GpioInputSyncs | 方向、输出值、输入/边沿中断 | 32 路逻辑端口不表示全部板级引出 |
| VGA | RGB565，24 位横/纵计数，buffer=16，reads=24 | 帧地址、分辨率、消隐/同步时序 | 帧内存格式、AXI 带宽和引脚 |
| USB | Cfg.Usb，UsbDmaMaxReads=16；包 NumPhyPorts=4 | OHCI 寄存器、DMA 描述符 | 当前 wrapper 独立 USB 时钟；不能仅开位后当成可用 USB PHY |
| Serial Link | Cfg.SerialLink；hw/serial_link.hjson | clock/reset/isolation、分频与链路配置 | 对端协议/地址域/USER 原子标识；不等于 LVDS 图像采集 |

Serial Link 生成常量：[serial_link.hjson](../../hw/serial_link.hjson) 当前 `NumChannels=1, NumBits=8, Log2MaxClkDiv=10, Log2RawModeTXFifoDepth=3`，对应 4 个双沿 lane、最大分频常量 1024、raw TX FIFO 深度编码为 3。更改后须同步寄存器 RTL、接口宽度和软件。

**当前未接入的配置字段**：`Cfg.SlinkMaxClkDiv` 的原始赋值虽写 1024，但字段只有 10 位，实际截断为 0；SoC 和 VIP 实例实际用 `cheshire_pkg::SlinkMaxClkDiv=1<<serial_link_single_channel_reg_pkg::Log2MaxClkDiv`。只改 Cfg 字段不生效，若要改变需要处理生成常量与实例连接。

VGA 还有一个需验证的容量关系：默认 `VgaMaxReadTxns=24`，其 bus-error 单元却用 `CoreMaxTxns=8` 作为 NumOutstanding。这里只记录消费者取值差异，不推断已经出现功能故障。

## 5. AXI RT

`Cfg.AxiRt=1` 在所有发起者与 xbar 之间插入 AXI RT 单元；软件配置周期、带宽预算/地址区等，硬件开关本身不会自动获得实时保证。

当前 `NumPending=16, WBufferDepth=16, NumAddrRegions=2, CutSplitterPaths=1, DisableSplitChecks=1`；PeriodWidth/BudgetWidth 固定为 32。生成入口 `AXIRT_NUM_MGRS=6, AXIRT_NUM_SUBS=2`，当前寄存器包 `NumMrg=6, NumSub=2, NumReg=12`。

默认 SoC 恰好有 6 个发起者。若同时开 Ara，变为 7 个；如果关 USB/SerialLink，又会改变数量。**SELCFG=1 只在 DefaultCfg 上开 RT，并不是“RT+Ara”配置**。组合 Ara 与 RT 前，需核对并重生成寄存器映射，不能仅叠加两位开关。来源：[AXI RT 生成寄存器包](../../.bender/git/checkouts/axi_rt-7cef46f372eaf0fb/src/regs/axi_rt_reg_pkg.sv)。

## 6. FPGA DDR 与时钟参数

来源：[dram_wrapper_xilinx.sv](../../target/xilinx/src/dram_wrapper_xilinx.sv)、[cheshire_top_xilinx.sv](../../target/xilinx/src/cheshire_top_xilinx.sv)、[phy_definitions.svh](../../target/xilinx/src/phy_definitions.svh)。以下是 FPGA wrapper 配置，不能直接作为采购 ASIC DDR IP 的规格。

| dram_cfg_t 字段 | VCU118 | VCU128 | Genesys2 | 含义 |
| --- | --- | --- | --- | --- |
| EnCdc | 1 | 1 | 1 | SoC/DDR AXI 跨时钟 |
| CdcLogDepth | 5 | 5 | 5 | CDC FIFO 深度指数，2^5=32 |
| IdWidth | 8 | 8 | 4 | DDR 侧 AXI ID |
| AddrWidth | 31 | 32 | 30 | DDR 控制器侧 byte 地址位宽 |
| DataWidth | 512 | 512 | 64 | DDR AXI 数据位宽；不是 DQ pin 数 |
| StrobeWidth | 64 | 64 | 8 | byte strobe 数 |
| MaxUniqIds | 8 | 8 | 8 | ID 适配可跟踪的唯一 ID 数 |
| MaxTxns | 24 | 24 | 24 | 宽度/ID 适配事务容量 |

VCU118 的 DDR4 物理参数 `CsNWidth=1, DmDbiNWidth=8, DqWidth=64, DqsWidth=8`；VCU128 为 `2/9/72/9`。物理 DQ 宽度与 AXI 512 bit 数据口分属不同层。

DDR wrapper 先调整数据宽度与 ID，经过 CDC 后把地址截到低 AddrWidth 位。VCU118 默认 DDR 窗口 0x80000000 起，截低 31 位得到控制器内偏移；改主存窗口/容量必须重新核对映射和是否别名，不是只改 LlcOutRegionEnd。

FPGA 顶层连接 `clkwiz.clk_50` 到 SoC、`clk_48` 到 USB。这里是源码连接意图；实际频率仍需看 IP 配置与实现约束。本轮没有核验 timing。`RtcFreq=1000000` 是 FPGA wrapper 的软件参考频率参数，不是 CPU 工作在 1 MHz。

VCU118 的板宏没有 `USE_USB/USE_VGA/USE_I2C`，但 wrapper **只按 USE_USB 自动修改 Cfg.Usb**，不会按其他缺少的引脚宏自动关闭全部对应 SoC 外设。区分“实例存在”“IO 引出”“板上验证”三种状态。

## 7. 仿真 VIP 参数

来源：[vip_cheshire_soc.sv](../../target/sim/src/vip_cheshire_soc.sv)。这是测试环境，不是芯片综合参数。

| 参数组 | 当前默认值 | 用途 |
| --- | --- | --- |
| ClkPeriodSys / ClkPeriodJtag / ClkPeriodRtc | 5ns / 20ns / 30518ns | 模型时钟周期；系统模型为 200 MHz，非物理 timing 承诺 |
| RstCycles | 5 | 复位周期数 |
| TAppl / TTest | 0.1 / 0.9 | 驱动/采样相位占周期比例 |
| UartBaudRate / UartParityEna | 115200 / 0 | UART 模型参数 |
| UartBurstBytes / UartWaitCycles | 256 / 60 | 测试端 burst/等待控制 |
| SlinkMaxWaitAx / R / Resp | 100 / 5 / 20 | Serial Link 测试端等待控制 |
| SlinkBurstBytes | 1024 | 测试端数据 burst byte 数 |
| SlinkMaxTxns / SlinkMaxTxnsPerId | 32 / 16 | VIP 事务能力，非 SoC 对应参数默认值 |
| SlinkAxiDebug | 0 | 测试接口 debug 选项 |
| UseDramSys | 0 | 选择 DRAM 模型；开启需要额外库/配置 |
| AxiStrbWidth / AxiStrbBits | DutCfg.AxiDataWidth/8、其 clog2 | 派生参数，随 DUT 位宽变化 |

改变 RTC 模型周期时应与 DutCfg.RtcFreq 一致；否则软件测频/超时会偏移。DutCfg 与各 AXI type 参数由 fixture 传入，不能只给 VIP 换一套位宽而不改 DUT。

## 8. ASIC 迁移时另立的配置清单

必须另行确定：SRAM 宏尺寸/端口/延迟/byte enable，ROM 内容与生成工具，时钟源/门控/复位/CDC，PAD/电平/IO 时序，DDR AXI 与控制器/PHY 参数，DFT/MBIST、工艺库和约束。CVA6/Ara/LLC 有参数只说明 RTL 可参数化，不证明任何一组参数已适配工艺。后续以 [02 提取交接书](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md) 和真实供应商接口摘要为准。
