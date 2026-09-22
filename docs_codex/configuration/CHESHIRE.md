# Cheshire SoC 配置参数手册

返回 [配置导航](README.md)。基准：2026-09-20，本仓库 HEAD `379ae4544bc62e05a2736b11b33a3244181bba38`；以下为源码检查，未重新编译或仿真。

## 1. 从哪里配置

参数定义、默认值、地址映射和 CPU 覆盖函数都在 [cheshire_pkg.sv](../../hw/cheshire_pkg.sv)。消费位置在 [cheshire_soc.sv](../../hw/cheshire_soc.sv)。仿真通过 [tb_cheshire_pkg.sv](../../target/sim/src/tb_cheshire_pkg.sv) 选配置；FPGA 通过 [cheshire_top_xilinx.sv](../../target/xilinx/src/cheshire_top_xilinx.sv) 单独派生配置。

下面逐项覆盖 `cheshire_cfg_t` 全部字段。**表中“默认”是 DefaultCfg，不是 VCU118 或当前仿真必然使用的值**；未显式初始化字段由 `default: '0` 置零。Ara 仿真配置只覆盖 `Ara=1, AraNrLanes=2, AraVLEN=2048`。VCU118 wrapper 则另改 RTC、SerialLink、USB，见常用配置篇。

类型缩写表示存储位宽：`byte_bt=8`、`shrt_bt=16`、`word_bt=32`、`doub_bt=64`、`dw_bt=10`、`aw_bt=6`，均为无符号二态 bit 向量。**可表示范围不等于模块支持范围**；例如 10 位字段无法表示 1024，6 位字段无法表示 64，超宽赋值会截断。`NumCores` 是 5 位；外部端口/规则计数是 4 位，不能因数组有 16 项就把计数写为 16。

## 2. 全部 SoC 字段

### 2.1 CPU 与 hart

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `Cva6RASDepth` | `shrt_bt` | `2` | 返回地址栈深度（项）；覆盖 CPU profile 的 RASDepth，影响函数返回预测。 |
| `Cva6BTBEntries` | `shrt_bt` | `32` | 分支目标缓冲项数；覆盖 BTBEntries，改变预测结构和面积。 |
| `Cva6BHTEntries` | `shrt_bt` | `128` | 分支历史表项数；覆盖 BHTEntries，不是 cache 容量。 |
| `Cva6NrPMPEntries` | `shrt_bt` | `0` | 物理内存保护 PMP 项数；本值把向量 profile 的 8 覆盖为 0。PMP 与地址路由/PMA 是不同机制。 |
| `Cva6ExtCieLength` | `doub_bt` | `'h2000_0000` | 在 [0x20000000,0x80000000) 内划出的可缓存、幂等、可执行区域长度，单位 byte；需在 0～0x60000000 范围内并核对零长度规则。 |
| `Cva6ExtCieOnTop` | `bit` | `0` | 0：上述区域从 0x20000000 开始；1：贴到 0x80000000 下沿。只改 CPU 属性，不自动创建物理存储或 AXI 路由。 |
| `NumCores` | `bit [MaxCoresWidth-1:0]` | `1` | 内部 CVA6 hart 数；当前使用 1，Ara 开启时源码拒绝大于 1。多核不是只改本字段。 |
| `NumExtIrqHarts` | `doub_bt` | `'0（聚合默认）` | 外部 hart 中需要 CLINT/PLIC 中断的数量；需同步生成中断控制器。 |
| `NumExtDbgHarts` | `doub_bt` | `'0（聚合默认）` | 接入 Debug Module 的外部 hart 数；同步 ExtHartinfo 和 debug 请求/不可用信号。 |
| `CoreUserAmoOffs` | `doub_bt` | `0` | CPU 写入 AXI USER 原子来源标识的起始偏移，hart i 使用 offset+i；需核对原子单元识别约定，不能随意与其他来源冲突。 |
| `CoreMaxTxns` | `dw_bt` | `8` | 每核 ID serializer 允许的在途事务数，也用于该核 bus-error 记录容量。 |
| `CoreMaxTxnsPerId` | `dw_bt` | `4` | ID 压缩后每个输出 ID 的在途上限；并非 CPU 指令窗口深度。 |

