# 片外器件与接口实现参考

返回[工程文档入口](00_README.md) · [软硬件层次与工具](software/LAYERS_AND_TOOLS.md) · [软件参考](software/README.md)

核对基准：2026-10-11，分支 `mp/ara-pulp-v2`，HEAD `eaf55be17a07368cdc04ae624301411f8a906593`。本文将器件、控制器、仿真对端、软件与平台接线对应起来，供自底向上查源码。软件支持主要指根 `sw/` 裸机代码；依赖 SDK/Linux 中存在的驱动不自动计为本平台已集成。

| 修改日期 | 内容 | 证据等级 |
| --- | --- | --- |
| 2026-10-11 | 汇总 DDR、Flash、EEPROM、SD 与 UART/JTAG/Serial Link/GPIO/VGA/USB/SPI/I²C 的连续答疑；补充 Boot ROM、时钟复位和扩展边界 | 当前源码静态核对及官方资料；未重新编译、仿真或板测 |

## 1. 对象分类与阅读方法

“片外器件”与“通信接口”不是同一类别。DDR、Flash、EEPROM、SD 是具体存储对象；UART、SPI、I²C、GPIO 等接口可以连接多种对象；Boot ROM 是片上存储。`external` 若出现在 Cheshire 端口名中，首先表示位于 `cheshire_soc` 模块外，不自动表示位于芯片外。

建立对应关系时依次检查：**外部对象 → 信号接口 → 片上控制器 RTL → 控制器驱动/DIF → 器件协议 HAL → 应用或启动程序**。并非每条路径都有全部层次：普通 UART 输出没有额外器件 HAL；DDR 初始化后通常由普通访存指令访问；JTAG 调试工具主要在开发主机运行。

“有 RTL”“有驱动”“有仿真对端”“测试实际通过”分别记录。协议模型不一定绑定器件型号，GPIO 测试也可以直接施加输入、检查输出，而无需模拟一颗具体芯片。

## 2. 四类存储介质对照

| 属性 | DDR 主存 | SPI NOR Flash | I²C EEPROM | SD 卡 |
| --- | --- | --- | --- | --- |
| 用途 | 运行代码、栈、数据及缓冲区 | 非易失镜像、启动介质 | 非易失小容量数据、启动介质 | 非易失块存储、启动介质 |
| 断电保留 | 否 | 是 | 是 | 是 |
| 当前明确型号 | 随 FPGA 板型配置，见下一节 | S25FS512S，512 Mbit / 64 MiB | 24FC1025，1 Mbit / 128 KiB | 未指定品牌、料号或容量 |
| 器件接口 | DDR 命令/地址、DQ/DQS 等 | SPI；器件具备多 I/O 能力，当前 HAL 用单线 | I²C | SPI 模式，不是原生四位 SD 模式 |
| SoC 接入 | 外部主存 AXI 口 | MMIO → SPI Host | MMIO → I²C Host | MMIO → SPI Host |
| 控制器 | FPGA Xilinx DDR IP；ASIC 采购 Controller/PHY 待集成 | 已有 SPI Host RTL | 已有 I²C RTL | 复用 SPI Host |
| 仿真后端 | axi_sim_mem 或 axi_dram_sim + DRAMSys | s25fs512s 模型 | M24FC1025 模型 | 默认 testbench 未接入模型 |
| 模型边界 | AXI，替代下游外存子系统 | SPI 引脚，保留片上控制器 | I²C 引脚，保留片上控制器 | 默认环境不支持 SD 启动仿真 |
| 软件入口 | 普通访存；ASIC 初始化待规范 | spi_s25fs512s_* | i2c_24fc1025_* | spi_sdcard_* |
| Boot ROM 角色 | 后续可用主存，无单独介质启动模式 | BOOTMODE=2，CS1 | BOOTMODE=3，第 0 颗 | BOOTMODE=1，CS0 |

### 2.1 DDR 的实现、模型与时序层次

真实硬件关系为 `SoC → AXI → DDR Controller → PHY → DDR 颗粒`。当前 [cheshire_soc.sv](../hw/cheshire_soc.sv) 的 `axi_llc_mst_req_o` / `axi_llc_mst_rsp_i` 是外存边界，`gen_llc` 中的 LLC 连接该端口。这里没有集成采购的 ASIC Controller/PHY。

