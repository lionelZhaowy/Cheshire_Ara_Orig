# 最小实践与验证记录

循序渐进的操作、判据和证据缺口

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/labs.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../labs.html) · [阅读路线](index.md)

- [本轮验证结果和证据等级](#evidence)
- [实践一：观察构建与初始化](#build)
- [实践二：在匹配环境中加载并检查结果](#run)
- [实践三：寄存器读取和UART写入](#mmio-lab)
- [实践四：计时、中断条件和返回](#irq-lab)
- [实践五：DMA配置与二维地址推演](#dma-lab)
- [实践六：最小向量计算](#vector-lab)
- [未关闭项与最小后续检查](#gaps)

**批次说明：**下面保留初版接口教程在`c4162204c`上的实际编译/检查结果。基础软件扩充批次为`bf1b4198`，只新增源码复核、工具查询和图文检查，见[本轮BSP记录](foundation-software.md#evidence)，没有重编或运行应用。

实践先建立可追溯输入，再增加设备交互。下面区分本轮实际编译结果、已有可复用命令和需要后续实现的测试。没有运行日志的预期现象不是通过记录。

<a id="evidence"></a>

## 本轮验证结果和证据等级

| 项目 | 本轮结果 | 证据和限制 |
| --- | --- | --- |
| 源码/配置/调用链 | 静态核对 | [源码哈希清单](../evidence/sources.json)，不等于RTL展开或目标运行 |
| 标量journey SPM | 重新编译/链接成功 | [build.log](../evidence/scalar-build/build.log)、[readelf](../evidence/scalar-build/readelf.txt)、[反汇编](../evidence/scalar-build/journey.dump) |
| RVV journey+边界/归约 | 重新编译/链接成功 | [build.log](../evidence/rvv-build/build.log)、[反汇编](../evidence/rvv-build/journey.dump)；未执行V指令 |
| 生产HelloWorld源码 | 在独立输出中重编/链接 | [hello-build](../evidence/hello-build/build.log)；复用本轮新编最小支持库，不是重新构建完整libcheshire.a |
| DMA访问编译探针 | 检查机器访存宽度 | [dma-probe.dump](../evidence/hello-build/dma-probe.dump)，不证明总线行为 |
| HTML/Markdown、源码路径/图片 | 定向检查 | [validation.json](../evidence/validation.json)，仅本专题范围 |
| 桌面/手机浏览器 | 实际Chrome检查 | [browser.json](../evidence/browser-review/browser.json)，仅文档渲染 |
| SVG/原生PPTX | 导出结构检查和PNG查看 | [图稿入口](../../../diagrams/2026-10-13_software_hardware_interfaces/README.md)；Office显示/编辑未实测 |
| SoC仿真/FPGA板测/ASIC | 本轮未执行 | 现有仿真清单与向量例不匹配；保留现有FPGA工程，不运行大型构建。历史HelloWorld用户报告不是本轮证据 |

本轮GCC版本及完整flags保存在build.log。编译保留了基于链接符号声明的`-Warray-bounds`告警；需要结合实际地址/反汇编分析，本轮未修正。LD的RWX LOAD段告警来自当前链接布局，不能把编译成功解释成运行隔离已经完善。以下构建使用独立目录，避免混入不同profile/ISA的旧对象。

<a id="build"></a>

## 实践一：观察构建与初始化

前提：仓库根、RISC-V GCC/ar/readelf/objdump/nm/size在PATH。采用已经存在的 [build\_journey.sh](../../../learning/scripts/build_journey.sh)，输出必须是新目录或空目录：

```
JOURNEY_DIR=$(mktemp -d /tmp/cheshire-interface-scalar.XXXXXX)
JOURNEY_OUT="$JOURNEY_DIR" bash docs_codex/learning/scripts/build_journey.sh scalar spm
riscv64-unknown-elf-readelf -h -l "$JOURNEY_DIR/journey.spm.elf"
riscv64-unknown-elf-nm -n "$JOURNEY_DIR/journey.spm.elf"
```

操作：找到ELF入口、LOAD、seed/result、\_\_bss\_start/end和\_\_stack\_pointer$；从反汇编找到 `_start → _zero_bss_loop → main`，判断 `.data`是谁装入。预期：入口在0x10000000、栈符号为0表示继承，结果数组在BSS；具体段大小随工具链变化。失败先查ISA/ABI、库来源、链接脚本和工具路径。

本轮实际标量产物text/data/bss为5328/796/548 byte；RVV depth为6092/908/548 byte，证据来自各build.log，不作为未来产物固定值。

<a id="run"></a>

## 实践二：在匹配环境中加载并检查结果

前提：已经用匹配CPU profile/SoC配置编译、展开的仿真库，或来源明确的VCU118 bitstream与JTAG连接。**当前保存的标量仿真清单不能直接用来验收RVV**。不在本实践自动重建RTL或覆盖旧清单。

[现有Questa启动脚本](../../../../target/sim/vsim/start.cheshire_soc.tcl)从Tcl读取SELCFG/BOOTMODE/PRELMODE/BINARY。先把构建返回的绝对ELF路径替换到下面占位符；这是待运行模板，不是本轮命令记录：

```
# 在已有正确映射的Questa work库环境内执行
set SELCFG 3
set BOOTMODE 0
set PRELMODE 0
set BINARY {/absolute/path/from-build/journey.spm.elf}
source target/sim/vsim/start.cheshire_soc.tcl
run -all
```

此处SELCFG=3仅适用于已正确编译的Ara组合；标量环境使用与其实际编译/配置匹配的选择。PRELMODE=0为JTAG；=2会经过UART debug服务，条件另含UART时钟/ROM服务正常。

FPGA参考当前[HS2适配器配置](../../../../util/openocd.hs2.tcl)与[公共配置](../../../../util/openocd.common.tcl)，仓库没有专用openocd.vcu118.tcl，HS2配置只适用于对应适配器，需沿用用户已验证的VCU118连接参数。在用户已有工作流程中用GDB加载 `.spm.elf`、设置PC到 `_start`并继续；必须保留Boot ROM初始化后的有效sp，不能在复位后尚无SPM/栈时强跳main。命令形状如下，端口以本次OpenOCD实际监听为准：

```
riscv64-unknown-elf-gdb /absolute/path/from-build/journey.spm.elf
(gdb) target extended-remote localhost:3333
(gdb) monitor halt
(gdb) load
(gdb) set $pc = _start
(gdb) continue
```

建议在执行前用GDB检查 `$sp`、`$mtvec`及LLC配置，不把这个形状当作自动完成复位/初始化的脚本。OpenOCD连接失败先查板型/线缆/端口；halt/load失败查JTAG与Debug Module；程序异常查mepc/mcause/mtval。

目标预期：`INIT seed=1 zeroed=137 errors=0`、`LEARN sum=28085 errors=0`和main返回0。保存UART/返回码/ELF哈希/RTL配置/工具版本，不能只记录“串口有字”。本次没有这些目标运行证据。

<a id="mmio-lab"></a>

## 实践三：寄存器读取和UART写入

先在已有HelloWorld或journey上观察HW\_FEATURES、RTC\_FREQ、UART LSR/THR的访问；需要改程序时在独立教学副本中进行，不覆盖 `sw/tests`。用反汇编区分 `lw/lbu/sb`和CSR读，用波形追踪RegMap、地址、选通、valid/ready、UART FIFO和TX。

预期：一个待发送字符产生THR写，FIFO/发送器随后工作；flush看到THRE/TEMT。可先打印单字符再打印格式化整数。不要对整段外设地址使用任意内存dump，RBR、claim、NEXT\_ID等读有副作用。坏结果回到[字符案例](cases.md#uart)逐层排查。

<a id="irq-lab"></a>

## 实践四：计时、中断条件和返回

第一步复用现有clint\_get\_core\_freq，观察mtime增长和mcycle增长，理解MMIO与CSR。第二步静态跟踪mtimecmp比较和mip.MTIP，**暂不把当前clint\_sleep\_until作为可靠等待API**。

第三步为后续S01/V01准备[GPIO INTR\_TEST→PLIC案例](cases.md#gpio-irq)的最小C处理程序：安装强符号trap\_vector、配置三个使能层、注入一个事件、记录一次ISR、清源/complete并返回主循环。仓库缺少可直接运行的完整默认PLIC测试；本轮不实施该新ISR。验收要求包括中断屏蔽期间pending保持、正确返回以及没有重复服务。

已有 [clic\_basic.spm.S](../../../../sw/tests/clic_basic.spm.S)可在匹配CLIC CPU/SoC组合上复用，先读其mtvec/mtvt/mintthresh设置及成功分支；默认Ara FPGA未启用CLIC，不可直接运行此测试并归咎软件。失败位置按[中断章](interrupts.md)的源→控制器→CPU→trap顺序查。

<a id="dma-lab"></a>

## 实践五：DMA配置与二维地址推演

先读现有 `dma_2d.spm.c`，在纸面或主机推演4行，每行15 byte，src起点步长1、dst步长7，总目的写范围到偏移35为止，36/37保存`!\0`。这种推演只校验地址/期望字符串，不是硬件DMA模型。

再检查本轮probe反汇编和wrapper DW，解释为什么32位ID不能盲目通过uint64\_t指针访问。**运行阻塞条件：控制接口位宽/拆读副作用、reps=0错误回传、排序/超时尚未验收。**后续授权修复后先验证单行不重叠，再跑原2D并对每字节和守卫比较；加入读/写错误、backpressure、零长度、最大有效长度/地址位和取消恢复测试。

不要为了绕过阻塞去调用普通sys\_dma\_memcpy：当前2D wrapper中reps=0路径也是待处理问题。更不能看到DONE\_ID等于提交ID就判定成功。

<a id="vector-lab"></a>

## 实践六：最小向量计算

前提见[Ara案例](cases.md#ara)中的profile、全SPM/独占范围、栈和一致性机制。构建与标量采用相同现有脚本：

```
RVV_DIR=$(mktemp -d /tmp/cheshire-interface-rvv.XXXXXX)
JOURNEY_OUT="$RVV_DIR" JOURNEY_DEPTH=1 bash docs_codex/learning/scripts/build_journey.sh rvv spm
rg -n 'vsetvli|vle32|vadd.vv|vse32' "$RVV_DIR/journey.dump"
```

本轮已得到这些实际指令。目标运行仍待匹配的仿真库或板级输入；预期尾部6例errors=0、归约/总和28085、守卫完整且返回0。输入错误注入可使用现有 `INJECT_ERROR=1` 在另一个新目录编译，预期目标报告非零错误，检查验收脚本是否真的捕获失败；本轮未运行该负例。

最后再比较`rvv-intrinsics`或`rvv-auto`入口，本轮没有重复构建它们。先检查编译器实际生成V指令，再在目标执行；不能以加了`-march=...v`代替向量化检查。

<a id="gaps"></a>

## 未关闭项与最小后续检查

| 未关闭事项 | 最小检查对象 | 对本专题结论的限制 |
| --- | --- | --- |
| Platform ROM普通返回、ROM C栈对齐 | `cheshire_bootrom.S`及实际生成指令；正常返回/启动测试 | 启用钩子前另行修复验收，默认0跳过返回问题 |
| 主Reg桥窄读副作用 | `axi_to_reg_v2`及两个bank请求，PLIC threshold/claim和FIFO布局 | 窄读不一定只影响一个寄存器；设备测试需观察邻址 |
| CLINT读取/比较/睡眠 | clint.c、mtime翻转、mtimecmp分拆更新、trap入口 | 当前sleep API不能证明定时等待可靠 |
| DMA DW、NEXT\_ID拆读与ND错误丢失 | wrapper、reg\_top、编译probe、Job FIFO/ND响应波形 | 编译/ID退休不是数据成功；无完成IRQ |
| Ara B错误和完整可见性 | vstu B响应、acc\_dispatcher pending/barrier、filter | 静态协作机制不能代替错误/并发运行验收 |
| Linux平台资源与缓存维护 | 当前DTS、选用的kernel/固件、DMA ops、IRQ/clock/reset驱动 | 配方/源码存在不等于Linux和向量抢占已跑通 |
| 新GB、NPU/ISP/LVDS、采购DDR | 最新IP规格、端口manifest、帧/张量/性能预算 | 本轮只给修改入口，不制造地址/中断号/频点/容量 |

软件/RTL功能修复交S01/V01及相应工程任务，详细本轮交接见 [L01主题记录](../../../handoffs/L01_software_hardware_interfaces.md)。

---

[上一页：自定义 IP 与 Linux 修改导航](integration.md)
