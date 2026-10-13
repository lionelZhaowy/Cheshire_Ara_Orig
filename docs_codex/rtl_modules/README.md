# Cheshire RTL 模块阅读与扩展指南

更新：2026-10-13。任务：L01。输入提交：`c4162204cfee0c48b81158b4296860a678d92bec`，实现结论以本次读取的工作区源码为准；逐文件 SHA-256 与代码定位见[源码清单](../diagrams/2026-10-13_rtl_module_comparison/source_manifest.json)。

这份指南回答：**寄存器写入后，模块内部哪些电路开始工作；数据怎样流动；状态怎样回到软件；接入自己的 IP 时必须保留哪些约定。** 它承接 Regbus 讨论，不重画 CPU—Crossbar—DDR 的 SoC 全景图。

每章用一至两张图展开真实 RTL 模块或同一模块内的关键逻辑，再按图内编号解释。图中 FIFO、寄存器、状态机和接口适配各自有明确职责；多个小实例只在对使用没有区别时合并。完整五通道 AXI 握手、每个同步触发器和状态机全部状态不逐一展开。

## 按模块阅读

| 章节 | 先解决的问题 | 图数 |
|---|---|---:|
| [00 Regbus](00_regbus.md) | 64→32 怎样转换；哪些事情软件仍须负责；自有 IP 怎样接入 | 2（连线已补齐） |
| [01 UART](01_uart.md) | APB 适配、波特率节拍、TX/RX FIFO 与读寄存器副作用 | 1 |
| [02 IIC / I²C](02_i2c.md) | FMT 命令、Host/Target 队列、SCL/SDA 时序与电气边界 | 1 |
| [03 SPI Host](03_spi.md) | 命令队列和数据队列为何分开；如何驱动 Flash 等器件 | 1 |
| [04 GPIO](04_gpio.md) | 输入同步/滤波、输出值/使能、掩码写与中断检测 | 1 |
| [05 PLIC](05_plic.md) | pending、active、优先级、claim/complete 的实际关系 | 1 |
| [06 CLINT / CLIC](06_clint_clic.md) | RTC 计数与本地中断选择是两个不同职责 | 2 |
| [07 IRQ Router](07_irq_router.md) | 按源配置目标掩码；它为什么不是另一个 PLIC | 1 |
| [08 BootROM](08_bootrom.md) | ROM 常量、延迟应答、软件生成与 ASIC 宏替换 | 1 |
| [09 SoC Regs](09_soc_regs.md) | scratch、硬件只读字段与 reggen 的修改入口 | 1 |
| [10 JTAG Debug](10_jtag_debug.md) | DMI、hart debug、调试存储窗和 SBA 四种关系 | 1 |
| [11 Serial Link](11_serial_link.md) | AXI 通道怎样跨链路；配置、时钟与对端约定 | 1 |
| [12 VGA](12_vga.md) | 帧缓冲 AXI 读取、像素 FIFO 与时序发生器 | 1 |
| [13 USB](13_usb.md) | OHCI 描述符 DMA、Reg→AXI 控制转换和 PHY CDC | 1 |
| [14 iDMA](14_idma.md) | 外部 AXI 配置、内部 Reg、任务队列、2D 展开及当前缺口 | 1 |
| [15 中断和异常处理](15_interrupt_exception.md) | 设备事件如何成为 CPU trap；异常如何随指令提交 | 1 |
| [16 LLC / SPM](16_llc_spm.md) | 命中/缺失、SRAM way 复用、flush 与缓存一致性责任 | 2 |
| [17 AXI 扩展与适配](17_axi_extension.md) | 新 IP 接口角色、两级译码、ID、位宽、CDC、限流与错误覆盖 | 1 |
| [18 时钟复位与启动](18_clock_reset_startup.md) | 配置域与工作域、复位依赖、Platform ROM 和事件恢复 | 1 |
| [19 DDR 与 LVDS/ISP 搬运](19_ddr_lvds_pipeline.md) | 控制器/PHY 边界、帧 DMA、NPU 搬运器与 GB 分工 | 1 |
| [20 CPU/Ara 与共享数据](20_accelerator_memory.md) | PMA、实际失效路径、WT/LLC 可见性与所有权交接 | 1 |

共 **21 篇文档、24 张当前采用的 A 图和 24 张 C 版试绘**。原有 17 篇已逐篇复核并修复；新增 4 篇围绕实际集成路径补缺。各图的 **213 条连接**由统一清单生成编号和连接表，协议/信号组、方向与用途可在图下查到。

打开 [A/C 连续走线对比页](../diagrams/2026-10-13_rtl_modules_native_c/index.html)：可按模块跳转、并排或上下比较、打开原尺寸。**用户比较 C 后已确认继续采用 A，后续补图与修订沿用 A**；C 使用 `svg-pptx-diagrams-native` 的彩色标题带、浅色主体及柔和边框，保留 A 的布局和全部连线。两版技术内容相同，C 仅保留为试绘记录，风格选择已完成。[C 图源、PPT 与检查说明](../diagrams/2026-10-13_rtl_modules_native_c/README.md)。

