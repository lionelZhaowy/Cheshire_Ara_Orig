# Ara/RVV 调试与故障诊断

Ara/RVV 构建、执行、访存与结果的诊断证据。

> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/vector-debug.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../vector-debug.html) · [阅读路线](index.md)

- [向量程序的分阶段诊断与证据](#layers)
- [首条向量指令陷入的配置核对](#configuration)
- [访存不结束或数组错误](#memory)
- [本地限制与未完成验收](#local-limits)

**本章任务**

为Ara/RVV的构建、启动、访存和结果问题提供独立入口；正常协作见Ara/RVV正文。

<a id="layers"></a>

## 向量程序的分阶段诊断与证据

错误定位按阶段：缺头文件查 include/toolchain；unknown intrinsic 查实际 header/API；汇编 illegal operands 查 -march 与编码；链接 relocation 查代码模型/脚本与对象 ABI；运行首条 V 陷入查 profile、真实 decoder、VS/FS。构建记录见[09-29 深度扩充编译记录](../evidence/depth-20260929-builds.txt)。

这三层分别回答“文件里有什么”“硬件实际执行什么”“执行结果是否正确”。实验 E 的命令集中在[实验手册](labs.md#lab-e)。此前深度扩充只完成轻量构建和文档检查，动态层仍待目标 SoC 环境。非法指令先查 mepc 对应机器码及 RVV/VS；挂在向量访存则查地址、Ara 请求/响应和共享区；结果错误再查首个差异与所有权。

<a id="configuration"></a>

## 首条向量指令陷入的配置核对

保存mepc/mcause/mtval及对应机器码，区分编译器生成了V、CPU初译码可识别、VS/FS已启用、Ara真实实例接通四件事。当前旧生产仿真列表的标量profile/stub与预期向量组合不一致，SELCFG=3不能单独修复；先由E01/V01建立自洽清单再运行实验E。用户已有VCU118 HelloWorld不证明RVV执行。

<a id="memory"></a>

## 访存不结束或数组错误

先查预约SPM、地址对齐和别名，再查acc请求/应答、addrgen/MMU使能、AR/R或AW/W/B和pending。CPU应答或函数ret不证明所有结果可读。错误数组先记录首个差异、实际vl序列、三个指针增量和守卫，再查输入可见性及是否并发修改。不得用增加fence掩盖未确认的缓存属性。

<a id="local-limits"></a>

## 本地限制与未完成验收

当前 `vstu.sv` 在 B 通道处明确留下“不能处理 B 错误”的 TODO，实际直接接受 B；vldu 的数据接收也未据 RRESP 构成完整的总线错误上报闭环。官方 Ara 最新 dispatcher 文档笼统提到总线错误，而本地版本只能据具体消费者确认支持范围。应保留读写错误注入验收，不能把译码/MMU 异常通路扩大解释成任意 AXI 错误都能精确陷入。

本地 addrgen 对元素未对齐地址有拒绝分支，使用 ILLEGAL\_INSTR 上报；索引访问还留有 vstart 支持限制注释。用本地实现规划测试时，应覆盖对齐、页边界、尾部、mask、故障元素和复位；不要用规范中存在某条指令来替代本版本的逐项验证。

上述为本地实现与注释证据，尚未完成本轮错误注入。非零vstart、mask、跨页、总线错误和上下文保存恢复需要独立覆盖；OSSupport=1不等于Linux/RTOS向量上下文管理已经可用。目标运行、数值及加速比仍为空白证据，不能由现有dump关闭。

出现超时，停止新任务并保留可能仍被写的缓冲；是否可排空、复位哪个域、怎样恢复向量上下文须由系统实现验证。正常背压见[Ara正文](ara.md#stalls-errors)，外设错误记录见[BusErr诊断](peripheral-debug.md#bus-errors)。

**源码与进一步阅读**

[CPU 队列、非推测发射、pending 与 barrier](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/acc_dispatcher.sv)；[初译码与 VS/FS](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/cva6_accel_first_pass_decoder.sv)；[专用接口字段](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/ara/intf_typedef.svh)；[内部运行表与地址应答](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_sequencer.sv)；[地址/翻译/对齐限制](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/addrgen.sv)；[load 完成](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vldu.sv)；[store 完成和 B 错误缺口](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/vlsu/vstu.sv)；[MMU 与保护消费者](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/load_store_unit.sv)；[本地支持声明与 ELEN](../../../.bender/git/checkouts/ara-2c7b103275a16c87/FUNCTIONALITIES.md)；[RVV 类型与编码](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/include/rvv_pkg.sv)；[随附官方 VRF/重排说明](../../../.bender/git/checkouts/ara-2c7b103275a16c87/docs/source/lane.rst)；[Ara 实例与失效通路](../../../hw/cheshire_soc.sv)；[dispatcher / sequencer / lanes / VLSU](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara.sv)；[csr\_vl\_d 分块选择](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/ara_dispatcher.sv)；[Ara 写失效](../../../.bender/git/checkouts/ara-2c7b103275a16c87/hardware/src/axi_inval_filter.sv)；[VS 与 acc\_cons 状态](../../../.bender/git/checkouts/cva6-20c9d7cbe0dd6995/core/csr_regfile.sv)

**看到vadd机器码是否说明加速成功？**

只说明静态产物包含指令；还需实际执行、独立结果和明确完成边界的计时。

---

[上一页：外设调试与故障诊断](peripheral-debug.md) · [下一页：平台、集成与测量诊断](system-debug.md)
