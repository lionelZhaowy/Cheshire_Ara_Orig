# 平台、集成与测量诊断

平台就绪、事务执行、数据与测量问题的定位。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/system-debug.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../system-debug.html) · [阅读路线](index.md)

- [系统故障的责任边界与定位顺序](#locate)
- [DDR 无响应、数据不一致与初始化停滞诊断](#ddr)
- [平台就绪与调试复位的本地边界](#platform-readiness)
- [目标运行失败的阶段定位](#simulation)
- [设备控制访问与系统任务完成状态诊断](#integration)
- [帧丢失、数据不完整与吞吐不足诊断](#frames)
- [计时异常与性能结果复现诊断](#measurement)
- [当前已知问题与证据状态](#known)

**本页用途**

正常过程在[DDR](ddr.md)、[IP接入](integration.md)、[帧交接](accelerators.md)和[测量](measurement.md)中连续讲解。本页集中已有材料所支持的定位顺序与工程限制，不代表这些现象已在本轮目标上复现。

<a id="locate"></a>

## 系统故障的责任边界与定位顺序

保存版本、配置、输入和完整命令，再从应用的结果条件反查驱动状态、MMIO访问、控制器事务与外部就绪。每次定位一份已提交工作：它是否被接受、是否还有在途访问、结果是否可见、谁仍拥有缓冲。正常背压允许等待；只有相应契约承诺的进展不再发生时，才按有界等待和恢复约定处理。

软件启动问题见[启动与软件诊断](software-debug.md)，外设症状见[外设诊断](peripheral-debug.md)，向量问题见[Ara/RVV诊断](vector-debug.md)。当前没有真实NPU/ISP和供应商ASIC DDR集成，以下相关部分是条件化定位方案，不能写成已发现并修复的硬件缺陷。

<a id="ddr"></a>

## DDR 无响应、数据不一致与初始化停滞诊断

先检查初始化程序的ELF/map：指令、栈、常量和被调用库是否都在已可用的ROM/SPM；若它们已驻留DDR，就在准备DDR之前依赖了DDR。随后区分电源/参考时钟、复位、PHY训练结果和AXI放行，不能只看CPU仍在运行。具体状态位、超时和重新训练顺序必须来自实际IP手册，当前ASIC接口尚缺这些输入。

AR已经握手但无R时，沿请求队列、命令调度、返回缓冲及上游RREADY逐段观察；刷新、行切换和竞争均会使响应延后。返回错误数据时记录地址、访问宽度、字节使能、首个差异及R/B响应，先排除缓存副本/别名和程序布局，再扩到地址映射、容量边界和器件时序。用已知可用的SPM保存日志和栈，避免诊断程序本身依赖待查内存。

训练失败、越界、R/B错误和中途复位属于后续V01的注错验收。恢复前必须确认仍可能写入的设备已停止、排空或按契约隔离，不能在超时后立即把旧buffer交给新任务。没有供应商模型和平台控制接口时，本页只能规定观察点，不提供虚构的“复位寄存器修复法”。

<a id="platform-readiness"></a>

## 平台就绪与调试复位的本地边界

当前[FPGA顶层](../../../target/xilinx/src/cheshire_top_xilinx.sv)中clkwiz.locked未接出；[DRAM wrapper](../../../target/xilinx/src/dram_wrapper_xilinx.sv)中MIG的init\_calib\_complete/c0\_init\_calib\_complete也为空连接。由这些输出本身不能证明系统已经形成“时钟稳定且训练完成才允许全部主设备访存”的统一放行闭环，也不能反推当前板卡必定无法工作；需要继续检查实际时序、其他ready路径和运行证据。ASIC平台应按自己的IP契约提供可观察的就绪关系。

[i\_dm\_top.ndmreset\_o](../../../hw/cheshire_soc.sv)未被消费，因此设置Debug Module的相应复位请求不等于已经驱动全SoC复位。检查对象应分为DM、hart、SoC和外设/外存域，不能把JTAG传输复位当作全部设备重新初始化。Platform ROM正常返回路径问题另见[S01-B01](../../03_Platform_ROM_Clock_IP_Configuration.md#s01-b01)；本轮只保留证据与后续验收条件。

<a id="simulation"></a>

## 目标运行失败的阶段定位

没有UART时先确认装载完成并恢复执行，再用PC判断是否到main。PC落在trap\_vector时读mepc/mcause/mtval，按dump找出错指令；落在测频函数时查RTC是否推进；落在UART等待时查LSR、除数和TX。结果错误先记首个差异元素、地址和指令，再查共享数据路径。不结束时看是否已返回main、scratch2 bit0及仍等待的MMIO。

旧测频和UART驱动包含无界等待，主机timeout避免工具无限占用，但不是目标端恢复机制。超时先区分ROM BIST/测频、halt/load/resume、首条V非法、MMU翻译或AXI背压。保存HEAD、profile/Cfg、ELF/map/dump、完整命令、首错上下文、PC/CSR和最后进度；波形关联实际事务，而不是只截串口尾部。单项设备和Ara症状继续使用各自诊断页。

<a id="integration"></a>

## 设备控制访问与系统任务完成状态诊断

对教材独立Reg加法器，先检查设备内部偏移与系统绝对地址是否经明确译码转换，+0/+4的数据lane和WSTRB是否正确，再观察START接受、BUSY、DONE、RESULT和IRQ。DONE电平未清而重复进入handler时，检查领取源号、清设备原因与complete顺序；源号和控制器生成尺寸不能凭端口接线推断。

扩展到主动AXI设备后，再查任务ID、长度、最后R/W/B及错误传播。MMIO写响应只说明提交寄存器成交，任务DONE也只有在IP契约定义范围内才有效。超时后保存buffer占用和旧任务代次，防止迟到写覆盖下一帧。当前iDMA控制位宽缺口见[集中证据](peripheral-debug.md#dma)；独立Reg实验通过不能关闭此项。

<a id="frames"></a>

## 帧丢失、数据不完整与吞吐不足诊断

先区分输入是否允许背压，再记录帧/行边界、每行有效字节、stride、FIFO占用和DDR无服务区间。平均带宽足够不保证长暂停不溢出；帧结束标记也不保证此前所有AXI写均完成。遇到半帧时保留原始边界和实际长度，恢复应从协议规定的帧边界开始，不能把队列残留直接当下一帧。

这些观察要求来自[未来帧流程](accelerators.md#frame-walkthrough)与接口契约，目前没有相应新IP运行证据。实际溢出/丢帧/取消策略由I01和IP方提供，缓存、缓冲区所有权与旁路原子边界由M01/S01/V01验证。

<a id="measurement"></a>

## 计时异常与性能结果复现诊断

先查开始/结束点是否覆盖结果完成和可见性，再查计数单位、频率、Debug暂停、权限与计数禁止状态。现有clint\_get\_mtime分高低读取的边界见[定时器诊断](peripheral-debug.md#interrupts)；不能把由不可靠采样得到的跳变当算法行为。不要在本轮文档任务中直接改计时库。

检查串口是否在窗口中、缓存和数据位置是否一致、是否计入格式转换/驱动/唤醒、是否有后台负载；保留全部样本并对照事件时间线。标量与向量返回相同总和仍可能有抵消错误，应逐元素比对。Ara store完成信号的已知错误处理限制仍见[向量诊断](vector-debug.md)，计时记录不能因此宣称总线操作都成功。

<a id="known"></a>

## 当前已知问题与证据状态

| 问题/限制 | 影响与依据 | 当前状态 |
| --- | --- | --- |
| Platform ROM普通返回布局 | 启用非零平台钩子的默认继续启动路径；[源码和已有ROM指令记录](../../handoffs/2026-10-06_L01_platform_rom_boot_review.md) | S01-B01未实施，不因迁移诊断关闭 |
| iDMA控制桥/寄存器/HAL位宽不一致 | 已有控制访问不能作成功DMA例；[集中说明](peripheral-debug.md#dma) | 待S01/V01修复授权与动态验收 |
| Ara写响应错误处理缺口 | 内部store完成不能单独证明写成功；[本地实现与验证边界](vector-debug.md) | 目标执行/错误注入未新增 |
| 未知DDR/工艺/新IP参数 | 缺少真实寄存器、时序、电气和模型输入 | 待用户/供应商/I01/M01/P01；这是输入缺口，不是已证实实现缺陷 |

本页迁移依据为既有DDR/系统集成/模型章节和以上独立交接，保留问题等级。本轮只有文档与静态源码核对，没有目标故障复现、驱动修复或恢复验证。

---

[上一页：Ara/RVV 调试与故障诊断](vector-debug.md) · [下一页：操作系统启动与状态诊断](os-debug.md)
