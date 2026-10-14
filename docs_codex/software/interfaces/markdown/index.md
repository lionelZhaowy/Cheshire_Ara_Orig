# 软硬件接口专题

当前源码、软件可见行为与 RTL 的对应关系

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/index.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../index.html) · [阅读路线](index.md)

- [阅读顺序与使用方法](#route)
- [输入版本与配置基线](#baseline)
- [从软件模块找到实际硬件](#source-map)
- [与既有文档及参考图的关系](#boundaries)

本专题负责五层结构中的**软硬件接口层**，借助必要的基础软件和 SoC RTL，把程序的一次操作追到硬件，再追到软件观察到的结果。适合有 RTL/NPU 经验、正在学习 RISC-V 启动和驱动的读者。

新增[基础软件与BSP](foundation-software.md)：从HAL/DIF、MMIO辅助代码、库归档和开发工具理解接口的使用。推荐先读本章，再进入构建启动与四类接口；[两层区别与联系](foundation-software.md#layers)用UART实例对照。

<a id="route"></a>

## 阅读顺序与使用方法

| 顺序 | 章节 | 阅读后能回答的问题 |
| --- | --- | --- |
| 前置 | [基础软件与BSP](foundation-software.md) | 哪些是软件实现、接口契约、构建工具，怎样定位代码 |
| 1 | [构建、加载与启动](build-boot.md) | ELF 放在哪里，CPU 怎样到达 main，谁清 BSS、准备栈 |
| 2 | [指令、Ara 与 CSR](instructions.md) | 普通计算、向量请求、CSR 分别走哪条接口 |
| 3 | [内存、MMIO 与数据交接](memory-mmio.md) | 一条 load/store 如何命中实际存储或产生寄存器副作用 |
| 4 | [异常与中断](interrupts.md) | 事件如何进入 trap，谁保存现场、清源、返回 |
| 5 | [五条软件到 RTL 案例](cases.md) | 字符、计时、DMA、GPIO 中断、RVV 的完整证据链 |
| 6 | [自定义 IP 与 Linux 修改导航](integration.md) | 地址、字段、IRQ、DMA、启动、设备树怎样共同修改 |
| 7 | [最小实践与验证记录](labs.md) | 当前可以动手做什么，怎样判定成功或阻塞 |

第一次按顺序阅读；定位问题时从案例表跳到相应机制。每个案例采用“目标/前提—软件—访问—RTL—完成—观察—排错”的顺序。本专题的图是静态源码关系图，不是仿真波形。

分层文档将构建、启动与运行支持另列为横向支撑。本专题沿用用户的五层框架：主机工具、crt0 和驱动归入基础软件的讨论范围，但不把编译器画成目标端每次 MMIO 都经过的调用层。软硬件接口本身是语义契约，不是一个必须被链接的库。[分层索引](../../LAYERS_AND_TOOLS.md)提供全局分类。

基础软件扩充按当前 `bf1b4198`核对，证据见[本次BSP记录](foundation-software.md#evidence)。下面保留初版接口教程的输入身份，不把两批验证合成一次。

<a id="baseline"></a>

## 输入版本与配置基线

本次核对日期 **2026-10-13**，分支 `mp/ara-pulp-v2`，主仓库 HEAD `c4162204cfee0c48b81158b4296860a678d92bec`。工作区已有文档、图稿迁移和其他对话的未跟踪文件；本次未改生产 RTL、软件或依赖。输入状态见 [input.json](../evidence/input.json)，引用源的 SHA-256 见 [sources.json](../evidence/sources.json)。上游来源由 [.bender/SNAPSHOT.tsv](../../../../.bender/SNAPSHOT.tsv)和 [UPSTREAM.lock](../../../../.bender/UPSTREAM.lock)记录；目录名后缀不是 commit。

| 对象 | 保存的上游 HEAD | 当前解释条件 |
| --- | --- | --- |
| CVA6 | `99eac9a649001bdf5b8f9da52e0ca73d5c48db1c` | 本地有集成差异；以被引用文件内容为准 |
| Ara | `2895ba907e9eb14b3464609dc791a969d159a7c3` | 专用 CVA6 加速器/MMU 接口 |
| AXI | `39f5f2d51c5e524f6fc5cf8b6e901f7dcc5622d7` | 检查此快照的桥/互连，不能套最新版本行为 |
| LLC | `559bcbd09a5a884dbe31e2d72fd95d024e357f39` | 当前配置接口是 Regbus |

[Bender.local](../../../../Bender.local)将依赖定向到仓库内快照，当前 [Bender.lock](../../../../Bender.lock)记录 Path、revision=null；这是当前锁法，不能据 null 宣称未固定依赖。其他已引用依赖的来源记录一并保存在证据清单。

| 配置入口 | 当前源码取值/选择 | 能证明什么 |
| --- | --- | --- |
| [cheshire.mk](../../../../cheshire.mk) `CHS_BENDER_RTL_FLAGS` | 默认 `cv64a6_imafdchsclic_sv39_wb` | 根规则默认标量 profile；不能通过 SELCFG 自动变成向量 CPU |
| [Ara/cheshire/Makefile](../../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/Makefile) `COMMON_CUSTOM_TARGETS` | `cv64a6_imafdcv_sv39`、`exclude_first_pass_decoder`、ARA；默认 2\_lanes | 官方集成入口选择向量译码，lane/VLEN 从配置文件读取 |
| [config/2\_lanes.mk](../../../../.bender/git/checkouts/ara-2c7b103275a16c87/config/2_lanes.mk) | 2 lanes，VLEN=2048 | 当前向量参考组合，非最终 ASIC 参数冻结 |
| [VCU118 清单](../../../../target/xilinx/scripts/add_sources.vcu118.tcl) 与 [FPGA top](../../../../target/xilinx/src/cheshire_top_xilinx.sv) | 向量 profile，ARA/2/2048；`gen_cheshire_xilinx_cfg()` 从 DefaultCfg 覆盖 RTC/SerialLink/USB/Ara | 已生成的配置和加源输入；不证明旧 bitstream 与此输入一致 |
| [现有仿真清单](../../../../target/sim/vsim/compile.cheshire_soc.tcl)、[TB 配置](../../../../target/sim/src/tb_cheshire_pkg.sv) | 现有清单仍选标量 profile，first-pass stub 与真实实现并存；Ara 的 SoC 组合用 SelectedCfg=3 | 向量仿真前须重建并验收匹配清单，不能直接只改 `SELCFG=3` |
| [sw/sw.mk](../../../../sw/sw.mk) | `rv64gc_zifencei` / `lp64d` | 默认软件不带 V；[Ara 软件入口](../../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/Makefile)另加 V |
| ASIC 规划 | 独立目录、固定配置、静态清单 | 提取、外购 DDR、GB、新 IP 尚未实现；Bender 不是长期迁移目标 |

`DefaultCfg` 是默认配置结构，不等于唯一实际平台：`gen_cva6_cfg()`、TB/FPGA 覆盖、CPU profile 与编译宏共同决定硬件。当前没有可追溯到本次源码和 ELF 的在板 bitstream 身份，因此不声称“当前板上一定运行这一配置”。用户曾报告的 VCU118 HelloWorld 只作为历史输出证据。

<a id="source-map"></a>

## 从软件模块找到实际硬件

DIF（Device Interface Function，设备接口函数）主要操作控制器寄存器；HAL（Hardware Abstraction Layer，硬件抽象层）还可封装片外器件命令。以下不是强制调用层级：应用可以直接调用 DIF，也可以直接 MMIO。

| 软件对象与关键符号 | 调用者 → 实际消费者 | 硬件落点/边界 |
| --- | --- | --- |
| [printf.c](../../../../sw/deps/printf/printf.c) `printf_`、`_out_char`；[uart.c](../../../../sw/lib/dif/uart.c) `_putchar` | 应用 printf 宏 → 格式化 → `_putchar` → `uart_write` | CPU 逐字节写 UART；`.a` 不在硬件中运行 |
| [UART DIF](../../../../sw/lib/dif/uart.c) `uart_init/read/write/flush` | 程序或 UART debug → `reg8` | `reg_uart_wrap → reg_to_apb → apb_uart`，不是 OpenTitan UART |
| [SPI DIF](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.c) `dif_spi_host_transaction` | Flash/SD HAL → command/TX/RX 寄存器 | `spi_host` 命令队列和收发状态机 |
| [I²C DIF](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_i2c.c) `dif_i2c_write_byte_raw` | EEPROM HAL → FDATA 等寄存器 | `i2c` 主机 FMT FIFO → SCL/SDA；器件地址不同于 SoC MMIO 基址 |
| [GPIO DIF](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_gpio.c) `dif_gpio_write_masked` | 应用 → 掩码寄存器 | `gpio` 输出/OE；实际板级引脚另核对 |
| [Flash HAL](../../../../sw/lib/hal/spi_s25fs512s.c)、[SD HAL](../../../../sw/lib/hal/spi_sdcard.c)、[EEPROM HAL](../../../../sw/lib/hal/i2c_24fc1025.c) | Boot ROM 或应用 → 设备协议 → SPI/I²C DIF | HAL 负责命令/等待/校验，RTL 控制器负责电气时序 |
| [GPT](../../../../sw/lib/gpt.c) `gpt_boot_part_else_raw`；[gpt.h](../../../../sw/include/gpt.h) `gpt_read_t` | GPT 按字节 offset/length 调用 read(priv, dst, addr, len) | GPT 不直接驱动总线；回调把读取转成对应介质事务 |
| [UART debug](../../../../sw/lib/hal/uart_debug.c) `uart_debug_serve` | Boot ROM → READ/WRITE/EXEC 解释 | 收到地址后由 **CPU** 读写内存或跳转；不是 UART 自带 AXI DMA |
| [CLINT DIF](../../../../sw/lib/dif/clint.c) | `clint_get_mtime` 等 → `reg32` | RTC 驱动的 MMIO 计数与比较；`get_mcycle` 另走 CPU CSR |
| [DMA API](../../../../sw/include/dif/dma.h) `sys_dma_2d_memcpy` | 头文件 inline 写参数、读 NEXT\_ID | DMA 控制 AXI slave 与搬运 AXI master 分开；当前缺口见案例 |
| [LLC API](../../../../.bender/git/checkouts/axi_llc-5fb8850caad4fcfa/sw/lib/axi_llc_reg32.c) | CPU 配置 way/commit/flush | LLC/SPM 阵列和配置状态机；不自动刷新 CPU L1 |
| [AXI RT API](../../../../.bender/git/checkouts/axi_rt-7cef46f372eaf0fb/sw/lib/axirt.c) | [axirt\_hello](../../../../sw/tests/axirt_hello.spm.c) 等配置预算 | SoC 可选 `i_axi_rt_unit_top`；不是通用 memcpy 库 |
| [util.h](../../../../sw/include/util.h) `reg8/reg32/fence`、[mmio.h](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/base/mmio.h) `mmio_region_read32/write32` | 上述 DIF/HAL 的最低软件访问工具 | load/store 或 fence 指令；没有名叫 MMIO 的独立硬件 IP |
| [sw.mk](../../../../sw/sw.mk) `CHS_SW_LIB_SRCS_O`、`libcheshire.a` | 链接器从归档取所需对象 | 格式化、crt0、本地 HAL/DIF、OT base/DIF/autogen、LLC/AXI RT 一同归档；unused 节可被裁掉 |

`params.h` 中的 `extern ... __base_uart` 是链接符号声明。`&__base_uart` 得到链接器赋的数值地址，不是先从该地址读取一个指针。全库编入归档也不表示最终 ELF 包含所有驱动，更不表示所有外设都启用。

<a id="boundaries"></a>

## 与既有文档及参考图的关系

[RTL 模块指南](../../../rtl_modules/README.md)负责模块内部电路；[软件手册](../../README.md)负责命令/API 查阅；本专题负责贯穿它们的执行场景，避免重建整份 SoC 地址表。详细地址和 C/I/E 条件继续查 [01 §8.1](../../../01_Cheshire_Ara_Quick_Start.md#81-cie-attributes)。

本轮附件只有文本，没有可直接核验的两张附图；已经找到[分层参考](../../LAYERS_AND_TOOLS.md)和 [SoC 规划图说明](../../../diagrams/2026-10-12_soc_landscape/README.md)。其中 C1–C9、S0–S2、多端口 DDR 和 Ara→GB 都按规划处理；采购 IP 的真实端口 manifest 尚未提供。最新已确认需求以 [IP/DDR 契约 §12](../../../engineering/IP_DDR_Interface_Contract.md)为准，不从图中冻结新地址、宽度或频率。

本专题中“源码事实”表示已核对引用源；“分析推断”表示根据该配置推演；“设计建议”表示后续需要实现与验证。编译结果、目标运行和板测分别记录在[实践页](labs.md#evidence)。

软件组件整体定位见[全组件软件栈](foundation-software.md#complete-stack)及[源码索引](foundation-software.md#component-index)；UART和GPT/Flash逐步调用链仍保留在同章。

---

[下一页：基础软件与BSP](foundation-software.md)