### 2.2 中断

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `NumExtInIntrs` | `doub_bt` | `0` | 外部输入中断数量；须与 PLIC/CLIC 容量和中断编号同步。0 时接口仍有占位位，应绑 0。 |
| `NumExtClicIntrs` | `shrt_bt` | `NumExtPlicIntrs` | CLIC 系统中断中的外部项数；默认使用 PLIC 生成容量减内部中断数。当前为 0。 |
| `NumExtOutIntrTgts` | `byte_bt` | `0` | 向外分发中断的目标组数；不等同于外部 hart 数。 |
| `NumExtOutIntrs` | `shrt_bt` | `0` | 每个外部分发目标的中断向量宽度；检查 intr_routed 的截取与编号。 |
| `ClicIntCtlBits` | `shrt_bt` | `8` | CLIC 中断控制字段实现位数；仅 Clic=1 时有相应实例。 |
| `NumExtIntrSyncs` | `shrt_bt` | `2` | 外部中断输入同步器级数；级数变化影响跨时钟可靠性与延迟，不能代替脉冲握手。 |

### 2.3 AXI 与 Reg 通路

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `AddrWidth` | `aw_bt` | `48` | SoC AXI/Reg 地址位宽，单位 bit；默认 48，不等于 CPU XLEN 或 Sv39 有效虚拟地址位数。 |
| `AxiDataWidth` | `dw_bt` | `64` | SoC AXI 数据位宽，单位 bit；默认 64。更改会联动 cache/LLC 容量、DMA reg64、DDR 适配和类型。 |
| `AxiUserWidth` | `dw_bt` | `2` | AXI USER 位宽；必须容纳原子来源和错误扩展字段，不能直接设 0。 |
| `AxiMstIdWidth` | `aw_bt` | `2` | 接入交叉开关前的 master ID 位宽；CVA6 自身仍用 4 位，经过 serializer 压缩。 |
| `AxiMaxMstTrans` | `dw_bt` | `24` | 传给交叉开关 MaxMstTrans：从 xbar 输出 master 端口看允许的在途容量。 |
| `AxiMaxSlvTrans` | `dw_bt` | `24` | 传给交叉开关 MaxSlvTrans：从 xbar 输入 slave 端口看允许的在途容量。 |
| `AxiUserAmoMsb` | `dw_bt` | `1` | 原子来源 USER 切片最高位；需小于 AxiUserWidth 且不小于 Lsb。 |
| `AxiUserAmoLsb` | `dw_bt` | `0` | 原子来源 USER 切片最低位；与各 AMO adapter 的 AxiUserIdLsb 对应。 |
| `AxiUserErrBits` | `dw_bt` | `0` | bus-error 单元解析的 USER 错误扩展位数；0 不代表关闭 AXI RESP 错误检测。 |
| `AxiUserErrLsb` | `dw_bt` | `0` | USER 错误扩展字段最低位；与原子来源字段的分配应统一规划。 |
| `AxiUserDefault` | `doub_bt` | `0` | CPU/Debug/DMA/VGA/USB 等通路的默认 USER 值；CPU/SerialLink 会进一步调整原子标识。 |
| `RegMaxReadTxns` | `dw_bt` | `8` | AXI 到普通 32 位寄存器通路之前的原子适配器最大在途读数。 |
| `RegMaxWriteTxns` | `dw_bt` | `8` | 同一寄存器通路原子适配器最大在途写数。 |
| `RegAmoNumCuts` | `aw_bt` | `1` | 寄存器通路原子适配器内部 AXI 流水切分级数。 |
| `RegAmoPostCut` | `bit` | `1` | 1：原子适配后再放 AXI cut；0：旁路该 cut，不是关闭原子支持。 |
| `RegAdaptMemCut` | `bit` | `1` | AXI 到 Reg 适配器 CutMemReqs；插入内部请求寄存，提高时序裕量但增加延迟。 |