| 文件 | 对应实现 |
| --- | --- |
| [dram_wrapper_xilinx.sv](../target/xilinx/src/dram_wrapper_xilinx.sv) | FPGA AXI 位宽、ID、可选 CDC 适配及 DDR IP 实例；DDR4 分支为 ddr4，DDR3 为 mig7s |
| [impl_ip.tcl](../target/xilinx/scripts/impl_ip.tcl) | Vivado DDR IP 创建及板型参数；VCU118 为 MT40A256M16LY-062E，VCU128 为 MT40A512M16HA-075E |
| [genesys2.mig7s.prj](../target/xilinx/src/ips/genesys2.mig7s.prj) | Genesys2 DDR3 配置 MT41J256m16XX-107 |
| [vip_cheshire_soc.sv](../target/sim/src/vip_cheshire_soc.sv) | UseDramSys 分支选择外存仿真后端，两者均直接接主存 AXI 请求/响应 |
| [axi_sim_mem.sv](../.bender/git/checkouts/axi-ecdc900686449c15/src/axi_sim_mem.sv) | 字节索引关联数组、AXI 队列和握手，保存写数据并返回读数据 |
| [axi_dram_sim.sv](../.bender/git/checkouts/dram_rtl_sim-150825794ee29da3/src/axi_dram_sim.sv) | AXI 位宽转换到 512-bit、AXI-to-AXI-Lite、读写仲裁，再接 sim_dram |
| [sim_dram.sv](../.bender/git/checkouts/dram_rtl_sim-150825794ee29da3/src/sim_dram.sv) | DPI 调用 add_dram、dram_send_req、dram_can_accept_req、dram_has_read_rsp 等，接入 CTRL+DRAM 模型 |
| [dram_sim_engine.sv](../.bender/git/checkouts/dram_rtl_sim-150825794ee29da3/src/dram_sim_engine.sv) | 配合 DRAMSys 仿真时间推进 |

上述颗粒料号是脚本配置证据，不是本轮检查了板卡实物 BOM，也不是 ASIC 选型决定。

`UseDramSys` 是 testbench 参数，默认 0；启动脚本通过 `USE_DRAMSYS` 传入，见 [Questa 启动脚本](../target/sim/vsim/start.cheshire_soc.tcl)及 [VCS 启动脚本](../target/sim/vcs/start.cheshire_soc.sh)。它不改变实际硬件，也不会自动添加可综合 Controller。

| 选择 | 保留的行为 | 不应推导的能力 |
| --- | --- | --- |
| 0：axi_sim_mem | 按地址保存数据、WSTRB 字节更新、burst、ID、R/B 响应和握手 | 不建模 DDR bank/打开行/预充电/刷新；不能用于确认目标 DDR 性能 |
| 1：DRAMSys 后端 | 由配置描述的存储系统调度和 DRAM 时序，通过接收能力与响应时间反映到 AXI | 不是采购 Controller RTL 的等价实现，不验证 PHY 训练、电气波形和供应商寄存器 |

普通模型也有时钟和传输时序：AXI 请求何时接收、数据何时有效、接收方何时 ready。DDR 内部时序则涉及行激活、预充电、刷新、bank 冲突等。访问同 bank 不同行时，两种模型可能返回相同数据，却给出不同服务延迟。普通模型的 `ApplDelay/AcqDelay` 是时钟边沿后的驱动/采样偏移，不是 DDR 时序参数。

axi_sim_mem 的数组不会自动初始化或随复位清零；默认 VIP 关闭未初始化访问警告。该模块不支持 ATOP；当前主存路径的原子处理应结合 SoC 中 LLC 上游适配器理解，不能简单将 ATOP 直接送给模型。模型未限定为采购 DDR 的实际容量，必要的越界/错误/背压测试须另行设计。

