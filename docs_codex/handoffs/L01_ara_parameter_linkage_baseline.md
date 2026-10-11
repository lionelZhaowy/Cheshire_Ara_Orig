# L01 / Ara 参数与 Cheshire 联动基线

> 记录日期：2026-10-09。2026-10-11 按任务/主题命名迁移；下方保留原始内容与验证边界。后续同主题变更在文件头追加修改记录。

## 基本信息

- 日期：2026-10-09。
- 授权：源码分析、官方资料核对、验证可行性答疑；不实施参数变更或 ASIC 提取。
- 输入：分支 `mp/ara-pulp-v2`，HEAD `2784340240915fe4338ec54bfd613723b127d62e`；开始时已跟踪文件无改动，13项已有未跟踪交接/图目录保留。
- 状态：初始配置入口与消费者静态梳理完成，等待用户指定候选配置。
- 负责路径：仅新增本交接；共享状态、任务表、生产 RTL/sw、filelist 均未修改。

## 本轮结果（源码确认）

1. `hw/cheshire_pkg.sv:559` 默认 AW48/DW64、Ara关闭、lane=2/VLEN=2048、RT关闭。`target/sim/src/tb_cheshire_pkg.sv:27` 的配置3开启Ara并明确2/2048；`target/sim/vsim/start.cheshire_soc.tcl:31` 把SELCFG传给SelectedCfg，fixture按索引选择DutCfg。
2. FPGA入口不同：`target/xilinx/src/cheshire_top_xilinx.sv:116` 从DefaultCfg生成配置，ARA宏开启Ara，NR_LANES/VLEN宏覆盖参数；当前VCU118加源脚本为向量profile、2/2048。
3. CPU源码选择独立：根`cheshire.mk:19`仍默认标量WB profile。Ara依赖`cheshire/Makefile:27`起选择向量profile、exclude_first_pass_decoder和ARA等宏。仅SELCFG=3不能切换CPU源码。
4. `hw/cheshire_soc.sv:806`传入NrLanes、VLEN；OSSupport固定1。FPUSupport、FPExtSupport、FixPtSupport、SegSupport未覆盖，沿用Ara顶层默认值：HalfSingleDouble、Enable、Enable、Enable。
5. Ara `hardware/src/ara.sv:369`按NrLanes生成lane，功能参数送入lane；NrLanes/VLEN还送dispatcher、sequencer、VLSU、slide和mask。`lane/lane.sv:30,396`与`lane/vector_regfile.sv:38`把每lane VRF容量落实为bank深度。寄存器总有效位数32×VLEN；VLEN2048为8KiB，2-lane每lane4KiB。只增加lane不增加此总有效容量，不能据此推断总面积不变。
6. `ara.sv:664`起检查lane非零、2次幂、不超过MaxNrLanes=16；VLEN非零、不小于ELEN=64、2次幂。仅是顶层检查，不是所有lane/VLEN组合可用证明；具体组合仍需检查VRF bank深度等消费者。
7. `hw/cheshire_soc.sv:606,818,841,861`：Ara AXI DW=32×lane，经invalidation filter和位宽转换接系统总线。2-lane为64；只改8-lane则256→64，不自动加宽主Xbar。
8. `hw/cheshire_pkg.sv:489`的gen_cva6_cfg同步覆盖CPU AXI DW/AW；`cheshire_soc.sv:242,513`的主Xbar/LLC消费系统位宽。`get_llc_size():276`包含DW/8，固定默认geometry时DW64容量128KiB，DW128容量256KiB。加宽必须联查CPU缓存、LLC/SPM、DMA、外设适配及平台出口。
9. `ara.sv:468`的OSSupport控制与CVA6 MMU接口连接，不代表OS启动/上下文保存已通过。该文件CVA6Cfg.VLEN用于虚拟地址信号；不能与Ara向量VLEN混同。
10. `cheshire_ara_asic/`本轮检查不存在；既定提取建议未实施。Ara写响应错误、iDMA控制位宽等既有动态缺口保持开放。

## 官方来源与版本

- `.bender/SNAPSHOT.tsv`记录Ara来源提交`2895ba907e9eb14b3464609dc791a969d159a7c3`、CVA6来源提交`99eac9a649001bdf5b8f9da52e0ca73d5c48db1c`；本地vendor含本地修改，不宣称整树等同上游。
- 在线核对对应Ara提交的顶层参数及Cheshire集成入口，与本次相关本地定义一致：
  - https://raw.githubusercontent.com/pulp-platform/ara/2895ba907e9eb14b3464609dc791a969d159a7c3/hardware/src/ara.sv
  - https://raw.githubusercontent.com/pulp-platform/ara/2895ba907e9eb14b3464609dc791a969d159a7c3/cheshire/Makefile

## 验证证据

- 在仓库根运行`git status --short`、`git branch --show-current`、`git rev-parse HEAD`及定向`rg/sed/cat`读取；使用web打开上述固定提交官方源码。
- 个别初始搜索使用不存在路径/未匹配zsh glob，报错后用`rg --files`定位并重新读取实际路径；不作为验证通过证据。
- `test -d cheshire_ara_asic`返回1；目录不存在。
- 未编译、未展开、未仿真、未板测、未综合；没有新增目标运行证据。
- 仅新增本交接，未提交。没有配置、接口或实施状态变化，无需合并共享状态。

## 下一步

1. 等待用户指定lane/VLEN/总线宽度或功能参数问题。
2. 对指定组合继续追踪消费者、约束和最小验证范围，区分静态候选与已验证能力。
3. 实施前明确最小修改文件、软件联动和验收条件，取得对应授权。