### 2.4 外部扩展端口与规则

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `AxiExtNumMst` | `bit     [MaxExtAxiMstWidth-1:0]` | `'0（聚合默认）` | 外部 AXI 发起者端口数，例如 NPU DMA 接入现有 SoC xbar；不自动形成 LLC 旁路。 |
| `AxiExtNumSlv` | `bit     [MaxExtAxiSlvWidth-1:0]` | `'0（聚合默认）` | 外部 AXI 被访问设备端口数，例如自定义大带宽 MMIO 设备。 |
| `AxiExtNumRules` | `bit     [MaxExtAxiSlvWidth-1:0]` | `'0（聚合默认）` | 外部 AXI 地址规则数；可多条规则映射同一端口，需无歧义且不超表容量。 |
| `AxiExtRegionIdx` | `byte_bt [2**MaxExtAxiSlvWidth-1:0]` | `'0（聚合默认）` | 规则到外部 AXI slave 相对索引的数组；有效项必须小于 AxiExtNumSlv。 |
| `AxiExtRegionStart` | `doub_bt [2**MaxExtAxiSlvWidth-1:0]` | `'0（聚合默认）` | 外部 AXI 地址区起点数组，单位 byte；规则区间左闭右开。 |
| `AxiExtRegionEnd` | `doub_bt [2**MaxExtAxiSlvWidth-1:0]` | `'0（聚合默认）` | 外部 AXI 地址区排他终点数组；每项 end>start，需在地址位宽内。 |
| `RegExtNumSlv` | `bit     [MaxExtRegSlvWidth-1:0]` | `'0（聚合默认）` | 外部 32 位 Reg 从设备端口数，适合 ISP/NPU 控制寄存器。 |
| `RegExtNumRules` | `bit     [MaxExtRegSlvWidth-1:0]` | `'0（聚合默认）` | 外部 Reg 地址规则数；这些规则也加入上层 AXI decoder。 |
| `RegExtRegionIdx` | `byte_bt [2**MaxExtRegSlvWidth-1:0]` | `'0（聚合默认）` | 规则到外部 Reg slave 相对索引数组；有效项小于 RegExtNumSlv。 |
| `RegExtRegionStart` | `doub_bt [2**MaxExtRegSlvWidth-1:0]` | `'0（聚合默认）` | 外部 Reg 区起点数组；需同时核对 CPU 非缓存/可执行属性。 |
| `RegExtRegionEnd` | `doub_bt [2**MaxExtRegSlvWidth-1:0]` | `'0（聚合默认）` | 外部 Reg 区排他终点数组；与 AXI 规则避免重叠。 |

