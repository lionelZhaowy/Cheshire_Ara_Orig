# 14 · Boot ROM、启动模式与应用初始化

ROM 服务、程序装载与应用入口的执行关系。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/boot.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../boot.html) · [阅读路线](index.md)

- [14.1 默认 ROM/JTAG 启动的输入与目标](#default-path)
- [14.2 Boot ROM 的片上环境初始化](#rom)
  - [14.2.1 固化启动代码、外部镜像与执行存储](#rom-and-media)
  - [14.2.2 Boot ROM 的早期存储与栈](#rom-initial-state)
  - [14.2.3 JTAG 装载与应用入口交接](#default-load)
- [14.3 应用入口与运行交接](#application)
  - [14.3.1 应用启动代码建立 C 环境](#crt)
  - [14.3.2 系统寄存器参与初始化与结束](#regs)
  - [14.3.3 程序结果校验与运行结束判据](#normal-result)
- [14.4 平台初始化扩展与程序装载方式](#boot-compare)
  - [14.4.1 Platform ROM 与 Boot ROM 的调用关系](#platform-rom)
  - [14.4.2 装载路径比较](#load-path-overview)
- [14.5 被动加载服务](#other-loaders)
  - [14.5.1 Serial Link：远端写入与 scratch 交接](#serial-link)
  - [14.5.2 UART：二进制读写与调用协议](#uart-passive)
- [14.6 自主介质启动](#media-boot)
  - [14.6.1 GPT/raw 镜像格式与 SPM 装载](#gpt-raw)
  - [14.6.2 SPI SD：块读取与 CRC](#sd-boot)
  - [14.6.3 SPI NOR：地址读取与器件配置](#nor-boot)
  - [14.6.4 I2C EEPROM：器件地址与内部地址](#eeprom-boot)
- [14.7 多阶段启动与大型镜像装载](#boot-growth)
  - [14.7.1 ZSL、OpenSBI 与操作系统启动的分层](#later-stages)

**本章任务**

先连续理解默认 ROM/JTAG 到 main 的一次启动，再比较平台钩子和其他装载方法。前置：[裸机 C 程序运行模型](runtime.md)、[工具链、链接与 ELF](build.md)及[存储层次与 SPM](memory.md)。

<a id="default-path"></a>

## 14.1 默认 ROM/JTAG 启动的输入与目标

假定使用已配套的单核标量设计，Bootrom=1、PlatformRom=0、内部 LLC 保留为 SPM，RTC、UART 与 JTAG 可用；应用是同一目录生成的 `journey.spm.elf`。主机已经完成编译链接，ELF 入口和装载地址由 spm.ld 确定。此刻文件仍在主机磁盘，CVA6 没有执行其中任何代码。

目标从复位开始执行自己的 Boot ROM。ROM 先使片上存储可用；仿真 VIP 经 JTAG 请求暂停，再通过 Debug Module 把 ELF 段搬到 SPM，设置应用入口并恢复 CPU。之后由应用 crt0 建立 C 环境、调用 main，main 计算并输出结果。先把这条路径读完，再看 UART、Link 或介质怎样替换装载者。JTAG 详细握手与板上调试工具将在[调试章](boot-debug.md)展开。

<a id="rom"></a>

## 14.2 Boot ROM 的片上环境初始化

<a id="rom-and-media"></a>

### 14.2.1 固化启动代码、外部镜像与执行存储

CPU 复位后的 BootAddr 默认是 `0x02000000`，指向固定 Boot ROM。ROM 是目标CPU立即可取指的启动程序；SPM 是稍后放入应用字节的运行存储；主机上的 ELF 是待装载文件。三者的名称和地址分别对应代码的来源、所在位置与格式。即使 ROM 和应用都使用名为 \_start 的符号，它们也属于不同映像，不会在一次应用链接中合并。

ASIC 中固定 ROM 内容需要在实现/制造前确定，具体可以映射为常量逻辑或 ROM 宏；FPGA 可通过重新生成硬件映像更新相应内容。外部 NOR/EEPROM 则可用规定流程更新程序镜像。更新外部镜像之所以有用，正是因为固定加载器能够读取不同的后续程序。

<a id="rom-initial-state"></a>

### 14.2.2 Boot ROM 的早期存储与栈

在默认保留内部 LLC（`LlcOutConnect=1、LlcNotBypass=1`）的配置下，`cheshire_bootrom.S` 等待 LLC 内建自测（BIST）完成，设置 CFG\_SPM 的 way 位图并提交配置。默认 8 个 way 全部作为 SPM。随后用 LLC\_SIZE 把早期栈放到阵列高端，128 KiB 时相应早期 sp 为 0x1001fff8。平台 ROM 若被配置，则按源码约定调用；默认无平台钩子时直接进入 \_boot 并调用 ROM 自己的 main。应用 crt0 的 24 字节保存动作发生在后续应用入口，不能当作 ROM C 调用前的调整；对应对齐缺口见[栈检查](software-debug.md#stack-handoff)。

Boot ROM 的 C 代码负责启动策略。模式 0 提供被动加载服务，模式 1/2/3 分别访问 SPI SD、SPI NOR 和 I2C EEPROM。JTAG VIP 等待 LLC 的 SPM 配置标志后就请求 halt，因而主线无需假设 ROM 的 C main 已执行完。删除 LLC 或改变其阵列容量会同时改变这里的启动存储和栈条件。

<a id="default-load"></a>

### 14.2.3 JTAG 装载与应用入口交接

VIP 的 `jtag_elf_halt_load` 在内部 LLC 路径轮询 CFG\_SPM\_LOW.bit0，随后请求 hart0 暂停并等待 allhalted。主机侧 elfloader 解析 ELF 的 PT\_LOAD 段，VIP 通过 Debug Module 的系统总线访问口写入目标地址。ELF entry 随后写入 DPC，即调试恢复 PC；恢复执行后，CVA6 开始取应用 \_start 的机器指令。

这个过程有两个必须分别满足的前提：目的存储已经可写，以及应用入口所需的栈/状态已经成立。当前 VIP 对 SPM 配置位的等待不覆盖后续栈建立步骤；spm.ld 的零栈符号表示应用继承进入时的 sp，因此应核对实际暂停 PC、sp 和有效栈区。主机能够写入段，不会自动替 CPU 建立栈。相关本地限制详见[继承栈诊断](software-debug.md#stack-handoff)。

<a id="application"></a>

## 14.3 应用入口与运行交接

<a id="crt"></a>

### 14.3.1 应用启动代码建立 C 环境

应用 crt0 首先关闭 M/S 全局中断并停住非零 hart。机器态（M）、监管态（S）和用户态（U）是 RISC-V 的权限层级，本书沿机器态裸机路径。crt0 根据非零栈符号决定是否换栈，建立 gp（访问全局数据的辅助指针），保存进入时的 sp、设置后的 gp 和返回地址 ra（不是完整处理器上下文），再把 mtvec 设为异常入口。

接着清除 \_\_bss\_start 到 \_\_bss\_end，把 result 等零初始化对象置零；设置 FS 并初始化浮点寄存器，然后 fence 并 call main。即使 C 只做整数运算，当前原始 crt0 仍执行双精度浮点指令，所以本例要求 F/D 硬件。VS 未在原 crt0 统一设置，向量变体由标量 main 在调用向量函数前开启。

异常是当前指令引起的事件，如非法指令或访存失败；中断是计时或设备等异步事件。两者统称 trap。CPU 把原因和位置记入 mcause、mepc、mtval 等 CSR，并跳到 mtvec。正常返回还需入口汇编与 handler 配合保存现场。本地弱 trap\_vector 默认自循环；本例的正常计算不使用异常服务，若触发 trap 则不具备自动恢复条件，见[对应诊断](software-debug.md#trap-stop)。完整机制见[异常与上下文](traps.md#software-context)。

<a id="regs"></a>

### 14.3.2 系统寄存器参与初始化与结束

SoC 寄存器位于 0x03000000。它们向软件提供硬件信息，避免把某个平台频率硬编码进每个应用。RTC\_FREQ（+0x44）供 CLINT 测频使用；NUM\_INT\_HARTS（+0x4c）报告核数；HW\_FEATURES（+0x50）报告配置能力；LLC\_SIZE（+0x54）报告阵列容量。容量和当前 way 用途需分别查询，硬件能力位还需结合引脚、时钟和设备模型理解。

scratch0..15 每项 4 字节，是 SoC 的通用读写寄存器；低几个槽由当前固件约定承担启动交接。它们只有少量信息容量，不是存放程序和数组的 scratchpad memory（SPM），也不是 CPU 的 mscratch CSR 或 Debug Module 的调试寄存器。名称相似不代表地址、容量或用途相同。

主线程序读取 RTC\_FREQ，用 RTC 与 mcycle 测系统频率，再配置 UART。printf 把结果变成字符，经 \_putchar、uart\_write、MMIO 写到 UART，VIP 采样串行数据并在换行后输出日志。返回前调用 uart\_write\_flush，确保末尾字符发完。

main 返回值在 a0；应用返回 0 是逐项检查通过的判据，非零是失败码。crt0 的 \_exit 把 `(返回值 << 1) | 1` 写到 scratch2（+0x08）。VIP 观察 bit0，右移得到返回码；0 输出 \[JTAG\] SUCCESS，非零输出 FAILED。随后 \_exit 的实际指令为 ret，验收应以完成寄存器和日志为准；调用者若希望收回执行权，还需事先建立有效返回地址。这个协议相当于测试环境的程序结束通知，不是操作系统的 exit 服务。

<a id="normal-result"></a>

### 14.3.3 程序结果校验与运行结束判据

本章主线的成功结果不是只出现 Hello。journey 先检查 seed 与 result 的启动初值，再计算和逐项检查 137 个整数，打印 `LEARN sum=28085 errors=0`，等待 UART 发送空闲，最后返回 0。VIP 从 SCRATCH2 读到完成标志和 0 返回码才报告 JTAG SUCCESS。输出正确而返回非零、返回 0 却没有预期逐项检查日志，都不足以验收这个指定程序。

这里是由当前源码推导的预期过程。本轮没有重新构建或执行目标；已有加载器段尾、继承栈等限制仍须在目标验收中核实，入口见[已知问题表](software-debug.md#known-issues)。后续几条启动路径只改变谁搬运、从哪里取镜像和怎样交接入口；应用的 C 环境和结果责任继续存在。

<a id="boot-compare"></a>

## 14.4 平台初始化扩展与程序装载方式

<a id="platform-rom"></a>

### 14.4.1 Platform ROM 与 Boot ROM 的调用关系

Platform ROM 是集成平台提供的早期代码入口，用于处理通用 Boot ROM 无法预先知道的 PLL、PAD、存储或其他 IP 初始化。Cheshire 不因为配置这个地址就生成这份 ROM；wrapper 还需提供内容、可取指的地址映射，以及所需控制寄存器。两段代码由同一个 CVA6 执行，Platform ROM 不是独立运行的管理核。

| 配置情况 | 当前代码路径 | 平台责任 |
| --- | --- | --- |
| Bootrom=1，PlatformRom=0 | CPU 进入自带 ROM，跳过平台钩子后进入通用启动流程 | 默认路径；平台提前满足所选启动方法需要的时钟、IO 和存储条件 |
| Bootrom=1，PlatformRom≠0 | 若内部 LLC 存在，ROM 初始化 SPM 并调整栈，再经 jalr 调用；无内部 LLC 的合法配置跳过这段初始化 | 首次栈访问前须有可写存储和有效 sp；无内部 LLC 时由平台保证。正常返回另受下述缺口限制 |
| Bootrom=0 | SoC 把 CPU BootAddr 设为 Cfg.PlatformRom | 平台入口直接承担第一阶段启动，不可假设内置 ROM 已建立栈和 SPM |

**栈的成立条件：**ROM 先执行 `la sp, __stack_pointer$`，只是把链接值写入寄存器。随后检查 `HW_FEATURES.llc`；该位为 0 就跳到 `_prom_check_run`，跳过 BIST、SPM 配置和按 LLC\_SIZE 调整栈。`cheshire_bootrom.ld` 的默认栈值指向 SPM 区域，加载这个值本身不能使对应存储可写。

例如 `LlcOutConnect=1、LlcNotBypass=0` 保留外存出口但没有内部 LLC/SPM。平台可以提前提供覆盖栈地址的替代可写存储，或让 Platform ROM 先执行不依赖栈的早期汇编，建立替代存储并设置满足 ABI 的 sp，再调用需要栈的 C 程序。这一责任同样适用于 `Bootrom=1`；若 PlatformRom=0，进入通用 ROM C 代码前也需要平台满足栈前提。`LlcOutConnect=0、LlcNotBypass=1` 的不一致组合仍应排除，不能据 feature 位推断真实实例存在。

依据：[\_start 的栈赋值、HW\_FEATURES 分支与 \_prom\_check\_run](../../../hw/bootrom/cheshire_bootrom.S)；[\_\_stack\_pointer$](../../../hw/bootrom/cheshire_bootrom.ld)；[gen\_llc / gen\_llc\_bypass 及 hw\_features.llc](../../../hw/cheshire_soc.sv)。以上为源码静态确认，未新增平台启动实测。

`Cfg.PlatformRom` 是硬件配置输入，SoC 把它反映到只读 `PLATFORM_ROM` 信息寄存器。应用不能通过写这个信息寄存器更换钩子地址。固定的是 ROM 指令和钩子配置；ROM 执行寄存器写入所建立的 PLL、PAD 或外设状态能否在运行时修改，则由对应 IP 的控制接口、锁定位和时钟依赖决定。沿官方平台钩子进行早期 PLL/IP 配置是本项目已确认的待实现方向，具体频率与 IP 仍未冻结，见[启动频率与运行时调频](clocks.md#boot-and-runtime-frequency)。

**适用范围：**当前非零 PlatformRom 的正常返回路径存在已确认缺陷，尚未修复；启用该钩子前需完成独立修复及回归。默认 PlatformRom=0 不进入此路径。详细控制流、生成 ROM 证据和上游修复见[软件诊断](software-debug.md#platform-rom-return)。

源码静态确认：[BootAddr](../../../hw/cheshire_soc.sv)、[\_prom\_check\_run / boot\_next\_stage / \_boot](../../../hw/bootrom/cheshire_bootrom.S)、[PLATFORM\_ROM 只读属性](../../../hw/regs/cheshire_regs.hjson)。依据与修复建议详见[Platform ROM 专题](../../03_Platform_ROM_Clock_IP_Configuration.md)。

<a id="load-path-overview"></a>

### 14.4.2 装载路径比较

复位 PC 进入 ROM 后有两种推进方式：ROM 继续建立栈、进入 C main 并读取模式/测频，服务 UART/Link 或自主介质；JTAG 则由外部 VIP 在自身条件满足后暂停并接管。当前 VIP 只在 LlcNotBypass 时轮询 CFG\_SPM\_LOW.bit0，没有等待 ROM C 或测频完成，也不能由这个配置位推出后续栈初始化已经结束。不同介质最终都要让程序字节落到可执行存储、确定入口并转交控制。文件格式、介质读取和入口选择分别完成，不能把主机读 ELF 的逻辑想成 CPU 自动解析 ELF。

| 装载来源 | 谁解释格式并搬运 | 入口与完成交接 |
| --- | --- | --- |
| 默认 JTAG | 主机 elfloader 解释 ELF；VIP/DM 经 SBA 写目标存储 | ELF entry → DPC → resume；当前等待条件见前文 |
| Serial Link | 外部主设备把各段写到已就绪存储 | scratch0/1 给入口，scratch2 掩码 2 通知 ROM |
| UART 被动服务 | 主机发送带地址/长度的二进制命令；ROM 接收字节 | EXEC 的 addr64 指定入口；服务返回 EOC 和返回值 |
| SPI SD / SPI NOR / I2C EEPROM | ROM 的控制器/器件驱动读取介质，GPT/raw 解释载荷 | 载荷放到 SPM code\_buf 起点，再从该处执行 |

<a id="other-loaders"></a>

## 14.5 被动加载服务

BOOT\_MODE=0 使 ROM C 进入 boot\_passive。ROM 完成测频并初始化 UART 后，轮询 scratch2 的掩码 2 和 UART 握手字节。PRELMODE 是 testbench 选择外部装载方式的参数；它与硬件 BOOT\_MODE 是不同输入。JTAG 接管前提见[调试章](boot-debug.md#takeover)。

<a id="serial-link"></a>

### 14.5.1 Serial Link：远端写入与 scratch 交接

**选择与搬运：**仿真 PRELMODE=1 由 VIP 通过 Link 对端发送 AXI 写；ROM 处于被动模式。主机侧解析 ELF，按目标段地址写入可用存储；ROM 本身不解析 ELF。地址译码、目标可写性及完成应答须由装载者核对。

**入口交接：**写数据完成并满足可见性约定后，装载者把入口低/高 32 位放入 scratch0/1，再向 scratch2 写掩码 2。ROM 测试的是 bit1，清 scratch2 后把 scratch1:0 拼为 64 位地址，调用 boot\_next\_stage。代码某些注释写 bit2，本书按表达式解释。入口必须指向已装载的可执行代码。

**适用与结果：**当前 VIP 有 Link 对端，VCU118 没有已建立的 Link 板端闭环。数据写完成后才能发布入口和启动通知；成功仍以应用数据和退出码判断。链路机制见[Serial Link 章](stream-io.md#link)，日志适配边界见[装载诊断](software-debug.md#alternate-loaders)。

<a id="uart-passive"></a>

### 14.5.2 UART：二进制读写与调用协议

**选择与格式：**ROM 被动服务收到 0x06 后回 ACK=0x06；PRELMODE=2 的 VIP 使用该服务。READ=0x11 带 addr64/len64，WRITE=0x12 带 addr64/len64 和数据，EXEC=0x13 带 addr64。本地服务直接收进 uint64\_t，主机应按该目标的小端字节顺序发送字段；终端发送 ELF 文件的原始字节不能构成这些命令。

**装载与交接：**WRITE 解析地址和长度后先 ACK，再把指定字节接收到该地址，结束回 EOT=0x04。装载者负责合法目标范围与各段/BSS 策略；服务没有 ELF 格式验证或完整地址白名单。EXEC 经 ACK、fence 后 invoke 指定地址；被调用代码返回时发送 EOC=0x14 和 32 位返回值。它与 scratch2 退出协议应分别观察。

**适用与结果：**115200 波特率依赖 ROM 测频及 UART 初始化；主机需匹配字节顺序、长度和超时。ACK 表示接受阶段，EOT 表示一次数据命令结束，EOC 及返回值表示被调用代码已返回，三者不能互换。主线实验没有新验收 UART 装载。协议依据为[uart\_debug\_serve](../../../sw/lib/hal/uart_debug.c)，配置见[UART 初始化](uart-gpio.md#uart-init)。

<a id="media-boot"></a>

## 14.6 自主介质启动

<a id="gpt-raw"></a>

### 14.6.1 GPT/raw 镜像格式与 SPM 装载

ROM 用 HAL 回调读取介质字节。gpt\_boot\_part\_else\_raw 先查 LBA1 的 GPT 签名（每 LBA 512 字节）；有签名时找符合类型/分区 GUID 和大小条件的分区，未找到符合条件的项时沿本地实现回退首分区截取范围；无签名则从介质偏移 0 读 raw 区。该简化实现不应当作完整 GPT 完整性或镜像认证机制。

默认 max\_lbas=96，原始路径读取 48 KiB；分区路径按含末尾 LBA 的区间读取，载荷上限同样受此值约束。目的地址为 &\_\_base\_spm，随后 boot\_next\_stage(code\_buf) 从缓冲起点执行，不从 ELF header 取 entry。连续镜像须把入口放在所约定起点并满足运行布局；rom.ld 用于 SPM 运行、外部镜像装载。教材 spm.ld 的 64 KiB 链接区是另一层约束。

跳转前函数把读取回调、设备私有指针和 gp 约定写进 scratch0/1/3，供后续阶段使用；这些槽在不同启动阶段的含义不同。根软件通用 GPT 打包规则当前已注释，ROM 解析代码仍保留。以下三路只更换设备初始化与 read 回调，镜像解释和入口规则共用本节。

**正常计时语义：**[clint\_spin\_until(tgt\_mtime)](../../../sw/lib/dif/clint.c) 等待绝对 mtime 阈值，阈值已过会立即返回；clint\_spin\_ticks(ticks) 才从调用时刻计算相对等待。下面的 SD/NOR 记录按当前真实调用解释，器件所要求的相对上电/命令等待仍需核验，见[实现差异与验证条件](software-debug.md#media-start)。

<a id="sd-boot"></a>

### 14.6.2 SPI SD：块读取与 CRC

**选择：**BOOT\_MODE=1 调用 boot\_spi\_sdcard；CS0，目标 SPI 24 MHz，另有 dummy CS。ROM 先用 HAL 完成卡初始化，再调用 `clint_spin_until((1000 * rtc_freq) / 1000000 + 1)`，等待 mtime 达到该绝对阈值，并非从初始化结束起再等 1 ms；**输入和装载：**spi\_sdcard\_read\_checkcrc 提供按字节范围读取的回调，底层以卡块传输并检查 CRC，共同加载器把 GPT/raw 载荷放到 SPM 起点；**入口：**成功读取后进入 boot\_next\_stage。

**适用范围：**当前 TB 不支持 BOOTMODE=1，因而这是现有 ROM 路径的源码教学，不能直接作为本地 SD 仿真配方。完成条件包括介质读取/CRC 有效、载荷完整、应用结果正确。具体命令见[SPI SD 协议](spi.md#sd)，验证缺口见[介质启动诊断](software-debug.md#media-start)。

<a id="nor-boot"></a>

### 14.6.3 SPI NOR：地址读取与器件配置

**选择：**BOOT\_MODE=2 调用 boot\_spi\_s25fs512s；CS1，SPI 频率 min(40 MHz, core\_freq/4)，初始化后调用 `clint_spin_until((350 * rtc_freq) / 1000000 + 1)`，等待 mtime 达到该绝对阈值，并非从初始化结束起再等 350 μs；**输入和装载：**spi\_s25fs512s\_single\_read 读取镜像，按共同 GPT/raw 规则写 SPM；**入口：**返回成功后调用 SPM 起点。

**适用范围：**本地 init 只配置 SPI host，single\_read 使用 0x13 读取；CR3V 配置方向问题位于 single\_flash 写擦路径，不是本只读启动路径的必经步骤。正常启动仍需器件模式、地址长度、模型或板级接线、连续镜像与应用结果逐项成立；VIP 存在 NOR 模型不等于该流程已通过。见[NOR 读取](spi.md#nor)与[介质启动验证条件](software-debug.md#media-start)。

<a id="eeprom-boot"></a>

### 14.6.4 I2C EEPROM：器件地址与内部地址

**选择：**BOOT\_MODE=3 初始化 I2C/24fc1025；**输入和装载：**i2c\_24fc1025\_read 把介质偏移转换为器件选择及内部地址，读到的 GPT/raw 字节按共同规则写入 SPM；**入口：**加载成功后调用 SPM 起点，不由 EEPROM 提供独立 ELF 入口。

**适用范围：**正常读取需要正确的器件地址、内部地址、ACK/STOP 和跨界拆分；当前 HAL 的边界/递归缺口尚待处理，本例不标为可立即运行。VIP 的少量预填数据也不是一份启动镜像。事务见[EEPROM 章](i2c.md#transaction)，问题证据见[介质启动诊断](software-debug.md#media-start)。

<a id="boot-growth"></a>

## 14.7 多阶段启动与大型镜像装载

<a id="later-stages"></a>

### 14.7.1 ZSL、OpenSBI 与操作系统启动的分层

当后续软件超出 ROM 的小型装载空间时，可以先把一个较小的加载器放入 SPM，由它继续读取大映像。本地 `sw/boot/zsl.c` 的 ZSL 使用前一阶段保留的读取回调访问启动介质；scratch0/1/3 在该阶段分别携带函数指针及标志、设备私有参数和原 gp 上下文。`grread` 负责按约定切换 gp 后调用读取函数。

ZSL 将 DTB 放到 `0x80800000`、固件载荷放到 `0x80000000`，再按入口约定交接。DTB 是设备树二进制，用数据结构描述硬件地址、设备和中断；OpenSBI 提供监管态软件所需的固件服务，U-Boot 再负责后续启动组织。`fw_payload` 可把 OpenSBI 与后续载荷组合起来。这条链与直接运行裸机 ELF 是不同用途。

这些 DRAM 写入要求外存已可用；当前 ZSL 不能代替尚未提供的 ASIC DDR 初始化驱动。把初始化职责放在 Platform ROM 或明确的早期平台阶段时，应按实际依赖安排，再进入 ZSL 的加载动作。本地通用 GPT 打包规则已注释，Linux 专用规则仍存在，操作前按[当前 SDK/镜像规则](../../software/BUILD_AND_SDK.md)逐项核对。

至此只需把 ZSL 理解成仍由同一个 CPU 执行的较小加载程序，它不会自动提供一个操作系统。随附官方软件文档描述了 Linux 启动栈，本地也保留 SDK 源码和镜像输入；这些材料不等于当前 VCU118、固定 Ara 配置或未来 ASIC 已完成 OS 验证。完整的固件、内核、根文件系统和第一个用户进程关系在[Linux 启动章](linux.md)连续解释；RTOS 的启动和调度在[RTOS 章](rtos.md)解释。它们不是当前裸机数组例子或 ASIC 裸机提取的前置。

官方设计意图参照本地 [Software Stack](../../../docs/um/sw.md) 和 [Platform ROM 集成说明](../../../docs/tg/integr.md#platform-rom)；软件手册中的 EEPROM 模式表、scratch 启动位和 UART EXEC 返回码有旧描述差异。本文分别以 `cheshire_bootrom.c` 的模式 3、`boot_passive` 的掩码 2、`uart_debug_serve` 的 EOC=0x14 为准，未据新版上游行为替代当前源码。

**源码与进一步阅读**

[启动选择与 scratch 协议](../../../hw/bootrom/cheshire_bootrom.c)；[GPT/raw 读取](../../../sw/lib/gpt.c)；[DMI 寄存器及字段](../../../.bender/git/checkouts/riscv-dbg-1a98531d53bb4602/src/dm_pkg.sv)；[SoC 寄存器属性](../../../hw/regs/cheshire_regs.hjson)；[ROM 初始化](../../../hw/bootrom/cheshire_bootrom.S)；[ELF 解析](../../../target/sim/src/elfloader.cpp)；[JTAG / UART / Link 加载](../../../target/sim/src/vip_cheshire_soc.sv)；[应用入口和退出](../../../sw/lib/crt0.S)

**UART 的 EXEC 地址和 NOR 自主启动入口为何可能不同？**

UART 调用装载者显式发送的 addr64；NOR 共同加载器从 SPM code\_buf 起点调用，要求镜像在该处布置入口。两者都要满足地址、代码和栈条件。

**NOR 镜像更新后，片上 Boot ROM 的程序是否也随之改变？**

不会。固定 ROM 仍执行原有读取流程，新镜像被搬到 SPM 后由 CPU 执行。变化的是载荷字节，而不是第一阶段加载器。

**Platform ROM 初始化 PLL 后，应用怎样改变频率？**

通过真实 PLL IP 的运行时控制接口，遵守停止任务、排空、安全时钟切换、锁定和恢复契约。ROM 固定初始代码不等于 PLL 状态锁死；还要先解决本地平台钩子的正常返回缺口。

---

[上一页：CPU、Ara、DMA 与 NPU 的共享数据](sharing.md) · [下一页：JTAG 与程序加载调试](boot-debug.md)
