# L01 Ara/RVV 教材优化：范围与验收

输入：`mp/ara-pulp-v2` / `459f9d6f5748e39063f7bb67e959c2f27859915d`。接到补充授权时已有本轮外设正文修改、报告与证据；原有用户修改仅 `learning/figures/20261007/editable/diagrams.pptx`，保护不动。生产 RTL、sw、依赖、配置只读，不运行大型目标验证。

## 修改前问题与执行清单

|正文|原问题|本轮动作|保留|
|---|---|---|---|
|ara|先使用 vl/vtype/VRF，再在下一章解释；缺真实顶层端口和完整状态分类|以137元素加法开篇，在硬件之前建立最小整数RVV模型；增加参数/CSR分类、端口、配置推导、逐指令协作串讲|初译码、非推测发送、握手、pending/MMU及教学波形|
|vector|概念与Ara重复；工具链版本讨论和错误排查打断三种编程入口|引用前章语义，以同一程序从启动到校验讲完；高级mask/tail、定点/浮点后置；诊断移出|汇编实际vl循环、独立参考、intrinsics/auto源、性能证据分层|
|sharing|当前CPU/Ara失效解释重复；实验所需缓冲前提太晚|增加在向量执行前必须满足的最小交接入口，合并重复段，正常与未来协议区分|物理别名、WT/pending/失效、原子与未来旁路边界|
|configuration/cva6|配置表先于向量语义，CPU VLEN字段易混淆|仅增加定向阅读提示与分类链接；全章重排留给全书方案|有效配置及profile核对事实|
|vector-debug（新增参考章）|诊断散布两章|集中构建/非法指令/访存/结果症状及本地限制，保留正文短提示和旧锚点|所有未验证状态与缺陷证据|

不更改图稿：复用现有Ara结构、接口、访存和WaveDrom示意；本文解释图的箭头与因果，不把示意周期当作性能数据。导航增加参考页；主章节仍为30章。

## 定向依据与版本适用性

本地Ara README声明面向RVV 1.0；优先阅读随附 `FUNCTIONALITIES.md`、`docs/source/lane.rst`，再对照 ara.sv、ara_dispatcher、ara_sequencer、lane/vector_regfile、ara_pkg::shuffle_index、vlsu/addrgen/vldu/vstu，以及CVA6 decoder/acc_dispatcher/load_store_unit和接口类型。SoC实例与参数以 `hw/cheshire_soc.sv::gen_ara`、`cheshire_pkg.sv` 为准。在线RVV规范用于架构语义，不能替代本地功能支持或运行证据。现有journey.c、rvv_add.S、rvv_intrinsics.c、rvv_auto.c及build_journey.sh只读。

本地 `ara.sv` 的静态约束检查lane为非零2次幂且不超过MaxNrLanes，VLEN为非零2次幂且≥ELEN；这些不是所有整机合法性条件。VRF按每lane八个64位单口bank组织，数据SRAM不能由控制状态复位推出全清零。SoC直接连接clk_i/rst_ni，scan输入0、输出悬空；内部存在VRF bank局部门控，不据此声称独立PLL/系统时钟域或DFT完成。

## 读者任务验收

正文应能独立回答：VLEN/vl/SEW/LMUL/lane的差别；指令、标量值、向量数据的三条路径；两lane e32四元素映射；请求接受/应答/CPU提交/执行与访存完成为何不同；交出与收回SPM缓冲的条件；三类配置变化影响什么。验收方式是逐题定位连续解释和手算，属于文档审读，不是招募读者测试或目标运行。

实际检查、最终对照与未验证项见本轮独立交接和 `learning/evidence/peripheral-20261008/`。该新目录同时记录外设与后续Ara补充修改，未覆盖旧证据。


## 最终结果与仍未完成的验证

已落实上述5行改动，保留全部旧语义锚点。24章现在先用137元素定义软件模型，随后给参数/状态分类、9个真实顶层端口的方向/接线（按功能合并为5表行）、容量和VLMAX推导，再沿load/add/store解释内部资源与CPU协作。25章保持同一算法比较汇编/intrinsics/auto；mask/tail、EMUL、定点/浮点在基本调用之后。26章把预约SPM条件在调用前明确链接，失效机制去重。

手算已核对：每寄存器256B、总VRF8KiB、每lane4KiB；e32/m1为64元素，137按本地min规则为64/64/9，指针推进256/256/36字节。两个既有WaveDrom均明确为因果示意，无固定拍数或加速承诺。CPU应答、提交、lane执行和load/store_complete保持区分；正文保留profile/真实decoder与共享区条件，详细问题进入vector-debug。

最终生成和浏览器通过证据见本轮handoff与release-*；未修改生产RTL/sw/配置，未新构建向量对象、未执行目标SoC、未测性能、未验证所有向量异常/指令组合。已有ELF/dump和用户HelloWorld不升级为Ara通过。独立评审可使用L01-R Prompt，真实运行留E01/S01/V01；不存在本轮改写后就自动关闭的Ara验证项。