### 2.5 时钟信息、启动与模块使能

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `RtcFreq` | `word_bt` | `32768` | RTC 参考频率，单位 Hz；写入只读配置寄存器供软件计时/测频。不会生成这个频率的时钟。 |
| `PlatformRom` | `word_bt` | `'0（聚合默认）` | 平台 ROM 地址；Bootrom=0 时成为 CPU BootAddr，默认 0 不能当作有效自定义 ROM。 |
| `Bootrom` | `bit` | `1` | 生成片内 Boot ROM；禁用时必须提供替代取指目标与启动存储。 |
| `Uart` | `bit` | `1` | 生成 UART；波特率由运行时寄存器设置，当前 Boot ROM 默认 115200。 |
| `I2c` | `bit` | `1` | 生成 I2C；自主 EEPROM 启动依赖它以及板级引脚。 |
| `SpiHost` | `bit` | `1` | 生成 SPI host；Flash/SD 的 SPI 启动依赖它。片选数量来自生成包。 |
| `Gpio` | `bit` | `1` | 生成 32 路 GPIO；板级是否引出要另看 wrapper。 |
| `Dma` | `bit` | `1` | 生成 iDMA 控制从端口和搬运主端口；详见外设篇。 |
| `SerialLink` | `bit` | `1` | 生成芯片间 Serial Link 以及收发 AXI 路由；不是 LVDS 图像接口。 |
| `Vga` | `bit` | `1` | 生成读帧缓冲的 VGA 模块；不是摄像头输入或 ISP。 |
| `Usb` | `bit` | `1` | 生成 USB OHCI 包装；还需要独立 USB 时钟和引脚适配。 |
| `AxiRt` | `bit` | `0` | 插入 AXI 实时带宽/事务管理模块；寄存器生成尺寸必须匹配 master 数。 |
| `Clic` | `bit` | `0` | 生成每核 CLIC，同时覆盖 CPU 的 RVSCLIC；默认仍保留 PLIC/CLINT。 |
| `IrqRouter` | `bit` | `0` | 1：可编程中断路由；0：输入中断直接扇出。不会消除 PLIC。 |
| `BusErr` | `bit` | `1` | 生成 CPU/DMA/VGA bus-error 记录和中断；不是全系统自动错误恢复。 |
| `Ara` | `bit` | `0` | 生成 Ara；必须同时选择 RVV=1 的 CPU profile、真实 decoder 和匹配软件。 |

### 2.6 调试

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `DbgIdCode` | `jtag_idcode_t` | `CheshireIdCode` | JTAG IDCODE 结构；version=1、part=c5e5、manufacturer=6d9、最低位=1，编码为 0x1c5e5db3。 |
| `DbgMaxReqs` | `dw_bt` | `4` | Debug 系统总线访存 mem_to_axi 可挂起请求数。 |
| `DbgMaxReadTxns` | `dw_bt` | `4` | 访问 Debug 寄存器/存储窗口前原子适配器的在途读上限。 |
| `DbgMaxWriteTxns` | `dw_bt` | `4` | 同一 Debug 从端口原子适配器在途写上限。 |
| `DbgAmoNumCuts` | `aw_bt` | `1` | Debug 从端口原子适配器 AXI cut 数。 |
| `DbgAmoPostCut` | `bit` | `1` | Debug 从端口原子适配器后是否再插 AXI cut。 |

### 2.7 LLC 与 SPM

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `LlcNotBypass` | `bit` | `1` | 1：启用 LLC/SPM 阵列（同时要求 LlcOutConnect=1）；0：旁路 LLC，无内部 LLC SPM。 |
| `LlcSetAssoc` | `shrt_bt` | `8` | LLC way 数；同时决定 SPM 可按 way 分配的数量。 |
| `LlcNumLines` | `shrt_bt` | `256` | 每个 way 的 cache line 数；不是全 cache 的 line 总数。 |
| `LlcNumBlocks` | `shrt_bt` | `8` | 每条 line 包含的 AXI 数据 beat 数；默认 8×8=64 byte/line。 |
| `LlcMaxReadTxns` | `dw_bt` | `16` | LLC 前原子适配器在途读容量；不要误当成整个 LLC MSHR 数。 |
| `LlcMaxWriteTxns` | `dw_bt` | `16` | LLC 前原子适配器在途写容量。 |
| `LlcAmoNumCuts` | `aw_bt` | `1` | LLC 前原子适配器的 AXI 流水切分级数。 |
| `LlcAmoPostCut` | `bit` | `1` | LLC 前原子适配器之后的 AXI cut 使能。 |
| `LlcOutConnect` | `bit` | `1` | 是否连接 LLC/旁路下游主存端口；0 时需另设计存储路径，不能保留 LlcNotBypass=1 期待 SPM 工作。 |
| `LlcOutRegionStart` | `doub_bt` | `'h8000_0000` | LLC 下游窗口起点；默认 DDR 起点 0x80000000，CPU 同时把此区列为可缓存/可执行。 |
| `LlcOutRegionEnd` | `doub_bt` | `64'h1_0000_0000` | 下游窗口排他终点；默认 0x100000000，形成 2 GiB 窗口，不证明物理 DDR 容量。 |