DRAMSys 上游是 SystemC/TLM 模拟器。本地 [集成 README](../.bender/git/checkouts/dram_rtl_sim-150825794ee29da3/README.md) 描述 DRAMSys5.0；[构建配方](../.bender/git/checkouts/dram_rtl_sim-150825794ee29da3/dram_rtl_sim.mk) 固定提交 8e021ea 并打补丁，包含删除/重拉目录的操作，不能当作无副作用的查询命令。Bender.lock 为本地 Path，checkout 目录名后缀不是上游 commit 证据。DRAMSys 不自动继承 Vivado 的颗粒配置，适配器的转换/排队也影响测得的延迟。

### 2.2 ASIC DDR 模型尚未交付时

以下是推进建议，尚未实施：

1. 先复用普通 AXI 存储模型建立软件、数据流和互连功能基线，按目标接口补充容量边界、字节选通、burst、背压及错误用例。
2. 需要性能探索时再评估当前版本 DRAMSys；参数与负载必须匹配，结果不作为采购 IP 性能保证。
3. 提前向供应商获取 AXI 位宽/ID/在途数/协议子集、寄存器、Controller/PHY 配对、时钟复位、初始化/训练/ready/error 及模型工具支持。NPU/ISP 旁路属于额外互连与一致性设计，普通模型不会自动解决，见 [M01 契约](engineering/IP_DDR_Interface_Contract.md)。
4. 初始化代码及栈先位于可用 ROM/SPM，DDR 就绪并按要求检查后，才放行访问或往其中装程序、切栈。官方 Platform ROM 钩子适合平台早期配置；当前返回路径缺陷 S01-B01 及栈对齐复核仍需处理，见 [平台约定](03_Platform_ROM_Clock_IP_Configuration.md)。
5. 采购模型到位后验证真实 Controller/PHY/匹配颗粒的连接、初始化、访问、复位与错误场景。黑盒可服务前期综合结构检查；仿真数组不能充当最终 ASIC DDR，缺少时序/物理视图不能完成相关签核。

### 2.3 Flash、EEPROM 与 SD 的文件和实际使用

| 对象 | 器件模型及 VIP | HAL 源码及头文件 | 启动与写入入口 |
| --- | --- | --- | --- |
| S25FS512S | [s25fs512s.v](../target/sim/models/s25fs512s.v)；VIP 的 i_spi_norflash，CS1 | [spi_s25fs512s.c](../sw/lib/hal/spi_s25fs512s.c)、[头文件](../sw/include/hal/spi_s25fs512s.h) | boot_spi_s25fs512s / flash_spi_s25fs512s |
| 24FC1025 | [24FC1025.v](../target/sim/models/24FC1025.v)，模块 M24FC1025；VIP 的 gen_i2c_eeproms | [i2c_24fc1025.c](../sw/lib/hal/i2c_24fc1025.c)、[头文件](../sw/include/hal/i2c_24fc1025.h) | boot_i2c_24fc1025 / flash_i2c_24fc1025 |
| SD 卡 | 默认 VIP 无卡模型；[tb_cheshire_soc.sv](../target/sim/src/tb_cheshire_soc.sv) 在 boot_mode==1 时明确 $fatal | [spi_sdcard.c](../sw/lib/hal/spi_sdcard.c)、[头文件](../sw/include/hal/spi_sdcard.h) | boot_spi_sdcard / flash_spi_sdcard |

表中 `boot_*` 在 [cheshire_bootrom.c](../hw/bootrom/cheshire_bootrom.c)，`flash_*` 在 [flash.c](../sw/boot/flash.c)。模型由 [Bender.yml](../Bender.yml) 的 simulation/test 目标纳入。源文件存在、构建规则纳入与运行通过是不同证据。

Flash HAL 包含初始化、读取与擦除/编程；`single_read` 使用 0x13、4-byte 地址及 Standard 单线宽度，不是 Quad 读取。VIP 连接 SI/SO/WPNeg/RESETNeg/SCK/CSNeg，`spih_norflash_preload()` 直接把镜像装入模型 Mem 数组，这一步不经过 SPI 烧写。

EEPROM VIP 生成两颗，A0 不同、A1=0、A2=1；第 0 颗写保护，`i2c_eeprom_preload()` 只预加载第 0 颗。HAL 有初始化、读、写；当前配置 400 kHz，按该器件控制字/地址与页组织访问。模型与器件资料的版权/许可应保留，不因项目开源就抹去第三方许可边界。

