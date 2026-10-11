# 34 · Ara VRF 与 SRAM 宏接口

VRF 消费者的容量、时序与候选技术映射。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/asic-memory.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../asic-memory.html) · [阅读路线](index.md)

- [34.1 VRF 读数据的消费者与传输路径](#consumer-first)
- [34.2 当前 VRF bank 的容量与接口契约](#bank-contract)
- [34.3 SRAM 读取与字节掩码写入时序](#read-latency)
  - [34.3.1 SRAM 读延迟变化与响应时序适配](#k-plus-two)
- [34.4 SRAM 宏拼接与写掩码适配](#macro-tiling)
- [34.5 存储宏视图、初始化与测试接口](#views-and-initialization)

**本章任务**

沿 Ara 读出一组操作数的过程，为一个真实 VRF bank 写出 SRAM 接口契约，并判断候选宏能否保持原有行为。前置：[Ara 的 lane、VRF 与操作数队列](ara.md)。这里只做源码推演，没有选定工艺宏。

<a id="consumer-first"></a>

## 34.1 VRF 读数据的消费者与传输路径

向量加法要从 VRF 取两个操作数。lane 内的 `operand_requester` 为读操作申请 bank；同一 bank 的读与结果写回经仲裁选出一次访问，送到 `vector_regfile`。VRF 返回的数据带着“应送往哪个操作数队列”的身份，进入队列后才交给运算单元。因此替换存储时，要同时保持数据、有效标志和队列选择的对应关系。

当前连接可按 `lane.i_operand_requester → lane.i_vrf.gen_banks[bank].data_sram → i_vrf_mux → lane.i_operand_queues` 阅读。这是 lane 内部的存储接口；地址是 bank 内的字索引，不是 CPU 物理地址，也不是 DDR 字节地址。AXI 的 burst、ID 或 WSTRB 不能直接当作这里的完整接口。

<a id="bank-contract"></a>

## 34.2 当前 VRF bank 的容量与接口契约

采用本地已记录的向量配置快照 `VLEN=2048 bit、NrLanes=2`。32 个架构向量寄存器共 `32×2048/8=8192 byte`；每 lane 分得 4096 byte。本地 `NrVRFBanksPerLane=8`、`ELEN=64`，所以每 bank 是 512 byte，即 **64 个 64-bit 字**，一共 16 个 bank。这些是数据位容量，不包括仲裁、队列、门控和外围面积。

| 当前实例项 | 源码给出的含义 | 宏适配必须保持什么 |
| --- | --- | --- |
| NumWords=64，DataWidth=64，NumPorts=1 | 一个 1RW 端口，一拍只选择读或写；6-bit bank 字地址 | 不能把 1RW 误写成同时独立读写的 1R1W；并发由 bank 仲裁提供 |
| req、we、be | req=1 才访问；we=1 写、we=0 读；8 位 be，每位控制 8 bit，高有效 | 正确转换片选、写使能和掩码极性；只更新允许的字节 |
| Latency=1，ByteWidth=8 | 实例未重写这两个参数，采用本地 tc\_sram 默认值 | 数据与一拍延迟的有效位、目标队列同时到达 |
| rst\_ni；SimInit="none" | 复位控制状态；默认模型不执行存储阵列清零 | 不能把低有效复位接到宏后就承诺 v0–v31 全零；使用前需由程序或初始化流程定义数据 |
| vrf\_clk | 非 VERILATOR 路径按 bank 门控；req 或上一拍 active 维持时钟 | 合法门控单元、测试可控性与读时序一起核；VERILATOR 分支直通时钟不是 ASIC 映射 |

本地官方随附资料 [Ara lane 文档](../../../.bender/git/checkouts/ara-2c7b103275a16c87/docs/source/lane.rst)解释 bank 分片；本页具体 2/2048 参数和时序以 [lane.sv](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/lane.sv)、[vector\_regfile.sv](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/lane/vector_regfile.sv)、[tc\_sram.sv](../../../.bender/git/checkouts/tech_cells_generic-223c43ccbeb688f9/src/rtl/tc_sram.sv) 为准；依赖是当前仓库固定路径快照，不以在线最新版本替代。

上表的初始化描述限定于 `src/rtl/tc_sram.sv` 行为实现。本地 [Xilinx XPM 实现](../../../.bender/git/checkouts/tech_cells_generic-223c43ccbeb688f9/src/fpga/tc_sram_xilinx.sv)另外固定使用零初始化，且其输出复位不等于每次系统复位都清整块阵列。选择不同 target 时须选中唯一实现；FPGA 上电零值不能成为 ASIC 软件依赖。

<a id="read-latency"></a>

## 34.3 SRAM 读取与字节掩码写入时序

先假设 bank 的字地址 3 已由程序写入已知值。周期 k 内，仲裁器选中该地址的读请求，同时指定目标队列 AluA；在下一采样边沿，本地 SRAM 读路径给出这个字，`rdata_valid_q` 更新为 `req_i & ~wen_i`，`tgt_opqueue_q` 同步延迟。于是周期 k+1 的 mux 把“字地址 3 的数据”送进 AluA。这里的 k/k+1 表示接口周期关系，不是整条向量指令只需一拍。

随后向同一地址提交写请求，`be=8'b00000001` 时只更新最低一个字节，其他七个字节保持原值。该写访问不会产生有效的 operand 返回，因为 `wen=1` 令读有效位为零。下一次真正读同一地址时，消费者才应检查新字节与保留字节。这给出了小测试的预期结果：局部写正确、未选字节不变、写操作不误入操作数队列。

读和写若同时申请本 bank，仲裁先选一笔，另一笔以后重试；这属于正常资源竞争。单端口实例并不存在“同拍两个端口读写冲突”的外部许可。宏内部 read-during-write 输出是否保持或变化，不能被消费者当作该写操作的有效读结果；若未来改成多端口，才需要另行确定同址冲突次序。

<a id="k-plus-two"></a>

### 34.3.1 SRAM 读延迟变化与响应时序适配

若候选宏到 k+2 才给出数据，而只改 `data_sram` 的实例名，k+1 的 `rdata_valid_q` 已宣告数据有效，`tgt_opqueue_q` 也已经指向本次队列。队列会在错误的周期接受旧值；到 k+2 新值出现时，路由身份可能已属于下一笔请求。错误因此不是“程序整体慢一拍”，而是数据和任务身份错配。

一种工程选择是寻找保持一拍契约的宏；另一种是重新设计响应时序，同时调整有效位、队列选择、请求授予/队列空间预留及门控维持周期，并回归连续请求和背压。当前 `operand_requester` 把已选 VRF 请求直接作为 grant，VRF 输出 mux 的接收端设为始终 ready；因此不能仅在输出处加一个随意的 valid 寄存器就断言适配完成。本轮不实施任一选择。

<a id="macro-tiling"></a>

## 34.4 SRAM 宏拼接与写掩码适配

教学假设只有 64×32-bit、带四位字节写使能的单端口宏，可以把两个宏并排组成一个 64×64-bit bank：地址和请求同时送给两片，数据与掩码各取一半，读结果按原位序拼接。若宏深度较小而需要纵向拼接，地址高位负责片选，读返回时还须保留相同延迟的片选身份。假设只用于推导，没有选中实际宏或承诺面积收益。

若宏只支持整字写，原本一拍的字节更新可能需要先读旧字、合并后再写。这样一个逻辑写占用多个物理周期；所有读取和其他写入必须服从新的互斥与完成规则。上游固定接收语义因此也要重新评估，不能仅把 be 全接为 1。以更宽宏浪费部分数据位、使用宏原生写掩码或改变逻辑组织，都是得到真实宏清单后才能比较的方案。

<a id="views-and-initialization"></a>

## 34.5 存储宏视图、初始化与测试接口

功能模型回答读写内容和周期；Liberty 时序模型描述引脚的建立/保持、时钟到输出、功耗及工作角；LEF 抽象提供外形、引脚和布线阻挡；版图交付与物理验证规则服务最终制造。它们要属于同一宏变体和版本。只有行为模型能读写，尚不能说明这个 bank 已经映射成可布线、可签核的 SRAM。

宏测试端口、冗余修复、保持/休眠脚及上电要求也在契约内。正常运行模式怎样固定这些脚，制造测试怎样接管，唤醒后哪些数据仍有效，分别见[存储制造测试](manufacturing-test.md#memory-test)与[状态保持](power.md#sequence)。Boot ROM 的常量逻辑或候选 ROM 宏还要验证指令字节、映射、读延迟和制造后可更新边界，不能因为同属“存储器”就沿用 VRF 接口。

本页只完成 VRF 的一个真实例子。完整 ASIC 盘点还包含 CPU cache、LLC data/tag、debug 存储和各类 FIFO；由 P01 获取工艺/宏资料，E01 保留消费者与来源，V01 用真实模型验证，S01 处理初始化契约。没有真实宏时，可以完成这份接口说明，不能完成工艺映射。

**把本页配置改成 VLEN=4096、lane 数仍为 2，哪个接口尺寸改变？**

总 VRF 增至 16 KiB，每 lane 8 KiB，每 bank 1 KiB，即 128×64 bit，字地址增至 7 bit。bank 数和 64-bit 数据宽保持本地组织不变；这种推导不代表该组合已经跑过时序或功能验证。

**能否从 tc\_sram 的 rst\_ni 推导向量寄存器复位后全零？**

不能。默认 SimInit="none" 的模型没有清零阵列；vector\_regfile 清的是有效位与路由状态。程序应先定义使用的向量数据。

---

[上一页：电源域与低功耗规划](power.md) · [下一页：跨时钟与复位域的事务交接](cdc-rdc.md)