### 2.8 VGA

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `VgaRedWidth` | `byte_bt` | `5` | 像素红色通道位数；默认 RGB565。 |
| `VgaGreenWidth` | `byte_bt` | `6` | 像素绿色通道位数。 |
| `VgaBlueWidth` | `byte_bt` | `5` | 像素蓝色通道位数；需同步 wrapper 端口和帧缓冲格式。 |
| `VgaHCountWidth` | `aw_bt` | `24` | 水平扫描计数器位宽；不是横向分辨率值，实际时序由寄存器配置。 |
| `VgaVCountWidth` | `aw_bt` | `24` | 垂直扫描计数器位宽；不是纵向分辨率值。 |
| `VgaBufferDepth` | `dw_bt` | `16` | VGA 读数据缓冲深度，传给 BufferDepth。 |
| `VgaMaxReadTxns` | `dw_bt` | `24` | VGA AXI 读事务在途上限；需同时检查错误单元容量。 |

### 2.9 Serial Link

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `SlinkMaxTxnsPerId` | `dw_bt` | `4` | Serial Link 出站 ID remapper 每 ID 最大事务数。 |
| `SlinkMaxUniqIds` | `dw_bt` | `4` | Serial Link 出站 ID remapper 可跟踪的不同 ID 数。 |
| `SlinkMaxClkDiv` | `shrt_bt` | `1024` | 原始赋值 1024，但 dw_bt 只有 10 位，存入该字段会截为 0；当前实例不读取它，实际用包级同名常量 1024，见外设篇。 |
| `SlinkRegionStart` | `doub_bt` | `64'h1_0000_0000` | 发往远端芯片的本地地址窗口起点。 |
| `SlinkRegionEnd` | `doub_bt` | `64'h2_0000_0000` | 远端窗口排他终点；默认窗口大小 4 GiB。 |
| `SlinkTxAddrMask` | `doub_bt` | `'hFFFF_FFFF` | 出站地址中保留原地址的位掩码。 |
| `SlinkTxAddrDomain` | `doub_bt` | `'h0000_0000` | 出站地址其余位的固定值；输出=(domain & ~mask) OR (原地址 & mask)。 |
| `SlinkUserAmoBit` | `dw_bt` | `1` | Serial Link 设置/清理的 USER 来源标记位；需与 AMO 来源域一致。 |

### 2.10 USB

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `UsbDmaMaxReads` | `dw_bt` | `16` | USB AXI 适配最大在途读数。 |
| `UsbAddrMask` | `doub_bt` | `'hFFFF_FFFF` | USB DMA 地址保留位掩码；配合 domain 做地址重映射。 |
| `UsbAddrDomain` | `doub_bt` | `'h0000_0000` | USB DMA 地址固定高位域；不能替代 MMU 或内存保护。 |

