# 16 · 异常、中断与上下文

函数调用、异常中断与任务上下文的保存责任。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/traps.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../traps.html) · [阅读路线](index.md)

- [16.1 函数调用、异常与中断的控制流](#call-versus-trap)
- [16.2 异常与中断入口的硬件状态更新](#trap-entry)
- [16.3 异常入口的整数寄存器保存与恢复](#software-context)
- [16.4 机器态定时器中断处理流程](#normal-service)
- [16.5 返回地址、特权返回与委托](#trap-return)
- [16.6 trap、任务切换与系统调用的关系](#syscall-scheduling)
- [16.7 本地异常与中断处理入口的适用范围](#local-handler)

**本章任务**

解释一段正在计算的程序怎样进入事件处理，再恢复原执行；为外设中断与 OS 调度建立共同前置。前置：[函数调用、ABI 与栈](runtime.md#abi)、[M/S/U 权限](cva6.md#privilege)。先按当前默认机器态、单核、非 CLIC 路径说明。

<a id="call-versus-trap"></a>

## 16.1 函数调用、异常与中断的控制流

journey 的 main 调用 make\_value 时，编译器知道调用发生在哪里。它把参数放入约定寄存器，保存调用后仍需要的 caller-save 值；call 设置返回地址 ra，被调用函数完成后用 ret 回来。两段代码按同一 ABI 主动合作，没有改变运行权限，也没有访问 mtvec。

现在设想数组循环运行到一半，定时器达到截止时间。当前指令没有主动 call 一个 handler，编译器也无法预先在这一位置插入保存动作。CPU 必须先记下原执行位置与状态，再转入软件入口；入口必须保护被打断代码仍需使用的寄存器。设备或计时产生的这种异步事件称中断。若当前指令执行 ECALL 请求环境服务，或无法按其语义执行，则产生同步异常。两者通称 trap，即控制流按架构规定转交处理程序。

trap 不是错误的同义词。定时器唤醒任务、UART 数据到达、用户程序用 ECALL 请求内核服务都是正常机制。本章讲控制转移与上下文；具体 UART/PLIC/CLINT 服务见[事件章](interrupts.md)，非法指令或无法返回等症状才进入[软件诊断](software-debug.md#trap-stop)。

<a id="trap-entry"></a>

## 16.2 异常与中断入口的硬件状态更新

以默认机器态定时中断为例：CLINT 提供到期条件，CPU 的 mie.MTIE 和 mstatus.MIE 允许响应，CPU 在可接受的位置进入 trap。当前任务的整数寄存器并未自动搬进 RAM。硬件更新 mepc、mcause 和相关 mstatus 字段，再把 PC 指向 mtvec 指定的入口。本地 crt0 把 mtvec 设为对齐的 \_trap\_handler\_wrap，使用直接入口模式。

| 状态 | 本例进入机器态 trap 时的作用 | 软件据此完成什么 |
| --- | --- | --- |
| mepc | 保存被中断处/引发异常的指令位置 | 决定返回地址；不能对所有原因都统一加 4 |
| mcause | RV64 最高位区分中断，其余为原因编号 | 区分 timer、外部事件、ECALL 等服务 |
| mtval | 原因相关的辅助信息，是否有值受实现/配置及原因影响 | 需要时解释地址或指令信息，不能假设每次都保存完整故障指令 |
| mstatus.MPIE / MPP | 保存进入前的中断许可与权限，进入时清 MIE | 给后续 MRET 提供恢复依据 |
| mtvec | 软件预先配置的入口地址和模式 | 将 trap 导向能够保存现场的有效代码 |

本例机器定时中断 cause 是 7，外部中断是 11。这里的 cause 表达 CPU 接收的类别；外部中断来自哪个设备，还要由 PLIC claim 返回源号。例如 GPIO0 的 PLIC 源号 20 不会变成 mcause=20。MIE 也不是所有权限情形下唯一的总开关；以上描述限定在当前 M 态程序，委托到 S 态的情况在后文区分。

<a id="software-context"></a>

## 16.3 异常入口的整数寄存器保存与恢复

假设循环里的 i 和 sum 当前在 a0、t0。处理程序也可能使用这两个寄存器；仅保存 mepc 并不能恢复它们。当前 [crt0.S](../../../sw/lib/crt0.S) 的 \_trap\_handler\_wrap 在原栈上减去 128 字节，保存 ra、t0…t6、a0…a7 共 16 个整数寄存器，再调用普通 C 函数 trap\_vector。C 编译器按 ABI 保存它实际使用的 s0…s11，因而在这个受限模型中，两部分配合保护被打断的整数程序。

```
/* 源码动作摘要；中间 save/restore 表示原文件中的逐项 sd/ld */
_trap_handler_wrap:
    sp -= 128
    save ra, t0..t6, a0..a7
    call trap_vector
    restore ra, t0..t6, a0..a7
    sp += 128
    mret
```

这段摘要不是可汇编的新实现。它强调三件事：栈在进入前就须有效且有余量；C handler 的 ret 只回到包装汇编；包装汇编最后还必须执行 mret。它没有自动切换到一个独立的中断栈，没有保存完整 FP/RVV 上下文，也没有通用嵌套策略。handler 若要使用浮点、向量或重新开放嵌套，需要另行设计对应保存协议；本书当前实例只用整数 handler。

再与普通函数比较：自愿调用前，调用者可以处理 caller-save；异步 trap 前，原程序没有这个机会，所以包装入口替它保存。与任务切换比较：只处理一个事件并回到原任务，可以恢复原栈上的保存值；若改去任务 B，调度器必须让 B 的整套上下文成为新的返回对象。原裸机包装并不具备这个任务所有权机制。

<a id="normal-service"></a>

## 16.4 机器态定时器中断处理流程

复用 [advanced.c](../examples/advanced.c) 的 timer 教学变体：启动先建立 trap 入口，关闭相关中断门，把 CLINT compare 设置到未来，然后再打开 MTIE/MIE。前台代码等待事件计数。当 mtime 达到 compare，CPU 按前述规则转入包装，包装在当前栈保存整数状态并调用程序覆盖的 trap\_vector。

handler 读 mcause，识别机器定时中断后递增 adv\_timer\_count，再用稳定的 mtime 读取结果把 compare 推到未来，消除“已到期”条件并安排下一次事件。它把打印留在前台，避免每次事件服务承担格式化和串口轮询。handler 返回后，包装恢复整数寄存器，mret 恢复原权限/中断许可和执行位置。前台继续等待，直到至少两次 timer 事件及本例的 GPIO 条件满足，才关闭本例打开的中断门、检查计数并输出结果。

本例真实的寄存器访问与初始化顺序在[中断章](interrupts.md#sequence)连续给出。这里描述的是现有源文件的预期过程和历史构建材料，本轮未执行 timer 场景。即使成功响应一次中断，也只证明一次服务，不证明固定周期调度、嵌套或多任务上下文切换。

<a id="trap-return"></a>

## 16.5 返回地址、特权返回与委托

普通 ret 根据 ra 回到调用者；mret 根据 mepc 和 mstatus 中保存的权限/中断状态返回，两者承担不同责任。定时中断处理完通常沿保存位置继续；同步 ECALL 的 mepc 指向 ECALL 自身，已完成服务的系统调用入口要安排继续到后续指令。不能将“所有 trap 都把 mepc 加 4”当模板：外部中断不应跳过程序指令，可重试异常也有自己的恢复策略，压缩指令还使一般指令长度不恒为 4 字节。

具有 S 态的系统可以由机器态通过 medeleg/mideleg 将允许委托的异常/中断交给 S 态处理。对应入口和返回状态使用 stvec、sepc、scause、stval 与 SRET。不是写了委托位就把正在 M 态执行的代码变成普通用户进程，也不是所有异常都能任意委托。默认裸机路径继续由 M 态承担，OS 所需的具体入口、权限和页表在后续 OS 章说明。

CLIC 的向量入口和门限属于另一种正常中断接口，本地有独立开发版本与示例。应先掌握本章的现场和返回责任，再看[CLIC](interrupts.md#clic)；不能把 mtvec 模式 3 的本地例子套成上述直接入口。

<a id="syscall-scheduling"></a>

## 16.6 trap、任务切换与系统调用的关系

任务 A 因定时或事件进入处理程序时，处理程序可以只服务事件，然后返回 A。调度器也可以决定让 B 先运行：先保存 A 的继续位置、栈和必要寄存器，记录 A 的状态；选择 B，换成 B 保存的栈和状态，再沿其入口恢复。稍后 B 让出执行，调度器才能按同一契约重新恢复 A。这就是[RTOS 章](rtos.md)的 A→B→A 过程；每次中断并不必然切换任务。

系统调用是另一种主动交接：用户程序通过规定 ABI 提交请求，ECALL 进入权限更高的软件，后者验证参数并提供服务。系统调用处理期间可以立即返回，也可能使当前任务阻塞并触发调度；同步入口与是否调度是两项不同判断。Linux 的用户缓冲区、驱动与地址空间还需各自处理，见[OS 设备操作](os-devices.md)。

FP/RVV 任务还拥有标量浮点寄存器、向量寄存器、相关 CSR，以及必须完成或妥善交接的在途工作。硬件能够执行 V 不等于某个 OS port 已安全保存这些状态。当前裸机整数包装不能替代该 port；对应支持必须按选定 OS 版本和本地接口核实。

<a id="local-handler"></a>

## 16.7 本地异常与中断处理入口的适用范围

应用 crt0 提供弱符号 trap\_vector，默认内容为自循环。advanced.c 用同名普通 C 函数覆盖它，借用已有整数包装；journey 没有覆盖它。因此 journey 的正常数组/UART过程可连续说明，但遇到 trap 后不具备已实现的恢复程序。这个可执行边界必须保留，具体停顿诊断见[软件诊断](software-debug.md#trap-stop)。

官方随附资料：[CVA6 trap 手册](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/docs/01_cva6_user/Traps_Interrupts_Exceptions.rst)。本地实现核对：[csr\_regfile 的 trap/返回状态更新](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv)、[整数包装与弱 handler](../../../sw/lib/crt0.S)、[现有整数 handler](../examples/advanced.c)。依赖快照为 cva6-20c9d7cbe0dd6995；随附手册的全家族支持描述不覆盖本地每组 profile，本文只使用已由当前实现核对的基本机制。

**只保存 mepc 并执行 mret，能否恢复被打断的数组循环？**

不能保证。handler 若改写循环仍需使用的寄存器，返回 PC 正确也会得到错误数据。要把硬件 CSR 保存、入口软件保存、C ABI 和设备清源一起解释。

**PLIC complete、C handler 的 ret 和 mret 各完成什么？**

complete 结束控制器的一次领取服务；ret 回到入口包装；mret 恢复 CPU 执行状态和位置。三者都不自动保证外设事件原因已清除。

---

[上一页：JTAG 与程序加载调试](boot-debug.md) · [下一页：MMIO 驱动、UART 与 GPIO](uart-gpio.md)
