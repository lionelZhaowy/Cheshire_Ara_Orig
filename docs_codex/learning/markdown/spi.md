# 20 · SPI、NOR 与 SD

SPI 控制器事务与 NOR、SD 设备协议。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/spi.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../spi.html) · [阅读路线](index.md)

- [20.1 NOR Flash 的已知数据读取](#read-task)
- [20.2 SPI 命令、地址与数据的片选连续性](#transaction)
  - [20.2.1 SPI 设备操作与事务分段](#segments)
- [20.3 SPI 控制器的读取流程](#controller)
  - [20.3.1 SPI 控制器的资源与配置](#host)
  - [20.3.2 配置、命令和数据寄存器](#register-contract)
  - [20.3.3 控制寄存器与初始化](#init)
- [20.4 NOR Flash 的软件调用链](#devices)
  - [20.4.1 初始化、读取、校验和结束](#nor)
  - [20.4.2 SPI 总线上的 SD 协议](#sd)
- [20.5 模型条件与后续验证](#verification)

**本章任务**

在同一次片选区间内完成 NOR 的命令、地址和 16 字节数据读取。前置：[MMIO/FIFO](uart-gpio.md#registers)；SD 留作后续协议扩展。

<a id="read-task"></a>

## 20.1 NOR Flash 的已知数据读取

SPI 是由 host 提供时钟和片选的串行接口，可以连接 Flash、采样器等设备；只有各器件规定的命令才能赋予字节含义。本工程实际有 S25FS512S NOR HAL 和 VIP 模型，主线选择读取地址 0 的 16 字节。[Infineon S25FS512S 官方数据手册](https://www.infineon.com/assets/row/public/documents/10/49/infineon-s25fs512s-512-mb-1-datasheet-en.pdf)给出该系列 512 Mbit（64 MiB）、1.8 V 类供电及串行命令；这不是所有 SPI Flash 的兼容保证，也不是实际板载完整订货号确认。

最小单线连接以 SoC 为参照：sck\_o 为时钟输出，csb\_o\[1\] 选中 NOR；sd\_o\[0\] 送器件 SI，sd\_i\[1\] 收 SO。sd\[3:0\] 的值/输入/使能由模式决定方向，SPI 不像 I2C 那样全线开漏；未选器件需释放共享返回线。VIP 接 WPNeg 到 sd2、RESETNeg 到 sd3，经三态和上拉保持适当非活动电平。实际器件的电源、WP#/RESET# 与 PAD 电压必须按板级核对。

VCU118 配置启用 QSPI/STARTUPE3，wrapper 将 CS1 路由到 FPGA 配置引脚通道；CS0 用于可选 SD，当前未启用 USE\_SD。这说明存在 QSPI 路由，不说明 NOR 模型等于本板实际芯片，也不授权对板上配置 Flash 擦写。

<a id="transaction"></a>

## 20.2 SPI 命令、地址与数据的片选连续性

读操作先拉低 CS1，发送 opcode 0x13，再发送四字节 Flash 内部地址，接着 host 提供时钟、NOR 返回 16 字节，最后释放 CS1。命令和地址走输出，数据走输入；地址 0 是器件内位置，接收数组是 RAM，CPU 配置控制器的 MMIO 地址又是第三种地址。

<a id="segments"></a>

### 20.2.1 SPI 设备操作与事务分段

TXDATA(+0x30) 将字节放进发送队列，COMMAND(+0x28) 决定怎样移出：LEN\[8:0\] 通常是字节数减一，CSAAT9 控制段结束后保持片选，SPEED\[11:10\] 与 DIRECTION\[13:12\] 选择线数和方向。dummy 段以时钟周期描述空转，不能把所有长度都当字节。RXDATA(+0x2c) 读出接收 FIFO。

DIF 的 transaction 接口把 opcode、address、dummy、data 等 segment 排成命令。NOR 的单线读取使用 0x13、四字节器件内部地址、接收 len 字节，前三者需要在同一选中区间内按序完成。CSID(+0x24) 选器件，CSAAT 保持跨段片选，最后一段释放；提前释放会使器件把剩余字节解释成新命令。

<a id="controller"></a>

## 20.3 SPI 控制器的读取流程

<a id="lab"></a>

<a id="host"></a>

### 20.3.1 SPI 控制器的资源与配置

SPI 由 host 驱动 SCK 和片选 CS，通过数据线移位。CPOL 选择空闲时钟电平，CPHA 选择采样相位；多数据线模式还改变每个时钟传多少位。`Cfg.SpiHost` 选择本地 OpenTitan spi\_host，其寄存器、命令 FIFO、TX/RX FIFO、移位器和状态机构成传输通路。

生成包 NumCS=3，最后一项为 dummy CS，对外有 2 个有效片选；当前 NOR 模型接 CS1。头文件对应 TX=72、RX=64 个 32 位字，命令队列深度为 4。扩大 FIFO 或片选需要同步生成配置与驱动，单次访问长度还受到 FIFO、命令字段和软件分块限制。

<a id="register-contract"></a>

### 20.3.2 配置、命令和数据寄存器

Reg32 控制访问采用 32 bit；CONTROL 中 SPIEN、SW\_RST、OUTPUT\_EN 复位为 0。SW\_RST 只重置控制器内部状态，外部器件另有上电/复位和协议状态。STATUS 是 RO 反馈，CONFIGOPTS/CSID 为配置，COMMAND 写入有提交副作用，RXDATA 读弹出，TXDATA 写入排队。寄存器分组见[SPI 索引](registers.md#group-4)。

<a id="init"></a>

### 20.3.3 控制寄存器与初始化

基址 0x03004000 的 CONTROL(+0x10) 包含 SPIEN31、SW\_RST30、OUTPUT\_EN29。初始化先复位并配置每个 CS 的 CONFIGOPTS（+0x18/+0x1c/+0x20），设分频、CPOL/CPHA 和片选建立保持，再开放控制器与输出。STATUS(+0x14) 的 READY 表示控制器可接受命令，ACTIVE 表示内部活动；外部 Flash 忙需要器件状态命令查询。

gen\_spi\_host/i\_spi\_host 使用 clk\_i/rst\_ni，后者低有效。DIF 按 divider=((core\_hz/spi\_hz)/2)-1 取整数，SCK 由 core\_hz/\[2×(divider+1)\] 得到，不能把目标频率当成连续精度保证。系统时钟驱动寄存器/FIFO，SCK 驱动线上位传输。本例目标 1 MHz，CPOL=0/CPHA=0，CS 建立/保持/空闲计数由 HAL 设置。设备外部复位需满足手册，不由 SW\_RST 代替。

<a id="devices"></a>

## 20.4 NOR Flash 的软件调用链

<a id="nor"></a>

### 20.4.1 初始化、读取、校验和结束

应用 [storage\_read.c](../examples/storage_read.c) → [NOR HAL 头文件](../../../sw/include/hal/spi_s25fs512s.h) / spi\_s25fs512s.c → dif\_spi\_host\_transaction → 控制器 MMIO。HAL 产生 0x13 与四字节地址，DIF 把三段变成 TX/RX 队列和 COMMAND。库只是这些函数的链接载体，不是额外的运行代理。

前提是 Cfg.SpiHost、VIP 的 CS1 NOR 和默认 0x9a 填充。程序由 RTC 测得 core\_hz，设置 spi\_freq=1000000、csid=1，调用 spi\_s25fs512s\_init，再 single\_read(&dev,bytes,0,16)。init 校验频率/片选并复位整个 host；两函数返回 int，0 为函数完成其流程。缓冲必须有 16 个可写字节，地址和长度都以字节计；HAL 按 RX 容量 64×4=256 字节分块。

DIF 提交命令并轮询取回接收数据，调用返回并不替代数据校验。逐字节确认 0x9a，输出 STORAGE stage=5 bytes=16 errors=0，UART flush，返回 0。此读操作没有 program/erase 的器件内部忙周期；若讨论写入，则 READY（能接命令）、ACTIVE（控制器活动）和器件 WIP（内部写忙）必须分别判断。实际步骤见[实验 D](labs.md#lab-d)，本轮未运行该 SoC 场景。

同一 host 多个 CS 可以有不同 CONFIGOPTS；切换应在上一个事务结束后进行。器件 HAL init 会重置共享 FIFO，不能在另一个 CS 正传输时重调；当前轮询库没有给出并发任务调度层。PLIC 源 17/18 分别服务错误/事件，不能把它们称为已实现的 DMA 完成驱动。

当前无统一有界等待，NOR 写路径另有静态缺陷；主线限定只读且需外层运行超时，写/擦除不列为可执行例。详见[SPI 诊断](peripheral-debug.md#spi)。

<a id="sd"></a>

### 20.4.2 SPI 总线上的 SD 协议

本地 SD 是 `spi_sdcard.c` 在 SPI host 上的软件协议，不是独立 SDIO 控制器。初始化先提供空时钟，经 CMD0 进入状态、CMD8 检查响应、CMD55+ACMD41 轮询激活，再用 CMD58 确认状态。块读写还涉及数据 token、命令 CRC7、数据 CRC16、忙等待、卡类型及块/字节寻址。

驱动的 csaat 传输保持命令多段的片选，csfree 通过 dummy CS 额外提供 8 个时钟，让卡释放数据线。配置实际卡片时，CSID、频率和超时单位要与板级接线匹配。函数返回码要汇总响应、CRC 和数据结果，初始化结束只是后续块读的前提。

<a id="verification"></a>

## 20.5 模型条件与后续验证

当前 VIP 有 NOR 模型与默认预填充，没有同等的 SD 模型；TB 对 SD 启动直接 fatal，VCU118 当前未启用 USE\_SD。已有 SD 源码可以用于协议阅读，端到端实验需先补卡模型或已确认的板端环境。最小验收应包含已知扇区 512 字节及 CRC 正确、缺卡/忙超时失败，两者分别记录。

本章不再为“搜索一次命令名”单设实验。阅读时沿 init → transaction → FIFO → COMMAND → 引脚追踪一次 16 字节 NOR 读取，再回到实验 D 执行构建与条件运行。完整字段按需查[SPI 寄存器索引](registers.md#group-4)。

**源码与进一步阅读**

[SPI 访问、复位和字段](../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/src/spi_host/data/spi_host.hjson)；[NOR 协议与分块](../../../sw/lib/hal/spi_s25fs512s.c)；[SD 初始化、CRC 和片选](../../../sw/lib/hal/spi_sdcard.c)；[控制器事务 API](../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/dif/dif_spi_host.c)；[FIFO 与状态机](../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/src/spi_host/rtl/spi_host_core.sv)；[SpihNumCs](../../../hw/cheshire_pkg.sv)

**COMMAND 提交后为什么仍要接收和校验？**

提交表示控制器获得工作描述；RX 数据回收才得到结果，逐字节比对才判断器件内容正确。

---

[上一页：I2C 与 EEPROM](i2c.md) · [下一页：Serial Link、VGA 与 USB](stream-io.md)