SD HAL 包括 CMD0/CMD8/ACMD41 等初始化、512-byte 块读写和可选 CRC 处理；初始化时钟 200 kHz，API 限制目标 SPI 频率不超过 25 MHz。读路径将字节地址换成块号后构造命令，不能据此宣称所有 SDSC/SDHC/SDXC 型号均已兼容或验证。[FPGA top](../target/xilinx/src/cheshire_top_xilinx.sv) 在 USE_SD 下将 SCK→CLK、MOSI→CMD、MISO←DAT0、CS0→DAT3；DAT1/2 不参与四位传输。[板级教程](../docs/tg/xilinx.md) 的 SD 启动路径限定 Genesys2。

文档冲突：本地 [docs/um/sw.md](../docs/um/sw.md) 把 EEPROM 启动模式误写为 0b10；当前 Boot ROM C 的 case3 为 EEPROM，本文采用 0b11。该历史文档本轮未修改。替换 Flash/EEPROM 型号时，应核对命令、地址、容量、页/扇区、供电和时序；同为 SPI/I²C 不保证驱动兼容。

## 3. 其他接口的 RTL、仿真和软件支持

### 3.1 片上控制器与片外对象

控制器实例都可从 [cheshire_soc.sv](../hw/cheshire_soc.sv) 定位；是否实际启用还取决于有效配置。

| 接口 | 片上 RTL / 实例 | 可能的片外对象（示例，不是本工程选型） |
| --- | --- | --- |
| UART | reg_uart_wrap / i_uart | USB-UART 桥、MCU、串口模块 |
| JTAG | dmi_jtag / i_dbg_dmi_jtag，连接 Debug Module | 调试探针、USB-JTAG 桥 |
| Serial Link | serial_link / i_serial_link | 使用兼容协议的 FPGA 或 SoC；不是通用 UART |
| GPIO | gpio / i_gpio | LED、按键、开关、外设中断/复位/使能引脚 |
| VGA | axi_vga / i_axi_vga | 显示器；数字 RGB 还需板级模拟输出网络 |
| USB | spinal_usb_ohci / i_spinal_usb_ohci | USB 外设；具体类别还需相应软件支持 |
| SPI Host | spi_host / i_spi_host | Flash、SPI 模式 SD、其他 SPI 外设 |
| I²C | i2c / i_i2c | EEPROM、传感器、配置芯片等 |

SPI/I²C/GPIO 源位于本地 OpenTitan peripherals 的 [src](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/src)；从 SoC 实例沿模块定义追踪时应使用当前依赖，不套用其他版本。

### 3.2 仿真对端与检查入口

本节的 VIP 均指 [vip_cheshire_soc.sv](../target/sim/src/vip_cheshire_soc.sv)，fixture 指 [fixture_cheshire_soc.sv](../target/sim/src/fixture_cheshire_soc.sv)。SystemVerilog task 在仿真器中执行，不是目标 CVA6 的 C 软件。

| 接口 | 当前仿真实现 / 符号 | 能做什么及未覆盖边界 |
| --- | --- | --- |
| UART | uart_read_byte、uart_write_byte、uart_debug_rw、uart_debug_elf_run_and_wait | 接收/显示串口输出、发送字节、与目标 debug 服务配合装载运行；不代表所有流控/异常都已覆盖 |
| JTAG | JTAG_DV、jtag_test::riscv_dbg、jtag_init、jtag_read_reg32/write_reg32、jtag_elf_run、jtag_wait_for_eoc | 模拟外部调试器，经 DMI/调试逻辑访问并装载运行 |
| Serial Link | i_serial_link、slink_axi_driver、i_slink_rand_slv、slink_read_beats/write_beats、slink_elf_run、slink_wait_for_eoc | 兼容链路对端、AXI 激励和随机从端代理；此前“对端存储环境”的说法不精确，不能直接当作保存写数据的 RAM |
| GPIO | fixture 的 gpio_i='0，gpio_o/gpio_en_o 未接 | 默认环境没有按键激励或 LED 输出检查，仍可通过新增场景测试 |
| VGA | fixture 的 RGB/hsync/vsync 输出未接 | 没有默认显示器模型/画面检查器 |
| USB | fixture 的 usb_clk_i=0、usb_rst_ni=1，DP/DM 输入零、输出未接 | 没有有效 USB 外部交互环境 |
| SPI/I²C | Flash / EEPROM 引脚模型及 tristate 适配 | 覆盖当前器件交互，不是所有协议兼容器件的完整集合 |

