# 10 · iDMA、流量管理与总线错误

数据搬运提交、完成、流量管理与本地执行条件。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/dma.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../dma.html) · [阅读路线](index.md)

- [10.1 DMA 内存搬运与 CPU 控制职责](#copy-task)
- [10.2 iDMA 的任务与数据通路](#dma)
  - [10.2.1 控制访问与搬运访问的实际路由](#control-data-paths)
  - [10.2.2 二维搬运的地址与完成语义](#two-dimensional)
  - [10.2.3 队列资源和当前错误能力](#resources)
  - [10.2.4 寄存器提交与任务 ID](#registers)
  - [10.2.5 DMA 拷贝任务与缓冲区交接](#normal-copy)
- [10.3 本地 iDMA 示例的执行条件](#lanes)
- [10.4 AXI RT 的预算与发起者规模](#axirt)
- [10.5 总线错误记录的查阅入口](#errors)

**本章任务**

把三行带间距数据搬成连续 48 字节，理解长度、步长和完成 ID。前置：[接口适配](adapters.md)、[SPM 与访存](memory.md)。

<a id="copy-task"></a>

## 10.1 DMA 内存搬运与 CPU 控制职责

CPU 可用 load/store 搬数据；iDMA 接收地址和尺寸后自行发 AXI 读写，让 CPU 处理别的工作。本章用 L=16、源行距32、目标行距16、共3行的例子追踪控制与数据路径。它是片上发起者，没有外接设备型号或串行引脚。当前例子因控制接口缺口只用于机制推导，不能在原工程直接提交，详见[门槛证据](peripheral-debug.md#dma)。

<a id="dma"></a>

## 10.2 iDMA 的任务与数据通路

DMA 的通用含义是 Direct Memory Access（直接存储访问）。本地 iDMA 官方文档将名称展开为 *intelligent AXI Direct Memory Access unit*，README 也用 *Data Movement Accelerator* 描述其定位；字母 i 不表示 input。当前实例可以读源地址并写目标地址，所以既可把外存输入搬到片上，也可把片上结果写回外存。方向由源、目标地址决定，2D 描述的是地址遍历方式。

CPU 配置控制目标端口，寄存器前端组成任务；job FIFO 保存任务，2D midend 将长度、步长和重复次数展开，backend 切分成总线允许的读写 burst，缓冲 R 数据再送 W，并跟踪返回。读取完成和写入完成分别依赖各自响应。当前选择的是 `idma_backend_rw_axi`，不能把上游库还支持 AXI Stream、OBI 等协议理解为本 SoC 已接入这些接口。

<a id="control-data-paths"></a>

### 10.2.1 控制访问与搬运访问的实际路由

CPU 提交的是参数，数据不必经过 CPU 寄存器。iDMA 的 AXI 发起口接主 Crossbar，与 CPU、Ara 一样使用地址译码访问目标；无需对每个存储体另拉一根 DMA 专线。下表用外存到 SPM 的搬运解释路径，地址只说明窗口，不表示已为应用分配缓冲区。

| 事务与发起者 | 地址与经过的模块 | 最终作用 |
| --- | --- | --- |
| CPU 配置 iDMA | 0x01000000 窗口 → Crossbar 的 AxiOut.dma → 配置原子适配/cut → wrapper 的 AXI-to-Reg → reg64\_2d 前端 | 保存地址、尺寸和选项；读 NEXT\_ID 提交 |
| iDMA 读源 | 外存窗口 → AxiIn.dma → Crossbar → LLC 前原子适配 → LLC 缓存或旁路 → 平台主存接口 | 经 R 返回源字节，进入 backend 缓冲 |
| iDMA 写目标 | 高 SPM 别名 → 同一 Crossbar/LLC 入口 → 别名重映射 → 已分配的 SPM way | 经 AW/W 把字节写进片上阵列，等待 B |
| CPU 查询完成 | 同一控制窗口的 DONE\_ID | 按任务 ID 判断退休，并结合错误记录与数据校验 |

反向搬运只需让源选 SPM、目标选外存窗口，仍由 iDMA 发读写事务。若启用 AXI RT，请求还经过其放行控制；BusErr 观察 DMA 总线返回。可达地址不等于任意外设都适合 memcpy：对 FIFO 或带副作用的 MMIO，还需核实访问宽度、地址递增、burst 和外设协议。LVDS 引脚或未映射的 NPU 局部 SRAM 也不会因 iDMA 存在就自动可访问。

<a id="two-dimensional"></a>

### 10.2.2 二维搬运的地址与完成语义

把带行间填充的图像看作二维字节数组：每行搬 L 字节，源/目的行起点间距分别为 S、D，共 R 行。对本地 2D midend，行起点按 srcₖ=src₀+k×S、dstₖ=dst₀+k×D 递推；stride 是起点间的字节增量，不是“搬完 L 后再额外跳 S”。例如 L=16、S=32、D=16、R=3，读区分别从 src+0/+32/+64 起，写成连续 48 字节。

midend 接受一个低维请求后才推进地址与计数；末行标 last，backend 仍需等真实响应。这个推导来自 idma\_nd\_midend 的 src\_addr\_calc/dst\_addr\_calc，不代表当前 DMA 桥已可运行。修复门槛通过后，先做三行不等数据与行间守卫，再测跨 burst、部分字节、背压和错误，检查只提交一次 NEXT\_ID。

<a id="resources"></a>

### 10.2.3 队列资源和当前错误能力

Cfg.Dma 选择实例，DmaConfEnableTwoD 默认 1，DmaJobFifoDepth=2、DmaNumAxInFlight=16、DmaMemSysDepth=8 分别控制不同资源。wrapper 固定 32 位任务 ID、32 位长度、单 stream，并拒绝零长传输。backend 配置 NO\_ERROR\_HANDLING，软件还需结合外层错误记录。wrapper 没有完成 IRQ；PLIC 中的 DMA 源是读写错误通知。

<a id="registers"></a>

### 10.2.4 寄存器提交与任务 ID

控制窗口 0x01000000 中，CONF(+0) 配选项，STATUS\_0(+4) 反映状态，DST/SRC 地址在 +0xd0/d4、+0xd8/dc，LENGTH 在 +0xe0/e4。参数稳定后读取 NEXT\_ID\_0(+0x44) 才提交并取得任务 ID；DONE\_ID\_0(+0x84) 用于完成查询。NEXT\_ID 是读带副作用，不能当作普通状态反复刷新。2D 步长和 repetitions 的字节/次数单位按 midend 与驱动核对。

<a id="normal-copy"></a>

### 10.2.5 DMA 拷贝任务与缓冲区交接

在接口通过独立修复验收的环境，CPU 先独占可达且可见的源/目标缓冲，给3行填不同数据并给间隙填守卫，配置 DST/SRC、LENGTH=16、两个 stride 和 repetitions=3；完成排序后仅读一次 NEXT\_ID 保存返回 ID。backend 将源三行读回并写到目标48字节，软件查询 DONE 到本 ID 完成，再排序并比较数据和未触碰区，最后交还缓冲区。读请求、写数据和写响应都属于搬运生命周期；ID匹配不代替内容检查。

真实接口在 [dif/dma.h](../../../sw/include/dif/dma.h)：sys\_dma\_2d\_memcpy(dst,src,size,dst\_stride,src\_stride,num\_reps) 提交并返回任务 ID，带 blocking 的变体轮询完成。它是头文件内联 MMIO，无器件 HAL。地址是设备可达地址，size/stride 单位为字节，num\_reps 是行数；旧实现等待无超时且 ID 访问有已知限制，保留生产代码不在此伪装成可用新驱动。

gen\_dma 的 cheshire\_idma\_wrap 使用系统 clk\_i、低有效 rst\_ni；控制侧由 AXI 转 Reg，数据侧为独立 AXI 主口。复位清控制/队列状态，不替你初始化源/目标 RAM。启动应从无在途任务的受控状态开始；多个调用者共享提交端口和 ID 序列，应串行化寄存器参数填写与触发读取。

<a id="lanes"></a>

## 10.3 本地 iDMA 示例的执行条件

当前 +0x44/+0x84 控制访问及 HAL 宽度门槛未关闭，advanced.c capstone 默认 BLOCKED/rc16、不提交 DMA；旧 lesson.c 分支仅为历史代码。

[症状排查与当前实现限制](peripheral-debug.md#dma)集中在诊断章。

<a id="axirt"></a>

## 10.4 AXI RT 的预算与发起者规模

AXI RT 在启用时位于发起者与 Crossbar 之间，按地址 region 和周期 budget 控制流量。一次 burst 的字节成本为 `(AXLEN+1)<<AXSIZE`。软件先 claim guard，再设置区域、读写预算/周期和 LEN\_LIMIT，最后开启 RT/IMTU；预算归零会影响请求推进，最终时延还受仲裁和目标服务影响。

寄存器窗口为 0x020c0000，guard 为 0x020c1ffc；RT\_ENABLE+0x0c、RT\_BYPASSED+0x10、IMTU\_ENABLE+0x1c 等含义可查[索引](registers.md#group-10)。IMTU\_ABORT 的预算/周期复位语义不等于通用 DMA 取消。当前生成尺寸为 6 managers×2 regions，SelectedCfg=1 与此默认组合匹配；Ara 全设备组合有 7 个发起者，需要同步生成表。

原 axirt\_budget.spm.c 通过 DMA 搬 1024 字节并检查读写预算各扣 1024，可用于理解单位；它运行前同样受 DMA 控制接口门槛约束。其 .dump 是已有软件反汇编，需结合 ELF、配置和真实运行日志才可作为新验证。该示例的等待边界见诊断章。

<a id="errors"></a>

## 10.5 总线错误记录的查阅入口

BusErr 是错误记录模块，与正常 DMA 完成 ID 分工不同。其带弹出副作用的读法和 VGA 容量问题统一见[诊断章](peripheral-debug.md#bus-errors)；完整寄存器见[iDMA](registers.md#group-7)与[BusErr](registers.md#group-11)分组。

**源码与进一步阅读**

[随附官方 iDMA 名称与分层](../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/doc/src/index.rst)；[官方 README 的 Data Movement Accelerator 与协议能力](../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/README.md)；[`gen_dma、i_dma_conf_atomics、i_dma_bus_err`](../../../hw/cheshire_soc.sv)；[`gen_2d、i_idma_midend、i_idma_backend、i_axi_rw_join`](../../../hw/cheshire_idma_wrap.sv)；[`src_addr_calc/dst_addr_calc`](../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/src/midend/idma_nd_midend.sv)；[`sys_dma_2d_memcpy` 与 ID 访问](../../../sw/include/dif/dma.h)；[控制寄存器固定 DW=32](../../../.bender/git/checkouts/idma-77bf7fa56d324e6a/target/rtl/idma_reg64_2d_reg_top.sv)；[预算测试源程序](../../../sw/tests/axirt_budget.spm.c)。

**源行距32、行长16表示每行后再跳32吗？**

不是。下一行起点是当前起点+32，当前16字节之后留16字节间隔。

---

[上一页：Cache、LLC/SPM 与存储路径](memory.md) · [下一页：Ara 结构与 CVA6 协处理器接口](ara.md)
