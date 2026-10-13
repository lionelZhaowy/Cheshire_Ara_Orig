# 内存、MMIO 与数据交接

地址、译码、副作用和可见性

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/memory-mmio.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../memory-mmio.html) · [阅读路线](index.md)

- [一条访存的完整路径](#path)
- [地址转换、属性与设备地址](#addresses)
- [访问宽度、选通和桥的副作用](#width)
- [寄存器字段如何改变电路](#registers)
- [volatile、屏障与缓存维护](#visibility)
- [LLC、SPM、DDR 和 Global Buffer](#storage)

RAM变量和MMIO寄存器都可以由load/store访问，但允许的重排、缓存、重复读取和访问宽度可能完全不同。地址数值相邻不表示语义相同。

<a id="path"></a>

## 一条访存的完整路径

以UART `0x03002000`的数据写为例：软件先取得链接符号基址并加偏移；`volatile uint8_t*`写生成字节store；CVA6检查地址/权限和属性，送出对应AXI地址、数据、大小和选通；主Xbar把地址路由到Reg出口；Reg桥转换成32位请求，再按RegMap选UART。读操作沿响应路径返回数值，写操作的总线响应只说明访问完成，不说明串行字节已经发完。

| 层次 | 当前文件/关键符号 | 做出的决定 |
| --- | --- | --- |
| 软件地址 | [common.ldh](../../../../sw/link/common.ldh) `__base_uart`；[uart.h](../../../../sw/include/dif/uart.h) `UART_THR_REG_OFFSET` | 基址+byte偏移；头文件和链接脚本没有自动生成同一地址真值源 |
| CPU地址语义 | [load\_store\_unit](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/load_store_unit.sv)、[load\_unit](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/load_unit.sv) `stall_ni` | M模式普通访问/有效特权；S/U页表转换、非幂等访问控制、错误 |
| 物理属性 | [cheshire\_pkg](../../../../hw/cheshire_pkg.sv) `gen_cva6_cfg`；[config\_pkg](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/include/config_pkg.sv)区域查询 | 哪些区域可cache、可执行、非幂等；不创建存储目标 |
| 主AXI路由 | `gen_axi_out(Cfg)` → [SoC](../../../../hw/cheshire_soc.sv) `i_axi_xbar` | 目标端口；UART落在 `[0x02000000,0x0c000000)` 的Reg出口 |
| AXI/Reg转换 | `i_reg_atomics → i_reg_atomics_cut → i_axi_to_reg_v2` | 接受AXI读写/突发，转换数据宽度/应答形式 |
| Reg译码 | `gen_reg_out → RegMap → i_reg_demux_decode → i_reg_demux` | UART窗口 `[0x03002000,0x03003000)`；没有命中则默认error slave |
| 外设寄存器 | `i_uart → reg_uart_wrap → apb_uart` | 选择寄存器、读取副作用、使能/数据状态变化 |

AXI的AW/W/AR/B/R分别是写地址、写数据、读地址、写响应、读响应通道。CPU请求经过缓存和缓冲后，C语句、机器指令、AXI beat、Reg请求不一定一一对应。

<a id="addresses"></a>

## 地址转换、属性与设备地址

VA（虚拟地址）是当前软件地址空间的地址；PA（物理地址）是CPU转换后用于平台译码的地址；DMA设备使用其可见的总线地址。当前裸机M模式普通例程通常以平台物理地址直接访问，crt0未建立页表，也未建立通用DMA地址映射层。开启MPRV等状态会改变有效访存权限，不能把“当前跑M模式”推广为所有访问都绕过检查。

Linux内核指针是VA，向驱动传递用户指针更不能直接填DMA SRC/DST。未来NPU是否与CPU看到相同PA、是否有窗口偏移/地址转换，必须由互连契约定义；当前没有证据证明新增NPU IOMMU已存在。Ara的MMU专用请求复用CPU翻译路径，与普通iDMA直接发AXI地址不同。

C/I/E分别表示可缓存、幂等、可执行属性。可缓存决定CPU是否允许形成缓存副本；非幂等提醒CPU不能把读FIFO之类访问当成可随意重复的普通内存；可执行涉及取指区域检查。它们不等于PMP/页表权限，也不能自动约束其他AXI master。

当前高SPM别名在 `0x14000000`，`gen_axi_out()`明确映射它；但 `gen_cva6_cfg()` 的SPM执行区按 `AmSpm+2*SizeSpm`连续计算。默认128KiB时执行上界是`0x10040000`，并不覆盖高别名。**高别名可作数据地址，不能因此把程序入口也搬到高别名。**完整默认区间和公式见[既有C/I/E分析](../../../01_Cheshire_Ara_Quick_Start.md#81-cie-attributes)。

<a id="width"></a>

## 访问宽度、选通和桥的副作用

[reg8/reg32](../../../../sw/include/util.h)返回volatile指针；[mmio\_region\_read32/write32](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/sw/device/lib/base/mmio.h)用地址句柄和偏移封装同类访问。`DOT_PLATFORM_RV32`只是当前编译宏，不会把RV64 CPU和AXI宽度变成32位。

Regbus请求是 `addr/write/wdata/wstrb/valid`，响应是 `rdata/error/ready`；`valid && ready`完成一次传输。目标应在规定的握手时刻产生一次副作用，不能在等待期间每周期重复写入。Regbus没有独立的AW、W、B或事务ID。

当前系统AXI64、主Regbus32。对8字节对齐A：AXI低4字节对应A，高4字节对应A+4。合法32位store到A+4时，桥把高半部搬到Reg数据低32位；软件不必手动移位。64位store可能变成两次32位写，不是原子的64位寄存器提交。四个wstrb分别对应Reg四个byte；访问者须选择目标支持的对齐/宽度。

这不是“桥永远按C类型只访问一个寄存器”。本地 [axi\_to\_reg\_v2.sv](../../../../.bender/git/checkouts/register_interface-902ad5bfde7bb98c/src/axi_to_reg_v2.sv) `NumBanks`、`i_periph_to_reg`、`i_reg_demux` 只过滤零选通写，读会送入两个bank；需结合 [mem\_to\_banks\_detailed.sv](../../../../.bender/git/checkouts/common_cells-7f7ae0f5e6bf7fb5/src/mem_to_banks_detailed.sv) 检查邻接读。于是一次窄读可能触及相邻32位寄存器。UART读LSR还可能同时触及MCR；PLIC读threshold相邻claim可能有更强副作用。新IP应把该现有桥行为列为验收条件，不以“用了uint32\_t”作为无邻读证明。

<a id="registers"></a>

## 寄存器字段如何改变电路

以[SoC寄存器HJSON](../../../../hw/regs/cheshire_regs.hjson)为例，reggen生成 [cheshire\_reg\_pkg](../../../../hw/regs/cheshire_reg_pkg.sv) 中的offset和结构，以及 [cheshire\_reg\_top](../../../../hw/regs/cheshire_reg_top.sv) 中的地址命中、字节使能和字段存储。软件C宏由同一HJSON生成，但SoC基址来自另一层。

`reg2hw`给功能RTL提供软件写出的值/写使能等字段，`hw2reg`把硬件值和更新使能带回寄存器。并非每个字段都有全部 q/qe/re/d/de成员，其结构由访问属性生成。SoC的RTC\_FREQ由硬件配置提供只读值；scratch是软件状态；自定义START需要功能RTL在提交点锁存参数，不能只写HJSON就产生NPU计算状态机。

| 语义 | 当前可对照对象 | 软件写法与风险 |
| --- | --- | --- |
| RO（只读） | SoC HW\_FEATURES/RTC\_FREQ | 读能力，不将写后读回当配置方法 |
| RW（读写） | scratch、部分enable字段 | 只操作定义位，避免并发读改写丢更新 |
| W1C（写1清除） | GPIO INTR\_STATE及生成DIF acknowledge | 写需要清除的mask；不要读全值OR mask后写回，可能清掉其他事件 |
| 读清除/弹出 | UART LSR错误、RBR FIFO | 诊断dump本身可能改变硬件；先保留状态再服务 |
| 读触发提交 | iDMA NEXT\_ID、PLIC claim | 不能把它们当普通只读计数器轮询 |
| 自清零/提交脉冲 | UART FCR FIFO reset等 | 写入后的0不等于写失败；按动作完成条件判断 |
| 保留位 | 各生成头未定义位 | 按IP约定写0或保留；避免用全1覆盖未知控制位 |

建议新增设备采用显式START/提交、可无副作用读取的STATUS、W1C事件和独立ERROR信息；这是设计建议，需要定义并发置位/清除优先级、byte mask和软复位语义。

<a id="visibility"></a>

## volatile、屏障与缓存维护

三者解决不同问题：volatile约束编译器对该访问的消除/合并；`fence`约束架构可见的访问顺序；cache clean/invalidate处理数据副本。`asm volatile("fence" ::: "memory")`同时提供指令和编译器memory clobber，但不能据此宣称所有缓存已flush。`fence.i`用于指令流与先前写入同步，也不是清理任意数据缓存的万能接口。

当前向量profile采用WT（write-through，写直达）L1D，但仍有读副本和写缓冲。CPU/Ara另有 `CSR_ACC_CONS`、标量/向量pending计数、barrier和 [axi\_inval\_filter](../../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/axi_inval_filter.sv) 的写地址失效机制；CVA6 [acc\_dispatcher](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/acc_dispatcher.sv)明确消费这些信息。这是当前特定组合的机制，不自动覆盖iDMA、USB、Serial Link或新增NPU。

```
CPU拥有输入/输出 → 填输入、准备输出保护区
→ 发布：必要cache维护 + 排序 → 提交任务和设备地址
→ 设备拥有缓冲 → 输出写入、排空、产生完成/错误状态
→ CPU取得匹配完成令牌 → 排序/必要invalidate → 校验结果
→ 后继消费者取得所有权 → 最后一位使用者释放
```

这是后续驱动的交接建议。超时意味着结果和在途状态未知，应停止新提交、隔离缓冲、按引擎的取消/排空/复位协议恢复；超时后立刻重用目的缓冲会与迟到写冲突。错误恢复接口未实现的设备不能宣称具备此闭环。

LLC下游的NPU旁路写也可能绕过当前AMO/LRSC监视器，因此不仅cache副本会过期，普通写还可能破坏共享原子观察范围。不能以“NPU不发原子指令”免除该问题。[IP/DDR契约](../../../engineering/IP_DDR_Interface_Contract.md)负责后续跨层约束。

<a id="storage"></a>

## LLC、SPM、DDR 和 Global Buffer

| 访问对象 | 当前路径和软件边界 |
| --- | --- |
| SPM低区/高别名 | CPU/Ara/iDMA → 主Xbar → LLC/SPM目标，底层同一阵列；低区可有L1副本，高别名按当前CPU属性不缓存；不能同时混用两个别名写同一数据 |
| DDR主存窗口 | 主Xbar → 原子适配 → LLC → 平台内存出口；LLC way状态决定缓存行为，DDR实体由平台提供 |
| LLC配置 | CPU → Regbus → `axi_llc_reg_wrap`；way重配/flush不等于CPU L1同步；代码/栈留在某way时禁止不经搬迁便回收 |
| 独立GB | 用户确认是新的共享片上SRAM；当前没有GB地址译码、仲裁或软件分配器；Ara宽侧分流、CPU是否直接访问及NPU搬运接口待定 |

仅让CPU地址“不可缓存”不保证经过的LLC也不分配，必须按实际路径检查。已有RVV教学例使用独占高别名SPM缓冲，避免同一程序混用低别名；这是实验条件，不是最终DDR缓存策略。

---

[上一页：指令、Ara 与 CSR](instructions.md) · [下一页：异常与中断](interrupts.md)