Serial Link 对端的 AXI 输出接 `axi_test::axi_rand_slave`，配置有等待周期范围及 `RAND_RESP=0`，输入侧另有 AXI driver。不能把“有随机代理”直接当作全面协议覆盖或已通过压力测试。

[tb_cheshire_soc.sv](../target/sim/src/tb_cheshire_soc.sv) 在 `BOOTMODE=0` 下有明确调用：

| PRELMODE | 实际调用 |
| --- | --- |
| 0 | jtag_init → jtag_elf_run → jtag_wait_for_eoc |
| 1 | slink_elf_run → slink_wait_for_eoc |
| 2 | uart_debug_elf_run_and_wait |

三条路径都用于 ELF 装载与运行观察；BOOTMODE=1 的 SD 自主启动则被当前 TB 明确拒绝。Flash/EEPROM 的预加载任务由 TB 调用，为对应自主启动准备镜像。

### 3.3 软件入口与实际职责

| 接口 | 文件 | 实现职责和限制 |
| --- | --- | --- |
| UART | [uart.c](../sw/lib/dif/uart.c)、[uart.h](../sw/include/dif/uart.h) | 初始化、收发、flush；printf 最终通过 UART 输出 |
| UART debug | [uart_debug.c](../sw/lib/hal/uart_debug.c)、[头文件](../sw/include/hal/uart_debug.h) | 目标端 uart_debug_init/check/serve，提供内存读写和执行；与 VIP 客户端配合 |
| JTAG | [openocd.common.tcl](../util/openocd.common.tcl)、[openocd.hs2.tcl](../util/openocd.hs2.tcl)、[openocd.genesys2.tcl](../util/openocd.genesys2.tcl)、[flash_disk.gdb](../util/flash_disk.gdb) | 开发主机 OpenOCD/GDB 配置和装载/烧写组织，不是目标端 JTAG HAL |
| Serial Link | [serial_link.h](../sw/include/regs/serial_link.h)、[params.h](../sw/include/params.h) 的 __base_slink | 寄存器定义和地址入口；根 sw/lib 未见独立 slink HAL；VIP task 不能计为 C 驱动 |
| GPIO | [dif_gpio.c](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_gpio.c)、[头文件](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_gpio.h) 及同目录 autogen | 读写、输出使能、滤波/中断等；有驱动不代表默认 fixture 有外部激励 |
| VGA | [axi_vga.h](../sw/include/regs/axi_vga.h)、params.h 的 __base_vga；[cheshire.genesys2_vga.dts](../sw/boot/cheshire.genesys2_vga.dts) | 寄存器定义及 simple-framebuffer 描述；根 sw/lib 未见专用 VGA HAL；DTS 不执行硬件初始化，也不证明运行成功 |
| USB | params.h 的 __base_usb | 根裸机 sw/lib/hal、dif 未见专用 USB 主机栈；不扩大为依赖 SDK/Linux 没有 USB 驱动 |
| SPI Host | [dif_spi_host.c](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.c)、[头文件](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.h) | 控制器事务、配置等，下接硬件，上接器件 HAL |
| I²C | [dif_i2c.c](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_i2c.c)、[头文件](../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_i2c.h) | 控制器时序/FIFO/收发配置等，上层另处理器件协议 |

[sw.mk](../sw/sw.mk) 将 OpenTitan `base/*.c`、`dif/*.c`、`dif/autogen/*.c` 纳入软件构建规则，并生成 Serial Link/VGA 等寄存器头。头文件只定义地址/字段时，不等于提供初始化和完整驱动。[库接口参考](software/LIBRARIES.md)解释具体 API 与 printf 调用链。

## 4. Boot ROM、平台信号与扩展对象

