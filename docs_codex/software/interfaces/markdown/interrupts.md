# 异常与中断

事件、控制器、trap 与返回

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/interrupts.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../interrupts.html) · [阅读路线](index.md)

- [当前配置有三种不同的事件路径](#routes)
- [pending、enable 和服务状态](#pending)
- [CPU进入处理程序的顺序](#trap)
- [原因判定、清除与返回](#service)
- [当前定时和CLIC例程的使用边界](#existing)

同步异常由当前指令引起，例如非法指令、页故障、访问错误；异步中断由定时器或设备事件引起。trap是CPU转入处理程序的动作，既用于异常，也用于中断。进入trap不等于硬件替软件保存了全部上下文。

<a id="routes"></a>

## 当前配置有三种不同的事件路径

| 配置/事件 | 实际路径 | 软件确认或清除 |
| --- | --- | --- |
| 默认PLIC外部中断 | 外设→`intr.intn`→直接fanout（IrqRouter=0）→PLIC→`xeip`→CVA6 `irq_i` | claim辨别源；处理/清设备状态；complete归还控制器的服务状态 |
| CLINT计时/软件中断 | `mtime>=mtimecmp` / MSIP→`mtip/msip`→CVA6 `time_irq_i/ipi_i` | 更新mtimecmp至未来 / 清MSIP；没有PLIC claim/complete |
| 可选IRQ Router | `intr`→按目标mask分配→PLIC/每hart/外部target | Router只选目的地，不代替设备清源和PLIC仲裁 |
| 可选CLIC | 路由源+core中断源→每hart的CLIC→valid/ready/id/level/shv/priv/kill接口 | 本地CLIC模式、向量表、源属性与CPU接受流程；不能套用PLIC完整流程 |
| 同步异常 | 取指/译码/执行/MMU异常→scoreboard/commit→trap | 保存cause/PC/附加值，修复或终止；不是外设claim |

定义见 [cheshire\_pkg.sv](../../../../hw/cheshire_pkg.sv) `cheshire_int_intr_t/cheshire_core_ip_t`，实例和消费者见 [cheshire\_soc.sv](../../../../hw/cheshire_soc.sv) `gen_irq_fanout/i_irq_router/i_plic/i_clint/gen_clic`。当前DefaultCfg的Clic与IrqRouter均为0。源0固定为0；外部输入先同步到SoC时钟域，再参与路由。参数允许扩展不表示已生成的PLIC/CLINT支持任意源数/hart数。

<a id="pending"></a>

## pending、enable 和服务状态

以GPIO边沿为例，输入事件令GPIO INTR\_STATE置位；GPIO的INTR\_ENABLE决定是否向外输出；PLIC gateway记录待处理并限制未complete的重复转发；PLIC按源优先级、target enable和threshold决定对CPU的外部通知；CPU再结合mip/mie、当前特权和全局允许决定是否进入trap。

这至少是三层使能：设备、控制器、CPU。读GPIO pending可以发现事件已发生，即使PLIC被屏蔽；看到 `mip.MEIP=1`也不等于当前允许受理。对本专题M模式例程，需 `mie.MEIE` 与 `mstatus.MIE`；跨特权场景还需考虑委托规则，不能把M模式条件原样用于所有模式。

[PLIC RTL](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/src/rv_plic/rtl/rv_plic.sv)把 `reg2hw.cc0.re`变成claim，把写同一CC寄存器的 `qe/q`变成complete；[rv\_plic\_gateway](../../../../.bender/git/checkouts/opentitan_peripherals-7b624fb57f78de9a/src/rv_plic/rtl/rv_plic_gateway.sv)管理pending/active。claim读取会改变控制器状态，返回0表示此时没有可claim的源。complete不是清设备状态；若设备电平仍有效，可在complete后重新请求。

<a id="trap"></a>

## CPU进入处理程序的顺序

[decoder](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/decoder.sv)结合IRQ控制形成cause；执行/访存错误也带异常信息回到对应scoreboard条目。[commit\_stage](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/commit_stage.sv)经 `ex_commit` 与PC交给 [csr\_regfile](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv) 的异常栈处理，保存mepc/mcause/mtval等，更新MPP/MPIE/MIE；[controller](../../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/controller.sv)与frontend处理flush和PC重定向。软件随后从mtvec指定的位置取指。

[crt0.S](../../../../sw/lib/crt0.S)使用直接模式 `_trap_handler_wrap`：减sp 128字节，保存ra、t0–t6、a0–a7，调用 `trap_vector`，恢复后 `mret`。整数callee-saved寄存器由C ABI被调用者责任保证；该包装不保存全部FP/RVV/任务状态，也不自动实现嵌套、抢占或RTOS上下文切换。

```
# 当前源码的关键结构（省略其余保存/恢复，不可单独复制执行）
_trap_handler_wrap:
    addi sp, sp, -128
    sd ra, 120(sp)
    # ...
    jal trap_vector
    # ...
    addi sp, sp, 128
    mret

.weak trap_vector
trap_vector:
    j trap_vector
```

应用要提供同名强符号 `void trap_vector(void)` 才能完成分发。这个C函数按普通函数返回，由外层汇编mret；不要再给它随意套带独立中断序言/尾声的编译器属性。运行ISR时要避免未保存的FP/RVV状态被使用，尤其是格式化浮点输出、向量化库或其他函数调用。

<a id="service"></a>

## 原因判定、清除与返回

RV64的mcause最高位表示中断，其余位是原因码。普通M外部中断cause=11，M timer=7，M software=3；这些不是PLIC设备源ID。PLIC源ID从claim取得；GPIO第几位由当前packed结构映射，不能把cause11分配给新设备。

下面是**流程示意，尚未作为新ISR实现或编译**：

```
void trap_vector(void) {
    /* 读取 mcause、mepc、mtval；保留现场诊断 */
    /* 如果是 M external：claim当前target */
    /* id==0则不伪造complete；已知id则读取设备原因并服务 */
    /* W1C设备仅写处理过的位；需要时排序/读回 */
    /* complete同一个id；更新软件完成计数 */
    /* 如果是timer：安排未来比较值，不调用PLIC complete */
    /* 未知异常：保存诊断并进入明确失败路径，避免无限重试 */
}
```

对于W1C事件，通常先服务/清源，再complete，避免电平仍有效而立即再次触发；如果设备另有协议，则按该协议和控制器手册执行。遇到未知源不应直接忽略或不停claim，需要屏蔽/记录并采用定义好的恢复策略。同步异常不能一律 `mepc+=4`：RISC-V可有16位压缩指令，页故障修复后可能需要重试原指令。`mret`只恢复处理器trap状态，不清设备、不排空DMA、不维护cache。

轮询和中断都只是发现状态的方法。轮询必须有超时/错误判据；中断等待仍需检查任务ID和结果可见性。WFI（Wait For Interrupt）不是可靠的“睡到指定任务完成”API，必须围绕共享条件处理唤醒竞争，并有可工作的trap入口。

<a id="existing"></a>

## 当前定时和CLIC例程的使用边界

[clint.c](../../../../sw/lib/dif/clint.c) `clint_sleep_until()` 的当前条件是 `if (clint_get_mtime() < tgt_mtime) return;`，因此未来目标会直接返回，不能当作已验证的定时睡眠实现。读取mtime的两个32位读没有高—低—高重试；写mtimecmp高后低也需检查中间值导致的暂态。已有[RTL模块交接](../../../handoffs/L01_rtl_module_guide.md)记录了这些静态缺口。本轮不修复。

[CLIC basic](../../../../sw/tests/clic_basic.spm.S)设置mtvec低两位为3、写mtvt CSR 0x307、源31的pending/enable/attr/ctl和mintthresh 0x347，先阻挡再放行合成事件。该测试要求CPU和SoC都支持对应CLIC组合；源31是该测试人为使用的源，不是NPU分配号。测试自己的成功/失败分支不能拿来替代普通PLIC ISR的mret返回示范。

外设中断的完整静态案例见[GPIO→PLIC→trap](cases.md#gpio-irq)，默认板上尚缺该案例完整ISR及运行验收；本专题明确列出其实现缺口而不伪造已运行程序。

---

[上一页：内存、MMIO 与数据交接](memory-mmio.md) · [下一页：五条软件到 RTL 案例](cases.md)