### 2.11 DMA

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `DmaConfMaxReadTxns` | `dw_bt` | `4` | 访问 DMA 控制窗口之前原子适配器在途读容量；不是搬运读容量。 |
| `DmaConfMaxWriteTxns` | `dw_bt` | `4` | DMA 控制窗口原子适配器在途写容量。 |
| `DmaConfAmoNumCuts` | `aw_bt` | `1` | DMA 控制窗口原子适配器内部流水级数。 |
| `DmaConfAmoPostCut` | `bit` | `1` | DMA 控制窗口原子适配器后 AXI cut 使能。 |
| `DmaConfEnableTwoD` | `bit` | `1` | 1：2D 寄存器前端+ND midend；0：1D 前端。寄存器布局与驱动必须匹配，1D 分支有待核查信号问题。 |
| `DmaNumAxInFlight` | `dw_bt` | `16` | DMA 后端可并行在途的 AXI 事务容量；传给 NumAxInFlight。 |
| `DmaMemSysDepth` | `dw_bt` | `8` | 后端所连存储系统深度预算；参与元数据 FIFO 容量，不是 DDR 字节容量或 8 级 CPU 流水。 |
| `DmaJobFifoDepth` | `aw_bt` | `2` | 前端与执行部分之间任务 FIFO 深度；2D 时存 2D 描述符，非 AXI beat FIFO。 |
| `DmaRAWCouplingAvail` | `bit` | `1` | 是否生成 R–AW 耦合硬件；这里 RAW 指读响应 R 与写地址 AW，不是 CPU 的 read-after-write 冒险开关。 |

### 2.12 GPIO、AXI RT 与 Ara

| 参数 | 类型 | DefaultCfg 原始值 | 含义与联动 |
| --- | --- | --- | --- |
| `GpioInputSyncs` | `bit` | `1` | 传给 GPIO 的 GpioAsyncOn，决定输入同步；关闭前需确认输入时钟关系。 |
| `AxiRtNumPending` | `aw_bt` | `16` | AXI RT 单元 pending 表容量。 |
| `AxiRtWBufferDepth` | `dw_bt` | `16` | AXI RT 写数据缓冲深度。 |
| `AxiRtNumAddrRegions` | `aw_bt` | `2` | 每 manager 的地址区域数量；需要匹配生成寄存器 NumSub。 |
| `AxiRtCutPaths` | `bit` | `1` | AXI RT splitter 路径切分开关，用面积/周期换时序。 |
| `AxiRtEnableChecks` | `bit` | `'0（聚合默认）` | 传入 DisableSplitChecks 的反相；默认 0，不能把它理解成开启整个工程的仿真断言。 |
| `AraNrLanes` | `byte_bt` | `2` | 并行向量 lane 数；当前配置 2。Ara=0 时只保留字段，不生成向量核。 |
| `AraVLEN` | `word_bt` | `2048` | 每个架构向量寄存器长度，单位 bit；当前 2048，32 个寄存器总有效容量 8 KiB。 |

## 3. 派生容量、ID 和端口数

- LLC 数据阵列容量：`LlcSetAssoc × LlcNumLines × LlcNumBlocks × AxiDataWidth / 8`。默认 `8×256×8×64/8=131072 byte=128 KiB`；每 way 16 KiB，每 line 64 byte。不含 tag、状态与控制逻辑。
- AXI 发起者数：`NumCores + 1(Debug) + Ara + Dma + SerialLink + Vga + Usb + AxiExtNumMst`。默认为 6，Ara 仿真为 7，VCU118 向量 wrapper 为 5。
- 交叉开关输出 ID 位宽：`AxiMstIdWidth + clog2(发起者数)`。以上三种配置均为 `2+3=5`。
- LLC 下游 ID 位宽：上述输出 ID 位宽再加 `LlcNotBypass`；默认启用 LLC 时为 6。来源是 [typedef.svh](../../hw/include/cheshire/typedef.svh)，接 DDR 时不要误用 2 位。
- CPU 原生 AXI ID 固定 4 位；`gen_cva6_id_map()` 支持压到 1/2/3 位。压缩增加共用 ID 的串行约束，不能只按 pin 数最小化。
- 普通 Reg 总线是 32 位数据/4 位 strobe；DMA 控制窗口走单独 AXI 到 reg64 前端，不能把二者混为一谈。

交叉开关固定配置还包括 `FallThrough=0`、`LatencyMode=CUT_ALL_PORTS`、`PipelineStages=0`、`UniqueIds=0`；这些不在 cheshire_cfg_t 中。增加端口会改变 ID/仲裁/错误追踪容量，也会影响 AXI RT 生成寄存器。

