# 37 · 时序约束与物理实现反馈

存储接口路径的时序约束、分析与布局影响。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/timing-physical.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../timing-physical.html) · [阅读路线](index.md)

- [37.1 VRF 地址与数据返回的时序路径](#real-path)
- [37.2 建立时间、保持时间与时钟周期约束](#setup-hold)
- [37.3 约束描述外部条件和合法捕获关系](#constraints)
- [37.4 VRF 宏布局的时序影响](#physical-feedback)
- [37.5 静态时序分析的输入与证据范围](#evidence)

**本章任务**

沿真实 VRF 地址与返回路径，解释约束、静态时序和物理布局怎样共同保证一次读正确完成。前置：[VRF 一拍读契约](asic-memory.md#read-latency)、[时钟](clocks.md)。本页不提供可直接签核的 SDC，也未运行综合或 STA。

<a id="real-path"></a>

## 37.1 VRF 地址与数据返回的时序路径

在本地 `operand_requester` 中，请求元数据寄存器保存当前向量地址，组合逻辑生成 bank 请求，再经过仲裁与选择，形成 `vrf_addr_o`。它进入 `vector_regfile.gen_banks[bank].data_sram.addr_i`；宏在指定时钟边沿接收地址。该路径是“寄存器 → 地址/仲裁逻辑 → SRAM 输入”，不是一个抽象的 CPU 频率数字。

下一段是“SRAM 输出 → VRF mux → 操作数队列寄存器”。与数据并行，`rdata_valid_q` 和 `tgt_opqueue_q` 给出本拍是否有效、应送哪个队列。功能验证核对它们属于同一请求，STA 则核对各条物理路径能否在要求的边沿前后稳定。两者共同成立，才保持一拍接口。

<a id="setup-hold"></a>

## 37.2 建立时间、保持时间与时钟周期约束

发射边沿后，寄存器经过 clock-to-Q 延迟输出新地址；地址译码、仲裁和布线继续消耗时间。接收 SRAM 在捕获边沿之前需要一段建立时间（setup），之后还需保持时间（hold）。忽略偏斜的简化建立条件是 `tCQ(max)+t逻辑(max)+t布线(max)+tsetup+不确定度 ≤ T`。这个式子用于理解预算；真正报告还考虑发射/捕获时钟到达、工作角和具体时序弧。

保持检查关注最早到达的新值，避免它在接收端仍应保持旧值时变化，所以只放慢时钟通常不能消除同一边沿的 hold 问题。门控时钟的插入延迟会改变宏和数据发射寄存器之间的相对边沿；时钟树与数据路径都需要纳入分析。若宏多一拍，先改变的是[消费者的功能契约](asic-memory.md#k-plus-two)，不能靠放宽时序约束把旧 valid 与新数据自动配对。

<a id="constraints"></a>

## 37.3 约束描述外部条件和合法捕获关系

| 约束对象 | 本例为什么需要 | 输入来自哪里 |
| --- | --- | --- |
| 主时钟、派生时钟及工作模式 | 确定系统寄存器和门控 SRAM 的边沿关系；PLL/分频改变时须描述对应关系 | 时钟架构与真实 PLL/门控库；不能照搬 FPGA 50 MHz 为 ASIC 目标 |
| 不确定度、时钟延迟 | 为抖动、建模/实现条件及相对到达留出正确预算 | IP/工艺和各实现阶段的分析方法 |
| 输入/输出延迟与负载 | 芯片接口的到达窗口由外部器件和板线决定；内部 SRAM 用宏时序弧描述 | PAD、封装、PCB 和对端时序；不能用 input\_delay 取代缺失宏 Liberty |
| 模式常量和时序例外 | 分析正常/测试/低功耗等合法工作状态，以及有证据的多周期或异步路径 | 功能协议、CDC 结构、测试策略；每条例外都要说明被排除的捕获为何不发生 |

False path 表示某种普通时序分析不适用于该路径，不是消除电路风险。Multicycle 表示接收协议允许更晚的捕获边沿，同时必须正确处理保持检查；只有控制逻辑确实不在中间边沿接收时才能这样写。VRF 当前一拍有效位不提供这种许可。跨域数据保持与 Gray 指针的物理约束则依[所用 CDC 单元契约](cdc-rdc.md#constraints-and-review)设置，不能统一切断。

<a id="physical-feedback"></a>

## 37.4 VRF 宏布局的时序影响

本页 2-lane 快照共有十六个 VRF bank。若每 lane 的八个宏分散过远，地址仲裁网络与返回 mux 的线长增加，原先逻辑级数相同的路径也会变慢。把宏靠近消费单元可能缩短数据线，但 SRAM 引脚面、供电环、布线阻挡和其他大宏又限制摆放；同一条控制线扇出很多 bank 时还会增加负载。

因此先做可行 floorplan，观察宏位置和通道，再完成标准单元放置、时钟树、布线与寄生提取。每阶段都重新读关键路径：延迟主要来自逻辑、线网、时钟偏斜还是宏本身？若尝试复制控制、调整组织或增加流水级，需重新核消费者、面积和功耗，不能只追求一张更好看的 STA 报告。供电完整性、拥塞、设计规则也可能反向限制频率与布局。

<a id="evidence"></a>

## 37.5 静态时序分析的输入与证据范围

STA 的输入是同版网表、标准单元与宏的 Liberty、SDC、所需寄生和模式/角定义。记录工具版本、库版本、时钟对象、约束覆盖与例外，再记录最大/最小路径和违例范围。前布局估计线延迟适合发现早期问题；布线后寄生更接近实际实现。单一典型角通过，不能代替所需工艺、电压、温度和测试模式的覆盖。

分析输入与时钟/例外职责参考 [OpenSTA 官方说明](https://openroad.readthedocs.io/en/latest/main/src/sta/README.html)；模型、寄生与角的组合参考 [官方示例](https://openroad.readthedocs.io/en/latest/main/src/sta/doc/Examples.html)；时钟树属于布局后实现问题，参考 [OpenROAD CTS 文档](https://openroad.readthedocs.io/en/latest/main/src/cts/README.html)。在线资料于 2026-10-08 查阅，只用于通用机制，不指定本项目 EDA 工具。真实路径依据本地 [operand\_requester](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/operand_requester.sv)和[vector\_regfile](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vector_regfile.sv)。

目前缺少工艺库、宏、IO 预算、目标工作点和签核环境，P01 负责取得这些输入。本页可以完成路径分析与待填预算；实际 SDC、综合、布局与签核尚未实施。读者应能指出这一条路径的两个端点、捕获边沿、所需模型，以及一个约束例外为什么不能随意添加。

**时钟周期增大一倍，所有建立和保持问题都会消失吗？**

不会。建立裕量可能改善，但同边沿保持检查、无约束路径、错误时钟关系及功能上的数据/valid 错配都不能由放慢频率保证解决。

---

[上一页：外设逻辑接口、PAD 与封装连接](physical-interfaces.md) · [下一页：Scan、MBIST 与制造测试](manufacturing-test.md)