**2026-10-13：B 配对端口版已被用户明确弃用。**离散模块不能靠文字名或编号表达连接；后续主图必须用连线/箭头组成结构。B 历史资产保留存档，不再展示为候选或自动生成。

两版均有 SVG、PNG、矢量 PDF 和原生可编辑 PPTX：[A 合辑](../diagrams/2026-10-13_rtl_module_comparison/A/editable/diagrams.pptx) · [C 合辑](../diagrams/2026-10-13_rtl_modules_native_c/C/editable/diagrams.pptx)。复现与检查见[图稿入口](../diagrams/2026-10-13_rtl_modules_native_c/README.md)。2026-10-12 原图保持不变，修改前的未提交文档也已归档备份。

## 本轮复核后，先留意这些区别

- **总线适配不完成软件契约。** Regbus 仍需合法访问宽度、字节使能、读副作用、时钟域和命令提交约定；它默认与 SoC 同时钟。
- **配置、任务和数据完成是三个层次。** iDMA 二维任务需 midend 汇总完成；LLC `COMMIT_CFG` 清零只说明接收提交；默认 trap 入口自旋，需要应用提供实际处理程序。
- **新增外部 master 不自动绕过 LLC。** 外部 AXI 接主 Xbar 后，访问 LLC 区域仍走 LLC；新 DDR 旁路需要另行实现，也改变缓存与原子操作的观察范围。
- **现有 Ara 失效机制有路径限制。** 它观察穿过自身过滤器的写地址，不覆盖新 NPU/ISP 旁路写；当前向量 profile 的 L1D 写穿也不消除在途写、LLC 副本和 buffer 所有权问题。
- **新 IP 仍属规划。** NPU、ISP、LVDS、GB、专用搬运及购买的 AXI4 DDR 接法均未由本轮实现。DDR 端口参数、训练/ready、CDC/复位、IRQ 和寄存器窗口需由最终 IP 资料确认。

## 接入自有 IP，优先读什么

NPU/ISP/PLL/DDR/LVDS 的**配置寄存器**首先按 Regbus 章设计：地址窗口、32-bit 访问语义、配置提交、状态/错误、中断、时钟复位。然后参考 SoC Regs 的 reggen 封装和 GPIO/PLIC/IRQ Router 的事件上报。大量图像与权重传输另看 iDMA、USB、VGA；这些实例说明“配置接口”和“搬运数据接口”可以是两套接口。

不能因为一个 IP 的数据口是 AXI master，就要求其控制口也必须是 AXI slave。当前 UART、SPI、I²C 主要靠软件读写 FIFO；VGA、USB、iDMA 会自己访问内存。自行增加 NPU 搬运器或帧写入 DMA 时，需要另定描述符/启动语义、地址范围、在途请求、完成条件与缓存维护，参见[IP/DDR 接口契约](../engineering/IP_DDR_Interface_Contract.md)。

## 所有章节共用的阅读约定

- `clk_i / rst_ni` 默认指 Cheshire SoC 输入时钟/低有效复位。没有为图假定具体频率，也没有把 Regbus 画成默认低频总线。RTC、JTAG TCK、USB PHY、Serial Link 接收时钟在对应章节单独说明。
- `Cfg.*` 是静态配置/生成条件；寄存器中的 enable 是运行时控制，两者不能混用。模块存在也不代表当前板级引脚、驱动和测试已齐全。
- 源码路径后给出本次快照的行号和可搜索符号。`#L` 跳转适用于支持源码行锚点的查看器；IDE 不识别时按表内行号或符号定位。
- 图内实线表示连接表定义的数据/请求路径，双箭头合并请求与返回；单箭头可表示主数据方向，反向 ready 在连接表说明。虚线连线是控制/事件或明确标注的逻辑关系，虚线模块是规划。交叉而无圆点不表示相连。矩形左侧细竖线表示存储/队列，不暗示它必定映射成 SRAM 宏。
- MMIO 的合法访问宽度由设备约定。32-bit Regbus、64-bit AXI 数据总线、RV64 的 XLEN 是三件事。尤其要检查读 FIFO、读清除、读触发提交等副作用。
- 本轮覆盖全部 21 篇、48 张预览；依据本地项目/依赖官方文档与当前 RTL 的静态对应、图稿与链接检查；未新跑 RTL 仿真、外设板测或 ASIC 签核。原生 PPT 对象已由脚本检查，未在 Microsoft Office 中验收外观。

当前工程曾由用户报告 VCU118 HelloWorld 成功；这不扩大为其他外设、DMA、Ara、DDR、USB 等已验证。对文中指出的现有缺口，只解释其影响，不在本次修改 RTL 或软件。