## 4. 默认地址地图

下表端点都是 byte 地址，采用 `[起点, 终点)`；窗口存在不代表其中每个 offset 都实现寄存器。关闭模块通常移除对应规则；不要继续访问旧地址。来源：`gen_axi_out()`、`gen_reg_out()`。

| 对象 | 默认起点 | 排他终点/长度 | 存在条件 |
| --- | --- | --- | --- |
| Debug 窗口 | 0x00000000 | 0x00040000 | 内建 |
| DMA 控制 | 0x01000000 | 0x01001000 | Dma |
| Boot ROM | 0x02000000 | 0x02040000 | Bootrom；窗口不等于 ROM 实体容量 |
| CLINT | 0x02040000 | 0x02080000 | 内建 |
| IRQ router | 0x02080000 | 0x020c0000 | IrqRouter |
| AXI RT | 0x020c0000 | 0x02100000 | AxiRt |
| SoC 配置寄存器 | 0x03000000 | 0x03001000 | 内建 |
| LLC 控制 | 0x03001000 | 0x03002000 | LlcNotBypass；合法配置还需连接下游 |
| UART / I2C / SPI / GPIO | 0x03002000 / 3000 / 4000 / 5000 | 每个 0x1000 byte | 对应使能 |
| Serial Link / VGA / USB 控制 | 0x03006000 / 7000 / 8000 | 每个 0x1000 byte | 对应使能 |
| BusErr | 0x03009000 | 每实例 0x40 byte | VGA、DMA、各 CPU 顺序编号，BusErr 开启 |
| PLIC | 0x04000000 | 0x08000000 | 内建 |
| CLIC | 0x08000000 | 每核 0x40000 byte | Clic |
| SPM 可缓存别名 | 0x10000000 | 默认 0x10020000 | 有效 LLC/SPM 阵列 |
| SPM 非缓存别名 | 0x14000000 | 默认 0x14020000 | 同一阵列的另一个入口 |
| 外部扩展属性区 | 0x20000000 | 0x80000000 | 仅 PMA 分区；需要额外地址规则/设备 |
| LLC 下游 DDR 窗口 | 0x80000000 | 0x100000000 | LlcOutConnect |
| Serial Link 远端窗口 | 0x100000000 | 0x200000000 | SerialLink |

软件地址另见 [common.ldh](../../sw/link/common.ldh)、[params.h](../../sw/include/params.h)。修改 RTL 地址不自动同步链接脚本。

**一个需要保留的源码差异**：`gen_cva6_cfg()` 的可执行 SPM 区长度写为 `2*SizeSpm`，起点 `AmSpm`；两个实际 SPM 别名却相隔 `0x04000000`。默认执行规则因此是 `[0x10000000,0x10040000)`，并没有覆盖 `0x14000000` 非缓存别名。不要根据旁边的 “AllSPM” 注释推断可从非缓存别名取指。本轮仅记录，未修改或动态验证。

## 5. 修改外部端口的最小思路

NPU 控制寄存器一般接 `RegExtNumSlv`；NPU 主动读写内存接 `AxiExtNumMst`。先设计地址规则、中断号、AXI 类型和 clock/reset 接口，再改配置与 wrapper。外部异步时钟需要 CDC；`NumExtIntrSyncs` 只同步中断位，不同步 AXI。

`AxiExtNumMst=1` 接入的是已有 SoC xbar，访问 DDR 地址仍按现有规则经过 LLC 路径。团队要求的 ISP/NPU 绕过 LLC 需要 DDR 侧新拓扑与一致性契约，无法只靠某个参数完成，见 [ASIC 提取交接书](../02_Cheshire_Ara_ASIC_Extraction_Handoff.md)。

`iomsb(0)=0` 用于保留合法占位端口范围；它不表示配置为 0 的模块实际存在。wrapper 要按有效计数连接，并给闲置输入稳定值。