| 对象 | 当前入口 | 分类和边界 |
| --- | --- | --- |
| Boot ROM | [cheshire_bootrom.S](../hw/bootrom/cheshire_bootrom.S)、[cheshire_bootrom.c](../hw/bootrom/cheshire_bootrom.c)、[生成 RTL](../hw/bootrom/cheshire_bootrom.sv)，SoC gen_bootrom | 片上启动存储；无须外部器件模型。它执行代码并调用驱动，从片外介质加载后续镜像 |
| Platform ROM | [官方随附集成说明](../docs/tg/integr.md)、[平台约定](03_Platform_ROM_Clock_IP_Configuration.md) | Cheshire 外围的平台启动入口，不必位于芯片外；当前返回路径缺陷及栈问题未验收 |
| 参考时钟/复位 | SoC clk_i/rst_ni；VIP clk_rst_gen；FPGA clkwiz/复位逻辑 | 外部振荡器/复位电路由具体平台决定，仿真信号发生器不是特定器件型号 |
| RTC 时基 | rtc_i；FPGA rtc_clk_q | 当前 FPGA 内部分频产生，不能推导已有日历 RTC 芯片 |
| 启动配置 | boot_mode_i，VIP set_boot_mode，FPGA 平台配置 | 可来自配置引脚或板级控制；不是存储器 |
| 外部 AXI/Reg/中断 | axi_ext_*、reg_ext_*、intr_ext_* | 可连接 Cheshire 外围的片上 IP，不天然属于片外层 |
| LVDS 图像输入 | 规划中的传感器接口 | 尚未实现和选定全部参数；ISP/NPU/GB 是拟议片上对象 |

软件访问关系示例：`应用/Boot ROM → 器件 HAL → SPI/I²C DIF → MMIO → 控制器 RTL → 引脚 → 器件`。UART 普通输出可直接走 `printf → UART DIF`。仿真端客户端与目标端程序分属不同执行环境。

## 5. FPGA 与 ASIC 的支持边界

[phy_definitions.svh](../target/xilinx/src/phy_definitions.svh) 中 VCU118 启用了 DDR4、QSPI、JTAG 等，未启用 USE_I2C/USE_SD/USE_VGA/USE_USB；Genesys2 则定义了后几项。UART 端口不通过这些宏控制，不能因宏列表未出现 UART 就判断其不存在。[FPGA top](../target/xilinx/src/cheshire_top_xilinx.sv) 将 Serial Link 输入绑常量、输出未接。GPIO 在默认仿真 fixture 中无外部场景。

USB 的数字 DP/DM 接线、VGA 的数字 RGB、SPI/I²C/GPIO 输出使能不等于 ASIC 电气接口已经完整。真实实现须按平台核对 PAD、电压、模拟输出/收发、上拉、供电与封装板级条件。UART/JTAG 的桥接器具体料号应查目标板原理图，当前核查没有确认这些器件型号。

本项目已有 VCU118 HelloWorld 为用户报告，不能扩大成全外设、Ara、DDR 全功能或 ASIC 就绪。判断是否要补仿真，应问“目标功能需要什么外部行为，当前是否有激励和结果检查”，而不是按存储器/通用接口类别推断覆盖。

## 6. 官方补充资料与维护

- [Cheshire 官方仿真](https://pulp-platform.github.io/cheshire/tg/sim/)：USE_DRAMSYS 与装载入口；具体配置以本地源码为准。
- [Cheshire 官方系统集成](https://pulp-platform.github.io/cheshire/tg/integr/)：外部系统集成、VIP 与 Platform ROM。
- [DRAMSys 官方仓库](https://github.com/tukl-msd/DRAMSys)：SystemC/TLM 存储系统仿真；不是可综合 Controller 交付。
- [Infineon S25FS512S 数据手册](https://www.infineon.com/assets/row/public/documents/10/49/infineon-s25fs512s-512-mb-1-datasheet-en.pdf)：512 Mbit、1.8V SPI NOR 系列；型号后缀及模式按实际采购核对。
- [Microchip 24FC1025](https://www.microchip.com/en-us/product/24FC1025)：1 Mbit、128-byte 页及 I²C 器件说明。

本文承接连续答疑的技术结论；实现和文档变更记录见[主题交接](handoffs/L01_interface_reference.md)。以后同主题补充优先更新本页和页首修改记录，避免在 handoff 中再复制整份技术说明。新的测试结果必须另有输入版本、命令与日志证据。
