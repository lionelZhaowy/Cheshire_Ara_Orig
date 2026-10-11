# 28 · 操作系统中的设备与缓冲区

裸机、RTOS 与 Linux 的设备调用和缓冲区管理。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/os-devices.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../os-devices.html) · [阅读路线](index.md)

- [28.1 UART 连接、配置与资源所有权](#same-uart)
- [28.2 裸机 UART 轮询发送流程](#baremetal-uart)
- [28.3 RTOS UART 独占服务任务方案](#rtos-uart)
  - [28.3.1 UART 发送中断与缓冲管理](#rtos-irq)
- [28.4 Linux TTY 与串口驱动调用链](#linux-uart)
  - [28.4.1 Linux 串口操作流程与完成条件](#linux-lifecycle)
- [28.5 设备树与 UART 驱动绑定](#driver-and-description)
- [28.6 设备缓冲区的地址与所有权管理](#buffer-ownership)
- [28.7 UART 数据交接的分层完成条件](#completion-check)

**裸机、RTOS 与 Linux 的 UART 软件职责**

前置：[UART 的正常事务](uart-gpio.md)、[任务/队列](rtos.md)、[用户进程与内核](linux.md)。贯穿任务是把数组校验结果 `N=137 errors=0 sum=28085` 发到串口接收端。分别走完裸机轮询、RTOS 消息服务、Linux TTY；后两者是条件化教学，不代表本平台已经移植完成。

<a id="same-uart"></a>

## 28.1 UART 连接、配置与资源所有权

外面仍是 UART 接收器：最小发送连接需要 SoC TX 接对端 RX、共同参考地、电平匹配，以及一致的波特率和帧格式；使用流控时再落实相应信号。当前控制器的寄存器、时钟分频和发送移位过程见 UART 章。OS 改变的是谁有权配置、谁排队、谁等待，以及多个应用如何共享端口。DTS、设备文件或任务队列都不会替代真实接线与时钟。

先假定 UART 已解除复位，实际输入时钟已知，双方采用经平台确认的波特率与 8N1，端口只有一个软件所有者。初始化通常在该所有者建立时做一次；每打印一个字符都重新初始化会清 FIFO、改分频并扰动其他使用者。多个设备实例、多个应用和多个物理串口是三种不同的“多个”，不能把一个全局 UART 初始化函数当成它们全部的资源管理。

<a id="baremetal-uart"></a>

## 28.2 裸机 UART 轮询发送流程

本地现有链是应用 → 格式化库 → `_putchar` → UART DIF → MMIO。该 UART 路径没有独立器件 HAL；不能为了凑“应用/库/HAL/DIF”四层而虚构一个 HAL。`uart_init` 的 freq 与 baud 分别以 Hz、bit/s 表达，按 `freq/(16×baud)` 求整数分频。freq 应来自实际平台时钟或本地测频结果，不是从其他板级 DTS 抄来的常量。

`uart_write` 轮询发送保持寄存器可接收状态，再写入一个字节。`uart_write_str` 重复该动作；len 是字节数，不包含 C 字符串的末尾零字符，除非应用明确要发零。函数的 void 返回没有编码超时或“对端已收到”的结果。`uart_write_flush` 等待发送保持与移位路径空闲，用于本地发送完成边界；其源码中的顺序 TODO 不在本轮关闭，详细证据见[实现注记与证据边界](os-debug.md#description)。

```
/* 本地 API 的连续调用示意；前置的测频、启动与接线按 UART 章。
 * core_hz 和 baud 是本平台已确认的值，代码片段未在本轮构建/运行。 */
#include "dif/uart.h"
#include "params.h"
static const char result[] = "N=137 errors=0 sum=28085\r\n";
/* 已完成数组逐元素检查后： */
uart_init(&__base_uart, core_hz, baud);
uart_write_str(&__base_uart, (void *)result, sizeof result - 1);
uart_write_flush(&__base_uart);
```

应用在 write 的轮询期间占用 CPU，等待期间除中断外不会自动切到另一个应用。控制器把字节送入发送路径，协议时钟逐位输出；对端按自己的时钟采样。验收先确认数组数据正确，再确认发出的字节数/内容，最后在接收端比对整行。字符出现在终端上是输出链证据，不能独自证明数组是由预期算法计算的。

本地 API：[uart.h](../../../sw/include/dif/uart.h)、[uart.c](../../../sw/lib/dif/uart.c)；printf 路径可与 [helloworld.c](../../../sw/tests/helloworld.c) 对照。

<a id="rtos-uart"></a>

## 28.3 RTOS UART 独占服务任务方案

最小 RTOS 教学方案可以继续使用轮询 DIF，而把端口交给一个日志任务独占。计算任务只产生结果结构并发送到队列；日志任务接收后格式化文本，再调用同样的 uart\_write\_str/flush。这样两个任务不会把各自的字符交错写进同一端口，也不需要在所有应用里重复配置寄存器。此处的服务任务是待实现方案，本地尚没有对应 RTOS port 或驱动交付。

走一遍正常过程：启动代码完成平台条件，创建日志队列与任务；日志任务首次运行时初始化 UART，然后在空队列上阻塞。计算任务完成校验，将 `{seq, errors, sum}` 按值入队，队列成功意味着消息副本已交付内核。日志任务被唤醒后把它转成一行字符，轮询发出并等待本地发送空闲，必要时向结果队列返回“seq 已发送”的通知，再继续等下一条。

这个设计把计算与格式化解耦，但轮询发送的 CPU 开销仍然存在。若日志任务优先级很高，它等待硬件的忙循环也可能影响其他任务。不能把“套了 RTOS 队列”写成“UART 已采用中断，CPU 等待时自动休眠”。队列长度、消息复制成本和服务优先级应由吞吐与延时预算决定。

<a id="rtos-irq"></a>

### 28.3.1 UART 发送中断与缓冲管理

需要节省 CPU 时，驱动可以维护软件发送缓冲：任务把待发送字节交给驱动，驱动填入当前可用 FIFO 并开启相应发送事件；中断到来时，ISR 再送入可容纳的字节，全部提交后关闭不再需要的发送中断。等待任务通过事件被唤醒，长字符串转换仍留在任务上下文。队列索引、IRQ 使能和“等待已结束”的判据需要同一套并发保护，才能避免遗漏唤醒。

这是一种正常中断驱动机制，不是异常恢复流程。本地 UART DIF 初始化会关闭中断，目前不能直接称它为该服务的实现。可用 TX 事件反映什么状态也需按硬件核对；“软件缓冲已空”与“最后停止位已发出”不是同一完成条件。ISR 不应阻塞等待发送完成，发送完成的通知策略由线程/驱动契约说明。这里也没有假定 UART 接上本地 iDMA。

<a id="linux-uart"></a>

## 28.4 Linux TTY 与串口驱动调用链

用户进程先通过已配置的终端或设备接口取得文件描述符 fd。fd 是内核管理的打开对象编号，不是 UART 基址，也不是硬件通道号。`write(fd, buffer, length)` 把用户缓冲中的字节交给内核；如果 stdout 连接到串口，printf 最终也走这类服务，但其用户态缓冲会增加一个提交边界。应用不应把 `__base_uart` 直接强转成用户指针访问 MMIO。

按本地 Linux v6.5 源码中默认 N\_TTY 线路规程及 8250 串口路径，可以连续跟踪：TTY write 入口处理用户请求，`n_tty_write` 执行终端相关处理，serial core 的 `uart_write` 把字节写入软件发送环形缓冲，`__uart_start` 进入具体 port 的启动方法；8250 的发送方法与 IRQ 处理把字节继续送往 UART。线路规程是终端字节处理层，可涉及换行等规则，因此要求字节精确一致时要确认终端属性。

注意 Linux 内核里的 `uart_write` 与本地裸机 DIF 同名，却有不同参数、对象和职责；它们不是链接到同一个库函数。Linux 驱动管理锁、中断和缓冲，用户调用可能因暂时无空间而阻塞，内核在等待期间调度其他线程。实际是否使用 DMA 是驱动和平台的另一项能力，本页的 UART 路径不以 DMA 为前提。

<a id="linux-lifecycle"></a>

### 28.4.1 Linux 串口操作流程与完成条件

一个完整条件例应先由平台维护者确认设备节点及其所有者，避免同时把它用作控制台/getty 和独占测试通道。应用 open 后检查 fd，读取并按接口设置终端属性：实际波特率、8N1、流控和输入/输出转换要与接收端一致。采用非阻塞模式时，写返回“暂不能接受”是正常调用语义，需通过就绪等待继续；首次教学选择已正确配置的阻塞 fd。

```
/* Linux 用户态条件示例：fd 已打开且完成上述配置；本轮未目标执行。 */
#include <errno.h>
#include <stddef.h>
#include <unistd.h>
#include <termios.h>
static int send_result(int fd) {
    const char text[] = "N=137 errors=0 sum=28085\r\n";
    size_t pos = 0;
    while (pos < sizeof text - 1) {
        ssize_t n = write(fd, text + pos, sizeof text - 1 - pos);
        if (n > 0) { pos += (size_t)n; continue; }
        if (n < 0 && errno == EINTR) continue;
        return -1;
    }
    while (tcdrain(fd) != 0) {
        if (errno != EINTR) return -1;
    }
    return 0;
}
```

write 返回正数给出本次接受的字节数，可能少于请求长度，所以循环推进 pos；EINTR 表达被信号打断的接口结果，处理它属于完整调用方法。所有字节被接受后，tcdrain 等待该终端的输出发送边界；返回也不证明对端进行了正确解码。调用方检查函数结果、按自己的所有权恢复所需属性并关闭 fd；若端口由别的系统服务共享，配置变更和关闭影响应由接口管理，不能假定“一进程退出就复位 UART”。

接收端应得到完整一行且字节数一致；应用记录退出状态，内核/设备侧记录所用终端和配置。测试日志不应与被测字节混发到同一串口。这个例子需要已验证的 Linux 驱动与终端环境；DTS 中出现一个 serial 节点只提供配置线索，当前适用性见下节。

<a id="driver-and-description"></a>

## 28.5 设备树与 UART 驱动绑定

本地 cheshire.dtsi 的 UART 节点使用 `compatible="ns16550a"`，声明基址 0x03002000、PLIC 源 1、`reg-shift=2` 和 `reg-io-width=4`。在 Linux v6.5 的 `8250_of.c` 中，compatible 用于匹配，reg-shift 控制寄存器编号的地址间隔，reg-io-width 决定访问大小。二者含义不同：间隔为 4 字节不自动证明只支持 32 位访问。

裸机 UART 实现使用 reg8，已有 DTS 的注释却写“only 32-bit access”。该差异应在当前总线适配与控制器版本上核对，再验证实际 Linux 访问方式；不能直接把注释当成否定裸机 8 位访问的硬件事实。本页 Linux 过程因此是有真实软件源码落点的条件例，不宣布当前 DTS/驱动组合可执行，细节集中见[描述核对项](os-debug.md#description)。

完成驱动绑定后，还需要端口资源、时钟、复位和中断实际可用。驱动 probe 建立内核设备对象，打开操作建立一次软件使用关系；这些阶段不等于每次 write 都重启控制器。DTS 只告诉驱动资源在哪里，驱动程序才能执行配置与服务。未来新增 ISP/NPU 也遵循这一分工，但不能把 UART 的字符设备接口强套到所有图像数据通路。

<a id="buffer-ownership"></a>

## 28.6 设备缓冲区的地址与所有权管理

UART 小字符串便于看到“提交”与“发送完”的区别。改为一帧图像后，按值复制整帧可能太昂贵，需要驱动管理缓冲队列与生命周期：应用交出一个获准的 buffer，驱动取得设备可访问的地址，设备工作期间应用按约定停止修改，收到完成后再归还。用户虚拟地址、内核指针和设备地址分别解释，不能从 fd 或用户 pointer 猜 DMA 地址。

轮询、中断和 DMA 解决不同问题：轮询/中断是如何知道进展，DMA 是谁搬运数据；用了中断不意味着用了 DMA，用了 DMA 也不保证应用已经可以读取最新数据。正常结束需要设备真正停止访问该 buffer，再执行平台规定的同步/映射归还，最后通知用户。详细地址与缓存前置在[设备地址](virtual-memory.md#device-addresses)和[共享存储](sharing.md)，测量提交到结果的边界见[实验测量](measurement.md#boundaries)。

<a id="completion-check"></a>

## 28.7 UART 数据交接的分层完成条件

| 观察 | 能说明什么 | 还不能说明什么 |
| --- | --- | --- |
| 应用算出 sum/逐元素通过 | 本次计算结果满足基准 | 文本已提交或发出 |
| RTOS 队列成功 / Linux write 接受若干字节 | 该层收到数据或其副本 | 控制器 FIFO 或线路已经空闲 |
| 驱动的软件发送队列为空 | 数据已继续提交到下层 | 最后一个字节已完成移位 |
| 控制器发送空闲 / 终端 drain 完成 | 满足本地发送完成契约 | 对端电气采样与协议解码正确 |
| 对端逐字节比较一致 | 这一次端到端文本传输正确 | 所有负载、并发或长时间运行已验证 |

读者应能分别画出三条链，指出初始化所有者、等待发生在哪层、数据副本什么时候能复用，以及本章每个“完成”究竟结束了什么。异常定位入口是[外设 UART 诊断](peripheral-debug.md#uart)和[OS 输入与适用性核对](os-debug.md)；正常路径不需要依靠故障树才能读懂。

**Linux 源码与官方接口依据**

本地 v6.5：[n\_tty\_write](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/buildroot/output/build/linux-v6.5/drivers/tty/n_tty.c)、[serial core](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/buildroot/output/build/linux-v6.5/drivers/tty/serial/serial_core.c)、[8250 发送与 IRQ](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/buildroot/output/build/linux-v6.5/drivers/tty/serial/8250/8250_port.c)、[8250 binding](../../../.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/buildroot/output/build/linux-v6.5/Documentation/devicetree/bindings/serial/8250.yaml)、[Cheshire DTS](../../../sw/boot/cheshire.dtsi)。完整来源快照见本轮 OS 交接。

---

[上一页：嵌入式 Linux 启动与用户程序](linux.md) · [下一页：自定义 IP 的控制、数据和中断接入](integration.md)
